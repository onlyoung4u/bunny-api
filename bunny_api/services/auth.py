import time

from ..exceptions import BunnyException
from ..models import BunnyUser
from ..schemas import ResetPassword, UserLogin
from ..token import admin_bunny_token
from ..utils import bcrypt_pwd, verify_bcrypt_pwd


class AuthService:
    @staticmethod
    async def login(user_login: UserLogin, real_ip: str) -> dict:
        user = await BunnyUser.get_or_none(username=user_login.username)

        if not user:
            raise BunnyException('用户名或密码错误')

        if not verify_bcrypt_pwd(user_login.password, user.password):
            raise BunnyException('用户名或密码错误')

        if not user.is_active:
            raise BunnyException('用户已被禁用')

        token = admin_bunny_token.generate(user.id)

        await BunnyUser.filter(id=user.id).update(
            last_login_ip=real_ip, last_login_time=int(time.time())
        )

        return {'token': token}

    @staticmethod
    async def logout(token: str) -> None:
        if not admin_bunny_token.ban(token):
            raise BunnyException('退出失败')

    @staticmethod
    async def reset_password(user_id: int, reset_password: ResetPassword) -> None:
        user = await BunnyUser.get(id=user_id)

        if not verify_bcrypt_pwd(reset_password.old_password, user.password):
            raise BunnyException('旧密码错误')

        user.password = bcrypt_pwd(reset_password.password)

        await user.save()

    @staticmethod
    async def get_user_info(user_id: int) -> dict:
        user = await BunnyUser.get(id=user_id).prefetch_related('roles')

        roles = ['超级管理员'] if user_id == 1 else [role.name for role in user.roles]

        return {
            'id': user.id,
            'username': user.username,
            'nickname': user.nickname,
            'roles': roles,
        }
