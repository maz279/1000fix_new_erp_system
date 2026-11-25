---
id: RP-006
title: BI Semantic Layer Data Dictionary
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead
author: BI Lead with Data Engineering and Enterprise Architecture
reviewers: [CTO, Solution Architect, Chief Data Officer, Security Lead, MDM Lead, Finance Manager, Operations Director]
approver: CTO with BI Lead
content_class: E
purpose: >
  The certified datasets a self-service analyst may query — each one's business meaning, fields, grain,
  joins, row-level-security binding, freshness guarantee, owner and steward. P06 promises management
  self-service analysis on certified datasets without SQL, and certification is a documentation act:
  a dataset is certified because someone wrote down what it means and signed for it, not because it
  loaded successfully. Without this file, self-service means every analyst inventing their own joins
  and the company acquiring one version of the truth per analyst.
traces_to: [M62, M62 §9, M25, P06, 04-00 P06, 05-02, 05-02 §10, 05-04, 05-04 §4, 05-04 §5, 05-06 §8, 05-06 NFR-039, RP-001, RP-002, RP-003, RP-004, RP-005, RP-007, RP-016, MD-035, MD-036, DM-011, TS-005, TS-014, TS-017]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md §9 BRU-DAT-01…BRU-DAT-12 — one definition per metric held in the metric registry; version-controlled change only; consumers notified before a change; no retirement while a consumer remains; certification status displayed wherever the metric appears; Bronze immutable; an unexpected source schema change stops the pipeline and the platform never infers a mapping; every fact model declares its grain and a build producing a different grain fails; every dataset and metric has a named business owner and a named technical steward; every producing module has a signed data contract before its data enters Silver; S3-classified personal data excluded from the analytical estate by default; analytical row-level security mirrors the user's ERP scope and is enforced in the query engine
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-02 (no P06 user queries a raw source table; only M62-certified datasets are exposed), PRU-P06-06 (every view states its data freshness), PRU-P06-08 (every aggregate decomposable), PRU-P06-12 (analytical queries run against the warehouse), PRU-P06-13 (a self-service query cannot degrade the operational estate; queries are bounded, queued and attributed)
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 Self-service — "build analyses on certified datasets without SQL, within row-level security"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-039 warehouse analytical query ≤ 10 s p95; §8 DI-06 data quality tests run on every warehouse load and failures block dependent refreshes
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# BI Semantic Layer Data Dictionary

| Item | Value |
|---|---|
| Governs | Every dataset exposed to `P06` self-service and to every dashboard and report |
| Certification authority | `M62`; **this file is the certification content** |
| Datasets specified | **18** (§4.3) |
| Enforcement | Row-level security in the **query engine** (`BRU-DAT-12`) |
| Query target | ≤ 10 s p95 (`NFR-039`) |
| Wave | W4 · `P1` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the dataset schema in §4.2. All six sections retained in order.

---

## 1. Purpose

`04-00` `P06` promises management *"self-service analysis on certified datasets without SQL, within
row-level security"*, and `PRU-P06-02` makes it a hard rule that **no `P06` user queries a raw source
table**. Both statements depend on a set of datasets that someone has certified.

**Certification is not a technical state.** A dataset loads or fails; it becomes *certified* when its
business meaning, grain, joins, security binding and freshness guarantee are written down and an owner
signs for them. `BRU-DAT-09` requires a named business owner and a named technical steward for every
dataset. **This file is where they are named and what they are signing.**

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Certified datasets | `PRU-P06-02` cannot be satisfied, so either self-service is withdrawn or analysts query raw tables — and the second produces numbers nobody can reproduce |
| Declared grain | `BRU-DAT-08` requires every fact model to declare its grain. An undeclared grain is double-counted revenue the first time two facts are joined |
| Documented joins | Two analysts join service orders to invoices differently and both are honest. `P06`'s promise of one version of the truth ends here, not at the metric layer |
| RLS bindings | `BRU-DAT-12` requires scope in the query engine. An unbound dataset is a scope breach waiting for its first export (`RP-005` `ED-02`) |
| Freshness guarantees | `PRU-P06-06` requires every view to state freshness and `AUT-P06-04` flags a stale one. A guarantee that exists nowhere cannot be breached, so nothing is ever flagged |
| Owners | An unowned dataset is never corrected and never retired |

