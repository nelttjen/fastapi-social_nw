from typing import List

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import (Boolean, Column, ForeignKey, Integer, JSON, MetaData, String, Table)
from sqlalchemy.orm import (
    DeclarativeMeta, Mapped, declarative_base, mapped_column, relationship,
)

Base: DeclarativeMeta = declarative_base()
auth_metadata = MetaData()

permission_groups = Table(
    'permission_groups',
    auth_metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('name', String(length=128), nullable=False),
    Column('permissions', JSON, nullable=False, default=dict),
)

users = Table(
    'users',
    auth_metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('username', String(length=128), unique=True, nullable=False, index=True),
    Column('email', String(length=320), unique=True, index=True, nullable=False),
    Column('hashed_password', String(length=1024), nullable=False),
    Column('is_active', Boolean, default=True, nullable=False),
    Column('is_superuser', Boolean, default=False, nullable=False),
    Column('is_verified', Boolean, default=False, nullable=False),

)

user_permission_groups = Table(
    'user_permission_groups',
    auth_metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('permission_group_id', Integer, ForeignKey('permission_groups.id'), nullable=False),
)


class PermissionGroups(Base):
    __tablename__ = 'permission_groups'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(length=128), nullable=False,
    )
    permissions: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict,
    )

    # users: Mapped[List['Users']] = relationship(
    #     'Users', secondary=user_permission_groups, back_populates='permission_groups',
    # )


class Users(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'users'

    # fastapi-users default
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False,
    )

    # custom fields
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(length=128), unique=True, index=True, nullable=False,
    )

    # permission_groups: Mapped[List['PermissionGroups']] = relationship(
    #     'PermissionGroups', secondary=user_permission_groups, back_populates='users',
    # )

