import pytest

from board.app import create_app
from board.models import Server, User
from board.models import db as database


PASSWORD = '123456'


@pytest.fixture
def app():
    """应用对象"""

    return create_app()


@pytest.yield_fixture
def db(app):
    """连接数据库的 db 对象"""

    # 连接数据库需要用到应用，此处创建一个临时的应用上下文对象
    with app.app_context():
        database.create_all()
        yield database
        database.drop_all()


# 此函数须提供一个 db 参数
# 在创建服务器并将其存储到数据库时，需要预先连接数据库
@pytest.fixture
def server(db):
    """服务器对象，也就是 Server 映射类的实例"""

    server = Server(name='test', host='127.0.0.1')
    server.save()
    return server

@pytest.yield_fixture
def client(app):
    """客户端"""

    # 这里使用 with 关键字是为了保证测试结束后清除 client
    with app.test_client() as client:
        yield client


@pytest.fixture
def user(db):
    """普通用户"""

    user = User(name='test_user', email='test@haha.com', is_admin=False)
    user.password = PASSWORD
    user.save()
    return user


@pytest.fixture
def admin(db):
    """管理员用户"""

    user = User(name='admin', email='admin@haha.com', is_admin=True)
    user.password = PASSWORD
    user.save()
    return user
