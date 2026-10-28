import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_app_env_is_required(
    monkeypatch: pytest.MonkeyPatch,
    settings_environment: dict[str, str],
) -> None:
    monkeypatch.delenv("APP_ENV")

    with pytest.raises(ValidationError, match="APP_ENV"):
        Settings(_env_file=None)


def test_unknown_app_env_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    settings_environment: dict[str, str],
) -> None:
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(ValidationError, match="APP_ENV"):
        Settings(_env_file=None)


@pytest.mark.parametrize("api_host", ["0.0.0.0", "192.168.1.20", "localhost", "::1"])
def test_development_api_host_must_be_the_configured_loopback(
    api_host: str,
    monkeypatch: pytest.MonkeyPatch,
    settings_environment: dict[str, str],
) -> None:
    monkeypatch.setenv("API_HOST", api_host)

    with pytest.raises(ValidationError, match=r"development API_HOST must be 127\.0\.0\.1"):
        Settings(_env_file=None)


def test_database_url_is_masked_in_settings_repr(
    settings_environment: dict[str, str],
) -> None:
    settings = Settings(_env_file=None)

    assert "test:test" not in repr(settings)
    assert "**********" in repr(settings)
