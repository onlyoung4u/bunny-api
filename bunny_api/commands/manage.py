import argparse
import asyncio
import sys
from typing import List, Type

from tortoise import Tortoise

from bunny_api.commands import commands
from bunny_api.commands.base import BaseCommand
from bunny_api.config import TORTOISE_ORM


async def main(argv: List[str]):
    parser = argparse.ArgumentParser(description='Bunny API 管理工具')
    subparsers = parser.add_subparsers(dest='command')

    # 注册所有命令
    command_instances: List[Type[BaseCommand]] = []
    for command_class in commands:
        command = command_class()
        command_instances.append(command)
        command.add_arguments(subparsers.add_parser(command.name, help=command.help))

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return

    # 初始化数据库连接
    await Tortoise.init(TORTOISE_ORM)

    # 执行对应的命令
    for command in command_instances:
        if command.name == args.command:
            await command.handle(**vars(args))
            break

    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))
