import json
from typing import Union

import aiohttp
from aiohttp import ClientResponse

from .element import AccessToken

get_token_url = "https://oapi.dingtalk.com/gettoken"


async def url_res(url, method: str = 'GET', headers=None, res: str = 'str', **kwargs) -> Union[ClientResponse, str, dict]:
    async with aiohttp.ClientSession() as session:
        async with session.request(method.upper(), url, headers=headers, **kwargs) as _res:
            resp = await _res.text()
    if res == 'json':
        return json.loads(resp)
    elif res == 'raw':
        return _res
    else:
        return resp


def get_token(app_key, app_secret) -> AccessToken:
    return AccessToken(AppKey=app_key, AppSecret=app_secret)
