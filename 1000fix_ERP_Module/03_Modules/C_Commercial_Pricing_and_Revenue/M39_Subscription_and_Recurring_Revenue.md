---
id: FIX-ERP2-M39
module_id: M39
module_code: SUB
module_name: Subscription & Recurring Revenue
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P1
wave: W4
---

# M39 — Subscription & Recurring Revenue
### Category C · Code `SUB` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M39 |
| **Module code** | `SUB` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | ★ New — split out of M08 and the former M20 "Billing" during v2.1 re-scoping |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 (Odoo `sale_subscription` concepts) + L2 (OCA `contract`, `contract_variable_quantity`, `contract_invoice_*`) + L5 (custom) |
| **Custom modules** | `cd_subscription_engine`, `cd_usage_rating`, `cd_proration`, `cd_recurring_metrics`, `cd_dunning_bridge` |
| **Requirement range** | FR-SUB-001 … FR-SUB-044 |
| **Requirement count** | **44** *(measured; register estimate 30)* |
| **Effort estimate** | **22 person-weeks** *(measured; register estimate 17 PW)* |
| **Depends on** | M08 Contract · M37 Catalogue · M11 Pricing · M36 Quotation · M33 Party Master · M20 Receivable · M51 Tax · M28 Integration · M29 Identity |
| **Depended on by** | M20, M53, M19, M54, M08, M05, M06, M13, M38, M25, M26, M35 |

---

## 2. Purpose

M39 turns a promise into money owed, on a schedule, forever.

Where M08 says *"this customer has a Comprehensive RAMC covering six appliances until 31 March"*,
M39 says *"invoice BDT 4,800 on the first of each month, prorate the two appliances added on the
14th, apply the 8% annual escalation on renewal, and this contributes BDT 4,800 to MRR."*

It is the **billing mechanics** layer for every recurring revenue stream the company operates:
AMC and RAMC subscriptions, managed-service tiers, data-backup subscriptions, rental hire
periods, protection plans billed monthly, marketplace seller subscriptions and any future
as-a-service offering. It also handles **usage-based charges** — remote support hours, storage
volume, incident counts beyond entitlement, overage on any metered dimension.

It does not create the invoice document, post to the ledger, or collect the cash. It computes
what is owed, when, and instructs M20. The category overview is explicit: M39 owns the
mechanics; M08 owns the agreement; M20 owns the money.

### Why It Exists

The v1.0 plan had no subscription module. AMC billing was assumed to be a periodic invoice run
inside billing. That assumption breaks the moment the business does what its plan says it will
do: sell six MSP tiers with usage components, rent equipment by the month, sell backup by the
gigabyte, and let corporate customers add and remove assets mid-cycle.

Without M39 the consequences are predictable and expensive: mid-cycle changes are billed wrong
or not at all; plan upgrades are handled by cancelling and re-creating, destroying history;
usage is billed from spreadsheets; and nobody can state MRR, ARR or churn — the three numbers
that determine whether a recurring-revenue business is working.

The business plan targets recurring revenue as the core of the company's growth: **AMC/RAMC
renewal uplift BDT 72 lac/year**, **MSP contribution BDT 95 lac/year**, **rental margin BDT 48
lac/year**. All three are recurring streams that must be billed accurately, at scale, without
manual intervention.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.10 (BR-BIL-*) | Recurring invoicing, billing cycles, consolidated invoicing |
| ERP BRD §8.8 | AMC billing frequency options and payment terms |
| `05-04` §3.2 | Corporate consolidated invoicing and invoice approval workflow |
| Business Plan §Managed Services | Six MSP tiers, monthly and annual, with usage components |
| Business Plan §RAMC Packages | Six residential packages sold on recurring terms |
| Business Plan §Rental | Periodic hire billing with utilisation-based components |
| Business Plan §Data Backup | Subscription storage services billed by volume |
| `04-00` P04 §Billing | "Consolidated invoices by cycle · itemised breakdown by site, department and asset" |
| `_CATEGORY_OVERVIEW.md` §4.2, §8 | The contract/subscription boundary; billing accuracy KPI > 99.5% |
| `02-02` §2 Category C | Registers M39 as ★ new, P1, W4, CFO-owned |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The subscription object: the billing instance behind a contract, plan or hire |
| 2 | Billing schedules: frequency, anniversary, calendar alignment, arrears/advance, first and final period |
| 3 | Charge model: recurring, one-time, usage-based, tiered, volume, minimum-commitment, overage |
| 4 | Quantity management: seats, assets, sites, devices, licences, storage volume |
| 5 | **Proration** on every mid-cycle event — start, stop, quantity change, plan change, suspension, termination |
| 6 | Plan change: upgrade, downgrade, cross-grade, with credit and charge treatment |
| 7 | Usage collection, rating and aggregation from metered sources |
| 8 | Entitlement-overage rating: charges arising when M08 entitlement is exhausted |
| 9 | Billing run execution: scheduling, batching, dry-run, exception handling, reissue |
| 10 | Consolidated and split billing: by customer, site, department, cost centre, project |
| 11 | Billing instruction to M20: what to invoice, for what period, at what tax treatment, with what breakdown |
| 12 | Credit and adjustment instructions arising from proration, service credits and disputes |
| 13 | Suspension, pause, resume, reactivation and their billing consequences |
| 14 | Cancellation, termination and final-period settlement |
| 15 | Renewal billing: term roll, escalation application, price-change notification |
| 16 | Payment method on file, autopay mandates and retry policy coordination with M20 |
| 17 | Dunning coordination: what a failed payment does to the subscription's state |
| 18 | **Recurring revenue metrics**: MRR, ARR, ACV, TCV, bookings, expansion, contraction, churn, net revenue retention |
| 19 | Cohort and retention analysis by product, segment, channel and vintage |
| 20 | Revenue-recognition basis supplied to M53 (deferred, over-time, usage) |
| 21 | Subscription forecasting and billing-run projection |
| 22 | The subscription API and events consumed by portals, finance and analytics |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| The agreement, its scope, entitlement and SLA | **M08** Contract | M08 defines what was promised; M39 bills it |
| The plan definition (frequency, included quantities, overage units) | **M37** Catalogue | A plan is a catalogue object; a subscription is an instance |
| Rates and prices | **M11** Pricing | Price is a commercial decision |
| Invoice document creation, numbering, delivery, posting | **M20** Receivable | Only Category G creates financial documents |
| Collection, dunning execution, receipts, allocation | **M20** Receivable | M39 supplies the state signal; M20 collects |
| Revenue-recognition schedules, postings and IFRS 15 treatment | **M53** Revenue & Settlement | M39 supplies the basis; M53 recognises |
| Tax rates, VAT calculation, NBR filing | **M51** Tax | M39 supplies the tax class and period; M51 computes |
| General ledger posting | **M19** Financial Accounting | — |
| Service delivery against the subscription | **M01** / **M05** / **M06** / **M13** | Delivery is operational |
| Entitlement balance and consumption | **M08** Contract | M39 rates the *overage*; M08 owns the balance |
| Payment gateway integration and card vaulting | **M20** / **M50** Treasury | Payment infrastructure is a finance-platform concern |
| Loyalty points earned on subscription spend | **M10** Loyalty | — |
| Marketplace commission settlement | **M53** Revenue & Settlement | Different money flow entirely |

