from pydantic import BaseModel, Field


class RoleParams(BaseModel):
    name: str = Field(description='角色名称', min_length=1, max_length=64)
    permissions: list[str] = Field(description='角色权限')
