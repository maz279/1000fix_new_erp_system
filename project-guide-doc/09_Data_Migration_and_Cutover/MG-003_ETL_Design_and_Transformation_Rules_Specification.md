---
id: MG-003
title: ETL Design and Transformation Rules Specification
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Migration Engineering Lead (unappointed — see MG-001 §5.1)
approver: Chief Technology Officer with Chief Architect
standards_basis: >
  DAMA-DMBOK 2.0 Ch. 8 — Data Integration & Interoperability (ELT/ETL design, latency, lineage) ·
  Odoo 19.0 ORM external-identifier and `load()` semantics · Transactional outbox pattern
  (AR-009) · ISO 8000-61:2016 data quality control · IEEE 1016-2009 design viewpoints
  (composition, dependency, information, interface)
traces_to: >
  PGD-000 MG-003 · AUDIT-011 DM-01 items 1, 2, 5, 6, 7 · BRD MIG-003, MIG-008, MIG-009, MIG-010,
  MIG-011, MIG-012, MIG-014 · 05-02 §12 MIG-02, MIG-05, MIG-06 · 05-06 OPS-07 · DM-003 SQ-01…SQ-18 ·
  DM-011 DQ-01…DQ-26 · DM-012 · DA-001 §3, §10, §12 · AR-009 §5 · AR-001 LB-08
depends_on: MG-001 · MG-002 · DA-001 · DA-002 · DA-009 · AR-007 · AR-009 · SC-007 · BE-004 · BE-006
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 22:35 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-003 — ETL Design and Transformation Rules Specification

### Category 09 · Code `MG` · DAMA-DMBOK 2.0 Ch. 8 · Odoo 19.0 ORM · Transactional outbox · IEEE 1016-2009

---

> **Local rule prefix: `ETR-nn`.** Verified unused workspace-wide at 2026-08-18 22:35 (+06).

---

## 1. Purpose

**This document specifies the machine.** `DM-003` states the order tiers load in; `DM-004`…`DM-010`
state which source field becomes which target field; `DM-011` states the quality rules;
`DM-012` states the file formats. **Nothing states how any of it executes.**

`AUDIT-011` `DM-01` names five of its seven unspecified items as belonging here — the ETL platform
and its retry, checkpointing and idempotency semantics; the staging-layer architecture; merge
reversibility; delta capture; and **the migration tooling itself, which BRD `MIG-008` requires
delivered to the Company, repeatable and re-runnable.**

This document supplies all five, plus the design decisions that the target architecture forces and
nobody has yet confronted: **that a bulk load through the Odoo ORM publishes an event per record
into a live bus with live consumers**, and that a bulk load *around* the ORM produces records the
application would never have permitted.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The pipeline architecture: seven zones, and what each guarantees (§4) |
| 2 | The tooling decision, with the alternatives tested and rejected (§3) |
| 3 | The load mechanism and **idempotency by deterministic external identifier** (§5) |
| 4 | The **residency second pass** through `CD-233` (§6) |
| 5 | The transformation-rule catalogue: structure, classes, and the standard transforms (§7) |
| 6 | Lineage: batch, run and record-level control values (§8) |
| 7 | Cleansing, matching and **merge reversibility** execution (§9) |
| 8 | Delta capture during the parallel run (§10) |
| 9 | The archive path and its exclusion mechanism (§11) |
| 10 | Error handling, restartability and the reject queue (§12) |
| 11 | **Event suppression during migration** — the finding this document raises (§13) |
| 12 | Performance, batching and the volumetric model (§14) |
| 13 | Rules `ETR-01`…`ETR-50` (§15) |

**Explicitly out of scope**

| Topic | Owned by |
|---|---|
| Profiling and extract | **`MG-002`** |
| Which fields map to which | `DM-004`…`DM-010` |
| Quality rule **content** and match thresholds | `DM-011` |
| Reconciliation reporting and sign-off | **`MG-004`**; `DM-013` |
| Rehearsal and timing measurement | **`MG-005`** |
| Rollback mechanics | **`MG-007`** |
| Environment sizing and provisioning | `PE-002` ⛔, `PE-005` ⛔ |
| Warehouse ETL (`CD-243`, dbt, W4) | `DA-007`; a different pipeline for a different purpose |
| Odoo **version-to-version** upgrades (OpenUpgrade) | `DA-001` §12; not migration — §3.2 |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| **DAMA-DMBOK 2.0** | Ch. 8 §2.2 ETL/ELT; §2.6 Data lineage; §2.8 Latency | §4 zone model; §8 lineage; §14 batch latency | DMBOK's real-time integration patterns are `IN-001`'s, not migration's |
| **IEEE 1016-2009** | Composition, dependency, information and interface design viewpoints | §4 composition; §4.4 dependency; §7–8 information; §5 interface | Structure and state-dynamics viewpoints belong to `AR-003` per module |
| **Odoo 19.0** | ORM `load()` and `ir.model.data` external identifiers | §5 load mechanism; `__migration__` namespace | `base_import`'s interactive UI is not used; the same code path is driven programmatically |
| **Transactional outbox** (`AR-009` §5) | Event written in the same transaction as the state change | §13 states the migration consequence and the suppression design | **This document proposes a suppression mechanism `AR-009` does not currently define** — raised as `MGA-04` |
| **ISO 8000-61:2016** | Data quality control (7.3) | §9 cleansing and §12 rejection are the control loop | — |
| `05-06` `OPS-07` | Forward-only, tested against production-sized data, reversible by documented procedure | §12 restartability; `MG-005` testing; `MG-007` reversal | — |

### 2.2 The constraints this design must satisfy simultaneously

Collected from across the estate. **Every one of them is already mandatory somewhere; this is the
first document in which they appear together, and three of them conflict.**

| # | Constraint | Source |
|:--:|---|---|
| C1 | Cleansing in the source or a staging layer, **never silently during load** | `05-02` `MIG-02`; `DQ-03` |
| C2 | Every load reversible; a dry run precedes every production load | `05-02` `MIG-03`; `SQ-11` |
| C3 | Legacy identifiers preserved on every migrated record | `05-02` `MIG-05`; `MS-18`; `FR-SRM-088` |
| C4 | Uncleansable records to a flagged, excluded archive area | `MIG-06`; `MIG-012`; `MS-08` |
| C5 | Migration idempotent and restartable | `DA-001` `MG-08` |
| C6 | Computed fields are computed by the platform, never supplied | `SQ-04` |
| C7 | **Residency-classified values only through `CD-233`** — no direct query, no migration script, no backfill | `AR-001` `LB-08`; `DA-001` `RS-03` |
| C8 | **An outbox row is written in the same transaction as every state change** | `05-02` `DM-15`; `AR-009` §5 |
| C9 | No two parallel loads write the same table or read a table the other writes | `SQ-07` |
| C10 | Deltas load in tier order; never a full re-run | `SQ-13`; `MS-17`; `MIG-009` |
| C11 | Bengali normalised to UTF-8 at extract, before matching or loading | `MS-26`; `MIG-011` |
| C12 | Tooling **delivered to the Company**, repeatable and re-runnable | **BRD `MIG-008`** |
| C13 | No migrated record enters `Active`/`Approved` where the module requires approval | `MS-09` |
| C14 | Rejected records go to the remediation queue, never to a later tier | `SQ-14` |

