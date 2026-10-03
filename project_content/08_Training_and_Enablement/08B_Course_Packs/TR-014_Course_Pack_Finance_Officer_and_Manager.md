---
id: TR-014
title: Course Pack — Finance Officer and Manager
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development with Finance
author: Learning & Development with Finance and Tax
reviewers: [Finance Manager, CFO, Warranty Claims Officer, Operations Director, Legal Counsel, Localisation Lead]
approver: Finance Manager with CFO
content_class: D
purpose: >
  Trains 12–24 finance staff, 4–10 warranty claims officers and 51+ counter cashiers on the postings,
  VAT treatment and reconciliations that carry statutory consequence. Finance errors are expensive
  and slow to detect: a wrong VAT treatment is not discovered by the customer, it is discovered by
  the NBR, and by then it has been repeated for months.
traces_to: [M19, M20, M50, M51, M52, M53, M09, M22, P03, P08, MD-035, MD-037, MD-038, MD-040, MD-026, TR-001, TR-002, TR-004, TR-006, TR-022, UI-029, SP-014, SP-019, SP-020, DT-010, DT-011, DT-012]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-014_Course_Pack_Finance_Officer_and_Manager_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md and SP-020_SOP_Month_End_and_Year_End_Close.md — the governing procedures
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md — VAT rates by supply type, VDS, and the mapping to Mushak 6.1 / 6.2 / 6.3 / 6.6 / 9.1 output; NBR-compliant Mushak generation is mandatory and records must be retained for at least five years
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-FIN family; BRU-WTY-01 claim evidence requirements; BRU-WTY-05 claims valued at the rate prevailing on service completion date; BRU-WTY-08 unsubmitted claims escalated as revenue leakage
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — finance and close KPIs; KPI-063 claims rejected for uncertified technician zero
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Finance Officer and Manager

| Item | Value |
|---|---|
| Audience role(s) | `R26` Finance Manager · `R27` Finance Officer · **`R28` Warranty Claims Officer (module)** · **`R29` Cashier / Counter Finance (module)** |
| Headcount | 12–24 finance · 4–10 claims · **51+ cashiers** |
| Duration | **Core 10 hours** over three days · warranty module 4 h · **counter cash module 3 h** |
| Delivery mode | Classroom with sandbox; counter cash module delivered regionally |
| Language | English primary for head-office finance; **Bengali for the counter cash module** (`DS-18`) |
| Prerequisites | Layer 1 universal core |
| Certification outcome | Functional competence record (`TR-006` cells 6 and 7) |
| Wave | W1 |

> **This pack carries three audiences with very different needs.** The 51+ cashiers are a
> branch-based, Bengali-speaking population who need three hours on cash and documents, not ten
> hours of ledger accounting. §3.3 separates them properly rather than sending them to the wrong
> course.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Post a transaction to the correct account and dimension, and explain why | Sandbox + items — `MD-035`, `MD-036` |
| 2 | **Apply the correct VAT treatment by supply type and produce the correct Mushak output** | **Critical items + sandbox** — `MD-037` |
| 3 | Raise, issue and correct an invoice and a credit note | Sandbox — `DT-010`…`DT-012` |
| 4 | Reconcile a payment across the nine payment methods and their settlement keys | Practical — `MD-038` |
| 5 | Run receivables ageing and collections within policy | Sandbox |
| 6 | Execute the month-end close checklist to `SP-020` | Practical |
| 7 | Recognise a transaction that will produce a statutory error and stop it | **Critical scenario** |
| 8 | Apply approval authority and log every override | Items — `SP-004`, `BR-STD-06` |
| 9 | *(Warranty)* Assemble a claim to evidential standard and reconcile reimbursement | Practical — `BRU-WTY-01`, `SP-014` |
| 10 | *(Counter cash)* Take payment, issue the correct document, reconcile and bank to `SP-019` | **Practical** |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to finance transactions · posting and approval authority | Layer 1 core | On release (`TR-024`); 24 months. **VAT and statutory content on every Finance Act or NBR change** (`LS-10`, `TR-001` §4.8) |

---

## 3. Module Outline

