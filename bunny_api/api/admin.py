from fastapi import APIRouter, Depends, Request

from ..middlewares import permission_check, set_log_body, verify_token
from ..response import success
from ..schemas import MenuCreate, ResponseSchema, UserLogin
from ..services import AuthService, MenuService

adminRouter = APIRouter(prefix='/admin', dependencies=[Depends(set_log_body)])
adminRouterWithAuth = APIRouter(
    prefix='/admin',
    dependencies=[Depends(verify_token), Depends(permission_check), Depends(set_log_body)],
)


@adminRouter.post('/login', name='login')
async def login(user_login: UserLogin) -> ResponseSchema:
    token = await AuthService.login(user_login)
    return success(token)


@adminRouterWithAuth.get('/menus')
async def get_menus(request: Request) -> ResponseSchema:
    user_id = request.state.user_id
    menus = await MenuService.get_user_menu(user_id)
    return success(menus)


@adminRouterWithAuth.post('/menu', name='menu.create')
async def create_menu(menu: MenuCreate) -> ResponseSchema:
    await MenuService.create_menu(menu)
    return success()
