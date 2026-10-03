---
id: DA-001
title: Logical & Physical Data Model / Database Schema Specification
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Architect
approver: Chief Architect
standards_basis: >
  ISO/IEC 11179-1:2023 (metadata registries) · DAMA-DMBOK 2.0 (2024 maintenance revision) ·
  Third normal form · PostgreSQL 16 declarative partitioning · Odoo 19 ORM conventions ·
  ISO/IEC/IEEE 42010:2022 information viewpoint
traces_to: >
  PGD-000 DA-001 · AR-008 (aggregates and invariants) · 05-02 DM-01…DM-15 · AS-03, AS-04, AS-10, AS-11 ·
  NFR-053, NFR-054, NFR-060, NFR-086/086a · DI-01…DI-08
depends_on: AR-008 · AR-005 · DA-005 (classification) · BE-005 (CD register)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-001 — Logical & Physical Data Model / Database Schema Specification

### Category 03 · Code `DA` · ISO/IEC 11179-1:2023 · 3NF · PostgreSQL 16 · Odoo 19 ORM

---

> **The measurement that sizes this document.** Extracting the `### 10.1 Owned Entities` table from
> all 67 module specifications at **2026-08-18 14:30 (+06)** returns **1,370 entity rows, 1,335
> distinct tables and 11,622 declared key attributes across 5,301 distinct field names.**
>
> `05-02_Data_Model_and_Entity_Catalogue.md` is titled *"225 Entities Across 30 Modules"*. It is
> correct for what it covers and was never restated. **This document is scoped to 1,335 tables, not
> 225** — a difference of roughly **6×** that changes what `DA-001` costs and how long it takes.

---

## 1. Purpose

`05-02` gives entity **names** and narrative ERDs. `AR-008` assigns **aggregates and invariants**.
Neither gives a developer a column, a type, a constraint, an index or a partition key.

This document is the schema: the standard column contract every table inherits, the type and naming
rules, the constraint and referential-integrity policy, the index and partition design with **named
partition keys**, the Odoo ORM mapping that makes it buildable, and the residency split that makes it
lawful.

It unblocks: every one of the 58+ custom Odoo modules, the migration mapping workbooks
(`DM-004`…`DM-010`) which currently target assumed structure, `DA-002`'s field-level dictionary, and
`SC-007`'s residency design.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The measured schema population, and its reconciliation against `05-02` |
| 2 | **The standard column contract** — what every table carries whether or not its specification says so |
| 3 | Naming, type and domain rules, including money, time, text and Bengali collation |
| 4 | Key strategy — surrogate, natural, business and sequence |
| 5 | Constraint policy — not-null, check, unique, and the `ondelete` matrix |
| 6 | Referential integrity across the module boundary, and across the residency boundary |
| 7 | **Index design** and the queries each index exists for |
| 8 | **Partitioning, with named partition keys** — the assertion `02-05` §8 makes and does not discharge |
| 9 | The three-tier Odoo ORM mapping: core → OCA → `cd_*` |
| 10 | The residency-split physical model and the resident-key join |
| 11 | Time-series and analytical store boundaries |
| 12 | DDL generation, migration shape and the schema-change contract |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Field-level business definitions, valid values, PII flags | `DA-002` Data Dictionary | This document gives structure; `DA-002` gives meaning |
| Aggregate boundaries and invariants | `AR-008` | This document realises them physically |
| Classification scheme and handling rules | `DA-005` | This document consumes the classes |
| Retention mechanism | `DA-006` | This document provides the partition and tombstone shapes it needs |
| Warehouse dimensional model | `DA-007` | OLTP here; OLAP there |
| Code list content | `DA-009` | This document declares the FK; `DA-009` governs the values |
| Per-module model design | `AR-003` SDD | An SDD applies this schema |
| Migration transformation logic | `MG-003` | Targets this schema |
| Physical infrastructure sizing | `PE-006` | This document states the volumetric drivers |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Odoo developers** | §4–§7 are the rules every model obeys; §11 is how they map to the ORM |
| **DBAs / platform engineers** | §8 indexes, §9 partitioning, §12 migration shape |
| `DA-002` author | The structural half of every dictionary entry |
| Migration team | §13 — every `DM-*` workbook currently targets assumed structure |
| DPO / `SC-007` | §10 residency split |
| QA | Constraints and invariants are directly testable |

---

## 2. Basis, Method and Measurement

### 2.1 Standards conformance

| Standard | Version | Conformance | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 11179-1:2023** | Edition 4, January 2023 | §4 naming follows the object-class / property / representation-term structure; registry metadata carried per table | **Departure:** the full MDR metamodel (Parts 3, 31, 33) is not instantiated. `DA-002` is the registry; this document is the schema. Instantiating an MDR for 5,301 data elements is `DA-002`'s decision, not a schema concern |
| **DAMA-DMBOK 2.0** | 2nd ed. with the 2024 maintenance revision | Data-architecture and data-modelling knowledge areas | **DMBOK 3.0 is in development and not released** (verified 2026-08-18); citing it would be citing an unpublished work |
| **Third normal form** | — | §5 — the transactional model is 3NF | **Deliberate denormalisation is declared, never incidental** — §5.3 lists all seven instances with their reason |
| **PostgreSQL 16** | Declarative partitioning | §9 | 16 is Odoo 19's tested pairing. **PostgreSQL 18 was released 25 September 2025 and is supported to 14 November 2030**; the move is reviewed at the Odoo upgrade gate (`AR-013` VC-03) |
| **Odoo 19 ORM** | 19.0 | §11 three-tier mapping | The ORM constrains the schema; §11.3 lists the seven places it does and what we do about each |
| ISO/IEC/IEEE 42010:2022 | 2022 | Information viewpoint; `AR-001` §6.3 kernel | Physical half of `AR-008`'s logical model |

### 2.2 Measured schema population

Counted from the filesystem at **2026-08-18 14:30 (+06)** per `PG-03` / `RG-06`. Commands in §15.

| Measure | Count |
|---|---:|
| Entity rows declared in module §10.1 tables | **1,370** |
| **Distinct table names** | **1,335** |
| Table names declared by more than one module | **34** — adjudicated in `AR-008` §7 |
| **Declared key attributes** (comma-separated across all rows) | **11,622** |
| **Distinct field names** | **5,301** |
| Field names appearing in exactly one entity | **4,020** (76%) |
| Field names appearing in ≥ 100 entities | **5** |
| Entities declaring a `state` field | **348** |
| Entities catalogued in `05-02` | **225** |

### 2.3 The finding that changes the scope of this document

> **`PGD-A5-01` — the entity catalogue is stale by roughly six times, and `DA-001` is the document
> that pays for it.**
>
> `05-02` covers **225 entities across 30 modules — about 17%** of the declared model. Sizing `DA-001`
> from `05-02` under-scopes it by ~83%. This document is scoped to the counted **1,335 tables**.
>
> Raised in `AR-008` §2.3 as `PGD-A3-13` and **restated here because this is where the cost lands.**

