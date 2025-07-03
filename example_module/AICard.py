import dingraia.exceptions
from dingraia.lazy import *
from dingraia.aiAPI.deepseek import DeepSeek, DeepSeek_R1
from dingraia.aiAPI.ollama import Ollama, DeepSeek_R1_32_B, DeepSeek_R1_8_B
from dingraia.aiAPI.siliconflow import SiliconFlow, DeepSeek_V2_5
from dingraia.aiAPI import APIKeys
from dingraia.waiter import Waiter

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


deepseek = DeepSeek("your_api_key", systemPrompt="你是一个有用的助手。", maxContextLength=1000)
ollama = Ollama(systemPrompt="你是一个有用的助手。", maxContextLength=1000)

# 此处为实现负载均衡的代码
api_keys = APIKeys(
    "your_api_key1",
    "your_api_key2"
)

siliconFlow = SiliconFlow(api_keys, systemPrompt="你是一个有用的助手。", maxContextLength=4096)

mainAI = siliconFlow
aiChatMode = False  # 设置为 True 开启全量AI聊天模式


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ai_reply(app: Dingtalk, member: Member, group: Group, message: MessageChain):
    s_mes = str(message)
    if s_mes.startswith("/ai"):
        if s_mes.startswith("/ai "):
            question = s_mes[4:]
        else:
            question = "<No input>"
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
        # 假设数据流为以下格式 / If the data flow is in the following format:
        # ```text
        # data: {"mes": "你好"}
        # ```
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
        try:
            await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema",
                                   card=ai_card,
                                   update_limit=100)
        except dingraia.exceptions.ApiPermissionDeniedError as e:
            await app.send_message(group, MessageChain("机器人没有权限发送AI卡片，请查看报错信息并勾选对应权限"))
            logger.error(f"{e.__class__.__name__}: {e}")
        # update_limit 用于控制信息流的更新频率，单位为字符，100则每100个字符更新一次卡片。
        # 一般情况下，钉钉会单独控制输出的卡片的打字机效果，所以每次更新100个也是够用且合适的。
        # The `update_limit` parameter controls the frequency of card updates,
        # the unit is characters, and 100 means to update the card every 100 characters.
        # In general, DingTalk will control the typing effect of the card separately,
        # so updating 100 characters every time is sufficient and appropriate.
    elif s_mes.startswith("/dsai "):
        question = s_mes[6:]
        ai_card = AICard()
        ai_card.set_response(deepseek.generateAnswerFunction(question, user=member))
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=40)
    elif s_mes.startswith("/dsrai "):
        question = s_mes[6:]
        ai_card = AICard()
        ai_card.set_response(deepseek.generateAnswerFunction(question, DeepSeek_R1, user=member))
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=40)
    elif s_mes.startswith("/oai "):
        question = s_mes[5:]
        ai_card = AICard()
        ai_card.set_response(ollama.generateAnswerFunction(question, DeepSeek_R1_32_B, user=member))
        # 4090推荐 32B，4060 8G推荐 8B
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=40)
    elif s_mes.startswith("/lai "):
        question = s_mes[5:]
        ai_card = AICard()
        ai_card.set_response(ollama.generateAnswerFunction(question, DeepSeek_R1_32_B, user=member))
        # 4090推荐 32B，4060 8G推荐 8B
        await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema", card=ai_card,
                               update_limit=40)
    elif s_mes == "/reset":
        mainAI.clearHistory()
        await app.send_message(group, MessageChain("重置对话成功"))


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def ai_chat(app: Dingtalk, member: Member, group: Group, message: MessageChain):
    if not aiChatMode:
        return
    if str(message) == '/reset':
        mainAI.clearHistory(member)
        await app.send_message(group, "历史已清除")
    elif str(message) == '/history':
        mes_sum = ""
        returnString = "\n"
        dReturnString = "\n\n"
        for mes in mainAI.messages(member):
            if mes.get("role") == "user":
                mes_sum += f"{mes.get('content').split('Message: ')[1].replace(returnString, dReturnString)}\n---\n\n"
            elif mes.get("role") == "assistant":
                mes_sum += f"> {mes.get('content').replace(returnString, dReturnString).replace(returnString, returnString + '> ')}\n---\n\n"
        await app.send_message(group, Markdown(f"# 对话历史\n\n{mes_sum}", title="[对话历史]"))
    elif str(message).startswith("/del"):
        if str(message) == '/del':
            mainAI.clearHistory(member)
            await app.send_message(group, "全部对话历史已清除")
            return
        elif str(message).startswith('/del '):
            count = str(message).split(' ', 1)[1]
            if count.isnumeric():
                count = int(count)
                if count > 0:
                    mainAI.deleteMessage(count, user=member)
                    await app.send_message(group, f"{count}条对话历史已清除")
                    return
            await app.send_message(group, "请输入有效的数字")
            return
        await app.send_message(group, "请输入有效的指令，用法：/del [数字]")
    elif str(message).startswith("/cp "):
        ats = message.include(At)
        if ats and len(ats):
            cpFrom = Member()
            cpFrom.staffId = ats[0].target
            await app.update_object(cpFrom)
            if not cpFrom.id or not cpFrom.name:
                await app.get_user(cpFrom)
                await app.update_object(cpFrom)
            if len(ats) == 1:
                await app.send_message(group, MessageChain(At(member), " 你现在要复制", At(cpFrom),
                                                           " 的对话历史，请等待Ta确认(60s)"))
                await app.send_message(group, Markdown("[同意](dtmd://dingtalkclient/sendMessage?content=/y)"
                                                       "  或  [拒绝](dtmd://dingtalkclient/sendMessage?content=/n)"))
                try:
                    res = await app.wait_message(Waiter(group, cpFrom), timeout=60)
                except asyncio.TimeoutError:
                    await app.send_message(group, "对方未确认，复制操作取消")
                    return
                if str(res) != "/y":
                    await app.send_message(group, "对方未确认，复制操作取消")
                    return
                raw = mainAI.messages(member)
                raw.clear()
                raw.extend(mainAI.messages(cpFrom))
                await app.send_message(group, MessageChain(At(member), "对话历史已复制"))
            elif len(ats) == 2:
                cpTo = Member()
                cpTo.staffId = ats[1].target
                await app.update_object(cpTo)
                if not cpTo.id or not cpTo.name:
                    await app.get_user(cpTo)
                    await app.update_object(cpTo)
                await app.send_message(group,
                                       MessageChain(At(member), " 你现在要把", At(cpFrom), "的对话历史复制给", At(cpTo),
                                                    "，请等待", At(cpTo), "确认(60s)"))
                await app.send_message(group, Markdown("[同意](dtmd://dingtalkclient/sendMessage?content=/y)"
                                                       "  或  [拒绝](dtmd://dingtalkclient/sendMessage?content=/n)"))
                try:
                    res = await app.wait_message(Waiter(group, cpTo), timeout=60)
                except asyncio.TimeoutError:
                    await app.send_message(group, "对方未确认，复制操作取消")
                    return
                if str(res) != "/y":
                    await app.send_message(group, "对方未确认，复制操作取消")
                    return
                raw = mainAI.messages(cpTo)
                raw.clear()
                raw.extend(mainAI.messages(cpFrom))
                await app.send_message(group, MessageChain(At(member), "对话历史已复制给", At(cpTo)))
            else:
                await app.send_message(group, "指令错误，请使用 /cp [用户] 或 /cp [用户1] [用户2]")
            return
    elif str(message) == "/regenerate":
        t = {}
        userMessages = mainAI.messages(member)
        while t.get("role") != "user":
            t = userMessages.pop(-1)
        content = t.get("content", "")
        question = content.split("Message: ")[1]
        ai_card = AICard()
        ai_card.set_response(mainAI.generateAnswerFunction(question, user=member, model="deepseek-ai/DeepSeek-V2.5"))
        if group.name == "Unknown":
            group.name = member.name
            group.id = member.id
        await app.send_ai_message(target=group, card=ai_card)
        await asyncio.sleep(0.5)
        await app.send_message(group, Markdown("[重新生成](dtmd://dingtalkclient/sendMessage?content=/regenerate)  或  "
                                               "[删除这个对话](dtmd://dingtalkclient/sendMessage?content=/del%201)  或  "
                                               "[清空所有历史](dtmd://dingtalkclient/sendMessage?content=/reset)  或  "
                                               "[查看对话历史](dtmd://dingtalkclient/sendMessage?content=/history)"
                                               ))
        return
    elif str(message).startswith('/set_last_message '):
        mes = str(message).split(' ', 1)[1]
        t = {}
        userMessages = mainAI.messages(member)
        while t.get("role") != "assistant":
            t = userMessages.pop(-1)
        t["content"] = mes
        mainAI.messages(member).append(t)
        await app.send_message(group, "已更新上一条消息")
        return
    elif str(message).startswith('/sys '):
        sysP = str(message).split(' ', 1)[1]
        mainAI.systemPrompt = sysP
        mainAI.clearHistory(member)
        await app.send_message(group, "历史已清除，已更新系统提示词")
    elif not str(message).startswith('/'):
        ai_card = AICard()
        question = str(message)
        ai_card.set_response(mainAI.generateAnswerFunction(question, user=member, model=DeepSeek_V2_5))
        if app.get_api_counts() >= 3000:
            await app.send_ai_message(target=group, card=ai_card)
            await asyncio.sleep(0.5)
            await app.send_message(group, Markdown("[重新生成](dtmd://dingtalkclient/sendMessage?content=/regenerate)  或  "
                                                   "[删除这个对话](dtmd://dingtalkclient/sendMessage?content=/del%201)  或  "
                                                   "[清空所有历史](dtmd://dingtalkclient/sendMessage?content=/reset)  或  "
                                                   "[查看对话历史](dtmd://dingtalkclient/sendMessage?content=/history)"
                                                   ))
        else:
            await app.send_ai_card(target=group, cardTemplateId="8f250f96-da0f-4c9f-8302-740fa0ced1f5.schema",
                                   card=ai_card,
                                   update_limit=100)
    elif str(message) == '/help':
        await app.send_message(group, Markdown(
            "# AI功能帮助\n\n"
            "[重新生成最后一次对话](dtmd://dingtalkclient/sendMessage?content=/regenerate)\n\n"
            "[删除最后一次对话](dtmd://dingtalkclient/sendMessage?content=/del%201)\n\n"
            "删除多个对话 /del [对话数量]\n\n"
            "[清空所有历史](dtmd://dingtalkclient/sendMessage?content=/reset)\n\n"
            "[查看对话历史](dtmd://dingtalkclient/sendMessage?content=/history)\n\n"
            "设置上一条AI消息 /set_last_message <消息内容>\n\n"
            "设置系统提示词 /sys <提示词>\n\n"
            "<>为必填项，[]为可选项\n\n"
        ))
