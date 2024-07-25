from typing import Awaitable, Dict, List, Union, Callable, Coroutine, Any
from aiohttp.web import Request
from aiohttp.web_response import StreamResponse
from .element import AppKey, AppSecret, EndPoint, Ticket


class Bot:

    def __init__(
            self, AppKey: str, AppSecret: str, robotCode: str, GroupWebhookAccessToken: str = None,
            GroupWebhookSecureKey: str = None
    ):
        self.appKey = AppKey
        self.appSecret = AppSecret
        self.robotCode = robotCode
        self.GroupWebhookAccessToken = GroupWebhookAccessToken
        self.GroupWebhookSecureKey = GroupWebhookSecureKey


class CallBack:

    def __init__(self, AesKey: str, Token: str, appKey: Union[AppKey, str]):
        self.AesKey = AesKey
        self.Token = Token
        self.AppKey = appKey
        self.elements = [self.AesKey, self.Token, self.AppKey]

    def __getitem__(self, item):
        return self.elements[item]

    def __setitem__(self, key, value):
        self.elements[key] = value


class Stream:

    def __init__(self, appKey: Union[AppKey, str], appSecret: Union[AppSecret, str]):
        self.AppKey = appKey
        self.AppSecret = appSecret


class CustomStreamConnect:

    def __init__(
            self,
            StreamUrl: str,
            SignHandler: Union[
                str,
                Callable[
                    [Union[AppKey, str], Union[AppSecret, str]],
                    Union[
                        Dict[Union[EndPoint, str], Union[Ticket, str]],
                        Coroutine[Any, Any, Dict[Union[EndPoint, str], Union[Ticket, str]]]
                    ]
                ]
            ] = None,
            ExtraHeaders: dict = None
    ):
        if ExtraHeaders is None:
            self.ExtraHeaders = {}
        self.StreamUrl = StreamUrl
        self.SignHandler = SignHandler


Handler = Callable[[Request], Awaitable[StreamResponse]]
Middleware = Callable[[Request, Handler], Awaitable[StreamResponse]]


class Config:

    def __init__(
            self,
            event_callback: CallBack = None,
            bot: Bot = None,
            stream: List[Stream] = None,
            *,
            customStreamConnect: CustomStreamConnect = None,
            autoBotConfig: bool = True,
            useDatabase: bool = True,
            webRequestHandlers: List[Middleware] = None,
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
        self.customStreamConnect = customStreamConnect
        self.bot: Union[Bot, None] = bot
        self.stream: Union[List[Stream], None] = stream
        self.webRequestHandlers = webRequestHandlers or []
        if not isinstance(self.stream, list):
            self.stream = [self.stream]
        if len(self.stream) == 1 and autoBotConfig:
            self.bot = Bot(stream[0].AppKey, stream[0].AppSecret, stream[0].AppKey)
