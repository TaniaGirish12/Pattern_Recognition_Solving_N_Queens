"""Generate Figure 1 for the report: a three-panel illustration of the
10-Queens problem.

  Panel A: empty 10x10 board
  Panel B: 10 queens placed along the main diagonal (clearly invalid -- every
           pair attacks along the same diagonal)
  Panel C: a valid 10-queens solution

The figure is saved as figure_problem.png (suitable for embedding in the
IEEE-format report) and figure_problem.pdf (for LaTeX inclusion).
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
N = 10

# One known valid solution for 10-Queens (column -> row indices).
VALID_SOLUTION = [0, 2, 5, 7, 9, 4, 8, 1, 3, 6]
INVALID_PLACEMENT = list(range(N))  # all queens on the main diagonal


def draw_board(ax, n, queens=None, highlight_conflicts=False, title=""):
    # Checkerboard squares
    for r in range(n):
        for c in range(n):
            color = "#F0D9B5" if (r + c) % 2 == 0 else "#B58863"
            ax.add_patch(Rectangle((c, n - 1 - r), 1, 1, facecolor=color,
                                    edgecolor="#333333", linewidth=0.5))

    # Place queens
    if queens is not None:
        for col, row in enumerate(queens):
            ax.text(col + 0.5, n - 1 - row + 0.5, "♛",  # black queen glyph
                    ha="center", va="center", fontsize=22,
                    color="#111111", zorder=3)

        # For panel B (invalid), draw red lines showing diagonal attacks
        if highlight_conflicts:
            # Draw a red line along the diagonal to show the conflict.
            ax.plot([0.5, n - 0.5], [n - 0.5, 0.5], color="red",
                    linewidth=2.5, linestyle="--", alpha=0.7, zorder=2)

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, fontsize=11, pad=10)


fig, axes = plt.subplots(1, 3, figsize=(11, 4.0))

draw_board(axes[0], N, queens=None, title="(A) Empty 10 x 10 board")
draw_board(axes[1], N, queens=INVALID_PLACEMENT, highlight_conflicts=True,
           title="(B) Invalid placement\n(all queens on one diagonal)")
draw_board(axes[2], N, queens=VALID_SOLUTION,
           title="(C) Valid 10-Queens solution")

fig.suptitle("Figure 1. The 10-Queens problem: empty board, an invalid "
             "placement, and one valid solution.",
             fontsize=10, y=0.02)

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
png_path = os.path.join(HERE, "figure_problem.png")
pdf_path = os.path.join(HERE, "figure_problem.pdf")
plt.savefig(png_path, dpi=200, bbox_inches="tight")
plt.savefig(pdf_path, bbox_inches="tight")
plt.close(fig)
print("Wrote", png_path)
print("Wrote", pdf_path)