---

## 2. Scope

**In scope.** The dataset schema; the eighteen certified datasets, their fields, grain, joins,
security bindings, freshness guarantees, owners and stewards; certification levels and their gates;
the self-service contract; and the boundary against metric definitions.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| **Metric definitions** | **`RP-001`** — a metric is computed *from* a dataset. §4.1 states the boundary |
| Warehouse architecture, medallion layers, pipeline mechanics | `M62` — this file is content, not architecture |
| Chart rendering | `RP-007` |
| Which dashboard uses which dataset | `RP-003`, `RP-004`, `RP-005` |
| Data-quality measurement of master data | **`RP-016`** — `RP-016` scores the data; this file describes the dataset |
| Migration-time profiling and cleansing | `DM-011` |
| The chart of accounts and dimensions | `MD-035`, `MD-036` |
| Field-level classification | `05-02` §10 — this file *applies* it |
| The proof that RLS holds | `TS-017` Block B; `TS-005` `SIT-J-006` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI Lead** (accountable) | The certification register |
| **Data engineers** | Building models to a declared grain and join set |
| **Self-service analysts** — `R01`–`R05`, `R06`, `R17`, `R21`, `R22`, `R26`, `R32` | What they may query and what it means |
| **Security Lead** | The RLS binding of every dataset |
| **Chief Data Officer** | `S3` exclusion and residency position |
| **QA** (`TS-005`, `TS-017`) | The bindings the tests verify |
| **`RP-001`** | The `source` field of every metric |

---

## 4. Content

### 4.1 The boundary with `RP-001`, stated first

`M62` `BRU-DAT-01` holds one definition per **metric**. `BRU-DAT-08` requires a declared grain per
**dataset**. They are different registers and conflating them is the commonest semantic-layer failure.

| | **`RP-001`** | **`RP-006`** *(this file)* |
|---|---|---|
| Registers | Metrics | Datasets |
| Answers | *What does "first-time fix rate" mean?* | *Which certified table do I compute it from, at what grain, joined how, scoped to whom?* |
| Unit | `KPI-nnn` | `ds_*` |
| Owner | Metric business owner | Dataset business owner + technical steward |
| Changes when | The business definition changes | The model, grain, join or source changes |

**A metric names exactly one primary dataset** (`RP-001` `KD-19`). **A dataset serves many metrics.**
Where a metric needs two datasets, the join is declared *here* and the metric cites the join, so the
join is never re-invented in a dashboard.

### 4.2 The dataset schema

Every certified dataset carries these sixteen fields.

| # | Field | Content |
|---:|---|---|
| 1 | `id` | `ds_<domain>_<fact\|dim>`, permanent |
| 2 | `name` | Business name, in business language |
| 3 | `meaning` | What one row **is**, in one sentence — the most-read field in the file |
| 4 | `grain` | The declared grain; a build producing a different grain fails (`BRU-DAT-08`) |
| 5 | `type` | `fact` · `dimension` · `bridge` · `snapshot` |
| 6 | `source_modules` | The producing `Mnn`, each with a signed data contract (`BRU-DAT-10`) |
| 7 | `fields` | Every field with business meaning, type and classification |
| 8 | `joins` | Permitted joins, their keys and their cardinality — **and the joins that are prohibited** |
| 9 | `rls_binding` | The `05-04` tier and the column the query engine filters on (`BRU-DAT-12`) |
| 10 | `excluded_fields` | Fields deliberately absent, with the reason (`BRU-DAT-11`, `PRU-P06-04`) |
| 11 | `freshness` | The guarantee, e.g. *"loaded by 05:30 BST daily"* (`PRU-P06-06`) |
| 12 | `history` | Retained period and whether it is slowly-changing |
| 13 | `quality_tests` | The `DI-06` tests that must pass; failure blocks dependent refresh |
| 14 | `business_owner` / `technical_steward` | Named functions (`BRU-DAT-09`) |
| 15 | `certification` | `Certified` · `Provisional` · `Deprecated` (§4.4) |
| 16 | `metrics_served` | The `KPI-nnn` identifiers computed from it |

**Field 8's prohibition half is what prevents double counting.** Declaring that
`ds_service_order_fact` may **not** be joined directly to `ds_invoice_line_fact` — because a job can
produce many invoice lines and an invoice can cover many jobs — stops the most likely wrong number in
the estate before an analyst produces it.

