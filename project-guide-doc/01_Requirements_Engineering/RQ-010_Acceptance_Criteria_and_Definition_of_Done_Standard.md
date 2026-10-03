---
id: RQ-010
title: Acceptance Criteria & Definition of Done Standard
category: 01 — Requirements Engineering
code: RQ
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Lead Business Analyst / Requirements Manager, with the PMO for gate-level criteria
approver: ERP Design Authority, endorsed by the ERP Steering Committee for wave and programme levels
standards_basis: ISO/IEC/IEEE 29148:2018 §6.5.3 (validation) · ISO/IEC/IEEE 29119-3:2021 · ISO 9001:2015 §8.6 (release of products) · ISO/IEC 25010:2023
traces_to: PGD-000 RQ-010 row · module §17 (1,568 acceptance criteria) · 02-02 §8 (DoD-01…DoD-17) · 06-02 §4 (gate criteria G1–G9) · 06-02 §5 (programme success criteria)
depends_on: RQ-001 (verification methods) · RQ-004 (coverage measures) · RQ-008 (Definition of Ready) · GV-009 (wave gate handbook)
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumerated_on: 2026-08-18 02:15 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# RQ-010 — Acceptance Criteria & Definition of Done Standard

### Category 01 · Code `RQ` · ISO 9001:2015 §8.6 · ISO/IEC/IEEE 29148:2018 §6.5.3

---

> **The programme has 1,568 acceptance criteria, a 17-item module Definition of Done, 70 wave-gate
> criteria and a set of programme success criteria. What it does not have is an evidence
> standard** — so two modules can both be "done" to entirely different bars, and nobody
> can tell from the record.
>
> Three measurements, taken at 2026-08-18 02:15 (+06), show the shape of it:
>
> | Measured | Result |
> |---|---|
> | Acceptance criteria rows in module §17 across 79 specifications | **1,568** |
> | Wave gates carrying an **Evidence** column | **1 of 9** — Gate 1 only. Gates 2–9 list criteria with no evidence type |
> | Module specifications citing `02-02` **§7** as the source of the Definition of Done | **33** — §7 is the Module Interaction Matrix. The Definition of Done is **§8** |
>
> The last is a broken cross-reference in a third of the estate, pointing at the wrong section of
> the right document, in the sentence that defines what "done" means.

---

## 1. Purpose

"Done" is the most expensive word in a programme. It releases a payment milestone, closes a wave
gate, unlocks the next wave's funding and transfers risk from the builder to the operator. It has
to mean the same thing in month 4 and in month 36, in the module that everyone watches and the
module that nobody does.

This document makes it mean one thing: a Definition of Done at four levels — story, module, wave
and programme — where every criterion names the **evidence type** that satisfies it, the role that
produces it, and the role that accepts it. It is the exit gate to which `RQ-008`'s Definition of
Ready is the entrance.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **evidence standard** — the eight evidence types and what each must contain (§3) |
| 2 | **Definition of Done at four levels** — story, module, wave, programme (§4) |
| 3 | The **acceptance criteria standard** for module §17, and its relationship to story criteria (§5) |
| 4 | **Wave gate criteria** — the evidence column the eight later gates lack (§6) |
| 5 | **Conditional acceptance** — when "done with exceptions" is permitted, and what it costs (§7) |
| 6 | **Acceptance roles and signatures** — who may say done, at which level (§8) |
| 7 | **Rejection and re-submission** (§9) |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Definition of Ready | `RQ-008` §4.3 | Entry gate; deliberately in a different document (`SU-09`) |
| Given/When/Then criteria form for stories | `RQ-008` §4.2 | Form; this document governs evidence |
| The wave gate governance process, assessors and consequences of failure | `GV-009` | Governance; this document supplies the evidence standard it applies |
| Test strategy, levels, environments and automation | `QA-001`, `QA-002`, `QA-005` | How testing is done |
| Defect severity, triage and the thresholds that block a gate | `QA-010` | §6.4 states the interface |
| UAT participant selection and script design | `QA-009` | §8.2 states the interface |
| Contractual deliverable acceptance | `CO-003` | §8.4 states the interface |
| Benefit realisation | `BM-004` | A benefit is realised after done, not at it |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Development teams | The bar their work is measured against, known before they start |
| QA | The evidence they produce and the completeness they assert |
| Business owners and super-users | What they are signing, and what their signature commits them to |
| PMO | The gate evidence pack and its completeness check |
| Steering Committee | What a gate pass actually asserts |
| Implementation vendor | The acceptance standard against which milestones are paid (`CO-003`) |
| Auditors | The evidence trail behind every "done" |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | Conformance |
|---|---|---|
| ISO/IEC/IEEE 29148:2018 | §6.5.3 Requirements activities in validation | Acceptance confirms the requirement met the *need*, not only the specification (§8.2) |
| ISO/IEC/IEEE 29119-3:2021 | Test completion reporting | Evidence types `E-2` and `E-3` follow its completion-report content |
| **ISO 9001:2015 §8.6** | Release of products and services | *"Documented information shall include evidence of conformity with the acceptance criteria and traceability to the person authorising release."* §3 and §8 implement both halves |
| ISO 9001:2015 §8.7 | Control of nonconforming output | §7 conditional acceptance implements the nonconformity route |
| ISO/IEC 25010:2023 | Product quality model | Quality criteria are accepted against `RQ-006` measurement methods, not against opinion |

