import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as ORMEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseModel
from src.users.models import User


class Role(str, Enum):
    USER = '0'
    MODER = '1'
    ADMIN = '2'

    def check_permission(self, other: 'Role') -> bool:
        int_role = int(self.value)
        int_other = int(other.value)
        return int_role >= int_other


class Chat(AsyncAttrs, BaseModel):
    __tablename__ = 'chat'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(length=255), nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id), nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow,
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean, default=False,
    )
    members_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default='1',
    )

    # relation
    owner: 'User' = relationship(
        'User', lazy='select',
    )

    users: list['User'] = relationship(
        'ChatUser', lazy='dynamic',
    )


class ChatUser(AsyncAttrs, BaseModel):
    __tablename__ = 'chat_user'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.id), nullable=False,
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey(Chat.id), nullable=False,
    )
    role: Mapped[Role] = mapped_column(
        ORMEnum(Role), default=Role.USER, server_default=Role.USER.name,
    )
    total_messages: Mapped[int] = mapped_column(
        Integer, default=0, server_default='0',
    )
    last_active: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow,
    )
    is_left: Mapped[bool] = mapped_column(
        Boolean, default=False,
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean, default=False,
    )

    # relation
    chat: 'Chat' = relationship(
        'Chat', lazy='joined', back_populates='users',
    )
    user: 'User' = relationship(
        'User', lazy='select',
    )


class InviteLink(AsyncAttrs, BaseModel):
    __tablename__ = 'invite_link'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    link: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey(Chat.id), nullable=False,
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey(User.id), nullable=False,
    )
    max_uses: Mapped[int] = mapped_column(
        Integer, nullable=True, default=None,
    )
    count_uses: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default='0',
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None,
    )

    # relation
    chat: 'Chat' = relationship(
        'Chat', lazy='joined',
    )
    owner: 'User' = relationship(
        'User', lazy='select',
    )

    def is_expired(self) -> bool:
        expired = self.expires_at is not None and self.expires_at < datetime.datetime.utcnow()
        max_uses = self.max_uses is not None and self.count_uses >= self.max_uses
        return expired or max_uses
