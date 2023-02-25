import asyncio
import itertools
from typing import Union
import inspect

from loguru import logger

from .builtins.broadcast.schema import ListenerSchema
from .context import channel_instance


class Channel:
    reg_event = {}
    
    def __init__(self) -> None:
        pass
    
    def use(self, ListenEvent: Union[list, ListenerSchema]):
        if type(ListenEvent) == ListenerSchema:
            ListenEvent = ListenEvent.listening_events
        
        def wrapper(func):
            module_name = inspect.getmodule(func).__name__
            for event in ListenEvent:
                if event in self.reg_event:
                    if module_name in self.reg_event[event]:
                        self.reg_event[event][module_name].append(func)
                    else:
                        self.reg_event[event][module_name] = [func]
                else:
                    self.reg_event[event] = {}
                    self.reg_event[event][module_name] = [func]
        
        return wrapper
    
    async def radio(self, RadioEvent, *args, sync=True):
        if RadioEvent in self.reg_event:
            modules = list(itertools.chain(*self.reg_event[RadioEvent].values()))
            for f in modules:
                send = {}
                sig = inspect.signature(f)
                params = sig.parameters
                for name, param in params.items():
                    for typ in args:
                        if param.annotation == type(typ):
                            send[name] = typ
                if not inspect.iscoroutine(f):
                    if sync:
                        logger.catch(asyncio.ensure_future)(f(**send))
                    else:
                        await f(**send)
                else:
                    f(**send)
    
    def set_channel(self):
        channel_instance.set(self)
    
    @staticmethod
    def current() -> "Channel":
        return channel_instance.get()
