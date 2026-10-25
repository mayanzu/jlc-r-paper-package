# Table 3 mechanism-study reproduction

Table 3 uses the original base/G10 joint-listening and reference-floor controls:
12 network seeds, two supplies, five recorded controller configurations and a
14-day horizon (120 executions). These controls retain their original method
labels and configuration; they are separate from the S200/G20 480-execution
confirmation and the 864-execution relay factorial.

```bash
# Check exact source hashes, imports, effective parameters and all recorded case identities.
python -B scripts/reproduce.py --mode rerun --study mechanisms --dry-run

# Explicit full simulation; output must be a new directory.
python -B scripts/reproduce.py --mode rerun --study mechanisms --output outputs/mechanisms_new --workers 1
```

The wrapper starts the unchanged original `run_strengthening.py` in a separate
Python process, preventing module-name collisions with current JLC-R imports.
The 18 required modules are in `code/reproduction/mechanisms/simulation/` and
are checked against the original `source_sha256` mapping in
`code/results/strengthening/floor/provenance.json`. Only the necessary import
closure is distributed; unrelated historical runners are excluded.

The effective `config` mapping in that original provenance was serialized as
`simulation/config.json`. This is a derived configuration file, not a recovered
original configuration-file byte stream. Import checks confirm that the
original driver's configuration loader yields exactly the recorded mapping.
The design and specification retain their original bytes and hashes.

The original harness generates `metrics.csv`, `node_metrics.csv`, `resources.csv`,
input arrays, execution traces and a fresh provenance record under the new output
directory. It does not overwrite `code/results/strengthening/floor/metrics.csv`.
The reference rows and newly generated results are distinct. Numerical values
can depend on the dependency environment; wall-clock runtimes and timestamps
are not expected to match.

Packaging validation checks source hashes, imports, original case identities,
dry-run behavior and safe subprocess dispatch. It does not claim a newly
completed 120-execution matrix. Saved-result `reproduce` separately recomputes
the six current Table 3 contrasts from the retained original seed rows.
