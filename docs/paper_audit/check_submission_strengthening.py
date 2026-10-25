"""Independent checks for the added source-availability recording study.

Uses saved latest-birth matrices, not the experiment's metric helper or simulator.
Original Holm families are checked by the existing scientific audit separately.
"""
from pathlib import Path
import csv,hashlib,itertools,json,math,re,statistics,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from paths import ROOT as PROJECT,MAIN

ID='reliability_20261025'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def independent_scores(latest,far):
    T,N=latest.shape
    assert (T,N)==(1344,100)
    assert np.all(latest>=-1) and np.all(latest<=np.arange(T)[:,None])
    assert np.all(np.diff(latest.astype(np.int32),axis=0)>=0)
    age=np.where(latest>=0,np.arange(T)[:,None]-latest+1,np.arange(T)[:,None]+1)
    result={'trace_mean_aoi_minutes':float(age.mean()*15)}
    for D in [4,16]:
        fresh=(latest>=0)&(age<=D);longest=[];long4=[];events60=0;events240=0;completed=[];eligible=0;censored=0
        for node in range(N):
            cursor=0;durations=[]
            for unavailable,group in itertools.groupby((~fresh[:,node]).tolist()):
                length=sum(1 for _ in group);end=cursor+length
                if unavailable:
                    duration=15*length;durations.append(duration)
                    events60+=int(duration>60);events240+=int(duration>240)
                    if far[node] and cursor>0:
                        eligible+=1
                        if end==T:censored+=1
                        else:completed.append(duration)
                cursor=end
            longest.append(max(durations,default=0));long4.append(any(v>240 for v in durations))
        k=f'D{D*15}_'
        result.update({k+'coverage_pct':float(100*fresh.mean()),
            k+'longest_gap_source_median_minutes':float(np.median(longest)),
            k+'longest_gap_source_p95_minutes':float(np.quantile(longest,.95)),
            k+'sources_any_gap_over_240min_pct':float(100*np.mean(long4)),
            k+'far_sources_any_gap_over_240min_pct':float(100*np.mean(np.array(long4)[far])),
            k+'events_over_60min_per_100_source_days':events60/(N*T/96)*100,
            k+'events_over_240min_per_100_source_days':events240/(N*T/96)*100,
            k+'far_completed_recovery_median_minutes':float(np.median(completed)) if completed else None,
            k+'far_completed_recovery_episodes':len(completed),
            k+'far_right_censored_recovery_episodes':censored,
            k+'far_right_censored_recovery_pct':100*censored/eligible if eligible else None})
    return result

def physical_evidence(project):
    """Recompute arithmetic and daylight support without importing a controller."""
    import ast
    report=project/'docs/paper_audit/strengthening_20261025/physical_accounting_20261025.json'
    if not report.exists():report=project/'COMPAG/audit/physical_accounting_20261025.json'
    record=json.loads(report.read_text(encoding='utf-8'))
    cfg=json.loads((project/'code/simulation/config.json').read_text(encoding='utf-8'))
    design=json.loads((project/'code/simulation/current_design.json').read_text(encoding='utf-8'))
    tree=ast.parse((project/'code/simulation/service_model.py').read_text(encoding='utf-8'))
    default=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(v,ast.Name) and v.id=='DEFAULTS' for v in n.targets))
    defaults={v.arg:ast.literal_eval(v.value) for v in default.keywords}
    c=record['calculations']
    assert defaults['control_frame_bits']==c['effective_control_frame_bits']==64
    assert cfg['packet_bits']==c['logical_payload_bits']==4000
    assert defaults['bitrate_bps']==c['bitrate_bps']==250000
    assert cfg['packet_bits']/defaults['bitrate_bps']*1000==c['nominal_data_airtime_ms']==16
    assert abs(cfg['solar_peak_j_per_round']/cfg['round_seconds']*1000-c['nominal_harvest_power_mW'])<1e-12
    assert cfg['battery_j']==4 and cfg['initial_battery_fraction']==.75 and cfg['radio_idle_w']==.056
    for condition in design['conditions']:
        timing=condition['config'];bound=2*20e-6*timing['sync_interval_s']+timing['sync_jitter_s']+timing['sync_turnaround_s']
        assert abs(bound-.017)<1e-12 and bound<=timing['guard_listen_s']==.02
    weather=[]
    for row in record['weather_support']:
        source=project/row['weather_file'];assert sha(source)==row['sha256']
        entries=read(source)[192:1536]
        ghi=np.array([float(v['ghi_w_m2']) for v in entries])
        hours=np.array([(int(v['local_round'])%96)/4 for v in entries]);day=(hours>=6)&(hours<18)
        assert len(ghi)==row['rounds']==1344
        assert int(np.sum((ghi>0)&~day))==row['positive_GHI_rounds_outside_template']
        assert abs(100*ghi[~day].sum()/ghi.sum()-row['GHI_energy_fraction_outside_template_pct'])<1e-10
        assert abs(100*np.mean(ghi[day]==0)-row['template_rounds_with_zero_GHI_pct'])<1e-10
        weather.append(row['condition'])
    return {'parameters':'executed inputs, manufacturer reference and derived values distinguished',
            'control_bits':64,'payload_airtime_ms':16,'uncertainty_bound_ms':17,'weather_inputs_checked':weather,
            'real_MAC_validated':False,'hardware_calibration':False}

