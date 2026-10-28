from datetime import date, datetime
from typing import ClassVar
from uuid import UUID

from sqlalchemy import Date, MetaData
from sqlalchemy.orm import DeclarativeBase

from app.db.types import UTCDateTime, UUIDChar

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map: ClassVar[dict[object, object]] = {
        UUID: UUIDChar(),
        datetime: UTCDateTime(),
        date: Date(),
    }
