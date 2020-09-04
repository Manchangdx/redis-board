'''测试首页 API
'''

from flask import url_for


class TestIndex:
    '''测试首页 API
    '''

    endpoint = 'api.index'

    def test_index(self, client):
        resp = client.get(url_for(self.endpoint))
        assert resp.status_code == 200
        assert b"<div id='app'></div>" in resp.data
