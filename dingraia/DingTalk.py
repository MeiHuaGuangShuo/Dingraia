import asyncio
import base64
import collections
import hmac
import importlib.metadata
import inspect
import signal
import socket
import urllib.parse
import uuid
from functools import reduce
from typing import Dict, Coroutine, Literal

import aiohttp
import websockets
from aiohttp import ClientSession, ClientResponse
from .log import logger
from .VERSION import VERSION
from .callback_handler import callback_handler
from .config import Config, Stream
from .element import *
from .event import MessageEvent
from .event.event import *
from .event.message import *
from .exceptions import *
from .message.chain import MessageChain
from .message.element import *
from .model import Group, Webhook
from .saya import Channel, Saya
from .signer import sign_js, decrypt
from .tools.debug import delog
from .verify import get_token
from .verify import url_res
from .vars import *
from .cache import cache

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

try:
    is_debug = os.path.exists("dingraia_debug.mode")
except:
    is_debug = False


def set_num():
    i = 0
    while True:
        i += 1
        yield i


_no = set_num()
err_reason = ErrorReason()


class Dingtalk:
    WS_CONNECT_HOST = "https://api.dingtalk.com"
    WS_CONNECT_URL = WS_CONNECT_HOST + "/v1.0/gateway/connections/open"
    clientSession: ClientSession = None
    config: Config = None
    _loop: asyncio.AbstractEventLoop = None
    _access_token: AccessToken = None
    api_request: "Dingtalk._api_request" = None
    oapi_request: "Dingtalk._oapi_request" = None
    async_tasks = []
    stream_checker = {}
    stream_connect = None
    """用于检测重复的回调, 键为任务名, 值为容纳50个StreamID的列表"""
    
    def __init__(self, config: Config = None):
        if Dingtalk.config is None:
            Dingtalk.config = config
    
    async def send_message(self, target: Union[Group, Member, OpenConversationId, str, Webhook, None], msg,
                           headers=None):
        """发送普通的文本信息
        
        Args:
            target: 要发送的地址，可以是Group, OpenConversationId, str格式的链接, 或者None发送到测试群
            msg: 要发送的文本
            headers: 要包含的请求头

        Returns:
            Response

        """
        # TODO
        if headers is None:
            headers = {}
        send_data = {}
        response = Response()
        response.recallType = f"Unsupported recall target {type(target).__name__}"
        if isinstance(target, str):
            if target.startswith('cid'):
                target = OpenConversationId(target)
        if isinstance(msg, BaseElement):
            if not isinstance(target, OpenConversationId) and not isinstance(target, Member):
                send_data = msg.data
            else:
                send_data = msg.template
        elif isinstance(msg, File):
            if not msg.mediaId:
                res = await self.upload_file(msg)
                send_data = msg.template
                send_data['media_id'] = res.mediaId
            else:
                send_data['media_id'] = msg.mediaId
            if isinstance(target, Group):
                target = target.openConversationId
        else:
            if isinstance(target, OpenConversationId) or isinstance(target, Member):
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
            
            send_data['robotCode'] = self.config.bot.robotCode
            send_data['openConversationId'] = str(target.openConversationId)
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
            response.recall_type = "url"
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        elif isinstance(target, Group):
            if time.time() < target.webhook.expired_time:
                url = target.webhook.url
                response.recall_type = "group webhook"
                self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
            else:
                logger.error("群组的Webhook链接已经过期！请检查来源IP是否正确或服务器时钟是否正确")
                return [False, -1]
        elif isinstance(target, Member):
            url = f"https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend"
            headers['x-acs-dingtalk-access-token'] = self.access_token
            self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
            send_data['userIds'] = [target.staffid]
            send_data['robotCode'] = self.config.bot.robotCode
            response.recallType = "personal"
        elif isinstance(target, Webhook):
            if time.time() < target.expired_time:
                url = target.url
                response.recall_type = "webhook"
            else:
                logger.error("指定的临时Webhook链接已经过期")
                return
        elif isinstance(target, OpenConversationId):
            url = 'https://api.dingtalk.com/v1.0/robot/groupMessages/send'
            response.recallType = "group"
            response.recallOpenConversationId = target
            self.log.info(f"[SEND][{target.name}({int(target)})] <- {repr(str(msg))[1:-1]}")
        else:
            url = str(target)
            self.log.info(f"[SEND] <- {repr(str(msg))[1:-1]}")
        delog.info(send_data, no=60)
        if url and "http" not in url:
            logger.error(f"Wrong send url [{url}]!")
            response.ok = False
            response.text = ""
            response.url = url
            response.recall_type = "Not completed request"
            return response
        response.sendData = send_data
        try:
            if 'api' in url:
                resp = await self.api_request.post(url, json=send_data, headers=headers)
            else:
                resp = await url_res(url, 'POST', json=send_data, headers=headers, res='raw')
            response.ok = resp.ok
            response.text = await resp.text()
            response.url = url
            delog.success("发送完成")
        except Exception as err:
            logger.exception(f"发送失败！", err)
            response.ok = False
            response.text = ""
            response.url = url
            response.recall_type = "Not completed request"
            return response
        else:
            delog.info(response.text, no=40)
            if not response.ok:
                try:
                    res = response.json()
                    errCode = res.get('errcode', res.get('code', -1))
                except:
                    errCode = -1
                raise err_reason[errCode](response.text)
            else:
                delog.success(f"Success!", no=40)
            return response
    
    def sendMessage(self, target: Union[Group, Member, OpenConversationId, str, Webhook, None], msg,
                    headers=None):
        """发送普通的文本信息, 对于异步函数send_message的同步包装
        
        Args:
            target: 要发送的地址，可以是Group, OpenConversationId, str格式的链接, 或者None发送到测试群
            msg: 要发送的文本
            headers: 要包含的请求头

        Returns:
            Response

        """
        return asyncio.run_coroutine_threadsafe(self.send_message(target, msg, headers), self.loop).result()
    
    async def recall_message(
            self,
            message: Response = None,
            *,
            openConversationId: Union[OpenConversationId, Group, str] = None,
            processQueryKeys: Union[str, List[str]] = None,
            robotCode: str = None,
            access_token: str = None,
            inThreadTime: int = 0
    ):
        """撤回一条消息
        
        Args:
            message: 通过send_message发送消息返回的对象
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            processQueryKeys: 消息的加密ID
            robotCode: 机器人的机器码
            access_token: 企业的AccessToken
            inThreadTime: 是否不等待撤回

        Returns:
            text

        """
        
        async def _run(_message, _openConversationId, _processQueryKeys, _robotCode, _access_token, _inThreadTime):
            _access_token = _access_token or self.access_token
            if message:
                _processQueryKeys = message.json['processQueryKey']
                _openConversationId = message.recallOpenConversationId
            _processQueryKeys = [str(x) for x in
                                 (_processQueryKeys if isinstance(_processQueryKeys, list) else [_processQueryKeys])]
            if isinstance(openConversationId, Group):
                _openConversationId = _openConversationId.conversationId
            if _openConversationId is not None:
                _openConversationId = str(_openConversationId)
            if _robotCode is None:
                _robotCode = self.config.bot.robotCode
            post_data = {
                "processQueryKeys": _processQueryKeys,
                "robotCode"       : _robotCode
            }
            url = "/v1.0/robot/otoMessages/batchRecall"
            if _openConversationId:
                url = "/v1.0/robot/groupMessages/recall"
                post_data['openConversationId'] = _openConversationId
            await asyncio.sleep(_inThreadTime)
            res = await self.api_request.post(url, json=post_data)
            return await res.json()
        
        if message.recallType not in ['group', 'personal']:
            raise UnsupportedRecallType(f"The recall type '{message.recallType}' is not supported for recall")
        if not inThreadTime:
            return await _run(message, openConversationId, processQueryKeys, robotCode, access_token, inThreadTime)
        else:
            return self.loop.create_task(
                _run(message, openConversationId, processQueryKeys, robotCode, access_token, inThreadTime))
    
    async def _send_card(
            self,
            cardTemplateId,
            outTrackId,
            cardData,
            openSpaceId,
            supportForward: bool = False,
            notificationOff: bool = False,
            alertContent: str = "你收到了一个卡片消息",
            lastContent: str = "卡片",
    ):
        exam = {
            "cardTemplateId"       : "b4fdsu2119f-9945-4e13-9989-747da19e3bc7",
            "outTrackId"           : "example_out_track_id",
            "callbackRouteKey"     : "example_route_key",
            "cardData"             : {},
            "privateData"          : {},
            "imGroupOpenSpaceModel": {
                "supportForward" : supportForward,
                "lastMessageI18n": {
                    "key": lastContent
                },
                "notification"   : {
                    "alertContent"   : alertContent,
                    "notificationOff": notificationOff
                }
            },
            "imRobotOpenSpaceModel": {
                "supportForward" : supportForward,
                "lastMessageI18n": {
                    "key": lastContent
                },
                "notification"   : {
                    "alertContent"   : alertContent,
                    "notificationOff": notificationOff
                }
            },
            "openSpaceId"          : "dtv1.card//im_group.cidp4Gh*******VCQ==;im_robot.manager****67",
            "docOpenDeliverModel"  : {
                "userId": "example_user_id"
            },
            "userIdType"           : 1,
            "callbackType"         : "STREAM"
        }
        raise ValueError("未完成")
    
    async def send_card(
            self,
            target: Union[OpenConversationId, Group, Member],
            cardData: dict,
            outTrackId: str = str(uuid.uuid1()),
    ) -> str:
        """
        
        Args:
            target: 发送的目标地址
            cardData: 卡片内容
            outTrackId: 自定义追溯ID, 默认使用UUID1生成

        Returns:
            str: outTrackId

        """
        resp = await self.api_request.post('/v1.0/card/instances', json=cardData)
        if not resp.ok:
            raise DingtalkAPIError(f"Error while create the card.Code={resp.status} text={await resp.text()}")
        body = {
            "outTrackId": outTrackId,
            "userIdType": 1,
        }
        if isinstance(target, Member):
            body['openSpaceId'] = f"dtv1.card//IM_ROBOT.{target.staffid}"
            cardData["imRobotOpenDeliverModel"] = {"spaceType": "IM_ROBOT"}
        else:
            if isinstance(target, Group):
                target = target.openConversationId
            openConversationId = str(target)
            body['openSpaceId'] = f"dtv1.card//IM_GROUP.{openConversationId}"
            body["imGroupOpenDeliverModel"] = {"robotCode": self.config.bot.appKey}
        resp = await self.api_request.post('/v1.0/card/instances/deliver', json=body)
        if not resp.ok:
            raise DingtalkAPIError(f"Error while deliver the card.Code={resp.status} text={await resp.text()}")
        return outTrackId
    
    async def send_markdown_card(
            self,
            target: Union[OpenConversationId, Group, Member],
            markdown: Markdown,
            logo: Union[File, str] = "@lALPDfJ6V_FPDmvNAfTNAfQ",
            outTrackId: str = str(uuid.uuid1()),
            supportForward: bool = False,
    ):
        """
        
        Args:
            target: 发送的目标
            markdown: Markdown对象, title在其中指定
            logo: Markdown标头的logo
            outTrackId: 自定义追溯ID, 默认使用UUID1生成
            supportForward: 是否支持折叠

        Returns:
            str: outTrackId

        """
        if isinstance(logo, File):
            if not logo.mediaId:
                logo = await self.upload_file(logo)
            logo = logo.mediaId
        if isinstance(logo, str):
            if not logo.startswith("@"):
                raise ValueError(f"logo {logo} is not a valid value!")
        else:
            raise ValueError(f"logo {logo} is not a valid value!")
        data = {
            "cardTemplateId"       : "589420e2-c1e2-46ef-a5ed-b8728e654da9.schema",
            "outTrackId"           : outTrackId,
            "cardData"             : {
                "cardParamMap": {
                    "markdown": markdown.text,
                    "title"   : markdown.title,
                    "logo"    : logo
                }
            },
            "imGroupOpenSpaceModel": {"supportForward": supportForward},
            "imRobotOpenSpaceModel": {"supportForward": supportForward},
            "callbackType"         : "STREAM"
        }
        return await self.send_card(target=target, cardData=data, outTrackId=outTrackId)
    
    async def update_card(self, outTrackId, cardParamData):
        if isinstance(cardParamData, Markdown):
            cardParamData = {
                "markdown": cardParamData.text,
                "title"   : cardParamData.title
            }
        body = {
            "outTrackId": outTrackId,
            "cardData"  : {
                "cardParamMap": cardParamData
            }
        }
        resp = await self.api_request.put('/v1.0/card/instances', json=body)
        if not resp.ok:
            raise DingtalkAPIError(f"Error while update the card.Code={resp.status} text={await resp.text()}")
        return await resp.json()
    
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
                           UUID: str = str(uuid.uuid1()),
                           access_token: str = None
                           ):
        userIds = userIds or [ownerUserId]
        userIds = [str(x) for x in userIds]
        userIds = ",".join(userIds)
        subAdminIds = subAdminIds or [ownerUserId]
        subAdminIds = [str(x) for x in subAdminIds]
        subAdminIds = ",".join(subAdminIds)
        access_token = access_token or self.access_token
        url = f"https://oapi.dingtalk.com/topapi/im/chat/scenegroup/create?access_token={access_token}"
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
        res = await url_res(url,
                            'POST',
                            json=data, res='json')
        if not res['success']:
            logger.error(f"Cannot create the group!Response: {json.dumps(res, ensure_ascii=False, indent=4)}")
        return res
    
    async def get_group(self, openConversationId: Union[OpenConversationId, Group, str], access_token: str = None):
        """获取场景群信息, `2` API 调用量
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            access_token: 企业的AccessToken

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        if access_token:
            res = await url_res(f'https://oapi.dingtalk.com/topapi/im/chat/scenegroup/get?access_token={access_token}',
                                'POST',
                                json={'open_conversation_id': openConversationId}, res='json')
        else:
            resp = await self.oapi_request.post("/topapi/im/chat/scenegroup/get",
                                                json={'open_conversation_id': openConversationId})
            res = await resp.json()
        if res['errcode']:
            if res['errcode'] == 4000003:
                logger.error(f"OpenConversationId 对应的群不是由群模板创建的或没有酷应用支持！")
            res['success'] = False
            return res
        if access_token:
            users_res = await url_res(
                f'https://oapi.dingtalk.com/topapi/im/chat/scenegroup/member/get?access_token={access_token}',
                'POST',
                json={'openConversationId': openConversationId, "maxResults": 1000},
                res='json')
        else:
            resp = await self.oapi_request.post('/topapi/im/chat/scenegroup/member/get',
                                                json={'open_conversation_id': openConversationId, "size": 1000,
                                                      "cursor"              : 0})
            users_res = await resp.json()
            users_res = users_res.get('result', {})
        res: dict = res['result']
        res['user_ids'] = users_res.get('member_user_ids')
        res['staff_id_nick_map'] = users_res.get('staff_id_nick_map')
        res['success'] = True
        return res
    
    async def get_depts(self, deptId: str = "1", access_token: str = None):
        """获取部门ID
        
        Args:
            deptId: 部门ID. 根部门为 1
            access_token: 企业的AccessToken

        Returns:

        """
        access_token = access_token or self.access_token
        if access_token:
            url = f"https://oapi.dingtalk.com/topapi/v2/department/listsub?access_token={access_token}"
            res = await url_res(url, 'POST', json={'dept_id': deptId}, res='json')
        else:
            resp = await self.oapi_request.post('/topapi/v2/department/listsub', json={'dept_id': deptId})
            res = await resp.json()
        return res
    
    async def get_user(self, userStaffId: Union[Member, str], language: str = "zh_CN", access_token: str = None):
        """获取用户详细信息
        
        Args:
            userStaffId: 用户的StaffID
            language: 语言. 默认zh-CN

        Returns:

        """
        userStaffId = self._staffId2str(userStaffId)
        access_token = access_token or self.access_token
        res = await url_res(
            f'https://oapi.dingtalk.com/topapi/v2/user/get?access_token={access_token}',
            'POST',
            json={"language": language, "userid": userStaffId}, res='json')
        return res
    
    async def remove_user(self, userStaffId: Union[Member, str], access_token: str = None):
        """从组织中直接移除用户
        
        Args:
            userStaffId: 用户的StaffID
            access_token: 组织的AccessToken

        Returns:

        """
        userStaffId = self._staffId2str(userStaffId)
        access_token = access_token or self.access_token
        res = await url_res(
            f'https://oapi.dingtalk.com/topapi/v2/user/delete?access_token={access_token}',
            'POST',
            json={"userid": userStaffId}, res='json')
        return res
    
    async def create_user(
            self,
            name: str,
            mobilePhone: Union[str, int],
            deptIds: Union[str, List[str]],
            userId: str = None,
            hidePhone: bool = None,
            jobNumber: str = None,
            positionName: str = None,
            personalEmail: str = None,
            organizeEmail: str = None,
            organizeEmailType: Literal['base', 'profession'] = None,
            workPlace: str = None,
            remark: str = None,
            extension: str = None,
            isSenior: bool = None,
            managerUserId: str = None,
            loginEmail: str = None
    ):
        """创建一名用户
        
        Args:
            name: 用户真实名称
            mobilePhone: 用户手机号. 企业内必须唯一
            deptIds: 用户所属部门ID
            userId: 用户的唯一userId. 企业内必须唯一, 不填可自动生成
            hidePhone: 是否隐藏该用户手机号
            jobNumber: 用户工号
            positionName: 用户职位名称
            personalEmail: 用户个人邮箱
            organizeEmail: 用户公司邮箱
            organizeEmailType: 用户公司邮箱类型
            workPlace: 工作地点
            remark: 标记
            extension: 额外信息
            isSenior: 是否开启高管模式
            managerUserId: 管理此用户的经理的UserID
            loginEmail: 登录邮箱

        Returns:

        """
        deptIds = ','.join([str(x) for x in (deptIds if isinstance(deptIds, list) else [deptIds])])
        data = {
            "name"        : name,
            "mobile"      : mobilePhone,
            "telephone"   : mobilePhone,
            "dept_id_list": deptIds,
        }
        if userId:
            data['userid'] = userId
        if positionName:
            data['title'] = positionName
        if jobNumber:
            data['job_number'] = jobNumber
        if personalEmail:
            data['email'] = personalEmail
        if organizeEmail:
            data['org_email'] = organizeEmail
        if organizeEmailType:
            data['org_email_type'] = organizeEmailType
        if hidePhone:
            data['hide_mobile'] = hidePhone
        if remark:
            data['remark'] = remark
        if workPlace:
            data['work_place'] = workPlace
        if extension:
            data['extension'] = extension
        if isSenior:
            data['senior_mode'] = isSenior
        if managerUserId:
            data['manager_userid'] = managerUserId
        if loginEmail:
            data['login_email'] = loginEmail
        resp = await self.oapi_request.post('/topapi/v2/user/create', json=data)
        res = await resp.json()
        return res
    
    async def update_user(
            self,
            userId,
            name: str = None,
            hide_mobile: bool = None,
            telephone: str = None,
            job_number: str = None,
            manager_userid: str = None,
            title: str = None,
            email: str = None,
            org_email: str = None,
            work_place: str = None,
            remark: str = None,
            dept_id_list: Union[list, int, str] = None,
            dept_title_list: dict = None,
            dept_order_list: dict = None,
            extension: dict = None,
            senior_mode: bool = None,
            hired_date: int = None,
            language: Literal["zh_CN", "en_US"] = None,
            force_update_fields: List[str] = None
    ):
        data = {"userid": self._staffId2str(userId)}
        if name:
            data['name'] = name
        if hide_mobile is not None:
            data['hide_mobile'] = hide_mobile
        if telephone:
            data['telephone'] = str(telephone)
        if job_number:
            data['job_number'] = str(job_number)
        if manager_userid:
            data['manager_userid'] = str(manager_userid)
        if title:
            data['title'] = str(title)
        if email:
            data['email'] = str(email)
        if org_email:
            data['org_email'] = str(org_email)
        if work_place:
            data['work_place'] = str(work_place)
        if remark:
            data['remark'] = str(remark)
        if dept_id_list:
            if not isinstance(dept_id_list, list):
                dept_id_list = [dept_id_list]
            data['dept_id_list'] = ",".join([str(x) for x in dept_id_list])
        if dept_title_list:
            data['dept_title_list'] = dept_title_list
        if dept_order_list:
            data['dept_order_list'] = dept_order_list
        if extension:
            data['extension'] = extension
        if senior_mode is not None:
            data['senior_mode'] = senior_mode
        if hired_date:
            data['hired_date'] = int(hired_date)
        if language:
            data['language'] = language
        if force_update_fields:
            data['force_update_fields'] = ",".join([str(x) for x in force_update_fields])
        resp = await self.oapi_request.post('/topapi/v2/user/update', json=data)
        res = await resp.json()
        return res
    
    async def mirror_group(self, openConversationId: Union[OpenConversationId, Group, str]):
        """复制群信息和群成员到一个新群. 群必须是场景群
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        raw = await self.get_group(openConversationId)
        if raw['title'].endswith('_mirror'):
            title = raw['title'][:-7]
        else:
            title = raw['title']
        userIds = raw['user_ids']
        adminUserIds = raw['sub_admin_staff_ids']
        if raw['success']:
            res = await self.create_group(title + " - 转生", raw['template_id'], raw['owner_staff_id'],
                                          raw['icon'], raw['owner_staff_id'], raw['owner_staff_id'],
                                          raw['management_options']['show_history_type'],
                                          raw['management_options']['validation_type'],
                                          raw['management_options']['searchable'])
            new_openConversationId = OpenConversationId(res['result']['open_conversation_id'])
            if res['success']:
                times = 0
                while times < 3:
                    res = await self.get_group(new_openConversationId)
                    if res.get('success'):
                        break
                    await asyncio.sleep(1)
                else:
                    logger.error("获取群信息失败超过 3 次!")
                    return {'success': False}
                invite_url = res['group_url']
                await self.send_message(OpenConversationId(openConversationId), MessageChain("新群链接: ", invite_url))
                res = await self.add_member(new_openConversationId, userIds)
            if not res['success']:
                logger.error(
                    f"Error while adding the member! Response: {json.dumps(res, indent=4, ensure_ascii=False)}")
            res = await self.set_admin(new_openConversationId, adminUserIds)
            if not res['success']:
                logger.error(
                    f"Error while setting the admin(s)! Response: {json.dumps(res, indent=4, ensure_ascii=False)}")
        else:
            res = raw
        return res
    
    async def update_group(
            self,
            openConversationId: Union[OpenConversationId, Group, str],
            *,
            title: str = None,
            owner_user_id: str = None,
            icon: Union[File, str] = None,
            mention_all_authority: bool = None,
            show_history_type: bool = None,
            validation_type: bool = None,
            searchable: bool = None,
            chat_banned_type: bool = None,
            management_type: bool = None,
            only_admin_can_ding: bool = None,
            all_members_can_create_mcs_conf: bool = None,
            all_members_can_create_calendar: bool = None,
            group_email_disabled: bool = None,
            only_admin_can_set_msg_top: bool = None,
            add_friend_forbidden: bool = None,
            group_live_switch: bool = None,
            members_to_admin_chat: bool = None,
            plugin_customize_verify: bool = None,
            access_token: str = None):
        """
        
        Args:
            openConversationId: 群ID
            title: 群标题
            owner_user_id: 群主的UserID
            icon: 群图标
            mention_all_authority: @all权限 0:所有人 1:群主
            show_history_type: 新成员是否可查看聊天历史消息
            validation_type: 入群验证
            searchable: 群是否可被搜索
            chat_banned_type: 是否全员禁言
            management_type: 管理类型 0:所有人 1:群主
            only_admin_can_ding: 群内DING权限 0:所有人 1:群主
            all_members_can_create_mcs_conf: 群会议权限 0:群主和管理员 1:所有人
            all_members_can_create_calendar: 群日历设置项，群内非好友/同事的成员是否可相互发起钉钉日程 0:非好友不可 1:任何人
            group_email_disabled: 是否禁止发送群邮件
            only_admin_can_set_msg_top: 置顶消息权限 0:所有人 1:群主
            add_friend_forbidden: 群成员私聊权限 0:所有人 1:仅管理员
            group_live_switch: 群直播权限 0:群主与管理 1:所有人
            members_to_admin_chat: 是否禁止非管理员向管理员发起单聊 0:允许 1:禁止
            plugin_customize_verify: 自定义群插件是否需要群主和管理员审批 0:不需要 1:需要
            access_token:

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        data = {"open_conversation_id": openConversationId}
        if title is not None:
            data['title'] = str(title)
        if owner_user_id is not None:
            data['owner_user_id'] = self._staffId2str(owner_user_id)
        if icon is not None:
            data['icon'] = self._file2mediaId(icon)
        if mention_all_authority is not None:
            data['mention_all_authority'] = 1 if mention_all_authority else 0
        if show_history_type is not None:
            data['show_history_type'] = 1 if show_history_type else 0
        if validation_type is not None:
            data['validation_type'] = 1 if validation_type else 0
        if searchable is not None:
            data['searchable'] = 1 if searchable else 0
        if chat_banned_type is not None:
            data['chat_banned_type'] = 1 if chat_banned_type else 0
        if management_type is not None:
            data['management_type'] = 1 if management_type else 0
        if only_admin_can_ding is not None:
            data['only_admin_can_ding'] = 1 if only_admin_can_ding else 0
        if all_members_can_create_mcs_conf is not None:
            data['all_members_can_create_mcs_conf'] = 1 if all_members_can_create_mcs_conf else 0
        if all_members_can_create_calendar is not None:
            data['all_members_can_create_calendar'] = 1 if all_members_can_create_calendar else 0
        if group_email_disabled is not None:
            data['group_email_disabled'] = 1 if group_email_disabled else 0
        if only_admin_can_set_msg_top is not None:
            data['only_admin_can_set_msg_top'] = 1 if only_admin_can_set_msg_top else 0
        if add_friend_forbidden is not None:
            data['add_friend_forbidden'] = 1 if add_friend_forbidden else 0
        if group_live_switch is not None:
            data['group_live_switch'] = 1 if group_live_switch else 0
        if members_to_admin_chat is not None:
            data['members_to_admin_chat'] = 1 if members_to_admin_chat else 0
        if plugin_customize_verify is not None:
            data['plugin_customize_verify'] = 1 if plugin_customize_verify else 0
        if access_token:
            res = await url_res(
                f'https://oapi.dingtalk.com/topapi/im/chat/scenegroup/update?access_token={access_token}',
                'POST',
                json=data, res='json')
        else:
            resp = await self.oapi_request.post("/topapi/im/chat/scenegroup/update",
                                                json=data)
            res = await resp.json()
        return res
    
    async def change_group_title(self, openConversationId: Union[OpenConversationId, Group, str], title: str):
        """
        
        Args:
            openConversationId:
            title:

        Returns:

        """
        return await self.update_group(openConversationId, title=title)
    
    async def change_group_owner(self, openConversationId: Union[OpenConversationId, Group, str], userStaffId: Union[Member, str]):
        """
        
        Args:
            openConversationId:
            userStaffId:

        Returns:

        """
        return await self.update_group(openConversationId, owner_user_id=userStaffId)
    
    async def mute_all(self, openConversationId: Union[OpenConversationId, Group, str]):
        return await self.update_group(openConversationId, chat_banned_type=True)
    
    async def unmute_all(self, openConversationId: Union[OpenConversationId, Group, str]):
        return await self.update_group(openConversationId, chat_banned_type=False)
    
    async def kick_member(self, openConversationId: Union[OpenConversationId, Group, str],
                          memberStaffIds: Union[Member, str, List[Union[Member, str]]]):
        """从群组中踢出一名成员. 群组必须是场景群
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            memberStaffIds: 成员的StaffID

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        memberStaffIds = self._staffId2list(memberStaffIds)
        memberStaffIds = ','.join(memberStaffIds)
        resp = await self.oapi_request.post('/topapi/im/chat/scenegroup/member/delete',
                                            json={"open_conversation_id": openConversationId,
                                                  "user_ids"            : memberStaffIds})
        res = await resp.json()
        return res
    
    async def add_member(self, openConversationId: Union[OpenConversationId, Group, str],
                         memberStaffIds: Union[Member, str, List[Union[Member, str]]]):
        """添加一个成员到群组. 群组必须是场景群
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            memberStaffIds: 成员的StaffID

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        memberStaffIds = self._staffId2list(memberStaffIds)
        memberStaffIds = ','.join(memberStaffIds)
        resp = await self.oapi_request.post('/topapi/im/chat/scenegroup/member/add',
                                            json={"open_conversation_id": openConversationId,
                                                  "user_ids"            : memberStaffIds})
        res = await resp.json()
        return res
    
    async def set_admin(self, openConversationId: Union[OpenConversationId, Group, str],
                        memberStaffIds: Union[Member, str, List[Union[Member, str]]], set_admin: bool = True):
        """设置一个成员是否为管理员. 群组必须是场景群
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            memberStaffIds: 成员的StaffID
            set_admin: 是否设置为群组管理员

        Returns:

        """
        openConversationId = self._openConversationId2str(openConversationId)
        memberStaffIds = self._staffId2list(memberStaffIds)
        resp = await self.api_request.put('/v1.0/im/sceneGroups/subAdmins',
                                          json={"openConversationId": openConversationId, "userIds": memberStaffIds,
                                                'role'              : 2 if set_admin else 3})
        res = await resp.json()
        return res
    
    async def mute_member(
            self,
            openConversationId: Union[OpenConversationId, Group, str],
            memberStaffIds: Union[Member, str, List[Union[Member, str]]],
            muteTime: int = 0
    ):
        """禁言一个成员
        
        Args:
            openConversationId: 群对话ID, 可以是OpenConversationId或Group对象
            memberStaffIds: 成员的StaffID
            muteTime: 禁言时长, 单位为秒, 值为0则解除禁言

        Returns:

        """
        url = f"https://api.dingtalk.com/v1.0/im/sceneGroups/muteMembers/set"
        memberStaffIds = [str(x) for x in (memberStaffIds if isinstance(memberStaffIds, list) else [memberStaffIds])]
        openConversationId = self._openConversationId2str(openConversationId)
        memberStaffIds = self._staffId2list(memberStaffIds)
        resp = await self.api_request.post('/v1.0/im/sceneGroups/muteMembers/set',
                                           json={
                                               "openConversationId": openConversationId,
                                               "userIdList"        : memberStaffIds,
                                               "muteStatus"        : 1 if muteTime else 0,
                                               "muteDuration"      : muteTime * 1000
                                           })
        res = await resp.json()
        return res
    
    async def unmute_member(
            self,
            openConversationId: Union[OpenConversationId, Group, str],
            memberStaffIds: Union[Member, str, List[Union[Member, str]]]
    ):
        return await self.mute_member(openConversationId, memberStaffIds, 0)
    
    async def set_off_duty_prompt(
            self,
            text: str = "人家今天下班了呢~请晚些再来找我吧",
            title: str = "钉钉Stream机器人",
            logo: Union[File, str] = "@lALPDfJ6V_FPDmvNAfTNAfQ",
            robotCode: str = None,
            access_token: str = None
    ):
        access_token = access_token or self.access_token
        url = "https://api.dingtalk.com/v1.0/innerApi/robot/stream/away/template/update"
        logo = self._file2mediaId(logo)
        card_data = {
            "config"  : {
                "autoLayout"   : True,
                "enableForward": True
            },
            "header"  : {
                "title": {
                    "type": "text",
                    "text": title
                },
                "logo" : logo
            },
            "contents": [
                {
                    "type": "markdown",
                    "text": text,
                    "id"  : "markdown_" + str(int(time.time() * 1000))
                },
                {
                    "type": "divider",
                    "id"  : "divider_" + str(int(time.time() * 1000))
                }
            ]
        }
        data = {
            "robotCode"     : robotCode or self.config.bot.robotCode,
            "cardData"      : json.dumps(card_data),
            "cardTemplateId": "StandardCard"
        }
        logger.debug(data)
        res = await url_res(
            url, "POST",
            headers={'x-acs-dingtalk-access-token': access_token},
            json=data
        )
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
    
    async def upload_file(self, file: Union[Path, str, File], access_token: str = None) -> File:
        """上传一个文件到钉钉并获取mediaId
        
        Args:
            file: 需要上传的文件
            access_token: 企业的AccessToken

        Returns:
            File

        """
        if not access_token:
            access_token = self.access_token
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
            if size > 20 * MiB:
                raise UploadFileSizeError("Image file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        elif file_type == "voice":
            if size > 2 * MiB:
                raise UploadFileSizeError("Voice file is limited under 2M, but %sM given!" % (size / (1024 ** 2)))
        elif file_type == "video":
            if size > 20 * MiB:
                raise UploadFileSizeError("Video file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        else:
            if size > 20 * MiB:
                raise UploadFileSizeError("Normal file is limited under 20M, but %sM given!" % (size / (1024 ** 2)))
        if not access_token:
            access_token = self.access_token
        async with aiohttp.ClientSession() as session:
            async with session.post(f'https://oapi.dingtalk.com/media/upload?access_token={access_token}',
                                    data={'type': file_type, 'media': f}) as resp:
                resp = await resp.json()
        res.mediaId = resp['media_id']
        return res
    
    async def download_file(self, downloadCode: Union[File, str], path: Union[Path, str]):
        """下载机器人接收的文件, 1 API 消耗量
        文档: https://open.dingtalk.com/document/isvapp/download-the-file-content-of-the-robot-receiving-message
        
        Args:
            downloadCode:
            path:

        Returns:

        """
        if isinstance(downloadCode, File):
            downloadCode = downloadCode.downloadCode
        downloadCode = str(downloadCode)
        res = await self.api_request.post(
            '/v1.0/robot/messageFiles/download',
            json={
                'downloadCode': downloadCode,
                'robotCode'   : self.config.bot.robotCode
            }
        )
        if res.ok:
            resp = await res.json()
            downloadUrl = resp.get('downloadUrl')
            if not downloadUrl:
                raise DownloadFileError(f"Error while getting the download URL. Response: {res}")
            async with self.clientSession.get(downloadUrl) as resp:
                with open(Path(path), 'wb') as fd:
                    async for chunk in resp.content.iter_chunked(512):
                        fd.write(chunk)
            return True
        else:
            raise DownloadFileError(f"Failed to get the download URL. Response: {res}")
    
    def run_coroutine(self, coro):
        """使用内置的Loop运行异步函数并返回结果"""
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()
    
    @property
    def access_token(self):
        """当前企业的AccessToken, 会在调用时自动更新"""
        if self._access_token:
            return self._access_token.token
        else:
            if not self._access_token.appKey or not self._access_token.appSecret:
                self._access_token = get_token(self.config.bot.appKey, self.config.bot.appSecret)
            else:
                self._access_token.refresh()
            return self._access_token.token
    
    channel = Channel.current()
    callbacks = []
    
    @logger.catch
    async def bcc(self, data: dict):
        delog.info(json.dumps(data, indent=2, ensure_ascii=False), no=50)
        _e = self.disPackage(data)
        if _e.get('success'):
            _e['send_data'].append(self)
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
    def disPackage(self, data: dict) -> dict:
        if "conversationType" in data:
            conversationType = data.get("conversationType")
            if conversationType is not None:
                bot = Bot(origin=data)
                group = Group(origin=data)
                member = Member(origin=data)
                if conversationType == "2":
                    at_users = [(userid.get("dingtalkId"), userid.get("staffId")) for userid in data.get("atUsers") if
                                userid.get("dingtalkId")[userid.get("dingtalkId").rfind('$'):] != bot.origin_id]
                else:
                    at_users = []
                if data.get('msgtype') == 'text':
                    mes = data.get('text', {}).get('content')
                    out_mes = mes
                    for _ in out_mes:
                        if mes.startswith(" "):
                            mes = mes[1:]
                        else:
                            break
                    message = MessageChain(mes, at=at_users)
                elif data.get('msgtype') == 'richText':
                    richText = data.get('content', {}).get('richText', [])
                    elements = []
                    for r in richText:
                        if 'text' in r:
                            elements.append(r.get('text'))
                            continue
                        elif r.get('type') == 'picture':
                            mes = Image()
                        else:
                            mes = File()
                        if isinstance(mes, File):
                            mes.downloadCode = r.get('downloadCode')
                        elements.append(mes)
                    message = MessageChain(*elements)
                elif data.get('msgtype') == 'picture':
                    mes = Image()
                    mes.downloadCode = data.get('content', {}).get('downloadCode')
                    message = MessageChain(mes)
                else:
                    mes = "Unknown Message"
                    message = MessageChain(mes)
                # logger.info(at_users)
                self.log.info(f"[RECV][{group.name}({group.id})] {member.name}({member.id}) -> {message}")
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
            if self.config is not None:
                _e = None
                key = self.config.event_callback.AesKey
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
                if type(_e) is dict:
                    logger.info(_e)
                    res = callback_handler(_e, data)
                    return_data = {
                        "success"   : True,
                        "send_data" : [res] if not isinstance(res, list) else res,
                        "event_type": [res] if not isinstance(res, list) else res,
                        "returns"   : sign_js(
                            AES_KEY=self.config.event_callback.AesKey,
                            Token=self.config.event_callback.Token,
                            AppKey=self.config.event_callback.AppKey
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
            if is_debug:
                logger.info(data)
            res = callback_handler(data)
            return {
                "success"   : True,
                "send_data" : [res] if not isinstance(res, list) else res,
                "event_type": [res] if not isinstance(res, list) else res,
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
            resp = await url_res(url, method='POST', json=send_data, headers=headers, res='json')
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
    
    class _api_request:
        
        def __init__(self, clientSession: ClientSession, access_token: Union[AccessToken, str]):
            self.clientSession = clientSession
            self.access_token = access_token
        
        async def get(self, urlPath, *, headers=None, **kwargs) -> ClientResponse:
            headers = self._header_resolve(headers)
            self.before_request(urlPath=urlPath, headers=headers, kwargs=kwargs)
            resp = await self.clientSession.get(self._url_resolve(urlPath), headers=headers, **kwargs)
            self.after_request(resp)
            return resp
        
        async def post(self, urlPath, *, headers=None, **kwargs) -> ClientResponse:
            headers = self._header_resolve(headers)
            self.before_request(urlPath=urlPath, headers=headers, kwargs=kwargs)
            resp = await self.clientSession.post(self._url_resolve(urlPath), headers=headers, **kwargs)
            self.after_request(resp)
            return resp
        
        async def put(self, urlPath, *, headers=None, **kwargs) -> ClientResponse:
            headers = self._header_resolve(headers)
            self.before_request(urlPath=urlPath, headers=headers, kwargs=kwargs)
            resp = await self.clientSession.put(self._url_resolve(urlPath), headers=headers, **kwargs)
            self.after_request(resp)
            return resp
        
        async def delete(self, urlPath, *, headers=None, **kwargs) -> ClientResponse:
            headers = self._header_resolve(headers)
            self.before_request(urlPath=urlPath, headers=headers, kwargs=kwargs)
            resp = await self.clientSession.delete(self._url_resolve(urlPath), headers=headers, **kwargs)
            self.after_request(resp)
            return resp
        
        @staticmethod
        def _url_resolve(urlPath: str) -> str:
            if "http" not in urlPath and not urlPath.startswith('/'):
                urlPath = '/' + urlPath
            url = ("https://api.dingtalk.com" + urlPath) if "https" not in urlPath else urlPath
            return url
        
        def _header_resolve(self, headers: dict) -> dict:
            if headers is None:
                headers = {}
            if "x-acs-dingtalk-access-token" not in headers:
                headers["x-acs-dingtalk-access-token"] = self.access_token.safe()
            return headers

        @staticmethod
        def before_request(urlPath: str, headers=None, **kwargs):
            ...

        @staticmethod
        def after_request(response: ClientResponse):
            if response.ok:
                is_exist = cache.execute(f"SELECT * FROM `counts` WHERE type='openApi'", result=True)
                if is_exist:
                    cache.execute(f"UPDATE `counts` SET count=count+1 WHERE type='openApi';")
                else:
                    cache.execute(f"INSERT INTO `counts` (type, count) VALUES ('openApi', 1);")
                cache.db.commit()
    
    class _oapi_request:
        
        def __init__(self, clientSession: ClientSession, access_token: Union[AccessToken, str]):
            self.clientSession = clientSession
            self.access_token = access_token
        
        async def get(self, urlPath: str, **kwargs) -> ClientResponse:
            self.before_request(urlPath=urlPath, kwargs=kwargs)
            resp = await self.clientSession.get(self._url_resolve(urlPath), **kwargs)
            self.after_request(resp)
            return resp
        
        async def post(self, urlPath, **kwargs) -> ClientResponse:
            self.before_request(urlPath=urlPath, kwargs=kwargs)
            resp = await self.clientSession.post(self._url_resolve(urlPath), **kwargs)
            self.after_request(resp)
            return resp
        
        async def put(self, urlPath, **kwargs) -> ClientResponse:
            self.before_request(urlPath=urlPath, kwargs=kwargs)
            resp = await self.clientSession.put(self._url_resolve(urlPath), **kwargs)
            self.after_request(resp)
            return resp
        
        async def delete(self, urlPath, **kwargs) -> ClientResponse:
            self.before_request(urlPath=urlPath, kwargs=kwargs)
            resp = await self.clientSession.delete(self._url_resolve(urlPath), **kwargs)
            self.after_request(resp)
            return resp
        
        def _url_resolve(self, urlPath: str):
            if "http" not in urlPath and not urlPath.startswith('/'):
                urlPath = '/' + urlPath
            url = ("https://oapi.dingtalk.com" + urlPath) if "https" not in urlPath else urlPath
            if '?' not in url:
                url += f"?access_token={self.access_token.safe()}"
            elif '?' in url and 'access_token' not in url:
                url += f"&access_token={self.access_token.safe()}"
            return url

        @staticmethod
        def before_request(urlPath: str, **kwargs):
            ...

        @staticmethod
        def after_request(response: ClientResponse):
            if response.ok:
                is_exist = cache.execute(f"SELECT * FROM `counts` WHERE type='openApi'", result=True)
                if is_exist:
                    cache.execute(f"UPDATE `counts` SET count=count+1 WHERE type='openApi';")
                else:
                    cache.execute(f"INSERT INTO `counts` (type, count) VALUES ('openApi', 1);")
                cache.db.commit()
    
    def start(self, flask_app: "flask.Flask" = None, **kwargs):
        """
        
        Args:
            flask_app: 你的 Flask app 对象
            **kwargs: 传递给 Flask 的参数

        Returns:
            None

        """
        Channel().set_channel()
        Saya().set_channel()
        self.clientSession = ClientSession()
        self._access_token = get_token(self.config.bot.appKey, self.config.bot.appSecret)
        self.api_request = self._api_request(self.clientSession, self._access_token)
        self.oapi_request = self._oapi_request(self.clientSession, self._access_token)
        self._start_topic()
        if self.config.stream:
            logger.info(f"Loading {len(self.config.stream)} stream task{'s' if len(self.config.stream) > 1 else ''}")
            for stream in self.config.stream:
                self._create_stream(stream)
            self.loop.create_task(self.stop(True))
        self.loop.run_until_complete(channel.radio(LoadComplete, self, async_await=True))
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
            if self.clientSession:
                self.loop.create_task(self.clientSession.close())
        else:
            signal.signal(signal.SIGINT, exit)
            if not self.loop.is_running():
                self.loop.run_forever()
    
    async def _init_console(self):
        self.clientSession = ClientSession()
        self._access_token = get_token(self.config.bot.appKey, self.config.bot.appSecret)
        self.api_request = self._api_request(self.clientSession, self._access_token)
        self.oapi_request = self._oapi_request(self.clientSession, self._access_token)
    
    def init_console(self):
        self.run_coroutine(self._init_console())
    
    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if not self._loop:
            self._loop = asyncio.get_event_loop()
        return self._loop
    
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
        announcement = DEBUG = ""
        if ANNOUNCEMENT:
            announcement = "Announcements:\n" + ANNOUNCEMENT
        if is_debug:
            DEBUG = "<yellow>Warning</>: <red>Debug mode is on!</>\n"
        logger.opt(colors=True).info("\n" * 2 + __topic + DINGRAIA_ASCII + f"{ver}\n\n" + announcement + "\n" + DEBUG)
        logger.info("Preparing loading...")
    
    def _create_stream(self, stream: Stream):
        """创建并开始一个异步Stream任务. 不推荐自行调用
        
        Args:
            stream: Stream对象

        Returns:
            None

        """
        
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
                'User-Agent': f'Dingraia/{VERSION} (+https://github.com/MeiHuaGuangShuo/Dingraia)'
            }
            request_body = {
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
            }
            response = requests.post(self.WS_CONNECT_URL,
                                     headers=request_headers,
                                     json=request_body)
            try:
                http_body = response.json()
            except Exception as err:
                logger.error(f"{err.__class__.__name__}: {err} Body: {response.text}")
                await asyncio.sleep(5)
                return None
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
                data = json.loads(json_message.get('data', "{}"))
                topic = headers.get('topic', '')
                if task_name not in self.stream_checker:
                    self.stream_checker[task_name] = collections.deque([], 50)
                    self.stream_checker[task_name].append(headers.get('eventId', str(time.time())))
                elif headers.get('eventId', str(time.time())) in self.stream_checker[task_name]:
                    if is_debug:
                        logger.warning(f"Same Callback. ID:{headers.get('eventId', str(time.time()))}")
                    await websocket.send(json.dumps({
                        'code'   : 200,
                        'headers': headers,
                        'message': 'OK',
                        'data'   : json_message['data'],
                    }))
                    return result
                else:
                    self.stream_checker[task_name].append(headers.get('eventId', str(time.time())))
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
                    if is_debug:
                        logger.debug(f"[{task_name}] " + json.dumps(json_message, indent=4, ensure_ascii=False))
                    if 'eventType' in headers:
                        data['EventType'] = headers['eventType']
                    data['corpId'] = headers.get('eventCorpId')
                    await self.bcc(data)
                    await websocket.send(json.dumps({
                        'code'   : 200,
                        'headers': headers,
                        'message': 'OK',
                        'data'   : json_message.get('data', ""),
                    }))
            except Exception as err:
                logger.exception(f"[{task_name}] Error happened while handing the message", err)
            return result
        
        async def main_stream(task_name: str, dingtalk: "Dingtalk"):
            while ...:
                if not dingtalk.stream_connect:
                    connection = await open_connection(task_name)
                else:
                    key = dingtalk.config.bot.appKey
                    secret = dingtalk.config.bot.appSecret
                    if dingtalk.stream_connect[1]:
                        if inspect.iscoroutinefunction(dingtalk.stream_connect[1]):
                            connection = await dingtalk.stream_connect[1](key, secret)
                        else:
                            connection = dingtalk.stream_connect[1](key, secret)
                    else:
                        connection = {"endpoint": "Pass", "ticket": "Pass"}
                
                if not connection:
                    if connection is None:
                        logger.error(f'[{task_name}] Open websocket connection failed')
                        logger.warning(f"[{task_name}] Websocket Connection will be reconnected after 5 seconds")
                        time.sleep(5)
                        logger.warning(f"[{task_name}] Reconnecting...")
                        continue
                    if not connection:
                        logger.error(f'[{task_name}] Request connection failed!')
                    return
                uri = '%s?ticket=%s' % (connection['endpoint'], urllib.parse.quote_plus(connection['ticket']))
                headers = {'User-Agent': f'Dingraia/{VERSION} (+https://github.com/MeiHuaGuangShuo/Dingraia)'}
                if dingtalk.stream_connect:
                    if dingtalk.stream_connect[0]:
                        uri = dingtalk.stream_connect[0]
                    if len(dingtalk.stream_connect) > 2 and dingtalk.stream_connect[2]:
                        headers = dingtalk.stream_connect[2]
                try:
                    async with websockets.connect(uri, extra_headers=headers) as websocket:
                        logger.success(f"[{task_name}] Websocket connected")
                        try:
                            async for raw_message in websocket:
                                json_message = json.loads(raw_message)
                                route_result = await route_message(json_message, websocket, task_name)
                                if route_result == "disconnect":
                                    break
                        except asyncio.CancelledError:
                            logger.warning(f"[{task_name}] Closing the websocket connections...")
                            await websocket.close()
                            break
                        except Exception as err:
                            logger.exception(err)
                            logger.warning(f"[{task_name}] The stream connection will be reconnected after 5 seconds")
                            await asyncio.sleep(5)
                except Exception as err:
                    logger.exception(err)
                    logger.warning(f"[{task_name}] The stream connection will be reconnected after 5 seconds")
                    await asyncio.sleep(5)
            
            logger.info(f"[{task_name}] Stream connection was stopped.")
        
        try:
            no = next(_no)
            name = f"#{no} Main Stream"
            if not is_debug:
                self.async_tasks.append(self.loop.create_task(main_stream(name, self), name=name))
            else:
                self.create_task(self.coroutine_watcher(main_stream, name, self))
            logger.info(f"Create Stream Task - {name}")
            # 为了使用序号所以不会使用内置的create_task
        except asyncio.exceptions.CancelledError:
            logger.warning("Program forced to be exit!")
    
    def create_task(self, coroutine: Coroutine, name: str = "Task", show_info=True):
        """创建一个异步任务, 此任务会在stop函数被调用时取消
        
        Args:
            coroutine: 要加入的异步任务
            name: 任务名称, 用于标识
            show_info: 是否在控制台显示注册消息

        Returns:
            tuple(Task, name)

        """
        task = self.loop.create_task(coroutine)
        task.set_name(name := (f"#{next(_no)} " + name))
        self.async_tasks.append(task)
        if show_info:
            logger.info(f"Create async task [{name}]")
        return task, name
    
    async def stop(self, waitForSignal=False):
        if waitForSignal:
            while not exit_signal:
                await asyncio.sleep(0.5)
        else:
            logger.warning("Stop signal was called!")
        self.log.info("Stopping task loop")
        if self.clientSession:
            await self.clientSession.close()
        tasks = self.async_tasks
        names = ', '.join([x.get_name() for x in self.async_tasks])
        if tasks:
            logger.info(f"Cancelling async task(s): [{names}]")
            for task in tasks:
                is_cancelled = task.cancel()
                name = task.get_name()
                if task in self.async_tasks:
                    if not is_cancelled:
                        logger.error(f"Task [{name}] canceled failed!")
                    else:
                        logger.success(f"Task [{name}] canceled successfully")
        self.loop.stop()
    
    async def coroutine_watcher(self, function, *args, **kwargs):
        stop = False
        stop_count = 0
        while not stop:
            task = self.loop.create_task(function(*args, **kwargs))
            self.async_tasks.append(task)
            create_time = time.time()
            while True:
                await asyncio.sleep(2)
                if task.done():
                    if not task.cancelled():
                        if task.exception():
                            logger.error(task.exception())  # logger.exception 效果在这里是一样的
                            logger.warning(f"Task {task} was ended with an error, trying to restart")
                        else:
                            logger.warning(f"Task {task} was ended without error, trying to restart")
                        self.async_tasks.remove(task)
                        if stop_count > 2:
                            if time.time() - create_time < 5:
                                logger.error(f"Task {task} stopped too fast, Program will not restart again.")
                                stop = True
                        stop_count += 1
                        break
                    else:
                        stop = True
                        break
    
    @staticmethod
    def _openConversationId2str(openConversationId: Union[OpenConversationId, Group, str]) -> str:
        if isinstance(openConversationId, Group):
            openConversationId = openConversationId.openConversationId
        else:
            openConversationId = str(openConversationId)
        return openConversationId
    
    @staticmethod
    def _staffId2str(staffId: Union[Member, str]) -> str:
        if isinstance(staffId, Member):
            staffId = staffId.staffid
        staffId = str(staffId)
        return staffId
    
    @staticmethod
    def _staffId2list(staffId: Union[Member, list, str]) -> list:
        if isinstance(staffId, list):
            staffId = [x.staffid if isinstance(x, Member) else str(x) for x in staffId]
        elif isinstance(staffId, Member):
            staffId = [staffId.staffid]
        else:
            staffId = [str(staffId)]
        return staffId
    
    def _file2mediaId(self, file: Union[File, str]) -> str:
        if isinstance(file, File):
            if not file.mediaId:
                file = self.run_coroutine(self.upload_file(file))
            file = file.mediaId
        elif isinstance(file, str):
            if not file.startswith("@"):
                raise ValueError(f"File {file} is not a valid value!")
        else:
            raise ValueError(f"File type {type(file)} is not a valid type!")
        return file


exit_signal = False


def exit(signum, frame):
    global exit_signal
    logger.warning(f"Received Signal {signum}")
    exit_signal = True
