from argparse import ArgumentParser


class BaseCommand:
    """命令基类"""

    name = ''  # 命令名称
    help = ''  # 命令帮助信息

    def add_arguments(self, parser: ArgumentParser):
        """
        添加命令参数
        子类可以重写此方法来添加自己的参数
        """
        pass

    async def handle(self, *args, **options):
        """
        执行命令
        子类必须实现此方法
        """
        raise NotImplementedError
