---
id: DA-008
title: Data Quality Management Plan
category: 03 — Data & Information Architecture
code: DA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: MDM Lead
approver: Chief Data Officer (unappointed — see DA-003 §5)
standards_basis: >
  ISO/IEC 25012 (data quality model) · ISO 8000-61:2016 (data quality management process) ·
  DAMA-DMBOK 2.0 (2024 maintenance revision) — Data Quality knowledge area
traces_to: >
  PGD-000 DA-008 · DM-011 (migration quality rules) · RP-016 (scorecard, 12 domains) ·
  DI-06 · M64 · DA-003 (accountability) · NFR-039
depends_on: DA-002 · DA-003 · DA-004 · RP-016 · DM-011
verified_on: 2026-08-18
priority: P2
needed_by: W3
enumeration_timestamp: 2026-08-18 14:30 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# DA-008 — Data Quality Management Plan

### Category 03 · Code `DA` · ISO/IEC 25012 · ISO 8000-61:2016 · DAMA-DMBOK 2.0

---

## 1. Purpose

Two strong documents already exist, and between them they leave a gap.

| Document | Covers | Does not cover |
|---|---|---|
| **`DM-011`** (35 KB) | Migration quality: rule register, profiling dimensions, cleansing, matching, thresholds, survivorship, remediation queue | **Anything after go-live.** It is a migration standard and says so |
| **`RP-016`** (25 KB) | The **scorecard definition**: 12 domains, four dimensions, per-domain weights, thresholds, timeliness windows, what a red score blocks | **How quality is managed** — who profiles what, when, how a defect is fixed, how prevention works |

**Neither governs ongoing production data quality across 51 branches and 500–2,000 marketplace
sellers.** `DM-011` ends at cutover; `RP-016` measures without managing.

This document is the management plan: the operating cycle, the prevention-first hierarchy, the
profiling schedule, the remediation workflow with a drain rate, and the consequences that make a red
score mean something.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The seam with `DM-011` and `RP-016`, stated explicitly |
| 2 | Quality dimensions and their measurement (ISO/IEC 25012) |
| 3 | **The prevention hierarchy** — why measurement is the last resort |
| 4 | The rule register in production, continuous with `DM-011`'s |
| 5 | Profiling: what, when, at what cost |
| 6 | **The remediation workflow**, with a declared drain rate |
| 7 | Consequences — what a red score actually blocks |
| 8 | The **external-actor problem**: 500–2,000 sellers entering data we do not control |
| 9 | Roles, cadence and reporting |
| 10 | The `M64` timing gap in production |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Migration-time cleansing, matching, survivorship | `DM-011` | One-time; continuous with this by design (§2) |
| Scorecard definition, weights, thresholds | **`RP-016`** | Retained unchanged; this document manages against it |
| Match/merge in steady state | `DA-004` | Deduplication is a quality outcome, designed there |
| Field definitions and valid values | `DA-002`, `DA-009` | A rule tests against them |
| Warehouse quality gates | `DA-007` §11.1 | Load-time, not source-time |
| Test data quality | `QA-004` | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Data stewards** | §7 is the daily work; §6 is the queue |
| Domain owners (`DA-003` §3.2) | §9 — accountable for their domain's score |
| M64 developers | §5 rule register; §7 remediation |
| Branch and marketplace operations | §8 — the prevention controls that land on them |
| CDO | §10 reporting |

---

## 2. The Seam

> **`RP-016` §4.1 already names its seam with `DM-011`.** This document is the third piece, and the
> boundary is stated so no rule is written twice.

| Phase | Owner | Rules | Queue |
|---|---|---|---|
| **Pre-go-live** — profiling, cleansing, matching, load | **`DM-011`** | `DQ-01`…`DQ-26` | Migration stewardship queue, funded by the migration team |
| **Measurement** — how quality is scored | **`RP-016`** | 12 domains, 4 dimensions, weights, thresholds | — |
| **Post-go-live management** — prevention, detection, remediation, prevention improvement | **`DA-008`** | `PQ-nn` (§5.2) | **Business-as-usual queue, §6** |

