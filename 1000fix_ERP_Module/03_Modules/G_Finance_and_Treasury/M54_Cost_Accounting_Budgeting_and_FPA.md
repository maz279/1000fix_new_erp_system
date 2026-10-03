---
id: FIX-ERP2-M54
module_id: M54
module_code: FPA
module_name: Cost Accounting, Budgeting & FP&A
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P2
wave: W6
---

# M54 — Cost Accounting, Budgeting & FP&A
### Category G · Code `FPA` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M54 |
| **Module code** | `FPA` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M19 monolith after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account` (analytic accounting) · L2 OCA `mis-builder`, `account-analytic`, `account-budgeting`, `account-financial-reporting` · L5 custom allocation, job costing, budget model and forecast engine |
| **Custom modules** | `cd_cost_allocation`, `cd_job_costing`, `cd_budget_ext`, `cd_fpa_forecast` |
| **Requirement range** | FR-FPA-001 … FR-FPA-040 |
| **Requirement count** | **40** *(measured — supersedes the 30 estimate in `02-02`)* |
| **Effort estimate** | **22 person-weeks** *(measured — supersedes the 17 PW estimate)* |
| **Depends on** | M19 GL · M20 Receivables · M52 Payables · M53 Revenue · M49 Fixed Assets · M15 Inventory · M21 HR & Payroll · M01/M31 Service · M62 Data Platform |
| **Depended on by** | M52, M49, M50, M11, M12, M13, M25, M26, M07, M08, M58, M65, M67 |

---

## 2. Purpose

M54 answers the question that the entire finance programme exists to make answerable:
**which parts of this business make money, and which do not?**

1000FiX runs **fourteen revenue streams** across **51+ branches**, with shared technicians,
shared workshops, shared logistics, shared branch overhead and shared head-office cost. Revenue
by stream is visible the moment M20 and M53 are live. Cost is not — because most cost is
incurred once and consumed by several streams at once. A technician's day serves a warranty job,
a paid repair and a contract call-out. A branch's rent supports a service counter, a retail
display and a workshop. Until that shared cost is attributed on a defensible basis, every
statement of "the rental business makes 55% margin" or "marketplace commission is worth BDT 84
lac" is an assertion, not a measurement.

M54 does three things:

1. **Costing** — attributes cost to the objects that consume it: jobs, contracts, branches,
   business lines, customers, technicians and assets.
2. **Budgeting** — sets the plan, holds it, and measures against it.
3. **FP&A** — forecasts forward, models scenarios, and explains variance.

It creates no journal entries and it owns no transactions. It reads the ledger M19 built and
turns it into management information. That separation is deliberate: management accounting
changes as the business changes, and it must never be able to destabilise the statutory ledger.

### Why It Exists

`_CATEGORY_OVERVIEW.md` §10 records the risk plainly: *"Costing never implemented, so margin
stays unknown — pricing decisions made blind."* That is the current state. M11's dynamic pricing,
M12's commission scheme, M13's rental rates and M08's contract pricing are all commercial
decisions that require a cost base, and today none of them has one.

Two specific consequences follow. First, **contracts with negative margin are invisible.** A
corporate AMC priced three years ago against an assumed cost may now be loss-making at every
call-out, and nothing in the business would reveal it. The category KPI is that 100% of such
contracts become visible. Second, **branch performance cannot be managed.** A branch manager
held accountable for a result they cannot see or influence is not accountable at all.

M54 is P2 and lands in Wave 6 because it depends on the ledger, receivables, payables, revenue,
assets and payroll all being live and clean. It cannot be pulled forward. But its absence is
visible — deliberately so — in KPI reporting from Wave 4 onward.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-001 | "Multi-branch chart of accounts with configurable structure per branch and **cost center**" |
| ERP BRD BR-FIN-008 | "Branch-wise P&L and consolidated financial statements" |
| Business Objective BO-06 | Financial control and reporting, owner CFO |
| Business Objective BO-07 | Branch-level profitability visibility |
| Business Objective BO-11 | MSP revenue ≥ 12% of revenue — a margin claim requiring a cost base |
| Business Objective BO-13 | Rental utilisation 68% and **gross margin 55%** — unverifiable without asset and operating cost attribution |
| Business Objective BO-14 | Refurbished units 12,000/year at **22% margin** — a costing claim |
| Business Objective BO-17 | "Make decisions on live data — manual reporting packs from 100% to zero" |
| `_CATEGORY_OVERVIEW.md` §2 | M54 scope: "Cost allocation, job and contract costing, budgets, variance, forecasting, business-line profitability" |
| `_CATEGORY_OVERVIEW.md` §5 | "Job, contract and business-line costing — M54, not M19" · "Budgeting and forecasting — M54, not M19" |
| `_CATEGORY_OVERVIEW.md` §8 | Budget variance explained within 3 days of close: 100% · **Contracts with negative margin identified: 100% visible** |
| `_CATEGORY_OVERVIEW.md` §10 | Risk: "Costing never implemented, so margin stays unknown — pricing decisions made blind. M54 is P2 but its absence is visible in KPI reporting from Wave 4" |
| Exec Summary §6.2 | Every one of the new revenue-line benefits (MSP 95, rental 48, refurbishment 65, marketplace 84, data services 30, dynamic pricing 40 lac) is a **margin** claim requiring M54 to verify |
| `M52` §7.2 | Field expense attributed to jobs — "precondition for M54's true job margin" |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M54 is a *reading* module. It consumes what other
> modules produce and produces management information. It writes no transactions and posts no
> journals. Both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The cost centre and cost object model: hierarchy, ownership, and what each may absorb |
| 2 | Cost element structure: the management view of cost, distinct from the statutory chart |
| 3 | Cost pooling: gathering shared cost into pools by nature and location |
| 4 | **Allocation cycles**: direct, step-down, reciprocal and activity-based allocation of shared cost |
| 5 | Allocation driver management: headcount, floor area, job volume, technician hours, revenue, transaction count |
| 6 | **Job and work-order costing**: labour, parts, travel, field expense and allocated overhead per job |
| 7 | **Contract costing**: cost to serve a contract across its life, against the revenue it earns |
| 8 | Service and product costing: standard cost, actual cost and their variance |
| 9 | Technician and resource costing: fully loaded hourly cost |
| 10 | Asset and rental-unit costing: cost to own and operate, against rental revenue |
| 11 | **Business-line profitability** across all 14 revenue streams |
| 12 | **Branch profitability**: revenue, direct cost, allocated overhead and contribution |
| 13 | Customer and segment profitability, including cost to serve |
| 14 | Channel profitability: counter, field, workshop, e-commerce, marketplace, corporate |
| 15 | Unit economics: cost per job, cost per branch, cost per technician-hour, cost per delivery |
| 16 | Inter-branch and inter-entity transfer pricing for internal service |
| 17 | **Budgeting**: annual operating budget, capital budget, versions, top-down and bottom-up |
| 18 | Budget workflow: preparation, submission, review, approval and locking |
| 19 | Budget availability checking and commitment consumption |
| 20 | **Variance analysis**: budget vs actual vs forecast, with drill-down and explanation capture |
| 21 | **Rolling forecast**: driver-based, updated on a defined cadence |
| 22 | Scenario and sensitivity modelling |
| 23 | Management reporting packs and the board pack |
| 24 | Cost-saving and efficiency initiative tracking against realised benefit |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Journal entries of any kind, including allocation postings | **M19** General Ledger | Only Category G's ledger creates journal entries. Where an allocation must post, M54 computes it and M19 posts it |
| Chart of accounts, dimensions, periods, statutory statements, consolidation | **M19** General Ledger | The statutory ledger is the source M54 reads |
| Actual revenue transactions and invoicing | **M20** Receivables | M54 reads revenue; it never bills |
| Revenue recognition timing and deferral | **M53** Revenue & Settlement | M54 uses **recognised** revenue, not billed revenue — the distinction is essential to margin |
| Actual cost transactions: vendor invoices, expenses, payroll | **M52** / **M21** | M54 reads cost; it never incurs it |
| Inventory valuation and stock cost | **M15** Inventory | M15 computes stock value; M54 consumes consumption cost |
| Landed cost computation | **M44** Import & Landed Cost | Computed once, upstream |
| Asset register, depreciation computation, capital approval | **M49** Fixed Assets | M49 computes depreciation; M54 attributes it. M49 approves capital; M54 holds the budget it consumes |
| Cash forecasting and liquidity | **M50** Treasury & Cash | M50 forecasts **cash**; M54 forecasts **result**. They are different questions with different drivers |
| Tax computation and effective tax rate determination | **M51** Tax & Regulatory | M54 reports the effective rate M51 computes |
| **Price setting, rate cards, discount policy, dynamic pricing** | **M11** Pricing (Category C) | M54 supplies the cost base; **M11 decides the price**. This boundary is absolute — a costing module that sets prices becomes a commercial module with an accounting mandate |
| Commission scheme design | **M12** Marketplace (with **M53**) | M54 informs the economics; M12 sets the scheme |
| Dashboards, executive visualisation and self-service BI | **M25** Business Intelligence (Category J) | M54 defines and computes the measures; M25 presents them |
| The data warehouse, ETL and semantic layer | **M62** Data Platform | M62 is the substrate M54's analytics run on |
| Predictive and ML models | **M26** AI/ML Services | M54 supplies the driver structure; M26 may model it |
| Technician utilisation and productivity measurement | **M02** Field Service | M02 measures activity; M54 costs it |
| Headcount planning and establishment control | **M21** HR & Payroll | M54 holds the personnel budget; M21 holds the establishment |
| KPI definition and the metric registry | **M25** Business Intelligence | One metric registry, owned by M25 |

### 3.3 Shared Concepts

| Concept | M54's Role | Owning Module |
|---|---|---|
| Cost centre | **Owns** the management structure; M19 owns the dimension and M30/M64 the master values | M54 / M19 / M64 |
| Cost object (job, contract, asset, customer, business line) | **Owns** the costing view | M54 |
| Actual cost | Reads from the ledger; never creates | M19 / M52 / M21 / M15 / M49 |
| Recognised revenue | Reads from M53; **never uses billed revenue for margin** | M53 / M54 |
| Allocation | **Owns** the computation; M19 posts where a posting is required | M54 / M19 |
| Standard cost | **Owns** | M54 |
| Budget | **Owns** — the defining artefact alongside costing | M54 |
| Capital budget | **Owns**; M49 consumes and reports against it | M54 / M49 |
| Forecast (result) | **Owns**; M50 owns the cash forecast | M54 / M50 |
| Cost base for pricing | **Owns** the cost; **M11 owns the price** | M54 / M11 |
| Margin | **Owns** the computation | M54 |
| Metric definition | Supplies financial measures; M25 owns the registry | M54 / M25 |
| Job cost | **Owns**; M01/M31 own the job | M54 / M01 / M31 |
| Technician hourly cost | **Owns** the fully loaded rate; M21 owns the pay | M54 / M21 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Controlling (CO)** | Cost centre accounting, internal orders, activity types with planned rates, assessment and distribution cycles, profitability analysis (CO-PA) with characteristics and value fields — all now reading the Universal Journal rather than separate tables | **Two things.** First, **activity types with planned rates** — a technician hour has a fully loaded cost rate that is planned, applied to jobs as they are worked, and reconciled to actual at period end. This is the mechanism that makes job costing possible in real time rather than only in arrears. Second, **profitability analysis with characteristics** — margin sliced by branch, business line, customer, channel and service type from one dataset. Since M19 already carries all seven dimensions on every ledger line, our CO-PA equivalent is a query, not a separate data structure | SAP's assessment/distribution cycle configuration depth and the CO-PA operating-concern apparatus; we ship a constrained allocation grammar |
| **SAP — the CO/FI reconciliation problem, and its removal in S/4HANA** | Historically, management accounting (CO) and financial accounting (FI) held separate data that had to be reconciled | **The lesson, adopted as a design rule: management accounting must never hold its own copy of actuals.** M54 reads M19's ledger lines. There is no M54 actuals table. A management report and a statutory report that disagree is the single most destructive thing a finance system can produce | Any design where M54 posts to its own ledger |
| **Oracle Fusion Cloud — Cost Management, Profitability and Cost Management (PCM)** | Cost accounting with cost books, allocation rules with drivers, profitability modelling with traceable allocation paths, waterfall visualisation of how cost reaches an object | **Traceable allocation paths** — for any allocated cost on any object, the system can show the pool it came from, the driver used, and the proportion applied. Allocation that cannot be explained is allocation that will be disputed by whoever it lands on, and disputed allocation destroys the credibility of branch accountability | PCM's separate modelling engine; our allocation runs against the ledger directly |
| **Microsoft Dynamics 365 Finance — Cost Accounting & Budgeting** | Cost accounting ledger with cost elements and objects, allocation bases, cost distribution and allocation policies; budget planning with scenarios, workflow, templates and top-down/bottom-up | **Budget planning as a workflow with scenarios and versions** — a budget is not a number, it is a process with drafts, submissions, reviews and a locked approved version, and every subsequent variance is measured against the locked version. Also adopted: budget control with configurable enforcement (warn or block) by category | The separate cost accounting ledger — same reason as the SAP lesson above |
| **Anaplan / Adaptive Insights / Workday Adaptive (FP&A class)** | Driver-based planning, rolling forecasts, scenario modelling, variance commentary capture, management report packs | **Driver-based rolling forecast with captured commentary.** The forecast is built from operational drivers — job volume, technician headcount, branch count, utilisation, average ticket — not from extrapolated financials. And **the variance explanation is captured in the system by the accountable owner**, which is what turns a variance report into a management process. This is the mechanism behind "budget variance explained within 3 days of close, 100%" | Full multi-dimensional planning-model tooling; our driver set is bounded and known |
| **Field-service and multi-site retail costing practice** | Cost to serve per job and per site; fully loaded technician cost; contribution before and after allocated overhead; contract profitability over life | **The two-margin presentation**: contribution margin (revenue less directly attributable cost) shown alongside net margin (after allocated overhead). Branch and contract managers can influence the first and largely cannot influence the second, and conflating them destroys accountability | Single-margin reporting |
| **OCA `mis-builder` + `account-analytic` + `account-budgeting`** | MIS report definitions over the ledger, analytic distribution, budget lines against analytic accounts | The reporting substrate. `mis-builder` supplies the management report definition engine and is a genuinely good fit for board and management packs | OCA budgeting alone as the budget model — no workflow, versions or scenarios; extended in `cd_budget_ext` |

**Design position.** Six deliberate positions.

First, **M54 holds no actuals of its own**. Every cost and revenue figure is read from M19's
ledger lines, which already carry entity, branch, cost centre, business line, project, brand and
channel. This makes a management-versus-statutory discrepancy structurally impossible, and it is
the single most important decision in the module.

Second, **margin uses recognised revenue, never billed revenue**. M53 is the source. A rental
month billed in advance and a warranty extension billed in full at inception would both produce
nonsense margins if measured against billing.

Third, **allocation must be explainable to the person it lands on**. Every allocated amount can
be traced back to its pool, driver and proportion. A branch manager who cannot see why BDT
80,000 of head-office cost landed on their P&L will reject the whole statement, and with it the
accountability the exercise was for.

Fourth, **contribution and net margin are both shown, always**. Contribution is what the
manager controls. Net is what the business earns. Reporting only one of them produces either
false comfort or unfair blame.

Fifth, **the forecast is driver-based and owned by the business**, not extrapolated by finance.
Job volume, branch count, technician headcount, utilisation and average ticket are the drivers;
finance owns the model, operations owns the driver assumptions, and the difference between them
is where the useful conversation happens.

Sixth, **M54 supplies cost; M11 sets price**. This boundary is absolute. The moment a costing
module starts producing prices, it acquires a commercial mandate it is not governed for, and
cost-plus pricing quietly replaces market pricing across fourteen revenue streams.

---

## 5. Functional Areas & Features

### 5.1 Cost Structure & Allocation

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FPA-001 | Cost centre model | Maintain a cost centre hierarchy with a named owner per centre, its permitted cost elements, its allocation behaviour (absorbing, allocating or both) and its entity and branch mapping (BR-FIN-001) | **P0** | L1/L5 |
| FR-FPA-002 | Cost element structure | Define a management cost-element structure — direct labour, parts, travel, field expense, branch overhead, central overhead, depreciation, financing — mapped to the statutory chart without duplicating it | **P0** | L5 |
| FR-FPA-003 | Cost object model | Define cost objects — job, work order, contract, customer, branch, business line, asset, rental unit, technician, channel, project — and the rules by which each may absorb cost | **P0** | L5 |
| FR-FPA-004 | Cost pooling | Gather shared cost into pools by nature and location, from the ledger, with each pool's composition traceable to its ledger lines | **P0** | L5 |
| FR-FPA-005 | Allocation drivers | Maintain allocation drivers — headcount, floor area, job volume, technician hours, revenue, transaction count, asset value — sourced automatically from the owning modules rather than entered | **P0** | L5 |
| FR-FPA-006 | Allocation cycles | Define and execute allocation cycles supporting direct, step-down and reciprocal methods, in a declared sequence, per entity and period | **P0** | L5 |
| FR-FPA-007 | Activity-based allocation | Support activity-based allocation where a driver better reflects consumption than a volume measure | P1 | L5 |
| FR-FPA-008 | Allocation traceability | Show, for any allocated amount on any cost object, the source pool, the driver, the driver value and the proportion applied | **P0** | L5 |
| FR-FPA-009 | Allocation posting | Where an allocation must be reflected in the ledger, compute it and raise it to M19 as a financial event; M54 never posts | **P0** | L5 |
| FR-FPA-010 | Transfer pricing | Apply an approved internal transfer price for services rendered between branches, cost centres or legal entities, and report the internal margin separately | P2 | L5 |

### 5.2 Job, Contract & Resource Costing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FPA-011 | Job costing | Accumulate, per service order and work order, the direct labour, parts consumed, travel, field expense and allocated overhead, and present the job margin against its recognised revenue | **P0** | L5 |
| FR-FPA-012 | Fully loaded technician rate | Compute a fully loaded hourly cost per technician grade and branch — salary, benefits, tools, vehicle, training, non-productive time — and apply it to jobs as hours are recorded | **P0** | L5 |
| FR-FPA-013 | Plan-to-actual rate reconciliation | Apply planned activity rates during the period and reconcile them to actual cost at period end, reporting the under- or over-absorption | **P0** | L5 |
| FR-FPA-014 | Contract costing | Accumulate the cost to serve a contract across its life — call-outs, parts, SLA penalties, account management — against the revenue M53 recognises, and present life-to-date and period margin | **P0** | L5 |
| FR-FPA-015 | Negative-margin contract identification | Identify and report every contract whose margin is negative on a life-to-date or trailing-period basis, with the cost drivers named | **P0** | L5 |
| FR-FPA-016 | Standard costing | Maintain standard costs for repeatable services and products, and report the variance between standard and actual by cause — rate, usage, mix and efficiency | P1 | L5 |
| FR-FPA-017 | Asset and rental-unit costing | Cost each rental unit and revenue-generating asset — depreciation from M49, maintenance, insurance, logistics — against the rental revenue M53 recognises | P1 | L5 |
| FR-FPA-018 | Cost to serve | Compute the cost to serve per customer and per segment, including service, logistics, support-contact and account-management cost | P1 | L5 |
| FR-FPA-019 | Unit economics | Compute and report cost per job, cost per branch, cost per technician-hour, cost per delivery and cost per contact, by period and by dimension | **P0** | L5 |

### 5.3 Profitability Analysis

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FPA-020 | Business-line profitability | Produce a full profit and loss for each of the 14 revenue streams — recognised revenue, direct cost, contribution, allocated overhead and net margin | **P0** | L5 |
| FR-FPA-021 | Branch profitability | Produce a branch P&L with contribution and net margin, using recognised revenue and both directly attributable and allocated cost (BR-FIN-008, BO-07) | **P0** | L5 |
| FR-FPA-022 | Two-margin presentation | Present contribution margin and net margin side by side in every profitability view, so that controllable and allocated cost are never conflated | **P0** | L5 |
| FR-FPA-023 | Customer and segment profitability | Report profitability by customer, corporate account and segment, ranked, with cost to serve visible | P1 | L5 |
| FR-FPA-024 | Channel profitability | Report profitability by channel — counter, field, workshop, e-commerce, marketplace, corporate, rental | P1 | L5 |
| FR-FPA-025 | Multi-dimensional slicing | Allow any profitability view to be sliced and combined across every ledger dimension without a separate data structure | **P0** | L5 |
| FR-FPA-026 | Profitability drill-down | Drill from any margin figure through its components to the underlying ledger lines and source transactions | **P0** | L5 |

### 5.4 Budgeting

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FPA-027 | Budget model | Hold budgets by account, cost centre, branch, business line, project and period, for the July–June fiscal year, in both operating and capital forms | **P0** | L2/L5 |
| FR-FPA-028 | Budget versions and scenarios | Maintain multiple budget versions — draft, submitted, approved, revised — with the approved version locked and every subsequent variance measured against it | **P0** | L5 |
| FR-FPA-029 | Budget workflow | Support top-down targets and bottom-up submission, with preparation, submission, review, challenge, approval and locking, each step recorded with its owner | **P0** | L5 |
| FR-FPA-030 | Driver-based budgeting | Build budget lines from operational drivers — job volume, headcount, branch count, utilisation, average ticket — so that a driver change reflows the budget rather than requiring re-entry | P1 | L5 |
| FR-FPA-031 | Capital budget | Hold the capital budget by category, entity and project, and expose availability and headroom to M49's capital approval | **P0** | L5 |
| FR-FPA-032 | Budget availability check | Answer a budget availability query for a coding combination, returning committed, actual and remaining, for M52 and M49 to consult | **P0** | L5 |
| FR-FPA-033 | Commitment tracking | Track committed spend — approved purchase orders and capital commitments — alongside actuals, so that budget consumption reflects obligations, not just invoices | P1 | L5 |
| FR-FPA-034 | Budget revision control | Permit a budget revision only through an approved reallocation or supplementary approval, retaining the original approved version | **P0** | L5 |

### 5.5 Forecasting, Variance & Management Reporting

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FPA-035 | Rolling forecast | Produce a rolling forecast of the result on a defined cadence, built from operational drivers and updated with actuals as periods close | **P0** | L5 |
| FR-FPA-036 | Variance analysis | Compare actual to budget and to forecast at every level of the cost centre and business-line hierarchy, with drill-down to the causing transactions | **P0** | L2/L5 |
| FR-FPA-037 | Variance explanation capture | Require the accountable owner to record an explanation for every variance above a threshold, within a defined period of the close, and track completion | **P0** | L5 |
| FR-FPA-038 | Scenario modelling | Model the effect of driver changes — branch count, job volume, technician headcount, price change, cost inflation — on the result, and retain each scenario | P1 | L5 |
| FR-FPA-039 | Management and board packs | Produce standard management and board reporting packs from one certified dataset, on a schedule, with no manual assembly (BO-17) | **P0** | L2/L5 |
| FR-FPA-040 | Initiative benefit tracking | Track cost-saving and efficiency initiatives against their claimed benefit, measuring realisation from the ledger rather than from assertion | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **No actuals of its own** | M54 holds no copy of actual cost or revenue. Every actual figure resolves to M19 ledger lines (via M62's warehouse projection for performance). A schema check asserts that no M54 table stores a posted actual amount |
| T-02 | **Single-source margin** | Revenue in every margin computation is **recognised** revenue from M53, never billed revenue from M20. Enforced by the semantic layer, with the source module recorded on every measure definition |
| T-03 | **Allocation determinism** | An allocation cycle re-run over the same period with the same driver values and the same cycle version produces identical results. Every allocation stores its cycle version, pool composition, driver values and proportions |
| T-04 | **Allocation traceability to the ledger line** | Any allocated amount resolves to the ledger lines composing its pool. Traceability is a stored path, not a re-derivation |
| T-05 | **Allocation cycle versioning** | Cycles are versioned and effective-dated. A prior period's allocation is always explained by the cycle version that produced it, never by the current one |
| T-06 | **Driver sourcing, not entry** | Drivers are sourced from their owning modules — headcount from M21, floor area from M47, job volume from M01/M31, technician hours from M02, asset value from M49, revenue from M53. A manually entered driver requires approval and is reported |
| T-07 | **Real-time job costing** | Job cost updates as labour, parts and expense are recorded, using planned activity rates, so that a job's margin is visible before the period closes. Period-end reconciliation adjusts to actual |
| T-08 | **Performance envelope** | Business-line and branch profitability across a full year returns in ≤ 5 s; a full allocation cycle run across all entities completes in ≤ 20 minutes; job-level drill-down resolves in ≤ 3 s |
| T-09 | **Volume envelope** | ~250,000 jobs/year × cost lines, 51+ branches, 14 business lines, ~5M ledger lines/year read per period, ~60–120 cost centres, allocation cycles producing ~500,000 allocation lines/year |
| T-10 | **Budget as a versioned immutable artefact** | An approved budget version is locked and never edited. A revision creates a new version referencing the original; variance is always measured against the version in force |
| T-11 | **Warehouse-backed analytics** | Profitability and variance analytics run against M62's dimensional model rather than the transactional ledger, refreshed on a defined cadence, with the refresh timestamp visible on every report so no one acts on stale data believing it current |
| T-12 | **Read-only integration posture** | M54's database role has no write access to any other module's tables and no journal-posting capability. Allocation postings are raised as M19 events like any other subledger's |
| T-13 | **Event emission via outbox** | Allocation results, budget approvals and forecast publications emit domain events (AS-08) consumed by M19, M49, M52 and M25 |
| T-14 | **Multi-entity scoping** | Cost centres, budgets, allocations and profitability views are entity-scoped; inter-entity allocation is an explicit, approved transfer-pricing transaction (AS-03) |
| T-15 | **Metric definition alignment** | Every financial measure M54 computes is registered in M25's metric registry with one definition, so that a margin figure means the same thing in a board pack, a dashboard and an API response |
| T-16 | **Explanation capture SLA** | Variance explanations are captured within 3 working days of close; completion is tracked and reported per owner |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M54 |
|---|---|---|
| **CEO** | Knows total revenue and total profit; cannot say which of 14 streams earns it | Sees a P&L per business line, per branch and per channel, from one certified dataset |
| **CFO** | Produces a management pack by hand, weeks after close | Reviews a generated pack and challenges the variances the owners have already explained |
| **CCO** | Prices new offers on judgement and competitor observation | Prices with a cost base, and can see which existing offers are unprofitable |
| **Branch manager** | Is told their branch's result, months later, and disputes the overhead in it | Sees contribution (what they control) and net margin (what the business earns), with the overhead traceable |
| **Operations Director** | Manages activity and hopes it converts to margin | Sees cost per job and cost per technician-hour by branch, and can act on the outliers |
| **Corporate Services Head** | Claims 55% rental margin | Demonstrates it — or discovers it is 38% and acts |
| **Account manager** | Fights for every contract renewal equally | Knows which accounts are profitable and which need repricing or exit |
| **Technician / dispatcher** | Unaffected directly | Benefit indirectly: the cost of their time is understood, so productivity investment is justified |
| **Board** | Receives a manually assembled pack, one version per meeting | Receives one pack from one dataset, with variance explanations already captured |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Margin visibility across 14 revenue streams** | Recognised revenue matched to attributed cost per business line | **This is the module that verifies every other module's benefit claim.** MSP (BDT 95 lac), rental (48), refurbishment (65), marketplace (84), data services (30) and dynamic pricing (40) are all margin claims that are unverifiable without M54 |
| **Negative-margin contract recovery** | 100% of loss-making contracts identified with their cost drivers | Directly protects the **BDT 72 lac** AMC/RAMC renewal uplift by ensuring renewals are repriced rather than repeated |
| **Pricing decisions with a cost base** | M11's dynamic pricing operates against a known cost floor rather than a guess | Underwrites the **BDT 40 lac** dynamic-pricing margin uplift claim |
| **Branch performance management** | Branch contribution visible and comparable across 51+ sites | Enables the underperforming-branch conversation to be about facts. Supports **BO-07** |
| **Overhead discipline** | Central cost allocated and visible to the branches carrying it | Overhead that nobody sees is overhead nobody challenges |
| **Budget control** | Availability checked at commitment, not discovered at invoice | Reduces uncontrolled spend and makes the annual budget a live constraint rather than a document |
| **Forecast reliability** | Driver-based rolling forecast maintained by the business | Reduces the surprise-adjustment pattern and improves the quality of every capital and hiring decision |
| **Management reporting labour eliminated** | Packs generated from one certified dataset | Supports **BO-17** — manual reporting packs from 100% to zero; a material share of the **BDT 62 lac** administrative saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The business stops guessing** | Every commercial decision for the next decade — which service lines to grow, which branches to open, what to charge, whom to serve — rests on knowing where margin comes from. This module is the difference between a business that is managed and one that is merely operated |
| **One version of the numbers** | Management and statutory reporting from the same ledger lines. There is no "the finance number" and "the operations number" |
| **Accountability that is fair** | Contribution separated from allocated overhead means managers are measured on what they control. Unfair measurement produces gaming, not performance |
| **Institutional argument quality** | When allocation is traceable, disagreements are about drivers and policy, not about arithmetic. That is a much more productive argument |
| **Investment readiness** | Segment profitability is the first thing an investor, acquirer or lender asks for, and the last thing an unmeasured business can produce |
| **Continuous improvement evidence** | Initiative benefit tracked from the ledger rather than claimed in a presentation |
| **Foundation for AI** | M26's pricing, dispatch and forecasting models need a cost structure to optimise against. Without M54 they optimise revenue and volume while margin does whatever it does |

---

## 8. Lifecycle & State Models

### 8.1 The Period Cost Cycle

```
   M19 PERIOD SOFT-CLOSED
        │  actuals complete: M20 revenue · M52 cost · M21 payroll ·
        │  M15 consumption · M49 depreciation · M53 recognised revenue
        ▼
  ┌──────────────────────┐
  │  ACTUALS AVAILABLE   │  (read from M19 via M62; M54 stores none)
  └──────────┬───────────┘
             │ drivers collected from owning modules
             ▼
  ┌──────────────────────┐  driver missing / unapproved manual driver
  │  DRIVERS RESOLVED    │─────────────────────────────────► EXCEPTION
  └──────────┬───────────┘
             │ cycles executed in declared sequence
             ▼
  ┌──────────────────────┐
  │  ALLOCATION RUN      │  direct → step-down → reciprocal → activity-based
  └──────────┬───────────┘
             │ planned rates reconciled to actual
             ▼
  ┌──────────────────────┐
  │  ABSORPTION          │  under/over-absorption reported and, where policy
  │  RECONCILED          │  requires, raised to M19
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  PROFITABILITY       │  business line · branch · customer · channel ·
  │  COMPUTED            │  contract · job · asset
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐  variance above threshold
  │  VARIANCE ANALYSED   │──────────────► owner must explain within 3 days
  └──────────┬───────────┘
             │ all threshold variances explained
             ▼
  ┌──────────────────────┐
  │  PACK PUBLISHED      │  management pack · board pack · branch packs
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │  FORECAST UPDATED    │  actuals replace forecast for the closed period;
  │                      │  rolling horizon extended
  └──────────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Actuals available | M19 period soft-closed with all subledgers posted | M19 |
