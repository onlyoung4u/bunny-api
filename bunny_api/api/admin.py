from fastapi import APIRouter, Depends, Request

from ..middlewares import permission_check, set_log_body, verify_token
from ..response import success
from ..schemas import MenuParams, ResponseSchema, UserLogin
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


@adminRouterWithAuth.get('/menu', name='menu.list')
async def menu_list() -> ResponseSchema:
    menus = await MenuService.list()
    return success(menus)


@adminRouterWithAuth.post('/menu', name='menu.create')
async def menu_create(menu: MenuParams) -> ResponseSchema:
    await MenuService.create(menu)
    return success()


@adminRouterWithAuth.put('/menu/{id}', name='menu.update')
async def menu_update(id: int, menu: MenuParams) -> ResponseSchema:
    await MenuService.update(id, menu)
    return success()


@adminRouterWithAuth.delete('/menu/{id}', name='menu.delete')
async def menu_delete(id: int) -> ResponseSchema:
    await MenuService.delete(id)
    return success()
