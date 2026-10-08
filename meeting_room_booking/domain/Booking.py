from datetime import datetime
from .shared.AggregateRoot import AggregateRoot
from .value_objects.BookingReference import BookingReference
from .value_objects.TimeRange import TimeRange
from .value_objects.BookingStatus import BookingStatus
from .events.BookingConfirmed import BookingConfirmed
from .events.BookingCancelled import BookingCancelled