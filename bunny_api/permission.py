import time
from functools import lru_cache

from .cache import bunny_cache
from .models import BunnyUserRole, BunnyRolePermission


class Permission:
    @staticmethod
    def get_flag() -> int:
        flag = bunny_cache.get('permission:flag')

        if not flag:
            flag = time.time()
            bunny_cache.set('permission:flag', flag)

        return int(flag)

    @staticmethod
    def refresh() -> None:
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
        role_ids = await BunnyUserRole.filter(user_id=user_id).values_list('role_id', flat=True)

        if not role_ids:
            return []

        permissions = await BunnyRolePermission.filter(role_id__in=role_ids).values_list(
            'permission', flat=True
        )

        return list(set(permissions))
