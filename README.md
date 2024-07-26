此文档最后更新于24/7/27 `v2.0.9`

# 这是什么？

这个是一个关于能套用Graia-Ariadne部分项目的模块
并运行的异步钉钉机器人代码，用来运行 基础 的Webhook类型
的微型机器人，只实现了30%的功能，将来可能会完善。

新功能/建议/Bug 请提出 [Issue](https://github.com/MeiHuaGuangShuo/Dingraia/issues/new/choose)

# 特点

支持协程（使用ensure_future执行），支持阻塞函数的并发（使用线程池），函数捕捉报错等，支持At，支持Stream方法

支持 文字, Markdown FeedCard, ActionCard和文件的发送

支持应答机制 (HTTP, Stream, OutGoing未专门适配，理论支持)

## 功能一览

- 应答机制
    - HTTP 回调
    - Stream 回调
    - OutGoing..?
- 使用方式
    - 脚本运行
    - 控制台模式
- 群聊功能
    - 发送消息
        - 文字
        - Markdown
        - ActionCard
        - FeedCard
    - 发送文件
        - 普通文件
        - 图片
        - 音频
        - ~~视频~~ (时长判断存疑)
    - 撤回消息 (钉钉限制仅通过API发送的文件才可以撤回)
    - 发送互动卡片 (自行构造JSON数据)
        - 预设 Markdown 卡片
    - 改变卡片内容 (自行构造JSON数据)
    - 创建群
    - 获取群消息
    - 获取部门消息
    - 获取用户消息
    - 删除用户 (组织)
    - 创建用户 (组织)
    - 更新用户信息 (组织)
    - 复制群 (未来可能移除)
    - 更新群信息
        - 同源功能
            - 更新群标题
            - 改变群主
            - 全体禁言/解禁
    - 解散群 (伪)
    - 踢出用户 (群)
    - 添加用户 (群)
    - 设置/取消管理员 (群)
    - 禁言用户/解除禁言用户 (群)
    - 设置机器人离线卡片 (Stream 独占)
    - 手动上传文件
    - 下载文件
- 特别功能
    - HTTP & Stream 同时运行
    - 运行周期内上传文件缓存
    - 即时重载 Debug 模式
    - ~~即时载入/卸载模块~~ (有Bug，仅可载入，无法卸载)

# 注意

本项目适用于一般聊天机器人开发，不建议用于生产环境

At可以传入Member实例（仅限企业内部机器人）与手机号，会自动识别

作者自身已经挂着该框架，保证框架确实可用 ~~如果懒癌发作不更新的另当别论~~

**自带文档可能更新不及时！（懒）**

**本项目基于企业内部机器人开发，使用企业内部机器人以获得更好的体验**

**普通Webhook机器人已经于2023年9月1日停用，目前不再支持（其他解决方法看下方 _发送消息_ 部分）**

**强烈推荐Stream模式**，安全，快速，随处可用

使用 **场景群** 获取最完整体验

# 需求

拥有企业内部开发权限

你可以在启动机器人时传入空值（忘记是哪里了），在企业内部机器人的情况下，自带临时地址，无需手动输入webhook地址（没有完整体验，只能收发）
> 仅 `HTTP` 模式下支持此特性

# 实现方法

通过使用 aiohttp异步服务端/Websockets 和装饰器进行函数调用的广播方法。

# 如何使用？

把导入的模块相应地替换成Dingraia中的模块即可。

查看 [GitBook文档](https://dingraia.gitbook.io/dingraia)

在 `main_example.py` 中包含了一个和官方相似的示例，使用以下命令即可开启
```shell
python main_example.py -k <AppKey> -s <AppSecret>
```
发送任意算数即可进行计算，如 `1+1`
**（严禁部署在公共群聊，因为是使用eval进行运算的）**

发送 `/md` 即可发送一个 Markdown 卡片

若命令错误会自动发送提示卡片

## 安装

### Pypi

```shell
pip install dingraia
```

### Pypi 清华源加速

#### 设置永久使用

```shell
python -m pip install --upgrade pip
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 安装
```shell
pip install dingraia -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 升级 Dingraia
```shell
pip install --upgrade dingraia
```

## 控制台模式

程序使用 `IPython` 以实现控制台功能，用户可以直接在控制台执行对应函数，方便操作

> 推荐入口脚本名称为 `main.py` ， 方便使用程序

**注意：在入口脚本中一定要使用 `if __name__ == '__main__'`
并在其后面使用 `app.start()`，否则会直接运行程序**

### 使用方法

```shell
python -m dingraia
```

## Debug 模式

### 即时刷新文件模式

程序使用 `Watchdog` 监听**当前环境文件夹下的所有以`.py``结尾的文件**
，当文件发生变动时将自动停止并重新运行程序。

#### 使用方法

```shell
python -m dingraia.debug main.py
```

### 程序 Debug 模式

设置环境变量 `Debug=1` 即可

`Linux` 使用 `export DEBUG=1`

`PowerShell` 使用 `$env:DEBUG=1`

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

它们都会并发执行。但是不推荐使用同步函数，因为框架全部是异步法方法，虽然提供了函数 `run_coroutine` 来运行异步函数，但是还是建议使用原生异步函数，
或者在异步函数中使用 `dingraia.util.async_exec` 的 `io_bound` 和 `cpu_bound` 运行同步函数

## 发送消息

```python
await app.send_message(Target, MessageChain("Message"))
# 当然也可以传入任意对象，前提是支持str方法
# 从 element 导入元素即可发送 MarkDown, ActionCard等支持的消息卡片
# Target 可以是 Group, Member, OpenConversationId, Webhook, str(链接)
# 程序会自动判断方法进行发送
```

对于使用只发机器人 (`Webhook`) 的用户，可以使用以下方法发送消息

```python
await app.send_message(
    "https://oapi.dingtalk.com/robot/send?access_token=***",
    MessageChain("Webhook 消息")
)
```

**注意：仅支持基础消息(普通消息，Markdown, ActionCard, FeedCard)的发送**

## 发送文件

```python
await app.send_message(group, Image('example.png'))
```

~~**注意：请不要使用**
`MessageChain(Image(...))`
**的方法来发送文件，否则会发送文字消息**~~

`v2.0.9` 已经支持在 `MessageChain` 中塞入 `File` 实例，
同时支持发送的消息为列表对象。你现在可以这样

```python
await app.send_message(group, MessageChain(
    "Before File", Image(r"\root\sese.png"), "After File"
))
```

等同于

```python
await app.send_message(group, [
    MessageChain("Before File"), Image(r"\root\sese.png"), MessageChain("After File")
])
```

## 撤回消息
```python
res = await app.send_message(Target, mes)
# Target 必须是 OpenConversationId ，即只有通过API发送的文件才支持撤回
await app.recall_message(res)
```

若在同步函数中发送消息，可以使用 `app.sendMessage` 方法，参数与 `app.send_message` 一致

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
通过Stream模式转发钉钉服务器的消息到WebSocket和Webhook，支持本项目的连接。
> 配置方法在 `main_example.py` 中有写，请自行配置

# 最后要说

本项目基于[Graia](https://github.com/GraiaProject/Ariadne)QQ机器人框架模仿开发，
有兴趣的话去点个star吧

# 鸣谢

特别感谢 [JetBrains](https://www.jetbrains.com/?from=Dingraia) 为 Dingraia 提供免费的 [PyCharm](https://www.jetbrains.com/pycharm/?from=Dingraia) 等 IDE 的授权  
[<img src=".github/jetbrains-variant-3.png" width="200"/>](https://www.jetbrains.com/?from=Dingraia)