| # | Rule |
|---|---|
| **SM-01** | **A rule keeps the same identifier before and after go-live.** `DM-011` §3 already requires this: *"the same rule keeps the same id in both, so pre- and post-go-live quality are comparable"* |
| **SM-02** | `RP-016`'s scorecard is the **single measurement instrument**. This document does not define a second one |
| **SM-03** | Where a `DM-011` rule has no production equivalent (a one-time encoding check), it is **retired at cutover with a recorded reason**, not silently dropped |

---

## 3. Quality Dimensions

**Four dimensions, per `RP-016` §4.4**, mapped to ISO/IEC 25012 characteristics and made measurable.

| Dimension | ISO/IEC 25012 | Question | Measurement |
|---|---|---|---|
| **Completeness** | Completeness | Is the value present where it should be? | Non-null / expected, per field, scoped by applicability |
| **Validity** | Syntactic + semantic accuracy | Does the value conform to its rule? | Passing rows / total, per rule |
| **Uniqueness** | Uniqueness (consistency) | Is the entity recorded once? | 1 − (duplicate candidates / population) |
| **Timeliness** | Currentness | Is the value current enough to act on? | Within the `RP-016` §4.5 freshness window |

### 3.1 Two dimensions deliberately not scored

| Dimension | Why not scored |
|---|---|
| **Accuracy** (does it match reality?) | **Unmeasurable without an external reference.** A customer's address is "accurate" only if someone goes there. Approximated by timeliness (`RP-016`'s explicit choice) and by delivery-completion confirmation (`MD-007` `is_verified`) |
| **Consistency across systems** | The ERP is the system of record; there is no second system to be consistent with. The **portal reconciliation** (`05-03` §3.4) and the **cross-system reconciliation** (DI-07, CD-241) cover it as an integration concern |

> **Not scoring accuracy is honest rather than lazy.** A scorecard that claims to measure accuracy
> without an external reference measures validity and calls it something else — and then a green
> accuracy score is read as "the data is right".

---

## 4. The Prevention Hierarchy

> **Measurement is the last resort, not the first.** A scorecard is how you find out you already have
> a problem.

| Level | Control | Cost of a defect | Example |
|:--:|---|---|---|
| **1** | **Make it impossible** — schema constraint, FK, check, exclusion | Zero — never occurs | `DA-001` §6: `NOT NULL`, `ck_`, `EXCLUDE` on overlapping periods |
| **2** | **Reject at entry** — hard business rule (**H** class) | Seconds — the user fixes it | `BRU-SRM-01`: no service order without an identified device |
| **3** | **Warn at entry** — soft rule (**S** class) | Minutes — the user may proceed | Address without a postcode |
| **4** | **Detect in flight** — automation, reconciliation | Hours to days | Nightly duplicate detection (`DA-004` §4.2) |
| **5** | **Detect on scorecard** | Weeks — a person must find and fix it | `RP-016` monthly score |
| **6** | **Discover downstream** | Months, and visible to a customer or a regulator | A rejected warranty claim; a wrong Mushak |

| # | Rule |
|---|---|
| **PH-01** | **Every quality rule declares the highest level at which it can be enforced, and is enforced there** |
| **PH-02** | A rule enforced at level 5 that **could** be enforced at level 1 or 2 is a **design defect**, recorded as one |
| **PH-03** | **A rising score with no level-1–3 change is measurement, not improvement.** Remediation closes a defect; prevention stops the next one |
| **PH-04** | Every remediation item asks *"what would have prevented this?"*, and the answer is a backlog item |

> **PH-03 is the rule that stops a quality programme becoming a cleaning programme.** Cleansing 4,000
> duplicate parties raises the score once. Adding create-time deterministic matching (`DA-004` §4.2)
> stops the next 4,000.

---

## 5. The Rule Register

### 5.1 Continuity with `DM-011`

`DM-011` §3 establishes `DQ-<DOMAIN>-nnn`, permanent, never reused, each carrying an
`error_message_id` resolving in `UI-004`, and states these are *"the migration-time expression of the
~300–500 `M64` domain quality rules"*.

