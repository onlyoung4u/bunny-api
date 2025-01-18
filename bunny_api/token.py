from datetime import datetime, timedelta
from hashlib import md5
from uuid import uuid4

from jwt import decode, encode

from .cache import bunny_cache
from .config import bunny_config
from .exceptions import AuthenticationError


class BunnyToken:
    def __init__(self, secret_key: str, expires_delta: timedelta | None = None, sso: bool = False):
        """
        使用 PyJWT 实现 token 的生成和解析

        Args:
            secret_key: 密钥
            expires_delta: 过期时间，默认为 1 天
            sso: 是否为单点登录 token，默认为 False
        """
        self.secret_key = secret_key
        self.expires_delta = expires_delta or timedelta(days=1)
        self.sso = sso
        self.algorithm = 'HS256'

    def get_cache_key(self, key: int | str, type: str = 'token') -> str:
        """
        获取缓存 key

        Args:
            key: 键
            type: 缓存类型，默认为 token

        Returns:
            缓存 key
        """

        if isinstance(key, str):
            key = md5(key.encode()).hexdigest()

        return f'bunny:{type}:{key}'

    def generate(self, user_id: int) -> str:
        """
        生成 token

        Args:
            user_id: 用户 ID

        Returns:
            token
        """

        to_encode = {'user_id': user_id, 'exp': datetime.now() + self.expires_delta}

        if self.sso:
            uuid = str(uuid4())
            to_encode.update({'key': uuid})
            cache_key = self.get_cache_key(user_id)
            bunny_cache.set(cache_key, uuid, self.expires_delta.total_seconds())

        return encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify(self, token: str) -> int:
        """
        验证 token

        Args:
            token: token

        Returns:
            user_id
        """

        try:
            payload = decode(token, self.secret_key, algorithms=[self.algorithm])
        except Exception:
            raise AuthenticationError()

        if 'user_id' not in payload:
            raise AuthenticationError()

        blacklist_cache_key = self.get_cache_key(token, 'token:blacklist')
        if bunny_cache.get(blacklist_cache_key):
            raise AuthenticationError()

        user_id: int = payload['user_id']

        if self.sso:
            if 'key' not in payload:
                raise AuthenticationError()

            cache_value = bunny_cache.get(self.get_cache_key(user_id))

            if not cache_value or cache_value != payload['key']:
                raise AuthenticationError()

        return user_id

    def ban(self, token: str) -> bool:
        """
        禁用 token

        Args:
            token: token

        Returns:
            bool
        """

        try:
            payload = decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: int = payload['user_id']
            expires_delta: timedelta = payload['exp'] - datetime.now()
            cache_key = self.get_cache_key(token, 'token:blacklist')
            bunny_cache.set(cache_key, user_id, expires_delta.total_seconds())
            return True
        except Exception:
            return False


def get_bunny_token(
    secret_key: str = bunny_config.token_secret_key,
    expires_delta: timedelta | None = None,
    sso: bool = False,
) -> BunnyToken:
    return BunnyToken(secret_key, expires_delta, sso)
