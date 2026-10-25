"""Fixed seed-level inference helpers for the independent validation."""
import numpy as np
from scipy.stats import t


def estimate(values, family=1):
    a = np.asarray(values, float)
    if len(a) < 2:
        raise ValueError('At least two independent seeds required')
    n = len(a)
    mean = float(a.mean())
    sd = float(a.std(ddof=1))
    se = sd / np.sqrt(n)
    half = float(t.ppf(.975, n-1) * se)
    adjusted = float(t.ppf(1-.05/(2*family), n-1) * se)
    loo = (a.sum()-a)/(n-1)
    return dict(n=n, mean=mean, sd=sd, ci95_low=mean-half, ci95_high=mean+half,
                simultaneous_low=mean-adjusted, simultaneous_high=mean+adjusted,
                p_raw=float(2*t.sf(abs(mean/se), n-1)) if se else (1. if mean == 0 else 0.),
                positive_seeds=int((a > 0).sum()), negative_seeds=int((a < 0).sum()),
                leave_one_out_min=float(loo.min()), leave_one_out_max=float(loo.max()))


def holm(rows):
    ordered = sorted(rows, key=lambda r: r['p_raw'])
    running = 0.
    for rank, row in enumerate(ordered):
        running = max(running, min(1., (len(rows)-rank)*row['p_raw']))
        row['p_holm'] = running
        row['family_size'] = len(rows)


def interaction(joint, lock, priority, admit):
    return np.asarray(joint)-np.asarray(lock)-np.asarray(priority)+np.asarray(admit)
