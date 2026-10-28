import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine


@pytest.mark.mysql
def test_mysql_test_instance_has_expected_session_settings(mysql_engine: Engine) -> None:
    with mysql_engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT @@version AS version, @@character_set_server AS charset, "
                    "@@collation_server AS collation, @@session.time_zone AS time_zone, "
                    "@@session.innodb_lock_wait_timeout AS lock_wait_timeout, "
                    "TIMEDIFF(NOW(), UTC_TIMESTAMP()) AS utc_offset"
                )
            )
            .mappings()
            .one()
        )

    assert str(row["version"]).startswith("8.4.")
    assert row["charset"] == "utf8mb4"
    assert row["collation"] == "utf8mb4_0900_ai_ci"
    assert row["time_zone"] == "+00:00"
    assert row["lock_wait_timeout"] == 5
    assert str(row["utc_offset"]) == "0:00:00"
