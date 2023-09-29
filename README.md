此文档最后更新于23/8/21，V2.0.0

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

**本项目基于企业内部机器人开发，使用企业内部机器人以获得更好的体验（作者没有尝试过普通机器人）**

**普通Webhook机器人已经于2023年9月1日停用，目前不再支持**

**强烈推荐Stream模式**，安全，快速，随处可用

# 需求

~~首先得有一个公网IP~~最新支持的Stream模式已经不需要了，还得拥有企业内部开发权限

你可以在启动机器人时传入空值（忘记是哪里了），在企业内部机器人的情况下，自带临时地址，无需手动输入webhook地址（没有完整体验，只能收发）

# 实现方法

通过使用 Flask服务端/Websocket 和装饰器进行函数调用的广播方法。

# 如何使用？

把导入的模块相应地替换成Dingraia中的模块即可。
~~具体请观看[Dingraia使用方法](https://wps.rainfd.net/dingraia%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95/)~~
没更新，建议别看

查看 `Usage.md` 获取基本用法

查看 [GitBook文档](https://dingraia.gitbook.io/dingraia)

由于Cloudflare和L服务器的原因，博客可能无法使用，如需帮助请联系我

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
app.send_message(group, MessageChain("Message"))  # 当然也可以传入任意对象，前提是支持str方法
# 从 element 导入元素即可发送 MarkDown, ActionCard等支持的消息卡片，如
```

## 发送文件

```python
app = Dingtalk()
app.send_message(group, Image('example.png'))
```

注意：机器人的发送提示实际是在准备发送时提示的，不一定代表确实发送成功

# 兼容度

30%...
（简单的模块只需要替换import的模块和app）

# TODO

让我想想...

# 最后要说

本项目基于[Graia](https://github.com/GraiaProject/Ariadne)QQ机器人框架模仿开发，
有兴趣的话去点个star吧


