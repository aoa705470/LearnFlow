from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy.orm import Session, sessionmaker

from app.db.engine import get_engine


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        class_=Session,
        autoflush=True,
        expire_on_commit=False,
        autobegin=False,
    )


def get_session() -> Iterator[Session]:
    """Yield one Session for one request without owning its transaction."""
    with get_session_factory()() as session:
        yield session
