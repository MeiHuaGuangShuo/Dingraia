from IPython import embed
import os
from pathlib import Path
from .message.chain import MessageChain
from .message.element import *
from .element import *


path = ''
oapi = "https://oapi.dingtalk.com"
api = "https://api.dingtalk.com"
os.environ['NoImportModule'] = '1'
if not os.path.exists(Path("main.py")):
    while True:
        path = input('Input filename(Empty to exit) > ')
        if not os.path.exists(Path(path)):
            print("File not found!")
path = path or "main.py"
path = path.replace('.py', '')
app = __import__(path).app
embed(colors='Neutral', using='asyncio')

