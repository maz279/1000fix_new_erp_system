---
id: BM-002
title: KPI Baseline Measurement Report
category: 15 — Benefits, Measurement & Assurance
code: BM
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer with the Programme Director
approver: ERP Steering Committee, on the recommendation of the CFO
standards_basis: >
  ISO/IEC/IEEE 15939:2017 (measurement process — the measurement information model,
  clauses 6.2–6.4) · ISO 21502:2020 §7.13 (benefits management) ·
  ISO 21503:2022 (programme management — benefits) · MSP 5th edition (benefits management
  theme; baseline before transition) · ISO 9001:2015 §9.1 (monitoring, measurement, analysis) ·
  ISO/IEC 25040:2011 (evaluation process)
traces_to: >
  PGD-000 BM-002 · AUDIT-015 RP-01 (CRITICAL — 250 KPI identifiers against 95 registered) ·
  AUDIT-015 RP-02 (CRITICAL — 44 of 95 baselines absent) · 06-02 §6 ("a KPI without a baseline
  cannot claim a benefit") · RL-005 §7.3 PIR-27 / RLA-09 (no wave review may claim any benefit
  until this document issues) · GV-001 CC-09 · D-018 · CO-003 SOW-27 · CO-005 §10.1 ·
  RP-015 §4.3, §4.5, §4.8 · RP-001 §4.1, §4.2, §4.3 · 00-07 H2-04, H2-10 · 00-06 M-03, M-04
depends_on: DA-007 (metric definitions) · RP-001 (KPI dictionary) · RP-015 (baseline register) · GV-011 (evidence custody) · SP-002 (as-is process baselines)
verified_on: 2026-08-19
enumeration_timestamp: 2026-08-19 00:48 (+06)
priority: P0
needed_by: Now
rule_space: BMR
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BM-002 — KPI Baseline Measurement Report

### Category 15 · Code `BM` · Rule space `BMR` · ISO/IEC/IEEE 15939:2017 · ISO 21502:2020 §7.13 · MSP 5th edition

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `BM-002` exists in `PGD-000` Category 15, status ⛔, `P0`,
>    `needed_by: Now`.
> 2. **`PG-03` Count, do not consult.** Every figure in §3, §4 and §9 was **counted from the
>    filesystem at 2026-08-19 00:48 (+06)**, with the reproduction command printed beside it. No
>    figure in this document is quoted from another document's description of itself — including
>    from the audit finding that commissioned it.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** `verified_on: 2026-08-19`.
>
> **This document releases a programme-wide stop.** `RL-005` `PIR-27` rules that *"until `BM-002`
> issues, no wave review can claim any benefit at all."* That stop is not lifted by this document
> existing. It is lifted **per KPI, on signature of that KPI's baseline record** (§8.4). This
> document is the instrument, the schedule and the standard — not the measurement.

---

## 1. Purpose

`06-02` §6 contains the rule the entire benefit case rests on:

> *"Every KPI's baseline is measured and signed off **before** the relevant wave begins. **A KPI
> without a baseline cannot claim a benefit.**"*

The programme wrote that rule and then built a **BDT 876 lac** annual benefit case without
measuring the baselines. `RL-005` converted the consequence into an operating rule — `PIR-27`, no
wave review may claim any benefit at all — and `CO-005` §10.1 priced it.

**This document exists because that position is recoverable, and only for a limited time.** A
baseline is a measurement of the world *before* the system changes it. Wave 1 go-live destroys the
measurable "before" state for every process it touches. Every week of delay permanently forecloses
part of the benefit case — not by making it smaller, but by making it **unprovable**, which under
`06-02` §6 is the same thing.

It does three jobs:

| # | Job | Where |
|---|---|---|
| 1 | **State the true baseline position**, counted rather than quoted — including a correction to the audit finding that commissioned this document | §3 |
| 2 | **Specify the measurement programme** — what is measured, by whom, by what method, against which wave deadline, and what is recorded when a measurement is no longer possible | §4–§6 |
| 3 | **Define the record, the signature and the release** that lifts `PIR-27` for one KPI | §7, §8 |

**What this document is not.** It is not the measurements. It is `version 1.0` of a report whose
data section fills as measurement proceeds; §8.6 defines the reissue cadence. Issuing the standard
and the schedule now, with an honest empty data set, is what allows measurement to start — and
starting is the entire point.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The counted baseline position** across all 95 registered KPIs, and the correction to `RP-02` (§3) |
| 2 | **Classification** of every KPI into the measurability classes `A`–`D`, with counts (§4) |
| 3 | **The measurement exercises** — the four standing exercises carried from `RP-015` §4.5, plus three this document adds (§5) |
| 4 | **The schedule**, wave-anchored, with the foreclosure dates (§6) |
| 5 | **The baseline record schema**, evidence custody and sign-off protocol (§7, §8) |
| 6 | **The `PIR-27` release mechanism** — per KPI, not per document (§8.4) |
| 7 | **The identifier reconciliation** — 250 in use against 95 registered — so far as baselines depend on it (§9) |
| 8 | **Governing rules** `BMR-01`…`BMR-18` (§10) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The metric **definitions** — the eighteen fields | `RP-001` §4.1; `DA-007` | **Consumed. A baseline against an undefined metric is not a baseline** (`BMR-02`), so this document sequences definition immediately before measurement but never authors it |
| The **targets** | `06-02` §2 | This document does not renegotiate a single target. It records what each can and cannot be measured against |
| The **benefit model** and its BDT values | `06-02` §3.1; `BM-003` | Consumed |
| **NPV, IRR, discounting, FX policy** | `BM-003` | Explicitly deferred; this document produces the measured inputs `BM-003` consumes |
| **Benefit ownership and the miss rule** | `BM-004` | This document names the benefit line a baseline supports; `BM-004` names who is accountable for delivering it |
| **Ratifying the 196 unregistered identifiers** | `RP-001` `O-01`; Enterprise Architecture | §9 states the position and its effect on baselines; it does not allocate |
| **Process-level as-is measurement** | `SP-002` | `BL-01` / `BMR-05` — reused and cited, never re-measured |
| **Adoption measures** | `CH-004` | A different question: adoption measures whether the system is used, not what the world was like before it |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **ERP Steering Committee** | §3.7 and §6.4 — the decision on whether to fund and schedule measurement before W1, which is a business-time decision, not a content one |
| **CFO** | §8.3 — the signature that makes a baseline claimable, and §3 for what is at stake |
| **Programme Director** | §6 — the schedule, and the foreclosure dates that cannot move |
| **Benefit owners** (`06-02` §3.5) | §5 — the exercise they personally must run, and §7 — what they are signing |
| **BI Lead** | §4.3, §9 — the definition-before-measurement sequence, and publication to `RP-001` field 16 |
| **Wave-gate assessors, `RL-005` reviewers** | §8.4 — whether `PIR-27` is released for the KPI in front of them |
| **Internal audit, Month 42 benefits audit** | §7.2 field 5 (basis) and §8.5 (evidence custody) — the fields the audit will actually read |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC/IEEE 15939:2017** | §6.2–§6.4, measurement information model | §7.2's record is the standard's chain made concrete: *information need* → *measurable concept* → *entity and attribute* → *base measure* → *derived measure* → *indicator* → *decision criteria*. §7.3 maps each schema field to its element | **Departure:** the standard assumes measurement is designed before the system. Here the system is designed and the measurement is retrofitted, so §4's classification of what is **no longer measurable** is an addition the standard does not contemplate |
| **ISO 21502:2020** | §7.13 benefits management | Baselines are a named input to benefit realisation; measurement precedes transition | None |
| **ISO 21503:2022** | Programme benefits management | The benefit-to-baseline-to-owner chain | None |
| **MSP 5th edition** *(PeopleCert; current edition, verified 2026-08-19)* | Benefits management theme | MSP's rule that a benefit profile carries a **measured** baseline, and that measurement occurs **before the transition that changes it** | **Departure:** MSP assumes a benefits map precedes the blueprint. `BM-004` builds the map after the blueprint; §4.1 class `C` is how that inversion is recorded honestly rather than concealed |
| **ISO 9001:2015** | §9.1.1 | What is measured, by what method, when, and by whom | None |
| **ISO/IEC 25040:2011** | Evaluation process | Applied to the confidence grading in §7.4 | None |

