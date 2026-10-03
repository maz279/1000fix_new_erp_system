---
id: RQ-004
title: Requirements Traceability Matrix
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager
approver: ERP Design Authority
standards_basis: ISO/IEC/IEEE 29148:2018 §5.2.8 (requirements attributes) · §6.5 (RE activities in other technical processes) · §6.6.3 (measurement for requirements) · ISO/IEC/IEEE 29119-3:2021 (test traceability)
traces_to: PGD-000 §2.1 item 3 · audit C-02 (M31 outside the traceability matrix) · audit TS-01 (three coverage denominators) · audit RP-01 (250 KPI identifiers against 95 registered) · audit F3 (DT-031 maps nine non-existent fields)
depends_on: RQ-001 (requirement set, denominator, attributes) · RR-002 (identifier convention) · RQ-003 (disposition attribute)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-004 — Requirements Traceability Matrix

### Category 01 · Code `RQ` · ISO/IEC/IEEE 29148:2018 §5.2.8, §6.5, §6.6.3

---

> **Every audit finding this programme has produced is a traceability failure.** Nine `MD-028`
> fields that do not exist (`F3`). Twenty-one events consumed and never published (`AP-01`). Two
> hundred and fifty-five entity references naming entities their declared owner does not define.
> Fifty-eight `M31` requirements outside the traceability matrix (`C-02`). Two hundred and fifty
> KPI identifiers against ninety-five registered (`RP-01`). Twelve role identifiers used and
> unregistered.
>
> None of these is a thinking error. Each is a **link that was asserted in one document and never
> checked against the other end**. An index would have surfaced every one of them automatically,
> on the day it was written.
>
> This document specifies that index: what links exist, which direction each runs, which must
> reciprocate, how coverage is measured from them, and what a broken link means.

---

## 1. Purpose

The programme cannot currently answer four questions that any wave gate will ask. *Which business
objective does this requirement serve?* *Which design realises it?* *Which test proves it?*
*What proportion of the requirement set is covered?* The last of these has three published
answers with three different denominators, which is why audit `TS-01` ruled that **no coverage
percentage may be quoted at all**.

