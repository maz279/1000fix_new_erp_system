---
id: DM-003
title: Entity Migration Priority and Sequencing Plan
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
author: Data Migration with MDM and Platform Engineering
reviewers: [Master Data Owner, CTO, CFO, HR Director, Warehouse Manager, QA Lead, Programme Content Lead]
approver: Data Migration Lead with Master Data Owner
content_class: E
purpose: >
  States the order in which migrated entities load, the dependency that fixes each position, which
  groups may load in parallel, and where the migration sequence joins the seed sequence in MD-048.
  05-02 DM-12 enforces foreign keys at the database level, which means a child loaded before its
  parent does not warn — it fails; and a load that fails halfway through a cutover window is the
  most expensive kind of failure this programme can have.
traces_to: [MD-048, 05-02, M01, M08, M09, M15, M17, M19, M20, M21, M33, M49, M50, M51, M52, M56, M64, DM-001, DM-002, DM-012, DM-013, DM-014]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-12 foreign keys enforced at the database level with an explicit ondelete policy; §2 shared kernel entities; §8 entity relationship diagrams
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md §2.1 — the ten seed load tiers this plan starts from
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/ — §16.4 of all 67 modules, enumerated 2026-08-18, giving the load wave of every migrated dataset
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 — per-wave module content and the data-migration statement for each wave
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-003 — Entity Migration Priority and Sequencing Plan

> **Identifier note (`CG-005` §3.3).** `DM-003` is a **content** identifier. `05-02` `DM-12`
> (modelling standard — referential integrity) is the rule this plan exists to satisfy, and is
> always written with its document prefix.

---

## 1. Purpose

`05-02` `DM-12` states: *"Foreign keys enforced at the database level; `ondelete` policy declared
explicitly."* That is the correct design, and it has one operational consequence:

> **A record loaded before its parent does not produce a warning. It produces a rejection.**

`MD-048` already solves this for the **47 authored seed datasets** — ten tiers, derived by
topologically sorting the `§5` dependency declarations of every `MD` file. This plan solves the
harder half: the **migrated transactional entities**, which depend on the seed data, on each other,
and on records loaded in earlier waves that are by then live and changing.

**Consequence of absence (`CP-03`).** Without a declared sequence:

| Failure | Where it bites |
|---|---|
| A load fails at 60% inside a two-hour cutover window | `DM-014` fallback trigger fires; the wave slips |
| Service orders load before the devices they reference | 50,000 rejections that look like a data-quality problem and are a sequencing problem |
| Open AR loads before the chart of accounts is rationalised | Control accounts cannot be reconciled; `G3-08` fails |
| Contracts load before their covered assets exist | Entitlement validation at intake is unenforceable — `BRU` coverage rules silently pass |
| Payroll YTD loads before the employee record | Every subsequent payroll calculation compounds an error nobody can unwind |
| Two teams load in parallel on tables with a shared FK | Deadlocks, partial commits, and a reconciliation that cannot say what loaded |

---

## 2. Scope

**In scope:** the seam between seed loading and migration loading; the migration tier model; the
per-wave load sequence for W1–W8; parallelism and the critical path; delta and re-run ordering;
rollback ordering; and rules `SQ-01`…`SQ-18`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Seed load order for the 47 authored `MD` datasets | [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) — **`DM-003` begins where `MD-048` ends** |
| Whether an entity migrates at all | [`DM-001_Data_Migration_Strategy_and_Scope_Register.md`](DM-001_Data_Migration_Strategy_and_Scope_Register.md) |
| Where the data comes from | [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) |
| Field-level mapping | `DM-004` … `DM-010` |
| The file format each load consumes | [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) |
| Proving a load correct | [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) |
| The clock — freeze windows, cut-off instants, go/no-go | [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) |
| ETL platform, orchestration engine, retry semantics | **`06-03` — does not exist** (`DM-001` `O-01`) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Data Migration Lead** | Build the cutover runsheet and size the window |
| **Migration analysts** | Know which load their workbook feeds and what must already be present |
| **Master Data Owner** | Confirm that `MD-048` tier 9 completes before migration tier `X1` starts |
| **Platform Engineering** | Schedule the orchestration, parallelism and lock strategy |
| **QA Lead** | Design the dry-run test that proves the sequence before the real window |
| **CFO / HR Director** | See why finance and payroll loads sit where they sit |

