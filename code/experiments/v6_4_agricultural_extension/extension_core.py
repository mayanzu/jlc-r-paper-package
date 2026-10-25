"""Shared execution core for the JLC-R COMPAG agricultural extension.

The frozen controllers and the frozen physical kernel are imported unchanged.
Only the new, explicitly configured supply multipliers and the exploratory
crop-canopy coupling (``canopy_model``) extend the original model. Every run
uses the same S200/G20 accounting as the 480-execution confirmation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
SIM = PROJECT / "code" / "simulation"
if str(SIM) not in sys.path:
    sys.path.insert(0, str(SIM))

from current_io import ROOT, load_config, build_scenario  # noqa: E402
from validation_model import StreamingBank  # noqa: E402
from jlc_r import JLCR  # noqa: E402
from v63_model import RelayRepairPADCAge  # noqa: E402
from v6_model import HYBSimulator  # noqa: E402
from v4_diagnostics import DiagnosticPADCAge, DiagnosticOptimized  # noqa: E402
from canopy_model import (  # noqa: E402
    STAGE_LAMBDA,
    STAGE_RANGES,
    channel_factor,
    spatial_canopy,
    transmittance,
)

# ---------------------------------------------------------------------------
# Read-only experiment hook for the exploratory canopy channel.
#
# The frozen simulator source is left byte-identical. When (and only when) a
# configuration carries ``canopy_channel_lambda``, the wrapper below rewrites
# ``self.prob`` immediately after the base constructor has computed the
# geometric probability and before any controller builds its reference routes
# or listening profiles. Without that key, behaviour is exactly the frozen one.
# ---------------------------------------------------------------------------
from simulator import Simulator as _FrozenSimulator  # noqa: E402

_FROZEN_SIM_INIT = _FrozenSimulator.__init__


def _canopy_aware_init(self, cfg, scenario, method, agent=None, training=False, seed=0):
    _FROZEN_SIM_INIT(self, cfg, scenario, method, agent, training, seed)
    lam = cfg.get("canopy_channel_lambda")
    if not lam:
        return
    canopy = np.asarray(getattr(scenario, "canopy"), dtype=float)
    if canopy.size == self.n:
        canopy = np.r_[canopy, 0.0]
    self.prob = np.clip(self.prob * channel_factor(canopy, lam),
                        getattr(scenario, "canopy_prob_floor", 0.35), 0.99)


if not getattr(_FrozenSimulator, "_canopy_extension_hook", False):
    _FrozenSimulator.__init__ = _canopy_aware_init
    _FrozenSimulator._canopy_extension_hook = True

DESIGN_PATH = HERE / "extension_design.json"
TREATMENTS = {
    # label: (energy stage or None, channel lambda or None)
    "C0": (None, 0.0),
    "I-C1": ("I", 0.0),
    "II-C1": ("II", 0.0),
    "II-C2": (None, 0.10),
    "II-C3": ("II", 0.10),
    "III-C1": ("III", 0.0),
    "III-C2": (None, 0.20),
    "III-C3": ("III", 0.20),
}
METHODS = {
    "JLC-R": "JLC-R-HYB-V63",
    "Prefix-only": "JLC-R-SA",
    "Hybrid control": "JLC-R-HYB",
    "PADC-AGE": "PADC-AGE",
    "PADC+relay": "PADC-AGE+V63",
}

FIELDS = [
    "task", "condition", "seed", "supply", "canopy_stage", "canopy_treatment",
    "canopy_lambda", "method", "implementation",
    "coverage_pct", "aoi_mean_minutes", "source_coverage_p5_pct", "night_off_pct",
    "source_p5_D2_pct", "source_p5_D4_pct", "source_p5_D8_pct", "source_p5_D16_pct",
    "coverage_D2_pct", "coverage_D4_pct", "coverage_D8_pct", "coverage_D16_pct",
    "far_coverage_D4_pct", "far_source_min_coverage_pct",
    "coverage_first_half_pct", "coverage_second_half_pct",
    "aoi_first_half_minutes", "aoi_second_half_minutes",
    "consumed_j", "harvested_j", "spilled_j", "spill_fraction",
    "base_consumed_j", "comm_consumed_j", "control_j",
    "initial_battery_mean_j", "battery_first_half_mean_j",
    "battery_second_half_mean_j", "battery_end_mean_j", "battery_min_mean_j",
    "generated", "delivered", "expired", "overflow", "unsensed", "outstanding",
    "demand_delivery_pct", "link_success_pct", "off_pct",
    "fdc_activated_node_periods", "fdc_triggered_node_periods",
    "hyb_thin_added_node_periods", "infeasible_node_periods", "node_periods",
    "forecast_infeasible_pct", "transit_protect_denials",
    "grant_denied_events", "forward_reserve_events", "transit_block_events",
    "hold_created", "held_packet_hop_successes",
    "canopy_mean", "transmittance_mean",
    "max_hold_violation_j", "max_slot_violation", "max_energy_balance_error_j",
    "runtime_seconds",
]


def load_design():
    return json.loads(DESIGN_PATH.read_text(encoding="utf-8"))


def condition_by_name(name):
    design = json.loads((ROOT / "current_design.json").read_text(encoding="utf-8"))
    return next(x for x in design["conditions"] if x["name"] == name)


def build_method(label, c, sc, bank):
    impl = METHODS[label]
    if impl == "JLC-R-HYB-V63":
        return JLCR(c, sc, bank, v63_mechanism="relay_repair")
    if impl == "JLC-R-HYB":
        return HYBSimulator(c, sc, bank)
    if impl == "JLC-R-SA":
        return DiagnosticOptimized(c, sc, bank, "JLC-R-SA")
    if impl == "PADC-AGE":
        return DiagnosticPADCAge(c, sc, bank)
    if impl == "PADC-AGE+V63":
        return RelayRepairPADCAge(c, sc, bank, v63_mechanism="relay_repair")
    raise ValueError(label)


def apply_canopy(c, sc, seed, treatment):
    """Attach the shared canopy field and apply the requested treatment."""
    stage, lam = TREATMENTS[treatment]
    canopy = spatial_canopy(sc.pos, seed)
    sc.canopy = canopy
    sc.canopy_prob_floor = 0.35
    c = dict(c)
    c["canopy_channel_lambda"] = float(lam if lam is not None else 0.0)
    if stage is not None:
        transmit = transmittance(canopy, stage)
        sc.solar_scale = sc.solar_scale * transmit
        sc.harvest = sc.harvest * transmit[None, :]
        sc.observed = sc.observed * transmit[None, :]
    sc.canopy_stage = stage or "none"
    sc.canopy_treatment = treatment
    return c, canopy


def summarize(task, condition, seed, supply, method, sim, metrics, canopy_info, runtime, source_by_d):
    logs = sim.logs
    rounds = len(logs)
    half = rounds // 2
    cov = np.array([v["coverage"] for v in logs]) * 100.0
    aoi = np.array([v["aoi_minutes"] for v in logs])
    battery = np.array([v["battery_mean_j"] for v in logs])

    distance = np.hypot(sim.sc.pos[:, 0] - sim.sc.sink[0], sim.sc.pos[:, 1] - sim.sc.sink[1])
    far = distance >= 200.0
    far_cov = float(100.0 * sim.source_fresh[far].sum() / (len(np.flatnonzero(far)) * sim.sc.rounds)) if far.any() else float("nan")
    per_source = 100.0 * sim.source_fresh / sim.sc.rounds
    far_min = float(per_source[far].min()) if far.any() else float("nan")
    p5_by_d = {d: float(np.quantile(100.0 * source_by_d[d] / sim.sc.rounds, 0.05)) for d in (2, 4, 8, 16)}
    assert np.array_equal(source_by_d[4], sim.source_fresh), "per-source D=4 count differs from frozen metric"

    by_role = getattr(sim, "by_role", {})
    def blocked(role, reason):
        return int(by_role.get(role, {}).get("block_" + reason, 0))

    row = {
        "task": task,
        "condition": condition,
        "seed": int(seed),
        "supply": float(supply),
        "canopy_stage": canopy_info.get("stage", "none"),
        "canopy_treatment": canopy_info.get("treatment", "none"),
        "canopy_lambda": float(canopy_info.get("lambda", 0.0)),
        "method": method,
        "implementation": METHODS[method],
        "coverage_pct": float(metrics["coverage_pct"]),
        "aoi_mean_minutes": float(metrics["aoi_mean_minutes"]),
        "source_coverage_p5_pct": float(metrics["source_coverage_p5_pct"]),
        "night_off_pct": float(metrics["night_off_pct"]),
        "source_p5_D2_pct": p5_by_d[2],
        "source_p5_D4_pct": p5_by_d[4],
        "source_p5_D8_pct": p5_by_d[8],
        "source_p5_D16_pct": p5_by_d[16],
        "coverage_D2_pct": float(metrics.get("coverage_D2_pct", np.nan)),
        "coverage_D4_pct": float(metrics.get("coverage_D4_pct", np.nan)),
        "coverage_D8_pct": float(metrics.get("coverage_D8_pct", np.nan)),
        "coverage_D16_pct": float(metrics.get("coverage_D16_pct", np.nan)),
        "far_coverage_D4_pct": far_cov,
        "far_source_min_coverage_pct": far_min,
        "coverage_first_half_pct": float(cov[:half].mean()),
        "coverage_second_half_pct": float(cov[half:].mean()),
        "aoi_first_half_minutes": float(aoi[:half].mean()),
        "aoi_second_half_minutes": float(aoi[half:].mean()),
        "consumed_j": float(metrics["consumed_j"]),
        "harvested_j": float(metrics["harvested_j"]),
        "spilled_j": float(metrics["spilled_j"]),
        "spill_fraction": float(metrics["spilled_j"] / metrics["harvested_j"]) if metrics["harvested_j"] > 0 else 0.0,
        "base_consumed_j": float(metrics.get("base_consumed_j", np.nan)),
        "comm_consumed_j": float(metrics.get("comm_consumed_j", np.nan)),
        "control_j": float(metrics.get("control_j", np.nan)),
        "initial_battery_mean_j": float(sim.initial_node_battery.mean()),
        "battery_first_half_mean_j": float(battery[:half].mean()),
        "battery_second_half_mean_j": float(battery[half:].mean()),
        "battery_end_mean_j": float(battery[-1]),
        "battery_min_mean_j": float(battery.min()),
        "generated": int(metrics["generated"]),
        "delivered": int(metrics["delivered"]),
        "expired": int(metrics["expired"]),
        "overflow": int(metrics["overflow"]),
        "unsensed": int(metrics["unsensed"]),
        "outstanding": int(metrics["outstanding"]),
        "demand_delivery_pct": float(metrics["demand_delivery_pct"]),
        "link_success_pct": float(metrics["link_success_pct"]),
        "off_pct": float(metrics["off_pct"]),
        "fdc_activated_node_periods": int(metrics.get("fdc_activated_node_periods", 0)),
        "fdc_triggered_node_periods": int(metrics.get("fdc_triggered_node_periods", 0)),
        "hyb_thin_added_node_periods": int(metrics.get("hyb_thin_added_node_periods", 0)),
        "infeasible_node_periods": int(metrics.get("infeasible_node_periods", 0)),
        "node_periods": int(metrics.get("node_periods", 0)),
        "forecast_infeasible_pct": float(metrics.get("forecast_infeasible_pct", np.nan)),
        "transit_protect_denials": int(getattr(sim, "transit_protect_denials", 0)),
        "grant_denied_events": blocked("CH", "grant_denied") + blocked("member", "grant_denied"),
        "forward_reserve_events": blocked("CH", "forward_reserve") + blocked("member", "forward_reserve"),
        "transit_block_events": blocked("CH", "transit_protect") + blocked("member", "transit_protect"),
        "hold_created": int(getattr(sim, "stats", {}).get("hold_created", 0)),
        "held_packet_hop_successes": int(getattr(sim, "stats", {}).get("held_packet_hop_successes", 0)),
        "canopy_mean": float(canopy_info.get("mean", 0.0)),
        "transmittance_mean": float(canopy_info.get("transmittance_mean", 1.0)),
        "max_hold_violation_j": float(metrics["max_hold_violation_j"]),
        "max_slot_violation": int(metrics["max_slot_violation"]),
        "max_energy_balance_error_j": float(metrics["max_energy_balance_error_j"]),
        "runtime_seconds": float(runtime),
    }
    return row


def run_case(task, condition, seed, supply, method, treatment="C0", days=None):
    import time

    t0 = time.time()
    design = load_design()
    days = design["days"] if days is None else days
    base = condition_by_name(condition)
    c = load_config(base)
    sc = build_scenario(c, seed, days, supply, base)
    canopy_info = {"stage": "none", "treatment": "C0", "lambda": 0.0,
                   "mean": float("nan"), "transmittance_mean": 1.0}
    if task == "canopy":
        c, canopy = apply_canopy(c, sc, seed, treatment)
        stage, lam = TREATMENTS[treatment]
        canopy_info = {
            "stage": stage or "none",
            "treatment": treatment,
            "lambda": float(lam if lam is not None else 0.0),
            "mean": float(canopy.mean()),
            "transmittance_mean": float(transmittance(canopy, stage).mean()) if stage else 1.0,
        }
    bank = StreamingBank(sc)
    sim = build_method(method, c, sc, bank)
    source_by_d = {d: np.zeros(sim.n, dtype=int) for d in (2, 4, 8, 16)}
    original_round = sim.round

    def observed_round():
        original_round()
        t0 = sim.t - 1
        if t0 < 0:
            return
        ages = np.where(sim.latest >= 0, t0 - sim.latest + 1, t0 + 1)
        for d, counter in source_by_d.items():
            counter += ((sim.latest >= 0) & (ages <= d)).astype(int)

    sim.round = observed_round
    metrics = sim.run()
    return summarize(task, condition, seed, supply, method, sim, metrics, canopy_info, time.time() - t0, source_by_d)
