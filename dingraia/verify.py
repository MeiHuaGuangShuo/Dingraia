import json
from typing import Union, Any

import aiohttp
import requests
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
    _url = get_token_url + f"?appkey={app_key}&appsecret={app_secret}"
    token = requests.get(_url).json()
    if not token['errcode']:
        return AccessToken(token['access_token'], token['expires_in'])
    else:
        raise ValueError(f"获取Access-Token失败！错误代码：{token['errcode']}，错误信息：{token['errmsg']}")
