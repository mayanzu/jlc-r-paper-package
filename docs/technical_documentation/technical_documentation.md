---
title: "Technical Documentation"
subtitle: "Joint Listening-Credit Planning and Relay Protection for Fresh Data Collection in Solar-Powered Agricultural Sensor Networks"
date: ""
lang: en-US
---

This package technical documentation is not a separately submitted journal supplement. It retains former S labels for record traceability. The compressed article contains parameters (Table 1), an eight-condition confirmation summary (Table 2), relay primary tests (Table 3), spatial stress results (Table 4), and Appendix A with precise statements and proof sketches. Complete pre-compression displays are retained as Tables E1--E8 below. This documentation contains three parts: experimental design and core evidence; analytical statements and complete proofs; and the new relay-protection factorial study. Table identifiers are retained from the original evidence record for traceability; gaps identify earlier developmental material that is archived offline, outside this minimal package. Included evidence and limitations are mapped in `docs/reproduction_map.md`. Citation and equation numbers refer to the main article. Full standalone derivations are in `docs/analytical_proofs.md`; additional paired displays are Repository Figures R1--R2.

**Contents.** Part I contains method comparison and parameters (Tables S1--S2), paired budget controls (S64--S65), independent five-method means and paired effects (S67--S68), noninferiority tests (S63), and the separate retained benchmark (S62). Part II contains analytical statements, complete proofs and reservation transitions (S69). Part III describes the S200/G20 relay factorial and its separate Holm-4 family. Detailed seed identities and prior use are provided in `audit/seed_registry.csv`.


**Reproduction coverage.** The supplied configurations and seed-level records support current main Tables 1--4, extended Tables E1--E8 and statistical Figures 2--5 plus Repository Figures R1--R2. The command and data mappings are given in `docs/reproduction_map.md`; independent statistical and resource-invariant checks are implemented in the accompanying scripts.

# Part I. Experimental design and core evidence

## Supplementary Note S1. Core mechanism controls and evidence scope

The current confirmation evaluates five complete configurations, twelve paired network seeds and eight weather--supply cells. Supporting controls isolate mechanisms in their own configurations; they are not additional executions or ablations of complete JLC-R. A seed is the independent pairing unit. Nodes, packets, repeated initializations and weather conditions do not increase independent sample size.

**Joint versus fixed listening (Table S64).** The continuous joint-planning controller, JLC-R-Cont, and its fixed-listening control share the executor, newest-first discipline, forecasting inputs and physical constraints. Twelve paired seeds per method and supply form the original held-out study. These historical labels identify modular configurations, not the final hybrid. The matched point-forecast arms change forecasting conservatism; they do not establish calibrated coverage of the scenario bank. The original paired joint-versus-fixed outcomes and reference-floor controls are supplied under `code/results/strengthening/floor/`; additional rejected development paths are archived offline.

**Reference floor (Table S65).** Twelve reused paired seeds, $70101+101k$, $k=0,\ldots,11$, compare with-minus-without floor under both continuous/newest-first and integer-slot/local-age planning. The first-stage reference communication floor is removed; the second-stage credit and physical-affordability checks remain. These paired extensions use original base synchronization and a 10-ms guard (G10). Four coverage contrasts form one Holm family; age and energy use nominal paired intervals.

Table S1. Method comparison.

| Approach | Prefix scenario budget | Coupled listening & slot capacity | Charged 1-hop forwarding reservation | Failed-grant cost accounting |
|---|---|---|---|---|
| Duty-cycle MAC [@rmac2007; @rimac2008] | — | Partial | — | — |
| Predictive ENO / PADC-MAC [@kansal2007; @padc2023; @heno2024] | Partial | Partial | — | — |
| Conformal / uncertainty-aware node budgeting [@uncertainty2023; @conformal2024] | Partial | — | — | — |
| AoI scheduling [@aoi_survey2021; @timely2022; @ondemand2022; @partial2025; @lyapunov2023; @fresh_learning2022] | — | — | — | — |
| **JLC-R (Proposed)** | **Yes** | **Yes** | **Yes** | **Yes** |

**Table note.** Entries describe the four accounting dimensions represented in each compared model and do not exclude related mechanisms elsewhere in the same area; each approach remains applicable to its own problem setting. *Partial* marks a dimension addressed implicitly or at another protocol layer, and --- marks a dimension outside the scope of the compared model.

Table S2. Base parameters of the supporting simulation configurations.

| Category | Parameter | Value |
|---|---|---|
| Network | Nodes; area; range | 100; 300 m×300 m; 120 m |
| Organization | Cells; rotation candidates per cell | 4×3; 5 |
| Time | Macro-round; credit period; forecast horizon | 900 s; 4 rounds; 96 rounds |
| Duration | Formal evaluation; forecast warm-up | 14 days; 2 days |
| Battery | Capacity; initial energy; communication reserve | 4 J; 3 J; 0.15 J |
| Recovery | Restart threshold after outage | At least 0.08 J and affordable current base tasks |
| Harvesting | Peak; supply multiplier | 0.12 J/round; 1.0 and 0.7 |
| Data | Logical packet; deadline; queue limit | 4000 bits; 4 rounds; 256 packets |
| Radio | $E_{elec}$; $\varepsilon_{fs}$; $\varepsilon_{mp}$ | 50 nJ/bit; 10 pJ/(bit·m$^2$); 0.0013 pJ/(bit·m$^4$) |
| Processing | Sensing; aggregation | Both 5 nJ/bit |
| Base power | Sleep; offline; extra idle listening | 5 µW; 2 µW; 56 mW |
| Listening | Member/CH caps; sync; guard per transaction | 0.1/1 s; 20 ms; 10 ms |
| Grants | Request/response payload; logical data rate | 64 bits each; 250 kbps |
| Planning | Traffic margin; future relay fraction | 1.25; 0.65 |
| Forecast | EWMA coefficient; scenarios; residual quantile | 0.7; 4; 0.9 |
| Cache | Fresh grant check; routing-cache lifetime | Same macro-round; at most 1 round |
| Broadcast | Prepaid cost per node per credit period | 0.0002 J |
| Execution | Decoding attempt limit; per-node loop limit | 3; 96 |

**Table note.** The 10-ms guard in this base configuration belongs to the supporting controls. The primary JLC-R confirmation instead uses a 20-ms guard and five paid S200 synchronization windows, as specified in main-text Section 5.1. The original parameter values in this table are preserved; they do not override the primary design.

## Supplementary Note S3. Implementation and deployment assumptions

The simulation uses atomic serialized admission. Physical battery, perishable credit, guard capacity and existing forwarding holds are checked locally; a neighbor cache does not reveal private live receiver state. A charged failed request is not a free query. The 1.05 transmit-electronics factor, the reference sink-edge control allowance and the 96-action per-node cap are retained implementation choices rather than measured hardware properties. Resource safety does not establish rendezvous, contention avoidance, delivery or fairness.

Planning uses $O(IMH)$ local time and $O(MH)$ working storage, excluding reference-route preprocessing; the vectorized network implementation uses $O(IMNH)$ time and $O(MNH)$ working battery-path storage. Queue selection scans up to $Q_{max}$ packets per action. The streaming forecast bank keeps a bounded residual history and pending forecasts; optional precomputed banks store all issuances and have a larger simulation-only footprint. Finite bisection and action limits establish termination, not convergence of network utility.

The threat model assumes honest local meters, controller execution, source identifiers and gateway weather. Cache forgery can disrupt routing without increasing a receiver's locally checked resources. Deployment would require authenticated beacons, replay protection and per-neighbor admission limits with their memory, signaling and energy costs included. Atomic serialization omits hidden terminals, collisions, interference and spatial reuse. Guards are accounting opportunities, not a complete TSCH or asynchronous MAC implementation. The frozen simulator and its required parent modules are supplied under `code/simulation/`.

## Supplementary Note S6. Irradiance, synchronization and forecasting boundaries

NOAA SURFRAD trajectories [@surfrad2024] use 1--17 January 2024 for Table Mountain (T1) and Bondville (T3), and 1--17 April 2024 for Table Mountain (T2). Two days initialize forecasting, fourteen days are scored and the last day provides the forecast tail. The 15-minute GHI means map to $H_i=s\phi_i(0.12)(\overline G_{GHI}/1000)$ J/round. QC0 GHI is retained; invalid GHI is reconstructed only from QC0 direct and diffuse components using solar zenith. Negative irradiance is clamped before averaging. Interior gaps of at most five minutes permit linear interpolation; larger or edge gaps fail. Only one minute (9 April, 13:21 local standard time) requires interpolation. Local standard time is UTC-7 at Table Mountain and UTC-6 at Bondville, without daylight-saving shifts. Provenance files retain source hashes and transformations; measured traces receive no synthetic forced-cloud episodes. Three trajectories remain three environmental records, independently of network-seed count.

The fixed 06:00--18:00 reference is retained in every season. The EWMA uses completed observations only when the reference factor $g>0.1$; winter reference-floor and spring-clipping effects remain inherited model limitations. Harvest conversion has no second daylight multiplier, and reference-night outage still uses hours outside 06:00--18:00. Historical S100/S200 mean 100-s/200-s synchronization intervals (nine/five paid windows per 900-s round); G10/G20 mean 10-ms/20-ms guards. The primary design is S200/G20. Timing bounds use assumed clock/bias/jitter allowances rather than device calibration, and guard affordability alone does not certify rendezvous. The timing configuration and all three processed seasonal inputs are included; full developmental timing logs are archived offline.

## Supplementary Note S8. Implementation identity and control mapping

Final JLC-R is the relay-repaired hybrid controller `JLC-R-HYB-V63` (`code/simulation/v63_model.py:RelayRepairHYB`), extending the inherited native `HYB60` baseline (`code/simulation/v6_model.py:HYBSimulator`, code identifier `JLC-R-HYB`) under unchanged physical parameters (H96, period4, M4, S200/G20, entry/exit scales 0.60/0.70). In addition to the selective local uncovered-fresh queue gate, `JLC-R-HYB-V63` incorporates upstream CH transit protection (`M-B`), uncovered staleness tie-breaking (`M-A`) and minimum two-slot CH relay-demand recognition ($\lfloor a_i^P K_i^{ref}(t)\rfloor<2$). The reactive branch explicitly uses the PADC duty rule and nonbinding permissions. Prefix planning, local resource safety and PADC-derived reaction have different evidential roles; the PADC-derived reaction contribution is stated explicitly. Historical `JLC-R-SA` maps to the display label `JLC-R-Prefix`, historical `JLC-R` to `JLC-R-Cont`, and `JLC-R-FIXED` to `JLC-R-Fixed`; original CSV labels remain unchanged. The five confirmation methods appear in the released CSVs as `JLC-R-HYB-V63` (display JLC-R), `JLC-R-SA` (display Prefix-only), `JLC-R-HYB` (display Hybrid control; the HYB60 design), `PADC-AGE` and `PADC-AGE+V63` (display PADC+relay). Implementation notes: weather factors are normalized by the spatial median (across nodes) of the observed-to-clear ratio at each eligible completed daylight round, and the hybrid thin/exit scale code defaults (0.98/0.99) are overridden by the frozen experimental configuration (0.60/0.70). Failed OC-v1 outcome histories are archived offline. The public seed-use registry retains essential cohort identities and prior use; the core comparison and cohort roles are summarized here and in Note S9. In the synthetic input, metering noise is generated independently of physical weather. For measured NOAA input, the ideal observation equals the modeled harvest after irradiance conversion, without additional metering noise; the spatial normalization and completed-round update order remain unchanged.

## Supplementary Note S9. Confirmation inference and cohort boundaries

The independent confirmation uses $160101+101k$, $k=0,\ldots,11$, with zero prior occurrences in the retained search, five methods and eight cells (480 runs). Table S63 reports the 32 noninferiority contrasts; Table S67 reports all five-method means and Table S68 the matched paired effects. Comparators are Prefix-only on Synthetic/T2 and PADC-AGE on T1/T3. One-sided margins are -1 pp for coverage/P5, +1 pp for nighttime outage and +5% of the baseline mean for AoI. These 32 tests and four winter coverage-superiority tests form the prespecified Holm-36 family at $\alpha=0.05$. Nominal two-sided intervals describe effect uncertainty and do not replace that decision rule.

The all-zero T2 nominal-supply outage contrast is a deterministic margin satisfaction ($s_d=0$), not a finite-$t$ result. Removing it from the correction denominator leaves all stochastic primary decisions unchanged. Table S63 additionally reports the paired relative-AoI sensitivity, $1.05\times$baseline$-$candidate, in the separate 33-test family including the targeted winter-AoI repair test. That sensitivity accounts for uncertainty in the baseline-dependent age margin. The retained probability columns support conservative missing-slot and relative-AoI sensitivity checks; these are robustness views, not additional preregistered confirmation.

Table S62 retains the separate $150101+101k$ benchmark cohort. The first two benchmark seeds had previous synchronization-debug/fixture use. All twelve benchmark results remain without favorable retrospective exclusions, and none are pooled with the independent confirmation. The pre-repair HYB60 controller passed 29/32 primary NI contrasts under the audited Holm-36 procedure; this prior study remains identified in the public seed-use registry, while the final repair benchmark and independent confirmation have their own supplied result files. The repair was selected using four reused development seeds, $140101+101k$, $k=0,\ldots,3$, which supply no independent confirmation sample.

Host-Python warm-planning timings use twelve calls per condition/controller/scenario count and separate temporary allocation peaks. They include diagnostic overhead and exclude forecast-bank generation and service; they are not MCU runtime or calibrated CPU-energy measurements. The final controller computes the prefix plan even in reactive mode. Essential seed-use records are included; full timing and observation-array logs are archived offline. Statistical inference is conditional on independent network seeds and a small-sample paired-$t$ approximation, with repeated weather trajectories kept within their stated scope.

### Core mechanism and sensitivity results

Table S64. Historical joint-planning mechanism comparison.

| Supply | Controller | Fresh coverage (%) | Night outage (%) | Mean AoI (min) |
|---:|---|---:|---:|---:|
| 1.0 | JLC-R-Cont | 73.34 | 0.000 | 356.0 |
| 1.0 | POINT-JL | 73.38 | 0.000 | 362.4 |
| 1.0 | JLC-R-Fixed | 57.73 | 3.104 | 950.1 |
| 1.0 | POINT | 58.80 | 3.213 | 908.7 |
| 1.0 | LPL-MATCH | 53.66 | 0.913 | 442.8 |
| 1.0 | BENO(0.4) | 27.47 | 0.000 | 3021.4 |
| 0.7 | JLC-R-Cont | 57.37 | 0.165 | 915.6 |
| 0.7 | POINT-JL | 57.46 | 0.209 | 910.4 |
| 0.7 | JLC-R-Fixed | 40.40 | 6.715 | 1734.6 |
| 0.7 | POINT | 41.27 | 6.811 | 1671.2 |
| 0.7 | LPL-MATCH | 41.22 | 4.818 | 1265.6 |
| 0.7 | BENO(0.4) | 16.70 | 0.000 | 5670.2 |

**Table note.** Historical new-seed confirmation of the joint optimization, n=12 paired seeds per method and supply. JLC-R-Fixed denotes the fixed-profile configuration of JLC-R-Cont. All methods use the common newest-first discipline. JLC-R-Cont and POINT-JL receive the same joint decision variables and physical constraints. Zero observed outage describes these finite runs. Mean AoI is complementary to threshold coverage.

Table S65. Reference-floor effects in matched planning pairs.

| Planner | $s$ | Coverage (pp) | Holm p | AoI (min) | Energy (J) |
|---|---|---|---|---|---|
| Continuous | 1.0 | 13.70 [10.64, 16.76] | 1.73e-06 | -458.4 [-710.4, -206.4] | 10.5 [8.1, 12.9] |
| Continuous | 0.7 | 14.49 [12.29, 16.68] | 4.75e-08 | -622.8 [-977.1, -268.4] | 11.1 [9.0, 13.3] |
| Integer | 1.0 | 13.74 [10.56, 16.91] | 1.73e-06 | -328.4 [-512.0, -144.8] | 13.3 [10.6, 16.0] |
| Integer | 0.7 | 14.35 [12.44, 16.25] | 1.58e-08 | -409.8 [-648.4, -171.2] | 13.3 [11.7, 14.9] |

**Table note.** Historical base synchronization/G10 configuration; with minus without reference floor, twelve reused paired seeds per cell; nominal 95% paired t intervals. The four coverage tests form one Holm family. AoI and energy are secondary outcomes. Both original arms were rerun; these observations are paired extensions.

### Independent confirmation and separate benchmark

Table S67. Full five-method absolute means in the independent confirmation.

