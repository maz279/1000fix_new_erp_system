---
id: MG-001
title: Data Migration Strategy
category: 09 — Data Migration & Cutover
code: MG
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration Lead
approver: Chief Technology Officer with Chief Financial Officer
standards_basis: >
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Data Integration & Interoperability, and Data
  Quality knowledge areas · PDMv2 (Practical Data Migration, 2nd edn, BCS 2012) — Landscape
  Analysis, Key Business Data Areas, Data Quality Rules, Migration Design · ISO 8000-61:2016 —
  data quality management process reference model · ISO/IEC 25012:2008 — data quality model
traces_to: >
  PGD-000 MG-001 · AUDIT-011 DM-01 (CRITICAL) · 06-03_Data_Migration_Strategy.md (planned, never
  written) · BRD §11.6.2 MIG-001…MIG-015 · 05-02 §12 MIG-01…MIG-07 · 00-04 RSK-014, ASM-03,
  DEP-05 · 06-02 gates G1-05, G2-06, G3-08 · GV-005 ISS-006 · DM-001 O-01
depends_on: DA-001 · DA-002 · DA-005 · DA-006 · SC-007 · GV-003 · GV-009 · DM-001 · DM-002
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 22:10 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# MG-001 — Data Migration Strategy

### Category 09 · Code `MG` · DAMA-DMBOK 2.0 · PDMv2 · ISO 8000-61:2016 · ISO/IEC 25012

---

> **Identifier notice — read before citing anything in this document.**
>
> Four identifier spaces in this estate are distinguishable only by digit count, and this document
> touches all four. Every citation below is qualified on first use and thereafter.
>
> | Space | Meaning | Owner |
> |---|---|---|
> | **`MG-001`…`MG-007`** | **The seven guiding documents of this category** | `PGD-000` |
> | `MG-01`…`MG-08` | **Schema-change rules**, a different thing entirely | `DA-001` §12; `AR-007` §MG |
> | `MIG-01`…`MIG-07` | Migration **standards** | `05-02` §12 |
> | `MIG-001`…`MIG-015` | Migration **requirements** | BRD §11.6.2 |
>
> `MS-nn` is **not used in this category**. It is already live twice — `GV-004` `MS-00`…`MS-12`
> (programme milestones) and `DM-001` `MS-01`…`MS-26` (migration standards). This document's local
> rules are **`MST-nn`**, verified unused across the workspace at 2026-08-18 22:10 (+06).
> Recorded as audit finding `MGA-02`.

---

## 1. Purpose

**A migration strategy states how data gets from a legacy estate into a new system, and the
1000FiX programme does not have one.** `06-03_Data_Migration_Strategy.md` was planned, the
filename was reserved in `FOLDER_STRUCTURE.md`, and the file was never written. `AUDIT-011` raised
that as its single **CRITICAL** finding, `DM-01`, and five separate content files record the same
absence independently as an open item.

This document is that strategy.

It does not repeat `DM-001`. `DM-001` is a 50 KB register that answers **what moves** — six
dispositions applied to every dataset in all 67 module `§16.4` sections, cut-off dates, historical
depth, the legacy-identifier rule and the personal-data position. It stops, deliberately and by
design, at the boundary of the technical mechanism, and says so in its own §2 out-of-scope table.

**This document owns everything on the other side of that boundary.**

### 1.1 The gap this document closes, stated exactly

`AUDIT-011` `DM-01` enumerates seven unspecified items and names the file that assumes each. This
category exists to specify them, and the allocation is stated here so that no item is written twice
and none is left to another document's assumption.

| # | Unspecified item | Assumed by | Requirement demanding it | Specified in |
|:--:|---|---|---|---|
| 1 | ETL / orchestration platform, retry semantics, checkpointing, idempotency keys | `DM-003` §4.6 | — | **`MG-003`** |
| 2 | Staging-layer architecture | `DM-011` `DQ-03` | `05-02` `MIG-02` | **`MG-003`** §4, with the environment position in **`MG-001`** §7 |
| 3 | Environment topology and masking mechanism | `DM-012` `LT-17` | `05-06` `NFR-086c` | **`MG-001`** §7 → `PE-002` ⛔ |
| 4 | **Rollback mechanics and their measured duration** | `DM-003` `SQ-08`, `DM-014` `CV-13`, trigger `T4` | BRD `MIG-007` | **`MG-007`** (mechanics), **`MG-005`** (measurement) |
| 5 | Merge reversibility for the burn-down period | `DM-011` `DQ-20` | — | **`MG-003`** §9.4 |
| 6 | Delta-capture mechanism during the parallel run | `DM-003` `SQ-13`, `DM-014` §4.8 | BRD `MIG-009` | **`MG-003`** §10 |
| 7 | **The migration tooling itself**, delivered to the Company, repeatable and re-runnable | Every load | **BRD `MIG-008`** | **`MG-003`** §3, and the **unallocated build component**, §11.3 below |

### 1.2 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The migration approach decision — big-bang, phased or parallel — derived, not assumed (§4) |
| 2 | The seam with `DM-001`…`DM-014`, stated rule by rule (§3) |
| 3 | The migration operating model: streams, roles, accountability, and who may stop a load (§5) |
| 4 | The migration lifecycle — the nine stages every dataset passes through (§6) |
| 5 | The environment and staging position, and its dependency on `PE-002` (§7) |
| 6 | Acceptance, tolerance and gate binding at programme level (§8) |
| 7 | The personal-data and residency position for migration processing (§9) |
| 8 | What is deliberately **not** migrated, and the authority that decided (§10) |
| 9 | The estimating position: why migration effort is currently unknowable, and what makes it knowable (§11) |
| 10 | Rules `MST-01`…`MST-31` (§12) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Which datasets move, and their disposition | **`DM-001`** | A business scope decision per module owner; this document does not reopen it |
| Which legacy systems exist and who holds them | **`DM-002`** | An inventory; **`MG-002`** specifies how each is profiled and extracted |
| Load order and tier dependencies | **`DM-003`** | Derived from `05-02` §8 foreign keys; **`MG-003`** executes it |
| Field-level source-to-target mapping | **`DM-004`…`DM-010`** | Seven workbooks, plus two unregistered domains (`AUDIT-011` `DM-02`) |
| Quality rules, matching, survivorship | **`DM-011`** | The rule content; **`MG-003`** §9 makes it executable |
| Load file formats | **`DM-012`** | The business-facing templates |
| Reconciliation **report format** | **`DM-013`** | **`MG-004`** owns the reconciliation **plan** and its evidence pack |
| Freeze windows and branch **communication content** | **`DM-014`** | **`MG-006`** owns the operational **runbook** |
| Post-go-live data quality management | `DA-008` | `DM-011` ends at cutover; `DA-008` begins after it |
| Legacy **decommissioning** — retirement, licence termination, proof it is off | `RL-006` ⛔ | Migration ends at parallel-run exit; decommissioning is a separate discipline |
| Schema-change migrations (Odoo module upgrades) | `DA-001` §12 `MG-01`…`MG-08`; `AR-007` | A different activity that shares a word |

### 1.3 Intended audience

