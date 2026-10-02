import heapq

from sokoban_single.algorithms.base_search import BaseSearch, Node


class UCS(BaseSearch):
    def _search(self, problem):
        root = Node(problem.initial_state)
        frontier = [root]
        best_g = {root.state: 0}

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
                if g < best_g.get(nxt, float("inf")):
                    best_g[nxt] = g
                    self.nodes_generated += 1
                    heapq.heappush(frontier, Node(nxt, node, action, g))
        return None