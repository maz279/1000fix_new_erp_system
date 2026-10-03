---
id: FIX-ERP2-M52
module_id: M52
module_code: APE
module_name: Accounts Payable & Employee Expense
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P1
wave: W3
---

# M52 — Accounts Payable & Employee Expense
### Category G · Code `APE` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M52 |
| **Module code** | `APE` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M19 monolith after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (vendor bills), `hr_expense` · L2 OCA `account-invoicing`, `account-payment`, `hr-expense`, `purchase-workflow` · L5 custom matching, payment run and expense control |
| **Custom modules** | `cd_ap_ext`, `cd_payment_run`, `cd_expense_claim` |
| **Requirement range** | FR-APE-001 … FR-APE-038 |
| **Requirement count** | **38** *(measured — supersedes the 28 estimate in `02-02`)* |
| **Effort estimate** | **19 person-weeks** *(measured — supersedes the 14 PW estimate)* |
| **Depends on** | M19 GL · M33 Party Master · M16 Procurement · M15 Inventory · M51 Tax · M50 Treasury · M21 HR & Payroll · M29 Identity · M28 Integration |
| **Depended on by** | M16, M42, M15, M44, M50, M51, M19, M54, M49, M21, M12, M46, M47, M25 |

---

## 2. Purpose

M52 controls **everything the Company pays that is not payroll**: vendor invoices, imports,
sub-contractors, marketplace and courier partners, brand consignment settlements, utility and
facility costs, and the expense claims and cash advances of a workforce that spends most of its
day away from a desk.

Two failures define the current state. The first is the classic payables failure: an invoice is
approved because someone senior signed a piece of paper, not because the system proved that the
goods were ordered, received and priced as agreed. The second is specific to a field-service
business at this scale — **200 to 400 technicians and riders** incurring travel, parts-purchase,
customer-site and emergency costs every day, settled through informal advances and paper
vouchers that nobody can reconcile to a job.

M52 exists to make both provable. No vendor invoice reaches a payment run without a
three-way match or an approved, reason-coded exception. No expense reaches the ledger without a
claimant, an approver who is not the claimant, a policy check and a receipt. And no payment
leaves the Company without the correct tax deducted at source — because under Bangladeshi law,
failing to deduct makes the payer liable for the tax, plus a surcharge.

### Why It Exists

The v2.0 draft placed payables inside M19. That is the design most likely to produce a
material fraud loss, for a structural reason: the module that pays and the module that keeps the
book of record must be separable, so that the controls between them can be enforced by the
system rather than by trust. SOD-01 (create a vendor and approve their invoice) and SOD-02
(raise a purchase order, receive the goods and approve the invoice) are the two segregations
that every payables fraud in the literature defeats, and they can only be enforced where
payables is a module with its own identity.

Beyond control, there is cost. A three-way match exception rate that nobody measures means
overbilling by vendors is invisible. Payment terms that nobody tracks mean either late-payment
damage to supplier relationships or early payment that gives away working capital for nothing.
Both are measurable the day M52 goes live and neither is measurable today.

M52 is P1 and lands in Wave 3 because the ledger cannot be trusted while the payables side of it
is manual, and because M15's consignment settlements to 17+ brand partners have to land
somewhere.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-010 | "Process vendor invoices with 3-way matching (PO + GRN + Invoice)" |
| ERP BRD BR-SCM-005 | "Perform 3-way matching: PO + GRN + Vendor Invoice" |
| ERP BRD BRU-FIN-06 | "A vendor invoice cannot be approved for payment without a corresponding approved GRN in the system" |
| ERP BRD §Process 4 | "3-way match: PO + GRN + Invoice → AP payment queue" |
| ERP BRD UC-018 | New vendor onboarding — Procurement + Finance; vendor activated in master before POs can be raised |
| ERP BRD §Month-End Close Day 4 | "Finance reviews AP/AR aging → posts accruals" |
| `05-04` §6 SOD-01 | "Create vendor + approve vendor invoice → fictitious vendor payment → hard block" |
| `05-04` §6 SOD-02 | "Raise purchase order + receive goods + approve invoice → purchase fraud → hard block (any two permitted, not all three)" |
| `05-05` BRU-FIN-09 | "TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise" |
| `_CATEGORY_OVERVIEW.md` §2 | M52 scope: "Vendor invoices, three-way-matched approval, payment runs, advances, staff expense claims" |
| `_CATEGORY_OVERVIEW.md` §8 | Three-way match exception rate < 5% · vendor payment on terms > 95% |
| `M15` §12.2 | Consignment settlement obligations raised to M52 at the moment of consumption |
| Company Profile §Service Infrastructure | 51+ branches and a nationwide field force — the source of the expense-claim volume |
| Exec Summary §6.2 | Administrative labour savings **BDT 62 lac per year** across modules |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M52 sits between procurement (which buys) and treasury
> (which pays). Both boundaries are precise, and both sides agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Vendor invoice capture: manual entry, vendor-portal submission, email and scanned/OCR intake |
| 2 | **Three-way matching** of invoice to purchase order and goods receipt, with configurable tolerances |
| 3 | Two-way matching for services and non-PO spend, against a contract or an approved requisition |
| 4 | Match-exception management: quantity, price, tax, currency and timing variances, with resolution routing |
| 5 | Invoice approval workflow by value band, category, cost centre and entity |
| 6 | The payable open-item ledger, ageing and vendor balance |
| 7 | Payment terms, due-date calculation, early-settlement discount evaluation and payment prioritisation |
| 8 | Payment run: proposal, review, approval, release and instruction to M50 |
| 9 | Tax deduction at source on payment — TDS and VDS — applying the rates and rules determined by M51 |
| 10 | Vendor advances and prepayments, their approval, tracking and settlement against invoices |
| 11 | Debit notes, vendor credit notes and their application |
| 12 | Retention money withheld from sub-contractors and its scheduled release |
| 13 | Brand consignment settlement obligations arising from M15 stock consumption |
| 14 | Marketplace seller, courier and referral-partner payables where they are trade payables rather than settlements *(settlements themselves are M53)* |
| 15 | Employee expense claims: submission, receipt capture, policy validation, approval and reimbursement |
| 16 | Employee cash advances (technician float, travel advance, emergency purchase) and their settlement |
| 17 | Per-diem, mileage and field-allowance calculation against policy |
| 18 | Corporate card and fuel-card reconciliation where such instruments are in use |
| 19 | Expense policy configuration, limits, category rules and violation handling |
| 20 | Accrual of received-not-invoiced (GRNI) and unrecorded liabilities at period end |
| 21 | Vendor statements, reconciliation and dispute handling |
| 22 | Duplicate-invoice and duplicate-payment prevention |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Requisition, RFQ, purchase order creation and approval | **M16** Procurement | Buying is a commercial lifecycle; M52 pays for what M16 committed |
| Goods receipt, inspection, quantity acceptance | **M15** Inventory (with **M16**) | The receipt is a physical fact recorded where the goods arrive |
| Vendor qualification, onboarding, contract, scorecard, quality events | **M42** Supplier Relationship | M52 pays a vendor; it does not select or manage one |
| Vendor master record, bank details of record, party identity | **M33** Party Master (with **M42**) | One party record serves every module; changing vendor bank details is a controlled M33/M42 event |
| Import documentation, LC opening, customs clearance, duty computation | **M44** Import & Landed Cost (with **M50** for the LC instrument) | Cross-border supply is a discipline of its own |
| Landed-cost allocation to stock | **M44** | Computed once, upstream |
| Bank account operation, payment file transmission, bank confirmation | **M50** Treasury & Cash | M52 authorises a payment; M50 executes and proves it |
| Cash disbursement at a branch counter | **M04** Branch Operations (position via **M50**) | Physical cash movement happens at the counter |
| TDS/VDS rate determination, challan deposit, certificate issuance, return filing | **M51** Tax & Regulatory | M52 applies the deduction M51 determines; M51 owns the statutory obligation |
| Payroll, salary, statutory employee deductions, gratuity and leave provisions | **M21** HR & Payroll | Payroll is a separate lifecycle with separate controls |
| Employee master, grade, entitlement and reporting line | **M21** HR & Payroll | M52 reads entitlement; it does not define it |
| Journal posting of payables, expenses, accruals and TDS | **M19** General Ledger | Only Category G's ledger creates journal entries |
| Commission calculation and marketplace seller payout runs | **M53** Revenue & Settlement | A payout is a settlement of a revenue share, not a trade payable |
| Capital expenditure approval and asset capitalisation | **M49** Fixed Assets | M52 processes the vendor invoice; M49 decides it is an asset |
| Budget availability checking as a hard block | **M54** Costing & FP&A | M54 owns the budget; M52 consults it and reports the breach |
| Fleet fuel and vehicle running cost operational tracking | **M46** Fleet & Vehicle | M46 tracks consumption; M52 pays the invoice |
| Facility and utility contract management | **M47** Facility & Workplace | M47 manages the arrangement; M52 pays it |

### 3.3 Shared Concepts

