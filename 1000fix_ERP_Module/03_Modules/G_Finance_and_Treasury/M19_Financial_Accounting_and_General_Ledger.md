---
id: FIX-ERP2-M19
module_id: M19
module_code: FIN
module_name: Financial Accounting & General Ledger
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P0
wave: W3
---

# M19 — Financial Accounting & General Ledger
### Category G · Code `FIN` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M19 |
| **Module code** | `FIN` |
| **Category** | G — Finance & Treasury |
| **Status** | Existing (re-scoped in v2.1 — tax moved to M51, cash and banking to M50, fixed assets to M49, costing and budgeting to M54, revenue schedules to M53, payables to M52) |
| **Priority** | **P0** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` · L2 OCA `account-financial-tools`, `account-financial-reporting`, `account-fiscal-rule`, `mis-builder` · L5 custom posting engine, consolidation and close control |
| **Custom modules** | `cd_gl_ext`, `cd_subledger_posting`, `cd_multi_entity_consolidation`, `cd_financial_statements_bd`, `cd_close_checklist` |
| **Requirement range** | FR-FIN-001 … FR-FIN-046 |
| **Requirement count** | **46** *(measured — supersedes the 40 estimate in `02-02`)* |
| **Effort estimate** | **28 person-weeks** *(measured — supersedes the 24 PW estimate)* |
| **Depends on** | M29 Identity · M30 Platform Admin · M28 Integration · M64 MDM · M33 Party Master |
| **Depended on by** | M20, M50, M51, M52, M53, M49, M54, M15, M16, M21, M13, M14, M12, M25, M62, and every module that raises a financial consequence |

---

## 2. Purpose

M19 is **the book of record**. Every taka that 1000FiX earns, spends, holds, owes or writes
off ends its journey as a line in this ledger, and nothing becomes a financial fact until it
does. It is the single place where the Company's financial position can be stated, defended to
an auditor, and signed by the CFO.

The distinction that governs the whole of Category G is simple and absolute: **operational
modules raise events; only M19 creates journal entries.** M15 does not post the value of stock
it consumes — it declares that stock was consumed, and M19 decides what that means in the
accounts. M20 does not post revenue — it issues an invoice, and M19 records the receivable.
This one rule is what makes it possible to change a commercial model, a pricing scheme or a
service line without destabilising the ledger.

Today the Company's finance function collects fifty-one branch spreadsheets, consolidates them
by hand in Excel, and produces a profit-and-loss statement **fifteen to twenty days after
month-end**. By the time the number exists, the month it describes is history and the decisions
it should have informed have already been made. M19 exists to close that gap to three days and
to make the closing number one that nobody has to reconstruct.

### Why It Exists

1000FiX operates **fourteen distinct revenue streams** across service, contracts, rental,
refurbishment, marketplace, e-commerce, data services and managed services, from **51+ branches**,
under **Bangladesh statutory obligations** with a **July–June fiscal year**, and with the
expectation of a second legal entity and eventually a second country. A ledger that cannot
carry entity, branch, cost centre, business line and project as first-class dimensions cannot
answer the only question the board actually asks: *which parts of this business make money?*

The v2.0 draft compressed general ledger, tax, cash, assets, costing and revenue into two
modules. That design fails in a specific and predictable way: every time the commercial team
launches a new offer, the accounting logic for it has to be edited into the same code that
carries the statutory ledger, and the ledger becomes unstable in exactly the periods when it
must be most reliable. The v2.1 split makes M19 deliberately narrow and deliberately boring.

M19 is P0 and lands in Wave 3 with M20, M52 and M50, because a ledger without receivables,
payables and cash is not a ledger — it is a chart of accounts.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-001 | "Maintain a multi-branch chart of accounts with configurable structure per branch and cost center" |
| ERP BRD BR-FIN-008 | "Generate branch-wise P&L and consolidated financial statements" |
| ERP BRD BR-FIN-012 | "Support Bangladesh fiscal year (July–June) and period management" |
| ERP BRD BR-FIN-013 | "Maintain a complete, immutable audit trail for all financial transactions" |
| ERP BRD §Process 8 (As-Is) | "Finance team collects branch spreadsheets monthly → consolidates manually in Excel → produces P&L 15–20 days after month-end" |
| ERP BRD §Month-End Close | Days 1–5 close sequence: reconciliation, AP/AR ageing, accruals, draft P&L |
| ERP BRD NFR-022 | "Bangladesh NBR income tax computation compliance" |
| Business Objective BO-06 | Financial control and reporting objective, owner CFO |
| Business Objective BO-07 | Branch-level profitability visibility |
| Business Objective BO-18 | "Be ready to operate in a second country — time to stand up a country pack ≤ 12 weeks" |
| Exec Summary §6.2 | Financial close and cash flow benefit valued at **BDT 26 lac per year** (M19 with M20) |
| `_CATEGORY_OVERVIEW.md` §1 | "Other modules raise billable events and cost events. Only Category G creates journal entries." |
| `_CATEGORY_OVERVIEW.md` §8 | Month-end close 15–20 days → ≤ 3 days; audit adjustments < 0.5% of revenue |
| Bangladesh Companies Act / NBR | Seven-year retention of financial transactions (BRD §Data Retention) |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M19 is the module most at risk of absorbing everything
> that touches money. Six capability groups have been moved out and are claimed by the modules
> named below; both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Chart of accounts: structure, hierarchy, account types, governance and change control |
| 2 | The accounting dimension model: entity, branch/operating unit, cost centre, business line, project, brand, channel |
| 3 | Journal entries — manual, recurring, reversing, accrual, allocation-result and subledger-generated |
| 4 | **The subledger posting engine**: the rules that convert a business event into a journal entry |
| 5 | Fiscal calendar, period open/close/hard-close, and the July–June Bangladesh fiscal year |
| 6 | The month-end and year-end close process, checklist, task ownership and sign-off |
| 7 | Multi-entity accounting: separate books per legal entity with a common chart |
| 8 | Intercompany transactions, balancing and elimination |
| 9 | Consolidation: entity roll-up, minority interest, consolidated statements |
| 10 | Multi-currency: transaction currency, functional currency, rate tables, translation and revaluation |
| 11 | Trial balance, general ledger enquiry, account analysis and drill-down to source transaction |
| 12 | Statutory financial statements: balance sheet, profit and loss, cash flow statement, statement of changes in equity, notes |
| 13 | Management reporting structures and reporting hierarchies over the chart |
| 14 | Opening balances, year-end closing entries and retained-earnings roll-forward |
| 15 | The immutable financial audit trail and the evidence pack for the external auditor |
| 16 | Financial data retention to the statutory seven years |
| 17 | Accrual and provision framework (the mechanism; the amounts come from the owning module) |
| 18 | Suspense, clearing and control-account management with mandatory reconciliation |
| 19 | Ledger-level segregation of duties and posting authority |
| 20 | Financial period reconciliation between every subledger and its control account |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Customer invoice creation, receipt capture, ageing, dunning, credit notes | **M20** Receivables | Invoicing is an operational lifecycle with its own states; M19 records the receivable it produces |
| Vendor invoice, three-way match, payment run, staff expense claims | **M52** Payables & Expense | Paying is a lifecycle with approval, matching and banking; M19 records the payable |
| Bank accounts, balances, statement import, reconciliation, cash position, cash forecasting, LC and facilities | **M50** Treasury & Cash | The bank position is a treasury discipline; M19 posts the result |
| Branch counter cash, shift float, drawer operation | **M04** Branch Operations (position consolidated by **M50**) | Cash handling happens at the counter, not in the ledger |
| VAT, Mushak forms and registers, VAT return, TDS/VDS, challans, certificates, income-tax schedules | **M51** Tax & Regulatory | Tax is statutory, changes annually, and must be a country pack rather than ledger code |
| Revenue schedules, deferral, performance obligations, commission ledgers, seller and partner payouts, escrow | **M53** Revenue & Settlement | Revenue timing is a contract question; M19 posts the release M53 computes |
| Asset register, capitalisation, depreciation calculation, disposal, CWIP, impairment, capital approval | **M49** Fixed Assets | The register is an operational estate; M19 posts depreciation and carrying value |
| Cost allocation cycles, job and contract costing, budgets, variance analysis, forecasting, business-line profitability | **M54** Costing & FP&A | Management accounting is a separate discipline built *over* the ledger |
| Pricing, rate cards, discount policy | **M11** Pricing (Category C) | What to charge is a commercial decision, never an accounting one |
| Recurring billing schedule, proration, subscription cycles | **M39** Subscription & Recurring Billing (Category C) | The schedule is commercial; M20 issues the invoice; M19 posts it |
| Inventory quantity, ownership class and valuation calculation | **M15** Inventory | M15 computes value and raises the event; M19 posts it |
| Landed-cost calculation | **M44** Import & Landed Cost | Computed once, upstream, and consumed by M15 and M19 |
| Payroll calculation, statutory deductions, payslips | **M21** HR & Payroll | M21 computes; M19 posts the payroll journal |
| Financial dashboards and executive analytics | **M25** Business Intelligence (Category J) | M19 supplies certified data; M25 presents it |
| Document storage and e-signature of financial evidence | **M24** Document & Records | M19 references documents; it does not store them |

### 3.3 Shared Concepts

| Concept | M19's Role | Owning Module |
|---|---|---|
| Chart of accounts | **Owns** — the defining artefact of this module | M19 |
| Accounting dimensions | **Owns** the dimension model; M64 governs the master values | M19 / M64 |
| Legal entity, branch, cost centre | Owns the accounting treatment; M30 owns the operational definition | M19 / M30 |
| Fiscal period | **Owns** — every module's cut-off derives from it | M19 |
| Journal entry | **Owns** — no other module may create one | M19 |
| Posting rule | **Owns** the engine; each subledger declares its event contract | M19 |
| Receivable balance | Owns the control account; M20 owns the open-item detail | M19 / M20 |
| Payable balance | Owns the control account; M52 owns the open-item detail | M19 / M52 |
| Bank balance | Owns the GL account; M50 owns the bank position and reconciliation | M19 / M50 |
| Tax balance | Owns the GL account; M51 owns the return, the register and the liability | M19 / M51 |
| Deferred revenue balance | Owns the control account; M53 owns the schedule | M19 / M53 |
| Asset carrying value | Owns the control account; M49 owns the register | M19 / M49 |
| Budget | Reads for variance reporting; does not own | M54 |
| Exchange rate | Owns the accounting rate table; M50 supplies the treasury rate | M19 / M50 |
| Audit trail | Owns the financial trail; M29 owns the platform-wide trail | M19 / M29 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA Finance — Universal Journal (ACDOCA)** | A single line-item table merging FI, CO, asset accounting and material ledger, removing FI↔CO reconciliation and letting reports read live line detail | **The single-journal principle is the most influential external reference for M19.** One posting table carrying every accounting and management dimension on the same line, so that there is exactly one number and no reconciliation between the statutory ledger and the management view. M54's costing reads the same lines M19 posts | SAP's ledger/ledger-group parallel-valuation apparatus and the extension-ledger concept — disproportionate for one accounting framework and two entities |
| **SAP S/4HANA — document splitting and multi-dimensional balancing** | Automatic splitting of a document so that a balance sheet can be produced per segment/profit centre | **Adopted in principle**: every balance-sheet posting carries entity and branch, so a branch balance sheet is derivable and intercompany is balanced automatically | Full configurable splitting characteristics; we fix the split dimensions to entity and operating unit |
| **Oracle Fusion Cloud Financials — Subledger Accounting (SLA)** | A rules-based engine that transforms subledger transactions into journal entries, preserving traceability from balance sheet to source transaction | **The single most important design borrowing.** M19's posting engine is an SLA-equivalent: subledgers publish typed events, and *accounting rules held in M19* decide the accounts, dimensions and timing. Changing how a revenue stream is accounted is a rule change in M19, not a code change in M20 | Oracle's full rule-authoring surface (journal line types, account derivation rules, supporting references) — we ship a constrained rule grammar and version it |
| **Oracle Fusion Cloud — General Ledger** | Cross-validation rules, intercompany balancing, allocations, revaluations, consolidation across ledgers | Cross-validation of dimension combinations, automatic intercompany balancing lines, period-end revaluation and translation | Oracle's ledger-set/reporting-currency depth; one reporting currency (BDT) with USD as a transaction currency is sufficient |
| **Microsoft Dynamics 365 Finance — General Ledger & financial dimensions** | Financial dimensions as configurable, reportable attributes on every posting; dimension sets; period close workspace | **The financial-dimension model**: dimensions are attributes of the line, not segments crammed into an account code. Our account code stays short and readable; entity, branch, cost centre, business line, project, brand and channel are dimensions. Also adopted: the close workspace as a task list with ownership and status | The unlimited-dimension configuration surface; we fix seven dimensions and require architecture-board approval to add an eighth |
| **IFS Cloud — Financials** | Multi-company with shared basic data, project-driven accounting for a service business | The service-business posture: a job/work order is a natural accounting object, and project/contract is a standing dimension rather than an add-on | IFS's project-accounting depth — M54 covers what we need |
| **NetSuite / Sage Intacct — multi-entity close** | Continuous close, entity roll-up, intercompany automation, close checklist with sign-off | **The close checklist as a system object** with named owners, dependencies, evidence attachment and an auditable sign-off — this is what turns a 15-day close into a 3-day close | Their consolidation-currency machinery beyond what a two-entity BDT group needs |
| **Odoo 19 CE `account` + OCA `account-financial-tools` / `account-financial-reporting` / `mis-builder`** | Journals, entries, reconciliation, analytic accounting, lock dates, trial balance, general ledger and aged-partner reports, MIS report builder | The transactional substrate. OCA `account_lock_date_update` and `account_journal_lock_date` (independent journal locking) are adopted as-is and are the mechanism behind our hard-close rule; `account_financial_report` supplies trial balance and GL reports; `mis-builder` supplies statement layouts | Odoo's analytic-account model as the primary dimension carrier — too weak for seven dimensions with cross-validation; extended in `cd_gl_ext` |
| **Bangladesh statutory practice (Companies Act 1994, IFRS as adopted / IAS-BFRS)** | July–June fiscal year, statutory statement formats, seven-year retention, audit evidence expectations | Fiscal calendar, statement formats and retention as configuration in a country pack, not as code | — |

**Design position.** Four deliberate positions.

First, **the posting engine lives in M19 and nowhere else**. This is the architectural
commitment that the whole category rests on. Fourteen revenue streams will change; some will be
retired and others invented. If each one carries its own posting logic, the ledger becomes an
aggregate of fourteen partly-maintained accounting opinions. Instead, every subledger publishes
a typed, versioned event, and M19 holds the rule that turns it into debits and credits. The
commercial team can launch an offer without a finance release.

Second, **dimensions are attributes, not account segments**. The temptation in Bangladeshi
practice is a long segmented account code — entity-branch-department-account. It produces a
chart with tens of thousands of combinations that nobody can maintain, and it makes adding a
business line a chart-restructuring exercise. We follow Dynamics: a short chart, seven
dimensions, and cross-validation rules that prevent nonsense combinations.

Third, **we close continuously, not monthly**. Subledger events post daily. The month-end close
is a *verification* exercise — reconcile, accrue, review, sign — not a data-entry exercise. This
is the only way a 51-branch business gets to a three-day close, and it is why the close
checklist is a first-class system object with named owners rather than a Word document.

Fourth, **manual journals are an exception, and are treated as one**. Every manual journal
requires a reason, supporting evidence and an approver who is not the preparer, and manual
journals as a proportion of total postings is a reported control metric. In a well-configured
ledger this number should fall towards zero; if it does not, the posting rules are wrong and
that is the signal we want.

---

## 5. Functional Areas & Features

### 5.1 Chart of Accounts & Dimension Model

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-001 | Chart of accounts | Maintain a single group chart of accounts with account code, name (English and Bengali), type, nature, parent, and permitted dimension set, shared across all legal entities (BR-FIN-001) | **P0** | L1/L5 |
| FR-FIN-002 | Account governance | Require an approval workflow to create, deactivate or reclassify an account, and prevent deletion of any account that has ever carried a posting | **P0** | L5 |
| FR-FIN-003 | Dimension model | Carry seven accounting dimensions on every journal line — legal entity, operating unit (branch), cost centre, business line, project/contract, brand, channel — with per-account rules for which are mandatory, optional or forbidden | **P0** | L5 |
| FR-FIN-004 | Cross-validation rules | Reject a dimension combination that violates a configured validity rule (for example, a rental-revenue account with a repair business line) | **P0** | L5 |
| FR-FIN-005 | Reporting hierarchies | Support multiple independent roll-up hierarchies over the same chart — statutory, management, tax and board reporting — without duplicating accounts | P1 | L2/L5 |
| FR-FIN-006 | Control accounts | Designate control accounts whose balance may be changed only by their owning subledger, and block direct manual posting to them | **P0** | L5 |
| FR-FIN-007 | Chart versioning | Retain a full history of chart and dimension changes with effective dates, so a prior period's statements remain reproducible | P1 | L5 |

### 5.2 Journal Entries & the Posting Engine

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-008 | Subledger posting engine | Convert every typed financial event published by a subledger module into a balanced journal entry, using versioned posting rules held in M19, and return the resulting entry reference to the source module | **P0** | L5 |
| FR-FIN-009 | Posting rule management | Allow a posting rule to be authored, tested against sample events, approved, versioned and activated with an effective date, without a code release | **P0** | L5 |
| FR-FIN-010 | Posting rule traceability | Record, on every generated entry, the rule and rule version that produced it, the source event and the source document | **P0** | L5 |
| FR-FIN-011 | Manual journal entry | Permit a manual journal with mandatory narrative, reason code, supporting document reference and an approver who is not the preparer | **P0** | L1/L5 |
| FR-FIN-012 | Recurring journals | Define recurring journal templates with a schedule, generate them for review, and post on approval | P1 | L1/L2 |
| FR-FIN-013 | Accrual and reversal | Post accrual entries flagged for automatic reversal on a nominated date, and evidence the reversal against the original | **P0** | L1/L5 |
| FR-FIN-014 | Journal import | Accept a validated bulk journal import with full pre-validation, all-or-nothing rejection, and the same approval controls as manual entry | P1 | L2 |
| FR-FIN-015 | Balanced-entry enforcement | Reject any entry that does not balance by legal entity and by the balancing dimension set, generating intercompany balancing lines where required | **P0** | L5 |
| FR-FIN-016 | Entry immutability | Prevent modification or deletion of a posted entry; corrections are made only by a reversing or adjusting entry that references the original | **P0** | L5 |
| FR-FIN-017 | Draft and review queue | Hold generated and imported entries in a reviewable draft state where the posting rule declares review is required, with an ageing alert on unreviewed drafts | P1 | L5 |

### 5.3 Fiscal Calendar, Period Control & Close

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-018 | Fiscal calendar | Support the Bangladesh **July–June fiscal year** with twelve monthly periods plus adjustment periods, per legal entity, with configurable period naming (BR-FIN-012) | **P0** | L1/L5 |
| FR-FIN-019 | Period states | Manage period state as open → soft-closed (subledger postings blocked, finance adjustments permitted) → hard-closed (no posting) → reopened (CFO-approved and logged) | **P0** | L2/L5 |
| FR-FIN-020 | Close blocking conditions | Prevent a period close while unposted entries, unreviewed drafts, unreconciled control accounts or incomplete close tasks exist in it (BRU-FIN-05) | **P0** | L5 |
| FR-FIN-021 | Close checklist | Maintain the month-end and year-end close as a structured task list with named owners, dependencies, target times, evidence attachment, status and sign-off | **P0** | L5 |
| FR-FIN-022 | Subledger reconciliation | Reconcile every subledger (AR, AP, inventory, fixed assets, tax, deferred revenue, cash) to its GL control account as a mandatory close step, and report any difference before the period may close | **P0** | L5 |
| FR-FIN-023 | Year-end close | Execute year-end: close income and expense accounts to retained earnings, roll balances forward, open the new year, and lock the closed year | **P0** | L1/L5 |
| FR-FIN-024 | Close performance tracking | Measure and report elapsed time per close task and per close cycle against the ≤ 3-day target | P1 | L5 |
| FR-FIN-025 | Soft-close for reporting | Produce a management position at any point mid-period without closing the period | P1 | L5 |

### 5.4 Multi-Entity, Intercompany & Consolidation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-026 | Multi-entity books | Maintain a complete, independently closeable set of books per legal entity on a shared chart and shared dimension model | **P0** | L1/L5 |
| FR-FIN-027 | Entity data isolation | Enforce that a user may view or post to only the entities their role permits, with no cross-entity leakage in any report or API response | **P0** | L5 |
| FR-FIN-028 | Intercompany transactions | Record a transaction between two group entities as balanced entries in both, with automatic intercompany receivable/payable generation and a shared reference | P1 | L5 |
| FR-FIN-029 | Intercompany reconciliation | Report intercompany balances by pair and flag any mismatch before consolidation | P1 | L5 |
| FR-FIN-030 | Consolidation | Produce consolidated statements across entities with elimination of intercompany balances and transactions, and an auditable elimination register | P1 | L5 |
| FR-FIN-031 | Branch-level statements | Produce a complete profit and loss and a derivable balance sheet per branch and per business line from the dimension model, without a separate branch ledger (BR-FIN-008) | **P0** | L5 |

### 5.5 Multi-Currency

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-032 | Currency model | Record every transaction in its transaction currency and in the entity's functional currency (BDT), retaining both amounts and the rate applied | **P0** | L1 |
| FR-FIN-033 | Rate tables | Maintain dated exchange-rate tables by rate type (spot, average, closing, statutory/customs), sourced from M50 and from Bangladesh Bank, with manual override under approval | **P0** | L5 |
| FR-FIN-034 | Revaluation | Revalue foreign-currency monetary balances at period end at the closing rate and post the unrealised gain or loss (BRU-FIN-07) | **P0** | L1/L5 |
| FR-FIN-035 | Realised gain/loss | Compute and post realised exchange differences on settlement of a foreign-currency receivable or payable | **P0** | L1 |
| FR-FIN-036 | Warranty claim currency | Support brand-partner warranty claims raised in USD at the rate prevailing on the date of service completion, with the resulting exposure visible until settlement (BRU-FIN-07 of the BRD) | P1 | L5 |

### 5.6 Reporting, Enquiry & Audit Trail

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FIN-037 | Trial balance | Produce a trial balance at any date, for any entity and any dimension combination, with opening, movement and closing columns | **P0** | L2 |
| FR-FIN-038 | Statutory statements | Produce the balance sheet, profit and loss, cash flow statement, statement of changes in equity and supporting notes in the statutory Bangladesh format, for any entity and consolidated | **P0** | L2/L5 |
| FR-FIN-039 | Drill-down | Allow any reported figure to be drilled from statement → account → journal line → source document, in every report and dashboard | **P0** | L5 |
| FR-FIN-040 | GL enquiry | Provide an account enquiry filterable by every dimension, period, source module, document type and preparer, exportable to Excel | **P0** | L2 |
| FR-FIN-041 | Immutable audit trail | Record, for every posting, the actor, timestamp, source, rule version, approver, IP and prior state, in a tamper-evident store retained for seven years (BR-FIN-013) | **P0** | L5 |
| FR-FIN-042 | Auditor evidence pack | Generate, on request, a period evidence pack: trial balance, subledger reconciliations, manual journal register with approvals, control-account movements and close sign-offs | P1 | L5 |
| FR-FIN-043 | Read-only external auditor access | Provide a scoped, read-only, time-limited external-auditor role with full drill-down and no posting capability | P1 | L5 |
| FR-FIN-044 | Certified data feed | Publish a certified, period-stamped ledger extract to M62/M25 so that all financial reporting derives from one source | **P0** | L5 |
| FR-FIN-045 | Opening balance load | Load and prove migrated opening balances, with a reconciliation report signed by the CFO before cutover | **P0** | L5 |
| FR-FIN-046 | Retention and archival | Retain financial transactions and their evidence for seven years, with archived periods remaining queryable (BRD §Data Retention) | **P0** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Single posting table with full dimensionality** | Every journal line carries all seven dimensions plus source-event metadata on the same row. No aggregate table is the source of any figure; all reports read line detail. This is the ACDOCA principle applied at our scale |
| T-02 | **Monetary type discipline** | All amounts use `Monetary` with an explicit currency; no floating-point arithmetic anywhere in the posting path (AS-10). Rounding is applied once, at a declared point, with the rounding difference posted to a named account |
| T-03 | **Append-only ledger** | Posted journal lines are insert-only. There is no update path and no delete path in the application, the API or the database role used by the application (AS-08 outbox, plus a `REVOKE UPDATE, DELETE` grant on posting tables) |
| T-04 | **Idempotent event consumption** | Every subledger event carries an idempotency key; replay after a network or broker failure must not produce a second journal entry. Duplicate detection is at the persistence layer, not the handler |
| T-05 | **Posting rule engine** | Rules are declarative, versioned records — event type, condition, debit/credit line specifications, dimension derivation — evaluated deterministically. Every rule has a test fixture, and rule activation requires the fixture to pass |
| T-06 | **Deterministic reproducibility** | Re-running the posting engine over the same event stream with the same rule versions produces byte-identical entries. This is the property that makes a restatement provable rather than argued |
| T-07 | **Period-lock enforcement at the data layer** | The period state check is enforced in the posting service and again as a database constraint; no API path, import path or administrative path can post into a hard-closed period |
| T-08 | **Close performance envelope** | Trial balance for a full year across all entities returns in ≤ 5 s; a statutory statement pack generates in ≤ 60 s; drill-down from statement line to source document resolves in ≤ 2 s |
| T-09 | **Transaction volume envelope** | ~250,000 service jobs/year, 51+ branches, 14 revenue streams → an estimated **3.5–5 million journal lines per year**. The posting table is partitioned by fiscal year and entity, with covering indexes on (entity, period, account) and (source_doc_type, source_doc_id) |
| T-10 | **Backdated posting control** | A posting whose effective date falls in an open prior period is permitted but flagged, counted and reported; a posting into a soft-closed period requires the finance-adjustment role |
| T-11 | **Event contract versioning** | Each subledger event has a versioned schema registered in M28. A schema change requires a corresponding posting-rule version; the engine refuses an unmapped schema version rather than guessing |
| T-12 | **Multi-entity isolation** | Every ledger record carries `company_id`; record rules and API scoping enforce entity isolation, verified by an automated cross-entity leakage test in CI (AS-03) |
| T-13 | **Tamper-evident audit store** | Audit records are hash-chained per period so that any retrospective alteration is detectable; the period hash is included in the close sign-off record |
| T-14 | **Timezone and date discipline** | Timestamps stored UTC, presented Asia/Dhaka (AS-11); the *accounting date* is a distinct field from the *system timestamp* and is the only date that determines period assignment |
| T-15 | **Bengali statement rendering** | Account names, statement captions and note text render in Bengali as well as English, including Bengali numerals where the statutory format requires them (AS-12) |
| T-16 | **Archive queryability** | Periods older than the online retention window move to a partitioned archive that remains queryable through the same enquiry API, with a documented restore path for the full seven years |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M19 |
|---|---|---|
| **CFO** | Signs a P&L produced 15–20 days late from 51 spreadsheets, and cannot fully evidence how it was built | Signs a statement closed in ≤ 3 days, every line of which drills to a source document |
| **Finance Manager** | Spends the first two weeks of every month collecting and re-keying | Spends them reviewing exceptions; collection and keying have disappeared |
| **Finance Officer** | Types journals from branch summaries | Reviews rule-generated postings and investigates the few that fail validation |
| **Branch Manager** | Has no reliable view of their branch's result until it is history | Sees their branch P&L live, on the same numbers head office sees |
| **Operations Director** | Argues about which branch numbers are right | Argues about what to do, because the numbers are not in dispute |
| **External auditor** | Requests schedules that are rebuilt by hand, and raises adjustments | Uses a read-only role, drills to source, and finds the reconciliations already done |
| **CEO / Board** | Receives a management pack assembled manually, one version per meeting | Receives one certified set of numbers, the same ones the system reports continuously |
| **Every operational module owner** | Must think about accounting when designing a feature | Publishes an event and stops thinking about accounting |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Financial close and cash-flow control** | Close cycle 15–20 days → ≤ 3 days; decisions taken on current rather than historical data | **BDT 26 lac per year** at steady state (Exec Summary §6.2, M19 with M20) |
| **Administrative labour released** | Manual consolidation, re-keying and schedule preparation eliminated across the finance team | A material share of the **BDT 62 lac** cross-module administrative saving |
| **Audit cost and risk reduction** | Reconciliations complete before the auditor arrives; evidence pack generated, not assembled | Audit adjustments < 0.5% of revenue; shorter audit fieldwork |
| **Branch accountability** | A branch P&L that the branch manager cannot dispute, available continuously | Precondition for BO-07 and for the entire M54 profitability programme |
| **Business-line visibility** | Fourteen revenue streams separable by dimension from day one | Prevents the classic failure where a new business line's profitability is unknown for two years |
| **Regulatory penalty avoidance** | A ledger that supports M51's returns with reconciled, evidenced figures | Supports the **zero tax compliance findings** target |
| **Second-entity and second-country readiness** | A new entity is configuration on a shared chart, not a new system | Supports BO-18: country pack stood up in ≤ 12 weeks |
| **Working-capital decisions** | Receivable, payable and cash positions are accurate daily rather than monthly | Enables the DSO and cash-forecast targets owned by M20 and M50 |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **A defensible book of record** | The Company can prove any number to any third party — auditor, NBR, bank, brand partner, potential investor — without reconstruction. This is the difference between a business that can raise finance and one that cannot |
| **ISO 9001 and ISMS conformance** | Documented, controlled, auditable financial processes with evidence retention support the certification 1000FiX markets as a differentiator |
| **Institutional memory** | The ledger stops depending on which finance officer knows how last year's numbers were built |
| **Fraud deterrence** | Immutability, approval separation, control-account protection and a hash-chained trail change what is possible, not merely what is discouraged |
| **Governance maturity** | A board that receives one certified set of numbers governs differently from one that receives a manually assembled pack |
| **Foundation for every other finance module** | M20, M50, M51, M52, M53, M49 and M54 all terminate here. None of them can be trusted if M19 is not |
| **Statutory continuity** | Seven-year queryable retention means a Companies Act or NBR enquiry about a prior year is answered, not researched |

---

## 8. Lifecycle & State Models

### 8.1 Journal Entry Lifecycle

```
   SUBLEDGER EVENT              MANUAL ENTRY
         │                           │
         ▼                           ▼
   ┌───────────┐              ┌───────────┐
   │ GENERATED │              │   DRAFT   │
   │ (by rule) │              │ (prepared)│
   └─────┬─────┘              └─────┬─────┘
         │                          │
         │ rule requires review     │ submitted
         ├──────────► ┌─────────────▼──────┐
         │            │   PENDING APPROVAL │
         │            └─────┬─────────┬────┘
         │        approved  │         │ rejected
         │                  │         └──────► RETURNED TO PREPARER
         ▼                  ▼
      ┌──────────────────────────┐
      │         POSTED           │   ◄── immutable from this point
      └───────────┬──────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
 ┌──────────┐          ┌─────────────┐
 │ REVERSED │          │  ARCHIVED   │  (period > online retention)
 │ (by new  │          │ queryable   │
 │  entry)  │          └─────────────┘
 └──────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Generated | A subledger event matches an active posting rule | System (posting engine) |