| Actuals available | Drivers resolved | Every driver sourced from its owning module for the period | System |
| Drivers resolved | Exception | A driver is missing, or a manual driver lacks approval | System |
| Drivers resolved | Allocation run | Cycles executed in the declared sequence for the entity and period | System |
| Allocation run | Absorption reconciled | Planned activity rates compared to actual cost; variance computed | System |
| Absorption reconciled | Profitability computed | All cost objects populated | System |
| Profitability computed | Variance analysed | Actual compared to the locked budget version and the current forecast | System |
| Variance analysed | Pack published | Every variance above threshold carries an owner's explanation | Cost centre owners → CFO |
| Pack published | Forecast updated | Closed-period actuals replace forecast; the rolling horizon extends | System |

### 8.2 Budget Cycle

```
  ┌──────────────┐  CFO/CEO issue top-down targets by business line and branch
  │  TARGET SET  │
  └──────┬───────┘
         │ distributed to cost centre owners
         ▼
  ┌──────────────┐   drivers seeded from actuals and the forecast
  │  IN          │
  │  PREPARATION │
  └──────┬───────┘
         │ submitted by the cost centre owner
         ▼
  ┌──────────────┐   returned for revision
  │  SUBMITTED   │◄────────────────────────┐
  └──────┬───────┘                         │
         │ reviewed and challenged         │
         ▼                                 │
  ┌──────────────┐                         │
  │  UNDER       │─────────────────────────┘
  │  REVIEW      │
  └──────┬───────┘
         │ approved by the CFO/CEO
         ▼
  ┌──────────────┐   ◄── every variance is measured against THIS version
  │  APPROVED    │       — locked, never edited
  │  (LOCKED)    │
  └──────┬───────┘
         │ supplementary approval or reallocation
         ▼
  ┌──────────────┐
  │  REVISED     │  new version; the original approved version is retained
  │  (v2, v3…)   │
  └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Target set | Top-down targets issued for the fiscal year | CFO / CEO |
| Target set | In preparation | Distributed to cost centre owners with drivers and prior actuals seeded | System |
| In preparation | Submitted | Owner completes and submits their budget | Cost centre owner |
| Submitted | Under review | Finance reviews and challenges against targets and drivers | Finance Manager / CFO |
| Under review | In preparation | Returned for revision with comments | Finance Manager |
| Under review | Approved (locked) | Approved by the CFO and, above threshold, the CEO or board | CFO / CEO |
| Approved | Revised | Supplementary approval or an approved reallocation; original version retained | CFO |

### 8.3 Allocation Cycle Version Lifecycle

| State | Meaning | Exit Condition |
|---|---|---|
| Drafted | Cycle defined — pools, drivers, sequence, method | Test run against a prior period |
| Tested | Executed against historical data with results reviewed for reasonableness | Results accepted |
| Approved | Approved by the CFO with an effective period | Effective period reached |
| Active | In use for allocation runs | Superseded |
| Superseded | Replaced by a later version | **Retained permanently** — prior allocations reference it |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FPA-01 | M54 creates no journal entries; where an allocation must post, it is raised to M19 as a financial event | **H** | CTO |
| BRU-FPA-02 | M54 stores no actual cost or revenue of its own; every actual resolves to M19 ledger lines | **H** | CTO |
| BRU-FPA-03 | Margin is computed on **recognised** revenue from M53, never on billed revenue from M20 | **H** | CFO |
| BRU-FPA-04 | Every allocated amount is traceable to its source pool, driver, driver value and proportion | **H** | CFO |
| BRU-FPA-05 | Allocation cycles are versioned and effective-dated; a prior period's allocation is explained by the version that produced it | **H** | CFO |
| BRU-FPA-06 | Allocation drivers are sourced from their owning modules; a manually entered driver requires approval and is reported | **H** | Finance Manager |
| BRU-FPA-07 | An allocation cycle re-run over the same period with the same inputs produces identical results | **C** | CTO |
| BRU-FPA-08 | Every profitability view presents contribution margin and net margin together; neither is shown alone | **H** | CFO |
| BRU-FPA-09 | An approved budget version is locked and never edited; a revision creates a new version retaining the original | **H** | CFO |
| BRU-FPA-10 | Variance is always measured against the approved budget version in force for the period | **H** | CFO |
| BRU-FPA-11 | A cost centre owner cannot approve their own budget submission | **H** | CFO |
| BRU-FPA-12 | Every variance above the configured threshold requires an explanation from the accountable owner within 3 working days of close | **H** | CFO |
| BRU-FPA-13 | A budget revision requires supplementary approval or an approved reallocation; a budget is never quietly increased | **H** | CFO |
| BRU-FPA-14 | Budget availability reflects committed spend as well as actuals; a commitment consumes budget when it is approved | **C** | CFO |
| BRU-FPA-15 | A capital request exceeding capital budget headroom is reported to M49 as an over-budget condition; M54 never approves it | **H** | CFO |
| BRU-FPA-16 | The fully loaded technician rate is approved by the CFO and applied consistently; it is never varied per job | **H** | CFO |
| BRU-FPA-17 | Under- or over-absorption of planned rates is reported every period and, where policy requires, raised to M19 | **C** | CFO |
| BRU-FPA-18 | An inter-entity or inter-branch transfer price is an approved rate, never negotiated per transaction | **H** | CFO |
| BRU-FPA-19 | M54 supplies a cost base; **it never sets or publishes a price** — that is M11's exclusive scope | **H** | CCO / CFO |
| BRU-FPA-20 | Every financial measure M54 computes is registered in M25's metric registry with a single definition | **H** | CTO |
| BRU-FPA-21 | Every report shows the timestamp of the data refresh it was computed from | **H** | CTO |
| BRU-FPA-22 | A contract identified as negative-margin is reported to the account owner and the CCO within the close cycle | **H** | CFO |
| BRU-FPA-23 | M54 has no write access to any other module's data and no posting capability | **H** | CTO |
| BRU-FPA-24 | Standard costs are approved and effective-dated; a change applies prospectively | **H** | CFO |
| BRU-FPA-25 | Initiative benefit is measured from the ledger, never from a claimed figure | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.cost.center` | `fix_cost_center` | Management cost centre | code, name_en, name_bn, parent_id, entity_id, branch_id, owner_user_id, type (absorbing/allocating/both), permitted_cost_elements, active_from, active_to |
| `fix.cost.element` | `fix_cost_element` | Management cost category | code, name, category (direct_labour/parts/travel/field_expense/branch_overhead/central_overhead/depreciation/financing), gl_account_mapping, behaviour (fixed/variable/semi_variable) |
| `fix.cost.object` | `fix_cost_object` | A thing that absorbs cost | type (job/work_order/contract/customer/branch/business_line/asset/rental_unit/technician/channel/project), reference, entity_id, absorbing_rules_json, active |
| `fix.cost.pool` | `fix_cost_pool` | Gathered shared cost | period_id, entity_id, name, cost_element_ids, source_cost_center_ids, gathered_amount, ledger_line_refs, composed_at |
| `fix.allocation.driver` | `fix_allocation_driver` | A basis of allocation | code, name, source_module, source_metric, unit, collection_method (auto/manual), manual_approval_required |
| `fix.allocation.driver.value` | `fix_allocation_driver_value` | Driver measurement for a period | driver_id, period_id, cost_object_type, cost_object_ref, value, sourced_from, sourced_at, entered_by, approved_by |
| `fix.allocation.cycle` | `fix_allocation_cycle` | An allocation definition | name, entity_id, sequence, method (direct/step_down/reciprocal/activity_based), pool_definition_json, driver_id, target_rule_json, version, state, effective_from, approved_by |
| `fix.allocation.run` | `fix_allocation_run` | An execution | cycle_id, cycle_version, period_id, entity_id, run_at, run_by, pools_processed, lines_generated, total_allocated, inputs_hash, state |
| `fix.allocation.line` | `fix_allocation_line` | One allocated amount, fully traceable | run_id, source_pool_id, target_cost_object_type, target_cost_object_ref, driver_id, driver_value, total_driver_value, proportion, allocated_amount, cost_element_id, ledger_line_refs, cost_center_id, branch_id, business_line_id |
| `fix.activity.rate` | `fix_activity_rate` | Planned fully loaded rate | activity_type (technician_hour/workshop_hour/delivery/contact), grade, branch_id, entity_id, planned_rate, basis_json, effective_from, effective_to, approved_by |
| `fix.absorption.reconciliation` | `fix_absorption_reconciliation` | Planned vs actual | period_id, entity_id, activity_type, planned_applied, actual_cost, over_under_absorption, treatment, raised_to_gl_at |
| `fix.job.cost` | `fix_job_cost` | Cost accumulated on a job | job_id (M01/M31), entity_id, branch_id, business_line_id, labour_hours, labour_cost, parts_cost, travel_cost, field_expense_cost, allocated_overhead, total_cost, recognised_revenue (M53), contribution_margin, net_margin, state, last_computed_at |
| `fix.contract.cost` | `fix_contract_cost` | Cost to serve a contract | contract_id (M08), entity_id, period_id, callout_cost, parts_cost, sla_penalty_cost, account_management_cost, allocated_overhead, total_cost, recognised_revenue, period_margin, life_to_date_cost, life_to_date_revenue, life_to_date_margin, negative_margin_flag |
| `fix.standard.cost` | `fix_standard_cost` | Standard for a repeatable service or product | catalogue_item_id, entity_id, standard_labour, standard_parts, standard_overhead, standard_total, effective_from, effective_to, approved_by |
| `fix.cost.variance` | `fix_cost_variance` | Standard vs actual by cause | period_id, catalogue_item_id or cost_object_ref, rate_variance, usage_variance, mix_variance, efficiency_variance, total_variance, explanation, explained_by |
| `fix.asset.cost` | `fix_asset_cost` | Cost to own and operate | asset_id (M49), period_id, depreciation (M49), maintenance_cost, insurance_cost, logistics_cost, allocated_overhead, total_cost, recognised_revenue (M53), margin, utilisation_pct |
| `fix.cost.to.serve` | `fix_cost_to_serve` | Per customer or segment | customer_id or segment, period_id, service_cost, logistics_cost, contact_cost, account_management_cost, allocated_overhead, total, recognised_revenue, margin, rank |
| `fix.unit.economics` | `fix_unit_economics` | Per-unit measures | period_id, entity_id, branch_id, business_line_id, metric (cost_per_job/cost_per_branch/cost_per_tech_hour/cost_per_delivery/cost_per_contact), value, volume, trend |
| `fix.profitability` | `fix_profitability` | The profitability fact | period_id, entity_id, dimension_set_json (branch, business line, customer, channel, segment), recognised_revenue, direct_cost, contribution_margin, allocated_overhead, net_margin, computed_at, refresh_timestamp |
| `fix.transfer.price` | `fix_transfer_price` | Internal service rate | service_type, from_cost_center_id, to_cost_center_id, from_entity_id, to_entity_id, rate, basis, effective_from, approved_by |
| `fix.budget` | `fix_budget` | Budget header | entity_id, fiscal_year_id, type (operating/capital), version, version_label, state, prepared_by, submitted_at, reviewed_by, approved_by, approved_at, locked_at, supersedes_version, revision_reason |
| `fix.budget.line` | `fix_budget_line` | One budget value | budget_id, account_id, cost_center_id, branch_id, business_line_id, project_id, period_id, amount, currency, driver_basis_json, notes |
| `fix.budget.target` | `fix_budget_target` | Top-down target | fiscal_year_id, entity_id, scope (business_line/branch/cost_center), scope_ref, target_amount, target_type (revenue/cost/margin), issued_by, issued_at |
| `fix.budget.commitment` | `fix_budget_commitment` | Committed but not yet actual | budget_line_id, source (purchase_order/capex_request), source_ref, committed_amount, committed_at, released_amount, state |
| `fix.budget.availability` | `fix_budget_availability` | Cached availability answer | coding_combination_hash, period_id, budget_amount, committed, actual, remaining, computed_at |
| `fix.forecast` | `fix_forecast` | A forecast version | entity_id, fiscal_year_id, horizon_periods, cadence, version, generated_at, generated_by, method (driver_based/trend), driver_assumptions_json, state |
| `fix.forecast.line` | `fix_forecast_line` | One forecast value | forecast_id, period_id, account_id, cost_center_id, business_line_id, forecast_amount, actual_amount, variance, confidence |
| `fix.forecast.driver` | `fix_forecast_driver` | A planning driver | code, name (job_volume/headcount/branch_count/utilisation/average_ticket/attrition/price_change/cost_inflation), owner_role, unit, source_module, current_value, assumption_value |
| `fix.scenario` | `fix_scenario` | Modelled alternative | name, base_forecast_id, driver_changes_json, result_summary_json, created_by, created_at, retained |
| `fix.variance.explanation` | `fix_variance_explanation` | The management process artefact | period_id, scope_type, scope_ref, variance_amount, variance_pct, threshold_breached, owner_user_id, explanation, root_cause_code, action_committed, due_at, submitted_at, accepted_by |
| `fix.management.pack` | `fix_management_pack` | Generated reporting pack | type (management/board/branch/business_line), period_id, scope_ref, sections_json, generated_at, data_refresh_at, document_id, distributed_to |
| `fix.initiative` | `fix_initiative` | Cost-saving or efficiency initiative | name, owner_id, claimed_benefit, benefit_measure_definition, baseline_period_id, start_period_id, realised_benefit_to_date, state, last_measured_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.gl.line`, `fix.gl.account`, `fix.gl.dimension`, `fix.fiscal.period` | M19 | **Read only — the sole source of actuals** |
| `fix.revenue.schedule`, `fix.performance.obligation` (recognised revenue) | M53 | Read — the revenue used in every margin |
| `fix.ar.invoice` | M20 | Read for reference only; **never used as the revenue basis for margin** |
| `fix.ap.invoice`, `fix.expense.claim` (field expense by job) | M52 | Read as attributed cost; supply the budget availability answer back |
| `fix.payroll.run`, `fix.employee`, `fix.attendance.record`, `fix.position` | M21 / M55 / M56 | Read for loaded rates and the headcount driver |
| `fix.stock.issue`, `fix.stock.valuation.event` | M15 | Read for parts cost on jobs |
| `fix.asset`, `fix.depreciation.line`, `fix.capex.request` | M17 / M49 | Read depreciation and asset cost; supply capital budget availability back |
| `fix.service.order`, `fix.work.order`, `fix.service.order` | M01 / M02 | Read as cost objects and volume drivers |
| `fix.field.session`, `fix.field.session` | M02 | Read as the technician-hour driver |
| `fix.contract`, `fix.service.credit` | M08 | Read as cost objects |
| `fix.site`, `fix.site` | M47 | Read as the floor-area driver |
| `fix.consignment`, `fix.consignment` | M03 | Read for cost per delivery |
| `fix.conversation`, `fix.conversation` | M27 | Read for cost per contact |
| `fix.tax.provision`, effective tax rate | M51 | Read for after-tax views |
| `fix.cash.forecast` | M50 | Read for the cash view alongside the result forecast |
| `fix.metric` | M62 | Register every financial measure |
| `fix.warehouse.fact.*` | M62 | The dimensional projection M54's analytics run against |
| `fix.price.resolution.log`, `fix.rate.card` | M11 | Read for price-versus-cost comparison; **M54 never writes a price** |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FPA-01 | M19 period soft-closed | Collect every allocation driver from its owning module for the period and validate completeness | Report missing drivers and **hold the allocation run**; never allocate on a stale or assumed driver |
| AUT-FPA-02 | Drivers resolved | Execute the allocation cycles in their declared sequence for each entity, storing full traceability per line | Halt the run at the failing cycle and report; partial allocation is not published |
| AUT-FPA-03 | Allocation complete | Reconcile planned activity rates to actual cost, compute under/over-absorption and raise it to M19 where policy requires | Report and flag the profitability views as provisional |
| AUT-FPA-04 | Allocation reconciled | Compute profitability across every dimension — business line, branch, customer, channel, contract, asset — and refresh the warehouse projection | Retain the prior computation and mark all reports as stale with the timestamp shown |
| AUT-FPA-05 | Labour, parts or expense recorded against a job | Update the job cost in near real time using planned activity rates | Job cost updates at the next scheduled run |
| AUT-FPA-06 | Profitability computed | Identify every contract with negative life-to-date or trailing-period margin, and notify the account owner and the CCO with the cost drivers named | Report generated; notification retried |
| AUT-FPA-07 | Profitability computed | Compare actual to the locked budget version and the current forecast at every hierarchy level, and identify variances above threshold | Report with a data-availability warning |
| AUT-FPA-08 | Variance above threshold identified | Assign the explanation task to the accountable cost centre owner with a 3-working-day deadline, and track completion | Task escalates to the owner's manager, then to the CFO |
| AUT-FPA-09 | All threshold variances explained, or the deadline reached | Generate the management pack, board pack and branch packs from the certified dataset and distribute them | Pack generated with unexplained variances listed as outstanding |
| AUT-FPA-10 | Period closed | Replace forecast with actual for the closed period, extend the rolling horizon, and reflow driver-based lines | Forecast retains the prior version with a staleness flag |
| AUT-FPA-11 | A forecast driver value changes materially | Reflow the affected forecast lines and notify the forecast owner of the result change | Alert only |
| AUT-FPA-12 | Budget cycle opens | Distribute preparation tasks to cost centre owners, seeded with prior actuals, current forecast and top-down targets | Manual distribution with an alert |
| AUT-FPA-13 | Budget submitted | Route for review, comparing the submission against its target and its driver basis, and highlight material departures | Submission held in the review queue |
| AUT-FPA-14 | Budget approved | Lock the version, publish it as the variance basis, and open budget availability for consumption | Approval held; the prior version remains the basis |
| AUT-FPA-15 | M52 or M49 requests budget availability | Return budget, committed, actual and remaining for the coding combination | Return a service-unavailable response; **the consuming module applies its own policy — M54 never returns a guessed availability** |
| AUT-FPA-16 | A purchase order or capital request is approved | Record the commitment against the budget line and reduce available headroom | Commitment recorded at the next sync with an alert |
| AUT-FPA-17 | A commitment is invoiced or cancelled | Release the commitment and reflect the actual | Commitment ages and is reported |
| AUT-FPA-18 | Monthly | Recompute unit economics, cost to serve, and customer and channel profitability rankings | Retain prior values and alert |
| AUT-FPA-19 | Quarterly | Measure each tracked initiative's realised benefit from the ledger against its claimed benefit | Report with a measurement-unavailable note |
| AUT-FPA-20 | An allocation cycle version is proposed for activation | Run it against a prior period and present the result comparison for CFO approval before activation | Activation blocked |

---

## 12. Interfaces

### 12.1 Upstream — M54 Consumes

| Source | What | Mechanism |
|---|---|---|
| M19 General Ledger | **All actuals** — dimensioned ledger lines, control balances, period state | REST + certified extract |
| M53 Revenue & Settlement | **Recognised revenue** by contract, obligation, business line and dimension | REST + extract |
| M52 Payables & Expense | Actual cost by cost centre, job and dimension, including field expense attributed to jobs | Extract + events |
| M21 HR & Payroll | Payroll cost, headcount, grades, attendance and productive-hour data for loaded rates | REST + extract |
| M15 Inventory | Parts consumption cost by job | Extract |
| M49 Fixed Assets | Depreciation by asset and dimension; capital commitments | Events + REST |
| M01 / M31 Service & Workshop | Job and work-order records as cost objects; job volume as a driver | Extract |
| M02 Field Service | Technician hours, travel and utilisation | Extract |
| M08 Contract & SLA | Contracts as cost objects; SLA penalties | REST |
| M03 Logistics | Delivery volume and logistics cost | Extract |
| M27 Contact Centre | Contact volume for cost per contact | Extract |
| M47 Facility | Floor area by location as an allocation driver | REST |
| M51 Tax & Regulatory | Effective tax rate and tax cost by business line | REST |
| M50 Treasury & Cash | Financing cost; the cash forecast for the combined view | REST |
| M11 Pricing | Rate cards and determined prices, for price-versus-cost comparison | REST |
| M62 Data Platform | The dimensional projection analytics run against | Warehouse |
| M25 Business Intelligence | The metric registry every M54 measure is registered in | REST |

### 12.2 Downstream — M54 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Allocation results and absorption variances requiring posting, as financial events | Events |
| M52 Payables & Expense | Budget availability for an invoice coding combination | REST |
| M49 Fixed Assets | Capital budget availability and headroom for capital approval | REST |
| M50 Treasury & Cash | Budgeted and forecast outflows as cash-forecast input | REST |
| M11 Pricing | **The cost base** — service cost, fully loaded rates, standard costs — as an input to pricing decisions. **M11 sets the price** | REST |
| M12 Marketplace | Marketplace channel economics informing commission scheme design | REST |
| M13 Rental | Rental unit cost and margin | REST |
| M08 Contract & SLA | Contract cost to serve and margin, including the negative-margin flag | REST + events |
| M07 CRM | Customer profitability and cost to serve | REST |
| M25 Business Intelligence | Computed financial measures, profitability facts and variance data for dashboards | Warehouse extract |
| M26 AI/ML Services | Cost structure and driver relationships for optimisation models | Warehouse extract |
| M21 HR & Payroll | Personnel budget by cost centre for establishment control | REST |
| P06 Analytics & Executive Dashboard | Profitability, budget, variance and forecast views | REST |
| P03 Admin Portal | Full costing, budgeting and FP&A workspace | Native |
| Board and management | Generated packs | Document via M24 |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `fpa.allocation_completed` | period, entity, cycles run, lines, total allocated | M19, M25 |
| `fpa.allocation_posting_required` | period, entity, allocation lines requiring GL treatment | M19 |
| `fpa.absorption_variance` | period, activity type, planned applied, actual, over/under | M19, M25 |
| `fpa.profitability_computed` | period, dimensions, revenue, contribution, net margin, refresh timestamp | M25, P06, M11 |
| `fpa.negative_margin_contract` | contract, customer, period margin, life-to-date margin, cost drivers | M08, M07, CCO |
| `fpa.variance_identified` | scope, amount, percentage, threshold, owner | Cost centre owners, M25 |
| `fpa.variance_explained` | scope, explanation, root cause, action committed | CFO, M25 |
| `fpa.variance_explanation_overdue` | scope, owner, days overdue | Owner's manager, CFO |
| `fpa.budget_approved` | entity, fiscal year, version, totals | M19, M52, M49, M50, M21 |
| `fpa.budget_revised` | entity, version, reason, prior version | M52, M49, CFO |
| `fpa.budget_exceeded` | coding combination, budget, committed, actual, overrun | M52, M49, cost centre owner, CFO |
| `fpa.commitment_recorded` / `fpa.commitment_released` | budget line, source, amount | M52, M49 |
| `fpa.forecast_published` | entity, horizon, version, driver assumptions | M50, M49, M25, P06 |
| `fpa.unit_economics_updated` | period, metric, value, dimension | M25, M11, M02 |
| `fpa.pack_published` | pack type, period, scope, document | M24, M25, distribution list |
| `fpa.initiative_benefit_measured` | initiative, claimed, realised, period | CFO, initiative owner |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-FPA-01 | Board and management distribution (email, document repository via M24) | Outbound | Pack distribution |
| INT-FPA-02 | Spreadsheet export for ad-hoc analysis | Outbound | Controlled export with the data-refresh timestamp embedded |
| INT-FPA-03 | Legacy budget spreadsheets | Inbound, one-time | Prior-year budget and actual comparatives; retired at cutover |
| INT-FPA-04 | External benchmarking data (industry cost ratios) | Inbound, optional | Comparative context for cost ratios |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/fpa/profitability` | GET | Profitability by any dimension combination, with contribution and net margin | P03, P06, M25, M11 |
| `/api/v1/fpa/profitability/{id}/drilldown` | GET | Drill from a margin figure to its ledger lines | P03, P06 |
| `/api/v1/fpa/job-cost/{job}` | GET | Job cost and margin | P03, M01, M31 |
| `/api/v1/fpa/contract-cost/{contract}` | GET | Contract cost to serve, life-to-date margin, negative-margin flag | P03, M08, P04 |
| `/api/v1/fpa/cost-to-serve/{customer}` | GET | Customer cost to serve and profitability | P03, M07 |
| `/api/v1/fpa/unit-economics` | GET | Cost per job, branch, technician-hour, delivery, contact | P03, P06, M02 |
| `/api/v1/fpa/cost-base` | GET | **The cost base for pricing** — service cost, loaded rates, standard cost | **M11**, P03 |
| `/api/v1/fpa/activity-rates` | GET · POST | Fully loaded activity rates | P03 |
| `/api/v1/fpa/allocation-cycles` | GET · POST | Author, test, approve and version allocation cycles | P03 |
| `/api/v1/fpa/allocation-runs` | POST · GET | Execute and review allocation | P03 |
| `/api/v1/fpa/allocation-lines/{object}` | GET | Traceability: pool, driver, proportion for any allocated amount | P03, P06 |
| `/api/v1/fpa/budgets` | GET · POST | Budget versions, lines and workflow | P03 |
| `/api/v1/fpa/budgets/{id}/submit` · `/approve` | POST | Budget workflow transitions | P03 |
| `/api/v1/fpa/budget-availability` | GET | **Budget, committed, actual, remaining for a coding combination** | **M52**, **M49**, P03 |
| `/api/v1/fpa/commitments` | POST · DELETE | Record and release a commitment | M52, M49 |
| `/api/v1/fpa/forecast` | GET · POST | Rolling forecast versions and lines | P03, P06, M50 |
| `/api/v1/fpa/forecast/drivers` | GET · PUT | Driver assumptions and ownership | P03 |
| `/api/v1/fpa/scenarios` | POST · GET | Scenario modelling | P03, P06 |
| `/api/v1/fpa/variances` | GET | Variance by scope with threshold flags | P03, P06 |
| `/api/v1/fpa/variances/{id}/explain` | POST | Capture the owner's explanation | P03 |
| `/api/v1/fpa/packs/{type}/{period}` | GET | Generate a management, board or branch pack | P03, P06, M24 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves budgets, allocation cycles, activity rates, standard costs and transfer prices |
| R26 Finance Manager | C R U A | All entities; runs allocation, prepares budgets and forecasts, manages variance process |
| R27 Finance Officer | C R | Assigned scope; driver collection, cost analysis, pack preparation — **cannot approve budgets or cycles** |
| R01 Chief Executive Officer | R A | All; approves budgets above the CFO band; board pack |
| R04 Chief Commercial Officer | R | Business line, customer, channel and contract profitability; **receives the cost base, sets no cost** |
| R05 Operations Director | R U A | All branches; owns branch and operational cost centre budgets and variance explanations |
| R06 Branch Manager | R U | **Own branch only** — P&L, contribution, budget, variance explanation |
| R02 Chief Technology Officer | R U | IT cost centre budget and variance; technical oversight of the module |
| R30 HR Manager | R U | Personnel budget by cost centre; headcount driver |
| R17 Inventory Manager / R19 Procurement Officer | R U | Own cost centre budget and variance |
| R21 Sales Manager / R22 Account Manager (Corporate) | R | Customer and contract profitability for assigned accounts |
| R32 Quality Manager / ISO Coordinator | R | Cost of quality and initiative benefit tracking |
| R33 IT / System Administrator | R | Configuration support; **no budget approval, no cycle approval** |
| R38 External Auditor | R | Scoped read-only — allocation basis and management-to-statutory reconciliation |
| Cost centre owners (various roles) | R U | **Own cost centre only** — budget preparation and variance explanation |