| Concept | M52's Role | Owning Module |
|---|---|---|
| Vendor invoice | **Owns** — the defining artefact of this module | M52 |
| Purchase order | Reads for matching; never creates or amends | M16 |
| Goods receipt note | Reads for matching; never creates | M15 / M16 |
| Three-way match | **Owns** the match and the exception; M16 owns the PO terms being matched against | M52 / M16 |
| Vendor master and bank details | Reads; a bank-detail change is a controlled M33/M42 event that M52 blocks payment on until re-verified | M33 / M42 |
| Payable balance | Owns the open-item detail; M19 owns the control account | M52 / M19 |
| Payment instruction | **Owns** the authorisation; M50 executes | M52 / M50 |
| TDS / VDS | Applies the determination; M51 owns rates, challans and certificates | M52 / M51 |
| Expense claim | **Owns**; M21 owns the employee and the entitlement | M52 / M21 |
| Employee advance | **Owns** the financial control; M04/M02 own the operational float | M52 / M04 / M02 |
| Consignment settlement | Owns the payable; M15 owns the consumption that creates it | M52 / M15 |
| Retention money | **Owns** the withholding and release; M08/M16 own the contract term | M52 |
| GRNI accrual | **Owns** the calculation; M19 posts it | M52 / M19 |
| Budget check | Consults and reports; M54 owns the budget and the policy | M52 / M54 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — FI-AP & Logistics Invoice Verification (MM-IV)** | Invoice verification against PO and GR with tolerance keys per company code, blocked-for-payment status by block reason, automatic payment programme (F110) with proposal, edit, and run stages, payment method supplements | **The blocked-for-payment model**: a matched exception does not reject the invoice, it *blocks payment on that invoice* with a named block reason that only a specific role can release. This keeps the liability recorded (so the accounts are right) while stopping the money (so the control holds). Also adopted: the three-stage payment run — proposal → review → release — with different authority at each stage | SAP's tolerance-key configuration matrix depth; we ship four tolerance dimensions (quantity, price, tax, timing) with per-category values |
| **SAP Ariba / Concur pattern** | Supplier-network invoice submission, invoice-status visibility to the supplier, mobile expense capture with receipt imaging and policy engine | **Vendor-submitted invoices through P05** with status visibility, which removes the "where is my payment" call entirely; and **mobile-first expense capture with the receipt photographed at the moment of spend** — the only approach that works for 200–400 field staff | The supplier-network commercial model and its fees |
| **Oracle Fusion Cloud Payables** | Invoice imaging and OCR intake, invoice holds and releases, payment process requests with validation, supplier-portal collaboration, prepayment application, withholding tax at invoice or payment | **Withholding tax computed at payment rather than at invoice** — this matches Bangladeshi TDS/VDS practice where the deduction crystallises when the payment is made. Also adopted: duplicate-invoice detection on a configurable key set at the point of entry, before the invoice is saved | Oracle's payment-process-request depth; our payment run is simpler and bank-file-oriented |
| **Microsoft Dynamics 365 Finance — Accounts Payable & Expense Management** | Vendor invoice journal and workflow, invoice matching policies at header and line, vendor collaboration, expense report policies with per-diem and mileage rules, cash-advance workflow | **Expense policy as a rules engine that evaluates at submission**, so the claimant sees a violation before an approver's time is spent on it; and **cash advance as a first-class object** that must be settled before another is issued | The full travel-request/booking workflow; our field spend is not travel-booking shaped |
| **IFS Cloud — Financials & field-service expense** | Field-technician expense against a work order, purchase for a job | **Expense and advance attributable to a job, work order or contract** rather than only to a cost centre. In a service business, the technician's taxi fare belongs to a job's margin, not to a general overhead pool. This is what makes M54's job costing complete | IFS's project-invoicing and travel-management depth, which assumes a project-services operating model rather than a high-volume repair network |
| **Bangladeshi statutory practice — TDS/VDS at source** | Deduction at prescribed rates on payment; deposit by deadline; certificate issuance; payer liability plus surcharge on failure; 50% surcharge under s.142 where the payee has no PSR or payment is not by bank transfer | **Deduction as a hard block on the payment path**, not a post-hoc adjustment; and **PSR and bank-transfer status as payment-run attributes**, because both change the rate that must be applied | — |
| **Odoo 19 CE `account` (vendor bills) + `hr_expense` + OCA `account-payment`, `hr-expense`, `purchase-workflow`** | Vendor bills, bill-to-PO reference, payment registration, batch payments, employee expenses with attachment, expense approval | The transactional substrate. OCA `account_payment_*` supplies batch payment mechanics; `purchase_*_matching` patterns inform the match model | Odoo's default two-way bill matching, which accepts a bill against a PO without proving receipt — this is precisely the control BRU-FIN-06 forbids |

**Design position.** Five deliberate positions.

First, **an exception blocks the payment, not the record**. Getting this backwards is the most
common payables design error. If a mismatched invoice is rejected outright, the liability
disappears from the books and the month-end accrual is wrong; if it is approved to keep the
books tidy, the control is gone. M52 records every valid invoice as a liability and blocks
payment at the invoice level with a named block reason.

Second, **the vendor bank account is the highest-risk field in the system**. Payment
redirection fraud — where a vendor's bank details are quietly changed before a payment run — is
the single most effective fraud against a payables function. In M52, a bank-detail change on a
vendor triggers an automatic payment block on that vendor until the change is independently
verified through a call-back recorded in M42, and the block cannot be released by the person
who requested the change.

Third, **field expense is captured at the moment of spend, on a phone, against a job**. A
technician who must keep a paper receipt until they next visit a branch will lose it, and the
cost will either be absorbed silently or claimed without evidence. The claim starts with a
photograph taken at the point of sale, geotagged and timestamped, attached to the job it belongs
to.

Fourth, **an advance is a debt until it is settled**. Technician floats and travel advances are
tracked per employee with an ageing, and a second advance cannot be issued while a first is
outstanding beyond its settlement period. This one rule eliminates the informal
rolling-float culture that makes field cash unreconcilable.

Fifth, **tax at source is a gate, not a calculation**. Under BRU-FIN-09 the payment does not
proceed if the deduction is not applied. M52 does not decide the rate — M51 does, from a country
pack that changes every July with the Finance Ordinance — but M52 will not release a payment
that has not been through determination.

---

## 5. Functional Areas & Features

### 5.1 Vendor Invoice Capture & Matching

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-APE-001 | Multi-channel invoice intake | Accept vendor invoices by manual entry, vendor-portal submission (P05), email attachment and scanned document with OCR-assisted field extraction, all producing the same invoice record | **P0** | L1/L5 |
| FR-APE-002 | Duplicate detection | Detect and block a duplicate invoice at the point of entry on a configurable key (vendor, invoice number, date, amount), including near-duplicates, before the record is saved | **P0** | L5 |
| FR-APE-003 | Three-way match | Match every stock and asset invoice line to its purchase order line and goods receipt line on quantity, price, tax and currency, within configured tolerances (BR-FIN-010, BR-SCM-005) | **P0** | L5 |
| FR-APE-004 | Two-way match | Match service and non-PO invoices to an approved contract, service entry or requisition where no goods receipt exists | **P0** | L5 |
| FR-APE-005 | Tolerance configuration | Configure match tolerances by category and value band across quantity, unit price, total value and receipt-date timing, as absolute and percentage limits | **P0** | L5 |
| FR-APE-006 | GRN precondition | Reject approval for payment of any goods invoice with no corresponding approved goods receipt (BRU-FIN-06) | **P0** | L5 |
| FR-APE-007 | Match exception handling | Record every mismatch with a typed reason, block payment on that invoice, route it to the responsible party — buyer, receiver or vendor — and track it to resolution | **P0** | L5 |
| FR-APE-008 | Partial receipt matching | Match an invoice against partial receipts and hold the unmatched balance without blocking the matched portion | P1 | L5 |
| FR-APE-009 | Import invoice matching | Match an import invoice against the import consignment, with landed-cost components reconciled to M44 and duty/VAT elements separated | P1 | L5 |
| FR-APE-010 | Coding and dimensions | Code every invoice line to an account, cost centre, business line, project/job, branch and entity, defaulting from the PO where one exists | **P0** | L5 |

### 5.2 Approval, Payables Ledger & Ageing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-APE-011 | Approval workflow | Route an invoice for approval by value band, expense category, cost centre and entity, enforcing that the approver is not the requisitioner, the receiver or the vendor creator (SOD-01, SOD-02) | **P0** | L5 |
| FR-APE-012 | Payable open-item ledger | Maintain the vendor open-item ledger — invoices, debit notes, credit notes, advances and payments — with a running balance per vendor per entity | **P0** | L1/L5 |
| FR-APE-013 | Payables ageing | Produce payables ageing by vendor, category, branch, entity, currency and age bucket, with an immutable snapshot at each period close | **P0** | L2/L5 |
| FR-APE-014 | Payment terms and due dates | Hold payment terms per vendor and per contract, compute the due date, and evaluate early-settlement discount value against the cost of cash | **P0** | L1/L5 |
| FR-APE-015 | Budget consultation | Consult M54 for budget availability on the coding combination, warn or block per policy, and record every override | P1 | L5 |
| FR-APE-016 | Vendor statement reconciliation | Reconcile a vendor's own statement against the M52 ledger and produce a difference report for dispute resolution | P1 | L5 |
| FR-APE-017 | Vendor dispute | Log a dispute against an invoice, hold payment on the disputed amount only, and track it to a coded outcome | P1 | L5 |

