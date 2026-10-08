from abc import ABC, abstractmethod


class Entity(ABC):
    _id_counters: dict[type, int] = {}
    @abstractmethod
    def __init__(self) -> None:
        subclass = type(self)
        Entity._id_counters[subclass] = Entity._id_counters.get(subclass, 0) + 1
        self._id: int = Entity._id_counters[subclass]

    @property
    def id(self) -> int:
            return self._id
    
    def __eq__(self, other: object) -> bool:
            if not isinstance(other, Entity):
                return False
            if type(self) is not type(other):
                return False
            return self.id == other.id
    
    def __hash__(self) -> int:
            return hash(self.id)