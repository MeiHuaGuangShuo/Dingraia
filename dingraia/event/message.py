from ..message import MessageChain
from ..membership import Member


class GroupMessage:
    
    type: str = "GroupMessage"
    
    message_chain: MessageChain
    
    sender: Member
