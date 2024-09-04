from typing import Generator, Iterator, List, Literal, Iterable, Optional, Protocol, Union


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
    _content_type: Optional[str] = None
    _texts: List[str] = []
    text: str = ""

    def __init__(self):
        super().__init__()

    def set_response(
            self,
            response: Union[SizedIterable[Union[str, MarkDown]], Generator],
            content_type: Literal["auto", "full", "stream"] = "auto"
    ):
        self.response = response
        self._content_type = content_type

    def check_response_type(self) -> str:
        if not self._content_type:
            self._content_type = "auto"
        if self._content_type == "auto":
            if len(self._texts) <= 1:
                pass
            else:
                if self._texts[1].startswith(self._texts[0]):
                    self._content_type = "full"
                else:
                    self._content_type = "stream"
        return self._content_type

    def set_content(self, content: str):
        self.response = [content]

    def streaming_string(self, length_limit: int = 0):
        """流式输出，总是输出完整文本

        Args:
            length_limit: 最小输出长度，默认为0，即不限制

        Returns:

        """
        full_string = ""
        content = ""
        c = ""
        for c in self.response:
            self._texts.append(c)
            content += c
            if len(content) >= length_limit:
                self.check_response_type()
                if self._content_type == "auto":
                    full_string = content
                    yield content
                elif self._content_type == "full":
                    full_string = c
                    yield c
                else:
                    full_string += content
                    yield full_string
                self.text = full_string
                content = ""
        if len(content) < length_limit:
            self.check_response_type()
            if self._content_type == "auto":
                full_string = content
            elif self._content_type == "full":
                full_string = c
            else:
                full_string += content
            self.text = full_string
            yield full_string

    def completed_string(self) -> str:
        content = list(self.streaming_string())
        if len(content):
            return content[-1]
        return ""

    @property
    def data(self):
        return {"content": self.text}
