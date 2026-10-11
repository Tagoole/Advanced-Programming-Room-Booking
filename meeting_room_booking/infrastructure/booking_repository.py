
from application.repositories import BookingRepository
from domain.Booking import Booking
from domain.value_objects.BookingReference import BookingReference

class InMemoryBookingRepository(BookingRepository):
    

    def __init__(self):
        self._bookings: dict[str, Booking] = {}

    def save(self, booking: Booking) -> None:
        self._bookings[str(booking.reference)] = booking

    def get_by_reference(self, reference: BookingReference) -> Booking | None:
        return self._bookings.get(str(reference))

    