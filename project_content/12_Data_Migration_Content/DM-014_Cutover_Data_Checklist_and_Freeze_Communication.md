---
id: DM-014
title: Cutover Data Checklist and Freeze Communication
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Migration with Change
author: Data Migration with the Change Lead and Branch Operations
reviewers: [CTO, CFO, Service Ops Director, Branch Operations Lead, Warehouse Manager, HR Director, Change Lead, Localisation Lead, QA Lead]
approver: CTO with the Programme Director
content_class: C
purpose: >
  Defines the data freeze windows, the last-transaction rules each branch and function must follow,
  the cutover runsheet structure, the communication schedule that reaches 51-plus branches before
  the freeze begins, the parallel-run instructions and the fallback trigger with its decision
  rights. Fifty-one branches must stop and start together; a branch that keeps writing to a
  spreadsheet through the freeze produces data that exists nowhere in the new system and nobody
  discovers it until a customer asks.
traces_to: [CM-012, OP-002, M15, M19, M50, M56, M01, M04, 06-01, 06-02, DM-001, DM-002, DM-003, DM-007, DM-008, DM-011, DM-012, DM-013]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §6.5 legacy decommission commitment — a wave gate is not passed while its legacy process is still running beyond the agreed parallel-run period; nineteen legacy systems and practices with their withdrawal wave
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §12 MIG-03 and MIG-07 — every load is reversible and a dry run precedes every production load; a two-week parallel run applies to service orders and finance before legacy decommission
    verified: 2026-08-18
    class: P1
  - source: primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md §11.6.2 — MIG-005 trial migration into staging with business UAT before every cutover; MIG-007 documented rehearsed rollback plan for every cutover; MIG-009 incremental delta migration during the parallel-run period
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M15 §16.4 — 51+ locations counted, van stock recalled and counted, and consignment balances confirmed with each brand, inside the cutover window
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M19 §16.4 and M50 §16.4 — one full parallel month-end close reconciled line by line and signed before the legacy system is retired; cash counted and witnessed at every location at cutover
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01 §3 — per-wave geography, from Dhaka HQ and five pilot centres at W1 to all 51+ service centres at W5
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# DM-014 — Cutover Data Checklist and Freeze Communication

> **Identifier note (`CG-005` §3.3).** `DM-014` is a **content** identifier; `05-02` `DM-08`
> (modelling standard — UTC stored, `Asia/Dhaka` presented) is cited with its document prefix and
> governs every instant in this file.
>
> **Scope note.** This file owns the **freeze, the sequence, the trigger and the content
> requirements** of every cutover communication. It does **not** author the messages themselves —
> see §2 and open item `O-04`.

---

## 1. Purpose

A cutover is the only moment in the programme when the company has **no system of record**. The
legacy source has stopped accepting writes and the new system has not yet accepted its opening
position. Everything that happens in that window either goes into the paper contingency and is keyed
later, or it is lost.

The register's justification is exact: *"Fifty-one branches must stop and start together; the
communication is as important as the technical plan."*

**Consequence of absence (`CP-03`).**

| Failure | Consequence |
|---|---|
| A branch keeps writing to its spreadsheet through the freeze | Those orders exist nowhere in the new system; the customer discovers it |
| The freeze instant is stated as a date, not a time | Fifty-one interpretations of "Friday" |
| Van stock is counted at different times across zones | The consolidated opening position is a set of snapshots taken on different days |
| The last-transaction rule is not stated per function | Finance closes a period, Operations does not, and the two disagree about what is "in" |
| No fallback trigger is defined | The decision to abort is taken late, under pressure, by whoever is in the room |
| The parallel run is not instructed | Staff run both systems inconsistently, and the reconciliation between them proves nothing |
| Branch staff receive the instruction in English | The people executing the freeze at 51 sites are not uniformly English-comfortable |

---

## 2. Scope

