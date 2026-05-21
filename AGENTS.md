# Automated Tech-Support Triager

## Описание проекта

FastAPI-приложение для автоматической обработки тикетов техподдержки IT-продуктов. Агент на основе LLM анализирует текст тикета, ищет похожие решения в FAQ и истории тикетов, классифицирует проблему (баг / вопрос / запрос функции), маршрутизирует в нужную команду и генерирует ответ.

## Стек

| Компонент | Технология |
|-----------|------------|
| API       | FastAPI (async) |
| База      | PostgreSQL + async SQLAlchemy 2.0 + Alembic |
| Кэш/брокер| Redis |
| Фоновые задачи | Celery |
| Агент     | LLM (локально через Ollama / OpenAI API) |
| Аутентиф. | JWT (access + refresh tokens) |
| Валидация | Pydantic V2 |
| ASGI      | Uvicorn |

## Архитектура

Слоистая архитектура с чёткими границами ответственности:

```
┌──────────────────────────────────────────────┐
│  API (routers)          — слой presentation  │
├──────────────────────────────────────────────┤
│  Schemas (Pydantic)     — слой валидации     │
├──────────────────────────────────────────────┤
│  Services               — бизнес-логика      │
├──────────────────────────────────────────────┤
│  Agent                  — AI-логика агента   │
├──────────────────────────────────────────────┤
│  Tasks (Celery)         — фоновые задачи     │
├──────────────────────────────────────────────┤
│  Repositories           — data access layer  │
├──────────────────────────────────────────────┤
│  Models (SQLAlchemy)    — схемы БД           │
└──────────────────────────────────────────────┘

Utils (db_manager, security, errors) — сквозные компоненты
```

## Правила разработки

### Обязательно
- **FastAPI Expert**: async/await везде, Annotated для DI, корректные HTTP статусы, lifespan для startup/shutdown
- **Python Pro**: полные type hints, X | None вместо Optional, dataclasses, контекстные менеджеры
- **Pydantic V2**: `model_config`, `field_validator`, `model_validate()`, `model_dump()`, `from_attributes=True`
- **SQLAlchemy 2.0**: Mapped + mapped_column, AsyncSession, select()/update()/delete(), selectinload
- **Repository Pattern**: абстрактный BaseRepository[ModelT] с имплементациями под каждую модель
- **DB Manager**: класс DBManager в `utils/db_manager.py` — обёртка над async_sessionmaker с контекст-менеджером
- **database.py**: engine + async_sessionmaker + get_db() dependency — в отдельном файле
- **Alembic**: все миграции через alembic, авто-генерация при изменении моделей
- **Celery**: celery_app в `tasks/celery_app.py`, таски тонкие — вызов сервисов
- **Обработка ошибок**: кастомные exception классы + глобальные exception handlers в main.py
- **Валидация**: Pydantic схемы для входа/выхода всех эндпоинтов
- **JWT**: access (15m) + refresh (7d) токены, bcrypt для паролей

### Запрещено
- Синхронные вызовы БД в async-коде
- Хранение паролей в plain text
- Жёстко закодированные секреты (всё через .env / Pydantic Settings)
- Смешивание sync/async кода
- Голые `except:`
- Мутабельные default-аргументы

## Структура проекта

