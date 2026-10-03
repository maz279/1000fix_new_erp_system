---
id: FIX-ERP2-M50
module_id: M50
module_code: TRE
module_name: Treasury, Cash & Banking
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

# M50 — Treasury, Cash & Banking
### Category G · Code `TRE` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M50 |
| **Module code** | `TRE` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M19 monolith after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (bank and cash journals, reconciliation) · L2 OCA `bank-statement-import`, `account-reconcile`, `account-payment-order`, `currency` · L5 custom cash consolidation, settlement reconciliation, forecasting and trade finance |
| **Custom modules** | `cd_cash_position`, `cd_bank_account_mgmt`, `cd_bank_reconciliation`, `cd_branch_cash_control`, `cd_gateway_settlement`, `cd_cashflow_forecast`, `cd_trade_finance` |
| **Requirement range** | FR-TRE-001 … FR-TRE-042 |
| **Requirement count** | **42** *(measured — supersedes the 30 estimate in `02-02`)* |
| **Effort estimate** | **22 person-weeks** *(measured — supersedes the 16 PW estimate)* |
| **Depends on** | M19 GL · M20 Receivables · M52 Payables · M04 Branch Operations · M33 Party Master · M29 Identity · M28 Integration · M30 Platform Admin |
| **Depended on by** | M19, M20, M52, M51, M53, M49, M54, M04, M02, M03, M21, M44, M12, M25, M13, M56 |

---

## 2. Purpose

M50 answers one question, continuously and accurately: **how much money does 1000FiX have,
where is it, and how much will it have next week?**

That question is currently unanswerable. Money enters the Company through **51+ branch cash
counters**, technician field collections, rider cash-on-delivery, three mobile-financial-service
and gateway channels, and direct bank transfer. It leaves through vendor payment runs, payroll,
branch petty cash and import settlements. Between the moment a customer hands over a note at a
counter in Chittagong and the moment that note is a reconciled figure in a bank account, there
are four handoffs and no system.

M50 is the module that closes that loop. It owns the bank account, the bank statement, the
reconciliation, the consolidated cash position, the payment execution path, the cash forecast,
and the trade-finance instruments that fund imports. It does not decide who owes what — M20 and
M52 do that. It proves that the money actually moved.

The single largest day-to-day financial control risk in the business is cash across the branch
network. M50, working with M04's counter discipline, converts that from a policy hope into a
system rule: **an unclosed shift blocks the next shift's opening.**

### Why It Exists

There are three distinct problems, and only a dedicated treasury module solves all three.

**Cash control at scale.** Fifty-one-plus counters, 200–400 technicians and a rider fleet all
handle cash. Without shift-level accountability, daily reconciliation and variance escalation
named to a person, losses are undetectable and therefore inevitable. The control is not
"count the cash" — it is that the system refuses to let the next shift open until the last one
is explained.

**The settlement gap.** Bangladeshi MFS and gateway payments settle to the merchant's bank on a
T+1 to T+3 cycle. The customer paid on Tuesday; the money arrives on Thursday, net of fees, in a
batch mixed with other days' transactions. If the ERP treats the customer payment and the bank
credit as one event, the difference becomes a permanent unreconciled suspense balance that grows
every month. This is the most common way Bangladeshi ERP implementations lose control of cash.
M50 reconciles the settlement batch to the underlying transactions and to the bank line.

**Cash visibility for decisions.** A business with imports, an expanding branch network, a
rental fleet and capital plans cannot decide anything without knowing next month's cash. Today
the answer is a spreadsheet built by one person. M50 builds the forecast from the receivables
due, the payables scheduled, the payroll committed and the facilities available.

M50 is P1 and lands in Wave 3 with M19, M20 and M52 — because a ledger, receivables and payables
without a proven bank position are three sets of numbers nobody can act on.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-004 | "Support multiple payment methods: cash, card, bKash, Nagad, SSLCOMMERZ, bank transfer" |
| ERP BRD BR-FIN-007 | "Automate bank reconciliation with imported bank statements" |
| ERP BRD §Process 6 (As-Is) | "Payment received in cash or bank transfer → manually recorded… cash reconciliation unreliable" |
| ERP BRD §Month-End Close Day 1–3 | "Finance runs bank reconciliation (automated statement matching)" |
| ERP BRD BRU-FIN-02 | Cash receipts above BDT 50,000 require the customer's NID |
| `05-05` BRU-FIN-10 | "Branch cash must be reconciled and closed daily; an unclosed shift blocks the next shift's opening" |
| `05-04` §6 SOD-12 | "Handle cash + reconcile the cash book → cash misappropriation → hard block" |
| `_CATEGORY_OVERVIEW.md` §2 | M50 scope: "Bank accounts, branch cash across 51+ counters, gateway settlement, cash-flow forecasting, LC and facilities" |
| `_CATEGORY_OVERVIEW.md` §7 | The complete cash-control mechanism across shift open, movement, close, field, rider, deposit, reconciliation and SoD |
| `_CATEGORY_OVERVIEW.md` §8 | Bank reconciliation auto-match > 94% · unreconciled gateway settlements > 7 days = 0 · branch cash variance < 1 per branch per month |
| `_CATEGORY_OVERVIEW.md` §10 | Risk: "Branch cash controls not adopted — high, direct loss. Shift discipline is a hard system rule, not a policy" |
| Company Profile §Service Infrastructure | 51+ service centres nationwide — the scale of the cash-handling estate |
| Company Profile §Payment Options | MFS, card and bank transfer in active use |
| Exec Summary §6.2 | Financial close and cash flow **BDT 26 lac per year** |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M50 sits between the counter (M04), the subledgers
> (M20, M52) and the ledger (M19). Every boundary is precise, and both sides agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Bank account master: accounts, banks, branches, currencies, purpose, opening and closing |
| 2 | Bank mandates and signatories, authority limits, and the change-control workflow over them |
| 3 | Bank statement acquisition: file import, portal download and host-to-host feed where available |
| 4 | Automatic bank reconciliation with rule-based and heuristic matching, and an exception queue |
| 5 | Bank charges, interest, and unadvised bank-originated entries |
| 6 | The consolidated cash position across all bank accounts, branch tills, field cash and cash in transit |
| 7 | **Branch cash consolidation** across 51+ counters: float, shift totals, variance and deposit tracking |
| 8 | Field technician cash reconciliation, per technician per day |
| 9 | Rider cash-on-delivery reconciliation, per rider per shift |
| 10 | Cash-in-transit tracking from branch to bank, with custody and proof of deposit |
| 11 | Petty cash imprest management at branch and head office |
| 12 | **Payment gateway and MFS settlement reconciliation**: settlement batch to transaction to bank line, net of fees |
| 13 | Payment execution: BEFTN and RTGS file generation, cheque issuance and control, MFS disbursement |
| 14 | Payment instruction lifecycle from M52/M20/M21/M53 through to bank confirmation |
| 15 | Cheque management: book control, issuance, presentation, stop payment, stale cheque handling |
| 16 | Cash-flow forecasting: direct short-horizon and indirect medium-horizon, by entity and currency |
| 17 | Liquidity management: minimum balance policy, inter-account transfer and sweep proposals |
| 18 | Bank facilities: overdraft, term loan and lease obligations — limits, drawdown, repayment schedule and covenant tracking |
| 19 | **Trade finance**: letters of credit, LC amendments, acceptance, retirement, bank guarantees and margins |
| 20 | Foreign-currency holdings, conversions, and the treasury rate supplied to M19 |
| 21 | Bank fee analysis and banking-relationship cost review |
| 22 | Treasury controls: dual authorisation, payment limits, beneficiary whitelisting and out-of-hours restriction |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Counter cash drawer operation, shift open and close, till count | **M04** Branch & Front Desk Operations | Cash handling is a counter process; M50 consolidates the position and enforces the rule |
| Customer invoice, receipt capture and allocation | **M20** Receivables | M20 records that money was received; M50 proves it reached the bank |
| Vendor invoice, match, approval and payment authorisation | **M52** Payables | M52 decides to pay; M50 executes |
| Payroll calculation and payslips | **M21** HR & Payroll | M21 computes; M50 executes the BEFTN salary file |
| Marketplace seller and partner payout calculation | **M53** Revenue & Settlement | M53 computes the payout; M50 disburses it |
| Journal posting of bank, cash, charges, interest and FX | **M19** General Ledger | Only Category G's ledger creates journal entries |
| TDS/VDS determination and challan deposit at the bank | **M51** Tax & Regulatory | M51 owns the statutory obligation; M50 executes the transfer |
| Import documentation, customs clearance, duty computation, landed cost | **M44** Import & Landed Cost | M50 owns the LC as a financial instrument; M44 owns the shipment |
| Purchase commitment that an LC funds | **M16** Procurement | The commercial decision is procurement's |
| Physical transport of cash between sites | **M03** Service Logistics (where a rider or courier carries it) | M50 tracks custody and proof; M03 moves it |
| Capital investment decisions and asset funding approval | **M49** Fixed Assets & Capital Investment | M50 reports whether the cash exists; M49 owns the approval |
| Budgeting, forecasting of profit, and business-line profitability | **M54** Costing & FP&A | M50 forecasts *cash*; M54 forecasts *result* |
| Fraud analytics and anomaly detection models | **M26** AI/ML Services | M50 enforces controls; M26 may score them |
| Customer credit limits and collection strategy | **M20** Receivables | Whether to extend credit is a receivable decision |

### 3.3 Shared Concepts

