"""微信相关视图控制器
"""

import hashlib
from flask import request, current_app, abort, render_template, make_response
from flask.views import MethodView
from wechatpy import parse_message, create_reply

from ..models import User
from ..wx import wx_dispatcher
from ..common.rest import RestView


class WxView(MethodView):
    """微信相关视图控制器类
    """

    def check_signature(self):
        """验证请求的来源是微信用户
        """
        print('request.args:', request.args)
        signature = request.args.get('signature')
        if signature is None:
            abort(403)
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        msg = [current_app.config['WX_TOKEN'], timestamp, nonce]
        msg.sort()
        sha = hashlib.sha1()
        sha.update(''.join(msg).encode())
        if sha.hexdigest() != signature:
            abort(403)

    def get(self):
        """验证在微信公众号后台设置的 URL
        """
        self.check_signature()
        return request.args.get('echostr')

    def post(self):
        """处理微信消息
        """
        self.check_signature()
        # request.data 是 XML 标记语言编写的字符串
        # 使用 parse_message 可以将其处理成 OrderedDict 有序字典对象
        # 其 content 属性值就是微信用户发送的信息
        msg = parse_message(request.data)
        # 调用 wx_dispatcher 的 dispatch 方法处理消息
        # 该方法收集了全部自定义的用以处理不同类型的消息的对象
        reply = wx_dispatcher.dispatch(msg)
        # BaseReply 的实例的 render 方法的返回值是 XML 字符串
        return reply.render()


class WxBindView(RestView):
    """微信用户绑定账户页面
    """

    def get(self, wx_id):
        """获取绑定用户的页面
        """
        result = render_template('wx_bind.html')
        return make_response(result, 200)

    def post(self, wx_id):
        """绑定用户
        """
        data = request.get_json()
        # 如果请求对象中携带的数据不全
        if data is None or 'name' not in data or 'password' not in data:
            return {'ok': False, 'message': '无效的用户数据'}, 400
        # 验证用户信息并返回用户对象
        user = User.authenticate(data['name'], data['password'])
        # 如果用户的 wx_id 属性值不为空，表明该用户已经绑定了某个微信用户
        if user.wx_id is not None:
            data = {'ok': False, 
                    'message': '该 Redis Board 用户已绑定到其它微信账户'}
            return data, 400
        user.wx_id = wx_id
        user.save()
        return {'ok': True, 'message': '绑定成功'}