> **The three that conflict:** C5 (idempotent, restartable) plus C8 (outbox on every write) plus C12
> (re-runnable by the Company) means a re-run republishes every event. §5 and §13 resolve it.

---

## 3. Tooling

### 3.1 The requirement, before the answer

BRD `MIG-008` is contractual and it is unusually specific: *"Migration tooling delivered to the
Company, repeatable and re-runnable."* Four properties follow, and they eliminate most options.

| # | Property | Consequence |
|:--:|---|---|
| 1 | **Delivered to the Company** | Not a consultant's laptop, not a SaaS account that lapses. It lives in the monorepo (`BE-004`) |
| 2 | **Repeatable** | Deterministic: the same input produces the same output, including keys |
| 3 | **Re-runnable** | Idempotent: running twice produces one record, not two (`ETR-09`) |
| 4 | *(implied by `MIG-005`, `SQ-11`)* | Runs identically in `migration-staging`, rehearsal and production |

### 3.2 What is **not** the tool, and why it needs saying

| Candidate | Why it is not the answer |
|---|---|
| **OCA OpenUpgrade** | It migrates **Odoo version to Odoo version** — schema deltas between major releases, with per-module upgrade scripts. It has no concept of a legacy source. It is the right tool for `DA-001` §12 `MG-01`…`MG-08` schema changes and irrelevant to legacy migration. **This confusion is likely enough that it is recorded rather than assumed away** |
| **`CD-243` warehouse ETL (dbt)** | The estate's only declared transformation tooling — and it is **W4**, and it loads a **ClickHouse warehouse**, not the operational model. Using it for W1 migration would mean building the W4 component at W0 for a purpose it was not designed for |
| **Direct SQL into PostgreSQL** | Bypasses ORM constraints, computed fields (C6), `_inherit` chains, record rules and **the outbox (C8)**. Produces rows the application would never have created and events that never fire. `AR-007` `N-18` and `AR-001` `LB-08` forbid it outright for classified data, and the same reasoning applies more broadly |
| **Odoo's interactive import UI (`base_import`)** | The right *code path*, the wrong *interface*. Manual, unlogged, unrepeatable, and it cannot be put in a runsheet with a measured duration |
| **A commercial ETL suite** | Would satisfy 2 and 3 and fail 1: licence cost, vendor lock and a skill the Company does not retain. `AR-013` build-vs-buy weighs this the same way for the platform generally |

### 3.3 The tooling decision

**`ETR-01`: the migration tool is a purpose-built Python package in the monorepo, driving the Odoo
ORM's `load()` path with deterministic external identifiers, over a PostgreSQL staging schema.**

| Layer | Technology | Why |
|---|---|---|
| **Staging store** | **PostgreSQL 16** — a separate schema/database in `migration-staging` | Already the platform's database (TSS); SQL is the right language for profiling and set-based cleansing; no new skill |
| **Transformation** | **Python 3.12** — the platform language (`BE-002`) | Same language, same linting, same CI, same reviewers as the rest of the estate |
| **Load** | **Odoo ORM `load()`** via a programmatic harness, using `ir.model.data` external identifiers | Preserves constraints, defaults, computed fields, `_inherit` chains and onchange-equivalent logic. **Gives idempotent upsert for free** (§5) |
| **Orchestration** | A declarative **run plan** per tier, executed by the harness | `DM-003` §4.4 is already the plan; the harness executes it rather than a second scheduler owning the order |
| **Reference implementations reviewed** | OCA-adjacent `odoo-data-flow` / `odoo_csv_import` (external-ID upsert, batched loading, transformation mappers) | Their **pattern** is adopted; whether either is vendored or reimplemented is `ETR-02` |

> **`ETR-02` — vendor-or-build is deferred to the Chief Architect, not settled here.** The *pattern*
> is decided: external-ID-keyed idempotent upsert through `load()`. Whether the estate vendors an
> existing OCA-community library under `BE-004`'s `vendor/` isolation and `BE-007`'s licence rules,
> or implements the pattern directly, is a build decision with licence and support consequences.
> **Either satisfies `MIG-008`; neither is assumed.** Raised as `Q-01`.

> **`ETR-03` — no orchestrator is introduced.** Airflow, Prefect and Dagster are all absent from the
> TSS and each would add an operational surface for a workload that runs nine times. The run plan is
> data; the harness is a CLI; the schedule is a human with a runsheet (`MG-006`). If a future
> steady-state integration needs orchestration, that is `IN-001`'s decision, not this one.

### 3.4 What "delivered to the Company" means concretely

| # | Deliverable | Standard |
|:--:|---|---|
| 1 | The package, in the monorepo, at a tagged release | `BE-004`, `BE-003` |
| 2 | A `README` and an operational runbook | `BE-006` |
| 3 | A `component.yaml` declaring what it touches | `BE-006` |
| 4 | A test suite runnable by `make` on a developer machine against synthetic data | `BE-001` |
| 5 | The **run plans** for all nine waves, as version-controlled data | `ETR-04` |
| 6 | Every transformation rule as **code with a test**, not as a spreadsheet comment | `ETR-05` |
| 7 | A `CD-SVC-nn` identifier in `BE-005` | **Does not exist — `MG-001` `Q-07`** |

---

## 4. Pipeline Architecture

### 4.1 Seven zones

**`ETR-06`: data moves forward only, one zone at a time, and every zone boundary is a recorded
event with a row count.** A zone is not a directory; it is a guarantee about what is true of the
data inside it.

```
 ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
 │ Z1 LAND  │──►│ Z2 RAW   │──►│ Z3 CLEAN │──►│ Z4 CONF  │──►│ Z5 LOAD  │──►│ Z6 TARGET│
 │ as       │   │ typed,   │   │ cleansed,│   │ conformed│   │ staged   │   │  Odoo /  │
 │ received │   │ manifest-│   │ matched, │   │ to DA-001│   │ payload, │   │ Postgres │
 │ immutable│   │ verified │   │ survived │   │  targets │   │ keyed    │   │          │
 └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └────┬─────┘
       │              │              │              │              │             │
       └──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
                                     │                                    ┌──────┴──────┐
                            ┌────────▼────────┐                           │ Z7 ARCHIVE  │
                            │  REJECT / QUEUE │                           │  flagged,   │
                            │  E1…E9 (DM-013) │                           │  excluded   │
                            └─────────────────┘                           └─────────────┘
```

