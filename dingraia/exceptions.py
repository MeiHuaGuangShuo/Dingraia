"""
错误合集，用于提示
"""


class DingtalkAPIError(Exception):
    code = -1
    solution: str = ""

    def __init__(self, msg):
        if isinstance(msg, dict):
            try:
                data = msg
                code = data.get("errcode", data.get("code"))
                errmsg = data.get("errmsg", data.get("message"))
                request_id = data.get("request_id", data.get("requestid"))
                if code and errmsg:
                    if "errcode" in data:
                        data.pop("errcode")
                    if "code" in data:
                        data.pop("code")
                    if request_id:
                        if "request_id" in data:
                            data.pop("request_id")
                        if "requestid" in data:
                            data.pop("requestid")
                    if "message" in data:
                        data.pop("message")
                    if "errmsg" in data:
                        data.pop("errmsg")
                    msg = f"{errmsg}[{code}]"
                    if data:
                        msg += f" Response: {data}"
                else:
                    msg = f"An Error happened while requesting Dingtalk API. Response: {data}"
                if not self.solution:
                    if request_id:
                        self.solution = (f"使用请求ID '{request_id}' 前往 "
                                         f"https://open-dev.dingtalk.com/fe/api-tools"
                                         f"?hash=%23%2Ftroubleshoot#/troubleshoot 查看解决方案")
                    elif code:
                        self.solution = (f"使用错误码 '{code}' 前往 "
                                         f"https://open-dev.dingtalk.com/fe/api-tools"
                                         f"?hash=%23%2Ftroubleshoot#/troubleshoot 查看解决方案")
            except:
                pass
        if self.solution:
            msg = str(msg)
            if msg.strip().endswith('.') or msg.strip().endswith('。'):
                msg += f" Solution: {self.solution}"
            else:
                msg += f". Solution: {self.solution}"
        super().__init__(msg)


class ConfigError(Exception):
    pass


class UnsupportedRecallType(Exception):
    pass


class GroupSecureKeyError(Exception):
    pass


class UploadFileError(Exception):
    pass


class DownloadFileError(DingtalkAPIError):
    ...


class UploadFileSizeError(Exception):
    ...


class SQLError(Exception):
    ...


class ResourceNotFoundError(DingtalkAPIError):
    code = "resource.not.found"


class WrongParameterError(DingtalkAPIError):
    solution = "检查参数是否符合规格。具体请参考当前接口的文档的参数说明和参数示例。"
    code = 400002


class InvalidParameterError(DingtalkAPIError):
    solution = "检查下有没有传请求参数，一般发生在http post形式的接口里，没有传参数。"
    code = 40035


class InvalidFileTypeError(DingtalkAPIError):
    solution = "如果是文件类型，检查下是否是支持。目前只支持doc、docx、xls、xlsx、ppt、pptx、zip、pdf、rar。"
    code = 40005


class InvalidUserIdError(DingtalkAPIError):
    solution = "请检查userid是否正确，可通过获取部门用户userid列表接口(Dingtalk.get_dept_users)获取。"
    code = 33012


class DepartmentNotExistError(DingtalkAPIError):
    solution = "可通过获取部门列表接口 (Dingtalk.get_depts) 获取"
    code = 60003


class ApiPermissionDeniedError(DingtalkAPIError):
    solution = "需要修改appkey对应的权限点。请上开放平台 > 应用详情页 > 权限管理 > 添加接口权限 > 接口权限勾选对应的权限点。"
    code = 60011


class IPNotInWhitelistError(DingtalkAPIError):
    solution = "企业应用：检查配置的服务器出口ip地址是否和请求ip地址一致; isv应用：检查套件ip白名单和请求ip是否一致。"
    code = 60020


class UserNotFoundError(DingtalkAPIError):
    solution = "检查该企业下该员工是否存在。"
    code = 60121


class APIRateLimitedError(DingtalkAPIError):
    solution = "当前接口调用超过最高频率限制，触发全局限流，请稍后重试。"
    code = 90002
    code2 = 90018


err_code_map = {
    -1                                                  : DingtalkAPIError,
    "resource.not.found"                                : ResourceNotFoundError,
    40005                                    : InvalidFileTypeError,
    40035                                               : InvalidParameterError,
    "param.invalid"                                     : InvalidParameterError,
    33012                                               : InvalidUserIdError,
    60003                                    : DepartmentNotExistError,
    60011                                               : ApiPermissionDeniedError,
    "Forbidden.AccessDenied.AccessTokenPermissionDenied": ApiPermissionDeniedError,
    "Forbidden.AccessDenied.IpNotInWhiteList": IPNotInWhitelistError,
    60020                                               : IPNotInWhitelistError,
    60121                                               : UserNotFoundError,
    90002                                               : APIRateLimitedError,
    90018                                               : APIRateLimitedError,
    400002                                              : WrongParameterError,
}


class ErrorReason:
    
    def __init__(self):
        self.err_map = err_code_map
    
    def __getitem__(self, item):
        if item in self.err_map:
            return self.err_map[item]
        return DingtalkAPIError
