from dataclasses import dataclass

from jose import jwt, JWTError
from src.users.services import UserService


@dataclass
class AuthService:
    user_service: UserService

    @staticmethod
    def _parse_token():
        pass