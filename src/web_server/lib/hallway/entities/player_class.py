import random
from typing import Optional, List

from src.web_server.lib.hallway.Items import Item, CollectorItem
from src.web_server.lib.hallway.Utils import Point, EntityDirections, line_of_sight_endpoints, \
    point_interpolator
from src.web_server.lib.hallway.cards.card import available_cards
from src.web_server.lib.hallway.cards.deck import Deck
from src.web_server.lib.hallway.entities.Passive import Passive
from src.web_server.lib.hallway.entities.Spell import SpellEntity
from src.web_server.lib.hallway.entities.enemies.Slime import EnemyClass
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.exceptions import InvalidAction
from src.web_server.lib.hallway.map.tiles import FloorTile


SPRINT_COOLDOWN = 10 * 60  # Ticks
KILL_COOLDOWN = 10 * 60  # Ticks


class PlayerState:
    READY = 0
    PROCESSING = 1
    NOT_READY = 2
    PREPARING_GAME = 3
    READY_FOR_GAME = 4


class PlayerClass(MovableEntity):
    def __init__(self, username: str, socket_id, game):
        super().__init__(game, username)
        self.MAX_MOVEMENT = 10
        self.color = ""
        self.sprite_name = f"{self.color}_0_0"
        self.username = username
        self.spawn_position = Point(1, 1)
        self.position = Point(1, 1)
        self.last_position = self.position
        self.class_name = None

        self.dead = False
        self.can_move = True

        self.movement_cooldown = 8  # Ticks
        self.movement_timer = 0
        self.movement_queue = []
        self.moving = False

        self.action_state = PlayerState.PREPARING_GAME
        self.direction = EntityDirections.DOWN

        # The item you are holding
        self.item: Optional[Item] = None
        self.stored_items: List[Item] = []

        self.objective: Point = Point(0, 0)

        self.passives: List[Passive] = []

        self.visible_tiles = []

        from src.web_server.lib.hallway.hallway_hunters import HallwayHunters
        self.game: HallwayHunters = game

        self.socket = socket_id

        # Fixed stats
        self.max_hp = 15
        self.max_mana = 10
        self.mana_regen = 1

        # Active stats
        self.hp = 15
        self.mana = 5

        # Cards to play
        self.deck = Deck(self)
        self.deck.emit_deck()

        self.queued_spell_idx = None

        # Inventory
        self.inventory = []

    def prepare_movement(self):
        pass

    def toggle_ready(self):
        if len(self.deck.selected_cards) == 0:
            raise InvalidAction("You cannot start the game without adding cards to your deck first!")

        if self.action_state == PlayerState.PREPARING_GAME:
            self.action_state = PlayerState.READY_FOR_GAME
        else:
            self.action_state = PlayerState.PREPARING_GAME

    def start(self):
        super().start()

        self.stored_items = []
        self.direction = EntityDirections.DOWN
        self.visible_tiles = self.compute_line_of_sight()
        self.generate_item()
        self.queued_spell_idx = None

        self.deck.start()

    def die(self):
        self.passives = []
        self.dead = True
        self.can_move = False
        self.queued_spell_idx = None

        self.drop_item()
        self.movement_queue.clear()
        self.movement_timer = 0
        self.game.broadcast("%s died" % self.username)

    def tick(self):
        super().tick()

        for passive in self.passives[:]:
            passive.tick()
            if passive.time == 0:
                self.passives.remove(passive)

        if self.position != self.last_position or self.direction != self.direction:
            self.update_line_of_sight()

    def update_line_of_sight(self):
        self.game.updated_line_of_sight = True
        self.visible_tiles = self.compute_line_of_sight()

    def movement_action(self):
        attempted_move = super().movement_action()

        new_position = self.position + attempted_move
        tile = self.game.board[new_position.x][new_position.y]

        if not tile.movement_allowed:
            raise InvalidAction("You cannot move on this tile.")

        # Reset the movement timer
        self.movement_timer = self.movement_cooldown

        # Pickup item
        ground_item = self.game.board[self.position.x][self.position.y].item
        if ground_item is not None and self.item is None:
            if isinstance(ground_item, CollectorItem):
                self.item = ground_item
                self.game.board[self.position.x][self.position.y].item = None

    def collide(self, other):
        if isinstance(other, EnemyClass):
            other: EnemyClass
            self.hp -= other.damage
            if self.hp <= 0:
                self.die()

        return other.can_move_through

    def prepare_action(self, action, extra=None):
        # We cannot do new actions while processing the queued actions
        if self.action_state == PlayerState.PROCESSING:
            return

        # We can ready or unready when we are not processing actions
        if action == "Enter":
            if self.action_state == PlayerState.READY:
                self.action_state = PlayerState.NOT_READY
            if self.action_state == PlayerState.NOT_READY:
                self.action_state = PlayerState.READY

        # We can only do actions when not ready.
        if self.action_state == PlayerState.READY:
            return
        try:
            n_action = int(action)
            self.suggest_card(n_action)
        except ValueError:
            pass

        if action == "ArrowUp":
            self.suggest_move(Point(0, -1))
        elif action == "ArrowDown":
            self.suggest_move(Point(0, 1))
        elif action == "ArrowLeft":
            self.suggest_move(Point(-1, 0))
        elif action == "ArrowRight":
            self.suggest_move(Point(1, 0))

    def suggest_move(self, move: Point):
        if not self.can_move:
            return

        # Remove the last move from the stack if moving in the opposite direction
        if len(self.movement_queue) > 0 and \
                ((self.movement_queue[-1].x == -move.x and move.x != 0) or
                 (self.movement_queue[-1].y == -move.y and move.y != 0)):
            self.movement_queue.pop(-1)
            return

        if len(self.movement_queue) == self.MAX_MOVEMENT:
            return

        self.movement_queue.append(move)

    def to_json(self):
        state = super().to_json()
        state.update({
            "color": self.color,
            "username": self.username,
            "dead": self.dead,
            "stored_items": [item.to_json() for item in self.stored_items],
            "state": self.action_state,
            "hp": self.hp,
            "mana": self.mana,
            "max_hp": self.max_hp,
            "max_mana": self.max_mana,
            "item": self.item.to_json() if self.item else None,
            "hand": [],
            "movement_queue": [move.to_json() for move in self.movement_queue],
            "class_name": self.class_name,
        })
        return state

    def personal_data_json(self):
        return {
            "passives": [passive.to_json() for passive in self.passives],
            "stored_items": [item.to_json() for item in self.stored_items],
            "hand": [vars(available_cards[card_name]) for card_name in self.deck.hand],
        }

    def convert_class(self, new_class):
        cls = new_class(self.username, self.socket, self.game)
        cls.ready = self.action_state
        cls.color = self.color
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
        visible_tiles = self.visible_tiles
        return [player for player in self.game.player_list if player.position in visible_tiles]

    def generate_item(self):
        random_x = random.randint(0, len(self.game.board[0]) - 1)
        random_y = random.randint(0, len(self.game.board) - 1)
        while not isinstance(self.game.board[random_x][random_y], FloorTile):
            random_x = random.randint(0, len(self.game.board[0]) - 1)
            random_y = random.randint(0, len(self.game.board) - 1)

        self.objective = Point(random_x, random_y)

        self.game.board[random_x][random_y].item = CollectorItem(self.color)

    def drop_item(self):
        if self.item is not None and \
                not isinstance(self.game.board[self.position.x][self.position.y].item, CollectorItem):
            self.game.board[self.position.x][self.position.y].item = self.item
            self.item = None
            self.update_line_of_sight()

    def suggest_card(self, n_action):
        if n_action >= len(self.deck.hand):
            return

        if self.mana < self.deck.hand[n_action].mana_cost:
            return

        if self.queued_spell_idx == n_action:
            self.queued_spell_idx = None
        else:
            self.queued_spell_idx = n_action

    def post_movement_action(self):
        if self.queued_spell_idx is not None:
            spell = self.deck.play_card(idx=self.queued_spell_idx)
            self.mana -= spell.mana_cost
            self.game.entities.append(SpellEntity(self, spell, f"{self.color}_{self.queued_spell_idx}", self.game))

            self.queued_spell_idx = None

        self.mana = min(self.mana + self.mana_regen, self.max_mana)

    def damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()


class Demolisher(PlayerClass):
    info = """Demolisher can blow up walls with its active effect."""

    def __init__(self, username: str, socket_id, game):
        super().__init__(username, socket_id, game)


class Spy(PlayerClass):
    info = "Placeholder info."

    def __init__(self, username, socket_id, game):
        super().__init__(username, socket_id, game)


class Scout(PlayerClass):
    info = """asd."""

    def __init__(self, username, socket_id, game):
        super().__init__(username, socket_id, game)

    def tick(self):
        super().tick()


class Wizard(PlayerClass):
    info = "Traditional mage class."

    def __init__(self, username, socket_id, game):
        super().__init__(username, socket_id, game)

        self.class_deck = []
        self.class_deck.extend([available_cards["heal"]] * 10)
        self.class_deck.extend([available_cards["axe"]] * 10)
        self.class_deck.extend([available_cards["spear"]] * 10)
