import functools
import inspect
from concurrent.futures import ThreadPoolExecutor

from dingraia.lazy import *


@channel.use(ListenerSchema(listening_events=[RadioComplete]))
async def radio_done_callback(app: Dingtalk, trace_id: TraceId):
    if trace_id is not None:
        if trace_id in app.message_trace_id:
            with ThreadPoolExecutor() as pool:
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
                    if inspect.iscoroutinefunction(func):
                        _ = app.loop.create_task(logger.catch(func)(**send))
                    else:
                        app.loop.run_in_executor(pool, functools.partial(logger.catch(func), **send))