### 2.4 The finding that changes what this document must *assert* rather than derive

Module §10.1 tables declare "Key Attributes" — a summary of notable columns. Across 1,370 rows:

| Mandatory column | Rule requiring it | Declared occurrences | Coverage |
|---|---|---:|---:|
| `company_id` | **DM-03, AS-03** — every transactional model | **12** | **0.9%** |
| `operating_unit_id` | **DM-03, AS-03** | **18** | **1.3%** |
| `zone_id` | DM-03, where relevant | 9 | — |
| `cost_center_id` | DM-03, where relevant | 13 | — |
| `business_line_id` | DM-03, where relevant | 17 | — |
| `currency_id` | **AS-10, DM-07** — with every `Monetary` | **8** | — |
| `create_uid` / `write_date` | DM-05 — all models | **0** | **0%** |
| `active` | DM-06 — soft delete | 54 | — |

> **Read this correctly.** The §10.1 "Key Attributes" column is a **summary, not a column list**;
> authors omitted boilerplate, which is reasonable in a specification. **This is not evidence that the
> columns are absent from the intended design.**
>
> **It is evidence that `DA-001` cannot derive them and must assert them.** §3's standard column
> contract is therefore *normative and inherited*, not a per-table declaration — and `AR-012` `FF-21`
> is what makes it true in code rather than in this document.

**One measured item is a genuine defect, not an omission:**

| Observation | Why it is a defect |
|---|---|
| **`currency` (bare) declared 54 times; `currency_id` 8 times** | `AS-10` / `DM-07` require `Monetary` with an explicit `currency_id` **foreign key**, never a bare text or float. A field *named* `currency` is a named design choice, not omitted boilerplate. §4.4 rules it and `AR-012` `FF-22` enforces it |

Raised as **`PGD-A5-02`**.

### 2.5 Source material

