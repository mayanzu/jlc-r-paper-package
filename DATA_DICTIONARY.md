# JLC-R minimal evidence dictionary

This package supplies the independent 480-execution confirmation, the original
120-execution mechanism controls, the agricultural extensions and the
864-execution relay factorial. `results/index.json` identifies their exact
retained CSV paths. This dictionary describes the bundled fields.
The independent comparison unit is a seeded trajectory. Supply conditions
share seeds. No rows were excluded.

## Bundled confirmation records

`code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv`
has 480 rows: 5 methods x 8 weather-supply cells x 12 unseen seeds
(`160101..161212`, step 101).

| Field | Meaning / units |
|---|---|
| `condition`, `supply`, `seed`, `method` | Fixed configuration label, dimensionless energy multiplier, geometry/channel seed, exact policy identifier |
| `coverage_pct` | 100 x fresh source-rounds / all N*T offered source-rounds, including unsampled demands |
| `aoi_mean_minutes` | Mean end-of-round source age, all nodes and rounds; undelivered sources start at evaluation time zero |
| `source_coverage_p5_pct` | Within-run p5 across N individual-source coverage percentages |
| `night_off_pct` | Offline node-rounds / all node-rounds at synthetic clock-envelope g(t)=0; retained clock definition also used for measured input |
| `consumed_j` | Physical joules debited |
| `delivered` | Unique sampled-demand destinations delivered |
| `max_hold_violation_j`, `max_slot_violation` | Numerical audit maxima; must satisfy `<1e-8` and `==0` |

`D_confirmation_metrics_seeds15.csv` has 96 rows: JLC-R-HYB-V63 only on the
12 benchmark seeds (`150101..151212`) for head-to-head against the frozen
V6.0/V6.2 table. `D_seed_search.csv` verifies zero prior occurrences of the
12 unseen seeds across the original code, temp and git history search. This is
a retained prior-use audit record, not a new scan of an absent public history.

`C_development_metrics.csv` (32 rows) and `A_hop_fates.csv` (32 rows) are
4-seed development/attribution snapshots on `140101..140404`; they are not
independent confirmation.

## Noninferiority table

`D_noninferiority_seeds16.csv` has 32 rows: 8 cells x 4 primary metrics
against the designated strong baseline (`JLC-R-SA` in `SYNTHETIC_G20`/`T2_G20`;
`PADC-AGE` in `WINTER_G20`/`T3_G20`).

| Field | Meaning |
|---|---|
| `condition`, `supply`, `metric`, `baseline`, `seed_set` | Cell, metric, matched baseline, seed set |
| `mean_diff`, `sd_diff` | Paired mean/SD of JLC-R minus baseline (pp for coverage/P5/outage; minutes for AoI) |
| `ci95_lo`, `ci95_hi`, `ci90_lo`, `ci90_hi` | Two-sided paired t intervals (df=11) |
| `margin` | NI margin: -1.0 pp (coverage/P5), +1.0 pp (outage), +5% of baseline mean (AoI) |
| `p_raw`, `p_rel` | One-sided paired t p values under the V6.0/V6.2 mean-baseline margin and the paired relative margin (AoI); identical otherwise |
| `t_stat`, `t_stat_rel` | Corresponding t statistics |
| `p_holm32`, `p_holm36`, `p_holm37`, `p_rel_holm33` | Step-down Holm adjustments; `Holm-36` is the prespecified 32 NI + 4 superiority family |
| `pass_holm36_005`, `pass_holm36_0025`, `pass_holm33_rel_005` | Pass flags at alpha 0.05 / 0.025 |

All 32 pass under `Holm-36 < 0.05`. Noninferiority does not mean every
outcome mean is better; winter lower-tail and energy-service tradeoffs remain.

## Weather inputs

Processed 15-minute GHI means (`local_round,ghi_w_m2`, W/m2) with two warm-up
days plus one forecast-tail day included in the row count:

- `code/results/expansion_measured/weather/ghi_15min.csv` for `WINTER_G20`
- `code/results/strengthening_weather/T2/ghi_15min.csv` for `T2_G20`
- `code/results/strengthening_weather/T3/ghi_15min.csv` for `T3_G20`
- `SYNTHETIC_G20` uses the synthetic generator and no CSV.

Provenance, URLs, per-file hashes, QC, UTC-7 conversion and aggregation are in
the sibling `provenance.json` / `quality.json`. The `.12 J per 1000 W/m2`
mapping preserves the energy scale and is not a fitted panel model.

## Mechanism, agricultural and relay records

| Dataset | Rows | Independent identifiers and additional fields |
| --- | --- | --- |
| `mechanism_controls` | 120 | Five original configurations, two supplies, twelve paired seeds; base/G10. Used for six Table 3 paired contrasts. |
| `supply_576` | 576 | `condition`, `supply`, `seed`, `method`; battery means are joules, fractions and coverage fields follow their column names. |
| `freshness_480` | 480 | Fixed simulated trajectories scored at D=2/4/8/16 rounds; `coverage_D*_pct` and `source_p5_D*_pct` are percentages. These thresholds are not additional independent trajectories. |
| `canopy_384` | 384 | `canopy_treatment`, stage and lambda identify the spatial energy--link stress. `transmittance_mean` is dimensionless; `far_coverage_D4_pct` is percent. |
| `relay_ablation_864` | 864 | `condition`, `supply`, `treatment`, `seed`, `configuration`; configurations A000--A111 encode T/R/S. All eight combinations share paired seed identities. |

`generated`, `unsensed`, `delivered`, `expired`, `overflow` and `outstanding`
count offered/sensed demands and final outcomes. Where supplied,
`generated + unsensed = 134400` and
`generated = delivered + expired + overflow + outstanding`.
Energy-balance and reservation maxima are verification summaries, not complete
per-packet trajectories. `runtime_seconds` is wall-clock time and is not a
scientific reproduction equality target.

The 36-test confirmation and separate four-test relay family remain separate.
For relay primary effects, the two primary winter conditions are averaged
within each network seed before paired inference (n=12). Agricultural paired
intervals are nominal descriptive intervals. Detailed definitions and
assumptions are in `docs/technical_documentation/technical_documentation.md`.

## Figure mapping

- `assets/paper_figures/fig1_scene.*` and `fig2_flow.*` are retained structural
  figures (SVG/PDF); they are not redrawn from outcomes.
- `python -B scripts/reproduce.py --mode reproduce --output outputs/reproduction_new`
  writes current numerical tables under `tables/`, statistics under
  `statistics/`, `agricultural_statistics/` and `relay_statistics/`, and
  quantitative panels under `figures/` in that new output directory.
- Main statistical Figures 3--6 and repository R1/R2 retain their inherited
  asset stems. `configs/article_figure_map.json` and `docs/reproduction_map.md`
  give the current numbering and exact paths.
- Explicit reruns write to separate new directories. The original mechanism
  harness writes `metrics.csv`; the other unified studies write
  `rerun_results.csv`. Distributed reference records are never overwritten.
