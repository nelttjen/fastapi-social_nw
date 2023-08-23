import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

from src.base.schemas import BaseORMModel


class UserBaseModel(BaseORMModel):
    username: str
    email: EmailStr


class UserCreate(UserBaseModel):
    password: str


class UserRead(UserBaseModel):
    id: int  # noqa: A003, VNE003
    is_active: bool
    is_superuser: bool
    is_staff: bool


class UserUpdate(BaseORMModel):
    username: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None)
    old_password: Optional[str] = Field(default=None)


class BanData(BaseModel):
    action: Literal['ban', 'unban']
    ban_reason: Optional[str] = Field(default=None)
    ban_until: Optional[datetime.datetime] = Field(default=None)
