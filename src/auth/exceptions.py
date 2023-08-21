from src.base.exceptions import Unauthorized


class BasCredentialsException(Unauthorized):
    detail = 'Invalid credentials provided'
    headers = {'WWW-Authenticate': 'Bearer'}
