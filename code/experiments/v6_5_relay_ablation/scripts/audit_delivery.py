"""Read-only independent completeness, raw-hash and conservation audit."""
import gzip
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE,PROJECT,read_config,sha


def audit():
    original=json.loads((HERE/'audit/frozen_assets_before.json').read_text())
    assert all(sha(PROJECT/name)==expected for name,expected in original.items())
    freeze=json.loads((HERE/'audit/execution_freeze.json').read_text())
    assert all(sha(PROJECT/name)==expected for name,expected in freeze['files_sha256'].items())
    rows=pd.read_csv(HERE/'results/formal_runs.csv')
    conditions=read_config('conditions.json')
    expected={(c['condition'],c['supply'],c['treatment'],s,a) for c in conditions['main']+conditions['canopy']
              for s in read_config('seeds.json')['formal'] for a in read_config('factorial_matrix.json')}
    actual=set(map(tuple,rows[['condition','supply','treatment','seed','configuration']].to_numpy()))
    assert expected==actual and len(rows)==len(expected)==864
    manifest={}
    max_balance=0.
    failure_manifest={}
    for path in sorted((HERE/'results/raw').glob('*.json.gz')):
        if '_failure_' in path.name:
            failure_manifest[path.relative_to(HERE).as_posix()]=sha(path)
            continue
        manifest[path.relative_to(HERE).as_posix()]=sha(path)
        with gzip.open(path,'rt',encoding='utf-8') as f:
            raw=json.load(f)
        m=raw['metrics'];cfg=raw['physical_config'];case=raw['case']
        assert len(raw['rounds'])==len(raw['resource_audit'])==1344
        assert len(raw['ch_credit_periods'])==12*336
        assert m['generated']+m['unsensed']==100*1344
        assert m['generated']==sum(m[k] for k in ['delivered','expired','overflow','outstanding'])
        assert m['max_slot_violation']==0 and m['max_hold_violation_j']<=1e-8
        assert m['max_energy_balance_error_j']<=1e-6 and m['max_node_energy_error_j']<=1e-8
        max_balance=max(max_balance,m['max_energy_balance_error_j'])
        assert cfg['guard_listen_s']==.02 and cfg['sync_interval_s']==200
        assert m['far_source_time_denominator']==1344*m['far_sources']
        assert np.isclose(np.sum(raw['source_fresh'])/(100*1344)*100,m['coverage_pct'],atol=1e-12,rtol=0)
        positions=np.asarray(raw['source_positions_m']);sink=np.asarray(raw['sink_position_m'])
        far=np.hypot(positions[:,0]-sink[0],positions[:,1]-sink[1])>=200
        assert int(far.sum())==m['far_sources']
        assert np.isclose(np.asarray(raw['source_fresh'])[far].sum()/m['far_source_time_denominator']*100,m['far_coverage_pct'],atol=1e-12,rtol=0)
        far_aoi=np.mean(raw['source_aoi_sum_minutes'])/1344
        assert np.isclose(far_aoi,m['aoi_mean_minutes'],rtol=0,atol=1e-9)
        key=(case['condition'],case['supply'],case['treatment'],case['seed'],case['configuration'])
        assert key in expected
        tab=rows[(rows.condition==key[0])&(rows.supply==key[1])&(rows.treatment==key[2])&(rows.seed==key[3])&(rows.configuration==key[4])].iloc[0]
        for field in ['coverage_pct','far_coverage_pct','source_coverage_p5_pct','aoi_mean_minutes','night_off_pct','consumed_j']:
            assert np.isclose(float(tab[field]),m[field],atol=1e-10,rtol=1e-14),(path,field)
    assert len(manifest)==864
    primary=pd.read_csv(HERE/'results/primary_tests.csv')
    assert list(primary.hypothesis)==['H1','H2','H3','H4'] and (primary.n==12).all()
    paired=pd.read_csv(HERE/'results/paired_effects.csv')
    assert set(paired.effect)=={'T','R','S','TR','TS','RS','TRS','Bundle','Loss_T','Loss_R','Loss_S'}
    # Recompute contrasts independently from the eight scalar records.
    for keys,g in rows.groupby(['condition','supply','treatment','seed']):
        for metric in ['far_coverage_pct','source_coverage_p5_pct','coverage_pct','aoi_mean_minutes']:
            y=g.set_index('configuration')[metric]
            values={'Bundle':y.A111-y.A000}
            for effect in ['T','R','S','TR','TS','RS','TRS']:
                ix=['TRS'.index(v)+1 for v in effect]
                values[effect]=sum(np.prod([1 if label[k]=='1' else -1 for k in ix])*value for label,value in y.items())/2**(3-len(effect))
            p=paired[(paired.condition==keys[0])&(paired.supply==keys[1])&(paired.treatment==keys[2])&(paired.seed==keys[3])&(paired.metric==metric)].set_index('effect').value
            for effect,value in values.items():
                assert np.isclose(p[effect],value,atol=1e-10,rtol=1e-13)
    report=dict(status='PASS',planned=864,completed=864,main_executions=768,canopy_executions=96,
        formal_seeds=12,raw_files=len(manifest),old_assets_unchanged=len(original),
        execution_snapshot_commit=freeze['snapshot_git_commit'],
        max_physical_energy_balance_error_j=max_balance,
        guard_violations=0,resource_hold_violations=0,
        errors_retained=len(list((HERE/'results/errors').glob('*.json'))) if (HERE/'results/errors').exists() else 0,
        failure_state_traces_retained=len(failure_manifest),
        primary_test_family=4,primary_independent_unit='network seed',all_factorial_interactions=True,
        original_confirmation_inference_unchanged=True)
    (HERE/'audit/raw_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (HERE/'audit/failure_trace_manifest.json').write_text(json.dumps(failure_manifest,indent=2)+'\n')
    (HERE/'audit/final_ablation_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (HERE/'audit/final_ablation_audit.md').write_text('# Final relay-ablation audit\n\n'+json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    audit()