### 3.3 Shared Concepts

| Concept | M39's Role | Owning Module |
|---|---|---|
| Subscription | **Owner** | M39 |
| Billing schedule | **Owner** | M39 |
| Proration | **Owner** | M39 |
| MRR / ARR / churn | **Owner** | M39 |
| Contract | Consumes; every subscription has one | M08 |
| Plan definition | Consumes | M37 |
| Rate | Consumes | M11 |
| Entitlement balance | Reads; rates the overage | M08 |
| Invoice | Instructs; never creates | M20 |
| Dunning stage | Consumes; reacts by changing subscription state | M20 |
| Revenue recognition | Supplies the basis | M53 |
| Usage record | **Owner** of rating; source modules own measurement | M39 (rating) / M05, M06, M13 (measurement) |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Oracle Fusion Cloud Subscription Management** | Subscription products, coverage subscriptions, usage-based subscriptions with a rating engine, proration by daily rate with or without credit, MRR normalisation (annual ÷ 12, half-yearly ÷ 6, quarterly ÷ 4), churn and expansion analytics, native ERP integration | **The whole model**: the subscription-vs-contract separation, **daily-rate proration with a declared credit treatment**, **usage rating as a distinct step from billing**, and **MRR normalisation excluding one-time charges**. This is the closest enterprise analogue to what 1000FiX needs | Oracle's product-catalogue coupling; our plans live in M37 |
| **SAP S/4HANA** — billing plans on service contracts, periodic billing | Scheduled billing dates independent of service delivery | The **billing plan independent of delivery** principle — an AMC bills monthly whether or not a visit occurred | SAP's convergent-invoicing and BRIM stack; disproportionate at our scale |
| **Zuora-class subscription billing** | Amendment-driven subscriptions, rating engine, revenue schedules, collections integration, subscription metrics | **Amendment as the change mechanism** — never cancel-and-recreate, because history and MRR movement must survive a plan change — and the **standard metric definitions** (MRR, ARR, expansion, contraction, churn, NRR) | Buying the platform; a licence at this scale would breach the zero-licence-cost principle |
| **Microsoft Dynamics 365 / Business Central recurring billing** | Recurring invoice generation from agreements | Legibility of the billing run for finance staff who are not billing specialists | Its limited proration and usage support |
| **Telecom / utility rating practice** | Metered usage rating, tiered and stepped tariffs, rating windows, rerating | **Rerating**: the ability to correct a rating error and reissue without breaking the ledger — essential because usage sources are imperfect | Full mediation-layer complexity |
| **Odoo 19 + OCA** — `sale_subscription`, `contract`, `contract_variable_quantity`, `contract_invoice_start_end_dates` | Recurring contracts generating invoices on a schedule with variable quantities | The **OCA `contract` recurring-invoicing engine as the L2 base** for schedule generation and invoice-line assembly | Its assumption that the recurring agreement and its billing are one object — M08/M39 must stay separate per the category boundary. OCA `contract` is used here as M39's engine, **not** as M08's contract model |

**Design position.** 1000FiX differs from the benchmarks in five ways.

First, **proration is a hard requirement from day one, not a phase two**. Corporate customers add
and remove devices constantly; residential customers upgrade packages mid-term. A billing engine
that cannot prorate produces either angry customers or lost revenue, and both are worse than the
build cost. Every proration is computed on a daily-rate basis with the credit treatment declared
on the plan, and every prorated line carries a plain-language explanation onto the invoice.

Second, **usage rating must tolerate imperfect sources**. Remote-support hours come from M05,
storage volume from M06, rental utilisation from M13. These sources will be late, will
occasionally double-report, and will sometimes need correction. M39 therefore rates against
declared periods with idempotency keys, supports rerating with a controlled reissue, and never
lets a source correction silently change a closed period.

Third, **MRR is computed once, centrally, with one definition**. In most mid-market companies
MRR is three different numbers in three different spreadsheets. M39 is the single computation,
with one-time charges excluded and non-monthly frequencies normalised, matching the Oracle and
Zuora convention so external benchmarking remains meaningful.

Fourth, **billing runs are boring by design**. Dry-run first, exception queue second, commit
third. A billing run that fails halfway must be resumable, and no customer may be invoiced twice
under any failure mode. The category KPI is **> 99.5% billing accuracy**; that is a systems
property, not a diligence property.

Fifth, **the customer sees what they are being billed for, in Bengali, before the invoice
arrives**. Recurring billing disputes are almost always surprise disputes. P01 and P04 show the
upcoming charge, its composition and any proration, ahead of the run.

---

## 5. Functional Areas & Features

### 5.1 Subscription & Schedule

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SUB-001 | Subscription creation | Create a subscription automatically when an M08 contract with a recurring charge is activated, binding it to the contract, the M37 plan and the M11 rate | P0 | L5 |
| FR-SUB-002 | Billing schedule | Generate the billing schedule from frequency (monthly, quarterly, half-yearly, annual, custom), alignment (anniversary or calendar), and timing (advance or arrears) | P0 | L2 |
| FR-SUB-003 | First and final period | Handle partial first and final periods by daily-rate proration, with the treatment declared on the plan | P0 | L5 |
| FR-SUB-004 | Charge model | Support recurring, one-time, usage-based, tiered, volume, stepped, minimum-commitment and overage charges on one subscription | P0 | L5 |
| FR-SUB-005 | Quantity management | Track billable quantity — devices, sites, seats, licences, storage — and hold its full effective-dated history | P0 | L5 |
| FR-SUB-006 | Multi-line subscriptions | Support many charge lines with independent quantities, rates, frequencies and start dates on one subscription | P1 | L5 |
| FR-SUB-007 | Billing calendar and cut-off | Apply a billing calendar with cut-off rules, working-day handling and public holidays | P1 | L5 |
| FR-SUB-008 | Payment terms | Carry payment terms, due-date derivation and any customer-specific term override from M33 | P0 | L1 |
| FR-SUB-009 | Autopay mandate | Register a payment method on file and an autopay mandate, and coordinate its use with M20 | P1 | L5 |
| FR-SUB-010 | Billing forecast | Project the next twelve billing runs by value and count, for cash forecasting in M50 | P2 | L5 |

