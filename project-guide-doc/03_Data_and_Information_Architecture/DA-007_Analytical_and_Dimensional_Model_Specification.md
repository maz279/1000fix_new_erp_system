---
id: DA-007
title: Analytical & Dimensional Model Specification
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Architect
approver: Chief Technology Officer
standards_basis: >
  Kimball dimensional modelling (bus matrix, conformed dimensions, SCD types) ·
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Data Warehousing & BI ·
  ClickHouse MergeTree · ISO/IEC 25012
traces_to: >
  PGD-000 DA-007 · 05-02 §9 (13 dimensions, 17 facts) · RP-006 (18 certified datasets) ·
  RP-001 (KPI dictionary) · audit RP-01, RP-02 (critical) · M62, M25 · NFR-039 · DI-06
depends_on: DA-001 · DA-002 · DA-005 · AR-008 · RP-006
verified_on: 2026-08-18
priority: P1
needed_by: W4
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-007 — Analytical & Dimensional Model Specification

### Category 03 · Code `DA` · Kimball dimensional modelling · ClickHouse

---

## 1. Purpose

Two dimensional models exist in this estate and **neither references the other**.

| Model | Content | Written |
|---|---|---|
| `05-02` §9 | **13 conformed dimensions and 17 fact tables**, with SCD types declared | 2026-08-12, for 30 modules |
| `RP-006` §4.3 | **18 certified datasets** — 13 facts and 5 dimensions — with a 16-attribute schema each | Later, for the semantic layer |

`RP-006` states its count deliberately: *"Eighteen, not one per module."* Its reasoning is sound. But
**`05-02` declares eight dimensions `RP-006` does not have** — `dim_part`, `dim_vendor`, `dim_seller`,
`dim_contract`, `dim_fault`, `dim_channel`, `dim_business_line`, `dim_time` — and four facts it does
not carry.

This document is the reconciliation, and the physical dimensional model beneath `RP-006`'s semantic
layer: the bus matrix, the grain declarations, the slowly-changing-dimension policy, the surrogate-key
strategy, and the ClickHouse realisation.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The reconciliation of `05-02` §9 and `RP-006` §4.3 |
| 2 | **The bus matrix** — facts × conformed dimensions |
| 3 | **Grain declarations** — one sentence per fact, enforced |
| 4 | Conformed dimension design and the conformance rule |
| 5 | **Slowly-changing-dimension policy**, per dimension, with the merge case |
| 6 | Surrogate keys, natural keys and late-arriving data |
| 7 | Fact table types — transaction, periodic snapshot, accumulating snapshot |
| 8 | Degenerate dimensions, junk dimensions and bridges |
| 9 | ClickHouse physical design — engines, ordering, partitioning, TTL |
| 10 | The metric layer, and the **250-vs-95 KPI problem** |
| 11 | Load patterns, data contracts and quality gates |
| 12 | Personal data and residency in the warehouse |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The semantic layer and its 16-attribute dataset schema | **`RP-006`** | Excellent and retained; this document is the physical model beneath it |
| KPI definitions and formulas | `RP-001` | This document says how a metric is computed *from* the model |
| Dashboards, reports, chart standards | `RP-002`…`RP-014` | |
| OLTP schema | `DA-001` | Source, not target |
| ETL tooling and orchestration | `MG-003`, CD-243 | This document states what must arrive |
| ML feature stores | `AR-011` §5.2 | Features derive from here |
| Warehouse infrastructure sizing | `PE-006` | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **M62 developers** | The physical model to build |
| M25 / `RP-006` owners | §2 reconciliation; §10 metric layer |
| Data engineers | §9 ClickHouse design; §11 load patterns |
| Analysts | §3 grain and §4 conformance — why a join is or is not permitted |
| DPO | §12 — personal data in the warehouse |

---

## 2. Reconciling the Two Models

### 2.1 What each contains

| | `05-02` §9 | `RP-006` §4.3 |
|---|---:|---:|
| Dimensions | **13** | **5** |
| Facts | **17** | **13** |
| Total | **30** | **18** |
| Per-object metadata | Grain + key attributes + SCD type | **16 attributes** incl. joins, RLS, freshness, quality tests, exclusions |
| Purpose | Physical dimensional model | **Certified semantic datasets** |

### 2.2 The reconciliation

> **They are not competing models. They are two layers, and neither says so.**

| Layer | Artefact | Content |
|---|---|---|
| **Physical dimensional model** | **This document** | Every dimension and fact table that exists in ClickHouse, including those no analyst queries directly |
| **Certified semantic layer** | **`RP-006`** | The 18 objects an analyst may query, each with joins, RLS binding, freshness and quality tests |

