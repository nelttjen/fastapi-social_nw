from src.app import app
from src.auth.routers import auth_router
from src.users.routers import user_router

app.include_router(
    auth_router,
    prefix='/api/auth',
    tags=['auth'],
)

app.include_router(
    user_router,
    prefix='/api/users',
    tags=['users'],
)