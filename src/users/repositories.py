from sqlalchemy import or_, select

from src.users.models import User
from src.base.repositories import BaseRepository
from src.users.exceptions import UsernameAlreadyExists, EmailAlreadyExists

from dataclasses import dataclass


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

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.get(User, user_id)
        return result or None

    async def credentials_available(self, email: str, username: str):
        result = await self.session.scalar(
            select(User.username, User.email).where(or_(
                User.email == email,
                User.username.ilike(username.lower()),
            )),
        )
        if result:
            if result.username.lower() == username.lower():
                raise UsernameAlreadyExists
            if result.email == email:
                raise EmailAlreadyExists
