---
id: FIX-ERP2-008
title: Pillar D — Finance, People & Governance Modules (M19–M24)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Pillar D — Finance, People & Governance
# Modules M19–M24: Features & Functions

**Pillar owners:** CFO (M19, M20) · HR Director (M21, M22) · Quality Manager (M23, M24)
**Data domain:** Money, workforce, competency, quality, records
**Modules:** M19 FIN · M20 BIL · M21 HRM · M22 LMS · M23 QMS · M24 DMS

---

# M19 — Financial Management & Bangladesh Compliance (FIN)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M19 / `FIN` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W3 |
| **Delivery layers** | L1 (Odoo account) + L2 (OCA account-financial-tools, l10n-bangladesh) + L5 (CD-083…089) |
| **Requirements** | FR-FIN-001 … FR-FIN-068 |
| **Effort** | 42 person-weeks |

## 1. Purpose

M19 is the **statutory ledger**. It holds the general ledger, receivables, payables, banking,
fixed assets, taxation and the Bangladesh regulatory obligations. Commercial billing logic
lives in M20; M19 receives its postings and remains the single financial truth.

## 2. Scope Expansion Over v1.0

| v1.0 | v2.0 Addition |
|---|---|
| Single company | Multi-entity with inter-company transactions and consolidation |
| BDT | Multi-currency with FX revaluation for imports, cross-border sales and brand claims in USD |
| Branch P&L | + Business-line P&L across 14 revenue streams, + cost-centre and project dimensions |
| Mushak 6.3 invoice | + Full VAT sub-ledger, e-VAT return preparation, VAT on marketplace (agent vs principal), input VAT credit tracking |
| TDS on vendor payments | + TDS on all applicable categories with challan tracking and certificate issuance |
| Fixed assets | + Rental asset fleet depreciation, + component depreciation, + revaluation and impairment |
| — | Cash-flow forecasting driven by receivables, payables and contract schedules |
| — | Budgeting and variance analysis by branch, business line and cost centre |
| — | Marketplace settlement accounting, escrow and payable-to-seller control accounts |

## 3. Functional Areas & Features

### 3.1 General Ledger & Structure

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-001 | Chart of accounts | Maintain a Bangladesh-compliant chart of accounts with entity, branch, cost-centre, business-line and project dimensions | P0 |
| FR-FIN-002 | Multi-entity accounting | Maintain separate books per legal entity with defined inter-company relationships | P1 |
| FR-FIN-003 | Journal management | Manage journals by type with numbering, approval and posting controls | P0 |
| FR-FIN-004 | Automatic postings | Post automatically from every source module — service, inventory, payroll, billing, settlement — with defined posting rules | P0 |
| FR-FIN-005 | Manual journals | Allow manual journals with approval, supporting-document attachment and reversal capability | P0 |
| FR-FIN-006 | Period management | Open, soft-close and hard-close periods; enforce a Bangladesh fiscal year (July–June) | P0 |
| FR-FIN-007 | Multi-currency | Record transactions in any currency with the functional currency as BDT; revalue balances at period end | P1 |
| FR-FIN-008 | Inter-company transactions | Record and eliminate inter-company balances at consolidation | P2 |
| FR-FIN-009 | Audit trail | Maintain an immutable, complete audit trail of every posting — who, what, when, before and after | P0 |

### 3.2 Accounts Receivable

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-010 | Customer ledger | Maintain a customer sub-ledger reconciled to the GL control account | P0 |
| FR-FIN-011 | Invoice posting | Post invoices raised by M20 with correct revenue, tax and dimension coding | P0 |
| FR-FIN-012 | Receipt processing | Record receipts by cash, card, bKash, Nagad, bank transfer and wallet, with automatic matching | P0 |
| FR-FIN-013 | Automated bank reconciliation | Import bank statements and match automatically, presenting only exceptions | P0 |
| FR-FIN-014 | Ageing & collections | Age receivables and drive a collections workflow with escalating reminders | P0 |
| FR-FIN-015 | Credit control | Enforce credit limits and holds set in M07; release with approval | P1 |
| FR-FIN-016 | Credit notes & refunds | Issue credit notes with approval and reason codes; process refunds through the original method | P0 |
| FR-FIN-017 | Bad debt provisioning | Provide for doubtful debts on a policy basis and write off with approval | P2 |

### 3.3 Accounts Payable

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-018 | Vendor ledger | Maintain a vendor sub-ledger reconciled to the GL control account | P0 |
| FR-FIN-019 | Invoice approval | Route vendor invoices through approval after three-way matching in M16 | P0 |
| FR-FIN-020 | Payment runs | Execute scheduled payment runs with bank file generation and approval workflow | P1 |
| FR-FIN-021 | Payment methods | Support cheque, bank transfer, BEFTN, RTGS and mobile money vendor payments | P1 |
| FR-FIN-022 | Advance & prepayment | Manage vendor advances and their settlement against invoices | P1 |
| FR-FIN-023 | Vendor statements | Reconcile vendor statements to the ledger and resolve differences | P2 |

