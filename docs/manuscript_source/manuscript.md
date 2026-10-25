---
title: "Joint Listening-Credit Planning and Relay Protection for Fresh Data Collection in Solar-Powered Agricultural Sensor Networks"
date: ""
lang: en-US
authors: [{"name": "Zhongjun Ma", "email": "041103@mail.slu.edu.cn", "corresponding": true, "affiliations": ["aff1", "aff2"]}, {"name": "Huiqing Jin", "email": "jin@mail.slu.edu.cn", "affiliations": ["aff1", "aff2"]}]
affiliations: [{"id": "aff1", "organization": "Anhui Provincial Key Laboratory of Transportation Information and Safety, Anhui Sanlian University", "city": "Hefei", "postcode": "230601", "state": "Anhui", "country": "China"}, {"id": "aff2", "organization": "Faculty of Intelligent Transportation, Anhui Sanlian University", "city": "Hefei", "postcode": "230601", "state": "Anhui", "country": "China"}]
---

# Abstract

Solar-powered agricultural sensor networks must divide finite energy between listening and multihop forwarding. Uncoordinated allocations can purchase reception capacity without funding the resulting relay work. We propose Joint Listening-Credit and Reservation (JLC-R), which couples integer listening and communication budgets with charged admission, one-hop forwarding holds and local staleness ordering. A demand-gated reactive branch handles infeasible or thin prefix plans under the same physical accounting. Separate twelve-seed budget controls attribute 13.70--16.97 percentage-point (pp) coverage gains to listening--credit coupling and credit floors. Across synthetic inputs and three NOAA SURFRAD irradiance trajectories, a 480-execution confirmation satisfies all 32 noninferiority criteria under Holm-36 and improves winter coverage over Prefix-only by 2.730--4.609 pp. Relative to the core two-branch controller, mean coverage gains are 0.10--0.53 pp, with up to 2.11 pp higher Source P5 and 458 min lower mean age. A separate 864-execution factorial supports bundle far-source coverage and staleness-ordering effects, while standalone transit-margin and two-slot-recognition effects remain unresolved. An additional 144-execution recording study finds shorter tail unavailability than Prefix-only but no resolved tail advantage over the core controller; every winter source and 48.25% of spring sources experience an observed freshness gap exceeding four hours. Supply and spatial-stress studies distinguish improved allocation from adequate absolute service. This simulation-only evaluation provides reproducible resource and availability evidence for subsequent field calibration of energy, propagation and reporting requirements.

**Keywords:** agricultural wireless sensor networks; solar energy harvesting; information freshness; joint resource scheduling; multihop relay protection

# 1 Introduction

Agricultural wireless sensor networks collect soil and microclimate observations from spatially distributed locations [@agri_ml2022; @agri_iot2024]. Solar-powered sensing cells and vineyard stations demonstrate the value of unattended monitoring [@horticulture_wsn2009; @solar_soil_cell2009; @matese2009nav]. Energy harvesting reduces battery maintenance but introduces weather-dependent service constraints [@kansal2007; @battery_survey2023; @eh_review2025]. Recent agricultural field studies report temporal variation in wireless soil-moisture relationships and sensitivity of near-soil RF links to water content, antenna height and vegetation [@kaiser2025wireless; @baumbauer2025rfid]. For periodic collection, timely information from peripheral locations matters alongside network averages: an observation must first be received and then traverse resource-limited relays before reaching the field gateway.

This creates a coordination problem. Listening buys a finite number of reception opportunities, while every admitted observation creates a subsequent forwarding obligation. A large listening budget can leave too little energy for forwarding; reducing listening also removes transaction capacity. Several senders can overcommit the same receiver, and an unfunded FIFO head can block a funded packet. Even a resource-safe schedule can repeatedly neglect particular sources. The question is therefore how to coordinate paid listening, communication credit and forwarding commitments within one controller.

Harvest prediction and uncertainty-aware budgeting improve the information available for workload decisions [@solar_prediction2023; @uncertainty2023; @conformal2024]. Their deployment assumptions vary, including indoor photovoltaic management [@harvar2024] and dependency-aware task scheduling [@scheduler2022]. They do not by themselves ensure that a multihop receiver retains resources for the work created by reception.

Duty-cycled protocols coordinate radio availability through routing-aware schedules, receiver initiation, preambles, repeated transmissions or synchronized hopping [@rmac2007; @rimac2008; @xmac2006; @contikimac2011; @tsch2015]. PADC-MAC and HENO-MAC adapt activity to harvesting [@padc2023; @heno2024], and finite-queue models connect energy to end-to-end response time [@blondia2022]. These approaches motivate a common charged execution model in which listening, failed requests and future forwarding compete for finite resources. The PADC duty rule provides the external control used here; its transfer does not reproduce the original MAC.

Age of information (AoI) distinguishes delivered traffic from useful updates [@aoi_survey2021]. Energy-harvesting policies address multisource updating, on-demand caches, incomplete battery information and slot constraints [@timely2022; @ondemand2022; @partial2025], while online scheduling [@lyapunov2023] and learning-based transmission, runtime allocation and networking address related decisions [@fresh_learning2022; @imitation2022; @networking2024]. Optimized clustering and learned routing offer another coordination layer [@qpsodrl2026]. Here, role rotation and next-hop scoring are shared across methods so that the comparisons isolate listening, credit and relay service. Source-level freshness exposes persistent gaps that aggregate delivery can conceal.

We propose JLC-R, a two-branch controller. Its prefix plan jointly funds integer listening and communication; a local demand gate selects a PADC-based branch when the plan is unavailable or thin. Both branches use charged admission, atomic forwarding holds, upstream transit screening and source-staleness ordering. No branch receives future weather, future decoding outcomes or global sink age.

The contributions are: (i) a unified listening--credit and forwarding-reservation formulation with explicit execution-safety conditions; (ii) a three-tier evaluation—budget coupling, complete-controller confirmation and incremental relay-bundle effects—using twelve-seed independent confirmation and a separate relay factorial; and (iii) supply, freshness and spatial-stress analyses relating relative performance to absolute monitoring feasibility. The study establishes a simulation-based resource-coordination framework that defines the calibration targets for hardware energy, MAC realization and agronomic service requirements.

# 2 Network and Resource Model

## 2.1 Periodic collection

The network contains 100 sensors in twelve geographic cells over a $300\,\mathrm m\times300\,\mathrm m$ field and an externally powered boundary sink. Five predetermined candidates per cell rotate as cluster heads (CHs); members use reachable CHs, and CHs forward toward lower sink-cost ranks. The common configured backbone substitutes a feasible reference phase when needed (occurring in 7 of the 60 seed--phase combinations across the 12-seed, five-phase confirmation runs). Per-packet processing preserves source identity and birth time; there is no packet aggregation. Table 1 specifies the common workload and resources.

Each round lasts $\Delta t=900$ s. Every source offers one 4000-bit sample with a four-round expiry deadline; unsampled demand remains in the service denominator. The planning period is $T_L=4$ rounds and horizon $H=96$. Base and communication costs precede end-of-round harvesting. Candidate links have $d_{ij}\le R_{comm}$ and decoding probability

$$
p_{ij}=0.97-0.25\left(\frac{d_{ij}}{R_{comm}}\right)^2. \qquad (1)
$$

This controlled profile represents distance-dependent packet loss, without collisions or foliage propagation. At most three decoding attempts are allowed per current hop per round. Outcomes are keyed by seed, round, link, sample and attempt, preventing policy-dependent random-number consumption from changing the channel.

## 2.2 Harvesting and physical expenditure

Synthetic daylight and harvested energy are

$$
g(t)=\begin{cases}\sin\!\left(\pi[u(t)-6]/12\right),&6\le u(t)<18,\\0,&\text{otherwise}.\end{cases} \qquad (2)
$$

