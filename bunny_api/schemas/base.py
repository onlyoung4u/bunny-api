from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from ..config import BunnyResponseConfig

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    code: int = BunnyResponseConfig.SUCCESS
    message: str = ''
    data: Optional[T] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=1000)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginationSchema(BaseModel):
    list: List[Any]
    total: int