| Input | Supply | Controller | Coverage (%) | Mean AoI (min) | Source P5 (%) | Night outage (%) | Energy (J) |
|---|---:|---|---:|---:|---:|---:|---:|
| Synthetic | 1.0 | Hybrid control | 54.739 | 577.079 | 27.284 | 0.974 | 2218.790 |
| Synthetic | 1.0 | JLC-R | 55.062 | 545.303 | 28.691 | 0.983 | 2218.896 |
| Synthetic | 1.0 | Prefix-only | 54.660 | 586.162 | 27.230 | 0.531 | 2219.789 |
| Synthetic | 1.0 | PADC-AGE | 51.278 | 630.492 | 23.655 | 0.768 | 2190.671 |
| Synthetic | 1.0 | PADC+relay | 51.652 | 591.701 | 25.197 | 0.772 | 2190.749 |
| Synthetic | 0.7 | Hybrid control | 39.272 | 1127.244 | 15.948 | 5.427 | 1984.887 |
| Synthetic | 0.7 | JLC-R | 39.665 | 1046.021 | 17.752 | 5.439 | 1984.943 |
| Synthetic | 0.7 | Prefix-only | 38.922 | 1250.015 | 15.486 | 4.603 | 1983.755 |
| Synthetic | 0.7 | PADC-AGE | 34.155 | 1293.363 | 11.586 | 4.198 | 1942.633 |
| Synthetic | 0.7 | PADC+relay | 34.610 | 1161.352 | 12.624 | 4.204 | 1942.702 |
| T1 winter | 1.0 | Hybrid control | 14.867 | 4272.273 | 2.536 | 2.556 | 1610.738 |
| T1 winter | 1.0 | JLC-R | 15.398 | 3814.259 | 2.729 | 2.579 | 1610.813 |
| T1 winter | 1.0 | Prefix-only | 10.789 | 3947.077 | 2.331 | 0.943 | 1598.788 |
| T1 winter | 1.0 | PADC-AGE | 14.264 | 4106.294 | 3.265 | 3.198 | 1606.269 |
| T1 winter | 1.0 | PADC+relay | 14.698 | 3777.080 | 3.505 | 3.207 | 1606.280 |
| T1 winter | 0.7 | Hybrid control | 9.732 | 4146.056 | 2.940 | 20.953 | 1250.308 |
| T1 winter | 0.7 | JLC-R | 9.951 | 4080.726 | 3.120 | 21.067 | 1250.438 |
| T1 winter | 0.7 | Prefix-only | 5.375 | 8184.607 | 1.626 | 17.250 | 1247.310 |
| T1 winter | 0.7 | PADC-AGE | 9.636 | 4241.756 | 3.561 | 22.754 | 1251.909 |
| T1 winter | 0.7 | PADC+relay | 9.719 | 4198.559 | 3.619 | 22.755 | 1251.909 |
| T2 spring | 1.0 | Hybrid control | 70.377 | 75.417 | 36.513 | 0.000 | 2410.504 |
| T2 spring | 1.0 | JLC-R | 70.599 | 72.032 | 38.620 | 0.000 | 2410.614 |
| T2 spring | 1.0 | Prefix-only | 70.459 | 81.068 | 36.503 | 0.000 | 2408.573 |
| T2 spring | 1.0 | PADC-AGE | 68.306 | 85.356 | 34.389 | 0.000 | 2404.327 |
| T2 spring | 1.0 | PADC+relay | 68.596 | 80.488 | 37.204 | 0.000 | 2404.428 |
| T2 spring | 0.7 | Hybrid control | 47.704 | 342.786 | 15.749 | 0.009 | 2162.704 |
| T2 spring | 0.7 | JLC-R | 48.086 | 291.959 | 17.828 | 0.009 | 2162.718 |
| T2 spring | 0.7 | Prefix-only | 48.393 | 426.996 | 15.656 | 0.000 | 2159.461 |
| T2 spring | 0.7 | PADC-AGE | 43.470 | 432.096 | 10.935 | 0.017 | 2141.508 |
| T2 spring | 0.7 | PADC+relay | 43.915 | 327.549 | 12.983 | 0.017 | 2141.517 |
| T3 winter | 1.0 | Hybrid control | 8.368 | 4975.376 | 2.218 | 42.689 | 1017.764 |
| T3 winter | 1.0 | JLC-R | 8.555 | 4890.627 | 2.448 | 42.756 | 1017.912 |
| T3 winter | 1.0 | Prefix-only | 4.919 | 7688.690 | 1.044 | 39.665 | 1014.132 |
| T3 winter | 1.0 | PADC-AGE | 8.055 | 5092.023 | 2.861 | 43.577 | 1018.353 |
| T3 winter | 1.0 | PADC+relay | 8.127 | 5065.694 | 2.936 | 43.580 | 1018.353 |
| T3 winter | 0.7 | Hybrid control | 6.476 | 6433.808 | 1.811 | 59.034 | 816.944 |
| T3 winter | 0.7 | JLC-R | 6.580 | 6394.479 | 2.078 | 59.084 | 817.062 |
| T3 winter | 0.7 | Prefix-only | 3.850 | 8715.874 | 0.933 | 56.691 | 813.762 |
| T3 winter | 0.7 | PADC-AGE | 6.235 | 6356.825 | 2.387 | 59.721 | 818.594 |
| T3 winter | 0.7 | PADC+relay | 6.273 | 6356.324 | 2.489 | 59.722 | 818.594 |

**Table note.** All five methods, eight cells and twelve unused seeds (480 records). Display aliases do not alter CSV identifiers; means are computed within cell and method. The PADC transfer control is diagnostic and does not redefine the primary matched baselines.

Table S68. JLC-R minus matched strong baseline in the unseen twelve-seed confirmation (`160101`--`161212`).

| Input | Supply | Coverage pp | Mean AoI min | Source P5 pp | Night outage pp |
|---|---|---|---|---|---|
| Synthetic | 1.0 | 0.402 [0.087, 0.717] | -40.859 [-75.545, -6.173] | 1.461 [0.663, 2.259] | 0.452 [0.292, 0.612] |
| Synthetic | 0.7 | 0.743 [0.408, 1.079] | -203.994 [-325.459, -82.530] | 2.266 [1.345, 3.186] | 0.836 [0.653, 1.019] |
| T1 winter | 1.0 | 1.134 [0.924, 1.343] | -292.034 [-442.405, -141.663] | -0.536 [-0.741, -0.332] | -0.619 [-0.666, -0.573] |
| T1 winter | 0.7 | 0.314 [0.245, 0.384] | -161.030 [-228.236, -93.825] | -0.440 [-0.712, -0.168] | -1.687 [-1.742, -1.631] |
| T2 spring | 1.0 | 0.140 [0.033, 0.247] | -9.037 [-20.587, 2.513] | 2.117 [1.348, 2.886] | 0.000 [0.000, 0.000] |
| T2 spring | 0.7 | -0.307 [-0.561, -0.052] | -135.037 [-254.468, -15.606] | 2.172 [1.019, 3.325] | 0.009 [-0.006, 0.025] |
| T3 winter | 1.0 | 0.501 [0.394, 0.608] | -201.396 [-239.462, -163.330] | -0.413 [-0.634, -0.191] | -0.821 [-0.879, -0.763] |
| T3 winter | 0.7 | 0.344 [0.262, 0.426] | 37.654 [6.068, 69.239] | -0.309 [-0.530, -0.087] | -0.638 [-0.668, -0.608] |

**Table note.** Means [nominal paired 95% t CI], $n=12$ strictly unseen seeds (`160101+101k`) per cell. Matched strong baseline is `JLC-R-Prefix` for Synthetic/T2 and `PADC-AGE` for T1/T3. All **32/32** primary noninferiority tests pass under the 36-test Holm family ($\alpha=0.05$), the 32-test Holm family, and the paired relative-AoI sensitivity family (Tables S62--S63). Complete 12-seed results on `150101`--`151212` (**32/32** NI pass) are in Table S62. The 32/32 conclusion uses prespecified noninferiority margins and Holm adjustment; it does not mean that all 32 mean differences favor V63. In particular, adverse winter P5, reduced-supply T3 age, synthetic outage and reduced-supply spring coverage means remain in the table.

Table S63. Relay-repaired `JLC-R-HYB-V63` noninferiority tests on the unseen twelve-seed confirmation (`160101`--`161212`, 32/32 NI pass).

| Input | Supply | Metric | Mean delta | Raw p | Holm-36 p | Rel-AoI Holm-33 p | Status |
|---|---|---|---|---|---|---|---|
| Synthetic | 1.0 | Coverage | 0.402 | 4.554e-07 | 7.742e-06 | 8.197e-06 | NI |
| Synthetic | 1.0 | Mean AoI | -40.859 | 0.0004874 | 0.002162 | 0.01159 | NI |
| Synthetic | 1.0 | P5 | 1.461 | 1.498e-05 | 0.0001648 | 0.0001648 | NI |
| Synthetic | 1.0 | Night outage | 0.452 | 5.740e-06 | 8.036e-05 | 8.036e-05 | NI |
| Synthetic | 0.7 | Coverage | 0.743 | 9.465e-08 | 1.704e-06 | 1.798e-06 | NI |
| Synthetic | 0.7 | Mean AoI | -203.994 | 0.0002641 | 0.001585 | 0.003958 | NI |
| Synthetic | 0.7 | P5 | 2.266 | 4.107e-06 | 6.160e-05 | 6.160e-05 | NI |
| Synthetic | 0.7 | Night outage | 0.836 | 0.03711 | 0.03711 | 0.04644 | NI |
| T2 spring | 1.0 | Coverage | 0.140 | 4.976e-11 | 1.095e-09 | 1.144e-09 | NI |
| T2 spring | 1.0 | Mean AoI | -9.037 | 0.01490 | 0.02979 | 0.04644 | NI |
| T2 spring | 1.0 | P5 | 2.117 | 1.141e-06 | 1.825e-05 | 1.825e-05 | NI |
| T2 spring | 1.0 | Night outage | 0.000 | 0 | 0 | 0 | NI |
| T2 spring | 0.7 | Coverage | -0.307 | 4.478e-05 | 0.0004115 | 0.0004115 | NI |
| T2 spring | 0.7 | Mean AoI | -135.037 | 0.007458 | 0.02237 | 0.03281 | NI |
| T2 spring | 0.7 | P5 | 2.172 | 4.115e-05 | 0.0004115 | 0.0004115 | NI |
| T2 spring | 0.7 | Night outage | 0.009 | 1.324e-19 | 4.635e-18 | 4.238e-18 | NI |
| T1 winter | 1.0 | Coverage | 1.134 | 7.879e-11 | 1.654e-09 | 1.733e-09 | NI |
| T1 winter | 1.0 | Mean AoI | -292.034 | 7.916e-06 | 0.0001029 | 0.0001102 | NI |
| T1 winter | 1.0 | P5 | -0.536 | 0.0002037 | 0.001426 | 0.001426 | NI |
| T1 winter | 1.0 | Night outage | -0.619 | 1.178e-16 | 3.770e-15 | 3.417e-15 | NI |
| T1 winter | 0.7 | Coverage | 0.314 | 8.943e-14 | 2.325e-12 | 2.415e-12 | NI |
| T1 winter | 0.7 | Mean AoI | -161.030 | 4.826e-08 | 9.169e-07 | 8.197e-06 | NI |
| T1 winter | 0.7 | P5 | -0.440 | 0.0004323 | 0.002162 | 0.002594 | NI |
| T1 winter | 0.7 | Night outage | -1.687 | 3.098e-18 | 1.022e-16 | 9.295e-17 | NI |
| T3 winter | 1.0 | Coverage | 0.501 | 2.439e-12 | 5.853e-11 | 6.097e-11 | NI |
| T3 winter | 1.0 | Mean AoI | -201.396 | 1.355e-11 | 3.116e-10 | 2.118e-10 | NI |
| T3 winter | 1.0 | P5 | -0.413 | 5.709e-05 | 0.0004567 | 0.0004567 | NI |
| T3 winter | 1.0 | Night outage | -0.821 | 3.553e-16 | 1.066e-14 | 9.948e-15 | NI |
| T3 winter | 0.7 | Coverage | 0.344 | 4.460e-13 | 1.115e-11 | 1.160e-11 | NI |
| T3 winter | 0.7 | Mean AoI | 37.654 | 3.459e-10 | 6.918e-09 | 1.963e-08 | NI |
| T3 winter | 0.7 | P5 | -0.309 | 1.353e-05 | 0.0001624 | 0.0001624 | NI |
| T3 winter | 0.7 | Night outage | -0.638 | 7.974e-19 | 2.711e-17 | 2.472e-17 | NI |

**Table note.** One-sided NI, $\alpha=0.05$, $n=12$ strictly unseen seeds (`160101`--`161212`); means are `JLC-R-HYB-V63` minus the frozen matched strong baseline (`JLC-R-SA` on Synthetic/T2 and `PADC-AGE` on T1/T3). All 32/32 tests pass under Holm-36, Holm-32 and Rel-AoI Holm-33 (`code/experiments/v6_3_relay_repair/D_noninferiority_seeds16.csv`). The T2/$s=1.0$ nighttime-outage contrast is degenerate ($0.000\%$ vs. $0.000\%$ on all twelve seeds, $s_d=0$): the released row records $t=\infty$ and $p=0$, which is interpreted as deterministic margin satisfaction rather than a finite-$t$ result.



**V63 implementation correspondence.** The final transit check precedes receiver response charging and uses a binary guard margin, plus a transit energy unit containing the maximum upstream receiver-control charge, reception/processing and reference forwarding. Two guards are the minimum reception-plus-forwarding demand recognized at period installation, not two extra free guards. Algorithms 1--2 in the main text specify this ordering; Python, physical costs and existing numerical results are unchanged. Historical conditional service sufficiency additionally requires V63 member admissions to pass its protected-resource checks.


**Multiplicity-column interpretation.** The main V63 result uses the specified 32 noninferiority contrasts plus four winter-coverage improvement tests, a 36-test one-sided Holm family at $\alpha=0.05$. The independent 480-row table reproduces 32/32 passes, as does the paired relative-AoI sensitivity (32 NI contrasts plus the targeted HYB60 age-repair contrast). The supplied auxiliary `p_holm37` column numerically matches the 36 tests with an additional conservative reserved $p=1$ slot, rather than the actual targeted repair probability. It yields 31/32 NI passes in the new-seed cohort and is not the primary procedure. Likewise, 32/32 is not established there at the stricter $\alpha=0.025$ cutoff. Original CSV values, primary baselines, margins and all adverse means are unchanged.

Table S62. Retained-seed benchmark: relay-repaired `JLC-R-HYB-V63` noninferiority tests on the retained twelve-seed family (`150101`--`151212`, 32/32 NI pass).

| Input | Supply | Metric | Mean delta | Raw p | Holm-36 p | Rel-AoI Holm-33 p | Status |
|---|---|---|---|---|---|---|---|
| Synthetic | 1.0 | Coverage | 0.354 | 2.388e-08 | 4.536e-07 | 4.536e-07 | NI |
| Synthetic | 1.0 | Mean AoI | -43.881 | 2.318e-05 | 0.0002549 | 0.0009775 | NI |
| Synthetic | 1.0 | P5 | 1.554 | 0.0007321 | 0.003501 | 0.003501 | NI |
| Synthetic | 1.0 | Night outage | 0.430 | 7.116e-07 | 1.139e-05 | 1.210e-05 | NI |
| Synthetic | 0.7 | Coverage | 0.762 | 3.778e-08 | 6.800e-07 | 6.800e-07 | NI |
| Synthetic | 0.7 | Mean AoI | -203.827 | 3.682e-05 | 0.0003682 | 0.0009775 | NI |
| Synthetic | 0.7 | P5 | 2.285 | 3.595e-06 | 5.393e-05 | 5.393e-05 | NI |
| Synthetic | 0.7 | Night outage | 0.751 | 0.001576 | 0.004728 | 0.004728 | NI |
| T2 spring | 1.0 | Coverage | 0.193 | 9.553e-10 | 1.911e-08 | 2.102e-08 | NI |
| T2 spring | 1.0 | Mean AoI | -24.155 | 0.02355 | 0.02355 | 0.03292 | NI |
| T2 spring | 1.0 | P5 | 2.306 | 0.0005835 | 0.003501 | 0.003501 | NI |
| T2 spring | 1.0 | Night outage | 0.000 | 0 | 0 | 0 | NI |
| T2 spring | 0.7 | Coverage | -0.031 | 7.716e-06 | 0.0001003 | 0.0001080 | NI |
| T2 spring | 0.7 | Mean AoI | -152.043 | 0.004224 | 0.008448 | 0.01440 | NI |
| T2 spring | 0.7 | P5 | 1.827 | 0.0002351 | 0.001646 | 0.001646 | NI |
| T2 spring | 0.7 | Night outage | 0.012 | 1.239e-19 | 4.336e-18 | 3.964e-18 | NI |
| T1 winter | 1.0 | Coverage | 1.133 | 1.712e-11 | 4.108e-10 | 4.279e-10 | NI |
| T1 winter | 1.0 | Mean AoI | -195.944 | 6.490e-06 | 9.086e-05 | 0.0001599 | NI |
| T1 winter | 1.0 | P5 | -0.456 | 0.0006233 | 0.003501 | 0.003501 | NI |
| T1 winter | 1.0 | Night outage | -0.599 | 7.805e-18 | 2.654e-16 | 2.420e-16 | NI |
| T1 winter | 0.7 | Coverage | 0.297 | 1.035e-13 | 3.000e-12 | 2.793e-12 | NI |
| T1 winter | 0.7 | Mean AoI | -134.910 | 2.703e-07 | 4.595e-06 | 1.210e-05 | NI |
| T1 winter | 0.7 | P5 | -0.312 | 1.282e-05 | 0.0001539 | 0.0001599 | NI |
| T1 winter | 0.7 | Night outage | -1.663 | 9.514e-18 | 3.140e-16 | 2.854e-16 | NI |
| T3 winter | 1.0 | Coverage | 0.463 | 4.542e-12 | 1.136e-10 | 1.181e-10 | NI |
| T3 winter | 1.0 | Mean AoI | -231.758 | 3.177e-10 | 6.988e-09 | 7.930e-09 | NI |
| T3 winter | 1.0 | P5 | -0.390 | 4.790e-05 | 0.0004311 | 0.0005269 | NI |
| T3 winter | 1.0 | Night outage | -0.779 | 1.258e-16 | 4.025e-15 | 3.648e-15 | NI |
| T3 winter | 0.7 | Coverage | 0.306 | 4.290e-11 | 9.866e-10 | 1.030e-09 | NI |
| T3 winter | 0.7 | Mean AoI | 3.786 | 6.700e-10 | 1.407e-08 | 3.025e-08 | NI |
| T3 winter | 0.7 | P5 | -0.411 | 0.0001345 | 0.001076 | 0.001076 | NI |
| T3 winter | 0.7 | Night outage | -0.608 | 9.690e-16 | 3.004e-14 | 2.713e-14 | NI |