$$
H_i(t)=s\,\phi_iH_{peak}g(t)w(t). \qquad (3)
$$

where $s$ scales supply, $\phi_i\sim U[0.7,1]$ is fixed local shading, and $w(t)$ includes correlated clear/cloudy weather and a low-supply episode on days 5--7. Measured irradiance is converted using $H_i=s\phi_i(0.12)(\overline G_{GHI}/1000)$ J/round. The synthetic template, cloud states and low-supply episode are common across controllers; measured trajectories use the NOAA SURFRAD records described in Section 4.1. Battery evolution is

$$
B_i(t+1)=\min\{B_{max},B_i(t)-E_i(t)+H_i(t)\}. \qquad (4)
$$

Every debit must be affordable. Capacity spill is recorded. Communication and forwarding holds respect $B_{reserve}$, whereas affordable base tasks may reduce the battery below that reserve. Restart requires both 0.08 J and affordable current base tasks. The peak $0.12$ J/round corresponds to a derived effective charging power of 0.133 mW at the reference irradiance. The 4-J capacity and 3-J initial energy are normalized simulation settings, without an assigned commercial panel or storage device. They do not establish a panel area, capacitor specification or deployment lifetime. Published agricultural platforms use different supply and storage configurations [@sat_tomato2022; @sat_sugarcane2026; @sat_solar2025]. The 56-mW radio-on input is of the order of the CC2420's 18.8-mA receive current at an assumed 3 V, but is not a measurement of the proposed node [@cc2420_datasheet]. The transmit-burst current in [@sat_node2026] describes another device and radio state. Parameter evidence distinguishes model settings, manufacturer specifications and arithmetic conversions.

The logical-packet energy model follows first-order clustered-network accounting [@leach2002], including a 5% transmit-electronics overhead:

$$
E_{Tx}(l,d)=\begin{cases}l(1.05E_{elec}+\varepsilon_{fs}d^2),&d<d_0,\\l(1.05E_{elec}+\varepsilon_{mp}d^4),&d\ge d_0,\end{cases}\quad d_0=\sqrt{\varepsilon_{fs}/\varepsilon_{mp}}. \qquad (5)
$$

$$
E_{Rx}=lE_{elec},\quad E_{sense}=lE_{sense,unit},\quad E_{proc}=lE_{proc,unit}. \qquad (6)
$$

For a modeled control message of $l_c=64$ bits, request and response costs are

$$
F_{ij}^{send}=\frac{l_c}{l}E_{Tx}(l,d_{ij})+l_cE_{elec},\quad F_{ij}^{recv}=\frac{l_c}{l}E_{Tx}(l,d_{ji})+l_cE_{elec}. \qquad (7)
$$

Each intersensor request and response consumes one prepaid endpoint transaction and its modeled control energy. Each fee combines a transmit cost and a fixed receive allowance; failed requests retain incurred fees. A separate ACK frame and failure-timeout radio state are not simulated. Decoding failure consumes transmission/reception energy; processing is charged only after successful decoding. Sink delivery bypasses intersensor admission. Paid listening provides

$$
K_i=\max\left\{0,\left\lfloor\frac{\tau_i-\tau_{sync}}{\tau_{guard}}\right\rfloor\right\}. \qquad (8)
$$

transactions, where $\tau_{sync}=\tau_{guard}=20$ ms. The primary configuration (denoted S200/G20, with 200-s synchronization intervals and 20-ms guard windows) pays five synchronization windows per round; member/CH listening caps leave at most 4/49 transactions. Serialization, endpoint airtime and information exchange are modeled costs, not a deployed collision-free MAC.

# 3 Joint Listening-Credit and Reservation

## 3.1 Causal information and forecasts

At each planning epoch, nodes know configured roles, geometry, link probabilities and reference loads, their own battery/queue, and charged neighbor broadcasts. The powered gateway supplies completed weather observations through the synchronization service. The simulator uses the spatial median across nodes at completed daylight rounds with $g(\tau)>0.1$:

$$
z_\tau=\operatorname{median}_i\frac{Y_i(\tau)}{s\phi_iH_{peak}g(\tau)},
$$
where $Y_i(\tau)=H_i(\tau)$ denotes the realized harvest of node $i$ at completed round $\tau$. An EWMA updated only from eligible observations is

$$
m_t=\beta m_{t-1}+(1-\beta)z_{t-1},\quad\beta=0.7. \qquad (9)
$$

It is initialized at $m_0=0.65$ after a two-day warm-up. The issuance-time scenario bank is

$$
\widehat H_i^m(t+h\mid t)=s\,\phi_iH_{peak}\,g(t+h)\,\operatorname{clip}\!\left(m_t-\delta_h^{(m)},\,\underline{w}_m,\,1.15\right), \qquad m\in\{1,\ldots,M\}, \qquad (10)
$$

with four paths: a point path ($\delta_h^{(1)}=0$, lower bound 0.05), two cyclic block samples from at most 192 completed daylight residuals $\xi_\tau=m_\tau-z_\tau$, and a nonnegative empirical 0.9 residual quantile; stress-path lower bounds are zero. Positive residuals reduce forecast supply. This bank provides heuristic conservatism, not calibrated probability coverage. At night the estimator retains its state. The modeled reliable information service is covered by synchronization and broadcast charges; its physical realization remains to be tested.

![JLC-R planning and charged relay execution.](figures/fig1_jlcr_flow.svg){width=100%}

Figure 1. JLC-R planning and charged relay execution.

**Figure note.** The credit-period plan and demand-gated PADC branch share the same integer Guard resources, physical debits and one-hop holds. Transit screening precedes the receiver response. Holds protect one attempt and expire at the round boundary; no end-to-end delivery guarantee follows.

## 3.2 Joint integer listening and credit

A reference tree carries one demand per source per round. For edge load $q_{ij}$, expected attempts are $q_{ij}/p_{ij}$; their incoming/outgoing sum is $\bar k_i$. The reference profile is

$$
\tau_i^{ref}=\min\{\tau_i^{fixed},\tau_{sync}+\lceil\eta\bar k_i\rceil\tau_{guard}\},\quad\eta=1.25. \qquad (11)
$$

Let $D_i(h)$ be expected transmit, receive/processing and grant expenditure under that tree. Expected attempts scale this planning approximation; execution retains the physical costs and retry limit. Intensity $a_i\in[0,1]$ installs only complete transactions:

$$
\begin{aligned}
K_i(h;a_i)&=\lfloor a_iK_i^{ref}(t+h)\rfloor,\\
r_i(h;a_i)&=\frac{K_i(h;a_i)}{\max\{1,K_i^{ref}(t+h)\}},\\
\tau_i(h;a_i)&=\tau_{sync}+K_i(h;a_i)\tau_{guard},\\
b_i(h;a_i)&=P_{sleep}\Delta t+5P_{idle}\tau_{sync}+P_{idle}K_i(h;a_i)\tau_{guard}\\
&\quad+E_{sense}+E_{broadcast}+\mathbf1_{h\ge T_L}\kappa\,r_i(h;a_i)D_i(h).
\end{aligned} \qquad (12)
$$

Here $\kappa=0.65$, and the fixed base counts all five synchronization windows once. The reference communication fraction $r_i$ couples purchased listening to attainable service. Current-period credit $x_i$ is released equally across four rounds. For each scenario,

$$
\widetilde B_i^{m}(0)=B_i(t),\quad e_i^{plan}(h)=b_i(h;a_i)+\mathbf1_{h<T_L}\frac{x_i}{T_L}, \qquad (13)
$$

$$
\begin{aligned}
\widetilde B_i^{m}(h)-e_i^{plan}(h)&\ge B_{reserve},\\
\widetilde B_i^{m}(h+1)&=\min\{B_{max},\widetilde B_i^{m}(h)-e_i^{plan}(h)+\widehat H_i^m(t+h\mid t)\}.
\end{aligned} \qquad (14)
$$

