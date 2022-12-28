from src.web_server.lib.hallway.Utils import EntityDirections
from src.web_server.lib.hallway.entities.enemies import EnemyClass
from src.web_server.lib.hallway.entities.entity import EntityAnimationFrames


class MonkeyBall(EnemyClass):

    def __init__(self, game):
        super().__init__("monkeyball", game)
        self.hp = 2

        self.MAX_MOVEMENT = 10
        self.BASE_MOVEMENT = 10

        # Set right and up animation frames
        self.idle_ru = [f"monkeyball_{i}_ru" for i in range(2)]
        self.start_ru = [f"monkeyball_{i}_ru" for i in range(3)]
        self.move_ru = [f"monkeyball_{i + 3}_ru" for i in range(4)]
        self.end_ru = list(reversed(self.start_ru))
        ru = EntityAnimationFrames(
            self.idle_ru, self.move_ru,
            self.start_ru, self.end_ru
        )

        # Set left and down animation frames
        self.idle_ld = [f"monkeyball_{i}_ld" for i in range(2)]
        self.start_ld = [f"monkeyball_{i}_ld" for i in range(3)]
        self.move_ld = [f"monkeyball_{i + 3}_ld" for i in range(4)]
        self.end_ld = list(reversed(self.start_ld))
        ld = EntityAnimationFrames(
            self.idle_ld, self.move_ld,
            self.start_ld, self.end_ld
        )

        self.directional_animation_frames[EntityDirections.RIGHT] = ru
        self.directional_animation_frames[EntityDirections.UP] = ru
        self.directional_animation_frames[EntityDirections.LEFT] = ld
        self.directional_animation_frames[EntityDirections.DOWN] = ld

        self.frame_duration = 5
        self.sprite_name = "monkeyball_0"
        self.animating = True
        self.loop = True

    def tick(self):
        super().tick()
