from dingraia.lazy import *
from dingraia.aiAPI import OpenAI

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

currentAI = None


# currentAI = OpenAI("sk-1145")


@channel.use(ListenEvent=ListenerSchema(listening_events=[AiAssistantMessage]))
async def init(app: Dingtalk, event: AiAssistantMessage):
    if isinstance(currentAI, OpenAI):
        if str(event.message) == "/reset":
            currentAI.clearHistory(event.sender)
            await app.assistant_send_ai_card(event, card="重置成功")
            return
        ai_card = AICard()
        ai_card.set_response(
            currentAI.generateAnswerFunction(str(event.message), user=event.sender, model="deepseek-ai/DeepSeek-V3"))
        await app.assistant_send_ai_card(event, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema",
                                         card=ai_card,
                                         update_limit=100)
    else:
        if str(event.message) == "流式输出":
            ai_card = AICard()
            ai_card.set_response(example_text.format(question=str(event.message)))
            await app.assistant_send_ai_card(event, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema",
                                             card=ai_card,
                                             update_limit=100)
        await app.assistant_send_ai_card(event, card=f"你好，你刚刚说了{event.message}")