### 5.3 Payment Run & Disbursement Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-APE-018 | Payment proposal | Generate a payment proposal by due date, vendor, entity, bank account and priority, showing discount opportunities and cash requirement | **P0** | L5 |
| FR-APE-019 | Proposal review and edit | Allow an authorised reviewer to include, exclude, part-pay or defer an item on the proposal, recording every change with a reason | **P0** | L5 |
| FR-APE-020 | Payment approval and release | Require approval of the payment run within the authority matrix by a role distinct from the preparer, and release it to M50 as a payment instruction batch | **P0** | L5 |
| FR-APE-021 | Tax deduction at source | Apply the TDS/VDS deduction determined by M51 to every applicable payment line, and block release where determination has not occurred (BRU-FIN-09) | **P0** | L5 |
| FR-APE-022 | Payment method selection | Select the payment method per vendor and value — BEFTN, RTGS, cheque, MFS or cash — respecting policy limits per method | **P0** | L5 |
| FR-APE-023 | Bank-detail change block | Automatically block payment to a vendor whose bank details have changed, until the change is independently verified, and prevent release by the requester of the change | **P0** | L5 |
| FR-APE-024 | Duplicate payment prevention | Prevent a second payment against an already-paid or already-in-flight invoice through any path, including manual payment | **P0** | L5 |
| FR-APE-025 | Payment execution tracking | Track every released instruction through M50 to bank confirmation, and reflect success, failure or return on the vendor's open items | **P0** | L5 |
| FR-APE-026 | Emergency and manual payment | Permit an out-of-cycle payment only with elevated approval, a reason code and inclusion on a standing exception report | P1 | L5 |
| FR-APE-027 | Retention withholding and release | Withhold contractual retention from a sub-contractor payment, track the balance, and release it on the scheduled date or on certified completion | P1 | L5 |

### 5.4 Advances, Prepayments & Consignment Settlement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-APE-028 | Vendor advance | Approve, pay and track a vendor advance or prepayment, and settle it automatically against the vendor's subsequent invoices | **P0** | L1/L5 |
| FR-APE-029 | Advance ageing and recovery | Age outstanding advances, escalate beyond threshold, and block further advances to a vendor with an overdue unsettled advance | P1 | L5 |
| FR-APE-030 | Consignment settlement | Receive consignment-consumption obligations from M15, accumulate them per brand per period, produce the settlement statement, and pay it under the brand agreement's terms | **P0** | L5 |
| FR-APE-031 | GRNI and unrecorded liability accrual | Compute the received-not-invoiced accrual and the estimated unrecorded liability at each period end, and raise both to M19 for posting | **P0** | L5 |
| FR-APE-032 | Debit and credit notes | Raise a debit note to a vendor (short delivery, quality rejection, price correction), receive vendor credit notes, and apply both against open items | **P0** | L1/L5 |

### 5.5 Employee Expense & Advances

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-APE-033 | Mobile expense capture | Capture an expense on the technician or staff app at the point of spend, with a photographed receipt, timestamp, location and the job, work order or cost centre it belongs to | **P0** | L5 |
| FR-APE-034 | Expense policy engine | Validate every claim line against policy — category limits, per-diem rates, mileage rates, receipt requirement thresholds, duplicate detection — and show the violation to the claimant at submission | **P0** | L5 |
| FR-APE-035 | Expense approval and reimbursement | Route a claim to the claimant's approver (never the claimant), then to Finance, and reimburse through the payment run or through payroll as configured | **P0** | L1/L5 |
| FR-APE-036 | Employee advance | Issue, track, age and settle employee cash advances — technician float, travel, emergency purchase — and block a further advance while an earlier one is unsettled beyond its period | **P0** | L5 |
| FR-APE-037 | Per-diem, mileage and field allowance | Compute per-diem, mileage and field allowances from policy rates against verified attendance, trip or route data, without manual calculation | P1 | L5 |
| FR-APE-038 | Corporate and fuel card reconciliation | Import card statements, match transactions to claims or to direct expense coding, and report unmatched card spend by holder | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Duplicate prevention before persistence** | Duplicate detection runs before the invoice record is committed, on an indexed composite key plus a fuzzy-amount/date check. A duplicate is never saved and then flagged; it is refused with the matching document identified |
| T-02 | **Match determinism and explainability** | Every match run stores its inputs (PO line, GRN line, invoice line, tolerance set version) and its outcome, so any exception can be explained months later without re-running the match |
| T-03 | **Payment-level blocking, not record-level rejection** | The block is an attribute of the invoice's payment eligibility. The liability posts to M19 regardless; only the disbursement is stopped |
| T-04 | **Idempotent payment instruction** | Every payment instruction batch carries an idempotency key end-to-end through M50 to the bank file. A retried release must never produce a second disbursement |
| T-05 | **Two-person integrity on the payment path** | Preparer, reviewer and releaser are enforced as distinct users at the service layer and re-validated at release time against the SoD service, not only at UI render time |
| T-06 | **Vendor bank-detail change detection** | A change to a vendor's payment bank details raises an immediate payment block, an alert to Finance and Procurement, and an entry on the standing exception report. The block release requires a verification record from M42 and a different user from the requester |
| T-07 | **Tax determination as a gate** | The payment release path calls M51's determination service and refuses release on any non-determination, including on service unavailability. Failing open is not permitted for a statutory deduction |
| T-08 | **Offline expense capture** | Expense capture works fully offline in the technician app (photograph, amount, category, job link) via an append-only journal, synchronising with server-side conflict resolution (AS-13) |
| T-09 | **Receipt image integrity** | Receipt images are stored in M24 with a content hash recorded on the claim line; a replaced image is detectable, and the same image hash submitted twice is flagged as a duplicate claim |
| T-10 | **Volume envelope** | ~12,000–20,000 vendor invoices per year; **~60,000–100,000 expense claim lines per year** from 200–400 field staff plus branch and head-office staff. Expense volume, not invoice volume, sizes this module |
| T-11 | **Monetary and FX discipline** | All amounts `Monetary` with explicit currency (AS-10); foreign-currency invoices retain the transaction amount, the rate used and the functional-currency amount, with the realised difference computed at payment |
| T-12 | **Event emission via outbox** | Every AP state change emits a domain event through the transactional outbox (AS-08); M19, M50, M51, M54 and M42 consume |
| T-13 | **Multi-entity and operating-unit scoping** | Every AP record carries `company_id` and `operating_unit_id`; cross-entity payment is blocked (AS-03) |
| T-14 | **PII handling** | Employee bank details, NID and vendor bank details are field-level encrypted, masked in every list view, and unmasking is logged (AS-14) |
| T-15 | **Approval performance** | An invoice reaches its first approver within 2 minutes of matching; an expense claim submitted on the app is visible to its approver within 30 seconds of connectivity |
| T-16 | **Retention** | Invoices, receipts, approvals, payment instructions and TDS evidence retained seven years and queryable (Companies Act / NBR; TDS certificate copies five years per the withholding rules) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M52 |
|---|---|---|
| **Finance officer (payables)** | Matches invoices to paper POs and GRNs by hand, chases signatures | Works an exception queue; matched invoices flow to the payment run without touch |
| **Procurement officer** | Is chased for approval on invoices they cannot verify | Sees only the exceptions attributable to their PO, with the variance named |
| **Technician** | Pays for a taxi or an urgent part from their own pocket or an informal float, keeps a receipt in a wallet, claims weeks later | Photographs the receipt at the counter, attaches it to the job, and is reimbursed in the next cycle |
| **Branch manager** | Approves expense vouchers with no policy reference | Approves in the app against a policy that has already validated the claim |
| **Vendor** | Calls to ask where the payment is | Sees invoice and payment status in P05 |
| **Brand partner** | Receives consignment settlements late and reconciled by email | Receives a system-generated settlement statement on the agreed cycle |
| **Finance Manager** | Cannot say what the Company owes until invoices are keyed | Sees payables ageing, GRNI accrual and cash requirement live |
| **CFO** | Discovers a duplicate payment or an overbilling after the fact, if at all | Sees exception rates and duplicate blocks as they happen |
| **Internal audit** | Tests a sample of payments for approval evidence | Tests the control, because the evidence is complete by construction |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Overbilling and duplicate-payment prevention** | Three-way match on every goods invoice; duplicate detection before persistence; single-payment enforcement | In benchmarked payables functions this alone recovers a fraction of a percent of total spend annually — on 1000FiX's parts, import, courier and facilities spend, a material recurring saving |
| **Administrative labour released** | Manual matching, chasing and voucher processing eliminated across finance and 51+ branches | A material share of the **BDT 62 lac** cross-module administrative saving |
| **Field expense control** | 200–400 field staff move from informal floats and paper vouchers to policy-validated, job-attributed claims | Removes an unquantified but structurally significant leakage channel, and makes technician cost visible per job for the first time |
| **Working capital optimisation** | Payment terms tracked and paid on terms — not early, not late — with discount opportunities surfaced | Vendor payment on terms > 95%; cash held rather than given away |
| **Supplier relationship value** | Predictable, on-terms payment and self-service status visibility | Improves commercial terms in negotiation and reduces the supply risk that follows late payment |
| **Job costing completeness** | Technician expenses attributed to jobs, not to an overhead pool | Precondition for M54's true job margin, and therefore for pricing decisions |
| **Tax penalty avoidance** | TDS/VDS applied as a gate on every applicable payment | Avoids payer liability for undeducted tax plus the s.142 surcharge — a direct, quantifiable exposure |
| **Close acceleration** | GRNI and unrecorded-liability accruals computed automatically at period end | Direct contributor to the ≤ 3-day close (KPI-050) |
| **Consignment settlement accuracy** | Obligations to 17+ brands raised at consumption and settled on statement | Protects warranty partnerships worth far more than the module |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Fraud resistance** | SOD-01 and SOD-02 enforced by the system, plus bank-detail change blocking, closes the three most-used payables fraud paths. This is a control the CFO can describe to a bank or an investor |
| **Audit evidence by construction** | Every payment carries its match, its approvals, its tax determination and its bank confirmation. The auditor tests the control rather than sampling documents |
| **Statutory withholding compliance** | Deduction as a gate means the Company cannot accidentally become liable for a vendor's tax |
| **Expense policy fairness** | A field technician and a head-office manager are judged against the same published rules, applied consistently. This matters more for morale than the amounts involved |
| **Vendor trust** | Predictable payment and transparent status change how suppliers price and prioritise 1000FiX |
| **ISO 9001 conformance** | Controlled procure-to-pay with documented approval and evidence retention |
| **Institutional memory** | Payment arrangements live in vendor records, not in a finance officer's relationship with a supplier |

