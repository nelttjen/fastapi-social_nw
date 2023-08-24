import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Literal, Optional, TypeVar
from urllib import parse

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import CompoundSelect

from src.base.models import BaseModel as BaseModelSQLAlchemy
from src.config import config

T = TypeVar('T', bound=BaseModelSQLAlchemy | Row)

info = logging.getLogger('all')


class QueryPage(BaseModel):
    results: Sequence[T]

    pages: int
    current_page: int

    items: int
    items_per_page: int

    next_page: Optional[str]
    previous_page: Optional[str]


@dataclass
class Pagination(ABC):
    session: AsyncSession
    page: int
    items_per_page: int

    pages: int
    items: int

    request: Request

    @abstractmethod
    async def _paginate(
            self, query: Select[Iterable[T]] | CompoundSelect,
    ) -> Select[Iterable[T]] | CompoundSelect:
        """Must implement pagicanion."""

    def _get_page(
            self, page_type: Literal['prev', 'next'], current_page: int,
    ) -> Optional[str]:
        if not self.pages:
            info.error('Pages must be calculated before using _get_page method')
            return

        current_page -= 1 if page_type == 'prev' else -1

        if current_page > self.pages or current_page < 1:
            return

        domain = config('DOMAIN', '127.0.0.1:8000')
        protocol = config('PROTOCOL', 'http')
        query_params = parse.urlencode(
            {**self.request.query_params, 'page': str(current_page)},
        )
        return f'{protocol}://{domain}/{self.request.url}?{query_params}'
