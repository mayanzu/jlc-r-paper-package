"""Inspect original G10 study dependencies without running the experiment."""
from pathlib import Path
from itertools import product
import csv,hashlib,importlib,json,sys

ROOT=Path(__file__).resolve().parents[3]
SIM=Path(__file__).resolve().parent/'simulation'

def inspect_study():
    manifest=ROOT/'audit/mechanism_source_manifest.json'
    if not manifest.is_file():manifest=Path(__file__).resolve().parent/'manifest.json'
    frozen=json.loads(manifest.read_text(encoding='utf-8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    provenance=json.loads((ROOT/frozen['provenance']).read_text(encoding='utf-8'))
    assert sha(ROOT/frozen['provenance'])==frozen['provenance_sha256']
    for name,digest in frozen['source_sha256'].items():
        assert sha(ROOT/name)==digest,name
        assert digest==provenance['source_sha256']['simulation/'+Path(name).name],name
    assert sha(ROOT/frozen['config']['path'])==frozen['config']['sha256']
    assert sha(ROOT/frozen['specification']['path'])==frozen['specification']['sha256']==provenance['spec_sha256']
    assert sha(ROOT/frozen['design'])==frozen['design_sha256']==provenance['design_sha256']
    sys.path.insert(0,str(SIM))
    import run_strengthening
    import expansion_driver
    assert Path(run_strengthening.__file__).resolve()==SIM/'run_strengthening.py'
    assert expansion_driver.load_config()==provenance['config'],'Recorded effective G10 configuration differs'
    loaded={Path(m.__file__).resolve() for m in tuple(sys.modules.values())
            if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==SIM}
    expected={ROOT/name for name in frozen['source_sha256']}
    assert loaded==expected,(loaded^expected)
    design=json.loads((ROOT/frozen['design']).read_text(encoding='utf-8'))
    assert design==provenance['design']
    cases={(c['name'],float(supply),int(seed),policy) for c,supply,seed,policy in
           product(design['conditions'],design['supplies'],design['seeds'],design['policies'])}
    with (ROOT/frozen['reference_metrics']).open(encoding='utf-8-sig',newline='') as stream:
        original={(r['condition'],float(r['supply']),int(r['seed']),r['method']) for r in csv.DictReader(stream)}
    assert cases==original and len(cases)==120
    return {'study':'mechanisms','planned_cases':120,'days':design['days'],
            'source_modules_verified':len(expected),'imports_verified':True,
            'effective_config_matches_original_provenance':True,'seed_case_identities_match':True,
            'timing':'base/G10','dry_run':True,'simulations_started':0}

if __name__=='__main__':
    if sys.argv[1:]!=['--inspect']:raise SystemExit('Use scripts/reproduce.py --mode rerun --study mechanisms [--dry-run]')
    print(json.dumps(inspect_study(),indent=2))
