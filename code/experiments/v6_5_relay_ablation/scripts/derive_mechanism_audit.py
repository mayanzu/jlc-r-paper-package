"""Read-only derivation of event denominators and installed-Guard transitions.

No simulation or hypothesis test is run. All quantities come from retained
raw logs; undefined opportunity rates remain missing. The independent n for
descriptive intervals is the network seed, never the number of CH periods.
"""
from pathlib import Path
import gzip,json,math,sys
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE


def ratio(n,d):
    return n/d if d else None


def main():
    assert json.loads((HERE/'audit/formal_audit.json').read_text())['status']=='PASS'
    rows=[]
    for path in sorted((HERE/'results/raw').glob('*.json.gz')):
        if '_failure_' in path.name:
            continue
        with gzip.open(path,'rt',encoding='utf-8') as f:raw=json.load(f)
        m=raw['metrics'];e=raw['events'];plans=raw['ch_credit_periods']
        count=lambda key:float(e.get(key,0))
        assert len(plans)==4032
        assert int(count('holds_created'))==int(m['hold_created'])
        assert int(count('committed_hop_successes'))==int(m['held_packet_hop_successes'])
        assert int(count('reactive_node_periods'))==int(m['fdc_activated_node_periods'])
        assert int(count('unused_forward_guards'))==int(m['slots_released_at_boundary'])+sum(raw['final_forward_guard_holds'])
        assert count('t_checks_executed')==count('t_positive_margin_checks')+count('t_zero_margin_checks')
        assert count('reject_transit_protect')==count('t_reject_positive_margin')+count('t_reject_zero_margin')
        assert 0<=count('staleness_changed_selection')<=count('staleness_discriminating_ties')<=count('staleness_comparison_opportunities')
        assert 0<=count('committed_hop_successes')<=count('holds_created')
        for record in plans:
            assert 0<=record['prefix_guards']<=49 and 0<=record['installed_guards']<=49
        r_only=[p for p in plans if p['low_guard'] and not p['queue_demand'] and p['reactive']]
        assert len(r_only)==int(count('r_only_reactive_periods'))
        if raw['case']['configuration'][1]=='0':assert count('reject_transit_protect')==0
        if raw['case']['configuration'][2]=='0':assert not r_only
        if raw['case']['configuration'][3]=='0':
            assert count('staleness_changed_selection')==count('staleness_active_comparisons')==0
        else:
            assert count('staleness_changed_selection')==count('staleness_would_change_selection')
            assert count('staleness_active_comparisons')==count('staleness_comparison_opportunities')
        installed_ge2=sum(p['installed_guards']>=2 for p in r_only)
        row=dict(raw['case'],
            source_demands=m['source_time_denominator'],
            request_calls=count('requests_all'),paid_requests=count('paid_requests_all'),
            member_request_calls=count('member_ch_requests'),paid_member_requests=count('paid_member_ch_requests'),
            member_receiver_responses=count('receiver_responses_member_ch'),
            t_checks=count('t_checks_executed'),t_positive_checks=count('t_positive_margin_checks'),
            t_zero_checks=count('t_zero_margin_checks'),
            t_positive_refusals=count('t_reject_positive_margin'),t_zero_refusals=count('t_reject_zero_margin'),
            t_refusals=count('reject_transit_protect'),
            t_refusals_per1000_paid_member_requests=1000*count('reject_transit_protect')/count('paid_member_ch_requests') if count('paid_member_ch_requests') else None,
            pre_response_refusals=count('pre_response_rejections'),post_response_refusals=count('post_response_rejections'),
            ch_periods=len(plans),ch_low_guard_only_demand=count('ch_low_guard_only_demand'),
            ch_reactive_periods=count('ch_reactive_periods'),r_only_choices=len(r_only),
            r_only_prefix_guard_mean=float(np.mean([p['prefix_guards'] for p in r_only])) if r_only else None,
            r_only_installed_guard_mean=float(np.mean([p['installed_guards'] for p in r_only])) if r_only else None,
            r_only_installed_ge2=installed_ge2,
            r_only_installed_two_guard_fraction=ratio(installed_ge2,len(r_only)),
            eligible_ties=count('staleness_comparison_opportunities'),
            discriminating_ties=count('staleness_discriminating_ties'),
            active_staleness_comparisons=count('staleness_active_comparisons'),
            actual_choice_changes=count('staleness_changed_selection'),
            potential_local_choice_changes=count('staleness_would_change_selection'),
            s_changes_per1000_eligible_ties=1000*count('staleness_changed_selection')/count('staleness_comparison_opportunities') if count('staleness_comparison_opportunities') else None,
            s_changes_per1000_discriminating_ties=1000*count('staleness_changed_selection')/count('staleness_discriminating_ties') if count('staleness_discriminating_ties') else None,
            commitments=count('holds_created'),committed_successful_hops=count('committed_hop_successes'),
            completed_hops_per1000_commitments=1000*count('committed_hop_successes')/count('holds_created') if count('holds_created') else None,
            unused_actual_forward_guards=count('unused_forward_guards'),
            unused_actual_forward_energy_j=count('unused_forward_energy_nj')*1e-9,
            unused_paid_slots=float(m['unconsumed_slots']))
        rows.append(row)
    assert len(rows)==864
    data=pd.DataFrame(rows)
    data.to_csv(HERE/'results/derived_mechanism_runs.csv',index=False)
    summary=[]
    keys=['condition','supply','treatment','configuration']
    for identity,g in data.groupby(keys,sort=False):
        assert len(g)==12
        row=dict(zip(keys,identity),independent_seeds=12)
        for column in data.select_dtypes(include='number'):
            if column in ['seed','supply']:continue
            a=g[column].to_numpy(dtype=float)
            defined=np.isfinite(a)
            row[column+'_defined_seeds']=int(defined.sum())
            if defined.all():
                mean=float(a.mean());half=float(stats.t.ppf(.975,11)*a.std(ddof=1)/math.sqrt(12))
                row[column+'_mean']=mean
                row[column+'_ci95_low']=mean-half
                row[column+'_ci95_high']=mean+half
            else:
                # No complete-case seed dropping to fabricate a twelve-seed CI.
                row[column+'_mean']=None;row[column+'_ci95_low']=None;row[column+'_ci95_high']=None
        summary.append(row)
    pd.DataFrame(summary).to_csv(HERE/'results/derived_mechanism_summary.csv',index=False)
    report=dict(status='PASS',successful_cases=864,ch_credit_period_records=864*4032,
        native_commitment_counts_match=True,native_committed_success_counts_match=True,
        native_reactive_counts_match=True,unused_guard_boundary_identity=True,
        t_margin_split_identity=True,s_choice_scope_identity=True,
        guard_transition_scope='Installed plan capacity, not a guarantee of online paid service or end-to-end delivery.',
        zero_denominators='Missing; no silent conversion to zero or complete-case CI with n=12.',
        statistical_scope='Descriptive seed-level intervals only; no added primary test or significance family.')
    (HERE/'audit/mechanism_log_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
