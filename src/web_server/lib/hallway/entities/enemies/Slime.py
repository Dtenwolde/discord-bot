from src.web_server.lib.hallway.entities.enemies import EnemyClass


class Slime(EnemyClass):
    def __init__(self, game):
        super().__init__("slime", game)
        self.hp = 2
