'''该模块实现用户管理视图
'''

from flask import request, g

from ..common.rest import RestView
from ..common.errors import RestError
from ..models import User, UserSchema
from .decorators import ObjectMustExists, TokenAuthenticate


# TODO 实现解绑用户微信账号的 API


class UserListView(RestView):
    '''该视图类用于获取用户列表和创建新用户，只有管理员用户才有相关权限
    '''

    method_decorators = (TokenAuthenticate(admin=True), )

    def get(self):
        '''获取用户列表'''

        users = User.query.all()
        return UserSchema().dump(users, many=True).data

    def post(self):
        '''创建新用户'''
        
        data = request.get_json()
        user, errors = UserSchema().load(data)
        if errors:
            return errors, 400
        user.save()
        return {'ok': True}, 201


class UserDetailView(RestView):
    '''该视图类用于对某个用户进行查询、更新和删除操作
    '''

    method_decorators = (TokenAuthenticate(admin=True), ObjectMustExists(User))

    def get(self, object_id):
        '''获取用户信息'''

        data, _ = UserSchema().dump(g.instance)
        return data

    def put(self, object_id):
        '''更新用户信息'''
        
        schema = UserSchema(context={'instance': g.instance})
        data = request.get_json()
        server, errors = schema.load(data, partial=True)
        if errors:
            return errors, 400
        server.save()
        return {'ok': True}

    def delete(self, object_id):
        """删除用户"""
        
        # 管理员用户不可删除自身
        if g.user.id == g.instance.id:
            raise RestError(400, 'You can not delete yourself')

        g.instance.delete()
        return {'ok': True}, 204
