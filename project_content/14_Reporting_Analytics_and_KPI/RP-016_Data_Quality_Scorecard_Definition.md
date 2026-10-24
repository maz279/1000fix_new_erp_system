---
id: RP-016
title: Data Quality Scorecard Definition
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: MDM with BI
author: MDM Lead with BI Lead and the data-domain owners
reviewers: [CTO delegate, Chief Data Officer, Solution Architect, Data Migration Lead, Finance Manager, Operations Director, HR Manager]
approver: MDM Lead with BI Lead
content_class: E
purpose: >
  The completeness, validity, uniqueness and timeliness measures for each master-data domain, with the
  thresholds at which a domain is declared unfit and the consequences that follow. Master data degrades
  silently after migration: nothing fails, no error is raised, and the first symptom is a warranty claim
  rejected for a wrong serial or a dispatch sent to an address last touched in 2019. The scorecard is
  what makes degradation visible before it causes a transaction to fail, and it is the gate that stops
  a dashboard reporting confidently on data that is no longer fit.
traces_to: [M64, M62, M62 §9, DM-011, DM-013, MD-001, MD-013, MD-021, MD-022, MD-024, MD-006, MD-007, MD-012, RP-001, RP-002, RP-004, RP-006, RP-011, RP-012, RP-015, 05-06 §8, 05-06 DI-06, 05-05 §12.5, TS-005, TS-017, OP-006]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md §2.2 Profiling dimensions — Completeness (% non-null per field per source file), Validity (% passing the format rule; the BD mobile format is the hardest), Uniqueness (estimated duplicate rate per candidate key), Timeliness (age distribution of last-touched date; an address last touched in 2019); §2.1 the quality-rule register; §2.6 thresholds set before the load by the business; §2.9 the M64 gate and its timing problem
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §8 DI-06 — data quality tests run on every warehouse load and failures block dependent refreshes; DI-07 cross-system reconciliation runs nightly with divergence alerting
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §12.5 AUT-059 — a data quality test fails: block the dependent dashboard refresh and alert the data owner; failure behaviour "show last-known-good with a staleness warning"
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64_Master_Data_Management_and_Configuration.md — single ownership per entity, golden record and survivorship, master data change control
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md §9 BRU-DAT-09 every dataset and metric has a named business owner and technical steward; BRU-DAT-07 an unexpected source schema change stops the pipeline
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Data Quality Scorecard Definition

| Item | Value |
|---|---|
| Dimensions | **4** — completeness, validity, uniqueness, timeliness (**from `DM-011` §2.2**) |
| Domains scored | **12** (§4.3) |
| Consequence of failure | **Blocks dependent dashboard refresh** (`AUT-059`, `DI-06`) |
| Metric range | `KPI-450`…`KPI-499` (`RP-001` §4.3) |
| Wave | W3 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the scorecard schema in §4.2. All six sections retained in order.

---

## 1. Purpose

The register states the mechanism: *"master data degrades silently after migration; the scorecard is
what makes degradation visible before it causes failure."*

**Silently is the operative word.** A customer record whose phone number was correct at migration and
whose owner changed number in 2027 produces no error. The record is complete, valid and unique. It is
simply wrong, and the first symptom is an OTP that never arrives and a booking that fails — attributed
to the notification gateway, not to the data.

`DM-011` §2.2 already defines the four dimensions and profiles them **before the load**. This file
extends the same four dimensions into **steady state**, which is a different problem: migration
profiling is a one-time gate with a known deadline; steady-state scoring is a continuous measure with no
deadline and therefore no natural owner.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Steady-state measures | `DM-011` profiles once. **Nothing measures the data on day 400**, which is when the degradation matters |
| Thresholds | `DI-06` blocks a dependent refresh on a failing test, and *failing* is undefined |
| Domain ownership | `M64` assigns single ownership per entity; **nobody is accountable for that entity's quality score** |
| A consequence | A scorecard nobody acts on is a report (`RP-002` `CT-01`) |
| A gate on analytics | `RP-011` `LT-10` and `RP-012` `AL-10` both defer to this file to decide when data is too poor to rank or alert on. **Without it they cannot** |
| A degradation signal | The first symptom is a failed transaction, and the cause is attributed elsewhere |

---

## 2. Scope

