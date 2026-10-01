import time

import os
from sokoban_single.models.action import Action
from sokoban_single.models.problem import SokobanProblem
from sokoban_single.models.state import State


# Node dùng để lưu thông tin cây tìm kiếm
class Node:
    def __init__(self, state: State, parent=None, action=None, g_cost: int = 0, h_cost: int = 0):
        self.state = state        # Trạng thái hiện tại
        self.parent = parent      # Node cha
        self.action = action      # Hành động dẫn tới node này
        self.g_cost = g_cost      # Chi phí thực tế từ điểm đầu (g)
        self.h_cost = h_cost      # Chi phí ước lượng tới đích (h)
        self.f_cost = g_cost + h_cost  # Tổng chi phí f = g + h

    # So sánh độ ưu tiên trong hàng đợi heapq (so sánh giá trị f_cost)
    def __lt__(self, other):
        return self.f_cost < other.f_cost


# Lớp trừu tượng cho các thuật toán tìm kiếm
class BaseSearch:
    def __init__(self):
        self.nodes_expanded = 0   # Số lượng node đã duyệt
        self.execution_time = 0.0 # Thời gian thực thi (giây)
        self.memory_used = 0.0    # Bộ nhớ tiêu thụ (MB)

    # Hàm truy vết lại danh sách các hành động từ đích về đầu
    def reconstruct_path(self, node: Node) -> list[str]:
        path = []
        curr = node
        while curr.parent is not None:
            # Chuyển hướng di chuyển sang định dạng chuỗi tiếng Anh (North, South...)[cite: 1]
            action_str = Action.to_string(curr.action)
            path.append(action_str)
            curr = curr.parent
        path.reverse()  # Đảo ngược lại để được chuỗi từ đầu đến đích
        return path

    # Đo lượng bộ nhớ RAM đang sử dụng (MB)
    def get_memory_usage(self) -> float:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)

    # Hàm giải bài toán (sẽ được các lớp UCS và AStar ghi đè)
    def solve(self, problem: SokobanProblem):
        raise NotImplementedError("Hàm solve phải được cài đặt ở lớp con.")