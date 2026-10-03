---
id: QA-011
title: Requirements-to-Test Coverage Standard and Report
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Quality Engineering with Enterprise Architecture
approver: Chief Technology Officer with the ERP Steering Committee
standards_basis: >
  ISO/IEC/IEEE 29119-3:2021 §11 (test completion report) · ISO/IEC/IEEE 29148:2018 §5.2.8 ·
  ISO/IEC 25040:2011 (evaluation process) · ISO 21502:2020 (measurement)
traces_to: >
  PGD-000 QA-011 · audit AUDIT-014 TS-01 (CRITICAL — three coverage denominators; no coverage
  percentage may be quoted) · 06-02 G4-10 (every v1.0 requirement demonstrated or superseded) ·
  RQ-001 §3.10.5 CR-01 · RQ-004 §5 CV-01…CV-04 · GV-009 GA-04 · QA-001 MTS-R1
depends_on: RQ-001 (denominator) · RQ-004 (RTM, measures) · QA-003 (cases, tc_id) · QA-005 (result shape) · QA-010 (defect state)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P0
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-011 — Requirements-to-Test Coverage Standard and Report

### Category 08 · Code `QA` · ISO/IEC/IEEE 29119-3:2021 §11 · ISO/IEC 25040:2011

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-011` exists in `PGD-000` Category 08, status ⛔ `P0` `W1`.
> 2. **`PG-03` Count, do not consult.** Every figure in §4 and §7 was counted at
>    **2026-08-18 22:01 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **This document closes the estate's only open CRITICAL finding.** `AUDIT-014` `TS-01` ruled
>    that **no coverage percentage may be quoted at all**. §3 and §4 make one quotable.

---

## 1. Purpose

`06-02` `G4-10` requires *"every v1.0 BRD requirement demonstrated as delivered or formally
superseded"* at Month 18. **That is a traceability query, and until now there was nothing to query
it against.**

`AUDIT-014` `TS-01`, the estate's single **CRITICAL** open finding, states why: three requirement
denominators are in circulation — 2,930, ~2,352 and 3,343 — and *"a coverage percentage computed on
2,930 and one computed on 3,343 differ by roughly 12 points at identical testing, which is more than
enough to move a Go/No-Go."*

**Two things have since changed.** `RQ-001` §3.10.5 counted the requirement population on disk with
a reproducible command and fixed the denominator at **3,347 rows**; `RQ-004` `CV-01` added the 42
`SWR` rows for **3,389** and defined ten coverage measures. **What has never existed is the
document that publishes them** — the report itself, its rules, its cadence, its audience and its
generation.

This is that document, and it is the last of Category 08 because it consumes all ten others.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The denominator and the four publication rules** that make a figure quotable (§3) |
| 2 | **The measured baseline at issue** — what coverage is today, which is zero and stated (§4) |
| 3 | **The measures** — ten requirement measures from `RQ-004`, plus **eight coverage dimensions requirements do not capture** (§5) |
| 4 | **What may not be measured yet**, and when each becomes available (§6) |
| 5 | **The report** — structure, cadence, audience, and the generation pipeline (§7) |
| 6 | **`G4-10`** — the query, and how it is answered (§8) |
| 7 | **Anti-patterns** — the six ways a coverage report misleads (§9) |
| 8 | **Governance** — who may change a measure, and the immutability rule (§10) |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| The requirement set and its denominator | `RQ-001` §3.10.5 | **Consumed. This document never re-derives it** |
| The RTM, its link types and `CV-M1`…`CV-M10` definitions | `RQ-004` §4, §5 | Consumed; this document publishes them and adds §5.3's dimensions |
| Case derivation and the case repository | `QA-003` | The numerator's source |
| Test execution | `QA-002`, `QA-005`…`QA-009` | |
| Defect thresholds | `QA-010` | `DMG-G2` consumes this report |
| Gate outcomes | `GV-009` | This report is an input |
| Content-to-content traceability | `RF-003` | `QA-001` §11.4 ruled this document the **engineering** coverage view |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Steering Committee** | §7.2's gate report — the single page on which a Go/No-Go rests |
| **Wave-gate assessors** | §5.1's `CV-M6`, which is a criterion and not a report |
| Head of Quality Engineering | The instrument behind the gate quality opinion |
| Enterprise Architecture | §3, §8 — denominator custody and the `G4-10` query |
| QA Lead | §7.4 — generation, and what breaks it |
| Implementation vendor and auditors | §9 — the six ways this report could mislead, stated so it does not |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **ISO/IEC/IEEE 29119-3:2021 §11** | The **test completion report** content model — §7.2's structure is its elements plus the coverage triple | **Departure:** published **fortnightly** as well as per gate. A completion report issued only at completion is not a control |
| **ISO/IEC/IEEE 29148:2018 §5.2.8** | Verifiability — a requirement with no case is reported, not assumed covered | None |
| **ISO/IEC 25040:2011** | Evaluation process — measures, criteria, decisions | Applied to the coverage measures |
| **ISO 21502:2020** | Measurement as a defined project practice | None |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `RQ-001` §3.10.5 `CR-01` | **3,347 requirement rows**, counted on disk 2026-08-18 02:15 (+06), with a reproduction command; `CR-02`, `CR-03` |
| `RQ-004` §5 `CV-01`…`CV-04` | **Denominator 3,347 + 42 `SWR` = 3,389**; the triple rule; the wave-scoping rule; **`CV-M1`…`CV-M10`**; `CV-04` making P0 coverage a criterion |
| `RQ-004` §6 | The measured trace integrity at issue — including `verification_method` absent from 3,347 of 3,347 |
| `QA-003` §5, §6 | `tc_id`, the 18 case attributes, and the reconciliation that makes the numerator countable |
| `QA-005` §8.5, §11.3 | `TAF-37` `tc_id` reconciliation; `TAF-61` the normalised result shape |
| `QA-010` | Defect state, which qualifies a *passing* case |
| `GV-009` `GA-04` | *"A percentage carries its denominator"* |
| `QA-001` `MTS-R1` | The triple rule, restated as a non-negotiable |
| `AUDIT-014` `TS-01` | The finding this document closes |
| `06-02` `G4-10` | The query §8 answers |

### 2.3 What this document closes

| Finding | Source | Severity | How | Residual |
|---|---|:--:|---|---|
| **`TS-01`** | `AUDIT-014` | **CRITICAL** | §3 fixes one denominator with its provenance and its reproduction command; §5 defines the measures; §7 publishes them as triples. **`TS-01` closes on the first published report at the Wave 1 gate**, not on this issue | The report must actually issue — `Q-01` |
| `G4-10` unanswerable | `06-02` | — | §8 states the query, its inputs and its answer form | `RQ-003` disposition data |
| `RQ-004` `CV-M5`…`CV-M8` blocked | `RQ-004` §5.3 | — | `QA-003`'s repository supplies the case set they were blocked on | §6 |
| `TS-12` `RF-003` dependency | `AUDIT-014` | Medium | `QA-001` §11.4 ruled this document the consolidated **engineering** coverage view | `RF-006` remains, owned by Content |
| `AF-06` | prior audit | — | §3.2 records `05-01`'s ~2,352 title as superseded by `CR-01` | `05-01` restatement |

---

## 3. The Denominator

### 3.1 The rule

> **`RTC-01`. There is one denominator: 3,389.**
>
> **3,347 adopted requirement rows** (`RQ-001` `CR-01`, counted on disk at 2026-08-18 02:15 (+06))
> **+ 42 `SWR` programme-level software requirements** = **3,389** (`RQ-004` `CV-01`).
>
> **No coverage percentage, completeness claim or effort figure may be published against any other
> denominator** (`CR-02`).

### 3.2 The four superseded figures, recorded so they do not return

| Figure | Where it appears | What it counts | Status |
|---:|---|---|---|
| 1,180 | `05-01` §1.3 total row | The superseded 30-module allocation | **Superseded** — self-declared |
| ~2,352 | `05-01` §1.3a and **its title** | 7 categories measured, 4 estimated | **Superseded** — mixed basis, prohibited for commitment by `RG-05`. Closes `AF-06` |
| 2,930 | `PGD-000`, `README.md`, `02-02` §3, the v2.0 BRD | Provenance not stated | **Superseded** |
| 3,343 | `_MODULE_SET_AUDIT_REPORT` §115/§522; `TS-01` | Provenance not stated | **Superseded** |
| *"2,900+"* | Master Index Category 13 preamble | A rounded form of 2,930 | **Superseded** |
| **3,389** | **`RQ-001` `CR-01` + `RQ-004` `CV-01`** | **Requirement rows counted on disk, plus `SWR`** | **AUTHORITATIVE** |

### 3.3 Why 3,389 and not one of the others

| Property | 3,389 | The others |
|---|:--:|:--:|
| Counted from the filesystem | ✔ | ✘ |
| Reproduction command published | ✔ (`RQ-001` §3.10.5) | ✘ |
| Enumeration timestamp | ✔ 2026-08-18 02:15 (+06) | ✘ |
| Duplicate check run | ✔ — 0 duplicates | ✘ |
| Counting rule stated | ✔ `CR-01` | ✘ |
| Change-controlled | ✔ `CR-03` | ✘ |

**No other figure states its provenance.** That is the whole argument, and it is `PG-03`'s
*"count, do not consult"* applied to the estate's most consequential number.

### 3.4 The four publication rules

| # | Rule | Source |
|---|---|---|
| **`RTC-02`** | **A coverage figure is published as a triple** — *numerator / denominator / enumeration timestamp*. `"78% covered"` is not publishable; `"2,643 / 3,389 at 2027-01-15 09:00 (+06)"` is | `CV-02`; `GA-04`; `MTS-R1` |
| **`RTC-03`** | **A wave-scoped measure states its wave denominator explicitly**, and wave and programme figures never appear in the same column without both denominators | `CV-03` |
| **`RTC-04`** | **The denominator moves only under `RQ-005` change control**, and is re-counted and re-stamped **at every wave gate** with the delta reported | `CR-03`; `BL-04` |
| **`RTC-05`** | **A measure that cannot be computed is published as *not measurable*, with the blocker and the expected date** — never omitted, and never shown as zero | `MTS-R2`; §6 |

> **`RTC-05` is the rule that prevents this report from repeating `TS-01` in a new form.** An omitted
> measure reads as an absent risk; a measure shown as 0% reads as a failure. **Neither is what *not
> yet measurable* means.**

---

## 4. The Measured Baseline at Issue

*Counted at 2026-08-18 22:01 (+06). This is the position the first report will be written against,
and it is published so the first non-zero figure has something to be a delta from.*

| Measure | Numerator | Denominator | Position |
|---|---:|---:|---|
| Requirement rows in the baseline | — | **3,389** | Fixed by `CR-01`/`CV-01` |
| Requirements carrying `verification_method` | **0** | 3,347 | **`RQ-004` §6.3** — the attribute does not exist (`QA-003` §3) |
| Requirements carrying a `source` attribute | **0** | 3,347 | `RQ-004` §6.3 |
| Requirements carrying an `owner` | **0** | 3,347 | `RQ-004` §6.3 |
| Requirements with ≥ 1 linked test case (`CV-M5`) | **0** | 3,389 | No case repository exists until `QA-003` is built |
| Distinct case identifiers in the estate | **620** | ~1,700 executable items | `QA-001` §4.4 — six incompatible schemes |
| Test packs with **no** case identifiers | **3 of 15** | | `TS-013`, `TS-016`, `TS-018` |
| Business objectives cited by ≥ 1 specification | **14** | 18 | `RQ-004` `RQA-17` |
| Specifications citing ≥ 1 objective | **30** | 79 | `RQ-004` §6.2 |
| KPI identifiers registered | **95** | **251 used** | **198 unregistered** |
| Entities catalogued in `05-02` | 434 | **1,370 declared — 1,335 owned** *(recounted 2026-08-19; `AR-008-F-01`)* | `RQ-004` `T-10` |
| Business rules catalogued in `05-05` | 140 | **1,330 in module §9** | 122 overlap |
| Roles registered | `R01`–`R38` | **`R39`–`R50` used** | Unregistered |
| SoD constraints registered | `SOD-01`–`SOD-12` | **`SOD-13`–`SOD-30` used** | Unregistered |
| Environments provisioned | **0** | 7 | `QA-001` §7.1 |

> **Every coverage measure this document defines currently evaluates to zero, and that is the
> honest position.** Publishing it is `RTC-05` applied to the baseline itself: a first report showing
> 62% with no predecessor invites the question *"from what?"*, and the answer needs to exist before
> the question is asked.

---

## 5. The Measures

### 5.1 The ten requirement measures

Defined by `RQ-004` §5.2 and **published by this document**. Not redefined — a second definition is
how `TS-01` happened.

| # | Measure | Formula | Reported to | Cadence |
|---|---|---|---|---|
| `CV-M1` | **Requirement definition coverage** | Requirements passing `RQ-001` `CK-01`…`CK-06` ÷ baseline | PMO | Fortnightly |
| `CV-M2` | **Objective coverage** | `BO-nn` with ≥ 1 reciprocal `T-01` ÷ 18 | Steering Committee | Wave gate |
| `CV-M3` | **Disposition coverage** | Requirements with `fit_gap` ≠ `undetermined` and evidence ÷ baseline | CFO, `GV-007` | Wave gate |
| `CV-M4` | **Design coverage** | Requirements with a resolving `T-04` ÷ requirements at `Allocated` or beyond | Design Authority | Wave gate |
| **`CV-M5`** | **Test coverage** | **Requirements with ≥ 1 `T-07` ÷ baseline** | QA | **Fortnightly** |
| **`CV-M6`** | **Test coverage, `P0`** | As `CV-M5`, restricted to `priority: P0` | **Wave gate** | **Wave gate** |
| `CV-M7` | **Verification coverage** | Requirements with a passing `T-08` ÷ requirements at `Built` or beyond | Wave gate | Wave gate |
| `CV-M8` | **Acceptance coverage** | Requirements at `Accepted` ÷ wave baseline | Steering Committee | Wave gate |
| `CV-M9` | **Trace integrity** | Requirements with zero open `D-1`…`D-4` defects ÷ baseline | Design Authority | Fortnightly |
| `CV-M10` | **Orphan count** | Requirements with no `T-01`, plus objectives with no requirement | Steering Committee | Wave gate |

> **`RTC-06`. `CV-M6` is a gate criterion, not a report** (`CV-04`). **A wave gate at which any `P0`
> requirement has no test case fails, regardless of the aggregate percentage.** Aggregates hide
> exactly the requirements that matter, because `P0`s are **22.7%** of the set and **100% of the
> regulatory exposure**.

### 5.2 What a "covered" requirement means

> **`RTC-07`.** A requirement counts toward `CV-M5` when **≥ 1 case in the `QA-003` repository lists
> it in `requirements`, and that case passes the `TDS-Q1`…`TDS-Q8` quality checks.**
>
> **Four things that do not make a requirement covered:**

| Not coverage | Why |
|---|---|
| A case that mentions the requirement in prose | Only the structured `requirements` field counts (`TDS-Q1`) |
| A case whose expected result is not falsifiable | `TDS-Q3` rejects it |
| A case marked `automated: yes` with no suite | `TAF-37` contradicts it at build time |
| **A case that exists but has never executed** | That is `CV-M5` coverage, **not `CV-M7` verification.** The two are separate measures precisely so this distinction cannot be blurred |

### 5.3 The eight dimensions requirements do not capture

**Requirement coverage is necessary and not sufficient.** Whole populations of test obligation on
this programme are not `FR-` rows, and a report that showed only `CV-M1`…`CV-M10` would show a
system as well covered while its largest risk populations were untested.

| # | Dimension | Numerator | Denominator | Owner | Source |
|:--:|---|---|---:|---|---|
| **`RTC-D1`** | **Denial-cell coverage** | Denied cells with a passing negative test, **UI and API** | **379** | `QA-007` | `05-04` §2; `SC-01` forbids sampling |
| **`RTC-D2`** | **Threat coverage** | `SC-002` threats with ≥ 1 executed case | **97** | `QA-007` | `SC-002` §6 |
| **`RTC-D3`** | **Abuse-case coverage** | Abuse cases executed | **32** | `QA-007` | `SC-002` §8 |
| **`RTC-D4`** | **NFR target coverage** | Numeric targets verified at 1.5× peak | **19** performance + 10 scalability | `QA-006` | `05-06` §1, §3 |
| **`RTC-D5`** | **WCAG criterion coverage, per surface** | Criteria evidenced by a method capable of finding their failure mode (`ACD-27`) | **55 × 13 surfaces** | `QA-008` | `UX-005` §7, §4.2 |
| **`RTC-D6`** | **Hard-rule coverage** | Class `H` rules with a **passing negative** case | Class `H` rules in scope | `QA-002` `LP-3` | `05-05`; `RQ-009`; `LVP-S2` |
| **`RTC-D7`** | **Journey coverage** | `TS-012` scenarios passing | **18 in 20 executions** | `QA-002` `LP-4` | `TS-012` §1.1 |
| **`RTC-D8`** | **Role coverage** | Roles with ≥ 1 executed and **signed** UAT script | **38** | `QA-009` | `05-04` §10 criterion 6 |

Two further measures qualify the whole set:

| # | Measure | Why |
|:--:|---|---|
| **`RTC-D9`** | **Bilingual pass rate** — scripts passed in **both** languages ÷ scripts on bilingual surfaces | `TX-10`; `ACD-20`. A pass recorded in English only is not a pass on a bilingual surface |
| **`RTC-D10`** | **Automation ratio** — automated cases in the permanent regression core ÷ cases in it, per level | `MTS-R8`. Verified by `TAF-37`, not self-reported |

### 5.4 The three that are hard limits, not reports

| Measure | Rule |
|---|---|
| **`CV-M6`** | 100% or the gate fails (`CV-04`, `RTC-06`) |
| **`RTC-D1`** | 100% of the wave's delivered denials, or the roles are not releasable (`05-04` §10 criterion 6) |
| **`RTC-D6`** | 100% of class `H` rules in scope with a passing negative (`LVP-S2`) |

---

## 6. What May Not Be Measured Yet

`RQ-004` §5.3 listed four blocked measures. Restated with what has since changed, and extended to
§5.3's dimensions.

| Measure | Blocked by | Available at | Changed since `RQ-004`? |
|---|---|---|---|
| `CV-M1` | `RQ-001` `CK-01`…`CK-06` need running against the set | **W1** | Computable now |
| `CV-M2`, `CV-M10` | Nothing — measured at `RQ-004` issue | **Now** | ✔ **14/18 and 30/79 published** |
| `CV-M3` | `RQ-003` determination has not started; **3,389 `undetermined`** | W1 gate, W1 scope only | Unchanged |
| `CV-M4` | `AR-003` issued as a standard; **92 of 93 design units remain** (`PGD-A3-08`) | W1 build start | Partially — the standard exists, the units do not |
| **`CV-M5`–`CV-M8`** | **The case repository did not exist** | **W1 build start** | ✔ **`QA-003` specifies it; it must be built** |
| `CV-M9` | The `RQ-004` §7.3 automated checks | On RTM generation | Unchanged |
| **All of `RTC-D1`…`RTC-D10`** | **0 of 7 environments; 38 role accounts absent; no automation framework** | **W1, if `QA-001` `Q-01` is funded** | New |

> **`RTC-08`.** Each blocked measure appears in every report as **`not measurable`**, with its
> blocker and expected date (`RTC-05`). A report that silently omits four of twenty measures is a
> report that overstates coverage by omission — which is the same class of defect as `TS-01`, in a
> new place.

---

## 7. The Report

### 7.1 Cadence and audience

| Report | Cadence | Contents | Audience |
|---|---|---|---|
| **Fortnightly coverage** | Fortnightly | `CV-M1`, `CV-M5`, `CV-M9`, `RTC-D10`, plus execution progress | QA, PMO, Design Authority |
| **Gate coverage report** | **Per wave gate**, at T−2 | **All twenty measures**, as triples, with deltas | **Steering Committee**, gate assessors |
| Level completion report | Per level exit | The level's slice | Gate evidence pack (`QA-001` §11.3) |
| **Programme closure** | W9 | The full set, plus the nine-gate trend | Steering Committee; `G9-04` handover |

### 7.2 Gate report structure

Its elements are 29119-3:2021 §11's, plus the coverage triple.

| § | Content |
|:--:|---|
| 1 | **Denominator statement** — 3,389, its provenance, its re-count at this gate, and the delta since the last (`RTC-04`) |
| 2 | **Wave scope** — the wave's requirement denominator, stated separately (`RTC-03`) |
| 3 | **`CV-M1`…`CV-M10`** — each as a triple, with the delta since the last gate |
| 4 | **`RTC-D1`…`RTC-D10`** — each as a triple |
| 5 | **The three hard limits** (§5.4) — pass/fail, not percentage |
| 6 | **Not measurable** — every blocked measure, its blocker, its expected date (`RTC-08`) |
| 7 | **Not executed** — every level's named non-execution (`MTS-R2`), and every `MTS-X2` exception |
| 8 | **Truncations and conditional acceptances**, cumulative across waves (`DMG-12`, `UAP-39`) |
| 9 | **Defect position** — `QA-010` `DMG-T1`…`T9` status |
| 10 | **`DDP` per level** and escape rate (`DMG-07`) |
| 11 | **`G4-10` position** (§8), from W1 onward — not first attempted at W4 |
| 12 | **Generation metadata** — RTM version, case-repository version, result-set identifier, enumeration timestamp |

### 7.3 The one-page summary

> **`RTC-09`.** The gate report opens with **one page** carrying: the denominator, the three hard
> limits as pass/fail, `CV-M5` and `CV-M6` as triples, the defect threshold status, and the count of
> *not measurable* and *not executed* items.
>
> **A Go/No-Go decision is taken in a meeting, from a summary.** If the summary is not designed, the
> decision is taken from whichever number is most quotable — and that is precisely how a figure on
> 2,930 came to be used interchangeably with one on 3,343.

### 7.4 Generation

| # | Rule |
|---|---|
| `RTC-10` | **The report is generated, not written.** A hand-assembled coverage report goes stale between assembly and reading, and that is `TS-11` and `PGD-A1-03` |
| `RTC-11` | Inputs are exactly four: the **`RQ-004` RTM**, the **`QA-003` case repository**, the **`QA-005` `TAF-61` normalised result set**, and the **`QA-010` defect register** |
| `RTC-12` | **Generation fails loudly.** A missing input produces *not measurable* (`RTC-05`), never a silently smaller denominator |
| `RTC-13` | **Every published report is retained immutably**, with its generation metadata, per `GA-08` — programme life + 5 years |
| `RTC-14` | **The report is reproducible**: re-running the generator against the same four input versions produces the same figures |

---

## 8. `G4-10` — The Query

### 8.1 The criterion

> `06-02` `G4-10`, Month 18: **"Every v1.0 BRD requirement demonstrated as delivered or formally
> superseded."**

`AUDIT-014` `TS-01` called this *"worse"* than the general denominator problem, because it *"is a
traceability query, and there is nothing to query it against."*

### 8.2 The query

```text
FOR each requirement R in baseline(v1.0 scope):
    delivered(R)  ⟺  R.state = Accepted
                     AND ∃ case C : R ∈ C.requirements
                     AND C.last_result = pass
                     AND C.execution ∈ evidence_pack(gate)
    superseded(R) ⟺  R.state = Superseded
                     AND ∃ change_record CR in RQ-005 : CR supersedes R
                     AND CR.approver ≠ null

