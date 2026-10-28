from datetime import UTC, datetime

from tests.factories import FixedClock


def test_fixed_clock_returns_supplied_instant() -> None:
    instant = datetime(2026, 10, 28, 9, 30, tzinfo=UTC)

    assert FixedClock(instant).now() == instant
