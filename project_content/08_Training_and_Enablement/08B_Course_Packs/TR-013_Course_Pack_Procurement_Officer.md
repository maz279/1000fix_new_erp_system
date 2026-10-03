---
id: TR-013
title: Course Pack — Procurement Officer
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Procurement
reviewers: [Procurement Manager, Finance Manager, Operations Director, Quality Manager, Legal Counsel, Localisation Lead]
approver: Finance Manager with Operations Director
content_class: D
purpose: >
  Trains 4–8 procurement officers who operate the company's principal cash-outflow control chain
  with vendor-facing consequence. A small team whose errors are expensive, slow to detect and
  externally visible: a three-way match not enforced is money paid for goods not received, and a
  vendor treated inconsistently is a relationship and a price the company loses.
traces_to: [M16, M42, M44, M52, M22, P03, P05, MD-016, MD-022, MD-026, MD-029, TR-001, TR-002, TR-004, TR-006, TR-022, UI-028, SP-004, SP-017, KB-009]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: TR-013_Course_Pack_Procurement_Officer_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md — requisition, sourcing, PO, receipt, three-way match, payment, exception handling; the company's principal cash-outflow control chain
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-INV-03 a purchase order cannot be raised for an item whose network-wide stock already exceeds the maximum level; BRU-INV-07 goods failing inspection go to quarantine; BR-STD-06 overrides permitted only where designed and always logged
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P05 targets over 90% of POs acknowledged and over 85% of invoices submitted through the portal, with a 60% cut in vendor phone queries
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Procurement Officer

| Item | Value |
|---|---|
| Audience role(s) | `R19` Procurement Officer |
| Headcount | **4–8** |
| Duration | **8 hours** over two days, plus 5 days supervised OJT |
| Delivery mode | Classroom with sandbox; single cohort |
| Language | English primary with Bengali parallel (head-office function, `DS-18`) |
| Prerequisites | Layer 1 universal core — **including anti-bribery and ethics** |
| Certification outcome | Functional competence record (`TR-006` cell 5) |
| Wave | W3 |

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Convert a requisition into a sourced, approved purchase order within authority | Sandbox + items |
| 2 | Enforce the **three-way match** and recognise every way it can be defeated | Practical + scenario |
| 3 | Recognise the stock-level block on a PO and respond correctly | Items keyed to `BRU-INV-03` |
| 4 | Manage vendor records, compliance documents and approval state | Sandbox keyed to `MD-016` |
| 5 | Run the `P05` vendor portal flow — PO acknowledgement, delivery, invoice submission | Sandbox |
| 6 | Handle a receipt exception — short, over, damaged, wrong, failed inspection | Practical keyed to `BRU-INV-07` |
| 7 | Apply approval authority and log every override with a reason | Items keyed to `SP-004`, `BR-STD-06` |
| 8 | **Recognise and escalate a conflict of interest or an inducement** | **Critical items** |
| 9 | Source a part correctly against `part_class` and brand requirement | Items keyed to `MD-022`, `KB-009` |
| 10 | Read vendor performance and act on it rather than on relationship | Scenario |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to procurement transactions · approval authority | Layer 1 core including ethics | On release (`TR-024`); 24 months. **Ethics annually** |

---

## 3. Module Outline

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | Procurement as a control chain, not a buying function | 30 min | Facilitated |
| 2 | The procurement console and the requisition-to-PO flow | 60 min | Walkthrough — `UI-028` |
| 3 | Sourcing, vendor selection and `MD-016` compliance state | 60 min | Practice |
| 4 | **The three-way match and how it fails** | 90 min | Practical + scenario |
| 5 | Receipt, inspection, quarantine and exceptions | 60 min | Practical — `BRU-INV-07` |
| 6 | Stock-level and duplicate-order blocks | 45 min | Items — `BRU-INV-03` |
| 7 | **`P05` vendor portal — what the vendor sees** | 60 min | Sandbox |
| 8 | Approval authority and override discipline | 45 min | Items — `SP-004` |
| 9 | **Ethics, conflict of interest and inducements** | 60 min | Facilitated + scenario |
| 10 | Part sourcing against `part_class` and brand requirement | 45 min | Practice — `KB-009` |
| 11 | Vendor performance and the difficult conversation | 45 min | Role play |
| | **Total** | **~8 hours** | |

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 1 | Every control in this chain exists because somebody, somewhere, paid for goods that never arrived | *"It's just paperwork."* |
| 4 | The three-way match fails most often not by fraud but by a receipt recorded from a delivery note rather than from the goods | *"The paperwork matched."* |
| 6 | `BRU-INV-03` blocks a PO where network stock already exceeds maximum. **The block is usually right and the branch asking is usually looking at their own shelf** | *"They need it urgently."* |
| 7 | What the vendor sees in `P05` is what determines whether they phone you. **Every field you leave blank is a phone call** | *"They can call if they're unsure."* |
| 9 | An inducement does not arrive labelled as one. It arrives as a favour, a sample, a family connection | *"It was only a gift."* |
| 11 | Vendor performance conversations are easier when they are routine and data-based, and impossible when they are the first one in two years | *"They've always been fine."* |