> **Why ISO/IEC/IEEE 15939 and not a benefits standard alone.** MSP and ISO 21503 say a baseline
> must exist. Neither says what a baseline *record* must contain to be defensible eighteen months
> later in front of an auditor. 15939 does, because it was written for exactly the failure mode
> this programme is in: numbers that are collected but not interpretable, because the population,
> the method and the information need were never recorded alongside them.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `06-02` §2 | `../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` | The **95 registered KPIs** and their baseline column — the primary subject of §3 |
| `06-02` §3.1, §3.5, §6 | same | The 14 benefit lines, their owners, and the rule this document serves |
| `RP-015` §4.2–§4.8 | `../../project_content/14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md` | The 13-field schema, the `A`–`D` classes, the four standing exercises `B1`–`B4`, rules `BL-01`…`BL-12`, and the by-benefit-line position |
| `RP-001` §4.1–§4.3 | `../../project_content/14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md` | The eighteen-field metric definition, the reconciled identifier space, and the allocated ranges |
| `AUDIT-015` `RP-01`, `RP-02` | `../../project_content/_AUDIT/AUDIT-015_Category_14_RP_Content_Audit.md` | The two CRITICAL findings this document addresses — **and, in `RP-02`'s case, corrects** (§3.4) |
| `RL-005` §7.1–§7.3 | `../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md` | `PIR-22`…`PIR-27` — what a wave review may claim, and the stop this document releases |
| `CO-005` §10.1 | `../14_Commercial_Vendor_and_Contract/CO-005_Total_Cost_of_Ownership_Model.md` | The claimed / claimable split at the verified FX rate |
| `DA-007` | `../03_Data_and_Information_Architecture/DA-007_Analytical_and_Dimensional_Model_Specification.md` | The dimensional model whose grain a baseline must match |
| `SP-002` | `../../project_content/…` | Process-level as-is measurements to be reused, never duplicated (`BMR-05`) |

### 2.3 Audit findings this document closes, raises or corrects

| Finding | Source | Disposition |
|---|---|---|
| `RP-02` **CRITICAL** — 44 of 95 baselines absent | `AUDIT-015` | **Advanced and corrected, not closed.** The numerator 44 is confirmed by independent count. The denominator is wrong: 27 of the 95 rows carry no baseline column at all, so the true position is **71 of 95**. §3.4. Closes on the last signed baseline, not on this issue |
| `RP-01` **CRITICAL** — 250 identifiers against 95 registered | `AUDIT-015` | **Confirmed by independent count** (§9.1) and its baseline consequence stated. Ratification remains `RP-001` `O-01`, Enterprise Architecture |
| `RLA-09` / `PIR-27` **HIGH** — no benefit claimable | `RL-005` §7.3 | **Release mechanism defined** (§8.4). Releases per KPI on signature; fully discharged when every wave-scoped KPI is signed |
| `H2-10` — one absolute target with no baseline, recorded *Fixed* | `00-07` | **Reopened.** §3.5 shows the register-wide position is 71, so a finding closed at n=1 was closed against a defect of n=71 |
| `M-03`, `M-04` — M31's 11 KPIs unregistered; M02–M06 KPIs shown as "—" | `00-06` | Confirmed as instances of `RP-01`; §9.3 |
| **`BMR-F-01`** *(new, HIGH)* | This document | `RP-02` states a correct numerator against a wrong denominator, and its complement ("51 numeric or genuine zero") counts 27 column-less rows as baselined. §3.4 |
| **`BMR-F-02`** *(new, HIGH)* | This document | **Only 15 of 95 KPIs have both a usable baseline and a module specification that produces the metric**; only 8 have a *precise* value and a producing module. Neither figure exists anywhere in the estate. §3.5 |
| **`BMR-F-03`** *(new, MEDIUM)* | This document | `RP-015` §4.3's class counts sum to 44 and are therefore scoped to the wrong population; §4.2 restates them against 71 |
| **`BMR-F-04`** *(new, MEDIUM)* | This document | `RP-015` §4.8's "roughly BDT 396 lac" understates the improvement-benefit exposure. The eight improvement lines total **BDT 542 lac**; three lines with the weakest baselines of all are omitted from the 396. §3.7 |
| **`BMR-F-05`** *(new, MEDIUM)* | This document | Nine KPIs have a usable baseline but **no module specification produces them** — measured metrics the system is not specified to compute. §3.6 |

---

## 3. The Counted Position

> **`BMR-01`. Every figure in this section is counted from `06-02` at 2026-08-19 00:48 (+06), with
> its command printed.** A baseline report that quotes another document's count of baselines has
> already failed at its own subject.

### 3.1 The register is 95, and it is three different tables

`06-02` §2 presents one register. It is structurally three, and the difference is the whole finding.

```bash
F=1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md
awk '/^### 2\./{s=$0} /^\| ID \|/{print s"  ==>  "$0}' "$F"
```

| Subsection | KPI range | Rows | Column 3 | Carries a baseline? |
|---|---|---:|---|:--:|
| §2.1 Service Delivery | `KPI-001`…`010` | 10 | `Baseline` | **Yes** |
| §2.2 Field Operations | `KPI-011`…`019` | 9 | `Baseline` | **Yes** |
| §2.3 Customer | `KPI-020`…`027` | 8 | `Baseline` | **Yes** |
| §2.4 Commercial | `KPI-028`…`036` | 9 | `Baseline` | **Yes** |
| §2.5 Warranty & Claims | `KPI-037`…`041` | 5 | `Baseline` | **Yes** |
| §2.6 Supply Chain | `KPI-042`…`049` | 8 | `Baseline` | **Yes** |
| §2.7 Financial | `KPI-050`…`058` | 9 | `Baseline` | **Yes** |
| §2.8 People & Quality | `KPI-059`…`068` | 10 | `Baseline` | **Yes** |
| | | **68** | | |
| §2.9 New Business Lines | `KPI-069`…`084` | 16 | **`Target`** | **No column exists** |
| §2.10 Platform | `KPI-085`…`095` | 11 | **`Target`** | **No column exists** |
| | | **27** | | |
| **Total** | `KPI-001`…`KPI-095` | **95** | | **68 of 95** |

**Verification**: 10 + 9 + 8 + 9 + 5 + 8 + 9 + 10 = **68** ✓ · 16 + 11 = **27** ✓ ·
68 + 27 = **95** ✓ · `grep -c "^| KPI-" "$F"` → **95** ✓ ·
`grep -o "KPI-[0-9]\{3\}" "$F" | sort -u | wc -l` → **95** distinct ✓.

> **§2.9 and §2.10 do not have unmeasured baselines. They have no baseline field.** Twenty-seven
> KPIs — 28% of the register — were specified in a table shape with nowhere to record one. This is
> not an omission an author could notice while filling rows in; it is a defect in the table's
> columns, and it is invisible to any check that reads rows rather than headers.

### 3.2 Of the 68 that have the field, 44 do not have a value

```bash
sed -n '45,152p' "$F" | grep "^| KPI-" | awk -F'|' '{b=$4; gsub(/^ *| *$/,"",b); print b}' \
  | sort | uniq -c | sort -rn
```

| Placeholder in the baseline column | Count |
|---|---:|
| `unmeasured` | **28** |
| `unknown` | **5** |
| `manual` | **4** |
| the literal word `baseline` | **3** |
| `untracked` | **2** |
| `n/a` | **2** |
| **No usable baseline** | **44** |
| A value of some kind | **24** |
| **Rows carrying the field** | **68** |

**Verification**: 28 + 5 + 4 + 3 + 2 + 2 = **44** ✓ · 68 − 44 = **24** ✓.

**The 44 is confirmed.** `AUDIT-015` `RP-02` reported exactly this number and this breakdown, and
an independent count reproduces it line for line. The finding's extraction was sound.

### 3.3 Of the 24 with a value, 9 are not measurements

A range or an approximation is not a baseline under `BL-02`/`BL-03`, because it cannot be compared
to a system-computed figure without an argument about which end of the range to use.

| Class | Count | Identifiers and values |
|---|---:|---|
| **Precise value** — a single number, including a genuine zero | **15** | `KPI-001` 20% · `KPI-004` 70% · `KPI-012` 55% · `KPI-013` 0% · `KPI-016` 0% · `KPI-020` 3.8/5 · `KPI-022` 40% · `KPI-025` 0% · `KPI-026` 0% · `KPI-028` 60% · `KPI-035` 0% · `KPI-042` 75% · `KPI-053` 0% · `KPI-059` 3 days · `KPI-065` 0% |
| **Approximation or range** | **9** | `KPI-010` ~10 min · `KPI-011` 4–5 · `KPI-014` ~35% · `KPI-023` ~15% · `KPI-037` ~50% at 30–90 days · `KPI-038` 15–20% · `KPI-040` 60–120 · `KPI-050` 15–20 days · `KPI-054` ~3–7 days |

**Verification**: 15 + 9 = **24** ✓.

> **None of the 24 — precise or approximate — carries a method, a date, a source, a sample size or
> a signature.** `RP-015` §4.2 field 5 states why that matters: *"a baseline of '70% first-time
> fix' is worthless without 'measured over 1,200 closed jobs across 6 branches, March–May 2026…'
> because that method must match `RP-001`'s definition or the comparison is invalid."* Under
> `BMR-03` all 24 are therefore **provisional** and must be evidenced or re-measured before they
> may be signed. Seven of the fifteen precise values are genuine zeros (class `D`) and are the
> cheapest to evidence, because the evidence is that the capability does not exist.

### 3.4 `BMR-F-01` — the finding that commissioned this document has a wrong denominator

**Severity: HIGH · Status: OPEN · Owner: Enterprise Architecture with the BI Lead**

