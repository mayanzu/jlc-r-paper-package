"""Run only after exact equivalence; formal runs also require pilot and freeze.

Every execution has a fresh exogenous StreamingBank and independent error log.
Completed raw cases are resumed by exact case identity; no seed is substituted.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import gc
import gzip
import json
import os
from pathlib import Path
import sys
import time
import traceback
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from experiment import HERE, PROJECT, read_config, execute, sha


def group_job(cases, out):
    # execute uses the unchanged StreamingBank; no controller or physics patch.
    results = []
    for case in cases:
        name = '{condition}_s{supply}_{treatment}_{seed}_{configuration}'.format(**case)
        path = Path(out) / (name + '.json.gz')
        if path.exists():
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                raw = json.load(f)
            assert raw['case'] == case
            results.append(raw['metrics'])
            continue
        try:
            results.append(execute(case, out))
        except Exception:
            error = dict(case=case, traceback=traceback.format_exc(), time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
            error_dir = HERE / 'results/errors'
            error_dir.mkdir(exist_ok=True)
            suffix = time.time_ns()
            (error_dir / f'{name}_{suffix}.json').write_text(json.dumps(error, indent=2)+'\n')
            results.append(dict(case=case, error=True))
        gc.collect()
    return results


def write_csv(path, rows):
    fields = sorted(set().union(*(r.keys() for r in rows)))
    # Missing event counts mean zero, missing ratios retain their explicit None.
    for row in rows:
        for field in fields:
            if field.startswith('event_') or field.startswith('relay_loss_'):
                row.setdefault(field, 0)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['pilot','formal'], required=True)
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    eq = json.loads((HERE/'audit/equivalence_audit.json').read_text())
    assert eq['status'] == 'PASS'
    for rel, expected in eq['source_sha256'].items():
        folder = 'scripts' if rel == 'verify_equivalence.py' else 'src'
        assert sha(HERE/folder/rel) == expected, f'Repeat equivalence after change: {rel}'
    if args.phase == 'formal':
        assert json.loads((HERE/'audit/pilot_audit.json').read_text())['status'] == 'PASS'
        freeze = json.loads((HERE/'audit/execution_freeze.json').read_text())
        for path, expected in freeze['files_sha256'].items():
            assert sha(PROJECT/path) == expected, path
    conds = read_config('conditions.json')
    seeds = read_config('seeds.json')['development' if args.phase == 'pilot' else 'formal']
    conditions = conds['pilot'] if args.phase == 'pilot' else conds['main']+conds['canopy']
    matrix = read_config('factorial_matrix.json')
    groups = [[dict(c, seed=seed, configuration=variant)]
              for c in conditions for seed in seeds for variant in matrix]
    out = HERE / 'results' / ('pilot_raw' if args.phase == 'pilot' else 'raw')
    out.mkdir(exist_ok=True)
    expected = len(groups)
    rows = []
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(group_job, group, str(out)) for group in groups]
        for index, future in enumerate(as_completed(futures),1):
            rows.extend(future.result())
            good = [r for r in rows if not r.get('error')]
            write_csv(HERE/'results'/f'{args.phase}_runs.csv', sorted(good,key=lambda r:(r['condition'],r['supply'],r['treatment'],r['seed'],r['configuration'])))
            print(f'{args.phase}: {len(good)}/{expected}, groups {index}/{len(groups)}, elapsed {time.perf_counter()-start:.1f}s', flush=True)
    failures = [r for r in rows if r.get('error')]
    report = dict(status='PASS' if len(rows)==expected and not failures else 'FAIL',
                  expected=expected, completed=len(rows)-len(failures), failures=len(failures),
                  runtime_seconds=time.perf_counter()-start)
    if args.phase == 'pilot':
        report['activation'] = {k: sum(r.get('event_'+k,0) for r in rows if not r.get('error')) for k in
            ['t_checks_executed','reject_transit_protect','ch_low_guard_only_demand','r_only_reactive_periods',
             'staleness_comparison_opportunities','staleness_changed_selection']}
    (HERE/'audit'/f'{args.phase}_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    assert report['status']=='PASS', report


if __name__ == '__main__':
    main()