This document creates the thread that makes those questions answerable: a bidirectional trace
from business objective through requirement, disposition, design, component, test case and
acceptance evidence, with the reciprocity rules that stop one end of a link being written without
the other.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **trace model** — the entities linked, the link types, and the direction each runs (§3) |
| 2 | The **reciprocity rules** — which links must be declared at both ends, and what happens when they are not (§3.4) |
| 3 | The **RTM schema** — the record structure and the storage it lives in (§4) |
| 4 | The **coverage measurement rules** — one denominator, stated formulas, publication constraints (§5) |
| 5 | The **measured trace integrity position** at issue: what is traceable today and what is not (§6) |
| 6 | **Production and maintenance** — who populates it, when, and the automated checks that hold it (§7) |
| 7 | The **defect taxonomy** for broken links and their disposition (§8) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| The requirement statements and attributes | `RQ-001` | This document links them; it does not define them |
| The fit-gap disposition | `RQ-003` | A disposition is a traced attribute, determined there |
| Test case design and the test repository | `QA-003` | The RTM links to test cases; it does not derive them |
| Test coverage *targets* and the gate thresholds | `QA-011`, `QA-010` | This document measures; those documents set the bar |
| The generated cross-reference index across all seven identifier spaces | `RR-006` | `RR-006` indexes the whole estate; this document traces the requirement thread |
| The KPI register itself | `06-02`, `BM-002` | The RTM records the link; the register owns the identifiers |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| PMO | The fortnightly requirement status report (`05-01` §6) and the wave-gate coverage evidence |
| QA | Which requirements have tests, at which level, with what result |
| Business owners | Which requirements serve their objective, and what evidence exists that it was delivered |
| Architects | Impact analysis: what breaks if this requirement changes |
| Auditors | The evidence chain from objective to acceptance |
| Implementation vendor | Which deliverables discharge which contractual requirements (`CO-003`) |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure |
|---|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §5.2.8 *Requirements attributes* | The trace links in §3 are realised as requirement attributes, per the standard's identification and traceability guidance | None |
| ISO/IEC/IEEE 29148:2018 | §6.5.1–6.5.3 | Trace to architecture (`AR-001`, `AR-003`), verification and validation is specified as mandatory link types `T-04`, `T-07`, `T-08` | None |
| ISO/IEC/IEEE 29148:2018 | §6.6.3 *Measurement for requirements* | §5 defines the measures, their formulas and their publication rules | None |
| ISO/IEC/IEEE 29119-3:2021 | Test traceability | Requirement → test case → execution → result is link types `T-07`, `T-08` | None |
| ISO/IEC 25010:2023 | — | Quality-attribute traces (`T-05`) bind NFRs to the functional requirements they constrain | None |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | What it provides |
|---|---|
| `RQ-001` §3.10.3, §3.10.5, Appendix A | The 13 attributes, the 3,347 + 42 baseline, the single denominator |
| `RQ-003` §3.3 | The disposition attribute schema linking requirement → gap → component |
| `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §1, §2 | 18 business objectives `BO-01`–`BO-18`; 95 registered `KPI-nnn` |
| `.../05-02` | Entity catalogue — 434 distinct `fix.*` references |
| `.../05-03` | Integration and event catalogue |
| `.../05-04` | Roles `R01`–`R38`; `SOD-01`–`SOD-12` |
| `.../05-05` | 140 `BRU` identifiers |
| `.../05-06` | 104 unique `NFR` identifiers |
| `../../primary-doc/…URD.md` | 245 user stories `US-<CODE>-nnn` |
| `../../primary-doc/…BRD.md` §13 | Use cases `UC-nnn` |
| `../../project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018` | Test content packs |

### 2.3 Audit findings this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `TS-01` (critical) | `AUDIT-014` | §5.1 fixes one denominator, states the formula, and forbids publication of any coverage figure computed otherwise | Closes when the first coverage report issues at the Wave 1 gate |
| `C-02` (critical) | `00-06` | The RTM covers **all** requirements in the `RQ-001` baseline. `M31`'s 53 rows are in Appendix A and therefore in the matrix | Closed on RTM population |
| `RP-01` (critical) | `AUDIT-015` | §6.4 measures the KPI trace: **95 registered, 251 in use, 198 unregistered**; link type `T-09` makes each one visible | Closes when `06-02` registers or retires the 198 |
| `AP-01` (critical) | `AUDIT-016` | Link type `T-06` reciprocates event producer and consumer, which is the check that finds a consumed-and-never-published event | Closes with `IN-003` |
| `F3` (critical) | `AUDIT-013` | Link type `T-10` reciprocates field references against the data dictionary | Closes with `DA-002` |
| **`RQA-17`** *(raised here)* | This document | **4 of 18 business objectives — `BO-01`, `BO-09`, `BO-15`, `BO-16` — are cited by no module or portal specification.** Only 30 of 79 specifications cite any objective | Open — §6.2 |
| **`RQA-18`** *(raised here)* | This document | **1,370 distinct entities are named across §10.1 + §10.2 of the 79 specifications — 1,335 owned, 35 referenced-but-unowned — against 434 catalogued in `05-02`** *(recounted 2026-08-19 18:46 (+06); the earlier 1,360 is superseded)* | Open — §6.5 |

---

# 3. The Trace Model

## 3.1 The primary thread

```
   BO-nn ──────▶ FR / SWR / SYR ──────▶ FG-nnn ──────▶ FDS / SDD ──────▶ CD-nnn
  business         requirement           gap            design           component
  objective            │                                   │                 │
   (18)                │                                   │                 │
                       ├──────────────────────────────────▶│                 │
                       │                                                     │
                       └──────────▶ TC-nnn ──────▶ execution ──────▶ acceptance
                                    test case        result            evidence
