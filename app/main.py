from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import auth, tickets, users
from app.config import settings
from app.database import engine
from app.utils.errors import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    app_exception_handler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(
    title="Automated Tech-Support Triager",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(tickets.router, prefix=settings.API_V1_PREFIX)

app.add_exception_handler(NotFoundException, app_exception_handler)
app.add_exception_handler(ForbiddenException, app_exception_handler)
app.add_exception_handler(UnauthorizedException, app_exception_handler)
app.add_exception_handler(ConflictException, app_exception_handler)
app.add_exception_handler(ValidationException, app_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
