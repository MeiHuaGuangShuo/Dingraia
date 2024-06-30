import time
import json
import requests
from collections import OrderedDict
from .exceptions import DingtalkAPIError


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
    
    def __init__(self, accessToken: str = None, expireTime: int = 0, *, AppKey: str = None, AppSecret: str = None):
        if not accessToken and (not AppKey or not AppSecret):
            raise ValueError
        self.token = accessToken
        self.appKey = AppKey
        self.appSecret = AppSecret
        if self.token:
            self.expired = expireTime if expireTime > 1600000000 else int(time.time()) + expireTime
        # else:
        #     self.refresh(True)
    
    def refresh(self, force=False) -> "AccessToken":
        if not force:
            if self.ok:
                return self
        if not self.appKey or not self.appSecret:
            raise ValueError
        url = f"https://oapi.dingtalk.com/gettoken?appkey={self.appKey}&appsecret={self.appSecret}"
        res = requests.get(url)
        if not res.ok:
            raise DingtalkAPIError(res.text)
        res = res.json()
        self.token = res['access_token']
        self.expired = res['expires_in'] if res['expires_in'] > 1600000000 else int(time.time()) + res['expires_in']
        return self
    
    def safe(self):
        if self:
            return self.token
        return self.refresh().token
    
    def __str__(self):
        return self.token
    
    def __int__(self):
        return self.expired
    
    def __bool__(self):
        return time.time() < self.expired
    
    def __repr__(self):
        return f"<AccessToken token={self.token} is_valid={self.ok}>"
    
    @property
    def ok(self):
        return time.time() < self.expired


class TimeStamp:
    timestamp: int
    
    def __init__(self, timeStamp):
        self.timestamp = timeStamp


class Response:
    ok: bool = None
    
    url: str = ""
    
    text: str = ""
    
    sendData: dict = {}
    
    recallType: str = ""
    
    recallOpenConversationId: str = None
    
    def json(self) -> dict:
        return json.loads(self.text)
    
    def __bool__(self) -> bool:
        return True if self.ok else False
    
    def __repr__(self):
        return f"<Response [{self.ok}]>"


class FixedSizeDict(OrderedDict):
    def __init__(self, *args, max_size=50, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = max_size

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.max_size:
            self.popitem(last=False)

class UrlBuilder:
    """抽象builder"""
    
    def __init__(self, base_url: str = ""):
        self.url = base_url
    
    def __getattr__(self, u):
        self.url += "." + str(u)
        return self
    
    def __floordiv__(self, other):
        self.url += "://" + str(other)
        return self
    
    def __truediv__(self, other):
        self.url += "/" + str(other)
        return self
    
    def __str__(self) -> str:
        return self.url
    
    def __repr__(self):
        return self.url
