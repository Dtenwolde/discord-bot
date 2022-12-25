from typing import List

from src.web_server.lib.hallway.Utils import Point, EntityDirections
from src.web_server.lib.hallway.algorithms import pathfinding
from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity


class EnemyClass(MovableEntity):
    def __init__(self, sprite_name: str, game):
        super().__init__(game)
        self.MAX_MOVEMENT = 6
        self.sprite_name = sprite_name
        self.spawn_position = Point(1, 1)
        self.position = Point(1, 1)
        self.last_position = self.position
        self.class_name = None

        self.dead = False
        self.can_move = True

        self.updated = True

        self.movement_cooldown = 10  # Ticks
        self.movement_timer = 0
        self.movement_queue = []
        self.moving = False

        self.direction = EntityDirections.DOWN

        from src.web_server.lib.hallway.hallway_hunters import HallwayHunters
        self.game: HallwayHunters = game

        self.passives: List[Passive] = []

        # Fixed stats
        self.damage = 2
        self.hp = 1

    def collide(self, other):
        if isinstance(other, SpellEntity):
            other: SpellEntity
            if other.card.damage_type != "heal":
                self.hp -= other.card.damage
            if self.hp <= 0:
                self.die()

        return other.can_move_through

    def start(self):
        super().start()
        self.direction = EntityDirections.DOWN

    def die(self):
        self.dead = True
        self.can_move = False
        self.movement_queue.clear()
        super().die()

    def tick(self):
        super().tick()

        for passive in self.passives[:]:
            passive.tick()
            if passive.time == 0:
                self.passives.remove(passive)

    def to_json(self):
        state = super().to_json()
        state.update({
            "dead": self.dead,
        })
        return state

    def prepare_movement(self):
        if self.dead:
            return

        path = pathfinding.astar(self.game.board, self.position, self.game.player_list[0].position)
        self.movement_queue = path[:self.MAX_MOVEMENT]