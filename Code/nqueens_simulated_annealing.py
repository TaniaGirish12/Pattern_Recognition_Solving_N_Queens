"""
N-Queens via Simulated Annealing.

State and objective are the same as in the hill-climbing file: one queen
per column, h(state) is the number of attacking pairs.

The annealing twist:
    At each step we pick a random "single queen move" neighbour. If that
    move reduces h we always accept it. If it makes things worse we accept
    it anyway with probability exp(-delta / T), where T is the current
    temperature. T starts high (so the search wanders freely and escapes
    local optima) and is cooled geometrically toward zero, at which point
    the algorithm behaves like greedy hill climbing.

Cooling schedule:
    T_k = T0 * alpha^k     with alpha in (0, 1), typically ~0.995.

We restart from a new random state if the temperature gets very cold
without finding a solution -- effectively a reheat.
"""

import math
import random
import time
import tracemalloc

from nqueens_hill_climbing import (
    _build_counters,
    _attacks_from_counters,
    _delta_for_move,
    _apply_move,
)


def solve_simulated_annealing(
    n,
    time_limit=None,
    seed=None,
    T0=None,
    alpha=0.995,
    min_T=1e-3,
    steps_per_temp=None,
):
    """Run simulated annealing with reheat restarts."""
    rng = random.Random(seed)
    start = time.perf_counter()
    if T0 is None:
        # A reasonable starting temperature: roughly the number of queens.
        T0 = max(1.0, n / 2.0)
    if steps_per_temp is None:
        steps_per_temp = max(20, n)

    best_state = None
    best_h = None
    restarts = 0
    while True:
        state = [rng.randrange(n) for _ in range(n)]
        rows, d1, d2 = _build_counters(state)
        h = _attacks_from_counters(rows, d1, d2)
        T = T0
        restarts += 1
        while T > min_T and h > 0:
            for _ in range(steps_per_temp):
                if h == 0:
                    break
                c = rng.randrange(n)
                r = rng.randrange(n)
                if r == state[c]:
                    continue
                delta = _delta_for_move(state, rows, d1, d2, c, r)
                if delta <= 0 or rng.random() < math.exp(-delta / T):
                    _apply_move(state, rows, d1, d2, c, r)
                    h += delta
            if h == 0:
                return state, restarts
            if time_limit is not None and (time.perf_counter() - start) > time_limit:
                return (best_state if best_h == 0 else None), restarts
            T *= alpha
        if h == 0:
            return state, restarts
        if best_h is None or h < best_h:
            best_h = h
            best_state = list(state)
        if time_limit is not None and (time.perf_counter() - start) > time_limit:
            return None, restarts


def is_valid_solution(state):
    if state is None:
        return False
    rows, d1, d2 = _build_counters(state)
    return _attacks_from_counters(rows, d1, d2) == 0


def run(n, time_limit=None, seed=None):
    tracemalloc.start()
    t0 = time.perf_counter()
    state, restarts = solve_simulated_annealing(
        n, time_limit=time_limit, seed=seed
    )
    elapsed = time.perf_counter() - t0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "SimulatedAnnealing",
        "n": n,
        "time_sec": elapsed,
        "peak_memory_kb": peak / 1024,
        "solved": is_valid_solution(state),
        "solution": state,
        "restarts": restarts,
    }


if __name__ == "__main__":
    for n in (8, 10, 30, 50):
        r = run(n, time_limit=30, seed=42)
        print(f"N={n}: solved={r['solved']}  time={r['time_sec']:.3f}s  "
              f"peak={r['peak_memory_kb']:.1f} KB  restarts={r['restarts']}")