**Field-level restrictions.** A branch manager sees their own branch's full P&L and no other
branch's detail, though they may see anonymised or ranked comparatives where policy permits.
Customer profitability and cost to serve are visible to R01–R05, R21, R22, R26 and R27 only.
Fully loaded technician rates and personnel cost by individual are restricted to R01–R03, R26,
R27 and R30 — **never to branch managers at individual level**, only in aggregate, because
individual pay is not a costing artefact.

**Segregation of duties.**
- A cost centre owner cannot approve their own budget submission — hard block.
- The user who authors an allocation cycle cannot approve it.
- The user who prepares a forecast cannot be its sole approver.
- **M54 has no posting rights at all**: no role in this module can create a journal entry, in any entity, at any value.
- R33 IT / System Administrator can operate the module but can never approve a budget, a cycle or a rate.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Business-line P&L** | CEO, CFO, CCO, board | Monthly | Recognised revenue, direct cost, contribution, allocated overhead and net margin for each of the 14 streams |
| **Branch P&L and league table** | CEO, CFO, Operations Director, Branch Managers | Monthly | Contribution and net margin per branch, ranked, with per-job and per-technician-hour economics |
| **Contract profitability and negative-margin register** | CFO, CCO, Account Managers | Monthly | Every contract's period and life-to-date margin, with **100% of negative-margin contracts identified** and their drivers named |
| **Customer profitability ranking** | CCO, CFO, Account Managers | Quarterly | Customers ranked by margin, with cost to serve, and the loss-making tail identified |
| **Channel profitability** | CCO, CEO | Monthly | Counter, field, workshop, e-commerce, marketplace, corporate and rental |
| **Job cost and margin analysis** | Operations Director, Branch Managers, CFO | Weekly | Cost and margin by job type, branch, technician and business line; outliers surfaced |
| **Unit economics dashboard** | CEO, CFO, Operations Director | Monthly | Cost per job, per branch, per technician-hour, per delivery, per contact — with trend |
| **Allocation traceability report** | Branch Managers, cost centre owners, CFO | Monthly | For every allocated amount: source pool, driver, driver value and proportion — **the credibility artefact** |
| **Absorption variance** | CFO, Finance Manager | Monthly | Planned rates applied against actual cost, by activity type and branch |
| **Budget vs actual vs forecast** | All cost centre owners, CFO, CEO | Monthly | Variance at every hierarchy level with drill-down to transactions |
| **Variance explanation status** | CFO, CEO | Per close | Explanations required, submitted, outstanding, by owner — against the 3-day, 100% target |
| **Rolling forecast** | CEO, CFO, board | Monthly | Result forecast by driver, with prior-version accuracy |
| **Scenario comparison** | CEO, CFO, board | On demand | Modelled alternatives with driver assumptions stated |
| **Capital budget consumption** | CFO, CEO, M49 | Monthly | Approved, committed, spent and remaining by category and project |
| **Cost structure analysis** | CFO, CEO | Quarterly | Fixed vs variable, direct vs overhead, by business line and branch; trend |
| **Standard vs actual cost variance** | CFO, Operations Director, CCO | Monthly | Rate, usage, mix and efficiency variance by service and product |
| **Rental and asset economics** | Corporate Services Head, CFO | Monthly | Cost to own and operate against rental revenue and utilisation — verifying BO-13 |
| **Management pack / board pack** | Board, executive team | Monthly / quarterly | One pack from one certified dataset, with the data-refresh timestamp on every page (BO-17) |
| **Initiative benefit realisation** | CFO, CEO, initiative owners | Quarterly | Claimed vs measured benefit from the ledger |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W8 Target |
|---|---|---|---|---|
| — | **Budget variance explained within 3 days of close** | n/a | 90% | **100%** |
| — | **Contracts with negative margin identified** | unknown | 100% visible | **100% visible** |
| — | Business lines with a complete P&L | 0 of 14 | 14 of 14 | **14 of 14** |
| — | Branches with a complete P&L including allocated overhead | 0 of 51+ | 51+ | **51+** |
| — | Jobs with a computed cost and margin | 0% | 95% | **> 99%** |
| — | Allocated cost that is fully traceable to pool, driver and proportion | n/a | 100% | **100%** |
| — | Allocation drivers sourced automatically (not manually entered) | n/a | 90% | **> 97%** |
| — | Management packs assembled manually | 100% | < 20% | **Zero** (BO-17) |
| — | Elapsed days from period close to management pack publication | 15–20 | 5 | **≤ 3** |
| — | Forecast accuracy at one-quarter horizon | n/a | ±12% | **±7%** |
| — | Budget submissions received by the cycle deadline | n/a | 90% | **100%** |
| — | Spend committed against an approved budget line | unmeasured | 92% | **> 98%** |
| — | Under/over-absorption as % of applied cost | n/a | < 8% | **< 4%** |
| — | Cost centres with a named accountable owner | unmeasured | 100% | **100%** |
| — | Financial measures registered in the M25 metric registry with one definition | n/a | 100% | **100%** |
| — | Management-to-statutory reconciliation differences | n/a | **Zero** | **Zero** |
| — | Initiatives with benefit measured from the ledger | 0% | 80% | **100%** |

