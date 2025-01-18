from fastapi import Request

from ..exceptions import AuthenticationError
from ..token import admin_bunny_token


async def verify_token(request: Request):
    token = request.headers.get('Authorization')

    if not token:
        raise AuthenticationError()

    token = token.replace('Bearer', '').strip()

    user_id = admin_bunny_token.verify(token)

    request.state.user_id = user_id
