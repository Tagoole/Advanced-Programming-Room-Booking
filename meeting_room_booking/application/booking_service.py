

from datetime import datetime
from domain.Booking import Booking
from domain.value_objects.BookingReference import BookingReference
from domain.value_objects.TimeRange import TimeRange
from domain.services import BookingDomainService
from domain.events.BookingConfirmed import BookingConfirmed
from domain.events.BookingCancelled import BookingCancelled
from application.dtos import ConfirmBookingCommand, CancelBookingCommand
from application.repositories import BookingRepository, RoomRepository

class BookingApplicationService:

    def __init__(
        self,
        booking_repo: BookingRepository,
        room_repo: RoomRepository,
        domain_service: BookingDomainService,
    ):
        self._booking_repo = booking_repo
        self._room_repo = room_repo
        self._domain_service = domain_service

    def confirm_booking(self, command: ConfirmBookingCommand) -> list:
        """
        Use Case 1: Confirm a booking.

        Flow: BR1 (TimeRange construction) -> BR4 (Domain Service,
        capacity check) -> BR2 (Booking.confirm(), raises BR5 event)
        -> handler -> BR3 (Room.accept_booking()) -> save.
        """

        # 1. Create Value Objects (BR1 enforced the instant these are built)
        reference = BookingReference.create(command.booking_reference)
        time_range = TimeRange.create(command.start, command.end)

        # 2. Load the Room first — we need it for the BR4 check below,
        #    and we must confirm it actually exists (BR6 - lookup rule)
        room = self._room_repo.get_by_id(command.room_id)
        if room is None:
            raise ValueError(f"Room {command.room_id} does not exist")

        # 3. Build the Booking Aggregate (still PENDING, not saved yet)
        booking = Booking(
            reference=reference,
            room_id=command.room_id,
            requester_id=command.requester_id,
            time_range=time_range,
            attendees=command.attendees,
        )

        # 4. BR4 — cross-aggregate check via the Domain Service.
        #    Raises before anything is confirmed or saved if it fails.
        self._domain_service.check_room_can_accommodate(booking, room)

        # 5. BR2 — Booking decides for itself whether it can transition
        #    to CONFIRMED. This also raises the BR5 Domain Event
        #    internally (see Booking.confirm()).
        booking.confirm()
        events = list(booking.get_domain_events())

        # 6. HANDLER: react to the BookingConfirmed event by asking
        #    Room (Aggregate B) to accept the new time range. Room
        #    enforces BR3 here, on its own terms. If it raises, we
        #    deliberately do NOT catch the exception — it propagates
        #    up, and neither booking nor room gets saved below.
        for event in events:
            if isinstance(event, BookingConfirmed):
                room.accept_booking(booking.time_range)

        # 7. Only save once every step above succeeded.
        self._booking_repo.save(booking)
        self._room_repo.save(room)
        booking.clear_domain_events()

        return events

    def cancel_booking(self, command: CancelBookingCommand) -> list:
        """
        Use Case 2: Cancel an existing booking.

        Flow: BR6 (lookup) -> BR2 (Booking.cancel(), raises event)
        -> handler -> Room.release_booking() -> save.
        """

        reference = BookingReference.create(command.booking_reference)

        # BR6 — lookup rule: must retrieve the existing Booking first
        booking = self._booking_repo.get_by_reference(reference)
        if booking is None:
            raise ValueError(f"Booking {reference} not found")

        booking.cancel()
        events = list(booking.get_domain_events())

        # Handler: free the room's slot again for someone else
        for event in events:
            if isinstance(event, BookingCancelled):
                room = self._room_repo.get_by_id(event.room_id)
                if room is not None:
                    room.release_booking(booking.time_range)
                    self._room_repo.save(room)

        self._booking_repo.save(booking)
        booking.clear_domain_events()

        return events