**In scope:** the cutover phase model; freeze windows and their exact instants; last-transaction
rules by function; the runsheet structure and its derivation from `DM-003`; the communication
schedule and the **content requirements** of each message; the paper contingency; the parallel-run
instruction; the delta procedure; the fallback trigger and decision rights; the resume-to-normal
criteria; and rules `CV-01`…`CV-22`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **The wording of every branch- and customer-facing message, in Bengali and English** | `CM-012` branch readiness · `CM-013` customer transition · `NT-*` notification templates. **`CM-012` and `CM-013` were unwritten at enumeration 2026-08-18 (Category 16 held zero files); the `NT` templates exist** (`O-04`) |
| What each branch must confirm before cutover | `CM-012` Branch Readiness Communication Checklist |
| The order entities load in | [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) |
| What a completed count must contain | [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md), [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) |
| Whether the load is correct | [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) |
| Post-go-live operational procedures and hypercare | `OP-002` — **unwritten; Category 17 held zero files at enumeration 2026-08-18** |
| Technical rollback mechanics | **`06-03` — does not exist** (`DM-001` `O-01`) |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **Data Migration Lead** | Build and run the cutover runsheet |
| **Change Lead** | Derive the communication plan and brief `CM-012`'s authors |
| **Branch managers (51+)** | Know exactly when to stop, what to do meanwhile, and when to start |
| **CFO / Financial Controller** | Coordinate the period close with the freeze |
| **Warehouse Manager** | Sequence 51 counts and 200–400 van recalls inside the window |
| **CTO / Programme Director** | Hold the go / no-go and fallback decision |
| **Contact Centre** | Answer customers during a window when status cannot be looked up |

---

## 4. Content

### 4.1 The five cutover phases

**`CV-01`: every cutover has the same five phases, whatever its wave.** Phase names are used
identically in the runsheet, the communications and the reconciliation reports so that a person in
one document knows where they are in another.

| Phase | Name | Starts | Ends | Systems accepting writes |
|:--:|---|---|---|---|
| **P0** | **Rehearsal** | T−21 days | T−7 days | Legacy only — the dry run is on a copy |
| **P1** | **Freeze approach** | T−3 days | Freeze instant | Legacy only; **no new masters created** |
| **P2** | **Freeze** | Freeze instant | Go decision | **Neither.** Paper contingency only |
| **P3** | **Parallel run** | Go decision | +2 weeks *(finance: +1 close)* | **Both**, with declared primacy |
| **P4** | **Legacy withdrawal** | Parallel-run exit | Decommission | New only |

> **`CV-02` — P2 is the only phase with no system of record**, and its duration is the single number
> the whole plan optimises. Every hour of P2 is an hour of paper.

> **`CV-03` — P4 is a gate, not a date.** BRD §6.5: *"A wave gate is not passed while its legacy
> process is still running beyond the agreed parallel-run period."* A branch still using its
> spreadsheet in P4 fails the wave gate for everyone.

### 4.2 Freeze windows by wave

Freeze scope follows the wave's migration content (`DM-001` §4.2) and the geography in `06-01` §3.

| Wave | Freeze scope | Sites | Estimated P2 | The constraint |
|:--:|---|---|---|---|
| **W1** | Customer master, corporate accounts, device registry, branch and employee master, open orders at pilot sites | **Dhaka HQ + 5 pilot centres** | **One weekend** | Party and asset volume; `S3` deferral |
| **W2** | **Stock at every location, van stock, consignment balances**, workshop WIP, open field jobs, loyalty | **All Dhaka centres** | **Extended — the count sets it** | **51+ counts and 200–400 van recalls** |
| **W3** | Accounting close, open AR/AP, bank and cash positions, open POs, open consignments | **All Dhaka + Chittagong** | **Aligned to a period end** | Cash counted at every location, witnessed |
| **W4** | Contracts, entitlements, warranty registrations, claims, subscriptions, tax opening positions | All active centres | Moderate | **Mushak sequence assertion** |
| **W5** | Employees, salary structures, **YTD payroll**, leave, competencies, fixed assets | **All 51+ centres** | Aligned to a payroll period | **YTD exactness; ideally an assessment-year boundary** |
| **W6–W8** | Rental, refurbishment, data services, imports, e-waste backlog | Per module | Smaller | Physical condition baselines |

