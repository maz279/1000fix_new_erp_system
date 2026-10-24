---
id: RP-015
title: Benefits Realisation and KPI Baseline Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Programme with Finance
author: Programme Manager with the CFO office and the fourteen benefit owners
reviewers: [CEO, CFO, CTO, CCO, Operations Director, HR Manager, Quality Manager, BI Lead, Steering Committee]
approver: CFO with Programme Manager
content_class: E
purpose: >
  The pre-programme baseline for every KPI the programme commits to improving, how each was measured,
  what evidence supports it, and who signed it. The rule it serves is already written: a KPI without a
  baseline cannot claim a benefit. Enumeration finds 44 of the 95 registered KPIs with no usable
  baseline, against a benefit case of BDT 876 lac a year — so as things stand, 46% of the measurement
  set cannot support a benefit claim and nobody has said so in one place. This file is where that is
  said, and where it is fixed.
traces_to: [06-02, 06-02 §1, 06-02 §2, 06-02 §3, 06-02 §5, 06-02 §6, 00-07, 00-07 H2-10, 04-00, RP-001, RP-002, RP-003, RP-008, RP-010, RP-011, RP-016, SP-002, TS-018, CG-012, M25]
priority: P1
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2 KPI register — 95 identifiers with a baseline column; §3.1 annual benefit at steady state totalling BDT 876 lac base case across 14 benefit lines; §3.2 benefit realisation curve; §3.5 benefit ownership with fourteen named owners and a "measured from" wave; §6 Benefit Tracking Discipline — "every KPI's baseline is measured and signed off before the relevant wave begins. A KPI without a baseline cannot claim a benefit"; and "honest reporting — missed benefits are reported as missed, with the reason"
    verified: 2026-08-20
    class: P1
  - source: Enumeration of 06-02 §2 baseline column, 2026-08-20 — of 95 KPI rows, 44 carry a non-numeric baseline: 28 "unmeasured", 5 "unknown", 4 "manual", 3 the literal word "baseline", 2 "untracked", 2 "n/a"; 51 carry a numeric or genuinely-zero baseline
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07_Category_H_Audit_and_Repository_Integrity_Report.md §2 finding H2-10 — "Category H overview carried an absolute KPI target with no baseline behind it", recorded as Fixed
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md P06 KPIs — manual management reporting effort −90%; P03 walk-in intake < 3 minutes against a ~10 minute baseline; P02 daily active usage > 95%
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Benefits Realisation and KPI Baseline Register

| Item | Value |
|---|---|
| KPIs registered in `06-02` §2 | **95** |
| **With a usable baseline** | **51** |
| **Without** | **44 — 46% of the register** |
| Benefit case at stake | **BDT 876 lac a year**, base case (`06-02` §3.1) |
| Benefit lines | 14, each with a named owner (`06-02` §3.5) |
| Wave | **W0** · `P1` — the earliest wave in the register |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the baseline schema in §4.2. All six sections retained in order.

---

## 1. Purpose

`06-02` §6 already contains the rule this file exists to serve, and it is unambiguous:

> *"Every KPI's baseline is measured and signed off **before** the relevant wave begins. **A KPI without
> a baseline cannot claim a benefit.**"*

**Enumeration of `06-02` §2 on 2026-08-20 finds 44 of the 95 registered KPIs with no usable baseline.**

| Baseline column value | Count |
|---|---:|
| "unmeasured" | 28 |
| "unknown" | 5 |
| "manual" | 4 |
| the literal word "baseline" | 3 |
| "untracked" | 2 |
| "n/a" | 2 |
| **Total without a usable baseline** | **44** |
| With a numeric or genuinely-zero baseline | 51 |

