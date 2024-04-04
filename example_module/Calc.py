from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def sendDifferentMessageType(app: Dingtalk, group: Group, member: Member, message: MessageChain):
    if not str(message).startswith('/') and str(message):
        message = str(message)
        allow_chars = "0123456789+-*/"
        for c in message:
            if c not in allow_chars:
                await app.send_message(group, MessageChain(f"Q: {message}\nA: None\n", At(member)))
                return
        try:
            ans = eval(message, {"exec": None, "eval": None}, {})
        except Exception as err:
            ans = f"{err.__class__.__name__}: {err}"
        await app.send_message(group, MessageChain(f"Q: {message}\nA: {ans}\n", At(member)))