> **`CV-04` — W2 and W3 have physical constraints that cannot be compressed by adding people.**
> A stock count at 51 locations and a witnessed cash count at 51 locations are each bounded by the
> number of qualified counters and the number of hours a branch can be closed. `CV-11` sequences
> them; it cannot shorten them.

> **`CV-05` — the finance freeze is aligned to a period end, not to a convenient weekend.** An
> opening trial balance struck mid-period cannot be agreed with the external auditor and cannot be
> reconciled against a filed return.

### 4.3 The freeze instant

| Rule | Detail |
|---|---|
| **`CV-06`** | The freeze is an **exact `Asia/Dhaka` instant**, published in the format `YYYY-MM-DD HH:MM (Asia/Dhaka)`, never as a date or a day name |
| **`CV-07`** | The same instant is the **cut-off** for `MS-17` — a source record created after it is a **delta**, handled in P3, never a re-load |
| **`CV-08`** | Count sheets carry the instant printed, not written (`DM-012` `LT-05`); a count outside the window is void (`IV-14`) |
| **`CV-09`** | Every freeze instant is stated in **both** Bengali and English in branch communications, with the same numerals convention as `BN-007` |

### 4.4 Last-transaction rules by function

**`CV-10`: every function receives its own last-transaction rule, in its own words, and confirms it
has stopped.** A single "stop using the old system" instruction is interpreted differently by a
counter agent, a storekeeper and a cashier.

| Function | Last transaction permitted | Then | Confirms by |
|---|---|---|---|
| **Front desk / intake** | The last walk-in served before the instant; the job card is completed on paper | **Paper intake pad**, pre-numbered from the reserved block (`SH-10`) | Branch manager confirms the last legacy job number |
| **Workshop** | Devices already on the bench continue; **no new bench entries** in legacy | Whiteboard photographed and preserved as the WIP count evidence | Supervisor signs the WIP count sheet |
| **Field / dispatch** | Jobs already assigned are completed and recorded on paper | **Paper visit forms**; no new dispatch in legacy | Dispatcher confirms the open-job list |
| **Store / inventory** | **No movement after the instant.** Issues and receipts stop | Store physically closed for the count; emergency issues on a **numbered manual voucher** | Two counters and the branch manager sign |
| **Van stock** | Van recalled per the zone schedule; **no issues from the van after recall** | Van sealed until counted | Technician and branch manager sign |
| **Cash** | Last receipt before the instant; drawer closed | **Witnessed count**, drawer sealed | Cashier and branch manager sign |
| **Invoicing / billing** | Last invoice on the legacy sequence, number recorded | **No manual invoices in P2** except on the emergency pad | Financial Controller records the last number **per sequence** |
| **Tax** | Last Mushak 6.3 issued, **number recorded and agreed with the tax consultant** | Nothing issued in P2 | CFO records the position (`FO-12`) |
| **Payroll** | Period closed and paid before the freeze | Nothing processed in P2 | HR Director confirms |
| **Procurement** | No new POs; receipts against existing POs on paper | Paper GRN pad | Procurement Manager confirms the open-PO list |
| **Contact centre** | Continues answering; **cannot look up status** in P2 | Scripted holding response; call-back list maintained | Contact centre supervisor |

> **`CV-11` — emergency work does not stop; recording it changes.** A device that must be repaired
> during P2 is repaired. What changes is that it is recorded on a numbered paper form and keyed as
> a **P2 catch-up batch** immediately after go, before normal operation resumes. `CV-16` makes the
> catch-up batch a runsheet step rather than an assumption.

### 4.5 The cutover runsheet

**`CV-12`: the runsheet is generated from `DM-003` §4.4, not authored independently** (`SQ-18`).
A runsheet step with no tier in the sequencing plan is a breach of the plan, not an addition to it.

