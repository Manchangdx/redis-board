from functools import wraps
from flask import g, request

from ..common.errors import RestError, AuthenticationError
from ..models import User


class ObjectMustExists:
    """该装饰器类用于判断 Server 映射类的某个实例是否存
    """

    def __init__(self, server_class):
        self.server_class = server_class

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kw):
            object_id = kw.get('object_id')
            if object_id is None:
                raise RestError(404, 'Object not exists.')
            if (obj := self.server_class.query.get(object_id)) is None:
                raise RestError(404, 'Object not exists.')
            g.instance = obj
            return func(*args, **kw)
        return wrapper


class TokenAuthenticate:
    """该装饰器用于用户登录时验证 HTTP Authorization 头所包含的 token
    """

    # admin 参数决定是否验证管理员权限
    def __init__(self, admin=False):
        self.admin = admin

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kw):
            # 获取请求对象的头部字段信息
            if not (pack := request.headers.get('Authorization', None)):
                raise AuthenticationError(401, 'Token not found.')
            # pack 须为 'jwt <token_value>' 这种形式，由空格分开两部分
            parts = pack.split()
            if parts[0].lower() != 'jwt':
                raise AuthenticationError(401, 'Invalid token header.')
            if len(parts) == 1:
                raise AuthenticationError(401, 'Token missing.')
            if len(parts) > 2:
                raise AuthenticationError(401, 'Invalid token.')
            token = parts[1]
            user = User.verify_token(token)
            # 如果需要验证用户的管理员身份
            if self.admin and not user.is_admin:
                raise AuthenticationError(403, 'No permission.')
            # 经过上面的层层验证
            g.user = user
            return func(*args, **kw)
        return wrapper
