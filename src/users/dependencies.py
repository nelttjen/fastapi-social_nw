from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.users.models import User
from src.users.repositories import UserRepository
from src.users.services import AdminUserService, UserService


async def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_user_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


async def get_admin_user_service(
        repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> AdminUserService:
    return AdminUserService(repository)


async def get_user_or_404(
        service: Annotated[UserService, Depends(get_user_service)],
        user_id: int,
) -> User:
    return await service.get_user_or_404(user_id)