**`RP-006`'s 5 dimensions are the 5 an analyst joins directly.** The other 8 in `05-02` are **real
tables** that either (a) join through a fact, or (b) are conformed dimensions used by facts not yet
certified.

### 2.3 The reconciled model

| `05-02` §9 object | Status in this model | `RP-006` |
|---|---|---|
| `dim_date` | **Conformed dimension** | `ds_calendar_dim` ✔ |
| `dim_time` | **Merged into `dim_date`** as time-of-day attributes | — |
| `dim_customer` | **Renamed `dim_party`** — a party may be customer, seller, vendor or partner (`AR-008` §3) | `ds_party_dim` ✔ |
| `dim_asset` | Conformed | `ds_asset_dim` ✔ |
| `dim_employee` | Conformed | `ds_employee_dim` ✔ |
| `dim_branch` | Conformed | `ds_branch_dim` ✔ |
| `dim_business_line` | **Conformed** | ✘ **not certified** — joins through facts |
| `dim_part` | **Conformed** | ✘ not certified — required by `ds_stock_movement_fact` |
| `dim_vendor` | **Merged into `dim_party`** — a vendor is a party role | — |
| `dim_seller` | **Merged into `dim_party`** — a seller is a party role | — |
| `dim_contract` | **Degenerate → dimension** (§8.1) | Carried in `ds_contract_fact` |
| `dim_fault` | **Conformed** | ✘ not certified — required for quality analysis |
| `dim_channel` | **Junk dimension** (§8.2) | — |
| 17 facts | 13 certified + 4 uncertified (§2.4) | |

> **The `dim_customer` → `dim_party` rename is not cosmetic.** `AR-008` §3 rules that a party holds
> multiple roles simultaneously — *"a marketplace seller can also be a customer"*. Three separate
> dimensions (`dim_customer`, `dim_vendor`, `dim_seller`) would reproduce in the warehouse exactly the
> duplicate-identity problem the OLTP kernel exists to prevent, and every cross-role analysis would
> require an analyst-invented union.

### 2.4 The four uncertified facts

| Fact | Why not certified | Certification path |
|---|---|---|
| `fact_inventory_snapshot` | Periodic snapshot; `RP-006` certifies the movement fact | Certify at W6 when demand planning (M43) needs it |
| `fact_technician_day` | Derivable from `ds_work_order_fact` + `ds_attendance_fact` | **Assess whether it is needed at all** — a derived fact that duplicates two certified ones is a maintenance cost |
| `fact_rental_period`, `fact_refurb_unit` | W6 business lines | Certify with M13 / M14 |

**Also present in `05-02` and not in `RP-006`:** `fact_dispatch`, `fact_msp_alert`, `fact_quality_event`,
`fact_ewaste`. Each is a genuine fact; each certifies with its module's wave.

### 2.5 Finding

> **`PGD-A5-14` — two dimensional models exist and neither references the other.**
>
> `05-02` §9 (30 objects) and `RP-006` §4.3 (18 objects) overlap on 18, diverge on 12, and **contain
> no cross-reference in either direction**. An engineer building M62 from `05-02` builds
> `dim_customer`, `dim_vendor` and `dim_seller`; an analyst reading `RP-006` expects `ds_party_dim`.
>
> §2.3 reconciles them. **`RP-006` is retained unchanged** — it is the better document for what it
> covers — and this document becomes the physical layer beneath it.

---

## 3. Grain

### 3.1 The rule

> **Declare the grain first, in one sentence, before any column.** `RP-006` `SM-01` already requires
> it: *"A dataset whose row cannot be described in a sentence has not been modelled."*

| # | Rule |
|---|---|
| **GR-01** | Every fact declares its grain as **one sentence describing what one row is** |
| **GR-02** | **Grain is enforced**: a build producing a different grain **fails** (`RP-006` `SM-02`, `BRU-DAT-08`) |
| **GR-03** | **Never mix grains in one fact.** A fact with both order-level and line-level rows double-counts on every measure |
| **GR-04** | Grain is stated at the **lowest atomic level available**. Aggregates are derived, never stored in place of the atom |
| **GR-05** | Every fact is **decomposable to its source records** (`RP-006` `SM-11`), and the decomposition path is recorded |

### 3.2 The grain declarations

