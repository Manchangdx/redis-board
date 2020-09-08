"""异常类模块
"""

class RestError(Exception):
    """继承异常基类创建的异常类，该类为项目中所有自定义异常类的基类
    """

    # code 是 HTTP 状态码，message 是错误信息
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self)


class RedisConnectError(RestError):
    """连接服务器异常
    """

    pass


class InvalidTokenError(RestError):
    """无效的 Token 异常
    """

    pass


class AuthenticationError(RestError):
    """认证异常
    """

    pass
