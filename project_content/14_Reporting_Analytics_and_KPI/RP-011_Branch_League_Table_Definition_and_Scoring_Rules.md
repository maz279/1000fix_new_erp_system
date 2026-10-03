---
id: RP-011
title: Branch League Table Definition and Scoring Rules
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with BI
author: Operations Director with BI Lead and branch manager representatives
reviewers: [CEO, Operations Director, Branch Manager representatives, HR Manager, Quality Manager, BI Lead, CFO delegate, Localisation Lead]
approver: Operations Director with CEO
content_class: D
purpose: >
  The metrics, weightings, size normalisation, exclusions and publication rules for the league table
  that ranks all 51+ branches. A ranking is the most behaviourally powerful artefact this programme
  will produce: it is read by every branch manager, it is remembered when nothing else on a dashboard
  is, and it changes what people do. An unfair or opaque ranking is gamed within one quarter, and once
  a league is being gamed the metrics it is built on stop describing the business — which costs more
  than having no league at all.
traces_to: [P06, 04-00 P06, RP-001, RP-003, RP-004, RP-006, RP-007, RP-008, RP-010, RP-016, 05-04, 05-04 §4, MD-003, MD-005, MD-006, MD-014, 06-02, 06-02 §2, VB-008, TS-016, TR-011, BN-003]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: RP-011_Branch_League_Table_Definition_and_Scoring_Rules_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 Branch league — "Rank and compare all 51+ branches on every operational and financial dimension"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-15 — "A branch manager sees their own branch's detail and only the ranked measure for peers"; PRU-P06-08 every aggregate decomposable; PRU-P06-17 status encoded independently of colour alone
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.1–§2.8 KPI register with baselines and W4/W8 targets; §6 Benefit Tracking Discipline
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.2 R06 Branch Manager headcount 51+, data scope "own branch"; §4 tier T2 branch isolation
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Branch League Table Definition and Scoring Rules

| Item | Value |
|---|---|
| Population | **51+ branches**, growing to 200 without redesign (`NFR-058`) |
| Audience | `R01`, `R05`, and **all 51+ `R06` branch managers** |
| Composite metrics | **7**, weighted (§4.3) |
| Publication | **Quarterly only** (`LT-11`) |
| Peer visibility | **Ranked measure only** — `PRU-P06-15` |
| Wave | W4 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the scoring schema in §4.3. All six sections retained in order.

---

## 1. Purpose

`04-00` `P06` commits to ranking *"all 51+ branches on every operational and financial dimension"*. The
register states the risk: *"an unfair or opaque ranking is gamed within one quarter."*

**Gaming is not misconduct; it is a rational response to a published ranking.** If first-time fix rate
is ranked and the definition excludes parts-wait, a branch improves its rank by classifying more
delays as parts-waits. Nobody lies; the metric stops measuring what it was built to measure. The
defences are all definitional, and they are all in this file:

| Defence | Mechanism |
|---|---|
| **Balance** | A composite across seven dimensions, so improving one at the expense of another gains nothing (§4.3) |
| **Size normalisation** | A 4-technician branch and a 40-technician branch compared fairly, or the ranking is a proxy for size (§4.4) |
| **Countervailing pairs** | Every throughput metric paired with a quality metric, so speed bought with rework scores worse (§4.5) |
| **Exclusion discipline** | The exclusions that make a metric gameable are stated and audited (§4.6) |
| **Cadence** | Quarterly, so a manager cannot optimise a monthly snapshot (`LT-11`) |
| **Transparency** | Every branch sees exactly how its own score was computed (`LT-05`) |

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Weightings | The league becomes whichever metric the builder put first |
| Normalisation | The largest branches win permanently and the ranking carries no information |
| A published method | Managers infer the method, optimise their inference, and dispute the result |
| Exclusions | The metric is gamed through classification rather than performance |
| Peer-visibility rules | `PRU-P06-15` is unimplemented and a branch manager reads another branch's cash |

---

## 2. Scope

