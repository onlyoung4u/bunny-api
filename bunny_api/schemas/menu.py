from pydantic import BaseModel, Field, field_validator


class MenuParams(BaseModel):
    parent_id: int = Field(description='父级菜单', ge=0)
    title: str = Field(description='菜单标题', min_length=1, max_length=64)
    path: str = Field(description='菜单路径', min_length=1, max_length=64)
    permission: str = Field(description='菜单权限', min_length=1, max_length=64)
    icon: str = Field(default='', description='菜单图标', max_length=64)
    link: str = Field(default='', description='菜单链接', max_length=255)
    hidden: bool = Field(default=False, description='是否隐藏')
    sort: int = Field(default=0, description='排序', ge=0, le=255)

    @field_validator('path')
    def validate_path(cls, v: str) -> str:
        if not v.startswith('/'):
            raise ValueError('path 必须以 / 开头')
        return v
