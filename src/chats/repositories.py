import datetime
import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError

from src.base.paginations import BaseLimitPagination
from src.base.repositories import BaseRepository
from src.base.schemas import QueryPage
from src.chats.models import Chat, ChatUser, InviteLink, Role

debugger = logging.getLogger('debugger')


@dataclass
class ChatRepository(BaseRepository[Chat]):
    paginator: BaseLimitPagination | None

    async def has_access_to_chat(self, chat_id: int, user_id: int, role: Role = Role.USER) -> bool:
        role_user: Role | None = await self.session.scalar(
            select(ChatUser.role).where(and_(
                ChatUser.chat_id == chat_id,
                ChatUser.user_id == user_id,
                ChatUser.is_banned == bool(False),
                ChatUser.is_left == bool(False),
            )),
        ) or None
        if not role_user:
            return False

        return role_user.check_permission(role)

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

    async def get_chats_for_user(self, user_id: int) -> QueryPage[Chat]:
        return await self.paginator.apply_pagination(
            select(Chat).outerjoin(
                ChatUser, ChatUser.chat_id == Chat.id,
            ).where(ChatUser.user_id == user_id),
            query_type='model',
        )

    async def get_chat_links(self, chat: Chat, exclude_expired: bool = True) -> QueryPage[InviteLink]:
        stmt = select(InviteLink).where(InviteLink.chat_id == chat.id)
        if exclude_expired:
            stmt = stmt.where(or_(
                InviteLink.expires_at > datetime.datetime.utcnow(),
                InviteLink.count_uses == InviteLink.max_uses,
            ))

        return await self.paginator.apply_pagination(
            stmt, query_type='model',
        )

    async def create_chat(self, user_id: int, chat_name: str) -> Chat:
        try:
            chat = Chat(
                name=chat_name, # noqa
                owner_id=user_id, # noqa
            )
            self.session.add(chat)
            await self.flush()
            debugger.debug(f'{chat.id=}')

            chat_user = ChatUser(
                user_id=user_id, chat_id=chat.id, # noqa
                role=Role.ADMIN, # noqa
            )
            self.session.add(chat_user)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise exc

        return chat