### 5.2 Change, Proration & Plan Movement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SUB-011 | Amendment model | Change a subscription by amendment, never by cancel-and-recreate, preserving identity, history and metric continuity | P0 | L5 |
| FR-SUB-012 | Quantity proration | Prorate on daily rate when quantity changes mid-cycle, in both directions, with the credit treatment declared on the plan | P0 | L5 |
| FR-SUB-013 | Asset attach/detach proration | Prorate automatically on M08 asset attachment or detachment, from the effective date | P0 | L5 |
| FR-SUB-014 | Plan upgrade | Apply an upgrade immediately or at next renewal as configured, crediting the unused portion and charging the new plan pro rata | P0 | L5 |
| FR-SUB-015 | Plan downgrade | Apply a downgrade at period end by default, with immediate downgrade permitted only where the plan allows, and never producing a cash refund without approval | P0 | L5 |
| FR-SUB-016 | Cross-grade | Move between plans of equivalent value with correct differential treatment | P2 | L5 |
| FR-SUB-017 | Backdated change | Support a backdated effective date within a governed window, computing catch-up charges or credits, and blocking changes into closed accounting periods | P1 | L5 |
| FR-SUB-018 | Pause and resume | Pause billing for a declared period with a declared entitlement treatment, and resume with correct schedule realignment | P1 | L5 |
| FR-SUB-019 | Suspension on non-payment | Suspend billing and service on the M20 dunning signal, per the declared policy, and reinstate on payment | P1 | L5 |
| FR-SUB-020 | Cancellation and final settlement | Cancel with notice validation, compute the final period, settle unbilled usage and any early-termination charge from M08 | P0 | L5 |
| FR-SUB-021 | Renewal roll | Roll the term on contract renewal, applying escalation and any agreed price change, with advance customer notice | P0 | L5 |
| FR-SUB-022 | Price-change notification | Notify the customer of any recurring price change the agreed notice period in advance, and record the notification as evidence | P0 | L5 |

### 5.3 Usage Collection & Rating

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SUB-023 | Usage ingestion | Ingest usage records from M05 (remote hours, incidents), M06 (storage volume), M13 (rental utilisation) and M08 (entitlement overage), with an idempotency key per record | P0 | L5 |
| FR-SUB-024 | Rating engine | Rate usage against the subscription's tariff — flat, tiered, volume, stepped, with included allowances and minimum commitments | P0 | L5 |
| FR-SUB-025 | Rating period control | Rate only within an open period; late-arriving usage for a closed period is rated into the next open period with an explanatory line | P0 | L5 |
| FR-SUB-026 | Overage from entitlement | Rate work delivered beyond an M08 entitlement at the contract's declared exhaustion treatment | P0 | L5 |
| FR-SUB-027 | Usage aggregation | Aggregate usage by subscription, site, department, asset and user for itemised presentation | P1 | L5 |
| FR-SUB-028 | Rerating | Rerate a period following a source correction, producing a controlled adjustment rather than mutating the original | P1 | L5 |
| FR-SUB-029 | Usage caps and alerts | Apply spend caps and alert the customer and account manager as thresholds are approached | P2 | L5 |
| FR-SUB-030 | Unrated usage exception queue | Surface usage that cannot be rated — no matching subscription, unknown tariff, closed period — as a worked exception queue, never dropping it | P0 | L5 |

### 5.4 Billing Run & Instruction

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SUB-031 | Billing run scheduling | Schedule billing runs by cycle, entity, customer group and channel, with a declared run calendar | P0 | L5 |
| FR-SUB-032 | Dry run | Execute a full dry run producing the exact result set for review, with variance against the prior period highlighted | P0 | L5 |
| FR-SUB-033 | Exception handling | Hold exceptions — missing rate, unrated usage, credit hold, disputed item, zero-value line — in a worked queue without blocking the rest of the run | P0 | L5 |
| FR-SUB-034 | Billing instruction to M20 | Instruct M20 with billable lines, periods, quantities, tax class, breakdown dimensions and the proration explanation | P0 | L5 |
| FR-SUB-035 | Consolidated invoicing | Consolidate many subscriptions into one invoice per customer, entity or billing account, per the customer's declared preference | P0 | L5 |
| FR-SUB-036 | Split billing | Split a subscription's charges across sites, departments, cost centres or projects, per agreed allocation rules | P1 | L5 |
| FR-SUB-037 | Credit and adjustment instruction | Instruct M20 to raise credits arising from proration, downgrade, service credit or dispute, always through the approval path | P0 | L5 |
| FR-SUB-038 | Run resumption and idempotency | Resume a failed run from its point of failure with no possibility of double billing | P0 | L5 |
| FR-SUB-039 | Upcoming-charge visibility | Present the next charge, its composition and any proration in P01 and P04 before the run executes | P1 | L5 |