The controller first maximizes listening, then credit at the returned intensity:

$$
\begin{aligned}
\sup_{a_i}\quad &a_i,\\
\text{subject to}\quad &0\le a_i\le1,\quad \exists\, x_i:\;\chi_{floor}T_Lr_i(0;a_i)D_i(0)\le x_i\le B_{max},\\
&\text{the prefixes in (13)--(14) using }b_i(h;a_i).
\end{aligned} \qquad (15)
$$

JLC-R sets $\chi_{floor}=1$. For each trial intensity the least-cost credit is $\textsc{Floor}_i(a)=T_Lr_i(0;a)D_i(0)$. Planned expenditure is nondecreasing in both variables, so two fifteen-step monotone searches retain feasible lower endpoints. The intensity upper endpoint is tested explicitly; slot conversion adds $10^{-9}$ before flooring. Credit search accuracy is at most $B_{max}2^{-15}$ J at fixed intensity, including a possible floor undershoot of that order. Stepwise Guard counts make the intensity target a feasible supremum, not necessarily an attained continuous optimum. An infeasible zero-base prefix is flagged separately from an affordable current transaction.

## 3.3 Charged admission and relay commitments

Execution maintains battery $B_i$, credit $c_i$, held forwarding energy $E_i^{res}$, remaining transactions $k_i$, and active held-packet set $\mathcal{S}_i(t)$ of cardinality $n_i^{res}=|\mathcal{S}_i(t)|$. Uncommitted energy is

$$
e_i^{free}=\min\{c_i,B_i-B_{reserve}\}-E_i^{res}. \qquad (16)
$$

A nonpositive free balance permits no unreserved payment. Sample $p$ may spend its own hold: $A_i(p)=e_i^{free}+e_i^{hold}(p)$. Every outgoing control-plus-data cost must fit $A_i(p)$, without using other samples' holds. Cached same-round unavailability can suppress a request; routing considers a missing or more-than-one-round-old cache unavailable. Surviving candidates require current, charged receiver admission.

After sender payment and any applicable transit screening, the receiver pays its response and must retain a forwarding transaction and energy for reception, processing and one reference outgoing attempt:

$$
e_j^{free}\ge E_{Rx}+E_{proc}+E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}. \qquad (17)
$$

The reference hold is $f_j=E_{Tx}(l,d_{jr})+\mathbf1_{r\ne sink}F_{jr}^{send}$. A member admission to a CH with an upstream CH dependency additionally protects a transit opportunity. Let $b_j^{tr}\in\{0,1\}$ indicate that dependency and

$$
u_j^{tr}=\max_{u\in\mathrm{CH}_t:j\in\mathcal C_u}F_{uj}^{recv}+E_{Rx}+E_{proc}+f_j.
$$

Before the receiver response, the request must satisfy

$$
k_j-n_j^{res}-1\ge b_j^{tr},\qquad e_j^{free}-F_{ij}^{recv}-(E_{Rx}+E_{proc}+f_j)\ge b_j^{tr}u_j^{tr}.
$$

When no upstream dependency exists, the transit margin is zero. This extra margin reserves no physical hold and applies only to member-to-CH requests; inter-CH requests use ordinary admission. Rejection retains the sender's payment without charging an unreached receiver response. Successful reception creates a forwarding hold only if the packet is enqueued. Outgoing attempts release the remaining hold; failed requests retain incurred fees and reconcile held resources. Unexecuted holds expire at round end. A reference hold can fund a dynamically chosen hop using additional free credit, but protects only one attempt.

## 3.4 Routing, priority and mode selection

Members use their associated CH; a CH screens at most five lower-rank candidates and chooses the lowest score

$$
J_{ij}=p_{ij}^{-1}+\mathrm{rank}_j+0.04\widehat Q_j+\frac{0.15}{\widehat B_j+0.15}. \qquad (18)
$$

where rank is shortest-path ETX and cached battery/queue are zero at the sink. Fixed score coefficients are common to all controllers. The selected candidate then faces complete affordability and admission checks; failure stops the current node action loop without exhaustive alternative search. Queues select committed packets first, then prioritize locally uncovered sources and fresh-coverage gain; tied candidates use oldest sender-local successful-forward birth, then newer birth and lower sequence number. This local history does not reveal sink age.

Let $a_i^P,x_i^P$ be the prefix plan and $f_i$ its zero-base infeasibility flag. Demand $d_i$ is true for queued uncovered-fresh work or an active CH with fewer than two planned transactions. With previous mode $h_i$,

$$
h_i^{\,\prime}=d_i\wedge[f_i\vee(a_i^P<0.60)\vee(h_i\wedge a_i^P<0.70)].
$$

If $h_i^{\,\prime}=1$, the controller applies the PADC duty law [@padc2023] to current battery and the causal four-round point prediction, installing integer listening and nonbinding communication permission $x_i=T_LB_{max}$. This permission adds no physical energy; all live reserve and hold checks remain. Otherwise $a_i^P,x_i^P$ are retained. Mode changes preserve queues, battery and local history. Reactive operation does not inherit a prefix-feasibility or energy-neutrality certificate.

```{=latex}
\begin{algorithm}[!htbp]
\caption{JLC-R planning and mode selection}
\label{alg:plan}
\small
\begin{algorithmic}[1]
\REQUIRE Current battery, queue/history, configured roles, causal scenario bank, prior mode
\STATE Define $\textsc{Feasible}(a,x)$ by all reserve prefixes in (13)--(14), $x\le B_{max}$
\STATE $f_i\gets\neg\textsc{Feasible}(0,0)$; $(a_i^P,x_i^P)\gets(0,0)$
\IF{$\neg f_i$}
 \STATE Find feasible lower intensity $a_i^P$ using $x=\textsc{Floor}_i(a)$; test 1, otherwise bisect 15 times
 \STATE At fixed $a_i^P$, bisect $[0,B_{max}]$ 15 times for largest feasible lower credit $x_i^P$
\ENDIF
\STATE Evaluate queued demand and CH two-transaction demand; update the hysteretic mode
\IF{reactive mode}
 \STATE Install PADC duty and permission $x_i=T_LB_{max}$
\ELSE
 \STATE Install $(a_i,x_i)=(a_i^P,x_i^P)$
\ENDIF
\STATE Purchase integer Guards by (12); release $c_i=x_i/T_L$ each round
\end{algorithmic}
\end{algorithm}
```

```{=latex}
\begin{algorithm}[!htbp]
\caption{Charged admission and execution}
\label{alg:exec}
\small
\begin{algorithmic}[1]
\FOR{each round}
 \STATE Replan every $T_L$ rounds; release credit, install Guards and clear prior-round holds
 \STATE Expire samples; pay affordable base/sensing/broadcast tasks, or record unsampled demand
 \FOR{each online node: members first, then CHs in decreasing rank}
  \FOR{at most 96 actions}
   \STATE Select a committed-first, local-age packet and one candidate by (18)
   \IF{no packet/candidate, insufficient transactions or unaffordable complete cost}
    \STATE \textbf{break} current node action loop
   \ENDIF
   \IF{intersensor hop}
    \STATE Consume sender transaction and pay request; stop on receiver unavailability
    \STATE Check member-to-CH transit margin before receiver response; stop on refusal
    \STATE Pay receiver response; check (17) and one remaining forwarding Guard; stop on refusal
   \ENDIF
   \STATE Release own residual hold; consume sink-hop transaction if applicable; attempt data
   \STATE On successful enqueue create one-hop hold; on delivery update source record
   \STATE Retain incurred costs; stop on non-link failure or three failed attempts on the hop
  \ENDFOR
 \ENDFOR
 \STATE Record service and disjoint demand outcomes; harvest, account spill and verify resource ledgers
\ENDFOR
\end{algorithmic}
\end{algorithm}
```

