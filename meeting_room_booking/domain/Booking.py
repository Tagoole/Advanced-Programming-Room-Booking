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

        # Basic sanity check — not one of BR1-BR6 itself, just a
        # guard against obviously nonsensical input.
        if attendees <= 0:
            raise ValueError("Attendees must be greater than zero")

        self._reference = reference
        self._room_id = room_id
        self._requester_id = requester_id
        self._time_range = time_range
        self._attendees = attendees
        self._status = BookingStatus.PENDING

    # ---------- public read-only properties ----------

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

    # ---------- business behaviour (BR2 lives here) ----------

    def confirm(self) -> None:
        if self._status != BookingStatus.PENDING:
            raise ValueError(
                f"Cannot confirm booking {self._reference}. "
                f"Current status is {self._status}"
            )

        self._status = BookingStatus.CONFIRMED

        self._raise_domain_event(
            BookingConfirmed(
                booking_reference=self._reference,
                room_id=self._room_id,
                occurred_on=datetime.now(),
            )
        )

    def cancel(self) -> None:
        if self._status == BookingStatus.CANCELLED:
            raise ValueError(
                f"Booking {self._reference} is already cancelled"
            )

        self._status = BookingStatus.CANCELLED

        self._raise_domain_event(
            BookingCancelled(
                booking_reference=self._reference,
                room_id=self._room_id,
                occurred_on=datetime.now(),
            )
        )

    def __str__(self):
        return (
            f"Booking({self._reference}, room={self._room_id}, "
            f"{self._time_range}, attendees={self._attendees}, status={self._status})"
        )
