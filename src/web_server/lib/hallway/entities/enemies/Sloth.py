from src.web_server.lib.hallway.Utils import EntityDirections
from src.web_server.lib.hallway.entities.enemies import EnemyClass
from src.web_server.lib.hallway.entities.entity import EntityAnimationFrames


class Sloth(EnemyClass):
    def __init__(self, game):
        super().__init__("sloth", game)
        self.hp = 2
        self.MAX_MOVEMENT = 3
        self.movement_cooldown = 25

        # Set right and up animation frames
        idle_ru = [f"sloth_{i}" for i in range(2)]
        move_ru = [f"sloth_{i}" for i in [0, 2, 3]]
        ru = EntityAnimationFrames(
            idle_ru, move_ru,
            idle_ru[:1], idle_ru[:1]
        )

        # Set left and down animation frames
        idle_ld = [f"sloth_{7 - i}" for i in range(2)]
        move_ld = [f"sloth_{7 - i}" for i in [0, 2, 3]]
        ld = EntityAnimationFrames(
            idle_ld, move_ld,
            idle_ld[:1], idle_ld[:1]
        )

        self.directional_animation_frames[EntityDirections.RIGHT] = ru
        self.directional_animation_frames[EntityDirections.UP] = ru
        self.directional_animation_frames[EntityDirections.LEFT] = ld
        self.directional_animation_frames[EntityDirections.DOWN] = ld

        self.frame_duration = 10
        self.sprite_name = idle_ld[0]
        self.animating = True
        self.loop = True

    def tick(self):
        super().tick()
