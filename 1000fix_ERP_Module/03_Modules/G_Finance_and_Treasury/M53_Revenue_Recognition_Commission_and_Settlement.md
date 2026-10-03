---
id: FIX-ERP2-M53
module_id: M53
module_code: REV
module_name: Revenue Recognition, Commission & Settlement
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P1
wave: W4 / W7
---

# M53 — Revenue Recognition, Commission & Settlement
### Category G · Code `REV` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M53 |
| **Module code** | `REV` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M20 monolith after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | **W4** (recognition core) · **W7** (marketplace settlement extension) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (deferred accounts) · L2 OCA `account-financial-tools`, `contract` (recurring structures) · L5 custom recognition engine, obligation model, commission ledger and payout engine |
| **Custom modules** | `cd_revenue_recognition`, `cd_performance_obligation`, `cd_commission_ledger`, `cd_settlement`, `cd_payout_engine`, `cd_escrow` |
| **Requirement range** | FR-REV-001 … FR-REV-044 |
| **Requirement count** | **44** *(measured — supersedes the 38 estimate in `02-02`)* |
| **Effort estimate** | **28 person-weeks** *(measured — supersedes the 24 PW estimate; W4 core ≈ 18 PW, W7 marketplace extension ≈ 10 PW)* |
| **Depends on** | M19 GL · M20 Receivables · M08 Contract & SLA · M39 Subscription · M11 Pricing · M51 Tax · M50 Treasury · M12 Marketplace *(W7)* · M33 Party Master |
| **Depended on by** | M19, M20, M50, M52, M54, M12, M13, M08, M39, M05, M25, M07, M40 |

---

## 2. Purpose

M53 answers two questions that look unrelated and are in fact the same question: **when has
1000FiX actually earned money, and who else is owed a share of it?**

The first is revenue recognition. Issuing an invoice is not earning revenue. A customer who buys
a two-year extended warranty in July has paid for twenty-four months of protection, and the
Company has earned one twenty-fourth of it by the end of that month. An AMC contract, a rental
period, a managed-services month, a prepaid service package and a marketplace transaction all
separate the moment of billing from the moment of earning. Recording them as revenue when the
invoice is raised overstates one period and understates another — and once statements are
issued on that basis, correcting it is a restatement.

The second is settlement. When an external seller completes a job under the 1000FiX brand, the
customer pays 1000FiX and 1000FiX owes the seller their share, net of commission and any
deductions. Same for a referral partner, a courier revenue-share, and a brand partner's
warranty arrangement. Getting these wrong does not produce an accounting error — it produces a
seller who stops working for the platform, and the marketplace is the growth engine that
`BO-12` depends on for **25% of job volume**.

Both are the same question because both turn on **the contract**: what was promised, what has
been delivered, what it is worth, and who is entitled to what. M53 owns that.

### Why It Exists

The v2.0 draft placed revenue recognition (`cd_revenue_recognition`) and settlement
(`cd_settlement`) inside M20. That is a category error. M20's job is to bill and collect;
its states are *issued, delivered, paid*. Revenue's states are *promised, satisfied,
recognised*. They move on different clocks, and forcing them into one module means either the
invoice states get polluted with accounting semantics or the accounting gets driven by
invoicing convenience. The second is what happens in practice, and it is how service companies
end up recognising a year of AMC revenue in the month it was billed.

There is also an audit reality. Under IFRS/BFRS as adopted in Bangladesh, revenue is the number
an auditor examines most closely, and the deferred revenue balance is the one they reconcile to
contracts. A schedule generated from a contract is defensible; a spreadsheet is not.

M53's delivery is deliberately split. The **W4 core** covers recognition, deferral, performance
obligations and the commission ledger — everything the existing business needs. The **W7
extension** covers marketplace seller settlement and partner payouts, which arrive with M12.
The category gate is unambiguous: **100% seller and partner payout accuracy is a Wave 7 gate
criterion.**

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-011 | "Support AMC/RAMC subscription billing with configurable billing cycles" — the billing side is M39/M20; the earning side is M53 |
| ERP BRD BR-FIN-008 | Branch-wise and consolidated financial statements — revenue must be correctly periodised to be meaningful |
| ERP BRD §Value-Added Services | Warranty Extension Programme, Residential Service Package (RAMC), Privileged Programme — all multi-period obligations |
| Company Profile §Value-Added Services | Warranty extension, RAMC, laptop rental, exchange offer, partner alliance programme |
| Business Objective BO-11 | "Build managed services into a material revenue line — MSP revenue share ≥ 12% of revenue" — a recurring, over-time obligation |
| Business Objective BO-12 | "Scale delivery capacity beyond owned headcount — marketplace share of job volume ≥ 25%" — the settlement volume driver |
| Business Objective BO-13 | "Establish rental as a profitable asset business — utilisation 68%, gross margin 55%" |
| `_CATEGORY_OVERVIEW.md` §2 | M53 scope: "Revenue schedules, deferral, performance obligations, commission ledgers, seller and partner payouts, escrow" |
| `_CATEGORY_OVERVIEW.md` §5 | "Commission calculation scheme: M12 defines; M53 calculates and pays" |
| `_CATEGORY_OVERVIEW.md` §8 | Seller and partner payout accuracy **100%** · deferred revenue reconciled to contracts 100% · revenue leakage < 0.5% (jointly with M20) |
| `_CATEGORY_OVERVIEW.md` §10 | Risks: "Revenue recognised in the wrong period — high, misstatement. Schedules generated from contracts, not entered manually; manual release requires CFO approval" · "Seller payouts wrong or late — high, marketplace collapses" |
| Exec Summary §6.2 | Marketplace commission and ads **BDT 84 lac/year** · MSP contribution **BDT 95 lac/year** · rental gross margin **BDT 48 lac/year** — all M53-periodised |
| IFRS 15 | Five-step model; service-type warranties are separate performance obligations recognised over time; extended warranties are contract liabilities released over the warranty period |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M53 sits between the commercial modules that define what
> was sold and the ledger that records it. Both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Performance obligations: identification, separation and their satisfaction criteria |
| 2 | Transaction price determination for accounting purposes, including variable consideration and constraint |
| 3 | Stand-alone selling price allocation across obligations in a bundle |
| 4 | Revenue schedules: generation from contracts, over-time and point-in-time patterns |
| 5 | Deferral and release: contract liabilities and their systematic recognition |
| 6 | Contract assets (unbilled receivable) and contract liabilities (deferred revenue) |
| 7 | Recognition triggers: time elapsed, milestone reached, usage consumed, delivery confirmed |
| 8 | Modification and termination accounting: prospective, cumulative catch-up and cancellation |
| 9 | Revenue reversal on cancellation, refund and credit note |
| 10 | Principal-versus-agent determination for accounting presentation (gross versus net revenue) |
| 11 | Contract cost capitalisation and amortisation where the framework requires it |
| 12 | Deferred-revenue reconciliation to the underlying contracts, every period |
| 13 | Revenue disclosure schedules: disaggregation, contract balances, remaining obligations |
| 14 | **Commission ledger**: accrual, adjustment and clearing of commission earned by and owed to third parties |
| 15 | **Seller settlement**: statement, deductions, net position and payout for marketplace sellers |
| 16 | **Partner and referral payouts**: alliance partners, referrers, courier revenue shares |
| 17 | Payout runs: proposal, hold, approval, release to M50, and confirmation |
| 18 | **Escrow**: funds held on behalf of a seller, their release conditions and their movement |
| 19 | Clawbacks, chargebacks and deductions against a settlement |
| 20 | Settlement dispute handling with sellers and partners |
| 21 | Seller and partner statements, self-billing documents and their portal presentment |
| 22 | Settlement reconciliation: what was collected, what was owed, what was paid, what remains held |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Invoice creation, delivery, receipt capture, ageing, dunning, credit notes | **M20** Receivables | Billing and earning are different events on different clocks |
| Recurring billing schedule, cycle definition, proration, plan change | **M39** Subscription & Recurring Billing (Category C) | The billing schedule is commercial; the revenue schedule is accounting, and they are frequently different |
| Price determination, rate cards, discounts, dynamic pricing | **M11** Pricing (Category C) | Commercial price is an input; accounting transaction price is a derived concept |
| Contract terms, SLA, entitlement, renewal | **M08** Contract & SLA Management | M08 authors the contract; M53 accounts for it |
| **Commission scheme definition** — rates, tiers, categories, seller agreements | **M12** Marketplace & Sellers (Category B/C) | M12 defines the scheme; **M53 calculates and pays** (`_CATEGORY_OVERVIEW.md` §5) |
| Seller onboarding, qualification, rating, suspension | **M12** Marketplace & Sellers | A settlement is only made to a seller M12 has approved |
| Marketplace order lifecycle, job assignment, dispute on service quality | **M12** with **M01** | M53 settles the money consequence, not the service dispute |
| Journal posting of revenue, deferral, commission and settlement | **M19** General Ledger | Only Category G's ledger creates journal entries |
| Payment execution to a seller's bank or wallet | **M50** Treasury & Cash | M53 authorises the payout; M50 disburses |
| Trade payables to vendors and sub-contractors | **M52** Payables | A settlement of a revenue share is not a trade payable |
| VAT treatment of a settlement, and the principal/agent **tax** position | **M51** Tax & Regulatory | M53 owns the accounting presentation; M51 owns the tax determination. **Both derive from decision D-03** |
| Rental asset capitalisation and depreciation | **M49** Fixed Assets (with **M13**) | M53 recognises the rental revenue; M49 carries the asset |
| Loyalty point liability and redemption value | **M10** Loyalty & Rewards | M10 computes the entitlement; M53 accounts for any material breakage or deferral |
| Warranty claim adjudication and recovery from brands | **M09** Warranty & Claims | M09 establishes the claim; M20 invoices it; M53 periodises where a service-type warranty applies |
| Business-line profitability and margin analysis | **M54** Costing & FP&A | M53 supplies periodised revenue; M54 pairs it with cost |
| Employee sales incentives and technician bonuses | **M21** HR & Payroll | Internal incentive is payroll; external commission is settlement |

### 3.3 Shared Concepts