```

**Rule `TR-01`.** The thread is complete for a requirement when every link in it resolves at both
ends. A requirement whose thread is incomplete is not "partially done"; it is **unverifiable**,
and it is reported as such.

## 3.2 Link types

| # | Link | From → To | Cardinality | Direction | Reciprocal? | Mandatory by |
|---|---|---|---|---|:--:|---|
| `T-01` | **Objective realisation** | `BO-nn` → requirement | 1 : n | Both | **✔** | Baseline |
| `T-02` | **Source derivation** | requirement → BRD §, URD `US-`, RFP §, statute, audit finding | n : m | Backward | ✗ | Baseline |
| `T-03` | **Disposition** | requirement → `fit_gap` + `component` (+ `FG-nnn`) | 1 : 1 | Forward | ✗ | `RQ-003` |
| `T-04` | **Design realisation** | requirement → FDS §, SDD § | n : m | Both | **✔** | Wave build start |
| `T-05` | **Quality constraint** | `NFR-nnn` → requirement it constrains | n : m | Both | **✔** | Baseline |
| `T-06` | **Event contract** | producer module → event → consumer module | n : m | Both | **✔** | `IN-003` |
| `T-07` | **Test derivation** | requirement → `TC-nnn` | 1 : n | Both | **✔** | Wave build start |
| `T-08` | **Verification evidence** | `TC-nnn` → execution result → acceptance record | 1 : n | Forward | ✗ | Wave gate |
| `T-09` | **Benefit measurement** | requirement → `KPI-nnn` → `BO-nn` | n : m | Both | **✔** | `BM-002` |
| `T-10` | **Data realisation** | requirement → entity → field | n : m | Both | **✔** | `DA-002` |
| `T-11` | **Rule constraint** | `BRU-<CODE>-nn` → requirement it constrains | n : m | Both | **✔** | `RQ-009` |
| `T-12` | **Role exercise** | requirement → `Rnn` | n : m | Forward | ✗ | `SC-004` |
| `T-13` | **Process realisation** | `BPM-nnn` process step → requirement | n : m | Both | **✔** | `RQ-007` |
| `T-14` | **Story representation** | `US-<CODE>-nnn` → requirement | n : m | Both | **✔** | `RQ-008` |
| `T-15` | **Dependency** | requirement → requirement | n : m | Both | **✔** | Baseline |
| `T-16` | **Migration** | requirement → legacy source → target entity | n : m | Forward | ✗ | `MG-003` |
| `T-17` | **Contract deliverable** | requirement → SoW deliverable | n : m | Both | **✔** | `CO-003` |

**Count check, regenerated before issue (`PG-M10`):** 17 link types, of which **12 are
reciprocal**.

## 3.3 Why direction matters

A one-directional link is how every finding in §2.3 happened. `06-02` declares which modules
serve `BO-01`; no module declares that it serves `BO-01`; nobody noticed, because the assertion
was only ever made from one end. `05-03` consumes `claim.evidence_incomplete`; no module publishes
it; nobody noticed, for the same reason.

**Rule `TR-02` — reciprocity.** For every link type marked reciprocal in §3.2, both ends shall
declare the link. A link declared at one end only is a **defect of class `D-1`** (§8) and is
raised, not silently repaired.

This extends the module template's rule `RG-04`, which already requires reciprocity for module
dependencies, to the other eleven reciprocal link types. `RG-04` works: module dependency
reciprocity is the one link class in the estate with no recorded finding against it. That is the
evidence that the rule is the right one and its coverage is too narrow.

## 3.4 Reciprocity check matrix

| Link | Declared at | And at | Check |
|---|---|---|---|
| `T-01` | `06-02` §1 objective row | Module §2 Evidence Basis | Every `BO-nn` names ≥ 1 module; every module names ≥ 1 `BO-nn` |
| `T-04` | Requirement attribute | FDS §1 / SDD §1 | Set equality both ways |
| `T-05` | `RQ-006` NFR row | Requirement attribute | Every NFR constrains ≥ 1 requirement |
| `T-06` | Module §12.3 Published | Consumer module §12.1 Upstream | Set equality; the check that closes `AP-01` |
| `T-07` | Requirement attribute | Test case header | Every P0/P1 requirement has ≥ 1 case |
| `T-09` | Module §15 KPI table | `06-02` §2 KPI register | Every used `KPI-nnn` is registered |
| `T-10` | Module §10.2 Referenced | Owning module §10.1 Owned | Verbatim entity-name match; the check that closes the 255-reference finding |
| `T-11` | Module §9 rule | `RQ-009` catalogue | Every rule catalogued; every catalogued rule owned by a module |
| `T-13` | `BPM-nnn` step | Requirement attribute | Every L2 process step realises ≥ 1 requirement |
| `T-14` | `US-<CODE>-nnn` | Requirement attribute | Every story maps to ≥ 1 requirement |
| `T-15` | Module §1 Depends on | Other module's Depended on by | `RG-04`, already enforced |
| `T-17` | `CO-003` deliverable | Requirement attribute | Every contracted deliverable traces to requirements |

---

# 4. RTM Schema

## 4.1 The record

The RTM is **one row per requirement**, not one row per link. Links are columns holding sets.
This keeps the denominator identical to the requirement count and makes coverage a column
operation rather than a join.

```yaml
requirement_id: FR-SRM-014
# --- from RQ-001 §3.10.3 -------------------------------------------------
title:            Estimate approval loop
priority:         P0
wave:             W1
status:           Approved
verification_method: Test
owner:            Service Operations Manager
# --- trace links ---------------------------------------------------------
T01_objectives:   [BO-01, BO-05]
T02_sources:      ["BRD §8.1", "URD US-SRM-014", "RFP §6.2"]
T03_disposition:  {fit_gap: build, layer: L5, component: cd_estimate, gap: FG-012}
T04_design:       [FG-012 FDS §6, SDD-M01 §4.3]
T05_nfrs:         [NFR-001, NFR-040]
T06_events:       {publishes: [estimate.issued, estimate.expired], consumes: [service_order.diagnosed]}
T07_tests:        [TC-M01-041, TC-M01-042, TC-E2E-002]
T08_evidence:     {executed: 3, passed: 3, uat: "G1 signed 2027-xx-xx"}
T09_kpis:         [KPI-014]
T10_entities:     [fix.service.estimate, fix.service.order]
T11_rules:        [BRU-SRM-13]
T12_roles:        [R08, R11]
T13_processes:    [BPM-L2-013]
T14_stories:      [US-SRM-014]
T15_depends_on:   [FR-SRM-011, FR-CAT-004]
T16_migration:    []
T17_deliverable:  [SOW-D-07]
# --- control -------------------------------------------------------------
last_traced:      2026-08-18
trace_complete:   false           # computed, never asserted
open_defects:     [D-1/T09]
```

**Rule `TR-03`.** `trace_complete` is **computed** from the mandatory link set for the
requirement's current lifecycle stage (§4.2). It is never set by hand. A field a human can assert
is a field that will be asserted.

## 4.2 Mandatory links by lifecycle stage

| Stage | Links that must resolve | Rationale |
|---|---|---|
| **Proposed** | `T-02` source | A requirement with no source is somebody's idea |
| **Approved** | + `T-01`, `T-05`, `T-11`, `T-15` | Objective, constraints and dependencies known before baseline |
| **Allocated** | + `T-03` disposition, `T-04` design, `T-17` deliverable | Cannot be scheduled without knowing what builds it |
| **Built** | + `T-06`, `T-10`, `T-12` | Contracts and data realised |
| **Verified** | + `T-07`, `T-08` | Tested with a recorded result |
| **Accepted** | + `T-09` where a benefit is claimed | Benefit measurable, per `BM-004` |

## 4.3 Storage

| Horizon | Storage | Rule |
|---|---|---|
| **Now → tool procurement** | A single generated markdown table per module, produced from the module files and the registers by script | Hand-maintained matrices diverge within one sprint. **`TR-04`: the RTM is generated, never typed** |
| **From tool procurement** (`RQ-005` §7) | The requirements-management tool, with links as first-class relations | The tool must support bidirectional link enforcement, or it does not satisfy `TR-02` |
| **Published view** | A coverage report per wave gate, plus an impact-analysis query on demand | `QA-011` consumes it |

**Rule `TR-05`.** The RTM is regenerated before every wave gate and before every published
coverage figure, with an enumeration timestamp (`PG-M11`). A matrix older than the artefacts it
indexes is worse than none, because it is trusted.

---

# 5. Coverage Measurement

## 5.1 One denominator *(closes `TS-01`)*

**Rule `CV-01`.** Every coverage measure in this programme uses the denominator defined in
`RQ-001` §3.10.5 rule `CR-01`: **the count of requirement rows in the baseline manifest**, which
at 2026-08-18 02:15 (+06) is **3,347 adopted + 42 `SWR` = 3,389**.

**Rule `CV-02`.** A coverage figure is published as a triple — *numerator / denominator /
enumeration timestamp*. `"78% covered"` is not a publishable figure. `"2,643 / 3,389 at
2027-01-15 09:00 (+06)"` is.

