from typing import Annotated
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from migrations.schema import Account
from src.common.token import TokenPayload
from src.domain.identity.entity.user import Pagination, UserResponse, UsersResponses
from src.infrastructure.http.guarded import get_current_user, get_refresh_token
from src.domain.identity.entity.logout import RefreshToken
from src.domain.identity.entity.refresh import RefreshResponse
from src.domain.identity.usecase.identity import IdentityUsecase
from src.domain.identity.entity.login import LoginRequest, LoginResponse
import os

router = APIRouter(prefix="/identity", tags=["identity"])


@router.post("/login")
def login(
    login: LoginRequest,
    response: Response,
    identity_usecase: Annotated[IdentityUsecase, Depends()],
) -> LoginResponse:
    resp = identity_usecase.login(login)

    if os.environ.get("ENV", "DEV") == "DEV":
        response.set_cookie(
            key="access_token", value=resp.accessToken, httponly=True, samesite="lax"
        )

    response.set_cookie(
        key="refresh_token", value=resp.refreshToken, httponly=True, samesite="strict"
    )

    return resp


@router.put("/refresh")
def refresh(
    response: Response,
    refresh_token: Annotated[RefreshToken, Depends(get_refresh_token)],
    identity_usecase: Annotated[IdentityUsecase, Depends(IdentityUsecase)],
) -> RefreshResponse:
    resp = identity_usecase.refresh(refresh_token)

    if os.environ.get("ENV", "DEV") == "DEV":
        response.set_cookie(
            key="access_token", value=resp.accessToken, httponly=True, samesite="lax"
        )

    return resp


@router.delete("/logout", status_code=204)
def logout(
    response: Response,
    refresh_token: Annotated[RefreshToken, Depends(get_refresh_token)],
    identity_usecase: Annotated[IdentityUsecase, Depends(IdentityUsecase)],
) -> None:
    identity_usecase.logout(refresh_token)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return None


@router.get("/users")
def list_users(
    identity_usecase: Annotated[IdentityUsecase, Depends(IdentityUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
    pagination: Annotated[Pagination, Depends(Pagination)],
) -> UsersResponses:
    return identity_usecase.list_users(auth, pagination)


@router.get("/me")
def me(
    identity_usecase: Annotated[IdentityUsecase, Depends(IdentityUsecase)],
    auth: Annotated[TokenPayload, Depends(get_current_user)],
) -> UserResponse:
    return identity_usecase.me(auth)
