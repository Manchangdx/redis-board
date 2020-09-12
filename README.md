# Redis Board

通过微信公众号监控 Redis 服务器。

项目环境要求：

- 操作系统 Linux / macOS
- 编程语言 Python 3.8
- 项目框架 Flask 1.1.2

## 项目启动流程

#### 1、安装项目所需第三方库

```bash
$ pip install -r requirements.txt
```

#### 2、安装 ngrok

下载地址：https://ngrok.com/download

#### 3、设置环境变量

```bash
$ export FLASK_APP=app.py BOARD_ENV=pro BOARD_SECRET_KEY=xxxxxx
$ export WX_APP_ID=xxxxxx WX_SECRET=xxxxxxx
```

#### 4、初始化数据库，创建数据表，添加管理员用户

```bash
$ flask init-db
```

#### 5、启动应用

```bash
$ flask run
```

#### 6、启动 ngrok 代理

```bash
$ ngrok http -region au 5000
```

启动项目后，启动 ngrok 做反向代理，随机创建外网地址用来接收微信公众号发起的请求。

#### 7、客户端操作

浏览器打开首页，自动跳转到登录页。管理员邮箱：`admin@haha.com` 密码：`123456` 。

登录成功后自动跳转到 Redis 服务器列表页。

## 项目简介

这是一个内部应用，分为如下四部分。

#### Redis 服务器

在 redis-board/board/models/server.py 中创建 Redis 服务器映射类，该类的实例就是 Redis 服务器对象。

所谓的 Redis 服务器对象，本质是可以向服务器发送请求的客户端，能够发送的请求包括测试服务器能否正常连接、获取服务器监控信息等。

#### 用户功能

按照权限区分，用户有两种：管理员用户和非管理员用户。

管理员用户对用户和服务器有完全的 “增删改查” 权限，非管理员用户只有 “查” 的权限。

#### 微信公众号

微信公众号的基础接口提供文本数据的转发。

微信用户关注此公众号后，向公众号发送文本信息，公众号转发给应用程序，应用程序根据文本信息作出相应的处理。

微信用户操作 Redis 服务器之前，要发出 bind 文本，应用程序返回一个绑定用户的表单。正确填写表单使得微信用户与应用程序的用户绑定，微信用户就获得了应用程序用户的角色权限。

#### 测试

使用 pytest 实现了测试功能，代码在 redis-board/tests 目录下。

设置好环境变量后，终端执行 `pytest` 命令即可测试除微信公众号之外的功能。