### 5.5 Recurring Revenue Metrics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SUB-040 | MRR and ARR | Compute MRR and ARR from recurring charges only, normalising non-monthly frequencies and excluding one-time charges | P0 | L5 |
| FR-SUB-041 | MRR movement | Decompose MRR movement into new, expansion, contraction, churn and reactivation, reconciling to the opening and closing balance | P0 | L5 |
| FR-SUB-042 | Churn measurement | Compute logo churn and revenue churn, gross and net, by product family, segment, channel and cohort | P0 | L5 |
| FR-SUB-043 | Cohort and retention analysis | Analyse retention and revenue retention by acquisition cohort, plan and channel | P1 | L5 |
| FR-SUB-044 | Bookings, ACV and TCV | Report bookings, annual contract value and total contract value alongside billed revenue, and reconcile the difference | P1 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Idempotent billing** | Every billing instruction carries a deterministic key of (subscription, period, charge line). Re-running a period can never invoice twice |
| T-02 | **Resumable runs** | A billing run is a set of independent per-subscription units with individual commit; failure resumes from the last uncommitted unit |
| T-03 | **Fixed-point money arithmetic** | All amounts use fixed-point decimal; proration rounds once, at a declared point, with a documented rounding rule and residual allocation |
| T-04 | **Daily-rate proration determinism** | Proration is computed from period days, not month fractions, so results are reproducible and explainable to the customer |
| T-05 | **Usage idempotency** | Usage records carry a source key; duplicate delivery is discarded, and correction is an explicit rerating event |
| T-06 | **Closed-period immutability** | No process may alter a period already closed by M19; corrections flow forward as adjustments |
| T-07 | **Amendment as event sourcing** | Subscription state is derived from an ordered amendment history, so any past state and any past MRR figure is reconstructible |
| T-08 | **Metric single-source** | MRR, ARR and churn are computed by one service; no dashboard recomputes them independently |
| T-09 | **Scale envelope** | A 50,000-subscription monthly run completes within its window; per-subscription computation ≤ 150 ms p95 |
| T-10 | **Dry-run fidelity** | The dry run executes the identical code path as the commit run, differing only in persistence, so a clean dry run guarantees a clean run |
| T-11 | **Exception isolation** | An exception on one subscription never blocks another; exceptions carry a machine-readable cause and a human action |
| T-12 | **Transactional outbox** | Billing instructions to M20 and metric events are written in the same transaction as the subscription state change |
| T-13 | **Multi-currency and multi-entity** | Subscriptions carry currency and legal entity; MRR reports in both transaction and reporting currency |
| T-14 | **Audit completeness** | Every amendment, rating, rerating, run and instruction is audited with actor, reason and before/after |
| T-15 | **Localisation** | Proration explanations, charge descriptions and upcoming-charge views are complete in Bengali |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M39 |
|---|---|---|
| **Finance officer** | Prepares AMC invoices by hand from a spreadsheet each month; mid-cycle changes are missed | Reviews a dry run, works an exception queue, commits — the invoices generate themselves |
| **Account manager** | Cannot answer "what will this cost me next month if I add ten laptops?" | Simulates the change and shows the prorated result immediately |
| **CFO** | Has no MRR, no ARR and no churn number | Sees MRR movement decomposed into new, expansion, contraction and churn, reconciled monthly |
| **Corporate client** | Receives an invoice that does not match what changed during the month | Sees the upcoming charge and its proration before the invoice, itemised by site and department |
| **MSP operations** | Delivers hours beyond entitlement that are never billed | Overage is rated automatically at the contract's declared treatment |
| **Rental coordinator** | Bills hire periods manually and misses part-months | Hire periods bill and prorate automatically |
| **Collections officer** | Chases invoices with no link to service consequence | A failed payment moves the subscription through a declared policy state, visible to everyone |
| **Residential customer** | Discovers a price increase on the invoice | Receives advance notice with the agreed notice period, recorded as evidence |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Recurring billing accuracy** | Deterministic proration, idempotent runs, exception queues instead of silent failures | Billing accuracy **> 99.5%** *(category KPI)* |
| **Recovery of mid-cycle revenue** | Assets attached mid-term are billed from the day they are covered, not from the next renewal | Closes a leakage path that is currently invisible; contributes to the **revenue leakage < 0.5%** programme target |
| **Overage revenue capture** | Work beyond entitlement is rated instead of absorbed | Directly supports the M08 target of **out-of-entitlement unbilled work < 0.5%** |
| **AMC / RAMC renewal economics** | Escalation applied automatically at renewal with notice evidence; renewal billing rolls without manual re-setup | Supports the **BDT 72 lac/year** renewal uplift owned by M08 |
| **Managed services scalability** | MSP tiers with usage components cannot be billed manually at scale | Enables the **BDT 95 lac/year** MSP contribution attributed to M05 |
| **Rental billing** | Periodic hire and utilisation billing without manual computation | Enables the **BDT 48 lac/year** rental margin attributed to M13 |
| **Administrative saving** | Manual monthly invoice preparation for the whole contract base disappears | A significant component of the **BDT 62 lac/year** administrative saving |
| **Cash-flow predictability** | Twelve-month billing forecast feeding M50 treasury | Supports the **BDT 26 lac/year** financial close and cash-flow benefit |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The company learns to think in recurring revenue** | MRR, churn and net revenue retention change how a service business is managed. Producing them reliably is the precondition for using them |
| **Billing trust** | Recurring billing errors destroy corporate relationships faster than service failures, because they suggest carelessness with the customer's money |
| **Auditability of recurring revenue** | An auditor can trace any invoice line to a subscription amendment, a rate version and a contract clause |
| **Fair and explainable charges** | A customer who can see how a part-month was calculated does not dispute it |
| **Scalability without headcount** | A contract base growing 2.5× does not require a 2.5× billing team |
| **Regulatory readiness** | VAT on recurring services requires consistent period attribution; M39 supplies it mechanically |
| **Model-ready data** | Churn prediction and expansion propensity in M26 depend on clean subscription event history |

---

## 8. Lifecycle & State Model

