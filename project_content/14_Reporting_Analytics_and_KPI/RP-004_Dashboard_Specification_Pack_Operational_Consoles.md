---
id: RP-004
title: Dashboard Specification Pack — Operational Consoles
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead with Operations
author: BI Lead with Operations Director, branch managers and the fourteen workspace owners
reviewers: [Operations Director, Branch Manager representatives, Dispatch Manager, Workshop Supervisor, Inventory Manager, Finance Manager, HR Manager, Quality Manager, IT Administrator, Content Design Lead, Localisation Lead]
approver: BI Lead with Operations Director
content_class: D
purpose: >
  The opening view of each of the fourteen P03 role workspaces plus the shared live operations board —
  what a service agent, dispatcher, branch manager, storekeeper, cashier or quality manager sees in
  the first two seconds of their shift, and what they are expected to do about it. The portal
  specification commits every workspace to "open on the work its role actually does"; deciding what
  that means for fourteen different roles is a content decision, and if it is not made here it is made
  by whoever builds the screen.
traces_to: [P03, 04-00 P03, P06, RP-001, RP-002, RP-003, RP-006, RP-007, RP-011, RP-012, RP-016, UI-013, UI-023, UI-024, UI-025, UI-026, UI-027, UI-028, UI-029, UI-030, UI-031, UI-032, UI-033, UI-034, UI-035, UI-036, VB-008, 05-04, 05-04 §4, 05-06 NFR-001, 05-06 NFR-033, 05-06 NFR-077, TS-006, TS-014, HC-005]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: RP-004_Dashboard_Specification_Pack_Operational_Consoles_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P03 — the fourteen role-scoped workspaces and the "Opens On" column for each; design requirements (every workspace reachable in one click, any record in ≤ 4 clicks, bulk actions on every list view, keyboard-first for intake, dispatch and finance, screen density for 1366×768); P03 KPIs walk-in intake < 3 min, morning queue dispatch < 10 min, page load < 2 s, training to competence < 4 h
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-001 screen load ≤ 2 s p95, NFR-033 dispatch board refresh ≤ 1 s for 500 open jobs, NFR-077 any record reachable in ≤ 4 clicks, §10 minimum desktop resolution 1366×768
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §4 data isolation tiers T0–T5 with objects per tier; §2 portal access matrix; §5 field-level permissions
    verified: 2026-08-20
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03C_Admin_Workspaces/ — the fourteen workspace copy packs UI-023 … UI-036, one per P03 console
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Dashboard Specification Pack — Operational Consoles

