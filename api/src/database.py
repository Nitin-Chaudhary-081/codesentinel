"""Database connection and session management (synchronous for Android compatibility)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from src.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url.replace("sqlite+aiosqlite", "sqlite"),
    echo=settings.debug,
    future=True,
)


def get_db() -> Session:
    return Session(engine)


def init_db() -> None:
    Base.metadata.create_all(engine)