**Rule `CV-03`.** Where a measure is scoped to a wave, the denominator is the count of
requirements whose `wave` attribute equals that wave, stated explicitly. Wave coverage and
programme coverage are never presented in the same column without their denominators.

## 5.2 The measures

| # | Measure | Formula | Reported to | Cadence |
|---|---|---|---|---|
| `CV-M1` | **Requirement definition coverage** | requirements passing `RQ-001` `CK-01`…`CK-06` ÷ baseline | PMO | Fortnightly |
| `CV-M2` | **Objective coverage** | `BO-nn` with ≥ 1 reciprocal `T-01` ÷ 18 | Steering Committee | Wave gate |
| `CV-M3` | **Disposition coverage** | requirements with `fit_gap` ≠ `undetermined` and evidence ÷ baseline | CFO, `GV-007` | Wave gate |
| `CV-M4` | **Design coverage** | requirements with a resolving `T-04` ÷ requirements at `Allocated` or beyond | Design Authority | Wave gate |
| `CV-M5` | **Test coverage** | requirements with ≥ 1 `T-07` ÷ baseline | QA, `QA-011` | Fortnightly |
| `CV-M6` | **Test coverage, P0** | as `CV-M5`, restricted to `priority: P0` | Wave gate | Wave gate |
| `CV-M7` | **Verification coverage** | requirements with a passing `T-08` ÷ requirements at `Built` or beyond | Wave gate | Wave gate |
| `CV-M8` | **Acceptance coverage** | requirements at `Accepted` ÷ wave baseline | Steering Committee | Wave gate |
| `CV-M9` | **Trace integrity** | requirements with zero open `D-1`…`D-4` defects ÷ baseline | Design Authority | Fortnightly |
| `CV-M10` | **Orphan count** | requirements with no `T-01`, plus objectives with no requirement | Steering Committee | Wave gate |

