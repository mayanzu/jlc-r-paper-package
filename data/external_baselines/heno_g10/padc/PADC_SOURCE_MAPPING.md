# PADC-DC source mapping

Rule verified and implementation fixed on 18 October 2026 before the first
PADC-DC comparison run. The common conditions and 16-test primary family
are fixed in RECENT_BASELINES_SPEC.md; RECENT_PADC.json executes only the
additional PADC-DC arm on the same 48 inputs as the HENO block.

Source: Sarang et al., IEEE Access 11 (2023), 17536--17554,
doi:10.1109/ACCESS.2023.3246108. Read printed page 17541 (PDF page 6),
Table 3 and Eqs. (2), (3), (5), (6). The author supplied the original PDF;
its SHA256 is 24259b9c2e153785ca1f5b163fa93a2561402bedd19f674144c2801453d21be7. The downloaded reference is a local reading
input, not part of the reproduction software or a redistributed article.

Use the same causal point forecast as POINT-JL. Sum its next four rounds to
obtain predicted one-hour energy P. Define expected stored fraction
r=(B+P)/Bmax. Set d=1 for r>=.5, or when r>=.3 AND P>=Ec. Otherwise set
d=r/.9 for .1<=r<.5 and d=.05 below .1. This interprets Eq. (5) in its
published percentage units: (100r-10+10)/(100-10). Table 3 explicitly gives
the .11--.55 middle range, resolving the dimensional ambiguity that would
arise from adding a literal 10 J. Ec is four times the common full-reference
base-plus-traffic cost. Predicted energy informs this decision only: it is
never added to the physical battery or used for pre-harvest affordability.

The common scheduled-listening mapping and nonbinding communication permission
are unchanged from the HENO block. Original NARNET training, alarm priority,
receiver-initiated contention, beacon timing and self-adaptive asynchronous
sleep are not reproduced. Thus the label is PADC-DC, a transferred duty rule,
not PADC-MAC. Thresholds are the source values, without fitting to any outcome.
