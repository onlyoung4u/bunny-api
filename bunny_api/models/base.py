from typing import Type
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel


class BaseModel(models.Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True, null=True)

    pydantic_model = None
    pydantic_queryset_model = None

    @classmethod
    def get_pydantic_model(cls) -> Type[PydanticModel]:
        if cls.pydantic_model is None:
            cls.pydantic_model = pydantic_model_creator(cls)
        return cls.pydantic_model

    def model_dump(
        self, include: list[str] | None = None, exclude: list[str] | None = None
    ) -> dict:
        return self.get_pydantic_model().model_dump(include=include, exclude=exclude)

    async def to_pydantic_model(self) -> PydanticModel:
        return await self.get_pydantic_model().from_tortoise_orm(self)

    @classmethod
    def get_pydantic_queryset_model(cls) -> Type[PydanticListModel]:
        if cls.pydantic_queryset_model is None:
            cls.pydantic_queryset_model = pydantic_queryset_creator(cls)
        return cls.pydantic_queryset_model

    class Meta:
        abstract = True