**Rule `CV-04`.** `CV-M6` — P0 test coverage — is a **gate criterion, not a report**. A wave gate
at which any P0 requirement has no test case fails, regardless of the aggregate percentage.
Aggregates hide exactly the requirements that matter, because P0s are 22.7% of the set and 100%
of the regulatory exposure.

## 5.3 What may not be measured yet

Stated so the absence is deliberate rather than discovered later:

| Measure | Blocked by | Available at |
|---|---|---|
| `CV-M3` disposition coverage | `RQ-003` determination has not started; 3,389 `undetermined` | Wave 1 gate, Wave 1 scope only |
| `CV-M4` design coverage | No FDS or SDD exists (`AR-003` unwritten) | Wave 1 build start |
| `CV-M5`–`CV-M8` | No test case repository exists (`QA-003` unwritten) | Wave 1 build start |
| `CV-M9` | Requires the automated checks in §7.3 | On RTM generation |

---

# 6. Measured Trace Integrity at Issue

*Counted at 2026-08-18 02:15 (+06). This is the position the RTM will be built on top of.*

## 6.1 Summary

| Link | What was measured | Result | Class |
|---|---|---|:--:|
| `T-01` | Business objectives cited by ≥ 1 specification | **14 of 18** | **`D-2`** |
| `T-01` | Specifications citing ≥ 1 business objective | **30 of 79** | **`D-1`** |
| `T-02` | Requirement rows carrying a source attribute | **0 of 3,347** | **`D-1`** |
| `T-03` | Requirements with an evidenced disposition | **0 of 3,389** | `RQ-003` §5.5 |
| `T-05` | NFR identifiers registered / duplicated | 104 unique in 109 rows — **5 duplicated** | **`D-3`** |
| `T-07` | Requirement rows carrying a verification method | **0 of 3,347** | **`D-1`** |
| `T-09` | KPI identifiers used vs registered | **251 used, 95 registered — 198 unregistered** | **`D-2`** |
| `T-10` | Entity references declared in module §10 vs catalogued in `05-02` | **1,370 declared (1,335 owned), 434 catalogued** | **`D-2`** |
| `T-11` | Business rules in module §9 vs catalogued in `05-05` | **1,330 vs 140 — 122 overlap** | **`D-2`** |
| `T-12` | Role identifiers used vs registered | `R01`–`R38` registered; **`R39`–`R50` used across 15 files, unregistered** | **`D-2`** |
| `T-12` | Segregation-of-duties identifiers | `SOD-01`–`SOD-12` registered; **`SOD-13`–`SOD-30` used, unregistered** | **`D-2`** |
| `T-14` | User stories vs requirements | 245 stories; **no story carries a requirement link** | **`D-1`** |
| `T-15` | Module dependency reciprocity (`RG-04`) | **Enforced; no finding recorded** | ✔ |

## 6.2 Finding `RQA-17` — four business objectives have no owner in the specification estate

`06-02` §1 registers 18 objectives. Searching all 79 module and portal specifications for `BO-nn`
citations at 02:15 (+06) returns fourteen: `BO-02`, `BO-03`, `BO-04`, `BO-05`, `BO-06`, `BO-07`,
`BO-08`, `BO-10`, `BO-11`, `BO-12`, `BO-13`, `BO-14`, `BO-17`, `BO-18`.

**Absent: `BO-01`, `BO-09`, `BO-15`, `BO-16`.**

