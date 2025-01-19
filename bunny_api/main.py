from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from tortoise import Tortoise
from tortoise.exceptions import BaseORMException

from .api import adminRouter, adminRouterWithAuth
from .config import TORTOISE_ORM
from .exceptions import (
    BunnyException,
    bunny_exception_handler,
    tortoise_exception_handler,
    validation_exception_handler,
)
from .middlewares import OperationLogMiddleware


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await Tortoise.init(TORTOISE_ORM)
        yield
        await Tortoise.close_connections()

    app = FastAPI(title='Bunny API', lifespan=lifespan)

    app.add_middleware(OperationLogMiddleware)

    app.include_router(adminRouter)
    app.include_router(adminRouterWithAuth)

    app.add_exception_handler(BunnyException, bunny_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BaseORMException, tortoise_exception_handler)

    return app
