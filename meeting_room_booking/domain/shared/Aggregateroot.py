from abc import abstractmethod
from .Entity import Entity
from .DomainEvent import DomainEvent


class AggregateRoot(Entity):
    