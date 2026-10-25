# Relay-factorial data dictionary and interpretation boundaries

`configuration` / `ablation_configuration` (`A000`–`A111`) and the three explicit
Boolean fields are the authoritative intervention identity. The inherited
`method` field is the frozen physical/planning kernel's internal policy name;
it must not be used to collapse the eight configurations. A111 is the frozen
JLC-R endpoint and A000 is the frozen Hybrid endpoint, as established by the
exact endpoint audit. Intermediate combinations are isolated interventions,
not additional public algorithm releases.

## Service and geography

- `coverage_pct`, `source_coverage_p5_pct`, `night_off_pct`: percentages in the
  frozen definitions; their paired differences are percentage points.
- `aoi_mean_minutes`, `far_aoi_mean_minutes`: source-time mean age in minutes,
  including the original never-updated-source convention.
- `far_sources`: sources at Euclidean distance ≥200 m from the frozen sink.
  `far_source_time_denominator = far_sources × 1344`. `far_coverage_pct` uses
  only this source set. Source P5 always uses all 100 sources.
- `far_delivered_samples`, `far_expired_samples`: unique samples reaching those
  terminal fates within the scored horizon. `far_expired_at_relay_samples`
  counts distinct expiries at a holder other than the sample's source.
- `far_relay_loss_events` and `relay_loss_*`: the retained diagnostic observer's
  far-source relay loss **events**, including repeated blocks and priority
  expiries. They are neither unique terminal losses nor independent replicates;
  successful later delivery is possible after a blocked event. The original
  S/L/C/Q/P/O category definitions remain unchanged.
- `source_coverage_sd_pct`: population SD over the 100 source coverage values.
  A smaller SD alone does not establish better service; coverage and P5 must
  also be considered.

## Requests, charges and transit protection

- `event_member_ch_requests` and `event_requests_all` count calls to the
  admission-request path. Some calls stop at known-unavailable or sender-credit
  checks before a request is paid/transmitted. They are candidate request
  opportunities, not a count of paid over-air messages.
- `event_paid_member_ch_requests` / `event_paid_requests_all` count sender
  request charges actually incurred. `event_receiver_responses_*` count
  receiver response charges. Pre-response and post-response refusals therefore
  remain distinct.
- `event_t_checks_executed` counts entry into the enabled member-to-CH check.
  `event_t_positive_margin_checks` and `event_t_zero_margin_checks` split the
  frozen binary `protect` state. `event_t_reject_positive_margin` and
  `event_t_reject_zero_margin` split its refusals in the same way.
- A zero-margin refusal can avoid the receiver response even when ordinary
  reception/forwarding was unaffordable. With a positive margin, the Guard
  threshold remains two pre-response guards, matching ordinary RX+forward
  safety. T does not add a third paid/held guard. Its intervention includes the
  positive energy/credit margin and refusal ordering; the T contrast cannot
  independently identify a benefit from an extra physical Guard reservation.
- `*_per_1000_member_requests` in the main analysis CSV uses candidate
  member-to-CH calls as denominator, not paid requests. Both denominators are
  provided explicitly in raw counts. Paid-request refusal rates can be
  reconstructed as `1000 × refusals / event_paid_member_ch_requests`; undefined
  ratios must remain missing rather than being converted to zero.

## Demand recognition and queue selection

- CH plan records contain pre-reactive prefix capacity, installed capacity,
  queue demand, low-Guard status, hysteresis eligibility, reactive choice and
  prefix infeasibility for every credit-period CH.
- `event_ch_low_guard_only_demand` is an opportunity count, even when R=0.
  `event_r_only_reactive_periods` counts actual reactive choices whose demand
  arose solely from the R term. Selection does not itself demonstrate service.
- Queue-choice counts exclude diagnostic `read_only_packet` queries. The
  committed-first candidate subset is applied before uncovered/gain ties are
  counted. `event_staleness_comparison_opportunities` counts top-prefix ties;
  `event_staleness_discriminating_ties` requires distinct local histories.
  `event_staleness_changed_selection` counts actual changes from the exact
  historical fallback in the currently observed queue state when S is enabled.
  It is a local counterfactual, not an assertion that an entire S=0 trajectory
  would have the same queue state.

## Forwarding and denominators

- `event_holds_created` counts successful admissions that create actual holds.
  `event_committed_hop_successes` counts successful subsequent hops by committed
  samples, including delivery to the sink. These remain single-hop successes.
- `event_receive_forward_transactions_completed` is the intersensor subset of
  committed successful forwarding, because the receiving endpoint creates
  another hop obligation; use `event_committed_hop_successes` for all completed
  committed hops including the sink.
- `event_unused_forward_guards` and the corresponding held-energy sum describe
  actual unexecuted commitments at round boundaries. A T admission margin is
  not an additional physical hold. Held energy is not automatically consumed.
- Counts per 1000 source demands use `100 × 1344`; refusal rates use their
  explicitly named request-call denominators; committed completion uses created
  commitments; S choice-change rate uses eligible top-prefix ties. Zero
  denominators are missing. These quantities have different units and are not
  interchangeable.

## Analysis units

The independent n is 12 network seeds. The two primary winter conditions are
averaged within seed before inference. Node, packet, hop, request and period
counts describe exposure and execution; they do not increase n. Interactions
use the specified factorial differences, not treatment-coded regression
coefficients. Conditional losses and marginal main effects remain distinct.

## Frozen canopy mapping

The existing WP4 field named `canopy_intensity` is used as an uncalibrated
spatial index. The executed transmittance is
`T_min + (T_max - T_min) * index`, while decoding decreases with the same
index. This exactly matches all 3600 retained node-stage records. An earlier
manuscript expression and the legacy module docstring described the opposite
energy direction; the new manuscript corrects that description, without
editing either frozen code or earlier data. The shared field therefore does
not establish a physiological model of co-located monotone shading and link
attenuation. The supplemental III-C3 panel inherits the actual frozen mapping.