| Concept | M53's Role | Owning Module |
|---|---|---|
| Performance obligation | **Owns** — the defining concept of this module | M53 |
| Revenue schedule | **Owns** | M53 |
| Deferred revenue balance | Owns the schedule and the reconciliation; M19 owns the control account | M53 / M19 |
| Contract | Reads terms and events; M08 authors | M08 / M53 |
| Billing schedule | Reads; frequently differs from the revenue schedule | M39 |
| Invoice | Consumes as a trigger and as a contract-balance movement | M20 |
| Transaction price | Derives the accounting transaction price from the commercial price | M11 / M53 |
| Commission scheme | Reads the scheme; **owns the calculation and the ledger** | M12 / M53 |
| Seller settlement | **Owns** | M53 |
| Escrow balance | **Owns** the obligation; M50 holds the funds | M53 / M50 |
| Payout instruction | **Owns** the authorisation; M50 executes | M53 / M50 |
| Principal/agent position | Owns the accounting presentation; M51 owns the tax treatment; both from D-03 | M53 / M51 |
| Rental revenue | Owns the periodisation; M13 owns the rental operation | M53 / M13 |
| Unbilled revenue | **Owns** the contract asset; M20 owns the unbilled *operational* exception | M53 / M20 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Revenue Accounting and Reporting (RAR)** | Revenue accounting contracts assembled from operational documents; performance obligations with fulfilment types; SSP allocation; contract liability and asset management; a revenue sub-ledger separate from the billing document | **The revenue accounting contract as a separate object from the billing document.** RAR's central insight is that the accounting view of a contract is *constructed* from operational documents rather than being one of them. Our `revenue.contract` is assembled from M08 contracts, M39 subscriptions, M20 invoices and M01 jobs, and it is the thing the auditor examines. Also adopted: fulfilment types (time-based, event-based, percentage-of-completion) as first-class | RAR's inbound-processing/BRF+ configuration layer; disproportionate for our obligation types |
| **Oracle Fusion Cloud — Revenue Management** | Automatic identification of customer contracts across source systems, performance obligation templates, SSP hierarchies with tolerance bands, revenue accounting separate from receivables | **SSP as maintained data with tolerance bands**, not a per-contract judgement. When a bundle is sold, allocation must be mechanical and repeatable, or every bundle becomes a manual accounting decision. Also adopted: the strict architectural separation from receivables — Oracle keeps Revenue Management and Receivables as distinct engines against the same transactions | Oracle's multi-source contract-identification rules engine; our sources are known and few |
| **Zuora RevPro / Workday (Zuora) revenue** | Subscription revenue automation, waterfall reporting, contract modification handling, revenue waterfall reconciliation | **The revenue waterfall as the primary control artefact** — a period-by-period view of opening deferred, additions, releases, modifications and closing, that reconciles to the ledger. This is what makes "deferred revenue reconciled to contracts, 100%" testable rather than aspirational | Their rating and subscription-management layer — that is M39's scope |
| **Marketplace settlement practice (Amazon/Shopify/Uber class platforms)** | Seller statements with gross, commission, fees, adjustments and net; scheduled payout cycles; reserve and rolling hold; deduction hierarchy; self-billing invoices; dispute windows | **The settlement statement as a document the seller can reconcile independently**, with a stable deduction hierarchy and a published payout calendar. Sellers leave platforms over payout opacity far more often than over commission rates. Also adopted: **rolling reserve/escrow** to cover expected refunds and quality claims, released on a defined schedule rather than at discretion | Dynamic algorithmic reserve rates; a fixed, published reserve policy is more defensible in a market where trust is the scarce resource |
| **Payment-facilitator and escrow practice** | Funds held on behalf of a third party segregated from operating cash; release conditions defined; a liability, never revenue | **Escrow as a segregated liability with its own bank account purpose** (M50 FR-TRE-003). Money held for a seller is not 1000FiX's money and must never appear in operating cash or fund operations. This is both an accounting and a reputational necessity | Full payment-facilitator regulatory apparatus — out of scope for the current model |
| **IFRS 15 — Revenue from Contracts with Customers** | Five-step model; service-type warranties as separate performance obligations recognised over time; extended warranties as contract liabilities released over the warranty period on a straight-line basis; assurance-type warranties accounted under IAS 37 as costs, not deferred revenue; transaction price allocated on stand-alone selling prices | **The assurance-versus-service warranty distinction, implemented as a mandatory attribute on every warranty product.** 1000FiX sells extended warranties (service-type — deferred and released over the period) and performs manufacturer warranty work (assurance-type — cost when incurred, revenue on claim). Conflating them is the most likely revenue error in this business | Nothing — this is the governing framework |
| **IFRS 16 / lessor accounting for the rental business** | Operating lease income recognised on a straight-line basis over the lease term | Straight-line recognition of rental revenue over the rental period, separated from the asset's depreciation in M49 | Finance-lease classification treatment unless the rental terms require it — a position to confirm with the auditor (§18 Q-04) |

**Design position.** Six deliberate positions.

First, **schedules are generated from contracts, never typed**. `_CATEGORY_OVERVIEW.md` §10
names manual entry as the risk. Every revenue schedule in M53 traces to a contract, a
subscription, an invoice or a job. A manual schedule is possible, requires CFO approval, and
appears on a standing report — the same treatment M19 gives a manual journal.

Second, **the revenue contract is a constructed object**. It is assembled from whatever
operational documents represent the customer arrangement, and it is what reconciles to the
deferred revenue balance. This is the single design decision that makes the deferred-revenue-to-
contract reconciliation possible.

Third, **warranty type is a mandatory product attribute**. Every warranty-bearing item in M37
carries assurance-or-service classification. There is no default. The accounting consequences
are completely different, and a business whose core operation is warranty work cannot afford
ambiguity here.

Fourth, **settlement accuracy is binary**. The category KPI is 100%, not 99.5%. A seller who
receives a wrong payout does not file a variance report — they stop accepting jobs, and they
tell other sellers. Every settlement is reconciled three ways: what the customer paid, what the
scheme says is owed, what was actually disbursed.

Fifth, **escrow is not our money**. Funds held for sellers sit in a purpose-designated account,
are a liability from the moment of collection, and are never available to operations. This is
enforced through M50's account-purpose restriction, not through policy.

Sixth, **the principal-versus-agent position is declared once, for accounting and for tax
together, and it is blocked until D-03 is settled**. M53's gross-versus-net presentation and
M51's VAT base derive from the same determination. Building the marketplace against an assumed
position risks restating every marketplace transaction ever processed.

---

## 5. Functional Areas & Features

### 5.1 Revenue Contracts & Performance Obligations

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-REV-001 | Revenue contract assembly | Construct a revenue accounting contract from the operational documents that represent a customer arrangement — M08 contract, M39 subscription, M20 invoice, M01 job, M13 rental — and maintain it as the object that reconciles to deferred revenue | **P0** | L5 |
| FR-REV-002 | Performance obligation identification | Identify and separate the distinct performance obligations in a contract, using obligation templates defined per product and service type in M37 | **P0** | L5 |
| FR-REV-003 | Warranty classification | Require every warranty-bearing item to carry a mandatory assurance-or-service classification, and apply the corresponding treatment with no default | **P0** | L5 |
| FR-REV-004 | Satisfaction criteria | Define, per obligation, whether it is satisfied over time or at a point in time, and the measure of progress — time elapsed, milestone, usage consumed or delivery confirmed | **P0** | L5 |
| FR-REV-005 | Transaction price determination | Determine the accounting transaction price from the commercial price, including variable consideration, discounts, refund liabilities and the constraint on variable amounts | **P0** | L5 |
| FR-REV-006 | Stand-alone selling price | Maintain SSP per item with a hierarchy (observable, adjusted market, cost-plus, residual) and tolerance bands, and allocate the transaction price across obligations mechanically | **P0** | L5 |
| FR-REV-007 | Principal/agent presentation | Determine gross-versus-net revenue presentation per arrangement type from the single declared position, and apply it consistently (with M51 for the tax base) | **P0** | L5 |
| FR-REV-008 | Contract modification | Account for a modification as a separate contract, a prospective change, or a cumulative catch-up, per the modification's nature, with the treatment recorded and evidenced | P1 | L5 |
| FR-REV-009 | Contract termination | Account for early termination, including release of remaining deferred revenue, termination fees and any refund liability | P1 | L5 |

### 5.2 Revenue Schedules, Deferral & Release

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-REV-010 | Schedule generation | Generate the revenue schedule for every obligation automatically from the contract, with no manual entry in the normal path | **P0** | L5 |
| FR-REV-011 | Over-time recognition | Release revenue over time on the defined measure of progress — straight-line for extended warranties, AMC/RAMC, managed services and rentals; usage-based where the obligation is consumption-driven | **P0** | L5 |
| FR-REV-012 | Point-in-time recognition | Recognise revenue at the point of transfer for repairs, parts sales, refurbished device sales and one-off services | **P0** | L5 |
| FR-REV-013 | Milestone and percentage-of-completion | Recognise revenue on milestone acceptance or measured progress for project-shaped engagements such as data services and corporate deployments | P1 | L5 |
| FR-REV-014 | Contract liability | Maintain deferred revenue per obligation with opening, additions, releases, modifications and closing, reconcilable at any date | **P0** | L5 |
| FR-REV-015 | Contract asset | Maintain unbilled revenue where performance precedes billing, and reclassify to a receivable when the invoice is raised | **P0** | L5 |
| FR-REV-016 | Recognition run | Execute the periodic recognition run per entity, produce the release entries for M19, and hold the run's inputs and outputs as evidence | **P0** | L5 |
| FR-REV-017 | Manual release control | Permit a manual recognition or deferral adjustment only with a reason, evidence and **CFO approval**, and report every occurrence | **P0** | L5 |
| FR-REV-018 | Revenue reversal | Reverse recognised revenue on cancellation, refund or credit note, restoring or extinguishing the obligation as appropriate | **P0** | L5 |
| FR-REV-019 | Revenue waterfall | Produce the period waterfall — opening deferred, additions, releases, modifications, reversals, closing — reconciled to the M19 control account | **P0** | L5 |
| FR-REV-020 | Deferred-to-contract reconciliation | Reconcile the total deferred revenue balance to the sum of open contract obligations every period, and report any difference before close | **P0** | L5 |
| FR-REV-021 | Remaining performance obligations | Report the value of unsatisfied obligations and the expected timing of their recognition | P1 | L5 |
| FR-REV-022 | Revenue disaggregation | Disaggregate recognised revenue by business line, revenue stream, customer segment, branch, channel, timing pattern and contract type | **P0** | L5 |
| FR-REV-023 | Contract cost capitalisation | Capitalise and amortise incremental costs of obtaining or fulfilling a contract where the framework requires it, over the obligation period | P2 | L5 |

