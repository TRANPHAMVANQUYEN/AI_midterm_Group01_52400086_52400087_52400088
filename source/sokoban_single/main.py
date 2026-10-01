import os
import sys

# Tự động định vị thư mục gốc 'source' để import không bị lỗi
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.board import Board
from sokoban_single.algorithms.a_star import AStarSearch
from sokoban_single.algorithms.ucs import UCSSearch
from sokoban_single.models.problem import SokobanProblem
from sokoban_single.ui.game_gui import GameGUI
from sokoban_single.ui.menu import MenuGUI


def main():
    # 1. Đường dẫn file bản đồ (Mặc định lấy file example_map.txt)
    map_path = "maps/example_map.txt"
    if not os.path.exists(map_path):
        os.makedirs("maps", exist_ok=True)
        with open(map_path, "w") as f:
            f.write("%%%%%\n%DAB%\n%%%%%")

    # 2. Hiển thị Menu GUI chọn thuật toán (UCS hoặc A*)
    menu = MenuGUI()
    algo_choice = menu.run()

    # Nếu người dùng tắt cửa sổ Menu thì thoát chương trình
    if algo_choice is None:
        print("Đã đóng Menu.")
        return

    # 3. Nạp bản đồ và tạo đối tượng bài toán[cite: 1]
    board = Board(map_path)
    problem = SokobanProblem(board)

    # 4. Thực thi thuật toán được chọn từ Menu
    if algo_choice == "UCS":
        print("\n--> Đang thực thi Uniform Cost Search (UCS)...")
        solver = UCSSearch()
        actions, cost, expanded, time_sec, mem_mb = solver.solve(problem)
        algo_name = "UCS"
    else:
        print("\n--> Đang thực thi A* Search (BFS Real Distance Heuristic)...")
        solver = AStarSearch(board)
        actions, cost, expanded, time_sec, mem_mb = solver.solve(problem)
        algo_name = "A*"

    # 5. In thông số thực nghiệm ra Console
    print("--------------------------------------------------")
    print(f"KẾT QUẢ THỰC NGHIỆM ({algo_name}):")
    print("Danh sách nước đi:", actions)
    print("Tổng chi phí (Cost):", cost)
    print("Số node đã mở (Nodes Expanded):", expanded)
    print(f"Thời gian xử lý: {time_sec:.4f} giây")
    print(f"Dung lượng bộ nhớ: {mem_mb:.2f} MB")
    print("--------------------------------------------------\n")

    if actions is None:
        print("Bản đồ này không có lời giải!")
        return

    # 6. Đóng gói thông số hiệu năng và khởi chạy giao diện xem lời giải (GameGUI)
    stats = {
        "cost": cost,
        "nodes": expanded,
        "time": time_sec,
        "memory": mem_mb
    }

    gui = GameGUI(board, problem, actions, stats)
    gui.run()


if __name__ == "__main__":
    main()