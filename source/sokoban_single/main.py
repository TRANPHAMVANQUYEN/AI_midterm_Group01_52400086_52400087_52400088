import sys

from common.board import Board
from sokoban_single.algorithms.a_star import AStar
from sokoban_single.algorithms.ucs import UCS
from sokoban_single.models.problem import SokobanProblem

DEFAULT_MAP = "maps/example_map.txt"
ALGORITHMS = {"astar": ("A*", AStar), "ucs": ("UCS", UCS)}


def main():
    map_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MAP
    chosen = sys.argv[2:] or list(ALGORITHMS)   # vd: python -m sokoban_single.main map.txt astar

    problem = SokobanProblem(Board(map_path))
    print("Map:", map_path)

    costs = {}
    for key in chosen:
        name, cls = ALGORITHMS[key]
        solver = cls()
        path = solver.solve(problem)
        costs[name] = None if path is None else len(path)

        print()
        print(f"=== {name} ===")
        if path is None:
            print("Không có lời giải")
        else:
            print("Actions:", ", ".join(solver.path_to_strings(path)))
            print("Total cost:", len(path))
        print("Expanded:", solver.nodes_expanded)
        print("Generated:", solver.nodes_generated)
        print("Max frontier:", solver.max_frontier)
        print(f"Time: {solver.execution_time:.3f} s")
        print(f"Memory: {solver.memory_used:.1f} MB")

    if len(set(costs.values())) > 1:
        print("\nCẢNH BÁO: cost các thuật toán khác nhau, kiểm tra heuristic hoặc bug!")


if __name__ == "__main__":
    main()