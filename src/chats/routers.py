from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.auth.dependencies import get_current_user
from src.base.schemas import DetailModel, PaginatedResponse, SuccessModel, base_401_response
from src.chats.dependencies import get_chat_info, get_chat_links_service, get_chat_service
from src.chats.models import Chat
from src.chats.schemas import ChatDetailedInfo, ChatInfo, ChatInviteLinkData, ChatInviteLinkDetail
from src.chats.services import ChatInviteLinkService, ChatService
from src.users.models import User

chat_router = APIRouter(
    prefix='',
)


@chat_router.get(
    '/info/{chat_id}',
    response_model=ChatDetailedInfo,
    status_code=status.HTTP_200_OK,
    responses={
        **base_401_response,
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
    '/list',
    response_model=PaginatedResponse[ChatInfo],
    status_code=status.HTTP_200_OK,
    responses={
        **base_401_response,
    },
)
async def get_chats_list(
        user: Annotated[User, Depends(get_current_user)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.get_user_chats(user.id)


@chat_router.post(
    '/create',
    response_model=ChatInfo,
    status_code=status.HTTP_201_CREATED,
    responses={
        **base_401_response,
    },
)
async def create_chat(
        chat_name: Annotated[str, Query()],
        user: Annotated[User, Depends(get_current_user)],
        chat_service: Annotated[ChatService, Depends(get_chat_service)],
):
    return await chat_service.create_chat(user.id, chat_name)


@chat_router.get(
    '/{chat_id}/invite_links/',
    response_model=PaginatedResponse[ChatInviteLinkDetail],
    status_code=status.HTTP_200_OK,
    responses={
        **base_401_response,
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
        chat_links_service: Annotated[ChatInviteLinkService, Depends(get_chat_links_service)],

        exclude_expired: bool = Query(default=True),
):
    return await chat_links_service.get_chat_invite_links(chat, user, exclude_expired)


@chat_router.post(
    '/{chat_id}/invite_links/',
    response_model=ChatInviteLinkDetail,
    status_code=status.HTTP_201_CREATED,
    responses={
        **base_401_response,
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
        create_data: ChatInviteLinkData,
        user: Annotated[User, Depends(get_current_user)],
        chat: Annotated[Chat, Depends(get_chat_info)],
        chat_links_service: Annotated[ChatInviteLinkService, Depends(get_chat_links_service)],
):
    return await chat_links_service.create_chat_invite_link(chat, user, create_data)


@chat_router.patch(
    '/chats/invite_links/{link_hash}',
    response_model=ChatInviteLinkDetail,
    status_code=status.HTTP_200_OK,
    responses={
        **base_401_response,
    },
)
async def update_chat_invite_link(
        update_data: ChatInviteLinkData,
):
    return


@chat_router.put(
    '/chats/invite_links/{link_hash}',
    response_model=SuccessModel,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            'model': DetailModel,
            'description': 'Link expired or incorrect',
        },
        **base_401_response,
        status.HTTP_403_FORBIDDEN: {
            'model': DetailModel,
            'description': 'Banned from chat',
        },
        status.HTTP_404_NOT_FOUND: {
            'model': DetailModel,
            'description': 'Link not found',
        },
        status.HTTP_409_CONFLICT: {
            'model': DetailModel,
            'description': 'User already invited to this chat',
        },
    },
)
async def accept_chat_invite_link(
        link_hash: str,
        user: Annotated[User, Depends(get_current_user)],
        chat_links_service: Annotated[ChatInviteLinkService, Depends(get_chat_links_service)],
):
    await chat_links_service.accept_chat_invite_link(link_hash=link_hash, user=user)
    return SuccessModel(success=True)
