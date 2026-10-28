from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Supplies time explicitly so domain rules never need to sleep in tests."""

    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)