**In scope.** The composite metrics and their weightings; size and mix normalisation; countervailing
pairs; exclusions; the scoring method; banding; peer visibility; publication cadence; the dispute
route; and gaming detection.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Metric definitions | **`RP-001`** — the league consumes definitions and creates none |
| Where the league is displayed | `RP-003` `E5`; `RP-004` `C3` panel 6; `RP-010` quarterly section 17 |
| Chart rendering of the league | `RP-007` — `CH-23` already prefers a sorted bar in one neutral token |
| Individual or technician performance | **Not here and not anywhere in this category.** `RP-003` §4.6 and `RP-008` `NR-14` both exclude named individuals |
| Incentive or bonus derived from rank | **Explicitly out of scope — see `LT-13`** |
| Branch master data — size, class, catchment | `MD-003`, `MD-005`, `MD-006` |
| Commentary on the league | `RP-008`, quarterly |
| Data-quality caveats | `RP-016` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Operations Director** (accountable) | Managing the network |
| **CEO and board** | `RP-010` quarterly section 17 |
| **All 51+ branch managers** | Their own position, their own score's derivation, and the peer ranked measure |
| **HR Manager** | Confirming the league is **not** an appraisal input (`LT-13`) |
| **BI Lead** | The scoring implementation |
| **L&D** (`TR-011`) | The branch manager course explains the league and how it is computed |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **LT-01** | **The league is a composite, never a single metric.** A single-metric ranking is gamed by definition |
| **LT-02** | **Every component is an `RP-001` metric with a measured baseline.** A metric with no baseline may not be ranked (`KD-20`) |
| **LT-03** | **Every throughput component is paired with a quality component** (§4.5). Speed without quality scores worse, not better |
| **LT-04** | **Scores are normalised for branch size and service mix** (§4.4), or the league ranks size |
| **LT-05** | **Every branch sees the full derivation of its own score** — components, raw values, normalised values, weights and contribution (`PRU-P06-08`) |
| **LT-06** | **A branch sees only the ranked measure for peers**, never their component detail (`PRU-P06-15`) |
| **LT-07** | **The method is published before the first league**, and changes take effect from the following quarter, never retrospectively |
| **LT-08** | **A branch below the minimum volume threshold is unranked, not ranked last** (§4.4) |
| **LT-09** | **Exclusions are stated and audited** (§4.6). An exclusion that a branch controls is a gaming route |
| **LT-10** | **Data quality gates the league**: a branch whose `RP-016` domain scores fall below threshold is shown as **"data quality below threshold"**, not ranked on unreliable data |
| **LT-11** | **Published quarterly only.** Monthly ranking noise invites gaming and rewards short-term optimisation; `RP-008` and `RP-010` both hold to this |
| **LT-12** | **Bands, not positions, in any external or wide-audience view** — `RP-005` `ED-07` applies the same principle to partners |
| **LT-13** | **The league is not an input to individual appraisal, bonus or incentive.** A ranking tied to pay is optimised rather than improved, and `BRU-HRM-03` computes technician incentive from measured jobs, not from branch rank |
| **LT-14** | **Every league publication carries its data cut-off, its version and the number of ranked branches** |
| **LT-15** | **Gaming is monitored, not assumed absent** (§4.8) |
| **LT-16** | **A branch may dispute its score** through a defined route with a decision within one publication cycle (§4.7) |

### 4.2 What is ranked, and what is not

`04-00` says *"every operational and financial dimension"*. **That is the capability, not the league.**
Ranking everything produces 30 rankings nobody reads and a composite nobody trusts.

| | Approach |
|---|---|
| **The composite league** | Seven weighted components (§4.3) — one ranking, published quarterly |
| **Dimension views** | Any `RP-001` metric may be sorted by branch on `RP-003` `E5` as a **view**, not as a published ranking. `PRU-P06-15` still applies |
| **Not ranked** | Financial margin at branch level (§4.6), safety incidents, complaint volume, and anything a branch cannot influence |

### 4.3 The seven components and their weights