### 4.3 The eighteen certified datasets

| `id` | One row is | Grain | Type | RLS tier | Serves |
|---|---|---|---|:--:|---|
| `ds_service_order_fact` | One service order | Service order | fact | `T2` branch | `KPI-001`…`009`, `KPI-006` |
| `ds_work_order_fact` | One field or workshop work order | Work order | fact | `T3` zone / workshop | `KPI-011`…`015` |
| `ds_sla_event_fact` | One SLA clock event — start, hold, resume, breach | SLA event | fact | `T2` | `KPI-006` |
| `ds_invoice_line_fact` | One invoice line | Invoice line | fact | `T1` entity | `KPI-053`…`056` |
| `ds_payment_fact` | One payment or receipt | Payment | fact | `T1` | `KPI-051`, `KPI-052` |
| `ds_gl_posting_fact` | One general-ledger posting | Posting | fact | `T1` | `KPI-050`, margin metrics |
| `ds_stock_movement_fact` | One stock movement | Movement | fact | `T2` location | `KPI-042`…`047` |
| `ds_claim_fact` | One warranty claim | Claim | fact | `T0` internal / brand-scoped externally | `KPI-037`…`041` |
| `ds_contract_fact` | One contract, with entitlement position | Contract | snapshot | `T4` account | `KPI-028`…`031` |
| `ds_conversation_fact` | One customer conversation across any channel | Conversation | fact | `T0` internal | `KPI-025`…`027` |
| `ds_survey_response_fact` | One CSAT or NPS response | Response | fact | `T2` | `KPI-020`, `KPI-021` |
| `ds_attendance_fact` | One employee-day attendance record | Employee × day | fact | `T2` + `T5` for pay detail | `KPI-061` |
| `ds_marketplace_job_fact` | One marketplace job with commission | Job | fact | `T4` seller | `KPI-079`…`082` |
| `ds_party_dim` | One party — customer, vendor, seller, partner | Party | dimension | `T0` with `T4` overlay | join key |
| `ds_asset_dim` | One device or asset | Asset | dimension | `T0` with `T4` overlay | `KPI-054` |
| `ds_employee_dim` | One employee | Employee | dimension | `T2`; pay fields excluded | join key |
| `ds_branch_dim` | One branch or service centre | Branch | dimension | `T0` | `RP-011` normalisation |
| `ds_calendar_dim` | One date, with fiscal and holiday attributes | Date | dimension | `T0` | every time series |

**Eighteen, not one per module.** A certified dataset is a **business object**, not a module export.
Sixty-seven module exports would reproduce the module boundaries inside the warehouse and force every
cross-module analysis into an analyst-invented join, which is the outcome `PRU-P06-02` exists to
prevent.

**`ds_calendar_dim` carries the fiscal year (July–June) and the `MD-041` holiday calendar including
moon-dependent dates.** Every "working days" metric — `KPI-050` close cycle above all — is wrong
without it, and it is the dataset most likely to be treated as trivial.

### 4.4 Certification levels and their gates

| Level | Means | Gate |
|---|---|---|
| **`Provisional`** | Loaded, grain declared, owner named. **Usable, labelled, not citable in a board pack** | Grain + owner + steward |
| **`Certified`** | Meaning, fields, joins, RLS binding, freshness, quality tests and exclusions all recorded and signed | All sixteen schema fields + a passing `DI-06` test set + the owner's signature |
| **`Deprecated`** | Superseded; **cannot be retired while a registered consumer remains** (`BRU-DAT-04`) | A successor named and consumers migrated |

**Certification status is displayed wherever the dataset's data appears** (`BRU-DAT-05`), which means a
`Provisional` dataset carries a visible label on every dashboard built on it. `RP-003` `XD-05` and
`RP-004` `OC-05` both require it.

### 4.5 Rules

