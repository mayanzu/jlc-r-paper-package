"""Isolated three-node intervention on the byte-frozen JLC-R controller.

No physical method is copied or patched. All-off delegates each changed node
to the actual HYBSimulator implementation, rather than a reconstructed control.
"""
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[2]
SIM = PROJECT / 'code/simulation'
sys.path.insert(0, str(SIM)) if str(SIM) not in sys.path else None
from v63_model import RelayRepairHYB
from v6_model import HYBSimulator


class RelayAblationAdapter(RelayRepairHYB):
    def __init__(self, c, sc, bank, transit_margin_on=True,
                 two_slot_gate_on=True, staleness_tie_on=True):
        self.transit_margin_on = bool(transit_margin_on)
        self.two_slot_gate_on = bool(two_slot_gate_on)
        self.staleness_tie_on = bool(staleness_tie_on)
        super().__init__(c, sc, bank, v63_mechanism='relay_repair')

    @property
    def configuration(self):
        return 'A' + ''.join(str(int(v)) for v in
                             (self.transit_margin_on, self.two_slot_gate_on,
                              self.staleness_tie_on))

    def _select(self, genuine, duty):
        if self.two_slot_gate_on:
            return RelayRepairHYB._select(self, genuine, duty)
        return HYBSimulator._select(self, genuine, duty)

    def _priority_tuple(self, i, p, cutoff):
        full = super()._priority_tuple(i, p, cutoff)
        # Actual frozen full key: uncovered, gain, -previous, birth, -sequence.
        return full if self.staleness_tie_on else full[:2] + full[3:]

    def request_grant(self, i, j, packet):
        if self.transit_margin_on:
            return RelayRepairHYB.request_grant(self, i, j, packet)
        return HYBSimulator.request_grant(self, i, j, packet)

    def metrics(self):
        row = super().metrics()
        row.update(ablation_configuration=self.configuration,
                   transit_margin_on=int(self.transit_margin_on),
                   two_slot_gate_on=int(self.two_slot_gate_on),
                   staleness_tie_on=int(self.staleness_tie_on))
        return row
