"""Seed-paired factorial contrasts; primary Holm family fixed in configs.

Never treats nodes, packets, periods or condition repetitions as independent n.
"""
import itertools
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from experiment import HERE, read_config, sha

METRICS = ['coverage_pct', 'far_coverage_pct', 'source_coverage_p5_pct',
           'aoi_mean_minutes', 'far_aoi_mean_minutes', 'night_off_pct', 'consumed_j',
           'source_coverage_sd_pct', 'far_delivered_samples', 'far_expired_samples',
           'far_expired_at_relay_samples', 'far_relay_loss_events']
EFFECTS = ['T','R','S','TR','TS','RS','TRS','Bundle','Loss_T','Loss_R','Loss_S']
CELL = ['condition','supply','treatment']


def estimate(values):
    a = np.asarray(values, dtype=float)
    assert len(a) == 12 and np.isfinite(a).all()
    mean = float(a.mean())
    sd = float(a.std(ddof=1))
    se = sd / np.sqrt(len(a))
    half = float(stats.t.ppf(.975, len(a)-1)*se)
    if sd == 0:
        t, p = (0., 1.) if mean == 0 else (None, None)
    else:
        t = mean / se
        p = float(2*stats.t.sf(abs(t), len(a)-1))
    return dict(n=len(a),mean_difference=mean,sd_difference=sd,se=se,
                ci95_low=mean-half,ci95_high=mean+half,t_statistic=t,df=len(a)-1,
                p_two_sided=p,positive_seeds=int((a>0).sum()),negative_seeds=int((a<0).sum()),
                zero_seeds=int((a==0).sum()),
                deterministic_zero_variance=bool(sd==0))


def contrast(y, effect):
    if effect == 'Bundle':
        return y['A111'] - y['A000']
    if effect.startswith('Loss_'):
        bits = list('111')
        bits['TRS'.index(effect[-1])] = '0'
        return y['A111'] - y['A'+''.join(bits)]
    indices = ['TRS'.index(f) for f in effect]
    return sum(np.prod([2*int(k[1+i])-1 for i in indices])*v for k,v in y.items()) / 2**(3-len(effect))


def holm(pvalues):
    p = np.asarray(pvalues, dtype=float)
    assert np.isfinite(p).all()
    order = np.argsort(p, kind='stable')
    adjusted = np.minimum(1, np.maximum.accumulate(p[order]*np.arange(len(p),0,-1)))
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result


def sensitivity(a):
    a = np.asarray(a, dtype=float)
    signs = np.asarray(list(itertools.product([-1,1], repeat=len(a))))
    null_means = (signs*a[None,:]).mean(axis=1)
    p = float(np.mean(np.abs(null_means) >= abs(a.mean())-1e-14))
    loo = [(a.sum()-v)/(len(a)-1) for v in a]
    return dict(sign_flip_p_two_sided=p,sign_flip_patterns=len(signs),
        loo_mean_min=float(min(loo)),loo_mean_max=float(max(loo)),
        max_single_seed_absolute_share=float(abs(a).max()/abs(a).sum()) if abs(a).sum() else 0,
        assumption='Independent seed contrasts symmetric about zero under the sign-flip null; no packet-level randomization claim.')


