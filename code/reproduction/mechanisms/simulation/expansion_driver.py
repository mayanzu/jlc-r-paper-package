"""Shared non-overwriting driver for the revision expansion studies.

A study design is a JSON file: stage label, specification file, horizon, seeds,
supplies, policies and optional named conditions (each with a config overlay).
Concrete runner scripts supply module-level scenario/simulator hooks. This
module handles input digests, execution-source snapshots, provenance, parallel
execution, traces and deterministic CSV outputs. It never overwrites an
existing output directory.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import csv
import gzip
import hashlib
import json
import platform
import shutil
import time

import numpy as np

from helpers import CODE, RESULTS, ROOT, sha, save, snapshot_sources
from validation_model import StreamingBank, ScenarioV2, DEFAULTS


def load_config(condition=None, extra=None):
    c = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    c.update(DEFAULTS)
    if condition:
        c.update(condition.get('config', {}))
    if extra:
        c.update(extra)
    return c


def _arrays(sc):
    return {k: np.ascontiguousarray(v, dtype='<f8') for k, v in dict(
        harvest=sc.harvest, observed=sc.observed, positions=sc.pos, shade=sc.shade).items()}


def _digest(arrays):
    return hashlib.sha256(b''.join(v.tobytes() for v in arrays.values())).hexdigest()


def store_inputs(out, arrays, digest, key):
    target = out / 'inputs' / (digest + '.npz')
    if target.exists():
        return digest
    stage = out / 'inputs' / (key + '.npz')
    np.savez_compressed(stage, **arrays)
    try:
        stage.replace(target)
    except FileExistsError:
        stage.unlink()
    return digest


def execute(job, design, out, build_scenario, build_simulator, collect):
    name, seed, supply = job
    out = Path(out)
    condition = next(c for c in design['conditions'] if c['name'] == name)
    c = load_config(condition)
    sc = build_scenario(c, seed, design['days'], supply, condition)
    arrays = _arrays(sc)
    digest = _digest(arrays)
    store_inputs(out, arrays, digest, f"{name}_{seed}_s{supply}")
    result = dict(job=list(job), metrics=[], nodes=[], extra=[])
    for policy in design['policies']:
        bank = StreamingBank(sc)
        sim = build_simulator(c, sc, bank, condition, policy)
        started = time.perf_counter()
        row = sim.run()
        ident = dict(condition=name, seed=seed, supply=supply,
                     method=row.get('method', policy), stage=design['stage'])
        row.update(**ident, physical_sha256=digest,
                   forecast_sha256=bank.signature.hexdigest(),
                   runtime_seconds=time.perf_counter() - started)
        result['metrics'].append(row)
        result['nodes'].extend(dict(**ident, **r) for r in sim.node_rows())
        if collect is not None:
            result['extra'].extend(dict(**ident, **r) for r in collect(sim, condition))
        with gzip.open(out / 'traces' / f'{name}_{seed}_s{supply}_{policy}.csv.gz',
                       'wt', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(sim.logs[0]))
            writer.writeheader()
            writer.writerows(sim.logs)
        print(name, seed, supply, policy,
              'C=%.3f off=%.3f' % (row['coverage_pct'], row['night_off_pct']), flush=True)
    return result


def run_study(design_path, output, build_scenario, build_simulator, collect=None,
              workers=6, resume=False, extra_name='extra.csv'):
    design_path = Path(design_path).resolve()
    design = json.loads(design_path.read_text(encoding='utf-8'))
    design.setdefault('conditions', [dict(name='DEFAULT', config={})])
    spec = ROOT / design['specification']
    out = Path(output).resolve()
    planned = len(design['conditions']) * len(design['seeds']) * len(design['supplies']) * len(design['policies'])
    records = []
    if out.exists():
        if not resume:
            raise RuntimeError('Refusing to overwrite existing output: ' + str(out))
        meta = json.loads((out / 'provenance.json').read_text(encoding='utf-8'))
        assert meta['design_sha256'] == sha(design_path) and meta['spec_sha256'] == sha(spec)
        if (out / 'jobs.jsonl.gz').exists():
            with gzip.open(out / 'jobs.jsonl.gz', 'rt', encoding='utf-8') as handle:
                records = [json.loads(line) for line in handle]
    else:
        for child in ['inputs', 'traces', 'execution_sources']:
            (out / child).mkdir(parents=True, exist_ok=False)
        snapshot_sources(out / 'execution_sources')
        shutil.copy2(spec, out / spec.name)
        shutil.copy2(design_path, out / 'design.json')
        meta = dict(started_utc=datetime.now(timezone.utc).isoformat(), planned_runs=planned,
                    config=load_config(), design=design, platform=platform.platform(),
                    python=platform.python_version(), numpy=np.__version__,
                    spec_sha256=sha(spec), design_sha256=sha(design_path),
                    source_sha256={p.relative_to(out / 'execution_sources').as_posix(): sha(p)
                                   for p in (out / 'execution_sources').rglob('*.py')})

    def record():
        meta['completed_runs'] = sum(len(r['metrics']) for r in records)
        (out / 'provenance.json').write_text(json.dumps(meta, indent=2) + '\n', encoding='utf-8')

    done = {tuple(r['job']) for r in records}
    record()
    jobs = [(cond['name'], seed, supply) for cond in design['conditions']
            for seed in design['seeds'] for supply in design['supplies']]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(execute, job, design, str(out),
                               build_scenario, build_simulator, collect) for job in jobs if job not in done]
        for future in as_completed(futures):
            result = future.result()
            with gzip.open(out / 'jobs.jsonl.gz', 'at', encoding='utf-8') as handle:
                handle.write(json.dumps(result) + '\n')
            records.append(result)
            record()
    assert len(records) == len(jobs), (len(records), len(jobs))
    save(out / 'metrics.csv', [r for j in records for r in j['metrics']])
    save(out / 'node_metrics.csv', [r for j in records for r in j['nodes']])
    if collect is not None:
        save(out / extra_name, [r for j in records for r in j['extra']])
    meta.update(completed_utc=datetime.now(timezone.utc).isoformat(),
                file_sha256={p.name: sha(p) for p in out.glob('*.csv')})
    record()
    print('COMPLETE', planned, out, flush=True)
