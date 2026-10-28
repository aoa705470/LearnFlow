from datetime import UTC, date, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import Column, MetaData, Table, insert, select
from sqlalchemy.engine import Engine

from app.db.types import (
    UTCDateTime,
    UUIDChar,
    local_date_type,
    long_text_type,
    standard_text_type,
    version_number_type,
)


@pytest.mark.mysql
def test_shared_storage_types_round_trip_without_truncation(mysql_engine: Engine) -> None:
    metadata = MetaData()
    table_name = f"t014_storage_probe_{uuid4().hex}"
    probe = Table(
        table_name,
        metadata,
        Column("id", UUIDChar(), primary_key=True),
        Column("occurred_at", UTCDateTime(), nullable=False),
        Column("version", version_number_type(), nullable=False),
        Column("planned_date", local_date_type(), nullable=False),
        Column("question", standard_text_type(), nullable=False),
        Column("body", long_text_type(), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_0900_ai_ci",
    )
    identifier = uuid4()
    supplied_time = datetime(
        2026,
        10,
        28,
        17,
        45,
        12,
        654321,
        tzinfo=timezone(timedelta(hours=8)),
    )
    question = "问" * 10_000
    body = "学" * 200_000

    metadata.create_all(mysql_engine)
    try:
        with mysql_engine.begin() as connection:
            connection.execute(
                insert(probe),
                {
                    "id": identifier,
                    "occurred_at": supplied_time,
                    "version": 18_446_744_073_709_551_615,
                    "planned_date": date(1000, 1, 1),
                    "question": question,
                    "body": body,
                },
            )
            row = connection.execute(select(probe)).mappings().one()

        assert row["id"] == identifier
        assert row["occurred_at"] == datetime(2026, 10, 28, 9, 45, 12, 654321, tzinfo=UTC)
        assert row["version"] == 18_446_744_073_709_551_615
        assert row["planned_date"] == date(1000, 1, 1)
        assert row["question"] == question
        assert row["body"] == body
    finally:
        metadata.drop_all(mysql_engine)
