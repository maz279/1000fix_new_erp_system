---
id: GV-004
title: Integrated Programme Plan & Master Schedule
category: 00 — Programme Governance & Control
code: GV
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Programme Management Office
approver: ERP Steering Committee
standards_basis: ISO 21502:2020 §7.3 planning · ISO 21503:2022 §programme planning · PMBOK Guide 7th Edition (Planning & Measurement performance domains) · PRINCE2 7th Edition (2023) plans practice · Critical path method
traces_to: PGD-000 GV-004 · audit finding M-09 (wave capacity not validated) · C-02 (M32–M67 have no wave) · AF-08 · GV-003 decisions D-019, D-020
depends_on: GV-001, GV-002, GV-003
verified_on: 2026-08-18
enumerated_on: 2026-08-18 02:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# GV-004 — Integrated Programme Plan & Master Schedule
# 1000FiX ERP System & Portal Suite v2.0

### Category 00 · Code `GV` · ISO 21502:2020 · PMBOK 7 · PRINCE2 7

---

> **The finding this document was written to close is `M-09`:** *"`06-01` assigns waves without
> checking whether the wave's module effort fits the wave's team-weeks. Add a capacity check per
> wave once totals are restated."* The totals are now restated and counted. **The check has been
> performed and the plan does not pass it.** §5 shows the arithmetic.

---

## 1. Purpose

This document converts the wave *shape* in `06-01` into a plan: a work breakdown, a dependency
network, a critical path, a resource-loaded schedule, and a capacity validation that says whether
the work fits the people in the time available.

`06-01` is a good roadmap. It states what each wave delivers, in what geography, with what team,
and what evidence closes its gate. What it does not do — and what a roadmap is not required to do
— is arithmetic. This document does the arithmetic, and reports the result without adjustment.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The programme work breakdown structure to level 3, and the WBS dictionary rules |
| 2 | The dependency network and the **critical path** |
| 3 | The resource-loaded schedule: demand against capacity, wave by wave |
| 4 | **The capacity validation closing `M-09`**, with the method and the working shown |
| 5 | The scheduling gaps: 37 modules with no wave; 1,816 requirements with no wave |
| 6 | Milestones, wave gate dates and float |
| 7 | Schedule risk, buffer policy and the re-planning trigger |
| 8 | What the plan cannot yet contain, and why |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The estimation **method** and the resource plan | `GV-007` | This document consumes effort figures; `GV-007` derives them |
| The cost of the schedule | `GV-008` | Time and money are baselined separately so that a schedule change is visibly a cost change |
| Wave gate **criteria** and their evidence standard | `GV-009` | This document places the gates in time; `GV-009` says what passing one means |
| Sprint-level planning, story points, velocity | `BE-008` | A master schedule that reaches into sprints is a schedule nobody can maintain |
| Rollout sequence across the 51+ branches | `RL-004` | Site-by-site rollout is a release activity |
| The module dependency **graph** — which module technically requires which | `AR-006` | **This is a hard dependency for this document and it does not exist.** See §4.4 |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Steering Committee** | The plan they approve, and the capacity finding they must respond to |
| **Board** | The evidence behind `D-014` — the schedule consequence of the counted effort position |
| **Programme Director / PMO** | The operating plan and the re-planning triggers |
| **Squad leads** | What their squad owes, in which wave |
| **Implementation vendor** | The delivery shape they are being asked to commit to, and the capacity assumption underneath it |
| **Business owners** | When their category lands, and when their people are needed |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / concept | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21502:2020** §7.3 | Planning: scope decomposition, sequencing, resourcing, integrated plan | §3 WBS, §4 network, §5 resourcing, §6 integrated schedule | None |
| **ISO 21503:2022** | Programme planning; component projects; benefit-driven sequencing | Waves are treated as component projects with their own gates | None |
| **PMBOK Guide 7th Edition** | *Planning* and *Measurement* performance domains; progressive elaboration | Waves 1–4 are planned to level 3; Waves 5–9 to level 2, pending `D-017` | Deliberate: planning Waves 5–9 in detail against an unapproved scope would be waste |
| **PRINCE2 7th Edition (2023)** | Plans practice: Programme / Stage / Team plans; product-based planning; **tolerance** | Master schedule = programme plan; wave plan = stage plan; sprint = team plan | Product-based planning is applied at wave level only; module specifications already act as product descriptions |
| **Critical path method** | Forward/backward pass; float; near-critical identification | §4.3 identifies the critical path and §4.5 the near-critical chains | Durations are derived from effort and assumed capacity, not from independently estimated activity durations — stated as a limitation at §8 |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| Implementation Roadmap & Phasing | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | Nine waves, modules and portals per wave, team composition per wave, geography, rollout pattern, contingency |
| KPI, Benefits & Acceptance Criteria §4 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` | 70 wave-gate criteria across nine gates |
| Risks… §3 | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` | 35 dependencies with owners and needed-by dates |
| Module specifications — `Effort estimate` row | `../../1000fix_ERP_Module/03_Modules/**/M*.md`, `P*.md` | **Directly summed**: 67 modules = 1,544 PW; 12 portals = 298 PW |
| Category H Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-07` | 1,513 PW measured across 65 files; `M-09` capacity check outstanding |
| Documentation Audit | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-06` | `M-09`; `C-02` — M32–M67 have no wave allocation |
| Decision Log | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) | `D-019` module identifier ambiguity; `D-020` the 37 unscheduled modules |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it |
|---|---|---|
| **`M-09`** | `00-06` | §5 performs the capacity check per wave, states the method, shows the working, and reports that **Waves 1, 2 and 4 are over capacity and Waves 6–9 are under-loaded** |
| `C-02` *(schedule half)* | `00-06` | §5.4 quantifies the consequence: **763 PW across 37 modules has no wave**. `C-02` identified the register gap; the schedule gap had not been measured |
| `AF-08` *(schedule half)* | `AUDIT-001` | §5.1 uses counted effort, not any of the three circulating figures |
| `RSK-005` | `00-04` | §7.3 sets the contingency policy the risk's mitigation requires |
| **New — `PGD-A2-04`** | this document | `06-01` allocates **1,180 requirements** across nine waves. The estate holds **2,996** distinct `FR-` identifiers. **1,816 requirements — 61% — have no wave** |
| **New — `PGD-A2-05`** | this document | `06-01` schedules module identifiers whose meaning changed in the 67-module architecture. `M20` and `M30` are ambiguous. Raised as `D-019` |

