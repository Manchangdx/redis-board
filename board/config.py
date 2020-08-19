"""应用配置文件
"""

import os


class DevConfig:
    """开发环境配置
    """

    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TEMPLATES_AUTO_RELOAD = True


class ProductConfig(DevConfig):
    """生产环境配置
    """

    DEBUG = False
    # sqlite 数据库文件路径
    # os.getcwd() 获取执行程序时所在的目录的绝对路径
    # replace 方法是为了兼容 Windows 系统中使用反斜杠表示目录结构的情况
    path = os.path.join(os.getcwd(), 'board.db').replace('\\', '/')
    # 数据库的地址格式：'sqlite://host:port/path' ，host:port 为空
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{path}'


configs = {
        'dev': DevConfig,
        'pro': ProductConfig
}
