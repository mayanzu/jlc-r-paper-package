"""Regenerate availability evidence from delivered-birth matrices; never simulate."""
from pathlib import Path
import csv,json,statistics,sys,math
import numpy as np
from scipy.stats import t
from paths import ROOT,AUDIT

ID='reliability_20261025'
METRICS=['D60_longest_gap_source_median_minutes','D60_longest_gap_source_p95_minutes',
 'D60_sources_any_gap_over_240min_pct','D60_far_sources_any_gap_over_240min_pct',
 'D60_events_over_240min_per_100_source_days','D60_far_completed_recovery_median_minutes',
 'D60_far_right_censored_recovery_pct','D240_coverage_pct']

def write(path,rows):
    rows=list(rows);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def reproduce(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(AUDIT))
    from check_submission_strengthening import independent_scores,sha
    base=ROOT/'code/experiments/v6_4_agricultural_extension'
    protocol=json.loads((base/f'{ID}_protocol.json').read_text(encoding='utf-8'))
    raw=base/'results'/f'{ID}_raw';cases=[]
    for f in sorted(raw.glob('*.npz')):
        meta=json.loads(f.with_suffix('.json').read_text(encoding='utf-8'))
        assert sha(f)==meta['raw_sha256']
        with np.load(f,allow_pickle=False) as data:
            scored=independent_scores(data['latest_birth'],np.linalg.norm(data['positions_m']-data['sink_m'],axis=1)>=200)
        cases.append({**{k:meta[k] for k in ['condition','supply','seed','method']},**scored})
    assert len(cases)==144
    write(out/'rescored_cases.csv',cases);summary=[];table=[]
    display={'WINTER_G20':'T1 / 0.7','T3_G20':'T3 / 0.7','T2_G20':'T2 / 1.0'}
    for condition in protocol['conditions']:
        selected=[r for r in cases if r['condition']==condition['condition']]
        for metric in METRICS:
            candidate={r['seed']:r[metric] for r in selected if r['method']=='JLC-R'}
            for method in protocol['methods']:
                values={r['seed']:r[metric] for r in selected if r['method']==method}
                finite=[v for v in values.values() if v is not None]
                delta=[candidate[s]-v for s,v in values.items() if v is not None and candidate[s] is not None]
                mean=statistics.mean(delta) if delta else None
                half=float(t.ppf(.975,len(delta)-1)*statistics.stdev(delta)/math.sqrt(len(delta))) if len(delta)>1 else None
                summary.append(dict(condition=condition['condition'],supply=condition['supply'],metric=metric,
                    method=method,n=len(finite),mean=statistics.mean(finite) if finite else None,paired_n=len(delta),
                    jlcr_minus_comparator=mean,ci95_low=mean-half if half is not None else None,
                    ci95_high=mean+half if half is not None else None))
        for method in protocol['methods']:
            rs=[r for r in selected if r['method']==method]
            cols=['D60_longest_gap_source_median_minutes','D60_longest_gap_source_p95_minutes',
                  'D60_sources_any_gap_over_240min_pct','D60_far_completed_recovery_median_minutes',
                  'D60_far_right_censored_recovery_pct']
            vals=[statistics.mean(r[c] for r in rs if r[c] is not None) for c in cols]
            vals=[vals[0]/60,vals[1]/60,vals[2],vals[3]/60,vals[4]]
            table.append(dict(condition=display[condition['condition']],controller=method.replace('Hybrid control','JLC-Core'),
                median_longest_gap_h=vals[0],p95_longest_gap_h=vals[1],sources_gap_over_4h_pct=vals[2],
                completed_far_recovery_h=vals[3],far_right_censored_pct=vals[4]))
    write(out/'reliability_summary.csv',summary);write(out/'Main_Table5_recomputed.csv',table)
    return {'cases':144,'summary_rows':96,'main_table_rows':12,'source':'144 original delivered-birth matrices',
            'new_simulations':0,'output':str(out)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists(),'Use a new output directory';print(json.dumps(reproduce(a.output),indent=2))
