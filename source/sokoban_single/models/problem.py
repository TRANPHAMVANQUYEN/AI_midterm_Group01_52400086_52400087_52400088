from collections import deque
from common.board import Board
from sokoban_single.models.action import Action, Direction
from sokoban_single.models.state import State

class SokobanProblem:
    def __init__(self, board: Board):
        self.board = board

        # Tạo Trạng thái ban đầu từ vị trí Agent và Thùng do Board khởi tạo
        self.initial_state = State(
            agent_pos=self.board.initial_agent_pos,
            boxes_pos=self.board.initial_boxes_pos
        )
        # Thống nhất dùng self.deadlocks_pos
        self.deadlocks_pos = self.find_deadlocks()

    def is_goal(self, state: State) -> bool:
        return state.boxes_pos == self.board.target

    def find_deadlocks(self) -> set[tuple[int, int]]:
        reachable_pos = set()
        queue = deque()
        visited_pull = set()

        # Khởi tạo từ các điểm Đích
        for target_pos in self.board.target:
            reachable_pos.add(target_pos)  # Ô đích chính là ô thùng đứng hợp lệ
            
            for direction in Direction:
                dr, dc = Action.get_delta(direction)
                pull_agent_pos = (target_pos[0] + dr, target_pos[1] + dc)
                
                if not self.board.is_wall(pull_agent_pos):
                    state_key = (target_pos, pull_agent_pos)
                    queue.append(state_key)
                    visited_pull.add(state_key)

        #BFS Loang để tìm tất cả các ô trống có thể kéo thùng tới từ các ô đích
        while queue:
            box_pos, agent_pos = queue.popleft()
            reachable_pos.add(box_pos)

            for direction in Direction:
                dr, dc = Action.get_delta(direction)
                # Ô thùng dịch chuyển tới khi kéo
                new_box_pos = (box_pos[0] + dr, box_pos[1] + dc)
                # Ô Agent phải đứng để thực hiện lực kéo
                new_agent_pos = (new_box_pos[0] + dr, new_box_pos[1] + dc)

                # Cả ô thùng mới và ô agent đứng kéo đều không được là TƯỜNG
                if not self.board.is_wall(new_box_pos) and not self.board.is_wall(new_agent_pos):
                    pull_state = (new_box_pos, new_agent_pos)
                    
                    if pull_state not in visited_pull:
                        visited_pull.add(pull_state)
                        queue.append(pull_state)

        # 3. Lọc Deadlock: Tất cả ô trống KHÔNG THỂ kéo tới từ Đích
        deadlock_positions = set()
        for r in range(self.board.height):
            for c in range(self.board.width):
                pos = (r, c)
                if not self.board.is_wall(pos) and pos not in reachable_pos:
                    deadlock_positions.add(pos)

        return deadlock_positions

    def get_successors(self, state: State) -> list[tuple[State, Direction, int]]:
        successors = []
        agent_r, agent_c = state.agent_pos

        for direction in Direction:
            dr, dc = Action.get_delta(direction)
            next_agent_pos = (agent_r + dr, agent_c + dc)

            if self.board.is_wall(next_agent_pos):
                continue

            if state.is_box_at(next_agent_pos):
                next_box_pos = (next_agent_pos[0] + dr, next_agent_pos[1] + dc)

                if self.board.is_wall(next_box_pos) or state.is_box_at(next_box_pos):
                    continue

                # Lọc Deadlock bằng tập deadlocks_pos
                if next_box_pos in self.deadlocks_pos:
                    continue

                new_boxes_pos = set(state.boxes_pos)
                new_boxes_pos.remove(next_agent_pos)
                new_boxes_pos.add(next_box_pos)

                new_state = State(agent_pos=next_agent_pos, boxes_pos=new_boxes_pos)
                successors.append((new_state, direction, 1))

            else:
                new_state = State(agent_pos=next_agent_pos, boxes_pos=state.boxes_pos)
                successors.append((new_state, direction, 1))

        return successors