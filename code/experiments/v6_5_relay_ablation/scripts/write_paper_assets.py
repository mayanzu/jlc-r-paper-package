"""Generate exact numeric tables and an independent English LaTeX study draft.

This does not edit the formal manuscript; scientific interpretation is checked
against these generated assets before the two authoritative sources are edited.
"""
from pathlib import Path
import sys
import json
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE


def main():
    data=pd.read_csv(HERE/'results/formal_runs.csv')
    assert len(data)==864
    winter=data[(data.condition.isin(['WINTER_G20','T3_G20']))&(data.supply==.7)&(data.treatment=='C0')]
    metrics=['coverage_pct','far_coverage_pct','source_coverage_p5_pct','aoi_mean_minutes','night_off_pct','consumed_j']
    by_seed=winter.groupby(['seed','configuration'])[metrics].mean()
    means=by_seed.groupby('configuration').mean()
    lines=['Table 5. Factorial ablation of relay protection under low-supply winter S200/G20 conditions.','',
        '| Configuration | T | R | S | Coverage (%) | Far coverage (%) | Source P5 (%) | AoI (h) | Night outage (%) | Energy (J) |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for configuration,row in means.iterrows():
        display=configuration + (' (Hybrid)' if configuration=='A000' else (' (JLC-R)' if configuration=='A111' else ''))
        values=[row.coverage_pct,row.far_coverage_pct,row.source_coverage_p5_pct,row.aoi_mean_minutes/60,row.night_off_pct,row.consumed_j]
        lines.append('| '+' | '.join([display,*list(configuration[1:]),*[f'{v:.3f}' for v in values]])+' |')
    lines+=['', '**Table note.** Each configuration mean first weights T1 winter and T3 winter at $s=0.7$ equally within each of twelve new paired seeds. '
        'These are 192 executions within the complete 864-run supplemental study, not the original confirmation. '
        'T is the additional pre-response transit margin; R is two-slot demand recognition; S is the exact local-staleness key. '
        'All configurations retain ordinary paid reception, one-hop holds, forwarding Guard safety and the same physical inputs. '
        'Far coverage uses the source--time denominator of sources at least 200 m from the sink; Source P5 uses all 100 sources. '
        'Figure 5 shows seed-paired effects and nominal 95% intervals. All nine conditions and all eight configurations remain in the complete data record.','']
    (HERE/'report/table5.md').write_text('\n'.join(lines),encoding='utf-8')
    primary=pd.read_csv(HERE/'results/primary_tests.csv')
    phr=[]
    for _,r in primary.iterrows():
        phr.append(f"{r.hypothesis}: {r.effect} on {r.metric}, {r.mean_difference:+.4f} pp "
            f"(95% CI [{r.ci95_low:+.4f}, {r.ci95_high:+.4f}]); "
            f"two-sided p={r.p_two_sided:.8g}; Holm-4 p={r.p_holm4:.8g}; "
            f"sign-flip p={r.sign_flip_p_two_sided:.8g}; "
            f"positive/negative/zero seeds={r.positive_seeds}/{r.negative_seeds}/{r.zero_seeds}; "
            f"leave-one-seed-out mean [{r.loo_mean_min:+.4f},{r.loo_mean_max:+.4f}].")
    (HERE/'report/primary_results.md').write_text('\n\n'.join(phr)+'\n',encoding='utf-8')
    events=[k for k in data if k.startswith('event_') or k.startswith('relay_loss_')]
    mechanisms={}
    for configuration,g in winter.groupby('configuration'):
        mechanisms[configuration]={k:int(g[k].sum()) for k in events if k!='event_unused_forward_energy_nj'}
        mechanisms[configuration]['source_time_denominator']=int(g.source_time_denominator.sum())
        mechanisms[configuration]['executions']=len(g)
    (HERE/'report/pooled_mechanisms.json').write_text(json.dumps(mechanisms,indent=2)+'\n')
    effect=pd.read_csv(HERE/'results/pooled_winter_effects.csv')
    latex=[r'\documentclass[10pt,a4paper]{article}',r'\usepackage[margin=22mm]{geometry}',
        r'\usepackage{booktabs,amsmath,graphicx,longtable}',r'\usepackage[T1]{fontenc}',
        r'\title{Supplemental Mechanistic Validation of Frozen JLC-R Relay Protection under S200/G20}',
        r'\author{Independent analysis draft}',r'\date{}',r'\begin{document}',r'\maketitle',
        r'\section{Scope and design}',
        'This is a new supplemental mechanism study specified after the original confirmation. '
        'It does not alter the original 480 executions, WP0--WP6, or the original noninferiority family. '
        'An isolated adapter crosses transit admission margin ($T$), two-slot relay demand recognition ($R$), '
        'and the exact local-staleness priority key ($S$). Ordinary charging, single-hop forwarding holds '
        'and safety checks remain enabled in all eight configurations. Both endpoints pass exact frozen-controller '
        'and published-record regression checks. The formal experiment retains all 864 planned executions: '
        '768 across four weather inputs and two supplies, plus 96 at the original T2 nominal-supply Stage III-C3 canopy condition. '
        'Twelve network seeds are paired across every configuration and condition.',
        r'\section{Statistical analysis}',
        'The four primary contrasts first average the T1 and T3 effects at $s=0.7$ within each seed. '
        'Two-sided paired Student tests use $n=12$ independent seed differences, 11 degrees of freedom, '
        'nominal 95\% confidence intervals and a separate Holm family of four tests. '
        'Other conditions and all interactions are descriptive secondary analyses. '
        'An exhaustive 4096-pattern seed sign-flip sensitivity assumes independent symmetric contrasts. '
        'Leave-one-seed-out means and direction counts retain every seed. No equivalence margin is introduced.',
        r'\section{Primary results}',
        primary[['hypothesis','effect','mean_difference','ci95_low','ci95_high','p_two_sided','p_holm4']].to_latex(index=False,float_format='%.6g',escape=True),
        r'\section{Main and interaction effects}',
        'Effects retain native direction: positive coverage/P5 and negative AoI/outage favor enabling the mechanism. '
        'Pairwise interactions average a difference of differences over the remaining factor; the third-order '
        'interaction is the full third difference. These are not regression coefficients. Conditional losses '
        'from the full controller are separate contrasts. The opposing-corner bundle satisfies '
        r'$\mathrm{Bundle}=E_T+E_R+E_S+E_{TRS}/4$.',
        effect[effect.metric.isin(['far_coverage_pct','source_coverage_p5_pct','aoi_mean_minutes'])][['metric','effect','mean_difference','ci95_low','ci95_high']].to_latex(index=False,longtable=True,float_format='%.6g',escape=True),
        r'\section{Interpretation boundaries}',
        'Mechanism event counts are descriptive execution evidence; repeated packets and CH periods do not '
        'increase independent replication. Far-source coverage uses only far-source time. '
        'Source P5 uses the entire source population. Staleness opportunities are distinguished from actual '
        'choice changes. Transit admission margins create neither energy nor Guard slots. Unused reservations '
        'refer to actual committed one-hop holds. Local non-overcommitment does not ensure end-to-end delivery. '
        'Zero, negative and imprecise effects remain valid findings and are not used to tune the frozen controller.',
        r'\end{document}','']
    (HERE/'report/manuscript_text.tex').write_text('\n\n'.join(latex),encoding='utf-8')


if __name__=='__main__':
    main()
