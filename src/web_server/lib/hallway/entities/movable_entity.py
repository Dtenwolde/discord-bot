from abc import abstractmethod

from src.web_server.lib.hallway.Utils import EntityDirections, direction_to_point
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.exceptions import InvalidAction


class MovableEntity(Entity):
    MAX_MOVEMENT = 10

    def __init__(self, game, unique_identifier=None):
        super().__init__(game, unique_identifier)
        self.can_move = True

        self.movement_cooldown = 2  # Ticks
        self.movement_timer = 0
        self.movement_queue = []
        self.moving = False

        self.direction = EntityDirections.DOWN

    def start(self):
        self.movement_timer = 0

    def tick(self):
        self.movement_timer = max(0, self.movement_timer - 1)

    def change_position(self, point):
        self.position = point

    def movement_action(self):
        """
        Performs the movement action, and will raise an InvalidAction exception if the move is not allowed.
        It will return the attempted move, which may result in some additional logic in the inherited class.
        :return:
        """
        if not self.can_move:
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

        # Compute temporary position based on next move
        new_position = move + self.position
        # Check move validity
        if new_position.x > self.game.size - 1 or \
                new_position.y > self.game.size - 1 or \
                new_position.x < 0 or new_position.y < 0:
            raise InvalidAction("You cannot move out of bounds.")

        tile = self.game.board[new_position.x][new_position.y]
        if not tile.movement_allowed:
            raise InvalidAction("You cannot move on this tile.")

        # Reset the movement timer
        self.movement_timer = self.movement_cooldown
        from src.web_server.lib.hallway.entities.player_class import PlayerClass

        can_move_through = True
        for entity in self.game.get_entities_at(new_position):
            if entity is self:
                continue

            can_move_through &= self.collide(entity)

            if isinstance(self, PlayerClass):
                print(can_move_through, entity, entity.can_move_through)

            entity.collide(self)

        if isinstance(self, PlayerClass):
            print(can_move_through, new_position)
        if can_move_through:

            self.position = new_position
            self.moving = True

            return move

        raise InvalidAction("An entity is preventing you from moving to this tile.")

    def get_interpolated_position(self):
        if self.direction is None:
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

    def die(self):
        self.alive = False
        self.game.entities.remove(self)

    @abstractmethod
    def post_movement_action(self):
        pass

    @abstractmethod
    def prepare_movement(self):
        pass
