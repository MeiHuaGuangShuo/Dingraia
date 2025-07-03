import json
import random
import string
from pathlib import Path
from uuid import uuid1
from io import BytesIO, BufferedReader
from contextlib import contextmanager
from typing import AsyncGenerator, Callable, Optional, Union
from dingraia.log import logger

import aiohttp


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
    try:
        yield str(fileName.resolve())
    except:
        pass
    fileName.unlink()


async def asyncGenerator2list(asyncGenerator: AsyncGenerator) -> list:
    """转换 AsyncGenerator 为 list

    Args:
        asyncGenerator: AsyncGenerator

    Returns:
        list: 转换后的 list

    """
    return [i async for i in asyncGenerator]


async def streamProcessor(
        response: aiohttp.ClientResponse,
        data_handler: Callable[[dict], Optional[str]] = None,
        line_prefix: str = "data:"
) -> AsyncGenerator[Union[str, dict], None]:
    """
    流式处理 HTTP 响应数据，将数据按行切分，并处理每行数据，返回处理后的结果（可选）
    Args:
        response: aiohttp.ClientResponse对象
        data_handler: 数据处理函数，接收json字符串，返回处理后的结果，留空则不处理直接返回dict对象
        line_prefix: 数据行前缀，默认"data:"

    Returns:
        AsyncGenerator[Union[str, dict], None]: 处理后的结果

    """
    buffer = ""
    async for chunk in response.content.iter_any():
        buffer += chunk.decode('utf-8', errors='replace')
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            processed = processLine(line, line_prefix, data_handler)
            if processed is not None:
                yield processed
    if buffer.strip():
        yield processLine(buffer, line_prefix, data_handler) or None


def processLine(
        line: str,
        prefix: str,
        handler: Callable[[dict], Optional[str]] = None
) -> Optional[Union[str, dict]]:
    """将数据从流式数据中提取出来

    Args:
        line: 数据行
        prefix: 数据行前缀
        handler: 数据处理函数，接收json字符串，返回处理后的结果，留空则不处理直接返回dict对象

    Returns:

    """
    line = line.strip()
    if prefix:
        if not line.startswith(prefix):
            return None
    try:
        json_str = line[len(prefix):].strip()
        if handler:
            return handler(json.loads(json_str)) if json_str else None
        return json.loads(json_str)
    except json.JSONDecodeError:
        # logger.error(f"Invalid JSON data: {line}")
        # 感觉没什么用，但是可能将来有用
        return None
    except Exception as e:
        logger.exception(f"Error processing line: {line}", e)
        return None


def randomChars(length: int) -> str:
    """生成随机字符串

    Args:
        length: 字符串长度

    Returns:
        str: 随机字符串

    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
