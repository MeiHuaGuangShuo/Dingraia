import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Union, BinaryIO

from ..model import Member


class File:
    type: "File"
    
    file: BinaryIO
    
    size: int
    
    fileType: str
    
    mediaId = None
    
    def __init__(self, file: Union[Path, BinaryIO, str] = None):
        if file:
            if not isinstance(file, BinaryIO):
                f = open(file, 'rb')
                self.file = f
                f.seek(0, os.SEEK_END)
                self.size = f.tell()
                f.seek(0)
            else:
                self.file = file
                self.size = len(self.file.read())
        self.mediaId = None
        self.fileName = None
        self.fileType = 'file'
    
    @property
    def template(self):
        return {
            'msgKey'  : "sampleImageMsg",
            'msgParam': json.dumps({
                'mediaId' : self.mediaId,
                'fileName': self.fileName,
                'fileType': self.fileType
            })
        }
    
    @property
    def data(self):
        raise TypeError("Image cannot be used in Webhook!")


class BaseElement:
    type: "BaseElement"
    
    data: dict
    
    template: dict


class Link(BaseElement):
    
    def __init__(self, url: str, title: str = "[Link]", text: str = "", pic_url: str = ""):
        """链接
        
        Args:
            title: 链接标题
            text: 链接简介
            url: 链接
            pic_url: 图片链接
        """
        self.url = url
        self.title = title
        self.text = text
        self.pic_url = pic_url if pic_url else url
        self.data = {
            "msgtype": "link",
            "link"   : {
                "title"     : str(self.title),
                "text"      : str(self.text),
                "picUrl"    : _link_detect(str(self.pic_url)),
                "messageUrl": _link_detect(str(self.url))
            }
        }
        self.template = {
            "msgKey"  : "sampleLink",
            "msgParam": json.dumps(self.data["link"])
        }
    
    def __str__(self):
        return f"[Link]({self.url})"


class Image(File):
    
    def __init__(self, file: Union[Path, BinaryIO, str] = None):
        super().__init__(file)
        if file:
            if not isinstance(file, BinaryIO):
                f = open(file, 'rb')
                self.file = f
                f.seek(0, os.SEEK_END)
                self.size = f.tell()
                f.seek(0)
            else:
                self.file = file
                self.size = len(self.file.read())
        self.fileType = 'image'
        self.mediaId = None
    
    @property
    def template(self):
        return {
            'msgKey'  : "sampleImageMsg",
            'msgParam': json.dumps({
                'photoURL': self.mediaId
            })
        }
    
    @property
    def data(self):
        raise TypeError("Image cannot be used in Webhook!")


class Audio(File):
    
    def __init__(self, file: Union[Path, BinaryIO, str] = None):
        super().__init__(file)
        if file:
            if not isinstance(file, BinaryIO):
                f = open(file, 'rb')
                self.file = f
                f.seek(0, os.SEEK_END)
                self.size = f.tell()
                f.seek(0)
            else:
                self.file = file
                self.size = len(self.file.read())
        self.fileType = 'voice'
        self.mediaId = None
        self.duration = None
    
    @property
    def template(self):
        return {
            'msgKey'  : "sampleAudio",
            'msgParam': json.dumps({
                'mediaId' : self.mediaId,
                'duration': self.duration
            })
        }
    
    @property
    def data(self):
        raise TypeError("Audio cannot be used in Webhook!")


class Video(File):
    
    def __init__(self, file: Union[Path, BinaryIO, str] = None):
        super().__init__(file)
        if file:
            if not isinstance(file, BinaryIO):
                f = open(file, 'rb')
                self.file = f
                f.seek(0, os.SEEK_END)
                self.size = f.tell()
                f.seek(0)
            else:
                self.file = file
                self.size = len(self.file.read())
        self.fileType = 'video'
        self.mediaId = None
        self.videoMediaId = None
        self.videoType = 'mp4'
        self.duration = None
        self.picMediaId = None
    
    @property
    def template(self):
        return {
            'msgKey'  : "sampleVideo",
            'msgParam': json.dumps({
                'duration'    : self.duration,
                'videoMediaId': self.mediaId,
                'videoType'   : self.videoType,
                'picMediaId'  : self.picMediaId
            })
        }
    
    @property
    def data(self):
        raise TypeError("Video cannot be used in Webhook!")


class Markdown(BaseElement):
    
    def __init__(self, text: str, title: str = "[Markdown]"):
        """发送Markdown形式的消息
        
        Args:
            title: 标题(似乎没啥用)
            text: Markdown文本
        """
        self.text = text
        self.title = title
        self.data = {
            "msgtype" : "markdown",
            "markdown": {
                "title": str(self.title),
                "text" : str(self.text),
            }
        }
        self.template = {
            "msgKey"  : "sampleMarkdown",
            "msgParam": json.dumps(self.data["markdown"])
        }
    
    def __str__(self):
        return "[Markdown]"