| # | Rule |
|---|---|
| **RR-01** | **The same identifier space continues into production.** No second register |
| **RR-02** | Every rule declares: dimension (§3), domain (`DA-003` §3.2), **prevention level (§4)**, severity, and the message id |
| **RR-03** | Severity follows `05-05`: **H** hard block · **A** approved override · **S** soft warning · **C** computed |
| **RR-04** | A rule producing rejections above its declared tolerance is **reviewed before the records are** (`DQ-24`) — a 30% rejection rate usually indicts the rule |
| **RR-05** | A withdrawn rule is `active = false` with date and reason; **never deleted** |

### 5.2 Production-only rule classes

Six classes that do not exist at migration time.

| Class | Example | Level |
|---|---|:--:|
| **`PQ-DECAY`** | Contact not confirmed within the `RP-016` freshness window | 5 |
| **`PQ-EXTERNAL`** | Seller-supplied listing data failing catalogue conformance (§8) | 2 |
| **`PQ-DRIFT`** | A code value in use that is not in its `DA-009` register | 1 |
| **`PQ-ORPHAN`** | A `resident_key` with no resident row (`DA-001` RR-03) | 4 |
| **`PQ-RECON`** | Portal and ERP party counts diverge (`05-03` §3.4) | 4 |
| **`PQ-EXPIRY`** | A certification expiring within 30 days and unrenewed | 4 |

> **`PQ-EXPIRY` is the one with the sharpest consequence.** `RP-016` weights D6 Certification
> timeliness at **40%** with the highest thresholds in the estate (99/97), because *"`KPI-063` targets
> zero claims rejected for an uncertified technician… `BRU-HRM-01` acts on the record, not on
> reality."* A certification record two weeks stale is a rejected claim.

---

## 6. Profiling

| Scope | Cadence | Depth |
|---|---|---|
| **12 scored domains** (`RP-016` §4.3) | **Monthly** | Full — all four dimensions, all rules |
| Party and contact (D1, D2) | **Weekly** | Uniqueness and timeliness only — the fastest-degrading domains |
| Certification (D6) | **Daily** | Expiry only — cheap and consequential |
| New/changed records | **Continuous** | Rule evaluation at write (levels 1–3) |
| Full estate outside the 12 domains | **Per wave gate** | Completeness and validity on `DA-002`-registered mandatory fields |

| # | Rule |
|---|---|
| **PR-01** | Profiling runs against the **warehouse**, never the OLTP primary (`RP-006` `SM-13`) |
| **PR-02** | Profiling cost is **bounded and measured**; a profile that degrades the estate is stopped |
| **PR-03** | **Every profile run is comparable to the last.** A changed rule creates a new version, and the trend break is labelled |
| **PR-04** | Profiling of **residency-classified fields runs inside the residency service**; the values never leave Z4 (`DA-001` RS-04) |

> **PR-04 is a real constraint on profiling.** Uniqueness on NID cannot be computed by pulling NIDs
> into a profiling job. It is computed inside CD-233 and only the **count** returns.

---

## 7. Remediation

### 7.1 The workflow

```
  DETECT ──► TRIAGE ──► ASSIGN ──► FIX ──► VERIFY ──► PREVENT
    │          │          │         │        │          │
  rule      severity   steward   source   re-run     PH-04:
  fires     + domain   by domain  system   the rule   what would
                                                       have stopped
                                                       this?
```

### 7.2 Queue rules — carried from `DM-011` and made continuous

| # | Rule | Source |
|---|---|---|
| **RQ-01** | Every blocking rejection enters the queue with **the rule, the record verbatim and a named owner** | `DQ-21` |
| **RQ-02** | **The queue has a declared drain rate and a target date per wave. A queue with no drain rate is a bin** | `DQ-22` |
| **RQ-03** | Items open at a wave gate are **reported by count and by rule** — never carried silently | `DQ-23` |
| **RQ-04** | Remediation output **re-enters at the same tier**, never as a shortcut | `DQ-25` |
| **RQ-05** | **Every closed item records a prevention answer** (PH-04) | New |
| **RQ-06** | An item open beyond its domain's target is **escalated to the domain owner**, then to the Council | New |

### 7.3 The capacity problem, stated

