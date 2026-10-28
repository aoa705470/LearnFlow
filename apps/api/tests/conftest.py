import os

import pytest

SAFE_SETTINGS = {
    "APP_ENV": "development",
    "API_HOST": "127.0.0.1",
    "API_PORT": "8000",
    "DATABASE_URL": "mysql+pymysql://test:test@127.0.0.1:3308/learnflow_test?charset=utf8mb4",
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
    os.environ.setdefault(name, value)


@pytest.fixture
def settings_environment(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    for name, value in SAFE_SETTINGS.items():
        monkeypatch.setenv(name, value)
    return SAFE_SETTINGS.copy()
