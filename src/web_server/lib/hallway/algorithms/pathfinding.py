import heapq
from typing import Optional, List

from src.web_server import timing
from src.web_server.lib.hallway import tiles
from src.web_server.lib.hallway.Utils import Point


#
# A* implementation taken from
# https://www.redblobgames.com/pathfinding/a-star/implementation.html
#
class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, Point]] = []

    def empty(self) -> bool:
        return not self.elements

    def put(self, item: Point, priority: float):
        heapq.heappush(self.elements, (priority, item))

    def get(self) -> Point:
        return heapq.heappop(self.elements)[1]


def get_neighbors(level_map: List[List[tiles.Tile]], current: Point):
    points = [
        Point(current.x + 1, current.y),
        Point(current.x - 1, current.y),
        Point(current.x, current.y + 1),
        Point(current.x, current.y - 1)
    ]
    return [p for p in points if level_map[p.x][p.y].movement_allowed]


def astar(level_map: List[List[tiles.Tile]], start: Point, goal: Point):
    def heuristic(a: Point, b: Point) -> float:
        return a.manhattan_distance(b)

    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Point, Optional[Point]] = {}
    cost_so_far: dict[Point, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: Point = frontier.get()

        if current == goal:
            break

        for neighbour in get_neighbors(level_map, current):
            new_cost = cost_so_far[current] + 1
            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                priority = new_cost + heuristic(neighbour, goal)
                frontier.put(neighbour, priority)
                came_from[neighbour] = current

    if goal not in came_from:
        # TODO: Random walk when we cannot find a path
        return []

    # Build the path
    path = []
    current_point = goal
    while current_point != start:
        path.append(current_point - came_from[current_point])
        current_point = came_from[current_point]

    path.reverse()
    return path