`DM-011` `DQ-16` sizes the migration queue in **thousands of decisions** at two minutes each.
**Production adds a continuous arrival rate on top of that backlog**, and the migration team is gone.

| # | Rule |
|---|---|
| **CQ-01** | Each domain declares a **steward time allocation per wave** (`DA-003` `SW-01`) |
| **CQ-02** | **Arrival rate is measured from the first month of live operation**, so the allocation is sized from data, not from hope |
| **CQ-03** | Where arrival exceeds drain for **two consecutive months**, the domain owner must either **resource it or raise a prevention backlog item** — the two legitimate responses |
| **CQ-04** | **A steward with no allocated time is an unresourced control and is reported as one** (`DA-003` `SW-04`) |

---

## 8. The External-Actor Problem

**500–2,000 marketplace sellers and 17+ brand partners enter data we do not control.** No existing
document addresses this, and it is the structural difference between this estate's quality problem and
an ordinary ERP's.

| Actor | Enters | Risk |
|---|---|---|
| **Marketplace sellers** | Listings, prices, availability, own stock, profile, KYC documents | Volume, low switching cost, no employment relationship |
| **Brand partners** | Rate cards, claim rules, recall notices, bulletins | Low volume, **high consequence** — a wrong rate card mis-prices every claim |
| **Corporate clients** | Bulk asset uploads, bulk service requests (CSV) | Bulk, unvalidated at source |
| **Vendors** | Catalogue, pricing, lead times, invoices | Feeds three-way match |

### 8.1 Controls

| # | Control | Level |
|---|---|:--:|
| **EX-01** | **Validate at the boundary, reject at entry.** An external actor's submission is rejected with a message they can act on (API-11: Bengali and English) | **2** |
| **EX-02** | **Never auto-accept into the golden record.** External-supplied master data enters as a **proposal** requiring steward acceptance where it affects a shared concept | 2 |
| **EX-03** | **Bulk upload is validated whole before any row commits.** A partially applied CSV is worse than a rejected one | 2 |
| **EX-04** | **Scorecard by actor, not only by domain.** A seller's data quality is part of their `fix.seller.score`, and falling below threshold reduces visibility then suspends — the mechanism `P07` already defines | 4 |
| **EX-05** | Brand rate cards are **effective-dated and versioned** (`DA-001` §4.7); a new card never silently restates prior claims | 1 |
| **EX-06** | External submissions are **quarantined from the warehouse** until accepted, so a bad listing does not move a metric | 4 |

> **EX-04 is the control that scales.** With 2,000 sellers, no steward can review every listing.
> Making quality part of the seller's own score, with a consequence they feel, moves enforcement from
> our stewards to their self-interest — and `P07` already carries the scoring and suspension
> machinery.

---

## 9. Roles, Cadence and Consequence

### 9.1 Accountability

| Role | Accountable for | Source |
|---|---|---|
| **Domain owner** (12) | The domain's score, and the decision to resource or prevent | `DA-003` §3.2 |
| **Data steward** | The queue, the fixes, the prevention answers | `DA-003` §4.1 |
| **MDM Lead** | The rule register, cross-domain arbitration, this plan | `MD-001` §2.2 |
| **CDO** | Reporting quality risk to the Council and the Board | `DA-003` CDO-08 |
| **Module squads** | Level 1–3 prevention controls in their own modules | PH-01 |

### 9.2 Cadence

| Activity | Cadence |
|---|---|
| Rule evaluation at write | Continuous |
| Certification expiry check | Daily |
| Party/contact profiling | Weekly |
| **Full scorecard** | **Monthly** — `RP-016` |
| Queue review per domain | Monthly |
| **Council review** | Monthly through W1–W5, quarterly after (`DA-003` §8) |
| Rule register review | Per wave gate |
| Prevention backlog review | Per wave gate |

### 9.3 Consequences — what a red score blocks

`RP-016` §4.6 defines them. This document adds the **management** consequence.

| Score | `RP-016` consequence | **Management consequence (this document)** |
|---|---|---|
| **Green** | Normal | — |
| **Amber** | Flagged | Domain owner states a cause and an action at the monthly review |
| **Red** | **Blocks** per `RP-016` §4.6 | **The domain owner must resource the queue or raise a prevention item (CQ-03).** A red score with neither is escalated to the Council |
| **Red two consecutive months** | — | **Council agenda item with the domain owner present.** Not a dashboard colour |