| Concept | M50's Role | Owning Module |
|---|---|---|
| Bank account | **Owns** — master, mandate, balance and reconciliation | M50 |
| Bank statement | **Owns** acquisition, storage and matching | M50 |
| Cash position | **Owns** — the consolidated figure across all forms of cash | M50 |
| Branch till and shift | Consolidates and enforces the close rule; M04 operates the drawer | M50 / M04 |
| Receipt | Reads from M20 as an expected bank inflow | M20 / M50 |
| Payment instruction | **Owns** execution; M52, M21 and M53 authorise | M50 |
| Gateway/MFS settlement | **Owns** the reconciliation; M20 owns the customer-side receipt | M50 / M20 |
| Cheque | **Owns** the book, issuance and lifecycle | M50 |
| Exchange rate | Owns the treasury/market rate; M19 owns the accounting rate table it feeds | M50 / M19 |
| Letter of credit | **Owns** the financial instrument; M44 owns the shipment it funds | M50 / M44 |
| Bank facility and loan | **Owns** limits, drawdown and repayment; M19 posts the liability | M50 / M19 |
| Cash forecast | **Owns**; inputs come from M20, M52, M21, M53 and M54 | M50 |
| Field and rider cash | Owns the reconciliation; M02 and M03 own the collection | M50 / M02 / M03 |
| NID threshold on cash receipts | Enforces at deposit-level control; M51 owns the statutory rule, M20 captures it | M50 / M51 / M20 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Bank Account Management (BAM) & Cash Management** | Centralised bank account master with signatory workflows and a full audit trail; real-time cash position; short- and long-term cash-flow forecasting; bank statement processing with reprocessing rules | **Bank Account Management as a governed master with a signatory change workflow** — the bank account is treated as a controlled object, not a configuration record. In a business with 51+ branches depositing into multiple banks, knowing exactly who can sign on what, and having the change history, is the difference between control and hope. Also adopted: the cash position as a live figure with a defined composition, not a month-end derivation | SAP's In-House Cash and payment-factory constructs; a single-country group of two entities does not need an internal bank |
| **SAP S/4HANA — Treasury & Risk Management (TRM), Trade Finance** | Letters of credit and bank guarantees as tracked instruments with limits, margins, amendments and expiry | **LC and guarantee as first-class instruments** with limit consumption, margin held, amendment history and expiry alerting. 1000FiX imports parts for 17+ brands; an expired or over-committed LC line stops the supply chain | TRM's hedge accounting and derivative valuation — no exposure of that kind exists |
| **Oracle Fusion Cloud Cash Management** | Bank statement import in multiple formats, automatic reconciliation with configurable matching rules, cash position by bank account and currency, bank account balance history, external transaction handling | **Layered matching**: exact reference match, then rule-based match (amount + date window + counterparty pattern), then one-to-many and many-to-one grouping, then a manual queue. This is what produces a > 94% auto-match rate rather than the 60–70% a single-rule matcher achieves. Also adopted: external transactions (bank-originated charges and interest) as a first-class category rather than a reconciliation exception | Oracle's bank-account-transfer and cash-pool automation depth |
| **Microsoft Dynamics 365 Finance — Cash and Bank Management** | Multiple bank accounts, statement reconciliation, electronic payments (EFT/ACH/wire), positive pay, cheque management with void and stop, bank facility tracking | **Cheque control as a numbered-stock discipline** — cheque books are inventory with issued, used, void, stopped and stale states, reconciled to the bank. Also adopted: the positive-pay concept, adapted as a **beneficiary whitelist** since positive pay is not offered by Bangladeshi banks; a payment to a beneficiary never previously paid requires elevated authorisation | Positive-pay file exchange itself — no local bank support |
| **Modern treasury management systems (Kyriba, Nomentia, HighRadius class)** | Multi-bank connectivity, AI-assisted reconciliation combining rule-based logic with learned patterns, automated cash forecasting from AR/AP and ERP projections, exception-focused analyst workflow | **Forecast built from the ledger, not typed into a spreadsheet** — receivables due dates, payables schedules, payroll commitments and settlement expectations compose the forecast automatically, and the analyst works variance rather than data entry. Also adopted: reconciliation as an exception workflow, where the measure of success is how few items a human sees | Full multi-bank connectivity middleware and AI-native matching in v1; our matching is deterministic and rule-based, with M26 available later to score residual exceptions |
| **Retail multi-site cash control practice** | Shift-level float, blind close, variance thresholds, banking runs with proof of deposit, exception escalation to a named person | **The whole pattern, hardened into a system rule.** The critical adaptation is that the enforcement point is the *next shift's opening*, not a report the branch manager reads later. A control that depends on someone reading a report is not a control at 51 sites | Cash-office automation hardware (smart safes, recyclers) — not economic at branch scale in this market |
| **Bangladesh payment infrastructure (Bangladesh Bank BEFTN, BD-RTGS; bKash, Nagad, SSLCOMMERZ)** | BEFTN batch credit transfers; RTGS for high-value time-critical payments above BDT 100,000; MFS and gateway merchant settlement on T+1 to T+3 cycles with fee deduction | **Payment method selection by value and urgency** — BEFTN for the payment run, RTGS above the threshold where same-day settlement matters. And **settlement reconciliation as a three-way match**: gateway settlement report ↔ underlying customer transactions ↔ bank statement credit, with the fee as an explicit reconciling item | Direct central-bank connectivity; we operate through our banks' corporate channels |
| **Odoo 19 CE `account` + OCA `bank-statement-import`, `account-reconcile`, `account-payment-order`** | Bank and cash journals, statement import (CAMT/OFX/CSV), reconciliation models and widgets, payment orders and batch files | The transactional substrate. OCA `account_statement_import_*` supplies format handling; `account_reconcile_oca` supplies the reconciliation surface; `account_payment_order` supplies payment file generation | Odoo's default reconciliation model set, which assumes low volume and a single cash channel |

**Design position.** Five deliberate positions.

First, **the shift-close rule is enforced at the opening, not in a report**. BRU-FIN-10 says an
unclosed shift blocks the next shift's opening. That is an operational inconvenience by design.
It is also the only control that survives contact with 51 branches, because it cannot be
ignored by a busy manager.

Second, **every non-cash receipt lives in a channel clearing account until it is proven**.
M20 posts there; M50 clears it. The clearing balance per channel, aged, is a headline
operational metric. A rising clearing balance means a gateway reconciliation is failing, and
that is visible within days rather than at year end.

Third, **cash in transit is a tracked custody state, not a gap**. Between the branch safe and
the bank teller, the money belongs to a named person with a reference. Deposits are matched to
bank lines, and an unmatched deposit older than the threshold is an incident, not a
reconciliation item.

Fourth, **the forecast is generated, and the analyst explains variance**. A treasury analyst
who spends their week assembling a forecast has no time to act on it. M50 assembles it from
system data; the analyst's work is judgement — collection likelihood, discretionary payment
timing, facility usage.

Fifth, **payment execution is separated from payment authorisation, by module**. M52, M21 and
M53 authorise; M50 executes. This means the bank connection lives in exactly one place, with one
set of controls, one audit trail, and one idempotency guarantee — and no subledger can ever
touch a bank file.

---

## 5. Functional Areas & Features

### 5.1 Bank Account Management & Governance

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-001 | Bank account master | Maintain every bank account with bank, branch, account number, currency, entity, purpose, opening and closing dates, and the GL account it maps to | **P0** | L1/L5 |
| FR-TRE-002 | Mandates and signatories | Record authorised signatories, their limits, joint-signing requirements and validity periods per account, with a change workflow requiring CFO approval and a full history | **P0** | L5 |
| FR-TRE-003 | Account purpose segregation | Designate accounts by purpose — collection, disbursement, payroll, tax, escrow, margin — and restrict which processes may transact on each | **P0** | L5 |
| FR-TRE-004 | Balance history | Retain daily opening and closing balances per account per currency, with the source of each balance recorded | **P0** | L5 |
| FR-TRE-005 | Bank relationship record | Hold the facility, fee schedule, service level and contact for each banking relationship, and report the total cost of each | P2 | L5 |

### 5.2 Bank Statement Processing & Reconciliation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-006 | Statement acquisition | Acquire bank statements by file import (CAMT.053, MT940, OFX, CSV, bank-specific formats), portal download or host-to-host feed, with duplicate-statement detection (BR-FIN-007) | **P0** | L2/L5 |
| FR-TRE-007 | Layered auto-matching | Match statement lines to expected items in layers — exact reference, rule-based (amount, date window, counterparty pattern), one-to-many and many-to-one grouping — targeting > 94% automatic match | **P0** | L5 |
| FR-TRE-008 | Matching rule management | Author, test, version and prioritise matching rules per bank and per transaction pattern, without a code release | **P0** | L5 |
| FR-TRE-009 | Reconciliation exception queue | Present unmatched lines as a prioritised queue with suggested matches, ageing and assignment, and prevent an item from being cleared without an explanation | **P0** | L2/L5 |
| FR-TRE-010 | Bank-originated entries | Recognise and classify bank charges, interest, tax on interest and unadvised debits as external transactions, and raise them to M19 without treating them as exceptions | **P0** | L5 |
| FR-TRE-011 | Reconciliation statement | Produce, per account per period, a formal bank reconciliation statement showing book balance, bank balance, and every reconciling item with its age | **P0** | L2/L5 |
| FR-TRE-012 | Reconciliation close gate | Prevent M19 period close until every bank account is reconciled and every reconciling item older than the threshold is explained | **P0** | L5 |

### 5.3 Branch, Field & Rider Cash Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-013 | Consolidated cash position | Present the total cash held across all bank accounts, branch tills, technician floats, rider collections, petty-cash imprests and cash in transit, by entity, branch and currency, updated continuously | **P0** | L5 |
| FR-TRE-014 | Branch shift consolidation | Receive every shift open, movement and close from M04 across 51+ counters, and maintain the branch cash position and its variance history | **P0** | L5 |
| FR-TRE-015 | Shift close enforcement | Block the opening of a new shift at a counter where the previous shift is not closed and reconciled (BRU-FIN-10) | **P0** | L5 |
| FR-TRE-016 | Variance escalation | Escalate a shift variance above the first threshold to the branch manager and above the second to the Finance Manager, with the counter, the cashier and the value named | **P0** | L5 |
| FR-TRE-017 | Field cash reconciliation | Reconcile technician-collected cash per technician per day against the receipts they issued, and block further field collection where an unresolved variance exists | **P0** | L5 |
| FR-TRE-018 | Rider cash-on-delivery reconciliation | Reconcile rider COD collections per rider per shift against delivered manifests, with variance handling identical to a counter shift | **P0** | L5 |
| FR-TRE-019 | Cash in transit | Track cash from branch safe to bank as a custody state with a named carrier, a reference and an expected deposit time, and match it to the bank statement credit | **P0** | L5 |
| FR-TRE-020 | Deposit matching | Match each branch deposit to its bank statement line, and raise an incident where a deposit is unmatched beyond the threshold | **P0** | L5 |
| FR-TRE-021 | Petty cash imprest | Operate imprest floats at branches and head office with top-up on evidence of spend, an expense limit, and a periodic count | P1 | L1/L5 |
| FR-TRE-022 | Cash holding limits | Enforce a maximum cash holding per counter and per branch safe, prompting a banking run when exceeded | P1 | L5 |
| FR-TRE-023 | High-value cash deposit control | Verify that receipts above the statutory cash threshold carry the NID captured by M20, and flag any deposit composed of such receipts without it (BRU-FIN-02) | **P0** | L5 |