| Source | Contribution |
|---|---|
| All 67 module specifications §10.1, §10.2 | **The measurement** — 1,335 tables, 5,301 fields |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` | DM-01…DM-15; §8 ERDs; §11 index and partition design; §10 classification |
| `../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md` | 22 aggregates, 54 invariants, the 34 multi-owned rulings |
| `../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` §6.3, §8.3 | Shared kernel; split-residency topology; trust zones |
| `../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` §4 | Naming, model and field conventions this document realises physically |
| `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.3 | Store assignment and sizing drivers |
| `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §3, §6.4, §8 | NFR-053/054/060 volumetrics; NFR-086 residency; DI-01…DI-08 |
| `../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md` | Code format standard `CF-01`…`CF-04` |

---

## 3. The Standard Column Contract

**Every table inherits this contract.** A module specification that does not list these columns still
gets them; a module that omits one fails `AR-012` `FF-21`.

### 3.1 Tier 1 — universal (every table without exception)

| Column | Type | Null | Purpose | Rule |
|---|---|:--:|---|---|
| `id` | `bigint GENERATED ALWAYS AS IDENTITY` | ✘ | Surrogate primary key | §4.5 |
| `create_uid` | `int → res_users` | ✘ | Who created it | DM-05 |
| `create_date` | `timestamp` (UTC) | ✘ | When | DM-05, AS-11 |
| `write_uid` | `int → res_users` | ✘ | Who last changed it | DM-05 |
| `write_date` | `timestamp` (UTC) | ✘ | When | DM-05 |

*Odoo supplies all five automatically. They are stated because `DA-002` must document them and because
migration and audit both depend on them existing.*

### 3.2 Tier 2 — every business table

| Column | Type | Null | Purpose | Rule |
|---|---|:--:|---|---|
| `active` | `boolean DEFAULT true` | ✘ | **Soft delete. Business records are archived, never hard-deleted** | DM-06, DI-08 |
| `company_id` | `int → res_company` | ✘ | Legal entity | **DM-03, AS-03** |
| `operating_unit_id` | `int → operating_unit` | ✘ | Branch / operating unit — **the multi-branch isolation mechanism** | **DM-03, AS-03**, tier T2 |

### 3.3 Tier 3 — every transactional table

Applied where the row records a business event or a lifecycle object, as opposed to configuration or
reference data.

| Column | Type | Null | Purpose | Rule |
|---|---|:--:|---|---|
| `zone_id` | `int → fix_zone` | ✔ | Dispatch / territory dimension | DM-03 |
| `cost_center_id` | `int → fix_cost_center` | ✔ | Finance reporting dimension | DM-03 |
| `business_line_id` | `int → fix_business_line` | ✘ | **Revenue-stream attribution across 14 streams** | DM-03 |

### 3.4 Tier 4 — conditional, by column class

| Condition | Columns |
|---|---|
| Table holds money | `currency_id int → res_currency NOT NULL` alongside **every** `numeric(16,2)` amount (§4.4) |
| Table has a lifecycle | `state varchar(40) NOT NULL` + `state_changed_at timestamp` (§4.6). **348 tables declare one** |
| Table is effective-dated | `valid_from date NOT NULL`, `valid_to date NULL` (§4.7) |
| Table is versioned | `version int NOT NULL DEFAULT 1` |
| Table holds a residency-classified value | **The value is not held. A `resident_key uuid` is held instead** (§10) |
| Table is a kernel extension | `party_id` / `catalogue_item_id` / `document_id` FK to the kernel owner (`AR-001` §6.3) |
| Table is a migration target | `legacy_source varchar(40)`, `legacy_id varchar(80)` (§4.5) |

### 3.5 Why this is a contract and not a template

> **QAS-03 in `AR-001` §10 rests entirely on §3.2 and §3.3.** *"Every transactional record carries the
> full dimensional context from Wave 1, even while a single Bangladesh entity operates."*
>
> The alternative is retrofitting a dimension onto live transactional data across **1,335 tables**.
> That is the class of change that does not get funded, so it is paid for on day one, on tables where
> `company_id` will hold the value `1` for at least nine waves.
>
> Twelve of 1,370 specifications say so. **This contract is why the other 1,358 get it anyway.**

---

## 4. Naming, Types and Domains

### 4.1 Naming (realising `AR-007` §4 physically)

| # | Rule | Example |
|---|---|---|
| **N-01** | Table: `fix_<domain>_<entity>`, snake_case, singular | `fix_service_order` |
| **N-02** | Odoo model: `fix.<domain>.<entity>` — the table name is **derived, never hand-set** | `fix.service.order` |
| **N-03** | Column: snake_case; `_id` many-to-one; `_ids` one/many-to-many | `partner_id`, `work_order_ids` |
| **N-04** | Boolean reads as an assertion | `is_warranty`, not `warranty` |
| **N-05** | Timestamp columns end `_at`; date columns end `_date` or `_on` | `occurred_at`, `promised_date` |
| **N-06** | Quantity columns carry their unit where not obvious | `duration_min`, `weight_kg` |
| **N-07** | ISO/IEC 11179-1:2023 object-class / property / representation form where a name is ambiguous | `service_order_total_amount`, not `total` |
| **N-08** | **No abbreviation that is not registered in `RR-001`** | `qty` only if registered |
| **N-09** | Index `ix_`; unique `uq_`; check `ck_`; foreign key `fk_`; exclusion `ex_` | `ix_fix_service_order_ou_state_created` |
| **N-10** | Partition child: `<parent>_<key>` | `fix_service_order_2027` |

> **N-07 exists because of the singleton measurement.** 4,020 of 5,301 field names (76%) appear in
> exactly one entity. Some of that is genuine domain specificity. Some is 67 authors independently
> naming the same concept — and `DA-002` §6 is where that is reconciled.

### 4.2 Type domains

| Domain | PostgreSQL type | Rule |
|---|---|---|
| Identifier (surrogate) | `bigint identity` | §4.5 |
| Identifier (business code) | `varchar(n)` with a check constraint | `MD-001` `CF-01`…`CF-04`; ASCII only, no Bengali in a code |
| Short text | `varchar(n)` with a stated `n` | **An unbounded `text` for a bounded concept is a defect** |
| Long text / narrative | `text` | Notes, descriptions, complaint text |
| **Money** | `numeric(16,2)` + `currency_id` | §4.4 — **never `float`, never `double precision`** |
| Quantity | `numeric(16,4)` | Stock, hours; 4 dp because parts fractionalise |
| Percentage | `numeric(7,4)` | Stored as a fraction, presented as % |
| Boolean | `boolean` | Never `char(1)`; never nullable without a stated three-state meaning |
| **Timestamp** | `timestamp` (no time zone), **UTC** | AS-11, DM-08 — presented `Asia/Dhaka` |
| Date | `date` | |
| Duration | `integer`, **minutes** | DM-08 |
| Enumeration | `varchar` + FK or check | §4.6, `DA-009` |
| JSON payload | `jsonb` | §4.8 — bounded uses only |
| Binary | **Never in a row.** Object-storage reference | Claim-check; `AR-009` P-05 |
| Geospatial | `numeric(9,6)` lat / `numeric(9,6)` lng | Not PostGIS — see §4.9 |

### 4.3 Text, encoding and Bengali

| # | Rule |
|---|---|
| **T-01** | Database encoding **UTF-8** throughout (DM-09) |
| **T-02** | **Collation `bn-BD-x-icu`** on every column that holds Bengali and is sorted or compared |
| **T-03** | A bilingual concept is **two columns** (`name_en`, `name_bn`), never one column with a language flag — both are needed simultaneously on a bilingual document |
| **T-04** | Bengali columns are sized **1.4×** their English counterpart. Bengali runs 15–30% longer; a `varchar(60)` English label needs `varchar(90)` in Bengali |
| **T-05** | Free-text search uses PostgreSQL FTS with a GIN index (ADR-010); the `to_tsvector` configuration is declared per column |
| **T-06** | **A state key is never displayed** (`MD-027` `STA-04`). The label is a `DA-009` lookup, not a column value |

> **T-04 is the rule most likely to be discovered rather than designed.** A Mushak 6.3 invoice with a
> truncated Bengali party name is a compliance defect, and it will be found at print, in production.

### 4.4 Money — the rule and the measured defect

| # | Rule |
|---|---|
| **M-01** | Every monetary column is `numeric(16,2)` and is accompanied by `currency_id int → res_currency NOT NULL` in the **same table** |
| **M-02** | **No `float`, `real` or `double precision` in any money path** (AS-10, DI-01) |
| **M-03** | Rounding is applied **once**, at a point declared in the module's SDD (`AR-003` DP-08) |
| **M-04** | A multi-currency table also carries `company_currency_amount` and `exchange_rate` where a converted value is persisted |
| **M-05** | **A bare `currency` text column is prohibited.** It cannot enforce referential integrity against `res_currency`, cannot carry rounding precision, and cannot be joined for revaluation |

> **`PGD-A5-02`.** The specifications declare **`currency` (bare) 54 times and `currency_id` 8 times**.
> `M-05` rules it; `AR-012` `FF-22` blocks it. This is a **correction to 54 specification rows**, not
> an omission — and it is cheap now, because no table exists.

### 4.5 Keys

| Kind | Rule |
|---|---|
| **Surrogate** | `id bigint identity` on every table. **Never a natural key as PK** — natural keys change, and an FK graph built on one propagates the change |
| **Natural** | Declared per table in `DA-002`, enforced by a **unique constraint**, never by convention |
| **Business code** | `MD-001` `CF-01`…`CF-04` — `<PREFIX>-<SEQ>`, ASCII, zero-padded, **no embedded meaning**, never reused |
| **Sequence** | Branch- and business-line-aware masks per `MD-040` (DM-11). The mask is configuration, not code |
| **Legacy key** | **`legacy_source` + `legacy_id` on every migrated table** — `MIG-05` requires legacy identifiers preserved on every migrated record |
| **Resident key** | `uuid` — the only permitted reference to a residency-classified value (§10) |

> **The legacy-key pair is a schema obligation, not a migration one.** If the columns do not exist in
> the target schema, `MIG-05` cannot be satisfied and every migrated record loses its provenance. It is
> listed here because `DM-004`…`DM-010` assume it and no schema currently provides it.

### 4.6 State columns

**348 tables declare a `state`.** Each is a state machine under `AR-003` DP-01 and a code list under
`DA-009`.

| # | Rule |
|---|---|
| **S-01** | `state varchar(40) NOT NULL` with a `DEFAULT` naming the initial state |
| **S-02** | The permitted set is **declared in `MD-027`**, keyed `model_name` + `state_key`, and enforced by a check constraint **generated** from the register |
| **S-03** | `state_changed_at timestamp NOT NULL` accompanies it — every state machine needs its own dwell-time measurement |
| **S-04** | The transition map lives in **one place** on the model (AS-06); the database enforces the *set*, the model enforces the *transitions* |
| **S-05** | A partial index on `(state)` exists only where a query filters on a **minority** state (§8.3) |

### 4.7 Effective dating

| # | Rule |
|---|---|
| **E-01** | An effective-dated table carries `valid_from date NOT NULL` and `valid_to date NULL` (null = open) |
| **E-02** | **An exclusion constraint prevents overlapping periods** for the same natural key — `EXCLUDE USING gist (natural_key WITH =, daterange(valid_from, valid_to) WITH &&)` |
| **E-03** | A lookup "as at" a date is a range containment test, never `ORDER BY valid_from DESC LIMIT 1` |
| **E-04** | Price books, rate cards, tax rates, payroll elements, competency requirements and SLA bands are all effective-dated. **Retrospective correction of a posted transaction uses the rate that applied then** |

> **E-02 is the constraint that prevents the most expensive class of finance defect.** Two overlapping
> tax-rate rows produce a Mushak invoice whose VAT depends on row order.

### 4.8 `jsonb` — bounded uses only

| Permitted | Prohibited |
|---|---|
| Diagnostic tree answers (`answers_json`) — shape varies by template | Anything queried in a `WHERE` on a hot path |
| Checklist item sets (`items_json`) | Anything with referential integrity to another table |
| Event payloads in the outbox | Anything a report aggregates |
| External API raw responses, for audit | **Anything that should have been a column** |

| # | Rule |
|---|---|
| **J-01** | Every `jsonb` column has a **declared JSON Schema** in `DA-002` and a validation trigger or model constraint |
| **J-02** | A `jsonb` field that acquires a query is **promoted to a column** at the next migration |
| **J-03** | `jsonb` never holds a residency-classified value, personal data beyond the minimum, or money |

### 4.9 Geospatial — why not PostGIS

| Option | Assessment |
|---|---|
| PostGIS | **Not adopted.** It is an extension with its own upgrade cycle, and the estate's spatial need is point storage, distance and geofence containment |
| **`numeric(9,6)` lat/lng pairs + application-side geometry** | **Chosen.** Routing is VROOM/OSRM (ADR-005), which takes coordinates; geofence containment is a bounded polygon test in `cd_geofence` |
| **Revisit if** | Territory optimisation or spatial joins over polygons enter scope — then PostGIS, as a declared ADR |

---

## 5. Normalisation

### 5.1 Position

**The transactional model is third normal form.** Every non-key attribute depends on the key, the
whole key and nothing but the key.

### 5.2 Why 3NF and not a star

An ERP's OLTP model exists to make **writes correct**, not reads fast. Denormalising for reporting
convenience puts the same fact in two places, and the two places diverge under concurrent update.
**Reporting is `DA-007`'s problem and it is solved in the warehouse** (`AR-001` LB-06).

### 5.3 Where 3NF is deliberately relaxed

**Seven declared denormalisations.** Each is a decision with a reason and a maintenance rule.
An eighth requires an ADR.

| # | Denormalisation | Reason | Maintenance |
|---|---|---|---|
| **DN-01** | `fix_service_order.total_cost` / `.total_price` stored, not computed | The branch board loads 500 rows; recomputing from lines is 500 sub-queries (NFR-033: ≤ 1 s) | Stored computed field with complete `depends`; `AR-012` `FF-18` |
| **DN-02** | `fix_service_order.promised_date` stored and **frozen at `received`** | Customer-visible and often contractual. A policy edit must not silently re-baseline live orders (`AR-003` §6.10) | Written once; never recomputed |
| **DN-03** | `fix_asset.current_owner_party_id` alongside the `fix_asset_ownership` history | Customer 360 and dispatch both need current ownership on every read | Maintained by the ownership state machine, single write path |
| **DN-04** | `fix_stock_quant` quantity aggregates | Availability lookup is the highest-frequency read in the estate | Odoo core behaviour; not ours to change |
| **DN-05** | `fix_party.display_name` composed | Every screen and document renders it | Stored computed |
| **DN-06** | `fix_sla_clock.breach_at` precomputed | Escalation scanning is a partial-index range scan, not a per-row calculation (§8.2) | Recomputed on pause/resume |
| **DN-07** | `fix_invoice_line.tax_amount` stored | **Statutory.** The Mushak 6.3 must show the tax as calculated at issue, not as recalculated later | Immutable after posting |

> **DN-07 is not an optimisation.** Recomputing a posted tax amount from a current rate would produce
> an invoice that disagrees with the one the customer holds and the one the NBR received.

### 5.4 What must never be denormalised

| # | Rule |
|---|---|
| **ND-01** | **Never denormalise a monetary balance.** Two places holding a balance produce two balances (`DM-011` `DQ-17` says the same about merges) |
| **ND-02** | Never denormalise a residency-classified value — that is a residency breach, not a performance choice (§10) |
| **ND-03** | Never denormalise consent. Consent is read from `fix_consent_record` at the moment of processing |
| **ND-04** | Never denormalise a permission or role. Authorisation is evaluated, never cached in a business row (`AR-001` LB-05) |

---

## 6. Constraints and Referential Integrity

### 6.1 Constraint policy

| Kind | Rule |
|---|---|
| **Primary key** | `id` on every table, no exceptions |
| **Not null** | **Default position.** A nullable column must have a stated meaning for null in `DA-002` |
| **Unique** | Every natural key. Partial unique where the key applies conditionally — `UNIQUE (serial_no) WHERE serial_no IS NOT NULL` |
| **Check** | Enumerations, ranges, non-negative money, cross-column consistency |
| **Exclusion** | Overlapping effective-dated periods (§4.7 E-02); double-booked rental assets (invariant I-46) |
| **Foreign key** | **Enforced at the database level, not only in application code** (DI-03) |

### 6.2 The `ondelete` matrix

`AR-007` N-16 requires `ondelete` declared explicitly on every many-to-one. **Odoo's default is
`set null`**, which is wrong for most business references.

| Relationship class | Policy | Reason |
|---|---|---|
| Transaction → master (order → party, order → asset) | **`RESTRICT`** | An order outlives a party-record merge. Silently orphaning it destroys history |
| Child → parent within an aggregate (line → header) | **`CASCADE`** | The line has no meaning without the header, and the aggregate is one transaction boundary (`AR-008` AG-01) |
| Transaction → configuration (order → SLA policy) | **`RESTRICT`** | Configuration is archived, never deleted (DM-06) |
| Optional annotation (order → campaign) | **`SET NULL`** | The annotation may legitimately disappear |
| Audit / log → subject | **`RESTRICT`**, or no FK where the subject may be disposed | An audit entry must survive its subject's disposal (`RS-08`, `RC-22`) |
| Kernel reference (anything → `res_partner`) | **`RESTRICT`** | Kernel records are never deleted |

> **The audit row is the subtle one.** `RC-22` retains access logs for 5 years; `RC-01` may dispose of
> the service order sooner. A `CASCADE` there would delete the evidence of lawful access along with the
> record it evidences. Where the retention of the log exceeds the retention of its subject, the FK is
> **not declared** and the reference is a soft pointer, documented in `DA-002`.

### 6.3 Referential integrity across the module boundary

`AR-001` LB-01 forbids a module reading another module's tables. **A foreign key is not a read.**

| # | Rule |
|---|---|
| **RI-01** | An FK to another module's table is **permitted and required** where the relationship is real. LB-01 governs *queries*, not *constraints* |
| **RI-02** | The FK is declared by the **referencing** module; the referenced module is notified via the `AR-006` dependency declaration |
| **RI-03** | **Data is still read through the owner's API or an event projection** — the FK guarantees the row exists; it does not license a join |
| **RI-04** | A cross-module join in a report is `DA-007`'s warehouse, not the OLTP store |

### 6.4 Referential integrity across the residency boundary

**There is none, and there cannot be.** Two physical databases (`AR-001` §8.3 Z3 and Z4) cannot share
a foreign key.

| # | Rule |
|---|---|
| **RR-01** | The regional row holds `resident_key uuid`; the resident row holds the same `uuid` as its natural key |
| **RR-02** | **Integrity is enforced by the residency service (CD-233), not by the database.** Every write of a resident value goes through it; it maintains both sides |
| **RR-03** | A **nightly reconciliation** (CD-241) detects orphans in both directions and alerts. A regional row whose `resident_key` resolves to nothing is a defect, and so is the reverse |
| **RR-04** | An erasure removes both sides in one saga (CD-248), or neither (`DA-006` §7) |

> **RR-02/RR-03 are the honest cost of the split-residency design.** A guarantee the database gave for
> free becomes a service plus a reconciliation job plus an alert. That cost is stated here rather than
> discovered when the first orphan appears — and §10.4 records that the *statutory basis* for paying it
> is now in question.

---

## 7. Volumetrics

The sizing drivers, because index and partition design follow from them.

| Table class | Driver | Volume | Source |
|---|---|---|---|
| `fix_service_order` | 5 M service orders/year by year 5 | **~25 M rows at year 5** | NFR-053 |
| `fix_work_order` | ~1.6 per service order | ~40 M | Derived |
| `fix_asset` | 5 M assets | **5 M** | NFR-054 |
| `fix_party` | 250,000+ customers/month | ~3 M at year 5 | `00-01` |
| `fix_location_ping` | 400 technicians × 30 s | **800/min ≈ 420 M/year** | NFR-056 |
| `fix_telemetry_point` | 50,000 points/min | **~26 bn/year** | NFR-055 |
| `account_move_line` | Every posting | ~200 M at year 5 | Derived |
| `fix_notification_log` | Every send | ~500 M/year | Derived |
| `fix_domain_event` | **988 event types**, every state change | High; pruned at 7 days (`AR-009` §5.3) | `AR-009` |
| Object storage | Documents, evidence | **50 TB, sub-10-second retrieval** | NFR-060 |

---

## 8. Index Design

### 8.1 Policy

| # | Rule |
|---|---|
| **IX-01** | **Every index exists for a named query.** An index with no query is write cost with no read benefit |
| **IX-02** | Every FK column is indexed — PostgreSQL does not do this automatically, and an unindexed FK makes the parent's delete-check a sequential scan |
| **IX-03** | Composite index column order follows **equality → range → sort** |
| **IX-04** | **Partial indexes for minority predicates** — `WHERE NOT breached` is far smaller than the table |
| **IX-05** | GIN for full-text and `jsonb` containment |
| **IX-06** | Index bloat and unused indexes are reviewed at every wave gate (`AR-012` §8) |

### 8.2 The core index set

Carried forward from `05-02` §11 and extended with the query each serves.

| Table | Index | Query it serves |
|---|---|---|
| `fix_service_order` | `(operating_unit_id, state, create_date DESC)` | Branch operations board — NFR-033 |
| `fix_service_order` | `(partner_id, create_date DESC)` | Customer 360 history — NFR-031 ≤ 2 s |
| `fix_service_order` | `(asset_id, create_date DESC)` | Device history and **rework detection** (`BRU-SRM-06`, 30-day window) |
| `fix_service_order` | GIN on `name`, complaint text | Free-text search **including Bengali** — NFR-035 ≤ 600 ms |
| `fix_work_order` | `(technician_id, scheduled_start)` | Technician schedule; dispatch board |
| `fix_sla_clock` | `(breach_at) WHERE NOT breached` | **Escalation scanning** — the partial index that makes it a range scan |
| `fix_asset` | `(serial_no)`, `(imei)`, `(asset_tag)` **unique partial** | Identity resolution; `DM-011` pass-1 deterministic matching |
| `fix_warranty_claim` | `(brand_id, state, submitted_date)` | Claim pipeline and ageing — P08 |
| `fix_stock_quant` | `(product_id, location_id)` | Availability lookup — highest-frequency read |
| `fix_entitlement` | `(contract_id, asset_id)` | **Coverage validation at intake** — gates `BRU-SRM-03` |
| `fix_commission_entry` | `(seller_id, period, state)` | Payout runs |
| `fix_domain_event` | `(published, occurred_at)` | **Outbox drain** — `AR-009` §5.2 |
| `fix_audit_entry` | `(model, res_id, occurred_at DESC)` | Audit lookup |
| `fix_party` | `(primary_mobile)` partial unique | OTP, notification, `DM-011` matching |

### 8.3 Indexes this document adds

Derived from queries the measured model implies and `05-02` §11 does not cover.

| Table | Index | Query |
|---|---|---|
| Tables with `state` (348) | `(operating_unit_id, state)` **where the state is actually queried** | Console list views. **Not created blindly on all 348** — IX-01 |
| `fix_consent_record` | `(party_id, purpose_code, valid_from DESC)` | **Lawful-basis check at the moment of processing** (ND-03) |
| Effective-dated tables | `gist (natural_key, daterange(valid_from, valid_to))` | The E-02 exclusion constraint provides it |
| `fix_document` | `(retention_class, disposal_due_date) WHERE NOT disposed` | **`DA-006` disposal batch selection** across 1,335 tables |
| Residency-referencing tables | `(resident_key)` | RR-03 reconciliation, both directions |
| `fix_party` | `(golden_record_id) WHERE golden_record_id IS NOT NULL` | `DM-011` `DQ-19` merge-loser resolution |

---

## 9. Partitioning

> **`02-05` §8 asserts PostgreSQL 16 partitioning and names no partition key.** `PGD-000`'s `DA-001`
> row records that omission. This section discharges it.

### 9.1 The partitioned tables and their keys

| Table | Strategy | **Partition key** | Interval | From | Retention link |
|---|---|---|---|---|---|
| `fix_service_order` | RANGE | **`create_date`** | Yearly | **Year 3** | `RC-01` — warranty + limitation |
| `fix_work_order` | RANGE | **`create_date`** | Yearly | Year 3 | With parent |
| `account_move` | RANGE | **`date`** (fiscal period) | Yearly | Year 2 | `RC-03` — 7 years |
| `account_move_line` | RANGE | **`date`** | Yearly | Year 2 | With parent |
| `fix_notification_log` | RANGE | **`create_date`** | **Monthly** | **W1** | `RC-04` — 13 months → `DM-2` drop |
| `fix_api_usage_log` | RANGE | **`create_date`** | Monthly | W1 | Per retention |
| `fix_audit_entry` | RANGE | **`occurred_at`** | Yearly | W1 | `RC-22` — 5 years |
| `fix_domain_event` | RANGE | **`occurred_at`** | **Weekly** | W1 | 7-day prune + archive |
| `fix_call_record` | RANGE | **`create_date`** | Monthly | W4 | `RC-15` — 6 months |
| `fix_location_ping` | **TimescaleDB hypertable** | **`time`**, partition by `technician_id` | Auto chunk | W2 | `RC-24` — 90 d full, then aggregate |
| `fix_telemetry_point` | **TimescaleDB hypertable** | **`time`**, partition by `asset_id` | Auto chunk | W8 | Compress after 7 d |
| `fix_metric_series` | **TimescaleDB hypertable** | **`time`** | Auto chunk | W5 | Compress after 7 d |

### 9.2 Why these and not others

| # | Rule |
|---|---|
| **P-01** | **A table is partitioned when its retention is time-based and its volume makes a `DELETE` impractical.** Partition drop (`DM-2`) is `DA-006`'s cheapest deletion method |
| **P-02** | A table is partitioned when queries are **time-bounded**, so the planner can prune |
| **P-03** | **`fix_service_order` is deferred to year 3** deliberately. Partitioning from W1 adds planning overhead and operational complexity for a table holding thousands of rows in W1. The `create_date` key is fixed **now** so the change is a re-partition, not a redesign |
| **P-04** | **A partition key must be immutable.** `create_date` never changes; `state` would move rows between partitions on every transition, which is why no table is partitioned by state |
| **P-05** | Partition maintenance (create-ahead, detach, drop) is **automated with alerting**. A missing future partition is an insert failure at midnight on 1 January |

> **P-04 is the trap.** `fix_service_order` looks partitionable by `state` — most queries filter on it,
> and closed orders vastly outnumber open ones. But a partition key must not change, and an order's
> whole purpose is to change state. Partition by `create_date`; index by `(operating_unit_id, state, …)`.

### 9.3 The TimescaleDB boundary

| # | Rule |
|---|---|
| **TS-01** | GPS, telemetry and metric series are **hypertables, not tables** (ADR-007) |
| **TS-02** | **Only Apache-2.0 licensed features are used** — a TSL dependency converts a $0 component into a licensed one mid-programme (`AR-013` §6) |
| **TS-03** | Continuous aggregates provide minute/hour/day downsampled tiers **surviving raw-data retention** — this is how `RC-24` keeps analytic value after 90 days without keeping personal location history |
| **TS-04** | Compression after **7 days** |
| **TS-05** | **No foreign key from a hypertable to an OLTP table.** The join is by id at query time; FK enforcement at 420 M rows/year is not viable |

---

## 10. The Residency-Split Physical Model

### 10.1 The two stores

| Store | Zone | Contents |
|---|---|---|
| **Regional primary** | Z3 | 1,335 tables less the classified values; TimescaleDB; ClickHouse; Redis; MinIO |
| **Bangladesh-resident** | **Z4** | **Only** residency-classified values, keyed by `resident_key`, separate key material |

### 10.2 The resident-key pattern

```
  REGIONAL (Z3)                              RESIDENT (Z4)
  fix_identity_document                      resident_identity_value
  ├ id               bigint                  ├ resident_key      uuid  PK
  ├ party_id         → fix_party             ├ value_ciphertext  bytea
  ├ document_type    varchar                 ├ key_ref           varchar
  ├ issuing_country  varchar                 ├ created_at        timestamp
  ├ verified_on      date                    └ access_log_id     bigint
  ├ resident_key     uuid  ─────────────────────────┘
  └ (NO nid_number, NO passport_number)      Reached ONLY via CD-233
