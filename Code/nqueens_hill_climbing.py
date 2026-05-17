import random
import time
import tracemalloc


def _build_counters(state):
    n = len(state)
    rows = [0] * n
    d1 = [0] * (2 * n - 1)   # r - c + (n - 1)
    d2 = [0] * (2 * n - 1)   # r + c
    for c, r in enumerate(state):
        rows[r] += 1
        d1[r - c + (n - 1)] += 1
        d2[r + c] += 1
    return rows, d1, d2


def _attacks_from_counters(rows, d1, d2):
    a = 0
    for k in rows:
        if k > 1:
            a += k * (k - 1) // 2
    for k in d1:
        if k > 1:
            a += k * (k - 1) // 2
    for k in d2:
        if k > 1:
            a += k * (k - 1) // 2
    return a


def _delta_for_move(state, rows, d1, d2, c, new_r):
    n = len(state)
    old_r = state[c]
    if old_r == new_r:
        return 0
    # Removing the queen at (old_r, c)
    delta = 0
    # row decrement
    delta -= rows[old_r] - 1
    # diag1 decrement
    delta -= d1[old_r - c + (n - 1)] - 1
    # diag2 decrement
    delta -= d2[old_r + c] - 1
    # Adding queen at (new_r, c)
    delta += rows[new_r]
    delta += d1[new_r - c + (n - 1)]
    delta += d2[new_r + c]
    return delta


def _apply_move(state, rows, d1, d2, c, new_r):
    n = len(state)
    old_r = state[c]
    rows[old_r] -= 1
    d1[old_r - c + (n - 1)] -= 1
    d2[old_r + c] -= 1
    state[c] = new_r
    rows[new_r] += 1
    d1[new_r - c + (n - 1)] += 1
    d2[new_r + c] += 1


def hill_climb_once(n, rng, max_sideways=0, max_steps=None, deadline=None):
    state = [rng.randrange(n) for _ in range(n)]
    rows, d1, d2 = _build_counters(state)
    h = _attacks_from_counters(rows, d1, d2)
    steps = 0
    sideways = 0
    limit = max_steps if max_steps is not None else 200 * n
    while steps < limit and h > 0:
        best_delta = 0
        best_moves = []
        for c in range(n):
            old_r = state[c]
            for r in range(n):
                if r == old_r:
                    continue
                d = _delta_for_move(state, rows, d1, d2, c, r)
                if d < best_delta:
                    best_delta = d
                    best_moves = [(c, r)]
                elif d == best_delta and d <= 0:
                    best_moves.append((c, r))
            if deadline is not None and time.perf_counter() > deadline:
                return state, h, steps
        if best_delta < 0:
            sideways = 0
        elif best_delta == 0 and sideways < max_sideways and best_moves:
            sideways += 1
        else:
            break
        c, r = rng.choice(best_moves)
        _apply_move(state, rows, d1, d2, c, r)
        h += best_delta
        steps += 1
    return state, h, steps


def solve_hill_climbing(n, time_limit=None, seed=None, max_sideways=0):
    rng = random.Random(seed)
    start = time.perf_counter()
    deadline = (start + time_limit) if time_limit is not None else None
    restarts = 0
    total_steps = 0
    best_state = None
    best_h = None
    while True:
        state, h, steps = hill_climb_once(
            n, rng, max_sideways=max_sideways, deadline=deadline
        )
        total_steps += steps
        restarts += 1
        if h == 0:
            return state, restarts, total_steps
        if best_h is None or h < best_h:
            best_h = h
            best_state = state
        if deadline is not None and time.perf_counter() > deadline:
            return None, restarts, total_steps


def is_valid_solution(state):
    if state is None:
        return False
    rows, d1, d2 = _build_counters(state)
    return _attacks_from_counters(rows, d1, d2) == 0


def run(n, time_limit=None, seed=None, max_sideways=10):
    tracemalloc.start()
    t0 = time.perf_counter()
    state, restarts, steps = solve_hill_climbing(
        n, time_limit=time_limit, seed=seed, max_sideways=max_sideways
    )
    elapsed = time.perf_counter() - t0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "algorithm": "HillClimbing",
        "n": n,
        "time_sec": elapsed,
        "peak_memory_kb": peak / 1024,
        "solved": is_valid_solution(state),
        "solution": state,
        "restarts": restarts,
        "steps": steps,
    }


if __name__ == "__main__":
    for n in (8, 10, 30, 50):
        r = run(n, time_limit=30, seed=42)
        print(f"N={n}: solved={r['solved']}  time={r['time_sec']:.3f}s  "
              f"peak={r['peak_memory_kb']:.1f} KB  restarts={r['restarts']}")
