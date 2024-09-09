import time
from ..log import logger


class TimeCost:
    
    def __init__(self, title=None):
        self.title = title

    @staticmethod
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
    
    def __enter__(self):
        self.start_time = time.perf_counter()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cost_time = time.perf_counter() - self.start_time
        logger.info(f"Time{f'({self.title})' if self.title is not None else ''}: {self.format_time(cost_time)}")
