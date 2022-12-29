from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from src.web_server.lib.hallway.Utils import Point, EntityDirections
from abc import abstractmethod


class EntityAnimationFrames:
    class State(Enum):
        IDLE = 0
        STARTING = 1
        MOVING = 2
        ENDING = 3

    def __init__(self, idle_frames, move_frames=None, start_move_frames=None, end_move_frames=None):
        self._frames = {
            self.State.IDLE: idle_frames,
            self.State.STARTING: start_move_frames,
            self.State.MOVING: move_frames,
            self.State.ENDING: end_move_frames
        }
        self.state = self.State.IDLE

    def get_animation_frames(self):
        assert self._frames[self.state] is not None, f"You did not specify an animation for '{self.state.name}'."
        return self._frames[self.state]


class SimpleEntityAnimationFrames:
    def __init__(self, frames):
        self.frames = frames
        self.state = None  # Set this to be consistent with EntityAnimationFrames

    def get_animation_frames(self):
        return self.frames


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


class EntityStat(object):
    def __init__(self, current, total):
        super().__init__()
        self.max = total
        self.current = current

    def __add__(self, other):
        if isinstance(other, int):
            return EntityStat(clamp(self.current + other, 0, self.max), self.max)
        raise NotImplemented("Err")

    def __sub__(self, other):
        if isinstance(other, int):
            return EntityStat(clamp(self.current - other, 0, self.max), self.max)
        raise NotImplemented("Err")

    def __lt__(self, other):
        if isinstance(other, int):
            return self.current < other
        raise NotImplemented("Err")

    def __le__(self, other):
        if isinstance(other, int):
            return self.current <= other
        raise NotImplemented("Err")

    def __ge__(self, other):
        if isinstance(other, int):
            return self.current >= other
        raise NotImplemented("Err")

    def __repr__(self):
        return f"{self.current}/{self.max}"

    def set_max(self, new_max):
        self.max = new_max
        self.current = new_max


class HPStat(EntityStat):
    def __init__(self, current, total, entity):
        super().__init__(current, total)
        self.entity = entity

    def __sub__(self, other):
        value = super().__sub__(other)
        if value.current <= 0:
            self.entity.die()
        return HPStat(value.current, value.max, self.entity)

    def __add__(self, other):
        value = super().__add__(other)
        if value.current <= 0:
            self.entity.die()
        return HPStat(value.current, value.max, self.entity)


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
        self.direction = None

        from src.web_server.lib.hallway.hallway_hunters import HallwayHunters
        self.game: HallwayHunters = game

        # Animation variables
        self.animating = False
        self.loop = False
        self.directional_animation_frames: dict[EntityDirections, Optional[EntityAnimationFrames]] = {
            EntityDirections.UP: None,
            EntityDirections.DOWN: None,
            EntityDirections.LEFT: None,
            EntityDirections.RIGHT: None,
        }
        self.animation_frames = None
        self.animation_zoom = []
        self.frame_duration = 5
        self.current_tick = 0

        # Current sprite string and the zoom level
        self.sprite_name = None
        self.zoom = 1

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

    def tick(self):
        """
        Every entity-tick, this function will get called.
        An entity-tick will happen at the server tick-rate
        :return:
        """
        if self.animating:
            # Check if we have a direction, and directional animations are set
            if self.direction is not None and self.directional_animation_frames[self.direction] is not None:
                self.animation_frames = self.directional_animation_frames[self.direction]

            frames = self.animation_frames.get_animation_frames()

            self.current_tick = (self.current_tick + 1) % (self.frame_duration * len(frames))

            # Check if we reached the end of the animation
            if self.current_tick == 0 and not self.loop:
                self.animating = False
                return

            current_frame = self.current_tick // self.frame_duration

            # Set current animation sprite and zoom level
            self.sprite_name = frames[current_frame]
            if len(self.animation_zoom) == len(frames):
                self.zoom = self.animation_zoom[current_frame]
            else:
                self.zoom = 1

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
            "zoom": self.zoom,
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

    def before_turn_action(self):
        pass
