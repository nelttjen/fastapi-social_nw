import datetime
from typing import Optional

from pydantic import BaseModel

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
    expires_at: Optional[datetime.datetime]

    max_uses: Optional[int]
    count_uses: int


class ChatInviteLinkData(BaseModel):
    max_uses: Optional[int]
    expired_at: Optional[datetime.datetime]
