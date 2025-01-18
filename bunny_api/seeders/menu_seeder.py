from bunny_api.models import BunnyMenu
from bunny_api.seeder import BaseSeeder


class MenuSeeder(BaseSeeder):
    """
    填充菜单
    """

    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_HANDLE = 'handle'

    ALL_ACTIONS = [ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE, ACTION_HANDLE]

    ACTIONS_LABELS = {
        ACTION_CREATE: '添加',
        ACTION_UPDATE: '修改',
        ACTION_DELETE: '删除',
        ACTION_HANDLE: '处理',
    }

    def get_action(
        self,
        parent_id: int,
        permission_prefix: str,
        actions: list[str] = [ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE],
    ) -> list[BunnyMenu]:
        actions_menu = []

        for action in actions:
            if action not in self.ALL_ACTIONS:
                continue

            actions_menu.append(
                BunnyMenu(
                    parent_id=parent_id,
                    title=self.ACTIONS_LABELS[action],
                    path='',
                    permission=f'{permission_prefix}.{action}',
                    hidden=True,
                )
            )

        return actions_menu

    async def run(self):
        # 系统设置-菜单
        system_menu = await BunnyMenu.create(
            parent_id=0,
            title='系统设置',
            path='/system',
            permission='system',
            icon='material-symbols:settings',
            sort=99,
        )

        # 系统设置-用户管理
        user_menu = await BunnyMenu.create(
            parent_id=system_menu.id, title='用户管理', path='/users', permission='user.list'
        )
        await BunnyMenu.bulk_create(self.get_action(user_menu.id, 'user'))

        # 系统设置-角色管理
        role_menu = await BunnyMenu.create(
            parent_id=system_menu.id, title='角色管理', path='/roles', permission='role.list'
        )
        await BunnyMenu.bulk_create(self.get_action(role_menu.id, 'role'))

        # 系统设置-菜单管理
        menu_menu = await BunnyMenu.create(
            parent_id=system_menu.id, title='菜单管理', path='/menus', permission='menu.list'
        )
        await BunnyMenu.bulk_create(self.get_action(menu_menu.id, 'menu'))

        # 系统设置-系统配置
        await BunnyMenu.create(
            parent_id=system_menu.id, title='系统配置', path='/settings', permission='settings'
        )

        # 系统设置-配置管理
        config_menu = await BunnyMenu.create(
            parent_id=system_menu.id, title='配置管理', path='/configs', permission='config.list'
        )
        await BunnyMenu.bulk_create(self.get_action(config_menu.id, 'config'))

        # 系统设置-操作日志
        await BunnyMenu.create(
            parent_id=system_menu.id, title='操作日志', path='/logs', permission='logs'
        )
