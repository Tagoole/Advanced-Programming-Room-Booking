from dataclasses import dataclass
from datetime import datetime
from ..shared.DomainEvent import DomainEvent
from ..value_objects.BookingReference import BookingReference


@dataclass(frozen=True)
class BookingConfirmed(DomainEvent):
    booking_reference: BookingReference
    room_id: int
    occurred_on: datetime

    def __str__(self):
        return (
            f"BookingConfirmed: {self.booking_reference} "
            f"for room {self.room_id} at {self.occurred_on}"
        )
