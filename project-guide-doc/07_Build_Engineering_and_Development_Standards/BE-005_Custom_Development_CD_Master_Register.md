---
id: BE-005
title: Custom Development (CD) Master Register
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: ERP Design Authority
standards_basis: >
  ISO 10007:2017 §6 (configuration identification) · ISO/IEC/IEEE 24765:2017 (identifier discipline) ·
  RG-01 / RG-02 (allocating authority, permanence) · PG-M13 (single allocating authority)
traces_to: >
  PGD-000 BE-005 · audit H-03 (two incompatible CD registers) · _MODULE_TEMPLATE §0 and §16.2 ·
  02-05 revision note item 5 · Technology Stack Specification §8.2, §25.1.7, §25.3.1 ·
  AR-007 §3.2 · AR-012 FF-16 · RQA-10 · PGD-A2-17
depends_on: GV-003 (D-nnn / CR-nnn spaces) · GV-011 (configuration management) · AR-006 · AR-007
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 12:46 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-005 — Custom Development (CD) Master Register

### Category 07 · Code `BE` · ISO 10007:2017 §6 · RG-01 · RG-02

---

> **This document is the single authoritative allocation of custom-development identifiers for the
> 1000FiX ERP programme.** It supersedes `02-05` §5.2, the Technology Stack Specification §8.2, and
> every provisional `CD` identifier in all 79 delivery-unit specifications. On issue, no other file
> in the workspace allocates a `CD` identifier.

---

## 1. Purpose

Every module specification in the programme carries a §16.2 table that names the custom software
that module needs, and every one of those tables carries the same warning:

> ⚠ CD identifiers are **provisional** until allocated by `02_Architecture/02-05`. **Do not create a
> build backlog item from an identifier in this table until 02-05 has issued it.**

`02-05` never issued them. Under the programme's own governance rule, that sentence means the
1000FiX programme **cannot lawfully create its own build backlog** — not one ticket, for any of the
1,850 person-weeks of custom development the estate names. This document removes that block.

It does three things. It **counts** what the estate actually contains, rather than repeating any
existing register's claim about it. It **issues** a permanent identifier for every custom-development
item, under an allocation scheme that cannot collide. And it **maps** every legacy identifier — from
all four incompatible registers now in circulation — onto the issued set, so that no existing
document becomes unreadable.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The complete enumeration of custom-development items across all 67 modules and all 12 portals |
| 2 | The **identifier standard** — form, allocating authority, permanence, retirement |
| 3 | The **issued register** — 331 items with owner, technical name, scope, type, wave and effort |
| 4 | The **crosswalk** from all four legacy registers to the issued identifiers |
| 5 | The **collision record** — every legacy identifier that denoted more than one component |
| 6 | Effort reconciliation between the register and the `GV-007` build baseline |
| 7 | Items named by the Technology Stack Specification that no delivery unit owns |
| 8 | Allocation, change and retirement governance; the conditions that enable `FF-16` |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| What each component *does* | The owning unit's specification §5–§15; `AR-003` SDD | This register names and identifies; it does not specify behaviour |
| The internal structure of an Odoo module | `AR-007` | Anatomy, inheritance, naming of models and tables |
| Repository placement of the code | `BE-004` | Where a `cd_*` directory lives in the monorepo |
| The artefact set each component ships | `BE-006` | README, runbook, OpenAPI, `component.yaml` |
| Sprint decomposition of a CD item into stories | `BE-008` | This register is the epic layer, not the story layer |
| Effort **method** and calibration | `GV-007` | This register carries the figures; `GV-007` owns how they are derived |
| Wave assignment as a plan | `GV-004` | This register records the wave each unit declares; the schedule is `GV-004`'s |
| Application identifiers `APP-01`…`APP-10` | §7.4 — **retired here** | The applications are portal deliverables and are identified as such |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Every developer** | The identifier that goes in `__manifest__.py`, in the branch name and in the commit scope |
| Product owner / backlog manager | The epic list. Nothing enters the backlog without an issued identifier (`BE-008` `SPR-07`) |
| Solution Architect | The allocation authority; the change route for a new component |
| Implementation vendor | The deliverable breakdown they price and are measured against |
| QA Lead | The unit of coverage reporting — `QA-004` traces tests to CD items |
| CFO / PMO | The reconciliation between the deliverable list and the effort baseline |
| Platform Engineering | `FF-16` cannot be enabled until this register exists; §10 states when it can |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO 10007:2017** | §6.2 Configuration identification | Every configuration item has a unique identifier, an owner, a documented scope and a controlled change route | Full |
| **ISO 10007:2017** | §6.3 Change control | §11.3 defines the raise–evaluate–approve route; a new CD item is a `CR-nnn` under `GV-003` | Full |
| **ISO/IEC/IEEE 24765:2017** | Identifier discipline | An identifier denotes exactly one item, permanently | **This is the clause the estate breaches 48 times.** §5 is the corrective standard |
| `RG-01` | Allocating authority | One authority allocates each space | Full — §11.1 |
| `RG-02` | Permanence | A withdrawn identifier is retired, never reissued | Full — §8.3 |
| `PG-M13` | Single allocating authority for a shared space | **Departure by design.** §5.2 replaces central allocation with a *derivable* scheme, which needs no allocator. The rationale is §4 |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| All 67 module specifications, §16.2 | `../../1000fix_ERP_Module/03_Modules/**/M*.md` | 251 CD rows in the flat scheme, 80 in the module-scoped scheme |
| All 12 portal specifications, §16.2 | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P*.md` | 14 CD rows, `CD-200`…`CD-213` |
| All 79 specifications, §1 Identity | ibid. | The declared **Effort estimate** and **Delivery wave** per unit |
| `02-05` §5.2 | `../../1000fix_ERP_Module/02_Architecture/` | The original `CD-001`…`CD-138` allocation, M01–M30 only |
| `02-05` revision note, item 5 | ibid. | *"A unified CD register covering all 67 modules is required and is not yet written"* |
| Technology Stack Specification §8.2 | `../../primary-doc/` | The 248-item "unified register" — Blocks 1, 2, 3 and `APP-01`…`APP-10` |
| ibid. §25.1.7, §25.3.1 | ibid. | Records the gap and proposes restating "~138 CD items" to 248 |
| `_MODULE_TEMPLATE` §0, §16.2 | `../../1000fix_ERP_Module/03_Modules/` | The provisional-identifier prohibition; the *"48 identifiers currently collide"* claim |
| `_PORTAL_SUITE_AUDIT_REPORT` | ibid. `K_Platform_and_Technology/` | *"CD-214 is the next free identifier… zero collisions against all 67 module files"* |
| `AR-007` §3.2 | `../02_Architecture_and_Design/` | Requires `x_cd_id` in every manifest, **issued** not provisional |
| `AR-012` `FF-16` | ibid. | The CI check that is unsatisfiable until this document exists |
| `GV-007` §4.1 | `../00_Programme_Governance_and_Control/` | The 1,842 PW counted build baseline this register reconciles against |

### 2.3 Audit findings this document closes or advances

| Finding | Source | Disposition |
|---|---|---|
| **`H-03`** — two incompatible CD registers exist | `00-07` | **Superseded and enlarged.** There are **four**, not two — §3.1. Closed by §6 |
| `M-01` / `02-05` rev. item 5 — unified register required | `02-05` | **Closed** — §6 is that register |
| `25.1.7` — the CD register covers 30 of 67 modules | TSS | **Closed** — §6 covers 79 of 79 units |
| `PGD-A2-17` — three identifier schemes for the same documents | `GV-011` | **Advanced** — the CD space is reduced from four schemes to one |
| `RQA-10` — *"31 CD identifiers collide; highest in use CD-214 against a register of 138"* | `PGD-AUDIT-004` | **Corrected.** Counted at 2026-08-18 12:46 (+06): **48** collide; the highest **in use** is `CD-213`; `CD-214` is claimed by no §16.2 row. Raised as `BEA-01` |
| `FF-16` unsatisfiable | `AR-012` §5.3 | **Enabled** — §10 states the conditions and the date |
| `AR-007` `Q-01` — *"When is `BE-005` issued?"* | `AR-007` §13 | **Answered** — this issue |

---

## 3. The Counted Position

**Enumerated 2026-08-18 12:46 (+06)** by reading §16.2 of all 79 delivery-unit specifications and
counting rows whose first column is a `CD` identifier. Per rule `PG-03` no figure below is quoted
from another register.

### 3.1 There are four CD registers in circulation, not two

| # | Register | Where | Covers | Items | Identifier form |
|---|---|---|---|---:|---|
| **R1** | The original allocation | `02-05` §5.2 | M01–M30 only | 138 | `CD-001`…`CD-138` |
| **R2** | The "unified" register | TSS §8.2, Blocks 1–3 + APP | All 67 modules + 10 applications | 248 + 10 | `CD-001`…`CD-248`, `APP-01`…`APP-10` |
| **R3** | The module estate, flat scheme | §16.2 of 66 units | 66 units | **251 rows** | `CD-001`…`CD-213` |
| **R4** | The module estate, scoped scheme | §16.2 of 13 modules | 13 modules | **80 rows** | `CD-C12-01`, `CD-C23-04`, … |

> **R3 and R4 coexist inside the same section of the same document set.** Thirteen modules — `M08`,
> `M09`, `M11`, `M12`, `M23`, `M24`, `M36`, `M37`, `M38`, `M39`, `M40`, `M60`, `M61` — write
> `CD-C12-01`; the other sixty-six write `CD-052`. Both forms appear under the heading
> *"### 16.2 Custom Development"*, in tables with identical columns. A build backlog generated from
> the estate by any mechanical process would produce two incompatible key spaces.

### 3.2 The estate, measured

| Measure | Value |
|---|---:|
| Delivery units with a §16.2 table | **79** (67 modules + 12 portals) |
| Units with **zero** CD rows | **0** |
| **Total CD rows** | **331** |
| Rows in the flat `CD-nnn` scheme | 251 |
| Rows in the module-scoped scheme | 80 |
| **Distinct legacy identifiers in use** | **272** |
| Distinct flat identifiers | 192, spanning `CD-001` … `CD-213` |
| Unused numbers inside that span | **21** — `CD-092`, `CD-096`…`CD-109`, `CD-119`…`CD-124` |
| **Identifiers denoting more than one component** | **48** |
| — of which denote two components | 37 |
| — of which denote three components | 11 |
| **Distinct components sharing a colliding identifier** | **107** |
| Total effort carried by the 331 rows | **1,850 PW** |

**Verification** *(regenerated per `PG-M10` immediately before issue)*: 251 + 80 = **331** ✓ ·
192 distinct flat + 80 scoped = **272** ✓ · (37 × 2) + (11 × 3) = 74 + 33 = **107** ✓.

> **The `_MODULE_TEMPLATE` §0 figure of "48 identifiers currently collide" is exactly right**, and
> has been right for long enough to be printed in the authoring template that every module author
> reads before writing a line. It was never acted on. A defect recorded in the template that
> instructs authors to reproduce it is the estate's most expensive habit.

### 3.3 R3 and R2 disagree about three-quarters of the identifier space

The Technology Stack Specification §8.2 presents itself as the unified register. It is not the
register the estate uses. Comparing every flat identifier used in a §16.2 table against the module
TSS §8.2 assigns it to:

| Comparison | Count | Share |
|---|---:|---:|
| Flat identifiers used by the module estate | 178 | 100% |
| **Agree** with TSS §8.2 Blocks 1–2 | **45** | **25.3%** |
| **Disagree** — TSS assigns the identifier to a different module | **133** | **74.7%** |

Worked examples, each verifiable in one `grep`:

| Identifier | TSS §8.2 assigns it to | The estate's §16.2 tables assign it to |
|---|---|---|
| `CD-141` | `M31` Workshop & Depot Repair | `M41` Warehouse Management |
| `CD-157` | `M36` Quotation & Tender | `M17` **and** `M19` **and** `M29` |
| `CD-194` | `M50` Treasury | `M26` AI/ML Services |
| `CD-207` | `M55` Time & Attendance | `P07` Marketplace Seller Portal |

> **This is the finding that matters commercially.** TSS §25.3.1 asks the CTO to restate the RFP's
> "~138 CD items" to **248**, on the basis that §8.2 is the complete register. §8.2 is a *different*
> register from the one the specifications use — agreeing with it on a quarter of the space, and
> covering 248 items against an estate of 331. Restating the RFP to 248 would replace one wrong
> number with another. **The number is 331.** Raised as `BEA-02`.

### 3.4 The portal block was allocated by a fourth route

`CD-200`…`CD-213` were claimed one at a time by the twelve portal specifications, each file reading
the previous file to find the next free number. `_PORTAL_SUITE_AUDIT_REPORT` records the result
accurately — *"CD-214 is the next free identifier. Verified: zero collisions against all 67 module
files"* — and that verification was true when it was performed.

It is an illustration of why the scheme fails rather than a criticism of the check. The portal
authors verified against the module estate at a moment; TSS §8.2 had meanwhile allocated `CD-200`…
`CD-213` to `M52`, `M53`, `M54`, `M55` and `M56`. **Two correct processes, run against two different
baselines, produced two allocations of the same fourteen numbers.**

---

## 4. Why Sequential Allocation Failed, and Will Fail Again

This section exists because the obvious remedy — renumber everything `CD-001`…`CD-331` and publish
it — reproduces the defect, and the programme has now paid for that mistake five times.

| # | Property of a flat sequential space | Consequence here |
|---|---|---|
| 1 | The next free number is a **function of the whole estate** | An author cannot allocate without reading 79 files, and the answer is stale before they finish |
| 2 | Allocation requires a **round trip to an authority** | `02-05` was that authority and never answered; five months of specifications were written against provisional numbers |
| 3 | Concurrent authors compute the **same** next free number | `CD-200`…`CD-213` allocated twice; `PGD-AUDIT-002` allocated twice within eight minutes by two sessions in this very repository |
| 4 | A re-scope **moves work between owners** but not identifiers | `CD-093`/`CD-094` moved M20 → M53 and the numbers travelled with them, orphaning the M20 rows |
| 5 | The identifier carries **no information** | `CD-157` is unreadable; a reviewer cannot tell that three modules claim it without a lookup |

> **The estate has recorded this failure mode five times** — `H-03` (48 CD collisions), `H2-04`
> (22 colliding KPI identifiers), `RQA-27` (10 double-allocated business-rule identifiers),
> `PGD-A2-27` / `RQA-34` (two audits sharing `PGD-AUDIT-002`), and the portal block above. In every
> case the recommendation was *"create a register and appoint an allocator."* In every case the
> register was not created, because creating it requires the same estate-wide read that allocation
> requires.
>
> **A scheme that needs no allocator cannot fail this way.** That is the change §5 makes.

---

## 5. The Identifier Standard

### 5.1 Form

```
CD-<UNIT>-<nn>
     │       └── two digits, allocated locally within the unit, from 01, never reused
     └────────── the permanent identifier of the owning delivery unit
