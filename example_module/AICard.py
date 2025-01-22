from dingraia.lazy import *
from dingraia.aiAPI.deepseek import DeepSeek, DeepSeek_R1

example_text = """\
你说的对，但是《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「提瓦特」的幻想世界，在这里，被神选中的人将被授予\
「神之眼」，导引元素之力。你将扮演一位名为「旅行者」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的同伴们，和他们一起击败强敌，\
找回失散的亲人——同时，逐步发掘「原神」的真相。

因为你的素养很差，我现在每天玩原神都能赚150原石，每个月差不多5000原石的收入， 也就是现实生活中每个月5000美元的收入水平，\
换算过来最少也30000人民币，虽然我只有14岁，但是已经超越了中国绝大多数人(包括你)的水平，这便是原神给我的骄傲的资本。\
毫不夸张地说，《原神》是miHoYo迄今为止规模最为宏大，也是最具野心的一部作品。即便在经历了8700个小时的艰苦战斗后，游戏还有许多尚未发现的秘密，\
错过的武器与装备，以及从未使用过的法术和技能。尽管游戏中的战斗体验和我们之前在烧机系列游戏所见到的没有多大差别，\
但游戏中各类精心设计的敌人以及Boss战已然将战斗抬高到了一个全新的水平。就和几年前的《塞尔达传说》一样，\
《原神》也是一款能够推动同类游戏向前发展的优秀作品。

你的问题是 {question}

You are right, but the game of "Genshin Impact" is a new open world adventure game developed by miHoYo. \
The game takes place in a fictional world called "Tavant", where the chosen ones are granted the power of\
 "the Eye of the Gods", guiding elemental power. You will play the role of a mysterious "Traveler", \
 meeting people with different personalities and abilities along the way, and defeating the powerful enemies.
 

Because your talent is poor, I can earn 150 gems every day playing Genshin Impact, and I get around 5000 gems a month, \
which is roughly the level of income in real life, \
not to mention that Genshin Impact is the largest and most ambitious game in recent years. \
Despite the 8700 hours of hard battles, there are still many secrets in the game that have not been discovered yet, \
the weapons and equipment you have missed, and the spells and skills you have never used. \
Although the combat experience in the game is similar to what we have seen in the previous generation of games, \
the game's enemies and Boss fights have pushed the combat to a new level. Just like the previous generation of games, \
Genshin Impact is a promising game that is driving other similar games forward.

Your question is {question}
"""

# DeepSeek 示例 / DeepSeek example
deepseek = DeepSeek("your_api_key", systemPrompt="你是一个有用的助手。", maxContextLength=1000)


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ai_reply(app: Dingtalk, group: Group, message: MessageChain):
    s_mes = str(message)
    if s_mes.startswith("/ai "):
        question = s_mes[4:]
        ai_card = AICard()
        # 你的AI API地址。只支持 POST 方式
        # Your AI API url. Only support POST method
        url = ""
        # 要 POST 的 JSON 数据
        # The JSON data to be POSTed
        payload = {

        }
        # 自定义请求头
        # Custom request headers
        headers = {

        }

        # 配置信息流解析方式，输入为每个信息流的 JSON 数据，返回值为信息流的文本内容
        # Configure the parsing method of the information flow,
        # the input is the JSON data of each information flow,
        # and the output is the text content of the information flow.
        # 假设数据流为一下格式 / If the data flow is in the following format:
        # data: {"mes": "你好"}
        # 则可以这样配置 / Then you can configure it like this:
        # data_handler = lambda data: data["mes"]
        # 你不需要考虑返回的数据是全量还是追加，程序会自动判断。仅在程序判断失误时才应该指定 AICard.content_type
        # AICard.content_type 的值应该为 "auto", "full" 或 "stream"，否则会抛出 ValueError异常。
        # You do not need to consider whether the returned data is complete or incremental,
        # the program will automatically determine it.
        # You should specify AICard.content_type only when the program makes a mistake.
        # The value of AICard.content_type should be "auto", "full" or "stream",
        # otherwise a ValueError exception will be thrown.
        # 设置方式(在本例) / Set up (in this example):
        # ai_card.content_type = "full"
        def data_handler(data: dict) -> str:
            return "Configure by your self."

        if url:
            ai_card.withPostUrl(url, json=payload, data_handler=data_handler, headers=headers)
        else:
            response = list(example_text.format(question=question))
            ai_card.set_response(response)
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=100)
        # update_limit 用于控制信息流的更新频率，单位为字符，100则每100个字符更新一次卡片。
        # 一般情况下，钉钉会单独控制输出的卡片的打字机效果，所以每次更新100个也是够用且合适的。
        # The `update_limit` parameter controls the frequency of card updates,
        # the unit is characters, and 100 means to update the card every 100 characters.
        # In general, DingTalk will control the typing effect of the card separately,
        # so updating 100 characters every time is sufficient and appropriate.
    elif s_mes.startswith("/dsai "):
        question = s_mes[6:]
        ai_card = AICard()
        ai_card.set_response(deepseek.generateAnswerFunction(question))
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=10)
    elif s_mes.startswith("/dsrai "):
        question = s_mes[6:]
        ai_card = AICard()
        ai_card.set_response(deepseek.generateAnswerFunction(question, DeepSeek_R1))
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=10)
