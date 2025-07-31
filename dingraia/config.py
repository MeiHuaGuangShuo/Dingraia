from typing import Any, Awaitable, Callable, Coroutine, Dict, List, Optional, Union

from aiohttp.web import Request
from aiohttp.web_response import StreamResponse

from .element import AppKey, AppSecret, EndPoint, Ticket
from .i18n import i18n
from .log import logger
from .message.chain import MessageChain


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
            StreamUrl: str = None,
            SignHandler: Union[
                Callable[
                    [Union[str, AppKey], Union[str, AppSecret]],
                    Union[
                        Dict[Union[Union[str, EndPoint, Ticket]], str],
                        Coroutine[Any, Any, Dict[Union[Union[str, EndPoint, Ticket]], str]]
                    ]
                ],
                str
            ] = None,
            ExtraHeaders: dict = None
    ):
        """自定义Stream连接配置

        Args:
            StreamUrl: Websocket连接地址，必须以ws或wss开头
            SignHandler: 验证签名方法。如果为字符串则向网址POST数据，验证方法和钉钉官网一致；如果为函数则传入AppKey和AppSecret，必须返回包含 `endpoint` 和 `ticket` 的字典
            ExtraHeaders: 进行Stream连接时附加的HTTP头部
        """
        self.StreamUrl = StreamUrl
        self.SignHandler = SignHandler
        self.ExtraHeaders = ExtraHeaders or {}


Handler = Callable[[Request], Awaitable[StreamResponse]]
Middleware = Callable[[Request, Handler], Awaitable[StreamResponse]]


class DataCacheTime:

    def __init__(
            self,
            dataCacheTime: int = 3600,
            *,
            userInfoCacheTime: int = None,
            groupInfoCacheTime: int = None,
            userUnionIdConventCacheTime: int = 410281690,
    ):
        self.dataCacheTime = dataCacheTime
        self.userInfoCacheTime = userInfoCacheTime or dataCacheTime
        self.groupInfoCacheTime = groupInfoCacheTime or dataCacheTime
        self.userUnionIdConventCacheTime = userUnionIdConventCacheTime


class FailedMessage:

    def __init__(
            self,
            *,
            onNSFWMessage: Any = MessageChain(i18n.NSFWMessageWarningText),
    ):
        """指定在特定情况失败时要发送的消息，参数同 Dingtalk.send_message 的 msg 参数，None为禁用

        Args:
            onNSFWMessage: 检测到NSFW消息时要发送的消息

        """
        self.onNSFWMessage = onNSFWMessage


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
            dataCacheTime: DataCacheTime = None,
            waitRadioMessageFinishedTimeout: int = 10,
            webRequestHandlers: List[Middleware] = None,
            raiseForApiError: bool = True,
            sendMessageOnFailed: Optional[FailedMessage] = None,
            language: str = None,
    ):
        """初始化Config
        
        Notes:
            在 `autoBotConfig` 启用且 `Stream` 启用时会自动替换 `Bot` 的值
        
        Args:
            event_callback:
            bot:
            stream:
            autoBotConfig: 是否自动替换Bot的值
            useDatabase: 是否使用数据库，不使用数据库可能会导致异常
            raiseForApiError: 是否在请求API失败时主动抛出异常
            sendMessageOnFailed: 是否在发送失败时发送替代信息
            waitRadioMessageFinishedTimeout: 停止时等待广播消息处理完成的超时时间
            webRequestHandlers: 自定义请求处理器
            language: 语言
        """
        self.raiseForApiError = raiseForApiError
        self.useDatabase = useDatabase
        self.dataCacheTime = dataCacheTime or DataCacheTime()
        self.waitRadioMessageFinishedTimeout = waitRadioMessageFinishedTimeout
        self.event_callback = event_callback
        self.customStreamConnect = customStreamConnect
        self.sendMessageOnFailed = sendMessageOnFailed
        self.bot: Optional[Bot] = bot
        self.stream: Optional[List[Stream]] = stream
        self.webRequestHandlers = webRequestHandlers or []
        if self.stream is not None:
            if not isinstance(self.stream, list):
                self.stream = [self.stream]  # NOQA
        else:
            self.stream = []
        if language:
            i18n.setLang(language)
        if not useDatabase:
            logger.warning(i18n.DisableDatabaseWarningText)
        if len(self.stream) == 1 and autoBotConfig:
            self.bot = Bot(stream[0].AppKey, stream[0].AppSecret, stream[0].AppKey)
