"""
Benchmark runner for all four N-Queens algorithms.

For each (algorithm, N) we:
  - Run the algorithm with a per-cell wall-clock time limit.
  - Record elapsed time and peak memory.
  - Verify the returned board is a real, conflict-free solution.

Outputs:
  - results.csv         (one row per (algorithm, N))
  - charts.pdf          (multi-page PDF with time, memory, success charts)
  - results_table.txt   (plain-text table that mirrors the CSV)
"""

import csv
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import nqueens_dfs
import nqueens_hill_climbing
import nqueens_simulated_annealing
import nqueens_genetic


HERE = os.path.dirname(os.path.abspath(__file__))

# Per-(algorithm, N) time budgets in seconds. DFS gets a small cap because
# the search space explodes past about N=30; the others get progressively
# more budget for larger boards.
TIME_LIMITS = {
    "DFS":               {10:  2,  30:   5,  50:  10,  100:  10, 200:  10, 500:  10},
    "HillClimbing":      {10:  5,  30:  10,  50:  15,  100:  30, 200:  60, 500:  90},
    "SimulatedAnnealing":{10:  5,  30:  10,  50:  20,  100:  40, 200:  60, 500: 120},
    "Genetic":           {10: 10,  30:  20,  50:  40,  100:  80, 200: 120, 500: 180},
}

N_VALUES = [10, 30, 50, 100, 200, 500]
ALGOS = [
    ("DFS",                "Exhaustive DFS",        nqueens_dfs.run),
    ("HillClimbing",       "Hill Climbing",         nqueens_hill_climbing.run),
    ("SimulatedAnnealing", "Simulated Annealing",   nqueens_simulated_annealing.run),
    ("Genetic",            "Genetic Algorithm",     nqueens_genetic.run),
]

SEED = 20251116  # one fixed seed so the run is reproducible