Each stop in Algorithm 2 exits only the current node action loop. Control payments debit physical battery and credit and reconcile the sample's hold; data attempts charge transmission, reception and successful processing. Algorithms 1 and 2 together with Eqs. (16)--(18) fully specify the cache validity, queue selector and atomic transaction rules. Planning requires $O(IMH)$ time and $O(MH)$ local storage ($I=15$, $M=4$); simulator-wide planning is $O(IMNH)$. Selection scans at most $Q_{max}$ packets per action. The full prefix plan is computed even before reactive selection; no embedded runtime has been measured and planner CPU energy is not included.

## 3.5 Resource properties

**Assumption A1 (Atomic serialized admission).** A receiver completes each request, response/denial and resulting data transition before another request can inspect or modify its balances. Concurrent radio reception, hidden terminals and distributed atomicity are outside the model.

**Lemma 1 (Execution safety and numerical-accuracy invariants).** *Fix the current battery, role sequence, listening plan, reference load and scenario bank. Let $\mathcal F_\epsilon\subseteq[0,B_{max}]$ contain credits whose prefix margins in (14) are all at least $-\epsilon$ for a fixed listening intensity $a$. If $0\in\mathcal F_\epsilon$, then $\mathcal F_\epsilon$ is a closed interval $[0,x_\epsilon^*]$, and after $I$ bisections the returned feasible lower endpoint $L_I$ satisfies $0\le x_\epsilon^*-L_I\le B_{max}2^{-I}$. Under the affordability guard $E_i(t)\le B_i(t)$ and (4), each node satisfies $0\le B_i(t)\le B_{max}$, and every admitted feasible credit satisfies all scenario prefix reserve constraints. Under A1, at serialized transaction boundaries the held energy and held guard transactions never exceed the receiver's uncommitted balance and capacity: $E_j^{res}\le\max\{0,\min\{c_j,B_j-B_{reserve}\}\}$ and $|\mathcal S_j(t)|\le k_j$. Finally, for any horizon $T$, offered demand $NT$ equals unsampled, delivered, expired, overflowed and in-transit packets, and the node energy ledger closes:*

$$
B_i(T)=B_i(0)+\sum_{t=0}^{T-1}\bigl[H_i(t)-E_i^{spilled}(t)\bigr]-\sum_{t=0}^{T-1}\bigl[E_i^{base}(t)+E_i^{data}(t)+E_i^{ctrl}(t)\bigr].
$$

The fixed-input scalar credit error is bounded by $1.22\times10^{-4}$ J for $B_{max}=4$ J and $I=15$; prefix tolerance is $10^{-10}$ J. The bound is not a network-freshness optimum. Appendix A retains precise service conditions, proof sketches and starvation counterexamples. Local safety neither guarantees end-to-end delivery nor prevents source starvation.

# 4 Experimental Design

## 4.1 Inputs, controls and common execution

Four inputs (synthetic, T1 Table Mountain winter, T2 Table Mountain spring and T3 Bondville winter) cross supply multipliers 1.0/0.7. NOAA SURFRAD inputs cover 1--17 January 2024 for T1/T3 and 1--17 April 2024 for T2 [@surfrad2024], including warm-up and forecast tail. They are three weather trajectories driving a synthetic network. The reference task is solar-powered open-field soil-moisture and microclimate monitoring. A 15-minute reporting interval and a 60-minute freshness criterion define the tested workload; these are not universal agronomic tolerances. Field evidence shows that wireless soil-moisture relationships can change over long deployments [@kaiser2025wireless]; near-soil RF links also depend on water content, antenna height and vegetation [@baumbauer2025rfid]. These studies motivate temporal reliability and calibration, without validating JLC-R or supplying crop-event labels. Frost detection, irrigation success and crop yield are not evaluated.

All comparisons share geometry, roles, weather, forecast banks and keyed decoding. S200/G20 pays 20-ms synchronization windows at 0, 200, 400, 600 and 800 s; a modeled 17-ms drift/jitter/turnaround budget fits each Guard. At 250 kbps the 4000-bit logical payload has 16-ms nominal airtime; it is separate from the 20-ms Guard. The frozen executor bounds the sum of discretionary listening and both endpoints' nominal payload airtimes by 99.98 s in the late-round service interval. The 17-ms budget is $2(20\,\mathrm{ppm})(200\,\mathrm s)+8\,\mathrm{ms}+1\,\mathrm{ms}$ and is checked on attempts. The logical payload is 500 bytes, larger than a single IEEE 802.15.4 frame, so fragmentation, framing, ACK and contention overhead require an implemented MAC [@cc2420_datasheet]. No method receives free synchronization or receiver access.

Table 1. Physical and execution parameters of the primary confirmation.

| Category | Parameter | Value |
| --- | --- | --- |
| Network | Nodes; area; range | 100; 300 m×300 m; 120 m |
| Organization | Cells; rotation candidates per cell | 4×3; 5 |
| Time | Macro-round; credit period; forecast horizon | 900 s; 4 rounds; 96 rounds |
| Duration | Formal evaluation; forecast warm-up | 14 days; 2 days |
| Battery | Capacity; initial energy; communication reserve | 4 J; 3 J; 0.15 J |
| Recovery | Restart threshold after outage | At least 0.08 J and affordable current base tasks |
| Harvesting | Peak; supply multiplier | 0.12 J/round; 1.0 and 0.7 |
| Data | Logical packet; deadline; queue limit | 4000 bits; 4 rounds; 256 packets |
| Radio | $E_{elec}$; $\varepsilon_{fs}$; $\varepsilon_{mp}$ | 50 nJ/bit; 10 pJ/(bit·m$^2$); 0.0013 pJ/(bit·m$^4$) |
| Processing | Sensing; aggregation | Both 5 nJ/bit |
| Base power | Sleep; offline; extra idle listening | 5 µW; 2 µW; 56 mW |
| Listening | Member/CH caps; guard per transaction | 0.1/1 s; 20 ms (G20) |
| Synchronization | Interval; window; paid windows per round | 200 s; 20 ms; 5 (S200) |
| Grants | Request/response payload; logical data rate | 64 bits each; 250 kbps |
| Planning | Traffic margin; future relay fraction | 1.25; 0.65 |
| Forecast | EWMA coefficient; scenarios; residual quantile | 0.7; 4; 0.9 |
| Cache | Fresh grant check; routing-cache lifetime | Same macro-round; at most 1 round |
| Broadcast | Prepaid cost per node per credit period | 0.0002 J |
| Execution | Decoding attempt limit; per-node loop limit | 3; 96 |

**Table note.** All five primary methods share these physical parameters. Listening caps include the first synchronization window and paid guard capacity; four additional 20-ms windows are charged in both planning and execution. A guard is a charged transaction opportunity; payload airtime and the round serialization envelope are checked separately.

Five controllers share that executor: JLC-R (the complete proposed controller); Prefix-only (the JLC prefix planner without the reactive branch or relay extensions); JLC-Core (the joint prefix planner plus demand-gated reactive branch, without relay extensions); PADC-AGE (the published PADC duty law with the common local-age selector); and PADC+relay (the PADC duty law augmented with the relay extensions). The three relay extensions are pre-response transit margin (T), CH two-slot demand recognition (R), and local source-staleness ordering (S). Ordinary forwarding holds remain common. For $r=(B+P)/B_{max}$, PADC duty is 1 if $r\ge0.5$ or $(r\ge0.3,P\ge E_c)$, otherwise $r/0.9$ for $0.1\le r<0.5$ and 0.05 below 0.1. Here $P$ is the causal four-round harvest and $E_c$ reference expenditure. Permission is nonbinding but physical checks remain.

