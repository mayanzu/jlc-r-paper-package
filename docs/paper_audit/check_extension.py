"""Read-only checks for the COMPAG agricultural-extension tables and figures.

The extension tables are compared against the CSV files produced by
code/experiments/v6_4_agricultural_extension. No simulator is imported.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from paths import ROOT as PROJECT, MAIN as COMPAG, AUDIT, FIGURES
from article_evidence import full_table_view
EXT = PROJECT / "code/experiments/v6_4_agricultural_extension/results"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def table(text, label):
    match = re.search(r"^Table " + re.escape(label) + r"\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)", text, re.M)
    require(match is not None, f"Missing table {label}")
    rows = [[v.strip() for v in line.strip().strip("|").split("|")] for line in match[1].splitlines()]
    require(len(rows) >= 3 and all(len(r) == len(rows[0]) for r in rows), f"Table {label} shape")
    return rows[0], rows[2:]


def number(value, actual, label, digits):
    require(re.fullmatch(r"[+-]?\d+(?:\.\d+)?", value) is not None, f"{label}: invalid number {value!r}")
    tolerance = 0.50001 * 10 ** (-digits) + 1e-12
    require(abs(float(value) - float(actual)) <= tolerance, f"{label}: displayed {value}, recomputed {actual:.14g}")


def different(value, actual, label):
    require(re.fullmatch(r"[+-]?\d+(?:\.\d+)?", value) is not None, f"{label}: invalid difference {value!r}")
    require(abs(float(value) - float(actual)) <= 0.0050001 + 1e-12, f"{label}: displayed {value}, recomputed {actual:.14g}")


def check_tables(ms):
    counts = {}
    # Table 6: winter supply response.
    header, rows = table(ms, "6")
    require(len(header) == 9 and len(rows) == 12, ("Table 6 shape", len(header), len(rows)))
    summary = read_csv(EXT / "supply_scan_summary.csv")
    response = read_csv(EXT / "supply_scan_response.csv")
    labels = {"T1 winter": "WINTER_G20", "T3 winter": "T3_G20"}
    for row in rows:
        condition = labels[row[0]]
        supply = float(row[1])
        for name, column, digits in [("JLC-R", 2, 2), ("Prefix-only", 3, 2),
                                     ("Hybrid control", 4, 2), ("PADC-AGE", 5, 2)]:
            entry = next(r for r in summary if r["condition"] == condition
                         and float(r["supply"]) == supply and r["controller"] == name)
            number(row[column], float(entry["coverage_pct_mean"]), f"Table 6 {row[0]} {supply} {name}", digits)
        entry = next(r for r in summary if r["condition"] == condition
                     and float(r["supply"]) == supply and r["controller"] == "JLC-R")
        resp = next(r for r in response if r["condition"] == condition and float(r["supply"]) == supply)
        number(row[6], float(entry["source_coverage_p5_pct_mean"]), f"Table 6 P5 {row[0]} {supply}", 2)
        number(row[7], float(entry["aoi_mean_minutes_mean"]) / 60.0, f"Table 6 AoI {row[0]} {supply}", 1)
        different(row[8], float(resp["battery_net_change_mean_j"]), f"Table 6 battery {row[0]} {supply}")
    counts["Table 6"] = (len(header), len(rows))

    # Table 7: freshness-window sensitivity.
    header, rows = table(ms, "7")
    require(len(header) == 7 and len(rows) == 8, ("Table 7 shape", len(header), len(rows)))
    fresh = read_csv(EXT / "freshness_summary.csv")
    contrasts = read_csv(EXT / "freshness_contrasts.csv")
    labels = {"Synthetic": "SYNTHETIC_G20", "T1 winter": "WINTER_G20",
              "T2 spring": "T2_G20", "T3 winter": "T3_G20"}
    for row in rows:
        parts = row[0].rsplit(" ", 1)
        condition, supply = labels[parts[0]], float(parts[1])
        for column, d in zip(range(1, 5), [2, 4, 8, 16]):
            entry = next(r for r in fresh if r["condition"] == condition and float(r["supply"]) == supply
                         and r["controller"] == "JLC-R" and int(r["D"]) == d)
            number(row[column], float(entry["coverage_mean"]), f"Table 7 {row[0]} D{d}", 2)
        entry = next(r for r in fresh if r["condition"] == condition and float(r["supply"]) == supply
                     and r["controller"] == "JLC-R" and int(r["D"]) == 4)
        number(row[5], float(entry["source_p5_mean"]), f"Table 7 P5 {row[0]}", 2)
        contrast = next(r for r in contrasts if r["condition"] == condition and float(r["supply"]) == supply
                        and int(r["D"]) == 4 and r["metric"] == "coverage")
        different(row[6], float(contrast["mean_difference"]), f"Table 7 delta {row[0]}")
    counts["Table 7"] = (len(header), len(rows))

    # Table 8: canopy-coupled stress test.
    header, rows = table(ms, "8")
    require(len(header) == 8 and len(rows) == 8, ("Table 8 shape", len(header), len(rows)))
    canopy = read_csv(EXT / "canopy_summary.csv")
    effects = read_csv(EXT / "canopy_effects.csv")
    for row in rows:
        treatment = row[0]
        for name, column in [("JLC-R", 1), ("Prefix-only", 2), ("Hybrid control", 3), ("PADC-AGE", 4)]:
            entry = next(r for r in canopy if r["treatment"] == treatment and r["controller"] == name)
            number(row[column], float(entry["coverage_pct_mean"]), f"Table 8 {treatment} {name}", 2)
        entry = next(r for r in canopy if r["treatment"] == treatment and r["controller"] == "JLC-R")
        number(row[5], float(entry["source_coverage_p5_pct_mean"]), f"Table 8 P5 {treatment}", 2)
        number(row[6], float(entry["far_coverage_D4_pct_mean"]), f"Table 8 far {treatment}", 2)
        change = next(r for r in effects if r["treatment"] == treatment
                      and r["controller"] == "JLC-R" and r["metric"] == "coverage_pct")
        different(row[7], float(change["mean_change"]), f"Table 8 delta {treatment}")
    counts["Table 8"] = (len(header), len(rows))
    return counts


def check_figures(ms):
    require("figures/fig4_cross_regime.svg" in ms and "figures/fig5_supply_scan.svg" in ms
            and "figures/fig7_canopy.svg" in ms
            and "Repository Figure R1" not in ms and "Repository Figure R2" not in ms,
            "Self-contained extension figure declarations")
    expected = {
        "fig4_cross_regime": ("cross_regime_absolute.csv", "cross_regime_comparison.csv"),
        "fig5_supply_scan": ("supply_scan_summary.csv", "supply_scan_thresholds.json"),
        "fig6_freshness": ("freshness_contrasts.csv",),
        "fig7_canopy": ("canopy_summary.csv", "canopy_effects.csv"),
    }
    checked = 0
    for stem, sources in expected.items():
        for suffix in [".pdf", ".svg"]:
            require((FIGURES / (stem + suffix)).is_file(), f"Missing figure {stem}{suffix}")
        record = json.loads((AUDIT / f"{stem}_data.json").read_text(encoding="utf-8"))
        for name in sources:
            path = FIGURES / name
            if path.is_file():
                continue
            path = EXT / name
            require(path.is_file(), f"Missing source {name}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            stored = [v for k, v in record.items() if k.endswith("sha256") and isinstance(v, str)]
            require(digest in stored, f"Figure data hash mismatch {stem} <- {name}")
            checked += 1
    return checked


def check_claims(ms):
    for token in ['candidate engineering references','normalized supply axis','solar-powered open-field soil-moisture and microclimate monitoring','reduced-form transmittance--attenuation parameterization','Stages I--III specify exploratory transmittance and attenuation ranges','Extensions use nominal paired 95% intervals','Rescoring at $D=4$ reproduces','hardware and protocol validation']:
        require(token in ms,token)
    for bad in ['achieves the 70% target','reaches the 80% target','field deployment of JLC-R']:
        require(bad not in ms,bad)
    return {'extension_exploratory':True,'candidate_reference_qualified':True,'field_boundary':True}


def check(ms):
    return {"tables": check_tables(full_table_view(ms)), "figure_sources": check_figures(ms), "claims": check_claims(ms)}
