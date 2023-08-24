from dataclasses import dataclass
from typing import Optional, Type

from src.base.exceptions import HTTP_EXC
from src.chats.exceptions import ChatAccessDenied
from src.chats.models import Chat
from src.chats.repositories import ChatRepository


@dataclass
class ChatService:
    chat_repository: ChatRepository

    async def get_chat(self, chat_id: int) -> Chat | None:
        return await self.chat_repository.get_chat(chat_id)

    async def _get_chat_or_error(
            self, chat_id: int, error: Type[HTTP_EXC], detail: Optional[str] = None,
    ):
        chat = await self.get_chat(chat_id)
        if not chat:
            raise error(detail=detail)
        return chat

    async def get_chat_or_404(self, chat_id: int) -> Chat:
        return await self._get_chat_or_error(chat_id, HTTP_EXC.NOT_FOUND)

    async def check_access_to_chat(self, chat_id: int, user_id: int):
        if not await self.chat_repository.has_access_to_chat(chat_id, user_id):
            raise ChatAccessDenied