| Zone | Guarantee | Physical form | Retention |
|:--:|---|---|---|
| **Z1 Land** | **Byte-identical to what the source produced.** Never modified | Object storage, hash-verified against the `MG-002` manifest | Until wave gate + statutory period |
| **Z2 Raw** | Parsed into typed columns; encoding normalised to UTF-8/NFC; manifest count reconciles | PostgreSQL staging tables, one per source object | Until parallel-run exit |
| **Z3 Clean** | `DM-011` rules applied; sentinels resolved; matched, merged, survived | PostgreSQL staging | *ibid.* |
| **Z4 Conform** | Values conformed to `DA-001` types, `DA-009` code lists, `DA-002` domains | PostgreSQL staging | *ibid.* |
| **Z5 Load payload** | The exact records to be loaded, each carrying its **deterministic external ID** | PostgreSQL staging + generated payload files | *ibid.* |
| **Z6 Target** | Live Odoo/PostgreSQL | The operational model | Live |
| **Z7 Archive** | Loaded, retrievable, **flagged and excluded** from operational logic | `DA-006` §8 archive tier | Per retention class |

> **`ETR-07` — Z1 is never edited, and this is not a formality.** Every reconciliation in `MG-004`
> is ultimately an assertion about Z1 versus Z6. If Z1 can be corrected in place, the denominator
> moves and R1 becomes uncomputable. A corrected source produces a **new extract** with a new
> `extract_id` (`MG-002` `LPX-25`).

> **`ETR-08` — cleansing happens in Z3, which satisfies C1 without ambiguity.** `MIG-02`'s *"in the
> source or a staging layer"* has been read loosely enough that `DM-011` `DQ-03` had to restate it.
> This design makes it structural: **the load path (Z5→Z6) has no transformation capability at all.**
> It reads a payload and writes it. There is nowhere for a silent cleanse to happen.

### 4.2 The staging schema

| Object class | Naming | Purpose |
|---|---|---|
| Raw tables | `raw_<src>_<object>` | Z2, one per source object, all columns text |
| Clean tables | `cln_<domain>_<entity>` | Z3 |
| Conform tables | `cnf_<domain>_<entity>` | Z4 |
| Payload tables | `pay_<odoo_model>` | Z5, one per target model |
| Reject table | `rej_records` | All zones, one row per rejected record with zone, rule and category |
| Control tables | `ctl_batch`, `ctl_run`, `ctl_step`, `ctl_xref`, `ctl_rule` | §8 |

> **`ETR-09`.** Staging tables are **wave-scoped and dropped at parallel-run exit** with a recorded
> destruction, per `MG-001` `MST-16`. A staging schema that survives its wave becomes an
> unmanaged copy of the customer base.

### 4.3 What runs where

| Zone transition | Executed by | Environment |
|---|---|---|
| Source → Z1 | The extract procedure (`MG-002` §7) | Custodian side → `migration-staging` |
| Z1 → Z2 | Parser (Python) | `migration-staging` |
| Z2 → Z3 | Cleanse/match (SQL + Python) | `migration-staging` |
| Z3 → Z4 | Conform (SQL) | `migration-staging` |
| Z4 → Z5 | Key generation and payload build (Python) | `migration-staging` |
| **Z5 → Z6** | **The load harness, over the Odoo ORM** | Executes **against the target environment** |
| Z6 → Z7 | Archive loader | Target |

> **`ETR-10`.** Only the Z5→Z6 step touches the target. Everything before it is reversible by
> deleting a staging table. **This is what makes `MG-007`'s rollback analysis tractable**: there is
> exactly one crossing point.

### 4.4 Dependency on `DM-003`

**`ETR-11`: the run plan is generated from `DM-003` §4.4, never authored independently** — the same
rule `DM-014` `CV-12` applies to the runsheet, applied one layer down. A run-plan step with no tier
in `DM-003` is a breach (`SQ-18`).

---

## 5. The Load Mechanism and Idempotency

### 5.1 Why the ORM, restated as design

| Requirement | Satisfied by the ORM path | Would be violated by direct SQL |
|---|---|---|
| C6 computed fields computed by the platform | Computes on write | Would need every computation reimplemented, and drift silently |
| `_inherit` chain behaviour across 79 build units | Applies | Bypassed |
| Constraints, `_sql_constraints`, `@api.constrains` | Enforced | Bypassed — invalid records land silently |
| Record rules and default values | Applied | Bypassed |
| C8 outbox row per state change | Written | **Not written — the event never exists and the divergence is silent (`TR-12`)** |
| Sequences and document numbering | Allocated correctly | Corrupted, and `M51`'s Mushak continuity depends on it |

> **`ETR-12`.** The load path is the ORM. Direct SQL is permitted **only** for (a) `ANALYZE`/index
> maintenance, (b) reading for reconciliation, and (c) the two explicitly-designed bulk paths in
> §14.3, each of which is named, reviewed and tested. Anything else is a design deviation requiring
> `AR-004` an ADR.

### 5.2 Deterministic external identifiers — the idempotency mechanism

Odoo's `ir.model.data` external identifier makes a load idempotent: loading a record whose external
ID already exists **updates** it rather than creating a second one. That property is only useful if
the identifier is **derivable from the source**, not allocated at load time.

**`ETR-13`: every migrated record's external identifier is a pure function of its source identity.**

```
  __migration__.<source_id>_<entity>_<legacy_record_id>

  examples
  __migration__.SRC008_party_C-0041288
  __migration__.SRC005_service_order_DHK-2024-11-04417
  __migration__.SRC017_asset_FA-2019-0883
```

| Property | Consequence |
|---|---|
| **Deterministic** | The same source row always produces the same external ID, in any environment, on any run |
| **Namespaced** | `__migration__` is reserved; nothing else may allocate in it (`ETR-14`) |
| **Source-qualified** | The same legacy id in two sources produces two identifiers — which is correct; deduplication is `DM-011`'s job, not the key's |
| **Re-runnable** | Satisfies C5 and `MIG-008` property 3 without a bespoke upsert |
| **Traceable** | The external ID **is** the lineage link, in addition to the §8 control columns |

> **`ETR-15` — where the source has no stable identifier, one is minted in Z2 and frozen.** Fourteen
> spreadsheet sources have no primary key. The rule: a **surrogate legacy key** is generated in Z2
> from a stated column set plus the file origin, recorded in `ctl_xref`, and **never regenerated**.
> A regenerated surrogate key breaks idempotency invisibly — the second run creates duplicates and
> every reconciliation still passes.

> **`ETR-16` — a merge does not delete the loser's external identifier.** `DQ-17` retains the loser
> and links it; the loser's `__migration__` external ID must resolve, or a re-run recreates it as a
> new record. §9.4 specifies the redirect.

### 5.3 The upsert semantics per disposition