---

## 3. Work Breakdown Structure

### 3.1 Decomposition rules

| Rule | Provision |
|---|---|
| `WBS-01` | Decomposition is by **deliverable**, not by activity. A WBS element names a thing that exists when it is done |
| `WBS-02` | **100% rule** — the children of an element sum to the element, with nothing extra |
| `WBS-03` | Every level-3 element has exactly one accountable squad and one business owner |
| `WBS-04` | A level-3 element carries an effort figure **counted from its specification**, never estimated in the plan |
| `WBS-05` | Work with no WBS element is not in the plan and will not be resourced. **This is the rule that makes §5.4 visible rather than absorbed** |

### 3.2 The structure

```
1000FiX ERP Programme (FIX-ERP2)
│
├── 1  GOVERNANCE & CONTROL                                    ~ see GV-007
│   ├── 1.1  Charter, governance, decision log                 GV-001…GV-003
│   ├── 1.2  Planning, estimation, budget                      GV-004, GV-007, GV-008
│   ├── 1.3  Assurance and audit                               GV-010
│   └── 1.4  Documentation & configuration control             GV-011
│
├── 2  ENGINEERING DEFINITION  ◄── 127 documents, UNESTIMATED (PGD-A1-05, D-021)
│   ├── 2.1  Requirements        RQ-001…RQ-010                 10 documents
│   ├── 2.2  Architecture        AR-001…AR-013                 13 documents
│   ├── 2.3  Data                DA-001…DA-009                  9 documents
│   ├── 2.4  Integration         IN-001…IN-008                  8 documents
│   ├── 2.5  Security & privacy  SC-001…SC-011                 11 documents
│   ├── 2.6  Experience          UX-001…UX-008  ◄── plus ~660–1,500 screens, UNESTIMATED
│   └── 2.7  Build standards     BE-001…BE-009                  9 documents
│
├── 3  BUILD                                                   1,842 PW counted
│   ├── 3.1  Category A  Service Delivery & Operations          7 modules   206 PW
│   ├── 3.2  Category B  Customer Engagement                    7 modules   148 PW
│   ├── 3.3  Category C  Commercial, Pricing & Revenue          9 modules   262 PW
│   ├── 3.4  Category D  Circular & Asset-Based                 3 modules    60 PW
│   ├── 3.5  Category E  Supply Chain & Inventory               6 modules   119 PW
│   ├── 3.6  Category F  Asset, Equipment & Facilities          5 modules   114 PW
│   ├── 3.7  Category G  Finance & Treasury                     8 modules   185 PW
│   ├── 3.8  Category H  People & Workforce                     7 modules   124 PW
│   ├── 3.9  Category I  Governance, Risk, Quality & Knowledge  4 modules    78 PW
│   ├── 3.10 Category J  Data, Analytics & Intelligence         4 modules    97 PW
│   ├── 3.11 Category K  Platform & Technology                  7 modules   151 PW
│   └── 3.12 Portals & Applications                            12 portals   298 PW
│
├── 4  CONTENT  ◄── workstream 5, GV-001 §6.3                  520–775 PW, UNBUDGETED (AF-09)
│   ├── 4.1  Master data & configuration                       48 files
│   ├── 4.2  UI copy, notifications, help                      88 files
│   ├── 4.3  Documents, templates, statutory forms             44 files
│   ├── 4.4  SOPs, knowledge, training                         74 files
│   ├── 4.5  Legal, policy & compliance                        24 files
│   ├── 4.6  Localisation (Bengali)                            18 files
│   └── 4.7  Migration, test, reporting, ops, ecosystem       181 files
│
├── 5  DATA MIGRATION                                          MG-001…MG-007
│   ├── 5.1  Legacy profiling — 48 sources, ALL UNPROFILED     AUDIT-011
│   ├── 5.2  ETL build and reconciliation
│   └── 5.3  Mock migrations, cutover, rollback
│
├── 6  INFRASTRUCTURE & PLATFORM                               PE-001…PE-009
│
├── 7  QUALITY & TEST                                          QA-001…QA-011
│
├── 8  CHANGE, TRAINING & ADOPTION                             CH-001…CH-005
│
└── 9  TRANSITION & OPERATIONS                                 RL-001…RL-006, SV-001…SV-006
```

