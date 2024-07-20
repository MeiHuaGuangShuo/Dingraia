import pkgutil
from dingraia.DingTalk import Dingtalk
from dingraia.config import Config, Bot, CallBack, Stream
from dingraia.saya import Saya
import argparse

# 可修改区域 ↓
module_dir = "example_module"  # 如果需要按模块导入，则需要填写
describe = "这里是Dingraia的示例启动文件"
# 可修改区域 ↑

app = Dingtalk(
    Config(bot=Bot('AppKey',
                   'AppSecret',
                   'robotCode'),
           # Bot 参数是一定要填写的
           event_callback=CallBack("AesKey",
                                   "Token",
                                   "CropId"),
           # event_callback 仅为作为 HTTP 模式的时候使用的，Stream模式无需填写，保持原样即可，支持单/多Stream
           stream=[Stream('AppKey1',
                          'AppSecret1')]
           ))

if __name__ == '__main__':  # 为了兼容 `python -m dingraia`， 此操作是必须的
    parser = argparse.ArgumentParser(description=describe)
    parser.add_argument("--app-key", "-k", type=str, help="Stream 模式下的AppKey")
    parser.add_argument("--app-secret", "-s", type=str, help="Stream 模式下的AppSecret")
    args = parser.parse_args()
    if bool(args.app_key) ^ bool(args.app_secret):
        raise ValueError("Invalid params.Using `-h` for usage.")
    if args.app_key and args.app_secret:
        app.config = Config(
            bot=Bot(args.app_key, args.app_secret, args.app_key),
            stream=[Stream(args.app_key, args.app_secret)]
        )
    saya = Saya.current()
    if module_dir:
        error_dict = {}
        with saya.module_context():
            for module_info in pkgutil.iter_modules([module_dir]):
                if module_info.name.startswith("_"):
                    continue
                saya.require(f"{module_dir}.{module_info.name}")
    app.start()
