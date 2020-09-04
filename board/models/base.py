from datetime import datetime 
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BaseModel(db.Model):
    """映射类基类
    """

    __abstract__ = True

    created_time = db.Column(db.DateTime, default=datetime.now)
    updated_time = db.Column(db.DateTime, default=datetime.now)

    def save(self):
        """将实例保存到数据库
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """将实例从数据库中删除
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        identifier = getattr(self, 'name', None) or self.id
        return f'<{self.__class__.__name__}: {identifier}>'