**In scope.** The four dimensions applied to steady-state master data; the twelve scored domains; per-
domain thresholds and their consequences; the scorecard's own metrics; ownership; remediation routing;
publication; and the boundary against migration profiling.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| **Migration-time profiling, cleansing, matching and survivorship** | **`DM-011`** — §4.1 states the seam |
| Migration reconciliation and control totals | `DM-013` |
| Master-data governance, ownership model, change control | **`M64`**, `MD-001` |
| The field-level validation rules themselves | The `MD` files — `MD-007` address, `MD-013` party, `MD-021`/`MD-022` device and parts, `MD-024` fault codes |
| Warehouse quality tests as a build gate | `M62`, `DI-06` — this file supplies the definitions those tests implement |
| Dataset certification | `RP-006` |
| Alert delivery | `RP-012` — the quality alert is `AUT-059`; §4.6 states the routing |
| Business-KPI baselines | `RP-015` |
| Transactional data quality — a wrong price on one order | The owning module's business rules |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **MDM Lead** (accountable with BI) | The scorecard and the remediation queue |
| **Data-domain owners** (`M64`) | Their domain's score and what they must fix |
| **BI Lead** | The `DI-06` test implementation and the `AUT-059` gate |
| **Data Migration Lead** | The handover from `DM-011` profiling to steady-state scoring |
| **Chief Data Officer** | Personal-data accuracy, a PDPA rectification duty (`NFR-093`) |
| **`RP-011`, `RP-012`** | The gate that decides when not to rank and when not to alert |
| **`R33` IT Administrator** | The `RP-004` `C14` panel 6 quality-failure panel |

---

## 4. Content

### 4.1 The seam with `DM-011`

**The four dimensions are `DM-011`'s, reused verbatim** (`CP-01`). What changes is when, why and what
happens next.

| | **`DM-011`** | **`RP-016`** *(this file)* |
|---|---|---|
| When | **Before the load**, once per source | **Continuously**, after go-live |
| Purpose | Decide whether data may be loaded | Detect degradation and gate analytics |
| Threshold set by | The business, before the load (`DM-011` §2.6) | The domain owner, reviewed per wave (§4.4) |
| Consequence of failure | Load blocked; remediation queue (`DM-011` §2.8) | **Dependent dashboard refresh blocked** (`AUT-059`); domain flagged; `RP-011`/`RP-012` gated |
| Ends | At cutover | Never |
| Owner | Data Migration Lead | **MDM Lead with the domain owner** |

> **`DM-011` §2.9 records "the `M64` gate and its timing problem".** That problem does not end at
> cutover — it becomes this file's, because `M64` is the governance mechanism and the domain owners it
> assigns are the people who must act on a falling score. `O-02`.

### 4.2 The scorecard schema

| # | Field | Content |
|---:|---|---|
| 1 | `domain` | The master-data domain (§4.3) |
| 2 | `owner` | The `M64` single owner of the entity — named function |
| 3 | `steward` | Technical steward (`BRU-DAT-09`) |
| 4 | `completeness` | % of required-at-target fields populated; **which fields are required is the definition, not the measure** |
| 5 | `validity` | % passing the owning `MD` file's format rule |
| 6 | `uniqueness` | Estimated duplicate rate per candidate key |
| 7 | `timeliness` | % of records touched within the domain's freshness window (§4.5) |
| 8 | `composite` | Weighted score (§4.4) |
| 9 | `threshold_amber` / `threshold_red` | Two thresholds, two consequences |
| 10 | `consequence` | What is blocked at red (§4.6) |
| 11 | `trend` | Direction over the last three periods — **the field that detects degradation** |
| 12 | `remediation` | Open remediation items and their owner |

**Field 11 is the reason this file exists.** A domain at 94% is not interesting; a domain that was 98%
three months ago and is now 94% is the finding, because at that rate it reaches the threshold in a
quarter and nothing has failed yet.

### 4.3 The twelve scored domains

