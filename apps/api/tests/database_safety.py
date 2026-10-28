from collections.abc import MutableMapping

from sqlalchemy.engine import make_url

DEFAULT_TEST_DATABASE_URL = (
    "mysql+pymysql://test:test@127.0.0.1:3308/learnflow_test?charset=utf8mb4"
)


def require_isolated_test_database(database_url: str) -> None:
    url = make_url(database_url)
    if url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("MySQL tests only allow a loopback database host.")
    if url.port != 3308:
        raise RuntimeError("MySQL tests require the isolated port 3308.")
    if url.database != "learnflow_test":
        raise RuntimeError("MySQL tests require the learnflow_test database.")


def configure_isolated_test_database(environment: MutableMapping[str, str]) -> str:
    """Make the validated test database the only database visible to the test app."""
    database_url = environment.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
    require_isolated_test_database(database_url)
    environment["TEST_DATABASE_URL"] = database_url
    environment["DATABASE_URL"] = database_url
    return database_url
