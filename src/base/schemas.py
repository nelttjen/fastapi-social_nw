from pydantic import (
    BaseModel, BaseConfig
)


class BaseORMModel(BaseModel):
    class Config(BaseConfig):
        from_attributes = True


class DetailModel(BaseModel):
    detail: str
