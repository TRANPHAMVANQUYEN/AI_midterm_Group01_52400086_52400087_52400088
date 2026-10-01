import os
import sys
from collections import deque

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.board import Board
from sokoban_single.models.state import State


# Lớp SokobanHeuristic chịu trách nhiệm tính hàm đánh giá h(n)
class SokobanHeuristic:
    def __init__(self, board: Board):
        self.board = board
        # Ma trận lưu trữ khoảng cách thực tế ngắn nhất từ mỗi ô tới từng ô đích
        # Cấu trúc: { pos_đích: { pos_ô_trên_map: số_bước_BFS } }
        self.target_distances = {}
        
        # Tính toán trước (Precompute) ma trận khoảng cách bằng BFS ngược từ các ô đích
        self._precompute_target_distances()

    # Thuật toán BFS ngược chạy từ các ô đích đến toàn bộ bản đồ
    def _precompute_target_distances(self):
        for target in self.board.targets:
            self.target_distances[target] = {}
            queue = deque([(target, 0)])
            visited = {target}

            while queue:
                curr_pos, dist = queue.popleft()
                self.target_distances[target][curr_pos] = dist

                r, c = curr_pos
                # Duyệt 4 hướng lân cận (Trái, Phải, Trên, Dưới)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    next_pos = (r + dr, c + dc)
                    # Nếu không phải tường % và chưa truy cập
                    if not self.board.is_wall(next_pos) and next_pos not in visited:
                        visited.add(next_pos)
                        queue.append((next_pos, dist + 1))

    # Phát hiện trạng thái góc chết (Deadlock Detection)[cite: 1]
    def is_deadlock(self, box_pos: tuple[int, int]) -> bool:
        # Nếu thùng đã đứng đúng ô đích D/C thì không tính là Deadlock[cite: 1, 2]
        if self.board.is_target(box_pos):
            return False

        r, c = box_pos
        # Kiểm tra 4 hướng xung quanh thùng xem có phải tường % không[cite: 1]
        top = self.board.is_wall((r - 1, c))
        bottom = self.board.is_wall((r + 1, c))
        left = self.board.is_wall((r, c - 1))
        right = self.board.is_wall((r, c + 1))

        # Thùng nằm ở góc vuông 2 bức tường mà không phải đích -> Deadlock[cite: 1]
        if (top and left) or (top and right) or (bottom and left) or (bottom and right):
            return True

        return False

    # Hàm tính giá trị h(n) cho một Trạng thái (State)
    def compute(self, state: State) -> float:
        total_h = 0
        targets_list = list(self.board.targets)
        boxes_list = list(state.boxes_pos)

        # 1. Nếu phát hiện bất kỳ thùng nào rơi vào góc chết -> Trả về vô cùng inf[cite: 1]
        for box in boxes_list:
            if self.is_deadlock(box):
                return float('inf')

        # 2. Ghép cặp giữa Thùng và Đích bằng khoảng cách BFS thực tế ngắn nhất
        unassigned_targets = set(targets_list)

        for box in boxes_list:
            min_dist = float('inf')
            best_target = None

            # Tìm ô đích gần thùng này nhất dựa trên số bước BFS thực tế
            for target in unassigned_targets:
                dist = self.target_distances[target].get(box, float('inf'))
                if dist < min_dist:
                    min_dist = dist
                    best_target = target

            # Nếu tìm thấy đích hợp lệ -> Cộng dồn khoảng cách và loại đích đó ra khỏi tập chờ
            if best_target is not None and min_dist != float('inf'):
                total_h += min_dist
                unassigned_targets.remove(best_target)
            else:
                # Thùng không thể di chuyển tới bất kỳ đích nào -> Deadlock
                return float('inf')

        return float(total_h)