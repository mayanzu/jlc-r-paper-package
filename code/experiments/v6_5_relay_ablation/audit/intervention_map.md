# Gate A: decision-node intervention map

The public controller remains `code/simulation/jlc_r.py:JLCR`. No frozen source
is edited. Line numbers refer to the frozen version recorded in
`frozen_assets_before.json`; source expressions, rather than line numbers alone,
identify each intervention.

| Factor | Frozen decision node | Enabled | Disabled | Permitted downstream state changes | Protected mechanisms | Tests |
|---|---|---|---|---|---|---|
| T | `RelayRepairHYB.request_grant`, member-to-CH condition: `slots_left[j]-forward_slot_holds[j]-1 < protect` OR `available(j)-rj-(erx+forward) < protect*transit_unit_j[j]` | Delegate to frozen JLC-R request path | Delegate to actual `HYBSimulator.request_grant` inherited from `ServiceSimulator` | Admission, denial reason, subsequent response costs and service consequences | Sender's already incurred request, receiver availability/response, post-response RX+forward cost and one guard, existing holds, no free capacity | B1; endpoint E1/E2; eight-combination invariants |
| R | `RelayRepairHYB._select`, `demand = uncov | (ch_mask & (runtime_cap_profiles[ph] < 2))` | Delegate to frozen JLC-R selector | Delegate to actual `HYBSimulator._select`, demand only `uncov` | Reactive selection/latch, installed plan and consequent service | Prefix feasibility, PADC rule, explicit configured 0.60/0.70 thresholds, reception and forward safety | B2; E1/E2 |
| S | `RelayRepairMixin._priority_tuple`: `(uncovered,gain,-previous,p.birth,-p.sequence)` | Full frozen key | Remove only `-previous`: `(uncovered,gain,p.birth,-p.sequence)` | Queue order and subsequent service | Both read-only and executing selectors retain committed-first candidate subset; no random tie-break | B3; E1/E2 |

The historical Hybrid control really omits all three decisions. Its priority
key is the exact four-element fallback above. Its configured thresholds are
0.60/0.70 (the defaults in the parent source differ, so the condition config
must always be supplied). E2 compares the actual class under that config.

The frozen staleness key is inserted **before birth** and sequence; the birth
key remains part of the fallback. The interventions follow this actual key,
including cases where a prose interpretation of “fourth level” might differ.

All configurations retain the frozen transit-array computation at plan install.
These derived arrays do not affect decisions when T=0 and create no physical
hold or expenditure. All-off metrics retain an explicit ablation identity;
only identity/extra V63 metadata are removed when comparing common metrics.

The frozen T energy expression is evaluated even when `protect == 0`. In that
case it can reject an otherwise ordinarily unaffordable reception before the
receiver response. The factorial T intervention therefore includes this
response-charge ordering effect, as well as a positive upstream margin. Logs
separate positive-margin and zero-margin checks/rejections. Neither category
is silently redefined or removed from the original frozen condition.

There is a further algebraic boundary: because `protect` is at most one,
`free_guards - 1 >= protect` requires two free guards when protection is
positive. The ordinary receive-plus-forward check also requires two guards
before the receiver response consumes one. Thus this T guard test does not
purchase or physically hold a third guard for a separate future transit. Its
distinctive effects are the additional positive energy/credit margin and the
pre-response timing of refusals, including ordinary-infeasible requests. The
T factorial contrast identifies the complete frozen gate, not an independently
isolated benefit of an extra guard reservation. This is an interpretation
boundary, not a correction or expansion of the frozen algorithm.

Observer counters are external to decision state. Diagnostic `read_only_packet`
peeks are excluded from queue-selection event denominators. Hop-fate events
reuse the original diagnostic taxonomy, so repeated blocked attempts are events,
not independent packets or statistical replications. Distinct far-source expiry
and expiry-at-relay sample counts are recorded separately. “Unused reserve”
counts actual committed forwarding holds at the round boundary, not a fictitious
T margin reservation: T creates an admission margin, not a physical extra hold.
