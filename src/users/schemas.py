from src.base.schemas import BaseORMModel


class UserBaseModel(BaseORMModel):
    username: str
    email: str


class UserCreate(UserBaseModel):
    password: str


class UserRead(UserBaseModel):
    id: int  # noqa: A003, VNE003
    is_active: bool
    is_superuser: bool
    is_staff: bool
