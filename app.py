"""应用入口文件
"""

import urllib

from board.app import create_app
from board.models import db


app = create_app()


@app.cli.command()
def init_db():
    """初始化数据库
    """
    db.create_all()
    print(f"Sqlite3 database file is {app.config['SQLALCHEMY_DATABASE_URI']}.")