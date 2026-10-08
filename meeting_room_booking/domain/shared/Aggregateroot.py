from abc import abstractmethod
from .Entity import Entity
from .DomainEvent import DomainEvent


class AggregateRoot(Entity):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        self._domain_events: list[DomainEvent] = []

    def _raise_domain_event(self, domain_event: DomainEvent) -> None:
        """Called internally by subclasses (e.g. Booking.confirm())
        AFTER a state change has already succeeded — never before."""
        self._domain_events.append(domain_event)

    def get_domain_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._domain_events)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()