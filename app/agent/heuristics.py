"""Heuristic fallback for when the LLM provider is unreachable.

These rules are intentionally simple — they exist so the system still produces
something useful (a tentative classification, a polite holding reply) when
Ollama / OpenAI is down. The LLM agent always supersedes this when available.
"""

from __future__ import annotations

from app.agent.matcher import MatchResult


_BUG_TOKENS_EN = {
    "error", "errors", "bug", "broken", "crash", "crashed", "fail", "fails",
    "failed", "failing", "stack", "trace", "500", "404", "exception", "wrong",
    "incorrect", "doesn't", "does not", "not working", "cannot", "can't",
    "issue", "problem", "throws",
}
_BUG_TOKENS_RU = {
    "ошибка", "ошибки", "ошибку", "падает", "упало", "сломан", "сломалось",
    "сломана", "не работает", "не работают", "не работает,", "не открывается",
    "падение", "критический", "критично", "не загружается", "вылетает",
    "исключение", "трейс", "стек", "проблема",
}
_FEATURE_TOKENS_EN = {
    "feature", "request", "would like", "could you", "please add", "support for",
    "wish", "could we", "we need", "nice to have", "would be great",
}
_FEATURE_TOKENS_RU = {
    "хочу", "хотелось", "хотелось бы", "добавьте", "добавить", "было бы здорово",
    "предложение", "запрос", "пожелание", "сделайте", "поддержка для",
    "нужна", "нужно",
}

_CRITICAL_TOKENS = {
    "production", "prod", "down", "outage", "data loss", "потеря данных",
    "продакшн", "лежит", "недоступен", "critical", "критический", "security",
    "безопасность", "leak", "утечка",
}
_HIGH_TOKENS = {
    "blocking", "блокирует", "everyone", "all users", "все пользователи",
    "many users", "много пользователей", "high", "urgent", "срочно",
}
_LOW_TOKENS = {
    "cosmetic", "косметик", "minor", "typo", "опечатка", "nice to have",
}

_CATEGORY_RULES: list[tuple[str, str, set[str]]] = [
    # (category, team, tokens)
    (
        "Database",
        "backend-db",
        {"database", "db", "postgres", "sql", "migration", "миграц", "бд"},
    ),
    (
        "Auth",
        "backend-api",
        {
            "login", "logout", "auth", "token", "session", "permission",
            "вход", "выход", "аутентифик", "авторизац", "сессия", "пароль",
            "password",
        },
    ),
    (
        "Reports",
        "backend-api",
        {"report", "reports", "отчёт", "отчет", "отчёты", "export", "экспорт"},
    ),
    (
        "API",
        "backend-api",
        {"api", "endpoint", "/users", "/api", "rest", "json", "request"},
    ),
    (
        "UI",
        "frontend",
        {
            "ui", "button", "кнопка", "верстка", "вёрстка", "layout", "css",
            "frontend", "page", "modal", "форма", "form", "стиль", "style",
        },
    ),
    (
        "Network",
        "infra",
        {
            "network", "connection", "timeout", "dns", "ssl", "certificate",
            "сеть", "сертификат", "соединение", "недоступен",
        },
    ),
]


def _contains_any(text: str, vocab: set[str]) -> bool:
    return any(token in text for token in vocab)


def classify(title: str, description: str, matches: MatchResult) -> str:
    blob = f"{title}\n{description}".lower()

    if matches.faq_articles:
        return "faq_match"
    if _contains_any(blob, _BUG_TOKENS_EN) or _contains_any(blob, _BUG_TOKENS_RU):
        return "bug"
    if _contains_any(blob, _FEATURE_TOKENS_EN) or _contains_any(
        blob, _FEATURE_TOKENS_RU
    ):
        return "feature_request"
    return "needs_info"


def route(title: str, description: str) -> tuple[str, str, str]:
    """Return (category, priority, assigned_team)."""
    blob = f"{title}\n{description}".lower()

    category = "Other"
    team = "backend-api"
    for cat, t, tokens in _CATEGORY_RULES:
        if _contains_any(blob, tokens):
            category = cat
            team = t
            break

    if _contains_any(blob, _CRITICAL_TOKENS):
        priority = "critical"
    elif _contains_any(blob, _HIGH_TOKENS):
        priority = "high"
    elif _contains_any(blob, _LOW_TOKENS):
        priority = "low"
    else:
        priority = "medium"

    return category, priority, team


_RESPONSE_RU = {
    "faq_match": (
        "Здравствуйте! Похоже, ваш вопрос уже разбирался — мы нашли подходящую "
        "статью в базе знаний и приложим её ниже. Если после прочтения вопрос "
        "останется, ответьте на это сообщение, и инженер подключится."
    ),
    "bug": (
        "Спасибо за подробное описание — мы зафиксировали инцидент и передаём "
        "его команде разработки. Ориентировочный срок реакции зависит от "
        "приоритета: critical — до 24 часов, high — 2–3 рабочих дня, medium — "
        "около недели. Мы напишем, как только появятся новости."
    ),
    "feature_request": (
        "Спасибо за идею — мы передали её продуктовой команде. Жёстких сроков "
        "по таким запросам не даём, но обязательно учтём ваш сценарий при "
        "планировании следующих релизов."
    ),
    "needs_info": (
        "Спасибо за обращение. Чтобы быстрее помочь, пришлите, пожалуйста: "
        "точный текст ошибки, шаги воспроизведения, версию приложения и "
        "браузера / ОС. После этого мы сразу подключим инженера."
    ),
}

_RESPONSE_EN = {
    "faq_match": (
        "Hi! It looks like this is covered by our knowledge base — we've "
        "attached the most relevant article below. If anything is still "
        "unclear after reading it, just reply here and an engineer will jump in."
    ),
    "bug": (
        "Thanks for the detailed report — we've logged the incident and routed "
        "it to engineering. Expected first response depends on priority: "
        "critical — under 24 hours, high — 2–3 business days, medium — within "
        "a week. We'll update you as soon as we have news."
    ),
    "feature_request": (
        "Thanks for the idea — we've forwarded it to the product team. We "
        "don't commit to firm dates for feature requests, but your scenario "
        "will be reviewed in the next planning cycle."
    ),
    "needs_info": (
        "Thanks for reaching out. To help faster, could you share the exact "
        "error message, steps to reproduce, app version and browser / OS? "
        "Once we have that, we'll loop in an engineer right away."
    ),
}


def response(ticket_type: str, lang: str, matches: MatchResult) -> str:
    table = _RESPONSE_RU if lang == "ru" else _RESPONSE_EN
    base = table.get(ticket_type) or table["needs_info"]
    if ticket_type == "faq_match" and matches.faq_articles:
        snippet = matches.faq_articles[0]
        base = base + "\n\n" + ("Из FAQ:\n" if lang == "ru" else "From the FAQ:\n") + snippet
    return base
