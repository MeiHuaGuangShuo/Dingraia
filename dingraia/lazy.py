"""
Lazy库是给懒人的你用的，但是有得必有失，请注意函数名冲突可能存在
"""
import asyncio  # NOQA
import functools  # NOQA
import inspect  # NOQA

from .DingTalk import Dingtalk  # NOQA
from .card import *  # NOQA
from .element import *  # NOQA
from .event.event import *  # NOQA
from .event.message import *  # NOQA
from .log import logger  # NOQA
from .message.chain import MessageChain  # NOQA
from .message.element import *  # NOQA
from .model import *  # NOQA
from .saya import *  # NOQA
from .saya.builtins.broadcast import ListenerSchema  # NOQA
from .tools import *  # NOQA
from .util.async_exec import cpu_bound, io_bound  # NOQA

channel = Channel.current()

onGroupMessage = channel.use(ListenerSchema(listening_events=[GroupMessage]))
onLoadComplete = channel.use(ListenerSchema(listening_events=[LoadComplete]))
onGroupNameChange = channel.use(ListenerSchema(listening_events=[GroupNameChange]))
onMessageSend = channel.use(ListenerSchema(listening_events=[MessageSend]))
onNoMessageSend = channel.use(ListenerSchema(listening_events=[NoMessageSend]))
onChatQuit = channel.use(ListenerSchema(listening_events=[ChatQuit]))
onChatKick = channel.use(ListenerSchema(listening_events=[ChatKick]))
onGroupDisband = channel.use(ListenerSchema(listening_events=[GroupDisband]))
