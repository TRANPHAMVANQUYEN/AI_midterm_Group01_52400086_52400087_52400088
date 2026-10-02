from collections import deque

from common.board import Board
from sokoban_single.models.action import Direction
from sokoban_single.models.state import State

INF = float("inf")


class Heuristic:
    """h(state) = tổng khoảng cách ngắn nhất ghép hộp với đích (min-cost matching).

    Khoảng cách là số ô đi thật (BFS, tránh tường), không phải Euclid hay Manhattan.
    Hộp kẹt góc mà không nằm trên đích thì trả về inf (deadlock).
    """

    def __init__(self, board: Board):
        self.board = board
        self.targets = sorted(board.target)
        # dist[j][ô] = số bước ngắn nhất từ ô đó tới đích thứ j
        self.dist = [self._bfs(t) for t in self.targets]
        self._cache: dict = {}

    def _bfs(self, start) -> dict:
        dist = {start: 0}
        queue = deque([start])
        while queue:
            r, c = queue.popleft()
            for d in Direction:
                dr, dc = d.value
                nxt = (r + dr, c + dc)
                if nxt not in dist and not self.board.is_wall(nxt):
                    dist[nxt] = dist[(r, c)] + 1
                    queue.append(nxt)
        return dist

    def _is_corner_deadlock(self, pos) -> bool:
        if pos in self.board.target:
            return False
        r, c = pos
        wall = self.board.is_wall
        up, down = wall((r - 1, c)), wall((r + 1, c))
        left, right = wall((r, c - 1)), wall((r, c + 1))
        return (up or down) and (left or right)

    def __call__(self, state: State) -> float:
        boxes = state.boxes_pos
        if boxes in self._cache:
            return self._cache[boxes]

        if any(self._is_corner_deadlock(b) for b in boxes):
            value = INF
        else:
            value = self._min_matching(sorted(boxes))
        self._cache[boxes] = value
        return value

    def _min_matching(self, boxes) -> float:
        """Quy hoạch động theo bitmask: ghép mỗi hộp với một đích khác nhau."""
        n = len(self.targets)
        dp = {0: 0}
        for b in boxes:
            new = {}
            for mask, cost in dp.items():
                for j in range(n):
                    if mask >> j & 1:
                        continue
                    d = self.dist[j].get(b)
                    if d is None:
                        continue
                    nm = mask | (1 << j)
                    c = cost + d
                    if c < new.get(nm, INF):
                        new[nm] = c
            dp = new
            if not dp:
                return INF
        return min(dp.values())