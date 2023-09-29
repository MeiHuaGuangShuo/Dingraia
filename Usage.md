你好！这里是详细的使用方法，在阅读之前，建议查看README.md

# 示例启动文件

首先，这里是一个2.0.0的启动文件

```python
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
    # HTTP 模式如下
    app.start(f_app, port=1145)
    # Stream 模式如下
    app.start()
```

# 启动方法

## 直接启动

### Windows(或使用pkg安装的Linux)

```shell
python main_example.py
```

### Linux(使用apt安装)

```shell
python3 main_example.py
```

# 模块文件

请在启动文件的指定位置填写你的模块文件夹

```python
 7 | # 可修改区域 ↓
>8<| module_dir = "Dir"  # 如果需要按模块导入，则需要填写
 9 | # 可修改区域 ↑
```

<details>
    <summary>不想以模块方式载入？</summary>
    <p>你可以直接在启动文件中写入代码，但需要保持以下内容</p>
    <pre><code lang="python"> 716 | # 可修改区域 ↓
>8<| module_dir = ""  # 此处留空
 9 | # 可修改区域 ↑</code></pre>
</details>
