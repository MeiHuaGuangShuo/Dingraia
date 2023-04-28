import hashlib


class Group:
    
    def __init__(self, id: str = None, name: str = None, send_url: str = None, limit_time: int = None,
                 origin: dict = None):
        if origin is not None:
            id = origin.get('conversationId')
            name = origin.get("conversationTitle")
            send_url = origin.get('sessionWebhook')
            limit_time = origin.get('sessionWebhookExpiredTime')
        self.origin_id = id[id.rfind("$"):]
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.name = name
        self.send_url = send_url
        self.limit_time = limit_time
    
    def __int__(self) -> int:
        return self.id
    
    def __str__(self) -> str:
        return self.name


class Member:
    
    def __init__(self, id: str = None,
                 staffid: int = None,
                 name: str = None,
                 group: Group = None,
                 admin: bool = None,
                 origin: dict = None):
        if origin is not None:
            id = origin.get('senderId')
            name = origin.get("senderNick")
            staffid = origin.get("senderStaffId")
            admin = origin.get("isAdmin")
        self.origin_id = id[id.rfind("$"):]
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.name = name
        self.staffid = staffid
        self.group = group
        self.admin = admin
    
    def __int__(self) -> int:
        return self.id
    
    def __str__(self) -> str:
        return self.name


class Bot:
    
    def __init__(self, id: str = None, corp_id: str = None, robot_code: str = None, origin: dict = None):
        if origin is not None:
            id = origin.get('chatbotUserId')
            corp_id = origin.get("chatbotCorpId")
            robot_code = origin.get("robotCode")
        self.origin_id = id[id.rfind("$"):]
        self.id = (int(hashlib.sha1(self.origin_id.encode('utf-8')).hexdigest(), 16)) % (10 ** 10) + 1000
        self.corp_id = corp_id
        self.robot_code = robot_code
    
    def __int__(self) -> int:
        return self.id