| — | Draft | A manual journal is prepared with narrative and reason code | Finance Officer |
| Generated | Posted | Rule does not require review, period is open, entry balances | System |
| Generated | Pending approval | Rule requires review, or amount exceeds the review threshold | System |
| Draft | Pending approval | Preparer submits with supporting document attached | Finance Officer |
| Pending approval | Posted | Approved by a user other than the preparer, within authority (BRU-FIN-11) | Finance Manager / CFO |
| Pending approval | Returned | Rejected with a reason | Finance Manager / CFO |
| Posted | Reversed | A reversing entry is posted referencing the original; the original itself is never altered | Finance Manager |
| Posted | Archived | Period passes the online retention window | System |

### 8.2 Fiscal Period Lifecycle

```
   ┌────────┐  period start   ┌────────┐  subledger cut-off  ┌─────────────┐
   │ FUTURE │────────────────►│  OPEN  │────────────────────►│ SOFT-CLOSED │
   └────────┘                 └────────┘                     └──────┬──────┘
                                   ▲                                │
                        CFO-approved│reopen                          │ all close tasks
                        (logged,    │                                │ signed off
                        exceptional)│                                ▼
                              ┌─────┴──────┐                  ┌─────────────┐
                              │ RE-OPENED  │◄─────────────────│ HARD-CLOSED │
                              └────────────┘                  └──────┬──────┘
                                                                     │ year-end
                                                                     ▼
                                                              ┌─────────────┐
                                                              │ YEAR LOCKED │
                                                              └─────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Future | Open | Prior period at least soft-closed; calendar permits | System / Finance Manager |
| Open | Soft-closed | Subledger cut-off reached; no unposted subledger events remain | Finance Manager |
| Soft-closed | Hard-closed | Every close-checklist task signed off; every control account reconciled; no unreviewed drafts (BRU-FIN-05) | CFO |
| Hard-closed | Re-opened | CFO approval with recorded reason; event logged and reported to the audit committee (BRU-FIN-06) | CFO |
| Re-opened | Hard-closed | Adjustments posted and re-signed | CFO |
| Hard-closed | Year locked | Year-end close executed, retained earnings rolled, statements signed | CFO |

### 8.3 Posting Rule Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Draft | Authored, not evaluable | Test fixture attached |
| Tested | Executed against sample events with expected output | All fixture cases pass |
| Approved | Reviewed by CFO or delegate | Effective date set |
| Active | In use by the posting engine | Superseded by a new version, or expired |
| Superseded | Replaced by a later version | Retained permanently — prior entries reference it |

> A posting rule is **never edited in place**. A change creates a new version with a new
> effective date. This is what allows a prior period's entries to be explained by the rule that
> actually produced them.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

BRU-FIN-01 … BRU-FIN-10 are the canonical Category G rules held in
`05_Cross_Cutting_Specifications/05-05` §Finance. M19 **enforces** those marked *M19* below and
**hosts the control account** for those enforced elsewhere. BRU-FIN-11 onward are new in this
specification.

| ID | Rule | Class | Enforced By | Owner |
|---|---|:--:|---|---|
| BRU-FIN-01 | Every customer invoice includes VAT at the applicable rate and displays the Company's BIN | **H** | M20 / M51 | CFO |
| BRU-FIN-02 | Cash receipts above BDT 50,000 require the customer's NID to be recorded | **H** | M50 / M51 | CFO |
| BRU-FIN-03 | A payment cannot be recorded against a cancelled invoice | **H** | M20 | Finance Manager |
| BRU-FIN-04 | A credit note requires approval by the Finance Manager or above | **H** | M20 | CFO |
| BRU-FIN-05 | A financial period cannot be closed while unposted entries exist in it | **H** | **M19** | CFO |
| BRU-FIN-06 | Once a period is hard-closed, no posting to it is possible without CFO-approved reopening, which is logged | **H** | **M19** | CFO |
| BRU-FIN-07 | Foreign-currency balances are revalued at period end at the official rate | **C** | **M19** | Finance Manager |
| BRU-FIN-08 | Marketplace transactions are accounted per the declared principal-or-agent model; the model cannot vary by transaction | **H** | M51 / M53 | CFO |
| BRU-FIN-09 | TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise | **H** | M51 / M52 | CFO |
| BRU-FIN-10 | Branch cash must be reconciled and closed daily; an unclosed shift blocks the next shift's opening | **H** | M04 / M50 | Finance Manager |
| BRU-FIN-11 | A journal entry cannot be approved by the user who prepared it, at any value | **H** | **M19** | CFO |
| BRU-FIN-12 | A posted journal entry can never be modified or deleted; correction is only by a referencing reversal or adjustment | **H** | **M19** | CFO |
| BRU-FIN-13 | Only the owning subledger may post to its control account; direct manual posting to a control account is blocked | **H** | **M19** | CFO |
| BRU-FIN-14 | Every journal line carries a legal entity and an operating unit; there is no unassigned value | **H** | **M19** | CTO |
| BRU-FIN-15 | A journal entry must balance within each legal entity; cross-entity entries generate intercompany balancing lines automatically | **H** | **M19** | Finance Manager |
| BRU-FIN-16 | A manual journal requires a reason code, a narrative and a supporting document reference | **H** | **M19** | Finance Manager |
| BRU-FIN-17 | A posting rule may be activated only after its test fixture passes and it is approved by the CFO or delegate | **H** | **M19** | CFO |
| BRU-FIN-18 | A posting rule is versioned and never edited in place; every posted entry references the rule version that produced it | **H** | **M19** | CTO |
| BRU-FIN-19 | The fiscal year runs July to June; period boundaries are not configurable per branch or per business line | **H** | **M19** | CFO |
| BRU-FIN-20 | Every subledger must reconcile to its control account before the period may be hard-closed; an unexplained difference blocks the close | **H** | **M19** | CFO |
| BRU-FIN-21 | An account that has ever carried a posting cannot be deleted; it may only be deactivated | **H** | **M19** | Finance Manager |
| BRU-FIN-22 | A dimension combination that violates an active cross-validation rule is rejected at posting, including via API and import | **H** | **M19** | Finance Manager |
| BRU-FIN-23 | Backdated postings into an open prior period are permitted, flagged, counted and reported monthly to the CFO | **S** | **M19** | Finance Manager |
| BRU-FIN-24 | Financial records are retained for seven years and remain queryable throughout | **H** | **M19** | CFO |
| BRU-FIN-25 | A user with journal-posting rights may not also administer posting rules (SOD extension) | **H** | **M19** | CFO |
| BRU-FIN-26 | External auditor access is read-only, time-limited, scoped to nominated entities and periods, and fully logged | **H** | **M19** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.gl.account` | `fix_gl_account` | Chart of accounts | code, name_en, name_bn, type, nature, parent_id, is_control_account, control_owner_module, permitted_dimensions, mandatory_dimensions, active_from, active_to |
| `fix.gl.dimension` | `fix_gl_dimension` | Dimension definition | code, name, source_model, is_mandatory_default, validation_scope |
| `fix.gl.dimension.value` | `fix_gl_dimension_value` | Permitted values per dimension | dimension_id, value_code, name, parent_id, entity_scope, active_from, active_to |
| `fix.gl.crossvalidation.rule` | `fix_gl_crossvalidation_rule` | Prohibited/required combinations | name, condition_json, effect (allow/deny/require), severity, active_from |
| `fix.gl.hierarchy` | `fix_gl_hierarchy` | Reporting roll-up structures | name, purpose (statutory/management/tax/board), root_node, version |
| `fix.gl.journal` | `fix_gl_journal` | Journal register | code, name, type (sales/purchase/cash/bank/general/opening/closing/adjustment), entity_id, sequence, lock_date |
| `fix.gl.entry` | `fix_gl_entry` | Journal entry header | reference, journal_id, entity_id, accounting_date, period_id, state, source (rule/manual/import), source_event_id, posting_rule_version_id, narrative, reason_code, prepared_by, approved_by, reversal_of_id, document_refs |
| `fix.gl.line` | `fix_gl_line` | **The ledger line — the single source of every figure** | entry_id, account_id, debit, credit, currency, amount_currency, fx_rate, entity_id, operating_unit_id, cost_center_id, business_line_id, project_id, brand_id, channel_id, partner_id, source_doc_type, source_doc_id, description |
| `fix.gl.posting.rule` | `fix_gl_posting_rule` | Event → entry rule | event_type, event_schema_version, condition_json, line_specs_json, dimension_derivation_json, requires_review, version, state, effective_from, approved_by |
| `fix.gl.posting.rule.fixture` | `fix_gl_posting_rule_fixture` | Rule test case | rule_id, sample_event_json, expected_lines_json, last_run_at, last_result |
| `fix.gl.event.inbox` | `fix_gl_event_inbox` | Consumed subledger events | source_module, event_type, schema_version, idempotency_key, payload_json, received_at, processed_at, entry_id, state, error |
| `fix.fiscal.year` | `fix_fiscal_year` | July–June year | entity_id, name, date_from, date_to, state |
| `fix.fiscal.period` | `fix_fiscal_period` | Period | fiscal_year_id, sequence, date_from, date_to, state, soft_closed_at, hard_closed_at, reopened_by, reopen_reason, period_hash |
| `fix.close.checklist` | `fix_close_checklist` | Close run | period_id, entity_id, type (month/year), started_at, completed_at, elapsed_hours, signed_off_by |
| `fix.close.task` | `fix_close_task` | One close step | checklist_id, sequence, name, owner_role, depends_on_task_id, target_hours, state, evidence_doc_ids, completed_by, completed_at |
| `fix.subledger.reconciliation` | `fix_subledger_reconciliation` | Control-account proof | period_id, subledger_module, control_account_id, subledger_balance, gl_balance, difference, explanation, state, signed_off_by |
| `fix.gl.recurring.template` | `fix_gl_recurring_template` | Recurring journal | name, journal_id, line_specs_json, schedule_rule, next_run, auto_post, active |
| `fix.gl.accrual` | `fix_gl_accrual` | Accrual with reversal | entry_id, reverse_on_date, reversal_entry_id, source_module, basis_description |
| `fix.currency.rate` | `fix_currency_rate` | Dated rates | currency, rate_type (spot/average/closing/statutory), rate_date, rate, source, entered_by, approved_by |
| `fix.fx.revaluation` | `fix_fx_revaluation` | Period-end revaluation run | period_id, entity_id, accounts, rate_used, unrealised_gain, unrealised_loss, entry_id |
| `fix.intercompany.transaction` | `fix_intercompany_transaction` | Cross-entity pair | from_entity_id, to_entity_id, shared_reference, amount, from_entry_id, to_entry_id, state, reconciled_at |
| `fix.consolidation.run` | `fix_consolidation_run` | Consolidated close | period_id, entities, state, elimination_entry_ids, generated_at, approved_by |
| `fix.consolidation.elimination` | `fix_consolidation_elimination` | Elimination line | run_id, rule, account_id, entity_pair, amount, basis |
| `fix.financial.statement` | `fix_financial_statement` | Statement definition and output | type (BS/PL/CF/SOCE), format_version, entity_scope, period_id, layout_json, generated_at, generated_by, document_id |
| `fix.gl.audit.record` | `fix_gl_audit_record` | Tamper-evident trail | entry_id, action, actor_id, occurred_at, ip, before_state_hash, after_state_hash, chain_hash |
| `fix.auditor.access.grant` | `fix_auditor_access_grant` | External auditor scope | party_id, entities, periods, granted_by, valid_from, valid_to, access_log_ref |
| `fix.opening.balance.load` | `fix_opening_balance_load` | Migration control | entity_id, as_at_date, source, staged_rows, validated_rows, rejected_rows, reconciliation_doc_id, signed_off_by |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.entity` (legal entity), `fix.entity`, `fix.branch`, `fix.cost.center` | M30 / M54 | Read; governed master |
| `fix.party` (customer, vendor, brand, seller, employee) | M33 | Read via API |
| `fix.ar.invoice`, `fix.ar.receipt`, `fix.ar.credit.note` | M20 | Read as posting source; control-account owner |
| `fix.ap.invoice`, `fix.ap.payment.run`, `fix.expense.claim` | M52 | Read as posting source; control-account owner |
| `fix.bank.account`, `fix.bank.statement.line`, `fix.cash.position` | M50 | Read; supplies the treasury rate and the reconciled bank movement |
| `fix.tax.determination`, `fix.vat.register.line`, `fix.withholding.determination` | M51 | Read; M51 owns the liability and the return |
| `fix.revenue.schedule`, `fix.performance.obligation`, `fix.settlement.cycle` | M53 | Read; M53 computes, M19 posts the release |
| `fix.asset`, `fix.depreciation.run`, `fix.asset.cwip` | M17 / M49 | Read; M49 computes, M19 posts |
| `fix.budget.line`, `fix.allocation.cycle`, `fix.cost.object` | M54 | Read for variance reporting; M54 reads M19 lines |
| `fix.stock.valuation.event` | M15 | Read as posting source |
| `fix.payroll.run`, `fix.payroll.gl.posting` | M56 | Read as posting source |
| `fix.landed.cost` | M44 | Read as posting source |
| `fix.document` | M24 | Reference only — evidence is stored in M24 |
| `fix.identity`, `fix.role`, `fix.sod.rule` | M29 / M60 | Read for authority and SoD enforcement |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FIN-01 | A subledger publishes a financial event | Match the active posting rule for the event type and version, generate the balanced entry, post or route for review, and acknowledge to the source module with the entry reference | Park the event in the inbox with an error state, alert the Finance Manager, and retry with backoff; **never** post a guessed entry |
| AUT-FIN-02 | An event arrives with no matching active posting rule | Hold in the inbox, raise a high-priority exception to the CFO and the owning module's squad, and report it on the daily unmapped-event list | Hard hold; the event is never discarded |
| AUT-FIN-03 | Accrual entry posted with a reversal date | Post the reversal automatically on that date, referencing the original | Alert if the reversal date falls in a closed period; queue for the next open period |
| AUT-FIN-04 | Recurring journal schedule due | Generate the entry from the template for review, or post directly where the template is marked auto-post | Alert the Finance Officer; template remains due |
| AUT-FIN-05 | Period-end reached | Open the close checklist, assign tasks to owners, start the elapsed-time clock, and notify each owner | Checklist opens manually |
| AUT-FIN-06 | A close task's dependency completes | Notify the next task owner and make the task actionable | Task remains blocked and appears on the overdue list |
| AUT-FIN-07 | Close attempted | Evaluate every blocking condition — unposted entries, unreviewed drafts, unreconciled control accounts, incomplete tasks — and either permit or report the precise blocker | Close blocked with a named reason; never silently permitted |
| AUT-FIN-08 | Period-end reached | Run subledger-to-control-account reconciliation for AR, AP, cash, inventory, fixed assets, tax and deferred revenue, and publish the result to the close checklist | Report the difference and block the close |
| AUT-FIN-09 | Period-end reached | Revalue foreign-currency monetary balances at the closing rate and post the unrealised gain or loss | Alert if no closing rate is available for a currency in use |
| AUT-FIN-10 | Year-end close executed | Close income and expense to retained earnings, roll balances forward, open the new fiscal year, and lock the closed year | Halt and report; partial year-end close is not permitted |
| AUT-FIN-11 | Intercompany transaction posted in one entity | Generate the mirror entry in the counterparty entity with the shared reference | Raise an intercompany exception for manual completion |
| AUT-FIN-12 | Consolidation run initiated | Roll up entity balances, apply elimination rules, produce consolidated statements and the elimination register | Report unmatched intercompany balances and halt |
| AUT-FIN-13 | A hard-closed period is reopened | Log the event, notify the CFO and the audit committee distribution, and add it to the standing exception report | Reopen is blocked without CFO approval |
| AUT-FIN-14 | A manual journal is submitted | Route to an approver who is not the preparer, within the authority matrix, with the supporting document attached | Entry remains in draft; escalate after the configured ageing period |
| AUT-FIN-15 | Daily | Publish the certified ledger extract to M62/M25 with a period stamp and a row-count and control-total assertion | Retain the previous extract, alert M62, and mark dashboards as stale |
| AUT-FIN-16 | A posting rule version is proposed for activation | Run its test fixture; block activation on any failure; on pass, route to the CFO for approval | Activation blocked |
| AUT-FIN-17 | Monthly | Produce the manual-journal register, the backdated-posting report, the reopened-period report and the control-account exception report for the CFO | Report generated with a data-availability warning |
| AUT-FIN-18 | Period exceeds the online retention window | Move the period's lines to the queryable archive partition and verify the row count and control totals before releasing the online rows | Archive aborts; online data is retained |

---

## 12. Interfaces

### 12.1 Upstream — M19 Consumes

| Source | What | Mechanism |
|---|---|---|
| M20 Receivables | Invoice issued, credit note, receipt applied, write-off, bad-debt provision | Event → posting engine |
| M52 Payables & Expense | Vendor invoice approved, payment made, advance issued and settled, expense claim approved, accrual | Event → posting engine |
| M50 Treasury & Cash | Bank movement reconciled, cash deposit, gateway settlement, bank charge, interest, FX conversion, treasury rate | Event → posting engine; REST for rates |
| M51 Tax & Regulatory | VAT output and input determination, TDS/VDS deduction and deposit, tax liability, adjustment | Event → posting engine |
| M53 Revenue & Settlement | Revenue release from schedule, deferral, commission accrual, settlement, escrow movement | Event → posting engine |
| M49 Fixed Assets | Capitalisation, depreciation run, disposal, impairment, CWIP transfer, revaluation | Event → posting engine |
| M54 Costing & FP&A | Allocation cycle result, standard-cost variance, provision proposal | Event → posting engine |
| M15 Inventory | Receipt, consumption, adjustment, revaluation, provision, write-off | Event `stock.*` → posting engine |
| M21 HR & Payroll | Payroll journal, provisions for gratuity, leave and bonus, employer contributions | Event → posting engine |
| M44 Import & Landed Cost | Duty, VAT at import, clearing and freight into landed cost | Event → posting engine |
| M13 Rental / M14 Refurbishment / M12 Marketplace / M06 Data Services | Business-line specific financial events | Event → posting engine |
| M30 Platform Admin / M64 MDM | Entity, operating unit, cost centre and dimension master values | Event projection |
| M33 Party Master | Customer, vendor, brand, seller and employee identity | REST |
| M29 Identity | Roles, authority matrix, SoD rules | REST |

### 12.2 Downstream — M19 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M20 Receivables | Receivable control-account balance, period state, posting confirmation | REST + events |
| M52 Payables | Payable control-account balance, period state, posting confirmation | REST + events |
| M50 Treasury | GL cash balances for reconciliation to the bank position | REST |
| M51 Tax | Posted transactions with tax attributes as the basis for the VAT return and tax schedules | REST + certified extract |
| M53 Revenue | Deferred-revenue control balance and posting confirmation | REST |
| M49 Fixed Assets | Asset control-account balance for register-to-GL reconciliation | REST |
| M54 Costing & FP&A | The full dimensioned ledger line set — the actuals against which every budget and allocation is measured | REST + certified extract |
| M25 Business Intelligence | Certified financial facts for dashboards and executive reporting | Warehouse extract |
| M62 Data Platform | Period-stamped certified ledger extract | Warehouse extract |
| M23 Quality / Internal Audit | Manual-journal register, reopened periods, control exceptions | REST + events |
| M24 Document & Records | Statement packs and evidence packs for retention | Command |
| P06 Analytics & Executive Dashboard | Financial position and result, with drill-down | REST |
| P03 Admin Operations Portal | Full finance workspace | Native |
| External auditor (scoped role) | Read-only ledger, reconciliations and evidence pack | P03 scoped role |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `gl.entry_posted` | entry reference, entity, period, source event, accounts, amounts, dimensions | M20, M52, M50, M51, M53, M49, M54, M25 |
| `gl.entry_reversed` | original entry, reversal entry, reason, actor | M23, M25, source module |
| `gl.event_unmapped` | source module, event type, schema version, payload reference | M28, M23, owning squad |
| `gl.period_opened` | entity, period | All financial modules |
| `gl.period_soft_closed` | entity, period, cut-off timestamp | All financial modules |
| `gl.period_hard_closed` | entity, period, period hash, signed off by | All financial modules, M24 |
| `gl.period_reopened` | entity, period, reason, approver | M23, M25, audit distribution |
| `gl.close_task_overdue` | checklist, task, owner, elapsed | M25, task owner |
| `gl.control_account_variance` | subledger, control account, difference, period | Owning subledger module, M23 |
| `gl.fx_revalued` | entity, period, currency, rate, unrealised gain/loss | M50, M25 |
| `gl.year_closed` | entity, fiscal year, retained-earnings movement | All modules, M24 |
| `gl.consolidation_completed` | period, entities, eliminations, statement references | M25, M24, P06 |
| `gl.certified_extract_published` | period, row count, control totals, extract reference | M62, M25, M54 |
| `gl.posting_rule_activated` | rule, version, effective date, approver | M23, owning subledger squads |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-FIN-01 | Bangladesh Bank published exchange rates | Inbound | Statutory closing and average rates for revaluation and translation |
| INT-FIN-02 | External audit firm (file exchange / scoped portal role) | Outbound | Evidence packs, trial balances, ledger extracts |
| INT-FIN-03 | Legacy standalone accounting software | Inbound, one-time | Opening-balance and comparative-year migration; retired at cutover |
| INT-FIN-04 | Statutory filing preparation (via M51) | Outbound | Ledger basis for income-tax schedules and annual return |
| INT-FIN-05 | Banking partners' corporate reporting (via M50) | Inbound | Reconciled bank movement as posting source |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/gl/events` | POST | Publish a financial event for posting (idempotent) | All subledger modules |
| `/api/v1/gl/entries/{ref}` | GET | Retrieve an entry with lines, dimensions and rule version | All modules, P03 |
| `/api/v1/gl/entries` | POST | Create a manual journal (draft) | P03 |
| `/api/v1/gl/entries/{ref}/approve` | POST | Approve and post a manual journal | P03 |
| `/api/v1/gl/entries/{ref}/reverse` | POST | Post a reversing entry | P03 |
| `/api/v1/gl/balances` | GET | Account balances by entity, period and dimension combination | M54, M25, P06 |
| `/api/v1/gl/trial-balance` | GET | Trial balance for a date, entity and dimension filter | M54, M25, P03, auditor |
| `/api/v1/gl/lines` | GET | Ledger line enquiry with full dimension filtering and drill-down references | M54, M25, P03 |
| `/api/v1/gl/control-accounts/{module}` | GET | Control-account balance for subledger reconciliation | M20, M52, M50, M51, M53, M49 |
| `/api/v1/gl/periods` | GET | Period states per entity | All financial modules |
| `/api/v1/gl/periods/{id}/close` | POST | Attempt a period close, returning blockers if any | P03 |
| `/api/v1/gl/close-checklist/{period}` | GET | Close tasks, owners, status and elapsed time | P03, P06 |
| `/api/v1/gl/statements` | GET | Generate a statutory or management statement | P03, P06, M24 |
| `/api/v1/gl/consolidation/{period}` | POST | Run consolidation for a period | P03 |
| `/api/v1/gl/rates` | GET · POST | Read and maintain dated exchange rates | M50, M51, M20, M52, P03 |
| `/api/v1/gl/posting-rules` | GET · POST | Author, test and version posting rules | P03 |
| `/api/v1/gl/audit-trail` | GET | Tamper-evident trail for an entry, account or period | Auditor, M23 |
| `/api/v1/gl/evidence-pack/{period}` | GET | Generate the period evidence pack | Auditor, P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | C R U D A | All entities; approves close, reopen, posting rules, chart changes |
| R26 Finance Manager | C R U A | All entities; approves manual journals within authority, owns close tasks |
| R27 Finance Officer | C R | Assigned entity/branch scope; prepares journals, cannot approve own |
| R01 Chief Executive Officer | R | All entities — reporting only |
| R02 Chief Technology Officer | R | All entities + posting-rule technical review; no posting rights |
| R04 Chief Commercial Officer | R | All entities — business-line results only |
| R05 Operations Director | R | All branches — operational P&L only |
| R06 Branch Manager | R | Own branch P&L and cost centre; no posting rights |
| R32 Quality Manager / ISO Coordinator | R | Control registers, manual-journal register, reopened-period report |
| R33 IT / System Administrator | R | Configuration and technical support; **no posting rights, no rule approval** |
| R38 External Auditor | R | Scoped entities and periods, time-limited, full drill-down, read-only |
| R28 Warranty Claims Officer | R | Warranty-related accounts and FX exposure only |
| R17 Inventory Manager / R19 Procurement Officer | R | Own control-account balances only |
| R37 Corporate Portal User (Finance) | — | **No M19 access.** Corporate customers see M20 statements only |