```

| `<UNIT>` | Meaning | Range in use |
|---|---|---|
| `M01` … `M67` | The owning module | 67 units |
| `P01` … `P12` | The owning portal or application | 12 units |
| `SVC` | A cross-cutting service owned by no single unit | §7.3 — **currently empty by decision** |

**Examples.** `CD-M01-01` is the first custom-development item of M01 Service Request & Order
Management. `CD-P07-02` is the second of the Marketplace Seller Portal. `CD-M53-04` is M53's fourth.

### 5.2 Rules

| # | Rule |
|---|---|
| **`CDR-01`** | A CD identifier has the form `CD-<UNIT>-<nn>`. No other form is valid after this issue |
| **`CDR-02`** | `<UNIT>` is the **permanent** module or portal identifier from `02-02` §5. It is **not** the category letter, **not** the three-letter module code, and does not change when a module is re-categorised or renamed |
| **`CDR-03`** | `<nn>` is allocated by the **owning unit's specification**, sequentially from `01`, and is unique **within that unit only**. No estate-wide read is required to allocate one |
| **`CDR-04`** | Identifiers are **permanent**. A withdrawn item's identifier is retired with a tombstone row in §8.3 and **never reissued** (`RG-02`) |
| **`CDR-05`** | An identifier denotes **exactly one deliverable component**. If a component is split, the original is retired and two new identifiers are allocated |
| **`CDR-06`** | When work moves between units, the identifier **does not move**. The item is retired in the losing unit and re-issued in the gaining unit, with the retirement row naming the successor |
| **`CDR-07`** | Every issued identifier appears in exactly one row of §6, and every row of §6 carries an owner, a type, a wave and an effort figure |
| **`CDR-08`** | An identifier may not appear in a manifest, a branch name, a commit scope, a backlog item or a test case unless it appears in §6 (`AR-007` §3.2, `FF-16`) |
| **`CDR-09`** | The two-digit `<nn>` field caps a unit at 99 items. The largest unit today holds **8**. If a unit needs a hundredth item, the unit is too large and is split under `AR-005`, not renumbered |
| **`CDR-10`** | Legacy identifiers are **read-only aliases** kept for historical traceability (§8). They are never used to create new work |
| **`CDR-11`** | The register is regenerated from the 79 specifications, never edited by hand. A discrepancy between §6 and a §16.2 table is resolved by correcting the specification and regenerating |

> **Why the module number and not the module code.** `02-02` §5 fixes `M11`'s code as `PRC` and
> records that it was `SLS`; `M21` is `HCM` and was `HRM`. TSS §8.2 carries a note correcting both.
> Codes have changed twice; the numbers have never changed. `CDR-02` binds to the stable half.

### 5.3 What the scheme costs

Stated so the trade is visible rather than assumed away.

| Cost | Assessment |
|---|---|
| Identifiers are longer — `CD-M01-01` against `CD-001` | Accepted. Nine characters against six, in exchange for a scheme that cannot collide |
| Every existing document's CD references become legacy | Mitigated by the complete crosswalk in §6 and §8. **No existing file needs editing to remain readable** |
| A component genuinely shared by two modules has one owner and one identifier | This is a feature. `AR-005` requires every capability to have exactly one owning module; a shared CD item was always a boundary defect |
| The register is no longer a single ascending list | Accepted. Ordering is by unit, which is how developers, squads and waves are organised anyway |
| `SVC` reintroduces a central space | Contained: `SVC` is **empty by decision** (§7.3), and any future entry requires Design Authority approval, not local allocation |

---

## 6. The Issued Register

**331 items · 79 delivery units · 1,850 PW · issued 2026-08-18.**

Read the table as follows. **Issued ID** is the identifier to use everywhere from this issue.
**Legacy ID** is what the owning specification's §16.2 currently prints, retained for traceability
only (`CDR-10`). **Wave** is the wave the row or its unit declares; where a row states its own wave
it wins. **PW** is the effort figure the §16.2 row carries — this register **transcribes** effort, it
does not estimate it (`GV-007` `EM-01`).

> **Generated, not transcribed.** The table below was produced mechanically from the 79
> specifications at 2026-08-18 12:46 (+06) under rule `CDR-11`. Scope text is abbreviated to the
> first clause of the source row; the owning specification remains authoritative for behaviour.

#### Category A — Service Delivery & Operations · 7 units · 34 CD items · 206 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M01-01`** | `cd_service_order` | core object, state machine, extensions | Odoo module | W1 | 16 | `CD-001` |
| **`CD-M01-02`** | `cd_diagnostic` | template builder, execution, fault coding | Odoo module | W1 | 8 | `CD-002` |
| **`CD-M01-03`** | `cd_sla` | multi-clock SLA, escalation matrix | Odoo module | W1 | 6 | `CD-003` |
| **`CD-M01-04`** | `cd_rework` | detection, linkage, attribution | Odoo module | W1 | 3 | `CD-004` |
| **`CD-M01-05`** | `cd_service_ext` | business-line extensions | Odoo module | W1 | 7 | `CD-005` |
| **`CD-M01-06`** | — | Service order API layer and tracking read model | Service | W1 | 6 | `CD-006` |
| **`CD-M02-01`** | `cd_dispatch` | scoring, board, assignment, override capture | Odoo module | W2 | 8 | `CD-012` |
| **`CD-M02-02`** | `cd_route` | VROOM/OSRM orchestration, publishing, adherence | Service + module | W2 | 5 | `CD-013` |
| **`CD-M02-03`** | `cd_offline_sync` | journal, replay, conflict resolution | Odoo module + protocol | W2 | 6 | `CD-014` |
| **`CD-M02-04`** | — | Technician mobile application (Flutter) | Mobile app | W2 | 18 | `CD-015` |
| **`CD-M02-05`** | — | cd_geofence + Traccar integration | Odoo module + service | W2 | 3 | `CD-016` |
| **`CD-M03-01`** | `cd_consignment` | consignment, leg, item, state machine | Odoo module | W3 | 6 | `CD-017` |
| **`CD-M03-02`** | `cd_custody` | custody ledger, POD/POC, seal, evidence integrity | Odoo module | W3 | 4 | `CD-018` |
| **`CD-M03-03`** | `cd_courier` | partner registry, booking API, webhook ingestion, reconciliation | Odoo module + service | W3 | 4 | `CD-019` |
| **`CD-M03-04`** | `cd_logistics_charge` | zone/distance charging, entitlement waiver | Odoo module | W3 | 2 | `CD-020` |
| **`CD-M03-05`** | — | Rider mobile application (Flutter) | Mobile app | W3 | 6 | `CD-021` |
| **`CD-M04-01`** | `cd_queue` | token, counter, display, priority, kiosk | Odoo module | W1 | 4 | `CD-022` |
| **`CD-M04-02`** | `cd_cash_drawer` | shift, drawer, movements, variance, deposit | Odoo module | W1 | 4 | `CD-023` |
| **`CD-M04-03`** | `cd_branch_ops` | counter workstation, storage location, checklists, dashboard | Odoo module + frontend | W1 | 5 | `CD-024` |
| **`CD-M05-01`** | `cd_msp_contract` | contract instance, entitlement consumption, coverage window, SLA credit | Odoo module | W5 | 6 | `CD-025` |
| **`CD-M05-02`** | `cd_monitoring` | monitored asset, agent registry, health scoring, coverage gaps | Odoo module + service | W5 | 8 | `CD-026` |
| **`CD-M05-03`** | `cd_alerting` | rules, correlation, de-duplication, escalation, suppression | Service | W5 | 7 | `CD-027` |
| **`CD-M05-04`** | `cd_msp_ticket` | client ticket, contractual SLA, problem, change | Odoo module | W5 | 6 | `CD-028` |
| **`CD-M05-05`** | `cd_remote_session` | consent, session orchestration, metering, recording linkage | Odoo module + service | W5 | 4 | `CD-029` |
| **`CD-M05-06`** | `cd_patch_mgmt` | patch inventory, scheduling, compliance reporting | Odoo module + service | W5 | 6 | `CD-030` |
| **`CD-M06-01`** | `cd_data_case` | case, workspace, access control, methodology log, inventory | Odoo module | W6 | 7 | `CD-031` |
| **`CD-M06-02`** | `cd_media_custody` | dual-control custody, seals, cleanroom booking | Odoo module | W6 | 4 | `CD-032` |
| **`CD-M06-03`** | `cd_destruction_cert` | wipe request, method selection, certificate, gate API, verification endpoint | Odoo module + service | W6 | 5 | `CD-033` |
| **`CD-M06-04`** | — | Backup service management — plan, monitoring, restore test, capacity metering | Odoo module | W6 | 2 | `CD-034` |
| **`CD-M31-01`** | `cd_repair_order` | repair order object, state machine, costing | Odoo module | W2 | 10 | `CD-007` |
| **`CD-M31-02`** | `cd_workshop + cd_bench` | workshop and bench master, allocation, capacity | Odoo module | W2 | 7 | `CD-008` |
| **`CD-M31-03`** | `cd_test_burnin` | test protocols, burn-in scheduling, station management | Odoo module | W2 | 6 | `CD-009` |
| **`CD-M31-04`** | — | WIP board — wall-display web application with auto-refresh | Frontend | W2 | 4 | `CD-010` |
| **`CD-M31-05`** | — | Bench terminal — barcode-first, offline-capable operator interface | Frontend | W2 | 3 | `CD-011` |

#### Category B — Customer Engagement & Experience · 7 units · 31 CD items · 144 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M07-01`** | `cd_account_mgmt` | assignment, eligibility, account plan, stakeholder map, health | Odoo module | W1 | 7 | `CD-040` |
| **`CD-M07-02`** | `cd_qbr` | scheduling, data assembly, bilingual document generation, action tracking | Odoo module + service | W1 | 6 | `CD-041` |
| **`CD-M07-03`** | `cd_sales_forecast` | forecast categories, snapshots, accuracy, renewal pipeline | Odoo module | W1 | 5 | `CD-042` |
| **`CD-M10-01`** | `cd_loyalty` | tiers, membership lifecycle, benefit engine, scope enforcement, points ledger | Odoo module | W2 | 7 | `CD-043` |
| **`CD-M10-02`** | `cd_wallet` | stored value ledger, application, payout | Odoo module | W2 | 3 | `CD-044` |
| **`CD-M10-03`** | `cd_voucher` | generation, eligibility, stacking, fraud controls | Odoo module | W2 | 4 | `CD-045` |
| **`CD-M10-04`** | `cd_referral` | codes, attribution, dual reward, circularity prevention | Odoo module | W2 | 2 | `CD-046` |
| **`CD-M10-05`** | — | Liability and breakage calculation service | Service | W2 | 2 | `CD-047` |
| **`CD-M27-01`** | `cd_conversation` | unified conversation, threading, channel adapters | Odoo module + service | W4 | 8 | `CD-048` |
| **`CD-M27-02`** | `cd_routing` | queues, skills, priority, concurrency, SLA | Odoo module | W4 | 5 | `CD-049` |
| **`CD-M27-03`** | `cd_agent_desktop` | screen pop, unified workspace, in-conversation actions | Frontend + module | W4 | 7 | `CD-050` |
| **`CD-M27-04`** | `cd_notification` | intent API, classification, consent/DND/quiet-hours enforcement, templates, delivery tr… | Service + module | W4 | 9 | `CD-051` |
| **`CD-M27-05`** | `cd_quality_monitor` | recording linkage, evaluation, calibration, coaching | Odoo module | W4 | 3 | `CD-052` |
| **`CD-M32-01`** | `cd_assistant` | session, turn pipeline, dialogue management, context | Service | W4 | 5 | `CD-053` |
| **`CD-M32-02`** | `cd_intent` | taxonomy, classification, entity extraction, Bengali handling | Service | W4 | 4 | `CD-054` |
| **`CD-M32-03`** | `cd_grounding` | retrieval, citation, freshness, no-answer behaviour | Service | W4 | 4 | `CD-055` |
| **`CD-M32-04`** | `cd_guardrail` | input validation, output filtering, scope, safety, audit | Service | W4 | 3 | `CD-056` |
| **`CD-M32-05`** | `cd_assistant_actions` | authenticated action execution and authority matrix | Service | W4 | 2 | `CD-057` |
| **`CD-M33-01`** | `cd_party_master` | party, roles, status, search, 360 read model | Odoo module + service | W1 | 8 | `CD-035` |
| **`CD-M33-02`** | `cd_party_hierarchy` | group structure, corporate contacts, approval chain | Odoo module | W1 | 4 | `CD-036` |
| **`CD-M33-03`** | `cd_consent` | consent record, notice versioning, evaluation API, rights requests, processing record | Odoo module + service | W1 | 7 | `CD-037` |
| **`CD-M33-04`** | `cd_bd_address` | administrative hierarchy, GPS, zone derivation | Odoo module | W1 | 3 | `CD-038` |
| **`CD-M33-05`** | `cd_identity_doc` | residency-controlled document capture and access | Odoo module + resident adapter | W1 | 2 | `CD-039` |
| **`CD-M34-01`** | `cd_voc` | survey triggers, sampling, fatigue, scoring, attribution, integrity | Odoo module | W4 | 6 | `CD-058` |
| **`CD-M34-02`** | `cd_closed_loop` | detractor detection, loop case, contact tracking, closure verification, escalation | Odoo module | W4 | 4 | `CD-059` |
| **`CD-M34-03`** | `cd_complaint` | customer-facing complaint case, acknowledgement, updates, remedy, M23 linkage | Odoo module | W4 | 5 | `CD-060` |
| **`CD-M34-04`** | `cd_journey` | journey definition, measurement, driver and verbatim analysis | Odoo module + service | W4 | 2 | `CD-061` |
| **`CD-M35-01`** | `cd_campaign` | campaign, approval, scheduling, capacity check, budget, emergency stop | Odoo module | W5 | 5 | `CD-062` |
| **`CD-M35-02`** | `cd_journey_orchestration` | journey design, instance state, conflict priority, exit handling | Odoo module + service | W5 | 5 | `CD-063` |
| **`CD-M35-03`** | `cd_attribution` | touchpoint capture, multi-touch model, holdout, incremental measurement | Service | W5 | 4 | `CD-064` |
| **`CD-M35-04`** | `cd_content` | content library, versioning, approval, bilingual validation, ad placements | Odoo module | W5 | 3 | `CD-065` |

