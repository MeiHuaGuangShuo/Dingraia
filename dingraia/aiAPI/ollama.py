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
                            current_pos = 0
                            while current_pos < len(content):
                                if onThink:
                                    end_pos = content.find('</think>', current_pos)
                                    if end_pos != -1:
                                        think_content = content[current_pos:end_pos]
                                        if not noThinkOutput:
                                            think_content = think_content.replace('\n', '\n> ')
                                            answer += think_content
                                            yield think_content
                                        current_pos = end_pos + len('</think>')
                                        onThink = False
                                        # Process remaining content as normal
                                        remaining = content[current_pos:]
                                        if remaining:
                                            answer += remaining
                                            yield remaining
                                        current_pos = len(content)  # Exit loop after processing
                                    else:
                                        # Entire remaining content is part of think
                                        think_content = content[current_pos:]
                                        if not noThinkOutput:
                                            think_content = think_content.replace('\n', '\n> ')
                                            answer += think_content
                                            yield think_content
                                        current_pos = len(content)
                                        # onThink remains True
                                else:
                                    # Look for <think> in remaining content
                                    start_pos = content.find('<think>', current_pos)
                                    if start_pos != -1:
                                        # Process normal content before <think>
                                        normal_content = content[current_pos:start_pos]
                                        if normal_content:
                                            answer += normal_content
                                            yield normal_content
                                        current_pos = start_pos + len('<think>')
                                        if not noThinkOutput:
                                            yield "> **思考** \n> \n> "
                                        onThink = True
                                    else:
                                        # Process all remaining as normal
                                        normal_content = content[current_pos:]
                                        if normal_content:
                                            answer += normal_content
                                            yield normal_content
                                        current_pos = len(content)
                    if answer:
                        self.messages(user=user).append({"role": "assistant", "content": answer})

        return generateAnswer()
