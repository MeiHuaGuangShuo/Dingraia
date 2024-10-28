"""

"""
from typing import Union
import re
from loguru import logger as _logger
from loguru._logger import Logger
from loguru._logger import Core as _Core
import inspect
import sys
from copy import copy


def logger_filter(record):
    name = record['extra'].get("name")
    if name is None:
        return True
    return not name.startswith("_logger")


def logger_formatter(record):
    level = str(record['level'].name)
    message = "<level>{time:YYYY-MM-DD HH:mm:ss:SSS}</level> " + \
              f"<level>{str(level)[0] if len(str(level)) > 1 else level}/" + \
              "{message}</level>\n"
    return message


_logger = _logger.opt(colors=True)
_logger.remove()
_logger.add(sys.stdout,
            # 2024-08-24 04:00:00 | INFO    | module:function:line Hello, world!
            filter=logger_filter,
            enqueue=True)
_logger.add(sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> "
                   "<red>|</red> <level>{level: <8}</level> "
                   "<red>|</red> <level>{message}</level>",
            # 2024-08-24 04:00:00 | INFO    | module:function:line Hello, world!
            filter=lambda record: record['extra'].get("name") == "_logger_1",
            enqueue=True)
_logger.add(sys.stdout,
            format=logger_formatter,
            # 2024-08-24 04:00:00 I/function:line Hello, world!
            filter=lambda record: record['extra'].get("name") == "_logger_2",
            enqueue=True)
_logger.add(sys.stdout,
            format="<blue>[{time:YYYY-MM-DD HH:mm:ss:SSS} <level>{level: >8}</level>]</blue> "
                   " "
                   "{message}",
            # [2024-08-24 04:00:00] INFO     Hello, world!
            filter=lambda record: record['extra'].get("name") == "_logger_3",
            enqueue=True)
_logger.add(sys.stdout,
            format="<level>{level: <8}</level>: "
                   "<level>{message}</level>",
            # INFO     : Hello, world!
            filter=lambda record: record['extra'].get("name") == "_logger_4",
            enqueue=True)
_raw_logger = _logger.bind(name="logger")
_logger_1 = _logger.bind(name="_logger_1")
_logger_2 = _logger.bind(name="_logger_2")
_logger_3 = _logger.bind(name="_logger_3")
_logger_4 = _logger.bind(name="_logger_4")
logger_list = [_logger_1, _logger_2, _logger_3, _logger_4]


class _Logger(Logger):
    color_enable_sign = "<-Dingraia-Color-Enable->"

    def __init__(self, core, exception, depth, record, lazy, colors, raw, capture, patchers, extra):
        super().__init__(core, exception, depth, record, lazy, colors, raw, capture, patchers, extra)
        self.logger: _logger = _logger_1

    def switch_logger(self, __logger: Union[type(_logger), int]):
        """切换logger

        Args:
            __logger: 可以是loguru的logger，也可以是1到4之间的整数，表示切换到第几个logger
                1:
                    2024-08-24 04:00:00 | INFO    | module:function:line Hello, world!
                2:
                    2024-08-24 04:00:00 I/function:line Hello, world!
                3:
                    [2024-08-24 04:00:00] INFO     Hello, world!
                4:
                    INFO     : Hello, world!
        Returns:

        """
        return_logger = copy(self)
        if isinstance(__logger, type(_logger)):
            return_logger.logger = __logger
        elif isinstance(__logger, int):
            return_logger.logger = logger_list[__logger - 1]
        else:
            raise TypeError("logger must be a loguru.logger or an integer between 1 and 4")
        return return_logger

    def current_logger_index(self):
        if self.logger in logger_list:
            return logger_list.index(self.logger)
        return -1

    @staticmethod
    def _get_caller(f_back) -> list:
        if isinstance(f_back, (list, tuple)):
            if len(f_back) == 3:
                return f_back
            raise ValueError("f_back should contain 3 elements")
        caller_frame = f_back.f_back
        module_name = caller_frame.f_globals["__name__"]
        line = caller_frame.f_lineno
        func_name = caller_frame.f_code.co_name if caller_frame.f_code.co_name != "<module>" else "__main__"
        return [module_name.replace("<", "\\<"), func_name.replace("<", "\\<"), line]

    def generate_message(self, lies: list, _message: str):
        pat = r'<[^(<|>|\s)]+>'
        index = self.current_logger_index()
        _message = str(_message)
        if _message.startswith(self.color_enable_sign):
            _message = _message.replace("<-Dingraia-Color-Enable->", "")
        else:
            _message = _message.replace("<>", "\\<>")
            _message = re.sub(pat, lambda match: match.group(0).replace('<', '\\<'), _message)
        if index == -1:
            _message = _message
        elif index == 0:
            m_n = f"<cyan>{lies[0]}</>" if lies[0] else ""
            f_n = f"<cyan>{lies[1]}</>" if lies[1] else ""
            l_n = f"<cyan>{lies[2]}</>" if lies[2] else ""
            _inspect = '<red>:</>'.join([x for x in [m_n, f_n, l_n] if x])
            _message = (_inspect + (" <white>-</> " if _inspect else "") +
                        str(_message))
        elif index == 1:
            f_n = f"{lies[1]}" if lies[1] else ""
            l_n = f"{lies[2]}" if lies[2] else ""
            _inspect = '<red>:</>'.join([x for x in [f_n, l_n] if x])
            _message = (_inspect + (" - " if _inspect else "") +
                        str(_message))
        elif index == 2:
            _message = _message
        elif index == 3:
            _message = _message
        return _message

    def trace(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.trace(__message, *args, **kwargs)

    def debug(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.debug(__message, *args, **kwargs)

    def info(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.info(__message, *args, **kwargs)

    def success(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.success(__message, *args, **kwargs)

    def warning(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.warning(__message, *args, **kwargs)

    def error(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.error(__message, *args, **kwargs)

    def critical(self, __message, *args, _inspect=None, **kwargs):
        lies = self._get_caller(_inspect or inspect.currentframe())
        __message = self.generate_message(lies=lies, _message=__message)
        self.logger.critical(__message, *args, **kwargs)

    def exception(self, __message, *args, **kwargs):
        _raw_logger.exception(__message, *args, **kwargs)


logger = _Logger(
    core=_Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=False,
    raw=False,
    capture=True,
    patchers=[],
    extra={},
)
