# N-Queens: Exhaustive, Greedy, Simulated Annealing, and Genetic Algorithm

Four approaches to the classic N-Queens problem, with a benchmark harness that
times them on N = 10, 30, 50, 100, 200, 500.

## Files

| File                             | What it is                                                       |
|----------------------------------|------------------------------------------------------------------|
| `nqueens_dfs.py`                 | Exhaustive depth-first backtracking                              |
| `nqueens_hill_climbing.py`       | Steepest-ascent hill climbing with random restarts               |
| `nqueens_simulated_annealing.py` | Simulated annealing with geometric cooling                       |
| `nqueens_genetic.py`             | Genetic algorithm with permutation encoding + order crossover    |
| `run_one.py`                     | Run a single `(algorithm, N)` benchmark cell, append to `results.json` |
| `run_benchmarks.py`              | Run the full grid in one shot (uses the same time-limit table)   |
| `make_charts.py`                 | Render `charts.pdf`, `results.csv`, `results_table.txt` from `results.json` |
| `results.json`                   | Raw benchmark data                                                |
| `results.csv` / `results_table.txt` | Human-readable summaries                                       |
| `charts.pdf`                     | Time / memory / success-rate plots (one figure per page)         |

## Running things

You only need Python 3 and `matplotlib`.

```bash
pip install matplotlib

# Run every (algorithm, N) cell at once:
python3 run_benchmarks.py

# Or run a single cell (algo, N, time-limit-in-seconds):
python3 run_one.py SimulatedAnnealing 200 30

# Rebuild the charts and tables from whatever is in results.json:
python3 make_charts.py
```

Each individual algorithm file also runs a quick self-test when invoked
directly:

```bash
python3 nqueens_dfs.py
python3 nqueens_hill_climbing.py
python3 nqueens_simulated_annealing.py
python3 nqueens_genetic.py
```

## Notes on the design

* All four algorithms use the same one-queen-per-column representation
  (`state[c] = r` means a queen at row `r`, column `c`), except the GA which
  uses a permutation of `[0, N-1]` so the genetic operators don't have to
  worry about row collisions either.
* The objective function is the number of attacking pairs of queens. A
  solution has zero attacks.
* Hill climbing and simulated annealing share the incremental delta
  computation in `nqueens_hill_climbing.py` so a single neighbour evaluation
  is O(1).
* The DFS time limit is checked at every recursive call; the other
  algorithms check their wall-clock budget between iterations so they all
  honour the per-cell timeout in `run_benchmarks.py`.