### 3.1 Core — 10 hours (`R26`, `R27`)

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | The finance control environment and where errors originate | 45 min | Facilitated |
| 2 | Chart of accounts, dimensions and why every posting carries them | 75 min | Practice — `MD-035`, `MD-036` |
| 3 | **VAT by supply type, VDS, and the Mushak mapping** | **150 min** | Practice + items — `MD-037` |
| 4 | Invoicing, credit notes and document sequences | 75 min | Sandbox — `MD-040`, `DT-010`…`DT-012` |
| 5 | **Payment methods, settlement and reconciliation** | 90 min | Practical — `MD-038` |
| 6 | Receivables, ageing and collections | 60 min | Sandbox |
| 7 | **Month-end close** — cut-off, accrual, reconciliation, sign-off | 90 min | Practical — `SP-020` |
| 8 | Approval authority and override discipline | 45 min | Items — `SP-004` |
| 9 | Recognising a statutory error before it posts | 60 min | Scenario |
| 10 | Reading the finance console and the `P06` finance view | 45 min | Walkthrough — `UI-029` |
| | **Total** | **~10 hours** | |

### 3.2 Warranty claims module — 4 hours (`R28`, W4)

Claim eligibility and evidence (`BRU-WTY-01`) · assembly from the job record · `P08` submission ·
query response · decision handling · **financial reconciliation and revenue-leakage escalation**
(`BRU-WTY-08`) · FX on claim valuation (`BRU-WTY-05`) · **the certification link** — a claim
rejected for an uncertified technician is `KPI-063`, target zero.

### 3.3 Counter cash module — 3 hours (`R29`, Bengali, regional)

Payment acceptance across methods · **document issue — which document, when** · shift
reconciliation · shortfall procedure · banking · custody · **what a cashier may and may not
approve**. Delivered with `TR-011` branch manager content so branch and counter agree.

**`PK-06`: the counter cash module is a distinct three-hour course for a distinct population.**
Sending 51+ Bengali-speaking branch cashiers to a ten-hour English finance course would fail them
and waste 500 person-hours.

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 2 | A posting without its dimensions is a number nobody can explain at board level. Profitability by revenue stream is a board commitment (`05-02` DM-03) | *"The account is enough."* |
| 3 | **VAT treatment is decided by supply type, not by customer type.** The Mushak form follows the treatment, and the wrong form is a compliance failure even when the amount is right | *"We always use the same form."* |
| 3 | Records must be retained for at least five years. A correction made now must still be explicable in five years' time | *"We'll clean it up at year end."* |
| 5 | Nine payment integrations settle into accounts that must be pre-defined. A reconciliation that "nearly balances" is not reconciled | *"It's within tolerance."* |
| 7 | Cut-off is the whole point of a close. A transaction in the wrong period is a restatement risk | *"It's only a day out."* |
| 3.2 | A claim rejected because the technician was uncertified is not a finance error — but **finance is where it becomes visible** and where the escalation starts | *"That's operations' problem."* |
| 3.3 | The cashier's shortfall procedure protects the cashier. Following it is not an admission | *"I'll make it up myself."* |

---

## 5. Participant Workbook Contents

Chart of accounts and dimension quick reference · **VAT treatment decision table by supply type,
with Mushak mapping** · document type and sequence guide · payment method and settlement key table ·
close checklist (`SP-020`) · ageing and collections policy · approval authority (`SP-004`) ·
reason codes · *(warranty)* claim evidence checklist · *(cash)* **counter cash card, Bengali** ·
**my access scope and posting authority**.

---

## 6. Exercises

