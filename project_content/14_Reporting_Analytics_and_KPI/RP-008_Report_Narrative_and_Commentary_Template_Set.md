---
id: RP-008
title: Report Narrative and Commentary Template Set
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Operations
author: Finance Manager with Operations Director, Quality Manager and Content Design
reviewers: [CFO, Operations Director, Quality Manager, CCO delegate, BI Lead, Content Design Lead, Programme Manager]
approver: CFO with Operations Director
content_class: D
purpose: >
  The structures in which monthly operations, financial, quality and executive commentary is written —
  what a variance explanation must contain, what it may not contain, and in what order. Numbers without
  narrative are re-interpreted by every reader, and narrative without a structure is re-invented every
  month, which makes commentary incomparable between periods and turns a management pack into a
  collection of essays whose tone tracks the author's confidence rather than the business.
traces_to: [RP-001, RP-002, RP-003, RP-010, RP-011, RP-015, 06-02, 06-02 §6, CG-003, CG-012, CG-004, M23, M60, SP-020, TS-018]
priority: P2
wave: W5
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §6 Benefit Tracking Discipline — monthly KPI dashboard with benefit owners commenting on variance; quarterly Steering review; attribution discipline requiring a documented causal mechanism; "honest reporting — missed benefits are reported as missed, with the reason. A benefit case that is never revisited is not a business case"
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md — every factual, statutory, pricing or capability claim names a primary source with a verification date
    verified: 2026-08-20
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md — sentence case, voice, tense, person, terminology precedence for enterprise content
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Report Narrative and Commentary Template Set

| Item | Value |
|---|---|
| Templates | **5** — operations, financial, quality, executive, benefit variance (§4.3) |
| Applies to | `RP-003` view commentary slots · `RP-010` board pack · `RP-011` league commentary |
| Cadence | Monthly, with a quarterly executive variant |
| Authors | Benefit and process owners, **not analysts** |
| Wave | W5 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the commentary field schema in §4.2. All six sections retained in order.

---

## 1. Purpose

`06-02` §6 requires the PMO to publish a monthly KPI dashboard on which **benefit owners comment on
variance**, and it sets the standard for that commentary explicitly: *"missed benefits are reported as
missed, with the reason. A benefit case that is never revisited is not a business case."*

That is a content requirement with no content behind it. Left unstructured, monthly commentary
develops three predictable pathologies:

| Pathology | What it looks like |
|---|---|
| **Narration** | "SLA compliance was 91%, down from 93%." The reader could see that. Nothing has been added |
| **Attribution without mechanism** | "Performance improved due to the new system." `06-02` §6 explicitly excludes benefits with no documented causal mechanism |
| **Drift** | Month one explains variance against target; month four explains it against last month; month seven explains it against expectation. **The commentary becomes incomparable, which is the one thing it exists to be** |

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| A field schema | Every commentator writes what occurs to them, and the pack cannot be read across periods |
| A variance standard | A 2% miss and a 40% miss are written in the same register |
| An attribution rule | Benefit claims survive into the board pack without a mechanism, and `06-02` §6's attribution discipline is unenforceable |
| A prohibition list | Commentary becomes advocacy; the reader cannot tell a fact from a hope |
| Named authorship | Commentary written by the analyst who produced the number is a self-assessment |

---

## 2. Scope

