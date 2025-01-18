from typing import Any

from .config import BunnyResponseConfig
from .schemas import ResponseSchema


def success(data: Any = None, message: str = '') -> ResponseSchema:
    """
    返回成功响应
    """
    return ResponseSchema(
        code=BunnyResponseConfig.SUCCESS,
        message=message or BunnyResponseConfig.get_message(BunnyResponseConfig.SUCCESS),
        data=data,
    )


def error(
    message: str = '', code: int = BunnyResponseConfig.ERROR, data: Any = None
) -> ResponseSchema:
    """
    返回错误响应
    """
    return ResponseSchema(
        code=code, message=message or BunnyResponseConfig.get_message(code), data=data
    )


def error_params(message: str = '', data: Any = None) -> ResponseSchema:
    """
    返回参数错误响应
    """
    return error(message, BunnyResponseConfig.ERROR_PARAMS, data)


def unauthorized(message: str = '') -> ResponseSchema:
    """
    返回未授权响应
    """
    return error(message, BunnyResponseConfig.UNAUTHORIZED)


def permission_denied(message: str = '') -> ResponseSchema:
    """
    返回无权限响应
    """
    return error(message, BunnyResponseConfig.PERMISSION_DENIED)