| Audience | What they use this document for |
|---|---|
| **CTO** | §4 approach, §11 the estimating position, §12 the rules that bind delivery |
| **CFO** | §8 finance tolerances, §10 what is written off, §4.4 why W3 is period-end bound |
| **Data Migration Lead** | The whole document; §5 is the operating model they run |
| **Implementation partner / vendor** | §6 lifecycle and §12 rules are contractual — see Category 14 |
| **Module business owners** | §5.3 — what accountability actually lands on them |
| **Programme Director / PMO** | §11 — why no migration-execution estimate exists yet |
| **Legal Counsel / DPO** | §9 — the lawful-basis position, stated as unresolved rather than assumed |
| **Branch Operations Lead** | §4.4 and §10.2 — why counting, not loading, is what W2/W3/W5 ask of branches |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / area | How this document conforms | Departure and rationale |
|---|---|---|---|
| **DAMA-DMBOK 2.0** (2024 maintenance revision) | Ch. 8 Data Integration & Interoperability — *Design Data Integration Solutions*; Ch. 13 Data Quality | The nine-stage lifecycle (§6) is the DMBOK extract-transform-load-verify cycle with profiling and reconciliation elevated to gates | DMBOK treats migration as a project inside integration. This programme has **nine** migrations, so §5 makes the operating model permanent rather than project-shaped |
| **PDMv2** — *Practical Data Migration*, 2nd edn, Johny Morris, BCS 2012 | Landscape Analysis; Key Business Data Areas; Data Quality Rules; Migration Design; System Retirement Plans | `DM-002` is Landscape Analysis; `MG-002` is its profiling arm. `DM-001`'s dispositions are Key Business Data Areas. **PDMv2's central claim — that migration is a business activity with a technical component — is adopted verbatim** (§5.3) | PDMv2 assumes one migration into one target. §4 adapts it to nine waves with a live target |
| **ISO 8000-61:2016** | Process reference model: *data quality planning · control · assurance · improvement* | §6 stages 2–4 are planning and control; `MG-004` is assurance; `DA-008` carries improvement past go-live | ISO 8000-61 is an organisation-level model. Applied here to a bounded migration programme, its *maturity assessment* arm (ISO 8000-62) is not used |
| **ISO/IEC 25012:2008** | Inherent data-quality characteristics | The profiling dimensions in `MG-002` §4 map to accuracy, completeness, consistency, credibility, currentness | `DM-011` already selects four dimensions. Not re-derived — adopted (`MST-04`) |
| **BRD §11.6.2 `MIG-001`…`MIG-015`** | Contractual migration requirements | §13 traces every one of the fifteen to the document that discharges it | — |
| **`05-02` §12 `MIG-01`…`MIG-07`** | Programme migration standards | Adopted unchanged; §12 does not restate them as new rules | — |

> **Why a book is cited as a standards basis.** There is no ISO standard for *data migration* as a
> discipline. ISO 8000 governs data quality; DMBOK governs data management; neither specifies a
> migration method. **PDMv2 is the recognised method**, published by BCS, and naming it is more
> honest than inventing a structure and calling it conformant. Rule `PG-06` requires the standard to
> be named; where none exists, it requires the departure to be stated. This is that statement.

### 2.2 Source material relied on

| Source | Location | What it establishes | Verified |
|---|---|---|---|
| `DM-001` Scope Register | `../../project_content/12_Data_Migration_Content/DM-001_*.md` | Six dispositions; the disposition of every §16.4 dataset; cut-offs; `MS-01`…`MS-26` | 2026-08-18 |
| `DM-002` Source Inventory | *ibid.* `DM-002_*.md` | **48 legacy sources in 8 classes**; custodians; extract methods; `SI-01`…`SI-12` | 2026-08-18 |
| `DM-003` Sequencing Plan | *ibid.* `DM-003_*.md` | Tiers `X0`…`X9`; per-wave load sequence; `SQ-01`…`SQ-18` | 2026-08-18 |
| `DM-011` Quality Standard | *ibid.* `DM-011_*.md` | Profiling dimensions; cleansing; matching bands; `DQ-01`…`DQ-26` | 2026-08-18 |
| `DM-013` Reconciliation Spec | *ibid.* `DM-013_*.md` | Five classes R1–R5; exceptions E1–E9; `RV-01`…`RV-12` | 2026-08-18 |
| `DM-014` Cutover Checklist | *ibid.* `DM-014_*.md` | Five phases P0–P4; checkpoints C1–C9; triggers T1–T7; `CV-01`…`CV-22` | 2026-08-18 |
| `AUDIT-011` | `../../project_content/_AUDIT/AUDIT-011_*.md` | 12 findings, 10 open; `DM-01` CRITICAL | 2026-08-18 |
| BRD | `../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6.1, §6.5, §11.6 | Legacy landscape; decommission commitment; `MIG-001`…`MIG-015` | 2026-08-18 |
| TSS | `../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2, §14 | Block 3 `CD-233`…`CD-248`; environment ladder; residency zones | 2026-08-18 |
| `DA-001` | `../03_Data_and_Information_Architecture/DA-001_*.md` | **The target schema** — 1,335 tables, standard column contract, §10 residency split | 2026-08-18 |
| `SC-007` | `../05_Security_Privacy_and_Compliance/SC-007_*.md` | Residency zones `Z1`–`Z4`; the transfer gate; quiet-copy prohibitions | 2026-08-18 |
| `GV-009` | `../00_Programme_Governance_and_Control/GV-009_*.md` | Gate criteria `G1-05`, `G2-06`, `G3-08`, `G5-01` and their evidence classes | 2026-08-18 |
| `GV-005` | `../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` | `ISS-006` — 48 sources unprofiled, **Critical** | 2026-08-18 |

### 2.3 Findings this document closes, and findings it cannot

| Finding | Source | Position after this issue |
|---|---|---|
| `AUDIT-011` **`DM-01`** — migration has a content specification and no technical specification | `AUDIT-011` | **Closed by the category**, not by this document alone. All seven items of §1.1 are now allocated to an issued document |
| `DM-001` `O-01`, `DM-003` `O-01`, `DM-011` `O-05`, `DM-013` `O-05`, `DM-014` `O-01` | Five content files | **Closed.** Each named `06-03` as absent; the content it required is `MG-001`…`MG-007` |
| `AUDIT-011` `DM-03` — all 48 sources unprofiled | `AUDIT-011`; `GV-005` `ISS-006` | **Not closed.** `MG-002` specifies the profiling; performing it is an execution act. §11 states what it unblocks |
| `AUDIT-011` `DM-02` — two migration domains have no workbook | `AUDIT-011` | **Not closed — outside this category.** A `DM-015`/`DM-016` registration is the Programme Content Lead's act under `CM-R1`. §10.3 records the consequence for scope |
| `AUDIT-011` `DM-05` — the physical-count programme is in no plan | `AUDIT-011` | **Partly.** §10.2 states the position and `MG-006` schedules it; **resourcing it is `GV-007`'s act** |
| `AUDIT-011` `DM-10` — transparency notice one wave late | `AUDIT-011`; `SC-003` | **Not closed.** §9.3 states it as unresolved and names the decision owner. It cannot be closed by an engineering document |

---

## 3. The Seam With Category 12 Content

> **`MST-01` — a rule is written once.** Where `DM-001`…`DM-014` already state a rule, this category
> **adopts it by citation and does not restate it**. A restated rule is a rule with two versions, and
> the second one drifts. This is the same discipline `DA-008` §2 applies to `DM-011`/`RP-016`.

| Question | Answered by | This category adds |
|---|---|---|
| *What moves, and what does not?* | **`DM-001`** dispositions `M`/`A`/`N`/`C`/`L`/`P` | Nothing. Adopted whole |
| *From where?* | **`DM-002`** 48 sources | **`MG-002`** — how each is profiled, extracted, and proven intact |
| *In what order?* | **`DM-003`** tiers `X0`–`X9` | **`MG-003`** — the orchestration that executes the order, and what happens when a tier fails |
| *Mapped to what?* | **`DM-004`…`DM-010`** | **`MG-003`** — the transformation-rule catalogue structure the workbooks compile into |
| *Validated how?* | **`DM-011`** rules; **`DM-013`** report | **`MG-004`** — the plan: who runs it, on what evidence, signed by whom, retained how long |
| *Proven how?* | **`DM-013`** R1–R5, E1–E9 | **`MG-004`** — the evidence pack, the independent check, the gate binding |
| *Frozen when?* | **`DM-014`** phases and instants | **`MG-006`** — the runbook: command structure, hour-by-hour, abort authority |
| *Undone how?* | **Nobody** | **`MG-007`** — mechanics, point of no return, data-loss position |
| *Timed how?* | **Nobody** | **`MG-005`** — rehearsals, and the measurement that replaces every estimate |

**Three rules govern the seam.**