### 3.4 Banking & Cash

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-024 | Bank account master | Manage bank accounts per entity with signatories and limits | P0 |
| FR-FIN-025 | Branch cash control | Consolidate cash positions from 51+ branch cash drawers (M04) with daily reconciliation | P0 |
| FR-FIN-026 | Cash deposits | Record deposits from branches to bank and match to statement | P0 |
| FR-FIN-027 | Petty cash | Manage branch petty cash floats with expense capture and replenishment | P1 |
| FR-FIN-028 | Payment gateway settlement | Reconcile gateway settlements (bKash, Nagad, SSLCOMMERZ) against transactions, fees and chargebacks | P0 |
| FR-FIN-029 | Cash-flow forecast | Forecast cash from receivables ageing, payables schedule, contract billing and payroll | P2 |

### 3.5 Taxation — Bangladesh

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-030 | VAT configuration | Configure VAT rates, exemptions and treatments by product, service and customer class | P0 |
| FR-FIN-031 | Mushak 6.3 invoice | Generate NBR-compliant Mushak 6.3 tax invoices with BIN, sequence and prescribed layout, in Bengali | P0 |
| FR-FIN-032 | VAT sub-ledgers | Maintain Mushak 6.1, 6.2, 6.2.1, 6.3, 6.5, 6.6 registers as applicable | P0 |
| FR-FIN-033 | Input VAT credit | Track input VAT on purchases and imports and offset against output VAT | P0 |
| FR-FIN-034 | VAT return preparation | Compile the Mushak 9.1 monthly return from ledger data with reconciliation to the GL | P0 |
| FR-FIN-035 | Marketplace VAT treatment | Apply the correct principal-vs-agent VAT treatment to marketplace transactions | P0 |
| FR-FIN-036 | TDS/VDS deduction | Deduct tax at source on applicable vendor payments at the correct rate by category | P0 |
| FR-FIN-037 | TDS challan & certificates | Track deposit challans and issue withholding certificates to vendors | P0 |
| FR-FIN-038 | Corporate income tax support | Produce the schedules required for corporate tax computation and filing | P1 |
| FR-FIN-039 | Customs & import duty | Account for duty, import VAT and clearing charges, linking to landed cost in M15/M16 | P2 |
| FR-FIN-040 | High-value cash NID rule | Enforce NID capture on cash receipts above the statutory threshold | P0 |

### 3.6 Fixed Assets

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-041 | Asset register | Maintain the fixed-asset register with acquisition, category, location, custodian and linkage to M17 | P1 |
| FR-FIN-042 | Depreciation | Calculate and post depreciation by method and rate, including rental-fleet assets | P1 |
| FR-FIN-043 | Asset movement | Record transfers, disposals, write-offs and gains/losses on disposal | P1 |
| FR-FIN-044 | Capital work in progress | Track CWIP and capitalise on commissioning | P2 |
| FR-FIN-045 | Impairment & revaluation | Record impairment and revaluation with approval | P2 |

### 3.7 Reporting, Budgeting & Close

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FIN-046 | Statutory financial statements | Produce a balance sheet, profit and loss, and cash-flow statement per entity and consolidated | P0 |
| FR-FIN-047 | Dimensional P&L | Produce P&L by branch, business line, cost centre, customer segment and contract | P0 |
| FR-FIN-048 | Budgeting | Prepare budgets by dimension with version control and approval | P2 |
| FR-FIN-049 | Budget variance | Report actual vs budget with variance analysis and commentary capture | P2 |
| FR-FIN-050 | Month-end close checklist | Drive a structured close with owners, dependencies and completion tracking | P1 |
| FR-FIN-051 | Close automation | Automate accruals, prepayment amortisation, FX revaluation and recurring journals | P1 |
| FR-FIN-052 | Management reporting pack | Generate the monthly management pack automatically on close | P1 |

*(FR-FIN-053 … FR-FIN-068 cover inter-company reconciliation, consolidation, audit support,
financial controls testing, and treasury — catalogued in Doc 11.)*

## 4. Key Entities

`account.move` (ext) · `fix.posting.rule` · `fix.dimension.set` · `fix.mushak.invoice` ·
`fix.vat.register` · `fix.vat.return` · `fix.tds.record` · `fix.tds.challan` ·
`fix.bank.account` · `fix.bank.statement.line` (ext) · `fix.gateway.settlement` ·
`fix.cash.position` · `fix.fixed.asset` · `fix.depreciation.schedule` · `fix.budget` ·
`fix.close.checklist` · `fix.fx.revaluation`

## 5. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Month-end close cycle | 15–20 days | ≤ 3 days |
| Bank reconciliation auto-match rate | manual | > 94% |
| Days sales outstanding | unmeasured | < 32 days |
| VAT return filed on time | manual | 100%, zero adjustments |
| Tax compliance findings | unmeasured | Zero |
| Unreconciled gateway settlements > 7 days | unmeasured | Zero |
| Audit adjustments at year end | unmeasured | < 0.5% of revenue |

