---
id: RQ-005
title: Requirements Management Plan
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager
approver: ERP Design Authority
standards_basis: ISO/IEC/IEEE 29148:2018 §6.2–§6.6 (requirement processes and requirements management) · §5.2.8 (attributes) · BABOK v3 (elicitation and collaboration)
traces_to: PGD-000 RQ-005 row · _MODULE_TEMPLATE §0 (seven identifier spaces, three colliding) · audit C-03 (FR-BFO retired) · audit H-03 (two incompatible CD registers) · audit AF-11 (two priority scales)
depends_on: RQ-001 (requirement set) · GV-003 (decision log) · GV-006 (scope baseline control) · RR-002 (identifier convention)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-005 — Requirements Management Plan

### Category 01 · Code `RQ` · ISO/IEC/IEEE 29148:2018 §6.2–§6.6

---

> **Every identifier defect in this programme was preventable by a plan that did not exist.**
> `_MODULE_TEMPLATE` §0 already documents seven identifier spaces and warns that three of them
> collide. `FR-BFO-` was allocated to M04 and retired (`C-03`). Two incompatible `CD` registers
> exist (`H-03`), of which 31 identifiers collide outright. Twelve role identifiers and eighteen
> segregation-of-duties identifiers are in use and unregistered. One hundred and ninety-eight KPI
> identifiers were allocated locally against a rule that forbids it. Two priority scales are in
> simultaneous use (`AF-11`). Five `NFR` identifiers denote two things each.
>
> Not one of these is a difficult problem. Each is what happens when **allocation authority is
> assumed rather than assigned**. This document assigns it, and states the process that surrounds
> it: how a requirement comes into existence, how it is analysed, baselined, changed, versioned,
> deferred and retired, and who may do each of those things.

---

## 1. Purpose

