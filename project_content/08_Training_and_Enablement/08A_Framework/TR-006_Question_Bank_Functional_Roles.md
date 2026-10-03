---
id: TR-006
title: Question Bank — Functional Roles
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with the domain owners of each functional area
reviewers: [Quality Manager, HR Director, Finance Manager, Operations Director, Security Lead, Inventory Manager, Localisation Lead]
approver: HR Director with Quality Manager
content_class: C
purpose: >
  The item bank that establishes a user is competent before they are granted production access to a
  system that touches money, stock, pay and customer commitments. Access granted on attendance is
  access granted on nothing; this bank is what turns the competence gate in TR-002 CU-05 from a
  policy sentence into a testable condition.
traces_to: [M22, M29, M19, M20, M15, M21, M23, M30, 05-04, MD-009, MD-010, MD-026, TR-001, TR-002, TR-003, TR-004, TR-007, TR-008, TR-011, TR-012, TR-014, TR-015, TR-016, TR-017, TR-021, TS-002]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: TR-006_Question_Bank_Functional_Roles_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-026 assessment delivery with pass criteria, attempt limits and result recording; §5.4 FR-LMS-038 competence evidence file
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §5 — the registered roles and their access scopes; 05-05 §2 BR-STD-06 overrides are permitted only where designed and are always logged with a reason
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-LMS-01 overdue mandatory training restricts the affected work types; BRU-FIN, BRU-INV and BRU-SRM rule families whose breach the bank tests recognition of
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-010 walk-in intake time under 3 minutes, KPI-064 mandatory training completion on time
    verified: 2026-08-17
    class: P1
  - source: Classical item-analysis practice — item difficulty and discrimination computed from live response data; items that fail to discriminate are retired regardless of face validity
    verified: 2026-08-17
    class: P3
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Question Bank: Functional Roles

| Item | Value |
|---|---|
| Audience role(s) | `R06`–`R09`, `R15`, `R17`–`R22`, `R24`, `R26`–`R35` — every non-technician operational role |
| Headcount | **~500 users** across the functional roles |
| Duration | 30–60 minutes per role assessment |
| Delivery mode | System-delivered (`M22` FR-LMS-026) with **sandbox transaction components** (`TS-002`) |
| Language | Bengali primary for branch-facing roles; English acceptable for head-office functions (`LS-07`, `DS-18`) |
| Prerequisites | Layer 1 universal core · the role's Layer 2 pack |
| Certification outcome | **Internal competence record gating production access** (`CU-05`, `LS-14`) |
| Wave | W2 |

> **Template conformance.** As `TR-005`: `TPL_Training_Course_Pack.md` applied to an assessment
> instrument. All ten sections retained in order and answered at bank level; §11–§13 justified
> additions. **Governance shared with `TR-005` is referenced rather than restated** (`CP-01`) — item
> rules `QB-01`, `QB-05`…`QB-20`, bank governance and item analysis all apply here unchanged.

---

## 1. Learning Objectives

**The bank must discriminate whether the user can operate their role's transactions correctly and
recognise the rules that constrain them.**

| # | The bank must discriminate whether the user can… | Applies to |
|---|---|---|
| 1 | Complete their role's core transaction correctly, first time | All roles |
| 2 | Recognise the **hard business rules** that block their action, and why | All roles |
| 3 | Select the correct reason code when overriding or exception-handling (`MD-026`, `BR-STD-06`) | All roles |
| 4 | Identify what they may **not** do — the boundary of their access scope (`05-04`) | All roles |
| 5 | Escalate correctly, to whom, with what evidence (`SP-005`) | All roles |
| 6 | Handle customer data within their permitted scope | All customer-facing roles |
| 7 | Recognise a transaction that will produce a financial or statutory error | Finance, cashier, procurement |
| 8 | Recognise a stock action that will corrupt inventory accuracy | Inventory, store keeper, warehouse |
| 9 | Recognise a dispatch or SLA decision that breaches a commitment | Dispatch, branch, contact centre |
| 10 | Recognise an administrative action that is destructive and irreversible | `R33` System Administrator |

