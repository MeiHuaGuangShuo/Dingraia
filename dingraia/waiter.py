from .message.chain import MessageChain
from .model import Group, Member


class Waiter:

    def __init__(self, group: Group, member: Member):
        self.group = group
        self.member = member

    async def detected_event(self, group: Group, member: Member, message: MessageChain):
        if self.group.id == group.id and self.member.id == member.id:
            return message
        return None
