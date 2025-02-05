from typing import Any, AsyncGenerator

from dingraia.model import Group, Member

from dingraia.tools import streamProcessor
from dingraia.aiAPI import aiAPI
from dingraia.log import logger
import aiohttp

DeepSeek_R1 = "deepseek-ai/DeepSeek-R1"
DeepSeek_V3 = "deepseek-ai/DeepSeek-V3"
DeepSeek_R1_Distill_Llama_70B = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
DeepSeek_R1_Distill_Qwen_32B = "eepseek-ai/DeepSeek-R1-Distill-Qwen-32B"  # 25/2/5 ，界面上确实是这么写的
DeepSeek_R1_Distill_Qwen_14B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
DeepSeek_R1_Distill_Llama_8B = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
DeepSeek_R1_Distill_Qwen_7B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
DeepSeek_R1_Distill_Qwen_1_5B = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
Pro_DeepSeek_R1_Distill_Llama_8B = "Pro/deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
Pro_DeepSeek_R1_Distill_Qwen_7B = "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
Pro_DeepSeek_R1_Distill_Qwen_1_5B = "Pro/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
Llama_3_3_70B_Instruct = "meta-llama/Llama-3.3-70B-Instruct"
Marco_o1 = "AIDC-AI/Marco-o1"
DeepSeek_V2_5 = "deepseek-ai/DeepSeek-V2.5"
Qwen2_5_72B_Instruct_128K = "Qwen/Qwen2.5-72B-Instruct-128K"
Qwen2_5_72B_Instruct = "Qwen/Qwen2.5-72B-Instruct"
Qwen2_5_32B_Instruct = "Qwen/Qwen2.5-32B-Instruct"
Qwen2_5_14B_Instruct = "Qwen/Qwen2.5-14B-Instruct"
Qwen2_5_7B_Instruct = "Qwen/Qwen2.5-7B-Instruct"
Qwen2_5_Coder_32B_Instruct = "Qwen/Qwen2.5-Coder-32B-Instruct"
Qwen2_5_Coder_7B_Instruct = "Qwen/Qwen2.5-Coder-7B-Instruct"
Qwen2_7B_Instruct = "Qwen/Qwen2-7B-Instruct"
Qwen2_1_5B_Instruct = "Qwen/Qwen2-1.5B-Instruct"
QwQ_32B_Preview = "Qwen/QwQ-32B-Preview"
TeleChat2 = "TeleAI/TeleChat2"
Yi_1_5_34B_Chat_16K = "01-ai/Yi-1.5-34B-Chat-16K"
Yi_1_5_9B_Chat_16K = "01-ai/Yi-1.5-9B-Chat-16K"
Yi_1_5_6B_Chat = "01-ai/Yi-1.5-6B-Chat"
Glm_4_9b_Chat = "THUDM/glm-4-9b-chat"
Vendor_A_Qwen2_5_72B_Instruct = "Vendor-A/Qwen/Qwen2.5-72B-Instruct"
Internlm2_5_7b_Chat = "internlm/internlm2_5-7b-chat"
Internlm2_5_20b_Chat = "internlm/internlm2_5-20b-chat"
Llama_3_1_Nemotron_70B_Instruct = "nvidia/Llama-3.1-Nemotron-70B-Instruct"
Meta_Llama_3_1_405B_Instruct = "meta-llama/Meta-Llama-3.1-405B-Instruct"
Meta_Llama_3_1_70B_Instruct = "meta-llama/Meta-Llama-3.1-70B-Instruct"
Meta_Llama_3_1_8B_Instruct = "meta-llama/Meta-Llama-3.1-8B-Instruct"
Gemma_2_27b_It = "google/gemma-2-27b-it"
Gemma_2_9b_It = "google/gemma-2-9b-it"
Pro_Qwen2_5_7B_Instruct = "Pro/Qwen/Qwen2.5-7B-Instruct"
Pro_Qwen2_7B_Instruct = "Pro/Qwen/Qwen2-7B-Instruct"
Pro_Qwen2_1_5B_Instruct = "Pro/Qwen/Qwen2-1.5B-Instruct"
Pro_THUDM_Chatglm3_6b = "Pro/THUDM/chatglm3-6b"
Pro_Glm_4_9b_Chat = "Pro/THUDM/glm-4-9b-chat"
Pro_Meta_Llama_3_1_8B_Instruct = "Pro/meta-llama/Meta-Llama-3.1-8B-Instruct"
Pro_Gemma_2_9b_It = "Pro/google/gemma-2-9b-it"


class SiliconFlow(aiAPI):

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
            apiKey: str,
            systemPrompt: str = "You are a helpful assistant.",
            maxContextLength: int = 1000
    ):
        self.apiKey = apiKey
        self.systemPrompt = systemPrompt
        self.maxContextLength = maxContextLength
        self.messages.append({"role": "system", "content": self.systemPrompt})

    def generateAnswerFunction(
            self, question: str, model: str = DeepSeek_V3, user: Member = None, noThinkOutput: bool = False
    ) -> AsyncGenerator[str, Any]:

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
                        "https://api.siliconflow.cn/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.apiKey}"},
                        json=payload
                ) as response:
                    if response.status != 200:
                        logger.error(
                            f"Error in SiliconFlow API: {response.status} {response.reason}, Response: {await response.text()}")
                        return
                    answer = ""
                    onThink = False
                    async for d in streamProcessor(response=response):
                        d: dict
                        if d:
                            reason_text = d["choices"][0]["delta"].get("reasoning_content")
                            main_text = d["choices"][0]["delta"]["content"]
                            if not answer.strip() and reason_text:
                                onThink = True
                            if onThink and not answer.strip().startswith("> **思考**"):
                                answer += "> **思考**\n> \n> "
                                yield "> **思考**\n> \n> "
                            if reason_text:
                                if "\n" in reason_text:
                                    reason_text = reason_text.replace("\n", "\n> ")
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

    async def getAvailableModels(self) -> dict[str, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.siliconflow.cn/v1/models",
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