| Fact | **One row is** | Type |
|---|---|---|
| `fact_service_order` | One service order | Transaction |
| `fact_work_order` | One field or workshop work order | Transaction |
| `fact_sla_event` | One SLA clock event — start, hold, resume, breach | Transaction |
| `fact_invoice_line` | One invoice line | Transaction |
| `fact_payment` | One payment or receipt | Transaction |
| `fact_gl_posting` | One general-ledger posting line | Transaction |
| `fact_stock_movement` | One stock movement | Transaction |
| `fact_claim` | One warranty claim | **Accumulating snapshot** (§7.3) |
| `fact_contract_period` | One contract × one period, with entitlement position | **Periodic snapshot** |
| `fact_conversation` | One customer conversation across any channel | Transaction |
| `fact_survey_response` | One CSAT or NPS response | Transaction |
| `fact_attendance` | One employee × one day | **Periodic snapshot** |
| `fact_marketplace_job` | One marketplace job with its commission | Transaction |
| `fact_dispatch` | One assignment decision | Transaction |
| `fact_inventory_snapshot` | One part × one location × one day | Periodic snapshot |
| `fact_msp_alert` | One alert | Accumulating snapshot |
| `fact_quality_event` | One NCR, complaint or rework event | Accumulating snapshot |
| `fact_ewaste` | One e-waste item | Transaction |
| `fact_rental_period` | One rental asset × one day | Periodic snapshot |
| `fact_refurb_unit` | One refurbished unit | Accumulating snapshot |

### 3.3 The prohibited joins

`RP-006` `SM-03` requires prohibited joins to be **declared explicitly with the double-count they
would cause**. The critical ones:

| Prohibited | Why | Correct route |
|---|---|---|
| `fact_service_order` ⋈ `fact_invoice_line` | **A job can produce many invoice lines and an invoice can cover many jobs.** Direct join double-counts both revenue and volume | Through `dim_date` + `dim_party`, or a declared bridge |
| `fact_work_order` ⋈ `fact_stock_movement` | A work order consumes many parts; a movement may serve several | Aggregate one side first |
| `fact_claim` ⋈ `fact_invoice_line` | A claim may cover several invoiced jobs | Through `dim_date` + `dim_party` |
| `fact_attendance` ⋈ `fact_work_order` | Employee-day vs work-order grain | Aggregate work orders to employee-day |
| Any two facts directly | **Facts join to dimensions, never to each other** | Drill-across on conformed dimensions (§4.3) |

> **`fact_service_order ⋈ fact_invoice_line` is the most likely wrong number in the estate**, and
> `RP-006` §4.2 already identifies it. It is repeated here because it is the join an analyst will
> reach for first when asked "revenue per job".

---

## 4. Conformed Dimensions

### 4.1 The conformance rule

> **A conformed dimension has the same meaning, the same key and the same attribute values wherever it
> is used.** That is what makes drill-across possible.

| # | Rule |
|---|---|
| **CD-01** | A conformed dimension is **defined once and shared**. A second `dim_branch` is a defect |
| **CD-02** | Attribute **names and values** are identical across every fact using it |
| **CD-03** | A fact using a conformed dimension uses **the conformed key**, never a local variant |
| **CD-04** | Adding an attribute is additive; **changing an attribute's meaning is a restatement** (`RP-006` `SM-15`) |
| **CD-05** | Every conformed dimension has **one business owner** (`DA-003` §3.2) |

### 4.2 The conformed set

| Dimension | Grain | Owner | SCD | Certified |
|---|---|---|:--:|:--:|
| **`dim_date`** | One calendar date | DD-09 Ops | Type 0 | ✔ |
| **`dim_party`** | One party (any role) | DD-01 CCO | **Type 2** | ✔ |
| **`dim_asset`** | One device or asset | DD-02 Service Ops | **Type 2** | ✔ |
| **`dim_employee`** | One employee | DD-07 HR | **Type 2** | ✔ |
| **`dim_branch`** | One branch or service centre | DD-09 Ops | **Type 2** | ✔ |
| **`dim_part`** | One part | DD-05 Supply Chain | **Type 2** | ✘ |
| **`dim_business_line`** | One business line | DD-06 CFO | Type 1 | ✘ |
| **`dim_fault`** | One fault code | DD-11 Technical | Type 1 | ✘ |
| **`dim_catalogue_item`** | One sellable item | DD-03 CCO | **Type 2** | ✘ |

### 4.3 `dim_date` — the one most often treated as trivial

`RP-006` says it plainly: *"`ds_calendar_dim` carries the fiscal year (July–June) and the `MD-041`
holiday calendar including moon-dependent dates. Every 'working days' metric — `KPI-050` close cycle
above all — is wrong without it."*

