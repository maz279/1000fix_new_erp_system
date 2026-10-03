---
id: FIX-ERP2-M56
module_id: M56
module_code: PAY
module_name: Payroll, Benefits & Statutory Compliance
category: H — People & Workforce
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: HR Director
system_owner: People Squad
priority: P0
wave: W5
regulatory_verified: 2026-08-12
---

# M56 — Payroll, Benefits & Statutory Compliance
### Category H · Code `PAY` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M56 |
| **Module code** | `PAY` |
| **Category** | H — People & Workforce |
| **Status** | ★ **New** — split from M21 after enterprise benchmarking |
| **Priority** | **P0** — cannot be descoped; statutory obligation |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | HR Director (process) · CFO (financial control) |
| **System owner** | People Squad |
| **Delivery layers** | L2 (OCA `hr_payroll_community`) + L5 (custom Bangladesh payroll) |
| **Custom modules** | `cd_payroll_bd`, `cd_statutory_bd`, `cd_beftn`, `cd_benefits`, `cd_final_settlement` |
| **Requirement range** | FR-PAY-001 … FR-PAY-054 |
| **Requirement count** | 54 |
| **Effort estimate** | 26 person-weeks |
| **Depends on** | **M21 Core HR** · **M55 Workforce (blocking)** · M57 Incentives · M19 GL · M50 Treasury · M51 Tax |
| **Depended on by** | M19 GL · M50 Treasury · M51 Tax · M54 FP&A · M24 Documents · M21 self-service · M65 |

---

## 2. Purpose

M56 turns employment, hours and performance into **net pay, paid correctly, on time, with
every statutory obligation discharged**.

It is the module where an error is immediately visible to 500+ people, immediately damaging to
trust in the entire ERP programme, and potentially a statutory breach.

### Why It Exists

Payroll is calculated manually in Excel today. The v1.0 BRD lists the consequences: payroll
calculation errors, overtime tracking inaccuracy, no performance-linked incentive calculation,
and a three-day processing cycle.

More seriously, Bangladesh payroll carries the densest statutory logic in the entire estate:
income tax slabs that change with each national budget, provident fund, gratuity, festival
bonus, leave encashment, BEFTN bank file formats, and — as of the current assessment year —
**withholding tax returns that have moved from monthly to quarterly**.

### Why It Is Its Own Module

Four reasons, all structural:

| Reason | Detail |
|---|---|
| **Change cadence** | Tax parameters change annually with the national budget, independently of everything else in HR |
| **Blast radius** | One defect affects every employee in a single run |
| **Segregation of duties** | Processing and approval must be separable; in Excel they are not |
| **Regulatory density** | NBR, Labour Act and banking obligations converge here and nowhere else |

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 (BR-HRM-007) | "Calculate payroll including basic salary, allowances, overtime, incentives, statutory deductions" |
| ERP BRD BR-HRM-009 | "Deduct income tax as per Bangladesh tax slabs and provident fund contributions" |
| ERP BRD BR-HRM-010 | "Generate bank salary transfer files in Bangladesh bank-compatible format" |
| ERP BRD BR-HRM-011 | "Generate and distribute digital payslips to employees" |
| ERP BRD BRU-HRM-05 | **Payroll cannot be finalised for a period whose attendance is not verified and locked** |
| ERP BRD §6.2 Process 9 | Current state: payroll calculated manually in Excel; bank transfers initiated individually |
| ERP BRD DEP-07 | Bangladesh bank BEFTN format must be confirmed with the banking partner |
| **Bangladesh Labour Act 2006** *(verified 2026-08-12)* | **Gratuity: wages of at least 30 days at the last-drawn rate for every completed year of service**; Provident Fund formation where three-quarters of workers demand it; Workers' Participation Fund and Workers' Welfare Fund |
| **NBR income tax, AY 2026–27** *(verified 2026-08-12)* | Tax-free threshold **BDT 375,000** general; **BDT 425,000** women and 65+; **BDT 500,000** persons with disabilities and third gender; **BDT 525,000** war-wounded freedom fighters and July Warriors 2024. **Minimum tax BDT 5,000** (BDT 1,000 for first-time registrants). **Investment rebate reduced to 10%**, capped at BDT 750,000 eligible investment. Top rate **30%** above approximately BDT 3.85 million |
| **NBR withholding returns** *(verified 2026-08-12)* | **Withholding tax return frequency has moved from monthly to quarterly**, with deadlines of **25 October, 25 January, 25 April and 25 July** |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | Payroll data is personal data; salary and bank details are S3; TIN is sensitive personal data with residency restriction |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Payroll calculation engine: earnings, deductions, gross-to-net |
| 2 | Bangladesh income tax computation with slabs, thresholds and rebate |
| 3 | Provident fund: employee and employer contribution, ledger, withdrawal |
| 4 | Gratuity: accrual, provision and payment on separation |
| 5 | Festival bonus calculation and payment |
| 6 | Leave encashment computation |
| 7 | Overtime and incentive integration into pay |
| 8 | Loans, advances and recovery schedules |
| 9 | Statutory and voluntary deductions |
| 10 | Payroll run: preparation, calculation, review, approval, posting |
| 11 | Off-cycle and correction runs |
| 12 | BEFTN bank file generation and disbursement confirmation |
| 13 | Digital payslip generation and distribution |
| 14 | Salary certificate and annual tax statement |
| 15 | Statutory returns: withholding tax return preparation, challans, certificates |
| 16 | Final settlement on separation |
| 17 | Payroll posting to the general ledger and cost allocation |
| 18 | Payroll reconciliation, control and audit |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Employee master, contract, salary structure definition** | **M21** | M56 consumes; it does not define employment terms |
| **Attendance, leave, approved overtime hours** | **M55** | M56 pays what M55 verified; it never recalculates hours |
| **Incentive scheme design and KPI calculation** | **M57** | M57 computes the incentive; M56 pays it |
| **Sales commission** | **M53** | Revenue-linked; paid through a different mechanism |
| **General ledger, chart of accounts, period close** | **M19** | M56 posts; M19 owns the ledger |
| **Bank account management, payment execution, reconciliation** | **M50** | M56 produces the file; M50 executes and reconciles |
| **VAT, TDS on vendor payments, corporate tax** | **M51** | Different tax domain; only payroll withholding sits here |
| **Employee expense claims and reimbursement** | **M52** | Not payroll, though it may be paid alongside |
| **Cost centre and budget definition** | **M54** | M56 allocates cost; M54 owns the structure |
| Medical insurance claims administration | **M59** / insurer | M56 deducts the premium only |
| Recruitment cost | **M58** | — |

