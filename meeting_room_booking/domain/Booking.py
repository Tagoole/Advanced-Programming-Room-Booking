from datetime import datetime
from .shared.AggregateRoot import AggregateRoot
from .value_objects.BookingReference import BookingReference
from .value_objects.TimeRange import TimeRange
from .value_objects.BookingStatus import BookingStatus
from .events.BookingConfirmed import BookingConfirmed
from .events.BookingCancelled import BookingCancelled

class Booking(AggregateRoot):
    def __init__(
            self,
            reference: BookingReference,
            room_id: int,
            requester_id: str,
            time_range: TimeRange,
            attendees: int,
    ):
        super().__init__()

        if attendees <= 0:
            raise ValueError("Number of attendees must be greater than zero.")
         
        self.reference = reference
        self.room_id = room_id
        self.requester_id = requester_id
        self.time_range = time_range
        self.attendees = attendees
        self.status = BookingStatus.PENDING

        # --- public read-only properties ---

    @property
    def reference(self) -> BookingReference:
        return self._reference
    