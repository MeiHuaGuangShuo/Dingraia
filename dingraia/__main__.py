from IPython import embed
import asyncio
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from aiohttp import ClientSession
from loguru import logger
from .message.chain import MessageChain
from .message.element import *
from .element import *
from .model import *
from .tools import *
from .DingTalk import Dingtalk


path = ''
os.environ['NoImportModule'] = '1'
if not os.path.exists(Path("main.py")):
    while True:
        path = input('Input filename(Empty to exit) > ')
        if not os.path.exists(Path(path)):
            logger.error("File not found!")
            exit(1)
path = path or "main.py"
path = path.replace('.py', '')
app: Dingtalk = __import__(path).app
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)


def start_loop():
    loop.run_forever()
    logger.info("loop stopped.")
    
    
def loop_runner(run_cell_async):
    try:
        return app.run_coroutine(run_cell_async)
    except KeyboardInterrupt:
        return
    except Exception as err:
        logger.exception(err)
    
    
pool = ThreadPoolExecutor()
app._loop = loop
logger.info("Init console...")
app.prepare()
pool.submit(start_loop)
logger.info("Starting Console...")
embed(colors='Neutral', using='asyncio', loop_runner=loop_runner)
logger.info("Stopping the loop")
pool.submit(loop.stop)
pool.shutdown(False)
logger.info("Console Stopped.")
os._exit(0)
