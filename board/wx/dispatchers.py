"""微信消息处理逻辑
"""

from wechatpy import WeChatClient
from wechatpy.replies import BaseReply, EmptyReply

from .handlers import default_handlers


class MessageDispatcher:
    """该类调用各类消息处理器处理信息
    """

    def __init__(self, app=None):
        self.handlers = []
        if app:
            self.init_app(app)

    def init_app(self, app):
        """初始化应用
        """
        # 创建微信客户端需提供两个参数 appid 和 secret 
        # 它们分别对应微信公众号页面上的 appID 和 appsecret 字段
        self.wx_client = WeChatClient(app.config.get('WX_APP_ID'),
                app.config.get('WX_SECRET'))

        for handler_class in default_handlers:
            # handler 为 handlers 模块中的消息处理类的实例
            handler = handler_class(wx_client=self.wx_client)
            # 将实例添加到 self.handlers 列表中
            self.register_handler(handler)

    def register_handler(self, handler):
        """添加消息处理类的实例到 self.handlers 列表
        """
        self.handlers.append(handler)

    def dispatch(self, msg):
        """调用此私有方法处理微信公众号发来的消息
        """
        return self._reply(msg)

    def _reply(self, msg):
        """处理消息的核心方法
        """
        for handler in self.handlers:
            # 每个消息处理器会判断 msg 的数据类型
            # 如果不符合，直接返回 None
            # 如果符合，返回处理之后的 BaseReply 实例
            reply = handler.handle(msg)
            if isinstance(reply, BaseReply):
                return reply
        # 如果微信公众号发来的消息不符合任何一个消息处理器的处理规则
        # 返回 EmptyReply 这个类的实例
        return EmptyReply()
