import time

from .cache import bunny_cache
from .models import BunnyRolePermission, BunnyUserRole
from .models.bunny import BunnyMenu


class Permission:
    @staticmethod
    def get_flag() -> int:
        flag = bunny_cache.get_memory('permission:flag')

        if not flag:
            flag = time.time()
            bunny_cache.set_memory('permission:flag', flag)

        return int(flag)

    @staticmethod
    def refresh() -> None:
        bunny_cache.set_memory('permission:flag', time.time())

    @staticmethod
    async def check_permission(user_id: int, permission: str) -> bool:
        if user_id == 1:
            return True

        permissions = await Permission.get_user_permissions(user_id, Permission.get_flag())

        return permission in permissions

    @staticmethod
    async def get_user_permissions(user_id: int, flag: int) -> list[str]:
        cache_key = f'permission:user:{user_id}:{flag}'

        permissions = bunny_cache.get_memory(cache_key)

        if permissions is not None:
            return permissions

        if user_id == 1:
            permissions = await BunnyMenu.all().values_list('permission', flat=True)
        else:
            role_ids = await BunnyUserRole.filter(user_id=user_id).values_list('role_id', flat=True)

            if not role_ids:
                permissions = []
            else:
                permissions = await BunnyRolePermission.filter(role_id__in=role_ids).values_list(
                    'permission', flat=True
                )

                permissions = list(set(permissions))

        bunny_cache.set_memory(cache_key, permissions)

        return permissions
