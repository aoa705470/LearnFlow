from datetime import UTC, datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy.dialects import mysql

from app.db.types import UTCDateTime, UUIDChar

MYSQL_DIALECT = mysql.dialect()


def test_uuid_type_uses_ascii_binary_storage_and_canonical_text() -> None:
    uuid_type = UUIDChar()
    identifier = UUID("A0A70547-0000-4000-8000-000000000001")

    assert str(uuid_type.compile(dialect=MYSQL_DIALECT)) == (
        "CHAR(36) CHARACTER SET ascii COLLATE ascii_bin"
    )
    assert uuid_type.process_bind_param(identifier, MYSQL_DIALECT) == (
        "a0a70547-0000-4000-8000-000000000001"
    )
    assert (
        uuid_type.process_result_value(
            "a0a70547-0000-4000-8000-000000000001",
            MYSQL_DIALECT,
        )
        == identifier
    )


def test_utc_datetime_normalizes_aware_values_and_preserves_microseconds() -> None:
    datetime_type = UTCDateTime()
    supplied = datetime(
        2026,
        10,
        28,
        17,
        45,
        12,
        654321,
        tzinfo=timezone(timedelta(hours=8)),
    )

    stored = datetime_type.process_bind_param(supplied, MYSQL_DIALECT)
    loaded = datetime_type.process_result_value(stored, MYSQL_DIALECT)

    assert str(datetime_type.compile(dialect=MYSQL_DIALECT)) == "DATETIME(6)"
    assert stored == datetime(2026, 10, 28, 9, 45, 12, 654321)
    assert loaded == datetime(2026, 10, 28, 9, 45, 12, 654321, tzinfo=UTC)


def test_utc_datetime_rejects_naive_python_values() -> None:
    with pytest.raises(ValueError, match="requires an aware datetime"):
        UTCDateTime().process_bind_param(datetime(2026, 10, 28, 9, 45), MYSQL_DIALECT)
