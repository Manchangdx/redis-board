"""测试用户管理 API 
"""

import json
from flask import url_for

from board.models import User
from tests.base import TokenHeaderMixin


class TestUserList(TokenHeaderMixin):
    """测试用户列表 API ，只有管理员用户才有相关操作权限
    """

    endpoint = 'api.user_list'

    def test_get_user_list(self, client, admin):
        """测试获取用户列表的 API
        """
        headers = self.token_header(admin)
        resp = client.get(url_for(self.endpoint), headers=headers)
        assert resp.status_code == 200
        users = resp.json
        assert len(users) == 1
        resp_user = users[0]
        assert resp_user['name'] == admin.name
        assert resp_user['email'] == admin.email
        assert 'created_time' in resp_user
        assert 'updated_time' in resp_user

    def test_create_user_success(self, client, admin):
        """测试创建用户成功
        """
        # 当前数据库中只有 admin 一个账号
        assert User.query.count() == 1
        # 新用户的相关数据
        data = {'name': 'test_user',
                'email': 'test_user@test.com',
                'password': '123456'}
        # 使用 /users/ 接口向服务器发送创建新用户的请求，并获得响应对象
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers=self.token_header(admin))
        assert resp.status_code == 201
        assert resp.json == {'ok': True}
        assert User.query.count() == 2
        new_user = User.query.filter_by(name=data['name']).first()
        assert new_user.email == data['email']
        # 测试新用户可以登录
        assert User.authenticate(data['name'], data['password']) == new_user
        assert User.authenticate(data['email'], data['password']) == new_user

    def test_create_user_fail_with_invalid_email(self, client, admin):
        """测试无效邮箱地址导致创建用户失败
        """
        data = {'name': 'test_user',
                'email': 'invalid_email.com',   # 无效的邮箱地址
                'password': '123456'}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers=self.token_header(admin))
        assert resp.status_code == 400
        errors = {'message': 'Not a valid email address.', 'ok': False}
        assert resp.json == errors

    def test_create_user_fail_with_duplicate_user(self, client, admin):
        """测试创建重复用户导致失败
        """
        data = {'name': admin.name,     # 重复的用户名导致创建失败
                'email': 'test_user@test.com',
                'password': '123456'}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers=self.token_header(admin))
        assert resp.status_code == 400
        errors = {'message': 'User is already existed.', 'ok': False}
        assert resp.json == errors


class TestUserDetail(TokenHeaderMixin):
    """测试用户详情 API ，也是只有管理员用户才有相关权限
    """

    endpoint = 'api.user_detail'

    def test_get_user_success(self, client, admin):
        """测试获取用户详情成功
        """
        url = url_for(self.endpoint, object_id=admin.id)
        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)
        assert resp.status_code == 200
        for key in ('name', 'email', 'is_admin'):
            assert resp.json[key] == getattr(admin, key)

    def test_get_no_exist_user_fail(self, client, admin):
        """测试获取不存在的用户失败
        """
        no_exist_user_id = 123
        url = url_for(self.endpoint, object_id=no_exist_user_id)
        headers = self.token_header(admin)
        resp = client.get(url, headers=headers)
        assert resp.status_code == 404
        assert resp.json == {'message': 'Object not exists.', 'ok': False}

    def test_update_user_success(self, client, admin):
        """测试更新用户成功
        """
        data = {'name': 'new_name'}
        assert data != admin.name
        assert User.query.count() == 1
        url = url_for(self.endpoint, object_id=admin.id)
        headers = self.token_header(admin)
        resp = client.put(url, data=json.dumps(data), headers=headers)
        assert resp.status_code == 200
        assert admin.name == data['name']

    def test_update_user_fail_with_same_name(self, client, admin, user):
        """测试由于与已存在用户同名导致更新失败
        """
        data = {'name': user.name}
        assert User.query.count() == 2
        url = url_for(self.endpoint, object_id=admin.id)
        headers = self.token_header(admin)
        resp = client.put(url, data=json.dumps(data), headers=headers)
        assert resp.status_code == 400
        errors = {'message': 'User is already existed.', 'ok': False}
        assert resp.json == errors

    def test_delete_user_success(self, client, admin, user):
        """测试删除用户成功
        """
        assert User.query.count() == 2
        url = url_for(self.endpoint, object_id=user.id)
        headers = self.token_header(admin)
        resp = client.delete(url, headers=headers)
        assert resp.status_code == 204
        assert User.query.count() == 1

    def test_admin_delete_itself_fail(self, client, admin):
        """测试管理员用户删除自身失败
        """
        assert User.query.count() == 1
        url = url_for(self.endpoint, object_id=admin.id)
        headers = self.token_header(admin)
        resp = client.delete(url, headers=headers)
        assert resp.status_code == 400
        assert User.query.count() == 1
        errors = {'message': 'You can not delete yourself', 'ok': False}
        assert resp.json == errors
