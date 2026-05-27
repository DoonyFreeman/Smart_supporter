# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Automated Tech-Support Triager — FastAPI app that ingests support tickets, runs an LLM-based agent (classify → match → route → respond), and persists results. PostgreSQL + Redis + Celery; React/Vite frontend.

`AGENTS.md` contains the full spec (architecture, DB schema, endpoints, agent algorithm). Treat it as the authoritative design doc — read it before non-trivial work.

## Common commands

Dependencies are managed with **uv** (see `uv.lock`, `pyproject.toml`).

```bash
# Install / sync deps
uv sync

# Run the API locally (expects postgres+redis up; see below)
uvicorn app.main:app --reload

# Celery worker
celery -A app.tasks.celery_app worker -l info

# Lint + format
ruff check .
ruff format --check .

# Type-check
mypy app/

# Tests (asyncio mode is auto via pyproject)
pytest -v
pytest tests/test_tickets.py::test_name -v   # single test

# Migrations
alembic revision --autogenerate -m "msg"
alembic upgrade head
alembic downgrade -1

# Full stack via docker
docker-compose up -d            # frontend(:3000), app(:8000), celery, postgres, redis
```

Frontend (`frontend/`): `npm run dev` (Vite), `npm run build` (tsc + vite build).

## Architecture notes (big picture)

Strict layered architecture — keep the boundaries:

```
api/v1 (routers)  →  services  →  repositories  →  models (SQLAlchemy)
                       │
                       ├── agent/  (LLM orchestration: classifier → matcher → router → responder)
                       └── tasks/  (Celery — thin wrappers around services)
schemas/  — Pydantic V2 I/O DTOs (separate from models)
utils/    — db_manager, security (JWT/bcrypt), errors (custom exceptions + handlers)
```

Key cross-cutting pieces:

- **`app/main.py`** wires routers under `settings.API_V1_PREFIX` and registers global exception handlers from `app/utils/errors.py`. Add new custom exceptions there and register them in `main.py`.
- **`app/database.py`** owns the async engine + `async_sessionmaker` + `get_db()` FastAPI dependency. All DB access is async (asyncpg + SQLAlchemy 2.0 `Mapped`/`select()`).
- **`app/api/deps.py`** exposes `Annotated`-based DI shortcuts (DB session, CurrentUser, Pagination). Use these instead of inlining `Depends(...)` in routes.
- **Repository pattern**: `app/repositories/base.py` is the abstract `BaseRepository[T]`; per-model repos extend it. Services depend on repos, never on `AsyncSession` directly.
- **Agent flow** (triggered by `POST /api/v1/tickets/submit` → Celery `process_ticket(ticket_id)`): SemanticMatcher → TicketClassifier → TicketRouter (only for `bug`) → ResponseGenerator. Final write updates `status`, `response_text`, `priority`, `category`, `assigned_team`, `resolved_at`. See AGENTS.md for the state machine.
- **LLM provider** lives in `app/agent/llm_provider.py`. `settings.LLM_STUB = True` swaps in a stub that emulates responses — tests set this in `conftest.py`. New agent code must respect the stub path.
- **Auth**: JWT access (15m) + refresh (7d), bcrypt password hashing in `utils/security.py`.

## Testing

- `tests/conftest.py` auto-detects Docker vs host and rewrites `@postgres:` → `@localhost:` in `DATABASE_URL`. Tests need a reachable Postgres (use `docker-compose up -d postgres redis`).
- Each test gets a nested-transaction `db_session` fixture; the FastAPI `get_db` dep is overridden to share that session, so the `client` fixture sees test data without commits.
- LLM is always stubbed in tests (`_settings.LLM_STUB = True`).

## Conventions (from AGENTS.md — enforced)

- async/await everywhere; never call sync DB code from async paths.
- Pydantic V2 only: `model_config`, `field_validator`, `model_validate`, `from_attributes=True`.
- SQLAlchemy 2.0 style only: `Mapped` + `mapped_column`, `select()/update()/delete()`, `selectinload` for relationships.
- `X | None`, not `Optional[X]`. No bare `except:`. No mutable default args.
- All secrets via `app/config.py` (Pydantic Settings + `.env`) — never hardcode.
- Celery tasks stay thin: parse args, call a service, return.

## Stray files

- `1.py` at repo root is untracked scratch — ignore it; don't extend it.
- `progress/000-plan.md` is the historical build plan (all stages marked complete in commit `657986f`).
