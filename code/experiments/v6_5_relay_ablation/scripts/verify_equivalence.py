"""Gate C: exact endpoint replication, including execution arrays and records."""
import gc
import hashlib
import json
from pathlib import Path
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from experiment import HERE, PROJECT, setup, sha, InstrumentedAblation
from v63_model import RelayRepairHYB
from v6_model import HYBSimulator
from validation_model import StreamingBank


class CachedBank:
    """Read-only memoization of the exogenous forecast, permitting exact replay."""
    def __init__(self, sc):
        self.inner = StreamingBank(sc)
        self.cache = {}
        self.entries = self

    def __getitem__(self, t):
        if t not in self.cache:
            self.cache[t] = self.inner[t]
        return self.cache[t]

    def __getattr__(self, name):
        return getattr(self.inner, name)


ARRAYS = ['battery', 'diagnostic_data', 'fdc_data', 'local_forwarded_birth',
          'source_fresh', 'latest', 'forward_holds', 'forward_slot_holds',
          'slots_left', 'sample_status', 'extra', 'quota', 'credit', 'hyb_latched']
ADDED = ['ablation_configuration', 'transit_margin_on', 'two_slot_gate_on', 'staleness_tie_on']
V63 = ['v63_mechanism', 'transit_protect_denials', 'mc_allowance_grants']


def compare(condition, supply, endpoint):
    cfg, sc, _ = setup(condition, 160101, supply)
    bank = CachedBank(sc)
    frozen = (RelayRepairHYB(dict(cfg), sc, bank) if endpoint == 'A111'
              else HYBSimulator(dict(cfg), sc, bank))
    fm = frozen.run()
    enabled = endpoint == 'A111'
    new = InstrumentedAblation(dict(cfg), sc, bank, enabled, enabled, enabled)
    nm = new.run()
    for key in ADDED + ([] if enabled else V63):
        nm.pop(key, None)
    assert fm == nm, {k: (fm.get(k), nm.get(k)) for k in set(fm) | set(nm) if fm.get(k) != nm.get(k)}
    assert frozen.logs == new.logs
    assert frozen.holds == new.holds and frozen.hold_slots == new.hold_slots
    for name in ARRAYS:
        np.testing.assert_array_equal(getattr(frozen, name), getattr(new, name), err_msg=name)
    assert [[vars(p) for p in q] for q in frozen.queues] == [[vars(p) for p in q] for q in new.queues]
    import csv
    rows = list(csv.DictReader((PROJECT / 'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv').open()))
    reference = next(r for r in rows if r['condition'] == condition and float(r['supply']) == supply
                     and int(r['seed']) == 160101 and r['method'] == ('JLC-R-HYB-V63' if enabled else 'JLC-R-HYB'))
    fields = ['coverage_pct', 'aoi_mean_minutes', 'source_coverage_p5_pct', 'night_off_pct', 'consumed_j']
    deviations = {k: float(fm[k]) - float(reference[k]) for k in fields}
    assert all(v == 0 for v in deviations.values()), deviations
    return dict(endpoint=endpoint, condition=condition, supply=supply, seed=160101,
        rounds=sc.rounds, compared_metrics=len(fm), arrays=ARRAYS,
        round_logs_exact=True, queues_and_holds_exact=True,
        published_deviations=deviations, maximum_numeric_deviation=0,
        max_energy_balance_error_j=fm['max_energy_balance_error_j'])


if __name__ == '__main__':
    records = []
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(compare,cond,supply,endpoint):(cond,supply,endpoint)
            for cond,supply in [('WINTER_G20',1.0),('T2_G20',1.0),('T3_G20',.7)]
            for endpoint in ['A111','A000']}
        for future in as_completed(futures):
            records.append(future.result())
            print(*futures[future], 'EXACT', round(time.perf_counter()-start,1),'s elapsed',flush=True)
    records.sort(key=lambda r:(r['condition'],r['supply'],r['endpoint']))
    report = dict(status='PASS', comparisons=records, source_sha256={p.name: sha(p) for p in
        [HERE / 'src/relay_ablation_adapter.py', HERE / 'src/mechanism_counters.py', Path(__file__)]})
    (HERE / 'audit/equivalence_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'audit/equivalence_audit.md').write_text('# Gate C: exact frozen equivalence\n\n'
        'PASS: A111 and A000 each reproduce their actual frozen controller on three full 14-day cells '
        '(seed 160101): T1/1.0, T2/1.0, T3/0.7. All common scalar metrics, 14 execution arrays, '
        'every round record, final queues and holds are exactly equal. Five published service/energy '
        'metrics also have zero difference from the retained confirmation CSV. '
        'No floating-point waiver was used. See equivalence_audit.json.\n', encoding='utf-8')