**In scope.** The five commentary templates, their field schema, the variance-explanation standard,
attribution rules, prohibitions, authorship and review, and the relationship to the pack that carries
them.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The numbers being commented on | `RP-001` metrics via `RP-002`/`RP-003` |
| The pack's contents and order | **`RP-010`** — this file supplies the prose structures the pack assembles |
| Which view carries which commentary slot | `RP-003` §4.5 allocates ownership per view |
| Baselines a variance is measured against | `RP-015` |
| Statutory report narrative | `RP-009` — statutory returns carry prescribed content, not commentary |
| Style, voice, tense and terminology | `CG-003`, `CG-004` — this file adds structure, not style |
| Evidence and sourcing rules | `CG-012` — applied here, not restated |
| Non-conformance and CAPA narrative | `M23` — a CAPA has its own record; quality commentary summarises, it does not replace |
| Board minutes and decisions | Company secretarial |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Benefit owners** (`06-02` §3.5, fourteen named) | The monthly variance commentary they owe |
| **Process owners** | Operations and quality commentary |
| **CFO and Finance Manager** | Financial commentary and the close narrative (`SP-020`) |
| **CEO office** | The executive summary and its quarterly variant |
| **Operations Director** | League commentary, quarterly (`RP-011` `LT-11`) |
| **Programme Manager** | Benefit variance against the `06-02` §3.2 curve |
| **BI Lead** | Which slots exist and who owes them |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **NR-01** | **Commentary explains, it does not narrate.** A sentence a reader could derive from the chart is deleted |
| **NR-02** | **Every variance beyond its tolerance is explained; every variance inside it is silent.** Tolerances are set per metric in §4.4, so commentary volume tracks exception, not effort |
| **NR-03** | **Attribution requires a mechanism.** "Because X" is written only where the causal path is stated and evidenced (`06-02` §6). Otherwise the wording is "associated with" or "cause not yet established" — **and the latter is an acceptable, expected answer** |
| **NR-04** | **A miss is reported as a miss** (`06-02` §6). No qualifier softens it; the recovery action carries the optimism, not the description |
| **NR-05** | **Every explanation names an action, an owner and a date**, or states explicitly that no action is being taken and why |
| **NR-06** | **Commentary is written by the accountable owner, not by the analyst who produced the number.** The analyst supplies the number and the decomposition; the owner supplies the explanation |
| **NR-07** | **Prior-month commitments are revisited first** (§4.5). A commentary that never returns to last month's action is where accountability disappears |
| **NR-08** | **Every factual claim beyond the reported metrics carries a source** (`CG-012`) |
| **NR-09** | **A metric is named by its `RP-001` identifier and approved name**, never by a colloquial variant (`CG-004`) |
| **NR-10** | **A `Provisional` metric is described as provisional in the commentary**, not only labelled on the chart (`KD-22`) |
| **NR-11** | **A metric with no measured baseline may not be described as improved or worsened** (`KD-20`, `RP-015`). It is described as "measured at X; no baseline established" |
| **NR-12** | **Word limits are enforced** (§4.3). An unlimited commentary field is filled to the length of the author's anxiety |
| **NR-13** | **Data-quality caveats are stated where they apply** (`RP-016`). A number computed on a domain scoring below threshold is reported with that fact |
| **NR-14** | **No individual is named** in operational or executive commentary. Teams, branches, roles and processes are named; people are managed elsewhere |

### 4.2 The commentary field schema

Every commentary entry, in every template, carries these seven fields in this order.

| # | Field | Content | Limit |
|---:|---|---|---|
| 1 | `metric` | `KPI-nnn` and its approved name (`NR-09`) | — |
| 2 | `position` | The value, its comparator and the variance, stated once | 25 words |
| 3 | `explanation` | **Why**, with the mechanism where known and "cause not yet established" where not (`NR-03`) | 60 words |
| 4 | `evidence` | What supports the explanation — a drill, a count, a related metric, an external source (`NR-08`) | 25 words |
| 5 | `action` | What is being done, by whom, by when — or a stated decision not to act (`NR-05`) | 40 words |
| 6 | `prior_commitment` | The status of last period's action on this metric (`NR-07`) | 20 words |
| 7 | `confidence` | `High` · `Medium` · `Low` on the explanation, not on the number | one word |

**Field 7 is the field that makes the set honest.** A `Low` confidence explanation is not a failure of
commentary; it is accurate reporting of an unfinished investigation, and it tells the reader how much
weight to place on the action in field 5.

### 4.3 The five templates

| # | Template | Author | Cadence | Scope | Length |
|---:|---|---|---|---|---|
| **N1** | **Operations commentary** | Operations Director | Monthly | Service delivery, field, logistics, `RP-003` `E4` metrics | ≤ 8 entries |
| **N2** | **Financial commentary** | CFO with Finance Manager | Monthly, and at close | Revenue, margin, cash, receivables, close, statutory position | ≤ 10 entries |
| **N3** | **Quality commentary** | Quality Manager | Monthly | NCR, CAPA, complaints, rework, audit, recurring root causes | ≤ 6 entries |
| **N4** | **Executive summary** | CEO office | Monthly; extended quarterly | The three things the board must know; not a digest of N1–N3 | ≤ 400 words |
| **N5** | **Benefit variance** | Each of the fourteen benefit owners (`06-02` §3.5) | Monthly from the wave the benefit becomes realisable | One benefit line each, against the `06-02` §3.2 curve | ≤ 5 fields, per benefit |

#### `N1` Operations commentary — structure

1. **Prior commitments** — every action from last month with its status (`NR-07`)
2. **Exceptions** — each metric beyond tolerance, in the §4.2 seven-field form
3. **Emerging** — a metric inside tolerance but moving consistently for three periods, flagged before it breaches
4. **Branch outliers** — by exception only, and **by branch, never by manager** (`NR-14`); the league itself is quarterly (`RP-011` `LT-11`)
5. **Capacity and constraint** — the binding constraint this month, named
6. **Nothing else.** A metric within tolerance and not moving is absent

#### `N2` Financial commentary — structure