### 5.3 Commission Ledger

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-REV-024 | Commission calculation | Calculate commission earned on each qualifying transaction from the scheme defined in M12, including tier, category, promotion and minimum-fee rules | **P0** *(W4 core; W7 for marketplace)* | L5 |
| FR-REV-025 | Commission ledger | Maintain a commission ledger per counterparty with accrual, adjustment, clearing and outstanding balance, independent of the payout cycle | **P0** | L5 |
| FR-REV-026 | Commission recalculation | Recalculate commission when the underlying transaction is amended, refunded or cancelled, and post the differential rather than replacing the original | **P0** | L5 |
| FR-REV-027 | Commission recognition | Recognise commission revenue in the correct period, separately from the settlement of the underlying transaction | **P0** | L5 |
| FR-REV-028 | Scheme change control | Apply a commission scheme change prospectively from its effective date and never retrospectively to settled transactions | **P0** | L5 |
| FR-REV-029 | Commission transparency | Expose the calculation basis — transaction, rate, tier applied, deductions — to the counterparty, line by line | **P0** | L5 |

### 5.4 Settlement, Payouts & Escrow *(W7 for marketplace; W4 for partners)*

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-REV-030 | Settlement statement | Produce, per counterparty per cycle, a statement showing gross transaction value, commission, fees, taxes, adjustments, holds and net payable, reconcilable independently by the counterparty | **P0** | L5 |
| FR-REV-031 | Deduction hierarchy | Apply deductions in a fixed, published order — commission, platform fees, taxes withheld, refunds, chargebacks, clawbacks, reserve — with each step visible on the statement | **P0** | L5 |
| FR-REV-032 | Escrow ledger | Hold funds collected on behalf of a counterparty as a segregated liability from the moment of collection, in a purpose-designated account, never available to operations | **P0** | L5 |
| FR-REV-033 | Reserve and release policy | Apply a published rolling reserve against expected refunds and quality claims, and release it on a defined schedule rather than at discretion | P1 | L5 |
| FR-REV-034 | Payout run | Generate a payout proposal per cycle, apply holds, obtain approval within the authority matrix, and release to M50 as a payment instruction batch | **P0** | L5 |
| FR-REV-035 | Payout hold | Place a hold on a counterparty's payout for a defined reason — dispute, quality investigation, incomplete KYC, tax status — with a named raiser and a release authority | **P0** | L5 |
| FR-REV-036 | Payout confirmation | Track every payout through M50 to bank or wallet confirmation and reflect the outcome on the counterparty's ledger and statement | **P0** | L5 |
| FR-REV-037 | Withholding on payouts | Apply tax withholding on payouts as determined by M51, and provide the counterparty with the certificate | **P0** | L5 |
| FR-REV-038 | Clawback and chargeback | Recover an over-payment, a refunded transaction or a chargeback from the counterparty's next settlement, or as a receivable where no settlement follows | **P0** | L5 |
| FR-REV-039 | Settlement dispute | Log a counterparty's settlement dispute against specific lines, hold only the disputed amount, route it for resolution and track it to a coded outcome | **P0** | L5 |
| FR-REV-040 | Self-billing document | Issue the self-billed document where the arrangement requires it, in the statutory format determined by M51 | P1 | L5 |
| FR-REV-041 | Three-way settlement reconciliation | Reconcile, per cycle, what the customer paid (M20/M50), what the scheme says is owed (M53), and what was disbursed (M50), and report any difference before the cycle closes | **P0** | L5 |
| FR-REV-042 | Counterparty portal presentment | Present statements, transaction detail, deductions, holds, payout status and dispute raising in P07 (sellers) and P12 (partners) | **P0** | L5 |
| FR-REV-043 | Payout calendar | Publish the payout cycle and cut-off calendar to counterparties, and adhere to it | **P0** | L5 |
| FR-REV-044 | Brand partner settlement | Account for and settle brand-partner arrangements where a revenue share or rebate applies, distinct from warranty claim receivables owned by M20 | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Schedules generated, never entered** | The normal path has no manual schedule creation. Manual adjustment requires CFO approval, carries a reason and evidence, and is counted as a control metric — mirroring M19's treatment of manual journals |
| T-02 | **Recognition determinism and reproducibility** | Re-running a recognition period over the same contract state and the same schedule versions produces byte-identical release amounts. This is what makes a prior-period revenue figure defensible |
| T-03 | **Immutable schedule lines after release** | A released schedule line is never edited. A modification creates a new schedule version with a documented treatment; the prior version is retained and referenced |
| T-04 | **Settlement calculation determinism** | Given the same transactions and the same scheme version, settlement produces identical figures. Every settlement line records the scheme version that produced it |
| T-05 | **Three-way settlement assertion** | Collected (M20/M50) − owed (M53) − disbursed (M50) must reconcile to zero plus known holds, per cycle per counterparty. A non-zero unexplained difference blocks the cycle from closing |
| T-06 | **Escrow segregation enforced technically** | Escrow balances map to bank accounts whose purpose designation in M50 (FR-TRE-003) forbids their use for operational payment. Enforced in the payment-run path, not by policy |
| T-07 | **Payout idempotency** | Each payout instruction carries an idempotency key through M50 to the bank. A retried payout run never double-pays a seller — an error that is unrecoverable in reputational terms |
| T-08 | **Monetary discipline** | All amounts `Monetary` with explicit currency (AS-10). Allocation across obligations resolves rounding at a declared point, with the residual assigned by a fixed rule so that allocated amounts always sum exactly to the transaction price |
| T-09 | **Scheme version effective dating** | Commission and reserve schemes are effective-dated and evaluated against the transaction date, never the calculation date. A retrospective scheme change cannot alter a settled transaction |
| T-10 | **Volume envelope** | W4 core: ~30,000–60,000 active obligations (AMC, RAMC, extended warranty, managed services, rentals) generating ~400,000 schedule lines/year. W7 extension: at BO-12's 25% of job volume, ~60,000+ marketplace transactions/year across 500–2,000 sellers, settled on a published cycle |
| T-11 | **Recognition run performance** | A full monthly recognition run across all entities and obligations completes in ≤ 30 minutes; the deferred-to-contract reconciliation in ≤ 10 minutes |
| T-12 | **Event emission via outbox** | Every recognition, commission and settlement state change emits a domain event through the transactional outbox (AS-08); M19, M50, M20, M12 and M54 consume |
| T-13 | **Multi-entity scoping** | Contracts, schedules, commission and settlement are entity-scoped; a settlement cannot cross entities (AS-03) |
| T-14 | **Counterparty data protection** | Seller and partner bank and wallet details are field-level encrypted, masked, and access-logged (AS-14) |
| T-15 | **Statement reproducibility** | A statement issued to a counterparty is stored as issued and is byte-reproducible; a later recalculation appears as an adjustment on a subsequent statement, never as a silent restatement of a delivered one |
| T-16 | **Retention** | Contracts, obligations, schedules, statements, settlements and payout evidence retained seven years and queryable |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M53 |
|---|---|---|
| **CFO** | Cannot state deferred revenue with confidence; carries a misstatement risk on every multi-period product | Signs a revenue figure reconciled to contracts, with a waterfall the auditor can follow |
| **Finance Manager** | Would maintain AMC and warranty deferral in a spreadsheet | Reviews a generated recognition run and works exceptions |
| **External auditor** | Would test revenue by sampling contracts and rebuilding schedules | Tests the schedule generation control and reconciles the waterfall |
| **Marketplace seller** | Does not exist yet; on other platforms, receives an opaque payout | Receives a statement they can reconcile line by line, on a published calendar |
| **Marketplace operations officer** | Would answer payout queries from a spreadsheet | Points the seller at their own portal; handles genuine disputes only |
| **Alliance / referral partner** | Chases their commission by email | Sees earned commission accrue in P12 and knows the payout date |
| **CCO** | Cannot see which revenue streams are recognised versus merely billed | Sees periodised revenue by stream, which is the only basis for judging a new offer |
| **Corporate Services Head** | Judges MSP and rental performance on billing | Judges them on earned revenue, matched to cost by M54 |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Marketplace viability** | 100% payout accuracy on a published calendar, with statements sellers can reconcile independently | Enables **BDT 84 lac/year** marketplace commission and ads (Exec Summary §6.2), and underwrites **BO-12**'s 25%-of-volume target. Payout failure is the identified route to marketplace collapse |
| **Managed services revenue integrity** | MSP contracts recognised over the service period rather than on billing | Makes **BDT 95 lac/year** MSP contribution (BO-11's ≥ 12% of revenue) a measurable number rather than a billing artefact |
| **Rental revenue periodisation** | Straight-line recognition over the rental term, paired with M49 depreciation | Makes **BDT 48 lac/year** rental gross margin and BO-13's 55% margin target real |
| **AMC/RAMC and extended warranty integrity** | Deferred and released over the protection period, not recognised on sale | Protects the **BDT 72 lac/year** AMC renewal uplift from being reported as a one-off spike, and supports genuine renewal analysis |
| **Misstatement risk elimination** | Schedules generated from contracts; manual release requires CFO approval | Removes the "revenue recognised in the wrong period" risk rated **high** in `_CATEGORY_OVERVIEW.md` §10 |
| **Revenue leakage closure** | Contract obligations tracked to satisfaction, with unbilled contract assets visible | Works with M20 to hold total leakage below 0.5% |
| **Commission accuracy for partners** | Calculation from the scheme, transparent to the counterparty, recalculated on amendment | Makes the Partner Alliance and referral programmes scalable rather than administratively capped |
| **Audit efficiency** | Waterfall and contract reconciliation produced, not assembled | Reduces the most examined area of the audit to a control test |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Reportable revenue** | Revenue is the number every external party looks at first — auditor, bank, investor, brand partner. A figure that reconciles to contracts is a different asset from one that reconciles to invoices |
| **Marketplace trust** | Sellers are a two-sided market's scarce side. Transparent, punctual, reconcilable settlement is the product as much as the job flow is |
| **Escrow integrity** | Money held for third parties never touching operating cash is a governance position the Company can state publicly — and a precondition if the marketplace ever attracts regulatory attention |
| **IFRS/BFRS conformance** | The service-versus-assurance warranty distinction, applied systematically, in a business whose core operation is warranty work |
| **Commercial agility** | A new bundled offer needs an obligation template and an SSP, not a finance project. This is what allows 14 revenue streams to become 16 |
| **Institutional memory** | Revenue treatment for each product lives in versioned configuration, not in the head of whoever built the spreadsheet |
| **Wave 7 gate discipline** | 100% payout accuracy as a stated gate criterion means the marketplace does not launch on a hope |

---

## 8. Lifecycle & State Models

### 8.1 Performance Obligation & Revenue Schedule

```
  OPERATIONAL DOCUMENTS (M08 contract · M39 subscription · M20 invoice · M01 job · M13 rental)
        │
        ▼
  ┌──────────────────────┐
  │  REVENUE CONTRACT    │  constructed, not entered
  │  (accounting view)   │
  └──────────┬───────────┘
             │ obligations identified from M37 templates
             ▼
  ┌──────────────────────┐   SSP allocation across obligations
  │  OBLIGATION          │
  │  IDENTIFIED          │
  └──────────┬───────────┘
             │ schedule generated
             ▼
  ┌──────────────────────┐
  │  DEFERRED            │  ◄── contract liability on the balance sheet
  │  (unsatisfied)       │
  └──────┬──────┬────────┘
         │      │ modification
         │      ▼
         │  ┌──────────────────────┐
         │  │ RESCHEDULED          │  prospective · catch-up · separate contract
         │  │ (new version, prior  │
         │  │  version retained)   │
         │  └──────┬───────────────┘
         │◄────────┘
         │ progress measured / trigger met
         ▼
  ┌──────────────────────┐
  │  PARTIALLY SATISFIED │  ── each release posts to M19
  └──────────┬───────────┘
             │ fully satisfied
             ▼
  ┌──────────────────────┐   cancellation / refund / credit note
  │  SATISFIED           │──────────────────────────────┐
  │  (fully recognised)  │                              ▼
  └──────────────────────┘                    ┌──────────────────────┐
                                              │  REVERSED            │
                                              │  (obligation         │
                                              │  extinguished or     │
                                              │  restored)           │
                                              └──────────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Revenue contract | Operational documents representing a customer arrangement are identified | System |
| Revenue contract | Obligation identified | Obligations separated using M37 templates; transaction price determined and allocated on SSP | System |
| Obligation identified | Deferred | Schedule generated from the contract | System |
| Deferred | Partially satisfied | A recognition trigger fires — time elapsed, milestone accepted, usage consumed, delivery confirmed | System |
| Deferred / Partially satisfied | Rescheduled | Contract modified; treatment determined and a new schedule version created | System / Finance Manager |
| Partially satisfied | Satisfied | All progress measures complete | System |
| Any state | Reversed | Cancellation, refund or credit note affecting the obligation | System |
| Any state | Manually adjusted | **CFO approval** with reason and evidence; reported on the manual-release register | CFO |

### 8.2 Settlement Cycle

```
  TRANSACTIONS ACCUMULATE (marketplace order · partner referral · revenue share)
        │  commission calculated per transaction, from the scheme version in force
        ▼
  ┌──────────────────────┐
  │  COMMISSION ACCRUED  │  counterparty ledger builds; escrow holds the customer's money
  └──────────┬───────────┘
             │ cycle cut-off reached
             ▼
  ┌──────────────────────┐
  │  STATEMENT COMPILED  │  gross · commission · fees · tax withheld · refunds ·
  │                      │  chargebacks · clawbacks · reserve · NET
  └──────────┬───────────┘
             │ three-way reconciliation: collected − owed − disbursed
             ▼
  ┌──────────────────────┐  difference   ┌──────────────────────┐
  │  RECONCILED          │──────────────►│  CYCLE BLOCKED       │
  └──────────┬───────────┘               └──────────────────────┘
             │ statement issued to counterparty (P07 / P12)
             ▼
  ┌──────────────────────┐   dispute raised   ┌──────────────────────┐
  │  PAYOUT PROPOSED     │───────────────────►│  DISPUTED (disputed  │
  └──────────┬───────────┘                    │  amount held only)   │
             │ hold rules evaluated           └──────────────────────┘
             ▼
  ┌──────────────────────┐   hold applied    ┌──────────────────────┐
  │  APPROVED            │──────────────────►│  HELD (reason, raiser│
  └──────────┬───────────┘                   │  release authority)  │
             │ released to M50                └──────────────────────┘
             ▼
  ┌──────────────────────┐   bank/wallet fails  ┌──────────────────────┐
  │  RELEASED            │─────────────────────►│  PAYOUT FAILED       │
  └──────────┬───────────┘                      └──────────────────────┘
             │ confirmation
             ▼
  ┌──────────────────────┐
  │  PAID                │  escrow released; counterparty ledger cleared
  └──────────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Commission accrued | A qualifying transaction completes; commission calculated from the scheme version in force at the transaction date | System |
| Commission accrued | Statement compiled | Cycle cut-off reached per the published calendar | System |
| Statement compiled | Reconciled | Collected, owed and disbursed reconcile to zero plus known holds | System |
| Statement compiled | Cycle blocked | Unexplained difference in the three-way reconciliation | System |
| Reconciled | Payout proposed | Statement issued to the counterparty and the dispute window opened | System |
| Payout proposed | Held | A hold reason applies — dispute, quality investigation, incomplete KYC, tax status | Marketplace Ops / Finance Manager |
| Payout proposed | Disputed | Counterparty disputes specific lines; only the disputed amount is held | Counterparty |
| Payout proposed | Approved | Approved within the authority matrix; withholding applied per M51 | Finance Manager / CFO |
| Approved | Released | Payment instruction batch passed to M50 with an idempotency key | System |
| Released | Paid | M50 confirms bank or wallet receipt; escrow released; ledger cleared | M50 |
| Released | Payout failed | Bank or wallet rejection | M50 |

### 8.3 Escrow Balance Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Collected | Customer money received for a transaction where a third party is entitled to a share — a liability from this moment | Cycle cut-off |
| Held in escrow | Segregated in a purpose-designated account; **never available to operations** | Statement compiled |
| Allocated | Assigned to a counterparty's settlement statement | Reserve applied |
| Reserved | The published rolling reserve portion retained against expected refunds and claims | Reserve release schedule reached |
| Released to payout | Included in an approved payout | Paid |
| Returned to customer | The underlying transaction is refunded before settlement | — |
| Forfeited / adjusted | Applied against a clawback or chargeback under the deduction hierarchy | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-REV-01 | Revenue schedules are generated from contracts; a manual schedule or manual release requires **CFO approval**, a reason and evidence, and is separately reported | **H** | CFO |
| BRU-REV-02 | Issuing an invoice never, by itself, recognises revenue; recognition follows satisfaction of the obligation | **H** | CFO |
| BRU-REV-03 | Every warranty-bearing item carries a mandatory assurance-or-service classification; there is no default and no unspecified value | **H** | CFO |
| BRU-REV-04 | A released schedule line is never edited; a modification creates a new schedule version with the prior version retained | **H** | CFO |
| BRU-REV-05 | Allocated amounts across obligations always sum exactly to the transaction price; the rounding residual is assigned by a fixed rule | **C** | Finance Manager |
| BRU-REV-06 | Revenue cannot be recognised into a period hard-closed in M19 | **H** | CFO |
| BRU-REV-07 | Deferred revenue must reconcile to the sum of open contract obligations before the period may close | **H** | CFO |
| BRU-REV-08 | Marketplace revenue is presented gross or net per the single declared principal-or-agent position; the presentation cannot vary by transaction (BRU-FIN-08) | **H** | CFO |
| BRU-REV-09 | **The marketplace presentation is not configured until decision D-03 is settled by external opinion**; until then, marketplace revenue accounting is refused rather than defaulted | **H** | CFO |
| BRU-REV-10 | Commission is calculated from the scheme version in force at the transaction date; a scheme change never applies retrospectively to settled transactions | **H** | CCO / CFO |
| BRU-REV-11 | Commission on an amended, refunded or cancelled transaction is recalculated by posting a differential, never by replacing the original calculation | **H** | Finance Manager |
| BRU-REV-12 | Funds collected on behalf of a counterparty are a liability from the moment of collection and are held in a purpose-designated account, never available to operations | **H** | CFO |
| BRU-REV-13 | A settlement cycle cannot close while the three-way reconciliation — collected, owed, disbursed — shows an unexplained difference | **H** | CFO |
| BRU-REV-14 | Deductions are applied in the fixed published order, and every step is visible on the counterparty's statement | **H** | CFO |
| BRU-REV-15 | The reserve rate and release schedule are published policy; they are never varied for an individual counterparty without CCO and CFO approval | **A** | CFO |
| BRU-REV-16 | A payout hold requires a reason from the controlled taxonomy, a named raiser and a defined release authority | **H** | Finance Manager |
| BRU-REV-17 | A counterparty dispute holds only the disputed amount, never the whole payout | **H** | CFO |
| BRU-REV-18 | A payout instruction replayed at any layer produces exactly one disbursement | **H** | CTO |
| BRU-REV-19 | Withholding determined by M51 is applied to every applicable payout, and the certificate is provided to the counterparty | **H** | CFO |
| BRU-REV-20 | A payout cannot be released to a counterparty whose onboarding, KYC or tax status is incomplete in M12/M33 | **H** | CFO |
| BRU-REV-21 | A statement issued to a counterparty is immutable; a recalculation appears as an adjustment on a later statement | **H** | CFO |
| BRU-REV-22 | The payout calendar is published to counterparties and adhered to; a cycle change requires notice per the counterparty agreement | **H** | CCO |
| BRU-REV-23 | A user who approves a marketplace seller cannot approve that seller's payout (SOD-06) | **H** | CFO |
| BRU-REV-24 | Payouts cannot cross legal entities | **H** | CFO |
| BRU-REV-25 | Contract cost capitalisation follows a documented policy approved by the CFO and the external auditor; it is never applied case by case | **H** | CFO |
| BRU-REV-26 | Recognition is deterministic: re-running a period over the same contract state produces identical amounts | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.revenue.contract` | `fix_revenue_contract` | The constructed accounting view of a customer arrangement | entity_id, customer_id, source_refs_json (M08/M39/M20/M01/M13), inception_date, term_start, term_end, transaction_price, currency, presentation (gross/net), business_line_id, state, modification_count |
| `fix.performance.obligation` | `fix_performance_obligation` | A distinct promise in the contract | contract_id, sequence, catalogue_item_id, obligation_template_id, description_en, description_bn, warranty_class (assurance/service/na), satisfaction_type (over_time/point_in_time), progress_measure (time/milestone/usage/delivery), allocated_price, ssp_used, ssp_method, recognised_to_date, deferred_balance, state |
| `fix.obligation.template` | `fix_obligation_template` | Per-product accounting treatment | catalogue_item_id or item_category, default_satisfaction_type, default_progress_measure, warranty_class, separability_rule, version, effective_from, approved_by |
| `fix.ssp` | `fix_ssp` | Stand-alone selling price | catalogue_item_id, entity_id, method (observable/adjusted_market/cost_plus/residual), value, currency, tolerance_pct, effective_from, effective_to, approved_by |
| `fix.revenue.schedule` | `fix_revenue_schedule` | Schedule header | obligation_id, version, generation_source (contract/manual), generated_at, total_amount, pattern, start_date, end_date, state, supersedes_version, manual_reason, cfo_approved_by |
| `fix.revenue.schedule.line` | `fix_revenue_schedule_line` | One planned or actual release | schedule_id, period_id, planned_date, planned_amount, recognised_amount, recognised_at, trigger_type, trigger_ref, gl_entry_ref, state, immutable_after |
| `fix.recognition.run` | `fix_recognition_run` | A periodic recognition execution | entity_id, period_id, run_at, run_by, obligations_processed, lines_released, total_recognised, inputs_hash, state, gl_batch_ref |
| `fix.contract.liability` | `fix_contract_liability` | Deferred revenue position | contract_id, obligation_id, entity_id, period_id, opening, additions, releases, modifications, reversals, closing, gl_control_account_id |
| `fix.contract.asset` | `fix_contract_asset` | Unbilled revenue | contract_id, obligation_id, entity_id, amount, arose_at, reclassified_to_receivable_at, invoice_id |
| `fix.contract.modification` | `fix_contract_modification` | A change and its treatment | contract_id, modification_date, nature, treatment (separate_contract/prospective/cumulative_catchup), price_change, obligation_changes_json, catch_up_amount, approved_by, evidence_doc_id |
| `fix.revenue.reversal` | `fix_revenue_reversal` | Reversal on cancel/refund/credit | obligation_id, trigger (cancellation/refund/credit_note), source_doc_ref, reversed_amount, obligation_outcome (extinguished/restored), gl_entry_ref |
| `fix.revenue.waterfall` | `fix_revenue_waterfall` | Period movement, reconciled | entity_id, period_id, business_line_id, opening_deferred, additions, releases, modifications, reversals, closing_deferred, gl_control_balance, difference, reconciled_at |
| `fix.remaining.obligation` | `fix_remaining_obligation` | Unsatisfied obligation disclosure | entity_id, as_at, business_line_id, amount, expected_period_band |
| `fix.contract.cost` | `fix_contract_cost` | Capitalised contract cost | contract_id, cost_type (obtaining/fulfilling), amount, amortisation_pattern, amortised_to_date, balance, policy_ref |
| `fix.commission.scheme.ref` | `fix_commission_scheme_ref` | Cached scheme version from M12 | scheme_id (M12), version, effective_from, effective_to, rules_json, cached_at |
| `fix.commission.entry` | `fix_commission_entry` | Commission on one transaction | counterparty_party_id, transaction_type, transaction_ref, transaction_date, gross_value, scheme_version, tier_applied, rate, commission_amount, currency, entity_id, state, differential_of_entry_id, recognised_period_id |
| `fix.commission.ledger` | `fix_commission_ledger` | Counterparty commission position | counterparty_party_id, entity_id, period_id, opening, accrued, adjusted, cleared, closing |
| `fix.settlement.counterparty` | `fix_settlement_counterparty` | Settlement configuration per party | party_id, type (seller/partner/referrer/courier/brand), entity_id, payout_cycle, payout_method, bank_or_wallet_details (encrypted), reserve_rate, reserve_release_days, kyc_state, tax_profile_ref, onboarding_complete, state |
| `fix.settlement.cycle` | `fix_settlement_cycle` | A settlement period | entity_id, counterparty_type, cycle_reference, period_from, period_to, cut_off_at, statement_issue_at, payout_date, state |
| `fix.settlement.statement` | `fix_settlement_statement` | The counterparty's statement — **immutable once issued** | cycle_id, counterparty_party_id, gross_value, commission, platform_fees, tax_withheld, refunds, chargebacks, clawbacks, reserve_applied, reserve_released, adjustments, net_payable, currency, issued_at, document_id, statement_hash, state |
| `fix.settlement.line` | `fix_settlement_line` | One transaction on a statement | statement_id, transaction_type, transaction_ref, transaction_date, gross, commission, fees, tax, net, deduction_sequence, notes |
| `fix.settlement.reconciliation` | `fix_settlement_reconciliation` | The three-way proof | cycle_id, counterparty_party_id, collected_amount (M20/M50), owed_amount (M53), disbursed_amount (M50), held_amount, difference, explanation, state, reconciled_at |
| `fix.escrow.balance` | `fix_escrow_balance` | Funds held for a counterparty | counterparty_party_id, entity_id, bank_account_id (purpose=escrow), collected, allocated, reserved, released, returned, balance, as_at |
| `fix.escrow.movement` | `fix_escrow_movement` | One escrow event | escrow_balance_id, movement_type (collect/allocate/reserve/release/return/forfeit), amount, source_ref, occurred_at, gl_entry_ref |
| `fix.payout.run` | `fix_payout_run` | A payout cycle execution | cycle_id, entity_id, proposal_total, held_total, final_total, currency, state, prepared_by, approved_by, released_at, instruction_batch_id (M50), idempotency_key |
| `fix.payout.line` | `fix_payout_line` | One counterparty payout | run_id, counterparty_party_id, statement_id, gross_payable, tax_withheld, net_amount, method, state, bank_confirmation_ref, failure_reason |
| `fix.payout.hold` | `fix_payout_hold` | Hold on a payout | counterparty_party_id, statement_id, amount_held, reason_code, raised_by, raised_at, release_authority_role, released_by, released_at, release_reason |
| `fix.settlement.dispute` | `fix_settlement_dispute` | Counterparty dispute | statement_id, line_ids, disputed_amount, reason_code, raised_by, raised_at, assigned_to, state, outcome_code, resolved_at, adjustment_ref |
| `fix.clawback` | `fix_clawback` | Recovery from a counterparty | counterparty_party_id, origin (refund/chargeback/overpayment/quality), amount, source_ref, recovery_method (next_settlement/receivable), recovered_amount, balance, state |
| `fix.self.billing.document` | `fix_self_billing_document` | Self-billed document where required | counterparty_party_id, statement_id, statutory_format_ref (M51), sequence_number, issued_at, document_id |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.contract`, `fix.contract.sla`, `fix.entitlement` | M08 | Read as the source of a revenue contract |
| `fix.subscription`, `fix.billing.schedule` | M25 / M39 | Read as a source; the billing schedule is distinct from the revenue schedule |
| `fix.ar.invoice`, `fix.ar.credit.note`, `fix.ar.receipt` | M20 | Read as trigger and as contract-balance movement |
| `fix.price.resolution.log` | M11 | Read the commercial price as the transaction-price input |
| `fix.catalogue.item`, `fix.catalogue.category` | M37 | Read for obligation templates and warranty classification |
| `fix.commission.scheme`, `fix.seller`, `fix.marketplace.job` | M12 | Read the scheme and the seller; **M12 defines, M53 calculates and pays** |
| `fix.rental.agreement`, `fix.rental.agreement` | M13 | Read as a source of over-time revenue |
| `fix.service.order`, `fix.work.order` | M01 / M02 | Read as a satisfaction trigger |
| `fix.brand.claim` | M09 | Read for claim-driven recognition and assurance-warranty cost |
| `fix.tax.determination`, `fix.withholding.determination` | M51 | Call for settlement tax and payout withholding |
| `fix.payment.instruction`, `fix.bank.account` | M50 | Instruct payouts; escrow account purpose designation |
| `fix.gl.account`, `fix.fiscal.period` | M19 | Read for period state and control-account reconciliation |
| `fix.party`, `fix.party` | M33 | Read counterparty identity and payment details |
| `fix.loyalty.liability` | M10 | Read for any material deferral or breakage treatment |
| `fix.asset` (rental pool) | M17 / M49 | Read for the asset paired with rental revenue |
| `fix.document` | M24 | Store statements, self-billing documents and evidence |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-REV-01 | A contract, subscription, rental or qualifying invoice is created | Construct or extend the revenue contract, identify obligations from M37 templates, determine and allocate the transaction price on SSP, and generate schedules | Hold as an exception with the missing input named — template, SSP or classification; **never generate a schedule on an assumption** |
| AUT-REV-02 | A warranty-bearing item has no assurance-or-service classification | Refuse to create the obligation and raise a high-priority exception to the CFO and the catalogue owner | Hard block |
| AUT-REV-03 | An item has no SSP or an SSP outside its tolerance band | Hold allocation, raise an exception, and route to the Finance Manager | Hard block on that contract only |
| AUT-REV-04 | Period end | Execute the recognition run per entity, release due schedule lines, and raise the release events to M19 | Halt the run, report the failing obligations, and block the M19 close task |
| AUT-REV-05 | A recognition trigger fires mid-period (milestone accepted, usage consumed, delivery confirmed) | Release the corresponding schedule line and raise the event to M19 | Queue for the next recognition run |
| AUT-REV-06 | A contract is modified in M08 or M39 | Determine the modification treatment, create a new schedule version retaining the prior, and post any cumulative catch-up | Hold the modification and route to the Finance Manager |
| AUT-REV-07 | An invoice is cancelled, credited or refunded in M20 | Reverse the affected recognition, restore or extinguish the obligation, and raise the event to M19 | High-priority exception |
| AUT-REV-08 | Period end | Reconcile deferred revenue to the sum of open obligations and to the M19 control account, and publish the waterfall | Report the difference and **block the M19 close** |
| AUT-REV-09 | A qualifying transaction completes | Calculate commission from the scheme version in force at the transaction date and accrue it to the counterparty ledger | Queue and retry; alert on repeated failure. Never accrue at a guessed rate |
| AUT-REV-10 | An underlying transaction is amended, refunded or cancelled | Recalculate commission and post the differential, referencing the original entry | High-priority exception |
| AUT-REV-11 | Customer money is collected on a transaction where a third party is entitled | Record the escrow liability against the counterparty in the purpose-designated account | Hard alert; escrow is never implicit |
| AUT-REV-12 | Settlement cycle cut-off reached | Compile the statement, apply the deduction hierarchy in order, apply the reserve, and run the three-way reconciliation | Cycle held; counterparties notified of the delay per the agreement |
| AUT-REV-13 | Three-way reconciliation shows an unexplained difference | Block the cycle from closing, raise an exception with the counterparty and amount named | Hard block |
| AUT-REV-14 | Statement reconciled | Issue the statement to the counterparty in P07/P12, store it immutably with its hash, and open the dispute window | Retry delivery; escalate after the configured period |
| AUT-REV-15 | Payout proposal generated | Evaluate hold rules — dispute, quality investigation, KYC, tax status — and apply holds before approval | Hold applied conservatively; a payout is never released past an unevaluated rule |
| AUT-REV-16 | Payout approved | Request withholding determination from M51, apply it, and release the batch to M50 with an idempotency key | **Refuse release without determination** |
| AUT-REV-17 | M50 confirms a payout | Clear the counterparty ledger, release the escrow, and update the statement status in the portal | Retain as released and report on the unconfirmed list |
| AUT-REV-18 | M50 reports a payout failure | Restore the counterparty balance, notify them with the reason, and flag the payment details for re-verification | High-priority exception |
| AUT-REV-19 | A refund or chargeback occurs after settlement | Create a clawback and recover it from the next settlement, or raise a receivable where no settlement follows | Clawback recorded and aged |
| AUT-REV-20 | Reserve release schedule reached | Release the reserved amount into the next settlement | Reserve remains held and appears on the reserve-ageing report |
| AUT-REV-21 | A counterparty raises a settlement dispute | Hold only the disputed amount, assign by reason code, and start the resolution clock | Dispute recorded and escalated |
| AUT-REV-22 | A marketplace revenue-accounting decision is required and D-03 is unsettled | **Refuse the accounting treatment** and report; marketplace revenue cannot be recognised until the position is declared | Hard block — by design |
| AUT-REV-23 | Daily | Publish the manual-release register, unbilled contract-asset ageing, escrow balance by counterparty, payout-hold register and settlement-exception list | Report with a data-availability warning |

---

## 12. Interfaces

### 12.1 Upstream — M53 Consumes

| Source | What | Mechanism |
|---|---|---|
| M08 Contract & SLA | Contract inception, terms, entitlement, modification, termination | Events + REST |
| M39 Subscription & Recurring Billing | Subscription creation, cycle, plan change, cancellation | Events |
| M20 Receivables | Invoice issued, credit note, cancellation, receipt applied | Events |
| M11 Pricing | The commercial price underlying the transaction price | REST |
| M37 Catalogue | Obligation templates, warranty classification, item classification | REST |
| M12 Marketplace & Sellers | **Commission scheme definitions and versions**; seller identity, onboarding and KYC state; marketplace orders | REST + events |
| M13 Rental & EaaS | Rental agreements and periods | Events |
| M01 / M31 Service & Workshop | Job completion as a satisfaction trigger | Events |
| M05 Managed Services | Service period and milestone acceptance | Events |
| M06 Data Services | Engagement milestones | Events |
| M09 Warranty & Claims | Claim events for warranty revenue and assurance-warranty cost | Events |
| M51 Tax & Regulatory | Tax treatment of settlements; withholding determination on payouts; the D-03 declared position | REST |
| M50 Treasury & Cash | Payout confirmation, failure and return; escrow account balances | Events |
| M19 General Ledger | Period state; deferred revenue and escrow control-account balances | REST |
| M33 Party Master | Counterparty identity and payment details | REST |

### 12.2 Downstream — M53 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Revenue recognised, deferral created and released, commission accrued, settlement, escrow movement, clawback — as financial events for posting | Events |
| M50 Treasury & Cash | Payout instruction batches; escrow balance expectations | Commands + events |
| M20 Receivables | Contract-asset reclassification to receivable; revenue-affecting credit note consequences | Events + REST |
| M52 Payables | Clawbacks recoverable as a receivable where no settlement follows | Events |
| M51 Tax & Regulatory | Settlement and commission transactions requiring tax treatment | Events |
| M12 Marketplace & Sellers | Seller settlement status, payout state, hold state, dispute state | REST + events |
| M54 Costing & FP&A | Periodised revenue by business line, stream and contract — the correct revenue for margin analysis | Warehouse extract + REST |
| M08 Contract & SLA | Contract financial state: recognised, deferred, remaining | REST |
| M07 CRM | Customer contract value and remaining obligation | REST |
| M25 BI / M62 Data Platform | Revenue, deferral, commission and settlement facts | Warehouse extract |
| P07 Marketplace Seller Portal | Statements, transaction detail, deductions, holds, payout status, dispute raising | REST |
| P12 Partner & Referral Portal | Commission earned, statements and payout status | REST |
| P08 Brand Partner Portal | Brand settlement statements where a revenue share applies | REST |
| P04 Corporate B2B Portal | Contract financial position | REST |
| P03 Admin Portal | Full revenue and settlement workspace | Native |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `revenue.contract_created` | contract, customer, obligations, transaction price, presentation | M19, M54, M08 |
| `revenue.obligation_identified` | obligation, type, satisfaction basis, allocated price, SSP method | M19, M54 |
| `revenue.schedule_generated` | obligation, schedule version, pattern, total | M19, M54 |
| `revenue.recognised` | obligation, period, amount, trigger, dimensions | M19, M54, M25 |
| `revenue.deferred` | obligation, amount, contract liability | M19, M54 |
| `revenue.reversed` | obligation, trigger, amount, outcome | M19, M20, M54 |
| `revenue.schedule_modified` | contract, modification treatment, catch-up, new version | M19, M08, M54 |
| `revenue.manual_release` | obligation, amount, reason, CFO approver | M19, M23, CFO |
| `revenue.waterfall_published` | entity, period, movement, reconciliation result | M19, M54, M25 |
| `revenue.deferred_variance` | entity, period, contract total, GL balance, difference | M19, M23 |
| `commission.accrued` | counterparty, transaction, scheme version, rate, amount | M19, M12, M54 |
| `commission.adjusted` | counterparty, original entry, differential, reason | M19, M12 |
| `settlement.statement_issued` | counterparty, cycle, gross, deductions, net, statement hash | M12, M19, P07, P12 |
| `settlement.reconciled` / `settlement.cycle_blocked` | cycle, counterparty, three-way result | M19, M50, M23 |
| `settlement.payout_released` | run, counterparty, net, withholding, method | M50, M19, M51 |
| `settlement.payout_confirmed` | payout line, bank reference, escrow released | M50, M19, M12, P07 |
| `settlement.payout_failed` | payout line, reason | M50, M12, M33 |
| `settlement.payout_held` | counterparty, amount, reason, raiser | M12, M19, P07 |
| `settlement.dispute_raised` / `settlement.dispute_resolved` | statement, lines, amount, outcome | M12, M27, M23 |
| `settlement.clawback_raised` | counterparty, origin, amount, recovery method | M19, M52, M12 |
| `escrow.movement` | counterparty, type, amount, balance | M19, M50 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-REV-01 | MFS wallets for seller payouts (bKash, Nagad — executed by M50) | Outbound | Payout to sellers who prefer wallet settlement |
| INT-REV-02 | Banking partners (BEFTN — executed by M50) | Outbound | Bank payouts to sellers and partners |
| INT-REV-03 | External auditor | Outbound | Revenue waterfall, contract reconciliation and evidence packs |
| INT-REV-04 | External tax counsel (via M51) | Bidirectional | The **D-03** principal-versus-agent opinion governing both presentation and tax base |
| INT-REV-05 | Legacy AMC/warranty contract records | Inbound, one-time | Opening obligations and deferred balances; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/revenue/contracts` | GET · POST | Revenue contracts and their obligations | P03, M08, M54 |
| `/api/v1/revenue/obligations/{id}` | GET | Obligation detail with schedule and recognition to date | P03, M08, M54 |
| `/api/v1/revenue/schedules/{obligation}` | GET | Schedule versions and lines | P03, auditor |
| `/api/v1/revenue/recognition-runs` | POST · GET | Execute and review a recognition run | P03 |
| `/api/v1/revenue/manual-release` | POST | Request a manual recognition or deferral (CFO approval required) | P03 |
| `/api/v1/revenue/waterfall` | GET | Period waterfall with reconciliation | P03, P06, auditor, M54 |
| `/api/v1/revenue/deferred-balance` | GET | Deferred revenue by contract, obligation, business line | P03, M19, M54 |
| `/api/v1/revenue/remaining-obligations` | GET | Unsatisfied obligation value and expected timing | P03, P06 |
| `/api/v1/revenue/ssp` | GET · POST | Stand-alone selling prices and tolerance bands | P03 |
| `/api/v1/commission/entries` | GET | Commission entries by counterparty and period | P07, P12, P03 |
| `/api/v1/commission/ledger/{counterparty}` | GET | Commission ledger position | P07, P12, P03 |
| `/api/v1/settlement/statements/{counterparty}` | GET | Statements, current and historical | P07, P12, P03 |
| `/api/v1/settlement/statements/{id}/lines` | GET | Transaction-level statement detail | P07, P12 |
| `/api/v1/settlement/cycles` | GET | The published payout calendar and cycle status | P07, P12, P03 |
| `/api/v1/settlement/reconciliation/{cycle}` | GET | Three-way reconciliation result | P03, auditor |
| `/api/v1/payouts/runs` | POST | Create and approve a payout run | P03 |
| `/api/v1/payouts/runs/{id}/release` | POST | Release to M50 (idempotent) | P03 |
| `/api/v1/payouts/holds` | POST · DELETE | Place and release a payout hold | P03, M12 |
| `/api/v1/settlement/disputes` | POST · GET | Raise and track a settlement dispute | P07, P12, P03 |
| `/api/v1/escrow/{counterparty}` | GET | Escrow balance and movement | P07, P03, M50 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; **sole approver of manual revenue release**; approves payout runs above threshold, reserve variations and the D-03 position |
| R26 Finance Manager | C R U A | All entities; recognition runs, reconciliation, settlement cycles, payout preparation and holds |
| R27 Finance Officer | C R | Assigned scope; schedule review, settlement compilation, dispute handling — **cannot approve a payout or a manual release** |
| R04 Chief Commercial Officer | R A | Commission schemes and payout calendar changes; reserve policy with the CFO |
| R24 Marketplace Operations Officer | R U | Marketplace settlements; may raise a payout hold — **cannot approve a payout (SOD-06)** |
| R22 Account Manager (Corporate) | R | Contract financial position for assigned accounts |
| R05 Operations Director | R | Revenue by business line and branch |
| R32 Quality Manager / ISO Coordinator | R | Manual-release register, payout-hold register, dispute register |
| R33 IT / System Administrator | R | Configuration and technical support; **no approval rights** |
| R01 Chief Executive Officer | R A | All; second approver for the highest payout band |
| R38 External Auditor | R | Scoped read-only — contracts, schedules, waterfall, reconciliations |
| R38 Marketplace Seller | R | Own statements, transaction detail, holds, payout status; may raise disputes (P07) |
| R38 Alliance / Referral Partner | R | Own commission and statements (P12) |
| R38 Brand Partner | R | Own settlement statements where a revenue share applies (P08) |
| R37 Corporate Portal User | R | Own contract financial position only (P04) |

**Field-level restrictions.** Counterparty bank and wallet details are field-level encrypted,
masked in every list view, and unmaskable only by R03, R26 and R27 with access logged (AS-14).
Commission rates and tiers of one counterparty are never visible to another. SSP values and
allocation detail are restricted to R01–R04, R26 and R27.

**Segregation of duties.**
- **SOD-06 enforced here:** a user who approves a marketplace seller cannot approve that seller's payout — hard block.
- The user who prepares a payout run cannot approve or release it.
- The user who raises a payout hold cannot be the sole releaser of it.
- A manual revenue release requires CFO approval and can never be self-approved.
- R24 Marketplace Operations Officer can hold a payout but never approve or release one — commercial judgement and money movement are separated.
- The user who authors a commission scheme in M12 cannot approve a settlement calculated under it.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Revenue waterfall** | CFO, auditor, board | Monthly | Opening deferred, additions, releases, modifications, reversals, closing — reconciled to the M19 control account |
| **Deferred revenue to contract reconciliation** | CFO, Finance Manager, auditor | Monthly | Deferred balance against the sum of open obligations, with any difference explained |
| **Revenue disaggregation** | CEO, CFO, CCO, board | Monthly | Recognised revenue by business line, stream, segment, branch, channel and timing pattern across all 14 streams |
| **Remaining performance obligations** | CFO, CEO, board | Quarterly | Unsatisfied obligation value and expected recognition timing — the forward revenue book |
| **Manual release register** | CFO, Quality Manager, auditor | Monthly | Every manual recognition or deferral with reason, evidence and CFO approval |
| **Recognition run log** | Finance Manager, CTO | Per run | Obligations processed, lines released, exceptions, elapsed time |
| **Contract asset ageing** | CFO, Finance Manager | Monthly | Unbilled revenue by age and contract — a leakage indicator alongside M20's |
| **Obligation exception report** | CFO, catalogue owner, Finance Manager | Daily | Items with no template, no SSP, or missing warranty classification — blocking schedule generation |
| **Commission earned and payable** | CFO, CCO, Marketplace Ops | Monthly | Commission by counterparty, scheme, tier and business line |
| **Settlement cycle status** | CFO, Marketplace Ops, CCO | Per cycle | Statements compiled, reconciled, issued, disputed, paid — against the published calendar |
| **Three-way settlement reconciliation** | CFO, auditor | Per cycle | Collected, owed, disbursed and held, per counterparty, with differences |
| **Payout accuracy** | CFO, CCO, CEO | Per cycle | Payouts correct on first issue — **the Wave 7 gate criterion at 100%** |
| **Payout hold register** | CFO, Marketplace Ops, Quality Manager | Weekly | Holds by reason, counterparty, value and age, with release authority |
| **Escrow balance and ageing** | CFO, Treasury (M50), auditor | Daily | Funds held per counterparty, allocated, reserved, released — proving segregation |
| **Settlement dispute register** | CCO, Marketplace Ops, Quality Manager | Weekly | Disputes by reason, value, age and outcome |
| **Clawback and chargeback recovery** | CFO, Marketplace Ops | Monthly | Clawbacks raised, recovered, outstanding by counterparty |
| **Counterparty settlement statement** | Sellers (P07), partners (P12), brands (P08) | Per cycle | Their own gross, deductions, holds and net — the document that keeps them on the platform |
| **Reserve position and release schedule** | CFO, CCO | Monthly | Reserve held by counterparty with release dates |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Seller and partner payout accuracy** *(Wave 7 gate criterion)* | n/a | n/a | **100%** |
| — | Deferred revenue reconciled to contracts | n/a | 100% | **100%** |
| — | Revenue schedules generated automatically (no manual entry) | n/a | 97% | **> 99%** |
| — | Manual revenue releases per period | n/a | < 5 | **< 2** |
| — | Payouts issued on the published calendar date | n/a | 97% | **100%** |
| — | Settlement cycles closing with a clean three-way reconciliation | n/a | 95% | **100%** |
| — | Settlement disputes as % of statements issued | n/a | < 3% | **< 1%** |
| — | Settlement dispute resolution cycle time | n/a | < 7 days | **< 3 days** |
| — | Obligations blocked for missing template, SSP or warranty classification | n/a | < 2% | **Zero** |
| — | Recognition run completion within the close window | n/a | 100% | **100%** |
| — | Revenue leakage — delivered obligations never recognised *(jointly with M20)* | unknown | < 1.5% | **< 0.5%** |
| — | Escrow balance reconciled to the designated bank account | n/a | 100% | **100%** |
| — | Payout failures caused by counterparty payment-detail errors | n/a | < 3% | **< 1%** |
| — | Duplicate payouts | n/a | **Zero** | **Zero** |
| — | Commission recalculations required after settlement | n/a | < 2% | **< 0.5%** |
| — | Audit adjustments to revenue | unmeasured | Zero material | **Zero** |

> **Register note.** M53 has **no KPI identifiers allocated in `06-02`** — the module did not
> exist in the v2.0 register. All sixteen metrics above require allocation, and the **payout
> accuracy and deferred-revenue reconciliation metrics are named in `_CATEGORY_OVERVIEW.md` §8**
> and must be registered as canonical. Recorded as audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — deferred revenue accounts, analytic structures | 10% |
| L2 | OCA `account-financial-tools`, `contract` (recurring structures), `account-financial-reporting` | 14% |
| L3 | Free scheduling and reporting aids | 3% |
| L5 | `cd_revenue_recognition`, `cd_performance_obligation`, `cd_commission_ledger`, `cd_settlement`, `cd_payout_engine`, `cd_escrow` | **73%** |

> Alongside M51, the highest custom share in Category G. Neither IFRS 15 obligation accounting
> nor marketplace settlement exists in the Odoo or OCA ecosystem at any usable depth.

### 16.2 Custom Development

| CD ID | Component | Type | Wave | Effort |
|---|---|---|:--:|---|
| **CD-176** | `cd_performance_obligation` — revenue contract construction, obligation identification and templates, warranty classification enforcement, SSP model and allocation, modification and termination treatment | Odoo module + service | W4 | **6 PW** |
| CD-093 | `cd_revenue_recognition` — schedule generation and versioning, recognition runs, over-time/point-in-time/milestone patterns, contract assets and liabilities, reversal, waterfall and reconciliation | Odoo module + service | W4 | **7 PW** |
| **CD-177** | `cd_commission_ledger` — commission calculation from M12 scheme versions, ledger, differential recalculation, recognition, transparency to counterparties | Odoo module | W4 | 5 PW |
| CD-094 | `cd_settlement` — settlement cycles, statements with the deduction hierarchy, three-way reconciliation, disputes, clawbacks, self-billing documents | Odoo module + service | **W7** | **5 PW** |
| **CD-178** | `cd_payout_engine` — payout runs, hold rules and authority, withholding integration, M50 instruction batching with idempotency, confirmation and failure handling | Odoo module | **W7** | 3 PW |
| **CD-179** | `cd_escrow` — escrow ledger, purpose-designated account binding, reserve policy and release schedule, movement accounting | Odoo module | **W7** | 2 PW |

> **CD register reallocation.** `02-05` §5.2 allocated **CD-093** (`cd_revenue_recognition`) and
> **CD-094** (`cd_settlement`) to **M20**. Both move to **M53** under the v2.1 re-scope. Four new
> IDs, **CD-176…179**, are claimed from the Category G block defined in `M19` §16.2. **All CD IDs
> remain provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M19 General Ledger (W3) | Every recognition, deferral and settlement terminates in a journal entry |
| M20 Receivables (W3) | Invoices are both a trigger and a contract-balance movement |
| M08 Contract & SLA (W4) | Contracts are the primary source of revenue contracts; must land in the same wave |
| M39 Subscription (W4) | Subscription cycles as a source; the billing schedule must be distinguishable from the revenue schedule |
| M37 Catalogue | Obligation templates and **warranty classification** — without these no schedule can be generated |
| M11 Pricing (W3) | The commercial price underlying the transaction price |
| M51 Tax (W4) | Settlement tax treatment and payout withholding |
| M50 Treasury (W3) | Payout execution and the escrow account purpose designation |
| M13 Rental (W6) | Rental revenue periodisation activates with M13 |
| **M12 Marketplace (W7)** | Commission scheme definitions and seller identity — **the W7 extension cannot start without it** |
| **Decision D-03 (external tax opinion)** | **A hard gate on the marketplace extension.** Gross-versus-net presentation and the tax base both derive from it. Marketplace revenue accounting is refused until it is declared |

**Delivers into:** M19 (revenue postings), M50 (payout instructions), M54 (periodised revenue
for margin), M12 (settlement status), P07 and P12 (counterparty statements).

> **The W4 / W7 split.** W4 delivers everything the existing business needs — recognition,
> deferral, obligations, commission for partners and referrers. W7 delivers marketplace seller
> settlement, escrow and the payout engine, arriving with M12. **100% payout accuracy is a Wave 7
> gate criterion**, meaning the marketplace does not go live until settlement is proven.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Open AMC / RAMC contracts | All active contracts | `fix.revenue.contract`, `fix.performance.obligation` | W4 cutover |
| Open extended warranty obligations | All active warranties | `fix.performance.obligation` (service-class) | W4 cutover |
| Open managed-services contracts | All active MSP contracts | `fix.revenue.contract` | W4 cutover |
| Opening deferred revenue balance | Per entity | `fix.contract.liability` + M19 opening journal | **W4 cutover — reconciliation critical** |
| Stand-alone selling prices | All catalogue items with obligations | `fix.ssp` | W4 minus 1 month |
| Obligation templates and warranty classification | All warranty-bearing and multi-period items | `fix.obligation.template` (via M37) | **W4 minus 2 months — blocking** |
| Open partner and referral commission balances | Current only | `fix.commission.ledger` | W4 cutover |
| Open rental agreements | With M13 | `fix.revenue.contract` | W6 |
| Seller settlement history | n/a — marketplace is new | — | W7 |

> **Migration position.** The **opening deferred revenue balance must be rebuilt from the
> underlying contracts, obligation by obligation — not loaded as a total.** A migrated total
> cannot be reconciled to contracts, which makes the module's central control (`deferred revenue
> reconciled to contracts, 100%`) unachievable from day one. Every migrated obligation carries
> its contract reference, term dates, allocated price and recognition-to-date. Where the legacy
> records do not support that reconstruction, the difference is quantified and written off under
> **CFO and external-auditor approval before cutover**, never carried as an unexplained balance.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every revenue schedule in production traces to a contract, subscription, invoice, job or rental — or to a CFO-approved manual release | Full-table assertion query |
| AC-02 | An invoice, on its own, never recognises revenue | Negative test across every revenue stream |
| AC-03 | An obligation cannot be created for a warranty-bearing item without an assurance-or-service classification | Negative test |
| AC-04 | An obligation cannot be allocated without an SSP within its tolerance band | Negative test |
| AC-05 | A manual recognition or deferral requires CFO approval and appears on the register | SoD negative test |
| AC-06 | A released schedule line cannot be edited; a modification creates a new version retaining the prior | Negative test plus version-history assertion |
| AC-07 | Re-running a recognition period over the same contract state produces identical amounts | Determinism test |
| AC-08 | Allocated amounts across obligations sum exactly to the transaction price in every case | Full-table assertion including rounding-edge cases |
| AC-09 | Deferred revenue reconciles to the sum of open obligations and to the M19 control account, every period | Three consecutive monthly closes signed by the CFO |
| AC-10 | A deferred-revenue variance blocks the M19 period close | Scripted close scenario |
| AC-11 | Revenue is reversed correctly on cancellation, refund and credit note, with the obligation restored or extinguished | Scripted scenario per trigger |
| AC-12 | The full monthly recognition run completes within 30 minutes at projected volume | Performance test |
| AC-13 | Commission is calculated from the scheme version in force at the transaction date; a retrospective scheme change does not alter settled transactions | Scripted scenario across a scheme-change boundary |
| AC-14 | Commission on an amended transaction posts a differential referencing the original, never a replacement | Assertion test |
| AC-15 | Funds collected for a counterparty are recorded as an escrow liability at collection and held in a purpose-designated account | Full-table assertion plus an M50 account-purpose test |
| AC-16 | Escrow funds cannot be used in an operational payment run | Negative test through M50's payment path |
| AC-17 | Every settlement cycle passes a clean three-way reconciliation before closing; a difference blocks the cycle | Scripted scenario plus three consecutive live cycles |
| AC-18 | Deductions apply in the fixed published order and every step is visible on the statement | Statement review against the published hierarchy |
| AC-19 | An issued statement is immutable and byte-reproducible; a recalculation appears as a later adjustment | Reproducibility test |
| AC-20 | **Payout accuracy is 100% across three consecutive cycles** — the Wave 7 gate criterion | Three cycles, every payout reconciled to its statement and to the scheme |
| AC-21 | A payout instruction replayed at any layer produces exactly one disbursement | End-to-end idempotency test through M50 |
| AC-22 | A payout cannot be released without an M51 withholding determination | Negative test with the service disabled |
| AC-23 | A payout cannot be released to a counterparty with incomplete onboarding, KYC or tax status | Negative test |
| AC-24 | A user who approves a seller cannot approve that seller's payout | SoD negative test (SOD-06) |
| AC-25 | A counterparty dispute holds only the disputed amount | Scripted scenario |
| AC-26 | Payouts are issued on the published calendar date across three consecutive cycles | Cycle records |
| AC-27 | **Marketplace revenue accounting is refused while D-03 is unsettled**, with no default presentation applied | Negative test |
| AC-28 | Opening deferred revenue is rebuilt obligation by obligation and reconciles to the M19 opening balance | CFO- and auditor-signed reconciliation |
| AC-29 | All counterparty-facing statement and portal content is complete in Bengali | Translation coverage report (AS-12) |
| AC-30 | CFO, external auditor and (for W7) the CCO sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 30 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Decision D-03 — is 1000FiX principal or agent for marketplace transactions?** This determines gross-versus-net revenue presentation here and the VAT base in M51. **Blocks the Wave 7 extension and is the highest-rated commercial risk in the programme** | CFO / CEO / external tax counsel | **Before Wave 7 build — blocking** |
| Q-02 | Which catalogue items are service-type warranties (deferred and released over the period) and which are assurance-type (cost when incurred)? Every warranty-bearing item needs a classification and there is no safe default | CFO / CCO / external auditor | **W4 minus 2 months — blocking** |
| Q-03 | What SSP method applies per item category, and who maintains and approves SSPs? Without SSPs no bundle can be allocated | CFO / CCO | **W4 minus 2 months — blocking** |
| Q-04 | Are rentals operating leases in every case, or do any rental terms require finance-lease treatment under IFRS 16? | CFO / external auditor | W6 (with M13) |
| Q-05 | Is contract cost capitalisation (FR-REV-023) applied, and under what policy? It is P2 and can be deferred if the auditor accepts expensing | CFO / external auditor | W5 |
| Q-06 | What is the marketplace payout cycle — weekly, fortnightly, or on a rolling schedule — and what is the cut-off? This is published to sellers and hard to change afterwards | CCO / CFO | **W7 minus 3 months — commercially binding** |
| Q-07 | What is the reserve/rolling-hold policy — rate, holding period and release schedule? A reserve that is too high suppresses seller supply; too low exposes the Company to refund risk | CCO / CFO | W7 minus 3 months |
| Q-08 | What is the deduction hierarchy, and is it acceptable to publish it to sellers in full? Transparency here is a competitive position, not just a control | CCO / CFO | W7 minus 3 months |
| Q-09 | What are the payout hold reasons and their release authorities? An over-broad hold policy will be read by sellers as arbitrary | CCO / CFO / Marketplace Ops | W7 build |
| Q-10 | Does the seller arrangement require self-billing documents, and in what statutory format? This depends on the D-03 outcome | CFO / M51 / tax consultant | W7 design |
| Q-11 | What is the payout authority matrix by value band, and who are the approvers? | CFO / CEO | W7 build |
| Q-12 | Can the legacy AMC, RAMC and extended-warranty records support obligation-by-obligation reconstruction of the opening deferred balance? If not, what is the approved write-off treatment for the difference? | CFO / external auditor | **W4 minus 3 months — determines migration feasibility** |
| Q-13 | Do partner and referral commissions in W4 need the full settlement machinery, or is commission accrual plus payment through M52 sufficient until W7? | CFO / CCO | W4 design |
| Q-14 | Which brand-partner arrangements involve a revenue share or rebate distinct from warranty claim receivables (FR-REV-044)? | CCO / Warranty Claims Officer | W5 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition, W4/W7 split), §4 (money flow), §5 (boundary map
— "M12 defines; M53 calculates and pays"), §8 (KPIs — payout accuracy 100%, deferred revenue
reconciled 100%), §9 (delivery sequence), §10 (risks — wrong-period recognition, seller payout
failure, **D-03**) ·
`M19_Financial_Accounting_and_General_Ledger.md` (posting engine, control accounts, period
close gate, Category G CD block) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` (invoicing as distinct from recognition,
contract-asset reclassification, revenue leakage) ·
`M50_Treasury_Cash_and_Banking.md` (payout execution, escrow account purpose designation
FR-TRE-003) ·
`M51_Tax_and_Regulatory_Compliance_Bangladesh.md` (settlement tax treatment, payout withholding,
**the shared D-03 determination**) ·
`M52_Accounts_Payable_and_Employee_Expense.md` (settlements as distinct from trade payables) ·
`M54_Cost_Accounting_Budgeting_and_FPA.md` (periodised revenue paired with cost for margin) ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M39_Subscription_and_Recurring_Revenue.md`
(billing schedule vs revenue schedule) ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md`
(obligation templates, warranty classification) ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M12_Marketplace_and_Seller_Ecosystem.md`
(commission scheme definition, seller onboarding) ·
`03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` (P07 seller, P12 partner, P08 brand) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §5 (retired `BIL`),
§7 · `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §6 SOD-06 ·
`05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md` BRU-FIN-08 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` BO-11, BO-12, BO-13

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-008, BR-FIN-011,
§Value-Added Services · `1000FiX_Services_Company_Profile.md` §Value-Added Services (Warranty
Extension Programme, RAMC, Privileged Programme, Partner Alliance Programme, Laptop Rental,
Exchange Offer) · `1000fix_business/Business planning for 1000 fix.docx` §Marketplace, §Rental

**External benchmark and accounting framework**
[IFRS 15 Revenue from Contracts with Customers](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-15-revenue-from-contracts-with-customers/) —
the five-step model, allocation on stand-alone selling prices ·
[IFRS 15 warranties — service-type warranties are separate performance obligations recognised over time; assurance-type warranties are accounted under IAS 37 as costs, not deferred revenue](https://www.cpdbox.com/021-warranties-ifrs-15/) —
the distinction that governs a warranty-service business ·
[Extended warranties as contract liabilities released straight-line over the warranty period](https://accountsexamples.com/extended-warranties-accounting-policy/) ·
[BDO — IFRS 15 in practice](https://www.bdo.global/getmedia/3bbbe2dd-2183-4a64-9df3-eb87a5c9895d/IFRS-AS-IP-IFRS-15-2024-25.pdf) ·
SAP S/4HANA Revenue Accounting and Reporting (RAR) — revenue accounting contracts constructed
from operational documents; performance obligations with fulfilment types; a revenue sub-ledger
separate from billing ·
[Oracle Fusion Cloud Revenue Management](https://www.oracle.com/erp/financial-management/) —
contract identification across sources, obligation templates, SSP hierarchies with tolerance
bands, revenue accounting separate from receivables ·
Zuora RevPro — the revenue waterfall as the primary reconciliation artefact ·
Marketplace settlement practice (Amazon, Shopify, Uber class) — seller statements with a fixed
deduction hierarchy, published payout calendars, rolling reserve and dispute windows ·
[NBR guidance on e-commerce VAT — commission-basis rather than gross-transaction-value taxation](https://www.tbsnews.net/bangladesh/vat-e-commerce-agencies-commissions-only-not-customers) —
evidence bearing on **D-03**

---

*Module M53 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