**Verified 2026-08-18.**

### 2.2 Source material relied on

| Source | Provides | Measured 02:15 (+06) |
|---|---|---|
| `../../1000fix_ERP_Module/03_Modules/*/[MP]*.md` §17 | Module acceptance criteria | **1,568 `AC-nn` rows across 79 specifications** |
| `.../02_Architecture/02-02` **§8** | Module Definition-of-Done | **`DoD-01` … `DoD-17`** |
| `.../06_Delivery_and_Implementation/06-02` §4 | Wave gate acceptance criteria | **70 criteria across `G1`–`G9`; only `G1` carries an Evidence column** |
| `.../06-02` §5 | Programme-level success criteria | — |
| `.../06-02` §6 | Benefit tracking discipline | — |
| `_MODULE_TEMPLATE` §17 | *"Definition of done: all criteria in `02_Architecture/02-02` §7 plus the module-specific criteria above."* | **Wrong section — 33 files affected** |
| `RQ-001` §3.19 | The four verification methods that determine evidence type | — |
| `RQ-008` §4.2, §4.3 | Story criteria form and Definition of Ready | — |
| `../../project_content/13_Test_and_Acceptance_Content/TS-006`…`TS-011`, `TS-018` | UAT script packs; defect taxonomy and sign-off forms | 6 + 1 |

### 2.3 Findings this document addresses

| Finding | Source | Treatment |
|---|---|---|
| `PGD-000` `RQ-010` row | Register | *"Module §17 acceptance criteria exist per module but there is no common evidence standard, so two modules can both be 'done' to different bars."* Confirmed | §3, §5 |
| **`RQA-30`** *(raised here)* | This document | **Eight of nine wave gates carry no evidence column.** Gate 1 states an evidence type per criterion; Gates 2–9 list criteria only | §6.2 |
| **`RQA-31`** *(raised here)* | This document | **33 module specifications cite `02-02` §7 as the Definition of Done**; §7 is the Module Interaction Matrix and §8 is the Definition of Done. 13 cite §8 correctly | §4.3 |
| `TS` findings | `AUDIT-014` | Four test packs cannot be executed — no accessibility reviewer (`TS-016`), no role accounts (`TS-017`), no staged stock (`TS-008`), no field logistics (`TS-015`). §6.5 makes evidence *producibility* a gate-entry check rather than a gate-day discovery | Partial — `QA-009` resources them |
| `H2-10` | Module template §7.2 | *"An absolute target against an unmeasured baseline cannot be assessed as met or missed."* `AC-06` in §5.2 applies the same test to acceptance criteria | Closed for criteria |

---

# 3. The Evidence Standard

## 3.1 Why evidence type is the whole standard

A criterion without a stated evidence type is satisfied by whatever the person asserting it
considers sufficient. That is how two modules both reach "done" at different bars — not through
dishonesty, but because *"business rules enforced"* can reasonably mean a code review to one
person and a negative test through the API to another.

**Rule `DD-01`.** Every acceptance criterion, at every level, names exactly one evidence type from
§3.2 and the role that produces it.

## 3.2 The eight evidence types

