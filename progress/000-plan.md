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

#### Этап 2 — Контракты (сначала данные)
- [ ] Написать SQLAlchemy модели: User, Ticket, FAQArticle, DocumentationArticle, TicketHistory, ErrorLog
- [ ] Написать Pydantic схемы: auth, user, ticket, faq, common (ErrorResponse, PaginatedResponse)

#### Этап 3 — API (пишем рутеры первыми)
- [ ] `app/api/deps.py` — Annotated типы: DB, CurrentUser, Pagination
- [ ] `app/api/v1/auth.py` — POST /register, /token, /refresh
- [ ] `app/api/v1/users.py` — CRUD /users (вся логика внутри рутеров)
- [ ] `app/api/v1/tickets.py` — CRUD /tickets + POST /submit (вся логика внутри рутеров)

#### Этап 4 — Вытягиваем Services (рефакторинг API)
- [ ] `app/repositories/base.py` — BaseRepository[T]
- [ ] `app/repositories/user_repository.py` — UserRepository
- [ ] `app/repositories/ticket_repository.py` — TicketRepository
- [ ] `app/repositories/faq_repository.py` — FAQRepository
- [ ] `app/repositories/documentation_repository.py` — DocumentationRepository
- [ ] Вынести логику из рутеров в сервисы:
  - `app/services/auth_service.py` — register, authenticate, refresh
  - `app/services/user_service.py` — CRUD
  - `app/services/ticket_service.py` — CRUD + submit + статусные переходы
  - `app/services/agent_service.py` — process_ticket (оркестрация агента)
- [ ] Рутеры становятся тонкими: `payload → service.call() → response`

#### Этап 5 — Celery + Agent
- [ ] `app/tasks/celery_app.py` — Celery app (redis broker/backend)
- [ ] `app/tasks/ticket_tasks.py` — `process_ticket(ticket_id)`
- [ ] `app/agent/prompts.py` — шаблоны промптов для LLM
- [ ] `app/agent/matcher.py` — SemanticMatcher (поиск похожих)
- [ ] `app/agent/classifier.py` — TicketClassifier
- [ ] `app/agent/router.py` — TicketRouter (категория + приоритет + команда)
- [ ] `app/agent/responder.py` — ResponseGenerator

#### Этап 6 — Инфраструктура
- [ ] Alembic: `alembic init`, авто-генерация миграции, `upgrade head`
- [ ] Dockerfile (multi-stage)
- [ ] docker-compose.yml (app + postgres:16 + redis:7)
- [ ] .env.example (все переменные)

#### Этап 7 — Тесты
- [ ] `tests/conftest.py` — async engine, test session, client, auth fixture
- [ ] `tests/test_auth.py` — register, login, refresh, ошибки
- [ ] `tests/test_tickets.py` — CRUD, submit, статусные переходы, фильтрация
- [ ] `tests/test_agent.py` — mock LLM, тест matcher/classifier/router/responder
