import asyncio
import functools
import inspect
import itertools
from concurrent.futures import ThreadPoolExecutor

from ..log import logger

from .builtins.broadcast.schema import ListenerSchema
from .context import channel_instance
from ..event.event import *


class Channel:
    reg_event = {}
    pool: ThreadPoolExecutor = None
    
    def __init__(self) -> None:
        pass
    
    def use(self, ListenEvent: Union[list, ListenerSchema]):
        if isinstance(ListenEvent, ListenerSchema):
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
            return func
        
        return wrapper

    async def radio(self, RadioEvent, *args, async_await: bool = False, trace_id: str = None, **kwargs):
        # logger.debug(f"{type(RadioEvent) in self.reg_event} {RadioEvent} {type(RadioEvent)} {self.reg_event}")
        if not trace_id:
            for a in args:
                if isinstance(a, (Group, Member)):
                    trace_id = a.trace_id
                    break
        if type(RadioEvent) is not type:
            RadioEvent = type(RadioEvent)
        if RadioEvent in self.reg_event:
            modules = list(itertools.chain(*self.reg_event[RadioEvent].values()))
            async_tasks = []
            loop = asyncio.get_event_loop()
            if not self.pool:
                self.pool = ThreadPoolExecutor()

            async def radio():
                with ThreadPoolExecutor() as pool:
                    for f in modules:
                        send = {}
                        sig = inspect.signature(f)
                        params = sig.parameters
                        for name, param in params.items():
                            for typ in args:
                                if isinstance(typ, param.annotation):
                                    send[name] = typ
                        send.update(kwargs)
                        if inspect.iscoroutinefunction(f):
                            async_tasks.append(loop.create_task(logger.catch(f)(**send)))
                        else:
                            async_tasks.append(loop.run_in_executor(pool, functools.partial(logger.catch(f), **send)))
                    if async_tasks and async_await:
                        await asyncio.gather(*async_tasks)
                        async_tasks.clear()

            task = loop.create_task(radio())
            if trace_id:
                def callback(_):
                    event = RadioComplete()
                    event.trace_id = trace_id
                    loop.create_task(self.radio(event, *[event, trace_id]))

                task.add_done_callback(callback)
    
    def set_channel(self):
        channel_instance.set(self)
    
    @classmethod
    def current(cls) -> "Channel":
        try:
            return channel_instance.get()
        except LookupError:
            cls().set_channel()
            return channel_instance.get()