**Field-level restrictions.** Entity-level consolidated figures, intercompany balances,
retained earnings and the consolidation elimination register are visible only to R01, R02, R03,
R26 and R38. Branch managers see their own operating unit's P&L and cost-centre detail, and no
other branch's.

**Segregation of duties.**
- **BRU-FIN-11 enforced here:** a journal preparer can never be its approver — hard block at any value.
- **BRU-FIN-25 enforced here:** posting rights and posting-rule administration are mutually exclusive.
- A user may not both reopen a period and post into it.
- R33 IT / System Administrator has configuration access with no transactional posting rights — the platform administrator can never move money in the books.
- **SOD-04** (create + approve credit note) and **SOD-01/02** (vendor and purchase fraud) are enforced in M20 and M52 respectively; M19 blocks the resulting entry if the SoD service reports a violation on the source document.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Trial balance** | Finance Manager, CFO, auditor | On demand | Opening, movement, closing by account, entity and dimension |
| **Statutory financial statements** | CFO, board, auditor, NBR (via M51) | Monthly / annual | Balance sheet, P&L, cash flow, changes in equity, notes — Bangladesh format, English and Bengali |
| **Consolidated statements** | CEO, CFO, board | Monthly / annual | Group position with eliminations and the elimination register |
| **Branch profit and loss** | Branch Manager, Operations Director, CFO | Real time | Revenue, direct cost, contribution and overhead by operating unit — the explicit BR-FIN-008 requirement |
| **Business-line profit and loss** | CCO, CEO, CFO | Monthly | All 14 revenue streams separated by the business-line dimension |
| **Close status dashboard** | CFO, Finance Manager | During close | Task status, owner, elapsed time, blockers, projected close date against the 3-day target |
| **Subledger reconciliation pack** | CFO, Finance Manager, auditor | Monthly | Each subledger to its control account, with differences and explanations |
| **Manual journal register** | CFO, Quality Manager, Internal Audit | Monthly | Every manual entry with preparer, approver, reason, value and supporting document |
| **Backdated posting report** | CFO | Monthly | Entries posted into a prior open period, by module and by preparer |
| **Reopened period report** | CFO, audit committee | On occurrence | Every reopen with reason, approver and the entries posted after reopening |
| **Control-account exception report** | Finance Manager, subledger owners | Daily | Any direct-posting attempt, any unexplained control variance |
| **Unmapped-event report** | CFO, CTO, subledger squads | Daily | Events held with no active posting rule — a leading indicator of revenue or cost not being recorded |
| **Posting rule register** | CFO, CTO, auditor | On change | Every rule, its version history, effective dates, approver and fixture results |
| **FX exposure and revaluation** | CFO, Finance Manager | Monthly | Foreign-currency monetary balances, rates applied, realised and unrealised results |
| **Intercompany balance report** | Finance Manager, CFO | Monthly | Balances by entity pair with mismatch flags |
| **Audit evidence pack** | External auditor | Annual / on request | Trial balance, reconciliations, journal registers, close sign-offs, control-account movements, period hashes |
| **Ledger activity by module** | CFO, CTO | Monthly | Posting volume, rule-generated vs manual proportion, error and hold rates |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-050** | Month-end close cycle | 15–20 days | 5 days | **≤ 3 days** |
| **KPI-052** | Days sales outstanding *(jointly with M20)* | unmeasured | 38 | **< 32** |
| — | Audit adjustments as % of revenue | unmeasured | < 1% | **< 0.5%** |
| — | Manual journals as % of total postings | ~100% | < 15% | **< 5%** |
| — | Subledger-to-control-account differences at close | unmeasured | < 5 unexplained | **Zero** |
| — | Unmapped financial events outstanding > 24 h | n/a | < 10 | **Zero** |
| — | Periods reopened after hard close | n/a | ≤ 2 per year | **≤ 1 per year** |
| — | Entries posted without an approver distinct from the preparer | unknown | **Zero** | **Zero** |
| — | Backdated postings as % of total postings | unmeasured | < 3% | **< 1%** |
| — | Branch P&L available to branch managers | 0 branches | 51+ | **51+, live** |
| — | Statement generation time (full statutory pack) | days | < 5 min | **< 60 s** |
| — | Drill-down completeness (reported figures traceable to source) | ~0% | 98% | **100%** |
| — | Year-end statutory audit fieldwork duration | unmeasured | −25% | **−40%** |

