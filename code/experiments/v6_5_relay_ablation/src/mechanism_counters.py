"""Read-only observers; selection counters exclude diagnostic read-only peeks.

Hop-loss categories reuse the frozen development observer. Those are events,
not unique lost packets. Far expiry-at-relay is also counted separately.
"""
from collections import Counter
import numpy as np
from relay_ablation_adapter import RelayAblationAdapter
from v63_observer import HopFateMixin


class InstrumentedAblation(HopFateMixin, RelayAblationAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = Counter()
        self.plan_records = []
        self.source_aoi_sum = np.zeros(self.n)
        self.source_delivered = np.zeros(self.n, dtype=int)
        self.source_expired = np.zeros(self.n, dtype=int)
        self.source_expired_relay = np.zeros(self.n, dtype=int)
        self.resource_records = []
        self._pending_plan = None

    def _select(self, genuine, duty):
        ph = self.phase(self.t)
        cap = self.runtime_cap_profiles[ph].copy()
        cutoff = self.t - self.c['deadline_rounds'] + 1
        uncov = np.array([self._uncovered_fresh(i, cutoff) for i in range(self.n)])
        heads = np.zeros(self.n, dtype=bool)
        heads[self.ch] = True
        low = heads & (cap < 2)
        allowed = genuine | (self.listen_scale < self.c['hyb_thin_scale']) | (
            self.hyb_latched & (self.listen_scale < self.c['hyb_exit_scale']))
        self.events['ch_plan_periods'] += int(heads.sum())
        self.events['ch_low_guard_periods'] += int(low.sum())
        self.events['ch_low_guard_only_demand'] += int((low & ~uncov).sum())
        self.events['ch_low_guard_only_allowed'] += int((low & ~uncov & allowed).sum())
        use = super()._select(genuine, duty)
        self.events['reactive_node_periods'] += int(use.sum())
        self.events['ch_reactive_periods'] += int(use[heads].sum())
        self.events['r_only_reactive_periods'] += int((use & low & ~uncov).sum())
        self.events['prefix_infeasible_node_periods'] += int((~self.diagnostic_prefix_good).sum())
        self._pending_plan = (cap, uncov, low, allowed, use.copy())
        return use

    def install_plan(self):
        super().install_plan()
        if self._pending_plan is not None:
            cap, uncov, low, allowed, use = self._pending_plan
            after = self.runtime_cap_profiles[self.phase(self.t)]
            for i in self.ch:
                self.plan_records.append(dict(round=int(self.t), node=int(i),
                    prefix_guards=int(cap[i]), installed_guards=int(after[i]),
                    queue_demand=int(uncov[i]), low_guard=int(low[i]),
                    hysteresis_eligible=int(allowed[i]), reactive=int(use[i]),
                    prefix_infeasible=int(not self.diagnostic_prefix_good[i])))

    def request_grant(self, i, j, packet):
        member = i not in self.ch and j in self.ch
        self.events['requests_all'] += 1
        self.events['member_ch_requests'] += int(member)
        si, rj = self.control_cost(i, j)
        before_sender = float(self.quota[i])
        before_receiver = float(self.quota[j])
        erx = self.c['packet_bits'] * (self.c['elec_j_per_bit'] + self.c['aggregate_j_per_bit'])
        cached_block = self.last_message[j] == self.t and (self.cached_off[j] or self.cached_quota[j] < erx)
        sender_ok = not cached_block and self.available(i, packet) >= self.tx_energy(i, j) + si
        receiver_ok = not self.off[j] and self.available(j) >= rj and self.slots_left[j] - self.forward_slot_holds[j] > 0
        if member and sender_ok and receiver_ok:
            self.events['t_check_opportunities'] += 1
            self.events['t_checks_executed'] += int(self.transit_margin_on)
            self.events['t_positive_margin_checks'] += int(self.transit_margin_on and self.transit_reserve[j] > 0)
            self.events['t_zero_margin_checks'] += int(self.transit_margin_on and self.transit_reserve[j] == 0)
        ok, fwd = super().request_grant(i, j, packet)
        paid = before_sender != self.quota[i]
        responded = before_receiver != self.quota[j]
        self.events['paid_requests_all'] += int(paid)
        self.events['paid_member_ch_requests'] += int(paid and member)
        self.events['receiver_responses_all'] += int(responded)
        self.events['receiver_responses_member_ch'] += int(responded and member)
        if not ok:
            self.events['pre_response_rejections'] += int(paid and not responded)
            self.events['post_response_rejections'] += int(responded)
            self.events['reject_' + packet.last_reason] += 1
            if packet.last_reason == 'transit_protect':
                self.events['t_reject_positive_margin' if self.transit_reserve[j] > 0 else 't_reject_zero_margin'] += 1
            if member:
                self.events['member_reject_' + packet.last_reason] += 1
        else:
            self.events['admitted_all'] += 1
            self.events['admitted_member_ch'] += int(member)
        return ok, fwd

    def choose_packet(self, i):
        queue = list(self.queues[i])
        self.events['queue_selections'] += 1
        self.events['queue_multi_candidates'] += int(len(queue) >= 2)
        committed = [p for p in queue if self.holds.get(p.sequence, (-1, 0))[0] == i]
        candidates = committed or queue
        self.events['committed_unresolved_ties'] += int(len(candidates) >= 2)
        cutoff = self.t - self.c['deadline_rounds'] + 1
        def full(p):
            # Bypass the switch solely for counterfactual read-only comparison.
            previous = self.local_forwarded_birth[i, p.source]
            return (previous < cutoff and p.birth >= cutoff,
                    p.birth - max(previous, cutoff - 1), -previous, p.birth, -p.sequence)
        def old(p):
            key = full(p)
            return key[:2] + key[3:]
        best_prefix = max(full(p)[:2] for p in candidates)
        tied = [p for p in candidates if full(p)[:2] == best_prefix]
        effective = len(tied) >= 2
        different_history = len({full(p)[2] for p in tied}) >= 2
        changed = max(candidates, key=full).sequence != max(candidates, key=old).sequence
        self.events['freshness_unresolved_ties'] += int(effective)
        self.events['staleness_comparison_opportunities'] += int(effective)
        self.events['staleness_discriminating_ties'] += int(different_history)
        self.events['staleness_active_comparisons'] += int(effective and self.staleness_tie_on)
        self.events['staleness_would_change_selection'] += int(changed)
        self.events['staleness_changed_selection'] += int(changed and self.staleness_tie_on)
        return super().choose_packet(i)

    def attempt(self, i, j, packet):
        committed = self.holds.get(packet.sequence, (-1, 0))[0] == i
        self.events['committed_attempts'] += int(committed)
        ok, why = super().attempt(i, j, packet)
        self.events['committed_hop_successes'] += int(committed and ok)
        if ok and j < self.n:
            self.events['successful_receptions'] += 1
            self.events['successful_member_receptions'] += int(i not in self.ch)
            self.events['holds_created'] += int(packet.sequence in self.holds)
            self.events['receive_forward_transactions_completed'] += int(committed)
        return ok, why

    def finalize(self, packet, status):
        if status == 'delivered':
            self.source_delivered[packet.source] += 1
        elif status == 'expired':
            self.source_expired[packet.source] += 1
            self.source_expired_relay[packet.source] += int(self._holder_of.get(packet.sequence, packet.source) != packet.source)
        return super().finalize(packet, status)

    def round(self):
        super().round()
        ages = np.where(self.latest >= 0, self.t - self.latest, self.t)
        self.source_aoi_sum += ages * self.c['round_seconds'] / 60
        self.events['unused_forward_guards'] += len(self.hold_slots)
        self.events['unused_forward_energy_nj'] += float(self.forward_holds.sum()) * 1e9
        self.resource_records.append(dict(round=int(self.t - 1),
            battery_min_j=float(self.battery.min()), battery_max_j=float(self.battery.max()),
            held_guards=int(self.forward_slot_holds.sum()), held_energy_j=float(self.forward_holds.sum()),
            max_hold_violation_j=float(self.max_hold_violation),
            max_slot_violation=int(self.max_slot_violation),
            energy_balance_error_j=float(self.logs[-1]['energy_balance_error_j'])))
