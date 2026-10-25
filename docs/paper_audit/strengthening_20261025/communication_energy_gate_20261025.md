# Gate 3: communication and energy model audit

## Checked implementation

- `code/simulation/service_model.py`: defaults, `control_cost`, `use_slot`, `attempt`.
- `code/simulation/v63_model.py:request_grant`: pre-response transit margin and subsequent ordinary reservation check.
- `code/simulation/diagnostic.py:attempt/debit`: data TX/RX, processing, affordability and unique demand states.
- `code/simulation/strengthening_model.py:attempt/round`: keyed clock/jitter check, five paid windows, conservative late-round endpoint envelope.
- `current_design.json`, `config.json`, `current_io.load_config`: effective frozen configuration.

## Findings and disposition

| Item | Verified model behavior | Implementation boundary / action |
|---|---|---|
| Guard vs payload | Payload 4000/250000 = 16 ms; Guard 20 ms is paid opportunity/uncertainty listening, not the entire physical frame slot. The late-round envelope sums discretionary listening and both endpoints' nominal payload times, with bound 99.98 s. | Abstract serialization is checked; it is not a contention schedule. A 500-byte logical payload exceeds a single 127-byte IEEE 802.15.4 MPDU and fragmentation is not modeled. State this in the paper. |
| Clock allowance | Worst relative drift 40 ppm over 200 s = 8 ms, plus relative jitter 8 ms and detection/turnaround 1 ms = 17 ms. The actual `attempt` checks keyed offsets against 20 ms. | These are configured bounds, not measured oscillator behavior or MAC synchronization validation. |
| Control width | Actual `control_frame_bits` is 64 in the executed default and main parameter table. Eq. (7) fees use that width. | Main narrative incorrectly said 160 bits: correct the prose to 64. Do not rewrite old records or change simulation costs. |
| Failure fees | Sender slot/fee are consumed before receiver/transit refusal; response is charged only after the corresponding stage is reached. Fee includes TX plus fixed control receive allowance. Failed data consumes TX/RX; successful processing is charged after decoding. | Fees are abstract allowances, not a complete frame-state implementation. No separate ACK/timeout state is simulated; do not claim otherwise. |
| Free reception | Intersensor data debit and transaction/hold checks remain in the shared physical executor. Sink bypass is explicit and sink has external power. | No free CH/member data reception found in the inspected execution paths. Broadcast propagation is an ideal paid information service, not a simulated broadcast MAC. |
| Atomicity | One request/response/data transition completes before another sender modifies local balances. Holds exclude other packets and protect one outgoing attempt. | Safety is under serialization; concurrent implementation needs atomic operations or a schedule. No hardware fairness/delivery guarantee. |
| Energy and hardware | Peak 0.12 J per 900 s is derived 0.133 mW; 4 J capacity and 3 J start are model settings. 56 mW is of the order of CC2420 RX at assumed 3 V. | No calibrated panel/storage/node is assigned. Ideal equivalent areas/capacitances in JSON are arithmetic examples, not selected hardware or measured specifications. |
| Daylight | Measured inputs have energy outside the fixed 06:00--18:00 forecast support; winter support also contains zero-GHI samples. Exact fractions are in `physical_accounting_20261025.json`. | Support mismatch is quantified, not relabeled full forecast error. Existing trajectories remain unchanged. |
| Planner cost | Full prefix computation precedes reactive selection, with O(IMH) local work and O(MH) storage. | No embedded runtime/CPU-energy measurement. Reactive selection does not make the implementation a cheap duty-only computation. |

Primary device source: Texas Instruments CC2420 datasheet, https://www.ti.com/lit/ds/symlink/cc2420.pdf, receive-current/data-rate specifications and section 16.2 length field. Device figures are manufacturer data; the model is not a CC2420 deployment validation.

## MAC experiment gate

A trustworthy contention experiment needs competing request arrival times, receiver arbitration, collisions, retries, ACK/timeouts and corresponding state-specific energy. Those states are absent from the current executor. Uniformly changing link success would not supply them. Therefore the gate for a new real-MAC sensitivity experiment is FAIL and no such experiment is started. This is a model-scope limit, not a finding of physical implementation validity.

## Completed checks

The five existing `test_v63.py` safety/information/neutrality tests passed (including exact off-switch equivalence and observer neutrality). The new logging wrapper reproduced all five stored metrics of one frozen confirmation case with zero difference. The full independent logging study additionally records late-round envelopes and timing misses; its final values will be audited after all planned cases finish.

Current status: no code-level energy/hold overbooking found in these checks; disclosure and narrative corrections are required before final GO. Final Gate 3 status depends on completed logging, frozen hashes and final consistency checks.

All 144 independent recordings completed without failures. Independent rescoring verifies 3,312 trajectory metrics and 96 aggregate rows. The maximum recorded conservative endpoint envelope was 21.83575090245332 s (limit 99.98 s), and timing misses were zero. This verifies the frozen abstract timing ledger, not frame-level MAC feasibility.