```
              ┌──────────┐
              │  DRAFT   │ created from an activated M08 contract
              └────┬─────┘
                   │ schedule generated; first period computed
              ┌────▼─────┐
              │ PENDING  │ awaiting the start date
              └────┬─────┘
                   │ start date reached
              ┌────▼─────┐
    ┌────────►│  ACTIVE  │◄──────── resumed / reinstated
    │         └────┬─────┘
    │              │
    │      ┌───────┼────────────┬──────────────────┐
    │      │       │            │                  │
    │      ▼       ▼            ▼                  ▼
    │  ┌────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────────┐
    │  │AMENDED │ │  PAUSED  │ │  SUSPENDED  │ │ PENDING      │
    │  │(new    │ │(customer │ │ (dunning    │ │ CANCELLATION │
    │  │version)│ │ request) │ │  signal)    │ │ (notice run) │
    │  └───┬────┘ └────┬─────┘ └──────┬──────┘ └──────┬───────┘
    │      │           │              │                │
    └──────┴───────────┴──────────────┘                │
                                                        │ effective date
                                            ┌───────────▼────────────┐
                                            │   FINAL BILLING        │
                                            │ (final period, unbilled│
                                            │  usage, settlement)    │
                                            └───────────┬────────────┘
                                                        │
                    ┌───────────────────────────────────┼──────────────┐
                    ▼                                   ▼              ▼
            ┌───────────────┐                  ┌────────────────┐ ┌──────────┐
            │   RENEWED     │                  │   CANCELLED    │ │ EXPIRED  │
            │ (term rolled, │                  │ (early, with   │ │(term end,│
            │  same subs.)  │                  │  settlement)   │ │ no renew)│
            └───────────────┘                  └────────┬───────┘ └────┬─────┘
                                                        └──────┬───────┘
                                                               ▼
                                                        ┌────────────┐
                                                        │   CLOSED   │
                                                        └────────────┘
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| — | Draft | M08 contract activated with at least one recurring charge | System |
| Draft | Pending | Plan bound, rate resolved, schedule generated, tax class present | System |
| Pending | Active | Start date reached; customer not on billing hold | System |
| Active | Amended | Change approved at the required authority; effective date valid and not in a closed period | Account Manager / Finance |
| Active | Paused | Approved pause reason; declared entitlement and billing treatment | Finance Manager |
| Active | Suspended | M20 dunning stage reached the declared suspension trigger | System (M20 event) |
| Suspended | Active | Payment received and cleared | System |
| Active | Pending Cancellation | Notice period validated against M08 | Account Manager / customer |
| Pending Cancellation | Final Billing | Effective date reached | System |
| Final Billing | Cancelled / Expired | Final period billed; unbilled usage rated; settlement instructed to M20 | System |
| Active | Renewed | M08 contract renewed; escalation applied; notice evidence recorded | System |
| Cancelled / Expired | Closed | All billing settled; no open disputes | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SUB-01 | Every subscription is bound to exactly one M08 contract; a subscription cannot exist without an agreement | **H** | CFO |
| BRU-SUB-02 | M39 never creates a financial document; it instructs M20 | **H** | CFO |
| BRU-SUB-03 | A subscription is changed by amendment; cancel-and-recreate is prohibited | **H** | CFO |
| BRU-SUB-04 | Proration is computed on a daily-rate basis with the credit treatment declared on the plan | **C** | CFO |
| BRU-SUB-05 | No billing instruction may be issued twice for the same subscription, period and charge line | **H** | CTO |
| BRU-SUB-06 | No change may be effective in an accounting period already closed by M19; corrections flow forward | **H** | CFO |
| BRU-SUB-07 | A recurring price change requires customer notice at the contractually agreed period, recorded as evidence | **H** | CCO |
| BRU-SUB-08 | Usage that cannot be rated is queued as an exception and never discarded | **H** | CFO |
| BRU-SUB-09 | Late-arriving usage for a closed period is rated into the next open period with an explanatory line | **C** | CFO |
| BRU-SUB-10 | Rerating produces an adjustment; it never mutates an issued charge | **H** | CFO |
| BRU-SUB-11 | A downgrade does not produce a cash refund without approval; the default is credit against future charges | **H** | CFO |
| BRU-SUB-12 | A suspended subscription generates no recurring charge for the suspended period unless the plan declares otherwise | **H** | CFO |
| BRU-SUB-13 | Cancellation requires notice validation against the M08 contract | **H** | CCO |
| BRU-SUB-14 | Final settlement includes all unbilled usage and any early-termination charge computed by M08 | **C** | CFO |
| BRU-SUB-15 | MRR excludes one-time charges and normalises non-monthly frequencies to a monthly value | **C** | CFO |
| BRU-SUB-16 | MRR movement must reconcile: opening + new + expansion − contraction − churn + reactivation = closing | **C** | CFO |
| BRU-SUB-17 | A billing run may only be committed after a dry run has been reviewed and its exceptions dispositioned | **H** | Finance Manager |
| BRU-SUB-18 | The person who amends a subscription cannot approve a credit arising from that amendment | **H** | CFO |
| BRU-SUB-19 | Every prorated line carries a plain-language explanation on the customer's invoice | **H** | CCO |
| BRU-SUB-20 | An asset detached from an M08 contract stops generating charges from the detachment date, not the next cycle | **C** | CFO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.subscription` | `fix_subscription` | The billing instance | name, contract_id, plan_item_id, partner_id, billing_account_id, entity_id, currency_id, state, start_date, end_date, frequency, alignment, timing, next_billing_date, payment_term_id, autopay_mandate_id |
| `fix.subscription.line` | `fix_subscription_line` | Charge lines | subscription_id, charge_type, item_id, qty, uom_id, rate, rate_lock_id, frequency, start_date, end_date, min_commitment, included_qty |
| `fix.subscription.amendment` | `fix_subscription_amendment` | Ordered change history | subscription_id, sequence, amendment_type, effective_date, before_json, after_json, mrr_delta, actor_id, reason, approved_by |
| `fix.billing.schedule` | `fix_billing_schedule` | Generated periods | subscription_id, period_start, period_end, billing_date, state, instruction_ref |
| `fix.proration.line` | `fix_proration_line` | Computed prorations | subscription_id, amendment_id, period_start, period_end, days, daily_rate, amount, direction, explanation_bn, explanation_en |
| `fix.usage.record` | `fix_usage_record` | Ingested usage | subscription_id, source_module, source_key, metric, qty, uom_id, usage_at, period_ref, state |
| `fix.usage.rating` | `fix_usage_rating` | Rating results | usage_record_ids, subscription_id, tariff_id, rated_qty, included_applied, rated_amount, period_ref, rerating_of_id |
| `fix.usage.tariff` | `fix_usage_tariff` | Rating tariffs | subscription_line_id, model (flat/tiered/volume/stepped), tiers_json, included_qty, overage_rate, cap_value |
| `fix.usage.exception` | `fix_usage_exception` | Unrated usage queue | usage_record_id, cause, detail, state, assigned_to, resolved_at |
| `fix.billing.run` | `fix_billing_run` | Run header | code, cycle, entity_id, scope_json, mode (dry/commit), state, started_at, completed_at, totals_json, resumed_from |
| `fix.billing.run.unit` | `fix_billing_run_unit` | Per-subscription unit | run_id, subscription_id, state, instruction_ref, exception_id, amount |
| `fix.billing.exception` | `fix_billing_exception` | Worked exception queue | run_id, subscription_id, cause_code, detail, state, assigned_to, disposition, resolved_at |
| `fix.billing.instruction` | `fix_billing_instruction` | Instruction to M20 | subscription_id, period_ref, idempotency_key, lines_json, tax_class_refs, breakdown_json, state, invoice_ref |
| `fix.billing.account` | `fix_billing_account` | Consolidation and split rules | partner_id, entity_id, consolidation_rule, split_rules_json, invoice_preference, delivery_preference |
| `fix.mrr.snapshot` | `fix_mrr_snapshot` | Period metric snapshot | period, entity_id, segment, product_family, opening, new, expansion, contraction, churn, reactivation, closing, arr |
| `fix.churn.record` | `fix_churn_record` | Churn events | subscription_id, period, type (logo/revenue), amount, reason_code, cohort, competitor |
| `fix.subscription.notice` | `fix_subscription_notice` | Price-change and renewal notices | subscription_id, notice_type, sent_at, channel, content_ref, acknowledged_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.contract`, entitlement balances, termination charges | M08 | Live read + events |
| `fix.subscription.plan.def` | M37 | Master data projection |
| `fix.price.lock`, rate resolution, escalation | M11 | REST |
| `fix.party`, billing contacts, payment terms, credit status | M33 | Live read |
| `fix.ar.invoice`, `fix.ar.credit.note`, dunning stage | M20 | Command + events |
| `fix.tax.code`, VAT treatment | M51 | Live read |
| Accounting period status | M19 | Live read |
| Usage sources: remote hours, storage volume, rental utilisation | M05, M06, M13 | Events |
| Revenue-recognition treatment | M53 | Projection supplied |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-SUB-01 | M08 contract activated with a recurring charge | Create the subscription, bind the plan and rate, generate the schedule, compute the first period | Create in Draft with an exception; alert Finance |
| AUT-SUB-02 | Billing date reached | Assemble the period's charges, rate outstanding usage, compute proration, and issue the billing instruction to M20 | Hold the unit as an exception; the rest of the run proceeds |
| AUT-SUB-03 | Scheduled dry run (T−2 days) | Execute the full dry run, produce the variance report against the prior period, and notify Finance | Retry; escalate to Finance Manager |
| AUT-SUB-04 | Usage record received | Validate, deduplicate by source key, match to a subscription, and rate against the tariff | Queue as a usage exception with the cause |
| AUT-SUB-05 | M08 asset attached or detached | Compute proration from the effective date and attach it to the next period | Raise a billing exception |
| AUT-SUB-06 | Plan change approved | Apply the amendment, compute credit and charge, recompute MRR delta | Hold as an exception; alert the account manager |
| AUT-SUB-07 | M20 dunning stage reaches the suspension trigger | Suspend the subscription per policy, halt recurring charges, and notify M08, M01 and the customer | Alert Finance; never suspend without the declared trigger |
| AUT-SUB-08 | Payment received on a suspended subscription | Reinstate, realign the schedule, and notify service modules | Alert Finance |
| AUT-SUB-09 | Contract renewal recorded in M08 | Roll the term, apply escalation, issue the price-change notice, regenerate the schedule | Create a manual renewal-billing task |
| AUT-SUB-10 | Price change scheduled | Send the customer notice at the contractual lead time and record the evidence | Escalate; block the price change if notice cannot be evidenced |
| AUT-SUB-11 | Cancellation effective date reached | Execute final billing: final period, unbilled usage, early-termination charge, settlement instruction | Hold in Final Billing; alert Finance |
| AUT-SUB-12 | Period close in M19 | Freeze the period, compute the MRR snapshot and movement decomposition, and publish metrics | Retry; escalate to CFO on failure |
| AUT-SUB-13 | Usage exception unresolved beyond threshold | Escalate to Finance Manager with the value at risk | Repeat escalation |
| AUT-SUB-14 | Spend cap threshold approached | Notify the customer and account manager | Log; retry |
| AUT-SUB-15 | Source correction received for a rated period | Create a rerating adjustment for the next open period, never mutating the issued charge | Queue for manual rerating |
| AUT-SUB-16 | Upcoming billing date (T−5 days) | Publish the upcoming charge and its composition to P01/P04 | Log; retry |

---

## 12. Interfaces

### 12.1 Upstream — M39 Consumes

| Source | What | Mechanism |
|---|---|---|
| M08 Contract | Contract activation, amendment, asset attach/detach, suspension, renewal, termination, early-termination charge, entitlement exhaustion | Events + REST |
| M37 Catalogue | Subscription plan definitions, tax class, revenue class | Master data projection |
| M11 Pricing | Plan rates, usage rates, escalation, change-of-plan pricing | REST |
| M36 Quotation | Accepted subscription proposals | Event `quotation.accepted` |
| M33 Party Master | Billing accounts, payment terms, billing contacts, credit status | Live read |
| M20 Receivable | Invoice outcome, payment receipt, dunning stage | Events |
| M19 Financial Accounting | Accounting period open/closed status | Live read |
| M05 Managed Services | Remote hours, incident counts, patch and monitoring volumes | Event `msp.usage_reported` |
| M06 Data Services | Backup storage volume and retention consumption | Event `data.usage_reported` |
| M13 Rental | Hire periods and utilisation | Event `rental.usage_reported` |
| M51 Tax | Tax treatment rules for recurring and usage supplies | REST |

### 12.2 Downstream — M39 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M20 Receivable | Billing instructions, credit instructions, consolidation and split directives, proration explanations | Command `POST /api/v1/billing/instruction` |
| M53 Revenue | Recurring, usage and one-time revenue basis with period attribution for recognition | Projection |
| M19 Financial Accounting | Deferred revenue movement basis | Via M53 |
| M08 Contract | Billing status, unbilled value, suspension and cancellation confirmations | Events + REST |
| M50 Treasury | Twelve-month billing forecast for cash planning | Projection |
| M54 FP&A | MRR, ARR, churn, cohort and bookings data for budgeting | Warehouse extract |
| M01 / M05 / M06 / M13 | Subscription state changes that gate service delivery (suspended, cancelled) | Events |
| M35 Marketing | Churn and expansion signals for campaigns | Events |
| M07 CRM | Expansion and contraction signals per account | Events |
| M25 BID · M26 AIM | Subscription, usage, billing and metric fact streams | Warehouse extract |
| P01 / P04 portals | Subscription view, upcoming charge, usage detail, plan change requests | REST via M28 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `subscription.created` | subscription id, contract, plan, MRR | M20, M53, M25 |
| `subscription.activated` | subscription id, start date, first period | M20, M08 |
| `subscription.amended` | subscription id, amendment type, effective date, MRR delta | M20, M53, M08, M07 |
| `subscription.prorated` | subscription id, amendment, amount, direction, explanation | M20 |
| `subscription.suspended` / `subscription.reinstated` | subscription id, cause, effective date | M08, M01, M05, M06, M13 |
| `subscription.cancelled` | subscription id, effective date, final settlement, churn reason | M08, M20, M35, M53 |
| `subscription.renewed` | subscription id, new term, escalation applied, MRR delta | M08, M20, M53 |
| `usage.rated` | subscription id, metric, qty, amount, period | M20, M25 |
| `usage.exception_raised` | usage record, cause, value at risk | Finance alerting |
| `billing.run_completed` | run id, mode, counts, totals, exception count | M20, M19, M50 |
| `billing.instruction_issued` | instruction id, subscription, period, amount, idempotency key | M20 |
| `mrr.snapshot_published` | period, opening, movements, closing, ARR | M54, M25, executive dashboards |
| `churn.recorded` | subscription id, type, amount, reason, cohort | M35, M07, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-SUB-01 | Payment gateways (bKash, Nagad, card) *(via M20)* | Outbound | Autopay collection against mandates |
| INT-SUB-02 | Bank direct debit / standing instruction *(via M50)* | Outbound | Recurring collection for corporate accounts |
| INT-SUB-03 | Corporate client AP portals | Outbound | Consolidated invoice submission where the client requires it |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/subscriptions` | GET/POST | Subscription register and creation | P03, M08 |
| `/api/v1/subscriptions/{id}` | GET | Full subscription with lines, schedule and history | P03, P04 |
| `/api/v1/subscriptions/{id}/amend` | POST | Apply an amendment with proration preview | P03, P04 |
| `/api/v1/subscriptions/{id}/preview` | POST | Simulate a change and return the prorated financial effect | P03, P04, P01 |
| `/api/v1/subscriptions/{id}/pause` · `/resume` | POST | Pause and resume billing | P03 |
| `/api/v1/subscriptions/{id}/cancel` | POST | Cancel with notice validation and final settlement preview | P03, P04 |
| `/api/v1/subscriptions/{id}/upcoming` | GET | Next charge with composition and proration explanation | P01, P04 |
| `/api/v1/subscriptions/{id}/usage` | GET | Rated usage detail for the current and prior periods | P04, P01 |
| `/api/v1/usage` | POST | Ingest usage records with idempotency keys | M05, M06, M13 |
| `/api/v1/billing/runs` | GET/POST | Schedule, dry-run, commit and resume a billing run | P03 |
| `/api/v1/billing/runs/{id}/exceptions` | GET/POST | Work the exception queue | P03 |
| `/api/v1/metrics/mrr` | GET | MRR, ARR and movement decomposition | P06, M54 |
| `/api/v1/metrics/churn` | GET | Churn and retention by cohort and segment | P06, M54 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | C R U D A | All |
| R26 Finance Manager | C R U A | All — run commit, exception disposition, credit approval |
| R27 Finance Officer | C R U | Assigned scope — exception working, dry-run review |
| R04 Chief Commercial Officer | R A | All — price change and escalation approval |
| R21 Sales Manager | R | Assigned segment |
| R22 Account Manager (Corporate) | R U | Assigned accounts — amendment proposal, preview |
| R06 Branch Manager | R | Own branch's subscriptions |
| R13 Remote Support Engineer | R | Assigned MSP clients — usage context |
| R34 Contact Centre Agent | R | Customer-facing subscription and upcoming-charge view |
| R33 IT / System Administrator | R U | Run configuration and scheduling |
| R36 Customer | R, request | Own subscriptions, usage and upcoming charges; plan-change requests |
| R37 Corporate Portal User | R, request | Own company; role-scoped; approver role may authorise changes |
| R38 External Party | R | Own subscription only (marketplace seller subscription) |

