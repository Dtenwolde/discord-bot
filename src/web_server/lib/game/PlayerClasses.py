import copy
import random
from typing import Optional, List, Tuple, Callable

from database.models.models import Profile
from src.web_server.lib.game.Items import RubbishItem, Item, CollectorItem
from src.web_server.lib.game.Tiles import GroundTile, WallTile, LadderTile, ChestTile
from src.web_server.lib.game.Utils import Point, PlayerAngles, direction_to_point, line_of_sight_endpoints, \
    point_interpolator
from src.web_server.lib.game.exceptions import InvalidAction

DEMOLISHER_COOLDOWN = 30  # Seconds
SPY_COOLDOWN = 30  # Seconds
SCOUT_COOLDOWN = 30  # Seconds
MRMOLE_COOLDOWN = 10  # Seconds


MOVEMENT_COOLDOWN = 8  # Ticks
SPRINT_COOLDOWN = 10 * 60  # Ticks
KILL_COOLDOWN = 10 * 60  # Ticks


class Passive(object):
    def __init__(self, time, callback, name="", args=()):
        self.name = name
        self.total_time = time
        self.time = time
        self.callback = callback
        self.args = args

    def tick(self):
        self.time -= 1
        if self.time == 0:
            self.callback(*self.args)

    def to_json(self):
        """
        Converts the passive to json, maybe for later to display all active passives

        :return:
        """
        return {
            "name": self.name,
            "time": self.time,
            "total_time": self.total_time,
        }


