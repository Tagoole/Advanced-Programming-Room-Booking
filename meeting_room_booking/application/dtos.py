from dataclasses import dataclass
from datetime import datetime


@dataclass
class ConfirmBookingCommand:
    """Input DTO for Use Case 1: Confirm a booking."""
    booking_reference: str
    requester_id: str
    room_id: int
    start_time: datetime
    end_time: datetime
    attendees: int


@dataclass
class CancelBookingCommand:
    """Input DTO for Use Case 2: Cancel a booking."""
    booking_reference: str


@dataclass
class BookingResult:
    """Output DTO returned by both use cases.

    Everything here is a plain string, so whatever calls the service
    never has to import a domain class just to read the outcome.
    """
    booking_reference: str
    status: str
    room_name: str
    events: tuple[str, ...]

    def __str__(self) -> str:
        return f"{self.booking_reference} is {self.status} in {self.room_name}"