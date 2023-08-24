import logging
from typing import Annotated, Optional

from fastapi import Depends
from jose import JWTError

from src.auth.auth_jwt import AuthTokenType
from src.auth.config import oauth2_scheme
from src.auth.services import AuthService
from src.base.exceptions import Forbidden, Unauthorized
from src.users.dependencies import get_user_service
from src.users.models import User
from src.users.services import UserService

debugger = logging.getLogger('debugger')


async def _get_user_from_token(
        auth_service: AuthService, token: str, checks: Optional[list[str]] = None,
):
    try:
        user = await auth_service.get_user_from_token(token, AuthTokenType.access)
    except JWTError as exc:
        raise Unauthorized('Token expired') from exc

    if user.is_banned:
        msg = 'This user is banned'
        banned_by = await auth_service.user_service.get_user_by_id(user.banned_by)
        if banned_by:
            msg += f' by {banned_by.username}'
        if user.ban_reason:
            msg += f' with reason: {user.ban_reason}'
        raise Forbidden(msg)

    if checks:
        requirements = [getattr(user, check) for check in checks if hasattr(user, check)]
        if not all(requirements):
            raise Forbidden('This user does not have all the required permissions')

    return user


async def get_auth_service(
        user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    return AuthService(user_service)


async def get_current_user(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        access_token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    return await _get_user_from_token(auth_service, access_token)


async def get_current_staff_user(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        access_token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    return await _get_user_from_token(auth_service, access_token, checks=['is_staff'])


async def get_current_superuser(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        access_token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    return await _get_user_from_token(auth_service, access_token, checks=['is_staff', 'is_superuser'])
