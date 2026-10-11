

from datetime import datetime

from domain.Room import Room
from domain.services import BookingDomainService
from application.dtos import ConfirmBookingCommand, CancelBookingCommand
from application.booking_service import BookingApplicationService
from infrastructure.booking_repository import InMemoryBookingRepository
from infrastructure.room_repository import InMemoryRoomRepository


def show(result):
    print(f"  {result}")
    for e in result.events:
        print(f"    event -> {e}")


def main():
    
    
    booking_repo = InMemoryBookingRepository()
    room_repo = InMemoryRoomRepository()
    service = BookingApplicationService(
        booking_repo, room_repo, BookingDomainService()
    )

    room = Room("Main Boardroom", capacity=12)
    room_repo.save(room)
    print(f"Room: {room.name} (id={room.id}, capacity={room.capacity})")

    print("\n1. Confirm a booking")
    show(service.confirm_booking(ConfirmBookingCommand(
        booking_reference="BK-9001",
        requester_id="student-42",
        room_id=room.id,
        start_time=datetime(2026, 10, 12, 10, 0),
        end_time=datetime(2026, 10, 12, 11, 30),
        attendees=8,
    )))
    print(f"  room holds {len(room_repo.get_by_id(room.id).confirmed_ranges)} range(s)")

    print("\n2. Overlapping booking")
    try:
        service.confirm_booking(ConfirmBookingCommand(
            booking_reference="BK-9002",
            requester_id="student-7",
            room_id=room.id,
            start_time=datetime(2026, 10, 12, 10, 45),
            end_time=datetime(2026, 10, 12, 12, 0),
            attendees=5,
        ))
    except ValueError as e:
        print(f"  refused: {e}")

    print("\n3. More attendees than the room holds")
    try:
        service.confirm_booking(ConfirmBookingCommand(
            booking_reference="BK-9003",
            requester_id="student-3",
            room_id=room.id,
            start_time=datetime(2026, 10, 12, 14, 0),
            end_time=datetime(2026, 10, 12, 15, 0),
            attendees=20,
        ))
    except ValueError as e:
        print(f"  refused: {e}")

    print("\n4. Room that was never saved")
    try:
        service.confirm_booking(ConfirmBookingCommand(
            booking_reference="BK-9004",
            requester_id="student-11",
            room_id=4242,
            start_time=datetime(2026, 10, 12, 16, 0),
            end_time=datetime(2026, 10, 12, 17, 0),
            attendees=2,
        ))
    except ValueError as e:
        print(f"  refused: {e}")

    print("\n5. Cancel BK-9001")
    show(service.cancel_booking(CancelBookingCommand(booking_reference="BK-9001")))
    print(f"  room holds {len(room_repo.get_by_id(room.id).confirmed_ranges)} range(s)")


if __name__ == "__main__":
    main()