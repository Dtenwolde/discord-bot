from typing import List

from src.web_server.lib.hallway.Utils import Point, EntityDirections
from src.web_server.lib.hallway.algorithms import pathfinding
from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.entity import EntityStat, HPStat
from src.web_server.lib.hallway.entities.spells.spell import SpellEntity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity


class EnemyClass(MovableEntity):
    def __init__(self, sprite_name: str, game):
        super().__init__(game)
        self.MAX_MOVEMENT = 6
        self.BASE_MOVEMENT = 10

        self.sprite_name = sprite_name
        self.spawn_position = Point(1, 1)
        self.position = Point(1, 1)
        self.last_position = self.position
        self.class_name = None

        self.dead = False
        self.can_move = True

        self.updated = True

        self.movement_cooldown = self.BASE_MOVEMENT  # Ticks
        self.movement_timer = 0
        self.movement_queue = []
        self.moving = False

        self.direction = EntityDirections.DOWN

        from src.web_server.lib.hallway.hallway_hunters import HallwayHunters
        self.game: HallwayHunters = game

        self.passives: List[Passive] = []

        # Fixed stats
        self.damage = 2
        self.hp = HPStat(1, 1, self)
        self.mana = EntityStat(0, 0)

    def collide(self, other):
        if isinstance(other, SpellEntity):
            other: SpellEntity
            if other.card.damage_type != "heal":
                self.hp -= other.card.damage

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

    def to_json(self):
        state = super().to_json()
        state.update({
            "dead": self.dead,
        })
        return state

    def post_movement_action(self):
        super().post_movement_action()

        # Apply passive timing
        for passive in self.passives[:]:
            passive.tick()
            if passive.time == 0:
                self.passives.remove(passive)

    def before_turn_action(self):
        if self.dead:
            return

        path = pathfinding.astar(self.game.board, self.position, self.game.player_list[0].position)
        self.movement_queue = path[:self.MAX_MOVEMENT]
        self.movement_cooldown = self.BASE_MOVEMENT
