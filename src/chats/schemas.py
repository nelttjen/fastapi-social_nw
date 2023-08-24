from src.base.schemas import BaseORMModel


class ChatInfo(BaseORMModel):
    id: int  # noqa


class ChatDetailedInfo(ChatInfo):
    pass
