import random
from typing import Optional, List, Tuple

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction


class AStarBot(BaseLogic):
    def __init__(self):
        super().__init__()
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # East, South, West, North
        self.goal_position: Optional[Position] = None
        self.inventory_full_threshold: int = 5

    def get_diamond_type(self, diamond: GameObject) -> str:
        """
        Membedakan tipe diamond berdasarkan atribut GameObject.
        Returns:
            - "blue": Blue diamond (points=1)
            - "red": Red diamond (points=2)
            - "button": Red button (type=DiamondButtonGameObject)
        """
        if diamond.type == "DiamondButtonGameObject":
            return "button"
        elif diamond.type == "DiamondGameObject":
            points = getattr(diamond.properties, "points", 1)
            if points == 2:
                return "red"
            else:
                return "blue"
        return "none"

    def heuristic(self, pos1: Position, pos2: Position, board: Board = None, bot_pos: Position = None) -> int:
        """
        Estimasi jarak Manhattan yang mempertimbangkan:
        1. Jarak dari bot ke target
        2. Jarak dari target ke base
        3. Weight dari tipe diamond (blue=1, red=2, button=1/4)
        """
        base_dist = abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)
        min_dist = base_dist

        if board is not None and bot_pos is not None:
            # Hitung jarak dari bot ke target
            bot_to_target = abs(bot_pos.x - pos2.x) + abs(bot_pos.y - pos2.y)
            
            # Gunakan rata-rata jarak bot-target dan target-base
            min_dist = (bot_to_target + base_dist) / 2

            # Cari base position dan hitung nearby diamonds
            base = None
            nearby_diamonds = []
            for bot in board.bots:
                if hasattr(bot.properties, "base"):
                    base = bot.properties.base
                    break
            
            if base:
                nearby_diamonds = [
                    obj for obj in board.game_objects
                    if obj.type == "DiamondGameObject" and
                    abs(obj.position.x - base.x) + abs(obj.position.y - base.y) <= 4
                ]

            # Cari objek pada posisi tujuan dan terapkan weight
            for obj in board.game_objects:
                if obj.position.x == pos2.x and obj.position.y == pos2.y:
                    if obj.type == "DiamondButtonGameObject":
                        # Red button weight=1, kecuali jika diamond dekat base <= 2 maka weight=4
                        weight = 4 if len(nearby_diamonds) <= 2 else 1
                        # Kalkulasikan skor akhir
                        return min_dist - weight
                    elif obj.type == "DiamondGameObject":
                        points = getattr(obj.properties, "points", 1)
                        # Red diamond weight=2, Blue diamond weight=1
                        weight = 2 if points == 2 else 1
                        return min_dist - weight

        return min_dist

    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        self.position = board_bot.position
        inventory = board_bot.properties.diamonds
        base = board_bot.properties.base

        # Kembali ke base jika inventory penuh
        if inventory >= self.inventory_full_threshold:
            dx = base.x - self.position.x
            dy = base.y - self.position.y
            if abs(dx) > abs(dy):
                return (1 if dx > 0 else -1, 0)
            elif dy != 0:
                return (0, 1 if dy > 0 else -1)
            else:
                return (1, 0)

        # Filter game objects dan gunakan heuristic untuk memilih target
        available_targets = [
            obj for obj in board.game_objects 
            if obj.type in ["DiamondGameObject", "DiamondButtonGameObject"]
        ]
        
        if available_targets:
            # Pilih target dengan skor heuristic terendah
            target = min(available_targets, 
                        key=lambda d: self.heuristic(d.position, base, board, self.position))
            
            # Tentukan arah gerakan ke target
            dx = target.position.x - self.position.x
            dy = target.position.y - self.position.y
            if abs(dx) > abs(dy):
                return (1 if dx > 0 else -1, 0)
            elif dy != 0:
                return (0, 1 if dy > 0 else -1)
            else:
                return (1, 0)

        # Jika tidak ada target, kembali ke base
        dx = base.x - self.position.x
        dy = base.y - self.position.y
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        elif dy != 0:
            return (0, 1 if dy > 0 else -1)
        else:
            return (1, 0)

    def should_return_to_base(self, board_bot: GameObject, board: Board) -> bool:
        steps_to_base = self.heuristic(self.position, board_bot.properties.base)
        time_left = int(board_bot.properties.milliseconds_left / 1000)
        diamonds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject"]
        diamond_nearby = any(self.heuristic(self.position, d.position, board) <= 3 for d in diamonds)
        return (
            board_bot.properties.diamonds >= self.inventory_full_threshold
            or steps_to_base >= time_left - 5
            or (board_bot.properties.diamonds > 2 and steps_to_base <= 5 and not diamond_nearby)
            or (time_left <= 5 and not diamond_nearby)
        )

    def select_target_diamond(self, board: Board, diamonds: List[GameObject]) -> Optional[GameObject]:
        """
        Prioritaskan area dengan density diamond tertinggi (berdasarkan jarak-weight/heuristic),
        lalu ambil diamond terdekat di cluster (juga berdasarkan heuristic).
        Jika inventory >= 4, hanya ambil diamond biru (red diamond di-ignore, boleh dilewati).
        """
        if not diamonds:
            return None

        # Jika inventory >= 4, hanya ambil diamond biru (ignore red diamond)
        inventory = board.bots[board.bot_index].properties.diamonds if hasattr(board, "bot_index") else 0
        if inventory >= 4:
            diamonds = [d for d in diamonds if hasattr(d, "properties") and getattr(d.properties, "points", 1) == 1]
            if not diamonds:
                return None

        cluster_radius = 2
        max_cluster_count = 0
        best_cluster_center = None

        # Cari cluster center dengan density tertinggi (pakai heuristic sebagai jarak)
        for diamond in diamonds:
            count = sum(
                self.heuristic(diamond.position, other.position, board) <= cluster_radius
                for other in diamonds
            )
            if count > max_cluster_count or (
                count == max_cluster_count and (
                    self.heuristic(self.position, diamond.position, board) <
                    self.heuristic(self.position, best_cluster_center.position, board) if best_cluster_center else True
                )
            ):
                max_cluster_count = count
                best_cluster_center = diamond

        # Ambil diamond terdekat di cluster (pakai heuristic)
        cluster_diamonds = [
            d for d in diamonds
            if self.heuristic(best_cluster_center.position, d.position, board) <= cluster_radius
        ] if best_cluster_center else []

        if cluster_diamonds:
            return min(cluster_diamonds, key=lambda d: self.heuristic(self.position, d.position, board))
        else:
            # Fallback: diamond terdekat (pakai heuristic)
            return min(diamonds, key=lambda d: self.heuristic(self.position, d.position, board))