```

| # | Rule |
|---|---|
| **RS-01** | **The classified value is never a column in Z3** — not encrypted, not hashed, not masked, not in a comment |
| **RS-02** | The regional table carries `resident_key uuid` and non-classified metadata only |
| **RS-03** | **Read and write go through the residency service (CD-233).** No direct query, no migration script, no backfill (`AR-001` LB-08) |
| **RS-04** | The classified value never enters an index, a log, a search corpus, a `jsonb` payload, an event payload, an LLM prompt, a report or a non-production environment |
| **RS-05** | Every read is logged with actor, purpose and timestamp; human reads require step-up (tier T5) |
| **RS-06** | Integrity is by reconciliation (RR-03), not by FK |

### 10.3 The currently classified field set

From `05-06` §6.4, mapped to the measured schema:

| Field | Regional table | Owner |
|---|---|---|
| National ID number | `fix_identity_document` | M33 |
| Passport number | `fix_identity_document` | M33 |
| TIN | `fix_party`, `hr_employee` | M33, M21 |
| Biometric attendance template | `fix_attendance_record` | M55 |
| Recovered customer data and its index | `fix_recovered_inventory` | M06 |
| Marketplace seller KYC documents | `fix_mp_seller_document` | M12 |
| Criminal-record checks | `fix_mp_seller_document` | M12 |

### 10.4 A verification finding that changes the basis of this design

> **`PGD-A5-03` — the statutory requirement may be a synchronised in-country copy, not exclusive
> residency. Verified against public sources 2026-08-18; requires legal confirmation.**
>
> The estate designs to an **exclusive residency** model: classified values live only in Z4 and are
> never duplicated regionally (`05-06` NFR-086, `AR-001` §8.3, ADR-018).
>
> Public reporting on **Personal Data Protection (Amendment) Ordinance, 2026 (Ordinance No. 23 of
> 2026), promulgated 5 February 2026** describes a materially different obligation:
>
> | Dimension | Estate's design | Reported statutory position |
> |---|---|---|
> | Mechanism | Value exists **only** in Bangladesh | **At least one synchronised real-time copy** within Bangladesh — a mirror |
> | Scope | Field types: NID, passport, TIN, biometric, recovered data, KYC | **"Restricted personal data"** and Critical Information Infrastructure per the Cyber Security Ordinance 2025 |
> | Definition | By field | **By impact** — national security, public order, defence, critical infrastructure, fundamental rights |
> | Direction of travel | — | The February 2026 amendment **narrowed** the original November 2025 scope |
>
> **Why this matters to `DA-001` specifically.** A mirror and an exclusion are different schemas. A
> mirror permits the value to sit in the regional table with a synchronised in-country replica —
> **no `resident_key`, no cross-store join, no reconciliation job, no FK loss (§6.4).** An exclusion
> requires everything in §10.2. **The estate is currently paying the higher price.**
>
> **What does not change.** `TR-02`'s position holds: **build the field-level classification mechanism
> in Wave 1 regardless**, because classification is data and a change of opinion is a
> **reclassification, not a redesign**. The residency service is still needed for access logging and
> step-up under tier T5.
>
> **What must change.** `DEP-31` / `D-13`'s question. It currently asks *"does the Authority accept a
> resident-key join?"* It should ask: **(a)** does the obligation attach to a mirror or an exclusion;
> **(b)** does 1000FiX's data fall within "restricted personal data" or CII; **(c)** is the field-type
> classification in `05-06` §6.4 the right basis, or must it be impact-based?
>
> **Evidentiary standing.** Secondary sources, not the statute. Recorded as a **verification finding
> requiring legal confirmation**, not as established fact. `RR-005` (Standards & Regulatory Currency
> Register) is the durable control.

---

## 11. Odoo ORM Mapping

### 11.1 The three tiers (DM-02)

| Tier | Mechanism | Schema effect |
|---|---|---|
| **Odoo core** | `res_partner`, `product_template`, `stock_move`, `account_move`, `hr_employee` | We do not own the DDL. Extension adds columns |
| **OCA** | `operating_unit`, `fieldservice_*`, `dms_*` | Same; **never forked** (AS-05) |
| **Custom `cd_*`** | New `fix_*` tables | We own the DDL entirely |

### 11.2 Extension mechanics and their DDL consequence

| Odoo mechanism | DDL result | Use when |
|---|---|---|
| `_inherit = 'model'` | **Columns added to the existing table** | Extending in place — the default |
| `_name` + `_inherit` (prototype) | **A new table with copied definition** | A genuinely separate lifecycle. **Rare, and the most misused** (`AR-007` §5.2) |
| `_inherits` (delegation) | New table + FK to parent, transparently joined | A record that *is-a* another record with its own table |
| New model | New table | New concept |

### 11.3 Where the ORM constrains the schema, and what we do

| # | Constraint | Response |
|---|---|---|
| **O-01** | Odoo names tables from the model — `fix.service.order` → `fix_service_order` | Accepted. N-02 makes it a rule rather than an accident |
| **O-02** | Odoo's `ondelete` default is `set null` | **N-16 / §6.2 override it explicitly on every FK.** `AR-012` `FF-25` |
| **O-03** | Odoo does not natively create partitioned tables | Partitioning is applied by **migration script** (§12), and the model is unaware of it |
| **O-04** | Odoo's `Monetary` requires a `currency_field` | M-01 makes `currency_id` mandatory in the same table |
| **O-05** | Odoo stores datetimes naive UTC | Matches AS-11. No conversion in the database |
| **O-06** | `active` is Odoo's soft-delete convention | Matches DM-06 |
| **O-07** | Odoo's ORM will happily read any table | **LB-01 is enforced by CI (`FF-01`), not by the database** |

### 11.4 What the schema must not do to the ORM

| # | Rule |
|---|---|
| **OM-01** | No database trigger that changes business data. Odoo's ORM will not see it, and the record cache will be wrong |
| **OM-02** | No view presented as a model where writes are expected |
| **OM-03** | No stored procedure holding business logic (AS-09) |
| **OM-04** | Triggers are permitted **only** for: partition routing, `jsonb` schema validation, and audit-table inserts |

---

## 12. Migration Shape and the Schema-Change Contract

| # | Rule |
|---|---|
| **MG-01** | Migrations are **forward-only** (OPS-07) |
| **MG-02** | **A release adds a column before code uses it; removes one only after no code references it — two releases, never one** |
| **MG-03** | Every migration dry-runs against a **production-sized clone** |
| **MG-04** | A migration touching residency-classified data goes through CD-233 (RS-03) |
| **MG-05** | Adding a `NOT NULL` column to a populated table: add nullable → backfill in batches → set not-null. **Never in one statement** on a 25 M-row table |
| **MG-06** | An index on a large table is created **`CONCURRENTLY`** |
| **MG-07** | A partition must exist before the period it covers. Create-ahead is automated and alerted (P-05) |
| **MG-08** | Every migration is idempotent and restartable (`MG-003`) |

---

## 13. What This Document Unblocks — and What It Invalidates

| Consumer | Effect |
|---|---|
| `DA-002` Data Dictionary | The structural half of **5,301 field entries** |
| `AR-003` per-module SDDs | The information viewpoint per module |
| **`DM-004`…`DM-010` mapping workbooks** | **Seven workbooks currently map to assumed structure.** `AUDIT-011` records all 48 legacy sources unprofiled; this document gives the **target** side a definition |
| `MG-003` ETL design | Transformation targets |
| `SC-007` residency design | §10, and the §10.4 finding |
| `DA-006` retention | Partition and tombstone shapes |
| `DA-007` warehouse | Source grain |
| `PE-006` capacity | §7 volumetrics |

> **The invalidation is worth stating plainly.** `MIG-05` requires legacy identifiers on every migrated
> record; §4.5 adds `legacy_source` + `legacy_id` as a schema obligation. **No mapping workbook
> currently maps to those columns, because they did not exist.** Seven workbooks need a column added,
> which is cheap — and cheaper now than at cutover.

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is `05-02` reissued for 1,335 tables, or superseded by this document?** (`PGD-A5-01`) | Enterprise Architecture | **W1 — blocking** | Which document a developer reads |
| **Q-02** | **Is the residency obligation a mirror or an exclusion (`PGD-A5-03`)?** The §10.2 pattern, the §6.4 FK loss and the reconciliation job all follow from the answer | CFO / Legal / DPO — `DEP-31`, `D-13` | **Before the W1 schema is fixed** | §10; `SC-007`; `PE-001` |
| **Q-03** | Are the 54 `currency` → `currency_id` corrections accepted, and who executes them? (`PGD-A5-02`) | Chief Architect | W1 | 54 specification rows; `FF-22` |
| **Q-04** | `BE-005` does not exist, so no table can cite an issued CD identifier | CTO | **W0 — blocking** | Every module's DDL ownership |
| **Q-05** | Does the schema hold PostgreSQL 16 through the Odoo upgrade slot, or move to 17/18 at the same gate? | Solution Architect / `AR-013` VC-03 | W5 | One major upgrade or two |
| **Q-06** | Who owns `DA-001` between wave gates, given the Chief Data Officer post is unfilled? | CTO / `DA-003` | W1 | Schema change authority |

---

## 15. Verification Commands

```bash
cd 1000fix_ERP_Module/03_Modules

