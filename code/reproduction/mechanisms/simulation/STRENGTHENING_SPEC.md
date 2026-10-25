# V3 fixed paired extensions (2026-10-22)

The design is fixed before extension outcomes. No new algorithm or protocol
stack is introduced. Seeds are reused paired extensions, not new independent
confirmation. Independent statistical unit is a network seed within one
weather/supply cell; no pooling of trajectories or treating nodes as replicates.

E5-Floor: 14 days, original physical configuration, synthetic input, supplies
1.0/0.7, seeds 70101+101k (k=0..11). Five arms: fixed, continuous without floor,
continuous with floor, integer/local-age with floor and without floor. The two
floor pairs differ only in the floor flag. All 120 runs are rerun because the
original Table 1 run records are absent from the distributed current package.
Primary family: four coverage differences (with minus without floor, two modes
by two supplies), paired t intervals and Holm p values. Secondary metrics are
descriptive paired estimates with nominal intervals.

E2-JointSync: 14 days, seeds 140101+101k, synthetic and original winter input,
supplies 1.0/0.7, guards 10/20 ms, six arms JLC-R-SA/JLC-R/POINT-JL/PADC-AGE/
PADC-DC/JLC-R-FIXED: 576 runs. Twelve debug runs use 150101/150202, three arms,
two guards, synthetic and supply 1.0; they are excluded from inference. Primary
family: JLC-R-SA minus PADC-AGE coverage, four G20 weather/supply cells, Holm.
All G10, other controls and other metrics are secondary sensitivity analyses.

Nine 20 ms windows begin at 0,100,...,800 s. Planner reserves nine, executor
charges only affordable windows from preharvest storage. Scheduled work is
reserved first; original sync is subtracted from scheduled cost and charged
once as window zero. All nine are required for traffic and fresh telemetry.
Offline nodes incur off-mode power and no nonexistent sync cost; partially
completed windows remain paid and the node is unavailable for traffic. No
within-round harvest is available. Abstract sequential traffic is confined to
[800.02,900) s with a checked sum-of-endpoint-airtime envelope. Timing checks
use conservative 100 s drift age, keyed uniform +/-8 ms jitter, endpoint biases
uniform +/-20 ppm, and 1 ms detection/turnaround. These are fixed model stress
assumptions, not calibrated hardware parameters. Clock is the same for every
controller. Sink clock bias is zero. Timing misses use paid timeout semantics.
This is a synchronization-aware execution stress test, not a complete MAC.

Scheduled listening caps 100/1000 ms include the original 20 ms; extra eight
windows are separate. Maximum guard slots are member 8/4 and CH 98/49 for
G10/G20. Typical member reference remains two slots, 40/60 ms. Continuous
floor(a*Kref) and integer planning are intentionally distinct. Role-level
resource means and reference-capacity histograms include all node-rounds;
available capacities count online nodes. planned_credit_j is the period amount
sampled each round; released_credit_j is the per-round quota. PADC has a
nonbinding permission allocation, not a JLC-R communication budget.

E1-MultiClimate: unchanged predictor and energy conversion, T1 Table Mountain
Jan 1-17 2024, T2 Table Mountain Apr 1-17, T3 Bondville Jan 1-17; local standard
time, first two days warmup, next fourteen scored, last day forecast tail.
Same network seeds as E2, G20 sync model, four arms JLC-R-SA/PADC-AGE/POINT-JL/
JLC-R-FIXED, supplies 1.0/0.7. T1's 96 trajectories are reused exactly from E2;
192 new runs for T2/T3. Primary family: four new-trajectory coverage comparisons
JLC-R-SA minus PADC-AGE (two trajectories by two supplies), Holm. T1 is already
in the E2 family, never a second independent test or execution. Three fixed
weather trajectories supply limited transportability evidence, not 36 climates.

All planned outcomes are retained. Inputs and execution snapshots are preserved
locally; compact CSVs, config hashes and verification are delivered. Statistics
are generated from seed rows. No parameter tuning after outcomes is permitted.
