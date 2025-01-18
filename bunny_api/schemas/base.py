from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

from ..config import BunnyResponseConfig

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    code: int = BunnyResponseConfig.SUCCESS
    message: str = ''
    data: Optional[T] = None