| Disposition | Semantics | Reload policy |
|---|---|---|
| `M` migrate live | Upsert by external ID | Per `DM-003`; **`X7` and `X8` step 5 are `never_reload`** (`SQ-06`) |
| `A` archive | Insert into the archive path (§11) | Append-only |
| `N` author new | **Not loaded by this pipeline.** Seed content via `MD-048` | n/a |
| `C` count | **No load step exists** (`SQ-12`) | n/a |
| `L` leave | Never enters Z1 | n/a |
| `P` purge | Never enters Z1; evidenced destruction only | n/a |

> **`ETR-17` — `never_reload` is enforced by the harness, not by discipline.** `X7` opening balances
> and `X8` YTD payroll carry a `never_reload` flag in the run plan; the harness **refuses** to
> execute a second load against a completed batch for those tiers without a recorded CFO/HR Director
> override token. `M56` calls a YTD reload *"the most dangerous migration in the programme"*; a rule
> in a document does not stop a tired engineer at 03:00 re-running a step.

### 5.4 State on load

**`ETR-18`: no migrated record enters an `Active` or `Approved` state where the owning module
requires an approval** (C13, `MS-09`). The load sets the state the module's own state machine would
permit for an unapproved record, and the approval — if any — is a business act afterwards.

---

## 6. The Residency Second Pass

### 6.1 The design

C7 is absolute: `AR-001` `LB-08` forbids a migration script touching the resident store. `DA-001`
`RS-03` repeats it. `AR-007` `MG-07` repeats it again. **Three documents forbid the obvious
implementation, and none specifies the alternative.** This is it.

```
  PASS 1 — main load (Z5 → Z6)
     writes fix_identity_document with:  party_id, document_type, issuing_country,
                                         verified_on, resident_key = NULL
     the classified value is NOT in the payload and never entered staging

  PASS 2 — residency load (Z1 → CD-233 → Z4 store)
     reads the classified value from the LANDED EXTRACT (Z1), in memory, per record
     calls CD-233 write API with (value, purpose, actor)
     receives resident_key
     calls the ORM to set fix_identity_document.resident_key
     the value is never written to Z2, Z3, Z4, Z5, a log, or a reject file
```

| # | Rule | Class |
|---|---|:--:|
| `ETR-19` | Pass 2 reads the classified value **only from Z1**, in memory, and never persists it in staging | **H** |
| `ETR-20` | Pass 2 runs **only after** the resident store is live and verified (`NFR-086`, `MS-21`, `SQ-10`) | **H** |
| `ETR-21` | A pass-2 failure leaves `resident_key = NULL` and the record on a **residency hold queue** (`DM-013` `E4`), never in a reject file containing the value | **H** |
| `ETR-22` | Pass 2 is **idempotent by the primary record's external ID**, not by the value. Re-running must not mint a second `resident_key` for the same field | **H** |
| `ETR-23` | Pass 2 logs actor, purpose and instant per write, per `RS-05` and `SC-010` | **H** |
| `ETR-24` | Z1 extracts containing classified values carry the **shortest retention in the estate** and are destroyed on pass-2 completion for that batch, with a destruction record | **H** |

### 6.2 The three consequences that must be planned for

| Consequence | Detail |
|---|---|
| **The classified data is never profiled or cleansed** | A malformed NID is discovered at pass 2, not at profiling (`MG-002` §10.2). Pass 2 therefore needs **its own validation and its own reject handling**, not a backfill's optimism |
| **Pass 2 is the least rehearsable step** | It cannot be rehearsed against production-derived classified data (`MG-001` §7.3, `Q-04`). It is rehearsed against synthetic keys, which tests the mechanism and not the data |
| **Pass 2 depends on `CD-233` at W1** | A **W1** Block 3 service whose effort is in no baseline (`BE-005` `BEA-05`). If it slips, `SQ-10` holds the fields out — correctly, and indefinitely |

---

## 7. The Transformation Rule Catalogue

### 7.1 Why a catalogue rather than code alone

`DM-004`…`DM-010` express transformations as workbook prose — *"trim, title-case, resolve to
`MD-006` upazila"*. That is right for a business-facing workbook and insufficient for execution.
**`ETR-25`: every workbook mapping row compiles to exactly one catalogued rule with an identifier,
an implementation and a test.**

| Column | Purpose |
|---|---|
| `rule_id` | `TR-<domain>-<nnn>` — allocated in `ctl_rule`, per domain |
| `workbook_ref` | The `DM-00n` row it implements |
| `source_field(s)` | One or more Z2 columns |
| `target_field` | The `DA-002` field |
| `class` | §7.2 |
| `implementation` | The Python callable or SQL expression |
| `null_behaviour` | `pass_null` / `default` / `reject` / `hold` |
| `failure_category` | → `DM-013` `E1`…`E9` |
| `test_ref` | The unit test that proves it |
| `owner_confirmed` | The business owner's confirmation (`MST-08`) |

> **`ETR-26`.** A rule with no `test_ref` may not run in production. `BE-006`'s 23-criterion
> definition of done applies to the migration package as to any component.

### 7.2 The eight rule classes

| Class | Meaning | Example | Reject on failure? |
|:--:|---|---|:--:|
| **T1 Copy** | Direct, type-converted | `customer_name` → `fix_party.name` | On type failure |
| **T2 Normalise** | Deterministic cleanup | Trim, collapse whitespace, case, NFC, digit normalisation | No |
| **T3 Parse** | Structured value from text | Mobile number to E.164; date from 6 observed formats | **Yes** |
| **T4 Look-up** | Resolve to a reference code | District name → `MD-006` code; brand name → `MD-021` | **Yes** (`E2`) |
| **T5 Derive** | Computed from several source fields | `full_address` from five columns | Configurable |
| **T6 Default** | Where the source is silent and the target requires a value | `country_id` = Bangladesh | No — but **the defaulted count is reported** |
| **T7 Classify** | Assign a target state, class or rung | Contract evidence rung; asset confidence `confirmed`/`probable`/`provisional` | No |
| **T8 Suppress** | Deliberately do not map | A legacy column with no target | No — **the decision is recorded** |

> **`ETR-27` — T6 defaults are counted and reported per field.** A default is a value the business
> never supplied. `DM-013` `R5` compares null profiles source-to-target; a silent default makes the
> target look *more* complete than the source, which reads as an improvement and is a fabrication.

> **`ETR-28` — T8 exists so that "unmapped" is a decision.** Every Z2 column is either mapped or
> explicitly suppressed with a reason. A column that is neither is an **unreviewed column**, and the
> harness fails the build. This is how a legacy field that mattered gets noticed before cutover
> rather than after.

### 7.3 The standard transforms

Implemented once, in the shared library, tested once, used everywhere. `DM-011` §2.4 already lists
the cleansing transformations; this is their executable form.

