"""定义了所有 API 对应的 URL
"""

from flask import Blueprint

from board.views.index import IndexView
from board.views.server import ServerList

# 创建 API 蓝图
api = Blueprint('api', __name__)

# 蓝图的 add_url_rule 方法定义路由及其视图函数
# 第一个参数为路径，第二个参数为视图函数（或类）
# 自定义 as_view 的参数作为视图函数（或类）名
# view_func 的值就是 flask.view.View 类 里定义的 view 函数
# 调用这个函数就是调用 IndexView 的父类 MethodView 的 dispatch_request 方法
# 此方法会调用 IndexView 的各种方法
# 例如浏览器使用 GET 方法访问主页时，由 IndexView 类中的 get 方法处理请求
api.add_url_rule('/', view_func=IndexView.as_view('index'))

# 当浏览器使用 GET 方法访问这个路径时
# 自动调用 ServerList 的 dispatch_request 方法
# 此方法在其父类 RestView 类中被定义
# 此方法的返回值就是发送给浏览器的 Response 对象
# 此方法内部会调用 ServerList 类中的 get 方法
api.add_url_rule('/servers/', view_func=ServerList.as_view('server_list'))
