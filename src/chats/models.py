import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as ORMEnum
from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseModel
from src.users.models import User


class Role(str, Enum):
    USER = '0'
    MODER = '1'
    ADMIN = '2'


# chat = Table(
#     'chat',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('name', String(length=255), nullable=False),
#     Column('owner_id', Integer, ForeignKey(user.c.id), nullable=False),
#     Column('created_at', DateTime, default=datetime.datetime.utcnow),
#     Column('is_closed', Boolean, default=False),
#     Column('members_count', Integer, nullable=False, default=1, server_default='1'),
# )
#
# chat_user = Table(
#     'chat_user',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('user_id', Integer, ForeignKey(user.c.id), nullable=False),
#     Column('chat_id', Integer, ForeignKey(chat.c.id), nullable=False),
#     Column('role', ORMEnum(Role), default=Role.USER, server_default=Role.USER.name),
#     Column('total_messages', Integer, default=0, server_default='0'),
#     Column('last_active', DateTime, default=datetime.datetime.utcnow),
#     Column('is_left', Boolean, default=False),
#     Column('is_banned', Boolean, default=False),
# )
#
# invite_link = Table(
#     'invite_link',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('link', Uuid, nullable=False),
#     Column('chat_id', Integer, ForeignKey(chat.c.id)),
#     Column('owner_id', Integer, ForeignKey(user.c.id)),
#     Column('max_uses', Integer, nullable=True, default=None),
#     Column('count_uses', Integer, nullable=False, default=0, server_default='0'),
#     Column('created_at', DateTime, default=datetime.datetime.utcnow),
#     Column('expires_at', DateTime, nullable=True, default=None),
# )


class Chat(BaseModel):
    __tablename__ = 'chat'

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
    owner: Mapped['User'] = relationship(
        'User',
    )


class ChatUser(BaseModel):
    __tablename__ = 'chat_user'

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
    chat: Mapped['Chat'] = relationship(
        'Chat',
    )
    user: Mapped['User'] = relationship(
        'User',
    )


class InviteLink(BaseModel):
    __tablename__ = 'invite_link'

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    link: Mapped[str] = mapped_column(
        Uuid, nullable=False,
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
    chat: Mapped['Chat'] = relationship(
        'Chat',
    )
    owner: Mapped['User'] = relationship(
        'User',
    )
