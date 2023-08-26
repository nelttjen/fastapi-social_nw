from src.app import app
from src.auth.routers import auth_router
from src.chats.routers import chat_router
from src.users.routers import admin_user_router, user_router

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

app.include_router(
    admin_user_router,
    prefix='/api/users',
    tags=['admin'],
)

app.include_router(
    chat_router,
    prefix='/api/chats',
    tags=['chats'],
)