**Table note.** One-sided NI, $\alpha=0.05$, $n=12$ (`150101`--`151212`); means are `JLC-R-HYB-V63` minus the frozen matched strong baseline (`JLC-R-SA` on Synthetic/T2 and `PADC-AGE` on T1/T3). All 32/32 tests pass under Holm-36, Holm-32, Rel-AoI Holm-33, and Holm-36 at $\alpha=0.025$ (`code/experiments/v6_3_relay_repair/D_noninferiority_seeds15.csv`). The T2/$s=1.0$ nighttime-outage contrast is degenerate ($0.000\%$ vs. $0.000\%$ on all twelve seeds, $s_d=0$): the released row records $t=\infty$ and $p=0$, which is interpreted as deterministic margin satisfaction rather than a finite-$t$ result.

\clearpage


## External-baseline transfer audit and reviewer access

The companion `docs/technical_documentation/external_baseline_audit.md` records the original assumptions and inputs of HENO-MAC and MAoIG, their mapping limits under S200/G20, and the evidence supporting the baseline scope in Section 5.3. MAoIG uses predicted harvesting rates to estimate affordable transmission times; the comparison is left open because its dynamic routing, per-cycle tree, update-generation decisions and interference-constrained schedule require executor extensions. No assumption of perfect future irradiance is used to exclude it.

The retained HENO-DC evidence is supplied under `data/external_baselines/heno_g10/`, including the original design, specification, 192-row HENO execution block, combined 240-row comparison, paired statistics, provenance, frozen analysis scripts and a retained adapter source. The adapter hash differs from the original execution provenance, so an exact historical execution-source copy is not claimed. It is a G10 rule-adapter study with twelve seeds per condition-method cell, not a second complete MAC comparison or an S200/G20 confirmation. Recorded method identifiers and all numerical files are preserved byte for byte. The audit maps the exact record paths and checksums.

The author-prepared review archive contains the technical documentation, original confirmation, agricultural extension and relay-factorial records with a file-level SHA-256 manifest. It must be attached through the journal submission system and made available to reviewers; preparation on the authors' computer is not evidence of reviewer access. No public URL or DOI is claimed. Upload and reviewer-visible attachment checks are specified in the submission handoff instructions.

# Part II. Analytical statements and complete proofs

## Supplementary Note S11. Supporting analytical statements and proofs

The prefix and serial-execution results below concern fixed planning inputs and the stated execution assumptions. The historical ideal-feedback rescue intervention is archived offline and is not a component of JLC-R.

**Analytical scope.**

The continuous-planning supporting model and the integer JLC-R executor share the following monotonicity and resource-safety foundations for the prefix and atomic execution modules. The scalar optimum and scenario-prefix certificate concern the prefix branch only; physical affordability, reservation safety and demand conservation continue to bind both modes. Lemma 1 consolidates the scalar, invariance and conservation invariants; Propositions 1--3 state the queue-order mechanism, the feasible-set structure of the joint plan and the starvation counterexample; Theorem 1 gives conditional schedule sufficiency. These properties make the stated budget and commitment rules well defined; their effects on freshness, outage and fairness require the controlled experiments in Section 6.

The results distinguish scalar optimization, physical safety, reservation safety and conditional service. Exact-arithmetic statements require nonnegative margins, whereas numerical feasibility accepts margins down to $-\epsilon_{num}$ with $\epsilon_{num}=10^{-10}$ J; the proofs below state the separate reservation-audit and physical-balance tolerances together with their distinct roles.

**Assumption A1 (Atomic serialized admission).** A receiver completes one request, charged response/denial and resulting data transition before another request can inspect or modify its local balances. Concurrent radio receptions, hidden terminals and distributed compare-and-swap are outside this model.

**Lemma 1 (Execution safety and numerical-accuracy invariants).** *Fix the current battery, role sequence, listening plan, reference load and scenario bank. Let $\mathcal F_\epsilon\subseteq[0,B_{max}]$ contain credits whose prefix margins in (14) are all at least $-\epsilon$ for a fixed listening intensity $a$. If $0\in\mathcal F_\epsilon$, then $\mathcal F_\epsilon$ is a closed interval $[0,x_\epsilon^*]$, and after $I$ bisections the returned feasible lower endpoint $L_I$ satisfies $0\le x_\epsilon^*-L_I\le B_{max}2^{-I}$. Under the affordability guard $E_i(t)\le B_i(t)$ and (4), each node satisfies $0\le B_i(t)\le B_{max}$, and every admitted feasible credit satisfies all scenario prefix reserve constraints. Under A1, at serialized transaction boundaries the held energy and held guard transactions never exceed the receiver's uncommitted balance and capacity: $E_j^{res}\le\max\{0,\min\{c_j,B_j-B_{reserve}\}\}$ and $|\mathcal S_j(t)|\le k_j$. Finally, for any horizon $T$, offered demand $NT$ equals unsampled, delivered, expired, overflowed and in-transit packets, and the node energy ledger closes:*

$$
B_i(T)=B_i(0)+\sum_{t=0}^{T-1}\bigl[H_i(t)-E_i^{spilled}(t)\bigr]-\sum_{t=0}^{T-1}\bigl[E_i^{base}(t)+E_i^{data}(t)+E_i^{ctrl}(t)\bigr].
$$

*The proof, which follows from monotonicity of the clipped battery recursion, the affordability guard, serialized reservations and the disjoint terminal outcomes, is given in the proofs below. If zero credit is infeasible for the fixed intensity, returning zero is a fallback without a feasibility certificate. For $B_{max}=4$ J and $I=15$, the credit error is bounded by $1.22\times10^{-4}$ J, and the per-round release error by at most $3.05\times10^{-5}$ J. These bounds concern the fixed-input scalar optimum in $\mathcal F_\epsilon$, rather than network freshness optimization; numerical execution permits prefix margins down to $-10^{-10}$ J, so exact reserve feasibility at machine precision is not asserted.*

**Proposition 1 (Protected-credit head-of-line blocking).** *Consider two unexpired packets at a relay, with an uncommitted packet ahead of a committed one, and let the committed packet $p$ own the relay's only hold, with $\min\{c_j,B_j-B_{reserve}\}=E_j^{res}=e_j^{hold}(p)>0$. A FIFO loop that stops at an unaffordable head then performs no transaction, even though the committed packet can still be served from its own hold: if its outgoing control-plus-data cost is at most $e_j^{hold}(p)$, its guard is available, and downstream admission and decoding succeed, selecting it first permits service.*

*Proof.* Equation (16) gives $e_j^{free}=0$ for the head packet, which it cannot cover; the committed packet's own hold covers its checked cost, so the same safe resource balances support a transaction solely through queue order. $\square$

The proposition explains how identical safe resource balances can support different executed service solely through queue order: locking without compatible priority can reduce coverage, while committed-service priority removes the obstruction.

**Proposition 2 (Feasible-set structure and credit-only infeasibility).** *For $\chi_{floor}=1$ and a fixed listening intensity $a$, let $F(a)=T_LaD_i(0)$ in the continuous-listening planner variant (where $r_i(0;a)=a$ without integer Guard flooring) and $F(a)=T_Lr_i(0;a)D_i(0)$ in JLC-R. If the least-cost reference plan $x=F(a)$ is prefix-feasible, then every credit in $[F(a),x_\epsilon^*(a)]$ is feasible, and $x_\epsilon^*(a)$ is nonincreasing in $a$ because planned expenditure (12) is nondecreasing in the listening intensity. If the zero-credit base plan at $a=1$ is already infeasible — the prefixes in (14) fail for $x=0$ — then no credit $x_i\ge0$ restores feasibility at that intensity: credit alone cannot repair an unaffordable listening base. The joint variable can restore feasibility by lowering $a$, since a sufficiently small intensity admits the zero-credit plan whenever the synchronization-level plan itself is affordable.*

*Proof.* Both statements follow from the monotone recursion in (13)--(14): expenditure is nondecreasing in $a$ and in $x$, while the clipped battery update is nondecreasing in the entering battery, so increasing either variable can only tighten every prefix margin. Downward closure of the feasible set then yields the interval and the monotonicity of its upper endpoint; and if any required prefix fails at zero credit, adding credit only deepens the shortfall. $\square$

Proposition 2 formalizes why the fixed-profile design benefits structurally from the joint variable: when the listening base dominates expenditure, credit-based repair is infeasible, whereas joint planning reframes the feasible set by paying for less listening and accepting the correspondingly smaller transaction capacity. The empirical counterpart — near-unchanged aggregate energy with sharply different listening/credit allocation — is reported in Section 6.2 of the main article.

**Proposition 3 (Committed-first starvation counterexample).** *There exist admissible arrival patterns and initial states under which committed-first service starves an uncommitted source indefinitely: if one bottleneck has capacity for one fresh packet per round and an already committed source always precedes a waiting uncommitted source, repeating this pattern serves the former and expires the latter forever. Committed-first priority and bounded queues therefore do not imply fairness. A sufficient deterministic protection is to guarantee every source a successful, fully funded route within latency $L_s$ after a new sample at least every $W_s$ rounds; its end-of-round age is then bounded by $(W_s+L_s)\Delta t$ after initialization. JLC-R provides no such per-source allocation.*

*Proof.* The periodic pattern is admissible, so induction over rounds serves only the committed source; each uncommitted sample expires after its deadline. The bound under the stated guarantee follows from the definition of $W_s$ and $L_s$. $\square$

The historical starvation and ideal-feedback rescue measurements are archived offline outside this minimal package. They do not establish a service-gap guarantee for JLC-R.

**Theorem 1 (Conditional serial service sufficiency).** *Consider one round after base tasks, with a fixed decreasing-rank routing tree, finite unexpired packets, truthful available caches, successful first decoding attempts and no receiver overflow. For sensor $i$, let $a_i^{in},a_i^{out}$ count incoming and outgoing packets in the prescribed schedule. Let $R_i$ sum reception, processing and receiver-control costs. Let $\overline C_i(p)$ be the larger of the prescribed outgoing control-plus-data cost and reference hold for packet $p$. Assume residual guard capacity is at least $a_i^{in}+a_i^{out}$. Residual credit and battery above reserve must each cover $R_i+\sum_p\overline C_i(p)$, with an action cap of at least $a_i^{out}$. For JLC-R, assume additionally that every prescribed member admission passes the pre-response transit checks in Section 4.3. If the conservative logical serialization envelope fits the macro-round, a member-first, decreasing-rank serial schedule can deliver every prescribed packet while respecting reservations.*

*Proof.* The proof is given in the proofs below. In outline, process members first, followed by tree vertices in decreasing rank, so each vertex receives all its upstream packets before its forwarding turn; the assumed budgets cover its remaining receptions and every packet's outgoing cost or larger reference hold, and induction along the finite tree completes delivery. $\square$

These sufficient conditions connect energy and capacity to an executable *abstract serial* service schedule. They exceed the conditions guaranteed by JLC-R, so the theorem does not establish greedy-routing success or synchronized radio operation. Conversely, any prescribed successful schedule requires at least $a_i^{in}+a_i^{out}$ guards and its actual per-node communication energy. Neither type of resource shortage can be overcome by reservations alone. Unconditional liveness fails, for example, when a held packet has zero free credit, an unavailable reference receiver and only more expensive alternatives. It can also fail when the single-choice loop leaves a cheaper affordable alternative untried. Harvest below every planned scenario may invalidate the next base plan. Present feasibility therefore does not imply recursive feasibility, and queue bounds enforced through expiry do not establish throughput stability or bounded steady-state AoI.

**Corollary 1 (First-attempt probability on a prescribed schedule).** If Theorem 1's deterministic initial resource and queue conditions hold and its $L$ prescribed decoding outcomes are independent Bernoulli trials, its all-first-success event has probability $\prod_{\ell=1}^{L}p_{e_\ell}$. Hence successful completion has conditional probability at least that product, bounded below by $p_{min}^{L}$. For a two-hop path with $p_{min}=0.72$, the value is 0.5184. This conditional bound excludes random weather and the executed greedy route; the one-attempt reservation cannot claim a three-retry bound without reserving all retry resources.

**Proofs and resource transitions.**

**Proof of Lemma 1.** *Monotone recursion and the interval.* For a fixed listening intensity $a$ and $x_1\le x_2$, we have $b(h)+w_hx_1\le b(h)+w_hx_2$ with $w_h=1/T_L$ for $h<T_L$ and zero otherwise. The capacity-clipped battery update is nondecreasing in the entering battery and nonincreasing in expenditure. Induction over $h$ gives $\widetilde B^m(h;x_2)\le\widetilde B^m(h;x_1)$ in every scenario. Subtracting the same expenditure preserves the ordering, making each prefix margin continuous and nonincreasing in $x$. When zero is feasible, their finite intersection on the compact box $[0,B_{max}]$ is a downward-closed interval $[0,x_\epsilon^*]$. Bisection preserves a feasible lower endpoint and an upper endpoint containing the supremum, halving their distance at each step, so the returned lower endpoint satisfies $0\le x_\epsilon^*-L_I\le B_{max}2^{-I}$. If zero is infeasible, returning zero is a fallback without a feasibility certificate.

*Battery invariance and scenario feasibility.* Under the exact-arithmetic affordability guard $E_i(t)\le B_i(t)$, every expenditure is affordable, harvest is nonnegative and (4) clips the resulting battery at $B_{max}$; induction gives $0\le B_i(t)\le B_{max}$ at every round. The bisection test checks every $(m,h)$ pair in (14), so every admitted feasible credit satisfies all scenario prefix reserve constraints; replacing the margin by $B_{reserve}-\epsilon_{num}$ yields the stated numerical condition on the planned scenarios, leaving future physical harvests uncertain.

*Non-overcommitment at serialized boundaries.* Under A1, both reservation sets are initially empty, and payments by unreserved traffic exclude all existing obligations. A reserved sample may spend its own hold but cannot spend another sample's resources. Before any payment, the sender performs the complete control-plus-data affordability check. A sender request reduces credit and battery, consumes its held guard if available, and reduces its own energy hold by the covered fee, leaving every remaining obligation to other samples affordable. If admission is denied, all charges persist without creating a new receiver obligation. Data transmission releases the old residual hold, and failed decoding creates no new hold. After successful reception, the post-control admission check covers immediate reception, processing and the new forwarding hold, leaving one unused guard for that hold. A receiver queue overflow prevents the installation of any new forwarding reservation. Round-boundary clearing only removes obligations. Induction over transitions therefore keeps $E_j^{res}\le\max\{0,\min\{c_j,B_j-B_{reserve}\}\}$ and $|\mathcal S_j(t)|\le k_j$ invariant; the positive part accommodates an empty hold set when affordable base expenditure leaves the battery below the communication reserve. Intermediate program statements are not admission boundaries at which concurrent requests can be accepted.

*Partition and energy ledger.* Every offered sample reaches exactly one terminal state (delivered, expired, overflowed) or remains queued at the horizon; the terminal sets are disjoint, giving the demand identity. Each physical debit enters exactly one of the disjoint base, data and control ledgers before the capacity clipping in (4); telescoping the recursion from $B_i(0)$ to $B_i(T)$ gives the stated ledger identity, with capacity-limit spill recorded separately.

*Tolerances.* Numerical execution accepts prefix margins down to $-\epsilon_{num}$ with $\epsilon_{num}=10^{-10}$ J; reservation audits use $10^{-8}$ J and physical-balance checks $10^{-6}$ J. These two-to-six-order separations are not interchangeable physical safety margins and cannot authorize borrowing energy, and the finite-precision bounds above concern the fixed-input scalar optimum rather than network freshness. $\square$

**Proof of Theorem 1.** Process members first, followed by tree vertices in decreasing rank. Each vertex receives all its upstream packets before its forwarding turn. The assumed budgets cover its remaining receptions and every packet's outgoing cost or larger reference hold. Payments remove the corresponding scheduled work, while existing holds cover a subset of remaining outgoing work. Each additional reception therefore has enough uncommitted energy and both current and subsequent guard transactions. The additional V63 assumption ensures that protected member admissions are not rejected before the response. Every granted packet decodes, fits the receiver queue and is forwarded during that receiver's later turn. Induction along the finite tree completes delivery, with each vertex performing at most its prescribed outgoing count. No step uses resources beyond the stated residual guard capacity and credit. $\square$

Table S69. Reservation state transitions.

| Transition | Existing obligation | New receiver obligation |
|---|---|---|
| Wait before request | Retained | None |
| Charged request, no response | Own guard consumed; own energy reduced by fee | None |
| Charged response, denied | Same; receiver response also charged | None |
| Granted data, decoding failure | Residual sender hold released | None |
| Successful data, queue overflow | Residual sender hold released | None |
| Successful queued reception | Residual sender hold released | Reference one-hop energy and one guard |
| Delivery to sink | Sender hold released; data charged | None |
| Round boundary | All remaining holds released | None; packet stays queued |

**Table note.** Charged energy and consumed guard transactions remain charged in every outcome.

# Part III. Supplemental relay-protection factorial study

This new study was specified after the original confirmation. Its 864 planned cases are complete: 768 for four weather inputs and two supplies, and 96 for the inherited T2/1.0 Stage III-C3 canopy condition. The original 480 records, WP0--WP6 evidence and original Holm-36 decisions remain unchanged. Twelve registered seeds, 210101--211212 in steps of 101, are paired across all nine conditions and eight configurations. The four development seeds are separate. The seed-use audit is bounded to the searched repository, retained archives and reachable source history; it makes no claim about unrecorded work elsewhere.

