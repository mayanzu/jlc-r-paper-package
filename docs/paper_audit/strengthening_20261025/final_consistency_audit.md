# Final consistency audit — 25 October 2026

## Scope correction before public release

The earlier GO below concerns numerical integrity, file readiness and reproducibility. The broader recommendation for immediate COMPAG submission was withdrawn after considering the limited incremental effects and severe observation gaps. Scientific competitiveness remains unresolved. The pre-publication access statements below are historical; the public v1.0.0 release is identified in `audit/github_release.json`.

## Original local-preparation disposition

**GO for submission of the local manuscript and complete reproducibility archive.** This is a submission-readiness judgment, not an acceptance forecast or a claim of field validation. Public GitHub release and journal upload are not performed; the author must attach the supplied archive or provide it on reviewer request, consistent with the availability statement. No online reviewer access is asserted.

The only formal main PDF is `main_cas_20261025_154339.pdf`, **19 pages**, SHA-256 `a4b1201035cce853919ca0876e8ba009f7b4ecbf7b77481c9f92a909a3bf2851`. The saved TeX and Markdown match the build manifest. No technical PDF was compiled. The manuscript contains five figures, five tables, the exact analytical statements/proof sketches, and 41 bibliography entries.

## Gate decisions and evidence

| Requirement | Disposition | Authoritative evidence |
| --- | --- | --- |
| H1 / paths and unique manuscript | PASS | COMPAG/manuscript.md, main_cas.tex and build_manifest.json; one main PDF; all new experiment files remain in existing v6_4 directory. |
| H2 / frozen science | PASS | frozen_preservation_20261025.json: 1,096 baseline code/data files inspected, no deletion; only seven existing workflow/README/map/inventory files changed. All 176 public immutable files and 864 original raw factorial hashes verified. |
| H3 / negative results | PASS | Main 5.5 / Table 5 / Discussion: all winter sources >4 h unavailable; 48.25% spring sources; unresolved JLC-Core P95 differences; conditional recovery and censoring disclosed. |
| H4 / 22-page cap | PASS | Actual CAS PDF: 19 pages including title, abstract, figures, tables, Appendix A, declarations and 41 references. Template fonts/margins unchanged; no overfull or undefined reference warnings. |
| Gate 0 / existing state | PASS | gate0_20261025.json and before snapshot; initial and final branch/commit unchanged; no checkout, reset, commit or push. |
| Gate 1 / external controls | PASS audited-stop route | Exactly two primary full texts: HENO-MAC and MAoIG. Full transfers fail the fixed-executor gate, duty-only adapter is conditional. No new independent SOTA comparison claimed and no further candidate search. |
| Gate 2 / task evidence | PASS simulation proxy | 144 independently seeded recordings, 144 raw 1344x100 delivered-birth matrices, protocol/source freeze, zero failures, source/event outputs and nominal paired intervals; no crop-event accuracy claim. |
| Gate 2 / parameter evidence | PASS | Nine evidence categories in parameter_evidence_20261025.csv and technical E9. 0.12 J/round, 4 J, 56 mW, Guards, 250 kbps, 4000 bits, 15-min workload and 60-min criterion are classified. |
| Gate 3 / physical accounting | PASS model audit; real-MAC experiment FAIL | 16-ms payload / 20-ms Guard / 17-ms uncertainty / 99.98-s envelope distinguished. Recorded maximum 21.83575090245332 s, zero timing misses. 64-bit narrative corrected. ACK, fragmentation, contention and planner CPU energy remain unvalidated. |
| Gate 3 / daylight | PASS support audit | Independent weather-input hash and support recomputation from all 3 scored 1344-round records; support mismatch is not labeled full forecast error. |
| Gate 4 / scientific manuscript | PASS | Introduction strengthened with two recent original COMPAG field papers; one reference application; no crop-stage mapping. Original six analytical statements and all full E1-E8 numeric checks retained. Five figures and five main tables. |
| Gate 5 / old statistics | PASS | Independent 32 NI decisions, original Holm-36 maximum 0.037107085836714966 and unchanged independent Holm-4; no new outcomes pooled into those families. |
| Gate 5 / new statistics | PASS | 3,312 trace numbers and 96 summary rows independently rescored; all 60 Table 5 values and new text reductions/rates checked, minute/hour conversion and nominal interval labels checked. |
| Gate 5 / reproduction | PASS | Current workspace and package reproduce passed; independent portable copy reproduce passed with runtime simulation-entry guard reporting zero entries. |
| Gate 5 / safety and dispatch | PASS | 5 current safety/information/observer tests passed in 51.036 s; 7 packaging tests passed; recording boundary selftests and frozen-case regression passed; reliability rerun dry-run has 144 cases and starts no simulation. |
| Gate 5 / PDF and references | PASS | Desktop compiler success for final saved TeX; terminal build success; all 19 pages rendered and inspected, no missing figure/overflow. Figure 1 equations 9-15/17/18, sections 3.3/3.4 and Algorithms 1/2 matched. |
| Gate 5 / availability and AI | PASS statement consistency | Data statement says archive available from corresponding author on reasonable request and GitHub planned upon publication. No public URL, DOI, journal upload or completed human review is invented. AI use includes manuscript, analysis/recording code and checks. |
| Reviewer handoff / external submission action | READY FOR AUTHOR ATTACHMENT | Final complete archive is delivered locally with a checksum; actual journal attachment/public release is not performed or represented as verified online reviewer access. This is the author submission step, not an executed experiment. |

