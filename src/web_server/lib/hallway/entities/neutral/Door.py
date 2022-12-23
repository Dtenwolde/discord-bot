from src.web_server.lib.hallway.entities.player_class import PlayerClass
from src.web_server.lib.hallway.entities.entity import Entity


class Key(Entity):
    def __init__(self, game):
        super().__init__(game)
        self.picked_up = False
        self.can_move_through = True

        self.animation_sprite_names = (
                (["key_0"] * 3 + ["key_1"] * 3) * 4 +
                (["key_0"] * 3 + ["key_2", "key_3", "key_2"])
        )
        self.frame_duration = 5
        self.sprite_name = self.animation_sprite_names[0]
        self.animating = True
        self.loop = True

    def collide(self, other: Entity):
        if isinstance(other, PlayerClass):
            self.picked_up = True
            self.die()

    def start(self):
        pass


class Door(Entity):
    def __init__(self, game, orientation="vertical"):
        assert orientation in ["vertical", "horizontal"], "Invalid door orientation passed."
        super().__init__(game)

        self.can_move_through = False
        self._key = Key(game)
        self.key_gotten = False

        self.animation_sprite_names = [
            f"door_{orientation[0]}_{i}" for i in range(4)
        ]
        self.sprite_name = self.animation_sprite_names[0]

        self.opening = False

    def get_key(self):
        self.key_gotten = True
        return self._key

    def start(self):
        assert self.key_gotten, "Ensure you add the doors' key to the list of entities. " \
                                "Get this key with door_object.get_key()"

    def tick(self):
        super().tick()
        if self.opening is True and self.animating is False:
            self.can_move_through = True
            self.opening = False

    def collide(self, other: Entity):
        if isinstance(other, PlayerClass):
            if self._key.picked_up and not self.can_move_through:
                self.animating = True
                self.opening = True