**Category effort verification.** The eleven category subtotals in branch 3 were produced by
summing the `Effort estimate` row of each module file and grouping by category folder:
206 + 148 + 262 + 60 + 119 + 114 + 185 + 124 + 78 + 97 + 151 = **1,544 PW**, which equals the
direct 67-file sum. Adding 3.12 gives **1,842 PW**. Recounted immediately before issue per
`PG-M10`.

> **Recorded, not smoothed over.** The first draft of this table carried **258** for Category C and
> **155** for Category K. The total was right and two of the eleven components were wrong — the
> error is invisible in a correct total, which is exactly why `PG-M10` requires the components to
> be regenerated and not merely reconciled. Caught by the pre-issue recount. Logged as
> `PGD-A2-13`.

> **Branches 1, 2, 4 carry no effort figure because none exists.** Branch 2 is 127 documents with
> no estimate (`PGD-A1-05`); branch 4 is 520–775 PW with no budget (`AF-09`); branch 1 has never
> been sized at all. `WBS-05` means they will not be resourced until `GV-007` sizes them. That is
> the intended, visible consequence.

---

## 4. Dependencies and the Critical Path

### 4.1 Dependency classes

| Class | Meaning | Example |
|---|---|---|
| **Technical** | B cannot be built until A exists | Nothing transacts before `M29` identity and `M28` integration |
| **Decision** | Work is blocked until a `D-nnn` is taken | All data-layer architecture waits on `D-013` |
| **Artefact** | Work is blocked until a guiding document exists | No build contract before `RQ-001`; no build backlog before `BE-005` |
| **External** | A third party must act | bKash, Nagad, NBR, brand partners — `DEP-16`…`DEP-30` |
| **Capacity** | Work is blocked by people, not by logic | UAT is blocked by super-user availability — `CON-12`, `RSK-001` |
| **Regulatory** | A statutory deadline constrains the date | PDPA enforcement ~13 May 2027, inside Wave 4 |

### 4.2 The blocking set before Wave 1 can start

| # | Predecessor | Class | Owner | Blocks |
|---|---|---|---|---|
| 1 | `D-001` charter approval | Decision | Board | Everything |
| 2 | `GV-002` Steering Committee constituted | Decision | CEO | Any approval of anything (`PGD-A1-09`) |
| 3 | `D-013` split-residency architecture + `DEP-31` legal opinion | Decision + External | DP Forum → Board | `DA-001` schema · `SC-007` · `PE-001` network · therefore all persistent-state build |
| 4 | `RR-002` identifier convention | Artefact | Enterprise Architecture | `BE-005` CD register → the build backlog |
| 5 | `BE-005` CD master register | Artefact | Enterprise Architecture | **Build backlog creation.** 48 identifiers currently collide |
| 6 | `RQ-001` SRS baselined | Artefact | Enterprise Architecture | The implementation contract; test derivation |
| 7 | `RQ-003` fit-gap | Artefact | Enterprise Architecture | The cost model — what Odoo already does |
| 8 | `AR-001` SAD + `AR-006` dependency map | Artefact | ARB | Wave sequencing validity (§4.4) |
| 9 | `MG-002` legacy profiling | Artefact | Migration lead | W1 gate criterion `G1-05` (customer and device data migrated and reconciled) |
| 10 | `D-002` super-user availability confirmed | Decision | Board | Every UAT, therefore every gate |
| 11 | 48 master data files (`MD-*`) | Content | Content Council | **Odoo cannot be configured without them** (`AF-09`) |
| 12 | `DEP-19` WhatsApp Business API, `DEP-20` SMS gateways | External | CTO | W1 notification delivery |

### 4.3 The critical path

Derived from §4.2 and the wave logic in `06-01` §1. Durations in weeks; the chain is expressed
from programme start (T0 = charter approval).

```
T0 ──► GV-002 constituted ──► D-013 legal opinion (DEP-31) ──► DA-001 schema ──► W1 build
  2wk        2wk                      6–10 wk  ◄── LONGEST SINGLE LEAD          17.4 wk
                                          │
                                          └──► SC-007 residency design ──► PE-001 network
                                                                    (parallel, joins W1)

  ┌── RR-002 (2wk) ──► BE-005 (3wk) ──► build backlog ─┐
  │                                                     ├──► W1 build
  └── RQ-001 SRS (6–8wk) ──► CO-003 SoW ──► contract ──┘
                                              6–10 wk

  W1 ──► W2 ──► W3 ──► W4 ──► W5 ──► W6 ──► W7 ──► W8 ──► W9
 17.4   17.4   21.7   21.7   17.4   17.4   17.4   17.4    8.7   = 156.5 weeks = 36 months
   │      │      │      │
   │      │      │      └─ PDPA enforcement ~13 May 2027 lands INSIDE W4
   │      │      └─ DEP-24 NBR e-VAT spec ─ external, W4
   │      └─ DEP-08 technician devices ─ D-011 unresolved
   └─ G1 gate: customer + device migration reconciled ◄── needs MG-002, all 48 sources unprofiled
```

**The critical path is not the build.** It is:

> `D-001` charter → `GV-002` constitution → `DEP-31` legal opinion → `D-013` residency decision →
> `DA-001` database schema → Wave 1 build → the wave chain to Wave 9.

**Pre-build critical path length: 10–14 weeks**, of which 6–10 weeks is the external legal opinion
at `DEP-31` — the longest single lead time in the programme and the one over which 1000FiX has
least control. It has been outstanding since 2026-08-12.

