import pytest

from board.app import create_app
from board.models import db as database, Server


@pytest.fixture
def app():
    """应用对象"""

    return create_app()


@pytest.yield_fixture
def db(app):
    """数据库"""

    with app.app_context():
        # 创建全部数据表
        database.create_all()
        yield database
        # yield 关键字实现的功能是：
        # 调用 db 相关的测试完毕后，自动执行下面的语句删除数据库表
        database.drop_all()


@pytest.fixture
def server(db):
    """Redis 服务器"""
    
    server = Server(name='redis_test', description='This is a test server.',
             host='127.0.0.1', port=6379)
    server.save()
    return server
