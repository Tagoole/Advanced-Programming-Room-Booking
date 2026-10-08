from abc import ABC, abstractmethod


class Entity(ABC):
    _id_counters: dict[type, int] = {}