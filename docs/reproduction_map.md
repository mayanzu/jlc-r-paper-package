# Paper-to-evidence reproduction map

Run the commands below from this repository root. Verification and saved-result reproduction do not call simulation entry points. The frozen source, input and seed-level evidence retain their original bytes.

| Article item | Retained evidence or definition | Output / verification |
| --- | --- | --- |
| Main Table 1 / extended E1 | `code/simulation/current_design.json`, `config.json`, and manuscript parameter definitions | `tables/Table1_parameters.csv`; compared with executed configuration. |
| Main Table 2 | Frozen confirmation, JLC-R rows and primary NI decisions | `tables/Main_Table2.csv`; all eight rows cross-checked with the independently verified full E2. |
| Extended Table E2 | `code/experiments/v6_3_relay_repair/D_confirmation_metrics_seeds16.csv` (480 rows) | `tables/Table2_confirmation.csv`, `statistics/primary_holm36.csv`; all 32 NI decisions and four winter comparisons recomputed. |
| Extended Table E3 | `code/results/strengthening/floor/metrics.csv` | `tables/Table3_recomputed_components.csv`; six raw-seed paired budget contrasts. Explicit original-study rerun: `--mode rerun --study mechanisms`. |
| Main Table 3 / extended E4 | `code/experiments/v6_5_relay_ablation/results/formal_runs.csv` (864 rows) | `tables/Table4_primary_relay_tests.csv`; all four independent primary contrasts and Holm-4. |
| Extended Table E5 | Same 864 rows, primary winter conditions | `tables/Table5_relay_factorial.csv`; eight configurations, two conditions averaged within each seed. |
| Extended Table E6 | `code/experiments/v6_4_agricultural_extension/results/supply.csv` (576 rows) | `tables/Table6_supply.csv` and regenerated supply summaries. |
| Extended Table E7 | Same results directory, `freshness.csv` (480 rows) | `tables/Table7_freshness.csv`; fixed trajectories scored at four age thresholds. |
| Main Table 4 / extended E8 | Same results directory, `canopy.csv` (384 rows) | `tables/Table8_canopy.csv`; the executed spatial energy--link stress. |
| Main Table 5 / E10 | 144 delivered-birth matrices in `code/experiments/v6_4_agricultural_extension/results/reliability_20261025_raw/` | `reliability/Main_Table5_recomputed.csv`, `reliability/reliability_summary.csv`; independent rescoring and all displayed cells checked. |
| E9 parameter evidence | `docs/paper_audit/strengthening_20261025/parameter_evidence_20261025.csv` | Evidence class, exact input and calibration boundary for all nine entries. |
| Main Figure 1 | `assets/paper_figures/fig1_jlcr_flow.*` | Updated vector method schematic; section references are 3.3/3.4 and planning equations 11--15. The example topology remains in `assets/paper_figures/fig1_scene.*`. |
| Figure 2 | Confirmation raw-seed means and paired comparisons | `figures/fig4_cross_regime.pdf`; inherited asset stem retained. |
| Figure 3 | Relay raw-seed outcomes and paired primary effects | `figures/fig5_relay_ablation.pdf`. |
| Figure 4 | Supply raw-seed outcomes | `figures/fig5_supply_scan.pdf`. |
| Figure 5 | Spatial-stress raw-seed outcomes | `figures/fig7_canopy.pdf`. |
| Repository Figure R1 | Confirmation raw-seed effects and confidence intervals | `figures/fig3_confirmation.pdf`; companion to main Table 2. |
| Repository Figure R2 | Freshness paired comparisons | `figures/fig6_freshness.pdf`; companion to extended Table E7. |
| Appendix A exact statements and sketches | Main article | Six original statements and their hypotheses are hash-checked (normalizing only Theorem 1's updated section reference) against the complete repository derivations. |
| Complete proofs and resource transitions | `docs/analytical_proofs.md` | Byte-preserved complete derivations; transition table checked against technical Table S69. |
| Normalized energy transfer assumptions | `docs/energy_scale.md` | Common scaling, numerical tolerances and the 4.10/9.14-day calculations. |

```bash
python -B scripts/reproduce.py --mode verify
python -B scripts/reproduce.py --mode reproduce --output outputs/reproduction_new
python -B scripts/reproduce.py --mode rerun --study confirmation --dry-run
python -B scripts/reproduce.py --mode rerun --study mechanisms --dry-run
python -B scripts/reproduce.py --mode rerun --study relay_ablation --dry-run
```

`configs/article_figure_map.json` gives current article/repository figure labels; statistical asset stems are unchanged and the corrected schematic has a distinct source name. `docs/repository_figures.md` displays R1--R2 directly. Statistical Figures 2--5 and R1--R2 are regenerated from raw seed-level outcomes before plotting; the distributed summary tables are reference records.

The NOAA source/QC metadata are in `data/surfrad/provenance.json`. Necessary prior seed use remains in `audit/seed_registry.csv`; independence is defined at the network-seed level. The 36-test confirmation and four-test relay families are separate; agricultural extensions report nominal descriptive paired intervals.

The exact G10 runner dependencies and effective configuration are documented in [mechanism_reproduction.md](mechanism_reproduction.md). The source-archive derivation is recorded in `audit/source_snapshot_provenance.json`. Publication status is in `audit/review_state.json`; the fixed-version publication steps are in [release_checklist.md](release_checklist.md).

Full extended E1--E8 are in Part IV of `docs/technical_documentation/technical_documentation.md`. `Main_Table1.csv` through `Main_Table5.csv` follow current article numbering; existing `Table1_...` through `Table8_...` output filenames retain their original identities and map to E1--E8 above. All complete numerical displays continue to be recomputed or independently checked.

New recording seeds are in `audit/reliability_20261025_seed_registry.csv`, separate from the unchanged original seed registry. Part V of the technical source records E9--E10 and limitations. Explicit rerun: `python -B scripts/reproduce.py --mode rerun --study reliability --output outputs/reliability_new`.
