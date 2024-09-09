from typing import Awaitable, Dict, List, Union, Callable, Coroutine, Any, Optional
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
                    [Union[str, AppKey], Union[str, AppSecret]],
                    Union[
                        Dict[Union[Union[str, EndPoint, Ticket]], str],
                        Coroutine[Any, Any, Dict[Union[Union[str, EndPoint, Ticket]], str]]
                    ]
                ]
            ] = None,
            ExtraHeaders: dict = None
    ):
        """自定义Stream连接配置

        Args:
            StreamUrl: Websocket连接地址，必须以ws或wss开头
            SignHandler: 验证签名方法。如果为字符串则向网址POST数据，验证方法和钉钉官网一致；如果为函数则传入AppKey和AppSecret，必须返回包含 `endpoint` 和 `ticket` 的字典
            ExtraHeaders: 进行Stream连接时附加的HTTP头部
        """
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
            dataCacheTime: float = 3600,
            webRequestHandlers: List[Middleware] = None,
            raise_for_api_error: bool = True,
    ):
        """初始化Config
        
        Notes:
            在 `autoBotConfig` 启用且 `Stream` 启用时会自动替换 `Bot` 的值
        
        Args:
            event_callback:
            bot:
            stream:
            autoBotConfig: 是否自动替换Bot的值
            raise_for_api_error: 是否在请求API失败时主动抛出异常
        """
        self.raise_for_api_error = raise_for_api_error
        self.useDatabase = useDatabase
        self.dataCacheTime = dataCacheTime
        self.event_callback = event_callback
        self.customStreamConnect = customStreamConnect
        self.bot: Optional[Bot] = bot
        self.stream: Optional[List[Stream]] = stream
        self.webRequestHandlers = webRequestHandlers or []
        if not isinstance(self.stream, list):
            if self.stream is not None:
                self.stream = [self.stream]
            else:
                self.stream = []
        if len(self.stream) == 1 and autoBotConfig:
            self.bot = Bot(stream[0].AppKey, stream[0].AppSecret, stream[0].AppKey)
