"""定义了所有 API 对应的 URL
"""

from flask import Blueprint

from board.views.index import IndexView

# 创建 API 蓝图
api = Blueprint('api', __name__)

# 蓝图的 add_url_rule 方法定义路由及其视图函数
# 第一个参数为路径，第二个参数为视图函数
# 自定义 as_view 的参数作为视图函数名
# 例如浏览器使用 GET 方法访问主页时，由 IndexView 类中的 get 方法处理请求
api.add_url_rule('/', view_func=IndexView.as_view('index'))
