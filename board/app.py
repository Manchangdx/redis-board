import os
from flask import Flask

from .config import configs
from .models import db
from .views import api
from .wx import wx_dispatcher


def create_app():
    """ 创建并初始化 Flask app
    """

    app = Flask(__name__)

    # 根据环境变量加载开发环境或生产环境配置
    env = os.environ.get('BOARD_ENV')

    if env in ('pro', 'prod', 'product'):
        app.config.from_object(configs['Pro'])
    else:
        app.config.from_object(configs['Dev'])

    # 注册蓝图 
    app.register_blueprint(api)

    # 在应用初始化的时候，app 设置了一个 extensions 属性，属性值是空字典
    # 下面这步操作的结果之一是向 app.extensions 里添加一组键值对
    # 键是 'sqlalchemy' ，值是 flask_sqlalchemy.__init__._SQLAlchemyState 类的实例
    # 该实例的 db 属性值就是这个 db ，connectors 属性值是空字典
    db.init_app(app)
    
    # 这步操作用于创建微信客户端以及注册消息处理器，其中用到了 app 的配置项
    wx_dispatcher.init_app(app)

    # 如果是开发环境则创建所有数据库表
    if app.debug:
        with app.app_context():
            # 这块儿根据映射类创建数据表，其实可以不用应用上下文
            # 给 create_all 方法加个参数 app=app 就行了
            # 因为 db 本身作为 flask_sqlalchemy.__init__.SQLAlchemy 类的实例
            # 它的 create_all 方法会调用自身的 get_app 方法获取应用
            # 而后者可以从上下文代理对象 current_app 中获取
            # 所以要先创建一个应用上下文对象，以便上下文代理对象获取当前应用
            # 代理对象 current_app 的作用之一是
            # 连接数据库时提供其配置项 SQLALCHEMY_DATABASE_URI
            # 代理对象 current_app 的作用之二是
            # 创建数据表时利用 current_app.extensions['sqlalchemy']
            # 也就是 _SQLAlchemyState 类的实例的 db 属性获取 db
            db.create_all()

    return app