### 3.3 Shared Concepts

| Concept | M56's Role | Owning Module |
|---|---|---|
| Employee | References | M21 |
| Salary structure | References | M21 |
| Hours and leave | Consumes verified, locked data | M55 |
| Incentive amount | Consumes calculated amount | M57 |
| Payslip | **Owns** | M56 |
| Gratuity provision | **Calculates**; M19 posts | M56 / M19 |
| BEFTN file | **Generates**; M50 transmits | M56 / M50 |
| Withholding return | **Prepares**; M51 files | M56 / M51 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Payroll / SuccessFactors Employee Central Payroll** | Country-specific payroll engines with statutory rule packs updated by the vendor; payroll control centre with checks before release | **The country-pack concept** — Bangladesh statutory rules as a versioned, effective-dated pack separate from the engine; **pre-release validation checks** | Vendor-maintained statutory updates — no vendor maintains a Bangladesh pack for Odoo, so the Company owns it |
| **Oracle Global Payroll** | Element-based earnings and deductions, balance framework, retroactive processing | **Element and balance architecture**; retro processing for backdated changes | Oracle's full element entry complexity |
| **Workday Payroll** | Configurable calculation with audit and off-cycle support | Off-cycle and correction run model | — |
| **OCA `hr_payroll_community`** | Open-source payroll structure, rules, payslips | The L2 substrate, extended with a Bangladesh pack | Its default rule set — entirely non-Bangladeshi |
| **Bangladesh payroll practice** | Slab-based tax with category thresholds, minimum tax, investment rebate, PF, gratuity, festival bonus, BEFTN | **The complete statutory set** | — |

**Design position.** Six deliberate differences, each driven by risk.

First, **statutory rules are a versioned country pack, not code**. Bangladesh tax thresholds
changed between AY 2025–26 (BDT 350,000) and AY 2026–27 (BDT 375,000). The 5% introductory slab
and the investment rebate rate are both under change. A payroll that hard-codes any of this
requires a release every budget. The pack is effective-dated data, and a prior period always
recalculates on the rule version that applied then.

Second, **payroll cannot run on unverified hours**. This is BRU-HRM-05 and it is a hard gate.
The most common payroll failure is not a calculation error; it is calculating correctly from
wrong inputs and correcting afterwards, which destroys confidence.

Third, **two full parallel runs before cutover**. The category risk register already states
this. It is restated here as a gate criterion, not an aspiration. Payroll is the one module
where a first-run failure would damage the credibility of the entire programme.

Fourth, **segregation of duties is enforced in the system**. The person who prepares payroll
cannot approve it, and neither can release the bank file. In Excel this control does not exist.

Fifth, **the payslip explains itself**. Every employee sees the hours, rates, incentive
components and deductions that produced their net pay. Payroll disputes are overwhelmingly
disputes about visibility, not arithmetic.

Sixth, **gratuity is provisioned continuously, not discovered at separation**. The Labour Act
sets gratuity at wages of at least 30 days per completed year at the last-drawn rate. Accruing
it monthly makes the liability visible and the separation affordable.

---

## 5. Functional Areas & Features

### 5.1 Payroll Engine

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-001 | Earnings elements | Define earnings elements — basic, house rent, medical, conveyance, other allowances, overtime, incentive, bonus, arrears — with calculation basis and taxability | **P0** | L2 |
| FR-PAY-002 | Deduction elements | Define deductions — income tax, provident fund, loan recovery, advance recovery, insurance premium, union dues, other — with statutory or voluntary classification | **P0** | L2 |
| FR-PAY-003 | Calculation sequence | Execute elements in a defined, auditable sequence with dependency resolution | **P0** | L5 |
| FR-PAY-004 | Balance framework | Maintain period, quarter and year-to-date balances per element per employee | **P0** | L5 |
| FR-PAY-005 | Proration | Prorate earnings for mid-period joiners, leavers, transfers, suspensions and unpaid absence | **P0** | L5 |
| FR-PAY-006 | Retroactive processing | Recalculate a prior period on a backdated change and pay the difference as arrears, **using the rule version that applied to that period** | **P1** | L5 |
| FR-PAY-007 | Multi-entity and multi-branch | Calculate and post by legal entity, branch and cost centre | P1 | L5 |
| FR-PAY-008 | Currency | Operate in BDT with the framework to support additional currencies for M65 expansion | P2 | L5 |

### 5.2 Bangladesh Statutory — Income Tax

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-009 | **Effective-dated statutory pack** | Maintain the Bangladesh tax rule pack — thresholds, slabs, rates, rebate, minimum tax — as versioned, effective-dated **configuration, not code** | **P0** | L5 |
| FR-PAY-010 | **Category thresholds** | Apply the correct tax-free threshold by taxpayer category: general, women and 65+, persons with disabilities and third gender, war-wounded freedom fighters and July Warriors 2024 | **P0** | L5 |
| FR-PAY-011 | Slab computation | Compute tax across the progressive slabs applicable to the assessment year | **P0** | L5 |
| FR-PAY-012 | **Minimum tax** | Apply the minimum tax where the slab computation falls below it, with the reduced amount for first-time registrants | **P0** | L5 |
| FR-PAY-013 | **Investment rebate** | Compute the investment rebate at the applicable rate against declared eligible investment, subject to the statutory cap | **P0** | L5 |
| FR-PAY-014 | Investment declaration | Collect and validate employee investment declarations and supporting evidence during the year | P1 | L5 |
| FR-PAY-015 | Annual tax projection | Project annual tax liability and spread deduction evenly across the year, adjusting as income or declarations change | **P1** | L5 |
| FR-PAY-016 | Exemptions and perquisites | Apply exemption limits on allowances and value perquisites per NBR rules | P1 | L5 |
| FR-PAY-017 | **Withholding return preparation** | Prepare the withholding tax return **quarterly**, for the deadlines of **25 October, 25 January, 25 April and 25 July** | **P0** | L5 |
| FR-PAY-018 | Tax challan and certificate | Record tax deposit challans and issue the annual tax deduction certificate per employee | **P0** | L5 |
| FR-PAY-019 | Salary certificate | Generate a salary certificate on request, in the format required for loan, visa and tax purposes | P1 | L5 |