def run_all():
    rows = []
    for key, label, runner in ALGOS:
        for n in N_VALUES:
            limit = TIME_LIMITS[key][n]
            print(f"--- {label}  N={n}  (limit {limit}s) ---", flush=True)
            t0 = time.perf_counter()
            try:
                if key == "DFS":
                    result = runner(n, time_limit=limit)
                else:
                    result = runner(n, time_limit=limit, seed=SEED)
            except Exception as exc:
                wall = time.perf_counter() - t0
                print(f"    ERROR after {wall:.1f}s: {exc}", flush=True)
                rows.append({
                    "algorithm": key,
                    "label": label,
                    "n": n,
                    "time_sec": wall,
                    "peak_memory_kb": 0.0,
                    "solved": False,
                    "note": f"error: {exc}",
                })
                continue
            wall = result["time_sec"]
            solved = result["solved"]
            peak_kb = result["peak_memory_kb"]
            note = "" if solved else f"DNF within {limit}s"
            print(
                f"    solved={solved}  time={wall:.3f}s  peak={peak_kb:.1f} KB",
                flush=True,
            )
            rows.append({
                "algorithm": key,
                "label": label,
                "n": n,
                "time_sec": wall,
                "peak_memory_kb": peak_kb,
                "solved": solved,
                "note": note,
            })
    return rows


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["algorithm", "label", "n", "time_sec",
                        "peak_memory_kb", "solved", "note"],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_text_table(rows, path):
    headers = ["Algorithm", "N", "Time (s)", "Peak Mem (KB)", "Solved", "Note"]
    lines = ["{:<22}{:>6}{:>12}{:>16}{:>10}  {}".format(*headers)]
    lines.append("-" * 90)
    for r in rows:
        lines.append("{:<22}{:>6}{:>12.4f}{:>16.2f}{:>10}  {}".format(
            r["label"],
            r["n"],
            r["time_sec"],
            r["peak_memory_kb"],
            "yes" if r["solved"] else "no",
            r["note"],
        ))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def plot_results(rows, pdf_path):
    by_algo = {}
    for r in rows:
        by_algo.setdefault(r["label"], []).append(r)
    for algo in by_algo:
        by_algo[algo].sort(key=lambda x: x["n"])

    colors = {
        "Exhaustive DFS": "#d62728",
        "Hill Climbing": "#1f77b4",
        "Simulated Annealing": "#2ca02c",
        "Genetic Algorithm": "#9467bd",
    }
    markers = {
        "Exhaustive DFS": "o",
        "Hill Climbing": "s",
        "Simulated Annealing": "^",
        "Genetic Algorithm": "D",
    }

    with PdfPages(pdf_path) as pdf:
        # Time vs N (log scale on y because the ranges differ a lot)
        fig, ax = plt.subplots(figsize=(9, 6))
        for label, recs in by_algo.items():
            xs = [r["n"] for r in recs if r["solved"]]
            ys = [r["time_sec"] for r in recs if r["solved"]]
            ax.plot(xs, ys, marker=markers[label], color=colors[label],
                    label=label, linewidth=2, markersize=7)
            # Mark DNF runs with an open marker at the time-limit
            for r in recs:
                if not r["solved"]:
                    ax.plot(r["n"], r["time_sec"], marker="x",
                            color=colors[label], markersize=10, mew=2)
        ax.set_xlabel("N (board size)")
        ax.set_ylabel("Wall-clock time (seconds)")
        ax.set_yscale("log")
        ax.set_title("N-Queens: solving time vs. N  (log scale, x = DNF)")
        ax.grid(True, which="both", linestyle=":", alpha=0.6)
        ax.legend()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # Memory vs N
        fig, ax = plt.subplots(figsize=(9, 6))
        for label, recs in by_algo.items():
            xs = [r["n"] for r in recs]
            ys = [r["peak_memory_kb"] for r in recs]
            ax.plot(xs, ys, marker=markers[label], color=colors[label],
                    label=label, linewidth=2, markersize=7)
        ax.set_xlabel("N (board size)")
        ax.set_ylabel("Peak traced memory (KB)")
        ax.set_yscale("log")
        ax.set_title("N-Queens: peak memory vs. N  (log scale)")
        ax.grid(True, which="both", linestyle=":", alpha=0.6)
        ax.legend()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # Success rate / which sizes finished
        fig, ax = plt.subplots(figsize=(9, 6))
        algos = list(by_algo.keys())
        ns = N_VALUES
        bar_w = 0.2
        for i, algo in enumerate(algos):
            recs = {r["n"]: r for r in by_algo[algo]}
            heights = [1 if recs.get(n, {}).get("solved") else 0 for n in ns]
            xs = [j + (i - 1.5) * bar_w for j in range(len(ns))]
            ax.bar(xs, heights, width=bar_w, color=colors[algo], label=algo)
        ax.set_xticks(range(len(ns)))
        ax.set_xticklabels([str(n) for n in ns])
        ax.set_ylim(0, 1.2)
        ax.set_ylabel("Solved (1 = yes, 0 = DNF)")
        ax.set_title("N-Queens: which (algorithm, N) cells reached a valid solution")
        ax.legend(loc="upper right")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # Bar chart of time per N grouped by algorithm
        fig, ax = plt.subplots(figsize=(10, 6))
        x_idx = list(range(len(ns)))
        for i, algo in enumerate(algos):
            recs = {r["n"]: r for r in by_algo[algo]}
            times = [recs.get(n, {}).get("time_sec", 0) for n in ns]
            xs = [j + (i - 1.5) * bar_w for j in x_idx]
            ax.bar(xs, times, width=bar_w, color=colors[algo], label=algo)
        ax.set_xticks(x_idx)
        ax.set_xticklabels([str(n) for n in ns])
        ax.set_ylabel("Wall-clock time (seconds)")
        ax.set_yscale("symlog", linthresh=0.01)
        ax.set_xlabel("N (board size)")
        ax.set_title("N-Queens: time per algorithm and N (symlog scale)")
        ax.legend()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


def main():
    rows = run_all()
    csv_path = os.path.join(HERE, "results.csv")
    pdf_path = os.path.join(HERE, "charts.pdf")
    txt_path = os.path.join(HERE, "results_table.txt")
    write_csv(rows, csv_path)
    write_text_table(rows, txt_path)
    plot_results(rows, pdf_path)
    print(f"\nWrote {csv_path}\nWrote {txt_path}\nWrote {pdf_path}")


if __name__ == "__main__":
    main()
