# Этап 0: Инициализация проекта

## Сделано
- [x] Создан шаблон проекта через `uv init supports_triager --app --python 3.12`
- [x] Настроен pyproject.toml (Python >=3.12)
- [x] Создана папка `progress/` для учёта прогресса

## Структура на текущий момент
```
supports_triager/
├── .python-version       # Python 3.12
├── pyproject.toml        # uv project config
├── README.md             # uv-шный readme (заменим позже)
├── main.py               # заглушка от uv
└── progress/
    └── 000-plan.md       # этот файл
```

## Следующие шаги (что нужно сделать)

### Порядок: Top-Down (API → Services)

Сначала пишем контракты и API, затем вытягиваем логику в сервисы.

#### ✅ Этап 1 — Фундамент проекта (завершён)
- [x] Установлены зависимости (`uv add fastapi sqlalchemy asyncpg alembic celery redis passlib bcrypt python-jose pydantic pydantic-settings python-multipart httpx pytest pytest-asyncio pytest-httpx ruff mypy greenlet`)
- [x] Создана структура папок согласно AGENTS.md + `__init__.py` в каждой
- [x] `app/config.py` — Pydantic Settings из .env
- [x] `app/database.py` — engine + async_sessionmaker + get_db
- [x] `app/utils/db_manager.py` — DBManager (async context manager)
- [x] `app/utils/errors.py` — AppException, NotFoundException, ForbiddenException, UnauthorizedException, ConflictException, ValidationException + handler
- [x] `app/utils/security.py` — hash_password, verify_password, create_access_token, create_refresh_token, get_current_user
- [x] `app/api/deps.py` — Annotated типы: DB, Pagination
- [x] `app/models/base.py` — DeclarativeBase
- [x] `app/main.py` — lifespan, exception handlers (6 штук), пустой FastAPI
- [x] Проверено: ruff ✅, format ✅, mypy ✅, `uvicorn` стартует и отвечает 200 на /docs

#### ✅ Этап 2 — Контракты (завершён)
- [x] SQLAlchemy модели: User, Ticket, FAQArticle, DocumentationArticle, TicketHistory, ErrorLog
- [x] Pydantic схемы: auth, user, ticket, faq, common (ErrorResponse, PaginatedResponse)

#### ✅ Этап 3 — API (завершён)
- [x] `app/api/deps.py` — Annotated типы: DB, CurrentUser, Pagination
- [x] `app/api/v1/auth.py` — POST /register, /token, /refresh
- [x] `app/api/v1/users.py` — CRUD /users
- [x] `app/api/v1/tickets.py` — CRUD /tickets + POST /submit

#### ✅ Этап 4 — Services + Repositories (завершён)
- [x] `app/repositories/base.py` — BaseRepository[T] (create, get, list, update, delete)
- [x] `app/repositories/user_repository.py` — UserRepository (+ get_by_email)
- [x] `app/repositories/ticket_repository.py` — TicketRepository (+ list_with_filters, find_similar_by_text)
- [x] `app/repositories/faq_repository.py` — FAQRepository (+ search_by_keywords)
- [x] `app/repositories/documentation_repository.py` — DocumentationRepository (+ search_by_product_area)
- [x] `app/services/auth_service.py` — register, authenticate, refresh
- [x] `app/services/user_service.py` — CRUD
- [x] `app/services/ticket_service.py` — CRUD + submit + статусные переходы
- [x] `app/services/agent_service.py` — process_ticket (оркестрация агента)
- [x] Рутеры тонкие: `payload → service.call() → response`

#### ✅ Этап 5 — Celery + Agent (завершён)
- [x] `app/tasks/celery_app.py` — Celery app (redis broker/backend, autodiscover)
- [x] `app/tasks/ticket_tasks.py` — `process_ticket(ticket_id)` (bridge async)
- [x] `app/agent/prompts.py` — шаблоны промптов: классификация, маршрутизация, ответ
- [x] `app/agent/matcher.py` — SemanticMatcher (поиск похожих тикетов/FAQ/docs)
- [x] `app/agent/classifier.py` — TicketClassifier (faq_match/bug/feature_request/needs_info)
- [x] `app/agent/router.py` — TicketRouter (категория + приоритет + команда)
- [x] `app/agent/responder.py` — ResponseGenerator
- [x] `app/agent/llm_provider.py` — LLMProvider (Ollama/OpenAI/stub)

#### ✅ Этап 6 — Инфраструктура (завершён)
- [x] `.env.example` — все переменные окружения
- [x] Alembic: `alembic init`, async `env.py`, авто-миграция `init`, `upgrade head` (проверен downgrade/re-upgrade)
- [x] `Dockerfile` — multi-stage (builder + runtime)
- [x] `docker-compose.yml` — app + celery + postgres:16 + redis:7

#### ✅ Этап 7 — Тесты (завершён)
- [x] `tests/conftest.py` — async engine, savepoint rollback, client, auth fixtures, celery mock
- [x] `tests/test_auth.py` — 9 тестов: register (4), login (3), refresh (3)
- [x] `tests/test_tickets.py` — 10 тестов: create (2), submit (2), list (3), get (2), update (2), delete (2)
- [x] `tests/test_agent.py` — 14 тестов: matcher (2), classifier (4), router (3), responder (2), agent_service (2)
- [x] Исправлены баги: `JWTError` не ловился в refresh, `redirect_slashes=False` для API, установлен `bcrypt==4.1.3`
- [x] Проверено: ruff ✅, mypy ✅ (1 pre-existing celery stub), pytest ✅ 37/37