```
supports_triager/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app, lifespan, include_routers, error handlers
│   ├── config.py                    # Pydantic Settings (.env)
│   ├── database.py                  # engine, async_sessionmaker, get_db
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                  # DB, CurrentUser, Pagination — Annotated типы
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py              # POST /auth/register, /auth/token, /auth/refresh
│   │       ├── users.py             # CRUD /users
│   │       └── tickets.py           # CRUD /tickets + POST /tickets/submit
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                  # DeclarativeBase
│   │   ├── user.py                  # User
│   │   ├── ticket.py                # Ticket (status, priority, category, assigned_team…)
│   │   ├── faq.py                   # FAQArticle
│   │   ├── documentation.py         # DocumentationArticle
│   │   ├── ticket_history.py        # TicketHistory (audit log)
│   │   └── error_log.py             # ErrorLog
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                  # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py                  # UserCreate, UserUpdate, UserResponse
│   │   ├── ticket.py                # TicketCreate, TicketUpdate, TicketResponse, TicketStatusEnum
│   │   ├── faq.py                   # FAQCreate, FAQResponse
│   │   └── common.py                # ErrorResponse, PaginationParams, PaginatedResponse[T]
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                  # BaseRepository[T] (abstract: create, get, list, update, delete)
│   │   ├── user_repository.py       # UserRepository
│   │   ├── ticket_repository.py     # TicketRepository (find_similar_by_text, …)
│   │   ├── faq_repository.py        # FAQRepository (search_by_keywords, …)
│   │   └── documentation_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # register, authenticate, refresh
│   │   ├── user_service.py          # get_users, get_user, update_user, delete_user
│   │   ├── ticket_service.py        # create_ticket, submit_ticket (→ celery), get_ticket, list_tickets
│   │   └── agent_service.py         # process_ticket — оркестрация агента
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── classifier.py            # TicketClassifier: определяет категорию
│   │   ├── matcher.py               # SemanticMatcher: поиск похожих тикетов/FAQ/docs
│   │   ├── router.py                # TicketRouter: команда + приоритет
│   │   ├── responder.py             # ResponseGenerator: генерация ответа
│   │   └── prompts.py               # Шаблоны промптов для LLM
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py            # Celery app (connect redis, autodiscover)
│   │   └── ticket_tasks.py          # process_ticket(ticket_id) — entry point агента
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db_manager.py            # DBManager: async context manager для сессий
│   │   ├── security.py              # hash_password, verify_password, create_access_token, create_refresh_token
│   │   └── errors.py                # AppException, NotFoundException, ForbiddenException + handlers
│   │
│   └── middleware/
│       └── __init__.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # async engine, test session, client, auth fixture
│   ├── test_auth.py
│   ├── test_tickets.py
│   └── test_agent.py
│
├── docker-compose.yml               # app + postgres:16 + redis:7
├── Dockerfile                       # multi-stage
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## DB Models

### User
| Поле | Тип | Описание |
|------|-----|----------|
| id | int, PK, auto | |
| email | str, unique, index | |
| hashed_password | str | bcrypt hash |
| full_name | str | |
| role | Enum(user/agent/admin) | |
| is_active | bool | |
| created_at | datetime, server_default=now() | |

### Ticket
| Поле | Тип | Описание |
|------|-----|----------|
| id | int, PK | |
| title | str | |
| description | str | |
| status | Enum(new/processing/resolved/triaged/needs_info/closed) | |
| priority | Enum(low/medium/high/critical) \| null | |
| category | str \| null | (Database, API, Reports, Auth, UI, Network, Other) |
| assigned_team | str \| null | (backend-db, backend-api, frontend, infra, …) |
| assigned_to | FK → User.id \| null | |
| created_by | FK → User.id | |
| response_text | text \| null | Сгенерированный ответ клиенту |
| resolved_at | datetime \| null | |
| created_at | datetime | |
| updated_at | datetime | |

### FAQArticle
| Поле | Тип |
|------|-----|
| id | int, PK |
| title | str |
| content | text |
| keywords | str (comma-separated) |
| category | str |
| created_at | datetime |

### DocumentationArticle
| Поле | Тип |
|------|-----|
| id | int, PK |
| title | str |
| content | text |
| product_area | str |
| created_at | datetime |

### TicketHistory (аудит)
| Поле | Тип |
|------|-----|
| id | int, PK |
| ticket_id | FK → Ticket.id |
| action | str |
| changed_by | FK → User.id |
| old_status | str \| null |
| new_status | str \| null |
| comment | text \| null |
| created_at | datetime |

## API Endpoints

### Auth (`/api/v1/auth`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | /register | Регистрация нового пользователя |
| POST | /token | Вход, получение access + refresh токенов |
| POST | /refresh | Обновление access-токена через refresh |

### Users (`/api/v1/users`)
| Метод | Путь | Описание |
|-------|------|----------|
| GET | / | Список пользователей (admin) |
| GET | /{id} | Детали пользователя |
| PATCH | /{id} | Обновление пользователя |
| DELETE | /{id} | Удаление (admin) |

### Tickets (`/api/v1/tickets`)
| Метод | Путь | Описание |
|-------|------|----------|
| POST | / | Создать тикет вручную |
| POST | /submit | Создать тикет + запустить Celery-обработку |
| GET | / | Список тикетов (с фильтрацией) |
| GET | /{id} | Детали тикета |
| PATCH | /{id} | Обновить тикет |
| DELETE | /{id} | Удалить тикет |

## Алгоритм работы агента (AgentService + Celery)

```
POST /api/v1/tickets/submit
         │
         ▼
  FastAPI: сохраняет Ticket (status=new)
         │
         ▼
  Celery: process_ticket.delay(ticket_id)
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │ 1. SemanticMatcher                           │
  │    → поиск похожих closed-тикетов (по тексту) │
  │    → поиск FAQ статей (по ключевым словам)    │
  │    → поиск Documentation статей               │
  └──────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │ 2. TicketClassifier                          │
  │    на основе текста + найденных совпадений:   │
  │    → "faq_match"   — есть решение в FAQ       │
  │    → "bug"         — баг бэкенда              │
  │    → "feature_request" — запрос новой функции │
  │    → "needs_info"  — недостаточно данных      │
  └──────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │ 3. TicketRouter (если классифицирован как bug)│
  │    → категория (Database / API / Reports / …) │
  │    → приоритет (low / medium / high / critical)│
  │    → assigned_team (backend-db, backend-api…) │
  └──────────────────────────────────────────────┘
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │ 4. ResponseGenerator                          │
  │    → если faq_match: пошаговый ответ из FAQ   │
  │    → если bug/feature: ответ-подтверждение    │
  │      с оценённым сроком                       │
  └──────────────────────────────────────────────┘
         │
         ▼
  Обновление Ticket в БД:
    → status = resolved / triaged / needs_info
    → response_text
    → priority, category, assigned_team (если применимо)
    → resolved_at (если resolved)