**`QB-21`: item 4 is assessed in every role bank.** The commonest access-related incident is not a
person doing their job badly; it is a person doing somebody else's job because nothing told them
where the boundary was.

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| **Production access grant** (`CU-05`) · role assignment in `M29` | Layer 1 core · the role's Layer 2 pack | **Bank reviewed 6-monthly; re-assessment on major release (`TR-024`) and every 24 months** |

---

## 3. Module Outline — *the bank blueprint*

**`QB-22`: one cell per role family, not one per role.** Roles sharing a transaction set share a
cell with a role-specific extension, so the bank stays maintainable.

| # | Cell | Roles | Core transactions tested |
|---:|---|---|---|
| 1 | **Service intake and branch** | `R08`, `R06` | Intake, device identification, condition capture, expectation setting, token, handover |
| 2 | **Dispatch** | `R07` | Assignment, priority, SLA risk, zone, capacity, re-routing |
| 3 | **Workshop** | `R09` | Bench assignment, WIP, escalation, QC gate, release |
| 4 | **Inventory and stores** | `R17`, `R18`, `R20` | Issue, return, transfer, van reconciliation, count, quarantine |
| 5 | **Procurement** | `R19` | Requisition, PO, receipt, three-way match, exception |
| 6 | **Finance** | `R26`, `R27`, `R28` | Invoice, credit, receipt, reconciliation, VAT treatment, claim evidence |
| 7 | **Counter cash** | `R29` | Collection, method, reconciliation, banking, shortfall |
| 8 | **Commercial** | `R21`, `R22`, `R24` | Quote, contract, entitlement, renewal, seller governance |
| 9 | **HR** | `R30`, `R31` | Attendance exception, leave, payroll input, joiner data |
| 10 | **Quality** | `R32` | NCR, CAPA, audit finding classification |
| 11 | **Contact centre** | `R34`, `R35` | Queue, disposition coding, transfer, complaint, wrap-up |
| 12 | **System administration** | `R33` | Configuration, permission, destructive-action confirmation, audit trail |
| 13 | **Logistics** | `R15` | Manifest, custody, exception, POD |

**Thirteen cells.**

### 3.1 Form composition

| Competence area | Share | Items on a 30-item form | Critical? |
|---|---:|---:|:--:|
| Core transaction correctness | 35% | 10–11 | |
| **Hard business rules** (`BRU-*`, `BR-STD-*`) | 20% | 6 | **✔ critical** |
| **Access-scope boundary** (`05-04`) | 10% | 3 | **✔ critical** |
| Reason codes and exception handling (`MD-026`) | 10% | 3 | |
| Escalation | 10% | 3 | |
| Data handling within scope | 10% | 3 | **✔ critical for customer-facing** |
| Role-specific consequence recognition | 5% | 1–2 | |

**Form length: 30 items. Pass: 80% overall, 100% on declared critical items** (`AS-04`).

### 3.2 Bank size

| Driver | Value |
|---|---|
| Form length | 30 items |
| Exposure ratio | 5× to 6× per cell — lower than `TR-005` because populations per cell are smaller and re-attempt volume is lower |
| Items per cell | **150–180** |
| Cells | 13 |
| **Total bank at steady state** | **~1,950–2,340 items** |
| **Minimum viable per cell** (`QB-04`) | 90 items → **~1,170 total** |

---

## 4. Facilitator Guide — *item-writing rules*

**All item-writing rules from [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) §4 apply unchanged
(`QB-01`, `QB-05`…`QB-15`).** Three additions specific to functional roles:

| # | Rule | Class |
|---|---|:--:|
| **QB-21** | Access-scope boundary is assessed in every cell | **H** |
| **QB-23** | Business-rule items present the **situation**, not the rule identifier. "You are asked to issue a part against a repair the customer has not approved" tests `BRU-SRM-11`; "What is `BRU-SRM-11`?" tests nothing | **H** |
| **QB-24** | Distractors for functional items are drawn from **real exception and override records** (`MD-026` reason codes actually used, override logs) once the system is live; before then, from the domain owner's stated common errors, marked as such | **H** |
| **QB-25** | Financial and statutory items are reviewed by the Finance Manager; access-scope items by the Security Lead | **H** |

---

## 5. Participant Workbook Contents

As `TR-005` §5, with the blueprint published and items withheld (`QB-16`). Role-specific additions:

