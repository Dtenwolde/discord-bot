from typing import Optional

from web_server.lib.game.Items import Item


class Tile:
    """
    Generic class, don't initialize this directly, use subclasses instead.
    """
    def __init__(self):
        self.image = "default_texture.png"
        self.movement_allowed = True
        self.opaque = True
        self.item: Optional[Item] = None

    def to_json(self):
        return {
            "image": self.image,
            "movement_allowed": self.movement_allowed,
            "opaque": self.opaque,
            "item": self.item.to_json() if self.item else None,
        }


class GroundTile(Tile):
    def __init__(self):
        super().__init__()
        self.image = ""

        self.movement_allowed = True
        self.opaque = False