`AUDIT-015` `RP-02` is titled *"44 of 95 KPI baselines are absent"* and tabulates:

| `RP-02` as published | Count |
|---|---:|
| "No usable baseline" | 44 — **46%** |
| "Numeric or genuine zero" | **51** |

**The numerator is right and the denominator is wrong.** The 44 were counted from a column that
exists on **68** rows. The complement of 44 in that population is **24**, not 51. The figure 51 is
95 − 44, which silently assigns a baseline to all 27 rows that have no baseline field at all.

| | `RP-02` | **Counted** |
|---|---:|---:|
| Registered KPIs | 95 | 95 |
| Rows carrying a baseline field | *(not stated)* | **68** |
| No usable baseline, of those carrying the field | 44 | **44** ✓ |
| Rate against the correct denominator | *"46%"* | **65%** |
| Rows with no baseline field at all | *(not counted)* | **27** |
| **KPIs with no usable baseline** | *(implied 44)* | **71 of 95 — 75%** |
| KPIs with a value of any kind | *(implied 51)* | **24 — 25%** |

**Verification**: 44 ÷ 68 = 0.647 → **65%** ✓ · 44 + 27 = **71** ✓ · 71 ÷ 95 = 0.747 → **75%** ✓ ·
95 − 71 = **24** ✓ · `RP-02`'s 51 = 95 − 44 ✓, confirming the denominator substitution.

**Why this is HIGH and not a clerical note.** `CO-005` §10.1 prices the claimable benefit using
*"`RP-02`: 44 of 95"* as its ratio. `RL-005` `PIR-27`, `GV-001` `CC-09`, the Category 15 overview
and `PGD-000` itself all restate "44 of 95". **The estate has a single shared understanding of the
size of this problem, and it is about 60% of the true size.**

> **This is the `PGD-A2-24` defect class** — a correct total concealing a wrong component —
> occurring inside the audit function itself, which is the exposure `GV-010` was written for and
> `AUDIT-019` named as *"1 critical, against the auditor's own authoring."*

**Remediation.** `RP-02` is **restated, not closed** — its extraction was sound and its conclusion
directionally right. `CO-005` §10.1's claimable split is recomputed by `BM-003` §7 on the corrected
population. Every document quoting "44 of 95" is corrected at its next issue; the list is §9.4.

### 3.5 `BMR-F-02` — the number that actually gates a benefit claim is 15

**Severity: HIGH · Status: OPEN · Owner: CFO with the BI Lead**

`06-02` §6 requires a baseline. A baseline alone does not deliver a benefit claim. A claim under
`RL-005` `PIR-22` needs **three** things: a signed baseline, a movement **measured from the
system**, and a documented causal mechanism. The second requires that some module actually computes
the metric.

```bash
# KPIs that any module or portal specification actually uses
grep -rho "KPI-[0-9]\{3\}" 1000fix_ERP_Module/03_Modules/ \
     1000fix_ERP_Module/04_Portals_and_Applications/ | sort -u > used.txt
```

| Position | Count | % of 95 |
|---|---:|---:|
| Registered in `06-02` §2 | 95 | 100% |
| …carrying a baseline field | 68 | 72% |
| …with a value of any kind | 24 | 25% |
| …with a **precise** value | 15 | 16% |
| Registered **and** used by at least one specification | 54 | 57% |
| **Usable baseline AND a producing specification** | **15** | **16%** |
| **Precise baseline AND a producing specification** | **8** | **8%** |

**The 15**: `KPI-001` `KPI-004` `KPI-010` `KPI-011` `KPI-012` `KPI-013` `KPI-014` `KPI-016`
`KPI-023` `KPI-025` `KPI-038` `KPI-042` `KPI-050` `KPI-053` `KPI-054`.

**The 8** *(precise and produced)*: `KPI-001` `KPI-004` `KPI-012` `KPI-013` `KPI-016` `KPI-025`
`KPI-042` `KPI-053`.

**Verification**: of the 24 valued, 15 appear in `used.txt` and 9 do not ✓ · of the 15 precise, 8
appear and 7 do not ✓ · 8 + 7 = **15** ✓ · 15 + 9 = **24** ✓.

> **Eight of ninety-five.** On the day this document issues, eight registered KPIs have a precise
> "before" number and a specified system component that will produce the "after". That is the
> honest size of the programme's measurement readiness, and no document in the estate has stated
> it.

### 3.6 `BMR-F-05` — nine measured metrics the system is not specified to compute

**Severity: MEDIUM · Status: OPEN · Owner: Enterprise Architecture**

The nine with a value but no producing specification:

| KPI | Metric | Baseline | Benefit line it serves | BDT lac |
|---|---|---|---|---:|
| `KPI-020` | CSAT | 3.8/5 | Customer retention | 78 |
| `KPI-022` | Online booking rate | 40% | *(none directly)* | — |
| `KPI-026` | AI first-contact resolution | 0% | Administrative labour savings | 62 |
| `KPI-028` | AMC/RAMC renewal rate | 60% | **AMC/RAMC renewal uplift** | **72** |
| `KPI-035` | Referral-attributed new customers | 0% | Customer retention | 78 |
| `KPI-037` | Claims submitted within 72 h | ~50% at 30–90 d | **Warranty revenue recovery** | **100** |
| `KPI-040` | Days from service to reimbursement | 60–120 | Warranty revenue recovery | 100 |
| `KPI-059` | Payroll processing time | 3 days | Administrative labour savings | 62 |
| `KPI-065` | Employee self-service adoption | 0% | Administrative labour savings | 62 |

`KPI-028` and `KPI-037` are named in `RP-015` §4.8 as **principal KPIs** of two benefit lines worth
**BDT 172 lac** between them, and neither is used by any module or portal specification.

**Verification**: 72 + 100 = **172** ✓.

**The likely cause is not that the metric is unbuilt.** It is that the owning module allocated one
of the 196 unregistered identifiers (§9) for the same metric, because `06-02` §2 had no room. That
is a reconciliation task, not a build task — but until it is done, these nine cannot be traced from
target to producing component, and `BMR-11` therefore blocks any benefit claim resting on them.
Raised to Enterprise Architecture against `RP-001` `O-01`.

### 3.7 `BMR-F-04` — the improvement-benefit exposure is BDT 542 lac, not 396

**Severity: MEDIUM · Status: OPEN · Owner: CFO**

`RP-015` §4.8 assesses all 14 benefit lines, then concludes that the weakest total *"roughly BDT
396 lac of the 876"*. Summing §4.8's own table by the classification it itself assigns:

| Line | BDT lac | `RP-015` §4.8 position | Needs a baseline? |
|---|---:|---|:--:|
| Warranty revenue recovery | 100 | **Weak** | Yes |
| Technician productivity | 130 | **Partial** | Yes |
| Inventory cost reduction | 34 | **Partial** | Yes |
| Administrative labour savings | 62 | **Weak** | Yes |
| Customer retention | 78 | **Partial** | Yes |
| AMC/RAMC renewal uplift | 72 | **Partial** | Yes |
| Financial close & cash flow | 26 | **Weak** | Yes |
| Dynamic pricing margin uplift | 40 | **Partial** — *"'baseline', i.e. indexed to itself"* | Yes |
| **Improvement benefits — need a measured baseline** | **542** | | |
| Managed services (MSP) | 95 | Class `C` | No |
| Rental gross margin | 48 | Class `C` | No |
| Refurbishment & resale margin | 65 | Class `C` | No |
| Marketplace commission | 84 | Class `D` | No |
| Data services | 30 | Class `C` | No |
| E-waste material recovery | 12 | Class `C`/`D` | No |
| **New-business absolutes — need none** | **334** | | |
| **Total** | **876** | | |

**Verification**: 100 + 130 + 34 + 62 + 78 + 72 + 26 + 40 = **542** ✓ ·
95 + 48 + 65 + 84 + 30 + 12 = **334** ✓ · 542 + 334 = **876** ✓ ·
`RP-015`'s 396 = 100 + 62 + 26 + 130 + 78 ✓ — the five lines it names, counting productivity and
retention **in full** while describing them as *"parts of"*.

**What the 396 leaves out is the worst of it.** Inventory (34), AMC/RAMC renewal (72) and dynamic
pricing (40) — **BDT 146 lac** — are excluded from the 396, yet all three depend on improvement
against a prior state, and two carry the weakest baselines in the register: `KPI-029` contract base
and `KPI-033` gross margin both record the literal word *"baseline"*, meaning the metric is indexed
to itself and the improvement is **arithmetically unmeasurable**, not merely unmeasured.

**Verification**: 34 + 72 + 40 = **146** ✓ · 396 + 146 = **542** ✓.

> **Restated for the Board: BDT 542 lac of the 876 — 62%, not 45% — is improvement benefit that
> requires a measured "before".** `BM-003` §7 carries this figure into the claimable computation.

### 3.8 The position in one table

