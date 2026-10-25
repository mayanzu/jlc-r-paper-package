"""Fixed V3 Floor, joint synchronization and multi-climate paired extensions."""
import argparse
import json
from pathlib import Path
import numpy as np
from expansion_driver import run_study
from helpers import ROOT, RESULTS
from validation_model import ScenarioV2
from strengthening_model import (ExtensionJoint, ExtensionOptimized,
                                 ExtensionPADC, ExtensionPADCAge)


def build_scenario(c, seed, days, supply, condition):
    sc = ScenarioV2(c, seed, days, supply)
    if condition.get('weather_file'):
        path = ROOT.parent.parent/condition['weather_file']
        ghi = np.loadtxt(path, delimiter=',', skiprows=1)[:, 1]
        if len(ghi) != sc.warm+sc.rounds+sc.tail:
            raise ValueError('Measured weather length mismatch')
        sc.harvest = ghi[:, None]/1000*sc.solar_scale[None, :]
        sc.observed = sc.harvest.copy()
    return sc


def build_simulator(c, sc, bank, condition, policy):
    c = dict(c)
    c['no_reference_floor'] = policy.endswith('-NF')
    base = policy.removesuffix('-NF')
    if base == 'JLC-R-SA':
        sim = ExtensionOptimized(c, sc, bank)
    elif base == 'PADC-AGE':
        sim = ExtensionPADCAge(c, sc, bank)
    elif base == 'PADC-DC':
        sim = ExtensionPADC(c, sc, bank, base)
    else:
        sim = ExtensionJoint(c, sc, bank, base)
    # Keep extension labels distinct in per-run files.
    if base == 'JLC-R-SA':
        sim.optimized_label = policy
    elif base == 'JLC-R':
        sim.joint_label = policy
    return sim


def collect(sim, condition):
    return sim.resource_rows()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--design', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    run_study(args.design, args.output, build_scenario, build_simulator, collect,
              workers=args.workers, resume=args.resume, extra_name='resources.csv')


if __name__ == '__main__':
    main()