| Column | Purpose |
|---|---|
| `step_no` | Sequence within the phase |
| `phase` | `P0`…`P4` (`CV-01`) |
| `tier` | → `DM-003` `X0`…`X9` |
| `activity` | What is done |
| `owner_role` | Who does it |
| `planned_start`, `planned_duration` | From the rehearsal's **measured** times, not estimates |
| `predecessor` | Explicit; parallel steps share a predecessor |
| `checkpoint` | Whether the step ends in a go/no-go |
| `rollback_step` | The reverse action, and its **measured** duration (`SQ-08`) |
| `evidence` | What is filed afterwards — count sheet, reconciliation, signature |
| `actual_start`, `actual_end`, `status` | Filled live |

> **`CV-13` — a runsheet whose durations are estimates has not been rehearsed.** P0 exists to
> replace every estimate with a measurement. `MIG-005` requires a trial migration into staging with
> business UAT before every cutover; `MIG-007` requires a **rehearsed** rollback plan.

### 4.6 Checkpoints and the go / no-go

| # | Checkpoint | Occurs | Criteria | Decision |
|:--:|---|---|---|---|
| **C1** | Rehearsal complete | End P0 | Dry run reconciles; **rollback rehearsed with a measured duration**; UAT signed | Data Migration Lead recommends |
| **C2** | Readiness | T−3 days | `CM-012` branch confirmations received from **every** site; counts scheduled; staff briefed in Bengali | Change Lead + Branch Operations Lead |
| **C3** | Freeze confirmed | Freeze instant + 2h | Every function has confirmed stop (§4.4); last numbers recorded | Data Migration Lead |
| **C4** | Extract complete | Per wave | Deltas extracted; profiling accepted (`DQ-02`) | Data Migration Lead |
| **C5** | Load complete | Per tier | `DM-013` report produced per tier | Domain owner |
| **C6** | **Reconciliation signed** | Before go | Every applicable `DM-013` sign-off form signed (`RV-11`) | **Domain owners** |
| **C7** | **GO / NO-GO** | End P2 | C1–C6 all pass; fallback still executable inside the remaining window | **CTO with the Programme Director** |
| **C8** | Parallel-run exit | End P3 | Two-week parallel reconciled; **finance: one full parallel close signed** | CFO for finance; CTO otherwise |
| **C9** | Legacy withdrawal | P4 | Every legacy practice for that wave confirmed stopped (BRD §6.5) | Programme Director |

> **`CV-14` — C7 is held by two named people and is not delegable.** A go decision taken by whoever
> is present at 04:00 is how a known-bad load reaches production.

### 4.7 The fallback trigger

**`CV-15`: fallback is triggered by a rule, not by a mood.** Any one of the following, at any
checkpoint, triggers it:

| # | Trigger | Why it is absolute |
|:--:|---|---|
| **T1** | An `RV-02` R1 reconciliation cannot balance — records are unaccounted for | Nobody can say what is missing |
| **T2** | A **finance exact-tolerance** control does not tie (`FO-08`, `FO-13`) | The opening position is wrong and will stay wrong |
| **T3** | An **E9 semantic defect** is found (`RV-16`) | The data loaded and means something else |
| **T4** | The remaining window is shorter than the **measured** rollback duration | Fallback would no longer be executable |
| **T5** | A domain owner declines to sign (`RV-11`) | The accountable person does not accept the data |
| **T6** | The Mushak 6.3 sequence position cannot be asserted (`FO-12`) | Uncorrectable statutory exposure |
| **T7** | A physical count is incomplete at more than the declared number of sites | The opening position is partly unknown |

| Rule | Detail |
|---|---|
| **`CV-16`** | On fallback, **the P2 paper catch-up batch is keyed into the legacy system**, not discarded. The company must still know what happened during the window |
| **`CV-17`** | Fallback is followed by a **written post-mortem within five working days**, naming the trigger and the remediation, filed with the wave gate evidence |
| **`CV-18`** | A wave may be re-attempted only after the trigger's root cause is closed — never on the assumption that the next attempt will go better |

### 4.8 The parallel run