| # | Transform | Notes |
|---|---|---|
| `S-01` | Whitespace trim and internal collapse | Applied before every comparison |
| `S-02` | Unicode **NFC** normalisation | C11; `MG-002` `LPX-24` |
| `S-03` | Bengali digit → ASCII digit for numeric and identifier fields | Display text preserved |
| `S-04` | Bangladesh mobile normalisation to `+8801XXXXXXXXX` | Handles `01…`, `8801…`, `+8801…`, spaces, hyphens |
| `S-05` | Date parse against an **explicit ordered format list per source**, never a generic parser | Ambiguous `03/04/2024` must not be guessed — §7.4 |
| `S-06` | Decimal parse with thousands separators and Bengali numerals | Currency is `numeric`, never float (`DA-001` §4) |
| `S-07` | Sentinel-to-null using the source's registered sentinel set | `MG-002` §4.3 |
| `S-08` | Name casing — **title case with an exception list**, never blind `.title()` | `MD` name conventions |
| `S-09` | Geography resolution to `MD-006` codes, cascade division→district→upazila | Fails to `E2`, never to a guess |
| `S-10` | Legacy-reference preservation into the §8 control columns | C3 |

### 7.4 The date-ambiguity rule

**`ETR-29`: no date is parsed by a format-guessing parser.** Each source declares its date format(s)
in profiling (`MG-002`), and `S-05` parses only against that declaration. Where a source genuinely
mixes formats, the **ambiguous subset is rejected to `E1`, not resolved by probability.**

> `DM-013` `RV-03` names a one-month date displacement as the classic semantic defect that passes
> both row counts and control totals. A day/month swap on a Bangladeshi service-order date produces
> a plausible date every time, and it is undetectable after load. This rule is the only defence, and
> it costs rejections.

---

## 8. Lineage and Control Values

### 8.1 Record-level: the three mandatory columns

`MS-18` and C3 require them; `DA-001`'s standard column contract carries them; this document states
their population.

| Column | Populated from | Mutability |
|---|---|---|
| `legacy_source_system` | `DM-002` `source_id` | **Immutable after load** |
| `legacy_record_id` | The source's identifier, or the Z2 surrogate (`ETR-15`) | Immutable |
| `migration_batch_id` | `ctl_batch.batch_id` | Immutable |

> **`ETR-30`.** These three columns are set by the load and **never editable afterwards**, enforced
> at the ORM layer, not by convention. `FR-SRM-088` delivers a user-facing feature on them — *"look
> up migrated historical service records with their original references"* — and `MG-004`'s
> reconciliations key on them. An editable lineage column is a lineage column that will be edited.

### 8.2 Run-level: the control tables

| Table | Grain | Key contents |
|---|---|---|
| `ctl_batch` | One per wave × tier × environment | `batch_id`, wave, tier, environment, cut-off instant, opened_by, state |
| `ctl_run` | One per execution attempt of a step | `run_id`, `batch_id`, step, start, end, outcome, operator, tool version |
| `ctl_step` | One per run-plan step | Step, tier, predecessor, reload policy, measured duration from rehearsal |
| `ctl_xref` | One per source record | `source_id`, `legacy_record_id`, surrogate key, external ID, target model, target id, zone reached, outcome |
| `ctl_rule` | One per transformation rule | §7.1 |

> **`ETR-31` — `ctl_xref` has a row for every source record, including the ones that never load.**
> This is the table that makes `DM-013` `RV-02`'s R1 identity computable: *source = loaded +
> rejected + excluded*, with a per-record explanation rather than an aggregate. `AUDIT-011` and
> `RV-02` both single out the "700 unaccounted records" failure mode; `ctl_xref` is what prevents it
> arithmetically rather than by care.

> **`ETR-32` — the batch id is declared before the first row** (`SQ-09`), and appears in every log
> line, every reject row, every reconciliation report and every runsheet step.

---

## 9. Cleansing, Matching and Merge Reversibility

### 9.1 Cleansing (Z2 → Z3)

`DM-011` owns the rules. **`ETR-33`: cleansing is a recorded transformation, never an in-place
update.** Z3 carries both the original and the cleansed value per field, so that a cleanse can be
inspected, challenged and reversed without re-extracting.

### 9.2 Matching

`DM-011` §2.5 specifies deterministic-first, fuzzy-last with four threshold bands. Execution notes:

| # | Rule |
|---|---|
| `ETR-34` | Matching runs in Z3, **across all sources for the entity**, not per source (`LPX-09`) |
| `ETR-35` | Match candidates and their scores are persisted, not recomputed. A score that changes between the review decision and the merge is a different decision |
| `ETR-36` | `DQ-15`'s asymmetric party rule is enforced in code: **a pass-3 fuzzy score never auto-merges a party**, whatever its value |
| `ETR-37` | The **review-queue size is computed and published before a threshold is set** (`DQ-16`, `AUDIT-011` `DM-04`), from the `MG-002` P3 candidate count |

### 9.3 Survivorship

`DM-011` §2.7 specifies attribute-by-attribute survivorship. **`ETR-38`: every surviving attribute
records which source it came from**, in a survivorship map on the golden record, so a wrong value can
be traced to a wrong rule rather than to a wrong merge.

### 9.4 Merge reversibility — `AUDIT-011` `DM-01` item 5

`DQ-20` keeps merges reversible **only through the burn-down window**, and nothing specifies the
mechanism. It is specified here.

| # | Element | Design |
|:--:|---|---|
| 1 | **The loser is retained, not deleted** | `DQ-17`; the loser record persists in an inactive state with a `merged_into` pointer |
| 2 | **The loser's external ID resolves** | To the loser record, which redirects. This is what stops a re-run recreating it (`ETR-16`) |
| 3 | **The merge is journalled** | `ctl_merge`: winner, loser, rule, score, decider, instant, and **the full pre-merge attribute set of both** |
| 4 | **Reversal is a supported operation** | Restores both records from the journal, re-points references recorded in the journal, and marks the merge reversed |
| 5 | **The window closes explicitly** | At burn-down exit the journal is retained but reversal is disabled by a recorded decision, not by the journal being deleted |

> **`ETR-39` — reversal must be *rehearsed*, not merely implemented.** `AUDIT-011` `DM-04` states the
> asymmetry plainly: a false merge exposes one customer's service history, addresses and contact
> details to another, which **under the PDPA 2026 is a personal-data incident, not a data-quality
> defect**. A reversal capability that has never been executed is a claim.

---

## 10. Delta Capture — `AUDIT-011` `DM-01` item 6

### 10.1 The requirement

BRD `MIG-009` requires incremental migration during the parallel run; `SQ-13` requires deltas in
tier order; `MS-17` forbids a second full load.

### 10.2 The mechanism, per source capability

**`MG-002` §8.2 establishes the uncomfortable input: most of this estate cannot produce a delta.**
The design therefore has three modes, and the mode is a property of the source.

| Mode | Applies to | Mechanism |
|:--:|---|---|
| **D1 — Timestamp delta** | `DB` sources with a usable `last_modified`; `MAIL`; `PUB` | Extract `where modified > cut_off`; load in tier order |
| **D2 — Set-difference delta** | `DB` sources **without** a timestamp; **all 14 `SS` sources** | Full re-extract → Z2 → **diff against the prior extract in staging** → the difference is the delta |
| **D3 — Operational catch-up** | `PAPER`; anything created on the P2 paper contingency | **Not a pipeline path.** Keyed as the `CV-11` P2 catch-up batch by operational staff |