#### Category C — Commercial, Pricing & Revenue · 9 units · 57 CD items · 262 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M08-01`** | `cd_contract_engine` | contract object, template binding, versioning, families, amendment, suspension, termina… | Odoo module | W4 | 9 | `CD-C08-01` |
| **`CD-M08-02`** | `cd_entitlement` | definition, movement ledger, balance read model, check API, exhaustion treatment | Odoo module + service | W4 | 8 | `CD-C08-02` |
| **`CD-M08-03`** | `cd_contract_sla` | contractual SLA, precedence, attainment computation, service credit scheme | Odoo module | W4 | 5 | `CD-C08-03` |
| **`CD-M08-04`** | `cd_contract_renewal` | lead-time triggers, renewal pipeline, escalation ladder, churn record | Odoo module | W4 | 4 | `CD-C08-04` |
| **`CD-M08-05`** | `cd_contract_profitability` | cost-to-serve accrual, margin computation, alerting | Odoo module | W4 | 3 | `CD-C08-05` |
| **`CD-M08-06`** | — | Preventive and obligation scheduler, contract API layer | Service | W4 | 3 | `CD-C08-06` |
| **`CD-M09-01`** | `cd_warranty_register` | unified register, entitlement verdict engine, precedence, void, transfer | Odoo module + service | W4 | 7 | `CD-C09-01` |
| **`CD-M09-02`** | `cd_protection_plan` | seven families, eligibility, inspection, policy issue, limits, reserve, loss ratio | Odoo module | W4 | 8 | `CD-C09-02` |
| **`CD-M09-03`** | `cd_claim_engine` | claim creation, evidence pack assembly, brand rule engine, validation, valuation | Odoo module + service | W4 | 9 | `CD-C09-03` |
| **`CD-M09-04`** | `cd_brand_recovery` | submission adapters, deadline scheduler, decisions, appeals, ageing and chasing | Odoo module + service | W4 | 6 | `CD-C09-04` |
| **`CD-M09-05`** | `cd_claim_reconciliation` | remittance matching, period reconciliation, write-off governance, brand scorecard | Odoo module | W4 | 4 | `CD-C09-05` |
| **`CD-M09-06`** | — | P08 Brand Partner Portal domain services and brand-scoped API | Service | W4 | 2 | `CD-C09-06` |
| **`CD-M11-01`** | `cd_pricing_engine` | resolution engine, access sequences, explanation trace, price lock, rule-set versioning | Odoo module + service | W3 | 8 | `CD-C11-01` |
| **`CD-M11-02`** | `cd_rate_card` | labour, brand, contract and marketplace rate cards with versioning | Odoo module | W3 | 4 | `CD-C11-02` |
| **`CD-M11-03`** | `cd_discount_governance` | bands, floors, approval routing, override log, exception reporting | Odoo module | W3 | 4 | `CD-C11-03` |
| **`CD-M11-04`** | — | Pricing API, public indicative endpoint, caching and invalidation | Service | W3 | 2 | `CD-C11-04` |
| **`CD-M11-05`** | `cd_price_experiment` | A/B framework with guardrails and evaluation | Odoo module | W7 | 3 | `CD-C11-05` |
| **`CD-M11-06`** | `cd_dynamic_pricing` | signal ingestion, corridor engine, guardrails, kill switch | Odoo module + service | W7 | 5 | `CD-C11-06` |
| **`CD-M12-01`** | `cd_seller_onboarding` | registration, KYC at T5, verification, agreement, tiers, approval workflow | Odoo module + service | W7 | 8 | `CD-C12-01` |
| **`CD-M12-02`** | `cd_listing` | service and product listings, moderation pipeline, prohibited items, seller stock | Odoo module | W7 | 7 | `CD-C12-02` |
| **`CD-M12-03`** | `cd_job_broadcast` | eligibility, matching, ranking, broadcast fan-out, bidding, award, reassignment, data-g… | Odoo module + service | W7 | 10 | `CD-C12-03` |
| **`CD-M12-04`** | `cd_seller_performance` | evidence parity, scorecard, consequence ladder, probation, appeals, reviews | Odoo module | W7 | 7 | `CD-C12-04` |
| **`CD-M12-05`** | `cd_dispute` | dispute workflow, mediation, remedy execution, recovery, fund blocking | Odoo module | W7 | 6 | `CD-C12-05` |
| **`CD-M12-06`** | `cd_seller_settlement` | commission schemes, wallet ledger, hold periods, payout instruction, statements | Odoo module + service | W7 | 7 | `CD-C12-06` |
| **`CD-M12-07`** | `cd_seller_ads` | boost, top-listing, advertising placements and reporting | Odoo module | W7 | 3 | `CD-C12-07` |
| **`CD-M12-08`** | — | Trust and safety — off-platform, collusion and manipulation detection with investigatio… | Service | W7 | 2 | `CD-C12-08` |
| **`CD-M36-01`** | `cd_estimate` | estimate object, diagnostic pre-population, cost build-up, availability signalling | Odoo module | W3 | 5 | `CD-C36-01` |
| **`CD-M36-02`** | `cd_quotation` | versioning, options, alternatives, terms, bilingual document generation | Odoo module | W3 | 6 | `CD-C36-02` |
| **`CD-M36-03`** | `cd_approval_loop` | internal approval routing and the multi-channel customer approval loop with evidence se… | Odoo module + service | W3 | 5 | `CD-C36-03` |
| **`CD-M36-04`** | — | Tokenised public approval surface (Bengali, 3G-optimised, one screen) | Service + front end | W3 | 2 | `CD-C36-04` |
| **`CD-M36-05`** | `cd_tender` | tender register, compliance matrix, document pack, bid security | Odoo module | W3 | 3 | `CD-C36-05` |
| **`CD-M36-06`** | `cd_quote_analytics` | conversion, turnaround, loss reason and variance reporting | Odoo module | W3 | 1 | `CD-C36-06` |
| **`CD-M37-01`** | `cd_catalogue` | unified item master, typed extensions, lifecycle, bitemporal history | Odoo module | W1 | 7 | `CD-C37-01` |
| **`CD-M37-02`** | `cd_service_product` | service definition, delivery modes, skills, durations, templates | Odoo module | W1 | 4 | `CD-C37-02` |
| **`CD-M37-03`** | `cd_repair_bom` | operations, rBOM, SRT, explosion engine, calibration workflow | Odoo module | W1 | 6 | `CD-C37-03` |
| **`CD-M37-04`** | `cd_fault_taxonomy` | symptom/fault/root-cause tree with brand mapping | Odoo module | W1 | 2 | `CD-C37-04` |
| **`CD-M37-05`** | `cd_catalogue_publish` | channel projections, completeness scoring, publication events | Odoo module | W1 | 3 | `CD-C37-05` |
| **`CD-M37-06`** | — | Catalogue read API, search index and resolution service | Service | W1 | 2 | `CD-C37-06` |
| **`CD-M38-01`** | `cd_commerce_api` | headless commerce API, catalogue read model, search index, tokenised public surfaces | Service | W7 | 6 | `CD-C38-01` |
| **`CD-M38-02`** | `cd_cart_checkout` | persistent mixed cart, checkout state machine, idempotent placement, payment orchestrat… | Odoo module + service | W7 | 8 | `CD-C38-02` |
| **`CD-M38-03`** | `cd_service_booking_commerce` | bookable services, slot reservation, service-order creation, plan and rental commerce | Odoo module | W7 | 5 | `CD-C38-03` |
| **`CD-M38-04`** | `cd_returns_rma` | return policy, RMA lifecycle, inspection, disposition, refund instruction, fraud scoring | Odoo module | W7 | 5 | `CD-C38-04` |
| **`CD-M38-05`** | `cd_merchandising` | collections, content, cross-sell, reviews, stock exposure policy | Odoo module | W7 | 3 | `CD-C38-05` |
| **`CD-M38-06`** | — | Storefront front-end integration and performance engineering *(with the P01 team)* | Front end | W7 | 3 | `CD-C38-06` |
| **`CD-M39-01`** | `cd_subscription_engine` | subscription object, amendment model, schedule generation, state machine | Odoo module | W4 | 6 | `CD-C39-01` |
| **`CD-M39-02`** | `cd_proration` | daily-rate proration, credit treatment, backdating, explanations | Odoo module | W4 | 4 | `CD-C39-02` |
| **`CD-M39-03`** | `cd_usage_rating` | ingestion, deduplication, tariff engine, rerating, exception queue | Odoo module + service | W4 | 5 | `CD-C39-03` |
| **`CD-M39-04`** | — | Billing run orchestrator — dry run, resumable commit, idempotent instruction to M20 | Service | W4 | 4 | `CD-C39-04` |
| **`CD-M39-05`** | `cd_recurring_metrics` | MRR, ARR, movement decomposition, churn, cohorts | Odoo module | W4 | 2 | `CD-C39-05` |
| **`CD-M39-06`** | `cd_dunning_bridge` | M20 dunning signal to subscription state policy | Odoo module | W4 | 1 | `CD-C39-06` |
| **`CD-M40-01`** | `cd_partner_program` | partner spine, typed extensions, programmes, tiers, onboarding, standing, exit | Odoo module | W7 | 5 | `CD-C40-01` |
| **`CD-M40-02`** | — | Brand authorisation register, expiry scheduler, obligation and audit tracking, work gat… | Odoo module | W7 | 4 | `CD-C40-02` |
| **`CD-M40-03`** | `cd_referral` | links, codes, lead submission with consent, attribution model and window | Odoo module | W7 | 3 | `CD-C40-03` |
| **`CD-M40-04`** | `cd_deal_registration` | registration, conflict detection, protection periods, channel precedence | Odoo module | W7 | 3 | `CD-C40-04` |
| **`CD-M40-05`** | `cd_partner_performance` | health scoring with factor decomposition, enablement, communications, analytics | Odoo module | W7 | 2 | `CD-C40-05` |
| **`CD-M40-06`** | `cd_franchise` | territory, fees, royalties, standards, benchmarking; plus MDF fund ledger and claims | Odoo module | W7 | 2 | `CD-C40-06` |
| **`CD-M40-07`** | — | P12 portal domain services and partner-scoped API | Service | W7 | 1 | `CD-C40-07` |

#### Category D — Circular & Asset-Based Business · 3 units · 11 CD items · 60 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M13-01`** | `cd_rental_asset` | fleet register, category and spec model, kits, status lifecycle, availability engine, u… | Odoo module | W6 | 8 | `CD-059` |
| **`CD-M13-02`** | `cd_rental_agreement` | reservation, allocation, agreement, eligibility and exposure, variation, framework call… | Odoo module | W6 | 7 | `CD-060` |
| **`CD-M13-03`** | `cd_condition_report` | mobile capture with offline queue, forced photography, hashing, side-by-side comparison… | Odoo module + mobile | W6 | 6 | `CD-061` |
| **`CD-M13-04`** | `cd_rental_billing` | rate ladder engine, deposit instruction and offset, waiver, metered usage, late charges… | Odoo module | W6 | 4 | `CD-062` |
| **`CD-M14-01`** | `cd_tradein` | request intake, valuation engine and curve, offer lifecycle, provenance and NEIR verifi… | Odoo module + service | W6 | 7 | `CD-063` |
| **`CD-M14-02`** | `cd_refurb` | work order, standard scope by class, cost accumulation, rework control, destruction gat… | Odoo module | W6 | 6 | `CD-064` |
| **`CD-M14-03`** | `cd_grading` | grading standard versioning, QA protocol execution, battery-health capture, determinist… | Odoo module | W6 | 5 | `CD-065` |
| **`CD-M14-04`** | `cd_resale` | refurbished stock class, grade-based pricing, ageing and markdown, disclosure report ge… | Odoo module | W6 | 4 | `CD-066` |
| **`CD-M18-01`** | `cd_ewaste` | collection channels and points, item record, triage and disposition log, destruction ga… | Odoo module | W8 | 6 | `CD-080` |
| **`CD-M18-02`** | `cd_recycling` | partner register with certification currency and downstream declarations, batch assembl… | Odoo module | W8 | 4 | `CD-081` |
| **`CD-M18-03`** | `cd_esg_report` | regulatory register, statutory returns with EPR target tracking, versioned factor sets,… | Odoo module | W8 | 3 | `CD-082` |

