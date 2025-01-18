from pydantic import BaseModel, Field


class MenuCreate(BaseModel):
    parent_id: int = Field(title='父级菜单', ge=0)
    title: str = Field(title='菜单标题', min_length=1, max_length=64)
    path: str = Field(title='菜单路径', min_length=1, max_length=64)
    permission: str = Field(title='菜单权限', min_length=1, max_length=64)
    icon: str = Field(default='', title='菜单图标', max_length=64)
    link: str = Field(default='', title='菜单链接', max_length=255)
    hidden: bool = Field(default=False, title='是否隐藏')
    sort: int = Field(default=0, title='排序', ge=0, le=255)