T, R and S respectively enable the exact pre-response transit check, the planned-Guard-below-two CH demand term, and the local-staleness key before the historical birth/sequence fallback. All-off matches the actual frozen Hybrid control and all-on matches frozen JLC-R. Six full fourteen-day endpoint comparisons (three reference conditions for each endpoint) reproduce every common scalar, fourteen execution arrays, all round logs and final queues/holds exactly; five retained published metrics also have zero difference. No floating-point waiver was used. All eight combinations pass observer-neutrality and safety tests.

The primary seed-level effect averages T1/0.7 and T3/0.7 equally before inference. H1 is the bundle effect on far coverage; H2 is the T marginal effect on far coverage; H3 is the R marginal effect on overall coverage; H4 is the S marginal effect on Source P5. There are twelve independent network-seed differences and eleven degrees of freedom, not twenty-four independent weather runs or thousands of packet replicates. All differences below are percentage points, intervals are nominal two-sided 95% paired Student intervals, and Holm correction applies only to this new four-test family.

\begin{table}[H]
\centering\small
\caption*{Relay-factorial primary comparisons (separate Holm-4 family).}
\begin{tabular}{lrrrrr}
\toprule
Test & Difference & 95\% CI & $t_{11}$ & Two-sided $p$ & Holm $p$ \\
\midrule
H1 & +0.1920 & [+0.1275, +0.2565] & 6.5516 & 4.12672e-05 & 0.000165069 \\
H2 & -0.0028 & [-0.0126, +0.0071] & -0.6198 & 0.548023 & 0.548023 \\
H3 & +0.0516 & [-0.0044, +0.1076] & 2.0296 & 0.0672962 & 0.134592 \\
H4 & +0.2067 & [+0.1247, +0.2888] & 5.5441 & 0.000174295 & 0.000522885 \\
\bottomrule
\end{tabular}
\end{table}

Bundle far-coverage and S/P5 effects are positive for all twelve seeds. Exhaustive 4096-pattern sign-flip sensitivity gives 0.000488 for each, assuming independent symmetric seed contrasts under the null. Their leave-one-seed-out means remain positive. T and R do not pass the primary family; nonsignificance is not equivalence. Their exact direction counts, all statistics and sensitivity values are retained in `results/primary_tests.csv` and `results/primary_seed_effects.csv` in the study directory.

The complete nine-condition report retains all eight absolute configurations, T/R/S marginal effects, three pairwise interactions, the three-way difference, the bundle and three full-background differences. The latter must not be substituted for marginal effects. Secondary outcomes and interactions use descriptive effects and nominal intervals, with no upgrade to primary status. The original G10 budget/locking experiments and S200/G20 relay factorial test different decisions under different physical timings and are not pooled.

Mechanism counts distinguish request-path calls from paid requests, pre-response from post-response refusals, and local queue choices from diagnostic read-only peeks. Among A111's primary winter executions, T refuses 37,070 of 471,652 paid member requests; 121 refusals have zero positive transit margin. R makes 38,406 low-Guard-only reactive choices, of which 21,189 install at least two Guards. S changes 56,133 of 251,982 eligible tied selections. These opportunity counts do not increase independent sample size or guarantee service. Guard installation precedes online affordability and decoding checks. Committed-hop success is not an end-to-end delivery guarantee. The derived mechanism audit cross-checks native commitment, completed-hop, reactive and boundary-release counts against the observer and audits all 3,483,648 CH credit-period records.

T is an admission margin, not an extra physical hold. Its positive binary Guard threshold matches ordinary receive-plus-forward safety; its intervention includes the energy/credit margin and refusal timing. Unused-resource counts refer to actual one-hop commitments, not an invented T reservation. Loss-event categories may contain repeated blocks of a packet; distinct far-source expiry-at-relay counts are separate. Zero-denominator rates remain missing, and incomplete rate sets are not silently used for twelve-seed intervals. Far-source coverage uses its own source-time denominator; Source P5 uses all 100 sources.

The inherited canopy mapping follows the executed WP4 code: $T_i=T_{min}+(T_{max}-T_{min})c_i$, while decoding probability decreases with the same spatial index. All 3600 retained node-stage energy records match this expression exactly. The earlier prose direction is corrected; the frozen code and every earlier result remain byte-identical. This reduced-form field is not a calibrated model of co-located monotone shading and radio attenuation. New canopy contrasts use the new seed cohort and remain separate from the original 384-run canopy panel.

The implementation/input/plan freeze is identified by the independent execution snapshot commit `d78291cd421638ccf8db9a7cdb79d493c3d4c0f9`. Its 47 source/input/plan payloads are retained byte for byte in `code/experiments/v6_5_relay_ablation/audit/execution_sources.zip`; `audit/source_snapshot_provenance.json` records the original container hash, the new public-container hash and all member hashes. Only embedded Git metadata was omitted from the public container; the original ZIP is preserved offline. Delivery-only formatting/audit corrections are recorded separately; no execution decision, input, seed or primary statistical rule was changed. The final audit verifies all 864 successful raw records, no failed cases, zero Guard/reservation violations and a maximum physical energy-ledger residual of $4.54\times10^{-8}$ J, below the unchanged $10^{-6}$ J tolerance.

The minimal study is in `code/experiments/v6_5_relay_ablation/`: configuration and statistical plan in `configs/`; all 864 seed-level outcome and mechanism-count records, paired effects and primary tests in `results/`; and the source freeze, seed-use and equivalence records in `audit/`. Full per-round/per-packet raw logs and intermediate manuscript drafts are archived offline. The explicit rerun mode can generate new execution logs into a new directory. Existing scientific records and the sole public JLC-R entry remain unchanged.



# Part IV. Extended evidence for the compressed article

Notes E1/E2 retain the detailed pre-compression protocol and implementation descriptions. Their internal numbered section references use that description's original numbering; current main sections are 2 (model), 3 (method), 4 (design) and 5 (results). All equation numbers 1--20 remain unchanged. Extended E1--E8 below preserve the complete numerical displays.

## Note E1. Complete execution and study protocols

# 5 Experimental Design and Evaluation

## 5.1 Monitoring Scenario and Common Physical Conditions

The evaluation models 100 sensors on a perturbed $10\times 10$ grid over $300\text{ m}\times 300\text{ m}$, with 12 active CHs and a boundary sink. Each simulation spans 14 scored days (following a 2-day forecast warm-up) with a 900-s (15-min) sampling interval and a four-round (60-min) freshness target. The 15-min sampling cadence lies within established agricultural telemetry practices, which range from 1-min updates in high-frequency plasticulture drip irrigation [@sat_tomato2022] to hourly reporting in low-power pasture and orchard monitoring [@horticulture_wsn2009; @sat_node2026]. We evaluate a fifteen-minute sampling interval and a sixty-minute freshness criterion as a specified monitoring workload. Soil matric potential thresholds of $-40$ to $-60$ kPa [@sat_tomato2022] govern irrigation trigger decisions rather than directly specifying a maximum acceptable data latency. The 4000-bit logical payload represents an unaggregated multi-parameter sensing record containing soil-profile, microclimate, timestamp and node-identification fields; Table 1 gives the physical and execution parameters of the primary S200/G20 confirmation. No field deployment, field calibration or agronomic endpoint was available for this study; every reported result is a simulation.

Four solar-input environments are crossed with supply multipliers 1.0 and 0.7. Synthetic input contains a specified reduced-supply episode. Measured NOAA SURFRAD records comprise Table Mountain winter (T1, 1--17 January 2024), Table Mountain spring (T2, 1--17 April 2024) and Bondville winter (T3, 1--17 January 2024), each with two initialization days, fourteen evaluation days and a forecast-tail day [@surfrad2024]. Bondville lies in an agricultural region of the US Midwest, while Table Mountain provides a high-desert reference site, so the measured trajectories span contrasting supply environments. These are measured irradiance inputs to modeled harvesting and a synthetic network, not field-network experiments. Conversion is $H_i=s\phi_i(0.12)(\overline G_{GHI}/1000)$ J/round. Flagged GHI minutes are reconstructed only from quality-valid direct and diffuse components using solar zenith; remaining interior gaps of at most five minutes are linearly interpolated, while larger or edge gaps fail. Negative irradiance is clamped before 15-minute averaging. Times use local standard time without daylight-saving shifts (UTC-7 at Table Mountain and UTC-6 at Bondville). The three measured records are three weather trajectories, regardless of the number of network seeds.

All primary comparisons use S200/G20: five 20-ms synchronization windows at 0, 200, 400, 600 and 800 s per round. Nodes must pay every necessary window before traffic and a fresh neighbor cache are authorized. The first window is included in scheduled listening, with four additional charges in both planning and execution. Relative clock drift at 20 ppm per endpoint contributes at most 8 ms over 200 s; link-relative jitter contributes 8 ms and turnaround/detection 1 ms, giving a modeled 17-ms budget within the 20-ms guard. Traffic retains the common late-round serialized endpoint-airtime check. 

Geometry, role schedules, weather, forecast banks and keyed decoding events are shared within seed-matched comparisons. All methods use identical sensing, listening, request, response, data, reserve and hold costs. No controller receives free synchronization, receiver access or knowledge of future weather or decoding outcomes.



## 5.2 Service Outcomes

Let $v_i(t)$ denote the latest birth round among source $i$'s samples delivered by the end of round $t$, with $v_i(t)=-1$ before its first delivery. We define the finite-horizon end-of-round age by the piecewise expression

$$
A_i(t)=
\begin{cases}
[t-v_i(t)+1]\Delta t, & v_i(t)\ge 0,\\
(t+1)\Delta t, & v_i(t)=-1.
\end{cases}
$$

A source contributes to fresh-source coverage only after a sample has been delivered and its age is at most $D\Delta t$. This initialization defines a finite-horizon metric without implying steady-state AoI. Fresh-source coverage over $T$ rounds is

$$
C_{fresh}=\frac{100}{NT}\sum_{t=0}^{T-1}\sum_{i=1}^{N}\mathbf1\{v_i(t)\ge0,\ A_i(t)\le D\Delta t\}. \qquad (19)
$$

Here $D=4$ (60 min) matches both the freshness criterion and the four-round packet-expiry deadline; soil monitoring and irrigation applications span hour-to-day reporting intervals [@agri_ml2022; @agri_iot2024], and adapting the controller to wider agronomic reporting windows (e.g., 2--4 h) requires scaling both the expiry deadline and the planning horizon accordingly. Coverage measures source information freshness rather than geographic sensing area or packet delivery ratio.

Source P5 aggregates in two stages: within each run, source $i$'s fresh-time proportion is $c_i=(100/T)\sum_t\mathbf1\{v_i(t)\ge0,\;A_i(t)\le D\Delta t\}$; Source P5 is the 0.05 quantile of the $N$ values $c_i$ (NumPy default linear interpolation). Run-level P5 values are then averaged or differenced across seeds.

Nighttime outage is the fraction of node-rounds in which a node is off while $g(t)=0$. Total energy consumption includes actual base, data and control expenditure across all battery-powered nodes. Mean AoI is calculated by averaging over all sources and evaluation rounds. Coverage and mean AoI weight the age distribution differently, so their policy rankings can differ. The accounting also records generated demand, delivery, unsampled demand, overflow, expiry and packets remaining in transit at termination.

## 5.3 Comparators and Mechanism Evidence

The primary independent confirmation evaluates five complete configurations under identical S200/G20 physical accounting:

1. **JLC-R**: the complete proposed controller combining integer-slot prefix planning, locally gated PADC reactive fallback, local-age scheduling and the three-part relay-protection module (pre-response CH transit protection, two-slot CH relay-demand recognition and uncovered-staleness tie-breaking).
2. **Prefix-only**: JLC-R with the PADC reactive branch and the relay-protection module disabled, isolating pure long-horizon integer prefix planning and local-age scheduling.
3. **Hybrid control**: the hybrid prefix/PADC controller without the relay-protection module, isolating the net effect of relay protection.
4. **PADC-AGE**: a recent-control adapter transferring the published PADC duty-cycle law [@padc2023] and nonbinding permission semantics to the common charged executor, paired with JLC-R's local-age packet selector.
5. **PADC+relay**: a diagnostic transfer equipping **PADC-AGE** with the JLC-R relay-protection module to test whether relay protection generalizes across duty-cycle rules.

For PADC-AGE, let $r=(B+P)/B_{max}$, where $P$ is the causal four-round point prediction and $E_c$ is common full-reference base-plus-traffic expenditure. Its duty is one when $r\ge0.5$, or when $r\ge0.3$ and $P\ge E_c$; otherwise it is $r/0.9$ for $0.1\le r<0.5$ and 0.05 below 0.1 [@padc2023]. This rule maps duty $d$ to $L=L_{sync}+d(L_{ref}-L_{sync})$ and paid integer capacity; communication permission is nonbinding, while live battery, reserve and holds constrain every action. The transferred rule uses the common solar input and predictor, and does not reproduce the original protocol's complete MAC implementation.

**External-baseline scope.** PADC-AGE is the external duty-rule baseline in the common S200/G20 executor. HENO-MAC uses a receiver-initiated solar--wind star MAC with priority classes and p-persistent CSMA [@heno2024]; its duty rule is retained as HENO-DC in the separate G10 study. MAoIG uses estimated harvesting rates to coordinate energy-adaptive paths, per-cycle forwarding trees, update generation and interference-constrained transmission schedules [@chen2022maoig]. The present evaluation fixes roles and sampling demand and charges discrete Guard transactions, so a full MAoIG comparison requires a different execution model. The repository's external-baseline audit documents these mappings.

Joint-versus-fixed listening and reference-floor controls use twelve paired seeds under the original base synchronization and G10 Guard configuration (Section 6.2). The separate S200/G20 factorial evaluates relay decisions within the hybrid controller (Section 6.3).



## 5.4 Independent Confirmation and Statistical Analysis

Twelve evaluation seeds, $160101+101k$ for $k=0,\ldots,11$, cross five methods and eight weather--supply cells, giving 480 executions. They are distinct from the controller-development cohorts. The primary hypotheses, noninferiority margins and multiplicity adjustment were specified before these runs. The prespecified regime-matched comparators are Prefix-only for Synthetic and T2, and PADC-AGE for T1 and T3; Table 2 retains all five controllers and their metric-specific tradeoffs.

The seed is the independent pairing unit. Nodes, packets, rounds and repeated conditions within seed are not independent replications. For matched differences $d_s$, nominal paired 95% intervals are

$$
\bar d\ \pm\ t_{0.975,n-1}\frac{s_d}{\sqrt n},\qquad \bar d=\frac1n\sum_{s=1}^{n}d_s,\quad s_d^2=\frac1{n-1}\sum_{s=1}^{n}(d_s-\bar d)^2. \qquad (20)
$$

The primary family contains 32 one-sided noninferiority tests (eight cells by four outcomes) and four winter coverage-improvement tests against Prefix-only. Margins are -1 pp for coverage/P5, +1 pp for nighttime outage and +5% of baseline mean AoI. Holm adjustment covers all 36 tests at $\alpha=0.05$. At T2 and $s=1.0$, both matched controllers have zero nighttime outage in every seed, satisfying the margin deterministically; including this tie or using the 35 evaluable tests gives the same decisions and maximum adjusted $p=0.03711$. Nominal two-sided intervals describe uncertainty separately from the one-sided decisions. A relative-AoI sensitivity uses $1.05\times$baseline$-$candidate in a separate 33-test family and retains all 32 NI decisions. Paired $t$ inference assumes independent seeds and an adequate small-sample approximation.

Primary inference uses only this twelve-seed cohort. Each execution checks demand conservation, battery nonnegativity and hold/guard invariants. Detailed seed registries and resource-invariant verification results are included in the reproducibility repository.

## 5.5 Agricultural Extension Experiments

The following analyses examine sensitivity to solar supply, freshness criteria and spatial energy--link heterogeneity. They are exploratory extensions of the independently confirmed controller, using the same physical kernel, 100-node network and S200/G20 timing. Their nominal paired intervals are separate from the primary confirmation family.



**Winter supply response.** T1 and T3 winter inputs cross six supply multipliers from 0.7 to 3.0, four controllers and twelve new seeds $170101+101k$, $k=0,\ldots,11$, giving 576 executions. JLC-R, Prefix-only, Hybrid control and PADC-AGE retain Table 1 parameters; PADC+relay remains a diagnostic in the confirmation. The multiplier changes physical harvest and its causal forecast together, while routing, thresholds, expiry and the 60-min freshness criterion remain fixed. Outcomes include service, consumed/harvested/spilled energy, battery trajectories, mode activation and prefix infeasibility. First- and second-half service and storage distinguish initial-battery support from sustained operation. These new seeds keep the sweep separate from Table 2.

**Freshness-window sensitivity.** A read-only observer scores each source in the 480 confirmation trajectories at $D\in\{2,4,8,16\}$ rounds (30, 60, 120 and 240 min). Generation, routing, listening, synchronization, energy expenditure and four-round packet expiry remain fixed. The $D=4$ recomputation reproduces coverage and Source P5 to $10^{-9}$. Changing this scoring criterion therefore tests freshness sensitivity without changing the sampling load or saving energy.

**Spatial energy--link stress test.** T2 at $s=1.0$ crosses twelve new seeds $190101+101k$, four controllers and eight treatments, giving 384 executions. A seeded plane-wave field over node positions provides a shared smooth index $c_i\in[0,1]$. Energy transmittance is $T_i=T_{min}+(T_{max}-T_{min})c_i$; decoding is $p_{ij}=p_{ij}^{0}[1-\lambda(c_i+c_j)/2]$, clipped to the valid range without changing adjacency. The index therefore raises transmittance while lowering decoding: a spatial heterogeneity stress, not a physical canopy-density law. Stage I uses $T\in[0.85,1.00]$, $\lambda=0$; Stage II uses $T\in[0.70,0.90]$, $\lambda=0.10$; Stage III uses $T\in[0.50,0.80]$, $\lambda=0.20$. C1 applies energy reduction, C2 link attenuation and C3 both, with fields and keyed decoding shared within seed. Vegetation propagation motivates link sensitivity [@itu_vegetation2021], but these values are not fitted crop or radio parameters.

