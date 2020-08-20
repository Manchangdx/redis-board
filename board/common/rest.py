class RestException(Exception):
    """异常基类
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__()
