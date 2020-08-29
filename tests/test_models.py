from board.models import Server
from board.common.rest import RestException


class TestServer:
    """测试 Server 映射类相关功能
    """

    def test_save(self, db):
        assert Server.query.count() == 0
        server = Server(name='test', host='127.0.0.1')
        server.save()
        assert  Server.query.count() == 1
        assert Server.query.first() == server

    def test_delete(self, db, server):
        assert Server.query.count() == 1
        server.delete()
        assert Server.query.count() == 0

    def test_ping_success(self, db, server):
        assert server.ping() is True

    def test_ping_failed(self, db):
        server = Server(name='test', host='127.0.0.1', port=6399)
        try:
            server.ping()
        except RestException as e:
            assert e.code == 400
            message = f"Redis server {server.host} can't be connected."
            assert e.message == message