| Type | Evidence | Contains | Produced by | Sufficient alone for |
|:--:|---|---|---|---|
| **`E-1`** | **Automated test result** | Test case ID, run ID, environment, commit SHA, pass/fail, execution timestamp | CI | Any criterion verified by Test where the case is automated |
| **`E-2`** | **Manual test record** | Case ID, tester, environment, data set, steps executed, actual vs expected, timestamp | QA | Test-verified criteria not economically automatable |
| **`E-3`** | **Test completion report** | Scope, cases planned/executed/passed/failed, defects by severity, residual risk, sign-off | QA Lead | Module and wave level only |
| **`E-4`** | **Witnessed demonstration** | Script, date, named witness, system state before and after, recording or signed record | Business owner as witness | Demonstration-verified criteria |
| **`E-5`** | **Inspection record** | Artefact and its version, checklist applied, reviewer, findings, disposition | Reviewer | Inspection-verified criteria |
| **`E-6`** | **Analysis record** | Model or reasoning applied, inputs, conclusion, reviewer | Architect | Analysis-verified criteria |
| **`E-7`** | **Signed acceptance** | Named role, date, scope accepted, exceptions listed, signature | Business owner | **Never alone** — always accompanies `E-1`…`E-6` |
| **`E-8`** | **Measured production observation** | Metric, instrument, sample window, value, threshold | SRE / Analytics | Criteria only provable in live operation |

**Rule `DD-02` — the method determines the type.** A criterion's evidence type follows from its
requirement's `verification_method` (`RQ-001` §3.19): Test → `E-1` or `E-2`; Demonstration →
`E-4`; Inspection → `E-5`; Analysis → `E-6`. A mismatch is a defect in one or the other.

**Rule `DD-03` — `E-7` never stands alone.** A signature asserts that evidence was reviewed and
found sufficient. A signature with no underlying evidence asserts only that somebody signed.

**Rule `DD-04` — evidence is dated and attributable.** Every artefact carries its production
timestamp and the role that produced it (`PG-M11`). Undated evidence cannot be shown to relate to
the version being accepted.

**Rule `DD-05` — `E-8` cannot gate a first release.** A criterion provable only in production
(*"auto-match ≥ 90%"*, *"disputes under 3%"*) is accepted at gate on its **instrumentation** —
that the measure exists, is collecting, and has a threshold and an owner — and is confirmed at the
post-implementation review (`RL-005`). Otherwise every wave gate waits for a quarter of production
data.

## 3.3 Evidence retention

| # | Rule |
|---|---|
| `DD-06` | Gate evidence is retained for the programme's life plus the statutory retention period in `LG-009` |
| `DD-07` | Evidence containing personal data is masked or references a masked dataset. `NFR-071` forbids unmasked data in non-production, and a UAT evidence pack is an artefact, not an environment |
| `DD-08` | Evidence is held where an auditor can reach it without asking the team that produced it |

---

# 4. Definition of Done — Four Levels

## 4.1 The levels

| Level | Unit | Accepted by | Frequency | Where defined |
|---|---|---|---|---|
| **Story** | A user story | Product owner / business owner | Per sprint | §4.2 |
| **Module** | A module or portal | Business owner + Design Authority | Per module, at its wave | §4.3 — `02-02` §8 `DoD-01`…`DoD-17` |
| **Wave** | A delivery wave | Steering Committee, on PMO evidence pack | 9 times | §4.4, `06-02` §4 |
| **Programme** | The whole platform | Board | Once | §4.5, `06-02` §5 |

**Rule `DD-09` — the levels nest.** A wave is not done until every module in it is done; a module
is not done until every story in it is done. A gate cannot be passed by aggregating incomplete
lower levels, which is the failure mode a percentage-complete report enables.

## 4.2 Story-level Definition of Done

| # | Criterion | Evidence | Produced by |
|---|---|---|---|
| `SD-01` | Every acceptance criterion passes | `E-1` or `E-2` | QA |
| `SD-02` | The negative-case criterion required by `RQ-008` `AC-06` passes | `E-1` or `E-2` | QA |
| `SD-03` | Code reviewed and merged per `BE-003` | `E-5` | Reviewer |
| `SD-04` | Unit tests written and passing; coverage thresholds met (`NFR-090`) | `E-1` | CI |
| `SD-05` | Every business rule the story enforces is negative-tested through **both UI and API** (`DoD-04`, `BR-24`) | `E-1` | QA |
| `SD-06` | Bengali strings complete for everything the story adds (`NFR-016`) | `E-1` translation coverage | Content Lead |
| `SD-07` | Applicable `NFR` targets met, measured by their `RQ-006` §3.5 instrument | `E-1` or `E-8` | QA / SRE |
| `SD-08` | Domain events emitted through the outbox and registered (`SWR-035`) | `E-1` | QA |
| `SD-09` | Trace links `T-04`, `T-07` populated reciprocally | `E-5` | BA |
| `SD-10` | No open defect at severity 1 or 2 against the story | `E-3` | QA Lead |
| `SD-11` | Business owner has accepted it | `E-7` | Business owner |

