from fastapi.responses import JSONResponse
from src.domain.identity.entity import exception as identity_exception
from src.domain.workspaces.entity import exception as workspace_exception
from src.infrastructure.security.tokenManager import JwtExpired, InvalidJwtToken
from src.infrastructure.http.guarded import AuthException
def register_error_handlers(app):
    @app.exception_handler(identity_exception.UserNotFound)
    def user_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "User not found"},
        )

    @app.exception_handler(identity_exception.InvalidCredentials)
    def invalid_credentials_exception_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid credentials"},
        )

    @app.exception_handler(identity_exception.RefreshTokenNotFound)
    def invalid_token_exception_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"},
        )

    @app.exception_handler(workspace_exception.WorkspaceNotFound)
    def workspace_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Workspace not found"},
        )

    @app.exception_handler(workspace_exception.GroupNotFound)
    def group_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Group not found"},
        )

    @app.exception_handler(workspace_exception.TaskNotFound)
    def task_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Task not found"},
        )

    @app.exception_handler(JwtExpired)
    def jwt_expired_exception_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "JWT token has expired"},
        )
    
    @app.exception_handler(InvalidJwtToken)
    def invalid_jwt_token_exception_handler(request, exc):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid JWT token"},
        )


    @app.exception_handler(AuthException)
    def auth_exception_handler(request, exc):
        resp = JSONResponse(
            status_code=401,
            content={"detail": exc.message},
        )
        resp.delete_cookie(key="access_token")
        resp.delete_cookie(key="refresh_token")
        return resp
