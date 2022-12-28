import random

from src.web_server.lib.hallway.entities.enemies.Slime import EnemyClass
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.Utils import Point


class EntitySpawner(MovableEntity):
    def __init__(self, game, entity: type(EnemyClass), **kwargs):
        super().__init__(game)
        self.to_spawn = entity
        self.kwargs = kwargs

    def prepare_movement(self):
        pass

    def collide(self, other: Entity) -> bool:
        return True

    def post_movement_action(self):
        if len(self.game.enemies) > 20 or self.game._turn % 2 == 1:
            return

        enemy = self.to_spawn(self.game, **self.kwargs)

        tries = 0
        while not self.game.board[enemy.position.x][enemy.position.y].movement_allowed:
            enemy.position = self.position + Point(random.randint(-4, 4), random.randint(-4, 4))
            tries += 1

            if tries == 10:
                return
        print(f"Spawning enemy at {enemy.position}")
        self.game.enemies.append(enemy)
