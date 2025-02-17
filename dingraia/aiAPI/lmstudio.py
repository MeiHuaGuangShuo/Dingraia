from typing import Any, AsyncGenerator

from dingraia.model import Group, Member

from dingraia.tools import streamProcessor
from dingraia.aiAPI import aiAPI
from dingraia.log import logger
import aiohttp

LLama_3_2 = "llama3.2"


class LMStudio(aiAPI):

    _messages = []

    def __init__(
            self,
            url: str = "http://localhost:1234/v1",
            systemPrompt: str = "You are a helpful assistant.",
            maxContextLength: int = 4096
    ):
        if url.endswith("/"):
            url = url[:-1]
        self.url = url
        self.systemPrompt = systemPrompt
        self.maxContextLength = maxContextLength

    def generateAnswerFunction(
            self, question: str, model: str = LLama_3_2, user: Member = None, noThinkOutput: bool = False
    ) -> AsyncGenerator[str, Any]:

        async def generateAnswer():
            userMessage = {"role": "user", "content": question}
            if isinstance(user, Member):
                userMessage["content"] = f"UserName: {user.name}, Message: {question}"
                if isinstance(user.group, Group):
                    userMessage["content"] = f"UserName: {user.name}, GroupName: {user.group.name}, Message: {question}"
            self.messages(user=user).append(userMessage)
            payload = self.ChatPayloadBase(user=user).copy()
            payload["model"] = model
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.url + "/chat/completions",
                        json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error in LMStudio API: {response.status} {response.reason}, Response: {await response.text()}")
                        raise StopIteration
                    answer = ""
                    temp = ""
                    onThink = False
                    async for d in streamProcessor(response=response):
                        d: dict
                        if d:
                            content = d["choices"][0]["delta"].get("content", "")
                            if not content:
                                continue
                            if not temp:
                                if content.rfind("<") != -1 and content.rfind(">") == -1:
                                    temp += content
                                    continue
                            else:
                                temp += content
                                if temp.rfind("<") != -1 and temp.rfind(">") == -1:
                                    continue
                                else:
                                    content = temp
                                    temp = ""

                            current_pos = 0
                            while current_pos < len(content):
                                if onThink:
                                    end_pos = content.find('</think>', current_pos)
                                    if end_pos != -1:
                                        think_content = content[current_pos:end_pos]
                                        if not noThinkOutput:
                                            think_content = think_content.replace('\n', '\n> ')
                                            yield think_content
                                        current_pos = end_pos + len('</think>')
                                        onThink = False
                                        remaining = content[current_pos:]
                                        if remaining:
                                            answer += remaining
                                            yield remaining
                                        current_pos = len(content)
                                    else:
                                        think_content = content[current_pos:]
                                        if not noThinkOutput:
                                            think_content = think_content.replace('\n', '\n> ')
                                            yield think_content
                                        current_pos = len(content)
                                else:
                                    start_pos = content.find('<think>', current_pos)
                                    if start_pos != -1:
                                        normal_content = content[current_pos:start_pos]
                                        if normal_content:
                                            answer += normal_content
                                            yield normal_content
                                        current_pos = start_pos + len('<think>')
                                        if not noThinkOutput:
                                            yield "> **思考** \n> \n> "
                                        onThink = True
                                    else:
                                        normal_content = content[current_pos:]
                                        if normal_content:
                                            answer += normal_content
                                            yield normal_content
                                        current_pos = len(content)
                    if answer:
                        self.messages(user=user).append({"role": "assistant", "content": answer})

        return generateAnswer()
