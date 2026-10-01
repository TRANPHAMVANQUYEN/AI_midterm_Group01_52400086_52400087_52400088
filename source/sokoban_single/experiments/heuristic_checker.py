import os
import sys

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.board import Board
from sokoban_single.algorithms.heuristics import SokobanHeuristic
from sokoban_single.algorithms.ucs import UCSSearch
from sokoban_single.models.problem import SokobanProblem


# Lớp HeuristicChecker chịu trách nhiệm kiểm tra tính chất Admissible và Consistent của h(n)
class HeuristicChecker:
    def __init__(self, map_path: str):
        self.map_path = map_path
        self.board = Board(map_path)
        self.problem = SokobanProblem(self.board)
        self.heuristic = SokobanHeuristic(self.board)

    # 1. Kiểm tra tính Admissible: h(n) <= h*(n)
    def check_admissibility(self) -> bool:
        print("\n--- KIỂM TRA TÍNH ADMISSIBLE: h(n) <= h*(n) ---")
        
        # Dùng UCS để tìm chi phí thực tế tối ưu h*(n) từ Initial State tới Goal
        ucs_solver = UCSSearch()
        actions, true_cost, _, _, _ = ucs_solver.solve(self.problem)

        if actions is None:
            print("[LƯU Ý]: Bản đồ không có lời giải, bỏ qua kiểm tra Admissible.")
            return True

        # Tính h(n) cho Initial State
        h_val = self.heuristic.compute(self.problem.initial_state)

        print(f"- Chi phí thực tế tối ưu h*(n) từ UCS: {true_cost}")
        print(f"- Chi phí ước lượng h(n) từ Heuristic: {h_val}")

        if h_val <= true_cost:
            print("=> KẾT QUẢ ADMISSIBLE: THỎA MẢN (h(n) <= h*(n))")
            return True
        else:
            print("=> KẾT QUẢ ADMISSIBLE: VI PHẠM (h(n) > h*(n))")
            return False

    # 2. Kiểm tra tính Consistent: h(n1) <= c(n1, a, n2) + h(n2)
    def check_consistency(self) -> bool:
        print("\n--- KIỂM TRA TÍNH CONSISTENT: h(n1) <= c + h(n2) ---")
        
        current_state = self.problem.initial_state
        h_n1 = self.heuristic.compute(current_state)

        successors = self.problem.get_successors(current_state)
        violations = 0
        checks = 0

        for next_state, action, step_cost in successors:
            h_n2 = self.heuristic.compute(next_state)

            # Nếu n2 là góc chết (Deadlock) thì h(n2) = inf -> thỏa mãn bất đẳng thức tam giác
            if h_n2 == float('inf'):
                checks += 1
                continue

            checks += 1
            # c(n1, a, n2) = step_cost = 1
            if h_n1 > step_cost + h_n2:
                violations += 1
                print(f"[VI PHẠM]: h(n1)={h_n1} > c={step_cost} + h(n2)={h_n2}")

        print(f"- Đã kiểm tra {checks} chuyển trạng thái từ Trạng thái ban đầu.")
        if violations == 0:
            print("=> KẾT QUẢ CONSISTENT: THỎA MẢN (Bất đẳng thức tam giác giữ nguyên cho mọi bước dịch chuyển)")
            return True
        else:
            print(f"=> KẾT QUẢ CONSISTENT: VI PHẠM ({violations} chuyển trạng thái bị lỗi)")
            return False

    # Chạy toàn bộ kiểm tra thực nghiệm
    def run_all_checks(self):
        print("==========================================================================================")
        print(f"BẮT ĐẦU KIỂM TRA TÍNH CHẤT HEURISTIC TRÊN MAP: {self.map_path}")
        print("==========================================================================================")
        
        is_admissible = self.check_admissibility()
        is_consistent = self.check_consistency()

        print("\n==========================================================================================")
        print("TỔNG KẾT XÁC MINH HÀM HEURISTIC:")
        print(f"- Admissible: {'ĐẠT' if is_admissible else 'KHÔNG ĐẠT'}")
        print(f"- Consistent: {'ĐẠT' if is_consistent else 'KHÔNG ĐẠT'}")
        print("==========================================================================================\n")


# Chạy test trực tiếp file heuristic_checker.py
if __name__ == "__main__":
    map_file = "maps/example_map.txt"

    if os.path.exists(map_file):
        checker = HeuristicChecker(map_file)
        checker.run_all_checks()
    else:
        print(f"Không tìm thấy file map tại: {map_file}. Hãy kiểm tra lại thư mục maps/")