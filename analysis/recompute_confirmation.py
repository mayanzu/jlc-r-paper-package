"""Recompute 32-test noninferiority statistics from supplied 480 records.

Never runs a simulator. Reads the bundled confirmation CSVs, recomputes
paired means/SDs/CIs/p values/Holm adjustments, and compares numerically to
the supplied table.
"""
from pathlib import Path
import csv
import math
import numpy as np
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / "code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv"
STATS = ROOT / "code/experiments/v6_3_relay_repair/D_noninferiority_seeds16.csv"
BENCH = ROOT / "code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds15.csv"
SEED_SEARCH = ROOT / "code/experiments/v6_3_relay_repair/D_seed_search.csv"
MATRIX = ROOT / "configs/experiment_matrix.json"


def rows(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def holm(ps):
    order = np.argsort(ps, kind="stable")
    out = np.empty(len(ps))
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[idx]))
        out[idx] = running
    return out


def one_sided_p(d):
    d = np.asarray(d, float)
    sd = d.std(ddof=1)
    if sd == 0:
        return 0.0 if d.mean() > 0 else 1.0
    return float(t.sf(d.mean() / (sd / math.sqrt(len(d))), len(d) - 1))


def recompute():
    import json

    data = rows(METRICS)
    assert len(data) == 480, len(data)
    idx = {(x["condition"], x["supply"], x["seed"], x["method"]): x for x in data}
    assert len(idx) == 480
    seeds = sorted({x["seed"] for x in data}, key=int)
    assert seeds == [str(160101 + 101 * k) for k in range(12)], seeds
    assert len({x["method"] for x in data}) == 5
    for x in data:
        assert float(x["max_hold_violation_j"]) < 1e-8
        assert int(x["max_slot_violation"]) == 0

    saved = rows(STATS)
    assert len(saved) == 32, len(saved)
    ni = []
    rel = []
    for x in saved:
        c, s = x["condition"], x["supply"]
        base = "JLC-R-SA" if c in ["SYNTHETIC_G20", "T2_G20"] else "PADC-AGE"
        assert x["baseline"] == base, (c, s, x["baseline"])
        a = np.array([float(idx[c, s, seed, "JLC-R-HYB-V63"][x["metric"]]) for seed in seeds])
        b = np.array([float(idx[c, s, seed, base][x["metric"]]) for seed in seeds])
        d = a - b
        upper = x["metric"] in ["aoi_mean_minutes", "night_off_pct"]
        margin = 0.05 * b.mean() if x["metric"] == "aoi_mean_minutes" else (1 if upper else -1)
        ni.append(one_sided_p(margin - d if upper else d - margin))
        rel.append(one_sided_p(1.05 * b - a) if x["metric"] == "aoi_mean_minutes" else ni[-1])
        se = d.std(ddof=1) / math.sqrt(12)
        half = t.ppf(0.975, 11) * se
        np.testing.assert_allclose(
            [d.mean(), d.std(ddof=1), d.mean() - half, d.mean() + half, margin, ni[-1], rel[-1]],
            [float(x[k]) for k in ["mean_diff", "sd_diff", "ci95_lo", "ci95_hi", "margin", "p_raw", "p_rel"]],
            rtol=1e-9, atol=1e-12,
        )
    improvements = _improvement_ps(idx, seeds)
    h36 = holm(ni + improvements)
    # 4 winter coverage superiority tests complete the prespecified Holm-36 family.
    h37 = holm(ni + improvements + [1.0])
    h32 = holm(ni)
    repair = _repair_p(idx, seeds)
    hr = holm(rel + [repair])
    for key, vals in [("p_holm36", h36[:32]), ("p_holm37", h37[:32]), ("p_holm32", h32), ("p_rel_holm33", hr[:32])]:
        np.testing.assert_allclose(vals, [float(x[key]) for x in saved], atol=1e-12, rtol=1e-9, err_msg=key)
    assert sum(h36[:32] < 0.05) == 32
    assert sum(hr[:32] < 0.05) == 32

    bench = rows(BENCH)
    assert len(bench) == 96
    assert {int(x["seed"]) for x in bench} == {150101 + 101 * k for k in range(12)}
    search = rows(SEED_SEARCH)
    assert {int(x["candidate_seed"]) for x in search} == {160101 + 101 * k for k in range(12)}
    for x in search:
        assert int(x["exact_seed_hits_in_code"]) == 0
        assert int(x["exact_seed_hits_in_temp"]) == 0

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    assert matrix["job_count"] == 480
    assert len(matrix["jobs"]) == 480
    matrix_keys = {(j["condition"], str(j["supply"]), str(j["seed"]), j["method"]) for j in matrix["jobs"]}
    assert matrix_keys == set(idx.keys())

    return dict(
        confirmation_rows=480,
        methods=5,
        seeds=12,
        primary_NI_tests=32,
        NI_pass=int(sum(h36[:32] < 0.05)),
        relative_sensitivity_pass=int(sum(hr[:32] < 0.05)),
        benchmark_rows=96,
        seed_search_rows=12,
        numerical_reference_match=True,
    )


def _improvement_ps(idx, seeds):
    out = []
    for c in ["WINTER_G20", "T3_G20"]:
        for s in ["1.0", "0.7"]:
            d = [float(idx[c, s, seed, "JLC-R-HYB-V63"]["coverage_pct"]) - float(idx[c, s, seed, "JLC-R-SA"]["coverage_pct"]) for seed in seeds]
            out.append(one_sided_p(d))
    return out


def _repair_p(idx, seeds):
    d = [float(idx["WINTER_G20", "1.0", seed, "JLC-R-HYB"]["aoi_mean_minutes"]) - float(idx["WINTER_G20", "1.0", seed, "JLC-R-HYB-V63"]["aoi_mean_minutes"]) for seed in seeds]
    return one_sided_p(d)


if __name__ == "__main__":
    import json as _json

    print(_json.dumps(recompute(), indent=2))
