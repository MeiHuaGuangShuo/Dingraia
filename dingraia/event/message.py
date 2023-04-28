from ..message.chain import MessageChain
from ..model import Member


class GroupMessage:
    
    type: str = "GroupMessage"
    
    message_chain: MessageChain
    
    sender: Member