### 5.3 Bangladesh Statutory — Benefits

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-020 | **Provident fund** | Compute employee and employer PF contributions on the defined base, maintain the member ledger, and report the fund position | **P0** | L5 |
| FR-PAY-021 | PF withdrawal and settlement | Handle PF withdrawal and settlement on separation per the fund rules | P1 | L5 |
| FR-PAY-022 | **Gratuity accrual** | Accrue gratuity monthly at **wages of at least 30 days per completed year of service at the last-drawn rate**, and publish the provision to M19 | **P0** | L5 |
| FR-PAY-023 | Gratuity payment | Compute and pay gratuity on qualifying separation, applying eligibility rules | **P0** | L5 |
| FR-PAY-024 | **Festival bonus** | Compute and pay festival bonus per policy and statute, with the correct tax treatment | **P0** | L5 |
| FR-PAY-025 | Leave encashment | Compute encashment of eligible leave balances from M55, at separation or per policy | **P1** | L5 |
| FR-PAY-026 | Workers' Participation and Welfare Fund | Support the statutory fund contributions where applicable to the Company | P2 | L5 |
| FR-PAY-027 | Insurance and medical benefit | Deduct premiums and record employer contributions for group insurance and medical schemes | P2 | L5 |
| FR-PAY-028 | Benefit enrolment | Manage employee enrolment in optional benefit schemes with effective dating | P2 | L5 |

### 5.4 Inputs, Loans & Advances

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-029 | **Attendance and leave input** | Consume verified, locked hours, absence and approved overtime from M55; **never recalculate them** | **P0** | L5 |
| FR-PAY-030 | **Incentive input** | Consume the calculated incentive amount from M57 with its supporting detail for the payslip | **P0** | L5 |
| FR-PAY-031 | Loan management | Record loans with amount, instalments and interest treatment; recover through payroll | P1 | L5 |
| FR-PAY-032 | Salary advance | Record advances and recover them per the agreed schedule | P1 | L5 |
| FR-PAY-033 | Recovery limits | Enforce a maximum aggregate deduction as a proportion of net pay | **P1** | L5 |
| FR-PAY-034 | One-time payments and deductions | Support ad-hoc payments and deductions with approval and reason | P1 | L5 |
| FR-PAY-035 | Arrears | Compute and pay arrears from backdated salary revisions | P1 | L5 |

### 5.5 Payroll Run & Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-036 | Payroll calendar | Define pay periods, cut-off dates, processing dates and payment dates by entity | **P0** | L5 |
| FR-PAY-037 | **Attendance lock gate** | **Prevent a payroll run for a period whose attendance is not verified and locked in M55** | **P0** | L5 |
| FR-PAY-038 | Pre-run validation | Run pre-payroll checks — missing bank details, missing tax category, negative net pay, variance beyond threshold, missing attendance — and block on error | **P0** | L5 |
| FR-PAY-039 | Trial run | Execute a trial run producing full results without committing, as many times as required | **P0** | L5 |
| FR-PAY-040 | **Variance analysis** | Compare each employee's gross and net against the prior period and flag variance beyond a threshold for review before approval | **P0** | L5 |
| FR-PAY-041 | **Approval** | Require formal approval of the payroll run by an authority who did not prepare it | **P0** | L5 |
| FR-PAY-042 | Commit and lock | Commit the approved run, lock it, and prevent further change except by a correction run | **P0** | L5 |
| FR-PAY-043 | Off-cycle run | Execute off-cycle runs for final settlements, arrears and corrections | **P1** | L5 |
| FR-PAY-044 | Correction run | Reverse and reprocess a committed run under approval, with a full audit trail | **P1** | L5 |
| FR-PAY-045 | Payroll reconciliation | Reconcile the run to the prior period, to the GL posting and to the bank disbursement | **P0** | L5 |