> **`ETR-40` — D2 is a full re-extract that produces a partial load.** For the spreadsheet estate
> this means **a second 51-branch collection round per wave**, two weeks after the first. It is a
> correct design and an expensive operational commitment, and it currently appears in no plan.
> Recorded as `MG-002` `Q-03` and referred to `MG-006` for scheduling.

> **`ETR-41` — a delta never re-runs a `never_reload` tier.** `X7` opening balances and `X8` YTD are
> struck at the cut-off instant and are not adjusted by delta; a post-cut-off financial transaction
> is a **transaction in the new system**, not a migration record. Getting this wrong restates an
> opening balance, which is `SQ-06`'s entire concern.

---

## 11. The Archive Path

`MIG-06`, `MIG-012` and `MS-08` require archived records to be **retrievable, flagged and excluded**
— all three. `DM-001` `MS-08` insists on all three or it is not archived, it is loaded.

| # | Element | Design |
|:--:|---|---|
| 1 | **Retrievable** | Loaded into the archive tier (`DA-006` §8), indexed by `legacy_source_system` + `legacy_record_id`, searchable from the operational UI (`FR-SRM-088`) |
| 2 | **Flagged** | `is_migrated_archive = true` on the record, set by the load and immutable |
| 3 | **Excluded** | **Excluded by the query, not by a convention.** Every operational, SLA, ageing, KPI and forecasting query filters the flag. `DA-007` warehouse models exclude it at the source-grain layer |
| 4 | Loaded **after the go decision** | `SQ-03`; `X9` is never on the critical path |

> **`ETR-42` — exclusion is tested, not asserted.** A fitness function (`AR-012`) asserts that no
> operational aggregate includes archive-flagged rows. `M01` §16.4 requires exclusion from SLA and
> rework; `M43` requires exclusion of migrated consumption from forecasting; `M15` requires it for
> inventory. **Three modules depend on an exclusion that is currently a sentence in a document.**

---

## 12. Errors, Restartability and the Reject Queue

### 12.1 Restartability

| # | Rule |
|---|---|
| — | Every step is **restartable from its last checkpoint**, and a checkpoint is a committed batch of records with their `ctl_xref` rows written |
| — | Batch size is a run-plan parameter, defaulting per §14.2, and a batch is atomic: it commits wholly or not at all |
| — | A restart **re-processes the failed batch only**, relying on external-ID idempotency (`ETR-13`) for safety |
| — | A step that fails after N configured retries **stops the tier** and does not proceed to the next; `SQ-14` forbids carrying rejects forward |

### 12.2 The reject queue

`DM-013` `E1`…`E9` define the categories; the pipeline populates them.

| Category | Raised in zone | Contains |
|:--:|---|---|
| `E1` blocking rule | Z3 | Rule id, record key, the failing value **masked if personal** |
| `E2` referential | Z4/Z5 | The unresolved key and the target it failed against |
| `E3` evidence hold | Z4 | The rung achieved and what is missing |
| `E4` residency hold | **Pass 2** | The record key **only** — never the value (`ETR-21`) |
| `E5` excluded by disposition | Z1 | Recorded, never silently dropped (`RV-07`) |
| `E6` quarantine | Z3 | Real stock, unresolvable part |
| `E7` merged | Z3 | Winner, loser, score |
| `E8` unresolved duplicate | Z3 | The candidate pair |
| `E9` semantic defect | **Post-load** | Found by `MG-004` R5; **triggers rollback** (`T3`) |

> **`ETR-43` — a reject row never contains a residency-classified value, and personal data in reject
> rows is masked to the minimum needed to identify the record.** Reject files are copied, emailed
> and attached to tickets. They are the least-guarded artefact in any migration and the one most
> likely to leak.

---

## 13. Event Suppression During Migration

### 13.1 The finding

**`05-02` `DM-15` and `AR-009` §5 make the transactional outbox mandatory: an event row is written
in the same database transaction as every state change.** `AR-009` `TR-12` records the risk of it
*not* being applied uniformly. Neither document contemplates a bulk load.

**Consequence, if nothing is done:**

| Wave | Records loaded through the ORM | Outbox rows generated | Consumers at that wave |
|:--:|---|---|---|
| **W1** | 100,000+ parties · 100,000+ addresses · **300,000–600,000 devices** · ~50,000 service orders | **≈ 0.5–0.9 million** | **`CD-234` notification dispatcher is a W1 component** (TSS: *"Novu + CD-234 deploys in Wave 1"*), plus `M28` integration platform, plus every W1 subscriber |
| W3 | Opening balances, AR/AP open items | Hundreds of thousands | Finance consumers, dunning (`n8n`), settlement |
| W5 | Employees, YTD payroll | Tens of thousands | Payroll, notification |

**A W1 party load with a live notification consumer is capable of sending a welcome message to
every customer 1000FiX has ever had.** Nothing in the estate currently prevents it.

### 13.2 The design

**`ETR-44`: the load harness executes inside a declared migration execution context, and the outbox
relay does not publish events emitted in that context.**

| Element | Design | Why not the alternative |
|---|---|---|
| **Context flag** | The harness sets a migration context carrying `batch_id`; the outbox row is written with `origin = migration` and the batch id | Not "disable the outbox": disabling it would violate C8, lose lineage, and re-create `TR-12`'s silent divergence |
| **Relay behaviour** | The relay **skips publication** of `origin = migration` rows by default | Not "delete the rows": they are the lineage record of what the load changed |
| **Selective replay** | A named subset of event types **may** be published after the go decision, deliberately, per wave — e.g. a search-index build, a read-model projection | `AR-009` `CD-247` already provides replay-from-a-point-in-time; this reuses it rather than inventing a path |
| **Consumers that need migration data** | Are rebuilt by **projection from the loaded state**, not by consuming a synthetic event storm | Deterministic, restartable, and does not depend on consumer idempotency under 900,000 messages |

| # | Rule | Class |
|---|---|:--:|
| `ETR-45` | No production migration load runs outside the migration execution context | **H** |
| `ETR-46` | Outbox rows from migration are **written and retained**, and **not published**, unless a named event type is explicitly enabled for that batch | **H** |
| `ETR-47` | Enabling publication for an event type is a recorded decision per wave, naming the consumer that needs it and confirming that consumer's idempotency | **A** |
| `ETR-48` | The rehearsal (`MG-005`) explicitly tests that **no notification, webhook or partner push is emitted** by a migration load | **H** |

> **`ETR-48` is the one that matters.** A suppression that has never been tested against a live
> notification consumer is an assumption, and the failure mode is irreversible and public. Raised to
> `AR-009` as **`MGA-04`**: the event architecture should carry the `origin = migration` concept in
> its own §5, because `MG-003` cannot bind a component it does not own.

