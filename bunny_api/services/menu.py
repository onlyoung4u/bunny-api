from typing import List

from tortoise.transactions import in_transaction

from ..exceptions import BunnyException
from ..models import BunnyMenu, BunnyRolePermission
from ..permission import Permission
from ..schemas import MenuParams


class MenuService:
    @staticmethod
    async def list() -> List[dict]:
        menus = await BunnyMenu.all().order_by('sort', 'id')
        return MenuService.handle_menu_tree(menus, False)

    @staticmethod
    async def create(menu: MenuParams) -> None:
        if menu.parent_id > 0:
            if not await BunnyMenu.filter(id=menu.parent_id, path__isnull=False).exists():
                raise BunnyException('父级菜单不存在')

        if menu.path and await BunnyMenu.filter(parent_id=menu.parent_id, path=menu.path).exists():
            raise BunnyException('路径已存在')

        if await BunnyMenu.filter(permission=menu.permission).exists():
            raise BunnyException('权限已存在')

        await BunnyMenu.create(**menu.model_dump())

        Permission.refresh()

    @staticmethod
    async def update(id: int, menu: MenuParams) -> None:
        if not await BunnyMenu.filter(id=id, is_system=False).exists():
            raise BunnyException('菜单不存在')

        if menu.parent_id > 0:
            if menu.parent_id == id:
                raise BunnyException('父级菜单不能是自身')

            if not await BunnyMenu.filter(id=menu.parent_id, path__isnull=False).exists():
                raise BunnyException('父级菜单不存在')

        if (
            menu.path
            and await BunnyMenu.filter(
                parent_id=menu.parent_id, path=menu.path, id__not=id
            ).exists()
        ):
            raise BunnyException('路径已存在')

        if await BunnyMenu.filter(permission=menu.permission, id__not=id).exists():
            raise BunnyException('权限已存在')

        await BunnyMenu.filter(id=id).update(**menu.model_dump())

        Permission.refresh()

    @staticmethod
    async def delete(id: int) -> None:
        if not await BunnyMenu.filter(id=id, is_system=False).exists():
            raise BunnyException('菜单不存在')

        ids = [id, *(await MenuService.get_all_children(id))]

        async with in_transaction():
            permissions = (
                await BunnyMenu.filter(id__in=ids).all().values_list('permission', flat=True)
            )

            await BunnyMenu.filter(id__in=ids).delete()

            await BunnyRolePermission.filter(permission__in=permissions).delete()

        Permission.refresh()

    @staticmethod
    async def get_all_children(id: int, visited: set | None = None) -> List[int]:
        if visited is None:
            visited = set()

        if id in visited:
            return []

        visited.add(id)

        list = await BunnyMenu.filter(parent_id=id).all()
        ids = [item.id for item in list]

        for item in list:
            ids.extend(await MenuService.get_all_children(item.id, visited))

        return ids

    @staticmethod
    def handle_menu_data(menu: BunnyMenu, handle: bool, path: str) -> dict:
        if not handle:
            return menu.model_dump()

        full_path = path + menu.path

        if path:
            component = full_path
        else:
            component = 'BasicLayout'

        meta = {'title': menu.title}

        if menu.icon:
            meta['icon'] = menu.icon

        return {
            'component': component,
            'meta': meta,
            'name': menu.permission,
            'path': full_path,
        }

    @staticmethod
    def handle_menu_tree(
        menus: List[BunnyMenu], handle: bool = True, parent_id: int = 0, path: str = ''
    ) -> List[dict]:
        tree: List[dict] = []

        for menu in menus:
            if menu.parent_id == parent_id:
                tree_item = MenuService.handle_menu_data(menu, handle, path)

                children = MenuService.handle_menu_tree(menus, handle, menu.id, path + menu.path)
                if children:
                    tree_item['children'] = children

                tree.append(tree_item)

        return tree

    @staticmethod
    async def get_user_menu(user_id: int, handle: bool = True) -> List[dict]:
        menus: List[BunnyMenu] = []

        filters = {} if handle else {'hidden': False}

        if user_id == 1:
            menus = await BunnyMenu.filter(**filters).order_by('sort', 'id')
        else:
            permissions = await Permission.get_user_permissions(user_id, Permission.get_flag())

            if permissions:
                menus = (
                    await BunnyMenu.filter(**filters)
                    .filter(permission__in=permissions)
                    .order_by('sort', 'id')
                )

        return MenuService.handle_menu_tree(menus, handle)
