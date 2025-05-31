import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class greedy12(BaseLogic):
    def __init__(self):
        super().__init__()
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.inv_full: int = 5
        self.cluster_radius: int = 2
        self.base_time_penalty: float = 0.5 

    def get_weight(self, obj: GameObject, board: Board, ignore_red=False) -> int:
        if obj.type == "DiamondGameObject":
            points = getattr(obj.properties, "points", 1)
            if ignore_red and points == 2:
                return 0
            return 2 if points == 2 else 1
        elif obj.type == "DiamondButtonGameObject":
            base = next((bot.properties.base for bot in board.bots 
                        if hasattr(bot.properties, "base")), None)
            if base:
                nearby = [
                    o for o in board.game_objects
                    if o.type == "DiamondGameObject" and
                    abs(o.position.x - base.x) + abs(o.position.y - base.y) <= 4
                ]
                total_weight = sum(self.get_weight(o, board) for o in nearby)
                return 3 if total_weight <= 2 else 0
            return 0
        return 0

    def get_cluster_value(self, pos: Position, board: Board, ignore_red: bool) -> float:
        # Menghitung nilai cluster berdasarkan total poin diamond di sekitar
        cluster = [
            o for o in board.game_objects
            if o.type == "DiamondGameObject" and
            abs(o.position.x - pos.x) <= self.cluster_radius and 
            abs(o.position.y - pos.y) <= self.cluster_radius
        ]
        return sum(self.get_weight(o, board, ignore_red) for o in cluster)

    def get_best_path(self, pos1: Position, pos2: Position, board: Board) -> tuple[int, Optional[GameObject]]:
        #distance antar posisi bot dan diamond
        base_dist = abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
        min_dist = base_dist
        best_teleporter = None

        teleporters = [o for o in board.game_objects if o.type == "TeleportGameObject"]
        for tp_a in teleporters:
            for tp_b in teleporters:
                if tp_a is not tp_b:
                    dist = (
                        abs(pos1.x - tp_a.position.x) + abs(pos1.y - tp_a.position.y) + 1 +
                        abs(tp_b.position.x - pos2.x) + abs(tp_b.position.y - pos2.y)
                    )
                    if dist < min_dist:
                        min_dist = dist
                        best_teleporter = tp_a

        return min_dist, best_teleporter

    def heuristic(self, pos1: Position, pos2: Position, board: Board, ignore_red=False, time_left=None) -> float:
        # jarak terbaik antara posisi bot dan diamond
        min_dist, _ = self.get_best_path(pos1, pos2, board)
        
        # Hitung weight objek pada posisi tujuan
        weight = 0
        for obj in board.game_objects:
            if obj.position.x == pos2.x and obj.position.y == pos2.y:
                weight = self.get_weight(obj, board, ignore_red)

        # total weight cluster diamond
        cluster_value = self.get_cluster_value(pos2, board, ignore_red)
        weight += cluster_value * 0.5 

        # semakin sedikit waktu , maka bot akan mencari diamond yang lebih dekat dengan base
        time_penalty = 0
        if time_left:
            time_penalty = max(0, min_dist * self.base_time_penalty * (1000 / time_left))

        return min_dist - weight + time_penalty

    #logika bot untuk kembali ke base
    def gobaselogic(self, bot: GameObject, board: Board, nearest_diamond_dist: int) -> bool:
        base = bot.properties.base
        steps_to_base = abs(bot.position.x - base.x) + abs(bot.position.y - base.y)
        time_left = int(bot.properties.milliseconds_left / 1000)
        return (
            bot.properties.diamonds >= 3 and nearest_diamond_dist > steps_to_base
            or steps_to_base >= time_left
            or bot.properties.diamonds >= self.inv_full
        )

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        self.position = board_bot.position
        base = board_bot.properties.base
        inventory = board_bot.properties.diamonds
        time_left = board_bot.properties.milliseconds_left

        # Filter diamond
        diamonds = [o for o in board.game_objects if o.type == "DiamondGameObject"]
        ignore_red = inventory >= 4
        if ignore_red:
            diamonds = [d for d in diamonds if getattr(d.properties, "points", 1) == 1]

        if not diamonds:
            return self.move_towards(base)

        # Pilih target dengan heuristic yang sudah memperhitungkan waktu
        nearest = min(diamonds, 
                     key=lambda d: self.heuristic(self.position, d.position, 
                                                board, ignore_red, time_left))
        nearest_dist, best_teleporter = self.get_best_path(self.position, nearest.position, board)

        # Cek apakah perlu kembali ke base
        if self.gobaselogic(board_bot, board, nearest_dist):
            return self.move_towards(base)

        # Gunakan jika dengan menggunakan teleporter lebih dekat ke diamond
        if best_teleporter:
            return self.move_towards(best_teleporter.position)

        # Bergerak ke diamond terdekat
        return self.move_towards(nearest.position)

    def move_towards(self, target: Position) -> Tuple[int, int]:
        #bergerak ke arah target
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        elif dy != 0:
            return (0, 1 if dy > 0 else -1)
        return (1, 0)