from typing import Optional

from pydantic import BaseModel


class Pagination(BaseModel):
    lastId: Optional[int] = None
    limit: Optional[int] = 10


class UserResponse(BaseModel):
    accountId: int
    username: str
    fullName: str
    email: str


class UsersResponses(BaseModel):
    users: list[UserResponse]
