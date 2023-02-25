import inspect
import hashlib
from .membership import Group, Member


class MessageChain:
    
    def __init__(self, *text, at: list = None):
        self.mes = [s for s in list(text) if type(s) == str]
        self.display = ''.join(self.mes)
        if at is not None:
            self.at = [(int(hashlib.sha1(at_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000 for at_id in at]
        else:
            self.at = []
        
    def include(self, typ):
        if inspect.ismodule(typ):
            typ = typ.__name__
        if inspect.isfunction(typ):
            typ = typ.__name__
        if typ == "At":
            return self.at
        
    def get_first(self, typ):
        if inspect.ismodule(typ):
            typ = typ.__name__
        if inspect.isfunction(typ):
            typ = typ.__name__
        if typ == "At":
            if self.at:
                return self.at[0]
            else:
                return []
    
    def __str__(self):
        return self.display


class MessageEvent:
    
    def __init__(self, type: str, id: str, atd: bool, message: MessageChain, group: Group, member: Member):
        self.type = type
        self.id = id
        self.atd = atd
        self.message = message
        self.group = group
        self.member = member
        
        