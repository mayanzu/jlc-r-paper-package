"""Read-only source, retained-data, table and primary-inference verification.

No simulator is imported or executed. Covers the released confirmation matrix
and specified displays, not field validity or summary-only historical records.
"""
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
import argparse,csv,hashlib,itertools,json,re
import numpy as np
from scipy import stats
from check_extension import check as check_extension
from check_relay_ablation import check as check_relay_ablation

import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from paths import ROOT as PROJECT, MAIN as COMPAG, AUDIT, TECH
from article_evidence import full_table_view,check_main_tables
EVIDENCE=PROJECT/'code/experiments/v6_3_relay_repair'
METRICS=['coverage_pct','aoi_mean_minutes','source_coverage_p5_pct','night_off_pct']
CONDITIONS={'Synthetic':'SYNTHETIC_G20','T1 winter':'WINTER_G20','T2 spring':'T2_G20','T3 winter':'T3_G20'}
ALIASES={'JLC-R':'JLC-R-HYB-V63','Prefix-only':'JLC-R-SA','Hybrid control':'JLC-R-HYB','PADC-AGE':'PADC-AGE','PADC+relay':'PADC-AGE+V63'}
SEEDS=list(range(160101,161213,101))

def require(condition,message):
    if not condition:raise AssertionError(message)

def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))

def table(text,label):
    match=re.search(r'^Table '+re.escape(label)+r'\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)',text,re.M)
    require(match is not None,f'Missing table {label}')
    rows=[[v.strip() for v in line.strip().strip('|').split('|')] for line in match[1].splitlines()]
    require(len(rows)>=3 and all(len(r)==len(rows[0]) for r in rows),f'Table {label} shape')
    return rows[0],rows[2:]

def table_context(text,label):
    match=re.search(r'^Table '+re.escape(label)+r'\..*?(?=^Table S?\d+\.|\Z)',text,re.M|re.S)
    require(match is not None,f'Missing table context {label}')
    return match[0]

