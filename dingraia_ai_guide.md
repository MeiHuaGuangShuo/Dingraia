# Dingraia AI 开发指南

## 简介

Dingraia 是一个支持异步和 Stream 的钉钉机器人框架，适用于群聊机器人，提供简单的 API 来实现群组操作，支持多种回调处理。本指南将帮助您通过
AI 快速开发 Dingraia 模块。

**注意**: 为了实现更好的代码生成效果，仍然建议通过代码库索引生成代码（如Curosr, Trae等支持Agent模式的AI），而不是靠本文档

## 快速开始

### 在主程序导入模块

```python
from dingraia.saya import Saya

saya = Saya.current()
with saya.module_context():
  saya.require(f"Module")
```

### 基本结构

每个 Dingraia 模块都遵循以下基本结构：

```python
from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def your_function_name(app: Dingtalk, group: Group, message: MessageChain):
    # 您的代码在这里
    if str(message) == "触发词":
        await app.send_message(group, "回复内容")
```

### 常用导入

```python
from dingraia.lazy import *  # 导入所有必要的类和函数，为了避免冲突，不太建议这样导入
```

## 消息处理

### 接收消息

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def receive_message(app: Dingtalk, group: Group, message: MessageChain):
    # 获取纯文本消息内容
    message_text = str(message)

    # 检查消息是否包含特定内容
    if message_text.startswith("/command"):
        # 处理命令
        pass
```

### 发送不同类型的消息

#### 发送消息/文件

```python
await app.send_message(group, MessageChain("这是一条文本消息"))
```

`MessageChain` 为一份消息容器，可以包含At消息和文件对象和任意可以被__str__的对象，比如

```python
from dingraia.lazy import *

MessageChain(At(member), "请查收您的文件", File("http://localhost/files"))
```

`File` 有两个实例化参数:

- `def __init__(self, file: Union[Path, BinaryIO, bytes, str] = None, fileName: str = None):`

其中, `file` 可以是路径/打开的文件流(如open())，文件字节或者URL。
有时候可能需要指定文件名才能成功上传，此时可以使用 `fileName` 指定文件名

默认情况下使用 `app.send_message` 会自动上传文件，当然也可以使用
内置的方法上传 `app.upload_file` ，使用方法见下文，会返回带mediaId
的对象。所有上传的文件会**自动开启缓存**，对文件本体使用 `SHA-256` 哈希化后
储存在数据库/内存中，第二次上传文件则会**直接返回**包含对应的mediaId的对象。

#### Markdown 消息

```python
await app.send_message(group, Markdown("**这是一条加粗的消息**", title="标题"))
```

#### 图片消息

```python
await app.send_message(group, Image("https://example.com/image.jpg"))
```

#### 链接消息

```python
await app.send_message(group, Link(
    url="https://example.com",
    title="标题",
    text="描述文本",
    pic_url="https://example.com/image.jpg"
))
```

#### 卡片消息

```python
await app.send_message(group, ActionCard(
    text="# 卡片标题\n内容",
    button=[
        ActionCardButton(text="按钮1", url="https://example.com"),
        ActionCardButton(text="按钮2", url="https://example.com/page2")
    ]
))
```

### 撤回消息

```python
res = app.send_message(OpenConversationId, MessageChain("你好"))
app.recall_message(res)
```

注意：只能撤回通过API发送的消息（即通过 `OpenConversationId` 发送的消息，
通过默认接收通道获取的对象直接发送是以 WebHook 形式发送的，但是如果发送的是文件则
会自动转为API发送，此时可以被撤回）

## AI 功能集成

### 创建 AI 回复函数

```python
from dingraia.aiAPI import OpenAI, APIKeys
from dingraia.lazy import *