---

## 5. Participant Workbook Contents

Requisition-to-PO flow · vendor compliance checklist (`MD-016`) · **three-way match failure modes**
· receipt exception decision aid · stock-level block explanation for requesters · `P05` field
completeness checklist · approval authority matrix (`SP-004`) · **ethics escalation route** ·
`part_class` sourcing rules · vendor performance measures · **my access scope and approval limits**.

---

## 6. Exercises

| # | Exercise | Sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Requisition to approved PO | Sandbox | Standard requisition | Within authority; correct vendor |
| 2 | **Three-way match with a seeded mismatch** | Sandbox | Invoice ≠ receipt | Mismatch caught; payment held |
| 3 | Receipt exception — damaged goods | Practical + sandbox | Damaged delivery | Quarantined, coded, vendor notified |
| 4 | PO blocked on stock level | Sandbox | Over-max item | Block respected; requester advised correctly |
| 5 | Vendor compliance lapse | Sandbox | Expired document | Vendor state changed; PO prevented |
| 6 | **Ethics scenario** | Scenario | Offer of an inducement | Declines and escalates; records it |
| 7 | `part_class` sourcing for a brand job | Scenario | Cheaper compatible offered | Selects correct class; explains cost |
| 8 | Vendor performance conversation | Role play | Underperforming vendor | Rubric: data-based, specific, documented |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 5 form, 30 items | 35% | 80%, **100% on match, block and ethics items** | 3 | 24 months |
| Sandbox exercises 1, 2, 4, 5 | 30% | All passed | 3 | 24 months |
| **Ethics scenario (exercise 6)** | 20% | Passed | 2 | **Annual** |
| Receipt exception and sourcing (3, 7) | 15% | Both passed | 3 | 24 months |
| **OJT sign-off — 5 days** | Gate | Procurement Manager | — | — |

---

## 8. Job Aids Produced

Three-way match failure modes · receipt exception decision aid · vendor compliance checklist ·
`P05` field completeness card · approval authority matrix · **ethics escalation card** ·
`part_class` sourcing card. All in `TR-022`.

---

## 9. Trainer Requirements

L&D with Procurement Manager co-delivering · **Finance Manager delivers module 4** · **Legal or
Compliance delivers module 9** · sandbox with vendor and PO data · cohort maximum 8 — one cohort
covers the population.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence handling an exception and an ethics situation | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and ethics scenario pass | > 85% first attempt |
| **Behaviour** | Three-way match exceptions caught before payment · override logging · `P05` field completeness · vendor query volume | Matches enforced 100%; queries falling |
| **Result** | **`P05` targets — over 90% POs acknowledged, over 85% invoices via portal, 60% cut in vendor phone queries** · payment error rate | Per `04-00` `P05`, `RP-001` |

**Required Drivers** (`LS-04`): reinforce — match and exception job aids · encourage — Procurement
Manager reviews first month's exceptions · monitor — match exceptions, override log, query volume ·
reward — competence record.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) ·
[`../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) ·
[`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) ·
`KB-009` substitution notes · `UI-028` procurement console copy · `LG-023` ethics ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 5 ·
[`TR-022_Job_Aid_and_Quick_Reference_Library.md`](TR-022_Job_Aid_and_Quick_Reference_Library.md).

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | `TS-002` sandbox with vendor, PO and invoice data does not exist | Test Lead with Procurement | W3 |
| **O-02** | `MD-016` vendor master is unpopulated; modules 3 and 5 teach against an empty register | MDM with Procurement | W3 |
| **O-03** | **`P05` vendor portal lands at W3 alongside this pack.** Module 7 teaches a portal that may not be stable when the course runs | CTO with Procurement | W3 |
| **O-04** | `LG-023` anti-bribery content is unwritten (Category 10 unstarted). Module 9 has no governing source | Legal Counsel | **W3 — blocks the ethics module** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measures named from `P05` targets (`LS-01`)
- [x] Three-way match taught by its failure modes rather than its steps
- [x] Ethics made a critical, annually-refreshed assessed component
- [x] Vendor-facing consequence of data completeness made explicit
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-INV-03`/`-07`, `BR-STD-06` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-04` `LG-023` ethics source — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Finance Manager and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