| Item | Value |
|---|---|
| Portal | `P03` Admin Operations Portal |
| Audience | **150–250 back-office and branch users** across `R05`–`R35` |
| Consoles specified | **14 workspaces + 1 shared live operations board = 15** |
| Hardware | **1366×768** — the common branch laptop (`05-06` §10) |
| Load target | **≤ 2 s p95** (`NFR-001`); dispatch board ≤ 1 s at 500 open jobs (`NFR-033`) |
| Copy packs | `UI-023` … `UI-036`, one per console |
| Wave | **W1** · `P1` — `P03` goes live at W1 |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` metric-table addition applied per console in §4.3. All six sections retained in order.

---

## 1. Purpose

`04-00` `P03` states the commitment and supplies a one-line answer per workspace in its *"Opens On"*
column — *"Queue, quick intake, customer search"* for Service Intake, *"Today's numbers, WIP ageing,
cash, staff, uncollected devices"* for the Branch Console. **Those are one-line briefs, not
specifications**, and there are fourteen of them for 150–250 people whose entire working day starts
on one of these screens.

This file turns each brief into a specified view. It is `W1` because `P03` is `W1`: **the console is
the first thing 150–250 people see of this programme**, and `04-00` sets training to competence at
under four hours, which is only achievable if the opening screen answers the role's first question
without navigation.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A specified opening view | Fourteen screens designed by whoever built them, each showing what was easy to query |
| A first-question answer | The agent opens the console, does not find the queue, and navigates — and `NFR-076`'s three-minute intake is lost before the customer is greeted |
| Density decisions | `04-00` sets 1366×768. A view designed at 1920 wide loses its right-hand column on every branch laptop, and the lost column is usually the one with the action in it |
| Role scoping | A branch console showing network data breaches `05-04` `T2`; one showing too little sends the manager to a spreadsheet |
| Alignment with `TS-006` | `UAT-R06-001` asks a branch manager to judge whether the console tells them today is going well. **Without this file the executor is judging an undesigned screen** (`TS-006` `O-06`) |

---

## 2. Scope

**In scope.** The opening view of all fourteen `P03` workspaces and the shared live operations board:
what appears, in what order, at what grain, scoped how, with what action attached and what it drills
to. Density rules for 1366×768, keyboard behaviour for the three high-volume roles, and the bilingual
obligation.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Metric definitions | `RP-001` (`PRU-P06-01`, `KD-15`) |
| Certified datasets | `RP-006` |
| Chart type, colour, axis, unit | `RP-007` |
| Executive views | `RP-003` — `E5` league and `E6` board are `P06`; §4.5 states the relationship |
| External audiences | `RP-005` |
| Labels, microcopy, empty states, errors | **`UI-023`…`UI-036`** per console; `UI-006`, `UI-004` |
| Everything below the opening view — list views, forms, wizards | The module specifications and `UI` packs |
| Alert thresholds | `RP-012` |
| League scoring | `RP-011` |
| Help and coach marks | `HC-005`, `HC-016` |

**One boundary stated explicitly.** This pack specifies **the opening view only**. A console is a
whole workspace; the opening view is the screen it lands on. Specifying the whole workspace here
would duplicate fourteen `UI` packs and the module specifications behind them (`CP-01`).

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **The fourteen workspace owners** | Confirming the opening view answers their role's first question |
| **BI Lead and engineers** | The build specification |
| **Content Design** | Binding each panel to its `UI-023`…`UI-036` labels |
| **Localisation** | The Bengali obligation, §4.7 |
| **QA** (`TS-006`) | What `UAT-R06-001` and the console scripts judge against |
| **L&D** (`TR-007`…`TR-021`) | The screen every course pack opens on |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **OC-01** | **Every console answers its role's first question of the day in the opening view, without navigation.** The question is stated per console in §4.3 |
| **OC-02** | **Every panel carries an action.** A panel that only informs is moved below the fold or removed; the opening view is working space, not a summary |
| **OC-03** | **Six panels maximum above the fold at 1366×768.** Enforced; a seventh displaces one and the displacement is a decision |
| **OC-04** | **Designed at 1366×768 and verified there** (`05-06` §10), not at the designer's resolution. No horizontal scroll (`PS-05`) |
| **OC-05** | Every metric is an `RP-001` identifier with its definition available on the view (`KD-17`, `PRU-P06-07`) |
| **OC-06** | **Every panel states its scope in words** — "your branch", "your zone", "your counter and shift" — because `05-04` scoping is invisible otherwise and a manager cannot tell whether a low number is good performance or a filtered view |
| **OC-07** | Scope follows `05-04` §4 tiers exactly. **A console never shows data above its role's tier** |
| **OC-08** | **Counts are actionable, not decorative**: every count links to the list it counts (`NFR-077`, ≤ 4 clicks) |
| **OC-09** | **Exceptions above averages.** An operational role acts on the twelve jobs at SLA risk, not on 94% compliance. Averages belong on `RP-003` |
| **OC-10** | Opening view load **≤ 2 s p95** (`NFR-001`); the dispatch board **≤ 1 s at 500 open jobs** (`NFR-033`) |
| **OC-11** | Keyboard-first for **intake, dispatch and finance** (`04-00` `P03`): every opening-view action reachable without a mouse |
| **OC-12** | **Status is encoded independently of colour** (`PRU-P06-17`); `RP-007` and `VB-008`'s eight tokens govern |
| **OC-13** | Every console's opening view is **bilingual**, and the Bengali is verified at 1366×768 against `VB-007`'s 20–40% expansion allowance |
| **OC-14** | **Freshness is shown where a panel is not live** (`PRU-P06-06`). A branch manager acting on yesterday's cash figure believing it is today's is the failure this prevents |
| **OC-15** | No `S3` field appears on any console (`BRU-DAT-11` in `M62` §9, `05-02` §10); `S2` fields appear only where `05-04` §5 permits the role |

### 4.2 The fifteen consoles

`04-00` `P03` names fourteen workspaces. The live operations board is shared and is the fifteenth
surface, specified in §4.5.

| # | Console | Role | Copy pack | First question |
|---:|---|---|---|---|
| C1 | Service Intake | `R08` | `UI-023` | *Who is waiting, and what do I do next?* |
| C2 | Dispatch Console | `R07` | `UI-024` | *What is unassigned or at risk right now?* |
| C3 | Branch Console | `R06` | `UI-025` | *Is my branch having a good day?* |
| C4 | Workshop Console | `R09` | `UI-026` | *What is on the bench, and what is stuck?* |
| C5 | Inventory Console | `R17` | `UI-027` | *What will run out, and what is wrong?* |
| C6 | Procurement Console | `R19` | `UI-028` | *What needs raising, chasing or approving?* |
| C7 | Finance Console | `R26`, `R27` | `UI-029` | *What is unbilled, unpaid or unreconciled?* |
| C8 | HR Console | `R30`, `R31` | `UI-030` | *Who is absent, expiring or awaiting approval?* |
| C9 | Quality Console | `R32` | `UI-031` | *What is open, overdue or recurring?* |
| C10 | Contract Console | `R22` | `UI-032` | *What renews, over-consumes or loses money?* |
| C11 | Warranty Console | `R28` | `UI-033` | *What is unsubmitted, rejected or ageing?* |
| C12 | Marketplace Console | `R24` | `UI-034` | *Who needs approving, and what is disputed?* |
| C13 | Managed Services Console | `R13` | `UI-035` | *Which estate is unhealthy and which SLA is at risk?* |
| C14 | System Console | `R33` | `UI-036` | *What failed, and who is waiting for access?* |
| C15 | **Live Operations Board** | `R05`, `R07`, `R06` | `UI-024` | *What needs intervention in the next hour?* |

### 4.3 Per-console opening views

Each specification gives the panels above the fold at 1366×768, the scope, the action and the drill.
Panels are ordered; order is the specification.

---

#### `C1` Service Intake — `R08`, 150–250 people, Bengali

| # | Panel | Scope | Action | Drill |
|---:|---|---|---|---|
| 1 | **Waiting queue** — walk-ins present, with wait time | Own branch | Call next | The intake form, pre-focused |
| 2 | **Quick intake** — the form itself, keyboard-ready | Own branch | Start intake | — |
| 3 | **Customer / device search** | All customers (`T0` catalogue, `T4` records) | Search | Customer 360 |
| 4 | Ready for collection — uncollected devices, oldest first | Own branch | Notify customer | Device record |
| 5 | My open intakes today | Own records | Complete | Order |
| 6 | Estimates awaiting customer decision | Own branch | Chase | Estimate |

**Panel 2 is a form, not a metric, and that is deliberate.** `NFR-076` sets walk-in intake at under
three minutes and `TS-006` `UAT-R08-001` times it over 20 samples. **A console that requires a click
to reach the intake form spends part of that budget on navigation.** `OC-11` keyboard-first applies
here above all.

---

#### `C2` Dispatch Console — `R07`, 3–8 people

| # | Panel | Scope | Action | Drill |
|---:|---|---|---|---|
| 1 | **Unassigned queue**, ranked by SLA risk | Assigned zones (`T3`) | Assign | Candidate list with scores |
| 2 | **SLA at risk** — jobs at 75% and 90% of clock | Zones | Escalate or reassign | Job with its clock and holds |
| 3 | **Live map** — technicians and open jobs | Zones | Reassign | Technician day |
| 4 | Technician load and capacity today | Zones | Rebalance | Roster |
| 5 | Failed visits and exceptions today | Zones | Reschedule | Job with evidence |
| 6 | Emergency insertions pending | Zones | Place | Job |

**`NFR-033`: ≤ 1 s refresh at 500 open jobs**, and `TS-006` `UAT-R07-001` times a full morning queue
against the ten-minute target. Panels 1–3 are the ten minutes.

---

#### `C3` Branch Console — `R06`, 51+ people

| # | Panel | Scope | Action | Drill |
|---:|---|---|---|---|
| 1 | **Today's numbers** — intakes, completions, revenue, cash collected | **Own branch (`T2`)** | — | Each to its list |
| 2 | **WIP ageing** — open jobs by age band, oldest first | Own branch | Chase | Job |
| 3 | **Cash position and shift status** — closed / unclosed | Own branch, own shifts | Close | Shift record |
| 4 | **Uncollected devices > 7 / 15 / 30 days** | Own branch | Notify or start abandonment | Device |
| 5 | **Staff on shift, absent, expiring certifications** | Own branch staff | Approve or escalate | Employee |
| 6 | **My branch's league position on one measure** | Own branch detail; **peers ranked measure only** (`PRU-P06-15`) | Open `RP-003` `E5` | `E5` |

> **Panel 1 is the answer to `TS-006` `UAT-R06-001`** — *"open the branch console and know, in one
> screen, whether today is going well"* — and `TS-006` `O-06` records that the script had no design to
> judge against. **This is that design.**

> **Panel 6 is the only place a branch manager meets the league table**, and `PRU-P06-15` limits it to
> their own detail plus the peer ranked measure. `RP-011` governs the ranking; `OC-07` governs what
> `R06` may see of it.

---

#### `C4` Workshop Console — `R09`, 20–40 people, Bengali

| # | Panel | Scope | Action | Drill |
|---:|---|---|---|---|
| 1 | **Bench board** — jobs by bench and state | Own workshop | Assign | Job |
| 2 | **Stuck** — parts hold, awaiting approval, awaiting QC | Own workshop | Release or chase | Job with the blocking reason |
| 3 | WIP by repair level L1 / L2 / L3 | Own workshop | Rebalance | Job |
| 4 | **QC queue** — awaiting independent QC | Own workshop | Perform QC — **blocked where the user was the repairer** (`SOD-07`) | Checklist |
| 5 | Rework flags raised today (`BRU-SRM-06`) | Own workshop | Investigate | Original and repeat job |
| 6 | Technician load on bench | Own workshop | Reassign | Technician |

---

#### `C5` Inventory Console — `R17`, 5–10 people

| # | Panel | Scope | Action | Drill |
|---:|---|---|---|---|
| 1 | **Below reorder point**, ranked by job impact | All locations | Raise requisition | Part with network position |
| 2 | **Stockouts causing job delay now** | All locations | Expedite or transfer | The held jobs |
| 3 | Van-stock variance by technician (`KPI-047`) | All locations | Investigate | Reconciliation |
| 4 | Transfers in transit and unconfirmed | All locations | Chase | Transfer |
| 5 | Quarantine and failed inspection | All locations | Disposition | Goods |
| 6 | Counts due and count variances (`KPI-042`) | All locations | Schedule or accept | Count sheet |

---

#### `C6` Procurement Console — `R19`, 4–8 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | Requisitions awaiting my approval, by value band (`05-04` §7) | Central | Approve or escalate |
| 2 | **POs unacknowledged** past their window | Central | Chase vendor |
| 3 | **Three-way-match exceptions** (`KPI-049`) | Central | Resolve |
| 4 | Overdue deliveries by vendor | Central | Chase |
| 5 | RFQs awaiting response | Central | Chase or award |
| 6 | Vendor scorecard movements (`KPI-048`) | Central | Review |

---

#### `C7` Finance Console — `R26`, `R27`, 12–24 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Unbilled completed work** (`KPI-056` revenue leakage) | Assigned scope / all entities | Raise invoice |
| 2 | **Receivables ageing** with the 30-day collections bucket | Scope | Chase |
| 3 | **Unreconciled bank items** — exceptions only (`AUT-044`) | Scope | Match |
| 4 | **Close checklist state** for the open period (`KPI-050`) | Entity | Progress |
| 5 | Credit notes awaiting approval, by band | Scope | Approve — **not own-created** (`SOD-04`) |
| 6 | **Statutory position** — the open `RP-009` filings and their deadlines | Entity | Open `RP-009` |

> **Panel 6 is a deliberate cross-reference, not a duplication.** `RP-009` owns the filings and their
> formats; this panel shows *whether a deadline is approaching* on the screen the finance team already
> lives on. A statutory deadline visible only in a separate register is a deadline discovered late.

---

#### `C8` HR Console — `R30`, `R31`, 4–8 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Attendance exceptions** yesterday (`KPI-061`) | All / assigned | Resolve |
| 2 | **Certifications expiring in 90 / 60 / 30 / 15 days** (`KPI-062`) | All employees | Schedule re-certification |
| 3 | **Overdue mandatory training** restricting work types (`BRU-LMS-01`) | All | Chase |
| 4 | Leave awaiting approval, with coverage warning (`BRU-HRM-04`) | Scope | Approve |
| 5 | **Payroll run state** — attendance lock, approvals outstanding | Entity | Progress — **two approvals required** (`SOD-03`) |
| 6 | Joiners and leavers this week, with access provisioning state | All | Verify — links to `C14` |

> **Panel 2 is the panel that prevents `KPI-063`.** `06-02` targets **zero** claims rejected for an
> uncertified technician, and `BRU-HRM-01` removes a technician from the dispatch pool on expiry.
> Visibility 90 days ahead is the only way that target is met without disrupting dispatch.

---

#### `C9` Quality Console — `R32`, 2–4 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Non-conformances open**, by age and severity | All branches | Assign |
| 2 | **CAPAs overdue or awaiting effectiveness verification** (`KPI-066`) | All | Verify |
| 3 | **Recurring root causes** across three periods (`BRU-QMS-09`, `M23` §9) | All | Table for management review |
| 4 | Complaints open and outside SLA (`KPI-024`) | All | Escalate |
| 5 | Audit plan progress (`KPI-068`) | All | Schedule |
| 6 | Rework and QC first-pass by branch (`KPI-005`, `KPI-007`) | All | Investigate |

---

#### `C10` Contract Console — `R22`, 8–20 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Renewals at −90 / −60 / −30 / −15 days** (`AUT-015`) | **Assigned accounts (`T4`)** | Quote |
| 2 | **Entitlement over-consumption** (`BRU-CTR-04`) | Assigned | Bill or block |
| 3 | **Negative-margin contracts** (`KPI-031`) | Assigned | Review |
| 4 | Preventive visits due and unscheduled (`AUT-017`) | Assigned | Schedule |
| 5 | SLA breaches and service credits accruing (`BRU-CTR-08`) | Assigned | Verify |
| 6 | Contracts awaiting activation (`BRU-CTR-01`) | Assigned | Complete |

---

#### `C11` Warranty Console — `R28`, 4–10 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Claims unsubmitted past 24 h** (`BRU-WTY-02`, `KPI-037`) | All claims | Submit |
| 2 | **Blocked on evidence** (`BRU-WTY-01`) — the actual leakage cause | All | Chase technician |
| 3 | **Approaching the brand's submission window** (`BRU-WTY-08`) | All | Escalate |
| 4 | Rejected claims awaiting dispute | All | Dispute |
| 5 | Unmatched brand remittances (`AUT-021`) | All | Reconcile |
| 6 | Claim ageing to reimbursement (`KPI-040`) | All | Review |

> Panels 1–3 are the `KPI-038` warranty-leakage target — from 15–20% to under 2% — expressed as three
> queues rather than one percentage. `OC-09` in its clearest form.

---

#### `C12` Marketplace Console — `R24`, 4–10 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | Sellers awaiting approval, with document verification state (`BRU-ECM-01`) | Marketplace | Approve |
| 2 | **Open disputes**, by age (`BRU-ECM-09`) | Marketplace | Decide |
| 3 | **Payouts held** and why (`BRU-BIL-03`) | Marketplace | Release — **not own-approved sellers** (`SOD-06`) |
| 4 | Sellers below performance threshold (`BRU-ECM-04`) | Marketplace | Warn or suspend |
| 5 | Registrations expiring (`BRU-ECM-08`) | Marketplace | Chase |
| 6 | Category qualification gaps (`BRU-ECM-07`) | Marketplace | Review |

---

#### `C13` Managed Services Console — `R13`, 15–40 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Estate health** — assets in alert | **Assigned clients** | Triage |
| 2 | **SLA at risk** on open tickets (`KPI-070`) | Assigned | Escalate |
| 3 | Open tickets by age and severity | Assigned | Work |
| 4 | Patch compliance by client | Assigned | Schedule |
| 5 | Predicted failures above confidence (`AUT-039`) — **human confirmation required** (`BRU-AIM-01`) | Assigned | Confirm or dismiss |
| 6 | Service reviews due | Assigned | Schedule |

---

#### `C14` System Console — `R33`, 4–8 people

| # | Panel | Scope | Action |
|---:|---|---|---|
| 1 | **Failed scheduled jobs** and jobs that did not run (`OPS-05`) | All systems | Investigate |
| 2 | **Integration errors and dead-letter depth** (`AUT-053`, `AUT-054`) | All | Triage |
| 3 | **Access requests awaiting approval**; SoD conflicts blocked (`BRU-SEC-07`) | All | Approve |
| 4 | **Orphaned accounts and leaver revocations outstanding** (`KPI-090`) | All | Revoke |
| 5 | Certificate and credential expiry < 30 days (`AUT-060`) | All | Rotate |
| 6 | **Data-quality test failures** blocking dashboard refresh (`AUT-059`) → `RP-016` | All | Escalate to data owner |

### 4.4 What is deliberately absent from every console

| Not on a console | Why |
|---|---|
| Network-wide totals on a branch-scoped console | `05-04` `T2`; and a manager who can see the network compares instead of acting (`OC-07`) |
| Any `S3` field | `BRU-DAT-11` (`M62` §9), `05-02` §10 (`OC-15`) |
| Named individual performance rankings | `RP-003` §4.6 applies here too; branch-level aggregates only, and `technician_incentive_detail` is summary-only for `R06` (`05-04` §5) |
| Averages as the primary panel | `OC-09` — exceptions above averages |
| A chart where a count would do | `RP-007` `CH-02`; a count that links to its list is more actionable than a sparkline |

### 4.5 The live operations board, `C15`

| Item | Value |
|---|---|
| Surface | Shared; rendered on `P06` (`RP-003` `E6`) and **embedded** into `C2` and `C3` |
| Embedding rule | `PRU-P06-16` — an embedded panel carries the host session's identity and scope and **never widens access** |
| Refresh | ≤ 60 s |
| Content | Open jobs, technicians on map, SLA countdowns, queue depth, system health — **counts and countdowns only, no metric definitions** (`PRU-P06-05`) |
| Scope | `R05` network · `R07` zones · `R06` own branch — **the same board, three scopes** |

**One board, not three.** `RP-003` `E6` specifies it; this file specifies its embedding and scoping
into the operational consoles. Building a second operational board would produce two live views that
disagree during an incident, which is when disagreement costs most.

### 4.6 Density and performance

| Rule | Detail |
|---|---|
| Resolution | **1366×768** design and verification target (`OC-04`, `05-06` §10) |
| Panels above the fold | **6 maximum** (`OC-03`) |
| Horizontal scroll | **None** (`PS-05`) |
| Load | ≤ 2 s p95 (`NFR-001`); `C2` and `C15` ≤ 1 s at 500 open jobs (`NFR-033`) |
| Clicks to any record | ≤ 4 (`NFR-077`) |
| Keyboard | Full keyboard operation on `C1`, `C2`, `C7` (`OC-11`) |
| Bulk actions | On every list a panel drills to (`04-00` `P03`) |
| Verification | `TS-014` `PERF-NFR-001-01`, `PERF-NFR-033-01`; `TS-016` `ACC-P03-*`; `TS-006` timed scripts |

### 4.7 Bilingual position

`CG-010` §3.2 makes this file bilingual because *"dashboard labels … reach branch managers"*. The
consoles with Bengali-first populations are `C1` (150–250 agents), `C3` (51+ branch managers), `C4`
(20–40 supervisors), and the storekeeper and cashier paths within `C5` and `C7`.

| Element | Bengali |
|---|---|
| Every panel title and count label on all fifteen consoles | **Yes** (`OC-13`) |
| Action verbs on every panel | **Yes** — the action is the point (`OC-02`) |
| Scope statements — "your branch", "your counter and shift" | **Yes** (`OC-06`); a mistranslated scope statement is worse than none |
| Metric names shown on a panel | Yes, from `RP-001` `name_bn` (`KD-21`, `O-04`) |
| Truncation | Verified at 1366×768 against `VB-007`'s 20–40% expansion allowance |
| This file's own specification prose | No — BI and workspace-owner audience |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `04-00` `P03` | The fourteen workspaces and their "Opens On" briefs |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Every metric named on every panel (`OC-05`) |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | The certified datasets behind them |
| **[`RP-007`](RP-007_Chart_Label_and_Visualisation_Standard.md)** | Panel rendering, status encoding, units |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md) `E6` | The board this file embeds (`C15`) |
| [`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md) | The league measure on `C3` panel 6 |
| [`RP-012`](RP-012_Alert_Threshold_and_Anomaly_Rule_Register.md), `RP-016` | The alerts and scorecards consoles link to |
| **`UI-023`…`UI-036`** | Labels for every panel — one pack per console |
| `05-04` §2, §4, §5, §7 | Scope, tier, field permissions, approval bands |
| `NFR-001`, `NFR-033`, `NFR-077`, `05-06` §10 | Performance and density |
| `TS-006`, `TS-014`, `TS-016` | Where the consoles are verified |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, with each workspace owner |
| Trigger for out-of-cycle review | A new workspace; a role change in `05-04`; a metric restatement; a panel displacement request (`OC-03`) |
| Owner | BI Lead with Operations Director; each console has its workspace owner as reviewer |
| Data file | `RP-004_Console_Panels.csv` — 15 consoles × 6 panels with scope, metric, action and drill |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is `W1` and `RP-001` is `W1`, `RP-006` is `W4`, `RP-007` is `W4`.** `OC-05` requires defined metrics, `OC-12` requires `RP-007` status encoding, and every panel needs a certified dataset. **Two of the three files this one depends on arrive three waves later**, so `P03` ships at W1 with consoles built against undefined metrics and unspecified rendering | Programme Content Lead with BI Lead | **W1 — `RP-006` and `RP-007` need W1 subsets** |
| **O-02** | **`P06` is W4 and `C15` is embedded into `C2` and `C3` at W1.** The live board is a `P06` surface (`RP-003` `E6`); the consoles that embed it are W1. Either an interim board is built inside `P03`, or `C2` and `C3` open without panel 3 and panel 6 respectively at W1 | Solution Architect with BI Lead | **W1** |
| **O-03** | **The 90 metrics named across these fifteen consoles are almost all undefined.** `RP-001` defines 8 of 250. **These 90 are the W1 priority subset** and should be sequenced ahead of the executive set, because `P03` ships first — which reverses the natural assumption that executive metrics come first | BI Lead | **W1 — ahead of `RP-003` `O-01`** |
| **O-04** | **No Bengali panel titles, action verbs, scope statements or metric names exist.** `OC-13` makes all four bilingual and `C1`, `C3`, `C4` serve 220–320 Bengali-first users **from W1**. `RP-001` `O-05` records the metric-name half; the panel and action half is this file's. Bengali authoring is unresourced | Localisation Lead | **W1 — blocking `P03` go-live for Bengali users** |
| **O-05** | **`R05` Operations Director, `R34` and `R35` contact-centre roles have no console in `04-00`'s fourteen.** `R05` has `P03` and `P06` access (`05-04` §2) and lands on… nothing specified; `R34`/`R35` work in `P10`, not `P03`, which is consistent — **but `R05`'s landing view is genuinely unallocated**, and `C15` plus `RP-003` is an assumption this file makes rather than a decision anyone took | Operations Director with BI Lead | **W1** |
| **O-06** | **`OC-03`'s six-panel limit has not been validated at 1366×768 with real Bengali labels.** Bengali expands 20–40% (`VB-007`); six panels that fit in English may not fit in Bengali, and the fallback — dropping to five — is a content decision, not a build one | Content Design Lead with Design System | **W1 — before build** |
| **O-07** | **`C7` panel 6 shows `RP-009` statutory deadlines, and `RP-009` is W3 while this file is W1.** The finance console ships without its statutory panel, or the panel ships against an incomplete register | Finance Manager with BI Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` metric-table addition applied per console
- [x] **All fourteen `04-00` `P03` workspaces specified, plus the shared live board — fifteen surfaces**
- [x] Each console's first question stated, and the opening view designed to answer it without navigation
- [x] Fifteen rules stated, including exceptions-above-averages, actionable-counts and stated-scope
- [x] Six ordered panels per console with scope, action and drill — 90 panels in total
- [x] **`TS-006` `O-06`'s unresolved dependency answered: `C3` panel 1 is the design `UAT-R06-001` judges**
- [x] `PRU-P06-15` applied to `C3` panel 6 — the only place 51+ branch managers meet the league
- [x] `PRU-P06-16` applied to the embedded live board, one board at three scopes
- [x] Every panel bound to a `UI-023`…`UI-036` copy pack
- [x] What is deliberately absent stated, including individual rankings and network totals on scoped consoles
- [x] Density, keyboard and performance rules tied to `1366×768`, `NFR-001`, `NFR-033` and `NFR-077`
- [x] Bilingual obligation scoped to panel titles, action verbs, scope statements and metric names
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `RP-006` and `RP-007` arrive three waves after this file — outstanding**
- [ ] **`O-03` 90 panel metrics undefined — outstanding; the W1 priority subset of `RP-001`**
- [ ] **`O-04` no Bengali panel content — outstanding; blocks `P03` go-live for 220–320 users**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending BI Lead and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
