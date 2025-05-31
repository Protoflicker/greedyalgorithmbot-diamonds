import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class original(BaseLogic):  
    def __init__(self):
        super().__init__()
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # East, South, West, North
        self.goal_position: Optional[Position] = None
        self.path: List[Position] = []
        self.visited: set[Position] = set()
        self.max_path_length: int = 200
        self.path_index: int = 0
        self.inventory_full_threshold: int = 5

    def heuristic(self, pos1: Position, pos2: Position) -> int:
        """Estimates the Manhattan distance between two positions.
        (M 02 - Algoritma Brute Force Bag1.pdf, M 07 - Algoritma Divide and Conquer Bag1.pdf)
        """
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def get_neighbors(self, board: Board, position: Position) -> List[Position]:
        neighbors = []
        for dx, dy in self.directions:
            new_pos = Position(x=position.x + dx, y=position.y + dy)
            if self.is_valid_position(board, position, new_pos):
                neighbors.append(new_pos)
        teleporters = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]
        for tele in teleporters:
            if position.x == tele.position.x and position.y == tele.position.y:
                for other in teleporters:
                    if tele.position != other.position:
                        neighbors.append(other.position)
        return neighbors

    def is_valid_position(self, board: Board, current_pos: Position, next_pos: Position) -> bool:
        return 0 <= next_pos.x < board.width and 0 <= next_pos.y < board.height

    def find_path_a_star(self, board: Board, start: Position, goal: Position, avoid: List[Position] = None) -> bool:
        """
        Finds the shortest path using A* search.
        (M 14 - Route Planning Bag1 .pdf, M 15 - Route Planning Bag2.pdf)
        """

        self.path.clear()
        self.path_index = 0
        self.visited.clear()
        start_key, goal_key = (start.x, start.y), (goal.x, goal.y)
        frontier = [(0, start_key)]
        came_from = {start_key: None}
        cost_so_far = {start_key: 0}
        self.visited.add(start_key)
        while frontier:
            frontier.sort(key=lambda x: x[0])
            _, current_key = frontier.pop(0)
            if current_key == goal_key:
                path = [Position(x=current_key[0], y=current_key[1])]
                while current_key != start_key and current_key is not None:
                    current_key = came_from.get(current_key)
                    if current_key is not None:
                        path.insert(0, Position(x=current_key[0], y=current_key[1]))
                    else:
                        return False
                self.path = path
                return True
            if len(self.path) > self.max_path_length:
                return False
            current_pos = Position(x=current_key[0], y=current_key[1])
            for next_pos in self.get_neighbors(board, current_pos):
                next_key = (next_pos.x, next_pos.y)
                if next_key not in self.visited:
                    new_cost = cost_so_far[current_key] + 1
                    cost_so_far[next_key] = new_cost
                    priority = new_cost + self.heuristic(next_pos, Position(x=goal_key[0], y=goal_key[1]))
                    frontier.append((priority, next_key))
                    came_from[next_key] = current_key
                    self.visited.add(next_key)
        return False

    def get_next_move_from_path(self, current_pos: Position) -> Tuple[int, int]:
        if not self.path or self.path_index >= len(self.path) - 1:
            return self.get_random_move(current_pos, None)
        next_pos = self.path[self.path_index + 1]
        self.path_index += 1
        return get_direction(current_pos.x, current_pos.y, next_pos.x, next_pos.y)

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        self.current_board = board
        self.position = board_bot.position
        diamonds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject"]
        base_position = board_bot.properties.base

        if self.goal_position and not any(d.position.x == self.goal_position.x and d.position.y == self.goal_position.y for d in diamonds):
            self.path = []
            self.goal_position = None

        if self.should_return_to_base(board_bot, board):
            if not self.find_path_a_star(board, self.position, base_position):
                return self.get_random_move(self.position, board)
            self.path_index = 0
            return self.get_next_move_from_path(self.position)

        cluster_radius = 2
        target_diamond = self.select_target_diamond(board, diamonds)
        cluster_nearby = target_diamond and self.heuristic(self.position, target_diamond.position) <= cluster_radius

        red_buttons = [obj for obj in board.game_objects if obj.type == "DiamondButtonGameObject"]
        red_button_nearby = next((rb for rb in red_buttons if self.heuristic(self.position, rb.position) <= 2), None)

        if cluster_nearby:
            if self.find_path_a_star(board, self.position, target_diamond.position):
                self.path_index = 0
                return self.get_next_move_from_path(self.position)
            return self.get_random_move(self.position, board)

        if red_button_nearby:
            if self.find_path_a_star(board, self.position, red_button_nearby.position):
                self.path_index = 0
                return self.get_next_move_from_path(self.position)
            return self.get_random_move(self.position, board)

        if target_diamond:
            if self.find_path_a_star(board, self.position, target_diamond.position):
                self.path_index = 0
                return self.get_next_move_from_path(self.position)
            return self.get_random_move(self.position, board)
        return self.get_random_move(self.position, board)

    def should_return_to_base(self, board_bot: GameObject, board: Board) -> bool:
        steps_to_base = self.heuristic(self.position, board_bot.properties.base)
        time_left = int(board_bot.properties.milliseconds_left / 1000)
        diamonds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject"]
        diamond_nearby = any(self.heuristic(self.position, d.position) <= 3 for d in diamonds)
        return (
            board_bot.properties.diamonds >= self.inventory_full_threshold
            or steps_to_base >= time_left - 5
            or (board_bot.properties.diamonds > 2 and steps_to_base <= 5 and not diamond_nearby)
            or (time_left <= 5 and not diamond_nearby)
        )

    def select_target_diamond(self, board: Board, diamonds: List[GameObject]) -> Optional[GameObject]:
        """
        Pilih diamond target terbaik (cluster terdekat/terbaik), jika tidak ada cluster, ambil diamond terdekat.
        """
        if not diamonds:
            return None
        inventory = board.bots[board.bot_index].properties.diamonds if hasattr(board, "bot_index") else 0
        base_pos = board.bots[board.bot_index].properties.base if hasattr(board, "bot_index") else Position(0, 0)
        # Tambahkan filter ini:
        if inventory >= 4:
            # Ignore red diamond, hanya proses blue diamond
            diamonds = [d for d in diamonds if getattr(d.properties, "points", 1) == 1]
            if not diamonds:
                return None

        cluster_radius = 2
        max_cluster_score = 0
        best_cluster: List[GameObject] = []
        min_total_dist = float('inf')
        teleporters = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]

        near_base_diamonds = [d for d in diamonds if self.heuristic(d.position, base_pos) <= 5]
        if near_base_diamonds:
            for diamond in near_base_diamonds:
                cluster = [other for other in near_base_diamonds if self.heuristic(diamond.position, other.position) <= cluster_radius]
                cluster_score = sum(2 if d.properties.points == 2 else 1 for d in cluster)
                min_dist = float('inf')
                for d in cluster:
                    dist_direct = self.heuristic(self.position, d.position)
                    dist_tp = dist_direct
                    if len(teleporters) >= 2:
                        for tp1 in teleporters:
                            for tp2 in teleporters:
                                if tp1.position != tp2.position:
                                    dist_tp = min(dist_tp, self.heuristic(self.position, tp1.position) + 1 + self.heuristic(tp2.position, d.position))
                    min_dist = min(min_dist, dist_tp)
                total_dist = min_dist
                if (cluster_score > max_cluster_score) or (
                    cluster_score == max_cluster_score and total_dist < min_total_dist
                ):
                    max_cluster_score = cluster_score
                    best_cluster = cluster
                    min_total_dist = total_dist
            if best_cluster:
                return min(best_cluster, key=lambda d: self.heuristic(self.position, d.position))

        max_cluster_score = 0
        best_cluster = []
        min_total_dist = float('inf')
        for diamond in diamonds:
            cluster = [other for other in diamonds if self.heuristic(diamond.position, other.position) <= cluster_radius]
            cluster_score = sum(2 if d.properties.points == 2 else 1 for d in cluster)
            min_dist = float('inf')
            for d in cluster:
                dist_direct = self.heuristic(self.position, d.position)
                dist_tp = dist_direct
                if len(teleporters) >= 2:
                    for tp1 in teleporters:
                        for tp2 in teleporters:
                            if tp1.position != tp2.position:
                                dist_tp = min(dist_tp, self.heuristic(self.position, tp1.position) + 1 + self.heuristic(tp2.position, d.position))
                min_dist = min(min_dist, dist_tp)
            total_dist = min_dist
            if inventory >= 3:
                dist_to_base = self.heuristic(diamond.position, base_pos)
                if (cluster_score > max_cluster_score) or (
                    cluster_score == max_cluster_score and total_dist < min_total_dist
                ):
                    max_cluster_score = cluster_score
                    best_cluster = cluster
                    min_total_dist = total_dist
            else:
                if cluster_score > max_cluster_score or (
                    cluster_score == max_cluster_score and (
                        not best_cluster or total_dist < min_total_dist
                    )
                ):
                    max_cluster_score = cluster_score
                    best_cluster = cluster
                    min_total_dist = total_dist
        if best_cluster:
            return min(best_cluster, key=lambda d: self.heuristic(self.position, d.position))
        #greedy closest diamond
        closest_target = None
        min_dist = float('inf')
        for target in diamonds:
            dist = self.heuristic(self.position, target.position)
            if dist < min_dist:
                min_dist = dist
                closest_target = target
        return closest_target