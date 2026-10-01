from common.board import Board
from sokoban_single.models.action import Action, Direction
from sokoban_single.models.state import State


# Lớp SokobanProblem chịu trách nhiệm mô hình hóa bài toán tìm kiếm không gian trạng thái
class SokobanProblem:
    def __init__(self, board: Board):
        # Lưu tham chiếu tới đối tượng Board chứa thông tin tĩnh như Tường và Đích
        self.board = board

        # Tạo Trạng thái ban đầu (Initial State) từ vị trí Agent và Thùng do Board khởi tạo[cite: 1]
        self.initial_state = State(
            agent_pos=self.board.initial_agent_pos,
            boxes_pos=self.board.initial_boxes_pos
        )

    # Kiểm tra xem trạng thái hiện tại đã đạt mục tiêu chưa[cite: 1]
    def is_goal(self, state: State) -> bool:
        # Đạt mục tiêu khi tập hợp tất cả vị trí thùng trùng hoàn toàn với tập hợp các vị trí đích[cite: 1]
        return state.boxes_pos == self.board.targets

    # Hàm sinh các trạng thái kế tiếp hợp lệ từ trạng thái hiện tại[cite: 1]
    def get_successors(self, state: State) -> list[tuple[State, tuple[int, int], int]]:
        successors = []
        agent_r, agent_c = state.agent_pos  # Tọa độ hàng và cột hiện tại của Agent

        # Duyệt qua từng hướng di chuyển trong danh sách 4 hướng[cite: 1]
        for direction in Direction.ALL:
            dr, dc = Action.get_delta(direction)
            next_agent_pos = (agent_r + dr, agent_c + dc)  # Tọa độ Agent dự kiến bước tới

            # Trường hợp 1: Ô kế tiếp là TƯỜNG (%) -> Bị cản, không đi được[cite: 1]
            if self.board.is_wall(next_agent_pos):
                continue

            # Trường hợp 2: Ô kế tiếp có THÙNG (B hoặc C) -> Xử lý đẩy thùng[cite: 1]
            if state.is_box_at(next_agent_pos):
                # Tọa độ dự kiến của Thùng sau khi bị đẩy cùng hướng
                next_box_pos = (next_agent_pos[0] + dr, next_agent_pos[1] + dc)

                # Kiểm tra cản của Thùng: Không được đẩy vào TƯỜNG hoặc THÙNG KHÁC[cite: 1]
                if self.board.is_wall(next_box_pos) or state.is_box_at(next_box_pos):
                    continue

                # Đẩy thùng thành công: Cập nhật vị trí các thùng
                new_boxes_pos = set(state.boxes_pos)
                new_boxes_pos.remove(next_agent_pos)  # Xóa vị trí cũ của thùng
                new_boxes_pos.add(next_box_pos)       # Thêm vị trí mới của thùng

                # Tạo State mới (Agent đứng ở vị trí cũ của thùng, Thùng dịch sang vị trí mới)
                new_state = State(agent_pos=next_agent_pos, boxes_pos=new_boxes_pos)
                successors.append((new_state, direction, 1))  # Chi phí mỗi bước đẩy là 1

            # Trường hợp 3: Ô kế tiếp là Ô TRỐNG hoặc ĐÍCH (D) -> Agent tự di chuyển[cite: 1]
            else:
                # Tạo State mới (Cập nhật vị trí Agent, giữ nguyên vị trí các thùng)
                new_state = State(agent_pos=next_agent_pos, boxes_pos=state.boxes_pos)
                successors.append((new_state, direction, 1))  # Chi phí mỗi bước đi là 1

        return successors