> **Consequence.** The 36-month horizon in `GV-001` §3.1 is measured from *kickoff*. On the current
> position, kickoff is **10–14 weeks** away at best, and Month 36 becomes Month 39–40 in calendar
> terms. This is inside the +3-month programme tolerance (`GV-001` §8.1) but consumes all of it
> before a line of code is written.

### 4.4 The dependency map that does not exist

`AR-006` (Module Dependency Map & Build Sequence) is ⛔ in `PGD-000` and is a **hard input** to
this document. `_MODULE_TEMPLATE` §16.3 requires *"no prerequisite in a later wave"* — a rule that
cannot be verified across 67 modules without the graph.

**What that means for this plan, stated plainly:** the wave sequence in §6 is inherited from
`06-01` and is *plausible* — identity and integration first, data-dependent AI last — but it is
**unverified**. A cycle or a back-dependency in the 67-module graph would not be visible today.
The plan is therefore issued as **provisional on `AR-006`**, and §7.4 makes its arrival a
re-planning trigger.

### 4.5 Near-critical chains

| Chain | Float | Why it matters |
|---|---|---|
| `RQ-001` SRS → `CO-003` SoW → vendor contract | ~2 weeks behind the residency chain | If the legal opinion arrives early, this becomes critical |
| `MG-002` legacy profiling (48 sources) → W1 gate `G1-05` | ~4 weeks | Profiling has not started. All 48 sources unprofiled (`AUDIT-011`) |
| 48 `MD-*` master data files → W1 configuration | ~3 weeks | Unbudgeted (`AF-09`). Odoo cannot be configured without them |
| `SC-003` DPIA → W2 customer-transcript processing | ~W2 | Audit `HC` records W2 transcript mining **with no confirmed legal basis** |
| `DEP-22` brand partner claim formats (17+ brands) → W4 | ~W4 | 17+ counterparties; the figure itself is unverified (`H2-12`) |

---

## 5. Capacity Validation — Closing `M-09`

### 5.1 Method

Stated in full so the result is reproducible rather than assertable.

| Step | Method |
|---|---|
| 1 | **Demand.** Sum the `Effort estimate` row of every module and portal specification. Enumerated 2026-08-18 02:06 (+06): modules 1,544 PW, portals 298 PW |
| 2 | **Allocation.** Assign each module's and portal's full effort to the **first** wave in which `06-01` §3 names it. Modules named again in a later wave ("complete", "core") are counted once, at first appearance |
| 3 | **Capacity.** From `06-01` §4, count only **build-capable** FTE: Senior Odoo Developer, Flutter/Mobile, Frontend, DevOps/Platform, Data/BI, AI/ML. Programme Manager, Solution Architect, Business Analyst, QA Engineer and Change & Training Lead are excluded from build capacity and shown separately |
| 4 | **Duration.** Wave months × 4.345 weeks |
| 5 | **Delivery factor.** Gross team-weeks × **0.78**, allowing for leave, public holidays, ceremonies, defect remediation and hypercare. This is a conventional figure and is declared as an assumption, not a measurement |
| 6 | **Compare.** Demand ÷ effective capacity per wave |

> **Assumption `GV-004-A1`.** The 0.78 delivery factor is an industry convention, not a 1000FiX
> measurement. The programme has no velocity history. `BE-008` must establish a measured factor by
> the end of Wave 1, at which point this analysis is re-run. **A lower factor makes every
> conclusion below worse, not better.**

### 5.2 Capacity against demand, wave by wave

| Wave | Months | Weeks | Build FTE | Gross team-weeks | Effective @0.78 | Demand (PW) | Ratio | Verdict |
|:--:|:--:|---:|---:|---:|---:|---:|---:|---|
| W1 | 1–4 | 17.4 | 3 | 52.2 | **40.7** | **217** | **5.33×** | ❌ **Infeasible** |
| W2 | 5–8 | 17.4 | 7 | 121.8 | **95.0** | **167** | **1.76×** | ❌ Over capacity |
| W3 | 9–13 | 21.7 | 9 | 195.3 | **152.3** | **153** | **1.00×** | ⚠ Zero float |
| W4 | 14–18 | 21.7 | 10 | 217.0 | **169.3** | **224** | **1.32×** | ❌ Over capacity |
| W5 | 19–22 | 17.4 | 10 | 174.0 | **135.7** | 108 | 0.80× | ✅ Fits |
| W6 | 23–26 | 17.4 | 12 | 208.8 | **162.9** | 99 | 0.61× | ✅ Under-loaded |
| W7 | 27–30 | 17.4 | 12 | 208.8 | **162.9** | 98 | 0.60× | ✅ Under-loaded |
| W8 | 31–34 | 17.4 | 10 | 174.0 | **135.7** | 13 | 0.10× | ✅ Nearly empty |
| W9 | 35–36 | 8.7 | 5 | 43.5 | **33.9** | 0 | 0.00× | ✅ Empty |
| **Total** | **36** | **156.5** | | **1,395.4** | **1,088.4** | **1,079** | **0.99×** | **Balances in total; wrong in shape** |