| Statement | Figure |
|---|---:|
| Registered KPIs | **95** |
| With a usable baseline | **24 (25%)** |
| With a precise baseline | **15 (16%)** |
| With a usable baseline **and** a producing specification | **15 (16%)** |
| With a precise baseline **and** a producing specification | **8 (8%)** |
| With **no** usable baseline | **71 (75%)** |
| Improvement benefit requiring a measured baseline | **BDT 542 lac (62% of 876)** |
| New-business absolutes requiring none | **BDT 334 lac (38%)** |
| Benefit claimable today under `06-02` §6 and `PIR-22` | **BDT 0** |

> **The last row is the one to read.** Not a reduced benefit, not a provisional one — zero, because
> `PIR-27` is a precondition rather than a quality standard, and no baseline in the register has
> been signed. §8.4 is how that changes.

---

## 4. Classification

### 4.1 The four classes, carried from `RP-015` §4.3

| Class | Means | Treatment | Who decides |
|:--:|---|---|---|
| **`A`** | **Measurable now** — data exists in a legacy system or in physical records | Extract and measure; record source, period, row count | Programme Manager with the benefit owner |
| **`B`** | **Measurable with effort** — no system data; needs sampling, timed observation or a manual count | Run the exercise (§5) | The benefit owner |
| **`C`** | **Permanently unmeasurable** — the activity does not exist pre-system, or the window has closed | Record **`NOT MEASURABLE`** with the reason; the target is restated as an **absolute standard**, not an improvement | Programme Manager, CFO countersigns |
| **`D`** | **Genuinely zero** — the capability does not exist, so the baseline is a real, measured `0` | Record `0` with its basis. **Zero is a measurement, not an absence** (`BL-09`) | Benefit owner |

> **`BMR-04`. Class `C` is the honest class and must not be avoided.** A programme that refuses to
> record `NOT MEASURABLE` will instead record a guess, and a guess in field 4 with nothing in field
> 5 is indistinguishable from a measurement eighteen months later. `BL-06` and `BMR-04` exist so
> the Month 42 audit can tell them apart.

### 4.2 `BMR-F-03` — the class counts must be restated against 71

**Severity: MEDIUM · Status: OPEN · Owner: Programme Manager**

`RP-015` §4.3 gives class counts of *"~20 of the 44"* (`A`), *"~15 of the 44"* (`B`) and *"~9 of
the 44"* (`C`), summing to 44, plus *"several of the 51"* as `D`. Both populations are the ones
`BMR-F-01` corrects: the classifiable population is **71**, and `D` is drawn from a real population
of **24** valued rows plus the column-less 27, not from a phantom 51.

**Restated allocation.** The 71 divide first by *why* they lack a baseline, which is determined by
table position and is therefore certain:

| Origin | Count | Character |
|---|---:|---|
| §2.1–§2.8, placeholder in the baseline column | **44** | A field exists and was not filled |
| §2.9–§2.10, no baseline column at all | **27** | No field exists to fill |
| **Total** | **71** | |

**Indicative class allocation**, by the rule in §4.1:

| Class | `RP-015` §4.3 | **This document** | From the 44 | From the 27 | Basis |
|:--:|---:|---:|---:|---:|---|
| **`A`** measurable now | ~20 | **20** | 20 | 0 | Legacy service, inventory, finance and payroll records exist and are extractable |
| **`B`** measurable with effort | ~15 | **20** | 17 | 3 | +3 from §2.10 — `KPI-092` translation completeness, `KPI-093` data-quality pass rate and `KPI-094` manual report count are all measurable against **today's** estate |
| **`C`** permanently unmeasurable | ~9 | **13** | 4 | 9 | +9 from §2.9 — MSP, rental, refurbishment, data-services and e-waste **service quality** metrics that have no pre-programme analogue |
| **`D`** genuinely zero | *"several"* | **18** | 3 | 15 | Capability-does-not-exist zeros, chiefly marketplace and platform absolutes |
| **Total** | 44 | **71** | **44** | **27** | |

**Verification**: 20 + 20 + 13 + 18 = **71** ✓ · 20 + 17 + 4 + 3 = **44** ✓ ·
0 + 3 + 9 + 15 = **27** ✓ · 44 + 27 = **71** ✓.

> **`BMR-06`. The allocation above is indicative and is confirmed per KPI at §4.3 step 2**, by the
> Programme Manager with the named benefit owner, and recorded in field 3 of that KPI's record. This
> document allocates counts, not verdicts. A class assigned centrally and never confirmed by the
> person who must measure it is the mechanism that produced 44 placeholders in the first place.

> **Note the shape of the correction, because it is the reason to accept it.** Widening the
> population from 44 to 71 does **not** add 27 measurement tasks. Eighteen of the 27 are class `D`
> genuine zeros — the cheapest records in the programme, because the evidence is a signed statement
> that the capability does not exist — and nine are class `C`. **The measurement workload grows by
> three metrics; the record-keeping workload grows by 27.** That distinction is what makes the
> corrected position affordable, and it is why the correction should be welcomed rather than
> resisted.

### 4.3 The definition-before-measurement sequence

> **`BMR-02`. A baseline against an undefined metric is not a baseline.** The metric about to be
> baselined is defined to `RP-001`'s eighteen fields **immediately before** it is measured.

`RP-001` §4.9 records that 8 of 250 metrics are defined. Waiting for all 250 would put the first
baseline beyond W1 and forfeit the entire improvement case. `RP-015` §4.4 step 1 supplies the fix
and this document adopts it as a rule: **definition and measurement are one sequenced activity per
metric**, not two documents in series.

| Step | Action | Owner | Evidence produced |
|---:|---|---|---|
| 1 | Define the metric — `RP-001` fields 1–15, 17, 18. Field 16 is filled by step 7 | BI Lead | An `RP-001` entry |
| 2 | **Confirm the class** `A`–`D` (§4.1) | Programme Manager with benefit owner | Class, with reason |
| 3 | **`A`** — extract from the legacy source | Data Migration with owner | Source, period, row count |
| 4 | **`B`** — run the exercise (§5) | Benefit owner | Protocol, sample, raw data |
| 5 | **`C`** — record `NOT MEASURABLE`; restate the target as an absolute | Programme Manager | Reason, CFO countersignature |
| 6 | **`D`** — record `0` with its basis | Benefit owner | Statement of non-existence |
| 7 | Record fields 5–7 and publish to `RP-001` field 16 | Measurer, then BI Lead | The baseline record (§7.2) |
| 8 | **Sign** (§8) | Benefit owner; CFO where a `06-02` §3.1 line is supported | Signature and date |
| 9 | **Release `PIR-27` for this KPI** (§8.4) | PMO | Register entry |

---

## 5. The Measurement Exercises

### 5.1 The four standing exercises, carried unchanged

`RP-015` §4.5 defines four class-`B` exercises. They are carried **verbatim in method**, because
`BL-01` prohibits re-measuring what another instrument already measures, and because each was
deliberately aligned to a verification protocol so that baseline and verification are directly
comparable.

| # | Exercise | Measures | Method | Aligned to |
|:--:|---|---|---|---|
| **`B1`** | **Timed observation, branch counter** | `KPI-010` walk-in intake time; agent handling times | **20 timed samples per branch across 6 branches** | `TS-006` `UA-12`; gate criterion `G1-03` |
| **`B2`** | **Job-record sample** | `KPI-002`, `KPI-003` TAT; `KPI-004` first-time fix; `KPI-005` rework; `KPI-006` SLA compliance; `KPI-007` QC first-pass | **1,200 closed jobs, 6 branches, 3 months**, coded against the `RP-001` definition including its exclusions | `RP-001` §4.5 exclusions |
| **`B3`** | **Effort census** | `KPI-094` manual management reports; the `04-00` **−90%** reporting-effort target; `KPI-059` payroll processing time; `KPI-050` close cycle | **Two-week time log across the affected functions**, counting hours spent producing recurring outputs | `RP-010` `BP-15` |
| **`B4`** | **Stock count and reconciliation** | `KPI-042` inventory accuracy; `KPI-047` van-stock variance | **Physical count at 6 locations plus 10 vans** | `TS-008` `UA-23` |

> **`B3` is the exercise nobody will want to run and the one with the largest number attached.**
> `04-00` commits to cutting manual management reporting effort by 90% and `RP-010` `BP-15`
> requires effort measured monthly against it. **Without `B3` that target has no denominator** and
> the single most quotable benefit in the programme is unfalsifiable. Carried from `RP-015` because
> it remains true and remains unfunded.

### 5.2 Three exercises this document adds

The four above do not reach the contract, claim and customer metrics that carry **BDT 250 lac** of
improvement benefit between them, nor the 27 column-less rows. These three complete the coverage.