def check(ms=None,project=PROJECT):
    ms=(MAIN/'manuscript.md').read_text(encoding='utf-8') if ms is None else ms
    base=project/'code/experiments/v6_4_agricultural_extension';results=base/'results'
    protocol=base/f'{ID}_protocol.json';plan=json.loads(protocol.read_text(encoding='utf-8'))
    freeze=json.loads((results/f'{ID}_execution_freeze.json').read_text())
    assert freeze['protocol_sha256']==sha(protocol)
    assert freeze['source_sha256']==sha(base/f'{ID}.py')
    # Hash every distributed simulation module listed in the local execution
    # inventory. Undistributed development tests are not runtime dependencies.
    checked=[]
    for name,h in plan['core_sha256'].items():
        f=project/'code/simulation'/name
        if f.exists():assert sha(f)==h,name;checked.append(name)
    assert 'v63_model.py' in checked and len(checked)>=18
    expected={(c['condition'],float(c['supply']),seed,method) for c in plan['conditions'] for seed in plan['seeds'] for method in plan['methods']}
    rows=read(results/f'{ID}_cases.csv');index={(x['condition'],float(x['supply']),int(x['seed']),x['method']):x for x in rows}
    assert len(rows)==len(index)==144 and set(index)==expected
    old=read(project/'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv')
    assert not (set(plan['seeds'])&{int(x['seed']) for x in old})
    registry=project/'audit/seed_registry.csv'
    if registry.exists():assert not(set(plan['seeds']) & {int(x['seed']) for x in read(registry)})
    geometries={};numeric=0;envelopes=[];timing=[]
    recomputed={}
    for key,row in index.items():
        f=results/f'{ID}_raw'/row['raw_file'];assert sha(f)==row['raw_sha256']
        with np.load(f,allow_pickle=False) as data:
            assert str(data['protocol_sha256'])==sha(protocol)
            assert int(data['round_seconds'])==900
            positions=data['positions_m'];sink=data['sink_m']
            signature=hashlib.sha256(positions.tobytes()+sink.tobytes()).hexdigest()
            pair=key[:3]
            if pair in geometries:assert geometries[pair]==signature
            else:geometries[pair]=signature
            values=independent_scores(data['latest_birth'],np.linalg.norm(positions-sink,axis=1)>=200)
        for metric,value in values.items():
            if value is None:assert row[metric] in ['',None]
            else:assert abs(float(row[metric])-value)<1e-8,(key,metric);numeric+=1
        assert abs(float(row['coverage_pct'])-values['D60_coverage_pct'])<1e-8
        assert abs(float(row['aoi_mean_minutes'])-values['trace_mean_aoi_minutes'])<1e-8
        for metric,tolerance in [('max_hold_violation_j',1e-8),('max_slot_violation',0),('max_node_energy_error_j',1e-8),('max_energy_balance_error_j',1e-6)]:
            assert float(row[metric])<=tolerance
        assert int(float(row['generated']))+int(float(row['unsensed']))==134400
        assert float(row['generated'])==sum(float(row[x]) for x in ['delivered','expired','overflow','outstanding'])
        assert float(row['max_serial_envelope_s'])<=99.98
        envelopes.append(float(row['max_serial_envelope_s']));timing.append(int(row['timing_misses']))
        recomputed[key]=values
    # Verify aggregate summaries and intervals from independently rescored cases.
    from scipy.stats import t
    summary=read(results/f'{ID}_summary.csv')
    for row in summary:
        c=row['condition'];s=float(row['supply']);method=row['method'];metric=row['metric']
        values=[];differences=[]
        for seed in plan['seeds']:
            v=recomputed[c,s,seed,method][metric];a=recomputed[c,s,seed,'JLC-R'][metric]
            if v is not None:values.append(v)
            if v is not None and a is not None:differences.append(a-v)
        assert int(row['n'])==len(values) and int(row['paired_n'])==len(differences)
        if values:assert abs(float(row['mean'])-statistics.mean(values))<1e-8
        else:assert row['mean']==''
        if differences:
            delta=statistics.mean(differences);assert abs(float(row['jlcr_minus_comparator'])-delta)<1e-8
            if len(differences)>1:
                half=float(t.ppf(.975,len(differences)-1)*statistics.stdev(differences)/math.sqrt(len(differences)))
                assert abs(float(row['ci95_low'])-(delta-half))<1e-8 and abs(float(row['ci95_high'])-(delta+half))<1e-8
    assert len(summary)==3*8*4
    # Important new prose numbers are independently linked to the same traces.
    ordered=['WINTER_G20','T3_G20','T2_G20']
    for condition in ordered:
        jlcr=[v for key,v in recomputed.items() if key[0]==condition and key[3]=='JLC-R']
        for metric,scale in [('D60_longest_gap_source_p95_minutes',60),('D60_events_over_60min_per_100_source_days',1),('D60_events_over_240min_per_100_source_days',1)]:
            assert f'{statistics.mean(v[metric] for v in jlcr)/scale:.2f}' in ms
        for comparator in ['Prefix-only','Hybrid control']:
            r=next(v for v in summary if v['condition']==condition and v['method']==comparator and v['metric']=='D60_longest_gap_source_p95_minutes')
            lo,hi=float(r['ci95_low']),float(r['ci95_high'])
            if comparator=='Hybrid control':assert lo<0<hi
            else:
                for value in [-float(r['jlcr_minus_comparator'])/60,-hi/60,-lo/60]:assert f'{value:.2f}' in ms
    block=re.search(r'^Table 5\.[^\n]+\n\n((?:\|[^\n]*\n)+)',ms,re.M)
    assert block,'Missing reliability result table'
    table=[[c.strip() for c in line.strip().strip('|').split('|')] for line in block[1].splitlines()][2:]
    assert len(table)==12
    names={'WINTER_G20':'T1 / 0.7','T3_G20':'T3 / 0.7','T2_G20':'T2 / 1.0'}
    for displayed in table:
        condition=next(k for k,v in names.items() if v==displayed[0])
        method=displayed[1].replace('JLC-Core','Hybrid control')
        metrics=['D60_longest_gap_source_median_minutes','D60_longest_gap_source_p95_minutes',
            'D60_sources_any_gap_over_240min_pct','D60_far_completed_recovery_median_minutes',
            'D60_far_right_censored_recovery_pct']
        for column,metric in enumerate(metrics,2):
            vals=[values[metric] for key,values in recomputed.items() if key[0]==condition and key[3]==method and values[metric] is not None]
            expected=statistics.mean(vals)/(60 if column in [2,3,5] else 1)
            assert abs(float(displayed[column])-expected)<=.005001,(displayed,metric,expected)
    # Honest model/task language is a release requirement, not a formatting rule.
    assert '$l_c=64$' in ms and '$l_c=160$' not in ms
    assert '500 bytes' in ms and 'fragmentation' in ms and 'ACK' in ms
    assert 'not calibrated to canopy density' in ms and 'phenological growth stages' not in ms
    assert 'not universal agronomic tolerances' in ms
    assert '144 executions' in ms and 'post-confirmation exploratory' in ms.lower()
    assert 'initialization is excluded' in ms and 'unfinished far-source episodes' in ms
    assert 'No second complete external protocol is evaluated' in ms or 'no second complete external protocol is evaluated' in ms
    physics=physical_evidence(project)
    return {'status':'PASS','recording_cases':144,'independent_network_seeds':12,'conditions':3,'controllers':4,
        'trace_numeric_checks':numeric,'aggregate_rows_checked':len(summary),'core_modules_checked':len(checked),
        'largest_nominal_serial_envelope_s':max(envelopes),'timing_misses':sum(timing),
        'new_confirmatory_test_family':None,'censoring_explicit':True,'new_MAC_validation_claimed':False,
        'physical_evidence':physics}

if __name__=='__main__':print(json.dumps(check(),indent=2))
