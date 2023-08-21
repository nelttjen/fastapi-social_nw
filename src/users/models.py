from typing import List

from sqlalchemy import (
    Boolean, Column, ForeignKey, Integer, JSON, String, Table,
)
from sqlalchemy.orm import (
    Mapped, mapped_column, relationship,
)

from src.base.models import (
    BaseModel, base_metadata,
)

# user = Table(
#     'user',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('username', String(length=128), unique=True, nullable=False, index=True),
#     Column('email', String(length=320), unique=True, nullable=False, index=True),
#     Column('password', String(length=1024), nullable=False),
#     Column('is_active', Boolean, default=False, nullable=False),
#     Column('is_staff', Boolean, default=False, nullable=False),
#     Column('is_superuser', Boolean, default=False, nullable=False),
#     Column('is_banned', Boolean, default=False, nullable=False),
# )
# permission_group = Table(
#     'permission_group',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('name', String(length=128), nullable=False),
#     Column('permissions', JSON, nullable=False, default=list),
# )
#
# user_permission_group = Table(
#     'user_permission_group',
#     base_metadata,
#     Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
#     Column('user_id', Integer, ForeignKey(user.c.id), nullable=False),
#     Column('permission_group_id', Integer, ForeignKey(permission_group.c.id), nullable=False),
# )


class User(BaseModel):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(length=128), unique=True, index=True, nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
    )
    is_staff: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )

    # related
    permission_groups: Mapped[List['PermissionGroup']] = relationship(
        'PermissionGroup', secondary='user_permission_group', back_populates='users',
    )


class PermissionGroup(BaseModel):
    __tablename__ = 'permission_group'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(length=128), nullable=False,
    )
    permissions: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
    )

    # related
    users: Mapped[List['User']] = relationship(
        'User', secondary='user_permission_group', back_populates='permission_group',
    )


class UserPermissionGroups(BaseModel):
    __tablename__ = 'user_permission_group'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(User.id), nullable=False,
    )
    permission_group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(PermissionGroup.id), nullable=False,
    )