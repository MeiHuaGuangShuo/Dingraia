from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def sendDifferentMessageType(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    if str(message) == "/link":
        await app.send_message(group, Link(
            url="https://github.com/MeiHuaGuangShuo/Dingraia",
            title="GitHub - Dingraia",
            text="Dingraia 作为一款开源的异步Python钉钉框架，可以方便地快速创建一个自己的钉钉群聊应答机器人",
            pic_url="https://github.com/favicon.ico"
        ))
    elif str(message) == "/ac":
        await app.send_message(group, ActionCard(
            text="![GitHub icon](https://github.com/favicon.ico)\n# Dingraia ActionCard Test",
            button=[
                ["Dingraia", "https://github.com/MeiHuaGuangShuo/Dingraia"],
                ["MeiHuaGuangShuo", "https://github.com/MeiHuaGuangShuo"],
            ]
        ))
    elif str(message) == "/fd":
        await app.send_message(group, FeedCard(
            [
                [
                    "【手绘逐帧meme】一键三连变成女孩子有多可爱！❤️-哔哩哔哩",
                    "https://www.bilibili.com/video/BV1TK421Y78b",
                    "https://i1.hdslb.com/bfs/archive/00265597ac97f440b886b7a6a8eb3dd2b4537f09.jpg"
                ],
                [
                    "全部ホントで全部ウソ / Cover* ななひら-哔哩哔哩",
                    "https://www.bilibili.com/video/BV17m411r7PG",
                    "https://i1.hdslb.com/bfs/archive/2abb17f5797ebe00ad356cccd96c50182cbf595a.jpg"
                ],
            ]
        ))
    elif str(message) == "/audio":
        await app.send_message(group, Audio(
            "https://www.bilibili.com/audio/BV17K4y1p79T?p=1"
        ))
    elif str(message) == "/image":
        await app.send_message(group, Image(
            "https://i0.hdslb.com/bfs/album/d5d5d9d5d5.jpg"
        ))
