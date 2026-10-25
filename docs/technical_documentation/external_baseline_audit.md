# External-baseline comparability audit

Scope: author-prepared source and retained-record audit, revised 24 October 2026.
This is not an independent protocol replication or a new performance experiment.
The current full-text gate is documented in [the 25 October audit](../paper_audit/strengthening_20261025/external_baseline_gate_20261025.md); it supports the external-comparison scope in current Section 4.1 and Discussion. It supersedes the MAoIG
future-information rationale in earlier candidate/fairness notes, which are
retained as historical records rather than rewritten.

## Published assumptions and inputs

| Candidate | Source and original inputs | Conflict with the frozen S200/G20 experiment | Decision and evidence boundary |
| --- | --- | --- | --- |
| HENO-MAC | Sarang et al., WCNC 2024, DOI [10.1109/WCNC57260.2024.10571258](https://doi.org/10.1109/WCNC57260.2024.10571258). [Author version](https://arxiv.org/abs/2401.00717), Sections III-A/B, Table I, Eq. (6), Section IV/Table II: solar/wind energy, remaining battery, energy-neutral state, receiver beacons, packet priority and CSMA contention; evaluated in a single-hop star. | The present executor uses solar-only inputs, fixed role/candidate installation, offered source samples and charged Guard transactions with one-hop holds. Mapping only the duty fraction omits the priority handshake, contention and original harvesting configuration. | The retained HENO-DC experiment is a duty-rule adapter. It is neither full HENO-MAC nor a current S200/G20 benchmark. |
| MAoIG | Chen et al., IEEE Internet of Things Journal 9(24), 25736-25751 (2022), DOI [10.1109/JIOT.2022.3197428](https://doi.org/10.1109/JIOT.2022.3197428). [Accepted manuscript](https://pure.coventry.ac.uk/ws/portalfiles/portal/56402495/Binder13.pdf), Section III-A, Definition 9, Section V-A and Algorithm 2: graph, local battery and predicted harvesting rates, workloads and neighbor feedback, update times and interference constraints. | MAoIG selects energy-adaptive paths and constructs a forwarding tree each cycle, then coordinates update generation and interference-constrained transmissions. The current fixed-role, Guard-transaction executor does not expose these joint decisions. | No complete MAoIG implementation is evaluated here. A fair comparison needs an executor extension and matched accounting for routing/control, listening, scheduling and offered-demand metrics. This is a study-scope limit, not proof that MAoIG cannot be ported. |

MAoIG's future affordability times are estimates. Section III-A explicitly
permits prediction from current measurements and past observations; Definition 9
uses estimated harvesting rates. A causal predictor is compatible with this
premise. Neither access to true future irradiance nor the assertion that causal
forecasting necessarily changes the core algorithm is an exclusion criterion.
The architectural mapping above is our assessment of comparability, rather than
a claim made by either original paper. No oracle-information experiment was run.

## Retained HENO-DC record: exact evidence route

Package root: `data/external_baselines/heno_g10/`. Original project source (now archived offline):
`code/results/recent_baselines/`. Copies retain original bytes and identifiers.

| Package-relative path below that root | Record meaning |
| --- | --- |
| `heno/design.json` | Four methods, two weather conditions, two supplies and twelve seeds: 192 executions, fourteen days each. |
| `heno/provenance.json` | Original configuration and execution-source hashes; `guard_listen_s=0.01` identifies G10. |
| `heno/RECENT_BASELINES_SPEC.md` | Frozen rule mapping, shared costs and historical comparison contract. |
| `heno/metrics.csv` | All 192 rows; 48 are HENO-DC. Historical `JLC-R` is not the present V63 implementation. |
| `metrics.csv`, `summary.csv`, `paired.csv`, `paired_source.csv` | Assembled 240-row comparison and original statistics, including the separate 48-row PADC-DC block. |
| `padc/`, `audit.json`, `provenance.json`, `audit_sources/` | Separate block, original assembly/analysis audit and frozen analysis scripts. These are retained evidence, not a fresh execution audit. |
| `adapter_source/recent_baselines.py` | Retained adapter for rule inspection; its hash differs from the HENO execution provenance version, so it is not an exact execution snapshot. |
| `evidence_manifest.json` | Source-to-package paths, byte sizes, SHA-256 values and direct checks of counts, seed sets and timing. |

The twelve seeds are `120101 + 101*k`, for `k=0,...,11`. The weather labels
are `SYNTHETIC` and `MEASURED`; supplies are 1.0 and 0.7. The HENO block's
recorded methods are `JLC-R`, `POINT-JL`, `JLC-R-FIXED` and `HENO-DC`.
They must not be relabeled as a V63 confirmation. The assembly audit records
a 16-test family; this is separate from the current Holm-36 and relay Holm-4
families. No historical result is promoted into either current family.

HENO-DC maps the duty fraction to paid scheduled listening, uses a completed
metered interval for its energy-neutral test and shares the historical
physical transaction checks. It omits hybrid harvesting, priority alarms and
the complete asynchronous MAC. Run-level metrics and provenance are supplied;
complete per-packet trajectories for this old comparison are not claimed.
The original provenance records adapter SHA-256
`e67abf7adf36a78c7d313e1538b75714a2e8df0f97eb9fbad483b3135d8f78f5`;
the retained adapter has SHA-256
`479ea23bdd0f379440934a7e43c84e58a617a7f337629c3c776cb765b7f5c805`.
The evidence manifest reports this difference explicitly. The exact historical
execution copy is not supplied, and historical source hashes alone do not
establish a fully reconstructable protocol execution. This limitation does not
change the frozen current-confirmation implementation or its execution snapshot.

## Reviewer delivery

The review archive includes this audit, the copied historical evidence,
confirmation/extension/factorial records and `SNAPSHOT_MANIFEST.sha256`.
Run `python -B verify_package.py` after extraction to verify distributed bytes.
The accompanying submission handoff gives an archive checksum and records
whether journal upload/reviewer visibility has actually been checked. Local
packaging alone is not reviewer access. No public repository or DOI is asserted.

The scientific limitation remains: PADC-AGE is the only external control in
the current S200/G20 confirmation, and a second complete external protocol
comparison has not been established.