---

## 14. Performance and the Volumetric Model

### 14.1 What determines the window

`MG-006`'s cutover window is arithmetic: `records ÷ throughput + reconciliation + contingency`.
**Two of those three are currently unknown, and the third is unknowable until the first is measured.**

| Input | State | Measured by |
|---|---|---|
| Record counts | **Unknown to a factor of two for devices** | `MG-002` profiling |
| Throughput per model | **Never measured** | `MG-005` rehearsal |
| Reconciliation duration | Never measured | `MG-005` |

> **`ETR-49`: this document publishes no throughput figure.** ORM-path throughput depends on the
> model's constraints, computed fields, `_inherit` depth and index set — all of which are `DA-001`
> and `AR-007` properties that vary per model by more than an order of magnitude. A figure quoted
> here would be an anchor with no measurement behind it (`PG-03`). `MG-005` §5 measures it per model.

### 14.2 Batching

| Parameter | Default | Note |
|---|---|---|
| Batch size | 1,000 records, tuned per model at rehearsal | Large enough to amortise, small enough to restart cheaply |
| Commit boundary | Per batch | §12.1 |
| Parallelism | **Per `SQ-07` only** — no two loads writing the same table, or reading a table the other writes | The outbox is a shared table; §14.3 |
| Index handling | Non-essential indexes dropped before a large load and rebuilt `CONCURRENTLY` after (`DA-001` `MG-06`) | Rebuild time is part of the window and is measured |

> **`ETR-50` — the outbox table is written by every load, which makes it the contention point
> `SQ-07` warns about.** `DM-003` `SQ-07` states that parallelism across a shared foreign key is
> prohibited *"even when it appears to work in a dry run"* and names the outbox specifically.
> Parallel tier execution is therefore permitted only where rehearsal has measured outbox contention
> at production volumes.

### 14.3 The two permitted bulk paths

Named, because `ETR-12` otherwise forbids them.

| # | Path | Where used | Control |
|:--:|---|---|---|
| 1 | **Bulk `COPY` into staging tables** | Z1→Z2 only. These are not target tables | No ORM involvement is correct here |
| 2 | **Archive tier bulk insert** (`X9`) | Z6→Z7 for archive-flagged records only | Archive records are excluded from all operational logic (§11) and carry no state machine. Reviewed under an `AR-004` ADR; tested by the `ETR-42` fitness function |

---

## 15. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed.

| # | Rule | Class |
|---|---|:--:|
| `ETR-01` | The tool is a Python package in the monorepo driving the Odoo ORM `load()` path over a PostgreSQL staging schema | **H** |
| `ETR-02` | Vendor-or-build for the load library is the Chief Architect's decision; the pattern is fixed | **A** |
| `ETR-03` | No workflow orchestrator is introduced for migration | **C** |
| `ETR-04` | Run plans are version-controlled data, delivered with the tool | **H** |
| `ETR-05` | Every transformation rule is code with a test, never a workbook comment | **H** |
| `ETR-06` | Data moves forward one zone at a time; every boundary is recorded with a row count | **H** |
| `ETR-07` | Z1 is immutable; a corrected source produces a new extract | **H** |
| `ETR-08` | The load path (Z5→Z6) has **no transformation capability** | **H** |
| `ETR-09` | Staging is wave-scoped and destroyed at parallel-run exit, with a record | **H** |
| `ETR-10` | Only Z5→Z6 touches the target | **H** |
| `ETR-11` | The run plan is generated from `DM-003` §4.4 | **H** |
| `ETR-12` | The load path is the ORM; direct SQL only via the two named paths of §14.3 | **H** |
| `ETR-13` | Every record's external identifier is a pure function of its source identity | **H** |
| `ETR-14` | `__migration__` is a reserved external-ID namespace | **H** |
| `ETR-15` | A minted surrogate legacy key is frozen in `ctl_xref` and never regenerated | **H** |
| `ETR-16` | A merge loser's external identifier continues to resolve | **H** |
| `ETR-17` | `never_reload` is enforced by the harness with a recorded override token | **H** |
| `ETR-18` | No migrated record enters `Active`/`Approved` where approval is required | **H** |
| `ETR-19` | Pass 2 reads classified values only from Z1, in memory, never persisted | **H** |
| `ETR-20` | Pass 2 runs only after resident-store verification | **H** |
| `ETR-21` | A pass-2 failure holds the record; the value never enters a reject file | **H** |
| `ETR-22` | Pass 2 is idempotent by the primary record's external ID | **H** |
| `ETR-23` | Every pass-2 write is logged with actor, purpose and instant | **H** |
| `ETR-24` | Classified Z1 extracts are destroyed on pass-2 completion, with a record | **H** |
| `ETR-25` | Every workbook mapping row compiles to exactly one catalogued rule | **H** |
| `ETR-26` | A rule with no test may not run in production | **H** |
| `ETR-27` | Defaulted values are counted and reported per field | **H** |
| `ETR-28` | Every source column is mapped or explicitly suppressed; neither fails the build | **H** |
| `ETR-29` | Dates are parsed only against a declared format list; ambiguity rejects | **H** |
| `ETR-30` | The three lineage columns are immutable after load, enforced at the ORM | **H** |
| `ETR-31` | `ctl_xref` carries a row for every source record, including those never loaded | **H** |
| `ETR-32` | The batch id is declared before the first row and appears in every artefact | **H** |
| `ETR-33` | Cleansing is a recorded transformation retaining the original value | **H** |
| `ETR-34` | Matching runs across all sources for the entity, not per source | **H** |
| `ETR-35` | Match scores are persisted, not recomputed | **H** |
| `ETR-36` | A fuzzy pass-3 score never auto-merges a party | **H** |
| `ETR-37` | The review-queue size is computed and published before a threshold is set | **H** |
| `ETR-38` | Every surviving attribute records its source | **H** |
| `ETR-39` | Merge reversal is implemented **and rehearsed** | **H** |
| `ETR-40` | D2 delta means a full re-extract producing a partial load; it is scheduled and resourced | **H** |
| `ETR-41` | A delta never re-runs a `never_reload` tier | **H** |
| `ETR-42` | Archive exclusion is enforced by query and tested by a fitness function | **H** |
| `ETR-43` | No reject row contains a classified value; personal data is masked to the minimum | **H** |
| `ETR-44` | Loads run inside a declared migration execution context | **H** |
| `ETR-45` | No production load runs outside that context | **H** |
| `ETR-46` | Migration outbox rows are written and retained but not published by default | **H** |
| `ETR-47` | Publishing a migration event type is a recorded per-wave decision naming the consumer | **A** |
| `ETR-48` | Rehearsal explicitly proves no notification, webhook or partner push is emitted | **H** |
| `ETR-49` | No throughput figure is published without measurement | **H** |
| `ETR-50` | Parallel tiers require rehearsal-measured outbox contention at production volume | **H** |

