from src.base.exceptions import Forbidden


class ChatAccessDenied(Forbidden):
    detail = 'You are not invited to this chat'