# Entity rows, tables, key attributes
for f in $(find . -name 'M[0-9]*.md'); do
  awk 'BEGIN{p=0} /^### 10\.1/{p=1;next} /^### 10\.2|^## 11\./{p=0} p' "$f" | grep -E '^\| `fix\.'
done > ent_rows.txt
wc -l < ent_rows.txt                                                  # -> 1370
awk -F'|' '{gsub(/[` ]/,"",$3); if($3!="") print $3}' ent_rows.txt | sort -u | wc -l   # -> 1335

# Distinct field names
awk -F'|' '{n=split($5,a,","); for(i=1;i<=n;i++){gsub(/^[ `]+|[ `]+$/,"",a[i]);
     if(a[i]!="") print a[i]}}' ent_rows.txt | sort > fld.txt
wc -l < fld.txt                                                       # -> 11622
sort -u fld.txt | wc -l                                               # -> 5301

# Mandatory dimensional column coverage
for c in company_id operating_unit_id currency_id create_uid; do
  printf "%-20s %d\n" "$c" "$(grep -cx "$c" fld.txt)"
done                                                                  # -> 12 / 18 / 8 / 0

# The money-column defect
printf "currency %d  currency_id %d\n" \
  "$(grep -cx currency fld.txt)" "$(grep -cx currency_id fld.txt)"    # -> 54 / 8