#### Category E — Supply Chain & Inventory · 6 units · 25 CD items · 119 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M15-01`** | `cd_stock_ext` | location hierarchy, status model, movement ledger, transfer lifecycle, negative-stock g… | Odoo module | W2 | 6 | `CD-068` |
| **`CD-M15-02`** | `cd_stock_ownership` | the six ownership classes, use-permission engine, class-change control, consignment bal… | Odoo module | W2 | 8 | `CD-069` |
| **`CD-M15-03`** | `cd_cycle_count` | ABC-driven scheduling, blind counting, variance thresholds, adjustment approval with SoD | Odoo module | W2 | 3 | `CD-070` |
| **`CD-M15-04`** | `cd_van_stock_control` | van locations, par levels, replenishment triggers, offline shift reconciliation, varian… | Odoo module + technician-app surface | W2 | 6 | `CD-139` |
| **`CD-M15-05`** | `cd_part_availability` | network availability search, reservation priority engine, substitution and backorder | Odoo module + service | W2 | 4 | `CD-140` |
| **`CD-M16-01`** | `cd_requisition` | multi-source demand intake, authority-matrix routing, delegation and escalation, low-va… | Odoo module | W3 | 5 | `CD-146` |
| **`CD-M16-02`** | `cd_rfq` | RFQ issue, portal response capture, normalised bid comparison, award with rationale | Odoo module | W3 | 4 | `CD-073` |
| **`CD-M16-03`** | `cd_sourcing_event` | sealed bid, reverse auction, approved-source list, sourcing decision rules, immutable e… | Odoo module | W3 | 3 | `CD-147` |
| **`CD-M16-04`** | `cd_three_way_match` | tolerance sets, match engine, exception classification and routing, duplicate detection… | Odoo module + service | W3 | 6 | `CD-148` |
| **`CD-M41-01`** | `cd_wms_structure` | warehouse, zone, bin master, capacity model, storage categories, slotting and re-slotti… | Odoo module | W3 | 4 | `CD-141` |
| **`CD-M41-02`** | `cd_wms_inbound` | inbound lifecycle, scan receipt, inspection execution, directive engine, cross-dock, ha… | Odoo module | W3 | 6 | `CD-142` |
| **`CD-M41-03`** | `cd_wms_outbound` | outbound queue, wave templates and engine, pick strategies, path sequencing, packing, s… | Odoo module | W3 | 6 | `CD-143` |
| **`CD-M41-04`** | `cd_wms_rf` | RF mobile application (Android, Bengali-first, offline-tolerant, scan-verified) | Mobile app | W3 | 5 | `CD-144` |
| **`CD-M41-05`** | `cd_wms_labour` | task model, assignment and interleaving, equipment constraints, time standards, product… | Odoo module | W3 | 1 | `CD-145` |
| **`CD-M42-01`** | `cd_vendor_ext` | supplier profile, classification, segmentation, category coverage, contacts, supplier 3… | Odoo module | W4 | 4 | `CD-072` |
| **`CD-M42-02`** | `cd_supplier_qualification` | questionnaires, scoring, approval workflow, activation gate service, validity and expir… | Odoo module + service | W4 | 6 | `CD-149` |
| **`CD-M42-03`** | `cd_supplier_scorecard` | fact ingestion, weighted scoring models, publication, review cycle, corrective actions,… | Odoo module | W4 | 4 | `CD-150` |
| **`CD-M42-04`** | `cd_supplier_risk` | risk assessment, concentration and single-source analysis, continuity requirements, cat… | Odoo module | W4 | 2 | `CD-151` |
| **`CD-M43-01`** | `cd_demand_plan` | history assembly, adjustment overlays, readiness gate, demand-stream separation, segmen… | Odoo module + service | W6 | 7 | `CD-152` |
| **`CD-M43-02`** | `cd_replenishment_policy` | service-level targets, lead-time modelling, safety-stock and reorder-parameter calculat… | Odoo module + service | W6 | 6 | `CD-153` |
| **`CD-M43-03`** | `cd_network_balance` | network stocking policy, multi-echelon logic, rebalancing proposals, van par optimisati… | Odoo module + service | W6 | 4 | `CD-154` |
| **`CD-M44-01`** | `cd_import_order` | import consignment lifecycle, proforma reconciliation, incoterm model, shipment and doc… | Odoo module | W6 | 5 | `CD-074` |
| **`CD-M44-02`** | `cd_trade_compliance` | HS classification with change control, tariff rate schedule, restriction and permit che… | Odoo module | W6 | 4 | `CD-155` |
| **`CD-M44-03`** | `cd_customs_clearance` | LCA form, letter of credit lifecycle with amendments and discrepancies, alternative pay… | Odoo module + service | W6 | 6 | `CD-156` |
| **`CD-M44-04`** | `cd_landed_cost` | cost factor model, allocation by value/weight/volume/quantity/direct, recoverable/inven… | Odoo module + service | W6 | 4 | `CD-071` |

#### Category F — Asset, Equipment & Facilities · 5 units · 22 CD items · 114 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M17-01`** | `cd_asset_registry` | asset identity, population, lifecycle state machine, configuration, relationships, acce… | Odoo module | W2 | 7 | `CD-075` |
| **`CD-M17-02`** | `cd_asset_identity` | multi-identifier model, validation, resolution client, duplicate detection, controlled… | Odoo module + L4 service | W2 | 7 | `CD-157` |
| **`CD-M17-03`** | `cd_asset_estate` | estate hierarchy, placement history, bulk load, reconciliation engine, portal surface,… | Odoo module | W2 | 5 | `CD-076` |
| **`CD-M17-04`** | `cd_asset_genealogy` | service-history projection, part and component genealogy, fault history, repeat-fault d… | Odoo module | W2 | 5 | `CD-158` |
| **`CD-M17-05`** | `cd_maintenance_plan` | plan definition, elapsed/usage/condition triggers, due-work generation, adherence repor… | Odoo module | W2 | 2 | `CD-077` |
| **`CD-M45-01`** | `cd_equipment_register` | equipment record, classification, measurement-critical flag, tagging, fixed-asset linka… | Odoo module | W5 | 5 | `CD-159` |
| **`CD-M45-02`** | `cd_tool_custody` | scan-based issue and return, custody states and chain, personal and job-linked issue, o… | Odoo module + technician-app surface | W5 | 5 | `CD-160` |
| **`CD-M45-03`** | `cd_calibration` | calibration profiles, schedule, execution with as-found/as-left, traceability chain, ce… | Odoo module + service | W5 | 8 | `CD-161` |
| **`CD-M45-04`** | `cd_equipment_maintenance` | PM plans, corrective routing to M31, availability state, downtime, physical verificatio… | Odoo module + auditor-app surface | W5 | 4 | `CD-162` |
| **`CD-M46-01`** | `cd_vehicle_ext` | vehicle record extension, class profiles, ownership basis, availability state machine,… | Odoo module | W5 | 4 | `CD-163` |
| **`CD-M46-02`** | `cd_vehicle_compliance` | statutory document register, class-driven requirements, expiry alerting, automatic off-… | Odoo module | W5 | 6 | `CD-164` |
| **`CD-M46-03`** | `cd_fuel_and_running_cost` | fuel capture, exception rule engine, odometer reconciliation, telematics device registe… | Odoo module + service | W5 | 6 | `CD-165` |
| **`CD-M46-04`** | `cd_driver_management` | driver register, licence validity gating, assignment and handover, pre-use check surfac… | Odoo module + driver-app surface | W5 | 4 | `CD-166` |
| **`CD-M47-01`** | `cd_site_register` | site record, type profiles, zones, status lifecycle, portfolio view and map, occupancy,… | Odoo module | W7 | 6 | `CD-167` |
| **`CD-M47-02`** | `cd_lease_admin` | lease record, lease abstraction into dated events, critical-date engine, renewal decisi… | Odoo module | W7 | 5 | `CD-168` |
| **`CD-M47-03`** | `cd_facility_work_order` | facility request, triage and SLA, assignment to internal or vendor, completion and veri… | Odoo module + vendor-portal surface | W7 | 6 | `CD-169` |
| **`CD-M47-04`** | `cd_site_compliance` | compliance item register, site-type requirement sets, licence dependency graph, expiry… | Odoo module + auditor-app surface | W7 | 3 | `CD-170` |
| **`CD-M48-01`** | `cd_stream_registry` | stream and device registry, signal model, provisioning and credential rotation, collect… | Odoo module + service | W8 | 5 | `CD-171` |
| **`CD-M48-02`** | `cd_telemetry` | protocol adapters (MQTT/Sparkplug B, HTTPS, file, OPC UA, SNMP, telematics), validation… | Standalone collector service + Odoo module | W8 | 8 | `CD-078` |
| **`CD-M48-03`** | `cd_alert_rules` | rule definition, stream evaluation, hysteresis and dwell, alert lifecycle, deduplicatio… | Odoo module + evaluation service | W8 | 5 | `CD-172` |
| **`CD-M48-04`** | `cd_asset_health` | composite health index, banding and trend, contributing-factor exposure, publication to… | Odoo module | W8 | 3 | `CD-079` |
| **`CD-M48-05`** | `cd_predictive_action` | model application through the M26 gateway, model governance at the point of use, RUL, p… | Odoo module + service | W8 | 5 | `CD-173` |

#### Category G — Finance & Treasury · 8 units · 41 CD items · 197 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M19-01`** | `cd_gl_ext` | seven-dimension model on the journal line, cross-validation rules, control-account prot… | Odoo module | W3 | 7 | `CD-157` |
| **`CD-M19-02`** | `cd_subledger_posting` | the event inbox, posting-rule engine, rule versioning, fixtures, idempotency and unmapp… | Odoo module + service | W3 | 9 | `CD-158` |
| **`CD-M19-03`** | `cd_multi_entity_consolidation` | intercompany balancing and reconciliation, entity roll-up, elimination rules, consolida… | Odoo module | W3 | 5 | `CD-159` |
| **`CD-M19-04`** | `cd_financial_statements_bd` | Bangladesh statutory statement formats, July–June calendar, Bengali rendering, notes an… | Odoo module | W3 | 4 | `CD-160` |
| **`CD-M19-05`** | `cd_close_checklist` | close task model, dependencies, ownership, evidence, sign-off, elapsed-time tracking, s… | Odoo module | W3 | 3 | `CD-089` |
| **`CD-M20-01`** | `cd_billing_engine` | billable-event contract and queue, invoice assembly across sources, bilingual rendering… | Odoo module + service | W3 | 8 | `CD-090` |
| **`CD-M20-02`** | `cd_ar_ext` | open-item ledger, ageing with immutable snapshots, credit profile, credit limits and ho… | Odoo module | W3 | 5 | `CD-161` |
| **`CD-M20-03`** | `cd_receipt_matching` | multi-tender capture, channel clearing model, auto-match scoring engine, allocation, un… | Odoo module + service | W3 | 6 | `CD-162` |
| **`CD-M20-04`** | `cd_credit_note_refund` | credit-note request and approval with reason taxonomy, statutory document, refund autho… | Odoo module | W3 | 3 | `CD-163` |
| **`CD-M20-05`** | `cd_dunning` | segment-specific ladders, suppression rules, collections worklist, promises, disputes,… | Odoo module | W3 | 4 | `CD-095` |
| **`CD-M49-01`** | `cd_fixed_asset_ext` | register extensions (custodianship, tagging, componentisation), movements as immutable… | Odoo module + mobile surface | W5 | 6 | `CD-088` |
| **`CD-M49-02`** | `cd_capex_approval` | capital request and business case, authority matrix, budget consumption against M54, ca… | Odoo module | W5 | 4 | `CD-180` |
| **`CD-M49-03`** | `cd_asset_depreciation_bd` | dual-book depreciation, Third Schedule tax book with initial and accelerated allowances… | Odoo module | W5 | 4 | `CD-181` |
| **`CD-M49-04`** | `cd_cwip` | CWIP accumulation from multiple cost sources, ageing and escalation, allocation basis a… | Odoo module | W5 | 2 | `CD-182` |
| **`CD-M50-01`** | `cd_cash_position` | consolidated cash position across all cash forms, real-time composition, entity and bra… | Odoo module + service | W3 | 3 | `CD-087` |
| **`CD-M50-02`** | `cd_bank_account_mgmt` | bank and account master, mandates and signatories with change control, purpose segregat… | Odoo module | W3 | 2 | `CD-167` |
| **`CD-M50-03`** | `cd_bank_reconciliation` | statement validation and ingestion, layered matching engine with versioned rules, excep… | Odoo module + service | W3 | 6 | `CD-168` |
| **`CD-M50-04`** | `cd_branch_cash_control` | shift consolidation across 51+ counters, shift-open blocking gate, variance escalation,… | Odoo module + service | W3 | 6 | `CD-169` |
| **`CD-M50-05`** | `cd_gateway_settlement` | provider configuration, settlement file ingestion, three-way matching, fee separation,… | Odoo module + service | W3 | 5 | `CD-170` |
| **`CD-M50-06`** | `cd_cashflow_forecast` | direct 13-week forecast generation from AR/AP/payroll/settlement/facility inputs, versi… | Odoo module | W3 | 3 | `CD-171` |
| **`CD-M50-07`** | `cd_trade_finance` | LC and guarantee lifecycle, margin and limit consumption, amendments, expiry alerting,… | Odoo module | W3 | 3 | `CD-172` |
| **`CD-M51-01`** | `cd_tax_engine_bd` | determination service, rule model, effective-dated evaluation, country-pack versioning… | Odoo module + service | W4 | 7 | `CD-173` |
| **`CD-M51-02`** | `cd_mushak` | statutory document formats as versioned data, sequence control, issuance timing rules,… | Odoo module | W4 | 5 | `CD-083` |
| **`CD-M51-03`** | `cd_vat_register` | registers 6.1, 6.2, 6.2.1, 6.5, 6.6, 6.7, 6.8; append-and-lock; register-to-ledger reco… | Odoo module | W4 | 5 | `CD-084` |
| **`CD-M51-04`** | `cd_vat_return` | Mushak 9.1 compilation from locked registers, variance analysis, approval, filing, ackn… | Odoo module | W4 | 4 | `CD-174` |
| **`CD-M51-05`** | `cd_tds` | TDS and VDS determination by section and service code, payee type and PSR conditions, d… | Odoo module | W4 | 5 | `CD-085` |
| **`CD-M51-06`** | `cd_nid` | high-value cash threshold rule, NID capture contract for M20/M04, encrypted storage, ev… | Odoo module | W4 | 1 | `CD-086` |
| **`CD-M51-07`** | `cd_income_tax_schedules` | Third Schedule tax depreciation book, taxable income computation, disallowances, advanc… | Odoo module | W4 | 3 | `CD-175` |
| **`CD-M52-01`** | `cd_ap_ext` | three-way and two-way matching engine, tolerance sets, typed exceptions with payment-le… | Odoo module + service | W3 | 8 | `CD-164` |
| **`CD-M52-02`** | `cd_payment_run` | proposal, review, three-person release, TDS/VDS gate, method selection, bank-detail cha… | Odoo module | W3 | 6 | `CD-165` |
| **`CD-M52-03`** | `cd_expense_claim` | mobile offline capture with receipt hashing and geotagging, policy rules engine, job at… | Odoo module + technician-app surface | W3 | 5 | `CD-166` |
| **`CD-M53-01`** | `cd_performance_obligation` | revenue contract construction, obligation identification and templates, warranty classi… | Odoo module + service | W4 | 6 | `CD-176` |
| **`CD-M53-02`** | `cd_revenue_recognition` | schedule generation and versioning, recognition runs, over-time/point-in-time/milestone… | Odoo module + service | W4 | 7 | `CD-093` |
| **`CD-M53-03`** | `cd_commission_ledger` | commission calculation from M12 scheme versions, ledger, differential recalculation, re… | Odoo module | W4 | 5 | `CD-177` |
| **`CD-M53-04`** | `cd_settlement` | settlement cycles, statements with the deduction hierarchy, three-way reconciliation, d… | Odoo module + service | W7 | 5 | `CD-094` |
| **`CD-M53-05`** | `cd_payout_engine` | payout runs, hold rules and authority, withholding integration, M50 instruction batchin… | Odoo module | W7 | 3 | `CD-178` |
| **`CD-M53-06`** | `cd_escrow` | escrow ledger, purpose-designated account binding, reserve policy and release schedule,… | Odoo module | W7 | 2 | `CD-179` |
| **`CD-M54-01`** | `cd_cost_allocation` | cost centre and element model, pooling, driver sourcing, direct/step-down/reciprocal/ac… | Odoo module + service | W6 | 7 | `CD-183` |
| **`CD-M54-02`** | `cd_job_costing` | job and contract cost accumulation, fully loaded activity rates, plan-to-actual absorpt… | Odoo module + service | W6 | 6 | `CD-184` |
| **`CD-M54-03`** | `cd_budget_ext` | budget model with versions and scenarios, top-down/bottom-up workflow, locking, capital… | Odoo module | W6 | 5 | `CD-185` |
| **`CD-M54-04`** | `cd_fpa_forecast` | driver-based rolling forecast, scenario modelling, variance identification and explanat… | Odoo module + service | W6 | 4 | `CD-186` |

