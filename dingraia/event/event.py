from typing import List

from ..model import *


class BasicEvent:
    type = "BasicEvent"
    trace_id: str = None
    
    def __init__(self, raw_mes: str = "", dec_mes: Union[str, dict] = ""):
        self.raw_mes = raw_mes
        self.dec_mes = dec_mes


class LoadComplete(BasicEvent):
    """框架加载完成事件"""


class GettingMessageError(BasicEvent):
    error: str
    errorCode: int


class RadioComplete(BasicEvent):
    trace_id: str = None


class NoMessageSend(BasicEvent):
    trace_id: str = None


class MessageSend(BasicEvent):
    trace_id: str = None


class CheckUrl(BasicEvent):
    type = 'CheckUrl'


class CheckIn(BasicEvent):
    
    member: Member
    
    bot: Bot


class ChatQuit(BasicEvent):
    """群成员退群事件"""
    
    operator: int
    """对应Operator, 为成员的StaffID"""
    
    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""

    corpId: str
    """对应CorpId"""
    
    time: int
    """TimeStamp*1000"""
    
    chatId: str
    """对应ChatId"""
    
    operatorUnionId = str
    """对应操作的唯一ID"""


class ChatKick(BasicEvent):
    """群成员被踢事件"""
    
    operator: int
    """对应Operator, 为成员的StaffID"""
    
    userIds: List[int]
    """对应userId, 为移除成员的StaffID"""
    
    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""

    corpId: str
    """对应CorpId"""
    
    time: int
    """TimeStamp*1000"""
    
    chatId: str
    """对应ChatId"""
    
    operatorUnionId = str
    """对应操作的唯一ID"""


class GroupNameChange(BasicEvent):
    """群名称变更事件"""
    
    operator: int
    """对应Operator, 为成员的StaffID"""
    
    operatorUnionId: str
    """对应operatorUnionId，为成员的UnionID"""
    
    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""
    
    title: str
    """对应title，为更改后的群标题"""
    
    time: int
    """TimeStamp*1000"""
    
    chatId: str
    """对应ChatId"""

    corpId: str
    """对应CorpId"""


class GroupDisband(BasicEvent):
    """群解散事件"""

    operator: int
    """对应Operator, 为成员的StaffID"""

    operatorUnionId: str
    """对应operatorUnionId，为成员的UnionID"""

    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""

    title: str
    """对应title，为更改后的群标题"""

    time: int
    """TimeStamp*1000"""

    chatId: str
    """对应ChatId"""

    corpId: str
    """对应CorpId"""


class CalendarEventChange(BasicEvent):
    """[不确定的命名]日程事件变更事件"""

    eventId: str
    """对应eventId，为日程事件的唯一标识"""

    calendarEventUpdateTime: int
    """对应calendarEventUpdateTime，为日程事件的更新时间，单位为毫秒"""

    calendarEventId: str
    """对应calendarEventId，为日程事件的唯一标识，包含下划线和精确到秒的时间戳"""

    calendarId: str
    """对应calendarId，为日程ID，可能为primary"""

    unionIdList: List[str]
    """对应unionIdList，为此次事件涉及的成员的UnionID列表"""

    changeType: str
    """对应changeType，为日程事件的变更类型，可能为created"""

    legacyCalendarEventId: str
    """对应legacyCalendarEventId，为日程事件的唯一标识（旧版），纯英文和数字组成"""

    operator: dict
    """对应operator，为操作者的权限组信息（不包含个人信息）"""

    EventType: str = "calendar_event_change"
    """对应EventType，为事件类型"""

    corpId: str
    """对应corpId，为企业ID"""


class CircleUserAction(BasicEvent):
    """[不确定的命名]圈子成员操作事件"""
    EventType: str = "circle_user_action"

    allUserOnline: bool
    """对应allUserOnline"""

    eventId: str
    """对应eventId，为事件ID"""

    circleCorpId: str
    """对应circleCorpId，为圈子的企业ID"""

    optName: str
    """对应optName，为操作的名称"""

    circleUserId: str
    """对应circleUserid，为操作的成员在圈子内的用户ID"""

    belongCorpId: str
    """对应belongCorpId，为操作所属企业ID"""

    optTime: int
    """对应optTime，为操作的时间戳"""

    circleOrgName: str
    """对应circleOrgName，为圈子的名称"""