---

## 4. Content

### 4.1 Two sequences, one seam

| | `MD-048` | `DM-003` |
|---|---|---|
| Governs | 47 **authored** seed datasets | **Migrated** transactional and party entities |
| Order derived from | The `§5` dependency table of each `MD` file | `05-02` §8 entity relationship diagrams and the module `§16.4` waves |
| Tiers | `0` … `9` | `X0` … `X9` |
| Reload policy | `full_replace` / `upsert` / `append_only` / `never_reload` | **`never_reload` by default** — see `SQ-06` |
| Runs | On every environment build | Once per wave, inside a cutover window |

> **`SQ-01` — the seam rule. No migration tier may start until `MD-048` tier 9 has completed
> successfully for that environment.** Migration references seed; seed never references migration.
> A migration load that "just needs one more code value" is a seed defect, not a migration
> workaround, and is fixed in the `MD` file (`CF-01`).

### 4.2 What fixes a position in the sequence

Only four things. Anything else is preference and is not a reason to move a tier.

| # | Constraint | Example |
|---|---|---|
| **1** | **A declared foreign key** (`05-02` `DM-12`) | `fix.service.order.partner_id` → `fix.party` |
| **2** | **A computed field that reads another table** | `fix.address.zone_code` is *computed from geometry* (`MD-007`) — zones must exist |
| **3** | **A control total that must tie to an already-loaded balance** | Open AR must reconcile to the receivable control account in the `M19` opening trial balance |
| **4** | **A business rule that blocks the record** | `M09` warranty entitlement cannot validate without the covered asset; `M08` entitlement consumption cannot open without the contract |

> **`SQ-02`.** A tier position justified by anything other than these four is challenged and moved.
> "It feels safer to do customers first" is not a dependency.

### 4.3 The migration tier model

| Tier | Contains | Depends on | May run in parallel with |
|:--:|---|---|---|
| **`X0`** | Migration control — `DM-002` source register, batch register, legacy-ID cross-reference tables | `MD-048` tier 9 | — |
| **`X1`** | **Party** — parties, party roles, party hierarchy, contact points, addresses | `X0`; seed tiers 0–2 (geography, entity, branch, zone) | — |
| **`X2`** | **Party dependants** — customer profiles, segments, credit profiles, identity documents *(S3, gated)*, consent state *(null by `MS-20`)*, corporate account assignment | `X1` | `X3` |
| **`X3`** | **Asset** — assets, asset identifiers, ownership, estates, rental pool, vehicles, tools | `X1`; seed tier 5 (device catalogue) | `X2` |
| **`X4`** | **Commercial** — contracts, covered assets, entitlements *(opening grant)*, warranty registers, protection policies, subscriptions, performance obligations | `X2`, `X3`; seed tier 6 | — |
| **`X5`** | **Service** — service orders *(live)*, work orders, repair WIP, open dispatch jobs, open consignments | `X1`, `X3`, `X4` | `X6` |
| **`X6`** | **Inventory** — counted stock positions, consignment balances, open RTVs, open POs, bin occupancy | Seed tier 5; `X1` (vendors) | `X5` |
| **`X7`** | **Finance opening** — opening trial balance, then open AR, open AP, bank balances, reconciling items, tax opening positions, **Mushak sequence assertion** | `X1`, `X4`, `X6`; seed tiers 1 and 4 | — |
| **`X8`** | **People** — employees, contracts, salary structures, **YTD payroll balances**, leave balances, competencies, certifications | `MD-048` tier 3; `X7` (GL accounts for payroll elements) | — |
| **`X9`** | **Archive** — historical service records, expired contracts, archived claims, historical invoices, OCR-indexed documents | All live tiers for that wave | Anything — **`X9` is never on the critical path** |

> **`SQ-03` — archive last, always.** `X9` volumes are the largest in the estate (500,000+ service
> records, 500,000+ paper documents) and its records are, by definition, excluded from operational
> logic. Loading archive inside the cutover window buys nothing and risks everything. `X9` runs
> **after** the go decision, over days, and its failure does not trigger fallback.

### 4.4 Per-wave load sequence