| Rule | Detail |
|---|---|
| **`CV-19`** | **Two weeks parallel on service orders and finance** before legacy decommission (`05-02` §12 `MIG-07`); finance additionally requires **one full parallel month-end close**, reconciled line by line and signed (`M19` §16.4) |
| **Primacy** | **The new system is the system of record from the go decision.** The legacy system is run in parallel for comparison only. Without declared primacy, staff use whichever is easier and the comparison proves nothing |
| **Delta** | Records created in the source during P2 and P3 load as deltas in tier order (`SQ-13`, BRD `MIG-009`) |
| **Comparison** | A daily comparison of the two systems on a declared set of measures, reported to the Change Lead |
| **Exit** | C8. **A parallel run that is simply allowed to lapse has not been exited**, and BRD §6.5 fails the wave gate |
| **Cost** | Running both systems is **double entry for the affected staff for two weeks**. It is a real operational cost and belongs in the plan, not in goodwill |

### 4.9 The 51-branch coordination problem

The largest cutovers in this programme — W2 stock and W3 cash — require simultaneous physical work
at more sites than the programme has migration staff.

| Constraint | Consequence for the plan |
|---|---|
| **51+ sites**, one migration team | Counting is done by **branch staff**, not by the migration team |
| Branch staff have never done a formal count | **Training and a rehearsal count are prerequisites**, not niceties |
| Counting requires the branch to be closed or quiet | Sequenced by zone, over a defined window (`CV-04`) |
| 200–400 vans must be recalled | Recall by zone; field service degrades during recall (`DM-007` `O-06`) |
| Communication reaches 51 sites through branch managers | **A single missed branch is a hole in the opening position** |
| Branch staff are not uniformly English-comfortable | **Every instruction must be Bengali-first** (`CV-09`, `O-04`) |

> **`CV-20` — a rehearsal count at a representative sample of branches is mandatory before W2.**
> The first time a storekeeper reads a count sheet must not be the night the opening balance is
> established.

### 4.10 Communication schedule

**This file owns the schedule and the content requirements. `CM-012`, `CM-013` and `NT-*` own the
wording. All three were unwritten at enumeration 2026-08-18 — Category 16 `CM` held zero files.**

| When | Audience | Must contain | Owning content |
|---|---|---|---|
| **T−21 days** | All branch managers | The wave, the phases, what will be asked of them, the count date | `CM-012` |
| **T−14 days** | Branch staff | **Bengali-first**: what changes, when to stop, what the paper contingency is | `CM-012`, `TR` job aid |
| **T−7 days** | All staff in scope | The **exact freeze instant**, the last-transaction rule for their function, who to call | `CM-012` |
| **T−7 days** | Customers with open jobs | That status enquiries may be delayed during the window; the hotline still answers | `CM-013`, `NT` |
| **T−3 days** | Branch managers | **Readiness confirmation request** — checkpoint C2 | `CM-012` |
| **T−1 day** | All staff in scope | Reminder with the instant, in Bengali and English | `CM-012` |
| **Freeze instant** | All staff in scope | **Stop now.** Confirm your last transaction number | `CM-012` |
| **During P2** | Contact centre | Holding-response script and the call-back procedure | `HC`, `NT` |
| **Go decision** | All staff in scope | **Start now.** First-day support routes and the P2 catch-up instruction | `CM-012`, `OP-002` |
| **Go + 1 day** | Customers | New reference format; legacy reference still searchable (`SH-12`) | `CM-013` |
| **Parallel run** | Affected functions | Which system is primary; what to compare; where to report a difference | `CM-012`, `OP-002` |
| **P4** | All staff | Legacy is closed. Confirm you are no longer using it | `CM-012` |

> **`CV-21` — a communication with no confirmation is not a communication.** Four of the twelve
> require a reply: readiness (C2), stop-confirmation (C3), start-acknowledgement and
> legacy-withdrawal confirmation (C9). The rest are broadcasts.

### 4.11 Governing rules

