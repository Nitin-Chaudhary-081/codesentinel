"""Application configuration — uses os.environ for compatibility."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

TESTING = os.getenv("CODESENTINEL_TESTING") == "1" or "pytest" in sys.modules


class Settings:
    app_name: str = "CodeSentinel"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./codesentinel_dev.db")
    redis_url: str | None = os.getenv("REDIS_URL") or None
    trusted_proxy: str | None = os.getenv("TRUSTED_PROXY") or None

    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    @property
    def jwt_configured(self) -> bool:
        return bool(self.jwt_secret) and self.jwt_secret != "change-me-in-production"


settings = Settings()

if not settings.jwt_configured and not TESTING:
    print(
        "FATAL: JWT_SECRET must be set to a strong, non-default value before "
        "starting (refusing to start with a default/empty secret in any mode).",
        file=sys.stderr,
    )
    sys.exit(1)