---

## 10. Reporting

| Report | Audience | Cadence | Content |
|---|---|---|---|
| **Domain scorecard** | Domain owner, steward | Monthly | `RP-016` — four dimensions, weighted, against threshold |
| **Estate summary** | Council, CDO | Monthly | 12 domains, trend, reds, open queue depth vs drain |
| **Prevention report** | Council | Wave gate | Rules moved down the hierarchy; defects prevented rather than fixed |
| **External-actor report** | CCO, marketplace ops | Monthly | Quality by seller and brand; suspensions triggered |
| **Board** | Board | Quarterly | Personal-data quality risk, via `DA-003` CDO-08 |

| # | Rule |
|---|---|
| **RP-01** | **Every report states its measurement date and the rule-set version.** A score is not comparable across a rule change (PR-03) |
| **RP-02** | **A red score is never reported without its queue depth and drain rate.** A score without capacity context is a number nobody can act on |

---

## 11. The `M64` Timing Gap in Production

> `DM-011` §2.9 records it: **`M64` is a W2 module** and its gate *"arrives one wave after the batches
> it is supposed to score."* `DQ-26` designs the migration interim. **Production has the same gap.**

| Capability | Needed from | `M64` delivers |
|---|---|---|
| Level 1–3 prevention (constraints, hard rules) | **W1** | **Not `M64`'s** — built in each module. Available |
| Certification expiry check | **W1** — dispatch depends on it | W2 |
| Duplicate detection | **W1** | W2 (interim in `DA-004` §9.1) |
| Rule register and scorecard | W2 | W2 |
| Remediation queue | **W1** | W2 |

| # | Interim rule |
|---|---|
| **IM-01** | **Levels 1–3 need no module.** Every W1 module carries its own constraints and **H**-class rules; that is the majority of prevention |
| **IM-02** | The W1 remediation queue is the **`DA-004` §9.1 M33 task list**, using the same rule identifiers `M64` will use |
| **IM-03** | **The scorecard does not exist in W1.** Quality is managed by rule rejections and the queue, not by a score. Recorded as a bounded gap in `GV-005` with an expiry at the W2 gate |
| **IM-04** | `M64` **re-scores the W1 population** when it arrives (`DQ-26`) |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| **Q-01** | **Is steward time allocated per domain per wave (CQ-01)?** Twelve domains with no allocation is twelve unresourced controls | Domain owners / Programme Manager | **W1 — blocking** | The whole plan |
| **Q-02** | Is `RP-016`'s **D2 24-month contact freshness window** correct? `RP-016` `O-05` labels it an assumption and calls it *"the most consequential number in this file"* | MDM Lead / CCO | W3 | D2 scoring |
| **Q-03** | Is EX-04 accepted — seller data quality feeding `fix.seller.score` with visibility and suspension consequences? | CCO / Marketplace Ops | W7 | The 2,000-seller control |
| **Q-04** | Are the ~300–500 `M64` domain rules authored, and by whom? `DM-011` names the number; no register holds them | MDM Lead / domain owners | W2 | §5 |
| **Q-05** | Is IM-03 accepted — **no scorecard in W1**? | Council / CDO | W1 | W1 quality visibility |
| **Q-06** | Does accuracy stay unscored (§3.1), or is an external reference procured for address and contact verification? | CDO / CCO | W4 | Scorecard scope |

---