| # | Rule | Class |
|---|---|:--:|
| **`MST-01`** | A rule stated in Category 12 is adopted by citation, never restated | **H** |
| **`MST-02`** | Where this category and Category 12 conflict, **Category 12 wins on business scope and this category wins on technical mechanism**. A conflict is raised to `GV-003` as a decision, never resolved silently in one file | **H** |
| **`MST-03`** | A rule identifier keeps its meaning across both categories. No `MG` document allocates into `MS-`, `SI-`, `SQ-`, `DQ-`, `LT-`, `RV-` or `CV-` | **H** |

---

## 4. The Migration Approach

### 4.1 The decision, and why it is not a preference

Three approaches exist, and the estate has already constrained the choice to one. The derivation is
recorded because *"phased, obviously"* is an assertion; this is a proof.

| Approach | What it means | Feasible here? | Determining evidence |
|---|---|:--:|---|
| **Big-bang** | One cutover; all data; all modules; all sites | **No** | `06-01` delivers 67 modules across **nine waves over 36 months** (`GV-004` §5.2). There is no single instant at which all target tables exist |
| **Full parallel run** | Both systems operated as systems of record until confidence is reached | **No, as a whole-estate approach** | 51+ branches, 500+ staff, paper-based processes. `DM-014` §4.8 already prices two weeks of double entry as *"a real operational cost"*. Whole-estate parallel for 36 months is not affordable in staff hours |
| **Phased by wave, with a bounded parallel run per wave** | Each wave migrates its own datasets in its own cutover window, then runs parallel for a declared period before legacy withdrawal | **Yes** | `05-02` §12 `MIG-07` **already mandates** a two-week parallel run on service orders and finance; `M19` §16.4 mandates one full parallel month-end close; BRD §6.5 makes legacy withdrawal a gate criterion |

> **`MG-001-D-01` is therefore a ratification, not a choice.** The programme has been committed to a
> phased approach with a bounded per-wave parallel run since `05-02` and the BRD were written.
> **What was missing was anybody writing it down as the approach**, with its consequences enumerated.
> That absence is why `DM-001` `O-01` exists.

### 4.2 What "phased" costs, stated honestly

A phased migration is the right answer here and it is not the cheap answer. Recording the costs is
part of the strategy, because each one lands on somebody who has not yet been told.

| Consequence | Detail | Owner of the cost |
|---|---|---|
| **Nine cutovers, not one** | Nine freeze windows, nine runbooks, nine reconciliation cycles, nine go/no-go decisions | Migration team; branch operations |
| **Nine parallel runs** | Two weeks each on the affected functions, plus one full parallel month-end close at W3 | Operational staff — **unresourced**, `DM-014` `O-03` |
| **A live target that keeps changing** | Wave 5 loads into a schema that Waves 1–4 have already extended. A W1 transformation may need re-verifying at W5 | Migration team; `DA-001` §12 schema-change contract |
| **Cross-wave referential debt** | W1 loads parties; W4 loads their contracts. Between them a party may be merged, renamed or deactivated by live business use | **`MG-003`** §8 — the cross-wave key stability rule |
| **The legacy estate must survive longer** | `SRC-013`…`SRC-015` (HR) run until W5, month 22. Spreadsheet estates degrade | Function custodians (`DM-002`) |
| **Two systems of record coexist for 36 months** | Not for the same data — but a customer can have a W1 party record and a W5 employee record, with the W5 half still in a spreadsheet | Every function; this is the true cost of phasing |

> **`MST-05`.** The per-wave parallel run is **bounded and exited by a decision** (`DM-014` `C8`),
> never allowed to lapse. `DM-014` `CV-19` already states this; the cost above is why it is enforced.

### 4.3 Migration classes — not every wave is the same shape

Treating nine cutovers as nine instances of one procedure is the error this section prevents.
Enumerating `DM-003` §4.4 against `DM-014` §4.2 on 2026-08-18 produces **four distinct cutover
shapes**, each with a different dominant constraint and a different rehearsal need.

| Class | Waves | Dominant constraint | Freeze driven by | Rehearsal requirement (`MG-005`) |
|:--:|:--:|---|---|---|
| **A — Volume** | **W1** | Record count: 100,000+ parties, 100,000+ addresses, **300,000–600,000 devices** (`M17` estimate, unverified) | Load and reconcile duration | **Timed dress rehearsal on production-sized data.** The window is arithmetic, and the arithmetic has never been run |
| **B — Physical** | **W2**, **W5** | **Human counting capacity at 51+ sites**; 200–400 van recalls | Counting throughput, not compute | **Rehearsal count at representative branches** (`DM-014` `CV-20`), plus a technical rehearsal |
| **C — Statutory** | **W3**, **W4** | Period-end alignment; exact finance tolerances; **Mushak 6.3 sequence continuity** | The accounting calendar and the NBR filing cycle | **Full rehearsal including a rehearsed trial-balance agreement** with the external auditor |
| **D — Bounded** | **W6, W7, W8** | Smaller populations; condition baselines; no statutory exposure | Module readiness | Technical rehearsal only |

> **`MST-06`.** A wave's migration class is declared before its rehearsal plan is written, and the
> class determines the rehearsal count (`MG-005` §3). Classing W2 as a volume problem — which it
> superficially resembles — produces a plan that adds servers to a problem bounded by storekeepers.

### 4.4 Why W3 cannot move, and W5 probably cannot either

Two waves have their cutover date fixed by something outside the programme's control. Stating this
in the strategy prevents it being discovered by a planner in month 12.

| Wave | External constraint | Consequence | Evidence |
|:--:|---|---|---|
| **W3** | The opening trial balance must be struck at a **period end** and agreed with the external auditor. A mid-period opening balance cannot be reconciled to a filed return | The W3 freeze window is **bound to the accounting calendar**, and the NBR Mushak 9.1 filing deadline of the 15th (`GV-004` §6.2) constrains it further | `DM-014` `CV-05`; `M19` §16.4; `G3-08` |
| **W5** | Year-to-date payroll balances are exact and compounding. Cutting over mid-assessment-year means carrying YTD across a system boundary inside a tax year | The W5 freeze is **preferentially aligned to an assessment-year boundary**, which may not coincide with month 22 | `M56` §16.4 — *"the most dangerous migration in the programme"*; `DM-009` `O-01`; `DM-014` `O-08` |

> **Open question `Q-01`** (§14): the W5 assessment-year alignment is undecided and it constrains
> the wave, not the other way round. `GV-004` §5.2 places W5 at months 19–22 with no reference to
> the tax calendar. **The two calendars have never been compared.**

---

## 5. The Migration Operating Model

### 5.1 Five streams, because migration is not one job

| Stream | Owns | Led by | Runs from |
|:--:|---|---|---|
| **S1 — Landscape & Extract** | The 48 sources: custodian engagement, profiling, extract, chain of custody | Data Migration Lead | **W0**, continuously |
| **S2 — Build & Transform** | Pipelines, transformation rules, staging schema, load harness | Migration Engineering Lead *(unappointed)* | W0 → each wave |
| **S3 — Business Data** | Dispositions `N` and `C`: authoring, counting, agreeing, confirming | **Module business owners** | W0 → W8 |
| **S4 — Assurance** | Reconciliation, evidence packs, sign-off, gate submission | QA Lead with domain owners | Per load |
| **S5 — Cutover Operations** | Runbook, command, communications, checkpoints, fallback | Data Migration Lead with Change Lead | Per wave |

> **`MST-07` — S3 is a business stream, not a migration-team stream.** `DM-001` §4.8 counts **34
> datasets produced by people, not pipelines** — 22 `N` (author new) and 12 `C` (count). Placing
> them in a technical stream is how they get estimated by engineers and delivered by nobody.

### 5.2 Accountability — who may stop a load

