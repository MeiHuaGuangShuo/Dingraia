此文档最后更新于25/5/22 `v2.1.0-Pre`

# 破坏性更改

在 `v2.0.9` 及以前的版本中，ActionCard的按钮属性名称为 `button` ，
在这之后的版本中将以 `buttons` 替代

在 `v2.1.0` 及以后的版本中 `dingraia.DingTalk.Dingtalk` 的 `get_user`
函数的第一个值由 `userStaffId` 变为 `user`

# 快速部署

[Stream连接快速部署](./quickDeployStream.md)

# 这是什么？

这个是一个在基础用例上模仿Graia-Ariadne模块
并运行的异步钉钉机器人代码，用来运行 **基础** 的Webhook类型
的微型机器人

新功能/建议/Bug 请提出 [Issue](https://github.com/MeiHuaGuangShuo/Dingraia/issues/new/choose)

# 特点

支持协程（使用ensure_future执行），支持阻塞函数的并发（使用线程池），函数捕捉报错等，支持At，支持Stream方法

支持 文字, Markdown FeedCard, ActionCard和文件的发送

支持应答机制 (HTTP, Stream, OutGoing未专门适配，理论支持)

## 功能一览

- 应答机制
    - HTTP 回调
    - Stream 回调
  - [AI 助理](#ai助理的配置)回复
- 使用方式
    - 脚本运行
        - 机器人阻塞模式
        - 单 API 模式 (需要额外配置)
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
      - 视频
  - 撤回消息 (钉钉限制：仅通过 API 发送的文件可撤回)
  - 发送互动卡片 (需自行构造 JSON 数据)
      - 预设 Markdown 卡片
  - 改变卡片内容 (需自行构造 JSON 数据)
  - 发送 AI 卡片，支持流式更新 (需[配置](#ai-卡片的配置))
      - 支持流式 Post 方法的 AI API
      - 对 `DeepSeek` API 的额外适配
      - 对 `Ollama` API 的额外适配 (已测试 DeepSeek-R1 本地模型)
    - 对 `SiliconFlow` API 的额外适配 (已测试 DeepSeek-V3)
    - 用户对话保存（使用数据库，自动保存，自动提取）
    - 用户对话隔离
    - 支持停止 AI 生成
  - 发送 AI 消息（低API用量），按段发送 (需[配置](#ai-卡片的配置))
  - 创建群组
  - 获取群消息
  - 获取部门消息
  - 获取用户详细信息
  - 删除用户 (组织)
  - 创建用户 (组织)
  - 更新用户信息 (组织)
  - 复制群组 **(未来可能移除)**
  - 更新群信息
      - 同源功能
          - 更新群标题
          - 转移群主权限
          - 全体禁言/解禁
  - 解散群组 (伪实现)
  - 踢出用户 (群组)
  - 添加用户 (群组)
  - 设置/取消管理员 (群组)
  - 禁言用户/解除禁言用户 (群组)
  - 设置机器人离线卡片 (Stream 模式独占)
  - 手动上传文件
  - 下载文件
- 特别功能
    - 同时运行 HTTP & Stream 模式
    - 运行周期内文件上传缓存
    - 插件支持
    - [即时重载 Debug 模式](#debug-模式)
    - **临时**切换全局默认 `AccessToken`
    - [用户/群组信息缓存](#关于缓存)
    - ~~即时载入/卸载模块~~ (存在 Bug，仅支持载入)

# 注意

本项目适用于一般聊天机器人开发，不建议用于生产环境

At可以传入Member实例（仅限企业内部机器人）与手机号，会自动识别

作者自身已经挂着该框架，保证框架确实可用 ~~如果懒癌发作不更新的另当别论~~

**自带文档可能更新不及时！（懒）**

**本项目基于企业内部机器人开发，使用企业内部机器人以获得更好的体验**

**普通Webhook机器人已经于2023年9月1日停用，目前不再支持（其他解决方法看下方 _发送消息_ 部分）**

**强烈推荐Stream模式**，安全，快速，随处可用

使用 **场景群** 获取最完整体验

钉钉默认的临时webhook地址有效期为**2小时**，如果存储后发送可能会导致
地址实现从而使用API发送，从而丢失At消息。

# 需求

拥有企业内部开发权限

你可以在启动机器人时 `Config` 传入空值，在企业内部机器人的情况下，自带临时地址，无需手动输入webhook地址（没有完整体验，只能收发）
> 仅 `HTTP` 模式下支持此特性

# 实现方法

通过使用 aiohttp异步服务端/Websockets 和装饰器进行函数调用的广播方法。

# 如何使用？

把导入的模块相应地替换成Dingraia中的模块即可。

查看 [Read the Docs文档](https://dingraia.readthedocs.io/zh-cn/latest/)
  - 涵盖 90% DingTalk.py

## 示例程序

在 `main_example.py` 中包含了一个和官方相似的示例，使用以下命令即可开启
```shell
python main_example.py -k <AppKey> -s <AppSecret>
```
发送任意算数即可进行计算，如 `1+1`
**（严禁部署在公共群聊，因为是使用eval进行运算的）**

发送 `/md` 即可发送一个 Markdown 卡片

若命令错误会自动发送提示卡片

### AI 卡片的配置

依次填入 `url`, `payload`, `headers`(可选)，
然后**自行编写 JSON 解析器**

> 程序已经自动处理流式输出的文本了。原流式传输的格式为
> ```text
> data: {"id": 114513, "type": "string", "text": "你"}
> 
> data: {"id": 114514, "type": "string", "text": "好"}
> 
> data: {"id": 114515, "type": "string", "text": "！"}
> ```
> 处理后则会直接返回 JSON 数据
> ```json
> {"id": 114513, "type": "string", "text": "你"}
> ```

例如，如果你的JSON数据是这样的

```json
{
    "id": 114513,
    "type": "string",
    "text": "你"
}
```

则你应该这么写

```python
def data_handler(data: dict) -> str:
    return data["text"]
```

然后一并传入 `withPostUrl` 中

### AI助理的配置

对于AI助理，其原理和上面AI卡片配置大体相同，但是使用了不同的API。
如果你需要流式更新的支持，你仍然需要配置一次AICard实例，
或者如果你有现成的字符串需要发送，也可以按照如下方式发送 (API消耗同AI卡片)

```python
from dingraia.lazy import *
from dingraia.aiAPI import OpenAI

currentAI = OpenAI("sk-1145141919810", systemPrompt="你很有用")


@channel.use(ListenEvent=ListenerSchema(listening_events=[AiAssistantMessage]))
async def init(app: Dingtalk, event: AiAssistantMessage):
    if str(event.message) == "/reset":
        currentAI.clearHistory(event.sender)
        await app.assistant_send_ai_card(event, card="重置成功")
        # card 参数填入字符串则直接发送字符串，预计消耗2API
        return
    ai_card = AICard()
    ai_card.set_response(
        currentAI.generateAnswerFunction(str(event.message), user=event.sender, model="deepseek-ai/DeepSeek-V3"))
    # 流式卡片配置和上面相同，但是使用的API不同，敬请注意
    await app.assistant_send_ai_card(event, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                                     update_limit=100)
```

关于可以获取的数据请查看 `dingraia.event.message.AiAssistantMessage`，当然也可以类似接受信息般使用，但是由于
回调数据可能为空并不建议这样做

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

## 单 API 模式

考虑到有时候需要特殊操作，所以开发了可以不阻塞仅使用 API 的方式

以下为示例代码

```python
from dingraia.lazy import *

app = Dingtalk()


async def main1():
    async with app.prepare:
        await app.get_user(...)


# 两种方法都行，app.stop 是要关闭ClientSession

async def main2():
    await app.prepare()
    await app.get_user(...)
    await app.stop()


asyncio.run(main1())
asyncio.run(main2())
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

# 关于缓存

**注意：非必要特别不建议禁用缓存，AI回复严重依赖缓存，禁用可能会导致AI功能报错**

程序默认在遇到以下情况时更新可以更新的缓存：

- 调用 `get_user`、`get_group` 的时候
- 遇到群组名称更新时
- 每次接收到信息时
- 上传文件时 (默认配置，无法禁用(相同的文件还浪费那API干啥))

对于以下行为会进行主动存储数据：

- AI对话
- API使用计数

如果需要设置禁用缓存或设置缓存时长，请在启动文件中添加额外参数

```python
from dingraia.lazy import *
from dingraia.config import Config, DataCacheTime

cache = DataCacheTime(
    dataCacheTime=86400,
    userInfoCacheTime=3600,
    groupInfoCacheTime=None,  # 将被设定为 86400
    userUnionIdConventCacheTime=410281690
)

app = Dingtalk(
    config=Config(
        useDatabase=False,  # 禁用内置数据库即禁用缓存
        dataCacheTime=cache  # 设置 get_user 等函数的允许使用缓存的时长
    )
)
app.get_user("<StaffId>", using_cache=True)
# using_cache 用于优先使用缓存，如果没有缓存仍然会从API获取用户信息
# 对于数据实时性要求高但不想全局禁用缓存的场景，请使用using_cache=False
```

当使用缓存时，`get_user`、`get_group` 将会在字典中添加 `dingraia_cache` 的键，
内容为部分缓存的值，一般包括 `id`,`staffId`,`openConversationId`,`name`,`timeStamp`之类

# 兼容度

似乎没有兼容度可言，已经变化成相似的独立框架了

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

