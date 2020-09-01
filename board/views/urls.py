"""定义了所有 API 对应的 URL
"""

from flask import Blueprint

from .index import IndexView
from .auth import AuthView
from .server import ServerListView, ServerDetailView, ServerMetricsView
from .user import UserListView, UserDetailView

# 创建 API 蓝图
api = Blueprint('api', __name__)

# 蓝图的 add_url_rule 方法定义路由及其视图函数
# 第一个参数是路由字符串
# 第二个参数是调用视图类的 as_view 方法得到的返回值，它是视图类的实例
# 调用 as_view 方法所提供的参数被赋值给视图类的实例的 __name__ 属性
# 应用 app（也就是 flask.Flask 类的实例）有个 view_functions 属性，属性值是字典
# 以首页为例，当 app 调用 register_blueprint 方法注册蓝图时
# 会把 'api.index' 作为 key , view_func 作为 value 的键值对
# 添加到自身的 view_functions 属性字典中
# 当浏览器发送首页请求时，应用程序根据路由获取 endpoint 值，也就是 'api.index'
# 再根据这个值从 app.view_functions 中获取对应的 view_func ，也就是视图类的实例
# 并调用该实例的 dispatch_request 方法，调用时会提供请求类型之类的参数
# 例如浏览器发起 GET 请求访问主页时
# IndexView 类的实例的 dispatch_request 方法内部会调用实例自身的 get 方法来处理
# 最后 dispatch_request 返回一个响应对象

# 首页
api.add_url_rule('/', view_func=IndexView.as_view('index'))

# 登录
api.add_url_rule('/login', view_func=AuthView.as_view('login'))

# 查询 Redis 服务器列表和新增 Redis 服务器
api.add_url_rule('/servers/', view_func=ServerListView.as_view('server_list'))

# 查询、修改或删除某个 Redis 服务器
api.add_url_rule('/servers/<int:object_id>', 
        view_func=ServerDetailView.as_view('server_detail'))

# 获取 Redis 服务器监控信息
api.add_url_rule('/servers/<int:object_id>/metrics',
        view_func=ServerMetricsView.as_view('server_metrics'))

# 用户管理
api.add_url_rule('/users/', view_func=UserListView.as_view('user_list'))
api.add_url_rule('/users/<int:object_id>',
        view_func=UserDetailView.as_view('user_detail'))