**Field-level restrictions.** Cost, margin and internal pricing structure are never exposed. MRR,
churn and cohort metrics are restricted to R01–R04, R26 and R54-scope FP&A users. Payment
mandate identifiers follow the `bank_account` restriction in `05-04` §5.

**Segregation of duties.** SOD-16 *(to be registered in `05-04` §6)*: the user who amends a
subscription cannot approve a credit arising from that amendment. This complements SOD-04
(credit note create/approve) enforced in M20.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| MRR movement waterfall | CFO, CEO, CCO | Monthly | Opening → new → expansion → contraction → churn → reactivation → closing, reconciled |
| ARR and bookings | CFO, CEO | Monthly | ARR, ACV, TCV, bookings vs billed, and the reconciliation between them |
| Churn and retention | CFO, CCO, Marketing | Monthly | Logo and revenue churn, gross and net retention, by family, segment, channel and cohort |
| Cohort retention curves | CFO, CCO | Quarterly | Retention and revenue retention by acquisition vintage and plan |
| Billing run summary | Finance Manager, CFO | Per run | Counts, values, exceptions by cause, variance against the prior period |
| Billing exception queue | Finance Officers | Real time | Open exceptions by cause, age, value at risk and assignee |
| Usage rating summary | Finance Manager, MSP Operations | Monthly | Rated usage by metric, subscription and source; unrated queue and its value |
| Proration audit | Finance Manager, auditor | Monthly | Every prorated line with its inputs, daily rate, days and explanation |
| Subscription base | CCO, CFO | Weekly | Active subscriptions by plan, frequency, value and next billing date |
| Unbilled value | CFO | Weekly | Delivered but unbilled usage and overage, by age |
| Billing forecast | CFO, Treasury (M50) | Monthly | Projected billing by cycle for twelve months |
| Price-change notice compliance | CCO, Quality Manager | Per change | Notices due, sent, acknowledged; any change lacking evidence |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-C39-01 | Subscription billing accuracy | n/a | 99.0% | **> 99.5%** |
| KPI-C39-02 | Billing runs completed without manual intervention | n/a | 85% | **> 95%** |
| KPI-C39-03 | Billing exceptions per 1,000 subscriptions | n/a | < 25 | **< 8** |
| KPI-C39-04 | Usage records rated within the same period | n/a | 95% | **> 99%** |
| KPI-C39-05 | Unrated usage value at period close | n/a | < 1% | **< 0.2%** |
| KPI-C39-06 | Mid-cycle changes billed in the correct period | unmeasured | 97% | **> 99.5%** |
| KPI-C39-07 | Recurring invoice disputes | unmeasured | < 4% | **< 1.5%** |
| KPI-C39-08 | Days to produce MRR and churn after period close | n/a | < 3 | **< 1** |
| KPI-C39-09 | Net revenue retention | unmeasured | ≥ 100% | **≥ 108%** |
| KPI-C39-10 | Revenue churn (monthly) | unmeasured | < 2.5% | **< 1.2%** |
| KPI-C39-11 | Price changes with evidenced advance notice | n/a | 100% | **100%** |
| KPI-C39-12 | Per-subscription billing computation p95 | n/a | ≤ 200 ms | **≤ 150 ms** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `account` period and payment-term primitives | 8% |
| L2 | OCA `contract`, `contract_variable_quantity`, `contract_invoice_start_end_dates`, `queue_job` | 30% |
| L5 | `cd_subscription_engine`, `cd_usage_rating`, `cd_proration`, `cd_recurring_metrics`, `cd_dunning_bridge` | 62% |

