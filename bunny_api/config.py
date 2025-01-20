from functools import lru_cache
from typing import Dict, Final

from pydantic_settings import BaseSettings


class BunnyResponseConfig:
    # 默认状态码
    SUCCESS = 0
    ERROR = 1
    ERROR_PARAMS = 2
    UNAUTHORIZED = 1000
    PERMISSION_DENIED = 1001

    # 状态码和消息的映射关系
    _codes = {
        SUCCESS: '操作成功',
        ERROR: '操作失败',
        ERROR_PARAMS: '参数错误',
        UNAUTHORIZED: '未登录或登录过期，请重新登录',
        PERMISSION_DENIED: '无权限',
    }

    @classmethod
    def get_message(cls, code: int) -> str:
        """获取状态码对应的消息"""
        return cls._codes.get(code, '未知错误')

    @classmethod
    def update_codes(cls, codes: Dict[int, str]) -> None:
        """
        更新或添加状态码和消息映射

        Args:
            codes: 状态码和消息的字典
        """
        cls._codes.update(codes)

    @classmethod
    def add_code(cls, code: int, message: str) -> None:
        """
        添加新的状态码和消息

        Args:
            code: 状态码
            message: 消息
        """
        cls._codes[code] = message


class BunnyConfig(BaseSettings):
    env: str = 'dev'

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    admin_token_secret_key: str
    admin_token_expires_seconds: int = 86400
    admin_token_sso: bool = False

    extra_models: str = ''

    cors_allow_origins: str = '*'
    cors_allow_credentials: bool = True
    cors_allow_methods: str = 'GET,POST,PUT,DELETE,OPTIONS'
    cors_allow_headers: str = '*'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False


@lru_cache
def get_config() -> BunnyConfig:
    return BunnyConfig()


def get_db_url(config: BunnyConfig) -> str:
    return f'mysql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}'


@lru_cache
def get_tortoise_orm_config() -> dict:
    models = ['aerich.models', 'bunny_api.models.bunny']

    if bunny_config.extra_models:
        extra_models = bunny_config.extra_models.split(',')
        models.extend(extra_models)

    return {
        'connections': {'default': get_db_url(bunny_config)},
        'apps': {
            'models': {
                'models': models,
                'default_connection': 'default',
            }
        },
    }


bunny_config: Final = get_config()

TORTOISE_ORM: Final = get_tortoise_orm_config()
