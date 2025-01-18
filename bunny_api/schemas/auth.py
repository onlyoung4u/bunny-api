from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(title='用户名', min_length=4, max_length=64)
    password: str = Field(title='密码', min_length=8, max_length=64)