---

# M20 — Billing, Revenue Recognition & Settlement (BIL)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M20 / `BIL` |
| **Status** | ★ New in v2.0 (split from v1.0 Finance) |
| **Priority** | P1 |
| **Wave** | W4 (core) → W7 (marketplace settlement) |
| **Delivery layers** | L5 (CD-090…095) |
| **Requirements** | FR-BIL-001 … FR-BIL-051 |
| **Effort** | 38 person-weeks |

## 1. Purpose

Fourteen revenue streams bill in fundamentally different ways: one-off repair invoices,
recurring AMC subscriptions, per-seat MSP fees, metered storage, rental periods plus damages,
marketplace commissions with seller payouts, brand warranty claims, ad placements and
material-recovery credits.

M20 is the engine that converts **activity into money owed and money owing**, then hands the
postings to M19. Separating it from the statutory ledger keeps the ledger stable while
commercial models evolve.

## 2. Functional Areas & Features

### 2.1 Billing Engine

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BIL-001 | Billable event capture | Capture billable events from every module — job completed, visit delivered, seat consumed, storage used, rental day elapsed, commission earned | P1 |
| FR-BIL-002 | Charge determination | Resolve the applicable price from M11 price books, contract terms, entitlements and offers | P1 |
| FR-BIL-003 | Automatic invoice generation | Generate an invoice from a completed job without manual data entry | P0 |
| FR-BIL-004 | Recurring/subscription billing | Bill contracts on their cycle with proration, mid-cycle changes and arrears/advance handling | P1 |
| FR-BIL-005 | Usage/metered billing | Bill metered consumption (storage GB, remote-session minutes, print counts, overage hours) with tiered rates | P2 |
| FR-BIL-006 | Consolidated B2B invoicing | Produce one consolidated invoice per corporate customer per cycle, itemised by site, department and asset | P1 |
| FR-BIL-007 | Split billing | Split a single job's charges between customer, insurer, brand and contract | P2 |
| FR-BIL-008 | Invoice approval | Route invoices above thresholds or with exceptions for approval before issue | P1 |
| FR-BIL-009 | Multi-channel delivery | Deliver invoices by email, WhatsApp, SMS link, portal and print, with delivery confirmation | P0 |
| FR-BIL-010 | Payment links | Attach a payment link (bKash / Nagad / card) to every issued invoice | P0 |

### 2.2 Collections & Dunning

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BIL-011 | Dunning sequences | Define escalating reminder sequences by customer class and value, executed automatically | P1 |
| FR-BIL-012 | Promise to pay | Record payment promises and monitor them | P2 |
| FR-BIL-013 | Payment plans | Agree and manage instalment plans with schedule tracking | P2 |
| FR-BIL-014 | Service suspension | Suspend contracted services on defined non-payment triggers, with reinstatement rules | P1 |
| FR-BIL-015 | Collections queue | Present a prioritised collections work queue by value, age and risk | P1 |

### 2.3 Revenue Recognition

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BIL-016 | Performance obligations | Identify performance obligations per contract and allocate transaction price | P2 |
| FR-BIL-017 | Revenue schedules | Generate deferral and recognition schedules for subscriptions, warranty products and prepaid packages | P2 |
| FR-BIL-018 | Point-in-time recognition | Recognise repair and product revenue at the point of transfer | P1 |
| FR-BIL-019 | Over-time recognition | Recognise contract revenue over the service period | P2 |
| FR-BIL-020 | Deferred revenue reporting | Report the deferred revenue balance and its future release profile | P2 |
| FR-BIL-021 | Warranty liability | Accrue expected cost of honouring sold warranty products and release it as claims occur | P2 |

### 2.4 Commissions & Partner Settlement

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BIL-022 | Commission schemes | Configure commission by seller tier, category, value band, promotion and period | P1 |
| FR-BIL-023 | Commission calculation | Calculate commission per marketplace transaction with taxes and withholding | P1 |
| FR-BIL-024 | Seller statement | Produce a periodic seller statement of earnings, commissions, fees, adjustments and net payable | P1 |
| FR-BIL-025 | Payout runs | Execute scheduled payouts to sellers with approval, bank/mobile-money file generation and confirmation | P1 |
| FR-BIL-026 | Payout controls | Apply hold periods, dispute holds, minimum thresholds and bar/unbar controls | P1 |
| FR-BIL-027 | Escrow handling | Hold customer funds in escrow until job completion where the commercial model requires it | P2 |
| FR-BIL-028 | Referral & alliance commissions | Calculate and pay referral and partner commissions from M10 | P2 |
| FR-BIL-029 | Sales incentive calculation | Calculate sales-team commissions and pass to payroll in M21 | P2 |
| FR-BIL-030 | Chargebacks & clawbacks | Reverse commissions on refund, dispute or fraud with full traceability | P1 |

