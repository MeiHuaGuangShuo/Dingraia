import sys
from contextlib import contextmanager
from typing import Union, Callable
import os
from ..log import logger

from .channel import Channel
from .context import channel_instance, saya_instance


class Saya:
    channels = {}
    mirrors = {}
    
    def __init__(self) -> None:
        pass
    
    def set_channel(self):
        saya_instance.set(self)
    
    @contextmanager
    def module_context(self):
        saya_token = saya_instance.set(self)
        yield
        saya_instance.reset(saya_token)
    
    @classmethod
    def current(cls) -> "Saya":
        try:
            return saya_instance.get()
        except LookupError:
            cls().set_channel()
            return saya_instance.get()
    
    def require(self, module_name: str):
        if os.getenv('NoImportModule'):
            return
        if module_name.endswith('.py'):
            module_name = module_name[:-3]
        logger.debug(f"正在载入模块 {module_name}")
        module = __import__(module_name)
        self.channels[module_name] = module
        self.mirrors[module] = module_name
        logger.info(f"模块 {module_name} 载入完成")
    
    def uninstall_channel(self, module_name: Union[str, Callable]):
        if module_name in self.channels or module_name in self.channels.values():  # 写到这里自己都看不懂了
            if module_name in self.channels.values():  # 如果是Callable则会转换成str
                t_module_name = self.mirrors[module_name]
                del self.mirrors[module_name]
                module_name = t_module_name
            if module_name in self.channels:
                del self.channels[module_name]
            else:
                raise KeyError("This must be an issue")
            channel = Channel.current()
            reged = channel.reg_event
            for module in reged.values():
                modules = list(module.keys())
                if module_name in modules:
                    channel.reg_event[event].pop(module_name)
            if module_name in sys.modules:
                del sys.modules[module_name]
        else:
            raise KeyError(f"模块 {module_name} 没有被载入！")
