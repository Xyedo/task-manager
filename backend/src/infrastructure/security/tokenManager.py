import time
import jwt
import os
from src.common.token import TokenPayload
import uuid


class JwtTokenManager:
    __access_token_secret: str
    __refresh_token_secret: str
    __access_token_expiry_seconds: int
    __refresh_token_expiry_seconds: int

    def __init__(self):
        self.__access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
        self.__refresh_token_secret = os.environ.get("REFRESH_TOKEN_SECRET")
        self.__access_token_expiry_seconds = os.environ.get(
            "ACCESS_TOKEN_EXPIRY_SECONDS", 60
        )  # 1 minute
        self.__refresh_token_expiry_seconds = os.environ.get(
            "REFRESH_TOKEN_EXPIRY_SECONDS", 60 * 60 * 24 * 30
        )  # 30 days

    def create_access_token(self, data: TokenPayload) -> str:

        payload = data.model_dump()
        payload["iat"] = int(time.time())
        if os.environ.get("ENV") == "production":
            payload["exp"] = int(time.time()) + self.__access_token_expiry_seconds
        return jwt.encode(payload, self.__access_token_secret, algorithm="HS256")

    def create_refresh_token(self, data: TokenPayload) -> str:

        payload = data.model_dump()
        payload["iat"] = int(time.time())
        payload["jti"] = str(uuid.uuid4())
        if os.environ.get("ENV") == "production":
            payload["exp"] = int(time.time()) + self.__refresh_token_expiry_seconds

        return jwt.encode(payload, self.__refresh_token_secret, algorithm="HS256")

    def verify_refresh_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token, self.__refresh_token_secret, algorithms=["HS256"]
            )
            return TokenPayload.model_validate(payload)

        except jwt.ExpiredSignatureError:
            raise JwtExpired()
        except jwt.InvalidTokenError:
            raise InvalidJwtToken()


class JwtExpired(Exception):
    def __init__(self, message="JWT token has expired"):
        self.message = message
        super().__init__(self.message)


class InvalidJwtToken(Exception):
    def __init__(self, message="Invalid JWT token"):
        self.message = message
        super().__init__(self.message)
