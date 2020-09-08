"""该模块实现用户登录视图
"""

from datetime import datetime
from flask import request

from ..models import User
from ..common.errors import AuthenticationError
from ..common.rest import RestView


class AuthView(RestView):
    """用户登录视图控制器类
    """

    # 应用程序启动后，前端代码会自动提供一个带有登录表单的页面
    # 填写表单并点击提交后，服务器收到请求，交由下面的方法处理
    def post(self):
        """此方法用于用户登录，登录成功后返回用于后续认证的 token
        """

        data = request.get_json()
        if not data:
            raise AuthenticationError(403, 'User name or password is required.')
        identifier = data.get('name') 
        password = data.get('password')

        if not identifier or not password:
            raise AuthenticationError(403, 'Circle value is not found.')

        # 验证账号密码，此方法返回对应的 User 实例
        user = User.authenticate(identifier, password)
        user.login_time = datetime.now()
        user.save()

        # 前端代码会获取下面的返回值中的 token 字段值（字符串）
        # 将其赋值给某个变量 XXXTOKEN 
        # 再调用 request.headers.set 方法将 'JWT ' 与 XXXTOKEN 字符串合起来
        # 赋值给 Authorization 字段
        # 以后每次请求都会携带 Authorization 字段
        return {'ok': True, 'token': user.generate_token()}
        # 登录成功后，前端代码自动控制跳转页面到服务器列表页
