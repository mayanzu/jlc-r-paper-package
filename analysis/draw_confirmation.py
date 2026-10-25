"""Regenerate the quantitative confirmation panels from supplied records.

Never imports a simulator. Reads the bundled 480 metrics + 32 NI rows and
writes SVG/PDF/PNG to the requested output directory, leaving distributed
assets intact.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv"
STATS = ROOT / "code/experiments/v6_3_relay_repair/D_noninferiority_seeds16.csv"


def rows(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def draw(output):
    data = rows(SOURCE)
    saved = rows(STATS)
    seeds = sorted({x["seed"] for x in data}, key=int)
    index = {(x["condition"], x["supply"], x["seed"], x["method"]): x for x in data}
    order = [(c, s) for c in ["SYNTHETIC_G20", "WINTER_G20", "T2_G20", "T3_G20"] for s in ["1.0", "0.7"]]
    names = {"SYNTHETIC_G20": "Synthetic", "WINTER_G20": "T1 winter", "T2_G20": "T2 spring", "T3_G20": "T3 winter"}
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 8,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.65,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.35))
    fig.subplots_adjust(left=0.15, right=0.985, top=0.94, bottom=0.09, wspace=0.60, hspace=0.43)
    contract = []
    metrics = [
        ("coverage_pct", "a  Fresh-source coverage", "Difference (percentage points)", False),
        ("aoi_mean_minutes", "b  Mean information age", "Difference (minutes)", True),
        ("source_coverage_p5_pct", "c  Lower-tail source coverage", "Difference (percentage points)", False),
        ("night_off_pct", "d  Nighttime outage", "Difference (percentage points)", True),
    ]
    for ax, (metric, title, xlabel, lower) in zip(axes.flat, metrics):
        ax.set_title(title, loc="left", fontsize=8.2, fontweight="bold", pad=10)
        ax.axvline(0, color="#7b858b", lw=0.75, ls="--", zorder=1)
        ax.set_yticks(range(8))
        ax.set_yticklabels([names[c] + " " + s for c, s in order], fontsize=7)
        ax.set_ylim(7.55, -0.55)
        ax.set_xlabel(xlabel, fontsize=7.5, labelpad=5)
        ax.tick_params(axis="x", labelsize=7)
        ax.tick_params(axis="y", length=0, pad=4)
        ax.grid(axis="y", color="#e9ecee", lw=0.6, zorder=0)
        for y, (c, s) in enumerate(order):
            baseline = "JLC-R-SA" if c in ["SYNTHETIC_G20", "T2_G20"] else "PADC-AGE"
            d = np.array([float(index[c, s, k, "JLC-R-HYB-V63"][metric]) - float(index[c, s, k, baseline][metric]) for k in seeds])
            x = next(x for x in saved if (x["condition"], x["supply"], x["metric"]) == (c, s, metric))
            mean, lo, hi = [float(x[k]) for k in ["mean_diff", "ci95_lo", "ci95_hi"]]
            assert abs(d.mean() - mean) < 1e-9
            ax.scatter(d, np.full(12, y) + np.linspace(-0.18, 0.18, 12), s=6, color="#9ba5ac", alpha=0.65, linewidth=0, zorder=2)
            color = "#176b78" if (mean < 0 if lower else mean > 0) else "#a0552e"
            ax.errorbar([mean], [y], xerr=[[mean - lo], [hi - mean]], fmt="D", markersize=3.8, color=color, elinewidth=1.6, markeredgecolor="white", markeredgewidth=0.45, zorder=4)
            contract.append(dict(metric=metric, condition=c, supply=s, baseline=baseline, seed_count=12, mean=mean, ci95=[lo, hi]))
        ax.margins(x=0.14)
    fig.canvas.draw()
    boxes = [ax.get_position().bounds for ax in axes.flat]
    assert max(b[2] for b in boxes) - min(b[2] for b in boxes) < 1e-8
    assert max(b[3] for b in boxes) - min(b[3] for b in boxes) < 1e-8
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / "fig3_confirmation.pdf")
    fig.savefig(output / "fig3_confirmation.svg")
    fig.savefig(output / "fig3_confirmation.png", dpi=600)
    plt.close(fig)
    (output / "figure_contract.json").write_text(
        json.dumps(
            dict(
                source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                statistics_sha256=hashlib.sha256(STATS.read_bytes()).hexdigest(),
                record_count=480,
                paired_points=384,
                contrasts=contract,
                excluded_seed_conditions=0,
                interpretation="Nominal two-sided 95% intervals depict effects. The original one-sided Holm-36 NI test determines the reported verdict; zero is not its margin.",
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Confirmation plotted: 32 contrasts, 384 paired observations -> {output}")
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=ROOT / "artifacts/confirmation")
    a = p.parse_args()
    draw(a.output.resolve())
