---
id: QA-010
title: Defect Management and Quality Gate Standard
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Quality Engineering
approver: Chief Technology Officer with the ERP Steering Committee
standards_basis: >
  ISO/IEC/IEEE 29119-3:2021 §12 (incident report) · ISO/IEC/IEEE 1044:2009 (classification of
  software anomalies) · ISO/IEC 25010:2023 · ISO 9001:2015 §10.2 (nonconformity and corrective
  action) · IEEE 1012 (verification and validation)
traces_to: >
  PGD-000 QA-010 · GV-009 §9.3 GA-12 (interim threshold, explicitly to be superseded) ·
  TS-018 (severity, priority, triage, forms) · 06-02 §4 (70 criteria, conditional-pass rule) ·
  QA-001 MTS-R3, §5.4 (RC-A populations) · AUDIT-014 TS-04 (NFR-090 §7 has no gate criterion)
depends_on: TS-018 (taxonomy) · QA-001 (risk classes) · QA-009 (UAT acceptance) · GV-009 (gate outcomes) · QA-011 (coverage)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-010 — Defect Management and Quality Gate Standard

### Category 08 · Code `QA` · ISO/IEC/IEEE 1044:2009 · 29119-3:2021 §12 · ISO 9001:2015 §10.2

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-010` exists in `PGD-000` Category 08, status ◐ `P1` `W1`.
> 2. **`PG-03` Count, do not consult.** Gate criteria counts and scope sizes counted at
>    **2026-08-18 22:01 (+06)** from `06-02` §4 and `BE-005`.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`GV-009` §9.3 asks this document not to adopt its own numbers**, because *"the numbers there
>    are conventional, not derived."* §5 derives them instead. That instruction is the reason this
>    document exists in the shape it does.

---

## 1. Purpose

`TS-018` is a strong defect taxonomy: four severities, four priorities, nine triage rules, a
ten-item automatic-`S1` list, and the three-record boundary between a defect, a non-conformance and
an incident. **What it does not contain is the number.**

`PGD-000` states the gap exactly: *"`TS-018` defines a defect taxonomy and forms. The **gate** — how
many open Sev-2s block go-live — is undefined."* `GV-009` then set an **interim** rule and asked to
be superseded:

> **`GA-12`, `GV-009` §9.3:** *"a gate may not be passed with any open Sev-1, or with more than five
> open Sev-2 defects in the wave's scope, or with any open Sev-2 that affects a P0 criterion. This is
> a placeholder set by this handbook because a gate with no defect threshold has no floor at all.
> **`QA-010` supersedes it and should not simply adopt it** — the numbers here are conventional, not
> derived."*

**This document derives them.** It also adds what a threshold alone cannot do: escape analysis, the
metrics that show whether the thresholds are working, and the missing gate check that
`AUDIT-014` `TS-04` found.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The boundary with `TS-018`** — what is consumed and what is added (§3) |
| 2 | **Defect lifecycle and states**, and the four that are usually missing (§4) |
| 3 | **The derived gate thresholds** — the derivation, then the numbers (§5) |
| 4 | **The four gate checks `06-02` does not contain**, including the one `TS-04` found (§6) |
| 5 | **Escape analysis** — what a defect found in production teaches (§7) |
| 6 | **Metrics** — the eight that matter, and the three that mislead (§8) |
| 7 | **Deferral and debt** — where a deferred defect goes (§9) |
| 8 | **Authority** — who may change a severity, defer, or accept a threshold breach (§10) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Severity and priority **definitions**, the automatic-`S1` list, triage rules `TR-01`…`TR-09`, sign-off forms | **`TS-018`** | **Consumed entirely and not restated.** Two authorities on a severity scale is how a scale stops meaning anything |
| The three-record boundary — defect / non-conformance / incident | `TS-018` §4.2 | Consumed |
| Gate outcomes, assessors, evidence classes | `GV-009` | This document supplies one input to a gate |
| Vulnerability severity (CVSS) and remediation SLAs | `SC-009` §3–§5 | §5.6 states the mapping |
| Technical debt classification and the debt ceiling | `BE-009` | §9.3 states the interface |
| Non-conformance and CAPA | `M23` | |
| Incident severity and response | `M66`, `SC-011` | |
| Coverage measurement | `QA-011` | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Wave-gate assessors** | §5 — the thresholds they assess against, and §6's four additional checks |
| **QA Lead and triage** | §4, §7, §10 — lifecycle, escape analysis, authority |
| Module business owners | §5.4, §9 — what blocks their wave and what a deferral commits them to |
| Steering Committee | §5.5, §8, §10.3 — the only body that may accept a threshold breach |
| Developers | §4, §9 — states, and where a deferred defect goes |
| Head of Quality Engineering | The gate quality opinion this standard makes assessable |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC/IEEE 1044:2009** | The anomaly-classification model — recognition, investigation, action, disposition — is §4's lifecycle | **Departure:** 1044's full attribute set is reduced to the 18 fields of §4.3. Rationale: an attribute nobody populates is an attribute that makes every query wrong |
| **ISO/IEC/IEEE 29119-3:2021 §12** | The incident-report content model | Realised as `TS-018`'s forms plus §4.3's fields |
| **ISO/IEC 25010:2023** | Severity is anchored to quality characteristics via `QA-001` §3.2 | None |
| **ISO 9001:2015 §10.2** | Nonconformity and corrective action — §7's escape analysis is the corrective-action loop | Defects route to `M23` CAPA where systemic (`TS-018`; `SC-009` `RC-5`) |
| **IEEE 1012** | V&V independence in the anomaly disposition | §10.1 — the discloser does not dispose |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `TS-018` §4.1 | **`S1`–`S4` severity definitions** and the **ten automatic-`S1` triggers** |
| `TS-018` §4.2 | The defect / non-conformance / incident boundary |
| `TS-018` §4.3 | **`P1`–`P4` priority** and triage rules `TR-01`…`TR-09` |
| `GV-009` §9.3 | **`GA-12`**, and the instruction to derive rather than adopt |
| `GV-009` §9.1 | Eleven standing criteria `SG-1`…`SG-11` |
| `06-02` §4 | **70 criteria across nine gates: 12, 10, 9, 10, 7, 6, 6, 5, 5** — the scope asymmetry §5.2 turns on |
| `BE-005` | **331 components across 79 units** — the normalisation denominator |
| `QA-001` §5.4 | **The eight `RC-A` populations** |
| `QA-001` `MTS-R3`, `MTS-R9` | Severity is never lowered to pass a gate; `RC-A` is never truncated |
| `QA-009` §10 | Conditional acceptance and its two absolute exclusions |
| `AUDIT-014` `TS-04` | **`NFR-090` §7's unit-test coverage gate is the only `05-06` §11 coverage standard with no gate criterion in `06-02` §4** |
| `BE-009` | The technical-debt register a deferred defect may become |

### 2.3 What this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `GA-12` interim | `GV-009` §9.3 | §5 supersedes it with a derivation, and §5.6 records what changed and why | — |
| `QA-010` register row ◐ | `PGD-000` | *"The gate — how many open Sev-2s block go-live — is undefined"* — §5.3 | — |
| `TS-04` residual | `AUDIT-014` | §6.1 adds the missing gate check for `NFR-090` §7's coverage standard | `RQ-006` renumbering |
| `PGD-A2-12` | `GV-009` §9.4 | §6.4 adds the KPI-reconciliation check as a defect-adjacent gate assertion | `06-02` restatement |

---

## 3. The Boundary With `TS-018`

| Element | Owner | This document |
|---|---|---|
| Severity `S1`–`S4` definitions | **`TS-018` §4.1** | Consumed unchanged |
| The ten automatic-`S1` triggers | **`TS-018` §4.1** | Consumed; §5.1 shows they map one-to-one onto `QA-001`'s `RC-A` populations |
| Priority `P1`–`P4` | **`TS-018` §4.3** | Consumed |
| Triage rules `TR-01`…`TR-09` | **`TS-018` §4.3** | Consumed; `QA-009` §8 adds three UAT-window rules |
| Defect / non-conformance / incident boundary | **`TS-018` §4.2** | Consumed |
| Sign-off forms | **`TS-018`** | Consumed |
| **Lifecycle states and transitions** | **`QA-010`** | §4 |
| **Gate thresholds** | **`QA-010`** | §5 |
| **Escape analysis** | **`QA-010`** | §7 |
| **Metrics** | **`QA-010`** | §8 |
| **Deferral destination and authority** | **`QA-010`** | §9, §10 |

> **`DMG-01`.** Where this document and `TS-018` appear to conflict on classification, **`TS-018`
> governs.** This document governs what happens to a classified defect.

---

## 4. Lifecycle

### 4.1 States

| State | Meaning | Exit condition |
|---|---|---|
| `New` | Raised, not triaged | Triage (`TR-01`) |
| `Triaged` | Severity, priority, owner and target assigned | Work starts, or deferred |
| `In progress` | Being fixed | Fix merged |
| **`Fixed — awaiting retest`** | Merged, **not verified** | Retest executed |
| **`Verified`** | **Retest passed, recorded against the defect** | — |
| `Deferred` | Accepted, scheduled or backlogged (`P3`/`P4`) | §9 |
| `Rejected` | Not a defect | §4.2 |
| **`Reopened`** | Recurred after `Verified` | **`TS-018` `TR-07`: severity one level higher**, and a non-conformance |
| `Blocked` | Cannot progress — dependency, environment, data | Named blocker with an owner |

### 4.2 The four states usually missing, and why each matters

| Missing state | What its absence causes |
|---|---|
| **`Fixed — awaiting retest` distinct from `Verified`** | A defect marked done by the fixer. `LVP-06`: **a fixed defect is retested by re-executing the failing case, not by the fixer's assertion** |
| **`Blocked` distinct from `In progress`** | A blocked defect ages invisibly inside the fix queue, and the gate discovers the dependency at T−0 |
| **`Reopened` distinct from `New`** | Recurrence is invisible, so `TR-07`'s severity escalation and the regression-core promotion never fire |
| **`Rejected` with a reason class** | *"Not a defect"* covers four different situations, and only one of them is benign — §4.4 |

### 4.3 Required fields

Reduced from ISO/IEC/IEEE 1044's full set to eighteen, because an unpopulated attribute makes every
query wrong.

| # | Field | Note |
|:--:|---|---|
| 1 | Identifier | |
| 2 | Title | Business-meaningful (`UAP-23`) |
| 3 | **Severity** | `TS-018` §4.1 |
| 4 | **Priority** | `TS-018` §4.3 |
| 5 | **State** | §4.1 |
| 6 | Found in level | `L1`–`L13`, **or `production`** |
| 7 | **Found by** | Role, and whether internal or external |
| 8 | **Injected in phase** | Requirements / design / build / configuration / data — §7.2 |
| 9 | **`tc_id`** | The case that found it, or **`none`**, which is itself a finding (§7.3) |
| 10 | Requirement(s) | `FR-`, `SWR-`, `NFR-`, `BRU-` |
| 11 | Component | `CD-<UNIT>-<nn>` (`BE-005`) |
| 12 | **`RC-A` flag** | Whether it touches a `QA-001` §5.4 population — **the field that drives §5.3** |
| 13 | Wave | The wave whose gate it counts against |
| 14 | Owner | |
| 15 | Target date | |
| 16 | Environment and build | |
| 17 | **Dataset version** | `TDM-23` — distinguishes a data change from a defect |
| 18 | Linked records | Non-conformance, incident, pen-test finding, debt item |

### 4.4 Rejection reasons

| Reason | Benign? | Action |
|---|---|---|
| Working as specified, and the specification is right | ✔ | Close; **consider a training or documentation gap** |
| **Working as specified, and the specification is wrong** | ✘ | **Not a rejection.** `TR-06`: escalated to the requirement owner |
| Test error — the case was wrong | ✔ | Fix the case (`TDS-36`) |
| **Not reproducible** | ✘ | **Not a rejection until the dataset version and environment are checked** (`TDM-27`). An intermittent product defect looks exactly like this |
| Duplicate | ✔ | Link, do not delete |
| **Shadow-process finding** | ✘ | `TS-012` `EE-05`: a **scope gap**, routed to the Programme Manager. *"Logging it as a defect hides it inside a defect count"* |

---

## 5. The Derived Gate Thresholds

### 5.1 The derivation — first principle

> **A gate threshold is not a tolerance for broken software. It is a statement of how much unresolved
> risk the business will operate with**, for the period between this gate and the next.

That gives three questions, and the answers derive the numbers.

| Question | Answer | Derives |
|---|---|---|
| **What may never be operated with?** | Anything unlawful, irreversible, or silently cumulative | **`S1` = zero, absolutely** |
| **How many workarounds can a function sustain?** | Bounded by the function's headcount and volume, not by a programme-wide count | **`S2` normalised to scope, capped per role** |
| **How long is the exposure?** | Until the next gate — **4 to 5 months** | Deferral limits, §9 |

### 5.2 Why a flat number is wrong — and why `GA-12` had to be interim

`GA-12` sets *"more than five open Sev-2 defects in the wave's scope"*. Counted at 22:01 (+06),
wave scopes differ by more than **4×**:

| Gate | Criteria | Relative scope | *"5 open `S2`"* means |
|:--:|---:|---:|---|
| `G1` | **12** | 1.00 | 1 `S2` per 2.4 criteria |
| `G2` | 10 | 0.83 | 1 per 2.0 |
| `G3` | 9 | 0.75 | 1 per 1.8 |
| `G4` | 10 | 0.83 | 1 per 2.0 |
| `G5` | 7 | 0.58 | 1 per 1.4 |
| `G6` | 6 | 0.50 | 1 per 1.2 |
| `G7` | 6 | 0.50 | 1 per 1.2 |
| `G8` | 5 | 0.42 | 1 per 1.0 |
| `G9` | 5 | 0.42 | 1 per 1.0 |

**The same flat number is a 2.4× looser bar at `G1` than at `G8`** — and `G1` is the gate with the
most criteria, the first production go-live, and the least mature system. A flat threshold is
loosest exactly where it should be tightest.

> **`DMG-02`.** Gate thresholds are **normalised to the wave's delivered scope**, measured in
> **delivered components** (`BE-005`, `CD-<UNIT>-<nn>`) — a count that is objective, already
> maintained, and does not move with how criteria were worded.

### 5.3 The thresholds

> **`DMG-03`. These supersede `GA-12` in full.** Every one is derived in §5.4.

| # | Threshold | Value | Applies |
|:--:|---|---|---|
| **`DMG-T1`** | **Open `S1` defects in the wave's scope** | **Zero. No exception, no acceptance, no conditional pass** | Every gate |
| **`DMG-T2`** | **Open defects of any severity on an `RC-A` population** (`QA-001` §5.4) | **Zero** | Every gate |
| **`DMG-T3`** | **Open `S2` defects** | **≤ 1 per 10 delivered components in the wave's scope, and never more than 8 in total** | Every gate |
| **`DMG-T4`** | **Open `S2` defects affecting a single role's primary tasks** | **≤ 1** | Every gate, per role |
| **`DMG-T5`** | **Open `S2` defects affecting a `P0` gate criterion** | **Zero** | Every gate |
| **`DMG-T6`** | **Open `S3` defects** | **No cap. A rising trend across two consecutive gates is a Conditional Pass**, not a Fail | Every gate |
| **`DMG-T7`** | **Defects `Fixed — awaiting retest` at T−0** | **Zero.** An unverified fix is an open defect (`LVP-06`) | Every gate |
| **`DMG-T8`** | **Defects `Blocked` for more than 20 working days** | **Zero** — resolved, escalated or accepted as a deferral with a date | Every gate |
| **`DMG-T9`** | **Reopened defects in the window** | **A count > 3 triggers a mandatory escape analysis** (§7) before the gate | Every gate |

### 5.4 The derivation of each number

| Threshold | Derived from |
|---|---|
| **`DMG-T1` zero `S1`** | Not a convention. Every one of `TS-018`'s **ten automatic-`S1` triggers** is an `MTS-G1` or `MTS-G2` failure: a posting that does not reconcile, a wrong Mushak field, stock moving without valuation, offline data loss, a wrong payroll figure, a party reaching data outside their scope, a residency-classified field written outside its store, a denial that holds in the UI and not the API, a target met by degrading another, an assisted user unable to complete a primary task. **Each is unlawful, irreversible or silently cumulative.** `MTS-R9` forbids truncating an `RC-A` population; permitting one open `S1` is exactly that truncation |
| **`DMG-T2` zero on `RC-A`** | The same argument, extended from *severity* to *population*. An `S3` on a statutory output is still on a statutory output, and severity is a judgement about symptom while `RC-A` is a fact about consequence |
| **`DMG-T3` ≤ 1 per 10 components, cap 8** | **Two independent bounds, and the lower binds.** (a) *Density:* `BE-006`'s 23-criterion DoD with 19 machine-checked means a component reaching a gate with more than one open `S2` did not meet its own DoD; **1 per 10 allows a tenth of the wave's components to carry one, which is the tolerance for genuine integration-surface findings.** (b) *Absolute:* the cap of 8 exists because at `G1`'s ~50 delivered components the density rule alone would allow 5, and at a late wave's ~90 it would allow 9 — but **no wave-gate assessment can meaningfully hold more than about 8 distinct open workarounds in view at once**, which is the practical limit on an `E1`/`E4` assessment. The cap binds from roughly the fourth wave onward |
| **`DMG-T4` ≤ 1 per role** | Derived from headcount and volume. `TS-018` defines `S2` as *"a core task cannot be completed, or only by a workaround that will not survive volume."* **`R06` is 51+ people, `R08` is 150–250, `R11` is 120–250**, and the system serves **250,000+ customers a month**. Two concurrent workarounds in one role's daily work is not a degraded experience — it is a parallel manual process, and `06-02` §5's success criterion is *zero shadow spreadsheets*. **One is the largest number compatible with that criterion** |
| **`DMG-T5` zero on a `P0` criterion** | `GA-12` had this and it is retained — it is the one part of the interim rule that was already derived rather than conventional. A `P0` criterion with a known workaround is a criterion not met |
| **`DMG-T6` `S3` trend, not cap** | An `S3` has a known workaround and no operational consequence, so a cap would fail gates for cosmetic reasons and create pressure to downgrade `S2`s — the `MTS-R3` failure mode. **But a rising `S3` count across two gates indicates falling build quality before it reaches severity**, which is exactly what a leading indicator should do |
| **`DMG-T7` zero awaiting retest** | Definitional. `LVP-06` makes a fix real only on retest; a defect *"fixed"* but unverified is indistinguishable from open, and counting it as closed is how a gate is passed on a number that is not true |
| **`DMG-T8` 20 working days blocked** | Derived from the gate cycle. `GV-009` sets the window at T−6 weeks = **30 working days**. A defect blocked longer than two-thirds of that window will not be resolved inside it, so it is decided at T−2 rather than discovered at T−0 (`GA-11`) |
| **`DMG-T9` 3 reopens** | Derived from `TR-07`, which escalates severity on recurrence. **Three recurrences in one window is a process signal, not three coincidences** — the regression derivation, the retest practice, or the fix quality is failing, and §7's analysis finds which |

### 5.5 Breach

| Outcome | Rule |
|---|---|
| **`DMG-T1`, `DMG-T2`, `DMG-T5` breached** | **Gate Fail.** Not a Conditional Pass. **No body may accept it**, including the Steering Committee — these are the `MTS-R9` populations, and an acceptance would be a truncation of an `RC-A` population |
| `DMG-T3`, `DMG-T4`, `DMG-T7`, `DMG-T8` breached | **Conditional Pass available**, accepted by the **Steering Committee** with a dated remediation plan, carried to every subsequent gate (`UAP-39`) |
| `DMG-T6`, `DMG-T9` breached | **Conditional Pass**, with the escape analysis (§7) as a condition of the next gate |

> **`DMG-04`.** A threshold breach is **never resolved by re-classifying the defect** (`TS-018`
> `DF-04`, `TR-09`; `MTS-R3`). Where severity is genuinely contested, §10.2 applies.

### 5.6 What changed from `GA-12`, and why

| `GA-12` | `QA-010` | Reason |
|---|---|---|
| No open Sev-1 | **`DMG-T1` retained, and made non-acceptable by any body** | The ten automatic-`S1` triggers are all unlawful, irreversible or silently cumulative |
| **≤ 5 open Sev-2, flat** | **`DMG-T3` ≤ 1 per 10 components, cap 8** | A flat number is a 2.4× looser bar at `G1` than at `G8`, and `G1` is the least mature gate |
| No Sev-2 on a P0 criterion | **`DMG-T5` retained unchanged** | Already derived rather than conventional |
| — | **`DMG-T2` zero on `RC-A`** | Severity is a symptom judgement; `RC-A` is a consequence fact |
| — | **`DMG-T4` ≤ 1 per role** | 51+ and 150–250 headcount roles cannot carry two parallel workarounds against `06-02` §5's zero-shadow-spreadsheet criterion |
| — | **`DMG-T6`…`DMG-T9`** | Unverified fixes, aged blockers and recurrence were entirely unbounded |

### 5.7 Vulnerability mapping

`SC-009` owns CVSS-based vulnerability severity. `SG-1` requires **zero open critical or high**
security findings at every gate.

| CVSS / `SC-009` | Defect severity | Threshold |
|---|:--:|---|
| Critical | **`S1`** | `DMG-T1` — zero |
| High | **`S1`** | `DMG-T1` — zero. **`SG-1` already requires this**; the mapping makes the two registers agree |
| Medium | `S2` | `DMG-T3`, `DMG-T4` |
| Low | `S3` | `DMG-T6` |

> **`DMG-05`.** A security finding enters `TS-018` triage like any other defect (`STP-42`). **A
> pen-test finding held in a separate register acquires a separate, slower SLA**, which is the
> failure mode `SC-009` `VD-4` already identified — *"one register, one SLA model."*

---

## 6. The Four Gate Checks `06-02` Does Not Contain

`06-02` §4's 70 criteria are business-outcome criteria. Four quality assertions are absent, and each
is cheap to check and expensive to omit.

### 6.1 `DMG-G1` — the unit-test coverage gate *(closes `TS-04`'s residual)*

> `AUDIT-014` `TS-04`: **`NFR-090` §7's unit-test coverage gate is the only `05-06` §11 coverage
> standard with no gate criterion in `06-02` §4. Nothing verifies it at `G1`–`G9`.**

| Element | Provision |
|---|---|
| Assertion | **≥ 80% line coverage of custom code**, and **100% branch coverage of `@financial_path` functions** (`QA-005` §9), for the wave's delivered components |
| Evidence | `E2` — the CI coverage report, with denominators (`MTS-R1`) |
| Breach | **Gate Fail** on the 100% financial-path assertion; **Conditional Pass** on the 80% line assertion |
| Note | Cited as **`NFR-090` §7**, never bare, until `RQ-006` renumbers (`TAF-44`) |

### 6.2 `DMG-G2` — the coverage-report check

| Element | Provision |
|---|---|
| Assertion | `QA-011`'s coverage report exists for the wave, **as a triple** (`MTS-R1`), and **`CV-M6` P0 test coverage is 100%** (`CV-04`) |
| Evidence | `E2` |
| Breach | **Gate Fail** on `CV-M6`; Conditional Pass otherwise |

### 6.3 `DMG-G3` — the not-executed check

| Element | Provision |
|---|---|
| Assertion | Every level's completion report names what was **not executed**, and no criterion is evidenced by a level recorded as not executed (`MTS-R2`, `GA-06`) |
| Evidence | `E2` + `E6` |
| Breach | **Gate Fail** — this is the check that prevents an unexecutable pack being reported as clean, which is `TS-06`'s named failure mode |

### 6.4 `DMG-G4` — the KPI reconciliation check *(`PGD-A2-12`)*

`GV-009` `SG-11` requires every numeric gate criterion to reconcile to its registered KPI's target
for that wave, or state why it is more demanding. `GV-009` §9.4 records the live example: **`G1-03`
demands at Month 4 a standard `KPI-010` does not target until Month 34.**

| Element | Provision |
|---|---|
| Assertion | Every numeric criterion reconciles to its KPI, or its divergence is stated and accepted |
| Evidence | `E2` |
| Breach | Conditional Pass; the divergence is recorded in `GV-003` |

---

## 7. Escape Analysis

### 7.1 What an escape is

> **`DMG-06`.** An **escape** is a defect found at a level later than the level that should have
> found it — including in production. Escapes are the only direct measurement of whether the test
> strategy works.

### 7.2 The analysis

Mandatory for: every production `S1` or `S2`; every `DMG-T9` breach; every wave's top three escapes
by cost.

| Question | Purpose |
|---|---|
| **Which level should have found this?** | Names the gap in `QA-001` §4's level set |
| **Was there a case for it?** (`tc_id` = `none`?) | A defect with no case is a **derivation** gap — `QA-003` |
| **If there was a case, why did it pass?** | A **case-quality** gap — `TDS-Q7` sufficiency |
| **In which phase was it injected?** | Requirements / design / build / configuration / data. **A requirements-injected defect is not fixed by more testing** |
| **Was it in an `RC-A` population?** | If yes, the risk assessment was wrong, not just the test |
| **Was it deferred earlier?** | A deferral that became an escape is a deferral-authority failure — §9 |

### 7.3 The action

| Finding | Action |
|---|---|
| No case existed | Add the case (`TDS-36`) **and the class of case**, not just the instance |
| The case existed and passed | Fix the case; if the technique was wrong, fix the technique for the whole class (`TDS-08`) |
| The level was wrong | Amend `QA-001` §4 or `QA-002`'s scope |
| **Systemic** | **Raise an `M23` non-conformance and a CAPA** (`TS-018`; `SC-009` `RC-5`), because the class matters more than the instance |
| Recurrence | `TR-07` — reopen one severity higher; **promote the case to the permanent regression core** (`TS-013` `RS-03`, `LVP-09`) |

### 7.4 The measure

> **`DMG-07` Defect Detection Percentage (`DDP`)**, per level:
>
> ```text
> DDP(level) = defects found at that level
>              ÷ (defects found at that level + defects that escaped past it)
> ```
>
> Reported per wave with its denominator (`MTS-R1`). **`DDP` is the only metric that measures the
> test strategy rather than the software**, and it is why §8 treats it as the primary one.

| Level | `DDP` target from W3 | Rationale |
|---|:--:|---|
| L1–L4 combined | ≥ 60% | The cheapest levels should find the most |
| L5 SIT | ≥ 20% | Boundary defects |
| L6, L7 | ≤ 15% combined | UAT finding a large share means earlier levels are not working |
| **Escaped to production** | **≤ 5%** | The number the business experiences |

---

## 8. Metrics

### 8.1 The eight that matter

| # | Metric | Cadence | Reported to | What it tells you |
|:--:|---|---|---|---|
| 1 | **Open defects by severity, in wave scope** | Daily in a cycle | QA, business owners | The gate position |
| 2 | **`DMG-T1`…`T9` threshold status** | Weekly, and at T−6/T−2/T−0 | Gate assessors | Whether the gate can pass |
| 3 | **`DDP` per level** | Per wave | Head of QE, CTO | **Whether the test strategy works** |
| 4 | **Escape rate to production** | Per release | Steering Committee | What the business experiences |
| 5 | **Reopen rate** | Per wave | QA Lead | Fix and regression quality |
| 6 | **Age of open defects by severity** | Weekly | QA Lead | Whether triage priorities are honoured |
| 7 | **Injection phase distribution** | Per wave | CTO | Where to invest — requirements, design or build |
| 8 | **Open conditional acceptances and deferrals, cumulative** | Per gate | Steering Committee | **Accumulated unresolved risk across waves** — the number nobody tracks by default |

### 8.2 The three that mislead

| Metric | Why it misleads |
|---|---|
| **Total defect count** | Falls when testing stops. It measures test activity, not quality, and it falls fastest exactly when it should rise |
| **Defects per developer** | Measures whoever writes the most code, and makes raising a defect a social act |
| **Pass rate** | *"98% of cases passed"* is compatible with every `S1` being in the 2%. **`DMG-T1`…`T5` are severity-and-population assertions precisely because a rate cannot express them** |

> **`DMG-08`.** §8.2's three are **not published** in gate reporting. `GA-04`'s denominator rule and
> `MTS-R1` are not satisfied by a metric that is misleading even when correctly denominated.

---

## 9. Deferral and Debt

### 9.1 Where a deferred defect goes

| Priority (`TS-018`) | Destination | Review |
|---|---|---|
| `P3` Next wave | The wave's backlog (`BE-008`), **reported at every gate until fixed** | Per gate |
| `P4` Backlog | Accepted and unscheduled | **Quarterly — scheduled or withdrawn, never silently retained** |
| **Accepted permanently** | **`BE-009` technical-debt register as a `DBT-nnn` item** | Per `BE-009` |

### 9.2 Rules

| # | Rule |
|---|---|
| `DMG-09` | **A deferral has an accepter by name, a business risk statement and a review date** — the same content as a conditional acceptance (`UAP-38`) |
| `DMG-10` | **No `S1` is deferred. No `RC-A` defect is deferred at any severity** (`DMG-T1`, `DMG-T2`) |
| `DMG-11` | **A deferral that becomes an escape is analysed as an authority failure**, not only as a technical one (§7.2) |
| `DMG-12` | **Deferral counts are cumulative across waves and published** (§8.1 metric 8). Nine waves of individually reasonable deferrals is how a system arrives at go-live with an unrecognised backlog |

### 9.3 The interface with `BE-009`

> **`DMG-13`.** A defect **permanently accepted** ceases to be a defect and becomes a **`DBT-nnn`
> debt item** under `BE-009`, where it is measured with principal-and-interest arithmetic and counts
> against the **hard 15% debt ceiling a deadline cannot waive**. It does not remain an open defect
> indefinitely, and it does not disappear. `BE-009` already counts **15 items, 6,550 instances, 1,387
> discrete, 6 of them S1 and 4 W0-blocking** before a line of code exists.

---

## 10. Authority

### 10.1 Who may do what

| Act | Who | Constraint |
|---|---|---|
| Raise a defect | **Anyone** | Never filtered before triage |
| Propose severity | The finder | `TS-018`: proposed by the finder, confirmed in triage |
| **Confirm severity** | **Triage**: QA Lead + module business owner + engineering + Solution Architect for cross-module (`TR-02`) | **Never the fixer alone** — IEEE 1012 independence |
| Set priority | **The module business owner** with QA | Never the finder, never the developer |
| **Change a severity after triage** | **Triage, with the change and its reason recorded** | **Never to affect a gate outcome** (`DF-04`, `TR-09`, `MTS-R3`) |
| Defer | The module business owner, within `TS-018` priority rules | **Never an `S1`, never an `RC-A`** |
| **Verify a fix** | **The retester, who is not the fixer** | `LVP-06`; `SC-009` `RC-2`/`IN-5` |
| Accept a `DMG-T3`/`T4`/`T7`/`T8` breach | **The Steering Committee** | With a dated remediation plan |
| **Accept a `DMG-T1`/`T2`/`T5` breach** | **Nobody** | §5.5 |
| Give the gate quality opinion | **Head of Quality Engineering** | Independent of the schedule (`MTS-S4`) |

### 10.2 Contested severity

| # | Rule |
|---|---|
| `DMG-14` | A contested severity is **recorded as contested, with both positions**, and escalated per `CG-002` §7 |
| `DMG-15` | **Pending resolution, the higher severity applies.** The alternative lets a gate pass while the argument continues, and the argument then ends |

### 10.3 The Steering Committee's limit

> **`DMG-16`.** The Steering Committee may accept schedule, cost and scope risk. **It may not accept
> an open `S1`, or any open defect on an `RC-A` population**, because those are unlawful,
> irreversible or silently cumulative outcomes and no governance body's authority extends to
> accepting them. This is the same boundary `MTS-R9` draws for truncation and `UAP-44` draws for
> conditional acceptance, and the three are deliberately identical.

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-010-D-01` | Whether to adopt `GA-12` | (a) adopt; (b) **derive and supersede** | **(b)** | `GV-009` §9.3 explicitly asked not to be adopted: *"the numbers here are conventional, not derived"* | §5; `DMG-T1`…`T9` |
| `QA-010-D-02` | `S2` threshold form | (a) flat count; (b) **normalised per delivered component with an absolute cap** | **(b)** | A flat 5 is a **2.4× looser bar at `G1` than at `G8`**, and `G1` is the least mature gate | `DMG-T3` |
| `QA-010-D-03` | Normalisation denominator | (a) gate criteria; (b) requirements; (c) **delivered components (`BE-005`)** | **(c)** | Objective, already maintained, and does not move with how a criterion was worded | `DMG-02` |
| `QA-010-D-04` | Whether severity alone governs | (a) severity only; (b) **severity plus `RC-A` population** | **(b)** | Severity is a judgement about symptom; `RC-A` is a fact about consequence. An `S3` on a statutory output is still on a statutory output | `DMG-T2` |
| `QA-010-D-05` | Per-role threshold | (a) none; (b) **≤ 1 open `S2` per role** | **(b)** | `R06` is 51+, `R08` is 150–250, and `06-02` §5 requires **zero shadow spreadsheets**. Two workarounds in one role's daily work *is* a shadow process | `DMG-T4` |
| `QA-010-D-06` | `S3` handling | (a) cap; (b) **trend across two gates** | **(b)** | A cap fails gates for cosmetic reasons and creates pressure to downgrade `S2`s — the `MTS-R3` failure mode | `DMG-T6` |
| `QA-010-D-07` | Whether a body may accept an `S1` | (a) Steering Committee may; (b) **nobody may** | **(b)** | The ten automatic-`S1` triggers are unlawful, irreversible or silently cumulative. Consistent with `MTS-R9` and `UAP-44` | §5.5, §10.3 |
| `QA-010-D-08` | Primary metric | (a) defect count; (b) pass rate; (c) **`DDP` per level** | **(c)** | `DDP` measures the **test strategy**; the other two measure test activity and can improve while quality falls | §7.4, §8 |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Does the Steering Committee accept that it **may not** accept an open `S1` or an `RC-A` defect? | ERP Steering Committee | **W1, at constitution** | §5.5, §10.3 — the standard's central assertion |
| `Q-02` | Is `DMG-G1` accepted as a **71st gate criterion** in `06-02` §4, closing `TS-04`'s residual? | Enterprise Architecture with CTO | **W1** | §6.1; `NFR-090` §7 |
| `Q-03` | Is the delivered-component count per wave published, so `DMG-T3` is computable at T−6? | Engineering Lead with PMO | **T−6 of `G1`** | `DMG-T3`, `DMG-02` |
| `Q-04` | Which defect-tracking tool holds the 18 fields, including `RC-A` and injection phase? | QA Lead with Platform Engineering | **W1** | §4.3; §7; §8 |
| `Q-05` | Are the §7.4 `DDP` targets accepted as gate reporting from W3? | Head of Quality Engineering with CTO | **W2** | §8 metric 3 |
| `Q-06` | Who maintains the cumulative deferral and conditional-acceptance register across nine waves? | PMO with QA Lead | **W1** | §8 metric 8; `DMG-12` |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | `GA-12` is superseded by derived thresholds, with the derivation shown | §5.4, §5.6 |
| `AC-02` | Every threshold states its value, scope and breach consequence | §5.3, §5.5 — 9 thresholds |
| `AC-03` | The flat-number problem is demonstrated with counted figures | §5.2 — **2.4× spread across gates** |
| `AC-04` | Severity and population are separate assertions | `DMG-T1` vs `DMG-T2` |
| `AC-05` | The lifecycle contains the four states usually missing | §4.2 |
| `AC-06` | Required fields include the ones that make escape analysis possible | §4.3 — 18 fields |
| `AC-07` | The four missing gate checks are specified, including `TS-04`'s | §6 |
| `AC-08` | Escape analysis has a trigger, a method, an action and a measure | §7 |
| `AC-09` | Metrics distinguish the eight that matter from the three that mislead | §8 |
| `AC-10` | Deferral has a destination, and permanent acceptance becomes `BE-009` debt | §9 |
| `AC-11` | Authority is bounded, including a limit on the Steering Committee | §10.3 |
| `AC-12` | Nothing in `TS-018` is restated or contradicted | §3; `DMG-01` |

