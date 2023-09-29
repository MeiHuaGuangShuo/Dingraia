from typing import List

from ..model import *


class BasicEvent:
    type = "BasicEvent"
    
    def __init__(self, raw_mes: str = "", dec_mes: str = ""):
        self.raw_mes = raw_mes
        self.dec_mes = dec_mes


class CheckUrl(BasicEvent):
    type = 'CheckUrl'


class CheckIn(BasicEvent):
    
    member: Member
    
    bot: Bot


class ChatQuit(BasicEvent):
    
    operator: int
    """对应Operator, 为成员的StaffID"""
    
    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""
    
    cropId: str
    """对应CorpId"""
    
    time: int
    """TimeStamp*1000"""
    
    chatId: str
    """对应ChatId"""
    
    operatorUnionId = str
    """对应操作的唯一ID"""


class ChatKick(BasicEvent):
    
    operator: int
    """对应Operator, 为成员的StaffID"""
    
    userIds: List[int]
    """对应userId, 为移除成员的StaffID"""
    
    openConversationId: OpenConversationId
    """对应OpenConversationId, 为对话ID"""
    
    cropId: str
    """对应CorpId"""
    
    time: int
    """TimeStamp*1000"""
    
    chatId: str
    """对应ChatId"""
    
    operatorUnionId = str
    """对应操作的唯一ID"""


class GroupNameChange(BasicEvent):
    
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
