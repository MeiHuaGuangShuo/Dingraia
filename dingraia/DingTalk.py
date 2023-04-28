import hmac
import time
import base64
import urllib.parse
from loguru import logger
from functools import reduce
from .message.chain import MessageChain
from .login import url_res
from .model import Group
from .message.element import *
from .saya import Channel, Saya
from .tools.debug import delog


send_url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}"


@logger.catch
def get_sign(secure_key: str):
    timestamp = str(round(time.time() * 1000))
    sign_str = timestamp + '\n' + secure_key
    sign = hmac.new(secure_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256).digest()
    sign = base64.b64encode(sign)
    sign = urllib.parse.quote_plus(sign)
    delog.success(f"成功加签", no=40)
    return sign, timestamp


class Dingtalk:
    """
    send_message: msg\n
    send_link: title, text, message_url,  picture_url\n
    send_markdown: title, text\n
    send_actioncard: title, text, button, orientation\n
    send_feedcard: links\n
    """
    sec_key = None
    access_token = None
    
    @staticmethod
    def __init__(sec_key=None, access_token=None):
        if Dingtalk.sec_key is None:
            if sec_key is not None:
                Dingtalk.sec_key = sec_key
            else:
                raise ValueError
        if Dingtalk.access_token is None:
            if sec_key is not None:
                Dingtalk.access_token = access_token
            else:
                raise ValueError
    
    async def send_message(self, target: Union[Group, str, None], msg, header=None):
        """发送普通的文本信息
        
        Args:
            target: 要发送的地址，可以是Group, str格式的链接, 或者None发送到测试群
            msg: 要发送的文本
            header: 要包含的请求头

        Returns:
            None

        """
        if type(msg) == Link:
            send_data = msg.data
        elif type(msg) == Markdown:
            send_data = msg.data
        elif type(msg) == ActionCard:
            send_data = msg.data
        elif type(msg) == FeedCard:
            send_data = msg.data
        else:
            send_data = {
                "msgtype": "text",
                "text"   : {
                    "content": str(msg)
                }
            }
        if type(msg) == MessageChain:
            if ats := msg.include(At):
                at = reduce(lambda x, y: x + y, ats)
                send_data["at"] = at.data
        sign = self.get_sign(Dingtalk.sec_key)
        if target is None:
            url = send_url.format(Dingtalk.access_token, sign[1], sign[0])
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        elif type(target) == Group:
            url = target.send_url
            self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        delog.info(send_data, no=60)
        return await self._send(url, send_data, header)
    
    async def send_link(self, target: Union[Group, str, None], title: str, text: str, mes_url: str, pic_url: str = "",
                        header=None):
        """发送一个链接
        
        Args:
            target: 要发送的地址，可以是Group, str格式的链接, 或者None发送到测试群
            title: 链接标题
            text: 链接简介
            mes_url: 链接
            pic_url: 图片链接
            header: 要包含的请求头

        Returns:
            None

        """
        send_data = {
            "msgtype": "link",
            "link"   : {
                "title"     : str(title),
                "text"      : str(text),
                "picUrl"    : self._link_detect(str(pic_url)),
                "messageUrl": self._link_detect(str(mes_url))
            }
        }
        sign = self.get_sign(Dingtalk.sec_key)
        if target is None:
            url = send_url.format(Dingtalk.access_token, sign[1], sign[0])
            self.log.info(f"[SEND] <- [链接({str(mes_url)})]")
        elif type(target) == Group:
            url = target.send_url
            self.log.info(f"[SEND][{target.name}({int(target)})] <- [链接({str(mes_url)})]")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- [链接({str(mes_url)})]")
        return await self._send(url, send_data, header)
    
    async def send_markdown(self, target: Union[Group, str, None], title: str, text: str, header=None):
        """发送Markdown形式的消息
        
        Args:
            target: 要发送的地址，可以是Group, str格式的链接, 或者None发送到测试群
            title: 标题(似乎没啥用)
            text: Markdown文本
            header: 要包含的请求头

        Returns:
            None

        """
        send_data = {
            "msgtype" : "markdown",
            "markdown": {
                "title": str(title),
                "text" : str(text),
            }
        }
        sign = self.get_sign(Dingtalk.sec_key)
        if target is None:
            url = send_url.format(Dingtalk.access_token, sign[1], sign[0])
            self.log.info(f"[SEND] <- [MarkDown({str(title)})]")
        elif type(target) == Group:
            url = target.send_url
            self.log.info(f"[SEND][{target.name}({int(target)})] <- [MarkDown({str(title)})]")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- [MarkDown({str(title)})]")
        return await self._send(url, send_data, header)
    
    async def send_actioncard(self, target: Union[Group, str, None], title: str, text: str, button: list,
                              orientation: int = 0, header=None):
        """发送ActionCard消息
        
        Args:
            target: 要发送的地址，可以是Group, str格式的链接, 或者None发送到测试群
            title: 标题(似乎没啥用)
            text: Markdown文本
            button: 按钮列表，即使只有一个也要使用[[title, url], ...]的格式
            orientation: 排列方向，0为竖向，1为横向，建议横向不超过5个字
            header: 要包含的请求头

        Returns:
            None

        """
        send_data = {
            "msgtype"   : "actionCard",
            "actionCard": {
                "title"         : str(title),
                "text"          : str(text),
                "btnOrientation": str(orientation)
            }
        }
        if len(button) == 1:
            send_data['actionCard']['singleTitle'] = str(button[0][0])
            send_data['actionCard']['singleURL'] = self._link_detect(str(button[0][1]))
        else:
            send_data['actionCard']['btns'] = []
            for b in button:
                if b[0] and b[1]:
                    send_data['actionCard']['btns'].append(
                        {"title": str(b[0]), "actionURL": self._link_detect(str(b[1]))})
        sign = self.get_sign(Dingtalk.sec_key)
        if target is None:
            url = send_url.format(Dingtalk.access_token, sign[1], sign[0])
            self.log.info(f"[SEND] <- [ActionCard({str(title)})]")
        elif type(target) == Group:
            url = target.send_url
            self.log.info(f"[SEND][{target.name}({int(target)})] <- [ActionCard({str(title)})]")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- [ActionCard({str(title)})]")
        return await self._send(url, send_data, header)
    
    async def send_feedcard(self, target: Union[Group, str, None], links: list, header=None):
        """发送FeedCard消息
        
        Args:
            target: 要发送的地址，可以是Group, str格式的链接, 或者None发送到测试群
            links: 链接列表，格式：[[title, msgURL, picURL], ...]
            header: 要包含的请求头

        Returns:
            None

        """
        if not links:
            logger.error("传入的FeedCard链接不能为空")
            return False
        send_data = {
            "msgtype" : "feedCard",
            "feedCard": {
                "links": []
            }
        }
        for link in links:
            if link[0] and link[1]:
                send_data['feedCard']['links'].append({
                    "title" : str(link[0]), "messageURL": self._link_detect(str(link[1])),
                    "picURL": self._link_detect(str(link[2]))
                })
        sign = self.get_sign(Dingtalk.sec_key)
        if target is None:
            url = send_url.format(Dingtalk.access_token, sign[1], sign[0])
            self.log.info(f"[SEND] <- [FeedCard]")
        elif type(target) == Group:
            url = target.send_url
            self.log.info(f"[SEND][{target.name}({int(target)})] <- [FeedCard]")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- [FeedCard]")
        await self._send(url, send_data, header)
    
    @staticmethod
    def _link_detect(link: str) -> str:
        if not str(link).startswith("http"):
            link = "https://" + str(link)
        return link
    
    @staticmethod
    class log:
        def info(*mes):
            logger.info(*mes)
        
        def debug(*mes):
            logger.debug(*mes)
        
        def warning(*mes):
            logger.warning(*mes)
        
        def success(*mes):
            logger.success(*mes)

    @staticmethod
    def get_sign(secure_key: str):
        timestamp = str(round(time.time() * 1000))
        sign_str = timestamp + '\n' + secure_key
        sign = hmac.new(secure_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256).digest()
        sign = base64.b64encode(sign)
        sign = urllib.parse.quote_plus(sign)
        return sign, timestamp
    
    @staticmethod
    async def _send(url, send_data, header=None):
        delog.info(f"发送中:{url}", no=40)
        try:
            resp = await url_res(url, method='POST', data=send_data, header=header, res='json')
            delog.success("发送完成")
        except Exception as err:
            logger.exception(f"端口发送失败！", err)
            return [False]
        else:
            delog.info(resp, no=40)
            if not resp['errcode']:
                delog.success(f"成功!", no=40)
                return [True]
            else:
                logger.error(f"发送失败！错误代码：{resp['errcode']}，错误信息：{resp['errmsg']}")
                return [False, resp['errcode'], resp['errmsg']]
            
    def start(self):
        Channel().set_channel()
        Saya().set_channel()