## 4.3 Module-level Definition of Done

**`02-02` §8 `DoD-01` … `DoD-17` is retained in full and is not restated here** — it is a good
list and it belongs to the module repository. This document adds the **evidence type per item**,
which is what was missing.

| `DoD` | Criterion *(abbreviated — `02-02` §8 governs the wording)* | Evidence | Produced by | Accepted by |
|---|---|:--:|---|---|
| `DoD-01` | Registered before specification, per `RG-01` | `E-5` | PMO | Design Authority |
| `DoD-02` | All P0 and P1 requirements implemented and demonstrated | `E-4` + `E-1` | QA | Business owner |
| `DoD-03` | Unit coverage ≥ 80%; 100% on financial and tax calculations | `E-1` | CI | QA Lead |
| `DoD-04` | Business rules enforced at the model layer, negative-tested through UI **and** API | `E-1` | QA | Business owner |
| `DoD-05` | Domain events published through the outbox and registered in the catalogue | `E-1` + `E-5` | QA + Integration Architect | Design Authority |
| `DoD-06` | APIs documented in OpenAPI 3.1 and published | `E-5` | Integration Architect | Design Authority |
| `DoD-07` | Access control, record rules and field permissions negative-tested for every applicable role | `E-1` | QA | CISO |
| `DoD-08` | Bengali translation complete for all user-facing strings | `E-1` | Content Lead | Change Lead |
| `DoD-09` | KPIs instrumented with allocated `KPI-nnn` and visible in `M25` | `E-8` | Analytics | Benefit owner |
| `DoD-10` | Data migration mapping defined and dry-run executed where legacy data exists | `E-3` | Migration Lead | Business owner |
| `DoD-11` | Operational runbook written | `E-5` | Platform Lead | Service Manager |
| `DoD-12` | Training material produced in Bengali and English for every affected role | `E-5` | L&D | Change Lead |
| `DoD-13` | UAT executed and signed by named business super-users | `E-3` + `E-7` | QA Lead + super-users | Business owner |
| `DoD-14` | Performance tested against applicable NFRs | `E-1` | QA | Solution Architect |
| `DoD-15` | Security review completed, zero open high or critical findings | `E-5` + `E-3` | Security reviewer | CISO |
| `DoD-16` | Rollback plan documented and rehearsed | `E-4` | Platform Lead | Release Manager |
| `DoD-17` | Regulatory citations verified current with a verified-on date | `E-5` | Compliance | DPO / CFO |

> **Correction — `RQA-31`.** `_MODULE_TEMPLATE` §17 states *"all criteria in `02_Architecture/02-02`
> **§7**"*. `02-02` §7 is the **Module Interaction Matrix**; the Definition of Done is **§8**.
> Measured: **33** module specifications carry the §7 citation, **13** carry §8 correctly. The
> template and the 33 files require correction. This is a `D-4` stale-link defect (`RQ-004` §8)
> and is referred to the module repository owner, since acting on another repository's working
> tree is outside this repository's authority (`PG-M8`, precedent `PGD-A1-10`).

**Rule `DD-10`.** `DoD-09` is the only item that may be satisfied by `E-8` *instrumentation
present* rather than by a measured value, per `DD-05`.

**Rule `DD-11`.** `DoD-15`'s *"zero open high or critical"* means zero at the **time of
acceptance**, evidenced, not zero at the time of the last scan.

## 4.4 Wave-level Definition of Done

A wave is done when all four hold:

| # | Criterion | Evidence |
|---|---|---|
| `WD-01` | Every module allocated to the wave meets §4.3 in full, or holds a recorded conditional acceptance under §7 | `E-3` roll-up + `E-7` per module |
| `WD-02` | Every wave gate criterion in `06-02` §4 for that gate is met, with the evidence type in §6.3 | Per criterion |
| `WD-03` | `RQ-004` coverage measures meet their gate thresholds — in particular `CV-M6`, **P0 test coverage, which is pass/fail and not a percentage** | `E-3` |
| `WD-04` | Defect thresholds in `QA-010` are met | `E-3` |

## 4.5 Programme-level Definition of Done

Per `06-02` §5, with evidence added:

| # | Criterion | Evidence |
|---|---|---|
| `PD-01` | All nine wave gates passed, each with a retained evidence pack | `E-3` × 9 |
| `PD-02` | Every `P0` requirement in the `RQ-001` baseline is at `Accepted` | `E-3` from `RQ-004` `CV-M8` |
| `PD-03` | The legacy estate is decommissioned per `RL-006`, with proof each system is off | `E-5` |
| `PD-04` | Benefit measurement is operating against measured baselines (`BM-002`, `BM-004`) | `E-8` |
| `PD-05` | Statutory obligations are discharged and evidenced (`SC-008`, `RR-005`) | `E-5` |
| `PD-06` | Service operations has accepted the platform into support (`SV-005`) | `E-7` |

---

# 5. Acceptance Criteria Standard

## 5.1 Two criteria populations, two purposes

| Population | Count | Level | Purpose | Form |
|---|---:|---|---|---|
| Story criteria | To be produced by `RQ-008` conversion | Story | Is this story done? | Given/When/Then (`RQ-008` §4.2) |
| **Module §17 criteria** | **1,568** | Module | Is this module fit for its business purpose? | This section |

**Rule `DD-12`.** They are not duplicates. A module criterion asserts something about the module as
a whole that no single story can — *"the branch can operate a full day using only this module"*.
A module criterion that restates a story criterion is deleted.

## 5.2 The module criterion standard

| # | Rule |
|---|---|
| `AC-01` | Each criterion states a single observable outcome |
| `AC-02` | Each names exactly one evidence type from §3.2 |
| `AC-03` | Each names the role that accepts it |
| `AC-04` | Each is falsifiable — a competent assessor can determine pass or fail without negotiation |
| `AC-05` | Each is bounded numerically where it asserts a quantity |
| `AC-06` | **A criterion asserting improvement against a baseline may not be used unless that baseline is measured.** `06-02` §6 and module template §7.2 both already say this; it is repeated because 44 of 95 KPI baselines are absent (`AUDIT-015`) |
| `AC-07` | Each traces to the requirements it covers |
| `AC-08` | Business-language, not implementation-language. A business owner signs it |

## 5.3 What is not a module acceptance criterion

| Not a criterion | It is | Belongs to |
|---|---|---|
| *"Code is clean and well structured"* | Unfalsifiable | Nothing |
| *"The module is complete"* | Circular | Nothing |
| *"Unit test coverage ≥ 80%"* | A Definition-of-Done item | `DoD-03` |
| *"Response under 400 ms"* | A quality requirement | `NFR-002` |
| *"Zero NBR exceptions at Gate 3"* | A wave gate criterion | `06-02` §4, `G3` |
| *"The invoice shows the Company's BIN"* | A story criterion | `RQ-008` |

**Rule `DD-13`.** The 1,568 existing criteria are assessed against §5.2 and §5.3 during conversion.
Criteria that are Definition-of-Done items, quality requirements or gate criteria are **moved to
their correct home, not deleted**. Deleting a criterion because it is in the wrong place removes a
control.

---

# 6. Wave Gate Criteria

## 6.1 What a gate asserts

A wave gate assesses six readiness dimensions. `06-02` §4 provides the criteria; `GV-009` owns the
governance; this document supplies the evidence standard.

| Dimension | Question | Primary evidence |
|---|---|---|
| Functional | Does it do what was specified? | `E-1`, `E-4` |
| Technical | Will it survive production? | `E-1`, `E-3`, `E-6` |
| Data | Is the data correct and reconciled? | `E-3` reconciliation |
| Operational | Can it be run and supported? | `E-4`, `E-5` |
| People | Can the users use it? | `E-3` UAT, `E-5` training |
| Commercial | Is the deliverable contractually acceptable? | `E-7`, `CO-003` |

## 6.2 Finding `RQA-30` — the missing evidence column

`06-02` §4 contains **70 gate criteria across nine gates**. Gate 1's table is
`| # | Criterion | Evidence |` — three columns, with an evidence type per criterion:
*demonstration + transaction log*, *timed observation, 20 samples*, *signed reconciliation*,
*security test report*, *translation coverage report*, *signed UAT record*.

**Gates 2 through 9 use `| # | Criterion |` — two columns.** Fifty-eight criteria across eight
gates, each stating what must be true and none stating what proves it.

**Consequence.** Gate 1's criteria are assessable; Gates 2–9's are negotiable. `G2-02`
*"24-hour offline operation demonstrated with zero data loss"* is a strong criterion, and whether
it is met by one scripted device test or by fifty technicians working a real day offline is worth
a wave of schedule.