| # | Exercise | Measures | Method | Why it is needed |
|:--:|---|---|---|---|
| **`B5`** | **Contract and claim file review** | `KPI-028` renewal rate · `KPI-030` contract SLA attainment · `KPI-031` negative-margin contracts · `KPI-036` warranty attach rate · `KPI-039` first-submission approval · `KPI-041` claims with complete evidence | **Full census of the AMC/RAMC register for the last 12 renewal cycles**, plus a **300-claim file sample across 4 brand principals, 12 months** | `KPI-028` and `KPI-037` are principal KPIs of two benefit lines worth **BDT 172 lac** and neither has a producing specification (`BMR-F-05`). This exercise is the only evidence route |
| **`B6`** | **Customer measurement wave** | `KPI-021` NPS · `KPI-024` complaint resolution within SLA · `KPI-027` first-contact resolution · re-evidences `KPI-020` CSAT and `KPI-023` churn | **A single survey instrument to a stratified sample of 800 customers across 6 branches and 3 segments**, plus a **12-month complaint-log census** | Customer retention is **BDT 78 lac** and rests on `KPI-020`/`KPI-021`/`KPI-023`. One is approximate, one is unmeasured, one has no producing specification. A single wave settles all three at one cost |
| **`A1`** | **Legacy extract programme** | The 20 class-`A` baselines — service, inventory, finance and payroll records | **Extract, count rows, state period and source system** for each of the 48 sources `MG-002` profiles | Class `A` is the cheapest class and the one most at risk from decommissioning (§6.3). Runs as an addendum to `MG-002` profiling, not as a separate mobilisation |

**Verification of the BDT 250 lac**: AMC/RAMC renewal uplift 72 + warranty revenue recovery 100 +
customer retention 78 = **250** ✓.

> **`B5` and `B6` are specified as single instruments deliberately.** Six separate small
> measurements will not be run; one census and one survey will. The estate's own evidence for this
> is `RP-015` `B1`–`B4`, which have been specified since `RP-015` issued and none of which has been
> run, because each needed its own mobilisation.

### 5.3 The two procedures that are not measurements

| # | Procedure | Applies to | Output |
|:--:|---|---:|---|
| **`C1`** | **Non-measurability determination** | 13 class-`C` KPIs | For each: `NOT MEASURABLE`, the reason (activity does not exist / window closed), and the **restated target as an absolute standard**. CFO countersignature. Feeds `BM-003` §7 and `BM-004`'s benefit profiles |
| **`D1`** | **Zero attestation** | 18 class-`D` KPIs | For each: `0`, with a signed statement of which capability does not exist and what evidence establishes that. **`BL-09` — zero is a measurement.** Cheapest records in the programme; complete these first to demonstrate the process works |

> **`BMR-07`. `D1` runs first.** Eighteen signed baselines at negligible cost, completed before any
> exercise mobilises, convert `PIR-27` from a total stop into a partial one and give the Steering
> Committee visible evidence that the measurement programme functions. A programme that begins with
> its hardest measurement produces no signed records for months and loses support.

### 5.4 Effort and cost

Estimated in the same shape as `GV-007`, and marked with an AACE estimate class per `CO-005`
`TCO-06`. **Business time, not vendor time** — which is why it belongs to the Steering Committee.

| Exercise | Business days | Functions involved | Class | Note |
|---|---:|---|:--:|---|
| `D1` zero attestation | 4 | Benefit owners | 3 | Desk exercise |
| `C1` non-measurability determination | 6 | Programme Manager, CFO | 3 | Desk exercise |
| `A1` legacy extract | 25 | Data Migration, Finance, Inventory, HR | 4 | Rides on `MG-002` profiling |
| `B1` timed observation | 12 | Branch operations, 6 branches | 3 | 20 samples × 6 sites |
| `B2` job-record sample | 30 | Service operations, QC | 4 | 1,200 records coded |
| `B3` effort census | 20 | Finance, HR, BI, branch management | 4 | Two-week log across ~8 functions |
| `B4` stock count | 15 | Inventory, 6 locations + 10 vans | 3 | Physical count |
| `B5` contract and claim review | 28 | Commercial, Warranty, Finance | 4 | Census + 300-claim sample |
| `B6` customer measurement wave | 18 | Customer Service, Marketing | 4 | 800-customer survey + log census |
| **Total** | **158 business days** | | **4** | ≈ **31.6 person-weeks** |

**Verification**: 4 + 6 + 25 + 12 + 30 + 20 + 15 + 28 + 18 = **158** ✓ · 158 ÷ 5 = **31.6 PW** ✓.

> **Set 31.6 person-weeks of business time against BDT 542 lac of improvement benefit that cannot
> otherwise be claimed.** At `CO-005` §10.1's verified rate of BDT 122.70/USD, BDT 542 lac is
> **$441.7K** a year. **Verification**: 542 × 100,000 ÷ 122.70 = **$441,728** ✓. This is the
> cheapest ratio in the programme, and `CO-005` §10.3 already records the recovery as *"~BDT 396
> lac of benefit is recoverable, not lost"* — a figure §3.7 corrects upward.

---

## 6. Schedule and Foreclosure

### 6.1 `BMR-08` — foreclosure is caused by the event that changes the measured thing, not by the wave that claims the benefit

The estate treats go-live as the universal foreclosing event. That is **true for observational
measurements and false for record-based ones**, and the distinction is worth months.

| Measurement kind | Exercises | What forecloses it | When |
|---|---|---|---|
| **Observational** — measures live behaviour as it happens | `B1` timed observation, `B3` effort census, `B4` physical count | **Go-live at the observed site.** The behaviour after go-live is a different behaviour | End of the wave that changes that process |
| **Record-based** — measures history already written down | `A1`, `B2` job records, `B5` contract and claim files, `B6` complaint-log census | **Legacy decommissioning** (`RL-006`), or retention expiry — *not* go-live. The records survive go-live | When `RL-006` retires the source |
| **Survey-based** — measures present opinion | `B6` customer survey | **Go-live changes the experience being rated.** A post-go-live NPS is a rating of the new system | End of the wave that changes the customer journey |
| **Attestation** | `C1`, `D1` | Nothing. A statement that a capability did not exist pre-programme remains true | Never |

> **This is the most useful sentence in this document for the Steering Committee.** Roughly half
> the measurement programme — `A1`, `B2`, `B5` and part of `B6` — is **not** foreclosed by Wave 1
> go-live, and the assumption that it is has been suppressing the case for running it at all.
> **What forecloses it instead is `RL-006`, and `RL-006` has no obligation to protect it.**

### 6.2 `BMR-F-06` — the decommissioning plan has no baseline-preservation obligation

**Severity: HIGH · Status: OPEN · Owner: Programme Director with the Migration Lead**

```bash
grep -ciE "baseline|KPI|BM-002" project-guide-doc/12_Release_Deployment_and_Transition/RL-006_Legacy_Decommissioning_Plan.md
```

**Result: 0.** `RL-006` mentions *baseline*, *KPI* and `BM-002` **zero times**. `MG-002` mentions
*baseline* three times, none of them about KPI baselines.

**The consequence.** Class `A` — 20 KPIs — and the record-based part of class `B` are extracted
from legacy sources. `RL-006` may lawfully retire a source the moment its migration is reconciled.
**If it does so before `A1`, `B2` or `B5` has run, a baseline that was recoverable becomes class
`C` permanently**, and the benefit it supports moves from claimable to unclaimable — silently,
because nothing in `RL-006` would flag it.

**Remediation — new rule, binding on `RL-006` and `MG-002`:**

> **`BMR-09`. A legacy source that carries an unsigned baseline may not be decommissioned.**
> `RL-006`'s decommissioning checklist adds a precondition: *"every `BM-002` class-`A` or
> record-based class-`B` baseline sourced from this system is signed, or the Programme Director has
> recorded a written waiver naming the benefit forgone."* `MG-002`'s profiling record adds a field:
> **`carries_baseline: yes | no`**, populated at profiling time.

Raised as `Q-02`; escalated to `GV-005` because it binds two documents in another category and
cannot be closed inside this one.

### 6.3 The wave calendar this schedule is anchored to

From `GV-004` §5.2, which is the register's authoritative wave-to-month mapping:

| Wave | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Months** | 1–4 | 5–8 | 9–13 | 14–18 | 19–22 | 23–26 | 27–30 | 31–34 | 35–36 |

> **`BMR-10`. This document anchors to `GV-004` §5.2 and to no other calendar.** `AUDIT-019` `CM-03`
> records that **two wave calendars remain current across the repository**. A measurement schedule
> that silently picks one of two calendars produces deadlines nobody can audit. If `GV-004` §5.2 is
> superseded, this section is reissued — it is not reinterpreted.

### 6.4 The schedule

