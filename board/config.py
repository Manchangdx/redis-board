"""应用配置文件
"""

import os


class DevConfig:
    """开发环境配置类
    """

    SECRET_KEY = os.environ.get('BOARD_SECRET_KEY') or 'asdf'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    WX_TOKEN = 'board-token'
    WX_APP_ID = os.environ.get('WX_APP_ID')
    WX_SECRET = os.environ.get('WX_SECRET')


class ProConfig(DevConfig):
    """生产环境配置类
    """

    DEBUG = False
    # sqlite 数据库文件路径
    # os.getcwd() 获取执行程序时所在的目录的绝对路径
    # replace 方法是为了兼容 Windows 系统中使用反斜杠表示目录结构的情况
    path = os.path.join(os.getcwd(), 'board.db').replace('\\', '/')
    # 数据库的地址格式：'sqlite://host:port/path' ，host:port 为空
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{path}'


configs = {
        'Dev': DevConfig,
        'Pro': ProConfig
}