## 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-D8-01 | Relationship to `DM-011`/`RP-016` | Supersede; **third piece with a stated seam** | **Third piece** | Both are good and neither covers production management | `SM-01` keeps rule ids continuous |
| D-D8-02 | Rule register | New space; **continue `DQ-<DOMAIN>-nnn`** | **Continue** | Pre- and post-go-live quality must be comparable | One register, two phases |
| D-D8-03 | Accuracy dimension | Score it; **do not score it** | **Do not** | Unmeasurable without an external reference; scoring it would mislabel validity | Approximated by timeliness |
| D-D8-04 | Programme emphasis | Measure and clean; **prevention hierarchy first** | **Prevention (§4)** | Cleansing raises a score once; prevention stops the next occurrence | PH-03, PH-04 mandatory |
| D-D8-05 | External actors | Steward review; **boundary validation + actor scorecard** | **Both** | No steward reviews 2,000 sellers' listings | EX-04 uses `P07`'s existing machinery |
| D-D8-06 | Red-score consequence | Dashboard colour; **resource or prevent, or escalate** | **Resource or prevent** | A red score with neither is a number nobody acts on | CQ-03, §9.3 |
| D-D8-07 | W1 scorecard | Build an interim; **no scorecard, rules only** | **Rules only** | Levels 1–3 deliver most of the value and need no module; a throwaway scorecard would not be comparable to `M64`'s | IM-03 registered with expiry |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The seam with `DM-011` and `RP-016` is stated, with no rule written twice | §2 |
| AC-02 | Dimensions map to ISO/IEC 25012, and unscored dimensions are justified | §3, §3.1 |
| AC-03 | **A prevention hierarchy exists and every rule declares its level** | §4 PH-01…PH-04 |
| AC-04 | The rule register continues `DM-011`'s identifier space | §5.1 |
| AC-05 | Profiling has a schedule, a cost bound and a residency-safe method | §6 |
| AC-06 | **The remediation queue has a declared drain rate and a capacity rule** | §7.2, §7.3 |
| AC-07 | The external-actor problem has controls that scale to 2,000 sellers | §8 |
| AC-08 | A red score has a management consequence, not only a colour | §9.3 |
| AC-09 | The `M64` W1/W2 gap has an interim with a registered expiry | §11 |

**Definition of done.** Complete when every criterion is met, Q-01 is resolved, and `PGD-000`'s
`DA-008` row is updated.

---

## 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | **`DM-011`** | Migration rules, thresholds, survivorship — continuous with this |
| Upstream | **`RP-016`** | The scorecard. **Retained unchanged; this manages against it** |
| Upstream | `DA-002` | Rules test registered elements and their valid values |
| Upstream | `DA-003` | Domain owners and stewards; `SW-01` allocation |
| Upstream | `DA-009` | `PQ-DRIFT` tests against the code-list register |
| Downstream | **`M64`** | The rule register and remediation queue |
| Downstream | `DA-004` | Duplicate rate is D1's dominant dimension (40% weight) |
| Downstream | `DA-007` §11.1 | Warehouse load gates |
| Downstream | `P07` | EX-04 seller scoring |
| Downstream | `DA-003` `GM-05` | The scorecard is a governance metric |

---

## 16. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./DA-002_Data_Dictionary.md` · `./DA-003_Data_Governance_Framework_and_Stewardship_Model.md` ·
`./DA-004_Master_Data_Management_Design.md` · `./DA-007_Analytical_and_Dimensional_Model_Specification.md` ·
`./DA-009_Reference_Data_and_Code_List_Register.md`

**Workspace**
`../../project_content/12_Data_Migration_Content/DM-011_Data_Quality_Rules_Cleansing_and_Deduplication_Standard.md` ·
`../../project_content/14_Reporting_Analytics_and_KPI/RP-016_Data_Quality_Scorecard_Definition.md` ·
`../../project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-007_Address_Format_and_Validation_Standard.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M64_Master_Data_Management_and_Configuration.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md`

**External standards**

| Standard | Version | Verified |
|---|---|---|
| ISO/IEC 25012 — Data quality model | Current | 2026-08-18 |
| ISO 8000-61 — Data quality management: process reference model | 2016 | 2026-08-18 |
| [DAMA-DMBOK](https://www.damadmbok.org/) — Data Quality knowledge area | 2.0 (2024 maintenance revision) | 2026-08-18 |

---

## 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Establishes the third piece between `DM-011` (migration) and `RP-016` (measurement): the **prevention hierarchy**, the production rule classes, the remediation queue with a capacity rule, and controls for **500–2,000 external actors** that no existing document addresses | *Pending — CDO, unappointed* |

---

*`DA-008` · Category 03 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
