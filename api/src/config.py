"""Application configuration — uses os.environ for compatibility."""

import os


class Settings:
    app_name: str = "CodeSentinel"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./codesentinel_dev.db")
    redis_url: str | None = os.getenv("REDIS_URL") or None

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


settings = Settings()
