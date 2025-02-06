from functools import lru_cache
from typing import List, Type

import bcrypt
from fastapi import Request

from .models.base import BaseModel
from .schemas import PaginationSchema


def bcrypt_pwd(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()


@lru_cache(maxsize=1000)
def verify_bcrypt_pwd(pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), hashed_pwd.encode())


def get_real_ip(request: Request) -> str:
    real_ip = request.headers.get('X-Real-IP')

    if real_ip:
        return real_ip

    x_forwarded_for = request.headers.get('X-Forwarded-For')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()

    return request.client.host


@lru_cache(maxsize=1000)
def str2list(s: str, sep: str = ',') -> List[str]:
    return [item.strip() for item in s.split(sep) if item.strip()]


async def paginate(
    model: Type[BaseModel],
    page: int,
    limit: int,
    related: list[str] | None = None,
    filters: dict | None = None,
    order_by: str | list[str] | None = None,
) -> PaginationSchema:
    """
    通用的分页查询函数

    Args:
        query: Tortoise ORM 的 QuerySet 对象
        page: 页码，从 1 开始
        limit: 每页数据量

    Returns:
        PaginationSchema: 包含当前页的数据列表和总数据量
    """

    offset = (page - 1) * limit

    query = model.filter(**(filters or {}))

    if related:
        query = query.prefetch_related(*related)

    total = await query.count()

    if order_by:
        if isinstance(order_by, str):
            order_by = [order_by]
        query = query.order_by(*order_by)

    query = query.offset(offset).limit(limit)

    items = await model.get_pydantic_queryset_model().from_queryset(query)

    return PaginationSchema(list=items.model_dump(), total=total)