Waves and their contents are taken from `06-01` §3 and the module `§16.4` sections. Only tiers with
content in that wave appear.

#### W1 — Foundation and service core

| Step | Tier | Load | Depends on | Workbook |
|:--:|:--:|---|---|---|
| 1 | `X0` | Batch register; source register; legacy-ID cross-reference | `MD-048` complete | `DM-012` |
| 2 | `X1` | Parties — customers, corporate accounts, employees-as-parties, brand partners | Seed geography, entity, branch, zone | `DM-004` |
| 3 | `X1` | Addresses; **zone computed after load, not supplied** | Step 2; seed `MD-005` zones | `DM-004` |
| 4 | `X2` | Customer profiles, segments, corporate hierarchy, account assignments | Step 2 | `DM-004` |
| 5 | `X2` | Identity records — **`S3` fields deferred** until the resident store is verified (`MS-21`) | Step 4; `NFR-086` sign-off | `DM-004` |
| 6 | `X3` | Devices and asset identifiers | Steps 2–3; seed `MD-021` | `DM-005` |
| 7 | `X3` | Asset ownership and corporate estates | Step 6 | `DM-005` |
| 8 | `X5` | Open and recent service orders *(archive flagged separately)* | Steps 2, 6 | `DM-006` |
| 9 | `X0` | Portal identities — **forced re-authentication, no password carried** | Step 2 | `DM-012` |

> **`SQ-04`.** Step 3 loads addresses **without** `zone_code` and lets the platform compute it.
> `MD-007` declares `zone_code` as *computed from geometry*; a supplied value would be an unverified
> assertion that silently overrides the computation, and dispatch would then route against it.

#### W2 — Field operations and inventory

| Step | Tier | Load | Depends on | Workbook |
|:--:|:--:|---|---|---|
| 1 | `X1` | Technician master; rider master | W1 `X1` | `DM-004` |
| 2 | `X6` | **Counted** stock positions per location — *not* the branch spreadsheets | Physical count complete (`DM-001` `C`) | `DM-007` |
| 3 | `X6` | Van stock — vans recalled and counted | Step 2 | `DM-007` |
| 4 | `X6` | Consignment balances — **brand-confirmed** | Step 2 | `DM-007` |
| 5 | `X6` | Open RTVs and pending credits | Step 2 | `DM-007` |
| 6 | `X5` | Open field jobs; workshop WIP | W1 `X5` | `DM-006` |
| 7 | `X4` | Privilege members — **actual remaining term**, never a reset term | W1 `X2` | `DM-010` |
| 8 | `X9` | Service history archive; legacy tracker extracts | Everything above | `DM-006` |

#### W3 — Money, movement and documents

| Step | Tier | Load | Depends on | Workbook |
|:--:|:--:|---|---|---|
| 1 | `X1` | Vendor and supplier parties; courier partners | W1 `X1` | `DM-004` |
| 2 | `X7` | Rationalised chart of accounts *(or as-is — `M19` `Q-02` unresolved)* | Seed `MD-035` | `DM-008` |
| 3 | `X7` | Tax codes, VAT/Mushak mapping, document sequences | Step 2; seed `MD-037`, `MD-040` | `DM-008` |
| 4 | `X7` | **Opening trial balance from the CFO-signed, auditor-agreed TB** | Steps 2–3 | `DM-008` |
| 5 | `X7` | Bank account master and mandates | Step 2 | `DM-008` |
| 6 | `X7` | **Counted** cash positions — branch, technician, petty | Physical count complete | `DM-008` |
| 7 | `X7` | Open AR at **open-item level**, never as a balance | Steps 4, W1 `X1` | `DM-008` |
| 8 | `X7` | Open AP, advances, retention, employee advances | Steps 4, 1 | `DM-008` |
| 9 | `X7` | Open bank reconciling items; unused cheque stock | Steps 5–6 | `DM-008` |
| 10 | `X6` | Open purchase orders; supplier price lists | Step 1 | `DM-007` |
| 11 | `X5` | Open pick-and-drop consignments | W2 `X5` | `DM-006` |
| 12 | `X9` | Historical invoices → warehouse only; paper archive OCR begins | Everything above | `DM-008`, `O-02` |