1. Prior commitments
2. **Revenue and margin** by stream, exceptions only, tied to `RP-003` `E2`
3. **Cash and working capital** — position, movement, and the 13-week view
4. **Close** — days taken, blockers, and whether `KPI-050`'s target was met (`SP-020`)
5. **Statutory** — filings made, on time, with zero adjustment; **any exception stated first** (`RP-009`)
6. **Leakage** — `KPI-056` unbilled work and `KPI-038` warranty leakage, with the recovery action
7. **Provisions, one-offs and restatements** — anything that makes this month incomparable, stated **before** the numbers that it affects

> **Item 7 placed before the numbers is deliberate.** A restatement disclosed after the figures has
> already misled the reader once.

#### `N3` Quality commentary — structure

1. Prior commitments, including **CAPA effectiveness verifications due** (`BRU-QMS-03`)
2. **Open non-conformances** by age, and any beyond their containment window
3. **Recurring root causes** across three periods — `BRU-QMS-09` escalates these automatically to management review, and this item is where they arrive
4. Complaints outside SLA, and the pattern if there is one
5. Rework and QC first-pass movement (`KPI-005`, `KPI-007`)
6. **Systemic observation** — one statement on whether quality is improving or the measures are, which are different things

#### `N4` Executive summary — structure

**Three things, 400 words, no metrics table.**

1. **What changed that matters** — one or two items, with the business consequence
2. **What is at risk** — the single item most likely to cause a miss, and what is being done
3. **What the board is asked to decide or note** — a decision request, or explicitly "nothing this month"

**`N4` is not a digest of `N1`–`N3`.** A summary assembled by shortening three commentaries produces
nine mild observations; the board needs the two that matter. Stated because the digest is what will
happen by default.

#### `N5` Benefit variance — structure

Per benefit line, against `06-02` §3.1 and the §3.2 realisation curve:

| Field | Content |
|---|---|
| `benefit` | The `06-02` §3.1 line and its owner (§3.5) |
| `plan_to_date` | From the §3.2 curve |
| `realised_to_date` | Measured, with the metric and its baseline named |
| `variance` | Value and % |
| `mechanism` | The documented causal path from system capability to financial effect (`06-02` §6, `NR-03`) |
| `baseline_status` | **`Measured` or `NOT MEASURED`** — and where the latter, **no benefit may be claimed** (`RP-015`, `NR-11`) |

> **`N5` will mostly read `NOT MEASURED` at first issue.** 44 of 95 registered KPIs have no baseline
> (`RP-001` `O-06`, `RP-015`). **That is the honest position and it is the point of the template** —
> `06-02` §6's rule becomes visible monthly rather than discovered at the Month 42 benefits audit.

### 4.4 Variance tolerances

`NR-02` needs numbers. These are proposed defaults; each metric's owner may tighten but not loosen.

| Metric class | Comment when variance exceeds |
|---|---|
| Statutory and compliance — `KPI-057`, `KPI-058`, `KPI-067` | **Any variance from target.** Zero means zero |
| Safety and data protection | **Any occurrence** |
| Financial control — leakage, billing accuracy, reconciliation | 0.5 percentage points, or any absolute breach |
| Customer-facing service — SLA, TAT, CSAT, first-time fix | 2 percentage points, or 3 consecutive periods of movement in one direction |
| Productivity and utilisation | 5% relative |
| Cost and inventory | 5% relative, or any threshold breach |
| Platform — uptime, latency | Any breach of the `NFR` target |
| Adoption — usage, self-service | 5 percentage points |

**Three consecutive periods of consistent movement is a trigger even inside tolerance** (`N1` item 3).
A metric drifting 1.5 points a month is inside a 2-point tolerance every month and 4.5 points down in a
quarter.

### 4.5 Authorship, review and the audit trail

| Rule | Detail |
|---|---|
| Author | The accountable owner (`NR-06`); the analyst supplies the number and its decomposition |
| Review | BI Lead checks metric names, identifiers and provisional labelling — **not the explanation** |
| Challenge | The Steering Committee challenges attribution quarterly (`06-02` §6) |
| Retention | Commentary is retained with the pack it appeared in (`RP-010`), because a benefits audit at Month 42 reads the explanations, not just the numbers |
| Prior commitments | Carried forward automatically into field 6; an action with no status is reported as "no status provided", never omitted |

### 4.6 Prohibitions

