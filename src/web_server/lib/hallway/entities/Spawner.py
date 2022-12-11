import random

from src.web_server.lib.hallway.entities.Enemies import EnemyClass
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.Utils import Point


class EntitySpawner(MovableEntity):
    def __init__(self, game, entity: type(EnemyClass), **kwargs):
        super().__init__(game)
        self.to_spawn = entity
        self.kwargs = kwargs

    def post_movement_action(self):
        if len(self.game.enemies) > 20 or self.game.turn % 2 == 1:
            return

        enemy = self.to_spawn(self.game, **self.kwargs)

        while not self.game.board[enemy.position.x][enemy.position.y].movement_allowed:
            enemy.position = self.position + Point(random.randint(-4, 4), random.randint(-4, 4))
        print(f"Spawning enemy at {enemy.position}")
        self.game.enemies.append(enemy)
