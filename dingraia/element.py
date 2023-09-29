import time
import json


class OpenConversationId:
    """OpenConversationId类，用于标识对象"""
    
    openConversationId: str
    """OpenConversationId值"""
    
    name: str
    """用于标识群名称，可能为无"""
    
    group_id: int
    """用于标识群ID(框架内显示ID)，可能为无"""
    
    def __init__(self, openConversationId, name="未知会话", group_id=0):
        self.openConversationId = openConversationId
        self.name = name
        self.group_id = group_id
    
    def __str__(self):
        return self.openConversationId
    
    def __int__(self):
        return self.group_id


class AccessToken:
    token: str
    
    expired: int = 0
    
    def __init__(self, accessToken: str = None, expireTime: int = 0):
        self.token = accessToken
        self.expired = expireTime if expireTime > 1600000000 else int(time.time()) + expireTime
    
    def __str__(self):
        return self.token
    
    def __int__(self):
        return self.expired
    
    @property
    def ok(self):
        return time.time() < self.expired


class TimeStamp:
    timestamp: int
    
    def __init__(self, timeStamp):
        self.timestamp = timeStamp
        
        
class Response:
    
    ok: bool = None
    
    url: str
    
    text: str
    
    sendData: dict
    
    recallType: str
    
    recallOpenConversationId: str = None
    
    @property
    def json(self):
        return json.loads(self.text)
    
    def __bool__(self):
        if self.ok:
            return True
        return False
