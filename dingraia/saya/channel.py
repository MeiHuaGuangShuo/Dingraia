import asyncio
import functools
import inspect
import itertools
from concurrent.futures import ThreadPoolExecutor

from .builtins.broadcast.schema import ListenerSchema
from .context import channel_instance
from ..event.event import *
from ..log import logger


class Channel:
    reg_event = {}
    pool: ThreadPoolExecutor = None
    onStop = False
    pendingRadios: List[asyncio.Task] = []

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

    async def radio(self, RadioEvent, *args, async_await: bool = False, traceId: TraceId = None, **kwargs):
        # logger.debug(f"{type(RadioEvent) in self.reg_event} {RadioEvent} {type(RadioEvent)} {self.reg_event}")
        # logger.debug(traceId)
        if self.onStop:
            return
        if not traceId:
            for a in args:
                if isinstance(a, (Group, Member)):
                    traceId = a.traceId
                    break
        if type(RadioEvent) is not type:
            RadioEvent = type(RadioEvent)
        if RadioEvent in self.reg_event:
            modules = list(itertools.chain(*self.reg_event[RadioEvent].values()))
            async_tasks = []
            loop = asyncio.get_event_loop()
            if not self.pool:
                self.pool = ThreadPoolExecutor()

            def callback():
                event = RadioComplete()
                event.trace_id = traceId
                loop.create_task(self.radio(RadioComplete, *[event, traceId, app], traceId=traceId))

            async def radio():
                with ThreadPoolExecutor() as pool:
                    for f in modules:
                        send = {}
                        sig = inspect.signature(f)
                        params = sig.parameters
                        for name, param in params.items():
                            for typ in args:
                                if param.annotation == "Dingtalk":
                                    send[name] = app
                                    continue
                                if isinstance(typ, param.annotation):
                                    send[name] = typ
                        send.update(kwargs)
                        if inspect.iscoroutinefunction(f):
                            async_tasks.append(logger.catch(f)(**send))
                        else:
                            async_tasks.append(loop.run_in_executor(pool, functools.partial(logger.catch(f), **send)))
                    should_callback = traceId and RadioEvent is not RadioComplete and app is not None

                    # async_tasks.append(callback())

                    async def _callback():
                        await asyncio.gather(*async_tasks)
                        if should_callback:
                            callback()
                        async_tasks.clear()

                    def _done_callback(future: asyncio.Task):
                        try:
                            r = future.result()
                        finally:
                            try:
                                self.pendingRadios.remove(future)
                            except ValueError:
                                pass
                    if async_tasks:
                        t = loop.create_task(_callback())
                        self.pendingRadios.append(t)
                        t.add_done_callback(_done_callback)
                        if async_await:
                            await t

            app = None
            for e in args:
                check = e
                if type(check) is not type:
                    check = type(check)
                if check.__name__ == "Dingtalk":
                    app = e
                    break
            # async_await = True
            task = loop.create_task(radio())
            if async_await:
                await task

    def set_channel(self):
        channel_instance.set(self)

    @classmethod
    def current(cls) -> "Channel":
        try:
            return channel_instance.get()
        except LookupError:
            cls().set_channel()
            return channel_instance.get()
