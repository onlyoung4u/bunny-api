import importlib
import inspect
import os
from pathlib import Path
from typing import List, Type

from bunny_api.commands.base import BaseCommand
from bunny_api.seeder import BaseSeeder


class SeederCommand(BaseCommand):
    """数据填充命令"""

    name = 'seeder'
    help = '数据填充相关命令'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='seeder_action')

        # 创建 seeder
        create_parser = subparsers.add_parser('create', help='创建新的 seeder')
        create_parser.add_argument('name', help='seeder 名称')

        # 运行 seeder
        run_parser = subparsers.add_parser('run', help='运行 seeder')
        run_parser.add_argument('--name', help='指定运行的 seeder 名称')

    async def handle(self, *args, **options):
        action = options.get('seeder_action')

        if action == 'create':
            await self.create_seeder(options['name'])
        elif action == 'run':
            await self.run_seeders(options.get('name'))

    async def create_seeder(self, name: str):
        """创建新的 seeder 文件"""
        # 获取项目根目录下的 seeders 文件夹
        seeders_dir = Path(os.getcwd()) / 'seeders'
        seeders_dir.mkdir(exist_ok=True)

        # 生成 seeder 文件
        file_path = seeders_dir / f'{name}_seeder.py'
        if file_path.exists():
            print(f'Seeder {name} 已存在')
            return

        template = f'''from bunny_api.seeder import BaseSeeder

class {name.title()}Seeder(BaseSeeder):
    """
    {name} 数据填充
    """
    
    async def run(self):
        """
        执行数据填充
        """
        pass
'''

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f'已创建 Seeder: {file_path}')

    async def run_seeders(self, name: str = None):
        """运行 seeder"""
        seeders = []

        # 获取内置 seeder
        built_in_seeders = self.get_built_in_seeders()
        seeders.extend(built_in_seeders)

        # 获取项目 seeder
        project_seeders = await self.get_project_seeders()
        seeders.extend(project_seeders)

        if name:
            seeders = [s for s in seeders if s.__name__.lower() == f'{name.lower()}seeder']
            if not seeders:
                print(f'未找到 Seeder: {name}')
                return

        for seeder_class in seeders:
            seeder = seeder_class()
            print(f'运行 {seeder_class.__name__}...')
            await seeder.run()
            print(f'{seeder_class.__name__} 完成')

    def get_built_in_seeders(self) -> List[Type[BaseSeeder]]:
        """获取内置的 seeders"""
        built_in_dir = Path(__file__).parent.parent / 'seeders'
        return self._load_seeders_from_dir(built_in_dir)

    async def get_project_seeders(self) -> List[Type[BaseSeeder]]:
        """获取项目中的 seeders"""
        project_dir = Path(os.getcwd()) / 'seeders'
        return self._load_seeders_from_dir(project_dir)

    def _load_seeders_from_dir(self, directory: Path) -> List[Type[BaseSeeder]]:
        """从指定目录加载所有 seeder"""
        seeders = []

        if not directory.exists():
            return seeders

        for file in directory.glob('*_seeder.py'):
            module_name = file.stem
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseSeeder) and obj != BaseSeeder:
                    seeders.append(obj)

        return seeders
