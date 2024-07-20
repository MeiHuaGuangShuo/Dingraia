import hashlib
from typing import Union
from ..element import OpenConversationId, TraceId


class Webhook:
    url: str

    expired_time: float

    def __init__(
            self,
            url: str = None,
            expired_time: int = None,
            _type: Union["Group", "Member"] = None,
            *,
            origin: dict = None
    ):
        if origin is not None:
            url = origin.get('sessionWebhook')
            expired_time = origin.get('sessionWebhookExpiredTime')
            _type = Member if origin.get('conversationType') == "1" else Group if origin.get(
                'conversationType') == "2" else None
        self.url = url
        self.expired_time = expired_time if 2600000000 > expired_time else expired_time / 1000
        self._type = _type

    def __str__(self) -> str:
        return self.url

    def __int__(self) -> int:
        return int(self.expired_time)

    def __float__(self) -> float:
        return self.expired_time


class Group:
    traceId: TraceId = None

    def __init__(
            self, id: str = None,
            name: str = None,
            send_url: str = None,
            conversationId: str = None,
            limit_time: int = 0,
            origin: dict = None
    ):
        self.webhook = None
        if origin is not None:
            id = origin.get('conversationId')
            name = origin.get("conversationTitle")
            send_url = origin.get('sessionWebhook')
            conversationId = origin.get('conversationId')
            limit_time = origin.get('sessionWebhookExpiredTime') or 0
            self.webhook = Webhook(origin=origin)
        self.origin_id = id[id.rfind("$"):]
        """原始加密"""
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        """计算所得ID，非真实群号"""
        self.name = name or "Unknown"
        """群聊的真实名称"""
        self.webhook = self.webhook or Webhook(send_url, limit_time)
        """群聊的临时Webhook地址，含有URL和过期时间戳"""
        self.openConversationId: OpenConversationId = OpenConversationId(conversationId, self.name, self.id)
        """对话ID"""

    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return self.name


class Member:
    traceId: TraceId = None

    def __init__(
            self,
            id: str = None,
            staffid: str = None,
            name: str = None,
            group: Group = None,
            admin: bool = None,
            origin: dict = None,
            staffId: str = None
    ):
        """成员的对象

        Args:
            id: 成员的唯一ID
            staffid: 成员在当前组织的工号，通常以数字和 '-'  号组成，也可以是其他字符
            staffId: 与staffid用法一致，任意一个填写均可
            name: 成员在组织内的名称
            group: 成员所属的组
            admin: 是否为 group 的管理员
            origin: 原始 JSON 数据，用于让此类自动匹配

        """
        if origin is not None:
            id = origin.get('senderId')
            name = origin.get("senderNick")
            staffid = origin.get("senderStaffId") or origin.get("StaffId")
            admin = origin.get("isAdmin")
        self.origin_id = id[id.rfind("$"):]
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.name = name
        self.staffid = staffid or staffId
        self.staffId = staffid or staffId
        self.group = group
        self.admin = admin

    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return self.name


class Bot:
    traceId: TraceId = None

    def __init__(self, id: str = None, corp_id: str = None, robot_code: str = None, origin: dict = None):
        if origin is not None:
            id = origin.get('chatbotUserId')
            corp_id = origin.get("chatbotCorpId") or origin.get('CropId')
            robot_code = origin.get("robotCode")
        self.origin_id = id[id.rfind("$"):]
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.corp_id = corp_id
        self.robot_code = robot_code

    def __int__(self) -> int:
        return self.id