### 5.6 Disbursement, Payslip & Settlement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PAY-046 | **BEFTN file generation** | Generate the bank salary transfer file in the format required by the banking partner, validated before release | **P0** | L5 |
| FR-PAY-047 | Disbursement release | Release the payment file to M50 for execution, under an authority separate from payroll approval | **P0** | L5 |
| FR-PAY-048 | Disbursement confirmation | Consume bank confirmation and record paid, failed and returned items, with a re-issue path | **P1** | L5 |
| FR-PAY-049 | Cash and alternative payment | Support the exception path for employees without a bank account, with additional control | P2 | L5 |
| FR-PAY-050 | **Digital payslip** | Generate a bilingual payslip showing hours, rates, every earning and deduction, tax basis, incentive detail and year-to-date balances | **P0** | L5 |
| FR-PAY-051 | Payslip distribution | Distribute payslips through self-service and, where consented, by email, with access control | **P0** | L5 |
| FR-PAY-052 | **Final settlement** | Compute final settlement on separation — notice, leave encashment, gratuity, PF, outstanding loans, recoveries — and release only after clearance from M21 | **P0** | L5 |
| FR-PAY-053 | **GL posting** | Post payroll to the general ledger by entity, branch and cost centre, with a reconcilable control account | **P0** | L5 |
| FR-PAY-054 | Payroll cost reporting | Report payroll cost by entity, branch, department, cost centre and element, feeding M54 | **P1** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Statutory pack as versioned data** | Thresholds, slabs, rates, rebate, minimum tax, PF and gratuity parameters are effective-dated configuration. A budget change is a pack update, not a release |
| T-02 | **Rule-version pinning** | Every payslip records the statutory pack version used. A retro calculation for a prior period uses that version, never the current one |
| T-03 | **Deterministic calculation** | The same inputs and the same pack version always produce the same result, and the calculation is reproducible line by line for audit |
| T-04 | **Calculation transparency** | Every payslip line traces to its source element, rule and input value; there are no derived figures without provenance |
| T-05 | **Hard gate on attendance lock** | The run cannot start if the period is unlocked in M55; enforced at the service layer, not the UI |
| T-06 | **Segregation enforced in the system** | Prepare, approve and release are three distinct permissions that cannot be held by one user for the same run |
| T-07 | **Immutability after commit** | A committed run is immutable. Change is only possible through a reversal-and-reprocess correction run with its own approval |
| T-08 | **S3 data protection** | Salary, bank details and TIN are encrypted, access-logged, and require step-up authentication; TIN resides in the **Bangladesh-resident store** |
| T-09 | **BEFTN format validation** | The file is validated against the bank's specification before release; a rejected file never reaches the bank |
| T-10 | **Payslip integrity** | Payslips are generated once, hashed, and retained; a reissued payslip after a correction is a new versioned document, not an overwrite |
| T-11 | **Bilingual rendering** | Payslips, salary certificates and tax certificates render correctly in Bengali and English |
| T-12 | **Retention** | Payroll and tax records retained 7 years; employee records 10 years after termination |
| T-13 | **Performance envelope** | Full payroll run for 500+ employees ≤ 20 minutes · trial run ≤ 20 minutes · payslip generation ≤ 5 minutes for the full population |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M56 |
|---|---|---|
| **Employee** | Receives an amount and cannot tell how it was calculated | Receives a payslip showing hours, rates, incentive detail, tax basis and year-to-date balances |
| **HR Officer** | Spends three days building payroll in Excel | Runs a trial, reviews variance, submits for approval — within hours |
| **HR Director** | Cannot demonstrate statutory compliance | Statutory pack versioned; returns prepared on schedule; certificates issued |
| **CFO** | Payroll arrives as a number with no breakdown | Payroll posts to the GL by branch and cost centre, reconciled to the bank |
| **Branch manager** | Cannot see branch payroll cost | Sees payroll cost by branch and department against budget |
| **Technician** | Distrusts incentive because it cannot be checked | Sees the incentive calculation on the payslip alongside the KPI detail from M57 |
| **Auditor** | Finds spreadsheets | Finds a locked run, an approval trail, a GL reconciliation and a rule-version record |
| **Leaver** | Waits for a manual settlement calculation | Final settlement computed automatically after clearance |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Payroll processing time** | Automated calculation replacing manual Excel construction | **3 days → under 4 hours** |
| **Payroll accuracy** | Verified inputs, deterministic calculation, variance checks, approval gate | **< 0.3% corrections per run** |
| **Statutory compliance** | Versioned pack, quarterly withholding returns, challans, certificates | **100% on-time filing**; removes an NBR exposure |
| **Gratuity liability visibility** | Monthly accrual and provision published to the GL | Converts an unquantified obligation into a managed provision |
| **Administrative labour saving** | HR officer time released from payroll construction and query handling | Material recurring saving across the HR function |
| **Enables performance-linked pay** | Incentive integrated, transparent and disputable on evidence | **Precondition** for the M02 productivity gain of 4–5 → 8–9 jobs per technician per day |
| **Reduced payroll disputes** | Self-explaining payslip | Disputes fall sharply where the calculation is visible |
| **Fraud and error control** | Segregation of duties, variance analysis, immutable committed runs | Closes a control gap that a spreadsheet cannot close |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Trust in the programme** | Payroll is the ERP's most visible promise to staff. Getting it right buys goodwill for everything else; getting it wrong costs more than any other module |
| **Employees are paid correctly and on time** | This is not a benefit to be argued for. It is the baseline obligation of an employer |
| **Statutory obligations become demonstrable** | An NBR or labour inspection is answered with records, not reconstruction |
| **The gratuity liability stops being invisible** | An unprovisioned gratuity obligation across 500+ staff with years of service is a material unrecorded liability |
| **Pay becomes explicable** | A manager can explain a payslip to their team member without escalating to HR |
| **Foundation for expansion** | A second country needs a payroll engine with a swappable country pack, not a second spreadsheet |

---

## 8. Lifecycle & State Model

### 8.1 Payroll Run

```
   +----------------+
   |  PERIOD OPEN   |
   +--------+-------+
            | attendance period locked in M55  <-- HARD GATE (BRU-HRM-05)
   +--------v-------+     unlocked --> RUN BLOCKED
   |   INPUTS       |  hours (M55), incentive (M57), one-time items, loans
   |   COLLECTED    |
   +--------+-------+
            |
   +--------v-------+     errors --> BLOCKED until resolved
   | PRE-VALIDATION |  bank details, tax category, negative net, missing inputs
   +--------+-------+
            |
   +--------v-------+
   |   TRIAL RUN    |<--------+  repeatable, no commitment
   +--------+-------+         |
            |                 |
   +--------v-------+         |
   |    VARIANCE    |---------+  corrections made, re-run
   |    REVIEWED    |
   +--------+-------+
            | submitted
   +--------v-------+
   |    PENDING     |  approver must not be the preparer  <-- SOD-03
   |    APPROVAL    |
   +--------+-------+
            | approved
   +--------v-------+
   |   COMMITTED    |  immutable; balances updated; payslips generated
   +--------+-------+
            |
   +--------v-------+
   |  GL POSTED     |  by entity, branch, cost centre (M19)
   +--------+-------+
            | released by a third authority  <-- SOD-29
   +--------v-------+
   | FILE RELEASED  |  BEFTN file to M50
   +--------+-------+
            |
   +--------v-------+
   |     PAID       |  bank confirmation consumed; failures re-issued
   +--------+-------+
            |
   +--------v-------+
   |  RECONCILED    |  run = GL = bank
   +----------------+

   CORRECTION RUN -- reversal and reprocess of a committed run, separately approved
   OFF-CYCLE RUN  -- final settlement, arrears, ad-hoc payment
```

### 8.2 Final Settlement

