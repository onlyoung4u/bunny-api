import asyncio
import sys

from .commands.manage import main


def cli():
    asyncio.run(main(sys.argv[1:]))


if __name__ == '__main__':
    cli()