### 5.4 Gateway & MFS Settlement Reconciliation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-024 | Settlement file ingestion | Ingest settlement and transaction reports from bKash, Nagad, SSLCOMMERZ and card acquirers on their published cycles, in each provider's format | **P0** | L5 |
| FR-TRE-025 | Three-way settlement match | Match each settlement batch to its underlying customer transactions in M20 and to the bank statement credit, treating the provider's fee and any tax on it as explicit reconciling items | **P0** | L5 |
| FR-TRE-026 | Channel clearing clearance | Clear matched transactions from the channel clearing account to the bank account, and report the residual clearing balance per channel by age | **P0** | L5 |
| FR-TRE-027 | Settlement exception handling | Identify transactions settled but not recorded, recorded but not settled, and settled at an unexpected value, and route each to resolution with the provider | **P0** | L5 |
| FR-TRE-028 | Refund and chargeback tracking | Track gateway refunds and chargebacks through to their settlement impact, and notify M20 to reverse the affected receipt | **P0** | L5 |
| FR-TRE-029 | Provider fee analysis | Report fees paid per channel against contracted rates, by volume band, and flag any deviation | P2 | L5 |

### 5.5 Payment Execution

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-030 | Payment instruction intake | Accept authorised payment instruction batches from M52, M21, M53 and M20 (refunds), with end-to-end idempotency and no capacity for a subledger to bypass M50 | **P0** | L5 |
| FR-TRE-031 | Bank file generation | Generate BEFTN batch credit files and RTGS instructions in each bank's required format, with validation before release | **P0** | L2/L5 |
| FR-TRE-032 | Payment method routing | Route each payment by value, urgency and beneficiary capability — BEFTN, RTGS above the high-value threshold, cheque, MFS disbursement or cash — within policy limits per method | **P0** | L5 |
| FR-TRE-033 | Treasury dual authorisation | Require dual authorisation for release of any payment file above the configured value, by users distinct from the authorising subledger's approvers | **P0** | L5 |
| FR-TRE-034 | Beneficiary whitelist | Require elevated authorisation for a payment to a beneficiary account never previously paid, and record the verification | **P0** | L5 |
| FR-TRE-035 | Cheque management | Control cheque books as numbered stock through issued, used, void, stopped and stale states, reconcile them to the bank, and support stop-payment instruction | **P0** | L5 |
| FR-TRE-036 | Payment confirmation | Confirm each payment against the bank statement or the bank's acknowledgement, and report success, failure or return to the authorising module | **P0** | L5 |

### 5.6 Liquidity, Forecasting & Trade Finance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRE-037 | Short-horizon cash forecast | Produce a rolling 13-week direct cash forecast from receivables due, payables scheduled, payroll committed, settlement expected and facility movements, by entity and currency | **P0** | L5 |
| FR-TRE-038 | Forecast accuracy tracking | Compare each forecast to actual and report accuracy by horizon, so the forecast is improved rather than merely produced | P1 | L5 |
| FR-TRE-039 | Liquidity policy | Hold minimum-balance and concentration policies per account, and propose inter-account transfers or sweeps where a policy is breached | P1 | L5 |
| FR-TRE-040 | Facilities and borrowings | Record overdrafts, term loans and lease obligations with limits, drawdowns, repayment schedules, interest terms and covenant tests, and raise each movement to M19 | P1 | L5 |
| FR-TRE-041 | Letters of credit and guarantees | Record LCs and bank guarantees with issuing bank, beneficiary, value, margin held, limit consumed, amendments, acceptance, retirement and expiry, and alert before expiry (with M44 for the shipment) | P1 | L5 |
| FR-TRE-042 | FX holdings and conversion | Track foreign-currency balances, record conversions with the rate achieved and the realised difference, and publish the treasury rate to M19's accounting rate table | P1 | L1/L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Single egress point for money** | All outbound payment paths terminate in M50. No subledger module holds bank credentials, generates a bank file, or can instruct a bank. Enforced by network policy and credential scope, not only by convention |
| T-02 | **End-to-end payment idempotency** | An idempotency key issued by the authorising module is carried through the instruction, the batch, the bank file and the confirmation. A replayed release at any layer produces exactly one disbursement |
| T-03 | **Statement ingestion integrity** | Every statement is checked for duplicate ingestion, sequence continuity (opening balance equals prior closing) and internal arithmetic before any line is matched. A statement failing any check is quarantined, not partially processed |
| T-04 | **Deterministic layered matching** | Matching runs in ordered, versioned layers with each match recording the layer, rule and confidence that produced it. A match is always explainable and always reversible |
| T-05 | **Matching performance** | A daily statement set across all accounts (estimated 3,000–6,000 lines) matches in ≤ 3 minutes; the reconciliation workspace loads in ≤ 2 s |
| T-06 | **Cash position freshness** | The consolidated cash position reflects a counter movement within 60 seconds of it being recorded in M04, and a bank statement line within 5 minutes of statement ingestion |
| T-07 | **Shift-close enforcement at the gate** | The block on opening a new shift is evaluated in the shift-open service path and re-evaluated server-side at commit; it cannot be bypassed by a client, an API call or an offline replay |
| T-08 | **Offline resilience at the counter** | Shift open, cash movement and shift close are recorded through an append-only local journal during connectivity loss and synchronise with server-side conflict resolution (AS-13). **The shift-close block is evaluated against the last known state and fails closed** — a counter that cannot verify the previous close does not open |
| T-09 | **Settlement matching at volume** | Gateway settlement batches carrying up to ~20,000 transactions reconcile against M20 receipts and the bank line within the settlement day |
| T-10 | **Bank credential and connectivity security** | Bank portal and host-to-host credentials are held in the platform secret store, never in application configuration; all bank communication is mutually authenticated and logged; credential use is restricted to the payment service identity |
| T-11 | **Monetary and FX discipline** | All amounts `Monetary` with explicit currency (AS-10); a bank balance is always stored in the account's currency with the functional-currency equivalent derived, never the reverse |
| T-12 | **Event emission via outbox** | Every treasury state change emits a domain event through the transactional outbox (AS-08); M19, M20, M52, M51 and M54 consume |
| T-13 | **Multi-entity isolation** | Every treasury record carries `company_id`; a payment cannot cross legal entities, and a bank account belongs to exactly one entity (AS-03) |
| T-14 | **Audit completeness on the money path** | Every payment instruction, authorisation, file release, bank response and reconciliation decision is logged immutably with actor, timestamp and IP, and retained seven years |
| T-15 | **Volume envelope** | 51+ counters × up to 3 shifts/day ≈ **55,000 shift records/year**; ~400,000 counter receipts/year; ~3,000–6,000 bank statement lines/day at peak; 12–25 bank accounts across entities |
| T-16 | **Forecast recomputation** | The 13-week forecast recomputes nightly in full and incrementally on material change, with each version retained so accuracy can be measured against what was actually forecast |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M50 |
|---|---|---|
| **Cashier** | Counts the till at shift end and hands over cash and a note | Closes the shift in the system with a counted balance; a variance is explained now, by them, not investigated later by someone else |
| **Branch manager** | Signs a cash summary they cannot verify | Sees the branch position live, is alerted to variances by counter and cashier, and cannot let a counter reopen on an unclosed shift |
| **Technician / rider** | Carries collected cash and settles informally | Reconciles daily against the receipts they issued; a variance blocks further collection until resolved |
| **Finance officer (bank)** | Reconciles statements line by line in Excel for days | Works an exception queue; > 94% of lines never reach a human |
| **Treasury / Finance Manager** | Builds a cash forecast in a spreadsheet from phone calls | Reviews a generated 13-week forecast and works the judgement items |
| **CFO** | Knows the cash position at month-end, approximately | Knows it continuously, by entity, branch and currency, with a forward view |
| **Procurement / import team** | Discovers an LC limit problem when the bank refuses | Sees limit consumption and expiry alerts before they bite |
| **Internal audit** | Samples cash records to test control | Tests the control itself, because the evidence is complete by construction |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Cash leakage elimination** | 51+ counters, 200–400 technicians and the rider fleet move from untracked to shift-reconciled with named accountability and a hard blocking rule | The **largest identified day-to-day financial control risk in the business** (`_CATEGORY_OVERVIEW.md` §10). Target: < 1 variance incident per branch per month |
| **Reconciliation labour released** | Bank reconciliation from days of manual matching to an exception queue at > 94% auto-match | A material share of the **BDT 62 lac** cross-module administrative saving |
| **Settlement recovery** | Gateway and MFS settlements matched three ways; settled-not-recorded and recorded-not-settled both detected within the cycle | Recovers value that is currently invisible; target zero unreconciled settlements older than 7 days |
| **Close acceleration** | Bank accounts reconciled continuously rather than at month-end | Direct contributor to the ≤ 3-day close (KPI-050) and to the **BDT 26 lac** close and cash-flow benefit |
| **Working capital efficiency** | A 13-week forward view allows payment timing, facility usage and surplus placement to be decided rather than defaulted | Reduces overdraft interest and avoids emergency borrowing |
| **Fraud prevention on the payment path** | Single egress point, dual authorisation, beneficiary whitelisting, cheque stock control, idempotent execution | Closes the outbound-payment fraud paths that a distributed payment capability leaves open |
| **Banking cost reduction** | Fee analysis per channel and per relationship against contracted rates | Provides the evidence base for renegotiating merchant and banking terms — currently negotiated without data |
| **Import continuity** | LC limits, margins and expiry tracked and alerted | Prevents supply interruption to warranty operations across 17+ brands |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **A provable cash position** | The Company can state, and evidence, exactly how much money it holds on any date. This is a precondition for bank facilities, investment discussion and any external financial scrutiny |
| **Accountability culture at the counter** | Naming variance to a shift and a person, at the time it happens, changes behaviour in a way that a monthly report cannot |
| **Statutory cash compliance** | High-value cash receipts carry NID evidence through to deposit, satisfying the NBR expectation at the point it is examined |
| **Segregation of duties on cash** | SOD-12 (handle cash + reconcile the cash book) enforced by the system rather than by staffing luck at a small branch |
| **Banking relationship credibility** | A treasury that produces accurate forecasts and reconciled positions negotiates from a different position |
| **ISO 27001 / ISMS alignment** | Bank credentials centralised, scoped and logged; one audited egress path rather than several |
| **Expansion readiness** | A new branch is a new till in an existing control framework, not a new spreadsheet. A second entity or country is new accounts under the same governance (BO-18) |

---

## 8. Lifecycle & State Models

### 8.1 The Cash Journey — from Counter to Reconciled Bank Balance

