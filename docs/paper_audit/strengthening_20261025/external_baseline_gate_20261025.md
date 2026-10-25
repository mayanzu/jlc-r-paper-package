# Gate 1: external-baseline decision (25 October 2026)

Scope: exactly two candidates were audited from original full texts. No new external performance matrix was run. Decisions concern faithful comparison inside the frozen S200/G20 executor, not general portability.

| Candidate | Primary-source location and mechanism | Frozen-interface conflict | Gate |
|---|---|---|---|
| HENO-MAC, DOI 10.1109/WCNC57260.2024.10571258 | Author PDF https://arxiv.org/pdf/2401.00717, sections III-A/B, Figure 3, Tables I/II: receiver wake-up, priority Tx beacons, priority-dependent wait, p-persistent contention, receiver selection and ACK; duty follows ENO/current battery. | The frozen sequential caller selects the sender before a request and provides no competing Tx-beacon set, wait timer, priority traffic or ACK state. A duty-only transfer drops those decisions; inventing multihop contention would require a different execution model. Solar-only input by itself is not a disqualifier. | FAIL for full-protocol comparison; CONDITIONAL only as explicitly named duty adapter. Existing G10 HENO-DC remains historical, not S200/G20 SOTA evidence. |
| MAoIG, DOI 10.1109/JIOT.2022.3197428 | Accepted PDF https://pure.coventry.ac.uk/ws/portalfiles/portal/56402495/Binder13.pdf, section III-A, Definition 9, section V-A, Algorithm 2: estimated harvesting rates, workload feedback, energy-adaptive cycle tree, generation timing and interference-constrained schedule. | Fixing the role/candidate tree removes Algorithm 2 path selection; imposing a sample every round removes its generation-time decision; a Guard budget does not provide the conflict schedule. A rank-only or queue-priority adapter would therefore be a different algorithm. | FAIL for faithful same-executor comparison. Causal prediction is permitted by the original premise; no future-weather oracle requirement is asserted. |

The original papers and linked arXiv/institutional/Zenodo records were checked for executable source links. No verified original execution artifact was obtained through those routes; this is a bounded search finding, not proof that no code exists. The primary PDFs were available and read, so the decisions do not rely on missing-paper access. Source SHA-256 values are in gate1_20261025.json; copyrighted source PDFs stay in the local process archive, outside the public package.

## Decision witnesses

1. HENO requires observing at least two competing requests before choosing a sender; the frozen request_grant(i,j,p) is called only after one sender/packet and candidate have been selected. Removing the competition/receiver choice does not implement full HENO.
2. MAoIG Algorithm 2 forms a cycle-specific tree using candidate workload/energy feedback, then calls its line-network scheduler. Retaining JLC-R's fixed role schedule and choosing one of its cached next hops supplies neither that tree protocol nor its update-generation schedule.
3. Neither failure is based on granting JLC-R a better queue or denying external methods causal forecasts. No altered external controller is presented as the original method.

## Stop rule and manuscript implication

Stop after these two audits. Do not create a third candidate or force a straw-man experiment. PADC-AGE remains the only current external duty-rule control; the missing second complete external protocol is disclosed. No claim of comprehensive SOTA superiority is supported. Original rule/edge-case implementation tests and a new 480-case matrix are not applicable after the full-protocol gate fails; no implementation PASS is claimed.

The existing package audit retains all historical HENO-DC records, including its execution-source mismatch. It is not promoted to current confirmation.