| # | Domain | `MD` source of truth | Owner | Why it matters |
|---:|---|---|---|---|
| D1 | **Party — customer, corporate, seller, vendor** | `MD-013`, `MD-015` | MDM Lead | Duplicates break Customer 360, loyalty and consolidated invoicing |
| D2 | **Contact — phone, email, address** | `MD-007`, `MD-013` | MDM Lead | **The highest-degradation domain.** A stale mobile breaks OTP, notification and dispatch |
| D3 | **Device and asset** | `MD-021` | Technical Director | A wrong serial blocks a warranty claim (`BRU-WTY-01`) and destroys rework detection |
| D4 | **Spare part and compatibility** | `MD-022` | Inventory Manager | A wrong compatibility mapping issues the wrong part |
| D5 | **Employee** | `MD-012` | HR Manager | Drives identity, dispatch eligibility and payroll |
| D6 | **Competency and certification** | `MD-010`, `MD-011` | Quality Manager | **An expired certification not recorded means `KPI-063` is wrong and a claim is rejected** |
| D7 | **Geography and zone** | `MD-006`, `MD-005` | MDM Lead | Zone assignment, dispatch, league normalisation |
| D8 | **Branch and location** | `MD-003`, `MD-004` | Operations Director | Scope, stock location, league |
| D9 | **Catalogue — service and product** | `MD-019`, `MD-020` | Commercial | Pricing and what is sellable |
| D10 | **Contract and entitlement** | `MD-032`, `MD-031` | Account Management | `BRU-SRM-03` and `BRU-CTR-04` both gate on it |
| D11 | **Financial — accounts, dimensions, tax codes** | `MD-035`, `MD-036`, `MD-037` | Finance Manager | Postings, Mushak mapping, margin by dimension |
| D12 | **Codes — fault, resolution, reason, status** | `MD-024`, `MD-025`, `MD-026`, `MD-027` | Technical Director | **Every metric defined on a code set moves when the codes do** (`RP-001` `KD-14`) |

**Twelve, aligned to `M64` entity ownership rather than to the 48 `MD` files.** Scoring 48 files would
produce 48 scores with no single owner per score; scoring twelve domains means each score has exactly
one accountable owner, which is `M64`'s own model.

### 4.4 Thresholds and weighting

**Weights differ by domain** because the dimensions do not matter equally everywhere.

| Domain | Completeness | Validity | Uniqueness | Timeliness | Amber | Red |
|---|---:|---:|---:|---:|:--:|:--:|
| D1 Party | 25% | 20% | **40%** | 15% | 95% | **90%** |
| D2 Contact | 30% | 30% | 10% | **30%** | 92% | **85%** |
| D3 Device | 30% | **35%** | 25% | 10% | 95% | **90%** |
| D4 Part | 30% | 30% | 20% | 20% | 95% | 90% |
| D5 Employee | **40%** | 30% | 20% | 10% | 98% | **95%** |
| D6 Certification | 30% | 20% | 10% | **40%** | **99%** | **97%** |
| D7 Geography | 30% | 40% | 20% | 10% | 98% | 95% |
| D8 Branch | 40% | 30% | 20% | 10% | 99% | 97% |
| D9 Catalogue | 30% | 30% | 20% | 20% | 96% | 92% |
| D10 Contract | **40%** | 30% | 10% | 20% | 98% | **95%** |
| D11 Financial | 30% | **40%** | 10% | 20% | **99%** | **97%** |
| D12 Codes | 30% | 30% | 20% | 20% | 98% | 95% |

**The weightings carry the judgements:**

| Choice | Reason |
|---|---|
| D1 uniqueness at 40% | Duplicate parties are the defining party-data failure, and `DM-011` §2.5 already treats matching as the hard problem |
| D2 timeliness at 30% and the lowest thresholds | **Contact data degrades fastest and is least controllable** — people change numbers. Setting 99% here would put the domain permanently red and train everyone to ignore it |
| D3 validity at 35% | A serial or IMEI either matches the format or it does not, and a wrong one blocks a claim |
| D6 timeliness at 40% with the highest thresholds | **`KPI-063` targets zero claims rejected for an uncertified technician.** A certification record two weeks stale is a rejected claim, and `BRU-HRM-01` acts on the record, not on reality |
| D11 validity at 40% and thresholds at 99/97 | Tax-code and account validity is a statutory exposure, not a quality preference (`NFR-021`, `NFR-101`) |
| D2's amber at 92% versus D6's at 99% | **A single threshold across twelve domains would be wrong eleven times.** Thresholds are per domain because degradation rates are per domain |

### 4.5 Timeliness windows

Timeliness needs a window per domain, or "stale" has no meaning. `DM-011` §2.2 gives the example of an
address last touched in 2019.

| Domain | Freshness window | Basis |
|---|---|---|
| D2 Contact | **24 months** since last confirmation | Beyond two years, mobile-number accuracy in Bangladesh degrades materially — **assumption, `O-05`** |
| D6 Certification | **Current** — expiry in the future | Binary; `BRU-HRM-01` acts on it |
| D10 Contract | Current — within term | Binary |
| D3 Device | 36 months since last service or confirmation | Devices are re-confirmed at each service |
| D5 Employee | 12 months since last review | Annual HR cycle |
| D1 Party | 24 months | Follows contact |
| D9 Catalogue, D11 Financial, D12 Codes | **Current version** — no stale records permitted | Configuration, not transactional data |
| D7 Geography, D8 Branch | 12 months; **and immediately on a gazetted change** | `MD-006` records five new upazilas created in May 2026 |

