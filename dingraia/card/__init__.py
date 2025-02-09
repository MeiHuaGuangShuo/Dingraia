from typing import AsyncGenerator, Callable, Generator, Iterator, List, Literal, Iterable, Optional, Protocol, Union

import aiohttp

from ..tools import asyncGenerator2list, streamProcessor
import json as _json


class MarkDown(str):
    pass


class SizedIterable(Protocol, Iterator, Iterable):
    def __len__(self) -> int:
        ...

    def __getitem__(self, item) -> str:
        ...


class BaseCard:

    data: Optional[dict[str, str]] = None

    def __init__(self):
        pass


class PrivateDataBuilder:

    def __init__(self, data: dict[str, dict]):
        self.data = data

    def to_json(self) -> dict:
        temp_data = {}
        for k, v in self.data.items():
            temp_data[k] = {
                "cardParamMap": v
            }
        return temp_data

    def solve(self):
        for k, v in self.data.items():
            if isinstance(self.data[k], dict):
                if len(self.data[k].keys()) == 1 and "cardParamMap" in self.data[k]:
                    self.data[k] = self.data[k]["cardParamMap"]


class AICard(BaseCard):

    response: Optional[Union[SizedIterable[str], list]] = None
    """流式回复内容，必须是可以被迭代的"""

    content_type: Literal["auto", "full", "stream"] = None
    """流式回复内容的类型，默认为auto自动判断，full代表每次全量，stream代表每次追加"""

    _texts: List[str] = []
    """流式回复内容的列表"""

    text: str = ""
    """最新的完整文本"""

    def __init__(self):
        super().__init__()
        self.content_type: str = "auto"

    def set_response(
            self,
            response: Union[SizedIterable[Union[str, MarkDown]], Generator, AsyncGenerator],
            content_type: Literal["auto", "full", "stream"] = "auto"
    ):
        """设置流式回复内容

        Args:
            response: 回复内容，可以是字符串、Generator、AsyncGenerator
            content_type: response输出内容的方式，默认为auto自动判断，stream代表每次追加，full代表每次全量

        Returns:

        """
        self.response = response
        self.content_type = content_type

    def check_response_type(self) -> str:
        if self.content_type not in ["auto", "full", "stream"]:
            raise ValueError(f"content_type must be 'auto', 'full', or 'stream', but got {self.content_type}")
        if not self.content_type:
            self.content_type = "auto"
        if self.content_type == "auto":
            if len(self._texts) <= 1:
                pass
            else:
                if self._texts[1].startswith(self._texts[0]):
                    self.content_type = "full"
                else:
                    self.content_type = "stream"
        return self.content_type

    def set_content(self, content: str):
        self.response = [content]

    async def streaming_string(self, length_limit: int = 0, full_content: bool = True):
        """流式输出

        Args:
            length_limit: 最小输出长度，默认为0，即不限制
            full_content: 是否输出完整文本，默认为True，即输出完整文本

        Returns:

        """
        full_string = ""
        content = ""
        c = ""
        if isinstance(self.response, AsyncGenerator):
            async for c in self.response:
                if not isinstance(c, str):
                    continue
                if not full_content:
                    yield c
                    continue
                self._texts.append(c)
                content += c
                if len(content) >= length_limit:
                    self.check_response_type()
                    if self.content_type == "auto":
                        full_string = content
                        yield content
                    elif self.content_type == "full":
                        full_string = c
                        yield c
                    else:
                        full_string += content
                        yield full_string
                    self.text = full_string
                    content = ""
        else:
            for c in self.response:
                self._texts.append(c)
                content += c
                if len(content) >= length_limit:
                    self.check_response_type()
                    if self.content_type == "auto":
                        full_string = content
                        yield content
                    elif self.content_type == "full":
                        full_string = c
                        yield c
                    else:
                        full_string += content
                        yield full_string
                    self.text = full_string
                    content = ""
        if len(content) < length_limit:
            self.check_response_type()
            if self.content_type == "auto":
                full_string = content
            elif self.content_type == "full":
                full_string = c
            else:
                full_string += content
            self.text = full_string
            yield full_string

    async def completed_string(self) -> str:
        content = await asyncGenerator2list(self.streaming_string())
        if len(content):
            return content[-1]
        return ""

    @property
    def data(self):
        return {"content": self.text}

    def withPostUrl(
            self, post_url: str, json: dict, data_handler: Callable[[dict], str], headers: dict = None,
            timeout: Optional[float] = None
    ):
        async def get_answer():
            async with aiohttp.ClientSession() as session:
                async with session.post(post_url, json=json, headers=headers, timeout=timeout) as response:
                    response.raise_for_status()
                    async for text in streamProcessor(response, data_handler):
                        yield text

        self.set_response(get_answer())
