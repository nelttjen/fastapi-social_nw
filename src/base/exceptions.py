from fastapi import HTTPException, status


class BadRequest(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Bad request'


class Unauthorized(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Unauthorized'


class Forbidden(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Forbidden'


class NotFound(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Requested resource not found'

