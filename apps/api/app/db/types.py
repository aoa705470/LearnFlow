from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from sqlalchemy import Date, DateTime, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator, TypeEngine


class UUIDChar(TypeDecorator[UUID]):
    """Store canonical UUID text with bytewise ASCII comparison."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[object]:
        if dialect.name == "mysql":
            return dialect.type_descriptor(
                cast(
                    TypeEngine[object],
                    mysql.CHAR(length=36, charset="ascii", collation="ascii_bin"),
                )
            )
        return dialect.type_descriptor(cast(TypeEngine[object], String(length=36)))

    def process_bind_param(self, value: UUID | None, dialect: Dialect) -> str | None:
        del dialect
        if value is None:
            return None
        if not isinstance(value, UUID):
            raise TypeError("UUIDChar values must be uuid.UUID instances")
        return str(value)

    def process_result_value(self, value: object | None, dialect: Dialect) -> UUID | None:
        del dialect
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            return UUID(value)
        raise TypeError("UUIDChar database values must be strings")


class UTCDateTime(TypeDecorator[datetime]):
    """Round-trip aware UTC datetimes through MySQL DATETIME(6)."""

    impl = DateTime
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[object]:
        if dialect.name == "mysql":
            return dialect.type_descriptor(cast(TypeEngine[object], mysql.DATETIME(fsp=6)))
        return dialect.type_descriptor(cast(TypeEngine[object], DateTime(timezone=False)))

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        del dialect
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("UTCDateTime requires an aware datetime")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: object | None, dialect: Dialect) -> datetime | None:
        del dialect
        if value is None:
            return None
        if not isinstance(value, datetime):
            raise TypeError("UTCDateTime database values must be datetime instances")
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)


def version_number_type() -> mysql.BIGINT:
    return mysql.BIGINT(unsigned=True)


def local_date_type() -> Date:
    return Date()


def standard_text_type() -> Text:
    return Text()


def long_text_type() -> mysql.MEDIUMTEXT:
    return mysql.MEDIUMTEXT()