# 创建 AI 实例
api_keys = APIKeys(
  "key1",
  "key2"
)
ai = OpenAI("your_api_key", systemPrompt="你是一个有用的助手。", maxContextLength=2048)
# 或者使用 api_keys 达到负载均衡
aiWithAverage = OpenAI(api_keys, systemPrompt="你是一个有用的助手。", maxContextLength=2048)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ai_reply(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    message_text = str(message)

    if message_text.startswith("/ai "):
        # 提取问题
        question = message_text[4:]

        # 创建 AI 卡片
        ai_card = AICard()

        # 设置 AI 响应
        ai_card.set_response(ai.generateAnswerFunction(question, user=member))

        # 发送 AI 卡片
        await app.send_ai_card(
            target=group,
            cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema",
            card=ai_card,
            update_limit=100
        )
        # 或者使用以下命令按段发送，不使用 API 发送，但是缺乏部分功能（如代码显示），适用于仅聊天
        await app.send_ai_message(group, ai_card)
        # 亦或者又是自己处理AI返回的内容
        ai_text = await ai_card.completed_string()
        # 以下自行处理后选择喜欢的方式发送
```

### 处理 AI 助手消息

```python
@channel.use(ListenEvent=ListenerSchema(listening_events=[AiAssistantMessage]))
async def handle_ai_assistant(app: Dingtalk, event: AiAssistantMessage):
    # 处理来自 AI 助手的消息
    message_text = str(event.message)

    # 发送回复
    await app.assistant_send_ai_card(event, card=f"你好，你刚刚说了: {message_text}")
```

## 实用功能示例

### 创建时间返回函数

```python
from dingraia.lazy import *
import datetime


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def get_current_time(app: Dingtalk, group: Group, message: MessageChain):
    if str(message) == "/time":
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await app.send_message(group, f"当前时间是: {current_time}")
```

### 创建计算器函数

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def calculator(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    message_text = str(message)

    # 检查是否为计算表达式
    if not message_text.startswith('/') and message_text:
        # 只允许特定字符
        allow_chars = "0123456789+-*/"
        if all(c in allow_chars for c in message_text):
            try:
                result = eval(message_text, {"exec": None, "eval": None}, {})
                await app.send_message(group, f"计算结果: {result}")
            except Exception as err:
                await app.send_message(group, f"计算错误: {err}")
```

### 创建帮助菜单

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def show_help(app: Dingtalk, group: Group, message: MessageChain):
    if str(message) == "/help":
        help_text = """
# 机器人帮助
- `/time` - 显示当前时间
- `/ai [问题]` - 向 AI 提问
- `/image` - 发送图片
- `/link` - 发送链接
- 直接输入算式 (如 `1+1`) - 计算结果
        """
        await app.send_message(group, Markdown(help_text, title="帮助菜单"))
```

## 高级功能

### 等待用户回复

```python
from dingraia.waiter import Waiter
import asyncio


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def wait_for_reply(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    if str(message) == "/ask":
        await app.send_message(group, "请回答问题")

        try:
            # 等待同一用户在同一群组的回复，超时时间为30秒
            reply = await app.wait_message(Waiter(group, member), timeout=30)
            await app.send_message(group, f"你的回答是: {reply}")
        except asyncio.TimeoutError:
            await app.send_message(group, "回答超时")
```

## 示例：创建接收用户消息并返回当前时间的函数

```python
from dingraia.lazy import *
import datetime


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def get_current_time(app: Dingtalk, group: Group, message: MessageChain):
    if str(message) == "当前时间" or str(message) == "现在几点":
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await app.send_message(group, f"当前时间是: {current_time}")
```

## 完整模块示例

以下是一个完整的模块示例，包含多种功能：

```python
from dingraia.lazy import *
import datetime
import random


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def multi_function_bot(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    message_text = str(message)

    # 时间功能
    if message_text == "当前时间" or message_text == "/time":
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await app.send_message(group, f"当前时间是: {current_time}")

    # 随机数功能
    elif message_text.startswith("/random"):
        try:
            parts = message_text.split()
            if len(parts) == 3:
                min_val = int(parts[1])
                max_val = int(parts[2])
                result = random.randint(min_val, max_val)
                await app.send_message(group, f"随机数 ({min_val}-{max_val}): {result}")
            else:
                await app.send_message(group, "用法: /random 最小值 最大值")
        except ValueError:
            await app.send_message(group, "请输入有效的数字")

    # 问候功能
    elif message_text == "你好" or message_text == "hello":
        await app.send_message(group, MessageChain(f"你好，", At(member), "！"))
```

## 核心类 API 参考

### Dingtalk 类

主要的应用程序类，用于处理所有钉钉机器人相关操作。

#### 主要属性

- `config: Config` - 配置对象
- `access_token: str` - 当前企业的 AccessToken，会在调用时自动更新
- `running_mode: List[str]` - 当前运行模式
- `clientSession: ClientSession` - 保持打开的ClientSession对象，用于处理异步请求，请不要使用with clientSession，使用with
  clientSession.get()直接使用即可
- `api_request` 和 `oapi_request` -
  对api.dintalk.com和oapi.dingtalk.com的包装，以实现不需要手动携带凭证请求，支持get,post,put,delete，返回ClientResponse对象，或者使用j开头的jget,jpost,jput,jdelete直接获得json返回。当
  `Config`中配置了错误时抛出错误则会抛出隶属于`DingtalkAPIError`的错误
- `access_token` - 获取当前bot的 access_token。在配置多Stream时可能会被切换（此特性尚未配置开关）。

#### 主要方法

##### 消息与卡片相关

- `async def send_message(target, *msg, headers=None) -> Response`
  发送文本、Markdown、图片、文件等消息。

> `target`: 发送的对象，一般是 `Group`, `Member` 或者Webhook链接
>
> `*msg`: 消息，支持内置消息格式和任何可以被转换为str的对象，支持文件，可以这样传入
`"1", File(...), 2, MessageChain(At(...), "3")`
>
> `headers`: 自定义请求头，一般状况下自动配置

- `async def send_card(target, cardTemplateId, cardData, ...) -> CardResponse`
  发送自定义卡片消息。

> `target`: 发送的对象，一般是 `Group`, `Member` 或 `OpenConversationId`
>
> `cardTemplateId`: 卡片模板ID，钉钉提供的模板ID字符串
>
> `cardData`: 卡片数据，字典格式，包含卡片内容
>
> `privateData`: 卡片私有数据，可选，用于存储不展示给用户的数据
>
> `supportForward`: 是否支持转发，默认False

-
`async def send_markdown_card(target, markdown, logo="@lALPDfJ6V_FPDmvNAfTNAfQ", outTrackId=..., supportForward=False) -> CardResponse`
发送 Markdown 卡片消息。

> `target`: 发送的对象，一般是 `Group`, `Member` 或 `OpenConversationId`
>
> `markdown`: Markdown对象，包含text和title属性
>
> `logo`: 卡片logo，可以是mediaId字符串(以@开头)或File对象
>
> `outTrackId`: 卡片追踪ID，默认自动生成
>
> `supportForward`: 是否支持转发，默认False

- `async def update_card(outTrackId, cardParamData, privateData=None)`
  更新已发送的卡片内容。

> `outTrackId`: 卡片追踪ID，可以是字符串或CardResponse对象
>
> `cardParamData`: 新的卡片数据，可以是字典或Markdown对象
>
> `privateData`: 新的私有数据，可选

-
`async def send_ai_card(target, cardTemplateId, card, update_limit=0, key="content", maxAnswerLength=8192, ...) -> CardResponse`
发送 AI 卡片消息。

> `target`: 发送的对象，一般是 `Group`, `Member` 或 `OpenConversationId`
>
> `cardTemplateId`: AI卡片模板ID，钉钉提供的模板ID字符串
>
> `card`: AICard实例，包含AI回复内容
>
> `update_limit`: 更新频率限制，单位为字符数，0表示不限制。注意：此选项和API消耗量强相关，
> 如需节省用量可调高数值或使用 `send_ai_message` 方法，此方法会按段发送 Markdown 消息代替 AI 卡片，节省 API 用量
>
> `key`: 卡片内容字段名，默认为"content"
>
> `stopActionId`: 停止输出的回调ActionId，默认为"stop"
>
> `maxAnswerLength`: 最大回答长度，默认8192字符

- `async def assistant_send_ai_card(event, card, cardTemplateId=..., update_limit=..., key=..., maxAnswerLength=...)`
  用于 AI 助手事件的卡片回复。

> `event`: AiAssistantMessage事件对象，包含会话信息
>
> `card`: AICard实例或字符串，包含AI回复内容
>
> `cardTemplateId`: AI卡片模板ID，默认为"8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema"
>
> `update_limit`: 更新频率限制，单位为字符数，0表示不限制，默认为0
>
> `key`: 卡片内容字段名，默认为"content"
>
> `maxAnswerLength`: 最大回答长度，默认8192字符

- `async def send_ai_message(target, card, maxAnswerLength=...)`
  通过 Markdown 消息发送 AI 消息，按段发送。

> `target`: 发送的对象，一般是 `Group`, `Member` 或 `OpenConversationId`
>
> `card`: AICard实例，包含AI回复内容
>
> `maxAnswerLength`: 最大回答长度，默认8192字符

##### 文件与媒体

- `async def upload_file(file: Union[Path, str, File]) -> File`
  上传文件，返回带 mediaId 的 File 对象。

> `file`: 要上传的文件，可以是文件路径、URL或File对象
>
> 返回: 包含mediaId的File对象，可直接用于发送消息
>
> 支持的文件类型: 图片(jpg/gif/png/bmp)、音频(amr/mp3/wav)、视频(mp4)、文档(doc/docx/xls/xlsx/ppt/pptx/zip/pdf/rar)

- `async def download_file(downloadCode: Union[File, str], path: Union[Path, str]) -> bool`
  下载机器人接收的文件。

> `downloadCode`: 文件下载码，可以是File对象或字符串
>
> `path`: 文件保存路径，需要包含文件名
>
> 返回: 下载成功返回True，失败会抛出DownloadFileError异常

##### 群组与成员管理

- `async def kick_member(openConversationId, memberStaffIds)`
  踢出群成员。

> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `memberStaffIds`: 要踢出的成员，可以是Member对象、staffId字符串或它们的列表
>
> 注意: 群组必须是场景群，且机器人需要有管理权限

- `async def add_member(openConversationId, memberStaffIds)`
  添加成员到群组。

> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `memberStaffIds`: 要添加的成员，可以是Member对象、staffId字符串或它们的列表
>
> 注意: 群组必须是场景群，且机器人需要有管理权限

- `async def mute_member(openConversationId, memberStaffIds, muteTime=0)`
  禁言成员。

> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `memberStaffIds`: 要禁言的成员，可以是Member对象、staffId字符串或它们的列表
>
> `muteTime`: 禁言时长，单位为秒，值为0则解除禁言
>
> 注意: 群组必须是场景群，且机器人需要有管理权限

- `async def unmute_member(openConversationId, memberStaffIds)`
  解除禁言。

> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `memberStaffIds`: 要解除禁言的成员，可以是Member对象、staffId字符串或它们的列表
>
> 注意: 这是mute_member(muteTime=0)的便捷方法

- `async def set_admin(openConversationId, memberStaffIds, set_admin=True)`
  设置/取消成员为管理员。

> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `memberStaffIds`: 要设置的成员，可以是Member对象、staffId字符串或它们的列表
>
> `set_admin`: True设置为管理员，False取消管理员身份
>
> 注意: 群组必须是场景群，且机器人需要有群主权限

##### 事件与回调

- `async def wait_message(waiter: Waiter, timeout: float = None)`
  等待指定用户/群组的下一条消息，常用于"请用户回复"场景。

> `waiter`: Waiter对象，指定等待条件(群组、成员等)
>
> `timeout`: 等待超时时间，单位为秒，None表示永不超时
>
> 返回: 符合条件的MessageChain对象
>
> 超时: 抛出asyncio.TimeoutError异常

- `async def recall_message(message, openConversationId=None, processQueryKeys=None, robotCode=None, inThreadTime=0)`
  撤回已发送的消息。

> `message`: 要撤回的消息Response对象，通常是send_message的返回值
>
> `openConversationId`: 群对话ID，可以是OpenConversationId、Group对象或字符串
>
> `processQueryKeys`: 消息的加密ID，用于撤回消息
>
> `robotCode`: 机器人编码，默认使用配置中的robotCode
>
> `inThreadTime`: 延迟撤回时间(秒)，0表示立即撤回

##### 机器人信息与配置

- `async def get_info(target, force_to_update=False)`
  获取群组、成员、对话等信息。

> `target`: 要获取信息的对象，可以是Group、Member、OpenConversationId等
>
> `force_to_update`: 是否强制刷新信息，不使用缓存
>
> 返回: 目标对象的详细信息字典

- `async def get_card_data(outTrackId: str) -> Optional[dict]`
  获取卡片数据。

> `outTrackId`: 卡片追踪ID
>
> 返回: 卡片数据字典，不存在则返回None

- `async def get_login_url(redirect_url=None, state=..., exclusiveLogin=False) -> str`
  获取 OAuth 登录链接。

> `redirect_url`: 登录成功后的回调URL，默认使用HOST配置
>
> `state`: 状态标识，用于防止CSRF攻击，默认自动生成
>
> `exclusiveLogin`: 是否为专属帐号登录
>
> 返回: 登录URL字符串

- `async def get_user_access_token(oauthCode, forceRefresh=False)`
  获取用户 access token。

> `oauthCode`: OAuth授权码或AccessToken对象
>
> `forceRefresh`: 是否强制刷新token
>
> 返回: 用户AccessToken对象
>
> 注意: 如果传入的是AccessToken对象且forceRefresh=True，则会使用其refreshToken刷新

##### 其他实用方法

- `def run_coroutine(coro: Coroutine) -> Any`
  在同步环境下运行异步协程。

> `coro`: 要运行的异步协程
>
> 返回: 协程的执行结果
>
> 注意: 使用内置的事件循环运行，适用于在同步代码中调用异步方法

- `def create_task(coroutine: Coroutine, name: str = "Task", show_info=True, not_cancel_at_the_exit=False)`
  创建后台异步任务。

> `coroutine`: 要作为任务运行的异步协程
>
> `name`: 任务名称，用于日志显示
>
> `show_info`: 是否显示任务信息
>
> `not_cancel_at_the_exit`: 程序退出时是否不取消任务
>
> 返回: 创建的asyncio.Task对象

- `async def stop()`
  停止机器人运行。

> 停止所有任务、关闭连接并退出程序
>
> 通常用于程序内部控制退出

- `async def send_ding(targets: List[Union[Member, str]], content: Union[MessageChain, str], remindType: int = 1)`
  发送Ding消息提醒。

> `targets`: 接收者列表，可以是Member对象或staffId字符串
>
> `content`: 提醒内容，可以是MessageChain或字符串
>
> `remindType`: 提醒类型，1=应用内提醒，2=短信提醒，3=电话提醒
>
> 注意: 此功能需要钉钉专业版支持

- `async def update_object(obj: Union[Group, Member, OpenConversationId, Any])`
  从缓存中更新对象数据，自动填充缺失的属性。

> `obj`: 要更新的对象，可以是Group、Member或OpenConversationId
>
> 返回: 更新后的对象
>
> 注意: 此方法会自动从缓存中读取并填充对象的缺失属性，如name、id等，在send_message等方法中会自动调用。此方法依赖于Config中的useDatabase选项

### Group 类

表示一个钉钉群组。

#### 属性

- `id: int` - 群组 ID
- `name: str` - 群组名称
- `webhook: Webhook` - 群组的临时 Webhook 地址
- `openConversationId: OpenConversationId` - 对话 ID
- `member: Optional[Member]` - 可能存在的实际对象（在单聊内有效）

#### 方法

- `__int__` 输出id属性
- `__str__` 输出群组名称

### Member 类

表示一个钉钉成员。

#### 属性

- `id: int` - 成员 ID
- `name: str` - 成员名称
- `staffId: str` - 成员工号
- `group: Group` - 所属群组
- `admin: bool` - 是否为管理员
- `avatar: Optional[str]` - 头像 URL
- `mobile: Optional[str]` - 手机号
- `unionId: Optional[str]` - unionId
- `isAdmin: Optional[bool]` - 是否为管理员
- `isBoss: Optional[bool]` - 是否为老板

#### 方法

- `__int__` 输出id属性
- `__str__` 输出name属性

### Config 类

机器人启动参数

#### 属性

- `event_callback: CallBack = None` - 事件回调配置，用于处理钉钉回调事件。
- `bot: Bot = None` - 机器人身份信息配置。
- `stream: List[Stream] = None` - Stream 模式下的多应用配置列表。
- `customStreamConnect: CustomStreamConnect = None` - 自定义 Stream 连接方式，用于对接非官方 Stream 服务
- `autoBotConfig: bool = True` - 是否自动更改机器人配置。若stream非空且此参数为True，会自动用stream的AppKey和AppSecret填充bot
- `useDatabase: bool = True` - 是否启用数据库缓存。
- `dataCacheTime: DataCacheTime = None` - 数据缓存时间设置。
- `waitRadioMessageFinishedTimeout: int = 10` - 机器人停止时等待消息处理完成的超时时间（秒），防止消息处理中断
- `webRequestHandlers: List[Middleware] = None` - HTTP 请求中间件列表。
- `raise_for_api_error: bool = True` - 调用钉钉 API 失败时是否主动抛出异常
- `language: str = None` - 框架日志和提示的语言（支持zh_CN、en_US，默认跟随系统）

#### 方法

-
`def __init__(event_callback: CallBack = None, bot: Bot = None, stream: List[Stream] = None, *, customStreamConnect: CustomStreamConnect = None, autoBotConfig: bool = True, useDatabase: bool = True, dataCacheTime: DataCacheTime = None, waitRadioMessageFinishedTimeout: int = 10, webRequestHandlers: List[Middleware] = None, raise_for_api_error: bool = True, language: str = None)`

> 实例化

### DataCacheTime 类

详细设定数据库对应数据缓存时间

#### 属性

- `dataCacheTime` - 数据缓存时间设置
- `userInfoCacheTime` - 用户信息缓存时间，未设置时与 dataCacheTime 相同
- `groupInfoCacheTime` - 群组信息缓存时间，未设置时与 dataCacheTime 相同
- `userUnionIdConventCacheTime` - 用户 unionId 转换缓存时间，默认非常久

#### 方法

-
`def __init__(dataCacheTime: int = 3600, *, userInfoCacheTime: int = None, groupInfoCacheTime: int = None, userUnionIdConventCacheTime: int = 410281690)`

> 实例化

### CustomStreamConnect 类

自定义Stream连接

#### 属性

- `StreamUrl`: Websocket连接地址，必须以ws或wss开头
- `SignHandler`: 验证签名方法。如果为字符串则向网址POST数据，验证方法和钉钉官网方法一致；如果为函数则传入AppKey和AppSecret，必须返回包含
  `endpoint` 和 `ticket` 的字典
- `ExtraHeaders`: 进行Stream连接时附加的HTTP头部

#### 方法

-
`def __init__(StreamUrl: str = None, SignHandler: Union[Callable[[Union[str, AppKey], Union[str, AppSecret]], Union[Dict[Union[Union[str, EndPoint, Ticket]], str],Coroutine[Any, Any, Dict[Union[Union[str, EndPoint, Ticket]], str]]]], str] = None, ExtraHeaders: dict = None)`

> 实例化

### 使用示例

1. 发送消息到群组：

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def send_group_message(app: Dingtalk, group: Group, message: MessageChain):
    # 发送文本消息
    await app.send_message(group, "Hello World!")

    # 发送 Markdown 消息
    await app.send_message(group, Markdown("**Hello World!**", title="标题"))

    # 发送图片
    await app.send_message(group, Image("https://example.com/image.jpg"))
```

2. 处理文件：

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def handle_file(app: Dingtalk, group: Group, message: MessageChain):
    # 上传文件
    file = await app.upload_file("path/to/file.jpg")
    await app.send_message(group, file)

    # 下载文件
    if isinstance(message[0], File):
        await app.download_file(message[0], "path/to/save.jpg")
```

3. 群组管理：

```python
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def manage_group(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    if str(message) == "/mute":
        # 禁言成员 5 分钟
        await app.mute_member(group, member, 300)
    elif str(message) == "/unmute":
        # 解除禁言
        await app.unmute_member(group, member)
``` 