```

## Статусы тикетов

```
new ──→ processing ──→ resolved      (FAQ — ответ готов)
                      → triaged       (назначено команде)
                      → needs_info    (не хватает данных)
                      → closed        (вручную)
```

## Обработка ошибок

- `NotFoundException` (404) — ресурс не найден
- `ForbiddenException` (403) — недостаточно прав
- `UnauthorizedException` (401) — неаутентифицирован
- `ConflictException` (409) — конфликт (email уже занят)
- `ValidationException` (422) — ошибка валидации (Pydantic)
- `AppException` (500) — внутренняя ошибка

Глобальные обработчики регистрируются в `main.py` через `@app.exception_handler(...)`.

## Запуск

```bash
# Настройка
cp .env.example .env
# docker-compose up -d postgres redis

# Миграции
alembic revision --autogenerate -m "init"
alembic upgrade head

# Запуск
uvicorn app.main:app --reload

# Celery worker
celery -A app.tasks.celery_app worker -l info
```

## Переменные окружения (.env)

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/support_triager
SECRET_KEY=<random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://localhost:6379/0

LLM_PROVIDER=ollama        # openai | ollama
LLM_MODEL=llama3
LLM_API_URL=http://localhost:11434/api/generate
LLM_API_KEY=

DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

## Команды для проверки

```bash
# Линтер
ruff check .
ruff format --check .

# Типы
mypy app/

# Тесты
pytest -v --asyncio-mode=auto

# Миграции
alembic upgrade head
alembic downgrade -1
```

## Генерация кода

Агент (LLM) должен генерировать ответы строго на русском языке, если тикет на русском. Для тестов/заглушек можно использовать `LLMProviderStub`, который эмулирует ответы агента без вызова внешнего API.
