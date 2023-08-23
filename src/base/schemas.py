from pydantic import BaseConfig, BaseModel


class BaseORMModel(BaseModel):
    class Config(BaseConfig):
        from_attributes = True


class DetailModel(BaseModel):
    detail: str


class SuccessModel(BaseModel):
    success: bool