# State machines
grep -cx state fld.txt                                                # -> 348
```

---

## 16. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D1-01 | Scope basis | `05-02`'s 225 entities; **the measured 1,335** | **Measured** | Sizing from a 30-module catalogue under-scopes by 83% | ~6× the deliverable; `PGD-A5-01` |
| D-D1-02 | Standard columns | Per-table declaration; **inherited contract** | **Inherited (§3)** | 12 of 1,370 specifications declare `company_id`; a contract plus a CI gate is the only way it becomes true | `FF-21` enforces |
| D-D1-03 | Normal form | Star; **3NF with 7 declared exceptions** | **3NF** | OLTP exists to make writes correct; reads are `DA-007`'s | An 8th denormalisation needs an ADR |
| D-D1-04 | Money | Bare `currency` text; **`numeric(16,2)` + `currency_id` FK** | **FK pair** | Referential integrity, rounding precision, revaluation join | 54 specification corrections |
| D-D1-05 | Partition key for orders | `state`; **`create_date`** | **`create_date`** | A partition key must be immutable; state is the one thing that changes | Index by state instead |
| D-D1-06 | Geospatial | PostGIS; **numeric lat/lng** | **numeric** | Need is points, distance and containment; routing is VROOM/OSRM | Revisit on polygon joins |
| D-D1-07 | Cross-residency integrity | FK (impossible); **service + reconciliation** | **Service + nightly reconciliation** | Two databases cannot share an FK | An orphan class the DB used to prevent |
| D-D1-08 | Legacy keys | Migration-only; **schema obligation** | **Schema (§4.5)** | `MIG-05` is unsatisfiable if the columns do not exist | 7 workbooks gain a column |

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Scope is counted, not consulted, with a reproducible method | §2.2, §15 |
| AC-02 | Every table inherits a stated standard column contract | §3 |
| AC-03 | Every type domain is declared, including money, time, text and Bengali | §4.2–§4.4 |
| AC-04 | `ondelete` is declared per relationship class, not left to the ORM default | §6.2 |
| AC-05 | **Every partitioned table names its partition key** — the `02-05` §8 gap | §9.1 — 12 tables |
| AC-06 | Every index names the query it exists for | §8.2, §8.3 |
| AC-07 | Deliberate denormalisation is enumerated with a maintenance rule | §5.3 — 7 instances |
| AC-08 | The residency split is expressed physically, with its integrity cost stated | §10, §6.4 |
| AC-09 | The ORM's constraints on the schema are stated with a response each | §11.3 |
| AC-10 | Findings are raised where measurement contradicts a published document | §2.3, §2.4, §10.4 |

**Definition of done.** Complete when every criterion is met, Q-01 and Q-02 are decided, `BE-005` is
issued, and `PGD-000`'s `DA-001` row is updated with a fresh enumeration timestamp. **`DA-001` reaches
✅ as a *standard* on issue; as a *complete DDL set* it tracks `AR-003`'s per-module schedule** — the
per-table DDL is produced with each module's SDD, one wave ahead of build.

---

## 18. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-008` | 22 aggregates, 54 invariants — this is their physical realisation |
| Upstream | `AR-005` | Boundary rulings determine table ownership |
| Upstream | `AR-007` §4 | Naming and model conventions, realised physically here |
| Upstream | **`BE-005`** | CD identifiers — Q-04, blocking |
| Downstream | `DA-002` | Field-level dictionary over this structure |
| Downstream | `DA-005` | Classification applied to these columns |
| Downstream | `DA-006` | Partition and tombstone shapes |
| Downstream | `DA-007` | Source grain for the warehouse |
| Downstream | `DA-009` | Code lists behind every enumeration and `state` |
| Downstream | `MG-003`, `DM-004`…`DM-010` | Migration targets — §13 |
| Downstream | `SC-007` | §10 and its §10.4 finding |
| Downstream | `PE-006` | §7 volumetrics |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` | Superseded as a *schema* source; retained for ERDs (§8) and classification (§10) pending Q-01 |

---

## 19. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-002_Data_Dictionary.md` … `./DA-009_Reference_Data_and_Code_List_Register.md` ·
`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-008_Domain_Model_and_Bounded_Context_Map.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §8 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §12.3 ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-001_Master_Data_Governance_Charter.md`