### 2.5 Refunds, Credits & Adjustments

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-BIL-031 | Refund request workflow | Raise, approve and execute refunds with reason codes and evidence | P1 |
| FR-BIL-032 | Gateway reversal | Process refunds through the original payment method where the gateway supports it | P1 |
| FR-BIL-033 | Store credit | Issue store credit to the customer wallet as an alternative to cash refund | P2 |
| FR-BIL-034 | SLA credits | Apply contractual service credits calculated in M08/M05 to the next invoice | P1 |
| FR-BIL-035 | Goodwill adjustments | Apply goodwill discounts with approval, reason and cost attribution | P1 |
| FR-BIL-036 | Dispute holds | Suspend collection on a disputed invoice pending resolution | P1 |

*(FR-BIL-037 … FR-BIL-051 cover advertising billing, deposit accounting, prepaid packages,
billing analytics, and revenue assurance controls — catalogued in Doc 11.)*

## 3. Key Entities

`fix.billable.event` · `fix.charge` · `fix.invoice.request` · `fix.subscription` ·
`fix.subscription.cycle` · `fix.usage.record` · `fix.consolidated.invoice` ·
`fix.dunning.sequence` · `fix.payment.plan` · `fix.revenue.schedule` ·
`fix.performance.obligation` · `fix.commission.entry` · `fix.seller.statement` ·
`fix.payout.run` · `fix.payout.line` · `fix.escrow.holding` · `fix.refund.request` ·
`fix.sla.credit.application` · `fix.warranty.liability`

## 4. KPIs

| KPI | Target |
|---|---|
| Invoices auto-generated without manual entry | 100% |
| Invoice issued within 1 hour of job closure | > 97% |
| Billing accuracy (credit notes as % of invoices) | < 1.5% |
| Subscription billing accuracy | > 99.5% |
| Seller payout accuracy | 100% |
| Seller payout on schedule | > 99% |
| Revenue leakage (unbilled delivered work) | < 0.5% |
| Deferred revenue reconciled to contracts | 100% |

---

# M21 — HR, Payroll & Workforce Management (HRM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M21 / `HRM` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W5 |
| **Delivery layers** | L1 (Odoo hr, attendance, holidays) + L2 (OCA hr, payroll) + L5 (CD-096…101) |
| **Requirements** | FR-HRM-001 … FR-HRM-052 |
| **Effort** | 31 person-weeks |

## 1. Purpose

M21 employs, schedules, pays and rewards 500+ people across 51+ locations, including
200–400 field technicians whose pay is linked to measured performance.

## 2. Functional Areas & Features

### 2.1 Employee Lifecycle

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-HRM-001 | Employee master | Maintain complete personal, employment, statutory, banking, emergency-contact and document records | P1 |
| FR-HRM-002 | Organisation structure | Model entity → division → department → branch → team with reporting lines and positions | P1 |
| FR-HRM-003 | Employment contracts | Record contract type (permanent, contractual, probation, part-time, apprentice), terms and renewals | P1 |
| FR-HRM-004 | Onboarding | Drive a structured onboarding checklist — documents, IT access, equipment, induction, mandatory training | P1 |
| FR-HRM-005 | Transfers & promotions | Record movements with effective dating and automatic access changes | P1 |
| FR-HRM-006 | Offboarding | Drive exit: clearance, asset return, access revocation, final settlement, exit interview | P1 |
| FR-HRM-007 | Document expiry tracking | Track expiry of NID, licences, medical certificates and work permits with alerts | P2 |

### 2.2 Time, Attendance & Scheduling

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-HRM-008 | Biometric attendance | Ingest attendance from biometric devices at branches | P1 |
| FR-HRM-009 | GPS mobile clock-in | Allow field staff to clock in and out from the mobile app with geofence validation | P1 |
| FR-HRM-010 | Attendance exceptions | Detect late, early, absent and missing punches, and route for regularisation approval | P1 |
| FR-HRM-011 | Shift & roster management | Plan shifts and rosters per branch and zone; publish to staff; feed availability to M02 dispatch | P1 |
| FR-HRM-012 | Overtime | Require pre-approval for overtime; record actual overtime and feed payroll | P1 |
| FR-HRM-013 | Leave management | Manage annual, sick, casual, maternity, paternity and unpaid leave with balances, accrual and encashment | P1 |
| FR-HRM-014 | Leave approval | Route leave through approval with coverage-threshold checks | P1 |
| FR-HRM-015 | Holiday calendar | Maintain the Bangladesh public-holiday calendar including moon-dependent dates, applied automatically | P1 |
| FR-HRM-016 | On-call & standby | Manage on-call rotas for 24/7 support with associated allowances | P2 |

