# External baseline audit for the staged comparison

Both methods below are decision-strategy reimplementations in the common transaction simulator. They receive the common deployment, energy inputs, propagation and task, and pay the model's actual sensing, synchronization, listening, control, data, failure and retry costs. CPU computation and hardware startup transients are not modeled for any method. Neither implementation claims to reproduce the original authors' complete hardware or network-stack results.

## EADCM: energy management

M. Gerndt, M. Ispir, I. Nunez and S. Benedict, “Energy-Aware Duty Cycle Management for Solar-Powered IoT Devices,” *Sensors* 25(14), 4500 (2025), https://doi.org/10.3390/s25144500. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC12300125/. No author implementation was located.

`code/simulation/eadcm_policy.py` retains the multi-day checkpoints, backward daily search, storage and terminal-charge constraints; `eadcm_host.py` implements daily updates and charged activity/sleep. The original single-device duty decision is paired with common fixed-reference FIFO multihop transport. One causal day forecast is repeated over a five-day horizon; application activity is quantized to one of 1/2/3/4 macro-rounds. The common battery has finite capacity and no separately modeled charge-rate limit. Previous completed work estimates application energy; an initial analytic common-load estimate is used before observations exist. These adaptations may change the policy's observed performance and do not establish a physical terminal-charge guarantee.

The development search compared horizons 3 and 5 days with a 20% target, using 2023 development inputs and previously used development seeds. Selection used the external method's own coverage, then P5, then lower age; the five-day setting was fixed before the final staged comparison. This method was retained as a compatibility exception to the preferred CCF journal range; *Sensors* is not represented here as CCF network category C.

## LANTERN: energy-aware multihop routing

Hossein Taghizadeh, Bardia Safaei, Amir Mahdi Hosseini Monazzah, Elyas Oustad, Sahar Rezagholi Lalani and Alireza Ejlali, “LANTERN: Learning-Based Routing Policy for Reliable Energy-Harvesting IoT Networks,” *IEEE Transactions on Network and Service Management* 21(6), 6542–6554 (2024), https://doi.org/10.1109/TNSM.2024.3450011. Publisher record: https://ieeexplore.ieee.org/document/10648748/. The accessible author manuscript was audited; no author code was located.

`lantern_policy.py` implements the energy metric, Q updates and power hysteresis; `rpl_upward.py` implements parent choice, epsilon exploration and upward RPL state; `rpl_trickle.py`, `causal_meter.py` and `router_mac.py` implement the corresponding common-executor timers, causal rate measurements and charged logical MAC. Dynamic parent selection is retained. The original 10-second energy input is adapted to rates estimated from the preceding completed 900-second round; future irradiance and future charge are unavailable. The comparison uses upward RPL/MOP0, explicit logical DIO/DIS/RPI sizes and a common serialized-MAC abstraction, not a complete Contiki/IPv6 wire stack.

In the author manuscript, the remaining-energy reward uses the negative reserve term in the equation and Algorithm 2 line 24; a conflicting line 9 parenthetical is documented by choosing the consistent equation/line-24 form. The root reward, Trickle redundancy and uniform listening were tested on development data. The bounded final candidate set used rewards C, 2C, 4C and 8C; redundancy 1, 3 and 10; and two listening budgets. The final 8C = 32 reward, redundancy 1 and 0.56-second listening were selected using LANTERN's own coverage, P5, age and control cost before reading final comparison effects. The root reward is a learning reward, not a physical energy grant.

## Two internal controls

`v6_model.py:HYBSimulator` is the base hybrid control. `v63_model.py:RelayRepairHYB` is the earlier JLC-R control and retains its original Guard and T/R/S mechanisms. The complete RC2 candidate adds bounded recovery, demand-triggered Guard protection and member activity cadence. These are progressive bundle comparisons; they do not separately identify the effect of each added mechanism.