**Arithmetic verification** *(per `PG-M10`, regenerated from the rows above immediately before
issue)*: gross team-weeks 52.2 + 121.8 + 195.3 + 217.0 + 174.0 + 208.8 + 208.8 + 174.0 + 43.5 =
**1,395.4**. Effective = 1,395.4 × 0.78 = **1,088.4**. Demand 217 + 167 + 153 + 224 + 108 + 99 +
98 + 13 + 0 = **1,079**, which equals 781 PW (`M01`–`M30`) + 298 PW (12 portals) ✓.

### 5.3 What this says

**1. The plan balances in aggregate and fails in shape.** Total demand (1,079 PW) sits within 1%
of total effective capacity (1,088 PW). That coincidence is what has allowed the plan to look
reasonable. But 61% of the demand falls in the first four waves, against 42% of the capacity.

**2. Wave 1 is not deliverable as planned.** 217 PW of work against 40.7 effective build
person-weeks. Even counting *every* role in the Wave 1 team as build capacity — 7 FTE, 121.8 gross,
95.0 effective — Wave 1 is **2.28× over**. Wave 1 contains `M01` (46 PW), `M29` (31), `M28` (30),
`M17` (26), `M07` (22), `M30` (19), `M04` (13) and `P03` (30). The three largest alone exceed the
wave's entire effective capacity by 2.6×.

**3. Waves 6–9 are half empty.** Combined spare effective capacity in Waves 5–9 is
27.7 + 63.9 + 64.9 + 122.7 + 33.9 = **313 PW**.

**4. The team ramp is inverted against the demand curve.** The team grows from 3 build FTE to 12
across the programme while demand falls from 217 PW to zero. The heaviest architectural and
foundational work is scheduled against the smallest team the programme will ever have.

### 5.4 The work that is in no wave at all

| Item | Effort | Wave |
|---|---:|---|
| Modules `M01`–`M30` — named in `06-01` §3 | 781 PW | W1–W9 |
| Portals `P01`–`P12` — named in `06-01` §3 | 298 PW | W1–W7 |
| **Modules `M31`–`M67` — named in no wave** | **763 PW** | **none** |
| **Total specified build** | **1,842 PW** | |

**763 PW — 41% of the specified build, 49% of module build — has no wave, no team and no date.**

Placing it in the spare capacity of Waves 5–9 (313 PW) leaves a shortfall of **450 PW**, or
roughly **8.6 additional build FTE sustained across Waves 5–9**. It cannot be placed in Waves 1–4,
which are already over capacity.

> `C-02` found that `M31` and `M32`–`M67` *"appear in no register… no wave allocation."* That was
> recorded as a traceability defect. **It is also a 763 person-week hole in the schedule**, and
> that consequence has not previously been stated. Raised as `D-020`.

### 5.5 The requirement allocation gap

| Source | Requirements | Method |
|---|---:|---|
| `06-01` §3 — sum of the nine per-wave "Requirements" figures | **1,180** | 142 + 178 + 156 + 189 + 148 + 134 + 121 + 79 + 33 |
| `05-01` title | ~2,352 | As written |
| `README` / `00-07` H2-01 — counted from 65 module files | 2,930 | Direct count |
| **Distinct `FR-` identifiers across all 67 module files** | **2,996** | Enumerated 2026-08-18 02:06 |

The wave plan's nine requirement figures sum to **exactly 1,180** — the v1.0 / 30-module total
(`H-02`). **1,816 requirements (61%) are allocated to no wave.**

> **This is not a fourth competing figure.** `AF-06` is open and the denominator is genuinely
> unresolved; `RQ-004` and `RR-006` must settle it. What is settled, on any denominator, is that
> the wave plan schedules the requirement set of an architecture the programme abandoned. Raised
> as `PGD-A2-04`.

### 5.6 The module identifiers the wave plan refers to

`06-01` schedules modules by identifier. Three of those identifiers changed meaning between the
30-module and 67-module architectures:

| In `06-01` | Meaning in the 30-module set | `M`-number on disk today | Where the capability now lives |
|---|---|---|---|
| `M20` (W4 core, W7 marketplace settlement) | Billing, Revenue Recognition **& Settlement** | `M20_Accounts_Receivable_Invoicing_and_Collections` | Settlement is **`M53`** Revenue Recognition, Commission & Settlement |
| `M30` (W1 core config, W9 multi-entity) | Platform Administration **& Multi-Entity/Multi-Country** | `M30_Platform_Administration_and_Configuration` | Multi-country is **`M65`** Multi-Entity, Multi-Country & Localisation |
| `M12` (W7) | E-Commerce, Parts Retail & Marketplace | `M12_Marketplace_and_Seller_Ecosystem` | E-commerce storefront is **`M38`** |

> **Wave 7's gate criterion `G7-02` requires "payout accuracy 100%".** Payout is settlement.
> Settlement is `M53`. `M53` is in no wave. The gate criterion tests a module the plan does not
> schedule. This is `C-01` — the two-architecture contradiction — reaching the delivery layer,
> where no audit has previously looked. Raised as `D-019` and `PGD-A2-05`.

---

## 6. The Master Schedule

### 6.1 Milestones

