"""WP2: winter supply-scaling response analysis (exploratory extension)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SOURCE = OUT / "supply.csv"
LABELS = {"WINTER_G20": "T1 winter", "T3_G20": "T3 winter"}
CONTROLLERS = ["JLC-R", "Prefix-only", "Hybrid control", "PADC-AGE"]
SUPPLIES = [0.7, 1.0, 1.5, 2.0, 2.5, 3.0]
SEEDS = list(range(170101, 171213, 101))
METRICS = ["coverage_pct", "aoi_mean_minutes", "source_coverage_p5_pct", "night_off_pct"]


def read_rows():
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    index = {(r["condition"], float(r["supply"]), int(r["seed"]), r["method"]): r for r in rows}
    expected = {(c, s, seed, m) for c in LABELS for s in SUPPLIES for seed in SEEDS for m in CONTROLLERS}
    assert len(rows) == 576 and set(index) == expected, (len(rows), len(expected - set(index)))
    return rows, index


def ci(values):
    values = np.asarray(values, dtype=float)
    half = float(stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return float(values.mean()), float(values.mean() - half), float(values.mean() + half)


def crossing(supplies, values, target):
    for i in range(len(supplies) - 1):
        a, b = values[i], values[i + 1]
        if (a - target) * (b - target) <= 0 and a != b:
            return float(supplies[i] + (target - a) * (supplies[i + 1] - supplies[i]) / (b - a))
    return None


def main():
    rows, index = read_rows()
    summary, response, paired = [], [], []
    for condition in LABELS:
        for supply in SUPPLIES:
            for controller in CONTROLLERS:
                subset = [index[(condition, supply, seed, controller)] for seed in SEEDS]
                entry = {"condition": condition, "supply": supply, "controller": controller}
                for metric in METRICS + ["consumed_j", "harvested_j", "spilled_j", "base_consumed_j",
                                         "comm_consumed_j", "coverage_second_half_pct",
                                         "coverage_first_half_pct", "battery_end_mean_j",
                                         "battery_second_half_mean_j", "battery_first_half_mean_j",
                                         "spill_fraction", "off_pct", "fdc_activated_node_periods",
                                         "infeasible_node_periods", "node_periods",
                                         "source_p5_D8_pct", "source_p5_D16_pct"]:
                    values = np.array([float(r[metric]) for r in subset], dtype=float)
                    entry[f"{metric}_mean"] = float(values.mean())
                    entry[f"{metric}_sd"] = float(values.std(ddof=1))
                summary.append(entry)
            jlc = [index[(condition, supply, seed, "JLC-R")] for seed in SEEDS]
            net = [float(r["battery_end_mean_j"]) - float(r["initial_battery_mean_j"]) for r in jlc]
            drift = [float(r["battery_second_half_mean_j"]) - float(r["battery_first_half_mean_j"]) for r in jlc]
            mean_net, lo_net, hi_net = ci(net)
            mean_drift, lo_drift, hi_drift = ci(drift)
            response.append({
                "condition": condition, "supply": supply,
                "coverage_mean": float(np.mean([float(r["coverage_pct"]) for r in jlc])),
                "source_p5_mean": float(np.mean([float(r["source_coverage_p5_pct"]) for r in jlc])),
                "battery_net_change_mean_j": mean_net, "battery_net_ci95_low": lo_net, "battery_net_ci95_high": hi_net,
                "battery_second_half_drift_mean_j": mean_drift, "battery_drift_ci95_low": lo_drift,
                "battery_drift_ci95_high": hi_drift,
                "harvest_available_per_node_day_j": float(np.mean([(float(r["harvested_j"]) - float(r["spilled_j"])) / (100 * 14) for r in jlc])),
                "consumed_per_node_day_j": float(np.mean([float(r["consumed_j"]) / (100 * 14) for r in jlc])),
                "base_per_node_day_j": float(np.mean([float(r["base_consumed_j"]) / (100 * 14) for r in jlc])),
                "comm_per_node_day_j": float(np.mean([float(r["comm_consumed_j"]) / (100 * 14) for r in jlc])),
                "spill_fraction_mean": float(np.mean([float(r["spill_fraction"]) for r in jlc])),
                "fdc_activation_share": float(np.mean([float(r["fdc_activated_node_periods"]) / max(1.0, float(r["node_periods"])) for r in jlc])),
                "prefix_infeasible_share": float(np.mean([float(r["infeasible_node_periods"]) / max(1.0, float(r["node_periods"])) for r in jlc])),
            })
            for comparator in CONTROLLERS[1:]:
                for metric in METRICS:
                    difference = np.array([float(index[(condition, supply, seed, "JLC-R")][metric]) -
                                           float(index[(condition, supply, seed, comparator)][metric]) for seed in SEEDS])
                    mean, low, high = ci(difference)
                    paired.append({"condition": condition, "supply": supply, "comparator": comparator,
                                   "metric": metric, "mean_difference": mean, "ci95_low": low, "ci95_high": high,
                                   "seed_count": len(SEEDS)})

    with (OUT / "supply_scan_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    with (OUT / "supply_scan_response.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(response[0]))
        writer.writeheader()
        writer.writerows(response)
    with (OUT / "supply_scan_paired.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)

    thresholds = {}
    for condition in LABELS:
        target_coverage = [next(r["coverage_mean"] for r in response if r["condition"] == condition and r["supply"] == s) for s in SUPPLIES]
        target_p5 = [next(r["source_p5_mean"] for r in response if r["condition"] == condition and r["supply"] == s) for s in SUPPLIES]
        net = [next(r["battery_net_change_mean_j"] for r in response if r["condition"] == condition and r["supply"] == s) for s in SUPPLIES]
        drift = [next(r["battery_second_half_drift_mean_j"] for r in response if r["condition"] == condition and r["supply"] == s) for s in SUPPLIES]
        thresholds[condition] = {
            "coverage_70_supply": crossing(SUPPLIES, target_coverage, 70.0),
            "coverage_80_supply": crossing(SUPPLIES, target_coverage, 80.0),
            "p5_10_supply": crossing(SUPPLIES, target_p5, 10.0),
            "p5_20_supply": crossing(SUPPLIES, target_p5, 20.0),
            "battery_neutral_supply": crossing(SUPPLIES, net, 0.0),
            "second_half_stable_supply": crossing(SUPPLIES, drift, 0.0),
            "max_coverage": max(target_coverage), "max_p5": max(target_p5),
            "coverage_values": target_coverage, "p5_values": target_p5,
            "battery_net_values": net, "battery_drift_values": drift,
        }
    (OUT / "supply_scan_thresholds.json").write_text(json.dumps(thresholds, indent=2) + "\n", encoding="utf-8")

    # Paired coverage differences at every supply (descriptive).
    lines = ["# WP2 - Winter supply-scaling response", ""]
    lines.append("New exploratory cohort: 12 seeds (`170101`-`171212`), two measured winter trajectories, "
                 "six supply multipliers, four controllers, 576 executions. Fixed network, S200/G20 timing, "
                 "60-min freshness target and physical costs; only the effective solar multiplier changes.")
    lines.append("")
    lines.append("Supply multipliers are model scalars acting on the normalized energy scale. They are not "
                 "calibrated panel-area or irradiance multipliers.")
    lines.append("")
    for condition in LABELS:
        t = thresholds[condition]
        lines.append(f"## {LABELS[condition]}")
        lines.append("")
        lines.append("| Supply | JLC-R coverage (%) | Prefix-only (%) | Hybrid (%) | PADC-AGE (%) | JLC-R P5 (%) | JLC-R AoI (min) | Battery change (J) | Second-half drift (J) |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for supply in SUPPLIES:
            entries = {r["controller"]: r for r in summary if r["condition"] == condition and r["supply"] == supply}
            resp = next(r for r in response if r["condition"] == condition and r["supply"] == supply)
            lines.append(f"| {supply:.1f} | {entries['JLC-R']['coverage_pct_mean']:.2f} | "
                         f"{entries['Prefix-only']['coverage_pct_mean']:.2f} | {entries['Hybrid control']['coverage_pct_mean']:.2f} | "
                         f"{entries['PADC-AGE']['coverage_pct_mean']:.2f} | {entries['JLC-R']['source_coverage_p5_pct_mean']:.2f} | "
                         f"{entries['JLC-R']['aoi_mean_minutes_mean']:.1f} | "
                         f"{resp['battery_net_change_mean_j']:+.3f} | {resp['battery_second_half_drift_mean_j']:+.3f} |")
        lines.append("")
        def label(value):
            return "not reached" if value is None else f"{value:.2f}"

        lines.append(f"Empirical crossings (linear interpolation on the modeled scale): coverage 70% "
                     f"{label(t['coverage_70_supply'])}; coverage 80% {label(t['coverage_80_supply'])}; "
                     f"P5 10% {label(t['p5_10_supply'])}; battery-neutral (end equals start) "
                     f"{label(t['battery_neutral_supply'])}; second-half drift zero "
                     f"{label(t['second_half_stable_supply'])}.")
        lines.append("")
        lines.append(f"Maximum JLC-R coverage in this sweep: {t['max_coverage']:.2f}%; maximum Source P5: {t['max_p5']:.2f}%.")
        lines.append("")
    (OUT / "supply_scan_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(thresholds, indent=2))


if __name__ == "__main__":
    main()
