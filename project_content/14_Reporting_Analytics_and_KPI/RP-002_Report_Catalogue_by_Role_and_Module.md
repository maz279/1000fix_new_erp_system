---
id: RP-002
title: Report Catalogue by Role and Module
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead
author: BI Lead with module business owners and Enterprise Architecture
reviewers: [CTO, CFO delegate, Operations Director, Quality Manager, Solution Architect, Support Lead, Localisation Lead]
approver: BI Lead with CTO delegate
content_class: E
purpose: >
  The single catalogue of every operational and management report the system produces — its audience,
  frequency, distribution, retention, owner and the metrics it carries. Sixty-seven module
  specifications and twelve portal specifications each declare their own reports in isolation, and
  enumeration finds 1,063 of them with no owner, no frequency, no retention and no evidence that
  anyone has ever counted them. A report estate nobody has counted is one nobody can rationalise,
  and every one of those 1,063 consumes build effort, warehouse capacity and someone's attention.
traces_to: [03_Modules §14, 06-02, M25, M62, P06, 04-00, 05-04, RP-001, RP-003, RP-004, RP-005, RP-006, RP-008, RP-009, RP-010, RP-013, RP-014, RP-016, CG-006, TS-014, OP-006]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: RP-002_Report_Catalogue_by_Role_and_Module_BN.md
sources:
  - source: Enumeration of 1000fix_ERP_Module/03_Modules/**/M*.md and P*.md §14 "Reports & Analytics" sections, 2026-08-20 — 79 specifications, 1,063 report rows excluding table headers, mean 13.5 per specification, 1,025 distinct report names, 34 names appearing in more than one specification accounting for 72 rows
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md §14 — the module template's Reports & Analytics section; §12 is Interfaces and §15 is KPIs
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-10 (a scheduled report is rendered per recipient under that recipient's security scope), PRU-P06-12 (analytical queries run against the warehouse, never against transactional databases, except the scoped real-time board)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 KPIs — manual management reporting effort −90%; decisions made on live data rather than compiled spreadsheets 100% of management reviews
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Report Catalogue by Role and Module

| Item | Value |
|---|---|
| Reports enumerated | **1,063** across **79** module and portal specifications |
| Distinct report names | 1,025 |
| Catalogued to the §4.2 schema | **0 — outstanding** (`O-02`) |
| Rationalisation target | §4.4 |
| Owner | BI Lead |
| Wave | W2 · `P1` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` metric-table addition applied as the catalogue schema in §4.2. All six sections retained in
> order.

---

## 1. Purpose

`P06` commits to cutting manual management reporting effort by **90%** and to 100% of management
reviews running on live data. Those are subtraction targets: they are met by *removing* compiled
spreadsheets, and you cannot remove what you have not listed.

**Nobody has listed it.** Enumerating §14 "Reports & Analytics" across all 79 module and portal
specifications returns **1,063 report rows** — a figure that appears in no programme document. The
register's justification for this file predicted *"hundreds of near-duplicate reports nobody owns"*;
the count is over a thousand, and the diagnosis needs correcting (§4.3).

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A single catalogue | 79 specifications each own a fragment. No one can answer "how many reports are we building?" — and the answer is 1,063 |
| Owners | A report with no owner is never retired, and `RP-013` shows unreviewed outputs accumulate until the system spends its capacity producing what nobody reads |
| Audience and frequency | Build effort is spent on reports that a role does not need at a cadence nobody asked for |
| Retention | `NFR-088` enforces statutory retention. A report is a record; an uncatalogued report has an undefined retention |
| The metric binding | A report carrying a metric not in `RP-001` is a second definition (`KD-15`, `PRU-P06-01`) |
| Rationalisation | 1,063 reports at even 1.5 days of build each is over 6 person-years. **This is a scope question disguised as a documentation gap** |

---

## 2. Scope

**In scope.** Every report, register, statement, extract, board and scheduled output the system
produces for a human. The catalogue schema, the rationalisation method, ownership, retention, the
distribution model, and the boundary against dashboards.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The metrics a report carries | `RP-001` — a report *cites* metrics, it does not define them |
| **Dashboards** — interactive, persistent, drillable views | `RP-003` executive, `RP-004` operational consoles, `RP-005` external. §4.1 draws the line |
| Statutory and regulatory returns | **`RP-009`** — those are filings with legal deadlines, not reports, and they carry a different control regime |
| The standing board and management pack | `RP-010` |
| Subscriptions and schedules | `RP-013` — this file says a report exists and who it is for; `RP-013` says when it is sent |
| Export marking and watermarking | `RP-014` |
| Narrative and commentary | `RP-008` |
| Certified datasets a report queries | `RP-006` |
| Data-quality scorecards | `RP-016` |
| Printed transactional documents — invoices, challans, job cards | Category 05 `DT`. **An invoice is a document, not a report** |
| Alerts | `RP-012`, `NT-021` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable) | The build backlog, the rationalisation decisions and the retirement queue |
| **Module business owners** | Confirming the reports their module declared are the reports they actually need |
| **Programme Manager** | The scope and effort consequence of 1,063 reports |
| **Every role `R01`–`R38`** | What outputs exist for them, §4.5 |
| **Support Lead** | What breaks when a report fails, and who notices |
| **Quality Manager** | Retention and ISO evidence (`NFR-024`, `NFR-088`) |

---

## 4. Content

### 4.1 Report, dashboard, document, filing — four things, four regimes

The four are routinely conflated, and each has a different owner, cadence and control.

| | **Report** *(this file)* | **Dashboard** | **Document** | **Filing** |
|---|---|---|---|---|
| Is | A rendered output answering a defined question at a point in time | A persistent interactive view | A transactional artefact given to a party | An externally mandated submission |
| Owner | `RP-002` | `RP-003`/`004`/`005` | Category 05 `DT` | **`RP-009`** |
| Cadence | Scheduled or on demand | Always available | Per transaction | Statutory deadline |
| Control | Retention, distribution, marking | Row-level security, freshness | Statutory format, sequence | **Legal deadline, submission route** |
| Failure mode | Nobody reads it | Wrong decision | Non-compliant artefact | **Missed deadline, penalty** |
| Example | Monthly branch performance report | Dispatch console | Mushak 6.3 challan | Mushak 9.1 return |

**The distinction is not pedantry.** A missed report is an annoyance; a missed filing is a penalty. A
wrong dashboard is a wrong decision today; a wrong document is potentially unlawful. Putting all four
in one catalogue would apply the weakest control regime to the highest-consequence artefact.

### 4.2 The catalogue schema

Every catalogued report carries these fifteen fields.

| # | Field | Content |
|---:|---|---|
| 1 | `id` | `RPT-nnnn`, allocated here, permanent (§4.6) |
| 2 | `name_en` / `name_bn` | Approved names; Bengali where the audience reads Bengali |
| 3 | `question` | The decision it supports, in one sentence |
| 4 | `audience` | `Rnn` roles, not job titles (`05-04`) |
| 5 | `owning_module` | The `Mnn` or `Pnn` that declared it |
| 6 | `business_owner` | The named function accountable for it being useful |
| 7 | `metrics` | The `KPI-nnn` identifiers it carries (`RP-001`) |
| 8 | `dataset` | The `RP-006` certified dataset it queries (`PRU-P06-02`, `PRU-P06-12`) |
| 9 | `grain` | The level the report presents |
| 10 | `frequency` | On demand · daily · weekly · monthly · per period · per event |
| 11 | `distribution` | In-product · scheduled (`RP-013`) · export only |
| 12 | `format` | Screen · PDF · Excel · CSV |
| 13 | `classification` | `S0`–`S3` from `05-02` §10, driving `RP-014` marking |
| 14 | `retention` | Period and its basis (`NFR-088`) |
| 15 | `disposition` | `Build` · `Merge into RPT-nnnn` · `Replace with dashboard` · `Retire` · `Defer to wave` |

**Field 15 is what makes this a catalogue rather than a list.** Every one of the 1,063 rows gets a
disposition, and the disposition is a decision with a name against it.

### 4.3 The enumerated position — and a corrected diagnosis

Enumerated from the 79 specifications on **2026-08-20**:

| Measure | Value |
|---|---:|
| Specifications carrying a §14 Reports & Analytics section | **79** — 67 modules + 12 portals |
| **Report rows** (table headers excluded) | **1,063** |
| Mean per specification | 13.5 |
| Highest | `M54` 20 · `M49` 19 · `M50` 19 · `M53` 19 · `M15` 18 · `M19` 18 · `M20` 18 · `M51` 18 |
| Specifications declaring **no** reports | **0** |
| Distinct report names | **1,025** |
| Names appearing in more than one specification | **34**, accounting for **72 rows** |

#### The register's diagnosis is directionally right and specifically wrong

The register says 67 modules specifying reports independently *"produces hundreds of near-duplicate
reports nobody owns"*. Two corrections:

| Claim | Finding |
|---|---|
| "hundreds" | **1,063** — an order of magnitude beyond "hundreds", and the finance cluster (`M19`, `M20`, `M49`–`M54`) alone declares 131 |
| "near-duplicate" | **Only 34 names recur, across 72 rows.** Duplication by name is a small problem: `custody exception report`, `forecast accuracy`, `knowledge usage` and `sync health` each appear in three specifications; a further 30 names appear in two |

**The real defect is not duplication. It is that 1,063 reports have no owner, no audience, no
frequency and no retention, and that no document in the programme states the number.** Deduplication
removes at most 38 rows. Rationalisation (§4.4) is where the volume is addressed, and it is a scope
decision, not a tidying exercise.

> **A register trace correction.** The Master Index traces this file to **`03_Modules` §12**. In the
> module template, **§12 is Interfaces**; **§14 is Reports & Analytics** and §15 is KPIs. Verified
> across all 67 module files — every one titles §14 *"Reports & Analytics"*. The trace should read
> §14. Raised as `O-01`, with the same correction needed on the Category 13 preamble, which describes
> §15 as Acceptance Criteria when §15 is KPIs and §17 is Acceptance Criteria.

### 4.4 Rationalisation — the method

`CT-01` to `CT-06` are applied to all 1,063 rows before any is built.

| # | Rule |
|---|---|
| **CT-01** | **A report must name the decision it supports and the role that takes it.** A report that supports no decision is retired at catalogue time, not built and retired later |
| **CT-02** | **If the question is "what is happening now", it is a dashboard, not a report** (§4.1). A large share of the 1,063 are standing views mis-declared as reports, and a dashboard replaces many reports at once |
| **CT-03** | **If the answer is a single number, it is a metric on an existing view**, not a report (`RP-001`) |
| **CT-04** | Where two or more rows answer the same question at different grains, **one report with a drill replaces them** (`PRU-P06-08` makes every aggregate decomposable, so the grains collapse) |
| **CT-05** | **A report whose only consumer is a person who could self-serve on a certified dataset is replaced by that dataset** (`RP-006`); `P06` promises self-service without SQL |
| **CT-06** | Every surviving report is assigned to a **wave**, and a report with no wave is not in scope |

**The expected effect, stated as a target rather than a claim:**

| Disposition | Target share | Basis |
|---|---:|---|
| Replace with a dashboard panel (`CT-02`) | ~35% | Most module §14 rows describe standing views |
| Merge into another report (`CT-04`) | ~20% | Same question, different grain |
| Replace with a certified dataset (`CT-05`) | ~10% | Analyst-consumed extracts |
| Retire — no decision (`CT-01`) | ~10% | Declared for completeness |
| **Build as a report** | **~25%, roughly 250–280** | The residue |

> **These percentages are a hypothesis, not a finding.** They are stated so the rationalisation has a
> testable expectation, and they will be replaced by counted dispositions. `O-02`.

### 4.5 Coverage by role

`CT-07`: **every role in `05-04` has at least one catalogued output, or its absence is deliberate and
recorded.** A role with no report is a role that manages by asking someone else.

| Role group | Roles | Primary outputs |
|---|---|---|
| Executive `R01`–`R05` | 5 | `RP-003` executive dashboards; `RP-010` board pack; branch league (`RP-011`) |
| Branch and service ops `R06`–`R09` | 4 | `RP-004` Branch, Dispatch, Workshop, Intake consoles; daily branch performance; WIP ageing; uncollected devices |
| Field `R10`–`R12`, `R16` | 4 | Own scorecard and earnings only — `05-04` `T4`. **A technician gets a personal report, never a peer comparison** |
| Technical services `R13`, `R14` | 2 | MSP estate and SLA reports; data-services custody register |
| Supply chain `R15`, `R17`–`R20` | 5 | Stock accuracy, van-stock variance, ageing, vendor scorecard, three-way-match exceptions |
| Commercial `R21`–`R25`, `R28` | 6 | Contract profitability, renewal pipeline, claim ageing, seller performance, refurbishment yield |
| Finance `R03`, `R26`, `R27`, `R29` | 4 | Ledger and reconciliation reports, ageing, cash position, shift close, **and the `RP-009` filings** |
| People and quality `R30`–`R32` | 3 | Attendance completeness, certification currency, payroll control, NCR and CAPA ageing |
| Platform `R33`, `R02` | 2 | Job success, integration health, access review, `RP-016` scorecards |
| Contact centre `R34`, `R35` | 2 | Queue and service level, disposition completeness, quality scores |
| External `R36`–`R38` | 3 | **`RP-005` only** — `PRU-P06-14` forbids external `P06` access |

### 4.6 Identifier and lifecycle rules

| # | Rule |
|---|---|
| **CT-08** | `RPT-nnnn` allocated here, permanent, never reused (`CP-02`) |
| **CT-09** | Every report names its `RP-006` dataset and runs against the **warehouse**, never a transactional database, except the scoped real-time board (`PRU-P06-12`) |
| **CT-10** | Every report carries only `RP-001` metrics. **A report containing its own calculation is rejected at review** (`KD-15`, `AUT-P06-08`) |
| **CT-11** | Every report is **rendered per recipient under that recipient's security scope** (`PRU-P06-10`). One report definition, many scoped renderings — never one rendering distributed widely |
| **CT-12** | Every report carries its classification and is marked on export per `RP-014` |
| **CT-13** | Every report states a retention period with its basis (`NFR-088`) |
| **CT-14** | Every report is **reviewed annually for continued use**; a report with no recorded consumption for two review cycles is retired (`RP-013` applies the same rule to subscriptions) |
| **CT-15** | A report version is pinned to the release it was specified against (`CG-006`) |
| **CT-16** | The catalogue is **counted, with its enumeration date**, and the count of uncatalogued module rows is reported alongside (`CP-11`) |

### 4.7 Bilingual position

`CG-010` §3.2 makes this file bilingual because *"the report catalogue … reach\[es\] branch
managers"*. Precisely:

| Element | Bengali required |
|---|---|
| Report **names** and their one-line questions, for any report a `R06`, `R08`, `R09`, `R18`, `R29` or field role receives | **Yes** — 51+ branch managers and 150–250 agents |
| Report **content** — column headings, labels, totals | Yes, per `RP-007` |
| The catalogue's own schema, rationalisation method and dispositions | No — BI and programme audience |

**So the Bengali counterpart is a name-and-question set, not a translation of this file.** Stated so
the Bengali effort is scoped correctly and not estimated against the whole document (`O-05`).

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| Module and portal `§14` | The 1,063 rows this catalogue rationalises |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Every metric a report carries (`CT-10`) |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | The certified dataset every report queries (`CT-09`) |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md), `RP-004`, `RP-005` | Where `CT-02` sends the ~35% that are dashboards |
| [`RP-009`](RP-009_Statutory_and_Regulatory_Report_Format_Register.md) | Where filings go — deliberately not here |
| [`RP-013`](RP-013_Scheduled_Report_and_Subscription_Catalogue.md), `RP-014` | Scheduling and marking |
| `05-04` | Roles for `audience`, and the scope that `CT-11` renders under |
| `05-02` §10 | The `S0`–`S3` classification |
| `NFR-088` | Retention |
| `06-01` | The wave each surviving report is assigned to (`CT-06`) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave during build; annually thereafter (`CT-14`) |
| Trigger for out-of-cycle review | A new module report request; a metric restatement affecting a report; a retention or classification change; a portal release replacing reports with a dashboard |
| Owner | BI Lead |
| Data files | `RP-002_Report_Catalogue.csv` — all 1,063 rows with dispositions · `RP-002_Role_Coverage.csv` · `RP-002_Retired_and_Merged.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The register traces this file to `03_Modules` §12; §12 is Interfaces and §14 is Reports & Analytics.** Verified across all 67 module files. The same class of error appears in the Category 13 preamble, which calls §15 Acceptance Criteria when §15 is KPIs and §17 is Acceptance Criteria — **that error propagated into four `TS` files before it was caught** | Programme Content Lead | **W2 — register correction** |
| **O-02** | **1,063 rows need a disposition and none has one.** `CT-01`…`CT-06` give the method; applying it needs each module business owner to confirm which of their declared reports supports a real decision. At 15 minutes a row that is **265 hours of owner time across eleven functions**, and the §4.4 percentages are a hypothesis until it is done | BI Lead with module business owners | **W2 — before any report is built** |
| **O-03** | **The build effort behind 1,063 reports is not in any plan.** At 1.5 days each that is over **6 person-years**; even the ~25% residue is 250–280 reports. `06-01` §4 provides 1 Data/BI Engineer FTE from W4 only. **Rationalisation is therefore not optional and its outcome is a scope decision for the Steering Committee** | Programme Manager with CTO | **W2** |
| **O-04** | **`RP-006` is `P1`/W4 and `CT-09` requires every report to name a certified dataset.** This file is W2. Reports catalogued at W2 will name datasets that do not yet exist, or will be catalogued without the field — the same forward-dependency shape `AUDIT-014` TS-02 recorded nine times in Category 13 | BI Lead | **W2** |
| **O-05** | **The Bengali name-and-question set (§4.7) has no author.** Bengali authoring capacity is unresourced across the programme (`AUDIT-012` BN-01, `TS-002` `O-06`, `RP-001` `O-05`), and branch-facing report names are read by 51+ branch managers | Localisation Lead | **W2** |
| **O-06** | **No report-consumption telemetry is specified**, so `CT-14`'s retirement rule cannot operate. `P06` measures dashboard usage; nothing measures whether a scheduled report was opened. Without it the estate can only grow | BI Lead with Platform Engineering | **W4 — with `RP-013`** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the catalogue schema
- [x] **1,063 reports enumerated across 79 specifications from the filesystem, with per-spec distribution**
- [x] **The register's "hundreds of near-duplicate" diagnosis corrected: 1,063 rows, only 34 recurring names**
- [x] The real defect restated — unowned, unscheduled, unretained volume rather than duplication
- [x] **Report / dashboard / document / filing distinguished across six dimensions, with the reason**
- [x] Fifteen-field catalogue schema including a mandatory disposition
- [x] Six rationalisation rules, with expected dispositions labelled a hypothesis rather than a finding
- [x] Role coverage across all 38 roles, including the deliberate `T4` limit on technician reports
- [x] Nine lifecycle rules, including per-recipient rendering and annual review
- [x] **The register trace error found and reported, with its Category 13 counterpart**
- [x] Bengali scope narrowed to names and questions, so the effort is estimated correctly
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 1,063 dispositions decided — outstanding (`O-02`)**
- [ ] **`O-03` build effort not in the plan — outstanding; a Steering scope decision**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending BI Lead and CTO delegate**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
