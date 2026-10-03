---
id: QA-003
title: Test Design Specification and Case Repository
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
approver: Head of Quality Engineering with Enterprise Architecture
standards_basis: >
  ISO/IEC/IEEE 29119-4:2021 (test techniques) · ISO/IEC/IEEE 29119-3:2021 §10 (test design
  specification, test case specification, test procedure specification) · ISO/IEC/IEEE 29148:2018
  §5.2.8 (verifiability) · BS 7925-2 technique definitions
traces_to: >
  PGD-000 QA-003 · RQ-004 §6.3 (verification_method absent from 3,347 of 3,347 rows) ·
  AUDIT-014 TS-01 · QA-001 QAA-03 (620 identified cases in six incompatible schemes) ·
  RQ-001 CR-01 · 05-05 business rules · 05-04 §10 criterion 6
depends_on: QA-001 (levels, risk classes) · RQ-001 (requirements, attributes) · RQ-004 (RTM, link T-07) · RQ-009 (business rules)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-003 — Test Design Specification and Case Repository

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-4:2021 · 29119-3:2021 §10

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-003` exists in `PGD-000` Category 08, status ◐ `P1` `W1`.
> 2. **`PG-03` Count, do not consult.** Case counts, scheme counts and requirement counts taken from
>    the filesystem at **2026-08-18 22:01 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1. The technique catalogue in §4 is 29119-4:2021's, not invented.
> 4. **`PG-M4` Verify citations.** Editions inherited from `QA-001` §18, verified 2026-08-18.
> 5. **`PG-05` Identifiers are permanent.** §5 introduces a new case-identifier scheme and
>    **does not renumber a single existing case** (`RG-02`). The crosswalk is §5.5.

---

## 1. Purpose

`QA-001` says a case exists for every requirement at the depth its risk class buys. **This document
says how that case comes into being, what it must contain, what it is called, and where it lives.**

Three counted facts define the problem it solves.

| # | Counted fact | Source | Consequence |
|:--:|---|---|---|
| 1 | **`verification_method` is absent from 3,347 of 3,347 requirement rows** | `RQ-004` §6.3, measured 2026-08-18 02:15 (+06) | **No requirement in this estate states how it will be proved.** Link type `T-07` is defeated outright, and `QA-003` has nothing to derive a technique from |
| 2 | **620 distinct case identifiers exist, in six mutually incompatible schemes**, against ~1,700 executable items | `QA-001` §4.4, counted here | Roughly two-thirds of the test estate cannot be traced, counted or reported (`QAA-03`) |
| 3 | **Three of fifteen test-script packs contain no case identifiers at all** — `TS-013`, `TS-016`, `TS-018` | counted §3.2 | Their content is real and their cases are not addressable, so `CV-M5` cannot see them |

The estate's test *content* is good. What it lacks is the **derivation** — the statement, per
requirement, of which technique produces which cases, so that "we tested it" becomes checkable
rather than assertable. `TS-003`…`TS-005` supply scenario libraries; a scenario library is a set of
useful journeys, not a set of cases derived from requirements by a stated method.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The missing attribute** — `verification_method`, its values, and the procedure that populates 3,347 rows (§3) |
| 2 | **The technique catalogue** — 29119-4:2021 techniques mapped to requirement class and risk class (§4) |
| 3 | **The case identifier scheme** — one derivable form, with a crosswalk that renumbers nothing (§5) |
| 4 | **The case specification** — the 18 attributes every case carries (§6) |
| 5 | **The case repository** — structure, storage, tooling, versioning and review (§7) |
| 6 | **Derivation rules per requirement class**, including the eight `RC-A` populations (§8) |
| 7 | **Negative, boundary and abuse case obligations** (§9) |
| 8 | **Case quality** — the eight checks a case must pass before it enters the repository (§10) |
| 9 | **Maintenance** — how a case changes when its requirement changes (§11) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Which levels exist, entry/exit, risk model | `QA-001` | Consumed |
| Scheduling of case execution | `QA-002` | |
| Test data values and personas | `QA-004`, `TS-002` | This document specifies a case's **data requirement**; `QA-004` supplies the data |
| Automation code | `QA-005` | A case is specified here and implemented there |
| Performance workload derivation | `QA-006` | Its cases derive from volumetrics, not from requirements |
| Security abuse-case derivation | `QA-007` | §9.3 states the interface; `SC-002`'s 32 abuse cases are the basis |
| Accessibility criterion derivation | `QA-008` | Derived from WCAG success criteria, not from `FR-` rows |
| Coverage measurement | `QA-011` | This document makes coverage *possible*; `QA-011` measures it |
| The requirement set itself | `RQ-001` | This document consumes it and asks for one attribute back |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Test analysts and QA engineers** | §4–§10 — the working method: technique, identifier, specification, quality checks |
| **Business analysts** | §3 — the `verification_method` attribute they must populate, and what each value commits to |
| Developers | §6, §9 — the case shape automation implements, and the negative-case obligation |
| Module business owners | §8 — why their module's rules produce the cases they do |
| `QA-011` and auditors | §5, §7 — how a case is addressed and where it is found |
| Implementation vendor | The derivation obligation attaching to every delivered requirement |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 29119-4:2021** (2nd ed.) | Specification-based, structure-based and experience-based technique definitions | §4's catalogue is the standard's, cited by name. Coverage measures per technique are its definitions | **Departure:** structure-based techniques (statement, branch, MC/DC) are applied **only at L1**, and only branch coverage is mandated, on financial paths. Rationale: `QA-002` `QA-002-D-02` |
| **ISO/IEC/IEEE 29119-3:2021** (2nd ed.) | §10 test design specification · test case specification · test procedure specification | §6 is the case specification; §7 the repository; §8 the design specification per class | **Departure:** the three are held as **one record with attributes**, not three documents. Rationale: `QA-003-D-03` |
| **ISO/IEC/IEEE 29148:2018** | §5.2.8 verifiability | §3 makes `verification_method` a required attribute, which is what §5.2.8 asks for and the estate does not have | None |
| **BS 7925-2** | Technique definitions | Used where 29119-4 defers to it for definitions | None |
| **ISTQB** | Test design terminology | Terminology only; not a conformance claim | Declared |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `RQ-001` §3.10 | The 13 requirement attributes, the well-formedness checks `CK-01`…`CK-12`, and the **3,347-row** baseline |
| `RQ-004` §6.3 | **`verification_method` absent from 3,347 of 3,347** — the gap this document closes |
| `RQ-004` §4 | Link type `T-07` requirement → test, which a case must populate |
| `RQ-009` | The business-rules catalogue; class `H` hard rules requiring negative cases |
| `05-04` §2, §10 | **456 portal-matrix cells, 77 granted, 379 denied**; criterion 6 makes negative testing a release condition |
| `05-05` | Business rules `BRU-*`; 137 distinct rules cited by the `TS` packs, 136 resolving |
| `QA-001` §4.4, §5.3, §5.4 | The 620/6-scheme position; the depth each risk class buys; the eight `RC-A` populations |
| `TS-001` §4.3 | The existing script identifier standard, which §5 extends rather than replaces |
| `TS-003`…`TS-017` | 620 existing cases whose identifiers are permanent under `PG-05` |
| `SC-002` | **97 threats, 32 abuse cases** — `QA-007`'s derivation basis, referenced in §9.3 |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it | Residual |
|---|---|---|---|
| `RQA-18` (`T-07` defeated) | `RQ-004` §6.3 | §3 specifies the attribute, its six values, and the population procedure with an owner and a wave | Population is 3,347 rows of analyst work — `Q-01` |
| `QAA-03` | `QA-001` §4.4 | §5 gives one derivable identifier form, and §5.5 crosswalks all 620 existing cases without renumbering any | Register change in Category 13 to record the crosswalk |
| `TS-01` (partial) | `AUDIT-014` | Coverage needs a numerator as well as a denominator. §5 and §7 make the numerator countable | `QA-011` publishes it |
| `PGD-000` `QA-003` row | Master register | *"2,930+ requirements need cases derived by a stated technique. `TS-003…005` provide scenario libraries, not derived cases"* — §4 and §8 supply the technique per class | — |

---

## 3. The Missing Attribute

### 3.1 What is missing, and why it defeats everything downstream

> **`RQ-004` §6.3, measured at 2026-08-18 02:15 (+06): `verification_method` is missing from
> 3,347 of 3,347 requirement rows.** The consequence it records is exact — *"No requirement states
> how it will be proved. `QA-003` has nothing to derive a technique from."*

A requirement without a verification method is not testable, and ISO/IEC/IEEE 29148:2018 §5.2.8
makes verifiability a property of a well-formed requirement rather than an optional extra. The
estate's requirements are, as `RQ-001` §3.10.4 puts it, *"well-written phrases rather than badly
written requirements"* — the failure is structural.

### 3.2 The six values

Deliberately few. A long list produces inconsistent classification; six can be assigned reliably by
a business analyst without a test background.

| Value | Meaning | Produces cases at | Evidence class |
|---|---|---|:--:|
| **`T` Test** | Proved by executing the system against defined inputs and checking outputs | L1–L7, L12 | `E5`, `E1` |
| **`A` Analysis** | Proved by reasoning over the design or the data — a model, a calculation, a query | L1, L8 | `E2` |
| **`D` Demonstration** | Proved by operating the system and observing, without instrumented measurement | L6, L7 | `E1` |
| **`I` Inspection** | Proved by examining the artefact — a document, a configuration, a label, a screen | L10, L11 | `E2`, `E6` |
| **`M` Measurement** | Proved by instrumented measurement against a numeric target | L8, L12 | `E3`, `E2` |
| **`C` Certification** | Proved by a third party accepting it — NBR, the bank, a brand | L7 | `E8` |

> **`TDS-01`.** Every requirement carries **exactly one** `verification_method`. Where two apply,
> the requirement is doing two things and is split under `RQ-005` change control. A requirement
> needing both a measurement and a certification — *"Mushak 9.1 filed by the 15th and accepted"* —
> is two requirements, and treating it as one is why `G3-04`'s evidence has been ambiguous.

### 3.3 The population procedure

3,347 rows is analyst work, not a decision. It is sequenced so that the rows that block the earliest
gate are populated first.

| # | Rule |
|---|---|
| `TDS-02` | **Population is by wave, in `AR-006` build order.** W1 scope first; the full set is never a prerequisite for starting |
| `TDS-03` | **The default is `T`.** An analyst may assign `T` without justification; assigning any other value requires a one-line reason recorded in the row. This makes the *cheap* answer the *safe* answer |
| `TDS-04` | **`C` Certification requires a named counterparty** and a named contact, because `E8` evidence requires one (`GA-01`) |
| `TDS-05` | **`M` Measurement requires the target and the tolerance to be present in the requirement.** A measurement method against *"fast"* is not a method — this is `RQ-001` `CK-04`'s subjective-language check applied at derivation time |
| `TDS-06` | **A row that cannot be assigned a method is a defective requirement**, raised to the requirement owner under `TR-06`, not assigned `T` to clear the queue |
| `TDS-07` | Population is a **`RQ-005` change-controlled edit** to the requirement row, and the denominator does not move (`CR-03`) |

**Sequence and owner:**

| Wave | Rows in scope | Owner | Due |
|:--:|---|---|:--:|
| W1 | The W1 requirement slice | Business Analysts with the QA Lead | **T−6 of `G1`** |
| W2–W4 | Rolling, one wave ahead | Business Analysts | T−6 of each gate |
| W5–W9 | Rolling | Business Analysts | T−6 of each gate |

> **This is roughly 3,347 one-line decisions.** At a conservative 40 rows per analyst-hour with the
> `TDS-03` default, that is **~84 analyst-hours ≈ 11 analyst-days** for the whole estate — small, and
> it unblocks `T-07`, `CV-M5`, `CV-M6` and `CV-M7`. Stated so the cost is not assumed to be large and
> the work therefore deferred.

---

## 4. The Technique Catalogue

### 4.1 The rule

> **`TDS-08`.** Every case is produced by a **named technique from §4.2**, and the case records which
> one. A case with no technique is an anecdote: it cannot be shown to be sufficient, it cannot be
> shown to be redundant, and it cannot be regenerated when the requirement changes.

### 4.2 Techniques, from ISO/IEC/IEEE 29119-4:2021

**Specification-based** — derived from what the requirement says:

| Technique | Use when the requirement… | Coverage measure | Levels |
|---|---|---|---|
| **Equivalence partitioning** | classifies inputs into classes treated alike | Each partition exercised ≥ 1 | L1, L2, L5, L7 |
| **Boundary value analysis** | has thresholds, limits, ranges, dates | Both sides of every boundary, plus the boundary | L1, L2, L5, L7 |
| **Decision table testing** | combines conditions into outcomes — approval bands, entitlement, pricing | Every feasible rule column | L1, L5, L7 |
| **Cause–effect graphing** | has conditions whose interactions matter | Every cause–effect pair | L1, L5 |
| **State transition testing** | has a lifecycle — service order, claim, contract, consignment | Every valid transition; **every invalid transition rejected** | L1, L5, L7 |
| **Classification tree** | has several independent input dimensions | Every leaf ≥ 1; pairwise across trees | L5 |
| **Combinatorial (pairwise)** | has many parameters whose full cross-product is infeasible | All pairs | L5, L8 |
| **Scenario / use case testing** | describes an actor completing a goal | Every main flow + every alternate + every exception | L5, L6, L7 |
| **Random / statistical** | is about volume behaviour rather than a specific outcome | Distribution stated | L8 |
| **Error guessing** | is in an area with a known defect history | Charter recorded | L5, exploratory |

**Structure-based** — derived from the code:

| Technique | Applied at | Mandated? |
|---|---|:--:|
| Statement coverage | L1 | ≥ 80% of custom code (`LVP-U1`) |
| **Branch coverage** | L1 | **100% on financial and tax paths** (`LVP-U2`) |
| Condition / MC/DC | L1 | Only where a `DI-01` money path has ≥ 4 conditions |

**Experience-based** — derived from the tester:

| Technique | Applied at | Constraint |
|---|---|---|
| Exploratory (charter-based) | L5, L7 | Time-boxed; charter and findings recorded. **Never a substitute for a derived case at `RC-A`/`RC-B`** |
| Checklist-based | L10, L11 | The checklist is the derived artefact — `TS-016`'s 21 checks are of this kind |

### 4.3 Technique by risk class *(`QA-001` §5.3, made concrete)*

| Risk class | Minimum technique set |
|:--:|---|
| **`RC-A`** | Equivalence partitioning **+** boundary value analysis **+** decision table (if conditions combine) **+** state transition (if a lifecycle) **+** **negative cases on every rule** **+** abuse cases where `SC-002` names a threat. **No sampling** |
| **`RC-B`** | Equivalence partitioning + boundary value analysis + decision table or state transition as applicable + negative cases on every hard rule |
| **`RC-C`** | Equivalence partitioning + boundary values. Sampling permitted, **with the sample and its method recorded** (`GA-05`) |
| **`RC-D`** | Exploratory, charter-based, time-boxed |

### 4.4 Technique by requirement class

| Requirement class | Identified by | Primary techniques |
|---|---|---|
| **Data-entry / validation** | A field, a format, a constraint | Equivalence partitioning, boundary values |
| **Calculation** — money, tax, commission, payroll | `DI-01` decimal path | Boundary values, decision table, **branch coverage at L1** |
| **Lifecycle / status** | A state model in module §6 | State transition, incl. **every invalid transition** |
| **Authorisation** | A role, a permission, a scope | **Decision table over `role × object × action`**, positive **and** negative (§9.2) |
| **Business rule** `BRU-*` | `05-05` / `RQ-009` | Decision table; class `H` rules get a mandatory negative case |
| **Integration** | An `IN-002` operation or `IN-003` event | Contract test (`IN-008`), plus equivalence partitioning on payload |
| **Statutory output** | Mushak, BEFTN, income tax | Decision table + **`C` certification** + `E8` |
| **Journey** | A `05-06` §11 critical journey | Scenario testing, all flows |
| **Non-functional, numeric** | `NFR-` with a target | **`M` measurement**; workload model in `QA-006` |
| **Non-functional, qualitative** | `NFR-` without a number | **`I` inspection** against a defined checklist — and the requirement is flagged to `RQ-001` `CK-04` |
| **Offline / sync** | `AR-010` paths | State transition + **conflict matrix** + field measurement |
| **Localisation** | Bilingual surface | Checklist + inspection + **expansion layout** (`QAA-09`) |
| **Accessibility** | A WCAG success criterion | Checklist + assistive-technology inspection (`QA-008`) |

---

## 5. The Case Identifier Scheme

### 5.1 The problem, counted

**Six incompatible schemes across fifteen packs**, and three packs with none:

| Scheme | Form | Packs | Cases |
|---|---|---|---:|
| SIT | `SIT-<category>-nnn` | `TS-003`, `TS-004`, `TS-005`, `TS-008` | 154+ |
| UAT | `UAT-R<nn>-nnn`, `UAT-R<nn>-P<nn>-nnn` | `TS-006`…`TS-011` | 352 |
| E2E | `E2E-nn` | `TS-012` | 17 |
| Performance | `PERF-NFR-nnn-nn` | `TS-014` | 38 |
| Offline | `OFF-nnn` | `TS-015` | 33 |
| Security | `SEC-nnn`, `SEC-SOD-nn` | `TS-017` | 19 |
| **none** | — | **`TS-013`, `TS-016`, `TS-018`** | **0 addressable** |

Four consequences, each observable today: cases cannot be counted across packs; `CV-M5` cannot join
requirement to case; a case cannot be cited in a defect without ambiguity; and the three
schemeless packs are invisible to every measure.

### 5.2 The scheme

> **`TDS-09`.** A case identifier is **derivable from the case's own properties** and needs no
> allocator:
>
> ```text
> TC-<LEVEL>-<SCOPE>-<nnn>
>
>   LEVEL  = L1 … L13                (QA-001 §4.2)
>   SCOPE  = the module, portal, role or NFR the case is scoped to
>            e.g. M01, P03, R06, NFR-037
>   nnn    = sequence within (LEVEL, SCOPE), zero-padded to three
> ```

This is `BE-005`'s solution to the same problem — sequential allocation across concurrent authors
produced 48 colliding CD identifiers denoting 107 components — applied to cases. **A derivable
identifier cannot collide**, because two authors working on the same `(LEVEL, SCOPE)` pair are by
definition working on the same thing and will see each other's rows.

| Property | Value |
|---|---|
| Uniqueness | Guaranteed within `(LEVEL, SCOPE)`; the pair is globally unique |
| Allocator | **None required** — the defect behind `RQA-34`, `PGD-A2-27` and five identifier collisions in this repository |
| Sortable | Yes, by level then scope |
| Meaningful | The level and the scope are readable without a lookup |
| Stable | A case keeps its identifier for life (`PG-05`) |

### 5.3 Examples

| Case | Identifier |
|---|---|
| Unit test of the Mushak 6.3 VAT calculation in `M19` | `TC-L1-M19-014` |
| SIT scenario: warranty order in `M01` → claim in `M09` with evidence | `TC-L5-M01-007` |
| UAT script for a Branch Manager cash procedure | `TC-L7-R06-003` |
| Negative test: `R25` denied the seller payout screen on `P07` | `TC-L9-P07-041` |
| Performance scenario for `NFR-037` offline sync ≤ 30 s | `TC-L8-NFR-037-002` |
| Accessibility check 2.4.7 focus visible on `P03` | `TC-L10-P03-021` |

### 5.4 What this scheme does **not** do

> **It does not renumber a single existing case.** `PG-05` makes identifiers permanent and `RG-02`
> forbids renumbering; `BE-005` observed the same constraint when it replaced sequential `CD-nnn`
> allocation. The 620 existing identifiers stay exactly as they are.

### 5.5 The crosswalk

Every existing case gains a `tc_id` **attribute** (§6) holding its `TC-` identifier. The pack keeps
its own identifier as `legacy_id`. Both resolve; neither is lost.

| Legacy scheme | Legacy example | Derived `tc_id` | Rule |
|---|---|---|---|
| `SIT-<cat>-nnn` | `SIT-A-012` | `TC-L5-<module>-nnn` | Scope resolves to the **owning module of the chain's origin**, recorded in the case |
| `UAT-R<nn>-nnn` | `UAT-R06-004` | `TC-L7-R06-004` | Direct; sequence preserved |
| `UAT-R<nn>-P<nn>-nnn` | `UAT-R38-P05-002` | `TC-L7-P05-nnn` | Portal scope wins for portal scripts |
| `E2E-nn` | `E2E-07` | `TC-L6-J07-001` | Scope is the journey `J01`…`J18` from `TS-012` §1.1 |
| `PERF-NFR-nnn-nn` | `PERF-NFR-037-02` | `TC-L8-NFR-037-002` | Direct |
| `OFF-nnn` | `OFF-014` | `TC-L12-<app>-nnn` | Scope is the application under test |
| `SEC-nnn` | `SEC-021` | `TC-L9-<scope>-nnn` | Scope is the portal, role or object |
| **none** — `TS-013`, `TS-016`, `TS-018` | — | **Allocated on entry to the repository** | These packs' cases become addressable for the first time |

> **`TDS-10`.** The crosswalk is generated, held in the repository, and **regenerated rather than
> maintained**. A hand-maintained crosswalk goes stale, which is `TS-11` and `PGD-A1-03`.

---

## 6. The Case Specification

### 6.1 The eighteen attributes

29119-3:2021 §10 separates test design specification, test case specification and test procedure
specification. **They are held here as one record with attributes** (`QA-003-D-03`), because three
documents per case across ~1,700 cases is unmaintainable and produces exactly the drift between them
that the separation was meant to prevent.

| # | Attribute | Mandatory | Notes |
|:--:|---|:--:|---|
| 1 | `tc_id` | ✔ | Derived, §5.2 |
| 2 | `legacy_id` | where one exists | §5.5; never removed |
| 3 | `title` | ✔ | What is being proved, in one line, in business terms |
| 4 | `level` | ✔ | `L1`…`L13` |
| 5 | `scope` | ✔ | Module, portal, role or NFR |
| 6 | `requirements` | ✔ | ≥ 1 `FR-`, `SWR-`, `NFR-` or `BRU-`. **A case with no requirement is rejected** (§10 `TDS-Q1`) |
| 7 | `technique` | ✔ | From §4.2, by name |
| 8 | `risk_class` | ✔ | `RC-A`…`RC-D`, from the requirement's assessment |
| 9 | `verification_method` | ✔ | Inherited from the requirement (§3.2); a mismatch is a defect |
| 10 | `type` | ✔ | `positive` · **`negative`** · `boundary` · `abuse` · `exploratory` |
| 11 | `preconditions` | ✔ | System state, data, role account, environment |
| 12 | `data_requirement` | ✔ | **What the data must be like**, not the values — values are `QA-004`'s |
| 13 | `steps` | ✔ | Ordered, each with an expected result. In business language for L7 |
| 14 | `expected_result` | ✔ | Falsifiable. *"System works correctly"* is rejected |
| 15 | `automated` | ✔ | `yes` · `no` · `partial`, with the `QA-005` suite reference |
| 16 | `regression_core` | ✔ | `yes`/`no`. `yes` only grows (`LVP-09`) |
| 17 | `bilingual` | ✔ | Whether the case must pass in both languages (`TX-10`) |
| 18 | `owner` | ✔ | The role accountable for the case being right |

### 6.2 The three rules that make a case worth writing

| # | Rule |
|---|---|
| `TDS-11` | **A case proves a requirement, not a screen.** A case whose `requirements` list is empty is not a case. This is the rule that turns a scenario library into a derived set |
| `TDS-12` | **An expected result is falsifiable.** A reader must be able to look at the system and say the case failed. `RQ-001` `CK-04` applies to cases as it applies to requirements |
| `TDS-13` | **A case states what the data must be *like*, never the values.** *"A customer with two open orders, one past its SLA"* is a data requirement; *"customer 4471"* is a coupling to a dataset that will be refreshed |

### 6.3 UAT cases carry a further obligation

`TS-006` `UA-06` and `UA-15` already require it; recorded here because it is a derivation rule:

| # | Rule |
|---|---|
| `TDS-14` | **A UAT case is written in the executor's language, not the tester's.** A UAT script written in tester language is signed without being read — the signature is obtained, the defect is not found, and 150–250 agents discover it at the counter |
| `TDS-15` | **A UAT case names the `SP` procedure it performs**, so a failure can be diagnosed to the system, the procedure or the training. **Nine roles cannot satisfy this today** (`QA-002` §9.2) |

---

## 7. The Case Repository

### 7.1 Requirements on the repository

| # | Requirement | Why |
|---|---|---|
| `TDS-16` | **Every case is one record with the §6.1 attributes**, queryable by any of them | `CV-M5` is a join, not a document search |
| `TDS-17` | **Version-controlled**, with history per case | `GV-011` configuration management; a case's change history explains a coverage movement |
| `TDS-18` | **Linked bidirectionally to requirements** (`T-07`) and to defects | `RQ-004` §4 requires reciprocity |
| `TDS-19` | **Linked to the automated implementation** where one exists, so `automated: yes` is verifiable rather than asserted | `MTS-R8`'s ratio is otherwise self-reported |
| `TDS-20` | **Exportable as the `TS` pack format**, so the content estate stays readable by business users | The packs are the artefact business owners sign |
| `TDS-21` | **The `TS` packs remain the authored source for their cases.** The repository indexes and links them; it does not replace them | `CP-01` — one authority per artefact |

### 7.2 The structure

```text
08_Quality_Engineering_and_Test/
└── QA-003_artefacts/
    ├── cases/
    │   ├── L1/  L2/  L3/  L4/  L5/  L6/  L7/  L8/  L9/  L10/  L11/  L12/  L13/
    │   │   └── <SCOPE>/TC-<LEVEL>-<SCOPE>-<nnn>.yaml
    ├── crosswalk.yaml          # generated, §5.5
    ├── coverage.yaml           # generated, consumed by QA-011
    └── schema/case.schema.json # the §6.1 attributes, validated in CI
