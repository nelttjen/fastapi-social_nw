from src.base.exceptions import BadRequest, DataConflict, Forbidden


class ChatAccessDenied(Forbidden):
    detail = 'You are not invited to this chat'


class AlreadyInvited(DataConflict):
    detail = 'You are already invited to this chat'


class UserBannedInChat(Forbidden):
    detail = 'You are banned from this chat'


class InvalidLink(BadRequest):
    detail = 'Link is invalid or expired'