| Prohibited | Why |
|---|---|
| Narrating the chart (`NR-01`) | Consumes the reader's attention and adds nothing |
| "Due to the new system" with no mechanism | `06-02` §6 attribution discipline |
| Naming an individual (`NR-14`) | Commentary is a management artefact, not a performance review |
| Softening a miss (`NR-04`) | `06-02` §6 requires misses reported as misses |
| Describing an unbaselined metric as improved (`NR-11`) | There is nothing to have improved from |
| A colloquial metric name (`NR-09`) | `CG-004`; and it breaks the link to `RP-001` |
| Forward projections in `N1`–`N3` | Operational commentary reports the period; projections belong in `N4` item 2 or a plan |
| Comparisons to unnamed external benchmarks | `CG-012`; an unsourced benchmark is an assertion |
| An unexplained restatement | `N2` item 7; and `RP-001` `KD-25` requires the restatement declared |
| Commentary on a metric whose data-quality domain is below threshold, without saying so | `NR-13`, `RP-016` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | Metric names, identifiers, provisional status, direction |
| **[`RP-015`](RP-015_Benefits_Realisation_and_KPI_Baseline_Register.md)** | Baselines — without them `NR-11` renders most of `N5` as `NOT MEASURED` |
| **[`RP-010`](RP-010_Board_and_Management_Pack_Template.md)** | The pack that carries these templates |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md) §4.5 | Which view carries which slot and who owns it |
| [`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md) | League commentary, quarterly |
| [`RP-016`](RP-016_Data_Quality_Scorecard_Definition.md) | Data-quality caveats (`NR-13`) |
| `06-02` §3.1, §3.2, §3.5, §6 | Benefit lines, curve, owners and the tracking discipline |
| `CG-003`, `CG-004`, `CG-012` | Style, terminology and evidence |
| `M23`, `SP-020` | Quality records and the close procedure |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Quarterly with the Steering Committee's attribution challenge |
| Trigger for out-of-cycle review | A new benefit line; a tolerance dispute; a restatement; commentary found to have drifted from the schema |
| Owner | Finance Manager with Operations Director |
| Data file | `RP-008_Commentary_Templates.csv` · `RP-008_Variance_Tolerances.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`06-02` §6 requires monthly benefit commentary from the wave each benefit becomes realisable, and the earliest is W2** (technician productivity, `06-02` §3.1 line 2). **This file is W5**, so the first three years' worth of monthly commentary would be written without a template. The same forward-dependency shape as `AUDIT-014` TS-02 | Programme Content Lead with Finance | **W2 — `N5` needed first** |
| **O-02** | **`N5` cannot be completed for most benefit lines.** 44 of 95 baselines are unmeasured and `RP-015` is `P1`/W0, already overdue (`RP-001` `O-06`). **The template will correctly read `NOT MEASURED` against a BDT 876 lac benefit case**, and that is a Steering matter rather than a content one | Programme with Finance | **W0 — via `RP-015`** |
| **O-03** | **The §4.4 tolerances are proposed, not agreed.** Each metric owner may tighten but not loosen, and no owner has yet seen them. A tolerance set by the content function rather than the accountable owner will be ignored the first month it produces an unwelcome exception | Finance Manager with each metric owner | **W5 — with `RP-001` `O-02`** |
| **O-04** | **`NR-06` requires the owner to write and the analyst not to.** `06-01` §4 gives Module Business Owners 20% of their time and 1 Data/BI Engineer FTE from W4. **Monthly commentary across N1–N5 is roughly 20–30 owner-hours a month**, and it is not in the business-side commitment | Programme Manager | **W5** |
| **O-05** | **No mechanism carries `prior_commitment` forward.** Field 6 requires last period's action and its status, and without a tool that is a manual re-keying that will lapse by month three — which is exactly where `NR-07` says accountability disappears. `TS-018` `O-02` records the same tooling gap for defects | BI Lead with Platform Engineering | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the commentary field schema
- [x] **The three pathologies named — narration, attribution without mechanism, drift — so the templates are justified by failure mode**
- [x] Fourteen rules stated, including explain-don't-narrate, mechanism-required and no-individuals
- [x] Seven-field schema with word limits, including a confidence field on the explanation rather than the number
- [x] Five templates specified with author, cadence and structure
- [x] **`N4` explicitly not a digest of `N1`–`N3`, with the reason**
- [x] **`N5` designed to make `06-02` §6's no-baseline-no-benefit rule visible monthly rather than at the Month 42 audit**
- [x] Variance tolerances proposed per metric class, with a three-period drift trigger inside tolerance
- [x] Ten prohibitions each carrying its reason
- [x] Restatement disclosure placed before the affected numbers
- [x] All internal links resolve
- [x] Five open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `N5` needed at W2 against a W5 file — outstanding**
- [ ] **`O-02` most benefit lines will read `NOT MEASURED` — outstanding; a Steering matter**
- [ ] **`O-03` tolerances not agreed with metric owners — outstanding**
- [ ] Named approvers recorded — **pending CFO and Operations Director**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