```

> **`TDS-22`.** A case file that fails `case.schema.json` **fails the build**. This is the same
> mechanism `BE-006` used for `component.yaml`: a claim a component makes about itself can be
> contradicted by CI. A case claiming `automated: yes` with no suite reference is contradicted the
> same way.

### 7.3 Tooling position

| Option | Assessment |
|---|---|
| A dedicated test-management product | Best querying; **but** it is a twelfth system, it holds the case set outside `GV-011` configuration control, and no budget line exists |
| **Files in the repository, schema-validated, indexed by a generator** | Version-controlled with the code, reviewable by pull request, free, and CI-checkable. **Chosen** — `QA-003-D-04` |
| A spreadsheet | The shadow-process outcome `TS-012` `EE-05` classifies as a scope gap. Rejected |

> **Revisit at the W4 gate.** If the case set exceeds ~3,000 records and query latency becomes a real
> constraint, a product is reconsidered with the file set as its import. Recorded so the decision is
> a decision and not an inheritance.

### 7.4 Review

| # | Rule |
|---|---|
| `TDS-23` | **A new `RC-A` case is reviewed by someone other than its author** before entering the repository |
| `TDS-24` | **A case that changed because a requirement changed carries the change reference** (`RQ-005`) |
| `TDS-25` | **A case deleted is archived, never removed.** Deletion history is how a coverage drop is explained |

---

## 8. Derivation Rules Per Class

### 8.1 The general procedure

| Step | Action | Produces |
|:--:|---|---|
| 1 | Take the requirement and its `verification_method` (§3) | The proof obligation |
| 2 | Assign its risk class from `QA-001` §5.2 — impact by the business owner, likelihood by engineering | `RC-A`…`RC-D` |
| 3 | Select the technique set from §4.3 and §4.4 | Named techniques |
| 4 | Derive **test conditions** — the things that must be true | Conditions |
| 5 | Derive **cases** from conditions by the technique's own coverage measure | Cases with `tc_id` |
| 6 | State the data requirement per case (`TDS-13`) | Input to `QA-004` |
| 7 | Assign level, automation intent and regression-core membership | Complete case |
| 8 | Pass the §10 quality checks | Repository entry |

### 8.2 The eight `RC-A` populations, and what each derives

`QA-001` §5.4 pre-assigns eight populations to `RC-A`. Their derivation is stated here so it is not
re-argued per module.

| Population | Technique | Cases produced | Sampling |
|---|---|---|:--:|
| **Financial and tax calculation paths** | Boundary values across every threshold and rate band + decision table + **L1 branch coverage** | One per band boundary, both sides; one per exemption path | **None** |
| **Statutory outputs** | Decision table over the output's field rules + `C` certification | One per statutory form per scenario class; **plus an `E8` acceptance** | **None** |
| **379 denied `role × portal` cells** | Decision table over `role × object × action`, **negative** | **379 negative cases minimum**, each proving the denial holds **through the API as well as the UI** | **None** — `SC-01` |
| **Class `H` hard rules** | Decision table + negative | One positive + **≥ 1 negative proving the rule blocks** per rule | **None** |
| **Residency-classified fields** | Equivalence partitioning over store × region + negative | One per field class per permitted store, plus a negative per forbidden store | **None** |
| **Offline conflict and sync paths** | State transition + conflict matrix | One per conflict type × resolution rule; **plus a field measurement** | **None** |
| **Custody and destruction chains** | State transition, **every invalid transition rejected** | One per chain step, plus a negative per bypass route | **None** |
| **`P0` requirements (~769)** | Per §4.4 by class | ≥ 1 per requirement — `CV-04` makes zero a gate failure | **None** |

### 8.3 The negative-case rule that dominates the estate

> **`05-04` §10 criterion 6 makes negative testing a condition of releasing a role**, and `05-04`
> §2's matrix has **456 cells: 77 granted, 379 denied** (`AUDIT-014` `X8`, exact). **`SC-01` forbids
> sampling the 379.**

That single rule produces **at least 379 cases before any positive testing**, repeated per wave as
roles are delivered, and it is the largest single derivation obligation in the category. `QA-007`
owns their content; this document owns the fact that they are derived, not sampled.

### 8.4 What does *not* derive from requirements

| Population | Derives from | Owner |
|---|---|---|
| Performance cases | Volumetrics and workload models | `QA-006` |
| Abuse cases | `SC-002`'s 97 threats and 32 abuse cases | `QA-007` |
| Accessibility cases | WCAG 2.2 success criteria and `UX-005`'s allocation | `QA-008` |
| Migration reconciliation cases | Control totals and mappings | `MG-004` ⛔ |
| Exploratory charters | Defect history and tester judgement | QA Lead |

---

## 9. Negative, Boundary and Abuse Cases

### 9.1 Why these are specified separately

Positive cases are written by default; the others are not, and every one of `QA-001`'s four quality
goals fails through a path a positive case never takes. **A test set that is 100% positive proves the
system works when used correctly, which is not the question.**

### 9.2 The negative-case obligation

| # | Rule |
|---|---|
| `TDS-26` | **Every class `H` hard rule has at least one negative case proving the rule blocks.** A rule tested only positively is a rule nobody has seen enforce |
| `TDS-27` | **Every denied `role × portal` cell in the wave's scope has a negative case**, and the case asserts the denial **through the API as well as the UI**. `TS-018` makes *"a denial that holds in the UI and not through the API"* an automatic `S1` |
| `TDS-28` | **Every state model has a case per invalid transition**, not only per valid one |
| `TDS-29` | **Every approval threshold has a case just over it and just under it**, and one **at** it |
| `TDS-30` | **Every mandatory evidence artefact has a bypass case** — a destruction certificate, a signature, a count, a three-way match. `G6-02` requires *zero* refurbished units released without a data destruction certificate; that is a negative assertion |

### 9.3 Abuse cases — the interface with `QA-007`

`SC-002` enumerates **97 threats and 32 abuse cases**. Their derivation belongs to `QA-007`; two
rules bind them here so the repository holds them consistently:

| # | Rule |
|---|---|
| `TDS-31` | **An abuse case is `type: abuse` in the repository** and traces to its `SC-002` threat identifier, not only to a requirement. A threat with no case is visible in `QA-011`'s report |
| `TDS-32` | **A pen-test finding with no matching `SC-002` threat adds a threat and a case** (`SC-009` `RC-4`) — the model was incomplete, and that is recorded rather than quietly patched |

### 9.4 Boundary cases in a bilingual, Bengali-first system

Recorded because these boundaries are specific to this system and are routinely missed:

| Boundary | Case obligation |
|---|---|
| **Bengali string expansion** | Every layout with a Bengali string at 130% of its English length (`UX-007`) — **`QAA-09`: no pack holds these** |
| **Lakh/crore grouping** | Amounts at 99,999 / 1,00,000 and 99,99,999 / 1,00,00,000 |
| **Bengali numerals** | Every numeric field rendered and parsed in both numeral sets |
| **Name transliteration** | `TS-002`'s deliberate near-duplicates — name matching must not produce a false negative |
| **Address depth to upazila** | Address parsing at every administrative level |
| **Date boundaries** | Bengali calendar display where used; the 15th for Mushak 9.1; month-end close |

---

## 10. Case Quality — the Eight Checks

> **`TDS-33`.** A case enters the repository only after passing all eight. **Six are machine-checked**
> by `case.schema.json` and the generator; two require a human.

| # | Check | Machine? | Rejects |
|:--:|---|:--:|---|
| `TDS-Q1` | `requirements` is non-empty and every identifier resolves | ✔ | A case proving nothing traceable |
| `TDS-Q2` | `technique` is one of §4.2's named techniques | ✔ | An anecdote |
| `TDS-Q3` | `expected_result` is present and contains no subjective term from `RQ-001` `CK-04`'s list | ✔ | *"System works correctly"* |
| `TDS-Q4` | `risk_class` matches the requirement's assessed class | ✔ | Silent depth reduction |
| `TDS-Q5` | `verification_method` matches the requirement's | ✔ | A drift between requirement and case |
| `TDS-Q6` | `automated: yes` resolves to a real suite reference | ✔ | A self-reported automation ratio |
| `TDS-Q7` | The case is **sufficient** for its technique's coverage measure — every partition, every boundary, every feasible rule column | ✖ human | An under-derived set that looks complete |
| `TDS-Q8` | An `RC-A` case has been reviewed by someone other than its author (`TDS-23`) | ✖ human | Single-author blind spots on the populations that matter most |

---

## 11. Maintenance

| # | Rule |
|---|---|
| `TDS-34` | **A requirement change re-derives its cases.** The change reference is recorded on every affected case (`TDS-24`) |
| `TDS-35` | **A requirement withdrawn archives its cases**, which is the only way a case leaves the regression core (`LVP-09`) |
| `TDS-36` | **A defect that reveals a missing case adds the case**, and the addition is recorded against the defect. This is how the set grows from experience without growing arbitrarily |
| `TDS-37` | **A recurring defect promotes its case to the permanent regression core** (`TS-013` `RS-03`, `TS-018` `TR-07`) |
| `TDS-38` | **The crosswalk and coverage files are regenerated, never edited** (`TDS-10`) |
| `TDS-39` | **The repository is re-counted at every wave gate** and the delta reported with the coverage triple (`CR-03`, `MTS-R1`) |

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-003-D-01` | Case identifier form | (a) continue six schemes; (b) one sequential space `TC-nnnn`; (c) **derivable `TC-<LEVEL>-<SCOPE>-<nnn>`** | **(c)** | A sequential space needs an allocator, and this repository has had **five identifier collisions** for want of one. A derivable identifier cannot collide | `TDS-09`; crosswalk §5.5; **zero existing cases renumbered** |
| `QA-003-D-02` | Whether to renumber the 620 existing cases | (a) renumber; (b) **crosswalk, both resolve** | **(b)** | `PG-05` and `RG-02`: identifiers are permanent. `BE-005` observed the same constraint | Every case carries `tc_id` and `legacy_id` |
| `QA-003-D-03` | 29119-3 §10's three specifications | (a) three documents per case; (b) **one record with attributes** | **(b)** | Three documents across ~1,700 cases is unmaintainable, and produces the drift the separation was meant to prevent | Declared departure, §2.1 |
| `QA-003-D-04` | Repository tooling | (a) test-management product; (b) **files + schema + generator, in the repository**; (c) spreadsheet | **(b)** | Version-controlled with the code, reviewable by PR, CI-checkable, inside `GV-011` control, and free | Revisited at the W4 gate if the set exceeds ~3,000 records |
| `QA-003-D-05` | Default `verification_method` | (a) require justification for every value; (b) **default `T`, justify others** | **(b)** | Makes the cheap answer the safe answer, so 3,347 rows get populated rather than deferred | `TDS-03`; ~11 analyst-days for the estate |
| `QA-003-D-06` | Structure-based techniques | (a) mandate MC/DC broadly; (b) **branch coverage on financial paths only, MC/DC where ≥ 4 conditions** | **(b)** | MC/DC across 331 components is disproportionate; on a money path with four conditions it is not | §4.2; `LVP-U2` |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is `verification_method` accepted as a 14th requirement attribute in `RQ-001` §3.10.3, and is the population resourced? | Enterprise Architecture with Business Analysts | **W1** | `T-07`; `CV-M5`, `CV-M6`, `CV-M7`; every derivation |
| `Q-02` | Who derives the 379 denial cases — `QA-007` alone, or `QA-007` with the module owners? | Security Lead with QA Lead | **W1** | §8.3; `G1-06`, `G1-09` |
| `Q-03` | Is the `QA-003_artefacts/` case repository accepted as the authoritative index, with the `TS` packs remaining the authored source? | Programme Content Lead with QA Lead | **W1** | `TDS-21`; `CP-01` boundary |
| `Q-04` | Who owns the Bengali expansion-layout cases that no pack holds? | Localisation Lead | **W1** | `QAA-09`; `G1-08`; `QA-002` `Q-05` |
| `Q-05` | Do `TS-013`, `TS-016` and `TS-018` receive allocated case identifiers, taking them from 0 addressable cases to countable? | QA Lead with Programme Content Lead | **W1** | §5.5; `CV-M5` completeness |

