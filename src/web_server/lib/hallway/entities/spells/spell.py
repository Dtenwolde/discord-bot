from typing import Optional

from src.web_server.lib.hallway.Utils import direction_to_point, Point, EntityDirections
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity


class SpellEntity(MovableEntity):
    card: Card = None

    def __init__(self, player, animation_length=1):
        super().__init__(player.game)

        self.position = player.position
        self.direction: Optional[EntityDirections] = player.direction if self.card.ability_range != 0 else None
        self.movement_cooldown = 4
        self.movement_queue = [direction_to_point(player.direction)] * self.card.ability_range

        waiting_ticks = max(0, animation_length - len(self.movement_queue))
        self.movement_queue.extend([Point(0, 0)] * waiting_ticks)
        self.entities = [self]
        self.death_callback = None

    def prepare_movement(self):
        pass

    def collide(self, other: Entity) -> bool:
        return True

    def movement_action(self):
        return super().movement_action()

    def post_movement_action(self):
        super().post_movement_action()
        self.die()


