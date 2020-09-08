from flask import request, g

from ..common.rest import RestView
from ..models import Server, ServerSchema
from .decorators import ObjectMustExists, TokenAuthenticate


class ServerListView(RestView):
    """该视图类用于查询全部 Redis 服务器和添加新的 Redis 服务器
    """

    method_decorators = (TokenAuthenticate(admin=True), )

    def get(self):
        """获取 Redis 列表
        """
        servers = Server.query.all()
        # data 的值是列表，列表中的元素是字典，字典由 servers 转换而来
        # many=True 参数保证可以处理多个 Server 实例
        data = ServerSchema().dump(servers, many=True).data
        return data

    def post(self):
        """创建 Redis 服务器
        """
        # data 是字典对象，保存着由客户端发来的数据
        data = request.get_json()
        host = data['host']
        data['host'] = '127.0.0.1' if host == 'localhost' else host
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        # 201 是代表成功应答的状态码，请求已被成功处理并创建了新的资源
        return {'ok': True}, 201


class ServerDetailView(RestView):
    """该视图类用于对某个服务器进行查询、更新和删除操作
    """
    
    method_decorators = (TokenAuthenticate(), ObjectMustExists(Server))

    def get(self, object_id):
        """获取服务器详情
        """
        # schema.dump 返回一个 marshmallow.schema.MarshalResult 类的实例
        # 该实例保存两个字典：Redis 服务器实例字典和错误信息字典
        # 此 get 方法在 RestView 类的 dispatch_request 方法中被调用
        # 调用前已经加了装饰器，如有错误则触发 RestError 异常
        data, _ = ServerSchema().dump(g.instance)
        return data

    def put(self, object_id):
        """更新服务器
        """
        # 这里需要在实例化 schema 载体的时候给 context 属性赋值
        # 也就是将 object_id 对应的 Server 实例存入 self.context 字典里
        schema = ServerSchema(context={'instance': g.instance})
        # data 是字典对象，保存着由客户端发来的数据
        data = request.get_json()
        # partial=True 的作用是将 data 字典中的字段更新到 context.instance 中
        # 也就是说返回的 server 就是更新后的 g.instance 对象
        # 这是 ServerSchema 中的 create_or_update 方法实现的
        # 如果此参数的值为 False 则只对 data 这个字典进行反序列化
        # 这样的话 errors 字典里肯定有内容了
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除服务器
        """
        g.instance.delete()
        # 状态码 204 的意思是请求执行成功，但不跳转到新页面，也不刷新当前页面
        return {'ok': True}, 204


class ServerMetricsView(RestView):
    """获取 Redis 服务器监控信息
    """

    # 注意针对某个 Server 实例的请求须使用 ObjectMustBeExist 实例装饰器处理
    method_decorators = [TokenAuthenticate(), ObjectMustExists(Server)]

    # TODO 如何限制访问频率
    def get(self, object_id):
        return g.instance.get_metrics()
