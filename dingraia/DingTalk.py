import asyncio
import base64
import hmac
import signal
import socket
import sys
import urllib.parse
import uuid
from functools import reduce
from typing import List, Dict, Coroutine
import os
import importlib.metadata
import aiohttp
import flask
import requests
import websockets
from loguru import logger

from .event import MessageEvent
from .config import Config, Stream
from .element import *
from .event.message import *
from .exceptions import *
from .message.chain import MessageChain
from .message.element import *
from .model import Group, Webhook
from .saya import Channel, Saya
from .signer import sign_js, decrypt
from .tools.debug import delog
from .callback_handler import callback_handler
from .verify import get_token
from .verify import url_res
from .VERSION import VERSION

send_url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}"
channel = Channel.current()
DINGRAIA_ASCII = r"""
 ____  _                       _
|  _ \(_)_ __   __ _ _ __ __ _(_) __ _
| | | | | '_ \ / _` | '__/ _` | |/ _` |
| |_| | | | | | (_| | | | (_| | | (_| |
|____/|_|_| |_|\__, |_|  \__,_|_|\__,_|
               |___/
"""
ANNOUNCEMENT = "See https://dingraia.gitbook.io/dingraia for documents"


def set_num():
    i = 0
    while True:
        i += 1
        yield i


_no = set_num()


