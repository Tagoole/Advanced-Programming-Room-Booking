
from application.repositories import BookingRepository
from domain.Booking import Booking
from domain.value_objects.BookingReference import BookingReference

class InMemoryBookingRepository(BookingRepository):
    """Simple in-memory version for the coursework — just a dict."""

    def __init__(self):
        self._bookings: dict[str, Booking] = {}

    def save(self, booking: Booking) -> None:
        self._bookings[str(booking.reference)] = booking

    def get_by_reference(self, reference: BookingReference) -> Booking | None:
        return self._bookings.get(str(reference))

    def get_by_room(self, room_id: int) -> list[Booking]:
        return [b for b in self._bookings.values() if b.room_id == room_id]
