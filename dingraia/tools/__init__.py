from pathlib import Path
from uuid import uuid1
from io import BytesIO, BufferedReader
from contextlib import contextmanager
from typing import AsyncGenerator, Union


def ColoredFormatter(message: str):
    color_map = {
        "red"    : "\033[1;31m",
        "green"  : "\033[1;32m",
        "yellow" : "\033[1;33m",
        "blue"   : "\033[1;34m",
        "magenta": "\033[1;35m",
        "cyan"   : "\033[1;36m",
        "white"  : "\033[1;37m",
        "reset"  : "\033[0m",
    }
    for color in color_map:
        message = message.replace(f"<{color}>", color_map[color])
        message = message.replace(f"</{color}>", color_map["reset"])
    return message


class NoUseClass:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, _):
        return self

    def __getitem__(self, item):
        return self

    def __setitem__(self, key, value):
        return self

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mod__(self, other):
        return self


@contextmanager
def write_temp_file(content: Union[BytesIO, BufferedReader], file_extension: str) -> str:
    """临时写入Bytes到临时目录

    Args:
        content: Bytes 数据
        file_extension: 文件后缀名

    Returns:
        str: 临时文件路径

    """
    fileName = Path.home() / ".dingraia" / f"temp_{uuid1()}.{file_extension}"
    fileName.parent.mkdir(parents=True, exist_ok=True)
    with open(fileName, "wb") as f:
        if isinstance(content, BytesIO):
            f.write(content.getvalue())
        elif isinstance(content, BufferedReader):
            f.write(content.read())
        else:
            raise TypeError(f"content must be BytesIO or BufferedReader, but got {type(content)}")
    yield str(fileName.resolve())
    fileName.unlink()


async def asyncGenerator2list(asyncGenerator: AsyncGenerator) -> list:
    """转换 AsyncGenerator 为 list

    Args:
        asyncGenerator: AsyncGenerator

    Returns:
        list: 转换后的 list

    """
    return [i async for i in asyncGenerator]