class Dingtalk:
    config: Config = None
    loop: asyncio.AbstractEventLoop = None
    _access_token: AccessToken = AccessToken()
    async_tasks = []
    
    @staticmethod
    def __init__(config: Config = None):
        if Dingtalk.config is None:
            Dingtalk.config = config
    
    async def send_message(self, target: Union[Group, OpenConversationId, str, Webhook, None], msg, headers=None):
        """发送普通的文本信息
        
        Args:
            target: 要发送的地址，可以是Group, OpenConversationId, str格式的链接, 或者None发送到测试群
            msg: 要发送的文本
            header: 要包含的请求头

        Returns:
            List(bool)

        """
        # TODO
        if headers is None:
            headers = {}
        send_data = {}
        if isinstance(msg, BaseElement):
            send_data = msg.data if not isinstance(target, OpenConversationId) else msg.template
        elif isinstance(msg, File):
            res = await self.upload_file(msg)
            send_data = msg.template
            send_data['media_id'] = res.mediaId
            target = target.openConversationId
        else:
            if isinstance(target, OpenConversationId):
                send_data = {
                    'msgKey'  : "sampleText",
                    'msgParam': json.dumps({
                        'content': str(msg)
                    })
                }
            else:
                send_data = {
                    "msgtype": "text",
                    "text"   : {
                        "content": str(msg)
                    }
                }
        if isinstance(target, OpenConversationId):
            send_data['robotCode'] = self.config.bot.robotCode
            send_data['openConversationId'] = target.openConversationId
            headers['x-acs-dingtalk-access-token'] = self.access_token
        if isinstance(msg, MessageChain):
            if ats := msg.include(At):
                at = reduce(lambda x, y: x + y, ats)
                send_data["at"] = at.data
        if not target:
            if not self.config.bot.GroupWebhookSecureKey or not self.config.bot.GroupWebhookAccessToken:
                raise ConfigError("Not GroupWebhookSecureKey or GroupWebhookAccessToken provided!")
        if target is None:
            sign = self.get_sign()
            url = send_url.format(sign[2], sign[1], sign[0])
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        elif isinstance(target, Group):
            if time.time() < target.webhook.expired_time:
                url = target.webhook.url
                self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
            else:
                logger.error("群组的Webhook链接已经过期！请检查来源IP是否正确或服务器时钟是否正确")
                return [False, -1]
        elif isinstance(target, Webhook):
            if time.time() < target.expired_time:
                url = target.url
            else:
                logger.error("指定的临时Webhook链接已经过期")
                return
        elif isinstance(target, OpenConversationId):
            url = 'https://api.dingtalk.com/v1.0/robot/groupMessages/send'
            self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        delog.info(send_data, no=60)
        return await self._send(url, send_data, headers)
    
    async def create_group(self,
                           name,
                           templateId,
                           ownerUserId,
                           icon,
                           userIds: list = None,
                           subAdminIds: list = None,
                           showHistory=False,
                           validation=True,
                           searchable=False,
                           UUID: str = str(uuid.uuid1())
                           ):
        userIds = userIds or [ownerUserId]
        userIds = ",".join(userIds)
        subAdminIds = subAdminIds or [ownerUserId]
        subAdminIds = ",".join(subAdminIds)
        url = f"https://oapi.dingtalk.com/topapi/im/chat/scenegroup/create?access_token={self.access_token}"
        data = {
            "title"                          : name,
            "template_id"                    : templateId,
            "owner_user_id"                  : ownerUserId,
            "user_ids"                       : userIds,
            "subadmin_ids"                   : subAdminIds,
            "uuid"                           : UUID,
            "icon"                           : icon,
            "mention_all_authority"          : 1,
            "show_history_type"              : 1 if showHistory else 0,
            "validation_type"                : 1 if validation else 0,
            "searchable"                     : 1 if searchable else 0,
            "chat_banned_type"               : 0,
            "management_type"                : 1,
            "only_admin_can_ding"            : 0,
            "all_members_can_create_mcs_conf": 1,
            "all_members_can_create_calendar": 0,
            "group_email_disabled"           : 0,
            "only_admin_can_set_msg_top"     : 1,
            "add_friend_forbidden"           : 0,
            "group_live_switch"              : 1,
            "members_to_admin_chat"          : 0
        }
        logger.debug(data)
        res = await url_res(url,
                            'POST',
                            json=data, res='json')
        return res
    
    async def get_group(self, openConversationId: str):
        res = await url_res(f'https://oapi.dingtalk.com/topapi/im/chat/scenegroup/get?access_token={self.access_token}',
                            'POST',
                            json={'open_conversation_id': openConversationId}, res='json')
        if res['errcode']:
            if res['errcode'] == 4000003:
                logger.error(f"OpenConversationId 对应的群不是由群模板创建的或没有酷应用支持！")
            return res
        users_res = await url_res(f'https://api.dingtalk.com/v1.0/im/sceneGroups/members/batchQuery',
                                  'POST',
                                  json={'openConversationId': openConversationId, "maxResults": 1000},
                                  header={'x-acs-dingtalk-access-token': self.access_token}, res='json')
        res: dict = res['result']
        res['user_ids'] = users_res['memberUserIds']
        return res
    
    async def mirror_group(self, openConversationId: str):
        raw = await self.get_group(openConversationId)
        res = await self.create_group(raw['title'] + " - 转生", raw['template_id'], raw['owner_staff_id'],
                                      raw['icon'], raw['user_ids'], raw['sub_admin_staff_ids'],
                                      raw['management_options']['show_history_type'],
                                      raw['management_options']['validation_type'],
                                      raw['management_options']['searchable'])
        return res
    
    async def kick(self, openConversationId: Group, memberStaffIds: Union[Member, str, List[Union[Member, str]]]):
        if isinstance(memberStaffIds, list):
            if isinstance(memberStaffIds[0], Member):
                memberStaffIds = [x.staffid for x in memberStaffIds]
        else:
            memberStaffIds = [memberStaffIds]
        memberStaffIds = ','.join(memberStaffIds)
        res = await url_res(
            f'https://oapi.dingtalk.com/topapi/im/chat/scenegroup/member/delete?access_token={self.access_token}',
            'POST',
            json={"open_conversation_id": openConversationId, "user_ids": memberStaffIds}, res='json')
        return res
    
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
    
    async def upload_file(self, file: Union[Path, str, File], access_token: str = None):
        if not isinstance(file, File):
            file_type = str(file)
            file_format = file_type[file_type.rfind('.') + 1:]
            if file_format in ['jpg', 'gif', 'png', 'bmp']:
                file_type = 'image'
                res = Image()
            elif file_format in ['amr', 'mp3', 'wav']:
                file_type = 'voice'
                res = Audio()
            elif file_format in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'pdf', 'rar']:
                file_type = 'file'
                res = File()
            elif file_format == 'mp4':
                file_type = 'video'
                res = Video()
            else:
                raise UploadFileError("Cannot upload the file which is not supported!")
            f = open(file, 'rb')
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
        else:
            size = file.size
            file_type = file.fileType
            f = file.file
            res = file
        if file_type == "image":
            if size > 20 * 1024 * 1024:
                raise UploadFileSizeError("Image file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        elif file_type == "voice":
            if size > 2 * 1024 * 1024:
                raise UploadFileSizeError("Voice file is limited under 2M, but %sM given!" % (size / (1024 ** 2)))
        elif file_type == "video":
            if size > 20 * 1024 * 1024:
                raise UploadFileSizeError("Video file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        else:
            if size > 20 * 1024 * 1024:
                raise UploadFileSizeError("Normal file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        if not access_token:
            access_token = self.access_token
        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://oapi.dingtalk.com/media/upload?access_token={access_token}',
                                    data={'type': file_type, 'media': f}) as resp:
                resp = await resp.json()
        res.mediaId = resp['media_id']
        return res
    
    @property
    def access_token(self):
        if self._access_token.ok:
            return self._access_token.token
        else:
            self._access_token = get_token(self.config.bot.appKey, self.config.bot.appSecret)
            return self._access_token.token
    
    channel = Channel.current()
    callbacks = []
    
    @logger.catch
    async def bcc(self, data: dict):
        delog.info(json.dumps(data, indent=2, ensure_ascii=False), no=50)
        _e = self.DisPackage(data)
        if _e.get('success'):
            _e['send_data'].append(Dingtalk())
            # if isinstance(_e.get('event_type'), BasicMessage):
            #     self.log.info(_e.get('send_data'))
            if not isinstance(_e.get('event_type'), list):
                _e['event_type'] = [_e.get('event_type')]
            for event in _e.get('event_type'):
                if event is not None:
                    await channel.radio(event, *_e.get('send_data'))
        if not _e:
            logger.warning("无法解包！")
            return ""
        return _e.get('returns') or {'err': 0}
    
    @logger.catch
    def DisPackage(self, data: dict) -> dict:
        if "conversationType" in data:
            conversationtype = data.get("conversationType")
            if conversationtype is not None:
                bot = Bot(origin=data)
                group = Group(origin=data)
                member = Member(origin=data)
                if conversationtype == "2":
                    at_users = [userid.get("dingtalkId") for userid in data.get("atUsers") if
                                userid.get("dingtalkId")[userid.get("dingtalkId").rfind('$'):] != bot.origin_id]
                else:
                    at_users = []
                if data.get('msgtype') != 'text':
                    raise ValueError("不支持解析文本以外的消息")
                mes = data.get('text').get('content')
                out_mes = mes
                for _ in out_mes:
                    if mes.startswith(" "):
                        mes = mes[1:]
                    else:
                        break
                # logger.info(at_users)
                message = MessageChain(mes, at=at_users)
                logger.info(message)
                event = MessageEvent(data.get('msgtype'), data.get('msgId'), data.get('isInAtList'), message, group,
                                     member)
                return {
                    "success"   : True,
                    "send_data" : [group, member, message, event, bot],
                    "event_type": [GroupMessage],
                    "returns"   : ""
                }
            else:
                logger.error("不支持的对话类型")
                logger.error(json.dumps(data, indent=2, ensure_ascii=False))
                return {
                    "success"   : False,
                    "send_data" : [],
                    "event_type": [None],
                    "returns"   : ""
                }
        elif "encrypt" in data:
            app = Dingtalk()
            if app.config is not None:
                _e = None
                key = app.config.event_callback.AesKey
                try:
                    _e = decrypt(data.get("encrypt"), key)
                except json.JSONDecodeError:
                    logger.error("无法解密，请检查配置的事件回调密钥")
                    return {
                        "success"   : False,
                        "send_data" : [],
                        "event_type": [None],
                        "returns"   : "400 Bad"
                    }
                except Exception as err:
                    logger.exception(err)
                    return {
                        "success"   : False,
                        "send_data" : [],
                        "event_type": [None],
                        "returns"   : "400 Bad"
                    }
                if _e is None:
                    logger.error("无法解密，请检查配置的事件回调密钥")
                    return {
                        "success"   : False,
                        "send_data" : [],
                        "event_type": [None],
                        "returns"   : ""
                    }
                if type(_e) == dict:
                    logger.info(_e)
                    res = callback_handler(_e, data)
                    return_data = {
                        "success"   : True,
                        "send_data" : [res],
                        "event_type": [res],
                        "returns"   : sign_js(
                            AES_KEY=app.config.event_callback.AesKey,
                            Token=app.config.event_callback.Token,
                            CropID=app.config.event_callback.CropId
                        )
                    }
                else:
                    return {
                        "success"   : False,
                        "send_data" : [],
                        "event_type": None,
                        "returns"   : ""
                    }
                # return_data['event_type'].append(BasicEvent(data, _e))
                return return_data
            return {
                "success"   : False,
                "send_data" : [],
                "event_type": [None],
                "returns"   : ""
            }
        elif 'EventType' in data:
            logger.info(data)
            res = callback_handler(data)
            return {
                "success"   : True,
                "send_data" : [res],
                "event_type": [res],
                "returns"   : ""
            }
        else:
            logger.error(f"未知的回调类型:{json.dumps(data, indent=2, ensure_ascii=False)}")
            return {
                "success"   : False,
                "send_data" : [],
                "event_type": [None],
                "returns"   : ""
            }
    
    @classmethod
    def get_sign(cls, secure_key: str = None):
        if secure_key is None:
            if cls.config:
                secure_key = cls.config.bot.GroupWebhookSecureKey
        if not secure_key:
            raise GroupSecureKeyError("Not GroupSecureKey provided!")
        timestamp = str(round(time.time() * 1000))
        sign_str = timestamp + '\n' + secure_key
        sign = hmac.new(secure_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256).digest()
        sign = base64.b64encode(sign)
        sign = urllib.parse.quote_plus(sign)
        return sign, timestamp, secure_key
    
    @staticmethod
    async def _send(url, send_data, headers=None):
        delog.info(f"发送中:{url}", no=40)
        if url and "http" not in url:
            url = 'http://' + url
        if not url:
            logger.error("Empty send url!")
            return [False]
        try:
            resp = await url_res(url, method='POST', json=send_data, header=headers, res='json')
            delog.success("发送完成")
        except Exception as err:
            logger.exception(f"发送失败！", err)
            return [False]
        else:
            delog.info(resp, no=40)
            if 'errcode' in resp:
                if not resp['errcode']:
                    delog.success(f"Success!", no=40)
                    return [True, resp]
                else:
                    logger.error(f"Failed to send the message!err_code：{resp['errcode']}, err_msg：{resp['errmsg']}")
                    return [False, resp['errcode'], resp['errmsg']]
            else:
                if 'processQueryKey' in resp:
                    delog.success(f"Success!", no=40)
                    return [True, resp]
                else:
                    logger.error(f"Failed to send the message!err_msg：{resp}, send_data: {send_data}")
                    return [False, resp]
    
    @staticmethod
    def _start_topic():
        
        def get_dist_map() -> Dict[str, str]:
            """获取与项目相关的发行字典"""
            dist_map: Dict[str, str] = {}
            for dist in importlib.metadata.distributions():
                name: str = dist.metadata["Name"]
                version: str = dist.metadata["Version"]
                if not name or not version:
                    continue
                if name.startswith(('dingraia', 'websocket', 'asyncio', 'flask')):
                    dist_map[name] = max(version, dist_map.get(name, ""))
            return dist_map
        
        try:
            x, y = os.get_terminal_size().columns, os.get_terminal_size().lines
        except:
            x, y = 80, 20
        _topic = f"[Dingraia v{VERSION}]"
        _topic_len = len(_topic)
        _topic_split = "=" * (((x - _topic_len) // 2) * 2)
        __topic = _topic_split[:len(_topic_split) // 2] + _topic + _topic_split[len(_topic_split) // 2:]
        ver = ""
        if vers := get_dist_map():
            for k, v in vers.items():
                ver += f"\n<magenta>{k}</>: <blue>{v}</>"
        announcement =  ""
        if ANNOUNCEMENT:
            announcement = "Announcements:\n" + ANNOUNCEMENT
        logger.opt(colors=True).info("\n" * 5 + __topic + DINGRAIA_ASCII + f"\n{ver}\n\n" + announcement + "\n")
        logger.info("Preparing loading...")
    
    def start(self, flask_app: flask.Flask = None, **kwargs):
        """
        
        Args:
            flask_app: 你的 Flask app 对象
            **kwargs: 传递给 Flask 的参数

        Returns:
            None

        """
        Channel().set_channel()
        Saya().set_channel()
        self._start_topic()
        if self.config.stream:
            logger.info(f"Loading {len(self.config.stream)} stream task{'s' if len(self.config.stream) > 1 else ''}")
            for stream in self.config.stream:
                self.create_stream(stream)
            self.loop.create_task(self.stop(True))
        if flask_app:
            from flask import request, jsonify
            
            @logger.catch
            @flask_app.route('/', methods=["POST"])
            async def receive_data():
                res = await self.bcc(request.json)
                if res:
                    if isinstance(res, dict):
                        return jsonify(res)
                    else:
                        return res
            
            flask_app.run(**kwargs)
        else:
            self.loop.run_forever()
    
    def create_stream(self, stream: Stream):
        
        WS_CONNECT_URL = "https://api.dingtalk.com/v1.0/gateway/connections/open"
        
        def get_host_ip():
            ip = ""
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
            finally:
                s.close()
                return ip
        
        async def open_connection(task_name: str):
            logger.info(f'[{task_name}] Requesting stream')
            request_headers = {
                'Content-Type': 'application/json',
                'Accept'      : 'application/json',
                'User-Agent'  : f'Dingraia/{VERSION} (+https://github.com/MeiHuaGuangShuo/Dingraia)'
            }
            request_body = json.dumps({
                'clientId'     : stream.AppKey,
                'clientSecret' : stream.AppSecret,
                'subscriptions': [
                    {'type': 'EVENT', 'topic': '*'},
                    {'type': 'CALLBACK', 'topic': '/v1.0/im/bot/messages/get'},
                    {'type': 'CALLBACK', 'topic': '/v1.0/im/bot/messages/delegate'},
                    {'type': 'CALLBACK', 'topic': '/v1.0/card/instances/callback'},
                ],
                'ua'           : f'Dingraia/{VERSION}',
                'localIp'      : get_host_ip()
            }).encode('utf-8')
            response = requests.post(WS_CONNECT_URL,
                                     headers=request_headers,
                                     data=request_body)
            http_body = response.json()
            if not response.ok:
                logger.error(f"[{task_name}] Open connection failed, Reason: {response.reason}, Response: {http_body}")
                if response.status_code == 401:
                    logger.warning(f"[{task_name}] The AppKey or AppSecret maybe inaccurate")
                    await self.stop()

                    return False
                return None
            return response.json()
        
        async def route_message(json_message, websocket: websockets.WebSocketServer, task_name: str):
            result = ''
            try:
                msg_type = json_message.get('type', '')
                headers = json_message.get('headers', {})
                data = json.loads(json_message.get('data', {}))
                topic = headers.get('topic', '')
                if msg_type == 'SYSTEM':
                    if topic == 'disconnect':
                        result = 'disconnect'
                        logger.warning(
                            f"[{task_name}] [System] Client was offered to disconnect, message: {json_message}")
                    else:
                        logger.info(f"[{task_name}] [System] topic: {topic}")
                    headers['topic'] = "pong"
                    await websocket.send(json.dumps({
                        'code'   : 200,
                        'headers': headers,
                        'message': 'OK',
                        'data'   : json_message['data'],
                    }))
                else:
                    logger.debug(json_message)
                    if 'eventType' in headers:
                        data['EventType'] = headers['eventType']
                    await self.bcc(data)
            except Exception as err:
                logger.exception(f"[{task_name}] Error happened while handing the message", err)
            return result
        
        async def main_stream(task_name: str):
            while True:
                connection = await open_connection(task_name)
                
                if not connection:
                    if connection == None:
                        logger.error(f'[{task_name}] Open websocket connection failed')
                        logger.warning(f"[{task_name}] Websocket Connection will be reconnected after 5 seconds")
                        time.sleep(5)
                        logger.warning(f"[{task_name}] Reconnecting...")
                        continue
                    if connection == False:
                        logger.error(f'[{task_name}] Request connection failed!')
                    return
                # logger.info(f'[{task_name}] Connection accessed')
                
                uri = '%s?ticket=%s' % (connection['endpoint'], urllib.parse.quote_plus(connection['ticket']))
                async with websockets.connect(uri) as websocket:
                    logger.success(f"[{task_name}] Websocket connected")
                    async for raw_message in websocket:
                        json_message = json.loads(raw_message)
                        # logger.debug(json_message)
                        route_result = await route_message(json_message, websocket, task_name)
                        if route_result == "disconnect":
                            break
                    # self.websocket.close()
            return
        
        try:
            self.loop = asyncio.get_event_loop()
            no = next(_no)
            name = f"#{no} Main Stream"
            self.async_tasks.append(self.loop.create_task(main_stream(name), name=name))
            logger.info(f"Create Stream Task - {name}")
        except asyncio.exceptions.CancelledError:
            logger.warning("Program forced to be exit!")
            sys.exit(0)
    
    def create_task(self, coroutine: Coroutine, name: str = "Task"):
        task = self.loop.create_task(coroutine)
        task.set_name(name := (f"#{next(_no)} " + name))
        self.async_tasks.append(task)
        logger.info(f"Create async task [{name}]")
        return task, name
    
    async def stop(self, waitForSignal=False):
        if waitForSignal:
            while not exit_signal:
                await asyncio.sleep(0.5)
        else:
            logger.warning("Stop signal was called!")
        self.log.info("Stopping task loop")
        tasks = asyncio.all_tasks()
        names = ', '.join([x.get_name() for x in self.async_tasks])
        logger.info(f"Cancelling async tasks: [{names}]")
        if tasks:
            for task in tasks:
                is_cancelled = task.cancel()
                name = task.get_name()
                if task in self.async_tasks:
                    if not is_cancelled:
                        logger.error(f"Task [{name}] canceled failed!")
                    else:
                        logger.success(f"Task [{name}] canceled successfully")
        self.loop.stop()


exit_signal = False


def exit(signum, frame):
    global exit_signal
    logger.warning(f"Received Signal {signum}")
    exit_signal = True


signal.signal(signal.SIGINT, exit)
signal.signal(signal.SIGTERM, exit)
