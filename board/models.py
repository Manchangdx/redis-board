"""映射类文件
"""

from redis import StrictRedis, RedisError
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from board.common.rest import RestException


db = SQLAlchemy()


# 该类的实例即为 Redis 服务器
class Server(db.Model):
    """Redis 服务器模型
    """

    __tablename__ = 'redis_server'

    id = db.Column(db.Integer, primary_key=True)
    # unique = True 不能有同名的服务器
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    host = db.Column(db.String(15))
    port = db.Column(db.Integer, default=6379)
    password = db.Column(db.String())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def redis(self):
        return StrictRedis(self.host, self.port, password=self.password)

    def ping(self):
        """测试 Redis 服务器能否正常连接，返回值是布尔值"""
        try:
            return self.redis.ping()
        except RedisError:
            raise RestException(400, 
                    f"Redis server {self.host} can't be connected.")

    def get_metrics(self):
        """获取 Redis 服务器监控信息，返回值是字典"""
        try:
            return self.redis.info()
        except RedisError:
            raise RestException(400, 
                    f"Redis server {self.host} can't be connected.")


    def save(self):
        """保存到数据库中
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """从数据库中删除
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Server(name={self.name})>' 