Audit `00-07` H2-10 found *one* absolute KPI target with no baseline behind it and recorded it as
fixed. **The register-wide position is 44**, and it has not been stated anywhere before this file.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Baselines | `06-02` §6's rule bites on 46% of the register, so no benefit on those metrics can be claimed — and the BDT 876 lac case rests substantially on them |
| Measurement basis | A baseline of "70%" with no stated method cannot be compared to a system-measured 82%, because the two may be measuring different populations |
| Evidence | The Month 42 benefits audit asks how the baseline was established. "It was in the business case" is not an answer |
| Sign-off | An unsigned baseline is renegotiated whenever a variance is uncomfortable |
| A measurement window | Baselines drift. A baseline measured after go-live is contaminated by the system it is meant to measure against |
| Honest reporting | `06-02` §6 requires missed benefits reported as missed. Without baselines, nothing can be identified as missed |

---

## 2. Scope

**In scope.** The baseline for every `06-02` §2 KPI and every `04-00` portal KPI the programme commits
to; the measurement basis, evidence, window and sign-off for each; the classification of baselines by
how they can be established; the benefit-line linkage; and the rules governing restatement.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Metric definitions | **`RP-001`** — a baseline is a value of a defined metric. §4.1 states the ordering problem |
| Benefit lines, values and the realisation curve | `06-02` §3 — this file supplies the baselines they depend on |
| Monthly benefit commentary | **`RP-008`** `N5` |
| The pack that reports realisation | `RP-010` sections 11 and 13 |
| Targets | `06-02` §2 — a target is a commitment, a baseline is a fact |
| Alert thresholds | `RP-012` — a threshold is neither |
| As-is process measurement | **`SP-002`** As-Is Process Baseline Register — §4.6 states the seam |
| Data-quality baselines | `RP-016` |
| Post-implementation benefits audit | `06-02` §6, Month 42 |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **CFO** (approver) | The evidential basis of the benefit case |
| **Programme Manager** | The measurement programme and the W0 gate |
| **The fourteen benefit owners** (`06-02` §3.5) | The baseline they will be measured against, and their `RP-008` `N5` commentary |
| **Steering Committee** | Which benefits can be claimed and which cannot |
| **BI Lead** | Baseline values for `RP-003` `XD-12` comparators and `RP-011` `LT-02` |
| **Internal and external audit** | The Month 42 benefits audit evidence trail |

---

## 4. Content

### 4.1 The ordering problem, stated first

**A baseline is a measured value of a defined metric.** Which means the correct order is: define the
metric, then measure the baseline, then set the target, then build the system.

**The programme did it in a different order.** `06-02` §2 set 95 targets against baselines in 2026-08;
`RP-001` defines 8 of 250 metrics; this file is `W0`, the earliest wave, and is being written after
Categories 00–13.

| Consequence | Handling |
|---|---|
| A baseline cannot be measured for an undefined metric | §4.4 sequences metric definition immediately before baseline measurement, per metric, rather than waiting for all of `RP-001` |
| Some baselines can no longer be measured pre-system | §4.3 class `C` — recorded as **permanently unmeasurable**, not left blank |
| Targets exist without baselines | `06-02` §2 targets stand; **this file does not renegotiate them.** It records what they can and cannot be measured against |

**This file does not pretend the ordering can be fixed retrospectively.** It classifies each baseline by
what is still possible.

### 4.2 The baseline schema

| # | Field | Content |
|---:|---|---|
| 1 | `kpi` | The `RP-001` identifier |
| 2 | `metric_defined` | Whether the metric has an eighteen-field `RP-001` definition — **a baseline against an undefined metric is not a baseline** |
| 3 | `class` | `A` measurable now · `B` measurable with effort · `C` permanently unmeasurable · `D` genuinely zero (§4.3) |
| 4 | `value` | The measured value, or `NOT MEASURABLE` with its class |
| 5 | `basis` | **How it was measured** — sample size, period, source, method |
| 6 | `evidence` | Where the working is retained (`CG-012`) |
| 7 | `window` | The period measured, and the date measured |
| 8 | `measured_by` | Named function |
| 9 | `signed_by` | Named signatory and date (`06-02` §6) |
| 10 | `benefit_line` | The `06-02` §3.1 line it supports, if any |
| 11 | `benefit_owner` | From `06-02` §3.5 |
| 12 | `wave_required` | The wave before which it must be signed |
| 13 | `restated_from` | Where a baseline has been restated (§4.7) |

