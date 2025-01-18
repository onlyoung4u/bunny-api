from ..exceptions import BunnyException
from ..models import BunnyMenu
from ..permission import Permission
from ..schemas import MenuCreate


class MenuService:
    @staticmethod
    async def create_menu(menu: MenuCreate) -> None:
        if menu.path and await BunnyMenu.filter(parent_id=menu.parent_id, path=menu.path).exists():
            raise BunnyException('菜单路径已存在')

        if await BunnyMenu.filter(permission=menu.permission).exists():
            raise BunnyException('菜单权限已存在')

        await BunnyMenu.create(**menu.model_dump())

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
        menus: list[BunnyMenu], handle: bool = True, parent_id: int = 0, path: str = ''
    ) -> list[dict]:
        tree = []

        for menu in menus:
            if menu.parent_id == parent_id and (not handle or (handle and menu.hidden is False)):
                tree_item = MenuService.handle_menu_data(menu, handle, path)

                children = MenuService.handle_menu_tree(menus, handle, menu.id, path + menu.path)
                if children:
                    tree_item['children'] = children

                tree.append(tree_item)

        return tree

    @staticmethod
    async def get_user_menu(user_id: int, handle: bool = True) -> list[dict]:
        menus = []

        if user_id == 1:
            menus = await BunnyMenu.all().order_by('sort', 'id')
        else:
            permissions = await Permission.get_user_permissions(user_id, Permission.get_flag())

            if permissions:
                menus = await BunnyMenu.filter(permission__in=permissions).order_by('sort', 'id')

        return MenuService.handle_menu_tree(menus, handle)
