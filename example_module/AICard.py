from dingraia.lazy import *

example_text = """\
你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「提瓦特」的幻想世界，在这里，被神选中的人将被授予
「神之眼」，导引元素之力。你将扮演一位名为「旅行者」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的同伴们，和他们一起击败强敌，
找回失散的亲人——同时，逐步发掘「原神」的真相。

因为你的素养很差，我现在每天玩原神都能赚150原石，每个月差不多5000原石的收入， 也就是现实生活中每个月5000美元的收入水平，
换算过来最少也30000人民币，虽然我只有14岁，但是已经超越了中国绝大多数人(包括你)的水平，这便是原神给我的骄傲的资本。
毫不夸张地说，《原神》是miHoYo迄今为止规模最为宏大，也是最具野心的一部作品。即便在经历了8700个小时的艰苦战斗后，游戏还有许多尚未发现的秘密，
错过的武器与装备，以及从未使用过的法术和技能。尽管游戏中的战斗体验和我们之前在烧机系列游戏所见到的没有多大差别，
但游戏中各类精心设计的敌人以及Boss战已然将战斗抬高到了一个全新的水平。就和几年前的《塞尔达传说》一样，
《原神》也是一款能够推动同类游戏向前发展的优秀作品。
"""


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ai_reply(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    s_mes = str(message)
    if s_mes.startswith("/ai "):
        question = s_mes[4:]
        ai_card = AICard()
        # 你的AI API地址。只支持 POST 方式
        url = ""
        # 要 POST 的 JSON 数据
        payload = {

        }
        # 自定义请求头
        headers = {

        }

        # 配置信息流解析方式，输入为每个信息流的 JSON 数据，返回值为信息流的文本内容
        def data_handler(data: dict) -> str:
            return "Configure by your self."

        if url:
            ai_card.withPostUrl(url, json=payload, data_handler=data_handler, headers=headers)
        else:
            response = list(example_text)
            ai_card.set_response(response)
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=100)