> **`SQ-05` — the control-account gate.** Steps 7 and 8 do not complete on a row count. They
> complete when the total of migrated open items **reconciles exactly** to the receivable and
> payable control accounts in step 4, and `M20` §16.4 additionally requires **each of the top 50
> customer balances to be confirmed with the customer in writing**. `DM-013` owns the report; this
> plan owns the position of the gate.

#### W4 — Agreements, billing and contact

| Step | Tier | Load | Depends on | Workbook |
|:--:|:--:|---|---|---|
| 1 | `X4` | Contracts and contract lines | W1 `X2`; seed `MD-032` | `DM-010` |
| 2 | `X4` | Covered assets | Step 1; W1 `X3` | `DM-010` |
| 3 | `X4` | Entitlements as an **opening `grant` movement with a declared as-at date** | Step 2 | `DM-010` |
| 4 | `X4` | Warranty registers and protection policies | W1 `X3`; seed `MD-031` | `DM-010` |
| 5 | `X4` | Open warranty claims — **live only where submission and approval evidence exists** | Step 4 | `DM-010` |
| 6 | `X4` | Subscriptions and billing schedules with opening MRR | Steps 1, W3 `X7` | `DM-010` |
| 7 | `X4` | Performance obligations; **deferred revenue rebuilt obligation by obligation** | Steps 1, 6 | `DM-008`, `DM-010` |
| 8 | `X7` | Opening input VAT credit **agreed to the last filed Mushak 9.1**; withholding positions | W3 `X7` | `DM-008` |
| 9 | `X7` | **Mushak 6.3 sequence position asserted — continuity critical** | Step 8 | `DM-008` |
| 10 | `X9` | Archived claims, expired contracts, historical proposals | Everything above | `DM-010` |

#### W5 — People, quality and managed services

| Step | Tier | Load | Depends on | Workbook |
|:--:|:--:|---|---|---|
| 1 | `X8` | Org units and positions | Seed `MD-008`, `MD-009` | `DM-009` |
| 2 | `X8` | Employees; employment contracts | Step 1; W1 `X1` employee parties | `DM-009` |
| 3 | `X8` | **Single verified opening service-book entry** — never a reconstructed history | Step 2 | `DM-009` |
| 4 | `X8` | Salary structures; bank details *(S3, gated)* | Step 2 | `DM-009` |
| 5 | `X8` | **Year-to-date tax, PF and gratuity balances** | Steps 2, 4; W3 `X7` GL accounts | `DM-009` |
| 6 | `X8` | Leave entitlements — **agreed with each employee before cutover** | Step 2 | `DM-009` |
| 7 | `X8` | Competencies and certifications *(evidenced only)* | Step 2; seed `MD-010`, `MD-011` | `DM-009` |
| 8 | `X3` | **Counted** fixed assets; test equipment; vehicles | Physical verification complete | `DM-005`, `DM-008` |
| 9 | `X7` | Fixed-asset opening cost, accumulated depreciation, **tax-book WDV agreed with the tax consultant** | Step 8; W3 `X7` | `DM-008` |
| 10 | `X4` | MSP contract instances; monitored assets | W4 `X4` | `DM-010` |
| 11 | `X9` | Open CAPAs live; ISO history archived | Everything above | `DM-010` |

> **`SQ-06` — `never_reload` for `X8` step 5.** Year-to-date payroll balances are the only dataset
> in the estate where a re-run is more dangerous than a failure. `M56` §16.4 calls this *"the most
> dangerous migration in the programme"*: a wrong YTD compounds into every subsequent calculation
> and produces a wrong year-end tax certificate for every employee. A reload requires **HR Director
> and CFO approval**, matching `MD-048` `LDX-05`.

#### W6–W8 — later waves

| Wave | Sequence |
|:--:|---|
| **W6** | `X3` rental assets and refurbished units *(identity created in `M17` first)* → `X4` open rental agreements and deposits *(reconciled to the Finance liability)* → `X7` current-year budget as an approved locked version → `X6` open LCs and in-flight import consignments → `X9` |
| **W7** | `X1` sellers *(Registered state only)* and referral partners → `X4` alliance schemes → `X3` site leases, licences and surveyed infrastructure → `X9` |
| **W8** | `X3` e-waste backlog → `X9` `M17` fault and failure history as the `M26` label set |