```
  CUSTOMER PAYS CASH AT A COUNTER (M04 drawer · M20 receipt)
        │
        ▼
  ┌──────────────┐  shift close: counted vs expected
  │ IN TILL      │───────────────────────────────────────┐
  │ (shift open) │                                       │
  └──────────────┘                            ┌──────────▼──────────┐
        │ shift closed, variance explained    │ VARIANCE — escalated│
        ▼                                     │ (branch mgr → FM)   │
  ┌──────────────┐                            └──────────┬──────────┘
  │ IN BRANCH    │◄──────────────── resolved ────────────┘
  │ SAFE         │
  └──────┬───────┘   holding limit breached → banking run prompted
         │ banking run: named carrier, reference, expected time
         ▼
  ┌──────────────┐   not matched within threshold   ┌──────────────┐
  │ CASH IN      │─────────────────────────────────►│  INCIDENT    │
  │ TRANSIT      │                                  └──────────────┘
  └──────┬───────┘
         │ deposit slip + bank statement credit matched
         ▼
  ┌──────────────┐
  │  IN BANK —   │
  │  RECONCILED  │
  └──────────────┘

  NON-CASH TENDER (card · bKash · Nagad · SSLCOMMERZ)
        │  M20 posts to the channel clearing account
        ▼
  ┌──────────────────┐   settlement report ingested   ┌───────────────────┐
  │ CHANNEL CLEARING │──────────────────────────────► │ THREE-WAY MATCHED │
  │ (aged daily)     │   txn ↔ settlement ↔ bank line │ (fee separated)   │
  └──────────────────┘                                └─────────┬─────────┘
        │ not settled beyond threshold                          │
        ▼                                                       ▼
  ┌──────────────────┐                                 ┌──────────────┐
  │ SETTLEMENT       │                                 │  IN BANK —   │
  │ EXCEPTION        │                                 │  RECONCILED  │
  └──────────────────┘                                 └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | In till | Shift opened with a counted float; **previous shift must be closed** (BRU-FIN-10) | Cashier (M04) |
| In till | In branch safe | Shift closed with a counted balance and any variance explained | Cashier + Branch Manager |
| In till | Variance escalated | Counted balance differs from expected beyond the first threshold | System |
| Variance escalated | In branch safe | Variance explained and accepted, or written off under approval | Branch Manager / Finance Manager |
| In branch safe | Cash in transit | Banking run initiated with a named carrier and reference | Branch Manager |
| Cash in transit | In bank — reconciled | Deposit matched to the bank statement credit | System / Finance Officer |
| Cash in transit | Incident | Not matched to a bank line within the threshold | System |
| — | Channel clearing | Non-cash receipt captured in M20 | M20 |
| Channel clearing | Three-way matched | Settlement report matched to transactions and to the bank credit | System |
| Channel clearing | Settlement exception | Not settled within the provider's published cycle plus tolerance | System |
| Three-way matched | In bank — reconciled | Clearing cleared to bank; fee posted to expense | System |

### 8.2 Payment Instruction Lifecycle

```
  M52 payment run · M21 payroll · M53 payout · M20 refund
        │ authorised in the originating module
        ▼
  ┌──────────────┐  validation failed  ┌──────────────┐
  │  RECEIVED    │────────────────────►│  REJECTED    │──► back to originator
  └──────┬───────┘                     └──────────────┘
         │ beneficiary and method validated
         ▼
  ┌──────────────┐  new beneficiary   ┌───────────────────┐
  │  VALIDATED   │───────────────────►│ AWAITING ELEVATED │
  └──────┬───────┘                    │ AUTHORISATION     │
         │                            └─────────┬─────────┘
         │◄─────────── authorised ──────────────┘
         ▼
  ┌──────────────┐   dual authorisation above threshold
  │  AUTHORISED  │
  └──────┬───────┘
         │ file generated and released to the bank
         ▼
  ┌──────────────┐   bank rejects   ┌──────────────┐
  │  RELEASED    │─────────────────►│   FAILED     │──► notify originator
  └──────┬───────┘                  └──────────────┘
         │ bank confirmation / statement match
         ▼
  ┌──────────────┐   funds returned  ┌──────────────┐
  │  CONFIRMED   │──────────────────►│  RETURNED    │──► notify originator
  └──────────────┘                   └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Received | An authorised instruction batch arrives with an idempotency key | M52 / M21 / M53 / M20 |
| Received | Rejected | Beneficiary details invalid, method unavailable, entity mismatch, or period closed | System |
| Received | Validated | Beneficiary, method, currency, limits and entity all valid | System |
| Validated | Awaiting elevated authorisation | Beneficiary account never previously paid | System |
| Validated / Awaiting | Authorised | Dual authorisation obtained where the value requires it, by users distinct from the originating approvers | Treasury authorisers |
| Authorised | Released | Bank file generated, validated and transmitted | System |
| Released | Confirmed | Bank acknowledgement or statement match | System / M50 |
| Released | Failed | Bank rejection at file or item level | Bank |
| Confirmed | Returned | Funds returned by the beneficiary bank | Bank |

