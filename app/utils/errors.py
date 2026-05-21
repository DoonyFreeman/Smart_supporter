from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail


class NotFoundException(AppException):
    status_code: int = 404
    detail: str = "Resource not found"


class ForbiddenException(AppException):
    status_code: int = 403
    detail: str = "Forbidden"


class UnauthorizedException(AppException):
    status_code: int = 401
    detail: str = "Unauthorized"


class ConflictException(AppException):
    status_code: int = 409
    detail: str = "Conflict"


class ValidationException(AppException):
    status_code: int = 422
    detail: str = "Validation error"


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, AppException):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
