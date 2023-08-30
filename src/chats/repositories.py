import datetime
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional, Type

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError

from src.base.exceptions import HTTP_EXC, NotFound
from src.base.paginations import BaseLimitPagination
from src.base.repositories import BaseRepository
from src.base.schemas import QueryPage
from src.chats.models import Chat, ChatUser, InviteLink, Role
from src.users.models import User

debugger = logging.getLogger('debugger')


@dataclass
class ChatRepository(BaseRepository[Chat | ChatUser]):
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

    async def get_chat_user(self, chat_id: int, user_id: int) -> ChatUser | None:
        stmt = select(ChatUser).where(and_(
            ChatUser.chat_id == chat_id,
            ChatUser.user_id == user_id,
        ))
        return await self.session.scalar(stmt) or None

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


@dataclass
class ChatLinkRepository(BaseRepository[InviteLink]):
    paginator: BaseLimitPagination | None

    async def get_chat_links(self, chat: Chat, exclude_expired: bool = True) -> QueryPage[InviteLink]:
        stmt = select(InviteLink).where(InviteLink.chat_id == chat.id)
        if exclude_expired:
            stmt = stmt.where(or_(
                or_(InviteLink.expires_at > datetime.datetime.utcnow(), InviteLink.expires_at == None),  # noqa
                or_(InviteLink.count_uses == InviteLink.max_uses, InviteLink.max_uses == None),  # noqa
            ))

        return await self.paginator.apply_pagination(
            stmt, query_type='model',
        )

    async def create_chat_link(
            self, user_id: int, chat_id: int,
            expired_at: Optional[datetime.datetime] = None, max_uses: Optional[int] = None,
    ):
        link_hash = hashlib.sha256(f'{user_id}:{chat_id}:{datetime.datetime.utcnow()}'.encode()).hexdigest()[:30]
        invite_link = InviteLink(
            link=link_hash,
            chat_id=chat_id,
            owner_id=user_id,
            expires_at=expired_at,
            max_uses=max_uses,
        )
        invite_link = await self.create(invite_link)
        return invite_link

    async def _get_invite_link(self, link_hash: str, exception: Type[HTTP_EXC]) -> InviteLink | None:
        stmt = select(InviteLink).where(InviteLink.link == link_hash)
        result: InviteLink | None = await self.session.scalar(stmt) or None
        if not result:
            raise exception
        return result

    async def get_invite_link_or_404(self, link_hash: str) -> InviteLink | None:
        return await self._get_invite_link(link_hash, NotFound)

    async def add_user_to_chat_by_link(self, user: User, chat_user: ChatUser | None, link: InviteLink) -> None:
        if chat_user:
            chat_user.is_left = False
        else:
            chat_user = ChatUser(
                chat_id=link.chat_id,
                user_id=user.id,
            )
            self.session.add(chat_user)

        link.count_uses += 1
        await self.session.commit()