| Objective | Target | Modules `06-02` names | Modules that name it |
|---|---|---|---|
| `BO-01` Automate the end-to-end service order lifecycle | 20% → **85%** processed without manual intervention | M01, M02, M20 | **none** |
| `BO-09` Remove capacity constraints on growth | **+87%** revenue over 18 months post-W4 | All | **none** |
| `BO-15` Make competency an enforced control | **Zero** claims rejected for uncertified technician | M22 | **none** |
| `BO-16` Bring every customer conversation into the system | ~0% → **100%** conversations captured | M27 | **none** |

`BO-01` is the programme's headline automation objective and `BO-09` carries its growth case.
Neither is claimed by any specification. **This is a one-directional link, not a scope gap** —
the modules almost certainly do deliver these objectives. But nothing in the estate says so, and
therefore nothing can report progress against them.

Only **30 of 79** specifications cite any objective at all, so 49 specifications currently trace
to no business purpose.

## 6.3 The absent attributes

Three attributes are absent from **every** requirement row in the estate, and each defeats a link
type outright:

| Attribute | Missing from | Link defeated | Consequence |
|---|---|---|---|
| `source` | 3,347 of 3,347 | `T-02` | No requirement can be traced back to the business need that produced it. Descoping is therefore blind |
| `verification_method` | 3,347 of 3,347 | `T-07` | No requirement states how it will be proved. `QA-003` has nothing to derive a technique from |
| `owner` | 3,347 of 3,347 | `T-01`, `T-08` | No named role accepts any requirement at UAT |

## 6.4 Finding — the KPI trace *(closes the measurement half of `RP-01`)*

| Measure | Count |
|---|---:|
| `KPI-nnn` registered in `06-02` §2 | **95** |
| `KPI-nnn` used across the 79 specifications | **251** |
| Used and **not** registered | **198** |
| Registered and used | 53 |
| Registered and never used | **42** |

The module template §0 already forbids local `KPI` allocation — *"Do not allocate locally"* — and
198 identifiers were allocated locally anyway. That is a rule with no mechanical check behind it,
which is what link type `T-09` and check `CT-06` supply.

**Consequence for the benefit case.** `AUDIT-015` places roughly BDT 396 lac of the BDT 876 lac
benefit case outside what can be claimed, because 44 of 95 baselines are absent. The 198
unregistered identifiers make it worse: a benefit measured against an unregistered KPI cannot be
reconciled to `06-02` at all.

## 6.5 Finding `RQA-18` — the entity trace

Module and portal §10 tables declare **1,370 distinct entities — 1,335 owned and 35 referenced but owned by nobody** (`AR-008-F-01`). `05-02`, the entity catalogue,
carries **434**. The estate therefore references roughly three times as many entities as the
catalogue defines.

This is the same defect class as the 255-reference finding already recorded in
`_MODULE_TEMPLATE` §10.2, measured at a different scope: that finding counted references naming
entities *their declared owner does not define*; this one counts references naming entities *the
catalogue does not define*. Both are `T-10` failures, and both are closed by the same
reciprocity check once `DA-001` and `DA-002` exist.

---

# 7. Production and Maintenance

## 7.1 Who populates what

| Link | Populated by | When |
|---|---|---|
| `T-01`, `T-02`, `T-11`, `T-15` | Module author / Business Analyst | At requirement authoring; retrofitted during the `RQ-001` §3.10.7 conversion |
| `T-03` | Solution Architect | At fit-gap determination (`RQ-003` §8) |
| `T-04` | FDS / SDD author | At design |
| `T-05` | Requirements Manager | At `RQ-006` re-basing |
| `T-06` | Integration Architect | At `IN-003` event catalogue |
| `T-07` | QA Lead | At test design (`QA-003`) |
| `T-08` | QA / UAT coordinator | At execution |
| `T-09` | Benefit owner | At `BM-002` baseline measurement |
| `T-10` | Data Architect | At `DA-001` / `DA-002` |
| `T-12` | CISO | At `SC-004` role registration |
| `T-13` | Process Owner | At `RQ-007` model production |
| `T-14` | Business Analyst | At `RQ-008` story conversion |
| `T-17` | Commercial Manager | At `CO-003` SoW |

## 7.2 Cadence

| Event | Action |
|---|---|
| Requirement created or changed | Its row is regenerated; `trace_complete` recomputed |
| Fortnightly | `CV-M1`, `CV-M5`, `CV-M9` reported to PMO (`05-01` §6) |
| Wave gate | Full RTM regeneration, all ten measures, timestamped (`TR-05`) |
| Design or test artefact issued | Reciprocal link written at both ends before issue |
| Audit | RTM is the primary evidence artefact |

