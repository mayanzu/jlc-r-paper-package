# Published release v1.0.0

Repository: https://github.com/mayanzu/jlc-r-paper-package

Release: https://github.com/mayanzu/jlc-r-paper-package/releases/tag/v1.0.0

The checklist below describes the release procedure and later maintenance. Dates and repository identifiers are supplied in CITATION.cff and audit/github_release.json. Historical validation files retain their original timing.

# Publishing the fixed release

The local release candidate is version 1.0.0. It contains no GitHub credentials,
local Git history or embedded Git repository. The original Git-bearing execution
container is retained offline; its source payloads are distributed in a new,
explicitly identified archive. Do not upload the author workspace, offline
recovery bundles, virtual environment or installation/verification logs.

1. Run `python -B scripts/reproduce.py --mode verify` and
   `python -B -m unittest discover -s tests -v` from this repository root.
2. Publish this directory to the chosen GitHub repository. Confirm that a
   signed-out reader can open its README and download the code/data.
3. Record the actual repository URL in `CITATION.cff` (`repository-code`) and
   `audit/review_state.json` (`public_url`). Set the actual publication date in
   `CITATION.cff` (`date-released`), and record the intended immutable version/tag
   in `audit/review_state.json` before creating the release. Use an actual tag
   such as `v1.0.0`, not a placeholder DOI or an unpublished commit identifier.
4. Refresh `python -B scripts/refresh_manifest.py`, rerun verification, commit
   the metadata and create the matching fixed tag/release. The tag names the
   final commit including its checksums. Do not insert the final commit's own
   hash into that same commit; a tag or later release record can identify it.
5. Add the working repository URL and fixed release identifier to the main
   manuscript's Data and Code Availability statement and recompile that main
   article only. The repository's manuscript source mirror identifies the
   reviewed draft; update it if the manuscript changes.
6. Supply the fixed release archive to the journal and check reviewer access.
   A DOI-backed archive can be added later using its actual assigned DOI.

Do not run formal simulation matrices merely to publish this packaging revision.
The explicit `rerun` interface remains available for independent users. The
installation and saved-result reproduction environment is documented in
`environment.json` and `audit/package_validation.json`.