| Decision | Held by | Delegable? | Source |
|---|---|:--:|---|
| A source may be extracted | Data Migration Lead, on `profiling_status ≥ reported` | No | `DM-002` `SI-01` |
| A transformation rule is correct | The domain's business owner | No | `DM-011`; `MST-08` |
| A load may run in production | The domain owner, recorded | No | `DM-003` `SQ-17` |
| A reconciliation is accepted | The domain signatory in `DM-013` §2.7 | **No** | `RV-11` |
| **Go / no-go at a cutover** | **CTO with the Programme Director**, jointly | **No** | `DM-014` `CV-14` |
| Fallback is invoked | Any trigger `T1`–`T7` fires it automatically; **the CTO may not override a trigger** | No | `DM-014` `CV-15`; **`MST-09`** |
| A tolerance is set | The accountable owner, **before** the first load | No | `RV-08` |
| A tolerance is changed after a load has run | **Nobody.** It is a new control, recorded as a change | — | `DQ-05`; **`MST-10`** |

> **`MST-09` is the load-bearing rule of this section.** `DM-014` `CV-15` states that fallback is
> triggered by a rule, not a mood. This document makes the corollary explicit: **the go/no-go
> authority and the fallback authority are not the same authority.** A CTO who can wave through a
> failed reconciliation at 04:00 has a trigger list that is advisory. Recorded as decision
> `MG-001-D-04`.

### 5.3 What actually lands on the business

PDMv2's central claim is that migration is a business activity with a technical component. The
enumeration below tests that claim against this estate and confirms it.

| Business commitment | Scale | Wave | In any plan? |
|---|---|:--:|:--:|
| Physical stock count at every location | 10,000 SKUs × up to 51 sites | W2 | **No** — `AUDIT-011` `DM-05` |
| Van recall and count | 200–400 vans | W2 | **No** |
| Brand consignment confirmation, in writing | 17+ brands | W2 | **No** |
| Witnessed cash count at every location | 51+ branches, 200–400 field floats | W3 | **No** |
| Top-50 customer balance confirmation, in writing | 50 confirmations | W3 | **No** — `M20` §16.4 |
| Full fixed-asset physical verification | 8,000–20,000 assets | W5 | **No; and no owner** — `DM-001` `O-06` |
| Test-equipment audit | Every branch and workshop | W5 | **No; and no owner** |
| Leave-balance agreement with each employee | 500+ individual agreements | W5 | **No** |
| Supervisor competency assessment | 500+ employees | W5 | **No** — `SRC-038`, *"the hard one"* |
| IT-asset physical audit | ~2,500 assets | W6 | **No; and no owner** |
| Delegation-of-authority capture | All limits in force | W3 | **No** — `SRC-039` |
| Statutory obligation discovery | Multi-week exercise | W1–W4 | **No** — `SRC-040` |
| **Two weeks of double entry per wave, plus one full parallel close** | All affected staff × 9 | Every wave | **No** — `DM-014` `O-03` |

**Against this, `06-01` §Resourcing allocates Data Owners at 20% through W1–W5.**

> **`MST-11`.** Every disposition `N` and `C` dataset has a **named owner, a start date and an
> effort figure in `GV-004`** before its wave's build starts. A dataset the business must produce,
> with no date, is not a plan — it is a discovery scheduled for the cutover weekend. This is
> `AUDIT-011` `DM-05` restated as an enforceable rule, and it is **not discharged at this issue**;
> §14 `Q-02` carries it.

---

## 6. The Migration Lifecycle

**`MST-12`: every dataset passes through all nine stages, in order, and a stage is complete only on
its stated evidence.** Stages may overlap across datasets; they may not be skipped within one.

| # | Stage | What happens | Exit evidence | Owning document |
|:--:|---|---|---|---|
| **1** | **Register** | The dataset is dispositioned; its sources are identified | A row in `DM-001` §4.2 and in `DM-002` | `DM-001`, `DM-002` |
| **2** | **Profile** | The source is measured — completeness, validity, duplication, staleness, encoding | A profiling report accepted by the data owner | **`MG-002`** |
| **3** | **Map** | Source fields are mapped to `DA-001` targets with a stated rule per field | A completed workbook row with a transformation rule id | `DM-004`…`DM-010`; **`MG-003`** §7 |
| **4** | **Cleanse** | Correction in the source or the staging layer — **never during load** | A cleansing run report; residuals in the remediation queue | `DM-011`; **`MG-003`** §9 |
| **5** | **Build** | The pipeline is written, unit-tested and version-controlled | A passing pipeline test suite; a tagged release | **`MG-003`** |
| **6** | **Rehearse** | The load runs against production-sized data, timed, with a rehearsed rollback | A rehearsal report with **measured** durations | **`MG-005`** |
| **7** | **Load** | The production load runs inside the cutover window | A completed batch with a batch id and a run log | **`MG-003`**, **`MG-006`** |
| **8** | **Reconcile** | R1–R5 are computed; exceptions are categorised; the owner signs | A signed `DM-013` report in the evidence pack | **`MG-004`** |
| **9** | **Accept** | The wave gate consumes the evidence; legacy withdrawal proceeds | A gate decision recorded in `GV-009` | `GV-009`; `RL-006` |

> **`MST-13` — stage 2 gates stage 3.** A mapping written before profiling is a hypothesis. **All
> seven existing workbooks are currently in that state** (`AUDIT-011` `DM-03`). They are not
> discarded — they are **re-verified** after profiling, and **the re-verification effort is in no
> estimate** (`Q-03`).

> **`MST-14` — stage 6 gates stage 7.** No production load runs against a pipeline that has not
> completed a rehearsal with a measured rollback duration. `05-06` `OPS-07`, BRD `MIG-005`,
> `DM-003` `SQ-11` and `DM-014` `CV-13` all require this independently; **`MG-005` is where it
> becomes schedulable.**

---

## 7. Environments and the Staging Layer

### 7.1 The position

`DM-011` `DQ-03` requires cleansing to happen *"in the source or a staging layer"*. **No document
describes the staging layer.** `DM-012` `LT-17` requires masking; no document says by what mechanism.
This section states the requirement; `MG-003` §4 designs the layer; **`PE-002` must specify the
environment that hosts it, and `PE-002` does not exist.**

| Environment | Migration role | Data class permitted | Status |
|---|---|---|:--:|
| `local` | Pipeline unit tests | **Synthetic only** — `BE-001` permits no path by which real data reaches a workstation | ✅ `BE-001` |
| `dev` | Pipeline integration tests | Synthetic + masked extracts | ⛔ `PE-002` |
| **`migration-staging`** | **The staging layer: land, profile, cleanse, transform, validate** | **Real, unmasked, non-residency-classified** — see §7.2 | ⛔ **Does not exist in any document** |
| `staging` | Trial migration with business UAT (`MIG-005`) | Production clone, **PII-masked** (TSS §14; `NFR-086c`) | ⛔ `PE-002` |
| **rehearsal** | Production-sized timed dress rehearsal (`MG-005`) | **Production-sized**; masking position unresolved — §7.3 | ⛔ **Does not exist** |
| `prod` | The load target | Real | ⛔ `PE-001`, `PE-002` |

> **`MST-15`.** The **`migration-staging`** environment is a distinct environment with its own
> access control, its own retention and its own destruction date. It is **not** `staging`. `staging`
> is masked by `NFR-086c`; a masked environment cannot host cleansing, because the cleansing is of
> the real values. Conflating the two is how unmasked personal data ends up in a UAT environment.

### 7.2 The contradiction this section must state rather than resolve

Three rules are simultaneously in force and they are not jointly satisfiable as written.

| # | Rule | Source |
|:--:|---|---|
| 1 | Cleansing happens in the source or **a staging layer** | `05-02` `MIG-02`; `DM-011` `DQ-03` |
| 2 | **Non-production environments never contain unmasked residency-classified data** | `05-06` `NFR-086c`; `DM-001` `MS-24`; `SC-007` §7 |
| 3 | Residency-classified values are read and written **only through the residency service `CD-233`** — *"no direct query, no migration script, no backfill"* | `AR-001` `LB-08`; `DA-001` `RS-03`; `AR-007` `MG-07` |

