from abc import ABC
from dataclasses import dataclass
from typing import (
    Generic, TypeVar,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.base.models import BaseModel

T = TypeVar('T', bound=BaseModel)


@dataclass
class BaseRepository(ABC, Generic[T]):
    session: AsyncSession

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def bulk_create(self, objs: list[T]) -> list[T]:
        self.session.add_all(objs)
        await self.session.commit()
        return objs

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.commit()

    async def update(self, obj: T) -> None:
        await self.session.merge(obj)
        await self.session.commit()

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
