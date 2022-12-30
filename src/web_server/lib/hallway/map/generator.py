import copy
import random
from typing import List, Tuple

from src.web_server.lib.hallway.Items import RubbishItem
from src.web_server.lib.hallway.entities.entity import Entity
from src.web_server.lib.hallway.entities.neutral.Chest import Chest
from src.web_server.lib.hallway.entities.neutral.Door import Door
from src.web_server.lib.hallway.entities.spells import available_cards
from src.web_server.lib.hallway.entities.spells.card import Card
from src.web_server.lib.hallway.map.tiles import *
from src.web_server.lib.hallway.Utils import Point


def get_surrounding_points(point: Point, scale):
    return [
        Point(point.x + scale, point.y),
        Point(point.x - scale, point.y),
        Point(point.x, point.y + scale),
        Point(point.x, point.y - scale)
    ]


def flood_fill(base: List[List[Tile]], player_spawn_location: Point, scale=3):
    rounded_spawn_location: Point = player_spawn_location // 3 * 3

    frontier = [rounded_spawn_location + Point(1, 1)]

    points = []
    while len(frontier) != 0:
        current = frontier.pop()
        points.append(current)

        neighbours = get_surrounding_points(current, scale)
        for neighbour in neighbours:
            if neighbour in points:
                continue

            # If this is a door placeholder, we add it to the list of points.
            # While we cannot search through the door, we add it to be able to search in it more easily
            if isinstance(base[neighbour.x][neighbour.y], DoorPlaceholder):
                points.append(neighbour)
            elif base[neighbour.x][neighbour.y].movement_allowed:
                frontier.append(neighbour)

    return points


class DoorPlaceholder(Tile):
    """
    We use this placeholder to be able to flood-fill from the users on this grid, as doors are entities otherwise.
    """

    def __init__(self, orientation):
        super().__init__()
        self.image = "void"
        self.movement_allowed = True
        self.opaque = True
        self.orientation = orientation

    def __repr__(self):
        return "X"