**Resolution taken here, and it is a decision, not a reading.**

| Data | Where it is cleansed | Mechanism |
|---|---|---|
| Non-residency-classified personal data (name, address, mobile, email) | **`migration-staging`**, unmasked | Standard pipeline; `migration-staging` is treated as a **production-class environment for access control**, not as a non-production environment |
| **Residency-classified values** (NID, passport, TIN, biometric template, recovered-data index, seller KYC) | **Never in staging at all** | A **second-pass load**, after the primary record exists, writing **through `CD-233`** only. `DM-003` `SQ-10` already sequences this; **`MG-003` §6 designs it** |

> **`MST-16`.** `migration-staging` is classified as a **production-class environment** under
> `DA-005`, with production access control, production audit logging (`SC-010`), a declared
> retention period and a **destruction date tied to the wave's parallel-run exit**. This is
> recorded as decision **`MG-001-D-02`** and referred to `SC-007` §6 (the transfer gate) and
> `PE-002` for sizing. **It is the single largest thing this document asks of infrastructure.**

> **`MST-17`.** No residency-classified value enters a pipeline, a staging table, a log, an error
> message, a reject file, a reconciliation report or a rehearsal dataset. `MG-003` §6 states the
> mechanism; `SC-007` §7's quiet-copy prohibitions apply unchanged. **A reject file containing a
> failed NID row is a residency breach**, and reject files are the least-guarded artefact in any
> migration.

### 7.3 The rehearsal-data problem, unresolved

`MG-005` requires rehearsal against **production-sized** data, and `05-06` `OPS-07` requires the
same for schema migrations. Two positions collide:

- Production-**sized** synthetic data does not test the migration, because the defects being hunted
  are in the *real* source values — the mojibake, the duplicates, the mixed encodings.
- Production-**derived** data in a rehearsal environment is a processing act on personal data with
  no stated basis, and `NFR-086c` forbids the residency-classified part outright.

**Position taken:** the rehearsal environment uses **real non-classified data under
`migration-staging`'s production-class controls** (`MST-16`), with the classified fields absent and
their second-pass load rehearsed **against synthetic keys only**. The residual risk — that the
`CD-233` second pass is the least-rehearsed step in the most sensitive load — is recorded as
`Q-04` and reported to `SC-003` (DPIA).

---

## 8. Acceptance, Tolerance and Gate Binding

### 8.1 Migration is a criterion at four of nine gates

| Gate | Criterion | Evidence class | Signatory | Status today |
|:--:|---|:--:|---|---|
| **G1** | `G1-05` Customer and device data migrated and reconciled | **E7** control totals + **E4** signed reconciliation | Data owner | **At risk — all 48 sources unprofiled** (`ISS-006`) |
| **G2** | `G2-06` Inventory accuracy ≥ 95% at migrated locations, verified by count | **E7** physical count reconciliation | Data owner | Count programme unresourced |
| **G2** | `G2-07` Van stock reconciling daily, variance < 2% | **E7** | Inventory Manager | Depends on `G2-06` |
| **G3** | `G3-08` Financial history migrated and reconciled to the trial balance | **E7** + **E4** | **CFO — non-delegable** | Auditor not engaged |
| **G5** | `G5-01` First payroll run processed, validated and paid with **zero** errors | **E7** + **E4** | HR Director + CFO | `MD-043` slabs unverified — `AUDIT-011` `DM-09` |

> **`MST-18`.** A gate criterion citing migration is satisfied by the **evidence pack** defined in
> `MG-004` §6, not by a status report. `GV-009` classes `E4` and `E7` are signature and reconciliation
> evidence respectively; a slide saying *"migration complete"* is neither.

### 8.2 The tolerance hierarchy

`DM-013` `RV-08` sets tolerances per domain. This document states the hierarchy that governs them,
because *"exact"* appears in five places and needs one definition.

| Tier | Meaning | Domains | Variance permitted |
|:--:|---|---|---|
| **T-EXACT** | Zero variance. A single unit of difference fails the load | GL, AR/AP, cash, bank, tax, **payroll YTD** | **None** |
| **T-ZERO-UNACCOUNTED** | Every source record is loaded, rejected or excluded, with no residual | **All loads** | **None** on the identity; rejections may exceed zero within their own tolerance |
| **T-DECLARED** | A numeric threshold set by the owner before the first load | Party rejection rate, inventory accuracy (≥95%), van variance (<2%) | As declared |
| **T-REPORTED** | No threshold; the figure is published and burned down | Asset provisional share, merge count, quarantine lines | n/a |
| **T-NONE** | The class does not apply; the reason is stated | Per `RV-01` | n/a |

> **`MST-19`.** *"Exact"* means **T-EXACT**: zero variance, not "within rounding". `M51` §16.4's
> position on the Mushak 6.3 sequence — *"the first thing an NBR audit looks for, and it cannot be
> corrected afterwards"* — is why this needed defining rather than assuming.

> **`MST-20`.** A **conditional pass** (`RV-09`) is available at T-DECLARED and T-REPORTED only.
> **T-EXACT and T-ZERO-UNACCOUNTED have two outcomes: pass or fail.** There is no conditional
> opening trial balance.

---

## 9. Personal Data, Residency and the Lawful Basis

### 9.1 What migration processes, at what scale

| Wave | Population entering a new controller environment | Classification |
|:--:|---|---|
| **W1** | **100,000+ customers**, ~2,000 corporate accounts, **100,000+ addresses**, **300,000–600,000 devices**, 500+ employees as parties | S2, with S3 fields deferred |
| W3 | Vendor contacts, bank mandates, 40–120 active suppliers | S2 |
| W4 | 3,000–5,000 contract counterparties; ~2,000 claim records | S2 |
| **W5** | **500+ employee records** — personnel files, NID copies, salary, bank details, leave, competency | **S3** |
| W6 | Data-recovery job records — **residual customer data from past recovery work** | **S3, disposition `P` (purge)** |
| W7 | 500–2,000 marketplace sellers with KYC documents | **S3** |

### 9.2 The three positions this document adopts unchanged

`M33` §16.4 states three rules; `DM-001` adopts them as `MS-19`…`MS-21`; this document adopts them
by citation under `MST-01` and adds nothing:

1. **Profile before load** — duplicate rate, completeness and validity measured on the source before
   any load and reported to the CCO. Executed by **`MG-002`**.
2. **No consent is inferred** — historical parties migrate with **no consent record**; consent is
   captured at the next interaction against the current notice.
3. **Sensitive fields last** — NID, TIN, passport, biometric and recovered-data fields migrate only
   after the Bangladesh-resident store is live and verified. Executed by **`MG-003`** §6 second pass.

### 9.3 What remains unresolved, and why this document cannot resolve it

> **The lawful basis for the migration processing itself is not recorded anywhere in the estate.**

`M33` rule 2 and `MS-20` correctly forbid *inferring* consent from prior dealings. That is right, and
it has a consequence nobody has followed through: **if consent is not the basis, some other basis
applies, and no document names it.** `LG-008` (privacy notice) and `LG-012` (residency statement)
were written 2026-08-17, stand at `Draft`, and are **registered at W2** — one wave after the W1
processing they would need to cover.

| Open | Why the file existing does not close it |
|---|---|
| `LG-008` is a **W2** artefact; the first party load is **W1** | A notice arriving after the processing it describes does not discharge `05-06` `NFR-092` |
| Neither file **determines a lawful basis** for a bulk controller-side migration | `LG-008` is customer-facing consent copy, not a basis determination |
| `SC-003` (DPIA) is issued and identifies the processing; it does not **decide** the basis | A DPIA assesses; a controller decides |

**`MST-21`.** No production load of personal data proceeds until the lawful basis is recorded in
`GV-003` as a programme decision with a named legal owner. This is a **hard rule against a P0 W1
load**, and stating it is uncomfortable precisely because it is the correct position. Escalated as
`Q-05` and referred to `GV-005` RAID as an issue, not a risk — the processing date is fixed and the
basis is absent.

