"""
DeepSeek API
"""
from typing import Any, AsyncGenerator

from dingraia.model import Group, Member

from dingraia.tools import streamProcessor
from dingraia.aiAPI import aiAPI
from dingraia.log import logger
import aiohttp

DeepSeek_Chat = "deepseek-chat"
DeepSeek_R1 = "deepseek-reasoner"
DeepSeekAPI = "https://api.deepseek.com/chat/completions"


class DeepSeek(aiAPI):

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

    def __init__(self, apiKey: str, systemPrompt: str = "You are a helpful assistant.", maxContextLength: int = 1000):
        super().__init__()
        self.apiKey = apiKey
        self.systemPrompt = systemPrompt
        self.maxContextLength = maxContextLength
        self.messages.append({"role": "system", "content": self.systemPrompt})

    def generateAnswerFunction(self, question: str, model: str = DeepSeek_Chat, user: Member = None) -> AsyncGenerator[
        str, Any]:

        async def generateAnswer():
            userMessage = {"role": "user", "content": question}
            if isinstance(user, Member):
                userMessage["name"] = f"{user.name}"
                userMessage["content"] = f"UserName: {user.name}, Message: {question}"
                if isinstance(user.group, Group):
                    userMessage["name"] += f" from {user.group.name}"
                    userMessage["content"] = f"UserName: {user.name}, GroupName: {user.group.name}, Message: {question}"
            self.messages.append(userMessage)
            payload = self.ChatPayloadBase.copy()
            payload["model"] = model
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        DeepSeekAPI,
                        headers={"Authorization": f"Bearer {self.apiKey}"},
                        json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error in DeepSeek API: {response.status} {response.reason}, Response: {await response.text()}")
                        yield StopIteration
                    answer = ""
                    onThink = model == DeepSeek_R1
                    async for d in streamProcessor(response=response):
                        d: dict
                        if d:
                            reason_text = d["choices"][0]["delta"].get("reasoning_content")
                            main_text = d["choices"][0]["delta"]["content"]
                            if onThink and not answer.strip().startswith("> **思考**"):
                                answer += "> **思考**\n> \n> "
                                yield "> **思考**\n> \n> "
                            if reason_text:
                                if "\n" in reason_text:
                                    # reason_text = reason_text.replace("\n\n", "<?\\n\\n?>")
                                    reason_text = reason_text.replace("\n", "\n> ")
                                    # reason_text = reason_text.replace("<?\\n\\n?>", "\n\n> ")
                                answer += reason_text
                                yield reason_text
                                continue
                            if main_text:
                                if onThink:
                                    onThink = False
                                    yield "\n\n"
                                answer += main_text
                                yield main_text
                    if answer:
                        self.messages.append({"role": "assistant", "content": answer})

        return generateAnswer()

    async def getAccountBalance(self) -> tuple[float, float, float, str]:
        async with (aiohttp.ClientSession() as session):
            async with session.get(
                    f"https://api.deepseek.com/user/balance",
                    headers={"Authorization": f"Bearer {self.apiKey}"}
            ) as response:
                data = await response.json()
                if data.get("is_available"):
                    return (data["balance_infos"][0]["total_balance"], data["balance_infos"][0]["granted_balance"],
                            data["balance_infos"][0]["topped_up_balance"], data["balance_infos"][0]["currency"])
                return 0.0, 0.0, 0.0, "Not available"

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