#### Category H — People & Workforce · 7 units · 26 CD items · 124 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M21-01`** | `cd_hr_core` | employee, contract versioning, effective dating, movements, lifecycle | Odoo module | W5 | 7 | `CD-066` |
| **`CD-M21-02`** | `cd_org_structure` | org units, job architecture, positions, assignments, delegation | Odoo module | W5 | 4 | `CD-067` |
| **`CD-M21-03`** | `cd_employee_ess` | employee and manager self-service | Frontend + module | W5 | 4 | `CD-068` |
| **`CD-M21-04`** | `cd_hr_documents` | appointment letter, identity card, service book, bilingual generation | Odoo module | W5 | 3 | `CD-069` |
| **`CD-M22-01`** | `cd_competency` | competency framework, role requirements, skill matrix, assessment, gap analysis, covera… | Odoo module | W5 | 6 | `CD-084` |
| **`CD-M22-02`** | `cd_certification` | certification register, expiry, renewal, lapse handling, eligibility service and overri… | Odoo module | W5 | 6 | `CD-085` |
| **`CD-M22-03`** | `cd_training_ops` | needs generation, plan, budget, vendor, effectiveness, evidence file | Odoo module | W5 | 4 | `CD-086` |
| **`CD-M55-01`** | `cd_attendance` | capture, geofence, derived attendance, exceptions, valuation, period lock | Odoo module + service | W5 | 7 | `CD-070` |
| **`CD-M55-02`** | `cd_leave` | types, entitlement, accrual, coverage check, balance projection | Odoo module | W5 | 4 | `CD-071` |
| **`CD-M55-03`** | `cd_roster` | shift patterns, roster construction, publication, change control, on-call | Odoo module | W5 | 5 | `CD-072` |
| **`CD-M55-04`** | `cd_capacity` | availability projection, skill tagging, capacity forecast | Service | W5 | 3 | `CD-073` |
| **`CD-M55-05`** | `cd_overtime` | request, pre-approval, budget, statutory limit enforcement | Odoo module | W5 | 2 | `CD-074` |
| **`CD-M55-06`** | — | Biometric device adapter and health monitoring | Service | W5 | 1 | `CD-075` |
| **`CD-M56-01`** | `cd_payroll_bd` | engine, elements, sequence, balances, proration, retro, run lifecycle | Odoo module | W5 | 9 | `CD-076` |
| **`CD-M56-02`** | `cd_statutory_bd` | versioned statutory pack, tax computation, categories, rebate, minimum tax, PF, gratuity | Odoo module | W5 | 7 | `CD-077` |
| **`CD-M56-03`** | `cd_beftn` | bank file generation, validation, release control, disbursement confirmation | Odoo module | W5 | 3 | `CD-078` |
| **`CD-M56-04`** | `cd_benefits` | PF ledger, insurance, loans, advances, recovery limits | Odoo module | W5 | 4 | `CD-079` |
| **`CD-M56-05`** | `cd_final_settlement` | settlement computation, clearance gate, certificates | Odoo module | W5 | 3 | `CD-080` |
| **`CD-M57-01`** | `cd_performance` | KPI definition, attribution, scorecards, disputes, review extension, calibration, PIP | Odoo module | W5 | 7 | `CD-081` |
| **`CD-M57-02`** | `cd_incentive_engine` | scheme versioning, eligibility, calculation, gates, simulation, adjustment, clawback, p… | Odoo module | W5 | 6 | `CD-082` |
| **`CD-M57-03`** | `cd_compensation` | compensation cycles, bands, equity analysis, proposals, succession | Odoo module | W5 | 3 | `CD-083` |
| **`CD-M58-01`** | `cd_recruitment_bd` | requisition with position and budget gate, structured evaluation, practical assessment,… | Odoo module | W6 | 7 | `CD-087` |
| **`CD-M58-02`** | `cd_onboarding` | onboarding orchestration, provisioning requests, readiness gate, induction, first-90-da… | Odoo module | W6 | 5 | `CD-088` |
| **`CD-M59-01`** | `cd_hse` | hazard register, risk assessment, JSA, safe work procedures, permits, PPE, inspections,… | Odoo module | W6 | 6 | `CD-089` |
| **`CD-M59-02`** | `cd_incident` | incident capture *(offline mobile)*, classification, investigation, root cause, CAPA, s… | Odoo module | W6 | 6 | `CD-090` |
| **`CD-M59-03`** | `cd_wellbeing` | occupational health records with dedicated access control, fitness status publication,… | Odoo module | W6 | 2 | `CD-091` |

#### Category I — Governance, Risk, Quality & Knowledge · 4 units · 23 CD items · 78 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M23-01`** | `cd_qms_process` | process register, policy and objectives, clause traceability index, certification regis… | Odoo module | W5 | 4 | `CD-C23-01` |
| **`CD-M23-02`** | `cd_checklist_authoring` | template authoring, versioning, applicability rules, gate declaration, evidence require… | Odoo module | W5 | 5 | `CD-C23-02` |
| **`CD-M23-03`** | `cd_nonconformance` | multi-source intake, typing, containment, disposition, RCA tooling, 8D, repeat detectio… | Odoo module | W5 | 5 | `CD-C23-03` |
| **`CD-M23-04`** | `cd_capa` | CAPA lifecycle, cross-module action dispatch, verification scheduler, escalation | Odoo module + service | W5 | 3 | `CD-C23-04` |
| **`CD-M23-05`** | `cd_internal_audit` | programme, independence engine, P11 mobile execution, findings, external audit hosting | Odoo module + service | W5 | 3 | `CD-C23-05` |
| **`CD-M23-06`** | `cd_quality_analytics` | trend, Pareto, control limits, management review pack assembly | Odoo module | W5 | 1 | `CD-C23-06` |
| **`CD-M24-01`** | `cd_document_core` | class taxonomy, auto-filing pipeline, metadata validation, exception queue, content-add… | Odoo module + service | W3 | 6 | `CD-C24-01` |
| **`CD-M24-02`** | `cd_records_retention` | schedule adoption from M60, retention computation, legal hold, disposal batches, certif… | Odoo module + service | W3 | 5 | `CD-C24-02` |
| **`CD-M24-03`** | `cd_esignature` | envelopes, tiered authentication, in-app and remote signing, sealing, completion certif… | Odoo module + service | W3 | 4 | `CD-C24-03` |
| **`CD-M24-04`** | `cd_evidence_pack` | pack composition, assembly by reference, completeness verification, sealing, controlled… | Odoo module | W3 | 2 | `CD-C24-04` |
| **`CD-M24-05`** | `cd_template_engine` | bilingual versioned templates, merge resolution, PDF/A rendering pipeline, watermarking… | Odoo module + service | W3 | 2 | `CD-C24-05` |
| **`CD-M60-01`** | `cd_risk_register` | risk objects, appetite and scales, versioned assessment, treatment, review scheduler, h… | Odoo module | W6 | 5 | `CD-C60-01` |
| **`CD-M60-02`** | `cd_control_framework` | control register, key designation, risk/obligation mapping, coverage reporting, authori… | Odoo module | W6 | 4 | `CD-C60-02` |
| **`CD-M60-03`** | `cd_control_testing` | declarative automated test engine, manual test workflow, evidence sealing, deficiency a… | Odoo module + service | W6 | 5 | `CD-C60-03` |
| **`CD-M60-04`** | `cd_obligation_register` | obligations, calendar, discharge and evidence, regulatory change, licences, retention s… | Odoo module | W6 | 4 | `CD-C60-04` |
| **`CD-M60-05`** | `cd_legal_matter` | legal matters, holds, insurance register and claims, third-party risk, continuity gover… | Odoo module | W6 | 2 | `CD-C60-05` |
| **`CD-M60-06`** | `cd_policy_governance` | policy library, attestation, exceptions; PDPA processing records, transfer register, su… | Odoo module + service | W6 | 2 | `CD-C60-06` |
| **`CD-M61-01`** | `cd_knowledge_article` | article types, bilingual authoring, operational linkage, review workflow, versioning, h… | Odoo module | W6 | 4 | `CD-C61-01` |
| **`CD-M61-02`** | `cd_troubleshooting_tree` | tree authoring, versioning, traversal API, node types and part linkage | Odoo module | W6 | 3 | `CD-C61-02` |
| **`CD-M61-03`** | `cd_knowledge_capture` | one-tap capture from a job, voice and photo capture, improvement queue, prompts and def… | Odoo module + service | W6 | 3 | `CD-C61-03` |
| **`CD-M61-04`** | `cd_knowledge_search` | bilingual index, usefulness ranking, context surfacing, gap analysis, AI corpus API | Service | W6 | 3 | `CD-C61-04` |
| **`CD-M61-05`** | — | Offline set computation, delta sync and stale-content invalidation *(with the P02 team)* | Service + mobile | W6 | 2 | `CD-C61-05` |
| **`CD-M61-06`** | `cd_brand_bulletin` | bulletin receipt, classification, distribution, acknowledgement, recall routing; techni… | Odoo module | W6 | 1 | `CD-C61-06` |

