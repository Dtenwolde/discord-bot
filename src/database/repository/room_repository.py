from src.web_server.lib.hallway.storage.database import db


def get_rooms():
    collection = db['gameRoom']
    return list(collection.find())


def get_room(room_id: int):
    collection = db['room']
    return collection.find_one({"message_id": room_id})


def find_room_by_message_id(message_id: int):
    collection = db['gameRoom']
    return collection.find_one({"message_id": message_id})
