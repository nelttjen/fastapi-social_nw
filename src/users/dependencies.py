from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.users.repositories import UserRepository
from src.users.services import UserService


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)
