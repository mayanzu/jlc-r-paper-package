"""Independent read-only recomputation of new Table 5 and Holm-4 inference.

No simulator or experiment analysis function is imported. Raw CSV records are
re-paired directly, independently of the analysis pipeline's contrast helper.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import re
import statistics
from scipy import stats

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from paths import ROOT as P, MAIN as C, AUDIT, FIGURES
from article_evidence import full_table_view
H=P/'code/experiments/v6_5_relay_ablation'


def read(name):
    with (H/'results'/name).open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))


def digest(path):
    if not path.exists() and path.parent.name=='figures':path=FIGURES/path.name
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(ms=None):
    ms=(C/'manuscript.md').read_text(encoding='utf-8') if ms is None else ms
    evidence=full_table_view(ms)
    rows=read('formal_runs.csv')
    assert len(rows)==864
    seeds=json.loads((H/'configs/seeds.json').read_text())['formal']
    conditions=json.loads((H/'configs/conditions.json').read_text())
    expected={(c['condition'],float(c['supply']),c['treatment'],s,a)
        for c in conditions['main']+conditions['canopy'] for s in seeds
        for a in ['A000','A001','A010','A011','A100','A101','A110','A111']}
    cases={(r['condition'],float(r['supply']),r['treatment'],int(r['seed']),r['configuration']):r for r in rows}
    assert set(cases)==expected and len(cases)==864
    for row in rows:
        bits=row['configuration'][1:]
        assert [int(row[k]) for k in ['transit_margin_on','two_slot_gate_on','staleness_tie_on']]==list(map(int,bits))
        assert row['ablation_configuration']==row['configuration']
        assert float(row['max_hold_violation_j'])<=1e-8 and float(row['max_slot_violation'])==0
        assert float(row['max_energy_balance_error_j'])<=1e-6 and float(row['max_node_energy_error_j'])<=1e-8
        assert int(row['generated'])+int(row['unsensed'])==134400
        assert int(row['generated'])==sum(int(row[v]) for v in ['delivered','expired','overflow','outstanding'])
    # Independent two-condition seed contrasts for the four prespecified tests.
    seed_effects={h:[] for h in ['H1','H2','H3','H4']}
    for seed in seeds:
        cell_values={h:[] for h in seed_effects}
        for condition in ['WINTER_G20','T3_G20']:
            y={a:cases[condition,.7,'C0',seed,a] for a in ['A000','A001','A010','A011','A100','A101','A110','A111']}
            cell_values['H1'].append(float(y['A111']['far_coverage_pct'])-float(y['A000']['far_coverage_pct']))
            for hypothesis,metric,index in [('H2','far_coverage_pct',0),('H3','coverage_pct',1),('H4','source_coverage_p5_pct',2)]:
                differences=[]
                for key in y:
                    if key[index+1]=='0':
                        enabled=list(key);enabled[index+1]='1';enabled=''.join(enabled)
                        differences.append(float(y[enabled][metric])-float(y[key][metric]))
                assert len(differences)==4
                cell_values[hypothesis].append(statistics.mean(differences))
        for hypothesis,values in cell_values.items():
            assert len(values)==2
            seed_effects[hypothesis].append(statistics.mean(values))
    estimates={}
    for hypothesis,values in seed_effects.items():
        mean=statistics.mean(values);sd=statistics.stdev(values);se=sd/math.sqrt(12)
        half=float(stats.t.ppf(.975,11)*se)
        p=float(2*stats.t.sf(abs(mean/se),11)) if se else (1. if mean==0 else None)
        estimates[hypothesis]=dict(mean_difference=mean,sd_difference=sd,ci95_low=mean-half,ci95_high=mean+half,p_two_sided=p)
    ordered=sorted(estimates,key=lambda h:estimates[h]['p_two_sided'])
    cumulative=0
    for rank,hypothesis in enumerate(ordered):
        cumulative=max(cumulative,min(1.,(4-rank)*estimates[hypothesis]['p_two_sided']))
        estimates[hypothesis]['p_holm4']=cumulative
    published=read('primary_tests.csv')
    assert len(published)==4 and {r['hypothesis'] for r in published}==set(estimates)
    for row in published:
        assert int(row['n'])==12 and int(row['df'])==11
        for field,value in estimates[row['hypothesis']].items():
            assert math.isclose(float(row[field]),value,rel_tol=1e-10,abs_tol=1e-10),(row['hypothesis'],field)
    # Current main Table 4 must show all four tests, including unresolved H2/H3.
    block=re.search(r'^Table 4\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)',evidence,re.M)
    assert block,'Missing primary relay tests'
    primary_display=[[v.strip() for v in line.strip().strip('|').split('|')]
                     for line in block[1].splitlines()][2:]
    assert len(primary_display)==4 and all(len(row)==5 for row in primary_display)
    for row,hypothesis in zip(primary_display,['H1','H2','H3','H4']):
        assert row[0].startswith(hypothesis+':')
        values=re.findall(r'[+-]?\d+\.\d+',row[2])
        assert len(values)==3
        estimate=estimates[hypothesis]
        for value,field in zip(values,['mean_difference','ci95_low','ci95_high']):
            assert abs(float(value)-estimate[field])<=.000500001,(hypothesis,field)
        for value,field in zip(row[3:5],['p_two_sided','p_holm4']):
            assert abs(float(value)-estimate[field])<=.000000500001,(hypothesis,field)
    # Displayed absolute means: average the two winters within each seed first.
    block=re.search(r'^Table 5\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)',evidence,re.M)
    assert block,'Missing relay factorial table'
    displayed=[[v.strip() for v in line.strip().strip('|').split('|')] for line in block[1].splitlines()][2:]
    assert len(displayed)==8 and all(len(r)==10 for r in displayed)
    metrics=['coverage_pct','far_coverage_pct','source_coverage_p5_pct','aoi_mean_minutes','night_off_pct','consumed_j']
    for row in displayed:
        configuration=row[0].split()[0]
        assert configuration in cases['WINTER_G20',.7,'C0',seeds[0],configuration]['configuration']
        assert row[1:4]==list(configuration[1:])
        for column,metric in enumerate(metrics,4):
            values=[statistics.mean([float(cases[c,.7,'C0',seed,configuration][metric]) for c in ['WINTER_G20','T3_G20']]) for seed in seeds]
            actual=statistics.mean(values)/(60 if metric=='aoi_mean_minutes' else 1)
            assert abs(float(row[column])-actual)<=.000500001,(configuration,metric,row[column],actual)
    metadata=json.loads((AUDIT/'relay_ablation_data.json').read_text())
    for relative,expected_sha in metadata['files_sha256'].items():
        assert digest(P/relative)==expected_sha,relative
    for token in metadata.get('primary_claim_tokens',[]):
        assert token in ms,token
    assert '## 4.3 Mechanism and agricultural studies' in ms
    assert 'separate four-test Holm family' in ms and 'post-confirmation plan' in ms
    assert 'local' in ms and 'Local safety neither guarantees end-to-end delivery' in ms
    assert 'figures/fig5_relay_ablation.svg' in ms
    mapping=json.loads((H/'audit/canopy_map_audit.json').read_text())
    assert mapping['status']=='PASS' and mapping['node_stage_records']==3600
    assert 'T_i=T_{min}+(T_{max}-T_{min})c_i' in ms
    assert 'T_i=T_{max}-(T_{max}-T_{min})c_i' not in ms
    return dict(formal_executions=864,primary_seed_units=12,holm_family=4,
        independent_primary_recomputations=4,table_numeric_cells=68,all_configurations=8,
        primary_estimates=estimates,
        original_confirmation_family_unchanged=True,raw_audit=json.loads((H/'audit/final_ablation_audit.json').read_text())['status'])


if __name__=='__main__':
    print(json.dumps(check(),indent=2))
