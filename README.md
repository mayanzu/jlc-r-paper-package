# JLC-R five-method reproducibility package

This package accompanies the revised manuscript. It contains the complete RC2 controller, two common-environment external reimplementations, two internal controls, processed NOAA inputs, 480 paired seed-level records, compact node ledgers and the locked statistical families. The package version and its public access location must be matched to the manuscript at submission.

## Design and scientific scope

Five methods were evaluated over four inputs, two supply multipliers and 12 paired network seeds for 14 days. There are 480 method–condition–seed records. The Hybrid and earlier JLC-R records are 192 previously executed and checked records; RC2, EADCM-CE and LANTERN-CE add 288 later executions. These network seeds had been used in the preceding 576-execution study, so this is a **staged comparison**, not an entirely new blind confirmation. Development used separate 2023 inputs and development seeds; the selected parameters were fixed before this comparison.

The network seed is the pairing unit. Paired-t inference assumes independent seed-level contrasts and an adequate small-sample approximation; the separately reported sign-flip sensitivity assumes symmetric null contrasts. Nominal intervals are not simultaneous bands. `environment.json` records the actual software versions used for the formal execution.

`code/simulation/jlc_r.py:JLCR` is the complete controller and fixes its three settings. The exact frozen execution-source bytes, including the original V63 parent and path-dependent research wrappers, are retained or mapped in `audit/frozen_source_mapping.json`. Four source copies have import/root-discovery adaptations. Their 24 short replays cover three methods and eight conditions, using one previously used seed and 192 rounds; saved trajectories and available decision logs agree. One complete 14-day RC2 replay also matches the saved arrays, metrics and relevant CSVs after a corrected export-order issue, documented in `audit/technical_replay_history.md`. These checks do not prove every untested state is identical.

EADCM and LANTERN are independently reimplemented decision strategies in the shared simulator, with the necessary input, workload and MAC adaptations described in `docs/external_baseline_audit.md`. These results are not a reproduction of the original authors' hardware or Cooja performance. Sampling, propagation and energy use are simulated; no field validation or hardware calibration is claimed.

## Commands

```bash
python -m pip install -r requirements.txt

# Read-only: hashes, node energy and sample ledgers, four outcomes, paired tests
python scripts/reproduce.py --mode verify

# Regenerate the four manuscript tables, five figure assets, statistical
# families and 40 condition means from saved results; no simulation is started
python scripts/reproduce.py --mode reproduce

# Inspect the full rerun plan without starting a simulation
python scripts/reproduce.py --mode rerun --study confirmation --dry-run

# Explicitly rerun one recorded case into a new directory outside this package
python scripts/reproduce.py --mode rerun --study confirmation --case-index 0

# Omitting --case-index explicitly reruns all 480 cases; this is time-consuming
python scripts/reproduce.py --mode rerun --study confirmation
```

Generated directories are created beside this package by default; `--output PATH` selects a new directory outside it. An existing output is never overwritten. A rerun is a reproducibility operation using the archived seeds and settings; it does not create independent confirmation evidence. It is never started by `verify` or `reproduce`.

## What is included

- `results/confirmation_480.csv` holds each run's four main/secondary outcomes, fixed-demand sampling and delivery, actual energy, terminal counts and original record hash.
- `results/node_records_48000.csv.gz` holds 100 source coverages and mean ages plus node-level energy ledgers per run. `verify` reconstructs the network metrics and checks demand and energy conservation. These compact records do not contain every round or packet event.
- `results/statistics/` contains the archived Holm-8, Holm-64, Holm-72 and separate sign-flip Holm-8 analyses. The scripts recompute and compare them from the seed records.
- `results/reporting_sensitivity_1920.csv`, `monitoring_gaps_480.csv` and `source_degradation_384.csv` describe the same saved trajectories; they add no independent replicates or hypothesis families.
- `configs/formal_protocol_original.json` is the original pre-execution lock, including its original then-pending status. `audit/formal_closure_receipt.json` and `audit/formal_verification.json` document later completion and verification.
- `audit/` contains the execution-source mapping, migration checks and seed history. The complete original execution arrays, per-round traces and attempts are preserved offline in the research archive; they are not bundled here. Full traces may be generated through an explicit rerun.

`docs/reproduction_map.md` maps all four main tables and five figure assets to their inputs and scripts. Historical V63 agricultural, spatial and 864-factorial results remain associated with their original version and are not relabeled as RC2 evidence.

## Input attribution and licensing

The irradiance inputs are processed NOAA SURFRAD measurements. Source and quality-control provenance are in `data/surfrad/provenance.json` and the associated metadata referenced there. See `THIRD_PARTY_NOTICES.md`: the software license does not relicense NOAA data or imply NOAA endorsement.