| Attribute class | Content |
|---|---|
| Calendar | Date, day, week, month, quarter, year, day-of-week |
| **Fiscal** | **Fiscal period, quarter and year on a July–June year** |
| **Bangladesh holidays** | Public holidays **including moon-dependent dates**, which cannot be computed and must be loaded per year from `MD-041` |
| Ramadan | Flag — service demand and working hours both shift materially |
| Working day | Flag, per branch calendar |
| Time-of-day | Hour, shift, peak flag — **the merged `dim_time`** (§2.3) |

> **Moon-dependent dates are the reason `dim_date` cannot be generated.** Eid dates are announced, not
> calculated. A warehouse that generates its own calendar will compute Bangladeshi working days wrongly
> every year, and the error will surface in the month-end close metric.

---

## 5. Slowly Changing Dimensions

### 5.1 Policy per dimension

| Dimension | Type | What is tracked | Why |
|---|:--:|---|---|
| `dim_date` | **0** | Nothing changes | |
| `dim_party` | **2** | Segment, tier, credit terms, division, district, acquisition source | **A job done in 2027 was done for a Silver customer even if they are Gold in 2029.** Type 1 would restate history |
| `dim_asset` | **2** | Category, brand, model, ownership, condition grade | Ownership transfer must not rewrite prior service history |
| `dim_employee` | **2** | Role, grade, branch, zone, skills, certifications | Attributing a 2027 job to a technician's 2029 grade is wrong, and it feeds incentive analysis |
| `dim_branch` | **2** | Division, district, size band, capabilities | A branch that changes size band must not restate its league history |
| `dim_part` | **2** | Category, class, ABC/XYZ, supersession chain | Supersession is a history, not a correction |
| `dim_catalogue_item` | **2** | Category, family, service type | |
| `dim_business_line` | **1** | Name, pillar | A rename is a rename |
| `dim_fault` | **1** | Description, category | A taxonomy correction is a correction |

### 5.2 Type 2 mechanics

| Column | Purpose |
|---|---|
| `<dim>_sk` | **Surrogate key** — unique per version, never the natural key |
| `<dim>_nk` | Natural key — the OLTP `id`, stable across versions |
| `valid_from`, `valid_to` | Version window; `valid_to` null or `9999-12-31` for current |
| `is_current` | Convenience flag |
| `version_no` | Sequence |
| `change_reason` | **Why the version was created** — the attribute that makes an audit answerable |

| # | Rule |
|---|---|
| **SC-01** | **A fact stores the surrogate key in force at the event's timestamp**, never the current one |
| **SC-02** | A Type-2 change creates a **new row**; the old row is closed, never updated in place beyond `valid_to` |
| **SC-03** | **Only declared attributes trigger a new version.** A phone-number correction is a Type-1 overwrite; a segment change is Type 2 |
| **SC-04** | The current-version query is a **filter on `is_current`**, not `ORDER BY valid_from DESC LIMIT 1` |
| **SC-05** | Overlapping versions for one natural key are a **quality-gate failure** (`DA-001` §4.7 E-02 applied in the warehouse) |

### 5.3 The merge case — what `DA-004` §5.2 hands to this document

A party merge (`party.merged`) is a **hard case for a Type-2 dimension** and no document currently
handles it.

| # | Rule |
|---|---|
| **MG-01** | On `party.merged`, the **loser's `dim_party` rows are closed** with `change_reason = 'merged'` and a `merged_into_sk` pointer |
| **MG-02** | **Historical facts keep their original surrogate key.** A 2027 order remains attributed to the party version in force in 2027 |
| **MG-03** | A **bridge** (`bridge_party_merge`) maps loser surrogate keys to the survivor's natural key, so *"all orders for this customer, including before the merge"* is answerable |
| **MG-04** | Reporting **defaults to the merged view** (via the bridge); the unmerged view remains available and is the audit position |
| **MG-05** | An **unmerge within the 90-day window** (`DA-004` UM-01) reverses MG-01 and MG-03 |

> **MG-02 is the decision.** Re-pointing historical facts to the survivor would be simpler to query and
> would **silently restate every published report** containing those orders. Keeping the fact and
> bridging the dimension preserves both the historical statement and the consolidated view.

---

## 6. Keys and Late-Arriving Data

| # | Rule |
|---|---|
| **KY-01** | Every dimension has a **surrogate key**; facts reference surrogates only |
| **KY-02** | The natural key is retained for lineage and for the source join |
| **KY-03** | **A fact arriving before its dimension row** is assigned an **inferred member** — a placeholder dimension row with the natural key and `is_inferred = true`, resolved on the next dimension load |
| **KY-04** | **An inferred member is a quality signal**, counted and reported. A persistent one indicates a broken load order, not a data problem |
| **KY-05** | **Late-arriving facts** are loaded with the dimension version in force at the **event timestamp**, not the load timestamp |
| **KY-06** | A **degenerate dimension** (order number, invoice number) stays on the fact — no dimension table for a bare identifier |