### 4.5 Parallelism and the critical path

| Wave | Longest chain | Parallel opportunity |
|:--:|---|---|
| W1 | `X0` → `X1` party → `X1` address → `X2` profile → `X3` asset → `X5` order | `X2` and `X3` overlap once `X1` completes; `X9` runs entirely outside the window |
| W2 | Physical count → `X6` stock → `X6` van → `X6` consignment | `X5` open jobs and `X4` members run alongside `X6` |
| W3 | `X7` CoA → opening TB → open AR → reconciliation | `X6` open POs and `X5` consignments run alongside |
| W5 | `X8` org → employee → salary → **YTD** | `X3` asset count and `X7` asset opening run alongside `X8` |

> **`SQ-07`.** Two loads may run in parallel only when **no table is written by both** and neither
> writes a table the other reads. Parallelism across a shared foreign key is prohibited even when it
> appears to work in a dry run — `05-02` `DM-15` writes an outbox row in the same transaction as
> every state change, and contention there is invisible until volume.

### 4.6 Deltas, re-runs and rollback

| Situation | Rule |
|---|---|
| Records created in the source after the cut-off instant | **Delta load** in the same tier order, after the main load, during the parallel run (BRD `MIG-009`). Never a re-run of the full extract |
| A tier fails mid-load | Roll back **that tier only**, in reverse dependency order. Tiers already committed stay |
| A tier must be re-run | Permitted only where `reload_policy` allows. `X7` and `X8` step 5 are `never_reload` |
| Rollback ordering | **Exact reverse of load order.** `X9` → `X8` → `X7` → `X6` → `X5` → `X4` → `X3` → `X2` → `X1` → `X0` |
| Rollback duration | **Measured in the dry run and published** — `MS-23`. A rollback of unknown duration cannot be inside a cutover window |
| Partial success | Not a state. A tier is loaded and reconciled, or it is rolled back (`DM-013`) |

### 4.7 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **`SQ-01`** | No migration tier starts before `MD-048` tier 9 completes for that environment | **H** |
| **`SQ-02`** | A tier position is justified by a foreign key, a computed field, a control total or a blocking business rule — nothing else | **C** |
| **`SQ-03`** | `X9` archive loads after the go decision and is never on the critical path | **H** |
| **`SQ-04`** | Computed fields are computed by the platform, never supplied by the load | **H** |
| **`SQ-05`** | Open items reconcile to their control account before the tier is declared complete | **H** |
| **`SQ-06`** | `X7` opening balances and `X8` YTD balances are `never_reload` without CFO and HR Director approval | **A** |
| **`SQ-07`** | No two parallel loads write the same table, or write a table the other reads | **H** |
| **`SQ-08`** | Rollback runs in exact reverse tier order, with a rehearsed and published duration | **H** |
| **`SQ-09`** | Every load declares its batch id before the first row (`MS-18`) | **H** |
| **`SQ-10`** | `S3` fields load in a separate, later step gated on `NFR-086` resident-store verification | **H** |
| **`SQ-11`** | A dry run against production-sized data precedes every production load (`05-06` `OPS-07`, BRD `MIG-005`) | **H** |
| **`SQ-12`** | Physical-count datasets have no load step until the count is signed (`MS-12`) | **H** |
| **`SQ-13`** | Deltas load in the same tier order as the main load | **H** |
| **`SQ-14`** | A rejected record goes to the remediation queue, never to a later tier "to try again" | **H** |
| **`SQ-15`** | Sequence changes are re-derived from the `§5`/FK declarations, not edited in place (`RG-06`) | **C** |
| **`SQ-16`** | The Mushak 6.3 sequence assertion is the **last** finance step and is verified before go (`M51`) | **H** |
| **`SQ-17`** | No tier may load into production without the domain owner's recorded sign-off (`MD-048` `LDX-03`) | **H** |
| **`SQ-18`** | The cutover runsheet is generated from this plan; a step in the runsheet with no tier here is a breach | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the same
> scale as `05-05` §1.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-048_Master_Data_Seed_Load_Workbook_Index.md) | The ten seed tiers this plan begins after; `LDX-01`…`LDX-07` are the analogous seed rules |
| [`DM-001_Data_Migration_Strategy_and_Scope_Register.md`](DM-001_Data_Migration_Strategy_and_Scope_Register.md) | Which entities are in scope, and which are counted rather than loaded |
| [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) | Extract readiness per source; a tier cannot start before its sources are profiled |
| `05-02` §8 entity relationship diagrams; §1 `DM-12`, `DM-15` | The foreign keys and the outbox behaviour that fix the order |
| `06-01` §3 | Which modules — and therefore which entities — exist in each wave |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | The gate at the end of every tier |