### 2.3 Payroll

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-HRM-017 | Salary structures | Define structures with basic, house rent, medical, conveyance, food and other allowances per Bangladesh practice | P1 |
| FR-HRM-018 | Payroll calculation | Calculate gross-to-net including attendance, overtime, incentives, deductions and arrears | P1 |
| FR-HRM-019 | Income tax computation | Apply Bangladesh income-tax slabs, investment rebates and monthly deduction | P0 |
| FR-HRM-020 | Provident fund & gratuity | Calculate PF contributions and gratuity provision per Bangladesh Labour Act | P0 |
| FR-HRM-021 | Statutory deductions | Apply all other statutory deductions and contributions | P0 |
| FR-HRM-022 | Loans & advances | Manage staff loans and advances with recovery schedules | P2 |
| FR-HRM-023 | Payroll approval & lock | Require review and approval before finalisation; lock the period on completion | P0 |
| FR-HRM-024 | BEFTN bank file | Generate the bank salary transfer file in the required Bangladesh format | P0 |
| FR-HRM-025 | Digital payslips | Generate and distribute bilingual payslips to employees securely | P1 |
| FR-HRM-026 | Payroll accounting | Post payroll to the general ledger with correct dimensional coding | P0 |
| FR-HRM-027 | Year-end tax statements | Produce annual tax statements and salary certificates | P1 |

### 2.4 Performance & Incentives

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-HRM-028 | Technician KPI capture | Capture jobs completed, first-time fix rate, CSAT, rework rate, SLA attainment, utilisation and revenue from M01/M02 | P1 |
| FR-HRM-029 | Incentive schemes | Define incentive schemes with thresholds, tiers, weightings and caps per role and grade | P1 |
| FR-HRM-030 | Incentive calculation | Calculate incentives monthly, with a minimum-threshold gate, and feed payroll | P1 |
| FR-HRM-031 | Incentive transparency | Show each technician their own scorecard and earned incentive in real time in the mobile app | P1 |
| FR-HRM-032 | Dispute handling | Allow an employee to query an incentive calculation with a defined resolution process | P2 |
| FR-HRM-033 | Performance appraisal | Run periodic appraisals with objectives, ratings, feedback and development actions | P2 |
| FR-HRM-034 | Succession & talent | Identify key roles, successors and flight risk | P3 |

### 2.5 Employee Self-Service

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-HRM-035 | Self-service portal | Let employees view their profile, payslips, leave balances, attendance and documents | P1 |
| FR-HRM-036 | Requests | Submit leave, overtime, expense, loan, document and grievance requests from web or mobile | P1 |
| FR-HRM-037 | Manager self-service | Let managers approve requests, view team attendance and see team KPIs from mobile | P1 |
| FR-HRM-038 | Expense claims | Submit and approve expense claims with receipt capture and reimbursement through payroll or AP | P1 |

*(FR-HRM-039 … FR-HRM-052 cover recruitment, disciplinary records, health and safety,
workforce analytics and HR compliance reporting — catalogued in Doc 11.)*

## 3. Key Entities

`hr.employee` (ext) · `fix.employment.contract` · `fix.org.position` · `fix.onboarding.task` ·
`fix.attendance.record` · `fix.attendance.exception` · `fix.shift.pattern` · `fix.roster` ·
`fix.overtime.request` · `hr.leave` (ext) · `fix.holiday.calendar` · `fix.salary.structure` ·
`fix.payslip` (ext) · `fix.tax.computation` · `fix.pf.record` · `fix.gratuity.provision` ·
`fix.beftn.file` · `fix.incentive.scheme` · `fix.incentive.calculation` ·
`fix.employee.kpi` · `fix.expense.claim`

## 4. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Payroll processing time | 3 days | < 4 hours |
| Payroll accuracy (corrections per run) | unmeasured | < 0.3% |
| Attendance capture completeness | manual books | > 99% |
| Leave balance disputes | frequent | < 5 per year |
| Technician incentive disputes | n/a | < 2% of calculations |
| Statutory filing on time | manual | 100% |
| Employee self-service adoption | 0% | > 85% |

---

# M22 — Learning, Certification & Technician Competency (LMS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M22 / `LMS` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W5 |
| **Delivery layers** | L4 (open-source LMS) + L5 (CD-102…104) |
| **Requirements** | FR-LMS-001 … FR-LMS-030 |
| **Effort** | 15 person-weeks |

## 1. Purpose

1000FiX is an authorised service partner for 17+ brands. **Every brand warranty job requires
a certified technician.** If a certification lapses unnoticed, the claim is rejected and the
revenue is lost — after the work has been done.

M22 makes competency an enforced system control rather than a filing-cabinet fact. It also
onboards and qualifies marketplace engineers, whose competency 1000FiX now vouches for.

## 2. Functional Areas & Features

### 2.1 Competency Framework

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LMS-001 | Competency model | Define competencies by device category, brand, repair level and speciality with proficiency levels | P2 |
| FR-LMS-002 | Role competency profiles | Define the competencies required for each role and grade | P2 |
| FR-LMS-003 | Individual competency record | Maintain each person's assessed competencies with evidence, assessor and date | P1 |
| FR-LMS-004 | Competency gap analysis | Report gaps between required and held competencies by person, branch and zone | P2 |
| FR-LMS-005 | Capacity by competency | Show how much certified capacity exists per brand and skill per zone — used for dispatch planning | P2 |