---

## 16. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Vendor an existing external-ID upsert library, or implement the pattern?** Licence, support and `BE-007` obligations differ | Chief Architect with `BE-007` | **W0** | Build start |
| `Q-02` | **Which `CD-SVC-nn` identifier owns this tool, in which wave, at what effort?** `MG-001` `Q-07` | Chief Architect with `GV-007` | **W0** | Everything in this document |
| `Q-03` | **Does `AR-009` accept the `origin = migration` outbox concept?** §13 designs a mechanism in a component this document does not own | Solution Architect with `AR-009` author | **W1 minus 2 months** | `ETR-44`…`ETR-48`; the W1 load |
| `Q-04` | **Which W1 consumers must be rebuilt by projection rather than by event replay?** §13.2 | Solution Architect | W1 minus 1 month | Go-decision readiness |
| `Q-05` | **Is `CD-233` funded and scheduled for W1?** Pass 2 depends on it; `BEA-05` records Block 3 effort is in no baseline | CTO with `GV-007` | **W0** | §6; every `S3` field |
| `Q-06` | **Who owns the two unregistered domains' transformation rules** — catalogue/pricing (W1) and documents (W3–W6)? No workbook exists to compile from | Programme Content Lead | **W1** | `MST-27`; part of W1 |

---

## 17. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-003-D-01` | Load mechanism | Direct SQL · `base_import` UI · **ORM `load()` harness** | **ORM `load()` harness** | Only the ORM preserves constraints, computed fields, `_inherit` behaviour and the outbox | Slower than SQL; the throughput must be measured, and the window depends on it |
| `MG-003-D-02` | Idempotency key | Load-time surrogate · natural key match · **deterministic external identifier** | **Deterministic external ID** | Gives re-runnability (`MIG-008`) with no bespoke upsert, and doubles as lineage | A surrogate key must be minted and frozen for 14 keyless sources (`ETR-15`) |
| `MG-003-D-03` | Staging technology | Files only · a data lake · **PostgreSQL schema** | **PostgreSQL** | Already the platform database; SQL suits set-based cleansing; no new skill or licence | `migration-staging` must be sized by `PE-002` |
| `MG-003-D-04` | Orchestration | Airflow/Prefect/Dagster · **run plan + CLI harness** | **Run plan + CLI** | Nine executions do not justify an orchestration platform; `DM-003` is already the plan | Cutover steps are driven by a human runsheet (`MG-006`) |
| `MG-003-D-05` | Migration events | Publish them · disable the outbox · **write and retain, do not publish** | **Write, retain, do not publish** | Preserves lineage and C8 while preventing a 900,000-message storm into live W1 consumers | Requires an `AR-009` change (`Q-03`, `MGA-04`) and an explicit rehearsal test |
| `MG-003-D-06` | Residency loading | In-pipeline encryption · **two-pass from Z1 through `CD-233`** | **Two-pass** | `LB-08`/`RS-03` forbid any other path | Classified data is never profiled or cleansed; pass 2 needs its own validation (§6.2) |

---

## 18. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All five `AUDIT-011` `DM-01` items allocated here are specified | §3–§5, §9.4, §10, §4 |
| `AC-02` | The tooling decision names and rejects the alternatives, including OpenUpgrade | §3.2 |
| `AC-03` | Idempotency has a stated mechanism, not an aspiration | §5.2 |
| `AC-04` | The residency path satisfies `LB-08` without exception | §6 |
| `AC-05` | Every constraint C1–C14 is discharged or its conflict resolved by a recorded decision | §2.2; §17 |
| `AC-06` | The transformation catalogue makes every workbook row executable and testable | §7 |
| `AC-07` | R1 completeness is computable by construction | §8.2 `ETR-31` |
| `AC-08` | Delta capture is specified for sources that cannot produce a delta | §10.2 |
| `AC-09` | Archive exclusion is enforced and tested, not asserted | §11 `ETR-42` |
| `AC-10` | The event-storm exposure is identified, designed against, and referred to its owning document | §13; `MGA-04` |
| `AC-11` | No unmeasured throughput or effort figure is published | `ETR-49` |

---

## 19. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `MG-001` | The strategy; lifecycle stages 4–7 |
| Upstream | `MG-002` | Extracts, manifests, sentinel registers, encoding declarations |
| Upstream | `DM-003` | The tier order the run plan is generated from |
| Upstream | `DM-011`, `DM-012` | Quality rules and load templates this executes |
| Upstream | `DA-001`, `DA-002`, `DA-009` | Target schema, field definitions, code lists |
| Upstream | `AR-007`, `AR-009`, `AR-001` | ORM standards, the outbox, `LB-08` |
| Upstream | `SC-007`, `SC-010` | Residency and audit logging |
| Downstream | **`MG-004`** | Reconciles what this loads; consumes `ctl_xref` and the batch register |
| Downstream | **`MG-005`** | Rehearses and measures this pipeline |
| Downstream | **`MG-006`**, **`MG-007`** | Executes and reverses it |
| Downstream | `BE-005` | Requires a `CD-SVC-nn` allocation (`Q-02`) |
| Downstream | `AR-009` | Requires the `origin = migration` concept (`Q-03`, `MGA-04`) |

---

## 20. References

**Within this repository**
[`MG-001`](MG-001_Data_Migration_Strategy.md) · [`MG-002`](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) · [`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) · [`MG-007`](MG-007_Rollback_and_Fallback_Plan.md) ·
[`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md`](../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md) ·
[`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md`](../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md) ·
[`../03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md`](../03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md) ·
[`../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md`](../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-003_*.md`, `DM-011_*.md`, `DM-012_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` §1 `DM-15`, §12 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2

**External standards and sources**

| Source | Used for | Verified |
|---|---|---|
| DAMA-DMBOK 2.0 Ch. 8 | Zone model, lineage, latency | 2026-08-18 |
| IEEE 1016-2009 | Design viewpoints | 2026-08-18 |
| Odoo 19.0 — *Export and import data*; ORM `load()` and `ir.model.data` external identifiers | §5 load mechanism and idempotency | 2026-08-18 |
| OCA OpenUpgrade (v19 scope) | Established as **not applicable** to legacy migration (§3.2) | 2026-08-18 |
| `odoo-data-flow` / `odoo_csv_import` (community) | The external-ID upsert pattern reviewed as a reference implementation | 2026-08-18 |
| Transactional outbox pattern (microservices.io) | §13 | 2026-08-18 |

---

## 21. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Migration Engineering (unappointed) with Enterprise Architecture | Initial issue. Specifies the pipeline, tooling, idempotency, residency second pass, transformation catalogue, lineage, merge reversibility, delta capture and archive path. Raises the migration event-storm exposure as `MGA-04` | CTO with Chief Architect *(pending — `GV-001` `CC-01`)* |

---

*`MG-003` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
