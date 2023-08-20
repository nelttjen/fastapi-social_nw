import logging
from typing import (
    Any, AsyncGenerator, Optional, Union,
)

from fastapi import (
    Depends, Request,
)
from fastapi_users import (
    BaseUserManager, IntegerIDMixin,
)
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from src.auth.dependencies import get_user_db
from src.auth.models import Users
from src.auth.schemas import UserCreate
from src.config import config

debugger = logging.getLogger('debugger')

transport = BearerTransport(tokenUrl='api/auth/jwt/login')
SECRET = config('JWT_SECRET', module='src.auth.config')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name='jwt-authentication',
    transport=transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[Users, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
            self, user: Users, request: Optional[Request] = None,
    ) -> None:
        debugger.debug(f'User {user.username} registered ')

    async def on_after_request_verify(
        self, user: Users, token: str, request: Optional[Request] = None,
    ) -> None:
        debugger.debug('Verifying token for %d id: %s' % (user.id, token))

    async def validate_password(
        self, password: str, user: Union[UserCreate, Users],
    ) -> None:
        pass


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)) -> AsyncGenerator[UserManager, Any]:
    yield UserManager(user_db=user_db)