| Depended on by |
|---|
| [`DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md`](DM-014_Cutover_Data_Checklist_and_Freeze_Communication.md) — the runsheet is generated from §4.4 · `DM-004`…`DM-010` — each workbook states its tier · `MD-048` §5 · `OP-002` · `CM-012` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Before every cutover**, and at every wave boundary |
| Trigger for out-of-cycle review | A new foreign key in `05-02` · a disposition change in `DM-001` · a module moving wave in `06-01` · a dry run revealing an undeclared dependency |
| Owner | Data Migration Lead, with the Master Data Owner accountable for the `MD-048` seam |
| Change log | `RF-006` |
| Enforcement | `SQ-01`…`SQ-18`; the dry-run gate; `DM-013` per-tier reconciliation |
| Derivation | Tier order is **re-derived from the FK and dependency declarations**, never hand-edited (`SQ-15`, `RG-06`) |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No orchestration specification exists.** `06-03` is absent (`DM-001` `O-01`), so retry semantics, checkpointing, idempotency keys and the batch-failure contract this plan assumes are unspecified. §4.6 states *what* must happen; nothing states *how* | CTO with Platform Engineering | **W1 — before the first dry run** |
| **`O-02`** | **`X9` archive has no mapping workbook for `M24` documents** — 500,000+ paper records at W3–W6 (`DM-001` `O-04`). The sequence position is declared here; the mapping does not exist | Programme Content Lead with Quality Manager | W3 |
| **`O-03`** | **`M19` `Q-02` is unresolved** — whether the chart of accounts is rationalised before migration or migrated as-is. W3 step 2 changes shape entirely depending on the answer, and every downstream finance step inherits it | CFO | **W3 minus 3 months** |
| **`O-04`** | **The cutover window duration is unknown** because no rollback has been rehearsed and no dry run has been run at production volume. `SQ-08` requires a published duration; there is none | Data Migration Lead with CTO | **W1** |
| **`O-05`** | `M64` provides the **quality-assessment gate on every load** at W2 (`M64` §16.4), but tiers `X1`…`X5` load at W1. The gate that is supposed to score each batch before acceptance arrives one wave after the batches it must score | Master Data Owner with CTO | **W1** |
| **`O-06`** | Whether the resident store (`NFR-086`) is available at W1 is unproven — `ASM-21` is explicitly not proven and `D-13` is an open decision blocking W1 architecture. `SQ-10` defers all `S3` steps; if the store slips, party migration completes without identity documents and a second pass is required | CTO with Legal Counsel | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] The `MD-048` seam stated explicitly, in both directions (`SQ-01`)
- [x] Position-fixing constraints reduced to four, so a tier order can be challenged objectively
- [x] Ten migration tiers `X0`…`X9` defined, with dependency and parallelism declared per tier
- [x] Per-wave sequences given for W1–W8, every step traced to the module `§16.4` that requires it
- [x] Archive placed off the critical path and the reason stated
- [x] Computed fields prohibited from being supplied (`SQ-04`) with the `MD-007` `zone_code` case worked
- [x] Control-account gate placed at the tier boundary, not at the end of the wave (`SQ-05`)
- [x] `never_reload` declared for the two datasets where a re-run is worse than a failure
- [x] Rollback order, duration requirement and "partial success is not a state" stated
- [x] Delta handling bound to BRD `MIG-009`, with the `MIG` space qualified (`DM-001` `O-07`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a, `bilingual: no` per `CG-010` §3.2
- [ ] **`O-01` no orchestration specification — the plan assumes a contract that does not exist**
- [ ] **`O-04` cutover window duration unknown — no rehearsed rollback**
- [ ] Named approver recorded — **pending Data Migration Lead with Master Data Owner**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
