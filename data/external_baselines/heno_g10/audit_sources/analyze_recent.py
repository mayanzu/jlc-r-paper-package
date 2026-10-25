"""Verify both recent-control blocks and recompute the fixed 16-test family.

The independent unit is one seed within one weather/supply setting. All
observations are retained; repeated conditions are not pooled as replicates.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone

import numpy as np
import scipy

from helpers import RESULTS, sha, save
from validation_stats import estimate, holm

METHODS = ['JLC-R', 'POINT-JL', 'JLC-R-FIXED', 'HENO-DC', 'PADC-DC']
FIELDS = ['coverage_pct', 'night_off_pct', 'aoi_mean_minutes', 'consumed_j',
          'source_coverage_p5_pct', 'mean_listen_fraction']


def load_verified(out):
    rows = []
    block_checks = {}
    for name, count in [('heno', 192), ('padc', 48)]:
        directory = out/name
        meta = json.loads((directory/'provenance.json').read_text(encoding='utf-8'))
        if not meta.get('completed_utc') or meta['completed_runs'] != count:
            raise ValueError(f'{name}: incomplete ({meta["completed_runs"]}/{count})')
        for rel, value in meta['file_sha256'].items():
            path = directory/rel
            if path.exists() and sha(path) != value:
                raise ValueError(f'{name}: recorded output changed: {rel}')
        sources_verified = 0
        for rel, value in meta['source_sha256'].items():
            path = directory/'execution_sources'/rel
            if path.exists():
                if sha(path) != value:
                    raise ValueError(f'{name}: execution source changed: {rel}')
                sources_verified += 1
        if sha(directory/'design.json') != meta['design_sha256']:
            raise ValueError(f'{name}: design changed')
        spec = directory/meta['design']['specification']
        if sha(spec) != meta['spec_sha256']:
            raise ValueError(f'{name}: specification changed')
        with (directory/'metrics.csv').open(encoding='utf-8-sig', newline='') as f:
            block = list(csv.DictReader(f))
        if len(block) != count:
            raise ValueError(f'{name}: metric row count')
        inputs_verified = 0
        for digest in sorted({r['physical_sha256'] for r in block}):
            path = directory/'inputs'/(digest+'.npz')
            if path.exists():
                with np.load(path, allow_pickle=False) as arrays:
                    raw = b''.join(np.ascontiguousarray(arrays[k], dtype='<f8').tobytes()
                                   for k in ['harvest', 'observed', 'positions', 'shade'])
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise ValueError(f'{name}: physical input digest')
                inputs_verified += 1
        for row in block:
            row['block'] = name
            for field in ['unsensed', 'delivered', 'expired', 'overflow', 'outstanding']:
                row[field] = int(row[field])
            if sum(row[k] for k in ['unsensed', 'delivered', 'expired',
                                    'overflow', 'outstanding']) != 100*96*14:
                raise ValueError('Demand partition failed')
            for field in ['max_hold_violation_j', 'max_node_energy_error_j']:
                if abs(float(row[field])) >= 1e-8:
                    raise ValueError(field)
            if int(row['max_slot_violation']) or abs(float(row['max_energy_balance_error_j'])) >= 1e-6:
                raise ValueError('Physical resource audit failed')
        rows.extend(block)
        block_checks[name] = dict(runs=count, metric_sha256=sha(directory/'metrics.csv'),
                                 inputs_verified=inputs_verified,
                                 execution_sources_verified=sources_verified)
    index = {}
    for row in rows:
        key = row['condition'], float(row['supply']), int(row['seed']), row['method']
        if key in index:
            raise ValueError('Duplicate condition/seed/method')
        index[key] = row
    seeds = sorted({int(r['seed']) for r in rows})
    if seeds != [120101+101*k for k in range(12)]:
        raise ValueError('Seed set differs from fixed design')
    for condition in ['SYNTHETIC', 'MEASURED']:
        for supply in [1., .7]:
            for seed in seeds:
                group = [index[(condition, supply, seed, method)] for method in METHODS]
                for field in ['physical_sha256', 'forecast_sha256']:
                    if len({r[field] for r in group}) != 1:
                        raise ValueError(f'Unmatched {field}: {condition}/{supply}/{seed}')
    return rows, index, seeds, block_checks


def calculate(out):
    rows, index, seeds, checks = load_verified(out)
    summary, paired, source = [], [], []
    for condition in ['SYNTHETIC', 'MEASURED']:
        for supply in [1., .7]:
            for method in METHODS:
                for field in FIELDS:
                    values = [float(index[condition, supply, s, method][field]) for s in seeds]
                    summary.append(dict(condition=condition, supply=supply, method=method,
                                        metric=field, **estimate(values)))
            for method in METHODS[1:]:
                for field in FIELDS:
                    values = [float(index[condition, supply, s, 'JLC-R'][field]) -
                              float(index[condition, supply, s, method][field]) for s in seeds]
                    primary = field == 'coverage_pct'
                    paired.append(dict(condition=condition, supply=supply,
                                       contrast='JLC-R minus '+method, metric=field,
                                       primary=primary, **estimate(values, family=16 if primary else 1)))
                    source.extend(dict(condition=condition, supply=supply, seed=s,
                                       comparator=method, metric=field, difference=v)
                                  for s, v in zip(seeds, values))
    family = [r for r in paired if r['primary']]
    if len(family) != 16:
        raise ValueError('Incomplete primary comparison family')
    holm(family)
    for row in paired:
        if not row['primary']:
            row.update(p_holm='', family_size='', simultaneous_low='', simultaneous_high='')
    return rows, summary, paired, source, checks


def check_table(path, expected):
    with path.open(encoding='utf-8-sig', newline='') as f:
        observed = list(csv.DictReader(f))
    if len(observed) != len(expected):
        raise ValueError(f'{path.name}: row count')
    for a, b in zip(observed, expected):
        for key, value in b.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if not np.isclose(float(a[key]), value, rtol=1e-11, atol=1e-11):
                    raise ValueError(f'{path.name}: {key}')
            elif a.get(key, '') != str(value):
                raise ValueError(f'{path.name}: {key}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=RESULTS/'recent_baselines')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    rows, summary, paired, source, checks = calculate(out)
    tables = {'metrics.csv': rows, 'summary.csv': summary,
              'paired.csv': paired, 'paired_source.csv': source}
    if args.check:
        for name, values in tables.items():
            check_table(out/name, values)
        print('Recent controls verified: 240 runs, 48 matched inputs, 12 seeds/cell, 16 primary tests.')
        return
    for name, values in tables.items():
        save(out/name, values)
    components = {name: json.loads((out/name/'provenance.json').read_text(encoding='utf-8'))
                  for name in ['heno', 'padc']}
    provenance = dict(stage='assembled_recent_duty_control_comparison',
                      assembled_utc=datetime.now(timezone.utc).isoformat(),
                      completed_runs=240, planned_runs=240,
                      completed_utc=max(v['completed_utc'] for v in components.values()),
                      scope='Assembly of two recorded execution blocks; no new trajectories',
                      block_provenance_sha256={name: sha(out/name/'provenance.json')
                                               for name in components},
                      file_sha256={name: sha(out/name) for name in tables})
    (out/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n', encoding='utf-8')
    audit_dir = out/'audit_sources'
    audit_dir.mkdir(exist_ok=True)
    for name in ['analyze_recent.py', 'validation_stats.py']:
        shutil.copy2(Path(__file__).parent/name, audit_dir/name)
    audit = dict(runs=240, independent_seeds_per_cell=12, primary_family_size=16,
                 exclusions=0, paired_input_groups=48, blocks=checks,
                 interpretation='Recent source-rule adapters in a common executor; '
                                'not complete published MAC reproductions',
                 numpy=np.__version__, scipy=scipy.__version__,
                 source_sha256={p.name: sha(p) for p in audit_dir.glob('*.py')},
                 output_sha256={name: sha(out/name) for name in tables})
    (out/'audit.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(audit, indent=2))
    for row in paired:
        if row['primary']:
            print(row['condition'], row['supply'], row['contrast'],
                  '%.3f [%.3f, %.3f] Holm p=%.5g' %
                  (row['mean'], row['ci95_low'], row['ci95_high'], row['p_holm']))


if __name__ == '__main__':
    main()
