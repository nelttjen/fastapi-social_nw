import logging
from typing import List

from sqlalchemy import (JSON, Boolean, Column, ForeignKey, Integer, String,
                        Table)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import BaseModel

info = logging.getLogger('all')


class User(BaseModel):
    __tablename__ = 'user'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
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
    ban_reason: Mapped[str] = mapped_column(
        String(length=1024), nullable=True, default=None,
    )
    banned_by: Mapped[int] = mapped_column(
        ForeignKey(id), nullable=True, default=None,
    )

    # related
    permission_groups: List['PermissionGroup'] = relationship(
        'PermissionGroup', secondary='user_permission_group', back_populates='users',
        lazy='selectin',
    )

    def has_permission(self, permission: str) -> bool:
        try:
            return permission in set([perm for group in self.permission_groups for perm in group.permissions])
        except Exception as e:
            info.error(f'error get user permission: {e}')
            return False


class PermissionGroup(BaseModel):
    __tablename__ = 'permission_group'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(  # noqa
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(length=128), nullable=False,
    )
    permissions: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
    )

    # # related
    users: List['User'] = relationship(
        'User', secondary='user_permission_group', back_populates='permission_groups',
        lazy='selectin',
    )


user_permission_group = Table(
    'user_permission_group',
    BaseModel.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('user_id', Integer, ForeignKey(User.id), nullable=False),
    Column('permission_group_id', Integer, ForeignKey(PermissionGroup.id), nullable=False),
)
