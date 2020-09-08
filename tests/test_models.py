from board.models import Server
from board.common.errors import RestError


class TestServer:
    """测试 Server 映射类相关功能
    """

    # 此方法内部未直接用到 db ，但运行代码时要连接数据库
    # 所以必须提供 db 参数，也就是调用 fixtures 里的 db 函数
    def test_save(self, db):
        # 初始状态下，数据库中没有保存任何 Redis 服务器
        assert Server.query.count() == 0
        server = Server(name='test', host='127.0.0.1')
        server.save()
        assert Server.query.count() == 1
        assert Server.query.first() is server

    # 此方法在运行时需要连接数据库，但无需提供 db 参数
    # 因为 server 参数会运行 fixtures.server 函数，此函数有个 db 参数
    def test_delete(self, server):
        assert Server.query.count() == 1
        server.delete()
        assert Server.query.count() == 0

    def test_ping_success(self, server):
        assert server.ping() is True

    def test_ping_fail(self, db):
        server = Server(name='haha', host='127.0.0.1', port=6399)
        server.save()
        try:
            server.ping()
        except RestError as e:
            assert e.code == 400
            message = f'Redis server {server.host} can\'t be connected.'
            assert e.message == message
