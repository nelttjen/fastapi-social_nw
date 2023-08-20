from typing import Optional

from fastapi_users import schemas

from src.schemas import BaseORMModel


class UserRead(schemas.BaseUser[int], BaseORMModel):
    id: int
    email: str
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False