| # | Rule | Class |
|---|---|:--:|
| `CV-01` | Five phases, named identically across runsheet, communications and reports | **H** |
| `CV-02` | P2 duration is minimised and published; every hour of P2 is an hour of paper | **C** |
| `CV-03` | A wave gate is not passed while a legacy practice for that wave is still running | **H** |
| `CV-04` | Physical-count windows are set by counting capacity, not by convenience | **H** |
| `CV-05` | The finance freeze aligns to a period end | **H** |
| `CV-06` | The freeze is an exact `Asia/Dhaka` instant, never a date or a day name | **H** |
| `CV-07` | The freeze instant is the `MS-17` cut-off; later records are deltas | **H** |
| `CV-08` | Count sheets carry the instant printed; a count outside the window is void | **H** |
| `CV-09` | Every instant and instruction reaching branch staff is stated in Bengali and English | **H** |
| `CV-10` | Each function has its own last-transaction rule and confirms it has stopped | **H** |
| `CV-11` | Emergency work continues on numbered paper and is keyed as a P2 catch-up batch | **H** |
| `CV-12` | The runsheet is generated from `DM-003` §4.4 (`SQ-18`) | **H** |
| `CV-13` | Runsheet durations are measured in P0, never estimated | **H** |
| `CV-14` | C7 go/no-go is held by the CTO with the Programme Director and is not delegable | **H** |
| `CV-15` | Fallback is triggered by T1–T7, not by judgement | **H** |
| `CV-16` | On fallback, the paper catch-up batch is keyed into the legacy system | **H** |
| `CV-17` | A fallback is followed by a written post-mortem within five working days | **H** |
| `CV-18` | A wave is re-attempted only after the trigger's root cause is closed | **H** |
| `CV-19` | Two weeks parallel with declared primacy; finance additionally one full parallel close | **H** |
| `CV-20` | A rehearsal count at representative branches precedes W2 | **H** |
| `CV-21` | Four communications require confirmation; the rest are broadcasts | **H** |
| `CV-22` | Every checkpoint decision is recorded with its decider, instant and evidence | **H** |

