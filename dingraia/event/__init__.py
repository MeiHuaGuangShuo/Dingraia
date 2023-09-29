from ..message.chain import MessageChain
from ..model import Group, Member


class MessageEvent:
    
    def __init__(self, type: str, id: str, atd: bool, message: MessageChain, group: Group, member: Member):
        self.type = type
        self.id = id
        self.atd = atd
        self.message = message
        self.group = group
        self.member = member
