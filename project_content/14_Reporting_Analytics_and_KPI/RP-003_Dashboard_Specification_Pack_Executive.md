---
id: RP-003
title: Dashboard Specification Pack — Executive
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead with the Executive
author: BI Lead with the CEO office, CFO, CCO and Operations Director
reviewers: [CEO, CFO, CCO, CTO, Operations Director, Programme Manager, Design System owner]
approver: CEO with CTO
content_class: D
purpose: >
  The executive dashboards on P06 — which metrics appear, in what order, at what grain, with which
  drill paths, commentary slots and mobile behaviour. Fourteen revenue streams and eighteen business
  objectives are reported to one board, and a board that reads four directors' four interpretations
  of the same quarter is a board taking four different decisions. This pack decides what management
  looks at before anyone builds it, because a dashboard designed in a tool becomes the definition of
  what the company measures.
traces_to: [P06, 04-00 P06, 06-02, 06-02 §1, 06-02 §3, 06-02 §5, M25, M62, README, RP-001, RP-002, RP-006, RP-007, RP-010, RP-011, RP-012, RP-014, RP-015, VB-008, UI-016, HC-008, 05-04, 05-06 NFR-038]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-01, PRU-P06-05 (Grafana defines no business metric; Metabase serves no sub-minute refresh), PRU-P06-06 (every view states its data freshness), PRU-P06-07, PRU-P06-08 (every aggregate decomposable), PRU-P06-09 (a drill-through never widens access), PRU-P06-17 (status encoded independently of colour alone)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 — executive capability set, branch league across 51+ branches, real-time operations board, self-service on certified datasets, mobile dashboards for managers away from a desk; KPIs executive dashboard load < 5 s, weekly usage by managers > 90%, decisions on live data 100%, manual reporting effort −90%
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §1 BO-01…BO-18 with metric, baseline, target and owner; §3.1 annual benefit at steady state by stream; §5 programme success criteria including "all 14 revenue streams transact end to end" and "management decisions are made on live dashboards"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/README.md §The Fourteen Revenue Streams — the fourteen streams and their owning modules
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-038 executive dashboard load ≤ 5 s
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Dashboard Specification Pack — Executive