#### Category J — Data, Analytics & Intelligence · 4 units · 22 CD items · 97 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M25-01`** | `cd_embedded_analytics` | signed scope-bound embedding, in-screen and portal placement, context binding, freshnes… | Odoo module + service | W4 | 5 | `CD-112` |
| **`CD-M25-02`** | `cd_report_distribution` | subscriptions, bursting by ERP scope, delivery orchestration through M27, retention fil… | Service + Odoo surface | W4 | 5 | `CD-191` |
| **`CD-M25-03`** | `cd_alert_engine` | threshold, trend and absence conditions, routing, acknowledgement, suppression, escalat… | Service + Odoo surface | W4 | 4 | `CD-192` |
| **`CD-M25-04`** | `cd_statutory_report` | pixel-controlled rendering with Bengali script and numerals, content lifecycle and cert… | Odoo module + service | W4 | 4 | `CD-193` |
| **`CD-M26-01`** | `cd_ml_gateway` | single inference entry point, authentication, timeout, fallback contract, guard-rail en… | Python / FastAPI service | W6 | 5 | `CD-113` |
| **`CD-M26-02`** | `cd_dispatch_ml` | assignment scoring, duration prediction, travel prediction, override capture and feedba… | Service + model pipelines | W6 | 4 | `CD-114` |
| **`CD-M26-03`** | `cd_forecast` | parts demand, service demand, batch scoring, accuracy measurement *(consumed by M43; no… | Service + model pipelines | W6 | 5 | `CD-115` |
| **`CD-M26-04`** | `cd_predictive` | predictive failure, quality risk, fraud and anomaly detection | Service + model pipelines | W8 | 4 | `CD-116` |
| **`CD-M26-05`** | `cd_pricing_ml` | win probability, elasticity, trade-in valuation, with pricing guard rails | Service + model pipelines | W8 | 4 | `CD-117` |
| **`CD-M26-06`** | `cd_llm_bridge` | self-hosted generative inference, retrieval-augmented grounding, entitlement-filtered r… | Service | W6 / W8 | 5 | `CD-118` |
| **`CD-M26-07`** | `cd_model_governance` | portfolio register, model cards, bias testing, AI risk register, data-sufficiency gates… | Odoo module + service | W6 | 4 | `CD-194` |
| **`CD-M26-08`** | `cd_model_monitoring` | drift detection (PSI, KS, attribution), performance tracking, retraining triggers, auto… | Service | W6 | 3 | `CD-195` |
| **`CD-M62-01`** | `cd_metric_registry` | metric definitions as code, certification workflow, versioning and change control, impa… | Service + Odoo surface | W4 | 7 | `CD-110` |
| **`CD-M62-02`** | `cd_warehouse_sync` | CDC and event ingestion, Bronze landing, replay and backfill, late-arriving handling, m… | Python / dbt service | W4 | 6 | `CD-111` |
| **`CD-M62-03`** | `cd_data_contract` | contract definition and signing, schema-drift detection, contract compliance monitoring… | Service + Odoo surface | W4 | 3 | `CD-187` |
| **`CD-M62-04`** | `cd_data_quality` | declarative test suite, four-pillar observability, incident lifecycle, degraded-status… | Service + Odoo surface | W4 | 4 | `CD-188` |
| **`CD-M62-05`** | `cd_lineage_catalogue` | OpenLineage emission and store, column-level lineage graph, catalogue, ownership and st… | Service + Odoo surface | W4 | 3 | `CD-189` |
| **`CD-M62-06`** | `cd_feature_store` | offline and online feature definition, point-in-time correct retrieval, serving API, sk… | Service | W4 | 3 | `CD-190` |
| **`CD-M63-01`** | `cd_workflow_engine` | process definition and versioning, durable instance state, step execution, declared fai… | Service + Odoo surface | W3 | 6 | `CD-196` |
| **`CD-M63-02`** | `cd_approval_matrix` | delegation-of-authority matrix, derived approval chains, chain patterns, SoD enforcemen… | Odoo module + service | W3 | 5 | `CD-197` |
| **`CD-M63-03`** | `cd_business_rules` | decision-table repository, versioning and effective dating, change control and approval… | Odoo module + service | W3 | 4 | `CD-198` |
| **`CD-M63-04`** | `cd_job_scheduler` | scheduled business jobs, working-hours calendar with Bangladeshi holidays and shift pat… | Odoo module + service | W3 | 4 | `CD-199` |

#### Category K — Platform & Technology · 19 units · 39 CD items · 449 PW

| Issued ID | Technical name | Scope | Type | Wave | PW | Legacy ID |
|---|---|---|---|:--:|--:|---|
| **`CD-M28-01`** | `cd_event_outbox` | outbox primitive, drain, envelope, schema registry, subscriptions, delivery, dead lette… | Odoo module + service | W1 | 9 | `CD-125` |
| **`CD-M28-02`** | `cd_api_layer` | API registry, OpenAPI generation and validation, versioning and deprecation, standard e… | Odoo module + service + frontend | W1 | 8 | `CD-126` |
| **`CD-M28-03`** | `cd_webhook` | outbound registry, signing, delivery and retry, auto-disable; inbound verification, rep… | Odoo module | W1 | 3 | `CD-127` |
| **`CD-M28-04`** | `cd_sync_engine` | offline command journal, delta scoping, conflict detection and server-authoritative res… | Odoo module + service | W1 | 6 | `CD-128` |
| **`CD-M28-05`** | `cd_integration_monitor` | integration register, connector framework, credential lifecycle, circuit breakers, auto… | Odoo module + service | W1 | 4 | `CD-129` |
| **`CD-M29-01`** | `cd_rbac_ext` | role register, permission sets, six-tier record rules, field permissions, delegation, a… | Odoo module + service | W1 | 8 | `CD-130` |
| **`CD-M29-02`** | `cd_audit_ext` | inherited immutable audit, hash chaining, data-access logging, bulk-export control, aud… | Odoo module | W1 | 6 | `CD-131` |
| **`CD-M29-03`** | `cd_sod` | SoD evaluation at assignment and at transaction, exception lifecycle, access request, a… | Odoo module | W1 | 6 | `CD-132` |
| **`CD-M29-04`** | `cd_identity_ext` | identity lifecycle, Keycloak integration, MFA and step-up, session policy, corporate SS… | Odoo module + service | W1 | 6 | `CD-157` |
| **`CD-M29-05`** | `cd_data_protection` | field classification, residency enforcement at write time, resident-key join, cross-bor… | Odoo module + service | W1 | 5 | `CD-158` |
| **`CD-M30-01`** | `cd_entity_config` | entity, branch, zone, cost centre, business line, working calendar, single-action branc… | Odoo module | W1 | 7 | `CD-133` |
| **`CD-M30-02`** | `cd_feature_flag` | flag registry, targeting, evaluation service, kill switch, telemetry correlation, stale… | Odoo module + service | W1 | 3 | `CD-135` |
| **`CD-M30-03`** | `cd_platform_ops` | configuration registry, versioning, promotion and rollback, emergency path, health cons… | Odoo module + frontend | W1 | 7 | `CD-138` |
| **`CD-M30-04`** | `cd_job_registry` | scheduled job registry, execution monitoring with failure, overrun and missed-run detec… | Odoo module | W1 | 2 | `CD-159` |
| **`CD-M30-05`** | `cd_design_tokens` | DTCG design-token realization and asset carrier for OWL 2 / Odoo Web (DSY-01, CR-P04-DSY-01) | Odoo module | W1 | 3 | `CD-DSY` |
| **`CD-M64-01`** | `cd_mdm` | domain register, governed attribute model, direct-edit prevention, change request workf… | Odoo module + frontend | W2 | 8 | `CD-134` |
| **`CD-M64-02`** | `cd_data_quality` | rule engine across six dimensions, classification and gating, scoring, continuous evalu… | Odoo module + service | W2 | 6 | `CD-160` |
| **`CD-M64-03`** | `cd_reference_data` | code list master, versioning and effective dating, distribution and cache invalidation,… | Odoo module | W2 | 3 | `CD-161` |
| **`CD-M65-01`** | `cd_country_pack` | pack model and lifecycle, nine-component structure, zero-core-change gate, jurisdiction… | Odoo module + service | W9 | 10 | `CD-137` |
| **`CD-M65-02`** | `cd_locale_pack` | locale model, Bengali locale with ICU collation and lakh/crore grouping, translation st… | Odoo module + service | W9 | 7 | `CD-136` |
| **`CD-M65-03`** | `cd_multi_entity` | entity jurisdiction extension, single-action entity provisioning, entity isolation and… | Odoo module | W9 | 6 | `CD-162` |
| **`CD-M66-01`** | `cd_itsm` | service catalogue, employee self-service portal, incident management with automatic cre… | Odoo module + frontend | W6 | 9 | `CD-163` |
| **`CD-M66-02`** | `cd_it_asset` | IT asset register and lifecycle, onboarding and offboarding workflows with settlement b… | Odoo module + service | W6 | 5 | `CD-164` |
| **`CD-M67-01`** | `cd_project` | project object and the five templates, work breakdown structure, scheduling and critica… | Odoo module + frontend | W7 | 8 | `CD-165` |
| **`CD-M67-02`** | `cd_project_resource` | role-based demand, candidate resolution against M55 availability, M02 commitments and M… | Odoo module + service | W7 | 5 | `CD-166` |
| **`CD-M67-03`** | `cd_project_billing` | project budget by category, cost aggregation from source modules by reference, committe… | Odoo module | W7 | 4 | `CD-167` |
| **`CD-P01-01`** | `p01_customer_web` | PWA: account, devices, booking funnel, tracking, approvals, payments, contracts, warran… | Next.js 15 application | W2 | 28 | `CD-200` |
| **`CD-P01-02`** | `p01_customer_app` | native application: parity surface, biometric login, push reliability, store presence,… | React Native application | W2 | 14 | `CD-201` |
| **`CD-P02-01`** | `p02_technician_app` | job queue and day, execution and diagnosis, evidence capture, parts and van reconciliat… | Flutter application | W2 | 40 | `CD-202` |
| **`CD-P03-01`** | `p03_workspace_framework` | role-scoped console registry and composition, console landing behaviour, global search,… | Odoo module (OWL 2) | W1 | 30 | `CD-203` |
| **`CD-P04-01`** | `p04_corporate_portal` | organisation account and client-side delegation model, estate view and bulk maintenance… | Next.js 15 application | W4 | 26 | `CD-204` |
| **`CD-P05-01`** | `p05_supplier_portal` | onboarding with document expiry control, RFQ and quotation, PO acknowledgement and ASN,… | Next.js 15 + Odoo portal extension | W3 | 18 | `CD-205` |
| **`CD-P06-01`** | `p06_analytics_surface` | dashboard composition and the fourteen functional dashboards, executive and branch leag… | Configuration + Next.js/OWL surfaces | W4 | 16 | `CD-206` |
| **`CD-P07-01`** | `p07_seller_web` | registration with class-differentiated in-flow verification, agreement execution and tr… | Next.js 15 application | W7 | 22 | `CD-207` |
| **`CD-P07-02`** | `p07_seller_app` | job broadcast and response window, bidding, acceptance, execution to owned-job standard… | React Native application | W7 | 12 | `CD-208` |
| **`CD-P08-01`** | `p08_brand_portal` | claim queue with evidence viewer and line-level decision, information-request tracked s… | Next.js 15 application | W4 | 18 | `CD-209` |
| **`CD-P09-01`** | `p09_logistics_rider` | rider manifest and day, scan-to-open stops, four-proof custody capture at collection an… | Flutter application + web console | W3 | 22 | `CD-210` |
| **`CD-P10-01`** | `p10_agent_console` | unified queue and presence, embedded softphone integration, screen pop with composed Cu… | Next.js 15 application | W4 | 22 | `CD-211` |
| **`CD-P11-01`** | `p11_auditor_app` | assigned audits and versioned checklist execution, observation and evidence capture, fi… | Flutter application | W5 | 16 | `CD-212` |
| **`CD-P12-01`** | `p12_partner_portal` | application with type declaration and transaction gate, referral link and code generati… | Next.js 15 application | W7 | 14 | `CD-213` |


#### Category roll-up

| Cat | Units (M / P) | CD items | PW |
|:--:|---|---:|---:|
| **A** | 7 / 0 | 34 | 206 |
| **B** | 7 / 0 | 31 | 144 |
| **C** | 9 / 0 | 57 | 262 |
| **D** | 3 / 0 | 11 | 60 |
| **E** | 6 / 0 | 25 | 119 |
| **F** | 5 / 0 | 22 | 114 |
| **G** | 8 / 0 | 41 | 197 |
| **H** | 7 / 0 | 26 | 124 |
| **I** | 4 / 0 | 23 | 78 |
| **J** | 4 / 0 | 22 | 97 |
| **K** | 7 / 12 | 39 | 449 |
| **Total** | **67 / 12** | **331** | **1850** |


---

## 7. Reconciliation

### 7.1 Against the `GV-007` build baseline

`GV-007` §4.1 states the counted build position as **1,842 PW** across 79 files, derived from the
**Effort estimate** row of each specification's §1 Identity table. This register derives **1,850 PW**
from a different place in the same 79 files — the sum of the §16.2 CD rows.

| Source | Method | Result |
|---|---|---:|
| `GV-007` §4.1 | Sum of §1 **Effort estimate** across 79 units | **1,842 PW** |
| This register §6 | Sum of §16.2 **Effort** across 331 CD rows | **1,850 PW** |
| | **Difference** | **+8 PW** |

**Two independent readings of 79 files agree to within 0.4%.** The difference is not distributed
noise: **75 of 79 units reconcile exactly**, and the whole 8 PW arises in four units.

### 7.2 The four units that do not reconcile

| Unit | §1 declared | §16.2 rows sum | Δ | Reading |
|---|---:|---:|---:|---|
| `M07` CRM, Sales Pipeline & Account Management | 22 | 18 | **−4** | §1 carries 4 PW that no CD row names |
| `M20` AR, Invoicing & Collections | 24 | 26 | **+2** | §16.2 names 2 PW more than §1 declares |
| `M50` Treasury, Cash & Banking | 22 | 28 | **+6** | §16.2 names 6 PW more than §1 declares |
| `M51` Tax & Regulatory Compliance (BD) | 26 | 30 | **+4** | §16.2 names 4 PW more than §1 declares |
| | **94** | **102** | **+8** | |

**Disposition.** The §1 figure is the one `GV-007` counted and the one `GV-004` planned against; it
remains the baseline. The four units are referred to their owning squads for correction under
`CDR-11` — the specification is corrected, then this register is regenerated. Raised as `BEA-03`.

> **`M50` is the one to look at first.** A 27% under-declaration in Treasury lands in Wave 3, which
> `GV-004` §5.2 already rates at **zero float**.

### 7.3 The 1,850 PW contains no configuration effort at all

This is the most consequential thing the reconciliation reveals, and it is visible only because the
two sums agree.

`02-05` §1 and TSS §10.14 both state that **Odoo 19 CE covers ~28% of requirements natively and OCA a
further ~24%** — 52% of the requirement estate delivered by configuring software that already exists.
Configuration is real work: `ir.model.access` rows, record rules, sequences, journals, chart of
accounts, warehouse and location trees, pricelists, SLA definitions, approval matrices, 23 Odoo
modules and 140+ OCA modules installed, parameterised and regression-tested.

For **75 of 79 units the §1 effort figure equals the §16.2 custom-development sum exactly**. There is
therefore no line anywhere in the estate for L1 and L2 configuration effort.

| Interpretation | Consequence |
|---|---|
| (a) The §1 figure was only ever a custom-development figure | Configuration effort is **entirely unbudgeted**, and the build baseline is understated by an unmeasured amount |
| (b) Configuration effort is silently absorbed inside the CD rows | The CD rows are then not custom-development estimates, and every derived figure — `FF-16` scope, vendor pricing, sprint sizing — is measuring something other than what it names |

Neither reading is benign, and the estate does not say which is true. `GV-007` §7.3 lists seven work
streams it explicitly excludes; **configuration is not among them**, so it is excluded by accident
rather than by decision. Raised as **`BEA-04`**, and referred to `GV-007` for a fifth work stream.

### 7.4 Cross-cutting services and the `APP-` space

**TSS §8.2 Block 3** names sixteen "standalone domain services not attributable to a single module",
`CD-233`…`CD-248`, sized at *~170–200 PW (est.)*. Tested against the estate at 2026-08-18 12:46 (+06):

| Test | Result |
|---|---|
| Block 3 identifiers appearing in any §16.2 table of any of the 79 units | **0 of 16** |
| Block 3 services with a plausible counterpart under a different identifier | **7 of 16** — e.g. the residency service (`CD-233`) against `M29`'s `cd_data_protection`; the ML inference gateway (`CD-245`) against `M26`'s `cd_ml_gateway`; the telemetry collector (`CD-237`) against `M48`'s `cd_telemetry` |
| Block 3 services with **no** counterpart found | **9 of 16** — including the document generation service, the OCR wrapper, the warehouse ETL, the RMM collector, the speech-to-text wrapper and the data-subject request orchestrator |
| Block 3 effort included in the 1,842 PW baseline | **None.** The baseline sums unit §1 rows, and Block 3 belongs to no unit |

**Position taken.** The `SVC` space defined in §5.1 is **left empty at this issue**, deliberately.
Populating it would mean this register asserting that nine unowned services exist and sizing them,
which is an architecture decision (`AR-005` ownership) and an estimate (`GV-007`), not an
identification exercise. Instead:

| Action | Owner | By |
|---|---|---|
| Rule on ownership for each of the sixteen Block 3 services — assign to a unit or confirm as cross-cutting | ERP Design Authority (`AR-005`) | **W0** |
| Size the confirmed cross-cutting set and add it to the build baseline as a fifth work stream | `GV-007` | W0 |
| Allocate `CD-SVC-nn` for each confirmed cross-cutting service and regenerate §6 | Chief Architect | W0 |

Raised as **`BEA-05`**. Between ~0 PW (fully duplicated) and ~200 PW (fully additional), the answer
is unknown, and the 1,842 PW baseline is exposed to the whole of that range.

**`APP-01`…`APP-10` are retired at this issue.** TSS §8.2 registers ten applications in a separate
space on the reasoning that *"an application is not an Odoo module"*. That is true and does not
require a second identifier space: all ten applications are portal deliverables and already carry
portal CD rows in §6 — for example `APP-01` Technician mobile application is `CD-P02-01`. Retaining
`APP-` would mean two identifiers for one deliverable, which is the defect this document exists to
remove. The crosswalk is in §8.2; the space is tombstoned in §8.3.

### 7.5 The wave curve this register produces

Because §6 covers **all 79 units** rather than the 42 in the programme's wave model, the demand
curve it implies differs materially from `GV-004` §5.2. Demand below is the §1 declared effort of
each unit, placed in the unit's own declared delivery wave; capacity is `GV-004` §5.2 unchanged.

| Wave | `GV-004` demand (42 units) | **All-79 demand** | Effective capacity | **Ratio** | `GV-004` verdict |
|:--:|---:|---:|---:|---:|---|
| W1 | 217 | **239** | 40.7 | **5.87×** | ❌ Infeasible |
| W2 | 167 | **240** | 95.0 | **2.53×** | ❌ Over capacity |
| W3 | 153 | **281** | 152.3 | **1.85×** | ⚠ was "zero float" |
| W4 | 224 | **353** | 169.3 | **2.09×** | ❌ Over capacity |
| W5 | 108 | **247** | 135.7 | **1.82×** | ✅ was "fits" |
| W6 | 99 | **235** | 162.9 | **1.44×** | ✅ was "under-loaded" |
| W7 | 98 | **185** | 162.9 | **1.14×** | ✅ was "under-loaded" |
| W8 | 13 | **39** | 135.7 | 0.29× | ✅ nearly empty |
| W9 | 0 | **23** | 33.9 | 0.68× | ✅ empty |
| **Total** | **1,079** | **1,842** | **1,088.4** | **1.69×** | *"balances in total"* |

**Verification** *(`PG-M10`)*: 239 + 240 + 281 + 353 + 247 + 235 + 185 + 39 + 23 = **1,842** ✓
against the `GV-007` build total of 1,842 ✓.

> **`GV-004` §5.4 states that 763 PW is *"in no wave at all"*. The figure is exactly right and the
> description is not.** All 37 of the M31–M67 specifications declare a delivery wave in their own §1
> Identity table — W1 48 PW, W2 47, W3 104, W4 153, W5 139, W6 136, W7 87, W8 26, W9 23. The work is
> not unplaced; it is placed in the specifications and **absent from the plan**, which is a different
> and more tractable problem.
>
> **The consequence is that the plan does not balance in aggregate either.** `GV-004` §5.3's central
> observation — *"the plan balances in aggregate and fails in shape"* — rests on 1,079 PW against
> 1,088 PW. Against the full 79-unit estate it is **1,842 against 1,088: 1.69×**, and **no wave
> before W8 is under capacity**. Raised as **`BEA-06`** and referred to `GV-004` and `GV-007` §9.2 as
> a re-estimation trigger.

---

## 8. Crosswalk, Collisions and Retirement

### 8.1 Reading a legacy identifier

Every existing document in the workspace — 79 specifications, `02-05`, the Technology Stack
Specification, the RFP, the audits — remains readable without edit. To resolve any legacy `CD`
reference:

| If the legacy identifier is… | Then |
|---|---|
| Unique across the estate (224 of 272) | Look it up in the **Legacy ID** column of §6; exactly one issued identifier is returned |
| One of the **48 colliding** identifiers | Look it up in §8.2, which lists every issued identifier that legacy number now denotes. **The reference is ambiguous and must be disambiguated by its context before use** |
| From TSS §8.2 Block 2 or Block 3 (`CD-139`…`CD-248`) | It may denote a different module from the estate's usage (§3.3). **Resolve against §6, never against TSS §8.2** |
| An `APP-nn` | See §8.2's application crosswalk |

### 8.2 The collision record

Forty-eight legacy identifiers denote 107 distinct components. Each is resolved below. **None of the
48 is reissued**; all are tombstoned under `CDR-04`.

| Legacy ID | Claimants | Issued identifiers now held | Distinct components denoted |
|---|:--:|---|---|
| `CD-059` | **2** | `CD-M34-02` · `CD-M13-01` | `cd_closed_loop` · `cd_rental_asset` |
| `CD-060` | **2** | `CD-M34-03` · `CD-M13-02` | `cd_complaint` · `cd_rental_agreement` |
| `CD-061` | **2** | `CD-M34-04` · `CD-M13-03` | `cd_journey` · `cd_condition_report` |
| `CD-062` | **2** | `CD-M35-01` · `CD-M13-04` | `cd_campaign` · `cd_rental_billing` |
| `CD-063` | **2** | `CD-M35-02` · `CD-M14-01` | `cd_journey_orchestration` · `cd_tradein` |
| `CD-064` | **2** | `CD-M35-03` · `CD-M14-02` | `cd_attribution` · `cd_refurb` |
| `CD-065` | **2** | `CD-M35-04` · `CD-M14-03` | `cd_content` · `cd_grading` |
| `CD-066` | **2** | `CD-M14-04` · `CD-M21-01` | `cd_resale` · `cd_hr_core` |
| `CD-068` | **2** | `CD-M15-01` · `CD-M21-03` | `cd_stock_ext` · `cd_employee_ess` |
| `CD-069` | **2** | `CD-M15-02` · `CD-M21-04` | `cd_stock_ownership` · `cd_hr_documents` |
| `CD-070` | **2** | `CD-M15-03` · `CD-M55-01` | `cd_cycle_count` · `cd_attendance` |
| `CD-071` | **2** | `CD-M44-04` · `CD-M55-02` | `cd_landed_cost` · `cd_leave` |
| `CD-072` | **2** | `CD-M42-01` · `CD-M55-03` | `cd_vendor_ext` · `cd_roster` |
| `CD-073` | **2** | `CD-M16-02` · `CD-M55-04` | `cd_rfq` · `cd_capacity` |
| `CD-074` | **2** | `CD-M44-01` · `CD-M55-05` | `cd_import_order` · `cd_overtime` |
| `CD-075` | **2** | `CD-M17-01` · `CD-M55-06` | `cd_asset_registry` · `Biometric device adapter and healt` |
| `CD-076` | **2** | `CD-M17-03` · `CD-M56-01` | `cd_asset_estate` · `cd_payroll_bd` |
| `CD-077` | **2** | `CD-M17-05` · `CD-M56-02` | `cd_maintenance_plan` · `cd_statutory_bd` |
| `CD-078` | **2** | `CD-M48-02` · `CD-M56-03` | `cd_telemetry` · `cd_beftn` |
| `CD-079` | **2** | `CD-M48-04` · `CD-M56-04` | `cd_asset_health` · `cd_benefits` |
| `CD-080` | **2** | `CD-M18-01` · `CD-M56-05` | `cd_ewaste` · `cd_final_settlement` |
| `CD-081` | **2** | `CD-M18-02` · `CD-M57-01` | `cd_recycling` · `cd_performance` |
| `CD-082` | **2** | `CD-M18-03` · `CD-M57-02` | `cd_esg_report` · `cd_incentive_engine` |
| `CD-083` | **2** | `CD-M51-02` · `CD-M57-03` | `cd_mushak` · `cd_compensation` |
| `CD-084` | **2** | `CD-M51-03` · `CD-M22-01` | `cd_vat_register` · `cd_competency` |
| `CD-085` | **2** | `CD-M51-05` · `CD-M22-02` | `cd_tds` · `cd_certification` |
| `CD-086` | **2** | `CD-M51-06` · `CD-M22-03` | `cd_nid` · `cd_training_ops` |
| `CD-087` | **2** | `CD-M50-01` · `CD-M58-01` | `cd_cash_position` · `cd_recruitment_bd` |
| `CD-088` | **2** | `CD-M49-01` · `CD-M58-02` | `cd_fixed_asset_ext` · `cd_onboarding` |
| `CD-089` | **2** | `CD-M19-05` · `CD-M59-01` | `cd_close_checklist` · `cd_hse` |
| `CD-090` | **2** | `CD-M20-01` · `CD-M59-02` | `cd_billing_engine` · `cd_incident` |
| `CD-157` | **3** | `CD-M17-02` · `CD-M19-01` · `CD-M29-04` | `cd_asset_identity` · `cd_gl_ext` · `cd_identity_ext` |
| `CD-158` | **3** | `CD-M17-04` · `CD-M19-02` · `CD-M29-05` | `cd_asset_genealogy` · `cd_subledger_posting` · `cd_data_protection` |
| `CD-159` | **3** | `CD-M45-01` · `CD-M19-03` · `CD-M30-04` | `cd_equipment_register` · `cd_multi_entity_consolidation` · `cd_job_registry` |
| `CD-160` | **3** | `CD-M45-02` · `CD-M19-04` · `CD-M64-02` | `cd_tool_custody` · `cd_financial_statements_bd` · `cd_data_quality` |
| `CD-161` | **3** | `CD-M45-03` · `CD-M20-02` · `CD-M64-03` | `cd_calibration` · `cd_ar_ext` · `cd_reference_data` |
| `CD-162` | **3** | `CD-M45-04` · `CD-M20-03` · `CD-M65-03` | `cd_equipment_maintenance` · `cd_receipt_matching` · `cd_multi_entity` |
| `CD-163` | **3** | `CD-M46-01` · `CD-M20-04` · `CD-M66-01` | `cd_vehicle_ext` · `cd_credit_note_refund` · `cd_itsm` |
| `CD-164` | **3** | `CD-M46-02` · `CD-M52-01` · `CD-M66-02` | `cd_vehicle_compliance` · `cd_ap_ext` · `cd_it_asset` |
| `CD-165` | **3** | `CD-M46-03` · `CD-M52-02` · `CD-M67-01` | `cd_fuel_and_running_cost` · `cd_payment_run` · `cd_project` |
| `CD-166` | **3** | `CD-M46-04` · `CD-M52-03` · `CD-M67-02` | `cd_driver_management` · `cd_expense_claim` · `cd_project_resource` |
| `CD-167` | **3** | `CD-M47-01` · `CD-M50-02` · `CD-M67-03` | `cd_site_register` · `cd_bank_account_mgmt` · `cd_project_billing` |
| `CD-168` | **2** | `CD-M47-02` · `CD-M50-03` | `cd_lease_admin` · `cd_bank_reconciliation` |
| `CD-169` | **2** | `CD-M47-03` · `CD-M50-04` | `cd_facility_work_order` · `cd_branch_cash_control` |
| `CD-170` | **2** | `CD-M47-04` · `CD-M50-05` | `cd_site_compliance` · `cd_gateway_settlement` |
| `CD-171` | **2** | `CD-M48-01` · `CD-M50-06` | `cd_stream_registry` · `cd_cashflow_forecast` |
| `CD-172` | **2** | `CD-M48-03` · `CD-M50-07` | `cd_alert_rules` · `cd_trade_finance` |
| `CD-173` | **2** | `CD-M48-05` · `CD-M51-01` | `cd_predictive_action` · `cd_tax_engine_bd` |

**Application crosswalk.** TSS §8.2 `APP-01`…`APP-10` resolve as follows and the space is retired:

| Legacy | Application | Issued ID |
|---|---|---|
| `APP-01` | Technician mobile application | `CD-P02-01` |
| `APP-02` | Logistics & rider application | `CD-P09-01` |
| `APP-03` | Field auditor & quality application | `CD-P11-01` |
| `APP-04` | Customer mobile application | `CD-P01-02` |
| `APP-05` | Customer self-service portal (web) | `CD-P01-01` |
| `APP-06` | Corporate B2B portal | `CD-P04-01` |
| `APP-07` | Brand partner portal | `CD-P08-01` |
| `APP-08` | Contact centre agent console | `CD-P10-01` |
| `APP-09` | Marketplace seller portal | `CD-P07-01` *(and `CD-P07-02` for the seller application)* |
| `APP-10` | Partner & referral portal | `CD-P12-01` |

> **The `APP-` space covered ten of the fourteen portal deliverables.** `CD-P03-01` (Admin Operations
> Portal, 30 PW), `CD-P05-01` (Vendor & Supplier Portal, 18 PW) and `CD-P06-01` (Analytics &
> Executive Dashboard, 16 PW) have no `APP-` identifier at all — 64 PW of portal build outside the
> application register that was supposed to be complete. A second reason to retire it rather than
> extend it.

### 8.3 Retirement register

Under `CDR-04` and `RG-02`, retired identifiers are tombstoned and never reissued.

| Space | Extent | Status | Successor |
|---|---|---|---|
| `CD-001` … `CD-138` (`02-05` §5.2, R1) | 138 identifiers | **Retired** | §6, via the Legacy ID column |
| `CD-139` … `CD-248` (TSS §8.2 Blocks 2–3, R2) | 110 identifiers | **Retired** | §6 for Block 2; §7.4 for Block 3 |
| `CD-001` … `CD-213` as used in §16.2 (R3) | 192 in use, 21 unused inside the span | **Retired** | §6 |
| `CD-C08-nn` … `CD-C61-nn` (R4) | 80 identifiers across 13 modules | **Retired** | §6 |
| `APP-01` … `APP-10` | 10 identifiers | **Retired** | §8.2 |
| `CD-214` and above | Never allocated to any component | **Reserved and closed.** The flat space is closed permanently; nothing is ever allocated from it again | `CD-<UNIT>-<nn>` |

**Total identifiers retired at this issue: 272 in use, plus 21 unused numbers inside the flat span,
plus the whole of `CD-214`+ .** Nothing above is deleted from any document; all remain resolvable
through §6 and §8.2.

---

## 9. What the Register Says About the Build

Three distributions, generated from §6, because each answers a question a plan needs and none of them
existed before.

### 9.1 By deliverable type — what skills the programme actually needs

| Type as declared in §16.2 | Items | Share |
|---|---:|---:|
| Odoo module | 180 | 54.4% |
| Odoo module + standalone service | 90 | 27.2% |
| Standalone service | 33 | 10.0% |
| Front-end component (OWL 2 / web) | 12 | 3.6% |
| Next.js application | 8 | 2.4% |
| Flutter application | 3 | 0.9% |
| Mobile application (framework unstated) | 3 | 0.9% |
| React Native application | 2 | 0.6% |
| **Total** | **331** | **100%** |

**Verification** *(`PG-M10`)*: 180 + 90 + 33 + 12 + 8 + 3 + 3 + 2 = **331** ✓.

> **Two readings a resource plan needs.**
>
> **(1) 82% of the deliverable count is Odoo work.** 270 of 331 items are an Odoo module or an Odoo
> module plus a service. `GV-007` §8.3 puts the hiring lead time for senior Odoo developers at 10–16
> weeks and `GV-004` §5.2 starts Wave 1 with **3 build FTE**. The scarcest role carries four-fifths
> of the deliverable list.
>
> **(2) The mobile framework question is live in the register, not just in the radar.** Five items
> are declared as React Native or as an unqualified "mobile application", against three declared
> Flutter. TSS §25.2.5 and `AR-013` both recommend Flutter as the single framework and neither
> decision has been taken. Until it is, `BE-002` must publish style rules for a stack the programme
> may not build, and `BE-001` must install a toolchain it may not need. Referred to `D-027`.

### 9.2 By category — where the custom code is

Counted in §6's category roll-up. Category **C** (Commercial, Pricing & Revenue) holds the most items
at **57**; Category **K** holds the most effort at **449 PW**, of which 298 PW is the twelve portals.
Categories **D** (11 items) and **A** (34 items / 206 PW) sit at opposite ends of the
items-per-person-week ratio, which is a useful signal for `BE-008` sizing: Category A averages
**6.1 PW per CD item**, Category I averages **3.4**.

### 9.3 By wave — §7.5

The wave distribution and its capacity consequence are in §7.5 rather than here, because the finding
is about the plan rather than about the register.

---

## 10. Enabling `FF-16`

`AR-012` §5.3 records `FF-16` — *"`x_cd_id` present and issued by `BE-005`"* — as one of two
fitness functions that are **unsatisfiable**, with the instruction: *"Build the check in W1; enable
when `BE-005` issues. Do not weaken it to 'any identifier' — that defeats its purpose."*

The check becomes satisfiable on the conditions below.

| # | Condition | Owner | Status at this issue |
|---|---|---|---|
| 1 | An issued register exists | Chief Architect | ✅ §6 |
| 2 | The register is machine-readable | Chief Architect | ⬜ **§11.4 — the register is regenerated into `cd-register.yaml`; `BE-006` `CBS-04` binds `component.yaml` to it** |
| 3 | `AR-007` §3.2's manifest rule cites the issued form | Solution Architect | ⬜ `AR-007` v1.1 — the manifest example shows a flat `CD-nnn`; it must show `CD-<UNIT>-<nn>` |
| 4 | The check validates form **and** membership | Platform Engineering (`PE-004`) | ⬜ W1 |
| 5 | The four unreconciled units are corrected (§7.2) | Owning squads | ⬜ W0 |

**Recommended enablement.** `FF-16` runs as **Warning** from the first CI build and is promoted to
**Blocking at the Wave 1 gate**, under `AR-012` §5.2's promotion rule. It should not start Blocking,
because condition 3 is an edit to a document this one depends on, and a Blocking check that fails on
its own dependency teaches developers to disable checks.

> **The check must validate membership, not just form.** `CD-M99-42` is well-formed and denotes
> nothing. A regex-only check would pass it, and the estate's history is of well-formed identifiers
> denoting the wrong thing.

---

## 11. Governance

### 11.1 Allocation authority

| Action | Authority | Route |
|---|---|---|
| Allocate `<nn>` within an existing unit | **The owning unit's specification author**, under `CDR-03` | Add the row to §16.2; regenerate §6 |
| Allocate a new unit `M68` / `P13` | `02-02` module register | Out of scope here; the CD space follows automatically |
| Allocate `CD-SVC-nn` | **ERP Design Authority** | §7.4; approval required, no local allocation |
| Retire an identifier | Chief Architect | §8.3 tombstone row + successor |
| Move an item between units | ERP Design Authority | `CDR-06`: retire and re-issue; both rows recorded |

> **`CDR-03` is the whole point.** An author adding a component to M43 allocates `CD-M43-04` by
> looking at one file — their own. There is no queue, no round trip, and no possibility that a
> concurrent author in M44 takes the same identifier. Compare `PG-M13`, which exists because two
> sessions took `PGD-AUDIT-002` eight minutes apart.

### 11.2 Change control

| Change | Instrument | Approver |
|---|---|---|
| New CD item inside an existing unit, no effort change | Specification revision | Solution Architect |
| New CD item that changes a unit's effort figure | **`CR-nnn` under `GV-003`** | Change Advisory Board |
| Splitting or merging CD items | `CR-nnn` + `CDR-05` retirement rows | ERP Design Authority |
| Moving work between units | `CR-nnn` + `CDR-06` | ERP Design Authority |
| Any change to §5's identifier standard | `CR-nnn` + a `D-nnn` decision in `GV-003` | ERP Steering Committee |

`GV-006` records that **56 modules, 6 portals and 477 content files entered scope with zero change
requests ever raised.** The register is the instrument that makes the next such movement visible:
a new CD item is a new row, and a new row is countable.

### 11.3 Freeze and baseline

| Baseline | Content | Set |
|---|---|---|
| `CD-B1` | The 331 items in §6 as issued | 2026-08-18 |
| Freeze point | The register is frozen at each **wave gate** under `GV-009`; the wave's items may not change scope after its gate opens | Per wave |
| Regeneration cadence | On any specification change touching §16.2, and unconditionally before each wave gate | `CDR-11` |

### 11.4 Machine-readable form

`§6` is the human-readable register. The build depends on a machine-readable one:

```yaml
# tooling/cd-register.yaml — generated, never hand-edited
generated_at: "2026-08-18T12:46:00+06:00"
baseline: CD-B1
items:
  - id: CD-M01-01
    unit: M01
    name: cd_service_order
    type: odoo_module
    wave: W1
    effort_pw: 16
    legacy: [CD-001]
  - id: CD-P02-01
    unit: P02
    name: p02_technician_app
    type: flutter_application
    wave: W2
    effort_pw: 40
    legacy: [CD-202, APP-01]
```

| Consumer | Uses it for |
|---|---|
| `FF-16` (`AR-012`, `PE-004`) | Manifest `x_cd_id` membership validation |
| `BE-003` `GW-04` | Branch-name validation |
| `BE-004` `REPO-09` | Directory-to-item mapping and `CODEOWNERS` generation |
| `BE-006` `CBS-04` | `component.yaml` cross-check |
| `BE-008` `SPR-07` | Backlog epic seeding |
| `QA-004` | Test-to-component traceability |

---

## 12. Findings Raised by This Register

| # | Finding | Sev | Against |
|---|---|:--:|---|
| **`BEA-01`** | `RQA-10` understates the CD collision count (31 against a counted **48**) and names `CD-214` as "the highest in use" when no §16.2 row claims it; the highest in use is `CD-213` | Med | `PGD-AUDIT-004` |
| **`BEA-02`** | TSS §25.3.1 proposes restating the RFP's deliverable count to **248**; the counted estate is **331**, and TSS §8.2 disagrees with the estate on **74.7%** of the flat identifier space | **Crit** | TSS §8.2, §25.3.1; RFP §5.3 |
| **`BEA-03`** | Four units' §16.2 rows do not sum to their §1 declared effort — `M07` −4, `M20` +2, `M50` +6, `M51` +4 PW | Med | `M07`, `M20`, `M50`, `M51` |
| **`BEA-04`** | **No configuration effort exists anywhere in the estate.** For 75 of 79 units the §1 effort figure equals the custom-development sum exactly, against a stated 52% L1+L2 requirement coverage | **Crit** | `GV-007` §7.3; `02-05` §1 |
| **`BEA-05`** | TSS Block 3's sixteen cross-cutting services (~170–200 PW est.) are owned by no unit, appear in no §16.2 table, and are outside the 1,842 PW baseline; 7 of 16 may duplicate module-owned components | High | TSS §8.2 Block 3 |
| **`BEA-06`** | With all 79 units placed in their own declared waves, the plan does not balance in aggregate: **1,842 PW against 1,088 PW effective capacity — 1.69×**, with no wave under capacity before W8 | **Crit** | `GV-004` §5.2, §5.3, §5.4 |
| **`BEA-07`** | Five CD items are declared React Native or unqualified "mobile application" against three declared Flutter, while `D-027` remains undecided | Med | `AR-013`; TSS §25.2.5 |
| **`BEA-08`** | `_MODULE_TEMPLATE` §0 has stated *"48 identifiers currently collide"* to every module author since the template was issued, and instructs them to proceed anyway | High | `_MODULE_TEMPLATE` §0, §16.2 |

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-005-D-01` | Identifier form | (a) Renumber flat `CD-001`…`CD-331`; (b) module-scoped `CD-<UNIT>-<nn>`; (c) keep flat, appoint an allocator | **(b)** | (a) and (c) both require an estate-wide read to allocate, which is the mechanism that failed five times (§4) | Identifiers lengthen; every existing reference becomes a legacy alias resolved by §6 |
| `BE-005-D-02` | Unit key | (a) Category+number `C12`; (b) module code `MKP`; (c) module number `M12` | **(c)** | Codes have changed twice (`SLS`→`PRC`, `HRM`→`HCM`); numbers never have | The 13 modules using the `C12` form are re-issued, not grandfathered |
| `BE-005-D-03` | Legacy identifiers | (a) Delete from source files; (b) retain as read-only aliases | **(b)** | Editing 79 specifications plus the RFP, TSS and audits to renumber would be a large change with no functional benefit and high transcription risk | Every legacy reference resolves through §6; nothing is silently broken |
| `BE-005-D-04` | The `APP-` space | (a) Retain alongside CD; (b) retire | **(b)** | It covered 10 of 14 portal deliverables and gave four of them a second identifier | §8.2 crosswalk; TSS §8.2's application table is superseded |
| `BE-005-D-05` | TSS Block 3 services | (a) Issue `CD-SVC-01`…`16` now; (b) leave `SVC` empty pending an ownership ruling | **(b)** | Issuing them would assert an architecture ownership decision this document has no authority to take, and size work `GV-007` has not sized | `BEA-05`; three W0 actions in §7.4 |
| `BE-005-D-06` | Effort figures | (a) Re-estimate at register level; (b) transcribe from §16.2 | **(b)** | `GV-007` `EM-01` owns estimation; a register that re-estimates creates a sixth competing figure | The 8 PW reconciliation gap is reported (`BEA-03`), not smoothed |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Do the sixteen TSS Block 3 services exist as separate deliverables, or are they already inside module CD items? | ERP Design Authority | **W0 — blocking** | The build baseline (±200 PW); `CD-SVC` allocation |
| `Q-02` | Is configuration effort inside the 1,850 PW or absent from it (`BEA-04`)? | CTO / `GV-007` | **W0 — blocking** | Every estimate, every sprint plan, every vendor price |
| `Q-03` | Which mobile framework — `D-027` (`BEA-07`)? | CTO | **W0** | `BE-001` toolchain, `BE-002` §6, 5 CD items |
| `Q-04` | Does the CFO's restatement of the RFP deliverable count use 248 or 331 (`BEA-02`)? | CFO / CTO | Before RFP re-issue | Vendor pricing basis |
| `Q-05` | Who regenerates the register, and on what trigger, once the implementation partner is authoring specifications? | Chief Architect | W1 | `CDR-11` operability |
| `Q-06` | Does the wave re-plan required by `BEA-06` precede or follow the Wave 1 gate? | ERP Steering Committee | **W0** | Whether Wave 1 starts against a 5.87× plan |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every one of the 79 delivery units appears in §6 with at least one item | 79 units enumerated; 0 with zero rows |
| `AC-02` | Every issued identifier is unique | 331 issued identifiers, 331 distinct — verified by construction and by count |
| `AC-03` | Every legacy identifier in use resolves to at least one issued identifier | 272 legacy identifiers, all present in §6's Legacy ID column or §8.2 |
| `AC-04` | Every colliding legacy identifier is disambiguated | 48 rows in §8.2 resolving 107 components |
| `AC-05` | The register reconciles to the `GV-007` baseline, or the difference is explained item by item | §7.1, §7.2 — 8 PW across four named units |
| `AC-06` | The register is regenerable from the source specifications without hand edits | `CDR-11`; §11.4 `cd-register.yaml` |
| `AC-07` | `FF-16`'s enablement conditions are stated with owners and dates | §10, five conditions |
| `AC-08` | Every figure carries an enumeration timestamp | Front matter and §3 |

**Definition of done.** Complete when every criterion above is met, `PGD-000`'s `BE-005` row moves to
✅ with a fresh timestamped enumeration, `AR-007` §3.2 is revised to show the issued form (§10
condition 3), and the approver has signed.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-02` §5 | Supplies the permanent unit identifiers `CDR-02` binds to |
| Upstream | `GV-003` | Owns `CR-nnn`; a new CD item with an effort change is a change request |
| Upstream | `GV-011` | Configuration management; this register is a configuration-identification instrument under it |
| Upstream | `AR-005` | Module ownership; a CD item's owner is the module that owns the capability |
| Downstream | `AR-007` §3.2 | `x_cd_id` in every manifest — **requires revision to the issued form** |
| Downstream | `AR-012` `FF-16` | Enabled by §10 |
| Downstream | `BE-002` | Commit scope and branch scope are issued identifiers |
| Downstream | `BE-003` `GW-04` | Branch naming |
| Downstream | `BE-004` `REPO-09` | Directory layout and `CODEOWNERS` |
| Downstream | `BE-006` `CBS-04` | `component.yaml` carries the issued identifier |
| Downstream | `BE-008` `SPR-07` | The backlog epic layer |
| Downstream | `QA-004`, `RQ-004` | Test and requirement traceability terminate on a CD item |
| Lateral | All 79 `../../1000fix_ERP_Module/03_Modules/**` §16.2 | Source of the register; corrected under `CDR-11` |
| Lateral | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2 | Superseded by §6; crosswalked in §8 |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-002`](BE-002_Coding_Standards_and_Style_Guide.md) ·
[`BE-003`](BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-008`](BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md) ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../00_Programme_Governance_and_Control/GV-003_Decision_Log_and_Change_Control_Procedure.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0, §16.2 ·
all 67 `M*.md` and all 12 `P*.md` §16.2 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/_PORTAL_SUITE_AUDIT_REPORT.md` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.1–§8.4, §25.1.7, §25.3.1

**External standards**
ISO 10007:2017 *Quality management — Guidelines for configuration management* — verified 2026-08-18 ·
ISO/IEC/IEEE 24765:2017 *Systems and software engineering — Vocabulary* — verified 2026-08-18

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 331 items issued across 79 units; four legacy registers retired; 48 collisions resolved; 8 findings raised | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-005` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