---

## 8. Lifecycle & State Models

### 8.1 Vendor Invoice Lifecycle

```
  INTAKE (portal P05 · email · scan/OCR · manual)
        │
        ▼
  ┌────────────┐  duplicate found  ┌────────────┐
  │  RECEIVED  │──────────────────►│  REFUSED   │ (never persisted as a payable)
  └─────┬──────┘                   └────────────┘
        │ coded + matched
        ▼
  ┌────────────────────────────────────────────────┐
  │                   MATCHED                      │
  └──────┬──────────────────────────────┬──────────┘
         │ within tolerance             │ variance
         ▼                              ▼
  ┌────────────┐                 ┌──────────────────┐
  │  APPROVED  │                 │ EXCEPTION —      │
  │ FOR PAYMENT│                 │ PAYMENT BLOCKED  │
  └─────┬──────┘                 │ (liability still │
        │                        │  posted to M19)  │
        │                        └────────┬─────────┘
        │                                 │ resolved / released
        │◄────────────────────────────────┘
        ▼
  ┌────────────┐   TDS determined   ┌────────────┐
  │  IN        │───────────────────►│  RELEASED  │──► M50 executes
  │  PAYMENT   │                    │            │
  │  RUN       │                    └─────┬──────┘
  └────────────┘                          │ bank confirmation
                                          ▼
                                    ┌────────────┐
                                    │    PAID    │
                                    └─────┬──────┘
                                          │ returned / failed
                                          ▼
                                    ┌────────────┐
                                    │  PAYMENT   │──► back to APPROVED FOR PAYMENT
                                    │  FAILED    │
                                    └────────────┘

  Parallel: DISPUTED (payment held on disputed amount only)
            CREDITED (vendor credit note applied)
            CANCELLED (approved, reason-coded, before payment)
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Received | Invoice captured through any channel and passes duplicate detection | Finance Officer / vendor (P05) / system (OCR) |
| Received | Refused | A duplicate or near-duplicate is identified | System |
| Received | Matched | Coded and matched to PO/GRN, or to contract for services | System |
| Matched | Approved for payment | Within tolerance; approval obtained within the authority matrix and SoD respected | Approver |
| Matched | Exception — payment blocked | Any variance outside tolerance, or no approved GRN for a goods invoice (BRU-FIN-06) | System |
| Exception | Approved for payment | Variance resolved by the responsible party, or released with elevated approval and a reason | Buyer / receiver / Finance Manager |
| Approved for payment | In payment run | Selected on a payment proposal | Finance Officer |
| In payment run | Released | Payment run approved by a distinct role; TDS/VDS determined and applied | Finance Manager / CFO |
| Released | Paid | Bank confirmation received via M50 | M50 |
| Released | Payment failed | Bank rejection or return | M50 |
| Any pre-payment state | Disputed | Dispute logged against the invoice or a line | Finance Officer / Procurement |
| Any pre-payment state | Cancelled | Approved cancellation with a reason before payment | Finance Manager |

### 8.2 Expense Claim Lifecycle

```
  ┌──────────┐  captured on phone at point of spend (offline-capable)
  │ CAPTURED │  receipt photo + amount + category + job/cost centre
  └────┬─────┘
       │ submitted
       ▼
  ┌────────────────┐  policy violation  ┌──────────────────┐
  │ POLICY CHECKED │───────────────────►│ RETURNED TO      │
  └────────┬───────┘                    │ CLAIMANT         │
           │ compliant / justified      └──────────────────┘
           ▼
  ┌──────────────────┐  rejected   ┌───────────┐
  │ PENDING MANAGER  │────────────►│ REJECTED  │
  │ APPROVAL         │             └───────────┘
  └────────┬─────────┘
           │ approved (never by the claimant)
           ▼
  ┌──────────────────┐
  │ PENDING FINANCE  │
  └────────┬─────────┘
           │ verified
           ▼
  ┌──────────────────┐   settled against an outstanding advance
  │    APPROVED      │────────────────────────────────────────┐
  └────────┬─────────┘                                        │
           │ reimbursement due                                ▼
           ▼                                          ┌───────────────┐
  ┌──────────────────┐                                │ ADVANCE       │
  │  IN PAYMENT RUN  │                                │ SETTLED       │
  └────────┬─────────┘   or via payroll (M21)         └───────────────┘
           ▼
  ┌──────────────────┐
  │   REIMBURSED     │
  └──────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Captured | Expense recorded with receipt image, amount, category and job/cost-centre attribution | Employee (P02/P03) |
| Captured | Policy checked | Submitted; policy engine evaluates every line | System |
| Policy checked | Returned to claimant | Violation with no permitted justification | System |
| Policy checked | Pending manager approval | Compliant, or violation justified within permitted bounds | System |
| Pending manager approval | Pending finance | Approved by the claimant's manager — never the claimant | Line manager |
| Pending finance | Approved | Coding, receipt and tax treatment verified | Finance Officer |
| Approved | Advance settled | An outstanding advance exists and covers the claim | System |
| Approved | In payment run | Reimbursement due to the employee | System |
| In payment run | Reimbursed | Payment confirmed by M50, or paid through payroll by M21 | M50 / M21 |

