"""测试基类
"""


class TokenHeaderMixin:
    """针对需要用户登录的验证提供带有 token 的头部
    """

    def token_header(self, user):
        """生成带有 jwt token 的头部并返回
        """
        value = f'JWT {user.generate_token()}'
        return {'Authorization': value,
                'Content-Type': 'application/json; charset=utf-8'}
