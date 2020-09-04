from collections import Mapping
from flask import request, make_response, Response, g
from flask.json import dumps
from flask.views import MethodView

from .errors import RestError


# 继承 MethodView 类创建新的视图方法类
# 如有需要，该类中定义的全部方法会被其子类继承并在子类中被调用
# 所有的 API 都将基于这个 RestView 类实现
# 当客户端发送请求到服务器，会调用此类中的方法
class RestView(MethodView):
    '''自定义视图类的基类
    '''

    content_type = 'application/json; charset=utf-8'
    method_decorators = []

    # 如果遇到报错，例如 RestError ，就调用此方法
    # 这是在 dispatch_request 方法中设置的
    def handle_error(self, exception):
        data = {
            'ok': False,
            'message': exception.message
        }
        result = dumps(data) + '\n'
        resp = make_response(result, exception.code)
        resp.headers['Content-Type'] = self.content_type
        return resp

    def dispatch_request(self, *args, **kwargs):
        # 获取客户端发送的请求对应的视图函数
        # Python 内置方法 getattr 可获得第一个参数的属性值
        # 第二个参数为属性名，第三个参数为缺省值
        method = getattr(self, request.method.lower(), None)
        if method is None and request.method == 'HEAD':
            method = getattr(self, 'get', None)

        # 断言 method 不是 None，逗号后面是断言失败的提示信息
        assert method is not None, 'Unimplemented method {}'.format(
                request.method)

        # 以下几行代码用于处理装饰器
        # 针对某个 Server 对象的删改查操作，会为对应的方法添加装饰器
        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        # 使用装饰器重定义视图函数
        for decorator in decorators:
            method = decorator(method)

        # 调用视图函数处理请求，获得返回值
        try:
            # resp 的值的类型有多种可能
            # IndexView.get 的返回值是 Response 对象
            # ServerListView.get 的返回值是列表
            # ServerListView.post 的返回值是元组
            # ServerDetailView.get 的返回值是 Server 实例
            # ServerDetailView.put 的返回值是 Server 实例
            # ServerDetailView.delete 的返回值是元组，等等...
            resp = method(*args, **kwargs)
        # RestError 是一众自定义异常类的父类
        except RestError as e:
            resp = self.handle_error(e)

        # 如果返回值是 Response 对象，直接返回
        if isinstance(resp, Response):
            return resp

        # 调用自定义的 unpack 方法解析返回值，获得三个对象
        data, code, headers = self.unpack(resp)
        # 如果状态码大于 400 则 data 为错误信息，对其进行处理
        if code >= 400 and isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    message = value[0]
                else:
                    message = value
            data = {'ok': False, 'message': message}

        # dumps 方法将 data 这个列表序列化成为字符串，再在末尾加个换行符
        result = dumps(data) + '\n'
        # make_response 方法返回带响应码的 Response 对象
        response = make_response(result, code)
        # 给 Response 对象增加报头信息
        response.headers.extend(headers)
        response.headers['Content-Type'] = self.content_type
        # 将 Response 对象返回给浏览器
        return response

    # 该方法用于解析视图函数的返回值
    @staticmethod
    def unpack(value):
        headers = {}
        # 例如调用的是 ServerListView 类中的 post 方法创建新 Server 实例
        # 返回值就是元组，也就是 value 的值是元组
        # 元组里面是一个字典和一个响应状态码
        if not isinstance(value, tuple):
            return value, 200, {}
        if len(value) == 3:
            data, code, headers = value
        if len(value) == 2:
            data, code = value
        return data, code, headers
