from domain.Booking import Booking
from domain.Room import Room
from domain.value_objects.BookingReference import BookingReference
from domain.value_objects.TimeRange import TimeRange
from domain.value_objects.BookingStatus import BookingStatus
from domain.services import BookingDomainService
from domain.events.BookingConfirmed import BookingConfirmed
from domain.events.BookingCancelled import BookingCancelled
from application.dtos import (
    ConfirmBookingCommand,
    CancelBookingCommand,
    BookingResult,
)
from application.repositories import BookingRepository, RoomRepository


class BookingApplicationService:
    """Runs the two use cases. Loads aggregates, calls them in order,
    handles the events they raise, then saves. No business rules here."""

    def __init__(
        self,
        booking_repo: BookingRepository,
        room_repo: RoomRepository,
        domain_service: BookingDomainService,
    ):
        self._booking_repo = booking_repo
        self._room_repo = room_repo
        self._domain_service = domain_service

    def confirm_booking(self, command: ConfirmBookingCommand) -> BookingResult:
        reference = BookingReference.create(command.booking_reference)
        time_range = TimeRange.create(command.start_time, command.end_time)

        # The room has to exist before we go any further.
        room = self._room_repo.get_by_id(command.room_id)
        if room is None:
            raise ValueError(
                f"Cannot confirm booking {reference}: "
                f"room {command.room_id} does not exist"
            )

        booking = Booking(
            reference=reference,
            room_id=command.room_id,
            requester_id=command.requester_id,
            time_range=time_range,
            attendees=command.attendees,
        )

        # Capacity needs both the booking and the room, so it sits in
        # the domain service rather than on either one.
        self._domain_service.check_room_can_accommodate(booking, room)

        booking.confirm()
        events = list(booking.get_domain_events())

        for event in events:
            if isinstance(event, BookingConfirmed):
                self._on_booking_confirmed(booking, room)

        # Nothing is saved until the handler above has gone through.
        self._booking_repo.save(booking)
        self._room_repo.save(room)
        booking.clear_domain_events()

        return self._to_result(booking, room, events)

    def cancel_booking(self, command: CancelBookingCommand) -> BookingResult:
        reference = BookingReference.create(command.booking_reference)

        # Load both aggregates before changing anything, so we never
        # cancel a booking and then fail on a missing room.
        booking = self._booking_repo.get_by_reference(reference)
        if booking is None:
            raise ValueError(f"Cannot cancel: booking {reference} was not found")

        room = self._room_repo.get_by_id(booking.room_id)
        if room is None:
            raise ValueError(
                f"Cannot cancel booking {reference}: "
                f"room {booking.room_id} does not exist"
            )

        # Check this now. After cancel() the status is CANCELLED and we
        # can no longer tell whether the room ever held this slot.
        was_confirmed = booking.status == BookingStatus.CONFIRMED

        booking.cancel()
        events = list(booking.get_domain_events())

        for event in events:
            if isinstance(event, BookingCancelled):
                self._on_booking_cancelled(booking, room, was_confirmed)

        self._booking_repo.save(booking)
        self._room_repo.save(room)
        booking.clear_domain_events()

        return self._to_result(booking, room, events)

    def _on_booking_confirmed(self, booking: Booking, room: Room) -> None:
        """Handler for BookingConfirmed. Asks the room to take the slot.
        The room checks its own overlap rule and may refuse."""
        room.accept_booking(booking.time_range)

    def _on_booking_cancelled(
        self, booking: Booking, room: Room, was_confirmed: bool
    ) -> None:
        """Handler for BookingCancelled. Gives the slot back, but only if
        the booking had actually been confirmed into the room."""
        if was_confirmed:
            room.release_booking(booking.time_range)

    @staticmethod
    def _to_result(booking: Booking, room: Room, events: list) -> BookingResult:
        return BookingResult(
            booking_reference=str(booking.reference),
            status=str(booking.status),
            room_name=room.name,
            events=tuple(str(e) for e in events),
        )