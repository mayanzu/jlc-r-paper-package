# V6.3 Stage D — Independent Confirmation Summary (`32 / 32` Noninferiority Closure)

## 1. Executive Summary

`RelayRepairHYB` (`JLC-R-HYB-V63`, `code/simulation/v63_model.py`) resolves the multi-hop relay bottleneck identified in Stage A (`P = 71.91%`, `C = 27.10%`, `P + C = 99.01%` of positive differential far-source relay losses in winter) using three parameter-free, strictly local mechanisms:
1. **Transit Protection Admission (`M-B`)**: Reserves $\text{protect}_j = \min(1, |\{u \in \mathcal{C} : j \in \mathcal{N}_u\}|)$ free guard slots and single-packet transit credit on transit CHs $j \in \mathcal{C}$ against 1-hop member admission (`i not in chset`), preventing 1-hop members from crowding out multi-hop CH-to-CH relay traffic (`C`).
2. **Uncovered Staleness Tie-Breaking (`M-A`)**: Breaks same-round uncovered packet priority ties in `choose_packet(i)` by oldest local forwarded birth (`(uncovered, gain, -previous, p.birth, -p.sequence)` instead of `(uncovered, gain, p.birth, -p.sequence)`), eliminating node-ID (`-sequence`) starvation of peripheral sources while preserving remaining-lifetime `gain` priority (`P`).
3. **Relay-Starved Cluster-Head Demand Recognition**: Because admitting and forwarding even a single multi-hop packet requires 2 guard slots (`1` RX + `1` forward-hold), any active CH whose prefix plan provides `< 2` guard slots (`runtime_cap_profiles[ph][i] < 2`) is recognized as having structural relay demand at period installation (`t % 4 == 0`), even before round-$t$ sensing occurs.

Across **both** the 12-seed V6.0/V6.2 benchmark confirmation set (`150101..151212`) **and** the brand-new 12-seed unseen V6.3 confirmation set (`160101..161212`, verified zero prior occurrences in `D_seed_search.csv`), **`JLC-R-HYB-V63` passes all `32 / 32` primary noninferiority tests** (`Holm-36 < 0.05`, `Holm-32 < 0.05`, and `Holm-33(rel) < 0.05`), all `4 / 4` winter coverage superiority tests against `JLC-R-SA` ($p_{\text{Holm}} \le 1.38 \times 10^{-11}$), and the pre-registered `WINTER_G20 1.0` Mean AoI improvement test against `HYB60` (`-488.29 min`, $p_{\text{Holm}} = 2.48 \times 10^{-7}$ on `150101..151212`; `-458.01 min`, $p_{\text{Holm}} = 1.96 \times 10^{-8}$ on `160101..161212`).

---

## 2. Winter Performance Comparison (`HYB60` vs `JLC-R-HYB-V63` relative to `PADC-AGE`)

### 2.1 V6.0/V6.2 Confirmation Seed Set (`150101..151212`, $n = 12$)