### 8.3 Employee Advance Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Requested | Advance requested with purpose, amount and expected settlement date | Approved or rejected |
| Approved | Authorised within the advance authority matrix | Disbursed |
| Outstanding | Money issued; a receivable from the employee | Settled by claims, returned in cash, or recovered |
| Partially settled | Claims applied for less than the advance | Fully settled or recovered |
| Overdue | Settlement date passed with a balance outstanding — **blocks any further advance to this employee** | Settled or recovered |
| Settled | Fully accounted for by approved claims and/or cash return | — |
| Recovered from payroll | Unsettled balance recovered through M21 with the employee's acknowledgement | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-APE-01 | A vendor invoice for goods cannot be approved for payment without a corresponding approved goods receipt (BRU-FIN-06) | **H** | CFO |
| BRU-APE-02 | A duplicate or near-duplicate vendor invoice is refused at entry and never persisted as a payable | **H** | Finance Manager |
| BRU-APE-03 | A match variance outside tolerance blocks payment on that invoice; the liability is still recorded | **H** | CFO |
| BRU-APE-04 | The user who created a vendor cannot approve that vendor's invoice (SOD-01) | **H** | CFO |
| BRU-APE-05 | No single user may raise a purchase order, receive its goods and approve its invoice; any two of the three are permitted (SOD-02) | **H** | CFO |
| BRU-APE-06 | The preparer, the reviewer and the releaser of a payment run must be three distinct users | **H** | CFO |
| BRU-APE-07 | TDS/VDS is deducted at the rate determined by M51 on every applicable payment; a payment cannot be released without a determination (BRU-FIN-09) | **H** | CFO |
| BRU-APE-08 | Where the payee cannot produce a valid Proof of Submission of Return, or where payment is not made by bank transfer, the elevated withholding rate is applied automatically | **C** | CFO |
| BRU-APE-09 | A change to a vendor's payment bank details blocks all payment to that vendor until independently verified, and the block cannot be released by the requester of the change | **H** | CFO |
| BRU-APE-10 | An invoice already paid or already in flight cannot be paid again through any path, including manual payment | **H** | CFO |
| BRU-APE-11 | Payment cannot be made across legal entities | **H** | CFO |
| BRU-APE-12 | An out-of-cycle emergency payment requires elevated approval, a reason code, and appears on the standing exception report | **A** | CFO |
| BRU-APE-13 | An employee expense claim cannot be approved by the claimant, at any value | **H** | Finance Manager |
| BRU-APE-14 | An expense claim line above the receipt-requirement threshold cannot be approved without an attached receipt image | **H** | Finance Manager |
| BRU-APE-15 | The same receipt image (by content hash) cannot be claimed twice | **H** | Finance Manager |
| BRU-APE-16 | A field expense must be attributed to a job, work order, contract or cost centre; unattributed expense is rejected | **H** | Finance Manager |
| BRU-APE-17 | A further employee advance cannot be issued while an earlier advance is unsettled beyond its settlement period | **H** | Finance Manager |
| BRU-APE-18 | An unsettled employee advance beyond the recovery threshold is recovered through payroll with recorded acknowledgement | **A** | HR Manager / CFO |
| BRU-APE-19 | A further vendor advance cannot be issued while an earlier advance to that vendor is unsettled beyond threshold | **H** | Finance Manager |
| BRU-APE-20 | Retention withheld from a sub-contractor is released only on the scheduled date or on certified completion, never on request alone | **H** | Finance Manager |
| BRU-APE-21 | Consignment settlement obligations from M15 are payable per the brand agreement's terms and are never netted against unrelated balances | **H** | CFO |
| BRU-APE-22 | GRNI and unrecorded-liability accruals are computed at every period end and raised to M19; the period cannot close without them | **H** | CFO |
| BRU-APE-23 | Payables ageing snapshots taken at period close are immutable | **H** | CFO |
| BRU-APE-24 | Per-diem, mileage and allowance rates are policy configuration approved by the CFO and HR Manager; they are never entered per claim | **H** | CFO / HR Manager |
| BRU-APE-25 | A budget breach on an invoice coding combination is reported and, where policy requires, blocked pending approval | **A** | CFO |
| BRU-APE-26 | A payment cannot be released into a period that is hard-closed in M19 | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.ap.invoice` | `fix_ap_invoice` | Vendor invoice header | vendor_id, vendor_invoice_number, entity_id, operating_unit_id, invoice_date, received_date, due_date, currency, fx_rate, subtotal, tax_total, total, balance, state, payment_block_reason, source_channel, po_ids, grn_ids, duplicate_check_hash, gl_entry_ref, tax_determination_ref |
| `fix.ap.invoice.line` | `fix_ap_invoice_line` | Invoice line | invoice_id, description, catalogue_item_id, quantity, uom, unit_price, line_total, tax_code, tax_amount, account_id, cost_center_id, business_line_id, project_id, branch_id, po_line_id, grn_line_id, match_state |
| `fix.ap.match` | `fix_ap_match` | Match result and evidence | invoice_line_id, po_line_id, grn_line_id, matched_qty, qty_variance, price_variance, tax_variance, timing_variance_days, tolerance_set_version, outcome, evaluated_at |
| `fix.ap.match.tolerance` | `fix_ap_match_tolerance` | Tolerance configuration | category, value_band, qty_abs, qty_pct, price_abs, price_pct, total_pct, timing_days, version, effective_from, approved_by |
| `fix.ap.exception` | `fix_ap_exception` | Match or approval exception | invoice_id, invoice_line_id, type, description, responsible_party (buyer/receiver/vendor/finance), raised_at, assigned_to, state, resolution_code, resolved_at, released_by, release_reason |
| `fix.ap.approval` | `fix_ap_approval` | Approval step | invoice_id, step, approver_role, approver_id, decision, decided_at, comment, sod_check_result, authority_band |
| `fix.ap.open.item` | `fix_ap_open_item` | Vendor ledger line | vendor_id, entity_id, document_type, document_id, document_date, due_date, original_amount, balance, currency, age_days, age_bucket, state, block_flag, dispute_id |
| `fix.ap.ageing.snapshot` | `fix_ap_ageing_snapshot` | Immutable period ageing | period_id, entity_id, vendor_id, category, branch_id, buckets, total, taken_at |
| `fix.ap.payment.run` | `fix_ap_payment_run` | A payment cycle | entity_id, run_date, bank_account_id, method, proposal_total, final_total, currency, state, prepared_by, reviewed_by, released_by, instruction_batch_id (M50), idempotency_key |
| `fix.ap.payment.line` | `fix_ap_payment_line` | One payment on a run | run_id, vendor_id, invoice_ids, gross_amount, tds_amount, vds_amount, net_amount, discount_taken, method, state, bank_confirmation_ref, failure_reason |
| `fix.ap.payment.block` | `fix_ap_payment_block` | Block on a vendor or invoice | scope (vendor/invoice), target_id, reason (bank_change/dispute/exception/compliance), raised_at, raised_by, state, released_by, release_reason, verification_ref (M42) |
| `fix.ap.advance` | `fix_ap_advance` | Vendor advance / prepayment | vendor_id, entity_id, amount, currency, purpose, po_ref, approved_by, paid_at, settled_amount, balance, expected_settlement_date, state, age_days |
| `fix.ap.debit.note` | `fix_ap_debit_note` | Debit note to a vendor | vendor_id, original_invoice_id, reason_code, amount, tax_amount, raised_by, approved_by, state, applied_to_invoice_id |
| `fix.ap.vendor.credit` | `fix_ap_vendor_credit` | Vendor credit note received | vendor_id, vendor_reference, original_invoice_id, amount, tax_amount, received_at, applied_to_invoice_id, state |
| `fix.ap.retention` | `fix_ap_retention` | Retention withheld | vendor_id, contract_ref, invoice_id, withheld_amount, release_due_date, release_condition, released_amount, released_at, state |
| `fix.ap.consignment.settlement` | `fix_ap_consignment_settlement` | Brand settlement obligation | brand_party_id, period, consumption_event_ids (M15), quantity, value, currency, statement_doc_id, agreed_at, invoice_id, paid_at, state |
| `fix.ap.grni.accrual` | `fix_ap_grni_accrual` | Received not invoiced | period_id, entity_id, po_line_id, grn_line_id, quantity, unit_cost, accrual_value, reversed_at, gl_entry_ref |
| `fix.ap.vendor.statement.recon` | `fix_ap_vendor_statement_recon` | Vendor statement match | vendor_id, statement_date, statement_balance, ledger_balance, difference, reconciling_items_json, state, resolved_at |
| `fix.ap.dispute` | `fix_ap_dispute` | Dispute with a vendor | invoice_id, disputed_amount, reason_code, raised_by, assigned_to, state, outcome_code, resolved_at |
| `fix.expense.policy` | `fix_expense_policy` | Expense rules | category, grade_scope, limit_amount, receipt_threshold, per_diem_rate, mileage_rate, requires_justification, effective_from, approved_by |
| `fix.expense.claim` | `fix_expense_claim` | Claim header | employee_id, entity_id, branch_id, period, total_amount, currency, state, submitted_at, manager_approved_by, finance_approved_by, advance_id, reimbursement_method, payment_line_id |
| `fix.expense.claim.line` | `fix_expense_claim_line` | Claim line | claim_id, expense_date, category, amount, currency, merchant, receipt_doc_id, receipt_hash, geo_lat, geo_lng, job_id, work_order_id, contract_id, cost_center_id, policy_result, violation_code, justification, tax_treatment |
| `fix.employee.advance` | `fix_employee_advance` | Cash advance to staff | employee_id, type (float/travel/emergency), amount, purpose, approved_by, issued_at, settlement_due_date, settled_amount, balance, state, age_days, recovered_via_payroll_ref |
| `fix.expense.card.transaction` | `fix_expense_card_transaction` | Corporate/fuel card line | card_id, holder_employee_id, transaction_date, merchant, amount, statement_ref, matched_claim_line_id, state |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.party` (vendor, brand, courier, sub-contractor) | M33 | Read via API |
| `fix.supplier.agreement`, `fix.supplier.scorecard`, `fix.supplier.profile` | M42 | Read; bank-detail verification record gates the payment block release |
| `fix.purchase.order`, `fix.purchase.order.line` | M16 | Read for matching; never written |
| `fix.goods.receipt`, `fix.goods.receipt.line` | M16 | Read for matching; never written |
| `fix.import.consignment`, `fix.landed.cost` | M44 | Read for import invoice matching |
| `fix.consignment.balance` events | M15 | Consumed to create the settlement obligation |
| `fix.tax.determination`, `fix.tax.rule`, `fix.tax.rule`, `fix.party.tax.profile` | M51 | Call and store the reference |
| `fix.payment.instruction`, `fix.bank.account` | M50 | Instruct and track |
| `fix.gl.account`, `fix.fiscal.period` | M19 | Read for period state and control-account balance |
| `fix.employee`, `fix.job.profile`, `fix.employee.assignment`, `fix.attendance.record` | M21 / M55 / M58 | Read for entitlement, approver and allowance basis |
| `fix.payroll.run` | M56 | Read/instruct for payroll-routed reimbursement and advance recovery |
| `fix.budget.line` | M54 | Read for budget consultation |
| `fix.service.order`, `fix.work.order` | M01 / M02 | Read for expense job attribution |
| `fix.vehicle`, `fix.vehicle.trip` | M46 | Read for mileage and fuel validation |
| `fix.document` | M24 | Store invoices, receipts and evidence |
| `fix.sod.rule` | M29 / M60 | Evaluate at every approval and release |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-APE-01 | An invoice arrives through any channel | Extract fields (OCR where scanned), run duplicate detection, code from the PO where one exists, and run the match | Route to manual coding queue with the extraction confidence shown |
| AUT-APE-02 | Match completes within tolerance | Route for approval by the authority matrix, checking SoD before presenting the task | Route to the Finance Manager with the SoD conflict named |
| AUT-APE-03 | Match variance outside tolerance | Raise a typed exception, block payment on the invoice, assign to the responsible party, and start the resolution clock | Exception remains open and appears on the daily exception report |
| AUT-APE-04 | A goods invoice arrives with no approved GRN | Block payment, notify the receiver and the buyer, and hold pending receipt confirmation (BRU-FIN-06) | Hard block; no override path at any authority |
| AUT-APE-05 | Payment proposal scheduled | Assemble the proposal by due date, priority and discount opportunity; show the cash requirement to M50 | Proposal generated empty with an alert |
| AUT-APE-06 | Payment run released | Call M51 for TDS/VDS determination per line, apply the deduction, and pass the batch to M50 with an idempotency key | Refuse release; a payment never proceeds without determination |
| AUT-APE-07 | Vendor bank details change in M33/M42 | Block all payment to that vendor immediately, alert Finance and Procurement, and require a verification record before release | Hard block; unconditional |
| AUT-APE-08 | M50 confirms a payment | Close the invoice open items, record the bank reference, and notify the vendor through P05 | Retain in released state and report on the unconfirmed-payment list |
| AUT-APE-09 | M50 reports a payment failure or return | Restore the invoices to approved-for-payment, alert Finance, and record the failure reason on the vendor record | High-priority exception |
| AUT-APE-10 | M15 raises a consignment consumption | Accumulate the obligation against the brand's settlement period | Queue and retry; alert on repeated failure |
| AUT-APE-11 | Brand settlement period closes | Generate the settlement statement, publish it to P08, and create the payable on agreement | Escalate to the Warehouse Manager and Finance Manager |
| AUT-APE-12 | Expense claim submitted | Evaluate every line against policy, show violations to the claimant immediately, and route compliant lines to the approver | Claim held with the policy service unavailable flagged; never auto-approved |
| AUT-APE-13 | Expense claim approved by Finance | Settle against an outstanding advance where one exists, otherwise queue for the reimbursement payment run or for payroll | Claim remains approved and appears on the pending-reimbursement list |
| AUT-APE-14 | Employee advance passes its settlement due date | Mark overdue, block further advances to that employee, and escalate to the line manager and Finance | Escalation is unconditional |
| AUT-APE-15 | Employee advance exceeds the recovery threshold | Raise a payroll recovery instruction to M21 with the employee's acknowledgement request | Escalate to HR Manager and CFO |
| AUT-APE-16 | Period end | Compute the GRNI accrual and the estimated unrecorded liability, and raise both to M19 | Block the close task and report |
| AUT-APE-17 | Period end | Take the immutable payables ageing snapshot | Block the close task |
| AUT-APE-18 | Vendor statement uploaded or received | Reconcile against the M52 ledger and produce the difference report | Report generated with unmatched items listed |
| AUT-APE-19 | Daily | Publish the payment-block register, the exception ageing, the overdue-advance list and the duplicate-block log | Report with a data-availability warning |
| AUT-APE-20 | Corporate or fuel card statement imported | Match transactions to claims or to direct coding, and report unmatched spend by cardholder | Unmatched lines held and escalated to the cardholder's manager |

