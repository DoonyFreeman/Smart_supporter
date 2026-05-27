import asyncio
import os
import re
from collections.abc import AsyncGenerator, Generator
from typing import Any

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)

from app.config import settings as _settings
from app.database import get_db
from app.main import app
from app.models import Base, User, UserRole
from app.utils.security import hash_password

# Detect if running inside Docker (postgres hostname resolves) or on host
_INSIDE_DOCKER = os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER") == "true"
if not _INSIDE_DOCKER:
    _settings.DATABASE_URL = _settings.DATABASE_URL.replace("@postgres:", "@localhost:")
_settings.LLM_STUB = True
_settings.LLM_API_URL = "http://localhost:11434/api/generate"

# CRITICAL: tests run destructive schema operations (drop_all). They MUST NOT
# touch the production database. Redirect to a dedicated test database — its
# name is the production db name + "_test" — and create it if missing.
_PROD_URL = _settings.DATABASE_URL
_TEST_DB_NAME = re.sub(r"/([^/?]+)(\?|$)", r"/\1_test\2", _PROD_URL).rsplit("/", 1)[-1]
_TEST_DB_URL = re.sub(r"/[^/?]+(\?|$)", f"/{_TEST_DB_NAME}\\1", _PROD_URL)
# Also point app.config at the test DB so endpoints hit by the TestClient
# read/write to the same isolated database.
_settings.DATABASE_URL = _TEST_DB_URL


def _ensure_test_database_exists() -> None:
    """Create the test database if it doesn't exist (uses asyncpg directly)."""
    # Strip SQLAlchemy driver prefix, swap db name to "postgres" to issue CREATE DATABASE.
    raw = _PROD_URL.replace("postgresql+asyncpg://", "postgresql://")
    admin_url = re.sub(r"/[^/?]+(\?|$)", "/postgres\\1", raw)

    async def _do() -> None:
        conn = await asyncpg.connect(admin_url)
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", _TEST_DB_NAME
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{_TEST_DB_NAME}"')
        finally:
            await conn.close()

    asyncio.run(_do())


_ensure_test_database_exists()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    e = create_async_engine(
        _TEST_DB_URL,
        echo=False,
        poolclass=NullPool,
    )
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(
            __import__("sqlalchemy").text("DROP TABLE IF EXISTS alembic_version")
        )
        await conn.run_sync(Base.metadata.create_all)
    yield e
    async with e.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await e.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)
    await session.begin_nested()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_data() -> dict[str, Any]:
    return {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "Test User",
    }


@pytest_asyncio.fixture
async def admin_data() -> dict[str, Any]:
    return {
        "email": "admin@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
    }


@pytest_asyncio.fixture
async def registered_user(
    db_session: AsyncSession, user_data: dict[str, Any]
) -> User:
    user = User(
        email=user_data["email"],
        hashed_password=hash_password(user_data["password"]),
        full_name=user_data["full_name"],
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def registered_admin(
    db_session: AsyncSession, admin_data: dict[str, Any]
) -> User:
    admin = User(
        email=admin_data["email"],
        hashed_password=hash_password(admin_data["password"]),
        full_name=admin_data["full_name"],
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    await db_session.flush()
    await db_session.refresh(admin)
    return admin


def create_ticket_payload(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "title": "Cannot connect to database",
        "description": "Getting timeout error when connecting to PostgreSQL from the API service.",
    }
    if overrides:
        payload.update(overrides)
    return payload


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient, user_data: dict[str, Any], registered_user: User
) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(
    client: AsyncClient, admin_data: dict[str, Any], registered_admin: User
) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": admin_data["email"], "password": admin_data["password"]},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(autouse=True)
def mock_celery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.tasks.ticket_tasks.process_ticket.delay", lambda *a, **kw: None)  # type: ignore
