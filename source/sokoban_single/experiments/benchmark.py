import os
import sys

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from common.board import Board
from sokoban_single.algorithms.a_star import AStarSearch
from sokoban_single.algorithms.ucs import UCSSearch
from sokoban_single.models.problem import SokobanProblem


# Lớp Benchmark chịu trách nhiệm chạy thực nghiệm so sánh hiệu năng các thuật toán
class Benchmark:
    def __init__(self, map_path: str):
        self.map_path = map_path
        self.board = Board(map_path)
        self.problem = SokobanProblem(self.board)

    # Chạy thực nghiệm so sánh giữa UCS và A*
    def run_comparison(self):
        print("==========================================================================================")
        print(f"BẮT ĐẦU THỰC NGHIỆM SO SÁNH TRÊN BẢN ĐỒ: {self.map_path}")
        print("==========================================================================================")

        # 1. Chạy thuật toán Uniform Cost Search (UCS)
        ucs_solver = UCSSearch()
        ucs_actions, ucs_cost, ucs_nodes, ucs_time, ucs_mem = ucs_solver.solve(self.problem)

        # 2. Chạy thuật toán A* Search
        a_star_solver = AStarSearch(self.board)
        astar_actions, astar_cost, astar_nodes, astar_time, astar_mem = a_star_solver.solve(self.problem)

        # 3. Hiển thị bảng so sánh chi tiết
        print("\n" + "-" * 90)
        print(f"{'Thuật toán (Algorithm)':<25} | {'Chi phí (Cost)':<15} | {'Node đã mở':<15} | {'Thời gian (s)':<15} | {'Bộ nhớ (MB)':<12}")
        print("-" * 90)

        ucs_cost_str = str(ucs_cost) if ucs_actions is not None else "N/A"
        print(f"{'Uniform Cost Search (UCS)':<25} | {ucs_cost_str:<15} | {ucs_nodes:<15} | {ucs_time:<15.4f} | {ucs_mem:<12.2f}")

        astar_cost_str = str(astar_cost) if astar_actions is not None else "N/A"
        print(f"{'A* Search (BFS Heuristic)':<25} | {astar_cost_str:<15} | {astar_nodes:<15} | {astar_time:<15.4f} | {astar_mem:<12.2f}")
        print("-" * 90)

        # 4. Phân tích kết quả thực nghiệm
        if ucs_actions and astar_actions:
            print("\n[ĐÁNH GIÁ THỰC NGHIỆM]:")
            print(f"- Cả 2 thuật toán đều tìm ra lời giải tối ưu có chi phí: {ucs_cost} bước.")
            
            if ucs_nodes > 0:
                reduction = ((ucs_nodes - astar_nodes) / ucs_nodes) * 100
                print(f"- Thuật toán A* cắt giảm được {reduction:.2f}% số lượng node duyệt so với UCS.")
            
            if ucs_time > 0:
                speedup = ucs_time / astar_time if astar_time > 0 else 0
                print(f"- Tốc độ xử lý của A* nhanh gấp {speedup:.2f} lần so với UCS.")
        else:
            print("\n[LƯU Ý]: Một hoặc cả hai thuật toán không tìm thấy lời giải trên bản đồ này.")

        print("==========================================================================================\n")

        # Trả về kết quả dạng dictionary để dễ lưu trữ hoặc vẽ biểu đồ
        return {
            "map": self.map_path,
            "ucs": {"cost": ucs_cost, "nodes": ucs_nodes, "time": ucs_time, "memory": ucs_mem},
            "astar": {"cost": astar_cost, "nodes": astar_nodes, "time": astar_time, "memory": astar_mem}
        }


# Chạy test trực tiếp file benchmark.py
if __name__ == "__main__":
    # Thay đổi đường dẫn map cần test
    map_file = "maps/example_map.txt"
    
    if os.path.exists(map_file):
        benchmark = Benchmark(map_file)
        benchmark.run_comparison()
    else:
        print(f"Không tìm thấy file map tại: {map_file}. Hãy kiểm tra lại thư mục maps/")