**Field 5 is the field the Month 42 audit will read.** A baseline of "70% first-time fix" is worthless
without "measured over 1,200 closed jobs across 6 branches, March–May 2026, from job cards, counting a
return visit within 30 days as a failure" — because that method must match `RP-001`'s definition or the
comparison is invalid.

### 4.3 Four classes of baseline

| Class | Means | Approach | Count |
|:--:|---|---|---:|
| **`A` Measurable now** | Data exists in a legacy system or in records | Extract and measure before the consuming wave | ~20 of the 44 |
| **`B` Measurable with effort** | No system data; requires a sampling exercise, timed observation or manual count | **A measurement project**, per §4.4 | ~15 of the 44 |
| **`C` Permanently unmeasurable** | The activity does not exist pre-system, or the measurement window has passed | **Recorded as `NOT MEASURABLE`, with the reason.** The target stands as an absolute, not as an improvement | ~9 of the 44 |
| **`D` Genuinely zero** | The baseline is truly zero because the capability does not exist | Recorded as `0`, measured, not "unmeasured" | Several of the 51 |

**Class `C` is the honest category and it must not be avoided.** `KPI-079` approved active marketplace
sellers has a pre-programme baseline of zero because there is no marketplace — that is class `D`, a real
zero. But `KPI-013` automatic assignment rate at "0%" is also class `D`, while `KPI-070` MSP SLA
attainment has **no** pre-programme baseline because MSP does not exist as a measured service — and a
target of 98% is then an absolute standard, not an improvement of 98 points.

**The distinction matters to the benefit case.** An improvement benefit needs a baseline; an absolute
standard does not, but it also cannot be counted as an improvement in `06-02` §3.1.

### 4.4 The measurement programme

`06-02` §6 requires each baseline signed **before its consuming wave**. That makes this a scheduled
programme, not a document.

| Step | Action | Owner |
|---:|---|---|
| 1 | **Define the metric first** (`RP-001` eighteen fields) for the metric about to be baselined. Partial-`RP-001` is acceptable per metric; an undefined metric is not | BI Lead |
| 2 | Classify the baseline `A`–`D` (§4.3) | Programme Manager with the benefit owner |
| 3 | **Class `A`**: extract from the legacy source; record source, period and row count | Data Migration with the owner |
| 4 | **Class `B`**: run the measurement — sample, timed observation or count. §4.5 gives the four standing exercises | The benefit owner |
| 5 | **Class `C`**: record `NOT MEASURABLE` with the reason and restate the target as an absolute | Programme Manager |
| 6 | Record basis, evidence and window (fields 5–7) | Measurer |
| 7 | **Sign off** — benefit owner and CFO for any baseline supporting a `06-02` §3.1 line | CFO |
| 8 | Publish to `RP-001` field 16, so the baseline reaches every dashboard comparator | BI Lead |

**Step 1 is the ordering fix.** Rather than waiting for all 250 `RP-001` definitions (`RP-001` `O-02`),
the metric about to be baselined is defined immediately before measurement. **That makes `RP-001` and
this file a single sequenced activity per metric**, which is the only way either meets `W0`/`W1`.

### 4.5 The four standing class-`B` measurement exercises

These four cover most class-`B` baselines and each is a defined exercise rather than an estimate.

| # | Exercise | Measures | Method |
|---:|---|---|---|
| **B1** | **Timed observation, branch counter** | `KPI-010` walk-in intake time *(baseline ~10 min)*; agent handling times | **20 timed samples per branch across 6 branches**, the same protocol `TS-006` `UA-12` and `G1-03` use for verification — so baseline and verification are directly comparable |
| **B2** | **Job-record sample** | `KPI-002`, `KPI-003` TAT; `KPI-004` first-time fix; `KPI-005` rework; `KPI-006` SLA compliance; `KPI-007` QC first-pass | **1,200 closed jobs, 6 branches, 3 months**, coded against the `RP-001` definition including its exclusions |
| **B3** | **Effort census** | `KPI-094` manual management reports; the `04-00` **−90% reporting-effort** target; `KPI-059` payroll processing time; `KPI-050` close cycle | **Two-week time log across the affected functions**, counting hours spent producing recurring outputs |
| **B4** | **Stock count and reconciliation** | `KPI-042` inventory accuracy *(baseline 75%)*; `KPI-047` van-stock variance | **Physical count at 6 locations plus 10 vans**, using the `TS-008` `UA-23` protocol |

