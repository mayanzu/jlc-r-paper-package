"""WP1: cross-regime comparison from the retained 480-run confirmation.

Reads only the frozen published metrics. No simulator is imported or executed.
All comparisons are seed-paired; the twelve network seeds are the independent
units. Formal inference remains the original Holm-36 noninferiority family;
the additional cross-baseline contrasts written here are descriptive.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
SOURCE = PROJECT / "code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv"
OUT = HERE / "results"
CELLS = [
    ("SYNTHETIC_G20", "Synthetic"),
    ("WINTER_G20", "T1 winter"),
    ("T2_G20", "T2 spring"),
    ("T3_G20", "T3 winter"),
]
SUPPLIES = [1.0, 0.7]
METHODS = {
    "JLC-R": "JLC-R-HYB-V63",
    "Prefix-only": "JLC-R-SA",
    "Hybrid control": "JLC-R-HYB",
    "PADC-AGE": "PADC-AGE",
    "PADC+relay": "PADC-AGE+V63",
}
METRICS = [
    ("coverage_pct", "Coverage", "percentage points", "higher"),
    ("aoi_mean_minutes", "Mean AoI", "minutes", "lower"),
    ("source_coverage_p5_pct", "Source P5", "percentage points", "higher"),
    ("night_off_pct", "Nighttime outage", "percentage points", "lower"),
]
SEEDS = list(range(160101, 161213, 101))


def read_rows():
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    index = {}
    for row in rows:
        index[(row["condition"], float(row["supply"]), int(row["seed"]), row["method"])] = row
    assert len(index) == 480
    return index


def t_interval(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    half = float(stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return mean, mean - half, mean + half


def main():
    OUT.mkdir(exist_ok=True)
    index = read_rows()
    rows = []
    for code, label in CELLS:
        for supply in SUPPLIES:
            for comparator in ["Prefix-only", "Hybrid control", "PADC-AGE", "PADC+relay"]:
                for metric, metric_label, unit, direction in METRICS:
                    base = np.array([float(index[(code, supply, s, METHODS[comparator])][metric]) for s in SEEDS])
                    jlc = np.array([float(index[(code, supply, s, METHODS["JLC-R"])][metric]) for s in SEEDS])
                    diff = jlc - base
                    mean, lo, hi = t_interval(diff)
                    base_mean = float(base.mean())
                    if abs(base_mean) < 1e-9:
                        relative = None
                    elif direction == "higher":
                        relative = 100.0 * mean / abs(base_mean)
                    else:
                        relative = -100.0 * mean / abs(base_mean)
                    rows.append(dict(
                        condition=code, condition_label=label, supply=supply,
                        comparator=comparator, metric=metric, metric_label=metric_label,
                        unit=unit, direction=direction, seed_count=len(SEEDS),
                        jlc_r_mean=float(jlc.mean()), comparator_mean=base_mean,
                        mean_difference=mean, ci95_low=lo, ci95_high=hi,
                        relative_improvement_pct=relative,
                        jlc_r_better=bool((mean > 0) if direction == "higher" else (mean < 0)),
                        inference="descriptive paired contrast; not part of Holm-36",
                    ))
    with (OUT / "cross_regime_comparison.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    absolute = []
    for code, label in CELLS:
        for supply in SUPPLIES:
            for name, method in METHODS.items():
                entry = dict(condition=code, condition_label=label, supply=supply, controller=name)
                for metric, metric_label, unit, direction in METRICS:
                    values = np.array([float(index[(code, supply, s, method)][metric]) for s in SEEDS])
                    entry[f"{metric}_mean"] = float(values.mean())
                    entry[f"{metric}_sd"] = float(values.std(ddof=1))
                entry["consumed_j_mean"] = float(np.mean([float(index[(code, supply, s, method)]["consumed_j"]) for s in SEEDS]))
                absolute.append(entry)
    with (OUT / "cross_regime_absolute.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(absolute[0]))
        writer.writeheader()
        writer.writerows(absolute)

    def find(condition, supply, comparator, metric):
        return next(r for r in rows if r["condition"] == condition and r["supply"] == supply
                    and r["comparator"] == comparator and r["metric"] == metric)

    highlights = {
        "winter_prefix_coverage": find("WINTER_G20", 0.7, "Prefix-only", "coverage_pct"),
        "winter_prefix_aoi": find("WINTER_G20", 0.7, "Prefix-only", "aoi_mean_minutes"),
        "synthetic_padc_coverage": find("SYNTHETIC_G20", 0.7, "PADC-AGE", "coverage_pct"),
        "spring_padc_coverage": find("T2_G20", 0.7, "PADC-AGE", "coverage_pct"),
        "spring_padc_p5": find("T2_G20", 0.7, "PADC-AGE", "source_coverage_p5_pct"),
    }
    hybrid = [r for r in rows if r["comparator"] == "Hybrid control"]
    summary = {
        "source_sha256": __import__("hashlib").sha256(SOURCE.read_bytes()).hexdigest(),
        "seed_count": len(SEEDS),
        "cells": len(CELLS), "supplies": len(SUPPLIES),
        "contrasts": len(rows),
        "highlights": highlights,
        "hybrid_control": hybrid,
        "hybrid_cells_where_jlc_r_coverage_lower": [r for r in hybrid if r["metric"] == "coverage_pct" and r["mean_difference"] < 0],
    }
    (OUT / "cross_regime_summary.json").write_text(json.dumps(summary, indent=2, default=float) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["seed_count", "contrasts"]}, indent=2))
    for key, value in highlights.items():
        print(key, round(value["comparator_mean"], 3), "->", round(value["jlc_r_mean"], 3),
              "diff", round(value["mean_difference"], 3), "CI", round(value["ci95_low"], 3), round(value["ci95_high"], 3))


if __name__ == "__main__":
    main()
