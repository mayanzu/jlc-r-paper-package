"""Figure 7: crop-canopy energy/channel coupling stress test (WP4)."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
PACKAGE=Path(__file__).resolve().parents[2]
R=Path(os.environ['JLCR_REPRO_OUTPUT']).resolve()
(R/'figures').mkdir(parents=True,exist_ok=True)
(R/'audit').mkdir(parents=True,exist_ok=True)
PROJECT=PACKAGE
OUT = Path(os.environ.get('JLCR_AGRICULTURAL_RESULTS',str(PROJECT / "code/experiments/v6_4_agricultural_extension/results")))
TREATMENTS = ["C0", "I-C1", "II-C1", "II-C2", "II-C3", "III-C1", "III-C2", "III-C3"]
CONTROLLERS = ["JLC-R", "Prefix-only", "Hybrid control", "PADC-AGE"]
COLORS = {"JLC-R": "#176b78", "Prefix-only": "#8a949a", "Hybrid control": "#6ba3ad", "PADC-AGE": "#a0552e"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


summary = read_csv(OUT / "canopy_summary.csv")
effects = read_csv(OUT / "canopy_effects.csv")
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .65})
fig, axes = plt.subplots(2, 2, figsize=(7.35, 5.0))
fig.subplots_adjust(left=.085, right=.985, top=.90, bottom=.17, wspace=.28, hspace=.52)
x = np.arange(len(TREATMENTS))
width = .19
for ax, metric, title, ylabel in [(axes[0, 0], "coverage_pct", "a  Fresh-source coverage", "Coverage (%)"),
                                  (axes[0, 1], "far_coverage_D4_pct", "b  Far-source coverage ($\\geq$200 m)", "Coverage (%)"),
                                  (axes[1, 1], "source_coverage_p5_pct", "d  Lower-tail source coverage", "Source P5 (%)")]:
    for k, controller in enumerate(CONTROLLERS):
        values = [float(next(r for r in summary if r["treatment"] == t and r["controller"] == controller)[f"{metric}_mean"])
                  for t in TREATMENTS]
        ax.bar(x + (k - 1.5) * width, values, width * .9, color=COLORS[controller], label=controller,
               edgecolor="white", linewidth=.3, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(TREATMENTS, rotation=35, ha="right", fontsize=6.2)
    ax.set_ylabel(ylabel, fontsize=6.8)
    ax.set_title(title, loc="left", fontsize=7.8, fontweight="bold", pad=7)
    ax.grid(axis="y", color="#edf0f1", lw=.5, zorder=0)
    ax.tick_params(labelsize=6.3)
    ax.margins(x=.02)
axes[0, 0].set_ylim(0, 88)
axes[0, 0].legend(fontsize=5.8, ncol=2, frameon=False, loc="upper right", handlelength=1.0,
                  columnspacing=.8, handletextpad=.35, borderaxespad=.2)
ax = axes[1, 0]
for controller in ["JLC-R", "Hybrid control"]:
    values = [next(r for r in effects if r["treatment"] == t and r["controller"] == controller
                   and r["metric"] == "coverage_pct") for t in TREATMENTS[1:]]
    means = [float(v["mean_change"]) for v in values]
    low = [float(v["ci95_low"]) for v in values]
    high = [float(v["ci95_high"]) for v in values]
    ax.errorbar(np.arange(1, len(TREATMENTS)), means,
                yerr=[np.array(means) - np.array(low), np.array(high) - np.array(means)],
                marker="o", markersize=3.2, lw=1.2, capsize=1.8, color=COLORS[controller], label=controller)
ax.axhline(0, color="#7b858b", lw=.7, ls="--")
ax.set_xticks(x)
ax.set_xticklabels(TREATMENTS, rotation=35, ha="right", fontsize=6.2)
ax.set_ylabel("Change from C0 (pp)", fontsize=6.8)
ax.set_title("c  Paired treatment effect on coverage", loc="left", fontsize=7.8, fontweight="bold", pad=7)
ax.grid(axis="y", color="#edf0f1", lw=.5, zorder=0)
ax.tick_params(labelsize=6.3)
ax.legend(fontsize=6.1, frameon=False, loc="lower left", handlelength=1.2)
ax.margins(x=.02)
fig.savefig(R / "figures/fig7_canopy.pdf")
fig.savefig(R / "figures/fig7_canopy.svg")
fig.savefig(R / "figures/fig7_canopy.png", dpi=600)
plt.close(fig)
(R / "audit/fig7_canopy_data.json").write_text(json.dumps(dict(
    source="code/experiments/v6_4_agricultural_extension/results/canopy_summary.csv",
    effects="code/experiments/v6_4_agricultural_extension/results/canopy_effects.csv",
    source_sha256=hashlib.sha256((OUT / "canopy_summary.csv").read_bytes()).hexdigest(),
    effects_sha256=hashlib.sha256((OUT / "canopy_effects.csv").read_bytes()).hexdigest(),
    seed_count=12, treatments=TREATMENTS, controllers=CONTROLLERS,
    note="Exploratory stress ranges; the same canopy field is shared by all controllers within a seed."),
    indent=2) + "\n", encoding="utf-8")
print("wrote fig7_canopy")
