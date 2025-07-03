import asyncio
import functools
import inspect
from concurrent.futures import ThreadPoolExecutor

from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[RadioComplete]))
async def radio_done_callback(app: Dingtalk, trace_id: TraceId):
    if trace_id is not None:
        if trace_id in app.message_trace_id:
            with ThreadPoolExecutor() as pool:
                async_tasks = []
                for func in app.message_handle_complete_callback:
                    send = {}
                    sig = inspect.signature(func)
                    params = sig.parameters
                    for name, param in params.items():
                        args = app.message_trace_id[trace_id].get("items", [])
                        args.append(app)
                        args.append(trace_id)
                        for typ in args:
                            if isinstance(typ, param.annotation):
                                send[name] = typ
                    notCall = False
                    for name, param in params.items():
                        if name not in send:
                            if param.default == param.empty:
                                try:
                                    logger.warning(
                                        f"Missing values for '{name}'({param.annotation}) at {func.__name__} at file {func.__code__.co_filename}, line {func.__code__.co_firstlineno}")
                                except:
                                    logger.warning(
                                        f"Missing values for '{name}'({param.annotation}) at {func.__name__}")
                                notCall = True
                    if notCall:
                        continue
                    if inspect.iscoroutinefunction(func):
                        async_tasks.append(app.loop.create_task(logger.catch(func)(**send)))
                    else:
                        async_tasks.append(
                            app.loop.run_in_executor(pool, functools.partial(logger.catch(func), **send)))
                await asyncio.gather(*async_tasks)
