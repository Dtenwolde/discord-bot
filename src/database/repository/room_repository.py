from database import db
from src.database.models.models import GameRoom


def get_rooms():
    return db.session.query(GameRoom).all()


def get_room(room_id: int):
    return db.session.query(GameRoom).filter(GameRoom.id == room_id).one_or_none()


def find_room_by_message_id(message_id: int):
    return db.session.query(GameRoom).filter(GameRoom.message_id == message_id).all()

