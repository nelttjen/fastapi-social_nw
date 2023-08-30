import logging
import math
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal, Optional
from urllib import parse

from fastapi import Request
from sqlalchemy import Select, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import CompoundSelect
from sqlalchemy.sql.functions import count

from src.base.schemas import QueryPage, T
from src.config import config

info = logging.getLogger('all')


@dataclass
class BaseLimitPagination:
    session: AsyncSession
    page: int
    items_per_page: int

    pages: Optional[int] = field(default=None, init=False)
    items: Optional[int] = field(default=None, init=False)

    request: Request

    async def _paginate(
            self, query: Select[Iterable[T]] | CompoundSelect,
    ) -> Select[Iterable[T]] | CompoundSelect:
        if self.items is None or self.pages is None:
            raise ValueError('call _calculate_items_pages() before paginating query')

        return query.offset(
            (self.page - 1) * self.items_per_page,
        ).limit(
            self.items_per_page,
        )

    def _get_page(
            self, current_page: int,
    ) -> Optional[str]:
        if self.pages is None:
            info.error('call _calculate_items_pages() before using _get_page method')
            return

        if current_page > self.pages or current_page < 1:
            return

        domain = config('DOMAIN', '127.0.0.1:8000')
        protocol = config('PROTOCOL', 'http')
        query_params = parse.urlencode(
            {**self.request.query_params, 'page': str(current_page)},
        )
        return f'{protocol}://{domain}{self.request.url.path}?{query_params}'

    async def _calculate_items_pages(
            self, query: Select[Iterable[T]] | CompoundSelect,
    ) -> None:
        result = await self.session.scalar(
            select(count()).select_from(query.subquery()),
        )
        self.items = result or 0
        self.pages = math.ceil(self.items / self.items_per_page)

    async def apply_pagination(
            self,
            query: Select[Iterable[T]] | Select[Iterable[Row]] | CompoundSelect,
            query_type: Literal['model', 'mixed'] = 'model',
    ) -> QueryPage[T] | QueryPage[Row]:
        await self._calculate_items_pages(query)
        paginated_query = await self._paginate(query)
        if query_type == 'model':
            results = (await self.session.scalars(paginated_query)).all()
        elif query_type == 'mixed':
            results = (await self.session.execute(paginated_query)).all()
        else:
            raise ValueError('query_type must be "model" or "mixed"')

        return QueryPage(
            results=results,
            pages=self.pages,
            current_page=self.page,
            items=self.items,
            items_per_page=self.items_per_page,
            next_page=self._get_page(self.page + 1),
            previous_page=self._get_page(self.page - 1),
        )