class PlayerClass:
    def __init__(self, profile: Profile, socket_id, game):
        self.name = ""
        self.profile = profile
        self.spawn_position = Point(1, 1)
        self.position = Point(1, 1)
        self.last_position = self.position
        self.move_suggestion = None

        self.movement_cooldown = MOVEMENT_COOLDOWN  # Ticks
        self.movement_timer = 0
        self.is_moving = False

        self.ability_cooldown = 0
        self.cooldown_timer = 0  # Ticks

        self.sprint_cooldown = SPRINT_COOLDOWN
        self.sprint_timer = 0

        self.kill_cooldown = KILL_COOLDOWN
        self.kill_timer = 0
        self.killing: Optional[PlayerClass] = None

        self.ready = False
        self.direction = PlayerAngles.DOWN

        # The item you are holding
        self.item: Optional[Item] = None
        self.stored_items: List[Item] = []

        self.objective: Point = Point(0, 0)

        self.passives: List[Passive] = []

        self.visible_tiles = []

        from src.web_server.lib.game.HallwayHunters import HallwayHunters
        self.game: HallwayHunters = game

        self.socket = socket_id

    def start(self):
        self.stored_items = []
        self.cooldown_timer = 0
        self.movement_timer = 0
        self.direction = PlayerAngles.DOWN
        self.visible_tiles = self.compute_line_of_sight()
        self.generate_item()

    def ability(self):
        if self.cooldown_timer != 0:
            raise InvalidAction("Ability on cooldown, %d remaining." % self.cooldown_timer)

    def sprint(self):
        if self.sprint_timer != 0:
            raise InvalidAction("Sprint on cooldown, %d remaining." % self.sprint_timer)

        self.movement_cooldown = int(MOVEMENT_COOLDOWN * 0.6)
        self.sprint_timer = SPRINT_COOLDOWN
        self.passives.append(Passive(60 * 2, self.stop_sprinting, name="sprint"))

    def kill(self):
        if self.kill_timer != 0:
            raise InvalidAction("Kill on cooldown, %d remaining." % self.kill_timer)

        visible_players = self.get_visible_players()
        visible_players.remove(self)
        if len(visible_players) == 0:
            raise InvalidAction("There is nobody around to kill.")

        self.kill_timer = KILL_COOLDOWN
        self.killing = visible_players[0]
        # self.movement_timer = 0  # Cannot move during kill
        self.passives.append(Passive(60 * 2, self.finish_kill, name="kill"))

    def finish_kill(self):
        self.movement_timer = 0
        self.kill_timer = KILL_COOLDOWN

        self.game.broadcast("%s died" % self.killing.profile.discord_username)
        self.killing = None
        # TODO: Actually kill the person

    def stop_sprinting(self):
        self.movement_cooldown = MOVEMENT_COOLDOWN

    def tick(self):
        for passive in self.passives[:]:
            passive.tick()
            if passive.time == 0:
                self.passives.remove(passive)

        self.cooldown_timer = max(0, self.cooldown_timer - 1)
        self.movement_timer = max(0, self.movement_timer - 1)
        self.sprint_timer = max(0, self.sprint_timer - 1)
        self.kill_timer = max(0, self.kill_timer - 1)

        last_direction = self.direction
        if self.movement_timer == 0:
            try:
                self.move()
            except:
                pass

        # Dont recompute if the player didnt move or turn
        if self.position != self.last_position or self.direction != last_direction:
            self.visible_tiles = self.compute_line_of_sight()

        self.last_position = self.position
        self.ready = False

    def change_position(self, point):
        self.position = self.spawn_position = point

    def move(self):
        # If there is no suggested move, we can stop right here
        if self.move_suggestion is None:
            self.is_moving = False
            return

        # Set the correct player model direction based on input
        if self.move_suggestion.x == 1:
            self.direction = PlayerAngles.RIGHT
        elif self.move_suggestion.x == -1:
            self.direction = PlayerAngles.LEFT
        elif self.move_suggestion.y == 1:
            self.direction = PlayerAngles.DOWN
        elif self.move_suggestion.y == -1:
            self.direction = PlayerAngles.UP

        # Compute temporary position based on next move
        new_position = self.move_suggestion + self.position
        # Check move validity
        if new_position.x > self.game.size - 1 or new_position.y > self.game.size - 1 or new_position.x < 0 or new_position.y < 0:
            raise InvalidAction("You cannot move out of bounds.")

        tile = self.game.board[new_position.x][new_position.y]

        # TODO: Synchronize animations server side maybe
        if isinstance(tile, ChestTile) \
                and tile.player == self \
                and self.item is not None:
            self.stored_items.append(self.item)
            self.item = None
            self.generate_item()

            # Animate the chest opening and closing
            tile.animation_ticks = 20
            tile.finish_animation = True
            self.game.animations.add(tile)

        if not tile.movement_allowed:
            raise InvalidAction("You cannot move on this tile.")

        # Reset the movement timer
        self.movement_timer = self.movement_cooldown

        # Move suggestion includes the ladder logic from Mole person
        if isinstance(tile, LadderTile) and tile.other_ladder is not None:
            self.position = tile.other_ladder.position
            self.direction = PlayerAngles.UP
        else:
            self.position = self.position + self.move_suggestion

        # Pickup item
        if self.position == self.objective \
                and self.game.board[self.objective.x][self.objective.y].item is not None:
            self.item = self.game.board[self.objective.x][self.objective.y].item
            self.game.board[self.objective.x][self.objective.y].item = None

        self.is_moving = True
        self.move_suggestion = None

    def suggest_move(self, move: Point):
        if move.x == 0 and move.y == 0:
            self.move_suggestion = None
            return

        self.move_suggestion = move

    def to_json(self, owner=True):
        # Default dictionary to see other players name
        state = {
            "username": self.profile.discord_username,
            "ready": self.ready,
            "position": self.position.to_json(),
            "name": self.name,
            "direction": self.direction.value,
            "is_moving": self.is_moving,
            "movement_cooldown": self.movement_cooldown,
            "movement_timer": self.movement_timer,
            "item": self.item.to_json() if self.item else None,
        }
        # In case you are owner add player sensitive information to state
        if owner:
            state.update({
                "cooldown": self.ability_cooldown,
                "cooldown_timer": self.cooldown_timer,
                "kill_cooldown": self.kill_cooldown,
                "kill_timer": self.kill_timer,
                "sprint": self.sprint_cooldown,
                "sprint_timer": self.sprint_timer,
                "passives": [passive.to_json() for passive in self.passives],
                "killing": self.killing.to_json(owner=False) if self.killing else None,
                "objective": self.objective.to_json(),
                "stored_items": [item.to_json() for item in self.stored_items],
            })
        return state

    def convert_class(self, new_class):
        cls = new_class(self.profile, self.socket, self.game)
        cls.ready = self.ready
        cls.position = self.position
        return cls

    def compute_line_of_sight(self):
        visible_positions = set()

        endpoints = line_of_sight_endpoints(self.direction)
        endpoints = [point + self.position for point in endpoints]
        for point in endpoints:
            walls = 0
            try:
                for intermediate in point_interpolator(self.position, point):
                    if not (0 <= intermediate.x < self.game.size and 0 <= intermediate.y < self.game.size):
                        break
                    # Allow for one wall in line of sight
                    if walls != 0 or self.game.board[intermediate.x][intermediate.y].opaque:
                        walls += 1

                    visible_positions.add(intermediate)
                    if walls == 2:
                        break
            except IndexError:
                pass

        return list(visible_positions)

    def get_visible_tiles(self):
        return [{
            "x": position.x,
            "y": position.y,
            "tile": self.game.board[position.x][position.y].to_json()
        } for position in self.visible_tiles]

    def get_visible_players(self):
        return [player for player in self.game.player_list if player.position in self.visible_tiles]

    def generate_item(self):
        random_x = random.randint(0, len(self.game.board[0]) - 1)
        random_y = random.randint(0, len(self.game.board) - 1)
        while not isinstance(self.game.board[random_x][random_y], GroundTile):
            random_x = random.randint(0, len(self.game.board[0]) - 1)
            random_y = random.randint(0, len(self.game.board) - 1)

        self.objective = Point(random_x, random_y)

        self.game.board[random_x][random_y].item = CollectorItem(self.name)


