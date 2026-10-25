"""Figure 6: freshness-window sensitivity (WP3)."""
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
SUPPLIES = [1.0, 0.7]
DS = [2, 4, 8, 16]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


rows = read_csv(OUT / "freshness_contrasts.csv")
plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": 8, "pdf.fonttype": 42, "svg.fonttype": "none",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .65})
fig, axes = plt.subplots(1, 2, figsize=(7.35, 2.85))
fig.subplots_adjust(left=.18, right=.945, top=.83, bottom=.21, wspace=.42)
labels = [f"{name} {supply}" for _, name in CELLS for supply in SUPPLIES]
for ax, metric, title in [(axes[0], "coverage", "a  Coverage difference (pp)"),
                          (axes[1], "source_p5", "b  Source P5 difference (pp)")]:
    matrix = np.array([[float(next(r for r in rows if r["condition"] == code and float(r["supply"]) == supply
                                  and int(r["D"]) == d and r["metric"] == metric)["mean_difference"])
                        for d in DS] for code, _ in CELLS for supply in SUPPLIES])
    vmax = max(4.0, float(np.ceil(matrix.max())))
    vmin = min(-1.0, float(np.floor(matrix.min())))
    norm = TwoSlopeNorm(vmin=vmin, vcenter=0.0, vmax=vmax)
    image = ax.imshow(matrix, cmap="RdBu_r", norm=norm, aspect="auto")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            ax.text(j, i, f"{value:+.1f}", ha="center", va="center", fontsize=6.2,
                    color="white" if abs(value) > 0.62 * vmax else "#20262a")
    ax.set_xticks(range(len(DS)))
    ax.set_xticklabels([f"{15 * d}" for d in DS], fontsize=6.8)
    if ax is axes[0]:
        ax.set_xlabel("Freshness criterion D (min)", fontsize=6.9, labelpad=3)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels if ax is axes[0] else [""] * len(labels), fontsize=6.6)
    ax.set_title(title, loc="left", fontsize=8.0, fontweight="bold", pad=7)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(DS), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=.9)
    ax.tick_params(which="minor", bottom=False, left=False)
fig.colorbar(image, ax=axes, fraction=.022, pad=.02).ax.tick_params(labelsize=6.2, length=2)
fig.savefig(R / "figures/fig6_freshness.pdf")
fig.savefig(R / "figures/fig6_freshness.svg")
fig.savefig(R / "figures/fig6_freshness.png", dpi=600)
plt.close(fig)
(R / "audit/fig6_freshness_data.json").write_text(json.dumps(dict(
    source="code/experiments/v6_4_agricultural_extension/results/freshness_contrasts.csv",
    source_sha256=hashlib.sha256((OUT / "freshness_contrasts.csv").read_bytes()).hexdigest(),
    thresholds_minutes=[15 * d for d in DS], cells=labels,
    comparators="Prefix-only for Synthetic/T2; PADC-AGE for T1/T3",
    note="Descriptive paired differences; packet generation, routing, energy and expiry are unchanged."),
    indent=2) + "\n", encoding="utf-8")
print("wrote fig6_freshness")
