import os

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

JWT_SECRET = os.environ.get('JWT_SECRET', 'insecure-jwt-secret---ie--vtoga')
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 15

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')