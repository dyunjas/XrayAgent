from typing import Generator, Optional
from fastapi import Header

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from app.utils.http_errors import http_unauthorized

from app.config import settings
from app.utils.auth import require_bearer


engine = create_engine(
    settings.db_dsn,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=1800
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)


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