> **B3 is the exercise nobody will want to run and the one with the largest number attached.** `04-00`
> commits to cutting manual management reporting effort by 90% and `RP-010` `BP-15` requires effort
> measured monthly against it. **Without B3 that target has no denominator** and the single most
> quotable benefit in the programme is unfalsifiable. `RP-010` `O-02` records it from the pack side.

### 4.6 The seam with `SP-002`

`SP-002` As-Is Process Baseline Register measures **processes**; this file measures **metrics**. They
overlap and must not diverge.

| | `SP-002` | `RP-015` *(this file)* |
|---|---|---|
| Measures | Process steps, handoffs, cycle time, effort per process | KPI values |
| Unit | Process | `KPI-nnn` |
| Used for | Process redesign (`SP-003`) | Benefit claims (`06-02` §3) |
| Overlap | **Cycle-time and effort measurements feed both** | — |

**Rule `BL-01`: where `SP-002` has measured a cycle time or an effort figure, this file uses it and
cites it rather than re-measuring.** Two independent measurements of the same activity will differ, and
the difference will be argued about instead of the benefit.

### 4.7 Rules

| # | Rule |
|---|---|
| **BL-01** | **Reuse `SP-002` measurements** where they exist; never re-measure the same activity (§4.6) |
| **BL-02** | **A baseline states its method**, not only its value (field 5). A value without a method cannot be compared to a system-measured figure |
| **BL-03** | **The measurement method must match the `RP-001` definition**, including its exclusions. A baseline measured on a different population is not a baseline |
| **BL-04** | **Every baseline is signed** by its benefit owner, and by the CFO where it supports a `06-02` §3.1 line (`06-02` §6) |
| **BL-05** | **A baseline is measured before the consuming wave begins**, never after go-live. A post-go-live baseline is contaminated by the system it measures against |
| **BL-06** | **`NOT MEASURABLE` is a valid, recorded answer** (class `C`), and the target is then restated as an absolute standard rather than an improvement |
| **BL-07** | **A baseline is never adjusted to improve a variance.** A restatement requires a stated method error, the benefit owner's and the CFO's approval, and the original retained (field 13) |
| **BL-08** | **A metric with no baseline may not appear as a trend or a variance** on any dashboard, pack or commentary (`KD-20`, `XD-13`, `BP-09`, `NR-11`, `LT-02`) |
| **BL-09** | **Zero is a measurement**, not an absence. Class `D` is recorded as `0` with its basis |
| **BL-10** | **Every baseline names the benefit line it supports**, or records that it supports none. A KPI supporting no benefit is a management metric, which is legitimate and should be visible |
| **BL-11** | **The count of unbaselined KPIs is published in every management pack** until it reaches zero (`RP-010` section 11) |
| **BL-12** | **The register is counted, with its enumeration date** (`CP-11`) |

### 4.8 The current position, by benefit line

`06-02` §3.1 has 14 benefit lines totalling BDT 876 lac base case, each with an owner (§3.5) and a wave
from which it is measured. This is the baseline readiness of each.