### 8.3 Letter of Credit Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Requested | LC application prepared against a purchase commitment (M16/M44) | Bank limit confirmed available |
| Issued | LC opened by the bank; margin held; facility limit consumed | Documents presented |
| Amended | Value, date or terms amended; amendment history retained | Returns to issued |
| Documents presented | Shipping documents received and checked against terms | Accepted or discrepant |
| Accepted | Acceptance given; liability crystallised on the due date | Retired |
| Discrepant | Discrepancies raised; waiver sought or documents refused | Accepted or cancelled |
| Retired | Payment made to the beneficiary; margin released; limit restored | — |
| Expired | Validity lapsed unused; margin released; limit restored | — |
| Cancelled | Cancelled before use | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-TRE-01 | A counter shift cannot open while the previous shift at that counter is unclosed or unreconciled (BRU-FIN-10) | **H** | Finance Manager |
| BRU-TRE-02 | The shift-close block fails closed: a counter that cannot verify the previous shift's close does not open | **H** | CFO |
| BRU-TRE-03 | A shift variance above the first threshold escalates to the branch manager; above the second, to the Finance Manager | **C** | Finance Manager |
| BRU-TRE-04 | A technician or rider with an unresolved cash variance is blocked from further cash collection | **H** | Finance Manager |
| BRU-TRE-05 | The person who handles cash may not reconcile the cash book for the same scope (SOD-12) | **H** | CFO |
| BRU-TRE-06 | Cash in transit is always attributed to a named carrier with a reference and an expected deposit time | **H** | Finance Manager |
| BRU-TRE-07 | A branch deposit not matched to a bank statement line within the threshold is raised as an incident, not held as a reconciling item | **H** | CFO |
| BRU-TRE-08 | Cash holding above the configured counter or safe limit prompts a mandatory banking run | **S** | Branch Manager |
| BRU-TRE-09 | Every non-cash receipt clears from its channel clearing account only on a matched settlement; clearing balances are aged and reported daily | **H** | CFO |
| BRU-TRE-10 | A settlement unreconciled for more than 7 days is a reportable exception with a named owner | **H** | CFO |
| BRU-TRE-11 | All outbound payments execute through M50; no other module may hold bank credentials or generate a bank file | **H** | CTO |
| BRU-TRE-12 | A payment above the configured value requires dual treasury authorisation by users distinct from the authorising subledger's approvers | **H** | CFO |
| BRU-TRE-13 | A payment to a beneficiary account never previously paid requires elevated authorisation and a recorded verification | **H** | CFO |
| BRU-TRE-14 | A payment instruction replayed at any layer produces exactly one disbursement | **H** | CTO |
| BRU-TRE-15 | A payment cannot be released into a period hard-closed in M19 | **H** | CFO |
| BRU-TRE-16 | A payment cannot cross legal entities; a bank account belongs to exactly one entity | **H** | CFO |
| BRU-TRE-17 | Cheque stock is controlled as numbered inventory; an unaccounted cheque number blocks the next issuance from that book | **H** | Finance Manager |
| BRU-TRE-18 | A bank statement failing duplicate, sequence or arithmetic validation is quarantined and never partially processed | **H** | CTO |
| BRU-TRE-19 | An M19 period cannot close until every bank account is reconciled and every reconciling item beyond the threshold is explained | **H** | CFO |
| BRU-TRE-20 | A bank mandate or signatory change requires CFO approval and retains a full history | **H** | CFO |
| BRU-TRE-21 | Bank accounts are restricted by purpose; a payroll account cannot be used for a vendor payment run | **H** | CFO |
| BRU-TRE-22 | Bank credentials are held only in the platform secret store and are scoped to the payment service identity | **H** | CTO |
| BRU-TRE-23 | A deposit composed of cash receipts above the statutory threshold is flagged where the corresponding NID evidence is absent | **H** | CFO |
| BRU-TRE-24 | An LC or guarantee within the configured expiry window raises an alert to Treasury, Procurement and the CFO | **C** | Finance Manager |
| BRU-TRE-25 | A facility drawdown that would breach a limit or a covenant is blocked pending CFO decision | **H** | CFO |
| BRU-TRE-26 | Every forecast version is retained so that accuracy can be measured against what was actually forecast | **H** | Finance Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.bank` | `fix_bank` | Banking institution | name, swift, country, relationship_manager, fee_schedule_ref, service_level |
| `fix.bank.account` | `fix_bank_account` | Bank account master | bank_id, branch_name, account_number, iban_or_local, currency, entity_id, purpose (collection/disbursement/payroll/tax/escrow/margin), gl_account_id, opened_at, closed_at, state |
| `fix.bank.mandate` | `fix_bank_mandate` | Signatory authority | bank_account_id, signatory_user_id, limit_amount, joint_with_ids, valid_from, valid_to, approved_by, change_history_ref |
| `fix.bank.balance` | `fix_bank_balance` | Daily balance history | bank_account_id, balance_date, opening, closing, currency, source (statement/portal/manual), captured_at |
| `fix.bank.statement` | `fix_bank_statement` | Imported statement | bank_account_id, statement_reference, format, period_from, period_to, opening_balance, closing_balance, line_count, ingest_hash, validation_state, imported_at, imported_by |
| `fix.bank.statement.line` | `fix_bank_statement_line` | One bank movement | statement_id, value_date, booking_date, amount, currency, direction, bank_reference, counterparty_name, counterparty_account, narrative, match_state, matched_layer, match_confidence, matched_object_type, matched_object_id |
| `fix.bank.matching.rule` | `fix_bank_matching_rule` | Reconciliation rule | bank_id, layer, priority, condition_json, target_object_type, tolerance_json, version, state, effective_from, approved_by |
| `fix.bank.reconciliation` | `fix_bank_reconciliation` | Formal reconciliation statement | bank_account_id, period_id, book_balance, bank_balance, reconciling_items_json, unexplained_count, state, prepared_by, reviewed_by, signed_off_at |
| `fix.bank.external.transaction` | `fix_bank_external_transaction` | Bank-originated entry | statement_line_id, type (charge/interest/tax/unadvised), amount, classified_by, gl_entry_ref |
| `fix.cash.position` | `fix_cash_position` | Consolidated cash | as_at, entity_id, branch_id, currency, in_bank, in_till, in_safe, in_field, in_transit, in_petty_cash, in_clearing, total, computed_at |
| `fix.branch.cash.day` | `fix_branch_cash_day` | Branch daily cash | branch_id, business_date, opening, receipts_cash, disbursements, deposits, closing, variance_total, shift_ids, state |
| `fix.shift.cash.summary` | `fix_shift_cash_summary` | Consolidated shift record from M04 | shift_id (M04), counter_id, branch_id, cashier_id, opened_at, closed_at, float_amount, expected_close, counted_close, variance, variance_reason, escalation_level, escalated_to, resolved_at, state |
| `fix.field.cash.reconciliation` | `fix_field_cash_reconciliation` | Technician daily cash | technician_id, business_date, receipts_issued_total, cash_declared, variance, evidence_refs, state, blocked_flag, resolved_at |
| `fix.rider.cash.reconciliation` | `fix_rider_cash_reconciliation` | Rider COD per shift | rider_id, manifest_id (M03), shift_date, cod_expected, cod_collected, cod_deposited, variance, state, blocked_flag |
| `fix.cash.in.transit` | `fix_cash_in_transit` | Banking run custody | branch_id, amount, currency, carrier_type (staff/rider/security_service), carrier_id, reference, dispatched_at, expected_deposit_at, bank_account_id, deposit_slip_ref, matched_statement_line_id, state, incident_id |
| `fix.petty.cash.imprest` | `fix_petty_cash_imprest` | Imprest float | location_id, custodian_id, imprest_amount, current_balance, last_topup_at, last_count_at, count_variance, state |
| `fix.settlement.provider` | `fix_settlement_provider` | Gateway/MFS provider config | name (bkash/nagad/sslcommerz/card_acquirer), settlement_cycle_days, fee_schedule_json, file_format, clearing_account_id, bank_account_id, contract_ref |
| `fix.settlement.batch` | `fix_settlement_batch` | One settlement from a provider | provider_id, batch_reference, settlement_date, gross_amount, fee_amount, tax_on_fee, net_amount, transaction_count, file_ref, bank_statement_line_id, state |
| `fix.settlement.line` | `fix_settlement_line` | One settled transaction | batch_id, provider_txn_ref, transaction_date, gross, fee, net, matched_receipt_id (M20), match_state, exception_type |
| `fix.settlement.exception` | `fix_settlement_exception` | Settlement discrepancy | provider_id, type (settled_not_recorded/recorded_not_settled/value_mismatch/chargeback), reference, amount, age_days, assigned_to, state, provider_case_ref, resolved_at |
| `fix.payment.instruction` | `fix_payment_instruction` | Batch received from a subledger | source_module, source_reference, entity_id, bank_account_id, method, total_amount, currency, line_count, idempotency_key, state, received_at, released_at, file_ref |
| `fix.payment.instruction.line` | `fix_payment_instruction_line` | One payment | instruction_id, beneficiary_party_id, beneficiary_account, beneficiary_bank, amount, currency, reference, method, state, bank_item_reference, confirmation_at, failure_reason |
| `fix.payment.authorisation` | `fix_payment_authorisation` | Treasury authorisation | instruction_id, authoriser_id, level (first/second/elevated), decided_at, decision, value_band, sod_check_result |
| `fix.beneficiary.whitelist` | `fix_beneficiary_whitelist` | Previously paid beneficiaries | party_id, beneficiary_account, bank, first_paid_at, verified_by, verification_ref, state |
| `fix.cheque.book` | `fix_cheque_book` | Cheque stock | bank_account_id, book_reference, number_from, number_to, received_at, custodian_id, state |
| `fix.cheque` | `fix_cheque` | One cheque | book_id, cheque_number, payee_party_id, amount, issued_at, issued_by, state (unused/issued/presented/void/stopped/stale), presented_at, statement_line_id, stop_reason |
| `fix.cash.forecast` | `fix_cash_forecast` | A forecast version | entity_id, currency, horizon_weeks, generated_at, version, method (direct/indirect), assumptions_json, state |
| `fix.cash.forecast.line` | `fix_cash_forecast_line` | One forecast bucket | forecast_id, week_start, category (ar_collection/ap_payment/payroll/tax/settlement/facility/capex/other), forecast_amount, actual_amount, variance, confidence |
| `fix.liquidity.policy` | `fix_liquidity_policy` | Balance policy | bank_account_id, minimum_balance, target_balance, maximum_concentration_pct, sweep_rule, active |
| `fix.bank.facility` | `fix_bank_facility` | Overdraft, loan or lease | bank_id, entity_id, type, limit_amount, currency, drawn_amount, available, interest_terms, repayment_schedule_json, covenants_json, start_date, end_date, state |
| `fix.facility.movement` | `fix_facility_movement` | Drawdown or repayment | facility_id, movement_date, type, amount, interest_component, principal_component, gl_entry_ref |
| `fix.letter.of.credit` | `fix_letter_of_credit` | LC instrument | bank_id, entity_id, lc_number, beneficiary_party_id, value, currency, margin_held, facility_id, issue_date, expiry_date, latest_shipment_date, import_consignment_id (M44), state, amendment_history_json, retired_at |
| `fix.bank.guarantee` | `fix_bank_guarantee` | Guarantee issued | bank_id, entity_id, beneficiary_party_id, type (bid/performance/advance), value, currency, margin_held, issue_date, expiry_date, state, claim_history_json |
| `fix.fx.holding` | `fix_fx_holding` | Foreign-currency position | entity_id, currency, bank_account_id, balance, as_at |
| `fix.fx.conversion` | `fix_fx_conversion` | Conversion executed | from_currency, to_currency, amount_from, amount_to, rate_achieved, bank_id, executed_at, realised_difference, gl_entry_ref |
| `fix.treasury.rate` | `fix_treasury_rate` | Market/treasury rate published to M19 | currency_pair, rate_date, buy_rate, sell_rate, source, published_to_gl_at |
| `fix.bank.fee.analysis` | `fix_bank_fee_analysis` | Fee review | provider_or_bank_id, period, volume, contracted_rate, effective_rate, fee_paid, deviation, reviewed_by |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.branch.shift`, `fix.cash.drawer`, `fix.cash.movement` | M04 | Consume events; M04 owns the drawer |
| `fix.ar.receipt`, `fix.ar.open.item` | M20 | Read for expected inflow and settlement matching; instruct receipt reversal |
| `fix.ap.payment.run`, `fix.ap.open.item` | M52 | Consume instructions; supply confirmation and cash constraint |
| `fix.payroll.run` | M56 | Consume the salary payment instruction |
| `fix.settlement.cycle`, `fix.payout.run` | M53 | Consume seller and partner payout instructions |
| `fix.gl.account`, `fix.fiscal.period`, `fix.currency.rate` | M19 | Read period state; publish the treasury rate |
| `fix.tax.determination`, `fix.tax.challan` | M51 / M56 | Execute challan deposits; read the NID threshold rule |
| `fix.party` (vendor, employee, seller, brand, bank) | M33 | Read via API |
| `fix.import.consignment` | M44 | Link the LC to the shipment it funds |
| `fix.purchase.order` | M16 | Read as the commitment an LC funds |
| `fix.consignment`, `fix.consignment` | M03 | Read for rider COD reconciliation and cash-carrier custody |
| `fix.technician.profile` | M02 | Read for field cash accountability |
| `fix.budget.line`, `fix.capex.request` | M54 / M49 | Read as forecast input |
| `fix.document` | M24 | Store statements, deposit slips, LC documents |
| `fix.sod.rule` | M29 / M60 | Evaluate SOD-12 and treasury authorisation separation |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-TRE-01 | Bank statement available (feed, portal or import) | Validate duplicate, sequence and arithmetic; ingest; run layered matching; publish the exception queue | Quarantine the statement whole; alert Treasury; never partially process |
| AUT-TRE-02 | Statement line matched | Clear the corresponding expected item and raise the posting event to M19 | Hold as matched-unposted and report |
| AUT-TRE-03 | Statement line unmatched after all layers | Add to the exception queue with suggested matches, age it, and assign by rule | Item remains queued and ages visibly |
| AUT-TRE-04 | Bank-originated entry detected (charge, interest, tax) | Classify, raise to M19 for posting, and add to the fee analysis | Route to manual classification |
| AUT-TRE-05 | M04 reports a shift close | Update the branch cash day, compute the variance, and escalate by threshold | Record and escalate to the branch manager on the next sync |
| AUT-TRE-06 | Shift open requested at a counter | Verify the previous shift is closed and reconciled; permit or block (BRU-FIN-10) | **Fail closed** — the counter does not open |
| AUT-TRE-07 | Technician or rider day ends | Prompt cash reconciliation against receipts issued; compute variance; block further collection where unresolved | Block applies on the next collection attempt |
| AUT-TRE-08 | Banking run initiated | Create the cash-in-transit record with carrier, reference and expected deposit time; start the matching clock | Manual creation with an alert |
| AUT-TRE-09 | Cash in transit unmatched beyond threshold | Raise an incident to the Branch Manager, Finance Manager and CFO | Escalation is unconditional |
| AUT-TRE-10 | Cash holding exceeds the counter or safe limit | Prompt a banking run and notify the branch manager | Alert only |
| AUT-TRE-11 | Settlement file available from a provider | Ingest, match three ways (transaction ↔ settlement ↔ bank line), separate fee and tax, clear the channel clearing account | Hold the batch, alert Treasury, and age the clearing balance |
| AUT-TRE-12 | Settlement exception detected | Classify (settled-not-recorded, recorded-not-settled, value mismatch, chargeback), assign an owner, and open a provider case where required | Exception remains open and ages on the report |
| AUT-TRE-13 | Chargeback or gateway refund settled | Notify M20 to reverse the affected receipt and restore the invoice | High-priority exception |
| AUT-TRE-14 | Payment instruction batch received | Validate beneficiaries, methods, limits and period; route new beneficiaries for elevated authorisation | Reject the batch to the originator with per-line reasons |
| AUT-TRE-15 | Payment authorised | Generate and validate the bank file, transmit, and record the release with its idempotency key | Hold as authorised-unreleased; never retransmit without idempotency verification |
| AUT-TRE-16 | Bank confirmation or matching statement line received | Confirm the payment and notify the originating module | Retain as released and report on the unconfirmed list |
| AUT-TRE-17 | Bank rejects or returns a payment | Notify the originating module, restore its open items, and record the reason on the beneficiary | High-priority exception |
| AUT-TRE-18 | Cheque presented on a statement | Match to the issued cheque and update its state; flag any presented cheque not issued in the system | Immediate hard alert to the CFO |
| AUT-TRE-19 | Nightly | Recompute the consolidated cash position and the 13-week forecast, retain the version, and compare the prior forecast to actual | Retain the previous version and alert |
| AUT-TRE-20 | Liquidity policy breached | Propose an inter-account transfer or sweep with the amount and accounts named | Alert only |
| AUT-TRE-21 | LC or guarantee within the expiry window | Alert Treasury, Procurement and the CFO with the instrument, value and dependent shipment | Alert repeats daily until acknowledged |
| AUT-TRE-22 | Facility drawdown requested that would breach a limit or covenant | Block and route to the CFO with the breach quantified | Hard block |
| AUT-TRE-23 | Period close initiated in M19 | Assert that every bank account is reconciled and every reconciling item beyond threshold is explained; permit or block the close | Close blocked with the accounts named |
| AUT-TRE-24 | Daily | Publish the clearing-balance ageing, the unmatched-deposit list, the cash-variance register and the unconfirmed-payment list | Report with a data-availability warning |

