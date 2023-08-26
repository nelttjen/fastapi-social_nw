from typing import Annotated, AsyncGenerator

from fastapi import Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.paginations import BaseLimitPagination
from src.database import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_limit_paginator(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        page: int = Query(default=1),
        per_page: int = Query(default=20),
) -> BaseLimitPagination:
    if page < 1:
        page = 1
    if not 1 <= per_page < 50:
        per_page = 20
    return BaseLimitPagination(request=request, page=page, items_per_page=per_page, session=session)