HENO-MAC's receiver-initiated solar--wind star and p-persistent CSMA differ from this executor [@heno2024]; its HENO-DC duty transfer is retained only in the G10 study. MAoIG uses estimated harvest rates with adaptive paths, per-cycle trees, update generation and conflict-constrained scheduling [@chen2022maoig]. Its full transfer would change the fixed-role, fixed-demand transaction model. A source-level audit of these two candidates found that full HENO requires receiver selection, priority contention and ACK states absent here, while full MAoIG jointly changes routing, generation times and conflict schedules. No second complete external protocol is evaluated; PADC-AGE remains a duty-rule adapter, limiting claims of algorithmic superiority.

## 4.2 Outcomes and primary inference

Let $v_i(t)$ be the latest delivered birth round, or $-1$ before first delivery. End-of-round age is

$$
A_i(t)=
\begin{cases}
[t-v_i(t)+1]\Delta t, & v_i(t)\ge 0,\\
(t+1)\Delta t, & v_i(t)=-1.
\end{cases}
$$
 Fresh-source coverage requires an actual delivery and age at most $D\Delta t$:

$$
C_{fresh}=\frac{100}{NT}\sum_{t=0}^{T-1}\sum_{i=1}^{N}\mathbf1\{v_i(t)\ge0,\ A_i(t)\le D\Delta t\}. \qquad (19)
$$

The primary criterion is $D=4$. Source P5 is the within-run 0.05 quantile (linear interpolation) of each source's fresh-time percentage, then summarized across seeds. Mean AoI averages source-round ages; nighttime outage is the off-node proportion during $g(t)=0$. Far coverage uses sources at least 200 m from the sink and their own source--time denominator. Demand outcomes distinguish unsampled, delivered, expired, overflowed and outstanding samples.

Twelve unused evaluation seeds cross five controllers and eight cells (480 executions). The seed is the independent pairing unit; packets, nodes and repeated conditions are not additional replicates. Matched intervals use

$$
\bar d\ \pm\ t_{0.975,n-1}\frac{s_d}{\sqrt n},\qquad \bar d=\frac1n\sum_{s=1}^{n}d_s,\quad s_d^2=\frac1{n-1}\sum_{s=1}^{n}(d_s-\bar d)^2, \qquad (20)
$$

with $n=12$. The prespecified family contains 32 one-sided noninferiority tests and four winter coverage-superiority tests against Prefix-only. NI comparators are Prefix-only for Synthetic/T2 and PADC-AGE for T1/T3; margins are $-1$ pp for coverage/P5, $+1$ pp for outage and $+5\%$ of baseline AoI. Holm-36 uses $\alpha=0.05$. The zero-outage T2/1.0 tie satisfies its margin deterministically. Paired $t$ inference assumes independent seeds and an adequate small-sample approximation; nominal two-sided intervals are not simultaneous confidence bands. All 32 noninferiority and four winter superiority hypotheses are evaluated within the single Holm-36 family, with worst-case adjusted $p$-values reported in Table 2.

## 4.3 Mechanism and agricultural studies

G10 budget controls use twelve paired seeds, original synchronization and 10-ms Guards, separately from primary S200/G20. The independent relay factorial switches pre-response transit margin T, CH two-slot demand recognition R and local-staleness ordering S in eight configurations. All-on is JLC-R; all-off is JLC-Core. Ordinary charged admission, one-hop holds and physical safeguards remain enabled. Twelve new seeds cross eight input--supply cells plus one T2 spatial-stress condition (864 executions). Four prespecified contrasts average T1/T3 at $s=0.7$ within each seed: bundle and T on far coverage, R on overall coverage, S on P5. Marginal effects average over the other factors; bundle is A111 minus A000. A separate four-test Holm family evaluates these contrasts. This post-confirmation plan leaves Holm-36 unchanged; remaining interactions and conditions are descriptive.

The supply study crosses two winter inputs, six multipliers ($0.7,1,1.5,2,2.5,3$), four controls and twelve new seeds (576 runs). Multipliers scale harvest and forecast together as a normalized supply axis. Freshness sensitivity rescores the 480 frozen confirmation trajectories at 30/60/120/240 min, leaving sampling and expiry unchanged. Spatial stress uses T2, four controls, eight treatments and twelve other seeds (384 runs). A smooth field $c_i\in[0,1]$ sets $T_i=T_{min}+(T_{max}-T_{min})c_i$ and $p_{ij}=p_{ij}^0[1-\lambda(c_i+c_j)/2]$. Stages I/II/III use transmittance ranges [0.85,1], [0.70,0.90], [0.50,0.80] and $\lambda=0,0.10,0.20$; C1/C2/C3 apply energy/link/both effects. This reduced-form stress separates imposed energy and decoding changes; it is not calibrated to canopy density, leaf area index or phenological growth. The common index has opposing responses: higher $c_i$ increases transmittance while decreasing decoding. Neither a Beer--Lambert conversion nor ITU vegetation guidance identifies these joint parameters for a particular crop [@itu_vegetation2021]. Extensions use nominal paired 95% intervals; 70%/80% lines are candidate engineering references. Independent, non-overlapping twelve-seed registries are used for the primary confirmation, G10 budget controls, 864-run relay factorial, 576-run supply scan and 384-run spatial stress test.


## 4.4 Independent monitoring-reliability recording

A post-confirmation exploratory study records end-of-round latest delivered birth times without changing controller decisions or random draws. Twelve previously unused paired seeds, $230101+101k$ ($k=0,\ldots,11$), cross four controllers and three conditions: T1/T3 at $s=0.7$ and T2 at $s=1.0$ (144 executions). The design and metrics were locked before these results. A regression against one frozen confirmation case reproduces coverage, AoI, P5, outage and energy exactly. The original Holm-36 and Holm-4 families remain unchanged.

For each source, an unavailability episode is a maximal run of scored rounds without a delivered update meeting the 60- or 240-minute age criterion. Runs include initialization and horizon censoring; their durations are observed lower bounds when censored. Long unavailability means an observed 60-minute-freshness outage strictly longer than 240 min. Recovery durations concern completed outages after prior fresh service; initialization is excluded and unfinished far-source episodes are reported separately. Source/event measurements are summarized within a run before paired network-seed summaries and nominal 95% intervals. They measure information availability, without agricultural event labels.


# 5 Results

## 5.1 Cross-regime service performance

All 32 NI criteria and four winter superiority tests pass Holm-36 (maximum adjusted $p=0.03711$; 31 stochastic NI passes and one deterministic outage tie). Table 2 reports absolute JLC-R service, while Figure 2 compares all five controllers across the eight regime cells. JLC-R establishes complementary gains across seasonal regimes: in winter deficits (T1/T3), it improves fresh-source coverage by 2.730--4.609 pp over Prefix-only by retaining service when prefix plans become infeasible; in higher-irradiance spring and synthetic regimes (T2 and Synthetic), it improves coverage by 2.29--5.51 pp over PADC-AGE (and 2.00--5.06 pp over PADC+relay) by coordinating reception with funded forwarding capacity. Compared with JLC-Core, which already incorporates joint prefix planning and demand-gated switching, adding the T/R/S relay extensions yields a modest mean coverage increase of 0.10--0.53 pp but substantially improves lower-tail service and timeliness across regimes, reducing mean AoI by 3.4--458 min and increasing Source P5 by 0.18--2.11 pp.

Table 2. JLC-R absolute outcomes and regime-matched primary NI decisions.

| Input | Supply | Coverage (%) | AoI (min) | Source P5 (%) | Night outage (%) | Max NI Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| Synthetic | 1.0 | 55.062 | 545.303 | 28.691 | 0.983 | 0.002162 |
| Synthetic | 0.7 | 39.665 | 1046.021 | 17.752 | 5.439 | 0.03711 |
| T1 winter | 1.0 | 15.398 | 3814.259 | 2.729 | 2.579 | 0.001426 |
| T1 winter | 0.7 | 9.951 | 4080.726 | 3.120 | 21.067 | 0.002162 |
| T2 spring | 1.0 | 70.599 | 72.032 | 38.620 | 0.000 | 0.02979 |
| T2 spring | 0.7 | 48.086 | 291.959 | 17.828 | 0.009 | 0.02237 |
| T3 winter | 1.0 | 8.555 | 4890.627 | 2.448 | 42.756 | 0.0004567 |
| T3 winter | 0.7 | 6.580 | 6394.479 | 2.078 | 59.084 | 0.0001624 |

