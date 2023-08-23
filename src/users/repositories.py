import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from src.base.exceptions import NotFound
from src.base.repositories import BaseRepository
from src.users.exceptions import UsernameOrEmailAlreadyExists
from src.users.models import User

debugger = logging.getLogger('debugger')


@dataclass
class UserRepository(BaseRepository[User]):
    async def find_for_login(self, search: str) -> User | None:
        result = await self.session.scalar(
            select(User).where(or_(
                User.username.ilike(search.lower()),
                User.email == search,
            )),
        )

        return result or None

    async def get_by_id(self, user_id: int, with_groups: bool = False) -> User | None:
        stmt = select(User).where(User.id == user_id)
        if with_groups:
            stmt = stmt.options(
                selectinload(User.permission_groups),
            )
        result = await self.session.scalar(stmt)
        return result or None

    async def credentials_available(
            self, email: str, username: str, not_by: Optional[int] = None,
    ) -> None:
        stmt = select(User.username, User.email).where(or_(
            User.email == email,
            User.username.ilike(username.lower()),
        ))

        if not_by is not None:
            stmt = stmt.where(User.id != not_by)

        result = await self.session.execute(stmt)
        if not (result := result.fetchone()):
            return

        db_username, db_email = result

        if db_username or db_email:
            if db_username.lower() == username.lower():
                raise UsernameOrEmailAlreadyExists('username already taken')
            if db_email == email:
                raise UsernameOrEmailAlreadyExists('email already taken')

    async def get_user_or_404(self, user_id: int) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFound('user not found')
        return user
