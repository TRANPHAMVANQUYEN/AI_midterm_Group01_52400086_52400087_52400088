class State:
    def __init__(self, agent_pos: tuple[int, int], boxes_pos: set[tuple[int, int]] | frozenset[tuple[int, int]]):
        self.agent_pos = agent_pos
        # Chuyển set thành frozenset để dữ liệu không bị thay đổi (immutable) và có thể hash được
        self.boxes_pos = frozenset(boxes_pos)

    def __eq__(self, other) -> bool:
        # Hai State được coi là bằng nhau nếu Agent và tất cả Thùng ở cùng vị trí
        if not isinstance(other, State): # orther xem cái đối tượng so sánh đó có phải là một state hay ko nếu ko thì tiễn
            return False
        return self.agent_pos == other.agent_pos and self.boxes_pos == other.boxes_pos

    def __hash__(self) -> int:
        # Tạo mã hash cho State để lưu được vào visited set / dictionary
        return hash((self.agent_pos, self.boxes_pos))

    def is_box_at(self, pos: tuple[int, int]) -> bool:
        # Kiểm tra xem tại tọa độ pos có thùng hay không
        return pos in self.boxes_pos