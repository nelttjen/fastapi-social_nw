from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.chats.repositories import ChatRepository
from src.chats.services import ChatService
from src.database import get_async_session


async def get_chat_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return ChatRepository(session)


async def get_chat_service(
        chat_repository: Annotated[ChatRepository, Depends(get_chat_repository)],
):
    return ChatService(chat_repository)


async def get_chat_info(
        chat_id: int,
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_chat_or_404(chat_id)
