"""Execution and serialization shared by gated development and formal runs."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from mechanism_counters import InstrumentedAblation
from relay_ablation_adapter import HERE, PROJECT, SIM, RelayAblationAdapter
from current_io import load_config, build_scenario
from validation_model import StreamingBank

EXT = PROJECT / 'code/experiments/v6_4_agricultural_extension'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_config(name):
    return json.loads((HERE / 'configs' / name).read_text(encoding='utf-8'))


def setup(condition, seed, supply, treatment='C0', rounds=None):
    design = json.loads((SIM / 'current_design.json').read_text(encoding='utf-8'))
    cond = next(v for v in design['conditions'] if v['name'] == condition)
    cfg = load_config(cond)
    expected = dict(nodes=100,area_m=300.,round_seconds=900,packet_bits=4000,
        deadline_rounds=4,battery_j=4.,initial_battery_fraction=.75,reserve_j=.15,
        forecast_rounds=96,period_rounds=4,sync_interval_s=200,guard_listen_s=.02,
        hyb_thin_scale=.60,hyb_exit_scale=.70)
    assert all(cfg[k]==v for k,v in expected.items()), 'Physical configuration drift'
    assert cfg['cluster_cols']*cfg['cluster_rows']==12
    sc = build_scenario(cfg, seed, 14, supply, cond)
    if treatment != 'C0':
        if str(EXT) not in sys.path:
            sys.path.insert(0, str(EXT))
        from extension_core import apply_canopy
        cfg, _ = apply_canopy(cfg, sc, seed, treatment)
    if rounds is not None:
        sc.rounds = rounds
    return cfg, sc, StreamingBank(sc)


def summarize(sim, metrics, case):
    far = sim.far_source
    count = int(far.sum())
    per_source = sim.source_fresh * 100 / sim.sc.rounds
    row = dict(case, **metrics)
    row.update(configuration=sim.configuration, far_sources=count,
        far_source_time_denominator=count * sim.sc.rounds,
        far_coverage_pct=float(per_source[far].mean()) if count else None,
        far_aoi_mean_minutes=float(sim.source_aoi_sum[far].mean() / sim.sc.rounds) if count else None,
        far_delivered_samples=int(sim.source_delivered[far].sum()),
        far_expired_samples=int(sim.source_expired[far].sum()),
        far_expired_at_relay_samples=int(sim.source_expired_relay[far].sum()),
        far_relay_loss_events=int(sum(sim.fate_counts.values())),
        source_coverage_sd_pct=float(per_source.std(ddof=0)),
        source_time_denominator=sim.n * sim.sc.rounds,
        battery_min_observed_j=min(v['battery_min_j'] for v in sim.resource_records),
        battery_max_observed_j=max(v['battery_max_j'] for v in sim.resource_records))
    row.update({'event_' + k: v for k, v in sim.events.items()})
    row.update({'relay_loss_' + k: int(v) for k, v in sim.fate_counts.items()})
    requests = sim.events['requests_all']
    member_requests = sim.events['member_ch_requests']
    holds = sim.events['holds_created']
    ties = sim.events['staleness_comparison_opportunities']
    row.update(events_per_1000_demand_denominator=sim.n * sim.sc.rounds,
        transit_rejects_per_1000_member_requests=1000 * sim.events['reject_transit_protect'] / member_requests if member_requests else None,
        post_response_rejects_per_1000_requests=1000 * sim.events['post_response_rejections'] / requests if requests else None,
        committed_successes_per_1000_holds=1000 * sim.events['committed_hop_successes'] / holds if holds else None,
        staleness_change_rate=sim.events['staleness_changed_selection'] / ties if ties else None,
        reactive_node_period_fraction=sim.events['reactive_node_periods'] / (sim.n * len(range(0, sim.sc.rounds, sim.c['period_rounds']))),
        ch_reactive_period_fraction=sim.events['ch_reactive_periods'] / sim.events['ch_plan_periods'])
    return row


def execute(case, output_dir):
    start = time.perf_counter()
    cfg, sc, bank = setup(case['condition'], case['seed'], case['supply'], case['treatment'])
    switches = read_config('factorial_matrix.json')[case['configuration']]
    sim = InstrumentedAblation(cfg, sc, bank, **switches)
    try:
        metrics = sim.run()
    except Exception:
        failure = dict(case=case, round=int(sim.t), physical_config=cfg,
            last_rounds=sim.logs[-20:], battery=sim.battery.tolist(),
            quota=sim.quota.tolist(), slots_left=sim.slots_left.tolist(),
            forward_holds=sim.forward_holds.tolist(), forward_guard_holds=sim.forward_slot_holds.tolist(),
            holds={str(k): list(v) for k,v in sim.holds.items()},
            queues=[[vars(p) for p in q] for q in sim.queues], events=dict(sim.events))
        name = '{condition}_s{supply}_{treatment}_{seed}_{configuration}'.format(**case)
        with gzip.open(Path(output_dir)/(name+f'_failure_{time.time_ns()}.json.gz'),'wt',encoding='utf-8') as stream:
            json.dump(failure,stream,default=lambda v:v.item())
        raise
    assert metrics['max_hold_violation_j'] <= 1e-8
    assert metrics['max_slot_violation'] == 0
    assert metrics['max_energy_balance_error_j'] <= 1e-6
    assert metrics['max_node_energy_error_j'] <= 1e-8
    assert metrics['generated'] + metrics['unsensed'] == sim.n * sc.rounds
    assert metrics['generated'] == sum(metrics[k] for k in ['delivered', 'expired', 'overflow', 'outstanding'])
    assert all(0 <= r['battery_min_j'] <= r['battery_max_j'] <= cfg['battery_j'] for r in sim.resource_records)
    row = summarize(sim, metrics, case)
    row['runtime_seconds'] = time.perf_counter() - start
    raw = dict(case=case, physical_config=cfg, metrics=row,
        source_positions_m=sc.pos.tolist(), sink_position_m=sc.sink.tolist(),
        events=dict(sim.events), relay_fate_events=dict(sim.fate_counts),
        ch_credit_periods=sim.plan_records, rounds=sim.logs,
        resource_audit=sim.resource_records,
        source_fresh=sim.source_fresh.tolist(), source_aoi_sum_minutes=sim.source_aoi_sum.tolist(),
        source_delivered=sim.source_delivered.tolist(), source_expired=sim.source_expired.tolist(),
        source_expired_at_relay=sim.source_expired_relay.tolist(),
        source_relay_loss_events={str(k): dict(v) for k, v in sim.source_fate_counts.items()},
        final_battery=sim.battery.tolist(), final_forward_holds=sim.forward_holds.tolist(),
        final_forward_guard_holds=sim.forward_slot_holds.tolist())
    name = '{condition}_s{supply}_{treatment}_{seed}_{configuration}'.format(**case)
    path = Path(output_dir) / (name + '.json.gz')
    with gzip.open(path, 'wt', encoding='utf-8') as stream:
        json.dump(raw, stream, ensure_ascii=False, default=lambda v: v.item())
    return row
