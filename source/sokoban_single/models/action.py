
import enum
class Direction(enum.Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    
class Action:
    NAME_MAP ={
        Direction.UP: "North",
        Direction.DOWN: "South",
        Direction.LEFT: "West",
        Direction.RIGHT: "East"
    }
    @staticmethod
    def get_delta(direction: Direction) -> tuple[int, int]:
        return direction.value
    # Trả về sự thay đổi tọa độ (dx, dy) tương ứng với hướng đi.
    @staticmethod
    def to_string(direction: Direction) -> str:
        return Action.NAME_MAP[direction]
    # Lấy ra kết quả di chuyển theo hướng đã chọn