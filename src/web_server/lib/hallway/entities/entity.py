from __future__ import annotations

import uuid
from src.web_server.lib.hallway.Utils import Point
from abc import abstractmethod


class Entity:
    """
    A generic entity class.
    It contains a list of information:
     - uid, which is used to keep track of entities on client-side.
     - position, its location on the map
     - game, the game of which this entity is part
     - can_move_through: bool, solid units have to check if they can move through the entity with this variable
    """
    def __init__(self, game, unique_identifier=None):
        if unique_identifier is None:
            unique_identifier = str(uuid.uuid4())
        self.uid = unique_identifier
        self.position = Point(1, 1)

        from src.web_server.lib.hallway.hallway_hunters import HallwayHunters
        self.game: HallwayHunters = game

        self.sprite_name = None

        self.class_name = None

        self.updated = True
        self.alive = True
        self.can_move_through = True

    @abstractmethod
    def start(self):
        """
        This function will get called when the game starts.
        It is only relevant for entities which are spawned before the game started.
        :return:
        """
        pass

    @abstractmethod
    def tick(self):
        """
        Every entity-tick, this function will get called.
        An entity-tick will happen twice per round, once after the player turn, and once after the enemy turn.
        :return:
        """
        pass

    @abstractmethod
    def collide(self, other: Entity) -> bool:
        """
        The collide function will be called when this entity enters the same space as another entity.
        Depending on the return value of this function is movement allowed.
        When this function returns true, movement is allowed, otherwise it is not.

        :param other: the other entity with which collision is detected
        :return bool: is this movement allowed
        """
        pass

    def to_json(self):
        """
        Takes the relevant shareable parameters and creates a dictionary out of them.
        :return:
        """

        if self.sprite_name is None:
            print(type(self))
            raise AttributeError("sprite_name is unset, this cannot be shared with the user.")

        state = {
            "uid": self.uid,
            "sprite_name": self.sprite_name,
            "position": self.position.to_json()
        }
        return state

    def die(self):
        """
        Use this to remove entities from the game.
        Dying will ensure the entity will also get removed from all player's rendered screens.
        :return:
        """
        self.alive = False
        self.game.remove_entity(self)
