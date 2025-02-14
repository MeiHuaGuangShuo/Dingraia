import time
import hashlib
from typing import Optional, Union
from ..element import OpenConversationId, TraceId
from ..cache import cache


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

    def __bool__(self):
        return time.time() < self.expired_time


class Group:
    traceId: TraceId = None

    def __init__(
            self,
            name: str = None,
            send_url: str = None,
            conversationId: str = None,
            limit_time: int = 0,
            origin: dict = None
    ):
        self.webhook = None
        if origin is not None:
            name = origin.get("conversationTitle")
            send_url = origin.get('sessionWebhook')
            conversationId = origin.get('conversationId')
            limit_time = origin.get('sessionWebhookExpiredTime') or 0
            self.webhook = Webhook(origin=origin)
        self.origin_id = conversationId if conversationId else ""
        """原始加密"""
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (
                    10 ** 10) + 1000 if self.origin_id else 0
        """计算所得ID，非真实群号"""
        self.name = name or "Unknown"
        """群聊的真实名称"""
        self.webhook = (self.webhook or Webhook(send_url, limit_time)) if send_url and limit_time else Webhook('', 0)
        """群聊的临时Webhook地址，含有URL和过期时间戳"""
        self.openConversationId: OpenConversationId = OpenConversationId(conversationId, self.name,
                                                                         self.id) if conversationId else OpenConversationId(
            '')
        """对话ID"""
        if origin is not None:
            self.update_cache()  # 为了防止特殊实例化数据覆盖缓存，只在有源请求才更新缓存

    def update_cache(self):
        if self.openConversationId is not None and self.id:
            if cache.value_exist("group_info", "openConversationId", str(self.openConversationId)):
                cache.execute("UPDATE group_info SET `id`=?,`chatId`=?,`name`=?,timeStamp=? WHERE "
                              "`openConversationId`=?",
                              (self.id, self.origin_id, self.name, time.time(), str(self.openConversationId)))
            else:
                cache.execute("INSERT INTO group_info (`id`,`chatId`,`openConversationId`,`name`,`info`,`timeStamp`) "
                              "VALUES (?,?,?,?,?,?)", (self.id, self.origin_id, str(self.openConversationId),
                                                       self.name, "{}", time.time()))
            if cache.value_exist("webhooks", "openConversationId", str(self.openConversationId)):
                cache.execute("UPDATE webhooks SET `url`=?,`expired`=?,timeStamp=? WHERE `openConversationId`=?",
                              (self.webhook.url, self.webhook.expired_time, time.time(), str(self.openConversationId)))
            else:
                cache.execute(
                    "INSERT INTO `webhooks` (id, openConversationId, url, expired, timeStamp) VALUES (?,?,?,?,?)",
                    (self.id, str(self.openConversationId), self.webhook.url, self.webhook.expired_time, time.time()))
            cache.commit()

    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return self.name


class Member:
    traceId: TraceId = None
    """追溯ID"""

    avatar: Optional[str] = None
    """头像"""

    mobile: Optional[str] = None
    """手机号"""

    stateCode: Optional[str] = None
    """国家码"""

    isHideMobile: Optional[bool] = None
    """是否隐藏手机号"""

    isRealAuthed: Optional[bool] = None
    """是否实名认证"""

    isSenior: Optional[bool] = None
    """是否为高管"""

    isBoss: Optional[bool] = None
    """是否为老板"""

    deptIdList: Optional[list] = None
    """部门ID列表"""

    unionId: Optional[str] = None
    """unionId"""

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
        self.origin_id = id[id.rfind("$"):] if id else ""
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (
                    10 ** 10) + 1000 if self.origin_id else 0
        self.name = name
        self.staffid = staffid or staffId
        self.staffId = staffid or staffId
        self.group = group
        self.admin = admin
        if origin is not None:
            self.update_cache(origin=origin)

    def calculate_id(self):
        if self.origin_id:
            self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (
                    10 ** 10) + 1000 if self.origin_id else 0
        else:
            self.id = 0

    def update_cache(self, origin: dict):
        if origin.get('conversationType') == '1':
            if cache.value_exist("user_info", "id", str(self.id)):
                cache.execute("UPDATE user_info SET `name`=?,`staffId`=?,timeStamp=? WHERE `id`=?",
                              (self.name, self.staffId, time.time(), str(self.id)))
            else:
                cache.execute("INSERT INTO user_info (`id`,`name`,`staffId`,`unionId`, `info`,`timeStamp`) "
                              "VALUES (?,?,?,?,?,?)", (str(self.id), self.name, self.staffId, '', '{}', time.time()))
            cache.commit()

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
        self.origin_id = id[id.rfind("$"):] if id else ""
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (
                    10 ** 10) + 1000 if self.origin_id else 0
        self.corp_id = corp_id
        self.robot_code = robot_code

    def __int__(self) -> int:
        return self.id
