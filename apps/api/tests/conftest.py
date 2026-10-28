import os

import pytest

from tests.database_safety import configure_isolated_test_database

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
