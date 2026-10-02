import statistics
from common.board import Board
from sokoban_single.algorithms.a_star import AStar
from sokoban_single.algorithms.ucs import UCS
from sokoban_single.models.problem import SokobanProblem

ALGORITHMS = {"UCS": UCS, "A*": AStar}



def compare(map_path: str, repeats: int = 3, time_limit: float | None = 120) -> dict:
    """Trả về {tên thuật toán: số liệu time và space} cho một map."""
    problem = SokobanProblem(Board(map_path))
    results = {}
    for name, cls in ALGORITHMS.items():
        # Lượt đo thời gian (không tracemalloc cho khỏi bị chậm)
        times = []
        for _ in range(max(1, repeats)):
            solver = cls(time_limit=time_limit)
            path = solver.solve(problem, track_memory=False)
            times.append(solver.execution_time)
            if solver.timed_out:
                break

        # Lượt đo bộ nhớ (có tracemalloc)
        mem_solver = cls(time_limit=time_limit)
        mem_solver.solve(problem, track_memory=True)

        results[name] = {
            "cost": None if path is None else len(path),
            "timed_out": solver.timed_out,
            # Time complexity: thời gian chạy và số node đã mở rộng
            "time": statistics.mean(times),
            "expanded": solver.nodes_expanded,
            # Space complexity: bộ nhớ đỉnh, số node lớn nhất trong frontier, số node đã sinh
            "memory": mem_solver.memory_used,
            "max_frontier": solver.max_frontier,
            "generated": solver.nodes_generated,
        }
    return results


def run_benchmark(map_paths: list[str], repeats: int = 3,
                  time_limit: float | None = 120) -> dict:
    """Chạy nhiều map, trả về {map: {thuật toán: số liệu}} để dùng lại."""
    return {m: compare(m, repeats, time_limit) for m in map_paths}


def print_report(report: dict) -> None:
    for map_path, results in report.items():
        print(f"\nMap: {map_path}")
        print(f"{'Algo':<5}{'Cost':>6}{'Time(s)':>10}{'Expanded':>10}"
              f"{'Mem(MB)':>10}{'MaxFront':>10}{'Generated':>11}")
        for name, r in results.items():
            cost = "N/A" if r["cost"] is None else r["cost"]
            note = "  (QUÁ GIỜ)" if r["timed_out"] else ""
            print(f"{name:<5}{cost:>6}{r['time']:>10.3f}{r['expanded']:>10}"
                  f"{r['memory']:>10.1f}{r['max_frontier']:>10}{r['generated']:>11}{note}")

def main() -> None:
    maps = [
        "maps/example_map.txt",
    
    ]
    report = run_benchmark(maps, repeats=3, time_limit=120)   # lưu vào biến
    print_report(report)                                      # rồi mới in


if __name__ == "__main__":
    main()