> **Register note.** KPI-050 and KPI-052 are the canonical identifiers allocated in `06-02`
> §2.7. **KPI-051** (bank reconciliation auto-match) and **KPI-057 / KPI-058** (VAT returns on
> time, tax compliance findings) are listed in `06-02` against M19 but are re-owned in v2.1 by
> **M50** and **M51** respectively; the register requires updating — recorded as audit action
> **A-01**. The eleven unnumbered metrics above are new to this specification and require
> allocation in `06-02` — audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — chart, journals, entries, reconciliation, multi-currency, fiscal periods, multi-company | 30% |
| L2 | OCA `account-financial-tools` (`account_lock_date_update`, `account_journal_lock_date`, `account_move_line_tax_editable`), `account-financial-reporting` (`account_financial_report` — trial balance, general ledger, aged balance), `mis-builder` (statement layouts), `account-fiscal-rule` | 24% |
| L3 | Free reporting and export aids | 3% |
| L5 | `cd_gl_ext`, `cd_subledger_posting`, `cd_multi_entity_consolidation`, `cd_financial_statements_bd`, `cd_close_checklist` | 43% |

> The custom share is higher than the `02-01` §11 indication for M19. The re-scope moved tax,
> cash, assets, costing and revenue *out* of M19, but the posting engine and the seven-dimension
> model — the two things that make the rest of Category G possible — are entirely custom and
> have no adequate L1 or L2 equivalent.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 5 of 5 identifiers below are claimed by another module: **CD-089** also claimed by M59; **CD-157** also claimed by M17, M29; **CD-158** also claimed by M17, M29; **CD-159** also claimed by M30, M45; **CD-160** also claimed by M45, M64. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-157** | `cd_gl_ext` — seven-dimension model on the journal line, cross-validation rules, control-account protection, reporting hierarchies, chart governance and versioning | Odoo module | 7 PW |
| **CD-158** | `cd_subledger_posting` — the event inbox, posting-rule engine, rule versioning, fixtures, idempotency and unmapped-event handling | Odoo module + service | **9 PW** |
| **CD-159** | `cd_multi_entity_consolidation` — intercompany balancing and reconciliation, entity roll-up, elimination rules, consolidated statements | Odoo module | 5 PW |
| **CD-160** | `cd_financial_statements_bd` — Bangladesh statutory statement formats, July–June calendar, Bengali rendering, notes and evidence pack | Odoo module | 4 PW |
| CD-089 | `cd_close_checklist` — close task model, dependencies, ownership, evidence, sign-off, elapsed-time tracking, subledger reconciliation gate | Odoo module | 3 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-083…089** to M19 as `cd_mushak`,
> `cd_vat_register`, `cd_tds`, `cd_nid`, `cd_cash_position`, `cd_fixed_asset_ext`,
> `cd_close_checklist`. Under the v2.1 re-scope: **CD-083, CD-084, CD-085 and CD-086** move to
> **M51**; **CD-087** (`cd_cash_position`) moves to **M50**; **CD-088** (`cd_fixed_asset_ext`)
> moves to **M49**; **CD-089** (`cd_close_checklist`) remains with M19. Four new IDs,
> **CD-157…160**, are claimed from the Category G block.
>
> **Category G CD block (for cross-module coherence).** CD-157…160 + CD-089 M19 ·
> CD-161…163 + CD-090 + CD-095 M20 · CD-164…166 M52 · CD-167…172 + CD-087 M50 ·
> CD-173…175 + CD-083…086 M51 · CD-176…179 + CD-093 + CD-094 M53 · CD-180…182 + CD-088 M49 ·
> CD-183…186 M54. Category G claims **41 CD IDs in total**: the new contiguous block CD-157…186
> plus eleven reallocated from M19's and M20's v2.0 allocations. CD-091 and CD-092 leave the
> category entirely, to **M39** (Category C).
> **All CD IDs remain provisional** pending the unified CD register required by audit finding
> M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity, M30 Platform Admin | Entity and operating-unit model, roles, authority matrix and SoD service must exist before a ledger can enforce anything |
| M28 Integration | The event outbox and schema registry are the transport for every posting event |
| M64 MDM | Dimension master values must be governed before they become mandatory on every line |
| M33 Party Master | Customers, vendors and brands must be identifiable before receivables and payables mean anything |
| M15 Inventory (W2) | Valuation events are the first non-finance posting source; M15 ships with a stubbed consumer in W2 and connects to the live engine in W3 |