| # | Rule |
|---|---|
| **SM-01** | **A dataset states what one row is** (field 3). A dataset whose row cannot be described in a sentence has not been modelled |
| **SM-02** | **Grain is declared and enforced**; a build producing a different grain **fails** (`BRU-DAT-08`) |
| **SM-03** | **Permitted joins are declared, and prohibited joins are declared explicitly** with the double-count they would cause |
| **SM-04** | **RLS is bound to a `05-04` tier and enforced in the query engine** (`BRU-DAT-12`), never in the presentation tool |
| **SM-05** | **`S3` fields are excluded by default** (`BRU-DAT-11`); inclusion requires named, approved, time-limited authorisation recorded in field 10 |
| **SM-06** | **Excluded fields are listed with their reason.** An absent field with no recorded reason will be added back by the next engineer |
| **SM-07** | Every dataset declares a **freshness guarantee**, and breaching it flags every dependent view (`AUT-P06-04`) |
| **SM-08** | Every dataset carries **`DI-06` quality tests**, and a failure **blocks dependent refresh** and marks dependent views unreliable (`AUT-P06-05`, `AUT-059`) |
| **SM-09** | Every dataset has a **named business owner and technical steward** (`BRU-DAT-09`) |
| **SM-10** | Every producing module has a **signed data contract** before its data enters Silver (`BRU-DAT-10`); an unexpected schema change **stops the pipeline** and the platform never infers a mapping (`BRU-DAT-07`) |
| **SM-11** | **Every fact is decomposable to its source records** (`PRU-P06-08`), and the decomposition path is recorded |
| **SM-12** | **Self-service queries are bounded, queued and attributed** (`PRU-P06-13`); a self-service query may not degrade the operational estate |
| **SM-13** | Analytical queries run against the **warehouse**, never a transactional database (`PRU-P06-12`) |
| **SM-14** | Query performance ≤ **10 s p95** (`NFR-039`), verified in `TS-014` `PERF-NFR-039-01` |
| **SM-15** | A dataset change follows the same **restatement discipline** as a metric: version, consumer notification before effect, and a stated history position (`BRU-DAT-02`, `BRU-DAT-03`) |
| **SM-16** | **Residency-classified fields never leave the Bangladesh-resident store**, and a dataset joining to them joins by resident key without duplicating the field (`NFR-086`) |

### 4.6 The self-service contract

`04-00` promises analysis *without SQL*. That promise needs a stated contract, or "self-service"
becomes an unbounded query surface on a production warehouse.

| The analyst may | The analyst may not |
|---|---|
| Query any `Certified` dataset within their `05-04` scope | Query a raw source table (`PRU-P06-02`) |
| Aggregate at or above the declared grain | Aggregate below the grain, or join across a prohibited join (`SM-03`) |
| Use any `RP-001` metric | **Define a new metric** (`KD-15`, `PRU-P06-01`) — they request one |
| Save and share an analysis within their scope | Share an analysis that renders outside the recipient's scope (`PRU-P06-10`) |
| Export within the `RP-014` marking and `AUT-P06-07` threshold rules | Export above the threshold without justification |
| Run a query bounded by cost and duration | Run an unbounded query — it is terminated with a narrower-scope suggestion (`AUT-P06-06`) |