---

## 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The missing `verification_method` attribute is specified with values, rules and a costed population procedure | §3 — 6 values, 7 rules, ~11 analyst-days |
| `AC-02` | Every case-producing technique is named from 29119-4:2021, not invented | §4.2 |
| `AC-03` | A technique set is stated per risk class and per requirement class | §4.3, §4.4 — 4 classes, 13 requirement classes |
| `AC-04` | One derivable case identifier scheme exists and needs no allocator | §5.2; `TDS-09` |
| `AC-05` | No existing case identifier is changed | §5.4, §5.5 — 620 preserved |
| `AC-06` | Every case carries the 18 attributes, six of them machine-checked | §6.1, §10 |
| `AC-07` | The repository structure, tooling and CI validation are specified | §7 |
| `AC-08` | Derivation is stated for all eight `RC-A` populations | §8.2 — 8 of 8, none samplable |
| `AC-09` | The negative-case obligation is explicit and counted | §8.3, §9.2 — **≥ 379** before any positive testing |
| `AC-10` | Case quality is eight checks, six machine-enforced | §10 |

**Definition of done.** Complete when every criterion is met, `verification_method` is populated for
the W1 requirement slice, the repository holds the crosswalk for all 620 existing cases, and the
approver has signed. Approval carries the `PGD-A1-09` qualification.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` §3.10 | Requirements, attributes, well-formedness — and the 14th attribute this document requests |
| Upstream | `RQ-004` §4, §6.3 | Link `T-07`; the measured absence this document closes |
| Upstream | `RQ-009`, `05-05` | Business rules whose class `H` members require negative cases |
| Upstream | `QA-001` §4, §5 | Levels and risk classes |
| Upstream | `05-04` §2, §10 | The 456-cell matrix, 379 denials, and the release condition |
| Downstream | `QA-004` | Consumes every case's `data_requirement` |
| Downstream | `QA-005` | Implements every case marked `automated` |
| Downstream | `QA-006`, `QA-007`, `QA-008` | Derive their own cases into this repository under this scheme |
| Downstream | `QA-011` | Counts the numerator this document makes countable |
| Downstream | `QA-010` | Defects link to `tc_id` |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/` | The authored source for 620 cases, indexed not replaced |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` · `./QA-005_Test_Automation_Framework_Specification.md` ·
`./QA-007_Security_Test_Plan.md` · `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../01_Requirements_Engineering/RQ-001_Software_Requirements_Specification.md` ·
`../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` ·
`../01_Requirements_Engineering/RQ-009_Business_Rules_Specification.md` ·
`../05_Security_Privacy_and_Compliance/SC-002_Threat_Model_STRIDE_and_Abuse_Case_Register.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-005_Custom_Development_CD_Master_Register.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-006_Component_Build_Specification_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` ·
`../../project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External standards — editions verified 2026-08-18**
ISO/IEC/IEEE 29119-4:2021 (2nd ed.) · ISO/IEC/IEEE 29119-3:2021 (2nd ed.) §10 ·
ISO/IEC/IEEE 29148:2018 §5.2.8 · BS 7925-2

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering | Initial issue. Specifies the **missing `verification_method` attribute** — absent from 3,347 of 3,347 rows — with six values, seven rules and a costed population procedure of ~11 analyst-days; a technique catalogue taken from 29119-4:2021 and mapped to four risk classes and thirteen requirement classes; **one derivable case identifier `TC-<LEVEL>-<SCOPE>-<nnn>` requiring no allocator**, with a crosswalk that renumbers **none of the 620 existing cases**; an 18-attribute case specification with six machine-checked quality gates; the file-based, schema-validated repository; derivation rules for all eight `RC-A` populations; and the **≥ 379 negative cases** the denial matrix produces before any positive testing. Closes `RQA-18` and `QAA-03` | *Pending — `GV-002`* |

---

*`QA-003` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
