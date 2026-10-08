from .shared.AggregateRoot import AggregateRoot
from .value_objects.TimeRange import TimeRange

class Room(AggregateRoot):

    def __init__(self, name: str, capacity:int):
        super().__innit__()

        if not name or not name.strip():
            raise ValueError("Room name cannot be empty")

        if capacity <= 0:
            raise ValueError("Room capacity must be greater than zero")

        self._name = name.strip()
        self._capacity = capacity

        self._confirmed_ranges: list[TimeRange] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def confirmed_ranges(self) -> tuple[TimeRange, ...]:
        return tuple(self._confirmed_ranges)

    