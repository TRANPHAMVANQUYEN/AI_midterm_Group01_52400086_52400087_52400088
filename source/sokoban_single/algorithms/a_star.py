import heapq

from sokoban_single.algorithms.base_search import BaseSearch, Node
from sokoban_single.algorithms.heuristics import Heuristic


class AStar(BaseSearch):
    def _search(self, problem):
        h = Heuristic(problem.board)
        start = problem.initial_state
        root = Node(start, h_cost=h(start))
        frontier = [root]
        best_g = {start: 0}

        while frontier:
            self.max_frontier = max(self.max_frontier, len(frontier))
            node = heapq.heappop(frontier)

            if node.g_cost > best_g[node.state]:
                continue  # bản cũ, đã có đường tốt hơn
            if problem.is_goal(node.state):
                return node

            self.nodes_expanded += 1
            for nxt, action, cost in problem.get_successors(node.state):
                g = node.g_cost + cost
                if g >= best_g.get(nxt, float("inf")):
                    continue
                hv = h(nxt)
                if hv == float("inf"):
                    continue  # deadlock, bỏ nhánh này
                best_g[nxt] = g
                self.nodes_generated += 1
                heapq.heappush(frontier, Node(nxt, node, action, g, hv))
        return None