**Delivers into:** M20, M52 and M50 cannot post in Wave 3 without M19. M51, M53, M49 and M54
cannot exist at all without it. **M19, M20, M52 and M50 must go live together** — a ledger
without receivables, payables and cash is not a ledger.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Legacy accounting software — chart of accounts | ~400–800 accounts | `fix.gl.account` (mapped and rationalised) | W3 minus 2 months |
| Legacy accounting software — trial balance at cutover | 1 opening balance set per entity | `fix.gl.line` (opening journal) | W3 cutover |
| Prior-year comparatives | 1–2 years, summary level | `fix.gl.line` (comparative journals) | W3 cutover |
| Open AR and AP items | Per M20 / M52 migration | Control accounts reconciled to subledger detail | W3 cutover |
| Branch spreadsheets (51+) | Historical only | **Not migrated** — retained as reference documents in M24 | W3 |
| Fixed asset register | Per M49 migration | Control account only in W3; register in W5 | W3 / W5 |
| Exchange-rate history | 2 years | `fix.currency.rate` | W3 |

> **Migration position — non-negotiable.** Opening balances are established from a **trial
> balance signed by the CFO and agreed with the external auditor**, and are proven by
> reconciling every control account to its subledger detail before cutover. In addition, **one
> full parallel month-end close** is run in the legacy system and in M19, and the two results are
> reconciled line by line and signed off, before the legacy system is retired. This is recorded
> as a category-level risk in `_CATEGORY_OVERVIEW.md` §10 ("financial history migration does not
> reconcile — opening balances wrong forever").

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No module other than M19 can create a journal entry through any path — UI, API, import or direct database role | Negative test suite plus a database grant audit |
| AC-02 | Every posted entry references the posting rule version, source event and source document that produced it | Full-table assertion query on production data |
| AC-03 | A posted entry cannot be modified or deleted through any path | Negative test on UI, API, import and administrative paths |
| AC-04 | Every journal line carries a non-null legal entity and operating unit | Database constraint plus full-table assertion |
| AC-05 | An entry that does not balance within a legal entity is rejected, and cross-entity entries generate intercompany lines automatically | Scripted scenario |
| AC-06 | A financial event with no active posting rule is held, alerted and never posted on a guessed treatment | Negative test with an unregistered event type |
| AC-07 | Event replay after an induced broker failure produces exactly one entry per event | Idempotency test with forced duplicate delivery |
| AC-08 | Re-running the posting engine over an event set with the same rule versions produces byte-identical entries | Determinism test |
| AC-09 | A period cannot be hard-closed while any blocking condition exists, and the blocker is named precisely | Scripted scenario per blocker type |
| AC-10 | No posting is possible into a hard-closed period through any path | Negative test on UI, API and import |
| AC-11 | A period reopen requires CFO approval, is logged, and appears on the audit report | Scripted scenario |
| AC-12 | Every subledger reconciles to its control account at close, with zero unexplained differences | Three consecutive monthly closes signed by the CFO |
| AC-13 | Month-end close completes in ≤ 3 days across all entities and business lines | Six consecutive close cycles, measured (KPI-050) |
| AC-14 | A journal preparer cannot approve their own entry at any value | SoD negative test (BRU-FIN-11) |
| AC-15 | Branch profit and loss is produced for all 51+ operating units from the dimension model, with no separate branch ledger | Statement output for every branch, reconciled to the group P&L |
| AC-16 | Consolidated statements eliminate all intercompany balances, and the elimination register reconciles | Consolidation run reviewed by the external auditor |
| AC-17 | Trial balance for a full year across all entities returns in ≤ 5 s, and the full statutory pack generates in ≤ 60 s | Performance test at projected production volume (≈ 5M lines/year) |
| AC-18 | Any figure in any statement drills to its source document in ≤ 2 s | Correctness and performance test across all statement lines |
| AC-19 | Opening balances reconcile to the signed legacy trial balance, control account by control account | CFO-signed reconciliation |
| AC-20 | One full parallel month-end close is completed and reconciled between legacy and M19 before legacy retirement | Signed parallel-run reconciliation |
| AC-21 | The audit trail is tamper-evident: any retrospective alteration is detectable via the period hash chain | Penetration/integrity test with an induced alteration |
| AC-22 | The external auditor role is read-only, time-limited and cannot post; all its access is logged | Negative test and access-log review |
| AC-23 | Statements and account names render completely in Bengali as well as English | Translation coverage report (AS-12) |
| AC-24 | Financial data older than the online window remains queryable through the same enquiry API | Archive query test on a migrated period |
| AC-25 | CFO and external auditor sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 25 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many legal entities exist today, and how many are planned within the programme horizon? Consolidation scope depends on the answer | CFO / CEO | W3 minus 3 months |
| Q-02 | Is the chart of accounts rationalised before migration, or migrated as-is and rationalised later? A rationalised chart is strongly recommended | CFO | W3 minus 3 months |
| Q-03 | Which accounting framework is the reporting basis — IFRS as adopted in Bangladesh (BFRS) in full, or the SME framework? This determines M53 and M49 treatments | CFO / external auditor | W3 design |
| Q-04 | Is the external auditor prepared to accept a system-generated evidence pack in place of manually prepared schedules? Early agreement saves an audit cycle | CFO / external auditor | W3 design |
| Q-05 | What is the manual-journal approval authority matrix by value band? | CFO | W3 build |
| Q-06 | How many comparative years must be migrated for statutory and board reporting? | CFO | W3 minus 2 months |
| Q-07 | Is the parallel month-end close approved as a business commitment, including the double-running effort it requires? | CFO / CEO | W3 minus 3 months |
| Q-08 | Which of the seven proposed dimensions are mandatory on which account types? A dimension that is mandatory everywhere will not be populated correctly | CFO / Finance Manager | W3 design |
| Q-09 | Does the business require a branch **balance sheet**, or is a branch P&L with a derivable balance sheet sufficient? Full branch balance sheets materially increase the posting-rule burden | CFO / Operations Director | W3 design |
| Q-10 | What is the online retention window before archival — three years or the full seven? | CFO / CTO | W3 build |
| Q-11 | Which cost-centre structure will be used, and does it match the operational branch hierarchy or differ from it? | CFO / Operations Director | W3 design |
| Q-12 | Are group-level segment disclosures required for the 14 revenue streams under the chosen framework? | CFO / external auditor | W4 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §1 (only Category G creates journal entries), §4 (money flow), §5
(boundary map), §8 (KPIs), §9 (delivery sequence), §10 (risks) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` ·
`M52_Accounts_Payable_and_Employee_Expense.md` · `M50_Treasury_Cash_and_Banking.md` ·
`M51_Tax_and_Regulatory_Compliance_Bangladesh.md` ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` ·
`M49_Fixed_Assets_and_Capital_Investment.md` · `M54_Cost_Accounting_Budgeting_and_FPA.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §11 (layer allocation),
§AS-01…AS-15 (architecture standards; AS-03, AS-08, AS-10, AS-11, AS-12 are load-bearing here) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 (definition of done) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 (CD register) ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §3.5 (finance roles),
§5 (field-level restrictions), §6 (SOD-01…SOD-12) ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` §Finance
(BRU-FIN-01…10) · `06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md`
§2.7 (KPI-050…058), BO-06, BO-07, BO-18

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-001, BR-FIN-008,
BR-FIN-012, BR-FIN-013, NFR-021, NFR-022, BRU-FIN-01…07, §Process 8 (As-Is close),
§Month-End Close Day 1–5, §Data Retention (7 years, Companies Act / NBR) ·
`1000FiX_Services_Company_Profile.md` §Service Infrastructure ·
`1000fix_business/Business planning for 1000 fix.docx` §Revenue streams

**External benchmark**
[SAP S/4HANA Universal Journal (ACDOCA)](https://sapinsider.org/articles/mastering-acdoca-7-essential-universal-journal-insights-for-sap-s-4hana-consultants-2025-edition/) —
one line-item table merging FI, CO, asset accounting and material ledger; no FI↔CO reconciliation ·
[SAP S/4HANA Finance module overview](https://www.erpresearch.com/en-us/sap-s4-hana-finance-accounting-module) ·
[Oracle Fusion Cloud Subledger Accounting](https://docs.oracle.com/en/cloud/saas/financials/25d/fausl/using-subledger-accounting.pdf) —
the rules-based engine that converts subledger transactions into journal entries with full
traceability; the direct model for `cd_subledger_posting` ·
[Oracle Fusion Cloud General Ledger](https://docs.oracle.com/en/cloud/saas/financials/26b/faugl/using-general-ledger.pdf) —
cross-validation rules, intercompany balancing, allocations, revaluation ·
[Oracle Fusion Cloud Financial Management](https://www.oracle.com/erp/financial-management/) ·
[Microsoft Dynamics 365 Finance modules](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
financial dimensions as line attributes rather than account segments; period close workspace ·
[OCA account-financial-tools](https://github.com/oca/account-financial-tools) — journal lock
dates, lock-date update control ·
[OCA account-financial-reporting (19.0)](https://github.com/OCA/account-financial-reporting/tree/19.0/account_financial_report) —
trial balance, general ledger and aged-partner reports ·
Bangladesh Companies Act 1994 and IFRS/BFRS as adopted — July–June fiscal year, statutory
statement formats, seven-year retention

---

*Module M19 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