**External standards and sources**

| Source | Version / date | Verified |
|---|---|---|
| [ISO/IEC 11179-1:2023 — Metadata registries, Part 1: Framework](https://www.iso.org/standard/78914.html) | Edition 4, January 2023 | 2026-08-18 |
| [DAMA-DMBOK](https://www.damadmbok.org/) | 2.0 with the 2024 maintenance revision; **3.0 in development, not released** | 2026-08-18 |
| [PostgreSQL 18 release notes](https://www.postgresql.org/docs/current/release-18.html) · [Table partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) | 18 released 25 September 2025 | 2026-08-18 |
| [PostgreSQL end-of-life dates](https://endoflife.date/postgresql) | 16 → Nov 2029; 18 → **14 November 2030** | 2026-08-18 |
| [Bangladesh PDPA 2026 overview](https://securiti.ai/bangladesh-personal-data-protection-act-overview/) | In force; enforcement ~13 May 2027 | 2026-08-18 |
| [Personal Data Protection (Amendment) Ordinance 2026, No. 23 of 2026](https://digitalpolicyalert.org/event/38601-president-implemented-personal-data-protection-amendment-ordinance-2026-ordinance-no-23-of-2026) | Promulgated 5 February 2026 | 2026-08-18 |
| [Government eases data localisation rules — The Daily Star](https://www.thedailystar.net/news/bangladesh/news/govt-eases-data-localisation-rules-drops-jail-terms-tech-firms-4076391) | February 2026 | 2026-08-18 |
| Odoo 19.0 ORM and inheritance model | 19.0 (released 18 September 2025) | 2026-08-18 |

---

## 20. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Scoped to the measured **1,335 tables / 5,301 fields**, not `05-02`'s 225. Establishes the standard column contract, names **12 partition keys**, and specifies the residency-split physical model. Raises `PGD-A5-01` (catalogue stale ~6×), `PGD-A5-02` (54 bare `currency` columns) and `PGD-A5-03` (residency may be a mirror, not an exclusion) | *Pending — Chief Architect* |

---

*`DA-001` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
