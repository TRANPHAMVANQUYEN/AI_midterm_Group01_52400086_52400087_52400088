import time
import tracemalloc
from sokoban_single.models.action import Action, Direction
from sokoban_single.models.problem import SokobanProblem
from sokoban_single.models.state import State

class Node:
    __slots__ = ("state", "parent", "action", "g_cost", "h_cost", "f_cost")

    def __init__(self, state: State, parent=None, action: Direction | None = None,
                 g_cost: int = 0, h_cost: int = 0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g_cost = g_cost            # chi phí thực từ đầu tới đây
        self.h_cost = h_cost            # ước lượng tới đích
        self.f_cost = g_cost + h_cost   # f = g + h

    def __lt__(self, other: "Node") -> bool:
        # Hòa f thì ưu tiên node có h nhỏ hơn (gần đích hơn)
        return (self.f_cost, self.h_cost) < (other.f_cost, other.h_cost)


class BaseSearch:
    """Lớp cha cho UCS và A*: lo đo đạc, lớp con chỉ cài _search."""

    def __init__(self):
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_frontier = 0        # số node lớn nhất trong frontier
        self.execution_time = 0.0    # giây
        self.memory_used = 0.0       # MB (bộ nhớ đỉnh Python cấp phát)

    def solve(self, problem: SokobanProblem) -> list[Direction] | None:
        """Chạy tìm kiếm, đo thời gian và bộ nhớ. Trả về path hoặc None."""
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_frontier = 0

        tracemalloc.start()
        start = time.perf_counter()
        goal_node = self._search(problem)
        self.execution_time = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.memory_used = peak / (1024 * 1024)

        if goal_node is None:
            return None
        return self.reconstruct_path(goal_node)

    def _search(self, problem: SokobanProblem) -> Node | None:
        """Trả về node đích, hoặc None nếu vô nghiệm. Lớp con phải cài."""
        raise NotImplementedError("Lớp con phải cài đặt _search.")

    @staticmethod
    def reconstruct_path(node: Node) -> list[Direction]:
        """Truy vết từ node đích về đầu, trả về list Direction."""
        path = []
        while node.parent is not None:
            path.append(node.action)
            node = node.parent
        path.reverse()
        return path

    @staticmethod
    def path_to_strings(path: list[Direction]) -> list[str]:
        """Đổi path sang North/South/West/East để in theo đề."""
        return [Action.to_string(d) for d in path]