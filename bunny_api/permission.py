import time
from functools import lru_cache

from .cache import bunny_cache
from .models import BunnyUser


class Permission:
    @staticmethod
    def get_flag() -> int:
        flag = bunny_cache.get('permission:flag')

        if not flag:
            flag = time.time()
            bunny_cache.set('permission:flag', flag)

        return int(flag)

    @staticmethod
    def refresh_flag() -> None:
        bunny_cache.set('permission:flag', time.time())

    @staticmethod
    async def check_permission(user_id: int, permission: str) -> bool:
        if user_id == 1:
            return True

        permissions = await Permission.get_user_permissions(user_id, Permission.get_flag())

        return permission in permissions

    @lru_cache
    @staticmethod
    async def get_user_permissions(user_id: int, flag: int) -> list[str]:
        user = (
            await BunnyUser.filter(id=user_id, is_active=True, is_deleted=False)
            .prefetch_related('roles')
            .first()
        )

        if not user:
            return []

        permissions = list(
            set([permission for role in user.roles for permission in role.permissions])
        )

        return permissions
