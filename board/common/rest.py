'''
该模块实现了 RESTful 风格的相关类型，主要包含 RestException 和 RestView 两个类型

RestException 是异常基类
该类型的异常发生时，将被自动序列化为 JSON 格式响应

RestView 是视图基类
基于该基类创建视图控制器类时，相关方法的调用结果将被序列化为 JSON 格式响应
'''

from collections import Mapping
from flask import request, Response, make_response
from flask.json import dumps
from flask.views import MethodView


class RestException(Exception):
    """异常基类
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__()


# 继承 MethodView 类创建新的视图方法类的基类
# 该类中定义的全部方法会被其子类继承并在子类中被调用
# 所有的 API 都将基于这个 RestView 类实现
# 当客户端发送请求到服务器，会调用此类中的方法
class RestView(MethodView):
    """自定义视图基类

    JSON 序列化，异常处理，装饰器支持
    """

    content_type = 'application/json; charset=utf-8'
    method_decorators = []

    # 如果遇到报错，例如 RestException ，就调用此方法
    # 这是在 dispatch_request 方法中设置的
    def handler_error(self, exception):
        """处理异常
        """
        data = {
            'ok': False,
            'message': exception.message
        }

        result = dumps(data) + '\n'
        resp = make_response(result, exception.code)
        resp.headers['Content-Type'] = self.content_type
        return resp

    def dispatch_request(self, *args, **kwargs):
        """ 重写父类方法，支持数据自动序列化
        """
        # 获取对应于 HTTP 请求方式的方法
        # Python 内置方法 getattr 可获得第一个参数的属性值
        # 第二个参数为属性名，第三个参数为缺省值
        method = getattr(self, request.method.lower(), None)
        if method is None and request.method == 'HEAD':
            method = getattr(self, 'get', None)

        # 断言 method 不是 None，逗号后面是断言失败的提示信息
        assert method is not None, 'Unimplemented method %r' % request.method

        # HTTP 请求方法定义了不同的装饰器
        # 以下几行代码用于处理装饰器
        # 针对某个 Server 对象的删改查操作，会为对应的方法添加装饰器
        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            method = decorator(method)

        try:
            # resp 的值的类型有多种可能
            # IndexView.get 的返回值是 Response 对象
            # ServerList.get 的返回值是列表
            # ServerList.post 的返回值是元组
            # ServerDetail.get 的返回值是 Server 实例
            # ServerDetail.put 的返回值是 Server 实例
            # ServerDetail.delete 的返回值是元组，等等...
            resp = method(*args, **kwargs)
        except RestException as e:
            resp = self.handler_error(e)

        # 如果返回结果已经是 HTTP 响应则直接返回
        if isinstance(resp, Response):
            return resp

        # 调用自定义的 unpack 方法获得三个返回值
        # 从返回值中解析出 HTTP 响应信息，比如状态码和头部
        data, code, headers = RestView.unpack(resp)

        # 处理错误，HTTP 状态码大于 400 时认为是错误
        # 返回的错误类似于 {'name': ['redis server already exist']} 将其调整为
        # {'ok': False, 'message': 'redis server already exist'}
        if code >= 400 and isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list) and len(data[key]) > 0:
                    message = data[key][0]
                else:
                    message = data[key]
            data = {'ok': False, 'message': message}

        # 序列化数据
        # dumps 方法将 data 这个列表序列化成为字符串，再在末尾加个换行符
        result = dumps(data) + '\n'
        # make_response 方法返回带响应码的 Response 对象
        response = make_response(result, code)
        # 给 Response 对象增加报头信息
        response.headers.extend(headers)
        # 设置响应数据类型为 applicaiton/json
        response.headers['Content-Type'] = self.content_type
        # 将 Response 对象返回给浏览器
        return response

    @staticmethod
    def unpack(value):
        """解析视图方法返回值
        """
        headers = {}
        # 例如调用的是 ServerList 类中的 post 方法创建新 Server 实例
        # 返回值就是元组，也就是 value 的值是元组
        # 元组里面是一个字典和一个响应状态码
        if not isinstance(value, tuple):
            return value, 200, {}
        # 如果返回值有 3
        if len(value) == 3:
            data, code, headers = value
        elif len(value) == 2:
            data, code = value
        return data, code, headers