| Exercise | Must complete by | Driven by | Consequence of missing it |
|---|---|---|---|
| **`D1`** zero attestation | **Month 2** | Nothing — do it first (`BMR-07`) | None; but the programme forgoes 18 cheap signed baselines and the evidence that measurement works |
| **`C1`** determination | **Month 3** | Feeds `BM-003` §7 and `BM-004` profiles | `BM-003` cannot state claimable benefit; 13 targets stay ambiguous between "improvement" and "standard" |
| **`B1`** timed observation | **Month 3** | **W1 go-live, end of Month 4** — walk-in intake changes | `KPI-010` becomes class `C`. `G1-03` loses its comparator, so the gate criterion *"under 3 minutes"* has nothing to be an improvement on |
| **`B3`** effort census | **Month 3** | **W1 go-live** — reporting and close effort change | The `04-00` **−90%** reporting target permanently loses its denominator |
| **`B4`** stock count | **Month 3** | **W1/W2 go-live** — inventory processes change | `KPI-042` (75%, approximate) cannot be upgraded to precise; inventory benefit **BDT 34 lac** weakens |
| **`B6`** customer survey half | **Month 4** | **W1 go-live** — the customer journey changes | `KPI-021` NPS becomes class `C`; customer retention **BDT 78 lac** loses its principal comparator |
| **`A1`** legacy extract | **Before `RL-006` retires each source** | **Decommissioning**, not go-live | 20 class-`A` baselines become class `C`; `BMR-09` is the control |
| **`B2`** job-record sample | **Before `RL-006` retires the service system** | Decommissioning | 6 service-delivery baselines lost; technician productivity **BDT 130 lac** and warranty **BDT 100 lac** weaken |
| **`B5`** contract and claim review | **Before `RL-006` retires the contract and claim systems** | Decommissioning | AMC/RAMC **BDT 72 lac** and warranty **BDT 100 lac** lose their principal comparators |
| **`B6`** complaint-log census | **Before retention expiry** | Retention policy | `KPI-024` lost |

### 6.5 What is already foreclosed

> **`BMR-11`. A foreclosed baseline is recorded, not quietly dropped.**

Nothing is recorded as foreclosed at this issue, because no wave has gone live. **That statement is
the reason to act now, and it will not be true at the next issue.** The 13 class-`C` KPIs are not
foreclosed by the programme — they were never measurable, because the activity did not exist.

**The distinction matters to the Board.** Class `C` is a fact about the world. A foreclosed class-`A`
baseline is a fact about the programme's own delay, and `BMR-11` requires it to be reported as such,
with the benefit line and the BDT figure attached, in the same management pack that reports progress.

### 6.6 The decision this document puts to the Steering Committee

| # | Decision | Options | This document's recommendation |
|---|---|---|---|
| 1 | **Fund 31.6 PW of business time before Month 4** | Fund · part-fund the observational exercises only · defer | **Fund in full.** §5.4's ratio — 31.6 PW against $441.7K/yr of otherwise unclaimable benefit — is the strongest in the programme |
| 2 | **Adopt `BMR-09`** binding `RL-006` and `MG-002` | Adopt · reject | **Adopt.** It costs one checklist line and one profiling field, and it protects the half of the programme that is *not* foreclosed by go-live |
| 3 | **Sequence `D1` before everything** | Yes · no | **Yes** (`BMR-07`) |
| 4 | **Accept the corrected population of 71** | Accept · retain "44 of 95" | **Accept.** §3.4. Retaining 44 means `BM-003`, `CO-005` §10.1 and every management pack continue to state a figure that is 60% of the truth |

---

## 7. The Baseline Record

### 7.1 One record per KPI

> **`BMR-12`. A baseline is a record, not a number.** A value with no method, population, date,
> source or signature is a figure of unknown provenance, and `BL-07` prohibits adjusting it later
> — which means an unevidenced figure is both unusable and permanent.

### 7.2 The schema — `RP-015` §4.2's thirteen fields, carried and extended

Fields 1–13 are `RP-015` §4.2 **unchanged**, so the two documents cannot diverge (`BL-01`). Fields
14–17 are added by this document to satisfy ISO/IEC/IEEE 15939 and the `PIR-27` release.

| # | Field | Content | Source |
|---:|---|---|---|
| 1 | `kpi` | The `RP-001` identifier | `RP-015` |
| 2 | `metric_defined` | Whether the eighteen-field `RP-001` definition exists | `RP-015` |
| 3 | `class` | `A` · `B` · `C` · `D` (§4.1) | `RP-015` |
| 4 | `value` | The measured value, or `NOT MEASURABLE` with its class | `RP-015` |
| 5 | `basis` | **How it was measured** — sample size, period, source, method | `RP-015` |
| 6 | `evidence` | Where the working is retained (`CG-012`, `GV-011`) | `RP-015` |
| 7 | `window` | The period measured, and the date measured | `RP-015` |
| 8 | `measured_by` | Named function | `RP-015` |
| 9 | `signed_by` | Named signatory and date | `RP-015` |
| 10 | `benefit_line` | The `06-02` §3.1 line it supports, or `none` | `RP-015` |
| 11 | `benefit_owner` | From `06-02` §3.5 | `RP-015` |
| 12 | `wave_required` | The wave before which it must be signed | `RP-015` |
| 13 | `restated_from` | Where a baseline has been restated (`BL-07`) | `RP-015` |
| **14** | **`information_need`** | **The decision this measurement informs**, in one sentence | **New** — ISO/IEC/IEEE 15939 §6.2.1 |
| **15** | **`confidence`** | **`High` · `Medium` · `Low`**, with the reason (§7.4) | **New** |
| **16** | **`producing_component`** | The module or portal that will compute the "after", or `NONE` | **New** — `BMR-F-02`, `BMR-F-05` |
| **17** | **`pir27_released`** | Date `PIR-27` was released for this KPI, or blank | **New** — §8.4 |

> **Field 16 is the one this estate did not know it needed.** `BMR-F-02` exists because nobody
> asked, of any KPI, *which component produces the after-value*. Eight of 95 can answer it with a
> precise before-value. A record that carries field 16 makes that question impossible to skip
> again.

### 7.3 Conformance to the ISO/IEC/IEEE 15939 measurement information model

| 15939 element | §7.2 field | Note |
|---|---|---|
| Information need | 14 | The decision the measure informs |
| Measurable concept | 10, 11 | The benefit line and its owner |
| Entity and attributes | `RP-001` fields 6, 7, 10 | Population, filter and grain — held in the dictionary, not duplicated |
| Base measure, measurement method | 5 | `basis` carries both |
| Derived measure, measurement function | `RP-001` field 5 | The formula |
| Indicator, analysis model | 4, 15 | Value with its confidence |
| Decision criteria | `06-02` §2 targets; 12 | The target and the wave it is judged at |

**Departure, recorded.** 15939 places decision criteria inside the measurement plan. Here they sit
in `06-02` §2 and are **not restated** (§1.1 out of scope), because restating 95 targets in a
second document is the mechanism that produced two live wave calendars. Field 12 carries the
pointer instead of the value.

### 7.4 Confidence grading

| Grade | Criteria | Effect |
|:--:|---|---|
| **High** | Full census or a sample ≥ 1,000 with a stated method matching the `RP-001` definition, from a system of record | Claimable without qualification |
| **Medium** | Sample of 100–999, or a census from records with known gaps, method stated | Claimable; the pack reports the grade beside the figure |
| **Low** | Sample < 100, or a method that does not fully match the definition, or an approximation carried from `06-02` pending re-measurement | **Not claimable.** Recorded so it is visible, and scheduled for upgrade |

> **All 24 values currently in `06-02` §2 enter at `Low`** (`BMR-03`), because none carries a
> method. Nine of them are approximations and cannot rise above `Low` without re-measurement; the
> fifteen precise ones rise to `Medium` or `High` on production of the working that generated them,
> if it still exists. **The first task of `A1` is to find out whether it does.**

### 7.5 The register

The per-KPI register is held as a controlled table under `GV-011`, keyed on field 1, with one row
per registered KPI — **95 rows on issue, all but the `D1` attestations empty.** It is not
reproduced in this document, because a register embedded in a versioned narrative document is a
register that goes stale between issues; that is `MGA-15` and `PGD-A1-03`, recorded repeatedly
across this estate.

> **`BMR-13`. The register is counted, with its enumeration timestamp** (`BL-12`, `CP-11`), and its
> **unsigned count is published in every management pack until it reaches zero** (`BL-11`).

---

## 8. Sign-off and Release

### 8.1 What a signature asserts

| The signatory asserts | Field |
|---|---|
| The metric was defined before it was measured | 2 |
| The method stated is the method used | 5 |
| The working is retained and retrievable | 6 |
| The population and period are as stated | 5, 7 |
| The value has not been adjusted to improve a variance (`BL-07`) | 4, 13 |

### 8.2 Who signs

| Case | Signatory | Countersignatory |
|---|---|---|
| Baseline supports a `06-02` §3.1 benefit line | The named benefit owner (`06-02` §3.5) | **CFO** (`BL-04`) |
| Baseline supports no benefit line — a management metric | The metric's `RP-001` business owner | Programme Manager |
| Class `C` — `NOT MEASURABLE` | Programme Manager | **CFO** (`BMR-04`) |
| Class `D` — zero attestation | Benefit owner | Programme Manager |

### 8.3 `BMR-14` — the CFO signature is the control, and it is not a formality

The CFO signs because the baseline is the denominator of a benefit the CFO will later report to the
Board. **A benefit owner signing alone has an incentive to accept a low baseline**, because a low
baseline makes the improvement look larger. The countersignature is the only place that incentive
is checked, and `GV-010`'s independent review samples signed baselines for exactly this.