> **Layer note.** OCA `contract` is adopted here as **M39's recurring-invoicing engine**, not as
> M08's contract model. M08 uses OCA `agreement`. Conflating the two would blur the boundary the
> category overview forbids, and the build must keep them separate.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C39-01 | `cd_subscription_engine` — subscription object, amendment model, schedule generation, state machine | Odoo module | 6 PW |
| CD-C39-02 | `cd_proration` — daily-rate proration, credit treatment, backdating, explanations | Odoo module | 4 PW |
| CD-C39-03 | `cd_usage_rating` — ingestion, deduplication, tariff engine, rerating, exception queue | Odoo module + service | 5 PW |
| CD-C39-04 | Billing run orchestrator — dry run, resumable commit, idempotent instruction to M20 | Service | 4 PW |
| CD-C39-05 | `cd_recurring_metrics` — MRR, ARR, movement decomposition, churn, cohorts | Odoo module | 2 PW |
| CD-C39-06 | `cd_dunning_bridge` — M20 dunning signal to subscription state policy | Odoo module | 1 PW |
| | | **Total** | **22 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M08 Contract | Every subscription is bound to a contract; the two are gated together in W4 |
| M37 Catalogue | Plan definitions and tax classes |
| M11 Pricing | Plan and usage rates |
| M20 Receivable *(W3)* | The invoice, dunning and receipt counterpart must exist first |
| M19 Financial Accounting *(W3)* | Period control governs what may be changed |
| M51 Tax *(W4)* | Recurring supply tax treatment |
| M05 / M06 / M13 | Usage sources — M05 lands W5, M06 and M13 W6; usage rating for those streams is enabled progressively |

