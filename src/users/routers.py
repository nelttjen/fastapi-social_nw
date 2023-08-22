from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.schemas import UserRead
from src.users.models import User

user_router = APIRouter(
    prefix='',
)


@user_router.get(
    path='/current',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'description': 'Bad token provided',
        },
    },
)
async def current_user(  # noqa: FNE008
    user: Annotated[User, Depends(get_current_user)],
):
    return user
