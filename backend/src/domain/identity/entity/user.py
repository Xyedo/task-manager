from typing import Optional

from src.common.model import Model


class Pagination(Model):
    lastId: Optional[int] = None
    limit: Optional[int] = 10


class UserResponse(Model):
    accountId: int
    username: str
    fullName: str
    email: str


class UsersResponses(Model):
    users: list[UserResponse]