**Table note.** Twelve paired seeds per cell. NI comparator: Prefix-only for Synthetic/T2 and PADC-AGE for T1/T3. The last column is the largest adjusted p among those four NI contrasts, not a superiority test. No NI criterion is defined for energy. Cross-controller coverage profiles and paired differences are shown in Figure 2; secondary metrics across baseline controllers are summarized in the accompanying text.

Tradeoffs across operating regimes remain explicit. Relative to PADC-AGE, JLC-R exhibits 0.309--0.536 pp lower winter Source P5, and its T3/0.7 mean AoI is 37.65 min higher (95% CI [6.07, 69.24]), well within the prespecified +5% NI margin of +317.8 min. Relative to Prefix-only, synthetic nighttime outage is 0.452--0.836 pp higher, and T2/0.7 mean coverage is 0.307 pp lower (CI [$-0.561$, $-0.052$]), which is offset by a 135 min reduction in mean AoI and a 2.172 pp gain in Source P5. Across all eight cells, network energy expenditure tracks harvested supply, from 8.17--16.11 J per node over the 14-day winter runs to 19.85--24.11 J in synthetic and spring runs, with JLC-R and JLC-Core differing by less than 0.002 J per node. Nevertheless, absolute winter coverage remains 6.58--15.40% with mean AoI of 63.57--106.57 h, underscoring that algorithmic coordination alone cannot substitute for severe winter energy deficits.

![Cross-regime absolute coverage and paired differences.](figures/fig4_cross_regime.svg){width=100%}

Figure 2. Cross-regime absolute coverage and paired differences.

**Figure note.** Five controls across eight cells; JLC-Core is the two-branch planner without T/R/S. Whiskers show nominal 95% paired-seed t intervals; paired coverage differences against each control are descriptive. Formal decisions use the prespecified Holm-36 family.

## 5.2 Budget coupling and relay mechanisms

Before isolating incremental relay rules, separate twelve-seed G10 budget-coupling controls quantify the foundational value of joint listening--credit planning. Holding execution rules fixed, replacing a fixed maximum-listening allocation with joint integer listening--credit optimization increases fresh-source coverage by +15.61 pp (95% CI [+12.39, +18.84]) at nominal supply ($s=1.0$) and +16.97 pp ([+14.45, +19.48]) at reduced supply ($s=0.7$). Enforcing the reference communication credit floor ($\chi_{floor}=1$ versus an unfloored planner $\chi_{floor}=0$ that can purchase guard slots without commensurate forwarding credit) adds +13.70/+14.49 pp for the continuous planner and +13.74/+14.35 pp for the integer Guard planner at nominal/reduced supply, with 95% CIs excluding zero in all four cases. These contrasts identify coupling reception capacity to funded forwarding credit as the principal driver of network-wide coverage in the G10 controls.

Table 3 retains all relay primary hypotheses. Bundle far coverage and staleness-ordering P5 improve after Holm-4; T and R remain unresolved. Both supported primary contrasts are positive in all twelve seeds; their leave-one-seed-out means remain positive and exhaustive sign-flip sensitivity values are 0.000488. This sensitivity assumes independent symmetric null contrasts and does not replace primary inference.

Table 3. Prespecified primary relay-factorial tests under low-supply winter S200/G20 conditions.

| Hypothesis and contrast | Outcome | Difference (pp), 95% CI | Raw $p$ | Holm-4 $p$ |
| --- | --- | --- | --- | --- |
| H1: complete bundle | Far coverage | +0.192 [+0.127, +0.256] | 0.000041 | 0.000165 |
| H2: transit protection T | Far coverage | -0.003 [-0.013, +0.007] | 0.548023 | 0.548023 |
| H3: two-slot recognition R | Overall coverage | +0.052 [-0.004, +0.108] | 0.067296 | 0.134592 |
| H4: staleness ordering S | Source P5 | +0.207 [+0.125, +0.289] | 0.000174 | 0.000523 |

**Table note.** Each of twelve seed-level contrasts first averages T1 and T3 at $s=0.7$ equally. The bundle is A111 minus A000; T, R and S are marginal on-minus-off effects averaged over the other factors. Intervals are nominal paired 95% $t$ intervals with 11 degrees of freedom. Two-sided tests use one separate Holm-4 family at $\alpha=0.05$. H1 and H4 pass that correction; H2 and H3 remain unresolved. Nonsignificance does not establish equivalence.

In the primary winter average, the bundle raises overall coverage by 0.174 pp and lowers AoI by 0.748 h, but raises outage by 0.090 pp and expenditure by 0.170 J (descriptive). Transit margin can change admissions without improving the primary far-source outcome; two-slot recognition can activate without installing usable forwarding capacity. Activation counts therefore do not establish service benefit. Figure 3 summarizes the main effects, two- and three-way interactions, and contention-event shifts across all eight factorial configurations; Table 3 reports the four prespecified primary tests.

![Relay-factorial main effects and interactions.](figures/fig5_relay_ablation.svg){width=100%}

Figure 3. Relay-factorial main effects and interactions.

**Figure note.** Low-supply winter effects are paired across twelve new seeds. Error bars are nominal 95% intervals. Table 3 alone defines Holm-4 primary decisions; other effects and interactions remain descriptive.

## 5.3 Supply adequacy and freshness requirements

Supply response separates battery balance from useful service (Figure 4). T1 coverage rises from 9.71% at $s=0.7$ to 71.07% at $s=3$, crossing the 70% reference near 2.90; T3 reaches only 35.55%. End-of-run battery parity occurs earlier, near 1.94 (T1) and 2.34 (T3). T1 at $s=3$ spills 40.8% of harvest and selects reactive operation in 1.8% of node-periods; PADC-AGE then exceeds JLC-R coverage (72.64% versus 71.07%). T3 still has 25.4% reactive periods and 17.6% zero-base infeasibility at that supply. Battery parity alone is insufficient for the specified freshness target.

![Winter service response to normalized supply.](figures/fig5_supply_scan.svg){width=100%}

Figure 4. Winter service response to normalized supply.

**Figure note.** Rows: T1/T3; columns: coverage, Source P5, mean AoI and end-of-run battery. Bands are nominal 95% t intervals over twelve new seeds. The 70%/80% lines are candidate references, 3 J marks initial battery, and $s$ is a normalized supply multiplier.

Increasing the age criterion to 240 min raises nominal T2 coverage from 70.60% to 95.30%, but nominal T1/T3 reach only 27.19%/16.79%; T3/0.7 remains 12.39%. Rescoring at $D=4$ reproduces confirmation values to numerical precision. Across the four windows ($D\in\{2,4,8,16\}$), matched coverage differences are positive in 29 of 32 cell--criterion combinations, with the three exceptions being T2/0.7 versus Prefix-only at 30/60/120 min; the winter ranking is preserved. Wider criteria count more delivered information as fresh but save no energy or workload, so wider scoring tolerances alone do not relieve energy deficits.

## 5.4 Spatial energy--link stress

Energy transmittance dominates the imposed spring degradation (Figure 5; Table 4). Stage III energy-only loss is $-28.47$ pp (95% CI [$-30.53$,$-26.41$]), versus $-3.20$ pp [$-4.16$,$-2.24$] for link attenuation alone. Joint loss is $-30.56$ pp [$-32.47$,$-28.66$]; the sub-additive interaction across controllers is +0.82--1.13 pp.

