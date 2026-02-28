from typing import Generator, Optional
from fastapi import Header

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker, Session
from app.utils.http_errors import http_unauthorized

from app.config import settings
from app.utils.auth import require_bearer


engine_kwargs = {
    "future": True,
    "pool_pre_ping": True,
}

if settings.db_pool_mode == "null":
    # One request -> one connection; closes after session close.
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update(
        {
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_recycle": settings.db_pool_recycle,
            "pool_timeout": settings.db_pool_timeout,
        }
    )

engine = create_engine(settings.db_dsn, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth_dep(authorization: Optional[str] = Header(default=None)) -> None:
    token = settings.agent_token
    if not token:
        return
    if not authorization or authorization != f"Bearer {token}":
        raise http_unauthorized("Bearer token mismatch")
