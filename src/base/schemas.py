from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from fastapi import status
from pydantic import BaseConfig, BaseModel
from sqlalchemy.engine import Row

from src.base.models import BaseModel as BaseModelSQLAlchemy

T = TypeVar('T', bound=BaseModelSQLAlchemy | Row)
TSQL = TypeVar('TSQL', bound=BaseModelSQLAlchemy)


class BaseORMModel(BaseModel):
    class Config(BaseConfig):
        from_attributes = True


class DetailModel(BaseModel):
    detail: str


class SuccessModel(BaseModel):
    success: bool


@dataclass
class QueryPage(Generic[T]):
    results: Sequence[T]

    pages: int
    current_page: int

    items: int
    items_per_page: int

    next_page: Optional[str]
    previous_page: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class PaginatedResponse(BaseModel, Generic[TSQL]):
    results: list[TSQL]

    pages: int
    current_page: int

    items: int
    items_per_page: int

    next_page: Optional[str]
    previous_page: Optional[str]

    class Config:
        arbitrary_types_allowed = True


base_401_response = {
    status.HTTP_401_UNAUTHORIZED: {
        'model': DetailModel,
        'desctiption': 'Token expired or incorrect',
    },
}
