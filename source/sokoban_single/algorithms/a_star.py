import heapq
import os
import sys
import time

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.board import Board
from sokoban_single.algorithms.base_search import BaseSearch, Node
from sokoban_single.algorithms.heuristics import SokobanHeuristic
from sokoban_single.models.problem import SokobanProblem


# Lớp AStarSearch thực thi thuật toán A* Search kế thừa từ BaseSearch
class AStarSearch(BaseSearch):
    def __init__(self, board: Board):
        super().__init__()
        self.board = board
        # Khởi tạo đối tượng tính Heuristic h(n) bằng BFS Real Distance
        self.heuristic = SokobanHeuristic(board)

    # Hàm thực thi giải bài toán Sokoban bằng A*
    def solve(self, problem: SokobanProblem):
        start_time = time.time()
        self.nodes_expanded = 0

        # Tính h(n) cho trạng thái ban đầu
        initial_h = self.heuristic.compute(problem.initial_state)

        # Nếu trạng thái ban đầu đã rơi vào Deadlock (h = inf) -> Không thể giải
        if initial_h == float('inf'):
            self.execution_time = time.time() - start_time
            self.memory_used = self.get_memory_usage()
            return None, float('inf'), self.nodes_expanded, self.execution_time, self.memory_used

        # Khởi tạo Node gốc (g_cost = 0, h_cost = initial_h)
        start_node = Node(state=problem.initial_state, parent=None, action=None, g_cost=0, h_cost=initial_h)

        # Hàng đợi ưu tiên (Priority Queue) sắp xếp theo f_cost = g_cost + h_cost
        counter = 0
        frontier = []
        heapq.heappush(frontier, (start_node.f_cost, counter, start_node))

        # Lưu chi phí g_cost nhỏ nhất tới từng State để tránh duyệt lặp
        explored = {problem.initial_state: 0}

        while frontier:
            # Lấy node có f_cost nhỏ nhất ra khỏi hàng đợi
            _, _, current_node = heapq.heappop(frontier)

            # Nếu g_cost của node hiện tại lớn hơn g_cost ngắn nhất đã ghi nhận -> Bỏ qua
            if current_node.g_cost > explored.get(current_node.state, float('inf')):
                continue

            self.nodes_expanded += 1

            # Kiểm tra xem trạng thái hiện tại đã đạt mục tiêu (Goal Test) chưa
            if problem.is_goal(current_node.state):
                self.execution_time = time.time() - start_time
                self.memory_used = self.get_memory_usage()

                # Truy vết đường đi và trả về kết quả
                path_actions = self.reconstruct_path(current_node)
                return path_actions, current_node.g_cost, self.nodes_expanded, self.execution_time, self.memory_used

            # Sinh các trạng thái kế tiếp hợp lệ
            for next_state, action, step_cost in problem.get_successors(current_node.state):
                new_g_cost = current_node.g_cost + step_cost

                # Nếu tìm được đường đi tới next_state với g_cost tốt hơn
                if next_state not in explored or new_g_cost < explored[next_state]:
                    # Tính h(n) cho trạng thái mới
                    h_cost = self.heuristic.compute(next_state)

                    # Bỏ qua nếu trạng thái rơi vào góc chết (Deadlock)
                    if h_cost == float('inf'):
                        continue

                    explored[next_state] = new_g_cost
                    child_node = Node(state=next_state, parent=current_node, action=action, g_cost=new_g_cost, h_cost=h_cost)
                    counter += 1
                    heapq.heappush(frontier, (child_node.f_cost, counter, child_node))

        # Trả về None nếu không tìm thấy lời giải
        self.execution_time = time.time() - start_time
        self.memory_used = self.get_memory_usage()
        return None, float('inf'), self.nodes_expanded, self.execution_time, self.memory_used