---

## 12. Interfaces

### 12.1 Upstream — M52 Consumes

| Source | What | Mechanism |
|---|---|---|
| M16 Procurement | Purchase orders, order lines, terms and buyer identity | REST |
| M15 Inventory | Goods receipts, receipt lines, inspection outcome; consignment consumption obligations | REST + events |
| M44 Import & Landed Cost | Import consignment, duty and VAT components, landed-cost breakdown | REST + events |
| M42 Supplier Relationship | Vendor agreement terms, payment terms, bank-detail verification records, quality events | REST |
| M33 Party Master | Vendor identity, BIN, TIN, bank details of record | REST |
| M51 Tax & Regulatory | TDS/VDS determination, PSR status, rate tables, deposit deadlines | REST |
| M50 Treasury & Cash | Payment confirmation, failure and return; available balance and cash constraint | Events + REST |
| M19 General Ledger | Period state, payable control-account balance, posting confirmation | REST |
| M21 HR & Payroll | Employee identity, grade, approver, attendance, payroll run for reimbursement and recovery | REST + commands |
| M54 Costing & FP&A | Budget availability on a coding combination | REST |
| M01 / M31 / M02 | Job and work-order references for expense attribution | REST |
| M46 Fleet & Vehicle | Trip and fuel data for mileage validation | REST |
| M29 Identity | SoD evaluation at every approval and release | REST |

