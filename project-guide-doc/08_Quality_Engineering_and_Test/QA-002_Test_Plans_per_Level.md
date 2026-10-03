---
id: QA-002
title: Test Plans per Level (Unit, Integration, System, End-to-End, UAT)
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead
approver: Head of Quality Engineering with the Programme Manager
standards_basis: >
  ISO/IEC/IEEE 29119-3:2021 §8 (Test Plan, clauses 8.1–8.20) ·
  ISO/IEC/IEEE 29119-2:2021 (test management processes) · PMBOK 7 Delivery performance domain
traces_to: >
  PGD-000 QA-002 · audit AUDIT-014 TS-02 (nine files consumed a wave before they exist) ·
  AUDIT-014 TS-06 · AUDIT-014 TS-07 · GV-009 EN-03 (a gate's test packs must exist and be executable) ·
  06-02 §4 (70 gate criteria) · 06-01 §3, §4, §5
depends_on: QA-001 (levels, risk model, entry/exit, capacity) · QA-003 (cases) · QA-004 (data) · GV-009 (gates)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-002 — Test Plans per Level

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-3:2021 §8

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-002` exists in `PGD-000` Category 08, status ⛔ `P0` `W1`.
> 2. **`PG-03` Count, do not consult.** Wave scopes, criteria counts and pack sizes counted at
>    **2026-08-18 22:01 (+06)** from `06-01` §3, `06-02` §4 and the 18 `TS` packs.
> 3. **`PG-06` Cite standards.** §2.1 maps every one of 29119-3:2021 §8's twenty clauses.
> 4. **`PG-M4` Verify citations.** Standard editions inherited from `QA-001` §18, verified 2026-08-18.

---

## 1. Purpose

`QA-001` says **which levels exist and what they must satisfy**. This document says **when each one
runs, who runs it, on what, with what, and what it delivers** — one plan per level, scheduled against
the nine waves.

It exists because of a specific, counted failure. `AUDIT-014` `TS-02` found that **nine of eighteen
test packs are consumed a wave before they exist, and seven of those nine are consumed at gate
`G1`** — the gate with 12 of the 70 criteria, at Month 4. `GV-009` then made the problem a gate entry
criterion: `EN-03` requires that *"every test pack the gate depends on exists and is executable"*,
checked at T−6 weeks. **Nothing between the two documents schedules the packs.** This one does.

> **The distinction 29119-3:2021 draws, and why it matters here.** §7 is the *organizational test
> strategy* — stable, programme-wide, and it is `QA-001`. §8 is the *test plan* — scoped, scheduled,
> resourced, and revised per wave. A programme that writes one document for both ends up revising its
> strategy every wave, which means it has no strategy.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The **plan architecture** — one master plan, thirteen level plans, nine wave instances (§3) |
| 2 | **The pack-to-gate schedule** — every pack, its earliest consuming criterion, and its corrected due date (§4) |
| 3 | **Level plan `LP-1`** — unit (§5) |
| 4 | **Level plan `LP-2`** — integration, contract and event, planned as one (§6) |
| 5 | **Level plan `LP-3`** — system integration testing (§7) |
| 6 | **Level plan `LP-4`** — end-to-end (§8) |
| 7 | **Level plan `LP-5`** — user acceptance (§9) |
| 8 | **Level plan `LP-6`** — the non-functional levels, which delegate to `QA-006`…`QA-008` (§10) |
| 9 | **The wave test calendar** — what each of W1–W9 tests, and the T−6 to T+2 window (§11) |
| 10 | **Deliverables, staffing and dependencies per plan**, including what each is blocked on (§12) |
| 11 | **Plan revision and re-baselining** (§13) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The level definitions, entry/exit criteria, risk model | `QA-001` | Consumed here, not restated |
| Case derivation technique, the case repository | `QA-003` | A plan schedules cases; it does not derive them |
| Test data provisioning and masking | `QA-004` | Named as a dependency per plan |
| Automation tooling and framework build | `QA-005` | `LP-1` and `LP-2` schedule the *work*; `QA-005` specifies the *thing* |
| Performance, security and accessibility plans in detail | `QA-006`, `QA-007`, `QA-008` | §10 states the interface; those documents are the plans |
| UAT participant selection, sign-off protocol | `QA-009` | `LP-5` schedules UAT; `QA-009` governs how business acceptance works |
| Defect thresholds | `QA-010` | |
| Coverage reporting | `QA-011` | |
| Migration test planning | `MG-004`, `MG-005` ⛔ | `LP-6` names L13's interface only |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **QA Lead** | The document they run the test function from, wave by wave |
| Engineering and Integration Leads | `LP-1` and `LP-2` — what they own and when it is due |
| Programme Manager | §4 and §11 — the test calendar, and where it collides with the delivery plan |
| Wave-gate assessors | `EN-03` evidence: which packs exist, which are executable, which are not |
| Business Owners Forum | `LP-5` — the UAT window, and the release of super-users it requires |
| Implementation vendor | The test obligations attaching to each wave's delivery |

---

## 2. Basis and Inputs

### 2.1 Conformance to ISO/IEC/IEEE 29119-3:2021 §8

The standard defines twenty clauses for a test plan. **All twenty are addressed**, in the master plan
(§3.2) or per level plan; the table records where, so an assessor can check rather than trust.

| Clause | 29119-3:2021 §8 element | Where |
|---|---|---|
| 8.1 | Introduction | §1 |
| 8.2 | Context of testing — project, test items, scope, assumptions, stakeholders | §3.2, §5–§10 *Context* |
| 8.3 | Testing communication | §3.4 |
| 8.4 | Risk register — product and project risks | §3.5 |
| 8.5 | Test strategy | **`QA-001`** — referenced, not duplicated |
| 8.6 | Test sub-processes | §5–§10, one per level plan |
| 8.7 | Test deliverables | §12.1 |
| 8.8 | Test data requirements | §12.3, delegated to `QA-004` |
| 8.9 | Test environment requirements | §12.4, delegated to `QA-001` §7 and `PE-002` |
| 8.10 | Retesting and regression testing | §3.6 |
| 8.11 | Suspension and resumption criteria | **`QA-001` §12** — referenced |
| 8.12 | Deviations from the organizational test strategy | §3.7 |
| 8.13 | Testing activities and estimates | §11, §12.2 |
| 8.14 | Staffing | §12.2 |
| 8.15 | Schedule | §4, §11 |
| 8.16 | Test entry criteria | `QA-001` §8.2 per level; wave entry §11.2 |
| 8.17 | Test exit criteria | `QA-001` §8.3 per level; wave exit §11.3 |
| 8.18 | Test completion reporting | `QA-001` §11.3; §12.1 |
| 8.19 | Approvals | §14 |
| 8.20 | References and glossary | §17 |

> **Departure, declared.** 29119-3:2021 anticipates a *test plan per project*. This programme has
> nine waves over 36 months against a fixed level set, so a plan per wave would be nine near-identical
> documents. The structure adopted is **one master plan + six level plans × nine wave instances**
> (§3.1), which keeps the invariant parts written once and the variant parts as data. §3.7 records
> this as the only deviation.

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `QA-001` §4, §5, §7, §8, §10 | The thirteen levels, risk classes, environments, entry/exit criteria, and the capacity position every plan is bounded by |
| `06-01` §3 | Wave scope and duration — W1 Months 1–4 … W9 Months 35–36 |
| `06-01` §4 | The staffing profile the plans are resourced from — **62 QA FTE-months** |
| `06-01` §5 | Cadence: two-week sprints, five to ten per wave; fortnightly to staging, **monthly to production** |
| `06-02` §4 | **70 gate criteria** — the consumers that set every pack's due date |
| `GV-009` §6.1, §9.2 | The gate window T−6 weeks to T+2, and entry criteria `EN-01`…`EN-07` |
| `TS-001` §4.8 | The pack-to-gate mapping this document schedules |
| `AUDIT-014` `TS-02`, `TS-06`, `TS-07` | The three findings this document is written against |
| `IN-008` §4–§7 | The contract and event test surface `LP-2` schedules |
| `BE-008` | Sprint model, Definition of Ready and Done — the unit of work `LP-1` attaches to |

### 2.3 Audit findings this document closes

| Finding | Source | How this document closes it | Residual |
|---|---|---|---|
| `TS-02` | `AUDIT-014` | §4 schedules **all 18 packs** against their earliest consuming criterion under `QA-001` `MTS-R6`, and §4.3 makes the derivation reproducible rather than a table to be maintained by hand | Register change in Category 13 — `QAA-01` |
| `EN-03` | `GV-009` §9.2 | §4.4 produces the T−6 pack readiness statement the entry criterion requires, per gate | — |
| `TS-06` | `AUDIT-014` | §12.5 attaches `MTS-D1`…`D5` to the specific level plan and wave that first needs them, so they appear in a schedule rather than only in a risk register | Funding — `QA-001` `Q-02` |
| `TS-07` | `AUDIT-014` | §12.2 allocates the 62 FTE-months across the six level plans and shows **which plans are under-resourced by how much** | Decision — `QA-001` `Q-01` |

---

## 3. Plan Architecture

### 3.1 One master, six level plans, nine wave instances

> **Why not thirteen level plans for thirteen levels.** L2, L3 and L4 share an owner, an
> environment, a trigger (every commit) and an evidence class; three plans would be three copies.
> L8–L13 are each the subject of their own `QA-` document or an unwritten `MG-` document; a plan
> here would duplicate or pre-empt them. Six is the number of genuinely distinct planning units.

| Plan | Levels covered (`QA-001` §4.2) | Owner | Trigger | Instances |
|---|---|---|---|---|
| **`LP-1`** | L1 Unit | Engineering Lead | Every commit | Continuous; reported per sprint |
| **`LP-2`** | L2 Integration · L3 Contract · L4 Event | Integration Lead | Every commit and every merge | Continuous; reported per sprint |
| **`LP-3`** | L5 SIT | **QA Lead** | Per release into `SIT` | 9 wave instances |
| **`LP-4`** | L6 End-to-end | **QA Lead** | Nightly, plus a gate run | 9 wave instances |
| **`LP-5`** | L7 UAT | **Business Owners Forum** with QA | Per wave, in a fixed window | 9 wave instances |
| **`LP-6`** | L8–L13 non-functional and specialist | Per §10 | Per wave gate / per release | 9 wave instances, delegated |

**A wave instance is data, not a document.** It is a row set — scope, dates, staffing, packs,
environment, exceptions — held against the plan it instantiates, and it is what the gate evidence
pack draws from. This is the same principle `BE-006` applied with `component.yaml`: the invariant is
prose, the variant is machine-readable.

### 3.2 The master plan — context common to all six

| 29119-3 §8.2 element | Value |
|---|---|
| **Project** | 1000FiX ERP System & Portal Suite v2.0 — 67 modules, 12 portals, 4 mobile applications, 331 components across 79 units |
| **Test items** | Every component in `BE-005`; every operation in `IN-002` (1,187); every event in `IN-003` (988); every requirement in the `CV-01` baseline (3,389) |
| **Scope of testing** | All thirteen levels of `QA-001` §4.2, at the depth `QA-001` §5.3 buys for each item's risk class |
| **Assumptions** | (a) `PE-002` and `PE-004` issue in time to provision the seven environments; (b) one of `QA-001` §10.5's closure routes is funded; (c) super-users are released per `EN-04`; (d) `MTS-D1`…`D5` are funded |
| **Constraints** | **62 QA FTE-months total, 8 of them in W1–W2**; business availability, which `06-01` §4 names *"the binding constraint on the programme"*; 0 of 7 environments provisioned at issue |
| **Stakeholders** | Per `QA-001` §9.2 RACI |
| **Basis** | `QA-001`; `05-06` §11; `06-02` §4 |

> **Every one of the four assumptions is currently false.** Stated here rather than buried, because
> 29119-3 §8.2 requires assumptions to be recorded and `GA-11` requires them to be checked at T−6
> weeks, not discovered at T−0. §12.6 tracks each one to an owner.

### 3.3 What a plan may not do

| # | Rule |
|---|---|
| `LVP-01` | **A plan may not weaken an exit criterion.** `QA-001` §8.3 is the floor; a plan may raise it for a wave, never lower it |
| `LVP-02` | **A plan may not reduce depth below the item's risk class.** That is a truncation, and truncation is `QA-001` §12.3's signed act |
| `LVP-03` | **A plan with an unmet assumption is re-baselined, not executed hopefully.** §13 |
| `LVP-04` | **A wave instance is closed by a completion report** (`QA-001` §11.3), never by the wave ending |
| `LVP-05` | **No plan schedules a pack that does not exist.** Where one is needed and absent, the plan records the gap as a blocker against a named owner — §4.4 |

### 3.4 Testing communication *(29119-3 §8.3)*

| Audience | Artefact | Cadence | From |
|---|---|---|---|
| Sprint team | Level `LP-1`/`LP-2` results in the sprint review | Fortnightly | CI |
| QA function | Execution progress — executed ÷ planned, passed ÷ executed | **Daily during a cycle** | Test management tooling |
| Module business owners | Defect profile for their modules | Weekly; **daily in a UAT window** | `TS-018` triage |
| Programme Manager | Test status against the wave calendar; blockers | Weekly | QA Lead |
| Steering Committee | Coverage triple, defect profile, exceptions, truncations | **Per gate** | `QA-011` + §12.1 |
| Wave-gate assessors | The `EN-03` pack readiness statement | **T−6 weeks** | §4.4 |

### 3.5 Risk register *(29119-3 §8.4)*

Project risks to the *testing*, distinct from product risks (which are `QA-001` §5's risk model) and
from programme risks (`GV-005` RAID). **Each is raised into `GV-005` at issue.**

| # | Project risk | Likelihood | Impact | Response | Owner |
|---|---|:--:|:--:|---|---|
| `LVP-R1` | **No environment is provisioned**; 0 of 7 at issue | **Certain today** | **Blocks L5–L13 entirely** | Escalate `PE-002` to W0; interim `CI`-only testing at L1–L4 | CTO |
| `LVP-R2` | **The 38 role accounts are not provisioned** | High | Blocks `LP-3`, `LP-5`, and 100% of `TS-017` | `MTS-D1`; `M29` configuration line in the W1 plan | `M29` owner |
| `LVP-R3` | **QA capacity is 1 FTE in W1–W2** against `G1`'s twelve criteria | **Certain today** | Truncation without a decision | `QA-001` `Q-01` at the W1 gate | CFO with CTO |
| `LVP-R4` | Super-users not released for the UAT window | High | `LP-5` cannot execute; `G1-11` fails | `EN-04` at T−6; escalate at T−4 | Business Owners Forum |
| `LVP-R5` | Business availability — *"the binding constraint"* (`06-01` §4) | High | UAT slips, and UAT is on the gate's critical path | Fixed windows published a wave ahead (§11.4) | Programme Manager |
| `LVP-R6` | Defect arrival exceeds fix capacity late in a wave | Medium | Gate slips or thresholds are argued | `QA-010` thresholds published before W1; weekly burn-down | QA Lead |
| `LVP-R7` | A wave's scope changes mid-cycle | Medium | `MTS-X3` re-opens every level below the change | `GV-006` scope lock; `MTS-U4` suspension | Programme Manager |
| `LVP-R8` | Automation is not built, so regression grows manual | High | By W5 the monthly cadence is unsustainable | `QA-001` route B; `QA-005` as W0 | CTO |

### 3.6 Retesting and regression *(29119-3 §8.10)*

| # | Rule |
|---|---|
| `LVP-06` | **A fixed defect is retested by re-executing the failing case**, not by the fixer's assertion. The retest is recorded against the defect |
| `LVP-07` | **A defect that recurs is reopened one severity higher and its case joins the permanent regression core** (`TS-018` `TR-07`; `TS-013` `RS-03`) |
| `LVP-08` | **Regression scope is derived from change impact**, not from "everything": the changed component, its `AR-006` dependents, its `IN-002` consumers, its `IN-003` subscribers, plus the permanent core |
| `LVP-09` | **The permanent regression core only grows.** A case leaves it only when the requirement it covers is withdrawn under `RQ-005` change control |
| `LVP-10` | **Smoke runs after every deployment**, per portal, in minutes (`TS-013`). A deployment with no smoke result is treated as not deployed |

### 3.7 Deviations from the organizational test strategy *(29119-3 §8.12)*

| # | Deviation | Rationale |
|---|---|---|
| `LVP-DV1` | The plan structure is **one master + six level plans × nine wave instances**, not one plan per project | Nine near-identical documents would drift. §3.1 |
| `LVP-DV2` | `LP-6` **delegates** its detail to `QA-006`, `QA-007`, `QA-008` and (when written) `MG-004`/`MG-005` | Those documents are the plans for their levels; restating them here would create two authorities. §10 |
| `LVP-DV3` | L2, L3 and L4 are planned as **one unit** | Shared owner, environment, trigger and evidence class |

**No other deviation exists.** Every other element of `QA-001` is adopted unmodified.

---

## 4. The Pack-to-Gate Schedule *(closes `TS-02`)*

### 4.1 The rule, restated

> **`QA-001` `MTS-R6`.** A test artefact is registered at **`wave(earliest consuming gate) − 1`**.
> Where that is `W0`, it is `Now`. **Never** the wave in which its subject matter matures.

This is the correction `AUDIT-014` asked to be made **once, register-wide** — the same defect having
appeared 20 times across four content categories, and having been corrected file-by-file twice
before with the pattern recurring at four times the volume.

### 4.2 Every pack, its consumer, and its due date

*Earliest consuming criterion derived from `06-02` §4 and `05-06` §11 at 2026-08-18 22:01 (+06).*

| Pack | Level | Registered | Earliest consumer | Gate month | **Due** | Δ |
|---|:--:|:--:|---|:--:|:--:|:--:|
| `TS-001` Strategy & traceability | — | W1 | Every level's traceability | M4 | **Now** | −1 |
| `TS-002` Test data & personas | all | W1 | `LP-3` entry, `LP-5` entry | M4 | **Now** | −1 |
| `TS-003` SIT A–D | L5 | W2 | `G1-02` full service-order lifecycle | M4 | **Now** | **−2** |
| `TS-004` SIT E–G | L5 | W3 | `G1-05` migration reconciliation | M4 | **Now** | **−3** |
| `TS-005` SIT H–K | L5 | W4 | `G1-06` SSO and role framework | M4 | **Now** | **−4** |
| `TS-006` UAT service ops | L7 | W1 | `G1-11` UAT signed off | M4 | **Now** | −1 |
| `TS-007` UAT commercial | L7 | W2 | `G4-03` contract engine | M18 | W3 | +1 |
| `TS-008` UAT supply chain | L7 | W3 | `G2-06` inventory accuracy by count | M8 | **W1** | **−2** |
| `TS-009` UAT finance | L7 | W1 | `G3-04` Mushak accepted with zero NBR exceptions | M13 | W2 | +1 |
| `TS-010` UAT people | L7 | W5 | `G5-01` first payroll run | M22 | W4 | −1 |
| `TS-011` UAT portals | L7 | W2 | `G1-11`; `P03` ships W1 | M4 | **Now** | **−2** |
| `TS-012` E2E | L6 | W2 | `G1-02`, `G1-03` | M4 | **Now** | **−2** |
| `TS-013` Regression + smoke | L5/L6 | W2 | First production deployment, W1 | M4 | **Now** | **−2** |
| `TS-014` Performance | L8 | W2 | `G1-10` performance targets met | M4 | **Now** | **−2** |
| `TS-015` Offline / field | L12 | W2 | `G2-02` 24-h offline, zero data loss | M8 | W1 | −1 |
| `TS-016` Accessibility | L10 | W2, `P2` | Per-portal release; `P03` ships W1 | M4 | **Now, `P1`** | **−2** |
| `TS-017` Security & privacy | L9 | W2 | `G1-06`, `G1-07`, **`G1-09`** | M4 | **Now** | **−2** |
| `TS-018` Defect taxonomy & forms | all | W2 | Triage from the first test cycle, W1 | M4 | **Now** | **−2** |

**Eleven of eighteen packs are due `Now`.** Nine were already known from `TS-02`; **`TS-011`,
`TS-013` and `TS-018` are found late by this scheduling and were not in `TS-02`'s list** — `TS-011`
because `P03` (the customer portal) ships in W1 and `G1-11` requires UAT sign-off on it; `TS-013`
because the monthly production cadence begins at W1 go-live; `TS-018` because triage begins with the
first test cycle, not with the first gate. **Registered as finding `QAA-08`: `TS-02`'s nine is a
lower bound, and the true figure is twelve.**

### 4.3 The derivation, made reproducible

A table maintained by hand goes stale — that is the defect behind `TS-11` and `PGD-A1-03`. The
schedule above is derivable, and the derivation is recorded so a future issue regenerates rather than
edits:

```text
For each pack P:
  consumers(P) = { criterion C in 06-02 §4  :  C's evidence includes P }
              ∪ { release event R in 05-06 §11 : R's cadence names P }
  due(P) = min( wave(c) for c in consumers(P) ) − 1        # MTS-R6
  if due(P) <= W0: due(P) = "Now"
```

**Rule `LVP-11`.** The schedule is regenerated at each wave gate and the delta reported. A pack whose
consumer set changed and whose due date did not is a scheduling defect, not a stable plan.

### 4.4 The `EN-03` pack readiness statement

`GV-009` `EN-03` requires, at T−6 weeks, that *"every test pack the gate depends on exists and is
executable."* **Executable is a stronger test than exists**, and four packs currently fail it for
reasons that have nothing to do with authoring.

| Pack | Exists | **Executable** | Blocker | Owner |
|---|:--:|:--:|---|---|
| `TS-006` | ✅ | ❌ | `MTS-D3` — no laptop, receipt printer, scanner, signature pad or floor-spec device | Operations Director |
| `TS-008` | ✅ | ❌ | `MTS-D4` — no staged stock: 40 labelled parts across 3 locations | Inventory Manager |
| `TS-015` | ✅ | ❌ | `MTS-D5` — no field logistics, and no safety cover for test personnel | Programme Manager |
| `TS-016` | ✅ | ❌ | `MTS-D2` — no accessibility reviewer | Content Design Lead |
| `TS-017` | ✅ | ⚠ | `MTS-D1` — 38 role accounts absent; the pack is *"not a precondition but the entire pack"* | `M29` owner |
| All 14 others | ✅ | ⚠ | 0 of 7 environments provisioned (`LVP-R1`) | CTO |

> **The readiness statement is produced per gate, in this shape, and it is `E2` evidence.** A gate
> whose statement shows a pack as *exists but not executable* has failed `EN-03` at T−6 weeks — which
> is the point of checking at T−6 rather than T−0.

---

## 5. `LP-1` — Unit Test Plan

| 29119-3 §8 element | Content |
|---|---|
| **Levels** | L1 |
| **Owner / accountable** | Engineering Lead |
| **Test items** | Every custom Python/Odoo model, every TypeScript module, every Dart class, every SQL function in the **331 components across 79 units** of `BE-005` |
| **Sub-processes** | Design (in-sprint, by the developer) · implementation · execution (every commit) · reporting (per sprint, per gate) |
| **Trigger** | Every commit, per `05-06` §11 |
| **Environment** | `CI`, fixtures only. **Never a shared database** — L1 must not depend on state |
| **Data** | Fixtures declared in the component; **no `TS-002` persona data at L1** — that is `LP-3`'s level |
| **Entry** | `QA-001` §8.2 L1 |
| **Exit** | ≥ 80% line coverage of custom code **and 100% of financial and tax calculation paths**, zero failing tests |
| **Evidence** | `E5` — tool, version, scope, per-case result, coverage |
| **Deliverables** | Test code in the component repository · coverage report per build · the L1 section of each sprint report and each level completion report |
| **Staffing** | **Developers, not QA.** `LP-1` consumes zero of the 62 QA FTE-months, by design |

### 5.1 The two coverage rules, and why they are different

| Rule | Target | Measured as | Why the difference |
|---|---|---|---|
| `LVP-U1` | **≥ 80% of custom code** | Line coverage over the component's own modules, excluding vendored and generated code | A ratio target. 80% is `05-06` §11's standard and `NFR-090` §7 restates it |
| `LVP-U2` | **100% of financial and tax calculation paths** | **Branch coverage** over every function on a money or tax path, identified by the `DI-01` decimal-arithmetic classification | An absolute. A financial path with one untested branch is a rounding rule nobody has exercised, and `MTS-G2` says these defects are silent and cumulative |

> **`LVP-U2` is measured as branch coverage, not line coverage, and this is deliberate.** A tax
> calculation is a set of conditions — threshold, exemption, rate band, rounding. Line coverage can
> reach 100% while never taking the exemption branch. **Recorded as `QA-002-D-02`.**

### 5.2 What `LP-1` must not become

| Anti-pattern | Why it is prohibited |
|---|---|
| Tests that require a running Odoo HTTP server | That is L2. `LVP-U3`: an L1 test that needs a server is re-classified, not accepted |
| Tests asserting on the database as a shared fixture | Breaks isolation, produces order-dependent suites, and hides the defect that matters |
| Coverage bought with assertion-free tests | `LVP-U4`: **coverage is a floor, not a goal.** A component whose coverage rose without a behavioural assertion is flagged in review (`BE-003` risk-based review) |
| Excluding hard code from the denominator | `LVP-U5`: the exclusion list is committed, reviewed and shrinking — never quietly extended to hit 80% |

---

## 6. `LP-2` — Integration, Contract and Event Test Plan

| Element | Content |
|---|---|
| **Levels** | L2 Integration · L3 Contract · L4 Event |
| **Owner** | Integration Lead |
| **Test items** | **1,187 API operations** (`IN-002`) · **988 domain events** (`IN-003`) · **~800 provider–consumer pacts** · **47 external integrations, 12 of them P0** (`IN-004`) |
| **Trigger** | Every commit; every merge; **a provider's build fails if any published pact fails verification** (`CT-02`, `FF-95`) |
| **Environment** | `CI` for L3/L4; `CI` + partner stubs for L2; **`SANDBOX`** for external certification (`IN-008` §7) |
| **Entry / Exit** | `QA-001` §8.2/§8.3 L2, L3, L4 |
| **Evidence** | `E5` |
| **Deliverables** | Pact files in the broker · contract verification report per build · event compatibility matrix per release · the L2–L4 sections of each completion report |
| **Staffing** | Developers and the Integration Lead. Consumes **~4 of the 62** QA FTE-months, for the shared harness only |

### 6.1 The boundary with `IN-008`

**`IN-008` is the specification; `LP-2` is the schedule.** `IN-008` §4 defines consumer-driven
contract testing, the pact lifecycle and rules `CT-01`…`CT-07`; it is not restated. `LP-2` adds:

| # | What `LP-2` adds | Why `IN-008` cannot |
|---|---|---|
| `LVP-I1` | **Per-wave scope:** which of the 1,187 operations and 988 events are in each wave's test scope, derived from `AR-006`'s build sequence | `IN-008` is wave-agnostic by design |
| `LVP-I2` | **The external-integration certification calendar** — 12 P0 destinations, each needing a counterparty booking and `E8` third-party confirmation | Booking a counterparty is a schedule act |
| `LVP-I3` | **The `SANDBOX` provisioning date**, which is a `PE-002` dependency (`LVP-R1`) | |
| `LVP-I4` | **The replay and idempotency window** — L4 exit requires replay tested, and replay needs a retained event stream, which needs storage sized in `PE-006` | |

### 6.2 The dependency that determines whether `LP-2` is achievable

> **`CT-07` states that a new consumer's pact that no provider satisfies fails the *consumer's*
> build.** That rule is the one that would have caught `IN-002`'s 100 unmatched paths at authoring
> time. It requires a **pact broker**, which requires the `CI` environment, which is **0 of 7
> provisioned**. Until then, L3 and L4 exist on paper. Recorded against `LVP-R1`.

---

## 7. `LP-3` — System Integration Test Plan

| Element | Content |
|---|---|
| **Level** | L5 SIT |
| **Owner** | **QA Lead** |
| **Test items** | The category-boundary business chains of `TS-003` (56 cases), `TS-004` (42), `TS-005` (56) — **154 identified scenarios**, plus the chains `AR-006` adds per wave |
| **Trigger** | Per release into `SIT` |
| **Environment** | **`SIT`**, full `TS-002` synthetic set, **all 38 role accounts** |
| **Entry** | `QA-001` §8.2 L5 — L1–L4 exit met for every module in the chain; role accounts present; business rules catalogued in `RQ-009` |
| **Exit** | Every scenario in the wave's SIT scope executed; **zero open `S1`**; open `S2` within the `QA-010` threshold; **every class `H` rule has a passing negative case** |
| **Evidence** | `E5` + `E1` |
| **Deliverables** | Execution log · defect records · hard-rule negative-case matrix · SIT completion report |
| **Staffing** | **~18 of the 62** QA FTE-months — the largest QA-owned consumer |

### 7.1 Scope per wave

Derived from `06-01` §3's wave content and `AR-006`'s dependency map. **The boundaries, not the
modules, are the scope** — `LP-3` tests seams.

| Wave | Category boundaries in scope | Primary pack | Gate criteria evidenced |
|:--:|---|---|---|
| W1 | A↔K (service ↔ platform), A↔B (service ↔ customer) | `TS-003`, `TS-005` | `G1-01`, `G1-02`, `G1-04`, `G1-06`, `G1-07` |
| W2 | A↔E (service ↔ stock), E↔K (stock ↔ platform) | `TS-003`, `TS-004` | `G2-01`, `G2-05`, `G2-06`, `G2-07` |
| W3 | E↔G (stock ↔ finance), A↔G, C↔G | `TS-004` | `G3-01`, `G3-02`, `G3-06`, `G3-07`, `G3-09` |
| W4 | B↔C (customer ↔ commercial), C↔G | `TS-003`, `TS-004` | `G4-01`, `G4-03`, `G4-08` |
| W5 | H↔G (people ↔ finance), I↔A (quality ↔ service) | `TS-005` | `G5-01`, `G5-03`, `G5-04` |
| W6 | D↔E (circular ↔ stock), D↔A | `TS-003`, `TS-004` | `G6-01`, `G6-02`, `G6-03` |
| W7 | B↔C↔G (marketplace settlement) | `TS-003`, `TS-004` | `G7-02`, `G7-03`, `G7-06` |
| W8 | J↔all (analytics ↔ everything) | `TS-005` | `G8-01`, `G8-02`, `G8-05` |
| W9 | Multi-entity across all | full regression core | `G9-01`, `G9-02` |

### 7.2 The rule that makes SIT worth its cost

> **`LVP-S1`.** A SIT scenario **asserts a business outcome on the far side of the boundary**, never
> that a message arrived. *"`M15` accepted the stock movement"* is L2. *"The ledger in `M19` moved by
> the right amount as a result"* is L5. A SIT pack full of message-arrival assertions is an expensive
> duplicate of `LP-2`.

| # | Additional rules |
|---|---|
| `LVP-S2` | **Every class `H` hard rule in the wave's scope has a negative case that proves the rule blocks.** A rule tested only positively is a rule nobody has seen enforce |
| `LVP-S3` | **A boundary defect is routed to both sides plus the Solution Architect** (`TS-018` `TR-05`). A seam defect with one owner stays open |
| `LVP-S4` | SIT does not begin until the **whole chain**'s L1–L4 have exited. Partial-chain SIT finds integration defects that are unit defects, at 10× the diagnosis cost |

---

## 8. `LP-4` — End-to-End Test Plan

| Element | Content |
|---|---|
| **Level** | L6 |
| **Owner** | **QA Lead** with the Programme Manager |
| **Test items** | **18 scenarios in 20 executions** (`TS-012`), reconciling the **14 revenue streams** with `05-06` §11's **15 critical journeys** |
| **Trigger** | **Nightly**, per `05-06` §11; plus a witnessed gate run |
| **Environment** | `UAT`, holding a stable release |
| **Entry / Exit** | `QA-001` §8.2/§8.3 L6 — exit requires five consecutive passing nights |
| **Evidence** | `E1` witnessed demonstration + `E5` nightly report |
| **Deliverables** | Nightly run history · witnessed gate demonstration record · journey coverage measure (`QA-011`) |
| **Staffing** | **~8 of the 62** FTE-months, falling as automation rises to 100% by W3 |

### 8.1 The reconciliation this plan protects

`AUDIT-014` `TS-08` records that **two authoritative end-to-end sets exist and disagree**: the
register says *"one scenario per revenue stream"* (14), `05-06` §11 enumerates **15 critical
journeys**, and neither list contains the other. `05-06` omits four revenue streams — warranty
extension sale, spare parts and accessories, backup subscription, advertising and boost — and adds
four journeys that are not revenue streams: procure-to-pay, payroll, complaint-to-CAPA, month-end
close.

`TS-012` §1.1 reconciles them to **18 scenarios in 20 executions** with zero orphans in either
direction. **That reconciliation is adopted here as authoritative.**

> **`LVP-E1`.** The four support scenarios — procure-to-pay, payroll, complaint-to-CAPA, month-end
> close — **are not deletable.** `TS-08` warns that a future reader will treat 18 as an error and
> "correct" it by removing them, and records that **they carry more `P0` business rules than any
> other group in the pack**. Any proposal to reduce the E2E set to 14 is a `GV-003` change request,
> not a tidy-up.

### 8.2 Nightly is a capability, not a preference

`05-06` §11 requires E2E *"automated, run nightly"*. **Nightly execution of 20 journeys is not
achievable manually at any staffing level**, which makes `LP-4` the level whose plan depends most
completely on `QA-005` and `PE-004`.

| Wave | Automated share (`QA-001` §6.4) | Manual executions per night | Feasible? |
|:--:|:--:|---:|:--:|
| W1 | 40% | 12 | **No** — 12 manual journeys nightly against 1 QA FTE |
| W2 | ~70% | 6 | Marginal |
| W3 | **100%** | 0 | Yes |

> **Recorded plainly: `LP-4` cannot meet its own trigger in W1 and W2.** The interim position is a
> **weekly** full run plus nightly execution of the automated subset, declared as an `MTS-X2`
> exception at the W1 and W2 gates with the scope not covered named. This is not a workaround
> presented as a plan; it is a gap with a date on it. Raised as `Q-02`.

---

## 9. `LP-5` — User Acceptance Test Plan

| Element | Content |
|---|---|
| **Level** | L7 |
| **Owner / accountable** | **Business Owners Forum**, with the QA Lead running the mechanics |
| **Test items** | **352 UAT scripts** across six packs — `TS-006` (80), `TS-007` (60), `TS-008` (58), `TS-009` (46), `TS-010` (36), `TS-011` (72) — covering every `P0` and `P1` requirement in the wave |
| **Trigger** | Once per wave, in a **fixed, published window** |
| **Environment** | `UAT`, **data frozen for the cycle** |
| **Entry** | `QA-001` §8.2 L7 — L5 and L6 exit; super-users named and released; executors trained (`UA-03`); **`MTS-D3` and `MTS-D4` present** |
| **Exit** | Every `P0`/`P1` requirement in scope executed **by a named super-user** and signed; every defect triaged; conditional acceptances recorded with dated remediation |
| **Evidence** | `E4` signed record + `E1` witnessed |
| **Deliverables** | Signed script sets · defect records · conditional-acceptance register · UAT completion report |
| **Staffing** | **~22 of the 62** QA FTE-months for coordination, evidence and triage — **plus business time**, which is the binding constraint |

### 9.1 The window

`06-01` §4 commits super-users at *"30% during UAT, 10% otherwise"* and names business availability
*"the binding constraint on the programme."* A UAT window that is not fixed and published a wave
ahead will not be honoured.

| # | Rule |
|---|---|
| `LVP-A1` | **The UAT window is published one full wave ahead** and is a fixed calendar commitment, not a target |
| `LVP-A2` | **UAT data is frozen for the window** (`MTS-U5`). A modification during the cycle suspends the level |
| `LVP-A3` | **The build under test is frozen for the window** except for `S1` fixes, each of which re-triggers the affected scripts (`MTS-U4`) |
| `LVP-A4` | **A super-user executes their own scripts.** A delegate's signature is not acceptance — `QA-001` `MTS-S1`. This is the rule most likely to be broken under schedule pressure |
| `LVP-A5` | **An untrained executor suspends their scripts** (`MTS-U6`, `UA-03`). An untrained executor measures training, not the system |
| `LVP-A6` | The window is **6 weeks** in W1 and W4 (broadest scope), **4 weeks** otherwise, ending at **T−2 weeks** so defects have a fix window before the gate |

### 9.2 The nine roles that cannot satisfy `UA-03` today

`AUDIT-014` `TS-10` found that nine roles across three packs have no course pack or no SOP, and
therefore cannot meet the training precondition. **This is a schedule item for `LP-5`, not only a
Category 06/08 content gap.**

| Role | Headcount | Missing | Packs affected |
|---|---:|---|---|
| `R06` Branch Manager | **51+** | **No SOP** — 11 of `TS-006`'s 12 `R06` scripts have no `SP` to diagnose against | `TS-006` |
| `R29` Cashier | **51+** | No course pack | `TS-009` |
| `R28` Warranty Claims Officer | 4–10 | No course pack — **and runs the whole claim pipeline against a `KPI-038` leakage target** | `TS-007` |
| `R14` Data Services Technician | 5–12 | No course pack — **the only role with `T5` restricted-data access** | `TS-006` |
| `R13` Remote Support Engineer | 15–40 | No course pack | `TS-006` |
| `R25` Retail / Refurbishment Officer | 5–15 | No course pack | `TS-007` |
| `R23` Marketing Manager | 2–4 | No course pack **and no SOP** | `TS-007` |
| `R05` Operations Director | 1–2 | No course pack | `TS-006` |
| `R03` CFO | 1 | No course pack | `TS-009` |

> **`LVP-A7`.** For each of these nine, `LP-5` requires **either** the course pack registered and
> delivered before the wave's window, **or** a recorded interim route naming who briefs the executor
> and on what. **Neither exists today.** Raised as `Q-03`, owned by the L&D Lead with the Business
> Process Analysts. Two roles carry 51+ headcount each.

### 9.3 Conditional acceptance

`06-02` §4 states that *"partial passes are recorded as conditional with a dated remediation plan."*
`LP-5` gives that its mechanics; `QA-009` gives it its authority.

| # | Rule |
|---|---|
| `LVP-A8` | A conditional acceptance names: the scripts not passed, the defect, the risk accepted, the remediation date, and **the business owner accepting it** |
| `LVP-A9` | **A conditional acceptance is carried into every subsequent gate report until closed** — the same treatment as a truncation (`QA-001` §12.3) |
| `LVP-A10` | **No `P0` requirement is conditionally accepted.** `CV-04` makes an untested `P0` a gate failure; an *un-passed* `P0` is a stronger case |

---

## 10. `LP-6` — The Non-Functional and Specialist Levels

`LP-6` is an **interface plan**. It schedules L8–L13 and states each one's dependencies; the plans
themselves live where the expertise does.

| Level | Plan document | Trigger | Wave instance owner | Status |
|:--:|---|---|---|:--:|
| **L8** Performance | **`QA-006`** | Before each wave gate, at 1.5× peak | Platform Engineering | ✅ issued |
| **L9** Security | **`QA-007`** (+ `SC-009` for pen-test) | Every build; pen-test per `SC-009` §7 | Security Lead | ✅ issued |
| **L10** Accessibility | **`QA-008`** | Before each portal release | Content Design Lead | ✅ issued |
| **L11** Localisation | **This plan, §10.1** | Before each wave gate | **Localisation Lead** | Specified here |
| **L12** Offline | **This plan, §10.2** | Before each mobile release | Mobile Lead | Specified here |
| **L13** Data migration | `MG-004`, `MG-005` | Before every cutover | Data Migration Lead | ⛔ **unwritten** |

### 10.1 L11 Localisation — the level with no pack of its own

L11 is the only level whose content is **split across three packs written for other purposes**:
`TS-002` supplies the Bengali text stress set, `TS-016` supplies assistive-technology verification,
`BN-018` supplies wording. `TS-001` recorded this as `O-05` and could not assign an owner;
`QA-001` §4.3 assigned it to the **Localisation Lead**.

| Element | Content |
|---|---|
| **Test items** | Every delivered screen in the wave, in both languages; every notification template; every document template |
| **Scope** | (a) **translation completeness** — `G1-08` requires 100% on delivered screens; (b) **rendering** — Bengali glyph shaping, conjuncts, numerals; (c) **formatting** — lakh/crore grouping, dates, currency; (d) **layout under expansion** — Bengali runs 15–30% longer, per `UX-007` |
| **Environment** | `SIT` |
| **Exit** | 100% translation on delivered screens; **no layout failure under Bengali expansion**; formatting and numerals correct |
| **Evidence** | `E2` translation coverage report + `E1` witnessed rendering review |
| **Gap** | **(d) layout under expansion has no test content in any pack.** `UX-007` specifies the design rule; nothing verifies it. Raised as **`QAA-09`**, owned by the Localisation Lead with `QA-003` to derive the cases |

### 10.2 L12 Offline — the level that cannot be planned from a desk

| Element | Content |
|---|---|
| **Test items** | 33 field scripts (`TS-015` `OFF-001`…`OFF-033`) across three offline applications — technician, rider, field auditor |
| **Targets** | `NFR-047` 24-hour offline · `NFR-037` sync ≤ 30 s on 3G after 24 h · `NFR-036` job list ≤ 8 s cold / ≤ 2 s warm on 3G · **zero data loss, non-negotiable** |
| **Environment** | The **field** — `05-06` §1 gives *"Field test"* as the measurement method for `NFR-036` and `NFR-037` |
| **Entry** | The build installs on the three floor-spec devices; **`MTS-D5` booked**; safety cover for test personnel resolved (`QAA-07`) |
| **Exit** | `QA-001` §8.3 L12 — measured in the field, `E3` + `E5` |
| **Blocker** | **`MTS-D5` is unfunded and unbooked.** Six named locations including a no-signal basement and a moving vehicle, three mobile operators, three devices, full-shift durations, real technicians as executors, a server-side observer |

> **`LVP-O1`.** A lab result does not discharge a field criterion (`GA-02`). `G2-02` and `G2-03` are
> field criteria. **An offline test executed with aeroplane mode in an office is recorded as
> *not executed* against those criteria** — `MTS-R2`.

### 10.3 L13 Data migration — planned against unwritten documents

L13's exit criterion is `E7` reconciliation, and its plan is `MG-004`. **`MG-001`…`MG-003` are ⛔
blocking and `MG-002` records that all 48 legacy sources are unprofiled.**

> **`LVP-M1`.** `LP-6` schedules L13's *test* activity — control totals, reconciliation, variance
> sign-off — against each wave's migration scope, and records that **the transformation logic it is
> testing does not yet have a specification.** `G1-05` requires *"customer and device data migrated
> and reconciled"* at Month 4, evidenced `E7`. Raised into `GV-005` as a programme risk; it is not a
> QA risk and cannot be mitigated from this category.

---

## 11. The Wave Test Calendar

### 11.1 Structure of a wave

`GV-009` §6.1 sets the gate window at **T−6 weeks to T+2**. The test calendar fits inside it, and
each wave has the same eight-stage shape regardless of length.

| Stage | Timing | Activity | Produces |
|---|---|---|---|
| 1 | Wave start | Scope locked (`GV-006` §6.3); risk classes assigned (`QA-001` §5.2); wave instances created | Wave test scope |
| 2 | Continuous | `LP-1`, `LP-2` on every commit | CI results |
| 3 | Per release | `LP-3` SIT cycles | SIT results, defects |
| 4 | Nightly | `LP-4` E2E | Nightly history |
| 5 | **T−6 weeks** | **`EN-01`…`EN-07` checked**, incl. **`EN-03` pack readiness** (§4.4) | Gate entry statement |
| 6 | T−6 to T−2 | **`LP-5` UAT window** (§9.1 `LVP-A6`) | Signed scripts |
| 7 | T−4 to T−1 | `LP-6` — performance at 1.5×, security, accessibility, localisation, offline, migration | `E5`, `E6`, `E3`, `E7` evidence |
| 8 | T−2 | Evidence pack reviewed (`GA-07`); level completion reports signed; coverage published (`QA-011`) | Gate evidence pack |

### 11.2 What each wave tests

| Wave | Months | Gate | Criteria | SIT focus | UAT packs | `LP-6` emphasis |
|:--:|---|:--:|---:|---|---|---|
| **W1** | 1–4 | `G1` | **12** | A↔K, A↔B | `TS-006`, `TS-011` | L8 first baseline · L9 `G1-09` zero critical/high · L10 `P03` · L11 `G1-08` |
| **W2** | 5–8 | `G2` | 10 | A↔E, E↔K | `TS-006`, `TS-008` | **L12 field — `G2-02`, `G2-03`** |
| **W3** | 9–13 | `G3` | 9 | E↔G, A↔G, C↔G | `TS-008`, `TS-009` | L13 financial history reconciliation `G3-08` · L9 payments |
| **W4** | 14–18 | `G4` | 10 | B↔C, C↔G | `TS-007`, `TS-009`, `TS-011` | **`G4-10` — every v1.0 requirement demonstrated or superseded** |
| **W5** | 19–22 | `G5` | 7 | H↔G, I↔A | `TS-010` | **L7 payroll parallel run — two cycles before first live payroll** |
| **W6** | 23–26 | `G6` | 6 | D↔E, D↔A | `TS-006`, `TS-011` | L9 custody and destruction `G6-02`, `G6-03` |
| **W7** | 27–30 | `G7` | 6 | B↔C↔G | `TS-007`, `TS-011` | **L9 marketplace scope isolation — the 379 denied cells at their widest** |
| **W8** | 31–34 | `G8` | 5 | J↔all | `TS-011` | L8 warehouse queries · model cards `G8-05` |
| **W9** | 35–36 | `G9` | 5 | multi-entity | full regression core | **L8 full-scale at 1.5× projected peak — `G9-03`** |
| | | | **70** | | | |

### 11.3 The two waves where the calendar does not fit

Stated rather than smoothed:

| Wave | Problem | Size |
|---|---|---|
| **W1** | 12 gate criteria, 11 packs due `Now`, 0 of 7 environments, 1 QA FTE, 38 role accounts absent, `LP-4` unable to meet its nightly trigger, and the first production go-live | **The most constrained wave in the programme is also the first** |
| **W4** | `G4-10` requires *"every v1.0 BRD requirement demonstrated as delivered or formally superseded"* — a traceability query over the full `CV-01` baseline, at Month 18 | This is the criterion `TS-01` made unanswerable and `QA-011` makes answerable. It needs the RTM populated from W1, not from W4 |

### 11.4 Publication

| # | Rule |
|---|---|
| `LVP-C1` | **The wave test calendar is published at wave start**, with the UAT window fixed (`LVP-A1`) |
| `LVP-C2` | **A date moves by change request, not by drift.** A slipped UAT window is a `GV-003` decision, because it consumes business availability that was committed elsewhere |
| `LVP-C3` | **The T−6 entry statement is published to the Steering Committee**, not held inside QA. `GA-11`: a gate that discovers at T−0 that its evidence cannot be produced has already failed |

---

## 12. Deliverables, Staffing and Dependencies

### 12.1 Deliverables *(29119-3 §8.7)*

| # | Deliverable | Produced by | Cadence | Consumer |
|---|---|---|---|---|
| `LVP-D1` | Test scope per wave instance | QA Lead | Wave start | All plans |
| `LVP-D2` | CI result set | `LP-1`, `LP-2` | Every commit | Sprint review; gate pack |
| `LVP-D3` | SIT execution log and hard-rule negative matrix | `LP-3` | Per cycle | Gate pack |
| `LVP-D4` | Nightly E2E history | `LP-4` | Nightly | Gate pack |
| `LVP-D5` | Signed UAT script sets | `LP-5` | Per wave | **`E4` gate evidence** |
| `LVP-D6` | Conditional-acceptance register | `LP-5` | Per wave, cumulative | Steering Committee |
| `LVP-D7` | Non-functional evidence set | `LP-6` | Per gate | Gate pack |
| `LVP-D8` | **Level completion report** per level per wave | Each plan owner | Per wave | Gate pack; `QA-011` |
| `LVP-D9` | **`EN-03` pack readiness statement** | QA Lead | **T−6 weeks** | Gate assessors |
| `LVP-D10` | Coverage triple | `QA-011` | Fortnightly + per gate | Steering Committee |

### 12.2 Staffing *(29119-3 §8.14)* — and where it does not reach

`QA-001` §10.2 counts **62 QA FTE-months**. This is their allocation across the six plans, and the
shortfall against each.

| Plan | Allocated FTE-months | Demand at `QA-001` §5.3 depth | Shortfall | Note |
|---|---:|---|---|---|
| `LP-1` | **0** | — | none | Developer-owned by design |
| `LP-2` | ~4 | Harness + per-wave scope | ~2 | Rises if the pact broker is late |
| `LP-3` | ~18 | 154 identified scenarios × 9 waves, plus regression | **~14** | The largest QA-owned level |
| `LP-4` | ~8 | 20 executions nightly until automated | **~10 in W1–W2** | Falls to ~0 once automated |
| `LP-5` | ~22 | 352 scripts + coordination + triage + evidence | ~6 | **Business time is the real constraint, and it is not in this budget** |
| `LP-6` | ~10 | L8 37 scenarios · L9 ~734 cases · L10 189 per portal release · L11 · L12 33 field scripts | **~35** | L9 and L10 dominate |
| **Total** | **62** | | **~67 short** | |

> **The allocation exhausts the budget and leaves roughly the same amount again unfunded.** This is
> `AUDIT-014` `TS-07` expressed as a schedule rather than a total, and it is why `QA-001` `Q-01` is
> a Wave 1 decision rather than a Wave 3 discovery. **`LP-6`'s ~35-month shortfall is concentrated in
> the two levels that carry `MTS-G1`** — security and accessibility.

### 12.3 Test data requirements *(29119-3 §8.8)*

| Plan | Data | Source | Blocker |
|---|---|---|---|
| `LP-1` | Component fixtures | Committed with the code | none |
| `LP-2` | Contract examples; event samples | `IN-002`, `IN-003` schemas | none |
| `LP-3` | **Full `TS-002` synthetic set** + 38 role accounts | `TS-002`; `QA-004` | `MTS-D1`; environment |
| `LP-4` | Full set, stable across the night | `TS-002` | environment |
| `LP-5` | **Full set, frozen** | `TS-002`; `QA-004` §7 | environment; freeze mechanism |
| `LP-6` | Production-*shaped volumes* (L8); role accounts (L9); Bengali stress set (L11); device data (L12) | `QA-004`, `QA-006` | **L8 volumes need generation, not masking — `QA-004` §8** |

**All of it is synthetic.** `MTS-R4` and `SG-3` prohibit production personal data in any
non-production environment without a lawful basis and the `QA-004` masking design.

### 12.4 Environment requirements *(29119-3 §8.9)*

Per `QA-001` §7. **0 of 7 provisioned at issue.** Each plan states the environment it cannot start
without, and `EN-06` makes readiness a T−6 check.

### 12.5 The physical dependencies, attached to a plan and a wave

`QA-001` §10.4 names five; here they are scheduled, so they appear in a plan rather than only in a
finding.

| Dependency | Plan | **First needed** | Blocks |
|---|---|:--:|---|
| `MTS-D1` 38 role accounts | `LP-3`, `LP-5`, `LP-6` L9 | **W1, at SIT entry** | `G1-06`, `G1-07`, `G1-09`; the whole of `TS-017` |
| `MTS-D2` accessibility reviewer | `LP-6` L10 | **W1, before `P03` release** | Every portal release |
| `MTS-D3` physical UAT kit | `LP-5` | **W1 UAT window** | `G1-03` |
| `MTS-D4` staged stock, 40 parts, 3 locations | `LP-5` | **W2 UAT window** | `G2-06`, `G2-07` |
| `MTS-D5` field logistics + safety cover | `LP-6` L12 | **W2, at T−4** | `G2-02`, `G2-03` |

### 12.6 The four assumptions, tracked

§3.2 records four assumptions, **all currently false**. Each is tracked to an owner and a date.

| # | Assumption | True? | Owner | Needed by |
|---|---|:--:|---|:--:|
| `LVP-AS1` | `PE-002` and `PE-004` issue in time to provision seven environments | **No** | CTO | **W1** |
| `LVP-AS2` | A `QA-001` §10.5 closure route is funded | **No** | CFO | **W1 gate** |
| `LVP-AS3` | Super-users released per `EN-04` | **Not yet** | Business Owners Forum | T−6 of each wave |
| `LVP-AS4` | `MTS-D1`…`D5` funded | **No** | Programme Manager | **W1** |

---

## 13. Plan Revision and Re-baselining

| # | Rule |
|---|---|
| `LVP-V1` | **A wave instance is baselined at wave start** and changes only by `GV-003` change control thereafter |
| `LVP-V2` | **A change to wave scope re-baselines the instance and re-opens every level below the change** (`MTS-X3`) |
| `LVP-V3` | **An assumption found false re-baselines the plan** (`LVP-03`). It is not executed hopefully and reported as slipped |
| `LVP-V4` | **This document is reviewed at every gate**, and the §4 schedule regenerated per `LVP-11` |
| `LVP-V5` | A level plan changes only with `QA-001`'s owner concurring, because a plan that weakens an exit criterion is a strategy change wearing a plan's clothes (`LVP-01`) |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-002-D-01` | Plan structure | (a) one plan per wave (9); (b) one per level (13); (c) **one master + 6 level plans × 9 wave instances** | **(c)** | Nine near-identical documents drift; thirteen duplicate three shared-owner levels and pre-empt four `QA-` documents | Declared as `LVP-DV1` under 29119-3 §8.12 |
| `QA-002-D-02` | L1 financial-path coverage measure | (a) line coverage; (b) **branch coverage** | **(b)** | A tax calculation is a set of conditions; line coverage can reach 100% without taking the exemption branch | `LVP-U2`; `QA-005` must configure branch coverage on `DI-01` paths |
| `QA-002-D-03` | Whether to restate `IN-008`'s contract-test rules | (a) restate; (b) **reference and add only schedule** | **(b)** | Two authorities on one subject is the defect behind four identifier collisions in this repository | `LP-2` §6.1 adds only `LVP-I1`…`I4` |
| `QA-002-D-04` | The E2E scenario count | (a) 14 revenue streams; (b) 15 critical journeys; (c) **18 in 20 executions per `TS-012`** | **(c)** | `TS-012` §1.1 proves coverage in both directions with zero orphans; the sources disagree and neither contains the other | `LVP-E1` makes the four support scenarios non-deletable |
| `QA-002-D-05` | `LP-4` nightly trigger in W1–W2 | (a) claim nightly; (b) **weekly full + nightly automated subset, declared as an exception**; (c) drop the trigger | **(b)** | 12 manual journeys nightly against 1 QA FTE is not achievable, and claiming it would be `MTS-R2`'s failure mode | `MTS-X2` exception at the W1 and W2 gates |
| `QA-002-D-06` | UAT window length | (a) 2 weeks; (b) **6 weeks W1/W4, 4 weeks otherwise, ending T−2**; (c) continuous | **(b)** | Defects need a fix window before the gate; `06-01` commits super-users at 30% during UAT | `LVP-A6`; published a wave ahead |
| `QA-002-D-07` | Where L11 and L12 plans live | (a) separate `QA-` documents; (b) **inside `LP-6`** | **(b)** | Neither justifies a register row of its own, and both already have content packs. L11's real gap is content, not planning | §10.1, §10.2; `QAA-09` raised for L11's missing layout-expansion cases |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Are `TS-011`, `TS-013` and `TS-018` accepted as three further mis-waved packs, taking `TS-02`'s nine to **twelve**? | Programme Content Lead with QA Lead | **W1** | §4.2; `QAA-08` |
| `Q-02` | Is `LP-4`'s W1–W2 weekly-instead-of-nightly exception accepted at the gate? | Head of Quality Engineering with CTO | **W1 gate** | `G1-02`; `05-06` §11 compliance |
| `Q-03` | For the nine roles with no course pack or SOP, is the course registered or the interim route recorded? | L&D Lead with Business Process Analysts | **T−6 of each wave** | `LVP-A7`; `UA-03`; `G1-11` |
| `Q-04` | When is the `SANDBOX` environment provisioned, and who certifies the 12 P0 external destinations? | Integration Lead with Platform Engineering | **W1** | `LVP-I2`, `LVP-I3`; `IN-008` §7 |
| `Q-05` | Who derives the L11 layout-under-expansion cases that no pack holds? | Localisation Lead with `QA-003` owner | **W1** | `QAA-09`; `G1-08` |
| `Q-06` | Does `MG-004` issue before W1, given `G1-05` requires reconciled migration at Month 4? | Data Migration Lead | **W1** | `LP-6` L13; `G1-05` |

---

## 16. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | All twenty clauses of 29119-3:2021 §8 are addressed or explicitly referenced | §2.1 — 20 of 20 |
| `AC-02` | Every one of the 18 packs has a due date derived from its earliest consuming criterion | §4.2 — 18 of 18 |
| `AC-03` | The schedule's derivation is reproducible, not hand-maintained | §4.3; `LVP-11` |
| `AC-04` | The `EN-03` pack readiness statement is specified and its current state published | §4.4 — 4 packs not executable, 1 partial |
| `AC-05` | Every level plan states owner, items, trigger, environment, entry, exit, evidence, deliverables, staffing | §5–§10 — 6 of 6 |
| `AC-06` | The 62 FTE-months are allocated across the plans, with the shortfall per plan stated | §12.2 |
| `AC-07` | Every physical dependency is attached to a plan and a wave | §12.5 — 5 of 5 |
| `AC-08` | Every assumption is stated with its truth value and an owner | §3.2, §12.6 — 4 of 4, **all false** |
| `AC-09` | The wave calendar covers all 70 gate criteria | §11.2 — 12+10+9+10+7+6+6+5+5 = **70** ✓ |
| `AC-10` | Deviations from `QA-001` are declared under 29119-3 §8.12 | §3.7 — 3 declared |

**Definition of done.** Complete when every criterion is met, `PGD-000`'s Category 08 row is updated
with a fresh enumeration timestamp, the first wave instance is baselined, and the approver has
signed. Approval carries the `PGD-A1-09` qualification.

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `QA-001` | Levels, risk model, entry/exit, environments, capacity — all consumed |
| Upstream | `GV-009` §6, §9 | The gate window and entry criteria this calendar fits inside |
| Upstream | `06-01` §3, §4, §5 | Wave scope, duration, staffing and cadence |
| Upstream | `06-02` §4 | The 70 criteria that set every due date |
| Upstream | `IN-008` | The contract and event surface `LP-2` schedules |
| Upstream | `BE-008` | Sprint model and DoD — the unit `LP-1` attaches to |
| Downstream | `QA-003` | Derives cases into the scope this document schedules |
| Downstream | `QA-006`, `QA-007`, `QA-008` | `LP-6` delegates L8, L9, L10 to them |
| Downstream | `QA-009` | Governs `LP-5`'s acceptance authority |
| Downstream | `QA-010`, `QA-011` | Consume defect and coverage output per wave instance |
| Downstream | `RL-003` | Go-live readiness consumes the completion reports |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-001`…`TS-018` | The 18 packs this document schedules |
| Lateral | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01`, `06-02` | Wave plan and gate criteria |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-003_Test_Design_Specification_and_Case_Repository.md` ·
`./QA-004_Test_Data_Management_and_Anonymisation_Plan.md` · `./QA-005_Test_Automation_Framework_Specification.md` ·
`./QA-006_Performance_and_Load_Test_Plan.md` · `./QA-007_Security_Test_Plan.md` ·
`./QA-008_Accessibility_Test_Plan.md` · `./QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md` ·
`./QA-010_Defect_Management_and_Quality_Gate_Standard.md` · `./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../04_Integration_and_API_Engineering/IN-008_Integration_Test_Sandbox_and_Certification_Specification.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-008_Sprint_Model_Estimation_and_Backlog_Management_Standard.md`

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../project_content/13_Test_and_Acceptance_Content/` (18 files) ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External standards — editions verified 2026-08-18**
ISO/IEC/IEEE 29119-2:2021 (2nd ed.) · ISO/IEC/IEEE 29119-3:2021 (2nd ed.) §8 · PMBOK Guide 7th Edition

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering | Initial issue. All 20 clauses of 29119-3:2021 §8 mapped; plan architecture of one master + six level plans × nine wave instances; **all 18 packs scheduled against their earliest consuming criterion, with a reproducible derivation** — finding **`QAA-08`**, that `TS-02`'s nine is a lower bound and the true figure is **twelve**; the `EN-03` pack readiness statement, showing **4 packs not executable and 1 partial**; six level plans with owner, trigger, environment, entry, exit, evidence, deliverables and staffing; **the 62 FTE-months allocated, leaving ~67 unfunded**; the wave calendar reconciling to all 70 gate criteria; five physical dependencies attached to a plan and a wave; four assumptions stated, **all false**. Closes `TS-02`, and gives `EN-03` its evidence. Raises `QAA-08`, `QAA-09` | *Pending — `GV-002`* |

---

*`QA-002` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