G4-10 passes ⟺ ∀ R : delivered(R) ∨ superseded(R)
```

### 8.3 What the query needs, and where each comes from

| Input | Source | State at issue |
|---|---|---|
| `baseline(v1.0 scope)` | `RQ-001` `CR-01` + the `wave` attribute | **Available** |
| `R.state` | `RQ-004` RTM lifecycle | Needs the RTM populated |
| `C.requirements` | `QA-003` §6.1 attribute 6 | Needs the repository built |
| `C.last_result` | `QA-005` `TAF-61` | Needs automation and execution |
| `evidence_pack` | `GV-009` `GA-07` | Per gate |
| Change records | `RQ-005` | Available |

### 8.4 The rules

| # | Rule |
|---|---|
| `RTC-15` | **`G4-10` is reported from W1 onward**, not first attempted at W4. A traceability query first run at Month 18 will fail, and there will be no time to fix what it finds |
| `RTC-16` | **A requirement neither delivered nor superseded is named individually** in the gate report. A count is not an answer to *"every requirement"* |
| `RTC-17` | **"Formally superseded" requires an approved `RQ-005` change record.** A requirement quietly dropped is neither delivered nor superseded, and it is the population this criterion exists to expose |
| `RTC-18` | **A requirement `Accepted` on a conditional acceptance is *not* delivered** for `G4-10` (`UAP-38`). It is reported separately, with its remediation date |

---

## 9. Anti-Patterns

Six ways this report could mislead while every figure in it is technically correct. Each is
prohibited by a named rule, so the prohibition is checkable.

| # | Anti-pattern | Prohibited by |
|:--:|---|---|
| 1 | **A percentage without its denominator** — the `TS-01` defect itself | `RTC-02`; `CV-02`; `GA-04`; `MTS-R1` |
| 2 | **Omitting an unmeasurable measure**, so absence reads as no risk | `RTC-05`, `RTC-08` |
| 3 | **Counting a written case as coverage of a passing test** — conflating `CV-M5` with `CV-M7` | §5.2; the two measures are separate for this reason |
| 4 | **Reporting an aggregate that hides `P0`s** — 95% coverage with untested `P0`s | `CV-04`; `RTC-06`; `CV-M6` is a criterion |
| 5 | **A wave figure presented as a programme figure**, or the reverse | `RTC-03`; `CV-03` |
| 6 | **Counting a case that did not execute, or a quarantined test, as coverage** | `MTS-R2`; `TAF-50`; §5.2 |

> **`RTC-19`.** A seventh, subtler than the six: **reporting coverage of requirements while a whole
> `RTC-D` dimension is at zero.** A system with 92% requirement coverage and **0 of 379 denial cells
> tested** is not 92% tested. §5.3 exists so that this cannot be true of any report generated under
> this standard.

---

## 10. Governance

| # | Rule |
|---|---|
| `RTC-20` | **The denominator is Enterprise Architecture's**, moved only under `RQ-005` and re-stamped at every gate (`CR-03`, `RTC-04`) |
| `RTC-21` | **A measure's definition is changed only by a `GV-003` decision**, and the change is stated on every subsequent report **for three gates**, so a trend break is never mistaken for a real movement |
| `RTC-22` | **A published report is never amended.** A correction issues as a new report with the correction stated. `RTC-13`'s immutability is what makes a trend meaningful |
| `RTC-23` | **The Head of Quality Engineering owns the report; Enterprise Architecture owns the denominator.** Separating them is deliberate: the party reporting coverage does not control what it is a fraction of |
| `RTC-24` | **A measure showing an implausible improvement is investigated before publication.** Coverage rising 30 points in a fortnight is a data change or a definition change, not a testing achievement |

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-011-D-01` | The denominator | (a) 2,930; (b) 3,343; (c) **3,389**; (d) defer to a reconciliation exercise | **(c)** | It is the only figure with a counting rule, a reproduction command, a duplicate check and a timestamp. **No other figure states its provenance** | **Closes `TS-01`** on first publication; `05-01`'s title and the README require restatement |
| `QA-011-D-02` | Whether to redefine the measures | (a) redefine here; (b) **consume `RQ-004` `CV-M1`…`CV-M10` unchanged and add `RTC-D1`…`RTC-D10`** | **(b)** | A second definition of a measure is how `TS-01` happened. Adding dimensions is not redefining measures | §5.1 consumed, §5.3 added |
| `QA-011-D-03` | Whether requirement coverage is sufficient | (a) report `CV-M*` only; (b) **add eight non-requirement dimensions** | **(b)** | 379 denial cells, 97 threats, 55 WCAG criteria × 13 surfaces and 19 NFR targets are **not `FR-` rows**, and a report omitting them would show a well-covered system with its largest risk populations untested | `RTC-D1`…`RTC-D10`; `RTC-19` |
| `QA-011-D-04` | Blocked measures | (a) omit; (b) show as 0%; (c) **publish as *not measurable* with blocker and date** | **(c)** | Omission reads as no risk; 0% reads as failure. Neither is what *not yet measurable* means | `RTC-05`, `RTC-08` |
| `QA-011-D-05` | Report production | (a) hand-assembled; (b) **generated from four named inputs, reproducibly** | **(b)** | A hand-assembled report goes stale between assembly and reading — `TS-11`, `PGD-A1-03` | `RTC-10`…`RTC-14` |
| `QA-011-D-06` | `G4-10` timing | (a) first attempt at W4; (b) **report from W1** | **(b)** | A traceability query first run at Month 18 will fail with no time to fix what it finds | `RTC-15` |
| `QA-011-D-07` | Ownership split | (a) one owner; (b) **QE owns the report, EA owns the denominator** | **(b)** | The party reporting coverage should not control what it is a fraction of | `RTC-23` |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Is the first gate coverage report produced at the W1 gate?** `TS-01` closes on publication, not on this issue | Head of Quality Engineering | **W1 gate** | **`TS-01` closure**; `G1` assessment |
| `Q-02` | Are `05-01`'s title, the README and `_MODULE_SET_AUDIT_REPORT` restated to 3,389? | Enterprise Architecture | **W1** | §3.2; closes `AF-06` |
| `Q-03` | Who builds the generator, and against which four input stores? | QA Lead with Platform Engineering | **W1** | `RTC-10`…`RTC-14`; the entire report |
| `Q-04` | When does `RQ-003` disposition begin, so `CV-M3` leaves *not measurable*? | Enterprise Architecture with CFO | **W1** | `CV-M3`; the cost model |
| `Q-05` | Are the 198 unregistered KPI identifiers and the unregistered `R39`–`R50` / `SOD-13`–`SOD-30` resolved, or reported as permanent exclusions? | Enterprise Architecture | **W2** | §4's baseline; `RTC-D8` |
| `Q-06` | Is `RTC-D5` (55 criteria × 13 surfaces) computable, given `TS-016` currently scripts 9 surfaces? | Content Design Lead | **W2** | `QA-008` `Q-03`; `ACD-05` |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Exactly one denominator is published, with provenance, reproduction and timestamp | §3.1, §3.3 — **3,389** |
| `AC-02` | Every superseded figure is recorded so it does not return | §3.2 — 5 superseded |
| `AC-03` | Four publication rules make a figure quotable | §3.4 — `RTC-02`…`RTC-05` |
| `AC-04` | The measured baseline at issue is published, including the zeros | §4 — 15 rows |
| `AC-05` | `RQ-004`'s ten measures are consumed, not redefined | §5.1 |
| `AC-06` | Eight non-requirement dimensions are defined with numerator, denominator and owner | §5.3 — `RTC-D1`…`RTC-D8`, plus `D9`, `D10` |
| `AC-07` | The three hard limits are distinguished from reported measures | §5.4 |
| `AC-08` | Every unmeasurable measure has a blocker and a date | §6 |
| `AC-09` | The gate report has a defined structure and a designed one-page summary | §7.2, §7.3 |
| `AC-10` | `G4-10` is expressed as an executable query with named inputs | §8.2, §8.3 |
| `AC-11` | Six anti-patterns are named, each prohibited by a cited rule | §9 |
| `AC-12` | The report is generated, reproducible and immutable | §7.4, `RTC-22` |

