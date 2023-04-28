import json
from typing import Union

import aiohttp
from loguru import logger

get_token_url = "https://oapi.dingtalk.com/gettoken"


async def url_res(url, method: str = 'GET', data=None, header=None, res: str = 'str') -> Union[str, dict]:
    async with aiohttp.ClientSession() as session:
        # logger.info("开始发送")
        async with session.request(method.upper(), url, headers=header, json=data) as _res:
            # logger.info("等待返回")
            resp = await _res.text()
            # logger.info(f"已经返回：{resp}")
            await session.close()
    # logger.info("发送完成")
    if res == 'json':
        return json.loads(resp)
    else:
        return resp


async def get_token(app_key, app_secret) -> str:
    _url = get_token_url + f"?appkey={app_key}&appsecret={app_secret}"
    token = await url_res(_url, res='json')
    if not token['errcode']:
        logger.success(f"成功获取Access-Token: {token['access_token']}，有效期：{token['expires_in']}秒")
        return token['access_token']
    else:
        logger.error(f"获取失败！错误代码：{token['errcode']}，错误信息：{token['errmsg']}")
        raise ValueError("获取Access-Token失败！")

