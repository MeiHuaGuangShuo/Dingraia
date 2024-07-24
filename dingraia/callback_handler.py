from .event.event import *
from .element import EasyDict


def matcher(key: str, *__dict: dict):
    for __d in __dict:
        res = __d.get(key[0].lower() + key[1:], __d.get(key[0].upper() + key[1:]))
        if res:
            return res


def callback_handler(event_body: dict, raw_body=None, trace_id=None):
    if raw_body is None:
        raw_body = {}
    event = None
    event_body = EasyDict(event_body, no_raise=True)
    if 'EventType' in event_body:
        if event_body.EventType in ['ChatQuit', 'chat_remove_member', 'chat_update_title']:
            if event_body.EventType == "ChatQuit":
                event = ChatQuit()
            elif event_body.EventType == 'chat_remove_member':
                event = ChatKick()
            elif event_body.EventType == 'chat_update_title':
                event = GroupNameChange()
            event.time = event_body.Timestamp
            event.chatId = event_body.ChatId
            event.operatorUnionId = event_body.OperatorUnionId
            event.operator = event_body.Operator
            event.title = event_body.Title
            event.openConversationId = OpenConversationId(event_body.OpenConversationId)
            event.cropId = event_body.CropId
            event.dec_mes = dict(event_body)
            event.raw_mes = raw_body
    if not event:
        event = BasicEvent()
        event.dec_mes = dict(event_body)
        event.raw_mes = raw_body
        return event
    bsEvent = BasicEvent(raw_body, dict(event_body))
    event.trace_id = bsEvent.trace_id = trace_id
    return [event, bsEvent]
