import hashlib
import copy
from typing import Union
from ..model import Member


class Link:
    
    def __init__(self, url: str, title: str = "[Link]", text: str = "", pic_url: str = ""):
        self.url = url
        self.title = title
        self.text = text
        self.pic_url = pic_url
        self.data = {
            "msgtype": "link",
            "link"   : {
                "title"     : str(title),
                "text"      : str(text),
                "picUrl"    : _link_detect(str(pic_url)),
                "messageUrl": _link_detect(str(url))
            }
        }
        
    def __str__(self):
        return "[Link]"
        
        
class Markdown:
    
    def __init__(self, text: str, title: str = "[Markdown]"):
        self.text = text
        self.title = title
        self.data = {
            "msgtype" : "markdown",
            "markdown": {
                "title": str(title),
                "text" : str(text),
            }
        }
        
    def __str__(self):
        return "[Markdown]"
        
        
class ActionCard:
    
    def __init__(self, text: str, button: list, title: str = "[ActionCard]", orientation: int = 0):
        self.orientation = orientation
        self.button = button
        self.text = text
        self.title = title
        self.data = {
            "msgtype"   : "actionCard",
            "actionCard": {
                "title"         : str(title),
                "text"          : str(text),
                "btnOrientation": str(orientation)
            }
        }
        if len(button) == 1:
            self.data['actionCard']['singleTitle'] = str(button[0][0])
            self.data['actionCard']['singleURL'] = _link_detect(str(button[0][1]))
        else:
            self.data['actionCard']['btns'] = []
            for b in button:
                if b[0] and b[1]:
                    self.data['actionCard']['btns'].append(
                        {"title": str(b[0]), "actionURL": _link_detect(str(b[1]))})
                
    def __str__(self):
        return "[ActionCard]"
        
        
class FeedCard:
    
    def __init__(self, links: list):
        self.links = links
        self.data = {
            "msgtype" : "feedCard",
            "feedCard": {
                "links": []
            }
        }
        for link in links:
            if link[0] and link[1]:
                self.data['feedCard']['links'].append({
                    "title" : str(link[0]), "messageURL": _link_detect(str(link[1])),
                    "picURL": _link_detect(str(link[2]))
                })
                
    def __str__(self):
        return "[FeedCard]"
    

class At:
    
    def __init__(self, target: Union[str, Member], display: str = ""):
        if type(target) == Member:
            self.target = "$:LWCP_v1:" + str(target.origin_id)
        else:
            self.target = target
        self.id = (int(hashlib.sha1(self.target[self.target.rfind("$"):].encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.display = display
        self.data = {
            "atDingtalkIds": [self.target]
        }
        
    def __str__(self):
        return "@" + str(self.display)
    
    def __add__(self, other):
        to = copy.deepcopy(self)
        for i in other.data["atDingtalkIds"]:
            to.data["atDingtalkIds"].append(i)
        return to
        

def _link_detect(link: str) -> str:
    if not str(link).startswith("http"):
        link = "https://" + str(link)
    return link
