"""Presentation-only report: all nine cells, all variants and all contrasts.

Reads the frozen analysis outputs without changing any estimate or test.
This formatter is separate from the pre-execution statistical pipeline.
"""
from pathlib import Path
import json
import pandas as pd
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE

METRICS={'coverage_pct':'Coverage (pp)','far_coverage_pct':'Far coverage (pp)',
    'source_coverage_p5_pct':'Source P5 (pp)','aoi_mean_minutes':'AoI (min)',
    'night_off_pct':'Night outage (pp)','consumed_j':'Energy (J)'}
ORDER=['T','R','S','TR','TS','RS','TRS','Bundle','Loss_T','Loss_R','Loss_S']
LABELS={'SYNTHETIC_G20':'Synthetic','WINTER_G20':'T1 winter','T2_G20':'T2 spring','T3_G20':'T3 winter'}


def frame_table(frame):
    return frame.to_markdown(index=False,floatfmt='.6g')


def estimate_text(row):
    return f'{row.mean_difference:+.4f} [{row.ci95_low:+.4f}, {row.ci95_high:+.4f}]'


def main():
    assert json.loads((HERE/'audit/formal_audit.json').read_text())['status']=='PASS'
    raw=pd.read_csv(HERE/'results/formal_runs.csv')
    absolute=pd.read_csv(HERE/'results/factorial_summary.csv')
    effects=pd.read_csv(HERE/'results/effect_summary.csv')
    primary=pd.read_csv(HERE/'results/primary_tests.csv')
    pooled=pd.read_csv(HERE/'results/pooled_winter_effects.csv')
    freeze=json.loads((HERE/'audit/execution_freeze.json').read_text())
    out=['# Supplemental S200/G20 relay-protection factorial study','',
        'The study retains all 864 planned formal executions: 768 across eight weather–supply cells and '
        '96 under the unchanged Stage III-C3 canopy stress condition. The independent unit is the network seed '
        '(n=12), paired across every configuration and condition. The original 480-run confirmation, '
        'its Holm-36 family and WP0–WP6 numerical records are unchanged.','',
        '## Four primary comparisons','',
        'Each seed first averages T1/0.7 and T3/0.7 equally. The two-sided paired Student tests use df=11 '
        'and a separate Holm family of four tests. Confidence intervals are nominal 95% paired t intervals. '
        'No noninferiority or equivalence margin is introduced.','']
    columns=['hypothesis','effect','metric','n','mean_difference','ci95_low','ci95_high','t_statistic','df','p_two_sided','p_holm4']
    out += [frame_table(primary[columns]),'', '## Small-sample sensitivity','',
        'The exhaustive 4096-pattern sign-flip sensitivity assumes independent seed differences symmetric '
        'around zero under the null. Direction counts and leave-one-seed-out means retain all seeds; '
        'they do not replace the prespecified primary decisions.','',
        frame_table(primary[['hypothesis','positive_seeds','negative_seeds','zero_seeds',
            'sign_flip_p_two_sided','loo_mean_min','loo_mean_max','max_single_seed_absolute_share']]),'',
        '## Pooled low-supply winter effects','']
    table=[]
    for effect in ORDER:
        row={'Effect':effect}
        for metric,label in METRICS.items():
            r=pooled[(pooled.effect==effect)&(pooled.metric==metric)].iloc[0]
            row[label]=estimate_text(r)
        table.append(row)
    out += [frame_table(pd.DataFrame(table)),'',
        'T/R/S are average on-minus-off effects across the four remaining-factor backgrounds. '
        'TR/TS/RS are differences of differences averaged over the remaining factor; TRS is the full third difference. '
        'Bundle is A111−A000. Loss_T/R/S is A111 minus the corresponding single-off configuration. '
        'These contrasts have different meanings and are not interchangeable. Under this contrast convention, '
        'Bundle = T + R + S + TRS/4. Pairwise interactions describe background dependence rather than an extra term in this opposing-corner identity.','',
        '## Complete condition-specific results','',
        'All remaining cells, canopy outcomes, interactions and nonprimary outcomes are secondary descriptive analyses. '
        'Intervals below are nominal and are not simultaneous multiplicity-adjusted statements. '
        'Positive coverage/P5 and negative age/outage effects favor enabling a factor. All negative and zero effects are retained.','']
    for keys,g in absolute.groupby(['condition','supply','treatment'],sort=False):
        condition,supply,treatment=keys
        title=LABELS[condition]+f', s={supply:g}'+(' — Stage III-C3' if treatment!='C0' else '')
        out += ['### '+title,'','Absolute means across twelve seeds; intervals are available in the full factorial-summary CSV.','']
        table=[]
        for _,r in g.sort_values('configuration').iterrows():
            row={'Configuration':r.configuration}
            for metric,label in METRICS.items():
                row[label.replace('(pp)','(%)')]=r[metric+'_mean']
            table.append(row)
        out += [frame_table(pd.DataFrame(table)),'','All factorial and full-background contrasts (mean [95% CI]):','']
        table=[]
        cell=effects[(effects.condition==condition)&(effects.supply==supply)&(effects.treatment==treatment)]
        for effect in ORDER:
            row={'Effect':effect}
            for metric,label in METRICS.items():
                r=cell[(cell.effect==effect)&(cell.metric==metric)].iloc[0]
                row[label]=estimate_text(r)
            table.append(row)
        out += [frame_table(pd.DataFrame(table)),'','Mechanism exposure and execution totals over twelve runs per configuration (not independent packet replications):','']
        runs=raw[(raw.condition==condition)&(raw.supply==supply)&(raw.treatment==treatment)]
        table=[]
        for configuration,items in runs.groupby('configuration'):
            def total(field):
                return int(items[field].sum()) if field in items else 0
            requests=total('event_member_ch_requests');paid=total('event_paid_member_ch_requests')
            refused=total('event_reject_transit_protect')
            holds=total('event_holds_created');completed=total('event_committed_hop_successes')
            ties=total('event_staleness_comparison_opportunities');changed=total('event_staleness_changed_selection')
            table.append({'Configuration':configuration,'Member request calls':requests,'Paid member requests':paid,
                'T refusals':refused,'T refusals/1000 paid member requests':1000*refused/paid if paid else None,
                'R-only reactive choices':total('event_r_only_reactive_periods'),
                'S eligible ties':ties,'S changed choices':changed,
                'S changes/1000 ties':1000*changed/ties if ties else None,
                'Commitments':holds,'Committed successful hops':completed,
                'Committed success/1000 commitments':1000*completed/holds if holds else None})
        out += [frame_table(pd.DataFrame(table)),'']
    out += ['## Interpretation and audit boundaries','',
        'T identifies the entire frozen pre-response gate: its positive credit/energy margin and earlier refusals. '
        'A zero-margin request can also be rejected before the receiver response. Its binary Guard threshold '
        'does not purchase or lock a third Guard beyond ordinary receive-plus-forward safety. '
        'Positive-margin and zero-margin events remain separate in the raw counters.','',
        'Queue-choice counters exclude read-only diagnostic peeks. A changed local choice is compared with '
        'the exact historical fallback in the observed queue state, not with the entire unobserved S=0 trajectory. '
        'A choice change and an R-only reactive switch are not themselves successful service.','',
        'Far-source coverage uses its own ≥200 m source-time denominator. Source P5 uses all 100 sources. '
        'Relay fate counts can contain repeated blocked events; distinct expiries at relays are provided separately. '
        'Unused actual one-hop holds are not invented T reservations, and held energy is not necessarily consumed. '
        'Local one-hop non-overcommitment does not imply end-to-end delivery or per-source fairness.','',
        'The Stage III-C3 panel inherits the exact WP4 mapping. The executed energy factor is '
        'T_min+(T_max−T_min)c, increasing with the spatial index while decoding decreases. '
        'All 3600 retained node-stage records confirm this expression exactly; the earlier prose expression '
        'has been corrected without altering the frozen source or data. This field is not a calibrated model '
        'of co-located monotone physical canopy shading and attenuation.','',
        '## Provenance and complete data','',
        f"Execution snapshot commit: `{freeze['snapshot_git_commit']}`. The original snapshot is retained in "
        '`audit/execution_snapshot.zip`; delivery-only formatting/audit corrections are listed separately. '
        'All raw files, failures and retry identities are covered by the final manifests. '
        'The source/configuration/input freeze, exact endpoint regressions, unit tests and seed-use audit '
        'remain in `audit/`. Full precision source-level outcomes, all interactions, conditional losses, '
        'remaining far-source outcomes and coverage dispersion are provided in the results CSVs. '
        'No service-dependent threshold, seed, physical parameter, outcome definition or primary hypothesis '
        'has been changed.','']
    (HERE/'report/ablation_analysis.md').write_text('\n'.join(out),encoding='utf-8')
    print('Complete report written: all 9 cells, 8 configurations and 11 contrasts per cell.')


if __name__=='__main__':
    main()
