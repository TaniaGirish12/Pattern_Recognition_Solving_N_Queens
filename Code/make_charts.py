import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "results.json")) as f:
    rows = json.load(f)

# Stable algorithm order
order = ["Exhaustive DFS", "Hill Climbing", "Simulated Annealing", "Genetic Algorithm"]
rows.sort(key=lambda r: (order.index(r["label"]), r["n"]))

# Write CSV
csv_path = os.path.join(HERE, "results.csv")
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["algorithm", "label", "n", "time_sec",
                                      "peak_memory_kb", "solved", "note"])
    w.writeheader()
    for r in rows:
        w.writerow(r)

# Write text table
txt_path = os.path.join(HERE, "results_table.txt")
headers = ["Algorithm", "N", "Time (s)", "Peak Mem (KB)", "Solved", "Note"]
lines = ["{:<22}{:>6}{:>12}{:>16}{:>10}  {}".format(*headers),
         "-" * 90]
for r in rows:
    lines.append("{:<22}{:>6}{:>12.4f}{:>16.2f}{:>10}  {}".format(
        r["label"], r["n"], r["time_sec"], r["peak_memory_kb"],
        "yes" if r["solved"] else "no", r["note"],
    ))
with open(txt_path, "w") as f:
    f.write("\n".join(lines) + "\n")

# Build charts
by_algo = {}
for r in rows:
    by_algo.setdefault(r["label"], []).append(r)
N_VALUES = sorted({r["n"] for r in rows})
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

pdf_path = os.path.join(HERE, "charts.pdf")
with PdfPages(pdf_path) as pdf:
    # Page 1: Time vs N
    fig, ax = plt.subplots(figsize=(9, 6))
    for label in order:
        recs = by_algo.get(label, [])
        solved = [(r["n"], r["time_sec"]) for r in recs if r["solved"]]
        dnf = [(r["n"], r["time_sec"]) for r in recs if not r["solved"]]
        if solved:
            xs, ys = zip(*solved)
            ax.plot(xs, ys, marker=markers[label], color=colors[label],
                    label=label, linewidth=2, markersize=8)
        for n, t in dnf:
            ax.plot(n, t, marker="x", color=colors[label], markersize=11, mew=2.5)
    ax.set_xlabel("N (board size)")
    ax.set_ylabel("Wall-clock time (seconds)")
    ax.set_yscale("log")
    ax.set_title("N-Queens: solving time vs. N (log scale,  X = did not finish)")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(loc="best")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # Page 2: Memory vs N
    fig, ax = plt.subplots(figsize=(9, 6))
    for label in order:
        recs = by_algo.get(label, [])
        recs = sorted(recs, key=lambda r: r["n"])
        xs = [r["n"] for r in recs]
        ys = [r["peak_memory_kb"] for r in recs]
        ax.plot(xs, ys, marker=markers[label], color=colors[label],
                label=label, linewidth=2, markersize=8)
    ax.set_xlabel("N (board size)")
    ax.set_ylabel("Peak traced memory (KB)")
    ax.set_yscale("log")
    ax.set_title("N-Queens: peak memory vs. N (log scale)")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(loc="best")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # Page 3: solved/not-solved bar chart
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bar_w = 0.2
    for i, label in enumerate(order):
        recs = {r["n"]: r for r in by_algo.get(label, [])}
        heights = [1 if recs.get(n, {}).get("solved") else 0 for n in N_VALUES]
        xs = [j + (i - 1.5) * bar_w for j in range(len(N_VALUES))]
        ax.bar(xs, heights, width=bar_w, color=colors[label], label=label)
    ax.set_xticks(range(len(N_VALUES)))
    ax.set_xticklabels([str(n) for n in N_VALUES])
    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Solved? (1 = yes, 0 = no)")
    ax.set_title("Which (algorithm, N) cells produced a valid solution")
    ax.set_xlabel("N (board size)")
    ax.legend(loc="upper right")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # Page 4: grouped time bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, label in enumerate(order):
        recs = {r["n"]: r for r in by_algo.get(label, [])}
        times = [recs.get(n, {}).get("time_sec", 0) for n in N_VALUES]
        xs = [j + (i - 1.5) * bar_w for j in range(len(N_VALUES))]
        ax.bar(xs, times, width=bar_w, color=colors[label], label=label)
    ax.set_xticks(range(len(N_VALUES)))
    ax.set_xticklabels([str(n) for n in N_VALUES])
    ax.set_ylabel("Wall-clock time (seconds)")
    ax.set_yscale("symlog", linthresh=0.01)
    ax.set_xlabel("N (board size)")
    ax.set_title("N-Queens: time per algorithm and N (symlog scale)")
    ax.legend(loc="best")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

print(f"Wrote {csv_path}")
print(f"Wrote {txt_path}")
print(f"Wrote {pdf_path}")
