# Redis Board

通过微信公众号监控 Redis 服务器

## 项目启动流程

#### 1、安装项目所需第三方库

pip install -r requirements.txt

#### 2、设置环境变量

export FLASK_APP=app.py BOARD_ENV=pro BOARD_SECRET_KEY=xxxxxx

export WX_APP_ID=xxxxxx WX_SECRET=xxxxxxx

#### 3、初始化数据库、创建数据表、添加管理员用户

flask init-db

#### 4、启动应用

flask run