### 8.4 The `PIR-27` release

> **`BMR-15`. `PIR-27` releases per KPI, on signature — never per document.**

`RL-005` `PIR-27` states that until `BM-002` issues, no wave review may claim any benefit. Read
literally, the issue of this document would release every claim at once, including for the 71 KPIs
with no baseline. That would be worse than the stop it replaces.

| State | `A3` in the wave review reports |
|---|---|
| No signed baseline for the KPI | **"Not claimable — no baseline"**, per `PIR-27`, unchanged |
| Signed, confidence `Low` | **"Not claimable — baseline confidence Low"**, with the upgrade date |
| Signed, confidence `Medium` or `High`, field 16 ≠ `NONE`, causal mechanism documented | **Claimable.** `PIR-22`'s three conditions are met |
| Signed class `C` | **"Absolute standard, not an improvement"** — reported against the target, never as a benefit against a baseline |
| Signed class `D` | **Claimable** — a movement from a real zero is a real movement |

**This is how `RLA-09` is discharged**: not by this document existing, but by the count of released
KPIs rising. `BMR-13` publishes that count.

### 8.5 Evidence custody

Working papers are retained under `GV-011` for the life of the programme **plus the Month 42
benefits audit plus seven years**, per the statutory retention applied to financial support in
`SC-008`. `BL-07` makes a baseline permanent, so its evidence must outlive the programme.

> **`BMR-16`. Evidence is retained at the point of measurement, not reconstructed afterwards.** A
> sample of 1,200 job records that cannot be re-identified is a number, not a measurement.

### 8.6 Reissue

| Trigger | Action |
|---|---|
| Any exercise in §5 completes | Data section reissued; version increments in the second digit |
| A baseline is restated under `BL-07` | Reissue with field 13 populated and the original retained |
| A baseline is foreclosed | Reissue recording it under `BMR-11`, with the benefit line and BDT figure |
| Each wave gate | Reissue with the unsigned count and the released count (`BMR-13`) |
| `GV-004` §5.2 is superseded | §6.3 and §6.4 reissued, never reinterpreted (`BMR-10`) |

---

## 9. The Identifier Position, So Far As Baselines Depend On It

### 9.1 `RP-01` confirmed by independent count

```bash
grep -rho "KPI-[0-9]\{3\}" 1000fix_ERP_Module/03_Modules/ \
     1000fix_ERP_Module/04_Portals_and_Applications/ | sort -u | wc -l
```

| Position | `RP-01` | **Counted 2026-08-19 00:48 (+06)** |
|---|---:|---:|
| Registered in `06-02` §2 | 95 | **95** ✓ |
| Distinct identifiers used in the 79 specifications | 250 | **250** ✓ |
| Used but unregistered — `KPI-110`…`KPI-305` | 196 | **196** ✓ |
| Registered but used by no specification | 41 | **41** ✓ |
| Both registered and used | 54 | **54** ✓ |
| Unallocated gap `KPI-096`…`KPI-109` | 14 | **14, and used nowhere** ✓ |

**Verification**: 95 + 196 = **291** distinct identifiers across the whole
`1000fix_ERP_Module` repository ✓, of which 250 appear in specifications and 41 appear only in
`06-02` ✓ · 250 − 196 = **54** ✓ · 95 − 54 = **41** ✓.

**`RP-01` is confirmed in every particular.** Its diagnosis is also confirmed: `06-02` §2 stopped at
95 while the architecture grew from 30 modules to 67, and module authors allocated locally and said
so. **The defect is in the register, not in the modules.**

### 9.2 What it costs this document

| Effect | Consequence for baselines |
|---|---|
| **196 identifiers have no registered baseline field at all** | They are module operational metrics, not board KPIs. `RP-001` §4.3 reserves `KPI-110`…`KPI-305` for exactly this. **This document does not baseline them** — but until they are ratified, no one can prove that none of them carries a board benefit |
| **41 registered identifiers are produced by nothing** | `BMR-F-02` and `BMR-F-05`. Nine of them have a value, so measurement effort would be spent on metrics the system may never compute |
| **`KPI-018` is one identifier over two metrics** | `M03` splits it into on-time collection and on-time delivery. **A single baseline cannot be measured for it** (`KD-05`). It is held out of `B2` until Enterprise Architecture splits it |
| **`KPI-013` naming inconsistency** | `06-02`'s name governs (`KD-04`). No baseline effect; recorded so the measurer uses the right definition |

> **`BMR-17`. This document baselines the 95 registered KPIs and no others.** If ratification under
> `RP-001` `O-01` promotes any of the 196 into the board register, that KPI enters this document's
> scope at the next issue with its own class and deadline. **It does not acquire a retrospective
> baseline**, and if its window has closed it enters as class `C`.

### 9.3 `00-06` `M-03` and `M-04` confirmed as instances

