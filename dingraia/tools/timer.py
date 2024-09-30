import time
import inspect
from ..log import logger


def format_time(seconds):
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"  # 纳秒
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"  # 微秒
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"  # 毫秒
    elif seconds < 60:
        return f"{seconds:.2f} s"  # 秒
    elif seconds < 3600:
        minutes, sec = divmod(seconds, 60)
        return f"{seconds:.2f} s ({int(minutes)}m {sec:.2f}s)"
    elif seconds < 86400:
        hours, minutes = divmod(seconds, 3600)
        minutes, sec = divmod(minutes, 60)
        return f"{seconds:.2f} s ({int(hours)}h {int(minutes)}m {sec:.2f}s)"
    else:
        days, hours = divmod(seconds, 86400)
        hours, minutes = divmod(seconds, 3600)
        minutes, sec = divmod(minutes, 60)
        return f"{seconds:.2f} s ({int(days)}d {int(hours)}h {int(minutes)}m {sec:.2f}s)"


class TimeCost:

    def __init__(self, title=None, print_time: bool = True):
        self.title = title
        self.print_time = print_time
        self.start_time = 0.0

    def func_time(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __call__(self, *args, **kwargs):
        if not self.start_time:
            self.start_time = time.perf_counter()
        else:
            self.cost_time = time.perf_counter() - self.start_time
            if self.print_time:
                logger.info(f"Time{f'({self.title})' if self.title is not None else ''}: {format_time(self.cost_time)}",
                            _inspect=inspect.currentframe())

    def __enter__(self):
        self.start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cost_time = time.perf_counter() - self.start_time
        if self.print_time:
            logger.info(f"Time{f'({self.title})' if self.title is not None else ''}: {format_time(self.cost_time)}",
                        _inspect=inspect.currentframe())