def main():
    assert json.loads((HERE/'audit/formal_audit.json').read_text())['status']=='PASS'
    data = pd.read_csv(HERE/'results/formal_runs.csv')
    assert len(data)==864
    assert not data.duplicated(CELL+['seed','configuration']).any()
    assert set(data.seed)==set(read_config('seeds.json')['formal'])
    assert (data.max_hold_violation_j<=1e-8).all() and (data.max_slot_violation==0).all()
    assert (data.max_energy_balance_error_j<=1e-6).all()
    summary = []
    for keys, group in data.groupby(CELL+['configuration'],sort=False):
        assert len(group)==12
        row = dict(zip(CELL+['configuration'], keys))
        for metric in METRICS:
            est = estimate(group[metric])
            for k in ['mean_difference','ci95_low','ci95_high']:
                row[metric+'_'+('mean' if k=='mean_difference' else k)] = est[k]
        summary.append(row)
    pd.DataFrame(summary).to_csv(HERE/'results/factorial_summary.csv',index=False)
    paired = []
    for keys, group in data.groupby(CELL+['seed'],sort=False):
        assert len(group)==8
        rows = group.set_index('configuration')
        for metric in METRICS:
            y = rows[metric].to_dict()
            all_effects = {e:float(contrast(y,e)) for e in EFFECTS}
            assert np.isclose(all_effects['Bundle'],sum(all_effects[e] for e in ['T','R','S'])+.25*all_effects['TRS'],rtol=0,atol=1e-10)
            for effect,value in all_effects.items():
                paired.append(dict(zip(CELL+['seed'],keys),metric=metric,effect=effect,value=value))
    paired = pd.DataFrame(paired)
    paired.to_csv(HERE/'results/paired_effects.csv',index=False)
    effects = []
    for keys, group in paired.groupby(CELL+['metric','effect'],sort=False):
        effects.append(dict(zip(CELL+['metric','effect'],keys),**estimate(group.value)))
    pd.DataFrame(effects).to_csv(HERE/'results/effect_summary.csv',index=False)
    plan=read_config('statistical_plan.json')
    winter = paired[(paired.treatment=='C0') & paired.condition.isin(['WINTER_G20','T3_G20']) & (paired.supply==.7)]
    pooled = winter.groupby(['seed','metric','effect'],as_index=False).value.mean()
    assert all(len(g)==2 for _,g in winter.groupby(['seed','metric','effect']))
    pooled.to_csv(HERE/'results/primary_seed_effects.csv',index=False)
    primary=[]
    for hypothesis,effect,metric in plan['primary']:
        a=pooled[(pooled.effect==effect)&(pooled.metric==metric)].sort_values('seed').value
        primary.append(dict(hypothesis=hypothesis,effect=effect,metric=metric,**estimate(a),**sensitivity(a)))
    adjusted=holm([r['p_two_sided'] for r in primary])
    for r,p in zip(primary,adjusted):
        r.update(p_holm4=float(p),reject_holm4=bool(p<.05))
    pd.DataFrame(primary).to_csv(HERE/'results/primary_tests.csv',index=False)
    pooled_effects=[]
    for keys,group in pooled.groupby(['metric','effect'],sort=False):
        pooled_effects.append(dict(zip(['metric','effect'],keys),**estimate(group.value)))
    pd.DataFrame(pooled_effects).to_csv(HERE/'results/pooled_winter_effects.csv',index=False)
    # Denominator-specific pooled rates, with seed-level rate CIs as uncertainty.
    events=[c for c in data.columns if c.startswith('event_') or c.startswith('relay_loss_')]
    mechanism=[]
    for keys, group in data.groupby(CELL+['configuration'],sort=False):
        row=dict(zip(CELL+['configuration'],keys), n=12,
            demand_denominator=int(group.source_time_denominator.sum()),
            member_request_denominator=int(group.event_member_ch_requests.sum()),
            request_denominator=int(group.event_requests_all.sum()),
            hold_denominator=int(group.event_holds_created.sum()),
            tie_denominator=int(group.event_staleness_comparison_opportunities.sum()))
        for event in events:
            row[event+'_sum']=float(group[event].sum())
            row[event+'_per1000_demand']=1000*float(group[event].sum())/row['demand_denominator']
        for rate,numerator,denominator in [
            ('transit_rejections_per1000_member_requests','event_reject_transit_protect','event_member_ch_requests'),
            ('post_response_rejections_per1000_requests','event_post_response_rejections','event_requests_all'),
            ('committed_successes_per1000_holds','event_committed_hop_successes','event_holds_created'),
            ('staleness_changes_per1000_ties','event_staleness_changed_selection','event_staleness_comparison_opportunities')]:
            row[rate]=1000*group[numerator].sum()/group[denominator].sum() if group[denominator].sum() else None
            individual=1000*group[numerator]/group[denominator]
            if np.isfinite(individual).all():
                est=estimate(individual)
                row[rate+'_seed_mean']=est['mean_difference']
                row[rate+'_seed_ci95_low']=est['ci95_low']
                row[rate+'_seed_ci95_high']=est['ci95_high']
        mechanism.append(row)
    pd.DataFrame(mechanism).to_csv(HERE/'results/mechanism_summary.csv',index=False)
    write_report(data,pd.DataFrame(primary),pd.DataFrame(pooled_effects))
    print(pd.DataFrame(primary)[['hypothesis','mean_difference','ci95_low','ci95_high','p_two_sided','p_holm4','sign_flip_p_two_sided']].to_string(index=False))


def write_report(data,primary,pooled):
    text=['# Supplemental S200/G20 relay-protection factorial analysis','',
        'This study was specified after the original confirmation and does not change WP0–WP6 or the original Holm-36 decisions. '
        'All 864 planned executions and all 12 formal seeds are retained. Primary results average T1 and T3 at s=0.7 within each seed. '
        'Effects are on-minus-off in native units; lower AoI/outage is favorable. Coverage/P5 differences are percentage points.', '',
        '## Four primary tests','',primary.to_markdown(index=False),'',
        '## All low-supply winter effects','',pooled.to_markdown(index=False),'',
        'The second- and third-order interactions are factorial difference contrasts, not fitted regression coefficients. '
        'The bundle obeys Bundle = T + R + S + TRS/4 under these contrast definitions; pairwise interactions instead describe background-dependent marginal effects. '
        'Conditional losses are reported separately and are not substituted for marginal main effects.', '',
        '## Scope and limitations','',
        'T is an admission margin and creates no extra physical hold. Unused-forward counts refer to actual one-hop holds at round boundaries. '
        'Hop-fate counts can contain repeated blocked events; distinct far-source expiry-at-relay sample counts remain separate. '
        'The canopy condition inherits the original T2/1.0 Stage III-C3 field, transmittance mapping and link attenuation. '
        'Canopy and other-cell effects are secondary descriptive results with nominal intervals. '
        'Twelve seeds limit precision; nonsignificance is not equivalence. Sign-flip sensitivity assumes independent symmetric seed contrasts. '
        'Local one-hop non-overcommitment does not guarantee end-to-end delivery.', '',
        '## Reproduction','',
        'See configs/statistical_plan.json, audit/execution_freeze.json and results/primary_seed_effects.csv. '
        'All raw records include physical configuration, CH plans, per-round energy audit, source counters and event denominators. '
        'No outcome-dependent tuning, exclusions or seed replacement is allowed.','']
    (HERE/'report/ablation_analysis.md').write_text('\n'.join(text),encoding='utf-8')


if __name__=='__main__':
    main()