| Benefit line | Base case, BDT lac | Measured from | Principal KPIs | Baseline position |
|---|---:|:--:|---|---|
| Warranty revenue recovery | 100 | W4 | `KPI-037`, `KPI-038`, `KPI-039` | **Weak** — `KPI-037` baseline is "~50% at 30–90 days", a qualitative range; `KPI-039` unmeasured |
| Technician productivity | 130 | **W2** | `KPI-011`, `KPI-012`, `KPI-014` | **Partial** — `KPI-011` 4–5 and `KPI-012` 55% are numeric; `KPI-015` unmeasured. **Earliest benefit, so earliest deadline** |
| Inventory cost reduction | 34 | W3 | `KPI-042`, `KPI-045`, `KPI-046` | **Partial** — `KPI-042` 75% numeric; `KPI-045`, `KPI-046` unmeasured. **B4 covers it** |
| Administrative labour savings | 62 | W3 | `KPI-001`, `KPI-094` | **Weak** — `KPI-094` is "manual". **B3 covers it** |
| Customer retention | 78 | W4 | `KPI-020`, `KPI-021`, `KPI-023` | **Partial** — CSAT 3.8/5 and churn ~15% numeric; `KPI-021` NPS unmeasured |
| AMC/RAMC renewal uplift | 72 | W5 | `KPI-028`, `KPI-029` | **Partial** — 60% numeric; contract base is "baseline", i.e. indexed |
| Financial close & cash flow | 26 | W3 | `KPI-050`, `KPI-051`, `KPI-052` | **Weak** — `KPI-050` is a 15–20 day range; `KPI-051` "manual"; `KPI-052` unmeasured. **B3 covers close** |
| Managed services (MSP) | 95 | W6 | `KPI-070`, `KPI-071`, `KPI-072` | **Class `C`** — MSP does not exist pre-system; targets are absolutes |
| Rental gross margin | 48 | W7 | `KPI-075`, `KPI-076` | **Class `C`** |
| Refurbishment & resale margin | 65 | W7 | `KPI-077`, `KPI-078` | **Class `C`** |
| Marketplace commission | 84 | W8 | `KPI-079`, `KPI-080`, `KPI-081` | **Class `D`** — genuine zeros |
| Data services | 30 | W7 | `KPI-073`, `KPI-074` | **Class `C`** |
| E-waste material recovery | 12 | W9 | `KPI-083`, `KPI-084` | **Class `C`/`D`** |
| Dynamic pricing margin uplift | 40 | W8 | `KPI-033` | **Partial** — "baseline", i.e. indexed to itself |

**Read the two columns together.** The five benefit lines with the **weakest baselines** — warranty
recovery, administrative savings, close and cash flow, plus parts of productivity and retention —
total roughly **BDT 396 lac of the 876**, and they are the lines that depend on *improvement against a
prior state*. The class-`C` and class-`D` lines total roughly **BDT 334 lac** and are new-business
absolutes that need no baseline.

