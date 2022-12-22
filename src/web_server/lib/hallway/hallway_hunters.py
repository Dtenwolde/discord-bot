from __future__ import annotations
import logging
import random
import threading
import time
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

from src.web_server import sio, timing

from src.web_server.lib.hallway import tiles
from src.web_server.lib.hallway.Utils import Point
from src.web_server.lib.hallway.entities.enemies.Slime import EnemyClass, Slime
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.entities.player_class import Demolisher, PlayerClass, PlayerState, Wizard
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.exceptions import InvalidAction
from src.web_server.lib.hallway.entities.Spawner import EntitySpawner
from src.web_server.lib.hallway.generator import Generator


games: Dict[int, HallwayHunters] = {}


class Phases(Enum):
    NOT_YET_STARTED = 0
    STARTED = 1


class HallwayHunters:
    def __init__(self, room_id, username):
        self.removed_entity_ids: List[str] = []
        self.tick_rate = 60
        self.room_id = room_id
        self.author = username
        self.phase = Phases.NOT_YET_STARTED
        self.player_list: List[PlayerClass] = []
        self.size = 93

        self.color_pool = ["blue", "red", "black", "purple", "green"]

        self.generator = Generator(self.size)
        self.room_centers: List[Point] = []
        self.board: List[List[tiles.Tile]] = []
        self.enemies: List[EnemyClass] = []
        self.entities: List[Entity] = []

        # Generate this to send to every player initially
        self.initial_board_json = [[tiles.UnknownTile().to_json() for _ in range(self.size)] for _ in range(self.size)]
        self.updated_line_of_sight = True

        self.spent_time = 0.00001
        self.ticks = 0
        self.processing_entities = False
        self.turn = 0
        self.finished = False

        self.game_loop_thread = threading.Thread(target=self.game_loop)
        self.game_lock = threading.Condition()

        self.board_changes = []

    def generate_spawners(self, n=2):
        assert n < len(self.room_centers)

        points = random.sample(self.room_centers, n)
        self.room_centers = [center for center in self.room_centers if center not in points]
        for point in points:
            spawner = EntitySpawner(self, Slime)
            spawner.position = point
            self.entities.append(spawner)
            self.board[point.x][point.y - 1] = tiles.TotemTopLeft()
            self.board[point.x][point.y] = tiles.TotemMidLeft()
            self.board[point.x][point.y + 1] = tiles.TotemBotLeft()
            self.board[point.x + 1][point.y - 1] = tiles.TotemTopRight()
            self.board[point.x + 1][point.y] = tiles.TotemMidRight()
            self.board[point.x + 1][point.y + 1] = tiles.TotemBotRight()

    def start(self):
        if self.phase == Phases.STARTED:
            return
        self.phase = Phases.STARTED

        # Generate current floor of the dungeon
        self.board, self.room_centers = self.generator.generate_board(self.size, self.room_id)
        self.generate_spawners(0)
        spawn_point = random.choice(self.room_centers)

        # Generate keys and door entities
        # entities = self.generator.generate_keys(spawn_point)
        # self.add_entities(entities)

        spawn_point_modifier = [
            Point(0, 0),
            Point(1, 0),
            Point(-1, 0),
            Point(1, 1),
            Point(-1, 1)
        ]
        for i, player in enumerate(self.player_list):
            player.change_position(spawn_point + spawn_point_modifier[i])
            player.start()
            sio.emit("game_state", self.export_board(player), room=player.socket, namespace="/hallway")

        self.turn = 0

        # Connect chest to player
        chest = tiles.ChestTile(self.player_list[0])
        self.board[spawn_point.x][spawn_point.y + 1] = chest
        chest.image = "chest_%s" % self.player_list[0].color

        self.finished = False
        self.game_lock.acquire()
        self.game_lock.notify()
        self.game_lock.release()

    def game_loop(self):
        s_per_tick = 1 / self.tick_rate
        while True:
            print("Started loop")
            while not self.finished:
                start = datetime.now()

                self.tick()

                diff = (datetime.now() - start).total_seconds()

                self.spent_time += diff
                self.ticks += 1.
                if self.ticks % self.tick_rate == 0:
                    self.spent_time = 0.000001
                    self.ticks = 0

                # Fill time sleeping while waiting for next tick
                time.sleep(s_per_tick - diff)

                logger = logging.getLogger("timing")
                logger.info(f"game_loop: {diff}")

            self.game_lock.acquire()
            self.game_lock.wait()
            self.game_lock.release()

    def process_entities(self):
        """
        Process all entities, returns False if nothing else needs to be done.
        :return:
        """
        movable_entities = [entity for entity in self.entities if isinstance(entity, MovableEntity)]
        for entity in movable_entities:
            if entity.movement_timer == 0:
                try:
                    entity.movement_action()
                except InvalidAction as e:
                    pass

        # Check if everybody has finished their movement
        for entity in movable_entities:
            if len(entity.movement_queue) != 0 or entity.movement_timer != 0:
                return True

        for entity in movable_entities:
            entity.post_movement_action()

        self.entities = [entity for entity in self.entities if entity.alive]
        return False

    def process_player_turn(self):
        for player in self.player_list:
            if player.action_state == PlayerState.NOT_READY:
                return
        for player in self.player_list:
            player.action_state = PlayerState.PROCESSING

        # Everybody is ready, process all movement actions, followed by actions
        for player in self.player_list:
            if player.movement_timer == 0:
                try:
                    player.movement_action()
                except InvalidAction:
                    pass

        # Check if everybody has finished their movement
        for player in self.player_list:
            if len(player.movement_queue) != 0 or player.movement_timer != 0:
                return

        # If all movement has been processed, process all queued spells
        for player in self.player_list:
            # Do end-of-turn stat updates and allow for new inputs.
            player.post_movement_action()
            player.action_state = PlayerState.NOT_READY

        self.increment_turn()

    def process_enemy_turn(self):
        for enemy in self.enemies:
            if enemy.movement_timer == 0:
                try:
                    enemy.movement_action()

                    self.updated_line_of_sight = True
                except InvalidAction:
                    pass
        for enemy in self.enemies:
            if len(enemy.movement_queue) != 0 or enemy.movement_timer != 0:
                return

        # If all movement has been processed, process all queued spells
        for enemy in self.enemies:
            # Do end-of-turn stat updates and allow for new inputs.
            enemy.post_movement_action()

        self.increment_turn()

    def tick(self):
        # Resolve entities
        for entity in self.entities:
            entity.tick()

        # Resolve entities in progress
        if self.processing_entities:
            self.processing_entities = self.process_entities()
        # Player turn
        elif self.turn % 2 == 0:
            for player in self.player_list:
                # Maybe check if this is allowed, maybe not
                player.tick()

            # If all players are ready, we can stop this preparation and go to next turn
            self.process_player_turn()

        # Enemy turn
        else:
            for enemy in self.enemies:
                enemy.tick()

            self.process_enemy_turn()
        # Update the player of all changes that occurred
        self.update_players()
        # After having sent the update to all players, empty board changes list
        self.board_changes = []

    def add_player(self, username: str, socket_id):
        for player in self.player_list:
            if player.username == username:
                # If the user is already in the list, overwrite the socket id to the newest one.
                player.socket = socket_id
                print("Already found player, overwriting socket id")
                return player

        player = PlayerClass(username, socket_id, self)

        player.color = self.color_pool.pop()
        if self.phase == Phases.NOT_YET_STARTED and len(self.player_list) < 8:
            self.player_list.append(player)
        return player

    def update_players(self):
        for player in self.player_list:
            sio.emit("game_state", self.export_board(player, reduced=True), room=player.socket, namespace="/hallway")

    def export_board(self, player: PlayerClass, reduced=False):
        data = {
            "started": self.phase == Phases.STARTED,
            "player_data": player.personal_data_json(),
            "all_players": [player.to_json() for player in self.player_list],
            "removed_entity_ids": [i for i in self.removed_entity_ids]
        }
        self.removed_entity_ids.clear()

        # If this players line of sight changed, send new data.
        if self.updated_line_of_sight:
            # TODO: Remove the condition in some cases
            visible_tiles = []
            for p in self.player_list:
                visible_tiles.extend(p.visible_tiles)

            data.update({
                "visible_tiles": [{
                    "x": p.x,
                    "y": p.y,
                    "tile": self.board[p.x][p.y].to_json()
                } for p in list(set(visible_tiles))]
            })

            # Share visible enemies too user
            visible_enemies = []
            visible_entities = []
            for tile in visible_tiles:
                for enemy in self.enemies:
                    if enemy.position == tile:
                        visible_enemies.append(enemy)
                for entity in self.entities:
                    if entity.position == tile:
                        visible_entities.append(entity)

            data.update({
                "visible_enemies": [enemy.to_json() for enemy in visible_enemies],
                "visible_entities": [entity.to_json() for entity in visible_entities]
            })

        if not reduced:
            data.update({
                "board_size": self.size
            })

        return data

    def set_color(self, username: str, color: str):
        if color not in self.color_pool:
            print("Color not available")
            return  # TODO: Notify player this colour is taken.
        player = self.get_player(username)
        assert player is not None
        self.color_pool.remove(color)
        self.color_pool.append(player.color)  # Add back previous color
        print(self.color_pool)
        player.color = color

    def get_player(self, username: str = None, socket_id=None) -> Optional[PlayerClass]:
        combined_list = self.player_list[:]

        if username is not None:
            for player in combined_list:
                if player.username == username:
                    return player
            return None
        elif socket_id is not None:
            for player in combined_list:
                if player.socket == socket_id:
                    return player
            return None

    def set_player(self, username, new_player):
        for i, player in enumerate(self.player_list):
            if player.username == username:
                self.player_list[i] = new_player
                return

    def remove_player(self, username: str):
        player = self.get_player(username)
        self.color_pool.append(player.color)
        print("Disconnecting player, current pool:", self.color_pool)

        if player in self.player_list:
            self.player_list.remove(player)

        if len(self.player_list) == 0:
            self.finished = True
            self.phase = Phases.NOT_YET_STARTED

    def broadcast(self, message):
        data = {
            "username": "SYSTEM",
            "message": message,
        }
        sio.emit("chat message", data, room=self.room_id, namespace="/hallway")

    def check_readies(self):
        for player in self.player_list:
            if player.action_state == PlayerState.NOT_READY:
                return False
        return True

    def in_bounds(self, position):
        return 1 < position.x < self.size - 2 and 1 < position.y < self.size - 2

    def change_tile(self, position, tile: tiles.Tile):
        if not self.in_bounds(position):
            return
        self.board[position.x][position.y] = tile
        self.board_changes.append({
            "x": position.x,
            "y": position.y,
            "tile": tile.to_json()
        })

    @timing
    def increment_turn(self):
        self.turn += 1
        self.processing_entities = True
        if self.turn % 2 == 1:
            # We just started an enemy turn, prepare all movement for the enemies
            for enemy in self.enemies:
                enemy.prepare_movement()

    def get_entities_at(self, position):
        all_entities = []
        all_entities.extend([x for x in self.player_list if x.position == position])
        all_entities.extend([x for x in self.entities if x.position == position])
        all_entities.extend([x for x in self.enemies if x.position == position])
        return all_entities

    def add_entities(self, entities):
        for entity in entities:
            entity.game = self
        self.entities.extend(entities)

    def remove_entity(self, entity):
        self.entities.remove(entity)
        self.removed_entity_ids.append(entity.uid)