> **Register note.** M54 has **no KPI identifiers allocated in `06-02`** — the module did not
> exist in the v2.0 register. The **budget-variance-explained and negative-margin-contract
> metrics are named in `_CATEGORY_OVERVIEW.md` §8** and must be registered as canonical. All
> seventeen metrics require allocation — recorded as audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account` — analytic accounting, analytic distribution | 14% |
| L2 | OCA `mis-builder` (management report definitions — a strong fit for packs), `account-analytic`, `account-budgeting`, `account-financial-reporting` | 26% |
| L3 | Free reporting and export aids | 4% |
| L5 | `cd_cost_allocation`, `cd_job_costing`, `cd_budget_ext`, `cd_fpa_forecast` | 56% |

> `mis-builder` carries an unusually large share for a Category G module. It is genuinely
> capable for management report definition over the ledger, and using it avoids rebuilding a
> reporting engine. The custom share is concentrated in allocation, job costing and the budget
> and forecast models, none of which have a usable open-source equivalent.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-183** | `cd_cost_allocation` — cost centre and element model, pooling, driver sourcing, direct/step-down/reciprocal/activity-based cycles, versioning, full traceability, transfer pricing | Odoo module + service | **7 PW** |
| **CD-184** | `cd_job_costing` — job and contract cost accumulation, fully loaded activity rates, plan-to-actual absorption reconciliation, standard costing and variance, asset and cost-to-serve costing, unit economics | Odoo module + service | **6 PW** |
| **CD-185** | `cd_budget_ext` — budget model with versions and scenarios, top-down/bottom-up workflow, locking, capital budget, availability service, commitment tracking, revision control | Odoo module | 5 PW |
| **CD-186** | `cd_fpa_forecast` — driver-based rolling forecast, scenario modelling, variance identification and explanation capture with SLA tracking, pack generation, initiative benefit tracking | Odoo module + service | 4 PW |

> **CD register position.** M54 is new in v2.1 and had no allocation in `02-05` §5.2. Four new
> IDs, **CD-183…186**, are claimed from the Category G block defined in `M19` §16.2 — completing
> that block. **All CD IDs remain provisional** pending the unified CD register required by audit
> finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M19 General Ledger (W3) | **The sole source of actuals.** M54 cannot exist without a clean, fully dimensioned ledger |
| M20 Receivables (W3) | Revenue transactions in the ledger |
| M52 Payables & Expense (W3) | Actual cost, including field expense attributed to jobs — without job attribution, job costing is incomplete |
| M53 Revenue & Settlement (W4) | **Recognised revenue** — the only revenue basis M54 uses for margin |
| M51 Tax (W4) | Effective tax rate for after-tax views |
| M49 Fixed Assets (W5) | Depreciation by dimension, and the capital budget relationship. **M49 is W5, before M54's W6** — M49 holds capital budgets as a configured allocation in W5 and migrates to M54's model in W6 (`M49` §18 Q-03) |
| M21 HR & Payroll (W5) | Payroll cost and headcount — the largest single cost pool and the primary driver |
| M62 Data Platform (W4) | The dimensional projection analytics run against |
| M25 Business Intelligence (W4) | The metric registry every M54 measure registers in |
| M01 / M31 / M02 (W1–W2) | Jobs, work orders and technician hours as cost objects and drivers |
| M08 Contract & SLA (W4) | Contracts as cost objects |
| M47 Facility (W7) | Floor area as an allocation driver; a configured value is used until M47 lands |

> **Why W6 and not earlier.** M54 depends on six other finance and operational modules being
> live and producing clean data. Attempting it earlier produces allocations over incomplete
> actuals, which is worse than no allocation at all — a wrong margin number is acted upon, a
> missing one is not. **But its absence is deliberately visible in KPI reporting from Wave 4**
> (`_CATEGORY_OVERVIEW.md` §10), so that the gap is a managed condition rather than a
> forgotten one.

**Delivers into:** M11 (cost base for pricing), M52 and M49 (budget availability), M50 (forecast
outflows), M08 and M07 (contract and customer margin), M25 (measures for dashboards), M26 (cost
structure for optimisation), and the board.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Cost centre structure | 60–120 centres | `fix.cost.center` | W6 minus 2 months |
| Cost element structure | Full management structure | `fix.cost.element` | W6 minus 2 months |
| Current-year budget | All cost centres and branches | `fix.budget` (as an approved version) | **W6 cutover** |
| Prior-year budget and actuals | 1–2 years | `fix.budget` (superseded versions), warehouse comparatives | W6, best-effort |
| Allocation policy and drivers | Current practice, where documented | `fix.allocation.cycle`, `fix.allocation.driver` | W6 minus 1 month |
| Fully loaded technician rates | Per grade and branch | `fix.activity.rate` | W6 minus 1 month |
| Standard costs for repeatable services | Where they exist | `fix.standard.cost` | W6 |
| Historical actuals for trend and forecast seeding | From M19 from W3 onward | Warehouse (M62) | W6 — **no external migration needed** |
| Capital budget | Current year | `fix.budget` (capital), from M49's W5 configured allocation | W6 |

> **Migration position.** M54 requires almost no data migration, and that is by design: its
> actuals come from M19, which by Wave 6 holds three waves of clean, dimensioned history. The
> only genuine migration is the **current-year budget**, which must be loaded as an approved
> locked version so that variance measurement begins immediately. The allocation policy is the
> harder item — **current practice is largely undocumented, and the allocation cycles must
> therefore be designed rather than migrated**, with the design agreed with branch managers
> before activation. An allocation basis imposed without that agreement will be rejected the
> first time it produces an unwelcome branch result.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | M54 stores no actual cost or revenue of its own; every actual resolves to M19 ledger lines | Schema assertion and code review |
| AC-02 | M54 has no journal-posting capability and no write access to another module's data | Database grant audit and code review |
| AC-03 | Every margin computation uses recognised revenue from M53, never billed revenue from M20 | Measure-definition review plus a reconciliation test |
| AC-04 | Management reporting and statutory reporting reconcile exactly for every period | Three consecutive monthly reconciliations signed by the CFO |
| AC-05 | Every allocated amount is traceable to its source pool, driver, driver value and proportion | Full-table assertion plus a traceability test on 50 sampled amounts |
| AC-06 | Re-running an allocation cycle over the same period with the same inputs produces identical results | Determinism test |
| AC-07 | A prior period's allocation is explained by the cycle version that produced it, not the current one | Scripted scenario across a cycle-version change |
| AC-08 | Allocation runs are held when any driver is missing; no allocation proceeds on a stale or assumed driver | Negative test per driver |
| AC-09 | More than 97% of allocation drivers are sourced automatically from their owning modules | Production measurement |
| AC-10 | A complete P&L is produced for all 14 business lines and all 51+ branches | Output review reconciled to the group P&L |
| AC-11 | Every profitability view presents contribution margin and net margin together | UI and API review |
| AC-12 | Any margin figure drills through to the underlying ledger lines in ≤ 3 s | Performance and correctness test |
| AC-13 | Business-line and branch profitability for a full year returns in ≤ 5 s | Performance test at production volume |
| AC-14 | A full allocation cycle run across all entities completes in ≤ 20 minutes | Performance test |
| AC-15 | Job cost and margin are computed for more than 99% of jobs | Production measurement |
| AC-16 | 100% of negative-margin contracts are identified and notified to the account owner and the CCO within the close cycle | Three consecutive closes |
| AC-17 | An approved budget version is locked and cannot be edited; a revision creates a new version | Negative test |
| AC-18 | Variance is always measured against the approved version in force for the period | Scripted scenario across a revision |
| AC-19 | A cost centre owner cannot approve their own budget submission | SoD negative test |
| AC-20 | 100% of variances above threshold carry an owner's explanation within 3 working days of close | Three consecutive closes |
| AC-21 | Budget availability returns budget, committed, actual and remaining, and returns an explicit unavailable response rather than a guess when it cannot compute | Contract test with M52 and M49 |
| AC-22 | An approved purchase order or capital request consumes budget headroom at approval, not at invoice | Scripted scenario |
| AC-23 | The rolling forecast regenerates on cadence, retains versions, and measures accuracy against actual | Twelve weeks of forecast-to-actual measurement |
| AC-24 | Management and board packs generate from one certified dataset with no manual assembly, and every page carries the data-refresh timestamp | Three consecutive monthly packs |
| AC-25 | Every financial measure M54 computes is registered in M25's metric registry with a single definition | Registry audit |
| AC-26 | Allocation cycle design is reviewed and accepted by branch managers before activation | Signed acceptance from a representative branch-manager group |
| AC-27 | All branch-manager-facing profitability and budget screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-28 | CFO, CEO and a nominated Branch Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 28 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **What is the allocation policy?** Which costs are allocated, on what drivers, in what sequence — and is it agreed with branch managers before activation? Current practice is largely undocumented, so this is design work, not migration | CFO / Operations Director / Branch Managers | **W6 minus 4 months — the largest single design item in this module** |
| Q-02 | Is head-office cost allocated to branches at all, or are branches measured on contribution only? Both are defensible; the choice determines what "branch profitability" means and how branch managers are held accountable | CFO / CEO | **W6 design — determines the whole reporting model** |
| Q-03 | What is the cost centre structure, and does it match the operational branch hierarchy or differ from it? (Also raised as `M19` §18 Q-11) | CFO / Operations Director | W6 minus 3 months |
| Q-04 | How is the fully loaded technician rate composed — which cost elements, and how is non-productive time treated? This single rate drives every job margin in the business | CFO / Operations Director / HR Manager | **W6 minus 2 months — high leverage** |
| Q-05 | What variance threshold triggers a mandatory explanation, by value and by percentage, and does it differ by cost centre size? | CFO | W6 build |
| Q-06 | Is budget control a warning or a hard block, and does it differ by expense category? (Also raised as `M52` §18 Q-10) | CFO | W6 design |
| Q-07 | What is the budget calendar — when does preparation start, when is approval required, and how does it align to the July–June fiscal year? | CFO / CEO | W6 minus 3 months |
| Q-08 | What is the forecast cadence — monthly, quarterly, or continuous — and who owns each driver assumption? | CFO / CEO / Operations Director | W6 design |
| Q-09 | Which drivers are the forecast built on, and are operational owners prepared to own their assumptions? A driver-based forecast that finance owns entirely is just an extrapolation | CFO / Operations Director / CCO | W6 design |
| Q-10 | Is inter-branch and inter-entity transfer pricing required in Wave 6, or can FR-FPA-010 (P2) follow? | CFO | W6 design |
| Q-11 | Do branch managers see other branches' results, ranked comparatives only, or nothing? This is a management-culture decision with real consequences for behaviour | CEO / Operations Director | W6 design |
| Q-12 | Are standard costs maintained for repeatable services, or is actual costing sufficient? Standard costing adds maintenance burden and only pays back where volumes are high and processes are stable | CFO / Operations Director | W6 design |
| Q-13 | What is the negative-margin contract escalation process once a contract is identified — reprice, renegotiate, or exit — and who decides? Identifying them is worthless without it | CCO / CFO | W6 build |
| Q-14 | What is the definition of each of the 14 business lines for costing purposes, and is it stable? A business line that is redefined annually cannot be trended | CCO / CFO | **W6 minus 3 months** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition), §4 (money flow — M54 reads the GL), §5 (boundary
map — costing and budgeting are M54, not M19), §8 (KPIs — budget variance explained 100%,
negative-margin contracts 100% visible), §9 (W6, "profitability by business line"), §10 (risk —
"costing never implemented, so margin stays unknown") ·
`M19_Financial_Accounting_and_General_Ledger.md` (**the sole source of actuals**; the seven-
dimension model that makes profitability analysis a query rather than a data structure; Category
G CD block; cost centre question Q-11) ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` (**recognised revenue** — the only
revenue basis for margin) ·
`M52_Accounts_Payable_and_Employee_Expense.md` (actual cost, field expense attributed to jobs,
budget availability consumption) ·
`M49_Fixed_Assets_and_Capital_Investment.md` (depreciation by dimension, capital budget
relationship and the W5/W6 sequencing question) ·
`M50_Treasury_Cash_and_Banking.md` (cash forecast — distinct from the result forecast) ·
`M51_Tax_and_Regulatory_Compliance_Bangladesh.md` (effective tax rate by business line) ·
`M20_Accounts_Receivable_Invoicing_and_Collections.md` (billed revenue — explicitly **not** the
margin basis) ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md`
(**M54 supplies cost; M11 sets price** — the absolute boundary) ·
`03_Modules/J_Data_Analytics_and_Intelligence/M25_Business_Intelligence_and_Reporting.md`
(the metric registry) ·
`03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` and
`M02_Field_Service_and_Dispatch_Management.md` (jobs and technician hours as cost objects and
drivers) ·
`03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md` (the largest cost pool and
the headcount driver) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` BO-06, BO-07,
BO-11, BO-13, BO-14, BO-17

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-001 (cost centre),
BR-FIN-008 (branch-wise P&L), §Process 8 (As-Is manual consolidation) ·
`1000FiX_Services_Company_Profile.md` §Core Services (the 14 revenue streams), §Service
Infrastructure (51+ branches) · `1000fix_business/Business planning for 1000 fix.docx`
§Business lines and margin assumptions

