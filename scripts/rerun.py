"""Explicit simulation mode. Every execution writes only into a new output directory."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import csv,hashlib,json,sys
from paths import ROOT

def read(name):
    with (ROOT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cases(study):
    if study=='reliability':
        plan=json.loads((ROOT/'code/experiments/v6_4_agricultural_extension/reliability_20261025_protocol.json').read_text(encoding='utf-8'))
        return [dict(study=study,condition=c['condition'],supply=c['supply'],seed=seed,method=method) for c in plan['conditions'] for seed in plan['seeds'] for method in plan['methods']]
    if study=='relay_ablation':
        data=read('code/experiments/v6_5_relay_ablation/results/formal_runs.csv')
        return [{'study':study,'condition':r['condition'],'supply':float(r['supply']),'treatment':r['treatment'],'seed':int(r['seed']),'configuration':r['configuration']} for r in data]
    paths={'confirmation':'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv',
        'supply':'code/experiments/v6_4_agricultural_extension/results/supply.csv',
        'freshness':'code/experiments/v6_4_agricultural_extension/results/freshness.csv',
        'canopy':'code/experiments/v6_4_agricultural_extension/results/canopy.csv'}
    if study=='agricultural_extension':return sum((cases(s) for s in ['supply','freshness','canopy']),[])
    aliases={'JLC-R-HYB-V63':'JLC-R','JLC-R-SA':'Prefix-only','JLC-R-HYB':'Hybrid control','PADC-AGE':'PADC-AGE','PADC-AGE+V63':'PADC+relay'}
    return [{'study':study,'condition':r['condition'],'supply':float(r['supply']),'seed':int(r['seed']),
        'method':aliases.get(r['method'],r['method']),'treatment':r.get('canopy_treatment','C0')} for r in read(paths[study])]

def job(payload):
    case,out=payload;out=Path(out)
    if case['study']=='reliability':
        sys.path.insert(0,str(ROOT/'code/experiments/v6_4_agricultural_extension'))
        from reliability_20261025 import execute as record
        return record(tuple(case[k] for k in ['condition','supply','seed','method']),out)
    if case['study']=='relay_ablation':
        sys.path.insert(0,str(ROOT/'code/experiments/v6_5_relay_ablation/src'))
        from experiment import execute
        actual={k:case[k] for k in ['condition','supply','treatment','seed','configuration']}
        return execute(actual,out)
    sys.path.insert(0,str(ROOT/'code/experiments/v6_4_agricultural_extension'))
    from extension_core import run_case
    return run_case(case['study'],case['condition'],case['seed'],case['supply'],case['method'],case['treatment'])

def execute(study,out,workers=1,dry_run=False):
    if study=='mechanisms':
        from mechanisms import execute as execute_mechanisms
        return execute_mechanisms(out,workers,dry_run)
    matrix=cases(study)
    if study=='reliability':
        base=ROOT/'code/experiments/v6_4_agricultural_extension'
        frozen_new=json.loads((base/'results/reliability_20261025_execution_freeze.json').read_text(encoding='utf-8'))
        for file,h in [(base/'reliability_20261025.py',frozen_new['source_sha256']),(base/'reliability_20261025_protocol.json',frozen_new['protocol_sha256'])]:
            assert hashlib.sha256(file.read_bytes()).hexdigest()==h
    # Check all byte-frozen files used by the factorial/current kernel before starting.
    frozen=json.loads((ROOT/'code/experiments/v6_5_relay_ablation/audit/execution_freeze.json').read_text(encoding='utf-8'))
    for name,expected in frozen['files_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    if dry_run:return {'mode':'rerun','study':study,'planned_cases':len(matrix),'first_case':matrix[0],'dry_run':True,'simulations_started':0}
    out=Path(out).resolve()
    assert not out.exists(),'Rerun output must be a new directory'
    assert not out.is_relative_to(ROOT) or out.is_relative_to(ROOT/'outputs'),'Refusing to write into frozen package inputs'
    out.mkdir(parents=True)
    raw=out/'raw';raw.mkdir()
    payload=[(c,str(raw)) for c in matrix]
    if workers==1:iterator=map(job,payload);pool=None
    else:pool=ProcessPoolExecutor(max_workers=workers);iterator=pool.map(job,payload)
    records=[]
    try:
        for row in iterator:
            records.append(row)
            # A fresh per-case record preserves completed work without touching originals.
            (out/f'case_{len(records):04d}.json').write_text(json.dumps(row,default=lambda v:v.item(),indent=2)+'\n',encoding='utf-8')
            print(f'{study}: {len(records)}/{len(matrix)}',flush=True)
    finally:
        if pool:pool.shutdown()
    fields=sorted(set().union(*(r.keys() for r in records)))
    with (out/'rerun_results.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
    return {'study':study,'completed':len(records),'output':str(out),'retained_results_unchanged':True}
