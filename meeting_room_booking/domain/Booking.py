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

    @property
    def room_id(self) -> int:
        return self._room_id

    @property
    def requester_id(self) -> str:
        return self._requester_id   

    @property
    def time_range(self) -> TimeRange:
        return self._time_range 

    @property
    def attendees(self) -> int:
        return self._attendees

    @property
    def status(self) -> BookingStatus:
        return self._status 

    # --- business behaviour ---

    def confirm(self):
        if self.status != BookingStatus.PENDING:
            raise ValueError("Only pending bookings can be confirmed."
                  f"Cannot confirm booking {self._reference}. "
                  f"Current status is {self._status}"              
                             )
        self._status = BookingStatus.CONFIRMED

        self._raise_domain_event(
            BookingConfirmed(
                booking_reference=self._reference,
                room_id=self._room_id,
                occured_on=datetime.now()
            )
        )

    def cancel(self) -> None:
        if self._status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled."
                  f"Cannot cancel booking {self._reference}. "
                  f"Current status is {self._status}"              
                             )
        self._status = BookingStatus.CANCELLED

        self._raise_domain_event(
            BookingCancelled(
                booking_reference=self._reference,
                room_id=self._room_id,
                occured_on=datetime.now()
            )
        )

    def __str__(self):
         return (
            f"Booking({self._reference}, room={self._room_id}, "
            f"{self._time_range}, attendees={self._attendees}, status={self._status})"
        )
