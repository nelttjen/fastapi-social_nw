import datetime

from src.auth.schemas import UserRead
from src.base.schemas import BaseORMModel


class ChatInfo(BaseORMModel):
    id: int  # noqa


class ChatDetailedInfo(ChatInfo):
    pass


class ChatInviteLink(BaseORMModel):
    id: int  # noqa
    link: str

    expires_at: datetime.datetime

    chat: ChatInfo


class ChatInviteLinkDetail(ChatInviteLink):
    owner: UserRead
    expires_at: datetime.datetime

    max_uses: int
    count_uses: int
