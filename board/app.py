import os
from flask import Flask

from board.views import api
from board.models import db
from board.config import configs


def create_app():
    """ 创建并初始化 Flask app
    """

    app = Flask(__name__)

    # 根据环境变量加载开发环境或生产环境配置
    env = os.environ.get('BOARD_ENV')

    if env in ('pro', 'prod', 'product'):
        app.config.from_object(configs['pro'])
    else:
        app.config.from_object(configs['dev'])

    # 从环境变量 RMON_SETTINGS 指定的文件中加载配置
    app.config.from_envvar('BOARD_SETTINGS', silent=True)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 注册 Blueprint
    app.register_blueprint(api)
    # 初始化数据库
    db.init_app(app)
    # 如果是开发环境则创建所有数据库表
    if app.debug:
        with app.app_context():
            db.create_all()
    return app
