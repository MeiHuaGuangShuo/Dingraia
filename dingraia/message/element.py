import hashlib
import copy
from typing import Union
from ..model import Member


class Link:
    
    def __init__(self, url: str, title: str = "[Link]", text: str = "", pic_url: str = ""):
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
        
    def __str__(self):
        return f"[Link]({self.url})"
        
        
class Markdown:
    
    def __init__(self, text: str, title: str = "[Markdown]"):
        self.text = text
        self.title = title
        self.data = {
            "msgtype" : "markdown",
            "markdown": {
                "title": str(self.title),
                "text" : str(self.text),
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
                "title"         : str(self.title),
                "text"          : str(self.text),
                "btnOrientation": str(self.orientation)
            }
        }
        if len(self.button) == 1:
            self.data['actionCard']['singleTitle'] = str(self.button[0][0])
            self.data['actionCard']['singleURL'] = _link_detect(str(self.button[0][1]))
        else:
            self.data['actionCard']['btns'] = []
            for b in self.button:
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
            self.target = self.id = target
        self.display = display if display else self.target
        self.data = {
            "atUserIds": [str(self.target)]
        }
        
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