| Section | Purpose |
|---|---|
| **What your access permits and what it does not** | The `05-04` scope for the role, in plain language — this is also the answer to item area 4 |
| The hard rules that will block you, and why they exist | Prevents the "the system won't let me" support call |
| Your escalation route | `SP-005` |
| The reason codes you will use | `MD-026` subset for the role |

---

## 6. Exercises — *sandbox transaction components*

`AS-03` requires a non-written component for any certification that gates. For functional roles that
component is a **completed sandbox transaction**, not a practical demonstration.

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Complete the role's core transaction end to end | `P03` workspace sandbox | Role-appropriate seeded data | Completed correctly, within the role's target time where one exists (e.g. `KPI-010` intake under 3 minutes) |
| 2 | **Handle a seeded exception** requiring a reason code | Sandbox | Seeded exception | Correct code from `MD-026`; correct route |
| 3 | **Encounter a hard-rule block and respond correctly** | Sandbox | Seeded blocking condition | Does **not** attempt to circumvent; escalates or corrects |
| 4 | Attempt an action outside the role's scope | Sandbox | Out-of-scope object | **Recognises the boundary and stops** (`QB-21`) |
| 5 | Cell-specific high-consequence transaction | Sandbox | Per cell — a payment, a stock adjustment, a permission change, a payroll input | Correct, with the confirmation step honoured |

**`QB-26`: exercise 3 is scored on the response to the block, not on avoiding it.** A user who
tries three workarounds and then escalates has demonstrated the wrong instinct even though they
ended in the right place.

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| Written form, 30 items | 60% | **80% overall, 100% on critical** | 3 | 24 months, or on major release |
| Sandbox transactions, 5 components | 40% | **All five passed** | 3 | 24 months |
| **Both must pass independently** | — | — | — | — |

> Conforms to [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md). **Item analysis, calibration, exposure control and
> rotation follow `TR-005` §7.1–§7.2 unchanged** (`QB-18`, `QB-19`).

**`QB-27`: passing this assessment is the condition for production access to the role's money-,
stock- or customer-affecting functions** (`CU-05`, `LS-14`). Access before the pass is an exception
requiring the same approval and logging as any override (`BR-STD-06`).

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| **Your access scope** — what this role may and may not do | One page, bilingual | `TR-022` |
| Hard rules that will block you | One page | `TR-022` |
| Reason-code quick reference for the role | One page | `TR-022` |
| Escalation card | One page | `TR-022` |

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| Item authors | The **domain owner** of each cell — Operations for dispatch, Finance for finance, Security for access scope |
| Item reviewers | A second domain reviewer; Finance Manager for financial items; Security Lead for access items (`QB-25`) |
| Sandbox assessors | L&D, with the domain owner defining the success criterion |
| Bengali authoring | Branch-facing cells authored in Bengali (`DS-17`); head-office cells may be English-first |
| Item analysis | As `TR-005` — **unowned**, `O-03` |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Perceived fairness and job-relevance | Diagnostic only (`LS-02`) |
| **Learning** | First-attempt pass rate per cell | Monitored; near-100% triggers review (`AS-06`) |
| **Behaviour** | **Override rate, exception rate and error rate of newly certified users vs the population** | Newly certified not materially worse after 30 days |
| **Result** | Contribution to `KPI-010` intake time · `KPI-064` mandatory completion · reduction in access-related incidents and correction transactions | Per `06-02` and `RP-001` |

**Required Drivers** (`LS-04`): reinforce — `TR-022` job aids · encourage — champions on the floor
(`TR-023`) · monitor — override and error-rate tracking per newly certified user · reward —
production access granted, and the competence record in `M22`.

> **The Behaviour measure here is unusually good and worth using.** Unlike most training, this one
> has a clean natural experiment: newly certified users enter the system on a known date, and their
> override, exception and correction rates are visible from day one. If they are worse than the
> population after 30 days, the assessment did not discriminate — regardless of what the pass rates
> say.

---

## 11. Bank Governance

**As [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) §11 unchanged** — item codes, edit-after-live prohibition,
6-monthly review, retirement triggers, Bengali parity, storage in `M22`, restricted access.

Two additions:

| Aspect | Rule |
|---|---|
| Release sensitivity | **A release that changes a transaction invalidates the items testing it.** `TR-024` release training reviews affected cells at every release — the functional bank ages far faster than the technical one |
| Rule sensitivity | A change to any `BRU-*` or `BR-STD-*` rule triggers immediate review of the items testing it |

