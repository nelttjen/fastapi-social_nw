from dataclasses import dataclass

from pydantic import EmailStr

from src.users.repositories import UserRepository
from src.users.models import User
from src.auth.config import pwd_context


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
