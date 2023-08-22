from fastapi import HTTPException, status


class UsernameAlreadyExists(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'User with this username already exists'

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=None,
        )


class EmailAlreadyExists(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'User with this email already exists'

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=None,
        )