## New findings and limits

The locked post-confirmation availability study completed all 144 cases with no failures, using twelve new paired network seeds (230101 through 231212, step 101), four unchanged controllers, T1/T3 at supply 0.7 and T2 at 1.0. Original outcome families and source bytes are retained. Wrapper fidelity regression reproduces five frozen reference metrics with zero deviation.

For JLC-R, the means of within-run source-P95 longest observed gaps are 309.14 h, 319.64 h and 21.28 h in T1, T3 and T2. Every winter source experiences a gap over four hours; the spring proportion is 48.25% overall and 75.48% among far sources. Reductions versus Prefix-only are 13.15, 10.20 and 6.56 h with nominal paired intervals. Corresponding differences from JLC-Core remain unresolved. Completed recovery is conditioned on prior service and completion; initialization is excluded and right-censoring is separately reported. Lower event counts and shorter completed-only recovery can coexist with severe persistent unavailability.

HENO-MAC and MAoIG fail faithful transfer inside the current fixed executor, for documented decision-interface conflicts. MAoIG permits estimated harvest rates; no oracle premise is used to reject it. The missing second complete external protocol remains a scientific limitation. Fragmentation, frame-state ACK/timeouts, contention atomicity, hardware energy calibration, planner CPU costs and crop-event outcomes remain unvalidated. These do not invalidate the scoped simulation results; the paper does not advertise them as established.

## Frozen evidence and repository state

Base branch: `codex/jlc-r-v6.3-relay-repair`; base commit: `e8e58650199e3508b94ac455c62f5c4bab87d689`. The final manuscript is an uncommitted working-tree revision, identified by the build/source/archive checksums rather than represented as the contents of that base commit. The pre-existing dirty tree was preserved; no commit, reset, checkout or push was performed. Full initial/final status is in the local process archive.

All 1,096 pre-existing code/data paths remain present. The seven changed old paths are workflow entry points, verifiers, current inventory, README and figure-label mapping; original simulation modules, scientific analysis programs, CSVs, NOAA inputs and formal raw records retain their bytes. All 176 public frozen files and 864 original factorial raw hashes pass. Full change inventories are supplied separately.

## Reproduction and review delivery

Commands: `python -B code/verify_delivery.py --manifest`; `python -B COMPAG/build.py --check`; `python -B COMPAG/audit/check_extension.py`; `python -B scripts/reproduce.py --mode verify/reproduce` in the minimum package; and explicit `--mode rerun --study reliability --dry-run`. Verify/reproduce never run a simulation and write generated analysis only to new directories. The independent portable-copy run guards actual simulation entry calls and records zero. Complete E1-E8 remain unchanged, with parameter E9 and availability E10 added to the editable technical source.

Local validation logs and all 19 rendered pages are in `temp/COMPAG_work/submission_strengthening_20261025_145832/`. Current/reproduction-generated results are under the prescribed `temp/current_research/` and `temp/minimal_reproduction/` work areas. Historical PDF/archive exports remain offline in temp; only the latest main PDF and latest handoff archive are current deliveries.
