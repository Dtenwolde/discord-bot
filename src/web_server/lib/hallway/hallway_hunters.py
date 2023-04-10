from __future__ import annotations
import logging
import random
import threading
import time
from datetime import datetime
from typing import List, Optional, Dict

from src.web_server import sio, timing
from src.web_server.lib.hallway.entities.movable_entity import MovableEntity
from src.web_server.lib.hallway.entities.spells import SpellEntity
from src.web_server.lib.hallway.entities.enemies.MonkeyBall import MonkeyBall
from src.web_server.lib.hallway.entities.enemies.Sloth import Sloth

from src.web_server.lib.hallway.map import tiles
from src.web_server.lib.hallway.Utils import Point, Turns, Phases
from src.web_server.lib.hallway.entities.enemies.Slime import EnemyClass, Slime
from src.web_server.lib.hallway.entities.player_class import PlayerClass, PlayerState
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.Spawner import EntitySpawner
from src.web_server.lib.hallway.map.generator import Generator

games: Dict[int, HallwayHunters] = {}


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
        self.allied_entities: List[Entity] = []
        self.enemy_entities: List[Entity] = []

        # Generate this to send to every player initially
        self.initial_board_json = [[tiles.UnknownTile().to_json() for _ in range(self.size)] for _ in range(self.size)]
        self.updated_line_of_sight = True

        self.spent_time = 0.00001
        self.ticks = 0
        self.processing_entities = False
        self._turn = 0
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
            self.enemy_entities.append(spawner)
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
        self.enemy_entities.clear()
        self.allied_entities.clear()

        entities = self.generator.generate_keys(spawn_point)
        self.add_enemy_entities(entities)

        chests = self.generator.generate_chests(self, loot_table=(
            [1],
            ["teleport"]
        ))
        self.add_enemy_entities(chests)

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

        # Create enemy for testing animations
        enemy = Sloth(self)
        enemy.change_position(spawn_point + spawn_point_modifier[-1])
        self.spawn_enemy(enemy)
        enemy = MonkeyBall(self)
        enemy.change_position(spawn_point + spawn_point_modifier[-2])
        self.spawn_enemy(enemy)

        self._turn = 0

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

    def process_player_turn(self):
        # Check if players are each ready with their queued actions
        for player in self.player_list:
            if player.action_state == PlayerState.NOT_READY:
                return

        # Set player state to processing and activate their prepared movement
        for player in self.player_list:
            player.action_state = PlayerState.PROCESSING
            player.movement_queue.extend(player.prepared_movement_queue)
            player.prepared_movement_queue.clear()

        # Check if everybody has finished their movement and spells
        for player in self.player_list:
            if len(player.movement_queue) != 0 or player.movement_timer != 0:
                return
            if len(player.entities) != 0:
                return

        # If all movement has been processed, process all queued spells
        for player in self.player_list:
            # Do end-of-turn stat updates and allow for new inputs.
            player.post_movement_action()
            player.action_state = PlayerState.NOT_READY

        self.increment_turn()

    def process_entity_turn(self, all_entities):
        # Only movable entities have movement_related functions
        entities = [entity for entity in all_entities if isinstance(entity, MovableEntity)]

        # Are all entities done moving?
        for entity in entities:
            if len(entity.movement_queue) != 0 or entity.movement_timer != 0:
                return

        # Do end-of-turn stat updates and allow for post-processing
        for entity in entities:
            entity.post_movement_action()

        self.increment_turn()

    def tick(self):
        # Resolve entities
        for entity in self.allied_entities:
            entity.tick()
        for entity in self.enemy_entities:
            entity.tick()
        for player in self.player_list:
            player.tick()

        # Player turn
        if self.to_move() == Turns.PLAYER:
            self.process_player_turn()
        # Allied entity turns (e.g., spells)
        elif self.to_move() == Turns.ALLY_ENTITY:
            self.process_entity_turn(self.allied_entities)
        # Enemy turn
        elif self.to_move() == Turns.ENEMY:
            self.process_entity_turn([
                entity for entity in self.enemy_entities if isinstance(entity, EnemyClass)
            ])
        # Enemy entity turn (e.g., spawners)
        else:
            self.process_entity_turn([
                entity for entity in self.enemy_entities if not isinstance(entity, EnemyClass)
            ])

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
            visible_tiles.extend(entity.position for entity in self.allied_entities)

            data.update({
                "visible_tiles": [{
                    "x": p.x,
                    "y": p.y,
                    "tile": self.board[p.x][p.y].to_json()
                } for p in list(set(visible_tiles))]
            })

            # Share visible enemies too user
            visible_entities = []
            for tile in visible_tiles:
                for entity in self.enemy_entities + self.allied_entities:
                    if entity.position == tile:
                        visible_entities.append(entity)

            data.update({
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
        sio.emit("notify", data, room=self.room_id, namespace="/hallway")

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
        self._turn += 1
        self.processing_entities = True
        if self.to_move() == Turns.ENEMY:
            # We just started an enemy turn, prepare all movement for the enemies
            for enemy in [entity for entity in self.enemy_entities if isinstance(entity, EnemyClass)]:
                enemy.before_turn_action()
        # Allied entity turns (e.g., spells)
        elif self.to_move() == Turns.ALLY_ENTITY:
            for entity in self.allied_entities:
                entity.before_turn_action()
        # Enemy entity turn (e.g., spawners)
        elif self.to_move() == Turns.ENEMY_ENTITY:
            for entity in self.enemy_entities:
                if not isinstance(entity, EnemyClass):
                    entity.before_turn_action()

    def get_entities_at(self, position):
        all_entities = []
        all_entities.extend(
            [x for x in (
                    self.player_list +
                    self.allied_entities +  # noqa
                    self.enemy_entities)
             if x.position == position]
        )
        return all_entities

    def remove_entity(self, entity):
        if entity in self.enemy_entities:
            self.enemy_entities.remove(entity)
        elif entity in self.allied_entities:
            self.allied_entities.remove(entity)
        else:
            return  # Already removed this entity
        self.removed_entity_ids.append(entity.uid)

    def spawn_enemy(self, enemy):
        self.enemy_entities.append(enemy)

    def to_move(self):
        return self._turn % 4

    def add_ally_entities(self, entities):
        for entity in entities:
            entity.game = self
        self.allied_entities.extend(entities)

    def add_enemy_entities(self, entities):
        for entity in entities:
            entity.game = self
        self.enemy_entities.extend(entities)