| # | Milestone | Month | Gate | Status |
|---|---|:--:|---|---|
| `MS-00` | **Charter approved; Steering Committee constituted** | T0 − 2 | `D-001` | ⬜ Not started |
| `MS-01` | `DEP-31` legal opinion received; `D-013` taken | T0 − 0 | Board minute | ⬜ **Critical path** |
| `MS-02` | Programme kickoff; team mobilised | 0 | Charter + resource plan | ⬜ |
| `MS-03` | Foundation go-live | 4 | **G1** — 12 criteria | ⬜ |
| `MS-04` | Field operations go-live | 8 | **G2** — 10 criteria | ⬜ |
| `MS-05` | Financial control go-live | 13 | **G3** — 9 criteria | ⬜ |
| `MS-06` | **v1.0 scope complete** | **18** | **G4** — 10 criteria | ⬜ **Tranche boundary; Waves 5–9 re-authorised here** (`D-017`) |
| `MS-07` | Workforce, quality & MSP go-live | 22 | **G5** — 7 criteria | ⬜ |
| `MS-08` | New asset businesses go-live | 26 | **G6** — 6 criteria | ⬜ |
| `MS-09` | Marketplace go-live | 30 | **G7** — 6 criteria | ⬜ |
| `MS-10` | Full intelligence go-live | 34 | **G8** — 5 criteria | ⬜ |
| `MS-11` | Expansion readiness; programme closure | 36 | **G9** — 5 criteria | ⬜ |
| `MS-12` | Benefits realisation review | 42 | Independent audit (`GV-010`) | ⬜ |

**Gate criteria count verification.** 12 + 10 + 9 + 10 + 7 + 6 + 6 + 5 + 5 = **70**, counted from
`06-02` §4 immediately before issue. `GV-009` restates these with an evidence standard and an
assessor, neither of which `06-02` supplies.

### 6.2 Regulatory dates that are not negotiable

| Date | Event | Wave | Consequence |
|---|---|:--:|---|
| **~13 May 2027** | PDPA 2026 complaint, investigation and penalty mechanisms activate | **W4** | Compliance is a gate condition at `G4`, not a Wave 5 activity. Penalties: BDT 25 lakh, or BDT 50 lakh for a significant data fiduciary |
| Monthly, by the **15th** | Mushak 9.1 VAT return, filed online via the NBR VAT Online portal | W3 onward | `G3-04` requires zero NBR exceptions. Input VAT credit is claimable only against valid Mushak 6.3 invoices |
| Quarterly: 25 Oct, 25 Jan, 25 Apr, 25 Jul | NBR withholding returns | W5 onward | Payroll and AP compliance |
| Annual | ISO 9001:2015 surveillance audit | All | `CON-11`; zero major non-conformances traced to systems |

### 6.3 Business-side commitment schedule

The binding constraint (`CON-12`, `RSK-001`). From `06-01` §4:

| Role | Commitment | Waves | Risk |
|---|---|---|---|
| Executive Sponsor (CEO) | 4 h/month steering | All | Low |
| Module business owners | 20% of time | Waves affecting their category | **`D-002` unresolved** |
| Super-users, 2–3 per module | 30% during UAT, 10% otherwise | Waves affecting their module | **`RSK-001` Critical** |
| Branch champions, 1 per branch | 4 h/week during rollout | W1–W5 | 51+ branches |
| Data owners | 20% during migration | W1–W5 | 48 unprofiled sources |

> **A capacity check on the business side has never been performed either.** 2–3 super-users per
> module × 67 modules at 30% during UAT is a demand `06-01` does not compute and no organisation
> chart in the estate supports. `GV-007` §resource plan must size it; it is not sized here because
> the estimation method belongs there.

---

## 7. Schedule Risk and Re-planning

### 7.1 Schedule risk register extract

| Risk | Rating | Schedule consequence | Treatment |
|---|:--:|---|---|
| `RSK-001` super-user availability | **Critical** | Wave gates slip regardless of build progress | `D-002`; `06-01` §9 — development does not run ahead into unaccepted work |
| `RSK-002` scope creep | **Critical** | The plan is re-based rather than delivered | `GV-006`; wave-locked scope; `CC-04` |
| `RSK-005` estimate inaccuracy on new lines | High | W5–W8 | 20% contingency; discovery spike before each new-line wave |
| `RSK-013` field connectivity worse than assumed | High | W2 sync work expands | Offline-first; field testing in weakest coverage |
| `RSK-015` OCA v19 migration gaps | High | Any wave; substitution is custom build | Verify OCA migration status **before** each wave |
| **New — capacity infeasibility** | **Critical** | §5.2: W1 at 5.33×, W2 at 1.76×, W4 at 1.32× | §7.2 options |
| **New — 763 PW unscheduled** | **Critical** | §5.4: 450 PW beyond available spare capacity | `D-020` |
| `DEP-31` legal opinion lead time | High | 6–10 weeks on the critical path, external | `MS-01`; escalate as an issue if not received within 4 weeks |

### 7.2 Options for the capacity finding

Presented as options because the choice is the Steering Committee's, not the planner's.

| # | Option | Effect | Cost | Risk |
|---|---|---|---|---|
| **A** | **Re-shape the team ramp** — front-load build capacity into Waves 1–2 and taper into Waves 6–9 | Corrects the inversion in §5.3(4) | Higher early burn; the same total | Hiring lead time; Wave 1 onboarding overhead against a small architecture base |
| **B** | **Extend Waves 1–4** | W1 needs ~5.3× its duration at 3 FTE | Breaches `CON-02` — v1.0 scope by Month 18 | The v1.0 commitment is a Board promise |
| **C** | **Descope Wave 1 to true foundation** — `M29`, `M28`, `M30` core only (80 PW); move `M01`, `M04`, `M07`, `M17` to W2 | W1 becomes ~2.0×, still over | Delays the service core, which is the business itself | `G1` gate criteria mostly test the service core |
| **D** | **Increase the delivery factor assumption** | Arithmetically closes the gap | Zero | **Not a plan.** It changes the number without changing the work |
| **E** | **Combination: A + C + accept a 4-month kickoff-to-W1 architecture runway** | The only combination that reconciles §5.2 with `CON-02` | Extends the horizon by ~4 months, inside `GV-001` tolerance | Requires `D-014` to be taken first |