### 12.2 Downstream — M52 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Vendor invoice approved, payment made, advance issued and settled, expense approved, GRNI and unrecorded-liability accrual, TDS liability | Events |
| M50 Treasury & Cash | Payment instruction batches, forecast cash requirement by due date | Commands + events |
| M51 Tax & Regulatory | TDS/VDS deducted per payment, with payee, section, rate and base — the input to challans and certificates | Events |
| M16 Procurement | Match exceptions attributable to a PO; invoice-to-PO closure | Events |
| M42 Supplier Relationship | Payment performance, dispute and quality events feeding the vendor scorecard | Events |
| M15 Inventory | Consignment settlement status per brand | Events |
| M49 Fixed Assets | Approved invoices flagged as capital, for capitalisation | Events |
| M54 Costing & FP&A | Actual cost by cost centre, business line, job and project, including field expense | Warehouse extract + events |
| M21 HR & Payroll | Advance recovery instructions; reimbursements routed through payroll | Commands |
| M25 BI / M62 Data Platform | Payables, expense, exception and payment-performance facts | Warehouse extract |
| P05 Vendor & Supplier Portal | Invoice submission, match status, payment status, expected date | REST |
| P08 Brand Partner Portal | Consignment settlement statements | REST |
| P02 Technician App | Expense capture, claim status, advance balance | REST |
| P03 Admin Portal | Full payables and expense workspace | Native |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `ap.invoice_received` | vendor, invoice reference, amount, channel, entity | M16, M42, M19 |
| `ap.invoice_matched` | invoice, PO/GRN references, variances, outcome | M16, M15, M42 |
| `ap.exception_raised` | invoice, type, variance, responsible party | M16, M15, M42, M23 |
| `ap.invoice_approved` | invoice, approvers, coding, amount, dimensions | M19, M54, M49 |
| `ap.payment_blocked` | scope, target, reason, raiser | M42, M23, M50 |
| `ap.payment_released` | run, vendor, invoices, gross, TDS, VDS, net, method | M50, M51, M19 |
| `ap.payment_confirmed` | run, line, bank reference, value date | M19, M42, M50 |
| `ap.payment_failed` | run, line, failure reason | M19, M42, M50 |
| `ap.tds_deducted` | payee, section, rate, base, deducted amount, payment reference | M51, M19 |
| `ap.advance_issued` / `ap.advance_settled` | vendor or employee, amount, purpose, balance | M19, M50, M21 |
| `ap.advance_overdue` | employee or vendor, amount, age | M21, M19, M23 |
| `ap.consignment_settlement_raised` | brand, period, quantity, value | M15, M19, P08 |
| `ap.grni_accrued` | period, entity, value, PO/GRN basis | M19, M54 |
| `ap.expense_approved` | employee, claim, lines, job attribution, amount | M19, M54, M21 |
| `ap.expense_policy_violation` | employee, claim line, violation code, amount | M21, M23, M54 |
| `ap.ageing_snapshot_taken` | period, entity, buckets, totals | M19, M50, M54 |
| `ap.duplicate_blocked` | vendor, invoice reference, matching document | M23, M42 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-APE-01 | Vendor email inboxes (invoice submission) | Inbound | Automated capture of emailed invoices into the intake queue |
| INT-APE-02 | OCR / document-extraction service | Bidirectional | Field extraction from scanned and PDF invoices |
| INT-APE-03 | Corporate card and fuel card issuers | Inbound | Statement import for reconciliation |
| INT-APE-04 | NBR tax rate and SRO reference (via M51) | Inbound | Current TDS/VDS rates and PSR verification |
| INT-APE-05 | Banking partners (via M50) | Outbound | BEFTN and RTGS payment files; confirmations inbound |
| INT-APE-06 | Brand partner settlement portals | Bidirectional | Consignment settlement statements and confirmations |
| INT-APE-07 | Legacy payables records and voucher files | Inbound, one-time | Open payable migration; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/ap/invoices` | POST · GET | Submit and retrieve vendor invoices | P05, P03, M16 |
| `/api/v1/ap/invoices/{id}/match` | POST | Run or re-run the match | P03 |
| `/api/v1/ap/invoices/{id}/approve` | POST | Approve for payment | P03 |
| `/api/v1/ap/exceptions` | GET · PATCH | Exception worklist and resolution | P03, P05, M16 |
| `/api/v1/ap/open-items` | GET | Vendor open-item ledger | P05, P03 |
| `/api/v1/ap/ageing` | GET | Payables ageing, live or snapshot | P03, P06, M50, M54 |
| `/api/v1/ap/payment-runs` | POST | Create a payment proposal | P03 |
| `/api/v1/ap/payment-runs/{id}/review` | POST | Review and amend a proposal | P03 |
| `/api/v1/ap/payment-runs/{id}/release` | POST | Approve and release to M50 (idempotent) | P03 |
| `/api/v1/ap/payment-blocks` | POST · DELETE | Raise and release a payment block | P03 |
| `/api/v1/ap/advances` | POST · GET | Vendor and employee advances | P03, P02 |
| `/api/v1/ap/consignment-settlements/{brand}` | GET | Brand settlement statement and status | P08, P03 |
| `/api/v1/expense/claims` | POST · GET | Submit and track expense claims (offline-capable) | P02, P03 |
| `/api/v1/expense/claims/{id}/approve` | POST | Manager and finance approval | P02, P03 |
| `/api/v1/expense/policy/evaluate` | POST | Pre-submission policy check | P02, P03 |
| `/api/v1/expense/advances/{employee}` | GET | Employee advance balance and ageing | P02, P03, M21 |
| `/api/v1/ap/vendor-statement-recon` | POST | Upload and reconcile a vendor statement | P03, P05 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves payment runs and emergency payments above threshold |
| R26 Finance Manager | C R U A | All entities; approves invoices and payment runs within authority, releases blocks |
| R27 Finance Officer | C R U | Assigned scope; captures invoices, resolves exceptions, prepares payment runs — **cannot release** |
| R19 Procurement Officer | R U | Own POs; resolves buyer-attributable exceptions — **no payment rights, cannot approve an invoice for a vendor they created** |
| R18 Branch Store Keeper / R20 Warehouse Operative | R | Receipt-attributable exceptions only |
| R06 Branch Manager | R U A | Own branch; approves branch expense claims and branch-coded invoices within authority |
| R05 Operations Director | R A | All branches; approves above branch authority |
| R30 HR Manager | R A | Employee advances, payroll recovery and allowance policy |
| R31 HR Officer | R | Employee advance and claim status |
| R10 / R11 / R12 Technician | C R | Own expense claims and own advance balance only (P02) |
| R08 / R09 / R15 / R16 and all staff roles | C R | Own expense claims only |
| R32 Quality Manager / ISO Coordinator | R | Exception, block, duplicate and policy-violation registers |
| R33 IT / System Administrator | R | Configuration and technical support; **no invoice approval, no payment release** |
| R38 Vendor | C R | Own invoices, match status and payment status only (P05) |
| R38 Brand Partner | R | Own consignment settlement statements only (P08) |
| R01 Chief Executive Officer / R02 Chief Technology Officer / R04 Chief Commercial Officer | R | Reporting only |

**Field-level restrictions.** Vendor bank details, employee bank details and NID are field-level
encrypted, masked in every list view, and visible unmasked only to R03, R26 and R27, with every
unmasking logged (AS-14). Unit costs and vendor prices follow the `05-04` §5 restriction.
Technicians see only their own claims and advances.

**Segregation of duties.**
- **SOD-01 enforced here:** the user who created a vendor can never approve that vendor's invoice — hard block.
- **SOD-02 enforced here:** no single user may raise a PO, receive its goods and approve its invoice; any two are permitted.
- **Payment three-person rule:** preparer, reviewer and releaser of a payment run must be three distinct users.
- A user may not both request a vendor bank-detail change and release the resulting payment block.
- A user may not both approve an expense claim and be its claimant, at any value.
- R19 Procurement Officer has no payment rights whatsoever — the person who commits spend never releases money.
- R33 IT / System Administrator has configuration access with no approval or release rights.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Payables ageing** | CFO, Finance Manager, Treasury | Daily | Balance by bucket, vendor, category, branch, entity and currency |
| **Three-way match exception report** | Finance Manager, Procurement, CFO | Daily | Open exceptions by type, value, age and responsible party — against the < 5% rate target |
| **Payment block register** | CFO, Finance Manager, Internal Audit | Daily | Every block with reason, raiser, age and release history — bank-detail blocks highlighted |
| **Payment run pack** | CFO, Finance Manager, Treasury | Per run | Proposal, changes made and by whom, TDS/VDS applied, cash requirement, approvals |
| **Vendor payment on terms** | CFO, Procurement, CCO | Monthly | % paid within terms, average days beyond terms, by vendor and category — against the > 95% target |
| **Discount opportunity report** | CFO, Finance Manager | Weekly | Early-settlement discounts available, taken and lost, with value |
| **Duplicate block log** | CFO, Internal Audit | Monthly | Every duplicate refused, with the matching document — evidence the control is working |
| **GRNI and unrecorded liability** | CFO, Finance Manager, auditor | Monthly | Received-not-invoiced by PO age and value; estimated unrecorded liability basis |
| **Vendor statement reconciliation** | Finance Manager, Procurement | Monthly | Differences by vendor with reconciling items |
| **Expense claim analysis** | CFO, HR Manager, Branch Managers | Monthly | Claim volume and value by category, branch, grade and job; cycle time from capture to reimbursement |
| **Expense policy violation register** | HR Manager, CFO, Quality Manager | Monthly | Violations by type, claimant and branch; justified vs rejected |
| **Employee advance ageing** | Finance Manager, HR Manager, Branch Managers | Weekly | Outstanding advances by employee and age; overdue and blocked list |
| **Field cost per job** | Operations Director, CFO, M54 | Monthly | Technician expense attributed to jobs — the input to true job margin |
| **Consignment settlement status** | CFO, Warehouse Manager, brand partners (P08) | Monthly | Obligation raised, statement agreed, paid, outstanding by brand |
| **TDS/VDS deduction summary** | CFO, Tax (M51) | Monthly | Deductions by section, payee category and rate — the basis for challans and certificates |
| **Emergency payment register** | CFO, Internal Audit | Monthly | Every out-of-cycle payment with approver and reason |
| **Retention register** | CFO, Finance Manager | Monthly | Retention held, release due, released, by sub-contractor |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-049** | Three-way match exception rate *(instrumented here; see register note)* | n/a | < 8% | **< 5%** |
| — | Vendor payment on terms | unmeasured | 90% | **> 95%** |
| — | Duplicate payments | unknown | **Zero** | **Zero** |
| — | Invoices processed without manual intervention (touchless) | 0% | 55% | **75%** |
| — | Invoice cycle time — receipt to approval | unmeasured | < 5 days | **< 2 days** |
| — | Match exception resolution cycle time | n/a | < 5 days | **< 3 days** |
| — | Expense claim cycle time — capture to reimbursement | weeks | < 10 days | **< 5 days** |
| — | Expense claims submitted from the mobile app at point of spend | 0% | 70% | **90%** |
| — | Expense claims with a compliant receipt attached | unmeasured | 95% | **99%** |
| — | Employee advances overdue beyond settlement period | untracked | < 10% | **< 2%** |
| — | Field expense attributed to a job or work order | ~0% | 85% | **95%** |
| — | GRNI accrual accuracy (subsequent invoice within ±5%) | n/a | 85% | **95%** |
| — | Early-settlement discounts captured where available | unknown | 60% | **85%** |
| — | Consignment settlements agreed with the brand within the cycle | n/a | 90% | **100%** |
| — | Payments released without a tax determination | n/a | **Zero** | **Zero** |
| — | Payment blocks open beyond 5 days | n/a | < 5% | **< 1%** |

> **Register note.** **KPI-049** (three-way match exception rate) is allocated to **M16** in
> `06-02` §2.5. The match is executed in M52 and the exception is resolved jointly, so the KPI is
> **instrumented in M52 and reported against both modules**; the register requires a joint-owner
> entry — recorded as audit action **A-01**. The fifteen unnumbered metrics are new to this
> specification and require allocation in `06-02` — audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` (vendor bills, payment registration, batch payments), `hr_expense` (claims, approval, attachment) | 28% |
| L2 | OCA `account-payment` (batch payment mechanics, payment order), `account-invoicing`, `hr-expense` (policy and analytic extensions), `purchase-workflow` | 22% |
| L3 | Free OCR/document-extraction bridges | 4% |
| L5 | `cd_ap_ext`, `cd_payment_run`, `cd_expense_claim` | 46% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 3 identifiers below are claimed by another module: **CD-164** also claimed by M46, M66; **CD-165** also claimed by M46, M67; **CD-166** also claimed by M46, M67. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-164** | `cd_ap_ext` — three-way and two-way matching engine, tolerance sets, typed exceptions with payment-level blocking, duplicate detection before persistence, GRNI accrual, vendor statement reconciliation, retention, consignment settlement | Odoo module + service | **8 PW** |
| **CD-165** | `cd_payment_run` — proposal, review, three-person release, TDS/VDS gate, method selection, bank-detail change block, duplicate-payment prevention, M50 instruction batching with idempotency | Odoo module | **6 PW** |
| **CD-166** | `cd_expense_claim` — mobile offline capture with receipt hashing and geotagging, policy rules engine, job attribution, per-diem and mileage computation, employee advance lifecycle, card reconciliation | Odoo module + technician-app surface | **5 PW** |

> **CD register position.** M52 is new in v2.1 and had no allocation in `02-05` §5.2. Three new
> IDs, **CD-164…166**, are claimed from the Category G block defined in `M19` §16.2. **All CD IDs
> remain provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M52 is scheduled in **W3** (P1) but declares a dependency on 2 module(s) that land later: **M21** (W5); **M51** (W4). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M52 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M52 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M19 General Ledger | Every payable and expense terminates in a journal entry; the control account and period model must exist |
| M33 Party Master | A payment to an ungoverned vendor record is the definition of the fraud this module prevents |
| M29 Identity | The SoD service is load-bearing: SOD-01, SOD-02 and the payment three-person rule are enforced through it |
| M16 Procurement | Purchase orders are one half of the three-way match. **M16 is W3 alongside M52** — until POs exist, two-way matching against approved requisitions operates and is reported as an exception class |
| M15 Inventory (W2) | Goods receipts are the other half of the match, and the source of consignment settlement obligations |
| M50 Treasury & Cash | Payment execution and confirmation; must go live with M52 |
| M51 Tax & Regulatory | TDS/VDS determination. **M51 is W4 while M52 is W3** — for the W3 window a provisional rate table maintained by the CFO's tax consultant operates as an M51 stub, with the same hard-gate behaviour. Recorded in §18 Q-02 |
| M21 HR & Payroll | Employee master, approver hierarchy and payroll-routed reimbursement. **M21 is W5** — until then, employee master is loaded from HR records into M33 and reimbursement runs through the payment run only |
| M42 Supplier Relationship | Bank-detail verification records that gate block release. **M42 is W4** — until then verification is a recorded manual call-back attested by two finance users |