> **D2's 24-month window is the most consequential number in this file and it is an assumption.**
> Confirmation at each service contact is the natural mechanism — a customer who used the service in the
> last two years has confirmed their number by receiving an OTP. `O-05`.

### 4.6 Consequences — what a red score blocks

A scorecard with no consequence is a report. These are the consequences, and they escalate.

| Score | Consequence |
|---|---|
| **Green** | Published; trend monitored (field 11) |
| **Amber** | Domain owner notified; remediation item raised with a date; **trend reported in `RP-010`** |
| **Red** | **1.** `AUT-059` **blocks the dependent dashboard refresh**; dependent views show last-known-good **with a staleness warning**, never stale data presented as current. **2.** `RP-011` `LT-10` — affected branches shown as *"data quality below threshold"* rather than ranked. **3.** `RP-012` `AL-10` — metric alerts on the domain suppressed and a quality alert raised instead. **4.** Escalation to the Chief Data Officer where the domain holds personal data |
| **Red for two consecutive periods** | **Steering item.** A domain red twice is a governance failure, not a data problem |

**Consequence 1 is `DI-06` and `AUT-059` verbatim**, and its failure behaviour is theirs: *show
last-known-good with a staleness warning*. **This file does not invent the gate; it supplies the
threshold that trips it**, which is the piece `DI-06` leaves undefined.

### 4.7 Rules