```
   SEPARATION RECORDED (M21)
        |
   +----v-----------+
   |  CLEARANCE     |  assets, van stock, tools, IT, dues, handover  (M21)
   |  IN PROGRESS   |
   +----+-----------+
        | clearance complete  <-- HARD GATE
   +----v-----------+
   | SETTLEMENT     |  notice pay, leave encashment (M55), gratuity accrual,
   | COMPUTED       |  PF settlement, outstanding loans, recoveries
   +----+-----------+
        |
   +----v-----------+
   |   APPROVED     |  HR Director and Finance Manager
   +----+-----------+
        |
   +----v-----------+
   |     PAID       |  through an off-cycle run
   +----+-----------+
        |
   +----v-----------+
   |  CERTIFICATES  |  final salary certificate, tax deduction certificate
   |    ISSUED      |
   +----------------+
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PAY-01 | **Payroll cannot run for a period whose attendance is not verified and locked in M55** *(BRU-HRM-05)* | **H** | HR Director / CFO |
| BRU-PAY-02 | **The person who prepares a payroll run cannot approve it** *(SOD-03)* | **H** | CFO |
| BRU-PAY-03 | **The person who approves a payroll run cannot release the bank file** *(SOD-29)* | **H** | CFO |
| BRU-PAY-04 | A committed run is immutable; change requires an approved correction run | **H** | CFO |
| BRU-PAY-05 | A run with pre-validation errors cannot proceed | **H** | HR Director |
| BRU-PAY-06 | Variance beyond the configured threshold must be reviewed and acknowledged before approval | **H** | CFO |
| BRU-PAY-07 | **Payroll uses the statutory pack version effective for the pay period, including on retroactive recalculation** | **H** | HR Director |
| BRU-PAY-08 | **The correct tax-free threshold is applied by taxpayer category** | **H** | HR Director |
| BRU-PAY-09 | **Minimum tax applies where the slab computation falls below it** | **H** | HR Director |
| BRU-PAY-10 | Investment rebate is granted only against a validated declaration within the statutory cap | **H** | HR Director |
| BRU-PAY-11 | **Gratuity accrues at not less than 30 days' wages per completed year at the last-drawn rate** *(Labour Act)* | **H** | CFO |
| BRU-PAY-12 | Aggregate deductions may not exceed the configured proportion of net pay | **H** | HR Director |
| BRU-PAY-13 | Net pay cannot be negative; an exception routes to HR for resolution | **H** | HR Director |
| BRU-PAY-14 | **Final settlement is released only after exit clearance is complete in M21** | **H** | HR Director / CFO |
| BRU-PAY-15 | Salary, bank details and TIN are S3: encrypted, access-logged, step-up authenticated; **TIN resides in the Bangladesh-resident store** | **H** | CDO |
| BRU-PAY-16 | **The withholding tax return is prepared quarterly for the 25 October, 25 January, 25 April and 25 July deadlines** | **H** | CFO |
| BRU-PAY-17 | Every employee receives a payslip for every run in which they are paid | **H** | HR Director |
| BRU-PAY-18 | Payroll and tax records are retained 7 years | **H** | CFO |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.payroll.element` | `fix_payroll_element` | Earning or deduction definition | code, type, calculation_basis, taxable, statutory, sequence, gl_account, effective_from |
| `fix.payroll.calendar` | `fix_payroll_calendar` | Pay periods | entity_id, period, cut_off_date, process_date, pay_date, state |
| `fix.payroll.run` | `fix_payroll_run` | One execution | calendar_id, run_type, state, prepared_by, approved_by, released_by, committed_at, pack_version, employee_count, gross_total, net_total |
| `fix.payslip` | `fix_payslip` | One employee, one run | run_id, employee_id, gross, deductions, net, pack_version, hash, document_ref, version |
| `fix.payslip.line` | `fix_payslip_line` | One element on a payslip | payslip_id, element_id, quantity, rate, amount, basis_detail, source_ref |
| `fix.payroll.balance` | `fix_payroll_balance` | Cumulative balances | employee_id, element_id, period, quarter_to_date, year_to_date |
| **`fix.statutory.pack`** | `fix_statutory_pack` | **Versioned Bangladesh rules** | version, jurisdiction, assessment_year, effective_from, effective_to, thresholds_json, slabs_json, rebate_rate, rebate_cap, minimum_tax, pf_rules_json, gratuity_rules_json, approved_by |
| `fix.tax.category` | `fix_tax_category` | Taxpayer classification | employee_id, category, threshold_applied, effective_from, evidence_ref |
| `fix.investment.declaration` | `fix_investment_declaration` | Rebate basis | employee_id, assessment_year, instrument, amount, evidence_ref, validated_by, eligible_amount |
| `fix.tax.deduction` | `fix_tax_deduction` | Tax withheld | employee_id, period, taxable_income, computed_tax, rebate, minimum_tax_applied, deducted |
| `fix.withholding.return` | `fix_withholding_return` | Quarterly return | quarter, due_date, prepared_at, filed_at, total_deducted, challan_refs, state |
| `fix.tax.challan` | `fix_tax_challan` | Deposit record | period, amount, challan_number, deposited_on, bank |
| `fix.pf.member` | `fix_pf_member` | Provident fund member | employee_id, joined_fund_on, employee_rate, employer_rate, state |
| `fix.pf.ledger` | `fix_pf_ledger` | PF movements | pf_member_id, period, employee_contribution, employer_contribution, interest, withdrawal, balance |
| `fix.gratuity.accrual` | `fix_gratuity_accrual` | Monthly accrual | employee_id, period, completed_years, last_drawn_wage, accrued_amount, cumulative_provision |
| `fix.loan` | `fix_loan` | Employee loan or advance | employee_id, type, principal, instalments, rate, outstanding, state |
| `fix.loan.recovery` | `fix_loan_recovery` | Recovery instalment | loan_id, run_id, amount, outstanding_after |
| `fix.one.time.item` | `fix_one_time_item` | Ad-hoc payment or deduction | employee_id, period, element_id, amount, reason, approved_by |
| `fix.beftn.file` | `fix_beftn_file` | Bank transfer file | run_id, generated_at, record_count, total_amount, file_ref, validated, released_by, released_at |
| `fix.disbursement.result` | `fix_disbursement_result` | Bank confirmation | beftn_file_id, employee_id, status, failure_reason, reissued_in_run |
| `fix.final.settlement` | `fix_final_settlement` | Separation payment | employee_id, notice_pay, leave_encashment, gratuity, pf_settlement, recoveries, net, clearance_ref, approved_by, paid_in_run |
| `fix.payroll.gl.posting` | `fix_payroll_gl_posting` | GL interface | run_id, entity_id, branch_id, cost_centre_id, account_id, debit, credit, posted_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, `fix.employment.contract`, `fix.salary.structure` | M21 | Employment terms and status |
| `fix.exit.clearance` | M21 | Final settlement gate |
| **`fix.attendance.period`, `fix.time.valuation`, `fix.leave.entitlement`** | **M55** | **Locked hours, overtime, encashable balances — blocking input** |
| `fix.payroll.element` | M56 | Incentive amount with supporting detail |
| `fix.bank.account` | M50 | Company disbursement account |
| `account.move` | M19 | GL posting target |
| `fix.document` | M24 | Payslip, certificate and return retention |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PAY-01 | Payroll cut-off reached | Verify the M55 attendance lock; collect inputs from M55, M57, loans and one-time items | **Block the run and escalate if the period is unlocked** |
| AUT-PAY-02 | Inputs collected | Run pre-validation; produce an error and warning report | Block on error; proceed on warning with acknowledgement |
| AUT-PAY-03 | Trial run executed | Produce variance analysis against the prior period per employee and in aggregate | — |
| AUT-PAY-04 | Variance beyond threshold | Flag for mandatory review; block approval until acknowledged | Escalate to CFO |
| AUT-PAY-05 | Run approved | Commit, lock, update balances, generate payslips, post to the GL | Roll back entirely; alert CFO |
| AUT-PAY-06 | Run committed | Generate the BEFTN file, validate against the bank specification, present for release | Block release; alert Finance |
| AUT-PAY-07 | File released | Transmit to M50 for execution; record the release authority | Escalate |
| AUT-PAY-08 | Bank confirmation received | Record paid, failed and returned items; queue failures for re-issue | Alert Finance on unmatched confirmations |
| AUT-PAY-09 | Payslips generated | Distribute through self-service; notify employees through M27 subject to consent | Retry; alert HR |
| AUT-PAY-10 | Month end | Accrue gratuity for every eligible employee; publish the provision to M19 | Escalate to CFO |
| AUT-PAY-11 | **Quarter end approaching** | **Prepare the withholding tax return for the 25th deadline; alert at 14 and 7 days** | **Escalate to CFO — a missed filing is a statutory breach** |
| AUT-PAY-12 | Assessment year change | Prompt statutory pack update; **block payroll on the new year until an approved pack version exists** | **Block and escalate** |
| AUT-PAY-13 | Exit clearance completed (event from M21) | Compute final settlement; route for approval | Manual settlement task |
| AUT-PAY-14 | Backdated salary or attendance change | Trigger retroactive recalculation using the original period's pack version; produce arrears | Flag for manual review |
| AUT-PAY-15 | Loan instalment due | Include recovery in the run, respecting the aggregate deduction limit | Defer instalment; notify employee and HR |
| AUT-PAY-16 | Annual year end | Generate tax deduction certificates and annual statements for every employee | Escalate to HR Director |