| Item | Value |
|---|---|
| Portal | `P06` Analytics & Executive Dashboard |
| Audience | `R01` CEO · `R02` CTO · `R03` CFO · `R04` CCO · `R05` Operations Director — **25–60 management users** |
| Dashboards specified | **7** (§4.2) |
| Load target | **≤ 5 s** (`NFR-038`); mobile parity §4.7 |
| Metrics source | `RP-001` only — `PRU-P06-01` |
| Wave | W4 · `P1` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` metric-table addition applied per dashboard in §4.3. All six sections retained in order.

---

## 1. Purpose

`06-02` §5 makes *"management decisions are made on live dashboards"* a programme success criterion,
and `04-00` sets weekly usage by managers above 90%. Neither is a build target. Both are content
decisions: **which seven views exist, what is on them, and what a director is expected to do having
looked.**

The failure mode is well documented and it is not slowness. It is that a dashboard built to
demonstrate capability shows everything available, a director reads the two numbers they already
trusted, and the rest becomes decoration. Within two quarters the board reverts to a compiled pack
— which is precisely the 90% effort reduction the programme committed to removing.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| An agreed metric set per view | Four directors specify four dashboards; `KPI-004` appears three times at three grains |
| Drill paths | `PRU-P06-08` requires every aggregate decomposable. Undesigned drills mean a director sees a bad number and cannot find the jobs behind it — so they ask for a spreadsheet |
| Commentary slots | Numbers without narrative are re-interpreted by every reader (`RP-008`) |
| Mobile behaviour | `04-00` promises key dashboards on a phone for managers away from a desk. Unspecified, that becomes a shrunken desktop view nobody uses |
| A "what to do" for each view | A dashboard with no decision attached is a report with animation |

---

## 2. Scope

**In scope.** The seven executive dashboards; per-view metric selection, layout order, grain, drill
paths, commentary slots, refresh and freshness declaration, mobile behaviour, and the decision each
view supports.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Metric definitions | **`RP-001`** — `PRU-P06-01` forbids defining a metric in a dashboard |
| Certified datasets and row-level security bindings | `RP-006` |
| Chart type, colour, axis and unit rendering | **`RP-007`** |
| The fourteen `P03` operational consoles | `RP-004` |
| External-audience analytics | `RP-005` — `PRU-P06-14` forbids external `P06` access |
| The branch league table's scoring rules | **`RP-011`** — this pack places the league on a view; `RP-011` decides how it ranks |
| Alert thresholds | `RP-012` |
| The standing board pack | `RP-010` — a document assembled from these views |
| Commentary wording | `RP-008` |
| Screen labels and microcopy | `UI-016` |
| Export marking | `RP-014` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **CEO and the board** | Group performance across 14 revenue streams |
| **CFO** | Revenue, margin, cash, close and statutory position |
| **CCO** | Commercial performance, contract base, marketplace, pricing |
| **Operations Director** | Network delivery performance and the branch league |
| **CTO** | Platform, adoption, automation and data quality |
| **BI Lead and engineers** | The build specification |
| **`RP-010`** | The pack assembled from these views |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **XD-01** | **Every view answers one question and states it at the top.** A view that answers three questions is three views |
| **XD-02** | **Every view states what a director is expected to do** if the number is wrong. A view with no action is not built |
| **XD-03** | **Nine metrics maximum per view.** The limit is arbitrary and it is enforced; a tenth metric displaces an existing one and the displacement is a decision |
| **XD-04** | Every metric is a `RP-001` identifier. **No inline calculation** (`KD-15`, `AUT-P06-08`) |
| **XD-05** | Every metric displays its definition, owner, source and certification status on the view (`PRU-P06-07`, `KD-17`). **A `Provisional` metric is visibly labelled** |
| **XD-06** | **Every aggregate drills to its constituent records** (`PRU-P06-08`), and the drill path is specified here, not discovered in the tool |
| **XD-07** | **A drill never widens access** (`PRU-P06-09`); permissions are re-evaluated at the destination |
| **XD-08** | Every view **states its data freshness** and is flagged when stale beyond its guarantee (`PRU-P06-06`, `AUT-P06-04`) |
| **XD-09** | **Metabase serves no sub-minute refresh; Grafana defines no business metric** (`PRU-P06-05`). The real-time board is Grafana over a scoped feed; everything else is Metabase over the warehouse (`PRU-P06-12`) |
| **XD-10** | Every view carries a **commentary slot** owned by a named function (`RP-008`) |
| **XD-11** | **Status and performance are encoded independently of colour** (`PRU-P06-17`, `PS-04`); `RP-007` governs how |
| **XD-12** | **Comparison is always to a stated basis** — prior period, same period last year, target, or baseline (`RP-015`). A number with no comparator supports no decision |
| **XD-13** | A metric with **no measured baseline** may appear but **may not carry a variance-to-baseline** (`KD-20`) |
| **XD-14** | View load ≤ **5 s** (`NFR-038`), verified in `TS-014` `PERF-NFR-038-01` |
| **XD-15** | Every view is specified for **phone** before it is built for desktop (§4.7) |

### 4.2 The seven dashboards

| # | Dashboard | Primary audience | Question it answers | Refresh |
|---:|---|---|---|---|
| **E1** | **Group Performance** | `R01`, board | Is the company performing, across all fourteen revenue streams? | Daily |
| **E2** | **Revenue Stream Detail** | `R01`, `R03`, `R04` | Which streams are growing, which are losing money, and why? | Daily |
| **E3** | **Financial Position** | `R03` | Where is cash, margin, receivables and the close? | Daily; close section per period |
| **E4** | **Service Delivery** | `R05`, `R01` | Are we delivering to the promise we made customers? | Hourly |
| **E5** | **Branch League** | `R05`, `R06`, `R01` | Which branches lead, which lag, and on what? | Daily |
| **E6** | **Live Operations Board** | `R05`, `R07` | What is happening right now that needs intervention? | **≤ 60 s** |
| **E7** | **Programme and Platform** | `R02`, `R01` | Is the platform healthy and is the programme delivering its benefits? | Daily |

**Seven, not one per director.** `E1` is the board view; `E2`–`E7` are the functional depths beneath
it. Every one of `E2`–`E7` is reachable from `E1` by a drill (`XD-06`), so the board view is the
entry point rather than a separate artefact that can diverge from it.

### 4.3 Per-dashboard specification

---

#### `E1` Group Performance

| Item | Value |
|---|---|
| Question | *Is the company performing, across all fourteen revenue streams?* |
| Action if wrong | Drill to `E2` for the stream, then to the owning function's view |
| Grain | Group, month-to-date and rolling 12 months |
| Freshness | Daily, 06:00 BST |
| Commentary owner | CEO office, monthly (`RP-008`) |

| Slot | Metric | Comparator |
|---:|---|---|
| 1 | Revenue, group | Prior month · same month last year · plan |
| 2 | Gross margin % | Prior month · plan |
| 3 | Revenue by stream — 14 streams, ranked | Prior month |
| 4 | `KPI-020` CSAT | Baseline 3.8/5 · target 4.7/5 |
| 5 | `KPI-006` SLA compliance | Target 96% |
| 6 | `KPI-011` Jobs per technician per day | Baseline 4–5 · target 8–9 |
| 7 | `KPI-050` Month-end close cycle | Baseline 15–20 days · target ≤ 3 |
| 8 | `KPI-095` Overall automation of routine work | Target 85% |
| 9 | **Benefit realisation to date** vs `06-02` §3.2 curve | Plan |

> **Slot 3 is the view's reason to exist.** `06-02` §5 criterion 1 requires all fourteen streams to
> transact end to end with zero shadow spreadsheets. **A stream showing no revenue on this view is
> either not live or not in the system**, and both are board-level facts. `TS-012` proves each stream
> works; this slot proves each stream *is being used*.

> **Slot 9 depends on `RP-015`.** Benefit realisation against the `06-02` §3.2 curve cannot be
> computed while 44 of 95 baselines are unmeasured (`RP-001` `O-06`). Until then the slot shows
> **realised benefit on measured baselines only, with the excluded count stated** — `O-02`.

---

#### `E2` Revenue Stream Detail

| Item | Value |
|---|---|
| Question | *Which streams are growing, which are losing money, and why?* |
| Action if wrong | Stream owner from `06-02` §3.5 is accountable; drill to their functional view |
| Grain | Revenue stream × month; drill to job, contract or order |
| Freshness | Daily |
| Commentary owner | Stream owner, monthly |

One row per stream, fourteen rows, each carrying: revenue, gross margin %, volume, month-on-month
movement, the stream's own headline KPI, and its `06-02` §3.1 benefit target. The stream list and
owning modules are taken from `README` §Fourteen Revenue Streams — **not restated here** (`CP-01`).

**`XD-03`'s nine-metric limit applies per row, not per view.** A fourteen-row table with six columns
is one metric family, not 84 metrics; the limit exists to stop unrelated metrics accumulating, and it
is recorded so a reviewer does not misapply it.

---

#### `E3` Financial Position

| Slot | Metric |
|---:|---|
| 1 | Cash position and 13-week forecast |
| 2 | `KPI-052` Days sales outstanding · receivables ageing |
| 3 | `KPI-056` Revenue leakage — unbilled delivered work |
| 4 | `KPI-050` Close cycle, with the close checklist state for the open period |
| 5 | `KPI-057` VAT returns filed on time with zero adjustment · `KPI-058` tax compliance findings |
| 6 | Gross margin by business line (`MD-036` dimensions) |
| 7 | `KPI-055` Billing accuracy — credit notes as % of invoices |
| 8 | `KPI-038` Warranty revenue leakage |
| 9 | `KPI-031` Contracts with negative margin |

> Slots 5 and 8 are the two the CFO is asked about externally. `RP-009` owns the filings themselves;
> this slot reports **whether they were filed on time and clean**, which is a different question and a
> different metric.

---

#### `E4` Service Delivery

| Slot | Metric |
|---:|---|
| 1 | `KPI-006` SLA compliance |
| 2 | `KPI-002` / `KPI-003` TAT — IT equipment and appliance on-site |
| 3 | `KPI-004` First-time fix rate |
| 4 | `KPI-005` Rework rate |
| 5 | `KPI-007` QC first-pass rate |
| 6 | `KPI-015` On-time arrival within window |
| 7 | `KPI-096` on-time collection · `KPI-097` on-time delivery *(the `RP-001` `KD-05` split)* |
| 8 | `KPI-009` Devices uncollected > 30 days |
| 9 | `KPI-024` Complaint resolution within SLA |

---

#### `E5` Branch League

| Item | Value |
|---|---|
| Question | *Which branches lead, which lag, and on what?* |
| Grain | Branch × month; drill to branch console (`RP-004`) then to job |
| Scoring | **`RP-011` governs entirely.** This view renders the ranking; it does not define it |
| Access | **`PRU-P06-15`: a branch manager sees their own branch's detail and only the ranked measure for peers** |

> **The access rule is the whole design.** `R06` is 51+ people and every one of them can open this
> view. Without `PRU-P06-15`, a branch manager reads another branch's cash position. `RP-005` handles
> the analogous problem for external parties; here it is internal and easier to overlook.

---

#### `E6` Live Operations Board

| Item | Value |
|---|---|
| Question | *What is happening right now that needs intervention?* |
| Refresh | **≤ 60 s** — Grafana over a scoped real-time feed (`PRU-P06-05`, `PRU-P06-12`) |
| Grain | Live: open jobs, technicians on map, SLA countdowns, queue depth, system health |
| Freshness | Displayed as a live timestamp, not a date (`XD-08`) |

**This is the one view exempt from the warehouse rule**, and the exemption is `PRU-P06-12`'s own —
*"except the scoped real-time board"*. It carries **no business metric definitions** (`PRU-P06-05`):
counts and countdowns only. Anything requiring a definition belongs on `E4`.

`AUT-P06-10` surfaces an SLA countdown reaching its threshold here **and** notifies the accountable
role, so the board is not the only line of defence.

---

#### `E7` Programme and Platform

| Slot | Metric |
|---:|---|
| 1 | `KPI-085` Uptime, business hours · `KPI-086` API p95 latency |
| 2 | `KPI-087` Event delivery success · `KPI-088` integration failures undetected > 5 min |
| 3 | `KPI-089` Critical vulnerabilities open > 7 days · `KPI-090` orphaned accounts after leaver |
| 4 | `KPI-092` Bengali translation completeness |
| 5 | `KPI-093` Data quality test pass rate → drill to `RP-016` scorecards |
| 6 | `KPI-094` Manual management reports remaining · `KPI-095` overall automation |
| 7 | Benefit realisation vs the `06-02` §3.2 curve, by benefit line |
| 8 | Open defect profile by severity (`TS-018` §4.1) and the deferral register count |
| 9 | Wave gate position — criteria met, conditional, outstanding (`TS-018` §4.5) |

> Slots 8 and 9 make this the only executive view that reports on **the programme** rather than the
> business. They are here rather than in a separate programme dashboard because `06-02` §5 makes
> programme delivery a board matter until Month 36, and a second artefact would diverge.

### 4.4 Drill paths

`XD-06` requires every aggregate to drill. The paths are specified, and `XD-07` means each hop
re-evaluates permissions.

| From | To | Then |
|---|---|---|
| `E1` slot 3 revenue by stream | `E2` stream row | Contract, order or job list |
| `E1` slot 5 SLA compliance | `E4` slot 1 | Branch → job → the SLA clock with its holds |
| `E1` slot 7 close cycle | `E3` slot 4 | The close checklist, then the open items blocking it |
| `E2` stream margin | Cost breakdown by `MD-036` dimension | Transaction |
| `E4` any delivery metric | `E5` branch league on that metric | Branch console (`RP-004`) → job |
| `E5` peer ranked measure | **Blocked** for `R06` (`PRU-P06-15`) | — |
| `E7` slot 5 data quality | `RP-016` scorecard for the failing domain | The failing records |

### 4.5 Commentary slots

`XD-10`: every view carries a commentary slot with a named owner and a cadence. `RP-008` supplies the
structures; this pack allocates the ownership.

| View | Commentary owner | Cadence |
|---|---|---|
| `E1` | CEO office | Monthly |
| `E2` | Stream owner (`06-02` §3.5) | Monthly |
| `E3` | CFO | Monthly, and at close |
| `E4` | Operations Director | Monthly |
| `E5` | Operations Director | Quarterly — **`RP-011` `LT-11` prohibits monthly league commentary**, because monthly ranking noise invites gaming |
| `E6` | None — live views carry no commentary | — |
| `E7` | CTO, with Programme Manager for slots 7–9 | Monthly |

### 4.6 What is deliberately absent

| Not on an executive view | Why | Where it is |
|---|---|---|
| Individual employee or technician performance | An executive view ranking named individuals changes behaviour before it informs a decision, and `05-04` §5 restricts `technician_incentive_detail` | `RP-004` at branch level; personal scorecards in `P02` |
| Individual customer detail | No executive decision needs a named customer; `05-02` §10 `S2` and PDPA minimisation both point away | `P03` Customer 360 |
| Any `S3` field | `BRU-DAT-11` excludes `S3` from the analytical estate by default | Nowhere on `P06` |
| Marketplace seller names in a ranking | `BRU-ECM-04` already automates visibility consequences; an executive ranking adds nothing and creates a disclosure question | `RP-005` seller's own scorecard |
| A "total system health" composite score | A single composite hides which component failed; slots 1–3 of `E7` are separate for that reason | — |

### 4.7 Mobile

`04-00` `P06` commits to *"key dashboards optimised for phone, for managers away from a desk"*.
`XD-15` requires phone-first specification.

| Rule | Detail |
|---|---|
| Phone views | `E1`, `E3`, `E4`, `E5`, `E6` — the five a manager acts on away from a desk. `E2` and `E7` are desktop |
| Layout | **One metric per screen height**, vertical scroll, no horizontal scroll (`PS-05`) |
| Slot order | The phone order is the desktop order truncated at slot 5 — **never a different selection**, or the phone becomes a second dashboard with a second meaning |
| Drill | One level on phone; deeper drills prompt to open on desktop |
| Load | ≤ 5 s on 3G (`NFR-038` with `PS-07`), verified in `TS-014` |
| Freshness | Shown on every phone view; a stale view is flagged before its numbers are read (`XD-08`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Every metric on all seven views (`XD-04`) — and 8 of 250 are defined |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | The certified datasets behind them (`PRU-P06-02`) |
| **[`RP-007`](RP-007_Chart_Label_and_Visualisation_Standard.md)** | Chart type, colour and unit rendering (`XD-11`) |
| **[`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md)** | The whole of `E5` |
| **[`RP-015`](RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md)** | Baselines for `XD-12` comparators and `E1` slot 9 |
| [`RP-008`](RP-008_Report_Narrative_and_Commentary_Template_Set.md) | Commentary structures for `XD-10` |
| [`RP-012`](RP-012_Alert_Threshold_and_Anomaly_Rule_Register.md) | The alerts that fire off these metrics |
| `06-02` §1, §3, §5 | Objectives, benefit model and success criteria |
| `README` §Fourteen Revenue Streams | The `E2` row set |
| `UI-016` | `P06` labels and microcopy |
| `05-04` | Executive scope, and `PRU-P06-15` for `E5` |
| `NFR-038` | The 5-second load target |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly with the Executive; after every wave gate |
| Trigger for out-of-cycle review | A new revenue stream; a `06-02` target change; a metric restatement (`KD-25`); a director requesting a tenth metric (`XD-03` makes it a displacement decision) |
| Owner | BI Lead with the CEO office |
| Change control | Slot changes are recorded with the displaced metric named, so drift is visible |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`RP-001` defines 8 of 250 metrics and this pack cites 30.** `XD-04` and `XD-05` require every metric to be a defined, certification-labelled `RP-001` entry. **Most slots on all seven views would display `Provisional` today**, which is honest but not what a board expects | BI Lead | **W4 — the 30 metrics on these views are the priority subset of `RP-001` `O-02`** |
| **O-02** | **`E1` slot 9 and `E7` slot 7 report benefit realisation against a curve that cannot be computed.** 44 of 95 baselines are unmeasured (`RP-001` `O-06`), and `RP-015` is `P1`/W0 — already overdue. The interim is realised-benefit-on-measured-baselines with the excluded count stated, and **that is a materially different number from the one `06-02` §3.2 promises** | Programme with Finance | **W4 — but `RP-015` is needed at W0** |
| **O-03** | **`E6`'s real-time feed has no specification.** `PRU-P06-12` exempts "the scoped real-time board" from the warehouse rule without defining the scope, the feed, or its load ceiling. `TS-014` `PERF-NFR-033-01` and `PERF-NFR-034-01` test a 500-job board and 5-second GPS latency; **nothing states what the board may query against a production database or what happens under load** | Solution Architect with BI Lead | **W4 — before `E6` is built** |
| **O-04** | **`E7` slots 8 and 9 read from `TS-018`, and `TS-018` has no defect-tracking tool** (`AUDIT-014` TS-07, `TS-018` `O-02`). An executive view of the open-defect profile and gate position needs a queryable source, not a markdown form | CTO with QA Lead | **W4** |
| **O-05** | **`P06` is W4 and `RP-004`'s operational consoles are W1.** Executives are `R01`–`R05` and their `05-04` §2 access is `P03` **and** `P06`. **Between W1 and W4 the executive audience has consoles and no executive view**, so the interim answer to "is the company performing" is `RP-004`'s branch console — or a spreadsheet, which is the thing being removed | Programme Content Lead with BI Lead | **W1 — interim position needed** |
| **O-06** | **No usage telemetry target is set per view.** `04-00` sets weekly usage by managers above 90% for `P06` as a whole; **a view-level figure is what shows which of the seven is decoration** (`XD-02`). `RP-002` `O-06` records the same gap for reports | BI Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` metric-table addition applied per dashboard
- [x] **Seven dashboards specified, with `E1` as the board entry point and `E2`–`E7` reachable by drill so they cannot diverge**
- [x] Fifteen rules stated, including the nine-metric limit, mandatory action-if-wrong and comparator discipline
- [x] Every slot bound to an `RP-001` identifier; no inline calculation permitted
- [x] Drill paths specified rather than left to the tool, with `PRU-P06-09` permission re-evaluation
- [x] **`PRU-P06-15` treated as the design of `E5` rather than a footnote — 51+ branch managers can open it**
- [x] `E6` correctly placed under `PRU-P06-05`/`-12` as the sole warehouse exemption, carrying no metric definitions
- [x] Commentary ownership allocated per view, with the league deliberately quarterly
- [x] **What is deliberately absent stated with reasons — individual performance, customer detail, `S3` fields, composite scores**
- [x] Mobile specified phone-first, with the same slot order truncated rather than a different selection
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` 30 cited metrics undefined — outstanding; views would ship labelled `Provisional`**
- [ ] **`O-02` benefit realisation uncomputable — outstanding; blocks two slots**
- [ ] **`O-05` no executive view between W1 and W4 — outstanding**
- [ ] Named approvers recorded — **pending CEO and CTO**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
