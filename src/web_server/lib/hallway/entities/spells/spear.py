from src.web_server.lib.hallway.Utils import direction_to_point, Point
from src.web_server.lib.hallway.cards.card import Card, available_cards
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity


class SpearSpell(SpellEntity):
    def __init__(self, player):
        card = available_cards["spear"]
        super().__init__(player, card)