Scope has already moved 11 → 30 → 67 modules with no change-control artefact in existence, so a
fourth expansion could not be distinguished from scope creep. Requirements are authored by
several functions into markdown files with no allocation authority, no state model and no change
record. This document makes the requirement set **manageable**: it defines the processes by which
requirements are elicited, analysed, agreed, baselined and changed; the authority that allocates
every identifier; the states a requirement moves through; and the measures by which the
requirements activity itself is monitored.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | Roles and responsibilities across the requirements activity (§3) |
| 2 | The four requirement processes of 29148 §6.2–§6.4, tailored to this programme (§4) |
| 3 | The **requirement state model** and the transitions permitted between states (§5) |
| 4 | **Change control** — request, impact assessment, authority, record (§6) |
| 5 | **Identifier allocation authority** — the register of every space, its owner and its rules (§7) |
| 6 | **Baseline, versioning, deferral and retirement** (§8) |
| 7 | **Tooling** — the interim method and the tool selection criteria (§9) |
| 8 | **Measurement of the requirements activity itself** (§10) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The requirements themselves | `RQ-001` | Content |
| The permanent identifier convention across all repositories | `RR-002` | §7 is an **interim** authority register for the requirements spaces only, and says so |
| Programme-wide scope baselining and change control | `GV-006` | Requirement change control (§6) sits **inside** programme change control, not beside it |
| The decision log | `GV-003` | Requirement decisions are recorded there; §6.5 states the interface |
| Configuration management of documents | `GV-011` | Document versioning; this document versions requirements |
| Estimation | `GV-007` | §10 supplies volatility inputs; it does not estimate |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Business analysts and module authors | The process they work in and the identifiers they may allocate |
| PMO | The change control they operate and the measures they publish |
| Steering Committee | The change authority they hold, and for what |
| Implementation vendor | How scope moves, and what a change costs them |
| Auditors | The control that should have prevented seven classes of finding |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance |
|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §6.2 Business or mission analysis | §4.1 |
| | §6.3 Stakeholder needs and requirements definition | §4.2 |
| | §6.4 System/software requirements definition | §4.3 |
| | §6.5 RE activities in architecture, verification and validation | §4.4 |
| | §6.6.1 Management overview · §6.6.2 Change management · §6.6.3 Measurement | §5, §6, §10 |
| | §5.2.8 Requirements attributes | §7 allocates the identity attribute; `RQ-001` §3.10.3 defines the rest |
| BABOK v3 | Elicitation and collaboration; requirements life cycle management | §4.2, §5 — cited as practice, not as a conformance claim |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | What it provides |
|---|---|
| `../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0 | The seven identifier spaces already documented, with their collision warnings — the starting point for §7 |
| `.../05-01` §6 | Requirement governance rules already in force: ownership, ID immutability, change control thresholds, acceptance criteria, traceability, coverage reporting, deferral discipline |
| `.../05-01` §1.3b | The `FR-BFO-` retirement precedent |
| `.../02-05` §5.2 | The `CD-001…138` allocation that modules subsequently overran |
| `RQ-001` §3.10.6 | The identifier spaces reserved and the `RQ-nn`/`RQ-nnn` collision |
| `RQ-004` §8 | The trace defect taxonomy that change control must not create |
| `FOLDER_STRUCTURE.md` §7 | Maintenance rules `PG-M1`–`PG-M11` this document operates within |

### 2.3 Audit findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `C-03` | `00-06` | `FR-BFO-` retired and never reissued. §7.4 makes retirement a recorded act with a tombstone, not a note in a revision block |
| `H-03` | `00-06` | Two incompatible `CD` registers. §7.2 assigns `CD` allocation to `BE-005` alone and forbids local allocation, with `CT-08` detecting breach |
| `AF-11` | `00-06` | Two priority scales. §7.5 declares `P0`–`P3` the single scale for the ERP estate and requires any document using another to say so |
| `RP-01` | `AUDIT-015` | 198 locally allocated KPI identifiers against a rule forbidding it. §7.2 pairs every "do not allocate locally" rule with a mechanical check |
| `PGD-A1-01` | `PGD-AUDIT-001` | Code allocated without checking existing spaces. §7.3 makes a **four-repository sweep** a precondition of any allocation |
| **`RQA-19`** *(raised here)* | This document | **Rules without checks do not hold.** Five of the seven spaces in `_MODULE_TEMPLATE` §0 carry an explicit prohibition that was breached anyway. §7.6 pairs each rule with its check | Open until `CT-06`–`CT-09` run in CI |

---

# 3. Roles and Responsibilities

| Role | Accountable for | May allocate | May approve |
|---|---|---|---|
| **Requirements Manager** *(owner of this plan)* | The requirement set's integrity, the state model, the change process, the measures | `SWR`, `SYR` | Requirement state transitions to `Approved` |
| **Business Analyst** (per category) | Elicitation, analysis, requirement authoring, story mapping | `FR-<CODE>-nnn` within their module's allocated range | — |
| **Business owner** (per module) | Requirement necessity, priority proposal, UAT acceptance | — | Necessity and acceptance |
| **ERP Solution Architect** | Feasibility, disposition, gap raising | `FG-nnn` | Feasibility |
| **Enterprise Architect** | Identifier convention, cross-module boundaries | — | Space creation |
| **PMO** | Change register, impact coordination, measure publication | — | P2/P3 changes |
| **ERP Design Authority** | Technical baseline, conflicting requirements | — | Baseline; P1 changes |
| **Steering Committee** | Scope, cost and benefit consequence | — | **P0/P1 changes; any change altering wave content, cost or a benefit** |
| **CISO / DPO** | Requirements with statutory consequence | — | Veto on any change weakening a statutory control |

**Rule `RM-01`.** A requirement has exactly **one** business owner. Where two functions claim it,
the boundary is wrong and is resolved as a scope-boundary question (`AR-005`), not by
co-ownership. Co-ownership is how `05-04` acquired three claimed owners for incident severity
(`OP-04`).

---

# 4. The Requirement Processes

## 4.1 Business or mission analysis *(§6.2)*

| Aspect | This programme |
|---|---|
| **Already performed** | BRD §2, §3, §6, §7 establish context, current state, future state and the 18 business objectives `BO-01`–`BO-18` |
| **Outstanding** | Four objectives — `BO-01`, `BO-09`, `BO-15`, `BO-16` — are claimed by no specification (`RQ-004` §6.2). Reciprocity is completed here, not re-analysed |
| **Owner** | Programme Director, with the benefit owners named in `06-02` §3.5 |
| **Output** | Every objective resolves to ≥ 1 requirement, and every requirement resolves to ≥ 1 objective — link `T-01` |

## 4.2 Stakeholder needs and requirements definition *(§6.3)*

| Aspect | This programme |
|---|---|
| **Already performed** | URD §3 personas, §5 goals, §6–17 — 245 user stories with acceptance criteria |
| **Elicitation techniques in use** | Document analysis, benchmark analysis (`04` of every module: SAP S/4HANA, Oracle Fusion, Dynamics 365, IFS Cloud), stakeholder workshops, process observation (`SP-002` baseline method) |
| **Outstanding** | Story-to-requirement mapping (`T-14`), Given/When/Then conversion, and Definition of Ready — all `RQ-008` |
| **Owner** | Business Analyst per category |

**Rule `RM-02` — elicitation for a change.** Any new or changed requirement after baseline states
which elicitation technique produced it and which stakeholder gave it. A requirement whose
provenance is "it came up" is refused.

## 4.3 System and software requirements definition *(§6.4)*

| Step | Activity | Output | Owner |
|---|---|---|---|
| 1 | Transform the need into a requirement in the `RQ-001` §3.10.2 construct | Draft requirement | BA |
| 2 | Allocate an identifier from the authorised space (§7) | `id` | BA, within range |
| 3 | Populate the 13 attributes (`RQ-001` §3.10.3) | Complete record | BA |
| 4 | Apply the nine individual characteristics (`W-01`–`W-09`) | Well-formed requirement | BA, peer-reviewed |
| 5 | Apply the five set characteristics (`S-01`–`S-05`) at module and programme level | Consistent set | Requirements Manager |
| 6 | Allocate the verification method | `verification_method` | BA with QA |
| 7 | Establish trace links (`RQ-004` §4.2, stage `Proposed`) | `T-01`, `T-02` | BA |
| 8 | Review and approve | State → `Approved` | Requirements Manager + business owner |

**Rule `RM-03` — no requirement enters a sprint without a testable acceptance criterion.**
Retained verbatim from `05-01` §6 and extended: it also requires a verification method, because a
criterion with no method is a criterion nobody has agreed how to check.

## 4.4 Requirements activities in other processes *(§6.5)*

| Process | Requirements activity | Artefact |
|---|---|---|
| **Architecture definition** (`AR-001`) | Requirements are allocated to architecture elements; conflicts and infeasibilities are returned to the requirement, not absorbed into the design | `T-04` |
| **Verification** (`QA-001`–`QA-011`) | Every requirement's method drives its test level; coverage is measured against the single denominator | `T-07`, `T-08` |
| **Validation** (`QA-009` UAT, `RQ-010`) | The business owner confirms the requirement met the need, not merely the specification | `T-08` acceptance |

**Rule `RM-04`.** Where architecture or test work finds a requirement infeasible, ambiguous or
contradictory, a **change request is raised against the requirement**. It is never resolved
silently in the design or the test. Silent resolution is how a design and a specification come to
describe different systems.

---

# 5. Requirement State Model

## 5.1 States

| State | Meaning | Entry condition | Who sets |
|---|---|---|---|
| `Proposed` | Authored, not agreed | Construct + `T-02` source | BA |
| `Approved` | Agreed and in the baseline | All 13 attributes; `W-01`–`W-09` pass; `T-01`, `T-05`, `T-11`, `T-15` resolve; business owner accepts | Requirements Manager |
| `Allocated` | Dispositioned and scheduled | `T-03` disposition with evidence; `T-04` design; `wave` fixed | Solution Architect |
| `Built` | Implemented | Component delivered; `T-06`, `T-10`, `T-12` resolve | Development Lead |
| `Verified` | Proved by its declared method | `T-07` case exists; `T-08` result passes | QA Lead |
| `Accepted` | Business owner has accepted it | UAT sign-off per `RQ-010` | Business owner |
| `Deferred` | Agreed, moved to a later wave | Approved change with a reason and a new target wave | PMO or Steering, by priority |
| `Superseded` | Replaced by another requirement | The replacing `id` recorded | Requirements Manager |
| `Retired` | Withdrawn; identifier permanently dead | Tombstone recorded (§8.4) | Requirements Manager |

## 5.2 Permitted transitions

```
  Proposed ──▶ Approved ──▶ Allocated ──▶ Built ──▶ Verified ──▶ Accepted
      │            │            │           │          │
      │            ├──────────▶ Deferred ◀──┘          │
      │            │                                   │
      ├──▶ Retired ◀── Superseded ◀────────────────────┘
      │            ▲
      └────────────┘

  Backward transitions permitted, each requiring a change record:
     Verified → Built      (defect found after verification)
     Built    → Allocated  (design change)
     Allocated→ Approved   (disposition invalidated, e.g. by RQ-003 §8.3 re-verification)
     Approved → Proposed   (baseline withdrawn — Steering Committee only)
