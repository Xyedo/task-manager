from src.common.model import Model


class LoginRequest(Model):
    username: str
    password: str


class LoginResponse(Model):
    accessToken: str
    refreshToken: str