**Definition of done.** Complete when every criterion is met, the tracking tool holds the 18 fields,
`DMG-T1`…`T9` are assessed at the W1 gate, and the approver has signed. Approval carries the
`PGD-A1-09` qualification.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `TS-018` | Severity, priority, triage, forms — consumed entirely |
| Upstream | `GV-009` §9.1, §9.3 | Standing criteria; `GA-12`, superseded here |
| Upstream | `QA-001` §5.4, `MTS-R3`, `MTS-R9` | `RC-A` populations and the truncation prohibition |
| Upstream | `06-02` §4 | The 70 criteria and their per-gate distribution |
| Upstream | `BE-005` | The delivered-component count `DMG-T3` normalises against |
| Upstream | `SC-009` | Vulnerability severity, mapped in §5.7 |
| Downstream | `GV-009` | `DMG-T1`…`T9` become the gate's defect assertion |
| Downstream | `QA-009` | Conditional acceptance operates inside these thresholds |
| Downstream | `QA-011` | `DMG-G2` consumes the coverage report |
| Downstream | `BE-009` | Permanently accepted defects become `DBT-nnn` debt |
| Downstream | `RL-003` | Go-live readiness consumes the threshold status |
| Lateral | `M23` | Systemic escapes raise a non-conformance and CAPA |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-005_Test_Automation_Framework_Specification.md` · `./QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md` ·
`./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-005_Custom_Development_CD_Master_Register.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-009_Technical_Debt_Register_and_Refactoring_Policy.md`

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4, §5 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-018_Defect_Taxonomy_Triage_and_Signoff_Forms.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
ISO/IEC/IEEE 1044:2009 · ISO/IEC/IEEE 29119-3:2021 §12 · ISO/IEC 25010:2023 ·
**ISO 9001:2015 §10.2** · IEEE 1012

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering | Initial issue. **Supersedes `GA-12` with nine derived thresholds `DMG-T1`…`T9`**, each with its derivation shown — including the counted demonstration that a flat `S2` count is a **2.4× looser bar at `G1` than at `G8`**, which is why `GA-12` had to be interim; separates **severity from population**, so an `S3` on an `RC-A` population is still blocking; adds the **per-role `S2` limit** derived from 51+ and 150–250 headcount roles against `06-02` §5's zero-shadow-spreadsheet criterion; a lifecycle containing the **four states usually missing**; eighteen required fields, including the `RC-A` flag and injection phase that make escape analysis possible; **the four gate checks `06-02` does not contain**, closing `TS-04`'s residual on `NFR-090` §7; `DDP` as the primary metric, with the three misleading metrics excluded from gate reporting; and **a stated limit on the Steering Committee's authority** — it may not accept an open `S1` or any open `RC-A` defect | *Pending — `GV-002`* |

---

*`QA-010` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
