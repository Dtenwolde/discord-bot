from abc import abstractmethod, ABCMeta

from src.web_server.lib.hallway.Utils import EntityDirections, direction_to_point
from src.web_server.lib.hallway.entities.entity import Entity, EntityAnimationFrames
from src.web_server.lib.hallway.exceptions import InvalidAction


class MovableEntity(Entity, metaclass=ABCMeta):
    def __init__(self, game, unique_identifier=None):
        super().__init__(game, unique_identifier)
        self.can_move = True

        self.MAX_MOVEMENT = 10

        self.movement_cooldown = 2  # Ticks
        self.movement_timer = 0
        self.movement_queue = []
        self.moving = False

        self.direction = EntityDirections.DOWN

    def die(self):
        super().die()
        self.movement_queue = []
        self.moving = False
        self.movement_timer = 0

    def start(self):
        self.movement_timer = 0

    def tick(self):
        if self.animation_frames is not None:
            if self.moving:
                # Begin with starting frames
                if self.animation_frames.state == EntityAnimationFrames.State.IDLE:
                    self.animation_frames.state = EntityAnimationFrames.State.STARTING
                    self.current_tick = 0
                    self.loop = False
                    self.animating = True
                # When done with the non-looping starting frames, set moving animation
                elif not self.animating:
                    self.animation_frames.state = EntityAnimationFrames.State.MOVING
                    self.current_tick = 0
                    self.loop = True
                    self.animating = True
            else:
                # Go back to the idle loop
                if not self.animating:
                    self.animation_frames.state = EntityAnimationFrames.State.IDLE
                    self.current_tick = 0
                    self.loop = True
                    self.animating = True

        super().tick()

        self.movement_timer = max(0, self.movement_timer - 1)
        if self.movement_timer == 0 and len(self.movement_queue) > 0:
            try:
                self.movement_action()
            except InvalidAction as e:
                pass

    def post_movement_action(self):
        if self.animation_frames is not None:
            self.animation_frames.state = EntityAnimationFrames.State.ENDING
            self.current_tick = 0
            self.loop = False
            self.animating = True

        self.moving = False

    def change_position(self, point):
        self.position = point

    def movement_action(self):
        """
        Performs the movement action, and will raise an InvalidAction exception if the move is not allowed.
        It will return the attempted move, which may result in some additional logic in the inherited class.
        :return:
        """
        if not self.can_move:
            self.moving = False
            raise InvalidAction("You cannot move.")

        if len(self.movement_queue) == 0:
            self.moving = False
            raise InvalidAction("There are no moves left in the queue for you.")

        move = self.movement_queue.pop(0)

        # Set the correct player model direction based on input
        if move.x == 1:
            self.direction = EntityDirections.RIGHT
        elif move.x == -1:
            self.direction = EntityDirections.LEFT
        elif move.y == 1:
            self.direction = EntityDirections.DOWN
        elif move.y == -1:
            self.direction = EntityDirections.UP
        else:
            self.moving = False
            self.direction = None

        # Compute temporary position based on next move
        new_position = move + self.position
        # Check move validity
        if new_position.x > self.game.size - 1 or \
                new_position.y > self.game.size - 1 or \
                new_position.x < 0 or new_position.y < 0:
            self.moving = False
            raise InvalidAction("You cannot move out of bounds.")

        self.movement_timer = self.movement_cooldown
        tile = self.game.board[new_position.x][new_position.y]
        if not tile.movement_allowed:
            self.moving = False
            raise InvalidAction("You cannot move on this tile.")

        can_move_through = True
        for entity in self.game.get_entities_at(new_position):
            if entity is self:
                continue

            can_move_through &= self.collide(entity)
            entity.collide(self)

        self.moving = self.can_move_through
        if can_move_through:
            # Reset the movement timer
            self.position = new_position
            return move

        self.moving = False
        raise InvalidAction("An entity is preventing you from moving to this tile.")

    def get_interpolated_position(self):
        if self.direction is None or not self.moving:
            return self.position

        progress = self.movement_timer / self.movement_cooldown

        position = self.position + (-1 * direction_to_point(self.direction)) * progress
        return position

    def to_json(self):
        state = super().to_json()
        state.update({
            "position": self.get_interpolated_position().to_json(),
            "direction": self.direction.value if self.direction is not None else None,
            "moving": self.moving,
        })
        return state
