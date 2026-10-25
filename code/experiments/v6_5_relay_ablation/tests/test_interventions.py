import copy
from collections import deque
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from experiment import setup, RelayAblationAdapter, InstrumentedAblation
from diagnostic import Sample
from validation_model import StreamingBank


class InterventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg, cls.sc, cls.bank = setup('WINTER_G20', 140101, 1.0, rounds=12)

    def sim(self, **switches):
        return RelayAblationAdapter(dict(self.cfg), self.sc, StreamingBank(self.sc), **switches)

    def prepare_request(self, sim, energy_margin=True):
        sim.install_plan()
        j = next(int(j) for j in sim.ch if sim.transit_reserve[j] and np.any(sim.parent == j))
        i = next(int(i) for i in np.flatnonzero(sim.parent == j) if i not in sim.ch)
        sim.off[[i, j]] = False
        sim.last_message[j] = -1
        sim.quota[i] = 1.0
        sim.slots_left[i] = 3
        sim.slots_left[j] = 2
        sim.forward_holds[:] = 0
        sim.forward_slot_holds[:] = 0
        nxt = int(sim.reference_next[sim.phase(sim.t)][j])
        fwd = sim.tx_energy(j, nxt) + (sim.control_cost(j, nxt)[0] if nxt < sim.n else 0)
        erx = sim.c['packet_bits'] * (sim.c['elec_j_per_bit'] + sim.c['aggregate_j_per_bit'])
        sim.quota[j] = sim.control_cost(i, j)[1] + erx + fwd + 0.5 * sim.transit_unit_j[j]
        return i, j, Sample(i, 0, 999)

    def test_B1_transit_and_charged_safety(self):
        for transit in (False, True):
            sim = self.sim(transit_margin_on=transit)
            i, j, p = self.prepare_request(sim)
            before = sim.battery.copy()
            ok, _ = sim.request_grant(i, j, p)
            self.assertEqual(ok, not transit)
            self.assertAlmostEqual(before[i] - sim.battery[i], sim.control_cost(i, j)[0])
            self.assertAlmostEqual(before[j] - sim.battery[j], 0 if transit else sim.control_cost(i, j)[1])
            if transit:
                self.assertEqual(p.last_reason, 'transit_protect')
            # Basic single-forward guard remains binding even with T off.
            sim = self.sim(transit_margin_on=transit)
            i, j, p = self.prepare_request(sim)
            sim.slots_left[j] = 1
            ok, _ = sim.request_grant(i, j, p)
            self.assertFalse(ok)
            self.assertEqual(p.last_reason, 'transit_protect' if transit else 'forward_reserve')
            self.assertFalse(sim.holds)
            sim = self.sim(transit_margin_on=transit)
            i, j, p = self.prepare_request(sim)
            sim.quota[j] = sim.control_cost(i, j)[1] / 2
            self.assertFalse(sim.request_grant(i, j, p)[0])
            self.assertEqual(p.last_reason, 'grant_denied')

    def test_B2_two_slot_demand_and_hysteresis(self):
        for gate in (False, True):
            sim = self.sim(two_slot_gate_on=gate)
            sim.install_plan()
            sim.t = 20
            j = int(sim.ch[0])
            sim.queues = [deque() for _ in range(sim.n)]
            sim.listen_scale[:] = 0.5
            sim.runtime_cap_profiles[sim.phase(sim.t)][:] = 3
            sim.runtime_cap_profiles[sim.phase(sim.t)][j] = 1
            genuine = np.zeros(sim.n, bool)
            use = sim._select(genuine, np.ones(sim.n))
            self.assertEqual(bool(use[j]), gate)
            # Queue demand is retained in both settings.
            sim.queues[j].append(Sample(j, sim.t, 777))
            self.assertTrue(sim._select(genuine, np.ones(sim.n))[j])
            # Both share the exit threshold, and then leave the reactive mode.
            sim.listen_scale[:] = 0.69
            self.assertTrue(sim._select(genuine, np.ones(sim.n))[j])
            sim.listen_scale[:] = 0.70
            self.assertFalse(sim._select(genuine, np.ones(sim.n))[j])

    def test_zero_transit_margin_preserves_frozen_response_ordering(self):
        for transit in (False,True):
            sim=InstrumentedAblation(dict(self.cfg),self.sc,StreamingBank(self.sc),transit_margin_on=transit)
            i,j,p=self.prepare_request(sim)
            sim.quota[j]-=.5*sim.transit_unit_j[j]+1e-6
            sim.transit_reserve[j]=0
            before=sim.battery.copy()
            self.assertFalse(sim.request_grant(i,j,p)[0])
            self.assertEqual(p.last_reason,'transit_protect' if transit else 'forward_reserve')
            self.assertAlmostEqual(before[i]-sim.battery[i],sim.control_cost(i,j)[0])
            self.assertAlmostEqual(before[j]-sim.battery[j],0 if transit else sim.control_cost(i,j)[1])
            self.assertEqual(sim.events['t_reject_zero_margin'],int(transit))
            self.assertEqual(sim.events['t_reject_positive_margin'],0)

    def test_B3_exact_staleness_key_and_commitment(self):
        for stale in (False, True):
            sim = self.sim(staleness_tie_on=stale)
            sim.t = 20
            i = 0
            older = Sample(1, 20, 100)
            fallback = Sample(2, 20, 10)
            sim.local_forwarded_birth[i, 1] = 1
            sim.local_forwarded_birth[i, 2] = 5
            sim.queues[i] = deque([fallback, older])
            expected = older if stale else fallback
            self.assertEqual(sim.choose_packet(i).sequence, expected.sequence)
            self.assertEqual(sim.read_only_packet(i).sequence, expected.sequence)
            sim.holds[fallback.sequence] = (i, 0.001)
            self.assertEqual(sim.choose_packet(i).sequence, fallback.sequence)
            self.assertEqual(sim.read_only_packet(i).sequence, fallback.sequence)

    def test_B4_all_combinations_and_observer_neutrality(self):
        for t in (False, True):
            for r in (False, True):
                for s in (False, True):
                    args = dict(transit_margin_on=t, two_slot_gate_on=r, staleness_tie_on=s)
                    plain = self.sim(**args)
                    observed = InstrumentedAblation(dict(self.cfg), self.sc, StreamingBank(self.sc), **args)
                    a, b = plain.run(), observed.run()
                    self.assertEqual(a, b)
                    np.testing.assert_array_equal(plain.battery, observed.battery)
                    np.testing.assert_array_equal(plain.diagnostic_data, observed.diagnostic_data)
                    self.assertEqual(a['max_slot_violation'], 0)
                    self.assertLessEqual(a['max_hold_violation_j'], 1e-8)
                    self.assertLessEqual(a['max_energy_balance_error_j'], 1e-6)
                    self.assertTrue(np.all(observed.battery >= 0))
                    self.assertEqual(observed.configuration, f'A{int(t)}{int(r)}{int(s)}')


if __name__ == '__main__':
    unittest.main()
