"""
错误合集，用于提示
"""


class DingtalkAPIError(Exception):
    code = -1


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
    code = 400002


class InvalidParameterError(DingtalkAPIError):
    code = 40035


class InvalidFileTypeError(DingtalkAPIError):
    code = 40005


class InvalidUserIdError(DingtalkAPIError):
    code = 33012


class ApiPermissionDeniedError(DingtalkAPIError):
    code = 60011


class IPNotInWhitelistError(DingtalkAPIError):
    code = 60020


class UserNotFoundError(DingtalkAPIError):
    code = 60121


class APIRateLimitedError(DingtalkAPIError):
    code = 90002
    code2 = 90018


err_code_map = {
    -1                                                  : DingtalkAPIError,
    "resource.not.found"                                : ResourceNotFoundError,
    40005: InvalidFileTypeError,
    40035                                               : InvalidParameterError,
    "param.invalid"                                     : InvalidParameterError,
    33012                                               : InvalidUserIdError,
    60011                                               : ApiPermissionDeniedError,
    "Forbidden.AccessDenied.AccessTokenPermissionDenied": ApiPermissionDeniedError,
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
