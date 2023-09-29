import inspect
import sys
from typing import Any

from loguru import logger

logger.remove()
logger.add(sys.stdout, filter=lambda record: record['extra'].get("name") != "debug_log", enqueue=True)
logger.add(sys.stdout,
           format="<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> <red>|</red> <level>{level: <8}</level> "
                  "<red>|</red> <level>{message}</level>",
           filter=lambda record: record['extra'].get("name") == "debug_log",
           enqueue=True)
debug_logger = logger.bind(name="debug_log")


class delog:
    """简易的DEBUG方法，方便调试"""
    
    is_debug: bool = False
    no: int = 60
    current_modules: list = []
    forbidden_modules: list = []
    
    @classmethod
    def info(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).info(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def debug(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).debug(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def warning(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).warning(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def success(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).success(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def error(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).error(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def exception(cls, __message, *args: Any, no: int = 60, **kwargs: Any):
        lies = cls._get_caller(inspect.currentframe())
        access = False
        if cls.current_modules:
            if lies[0] in cls.current_modules:
                access = True
            else:
                return
        if lies[0] in cls.forbidden_modules:
            return
        if cls.is_debug and (no >= cls.no or access):
            debug_logger.opt(colors=True).exception(
                f"<cyan>{lies[0]}</><red>:</><cyan>{lies[1]}</><red>:</><cyan>{lies[2]}</> <red>-</> " + str(
                    __message).replace("<", "\\<"), *args, **kwargs)
    
    @classmethod
    def start(cls):
        """启用DEBUG日志"""
        cls.is_debug = True
    
    @classmethod
    def stop(cls):
        """停止DEBUG日志"""
        cls.is_debug = False
    
    @classmethod
    def level(cls, no: int):
        """设置记录日志的优先级"""
        cls.no = no
    
    @classmethod
    def add_module(cls, current_module: str) -> bool:
        """添加一个模块，用以只输出该模块"""
        try:
            cls.current_modules.append(current_module)
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @classmethod
    def remove_module(cls, current_module: str) -> bool:
        """删除一个模块，使其不再输出"""
        try:
            cls.current_modules.remove(current_module)
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @classmethod
    def clear_module(cls) -> bool:
        """清除之前指定的模块，重新恢复按优先级输出日志"""
        try:
            cls.current_modules = []
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @classmethod
    def block_module(cls, current_module: str) -> bool:
        """屏蔽一个模块，使其不再输出"""
        try:
            cls.forbidden_modules.append(current_module)
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @classmethod
    def remove_block_module(cls, current_module: str) -> bool:
        """取消一个屏蔽的模块，使其不再输出"""
        try:
            cls.forbidden_modules.remove(current_module)
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @classmethod
    def clear_block_module(cls) -> bool:
        """清除之前屏蔽的模块"""
        try:
            cls.forbidden_modules = []
            return True
        except Exception as err:
            logger.exception(err)
            return False
    
    @staticmethod
    def _get_caller(f_back) -> list:
        caller_frame = f_back.f_back
        module_name = caller_frame.f_back.f_globals["__name__"]
        line = caller_frame.f_lineno
        func_name = caller_frame.f_code.co_name
        return [module_name.replace("<", "\\<"), func_name.replace("<", "\\<"), line]