| # | Component | Metric | Weight | Direction | Pairs with |
|---:|---|---|---:|---|---|
| 1 | **Service promise kept** | `KPI-006` SLA compliance | **20%** | Higher better | 2 |
| 2 | **Done right first time** | `KPI-004` first-time fix rate | **20%** | Higher better | 1, 3 |
| 3 | **Quality of work** | `KPI-005` rework rate | **15%** | **Lower better** | 2, 4 |
| 4 | **Throughput** | `KPI-011` jobs per technician per day, normalised | **15%** | Higher better | 3 |
| 5 | **Customer experience** | `KPI-020` CSAT | **15%** | Higher better | 4 |
| 6 | **Control discipline** | Composite of cash closed daily (`BRU-FIN-10`), van-stock variance (`KPI-047`), inventory accuracy (`KPI-042`) | **10%** | Higher better | — |
| 7 | **Housekeeping** | Uncollected devices > 30 days (`KPI-009`), QC first-pass (`KPI-007`) | **5%** | 009 lower, 007 higher | — |
| | **Total** | | **100%** | | |

**Why these seven and not others:**

| Choice | Reason |
|---|---|
| SLA and first-time fix at 20% each | They are the two promises a customer experiences directly, and `06-02` targets both |
| Rework at 15% and **inverted** | It is the countervailing weight to throughput. A branch that hits 9 jobs a day by returning to a third of them scores worse overall than one at 7 with 3% rework |
| CSAT at 15% | The only component the customer scores rather than the system |
| Control discipline at 10% | Cash and stock discipline are binary controls, not performance curves; 10% is enough to matter and too little to dominate |
| Housekeeping at 5% | Real but small; a higher weight would make uncollected devices the league |
| **No financial margin** | §4.6 |
| **No safety metric** | §4.6 |

### 4.4 Normalisation — the fairness half

Without this, the league ranks branch size. `MD-003` holds branch class and `MD-005` holds zone.

| # | Rule |
|---|---|
| **LT-17** | **Volume-based components are per-capita or per-job**, never absolute. Throughput is jobs per technician per day, not jobs |
| **LT-18** | **Branches are ranked within their class** — `MD-003` branch class — **and in an all-branch view**. A metropolitan flagship and a district service point are compared within class first |
| **LT-19** | **Service mix is normalised.** A branch doing mostly appliance on-site work has a structurally different TAT and first-time fix profile from one doing mostly IT workshop repair. **Each component is scored against the branch's own mix-adjusted expectation**, not against the network mean |
| **LT-20** | **Minimum volume threshold: 30 completed jobs in the quarter.** Below it a branch is **unranked** and shown as *"below minimum volume"* (`LT-08`). Small denominators produce extreme percentages that are noise, and ranking noise is what destroys confidence in a league |
| **LT-21** | **A branch open for less than a full quarter is unranked**, and reported separately with its ramp position |
| **LT-22** | **Catchment and seasonality are not normalised**, and that is a stated limitation rather than an oversight — no defensible adjustment exists without data the programme does not yet have (`O-04`) |

**Scoring method.** Each component is converted to a **percentile within the comparison set** (class,
then all-branch), then weighted and summed. Percentiles rather than raw z-scores because a percentile
is explainable to 51+ branch managers, and an unexplainable score is a disputed score.

### 4.5 Countervailing pairs

`LT-03` in full. Each pair means an improvement bought at the other's expense is net-neutral or
net-negative.

| Pair | Gaming route it closes |
|---|---|
| Throughput ↔ **Rework** | Rushing jobs to raise jobs-per-day raises rework, which is inverted at 15% |
| First-time fix ↔ **Rework** | Recording a partial fix as complete produces a return visit, which is rework |
| SLA compliance ↔ **Hold count** | An SLA met by pausing the clock is visible: `RP-001` `KPI-006` requires the **hold count published beside compliance**, and an abnormal hold rate is a §4.8 gaming signal |
| CSAT ↔ **Survey response rate** | Selectively surveying satisfied customers raises CSAT; response rate is monitored under §4.8 |
| Uncollected devices ↔ **Premature closure** | Closing a job to clear the uncollected list creates a reopen, which is rework |

> **`KPI-006`'s hold exclusion is the single most gameable rule in the league**, and `RP-001` already
> requires the hold count published beside it. This file makes an abnormal hold rate a monitored
> signal rather than a footnote.

### 4.6 Exclusions, and what is deliberately not ranked