def displayed(value,actual,label):
    """Compare to the rounding unit actually printed, including scientific p."""
    require(re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',value) is not None,f'{label}: invalid number {value!r}')
    mantissa,*exponents=re.split('[eE]',value)
    decimals=len(mantissa.split('.',1)[1]) if '.' in mantissa else 0
    exponent=int(exponents[0]) if exponents else 0
    tolerance=.50001*10.**(exponent-decimals)+1e-12
    require(abs(float(value)-actual)<=tolerance,f'{label}: displayed {value}, recomputed {actual:.14g}')

def holm(probabilities):
    values=np.asarray(probabilities,dtype=float);order=np.argsort(values,kind='stable');adjusted=np.empty(len(values))
    adjusted[order]=np.minimum(1.,np.maximum.accumulate(values[order]*(len(values)-np.arange(len(values)))))
    return adjusted

def one_sided(values):
    values=np.asarray(values,dtype=float);sd=float(values.std(ddof=1))
    if sd<1e-14:return (float('inf'),0.) if values.mean()>0 else (float('-inf'),1.)
    statistic=float(values.mean()/(sd/np.sqrt(len(values))))
    return statistic,float(stats.t.sf(statistic,len(values)-1))

def confirmation(records):
    expected=set(itertools.product(CONDITIONS.values(),(1.,.7),SEEDS,ALIASES.values()));indexed={}
    for row in records:
        key=row['condition'],float(row['supply']),int(row['seed']),row['method']
        require(key not in indexed,f'Duplicate confirmation key {key}');indexed[key]=row
        for metric in METRICS+['consumed_j']:
            value=float(row[metric]);require(np.isfinite(value) and value>=0,f'Invalid {metric}: {key}')
            if metric in ['coverage_pct','source_coverage_p5_pct','night_off_pct']:require(value<=100,f'Percentage bound {key}, {metric}')
        require(float(row['max_hold_violation_j'])==0 and float(row['max_slot_violation'])==0,f'Recorded safety maximum {key}')
    require(set(indexed)==expected,f'Confirmation matrix mismatch; missing={len(expected-set(indexed))}, extra={len(set(indexed)-expected)}')
    def vector(c,s,method,metric):return np.array([float(indexed[c,s,seed,method][metric]) for seed in SEEDS])
    means={(c,s,method):{metric:float(vector(c,s,method,metric).mean()) for metric in METRICS+['consumed_j']}
           for c,s,method in itertools.product(CONDITIONS.values(),(1.,.7),ALIASES.values())}
    tests=[]
    for c,s in itertools.product(CONDITIONS.values(),(1.,.7)):
        baseline='JLC-R-SA' if c in ['SYNTHETIC_G20','T2_G20'] else 'PADC-AGE'
        for metric in METRICS:
            a=vector(c,s,'JLC-R-HYB-V63',metric);b=vector(c,s,baseline,metric);difference=a-b
            margin=-1. if metric in ['coverage_pct','source_coverage_p5_pct'] else (1. if metric=='night_off_pct' else .05*b.mean())
            favorable=difference-margin if margin<0 else margin-difference
            relative=1.05*b-a if metric=='aoi_mean_minutes' else favorable
            statistic,probability=one_sided(favorable);rel_statistic,rel_probability=one_sided(relative)
            se=difference.std(ddof=1)/np.sqrt(12)
            result=dict(condition=c,supply=s,baseline=baseline,metric=metric,mean_diff=float(difference.mean()),sd_diff=float(difference.std(ddof=1)),margin=float(margin),t_stat=statistic,p_raw=probability,t_stat_rel=rel_statistic,p_rel=rel_probability,deterministic_tie=bool(np.all(difference==0)))
            for level in [90,95]:
                width=stats.t.ppf(.5+level/200,11)*se
                result[f'ci{level}_lo']=float(difference.mean()-width);result[f'ci{level}_hi']=float(difference.mean()+width)
            tests.append(result)
        if c in ['WINTER_G20','T3_G20']:
            delta=vector(c,s,'JLC-R-HYB-V63','coverage_pct')-vector(c,s,'JLC-R-SA','coverage_pct')
            _,probability=one_sided(delta)
            tests.append(dict(condition=c,supply=s,metric='coverage_superiority',p_raw=probability))
    for result,p in zip(tests,holm([r['p_raw'] for r in tests])):result['p_holm36']=float(p)
    ni=[r for r in tests if r['metric']!='coverage_superiority']
    repair=vector('WINTER_G20',1.,'JLC-R-HYB','aoi_mean_minutes')-vector('WINTER_G20',1.,'JLC-R-HYB-V63','aoi_mean_minutes')
    _,repair_p=one_sided(repair)
    for result,p in zip(ni,holm([r['p_rel'] for r in ni]+[repair_p])[:-1]):result['p_rel_holm33']=float(p)
    require(len(tests)==36 and len(ni)==32,'Primary family size')
    require(sum(r['deterministic_tie'] for r in ni)==1,'Deterministic tie count')
    require(all(r['p_holm36']<.05 for r in tests),'Primary Holm decisions differ from manuscript')
    return means,tests,ni

def check_tables(ms,sup,means,ni):
    counts={};_,rows=table(ms,'2')
    require(len(rows)==40 and len({tuple(r[:3]) for r in rows})==40,'Table 2 row keys')
    for row in rows:
        require(len(row)==9,'Table 2 columns');method=row[2].replace('$^{*}$','')
        expected=means[CONDITIONS[row[0]],float(row[1]),ALIASES[method]]
        for value,metric in zip(row[3:8],METRICS+['consumed_j']):displayed(value,expected[metric],f'Table 2 {row[:3]} {metric}')
        if method=='JLC-R':
            require(row[2]=='JLC-R$^{*}$','JLC-R primary NI annotation')
            maximum=max(t['p_holm36'] for t in ni if t['condition']==CONDITIONS[row[0]] and t['supply']==float(row[1]))
            displayed(row[8],maximum,f'Table 2 primary Holm maximum {row[:2]}')
        else:require(row[2]==method and row[8]=='---','Only primary JLC-R comparisons receive NI marks')
    counts['Extended Table E2']=208;_,rows=table(sup,'S67')
    require(len(rows)==40 and len({tuple(r[:3]) for r in rows})==40,'S67 row keys')
    for row in rows:
        require(len(row)==8,'S67 columns');expected=means[CONDITIONS[row[0]],float(row[1]),ALIASES[row[2]]]
        for value,metric in zip(row[3:],METRICS+['consumed_j']):displayed(value,expected[metric],f'S67 {row[:3]} {metric}')
    counts['Table S67']=200;tests={(r['condition'],r['supply'],r['metric']):r for r in ni};_,rows=table(sup,'S68')
    require(len(rows)==8 and len({tuple(r[:2]) for r in rows})==8,'S68 row keys')
    for row in rows:
        require(len(row)==6,'S68 columns')
        for value,metric in zip(row[2:],METRICS):
            values=re.findall(r'[+-]?\d+\.\d+',value);require(len(values)==3,f'S68 effect/CI shape: {value}')
            result=tests[CONDITIONS[row[0]],float(row[1]),metric]
            for number,field in zip(values,['mean_diff','ci95_lo','ci95_hi']):displayed(number,result[field],f'S68 {row[:2]} {metric} {field}')
    counts['Table S68']=96
    metric_labels={'Coverage':'coverage_pct','Mean AoI':'aoi_mean_minutes','P5':'source_coverage_p5_pct','Night outage':'night_off_pct'}
    _,rows=table(sup,'S63');require(len(rows)==32 and len({tuple(r[:3]) for r in rows})==32,'S63 row keys')
    for row in rows:
        result=tests[CONDITIONS[row[0]],float(row[1]),metric_labels[row[2]]]
        for value,field in zip(row[3:7],['mean_diff','p_raw','p_holm36','p_rel_holm33']):displayed(value,result[field],f'S63 {row[:3]} {field}')
        require(row[7]=='NI',f'S63 decision {row[:3]}')
    counts['Table S63']=128
    return counts

def check_article_core(ms,sup):
    layout=json.loads((AUDIT/'article_layout.json').read_text(encoding='utf-8'))
    require(re.findall(r'^Table ([A-Z]?\d+)\.',ms,re.M)==['1','2','3','4','5'],'Article table inventory')
    _,parameters=table(ms,'1');_,legacy=table(sup,'S2')
    expected=[r if r[0]!='Listening' else ['Listening','Member/CH caps; guard per transaction','0.1/1 s; 20 ms (G20)'] for r in legacy]
    expected.insert(next(i for i,r in enumerate(expected) if r[0]=='Grants'),['Synchronization','Interval; window; paid windows per round','200 s; 20 ms; 5 (S200)'])
    require(parameters==expected,'Current parameter table; legacy scientific parameters otherwise unchanged')
    design=json.loads((PROJECT/'code/simulation/current_design.json').read_text(encoding='utf-8'))
    require(all(c['config']['guard_listen_s']==.02 and c['config']['sync_interval_s']==200 and c['config']['sync_window_count']==5 for c in design['conditions']),'Parameter display matches frozen current timing')
    _,components=table(full_table_view(ms),'3')
    require(len(components)==3,'Only seed-recomputable G10 budget controls belong in main Table 3')
    records=read_csv(PROJECT/'code/results/strengthening/floor/metrics.csv')
    for target,(first,second) in enumerate([('JLC-R','JLC-R-FIXED'),('JLC-R','JLC-R-NF'),('JLC-R-SA','JLC-R-SA-NF')]):
        require(components[target][1]=='12 paired','Historical paired unit count')
        for column,supply in [(2,1.),(3,.7)]:
            arms={m:{int(r['seed']):float(r['coverage_pct']) for r in records
                     if r['method']==m and float(r['supply'])==supply} for m in [first,second]}
            require(set(arms[first])==set(arms[second]) and len(arms[first])==12,'Complete floor pairing')
            delta=np.array([arms[first][seed]-arms[second][seed] for seed in sorted(arms[first])])
            mean=float(delta.mean());half=float(stats.t.ppf(.975,11)*delta.std(ddof=1)/np.sqrt(12))
            numbers=re.findall(r'[+-]?\d+\.\d+',components[target][column])
            require(len(numbers)==3,'Table 3 mean/CI shape')
            for value,actual in zip(numbers,[mean,mean-half,mean+half]):
                displayed(value,actual,f'Table 3 raw-seed recomputation {target}, supply {supply}')
    require('99.01%' not in ms and '16.74' not in ms,'Unsupported historical attribution removed from main claims')
    proof_path=PROJECT/layout['proof_source']
    require(hashlib.sha256(proof_path.read_bytes()).hexdigest()==layout['repository_proofs_sha256'],
            'Complete original analytical derivations retained in repository')
    proof_text=proof_path.read_text(encoding='utf-8')
    for label,digest in layout['main_statement_sha256'].items():
        pattern=r'^\*\*'+re.escape(label)+r'\b[^\n]+'
        main_statement=re.search(pattern,ms,re.M);full_statement=re.search(pattern,proof_text,re.M)
        require(main_statement is not None and full_statement is not None,f'Core statement retained: {label}')
        require(main_statement[0].replace('Section 3.3','Section 4.3')==full_statement[0] and hashlib.sha256(main_statement[0].replace('Section 3.3','Section 4.3').encode()).hexdigest()==digest,
                f'Exact original hypotheses and statement: {label}')
    require(ms.count('*Proof sketch.*')==4 and '**Proof sketch of Lemma 1.**' in ms,
            'Main paper supplies proof sketches for every retained safety/service result')
    require(table(proof_text,'A1')==table(sup,'S69'),'Complete reservation transitions retained in repository')
    mapping=json.loads((PROJECT/'configs/article_figure_map.json').read_text())
    declared=re.findall(r'!\[[^\]]*\]\(figures/([^\)]+)\.svg\)\{width=100%\}\s*\nFigure (\d+)\.',ms)
    require({number:stem for stem,number in declared}==mapping['main'],'Five main figure identities and labels')
    require('Repository Figure R1' not in ms and 'Repository Figure R2' not in ms,'Main text is self-contained; repository figures are not required')
    require(not re.search(r'Supplementary|\bHTR\b',ms),'Archive pointers must not be described as a separately submitted supplement')
    require('All 32 NI criteria' in ms and 'The last column is the largest adjusted p among those four NI contrasts' in ms and 'No NI criterion is defined for energy' in ms,'Objective NI annotation definition')
    require("h_i'" not in ms and ms.count(r'h_i^{\,\prime}')>=2,'Consistent spaced prime in hybrid-state notation')
    require('less than 2 ms' not in ms and '0.24 s' not in ms and 'no embedded runtime has been measured' in ms,'No unverified runtime measurement')
    require(not re.search(r'JLC-R-HYB|HYB60|OC-v1|JLC-R-Cont|JLC-R-Prefix',ms.split('# Data and Code Availability')[0]),'Academic names in article body')
    return {'parameters_verified':len(parameters),'five_method_rows':40,'exact_core_statements':6,
            'complete_repository_proofs_verified':True,'main_figures':5,'repository_figures':2,'formal_supplementary_references':0}

def check_published_tests(ni):
    published=read_csv(EVIDENCE/'D_noninferiority_seeds16.csv');computed={(r['condition'],r['supply'],r['metric']):r for r in ni}
    keys=[(r['condition'],float(r['supply']),r['metric']) for r in published]
    require(len(published)==len(set(keys))==32 and set(keys)==set(computed),'Published NI keys')
    fields=['mean_diff','sd_diff','ci90_lo','ci90_hi','ci95_lo','ci95_hi','margin','t_stat','p_raw','t_stat_rel','p_rel','p_holm36','p_rel_holm33']
    for row,key in zip(published,keys):
        expected=computed[key];require(row['baseline']==expected['baseline'],f'Published baseline {key}')
        for field in fields:require(np.isclose(float(row[field]),expected[field],atol=1e-10,rtol=1e-9),f'Published {field} mismatch {key}')

def check_historical_sources(sup):
    """Keep the original historical identity/timing/direction checks in the HTR."""
    for n in [46,48,49,50,51,52]:
        block=table_context(sup,'S'+str(n))
        require('**Table note.**' in block and 'JLC-R-Prefix' in block,f'S{n} local historical identity')
        require('JLC-R (opt.)' not in block and 'JLC-R (orig.)' not in block,f'S{n} ambiguous historical label')
    for n in [50,52]:
        block=table_context(sup,'S'+str(n))
        require(not any(x in block for x in ['coverage pct','aoi mean minutes','consumed j']),f'S{n} display metrics')
    for n,timing in [(46,'G10'),(48,'S100/G10'),(49,'S100/G20'),(50,'S100/G20'),(51,'S100/G20'),(52,'S100/G20')]:
        require(timing in table_context(sup,'S'+str(n)),f'S{n} historical timing')
    _,registry_rows=table(sup,'S71')
    for study in ['Recent duty-rule controls','Optimized-prefix study','Reference-floor ablation','Long-horizon rescue']:
        row=next(r for r in registry_rows if r[0].startswith(study))
        require('Base timing/G10' in row[3],f'{study} retained G10 configuration')
    require('JOINT had higher mean coverage and lower mean AoI than the scheduled configuration at both supplies' in sup,'S25 prose direction')
    _,rows=table(sup,'S25')
    for supply in [1.,.7]:
        candidates=[r for r in rows if float(r[1])==supply]
        joint=next(r for r in candidates if r[0]=='JOINT');scheduled=next(r for r in candidates if r[0]=='Scheduled')
        require(float(joint[2])>float(scheduled[2]) and float(joint[4])<float(scheduled[4]),'S25 JOINT/Scheduled numeric direction')

def analytical_blocks(source):
    blocks={}
    patterns={
        'lemma_statement':r'^\*\*Lemma 1\b.*?(?=^\*\*Proposition 1)',
        'theorem_statement':r'^\*\*Theorem 1\b.*?\n\n\*Proof\.\* [^\n]+',
        'corollary':r'^\*\*Corollary 1\b[^\n]+',
        'lemma_proof':r'^\*\*Proof of Lemma 1\.\*\*.*?(?=^\*\*Proof of Theorem 1)',
        'theorem_proof':r'^\*\*Proof of Theorem 1\.\*\*.*?(?=^Table S69\.)',
        **{'proposition_'+str(n):r'^\*\*Proposition '+str(n)+r'\b.*?\n\n\*Proof\.\* [^\n]+' for n in [1,2,3]},
    }
    for name,pattern in patterns.items():
        match=re.search(pattern,source,re.M|re.S);require(match is not None,f'Missing analytical block {name}')
        blocks[name]=hashlib.sha256(match[0].strip().encode()).hexdigest()
    return blocks

def check_layout(sup):
    layout=json.loads((AUDIT/'supplementary_layout.json').read_text(encoding='utf-8'))
    labels=re.findall(r'^Table (S\d+)\.',sup,re.M)
    require(labels==layout['retained_tables'] and len(labels)==len(set(labels)),'Curated table inventory')
    for label,expected in layout['retained_table_data_sha256'].items():
        raw=re.search(r'^Table '+label+r'\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)',sup,re.M)[1].strip()
        require(hashlib.sha256(raw.encode()).hexdigest()==expected,f'{label} original table data preserved')
    require('The first two benchmark seeds had previous synchronization-debug/fixture use.' in sup,'Benchmark prior-use disclosure')
    require('pre-repair HYB60 controller passed 29/32' in sup,'Pre-repair NI boundary')
    require('31/32 NI passes in the new-seed cohort' in sup and 'not established there at the stricter' in sup,'Conservative inference boundary')
    require(analytical_blocks(sup)==layout['preserved_analytical_blocks_sha256'],'Complete original analytical statements and proofs preserved')
    return layout

def check_archive(archive):
    """Optional explicit local companion check; core audit remains portable."""
    layout=json.loads((AUDIT/'supplementary_layout.json').read_text(encoding='utf-8'))
    frozen=archive/'frozen_before_reorganization/supplementary.md'
    require(hashlib.sha256(frozen.read_bytes()).hexdigest()==layout['frozen_supplementary_sha256'],'Frozen supplementary source hash')
    original=frozen.read_text(encoding='utf-8')
    history=(archive/'historical_technical_report.md').read_text(encoding='utf-8')
    history=re.sub(r'\bH(\d+)\b',lambda m:'S'+m[1] if int(m[1])<=72 else m[0],history)
    for label,expected in layout['frozen_table_data_sha256'].items():
        for source in [original,history]:
            raw=re.search(r'^Table '+label+r'\. [^\n]*\n\s*\n((?:\|[^\n]*\n)+)',source,re.M)[1].strip()
            require(hashlib.sha256(raw.encode()).hexdigest()==expected,f'Archived {label} original data preserved')
    check_historical_sources(original);check_historical_sources(history)
    require(len(re.findall(r'^Figure S\d+\.',history,re.M))==12,'Archived figure count')
    for line in (archive/'ARCHIVE_MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
        checksum,name=line.split('  ',1);path=archive/name
        require(path.resolve().is_relative_to(archive.resolve()),'Archive manifest path')
        require(hashlib.sha256(path.read_bytes()).hexdigest()==checksum,f'Archive checksum {name}')
    return dict(tables_preserved=72,figures_preserved=12,frozen_supplementary_pages=51)

def check_sources(ms,sup):
    compact=re.sub(r'\s+','',ms)
    formula=re.search(r'A_i\(t\)=\\begin\{cases\}(.*?)\\end\{cases\}',compact)
    require(formula is not None,'Piecewise AoI definition')
    require(formula[1]==r'[t-v_i(t)+1]\Deltat,&v_i(t)\ge0,\\(t+1)\Deltat,&v_i(t)=-1.','Frozen AoI branches')
    require(r'\mathbf1\{v_i(t)\ge0,' in compact,'Freshness requires delivery')
    require('transit screening' in ms and 'Before the receiver response' in ms,'Pre-response protection')
    require('pay its response' not in ms or 'receiver pays its response' in ms,'Charged response')
    for token in ['sender payment','failed requests retain incurred fees','one attempt','expire at round end','current node action loop','reduced-form transmittance--attenuation parameterization','not calibrated probability coverage','not a network-freshness optimum','no embedded runtime has been measured']:
        require(token in ms,token)
    require(r'\sup_{a_i}' in ms and 'not necessarily an attained continuous optimum' in ms,'Integer supremum')
    require('spatial median across nodes' in ms and r'g(\tau)>0.1' in ms,'Causal normalization')
    layout=check_layout(sup)
    sections=set(re.findall(r'^#{1,2} (\d+(?:\.\d+)?)\s',ms,re.M))
    for number in re.findall(r'\bSections?\s+(\d+(?:\.\d+)?)',ms):require(number in sections,f'Unknown main section {number}')
    table_labels=set(re.findall(r'^Table ([SEA]?\d+)\.',ms+'\n'+sup,re.M))
    for label in re.findall(r'\bTables? ([SEA]?\d+)',ms):require(label in table_labels,f'Unknown table {label}')
    figure_labels=set(re.findall(r'^Figure (S?\d+)\.',ms,re.M))
    for label in re.findall(r'\bFigures? (S?\d+)',ms):require(label in figure_labels,f'Unknown figure {label}')
    bib=(COMPAG/'references.bib').read_text(encoding='utf-8');bib_keys=set(re.findall(r'@\w+\{([^,]+),',bib));cited=set()
    for block in re.findall(r'\[(@[^\]]+)\]',ms+'\n'+sup):cited.update(re.findall(r'@([\w-]+)',block))
    require(cited<=bib_keys,f'Missing bibliography keys {cited-bib_keys}')
    return dict(tables=len(table_labels),citations=len(cited),archived_tables=len(layout['archived_tables']))


def check_registry():
    registry=json.loads((AUDIT/'study_registry.json').read_text(encoding='utf-8'));seen=set();verified=0
    coverage=json.loads((PROJECT/'audit/data_coverage.json').read_text(encoding='utf-8'))['cohorts']
    for cohort in registry['cohorts']:
        require(cohort['name'] not in seen,'Duplicate registry identity');seen.add(cohort['name']);path=PROJECT/cohort['path']
        if not path.is_file():
            require(coverage[cohort['name']]=='seed-use-only',f'Missing public data {path}');continue
        verified+=1
        require(path.resolve().is_relative_to(PROJECT),f'Registry path {path}')
        require(hashlib.sha256(path.read_bytes()).hexdigest()==cohort['sha256'],f'Registry source hash {cohort["name"]}')
        rows=read_csv(path);require(len(rows)==cohort['rows'],f'Registry rows {cohort["name"]}')
        require(sorted({int(r['seed']) for r in rows})==cohort['seeds'],f'Registry seeds {cohort["name"]}')
        methods=sorted({r['method'] for r in rows});require(methods==cohort['methods'] and set(cohort['display_aliases'])<=set(methods),f'Registry method IDs {cohort["name"]}')
        if 'configuration_source' in cohort:
            config_path=PROJECT/cohort['configuration_source']
            require(hashlib.sha256(config_path.read_bytes()).hexdigest()==cohort['configuration_sha256'],f'Configuration hash {cohort["name"]}')
            source=json.loads(config_path.read_text(encoding='utf-8'));base=source['config']
            conditions=source.get('design',{}).get('conditions',[{'name':'default','config':{}}])
            guards={c['name']:c.get('config',{}).get('guard_listen_s',base['guard_listen_s']) for c in conditions}
            require(guards==cohort['guard_seconds_by_condition'],f'Registry guard configuration {cohort["name"]}')
            if cohort['timing'].startswith('base/G10'):
                require(set(guards.values())=={.01},f'Base G10 provenance {cohort["name"]}')
    current=next(c for c in registry['cohorts'] if c['name']=='independent_confirmation')
    require(current['display_aliases']=={v:k for k,v in ALIASES.items()},'Current display/CSV identities')
    return verified

def audit(ms=None,sup=None,records=None):
    ms=(COMPAG/'manuscript.md').read_text(encoding='utf-8') if ms is None else ms
    sup=(TECH/'technical_documentation.md').read_text(encoding='utf-8') if sup is None else sup
    records=read_csv(EVIDENCE/'D_confirmation_metrics_seeds16.csv') if records is None else records
    means,tests,ni=confirmation(records);check_published_tests(ni);counts=check_tables(full_table_view(ms),sup,means,ni);counts.update(check_main_tables(ms,table))
    inventory=check_sources(ms,sup);cohorts=check_registry();article=check_article_core(ms,sup)
    extension=check_extension(ms)
    relay=check_relay_ablation(ms)
    from check_submission_strengthening import check as check_strengthening
    strengthening=check_strengthening(ms)
    return dict(scope='Retained records and supplemental factorial study; no simulation or field-validation claim.',confirmation_rows=len(records),ni_contrasts=len(ni),stochastic_ni_passes=sum(not r['deterministic_tie'] for r in ni),deterministic_ties=sum(r['deterministic_tie'] for r in ni),winter_superiority_tests=4,maximum_primary_holm_p=max(r['p_holm36'] for r in tests),displayed_numbers=counts,published_statistics_compared=32,retained_cohorts_verified=cohorts,source_inventory=inventory,article_core=article,extension=extension,relay_ablation=relay,submission_strengthening=strengthening)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--json',type=Path,help='Optional report path; default writes no files');parser.add_argument('--archive-root',type=Path,help='Optional historical companion directory for relocation verification');args=parser.parse_args()
    result=audit()
    if args.archive_root:result['historical_archive']=check_archive(args.archive_root)
    if args.json:args.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2));print('Scientific consistency verified against retained data; no simulation executed.')

if __name__=='__main__':main()
