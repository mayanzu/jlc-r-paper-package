"""Figure 5: paired factorial effects and event-level mechanistic evidence.

Contract: which frozen relay-protection decisions affect low-supply winter
service, and do observed decisions support that interpretation? Quantitative
2x2 grid: far-source response, lower-tail fairness, AoI tradeoff, mechanism
events. All panels show 12 seed-level contrasts and nominal paired 95% t CIs.
The original confirmation and canopy are not pooled into these panels.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment import HERE, PROJECT


def plot():
    mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],
        'font.size':7.5,'axes.spines.top':False,'axes.spines.right':False,
        'axes.linewidth':.6,'svg.fonttype':'none','pdf.fonttype':42,
        'legend.frameon':False,'xtick.labelsize':7,'ytick.labelsize':7})
    paired=pd.read_csv(HERE/'results/primary_seed_effects.csv')
    effects=['T','R','S','TR','TS','RS','TRS','Bundle']
    labels=['T','R','S','T × R','T × S','R × S','T × R × S','Bundle']
    figure,axes=plt.subplots(2,2,figsize=(7.2,5.8))
    figure.subplots_adjust(left=.13,right=.98,bottom=.10,top=.94,wspace=.52,hspace=.48)
    source=[]
    for ax,metric,title,unit in zip(axes.flat[:3],
            ['far_coverage_pct','source_coverage_p5_pct','aoi_mean_minutes'],
            ['Far-source fresh coverage','Source P5','Mean age of information'],
            ['Effect (percentage points)','Effect (percentage points)','Effect (minutes)']):
        ax.axvline(0,color='#999999',linewidth=.6,zorder=0)
        for index,effect in enumerate(effects):
            group=paired[(paired.metric==metric)&(paired.effect==effect)].sort_values('seed')
            a=group.value.to_numpy()
            mean=a.mean(); half=stats.t.ppf(.975,11)*a.std(ddof=1)/np.sqrt(12)
            color='#b56a32' if effect=='Bundle' else ('#326780' if len(effect)==1 else '#647982')
            offset=np.linspace(-.13,.13,12)
            ax.scatter(a,index+offset,s=5,color=color,alpha=.32,linewidths=0,zorder=1)
            ax.errorbar(mean,index,xerr=half,fmt='o',markersize=3.5,color=color,
                capsize=2,elinewidth=.9,zorder=3)
            for seed,value in zip(group.seed,a):
                source.append(dict(panel=title,metric=metric,effect=effect,seed=int(seed),value=float(value)))
        ax.set_yticks(range(8),labels)
        ax.set_ylim(7.6,-.6)
        ax.set_title(title,loc='left',fontsize=8,pad=10)
        ax.set_xlabel(unit)
        ax.tick_params(axis='y',length=0)
        ax.grid(axis='x',color='#eeeeee',linewidth=.4)
    data=pd.read_csv(HERE/'results/formal_runs.csv')
    winter=data[(data.condition.isin(['WINTER_G20','T3_G20']))&(data.supply==.7)&(data.treatment=='C0')]
    ax=axes.flat[3]
    mech=[('event_reject_transit_protect','Transit rejection'),
          ('event_r_only_reactive_periods','R-only selection'),
          ('event_staleness_changed_selection','S changes choice'),
          ('relay_loss_C','Member crowding'),
          ('event_committed_hop_successes','Committed success')]
    for index,(column,label) in enumerate(mech):
        rates=winter.assign(rate=1000*winter[column]/winter.source_time_denominator)
        values=rates.groupby(['seed','configuration']).rate.mean().unstack()
        a=values.A111-values.A000
        mean=a.mean(); half=stats.t.ppf(.975,11)*a.std(ddof=1)/np.sqrt(12)
        ax.scatter(a,index+np.linspace(-.13,.13,12),s=5,color='#326780',alpha=.32,linewidths=0)
        ax.errorbar(mean,index,xerr=half,fmt='o',markersize=3.5,color='#326780',capsize=2,elinewidth=.9)
        for seed,value in a.items():
            source.append(dict(panel='Mechanism events',metric=column,effect='Bundle',seed=int(seed),value=float(value)))
    ax.axvline(0,color='#999999',linewidth=.6,zorder=0)
    ax.set_yticks(range(len(mech)),[v[1] for v in mech])
    ax.set_ylim(4.6,-.6)
    ax.tick_params(axis='y',length=0)
    ax.set_title('Decision and contention events',loc='left',fontsize=8,pad=10)
    ax.set_xlabel('Bundle change per 1000 sampling demands')
    ax.grid(axis='x',color='#eeeeee',linewidth=.4)
    for label,ax in zip('abcd',axes.flat):
        ax.text(-.17,1.08,label,transform=ax.transAxes,fontsize=9,fontweight='bold',va='top')
    figure.canvas.draw()
    qa=HERE/'audit/figure_qa'
    qa.mkdir(exist_ok=True)
    # Optional external QA library; geometry is also saved for portable review.
    geometry={str(k):[float(v) for v in ax.get_position().bounds] for k,ax in enumerate(axes.flat)}
    import json
    (qa/'axes_geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    widths=[b[2]*figure.get_figwidth()*72 for b in geometry.values()]
    heights=[b[3]*figure.get_figheight()*72 for b in geometry.values()]
    assert max(widths)-min(widths)<=1.5 and max(heights)-min(heights)<=1.5
    skill=Path.home()/'.agents/skills/nature-figure/scripts'
    if (skill/'audit_panel_alignment.py').exists():
        sys.path.insert(0,str(skill))
        from audit_panel_alignment import require_matplotlib_panel_alignment
        require_matplotlib_panel_alignment(figure,json_out=qa/'fig5.alignment.json',
            overlay_svg=qa/'fig5.alignment.svg',tolerance_pt=1.5,gutter_tolerance_pt=1.5,strict=True)
    out=HERE/'report'
    figure.savefig(out/'fig5_relay_ablation.svg')
    figure.savefig(out/'fig5_relay_ablation.pdf')
    figure.savefig(out/'fig5_relay_ablation.png',dpi=600)
    plt.close(figure)
    pd.DataFrame(source).to_csv(HERE/'results/figure5_source_data.csv',index=False)


if __name__=='__main__':
    plot()
