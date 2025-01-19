from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .auth import operation_log


class OperationLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await operation_log(request, call_next)