> **KY-05 is the rule that makes a late-arriving offline sync correct.** A technician's work completed
> at 11:20 and synced at 18:00 (`AR-010`) must attribute to the technician's 11:20 grade and the
> customer's 11:20 segment.

---

## 7. Fact Table Types

### 7.1 Transaction

One row per event. Additive measures. **The default and the preferred type.**

### 7.2 Periodic snapshot

One row per entity per period. **Semi-additive** — a stock balance sums across parts but not across
days. Used for `fact_inventory_snapshot`, `fact_attendance`, `fact_contract_period`,
`fact_rental_period`.

| # | Rule |
|---|---|
| **PS-01** | The period grain is declared and never mixed |
| **PS-02** | **Semi-additivity is documented on every measure** — a measure summed across the wrong dimension is a wrong number that looks right |

### 7.3 Accumulating snapshot

One row per process instance, **updated as it progresses**, with a column per milestone. Used for
`fact_claim`, `fact_quality_event`, `fact_msp_alert`, `fact_refurb_unit`.

| # | Rule |
|---|---|
| **AS-01** | One row per instance; milestone dates fill in as the process advances |
| **AS-02** | **Lag measures are stored, not computed at query time** — days-to-submit, days-to-decision, days-to-payment |
| **AS-03** | ClickHouse's append-oriented engines make in-place update awkward; §9.3 states the pattern |

> **`fact_claim` is the estate's clearest accumulating-snapshot case.** A warranty claim moves through
> created → evidence assembled → submitted → decided → remitted, and **the whole management question
> is how long each step takes**. Modelling it as a transaction fact would require five self-joins to
> answer it.

---

## 8. Degenerate, Junk and Bridge

### 8.1 Degenerate dimensions

Order number, invoice number, claim number, consignment number — **identifiers with no attributes**.
They stay on the fact. `dim_contract` from `05-02` is degenerate at the fact level and a genuine
dimension where contract attributes are needed.

### 8.2 Junk dimensions

Low-cardinality flags and indicators combined into one dimension rather than a column each.

| Junk dimension | Combines |
|---|---|
| `dim_service_context` | Channel, order type, priority, delivery mode, warranty flag |
| `dim_payment_context` | Method, rail, instalment flag, refund flag |

> `05-02`'s `dim_channel` becomes an attribute of `dim_service_context`. Channel alone is one attribute
> with six values; combining it with the other five context flags gives one join instead of five.

### 8.3 Bridges

| Bridge | Resolves |
|---|---|
| `bridge_party_merge` | §5.3 MG-03 — pre-merge facts to the surviving party |
| `bridge_party_role` | **A party holding several roles simultaneously** (`AR-008` §3) — the many-to-many that makes "seller who is also a customer" answerable |
| `bridge_contract_asset` | A contract covering many assets; an asset on many contracts over time |
| `bridge_order_invoice` | **The declared route for the prohibited `fact_service_order ⋈ fact_invoice_line` join** (§3.3), with allocation factors |

> **`bridge_order_invoice` is how the prohibited join becomes a permitted one.** It carries an
> allocation factor so revenue attributed from an invoice covering four jobs sums to 100% and not 400%.

---

## 9. ClickHouse Physical Design

### 9.1 Why ClickHouse (ADR-009)

Analytical volume from Wave 8 exceeds what a PostgreSQL read replica can serve economically. The
model above is engine-neutral; this section is the realisation.

### 9.2 Engines

| Object | Engine | Rationale |
|---|---|---|
| Transaction facts | `MergeTree` | Append-only, the natural fit |
| Periodic snapshots | `MergeTree`, partitioned by period | |
| **Accumulating snapshots** | **`ReplacingMergeTree`** ordered by the process key | §9.3 |
| Type-2 dimensions | `ReplacingMergeTree` on `(nk, version_no)` | Versions accumulate; latest wins on merge |
| Type-1 dimensions | `ReplacingMergeTree` on `nk` | |
| Pre-aggregations | `AggregatingMergeTree` + materialised view | §9.5 |

### 9.3 The accumulating-snapshot pattern

`ReplacingMergeTree` deduplicates **eventually**, not immediately. A milestone update inserts a new
row version; a query before the background merge sees both.

| # | Rule |
|---|---|
| **CH-01** | Every accumulating-snapshot query uses **`FINAL`** or an explicit `argMax` per column |
| **CH-02** | The **certified dataset (`RP-006`) exposes a view that applies this**, so no analyst must remember it |
| **CH-03** | `version` is the **load sequence**, so the latest wins deterministically |

