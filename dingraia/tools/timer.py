import time
from ..log import logger


class TimeCost:
    
    def __init__(self, title=None):
        self.title = title
    
    def __enter__(self):
        self.start_time = time.time()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        cost_time = time.time() - self.start_time
        logger.info(f"Time{f'({self.title})' if self.title is not None else ''}: {cost_time}s")