class Demolisher(PlayerClass):
    def __init__(self, profile, socket_id, game):
        super().__init__(profile, socket_id, game)

        self.name = self.__class__.__name__
        self.ability_cooldown = self.game.tick_rate * DEMOLISHER_COOLDOWN

    def ability(self):
        super().ability()
        position = copy.copy(self.position)
        old_position = Point(position.x, position.y)

        if self.direction == PlayerAngles.UP:
            if isinstance(self.game.board[position.x][position.y - 1], WallTile):
                position.y = position.y - 2
        elif self.direction == PlayerAngles.DOWN:
            if isinstance(self.game.board[position.x][position.y + 1], WallTile):
                position.y = position.y + 2
        elif self.direction == PlayerAngles.LEFT:
            if isinstance(self.game.board[position.x - 1][position.y], WallTile):
                position.x = position.x - 2
        elif self.direction == PlayerAngles.RIGHT:
            if isinstance(self.game.board[position.x + 1][position.y], WallTile):
                position.x = position.x + 2
        if old_position == position:
            raise InvalidAction("You cannot demolish this tile right now")

        for x in range(-1, 2):
            for y in range(-1, 2):
                diff = Point(x, y)
                tile = GroundTile()
                tile.item = RubbishItem()
                self.game.change_tile(position + diff, tile)
        self.cooldown_timer = self.ability_cooldown


class Spy(PlayerClass):
    def __init__(self, profile, socket_id, game):
        super().__init__(profile, socket_id, game)
        self.name = self.__class__.__name__

        self.ability_cooldown = SPY_COOLDOWN

    def ability(self):
        super().ability()
        self.cooldown_timer = self.ability_cooldown


class Scout(PlayerClass):
    def __init__(self, profile, socket_id, game):
        super().__init__(profile, socket_id, game)

        self.name = self.__class__.__name__
        self.ability_cooldown = SPY_COOLDOWN

    def ability(self):
        super().ability()
        self.cooldown_timer = self.ability_cooldown


class MrMole(PlayerClass):
    def __init__(self, profile, socket_id, game):
        super().__init__(profile, socket_id, game)

        self.name = self.__class__.__name__
        self.ability_cooldown = self.game.tick_rate * MRMOLE_COOLDOWN

        self.ladders = []

    def ability(self):
        super().ability()

        position = copy.copy(self.position)

        ladder = LadderTile(self.position)
        self.ladders.append(ladder)
        # You can have only two ladders, if you create more, the oldest one will get removed
        if len(self.ladders) > 2:
            to_remove_ladder = self.ladders.pop(0)
            self.game.change_tile(to_remove_ladder.position, GroundTile())
        if len(self.ladders) == 2:
            ladder.other_ladder = self.ladders[0]
            self.ladders[0].other_ladder = ladder

        print("Created ladder", len(self.ladders))

        self.game.change_tile(position, ladder)
        self.cooldown_timer = self.ability_cooldown
