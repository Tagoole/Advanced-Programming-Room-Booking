from abc import ABC, abstractmethod
from domain.Booking import Booking
from domain.Room import Room
from domain.value_objects.BookingReference import BookingReference

class BookingRepository(ABC):
  """Abstract interface — Domain and Application depend on this,
    never on a concrete storage technology."""
    
  @abstractmethod
  def save( self, booking: Booking) -> None:
    """Save a booking to the repository."""
    pass
  
  @abstractmethod
  def get_by_reference(self, reference: BookingReference) -> Booking:
    """Retrieve a booking by its reference."""
    pass
  
  @abstractmethod
  def get_by_room(self, room: Room) -> list[Booking]:
    """Retrieve all bookings for a specific room."""
    pass
  
class RoomRepository(ABC):
  """Abstract interface for the Room Aggregate."""
  
  @abstractmethod
  def save(self, room: Room) -> None:
    """Save a room to the repository."""
    pass
  
  @abstractmethod
  def get_by_id(self, room_id: int) -> Room | None:
    """Retrieve a room by its ID."""
    pass
  
  