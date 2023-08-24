from dataclasses import dataclass
from typing import Optional

from sqlalchemy import and_, exists, select

from src.base.repositories import BaseRepository
from src.chats.models import Chat, ChatUser


@dataclass
class ChatRepository(BaseRepository[Chat]):
    async def has_access_to_chat(self, chat_id: int, user_id: int) -> bool:
        return await self.session.scalar(
            select(exists()).where(and_(
                ChatUser.chat_id == chat_id,
                ChatUser.user_id == user_id,
                ChatUser.is_banned == bool(False),
                ChatUser.is_left == bool(False),
            )),
        )

    async def get_chat(self, chat_id: int) -> Chat | None:
        return await self.session.get(Chat, chat_id) or None

    async def get_chat_users(
            self, chat_id: int, filter_by: Optional[dict],
    ) -> list[ChatUser]:
        stmt = select(ChatUser).where(ChatUser.chat_id == chat_id)
        if filter_by:
            stmt = stmt.filter_by(**filter_by)
        stmt.order_by(ChatUser.last_active.desc())

        return list(await self.session.scalars(stmt))

    async def get_chat_banned_users(self, chat_id: int) -> list[ChatUser]:
        return await self.get_chat_users(chat_id, filter_by={'is_banned': True})
