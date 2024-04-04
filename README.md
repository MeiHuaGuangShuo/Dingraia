此文档最后更新于24/4/5 v2.0.8

# 这是什么？

这个是一个关于能套用Graia-Ariadne部分项目的模块
并运行的异步钉钉机器人代码，用来运行 基础 的Webhook类型
的微型机器人，只实现了30%的功能，将来可能会完善。
作者是Python废物，请不要催，你行你上。

# 特点

支持协程（使用ensure_future执行），支持阻塞函数的并发（使用线程池），函数捕捉报错等，支持At，支持Stream方法

# 注意

本项目适用于一般聊天机器人开发，不建议用于生产环境

At可以传入Member实例（仅限企业内部机器人）与手机号，会自动识别

作者自身已经挂着该框架，保证框架确实可用 ~~如果懒癌发作不更新的另当别论~~

**自带文档可能更新不及时！（懒）**

**本项目基于企业内部机器人开发，使用企业内部机器人以获得更好的体验**

**普通Webhook机器人已经于2023年9月1日停用，目前不再支持（其他解决方法看下方 _发送消息_ 部分）**

**强烈推荐Stream模式**，安全，快速，随处可用

# 需求

~~首先得有一个公网IP~~最新支持的Stream模式已经不需要了，还得拥有企业内部开发权限

你可以在启动机器人时传入空值（忘记是哪里了），在企业内部机器人的情况下，自带临时地址，无需手动输入webhook地址（没有完整体验，只能收发）

# 实现方法

通过使用 Flask服务端/Websocket 和装饰器进行函数调用的广播方法。

# 如何使用？

把导入的模块相应地替换成Dingraia中的模块即可。

~~查看 `Usage.md` 获取基本用法~~

查看 [GitBook文档](https://dingraia.gitbook.io/dingraia)

由于Cloudflare和L服务器的原因，博客可能无法使用，如需帮助请联系我

在 `main_example.py` 中包含了一个和官方相似的示例，使用以下命令即可开启
```shell
python main_example.py -k <AppKey> -s <AppSecret>
```
发送任意算数即可进行计算，如 `1+1`
**（严禁部署在公共群聊，因为是使用eval进行运算的）**

发送 `/md` 即可发送一个 Markdown 卡片

## 安装

### Pypi

```shell
pip install dingraia
```

### Pypi豆瓣源(个人认为挺快的)

```shell
pip install dingraia -i https://pypi.douban.com/simple
```

### 更新

~~不会吧不会吧不会有人连pip怎么更新模块都不会就玩python了吧~~

```shell
pip install --upgrade dingraia
```

## 接收函数

```python
@channel.use(ListenerSchema(listening_events[GroupMessage]))  # 目前只支持GroupMessage
async def example(app: Dingtalk, group: Group):
    ...
```

当然，也可以这样

```python
@channel.use(ListenerSchema(listening_events[GroupMessage]))
def example(app: Dingtalk, group: Group):
    ...
```

它们都会并发执行
~~(你不会异步的话建议直接使用def，这样理论上效率会快一点)~~
框架全部是异步法方法，虽然提供了函数来运行异步函数，但是还是建议使用异步函数

## 发送消息

```python
await app.send_message(Target, MessageChain("Message"))  # 当然也可以传入任意对象，前提是支持str方法
# 从 element 导入元素即可发送 MarkDown, ActionCard等支持的消息卡片
# Target 可以是 Group, Member, OpenConversationId, Webhook, str(链接)
# 程序会自动判断方法进行发送
```

## 发送文件

```python
await app.send_message(group, Image('example.png'))
```

**注意：请不要使用** 
`MessageChain(Image(...))` 
**的方法来发送文件，否则会发送文字消息**

## 撤回消息
```python
res = await app.send_message(Target, mes)
# Target 必须是 OpenConversationId ，即只有通过API发送的文件才支持撤回
await app.recall_message(res)
```

若在同步函数中发送消息，可以使用 `app.sendMessage` 方法，参数与 `app.send_message` 一致

注意：机器人的发送提示实际是在准备发送时提示的，不一定代表确实发送成功

# 在同步函数中执行异步函数

使用如下代码即可
```python
from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events[GroupMessage]))
def sync_example(app: Dingtalk):
    app.run_coroutine(app.mute_all(...)) # 使用的是app.loop执行的
```

# 兼容度

20%...
（简单的模块只需要替换import的模块和app）

# TODO

让我想想...

# 衍生项目

[DingtalkStreamPushForward](https://github.com/MeiHuaGuangShuo/DingtalkStreamPushForward) - 
通过Stream模式转发钉钉服务器的消息到WebSocket和Webhook，支持本项目的连接

# 最后要说

本项目基于[Graia](https://github.com/GraiaProject/Ariadne)QQ机器人框架模仿开发，
有兴趣的话去点个star吧


