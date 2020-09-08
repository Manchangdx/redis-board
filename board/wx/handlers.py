"""消息处理
"""

import os
import re
from qqwry import QQwry
from wechatpy.events import SubscribeEvent
from wechatpy.messages import TextMessage
from wechatpy import create_reply
from flask import url_for

from ..models import User, Server


class BaseHandlerMeta(type):
    """消息处理器基类的元类
    """

    def __new__(metacls, cls_name, super_cls_tuple, args_dict):
        # 要求 BaseHandler 的子类必须实现 handler 属性或方法
        if cls_name != 'BaseHandler' and 'handle' not in args_dict:
            raise NotImplementedError('Must be implement handle method.')
        return super().__new__(metacls, cls_name, super_cls_tuple, args_dict)


class BaseHandler(metaclass=BaseHandlerMeta):
    """消息处理器基类
    """

    command = ''

    def __init__(self, wx_client=None):
        self.wx_client = wx_client

    def check_match(self, message):
        """检查消息是否匹配某种命令模式
        """
        if not isinstance(message, TextMessage):
            return False
        # 字符串的 startswith 方法检查字符串是否以指定的值开头
        if not message.content.strip().lower().startswith(self.command):
            return False
        return True


class SubscribeEventHandler(BaseHandler):
    """关注事件处理器，当用户关注公众号时触发的事件
    """

    def handle(self, message, *args, **kw):
        """处理消息的核心方法
        """
        # 如果消息的数据类型不是订阅事件类，直接返回 None
        if not isinstance(message, SubscribeEvent):
            return
        # 获取微信用户信息
        result = self.wx_client.user.get(message.source)
        # 返回给微信公众号 BaseReply 类的实例
        return create_reply('欢迎关注 Redis Board 公众号，小包子🐶', message)


class IPLocationHandler(BaseHandler):
    """处理 IP 消息，返回 IP 地理位置
    """

    command = 'ip'

    def __init__(self, wx_client=None):
        """获取 IP 地址数据
        """
        super().__init__()
        file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                '../static/qqwry.dat')
        self.q = QQwry()
        self.q.load_file(file)

    def handle(self, message):
        # 判断消息开头是否匹配
        if not self.check_match(message):
            return
        parts = message.content.strip().split()
        if len(parts) == 1 or len(parts) > 2:
            return create_reply('IP 地址无效', message)
        ip = parts[1]
        pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if not re.match(pattern, ip):
            return create_reply('IP 地址无效', message)
        result = self.q.lookup(ip)
        if result:
            return create_reply(result[0], message)
        return create_reply('未找到 IP 对应的地址', message)
            

class BindBaseHandler(BaseHandler):
    """处理绑定用户的消息
    """

    command = 'bind'

    def handle(self, message):
        # 判断消息是否匹配
        if not self.check_match(message):
            return
        user = User.get_user_via_wx_id(message.source)
        if user:
            return create_reply(f'你已经绑定到 {user.name}', message)
        # 参数分别是：API ，参数，_external=True 表示返回连接的绝对路径
        url = url_for('api.wx_bind', wx_id=message.source, _external=True)
        return create_reply(f'请打开链接完成用户绑定：{url}', message)


class RedisBaseHandler(BaseHandler):
    """处理 Redis 相关的消息
    """

    command = 'redis'

    def handle(self, message):
        if not self.check_match(message):
            return
        user = User.get_user_via_wx_id(message.source)
        if not user:
            return create_reply('未绑定 Redis Board 用户', message)
        parts = message.content.strip().split()
        if len(parts) == 1:
            return
        if parts[1].lower() == 'ls':
            return create_reply(self.server_list(), message)
        if parts[1].lower() == 'del':
            return create_reply(self.del_server(*parts[2:]), message)
        else:
            return

    def server_list(self):
        """获取 Redis 服务器列表的字符串
        """
        content = '\n'.join([f'{server.name} {server.host} {server.status}'
            for server in Server.query])
        if content:
            return content
        return '暂无 Redis 服务器'

    def del_server(self, *servers):
        """删除一个或多个服务器
        """
        if not servers:
            return '未指定需要删除的服务器'
        result = ''
        for name in servers:
            server = Server.query.filter_by(name=name).first()
            if server:
                server.delete()
                result += f'成功删除 {name}\n'
            else:
                result += f'未找到 {name}\n'
        return result.strip()


class EchoHandler(BaseHandler):
    """文本消息处理类
    """

    def handle(self, message, *args, **kw):
        if not isinstance(message, TextMessage):
            return 
        return create_reply(message.content, message)


default_handlers = (
        SubscribeEventHandler, 
        IPLocationHandler,
        BindBaseHandler, 
        RedisBaseHandler, 
        EchoHandler,
)
