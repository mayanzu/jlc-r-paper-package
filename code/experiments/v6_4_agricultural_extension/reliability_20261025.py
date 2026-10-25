"""Read-only source-trajectory experiment; frozen controller bytes are unchanged.

Explicit modes: selftest, regression, run, analyze. Only run/regression simulate.
The locked prospective logging design is not part of the original confirmation.
"""
from pathlib import Path
import argparse,csv,hashlib,json,sys,time,traceback,os
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
PROTOCOL=HERE/'reliability_20261025_protocol.json'
ID='reliability_20261025'
RESULTS=HERE/'results'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load():return json.loads(PROTOCOL.read_text(encoding='utf-8'))
def write_json(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def write_csv(path,rows):
    rows=list(rows)
    if not rows:return
    with Path(path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def runs(mask):
    """Half-open maximal True runs, including horizon-censored runs."""
    edges=np.diff(np.r_[False,np.asarray(mask,dtype=bool),False].astype(np.int8))
    return list(zip(np.flatnonzero(edges==1).tolist(),np.flatnonzero(edges==-1).tolist()))

def trajectory_metrics(latest,positions,sink,step_minutes=15):
    latest=np.asarray(latest);T,N=latest.shape
    assert np.all(latest<=np.arange(T)[:,None])
    assert np.all(np.diff(latest.astype(np.int32),axis=0)>=0)
    ages=np.where(latest>=0,np.arange(T)[:,None]-latest+1,np.arange(T)[:,None]+1)
    far=np.linalg.norm(np.asarray(positions)-np.asarray(sink),axis=1)>=200.
    sources=[];episodes=[]
    for D in [4,16]:
        fresh=(latest>=0)&(ages<=D)
        for node in range(N):
            periods=runs(~fresh[:,node]);lengths=[(b-a)*step_minutes for a,b in periods]
            completed=[];right=0;eligible=0
            for a,b in periods:
                left_censored=a==0;right_censored=b==T
                # Recovery is conditional on a previous fresh observation;
                # initialization is not a loss-and-recovery episode.
                if not left_censored:
                    eligible+=1;right+=int(right_censored)
                    if not right_censored:completed.append((b-a)*step_minutes)
                episodes.append(dict(node=node,criterion_minutes=D*step_minutes,start_round=a,end_round_exclusive=b,
                    observed_duration_minutes=(b-a)*step_minutes,left_censored=int(left_censored),
                    right_censored=int(right_censored),far=int(far[node]),
                    recovery_eligible=int(not left_censored),completed_recovery=int(not left_censored and not right_censored)))
            first=np.flatnonzero(fresh[:,node])
            sources.append(dict(node=node,criterion_minutes=D*step_minutes,far=int(far[node]),
                fresh_coverage_pct=float(100*fresh[:,node].mean()),
                longest_observed_unavailability_minutes=max(lengths,default=0),
                events_over_60min=sum(v>60 for v in lengths),events_over_240min=sum(v>240 for v in lengths),
                any_event_over_240min=int(any(v>240 for v in lengths)),
                left_censored_events=sum(a==0 for a,b in periods),right_censored_events=sum(b==T for a,b in periods),
                first_fresh_end_minutes=int((first[0]+1)*step_minutes) if len(first) else None,
                recovery_eligible_episodes=eligible,right_censored_recovery_episodes=right,
                completed_recovery_episodes=len(completed)))
    summary={}
    for D in [60,240]:
        rows=[x for x in sources if x['criterion_minutes']==D]
        far_rows=[x for x in rows if x['far']]
        completed=[x['observed_duration_minutes'] for x in episodes if x['criterion_minutes']==D and x['far'] and x['completed_recovery']]
        eligible=sum(x['recovery_eligible_episodes'] for x in far_rows)
        censored=sum(x['right_censored_recovery_episodes'] for x in far_rows)
        prefix=f'D{D}_'
        summary.update({prefix+'coverage_pct':float(np.mean([x['fresh_coverage_pct'] for x in rows])),
            prefix+'longest_gap_source_median_minutes':float(np.median([x['longest_observed_unavailability_minutes'] for x in rows])),
            prefix+'longest_gap_source_p95_minutes':float(np.quantile([x['longest_observed_unavailability_minutes'] for x in rows],.95)),
            prefix+'sources_any_gap_over_240min_pct':float(100*np.mean([x['any_event_over_240min'] for x in rows])),
            prefix+'far_sources_any_gap_over_240min_pct':float(100*np.mean([x['any_event_over_240min'] for x in far_rows])) if far_rows else None,
            prefix+'events_over_60min_per_100_source_days':float(sum(x['events_over_60min'] for x in rows)/(N*T*step_minutes/1440)*100),
            prefix+'events_over_240min_per_100_source_days':float(sum(x['events_over_240min'] for x in rows)/(N*T*step_minutes/1440)*100),
            prefix+'far_completed_recovery_median_minutes':float(np.median(completed)) if completed else None,
            prefix+'far_completed_recovery_episodes':len(completed),
            prefix+'far_right_censored_recovery_episodes':censored,
            prefix+'far_right_censored_recovery_pct':float(100*censored/eligible) if eligible else None})
    summary['trace_mean_aoi_minutes']=float(ages.mean()*step_minutes)
    return summary,sources,episodes

def execute(case,outdir):
    # Importing the existing builder does not execute a case or change C0 inputs.
    import extension_core as core
    from validation_model import StreamingBank
    condition,supply,seed,method=case
    base=core.condition_by_name(condition);c=core.load_config(base)
    sc=core.build_scenario(c,seed,14,supply,base);sim=core.build_method(method,c,sc,StreamingBank(sc))
    latest=[];max_envelope=0.;original_round=sim.round
    def observe():
        nonlocal max_envelope
        original_round();latest.append(sim.latest.copy())
        actual=sim.listen_profiles[sim.phase(sim.t-1)]
        envelope=float(np.maximum(0,actual[~sim.off]-c['sync_listen_s']).sum()+sim.slots_used.sum()*c['packet_bits']/c['bitrate_bps'])
        max_envelope=max(max_envelope,envelope)
    sim.round=observe
    started=time.perf_counter();metrics=sim.run();elapsed=time.perf_counter()-started
    matrix=np.asarray(latest,dtype=np.int16)
    summary,_,_=trajectory_metrics(matrix,sc.pos,sc.sink)
    assert abs(summary['D60_coverage_pct']-metrics['coverage_pct'])<1e-9
    assert abs(summary['trace_mean_aoi_minutes']-metrics['aoi_mean_minutes'])<1e-8
    assert max_envelope<=99.98
    for k,tol in [('max_hold_violation_j',1e-8),('max_slot_violation',0),('max_node_energy_error_j',1e-8),('max_energy_balance_error_j',1e-6)]:
        if k in metrics:assert float(metrics[k])<=tol,(case,k,metrics[k])
    stem=f'{ID}_{condition}_s{supply:g}_{seed}_{method.replace(" ","_")}'
    target=Path(outdir)/f'{stem}.npz';assert not target.exists()
    np.savez_compressed(target,latest_birth=matrix,positions_m=sc.pos,sink_m=sc.sink,
        round_seconds=np.array(c['round_seconds']),protocol_sha256=np.array(sha(PROTOCOL)))
    row=dict(condition=condition,supply=supply,seed=seed,method=method,runtime_seconds=elapsed,
        max_serial_envelope_s=max_envelope,timing_misses=int(metrics.get('timing_misses',0)),
        raw_file=target.name,raw_sha256=sha(target),**summary)
    for k in ['coverage_pct','aoi_mean_minutes','source_coverage_p5_pct','night_off_pct','consumed_j','generated','unsensed','delivered','expired','overflow','outstanding','max_hold_violation_j','max_slot_violation','max_node_energy_error_j','max_energy_balance_error_j']:
        if k in metrics:row[k]=float(metrics[k])
    write_json(target.with_suffix('.json'),row)
    return row

def selftest():
    assert runs([0,1,1,0,1])==[(1,3),(4,5)]
    # Never-delivered observations do not become fresh merely because age is low.
    latest=np.full((20,2),-1,dtype=int);summary,src,episodes=trajectory_metrics(latest,[[250,0],[0,0]],[0,0])
    assert summary['D60_coverage_pct']==0 and summary['D240_coverage_pct']==0
    assert all(x['longest_observed_unavailability_minutes']==300 for x in src)
    assert all(x['left_censored'] and x['right_censored'] for x in episodes)
    assert summary['D60_far_completed_recovery_median_minutes'] is None
    # Fresh every round gives no outage and age exactly one round.
    latest=np.tile(np.arange(20)[:,None],(1,2));summary,src,episodes=trajectory_metrics(latest,[[250,0],[0,0]],[0,0])
    assert not episodes and summary['D60_coverage_pct']==100 and summary['trace_mean_aoi_minutes']==15
    # Age=4 remains fresh. A four-round outage is 60min, not over 60min.
    latest=np.array([[0],[0],[0],[0],[0],[0],[0],[0],[8]])
    summary,src,episodes=trajectory_metrics(latest,[[250,0]],[0,0])
    e=next(x for x in episodes if x['criterion_minutes']==60)
    assert (e['start_round'],e['end_round_exclusive'],e['observed_duration_minutes'])==(4,8,60)
    assert e['completed_recovery']==1 and src[0]['events_over_60min']==0
    print('PASS: initialization, inclusive freshness, strict duration, censoring and completed recovery tests')

def regression(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    row=execute(('T3_G20',.7,160101,'JLC-R'),out)
    source=PROJECT/'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv'
    with source.open(encoding='utf-8-sig',newline='') as f:
        reference=next(r for r in csv.DictReader(f) if r['condition']=='T3_G20' and float(r['supply'])==.7 and int(r['seed'])==160101 and r['method']=='JLC-R-HYB-V63')
    fields=['coverage_pct','aoi_mean_minutes','source_coverage_p5_pct','night_off_pct','consumed_j']
    delta={k:abs(row[k]-float(reference[k])) for k in fields};assert max(delta.values())<1e-8,delta
    result={'status':'PASS','regression_case':load()['fidelity_regression'],'absolute_deviation':delta,
        'source_sha256':sha(source),'protocol_sha256':sha(PROTOCOL),'wrapper_source_sha256':sha(__file__)}
    write_json(out/'regression.json',result);print(json.dumps(result,indent=2))

def run(workers):
    protocol=load();raw=RESULTS/f'{ID}_raw';raw.mkdir(exist_ok=False)
    cases=[(c['condition'],c['supply'],seed,method) for c in protocol['conditions'] for seed in protocol['seeds'] for method in protocol['methods']]
    assert len(cases)==144
    freeze={'protocol_sha256':sha(PROTOCOL),'source_sha256':sha(__file__),'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'frozen_core_sha256':protocol['core_sha256'],'cases':cases,'workers':workers,'nature':protocol['nature']}
    for name,h in protocol['core_sha256'].items():assert sha(PROJECT/'code/simulation'/name)==h,name
    write_json(RESULTS/f'{ID}_execution_freeze.json',freeze)
    rows=[];failures=[];started=time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs={pool.submit(execute,case,raw):case for case in cases}
        for future in as_completed(jobs):
            case=jobs[future]
            try:rows.append(future.result())
            except Exception:failures.append({'case':case,'traceback':traceback.format_exc()})
            write_csv(RESULTS/f'{ID}_cases.csv',sorted(rows,key=lambda x:(x['condition'],x['seed'],x['method'])))
            status={'completed':len(rows),'failed':len(failures),'planned':len(cases),'elapsed_seconds':time.time()-started,'failures':failures}
            write_json(RESULTS/f'{ID}_progress.json',status)
            print(json.dumps({k:status[k] for k in ['completed','failed','planned','elapsed_seconds']}),flush=True)
    assert not failures,failures
    assert len(rows)==144
    for name,h in protocol['core_sha256'].items():assert sha(PROJECT/'code/simulation'/name)==h,name

def analyze():
    from scipy.stats import t
    raw=RESULTS/f'{ID}_raw';summaries=[];source_rows=[];episodes=[]
    for f in sorted(raw.glob('*.npz')):
        meta=json.loads(f.with_suffix('.json').read_text());assert sha(f)==meta['raw_sha256']
        with np.load(f,allow_pickle=False) as a:summary,sources,events=trajectory_metrics(a['latest_birth'],a['positions_m'],a['sink_m'])
        for k,v in summary.items():
            if v is None:assert meta[k] is None
            else:assert abs(v-meta[k])<1e-8,(f,k)
        key={k:meta[k] for k in ['condition','supply','seed','method']}
        summaries.append(dict(**key,**summary))
        source_rows.extend(dict(**key,**x) for x in sources);episodes.extend(dict(**key,**x) for x in events)
    assert len(summaries)==144
    write_csv(RESULTS/f'{ID}_sources.csv',source_rows)
    import gzip,io
    with gzip.open(RESULTS/f'{ID}_episodes.csv.gz','wt',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(episodes[0]));writer.writeheader();writer.writerows(episodes)
    stats=[]
    metrics=['D60_longest_gap_source_median_minutes','D60_longest_gap_source_p95_minutes','D60_sources_any_gap_over_240min_pct','D60_far_sources_any_gap_over_240min_pct','D60_events_over_240min_per_100_source_days','D60_far_completed_recovery_median_minutes','D60_far_right_censored_recovery_pct','D240_coverage_pct']
    for c in load()['conditions']:
        selected=[x for x in summaries if x['condition']==c['condition']]
        for metric in metrics:
            candidate={x['seed']:x[metric] for x in selected if x['method']=='JLC-R'}
            for method in load()['methods']:
                values={x['seed']:x[metric] for x in selected if x['method']==method}
                finite=[v for v in values.values() if v is not None]
                difference=[candidate[s]-v for s,v in values.items() if v is not None and candidate[s] is not None]
                assert len(values)==12
                mean=float(np.mean(finite)) if finite else None
                delta=float(np.mean(difference)) if difference else None
                half=float(t.ppf(.975,len(difference)-1)*np.std(difference,ddof=1)/np.sqrt(len(difference))) if len(difference)>1 else None
                stats.append(dict(condition=c['condition'],supply=c['supply'],metric=metric,method=method,n=len(finite),mean=mean,
                    paired_n=len(difference),jlcr_minus_comparator=delta,ci95_low=delta-half if half is not None else None,
                    ci95_high=delta+half if half is not None else None))
    write_csv(RESULTS/f'{ID}_summary.csv',stats)
    write_json(RESULTS/f'{ID}_analysis.json',{'status':'PASS','cases':len(summaries),'sources':len(source_rows),'episodes':len(episodes),
        'statistical_unit':'network seed; source and event values are within-run summaries','primary_tests':0,
        'censoring':'observed runs include horizon censoring; recovery excludes initialization and incomplete episodes, with censoring reported separately',
        'raw_sha256':{f.name:sha(f) for f in sorted(raw.glob('*.npz'))}})
    print('PASS: all recorded matrices independently rescored; summaries and nominal paired intervals written')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',required=True,choices=['selftest','regression','run','analyze']);parser.add_argument('--output',type=Path);parser.add_argument('--workers',type=int,default=min(8,max(1,(os.cpu_count() or 2)-2)));args=parser.parse_args()
    if args.mode=='selftest':selftest()
    elif args.mode=='regression':
        if not args.output:parser.error('regression requires a new --output directory')
        regression(args.output)
    elif args.mode=='run':
        if args.workers<1:parser.error('workers must be positive')
        run(args.workers)
    else:analyze()