**Delivers into:** M50 (payment instructions and cash requirement), M51 (TDS/VDS deducted),
M19 (payables postings), M54 (actual cost by job and cost centre), M15 (consignment settlement
closure). **M19, M20, M52 and M50 must go live together.**

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open vendor invoices at cutover | Estimated 800–2,000 open items | `fix.ap.invoice`, `fix.ap.open.item` | W3 cutover |
| Open vendor advances and prepayments | Current only | `fix.ap.advance` | W3 cutover |
| Vendor payment terms and bank details | All active vendors | Via M33 / M42 masters | W3 minus 1 month |
| Retention held on sub-contractors | Current only | `fix.ap.retention` | W3 cutover |
| Outstanding employee advances and floats | 200–400 field staff plus branch floats | `fix.employee.advance` | W3 cutover |
| Unreimbursed expense claims | Current only | `fix.expense.claim` | W3 cutover |
| Open consignment settlement obligations | 17+ brands | `fix.ap.consignment.settlement` | W3, brand-confirmed |
| Expense policy rates | Current policy | `fix.expense.policy` | W3 minus 1 month |
| Historical invoices | 2 years where recoverable | Warehouse (M62), **not** the operational ledger | W3–W4, best-effort |

> **Migration position.** Open payables migrate at **document level with their PO and GRN
> references where they exist**; a migrated payable balance without its underlying invoices
> cannot be matched, disputed or reconciled to a vendor statement. **Every vendor bank detail is
> re-verified before the first payment run** — migration is the single most attractive moment for
> a payment-redirection fraud, and a migrated bank account is treated as unverified until an
> independent call-back is recorded. **Outstanding employee advances are confirmed in writing by
> each employee** before migration; an advance the employee does not acknowledge is escalated to
> HR rather than loaded silently.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A goods invoice cannot be approved for payment without an approved GRN, through any path | Negative test on UI, API and import (BRU-FIN-06) |
| AC-02 | Three-way match runs on 100% of goods invoices, with the exception rate measurable from day one | Production measurement over one month (KPI-049) |
| AC-03 | A match exception blocks payment while the liability still posts to M19 | Scripted scenario with the GL entry verified |
| AC-04 | A duplicate or near-duplicate invoice is refused at entry and never persisted | Negative test across exact, near and cross-channel duplicates |
| AC-05 | The user who created a vendor cannot approve that vendor's invoice | SoD negative test (SOD-01) |
| AC-06 | No single user can raise a PO, receive its goods and approve its invoice | SoD negative test (SOD-02) |
| AC-07 | Preparer, reviewer and releaser of a payment run are enforced as three distinct users at release time | SoD negative test |
| AC-08 | A payment cannot be released without a TDS/VDS determination, including when the determination service is unavailable | Negative test with the service disabled |
| AC-09 | A vendor bank-detail change blocks payment immediately, and the block cannot be released by the requester | Scripted scenario |
| AC-10 | An invoice already paid or in flight cannot be paid again through any path | Negative test including manual payment and replay |
| AC-11 | A released payment batch replayed after a network failure produces exactly one disbursement | Idempotency test end-to-end through M50 |
| AC-12 | Vendor payment on terms exceeds 95% at Wave 8 | Three consecutive monthly measurements |
| AC-13 | Expense capture works fully offline for a complete shift and synchronises without loss or duplication | Offline test with 20 technicians over five shifts |
| AC-14 | The same receipt image cannot be claimed twice | Negative test on content hash |
| AC-15 | An expense claim cannot be approved by its claimant at any value | SoD negative test |
| AC-16 | A field expense cannot be submitted without attribution to a job, work order, contract or cost centre | Negative test |
| AC-17 | A further advance cannot be issued to an employee with an overdue unsettled advance | Negative test |
| AC-18 | Policy violations are shown to the claimant at submission, before any approver's time is spent | UX test and cycle-time measurement |
| AC-19 | GRNI accrual is computed at every period end and blocks the close if not raised | Scripted close scenario |
| AC-20 | Consignment settlement obligations from M15 are accumulated per brand and reconcile to M15's consumption records | Three consecutive monthly reconciliations with at least three brands |
| AC-21 | Payables ageing snapshots are immutable and reproduce exactly on re-query | Assertion test after subsequent transactions |
| AC-22 | Open payables migrate at document level and reconcile exactly to the M19 payable control account | CFO-signed reconciliation |
| AC-23 | Every migrated vendor bank detail is independently re-verified before the first payment run | Verification register signed by two finance users per vendor |
| AC-24 | Vendor bank details, employee bank details and NID are encrypted, masked, and every unmasking is logged | Security review and log inspection |
| AC-25 | All technician-facing expense screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-26 | CFO, Finance Manager and a nominated Branch Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 26 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What are the three-way match tolerances by category and value band, and who approves a change to them? | CFO / Procurement | W3 design |
| Q-02 | **M51 is Wave 4 but M52 is Wave 3.** Is a CFO-maintained provisional TDS/VDS rate table acceptable as an M51 stub for the W3 window, with the same hard-gate behaviour? | CFO / CTO | **W3 minus 3 months — blocking** |
| Q-03 | What is the invoice approval authority matrix by value band, category and entity? | CFO | W3 build |
| Q-04 | What is the payment-run approval authority matrix, and who are the designated releasers? | CFO / CEO | W3 build |
| Q-05 | What is the expense policy — category limits by grade, per-diem rates, mileage rate, receipt threshold — and who approves changes to it? | CFO / HR Manager | W3 design |
| Q-06 | Are technician floats being replaced by expense claims, retained alongside them, or converted to corporate/fuel cards? The advance model differs materially between these | CFO / Operations Director | W3 design |
| Q-07 | Which brands' consignment agreements specify settlement terms, in what currency, and on what cycle? | Warehouse Manager / CCO | W3 minus 2 months |
| Q-08 | Is reimbursement routed through the payment run, through payroll, or by employee election? M21 is W5, which constrains the answer for W3 | CFO / HR Manager | W3 design |
| Q-09 | Do we operate corporate or fuel cards today, and with which issuers? FR-APE-038 is P2 and can be deferred if not | CFO / Operations Director | W4 |
| Q-10 | Is a budget breach on an invoice a warning or a hard block, and does the answer differ by category? M54 is W6, so a W3 answer is a placeholder | CFO | W3 design, revisit W6 |
| Q-11 | What is the emergency/out-of-cycle payment policy — permitted circumstances, authority and frequency limit? | CFO | W3 build |
| Q-12 | Which vendors submit invoices through P05 from go-live, and which continue by email or paper? Touchless-processing targets depend on it | Procurement / CFO | W3 minus 2 months |
| Q-13 | What is the manual call-back procedure for vendor bank-detail verification before M42 lands in W4, and who attests it? | CFO / Procurement | **W3 minus 1 month — control-critical** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition), §4 (money flow), §5 (boundary map), §8 (KPIs),
§9 (delivery sequence) · `M19_Financial_Accounting_and_General_Ledger.md` (posting engine,
control accounts, period model, Category G CD block) · `M50_Treasury_Cash_and_Banking.md`
(payment execution, bank confirmation) ·
`M51_Tax_and_Regulatory_Compliance_Bangladesh.md` (TDS/VDS determination, challans, certificates) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` (settlements, as distinct from trade
payables) · `M49_Fixed_Assets_and_Capital_Investment.md` (capital invoices) ·
`M54_Cost_Accounting_Budgeting_and_FPA.md` (budget consultation, actual cost by job) ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md` §12.2
(consignment settlement obligations), FR-INV-013 ·
`03_Modules/E_Supply_Chain_and_Inventory/M16_Procurement_and_Strategic_Sourcing.md` ·
`03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md` ·
`03_Modules/E_Supply_Chain_and_Inventory/M44_Import_Trade_Compliance_and_Landed_Cost.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §6 SOD-01, SOD-02 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` BRU-FIN-09 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.5 (KPI-049),
§2.7, BO-06

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-010, BR-SCM-005,
BRU-FIN-06, §Process 4 (three-way match to AP payment queue), UC-018, §Month-End Close Day 4 ·
`1000FiX_Services_Company_Profile.md` §Service Infrastructure (51+ branches, nationwide field
force)

**External benchmark**
SAP S/4HANA FI-AP and Logistics Invoice Verification (MM-IV) — tolerance keys, blocked-for-payment
with named block reasons, the F110 automatic payment programme's proposal → edit → run stages ·
SAP Ariba and SAP Concur patterns — supplier-network invoice submission with status visibility;
mobile receipt capture with a policy engine ·
[Oracle Fusion Cloud Payables](https://www.oracle.com/erp/financial-management/) — invoice
imaging and OCR intake, invoice holds and releases, prepayment application, and withholding tax
computed at payment rather than at invoice ·
[Microsoft Dynamics 365 Finance — Accounts Payable and Expense Management](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
invoice matching policies, expense report policies with per-diem and mileage rules, cash-advance
workflow ·
[TDS and VDS rates Bangladesh FY 2025–26](https://rakibhassan.eu/tds-vds-rates-bangladesh-2025-26/) —
s.89 contractor/supplier and s.90 service rates split by individual and non-individual payee,
VDS service codes under SRO 182-Ain/2025/310-Mushak, deposit deadlines, Mushak 6.6 certificate
issuance, and the s.142 50% surcharge where the payee has no PSR or payment is not by bank
transfer — the reason TDS is a payment gate rather than a calculation ·
[ICAB — changes in VDS 2025-26](https://www.icab.org.bd/icabadmin/uploads/ckeditor/5679Changes_in_VDS_2025-26.pdf) ·
OCA `account-payment` — payment orders and batch payment mechanics · Odoo 19 `hr_expense`

---

*Module M52 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
