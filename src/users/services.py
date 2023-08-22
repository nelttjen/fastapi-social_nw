from dataclasses import dataclass

from pydantic import EmailStr

from src.users.repositories import UserRepository
from src.users.models import User
from src.auth.config import pwd_context
from src.base.exceptions import Unauthorized


@dataclass
class UserService:
    user_repository: UserRepository

    async def create_user(
            self,
            username: str,
            email: EmailStr,
            password: str,
    ) -> User:
        await self.user_repository.credentials_available(email=email, username=username)

        hashed_password = await self.make_password_hash(password=password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )
        await self.user_repository.create(user)
        await self.user_repository.commit()

        return user

    @staticmethod
    async def make_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def check_password_hash(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    async def get_user_for_login(self, query: str) -> User | None:
        return await self.user_repository.find_for_login(search=query)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.get_by_id(user_id=user_id)

    async def get_user_or_401(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id=user_id)
        if not user:
            raise Unauthorized
        return user
