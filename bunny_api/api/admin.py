from fastapi import APIRouter

from ..response import success
from ..schemas.base import ResponseSchema
from ..schemas.menu import MenuCreate
from ..services.menu import MenuService

adminRouter = APIRouter(prefix='/admin')


@adminRouter.post('/menu')
async def create_menu(menu: MenuCreate) -> ResponseSchema:
    await MenuService.create_menu(menu)
    return success()
