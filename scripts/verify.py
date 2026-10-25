"""Verify immutable evidence and independently recompute statistics; no simulation."""
from pathlib import Path, PurePosixPath
import csv,hashlib,json,sys
import numpy as np
from paths import ROOT,AUDIT

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def verify(check_manifest=True):
    if check_manifest:
        lines=(ROOT/'audit/checksums.sha256').read_text(encoding='utf-8').splitlines()
        expected={}
        for line in lines:
            h,name=line.split('  ',1);rel=PurePosixPath(name)
            assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in name
            assert digest(ROOT/name)==h,name;expected[name]=h
        actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()
                and not any(n in p.relative_to(ROOT).parts for n in ['.git','__pycache__','outputs','.venv'])
                and p.relative_to(ROOT).as_posix() not in ['audit/checksums.sha256','SNAPSHOT_MANIFEST.sha256']}
        assert actual==set(expected),f'Unmanifested/missing files: {actual^set(expected)}'
    else:expected={}
    original=json.loads((ROOT/'audit/original_record_hashes.json').read_text(encoding='utf-8'))
    for name,h in original['files_sha256'].items():assert digest(ROOT/name)==h,name
    from source_archives import verify_source_archive
    archive=verify_source_archive()
    from mechanisms import inspect_study
    mechanism=inspect_study()
    ab=ROOT/'code/experiments/v6_5_relay_ablation'
    freeze=json.loads((ab/'audit/execution_freeze.json').read_text(encoding='utf-8'))
    for name,h in freeze['files_sha256'].items():assert digest(ROOT/name)==h,name
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(AUDIT))
    from analysis.recompute_confirmation import recompute
    from check_scientific_consistency import audit
    confirmation=recompute();paper=audit()
    datasets={
        'confirmation_480':'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv',
        'supply_576':'code/experiments/v6_4_agricultural_extension/results/supply.csv',
        'freshness_480':'code/experiments/v6_4_agricultural_extension/results/freshness.csv',
        'canopy_384':'code/experiments/v6_4_agricultural_extension/results/canopy.csv',
        'relay_ablation_864':'code/experiments/v6_5_relay_ablation/results/formal_runs.csv'}
    resources={}
    for label,name in datasets.items():
        data=rows(ROOT/name);assert len(data)==int(label.rsplit('_',1)[1])
        for row in data:
            for field,tol in [('max_hold_violation_j',1e-8),('max_slot_violation',0),('max_energy_balance_error_j',1e-6),('max_node_energy_error_j',1e-8)]:
                if field in row and row[field]!='':assert float(row[field])<=tol,(label,field)
            if all(k in row for k in ['generated','unsensed','delivered','expired','overflow','outstanding']):
                assert int(row['generated'])+int(row['unsensed'])==134400
                assert int(row['generated'])==sum(int(row[k]) for k in ['delivered','expired','overflow','outstanding'])
        resources[label]=len(data)
    return {'status':'passed','reproduction_coverage':'main Tables 1-5, full E1-E8, independent reliability trajectories and parameter evidence','manifest_files':len(expected),'original_frozen_files':len(original['files_sha256']),
        'confirmation':confirmation,'paper_consistency':paper,'resource_summary_rows':resources,
        'source_archive':archive,'mechanism_rerun_readiness':mechanism,
        'new_simulations':0,
        'resource_check_scope':'Supplied seed-level maxima and demand ledgers.'}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