> This extends `AUDIT-011` `DM-10` and `AUDIT-010` `HC-01`. It is the **third** finding in the
> programme concerning the *lawfulness* of a planned activity rather than its correctness, and it
> lands at the largest population and the earliest wave of the three.

### 9.4 Residency at migration — the `MIG-014` requirement

BRD `MIG-014` requires *"residency classification applied at migration; no residency-restricted
field lands in the regional store."* Combined with `AR-001` `LB-08` (*"never by direct query, not
even in a migration or a backfill"*), this makes the second-pass design of `MG-003` §6 the **only
lawful path** for six field types.

| Field | Regional table (`Z3`) | Load path | Gate |
|---|---|---|---|
| National ID number | `fix_identity_document` | **`CD-233` second pass** | After resident store verified |
| Passport number | `fix_identity_document` | `CD-233` second pass | *ibid.* |
| TIN | `fix_party`, `hr_employee` | `CD-233` second pass | *ibid.* |
| Biometric attendance template | `fix_attendance_record` | `CD-233` second pass; **W5** | *ibid.* |
| Recovered customer data + index | `fix_recovered_inventory` | **Disposition `P` — purged, not migrated** | Before W6 |
| Marketplace seller KYC | `fix_mp_seller_document` | `CD-233` second pass; W7 | *ibid.* |

> **`MST-22`.** `CD-233` is a **W1** component (TSS §8.2 Block 3). The W1 party load therefore
> depends on it existing at W1, and **`BE-005` records that Block 3 effort is in no baseline**
> (`BEA-05`). If `CD-233` slips, the S3 second pass slips, and `DM-003` `SQ-10` holds those fields
> out of the load indefinitely — which is the correct behaviour and a growing backlog.

> **`MST-23`.** `DA-001` §10.4 records verification finding `PGD-A5-03`: the statutory obligation
> may be a **synchronised in-country mirror** rather than exclusive residency. **This does not change
> the migration design.** The second-pass-through-`CD-233` path is correct under either reading, and
> is the cheaper one to unwind. No migration decision waits on `DEP-31`.

---

## 10. What Is Not Migrated

### 10.1 The position

`DM-001` §4.2.5 and §4.2.6 enumerate 20 `L` (leave) and 4 `P` (purge) datasets. This document does
not re-enumerate them. It states the two rules that make the decisions durable.

| # | Rule | Class |
|---|---|:--:|
| **`MST-24`** | A dataset that is not migrated has a **recorded decision naming what is given up**, and the affected baseline is referred to `RP-015`. "We decided not to" without a consequence statement is not a decision | **H** |
| **`MST-25`** | A **purge** (`P`) produces a **destruction record**, retained per `DA-006`. Purging without evidence is indistinguishable from losing | **H** |

### 10.2 Counting is not migrating

Four modules — `M15` inventory, `M49` fixed assets, `M50` cash, `M45` test equipment — independently
refuse to load their legacy spreadsheets and require a physical count instead. `M15` §16.4 states
the reasoning that governs the whole category:

> *"The spreadsheets are 75% accurate; loading them guarantees that inventory accuracy never
> recovers, because every subsequent variance is contaminated by an unknown opening error."*

> **`MST-26`.** A disposition `C` dataset **has no load step**. `DM-003` `SQ-12` already states this.
> What this document adds: **a `C` dataset appears in `GV-004` as a business activity with a
> duration, a resource and a predecessor**, or it will be discovered during the freeze. See `Q-02`.

### 10.3 Two domains are in scope and have no specification

`AUDIT-011` `DM-02` found two migration domains declared by the modules and registered by nobody:

| Domain | Volume | Load wave | Consequence for this strategy |
|---|---|:--:|---|
| **Documents and paper archive** | **500,000+ paper service records**; 3,000–5,000 contract originals; 7 years of statutory financial records | **W3–W6** | The largest single population in the estate has **no mapping specification**. `MG-003` cannot design a transformation for it; `MG-005` cannot rehearse it |
| **Catalogue and pricing** | ~1,200 service descriptions; **~18,000 parts rows, 30–40% duplicated**; ~60,000 OEM references; **~1,200 price points across 51+ inconsistent branch sheets** | **W1** *(catalogue)*, W3 *(pricing)* | **This is a W1 dataset.** `M37` calls it *"the single largest change-management task of Wave 1"* and it has no workbook |

> **`MST-27`.** A dataset with a `DM-001` disposition of `M` and **no mapping workbook** is
> **blocked at lifecycle stage 3** and may not proceed to build. It is not silently omitted and it
> is not improvised at load time. **The catalogue domain blocks part of W1 today.** Registering
> `DM-015`/`DM-016` is the Programme Content Lead's act under `CM-R1`; this rule states what happens
> until then. Recorded as `Q-06`.

---

## 11. The Estimating Position

### 11.1 Why no migration-execution estimate exists

`GV-007` §7.3 excludes *"data migration execution beyond the `MG-*` documents"* from the programme
estimate, with the stated reason: *"48 sources are unprofiled; execution effort is unknowable until
`MG-002` completes."* **That exclusion is correct and it should not be quietly closed by a guess.**

The dependency chain is short and every link is currently broken:

```
  Profile 48 sources  (MG-002)
        │
        ├──► Measured volumes, duplicate rates, quality per source
        │           │
        │           ├──► Re-verify 7 mapping workbooks written against assumed structure
        │           ├──► Size the DM-011 review queue at three candidate thresholds  (AUDIT-011 DM-04)
        │           └──► Size the remediation and stewardship backlog
        │
        ├──► Transformation build effort  (MG-003)
        ├──► Rehearsal count and duration  (MG-005)
        └──► Cutover window arithmetic  (MG-006)  ──►  Rollback window feasibility  (MG-007 T4)
```

> **`MST-28`.** No migration-execution figure is published until `MG-002` profiling completes for the
> sources feeding that wave. A figure published earlier is an anchor, and `GV-007` `BEA-06` already
> records what happens when an unfounded figure becomes a baseline.

### 11.2 What profiling costs, so it can be funded

Profiling is itself work, and it is currently in nobody's budget. `MG-002` §8 derives the figure;
the shape is stated here because the strategy must say who pays for the thing that unblocks
everything else.

| Source class | Count | Effort driver | Can it be parallelised? |
|---|---:|---|---|
| `DB` | 4 | Schema discovery on undocumented databases; vendor access | Partly |
| `SS` | 14 | **Collection across 51+ branches** — the constraint is custodian availability, not parsing | Poorly — it is 51 conversations |
| `PORTAL` | 5 | Rate-limited manual download; no bulk export | No |
| `MAIL` | 2 | Human triage of thread-based records | No |
| `PAPER` | 12 | Sampling and volumetric estimation, not full read | Partly |
| `PEOPLE` | 3 | **Not profiling at all — an authoring programme** | No |
| `PUB` | 4 | Version pinning and adviser verification | Yes |
| `CFG` | 4 | Survey and credential inventory | Yes |

> **`MST-29`.** `SRC-001` (`station.1000fix.com`) and `SRC-002` (the legacy tracker) are **profiled
> and extracted first**, before any other work. BRD §6.5 withdraws both at **W2**; `DM-002` §10
> records that data not extracted before that date is **lost and unrecoverable**. This is the only
> irreversible deadline in the entire migration programme.

### 11.3 The build component that does not exist

**Enumerated 2026-08-18 22:10 (+06) against `BE-005` (331 items, 79 units) and TSS §8.2 Block 3
(`CD-233`…`CD-248`):**

| Test | Result |
|---|---|
| `BE-005` items whose description mentions migration, ETL or cutover | **0 of 331** |
| TSS Block 3 services scoped to legacy-to-ERP migration | **0 of 16.** `CD-243` is *warehouse* ETL (dbt) at **W4**; `CD-236` is route optimisation |
| A `CD` unit owning the migration tooling BRD `MIG-008` requires delivered | **None** |
| `CD-SVC-nn` space, reserved by `BE-005` §5.1 for cross-cutting services | **Deliberately empty at that issue** |