| Not ranked | Why |
|---|---|
| **Branch financial margin** | Margin at branch level is driven by service mix, pricing decisions taken centrally (`MD-029`) and warranty-versus-paid work ratios a branch does not choose. **Ranking it would rank the catchment**, and it would create an incentive to decline low-margin warranty work — which is the company's brand obligation |
| **Safety incidents** | **Ranking safety suppresses reporting.** `SP-030` and `NFR-083` depend on incidents being reported; a league position that falls when a branch reports an incident is the most damaging possible incentive. Safety is managed, escalated and audited — never ranked |
| **Complaint volume** | Same mechanism: a branch that logs complaints properly would rank below one that resolves them informally. **Complaint *resolution within SLA* is ranked indirectly through CSAT**; volume is not |
| Attendance and HR metrics | Managed through `RP-004` `C8`, not ranked |
| Anything a branch cannot influence — network stock availability, central pricing, portal uptime | Ranking an uncontrollable is demoralising and uninformative |

**Component exclusions that must be audited** (`LT-09`), because each is a classification a branch
partly controls:

| Exclusion | Audit |
|---|---|
| `KPI-006` approved holds | Hold rate per branch monitored; abnormal rate investigated (§4.8) |
| `KPI-004` parts-wait exclusion | Parts-wait classification rate monitored per branch |
| `KPI-005` rework 30-day window | Reopen-after-31-days rate monitored — a spike indicates window-gaming |
| `KPI-020` CSAT survey population | Response rate and send rate monitored |

### 4.7 Publication, visibility and dispute

| Item | Rule |
|---|---|
| Cadence | **Quarterly** (`LT-11`) |
| Where | `RP-003` `E5`; `RP-004` `C3` panel 6 (own detail + peer ranked measure); `RP-010` quarterly section 17 |
| Own branch | **Full derivation** — components, raw, normalised, weight, contribution (`LT-05`) |
| Peers | **Ranked measure only** (`LT-06`, `PRU-P06-15`) |
| Unranked branches | Listed with the reason — below minimum volume, part-quarter, or data quality below threshold |
| Metadata | Cut-off, version, number of ranked branches (`LT-14`) |
| Bengali | **Component names, band names and the derivation labels** are bilingual — 51+ branch managers, `CG-010` §3.2 |
| Bands | Quartile bands published alongside position; **bands only in any wide-audience view** (`LT-12`) |
| **Dispute** | A branch manager may dispute within 10 working days, in writing, to the Operations Director; BI Lead verifies the computation; **a decision is issued within the same publication cycle** and a correction restates the league with the restatement labelled (`LT-16`, `RP-001` `KD-28`) |

### 4.8 Gaming detection

`LT-15`: monitored, not assumed absent. Reviewed quarterly with the league.

| Signal | What it may indicate |
|---|---|
| Hold rate materially above class median | `KPI-006` clock pausing |
| Parts-wait classification rate above class median | `KPI-004` exclusion routing |
| Reopen rate spiking just after the 30-day rework window | Window management |
| CSAT response rate materially below class median | Selective surveying |
| Job closure clustering immediately before a period end | Throughput timing |
| Sharp rank improvement with no change in any underlying operational metric | Classification change rather than performance change |
| Uncollected-device count falling with reopen count rising | Premature closure |

