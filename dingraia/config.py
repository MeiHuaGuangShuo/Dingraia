from typing import List


class Bot:
    
    def __init__(self, AppKey: str, AppSecret: str, robotCode: str, GroupWebhookAccessToken: str = None,
                 GroupWebhookSecureKey: str = None):
        self.appKey = AppKey
        self.appSecret = AppSecret
        self.robotCode = robotCode
        self.GroupWebhookAccessToken = GroupWebhookAccessToken
        self.GroupWebhookSecureKey = GroupWebhookSecureKey


class CallBack:
    
    def __init__(self, AesKey: str, Token: str, CropId: str):
        self.AesKey = AesKey
        self.Token = Token
        self.CropId = CropId
        self.elements = [self.AesKey, self.Token, self.CropId]
    
    def __getitem__(self, item):
        return self.elements[item]
    
    def __setitem__(self, key, value):
        self.elements[key] = value


class Stream:
    
    def __init__(self, AppKey: str, AppSecret: str):
        self.AppKey = AppKey
        self.AppSecret = AppSecret


class Config:
    
    def __init__(self,
                 event_callback: CallBack = None,
                 bot: Bot = None,
                 stream: List[Stream] = None
                 ):
        self.event_callback = event_callback
        self.bot = bot
        self.stream = stream
        if not isinstance(self.stream, list):
            self.stream = [self.stream]
