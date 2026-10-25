"""Figure 5: winter monitoring feasibility under supply scaling (WP2)."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

import os
PACKAGE=Path(__file__).resolve().parents[2]
R=Path(os.environ['JLCR_REPRO_OUTPUT']).resolve()
(R/'figures').mkdir(parents=True,exist_ok=True)
(R/'audit').mkdir(parents=True,exist_ok=True)
PROJECT=PACKAGE
OUT = Path(os.environ.get('JLCR_AGRICULTURAL_RESULTS',str(PROJECT / "code/experiments/v6_4_agricultural_extension/results")))
LABELS = [("WINTER_G20", "T1 winter"), ("T3_G20", "T3 winter")]
CONTROLLERS = ["JLC-R", "Prefix-only", "Hybrid control", "PADC-AGE"]
COLORS = {"JLC-R": "#176b78", "Prefix-only": "#8a949a", "Hybrid control": "#6ba3ad", "PADC-AGE": "#a0552e"}
SUPPLIES = [0.7, 1.0, 1.5, 2.0, 2.5, 3.0]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


summary = read_csv(OUT / "supply_scan_summary.csv")
thresholds = json.loads((OUT / "supply_scan_thresholds.json").read_text(encoding="utf-8"))
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .65})
fig, axes = plt.subplots(2, 4, figsize=(7.4, 4.6), sharex=True)
fig.subplots_adjust(left=.075, right=.985, top=.845, bottom=.145, wspace=.34, hspace=.22)
panels = [
    ("coverage_pct", "Coverage (%)", "a  Fresh-source coverage", False),
    ("source_coverage_p5_pct", "Source P5 (%)", "b  Lower-tail coverage", False),
    ("aoi_mean_minutes", "Mean AoI (min)", "c  Information age", False),
    ("battery_end_mean_j", "Battery at end (J)", "d  Stored energy", False),
]
for row, (code, label) in enumerate(LABELS):
    for col, (metric, ylabel, title, _) in enumerate(panels):
        ax = axes[row, col]
        for controller in CONTROLLERS:
            entries = [next(r for r in summary if r["condition"] == code and float(r["supply"]) == s
                            and r["controller"] == controller) for s in SUPPLIES]
            means = np.array([float(r[f"{metric}_mean"]) for r in entries])
            sd = np.array([float(r[f"{metric}_sd"]) for r in entries])
            ci = stats.t.ppf(0.975, 11) * sd / np.sqrt(12)
            ax.plot(SUPPLIES, means, marker="o", markersize=2.8, linewidth=1.2,
                    color=COLORS[controller], label=controller, zorder=3)
            ax.fill_between(SUPPLIES, means - ci, means + ci, color=COLORS[controller],
                            alpha=.12, linewidth=0, zorder=2)
        if metric == "coverage_pct":
            for target in (70, 80):
                ax.axhline(target, color="#b8bfc4", lw=.7, ls=(0, (3, 2)), zorder=1)
            if row == 0:
                ax.text(2.55, 71.2, "70%", fontsize=5.8, color="#6b757a", ha="right")
                ax.text(2.55, 81.2, "80%", fontsize=5.8, color="#6b757a", ha="right")
        if metric == "battery_end_mean_j":
            ax.axhline(3.0, color="#b8bfc4", lw=.7, ls=(0, (3, 2)), zorder=1)
        ax.set_title(title if row == 0 else "", loc="left", fontsize=7.6, fontweight="bold", pad=6)
        ax.set_ylabel(f"{label}\n{ylabel}" if col == 0 else ylabel, fontsize=6.6)
        ax.tick_params(labelsize=6.3)
        ax.grid(axis="y", color="#edf0f1", lw=.5, zorder=0)
        ax.set_xlim(0.55, 3.1)
        ax.set_xticks(SUPPLIES)
        ax.set_xticklabels([f"{s:.1f}" for s in SUPPLIES], fontsize=6.1, rotation=0)
        if row == 1:
            ax.set_xlabel("Supply multiplier", fontsize=6.6, labelpad=3)
handles = [plt.Line2D([], [], color=COLORS[c], marker="o", markersize=3, lw=1.2, label=c) for c in CONTROLLERS]
fig.legend(handles=handles, labels=CONTROLLERS, fontsize=6.7, ncol=4, frameon=False,
           loc="upper center", bbox_to_anchor=(.5, .965), handlelength=1.4, columnspacing=1.4)
fig.savefig(R / "figures/fig5_supply_scan.pdf")
fig.savefig(R / "figures/fig5_supply_scan.svg")
fig.savefig(R / "figures/fig5_supply_scan.png", dpi=600)
plt.close(fig)
(R / "audit/fig5_supply_scan_data.json").write_text(json.dumps(dict(
    source="code/experiments/v6_4_agricultural_extension/results/supply_scan_summary.csv",
    source_sha256=hashlib.sha256((OUT / "supply_scan_summary.csv").read_bytes()).hexdigest(),
    thresholds_sha256=hashlib.sha256((OUT / "supply_scan_thresholds.json").read_bytes()).hexdigest(),
    seed_count=12, supplies=SUPPLIES, controllers=CONTROLLERS,
    note="Bands are nominal 95% t intervals across 12 paired seeds. Supply multipliers are normalized model scalars.",
    thresholds=thresholds), indent=2) + "\n", encoding="utf-8")
print("wrote fig5_supply_scan")
