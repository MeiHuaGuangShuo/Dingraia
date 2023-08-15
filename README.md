# 这是什么？
这个是一个关于能套用Graia-Ariadne项目的小部分模块
并运行的异步钉钉机器人代码，用来运行 基础 的Webhook类型
的微型机器人，只实现了10%的功能，将来可能会完善。
作者是Python废物，请不要催，你行你上。

# 特点
支持协程，支持阻塞函数的并发，函数捕捉报错等，支持At含有userid的人员

# 注意
本项目适用于一般聊天机器人开发，不建议用于生产环境
作者自身已经挂着该框架，保证框架确实可用

# 需求
首先得有一个公网IP，还得拥有企业内部开发权限

# 实现方法
通过使用简单的Flask服务端和非常简单的装饰器进行非常简单
的广播方法。

# 如何使用？
把导入的模块相应地替换成Dingraia中的模块即可。
具体请观看[Dingraia使用方法](https://wps.rainfd.net/dingraia%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95/)

由于Cloudflare和lj服务器的原因，博客可能无法使用，如需帮助请联系我

## 安装
### Pypi
```shell
pip install dingraia
```
### Pypi豆瓣源(个人认为挺快的)
```shell
pip install dingraia -i https://pypi.douban.com/simple
```

## 接收函数
```python
@channel.use(ListenerSchema(listening_events[GroupMessage]))  # 目前只支持GroupMessage
async def example(group: Group):  # 此处暂不支持传入机器人实例
    ...
```
当然，也可以这样
```python
@channel.use(ListenerSchema(listening_events[GroupMessage]))
def example(group: Group):  # 此处暂不支持传入机器人实例
    ...
```
它们都会并发执行
~~(你不会异步的话建议直接使用def，这样理论上效率会快一点)~~
## 发送消息
```python
app = Dingtalk()
app.send_message(MessageChain("Message")) # 当然也可以传入任意对象，前提是支持str方法
# 从 element 导入元素即可发送 MarkDown, ActionCard等支持的消息卡片，如
app.send_message(MarkDown(...))
```
注意：机器人的发送提示实际是在准备发送时提示的，不一定代表确实发送成功

# 兼容度？
30%...

# TODO
Flask服务端分离，Websocket链接，消息等待

# 最后要说
本项目基于[Graia](https://github.com/GraiaProject/Ariadne)QQ机器人框架开发，
有兴趣的话去点个star吧


