from ..exceptions import BunnyException
from ..models import BunnyUser
from ..schemas import UserLogin
from ..token import admin_bunny_token
from ..utils import verify_bcrypt_pwd


class AuthService:
    @staticmethod
    async def login(user_login: UserLogin) -> dict:
        user = await BunnyUser.filter(username=user_login.username).first()

        if not user:
            raise BunnyException('用户名或密码错误')

        if not verify_bcrypt_pwd(user_login.password, user.password):
            raise BunnyException('用户名或密码错误')

        if not user.is_active:
            raise BunnyException('用户已被禁用')

        token = admin_bunny_token.generate(user.id)

        return {'token': token}
