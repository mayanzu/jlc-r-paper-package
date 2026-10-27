# Package rerun validation

The package's first complete technical replay used the existing seed and condition for case 0. Its latest-delivery and battery arrays and all computed metrics matched the formal record. Its saved sample-status array had 278 outstanding samples still coded as zero because the portable wrapper saved the array before the original model's end-of-run `metrics()` finalization.

The portable wrapper was corrected to call `metrics()` before saving the array and to require a status for every offered sample. A second replay with the same seed and configuration in a new directory reproduced the original arrays and every saved metric exactly; its node-ledger, cadence-plan and intentional-sleep CSVs also matched byte for byte. Both attempts and the original wrapper are retained in the offline research archive. Neither attempt changed the formal record or constitutes a new independent confirmation experiment.
