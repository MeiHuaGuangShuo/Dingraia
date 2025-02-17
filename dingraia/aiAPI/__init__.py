"""

"""
import json

import aiohttp

from ..model import Member, Group
from ..log import logger
from ..tools import streamProcessor
from ..cache import cache
from typing import Any, AsyncGenerator, Dict, Union, List


class aiAPI:

    _messages: List[dict] = []

    _userMessages: Dict[str, list] = {}

    systemPrompt: str = ""

    maxContextLength: int = 2048

    def messages(self, user: Union[Member, int] = None) -> list:
        if isinstance(user, Member) and user.id:
            if str(user.id) not in self._userMessages:
                self._userMessages[str(user.id)] = [{"role": "system", "content": self.systemPrompt}]
            messages = self._userMessages[str(user.id)]
        else:
            if not self._messages:
                self._messages.append({"role": "system", "content": self.systemPrompt})
            messages = self._messages
        if len(messages) > 1:
            texts = "".join([str(m.get("content", "")) for m in messages])
            while len(texts) > self.maxContextLength:
                messages.pop(1)
                texts = "".join([str(m.get("content", "")) for m in messages])
        return messages

    def ChatPayloadBase(self, user: Union[Member, int] = None) -> dict:
        return {
            "messages": self.messages(user),
            "stream"  : True
        }

    def clearHistory(self, user: Union[Member, int] = None):
        if isinstance(user, Member):
            if str(int(user)) in self._userMessages:
                self._userMessages.pop(str(user.id))
            return
        self._messages = [{"role": "system", "content": self.systemPrompt}]
        self._userMessages = {}
        self.saveHistory()

    def deleteMessage(self, count: int = None, user: Union[Member, int] = None):
        if not count:
            self.clearHistory(user=user)
            return
        if isinstance(user, Member):
            if str(int(user)) in self._userMessages:
                mes = self._userMessages[str(user.id)]
                msgLen = len(mes)
                if msgLen <= 3:
                    mes = []
                elif count * 2 >= msgLen - 1:
                    mes = []
                else:
                    while count > 0:
                        m = mes[-1]
                        if m.get("role") == "user":
                            count -= 1
                        mes.pop(-1)
                self._userMessages[str(user.id)] = mes
            return
        mes = self._messages
        msgLen = len(mes)
        if msgLen <= 3:
            mes = []
        elif count * 2 >= msgLen - 1:
            mes = []
        else:
            while count > 0:
                m = mes[-1]
                if m.get("role") == "user":
                    count -= 1
                mes.pop(-1)
        self._messages = mes
        self.saveHistory()



    def saveHistory(self):
        data = json.dumps({
            "messages"    : self._messages,
            "userMessages": self._userMessages
        }, ensure_ascii=False, indent=4)
        if not cache.value_exist("aiAPI", "name", "history"):
            cache.execute("INSERT INTO aiAPI (name, data) VALUES ('history',?)", (data,))
        else:
            cache.execute("UPDATE aiAPI SET data =? WHERE name = 'history'", (data,))
        cache.commit()

    def loadHistory(self):
        if not cache.value_exist("aiAPI", "name", "history"):
            return
        data = cache.execute("SELECT data FROM aiAPI WHERE name = 'history'", result=True)[0][0]
        data = json.loads(data)
        self._messages = data.get("messages", [])
        self._userMessages = data.get("userMessages", {})


class OpenAI(aiAPI):

    apiKey: str = ""

    baseUrl: str = "https://api.openai.com/v1"

    platformName: str = "OpenAI"

    def __init__(
            self,
            apiKey: str,
            systemPrompt: str = "You are a helpful assistant.",
            maxContextLength: int = 2048,
            baseUrl: str = "https://api.openai.com/v1",
    ):
        self.apiKey = apiKey
        if baseUrl:
            if baseUrl.endswith("/"):
                baseUrl = baseUrl[:-1]
            self.baseUrl = baseUrl
        self.systemPrompt = systemPrompt
        self.maxContextLength = maxContextLength
        self.loadHistory()
        if not self.messages():
            self.messages().append({"role": "system", "content": self.systemPrompt})

    async def getAvailableModels(self) -> dict[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.baseUrl + "/models",
                    headers={"Authorization": f"Bearer {self.apiKey}"}
            ) as response:
                data = await response.json()
                data = data["data"]
                models = {}
                for model in data:
                    models[model["id"]] = model
                return models

    def generateAnswerFunction(
            self, question: str, model: str = "", user: Member = None, noThinkOutput: bool = False
    ) -> AsyncGenerator[str, Any]:

        async def generateAnswer():
            userMessage = {"role": "user", "content": question}
            if isinstance(user, Member):
                userMessage["content"] = f"UserName: {user.name}, Message: {question}"
                if isinstance(user.group, Group):
                    userMessage["content"] = f"UserName: {user.name}, GroupName: {user.group.name}, Message: {question}"
            self.messages(user).append(userMessage)
            payload = self.ChatPayloadBase(user).copy()
            payload["model"] = model
            preWriteAssistantMessage = {"role": "assistant", "content": "{Not complete yet, ignore this message}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.baseUrl + "/chat/completions",
                        headers={"Authorization": f"Bearer {self.apiKey}"},
                        json=payload
                ) as response:
                    self.messages(user).append(preWriteAssistantMessage)
                    if response.status != 200:
                        logger.error(
                            f"Error in {self.platformName} API: {response.status} {response.reason}, Response: {await response.text()}")
                        yield f"Error in {self.platformName} API: {response.status} {response.reason}"
                        preWriteAssistantMessage["content"] = "{Empty Answer}"
                        return
                    answer = ""
                    onThink = False
                    async for d in streamProcessor(response=response):
                        d: dict
                        if d:
                            reason_text = d["choices"][0]["delta"].get("reasoning_content")
                            main_text = d["choices"][0]["delta"].get("content")
                            if not answer.strip() and reason_text:
                                onThink = True
                            if onThink and not answer.strip().startswith("> **思考**") and not noThinkOutput:
                                yield "> **思考**\n> \n> "
                            if reason_text:
                                if "\n" in reason_text:
                                    reason_text = reason_text.replace("\n", "\n> ")
                                if not noThinkOutput:
                                    yield reason_text
                                continue
                            if main_text:
                                if onThink:
                                    onThink = False
                                    yield "\n\n"
                                answer += main_text
                                yield main_text
                    if answer:
                        preWriteAssistantMessage["content"] = answer
                    else:
                        preWriteAssistantMessage["content"] = "{Empty Answer}"
                    self.saveHistory()

        return generateAnswer()
