"""该模块用于实现 Redis 服务器映射类及其相应的序列化类
"""

from redis import StrictRedis, RedisError
from marshmallow import Schema, fields, validate, post_load
from marshmallow import validates_schema, ValidationError

from .base import db, BaseModel
from ..common.errors import RestError


# 该类的实例即为连接 Redis 服务器的客户端对象
class Server(BaseModel):
    """Redis 客户端模型
    """

    __tablename__ = 'redis_server'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(512))
    host = db.Column(db.String(15))
    port = db.Column(db.Integer, default=6379)
    password = db.Column(db.String())

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


# marshmallow 是用来实现复杂的 ORM 对象与 Python 原生数据类型相互转换的库
# 例如 Server 映射类实例与 JSON 对象相互转换
# 相互转换需要一个中间载体，这个中间载体就是 Schema 子类的实例
# 继承基类 Schema 创建子类，属性对应 Server 类的属性，每个字段都有一些约束
# Server 实例转换为字典或 JSON 字符串的过程叫做序列化
# JSON 字符串或字典转换为 Server 实例的过程叫做反序列化
# 序列化和反序列化需要对某些字段进行验证，使用 marshmallow 可以很好地实现需求
class ServerSchema(Schema):
    """Redis服务器记录序列化类
    """

    # 序列化是将 Server 实例作为参数调用 dump 或 dumps 方法
    # 返回一个字典对象或 JSON 字符串
    # 反序列化是将字典对象或 JSON 字符串作为参数调用 load 或 loads 方法
    # 返回一个 Server 实例
    # dump_only 表示该字段只能序列化，load_only 表示该字段只能反序列化
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    description = fields.String(validate=validate.Length(0, 512))
    # host 必须是 IPv4 地址，通过正则验证
    host = fields.String(required=True,
            validate=validate.Regexp(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'))
    port = fields.Integer(validate=validate.Range(1024, 65536))
    password = fields.String()
    updated_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # 使用 validates_schema 装饰器创建验证器函数，函数名自定义
    # 该方法在 self 调用 load 或 loads 方法进行反序列化时自动运行
    # 也就是将 JSON 对象转换成 Server 实例时会运行
    # 参数 data 是一个字典对象
    @validates_schema
    def validate_schema(self, data):
        # 如果字典中没有 port 字段，将其设为默认值 6379
        if 'port' not in data:
            data['port'] = 6379
        # 当前类继承了 marshmallow.schema.Schema 类
        # 而 Schema 继承了同模块下的 BaseSchema 类
        # BaseSchema.__init__ 中定义了实例属性 context 的默认值为空字典
        # 如果服务器已经存在，在相关请求出现时
        # self.context 的 instance 字段值会被定义为 Server 实例
        instance = self.context.get('instance', None)
        server = Server.query.filter_by(name=data['name']).first()
        # 创建服务器时，server 的值为 None，验证完毕
        # 更新服务器时，如果更新服务器的 name ，server 的值也是 None ，验证完毕
        if server is None:
            return
        # 创建服务器时，反序列化时不允许创建已经存在的服务器
        if instance is None:
            raise ValidationError('Redis server is already existed.', 'name')
        # 更新服务器时，instance 应该为 Server 实例
        if server != instance:
            # 如果更新服务器的名字时用了另一个服务器的名字，会触发此异常
            raise ValidationError('Redis server is already existed.', 'name')

    # 在反序列化时，如果通过了验证器的验证，则自动运行此方法
    @post_load
    def create_or_update(self, data):
        instance = self.context.get('instance', None)
        # 添加服务器时，instance 是 None
        # 更新服务器时，instance 是 Server 实例
        if instance is None:
            return Server(**data)
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
