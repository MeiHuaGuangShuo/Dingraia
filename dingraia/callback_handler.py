from .event.event import *


def callback_handler(event_body: dict, raw_body=None):
    if raw_body is None:
        raw_body = {}
    if 'EventType' in event_body:
        if event_body['EventType'] == "ChatQuit":
            event = ChatQuit()
            event.time = event_body.get('Timestamp', event_body.get('timestamp'))
            event.chatId = event_body.get('ChatId', event_body.get('chatId'))
            event.operatorUnionId = event_body.get('OperatorUnionId', event_body.get('operatorUnionId'))
            event.operator = event_body.get('Operator', event_body.get('operator'))
            event.openConversationId = OpenConversationId(
                event_body.get('OpenConversationId', event_body.get('openConversationId')))
            event.cropId = event_body.get('CropId', event_body.get('cropId'))
            event.dec_mes = event_body
            event.raw_mes = raw_body
            return event
        elif event_body['EventType'] == 'chat_remove_member':
            event = ChatQuit()
            return event
        elif event_body['EventType'] == 'chat_update_title':
            event = GroupNameChange()
            event.time = event_body.get('Timestamp', event_body.get('timestamp'))
            event.chatId = event_body.get('ChatId', event_body.get('chatId'))
            event.operatorUnionId = event_body.get('OperatorUnionId', event_body.get('operatorUnionId'))
            event.operator = event_body.get('Operator', event_body.get('operator'))
            event.openConversationId = OpenConversationId(
                event_body.get('OpenConversationId', event_body.get('openConversationId')))
            event.title = event_body.get('Title', event_body.get('title'))
            event.dec_mes = event_body
            event.raw_mes = raw_body
            return event
    event = BasicEvent()
    event.dec_mes = event_body
    event.raw_mes = raw_body
    return event
