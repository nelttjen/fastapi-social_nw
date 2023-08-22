import datetime
import logging
from dataclasses import dataclass
from typing import Any

from jose import jwt, JWTError

from src.users.models import User
from src.users.services import UserService
from src.users.schemas import UserCreate
from src.auth.auth_jwt import AuthTokenType, generate_tokens
from src.auth.config import JWT_SECRET
from src.auth.exceptions import BadCredentialsException, BadTokenException


debugger = logging.getLogger('debugger')


@dataclass
class AuthService:
    user_service: UserService

    @staticmethod
    def _parse_token(  # noqa: FNE008
            token: str, token_type: AuthTokenType,
    ) -> dict:
        payload = jwt.decode(
            token=token,
            key=JWT_SECRET,
            algorithms=['HS256'],
        )

        user_id = payload.get('user_id')
        username = payload.get('username')
        expires = payload.get('expires')
        token_type_payload = payload.get('token_type')

        if not all([user_id, username, expires, token_type_payload]):
            debugger.debug('bad payload')
            raise JWTError

        correct = token_type_payload == token_type.name
        expired = datetime.datetime.fromisoformat(expires) < datetime.datetime.utcnow()

        if not correct or expired:
            debugger.debug(f'{correct=} {expired=} {expires=}')
            raise JWTError

        return {
            'user_id': user_id,
            'username': username,
            'expires': expires,
            'token_type': token_type,
        }

    async def get_user_from_token(
            self, token: str, token_type: AuthTokenType,
    ) -> User:
        data = self._parse_token(token=token, token_type=token_type)
        user = await self.user_service.get_user_by_id(user_id=data['user_id'])
        return user

    async def authenticate_user(
        self, username: str, password: str,
    ) -> dict[str, Any]:
        user = await self.user_service.get_user_for_login(query=username)
        if not user:
            raise BadCredentialsException
        if not await self.user_service.check_password_hash(password, user.password):
            raise BadCredentialsException

        return {'user': user, **generate_tokens(user)}

    async def refresh_tokens(
        self, refresh_token: str,
    ) -> dict[str, Any]:
        try:
            user = await self.get_user_from_token(refresh_token, AuthTokenType.refresh)
            return {'user': user, **generate_tokens(user)}
        except JWTError:
            raise BadTokenException

    async def validate_access_token(self, access_token: str):
        try:
            self._parse_token(access_token, AuthTokenType.access)
        except JWTError as exc:
            raise BadTokenException from exc

    async def register_user(
        self, new_user: UserCreate,
    ) -> dict[str, Any]:
        user = await self.user_service.create_user(
            username=new_user.username,
            email=new_user.email,
            password=new_user.password,
        )
        return {'user': user, **generate_tokens(user)}
