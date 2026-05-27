import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.llm_provider import close_http_client
from app.api.v1 import auth, tickets, users
from app.config import settings
from app.database import engine
from app.middleware import RequestContextMiddleware
from app.utils.errors import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    app_exception_handler,
)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await close_http_client()
    await engine.dispose()


app = FastAPI(
    title="Automated Tech-Support Triager",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
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


@app.get("/health", tags=["meta"], include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}