**Reporting.** Extension results use seed-paired means and nominal two-sided 95% $t$ intervals; no new multiplicity-adjusted family is declared. New cohorts do not overlap the confirmation, and all specified seeds are retained. The 70% and 80% coverage lines are candidate engineering references, not universal agronomic standards.

## 5.6 Three-Factor Relay-Protection Ablation

The S200/G20 mechanism study crosses pre-response CH transit protection ($T$), two-slot CH demand recognition ($R$), and sender-local staleness ordering ($S$) in eight configurations, $(T,R,S)\in\{0,1\}^3$. All-on is JLC-R and all-off is Hybrid control. Disabling T removes its additional pre-response margin while retaining ordinary charged admission, forwarding affordability and the forwarding Guard. Disabling R removes the planned-Guard-below-two demand term, retaining queue demand and 0.60/0.70 hysteresis. Disabling S removes staleness from the priority key while retaining committed-first selection, uncovered demand, freshness gain, birth time and sequence order.

Twelve seeds, $210101+101k$ for $k=0,\ldots,11$, are distinct from the confirmation and agricultural-extension cohorts; four separate development seeds serve execution checks. Eight configurations across four inputs and two supplies give 768 executions. A further 96 use the Stage III-C3 spatial-stress treatment at T2 and $s=1.0$. All retain Table 1 parameters, fourteen scored days and the forecast warm-up. Outcomes and the analysis plan were fixed before execution.

For outcome $Y$, the $T$ main effect is $\frac14\sum_{r,s}[Y(1,r,s)-Y(0,r,s)]$, with analogous definitions for $R$ and $S$. Pairwise interactions are differences of these on-minus-off differences, averaged over the remaining factor; the third-order interaction is the full third difference. The bundle contrast is $Y(1,1,1)-Y(0,0,0)$. Full-background losses, such as $Y(1,1,1)-Y(0,1,1)$, are reported separately from marginal effects. Four primary contrasts are fixed for this new study: bundle and $T$ effects on far-source fresh coverage, the $R$ effect on overall coverage, and the $S$ effect on Source P5. Each seed's contrast is first averaged equally over T1 and T3 at $s=0.7$, yielding twelve independent paired effects. Two-sided paired $t$ inference uses 11 degrees of freedom, nominal 95% confidence intervals and a separate four-test Holm family at $\alpha=0.05$. This post-confirmation plan does not modify the original 36-test family or its noninferiority margins. Other cells, spatial-stress treatments, interactions and remaining outcomes are secondary descriptive analyses. Leave-one-seed-out means, effect-direction counts and exhaustive seed-level sign flips assess sensitivity; the sign-flip calculation assumes independent, symmetric seed contrasts under the null. A nonsignificant contrast is not an equivalence finding.

Far-source outcomes use sources at least 200 m from the sink and their own source--time denominator. Read-only mechanism logs distinguish paid requests, pre-response and post-response refusals, successful receptions, committed forwarding, unused actual holds, low-Guard demand recognition and effective queue ties. Staleness activation and actual changes to the selected packet are counted separately, excluding diagnostic read-only peeks. Request refusals use their corresponding request denominators; forwarding completion uses created commitments, and sorting changes use eligible ties. Hop-loss diagnostics count repeated events and are distinguished from unique expired samples.

## Note E2. Detailed planning and execution contracts

# 3 Network, Harvesting, and Cost Models

## 3.1 Network and Time Model

To separate resource coordination from site-specific hardware, we model a 300 m $\times$ 300 m multi-hop agricultural monitoring network. Individual source identities allow service to be evaluated separately for observation locations. The boundary sink represents a field gateway position. The 15-minute reporting interval and one-hour freshness target are controlled service requirements anchored in Section 5 to published agricultural telemetry practice.

The target setting is coordinated periodic collection with individually attributable observations, fixed role schedules and the serialized service abstraction specified in Assumption A1. Listening expenditure and relay commitments share each node's finite energy and transaction resources.

Consider a network $G=(V,E)$ containing $N$ homogeneous sensors and a sink with stable external power. Two nodes have a candidate undirected link when their distance is at most $R_{comm}$. Forwarding follows decreasing sink-cost ranks, with the active direction determined by current node roles. Cluster members transmit to reachable neighboring cluster heads (CHs), which process each received packet before forwarding it to another CH or the sink. Per-packet processing preserves every source identifier and birth time. We denote its cost by $E_{proc}$ (per-bit constant $E_{proc,unit}$). No packet-count reduction or LEACH-style data compression is performed: the model forwards individually attributable raw readings.

The modeled network comprises 12 geographic cells, each with a rotation set formed by the five nodes nearest its center. These nodes become CHs in a predetermined order, and members associate with reachable CHs in the current phase. The schedule is exogenous, with no optimization of CH selection. If a proposed phase has no feasible CH backbone, the simulator substitutes the first candidate from every cell. Network construction fails if the replacement backbone is also infeasible. These fallback phases are configured before execution and shared identically across all compared methods (occurring in 7 of the 60 seed--phase configurations, or 11.7%, in the twelve-seed confirmation cohort), and can slightly reduce the number of distinct sources observed as CHs. Each macro-round lasts $\Delta t=900$ s and contains a scheduled traffic opportunity. The credit period is $T_L=4$ rounds, and the forecast horizon is $H=96$ rounds. Base-task and communication costs are charged before energy is harvested at the round's end.

Each source generates one sampling demand per macro-round, with a logical packet size of $l=4000$ bits and a four-round deadline. A demand that cannot be sensed is recorded as unsampled and remains in the accounting denominator, preserving offered demand during sleep or outage. Sampled packets retain their source identifiers and birth rounds, and the ledger separately records queue overflow and deadline expiry.

Let $d_{ij}$ be the Euclidean distance between nodes $i$ and $j$. For a candidate link satisfying $d_{ij}\le R_{comm}$, the logical-packet decoding probability depends on distance as follows:

$$
p_{ij}=0.97-0.25\left(\frac{d_{ij}}{R_{comm}}\right)^2. \qquad (1)
$$

Equation (1) provides a reproducible, distance-ordered link degradation profile over $p_{ij}\in[0.72,0.97]$; it isolates geometry-dependent relay bottlenecks under controlled channel realizations rather than site-specific foliage multipath, and models neither vegetation attenuation, collisions nor the physical layer. A separately configured extension, used only in the spatial energy--link stress test of Section 5.5, uses a common spatial index for solar transmittance and decoding stress; the primary confirmation uses (1) unchanged. Each packet has at most three decoding attempts on its current hop per round, with the counter reset after a successful hop change. Outcomes are keyed by seed, round, link, sample identifier and attempt index, so policy-dependent random-number consumption cannot change the exogenous channel.



## 3.2 Solar Input and Battery Dynamics

The 4000-bit logical packet is a source-attributed monitoring payload carrying soil and microclimate measurements with identifiers, timestamps and metadata. The distance-dependent decoding probability is a controlled communication abstraction.

Let $u(t)$ denote the hour of day at round $t$, giving the synthetic daylight component

$$
g(t)=\begin{cases}\sin\!\left(\pi[u(t)-6]/12\right),&6\le u(t)<18,\\0,&\text{otherwise}.\end{cases} \qquad (2)
$$

The harvested energy is

$$
H_i(t)=s\,\phi_iH_{peak}g(t)w(t). \qquad (3)
$$

Here $s\in\{1,0.7\}$ is the supply multiplier, $\phi_i\sim U[0.7,1]$ is a fixed local-shading factor, and $H_{peak}=0.12$ J/round. The shared weather state changes daily, with clear-to-clear and cloudy-to-clear probabilities of 0.80 and 0.45, respectively. Clear and cloudy states have means of 1 and 0.4. Correlated fluctuations use a coefficient of 0.85 and an innovation standard deviation of 0.035; weather factors are clipped to [0.05,1.15]. On zero-indexed days 5, 6 and 7, the mean is fixed at 0.22 to impose a sustained low-supply period. Physical weather and metering noise are generated from independent random streams.

Given node $i$'s round expenditure $E_i(t)$, the battery state evolves according to

$$
B_i(t+1)=\min\{B_{max},B_i(t)-E_i(t)+H_i(t)\}. \qquad (4)
$$

Every physical debit must be affordable, so $B_i(t)-E_i(t)<0$ is prohibited; energy spilled at the capacity limit is recorded separately. The 0.08 J restart threshold is subordinate to current-task affordability: a node restarts only when its battery exceeds both values. The communication reserve $B_{reserve}$ applies differently to communication and base tasks. Communication, charged control exchanges and forwarding reservations must respect the reserve, whereas listening, sensing and existing broadcasts require only immediate affordability. The reserve therefore governs planned service and admission, while base-task execution can reduce the physical battery below it.

Each node retains a fixed shading factor $\phi_i$, and days 5--7 impose a multi-day supply reduction. Storage ($B_{max}=4$ J) and peak harvest ($H_{peak}=0.12$ J/round) define a normalized energy-to-workload model rather than a particular commercial battery or panel. Agricultural platforms use different storage and photovoltaic configurations [@sat_tomato2022; @sat_sugarcane2026; @sat_solar2025]. The 56-mW idle-listening cost is a model input; the 52--53 mA measurement in [@sat_node2026] concerns transmit bursts.

The supply multiplier scales physical harvest and its causal forecast together and cannot be directly converted to panel area. The 3-J initial battery supports transient operation during supply deficits. Common-scaling assumptions, numerical tolerances and deficit-scale calculations are documented in the reproducibility repository.

## 3.3 Data and Control Energy

We adopt a first-order logical-packet energy model consistent with classical clustered-network analysis [@leach2002], including the implementation's 5% transmit-electronics overhead:

$$
E_{Tx}(l,d)=\begin{cases}l(1.05E_{elec}+\varepsilon_{fs}d^2),&d<d_0,\\l(1.05E_{elec}+\varepsilon_{mp}d^4),&d\ge d_0,\end{cases}\quad d_0=\sqrt{\varepsilon_{fs}/\varepsilon_{mp}}. \qquad (5)
$$

Reception, sensing and processing after successful reception incur the following costs:

$$
E_{Rx}=lE_{elec},\quad E_{sense}=lE_{sense,unit},\quad E_{proc}=lE_{proc,unit}. \qquad (6)
$$

Failed decoding incurs affordable transmission and reception costs, with per-packet processing charged only after successful reception. A blind transmission toward an unavailable receiver also retains its charged transmission cost.

Reservation-enabled methods exchange requests and responses, each carrying a logical payload of $l_c=64$ bits. Their sender-side and receiver-side control charges are

$$
F_{ij}^{send}=\frac{l_c}{l}E_{Tx}(l,d_{ij})+l_cE_{elec},\quad F_{ij}^{recv}=\frac{l_c}{l}E_{Tx}(l,d_{ji})+l_cE_{elec}. \qquad (7)
$$

The sender prepays the full exchange and receives no refund when the receiver is offline or fails to respond. The receiver incurs its charge only when a response is affordable. This timeout-cost approximation abstracts the exchange without simulating individual transceiver states. Each control charge reduces both physical battery energy and current communication credit and is recorded once in a separate control ledger. A direct sink transmission bypasses this authorization because the exchange is intersensor.

## 3.4 Finite Listening and Guard Capacity

Let $\tau_i$ denote prepaid synchronization, waiting and guard-listening time per round, with a 20-ms synchronization window and a $\tau_{guard}=20$ ms guard (G20). The resulting number of available guard transactions is

$$
K_i=\max\left\{0,\left\lfloor\frac{\tau_i-\tau_{sync}}{\tau_{guard}}\right\rfloor\right\}. \qquad (8)
$$

Each data attempt consumes one sender transaction and, when reception is possible, one receiver transaction. A node's $K_i$ capacity is shared between transmission and reception. In reservation-enabled methods, a request consumes a sender transaction even when rejected, and an affordable receiver response consumes a receiver transaction. Data sent after a grant reuse these transactions without a second slot debit.

The 250 kbps rate references a 2.4 GHz IEEE 802.15.4-class timing scale, and a 4000-bit logical observation corresponds to a long-frame physical layer such as IEEE 802.15.4g SUN-class links or a coded-PHY mode with a comparable payload budget. Guard time covers control exchange and listening, while data require additional airtime: at 250 kbps, a 4000-bit logical packet needs 16 ms beyond its guard interval. The implemented sequential time envelope is $\sum_{i\in\mathcal O_t}\tau_i+\sum_i u_i l/R_b\le\Delta t$, where $\mathcal O_t$ contains online nodes and $u_i$ counts consumed endpoint transactions. Since $\tau_i=\tau_{sync}+K_i\tau_{guard}+\rho_i$ with $0\le\rho_i<\tau_{guard}$, it includes synchronization, allocated guards and residual listening, with data airtime counted at both endpoints and even for charged denials. Listening costs $P_{idle}\tau_i$, with unused transactions retaining their prepaid cost, while data electronics and amplifier expenditure are charged separately under (5)--(6).

The scheduled listening caps are 100 ms for a member and 1000 ms for a CH, including the original 20 ms synchronization window. Additional synchronization windows are accounted for separately; these caps do not bound every radio wake-up during a macro-round. Holding the caps fixed at $\tau_{guard}=20$ ms (G20) gives maximum member and CH capacities of 4 and 49 transactions, respectively, and a typical member's two-guard reference demand corresponds to 60 ms of scheduled listening. Under continuous planning, $K_i=\lfloor a_iK_i^{ref}\rfloor$ can discard a fractional guard: $a_i=0.98$ and $K_i^{ref}=2$ pay for 59.2 ms of G20 listening but supply only one executable guard. Integer-slot planning retains a separate allocation mechanism; the continuous result is not rounded upward.

The capacity $K_i$ constrains service transactions within the serialized abstraction. The pairwise timing budget and clock assumptions are stated in Section 5.1.

# 4 Joint Listening-Credit and Reservation

JLC-R coordinates four local decisions: how much listening capacity to purchase, how much communication credit to release, which forwarding obligations to protect, and which queued observation to serve. A causal prefix planner and a PADC-based reactive branch share the same charged execution rules. Cluster-head transit protection, two-slot relay-demand recognition and sender-local source staleness form part of the controller throughout this section. The forecast horizon is 96 rounds, the credit period is four rounds, and the scenario bank contains four paths.

## 4.1 Causal Forecasts and Residual Scenarios

Forecasting uses gateway weather measurements and a fixed local-shading map. Let $Y_i(\tau)$ denote the observed harvest of node $i$ at completed round $\tau$. For rounds with daylight component $g(\tau)>0.1$, the normalized weather factor is the spatial median across nodes

$$
z_\tau=\operatorname{median}_{i=1,\ldots,N}\frac{Y_i(\tau)}{s\,\phi_i H_{peak}\,g(\tau)},\qquad g(\tau)>0.1.
$$

The median aggregates across nodes at each eligible completed daylight round; the EWMA below aggregates across time. In the simulator, this spatial median across de-shaded node observations extracts the common field-level weather fluctuation while suppressing single-node metering noise; in a physical field deployment, the powered edge gateway measures the unshaded irradiance factor $z_{t-1}$ locally using a co-located reference pyranometer or reference photovoltaic cell and broadcasts that scalar in the periodic synchronization beacon without consuming sensor uplink bandwidth. At round $t$, only observations from completed rounds $\tau\le t-1$ are used. The exponentially weighted moving average (EWMA) is

$$
m_t=\beta m_{t-1}+(1-\beta)z_{t-1},\quad\beta=0.7. \qquad (9)
$$

The estimator uses only completed-round observations and is not updated at night. At 06:15, the completed 06:00 observation is ignored because its daylight component is zero. At 06:45, the completed 06:30 observation can update the estimate because its component exceeds 0.1. The last eligible 17:30 observation updates the estimate at 17:45; that state is retained through the night until the next eligible morning observation. In the experiments, a two-day history initializes forecasting, with $m=0.65$ and a residual window containing at most 192 valid daylight observations.

Let $\xi_\tau=m_\tau-z_\tau$ be the one-step forecast residual observed in completed daylight rounds $\tau<t$. At issuance round $t$, the planner constructs $M=4$ supply scenarios for $h\in\{0,\ldots,H-1\}$:

$$
\widehat H_i^m(t+h\mid t)=s\,\phi_iH_{peak}\,g(t+h)\,\operatorname{clip}\!\left(m_t-\delta_h^{(m)},\,\underline{w}_m,\,1.15\right), \qquad m\in\{1,\ldots,M\}, \qquad (10)
$$

where $\delta_h^{(1)}=0$ with lower clip bound $\underline{w}_1=0.05$ defines the point forecast, and $\underline{w}_m=0$ applies to the three stress paths ($m\in\{2,3,4\}$). Specifically, $\delta_h^{(2)}$ and $\delta_h^{(3)}$ draw cyclic block samples from the 192-sample daylight residual window, while $\delta_h^{(4)}=Q_{0.9}(\xi)$ applies a one-sided correction at the empirical 0.9 residual quantile (with negative quantiles truncated to zero).

The four-path residual bank buffers multi-day low irradiance at $O(MH)$ cost without chance constraints. Positive residuals mark overprediction, so subtracting them lowers projected supply. The stress paths provide an optional conservatism buffer against sustained low input; they do not define a calibrated confidence set. The cell rotation, reference tree and shading factor $\phi_i$ are configured in advance and available locally.