**Rule `DD-14`.** Every gate criterion at every gate carries an evidence type from §3.2, a sample
where the evidence is observational, and the role that produces it. Gate 1's three-column form is
the standard; the other eight gates are brought to it.

## 6.3 The gate criterion record

```yaml
criterion_id:  G2-02
gate:          Gate 2 — Field Operations (Month 8)
dimension:     Functional
statement:     24-hour offline operation demonstrated with zero data loss
evidence_type: E-4                       # witnessed demonstration
evidence_spec: >                         # DD-14: the sample, not just the type
  Scripted 24-hour offline scenario executed on 10 devices across 3 branch
  clusters (C1, C3, C5 per SP-002 §4.3), including forced termination, battery
  exhaustion and mid-sync connectivity loss; queued transaction count reconciled
  before and after synchronisation.
produced_by:   QA Lead
witnessed_by:  Ops Director
accepted_by:   Steering Committee
requirements:  [SWR-030, SWR-031, SWR-032, NFR-047, NFR-037]
threshold:     Zero lost transactions; zero double-applied transactions
```

## 6.4 Interface with defect management

**Rule `DD-15`.** `QA-010` sets the defect thresholds that block a gate. This document requires
only that the threshold **exists and is stated before the gate**, not decided at it. A threshold
agreed on gate day is agreed under the pressure of a gate day.

## 6.5 Evidence producibility — checked before the gate, not at it

Audit `AUDIT-014` found four test packs that **cannot be executed**: `TS-016` has no accessibility
reviewer, `TS-017` has no role accounts, `TS-008` has no staged stock, `TS-015` has no field
logistics.

**Rule `DD-16`.** At **gate minus 8 weeks**, the PMO confirms for every criterion in the coming
gate that its evidence is *producible*: the environment exists, the data exists, the reviewer
exists, the accounts exist, the equipment exists. A criterion whose evidence cannot be produced is
escalated then, when it can still be resourced — not discovered on gate day, when the only
available outcome is a conditional pass.

---

# 7. Conditional Acceptance

## 7.1 When it is permitted

`06-02` §4 already states that *"all criteria must be met; partial passes are recorded as
conditional with a dated remediation plan."* This section makes that operable.

**Rule `DD-17`.** Conditional acceptance is permitted only when **all four** hold:

| # | Condition |
|---|---|
| `CA-1` | The unmet criterion is **not** `P0`, **not** statutory, and **not** safety-related |
| `CA-2` | A dated remediation plan exists with a named owner and a target inside the next wave |
| `CA-3` | The operational workaround is documented, communicated and rehearsed |
| `CA-4` | The accepting authority for the level records that they accepted it conditionally, and why |

**Rule `DD-18` — the absolute exclusions.** A criterion that is `P0`, statutory or safety-related
**may not** be conditionally accepted. There is no remediation plan for having gone live without a
lawful basis, and there is no workaround for an uncertified technician on a certification-required
job.

**Rule `DD-19` — the ledger.** Open conditional acceptances are carried in a published register and
reported at every subsequent gate until closed. **A conditional acceptance that survives two gates
is escalated to the Steering Committee as a scope or quality decision**, because at that point it
has become the permanent state and should be recorded as one.

## 7.2 What conditional acceptance costs

| Consequence | Rule |
|---|---|
| The next wave inherits the remediation as scheduled work, not as slack | `GV-004` |
| Any benefit dependent on the criterion is **not** claimed until it closes | `BM-004`, `06-02` §6 |
| Any contractual milestone dependent on it is **not** released until it closes | `CO-003` |
| The conditional item appears in the next gate's evidence pack | `DD-19` |

---

# 8. Acceptance Roles

## 8.1 Who may say done

| Level | Proposes | Verifies | **Accepts** | Vetoes |
|---|---|---|---|---|
| Story | Developer | QA | **Product owner / business owner** | — |
| Module | Delivery Lead | QA Lead | **Business owner + Design Authority** | CISO on `DoD-15`; DPO on `DoD-17` |
| Wave | PMO | QA Lead + Design Authority | **Steering Committee** | DPO/CISO on any statutory criterion |
| Programme | Programme Director | Independent assurance (`GV-010`) | **Board** | — |

**Rule `DD-20` — the acceptor is never the producer.** The role accepting an item never produced
its evidence. `PGD-A1-13` recorded an audit that missed its own arithmetic error twice; the
lesson generalises.

**Rule `DD-21` — acceptance is by role, never by name.** Roles persist across a 36-month
programme; people do not.

