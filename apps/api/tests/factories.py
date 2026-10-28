from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FixedClock:
    current: datetime

    def now(self) -> datetime:
        return self.current