> **CH-01 is the single most likely source of a wrong number in a ClickHouse warehouse**, and it is
> invisible: the query returns a plausible result with duplicated rows. CH-02 is why the semantic layer
> exists.

### 9.4 Ordering and partitioning

| Object | `ORDER BY` | `PARTITION BY` |
|---|---|---|
| `fact_service_order` | `(branch_sk, date_sk, service_order_sk)` | `toYYYYMM(date)` |
| `fact_invoice_line` | `(company_sk, date_sk, invoice_sk, line_no)` | `toYYYYMM(date)` |
| `fact_gl_posting` | `(company_sk, fiscal_period, account_sk)` | `fiscal_period` |
| `fact_stock_movement` | `(location_sk, date_sk, part_sk)` | `toYYYYMM(date)` |
| `fact_attendance` | `(employee_sk, date_sk)` | `toYYYYMM(date)` |
| Dimensions | `(nk, version_no)` | none — dimensions are small |

| # | Rule |
|---|---|
| **CH-04** | `ORDER BY` leads with the **most common filter**, then the date, then the grain key |
| **CH-05** | **Partition monthly, not daily.** Daily partitions on a five-year fact produce ~1,800 parts and degrade planning |
| **CH-06** | **TTL clauses implement `DA-006`'s retention in the warehouse** — the warehouse is a store an erasure must reach (`DA-006` §5.2 store 4) |

### 9.5 Pre-aggregation

| # | Rule |
|---|---|
| **CH-07** | Pre-aggregate only where a **measured** query breaches NFR-039 (≤ 10 s p95) |
| **CH-08** | Every pre-aggregation is a **materialised view over an atomic fact**, never a replacement for it (GR-04) |
| **CH-09** | A pre-aggregation is **registered as a dataset** with its own grain, or it becomes a shadow model |

---

## 10. The Metric Layer and the KPI Problem

### 10.1 The rule

| # | Rule |
|---|---|
| **ML-01** | **A metric is defined once, in `RP-001`, and computed in one place** |
| **ML-02** | Every metric declares the **dataset it is computed from** (`RP-006` attribute 16) and the grain it is valid at |
| **ML-03** | A metric computed in two places is a defect, whatever the two places agree today |
| **ML-04** | A metric change follows **restatement discipline**: version, consumer notification before effect, stated history position (`RP-006` `SM-15`) |

### 10.2 The measured problem

> **Audit `RP-01` (critical):** *"250 distinct `KPI-` identifiers in use against 95 registered."*

| Position | Count |
|---|---:|
| Registered in `06-02` §2 | **95** |
| Distinct `KPI-` identifiers in use | **250** |
| **In use but unregistered** — a contiguous block `KPI-110`…`KPI-305` | **196** |
| Registered but used by no module | **41** |
| Both registered and used | 54 |

**The cause is documented and was not connected:** the Category E module audit records *"KPI register
exhausted. `06-02` §2.6 stops at KPI-049."* **Module authors did not redefine metrics; they ran out of
numbers.**

### 10.3 Why this is a `DA-007` problem and not only an `RP-001` problem

| Consequence | Detail |
|---|---|
| **A dataset cannot declare `metrics_served`** | `RP-006` attribute 16 requires the `KPI-nnn` identifiers a dataset serves. 196 of them resolve to no owner, no formula and no target |
| **A metric with no formula cannot be assigned a grain** | ML-02 is unsatisfiable for 196 metrics |
| **`RP-02` compounds it** | **44 of 95 baselines are absent.** A metric with no baseline cannot be assessed as met or missed |
| **The warehouse would encode the ambiguity** | Building `fact_*` measures against unregistered metrics bakes 196 undefined definitions into physical tables |

### 10.4 The position

| # | Rule |
|---|---|
| **KP-01** | **A dataset may not declare `metrics_served` for an unregistered `KPI-nnn`.** It declares them as `Provisional` and the dashboard carries the label (`RP-006` §4.4) |
| **KP-02** | **`DA-007` does not physicalise a measure for an unregistered metric.** The atomic fact carries the source measures; the metric is a semantic-layer calculation until registered |
| **KP-03** | Registration of the 196 is `RP-001`'s and Enterprise Architecture's, per `RP-01`'s remediation |
| **KP-04** | `KPI-018` — **one identifier over two different metrics** (on-time collection and on-time delivery in `M03`) — must be **split before either is physicalised** |

> **KP-02 is the protective rule.** Storing a measure in a fact table commits its definition to
> physical schema. Leaving it in the semantic layer keeps it changeable while 196 metrics are being
> ratified.