**A signal is an investigation, not an accusation.** Every one has an innocent explanation — a genuine
parts shortage produces exactly the parts-wait pattern above — and the review begins with the branch
manager's account.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | All seven components; `KPI-006`'s hold-count rule; baselines (`LT-02`) |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | `ds_branch_dim` for class and normalisation; the component facts |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md) `E5`, `RP-004` `C3` | Where it is displayed, with `PRU-P06-15` scoping |
| [`RP-007`](RP-007_Chart_Label_and_Visualisation_Standard.md) | Rendering — `CH-23` sorted bar in one neutral token for 51 branches |
| [`RP-008`](RP-008_Report_Narrative_and_Commentary_Template_Set.md), `RP-010` | Quarterly commentary and publication |
| **[`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md)** | The data-quality gate (`LT-10`) |
| `MD-003`, `MD-005`, `MD-006` | Branch class, zone, geography |
| `05-04` §4 `T2`, `PRU-P06-15` | Peer visibility |
| `06-02` §2 | Component baselines and targets |
| `TR-011` | The branch manager course explains the method |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually; weights reviewed with the Operations Director and branch manager representatives |
| Trigger for out-of-cycle review | A gaming signal confirmed; a component metric restated (`KD-25`); a new branch class; a dispute upheld; branch count crossing a normalisation threshold |
| Change rule | **Method changes take effect from the following quarter, never retrospectively** (`LT-07`) |
| Owner | Operations Director with BI Lead |
| Data file | `RP-011_League_Components.csv` · `RP-011_Normalisation_Rules.csv` · `RP-011_Gaming_Signals.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Four of the seven components have no measured baseline**, and `LT-02` forbids ranking a metric without one. `KPI-006` SLA compliance, `KPI-005` rework rate, `KPI-007` QC first-pass and `KPI-047` van-stock variance all read "unmeasured" or "untracked" in `06-02` §2. **The league cannot be published from four unbaselined components** — 55% of the weight | Operations Director with Programme | **W4 — via `RP-015`, which is W0 and overdue** |
| **O-02** | **The weightings are proposed by the content function and have not been agreed with the 51+ branch managers who will be ranked by them.** `LT-07` requires the method published before the first league; a weighting set imposed without consultation is disputed on first publication, and the dispute is about legitimacy rather than arithmetic | Operations Director with branch manager representatives | **W4 — before the first publication** |
| **O-03** | **`LT-19` mix normalisation has no method.** Scoring each component against a branch's own mix-adjusted expectation requires a mix model that does not exist, and `MD-003` branch class may be too coarse a proxy. **Without it the league partly ranks service mix** — the defect `LT-04` exists to prevent | BI Lead with Operations Director | **W4** |
| **O-04** | **Catchment and seasonality are not normalised** (`LT-22`), stated as a limitation. A coastal branch in monsoon season and a Dhaka branch in the same quarter face different demand; **no defensible adjustment exists yet**, and this will be the most common basis of dispute under `LT-16` | Operations Director with BI Lead | W4 |
| **O-05** | **`LT-13` excludes the league from appraisal and incentive, and nothing enforces it.** `BRU-HRM-03` computes technician incentive from measured jobs, but **no rule prevents a branch manager's own appraisal referencing league position** — and if it does, every defence in §4.5 and §4.8 is overwhelmed | HR Manager with Operations Director | **W4 — needs an HR policy statement** |
| **O-06** | **Gaming detection needs a class median and 51+ branches of history to compute one.** §4.8's signals are all relative to a class median, which does not exist until several quarters of data do. **The first two or three leagues therefore have no gaming detection**, which is exactly when incentives to game are strongest | BI Lead | W4 |
| **O-07** | **No Bengali component names, band names or derivation labels exist**, and `LT-05` requires every one of 51+ Bengali-reading branch managers to understand their own score's derivation. **A score a manager cannot read is a score they will dispute.** `RP-001` `O-05` and `RP-004` `O-04` record the same unresourced Bengali dependency | Localisation Lead | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the scoring schema
- [x] **Gaming treated as a rational response rather than misconduct, with six definitional defences**
- [x] Seventeen rules stated, including composite-not-single, quality-pairing and quarterly-only
- [x] Seven weighted components summing to 100%, each with the reason for its weight
- [x] **Rework inverted at 15% as the explicit countervailing weight to throughput**
- [x] Normalisation specified for size, class and mix, with percentile scoring chosen for explainability
- [x] **Minimum volume threshold with unranked rather than ranked-last treatment**
- [x] Five countervailing pairs, each naming the gaming route it closes
- [x] **Margin, safety and complaint volume excluded with the incentive mechanism stated for each — ranking safety suppresses reporting**
- [x] Four component exclusions identified as gameable and placed under audit
- [x] Peer visibility bound to `PRU-P06-15`; own-score derivation required in full
- [x] A dispute route with a decision inside one publication cycle
- [x] Seven gaming signals, each framed as an investigation rather than an accusation
- [x] `LT-13` separating the league from pay, with the reason
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` four of seven components unbaselined — outstanding; 55% of the weight cannot be ranked**
- [ ] **`O-02` weightings not agreed with the branch managers — outstanding**
- [ ] **`O-03` no mix-normalisation method — outstanding; the league partly ranks mix**
- [ ] **`O-05` nothing prevents appraisal referencing rank — outstanding; needs an HR policy statement**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding (`O-07`)**
- [ ] Named approvers recorded — **pending Operations Director and CEO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
