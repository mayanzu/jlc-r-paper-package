# JLC-R COMPAG minimal reproducibility package

Repository: [https://github.com/mayanzu/jlc-r-paper-package](https://github.com/mayanzu/jlc-r-paper-package). Fixed release: [v1.0.0](https://github.com/mayanzu/jlc-r-paper-package/releases/tag/v1.0.0).

This repository
contains the frozen JLC-R source, necessary configuration, processed SURFRAD
inputs, seed-level final outcomes, statistical/plotting tools and technical
documentation for the current COMPAG manuscript.

The package supports the 480-execution confirmation, the agricultural supply
(576), freshness (480) and canopy (384) studies, and the independent 864-case
T/R/S factorial. Recorded method identifiers and physical inputs retain their
original bytes. The public JLC-R entry is `code/simulation/jlc_r.py:JLCR`,
implemented by `v63_model.py:RelayRepairHYB` (`JLC-R-HYB-V63`). Required parent
modules retain their names and bytes. The isolated original G10 mechanism-study
dependencies support extended Table E3 and are not another JLC-R release.

**Reproduction scope:** the supplied frozen configurations and seed-level records support the current main numerical Tables 1--5, complete extended Tables E1--E8 and statistical Figures 2--5, plus repository Figures R1--R2. Complete derivations are in `docs/analytical_proofs.md`; energy scaling is documented in `docs/energy_scale.md`. See [reproduction_map.md](docs/reproduction_map.md) for data and command mappings.

## Install

Python 3.12 was used locally. All numerical inputs are supplied; verify and
reproduce do not need a network connection, API key or TeX installation.

```bash
python -m pip install -r requirements-lock.txt
```

`requirements-lock.txt` pins the tested environment, including transitive
dependencies. `requirements.txt` lists the direct minimum requirements. LaTeX and
Pandoc are optional tools only for compiling the editable technical-document
source; they are not needed for the commands below.

## Three explicit modes

```bash
# Hashes, seed-level resource ledgers, primary statistics and table consistency.
# No simulation.
python -B scripts/reproduce.py --mode verify

# Main Tables 1-5, full extended Tables E1-E8, main statistical Figures 2-5 and repository Figures R1-R2.
# No simulation; outputs never overwrite distributed evidence.
python -B scripts/reproduce.py --mode reproduce

# Inspect matrices and frozen hashes without executing a simulation.
python -B scripts/reproduce.py --mode rerun --study confirmation --dry-run
python -B scripts/reproduce.py --mode rerun --study mechanisms --dry-run
python -B scripts/reproduce.py --mode rerun --study relay_ablation --dry-run

# Explicit full simulation reruns; these can be computationally expensive.
python -B scripts/reproduce.py --mode rerun --study confirmation --output outputs/confirmation_new
python -B scripts/reproduce.py --mode rerun --study mechanisms --output outputs/mechanisms_new
python -B scripts/reproduce.py --mode rerun --study relay_ablation --output outputs/relay_new
python -B scripts/reproduce.py --mode rerun --study agricultural_extension --output outputs/agricultural_new
```

The agricultural tasks can also be selected separately as `supply`, `freshness`
or `canopy`. `--workers` defaults to one. Rerun rejects existing output directories
and paths inside frozen package inputs. It uses the original source/configuration
and the exact recorded case identities. Newly generated results remain separate
from the distributed reference CSVs. This packaging revision validated verify,
saved-result reproduce and rerun dry-runs; it did not rerun the original formal matrices. A separate 144-case post-confirmation recording study was executed, with its own protocol, seeds, raw traces and descriptive intervals.

The `mechanisms` study runs the original 120-case base/G10 extended Table E3 design in a
separate process. Its 18 necessary source modules match the original execution
provenance. The effective configuration is serialized from that provenance and
checked for exact parameter equality before dispatch. See
[mechanism reproduction](docs/mechanism_reproduction.md). This command writes
`metrics.csv`, resource records and detailed logs into its new output directory.


In the author's local workspace, default generated outputs go to project
`JLC-R/temp/minimal_reproduction/`; in an independent checkout they go to
`outputs/`. Use `--output` to choose a new directory. The root `reproduce.py`
and `verify_package.py` remain safe compatibility entries: neither starts an
implicit smoke simulation.

## Evidence and audit

- [Result index](results/index.json) maps friendly study names to unchanged file paths.
- [Reproduction map](docs/reproduction_map.md) maps every main table/figure to data and commands.
- [Technical documentation](docs/technical_documentation/README.md) retains S63, S67, S68 and proofs.
- [External-baseline audit](docs/technical_documentation/external_baseline_audit.md) states the HENO-DC/MAoIG comparison limits.
- [Seed registry](audit/seed_registry.csv) preserves formal, reused and development identities.
- [Frozen-record hashes](audit/original_record_hashes.json) and [distribution checksums](audit/checksums.sha256) serve different purposes: numerical/kernel immutability and the complete current package.
- [Source snapshot provenance](audit/source_snapshot_provenance.json) records the 47 byte-preserved source/input/plan payloads in the public execution archive. Embedded Git metadata is omitted; the original container is preserved offline with its original hash.

`.gitattributes` disables Git line-ending normalization for this distribution,
so cloning or staging on Windows preserves the frozen checksum identities.

The original 36-test Holm family and the separate relay Holm-4 family are not
pooled. Noninferiority does not imply every outcome mean improves. Field energy,
propagation, MAC and agronomic validity remain untested calibration requirements.

The public package excludes development branches, failed candidates, historical complete
per-packet/per-round logs, duplicate execution outputs, prior manuscript PDFs,
TeX caches, virtual environments and the full `technical_history/` archive.
These remain in the author's offline project `temp/`, not in the public package.
Essential prior seed use is retained even when those development outcomes are
not public. A provenance hash for an absent historical log is not a fresh audit
of that log. Resource verification here checks the supplied seed-level maxima
and demand ledgers; explicit reruns can generate new detailed logs.

The saved-result reproduction pipeline recomputes agricultural summaries,
paired effects and factorial plot inputs from seed-level CSVs before drawing
the figures. The distributed derived summaries remain reference records.

Software licensing is in [LICENSE](LICENSE); third-party data rights are separate
and described in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Main figure numbers and retained asset names are mapped in
`configs/article_figure_map.json`; asset stems remain unchanged to preserve
execution provenance. For the local release candidate, publication status and
version fields are recorded in `audit/review_state.json`. Use the fixed release/tag to identify this snapshot. Follow the
[release checklist](docs/release_checklist.md) when publishing the fixed version.

Packaging regression checks can be run with
`python -B -m unittest discover -s tests -v`; they do not execute a performance
matrix or alter distributed evidence.

## Independent monitoring-availability recordings

The added `reliability_20261025` study comprises 144 executions: twelve new paired seeds, four unchanged controllers, T1/T3 at supply 0.7 and T2 at supply 1.0. Its raw 1,344-by-100 delivered-birth matrices are deliberately retained because continuous outages cannot be inferred from seed-level coverage or mean age. This is post-confirmation exploratory evidence; neither original Holm family is expanded. It supplies main Table 5 and technical E10. E9 classifies parameter evidence.

The standard verify/reproduce modes include independent matrix rescoring. Outputs include `reliability/Main_Table5_recomputed.csv` and the complete nominal paired summaries. Rerun remains explicit:

```bash
python -B scripts/reproduce.py --mode rerun --study reliability --dry-run
python -B scripts/reproduce.py --mode rerun --study reliability --output outputs/reliability_new
```

Every winter source experienced a gap longer than four hours; the JLC-R spring proportion was 48.25%. Tail-gap differences from JLC-Core remain unresolved. Horizon-censored gaps and completed-only recovery are reported together. These outcomes do not establish irrigation, frost-detection or yield performance. New seed usage and full-text external/MAC gate decisions are indexed in `audit/reliability_20261025_seed_registry.csv` and `docs/paper_audit/strengthening_20261025/`. The fixed public release is [v1.0.0](https://github.com/mayanzu/jlc-r-paper-package/releases/tag/v1.0.0). No DOI has been assigned.

## Obtain and cite this release

Use the v1.0.0 release archive or clone the v1.0.0 tag. `main` is the current distribution; the tag identifies the manuscript snapshot. `CITATION.cff` supplies software citation metadata. The software is MIT-licensed; processed NOAA inputs retain the provider attribution and terms in `THIRD_PARTY_NOTICES.md`. The release archive includes `audit/checksums.sha256` and `SNAPSHOT_MANIFEST.sha256`; run the verify command after downloading.

Publication makes the code and evidence accessible. It does not resolve the limited incremental effects, missing second complete external-protocol comparison, or unvalidated field/MAC behavior documented above. Earlier GO wording in the local preparation audit refers to numerical/file readiness; it is not a scientific recommendation to submit immediately.