---

## 12. Interfaces

### 12.1 Upstream — M50 Consumes

| Source | What | Mechanism |
|---|---|---|
| M04 Branch Operations | Shift open, cash movement, shift close, counted balance and variance across 51+ counters | Events |
| M20 Receivables | Receipts by tender, channel clearing postings, expected inflows, refund instructions | Events + commands |
| M52 Payables | Authorised payment instruction batches; cash requirement by due date | Commands + REST |
| M21 HR & Payroll | Salary payment instruction batches | Commands |
| M53 Revenue & Settlement | Seller and partner payout instruction batches; escrow movements | Commands |
| M51 Tax & Regulatory | Challan deposit instructions; NID threshold rule | Commands + REST |
| M02 Field Service | Technician cash collections and daily declarations | Events |
| M03 Logistics | Rider COD manifests and collections; cash-carrier custody | Events |
| M44 Import & Landed Cost | Import consignments requiring LC; document presentation status | REST + events |
| M16 Procurement | Purchase commitments that an LC funds | REST |
| M19 General Ledger | Period state; GL bank balances for reconciliation | REST |
| M54 Costing & FP&A / M49 Fixed Assets | Budgeted and planned cash outflows as forecast input | REST |
| M33 Party Master | Beneficiary and counterparty identity | REST |

