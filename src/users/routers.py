import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_superuser, get_current_superuser_with_groups, get_current_user
from src.base.schemas import DetailModel, SuccessModel
from src.users.dependencies import get_admin_user_service, get_user_or_404, get_user_service
from src.users.models import User
from src.users.schemas import BanData, UserRead, UserUpdate
from src.users.services import AdminUserService, UserService

debugger = logging.getLogger('debugger')


user_router = APIRouter(
    prefix='',
)

admin_user_router = APIRouter(
    prefix='/admin',
)


@user_router.get(
    path='/current',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Bad token provided',
        },
    },
)
async def current_user_get(
    user: Annotated[User, Depends(get_current_user)],
):
    return user


@user_router.patch(
    path='/current',
    response_model=UserRead,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Bad token provided',
        },
        status.HTTP_400_BAD_REQUEST: {
            'model': DetailModel,
            'description': 'Invalid data provided',
        },
        status.HTTP_409_CONFLICT: {
            'model': DetailModel,
            'description': 'Credentials are taken',
        },
    },
)
async def current_user_post(
    update_data: UserUpdate,
    user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.update_user(user, update_data)


@admin_user_router.post(
    path='/ban/<user_id>',
    response_model=SuccessModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': DetailModel,
            'description': 'Invalid data provided',
        },
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Bad token provided',
        },
        status.HTTP_403_FORBIDDEN: {
            'model': DetailModel,
            'description': 'User has no permission to ban',
        },
    },
)
async def admin_ban_user(
        ban_data: BanData,
        user: Annotated[User, Depends(get_current_superuser)],
        user_to_action: Annotated[User, Depends(get_user_or_404)],
        user_service: Annotated[AdminUserService, Depends(get_admin_user_service)],
):
    debugger.debug(f'{ban_data.action} user {user_to_action.username} by {user.username}')

    if ban_data.action == 'ban':
        await user_service.ban_user(user_to_action, user, ban_data)
    elif ban_data.action == 'unban':
        await user_service.unban_user(user_to_action)
    return SuccessModel(success=True)


async def test_groups(
        user: Annotated[User, Depends(get_current_superuser_with_groups)],
):
    for group in user.permission_groups:
        debugger.debug(f'Found user group {group.name} with permissions {group.permissions}')
    return
