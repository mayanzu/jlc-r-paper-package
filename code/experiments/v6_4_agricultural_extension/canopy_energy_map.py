"""Per-node canopy transmittance map for the WP4 stress test (no simulation).

The canopy field is deterministic given the network seed; this script records the
node-level energy factor that the simulator applies during the 384 canopy runs.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
sys.path.insert(0, str(PROJECT / "code" / "simulation"))
from current_io import ROOT, load_config, build_scenario  # noqa: E402
from canopy_model import spatial_canopy, transmittance, STAGE_RANGES  # noqa: E402

OUT = HERE / "results"
SEEDS = list(range(190101, 191213, 101))
STAGES = ["I", "II", "III"]


def main():
    design = json.loads((ROOT / "current_design.json").read_text(encoding="utf-8"))
    condition = next(x for x in design["conditions"] if x["name"] == "T2_G20")
    c = load_config(condition)
    rows, summary = [], []
    for seed in SEEDS:
        sc = build_scenario(c, seed, 14, 1.0, condition)
        canopy = spatial_canopy(sc.pos, seed)
        distance = np.hypot(sc.pos[:, 0] - sc.sink[0], sc.pos[:, 1] - sc.sink[1])
        for stage in STAGES:
            factor = transmittance(canopy, stage)
            for node in range(len(canopy)):
                rows.append({
                    "seed": seed, "node": node, "stage": stage,
                    "x_m": float(sc.pos[node, 0]), "y_m": float(sc.pos[node, 1]),
                    "distance_to_sink_m": float(distance[node]),
                    "canopy_intensity": float(canopy[node]),
                    "relative_harvest_factor": float(factor[node]),
                })
            summary.append({
                "seed": seed, "stage": stage,
                "transmittance_min": float(factor.min()),
                "transmittance_p5": float(np.quantile(factor, 0.05)),
                "transmittance_mean": float(factor.mean()),
                "fraction_below_0_7": float((factor < 0.7).mean()),
                "spearman_canopy_distance": float(
                    np.corrcoef(np.argsort(np.argsort(canopy)), np.argsort(np.argsort(distance)))[0, 1]),
                "far_mean_transmittance": float(factor[distance >= 200].mean()) if (distance >= 200).any() else float("nan"),
            })
    with (OUT / "canopy_node_energy.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (OUT / "canopy_energy_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    print(json.dumps({
        "nodes": len(rows) // (len(SEEDS) * len(STAGES)),
        "rows": len(rows),
        "stage_ranges": STAGE_RANGES,
        "mean_transmittance_by_stage": {
            stage: float(np.mean([r["transmittance_mean"] for r in summary if r["stage"] == stage]))
            for stage in STAGES},
    }, indent=2))


if __name__ == "__main__":
    main()
