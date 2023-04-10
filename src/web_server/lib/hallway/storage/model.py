import sqlalchemy
from sqlalchemy import String, JSON, Column, Integer

from src.web_server.lib.hallway.storage.database import GameBase


class StoredDeck(GameBase):
    __tablename__ = "deck"

    player_name = Column(String, primary_key=True)
    money = Column(Integer)

    active_deck = Column(JSON)
    obtained_cards = Column(JSON)
