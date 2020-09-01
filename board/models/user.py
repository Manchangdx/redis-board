import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from calendar import timegm
from marshmallow import Schema, fields, validate, post_load
from marshmallow import validates_schema, ValidationError

from .base import db, BaseModel
from ..common.errors import InvalidTokenError, AuthenticationError


class User(BaseModel):
    '''用户映射类
    '''

    id = db.Column(db.Integer, primary_key=True)
    wx_id = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    login_time = db.Column(db.DateTime)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self._password, pwd)

    @classmethod
    def authenticate(cls, identifier, pwd):
        '''根据用户名或邮箱认证用户并检查密码是否正确

        Args:
            identifier (str): 用户名或邮箱
            pwd (str): 密码

        Return:
            object: User 实例
        '''
        user = cls.query.filter(db.or_(cls.name==identifier,
                cls.email==identifier)).first()
        if not user or not user.verify_password(pwd):
            raise AuthenticationError(403, 'Authenticate failed.')
        return user

    @classmethod
    def wx_id_user(cls, wx_id):
        '''根据 wx_id 获取用户对象'''
        return cls.query.filter_by(wx_id=wx_id).first()

    def generate_token(self):
        '''生成 JSON WEB TOKEN

        首先创建载荷字典对象，其中包括用户ID、管理员判断、过期时间、刷新时间
        然后将载荷字典作为参数调用 jwt.encode 方法生成 token
        生成的 token 是二进制字符串，将其转换成 ASCII 字符串并返回
        '''
        # 设置 token 的过期时间为 1 天
        exp = datetime.utcnow() + timedelta(days=1)
        # token 过期后 10 分钟内，可以刷新旧的 token 获取新 token
        # datetime.datetime 对象的 utctimetuple 方法的返回值
        # 是 time.struct_time 对象，该对象为类 tuple 对象
        struct_time = (exp + timedelta(minutes=10)).utctimetuple()
        # calendar 模块中的 timegm 函数接收元组对象作为参数
        # 返回值是 GMT 计算时间戳的数值
        # 即从 1970 年 1 月 1 日到 struct_time 所指时间的秒数
        refresh_exp = timegm(struct_time)
        # 定义载荷，四个字段：ID 、管理员标识、过期时间、刷新时间
        payload = {
            'uid': self.id,
            'is_admin': self.is_admin,
            'exp': exp,
            'refresh_exp': refresh_exp
        }
        # 创建 token ，三个参数：载荷、秘钥、算法
        token = jwt.encode(payload, current_app.secret_key, algorithm='HS512')
        return token.decode()

    @classmethod
    def verify_token(cls, token, verify_exp=True):
        '''客户端向服务器发送请求时，验证 token

        Args:
            token (str): JSON WEB TOKEN
            verify_exp (bool): 是否验证 token 的过期时间

        Return:
            object: 返回用户对象（User 类实例）
        '''
        # verify_exp 的值如果为 False ，则不验证 token 的过期时间
        # 也就是说即使 token 过期也没关系，还是可以得到 payload
        # 如果 verify_exp 等于 True ，则验证 token 的过期时间
        # token 过期则抛出 ExpiredSignatureError 异常
        options = None if verify_exp else {'verify_exp': False}
        # 获取载荷，它是字典对象
        try:
            # 前两个位置参数：token 、秘钥
            # verify ：是否验证秘钥；algorithms ：算法列表
            # options ：其它选项；require_exp ：载荷必须有 exp 字段
            payload = jwt.decode(token, current_app.secret_key, verify=True,
                    algorithms=['HS512'], options=options, require_exp=True)
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(403, str(e))
        # 验证载荷中的关键字段是否存在
        conditions = ('uid' in payload, 'is_admin' in payload,
                'refresh_exp' in payload)
        if not all(conditions):
            raise InvalidTokenError(403, 'Invalid token.')
        # 检查是否过了允许刷新的时间，刷新时间是 token 过期后 10 分钟内
        if payload['refresh_exp'] < timegm(datetime.utcnow().utctimetuple()):
            raise InvalidTokenError(403, 'Invalid token.')
        # 经过上面的层层检查后
        if not (user := cls.query.get(payload['uid'])):
            raise InvalidTokenError(403, 'User not exists.')
        return user

    @classmethod
    def create_administrator(cls):
        '''创建管理员账号

        Return:
            name (str): 管理员账号名字
            password (str): 管理员账号密码
        '''
        name = 'Admin'
        password = '123456'
        if (admin := cls.query.filter_by(name=name).first()):
            return name, password
        email = 'admin@haha.com'
        admin = cls(name=name, email=email, is_admin=True)
        admin.password = password
        admin.save()
        return name, password


# marshmallow 是用来实现复杂的 ORM 对象与 Python 原生数据类型之间相互转换的库
# 相互转换需要一个中间载体，也就是 Schema 子类的实例
# 继承 Schema 创建子类，子类属性对应 User 类的属性，每个字段有一些约束
# User 实例转换为字典或 JSON 字符串的过程叫做序列化，反之叫做反序列化
# 序列化和反序列化需要对某些字段进行验证，使用 marshmallow 可以很好地实现需求
class UserSchema(Schema):
    '''User 实例序列化类
    '''

    id = fields.Integer(dump_only=True)
    wx_id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(2, 64))
    email = fields.Email(required=True, validate=validate.Length(2, 64))
    password = fields.String(load_only=True, validate=validate.Length(2, 128))
    is_admin = fields.Boolean()
    created_time = fields.DateTime(dump_only=True)
    updated_time = fields.DateTime(dump_only=True)
    login_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data):
        instance = self.context.get('instance', None)
        user = User.query.filter(db.or_(User.name==data.get('name'),
                User.email==data.get('email'))).first()
        # 创建用户时，user 的值为 None ，验证完毕
        # 修改用户时，如果修改的是用户的 name ，那么 user 的值为 None，验证完毕
        if user is None:
            return
        # 当 instance 是 None 时，肯定是创建用户操作
        # 创建用户时，不允许创建同名用户
        if instance is None:
            field = 'name' if data.get('name') else 'email'
            raise ValidationError('User is already existed.', field)
        # 修改用户时，instance 应该为 user
        if user != instance:
            # 修改用户名时，新用户名与另一个用户同名，会触发此异常
            field = 'name' if data.get('name') else 'email'
            raise ValidationError('User is already existed.', field)

    # 在反序列化时，如果通过了验证器的验证，则自动运行此方法
    @post_load
    def create_or_update(self, data):
        instance = self.context.get('instance', None)
        # 创建用户时，instance 是 None
        # 修改用户时，instance 是 Server 实例
        if instance is None:
            return User(**data)
        # FIXME 更新用户时可能会覆盖用户密码，如何处理？
        for key, value in data.items():
            setattr(instance, key, value)
        return instance
