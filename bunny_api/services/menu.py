from ..models.bunny import BunnyMenu
from ..schemas.menu import MenuCreate
from ..exceptions import BunnyException


class MenuService:
    @staticmethod
    async def create_menu(menu: MenuCreate) -> None:
        if await BunnyMenu.filter(parent_id=menu.parent_id, path=menu.path).exists():
            raise BunnyException('菜单路径已存在')

        if await BunnyMenu.filter(permission=menu.permission).exists():
            raise BunnyException('菜单权限已存在')

        await BunnyMenu.create(**menu.model_dump())
