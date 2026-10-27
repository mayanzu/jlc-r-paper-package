# Current evidence map

This map covers the revised main article and completed five-method staged comparison. `--mode reproduce` writes all four table data files and all five figure assets to a new output directory without starting a simulation.

| Evidence | Saved input | Regeneration or verification |
|---|---|---|
| All five methods across eight conditions | `results/confirmation_480.csv` | `--mode reproduce` creates `condition_means_40.csv` |
| Primary coverage and Source P5 contrasts | Seed records and `results/statistics/primary_holm8.csv` | `--mode verify` recomputes; `--mode reproduce` writes the table |
| Condition-specific primary endpoints | Seed records and `cell_primary_endpoints_holm64.csv` | The complete Holm-64 family is recomputed; `external_coverage.svg` shows coverage for both external comparators |
| Jain and AoI contrasts | Seed records and `fairness_age_holm72.csv` | The complete secondary family is recomputed |
| Primary sign-flip sensitivity | Seed records and `sign_flip_holm8.csv` | All 4096 sign patterns are recomputed, with a separate Holm-8 correction |
| Sampling, fixed-demand delivery and energy | Seed records and `node_records_48000.csv.gz` | `--mode verify` checks counts, all 48000 node balances and the 480 total energies |
| Source tradeoffs and monitoring gaps | `source_degradation_384.csv`, `monitoring_gaps_480.csv` | Saved-trajectory descriptions; not new tests or independent replicates |
| Reporting-threshold sensitivity | `reporting_sensitivity_1920.csv` | Descriptive rescoring of the same saved trajectories; original packet expiry remains D4 |
| Exact execution-source bytes and input identity | `audit/frozen_source_mapping.json`, protocol and input metadata | `--mode verify` hashes the mapped bytes and archive |
| Round arrays and method-specific logs | Original records are retained offline; an explicit rerun produces round-level latest-delivery and battery arrays, terminal sample statuses, node ledgers and applicable planning or control logs | The compact node records do not contain these detailed arrays or a complete packet-event trace |

| Main item | Generated file or source | Meaning |
|---|---|---|
| Table 1 | `table1_effective_parameters.csv` | Full effective settings behind the compact parameter table |
| Table 2 | `table2_methods.csv` | Five method identities and common-model adaptations |
| Table 3 | `table3_primary_contrasts.csv` | Equal-condition paired primary effects and Holm-8 decisions |
| Table 4 | `table4_tradeoffs.csv` | Equal-condition sampling, fixed-demand delivery, energy and Jain means |
| Figure 1 | `figure1_core.svg` / `.pdf` | Retained diagram of the inherited transaction core; cadence and recovery are described in the article |
| Figure 2 | `aggregate_effects.svg` / `.pdf` | Equal-condition coverage and Source P5 paired contrasts |
| Figure 3 | `external_coverage.svg` / `.pdf` | Condition-specific coverage contrasts with the two external methods |
| Figure 4 | `sampling_tradeoff.svg` / `.pdf` | Sampling completion and fixed-demand delivery |
| Figure 5 | `service_boundary.svg` / `.pdf` | Observed longest-gap P95 and Jain difference against LANTERN |

Figure 3 shows the 16 condition-level coverage contrasts against EADCM and LANTERN; its adjusted decisions still use all 64 tests in the family. Error bars are nominal paired 95% intervals. A hollow marker indicates Holm-adjusted p ≥ 0.05. The results are not field measurements. Figure 5's gap metric is descriptive, includes boundary-censored intervals and reuses the same network seeds.