### 2.2 Certification Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LMS-006 | Certification register | Record every brand and vendor certification with issuing body, number, scope, issue and expiry dates and the certificate document | P1 |
| FR-LMS-007 | Expiry alerting | Alert the technician, their manager and HR at 90/60/30/15 days before expiry | P1 |
| FR-LMS-008 | Dispatch enforcement | Prevent assignment of brand warranty work to a technician whose certification has expired (hard block) | P0 |
| FR-LMS-009 | Re-certification workflow | Plan, schedule and track re-certification before expiry | P1 |
| FR-LMS-010 | Certification evidence | Store certificates with verification, retrievable for brand audits | P1 |
| FR-LMS-011 | External verification | Support verification of a certificate against the issuing brand where an interface exists | P3 |

### 2.3 Training Delivery

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LMS-012 | Course catalogue | Maintain courses with objectives, content, duration, prerequisites and the competencies they confer | P2 |
| FR-LMS-013 | Content delivery | Deliver online modules, videos and documents, with offline download for field staff | P2 |
| FR-LMS-014 | Classroom & practical | Schedule classroom and hands-on sessions with attendance capture | P2 |
| FR-LMS-015 | Learning paths | Define role-based paths (junior technician → senior technician → specialist) | P2 |
| FR-LMS-016 | Mandatory training | Assign and enforce mandatory training (safety, ISO, data protection, code of conduct) with completion deadlines | P1 |
| FR-LMS-017 | Bengali content | Deliver all field-facing training in Bengali | P1 |

### 2.4 Assessment & Certification Issuance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LMS-018 | Knowledge assessment | Run scored online assessments with question banks, randomisation and pass thresholds | P2 |
| FR-LMS-019 | Practical assessment | Record supervised practical assessments against defined criteria | P2 |
| FR-LMS-020 | Internal certification | Issue internal certifications with validity periods, feeding the competency record | P2 |
| FR-LMS-021 | Re-assessment triggers | Trigger re-assessment automatically on a quality event — repeated rework, failed QC, complaint | P2 |

### 2.5 Marketplace Seller Qualification

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LMS-022 | Seller onboarding curriculum | Require marketplace engineers to complete a standards and platform curriculum before activation | P2 |
| FR-LMS-023 | Seller skill declaration & test | Verify declared skills with an assessment before granting category access | P2 |
| FR-LMS-024 | Continuous standards training | Push updated standards to sellers with acknowledgement tracking | P3 |

