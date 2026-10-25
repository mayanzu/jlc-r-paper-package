"""Plot the existing 12-seed paired confirmation. Never imports a simulator."""
from pathlib import Path
import csv,hashlib,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
PACKAGE=Path(__file__).resolve().parents[2]
R=Path(os.environ['JLCR_REPRO_OUTPUT']).resolve()
(R/'figures').mkdir(parents=True,exist_ok=True)
(R/'audit').mkdir(parents=True,exist_ok=True)
P=PACKAGE
source=P/'code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv'
stats=P/'code/experiments/v6_3_relay_repair/D_noninferiority_seeds16.csv'
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
data=rows(source);saved=rows(stats);seeds=sorted({x['seed'] for x in data},key=int)
index={(x['condition'],x['supply'],x['seed'],x['method']):x for x in data}
order=[(c,s) for c in ['SYNTHETIC_G20','WINTER_G20','T2_G20','T3_G20'] for s in ['1.0','0.7']]
names={'SYNTHETIC_G20':'Synthetic','WINTER_G20':'T1 winter','T2_G20':'T2 spring','T3_G20':'T3 winter'}
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.65})
fig,axes=plt.subplots(2,2,figsize=(7.2,6.35))
fig.subplots_adjust(left=.15,right=.985,top=.94,bottom=.09,wspace=.60,hspace=.43)
contract=[]
metrics=[('coverage_pct','a  Fresh-source coverage','Difference (percentage points)',False),('aoi_mean_minutes','b  Mean information age','Difference (minutes)',True),('source_coverage_p5_pct','c  Lower-tail source coverage','Difference (percentage points)',False),('night_off_pct','d  Nighttime outage','Difference (percentage points)',True)]
for ax,(metric,title,xlabel,lower) in zip(axes.flat,metrics):
    ax.set_title(title,loc='left',fontsize=8.2,fontweight='bold',pad=10)
    ax.axvline(0,color='#7b858b',lw=.75,ls='--',zorder=1)
    ax.set_yticks(range(8));ax.set_yticklabels([names[c]+' '+s for c,s in order],fontsize=7)
    ax.set_ylim(7.55,-.55);ax.set_xlabel(xlabel,fontsize=7.5,labelpad=5)
    ax.tick_params(axis='x',labelsize=7);ax.tick_params(axis='y',length=0,pad=4)
    ax.grid(axis='y',color='#e9ecee',lw=.6,zorder=0)
    for y,(c,s) in enumerate(order):
        baseline='JLC-R-SA' if c in ['SYNTHETIC_G20','T2_G20'] else 'PADC-AGE'
        d=np.array([float(index[c,s,k,'JLC-R-HYB-V63'][metric])-float(index[c,s,k,baseline][metric]) for k in seeds])
        x=next(x for x in saved if (x['condition'],x['supply'],x['metric'])==(c,s,metric))
        mean,lo,hi=[float(x[k]) for k in ['mean_diff','ci95_lo','ci95_hi']]
        assert abs(d.mean()-mean)<1e-9
        ax.scatter(d,np.full(12,y)+np.linspace(-.18,.18,12),s=6,color='#9ba5ac',alpha=.65,linewidth=0,zorder=2)
        color='#176b78' if (mean<0 if lower else mean>0) else '#a0552e'
        ax.errorbar([mean],[y],xerr=[[mean-lo],[hi-mean]],fmt='D',markersize=3.8,color=color,elinewidth=1.6,markeredgecolor='white',markeredgewidth=.45,zorder=4)
        contract.append(dict(metric=metric,condition=c,supply=s,baseline=baseline,seed_count=12,mean=mean,ci95=[lo,hi]))
    ax.margins(x=.14)
fig.canvas.draw()
skill=Path.home()/'.agents/skills/nature-figure/scripts'
if skill.exists():
    sys.path.insert(0,str(skill))
    from audit_panel_alignment import require_matplotlib_panel_alignment
    require_matplotlib_panel_alignment(fig,json_out=R/'audit/confirmation_figure_alignment.json',strict=True)
else:
    boxes=[ax.get_position().bounds for ax in axes.flat]
    assert max(b[2] for b in boxes)-min(b[2] for b in boxes)<1e-8
    assert max(b[3] for b in boxes)-min(b[3] for b in boxes)<1e-8
    (R/'audit/confirmation_figure_alignment.json').write_text(json.dumps(dict(equal_plot_rectangles=True,axes_normalized=boxes),indent=2)+'\n',encoding='utf-8')
fig.savefig(R/'figures/fig3_confirmation.pdf')
fig.savefig(R/'figures/fig3_confirmation.svg')
fig.savefig(R/'figures/fig3_confirmation.png',dpi=600)
plt.close(fig)
(R/'audit/confirmation_figure_data.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),statistics_sha256=hashlib.sha256(stats.read_bytes()).hexdigest(),record_count=480,paired_points=384,contrasts=contract,excluded_seed_conditions=0,interpretation='Nominal two-sided 95% intervals depict effects. The original one-sided Holm-36 NI test determines the reported verdict; zero is not its margin.'),indent=2)+'\n',encoding='utf-8')
print('Existing confirmation plotted: 32 contrasts, 384 paired metric observations; no simulation.')
