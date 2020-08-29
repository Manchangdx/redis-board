import json
from flask import url_for

from board.models import Server
from tests.base import TokenHeaderMixin


class TestServerListView(TokenHeaderMixin):
    '''测试查询 Redis 服务器列表和新增 Redis 服务器的 API
    '''

    endpoint = 'api.server_list'

    def test_get_servers(self, server, client, admin):
        '''获取 Redis 服务器列表'''

        # 客户端向服务器发送 GET 请求
        resp = client.get(url_for(self.endpoint),
                headers=self.token_header(admin))

        # RestView 视图基类会设置 HTTP 头部 Content-Type
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'
        # 访问成功后返回状态码 200
        assert resp.status_code == 200

        # resp 对象的 json 属性值是 views/server.py 中
        # ServerListView 类的 get 方法的返回值，它是一个列表
        servers = resp.json

        # 由于当前测试环境中只有一个 Redis 服务器，所以返回的数量为 1
        assert len(servers) == 1

        h = servers[0]
        assert h['name'] == server.name
        assert h['description'] == server.description
        assert h['host'] == server.host
        assert h['port'] == server.port
        assert 'created_time' in h
        assert 'updated_time' in h

    def test_create_server_success(self, db, client, admin):
        '''测试创建 Redis 服务器成功'''

        assert Server.query.count() == 0

        data = {
            'name': 'test',
            'description': '测试服务器',
            'host': '127.0.0.1'
        }

        # 客户端向服务器发送 POST 请求
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers=self.token_header(admin))

        assert resp.status_code == 201
        # resp.json 是 ServerListView 类的 post 方法的返回值元组的第一个元素
        assert resp.json == {'ok': True}
        assert Server.query.count() == 1

        # 这个服务器是 client.post 方法创建的
        # 创建过程也是在 ServerListView 类的 post 方法里
        server = Server.query.first()
        for key, value in data.items():
            assert getattr(server, key) == value

    def test_create_redis_server_fail(self, db, client, admin):
        '''测试创建 Redis 服务器失败'''

        data = {
            'name': 'test',
            'description': '测试服务器',
            'host': '127.0.0.1234'  # 设置无效的 IP 地址
        }
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers=self.token_header(admin))

        assert resp.status_code == 400
        # resp.json 的值是 RestView 类中 handle_error 方法的 data 变量
        # 它是一个字典
        d = resp.json
        assert d['ok'] is False
        assert d['message'] == 'String does not match expected pattern.'

    def test_create_duplicate_redis_server_fail(self, server, client, admin):
        '''测试创建重复的 Redis 服务器失败'''

        data = {
            'name': server.name,
            'description': '测试创建重复的服务器',
            'host': '127.0.0.1'
        }
        resp = client.post(url_for(self.endpoint), data = json.dumps(data),
                headers=self.token_header(admin))

        assert resp.status_code == 400
        d = resp.json
        assert d['ok'] is False
        assert d['message'] == 'Redis server is already existed.'


class TestServerDetailView(TokenHeaderMixin):
    '''测试查询、修改和删除某个 Redis 服务器的 API
    '''

    endpoint = 'api.server_detail'

    def test_get_server_success(self, server, client, admin):
        '''测试查询某个 Redis 服务器详情成功'''
        url = url_for(self.endpoint, object_id=server.id)
        resp = client.get(url, headers=self.token_header(admin))
        assert resp.status_code == 200
        # data 是服务器返回的映射类 Server 实例的字典
        data = resp.json
        for key, value in data.items():
            # data 中这两项的值是字符串，server 中这两项的值是 datetime 对象
            # 所以这两项就不判断了
            if key not in ('created_time', 'updated_time'):
                    assert getattr(server, key) == value

    def test_get_server_fail(self, server, client, admin):
        '''测试查询某个 Redis 服务器详情失败'''
        not_exist_id = 123
        url = url_for(self.endpoint, object_id=not_exist_id)
        resp = client.get(url, headers=self.token_header(admin))
        assert resp.status_code == 404
        assert resp.json == {'ok': False, 'message': 'Object not exists.'}

    def test_update_server_success(self, server, client, admin):
        '''测试更新某个 Redis 服务器成功'''
        # data 就是要更新的字段
        data = {'name': 'new_redis_client_name'}
        assert data['name'] != server.name
        assert Server.query.count() == 1
        resp = client.put(url_for(self.endpoint, object_id=server.id),
                data = json.dumps(data), headers=self.token_header(admin))
        assert resp.status_code == 200

    def test_update_server_fail(self, server, client, admin):
        '''测试更新某个 Redis 服务器失败'''
        assert Server.query.count() == 1
        second_server = Server(name='redis_test_2', description='test',
                host='127.0.0.1')
        second_server.save()
        assert Server.query.count() == 2
        # 尝试将 second_server 的 name 值改为 server 的 name 值
        # 这样的更改应该失败，以此来测试更新失败的流程是否顺畅
        data = {'name': server.name}
        resp = client.put(url_for(self.endpoint, object_id=second_server.id),
                data = json.dumps(data), headers=self.token_header(admin))
        assert resp.status_code == 400
        errors = {'ok': False, 'message': 'Redis server is already existed.'}
        assert resp.json == errors

    def test_delete_server_success(self, server, client, admin):
        '''测试删除某个服务器成功'''
        assert Server.query.count() == 1
        resp = client.delete(url_for(self.endpoint, object_id=server.id),
                headers=self.token_header(admin))
        assert resp.status_code == 204
        assert Server.query.count() == 0

    def test_delete_server_fail(self, client, admin):
        '''测试删除某个不存在的服务器失败'''
        not_exist_id = 123
        assert Server.query.get(not_exist_id) is None
        resp = client.delete(url_for(self.endpoint, object_id=not_exist_id),
                headers=self.token_header(admin))
        assert resp.status_code == 404
        errors = {'ok': False, 'message': 'Object not exists.'}
        assert resp.json == errors


class TestServerMetricsView(TokenHeaderMixin):
    '''测试获取 Redis 监控信息的 API
    '''

    endpoint = 'api.server_metrics'

    def test_get_metrics_success(self, server, client, admin):
        '''测试成功获取某个 Redis 服务器的监控信息'''
        resp = client.get(url_for(self.endpoint, object_id=server.id),
                headers=self.token_header(admin))
        assert resp.status_code == 200
        # resp.json 的值是 redis.info 方法返回的字典对象
        metrics = resp.json
        assert 'total_commands_processed' in metrics
        assert 'used_cpu_sys' in metrics
        assert 'used_memory' in metrics

    def test_get_metrics_fail(self, server, client, admin):
        '''测试获取某个 Redis 服务器的监控信息失败'''
        not_exist_id = 123
        assert Server.query.get(not_exist_id) is None
        resp = client.get(url_for(self.endpoint, object_id=not_exist_id),
                headers=self.token_header(admin))
        assert resp.status_code == 404
        errors = {'message': 'Object not exists.', 'ok': False}
        assert resp.json == errors
