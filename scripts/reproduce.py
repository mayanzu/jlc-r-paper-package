"""Three modes: verify/reproduce never run simulations; rerun is explicit."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import argparse,json,sys
from paths import ROOT,output_root

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['verify','reproduce','rerun'],required=True)
    p.add_argument('--study',choices=['confirmation','mechanisms','relay_ablation','agricultural_extension','supply','freshness','canopy','reliability'])
    p.add_argument('--output',type=Path)
    p.add_argument('--workers',type=int,default=1)
    p.add_argument('--dry-run',action='store_true',help='Check rerun matrix and frozen source hashes without simulation')
    a=p.parse_args()
    if a.workers<1:p.error('--workers must be positive')
    if a.mode=='rerun':
        if not a.study:p.error('--study is required for rerun')
        from rerun import execute
        out=a.output or output_root()/('rerun_'+a.study+'_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S'))
        print(json.dumps(execute(a.study,out,a.workers,a.dry_run),indent=2));return
    if a.study or a.dry_run:p.error('--study and --dry-run apply only to rerun')
    from verify import verify
    report=verify()
    if a.mode=='reproduce':
        out=a.output or output_root()/('reproduce_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S'))
        out=out.resolve()
        if out.exists():p.error('--output must be a new directory')
        if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/'outputs'):p.error('Generated outputs cannot overwrite package inputs')
        out.mkdir(parents=True)
        from reproduce_tables import reproduce as tables
        from reproduce_figures import reproduce as figures
        from reproduce_statistics import agricultural
        report['tables']=tables(out/'tables')
        agricultural_results=agricultural(out/'agricultural_statistics')
        # Independently recomputed primary Holm-36 table.
        sys.path.insert(0,str(ROOT/'docs/paper_audit'))
        from check_scientific_consistency import confirmation,read_csv
        from reproduce_tables import write
        _,tests,_=confirmation(read_csv(ROOT/'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv'))
        write(out/'statistics/primary_holm36.csv',tests)
        # Original factorial analysis, writing only to the new output tree.
        import runpy,shutil
        ab=ROOT/'code/experiments/v6_5_relay_ablation';work=out/'relay_statistics'
        (work/'results').mkdir(parents=True);(work/'report').mkdir();(work/'audit').mkdir()
        shutil.copyfile(ab/'audit/formal_audit.json',work/'audit/formal_audit.json')
        shutil.copyfile(ab/'results/formal_runs.csv',work/'results/formal_runs.csv')
        module=runpy.run_path(str(ab/'scripts/analyze_effects.py'),run_name='reproduction_analysis')
        module['main'].__globals__['HERE']=work;module['main']()
        report['figures']=figures(out,agricultural_results,work/'results')
        from reproduce_reliability import reproduce as reliability
        report['reliability']=reliability(out/'reliability')
        report['plot_inputs']='Recomputed from supplied seed-level rows before plotting; distributed derived summaries are not used as a substitute.'
        report['output']=str(out)
        (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
