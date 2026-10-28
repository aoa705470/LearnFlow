import os
from collections.abc import Iterator

import pytest
from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.db.engine import create_database_engine
from tests.database_safety import (
    configure_isolated_test_database,
    require_isolated_test_database,
)

SAFE_SETTINGS = {
    "APP_ENV": "development",
    "API_HOST": "127.0.0.1",
    "API_PORT": "8000",
    "ALLOWED_HOSTS": '["127.0.0.1:5173","127.0.0.1:8000"]',
    "ALLOWED_ORIGINS": '["http://127.0.0.1:5173","http://127.0.0.1:8000"]',
    "DB_POOL_SIZE": "5",
    "DB_MAX_OVERFLOW": "5",
    "DB_POOL_TIMEOUT_SECONDS": "10",
    "DB_POOL_RECYCLE_SECONDS": "1800",
    "DB_CONNECT_TIMEOUT_SECONDS": "5",
    "DB_READ_TIMEOUT_SECONDS": "30",
    "DB_WRITE_TIMEOUT_SECONDS": "30",
    "DB_LOCK_WAIT_TIMEOUT_SECONDS": "5",
}

for name, value in SAFE_SETTINGS.items():
    os.environ[name] = value

configure_isolated_test_database(os.environ)


@pytest.fixture
def settings_environment(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    for name, value in SAFE_SETTINGS.items():
        monkeypatch.setenv(name, value)
    database_url = os.environ["TEST_DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", database_url)
    return {**SAFE_SETTINGS, "DATABASE_URL": database_url}


@pytest.fixture
def mysql_engine() -> Iterator[Engine]:
    if os.getenv("RUN_MYSQL_TESTS") != "1":
        pytest.skip("Set RUN_MYSQL_TESTS=1 to run the isolated MySQL test.")

    database_url = os.environ["DATABASE_URL"]
    require_isolated_test_database(database_url)
    database_engine = create_database_engine(Settings(_env_file=None))
    try:
        yield database_engine
    finally:
        database_engine.dispose()
