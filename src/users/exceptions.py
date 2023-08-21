from fastapi import HTTPException, status


class UsernameAlreadyExists(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'User with this username already exists'


class EmailAlreadyExists(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'User with this email already exists'


BadCredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Invalid username or password.',
    headers={'WWW-Authenticate': 'Bearer'},
)