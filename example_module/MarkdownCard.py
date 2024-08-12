from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def sendDifferentMessageType(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    if str(message) == "/md":
        cardResponse = await app.send_markdown_card(group,
                                                    Markdown("**这是一个markdown消息，初始状态，将于5s后更新**",
                                                             "钉钉AI卡片"))
        await asyncio.sleep(5)
        mark_down = cardResponse.card_data
        mark_down["markdown"] = "**这是一个markdown消息，已更新**"
        await app.update_card(cardResponse.outTrackId, mark_down)
