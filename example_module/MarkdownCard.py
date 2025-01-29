import dingraia.exceptions
from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def sendDifferentMessageType(app: Dingtalk, group: Group, message: MessageChain):
    if str(message) == "/md":
        try:
            cardResponse = await app.send_markdown_card(group,
                                                        Markdown("**这是一个markdown消息，初始状态，将于5s后更新**",
                                                                 "钉钉AI卡片"))
        except dingraia.exceptions.ApiPermissionDeniedError as e:
            await app.send_message(group, MessageChain("机器人没有权限发送MarkDown卡片，请查看报错信息并勾选对应权限"))
            logger.error(f"{e.__class__.__name__}: {e}")
        else:
            await asyncio.sleep(5)
            mark_down = cardResponse.card_data
            mark_down["markdown"] = "**这是一个markdown消息，已更新**"
            try:
                await app.update_card(cardResponse.outTrackId, mark_down)
            except dingraia.exceptions.ApiPermissionDeniedError as e:
                await app.send_message(group,
                                       MessageChain("机器人没有权限更新MarkDown卡片，请查看报错信息并勾选对应权限"))
                logger.error(f"{e.__class__.__name__}: {e}")
