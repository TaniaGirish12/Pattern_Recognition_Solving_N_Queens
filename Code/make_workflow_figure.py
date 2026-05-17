"""Generate Figure 2 for the report: a flow diagram of the benchmarking
methodology pipeline.

Stages: Initialization -> Per-cell loop -> Algorithm execution
        -> Verification -> Aggregation -> Visualization
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))

fig, ax = plt.subplots(figsize=(12, 4.3))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.3)
ax.set_aspect("equal")
ax.axis("off")

stages = [
    ("Initialization", "Read algorithm\nlist, N values,\ntime budgets, seed", "#1F4E79"),
    ("Per-cell\nExperiment Loop", "Select (algorithm, N)\npass time budget", "#2E74B5"),
    ("Algorithm\nExecution", "Run chosen method\nstart perf_counter\nand tracemalloc", "#5B9BD5"),
    ("Verification", "Independent\nattack-count\nrecomputation", "#70AD47"),
    ("Data\nAggregation", "Append to\nresults.json,\nwrite CSV + text", "#E2A53A"),
    ("Visualization", "Plot time, memory,\nsolved status\nas charts.pdf", "#C0504D"),
]

# Compute box positions evenly across the figure
n = len(stages)
total_width = 11.6
left_margin = 0.2
gap = (total_width - n * 1.6) / (n - 1) if n > 1 else 0
box_width = 1.6
box_height = 2.6
y_top = 3.5
y_bottom = y_top - box_height

centres = []
x = left_margin
for i in range(n):
    centres.append(x + box_width / 2)
    x += box_width + gap

for i, ((title, subtitle, color), cx) in enumerate(zip(stages, centres)):
    # Header bar
    header_h = 0.55
    ax.add_patch(FancyBboxPatch((cx - box_width / 2, y_top - header_h),
                                 box_width, header_h,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor=color, edgecolor=color,
                                 linewidth=1.5, zorder=2))
    # Body
    ax.add_patch(FancyBboxPatch((cx - box_width / 2, y_bottom),
                                 box_width, box_height - header_h,
                                 boxstyle="round,pad=0.02,rounding_size=0.08",
                                 facecolor="#FFFFFF", edgecolor=color,
                                 linewidth=1.5, zorder=2))
    ax.text(cx, y_top - header_h / 2, title, ha="center", va="center",
            color="white", fontsize=10, fontweight="bold", zorder=3)
    ax.text(cx, y_bottom + (box_height - header_h) / 2 - 0.05,
            subtitle, ha="center", va="center", fontsize=8.5,
            color="#222222", zorder=3)

# Arrows between boxes
for i in range(n - 1):
    a = FancyArrowPatch((centres[i] + box_width / 2 + 0.02,
                          y_top - box_height / 2),
                         (centres[i + 1] - box_width / 2 - 0.02,
                          y_top - box_height / 2),
                         arrowstyle="-|>", mutation_scale=18,
                         color="#444444", linewidth=1.6, zorder=1)
    ax.add_patch(a)

# Feedback loop arrow (from last back to second, indicating the loop)
loop = FancyArrowPatch((centres[-2], y_bottom - 0.05),
                       (centres[1], y_bottom - 0.05),
                       connectionstyle="arc3,rad=0.35",
                       arrowstyle="-|>", mutation_scale=15,
                       color="#888888", linewidth=1.2,
                       linestyle="dashed", zorder=1)
ax.add_patch(loop)
ax.text((centres[1] + centres[-2]) / 2, y_bottom - 0.95,
        "loop over remaining (algorithm, N) cells",
        ha="center", va="center", fontsize=8.5, style="italic",
        color="#666666")

ax.text(6.0, 0.1,
        "Figure 2. Pipeline of the benchmarking methodology used in this study.",
        ha="center", va="center", fontsize=10)

png_path = os.path.join(HERE, "figure_workflow.png")
pdf_path = os.path.join(HERE, "figure_workflow.pdf")
plt.savefig(png_path, dpi=200, bbox_inches="tight")
plt.savefig(pdf_path, bbox_inches="tight")
plt.close(fig)
print("Wrote", png_path)
print("Wrote", pdf_path)