> **Option D is listed to be rejected explicitly.** The delivery factor is the single input in §5.1
> that can be changed without changing anything real. A plan re-run at 0.95 shows Wave 1 at 4.4×
> instead of 5.3× and is no more deliverable.

### 7.3 Buffer and contingency policy

| Provision | Rule |
|---|---|
| Wave buffer | 4 weeks per wave, per `06-01` §9. A slip ≤ 4 weeks is absorbed; > 4 weeks is a Steering Committee decision |
| New-line contingency | **20% on Waves 5–8**, per `RSK-005` |
| Programme tolerance | +3 months (`GV-001` §8.1) |
| Buffer visibility | Buffer is held at **programme** level and drawn by change request (`CC-08`). Buffer distributed into wave plans is buffer that will be consumed |
| **Buffer already consumed** | The 10–14 week pre-kickoff critical path (§4.3) consumes the whole +3-month programme tolerance **before Month 0** |

### 7.4 Re-planning triggers

The plan is re-run, not adjusted, when any of these occurs:

| # | Trigger | Why |
|---|---|---|
| 1 | `AR-006` module dependency map is issued | §4.4 — the sequence is currently unverified |
| 2 | `D-014` is decided | The effort baseline changes |
| 3 | `D-020` places the 37 unscheduled modules | 763 PW enters the schedule |
| 4 | `D-019` resolves the module identifier ambiguity | `M20`, `M30` allocations may move |
| 5 | `GV-007` sizes content, guiding documents and screen design | Three unestimated work streams enter branches 2 and 4 |
| 6 | Wave 1 completes | The measured delivery factor replaces assumption `GV-004-A1` |
| 7 | A wave slips > 4 weeks | `06-01` §9 |
| 8 | Scope baseline changes under `GV-006` | By definition |

---

## 8. What This Plan Cannot Yet Contain

Stated explicitly, because a plan that hides its own preconditions is worse than one that is late.

| Missing input | Consequence for this plan | Owner |
|---|---|---|
| `AR-006` module dependency map | The wave **sequence** is inherited and unverified. Cycles and back-dependencies would be invisible | ARB |
| `GV-007` estimation model | Branches 1, 2 and 4 of the WBS carry no effort. Three work streams are unresourced | Programme Director |
| `D-020` placement of `M31`–`M67` | 41% of build has no wave | Steering Committee |
| `RQ-004` RTM | Requirement-to-wave allocation cannot be verified; §5.5 stands unresolved | Enterprise Architecture |
| `BE-008` sprint model and velocity | The 0.78 delivery factor is an assumption, not a measurement | Enterprise Architecture |
| Measured business-side capacity | The binding constraint (`CON-12`) is unquantified | HR Director / PMO |
| Per-module effort **split across waves** | Modules appearing in two waves ("core", "complete") are allocated whole to the first. This overstates early demand and understates late demand — the direction of the error is stated, its size is not knowable without the split | Module owners |

> **Limitation `GV-004-L1`.** Because of the last row, the §5.2 per-wave ratios carry a known bias.
> `M01`, `M17`, `M11`, `M20`, `M25`, `M26` and `M30` are each named in two waves. Splitting them
> would reduce W1 from 217 PW and increase W2, W7, W8 and W9. **It would not change the aggregate
> position, and it would not make Wave 1 feasible** — the three largest W1 modules alone (46 + 31 +
> 30 = 107 PW) exceed W1's effective capacity of 40.7 PW by 2.6×.

---

## 9. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `GV-004-D-01` | Which effort figure to plan against | 834 · 1,302 · 1,513 · counted | **Counted, 1,842 PW** | `RG-06`. The other three are all module-only and all stale | The capacity finding is 22% worse than it would have been on 1,513 |
| `GV-004-D-02` | Whether to publish a failing capacity check | Adjust the delivery factor · Re-shape and publish the adjusted plan · Publish the failure and the options | **Publish the failure** | `M-09` asked for the check, not for a plan that passes it. Adjusting an input to produce a pass is the defect `PGD-A1-02` and `PGD-A1-13` describe | The Steering Committee receives a finding, not a plan |
| `GV-004-D-03` | How to allocate modules named in two waves | Split by judgement · Allocate whole to first wave and declare the bias | **Whole to first wave, bias declared** | Splitting without a published split is invention. Declaring the bias is falsifiable | `GV-004-L1`; the direction of the error is known and stated |
| `GV-004-D-04` | Whether to plan Waves 5–9 to level 3 | Plan all to level 3 · Level 2 for 5–9 | **Level 2 for Waves 5–9** | `D-017` may not authorise them. Detailed planning against unauthorised scope is waste | Waves 5–9 re-planned at `MS-06` |
| `GV-004-D-05` | Whether to include portals in the capacity demand | Modules only, as precedent · Include | **Include, 298 PW** | Portals are scheduled in `06-01` and staffed by named Flutter and Frontend roles. Excluding their effort while including their people inflates apparent capacity | W2 and W4 demand rises; the finding sharpens |

