"""
Run a single (algorithm, N) benchmark cell and append the result to
results.json. This is what the benchmark driver uses to fit each cell
inside its wall-clock budget.

Usage:
    python3 run_one.py <algo> <n> <time_limit_seconds>
    algo in {DFS, HillClimbing, SimulatedAnnealing, Genetic}
"""

import json
import os
import sys

import nqueens_dfs
import nqueens_hill_climbing
import nqueens_simulated_annealing
import nqueens_genetic


HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(HERE, "results.json")
SEED = 20251116

RUNNERS = {
    "DFS":                ("Exhaustive DFS",      nqueens_dfs.run),
    "HillClimbing":       ("Hill Climbing",       nqueens_hill_climbing.run),
    "SimulatedAnnealing": ("Simulated Annealing", nqueens_simulated_annealing.run),
    "Genetic":            ("Genetic Algorithm",   nqueens_genetic.run),
}


def append_result(row):
    rows = []
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            try:
                rows = json.load(f)
            except Exception:
                rows = []
    # If a row for this (algo, n) already exists, overwrite it.
    rows = [r for r in rows if not (r["algorithm"] == row["algorithm"]
                                    and r["n"] == row["n"])]
    rows.append(row)
    with open(RESULTS_PATH, "w") as f:
        json.dump(rows, f, indent=2)


def main():
    algo = sys.argv[1]
    n = int(sys.argv[2])
    time_limit = float(sys.argv[3])
    label, runner = RUNNERS[algo]
    print(f"--- {label} N={n} (limit {time_limit}s) ---", flush=True)
    if algo == "DFS":
        result = runner(n, time_limit=time_limit)
    else:
        result = runner(n, time_limit=time_limit, seed=SEED)
    note = "" if result["solved"] else f"DNF within {time_limit}s"
    row = {
        "algorithm": algo,
        "label": label,
        "n": n,
        "time_sec": result["time_sec"],
        "peak_memory_kb": result["peak_memory_kb"],
        "solved": result["solved"],
        "note": note,
    }
    append_result(row)
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
