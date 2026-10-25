"""Run the published plotting calculations into a new output directory; no simulation."""
from pathlib import Path
import json,os,runpy,shutil,sys
from paths import ROOT

def reproduce(out,agricultural_results=None,ablation_results=None):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'))
    os.environ['JLCR_REPRO_OUTPUT']=str(out)
    if agricultural_results:os.environ['JLCR_AGRICULTURAL_RESULTS']=str(agricultural_results)
    for name in ['plot_confirmation.py','plot_cross_regime.py','plot_supply_scan.py','plot_freshness.py','plot_canopy.py']:
        runpy.run_path(str(ROOT/'tools/paper_figures'/name),run_name='__main__')
    ab=ROOT/'code/experiments/v6_5_relay_ablation'
    work=out/'relay_plot_work'
    for name in ['results','audit','report']:(work/name).mkdir(parents=True,exist_ok=True)
    for name in ['primary_seed_effects.csv','formal_runs.csv']:
        shutil.copyfile(Path(ablation_results or ab/'results')/name,work/'results'/name)
    module=runpy.run_path(str(ab/'scripts/plot_ablation.py'),run_name='reproduction_plot')
    module['plot'].__globals__['HERE']=work
    module['plot']()
    for suffix in ['.pdf','.svg','.png']:shutil.copyfile(work/'report'/('fig5_relay_ablation'+suffix),out/'figures'/('fig5_relay_ablation'+suffix))
    mapping=json.loads((ROOT/'configs/article_figure_map.json').read_text(encoding='utf-8'))
    (out/'figures/figure_map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    return {'figures_directory':str(out/'figures'),'main_statistical_figures':'2-5','repository_figures':['R1','R2'],'figure_map':mapping,'new_simulations':0}

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(reproduce(a.output),indent=2))
