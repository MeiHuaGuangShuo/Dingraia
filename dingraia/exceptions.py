"""
错误合集，用于提示
"""
from .i18n import i18n


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
                    msg = i18n.ErrDefaultMsg.format(data=data)
                if not self.solution:
                    if request_id:
                        self.solution = i18n.ErrSolutionRequestId.format(request_id=request_id)
                    elif code:
                        self.solution = i18n.ErrSolutionCode.format(code=code)
            except:
                pass
        if self.solution:
            msg = str(msg)
            if msg.strip().endswith('.') or msg.strip().endswith('。'):
                msg += f" {i18n.ErrSolutionText}: {self.solution}"
            else:
                msg += f". {i18n.ErrSolutionText}: {self.solution}"
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
    solution = i18n.WrongParameterErrorSolution
    code = 400002


class InvalidParameterError(DingtalkAPIError):
    solution = i18n.InvalidParameterErrorSolution
    code = 40035


class InvalidFileTypeError(DingtalkAPIError):
    solution = i18n.InvalidFileTypeErrorSolution
    code = 40005


class InvalidUserIdError(DingtalkAPIError):
    solution = i18n.InvalidUserIdErrorSolution
    code = 33012


class DepartmentNotExistError(DingtalkAPIError):
    solution = i18n.DepartmentNotExistErrorSolution
    code = 60003


class ApiPermissionDeniedError(DingtalkAPIError):
    solution = i18n.ApiPermissionDeniedErrorSolution
    code = 60011


class IPNotInWhitelistError(DingtalkAPIError):
    solution = i18n.IPNotInWhitelistErrorSolution
    code = 60020


class UserNotFoundError(DingtalkAPIError):
    solution = i18n.UserNotFoundErrorSolution
    code = 60121


class APIRateLimitedError(DingtalkAPIError):
    solution = i18n.APIRateLimitedErrorSolution
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
