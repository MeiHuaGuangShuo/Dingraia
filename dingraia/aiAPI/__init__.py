"""

"""
import json

import aiohttp

from ..model import Member, Group
from ..log import logger
from ..tools import streamProcessor
from ..cache import cache
from typing import Any, AsyncGenerator, Dict, Optional, Union, List


class aiAPI:

    _messages: List[dict] = []

    _userMessages: Dict[str, list] = {}

    systemPrompt: str = ""

    maxContextLength: int = 2048

    def messages(self, user: Union[Member, str] = None) -> list:
        usrIdent = self.extractUser(user)
        if isinstance(user, Member) and usrIdent:
            if usrIdent not in self._userMessages:
                prompt = self.extractUserPrompt(user)
                self._userMessages[usrIdent] = [{"role": "system", "content": prompt or self.systemPrompt}]
            messages = self._userMessages[usrIdent]
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

    def ChatPayloadBase(self, user: Union[Member, str] = None) -> dict:
        return {
            "messages": self.messages(user),
            "stream"  : True
        }

    def clearHistory(self, user: Union[Member, str] = None):
        usrIdent = self.extractUser(user)
        if isinstance(user, Member):
            if str(usrIdent) in self._userMessages:
                self._userMessages[usrIdent].clear()
                prompt = self.extractUserPrompt(user)
                if prompt:
                    self._userMessages[usrIdent] = [{"role": "system", "content": prompt}]
            return
        self._messages = [{"role": "system", "content": self.systemPrompt}]
        self._userMessages = {}
        self.saveHistory()

    def deleteMessage(self, count: int = None, user: Union[Member, str] = None):
        if not count:
            self.clearHistory(user=user)
            return
        if isinstance(user, Member):
            usrIdent = self.extractUser(user)
            if str(usrIdent) in self._userMessages:
                mes = self._userMessages[str(usrIdent)]
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
                self._userMessages[str(usrIdent)] = mes
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

    def setSystemPrompt(
            self, prompt: str, user: Union[Member, str] = None,
            clearHistory: bool = False, bindPrompt: bool = False
            ):
        if isinstance(user, Member):
            usrIdent = self.extractUser(user, "Null")
            if clearHistory:
                self._userMessages[usrIdent].clear()
            self._userMessages[usrIdent].extend({"role": "system", "content": prompt})
            if bindPrompt:
                if not cache.value_exist("aiAPI", "name", "userPrompt"):
                    data = {usrIdent: prompt}
                    cache.execute("INSERT INTO aiAPI (name, data) VALUES ('userPrompt',?)", (data,))
                else:
                    data = cache.execute("SELECT data FROM aiAPI WHERE name = 'userPrompt'", result=True)[0][0]
                    data = json.loads(data)
                    data[usrIdent] = prompt
                    cache.execute("UPDATE aiAPI SET data =? WHERE name = 'userPrompt'", (data,))
        else:
            self.systemPrompt = prompt
            if clearHistory:
                self._messages.clear()
                self._messages.append({"role": "system", "content": self.systemPrompt})
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

    def extractUserPrompt(self, user: Optional[Member]) -> Optional[str]:
        if not isinstance(user, Member):
            return None
        if not cache.value_exist("aiAPI", "name", "userPrompt"):
            return None
        usrIdent = self.extractUser(user)
        data = cache.execute("SELECT data FROM aiAPI WHERE name = 'userPrompt'", result=True)[0][0]
        data = json.loads(data)
        prompt = data.get(usrIdent)
        return prompt

    @staticmethod
    def extractUser(user: Optional[Member], default=None):
        if not isinstance(user, Member):
            return user or default
        return user.unionId or default


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