## 7.3 Automated checks

| # | Check | Detects | Closes |
|---|---|---|---|
| `CT-01` | Every requirement resolves ≥ 1 `BO-nn`, and every `BO-nn` is resolved by ≥ 1 requirement | Orphan requirements and unowned objectives | `RQA-17` |
| `CT-02` | Every requirement carries `source`, `owner`, `verification_method` | The three absent attributes | §6.3 |
| `CT-03` | Every module §12.1 event appears in some module's §12.3 | Consumed-never-published events | `AP-01` |
| `CT-04` | Every §10.2 referenced entity appears verbatim in its owner's §10.1 | Phantom entity references | 255-ref finding |
| `CT-05` | Every referenced field exists in the data dictionary | Phantom fields | `F3` |
| `CT-06` | Every used `KPI-nnn` is registered in `06-02` | Local KPI allocation | `RP-01` |
| `CT-07` | Every used `Rnn` and `SOD-nn` is registered in `05-04` | Unregistered roles | `OP-10` |
| `CT-08` | Every used `BRU-` is catalogued and every catalogued rule is owned | Rule drift | `EO-02` |
| `CT-09` | Every `NFR-nnn` is unique and constrains ≥ 1 requirement | Double-allocation and orphan NFRs | `AP-02` |
| `CT-10` | No requirement precedes a requirement it depends on, by wave | Wave-order violations | `RG` wave check |
| `CT-11` | Every P0/P1 requirement has ≥ 1 test case | Untested critical requirements | `CV-M6` gate |
| `CT-12` | Every reciprocal link resolves at both ends | All `D-1` defects | `TR-02` |

**Rule `TR-06`.** `CT-01` … `CT-12` run on every RTM regeneration and, from Wave 1, as a
documentation gate in CI. **A check that runs only when someone remembers is not a control** —
that is the lesson of `PG-M10`, published because care alone failed twice in one session.

---

# 8. Trace Defect Taxonomy

| Class | Defect | Example from the estate | Disposition |
|:--:|---|---|---|
| **`D-1`** | **Link asserted at one end only** | `06-02` names modules for `BO-01`; no module names `BO-01` | Raise to the owner of the silent end. **Never repair by deleting the asserted end** |
| **`D-2`** | **Link target does not exist** | 198 unregistered `KPI-nnn`; `R39`–`R50`; 9 non-existent `MD-028` fields (`F3`) | Register the target or retire the reference. A dangling reference is never left |
| **`D-3`** | **Link target is ambiguous** | `NFR-090` denotes two different requirements; `FR-ECM-` denotes M12 in `05-01` and M38 in the module estate | **Highest severity.** Both readings are plausible, so the defect survives review. Resolve in `RR-002` |
| **`D-4`** | **Link is stale** | `05-01` §4 portal allocation `001…140` against an actual `001…358` | Re-derive from the governing artefact and re-date |
| **`D-5`** | **Link is absent where mandatory** | 3,347 requirements with no `verification_method` | Populate; until then the requirement cannot progress past `Verified` |

**Rule `TR-07`.** A trace defect is recorded against the **link**, not against either document, and
is closed only when both ends agree. Closing it by editing the end that is easier to reach is how
`D-3` defects are created.

---

# 9. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | RTM granularity | (a) One row per link; (b) one row per requirement with link-set columns | **(b)** | Keeps the denominator identical to the requirement count; coverage becomes a column operation, not a join |
| D-02 | Maintenance method | (a) Hand-maintained; (b) generated from source artefacts | **(b)** | A hand-maintained matrix diverges within one sprint and is then trusted while wrong |
| D-03 | Reciprocity scope | (a) Dependencies only, as `RG-04`; (b) all 12 reciprocal link types | **(b)** | `RG-04` is the one link class with no recorded finding. The rule works; its coverage was too narrow |
| D-04 | `trace_complete` | (a) Author-asserted; (b) computed | **(b)** | An assertable completeness field will be asserted, which is `PGD-A1-08` in miniature |
| D-05 | P0 test coverage | (a) Reported as a percentage; (b) a pass/fail gate criterion | **(b)** | An aggregate hides the 22.7% of requirements carrying 100% of the regulatory exposure |
| D-06 | How to close `D-1` defects | (a) Delete the asserted end; (b) require the silent end to declare | **(b)** | Deletion destroys information and makes the estate look consistent while being less complete |
| D-07 | Whether to publish coverage before the RTM is populated | (a) Publish provisional figures; (b) publish the measures and state which are blocked | **(b)** | `TS-01` was caused by figures published ahead of their basis |

