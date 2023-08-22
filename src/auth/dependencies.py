import logging
from typing import Annotated

from fastapi import Depends

from src.users.models import User
from src.users.services import UserService
from src.users.dependencies import get_user_service
from src.auth.services import AuthService
from src.auth.auth_jwt import AuthTokenType
from src.auth.config import oauth2_scheme


debugger = logging.getLogger('debugger')


async def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    debugger.debug(auth_service)
    return await auth_service.get_user_from_token(access_token, AuthTokenType.access)