**External benchmark**
SAP S/4HANA Controlling (CO) — cost centre accounting, activity types with planned rates,
assessment and distribution cycles, profitability analysis with characteristics ·
[SAP S/4HANA Universal Journal — the removal of the FI/CO reconciliation problem, and the design lesson that management accounting must not hold its own copy of actuals](https://sapinsider.org/articles/mastering-acdoca-7-essential-universal-journal-insights-for-sap-s-4hana-consultants-2025-edition/) ·
[Oracle Fusion Cloud Cost Management and Profitability and Cost Management](https://www.oracle.com/erp/financial-management/) —
allocation rules with drivers, traceable allocation paths, profitability modelling ·
[Microsoft Dynamics 365 Finance — Cost Accounting and Budgeting](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
cost elements and objects, allocation bases and policies; budget planning across all dimensions ·
[Budget planning in Dynamics 365 Finance](https://avantiico.com/budget-planning-d365-finance/) —
scenarios, workflow, top-down and bottom-up ·
Anaplan / Workday Adaptive Planning class FP&A practice — driver-based rolling forecasts,
scenario modelling, variance commentary captured in-system ·
[OCA mis-builder and account-financial-reporting](https://github.com/OCA/account-financial-reporting) —
management report definition over the ledger

---

*Module M54 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