**Definition of done.** Complete when every criterion is met, the generator produces the first
report from the four inputs, that report is published at the Wave 1 gate, and the approver has
signed. **`AUDIT-014` `TS-01` closes on that publication.** Approval carries the `PGD-A1-09`
qualification.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-001` §3.10.5 | The denominator and its counting rule |
| Upstream | `RQ-004` §5 | `CV-01`…`CV-04` and the ten measures |
| Upstream | `QA-003` | The case repository — the numerator's source |
| Upstream | `QA-005` §11.3 | The normalised result set |
| Upstream | `QA-006`, `QA-007`, `QA-008`, `QA-009` | `RTC-D1`…`RTC-D8` numerators |
| Upstream | `QA-010` | Defect state qualifying a passing case |
| Downstream | `GV-009` | The gate coverage report is gate evidence |
| Downstream | `QA-010` `DMG-G2` | Consumes `CV-M6` |
| Downstream | `RL-003` | Go-live readiness consumes coverage evidence |
| Downstream | `BM-002` | Benefits measurement consumes the objective coverage measure |
| Lateral | `RF-003` | Content-to-content traceability; **this document is the engineering view** (`QA-001` §11.4) |
| Lateral | `../../project_content/_AUDIT/AUDIT-014` | `TS-01`, closed on first publication |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-003_Test_Design_Specification_and_Case_Repository.md` · `./QA-005_Test_Automation_Framework_Specification.md` ·
`./QA-006_Performance_and_Load_Test_Plan.md` · `./QA-007_Security_Test_Plan.md` ·
`./QA-008_Accessibility_Test_Plan.md` · `./QA-009_UAT_Plan_and_Business_Sign_off_Protocol.md` ·
`./QA-010_Defect_Management_and_Quality_Gate_Standard.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../01_Requirements_Engineering/RQ-001_Software_Requirements_Specification.md` ·
`../01_Requirements_Engineering/RQ-004_Requirements_Traceability_Matrix.md` ·
`../01_Requirements_Engineering/RQ-005_Requirements_Management_Plan.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §2 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §4 ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
ISO/IEC/IEEE 29119-3:2021 §11 · ISO/IEC/IEEE 29148:2018 §5.2.8 · ISO/IEC 25040:2011 · ISO 21502:2020

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Quality Engineering with Enterprise Architecture | Initial issue. **Fixes one denominator — 3,389 — with its provenance, reproduction command and timestamp, and records all five superseded figures so they cannot return**; four publication rules making a figure quotable; **the measured baseline at issue, published including its zeros**, so the first non-zero figure has a delta to be measured from; `RQ-004`'s ten measures consumed unchanged and **eight non-requirement dimensions added** — 379 denial cells, 97 threats, 32 abuse cases, 29 NFR targets, 55 WCAG criteria × 13 surfaces, hard rules, journeys and 38 roles — because a requirement-only report would show a well-covered system with its largest risk populations untested; three hard limits distinguished from reported measures; every unmeasurable measure published **with a blocker and a date** rather than omitted; a generated, reproducible, immutable report with a designed one-page summary; **`G4-10` expressed as an executable query, reported from W1 rather than first attempted at Month 18**; and six named anti-patterns, each prohibited by a cited rule. **Closes `AUDIT-014` `TS-01` on first publication** | *Pending — `GV-002`* |

---

*`QA-011` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
