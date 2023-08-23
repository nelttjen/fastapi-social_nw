import re
import warnings
from dataclasses import dataclass
from typing import Optional, Type

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from src.auth.config import pwd_context
from src.base.exceptions import HTTP_EXC, BadRequest, NotFound, Unauthorized
from src.config import config
from src.users.exceptions import (EmailValidationError,
                                  PasswordValidationError,
                                  UsernameOrEmailAlreadyExists,
                                  UsernameValidationError)
from src.users.models import User
from src.users.repositories import UserRepository
from src.users.schemas import BanData, UserUpdate


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

        await RegisterService.password_validator(username=username, email=email, password=password)
        # await RegisterService.email_validator(email=email)
        await RegisterService.username_validator(username=username)

        hashed_password = await RegisterService.make_password_hash(password=password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )
        await self.user_repository.create(user)
        await self.user_repository.commit()

        return user

    async def update_user(
            self,
            user: User,
            update_data: UserUpdate,
    ):
        if update_data.username:
            await RegisterService.username_validator(username=update_data.username)
            user.username = update_data.username

        if update_data.email:
            await RegisterService.email_validator(email=update_data.email)
            user.email = update_data.email

        if update_data.password and update_data.old_password:
            if not await RegisterService.check_password_hash(update_data.old_password, user.password):
                raise PasswordValidationError('Old password does not match')

            await RegisterService.password_validator(
                username=user.username, email=user.email, password=update_data.password,
            )
            user.password = await RegisterService.make_password_hash(password=update_data.password)

        try:
            await self.user_repository.update(user)
        except IntegrityError as e:
            raise UsernameOrEmailAlreadyExists('username or email already exists') from e

        return user

    async def get_user_for_login(self, query: str) -> User | None:
        return await self.user_repository.find_for_login(search=query)

    async def get_user_by_id(self, user_id: int, with_groups: bool = False) -> User | None:
        return await self.user_repository.get_by_id(user_id=user_id, with_groups=with_groups)

    async def _get_user_or_exception(
            self, user_id: int, exception: Type[HTTP_EXC], detail: Optional[str] = None,
    ) -> User | None:
        user = await self.get_user_by_id(user_id=user_id)

        if not user:
            if detail:
                exception = exception(detail)

            raise exception

        return user

    async def get_user_or_401(
            self, user_id: int, detail: Optional[str] = None,
    ) -> User:
        return await self._get_user_or_exception(user_id, Unauthorized, detail)

    async def get_user_or_404(
            self, user_id: int, detail: Optional[str] = None,
    ) -> User:
        return await self._get_user_or_exception(user_id, NotFound, detail)


@dataclass
class AdminUserService:
    user_repository: UserRepository

    async def ban_user(
            self, user, banned_by: User, ban_data: BanData,
    ) -> None:
        if user.id == banned_by.id:
            raise BadRequest('You cannot ban yourself')
        if user.is_superuser:
            raise BadRequest('You cannot ban a superuser')

        user.is_banned = True
        user.banned_by = banned_by.id
        user.ban_reason = ban_data.ban_reason

        await self.user_repository.update(user)

    async def unban_user(self, user: User) -> None:
        if not user.is_banned:
            return

        user.is_banned = False
        user.banned_by = None
        user.ban_reason = None
        await self.user_repository.update(user)


@dataclass
class RegisterService:

    @staticmethod
    async def password_validator(
            username: str, email: str, password: str,
    ) -> None:
        if config('DISABLE_PASSWORD_VALIDATOR', False, module='src.auth.config'):
            return

        if username in password or email in password:
            raise PasswordValidationError('Password cannot contains username or email')

        if not 6 <= len(password) <= 50:
            raise PasswordValidationError('Password must be between 6 and 50 characters long')

        regex_password = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[\d#@$=_+*&^%]).+$')
        if not regex_password.match(password):
            raise PasswordValidationError('Password must contain at least one uppercase letter, lower case letter, '
                                          'and at least one number or special character (#@$=_+*&^%)')

    @staticmethod
    async def email_validator(email: EmailStr) -> None:
        warnings.warn(
            stacklevel=2,
            category=DeprecationWarning,
            message="This func is deprecated, use 'PyDantic' 'EmailStr' instead",
        )

        regex_email = re.compile(r'^[\w-]+@([\w-]+\.)+[\w-]{2,4}$')
        if not regex_email.match(email):
            raise EmailValidationError

    @staticmethod
    async def username_validator(username: str) -> None:
        regex_username = re.compile(r'^[a-zA-Z0-9_-]{4,32}$')
        if not regex_username.match(username):
            raise UsernameValidationError('Username must be between 4 and 32 characters long, '
                                          'and can contain only letters, numbers and dashes')

    @staticmethod
    async def make_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    async def check_password_hash(
            plain_password: str, hashed_password: str,
    ) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