**A saved analysis is not a certified report.** If it becomes something people rely on, it enters
`RP-002` and acquires an owner, a retention period and a review date. Stated because the commonest
path to a shadow reporting estate is a shared self-service analysis that quietly became the monthly
number.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `M62` §9 | Every rule in §4.5 derives from a `BRU-DAT-*` |
| `P06` §9 | `PRU-P06-02`, `-06`, `-08`, `-12`, `-13` |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | The metrics each dataset serves (field 16) |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md), `RP-004`, `RP-005` | The consumers whose scope bindings must match |
| [`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md) | The quality tests in field 13 |
| `05-02` | Entities and the `S0`–`S3` classification |
| `05-04` §4, §5 | The tier and field bindings |
| `MD-035`, `MD-036`, `MD-041` | Accounts, dimensions and the fiscal calendar |
| [`DM-011`](../12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md) | Migration-time profiling, which precedes steady-state certification |
| `NFR-039`, `DI-06`, `NFR-086` | Performance, quality gating and residency |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave; certification reviewed annually per dataset |
| Trigger for out-of-cycle review | A source schema change (`BRU-DAT-07` stops the pipeline, so this is immediate); a new metric needing a new dataset; a grain change; a classification change; an RLS change in `05-04` |
| Owner | BI Lead; each dataset has its own business owner and technical steward |
| Data file | `RP-006_Dataset_Register.csv` — 18 datasets × 16 fields · `RP-006_Field_Dictionary.csv` · `RP-006_Join_Matrix.csv` including prohibited joins |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is W4 and its consumers are earlier.** `RP-004` is **W1** and `RP-002` is W2, and both require every panel and report to name a certified dataset (`OC-05`, `CT-09`). **`P03` ships at W1 against datasets that do not exist**; a W1 subset covering `ds_service_order_fact`, `ds_work_order_fact`, `ds_stock_movement_fact`, `ds_branch_dim` and `ds_calendar_dim` is the minimum | BI Lead with Programme Content Lead | **W1 — subset needed** |
| **O-02** | **`M62` is a W8 platform capability in `06-01`** and this dictionary is W4. `BRU-DAT-01`…`12` describe the mechanism — metric registry, contract enforcement, query-engine RLS, certification display. **Until W8 the rules in §4.5 have no enforcement point**, and `SM-04`'s query-engine RLS in particular cannot be met by a presentation-tool filter without breaching `RP-005` `ED-02` | CTO with BI Lead | **W4 — interim enforcement position needed** |
| **O-03** | **No data contract exists for any producing module.** `BRU-DAT-10` requires a signed contract before data enters Silver, and `SM-10` restates it. Sixty-seven modules produce into this estate and **none has a contract**, so `BRU-DAT-07`'s pipeline-stop on schema change has no baseline to detect a change against | Solution Architect with BI Lead | **W4 — before the first Silver load** |
| **O-04** | **The eighteen datasets are named and outlined, not specified.** Fields, joins, prohibited joins, RLS columns, exclusions and quality tests are the substance and none is written — an estimated 90–140 person-days with data engineering and eleven business owners | BI Lead with Data Engineering | **W4; W1 for the `O-01` subset** |
| **O-05** | **`SM-16` residency and `NFR-086` split-residency have no legal opinion** — `DEP-31`/`D-13`, recorded as overdue in `TS-017` `O-04`. Several datasets join to residency-classified fields (`ds_party_dim`, `ds_employee_dim`), and **whether a resident-key join satisfies `NFR-086` in an analytical store is exactly the unanswered question** | CTO with Legal Counsel | **W4 — `DEP-31` already overdue** |
| **O-06** | **`ds_attendance_fact` carries a `T5` overlay for pay detail and `BRU-DAT-11` excludes `S3` by default.** Individual payslip data is `S3` (`05-02` §10). **Whether payroll analytics exist at all in the analytical estate is undecided**, and `RP-004` `C8` panel 5 shows payroll run state, which is metadata rather than pay data — a distinction that needs recording before it is blurred | Chief Data Officer with HR Manager | W4 |
| **O-07** | **`SM-08` originally cited `AUT-P06-59`, which does not exist** — `P06`'s automation range is `AUT-P06-01`…`AUT-P06-10` and the intended reference is `AUT-059` in `05-05` §12.5 (a data-quality test failure blocks the dependent dashboard refresh). **Corrected during the Category 14 audit** (`AUDIT-015` RP-14). Retained as an open item because the underlying risk stands: a portal-scoped and a programme-scoped automation identifier differing only by an infix will be conflated again | BI Lead | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the dataset schema
- [x] **The `RP-001` boundary stated first across five dimensions — metrics versus datasets**
- [x] Sixteen-field dataset schema, including the prohibited-joins and excluded-fields halves
- [x] **Eighteen datasets specified as business objects rather than module exports, with the reason**
- [x] Three certification levels with explicit gates, and `Provisional` labelled on every dependent view
- [x] Sixteen rules stated, each traced to a `BRU-DAT-*` or `PRU-P06-*`
- [x] **A self-service contract with a may / may not table, and the shadow-estate path named**
- [x] `ds_calendar_dim` called out as the dataset most likely to be treated as trivial and most able to break every duration metric
- [x] All internal links resolve
- [x] Seven open items recorded, including a self-reported identifier error (`O-07`)
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` W1 consumers against a W4 file — outstanding; a five-dataset subset is needed at W1**
- [ ] **`O-03` no module data contracts — outstanding; `BRU-DAT-07` has no baseline**
- [ ] **`O-04` the eighteen datasets outlined, not specified — outstanding**
- [ ] Named approvers recorded — **pending CTO and BI Lead**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
