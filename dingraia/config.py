from typing import List, Union, Callable


class Bot:
    
    def __init__(self, AppKey: str, AppSecret: str, robotCode: str, GroupWebhookAccessToken: str = None,
                 GroupWebhookSecureKey: str = None):
        self.appKey = AppKey
        self.appSecret = AppSecret
        self.robotCode = robotCode
        self.GroupWebhookAccessToken = GroupWebhookAccessToken
        self.GroupWebhookSecureKey = GroupWebhookSecureKey


class CallBack:
    
    def __init__(self, AesKey: str, Token: str, AppKey: str):
        self.AesKey = AesKey
        self.Token = Token
        self.AppKey = AppKey
        self.elements = [self.AesKey, self.Token, self.AppKey]
    
    def __getitem__(self, item):
        return self.elements[item]
    
    def __setitem__(self, key, value):
        self.elements[key] = value


class Stream:
    
    def __init__(self, AppKey: str, AppSecret: str):
        self.AppKey = AppKey
        self.AppSecret = AppSecret


class CustomStreamConnect:
    
    def __init__(self, StreamUrl: str, SignHandler: Union[str, Callable] = None, ExtraHeaders: dict = None):
        if ExtraHeaders is None:
            self.ExtraHeaders = {}
        self.StreamUrl = StreamUrl
        self.SignHandler = SignHandler


class Config:
    
    def __init__(self,
                 event_callback: CallBack = None,
                 bot: Bot = None,
                 stream: List[Stream] = None,
                 *,
                 autoBotConfig: bool = True,
                 useDatabase: bool = True
                 ):
        """初始化Config
        
        Notes:
            在 `autoBotConfig` 启用且 `Stream` 启用时会自动替换 `Bot` 的值
        
        Args:
            event_callback:
            bot:
            stream:
            autoBotConfig: 是否自动替换Bot的值
        """
        self.useDatabase = useDatabase
        self.event_callback = event_callback
        self.bot: Union[Bot, None] = bot
        self.stream: Union[List[Stream], None] = stream
        if not isinstance(self.stream, list):
            self.stream = [self.stream]
        if len(self.stream) == 1 and autoBotConfig:
            self.bot = Bot(stream[0].AppKey, stream[0].AppSecret, stream[0].AppKey)
