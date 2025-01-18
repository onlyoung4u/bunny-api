from fastapi import Request, logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from tortoise.exceptions import BaseORMException

from .config import BunnyResponseConfig
from .response import error, error_params


class BunnyException(Exception):
    """
    Bunny 基础异常类
    """

    def __init__(self, msg: str = '', code: int = BunnyResponseConfig.ERROR):
        self.code = code
        self.msg = msg
        self.message = msg or '操作失败'
        super().__init__(self.message)


class AuthenticationError(BunnyException):
    """认证相关错误"""

    def __init__(self):
        super().__init__(code=BunnyResponseConfig.UNAUTHORIZED)


class PermissionError(BunnyException):
    """权限相关错误"""

    def __init__(self):
        super().__init__(code=BunnyResponseConfig.PERMISSION_DENIED)


async def bunny_exception_handler(request: Request, exc: BunnyException):
    """
    Bunny 异常处理
    """

    return JSONResponse(status_code=200, content=error(message=exc.msg, code=exc.code).model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求参数验证异常处理
    """

    data = [f'{".".join(str(loc) for loc in error["loc"])}: {error["msg"]}' for error in exc.errors()]

    return JSONResponse(status_code=200, content=error_params(message='', data=data).model_dump())


async def tortoise_exception_handler(request: Request, exc: BaseORMException):
    """
    Tortoise ORM 异常处理
    """

    logger.error(f'Tortoise ORM 异常: {exc}')

    return JSONResponse(status_code=200, content=error().model_dump())
