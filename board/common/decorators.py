from functools import wraps
from flask import g

from .rest import RestException


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
                raise RestException(404, 'Object not exists.')
            if (obj := self.server_class.query.get(object_id)) is None:
                raise RestException(404, 'Object not exists.')
            g.instance = obj
            return func(*args, **kw)
        return wrapper