### 12.2 Downstream — M50 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Bank movements reconciled, charges, interest, FX conversions, facility movements, cash variances — as financial events for posting | Events |
| M20 Receivables | Settlement matched, cheque cleared, cheque bounced, gateway reversal, refund executed | Events |
| M52 Payables | Payment confirmed, failed or returned; available cash constraint on the payment proposal | Events + REST |
| M21 HR & Payroll | Salary payment confirmation | Events |
| M53 Revenue & Settlement | Payout confirmation; escrow balance | Events |
| M51 Tax & Regulatory | Challan deposit confirmation with bank reference and date | Events |
| M04 Branch Operations | Shift-open permission decision; variance escalation state | REST |
| M02 / M03 | Field and rider cash blocking state | REST |
| M54 Costing & FP&A | Cash actuals and forecast for the financial plan | REST + extract |
| M49 Fixed Assets | Cash availability for capital investment decisions | REST |
| M25 BI / M62 Data Platform | Cash, reconciliation, settlement and variance facts | Warehouse extract |
| P06 Analytics & Executive Dashboard | Cash position and forecast | REST |
| P03 Admin Portal | Full treasury workspace | Native |
| P09 Logistics & Rider App | Rider COD reconciliation surface | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `treasury.statement_ingested` | account, period, line count, validation result | M19, M25 |
| `treasury.line_matched` | statement line, matched object, layer, confidence | M19, M20, M52 |
| `treasury.reconciliation_completed` | account, period, book vs bank, reconciling items | M19, M25 |
| `treasury.bank_charge_recorded` | account, type, amount, classification | M19, M54 |
| `treasury.cash_position_updated` | as-at, entity, branch, composition, total | M25, P06, M54 |
| `treasury.shift_variance_detected` | branch, counter, cashier, shift, variance, escalation level | M04, M19, M23, M21 |
| `treasury.shift_open_blocked` | branch, counter, reason, prior shift | M04, M06 branch manager |
| `treasury.field_cash_variance` | technician, date, variance, blocked flag | M02, M21, M23 |
| `treasury.rider_cash_variance` | rider, manifest, variance, blocked flag | M03, M21, M23 |
| `treasury.deposit_unmatched` | branch, amount, carrier, age | M19, M23, M04 |
| `treasury.settlement_matched` | provider, batch, transactions, fee, bank line | M20, M19, M54 |
| `treasury.settlement_exception` | provider, type, reference, amount, age | M20, M19, M23 |
| `treasury.chargeback_settled` | provider, transaction, receipt, amount | M20, M19 |
| `treasury.payment_released` | instruction, method, total, bank, idempotency key | M52, M21, M53, M19 |
| `treasury.payment_confirmed` | instruction line, bank reference, value date | M52, M21, M53, M19, M51 |
| `treasury.payment_failed` / `treasury.payment_returned` | instruction line, reason | M52, M21, M53, M19 |
| `treasury.cheque_state_changed` | cheque, state, statement reference | M52, M19, M23 |
| `treasury.forecast_published` | entity, horizon, version, buckets | M54, M49, M25, P06 |
| `treasury.facility_movement` | facility, type, amount, drawn, available | M19, M54 |
| `treasury.lc_state_changed` | LC, state, value, margin, expiry | M44, M16, M19 |
| `treasury.lc_expiry_warning` | LC, days remaining, dependent shipment | M44, M16, CFO |
| `treasury.fx_converted` | currencies, amounts, rate, realised difference | M19, M54 |
| `treasury.rate_published` | currency pair, rate type, rate, date | M19, M20, M52, M51 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-TRE-01 | Corporate banking portals (all banking partners) | Bidirectional | Statement download, payment file upload, balance enquiry |
| INT-TRE-02 | Bangladesh Bank BEFTN (via partner banks) | Outbound | Batch credit transfers for vendor, payroll and payout runs |
| INT-TRE-03 | Bangladesh Bank BD-RTGS (via partner banks) | Outbound | High-value time-critical payments above the RTGS threshold |
| INT-TRE-04 | bKash merchant settlement reporting | Inbound | Settlement batches and transaction-level reports |
| INT-TRE-05 | Nagad merchant settlement reporting | Inbound | Settlement batches and transaction-level reports |
| INT-TRE-06 | SSLCOMMERZ settlement and reconciliation reports | Inbound | Settlement, fee, refund and chargeback reporting |
| INT-TRE-07 | Card acquirer settlement files | Inbound | Card settlement and interchange fee reporting |
| INT-TRE-08 | Trade-finance desks at issuing banks | Bidirectional | LC application, amendment, document status, guarantee issuance |
| INT-TRE-09 | Bangladesh Bank published rates | Inbound | Reference and statutory FX rates |
| INT-TRE-10 | Cash-in-transit security service (where used) | Bidirectional | Collection confirmation and deposit proof |
| INT-TRE-11 | Legacy bank reconciliation spreadsheets | Inbound, one-time | Opening reconciling items; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/treasury/cash-position` | GET | Consolidated cash position by entity, branch and currency | P03, P06, M54, M49 |
| `/api/v1/treasury/bank-accounts` | GET · POST | Bank account master and mandates | P03 |
| `/api/v1/treasury/statements` | POST · GET | Import and retrieve bank statements | P03 |
| `/api/v1/treasury/reconciliation/{account}/{period}` | GET · POST | Reconciliation workspace and sign-off | P03 |
| `/api/v1/treasury/matching-rules` | GET · POST | Author, test and version matching rules | P03 |
| `/api/v1/treasury/shift-open-permission` | GET | Whether a counter may open a new shift | M04, P03 |
| `/api/v1/treasury/branch-cash/{branch}` | GET | Branch cash day, shifts and variances | P03, P11 |
| `/api/v1/treasury/field-cash/{technician}` | GET · POST | Field cash reconciliation and declaration | P02 |
| `/api/v1/treasury/rider-cash/{rider}` | GET · POST | Rider COD reconciliation | P09 |
| `/api/v1/treasury/cash-in-transit` | POST · GET | Raise and track a banking run | P03 |
| `/api/v1/treasury/settlements` | GET | Settlement batches, matches and exceptions | P03, M20 |
| `/api/v1/treasury/clearing-ageing` | GET | Channel clearing balance by age | P03, P06, M20 |
| `/api/v1/treasury/payment-instructions` | POST | Submit an authorised payment batch (idempotent) | M52, M21, M53, M20 |
| `/api/v1/treasury/payment-instructions/{id}/authorise` | POST | Treasury authorisation | P03 |
| `/api/v1/treasury/payment-instructions/{id}/status` | GET | Execution and confirmation status | M52, M21, M53, M20, P05 |
| `/api/v1/treasury/cheques` | GET · POST | Cheque book and cheque lifecycle, including stop payment | P03 |
| `/api/v1/treasury/forecast` | GET | Cash forecast by entity, currency and horizon | P03, P06, M54 |
| `/api/v1/treasury/facilities` | GET · POST | Facilities, drawdowns and covenant status | P03 |
| `/api/v1/treasury/letters-of-credit` | GET · POST | LC lifecycle and limit consumption | P03, M44, M16 |
| `/api/v1/treasury/rates` | GET · POST | Treasury rates published to M19 | M19, M20, M52, M51, P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves mandates, facilities, LCs, high-value payments and cash write-offs |
| R26 Finance Manager | C R U A | All entities; treasury operations, reconciliation sign-off, variance resolution, first payment authorisation |
| R27 Finance Officer | C R U | Assigned scope; statement import, matching exceptions, settlement reconciliation — **cannot authorise a payment** |
| R29 Cashier / Counter Finance | C R | Own counter and shift only; declares the shift close — **cannot reconcile the cash book (SOD-12)** |
| R06 Branch Manager | R U A | Own branch; approves variance explanations within authority, initiates banking runs |
| R05 Operations Director | R | All branches; cash position and variance reporting |
| R10 / R11 / R12 Technician | C R | Own field cash declaration only (P02) |
| R16 Rider / Delivery Agent | C R | Own COD reconciliation only (P09) |
| R15 Logistics Coordinator | R U | Rider COD reconciliation for assigned area |
| R19 Procurement Officer | R | LC and guarantee status relevant to their commitments; **no payment rights** |
| R32 Quality Manager / ISO Coordinator | R | Cash variance, deposit incident and settlement exception registers |
| R33 IT / System Administrator | R | Configuration and technical support; **no payment authorisation, no bank credential access** |
| R01 Chief Executive Officer | R A | All; second authoriser for the highest payment band |
| R02 Chief Technology Officer | R | Technical oversight; **no payment rights** |
| R38 External Auditor | R | Scoped read-only — reconciliations, cash registers, payment authorisations |

**Field-level restrictions.** Bank account numbers, mandate details and beneficiary account
numbers are masked in every list view and visible unmasked only to R03, R26 and R27, with every
unmasking logged (AS-14). Bank credentials are never visible in the application to any role
(BRU-TRE-22). Customer NID on high-value cash deposits follows the M20 masking rule.

**Segregation of duties.**
- **SOD-12 enforced here:** a user who handles cash for a scope cannot reconcile the cash book for that scope — hard block.
- Treasury payment authorisers must be distinct from the approvers in the authorising subledger (M52, M21, M53).
- Dual authorisation above the configured value requires two distinct treasury authorisers.
- A user may not both request a bank mandate change and approve it.
- A user may not both issue a cheque and reconcile the account it is drawn on.
- A user may not both raise a cash variance explanation and approve its write-off.
- R33 IT / System Administrator has configuration access with no authorisation rights and no credential access.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Treasury dashboard — consolidated cash position** | CFO, CEO, Finance Manager | Real time | Cash by bank, till, safe, field, transit, petty cash and clearing, by entity, branch and currency — the daily-visibility control named in `_CATEGORY_OVERVIEW.md` §7 |
| **13-week cash forecast** | CFO, CEO, board | Weekly | Direct forecast by category with prior-version accuracy |
| **Bank reconciliation status** | CFO, Finance Manager | Daily | Auto-match rate per account, exception queue depth and age, accounts not yet reconciled — against the > 94% target |
| **Reconciliation statement pack** | CFO, auditor | Monthly | Formal reconciliation per account with every reconciling item and its age |
| **Branch cash variance register** | CFO, Operations Director, Branch Managers | Daily | Variance by branch, counter, cashier and shift — against the < 1 incident per branch per month target |
| **Unclosed shift report** | Branch Manager, Operations Director, CFO | Real time | Every counter with an open or unreconciled prior shift, and the openings it is blocking |
| **Field and rider cash reconciliation** | Operations Director, Dispatch Manager, CFO | Daily | Declaration completion, variance value and blocked collectors |
| **Cash in transit and deposit matching** | CFO, Finance Manager, Branch Managers | Daily | Deposits in transit, matched, unmatched and beyond threshold — with incidents |
| **Channel clearing ageing** | CFO, Finance Manager, CTO | Daily | Balance per payment channel by age — the leading indicator of settlement failure |
| **Settlement reconciliation** | CFO, Finance Manager | Per cycle | Batches ingested, three-way matched, fee reconciled, exceptions by type and age |
| **Gateway fee analysis** | CFO, CCO, CTO | Monthly | Fee paid vs contracted rate per provider and volume band |
| **Payment execution register** | CFO, Internal Audit | Daily | Instructions received, authorised, released, confirmed, failed and returned, with authorisers |
| **New beneficiary register** | CFO, Internal Audit | Weekly | Every first-time beneficiary with the verification record |
| **Cheque control register** | Finance Manager, CFO, auditor | Monthly | Book stock, issued, presented, void, stopped, stale; any presented-not-issued alert |
| **Bank facility and covenant status** | CFO, CEO, board | Monthly | Limits, drawn, available, repayment schedule, covenant tests |
| **LC and guarantee register** | CFO, Procurement, Import team | Weekly | Instruments open, value, margin held, limit consumed, expiry countdown |
| **FX position and conversions** | CFO, Finance Manager | Monthly | Currency balances, conversions, rates achieved, realised differences |
| **Banking cost review** | CFO | Quarterly | Total cost per banking relationship and per channel |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-051** | Bank reconciliation auto-match rate *(re-owned from M19 — see register note)* | manual | 90% | **> 94%** |
| — | Unreconciled gateway/MFS settlements older than 7 days | unmeasured | < 5 | **Zero** |
| — | Branch cash variance incidents per branch per month | unmeasured | < 2 | **< 1** |
| — | Shifts closed and reconciled on the same day | unmeasured | 97% | **99.5%** |
| — | Counter openings blocked by an unclosed prior shift | n/a | tracked | **Falling to near zero** |
| — | Field cash reconciliation completion per technician per day | 0% | 95% | **99%** |
| — | Rider COD reconciliation completion per shift | 0% | 95% | **99%** |
| — | Deposits matched to a bank line within 2 business days | unmeasured | 95% | **99.5%** |
| — | Channel clearing balance older than 3 days | unmeasured | < 5% | **Zero** |
| — | Cash position accuracy (system vs counted, spot check) | unmeasured | 98% | **99.9%** |
| — | 13-week forecast accuracy at 4-week horizon | n/a | ±15% | **±8%** |
| — | Payments confirmed against bank within 1 business day of release | unmeasured | 95% | **99%** |
| — | Duplicate disbursements | unknown | **Zero** | **Zero** |
| — | Bank accounts reconciled before period close | manual | 100% | **100%** |
| — | Cheques presented but not issued in the system | unknown | **Zero** | **Zero** |
| — | LCs or guarantees expiring without action | unknown | **Zero** | **Zero** |

> **Register note.** **KPI-051** (bank reconciliation auto-match) is allocated to **M19** in
> `06-02` §2.7. Under the v2.1 re-scope, bank reconciliation is owned by **M50**; the register
> requires updating — recorded as audit action **A-01**. The fifteen unnumbered metrics are new
> to this specification and require allocation in `06-02` — audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — bank and cash journals, payment registration, basic reconciliation, multi-currency | 20% |
| L2 | OCA `bank-statement-import` (`account_statement_import_*` for CAMT/OFX/CSV), `account-reconcile` (`account_reconcile_oca`), `account-payment-order` (payment file generation), `currency` | 24% |
| L3 | Free bank-format parsers and file utilities | 4% |
| L5 | `cd_cash_position`, `cd_bank_account_mgmt`, `cd_bank_reconciliation`, `cd_branch_cash_control`, `cd_gateway_settlement`, `cd_cashflow_forecast`, `cd_trade_finance` | 52% |

> The custom share is the highest in Category G, and deliberately so. Branch cash consolidation
> across 51+ counters, three-way gateway settlement reconciliation, and a generated cash forecast
> have no L1 or L2 equivalent anywhere in the open-source Odoo ecosystem.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 7 of 7 identifiers below are claimed by another module: **CD-087** also claimed by M58; **CD-167** also claimed by M47, M67; **CD-168** also claimed by M47; **CD-169** also claimed by M47; **CD-170** also claimed by M47; **CD-171** also claimed by M48; **CD-172** also claimed by M48. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-087 | `cd_cash_position` — consolidated cash position across all cash forms, real-time composition, entity and branch views | Odoo module + service | 3 PW |
| **CD-167** | `cd_bank_account_mgmt` — bank and account master, mandates and signatories with change control, purpose segregation, balance history, relationship records | Odoo module | 2 PW |
| **CD-168** | `cd_bank_reconciliation` — statement validation and ingestion, layered matching engine with versioned rules, exception queue, formal reconciliation statement, close gate | Odoo module + service | **6 PW** |
| **CD-169** | `cd_branch_cash_control` — shift consolidation across 51+ counters, shift-open blocking gate, variance escalation, field and rider reconciliation, cash in transit, deposit matching, petty cash | Odoo module + service | **6 PW** |
| **CD-170** | `cd_gateway_settlement` — provider configuration, settlement file ingestion, three-way matching, fee separation, clearing clearance, exception and chargeback handling | Odoo module + service | **5 PW** |
| **CD-171** | `cd_cashflow_forecast` — direct 13-week forecast generation from AR/AP/payroll/settlement/facility inputs, versioning, accuracy measurement, liquidity policy | Odoo module | 3 PW |
| **CD-172** | `cd_trade_finance` — LC and guarantee lifecycle, margin and limit consumption, amendments, expiry alerting, facilities and covenants, FX holdings | Odoo module | 3 PW |

> **CD register reallocation.** **CD-087** (`cd_cash_position`) was allocated to **M19** in
> `02-05` §5.2 and moves to **M50** under the v2.1 re-scope. Six new IDs, **CD-167…172**, are
> claimed from the Category G block defined in `M19` §16.2. **All CD IDs remain provisional**
> pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M19 General Ledger | Bank, cash, charge, FX and facility movements all terminate in journal entries |
| M20 Receivables | The expected-inflow side of reconciliation and the channel clearing model; must go live together |
| M52 Payables | The payment instruction source; must go live together |
| M04 Branch & Front Desk Operations (W1) | Shift and drawer events are the input to branch cash consolidation. **M04 must expose the shift contract before M50 can enforce the block** |
| M29 Identity | SOD-12 and treasury authorisation separation |
| M28 Integration | Event outbox; the secret store for bank credentials |
| M33 Party Master | Beneficiary identity |
| M02 / M03 (W2–W3) | Field and rider cash collection events |
| M51 Tax & Regulatory | Challan deposit execution and the NID threshold rule. **M51 is W4** — the NID threshold operates from a configured constant in W3 |
| M44 Import & Landed Cost | LC-to-shipment linkage. **M44 is W6** — LC tracking operates standalone until then, with the shipment reference entered manually |
| M21 HR & Payroll | Salary payment execution. **M21 is W5** — payroll files are prepared manually until then |

**Delivers into:** M19 (bank postings and reconciliation gate), M20 (settlement and clearance),
M52 (payment confirmation), M51 (challan confirmation), M53 (payout execution), M54 (cash
actuals and forecast). **M19, M20, M52 and M50 must go live together.**

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Bank account master and mandates | 12–25 accounts across entities | `fix.bank.account`, `fix.bank.mandate` | W3 minus 2 months |
| Opening bank balances at cutover | One per account | `fix.bank.balance` + M19 opening journal | W3 cutover |
| Open reconciling items (uncleared cheques, deposits in transit) | Current only | `fix.bank.reconciliation` reconciling items | W3 cutover |
| Unused cheque stock | All books held | `fix.cheque.book`, `fix.cheque` | W3 cutover |
| Branch till floats and safe balances | 51+ branches | `fix.branch.cash.day` opening | W3 cutover |
| Technician floats and rider balances | 200–400 staff | `fix.field.cash.reconciliation` opening | W3 cutover |
| Petty cash imprests | All locations | `fix.petty.cash.imprest` | W3 cutover |
| Open channel clearing balances | Per provider | `fix.settlement.batch` reconstruction | W3 cutover, provider-confirmed |
| Open LCs, guarantees and facilities | Current only | `fix.letter.of.credit`, `fix.bank.guarantee`, `fix.bank.facility` | W3 cutover |
| Historical bank statements | 1–2 years where recoverable | Warehouse (M62) | W3–W4, best-effort |

> **Migration position — non-negotiable.** Cash balances at every location are established by a
> **physical count at cutover**, witnessed and signed, not by loading a recorded balance. Bank
> balances are established from the **bank's own statement, not from the legacy book balance**,
> with every reconciling item individually identified and aged. Open channel clearing balances
> are reconstructed from each provider's settlement history and **confirmed with the provider in
> writing**. Unused cheque stock is physically counted against the register. A migration that
> carries an unexplained cash or clearing balance forward guarantees the reconciliation never
> reaches the > 94% target, because every subsequent exception is contaminated by an unknown
> opening error — the same principle recorded for inventory in `M15` §16.4.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A counter cannot open a shift while the previous shift at that counter is unclosed or unreconciled, through any path including offline replay | Negative test on UI, API and offline sync (BRU-FIN-10) |
| AC-02 | The shift-open check fails closed when the previous shift's state cannot be verified | Negative test with connectivity severed |
| AC-03 | Bank reconciliation auto-match reaches 94% by line count across all accounts | Production measurement over one month (KPI-051) |
| AC-04 | A statement failing duplicate, sequence or arithmetic validation is quarantined whole and never partially processed | Negative test per failure mode |
| AC-05 | Every match records the layer, rule and confidence that produced it and is reversible | Full-table assertion plus a reversal test |
| AC-06 | Gateway and MFS settlements match three ways — transaction, settlement, bank line — with fee and tax as explicit reconciling items | Three consecutive settlement cycles per provider |
| AC-07 | No settlement remains unreconciled beyond 7 days at steady state | Thirty consecutive days of clearing ageing |
| AC-08 | Channel clearing balances age to zero; no balance older than 3 days at steady state | Thirty consecutive days of clearing ageing |
| AC-09 | No module other than M50 can generate a bank file or hold bank credentials | Code review, credential scope audit and network policy review |
| AC-10 | A payment instruction replayed at any layer produces exactly one disbursement | End-to-end idempotency test with forced replay at instruction, batch and file layers |
| AC-11 | A payment above the configured value cannot be released without dual treasury authorisation by users distinct from the subledger approvers | SoD negative test |
| AC-12 | A payment to a never-before-paid beneficiary requires elevated authorisation and records the verification | Scripted scenario |
| AC-13 | A cheque presented on a statement but not issued in the system raises an immediate hard alert | Seeded-defect test |
| AC-14 | A user who handles cash cannot reconcile the cash book for the same scope | SoD negative test (SOD-12) |
| AC-15 | A technician or rider with an unresolved cash variance is blocked from further collection | Scripted scenario |
| AC-16 | A deposit unmatched beyond the threshold raises an incident to the named escalation chain | Scripted scenario |
| AC-17 | The consolidated cash position reflects a counter movement within 60 seconds and a statement line within 5 minutes | Latency test at production volume |
| AC-18 | M19 cannot close a period while any bank account is unreconciled or any reconciling item beyond threshold is unexplained | Scripted close scenario |
| AC-19 | The 13-week forecast generates nightly, retains each version, and measures accuracy against actual | Twelve consecutive weeks of forecast-to-actual measurement |
| AC-20 | An LC within the expiry window alerts Treasury, Procurement and the CFO daily until acknowledged | Scripted scenario |
| AC-21 | A facility drawdown that would breach a limit or covenant is blocked | Negative test |
| AC-22 | A daily statement set of 6,000 lines matches within 3 minutes | Performance test at projected volume |
| AC-23 | Opening cash balances are established by witnessed physical count at every location, and opening bank balances from the bank's own statement | Signed count records for all 51+ branches and bank confirmations per account |
| AC-24 | Open channel clearing balances are confirmed in writing by each provider before cutover | Provider confirmations on file |
| AC-25 | Bank credentials are absent from application configuration and visible to no role | Security review and secret-store audit |
| AC-26 | All cashier, technician and rider cash screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-27 | CFO, Finance Manager and a nominated Branch Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 27 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which banks does 1000FiX hold accounts with, how many accounts, and which offer statement download, host-to-host feed or only manual retrieval? Auto-match feasibility depends entirely on this | CFO / CTO | **W3 minus 3 months — blocking** |
| Q-02 | What statement formats does each bank provide — CAMT.053, MT940, OFX, CSV, or PDF only? A PDF-only bank cannot reach the auto-match target and needs a different plan | CFO / CTO | **W3 minus 3 months — blocking** |
| Q-03 | What are the settlement cycles, file formats and fee schedules under the current bKash, Nagad, SSLCOMMERZ and card-acquirer merchant agreements? | CFO / CTO | W3 minus 2 months |
| Q-04 | What are the cash variance thresholds for branch-manager escalation and for Finance Manager escalation, and at what value does a variance become a disciplinary matter? | CFO / HR Manager | W3 build |
| Q-05 | What are the maximum cash holding limits per counter and per branch safe, and what is the banking-run frequency policy? | CFO / Operations Director | W3 build |
| Q-06 | Is a cash-in-transit security service used, at which branches, and does it provide an electronic confirmation feed? | CFO / Operations Director | W3 design |
| Q-07 | What is the treasury payment authorisation matrix — value bands, first and second authorisers, and the elevated band? | CFO / CEO | W3 build |
| Q-08 | Is the RTGS threshold policy set at the Bangladesh Bank minimum of BDT 100,000, or higher for cost reasons? | CFO | W3 build |
| Q-09 | What bank facilities exist today — overdraft, term loans, LC lines, guarantee lines — with what limits and covenants? | CFO | W3 minus 2 months |
| Q-10 | Which import flows use LCs and which use TT or open account? LC volume determines whether FR-TRE-041 stays P1 | CFO / Procurement | W3 design |
| Q-11 | Is technician and rider cash collection continuing at current volumes, or being reduced in favour of digital payment? The control design is the same but the volume assumption changes the counter-side effort | CFO / Operations Director | W3 design |
| Q-12 | Does the shift-open block need a documented emergency override for a genuine operational failure, and if so who holds it and how is it reported? | CFO / Operations Director | **W3 design — this is the most likely point of adoption resistance** |
| Q-13 | What minimum-balance and concentration policies apply per account? | CFO | W3 build |
| Q-14 | Who are the designated treasury authorisers, and what is the coverage plan for leave and absence? A dual-authorisation rule with two people and one on leave becomes an override culture | CFO / CEO | W3 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition), §4 (money flow), §5 (boundary map), §7 (cash
control across 51+ branches — the full control table), §8 (KPIs), §9 (delivery sequence), §10
(risks) · `M19_Financial_Accounting_and_General_Ledger.md` (posting engine, period close gate,
rate table, Category G CD block) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` (channel clearing model, receipt capture,
refund instruction) · `M52_Accounts_Payable_and_Employee_Expense.md` (payment instruction
authorisation) · `M51_Tax_and_Regulatory_Compliance_Bangladesh.md` (challan deposit, NID
threshold) · `M53_Revenue_Recognition_Commission_and_Settlement.md` (payout execution, escrow) ·
`M54_Cost_Accounting_Budgeting_and_FPA.md` (cash actuals and forecast input) ·
`03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md`
(shift, drawer and counter cash — the source of the shift contract) ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md`
(technician cash collection) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md`
(rider COD) ·
`03_Modules/E_Supply_Chain_and_Inventory/M44_Import_Trade_Compliance_and_Landed_Cost.md`
(the shipment an LC funds) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §6 SOD-12 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` BRU-FIN-02,
BRU-FIN-10 · `06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`
§2.7 (KPI-051), BO-06

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-004, BR-FIN-007,
BRU-FIN-02, §Process 6 (As-Is: cash reconciliation unreliable), §Month-End Close Day 1–3
(automated statement matching) · `1000FiX_Services_Company_Profile.md` §Service Infrastructure
(51+ centres), §Payment Options

**External benchmark**
[SAP S/4HANA Bank Account Management and Cash Management](https://sapinsider.org/articles/mastering-acdoca-7-essential-universal-journal-insights-for-sap-s-4hana-consultants-2025-edition/) —
centralised bank account master with signatory workflows and audit trail; real-time cash position;
short- and long-term forecasting · SAP Treasury & Risk Management — letters of credit and bank
guarantees as tracked instruments with limits and margins ·
[Oracle Fusion Cloud Cash Management](https://www.oracle.com/erp/financial-management/) —
multi-format statement import, configurable matching rules, external transactions as a
first-class category ·
[Microsoft Dynamics 365 Finance — Cash and Bank Management](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
multiple bank accounts, EFT/ACH/wire, positive pay, cheque management ·
[Treasury management system practice — cash forecasting and reconciliation automation](https://www.nomentia.com/blog/treasury-management-system) —
forecasts generated from AR/AP and ERP projections; reconciliation as an exception workflow ·
[Bangladesh Bank BD-RTGS System Rules](https://www.bb.org.bd/aboutus/regulationguideline/psd/rtgs_v1.2.pdf) —
minimum RTGS value of BDT 100,000 for high-value time-critical settlement ·
[Bangladesh Bank payment systems (BACH, BACPS, BEFTN)](https://www.bb.org.bd/en/index.php/financialactivity/paysystems) ·
[Bangladesh Bank PSD Circular 01/2025](https://www.bb.org.bd/mediaroom/circulars/psd/jan192025psd01e.pdf) ·
[SSLCOMMERZ settlement and reconciliation reporting](https://sslcommerz.com/payment-gateway/) and
[bKash merchant settlement](https://www.bkash.com/en/business/merchant) — T+1 to T+3 merchant
settlement cycles with fee deduction, the basis for the two-stage payment model ·
OCA `bank-statement-import`, `account-reconcile`, `account-payment-order`

---

*Module M50 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