*(FR-LMS-025 … FR-LMS-030 cover training cost tracking, external training providers,
training effectiveness measurement and learning analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.competency` · `fix.competency.level` · `fix.role.profile` · `fix.employee.competency` ·
`fix.certification` · `fix.certification.record` · `fix.course` · `fix.course.content` ·
`fix.learning.path` · `fix.enrolment` · `fix.assessment` · `fix.assessment.result` ·
`fix.training.session` · `fix.seller.qualification`

## 4. KPIs

| KPI | Target |
|---|---|
| Certifications current (no lapses) | 100% |
| Claims rejected for uncertified technician | Zero |
| Mandatory training completion | > 98% on time |
| Competency gap in any zone/brand | Zero critical gaps |
| Average training hours per technician per year | > 24 |
| Post-training first-time-fix improvement | > 5 percentage points |

---

# M23 — Quality, ISO & Compliance Management (QMS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M23 / `QMS` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W5 |
| **Delivery layers** | L2 (OCA management-system, 33 modules) + L5 (CD-105…106) |
| **Requirements** | FR-QMS-001 … FR-QMS-037 |
| **Effort** | 17 person-weeks |

## 1. Purpose

1000FiX is Bangladesh's **only ISO 9001:2015 certified** IT service provider. That
certification is a commercial differentiator and an operational obligation: it requires
documented, traceable, continually improved processes.

M23 runs the management systems — ISO 9001 quality, ISO 27001 information security, and the
compliance obligations arising from the new business lines (data services, e-waste, marketplace).

## 2. Functional Areas & Features

### 2.1 Management System Framework

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-001 | Standards register | Maintain the standards the Company operates under (ISO 9001:2015, ISO 27001, and applicable regulations) with clause-level mapping to processes and controls | P1 |
| FR-QMS-002 | Policy & procedure control | Author, review, approve, publish, version and withdraw policies and procedures with acknowledgement tracking | P1 |
| FR-QMS-003 | Process register | Maintain the process map with owners, inputs, outputs, controls and KPIs | P1 |
| FR-QMS-004 | Context & interested parties | Record organisational context, interested parties and their requirements per ISO 9001 clause 4 | P2 |
| FR-QMS-005 | Risk & opportunity register | Maintain quality and information-security risks with assessment, treatment and review | P1 |
| FR-QMS-006 | Management review | Schedule, conduct and record management reviews with the required inputs and outputs | P1 |
| FR-QMS-007 | Objectives & planning | Set quality objectives, cascade them and track attainment | P2 |

### 2.2 Quality Control in Operations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-008 | Inspection & checklist library | Maintain QC checklists per device type, repair level, business line and process stage | P0 |
| FR-QMS-009 | QC enforcement | Enforce mandatory QC completion before defined state transitions in M01, M13, M14 and M18 | P0 |
| FR-QMS-010 | Sampling plans | Define statistical sampling for independent QC on high-volume, low-risk work | P2 |
| FR-QMS-011 | Field quality audits | Run scheduled and random field audits of completed work with evidence capture on mobile | P2 |
| FR-QMS-012 | Mystery shopping | Manage mystery-shopper programmes for branches and marketplace sellers | P3 |
| FR-QMS-013 | Calibration of test equipment | Ensure measurement equipment used in QC is calibrated (linked to M17) | P2 |

### 2.3 Non-Conformance & CAPA

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-014 | Non-conformance reporting | Raise NCRs from any source — QC failure, complaint, audit, rework, supplier defect, security incident | P1 |
| FR-QMS-015 | Classification & severity | Classify NCRs by type, process, severity and impact | P1 |
| FR-QMS-016 | Containment | Record immediate containment actions and affected scope | P1 |
| FR-QMS-017 | Root-cause analysis | Support structured root-cause methods (5-Why, fishbone) with evidence | P1 |
| FR-QMS-018 | Corrective & preventive action | Raise CAPAs with owners, due dates and verification of effectiveness | P1 |
| FR-QMS-019 | Effectiveness verification | Verify after a defined period that the CAPA worked; reopen if not | P1 |
| FR-QMS-020 | Trend analysis | Analyse NCR trends by process, branch, technician, supplier and device model | P1 |

### 2.4 Complaint Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-021 | Complaint intake | Receive complaints from every channel with automatic acknowledgement | P0 |
| FR-QMS-022 | Complaint classification | Classify by category, severity, product/service and responsible process | P1 |
| FR-QMS-023 | Complaint SLA | Apply resolution SLAs by severity with escalation | P1 |
| FR-QMS-024 | Investigation & resolution | Investigate, resolve, communicate to the customer and confirm satisfaction | P1 |
| FR-QMS-025 | Compensation & goodwill | Approve and apply goodwill remedies with cost attribution | P1 |
| FR-QMS-026 | Regulatory/consumer complaints | Handle complaints escalated to consumer-protection authorities with a defined process and evidence pack | P2 |

### 2.5 Audit Programme

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-027 | Audit plan | Maintain an annual internal audit programme covering all processes and branches | P1 |
| FR-QMS-028 | Audit execution | Conduct audits on mobile with checklists, evidence capture and offline support | P1 |
| FR-QMS-029 | Findings management | Record findings, classify them and link them to NCRs and CAPAs | P1 |
| FR-QMS-030 | External audit support | Prepare evidence packs for certification, brand-partner and regulator audits | P1 |
| FR-QMS-031 | Supplier & seller audits | Audit suppliers and marketplace sellers against defined criteria | P2 |

### 2.6 Information Security Management (ISO 27001)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-QMS-032 | Control register | Maintain the Statement of Applicability and control implementation status | P2 |
| FR-QMS-033 | Security incident management | Record, classify, investigate and close security incidents with breach-notification assessment | P1 |
| FR-QMS-034 | Asset & data classification | Classify information assets and apply handling rules | P2 |
| FR-QMS-035 | Access review | Run periodic access reviews with evidence (data from M29) | P2 |

*(FR-QMS-036 … FR-QMS-037 cover business-continuity planning and quality analytics —
catalogued in Doc 11.)*

## 3. Key Entities

`fix.standard.clause` · `fix.policy.document` · `fix.process.register` · `fix.risk.register` ·
`fix.management.review` · `fix.quality.objective` · `fix.checklist.template` ·
`fix.inspection.result` · `fix.nonconformance` · `fix.root.cause` · `fix.capa` ·
`fix.capa.verification` · `fix.complaint` (shared with M07) · `fix.audit.plan` ·
`fix.audit.execution` · `fix.audit.finding` · `fix.security.incident` · `fix.soa.control`

## 4. KPIs

| KPI | Target |
|---|---|
| ISO 9001 surveillance major non-conformances | Zero |
| CAPA closed on time | > 95% |
| CAPA effectiveness verified | > 90% |
| Complaint resolution within SLA | > 95% |
| Repeat complaints (same root cause) | < 5% |
| Internal audit plan completion | 100% |
| Rework rate (company-wide) | < 3% |
| Security incidents with breach notification required | Zero |

---

# M24 — Document Management, E-Signature & Records (DMS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M24 / `DMS` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W3 |
| **Delivery layers** | L2 (OCA dms) + L4 (Mayan EDMS) + L5 (CD-107…109) + L6 (e-signature) |
| **Requirements** | FR-DMS-001 … FR-DMS-030 |
| **Effort** | 15 person-weeks |

## 1. Purpose

Every module generates documents that must be found, proven, retained and eventually
destroyed: service reports, estimates, invoices, Mushak tax documents, contracts, warranty
evidence packs, chain-of-custody records, destruction certificates, disposal certificates,
ISO records, payroll documents and audit evidence.

M24 makes documents **retrievable and defensible**.

## 2. Functional Areas & Features

### 2.1 Repository & Classification

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DMS-001 | Central repository | Store all documents centrally with versioning, immutability where required, and linkage to their source record | P1 |
| FR-DMS-002 | Classification & metadata | Classify documents by type, business line, entity, branch, sensitivity and retention class | P1 |
| FR-DMS-003 | Auto-filing | File documents automatically from their originating transaction with the correct metadata | P1 |
| FR-DMS-004 | Search | Search by metadata and full text, including OCR'd content, in Bengali and English | P1 |
| FR-DMS-005 | Bengali OCR | Extract text from scanned Bengali and English documents | P2 |
| FR-DMS-006 | Bulk scanning | Support bulk digitisation of legacy paper records with batch metadata assignment | P2 |
| FR-DMS-007 | Storage tiering | Move older documents to lower-cost storage while keeping them retrievable | P3 |

### 2.2 Templates & Generation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DMS-008 | Template library | Maintain document templates — job sheets, estimates, service reports, invoices, contracts, certificates, gate passes | P1 |
| FR-DMS-009 | Bilingual generation | Generate every customer-facing document in Bengali or English by preference | P1 |
| FR-DMS-010 | Dynamic content | Populate templates from live data with conditional sections and branding per entity | P1 |
| FR-DMS-011 | Batch generation | Generate documents in bulk (statements, certificates, payslips) | P2 |
| FR-DMS-012 | Output formats | Produce PDF/A for archival, plus print and mobile-optimised formats | P1 |

### 2.3 Signature & Approval

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DMS-013 | In-person e-signature | Capture signatures on device screens with signer identity, timestamp and GPS | P1 |
| FR-DMS-014 | Remote e-signature | Send documents for remote signature with OTP-based identity verification | P1 |
| FR-DMS-015 | Qualified e-signature | Use an accredited provider for legally binding contracts (AMC, MSP, rental, seller agreements) | P2 |
| FR-DMS-016 | Signature audit trail | Maintain a tamper-evident audit trail of the signing process | P1 |
| FR-DMS-017 | Approval workflows | Route documents through configurable approval chains with delegation and escalation | P1 |
| FR-DMS-018 | Document integrity | Apply hashing and tamper detection to signed and archival documents | P1 |

### 2.4 Records Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DMS-019 | Retention schedules | Define retention periods per document class per the statutory table (see below) | P0 |
| FR-DMS-020 | Retention enforcement | Prevent premature deletion and trigger review or disposal at end of retention | P0 |
| FR-DMS-021 | Legal hold | Suspend disposal for documents under legal or investigative hold | P0 |
| FR-DMS-022 | Certified disposal | Dispose at end of retention with a disposal record | P1 |
| FR-DMS-023 | Evidence packs | Assemble a complete, indexed evidence pack for a claim, audit, dispute or regulator on demand | P1 |
| FR-DMS-024 | Access control & watermarking | Enforce document-level access control; watermark sensitive documents on view and download | P1 |
| FR-DMS-025 | Access audit | Log every view, download, print and share of a controlled document | P0 |

### Statutory Retention Table

| Document Class | Retention | Basis |
|---|---|---|
| Financial transactions, invoices, Mushak documents | 7 years | Bangladesh Companies Act / NBR |
| Customer records | 7 years after last transaction | Business law |
| Service and repair records | 5 years | Operational / warranty |
| Warranty claim evidence | 7 years | Brand partner audit requirements |
| Employee records | 10 years after termination | Bangladesh Labour Act |
| Payroll and tax records | 7 years | NBR |
| Audit logs and access records | 5 years | ICT Act / ISO 27001 |
| Data-recovery case records | 5 years; recovered data purged per agreement | ISO 27001 / DSA 2018 |
| Data destruction certificates | 7 years | Customer assurance / ISO 27001 |
| E-waste disposal certificates | 7 years | Environmental compliance |
| Contracts | 7 years after expiry | Contract law |
| ISO management-system records | 3 certification cycles | ISO 9001 |
| Marketplace seller agreements & KYC | 7 years after termination | Regulatory / dispute |

*(FR-DMS-026 … FR-DMS-030 cover portal document sharing, customer document access, and
document analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.document` · `fix.document.class` · `fix.document.version` · `fix.document.template` ·
`fix.signature.envelope` · `fix.signature.event` · `fix.approval.chain` ·
`fix.retention.schedule` · `fix.legal.hold` · `fix.disposal.record` · `fix.evidence.pack` ·
`fix.document.access.log`

## 4. KPIs

| KPI | Target |
|---|---|
| Documents auto-filed from transactions | > 96% |
| Document retrieval time | < 10 seconds |
| Paper documents in active use | Zero by W6 |
| Evidence pack assembly time | < 5 minutes |
| Retention violations | Zero |
| E-signature completion rate | > 92% |

---

*Next document: `09_Pillar_E_Intelligence_and_Platform_Modules.md`*