---

## 12. Effort, Coverage and the Resourcing Position

| Item | Position |
|---|---|
| Items required, steady state | **~1,950–2,340** across 13 cells |
| Minimum viable | **~1,170** (90 per cell) |
| Items written | **0** |
| Authoring rate | 6–10 calibrated items per domain-owner hour including review |
| **Effort to minimum viable** | **~120–195 hours**, spread across 13 domain owners |
| Effort to steady state | ~195–390 hours |
| **Annual churn** | **Higher than `TR-005`** — release sensitivity (§11) means functional items age with the software, not with the devices. Estimate 25–35% a year |
| Author population | Domain owners, **not** the `R12` specialists — this bank does **not** compete with Category 07 |

> **The one piece of good news in the training effort picture.** `TR-006` is authored by thirteen
> different domain owners at roughly 10–15 hours each. It is the only substantial content
> commitment in this category that does not draw on the 15–30 `R12` specialists already
> over-committed to `KB` articles and `TR-005`.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) | The governing policy |
| [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) | Shared item rules, analysis and governance (`CP-01`) |
| [`TR-002_Role_Based_Curriculum_Map.md`](TR-002_Role_Based_Curriculum_Map.md) | `CU-05` — the access gate this bank operates |
| `TR-007`, `TR-008`, `TR-011`, `TR-012`, `TR-014`, `TR-015`, `TR-016`, `TR-017`, `TR-021` | The packs whose competences the cells assess |
| [`../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) | Job aids produced in §8 |
| [`../08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md`](../08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) | Release sensitivity in §11 |
| `05-04` Role, Permission and Access Matrix | Access-scope items |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Reason-code items |
| `M29` Identity, Access and Information Security | The access grant this gates |
| `TS-002` | Sandbox data for §6 |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The bank is empty**; ~1,170 items minimum before `CU-05` can gate access for any role. Twelve `TR` packs land in W1 and this bank lands in W2 — **so W1 roles receive production access before the gate exists** | L&D with domain owners | **W1, not W2 — raised as audit finding TR-05** |
| **O-02** | **`TS-002` sandbox data does not exist** (Category 13 unstarted). All five §6 exercises depend on it, and `QB-24` distractors depend on live override records that also do not exist yet | Test Lead with L&D | **W1** |
| **O-03** | **Item analysis is unowned** — same gap as `TR-005` `O-03` | L&D with CTO | W2 |
| **O-04** | Whether `M29` can gate access on an `M22` competence signal is unconfirmed (`TR-002` `O-07`, `TR-004` `O-03`). **`QB-27` is the rule that depends on it most directly** | CTO with Security Lead | **Before W1 go-live** |
| **O-05** | Thirteen domain owners must each author 90+ items. **None has been asked**, and none has this in a workplan | L&D with the functional directors | **W1** |
| **O-06** | `QB-24` prefers distractors from real override and exception data, which does not exist pre-go-live. The interim — domain owners' stated common errors — must be **marked as provisional** and revisited after 6 months of live data | L&D | W3 review |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — ten sections retained, bank-level interpretation, additions justified
- [x] **Shared governance referenced rather than duplicated from `TR-005` (`CP-01`)**
- [x] Blueprint organised by role family rather than by role, with the reason stated (`QB-22`)
- [x] Access-scope boundary made a universal assessed area (`QB-21`)
- [x] Business-rule items required to present the situation, not the rule identifier (`QB-23`)
- [x] Sandbox transactions used as the non-written component, with the block-response exercise scored on instinct (`QB-26`)
- [x] Passing made the explicit condition for production access (`QB-27`)
- [x] Release sensitivity identified as the dominant ageing driver for this bank
- [x] Behaviour-level measure identified as a genuine natural experiment
- [x] Effort stated, and the absence of `R12` competition noted as the one favourable fact
- [x] All internal links resolve
- [x] `BR-STD-06`, `BRU-LMS-01` cited to `05-05`; `FR-LMS-*` to `M22`; `KPI-010`/`-064` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` bank available before W1 access grants — outstanding; the wave placement is wrong**
- [ ] **`O-05` thirteen domain owners tasked — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
