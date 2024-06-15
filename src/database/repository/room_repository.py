from typing import List

from src.database import db
from src.database.models.models import GameRoom


def get_rooms() -> List[GameRoom]:
    return db.session.query(GameRoom).all()


def get_room(room_id: int) -> GameRoom:
    return db.session.query(GameRoom).filter(GameRoom.id == room_id).one_or_none()


def find_room_by_message_id(message_id: int) -> List[GameRoom]:
    return db.session.query(GameRoom).filter(GameRoom.message_id == message_id).all()
