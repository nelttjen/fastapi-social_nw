import logging
from enum import Enum
from datetime import timedelta, datetime

import jwt

from src.config import config
from src.users.models import User

debugger = logging.getLogger('debugger')

SECRET = config('JWT_SECRET', module='src.auth.config')
AUTH_TOKEN_EXPIRES = timedelta(minutes=config('ACCESS_TOKEN_EXPIRE_MINUTES', module='src.auth.config'))
REFRESH_TOKEN_EXPIRES = timedelta(minutes=config('REFRESH_TOKEN_EXPIRE_MINUTES', module='src.auth.config'))


class AuthTokenType(str, Enum):
    access = 'access_token'
    refresh = 'refresh_token'


def _create_token(user: User, token_type: AuthTokenType, expires: timedelta) -> str:
    payload = {
        'user_id': user.id,
        'username': user.username,
        'token_type': token_type.name,
        'expires': (datetime.utcnow() + expires).isoformat(),
    }
    return jwt.encode(
        payload=payload,
        key=SECRET,
        algorithm='HS256',
    )


def create_access_token(user: User) -> str:
    return _create_token(user, AuthTokenType.access, expires=AUTH_TOKEN_EXPIRES)


def create_refresh_token(user: User) -> str:
    return _create_token(user, AuthTokenType.refresh, expires=REFRESH_TOKEN_EXPIRES)


def generate_tokens(user: User) -> dict[str, str]:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        AuthTokenType.access: access_token,
        AuthTokenType.refresh: refresh_token,
    }
