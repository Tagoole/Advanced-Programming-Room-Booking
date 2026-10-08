from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True, slots=True)
class TimeRange: 
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError(
                "A booking time range cannot end before or at the same time it starts."
            )
        if self.start.date() != self.end.date():
            raise ValueError(
                "A booking time range must start and end on the same day."
            )
        working_start = time(8, 0)
        working_end = time(18, 0)

        if self.start.time() < working_start or self.end.time() > working_end:
            raise ValueError(
                "Bookings are only allowed between 08:00 and 18:00."
            )

    @classmethod
    def create(cls, start: datetime, end: datetime) -> "TimeRange":
        """Preferred way to create a TimeRange — makes intent clear
        at the call site."""
        return cls(start=start, end=end)

    def overlaps_with(self, other: "TimeRange") -> bool:
        """
        Returns True if this time range overlaps with another.

        Used by Room (see domain/Room.py) to protect BR3: "two
        confirmed bookings for the same room must not overlap."
        """
        return self.start < other.end and other.start < self.end

    def __str__(self) -> str:
        return f"{self.start.strftime('%Y-%m-%d %H:%M')} \u2192 {self.end.strftime('%H:%M')}"
