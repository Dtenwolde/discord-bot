from sqlalchemy import String, JSON, Column, Integer

from src.database import db


class StoredDeck(db.Model):
    __tablename__ = "deck"

    player_name = Column(String, primary_key=True)
    money = Column(Integer)

    active_deck = Column(JSON)
    obtained_cards = Column(JSON)
