"""用户登录认证功能测试
"""

import json
from flask import url_for

from board.models import User
from tests.fixtures import PASSWORD


class TestAuth:
    """测试用户登录
    """

    endpoint = 'api.login'

    def test_admin_login_success(self, client, admin):
        """测试管理员用户登录成功"""

        data = {'name': admin.name, 'password': PASSWORD}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers={'Content-Type':'application/json; utf-8'})
        assert resp.status_code == 200
        assert resp.json['ok'] is True
        resp_user = User.verify_token(resp.json['token'])
        assert admin == resp_user   

    def test_normal_user_login_success(self, client, user):
        """测试普通用户登录成功"""

        data = {'name': user.name, 'password': PASSWORD}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers={'Content-Type':'application/json; utf-8'})
        assert resp.status_code == 200
        assert resp.json['ok'] is True
        resp_user = User.verify_token(resp.json['token'])
        assert user == resp_user

    def test_login_fail_with_no_password(self, client, user):
        """测试未提供密码导致登录失败"""

        data = {'name': user.name}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers={'Content-Type':'application/json; utf-8'})
        assert resp.status_code == 403
        assert resp.json == {'message': 'Circle value is not found.', 
                'ok': False}

    def test_login_fail_with_wrong_password(self, client, user):
        """测试密码错误导致登录失败"""
        
        wrong_password = 'haha'
        data = {'name': user.name, 'password': wrong_password}
        resp = client.post(url_for(self.endpoint), data=json.dumps(data),
                headers={'Content-Type':'application/json; utf-8'})
        assert resp.status_code == 403
        assert resp.json == {'message': 'Authenticate failed.', 'ok': False}
