from src.web_server.lib.hallway.entities.entity import Entity, SimpleEntityAnimationFrames
from src.web_server.lib.hallway.entities.player_class import PlayerClass


class Chest(Entity):
    def __init__(self, game):
        super().__init__(game)

        self.can_move_through = False

        self.animation_frames = SimpleEntityAnimationFrames([
            f"chest_red_{i}" for i in range(5)
        ])
        self.sprite_name = self.animation_frames.get_animation_frames()[0]
        self.opened = False
        self.loot = []

    def start(self):
        pass

    def collide(self, other: Entity):
        if not self.opened and isinstance(other, PlayerClass):
            self.animating = True
            self.opened = True

            other.deck.hand.extend(self.loot)
            self.loot.clear()

    def add_loot(self, loot):
        self.loot.append(loot)
