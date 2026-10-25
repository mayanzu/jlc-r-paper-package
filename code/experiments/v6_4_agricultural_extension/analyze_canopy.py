"""WP4: crop-canopy energy/channel coupling stress test (exploratory)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SOURCE = OUT / "canopy.csv"
TREATMENTS = ["C0", "I-C1", "II-C1", "II-C2", "II-C3", "III-C1", "III-C2", "III-C3"]
CONTROLLERS = ["JLC-R", "Prefix-only", "Hybrid control", "PADC-AGE"]
SEEDS = list(range(190101, 191213, 101))


def read_rows():
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    index = {(r["canopy_treatment"], int(r["seed"]), r["method"]): r for r in rows}
    expected = {(t, seed, m) for t in TREATMENTS for seed in SEEDS for m in CONTROLLERS}
    assert len(rows) == 384 and set(index) == expected, (len(rows), len(expected - set(index)))
    return rows, index


def ci(values):
    values = np.asarray(values, dtype=float)
    half = float(stats.t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values)))
    return float(values.mean()), float(values.mean() - half), float(values.mean() + half)


def main():
    rows, index = read_rows()
    summary, effects, contrasts = [], [], []
    metrics = ["coverage_pct", "aoi_mean_minutes", "source_coverage_p5_pct", "night_off_pct",
               "far_coverage_D4_pct", "far_source_min_coverage_pct", "link_success_pct",
               "transit_protect_denials", "grant_denied_events", "forward_reserve_events",
               "transit_block_events", "hold_created", "held_packet_hop_successes",
               "consumed_j", "spilled_j", "spill_fraction", "battery_end_mean_j", "off_pct",
               "coverage_D8_pct", "coverage_D16_pct"]
    for treatment in TREATMENTS:
        for controller in CONTROLLERS:
            subset = [index[(treatment, seed, controller)] for seed in SEEDS]
            entry = {"treatment": treatment, "controller": controller}
            for metric in metrics:
                values = np.array([float(r[metric]) for r in subset])
                entry[f"{metric}_mean"] = float(values.mean())
                entry[f"{metric}_sd"] = float(values.std(ddof=1))
            summary.append(entry)
        for controller in CONTROLLERS:
            for metric in ["coverage_pct", "aoi_mean_minutes", "source_coverage_p5_pct",
                           "far_coverage_D4_pct", "battery_end_mean_j"]:
                delta = np.array([float(index[(treatment, seed, controller)][metric]) -
                                  float(index[("C0", seed, controller)][metric]) for seed in SEEDS])
                mean, low, high = ci(delta)
                effects.append({"treatment": treatment, "controller": controller, "metric": metric,
                                "mean_change": mean, "ci95_low": low, "ci95_high": high})
        for comparator in CONTROLLERS[1:]:
            for metric in ["coverage_pct", "source_coverage_p5_pct", "far_coverage_D4_pct",
                           "aoi_mean_minutes"]:
                delta = np.array([float(index[(treatment, seed, "JLC-R")][metric]) -
                                  float(index[(treatment, seed, comparator)][metric]) for seed in SEEDS])
                mean, low, high = ci(delta)
                contrasts.append({"treatment": treatment, "comparator": comparator, "metric": metric,
                                  "mean_difference": mean, "ci95_low": low, "ci95_high": high})

    with (OUT / "canopy_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    with (OUT / "canopy_effects.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(effects[0]))
        writer.writeheader()
        writer.writerows(effects)
    with (OUT / "canopy_contrasts.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(contrasts[0]))
        writer.writeheader()
        writer.writerows(contrasts)

    def get(treatment, controller, metric):
        return next(r for r in summary if r["treatment"] == treatment and r["controller"] == controller)[f"{metric}_mean"]

    # Interaction of joint degradation: C3 - C1 - C2 + C0 (paired by seed).
    interactions = []
    for stage, c1, c2, c3 in [("II", "II-C1", "II-C2", "II-C3"), ("III", "III-C1", "III-C2", "III-C3")]:
        for controller in CONTROLLERS:
            delta = np.array([
                (float(index[(c3, s, controller)]["coverage_pct"]) - float(index[(c1, s, controller)]["coverage_pct"]))
                - (float(index[(c2, s, controller)]["coverage_pct"]) - float(index[("C0", s, controller)]["coverage_pct"]))
                for s in SEEDS])
            mean, low, high = ci(delta)
            interactions.append({"stage": stage, "controller": controller, "metric": "coverage_pct",
                                 "interaction": mean, "ci95_low": low, "ci95_high": high})
    with (OUT / "canopy_interactions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(interactions[0]))
        writer.writeheader()
        writer.writerows(interactions)

    def contrast(treatment, comparator, metric):
        return next(r for r in contrasts if r["treatment"] == treatment and r["comparator"] == comparator and r["metric"] == metric)

    severe = contrast("III-C3", "Hybrid control", "coverage_pct")
    severe_padc = contrast("III-C3", "PADC-AGE", "coverage_pct")
    if severe["ci95_low"] > 0:
        verdict = "case1"
        verdict_text = ("JLC-R retains a positive paired coverage advantage over the hybrid control under "
                        "the most severe joint degradation (95% interval excludes zero).")
    elif severe["ci95_high"] < 0:
        verdict = "case3"
        verdict_text = ("JLC-R falls behind the hybrid control under the most severe joint degradation; the "
                        "physical channel/energy loss exceeds what resource scheduling can compensate.")
    else:
        verdict = "case2"
        verdict_text = ("JLC-R and the hybrid control are statistically comparable under the most severe joint "
                        "degradation; the mechanism remains robust but the added agricultural-specific evidence "
                        "is limited.")

    lines = ["# WP4 - Crop-canopy energy/channel coupling", ""]
    lines.append("Exploratory stress test on the T2 spring trajectory at nominal supply, 12 seeds "
                 "(`190101`-`191212`), four controllers, eight treatment combinations, 384 executions. The same "
                 "spatially correlated canopy field is shared by all controllers within each seed. Ranges are "
                 "candidate stress ranges, not measured crop physiological parameters.")
    lines.append("")
    lines.append("Treatments: C0 baseline; C1 energy transmittance only; C2 channel attenuation only; C3 joint. "
                 "Stage I (0.85-1.00 transmittance, lambda=0) coincides with C0/C1, so only its C1 cell is run. "
                 "Stages II and III add lambda=0.10 and 0.20 respectively.")
    lines.append("")
    lines.append("## Absolute outcomes")
    lines.append("")
    lines.append("| Treatment | JLC-R cov. (%) | Prefix-only (%) | Hybrid (%) | PADC-AGE (%) | JLC-R P5 (%) | JLC-R far cov. (%) | JLC-R transit denials |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for treatment in TREATMENTS:
        lines.append(f"| {treatment} | {get(treatment, 'JLC-R', 'coverage_pct'):.2f} | "
                     f"{get(treatment, 'Prefix-only', 'coverage_pct'):.2f} | "
                     f"{get(treatment, 'Hybrid control', 'coverage_pct'):.2f} | "
                     f"{get(treatment, 'PADC-AGE', 'coverage_pct'):.2f} | "
                     f"{get(treatment, 'JLC-R', 'source_coverage_p5_pct'):.2f} | "
                     f"{get(treatment, 'JLC-R', 'far_coverage_D4_pct'):.2f} | "
                     f"{get(treatment, 'JLC-R', 'transit_protect_denials'):.0f} |")
    lines.append("")
    lines.append("## Change from the C0 baseline (JLC-R)")
    lines.append("")
    lines.append("| Treatment | Coverage (pp) | Mean AoI (min) | Source P5 (pp) | Far coverage (pp) | End battery (J) |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for treatment in TREATMENTS[1:]:
        row = {r["metric"]: r for r in effects if r["treatment"] == treatment and r["controller"] == "JLC-R"}
        lines.append(f"| {treatment} | {row['coverage_pct']['mean_change']:+.2f} "
                     f"[{row['coverage_pct']['ci95_low']:+.2f}, {row['coverage_pct']['ci95_high']:+.2f}] | "
                     f"{row['aoi_mean_minutes']['mean_change']:+.1f} | {row['source_coverage_p5_pct']['mean_change']:+.2f} | "
                     f"{row['far_coverage_D4_pct']['mean_change']:+.2f} | {row['battery_end_mean_j']['mean_change']:+.3f} |")
    lines.append("")
    lines.append("## Joint-degradation interaction")
    lines.append("")
    lines.append("The interaction is (C3 - C1) - (C2 - C0): a negative value means the two degradations compound "
                 "more strongly than their separate effects.")
    lines.append("")
    lines.append("| Stage | Controller | Interaction (pp) | 95% CI |")
    lines.append("| --- | --- | ---: | --- |")
    for row in interactions:
        lines.append(f"| {row['stage']} | {row['controller']} | {row['interaction']:+.2f} | "
                     f"[{row['ci95_low']:+.2f}, {row['ci95_high']:+.2f}] |")
    lines.append("")
    lines.append("## Mechanism counters (JLC-R)")
    lines.append("")
    lines.append("| Treatment | Link success (%) | Grant denied | Forward reserve | Transit denials | Holds created | Held-hop successes | Off (%) | Spill (%) |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for treatment in TREATMENTS:
        entry = next(r for r in summary if r["treatment"] == treatment and r["controller"] == "JLC-R")
        lines.append(f"| {treatment} | {float(entry['link_success_pct_mean']):.2f} | "
                     f"{float(entry['grant_denied_events_mean']):.0f} | {float(entry['forward_reserve_events_mean']):.0f} | "
                     f"{float(entry['transit_protect_denials_mean']):.0f} | {float(entry['hold_created_mean']):.0f} | "
                     f"{float(entry['held_packet_hop_successes_mean']):.0f} | {float(entry['off_pct_mean']):.2f} | "
                     f"{100 * float(entry['spill_fraction_mean']):.1f} |")
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(f"Under the most severe joint treatment (III-C3), the paired JLC-R minus hybrid-control coverage "
                 f"difference is {severe['mean_difference']:+.2f} pp "
                 f"[{severe['ci95_low']:+.2f}, {severe['ci95_high']:+.2f}]; against PADC-AGE it is "
                 f"{severe_padc['mean_difference']:+.2f} pp "
                 f"[{severe_padc['ci95_low']:+.2f}, {severe_padc['ci95_high']:+.2f}]. {verdict_text}")
    lines.append("")
    lines.append("Because the channel treatment reduces decoding probability and changes ETX ranks identically for "
                 "all controllers, the comparison isolates scheduling and relay-protection behaviour under a shared "
                 "physical environment. It does not validate a field propagation model, and the transmittance values "
                 "are not a crop-specific calibration.")
    (OUT / "canopy_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "severe_vs_hybrid": severe, "severe_vs_padc": severe_padc,
                      "interactions": interactions}, indent=2))


if __name__ == "__main__":
    main()