---

## 11. Load, Contracts and Quality

| # | Rule |
|---|---|
| **LD-01** | Every producing module has a **signed data contract** before its data enters the warehouse (`RP-006` `SM-10`, `BRU-DAT-10`) |
| **LD-02** | **An unexpected schema change stops the pipeline. The platform never infers a mapping** (`BRU-DAT-07`) |
| **LD-03** | Loads are **incremental by event or watermark**, never full-refresh at fact volume |
| **LD-04** | **Dimensions load before facts**; a fact arriving early gets an inferred member (KY-03) |
| **LD-05** | Every dataset declares a **freshness guarantee**; breaching it flags every dependent view (`SM-07`) |
| **LD-06** | Every dataset carries **`DI-06` quality tests**, and a failure **blocks dependent refresh** (`SM-08`) |
| **LD-07** | Loads are **idempotent and restartable** |
| **LD-08** | **Analytical queries never run against a transactional database** (`SM-13`) |

### 11.1 Quality gates

| Gate | Check |
|---|---|
| Grain | Row count at declared grain matches expectation; duplicates at grain = failure (GR-02) |
| Referential | Every fact FK resolves to a dimension row; inferred members counted (KY-04) |
| **Reconciliation** | **Fact totals reconcile to the source system** — invoice line sum vs GL, movement sum vs stock balance |
| SCD integrity | No overlapping versions per natural key (SC-05) |
| Freshness | Load completed within the guarantee |
| Completeness | Expected periods present; no gaps |

> **Reconciliation is the gate that catches the errors the others miss.** A load can pass grain,
> referential integrity and freshness and still be missing a day's invoices.

---

## 12. Personal Data and Residency in the Warehouse

| # | Rule |
|---|---|
| **PD-01** | **`S3` fields are excluded by default** (`RP-006` `SM-05`, `BRU-DAT-11`). Inclusion requires named, approved, time-limited authorisation recorded in the dataset's `excluded_fields` |
| **PD-02** | **Residency-classified fields never leave the resident store.** A dataset joins by **resident key** without duplicating the field (`SM-16`, `DA-001` §10) |
| **PD-03** | **Row-level security is bound to a `05-04` tier and enforced in the query engine**, never in the presentation tool (`SM-04`, `BRU-DAT-12`) |
| **PD-04** | **The warehouse is in erasure scope** — `DA-006` §5.2 store 4. TTL and targeted delete both apply |
| **PD-05** | Aggregates over personal data respect the **minimum group size of 5** (`DA-005` AG-02) |
| **PD-06** | `dim_employee` **excludes pay fields** (`RP-006` §4.3); pay analysis uses `fact_attendance` under `T5` |

> **PD-04 is the one that makes warehouse design harder than it looks.** A columnar append-oriented
> store is optimised for never deleting anything. An erasure must still reach it, which is why §9.4
> partitions monthly — a partition is the unit a targeted delete can operate on economically.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is the §2.3 reconciliation accepted (`PGD-A5-14`)?** Specifically the `dim_customer`/`dim_vendor`/`dim_seller` → `dim_party` merge | Enterprise Architecture / M62 | **W4 — blocking M62** | The physical model |
| **Q-02** | **Are the 196 unregistered KPIs ratified before W4?** `RP-006` cannot declare `metrics_served` without them | Enterprise Architecture / CTO | **W4** | KP-01, KP-02 |
| **Q-03** | Is `KPI-018` split before physicalisation (KP-04)? | Enterprise Architecture | W4 | `fact_consignment` measures |
| **Q-04** | **Are the 44 missing baselines measured before go-live changes them?** (`RP-02`) `BM-002` is time-critical in a way the others are not | Programme Director / `BM-002` | **Now** | Benefit assessability |
| **Q-05** | Is `fact_technician_day` needed, or derivable? (§2.4) | M25 / M62 owners | W4 | Model size |
| **Q-06** | Does `05-02` §9 get reissued to match §2.3, or is `DA-007` the authority? | Enterprise Architecture | W4 | Which document M62 builds from |
| **Q-07** | Is the minimum group size of 5 workable for a 51-branch network? (`DA-005` Q-04) | CDO / Ops | W4 | PD-05 |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D7-01 | Two models | Pick one; **two layers** | **Physical (`DA-007`) beneath semantic (`RP-006`)** | Both are right for what they cover and neither said so | `RP-006` retained unchanged |
| D-D7-02 | Party dimensions | Three (`customer`/`vendor`/`seller`); **one `dim_party`** | **One** | Three would reproduce in the warehouse the duplicate-identity problem the OLTP kernel prevents | `bridge_party_role` for multi-role analysis |
| D-D7-03 | `dim_time` | Separate; **merged into `dim_date`** | **Merged** | A separate minute dimension joins on every fact for six attributes | Time-of-day attributes on `dim_date` |
| D-D7-04 | Merge handling in facts | Re-point to survivor; **keep original SK + bridge** | **Keep + bridge** | Re-pointing silently restates every published report | MG-02, MG-03 |
| D-D7-05 | Late-arriving dimension | Reject the fact; **inferred member** | **Inferred member** | Rejecting loses the fact; inferring keeps it and flags the load order | KY-03, KY-04 |
| D-D7-06 | Unregistered KPIs | Physicalise anyway; **semantic layer only until registered** | **Semantic only** | Physicalising commits 196 undefined definitions to schema | KP-02 |
| D-D7-07 | ClickHouse partition | Daily; **monthly** | **Monthly** | Daily gives ~1,800 parts on a five-year fact; monthly is also the erasure unit | CH-05, PD-04 |
| D-D7-08 | Accumulating snapshots | Transaction fact + self-joins; **`ReplacingMergeTree` + view** | **Accumulating** | The management question is step duration; five self-joins is not an answer | CH-01, CH-02 |

