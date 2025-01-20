from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(description='用户名', min_length=4, max_length=64)
    password: str = Field(description='密码', min_length=8, max_length=64)
