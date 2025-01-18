from bunny_api.models.bunny import BunnyUser
from bunny_api.seeder import BaseSeeder
from bunny_api.utils import bcrypt_pwd


class UserSeeder(BaseSeeder):
    """
    填充超级管理员
    """

    async def run(self):
        await BunnyUser.create(username='admin', nickname='超级管理员', password=bcrypt_pwd('luckybunny'))
