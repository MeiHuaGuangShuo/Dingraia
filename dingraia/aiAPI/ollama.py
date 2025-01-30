from typing import Any, AsyncGenerator

from dingraia.model import Group, Member

from dingraia.tools import streamProcessor
from dingraia.aiAPI import aiAPI
from dingraia.log import logger
import aiohttp

LLama_3_2 = "llama3.2"
DeepSeek_R1_1_5_B = "deepseek-r1:1.5b"
DeepSeek_R1_7_B = "deepseek-r1:7b"
DeepSeek_R1_8_B = "deepseek-r1:8b"
DeepSeek_R1_14_B = "deepseek-r1:14b"
DeepSeek_R1_32_B = "deepseek-r1:32b"
DeepSeek_R1_70_B = "deepseek-r1:70b"
DeepSeek_R1_671_B = "deepseek-r1:671b"


class Ollama(aiAPI):

    _messages = []

    @property
    def messages(self) -> list:
        if len(self._messages) > 1:
            texts = "".join([str(m.get("content", "")) for m in self._messages])
            while len(texts) > self.maxContextLength:
                self._messages.pop(1)
                texts = "".join([str(m.get("content", "")) for m in self._messages])
        return self._messages

    @property
    def ChatPayloadBase(self) -> dict:
        return {
            "messages": self.messages,
            "stream"  : True
        }

    def __init__(
            self,
            url: str = "http://localhost:11434",
            systemPrompt: str = "You are a helpful assistant.",
            maxContextLength: int = 1000
    ):
        if url.endswith("/"):
            url = url[:-1]
        self.url = url
        self.systemPrompt = systemPrompt
        self.maxContextLength = maxContextLength
        self.messages.append({"role": "system", "content": self.systemPrompt})

    def generateAnswerFunction(self, question: str, model: str = LLama_3_2, user: Member = None) -> AsyncGenerator[
        str, Any]:

        async def generateAnswer():
            userMessage = {"role": "user", "content": question}
            if isinstance(user, Member):
                userMessage["content"] = f"UserName: {user.name}, Message: {question}"
                if isinstance(user.group, Group):
                    userMessage["content"] = f"UserName: {user.name}, GroupName: {user.group.name}, Message: {question}"
            self.messages.append(userMessage)
            payload = self.ChatPayloadBase.copy()
            payload["model"] = model

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.url + "/api/chat",
                        json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error in Ollama API: {response.status} {response.reason}, Response: {await response.text()}")
                        raise StopIteration
                    answer = ""
                    onThink = False
                    async for d in streamProcessor(response=response, line_prefix=""):
                        d: dict
                        if d:
                            content = d["message"]["content"]
                            if "<think>" in content and "</think>" in content:
                                answer += "> **思考: ** "
                                yield "> **思考: ** "
                                content = content.replace("<think>", "").replace("</think>", "")
                            elif "<think>" in content:
                                onThink = True
                                answer += "> **思考**\n> \n> "
                                yield "> **思考**\n> \n> "
                                content = content.replace("<think>", "")
                            elif "</think>" in content:
                                onThink = False
                                yield "\n\n---\n\n"
                                answer += "\n\n---\n\n"
                                content = content.replace("</think>", "")
                            if content:
                                if onThink and "\n" in content:
                                    content = content.replace("\n", "\n> ")
                                answer += content
                                yield content
                    if answer:
                        self.messages.append({"role": "assistant", "content": answer})

        return generateAnswer()

    async def getAvailableModels(self) -> dict[str, str]:
        async with (aiohttp.ClientSession() as session):
            async with session.get(
                    f"https://api.deepseek.com/models",
                    headers={"Authorization": f"Bearer {self.apiKey}"}
            ) as response:
                data = await response.json()
                data = data["data"]
                models = {}
                for model in data:
                    models[model["id"]] = model
                return models

    def clearHistory(self):
        self._messages = [
            {"role": "system", "content": self.systemPrompt}
        ]