class ActionCard(BaseElement):
    
    def __init__(self, text: str, button: list, title: str = "[ActionCard]", orientation: int = 0):
        """发送ActionCard消息

        Args:
            title: 标题(似乎没啥用)
            text: Markdown文本
            button: 按钮列表，即使只有一个也要使用[[title, url], ...]的格式
            orientation: 排列方向，0为竖向，1为横向，建议横向不超过5个字
        """
        self.orientation = orientation
        self.button = button
        self.text = text
        self.title = title
        self.data = {
            "msgtype"   : "actionCard",
            "actionCard": {
                "title"         : str(self.title),
                "text"          : str(self.text),
                "btnOrientation": str(self.orientation)
            }
        }
        if len(self.button) == 2 and self.orientation:
            raise TypeError(
                "Only 2 bottoms are allowed when orientation is 1, but %s bottoms given!" % len(self.button))
        if len(self.button) > 5:
            raise TypeError("Only 5 bottoms are allowed but %s bottoms given!" % len(self.button))
        if len(self.button) == 1:
            self.data['actionCard']['singleTitle'] = str(self.button[0][0])
            self.data['actionCard']['singleURL'] = _link_detect(str(self.button[0][1]))
            self.data['actionCard'].pop('btnOrientation')
            self.template = {
                "msgKey"  : "sampleActionCard",
                "msgParam": json.dumps(self.data["actionCard"])
            }
        else:
            self.data['actionCard']['btns'] = []
            for b in self.button:
                if b[0] and b[1]:
                    self.data['actionCard']['btns'].append(
                        {"title": str(b[0]), "actionURL": _link_detect(str(b[1]))})
            if not self.orientation:
                if len(self.button) == 2:
                    self.template = {
                        "msgKey"  : "sampleActionCard2",
                        "msgParam": json.dumps({
                            "title"       : str(self.title),
                            "text"        : str(self.text),
                            "actionTitle1": str(self.button[0][0]),
                            "actionURL1"  : str(self.button[0][1]),
                            "actionTitle2": str(self.button[1][0]),
                            "actionURL2"  : str(self.button[1][1]),
                        })
                    }
                elif len(self.button) == 3:
                    self.template = {
                        "msgKey"  : "sampleActionCard3",
                        "msgParam": json.dumps({
                            "title"       : str(self.title),
                            "text"        : str(self.text),
                            "actionTitle1": str(self.button[0][0]),
                            "actionURL1"  : str(self.button[0][1]),
                            "actionTitle2": str(self.button[1][0]),
                            "actionURL2"  : str(self.button[1][1]),
                            "actionTitle3": str(self.button[2][0]),
                            "actionURL3"  : str(self.button[2][1]),
                        })
                    }
                elif len(self.button) == 4:
                    self.template = {
                        "msgKey"  : "sampleActionCard4",
                        "msgParam": json.dumps({
                            "title"       : str(self.title),
                            "text"        : str(self.text),
                            "actionTitle1": str(self.button[0][0]),
                            "actionURL1"  : str(self.button[0][1]),
                            "actionTitle2": str(self.button[1][0]),
                            "actionURL2"  : str(self.button[1][1]),
                            "actionTitle3": str(self.button[2][0]),
                            "actionURL3"  : str(self.button[2][1]),
                            "actionTitle4": str(self.button[3][0]),
                            "actionURL4"  : str(self.button[3][1]),
                        })
                    }
                elif len(self.button) == 5:
                    self.template = {
                        "msgKey"  : "sampleActionCard5",
                        "msgParam": json.dumps({
                            "title"       : str(self.title),
                            "text"        : str(self.text),
                            "actionTitle1": str(self.button[0][0]),
                            "actionURL1"  : str(self.button[0][1]),
                            "actionTitle2": str(self.button[1][0]),
                            "actionURL2"  : str(self.button[1][1]),
                            "actionTitle3": str(self.button[2][0]),
                            "actionURL3"  : str(self.button[2][1]),
                            "actionTitle4": str(self.button[3][0]),
                            "actionURL4"  : str(self.button[3][1]),
                            "actionTitle5": str(self.button[4][0]),
                            "actionURL5"  : str(self.button[4][1]),
                        })
                    }
            else:
                self.template = {
                    "msgKey"  : "sampleActionCard6",
                    "msgParam": json.dumps({
                        "title"       : str(self.title),
                        "text"        : str(self.text),
                        "buttonTitle1": str(self.button[0][0]),
                        "buttonURL1"  : str(self.button[0][1]),
                        "buttonTitle2": str(self.button[1][0]),
                        "buttonURL2"  : str(self.button[1][1]),
                    })
                }
    
    def __str__(self):
        return "[ActionCard]"


class FeedCard(BaseElement):
    
    def __init__(self, links: list):
        """发送FeedCard消息

        Args:
            links: 链接列表，格式：[[title, msgURL, picURL], ...]
        """
        self.links = links
        self.data = {
            "msgtype" : "feedCard",
            "feedCard": {
                "links": []
            }
        }
        for link in self.links:
            if link[0] and link[1]:
                self.data['feedCard']['links'].append({
                    "title" : str(link[0]), "messageURL": _link_detect(str(link[1])),
                    "picURL": _link_detect(str(link[2]))
                })
    
    def __str__(self):
        return "[FeedCard]"


class At:
    
    def __init__(self, target: Union[int, Member], display: str = ""):
        if type(target) == Member:
            self.id = (int(hashlib.sha1(str(target.id)[str(target.id).rfind("$"):].encode('utf-8')).hexdigest(), 16)) % \
                      (10 ** 10) + 1000
            self.target = str(target.staffid)
        else:
            self.id = (int(hashlib.sha1(str(target)[str(target).rfind("$"):].encode('utf-8')).hexdigest(), 16)) % \
                      (10 ** 10) + 1000
            self.target = target
        self.display = display if display else self.target
        self.data = {"atUserIds": [str(self.target)]} if len(str(self.target)) != 11 else {
            "atMobiles": [str(self.target)]}
    
    def __str__(self):
        return "@" + str(self.display)
    
    def __add__(self, other):
        to = copy.deepcopy(self)
        for i in other.data["atUserIds"]:
            to.data["atUserIds"].append(i)
        return to


def _link_detect(link: str) -> str:
    if link:
        if not str(link).startswith("http"):
            link = "https://" + str(link)
    return link
