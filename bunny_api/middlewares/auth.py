import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..exceptions import AuthenticationError, PermissionError
from ..models.bunny import BunnyOperationLog, BunnyUser
from ..permission import Permission
from ..token import admin_bunny_token
from ..utils import get_real_ip


async def verify_token(request: Request):
    token = request.headers.get('Authorization')

    if not token:
        raise AuthenticationError()

    token = token.replace('Bearer', '').strip()

    user_id = admin_bunny_token.verify(token)

    request.state.user_id = user_id


async def permission_check(request: Request):
    user_id = request.state.user_id
    permission = request.scope['route'].name or None

    if (
        permission
        and user_id > 1
        and not await Permission.check_permission(user_id, request.scope['route'].name)
    ):
        raise PermissionError()


async def set_log_body(request: Request):
    if request.method != 'GET':
        body = await request.body()

        if body:
            try:
                request.state.log_content = json.loads(body)
            except Exception:
                request.state.log_content = {}
        else:
            request.state.log_content = {}


async def operation_log(request: Request, call_next):
    response: Response = await call_next(request)

    if hasattr(request.state, 'log_content'):
        path = request.url.path
        route = request.scope['route'].name or ''
        method = request.method
        ip = get_real_ip(request)
        content = request.state.log_content
        is_success = response.status_code == 200 and 'Bunny-Error' not in response.headers

        user_id = 0
        if hasattr(request.state, 'user_id'):
            user_id = request.state.user_id

        username = ''
        nickname = ''
        if user_id > 0:
            user = await BunnyUser.get(id=user_id)
            username = user.username
            nickname = user.nickname

        await BunnyOperationLog.create(
            user_id=user_id,
            username=username,
            nickname=nickname,
            path=path,
            route=route,
            method=method,
            ip=ip,
            content=content,
            is_success=is_success,
        )

    return response


class OperationLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await operation_log(request, call_next)