---

## 15. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The two existing models are reconciled object by object | §2.3 |
| AC-02 | **Every fact declares its grain in one sentence** | §3.2 — 20 facts |
| AC-03 | Prohibited joins are declared with the double-count they cause | §3.3 |
| AC-04 | Conformed dimensions have one owner and a conformance rule | §4.1, §4.2 |
| AC-05 | SCD type is declared per dimension with the reason | §5.1 |
| AC-06 | **The party-merge case is handled** — the gap `DA-004` §5.2 hands over | §5.3 |
| AC-07 | Late-arriving data has an inferred-member policy | §6 KY-03…KY-05 |
| AC-08 | ClickHouse engine, ordering, partitioning and the `FINAL` trap are specified | §9 |
| AC-09 | The 250-vs-95 KPI problem has a stated position that does not bake ambiguity into schema | §10.4 |
| AC-10 | Personal data, residency and erasure in the warehouse are addressed | §12 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are resolved, and
`PGD-000`'s `DA-007` row is updated.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DA-001` | Source grain; OLTP structure |
| Upstream | `DA-002` | Field meaning; lineage |
| Upstream | `DA-005` §6.6 | Warehouse handling rules |
| Upstream | `AR-008` | The party kernel — why `dim_party` is one dimension |
| Upstream | **`RP-006`** | The semantic layer this sits beneath. **Retained unchanged** |
| Upstream | `RP-001` | Metric definitions |
| Downstream | **`M62`, `M25`** | The physical model to build |
| Downstream | `AR-011` §5.2 | ML features derive from these facts |
| Downstream | `DA-006` §5.2 | The warehouse is store 4 in the erasure saga |
| Downstream | `DA-008` | Quality gates §11.1 feed the scorecard |
| Downstream | `BM-002` | Baselines (Q-04) |
| Lateral | `05-02` §9 | Reconciled in §2.3; reissue is Q-06 |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md` ·
`./DA-004_Master_Data_Management_Design.md` §5.2 ·
`./DA-005_Data_Classification_and_Handling_Standard.md` §6.6 ·
`./DA-006_Data_Retention_Archival_and_Deletion_Design.md` §5.2 ·
`./DA-008_Data_Quality_Management_Plan.md` ·
`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §9 ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-006_BI_Semantic_Layer_Data_Dictionary.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md` ·
`../../project_content/_AUDIT/AUDIT-015_Category_14_RP_Content_Audit.md` `RP-01`, `RP-02` ·
`../../project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`

**External standards**

| Source | Version | Verified |
|---|---|---|
| Kimball & Ross, *The Data Warehouse Toolkit* — bus matrix, conformed dimensions, SCD types, fact table types | 3rd edition | 2026-08-18 |
| [DAMA-DMBOK](https://www.damadmbok.org/) — Data Warehousing & BI | 2.0 (2024 maintenance revision) | 2026-08-18 |
| ClickHouse MergeTree engine family | 24.x | 2026-08-18 |

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Reconciles `05-02` §9's 30 objects with `RP-006`'s 18 as **two layers, not two models**. Declares grain for 20 facts and SCD policy for 9 dimensions. Handles the party-merge case `DA-004` hands over. Raises `PGD-A5-14` (two unreferenced models) and states the position on the 196 unregistered KPIs | *Pending — CTO* |

---

*`DA-007` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