![Spatial energy and decoding stress.](figures/fig7_canopy.svg){width=100%}

Figure 5. Spatial energy and decoding stress.

**Figure note.** Panels show overall coverage, far-source coverage, paired changes from C0 and Source P5. C1/C2/C3 separate energy/link/joint effects. Intervals are nominal paired 95% t intervals over twelve seeds. Stages I--III specify exploratory transmittance and attenuation ranges, separating imposed supply loss (C1) from decoding loss (C2).

Table 4. Spatial energy and channel heterogeneity stress test in T2 spring.

| Treatment | JLC-R (%) | Prefix-only (%) | JLC-Core (%) | PADC-AGE (%) | JLC-R P5 (%) | JLC-R far (%) | JLC-R $\Delta$ vs C0 (pp) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 67.16 | 66.92 | 66.86 | 64.60 | 29.66 | 51.50 | 0.00 |
| I-C1 | 62.93 | 62.72 | 62.53 | 59.74 | 26.16 | 46.04 | -4.23 |
| II-C1 | 53.41 | 53.35 | 52.97 | 49.39 | 17.44 | 34.31 | -13.75 |
| II-C2 | 66.03 | 65.78 | 65.68 | 63.46 | 29.88 | 50.02 | -1.14 |
| II-C3 | 52.33 | 52.33 | 51.94 | 48.23 | 17.94 | 32.80 | -14.83 |
| III-C1 | 38.69 | 38.88 | 38.24 | 35.00 | 8.09 | 18.99 | -28.47 |
| III-C2 | 63.96 | 63.67 | 63.59 | 61.63 | 27.21 | 46.02 | -3.20 |
| III-C3 | 36.60 | 36.61 | 36.10 | 32.85 | 7.35 | 16.35 | -30.56 |

**Table note.** Means over twelve new seeds ($190101$--$191212$) on the T2 spring trajectory at $s=1.0$. C1 applies energy transmittance only, C2 channel attenuation only, C3 both. The same spatial energy--link index is shared by all controllers within a seed, with the energy and decoding responses specified in Section 4.3. Far sources are at least 200 m from the sink. Stages I--III specify exploratory transmittance and attenuation ranges, without crop-stage or field calibration. These runs are not pooled with the primary confirmation.

At III-C3, JLC-R exceeds JLC-Core by 0.50 pp (CI [0.39,0.60]) and PADC-AGE by 3.75 pp [3.23,4.28]. Mean coverage is indistinguishable from Prefix-only (difference $-0.01$ pp [$-0.36$,$+0.35$]); P5 is 1.66 pp higher and AoI 389 min lower, while far coverage is 0.53 pp lower. Admission refusals increase and committed-hop completion falls more sharply than decoding success, locating much of the loss in relay service. Absolute coverage below 37% and far coverage below 17% bound the practical claim. All confirmation records preserve offered-demand accounting and report zero Guard/hold violations; resource safety does not imply fairness or freshness.

## 5.5 Continuity of monitoring information

The independent recording study exposes gaps hidden by mean coverage (Table 5). For JLC-R, mean within-run source-P95 longest observed unavailability is 309.14/319.64 h in T1/T3 at $s=0.7$, compared with 21.28 h in T2 at $s=1.0$. Every source in both winter conditions experiences an observed 60-minute-freshness outage exceeding four hours; the spring proportion is 48.25%, rising to 75.48% among far sources. These durations include horizon-censored runs and are lower bounds where recovery is unobserved. Relative to Prefix-only, JLC-R reduces the P95 longest gap by 13.15 h (nominal paired 95% CI [9.37,16.93]), 10.20 h [8.55,11.85] and 6.56 h [1.67,11.45] in T1, T3 and T2, respectively. Corresponding differences from JLC-Core have intervals crossing zero in all three conditions.

Table 5. Observed monitoring unavailability and conditional recovery in the independent recording study.

| Cell / supply | Controller | Median gap (h) | P95 gap (h) | Sources >4 h (%) | Far recovery (h) | Censored (%) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T1 / 0.7 | JLC-R | 189.75 | 309.14 | 100.00 | 2.79 | 7.55 |
| T1 / 0.7 | JLC-Core | 185.86 | 310.31 | 100.00 | 2.94 | 7.64 |
| T1 / 0.7 | Prefix-only | 313.05 | 322.29 | 100.00 | 1.60 | 17.24 |
| T1 / 0.7 | PADC-AGE | 196.49 | 313.35 | 100.00 | 3.05 | 7.65 |
| T3 / 0.7 | JLC-R | 281.96 | 319.64 | 100.00 | 2.12 | 11.32 |
| T3 / 0.7 | JLC-Core | 282.20 | 320.62 | 100.00 | 2.24 | 11.61 |
| T3 / 0.7 | Prefix-only | 313.18 | 329.84 | 100.00 | 1.79 | 24.21 |
| T3 / 0.7 | PADC-AGE | 283.08 | 320.98 | 100.00 | 2.80 | 11.52 |
| T2 / 1.0 | JLC-R | 5.15 | 21.28 | 48.25 | 1.29 | 0.51 |
| T2 / 1.0 | JLC-Core | 5.10 | 23.24 | 48.50 | 1.35 | 0.54 |
| T2 / 1.0 | Prefix-only | 6.14 | 27.84 | 52.50 | 1.38 | 0.35 |
| T2 / 1.0 | PADC-AGE | 6.34 | 22.34 | 57.25 | 1.38 | 0.77 |

**Table note.** Twelve paired network seeds per cell; four controllers and three cells give 144 executions. A gap is a maximal run without a delivered observation aged at most 60 min. Median/P95 columns are across-source quantiles of each source's longest observed gap, averaged across seeds. Sources >4 h includes initialization and horizon-censored gaps. Far recovery is the mean across seeds of completed-episode medians for sources at least 200 m from the sink, excluding initialization; Censored is the mean percentage of eligible far-source recovery episodes unfinished at day 14. Completed recovery and censored episodes must be interpreted together. Full event rates, 240-minute-criterion results and nominal paired intervals are retained in the reproducibility archive.

For T1, T3 and T2, respectively, JLC-R records 79.79, 48.79 and 213.21 outages longer than 60 min per 100 source-days; rates for outages longer than 240 min are 38.94, 23.05 and 21.40. A low event rate can reflect one prolonged outage rather than reliable service. The shorter completed recovery for winter Prefix-only does not reverse its worse long-gap performance: many episodes remain unfinished, and the recovery median excludes them. These are information-availability proxies for periodic soil-moisture and microclimate monitoring, without crop-event or control-success labels.

# 6 Discussion

JLC-R coordinates reception opportunities with the forwarding work they create. The G10 controls demonstrate listening--credit coupling within their original synchronization configuration; the S200/G20 confirmation evaluates the complete controller against Prefix-only and PADC-AGE. Relative to JLC-Core, the three relay extensions add 0.10--0.53 pp in mean coverage but deliver larger lower-tail and timeliness gains (up to 2.11 pp Source P5 and 458 min mean AoI). The separate factorial supports selective bundle and staleness benefits rather than evidence that every component independently improves its target outcome or that a three-component synergy is necessary.

For agricultural design, source-level freshness and continuous unavailability should accompany mean delivery and storage balance. The new recordings show that modest aggregate gains can coexist with multi-day winter observation gaps, while the bundle does not resolve a P95-gap advantage over JLC-Core. Peripheral observations compete for relay capacity, and battery parity can precede useful reporting service. At high T1 supply, PADC-AGE overtakes the conservative planner; under winter deficit or spatial transmittance loss, better allocation cannot replace missing energy. Changing the reporting workload may alter this balance, but the present age-window analysis changes only the scoring criterion.