---

## 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Does a per-module effort split across waves exist anywhere, or is "core / complete" purely narrative? | Module owners | Week 4 | `GV-004-L1`; per-wave precision |
| `Q-02` | Which of `M31`–`M67` are prerequisites of Waves 1–4 rather than additions to Waves 5–9? Without `AR-006` this cannot be answered | ARB | Week 6 | `D-020`; the whole sequence |
| `Q-03` | Is the 36-month horizon measured from charter approval or from kickoff? §4.3 shows a 10–14 week gap between them | Steering Committee | Week 2 | Every date in §6.1 |
| `Q-04` | What is the hiring lead time for a senior Odoo developer in Dhaka? Option A in §7.2 depends on it | HR Director | Week 4 | `GV-007` ramp plan |
| `Q-05` | Has any wave date been checked against Ramadan and the Eid periods (`CON-08`, `ASM-16`)? The Islamic calendar moves ~11 days each year across a 36-month programme | PMO | Week 4 | `MS-03`…`MS-11` |

---

## 11. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | A capacity check exists for every wave, with the method stated | §5.1, §5.2 — 9 of 9 waves |
| `AC-02` | Every effort figure is counted at the time of writing, with a timestamp | §5.1 step 1; 2026-08-18 02:06 (+06) |
| `AC-03` | Every arithmetic roll-up is regenerated from its rows | §3.2 category verification; §5.2 verification note; §6.1 gate count |
| `AC-04` | The critical path is identified and its longest lead named | §4.3 — `DEP-31`, 6–10 weeks |
| `AC-05` | Work with no wave is quantified, not noted | §5.4 — 763 PW, 37 modules |
| `AC-06` | Missing inputs are declared rather than assumed | §8 — seven inputs |
| `AC-07` | Known bias in the analysis is declared with its direction | `GV-004-L1` |
| `AC-08` | Options for the capacity finding are presented without a recommendation being disguised as a plan | §7.2 — five options, one explicitly rejected |
| `AC-09` | Re-planning triggers are defined | §7.4 — eight triggers |

**Definition of done.** Complete when every criterion is met, the Steering Committee has responded
to the §5 capacity finding by selecting an option from §7.2, `AR-006` has been issued and the plan
re-run against it, and `PGD-000` records `GV-004` as ✅ with a fresh enumeration timestamp.

---

## 12. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | [`GV-001`](GV-001_Programme_Charter_and_Mandate.md) | Fixes the horizon, the wave shape and the tranche boundary |
| Upstream | [`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) | `D-019`, `D-020` block the baseline |
| Upstream | `AR-006` | **Hard dependency, does not exist.** §4.4 |
| Downstream | [`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md) | Consumes §5 to derive the resource plan |
| Downstream | [`GV-008`](GV-008_Programme_Budget_and_Cost_Baseline.md) | Converts the schedule to a drawdown profile |
| Downstream | [`GV-009`](GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md) | Places the nine gates §6.1 fixes in time |
| Downstream | `RL-004` | Branch rollout sequences inside the wave dates |
| Downstream | `BE-008` | Must supply the measured delivery factor replacing `GV-004-A1` |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` | The roadmap this document plans |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §4 | The 70 gate criteria placed at §6.1 |
| Lateral | `../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §3 | The 35 dependencies in §4.2 |

---

## 13. References

**Within this repository**
[`PGD-000`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`PGD-AUDIT-002`](../_AUDIT/PGD-AUDIT-002_Category_00_Governance_Audit.md) ·
[`GV-003`](GV-003_Decision_Log_and_Change_Control_Procedure.md) ·
[`GV-007`](GV-007_Estimation_Model_and_Resource_Plan.md)

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01` §1, §3, §4, §9 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §4 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-04` §3, `00-06` `M-09`, `00-07` H2-08 ·
`../../1000fix_ERP_Module/03_Modules/**/M*.md`, `P*.md` — `Effort estimate` rows, directly summed

**External standards** *(all verified 2026-08-18)*

| Source | Used for |
|---|---|
| ISO 21502:2020 §7.3 planning | WBS, sequencing, resourcing |
| ISO 21503:2022 programme planning | Wave-as-component-project |
| PMBOK Guide 7th Edition — Planning and Measurement performance domains | §3, §5 |
| PRINCE2 7th Edition (2023) — plans practice, tolerance | §6, §7.3 |
| Critical path method — forward/backward pass, float | §4.3, §4.5 |
| NBR VAT filing: Mushak 9.1 due by the 15th of the following month, online via the VAT Online portal | §6.2 |
| Bangladesh PDPA 2026 — enforcement mechanisms activate ~13 May 2027 | §6.2 |

---

## 14. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Programme Management Office | Initial issue. **Closes `M-09`** with a per-wave capacity check that the plan fails. Quantifies the schedule half of `C-02` at 763 PW. Raises `PGD-A2-04` (1,816 unallocated requirements) and `PGD-A2-05` (ambiguous module identifiers in the wave plan) | *pending Steering Committee* |

---

*`GV-004` · Category 00 · 1000FiX ERP System v2.0 · CONFIDENTIAL — Internal Use Only*
*1000FiX Services Limited · Hotline 16743 · info@1000fix.com · ISO 9001:2015 Certified*
