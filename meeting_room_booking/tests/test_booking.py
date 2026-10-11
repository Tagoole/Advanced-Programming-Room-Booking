"""
T1-T8.

    T1 -> BR1   value rule           rejection + boundary
    T2 -> BR2   identity/state       rejection
    T3 -> BR3   aggregate invariant  rejection
    T4 -> BR4   cross-concept        boundary
    T5 -> BR5   follow-up event
    T6 -> BR6   lookup rule          rejection
    T7 -> main use case end to end
    T8 -> Room refuses the follow-up action
"""

import pytest
from datetime import datetime, timedelta

from domain.value_objects.TimeRange import TimeRange
from domain.value_objects.BookingReference import BookingReference
from domain.value_objects.BookingStatus import BookingStatus
from domain.Booking import Booking
from domain.Room import Room
from domain.services import BookingDomainService
from domain.events.BookingConfirmed import BookingConfirmed
from application.dtos import ConfirmBookingCommand, CancelBookingCommand
from application.booking_service import BookingApplicationService
from infrastructure.booking_repository import InMemoryBookingRepository
from infrastructure.room_repository import InMemoryRoomRepository


def a_time_range(start_hour=10, hours=1, day=5):
    start = datetime(2026, 10, day, start_hour, 0)
    return TimeRange.create(start, start + timedelta(hours=hours))


def a_service():
    booking_repo = InMemoryBookingRepository()
    room_repo = InMemoryRoomRepository()
    service = BookingApplicationService(
        booking_repo, room_repo, BookingDomainService()
    )
    return service, booking_repo, room_repo


def test_t1_time_range_rejects_bad_values_and_checks_working_hours():
    with pytest.raises(ValueError, match="cannot end before"):
        TimeRange.create(
            datetime(2026, 10, 5, 10, 0),
            datetime(2026, 10, 5, 9, 0),
        )

    ending_at_six = TimeRange.create(
        datetime(2026, 10, 5, 17, 0),
        datetime(2026, 10, 5, 18, 0),
    )
    assert ending_at_six.end.hour == 18

    with pytest.raises(ValueError, match="08:00 and 18:00"):
        TimeRange.create(
            datetime(2026, 10, 5, 17, 0),
            datetime(2026, 10, 5, 18, 1),
        )


def test_t2_booking_keeps_its_reference_and_refuses_a_second_confirm():
    ref = BookingReference.create("BK-1001")
    booking = Booking(ref, 1, "user-1", a_time_range(), attendees=4)

    assert booking.status == BookingStatus.PENDING

    booking.confirm()
    assert booking.status == BookingStatus.CONFIRMED
    assert booking.reference == ref

    with pytest.raises(ValueError, match="Cannot confirm"):
        booking.confirm()

    assert booking.status == BookingStatus.CONFIRMED


def test_t3_room_refuses_an_overlapping_booking():
    room = Room("Board Room", capacity=10)
    first = a_time_range(start_hour=10)
    second = a_time_range(start_hour=10)

    room.accept_booking(first)

    with pytest.raises(ValueError, match="already booked"):
        room.accept_booking(second)

    assert len(room.confirmed_ranges) == 1



def test_t4_capacity_check_allows_exactly_full_and_refuses_one_more():
    room = Room("Small Office", capacity=10)
    service = BookingDomainService()

    exactly_full = Booking(
        BookingReference.create("BK-1002"), room.id, "user-1",
        a_time_range(), attendees=10,
    )
    service.check_room_can_accommodate(exactly_full, room)

    one_too_many = Booking(
        BookingReference.create("BK-1009"), room.id, "user-1",
        a_time_range(), attendees=11,
    )
    with pytest.raises(ValueError, match="cannot accommodate"):
        service.check_room_can_accommodate(one_too_many, room)



def test_t5_confirming_raises_the_booking_confirmed_event():
    ref = BookingReference.create("BK-1003")
    booking = Booking(ref, 1, "user-1", a_time_range(), attendees=3)

    booking.confirm()
    events = booking.get_domain_events()

    assert len(events) == 1
    assert isinstance(events[0], BookingConfirmed)
    assert events[0].booking_reference == ref
    assert events[0].room_id == 1



def test_t6_confirm_is_refused_when_the_room_was_never_saved():
    service, booking_repo, _ = a_service()

    command = ConfirmBookingCommand(
        booking_reference="BK-1004",
        requester_id="user-1",
        room_id=9999,
        start_time=datetime(2026, 10, 5, 10, 0),
        end_time=datetime(2026, 10, 5, 11, 0),
        attendees=2,
    )

    with pytest.raises(ValueError, match="does not exist"):
        service.confirm_booking(command)

    assert booking_repo.get_by_reference(
        BookingReference.create("BK-1004")
    ) is None



def test_t7_confirming_updates_the_room_and_saves_the_booking():
    service, booking_repo, room_repo = a_service()

    room = Room("Conference Room", capacity=20)
    room_repo.save(room)

    result = service.confirm_booking(ConfirmBookingCommand(
        booking_reference="BK-2001",
        requester_id="user-9",
        room_id=room.id,
        start_time=datetime(2026, 10, 6, 14, 0),
        end_time=datetime(2026, 10, 6, 15, 0),
        attendees=5,
    ))

    assert result.booking_reference == "BK-2001"
    assert result.status == "CONFIRMED"
    assert result.room_name == "Conference Room"
    assert any("BookingConfirmed" in e for e in result.events)

    assert len(room_repo.get_by_id(room.id).confirmed_ranges) == 1

    saved = booking_repo.get_by_reference(BookingReference.create("BK-2001"))
    assert saved.status == BookingStatus.CONFIRMED


def test_t8_room_refuses_the_follow_up_and_nothing_is_saved():
    service, booking_repo, room_repo = a_service()

    room = Room("Boardroom", capacity=10)
    room_repo.save(room)

    service.confirm_booking(ConfirmBookingCommand(
        booking_reference="BK-3001",
        requester_id="user-1",
        room_id=room.id,
        start_time=datetime(2026, 10, 7, 9, 0),
        end_time=datetime(2026, 10, 7, 10, 0),
        attendees=4,
    ))

    clashing = ConfirmBookingCommand(
        booking_reference="BK-3002",
        requester_id="user-2",
        room_id=room.id,
        start_time=datetime(2026, 10, 7, 9, 30),
        end_time=datetime(2026, 10, 7, 10, 30),
        attendees=2,
    )

    with pytest.raises(ValueError, match="already booked"):
        service.confirm_booking(clashing)

    assert booking_repo.get_by_reference(
        BookingReference.create("BK-3002")
    ) is None
    assert len(room_repo.get_by_id(room.id).confirmed_ranges) == 1