| # | Rule |
|---|---|
| **QS-01** | **The four dimensions are `DM-011`'s** and are not redefined (`CP-01`) |
| **QS-02** | **Every domain has exactly one owner**, from `M64`'s entity ownership (`BRU-DAT-09`) |
| **QS-03** | **Completeness is measured against required-at-target fields**, and which fields are required is a stated definition per domain, not a measurement artefact |
| **QS-04** | **Validity is measured against the owning `MD` file's rule**, never against a rule invented here |
| **QS-05** | **Thresholds are per domain** (§4.4). A single programme-wide threshold is wrong for most domains |
| **QS-06** | **Every score carries its trend** over three periods (field 11); a falling green score is reported |
| **QS-07** | **A red score has a consequence that operates automatically** (§4.6), not a notification |
| **QS-08** | **Timeliness needs a window** per domain (§4.5); without one it is unmeasurable |
| **QS-09** | **The scorecard's own metrics live in `KPI-450`…`KPI-499`** and are defined in `RP-001` like any other metric |
| **QS-10** | **Remediation is routed to the domain owner with a date**, and open items appear on the scorecard (field 12) |
| **QS-11** | **Personal-data accuracy is a statutory duty**, not only a quality measure — `NFR-093` requires rectification with controller notification within 30 days, so a D1 or D2 failure has a PDPA dimension |
| **QS-12** | **The scorecard is published weekly** (`RP-013` `SUB-18`) and reported monthly in the pack (`RP-010` section 10) |
| **QS-13** | **A domain cannot be scored on a dataset that is not certified** (`RP-006`); an uncertified source makes the score unverifiable |
| **QS-14** | **Counted, with its enumeration date** (`CP-11`) |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`DM-011`](../12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md)** | The four dimensions, and the handover from profiling to steady state |
| **`M64`**, `MD-001` | Entity ownership, which determines the twelve domain owners |
| The `MD` files behind each domain | The validation rules validity is measured against (`QS-04`) |
| **[`RP-006`](RP-006_BI_Semantic_Layer_Data_Dictionary.md)** | Certified datasets the scores are computed on (`QS-13`) |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | `KPI-450`…`KPI-499` definitions (`QS-09`) |
| `DI-06`, `AUT-059` | The gate this file supplies thresholds for |
| [`RP-011`](RP-011_Branch_League_Table_Definition_and_Scoring_Rules.md) `LT-10`, `RP-012` `AL-10` | The two consumers that depend on the red state |
| [`RP-004`](RP-004_Dashboard_Specification_Pack_Operational_Consoles.md) `C14` panel 6, `RP-010` section 10, `RP-013` `SUB-18` | Where it is published |
| `NFR-093` | The PDPA rectification duty behind `QS-11` |
| `TS-005` `SIT-J-001`/`-002` | Where the gate is verified |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Thresholds per wave gate; windows annually |
| Trigger for out-of-cycle review | A domain red twice; a new `MD` domain; a gazetted geography change; a `DM-011` threshold change at a later cutover; a PDPA rectification pattern |
| Owner | MDM Lead with BI Lead; each domain has its `M64` owner |
| Data file | `RP-016_Domain_Scorecards.csv` — 12 domains × 12 fields · `RP-016_Dimension_Rules.csv` · `RP-016_Remediation_Queue.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is W3 and `RP-011` `LT-10` and `RP-012` `AL-10` both defer to it, at W4.** That ordering is correct — **but `RP-004` `C14` panel 6 shows quality-test failures at W1**, so the console panel exists three waves before the thresholds that define a failure. `DI-06` blocks a refresh on a "failing" test with no definition of failing until W3 | Programme Content Lead with MDM Lead | **W1 — an interim threshold set is needed** |
| **O-02** | **`DM-011` §2.9 records "the `M64` gate and its timing problem", and `M64` is a W1 foundation while this file is W3.** The twelve domain owners in §4.3 are assigned by `M64` entity ownership; **`MD-001` §governance assigns data-domain ownership and no owner has confirmed accountability for a quality score**, which is a different commitment from owning the entity | MDM Lead with `M64` owner | **W3** |
| **O-03** | **The twelve threshold pairs and forty-eight weightings in §4.4 are proposed by the content function.** `DM-011` §2.6 sets the precedent that thresholds are set **by the business before the load**; the same must apply here, and no domain owner has seen these. **A threshold that blocks a dashboard refresh is an operational commitment** | MDM Lead with each domain owner | **W3 — before the gate is enabled** |
| **O-04** | **`QS-03` requires a stated list of required-at-target fields per domain, and none exists.** Completeness is meaningless without it: measuring 200 fields when 40 are required produces a permanently low score, and measuring 5 produces a permanently high one. `DM-011` has this for migration; **the steady-state list is not the same list** | MDM Lead with each domain owner | **W3** |
| **O-05** | **D2's 24-month contact-freshness window is an assumption** (§4.5) and it drives 30% of the weight in the highest-degradation domain. **No evidence supports 24 rather than 18 or 36 months**, and the whole D2 score moves with it. `RP-014`-style evidence discipline (`CG-012`) applies | MDM Lead with Customer Service Manager | **W3** |
| **O-06** | **`QS-11` makes a D1/D2 failure a PDPA matter and no rectification workflow exists.** `NFR-093` requires rectification with controller notification within 30 days; **the scorecard will detect inaccurate personal data at scale and there is nowhere to route it** beyond the remediation queue. `LG-012` is unwritten in operative form | Chief Data Officer with MDM Lead | **W3 — before 13 May 2027 enforcement** |
| **O-07** | **Nothing measures whether a record is *correct*, only whether it is complete, valid, unique and fresh.** A phone number that is well-formed, unique, populated and confirmed 3 months ago can still be wrong. **The four dimensions cannot detect accuracy**, and §1's example — the customer who changed number — passes all four. The only real accuracy signal is transaction feedback: a failed OTP, a returned delivery, a bounced email. **That signal is not currently fed back into any domain score** | MDM Lead with BI Lead | **W3 — the most valuable extension to this scorecard** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the scorecard schema
- [x] **The four dimensions reused verbatim from `DM-011` §2.2 rather than redefined (`CP-01`)**
- [x] The `DM-011` seam stated across six dimensions — before-the-load versus continuous, and the ownership handover
- [x] Twelve-field schema, with the trend field identified as the one that detects degradation
- [x] **Twelve domains aligned to `M64` entity ownership rather than to 48 `MD` files, so each score has one owner**
- [x] Per-domain weightings and two thresholds, with the judgement behind each weighting stated
- [x] **D2 contact given the lowest thresholds because it degrades fastest, and D6 certification the highest because `KPI-063` targets zero**
- [x] Timeliness windows per domain, with the assumption flagged
- [x] **Four automatic consequences at red, including the `AUT-059` gate this file supplies the threshold for**
- [x] Fourteen rules stated, including thresholds-are-per-domain and a red score having an automatic consequence
- [x] The PDPA rectification dimension of personal-data accuracy recorded
- [x] **`O-07` states plainly that the four dimensions cannot detect accuracy, and names the transaction-feedback signal that could**
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `C14` panel at W1 against W3 thresholds — outstanding**
- [ ] **`O-03` thresholds and weightings unowned — outstanding; blocks enabling the gate**
- [ ] **`O-04` no required-field list per domain — outstanding; completeness is unmeasurable without it**
- [ ] **`O-07` no accuracy measure — outstanding; the scorecard's known blind spot**
- [ ] Named approvers recorded — **pending MDM Lead and BI Lead**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