```

**Rule `RM-05`.** A backward transition is a **change**, and carries the same record as any other
change (§6). Requirements that quietly slip backwards are how a wave reports 90% complete twice.

**Rule `RM-06`.** `Deferred` is never a resting state without a target wave. A deferral with no new
target is a silent drop, forbidden by `05-01` §6 and detected by check `CT-13` (§10.3).

---

# 6. Change Control

## 6.1 What constitutes a change

| Change | Requires a CR |
|---|:--:|
| New requirement after baseline | ✔ |
| Change to a requirement statement altering its meaning | ✔ |
| Change of priority | ✔ |
| Change of wave (deferral or acceleration) | ✔ |
| Change of verification method | ✔ |
| Withdrawal or supersession | ✔ |
| Change of disposition after `Allocated` | ✔ |
| Editorial correction not altering meaning (typography, formatting) | ✗ — recorded in the revision history |
| Populating an attribute that was always mandatory but absent | ✗ — this is conversion (`RQ-001` §3.10.7), not change |

**Rule `RM-07`.** The conversion of the 3,347 adopted rows under `RQ-001` §3.10.7 is **not** a
change. It makes existing requirements conform; it does not alter what the system shall do. Any
conversion that *does* alter meaning stops and becomes a CR. This distinction must be stated
explicitly or the conversion will be used as cover for scope movement.

## 6.2 Change authority

| Change affects | Authority | Rationale |
|---|---|---|
| A `P0` or `P1` requirement | **Steering Committee** | Retained from `05-01` §6 |
| A `P2` or `P3` requirement | **PMO** | Retained from `05-01` §6 |
| Wave content, cost or a claimed benefit | **Steering Committee**, with the benefit owner | `BM-004` |
| A statutory control | **Steering Committee**, with a **DPO/CISO veto** | PDPA 2026 exposure to BDT 50 lakh |
| A requirement already `Accepted` | **Steering Committee** | Re-opening acceptance is a contractual act (`CO-003`) |

> **Governance circularity, stated.** The Steering Committee's terms of reference do not exist
> (`GV-002`), so no change can currently be approved by the authority this table names. That is
> finding `PGD-A1-09` applied to requirements. Until `GV-002` issues, changes are **recorded and
> queued**, not approved — and the queue length is a published measure (`RM-M6`, §10.2).

## 6.3 The change record

| Field | Rule |
|---|---|
| `cr_id` | `CR-nnn`, allocated by PMO |
| `raised_by`, `raised_on` | Role and date |
| `requirements_affected` | Every `id`; a CR affecting "M15 generally" is refused |
| `change_type` | New / amend / priority / wave / method / withdraw / supersede / disposition |
| `driver` | The elicitation source, audit finding, statute, defect or decision behind it |
| `impact_design` | `T-04` artefacts requiring change |
| `impact_test` | `T-07` cases requiring change |
| `impact_effort` | Person-weeks, from `GV-007`'s model |
| `impact_cost` | From `CO-005`'s model |
| `impact_benefit` | Any `BO-nn` or `KPI-nnn` affected |
| `impact_wave` | Whether the wave gate date moves |
| `statutory_assessment` | DPO/CISO position where a statutory control is touched |
| `decision`, `decided_by`, `decided_on` | Recorded in `GV-003` |
| `implemented_on` | When the requirement record was updated |

**Rule `RM-08` — impact before decision.** A CR is not tabled until all seven `impact_*` fields are
populated. A change approved without its impact assessed is how 11 modules became 67 with no
budget movement.

## 6.4 Impact analysis method

Impact is computed from the RTM, not estimated:

```
  Given a changed requirement R:
     forward   = T-03 disposition ∪ T-04 designs ∪ T-06 events ∪ T-07 tests ∪ T-10 entities
     backward  = T-01 objectives ∪ T-09 KPIs ∪ T-14 stories ∪ T-17 deliverables
     lateral   = T-15 dependents (transitive) ∪ T-05 NFRs ∪ T-11 rules
     impact(R) = forward ∪ backward ∪ lateral