Each sensor runs Algorithm 1 after receiving the gateway's past weather observation $z_{t-1}$ in the periodic synchronization beacon. Reception is covered by prepaid synchronization listening $\tau_{sync}$ and the per-period broadcast cost $E_{broadcast}$. Geometry, link probabilities, role schedules and expected-transmission-count (ETX) ranks are configured before execution. Each node obtains its own current battery and queue state locally. The powered gateway broadcasts its local past weather scalar $z_{t-1}$ through the periodic synchronization beacon, keeping those observations available to the causal forecast bank even during sensor outages. After an online node pays its fixed broadcast charge, its reported battery, credit and queue enter the common neighbor cache. Eligible senders read that cache, while charged requests reveal the receiver's current local feasibility. This ideal, reliable one-hop information service abstracts broadcast propagation; its fixed broadcast and synchronization charges represent the assumed expenditure.

## 4.2 Unified Listening, Capacity and Credit Planning

Reference traffic accumulates one sample per source per round along a fixed tree. Let $E_{ref}$ denote its directed edges in the current rotation phase, and $q_{ij}$ the expected logical-packet count on edge $(i,j)$. Reference decoding work is approximated by $q_{ij}/p_{ij}$, yielding node $i$'s expected transmit and receive attempts:

$$
\bar k_i=\sum_{j:(i,j)\in E_{ref}}\frac{q_{ij}}{p_{ij}}+\sum_{u:(u,i)\in E_{ref}}\frac{q_{ui}}{p_{ui}}.
$$

This planning approximation leaves the three-attempt limit unchanged during actual execution. The reference listening profile is

$$
\tau_i^{ref}=\min\{\tau_i^{fixed},\tau_{sync}+\lceil\eta\bar k_i\rceil\tau_{guard}\},\quad\eta=1.25. \qquad (11)
$$

Fixed listening caps are 0.1 s for members and 1 s for CHs, yielding at most 4 and 49 transactions at the 20-ms guard. Equation (11) couples reduced listening expenditure to reduced capacity under (8). Planning uses the configured role schedule, fixed demand and link probabilities, without requiring future queues or observed future weather. The $\bar k_i=0$ case is absent in the connected specified model: every sensor contributes its own unit demand to an outgoing reference edge, so $\bar k_i\ge1/p_{ir}\ge1$. With $\eta\ge1$, the specified caps leave positive $K_i$ (at least two at the default probabilities); offline execution can still set remaining transactions to zero.

The planning decision is a listening intensity $a_i\in[0,1]$ applied to the discretionary part of the reference profile, together with period communication credit $x_i$. For horizon step $h$, let $D_i(h)=L_i^{data}(t+h)+L_i^{grant}(t+h)$ denote the reference communication demand, with

$$
L_i^{data}(t+h)=\sum_{j}\frac{q_{ij}}{p_{ij}}E_{Tx}(l,d_{ij})+\sum_{u}\frac{q_{ui}}{p_{ui}}(E_{Rx}+E_{proc}),\quad
L_i^{grant}(t+h)=\sum_{j}\frac{q_{ij}}{p_{ij}}F_{ij}^{send}+\sum_{u}\frac{q_{ui}}{p_{ui}}F_{ui}^{recv}
$$

approximating reference data and control loads at step $t+h$. Expected attempt counts scale both terms. The data approximation includes reception and processing per expected attempt, whereas actual processing is charged only after successful decoding. The reference sender estimate includes a control allowance on sink edges even though execution bypasses that exchange. 

With role-dependent profiles, JLC-R purchases only whole guard transactions. Let $K_i^{ref}$ be the reference capacity from (8) and (11), and let $r_i$ denote the fraction of reference communication supported by the installed capacity:

$$
\begin{aligned}
K_i(h;a_i)&=\lfloor a_iK_i^{ref}(t+h)\rfloor,\\
r_i(h;a_i)&=\frac{K_i(h;a_i)}{\max\{1,K_i^{ref}(t+h)\}},\\
\tau_i(h;a_i)&=\tau_{sync}+K_i(h;a_i)\tau_{guard},\\
b_i(h;a_i)&=P_{sleep}\Delta t+5P_{idle}\tau_{sync}+P_{idle}K_i(h;a_i)\tau_{guard}\\
&\quad+E_{sense}+E_{broadcast}+\mathbf1_{h\ge T_L}\kappa\,r_i(h;a_i)D_i(h).
\end{aligned} \qquad (12)
$$

Here $\kappa=0.65$ budgets a fraction of future reference communication beyond the current period. Scheduled listening $\tau_i$ includes the first synchronization window; the fixed base $b_i$ counts that window and four additional S200 windows exactly once. Reducing $a_i$ reduces both paid listening and attainable communication capacity. Actual sensing, control and data tasks retain their complete physical costs.

Let $x_i$ denote additional communication credit for the current period, released equally across its $T_L$ rounds. For each scenario $m$, planned expenditure precedes harvesting:

$$
\widetilde B_i^{m}(0)=B_i(t),\quad e_i^{plan}(h)=b_i(h;a_i)+\mathbf1_{h<T_L}\frac{x_i}{T_L}, \qquad (13)
$$

$$
\begin{aligned}
\widetilde B_i^{m}(h)-e_i^{plan}(h)&\ge B_{reserve},\\
\widetilde B_i^{m}(h+1)&=\min\{B_{max},\widetilde B_i^{m}(h)-e_i^{plan}(h)+\widehat H_i^m(t+h\mid t)\}.
\end{aligned} \qquad (14)
$$

With roles and reference loads fixed, the joint controller chooses the listening intensity first and the communication credit second, lexicographically. Because guard counts are step functions of continuous intensity $a_i$, the feasible intensity set can have an unattained upper boundary, so the planner targets the feasible supremum:

$$
\begin{aligned}
\sup_{a_i}\quad &a_i,\\
\text{subject to}\quad &0\le a_i\le1,\quad \exists\, x_i:\;\chi_{floor}T_Lr_i(0;a_i)D_i(0)\le x_i\le B_{max},\\
&\text{the prefixes in (13)--(14) using }b_i(h;a_i).
\end{aligned} \qquad (15)
$$

JLC-R uses $\chi_{floor}=1$ to couple purchased listening to a minimum current-period service budget. For a trial $a_i$, the least-cost permissible credit is $T_Lr_i(0;a_i)D_i(0)$. With fixed roles and inputs, planned expenditure is nondecreasing in listening intensity and credit. The planner tests $a_i=1$ explicitly and otherwise uses fifteen monotone bisections on $[0,1]$, retaining a numerically feasible lower endpoint. Checking the upper endpoint avoids losing an integer guard through numerical rounding; numerical slot conversion uses a $+10^{-9}$ offset before flooring. For the returned intensity, a second fifteen-step bisection on $[0,B_{max}]$ maximizes credit. Its lower endpoint can lie below the exact floor by at most $B_{max}2^{-15}$ J; this bound is numerical and physical affordability remains enforced. The scalar credit bound in Lemma 1 applies at the fixed returned intensity.

If the zero-listening, zero-credit base prefix is infeasible, the planner records that condition explicitly, and Section 4.6 determines whether current demand warrants reactive operation. Neither branch purchases fractional guards, adds energy to storage or changes the offered sampling demand. Floor-free and fixed-listening controls isolate the budgeting mechanism in Section 6.2.

## 4.3 Reception and One-Hop Forwarding Reservation

Execution tracks physical battery energy $B_i$, communication credit $c_i$, reserved forwarding energy $E_i^{res}$ and remaining unconsumed guard transactions $k_i$. After excluding other samples' obligations, the free energy is

$$
e_i^{free}=\min\{c_i,B_i-B_{reserve}\}-E_i^{res}. \qquad (16)
$$

The raw free balance in (16) can be negative after affordable base tasks leave the battery below the communication reserve. A nonpositive balance authorizes no unreserved payment; execution compares it with a strictly positive full cost. A reserved sample may use its own held credit and forwarding transaction. Other traffic uses only uncommitted resources and cannot borrow that entitlement. Actual control expenditure is reconciled against the relevant hold, so a nominal reservation is not charged twice as physical consumption.

The sender first checks local affordability and available guard transactions. Admission treats a broadcast as fresh only when its reception timestamp $t_j^{msg}$ equals the current macro-round $t$: the threshold is $t-t_j^{msg}=0$, including broadcasts received within the same credit period. If that broadcast reports outage or credit below $E_{Rx}+E_{proc}$, the sender waits without issuing a request, and a timestamp $t_j^{msg}<t$ is stale. Routing uses a separate cache lifetime: a missing timestamp or $t-t_j^{msg}>1$ marks the node unavailable. Cached screening can therefore cause waiting before any request; surviving candidates require a charged exchange for current receiver-local feasibility. After affordable control costs have been charged, the receiver must satisfy

$$
e_j^{free}\ge E_{Rx}+E_{proc}+E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}. \qquad (17)
$$

Here $r$ denotes the reference next hop, with the intersensor request charge omitted when $r$ is the sink. Before consuming the current reception transaction, the receiver needs at least two uncommitted transactions: one for reception and one for subsequent forwarding. Successful reception creates the forwarding obligation only when the packet fits the receiver queue. A failed decoding attempt does not create an additional receiver reservation.

The reference hold $e_j^{hold}(p)=E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}$ entitles the sample to resources for one attempt without fixing its next hop. For a dynamically selected candidate $u$, let $C_{ju}=E_{Tx}(l,d_{ju})+\mathbf1_{u\ne sink}F_{ju}^{send}$. The sample may spend $A_j(p)=\min\{c_j,B_j-B_{reserve}\}-(E_j^{res}-e_j^{hold}(p))=e_j^{free}+e_j^{hold}(p)$. A charged request proceeds only when the complete control-plus-data cost satisfies $C_{ju}\le A_j(p)$. A more expensive hop can therefore use current free credit to cover the difference, while other samples' reservations remain protected. Control payments reduce battery energy and credit, along with the sample's remaining hold where applicable. A denied request retains its transaction and fee even when some held energy remains.

Competing inputs use only the credit and transactions left after existing reservations, preventing duplicate commitment of those resources. Committed samples receive priority when the node selects queued work; the local-age discipline in Section 4.4 preserves this commitment priority while ranking the remaining observations by local freshness and staleness. Actual transmission releases the remaining obligation, while a failed request retains every incurred energy and transaction charge. Unexecuted obligations expire at the round boundary; queued samples compete again under the next round's resources. The reservation protects a local one-hop attempt; end-to-end delivery is not guaranteed.

**Cluster-head transit protection for multihop relays.** Upstream CHs collect and relay source-attributed observations toward the edge gateway. Immediate member admissions can preempt their downstream relay resources. Let $b_j^{tr}=\min\{1,|\{u\in\mathrm{CH}_t:j\in\mathcal C_u\}|\}\in\{0,1\}$ indicate an upstream CH dependency. Let $r$ be $j$'s reference next hop and $f_j=E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}$. The implementation's transit unit is

$$
u_j^{tr}=\max_{u\in\mathrm{CH}_t:j\in\mathcal C_u}F_{uj}^{recv}+E_{Rx}+E_{proc}+f_j,
$$

with zero protection when no dependency exists. After the sender pays its request, but **before** $j$ consumes a response guard or pays its response, a member request ($i\notin\mathrm{CH}_t$, $j\in\mathrm{CH}_t$) additionally checks

$$
k_j-n_j^{res}-1\ge b_j^{tr},\qquad e_j^{free}-F_{ij}^{recv}-(E_{Rx}+E_{proc}+f_j)\ge b_j^{tr}u_j^{tr}.
$$

A rejection retains the sender's incurred request cost and leaves the receiver's response uncharged. An accepted request then pays the receiver response and must still pass the ordinary post-response check (17), including one remaining forwarding guard. The binary protection is a local admission margin and creates no additional guard slots or physical energy hold. The separate two-slot demand test in Algorithm 1 recognizes that reception plus subsequent forwarding needs at least two paid transactions. Inter-CH requests use the ordinary admission rule. These checks use configured local topology and local resource balances and introduce no new signaling. They protect candidate transit opportunity; per-source delivery is not guaranteed.

## 4.4 Routing, Feedback, and Algorithm Flow

Members use their current uplink associations, while CHs consider next hops with lower sink-cost ranks. A CH retains at most five candidates in implementation order. Candidate screening checks cached availability, transmission cost, credit and local reservations before applying the routing score

$$
J_{ij}=p_{ij}^{-1}+\mathrm{rank}_j+0.04\widehat Q_j+\frac{0.15}{\widehat B_j+0.15}. \qquad (18)
$$

The 0.04 coefficient has reciprocal-packet units, and the 0.15 J constants normalize the battery term; the resulting score is dimensionless. These are fixed heuristic coefficients, not fitted weights: they shape candidate ordering identically in every method, so all reported differences arise from listening, credit, hold and scheduling decisions. Here $\mathrm{rank}_j$ is candidate $j$'s sink-cost rank, defined by the shortest sum of expected transmission counts $p_{uv}^{-1}$ toward the sink. The cached queue length $\widehat Q_j$ and battery $\widehat B_j$ describe node $j$'s latest broadcast; both are zero at the sink. All ablations share this heuristic and its fixed coefficients, with reservation-enabled methods additionally prioritizing committed service. Candidate screening first checks data affordability, followed by the selected intersensor hop's complete control-plus-data check in Section 4.3. The forwarding loop stops if that cost exceeds the sample's own hold plus free credit, or if the receiver is unavailable or denies admission. The sample then remains queued; there is no forced reference-hop fallback and no exhaustive search of alternatives. This single-choice rule guarantees that a node never spends beyond the checked resources. When $e_j^{free}=0$, a hop exceeding the remaining hold cannot execute even if the reference receiver is unavailable. Unspent holds expire at the round boundary, and the sample competes again until delivery, overflow or expiry. This mechanism guarantees local non-overcommitment while leaving route execution and delivery conditional on available resources. Link failures consume the attempt's resources without creating a reserved retry.

In Algorithm 1, $\textsc{Floor}_i(a)=T_Lr_i(0;a)D_i(0)$ is the minimum reference communication budget. Algorithm 2 executes charged requests, admission and data. Packet selection first protects locally committed samples, then prioritizes locally uncovered sources; among samples tied on uncovered status and fresh-coverage gain, the oldest sender-local forwarded birth round is served first. Sequence number is only a final tie-break. This uses local successful-hop history without sink-age feedback. The local queue is $Q_i$, $n_i^{res}$ counts forwarding guard holds, and $A_i(p)$ combines uncommitted credit with sample $p$'s own hold. Prefix feasibility uses tolerance $\epsilon_{num}=10^{-10}$ J. Appendix A gives precise statements and proof sketches; complete derivations and the distinct physical-balance and reservation tolerances are provided in the reproducibility repository.

```{=latex}
\begin{algorithm}[!htbp]
\caption{JLC-R prefix planning and PADC-based mode selection}
\label{alg:plan}
\small
\begin{algorithmic}[1]
\REQUIRE Current local battery and queue/history; causal forecast bank; known roles; $H=96$, $T_L=4$, $I=15$; previous mode $h_i$
\ENSURE Paid integer listening profile and released communication permission
\STATE Construct causal point and residual paths in (9)--(10)
\STATE $a_i^P\gets0$; $x_i^P\gets0$; $f_i\gets\neg\textsc{PrefixFeasible}(0,0)$
\IF{$\neg f_i$}
  \STATE $L\gets0$; $U\gets1$
  \IF{$\textsc{PrefixFeasible}(U,\textsc{Floor}_i(U))$}
    \STATE $L\gets U$
  \ELSE
    \FOR{$q=1,\ldots,I$}
      \STATE $v\gets(L+U)/2$
      \IF{$\textsc{PrefixFeasible}(v,\textsc{Floor}_i(v))$}
        \STATE $L\gets v$
      \ELSE
        \STATE $U\gets v$
      \ENDIF
    \ENDFOR
  \ENDIF
  \STATE $a_i^P\gets L$; $L_2\gets0$; $U_2\gets B_{max}$
  \FOR{$q=1,\ldots,I$}
    \STATE $v\gets(L_2+U_2)/2$
    \IF{$\textsc{PrefixFeasible}(a_i^P,v)$}
      \STATE $L_2\gets v$
    \ELSE
      \STATE $U_2\gets v$
    \ENDIF
  \ENDFOR
  \STATE $x_i^P\gets L_2$
\ENDIF
\STATE $d_i\gets$ queued uncovered-fresh demand $\vee\ \bigl(i\in\text{CH}_t\wedge\lfloor a_i^PK_i^{ref}(t)\rfloor<2\bigr)$
\STATE $\,h_i^{\,\prime}\gets d_i\wedge[f_i\vee(a_i^P<0.60)\vee(h_i\wedge a_i^P<0.70)]$
\IF{$h_i^{\,\prime}$}
  \STATE $a_i\gets\textsc{PADCDuty}(B_i,\widehat H_i^{point},\text{reference costs})$; $x_i\gets T_LB_{max}$
\ELSE
  \STATE $a_i\gets a_i^P$; $x_i\gets x_i^P$
\ENDIF
\STATE Install $K_i(h)\gets\lfloor a_iK_i^{ref}(t+h)\rfloor$ and actual paid listening for every known role
\STATE Release $c_i\gets x_i/T_L$ each round; execute Algorithm 2's battery/hold/capacity checks; retain $h_i^{\,\prime}$ for the next epoch
\STATE \textbf{function} $\textsc{PrefixFeasible}(a,x)$
\IF{$x>B_{max}$}
  \RETURN \textbf{false}
\ENDIF
\FOR{$m=1,\ldots,M$}
  \STATE $b\gets B_i(t)$
  \FOR{$h=0,\ldots,H-1$}
    \STATE $e\gets$ integer paid-base specialization of (12) $+\mathbf1_{h<T_L}x/T_L$
    \IF{$b-e<B_{reserve}-\epsilon_{num}$}
      \RETURN \textbf{false}
    \ENDIF
    \STATE $b\gets\min\{B_{max},b-e+\widehat H_i^m(t+h\mid t)\}$
  \ENDFOR
\ENDFOR
\RETURN \textbf{true}
\end{algorithmic}
\end{algorithm}
```

