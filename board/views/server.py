from flask import request, g

from board.common.rest import RestView
from board.models import Server, ServerSchema

class ServerList(RestView):
    """该视图类用于查询全部 Redis 服务器和添加新的 Redis 服务器
    """

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
        server, errors = ServerSchema().load(data)
        if errors:
            return errors, 400
        server.ping()
        server.save()
        # 201 是代表成功应答的状态码，请求已被成功处理并创建了新的资源
        return {'ok': True}, 201