Transfer is limited by three irradiance trajectories, normalized costs and a fixed daylight template whose support includes zero-GHI winter samples and excludes some measured spring edge-hour energy. The spatial index is a reduced-form transmittance--attenuation parameterization rather than a measured canopy radiative-transfer model. A nonnegative end-of-run battery change over one 14-day weather trace does not establish long-term energy neutrality: initial storage, spill and seasonal variation can change the balance. A field implementation must calibrate photovoltaic/storage and radio costs, include planner CPU energy, and realize synchronization, paid admission and atomic commitments under contention. Collisions, hidden terminals, interference, spatial reuse and scenario-bank sensitivity remain untested. The resource invariants establish local execution safety; unconditional source-level service and deployment performance remain open.

# 7 Conclusion

JLC-R couples integer listening and communication budgets with charged one-hop forwarding commitments. The 480-execution confirmation meets the specified noninferiority criteria and improves winter coverage over Prefix-only; the 864-run factorial shows that the T/R/S relay bundle adds modest mean coverage over JLC-Core but material lower-tail and timeliness gains, while primary T/R effects remain unresolved. Supply and spatial-stress studies show that improved allocation can coexist with inadequate absolute service. The independent trajectory recordings expose persistent winter unavailability despite relative gains over Prefix-only. The method provides a reproducible basis for calibrating energy, propagation and reporting requirements; field performance requires hardware and protocol validation.

# Appendix A. Analytical Statements and Proof Sketches

The analytical statements below establish the formal execution-safety invariants and service conditions under Assumption A1, using the resource definitions in Section 3.5. They concern planned scenarios and serialized actions; they do not supply unconditional delivery or fairness.

**Proof sketch of Lemma 1.** The clipped battery recursion is monotone in incoming energy and antitone in expenditure, giving a downward-closed feasible credit interval. Each bisection halves its width. Affordability and clipping preserve battery bounds. Under A1, a transaction can spend its own hold but excludes every other hold; post-reception admission funds the new obligation. Induction preserves the energy/Guard invariants. Disjoint terminal sample states give demand conservation, and telescoping the debits and spill gives the energy ledger.

**Proposition 1 (Protected-credit head-of-line blocking).** *Consider two unexpired packets at a relay, with an uncommitted packet ahead of a committed one, and let the committed packet $p$ own the relay's only hold, with $\min\{c_j,B_j-B_{reserve}\}=E_j^{res}=e_j^{hold}(p)>0$. A FIFO loop that stops at an unaffordable head then performs no transaction, even though the committed packet can still be served from its own hold: if its outgoing control-plus-data cost is at most $e_j^{hold}(p)$, its guard is available, and downstream admission and decoding succeed, selecting it first permits service.*

*Proof sketch.* The uncommitted head has zero free credit, whereas the committed packet can use its own funded hold. Its selection permits service under the stated downstream and decoding conditions. $\square$

**Proposition 2 (Feasible-set structure and credit-only infeasibility).** *For $\chi_{floor}=1$ and a fixed listening intensity $a$, let $F(a)=T_LaD_i(0)$ in the continuous-listening planner variant (where $r_i(0;a)=a$ without integer Guard flooring) and $F(a)=T_Lr_i(0;a)D_i(0)$ in JLC-R. If the least-cost reference plan $x=F(a)$ is prefix-feasible, then every credit in $[F(a),x_\epsilon^*(a)]$ is feasible, and $x_\epsilon^*(a)$ is nonincreasing in $a$ because planned expenditure (12) is nondecreasing in the listening intensity. If the zero-credit base plan at $a=1$ is already infeasible — the prefixes in (14) fail for $x=0$ — then no credit $x_i\ge0$ restores feasibility at that intensity: credit alone cannot repair an unaffordable listening base. The joint variable can restore feasibility by lowering $a$, since a sufficiently small intensity admits the zero-credit plan whenever the synchronization-level plan itself is affordable.*

*Proof sketch.* Increasing listening or credit increases planned expenditure in every prefix. Monotonicity yields the feasible interval and shows why adding credit cannot repair an infeasible zero-credit base. $\square$

**Proposition 3 (Committed-first starvation counterexample).** *There exist admissible arrival patterns and initial states under which committed-first service starves an uncommitted source indefinitely: if one bottleneck has capacity for one fresh packet per round and an already committed source always precedes a waiting uncommitted source, repeating this pattern serves the former and expires the latter forever. Committed-first priority and bounded queues therefore do not imply fairness. A sufficient deterministic protection is to guarantee every source a successful, fully funded route within latency $L_s$ after a new sample at least every $W_s$ rounds; its end-of-round age is then bounded by $(W_s+L_s)\Delta t$ after initialization. JLC-R provides no such per-source allocation.*

*Proof sketch.* Repeating the admissible one-packet service pattern always selects the committed source. Under the additional per-source service assumption, generation spacing and route latency bound age by $(W_s+L_s)\Delta t$. $\square$

**Theorem 1 (Conditional serial service sufficiency).** *Consider one round after base tasks, with a fixed decreasing-rank routing tree, finite unexpired packets, truthful available caches, successful first decoding attempts and no receiver overflow. For sensor $i$, let $a_i^{in},a_i^{out}$ count incoming and outgoing packets in the prescribed schedule. Let $R_i$ sum reception, processing and receiver-control costs. Let $\overline C_i(p)$ be the larger of the prescribed outgoing control-plus-data cost and reference hold for packet $p$. Assume residual guard capacity is at least $a_i^{in}+a_i^{out}$. Residual credit and battery above reserve must each cover $R_i+\sum_p\overline C_i(p)$, with an action cap of at least $a_i^{out}$. For JLC-R, assume additionally that every prescribed member admission passes the pre-response transit checks in Section 3.3. If the conservative logical serialization envelope fits the macro-round, a member-first, decreasing-rank serial schedule can deliver every prescribed packet while respecting reservations.*

*Proof sketch.* Process members and then relay vertices in decreasing rank. Each vertex has received its prescribed incoming packets before forwarding. The assumed budgets and Guard counts cover its remaining receptions and outgoing costs or holds, and the protected-admission assumption prevents premature refusal. Induction delivers all prescribed packets within the action and serialization limits. $\square$

**Corollary 1 (First-attempt probability on a prescribed schedule).** If Theorem 1's deterministic initial resource and queue conditions hold and its $L$ prescribed decoding outcomes are independent Bernoulli trials, its all-first-success event has probability $\prod_{\ell=1}^{L}p_{e_\ell}$. Hence successful completion has conditional probability at least that product, bounded below by $p_{min}^{L}$. For a two-hop path with $p_{min}=0.72$, the value is 0.5184. This conditional bound excludes random weather and the executed greedy route; the one-attempt reservation cannot claim a three-retry bound without reserving all retry resources.

# CRediT Authorship Contribution Statement

**Zhongjun Ma:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing -- original draft, Visualization. **Huiqing Jin:** Resources, Supervision, Project administration, Funding acquisition, Writing -- review & editing.

# Declaration of Competing Interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

Generative AI tools assisted with manuscript editing, preparation of analysis and experiment-recording code, and consistency checking. The frozen controller and original numerical records were retained; executable analyses support the reported values. The authors take full responsibility for the content of the publication.

# Funding

This work was supported by the Road Traffic Safety Scientific Research Innovation Team Project (Project No.: 2023AH010064).

# Data and Code Availability

The simulation source, configurations, seed registries, processed NOAA SURFRAD inputs and seed-level results are publicly available in the JLC-R repository, release [v1.0.0](https://github.com/mayanzu/jlc-r-paper-package/releases/tag/v1.0.0) [@jlcr_repro2026]. The release includes the 480-execution confirmation, agricultural extensions, 864-execution factorial and 144 delivered-birth recordings, with scripts to verify records and regenerate statistics, numerical tables and statistical figures. The algorithm entry is `code/simulation/jlc_r.py:JLCR` (JLC-R-HYB-V63). Input provenance and third-party data terms are included.

# References
