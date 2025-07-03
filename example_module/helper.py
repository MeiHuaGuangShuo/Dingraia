from dingraia.lazy import *

HELP_MARKDOWN = """\
# Dingraia
一个支持异步和Stream的钉钉机器人(Dingtalk Robot)框架，适应于群聊机器人，提供部分简单的API来实现群组操作，支持部分主要回调处理

## 正在处于测试模式

# 帮助

## 命令列表
 - `/help` 查看帮助
 - `1+1`, `2*3` 等简单计算表达式
 - `/md` 发送Markdown格式的消息
 - `/link` 发送链接
 - `/ac` 发送 ActionCard 消息
 - `/fd` 发送 FeedCard 消息
 - `/audio` 发送语音消息
 - `/image` 发送图片消息
 - `/ai [消息]` 发送测试 AI 卡片

"""


async def none_message(app: Dingtalk, traceId: TraceId, group: Group):
    if not app.is_send_message(traceId):
        await app.send_message(group, Markdown(HELP_MARKDOWN, title="[Dingraia Help]"))


@channel.use(ListenEvent=ListenerSchema(listening_events=[LoadComplete]))
def init(app: Dingtalk):
    app.message_handle_complete_callback.append(none_message)
