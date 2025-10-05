import os
from fastapi import Request
import jwt
from src.domain.identity.entity.logout import RefreshToken
from src.common.token import TokenPayload
from src.infrastructure.security.tokenManager import JwtTokenManager


class AuthException(Exception):
    def __init__(
        self, message="Authentication credentials were not provided or are invalid"
    ):
        self.message = message
        super().__init__(self.message)


def get_current_user(request: Request) -> TokenPayload:
    token = request.cookies.get("access_token")
    if token:
        res = jwt.decode(
            token, os.environ.get("ACCESS_TOKEN_SECRET"), algorithms=["HS256"]
        )
        return TokenPayload.model_validate(res)

    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ", maxsplit=1)[1]
        if token:
            res = jwt.decode(
                token, os.environ.get("ACCESS_TOKEN_SECRET"), algorithms=["HS256"]
            )
            return TokenPayload.model_validate(res)

    raise AuthException()


def get_refresh_token(request: Request) -> RefreshToken:
    token = request.cookies.get("refresh_token")
    if token:
        return RefreshToken(token=token)

    raise AuthException()
