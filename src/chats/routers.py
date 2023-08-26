from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.auth.dependencies import get_current_user
from src.base.schemas import DetailModel, PaginatedResponse
from src.chats.dependencies import get_chat_info, get_chat_service
from src.chats.models import Chat
from src.chats.schemas import ChatDetailedInfo, ChatInfo, ChatInviteLinkDetail
from src.chats.services import ChatService
from src.users.models import User

chat_router = APIRouter(
    prefix='',
)


@chat_router.get(
    '/chats/info/<chat_id>',
    response_model=ChatDetailedInfo,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Token expired or invalid',
        },
        status.HTTP_403_FORBIDDEN: {
            'model': DetailModel,
            'description': 'User has no access to this chat',
        },
        status.HTTP_404_NOT_FOUND: {
            'model': DetailModel,
            'description': 'Chat not found',
        },
    },
)
async def get_chat_info_by_id(
        user: Annotated[User, Depends(get_current_user)],
        chat: Annotated[Chat, Depends(get_chat_info)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    await chat_service.check_access_to_chat(chat.id, user.id)
    return chat


@chat_router.get(
    '/chats/list',
    response_model=PaginatedResponse[ChatInfo],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Token expired or invalid',
        },
    },
)
async def get_chats_list(
        user: Annotated[User, Depends(get_current_user)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_user_chats(user.id)


@chat_router.post(
    '/chats/create',
    response_model=ChatInfo,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Token expired or invalid',
        },
    },
)
async def create_chat(
        chat_name: Annotated[str, Query()],
        user: Annotated[User, Depends(get_current_user)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.create_chat(user.id, chat_name)


@chat_router.get(
    '/chats/<chat_id>/invite_links/',
    response_model=PaginatedResponse[ChatInviteLinkDetail],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Token expired or invalid',
        },
        status.HTTP_403_FORBIDDEN: {
            'model': DetailModel,
            'description': 'You have no privileges to create invite links to this chat',
        },
        status.HTTP_404_NOT_FOUND: {
            'model': DetailModel,
            'description': 'Chat not found',
        },
    },
)
async def get_chat_invite_links(
        user: Annotated[User, Depends(get_current_user)],
        chat: Annotated[Chat, Depends(get_chat_info)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],

        exclude_expired: bool = Query(default=True),
):
    return await chat_service.get_chat_invite_links(chat, user, exclude_expired)


@chat_router.post(
    '/chats/<chat_id>/invite_links/',
    response_model=ChatInviteLinkDetail,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            'model': DetailModel,
            'description': 'Token expired or invalid',
        },
        status.HTTP_403_FORBIDDEN: {
            'model': DetailModel,
            'description': 'You have no privileges to create invite links to this chat',
        },
        status.HTTP_404_NOT_FOUND: {
            'model': DetailModel,
            'description': 'Chat not found',
        },
    },
)
async def create_chat_invite_link(
        user: Annotated[User, Depends(get_current_user)],
        chat: Annotated[Chat, Depends(get_chat_info)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    await chat_service.create_chat_invite_link(chat, user)
