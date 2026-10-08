from enum import Enum


class BookingStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

    def __str__(self) -> str:
        return self.value