---

## 12. Interfaces

### 12.1 Upstream — M56 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M55 Workforce** | **Locked attendance period, valued hours, approved overtime, leave taken, encashable balances** | **Event + REST — blocking** |
| **M21 Core HR** | Employee, contract, salary structure, status, movements, exit clearance | REST + event |
| **M57 Performance** | Calculated incentive amount with supporting KPI detail | Event |
| M50 Treasury | Company disbursement account; bank confirmation | REST + event |
| M51 Tax | Statutory pack review; challan and filing coordination | REST |
| M30 Platform Admin | Entity, branch, cost centre structure | Master data |
| M29 Identity | S3 field control, step-up authentication, residency enforcement | Service |

### 12.2 Downstream — M56 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M19 General Ledger** | **Payroll posting by entity, branch and cost centre; gratuity provision** | **Command** |
| **M50 Treasury** | **BEFTN file for execution; disbursement instruction** | **Command** |
| **M51 Tax** | Withholding tax return data, challans, certificates | Event + REST |
| M21 Core HR | Payslips and certificates for employee self-service | REST |
| M54 FP&A | Payroll cost by entity, branch, department, cost centre and element | Warehouse extract |
| M24 Documents | Payslips, certificates, returns for retention | Command |
| M27 Contact Centre | Payslip availability notification | Event |
| M60 GRC | Segregation-of-duties evidence, approval trail, control testing data | Event |
| M25 Business Intelligence | Payroll cost, headcount cost, overtime cost facts | Warehouse extract |
| P03 Admin Portal, P02 Technician App | Payslip and settlement self-service | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `payroll.run_started` | run, period, entity, employee count | M25 |
| `payroll.validation_failed` | run, error count, categories | HR, CFO |
| `payroll.variance_flagged` | run, employees, variance detail | CFO |
| `payroll.approved` | run, approver, totals | M19, M50 |
| **`payroll.committed`** | **run, gross, net, deductions, GL posting** | **M19, M54, M25** |
| `payroll.file_released` | BEFTN file, record count, total, releaser | **M50** |
| `payroll.paid` | run, paid count, failed count | M50, HR |
| `payslip.generated` | employee, run, document ref | M21, M24, M27 |
| `gratuity.accrued` | period, total provision, movement | **M19**, M54 |
| `withholding_return.prepared` | quarter, total, due date | **M51**, CFO |
| `final_settlement.computed` | employee, components, net | HR, CFO |
| `statutory_pack.published` | version, assessment year, effective from | M51, M60 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/payroll/runs` | GET / POST | Create and list payroll runs | P03 |
| `/api/v1/payroll/runs/{id}/validate` | POST | Pre-run validation | P03 |
| `/api/v1/payroll/runs/{id}/trial` | POST | Execute a trial run | P03 |
| `/api/v1/payroll/runs/{id}/variance` | GET | Variance analysis | P03 |
| `/api/v1/payroll/runs/{id}/approve` | POST | Approve — preparer blocked | P03 |
| `/api/v1/payroll/runs/{id}/release` | POST | Release the bank file — approver blocked | P03 |
| `/api/v1/payroll/runs/{id}/beftn` | GET | Retrieve the validated BEFTN file | M50 |
| `/api/v1/payslips/{employee}/{period}` | GET | Payslip retrieval | P02, P03 |
| `/api/v1/payroll/statutory-pack` | GET / POST | Statutory pack management | P03, M51 |
| `/api/v1/payroll/settlement/{employee}` | GET / POST | Final settlement | P03 |
| `/api/v1/payroll/withholding-return/{quarter}` | GET | Quarterly return data | M51, P03 |
| `/api/v1/payroll/cost` | GET | Payroll cost analysis | P06, M54 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R41 Payroll Officer** *(new role)* | C R U | **Prepare only** — cannot approve or release |
| R30 HR Manager | R **A** | **Approve** — cannot prepare or release |
| R26 Finance Manager | R **A** | **Release the bank file** — cannot prepare or approve |
| R03 Chief Financial Officer | R A | All — oversight, variance, statutory pack approval |
| R31 HR Officer | R | Input preparation; no calculation or approval authority |
| **R40 Chief Data Officer** | R A | S3 access governance and audit |
| R49 GRC / Internal Audit | R | Approval trail, segregation evidence, control testing |
| **Employee (self)** | R | **Own payslips, certificates and settlement only** |
| R06 Branch Manager | R | Branch payroll cost in aggregate — **no individual pay data** |
| R33 IT / System Administrator | — | **No access to payroll data**; platform administration only |

**Field-level restrictions.** Individual salary, bank details and TIN are **S3**: encrypted,
access-logged, step-up authenticated. Branch managers see aggregate cost only, never individual
pay. This is the strictest financial-data permission model in the ERP after M06.

**Segregation of duties — three-way.** Prepare (R41), approve (R25) and release (R26) are three
distinct permissions. No user may hold two of them for the same run. This is **SOD-03** and
**SOD-29**, enforced at the service layer.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Payroll run dashboard | HR Director, CFO | Per run | Status, employee count, gross, net, deductions, exceptions |
| **Pre-validation report** | **Payroll Officer, HR Director** | **Per run** | Errors blocking the run and warnings requiring acknowledgement |
| **Variance analysis** | **CFO, HR Director** | **Per run** | Employees with gross or net variance beyond threshold, with cause |
| Payroll register | HR Director, CFO, auditor | Per run | Every employee, every element, gross to net |
| **Payroll to GL reconciliation** | **CFO, auditor** | **Per run** | Run totals against GL posting against bank disbursement |
| Statutory deduction summary | HR Director, CFO | Monthly | Tax, PF, other statutory deductions by entity |
| **Withholding return** | **CFO, NBR** | **Quarterly** | Return data for the 25 October, 25 January, 25 April, 25 July deadlines |
| **Gratuity provision** | **CFO, auditor** | **Monthly** | Accrual movement, cumulative provision, employees by service band |
| PF fund position | CFO, trustees | Monthly | Contributions, withdrawals, balance by member |
| Payroll cost analysis | CFO, branch managers, M54 | Monthly | Cost by entity, branch, department, cost centre, element against budget |
| Overtime cost | HR Director, CFO | Monthly | Overtime hours and cost by branch, against budget |
| **Segregation of duties evidence** | **GRC, auditor** | **Per run** | Preparer, approver, releaser — distinct identities confirmed |
| Final settlement register | HR Director, CFO | Monthly | Settlements computed, approved, paid, outstanding |
| Payslip distribution | HR Director | Per run | Payslips generated, accessed, undelivered |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-235 | **Payroll processing time** | 3 days | < 8 hours | **< 4 hours** |
| KPI-236 | **Payroll corrections per run** | unmeasured | < 1% | **< 0.3%** |
| KPI-237 | **Statutory filings on time** | manual | **100%** | **100%** |
| KPI-238 | **Payroll runs on unlocked attendance periods** | n/a | **0** | **0** |
| KPI-239 | **Segregation-of-duties breaches** | n/a | **0** | **0** |
| KPI-240 | Payroll to GL to bank reconciliation | manual | **100%** | **100%** |
| KPI-241 | Payslips delivered on pay date | unmeasured | 98% | **100%** |
| KPI-242 | Payroll disputes raised per run | unmeasured | < 1.5% | **< 0.5%** |
| KPI-243 | BEFTN files rejected by the bank | unmeasured | < 1% | **0** |
| KPI-244 | **Gratuity provision published monthly** | never | **100%** | **100%** |
| KPI-245 | Final settlement paid within 30 days of clearance | unmeasured | 90% | **> 98%** |
| KPI-246 | **TIN found outside the resident store** | n/a | **0** | **0** |
| KPI-247 | Full payroll run duration (500+ employees) | 3 days | < 30 min | **< 20 min** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `hr_payroll_community` — structure, rules, payslip framework | 20% |
| L5 | `cd_payroll_bd`, `cd_statutory_bd`, `cd_beftn`, `cd_benefits`, `cd_final_settlement` | 80% |

> **No L1 coverage.** Odoo Community does not ship a payroll engine, and no OCA Bangladesh
> localisation exists. The statutory content is entirely custom and entirely the Company's to
> maintain.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 5 of 5 identifiers below are claimed by another module: **CD-076** also claimed by M17; **CD-077** also claimed by M17; **CD-078** also claimed by M48; **CD-079** also claimed by M48; **CD-080** also claimed by M18. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-076 | **`cd_payroll_bd`** — engine, elements, sequence, balances, proration, retro, run lifecycle | Odoo module | **9 PW** |
| CD-077 | **`cd_statutory_bd`** — versioned statutory pack, tax computation, categories, rebate, minimum tax, PF, gratuity | Odoo module | **7 PW** |
| CD-078 | **`cd_beftn`** — bank file generation, validation, release control, disbursement confirmation | Odoo module | **3 PW** |
| CD-079 | `cd_benefits` — PF ledger, insurance, loans, advances, recovery limits | Odoo module | 4 PW |
| CD-080 | `cd_final_settlement` — settlement computation, clearance gate, certificates | Odoo module | 3 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M55 Workforce** | **Blocking, absolute** — payroll cannot run without verified locked hours |
| **M21 Core HR** | **Blocking** — employee, contract and salary structure |
| **BEFTN format confirmed with the banking partner** | **Blocking** *(DEP-07)* — the file specification must come from the bank |
| **Statutory pack authored and approved** | **Blocking** — thresholds, slabs, rebate, PF and gratuity rules must be documented before configuration |
| M19 General Ledger | Posting target — live from W3 |
| M50 Treasury | Disbursement execution — live from W3 |
| M57 Performance | Incentive input — same wave; payroll can run without incentive if M57 slips |
| M51 Tax | Return filing coordination — live from W4 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Salary structures | 500+ | `fix.salary.structure` (M21) | W5 |
| Year-to-date tax and PF balances | 500+ | `fix.payroll.balance`, `fix.pf.ledger` | **W5 — critical** |
| Outstanding loans and advances | Variable | `fix.loan` | W5 |
| Gratuity service history | 500+ | `fix.gratuity.accrual` (opening provision) | W5 |
| Investment declarations for the current year | 500+ | `fix.investment.declaration` | W5 |
| Historical payslips | **Not migrated** — retained as documents in M24 if they exist | — | — |

> **Migration warning — the most dangerous in the programme.** **Year-to-date balances must be
> exact.** If year-to-date tax, PF or gratuity balances are wrong at cutover, every subsequent
> calculation compounds the error, and the year-end tax certificate will be wrong for every
> employee. Cutover at the **start of an assessment year** if at all possible; if not, reconcile
> year-to-date balances employee by employee and obtain sign-off from both HR Director and CFO
> before the first live run.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **Two full parallel payroll cycles run alongside the existing process with zero unexplained differences** | **Two months of parallel run, reconciled employee by employee, signed by HR Director and CFO** |
| AC-02 | **Payroll cannot run for a period whose attendance is unlocked in M55** | **Negative test through UI and API** |
| AC-03 | **The preparer cannot approve; the approver cannot release** | **Negative test for all three permission combinations** |
| AC-04 | A committed run is immutable; change is possible only via an approved correction run | Negative test |
| AC-05 | **Tax computation is correct for every taxpayer category, including minimum tax and investment rebate** | **Test matrix across all four categories and rebate boundaries, verified against manual calculation** |
| AC-06 | **A retroactive calculation for a prior period uses that period's statutory pack version** | **Scripted test across an assessment-year boundary** |
| AC-07 | **Gratuity accrues at not less than 30 days' wages per completed year at the last-drawn rate** | **Calculation audit against Labour Act for 20 employees across service bands** |
| AC-08 | The BEFTN file validates against the bank specification and is accepted on first submission | Bank test submission |
| AC-09 | Payroll reconciles to the GL posting and to the bank disbursement | Three consecutive runs |
| AC-10 | **The payslip shows hours, rates, every element, tax basis, incentive detail and year-to-date balances, in Bengali and English** | **Review by HR Director and a technician sample** |
| AC-11 | **Final settlement cannot be released before exit clearance is complete** | **Negative test** |
| AC-12 | **The quarterly withholding return prepares correctly for the statutory deadline** | **One full quarter cycle** |
| AC-13 | **Salary, bank details and TIN require step-up authentication and log every access; TIN is absent from every regional store** | **Access audit and data-flow audit** |
| AC-14 | **Year-to-date balances at cutover reconcile exactly to the legacy position** | **Employee-by-employee reconciliation signed by HR Director and CFO** |
| AC-15 | Full payroll run for 500+ employees completes in ≤ 20 minutes | Load test |
| AC-16 | HR Director, CFO and the Payroll Officer sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Have the AY 2026–27 tax slabs been finalised?** Sources conflict on whether the 5% introductory slab is abolished and what the resulting slab structure is. **The pack must be built from the enacted Finance Act, not from press reporting.** | CFO / Tax advisor | **W5 minus 3 months** |
| Q-02 | **Has the BEFTN file specification been obtained from the banking partner?** *(DEP-07)* | CFO | **W5 minus 4 months** |
| Q-03 | **Does a Provident Fund exist, and what are the contribution rates and rules?** *(links to M21 Q-02)* | HR Director / CFO | **W5 minus 3 months** |
| Q-04 | Is gratuity paid at the statutory minimum of 30 days per year, or at a higher rate by policy? | HR Director / CFO | W5 build |
| Q-05 | **Is there an existing gratuity provision in the accounts, or is this liability currently unrecorded?** | CFO / auditor | **Immediately** |
| Q-06 | How many festival bonuses are paid per year, at what rate, and to whom? | HR Director | W5 build |
| Q-07 | **Can cutover be aligned to the start of an assessment year?** If not, what is the year-to-date reconciliation plan? | HR Director / CFO | **W5 minus 4 months** |
| Q-08 | Do all employees have bank accounts, or is there a cash payment population requiring an exception path? | HR Director / CFO | W5 design |
| Q-09 | Who is appointed Payroll Officer? This role must be distinct from the approver and the releaser. | HR Director | **W5 minus 2 months** |
| Q-10 | Is a specialist Bangladesh payroll or tax advisor engaged to validate the statutory pack before go-live? | CFO | **W5 minus 3 months** |

**Q-01 and Q-05 are the material ones.** Building a statutory pack from press reporting rather
than the enacted Finance Act is how payroll goes wrong at scale. An unrecorded gratuity
liability across 500+ staff with years of service is a material balance-sheet issue independent
of this programme.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (why payroll is separate), §7 (statutory obligations), §10 (risks) ·
`M21_Core_HR_and_Employee_Lifecycle.md` · `M55_Time_Attendance_and_Workforce_Scheduling.md` ·
`M57_Performance_Incentives_and_Compensation.md` ·
`03_Modules/G_Finance_and_Treasury/_CATEGORY_OVERVIEW.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-HRM-007/009/010/011,
BRU-HRM-05, §6.2 Process 9, DEP-07 · `1000FiX_ERP_System_Comprehensive_URD.md` Personas 9–10

**External benchmark and regulation** *(verified 2026-08-12)*
**Bangladesh Labour Act 2006 (as amended)** — **gratuity at wages of at least 30 days at the
last-drawn rate for every completed year of service**; Provident Fund formation where
three-quarters of workers demand it; Workers' Participation and Welfare Funds ·
**NBR income tax, assessment year 2026–27** — tax-free threshold **BDT 375,000** general,
**BDT 425,000** women and 65+, **BDT 500,000** persons with disabilities and third gender,
**BDT 525,000** war-wounded freedom fighters and July Warriors 2024; **minimum tax BDT 5,000**
(BDT 1,000 for first-time registrants); **investment rebate reduced to 10%** with eligible
investment capped at **BDT 750,000**; top rate **30%** ·
**NBR withholding returns** — frequency **moved from monthly to quarterly**, deadlines
**25 October, 25 January, 25 April, 25 July** ·
**Bangladesh Personal Data Protection Act 2026** — payroll data is personal data; TIN is
sensitive personal data with cross-border transfer restriction ·
SAP Payroll country packs and payroll control centre · Oracle Global Payroll element and
balance architecture · Workday Payroll off-cycle model · OCA `hr_payroll_community`

---

*Module M56 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