> Class: **H** hard block · **A** approved override · **S** soft warning · **C** computed — the same
> scale as `05-05` §1.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md`](DM-003_Entity_Migration_Priority_and_Sequencing_Plan.md) | The runsheet is generated from §4.4 |
| [`DM-013_Reconciliation_and_Validation_Report_Specification.md`](DM-013_Reconciliation_and_Validation_Report_Specification.md) | C5, C6 and triggers T1, T2, T3, T5 all read its output |
| [`DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md`](DM-007_Field_Mapping_Workbook_Inventory_and_Parts.md) · [`DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md`](DM-008_Field_Mapping_Workbook_Finance_and_Open_Items.md) | What the counts must produce; the finance freeze alignment |
| [`DM-012_Migration_Load_Template_Pack.md`](DM-012_Migration_Load_Template_Pack.md) | Count sheets are cutover artefacts and carry the instant |
| [`DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md`](DM-002_Legacy_Source_System_Inventory_and_Extract_Catalogue.md) | Which sources freeze and which decommission (`SI-07`) |
| BRD §6.5 legacy decommission commitment | `CV-03` and the P4 gate |
| `06-01` §3 | Wave geography — which sites are in scope for each freeze |
| `CM-012` Branch Readiness Communication Checklist | **Unwritten** — the readiness confirmation C2 depends on |
| `CM-013` Customer Migration and Transition Pack | **Unwritten** — customer-facing messages |
| `OP-002` | **Unwritten** — first-day support and hypercare |
| **`06-03`** | **Does not exist** — technical rollback mechanics |

| Depended on by |
|---|
| Every wave gate in `06-02` · the `M15` and `M50` count programmes · `CM-012` and `CM-013` authoring · the contact-centre P2 script |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Before every cutover**, and immediately after — the post-cutover review updates the next one |
| Trigger for out-of-cycle review | A wave scope change · a new legacy source discovered · a rehearsal producing durations outside plan · a fallback |
| Owner | Data Migration Lead, with the Change Lead accountable for the communication schedule |
| Change log | `RF-006`; every checkpoint decision recorded per `CV-22` |
| Enforcement | `CV-01`…`CV-22`; the C1–C9 checkpoints; the T1–T7 triggers |
| Improvement loop | **Each wave's post-cutover review feeds the next wave's runsheet.** W1 has five sites and W5 has 51+; the plan must get better, not just repeat |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **`O-01`** | **No cutover has been rehearsed and no rollback duration has been measured.** `CV-13` requires measured durations and trigger T4 compares the remaining window against one. Every duration in the current plan is an estimate | Data Migration Lead with CTO | **W1 — P0 of the first cutover** |
| **`O-02`** | **The W2 count window has no schedule.** 51+ locations, 200–400 van recalls and 17+ brand confirmations, with counting done by branch staff who have not been trained (`CV-20`). This is `DM-007` `O-01` seen from the cutover side | Warehouse Manager with Branch Operations Lead | **W2 minus 3 months** |
| **`O-03`** | **The parallel run is unresourced.** Two weeks of double entry for service and finance staff, plus one full parallel month-end close, appear in no plan (`DM-008` `O-04`) | Programme Director with CFO | **W2 / W3 minus 2 months** |
| **`O-04`** | **Every message in §4.10 is Bengali-first for its audience, and Category 12 is English-only** (`CG-010` §3.2). `CM-012` and `CM-013`, which must carry these messages, were **unwritten at enumeration 2026-08-18** (Category 16 held zero files). `CV-09` is unenforceable until they exist and are translated | Change Lead with Localisation Lead and Programme Content Lead | **W1 — T−21 of the first cutover** |
| **`O-05`** | **`OP-002` is unwritten** *(enumerated 2026-08-18; Category 17 held zero files)*, so the go-decision message has no first-day support routes to point at and P4 has no hypercare model | Support Lead | **W1** |
| **`O-06`** | **The paper contingency has no forms.** `CV-11` requires numbered paper intake pads, manual issue vouchers, paper GRNs and paper visit forms drawn from the reserved sequence block (`SH-10`). `DT` templates exist for live documents, not for P2 contingency | Data Migration Lead with Content Design | **W1 minus 1 month** |
| **`O-07`** | **The contact-centre P2 script does not exist.** For the duration of P2 the hotline cannot look up a job status, and 250,000+ monthly customers are unaware there is a window | Customer Service Manager with Content Design | **W1 minus 1 month** |
| **`O-08`** | **W5 cutover timing versus the assessment-year boundary is undecided** (`DM-009` `O-01`), and it constrains the W5 freeze window rather than the other way round | HR Director with CFO and PMO | **W3** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §7 Open Items added per category convention
- [x] **Five cutover phases defined** and named identically across runsheet, communications and reports
- [x] P2 identified as the only phase with no system of record, and its duration made the optimisation target
- [x] Freeze windows given per wave, with the physical constraint named for each
- [x] **Freeze stated as an exact `Asia/Dhaka` instant**, bound to the `MS-17` cut-off rule
- [x] **Last-transaction rules given per function**, in that function's own terms, each with a confirmation
- [x] Emergency work handled explicitly through a numbered paper contingency and a P2 catch-up batch
- [x] Runsheet generated from `DM-003`, with measured rather than estimated durations
- [x] **Nine checkpoints** with named deciders; C7 made non-delegable
- [x] **Seven absolute fallback triggers**, each traced to a specific reconciliation or statutory rule
- [x] Fallback consequences specified — catch-up keying, post-mortem, root-cause closure before re-attempt
- [x] Parallel run given declared primacy, an exit checkpoint, and its cost stated
- [x] The 51-branch coordination problem stated with its consequences for who counts and who trains
- [x] Communication schedule specified with **content requirements and confirmation obligations**, while wording is left to its owning files (`CP-01`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a for this file, `bilingual: no` per `CG-010` §3.2; **the Bengali-first requirement for branch messages is `CV-09` and its gap is `O-04`**
- [ ] **`O-01` no cutover rehearsed; no rollback duration measured**
- [ ] **`O-02` W2 count window unscheduled**
- [ ] **`O-04` every branch message is Bengali-first and none of the owning files exists**
- [ ] **`O-06` paper contingency forms do not exist**
- [ ] Named approver recorded — **pending CTO with Programme Director**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