`M-03` (M31's 11 KPIs unregistered) and `M-04` (M02–M06 KPIs shown as "—") are both consequences of
register exhaustion. No separate remediation; they close when `RP-001` `O-01` closes.

### 9.4 Documents that quote "44 of 95" and require correction

| Document | Where | Correction |
|---|---|---|
| `PGD-000` | Category 15 header note | 71 of 95; improvement exposure BDT 542 lac |
| `15/_CATEGORY_OVERVIEW.md` | Purpose; `AUDIT-015` table | Same |
| `CO-005` §10.1 | Claimable computation | Recomputed by `BM-003` §7 on the corrected population |
| `RL-005` §7.3 | `PIR-27` narrative | 71 of 95; release mechanism now defined in §8.4 |
| `GV-001` `CC-09` | Charter constraint | 71 of 95 |
| `AUDIT-015` `RP-02` | The finding itself | **Restated, not closed** (§3.4) |

> **`BMR-18`. A figure this document corrects is corrected at the correcting document's issue, and
> the correction is listed.** A correction made silently in one document while six others carry the
> old figure produces the divergence `RR-002` exists to prevent.

---

## 10. Governing Rules — Consolidated

| # | Rule |
|---|---|
| **`BMR-01`** | Every figure describing the baseline position is **counted, with its command and timestamp**. A baseline report that quotes another document's count has failed at its own subject |
| **`BMR-02`** | **A baseline against an undefined metric is not a baseline.** Definition precedes measurement, per metric, immediately |
| **`BMR-03`** | The 24 values already in `06-02` §2 are **provisional at confidence `Low`** until evidenced or re-measured. None carries a method |
| **`BMR-04`** | **Class `C` is a valid, recorded answer.** `NOT MEASURABLE` with a reason, CFO countersigned, and the target restated as an absolute standard |
| **`BMR-05`** | **Reuse `SP-002` measurements** where they exist; never re-measure the same activity (`BL-01`) |
| **`BMR-06`** | The class allocation in §4.2 is **indicative**; class is confirmed per KPI by the Programme Manager with the named benefit owner |
| **`BMR-07`** | **`D1` runs first.** Eighteen cheap signed baselines prove the process works before an exercise mobilises |
| **`BMR-08`** | **Foreclosure is caused by the event that changes the measured thing** — go-live for observational and survey measures, decommissioning for record-based ones |
| **`BMR-09`** | **A legacy source carrying an unsigned baseline may not be decommissioned** without a written waiver naming the benefit forgone. Binds `RL-006` and `MG-002` |
| **`BMR-10`** | This schedule anchors to **`GV-004` §5.2 and no other calendar**. If superseded, §6 is reissued, not reinterpreted |
| **`BMR-11`** | **A foreclosed baseline is recorded**, with its benefit line and BDT figure, in the management pack that reports progress |
| **`BMR-12`** | **A baseline is a record, not a number** — seventeen fields, §7.2 |
| **`BMR-13`** | The register is **counted with its enumeration timestamp**, and its **unsigned count published in every management pack until it reaches zero** (`BL-11`, `BL-12`) |
| **`BMR-14`** | The **CFO countersignature** is a control against the benefit owner's incentive to accept a low baseline, not a formality |
| **`BMR-15`** | **`PIR-27` releases per KPI, on signature** — never per document |
| **`BMR-16`** | **Evidence is retained at the point of measurement**, never reconstructed |
| **`BMR-17`** | This document baselines **the 95 registered KPIs and no others**. A later-ratified KPI enters at the next issue and acquires no retrospective baseline |
| **`BMR-18`** | A figure this document corrects is **corrected at issue and the correction listed** (§9.4) |

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BM-002-D-01` | The classifiable population | Retain `RP-02`'s 44 · restate to 71 | **71** | 27 rows have no baseline field; counting them as baselined is a denominator substitution (§3.4) | Six documents carry a corrected figure (§9.4); `BM-003` recomputes claimable benefit |
| `BM-002-D-02` | Whether to publish "8 of 95" | Suppress as demoralising · publish | **Publish** (§3.5) | `06-02` §6's own standard: *"missed benefits are reported as missed"*. A measurement-readiness figure the Board does not have is a figure it cannot act on | The Steering Committee decision in §6.6 becomes unavoidable |
| `BM-002-D-03` | Foreclosure model | Go-live forecloses everything · event-specific | **Event-specific** (`BMR-08`) | Record-based measures survive go-live; treating them as lost suppressed the case for running them | Roughly half the programme gains months of window; `BMR-09` becomes necessary |
| `BM-002-D-04` | `PIR-27` release granularity | Per document at issue · per KPI on signature | **Per KPI** (`BMR-15`) | Releasing at issue would permit claims against 71 unmeasured KPIs — worse than the stop | `A3` reporting gains five defined states (§8.4) |
| `BM-002-D-05` | Sequence | Hardest exercise first · cheapest first | **`D1` first** (`BMR-07`) | 18 signed records at negligible cost, demonstrating the process before mobilisation | Visible progress inside Month 2 |
| `BM-002-D-06` | Whether to restate the 95 targets here | Restate for convenience · point to `06-02` §2 | **Point** | Restating 95 targets in a second document is the mechanism that produced two live wave calendars | Field 12 carries a pointer, not a value |

> **Rule `DL-06` applies.** These are local decisions in the `BM-002-D-nn` space. A decision with
> programme-wide effect — `D-01` above, and the §6.6 funding decision — is raised as a `D-nnn` in
> `GV-003`.

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Will the Steering Committee fund 31.6 PW of business time before Month 4?** (§6.6 decision 1) | Programme Director | **Month 1** | Every observational exercise; BDT 542 lac of improvement benefit |
| `Q-02` | **Will `RL-006` and `MG-002` adopt `BMR-09`?** Escalated to `GV-005` because it binds documents in two other categories | Programme Director with Migration Lead | Before the first decommissioning | 20 class-`A` and 3 record-based class-`B` exercises |
| `Q-03` | **Does the working behind the 15 precise values in `06-02` §2 still exist?** If not, all 24 are `Low` permanently until re-measured | BI Lead | Month 2 | `BMR-03` upgrade path; confidence grades in §7.4 |
| `Q-04` | **When are the 196 identifiers ratified**, and does any of them carry a board-level benefit? | Enterprise Architecture (`RP-001` `O-01`) | W1 | `BMR-17`; the completeness of this document's scope |
| `Q-05` | **Which 41 registered-but-unproduced KPIs will be produced, and by what?** Nine have values (§3.6) | Enterprise Architecture | W1 | Field 16; `BMR-F-05`; **BDT 172 lac** of benefit-line comparators |
| `Q-06` | **Which wave calendar governs** — `GV-004` §5.2 or the second calendar `CM-03` records? | Programme Director | Month 1 | Every deadline in §6.4 (`BMR-10`) |
| `Q-07` | **Is `KPI-018` split before `B2` runs?** One identifier over two metrics cannot take one baseline | Enterprise Architecture | Before `B2` | `KPI-018`; logistics benefit attribution |

> An open question with no owner and no needed-by date is not an open question — it is an
> unrecorded risk. `Q-01` and `Q-02` are escalated to `GV-005` at issue.

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every figure in §3, §4 and §9 is counted, with a reproduction command and a timestamp | §3.1–§3.8, §9.1; `enumeration_timestamp` |
| `AC-02` | All 95 registered KPIs are accounted for in exactly one class or in the valued set | §4.2: 20 + 20 + 13 + 18 = 71, plus 24 valued = 95 |
| `AC-03` | Every arithmetic total is verified from its own rows (`PG-M10`) | **Thirteen** `**Verification**` statements |
| `AC-04` | The correction to `RP-02` is stated with its cause, its consequence and the list of documents to correct | §3.4, §9.4 |
| `AC-05` | A `PIR-27` release mechanism exists that does not release unmeasured KPIs | §8.4, `BMR-15` |
| `AC-06` | Every exercise has an owner, a method, a duration and a deadline driven by a named event | §5, §6.4 |
| `AC-07` | The record schema conforms to ISO/IEC/IEEE 15939's information model, with departures stated | §7.2, §7.3 |
| `AC-08` | Every new finding carries severity, owner and remediation | §2.3, §3.4–§3.7, §6.2 |
| `AC-09` | No target from `06-02` §2 is restated or renegotiated | §1.1 out-of-scope; `BM-002-D-06` |
| `AC-10` | Steering Committee decisions are stated as decisions, with a recommendation | §6.6 |

**Definition of done.** This document is complete when every criterion above is met, its `PGD-000`
status is updated with a fresh enumeration timestamp, and the CFO has signed. **It is not complete
when the baselines are measured** — that is the register's definition of done (`BMR-13`), and it is
reached when the unsigned count reaches zero.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `06-02` §2, §3, §6 | The register, the benefit model and the rule this document serves |
| Upstream | `RP-001` §4.1–§4.3 | Metric definitions and the identifier space |
| Upstream | `RP-015` §4.2–§4.8 | The schema, classes, exercises and rules carried here |
| Upstream | `DA-007` | Grain and dimensional consistency |
| Upstream | `GV-004` §5.2 | The wave calendar every deadline anchors to (`BMR-10`) |
| Upstream | `SP-002` | Process measurements reused, not duplicated (`BMR-05`) |
| Downstream | **`BM-003`** | Consumes §3.7's BDT 542 lac and §3.8 to recompute claimable benefit and the ROI position |
| Downstream | **`BM-004`** | Consumes signed baselines as the starting point of every benefit profile |
| Downstream | `RL-005` §7 | `PIR-27` released per KPI by §8.4; `A3` reporting states |
| Downstream | `GV-001`, `GV-008` | Charter constraint `CC-09` and the budget's benefit side |
| Downstream | `CO-005` §10.1 | Claimable split recomputed on the corrected population |
| Downstream | `RP-001` field 16 | Baselines published to the dictionary so every dashboard comparator resolves |
| Lateral | **`RL-006`, `MG-002`** | **`BMR-09`** — decommissioning precondition and the `carries_baseline` profiling field |
| Lateral | `GV-010` | Samples signed baselines for the incentive check in §8.3 |
| Lateral | `GV-011` | Register custody and evidence retention |
| Lateral | `CH-004` | Adoption measures; distinct question, shared measurement calendar |
| Lateral | `RP-010`, `RP-011`, `RP-012` | Packs, league tables and alerts blocked on baselines by `BL-08` |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./BM-003_Business_Case_and_ROI_Model.md` · `./BM-004_Benefits_Realisation_Plan.md` ·
`./BM-005_Lessons_Learned_and_Continuous_Improvement_Register.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-011_Documentation_Control_and_Configuration_Management_Plan.md` ·
`../03_Data_and_Information_Architecture/DA-007_Analytical_and_Dimensional_Model_Specification.md` ·
`../09_Data_Migration_and_Cutover/MG-002_Legacy_System_Profiling_and_Extract_Specification.md` ·
`../12_Release_Deployment_and_Transition/RL-005_Post_Implementation_Review_Standard.md` ·
`../12_Release_Deployment_and_Transition/RL-006_Legacy_Decommissioning_Plan.md` ·
`../14_Commercial_Vendor_and_Contract/CO-005_Total_Cost_of_Ownership_Model.md`

**Workspace**
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md` ·
`../../project_content/_AUDIT/AUDIT-015_Category_14_RP_Content_Audit.md` ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_BRD.md` §19, §20

**External standards and sources**

| Source | Edition relied on | Verified |
|---|---|---|
| ISO/IEC/IEEE 15939 — Systems and software engineering, Measurement process | **2017**, first edition 2017-05; current | 2026-08-19 |
| ISO 21502 — Guidance on project management | **2020** | 2026-08-19 |
| ISO 21503 — Guidance on programme management | **2022** *(revised from 2017)* | 2026-08-19 |
| ISO 21500 — Project, programme and portfolio management, context and concepts | **2021** *(repositioned; ISO 21502:2020 carries the practice guidance)* | 2026-08-19 |
| MSP — Managing Successful Programmes | **5th edition**, PeopleCert *(current; AXELOS acquired 2021)* | 2026-08-19 |
| ISO 9001 — Quality management systems | **2015** | 2026-08-19 |
| ISO/IEC 25040 — Evaluation process | **2011** | 2026-08-19 |

> Every path above was resolved on disk at 2026-08-19 00:48 (+06) before issue. Where a referenced
> document does not yet exist, it is marked in `PGD-000` rather than linked.

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Enterprise Architecture for the CFO | Initial issue. Corrects `AUDIT-015` `RP-02`'s denominator (44 of 68, not 44 of 95; true position 71 of 95). Establishes that only **15 of 95** KPIs have both a usable baseline and a producing specification, and only **8** have a precise one. Restates the improvement-benefit exposure at **BDT 542 lac**, not 396. Adds the event-specific foreclosure model and rule `BMR-09` binding `RL-006` and `MG-002`. Defines the per-KPI `PIR-27` release. Six new findings `BMR-F-01`…`BMR-F-06` | CFO |

---

*`BM-002` · Category 15 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
