from dataclasses import dataclass
from typing import Optional, Type

from src.base.exceptions import HTTP_EXC, NotFound
from src.base.schemas import QueryPage
from src.chats.exceptions import AlreadyInvited, ChatAccessDenied, InvalidLink, UserBannedInChat
from src.chats.models import Chat, ChatUser, Role
from src.chats.repositories import ChatLinkRepository, ChatRepository
from src.chats.schemas import ChatInviteLinkDetail
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

    async def is_user_in_chat(self, chat_id: int, user_id: int) -> bool:
        return await self.chat_repository.has_access_to_chat(chat_id, user_id, Role.USER)

    async def get_user_chats(self, user_id: int) -> QueryPage[Chat]:
        return await self.chat_repository.get_chats_for_user(user_id)

    async def get_chat_user(self, chat_id: int, user_id: int) -> ChatUser | None:
        return await self.chat_repository.get_chat_user(chat_id, user_id)

    async def create_chat(self, user_id: int, chat_name: str) -> Chat:
        return await self.chat_repository.create_chat(user_id, chat_name)


@dataclass
class ChatInviteLinkService:
    links_repository: ChatLinkRepository
    chat_service: ChatService

    async def get_chat_invite_links(
            self, chat: Chat, user: User, exclude_expired: bool = True,
    ):
        await self.chat_service.check_access_to_chat(chat.id, user.id, role=Role.MODER)
        return await self.links_repository.get_chat_links(chat, exclude_expired)

    async def create_chat_invite_link(
            self, chat: Chat, user: User, create_data: ChatInviteLinkDetail,
    ):
        await self.chat_service.check_access_to_chat(chat.id, user.id, role=Role.MODER)
        return await self.links_repository.create_chat_link(
            user.id, chat.id,
            create_data.expired_at, create_data.max_uses,
        )

    async def accept_chat_invite_link(self, link_hash: str, user: User):
        link = await self.links_repository.get_invite_link_or_404(link_hash)

        if link.is_expired():
            raise InvalidLink

        chat_user: ChatUser | None = await self.chat_service.get_chat_user(link.chat_id, user.id)

        if chat_user:
            if chat_user.is_banned:
                raise UserBannedInChat
            if not chat_user.is_left:
                raise AlreadyInvited

        await self.links_repository.add_user_to_chat_by_link(user, chat_user, link)
