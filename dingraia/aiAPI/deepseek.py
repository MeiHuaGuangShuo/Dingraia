"""
DeepSeek API
"""
from typing import Union

from dingraia.aiAPI import APIKeys, OpenAI
import aiohttp

DeepSeek_Chat = "deepseek-chat"
DeepSeek_R1 = "deepseek-reasoner"


class DeepSeek(OpenAI):

    _messages = []

    def __init__(
            self, apiKey: Union[str, APIKeys], systemPrompt: str = "You are a helpful assistant.",
            maxContextLength: int = 1024
            ):
        super().__init__(apiKey, systemPrompt, maxContextLength, baseUrl="https://api.deepseek.com")

    async def getAccountBalance(self) -> tuple[float, float, float, str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.deepseek.com/user/balance",
                    headers={"Authorization": f"Bearer {self.apiKey.getKey()}"}
            ) as response:
                data = await response.json()
                if data.get("is_available"):
                    return (data["balance_infos"][0]["total_balance"], data["balance_infos"][0]["granted_balance"],
                            data["balance_infos"][0]["topped_up_balance"], data["balance_infos"][0]["currency"])
                return 0.0, 0.0, 0.0, "Not available"