**The migration tooling has no identifier, no wave, no effort and no owner, while being a P0
contractual deliverable.** `MG-003` §3 specifies what must be built; **allocating `CD-SVC-nn` is the
Chief Architect's act under `BE-005` `CDR-01`**, and this document requests it rather than
performing it. Recorded as finding `MGA-01` and open question `Q-07`.

---

## 12. Governing Rules

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the
> same scale as `05-05` §1 and `DM-001` §4.9.

| # | Rule | Class |
|---|---|:--:|
| `MST-01` | A Category 12 rule is adopted by citation, never restated | **H** |
| `MST-02` | Category 12 wins on business scope; this category wins on technical mechanism; conflicts go to `GV-003` | **H** |
| `MST-03` | No `MG` document allocates into the `MS-`, `SI-`, `SQ-`, `DQ-`, `LT-`, `RV-` or `CV-` spaces | **H** |
| `MST-04` | Quality dimensions are `DM-011`'s four, mapped to ISO/IEC 25012; not re-derived | **C** |
| `MST-05` | The per-wave parallel run is exited by a decision, never allowed to lapse | **H** |
| `MST-06` | A wave declares its migration class (A/B/C/D) before its rehearsal plan is written | **H** |
| `MST-07` | Disposition `N` and `C` datasets belong to the business stream `S3`, not to migration engineering | **H** |
| `MST-08` | A transformation rule is confirmed correct by the domain's business owner, not by the migration team | **H** |
| `MST-09` | **The go/no-go authority may not override a fallback trigger.** The two authorities are separate | **H** |
| `MST-10` | A tolerance may not be changed after a load has run; a new tolerance is a recorded change | **H** |
| `MST-11` | Every `N` and `C` dataset has a named owner, a start date and an effort figure in `GV-004` before its wave's build starts | **H** |
| `MST-12` | Every dataset passes all nine lifecycle stages in order, on stated evidence | **H** |
| `MST-13` | Profiling gates mapping. A workbook written before its source was profiled is re-verified before build | **H** |
| `MST-14` | Rehearsal gates production load. No unrehearsed pipeline runs in production | **H** |
| `MST-15` | `migration-staging` is a distinct environment, never `staging` | **H** |
| `MST-16` | `migration-staging` is classified production-class: production access control, audit logging, retention and a destruction date | **H** |
| `MST-17` | No residency-classified value enters a pipeline, staging table, log, reject file, report or rehearsal dataset | **H** |
| `MST-18` | A migration gate criterion is satisfied by the `MG-004` evidence pack, not by a status report | **H** |
| `MST-19` | "Exact" means T-EXACT — zero variance | **C** |
| `MST-20` | T-EXACT and T-ZERO-UNACCOUNTED admit only pass or fail; no conditional pass | **H** |
| `MST-21` | No production load of personal data proceeds until the lawful basis is recorded in `GV-003` | **H** |
| `MST-22` | The S3 second pass depends on `CD-233` at W1; if it slips, S3 fields are held, not loaded | **H** |
| `MST-23` | The migration design does not wait on `DEP-31`; the `CD-233` path is correct under either residency reading | **C** |
| `MST-24` | A non-migrated dataset carries a recorded decision naming what is given up | **H** |
| `MST-25` | A purge produces a destruction record retained per `DA-006` | **H** |
| `MST-26` | A disposition `C` dataset appears in `GV-004` as a business activity with duration, resource and predecessor | **H** |
| `MST-27` | A disposition `M` dataset with no mapping workbook is blocked at lifecycle stage 3 | **H** |
| `MST-28` | No migration-execution figure is published before `MG-002` profiling completes for that wave's sources | **H** |
| `MST-29` | `SRC-001` and `SRC-002` are profiled and extracted first. Their data is unrecoverable after W2 | **H** |
| `MST-30` | Every migration artefact — pipeline, rule, template, runsheet — is version-controlled under `BE-003` and released under `BE-006` | **H** |
| `MST-31` | The migration tooling is **delivered to the Company**, repeatable and re-runnable, with its own README and runbook (BRD `MIG-008`) | **H** |

---

## 13. Requirement Traceability — BRD `MIG-001`…`MIG-015`

**Every contractual migration requirement is discharged by a named document.** Enumerated against
BRD §11.6.2 on 2026-08-18.

| # | Requirement | Pri | Discharged by | State |
|---|---|:--:|---|---|
| `MIG-001` | Field-level source-to-target mapping, per wave | P0 | `DM-004`…`DM-010` + **two unregistered domains** | ⚠ **Partial** — `MST-27` |
| `MIG-002` | Profiling before every load, reported to the data owner | P0 | **`MG-002`** | ✔ Specified; **unperformed** |
| `MIG-003` | Cleansing in the source, business owner accountable | P0 | `DM-011`; **`MG-003`** §9 | ✔ |
| `MIG-004` | Validation rules and reconciliation reports with control totals | P0 | `DM-013`; **`MG-004`** | ✔ |
| `MIG-005` | Trial migration into `staging` with business UAT before every cutover | P0 | **`MG-005`** | ✔ Specified; environment ⛔ `PE-002` |
| `MIG-006` | Signed reconciliation as a wave gate criterion | P0 | `DM-013` §2.7; **`MG-004`** §6; `GV-009` | ✔ |
| `MIG-007` | Documented, **rehearsed** rollback plan for every cutover | P0 | **`MG-007`** (plan) + **`MG-005`** (rehearsal) | ✔ Specified; **unrehearsed** |
| `MIG-008` | **Migration tooling delivered to the Company**, repeatable and re-runnable | P0 | **`MG-003`** §3, §12 | ⚠ **No build component exists** — `MGA-01` |
| `MIG-009` | Incremental / delta migration during the parallel run | P1 | **`MG-003`** §10 | ✔ |
| `MIG-010` | Audit trail preserved; legacy identifiers retained on every record | P0 | `DM-001` `MS-18`; **`MG-003`** §8 | ✔ |
| `MIG-011` | Bengali text conversion and UTF-8 normalisation | P1 | `DM-001` `MS-26`; **`MG-002`** §6, **`MG-003`** §7.3 | ✔ |
| `MIG-012` | Archive area for uncleansable records — retrievable, flagged, excluded | P1 | `DM-001` `MS-08`, `MS-10`; **`MG-003`** §11; `DA-006` §8 | ✔ |
| `MIG-013` | Financial history reconciled **to the trial balance** before Gate 3 | P0 | **`MG-004`** §4.2, §10.1; `G3-08` | ✔ Specified; auditor **not engaged** |
| `MIG-014` | Residency classification applied at migration | P0 | §9.4; **`MG-003`** §6; `SC-007` | ✔ |
| `MIG-015` | Lawful basis recorded; transparency notice addressed | P0 | §9.3 | ⛔ **Unresolved** — `MST-21`, `Q-05` |

**Count: 15 requirements · 11 fully discharged by specification · 2 partial · 1 blocked on a build
allocation · 1 blocked on a legal decision.**

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **`Q-01`** | **Is the W5 cutover aligned to the assessment-year boundary?** `GV-004` places W5 at months 19–22 with no reference to the tax calendar; `M56` makes YTD exactness non-negotiable | HR Director with CFO and PMO | **W3** | The W5 freeze window; `MG-006` §5 |
| **`Q-02`** | **Who resources the physical-verification programme?** 13 business commitments (§5.3) against Data Owners at 20%. `AUDIT-011` `DM-05` open | Programme Director with `GV-007` | **W0** | `G2-06`, `G3-08`, `G5-01`; `MST-11`, `MST-26` |
| **`Q-03`** | **What does re-verifying seven mapping workbooks after profiling cost?** `MST-13` requires it; no estimate exists | Data Migration Lead | **W1** | `GV-007` re-forecast |
| **`Q-04`** | **How is the `CD-233` second-pass load rehearsed** without production-derived classified values? §7.3 | Head of InfoSec with DPO | **W1** | `MG-005` §4; the S3 load |
| **`Q-05`** | **What is the lawful basis for the migration processing itself?** Not consent (`MS-20`); not named anywhere. 100,000+ data subjects at W1 | **Legal Counsel with the DPO** | **W1 — before the first party load** | **`MST-21` blocks every personal-data load** |
| **`Q-06`** | **Who registers `DM-015` catalogue/pricing and `DM-016` documents?** A W1 dataset is unspecified today | Programme Content Lead | **W1** | `MST-27`; part of the W1 load |
| **`Q-07`** | **Which `CD-SVC-nn` identifier owns the migration tooling, and in which wave?** BRD `MIG-008` is P0 and contractual | Chief Architect with `GV-007` | **W0** | `MG-003` build; every load |
| **`Q-08`** | **Is `migration-staging` funded and sized?** `PE-002` does not exist; §7 states the requirement against no infrastructure design | CTO with `PE-002` author | **W0** | The whole lifecycle from stage 4 |

