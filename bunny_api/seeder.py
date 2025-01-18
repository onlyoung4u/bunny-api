class BaseSeeder:
    """Seeder 基类"""

    async def run(self):
        """
        执行数据填充
        子类必须实现此方法
        """
        raise NotImplementedError
