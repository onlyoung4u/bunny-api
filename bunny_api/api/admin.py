from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from ..middlewares import permission_check, set_log_body, verify_token
from ..permission import Permission
from ..response import success
from ..schemas import (
    MenuParams,
    PaginationParams,
    ResetPassword,
    ResponseSchema,
    RoleParams,
    UserLogin,
)
from ..services import AuthService, LogsService, MenuService, RoleService
from ..utils import get_real_ip

adminRouter = APIRouter(prefix='/admin', dependencies=[Depends(set_log_body)])
adminRouterWithAuth = APIRouter(
    prefix='/admin',
    dependencies=[Depends(verify_token), Depends(permission_check), Depends(set_log_body)],
)


@adminRouter.post('/login', name='login')
async def login(request: Request, user_login: UserLogin) -> ResponseSchema:
    token = await AuthService.login(user_login, get_real_ip(request))
    return success(token)


@adminRouterWithAuth.post('/logout', name='logout')
async def logout(request: Request) -> ResponseSchema:
    token = request.headers.get('Authorization')
    token = token.replace('Bearer', '').strip()
    await AuthService.logout(token)
    return success()


@adminRouterWithAuth.post('/reset-password')
async def reset_password(request: Request, reset_password: ResetPassword) -> ResponseSchema:
    await AuthService.reset_password(request.state.user_id, reset_password)
    return success()


@adminRouterWithAuth.get('/user/info')
async def user_info(request: Request) -> ResponseSchema:
    user = await AuthService.get_user_info(request.state.user_id)
    return success(user)


@adminRouterWithAuth.get('/permissions')
async def get_permissions(request: Request) -> ResponseSchema:
    permissions = await Permission.get_user_permissions(
        request.state.user_id, Permission.get_flag()
    )
    return success(permissions)


@adminRouterWithAuth.get('/menus')
async def get_menus(request: Request) -> ResponseSchema:
    menus = await MenuService.get_user_menu(request.state.user_id)
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


@adminRouterWithAuth.get('/role', name='role.list')
async def role_list(params: Annotated[PaginationParams, Query()]) -> ResponseSchema:
    roles = await RoleService.list(params)
    return success(roles)


@adminRouterWithAuth.get('/role/{id}', name='role.list')
async def role_detail(id: int) -> ResponseSchema:
    role = await RoleService.detail(id)
    return success(await role.to_pydantic_model())


@adminRouterWithAuth.post('/role', name='role.create')
async def role_create(request: Request, role: RoleParams) -> ResponseSchema:
    await RoleService.create(role, request.state.user_id)
    return success()


@adminRouterWithAuth.put('/role/{id}', name='role.update')
async def role_update(request: Request, id: int, role: RoleParams) -> ResponseSchema:
    await RoleService.update(id, role, request.state.user_id)
    return success()


@adminRouterWithAuth.delete('/role/{id}', name='role.delete')
async def role_delete(request: Request, id: int) -> ResponseSchema:
    await RoleService.delete(id, request.state.user_id)
    return success()


@adminRouterWithAuth.get('/logs', name='logs')
async def logs_list(params: Annotated[PaginationParams, Query()]) -> ResponseSchema:
    logs = await LogsService.list(params)
    return success(logs)