class Generator:
    def __init__(self, generator_size):
        self.DOOR_PERCENTAGE = 0.5
        self.generator_size = generator_size
        self.base: List[List[Tile]] = [[UnknownTile() for _ in range(generator_size)] for _ in range(generator_size)]
        self.room_centers: List[Point] = []
        self.doors: List[Door] = []
        self.entities: List[Entity] = []
        self.valid_3x3_locations: List[Point] = []

    def room_generator(self, size, attempts=50):
        def room_fits(_x, _y, _width, _height):
            """
            Check if a room fits if all the squares around it and itself are walls
            """
            for i in range(_x - 1, _x + _width + 1):
                for j in range(_y - 1, _y + _height + 1):
                    if not isinstance(self.base[i][j], UnknownTile):
                        return False
            return True

        def carve_room(_x, _y, _width, _height):
            """
            Replace tiles with ground tiles for all in the x, y, width, height range.
            """
            for i in range(_x, _x + _width):
                for j in range(_y, _y + _height):
                    self.base[i][j] = FloorTile()
            return True

        min_size = 3
        max_size = 7

        rooms = []
        for _ in range(attempts):
            width = random.randint(min_size // 2, max_size // 2) * 2 + 1
            height = random.randint(min_size // 2, max_size // 2) * 2 + 1

            x = random.randint(0, (size - width - 2) // 2) * 2 + 1
            y = random.randint(0, (size - height - 2) // 2) * 2 + 1

            if room_fits(x, y, width, height):
                rooms.append(Point(x + width // 2, y + height // 2))
                carve_room(x, y, width, height)

        self.room_centers = rooms

    def maze_generator(self):
        def check_point(_point, _orig_point):
            # If the left point is not the original point, and it is already ground, it is not valid
            lp = Point(_point.x - 1, _point.y)
            if lp != _orig_point and isinstance(self.base[_point.x - 1][_point.y], FloorTile):
                return False
            rp = Point(_point.x + 1, _point.y)
            if rp != _orig_point and isinstance(self.base[_point.x + 1][_point.y], FloorTile):
                return False
            tp = Point(_point.x, _point.y - 1)
            if tp != _orig_point and isinstance(self.base[_point.x][_point.y - 1], FloorTile):
                return False
            bp = Point(_point.x, _point.y + 1)
            if bp != _orig_point and isinstance(self.base[_point.x][_point.y + 1], FloorTile):
                return False
            return True

        size = len(self.base)
        # add all wall cells to a list to process
        wall_cells = []
        for x in range(1, size, 2):
            for y in range(1, size, 2):
                if not self.base[x][y].movement_allowed:
                    wall_cells.append(Point(x, y))

        while len(wall_cells) > 0:
            # Pop an uncarved cell and set it to ground, then branch from this position onward
            carved_cells = [wall_cells.pop()]
            self.base[carved_cells[0].x][carved_cells[0].y] = FloorTile()
            while len(carved_cells) > 0:
                current_cell = carved_cells[random.randint(0, len(carved_cells) - 1)]
                potential_cells = []
                x = current_cell.x
                y = current_cell.y
                if x - 1 != 0 and isinstance(self.base[x - 2][y], UnknownTile):
                    potential_cells.append(Point(x - 2, y))
                if x + 2 != size and isinstance(self.base[x + 2][y], UnknownTile):
                    potential_cells.append(Point(x + 2, y))
                if y - 1 != 0 and isinstance(self.base[x][y - 2], UnknownTile):
                    potential_cells.append(Point(x, y - 2))
                if y + 2 != size and isinstance(self.base[x][y + 2], UnknownTile):
                    potential_cells.append(Point(x, y + 2))

                if len(potential_cells) != 0:
                    next_cell = potential_cells[random.randint(0, len(potential_cells) - 1)]
                    # Remove this cell from all available wall cells
                    wall_cells.remove(next_cell)
                    self.base[next_cell.x][next_cell.y] = FloorTile()
                    self.base[(next_cell.x + current_cell.x) // 2][(next_cell.y + current_cell.y) // 2] = FloorTile()
                    carved_cells.append(next_cell)
                else:
                    carved_cells.remove(current_cell)

    def connector_generator(self):
        size = len(self.base)
        start = Point(1, 1)
        region = []
        tails = [start]

        while True:
            # Expand the current region to include all connected tiles
            while len(tails) > 0:
                tail = tails.pop()
                region.append(tail)
                p = Point(tail.x + 2, tail.y)
                if self.base[tail.x + 1][tail.y].movement_allowed and p not in region and p not in tails:
                    tails.append(p)
                p = Point(tail.x - 2, tail.y)
                if self.base[tail.x - 1][tail.y].movement_allowed and p not in region and p not in tails:
                    tails.append(p)
                p = Point(tail.x, tail.y + 2)
                if self.base[tail.x][tail.y + 1].movement_allowed and p not in region and p not in tails:
                    tails.append(p)
                p = Point(tail.x, tail.y - 2)
                if self.base[tail.x][tail.y - 1].movement_allowed and p not in region and p not in tails:
                    tails.append(p)

            # If the current region is large enough to spawn the entire board, stop
            if len(region) == (len(self.base) // 2) ** 2:
                return

            # Add random connections to an unknown region
            edges = set()
            for segment in region:
                points = [
                    Point(segment.x + 2, segment.y),
                    Point(segment.x - 2, segment.y),
                    Point(segment.x, segment.y + 2),
                    Point(segment.x, segment.y - 2)
                ]
                for point in points:
                    if 0 < point.x < size \
                            and 0 < point.y < size \
                            and point not in region:
                        edges.add(point)

            edges = list(edges)
            # the amount of random connections to make
            for i in range(min(2, len(edges))):
                random_door = edges[random.randint(0, len(edges) - 1)]
                # Removed
                edges.remove(random_door)
                if i == 0:
                    tails.append(random_door)
                if Point(random_door.x - 2, random_door.y) in region:
                    if random.random() < self.DOOR_PERCENTAGE:
                        tile = DoorPlaceholder("vertical")
                    else:
                        tile = FloorTile()
                    self.base[random_door.x - 1][random_door.y] = tile
                    continue
                if Point(random_door.x + 2, random_door.y) in region:
                    if random.random() < self.DOOR_PERCENTAGE:
                        tile = DoorPlaceholder("vertical")
                    else:
                        tile = FloorTile()
                    self.base[random_door.x + 1][random_door.y] = tile
                    continue
                if Point(random_door.x, random_door.y + 2) in region:
                    if random.random() < self.DOOR_PERCENTAGE:
                        tile = DoorPlaceholder("horizontal")
                    else:
                        tile = FloorTile()
                    self.base[random_door.x][random_door.y + 1] = tile
                    continue
                if Point(random_door.x, random_door.y - 2) in region:
                    if random.random() < self.DOOR_PERCENTAGE:
                        tile = DoorPlaceholder("horizontal")
                    else:
                        tile = FloorTile()
                    self.base[random_door.x][random_door.y - 1] = tile
                    continue

    def remove_dead_ends(self):
        size = len(self.base)

        def is_end(_x, _y):
            end_count = sum([
                not self.base[_x][_y - 1].movement_allowed,
                not self.base[_x][_y + 1].movement_allowed,
                not self.base[_x - 1][_y].movement_allowed,
                not self.base[_x + 1][_y].movement_allowed
            ])

            return end_count == 3

        def get_neighbour(point):
            if self.base[point.x][point.y - 1].movement_allowed:
                return Point(point.x, point.y - 2)
            if self.base[point.x][point.y + 1].movement_allowed:
                return Point(point.x, point.y + 2)
            if self.base[point.x - 1][point.y].movement_allowed:
                return Point(point.x - 2, point.y)
            if self.base[point.x + 1][point.y].movement_allowed:
                return Point(point.x + 2, point.y)

        # Find all ends in the maze
        ends = []
        for x in range(1, size, 2):
            for y in range(1, size, 2):
                if is_end(x, y):
                    ends.append(Point(x, y))

        # Keep removing hallways until there is no more end
        for end in ends:
            while is_end(end.x, end.y):
                neighbour = get_neighbour(end)
                self.base[end.x][end.y] = UnknownTile()
                self.base[(end.x + neighbour.x) // 2][(end.y + neighbour.y) // 2] = UnknownTile()
                end = neighbour

    def upscale_nx(self, scale=3):
        size = len(self.base)

        upscaled_board = []
        for x in range(size):
            row = []
            for y in range(size):
                tile = self.base[x][y]
                for _ in range(scale - 1):
                    row.append(copy.deepcopy(tile))
                row.append(tile)
            for _ in range(scale - 1):
                upscaled_board.append(copy.deepcopy(row))
            upscaled_board.append(row)

        # Fill in the correct wall tiles
        for x in range(1, size * scale - 2):
            for y in range(1, size * scale - 2):
                if isinstance(upscaled_board[x][y], UnknownTile):
                    # Add the correct tiles to the board.
                    down = upscaled_board[x][y + 1].movement_allowed
                    up = upscaled_board[x][y - 1].movement_allowed
                    left = upscaled_board[x - 1][y].movement_allowed
                    right = upscaled_board[x + 1][y].movement_allowed

                    # Add the correct corner and edge tiles
                    if down:
                        if left:
                            upscaled_board[x][y] = BottomLeftCornerWall()
                            upscaled_board[x][y - 1] = BottomLeftCornerWall2()
                        elif right:
                            upscaled_board[x][y] = BottomRightCornerWall()
                            upscaled_board[x][y - 1] = BottomRightCornerWall2()
                        else:
                            upscaled_board[x][y] = BottomWall()
                            upscaled_board[x][y - 1] = BottomWall2()
                            chance = random.randint(0, 20)
                            if chance == 1:
                                upscaled_board[x][y].image = "edge_b_alt1"
                                upscaled_board[x][y - 1].image = "edge_b_alt1_top"
                            if chance == 2:
                                upscaled_board[x][y].image = "edge_b_alt2"
                                upscaled_board[x][y - 1].image = "edge_b_alt2_top"
                            if chance == 3:
                                upscaled_board[x][y].image = "edge_b_alt3"
                    elif up:
                        if left:
                            upscaled_board[x][y] = TopLeftCornerWall2()
                            upscaled_board[x][y + 1] = TopLeftCornerWall()
                        elif right:
                            upscaled_board[x][y] = TopRightCornerWall2()
                            upscaled_board[x][y + 1] = TopRightCornerWall()
                        else:
                            upscaled_board[x][y] = TopWall()
                            chance = random.randint(0, 10)
                            if chance == 1:
                                upscaled_board[x][y].image = "edge_t_alt1"
                    elif left:
                        upscaled_board[x][y] = LeftWall()

                    elif right:
                        upscaled_board[x][y] = RightWall()
                    else:
                        bl = upscaled_board[x - 1][y + 1].movement_allowed
                        tl = upscaled_board[x - 1][y - 1].movement_allowed
                        br = upscaled_board[x + 1][y + 1].movement_allowed
                        tr = upscaled_board[x + 1][y - 1].movement_allowed
                        if tr:
                            upscaled_board[x][y] = InnerBottomLeftCornerWall()
                            upscaled_board[x][y - 1] = InnerBottomLeftCornerWall2()
                        if br:
                            upscaled_board[x][y] = InnerTopLeftCornerWall()
                            upscaled_board[x][y - 1] = InnerTopLeftCornerWall2()
                        if tl:
                            upscaled_board[x][y] = InnerBottomRightCornerWall()
                            upscaled_board[x][y - 1] = InnerBottomRightCornerWall2()
                        if bl:
                            upscaled_board[x][y] = InnerTopRightCornerWall()
                            upscaled_board[x][y - 1] = InnerTopRightCornerWall2()

        # Add the correct door tiles
        for x in range(1, size * scale, scale):
            for y in range(1, size * scale, scale):
                tile = upscaled_board[x][y]
                if isinstance(tile, DoorPlaceholder):
                    if tile.orientation == "vertical":
                        for y_repl in range(3):
                            upscaled_board[x - 1][y - 1 + y_repl] = FloorTile()
                            upscaled_board[x + 1][y - 1 + y_repl] = FloorTile()

                        upscaled_board[x][y - 3] = ThinWallTileVerticalConnectorTop2()
                        upscaled_board[x][y - 2] = ThinWallTileVerticalConnectorTop1()
                        upscaled_board[x][y - 1] = ThinWallTileVertical()
                        upscaled_board[x][y + 1] = ThinWallTileVertical()
                        upscaled_board[x][y + 2] = ThinWallTileVerticalConnectorBottom()
                    else:
                        for x_repl in range(3):
                            upscaled_board[x - 1 + x_repl][y - 1] = ThinWallTileHorizontal()
                            upscaled_board[x - 1 + x_repl][y + 1] = FloorTile()

                        upscaled_board[x - 2][y - 1] = ThinWallTileHorizontalConnectorLeft1()
                        upscaled_board[x - 2][y] = ThinWallTileHorizontalConnectorLeft2()
                        upscaled_board[x + 2][y - 1] = ThinWallTileHorizontalConnectorRight1()
                        upscaled_board[x + 2][y] = ThinWallTileHorizontalConnectorRight2()

                        upscaled_board[x - 1][y] = BottomWall()
                        upscaled_board[x + 1][y] = BottomWall()

                    door = Door(None, orientation=tile.orientation)
                    door.position = Point(x, y)
                    self.doors.append(door)

        self.base = upscaled_board
        self.room_centers = [center * scale for center in self.room_centers]

    def generate_props(self):
        size = len(self.base)

        for x in range(0, size):
            for y in range(0, size):
                if isinstance(self.base[x][y], FloorTile):
                    chance = random.randint(0, 30)
                    if chance == 0:
                        self.base[x][y].item = RubbishItem()

    def generate_keys(self, player_spawn_location: Point):
        n_prev_valid_locations = -1
        valid_locations = []

        # Keep looping until we find no more new tiles
        while len(valid_locations) != n_prev_valid_locations:
            n_prev_valid_locations = len(valid_locations)
            valid_locations = flood_fill(self.base, player_spawn_location)
            location_modifiers = [
                Point(x, y) for x in range(-1, 2) for y in range(-1, 2)
            ]

            for door in self.doors:
                if door.key_gotten:
                    continue
                if door.position in valid_locations:
                    # Get the key for this door, place it in a reachable location
                    key = door.get_key()
                    key.position = random.choice(valid_locations) + random.choice(location_modifiers)
                    self.entities.append(key)

                    # Remove the blocked door so we can continue the floodfill
                    self.base[door.position.x][door.position.y] = FloorTile()

        self.valid_3x3_locations = valid_locations
        return self.entities + self.doors

    def generate_chests(self, game, n_chests=50, loot_table: Tuple[List[float], List[str]] = None):
        location_modifiers = [
            Point(x, y) for x in range(-1, 2) for y in range(-1, 2)
        ]

        chests = []
        for i in range(n_chests):
            # Generate a position we can move on, and where no entities are placed yet
            position = random.choice(self.valid_3x3_locations) + random.choice(location_modifiers)
            while (
                    not self.base[position.x][position.y].movement_allowed or
                    len(game.get_entities_at(position)) != 0
            ):
                position = random.choice(self.valid_3x3_locations)

            chest = Chest(game)
            chest.position = position
            loot_name = random.choices(loot_table[1], weights=loot_table[0])[0]
            chest.add_loot(loot_name)
            chests.append(chest)

        return chests

    def print(self):
        for row in self.base:
            for tile in row:
                print(tile, end="")
            print("\n")

    def generate_board(self, size, room) -> Tuple[List[List[Tile]], List[Point]]:
        scale = 3
        if size % scale != 0:
            raise ValueError("Room size must be a multiple of %d.", scale)
        generator_size = size // scale
        if generator_size % 2 == 0:
            raise ValueError("Room size cannot be an even number.")

        self.doors.clear()
        self.entities.clear()
        self.room_centers.clear()

        self.base = [[UnknownTile() for _ in range(generator_size)] for _ in range(generator_size)]

        self.room_generator(generator_size, attempts=30)
        self.maze_generator()
        self.connector_generator()
        self.remove_dead_ends()
        self.upscale_nx(scale=scale)
        self.generate_props()

        return self.base, self.room_centers
