import json
from flask import url_for

from board.models import Server


class TestServerList:
    """测试 Redis 服务器列表 API
    """

    endpoint = 'api.server_list'

    def test_get_servers(self, server, client):
        """获取 Redis 服务器列表
        """
        # 客户端向服务器发送 GET 请求
        resp = client.get(url_for(self.endpoint))

        # RestView 视图基类会设置 HTTP 头部 Content-Type 为 json
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
        # 访问成功后返回状态码 200
        assert resp.status_code == 200

        # resp 对象的 json 属性值是 views/server.py 中
        # ServerList 类的 get 方法的返回值，它是一个列表
        servers = resp.json

        # 由于当前测试环境中只有一个 Redis 服务器，所以返回的数量为 1
        assert len(servers) == 1

        h = servers[0]
        assert h['name'] == server.name
        assert h['description'] == server.description
        assert h['host'] == server.host
        assert h['port'] == server.port
        assert 'updated_at' in h
        assert 'created_at' in h

    def test_create_server_success(self, db, client):
        """测试创建 Redis 服务器成功
        """
        assert Server.query.count() == 0
        data = {
            'name': 'test',
            'description': '测试服务器',
            'host': '127.0.0.1'
        }
        # 客户端向服务器发送 POST 请求
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                content_type='application/json')
        assert resp.status_code == 201
        # resp.json 是 ServerList 类的 post 方法的返回值元组的第一个元素
        assert resp.json == {'ok': True}
        assert Server.query.count() == 1
        # 这个服务器是 client.post 方法创建的
        # 创建过程也是在 ServerList 类的 post 方法里
        server = Server.query.first()
        for key, value in data.items():
            assert getattr(server, key) == value