## 8.2 UAT and validation

**Rule `DD-22`.** Business acceptance asserts that the requirement **met the need**, not that it
matched the specification. 29148 §6.5.3 distinguishes validation from verification, and a
requirement can be built exactly as written and still be wrong. Where UAT finds that, a change
request is raised (`RQ-005` §6) — it is not absorbed silently.

`QA-009` owns participant selection, scripting and defect triage authority. `TS-006`…`TS-011`
provide six script packs; `TS-018` provides the defect taxonomy and sign-off forms.

## 8.3 The current governance position

The Steering Committee's terms of reference do not exist (`GV-002`, `PGD-A1-09`). **No wave gate
can currently be accepted by the authority §8.1 names.** Until `GV-002` issues, gate evidence packs
are assembled and held; they are not signed. This is stated rather than worked around, because a
gate signed by an unconstituted body is a gate that can be challenged later, at the worst moment.

## 8.4 Interface with contractual acceptance

**Rule `DD-23`.** `CO-003`'s deliverable acceptance schedule shall reference this standard rather
than define a parallel one. Two acceptance definitions — one technical, one contractual — is how
"done" becomes negotiable per invoice, which is the outcome `CO-003`'s register row exists to
prevent.

---

# 9. Rejection and Re-submission

**Rule `DD-24`.** Rejection states the criterion not met, the evidence that was insufficient, and
what would be sufficient. *"Not accepted"* with no criterion cited is not a rejection; it is an
opinion, and it cannot be remediated.

**Rule `DD-25`.** Re-submission re-runs only the criteria affected by the change, **plus the
regression set for the component** (`TS-013`). Re-running everything is expensive; re-running only
the failed criterion is how a fix breaks something adjacent.

**Rule `DD-26`.** Every rejection is recorded with its date and cause. Rejection cause distribution
is the input to `RM-M9` rework rate (`RQ-005` §10.2) and is the strongest available signal that
Definition of Ready is being applied too loosely.

---

# 10. Decisions Recorded

| # | Decision | Options | Chosen | Rationale |
|---|---|---|---|---|
| D-01 | Whether to restate `02-02` §8 `DoD-01`–`DoD-17` | (a) Restate with evidence; (b) reference and add the evidence column | **(b)** | `PG-02` and the cross-repository rule. The list is good and belongs to the module repository; what was missing was evidence |
| D-02 | Number of DoD levels | (a) Story and wave; (b) four — story, module, wave, programme | **(b)** | A module is the unit business owners accept and the unit `02-02` §8 already governs. Omitting it would orphan a working control |
| D-03 | Whether an evidence type is mandatory per criterion | (a) Recommended; (b) mandatory — `DD-01` | **(b)** | Without it, "done" means whatever the asserter thinks. That is the finding this document exists to close |
| D-04 | Criteria only provable in production | (a) Block the gate; (b) accept on instrumentation, confirm at PIR | **(b)**, `DD-05` | Otherwise every gate waits for a quarter of production data |
| D-05 | Conditional acceptance | (a) Forbid; (b) permit under four conditions with absolute exclusions | **(b)**, `DD-17`, `DD-18` | Forbidding it produces dishonest full passes. Bounding it keeps it visible |
| D-06 | What happens to misplaced module criteria | (a) Delete; (b) move to their correct home | **(b)**, `DD-13` | Deleting a misplaced criterion removes a control |
| D-07 | Whether the acceptor may have produced the evidence | (a) Permitted where resource is tight; (b) never — `DD-20` | **(b)** | `PGD-A1-13`: a function checking its own work missed the same error twice |
| D-08 | Gate evidence producibility | (a) Assessed at the gate; (b) confirmed at gate minus 8 weeks | **(b)**, `DD-16` | Four test packs are already known to be unexecutable. Discovering that on gate day leaves only a conditional pass |

---

# 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | Who adds the evidence column to Gates 2–9 in `06-02` §4 — this repository or the module repository? | PMO / Enterprise Architecture | W1 | `DD-14`; the first gate that is not Gate 1 |
| Q-02 | When are the 33 `02-02` §7 citations corrected to §8? | Enterprise Architecture | W1 | `RQA-31`; the meaning of "done" in a third of the estate |
| Q-03 | Are the 1,568 module criteria assessed against §5.2 by module authors or centrally? | Lead BA | W1 | `DD-13` |
| Q-04 | Which defect thresholds block a gate, and are they agreed before Gate 1? | QA Lead (`QA-010`) | W1 | `DD-15`, `WD-04` |
| Q-05 | Who resources the four unexecutable test packs, and by when? | QA Lead / Programme Director | W1 | `DD-16`; `TS-008`, `TS-015`, `TS-016`, `TS-017` |
| Q-06 | Will `CO-003` reference this standard, or is a separate contractual definition already drafted? | Commercial Manager | W1 | `DD-23`; whether "done" stays single-valued |
| Q-07 | Who signs gates while `GV-002` does not exist? | CTO | **Now** | Every gate; `PGD-A1-09` |