**So the exposure is not the whole benefit case.** It is concentrated in the improvement benefits, which
are also the earliest: **technician productivity is measured from W2** and is the largest single line at
BDT 130 lac.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Metric definitions — a baseline against an undefined metric is not a baseline (§4.1, `BL-03`) |
| `06-02` §2, §3, §6 | The 95 KPIs, the 14 benefit lines, the curve and the tracking rule |
| **[`SP-002`](../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-002_As_Is_Process_Baseline_Register.md)** | Existing as-is measurements to reuse (`BL-01`) |
| [`RP-008`](RP-008_Report_Narrative_and_Commentary_Template_Set.md) `N5` | Where the baseline position is reported monthly |
| [`RP-010`](RP-010_Board_and_Management_Pack_Template.md) sections 11, 13 | Where it reaches the board |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md) `XD-12`, `RP-011` `LT-02` | Comparators and league eligibility that depend on baselines |
| [`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md) | Data-quality baselines, separately |
| `TS-006` `UA-12`, `TS-008` `UA-23` | The protocols B1 and B4 reuse, so baseline and verification are comparable |
| [`CG-012`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) | Evidence and sourcing |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Monthly until zero unbaselined KPIs remain (`BL-11`); then at each wave gate |
| Trigger for out-of-cycle review | A metric restatement (`KD-25`) invalidating a baseline; a new KPI; a new benefit line; a restatement request under `BL-07` |
| Owner | Programme Manager with the CFO office |
| Data file | `RP-015_Baseline_Register.csv` — 95 KPIs × 13 fields · `RP-015_Measurement_Evidence/` · `RP-015_Restatements.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is `W0` — the earliest wave in the register — and it is being written after Categories 00 to 13.** `06-02` §6 requires baselines signed **before** the consuming wave, and the earliest benefit is measured from **W2** (technician productivity, BDT 130 lac). **Every wave already begun has begun without signed baselines**, and `BL-05` means a baseline measured now for a W1 or W2 metric is already contaminated in the pilot branches | Programme Manager with CFO | **Immediate — the W0 gate has passed** |
| **O-02** | **44 of 95 KPIs have no usable baseline** and `06-02` §6 states they cannot claim a benefit. Roughly **BDT 396 lac of the 876 lac base case** rests on improvement benefits whose baselines are weak or absent. **This has not been stated to the Steering Committee in one place before this file** | CFO with Programme Manager | **Immediate — Steering item** |
| **O-03** | **The four class-`B` measurement exercises have no owner, no schedule and no budget.** B1 needs 120 timed observations, B2 needs 1,200 job records coded, B3 needs a two-week effort census across several functions, B4 needs counts at 6 locations and 10 vans. **`06-01` §4 does not allocate business time for any of them**, and B3 is the one carrying the −90% reporting target | Programme Manager with each benefit owner | **W1 — B1, B2 and B4 before W2; B3 before any −90% claim** |
| **O-04** | **`BL-03` requires the measurement method to match the `RP-001` definition, and `RP-001` defines 8 of 250 metrics.** §4.4 step 1 sequences definition immediately before measurement per metric, which is workable — **but it makes `RP-001` `O-02` and this file's `O-03` a single critical path** that no plan currently shows | BI Lead with Programme Manager | **W1** |
| **O-05** | **Several `06-02` §2.10 platform KPIs have a baseline equal to their target** — `KPI-085` ≥ 99.9%, `KPI-086` < 400 ms, `KPI-087` > 99.9%. `RP-001` `O-04` records the same finding. **Either they are pre-programme measurements that happen to meet target, or the column transcribes the target** — and in the second case they are class `C` absolutes, not improvement benefits | BI Lead with CTO | **W1** |
| **O-06** | **`04-00` carries portal KPIs with baselines that `06-02` §2 does not register** — `P03` walk-in intake against ~10 minutes, `P06` reporting effort −90%, `P02` daily active usage. **This file's scope covers them (§2) and they are not in the 95**, so the true baseline population is larger than 95 and has not been counted | Programme Manager with BI Lead | **W1** |
| **O-07** | **Class `C` requires targets restated as absolutes** (`BL-06`), which changes how they appear in `06-02` §3.1's benefit model. Roughly BDT 334 lac of the case is new-business absolutes. **Whether those may be presented as "benefit" in the same table as improvement benefits is a business-case presentation question**, and the Month 42 audit will ask it | CFO with Programme Manager | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the baseline schema
- [x] **44 of 95 unbaselined KPIs enumerated from `06-02` §2 with the value counts, extending `00-07` H2-10 from one instance to the register-wide position**
- [x] **The ordering problem stated first — define, measure, target, build — and the programme's actual order acknowledged rather than glossed**
- [x] Thirteen-field baseline schema, with the measurement-basis field identified as what the Month 42 audit reads
- [x] **Four baseline classes including `NOT MEASURABLE` as a valid recorded answer, and genuine zero distinguished from unmeasured**
- [x] An eight-step measurement programme that sequences metric definition immediately before measurement, per metric
- [x] **Four standing class-`B` exercises specified, reusing the `TS-006` and `TS-008` protocols so baseline and verification are comparable**
- [x] The `SP-002` seam stated with a reuse rule, so the same activity is not measured twice
- [x] Twelve rules stated, including never-adjust-to-improve-a-variance and zero-is-a-measurement
- [x] **Baseline readiness assessed against all 14 benefit lines, with the exposure quantified at ~BDT 396 lac of 876 and located in the improvement benefits**
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` the `W0` gate has passed — outstanding; baselines for W1/W2 metrics are already contaminated in pilot branches**
- [ ] **`O-02` ~BDT 396 lac of improvement benefit has weak or absent baselines — outstanding; Steering item**
- [ ] **`O-03` the four measurement exercises are unowned and unbudgeted — outstanding**
- [ ] Named approvers recorded — **pending CFO and Programme Manager**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
