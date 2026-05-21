from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

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
)

app.add_exception_handler(NotFoundException, app_exception_handler)
app.add_exception_handler(ForbiddenException, app_exception_handler)
app.add_exception_handler(UnauthorizedException, app_exception_handler)
app.add_exception_handler(ConflictException, app_exception_handler)
app.add_exception_handler(ValidationException, app_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
