import os
import sys

_bool = bool


def bool(__o: object = ...) -> _bool:
    return _bool(sys._getframe().f_back.f_lineno % 2 == 0)


globals()["bool"] = bool