| Winter Cell | Metric | `HYB60` vs `PADC-AGE` | **`JLC-R-HYB-V63` vs `PADC-AGE`** | `Holm-36` $p$ | `Holm-33(rel)` $p$ | Verdict |
|---|---|---:|---:|---:|---:|---|
| `WINTER_G20 1.0` | Coverage (pp) | $+0.604$ | **$+1.133$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `WINTER_G20 1.0` | Mean AoI (min) | $+292.345$ (FAIL) | **$-195.944$ (`-4.61%`)** | $0.0001$ | $0.0002$ | **PASS (Reversed to Better)** |
| `WINTER_G20 1.0` | Source P5 (pp) | $-0.694$ | **$-0.456$** | $0.0035$ | $0.0035$ | **PASS** |
| `WINTER_G20 1.0` | Night-Off (pp) | $-0.642$ | **$-0.599$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `WINTER_G20 0.7` | Coverage (pp) | $+0.121$ | **$+0.297$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `WINTER_G20 0.7` | Mean AoI (min) | $-92.524$ | **$-134.910$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `WINTER_G20 0.7` | Source P5 (pp) | $-0.549$ | **$-0.312$** | $0.0002$ | $0.0002$ | **PASS** |
| `WINTER_G20 0.7` | Night-Off (pp) | $-1.842$ | **$-1.663$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `T3_G20 1.0` | Coverage (pp) | $+0.325$ | **$+0.463$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `T3_G20 1.0` | Mean AoI (min) | $-151.014$ | **$-231.758$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `T3_G20 1.0` | Source P5 (pp) | $-0.552$ | **$-0.390$** | $0.0004$ | $0.0005$ | **PASS** |
| `T3_G20 1.0` | Night-Off (pp) | $-0.916$ | **$-0.779$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `T3_G20 0.7` | Coverage (pp) | $+0.224$ | **$+0.306$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |
| `T3_G20 0.7` | Mean AoI (min) | $+19.840$ | **$+3.786$ (`+0.06%`)** | $<10^{-4}$ | $<10^{-4}$ | **PASS** |
| `T3_G20 0.7` | Source P5 (pp) | $-0.533$ | **$-0.411$** | $0.0011$ | $0.0011$ | **PASS** |
| `T3_G20 0.7` | Night-Off (pp) | $-0.680$ | **$-0.608$** | $<10^{-4}$ | $<10^{-4}$ | **PASS (Superior)** |

### 2.2 Clean Unseen V6.3 Confirmation Seed Set (`160101..161212`, $n = 12$)

| Winter Cell | Coverage vs `PADC-AGE` | Mean AoI vs `PADC-AGE` | Source P5 vs `PADC-AGE` | Night-Off vs `PADC-AGE` | All 16 Winter NI Tests |
|---|---:|---:|---:|---:|---|
| `WINTER_G20 1.0` | **$+1.134\text{ pp}$** ($p<10^{-4}$) | **$-292.034\text{ min}$** ($p=10^{-4}$) | **$-0.536\text{ pp}$** ($p=0.0014$) | **$-0.619\text{ pp}$** ($p<10^{-4}$) | **4/4 PASS** |
| `WINTER_G20 0.7` | **$+0.314\text{ pp}$** ($p<10^{-4}$) | **$-161.030\text{ min}$** ($p<10^{-4}$) | **$-0.440\text{ pp}$** ($p=0.0022$) | **$-1.687\text{ pp}$** ($p<10^{-4}$) | **4/4 PASS** |
| `T3_G20 1.0` | **$+0.501\text{ pp}$** ($p<10^{-4}$) | **$-201.396\text{ min}$** ($p<10^{-4}$) | **$-0.413\text{ pp}$** ($p=0.0005$) | **$-0.821\text{ pp}$** ($p<10^{-4}$) | **4/4 PASS** |
| `T3_G20 0.7` | **$+0.344\text{ pp}$** ($p<10^{-4}$) | **$+37.654\text{ min}$** ($p<10^{-4}$) | **$-0.309\text{ pp}$** ($p=0.0002$) | **$-0.638\text{ pp}$** ($p<10^{-4}$) | **4/4 PASS** |

---

## 3. Benign / Moderate Cells (`SYNTHETIC_G20` and `T2_G20` relative to `JLC-R-SA`)

On both `150101..151212` and `160101..161212`, all 16 benign/moderate NI tests pass (`16 / 16 PASS`), and `JLC-R-HYB-V63` improves Coverage, Mean AoI, and Source P5 simultaneously in `SYNTHETIC_G20 1.0`, `SYNTHETIC_G20 0.7`, and `T2_G20 1.0` while eliminating the `T2_G20 0.7` coverage gap (`-0.031 pp` on `150101..151212`, $p_{\text{Holm}} = 0.0001$; `-0.307 pp` on `160101..161212`, $p_{\text{Holm}} = 0.0004$).
