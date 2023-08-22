import json
from typing import Union
import requests
import aiohttp
from .element import AccessToken

get_token_url = "https://oapi.dingtalk.com/gettoken"


async def url_res(url, method: str = 'GET', header=None, res: str = 'str', **kwargs) -> Union[str, dict]:
    async with aiohttp.ClientSession() as session:
        # logger.info("开始发送")
        async with session.request(method.upper(), url, headers=header, **kwargs) as _res:
            # logger.info("等待返回")
            resp = await _res.text()
            # logger.info(f"已经返回：{resp}")
    # logger.info("发送完成")
    if res == 'json':
        return json.loads(resp)
    else:
        return resp


def get_token(app_key, app_secret) -> AccessToken:
    _url = get_token_url + f"?appkey={app_key}&appsecret={app_secret}"
    token = requests.get(_url).json()
    if not token['errcode']:
        return AccessToken(token['access_token'], token['expires_in'])
    else:
        raise ValueError(f"获取Access-Token失败！错误代码：{token['errcode']}，错误信息：{token['errmsg']}")

