from .Booking import Booking
from .Room import Room


class BookingDomainService:

    def check_room_can_accommodate(self, booking: Booking, room: Room) -> None:
        if booking.attendees > room.capacity:
            raise ValueError(
                f"Room '{room.name}' has capacity {room.capacity}, "
                f"which cannot accommodate {booking.attendees} attendees."
            )