from ..message.chain import MessageChain
from ..model import *


class BasicMessage:
    type = "BasicMessage"
    
    message: MessageChain
    
    sender: Member


class GroupMessage(BasicMessage):
    type = "GroupMessage"
    
    sender: Member
    
    group: Group
    
    bot: Bot


class AiAssistantMessage(BasicMessage):
    type = "AiAssistantMessage"

    sender: Member

    msgType: str

    group: Group

    webhook: Webhook

    openConversationId: OpenConversationId

    corpId: str

    conversationToken: str

    data: dict

    def __getattr__(self, item):
        if item in self.data:
            return self.data.get(item)
        return None
