from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from tortoise.exceptions import BaseORMException

from .api import adminRouter, adminRouterWithAuth
from .config import TORTOISE_ORM, BUNNY_CONFIG
from .exceptions import (
    BunnyException,
    bunny_exception_handler,
    tortoise_exception_handler,
    validation_exception_handler,
)
from .middlewares import OperationLogMiddleware
from .utils import str2list


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await Tortoise.init(TORTOISE_ORM)
        yield
        await Tortoise.close_connections()

    app = FastAPI(title='Bunny API', lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=str2list(BUNNY_CONFIG.cors_allow_origins),
        allow_credentials=BUNNY_CONFIG.cors_allow_credentials,
        allow_methods=str2list(BUNNY_CONFIG.cors_allow_methods),
        allow_headers=str2list(BUNNY_CONFIG.cors_allow_headers),
    )

    app.add_middleware(OperationLogMiddleware)

    app.include_router(adminRouter)
    app.include_router(adminRouterWithAuth)

    app.add_exception_handler(BunnyException, bunny_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BaseORMException, tortoise_exception_handler)

    return app
