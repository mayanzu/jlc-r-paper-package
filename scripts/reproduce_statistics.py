"""Recompute agricultural plot inputs directly from the distributed seed rows."""
from pathlib import Path
import runpy,shutil
from paths import ROOT

def agricultural(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    ext=ROOT/'code/experiments/v6_4_agricultural_extension'
    for name in ['supply.csv','freshness.csv','canopy.csv']:shutil.copyfile(ext/'results'/name,out/name)
    for name in ['analyze_cross_regime.py','analyze_supply_scan.py','analyze_freshness.py','analyze_canopy.py']:
        namespace=runpy.run_path(str(ext/name),run_name='saved_result_analysis')
        globals_=namespace['main'].__globals__
        globals_['OUT']=out
        if name!='analyze_cross_regime.py':globals_['SOURCE']=out/globals_['SOURCE'].name
        namespace['main']()
    return out
