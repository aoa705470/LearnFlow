from functools import lru_cache, partial

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry

from app.core.config import Settings, get_settings


def _configure_mysql_session(
    lock_wait_timeout_seconds: int,
    dbapi_connection: DBAPIConnection,
    _connection_record: ConnectionPoolEntry,
) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SET SESSION time_zone = '+00:00'")
        cursor.execute(
            "SET SESSION innodb_lock_wait_timeout = %s",
            (lock_wait_timeout_seconds,),
        )
    finally:
        cursor.close()


def create_database_engine(settings: Settings) -> Engine:
    database_engine = create_engine(
        settings.database_url.get_secret_value(),
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_recycle=settings.db_pool_recycle_seconds,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": settings.db_connect_timeout_seconds,
            "read_timeout": settings.db_read_timeout_seconds,
            "write_timeout": settings.db_write_timeout_seconds,
        },
    )
    event.listen(
        database_engine,
        "connect",
        partial(_configure_mysql_session, settings.db_lock_wait_timeout_seconds),
    )
    return database_engine


@lru_cache
def get_engine() -> Engine:
    return create_database_engine(get_settings())
