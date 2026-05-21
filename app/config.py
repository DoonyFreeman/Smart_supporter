from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/support_triager"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = "redis://localhost:6379/0"

    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3"
    LLM_API_URL: str = "http://localhost:11434/api/generate"
    LLM_API_KEY: str = ""

    DEBUG: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    API_V1_PREFIX: str = "/api/v1"


settings = Settings()