```{=latex}
\begin{algorithm}[!htbp]
\caption{Charged receiver reservation and execution}
\label{alg:exec}
\small
\begin{algorithmic}[1]
\REQUIRE Batteries $B_i$, queues $Q_i$, cached broadcasts, plans from Algorithm 1, horizon $T$
\ENSURE Updated batteries, queues, reservations and unique sample-outcome ledger
\STATE \textit{Each break ends the current node action loop; the next node still executes.}
\FOR{$t=0,\ldots,T-1$}
  \IF{$t\bmod T_L=0$}
    \STATE Run Algorithm 1 at each node and install the configured roles
  \ENDIF
  \STATE $c_i\gets x_i/T_L$; $k_i\gets K_i(t)$; clear previous-round holds, for every $i$
  \STATE Expire old samples; pay affordable base/sensing/broadcast tasks, or record unsampled
  \FOR{each online $i$: members first, then CHs in decreasing sink-cost rank}
    \FOR{$a=1,\ldots,96$}
      \IF{$Q_i=\varnothing$}
        \STATE \textbf{break}
      \ENDIF
      \STATE $p\gets$ highest-priority sample in $Q_i$ (committed first; uncovered local-age next, breaking birth ties by oldest local forward then sequence)
      \STATE $j\gets$ member's parent, or $\arg\min_{u\in\mathcal C_i(p)}J_{iu}$ for a CH, using (18)
      \IF{no candidate, $E_{Tx}(l,d_{ij})>A_i(p)$, or no usable sender transaction}
        \STATE \textbf{break}
      \ENDIF
      \STATE $f\gets0$
      \IF{$j\ne sink$}
        \IF{same-round cache reports $j$ unavailable, or $E_{Tx}(l,d_{ij})+F_{ij}^{send}>A_i(p)$}
          \STATE \textbf{break}
        \ENDIF
        \STATE $\textsc{ConsumeSlot}(i,p)$; $\textsc{PayControl}(i,F_{ij}^{send},p)$
        \IF{$j$ offline, $e_j^{free}<F_{ij}^{recv}$, or $k_j-n_j^{res}<1$}
          \STATE \textbf{break}
        \ENDIF
        \STATE $r\gets$ reference next hop of $j$; $f\gets E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}$
        \IF{$i\notin\text{CH}_t$ and $j\in\text{CH}_t$}
          \STATE $z\gets b_j^{tr}$
          \IF{$k_j-n_j^{res}-1<z$ or $e_j^{free}-F_{ij}^{recv}-(E_{Rx}+E_{proc}+f)<zu_j^{tr}$}
            \STATE \textbf{break} \COMMENT{sender request charged; receiver response not charged}
          \ENDIF
        \ENDIF
        \STATE $\textsc{ConsumeSlot}(j)$; $\textsc{PayControl}(j,F_{ij}^{recv})$
        \IF{$e_j^{free}<E_{Rx}+E_{proc}+f$ or $k_j-n_j^{res}<1$}
          \STATE \textbf{break}
        \ENDIF
      \ENDIF
      \STATE Release $p$'s remaining hold at $i$; if $j=sink$, consume one sender transaction
      \STATE $(ok,reason)\gets\textsc{DataAttempt}(i,j,p)$ using (1) and the physical energy model
      \IF{$ok$}
        \STATE Remove $p$ from $Q_i$; deliver to the sink or enqueue at $j$ unless overflow
        \IF{$j\ne sink$ and $p$ was enqueued}
          \STATE $e_j^{hold}(p)\gets f$; $E_j^{res}\gets E_j^{res}+f$; $n_j^{res}\gets n_j^{res}+1$
        \ENDIF
      \ELSIF{$reason\ne\texttt{link\_loss}$ or $p$ has reached three attempts this round}
        \STATE \textbf{break}
      \ENDIF
    \ENDFOR
  \ENDFOR
  \STATE Record service/unused credit \COMMENT{Assert reservation and capacity invariants}
  \STATE $B_i\gets\min\{B_{max},B_i+H_i(t)\}$ for every $i$; account for spill and check conservation
\ENDFOR
\end{algorithmic}
\end{algorithm}
```

The cached candidate set $\mathcal C_i(p)$ follows the data-affordability screening in Section 4.4 and contains at most five lower-rank neighbors. $\textsc{ConsumeSlot}$ first uses a sample's own reserved transaction, while $\textsc{PayControl}$ debits battery and credit and reconciles its held energy. $\textsc{DataAttempt}$ charges transmission, reception and successful processing, applies the decoding test and updates the unique sample ledger. An admission rejection preserves the queued sample and all incurred charges. Every break in Algorithm 2 exits the current node's 96-action loop, then execution continues with the next node; it neither exits the macro-round nor starts an alternative-candidate search, as discussed in Section 4.4.

With two 15-step searches, planning takes $O(IMH)$ time and $O(MH)$ local working storage for $M$ scenarios, $H$ forecast rounds and $I=15$ iterations; the vectorized simulator uses $O(IMNH)$ aggregate time. Queue selection scans at most $Q_{max}$ packets per action. These finite computations establish termination rather than network-state convergence.

\FloatBarrier

## 4.5 Resource Safety and Service Boundaries

The prefix certificate applies to planned scenarios, whereas physical affordability, reservation safety and demand conservation bind every executed action in both modes. These are separate properties: a safe current transaction does not imply a feasible future energy trajectory or successful end-to-end delivery.

**Assumption A1 (Atomic serialized admission).** A receiver completes one request, charged response/denial and resulting data transition before another request can inspect or modify its local balances. Concurrent radio receptions, hidden terminals and distributed compare-and-swap are outside this model.

**Lemma 1 (Execution safety and numerical-accuracy invariants).** *Fix the current battery, role sequence, listening plan, reference load and scenario bank. Let $\mathcal F_\epsilon\subseteq[0,B_{max}]$ contain credits whose prefix margins in (14) are all at least $-\epsilon$ for a fixed listening intensity $a$. If $0\in\mathcal F_\epsilon$, then $\mathcal F_\epsilon$ is a closed interval $[0,x_\epsilon^*]$, and after $I$ bisections the returned feasible lower endpoint $L_I$ satisfies $0\le x_\epsilon^*-L_I\le B_{max}2^{-I}$. Under the affordability guard $E_i(t)\le B_i(t)$ and (4), each node satisfies $0\le B_i(t)\le B_{max}$, and every admitted feasible credit satisfies all scenario prefix reserve constraints. Under A1, at serialized transaction boundaries the held energy and held guard transactions never exceed the receiver's uncommitted balance and capacity: $E_j^{res}\le\max\{0,\min\{c_j,B_j-B_{reserve}\}\}$ and $|\mathcal S_j(t)|\le k_j$. Finally, for any horizon $T$, offered demand $NT$ equals unsampled, delivered, expired, overflowed and in-transit packets, and the node energy ledger closes:*

$$
B_i(T)=B_i(0)+\sum_{t=0}^{T-1}\bigl[H_i(t)-E_i^{spilled}(t)\bigr]-\sum_{t=0}^{T-1}\bigl[E_i^{base}(t)+E_i^{data}(t)+E_i^{ctrl}(t)\bigr].
$$

*The proof, which follows from monotonicity of the clipped battery recursion, the affordability guard, serialized reservations and the disjoint terminal outcomes, is outlined in Appendix A, with full derivations in the reproducibility repository. If zero credit is infeasible for the fixed intensity, returning zero is a fallback without a feasibility certificate. For $B_{max}=4$ J and $I=15$, the credit error is bounded by $1.22\times10^{-4}$ J, and the per-round release error by at most $3.05\times10^{-5}$ J. These bounds apply to the fixed-input scalar optimum in $\mathcal F_\epsilon$, not to network freshness optimization. Numerical execution accepts prefix margins down to $-10^{-10}$ J.*

The prefix feasible set is downward closed in credit and listening intensity (Proposition 2 in Appendix A). Credit alone cannot repair an unaffordable listening base. Conversely, reservations require compatible queue order: an unfunded FIFO head can block a funded committed packet (Proposition 1). Committed-first scheduling supplies no per-source service guarantee (Proposition 3). The conditional serial-service theorem in Appendix A assumes sufficient endpoint resources, passing protected admissions, successful decoding and adequate queues; the executed greedy route does not enforce these conditions. These limits motivate the complementary AoI and source-P5 outcomes.




## 4.6 Locally Gated PADC-Based Reactive Mode

Let $a_i^P,x_i^P$ denote the prefix plan, and let $f_i$ record failure of the zero-base prefix together with zero installed listening and credit. Zero credit alone does not imply this condition. Local demand $d_i$ holds when an unexpired queued packet comes from a source without a sufficiently recent successful hop in the sender's history, or when an active CH has fewer than two planned guards ($\lfloor a_i^PK_i^{ref}(t)\rfloor<2$). Two guards provide the minimum receive-and-forward opportunity, including one protected outgoing transaction. Demand recognition occurs at period installation, before new samples and receptions can populate the queue. With previous hybrid state $h_i$, the fixed mode decision is

$$
h_i^{\,\prime} = d_i\wedge\left[f_i\vee(a_i^P<0.60)\vee(h_i\wedge a_i^P<0.70)\right].
$$

When $h_i^{\,\prime}=1$, JLC-R uses the PADC duty law [@padc2023] on the current battery plus the causal four-round point forecast, normalized by capacity and reference activity costs. It installs integer listening slots at that duty and period communication permission $x_i=T_LB_{max}$, matching the nonbinding-permission semantics of the PADC adapter. This number is a permission bound, not energy added to storage: every request, reception, processing operation and subsequent hold is checked against current battery, communication reserve and available capacity. Otherwise the original prefix plan is retained. The queue gate uses state already available at planning time and inspects no private receiver resources, future weather, future decoding or global sink age. The next mode is recomputed each planning epoch without resetting queues, battery, successful-hop history or physical holds.

The reactive branch changes the applicable guarantee. It permits service when the long-horizon plan lacks a certificate; it does not inherit scenario-prefix feasibility or promise long-term energy neutrality. The finite physical debit and atomic hold conditions remain unchanged. The fixed 0.60/0.70 hysteresis adds constant state per node, but the implementation still computes the full prefix plan first, even when many nodes use PADC afterward. Its planning cost is therefore $O(IMNH)$ plus the duty calculation and queue scan, rather than the cost of the reactive rule alone. Calibrated planner CPU-energy consumption is not included in the radio/sensing energy ledger, and no embedded runtime has been measured.

\FloatBarrier

## Extended tables E1--E8

The E labels preserve the complete pre-compression numerical displays. Current main Tables 1--4 are mapped in docs/reproduction_map.md.

Table E1. Physical and execution parameters of the primary confirmation.

| Category | Parameter | Value |
| --- | --- | --- |
| Network | Nodes; area; range | 100; 300 m×300 m; 120 m |
| Organization | Cells; rotation candidates per cell | 4×3; 5 |
| Time | Macro-round; credit period; forecast horizon | 900 s; 4 rounds; 96 rounds |
| Duration | Formal evaluation; forecast warm-up | 14 days; 2 days |
| Battery | Capacity; initial energy; communication reserve | 4 J; 3 J; 0.15 J |
| Recovery | Restart threshold after outage | At least 0.08 J and affordable current base tasks |
| Harvesting | Peak; supply multiplier | 0.12 J/round; 1.0 and 0.7 |
| Data | Logical packet; deadline; queue limit | 4000 bits; 4 rounds; 256 packets |
| Radio | $E_{elec}$; $\varepsilon_{fs}$; $\varepsilon_{mp}$ | 50 nJ/bit; 10 pJ/(bit·m$^2$); 0.0013 pJ/(bit·m$^4$) |
| Processing | Sensing; aggregation | Both 5 nJ/bit |
| Base power | Sleep; offline; extra idle listening | 5 µW; 2 µW; 56 mW |
| Listening | Member/CH caps; guard per transaction | 0.1/1 s; 20 ms (G20) |
| Synchronization | Interval; window; paid windows per round | 200 s; 20 ms; 5 (S200) |
| Grants | Request/response payload; logical data rate | 64 bits each; 250 kbps |
| Planning | Traffic margin; future relay fraction | 1.25; 0.65 |
| Forecast | EWMA coefficient; scenarios; residual quantile | 0.7; 4; 0.9 |
| Cache | Fresh grant check; routing-cache lifetime | Same macro-round; at most 1 round |
| Broadcast | Prepaid cost per node per credit period | 0.0002 J |
| Execution | Decoding attempt limit; per-node loop limit | 3; 96 |

**Table note.** All five primary methods share these physical parameters. Listening caps include the first synchronization window and paid guard capacity; four additional 20-ms windows are charged in both planning and execution. A guard is a charged transaction opportunity; payload airtime and the round serialization envelope are checked separately.

Table E2. Five-method outcomes and primary noninferiority decisions in the independent confirmation.

| Input | Supply | Controller | Coverage (%) | Mean AoI (min) | Source P5 (%) | Night outage (%) | Energy (J) | Max NI Holm p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Synthetic | 1.0 | JLC-R$^{*}$ | 55.062 | 545.303 | 28.691 | 0.983 | 2218.896 | 0.002162 |
| Synthetic | 1.0 | Prefix-only | 54.660 | 586.162 | 27.230 | 0.531 | 2219.789 | --- |
| Synthetic | 1.0 | Hybrid control | 54.739 | 577.079 | 27.284 | 0.974 | 2218.790 | --- |
| Synthetic | 1.0 | PADC-AGE | 51.278 | 630.492 | 23.655 | 0.768 | 2190.671 | --- |
| Synthetic | 1.0 | PADC+relay | 51.652 | 591.701 | 25.197 | 0.772 | 2190.749 | --- |
| Synthetic | 0.7 | JLC-R$^{*}$ | 39.665 | 1046.021 | 17.752 | 5.439 | 1984.943 | 0.03711 |
| Synthetic | 0.7 | Prefix-only | 38.922 | 1250.015 | 15.486 | 4.603 | 1983.755 | --- |
| Synthetic | 0.7 | Hybrid control | 39.272 | 1127.244 | 15.948 | 5.427 | 1984.887 | --- |
| Synthetic | 0.7 | PADC-AGE | 34.155 | 1293.363 | 11.586 | 4.198 | 1942.633 | --- |
| Synthetic | 0.7 | PADC+relay | 34.610 | 1161.352 | 12.624 | 4.204 | 1942.702 | --- |
| T1 winter | 1.0 | JLC-R$^{*}$ | 15.398 | 3814.259 | 2.729 | 2.579 | 1610.813 | 0.001426 |
| T1 winter | 1.0 | Prefix-only | 10.789 | 3947.077 | 2.331 | 0.943 | 1598.788 | --- |
| T1 winter | 1.0 | Hybrid control | 14.867 | 4272.273 | 2.536 | 2.556 | 1610.738 | --- |
| T1 winter | 1.0 | PADC-AGE | 14.264 | 4106.294 | 3.265 | 3.198 | 1606.269 | --- |
| T1 winter | 1.0 | PADC+relay | 14.698 | 3777.080 | 3.505 | 3.207 | 1606.280 | --- |
| T1 winter | 0.7 | JLC-R$^{*}$ | 9.951 | 4080.726 | 3.120 | 21.067 | 1250.438 | 0.002162 |
| T1 winter | 0.7 | Prefix-only | 5.375 | 8184.607 | 1.626 | 17.250 | 1247.310 | --- |
| T1 winter | 0.7 | Hybrid control | 9.732 | 4146.056 | 2.940 | 20.953 | 1250.308 | --- |
| T1 winter | 0.7 | PADC-AGE | 9.636 | 4241.756 | 3.561 | 22.754 | 1251.909 | --- |
| T1 winter | 0.7 | PADC+relay | 9.719 | 4198.559 | 3.619 | 22.755 | 1251.909 | --- |
| T2 spring | 1.0 | JLC-R$^{*}$ | 70.599 | 72.032 | 38.620 | 0.000 | 2410.614 | 0.02979 |
| T2 spring | 1.0 | Prefix-only | 70.459 | 81.068 | 36.503 | 0.000 | 2408.573 | --- |
| T2 spring | 1.0 | Hybrid control | 70.377 | 75.417 | 36.513 | 0.000 | 2410.504 | --- |
| T2 spring | 1.0 | PADC-AGE | 68.306 | 85.356 | 34.389 | 0.000 | 2404.327 | --- |
| T2 spring | 1.0 | PADC+relay | 68.596 | 80.488 | 37.204 | 0.000 | 2404.428 | --- |
| T2 spring | 0.7 | JLC-R$^{*}$ | 48.086 | 291.959 | 17.828 | 0.009 | 2162.718 | 0.02237 |
| T2 spring | 0.7 | Prefix-only | 48.393 | 426.996 | 15.656 | 0.000 | 2159.461 | --- |
| T2 spring | 0.7 | Hybrid control | 47.704 | 342.786 | 15.749 | 0.009 | 2162.704 | --- |
| T2 spring | 0.7 | PADC-AGE | 43.470 | 432.096 | 10.935 | 0.017 | 2141.508 | --- |
| T2 spring | 0.7 | PADC+relay | 43.915 | 327.549 | 12.983 | 0.017 | 2141.517 | --- |
| T3 winter | 1.0 | JLC-R$^{*}$ | 8.555 | 4890.627 | 2.448 | 42.756 | 1017.912 | 0.0004567 |
| T3 winter | 1.0 | Prefix-only | 4.919 | 7688.690 | 1.044 | 39.665 | 1014.132 | --- |
| T3 winter | 1.0 | Hybrid control | 8.368 | 4975.376 | 2.218 | 42.689 | 1017.764 | --- |
| T3 winter | 1.0 | PADC-AGE | 8.055 | 5092.023 | 2.861 | 43.577 | 1018.353 | --- |
| T3 winter | 1.0 | PADC+relay | 8.127 | 5065.694 | 2.936 | 43.580 | 1018.353 | --- |
| T3 winter | 0.7 | JLC-R$^{*}$ | 6.580 | 6394.479 | 2.078 | 59.084 | 817.062 | 0.0001624 |
| T3 winter | 0.7 | Prefix-only | 3.850 | 8715.874 | 0.933 | 56.691 | 813.762 | --- |
| T3 winter | 0.7 | Hybrid control | 6.476 | 6433.808 | 1.811 | 59.034 | 816.944 | --- |
| T3 winter | 0.7 | PADC-AGE | 6.235 | 6356.825 | 2.387 | 59.721 | 818.594 | --- |
| T3 winter | 0.7 | PADC+relay | 6.273 | 6356.324 | 2.489 | 59.722 | 818.594 | --- |

