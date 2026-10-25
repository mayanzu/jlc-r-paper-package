"""Gate E: content-addressed offline execution snapshot, without changing root Git."""
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE,PROJECT,SIM,sha


def freeze():
    assert json.loads((HERE/'audit/equivalence_audit.json').read_text())['status']=='PASS'
    pilot=json.loads((HERE/'audit/pilot_audit.json').read_text())
    assert pilot['status']=='PASS' and pilot['completed']==32
    frozen=json.loads((HERE/'audit/frozen_assets_before.json').read_text())
    assert all(sha(PROJECT/name)==expected for name,expected in frozen.items()), 'Frozen asset changed'
    files=[p for p in SIM.iterdir() if p.suffix in ['.py','.json']]
    files += [p for folder in ['src','scripts','tests','configs'] for p in (HERE/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.json']]
    files += [PROJECT/'code/experiments/v6_4_agricultural_extension'/name for name in ['extension_core.py','extension_design.json']]
    for condition in json.loads((SIM/'current_design.json').read_text())['conditions']:
        if condition.get('weather_file'):
            files.append(PROJECT/condition['weather_file'])
    hashes={p.relative_to(PROJECT).as_posix():sha(p) for p in files}
    name=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    snapshot=PROJECT/'temp/relay_ablation_20261024'/('execution_snapshot_'+name)
    snapshot.mkdir()
    for path in hashes:
        dest=snapshot/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(PROJECT/path,dest)
    def git(*args):
        return subprocess.run(['git',*args],cwd=snapshot,capture_output=True,text=True,check=True).stdout.strip()
    git('init','--initial-branch=main')
    git('config','core.autocrlf','false')
    git('add','.')
    git('-c','user.name=JLC-R research audit','-c','user.email=local-audit@example.invalid',
        'commit','-m','Freeze relay factorial implementation, physical inputs and statistical plan before formal execution')
    record=dict(status='FROZEN',created_utc=datetime.now(timezone.utc).isoformat(),
        snapshot_git_commit=git('rev-parse','HEAD'),snapshot_project_relative_path=snapshot.relative_to(PROJECT).as_posix(),
        root_git_head=subprocess.run(['git','rev-parse','HEAD'],cwd=PROJECT,capture_output=True,text=True,check=True).stdout.strip(),
        root_git_worktree='Existing uncommitted work preserved; root index and history not modified.',
        files_sha256=hashes,planned_formal_executions=864,formal_results_present=0,
        equivalence_sha256=sha(HERE/'audit/equivalence_audit.json'),pilot_sha256=sha(HERE/'audit/pilot_audit.json'))
    assert not list((HERE/'results/raw').glob('*.json.gz'))
    (HERE/'audit/execution_freeze.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='files_sha256'},indent=2))


if __name__=='__main__':
    freeze()