```

**Rule `RM-09`.** Where the RTM cannot compute `impact(R)` because a link is absent, the CR is
**blocked** and the missing link is raised as an `RQ-004` §8 defect. A change assessed against an
incomplete trace is an unassessed change.

## 6.5 Interface with the decision log

Every CR decision is recorded in `GV-003`. `GV-003` does not yet exist, and audits already cite a
decision `D-14` that has no record (`AF-04`). Until `GV-003` issues, requirement change decisions
are recorded in an interim register held by the PMO and **migrated wholesale** on `GV-003`'s
issue — not re-keyed, and not left behind.

---

# 7. Identifier Allocation Authority

## 7.1 Why this section is the heart of the plan

Seven of the findings in §2.3 are identifier failures, and the register's own audit committed two
more while naming identifier collisions as the estate's largest defect class. Allocation is the
one act that cannot be corrected later, because `PG-05` makes identifiers permanent.

## 7.2 The authority register *(interim, pending `RR-002`)*

| Space | Format | Scope | **Allocating authority** | May a module author allocate? | Check |
|---|---|---|---|:--:|---|
| `FR-<CODE>-nnn` | 3-digit, optional letter suffix | Module-local | `05-01` §1.3, within the module's issued range | **✔ within range only** | `CT-14` |
| `FR-POR-nnn` | 3-digit, one flat sequence | Portal estate | `05-01` §4 | ✗ | `CT-14` |
| `SWR-nnn` | 3-digit | Programme-wide software | **`RQ-001`** | ✗ | `CT-08` |
| `SYR-nnn` | 3-digit | Programme-wide system | **`RQ-002`** | ✗ | `CT-08` |
| `NFR-nnn` | 3-digit, optional letter | Programme-wide | **`RQ-006`** (re-basing `05-06`) | ✗ — *cite, do not invent* | `CT-09` |
| `BRU-<CODE>-nn` | 2-digit | Module-local | Module file; catalogued by `RQ-009` | ✔ | `CT-08` |
| `AUT-<CODE>-nn` | 2-digit | Module-local | Module file | ✔ | `CT-08` |
| `FG-nnn` | 3-digit | Programme-wide gaps | **`RQ-003`** | ✗ | `CT-08` |
| `CD-nnn` | 3-digit | Programme-wide build items | **`BE-005` only** | ✗ — **31 collide today** | `CT-08` |
| `KPI-nnn` | 3-digit | Programme-wide | **`06-02` register only** | ✗ — **198 allocated locally** | `CT-06` |
| `R nn` | 2-digit | Programme-wide roles | **`05-04` / `SC-004`** | ✗ — **12 unregistered** | `CT-07` |
| `SOD-nn` | 2-digit | Programme-wide | **`05-04`** | ✗ — **18 unregistered** | `CT-07` |
| `UC-nnn` | 3-digit | Programme-wide use cases | **BRD §13** | ✗ | `CT-08` |
| `US-<CODE>-nnn` | 3-digit | Programme-wide stories | **URD** / `RQ-008` | ✗ | `CT-08` |
| `BPM-nnn` | 3-digit | Process models | **`RQ-007`** | ✗ | `CT-08` |
| `CR-nnn` | 3-digit | Change requests | **PMO** | ✗ | — |
| `TC-nnn` | 3-digit | Test cases | **`QA-003`** | ✗ | `CT-08` |

## 7.3 Allocation procedure

**Rule `RM-10` — the four-repository sweep.** Before any new identifier **space** is created, the
proposer sweeps `primary-doc/`, `old-primary-doc/`, `1000fix_ERP_Module/`, `project_content/` and
`project-guide-doc/` for the prefix and records the result with a timestamp. This is the control
whose absence produced `PGD-A1-01`, and whose absence produced it **a second time** — `RQ-001`
§3.10.6 records that the category code `RQ` collides with `RQ-01`…`RQ-14` in `LG-010`, undetected
by the audit that closed the first instance.

```bash
# The sweep. Run before creating any space; record the output and the timestamp.
grep -rhoE '\b<PREFIX>-[0-9]+' primary-doc old-primary-doc \
     1000fix_ERP_Module project_content project-guide-doc | sort -u | wc -l
