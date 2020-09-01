'''该模块实现用户登录视图
'''

from datetime import datetime
from flask import request

from ..models import User
from ..common.errors import AuthenticationError
from ..common.rest import RestView


class AuthView(RestView):
    '''用户登录视图控制器类
    '''

    def post(self):
        '''此方法用于用户登录

        用户可以使用名字或邮箱登录，登录成功后返回用于后续认证的 token
        '''

        data = request.get_json()
        if not data:
            raise AuthenticationError(403, 'User name or password is required.')
        identifier = data.get('name') or data.get('email')
        password = data.get('password')

        if not identifier or not password:
            raise AuthenticationError(403, 'Circle value is not found.')

        user = User.authenticate(identifier, password)
        user.login_time = datetime.utcnow()
        user.save()
        return {'ok': True, 'token': user.generate_token()}
