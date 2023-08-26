from dataclasses import dataclass
from typing import Optional, Type

from src.base.exceptions import HTTP_EXC, NotFound
from src.base.schemas import QueryPage
from src.chats.exceptions import ChatAccessDenied
from src.chats.models import Chat, Role
from src.chats.repositories import ChatRepository
from src.users.models import User


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
        return await self._get_chat_or_error(chat_id, NotFound)

    async def check_access_to_chat(self, chat_id: int, user_id: int, role: Role = Role.USER):
        if not await self.chat_repository.has_access_to_chat(chat_id, user_id, role):
            raise ChatAccessDenied

    async def get_user_chats(self, user_id: int) -> QueryPage[Chat]:
        return await self.chat_repository.get_chats_for_user(user_id)

    async def create_chat(self, user_id: int, chat_name: str) -> Chat:
        return await self.chat_repository.create_chat(user_id, chat_name)

    async def get_chat_invite_links(
            self, chat: Chat, user: User, exclude_expired: bool = True,
    ):
        await self.check_access_to_chat(chat.id, user.id, role=Role.MODER)
        return await self.chat_repository.get_chat_links(chat, exclude_expired)