# Must return 0.
```

**Rule `RM-11` — width is part of the identifier.** `RQ-001` and `RQ-01` are different spaces only
because their widths differ, and that is a fragile distinction. New spaces use **three digits**
without exception, so width can never be the only thing separating two meanings.

**Rule `RM-12` — allocation within a range.** A module author may allocate `FR-<CODE>-nnn` only
inside the range `05-01` §1.3 has issued to that module, and only sequentially. Overrunning the
range is a CR, not an act of authorship. The portal estate overran `FR-POR-140` to `FR-POR-358`
without one (`RQA-06`).

## 7.4 Retirement and supersession

**Rule `RM-13`.** A withdrawn identifier is **retired with a tombstone**, never reissued and never
silently deleted. The tombstone records the identifier, what it denoted, the date, the reason and
the superseding identifier if any.

| Retired | Denoted | Retired on | Reason | Superseded by |
|---|---|---|---|---|
| `FR-BFO-nnn` | M04 Branch & Front Desk, during drafting | 2026-08-12 | Permanent code `FRD` allocated | `FR-FRD-nnn` |
| `FR-SLS-nnn` | M11 in `05-01` §1.3 | **Pending** — `RQA-09` | Module uses `PRC` | `FR-PRC-nnn` |
| `FR-SCM-nnn` | M16 in `05-01` §1.3 | **Pending** — `RQA-09` | Module uses `PRO` | `FR-PRO-nnn` |
| `FR-BIL-nnn` | M20 in `05-01` §1.3 | **Pending** — `RQA-09` | Module uses `ARB` | `FR-ARB-nnn` |
| `FR-HRM-nnn` | M21 in `05-01` §1.3 | **Pending** — `RQA-09` | Module uses `HCM` | `FR-HCM-nnn` |
| `OPS-nnn` | Category 10 in `PGD-000`, pre-issue | 2026-08-18 | Near-collision with `OP` (`PGD-A1-06`) | `PE-nnn` |

> Four retirements are **pending**, not complete: `BRU-BIL-`, `BRU-HRM-`, `BRU-SCM-` and the
> `FR-` forms are still cited by the BRD §10, the URD and `05-05`. Retiring an identifier whose
> citations remain live creates a `D-2` dangling reference (`RQ-004` §8). Each retirement
> therefore carries a citation-update task, and is not closed until `CT-08` returns clean.

## 7.5 The priority scale

**Rule `RM-14`.** The ERP estate uses exactly one priority scale: **`P0` / `P1` / `P2` / `P3`**, as
defined in `RQ-001` §3.10.11. The website content estate's `P1`–`P4` scale means something
different (`AF-11`); any document using it states so in its front matter. A document using an
unlabelled four-value scale is ambiguous by construction.

## 7.6 Finding `RQA-19` — rules without checks do not hold

| Rule already in force | Where | Breached | Measured breach |
|---|---|:--:|---|
| *"`KPI-nnn` — do not allocate locally"* | `_MODULE_TEMPLATE` §0 | **✔** | 198 local allocations |
| *"`CD-nnn` — do not allocate locally"* | `_MODULE_TEMPLATE` §0 | **✔** | 31 colliding, highest `CD-214` against a register of 138 |
| *"`R nn` — never reuse an ID for a different role"* | `_MODULE_TEMPLATE` §0 | **✔** | `R39`–`R50` used, unregistered |
| *"`SOD-nn` — allocated by `05-04`"* | `_MODULE_TEMPLATE` §0 | **✔** | `SOD-13`–`SOD-30` used, unregistered |
| *"`NFR-nnn` — cite, do not invent"* | `_MODULE_TEMPLATE` §0 | **✔** | 5 identifiers denote two requirements each |
| *"Requirement count is counted, not consulted"* (`RG-06`) | `_MODULE_TEMPLATE` §0 | **✔** | Four denominators in circulation |
| *"Every referenced entity appears verbatim in its owner's §10.1"* | `_MODULE_TEMPLATE` §10.2 | **✔** | 255 references, and 1,360 vs 434 catalogued |

**Seven prohibitions, seven breaches.** The prohibitions are correct and were read — several are
quoted back in the module files that breach them. The conclusion is not that authors were
careless; it is that **a rule enforced by attention is not enforced**. Every rule in §7 is
therefore paired with a check in `RQ-004` §7.3 that runs mechanically, and rule `RM-15` follows.

**Rule `RM-15`.** A new prohibition may not be published in this category without naming the
automated check that detects its breach. A prohibition with no check is a recorded intention.

---

# 8. Baseline, Versioning, Deferral and Retirement

## 8.1 Baseline

| # | Rule |
|---|---|
| `BS-01` | The requirement set is baselined as a whole, at the version and timestamp in `RQ-001` Appendix A |
| `BS-02` | Baseline requires the five set characteristics (`RQ-001` §3.10.9) to pass, or each failure to be recorded with an owner and a target |
| `BS-03` | The baseline is re-counted and re-stamped at every wave gate (`CR-03`, `TR-05`) |
| `BS-04` | Between baselines, the requirement set is the previous baseline **plus** the approved CR log. It is never the current state of the files |

## 8.2 Versioning

| Object | Versioned how |
|---|---|
| The requirement set | Baseline version `n.m`, incremented at each wave gate or on Steering approval of a material CR |
| An individual requirement | Not separately versioned. Its `status` and its CR history are the record. Per-requirement versioning creates a version graph nobody reads |
| A module specification file | `GV-011` document configuration management |

## 8.3 Deferral

**Rule `RM-16`.** A deferral records the requirement, the reason, the approving authority, the
original wave and the new wave. A deferral without a new wave is a withdrawal and takes the
withdrawal path. `05-01` §6 already says this; check `CT-13` makes it hold.

## 8.4 Retirement

**Rule `RM-17`.** Retirement requires: the tombstone (§7.4), the citation-update task, and
`CT-08` returning clean for that prefix. Only then is the retirement closed.

---

# 9. Tooling

## 9.1 The present position, measured

Every one of the 601 workspace files is markdown; a search for `*.yaml`, `*.yml`, `*.json`,
`*.sql`, `*.tf` and `*.py` across the estate returns **zero files** (`PGD-AUDIT-001` §7.3). There
is no requirements-management tool, no database, and no mechanism that can enforce a link.

## 9.2 Interim method — until a tool exists

| # | Rule |
|---|---|
| `TL-01` | Requirements remain in the module and portal files. **Do not migrate to a spreadsheet.** A spreadsheet is a tool with no link enforcement and no version control, and it will be emailed |
| `TL-02` | The 13 attributes are carried in an extended requirement table with one column per attribute, or a YAML block per requirement, per `RQ-001` Appendix C |
| `TL-03` | The RTM is **generated** by script from the files and registers (`TR-04`), never typed |
| `TL-04` | Checks `CK-01`–`CK-12` and `CT-01`–`CT-14` run as scripts on every change and, from Wave 1, in CI |
| `TL-05` | The generated RTM and check output carry an enumeration timestamp (`PG-M11`) |

## 9.3 Tool selection criteria

| # | Criterion | Why | Weight |
|---|---|---|:--:|
| `TS-01` | **Bidirectional link enforcement** — a link cannot be written at one end only | Without it, `TR-02` is unenforceable and the `D-1` defect class returns | **Must** |
| `TS-02` | Custom attributes, including the four programme-specific ones | 13 attributes, not the tool's default 6 | **Must** |
| `TS-03` | Baseline and change history at set level | `BS-01`–`BS-04` | **Must** |
| `TS-04` | Scriptable export for the generated RTM and the check suite | `TL-03`, `TL-04` | **Must** |
| `TS-05` | Bengali (UTF-8) content without corruption in fields, exports and reports | Requirements cite Bengali strings and Bengali acceptance criteria | **Must** |
| `TS-06` | Test-case linkage, either native or by integration | `T-07`, `T-08` | Should |
| `TS-07` | Role-based access aligned to §3 | Allocation authority must be enforced, not documented | Should |
| `TS-08` | Data residency compatible with `SWR-015` where requirements reference personal data structures | PDPA 2026 | Must, if hosted |
| `TS-09` | Licence and cost consistent with `02-05` §6 — an L6 component requires CFO approval | `CN-04` | Must |
| `TS-10` | Import of 3,389 requirements with attributes and links | Migration cost | Should |

**Rule `RM-18`.** Tool selection is a `buy` disposition and follows `RQ-003` §4.3 evidence `E-06`:
CFO approval plus a recorded assessment of why no open-source equivalent is viable.

---

# 10. Measurement of the Requirements Activity *(§6.6.3)*

## 10.1 Why measure the activity, not only the requirements

`RQ-004` §5 measures the requirement *set*. This section measures the *process* — because
volatility, ageing and change throughput are the leading indicators of the scope movement that
turned 11 modules into 67 with no artefact recording it.

## 10.2 The measures

| # | Measure | Formula | Reported to | Cadence | Signal |
|---|---|---|---|---|---|
| `RM-M1` | **Requirement volatility** | CRs affecting requirements ÷ baseline count, per period | Steering | Monthly | > 5%/month means the baseline is not stable enough to build against |
| `RM-M2` | **Change lead time** | Median days, CR raised → decided | PMO | Monthly | A slow queue produces out-of-process change |
| `RM-M3` | **Requirement ageing** | Days in `Proposed` without approval | Requirements Manager | Fortnightly | Ageing requirements are unowned requirements |
| `RM-M4` | **Attribute completeness** | Requirements with all 13 attributes ÷ baseline | PMO | Fortnightly | The conversion (`RQ-001` §3.10.7) burn-down |
| `RM-M5` | **Identifier integrity** | Open `D-2`/`D-3` defects (`RQ-004` §8) | Design Authority | Fortnightly | Should trend to zero and stay there |
| `RM-M6` | **Undecided CR queue** | CRs raised and not decided | Steering | Monthly | Currently unbounded — no constituted approver exists (`PGD-A1-09`) |
| `RM-M7` | **Deferral rate** | Requirements moved to a later wave ÷ wave baseline | Steering | Wave gate | Sustained deferral is descope by attrition |
| `RM-M8` | **Silent-drop count** | `Deferred` requirements with no target wave | PMO | Fortnightly | **Target: zero.** Any non-zero value is a control failure |
| `RM-M9` | **Rework rate** | Requirements returning from `Built`/`Verified` to an earlier state | Design Authority | Wave gate | High rework indicates weak `W-01`–`W-09` review |

## 10.3 Process checks

| # | Check | Detects |
|---|---|---|
| `CT-13` | Every `Deferred` requirement has a target wave | Silent drops (`RM-M8`) |
| `CT-14` | Every `FR-<CODE>-nnn` lies inside its module's issued range | Range overrun (`RQA-06`) |
| `CT-15` | Every state transition has a permitted predecessor (§5.2) | State-model violations |
| `CT-16` | Every backward transition has a CR | Undocumented rework |
| `CT-17` | Every CR has all seven `impact_*` fields before decision | `RM-08` breach |
| `CT-18` | Every retired prefix returns zero live citations | `RM-17`, dangling references |

---

# 11. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Where requirements live in the interim | (a) Migrate to a spreadsheet; (b) stay in the module files | **(b)** | A spreadsheet has no link enforcement and no version control, and it circulates by email |
| D-02 | Per-requirement versioning | (a) Version each requirement; (b) version the set, track status and CR history | **(b)** | A per-requirement version graph is written and never read |
| D-03 | Whether conversion is a change | (a) Yes, CR each; (b) No — conversion makes existing requirements conform | **(b)**, with `RM-07` guarding the boundary | 3,347 CRs would stop the programme; but the boundary must be explicit or conversion becomes cover for scope movement |
| D-04 | Identifier width for new spaces | (a) Match existing widths; (b) three digits, always | **(b)** | `RQ-001`/`RQ-01` shows that width is a fragile way to separate meanings |
| D-05 | Whether to publish a prohibition without a check | (a) Yes; (b) No — `RM-15` | **(b)** | Seven existing prohibitions, seven breaches. The evidence is unambiguous |
| D-06 | Change authority while `GV-002` does not exist | (a) Delegate to PMO temporarily; (b) record and queue, publish the queue | **(b)** | Delegating an authority that has not been constituted creates decisions nobody can defend later |
| D-07 | Retirement of the four stale `05-01` prefixes | (a) Retire now; (b) retire with a citation-update task, closed on `CT-08` clean | **(b)** | Retiring an identifier whose citations remain live creates dangling references |

---

# 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | When is the Steering Committee constituted, so that CRs can be decided rather than queued? | CTO | **Now** | All change control; `RM-M6` |
| Q-02 | Which tool, and is it funded? | Requirements Manager / CFO | W1 | `TS-01`–`TS-10`; enforcement at scale |
| Q-03 | Who owns and runs the check suite until CI exists? | PMO | **Now** | `RM-15`; every check in §10.3 |
| Q-04 | Do the four pending prefix retirements require BRD and URD reissue, or an erratum? | Enterprise Architecture | W1 | `RM-17`, `CT-18` |
| Q-05 | Is `RR-002` going to ratify §7 as written, or re-base the spaces? | Enterprise Architecture | W2 | §7's interim status |
| Q-06 | Who are the per-module business owners named in `RM-01`? | Programme Director | W1 | Requirement approval and acceptance |

---

# 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Roles, allocation rights and approval rights defined with no shared ownership | §3, `RM-01` |
| AC-02 | The four 29148 processes tailored and assigned | §4 |
| AC-03 | A nine-state model with permitted transitions, including backward transitions as changes | §5 |
| AC-04 | Change control defines what a change is, who approves it and what impact must be assessed first | §6 |
| AC-05 | An allocation authority named for every identifier space in use | §7.2 |
| AC-06 | The four-repository sweep mandated before any space is created | `RM-10` |
| AC-07 | Retirement requires a tombstone and a clean citation check | `RM-13`, `RM-17` |
| AC-08 | Every prohibition is paired with a mechanical check | `RM-15`, §10.3 |
| AC-09 | Nine process measures with formulas, audiences and signal interpretation | §10.2 |
| AC-10 | The governance circularity is stated rather than worked around | §6.2 |

---

# 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `GV-002` | Constitutes the change authority §6.2 names |
| Upstream | `GV-003` | Records every requirement decision |
| Upstream | `GV-006` | Programme scope control, inside which §6 sits |
| Upstream | `RR-002` | Will ratify or re-base §7 |
| Lateral | `RQ-001` | The requirement set this plan manages |
| Lateral | `RQ-004` | The RTM that computes `impact(R)` and runs `CT-01`–`CT-12` |
| Downstream | `RQ-003` | Disposition re-verification triggers a state transition |
| Downstream | `RQ-008` | Story management operates inside this plan |
| Downstream | `BE-005` | Sole `CD` allocation authority per §7.2 |
| Downstream | `BE-008` | Sprint and backlog model consuming the state model |
| Downstream | `GV-007` | Volatility and change-throughput inputs |
| Downstream | `QA-010` | Defect management interfacing with backward transitions |

---

# 15. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-002`](RQ-002_System_Requirements_Specification.md) ·
[`RQ-003`](RQ-003_Fit_Gap_Analysis_and_Functional_Design_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`../FOLDER_STRUCTURE.md`](../FOLDER_STRUCTURE.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §0, §10.2, §16.2 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01` §1.3, §1.3b, §6 ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §5.2 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06`, `00-07`

**External**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018 §6.2–§6.6 | 2026-08-18 |
| BABOK v3 (IIBA) — elicitation, requirements life cycle management | 2026-08-18 |

---

# 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Allocation authority assigned for 17 identifier spaces; four-repository sweep mandated; nine-state model; change control with mandatory impact; finding `RQA-19` — seven prohibitions, seven breaches — and rule `RM-15` in response | *Pending — `GV-002`* |

---

*`RQ-005` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
