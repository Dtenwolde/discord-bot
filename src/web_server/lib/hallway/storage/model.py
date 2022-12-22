import sqlalchemy
from sqlalchemy import String, JSON

from src.web_server.lib.hallway.storage.database import GameBase


class StoredDeck(GameBase):
    __tablename__ = "deck"

    player_name = String()
    active_deck = JSON()
    obtained_cards = JSON()
