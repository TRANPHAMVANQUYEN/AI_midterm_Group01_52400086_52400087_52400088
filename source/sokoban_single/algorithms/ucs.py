import heapq
import os
import sys
import time

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sokoban_single.algorithms.base_search import BaseSearch, Node
from sokoban_single.models.problem import SokobanProblem


# Lớp UCSSearch thực thi thuật toán Uniform Cost Search kế thừa từ BaseSearch
class UCSSearch(BaseSearch):
    def __init__(self):
        super().__init__()

    # Hàm thực thi giải bài toán Sokoban bằng UCS
    def solve(self, problem: SokobanProblem):
        start_time = time.time()
        self.nodes_expanded = 0

        # Khởi tạo Node gốc từ trạng thái ban đầu của bài toán (g_cost = 0, h_cost = 0)
        start_node = Node(state=problem.initial_state, parent=None, action=None, g_cost=0, h_cost=0)

        # Hàng đợi ưu tiên (Priority Queue) chứa các node cần duyệt
        # Lưu dưới dạng tuple: (f_cost, counter, node) để tránh lỗi so sánh trực tiếp khi f_cost bằng nhau
        counter = 0
        frontier = []
        heapq.heappush(frontier, (start_node.g_cost, counter, start_node))

        # Lưu chi phí g_cost nhỏ nhất tới từng State để tránh duyệt lặp trạng thái không tối ưu
        explored = {problem.initial_state: 0}

        while frontier:
            # Lấy node có g_cost nhỏ nhất ra khỏi hàng đợi
            current_g, _, current_node = heapq.heappop(frontier)

            # Nếu g_cost trong hàng đợi lớn hơn chi phí đã ghi nhận ngắn nhất -> Bỏ qua
            if current_g > explored.get(current_node.state, float('inf')):
                continue

            self.nodes_expanded += 1

            # Kiểm tra xem trạng thái hiện tại đã đạt mục tiêu (Goal Test) chưa
            if problem.is_goal(current_node.state):
                self.execution_time = time.time() - start_time
                self.memory_used = self.get_memory_usage()
                
                # Truy vết đường đi và trả về danh sách kết quả
                path_actions = self.reconstruct_path(current_node)
                return path_actions, current_node.g_cost, self.nodes_expanded, self.execution_time, self.memory_used

            # Sinh các trạng thái kế tiếp hợp lệ
            for next_state, action, step_cost in problem.get_successors(current_node.state):
                new_g_cost = current_node.g_cost + step_cost

                # Nếu trạng thái chưa được duyệt HOẶC tìm được đường đi tới trạng thái đó với g_cost rẻ hơn
                if next_state not in explored or new_g_cost < explored[next_state]:
                    explored[next_state] = new_g_cost
                    child_node = Node(state=next_state, parent=current_node, action=action, g_cost=new_g_cost, h_cost=0)
                    counter += 1
                    heapq.heappush(frontier, (new_g_cost, counter, child_node))

        # Trả về None nếu không tìm thấy lời giải
        self.execution_time = time.time() - start_time
        self.memory_used = self.get_memory_usage()
        return None, float('inf'), self.nodes_expanded, self.execution_time, self.memory_used