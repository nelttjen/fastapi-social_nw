from fastapi import FastAPI
from fastapi_users import FastAPIUsers

from src.config import config
from src.logging import init_loggers
from src.auth.schemas import (
    UserRead, UserCreate,
)
from src.auth.auth_jwt import (
    auth_backend, get_user_manager,
)
from src.auth.models import Users

init_loggers()

app = FastAPI(debug=config('DEBUG', False))
fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend]
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/api/auth/jwt',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/api/auth',
    tags=['auth'],
)