**Table note.** Means over twelve unused paired seeds per cell (480 runs). The star marks satisfaction of all four prespecified NI margins in that cell against Prefix-only for Synthetic/T2 and PADC-AGE for T1/T3, under the common 36-test Holm family. The last column is the largest adjusted p among those four NI contrasts, not an all-pairwise superiority test. The deterministic T2/1.0 zero-outage tie satisfies its margin without finite-t inference. No NI criterion is defined for energy. Repository Figure R1 shows the paired effects and nominal 95% intervals; full per-contrast statistics remain in the reproducibility repository.

Table E3. Historical G10 listening and reference-floor controls.

| Contrast | Seeds/cell | Supply 1.0, coverage change (pp) | Supply 0.7, coverage change (pp) |
| --- | --- | --- | --- |
| Joint minus fixed listening | 12 paired | +15.61 [+12.39, +18.84] | +16.97 [+14.45, +19.48] |
| Reference floor, continuous planner | 12 paired | +13.70 [+10.64, +16.76] | +14.49 [+12.29, +16.68] |
| Reference floor, integer planner | 12 paired | +13.74 [+10.56, +16.91] | +14.35 [+12.44, +16.25] |

**Table note.** Seed-paired coverage differences and nominal 95% $t$ intervals; all contrasts share the same twelve-seed cohort. The four reference-floor coverage tests form a separate Holm family. These controls use original base synchronization and a 10-ms Guard (maximum member/CH capacities 8/98 transactions and 40-ms two-Guard reference listening). They are not pooled with the primary S200/G20 confirmation.

Table E4. Prespecified primary relay-factorial tests under low-supply winter S200/G20 conditions.

| Hypothesis and contrast | Outcome | Difference (pp), 95% CI | Raw $p$ | Holm-4 $p$ |
| --- | --- | --- | --- | --- |
| H1: complete bundle | Far coverage | +0.192 [+0.127, +0.256] | 0.000041 | 0.000165 |
| H2: transit protection T | Far coverage | -0.003 [-0.013, +0.007] | 0.548023 | 0.548023 |
| H3: two-slot recognition R | Overall coverage | +0.052 [-0.004, +0.108] | 0.067296 | 0.134592 |
| H4: staleness ordering S | Source P5 | +0.207 [+0.125, +0.289] | 0.000174 | 0.000523 |

**Table note.** Each of twelve seed-level contrasts first averages T1 and T3 at $s=0.7$ equally. The bundle is A111 minus A000; T, R and S are marginal on-minus-off effects averaged over the other factors. Intervals are nominal paired 95% $t$ intervals with 11 degrees of freedom. Two-sided tests use one separate Holm-4 family at $\alpha=0.05$. H1 and H4 pass that correction; H2 and H3 remain unresolved. Nonsignificance does not establish equivalence.

Table E5. Factorial ablation of relay protection under low-supply winter S200/G20 conditions.

| Configuration | T | R | S | Coverage (%) | Far coverage (%) | Source P5 (%) | AoI (h) | Night outage (%) | Energy (J) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A000 (Hybrid) | 0 | 0 | 0 | 7.811 | 4.647 | 2.054 | 90.136 | 40.019 | 1031.382 |
| A001 | 0 | 0 | 1 | 7.842 | 4.769 | 2.252 | 89.486 | 40.017 | 1031.383 |
| A010 | 0 | 1 | 0 | 7.859 | 4.722 | 2.057 | 90.322 | 40.107 | 1031.552 |
| A011 | 0 | 1 | 1 | 7.889 | 4.842 | 2.256 | 89.667 | 40.105 | 1031.552 |
| A100 | 1 | 0 | 0 | 7.899 | 4.645 | 2.045 | 89.882 | 40.019 | 1031.382 |
| A101 | 1 | 0 | 1 | 7.929 | 4.764 | 2.262 | 89.203 | 40.015 | 1031.383 |
| A110 | 1 | 1 | 0 | 7.956 | 4.720 | 2.057 | 90.084 | 40.112 | 1031.552 |
| A111 (JLC-R) | 1 | 1 | 1 | 7.985 | 4.839 | 2.268 | 89.388 | 40.109 | 1031.552 |

**Table note.** Each configuration mean first weights T1 winter and T3 winter at $s=0.7$ equally within each of twelve new paired seeds. These are 192 executions from the complete 864-run study. T is the additional pre-response transit margin; R is two-slot demand recognition; S is the exact local-staleness key. All configurations retain ordinary paid reception, one-hop holds, forwarding Guard safety and the same physical inputs. Far coverage uses the source--time denominator of sources at least 200 m from the sink; Source P5 uses all 100 sources. Figure 4 shows seed-paired effects and nominal 95% intervals. All nine conditions and all eight configurations remain in the complete data record.

Table E6. Winter monitoring response to effective supply scaling.

| Condition | $s$ | JLC-R | Prefix-only | Hybrid control | PADC-AGE | JLC-R P5 (%) | JLC-R AoI (h) | Battery change (J) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 winter | 0.7 | 9.71 | 5.23 | 9.49 | 9.43 | 2.75 | 69.8 | -2.78 |
| T1 winter | 1.0 | 14.81 | 10.07 | 14.32 | 13.80 | 2.37 | 68.2 | -2.23 |
| T1 winter | 1.5 | 33.57 | 31.86 | 33.13 | 30.02 | 6.28 | 10.4 | -0.51 |
| T1 winter | 2.0 | 52.87 | 51.66 | 52.55 | 49.79 | 17.38 | 2.8 | +0.08 |
| T1 winter | 2.5 | 65.61 | 64.92 | 65.37 | 64.86 | 30.24 | 1.5 | +0.36 |
| T1 winter | 3.0 | 71.07 | 70.22 | 70.91 | 72.64 | 36.74 | 1.1 | +0.44 |
| T3 winter | 0.7 | 6.47 | 3.74 | 6.37 | 6.15 | 1.81 | 107.5 | -2.76 |
| T3 winter | 1.0 | 8.33 | 4.73 | 8.17 | 7.90 | 2.08 | 84.4 | -2.45 |
| T3 winter | 1.5 | 13.30 | 9.17 | 13.00 | 11.98 | 2.95 | 47.7 | -1.59 |
| T3 winter | 2.0 | 20.47 | 16.11 | 20.10 | 18.50 | 4.79 | 32.9 | -0.46 |
| T3 winter | 2.5 | 28.09 | 23.56 | 27.66 | 25.97 | 7.22 | 22.5 | +0.21 |
| T3 winter | 3.0 | 35.55 | 31.22 | 35.13 | 33.34 | 11.07 | 14.1 | +0.40 |

**Table note.** Means over twelve new seeds ($170101$--$171212$) per cell and multiplier. Coverage and Source P5 are percentages; AoI is in hours; battery change is the end-of-run node mean minus the 3-J initial value. Supply multipliers are normalized model scalars applied to physical harvest and to the causal forecast, not calibrated panel-area or irradiance multipliers. These runs are exploratory and are not pooled with Table 2.

Table E7. Freshness-window sensitivity of JLC-R coverage.

| Cell (supply) | 30 min | 60 min | 120 min | 240 min | P5 at 60 min | $\Delta$ vs matched at 60 min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Synthetic 1.0 | 41.63 | 55.06 | 67.63 | 75.75 | 28.69 | +0.40 |
| Synthetic 0.7 | 29.68 | 39.67 | 50.43 | 59.08 | 17.75 | +0.74 |
| T1 winter 1.0 | 11.44 | 15.40 | 20.64 | 27.19 | 2.73 | +1.13 |
| T1 winter 0.7 | 7.12 | 9.95 | 13.98 | 19.68 | 3.12 | +0.31 |
| T2 spring 1.0 | 53.34 | 70.60 | 86.43 | 95.30 | 38.62 | +0.14 |
| T2 spring 0.7 | 36.11 | 48.09 | 61.60 | 73.45 | 17.83 | -0.31 |
| T3 winter 1.0 | 6.16 | 8.56 | 11.97 | 16.79 | 2.45 | +0.50 |
| T3 winter 0.7 | 4.77 | 6.58 | 9.07 | 12.39 | 2.08 | +0.34 |

**Table note.** JLC-R coverage (%) recomputed on the frozen 480 confirmation trajectories. Matched comparator is Prefix-only for Synthetic/T2 and PADC-AGE for T1/T3; the last column is a descriptive paired difference at the study criterion. Packet generation, routing, energy and four-round expiry are unchanged; only the age criterion changes. D=4 reproduces Table 2.

Table E8. Spatial energy and channel heterogeneity stress test in T2 spring.

| Treatment | JLC-R (%) | Prefix-only (%) | Hybrid control (%) | PADC-AGE (%) | JLC-R P5 (%) | JLC-R far (%) | JLC-R $\Delta$ vs C0 (pp) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 67.16 | 66.92 | 66.86 | 64.60 | 29.66 | 51.50 | 0.00 |
| I-C1 | 62.93 | 62.72 | 62.53 | 59.74 | 26.16 | 46.04 | -4.23 |
| II-C1 | 53.41 | 53.35 | 52.97 | 49.39 | 17.44 | 34.31 | -13.75 |
| II-C2 | 66.03 | 65.78 | 65.68 | 63.46 | 29.88 | 50.02 | -1.14 |
| II-C3 | 52.33 | 52.33 | 51.94 | 48.23 | 17.94 | 32.80 | -14.83 |
| III-C1 | 38.69 | 38.88 | 38.24 | 35.00 | 8.09 | 18.99 | -28.47 |
| III-C2 | 63.96 | 63.67 | 63.59 | 61.63 | 27.21 | 46.02 | -3.20 |
| III-C3 | 36.60 | 36.61 | 36.10 | 32.85 | 7.35 | 16.35 | -30.56 |

**Table note.** Means over twelve new seeds ($190101$--$191212$) on the T2 spring trajectory at $s=1.0$. C1 applies energy transmittance only, C2 channel attenuation only, C3 both. The same spatial energy--link index is shared by all controllers within a seed, with the opposing energy and decoding responses specified in Section 5.5. Far sources are at least 200 m from the sink. Transmittance and attenuation ranges are exploratory stress parameters, not measured crop properties. These runs are not pooled with Table 2.


# Part V. Submission-strengthening evidence (25 October 2026)

This addition does not modify any of the original S/E tables, confirmation statistics or frozen controller. The prospective recording protocol and source were locked before the 144 new outcomes were examined. These runs are post-confirmation exploratory observations, separate from both Holm-36 and Holm-4. The three cells, four controllers and twelve paired network seeds are listed in `code/experiments/v6_4_agricultural_extension/reliability_20261025_protocol.json`. No crop events, hardware calibration or implemented contention MAC are supplied.

Table E9. Reference-task parameter evidence and transfer boundaries.

| Parameter | Value | Evidence class | Transfer boundary |
| --- | --- | --- | --- |
| Effective harvest | 0.12 J/900 s | simulation setting | 0.133 mW is an arithmetic conversion; no panel-area calibration |
| Storage / initial energy | 4 J / 3 J | simulation setting | no commercial battery or capacitor assigned |
| Radio-on listening | 56 mW | simulation input; manufacturer-order reference | CC2420 RX 18.8 mA at assumed 3 V gives 56.4 mW; not a node measurement |
| Guard / synchronization | 20 ms / 200 s, five windows | simulation timing assumptions | 17-ms configured uncertainty bound; no oscillator experiment |
| Logical bitrate | 250 kbps | simulation input; manufacturer-supported rate | framing/fragmentation/ACK overhead excluded |
| Logical observation | 4000 bits (500 bytes) | simulation workload | 16-ms nominal payload time; not one physical 802.15.4 frame |
| Control message | 64 bits | executed model setting | Eq. (7) allowance; narrative 160-bit error corrected |
| Sampling | 15 min | reference task setting | not derived from frost/irrigation event labels |
| Freshness criterion | 60 min, sensitivity 240 min | service evaluation criterion | not a universal agronomic tolerance |

**Table note.** Exact source locations and source categories are in `docs/paper_audit/strengthening_20261025/parameter_evidence_20261025.csv`. No entry is a measurement of the proposed node. Manufacturer data are from TI CC2420 SWRS041C (2013); assumed voltage is explicitly identified. The 64-bit control width is the executed default, correcting a 160-bit narrative error without altering energy accounting.

Table E10. Independent availability recordings corresponding to main Table 5.

| Cell / supply | Controller | Median gap (h) | P95 gap (h) | Sources >4 h (%) | Far recovery (h) | Censored (%) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T1 / 0.7 | JLC-R | 189.75 | 309.14 | 100.00 | 2.79 | 7.55 |
| T1 / 0.7 | JLC-Core | 185.86 | 310.31 | 100.00 | 2.94 | 7.64 |
| T1 / 0.7 | Prefix-only | 313.05 | 322.29 | 100.00 | 1.60 | 17.24 |
| T1 / 0.7 | PADC-AGE | 196.49 | 313.35 | 100.00 | 3.05 | 7.65 |
| T3 / 0.7 | JLC-R | 281.96 | 319.64 | 100.00 | 2.12 | 11.32 |
| T3 / 0.7 | JLC-Core | 282.20 | 320.62 | 100.00 | 2.24 | 11.61 |
| T3 / 0.7 | Prefix-only | 313.18 | 329.84 | 100.00 | 1.79 | 24.21 |
| T3 / 0.7 | PADC-AGE | 283.08 | 320.98 | 100.00 | 2.80 | 11.52 |
| T2 / 1.0 | JLC-R | 5.15 | 21.28 | 48.25 | 1.29 | 0.51 |
| T2 / 1.0 | JLC-Core | 5.10 | 23.24 | 48.50 | 1.35 | 0.54 |
| T2 / 1.0 | Prefix-only | 6.14 | 27.84 | 52.50 | 1.38 | 0.35 |
| T2 / 1.0 | PADC-AGE | 6.34 | 22.34 | 57.25 | 1.38 | 0.77 |

**Table note.** Twelve paired network seeds per cell; four controllers and three cells give 144 executions. A gap is a maximal run without a delivered observation aged at most 60 min. Median/P95 columns are across-source quantiles of each source's longest observed gap, averaged across seeds. Sources >4 h includes initialization and horizon-censored gaps. Far recovery is the mean across seeds of completed-episode medians for sources at least 200 m from the sink, excluding initialization; Censored is the mean percentage of eligible far-source recovery episodes unfinished at day 14. Completed recovery and censored episodes must be interpreted together. Full event rates, 240-minute-criterion results and nominal paired intervals are retained in the reproducibility archive.

The full 96-row summary and nominal paired intervals are in `results/reliability_20261025_summary.csv` below the existing agricultural-extension directory. The 144 raw delivered-birth matrices and metadata are in `results/reliability_20261025_raw/`. Source-level summaries and event episodes are in `reliability_20261025_sources.csv` and `reliability_20261025_episodes.csv.gz`. Initialization counts as unavailable; left/right-censored durations are observed lower bounds. Recovery excludes initialization and incomplete episodes; right-censoring remains separately reported. Thus a short completed recovery median cannot by itself indicate better availability.

The recording wrapper exactly reproduced the five reference metrics of the frozen T3/0.7 JLC-R case at seed 160101 before the new matrix. This is a fidelity regression, not a new independent data point. `results/reliability_20261025_regression.json` records zero deviations. The 144-run progress and execution freeze preserve zero failures, protocol/source hashes and all case identities. The original five safety/information tests also passed.

## Reproduction and independent verification

`python -B scripts/reproduce.py --mode verify` checks hashes, raw traces, censoring, independent network pairing, all main Table 5 cells and all original statistics. `--mode reproduce` reconstructs the availability summaries from the 144 raw matrices using an independent group-by implementation, without importing or running the simulator. Results go to a new output tree. `--mode rerun --study reliability --dry-run` inspects the locked matrix; omitting `--dry-run` explicitly runs the frozen wrapper in a new output directory.

## Physical and external-comparison gates

The full-text audit stops after HENO-MAC and MAoIG. Both fail faithful transfer inside the fixed executor; HENO's duty-only adaptation is conditional and is not a full independent MAC comparison. MAoIG permits estimated harvesting rates. Detailed decision witnesses, primary-source PDF hashes and bounded source searches are in `docs/paper_audit/strengthening_20261025/`.

The 20-ms Guard and 16-ms logical data airtime are separate model terms. The 500-byte logical observation needs fragmentation for IEEE 802.15.4; framing, ACK/timeouts and competing receiver arbitration are not implemented. A 17-ms configured drift/jitter/turnaround bound is checked on attempts. The recorded conservative endpoint envelope reaches 21.8358 s, below 99.98 s, with zero timing misses. This establishes the abstract execution bound only. Fixed-daylight support mismatch, normalized hardware conversions and CPU-energy omissions are detailed in the communication/energy audit. No real-MAC experiment passes the execution-model gate.
