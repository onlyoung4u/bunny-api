from fastapi import APIRouter, Depends, Request

from ..middlewares import verify_token
from ..response import success
from ..schemas import MenuCreate, ResponseSchema, UserLogin
from ..services import AuthService, MenuService

adminRouter = APIRouter(prefix='/admin')
adminRouterWithAuth = APIRouter(prefix='/admin', dependencies=[Depends(verify_token)])


@adminRouter.post('/login')
async def login(user_login: UserLogin) -> ResponseSchema:
    token = await AuthService.login(user_login)
    return success(token)


@adminRouterWithAuth.get('/menus')
async def get_menus(request: Request) -> ResponseSchema:
    user_id = request.state.user_id
    menus = await MenuService.get_user_menu(user_id)
    return success(menus)


@adminRouterWithAuth.post('/menu')
async def create_menu(menu: MenuCreate) -> ResponseSchema:
    await MenuService.create_menu(menu)
    return success()
