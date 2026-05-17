"""
N-Queens via exhaustive depth-first search (backtracking).

This is the classical recursive backtracking approach. We place one queen per
row, and prune any partial placement that already has a column or diagonal
conflict. The first complete board we find is returned.

Note: this is guaranteed to find a solution if one exists, but the search
space is huge for large N, so it is only practical up to maybe N ~ 30. For
larger N the benchmark runner will impose a wall-clock timeout.
"""

import sys
import time
import tracemalloc


def solve_dfs(n, time_limit=None):
    """Return one valid N-Queens placement as a list of column indices.

    queens[r] = c means there is a queen at row r, column c.
    If `time_limit` (seconds) is given and exceeded, returns None.
    """
    cols = set()      # columns already used
    diag1 = set()     # r - c for the / diagonal
    diag2 = set()     # r + c for the \ diagonal
    queens = [0] * n
    start = time.perf_counter()
    timed_out = [False]

    def backtrack(row):
        if timed_out[0]:
            return False
        if time_limit is not None and (time.perf_counter() - start) > time_limit:
            timed_out[0] = True
            return False
        if row == n:
            return True
        for c in range(n):
            if c in cols or (row - c) in diag1 or (row + c) in diag2:
                continue
            queens[row] = c
            cols.add(c)
            diag1.add(row - c)
            diag2.add(row + c)
            if backtrack(row + 1):
                return True
            cols.remove(c)
            diag1.remove(row - c)
            diag2.remove(row + c)
        return False

    sys.setrecursionlimit(max(1000, n * 10))
    ok = backtrack(0)
    if timed_out[0] or not ok:
        return None
    return queens


def is_valid_solution(queens):
    """Check that no two queens attack each other."""
    n = len(queens)
    if len(set(queens)) != n:
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if abs(queens[i] - queens[j]) == abs(i - j):
                return False
    return True


def run(n, time_limit=None):
    """Run DFS for the given N and return a result dict for the benchmark."""
    tracemalloc.start()
    t0 = time.perf_counter()
    solution = solve_dfs(n, time_limit=time_limit)
    elapsed = time.perf_counter() - t0
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "DFS",
        "n": n,
        "time_sec": elapsed,
        "peak_memory_kb": peak / 1024,
        "solved": solution is not None and is_valid_solution(solution),
        "solution": solution,
    }


if __name__ == "__main__":
    # Quick smoke test
    for n in (4, 8, 10):
        r = run(n, time_limit=10)
        print(f"N={n}: solved={r['solved']}  time={r['time_sec']:.4f}s  "
              f"peak={r['peak_memory_kb']:.1f} KB")
