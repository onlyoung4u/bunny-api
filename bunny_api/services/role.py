from typing import List

from tortoise.transactions import in_transaction

from ..exceptions import BunnyException
from ..models.bunny import BunnyMenu, BunnyRole, BunnyRolePermission, BunnyUserRole
from ..permission import Permission
from ..schemas import PaginationParams, PaginationSchema, RoleParams
from ..utils import paginate


class RoleService:
    @staticmethod
    async def list(params: PaginationParams) -> PaginationSchema:
        return await paginate(BunnyRole, params.page, params.limit)

    @staticmethod
    async def detail(id: int) -> BunnyRole:
        role = await BunnyRole.get_or_none(id=id)

        if not role:
            raise BunnyException('未知的角色')

        return role

    @staticmethod
    async def permission_check(permissions: List[str], user_id: int) -> List[str]:
        permissions = list(set(permissions))

        if await BunnyMenu.filter(permission__in=permissions).count() != len(permissions):
            raise BunnyException('存在未知的权限')

        if user_id > 1:
            for permission in permissions:
                if not await Permission.check_permission(user_id, permission):
                    raise BunnyException('权限越级')

        return permissions

    @staticmethod
    async def create(role_params: RoleParams, user_id: int) -> None:
        if await BunnyRole.filter(name=role_params.name).exists():
            raise BunnyException('角色名称已存在')

        permissions = await RoleService.permission_check(role_params.permissions, user_id)

        async with in_transaction():
            role = await BunnyRole.create(name=role_params.name, creator_id=user_id)

            permission_list = []
            for permission in permissions:
                permission_list.append(BunnyRolePermission(role_id=role.id, permission=permission))

            await BunnyRolePermission.bulk_create(permission_list)

    @staticmethod
    async def update(id: int, role_params: RoleParams, user_id: int) -> None:
        filters = {'creator_id': user_id} if user_id > 1 else {}
        if not await BunnyRole.filter(id=id, **filters).exists():
            raise BunnyException('角色不存在')

        if await BunnyRole.filter(name=role_params.name, id__not=id).exists():
            raise BunnyException('角色名称已存在')

        permissions = await RoleService.permission_check(role_params.permissions, user_id)

        async with in_transaction():
            await BunnyRole.filter(id=id).update(name=role_params.name)

            await BunnyRolePermission.filter(role_id=id).delete()

            permission_list = []
            for permission in permissions:
                permission_list.append(BunnyRolePermission(role_id=id, permission=permission))

            await BunnyRolePermission.bulk_create(permission_list)

        Permission.refresh()

    @staticmethod
    async def delete(id: int, user_id: int) -> None:
        filters = {'creator_id': user_id} if user_id > 1 else {}
        if not await BunnyRole.filter(id=id, **filters).exists():
            raise BunnyException('角色不存在')

        async with in_transaction():
            await BunnyRole.filter(id=id).delete()
            await BunnyRolePermission.filter(role_id=id).delete()
            await BunnyUserRole.filter(role_id=id).delete()

        Permission.refresh()