> An open question with no owner and no needed-by date is an unrecorded risk. All eight are referred
> to `GV-005` RAID; `Q-02` and `Q-05` are referred as **issues**, not risks, because their trigger
> dates are already fixed.

---

## 15. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `MG-001-D-01` | Migration approach | Big-bang · full parallel · **phased by wave with bounded parallel run** | **Phased by wave** | The only option consistent with nine waves over 36 months and with `MIG-07`, which already mandates it | Nine cutovers, nine parallel runs, a live and changing target schema (§4.2) |
| `MG-001-D-02` | Classification of `migration-staging` | Non-production (masked) · **production-class (unmasked, controlled)** | **Production-class** | Cleansing operates on real values; a masked environment cannot host it. `NFR-086c` is satisfied by excluding classified values entirely, not by masking them | Production access control, audit logging, retention and a destruction date. Referred to `PE-002` and `SC-007` |
| `MG-001-D-03` | Residency-classified field loading | Single-pass with in-pipeline encryption · **two-pass through `CD-233`** | **Two-pass through `CD-233`** | `AR-001` `LB-08` forbids any migration script touching the store directly. Correct under both readings of `PGD-A5-03` | The most sensitive load is the least rehearsable (`Q-04`) |
| `MG-001-D-04` | Fallback authority | Go/no-go holder may override triggers · **triggers are absolute** | **Triggers are absolute** | An overridable trigger is advice. `DM-014` `CV-15` intends absolutes | The CTO can decline to go; the CTO cannot decline to fall back |
| `MG-001-D-05` | Whether to publish an interim migration-execution estimate | Publish an indicative range · **publish nothing until `MG-002`** | **Publish nothing** | `GV-007` already excludes it for the correct reason. An indicative range becomes a baseline | The programme carries an openly unsized workstream, which is honest and uncomfortable |

> Decisions with programme-wide effect are raised as `D-nnn` in `GV-003`. `MG-001-D-02` and
> `MG-001-D-04` are so raised; the remaining three are local.

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All seven `AUDIT-011` `DM-01` items are allocated to a named issued document | §1.1; the seven documents exist on disk |
| `AC-02` | The approach is derived from cited evidence, not asserted | §4.1 |
| `AC-03` | The seam with `DM-001`…`DM-014` is stated question by question, with no rule restated | §3 |
| `AC-04` | All fifteen BRD `MIG-nnn` requirements are traced to a discharging document with a state | §13 |
| `AC-05` | The staging-environment contradiction is stated and resolved by a recorded decision | §7.2; `MG-001-D-02` |
| `AC-06` | The lawful-basis gap is stated as unresolved with a named owner, not assumed closed | §9.3; `Q-05` |
| `AC-07` | The absence of a migration build component is measured, not asserted | §11.3, enumerated 22:10 (+06) |
| `AC-08` | Every local rule uses a prefix verified unused workspace-wide | `MST-nn`; verified 22:10 (+06) |
| `AC-09` | Every open question has an owner and a needed-by date | §14 |
| `AC-10` | Every cited path resolves | Verified at issue |

**Definition of done.** Complete when every criterion is met, the `PGD-000` row is updated with a
fresh enumeration timestamp, and the approver has signed. **The approval record cannot exist until
`GV-001` `CC-01` completes** — the qualified-✅ position of `PGD-A2-25` applies to this document as
to every other in the estate.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `DA-001`, `DA-002` | The target schema and field definitions every transformation lands in |
| Upstream | `DA-005`, `DA-006` | Classification of migrated data; archive and destruction rules |
| Upstream | `SC-007` | Residency zones and the transfer gate governing the S3 second pass |
| Upstream | `GV-003`, `GV-009` | Decision recording; the gates migration evidence feeds |
| Upstream | `DM-001`…`DM-014` | The content half of this category |
| Downstream | **`MG-002`…`MG-007`** | Every one implements a part of this strategy |
| Downstream | `QA-004` | Test data management consumes the masking and provisioning position of §7. **Issued during this session** — re-enumerated 2026-08-19 09:30 (+06); Category 08 holds 7 of 11 `QA` documents. The §7 seam must be reconciled between the two — see `MG-002`/`MG-005` and audit finding `MGA-07` |
| Downstream | `PE-002` ⛔ | Must size and specify `migration-staging` and the rehearsal environment |
| Downstream | `RL-002`, `RL-003`, `RL-006` ⛔ | Deployment plan, readiness assessment and legacy decommissioning consume migration evidence |
| Downstream | `SV-005` ⛔ | Hypercare inherits the migration defect backlog at each go-live |
| Lateral | `../../1000fix_ERP_Module/03_Modules/` §16.4 × 67 | The per-module migration statements this strategy serves |
| Lateral | `../../project_content/12_Data_Migration_Content/` | The 14 content files, unchanged by this document |

---

## 18. References

**Within this repository**
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md) ·
[`./_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`MG-002`](MG-002_Legacy_System_Profiling_and_Extract_Specification.md) ·
[`MG-003`](MG-003_ETL_Design_and_Transformation_Rules_Specification.md) ·
[`MG-004`](MG-004_Reconciliation_and_Validation_Plan.md) ·
[`MG-005`](MG-005_Mock_Migration_and_Dress_Rehearsal_Plan.md) ·
[`MG-006`](MG-006_Cutover_Plan_and_Runbook.md) ·
[`MG-007`](MG-007_Rollback_and_Fallback_Plan.md) ·
[`../03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md`](../03_Data_and_Information_Architecture/DA-001_Logical_and_Physical_Data_Model_and_Database_Schema_Specification.md) ·
[`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md`](../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md) ·
[`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md`](../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md)

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-001…DM-014` ·
`../../project_content/_AUDIT/AUDIT-011_Category_12_DM_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §6.1, §6.5, §11.6 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §8.2, §14 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §12

**External standards and sources**

| Source | Used for | Verified |
|---|---|---|
| DAMA-DMBOK 2.0 (2024 maintenance revision), Ch. 8 & 13 | Lifecycle and quality framing | 2026-08-18 |
| Johny Morris, *Practical Data Migration* (PDMv2), 2nd edn, BCS, 2012 | Landscape analysis, business-led migration principle | 2026-08-18 |
| ISO 8000-61:2016 — *Data quality management: process reference model* | Planning / control / assurance / improvement split | 2026-08-18 |
| ISO/IEC 25012:2008 — data quality model | Inherent quality characteristics | 2026-08-18 |
| Personal Data Protection Act 2026 (Bangladesh); Personal Data Protection (Amendment) Ordinance 2026 (No. 23 of 2026), 5 Feb 2026 | §9 lawful basis and residency; **secondary sources — see `DA-001` §10.4 `PGD-A5-03`** | 2026-08-18 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Data Migration Lead with Enterprise Architecture | Initial issue. Closes `AUDIT-011` `DM-01` for the strategy layer; allocates all seven unspecified items; records five decisions and eight open questions | CTO with CFO *(pending — `GV-001` `CC-01`)* |

---

*`MG-001` · Category 09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
