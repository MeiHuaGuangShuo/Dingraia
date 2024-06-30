from .event.event import *


def matcher(key: str, *__dict: dict):
    for __d in __dict:
        res = __d.get(key[0].lower() + key[1:], __d.get(key[0].upper() + key[1:]))
        if res:
            return res


def callback_handler(event_body: dict, raw_body=None, trace_id=None):
    if raw_body is None:
        raw_body = {}
    event = None
    if 'EventType' in event_body:
        if event_body['EventType'] == "ChatQuit":
            event = ChatQuit()
            event.time = matcher('Timestamp', event_body)
            event.chatId = matcher('ChatId', event_body)
            event.operatorUnionId = matcher('OperatorUnionId', event_body)
            event.operator = matcher('Operator', event_body)
            event.openConversationId = OpenConversationId(
                matcher('OpenConversationId', event_body))
            event.cropId = matcher('CropId', event_body)
            event.dec_mes = event_body
            event.raw_mes = raw_body
        elif event_body['EventType'] == 'chat_remove_member':
            event = ChatKick()
            event.time = matcher('Timestamp', event_body)
            event.chatId = matcher('ChatId', event_body)
            event.userIds = matcher('userId', event_body)
            event.operatorUnionId = matcher('OperatorUnionId', event_body)
            event.operator = matcher('Operator', event_body)
            event.openConversationId = OpenConversationId(
                matcher('OpenConversationId', event_body))
            event.cropId = matcher('CropId', event_body)
            event.dec_mes = event_body
            event.raw_mes = raw_body
        elif event_body['EventType'] == 'chat_update_title':
            event = GroupNameChange()
            event.time = matcher('Timestamp', event_body)
            event.chatId = matcher('ChatId', event_body)
            event.operatorUnionId = matcher('OperatorUnionId', event_body)
            event.operator = matcher('Operator', event_body)
            event.title = matcher('Title', event_body)
            event.openConversationId = OpenConversationId(
                matcher('OpenConversationId', event_body), event.title)
            event.cropId = matcher('CropId', event_body)
            event.dec_mes = event_body
            event.raw_mes = raw_body
    if not event:
        event = BasicEvent()
        event.dec_mes = event_body
        event.raw_mes = raw_body
        return event
    bsEvent = BasicEvent(raw_body, event_body)
    event.trace_id = bsEvent.trace_id = trace_id
    return [event, bsEvent]
