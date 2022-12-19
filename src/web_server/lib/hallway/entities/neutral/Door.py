from src.web_server.lib.hallway.entities.player_class import PlayerClass
from src.web_server.lib.hallway.entities.entity import Entity


class Key(Entity):
    def __init__(self, game):
        super().__init__(game)
        self.sprite_name = f"key"
        self.picked_up = False
        self.can_move_through = True

    def collide(self, other: Entity):
        if isinstance(other, PlayerClass):
            self.picked_up = True
            self.die()

    def tick(self):
        pass

    def start(self):
        pass


class Door(Entity):
    def __init__(self, game, orientation="vertical"):
        assert orientation in ["vertical", "horizontal"], "Invalid door orientation passed."
        super().__init__(game)
        self.sprite_name = f"door_{orientation[0]}"

        self.can_move_through = False
        self._key = Key(game)
        self.key_gotten = False

    def get_key(self):
        self.key_gotten = True
        return self._key

    def start(self):
        assert self.key_gotten, "Ensure you add the doors' key to the list of entities. " \
                                 "Get this key with door_object.get_key()"

    def tick(self):
        pass

    def collide(self, other: Entity):
        if isinstance(other, PlayerClass):
            if self._key.picked_up:
                self.can_move_through = True
