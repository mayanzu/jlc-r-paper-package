# Recent duty-control comparison: fixed comparison contract

Design fixed on 18 October 2026 before the first comparison output.

Purpose: compare the JLC-R planner with recent, source-defined duty-control
rules under the same multihop executor. These are control-law adaptations,
not full implementations or rankings of the published MAC protocols.

## Common conditions

Use twelve seeds `120101 + 101*k`, k=0,...,11, absent from the supplied earlier
results. Each has 100 nodes, 14 days, supply 1.0 and 0.7, the original 4000-bit
observations, 4 J battery, one-hour deadline and fixed role schedule. Run both
the unchanged synthetic weather and the retained SURFRAD winter input. The
latter supplies new topology/channel seeds, not new sites or seasons.

All arms share source demand, keyed channel outcomes, the causal point/scenario
bank, route scoring, per-role listening ceilings, paid synchronization and
guards, finite endpoint transaction capacity, charged receiver admission,
one-hop holds, and newest-first committed-service priority. A fraction d maps
to `sync + d*(reference_listening - sync)`, exactly the scale used by JLC-R.
This transfers an activity fraction to a scheduled listening opportunity;
it does not reconstruct an asynchronous sleep/wake trace or contention MAC.
All absolute propagation/timing assumptions of the main simulator remain.

JLC-R and POINT-JL keep their original prefix planners without retuning. The
fixed-profile arm keeps the original JLC-R-FIXED implementation. Duty-rule
arms have a nonbinding communication permission of 4 J per node per round;
every transaction still passes actual battery, reserve, hold and slot checks.
Thus no JLC-R forecast credit cap suppresses the transferred duty controllers.
The permission is not an energy allocation or predicted physical consumption.

## Source-defined rules and scope

HENO-DC transfers Table I and Eq. (6) of Sarang et al., WCNC 2024,
doi:10.1109/WCNC57260.2024.10571258 (author version arXiv:2401.00717).
Set d=1 when the completed metered one-hour harvest covers the full reference
base-plus-traffic cost or current battery fraction r >= .5. Otherwise use
d=(r-.1)/.9 for .1 <= r < .5 and d=.05 below .1. Current battery already
includes the completed interval's consumption and harvest: neither is added
again. The published discontinuity at .1 is retained. The original 224 J/hour
full-activity cost becomes the common model's full-reference service cost;
solar plus wind becomes the identical solar-only supply given to all arms.
No hybrid supply advantage, special alarm classes or asynchronous signaling
is imported into this controlled comparison.

The planned PADC-DC block transfers PADC-MAC (IEEE Access 2023,
doi:10.1109/ACCESS.2023.3246108). Its complete Table 3 must be verified from
the original before implementation or execution. It will use the same point
forecast as POINT-JL, not claim to reproduce the original NARNET predictor.
Its exact rule will be fixed in a separate source-mapping document before
its first run. This block cannot be represented as completed until then.

## Execution and inference

The HENO block runs JLC-R, POINT-JL, JLC-R-FIXED, HENO-DC (192 runs). The
PADC block, if its source rule is verified, adds only PADC-DC on the same 48
condition/seed/supply inputs. No result selects a seed, setting, threshold,
rule variant, exclusion or paper headline. Keep every executed arm.

Primary outcome: fresh-source coverage. Report paired seed differences for
JLC-R minus each of POINT-JL, JLC-R-FIXED, HENO-DC and PADC-DC, separately in
each weather/supply cell. The full primary family is 16 two-sided tests with
Holm correction and nominal plus Bonferroni simultaneous 95% t intervals.
If PADC is unavailable, mark that block incomplete; do not silently shrink
the planned comparison family. Outage, AoI, energy and service tails are
secondary descriptive outcomes. Twelve independent seeds are the statistical
unit per cell; weather/supplies repeat seeds and are never pooled as n=48.

Verify identical physical and forecast digests within pairs, disjoint demand
outcomes, node/network energy balance, hold and capacity maxima. Preserve the
design, source hashes, exact inputs and run records while validating. The
delivered minimal evidence retains metrics, summaries, contrasts, audit and
source mappings; full trajectories are regenerated with the non-overwriting
runner. No raw-data audit may be asserted for absent artifacts.
