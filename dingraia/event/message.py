from ..message.chain import MessageChain
from ..model import *


class BasicMessage:
    type = "BasicMessage"
    
    message: MessageChain
    
    sender: Member


class GroupMessage(BasicMessage):
    type = "GroupMessage"
    
    message_chain: MessageChain
    
    sender: Member
    
    group: Group
    
    bot: Bot
