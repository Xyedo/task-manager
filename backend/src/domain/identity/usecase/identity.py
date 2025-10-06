from src.infrastructure.security.tokenManager import JwtTokenManager
from src.domain.identity.entity.login import LoginRequest, LoginResponse
from src.domain.identity.entity.logout import RefreshToken
from src.domain.identity.entity.refresh import RefreshResponse
from src.domain.identity.entity.user import Pagination, UserResponse, UsersResponses
from src.infrastructure.database.repository import Repository
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from migrations.schema import Account, Authentication
from src.domain.identity.entity.exception import (
    RefreshTokenNotFound,
    UserNotFound,
    InvalidCredentials,
)
from src.common.token import TokenPayload


class IdentityUsecase:
    __hasher: PasswordHasher
    __repository: Repository
    __token_manager: JwtTokenManager

    def __init__(self):
        self.__hasher = PasswordHasher()
        self.__repository = Repository()
        self.__token_manager = JwtTokenManager()

    def login(self, login_request: LoginRequest) -> LoginResponse:

        with self.__repository.session() as session:
            account = (
                session.query(Account)
                .where(Account.username == login_request.username)
                .first()
            )
            if not account:
                raise UserNotFound()

            try:
                self.__hasher.verify(account.hashed_password, login_request.password)
            except VerifyMismatchError:
                raise InvalidCredentials()

            try:
                if self.__hasher.check_needs_rehash(account.hashed_password):
                    new_hash = self.__hasher.hash(login_request.password)
                    account.hashed_password = new_hash
                    session.add(account)
            except Exception:
                pass

            access_token = self.__token_manager.create_access_token(
                TokenPayload(
                    id=account.account_id,
                    tenant_id=account.tenant_id,
                    username=account.username,
                )
            )
            refresh_token = self.__token_manager.create_refresh_token(
                TokenPayload(
                    id=account.account_id,
                    username=account.username,
                    tenant_id=account.tenant_id,
                )
            )

            auth = Authentication(token=refresh_token)
            session.add(auth)

            return LoginResponse(accessToken=access_token, refreshToken=refresh_token)

    def refresh(self, payload: RefreshToken) -> RefreshResponse:
        with self.__repository.session() as session:
            token_data = self.__token_manager.verify_refresh_token(payload.token)

            auth = (
                session.query(Authentication)
                .where(Authentication.token == payload.token)
                .first()
            )
            if not auth:
                raise RefreshTokenNotFound()

            return RefreshResponse(
                accessToken=self.__token_manager.create_access_token(
                    TokenPayload(
                        user_id=token_data.id,
                        username=token_data.username,
                        tenant_id=token_data.tenant_id,
                    )
                )
            )

    def logout(self, payload: RefreshToken):

        with self.__repository.session() as session:
            auth = (
                session.query(Authentication)
                .where(Authentication.token == payload.token)
                .first()
            )
            if not auth:
                raise RefreshTokenNotFound()

            session.delete(auth)

    def list_users(
        self, payload: TokenPayload, pagination: Pagination
    ) -> UsersResponses:
        with self.__repository.session() as session:
            accounts = (
                session.query(Account)
                .where(
                    
                        Account.tenant_id == payload.tenant_id,
                        Account.account_id
                        > (pagination.lastId if pagination.lastId else 0),
                  
                )
                .order_by(Account.account_id)
                .limit(pagination.limit if pagination.limit else 10)
                .all()
            )


            return UsersResponses(
                users=[
                    UserResponse(
                        accountId=user.account_id,
                        username=user.username,
                        fullName=user.full_name,
                        email=user.email,
                    )
                    for user in accounts
                ]
            )

    def me(self, payload: TokenPayload) -> UserResponse:

        with self.__repository.session() as session:
            account = (
                session.query(Account)
                .where(Account.account_id == payload.user_id)
                .first()
            )
            if not account:
                raise UserNotFound()

            return UserResponse(
                accountId=account.account_id,
                username=account.username,
                fullName=account.full_name,
                email=account.email,
            )
