import pytest

from tests.database_safety import (
    DEFAULT_TEST_DATABASE_URL,
    configure_isolated_test_database,
    require_isolated_test_database,
)


def test_test_database_overrides_an_existing_application_database_url() -> None:
    environment = {
        "DATABASE_URL": "mysql+pymysql://user:password@127.0.0.1:3306/learnflow_prod",
        "TEST_DATABASE_URL": DEFAULT_TEST_DATABASE_URL,
    }

    configured_url = configure_isolated_test_database(environment)

    assert configured_url == DEFAULT_TEST_DATABASE_URL
    assert environment["DATABASE_URL"] == DEFAULT_TEST_DATABASE_URL


@pytest.mark.parametrize(
    "database_url",
    [
        "mysql+pymysql://user:password@127.0.0.1:3307/learnflow_test",
        "mysql+pymysql://user:password@127.0.0.1:3308/learnflow_dev",
        "mysql+pymysql://user:password@example.com:3308/learnflow_test",
    ],
)
def test_test_database_guard_rejects_unsafe_urls(database_url: str) -> None:
    with pytest.raises(RuntimeError):
        require_isolated_test_database(database_url)
