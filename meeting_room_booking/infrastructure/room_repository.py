

from application.repositories import RoomRepository
from domain.Room import Room


class InMemoryRoomRepository(RoomRepository):

    def __init__(self):
        self._rooms: dict[int, Room] = {}

    def save(self, room: Room) -> None:
        # We use the Entity's technical id as the storage key.
        self._rooms[room.id] = room

    def get_by_id(self, room_id: int) -> Room | None:
        return self._rooms.get(room_id)
