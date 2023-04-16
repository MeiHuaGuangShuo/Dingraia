# 这是什么？
这个是一个关于能套用Graia-Ariadne项目的小部分模块
并运行的异步钉钉机器人代码，用来运行 基础 的Webhook类型
的微型机器人，只实现了10%的功能，将来可能会完善。
作者是Python废物，请不要催，你行你上。

# 特点
支持协程，支持阻塞函数的并发，函数捕捉报错等

# 注意
本项目适用于一般聊天机器人开发，99%不适应生产环境
作者自身已经挂着该框架，保证框架确实可用

# 需求
首先得有一个公网IP，还得拥有企业内部开发权限

# 实现方法
通过使用简单的Flask服务端和非常简单的装饰器进行非常简单
的广播方法，非常容易在运作过程中报错。

# 如何使用？
把导入的模块相应地替换成Ding中的模块即可。
具体请观看[Dingraia使用方法](https://wps.lxyddice.top/meihuaguangshuo/dingraia%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95/)
由于cloudflare的原因，博客无法使用，如需帮助请联系我
## 接受函数
```python
@channel.use(ListenerSchema(listening_events[GroupMessage]))
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
## 发送消息
```python
app = Dingtalk()
app.send_message(MessageChain()) # 当然也可以传入任意对象，前提是支持str方法
# 从 element 导入元素即可发送 MarkDown, ActionCard等支持的消息卡片
```
注意：机器人的发送提示实际是在准备发送时提示的，不一定代表确实发送成功

# 兼容度？
10%...

# TODO
Flask服务端分离，Websocket链接，消息等待

# 最后要说
求梨膏，去看看[Graia](https://github.com/GraiaProject/Ariadne)项目吧，这个机器人框架真的很好用，
至少目前用起来真的很不错。

# 开源协议？
由于Graia项目使用 GNU AGPL-3.0 协议，故本开源协议相同

如果你觉得我的$hit代码侵犯了您的著作权，请联系我删除
