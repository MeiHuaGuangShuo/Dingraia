from flask import request
from .DingTalk import Dingtalk
from .model import Group, Member, Bot
from .event import MessageEvent
from .message.chain import MessageChain
from .saya import Channel
from .event.message import GroupMessage
from loguru import logger
channel = Channel.current()
callbacks = []


@logger.catch
async def bcc():
    res = request.get_json()
    # logger.info(json.dumps(res, indent=2))
    _e = dispackage(res)
    if not _e:
        logger.warning("无法解包！")
        return
    log(_e)
    await channel.radio(GroupMessage, *_e, sync=True)


@logger.catch
def dispackage(data: dict) -> list:
    conversationtype = data.get("conversationType")
    if conversationtype is not None:
        bot = Bot(origin=data)
        group = Group(origin=data)
        member = Member(origin=data)
        if conversationtype == "2":
            at_users = [userid.get("dingtalkId") for userid in data.get("atUsers") if userid.get("dingtalkId")[userid.get("dingtalkId").rfind('$'):] != bot.origin_id]
        else:
            at_users = []
        if data.get('msgtype') != 'text':
            raise ValueError("不支持解析文本以外的消息")
        mes = data.get('text').get('content')
        for _ in mes:
            if mes.startswith(" "):
                mes = mes[1:]
            else:
                break
        # logger.info(at_users)
        message = MessageChain(mes, at=at_users)
        event = MessageEvent(data.get('msgtype'), data.get('msgId'), data.get('isInAtList'), message, group, member)
        return [group, member, message, event, bot]
    else:
        raise ValueError("不支持的对话类型")


def log(data):
    if data[0].name is None:
        data[0].name = "临时会话"
    Dingtalk.log.info(f"[RECV][{data[0].name}({int(data[0])})][{data[1].name}({int(data[1])})] -> {str(data[2])}")
    
    

