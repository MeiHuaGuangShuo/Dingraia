import time
import json
import urllib.request
from collections import OrderedDict
from .exceptions import DingtalkAPIError
from typing import Optional


class OpenConversationId:
    """OpenConversationId类，用于标识对象"""

    openConversationId: str
    """OpenConversationId值"""

    name: str
    """用于标识群名称，可能为无"""

    group_id: int
    """用于标识群ID(框架内显示ID)，可能为无"""

    traceId: "TraceId" = None
    """用于标识请求的traceId"""

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
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise DingtalkAPIError(response.read().decode('utf-8'))
            res = json.loads(response.read().decode('utf-8'))
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


class TraceId:
    """TraceId上下文管理器"""

    traceId: str = None

    def __init__(self, traceId: str = None):
        self.traceId = traceId

    def __str__(self):
        return self.traceId

    def __enter__(self):
        return self.traceId

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Context:
    traceId: Optional[TraceId] = None

    def __init__(self):
        pass

    def __enter__(self, traceId: TraceId):
        self.traceId = traceId
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.traceId = None


class EasyDict(dict):
    """字典类，支持属性访问"""

    def __init__(self, __dict: dict, capitalize=True, no_raise=False):
        self.capitalize = capitalize
        self.no_raise = no_raise

        for k, v in __dict.items():
            if isinstance(v, dict):
                __dict[k] = EasyDict(v, capitalize=capitalize, no_raise=no_raise)

        super().__init__(__dict)

    def __getattr__(self, item, default=None):
        """
        获取属性值
        Args:
            item: 属性名

        Returns:
            Union[None, str, int, float, bool, list, dict]: 属性值

        """
        res = self.get(item, default)
        if item not in self.keys() and not self.capitalize and isinstance(item, str):
            if len(item) == 1:
                return res
            if item[0].isupper():
                item = item[0].lower() + item[1:]
            else:
                item = item[0].upper() + item[1:]
            return self.get(item)
        return res

    def __getitem__(self, item):
        if item not in self.keys() and not self.capitalize and isinstance(item, str):
            if len(item) == 1:
                if self.no_raise:
                    return None
                raise KeyError(item)
            if item[0].isupper():
                item = item[0].lower() + item[1:]
            else:
                item = item[0].upper() + item[1:]
            if item not in self.keys():
                if self.no_raise:
                    return None
                raise KeyError(item[0].lower() + item[1:] if item[0].isupper() else item[0].upper() + item[1:])
            return self.get(item)
        else:
            return self.get(item)

    def __contains__(self, item):
        if self.capitalize or not isinstance(item, str):
            return item in self.keys()
        if len(item) == 1:
            return item in self.keys()
        if item.isupper():
            item = item[0].lower() + item[1:]
        else:
            item = item[0].upper() + item[1:]
        return item in self.keys()

    def __setattr__(self, key, value):
        if key in ("capitalize", "no_raise"):
            super().__setattr__(key, value)
            return
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def to_dict(self):
        for k, v in self.items():
            if isinstance(v, EasyDict):
                super().__setitem__(k, v.to_dict())
        return dict(self)


class AppKey(str):
    pass


class AppSecret(str):
    pass


class EndPoint(str):
    pass


class Ticket(str):
    pass
