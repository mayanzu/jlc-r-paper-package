"""Figure 4: cross-regime synthesis of the retained 480-run confirmation.

Reads only computed CSV outputs from the extension analysis. No simulator.
"""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

import os
PACKAGE=Path(__file__).resolve().parents[2]
R=Path(os.environ['JLCR_REPRO_OUTPUT']).resolve()
(R/'figures').mkdir(parents=True,exist_ok=True)
(R/'audit').mkdir(parents=True,exist_ok=True)
PROJECT=PACKAGE
OUT = Path(os.environ.get('JLCR_AGRICULTURAL_RESULTS',str(PROJECT / "code/experiments/v6_4_agricultural_extension/results")))
CELLS = [("SYNTHETIC_G20", "Synthetic"), ("WINTER_G20", "T1 winter"),
         ("T2_G20", "T2 spring"), ("T3_G20", "T3 winter")]
SUPPLIES = ["1.0", "0.7"]
CONTROLLERS = ["JLC-R", "Prefix-only", "Hybrid control", "PADC-AGE", "PADC+relay"]
COLORS = {"JLC-R": "#176b78", "Prefix-only": "#8a949a", "Hybrid control": "#6ba3ad",
          "PADC-AGE": "#a0552e", "PADC+relay": "#cf9b7c"}
COMPARATORS = ["Prefix-only", "Hybrid control", "PADC-AGE", "PADC+relay"]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


absolute = rows(OUT / "cross_regime_absolute.csv")
paired = rows(OUT / "cross_regime_comparison.csv")
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .65})
fig = plt.figure(figsize=(7.4, 5.5))
grid = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=.40, left=.085, right=.975, top=.845, bottom=.20)
ax = fig.add_subplot(grid[0, 0])
labels = [f"{name} {supply}" for code, name in CELLS for supply in SUPPLIES]
x = np.arange(len(labels))
width = .16
handles = []
for k, controller in enumerate(CONTROLLERS):
    values, errors = [], []
    for code, _ in CELLS:
        for supply in SUPPLIES:
            entry = next(r for r in absolute if r["condition"] == code
                         and r["supply"] == supply and r["controller"] == controller)
            values.append(float(entry["coverage_pct_mean"]))
            errors.append(1.96 * float(entry["coverage_pct_sd"]) / np.sqrt(12))
    bars = ax.bar(x + (k - 2) * width, values, width * .92, label=controller, color=COLORS[controller],
                  edgecolor="white", linewidth=.3, zorder=3,
                  yerr=errors, error_kw=dict(ecolor="#4d565b", elinewidth=.5, capsize=1.0, capthick=.5))
    handles.append(bars)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=55, ha="right", fontsize=6.6)
ax.set_ylabel("Fresh-source coverage (%)", fontsize=7.5)
ax.set_title("a  Absolute service across eight cells", loc="left",
             fontsize=8.2, fontweight="bold", pad=8)
ax.grid(axis="y", color="#e9ecee", lw=.6, zorder=0)
ax.tick_params(axis="y", labelsize=7)
ax.margins(x=.012)
fig.legend(handles, CONTROLLERS, fontsize=6.6, ncol=5, frameon=False, loc="upper center",
           bbox_to_anchor=(.5, .965), handlelength=1.1, columnspacing=1.1, handletextpad=.4)

ax2 = fig.add_subplot(grid[0, 1])
matrix = np.array([[float(next(r for r in paired if r["condition"] == code and r["supply"] == supply
                               and r["comparator"] == comparator and r["metric"] == "coverage_pct")["mean_difference"])
                    for comparator in COMPARATORS] for code, _ in CELLS for supply in SUPPLIES])
norm = TwoSlopeNorm(vmin=min(-1.0, matrix.min()), vcenter=0.0, vmax=max(5.5, matrix.max()))
image = ax2.imshow(matrix, cmap="RdBu_r", norm=norm, aspect="auto")
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        value = matrix[i, j]
        ax2.text(j, i, f"{value:+.2f}", ha="center", va="center", fontsize=6.4,
                 color="white" if abs(value) > 2.6 else "#20262a")
ax2.set_xticks(range(len(COMPARATORS)))
ax2.set_xticklabels(["Prefix\n-only", "Hybrid\ncontrol", "PADC\n-AGE", "PADC\n+relay"], fontsize=6.3)
ax2.set_yticks(range(len(labels)))
ax2.set_yticklabels(labels, fontsize=6.4)
ax2.set_title("b  JLC-R minus comparator", loc="left",
              fontsize=8.2, fontweight="bold", pad=8)
ax2.tick_params(length=0)
for spine in ax2.spines.values():
    spine.set_visible(False)
cbar = fig.colorbar(image, ax=ax2, fraction=.042, pad=.03)
cbar.ax.tick_params(labelsize=6.2, length=2)
cbar.set_label("pp", fontsize=6.5, labelpad=2)
ax2.set_xticks(np.arange(-.5, len(COMPARATORS), 1), minor=True)
ax2.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
ax2.grid(which="minor", color="white", linewidth=.8)
ax2.tick_params(which="minor", bottom=False, left=False)

fig.savefig(R / "figures/fig4_cross_regime.pdf")
fig.savefig(R / "figures/fig4_cross_regime.svg")
fig.savefig(R / "figures/fig4_cross_regime.png", dpi=600)
plt.close(fig)
(R / "audit/fig4_cross_regime_data.json").write_text(json.dumps(dict(
    source="code/experiments/v6_4_agricultural_extension/results/cross_regime_absolute.csv",
    paired="code/experiments/v6_4_agricultural_extension/results/cross_regime_comparison.csv",
    absolute_sha256=hashlib.sha256((OUT / "cross_regime_absolute.csv").read_bytes()).hexdigest(),
    paired_sha256=hashlib.sha256((OUT / "cross_regime_comparison.csv").read_bytes()).hexdigest(),
    cells=labels, controllers=CONTROLLERS, comparators=COMPARATORS,
    interpretation="Panel b shows descriptive paired coverage differences; the formal decisions remain the Holm-36 noninferiority family.",
    coverage_matrix=matrix.tolist()), indent=2) + "\n", encoding="utf-8")
print("wrote fig4_cross_regime")