> **Phasing note.** The subscription engine, proration and billing runs are complete in W4 for
> AMC, RAMC and protection plans. Usage rating is built in W4 but activated per source as M05
> (W5), M13 (W6) and M06 (W6) go live. This is a deliberate sequencing decision, not a
> descoping — the tariff engine is delivered and tested in W4 against simulated sources.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| AMC/RAMC billing schedules (spreadsheets) | ~3,000–5,000 | `fix.subscription` + `fix.billing.schedule` | W4 |
| Corporate AMC billing arrangements | ~150 | `fix.subscription` + `fix.billing.account` | W4 |
| MSP billing arrangements | ~40 | `fix.subscription` | W5 |
| Historic invoiced recurring revenue (for MRR baseline) | 24 months | Warehouse only | W4 |
| Payment mandates and standing instructions | Unknown | `fix.subscription` autopay reference *(via M20)* | W4 |

**Migration rule.** Subscriptions migrate with a declared "as-at" period and an opening MRR
figure that must reconcile to the last manually issued invoice for that customer. Any
subscription that cannot be reconciled migrates in Draft and is not billed until Finance
confirms it. Double-billing during cutover is the single largest reputational risk of Wave 4;
the cutover plan must include a parallel-run period with reconciliation before the manual
process is retired.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A subscription is created and scheduled automatically on M08 contract activation | End-to-end test across four contract families |
| AC-02 | No subscription can be billed twice for the same period under any failure or retry condition | Chaos test with induced failures mid-run |
| AC-03 | A billing run of 50,000 subscriptions completes within its window and is resumable from any point of failure | Load and resumption test |
| AC-04 | A dry run and its committed run produce identical results | Comparison test over the full base |
| AC-05 | Mid-cycle quantity change, asset attach/detach, upgrade and downgrade all prorate correctly on a daily-rate basis | Proration test matrix with hand-calculated expected values |
| AC-06 | Every prorated line carries a plain-language Bengali explanation on the customer's invoice | Document inspection |
| AC-07 | Usage arriving late, duplicated or corrected is handled without corrupting a closed period | Scripted scenarios per case |
| AC-08 | Unrated usage is never discarded and always appears in the exception queue with its value | Negative test with unmatched usage |
| AC-09 | MRR movement reconciles: opening + new + expansion − contraction − churn + reactivation = closing | Reconciliation test over six simulated periods |
| AC-10 | A dunning-triggered suspension halts billing and notifies every service module, and reinstatement restores correctly | Joint test with M20, M08 and M01 |
| AC-11 | Final settlement on cancellation includes all unbilled usage and any early-termination charge | Scripted scenario |
| AC-12 | A price change cannot take effect without evidenced advance notice at the contractual period | Negative test |
| AC-13 | A corporate customer sees the upcoming charge, its composition and proration in P04 before the run | Demonstration |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements, including a parallel-run reconciliation | Signed UAT record + reconciliation report |
| AC-15 | Zero critical or high security findings | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the default proration credit treatment on downgrade — credit against future charges, or refund? The design assumes credit | CFO | W4 build |
| Q-02 | What is the contractual notice period for a recurring price change, and does it differ between residential and corporate? | CCO / Legal | W4 build |
| Q-03 | At which M20 dunning stage does a subscription suspend, and does suspension stop service as well as billing? | CFO / Ops Director | W4 build |
| Q-04 | Is billing in advance or in arrears the default for AMC/RAMC, and is it consistent across families? | CFO | W4 build |
| Q-05 | Do corporate customers require consolidated invoicing per legal entity, per site, or per their own cost-centre structure? | CFO / Account Managers | W4 build |
| Q-06 | Are backdated amendments permitted at all, and if so within what window? | CFO | W4 build |
| Q-07 | What is the VAT period-attribution treatment for usage rated late into a subsequent period? | CFO / Tax adviser | W4 build |
| Q-08 | How long must the parallel run between manual and automated recurring billing last before the manual process is retired? | CFO | **W4 cutover — blocking** |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §4.2, §8 ·
`M08_Contract_Lifecycle_Management.md` §3, §12 ·
`M37_Product_and_Service_Catalogue_Management.md` §5.5 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §5.2 ·
`M36_Quotation_Estimation_and_Tender_Management.md` §12 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §6 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P04 §Billing ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.8, §8.10 ·
`1000FiX Business Plan` §Managed Services, §RAMC Packages, §Rental, §Data Backup ·
`1000FiX_ERP_System_Comprehensive_URD.md` §8

**External benchmark**
Oracle Fusion Cloud Subscription Management — usage-based subscriptions, daily-rate proration with and without credit, MRR normalisation, churn and expansion analytics ·
SAP S/4HANA billing plans on service contracts — billing independent of delivery ·
Zuora-class subscription billing — amendment-driven change, rating engine, standard subscription metrics ·
Telecom and utility rating practice — tiered tariffs, rating windows, rerating ·
Odoo 19 `sale_subscription` and OCA `contract` / `contract_variable_quantity` module family

---

*Module M39 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