| # | Exercise | Sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Post ten transactions with dimensions | Sandbox | Mixed transaction set | All correct, all dimensioned |
| 2 | **VAT treatment across eight supply types** | Sandbox | Service, goods, export, exempt, VDS cases | **All eight correct with the right Mushak form** |
| 3 | Invoice, credit and re-issue | Sandbox | Correction scenario | Sequence integrity preserved |
| 4 | **Reconcile a day across five payment methods** | Practical | Seeded settlement file with one break | Break found and explained |
| 5 | Ageing review and collections action | Sandbox | Aged ledger | Correct prioritisation |
| 6 | **Month-end close checklist** | Practical | Period with two cut-off errors | Both found before sign-off |
| 7 | Statutory error scenario | Scenario | Transaction with a wrong VAT treatment | Stopped before posting; escalated |
| 8 | *(Warranty)* Assemble and submit a claim | Sandbox | Completed warranty job | Evidence complete; `BRU-WTY-01` satisfied |
| 9 | *(Cash)* Counter shift with a shortfall | Practical | Cash scenario | Correct documents; shortfall procedure followed |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 6 form, 30 items | 25% | 80%, **100% on VAT and statutory items** | 3 | 24 months |
| **VAT and Mushak exercise (2)** | 25% | **All eight correct** | 3 | **On every Finance Act / NBR change** |
| Core sandbox (1, 3, 5) | 15% | All passed | 3 | 24 months |
| Reconciliation and close (4, 6) | 20% | Both passed | 3 | 24 months |
| Statutory error scenario (7) | 15% | Passed | 3 | 24 months |
| *(Warranty)* exercise 8 | Gate for `R28` | Passed | 3 | 24 months |
| *(Cash)* `TR-006` cell 7 + exercise 9 | Gate for `R29` | 80% + practical pass | 3 | 24 months |
| **OJT sign-off — 5 days** | Gate | Finance Manager | — | — |

---

## 8. Job Aids Produced

Chart of accounts quick reference · **VAT treatment and Mushak decision card** · document and
sequence guide · payment settlement key table · close checklist · approval authority matrix ·
*(warranty)* claim evidence checklist · **(cash) counter card, Bengali**. All in `TR-022`.

---

## 9. Trainer Requirements

L&D with **Finance Manager delivering modules 2, 3, 7 and 9** · Tax specialist for module 3 ·
`R28` co-delivers the warranty module · **Bengali-speaking trainer for the counter cash module** ·
sandbox with realistic ledger, settlement files and a close period · cohort maximum 12 core, 15
counter cash · **51+ cashiers means 4–5 regional cohorts**.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence on VAT treatment and close | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and VAT exercise pass | > 85% first attempt; **VAT exercise 100% or re-take** |
| **Behaviour** | VAT correction volume · reconciliation breaks · close cut-off errors · cash variance at branches · claim rejection rate | Corrections and breaks falling |
| **Result** | Close cycle time · statutory filing accuracy · **`KPI-063` claims rejected for an uncertified technician — zero** · cash variance | Per `06-02`, `RP-001` |

**Required Drivers** (`LS-04`): reinforce — VAT decision card at the desk · encourage — Finance
Manager reviews the first close with each officer · monitor — correction and break volumes ·
reward — competence record; posting authority.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) ·
[`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) ·
[`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) ·
`DT-010`…`DT-012` statutory documents · `UI-029` finance console copy ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cells 6 and 7 ·
[`TR-011_Course_Pack_Branch_Manager.md`](TR-011_Course_Pack_Branch_Manager.md) — cash module alignment.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MD-037` VAT and Mushak mapping is authored but unpopulated with actual rates.** Module 3 — 150 minutes and the highest-consequence content in the pack — has no live data | Tax with Finance | **W1 — blocking module 3** |
| **O-02** | `TS-002` sandbox with a realistic ledger, settlement files and a close period does not exist | Test Lead with Finance | **W1** |
| **O-03** | **51+ cashiers is a larger population than the core finance audience**, delivered regionally in Bengali. §3.3 sizes it at 4–5 cohorts; this is not in any trainer plan (`TR-001` `O-04`) | HR Director with Finance | **W1** |
| **O-04** | The warranty module is W4 while the core is W1. `R28` officers exist from W1 and would be untrained on claims for three waves | Training Lead with Finance | W1 interim |
| **O-05** | VAT re-certification "on every Finance Act or NBR change" needs a trigger owner. **Nobody currently watches for the change and initiates retraining** | Tax with L&D | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measures named (`LS-01`)
- [x] **Three distinct audiences separated properly rather than merged (`PK-06`)**
- [x] VAT and Mushak treated as the highest-consequence content, with a 100%-or-retake standard
- [x] Statutory refresh tied to Finance Act / NBR change rather than a calendar (`LS-10`)
- [x] Warranty module links claim rejection to technician certification (`KPI-063`)
- [x] Counter cash module delivered in Bengali to the population that needs it
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-WTY-01`/`-05`/`-08`, `BR-STD-06` cited to `05-05`; `KPI-063` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `MD-037` rates populated — outstanding; blocks the pack's most important module**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Finance Manager and CFO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