---

# 10. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Which modules claim `BO-01`, `BO-09`, `BO-15` and `BO-16`, and will they declare it? | Programme Director | W1 | `CV-M2`; benefit reporting on four objectives |
| Q-02 | Are the 198 unregistered `KPI-nnn` to be registered in `06-02` or retired? | Benefit owners / PMO | W1 | `T-09`, `BM-002`, roughly BDT 396 lac of benefit claim |
| Q-03 | Which tool will hold bidirectional links, and does the shortlist enforce reciprocity? | Requirements Manager | W1 | `TR-02` at scale; `RQ-005` §7 |
| Q-04 | Who owns the generation script until a tool exists, and where does it run? | PMO | **Now** | `TR-04`, `TR-06` |
| Q-05 | Does `RR-006` (master cross-reference index) supersede the generated RTM, or consume it? | Enterprise Architecture | W2 | Duplication risk between `RQ-004` and `RR-006` |
| Q-06 | Is `FR-ECM-` an M12 or M38 identifier? A `D-3` defect cannot be traced around | Enterprise Architecture | **Now** | Every trace touching `ECM` |

---

# 11. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | 17 link types defined with direction, cardinality and reciprocity | §3.2 |
| AC-02 | Reciprocity rule stated with the check for each reciprocal link | §3.3, §3.4 |
| AC-03 | RTM schema defined with `trace_complete` computed, not asserted | §4.1, `TR-03` |
| AC-04 | Mandatory link set defined per lifecycle stage | §4.2 |
| AC-05 | One denominator, with formula and publication rule | §5.1, `CV-01`–`CV-03` |
| AC-06 | Ten coverage measures with formulas, audiences and cadences | §5.2 |
| AC-07 | Measures currently unavailable are declared, not left to be discovered | §5.3 |
| AC-08 | Trace integrity measured against the estate, with counts and timestamp | §6 |
| AC-09 | Twelve automated checks, each mapped to the audit finding it closes | §7.3 |
| AC-10 | Defect taxonomy with a disposition rule that forbids repair-by-deletion | §8, `TR-07` |

---

# 12. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` | Requirement set, denominator, the 13 attributes the links attach to |
| Upstream | `RR-002` | Identifier convention; `D-3` defects cannot be closed without it |
| Upstream | `06-02` §1, §2 | Business objectives and the KPI register |
| Lateral | `RQ-003` | `T-03` disposition |
| Lateral | `RQ-006` | `T-05` quality constraints |
| Lateral | `RQ-007` | `T-13` process realisation |
| Lateral | `RQ-008` | `T-14` story representation |
| Lateral | `RQ-009` | `T-11` rule constraints |
| Downstream | `QA-011` | Requirements-to-test coverage report, computed from `CV-M5`–`CV-M7` |
| Downstream | `QA-001`, `QA-003` | Test strategy and case derivation consuming `T-07` |
| Downstream | `BM-004` | Benefit realisation consuming `T-09` |
| Downstream | `RR-006` | Master cross-reference index, of which this is the requirement thread |
| Downstream | `CO-003` | Deliverable acceptance consuming `T-17` |
| Downstream | `AR-003`, `DA-002`, `IN-003` | Design, dictionary and event catalogue supplying `T-04`, `T-10`, `T-06` |

---

# 13. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-002`](RQ-002_System_Requirements_Specification.md) ·
[`RQ-003`](RQ-003_Fit_Gap_Analysis_and_Functional_Design_Specification.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-007`](RQ-007_Business_Process_Model_Repository.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`RQ-010`](RQ-010_Acceptance_Criteria_and_Definition_of_Done_Standard.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02` §1, §2 ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01`…`05-06` ·
`../../1000fix_ERP_Module/03_Modules/` §2, §9, §10, §12, §13, §15 of all 79 specifications ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §6–17 ·
`../../project_content/13_Test_and_Acceptance_Content/`

**External**

| Reference | Verified on |
|---|---|
| ISO/IEC/IEEE 29148:2018 §5.2.8, §6.5, §6.6.3 | 2026-08-18 |
| ISO/IEC/IEEE 29119-3:2021 | 2026-08-18 |
| ISO/IEC 25010:2023 | 2026-08-18 |

---

# 14. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 17 link types with 12 reciprocal; one denominator fixed; ten coverage measures; trace integrity measured; findings `RQA-17`, `RQA-18` raised | *Pending — `GV-002`* |

---

*`RQ-004` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
