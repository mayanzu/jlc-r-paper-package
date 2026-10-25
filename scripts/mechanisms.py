"""Safe dispatch to the exact Table 3 G10 experiment in an isolated process."""
from pathlib import Path
import csv,json,os,subprocess,sys
from paths import ROOT

def inspect_study():
    entry=ROOT/'code/reproduction/mechanisms/entry.py'
    result=subprocess.run([sys.executable,'-B',str(entry),'--inspect'],cwd=ROOT,
                          capture_output=True,text=True,encoding='utf-8',check=True)
    return json.loads(result.stdout)

def execute(out,workers=1,dry_run=False):
    if workers<1:raise ValueError('workers must be positive')
    report=inspect_study()
    if dry_run:return report
    out=Path(out).resolve()
    if out.exists():raise ValueError('Rerun output must be a new directory')
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/'outputs'):
        raise ValueError('Refusing to write into frozen package inputs')
    harness=ROOT/'code/reproduction/mechanisms/simulation/run_strengthening.py'
    design=ROOT/'code/results/strengthening/floor/design.json'
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    # Execute the original script, rather than importing its functions into a
    # process that may already have loaded the current JLC-R parent modules.
    subprocess.run([sys.executable,'-B',str(harness),'--design',str(design),
                    '--output',str(out),'--workers',str(workers)],cwd=ROOT,env=env,check=True)
    with (out/'metrics.csv').open(encoding='utf-8-sig',newline='') as stream:records=list(csv.DictReader(stream))
    if len(records)!=report['planned_cases']:raise RuntimeError('Incomplete mechanism rerun')
    return {'study':'mechanisms','completed':len(records),'output':str(out),
            'retained_results_unchanged':True,'results_file':'metrics.csv'}
