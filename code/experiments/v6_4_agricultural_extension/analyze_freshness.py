"""WP3: freshness-threshold sensitivity on the retained confirmation trajectories."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
OUT = HERE / "results"
SOURCE = OUT / "freshness.csv"
PUBLISHED = PROJECT / "code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv"
CELLS = [("SYNTHETIC_G20", "Synthetic"), ("WINTER_G20", "T1 winter"),
         ("T2_G20", "T2 spring"), ("T3_G20", "T3 winter")]
SUPPLIES = [1.0, 0.7]
METHODS = {"JLC-R": "JLC-R-HYB-V63", "Prefix-only": "JLC-R-SA", "Hybrid control": "JLC-R-HYB",
           "PADC-AGE": "PADC-AGE", "PADC+relay": "PADC-AGE+V63"}
DS = [2, 4, 8, 16]
SEEDS = list(range(160101, 161213, 101))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def ci(values):
    values = np.asarray(values, dtype=float)
    half = float(stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return float(values.mean()), float(values.mean() - half), float(values.mean() + half)


def main():
    rows = read_csv(SOURCE)
    assert len(rows) == 480, len(rows)
    index = {(r["condition"], float(r["supply"]), int(r["seed"]), METHODS[r["method"]]): r for r in rows}
    published = {(r["condition"], float(r["supply"]), int(r["seed"]), r["method"]): r
                 for r in read_csv(PUBLISHED)}
    assert set(index) == set(published)
    worst_d4, worst_p5 = 0.0, 0.0
    for key, row in index.items():
        worst_d4 = max(worst_d4, abs(float(row["coverage_D4_pct"]) - float(published[key]["coverage_pct"])))
        worst_p5 = max(worst_p5, abs(float(row["source_p5_D4_pct"]) - float(published[key]["source_coverage_p5_pct"])))
    assert worst_d4 < 1e-9 and worst_p5 < 1e-9, (worst_d4, worst_p5)

    summary, contrasts = [], []
    for code, label in CELLS:
        for supply in SUPPLIES:
            for name in METHODS:
                subset = [index[(code, supply, seed, METHODS[name])] for seed in SEEDS]
                for d in DS:
                    summary.append({
                        "condition": code, "condition_label": label, "supply": supply, "controller": name,
                        "D": d, "threshold_minutes": 15 * d,
                        "coverage_mean": float(np.mean([float(r[f"coverage_D{d}_pct"]) for r in subset])),
                        "coverage_sd": float(np.std([float(r[f"coverage_D{d}_pct"]) for r in subset], ddof=1)),
                        "source_p5_mean": float(np.mean([float(r[f"source_p5_D{d}_pct"]) for r in subset])),
                        "source_p5_sd": float(np.std([float(r[f"source_p5_D{d}_pct"]) for r in subset], ddof=1)),
                    })
            matched = "Prefix-only" if code in ["SYNTHETIC_G20", "T2_G20"] else "PADC-AGE"
            for d in DS:
                for metric, field in [("coverage", f"coverage_D{d}_pct"), ("source_p5", f"source_p5_D{d}_pct")]:
                    difference = np.array([float(index[(code, supply, seed, "JLC-R-HYB-V63")][field]) -
                                           float(index[(code, supply, seed, METHODS[matched])][field]) for seed in SEEDS])
                    mean, low, high = ci(difference)
                    contrasts.append({"condition": code, "condition_label": label, "supply": supply,
                                      "comparator": matched, "metric": metric, "D": d,
                                      "threshold_minutes": 15 * d, "mean_difference": mean,
                                      "ci95_low": low, "ci95_high": high})
    with (OUT / "freshness_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    with (OUT / "freshness_contrasts.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(contrasts[0]))
        writer.writeheader()
        writer.writerows(contrasts)

    lines = ["# WP3 - Freshness-threshold sensitivity", ""]
    lines.append("The 480 frozen confirmation trajectories were re-executed with a read-only per-round observer. "
                 "Packet generation, routing, listening, energy and packet-expiry behaviour are unchanged; only the "
                 "age criterion entering the coverage metric changes. The D=4 recomputation matches the published "
                 "480-run metrics to $10^{-9}$ (maximum absolute deviation in coverage and Source P5).")
    lines.append("")
    lines.append("D=2/4/8/16 correspond to 30/60/120/240 min. Packet deadline remains four rounds; the wider "
                 "criteria therefore describe reporting-window sensitivity, not a lower-frequency sampling design.")
    lines.append("")
    for code, label in CELLS:
        lines.append(f"## {label}")
        lines.append("")
        lines.append("| Supply | D (min) | JLC-R cov. (%) | Prefix-only (%) | Hybrid (%) | PADC-AGE (%) | JLC-R P5 (%) | Matched diff. (pp) |")
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for supply in SUPPLIES:
            for d in DS:
                entries = {r["controller"]: r for r in summary
                           if r["condition"] == code and r["supply"] == supply and r["D"] == d}
                contrast = next(r for r in contrasts if r["condition"] == code and r["supply"] == supply
                                and r["D"] == d and r["metric"] == "coverage")
                lines.append(f"| {supply} | {15 * d} | {entries['JLC-R']['coverage_mean']:.2f} | "
                             f"{entries['Prefix-only']['coverage_mean']:.2f} | {entries['Hybrid control']['coverage_mean']:.2f} | "
                             f"{entries['PADC-AGE']['coverage_mean']:.2f} | {entries['JLC-R']['source_p5_mean']:.2f} | "
                             f"{contrast['mean_difference']:+.2f} [{contrast['ci95_low']:+.2f}, {contrast['ci95_high']:+.2f}] |")
        lines.append("")
    gains = [r["mean_difference"] for r in contrasts if r["metric"] == "coverage"]
    p5_gains = [r["mean_difference"] for r in contrasts if r["metric"] == "source_p5"]
    lines.append("## Reading")
    lines.append("")
    lines.append(f"Across the 32 cell-supply-threshold combinations, the matched coverage difference ranges from "
                 f"{min(gains):+.2f} to {max(gains):+.2f} pp; the Source P5 difference ranges from "
                 f"{min(p5_gains):+.2f} to {max(p5_gains):+.2f} pp. The sign is not uniform: the T2/0.7 "
                 "prefix-only contrast is slightly negative at D=4 and remains so at wider thresholds, while the "
                 "PADC comparisons remain strongly positive. This is consistent with the retained noninferiority "
                 "result and is not a claim of uniform superiority.")
    lines.append("")
    lines.append("Widening D raises coverage for every controller because packets that are present but older "
                 "become eligible. The ordering of controllers is broadly preserved, which indicates that the "
                 "reported mechanism differences are not an artefact of the 60-min criterion. No energy saving is "
                 "implied: all runs consume the same physical energy as the original confirmation.")
    (OUT / "freshness_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"worst_D4_deviation": worst_d4, "worst_P5_deviation": worst_p5,
                      "coverage_diff_range": [min(gains), max(gains)],
                      "p5_diff_range": [min(p5_gains), max(p5_gains)]}, indent=2))


if __name__ == "__main__":
    main()
