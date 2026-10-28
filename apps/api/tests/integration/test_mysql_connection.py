import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool


def require_isolated_test_database(database_url: str) -> None:
    url = make_url(database_url)
    if url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("MySQL tests only allow a loopback database host.")
    if url.port != 3308:
        raise RuntimeError("MySQL tests require the isolated port 3308.")
    if url.database != "learnflow_test":
        raise RuntimeError("MySQL tests require the learnflow_test database.")


@pytest.mark.mysql
def test_mysql_test_instance_has_expected_session_settings() -> None:
    if os.getenv("RUN_MYSQL_TESTS") != "1":
        pytest.skip("Set RUN_MYSQL_TESTS=1 to run the isolated MySQL test.")

    database_url = os.environ["TEST_DATABASE_URL"]
    require_isolated_test_database(database_url)
    engine = create_engine(database_url, poolclass=NullPool)

    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT @@version AS version, @@character_set_server AS charset, "
                    "@@collation_server AS collation, @@session.time_zone AS time_zone, "
                    "TIMEDIFF(NOW(), UTC_TIMESTAMP()) AS utc_offset"
                )
            )
            .mappings()
            .one()
        )

    engine.dispose()
    assert str(row["version"]).startswith("8.4.")
    assert row["charset"] == "utf8mb4"
    assert row["collation"] == "utf8mb4_0900_ai_ci"
    assert str(row["utc_offset"]) == "0:00:00"


@pytest.mark.parametrize(
    "database_url",
    [
        "mysql+pymysql://user:password@127.0.0.1:3307/learnflow_test",
        "mysql+pymysql://user:password@127.0.0.1:3308/learnflow_dev",
        "mysql+pymysql://user:password@example.com:3308/learnflow_test",
    ],
)
def test_mysql_guard_rejects_unsafe_database_urls(database_url: str) -> None:
    with pytest.raises(RuntimeError):
        require_isolated_test_database(database_url)
