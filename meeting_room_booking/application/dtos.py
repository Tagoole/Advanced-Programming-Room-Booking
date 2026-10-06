#Data Transfer Objects.


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
    attendees: int   # added so BookingDomainService can check BR4
    
    
@dataclass
class CancelBookingCommand:
    """Input DTO for Use Case 2: Cancel a booking."""
    booking_reference: str
   