---

# 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Eight evidence types defined, each with required contents and a producing role | §3.2 |
| AC-02 | Evidence type is mandatory per criterion and derives from the verification method | `DD-01`, `DD-02` |
| AC-03 | Four DoD levels defined, nesting stated | §4.1, `DD-09` |
| AC-04 | `02-02` §8's 17 items are referenced, not restated, and each is given an evidence type | §4.3 |
| AC-05 | The `02-02` §7/§8 citation defect is measured and referred | `RQA-31` |
| AC-06 | The missing gate evidence column is measured and a record format supplied | §6.2, §6.3 |
| AC-07 | Conditional acceptance is bounded with absolute exclusions and a visibility ledger | §7, `DD-17`–`DD-19` |
| AC-08 | Acceptance roles are separated from evidence producers | §8.1, `DD-20` |
| AC-09 | Evidence producibility is checked 8 weeks before a gate | `DD-16` |
| AC-10 | The governance circularity is stated rather than worked around | §8.3 |

---

# 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` §3.19 | Verification methods determining evidence type |
| Upstream | `RQ-008` §4.3 | Definition of Ready — the entry gate this is the exit gate to |
| Upstream | `02-02` §8 | Module Definition-of-Done, referenced and given evidence |
| Upstream | `06-02` §4, §5 | Wave gate and programme success criteria |
| Lateral | `RQ-004` | Coverage measures `CV-M6`, `CV-M8` used at `WD-03` |
| Lateral | `RQ-009` §8 | Rule test obligations feeding `SD-05`, `DoD-04` |
| Downstream | `GV-009` | Wave gate handbook applying this evidence standard |
| Downstream | `QA-001`, `QA-009`, `QA-010`, `QA-011` | Test strategy, UAT, defect gates and coverage reporting |
| Downstream | `CO-003` | Contractual acceptance referencing this standard (`DD-23`) |
| Downstream | `RL-003` | Go-live readiness assessment |
| Downstream | `RL-005` | Post-implementation review confirming `E-8` criteria |
| Downstream | `BM-004` | Benefit claims gated on criteria closing |

---

# 14. References

**Within this repository**
[`RQ-001`](RQ-001_Software_Requirements_Specification.md) ·
[`RQ-004`](RQ-004_Requirements_Traceability_Matrix.md) ·
[`RQ-005`](RQ-005_Requirements_Management_Plan.md) ·
[`RQ-006`](RQ-006_Non_Functional_Requirements_Specification.md) ·
[`RQ-008`](RQ-008_Use_Case_and_User_Story_Specification.md) ·
[`RQ-009`](RQ-009_Business_Rules_Specification.md) ·
[`../PGD-000_Master_Register_of_Project_Guiding_Documents.md`](../PGD-000_Master_Register_of_Project_Guiding_Documents.md)

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-02_Module_Catalogue_Master_Register.md` **§8** ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4, §5, §6 ·
`../../1000fix_ERP_Module/03_Modules/*/[MP]*.md` §17 ·
`../../1000fix_ERP_Module/03_Modules/_MODULE_TEMPLATE.md` §17 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-006`…`TS-011`, `TS-013`, `TS-018`

**External**

| Reference | Verified on |
|---|---|
| ISO 9001:2015 §8.6 (release of products and services), §8.7 (nonconforming output) | 2026-08-18 |
| ISO/IEC/IEEE 29148:2018 §6.5.3 (validation) | 2026-08-18 |
| ISO/IEC/IEEE 29119-3:2021 (test completion reporting) | 2026-08-18 |
| ISO/IEC 25010:2023 | 2026-08-18 |

---

# 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Eight evidence types; DoD at four levels; `02-02` §8 referenced with an evidence type per item; findings `RQA-30` (8 of 9 gates lack an evidence column) and `RQA-31` (33 files cite the wrong DoD section) raised; conditional acceptance bounded with absolute exclusions | *Pending — `GV-002`* |

---

*`RQ-010` · Category 01 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
