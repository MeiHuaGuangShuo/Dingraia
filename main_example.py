import pkgutil
from dingraia.config import Config, Bot, CallBack, Stream
from dingraia.saya import Saya
from dingraia.DingTalk import Dingtalk
from flask import Flask

# 可修改区域 ↓
module_dir = ""  # 如果需要按模块导入，则需要填写
# 可修改区域 ↑

app = Dingtalk(
    Config(bot=Bot('AppKey',
                   'AppSecret',
                   'robotCode'),
           event_callback=CallBack("AesKey",
                                   "Token",
                                   "CropId"),
           # 上方的仅为作为 HTTP 模式的时候使用的，Stream模式仅需配置下方，支持单/多Stream
           stream=[Stream('AppKey1',
                          'AppSecret1'),
                   Stream('AppKey2',
                          'AppSecret2',
                          )]
           ))

saya = Saya.current()
f_app = Flask(__name__)


if module_dir:
    error_dict = {}
    with saya.module_context():
        for module_info in pkgutil.iter_modules([module_dir]):
            if module_info.name.startswith("_"):
                continue
            saya.require(f"{module_dir}.{module_info.name}")

if __name__ == '__main__':
    app.start()
