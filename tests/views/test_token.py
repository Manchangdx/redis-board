"""该模块用于测试基于 token 的认证功能
"""

from flask import url_for

from tests.base import TokenHeaderMixin


class TestTokenAuth(TokenHeaderMixin):
    """通过获取服务器列表 API 测试 token 认证功能
    """

    endpoint = 'api.server_list'

    def test_auth_success(self, client, admin):
        """测试 token 认证成功
        """
        resp = client.get(url_for(self.endpoint), 
                headers = self.token_header(admin))
        assert resp.status_code == 200

    def test_auth_fail_with_no_token(self, client):
        """测试没有 token 时认证失败
        """
        resp = client.get(url_for(self.endpoint))
        assert resp.status_code == 401
        assert resp.json == {'message': 'Token not found.', 'ok': False}

    def test_auth_fail_with_invalid_header(self, client, admin):
        """测试无效 token 认证失败
        """
        headers = self.token_header(admin)
        headers.update({'Authorization': 'JWT'})
        resp = client.get(url_for(self.endpoint), headers=headers)
        assert resp.status_code == 401
        assert resp.json == {'message': 'Token missing.', 'ok': False}

    def test_auth_fail_with_no_admin(self, client, user):
        """测试非管理员用户 token 认证失败
        """
        resp = client.get(url_for(self.endpoint),
                headers = self.token_header(user))
        assert resp.status_code == 403
        assert resp.json == {'message': 'No permission.', 'ok': False}
