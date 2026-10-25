"""Recompute all V3 seed-paired tables and audit exact local evidence."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
import numpy as np
from helpers import ROOT, RESULTS, save, sha
from validation_stats import estimate, holm
from expansion_driver import load_config

FIELDS = ['coverage_pct','aoi_mean_minutes','source_coverage_p5_pct','night_off_pct',
          'consumed_j','sync_initial_energy_j','sync_extra_energy_j','slots_available',
          'slots_used','denied','sync_missed_windows','timing_misses',
          'forecast_rmse_j_per_round','issued_extra_credit_j','unused_extra_credit_j']


def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))


def verify(out):
    meta=json.loads((out/'provenance.json').read_text())
    d=meta['design']; rows=read(out/'metrics.csv')
    expected=len(d['seeds'])*len(d['conditions'])*len(d['supplies'])*len(d['policies'])
    assert len(rows)==expected==meta['completed_runs'] and meta.get('completed_utc')
    assert sha(out/'design.json')==meta['design_sha256']
    assert sha(out/d['specification'])==meta['spec_sha256']
    for name,digest in meta['file_sha256'].items():
        assert sha(out/name)==digest,name
    for name,digest in meta['source_sha256'].items():
        assert sha(out/'execution_sources'/name)==digest,name
    index={(r['condition'],float(r['supply']),int(r['seed']),r['method']):r for r in rows}
    assert len(index)==expected
    maxima={f:0. for f in ['max_node_energy_error_j','max_energy_balance_error_j','max_hold_violation_j','max_slot_violation','joint_floor_violations']}
    for r in rows:
        assert sum(int(r[k]) for k in ['unsensed','delivered','expired','overflow','outstanding'])==100*96*d['days']
        for f in maxima:maxima[f]=max(maxima[f],abs(float(r[f])))
        assert float(r['sync_extra_energy_j'])<=8*100*96*d['days']*.020*.056+1e-6
        assert float(r['sync_extra_energy_j'])<=8*float(r['sync_initial_energy_j'])+1e-6
    assert maxima['max_node_energy_error_j']<1e-8
    assert maxima['max_energy_balance_error_j']<1e-6
    assert maxima['max_hold_violation_j']<1e-8
    assert maxima['max_slot_violation']==maxima['joint_floor_violations']==0
    for cond in d['conditions']:
        for supply in d['supplies']:
            for seed in d['seeds']:
                group=[index[cond['name'],supply,seed,p] for p in d['policies']]
                for f in ['physical_sha256','forecast_sha256','clock_sha256']:
                    assert len({r[f] for r in group})==1,f
    digests={r['physical_sha256'] for r in rows}
    for digest in digests:
        with np.load(out/'inputs'/(digest+'.npz')) as a:
            data=b''.join(np.ascontiguousarray(a[k],dtype='<f8').tobytes() for k in ['harvest','observed','positions','shade'])
            assert hashlib.sha256(data).hexdigest()==digest
    return rows,index,d,dict(runs=expected,input_groups=len(digests),execution_sources=len(meta['source_sha256']),**maxima)


def calculate(out):
    rows,index,d,audit=verify(out)
    summary=[]; paired=[]
    for condition in d['conditions']:
        name=condition['name']
        for supply in d['supplies']:
            for method in d['policies']:
                for f in FIELDS:
                    summary.append(dict(condition=name,supply=supply,method=method,metric=f,
                        **estimate([float(index[name,supply,s,method][f]) for s in d['seeds']])))
            pairs=([('JLC-R','JLC-R-NF'),('JLC-R-SA','JLC-R-SA-NF')] if d['stage']=='E5-Floor'
                   else [('JLC-R-SA',m) for m in d['policies'] if m!='JLC-R-SA'])
            for method,reference in pairs:
                for f in FIELDS:
                    primary=(f=='coverage_pct' and (d['stage']=='E5-Floor' or
                             (reference=='PADC-AGE' and name.endswith('G20'))))
                    paired.append(dict(condition=name,supply=supply,method=method,reference=reference,
                        metric=f,primary=int(primary),**estimate([float(index[name,supply,s,method][f])-
                        float(index[name,supply,s,reference][f]) for s in d['seeds']],family=4 if primary else 1)))
    family=[r for r in paired if r['primary']]
    holm(family)
    if d['stage']!='E2-debug':assert len(family)==4
    # Role statistics: within-run means are summarized across seeds, never nodes.
    resources=read(out/'resources.csv'); role_summary=[];role_paired=[]
    means=[r for r in resources if r['kind']=='role_mean']
    ridx={(r['condition'],float(r['supply']),int(r['seed']),r['method'],r['role']):r for r in means}
    rfields=[k for k in means[0] if k not in ['condition','supply','seed','method','stage','kind','role','node_rounds']]
    for condition in d['conditions']:
        for supply in d['supplies']:
            for role in ['member','CH']:
                for method in d['policies']:
                    for f in rfields:
                        if not ridx[condition['name'],supply,d['seeds'][0],method,role].get(f):continue
                        role_summary.append(dict(condition=condition['name'],supply=supply,role=role,
                            method=method,metric=f,**estimate([float(ridx[condition['name'],supply,s,method,role][f]) for s in d['seeds']])))
                if d['stage']=='E5-Floor':
                    for method,reference in [('JLC-R','JLC-R-NF'),('JLC-R-SA','JLC-R-SA-NF')]:
                        for f in rfields:
                            if not ridx[condition['name'],supply,d['seeds'][0],method,role].get(f):continue
                            role_paired.append(dict(condition=condition['name'],supply=supply,role=role,method=method,
                                reference=reference,metric=f,**estimate([float(ridx[condition['name'],supply,s,method,role][f])-
                                float(ridx[condition['name'],supply,s,reference,role][f]) for s in d['seeds']])))
    return summary,paired,role_summary,role_paired,audit


def run_manifest(out):
    meta=json.loads((out/'provenance.json').read_text())
    d=meta['design']
    source_digest=hashlib.sha256(json.dumps(meta['source_sha256'],sort_keys=True).encode()).hexdigest()
    records=[]
    for r in read(out/'metrics.csv'):
        cond=next(c for c in d['conditions'] if c['name']==r['condition'])
        c=load_config(cond);c['no_reference_floor']=r['method'].endswith('-NF')
        climate=('T2' if r['condition'].startswith('T2') else 'T3' if r['condition'].startswith('T3')
                 else 'T1' if r['condition'].startswith('WINTER') else 'Synthetic')
        records.append(dict(experiment_id=d['stage'],run_id=f"{d['stage']}_{r['condition']}_{r['seed']}_{r['supply']}_{r['method']}",
            controller=r['method'],seed=r['seed'],weather_site={'T1':'Table Mountain CO','T2':'Table Mountain CO','T3':'Bondville IL'}.get(climate,'Synthetic'),
            weather_period='2024-04-01/2024-04-17' if climate=='T2' else '2024-01-01/2024-01-17' if climate in ['T1','T3'] else 'seeded synthetic',
            supply_scale=r['supply'],guard_ms=r['guard_ms'],sync_interval_s=r['sync_interval_s'],clock_drift_ppm=r['clock_drift_ppm'] if c.get('joint_sync_execution') else 0,
            jitter_config='uniform +/-8ms plus 1ms turnaround' if c.get('joint_sync_execution') else 'disabled',
            floor_enabled=r['floor_enabled'],planning_mode='fixed' if r['method']=='JLC-R-FIXED' else r['planning_mode'],selector_mode=r['selector_mode'],
            code_version=source_digest,config_hash=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest(),
            input_hash=r['physical_sha256'],forecast_hash=r['forecast_sha256'],clock_hash=r['clock_sha256'],
            fresh_coverage=r['coverage_pct'],mean_aoi_min=r['aoi_mean_minutes'],source_coverage_p5=r['source_coverage_p5_pct'],
            total_energy_j=r['consumed_j'],sync_energy_j=r['sync_energy_j'],night_outage_pct=r['night_off_pct'],
            energy_balance_error=r['max_energy_balance_error_j'],reservation_violations=r['max_hold_violation_j']))
    return records


def table_equal(path, rows):
    old=read(path)
    assert len(old)==len(rows),str(path)
    for a,b in zip(old,rows):
        for k,v in b.items():
            if isinstance(v,(int,float)):
                assert np.isclose(float(a[k]),v,rtol=1e-10,atol=1e-10),(path,k,a[k],v)
            else:assert a[k]==str(v),(path,k)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    summary,paired,role_summary,role_paired,audit=calculate(args.output)
    tables={'summary.csv':summary,'paired.csv':paired,'role_summary.csv':role_summary,
            'run_manifest.csv':run_manifest(args.output)}
    if role_paired:tables['role_paired.csv']=role_paired
    for name,rows in tables.items():
        if args.check:table_equal(args.output/name,rows)
        else:save(args.output/name,rows)
    if not args.check:
        dest=args.output/'audit_sources';dest.mkdir(exist_ok=True)
        for name in ['analyze_strengthening.py','validation_stats.py']:shutil.copy2(ROOT/name,dest/name)
        audit.update(source_sha256={f.name:sha(f) for f in dest.glob('*.py')},
            output_sha256={name:sha(args.output/name) for name in tables},
            independent_unit='network seed; trajectories and supplies not pooled',
            primary_family_size=sum(r['primary'] for r in paired))
        (args.output/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
    for r in paired:
        if r['primary']:print(r['condition'],r['supply'],r['method'],r['reference'],r['mean'],r['ci95_low'],r['ci95_high'],r['p_holm'])


if __name__=='__main__':main()
