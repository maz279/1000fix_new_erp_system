---
id: FIX-ERP2-M49
module_id: M49
module_code: FXA
module_name: Fixed Assets & Capital Investment
category: G — Finance & Treasury
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Financial Officer
system_owner: Finance Squad
priority: P2
wave: W5
---

# M49 — Fixed Assets & Capital Investment
### Category G · Code `FXA` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M49 |
| **Module code** | `FXA` |
| **Category** | G — Finance & Treasury |
| **Status** | ★ **New** — extracted from the v2.0 M19 monolith after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Chief Financial Officer |
| **System owner** | Finance Squad |
| **Delivery layers** | L1 Odoo `account_asset` · L2 OCA `account-fixed-asset` family · L5 custom capital approval, dual-book depreciation, CWIP and verification |
| **Custom modules** | `cd_fixed_asset_ext`, `cd_capex_approval`, `cd_asset_depreciation_bd`, `cd_cwip` |
| **Requirement range** | FR-FXA-001 … FR-FXA-034 |
| **Requirement count** | **34** *(measured — supersedes the 22 estimate in `02-02`)* |
| **Effort estimate** | **16 person-weeks** *(measured — supersedes the 11 PW estimate)* |
| **Depends on** | M19 GL · M52 Payables · M51 Tax · M50 Treasury · M54 Costing · M33 Party Master · M30 Platform Admin |
| **Depended on by** | M19, M51, M54, M13, M45, M46, M47, M17, M15, M25 |

---

## 2. Purpose

M49 is **the financial truth about what 1000FiX owns**: what was bought, what it cost, what it
is worth now, where it is, who is accountable for it, and what it will cost to replace.

Every other module that touches an asset sees it operationally. M45 sees a calibrated
multimeter that a technician has signed out. M46 sees a delivery van with a service due. M47
sees a branch air conditioner that needs maintenance. M17 sees a monitored device. M13 sees a
laptop out on rental. All of those views are correct and none of them is the balance sheet.
M49 is the balance sheet, and it is the only module that decides that an expenditure has become
an asset.

Two things make this more than bookkeeping for 1000FiX. First, the Company is **expanding its
branch network** — the 1000FiX Station programme — and every new branch is a capital event
with fit-out, equipment, furniture and IT. Without a capital approval and tracking process, the
cost of opening a branch is discovered afterwards. Second, the **rental business** capitalises
devices that generate revenue, and BO-13's 55% gross margin target is meaningless unless the
depreciation of those devices is accurate and matched to the revenue M53 recognises.

There is also a statutory reason M49 cannot be an afterthought. Bangladesh's Income Tax Act
2023 prescribes its own depreciation rates under the Third Schedule — different from any
sensible accounting policy — which means the Company must maintain **two depreciation books over
one asset register**, permanently. That is not a reporting variation; it is a structural
requirement.

### Why It Exists

The v2.0 draft carried fixed assets as `cd_fixed_asset_ext` inside M19. That places an
operational estate — thousands of items across 51+ branches, moving between locations, held by
named people, verified physically — inside the statutory ledger. The register would then be
maintained by whoever had time, and the classic outcome follows: the register and the general
ledger diverge, and by year three nobody can reconcile them without a full physical count.

The category KPI is explicit and unforgiving: **fixed asset register reconciled to GL, 100%.**

M49 is P2 and lands in Wave 5 because the ledger can carry asset balances as control-account
totals through Waves 3 and 4. What it cannot do indefinitely is carry them without an underlying
register, and the longer that continues the more expensive the eventual reconstruction becomes.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FIN-015 | "Track fixed assets and calculate depreciation" (P2) |
| ERP BRD NFR-022 | "Bangladesh NBR income tax computation compliance" — which requires Third Schedule tax depreciation |
| ERP BRD §Data Retention | Financial records 7 years — Companies Act / NBR |
| `_CATEGORY_OVERVIEW.md` §2 | M49 scope: "Asset register, capitalisation, depreciation, disposal, CWIP, impairment, capital approval" |
| `_CATEGORY_OVERVIEW.md` §5 | "Fixed asset capitalisation and depreciation — M49; not M17, M45, M46 (operational views)" · "Rental-pool assets as capitalised assets — M49 (with M13)" |
| `_CATEGORY_OVERVIEW.md` §8 | **Fixed asset register reconciled to GL: 100%** |
| `_CATEGORY_OVERVIEW.md` §9 | W5 — "capital under control" |
| Business Objective BO-13 | Rental gross margin 55% — requires accurate depreciation of the rental pool |
| Company Profile §Growth Initiatives | "Expanding service center network (1000FiX Station)" — the capital programme M49 governs |
| Company Profile §Service Infrastructure | 51+ service centres — the estate the register covers |
| Exec Summary §6.2 | Rental gross margin **BDT 48 lac/year** — depreciation-sensitive |
| `M15` §3.2 | "Rental-pool devices as capitalised assets — M49 (with M13); M15 holds the visibility, M49 holds the capitalisation" |
| Income Tax Act 2023, Third Schedule | Depreciation rates by asset class; initial and accelerated allowances |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M49 owns the *financial* asset. Five other modules own
> *operational* views of the same physical items, and every one of those boundaries is stated
> here and claimed reciprocally.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Capital expenditure request, business case, approval workflow and authorisation limits |
| 2 | Capital budget consumption tracking against approved capex |
| 3 | The fixed asset register: identity, class, cost, location, custodian, dates and status |
| 4 | Capitalisation policy and the threshold decision — what becomes an asset and what is expensed |
| 5 | Capitalisation from vendor invoices, imports, internal construction and internal transfers |
| 6 | Componentisation where components have different useful lives |
| 7 | **Capital work in progress (CWIP)**: accumulation, allocation and transfer to an active asset |
| 8 | **Dual-book depreciation**: the accounting book under the Company's policy and the tax book under the Third Schedule |
| 9 | Depreciation methods, useful lives, residual values and their approved change |
| 10 | Depreciation runs, catch-up, suspension and reinstatement |
| 11 | Asset revaluation where the accounting policy permits it |
| 12 | Impairment: indicator assessment, testing, recognition and reversal |
| 13 | Asset transfer between locations, branches, cost centres and legal entities |
| 14 | Custodianship: the named person accountable for an asset |
| 15 | Physical verification: schedule, execution, variance, and register correction under approval |
| 16 | Asset tagging, barcode and QR labelling |
| 17 | Disposal: approval, method (sale, scrap, trade-in, donation), gain or loss, and disposal proceeds |
| 18 | Write-off of lost, stolen or destroyed assets |
| 19 | Leased assets and right-of-use recognition where the framework requires it |
| 20 | Insurance coverage tracking against asset values, and claim linkage |
| 21 | Asset-level financial reporting: schedules, movements, ageing and net book value |
| 22 | Post-implementation review of major capital projects against their business case |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Journal posting of capitalisation, depreciation, impairment and disposal | **M19** General Ledger | Only Category G's ledger creates journal entries; M49 computes and raises |
| Vendor invoice capture, matching, approval and payment | **M52** Payables | M52 processes the invoice; M49 decides that its subject is an asset |
| Purchase requisition, RFQ and purchase order for capital items | **M16** Procurement | The buying process is the same whether the item is capital or expense |
| Import documentation, duty and landed cost on imported assets | **M44** Import & Landed Cost | Landed cost is computed once, upstream, and adopted as the asset cost |
| **Tax depreciation rates, income-tax computation and disallowances** | **M51** Tax & Regulatory | M51 owns the Third Schedule rates and the tax return; M49 holds the tax book they drive |
| Test equipment, tools and calibrated instruments — issue, return, calibration, condition | **M45** Enterprise Asset & Test Equipment | A multimeter is operationally an issued tool; financially it is an M49 asset. Both are true |
| Vehicle operations, fuel, maintenance, driver, licensing, trips | **M46** Fleet & Vehicle | M46 runs the van; M49 depreciates it |
| Facility maintenance, utilities, occupancy, workplace services | **M47** Facility & Workplace | M47 maintains the branch; M49 carries its fit-out |
| Customer and monitored device registry, telemetry, health | **M17** Device & Asset Registry | A customer's device is never a 1000FiX asset |
| Rental fleet operation: availability, booking, utilisation, condition, damage | **M13** Rental & EaaS | M13 rents the laptop; M49 capitalises and depreciates it |
| Rental revenue recognition | **M53** Revenue & Settlement | M53 recognises the income; M49 depreciates the asset producing it |
| Inventory, consumables and spare parts stock | **M15** Inventory | Stock is not a fixed asset; the transfer between them is a controlled M15/M49 event |
| Maintenance planning, preventive schedules and work orders on assets | **M45** / **M46** / **M47** | Maintenance is operational; its cost may or may not be capital, and M49 decides only that |
| Capital budget setting and the wider financial plan | **M54** Costing & FP&A | M54 owns the budget; M49 consumes and reports against it |
| Cash availability for capital spend | **M50** Treasury & Cash | M50 reports whether the cash exists |
| E-waste disposal, recycling certificates and environmental compliance | **M18** E-Waste & Circular Economy | M49 records the financial disposal; M18 disposes of it lawfully |
| Document storage of title deeds, invoices and certificates | **M24** Document & Records | M49 references; M24 stores |

### 3.3 Shared Concepts

| Concept | M49's Role | Owning Module |
|---|---|---|
| Fixed asset | **Owns** the financial asset — the defining artefact of this module | M49 |
| Physical item | Owns the financial identity; the operational module owns its use | M49 / M45 / M46 / M47 / M17 / M13 |
| Asset cost | **Owns**; adopts landed cost from M44 and invoice value from M52 | M49 / M44 / M52 |
| Depreciation (accounting book) | **Owns** the computation; M19 posts | M49 / M19 |
| Depreciation (tax book) | Owns the book; **M51 owns the rates and the tax computation** | M49 / M51 |
| Asset carrying value | Owns the register detail; M19 owns the control account | M49 / M19 |
| CWIP | **Owns** | M49 |
| Capital budget | Consumes and reports; M54 owns the budget | M49 / M54 |
| Custodian | **Owns** the financial accountability; HR owns the person | M49 / M21 |
| Asset location | **Owns** the register location; the operational module owns the working location | M49 / M45 / M46 / M47 |
| Rental pool asset | **Owns** the capitalisation; M13 owns the rental operation and M15 the stock visibility until allocation | M49 / M13 / M15 |
| Disposal | **Owns** the financial disposal; M18 owns lawful disposal and M14 owns trade-in valuation | M49 / M18 / M14 |
| Insurance | Owns the value-to-cover linkage; the policy itself sits with Finance administration | M49 |
| Impairment | **Owns** | M49 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Asset Accounting (FI-AA) in the Universal Journal** | Asset accounting permanently reconciled with the GL in ACDOCA — the old FI-AA-to-GL reconciliation step is gone; parallel valuation with each depreciation area mapped to an accounting principle; assets under construction with settlement to a final asset; transfers, retirement and scrapping across the lifecycle | **Two things, both structural.** First, the **register and the ledger reconcile by construction, not by a monthly exercise** — M49 raises every movement as an event and M19 posts it, so a divergence is impossible rather than merely unwelcome. Second, **parallel depreciation areas mapped to accounting principles** — our accounting book and Third Schedule tax book are two areas over one asset, not two systems. Also adopted: CWIP settling to a final asset as a first-class transaction | SAP's depreciation-area configuration depth and its ledger-group apparatus; two books over one principle set is our whole requirement |
| **Oracle Fusion Cloud — Assets** | Mass additions from Payables, asset categories driving default depreciation rules, asset books (corporate and tax), physical inventory reconciliation, retirement with proceeds and cost of removal | **Mass additions from Payables as the primary capitalisation path.** An asset should be created *from* the invoice that bought it, carrying the invoice reference, not keyed separately from a printout — this is the single largest source of register-to-ledger divergence. Also adopted: category-driven defaults, so an asset class implies its life, method and tax class rather than depending on the person creating it | Oracle's multi-book/multi-currency reporting depth |
| **Microsoft Dynamics 365 Finance — Fixed Assets** | Asset books with independent depreciation profiles, asset lifecycle states, budgeting for fixed assets, mass update and disposal, integration with procurement | **Asset lifecycle states as an explicit state machine** — requested, under construction, acquired, in use, idle, held for disposal, disposed — because an asset's financial treatment differs by state and an "in use" flag is not sufficient. Also adopted: capital budgeting linked to the asset record | Dynamics' fixed-asset budgeting module in favour of M54 owning the budget |
| **IFS Cloud / EAM-class systems** | Equipment register with maintenance, condition and financial views over the same object | **The two-view principle, implemented as two modules with one link.** The operational modules (M45, M46, M47, M17, M13) hold the working record; M49 holds the financial record; a single asset identifier joins them. Neither is subordinate to the other, and neither duplicates the other's data | A combined EAM/finance object — it forces the finance team into maintenance workflows and the maintenance team into depreciation policy |
| **IFRS/BFRS — IAS 16, IAS 36, IFRS 16** | Componentisation where components have different useful lives; impairment indicator assessment and testing; right-of-use asset recognition for leases | **Componentisation available but policy-gated** (a branch fit-out separated from its air conditioning has different lives); **impairment as an indicator-driven annual assessment** rather than an event nobody triggers; right-of-use recognition for branch leases where the framework requires it | Revaluation model as the default — cost model unless the auditor and CFO adopt otherwise |
| **Bangladesh Income Tax Act 2023, Third Schedule** | Normal depreciation on written-down value by class — building 5%, factory building 10%, furniture and office equipment 10%, plant and machinery 10%, motor vehicles 10% (20% if for hire), computer hardware 25%; initial allowance 10% on buildings and 25% on machinery on purchase cost; accelerated 50/30/20 for qualifying new industrial machinery | **A permanent, separate tax book with its own rates, its own written-down values and its own allowance tracking**, reconciled to the accounting book through a maintained difference schedule that feeds M51's income-tax computation | Attempting to run one book and adjust at year end — it produces an unauditable reconciliation within two years |
| **Odoo 19 CE `account_asset` + OCA `account-fixed-asset`** | Asset creation from vendor bills, depreciation boards, asset categories, disposal | The transactional substrate: asset objects, depreciation boards and bill-to-asset linkage | Odoo's single-book model, which cannot express a parallel tax book; extended in `cd_asset_depreciation_bd` |

**Design position.** Five deliberate positions.

First, **the register and the ledger cannot diverge, because they are the same movement**.
Every capitalisation, depreciation charge, transfer, impairment and disposal is raised by M49 as
an event and posted by M19's engine. There is no path by which a register entry exists without a
ledger consequence, or vice versa. The 100% reconciliation KPI is then a verification, not an
achievement.

Second, **assets are created from invoices, not from lists**. The capitalisation path starts at
an approved M52 invoice flagged as capital, carrying its cost, vendor, date and dimensions. A
manually created asset is possible, requires a reason and an approver, and is reported.

Third, **two books, one register, permanently**. The accounting book follows Company policy; the
tax book follows the Third Schedule. Neither is derived from the other at year end; both are
maintained continuously, and the difference schedule between them is a maintained artefact that
M51 consumes directly.

Fourth, **an asset always has a custodian**. Not a department — a named person. At 51+ branches
with equipment that moves, an asset accountable to "the branch" is accountable to nobody, and
physical verification becomes an argument rather than a count.

Fifth, **capital is approved before it is spent, and reviewed after**. A capital request carries
a business case, consumes an approved budget, and — above a threshold — is reviewed against its
case after implementation. Without the review, the approval process becomes a formality within
two cycles.

---

## 5. Functional Areas & Features

### 5.1 Capital Investment Approval

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FXA-001 | Capital request | Raise a capital expenditure request carrying purpose, asset class, estimated cost, expected life, branch or entity, business case and expected benefit | **P0** | L5 |
| FR-FXA-002 | Approval workflow | Route the request by value band, asset class and entity through an authorisation matrix, with each approval recorded and the approver distinct from the requester | **P0** | L5 |
| FR-FXA-003 | Budget consumption | Check the request against the approved capital budget held in M54, show the remaining headroom, and record every over-budget approval as an exception | **P0** | L5 |
| FR-FXA-004 | Cash consultation | Present the treasury cash position and forecast from M50 alongside the approval decision for requests above the configured value | P1 | L5 |
| FR-FXA-005 | Request to procurement | On approval, release the request to M16 as an authorised commitment, carrying the capital reference that will follow through to the asset | **P0** | L5 |
| FR-FXA-006 | Capital project | Group related requests into a capital project — a branch opening, a workshop build-out — with a total budget, a schedule and a single accountable owner | P1 | L5 |
| FR-FXA-007 | Post-implementation review | Require, for projects above a threshold, a review of actual cost and realised benefit against the business case, within a defined period of completion | P2 | L5 |

### 5.2 Asset Register, Capitalisation & CWIP

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FXA-008 | Asset register | Maintain every fixed asset with a unique identifier, class, description (English and Bengali), cost, acquisition date, in-service date, location, cost centre, entity, custodian, supplier, invoice reference, warranty expiry, serial and status | **P0** | L1/L5 |
| FR-FXA-009 | Asset classes | Define asset classes that carry default useful life, depreciation method, residual policy, GL account set and **Third Schedule tax class**, so that classification determines treatment | **P0** | L5 |
| FR-FXA-010 | Capitalisation policy | Apply a configured capitalisation threshold and policy rules to determine whether an expenditure is capitalised or expensed, and record the decision on the transaction | **P0** | L5 |
| FR-FXA-011 | Capitalisation from invoice | Create the asset from an approved M52 invoice flagged as capital, carrying cost, vendor, date, dimensions and the invoice reference, with no re-keying | **P0** | L5 |
| FR-FXA-012 | Landed cost adoption | Adopt the final landed cost published by M44 for imported assets, and adjust the asset cost where it is published after capitalisation | **P0** | L5 |
| FR-FXA-013 | Manual asset creation | Permit manual creation only with a reason code and an approver, and include it on a standing report | P1 | L5 |
| FR-FXA-014 | Componentisation | Split an asset into components with independent useful lives and depreciation, where the policy requires it | P1 | L5 |
| FR-FXA-015 | Capital work in progress | Accumulate expenditure against a CWIP asset — vendor invoices, internal labour, allocated overhead — and hold it undepreciated until it is brought into use | **P0** | L5 |
| FR-FXA-016 | CWIP settlement | Transfer accumulated CWIP to one or more active assets on commissioning, allocating cost by an approved basis, and start depreciation from the in-service date | **P0** | L5 |
| FR-FXA-017 | CWIP ageing | Report CWIP by age and project, and escalate any balance held beyond the configured period without commissioning | P1 | L5 |
| FR-FXA-018 | Stock-to-asset transfer | Convert an item from M15 inventory to a fixed asset — a rental-pool device, an internally deployed machine — at its inventory value, with the movement controlled and reported | **P0** | L5 |
| FR-FXA-019 | Asset tagging | Generate asset tags with barcode and QR, printable on the branch label printers, and support scan-based identification | **P0** | L5 |

### 5.3 Depreciation — Accounting and Tax Books

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FXA-020 | Dual-book depreciation | Maintain, over one asset register, an accounting book under Company policy and a **tax book under the Income Tax Act 2023 Third Schedule**, computed independently and reconciled continuously (BR-FIN-015, NFR-022) | **P0** | L5 |
| FR-FXA-021 | Depreciation methods | Support straight-line and reducing-balance in the accounting book, and written-down-value with initial and accelerated allowances in the tax book, per asset class | **P0** | L1/L5 |
| FR-FXA-022 | Depreciation run | Execute the periodic depreciation run per entity and per book, produce the charge by asset and dimension, and raise the accounting-book result to M19 for posting | **P0** | L1/L5 |
| FR-FXA-023 | Life and method change | Permit a change of useful life, method or residual value only with approval, applying it prospectively and recording the justification | **P0** | L5 |
| FR-FXA-024 | Depreciation suspension | Suspend depreciation on an asset that is idle or held for disposal where the policy requires, and reinstate it on return to use | P1 | L5 |
| FR-FXA-025 | Catch-up and back-dated in-service | Compute catch-up depreciation where an asset is capitalised after its in-service date, without distorting the current period's charge | P1 | L5 |
| FR-FXA-026 | Book difference schedule | Maintain the running difference between the accounting and tax books per asset and in total, as the direct input to M51's deferred tax and income-tax computation | **P0** | L5 |

### 5.4 Movement, Verification, Impairment & Disposal

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FXA-027 | Asset transfer | Transfer an asset between locations, branches, cost centres or legal entities, with approval where the entity changes, and carry cost and accumulated depreciation with it | **P0** | L5 |
| FR-FXA-028 | Custodianship | Assign a named custodian to every asset, record every custodian change with acknowledgement, and produce a custody statement per person | **P0** | L5 |
| FR-FXA-029 | Physical verification | Schedule and execute physical verification by location and class, capture results by scan on a mobile device, and report found, not-found and unregistered items | **P0** | L5 |
| FR-FXA-030 | Verification variance | Route every verification variance for investigation, and permit a register correction only with approval and a reason, never by the verifier alone | **P0** | L5 |
| FR-FXA-031 | Revaluation | Support revaluation of an asset class where the accounting policy adopts the revaluation model, with the valuation basis and valuer recorded | P2 | L5 |
| FR-FXA-032 | Impairment | Assess impairment indicators at least annually and on trigger events, test where indicated, recognise or reverse impairment with the basis recorded, and raise it to M19 | P1 | L5 |
| FR-FXA-033 | Disposal | Dispose of an asset by sale, scrap, trade-in or donation with approval, compute the gain or loss, capture proceeds through M20, and route physical disposal to M18 where required | **P0** | L5 |
| FR-FXA-034 | Loss and write-off | Write off a lost, stolen or destroyed asset with approval, an incident reference and an insurance-claim linkage where one exists | **P0** | L5 |

> **Leases and right-of-use.** Where the Company's reporting framework requires right-of-use
> recognition for branch and equipment leases, the right-of-use asset is created and depreciated
> in M49 against the lease liability held in M50 (FR-TRE-040). Whether this applies depends on
> the framework decision recorded in `M19` §18 Q-03 and is confirmed in §18 Q-05 below.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Register-to-ledger reconciliation by construction** | Every asset movement raises a financial event that M19 posts. There is no path to create, change or dispose of an asset without a corresponding ledger consequence. The reconciliation is a verification assertion, not a reconstruction |
| T-02 | **Invoice-linked capitalisation** | An asset created from an M52 invoice retains that invoice reference permanently and immutably. A full-table assertion that every asset has a source (invoice, import, stock transfer, CWIP settlement or approved manual creation) is a standing control |
| T-03 | **Two books, one register** | Accounting and tax depreciation are computed independently over the same asset record. Neither is derived from the other. The difference is a maintained value, not a year-end calculation |
| T-04 | **Depreciation determinism** | Re-running depreciation for a period over the same asset state produces identical charges in both books. Each run stores its inputs so any charge can be explained without re-derivation |
| T-05 | **Prospective-only life changes** | A useful-life, method or residual change applies from its effective period forward. Retrospective restatement of prior depreciation is not available in the application; it requires a M19 journal with its own approval |
| T-06 | **Immutable asset history** | Asset events — capitalisation, transfer, custodian change, revaluation, impairment, disposal — are insert-only. A correction is a compensating event referencing the original |
| T-07 | **Offline physical verification** | Verification runs offline on a mobile device with scan capture, synchronising through an append-only journal with server-side conflict resolution (AS-13). A branch with poor connectivity must still be verifiable |
| T-08 | **Asset identifier as the operational join key** | The M49 asset identifier is the key by which M45, M46, M47, M17 and M13 link their operational records. Neither side duplicates the other's attributes; each reads what it needs |
| T-09 | **Monetary discipline** | All amounts `Monetary` with explicit currency (AS-10). Depreciation rounding is resolved at a declared point so that accumulated depreciation never exceeds depreciable cost |
| T-10 | **Volume envelope** | Estimated **8,000–20,000 assets** across 51+ branches, workshops, vehicles, IT estate and the rental pool, generating ~200,000 depreciation lines per year across two books |
| T-11 | **Depreciation run performance** | A full monthly dual-book depreciation run across all entities completes in ≤ 15 minutes; the register-to-ledger reconciliation in ≤ 5 minutes |
| T-12 | **Event emission via outbox** | Every asset state change emits a domain event through the transactional outbox (AS-08); M19, M51, M54 and the operational asset modules consume |
| T-13 | **Multi-entity scoping** | Every asset carries `company_id` and `operating_unit_id`; an inter-entity transfer is an explicit approved transaction, never an attribute edit (AS-03) |
| T-14 | **Label generation** | Asset tags render as Code-128 and QR on branch thermal printers, with Bengali descriptions (AS-12) |
| T-15 | **Retention** | Asset records, movements, verification results and disposal evidence retained seven years after disposal, and remain queryable |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M49 |
|---|---|---|
| **CFO** | Signs a balance-sheet asset figure supported by a spreadsheet, and cannot evidence it item by item | Signs a figure that reconciles to a register, item by item, with a physical verification behind it |
| **Finance Manager** | Rebuilds the depreciation schedule annually and reconciles at year end | Reviews a monthly dual-book run; the reconciliation is already done |
| **Tax consultant** | Reconstructs Third Schedule depreciation from an incomplete asset list | Receives a maintained tax book with written-down values and allowance history |
| **Branch manager** | Has equipment on site with no record of what it is worth or who is accountable | Has a custody statement, a verification schedule, and named accountability |
| **Operations Director** | Approves a new branch fit-out without visibility of what previous ones cost | Sees the capital project history and the post-implementation reviews |
| **Corporate Services Head (rental)** | Judges rental margin without accurate depreciation | Sees rental revenue from M53 matched to asset depreciation from M49 in M54's margin |
| **Procurement** | Buys capital items with no link from the PO to the eventual asset | Carries the capital reference from request to PO to invoice to asset |
| **External auditor** | Performs a fixed-asset reconstruction as part of every audit | Tests the register-to-ledger control and reviews the verification results |
| **Internal audit** | Has no basis to test asset existence | Tests verification coverage and variance resolution |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Balance-sheet integrity** | Register reconciled to GL, 100%, with physical verification behind it | Removes an audit qualification risk on one of the largest balance-sheet lines, and supports the < 0.5% audit-adjustment target |
| **Rental business margin accuracy** | Rental-pool devices capitalised and depreciated correctly, matched to M53's recognised rental revenue | Makes **BDT 48 lac/year** rental gross margin and **BO-13**'s 55% margin target measurable rather than assumed |
| **Tax depreciation optimisation** | Third Schedule rates, initial allowances and accelerated allowances tracked per asset and claimed in full | Initial allowance of 25% on machinery and 10% on buildings is frequently under-claimed when the register is incomplete — a direct, recurring cash-tax benefit |
| **Capital discipline** | Requests approved against budget with a business case, and reviewed against outcome | Makes the branch-expansion programme's cost predictable, and stops the pattern where the cost of opening a branch is discovered afterwards |
| **Asset loss reduction** | Named custodianship and scheduled physical verification across 51+ branches | Converts an unmeasured loss channel into a measured one with accountability |
| **Insurance efficiency** | Coverage tracked against actual asset values by location | Prevents both under-insurance (a real loss) and over-insurance (a recurring premium waste) |
| **Depreciation accuracy in branch P&L** | Depreciation charged to the branch and cost centre that uses the asset | Precondition for M54's branch profitability being credible |
| **Close acceleration** | Depreciation run and reconciliation automated | Contributes to the ≤ 3-day close (KPI-050) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **A defensible asset base** | An asset register that reconciles is a precondition for bank facilities secured on assets, for insurance claims, and for any investment or valuation discussion |
| **Accountability for physical property** | Named custody at 51+ sites changes behaviour in a way that an asset list does not |
| **Statutory conformance** | Third Schedule depreciation maintained continuously rather than reconstructed, supporting the NFR-022 income-tax compliance requirement |
| **ISO 9001 alignment** | Controlled equipment records with verification evidence support the quality system that M45 depends on |
| **Insurance and claim readiness** | A loss event is evidenced by a register entry, a custodian, a verification history and a value — not by a photograph and an estimate |
| **Expansion readiness** | A new branch is a capital project against a template, with a known cost profile — supporting the 1000FiX Station programme |
| **Environmental accountability** | Financial disposal linked to M18's lawful disposal closes the loop between writing an asset off and disposing of it properly |

---

## 8. Lifecycle & State Models

### 8.1 Capital Request to Asset

```
  ┌──────────────┐   business case, budget check (M54), cash view (M50)
  │  REQUESTED   │
  └──────┬───────┘
         │ approved within the authority matrix
         ▼
  ┌──────────────┐  released to M16 with the capital reference
  │  APPROVED    │──────────────────────────────────────────┐
  └──────┬───────┘                                          │
         │ rejected / lapsed                                ▼
         ▼                                          ┌──────────────┐
  ┌──────────────┐                                  │  COMMITTED   │ (PO raised)
  │  CLOSED      │                                  └──────┬───────┘
  └──────────────┘                                         │ goods/services received,
                                                           │ M52 invoice approved as capital
                                                           ▼
                                              ┌────────────────────────┐
                                              │  CWIP                  │ (if not yet in use)
                                              │  accumulating          │
                                              └───────────┬────────────┘
                                                          │ commissioned — cost allocated
                                                          ▼
                                              ┌────────────────────────┐
                                              │  ASSET — IN SERVICE    │  depreciation starts
                                              └───────────┬────────────┘
                                                          │ post-implementation review
                                                          ▼
                                              ┌────────────────────────┐
                                              │  REVIEWED (projects    │
                                              │  above threshold)      │
                                              └────────────────────────┘
```

### 8.2 Asset Lifecycle

```
   ┌─────────────┐  from M52 invoice · M44 import · M15 stock · CWIP settlement
   │  ACQUIRED   │  (or approved manual creation)
   └──────┬──────┘
          │ in-service date reached
          ▼
   ┌─────────────┐◄──────── reinstated ────────┐
   │  IN SERVICE │                             │
   │ depreciating│                             │
   └──┬───┬───┬──┘                      ┌──────┴──────┐
      │   │   │  idle / not in use      │    IDLE     │
      │   │   └────────────────────────►│ (depreciation
      │   │                             │  per policy) │
      │   │  transferred                └─────────────┘
      │   ▼
      │ ┌─────────────┐  location · branch · cost centre · entity (approval)
      │ │ TRANSFERRED │──► returns to IN SERVICE at the new location
      │ └─────────────┘
      │
      │  impairment indicator / revaluation
      ▼
   ┌─────────────┐
   │  IMPAIRED / │──► carrying value adjusted; depreciation recalculated prospectively
   │  REVALUED   │
   └──────┬──────┘
          │ disposal decision approved
          ▼
   ┌──────────────────┐   depreciation suspended per policy
   │ HELD FOR DISPOSAL│
   └──────┬───────┬───┘
          │       │ lost · stolen · destroyed
          │       ▼
          │  ┌─────────────┐  incident + insurance claim linkage
          │  │ WRITTEN OFF │
          │  └─────────────┘
          │ sold · scrapped · traded in · donated
          ▼
   ┌─────────────┐  gain/loss computed · proceeds via M20 · physical disposal via M18
   │  DISPOSED   │
   └─────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Acquired | Capital invoice approved in M52, import landed in M44, stock converted from M15, or CWIP settled | System |
| — | CWIP | Expenditure incurred against a capital project not yet commissioned | System |
| CWIP | Acquired / In service | Commissioning confirmed; cost allocated to one or more assets on an approved basis | Finance Manager |
| Acquired | In service | In-service date reached; depreciation begins in both books | System |
| In service | Idle | Asset not in use; depreciation treatment follows policy | Custodian / Finance Manager |
| In service | Transferred | Transfer approved; entity change requires elevated approval | Branch Manager / Finance Manager |
| In service | Impaired / Revalued | Impairment indicator confirmed by test, or revaluation performed under an adopted policy | CFO |
| In service / Idle | Held for disposal | Disposal decision approved within the authority matrix | Finance Manager / CFO |
| Held for disposal | Disposed | Sale, scrap, trade-in or donation executed; gain or loss computed; proceeds recorded | Finance Manager |
| Any state | Written off | Loss, theft or destruction confirmed with an incident reference and approval | CFO |
| Disposed / Written off | — | Record retained for seven years | — |

### 8.3 Physical Verification Cycle

| State | Meaning | Exit Condition |
|---|---|---|
| Scheduled | A verification round planned for a location, class or custodian | Assigned to a verifier |
| In progress | Scan-based capture under way, offline-capable | All in-scope assets attempted |
| Submitted | Results captured: found, not found, unregistered items discovered | Variances identified |
| Variance investigation | Each variance assigned for explanation | Explained or escalated |
| Correction proposed | A register change proposed on the basis of the verification | Approved by a role other than the verifier |
| Closed | All variances explained, corrections approved and applied | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FXA-01 | Every asset in the register has a source — invoice, import, stock transfer, CWIP settlement, or an approved manual creation | **H** | CFO |
| BRU-FXA-02 | Every asset movement raises a financial event; there is no register change without a ledger consequence | **H** | CFO |
| BRU-FXA-03 | The asset register must reconcile to the M19 control account before the period may close | **H** | CFO |
| BRU-FXA-04 | A capital request cannot be approved by its requester | **H** | CFO |
| BRU-FXA-05 | A capital request exceeding the approved capital budget requires approval at the next authority level and is recorded as an exception | **A** | CFO |
| BRU-FXA-06 | Expenditure is capitalised only where it meets the configured threshold and policy; the decision is recorded on the transaction | **H** | CFO |
| BRU-FXA-07 | CWIP is not depreciated; depreciation begins on the in-service date after commissioning | **H** | CFO |
| BRU-FXA-08 | CWIP held beyond the configured period without commissioning is escalated to the CFO | **S** | Finance Manager |
| BRU-FXA-09 | Every asset has one named custodian at all times; a custodian change requires the new custodian's acknowledgement | **H** | Finance Manager |
| BRU-FXA-10 | A useful-life, method or residual-value change requires approval and applies prospectively only | **H** | CFO |
| BRU-FXA-11 | Accumulated depreciation can never exceed depreciable cost | **C** | CTO |
| BRU-FXA-12 | The accounting book and the tax book are maintained independently; neither is derived from the other at period end | **H** | CFO |
| BRU-FXA-13 | Tax depreciation uses the Third Schedule rates and classes supplied by M51; M49 holds no tax rate of its own | **H** | CFO |
| BRU-FXA-14 | An inter-entity asset transfer requires elevated approval and carries cost and accumulated depreciation | **H** | CFO |
| BRU-FXA-15 | A physical verification variance cannot be corrected in the register by the person who performed the verification | **H** | CFO |
| BRU-FXA-16 | A register correction arising from verification requires approval and a reason, and appears on a standing report | **H** | Finance Manager |
| BRU-FXA-17 | A disposal requires approval within the authority matrix; the gain or loss and the disposal proceeds are recorded | **H** | CFO |
| BRU-FXA-18 | An asset disposed of physically must be routed to M18 where e-waste or environmental rules apply | **H** | Quality Manager |
| BRU-FXA-19 | A write-off for loss, theft or destruction requires an incident reference and CFO approval | **H** | CFO |
| BRU-FXA-20 | A rental-pool asset is a fixed asset, never consumable stock, and cannot be issued to a repair job (mirrors BRU-INV-21) | **H** | Finance Manager |
| BRU-FXA-21 | A stock-to-asset conversion is a controlled, reason-coded transaction at the inventory value published by M15 | **H** | CFO |
| BRU-FXA-22 | Imported assets are not finally valued until M44 publishes the landed cost; interim value is flagged provisional (mirrors BRU-INV-15) | **H** | CFO |
| BRU-FXA-23 | Depreciation cannot be posted into a period hard-closed in M19 | **H** | CFO |
| BRU-FXA-24 | A capital project above the review threshold requires a post-implementation review within the defined period | **H** | CFO |
| BRU-FXA-25 | Insurance coverage is reviewed against register values at least annually; a coverage gap is reported to the CFO | **S** | Finance Manager |
| BRU-FXA-26 | Impairment indicators are assessed at least annually and on trigger events; the assessment is recorded whether or not impairment results | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.capex.request` | `fix_capex_request` | Capital expenditure request | reference, requester_id, entity_id, branch_id, asset_class_id, purpose, business_case_doc_id, estimated_cost, currency, expected_life, expected_benefit, budget_line_id (M54), budget_headroom_at_request, state, project_id, po_ref (M16) |
| `fix.capex.approval` | `fix_capex_approval` | Approval step | request_id, step, approver_role, approver_id, decision, decided_at, authority_band, over_budget_flag, comment |
| `fix.capital.project` | `fix_capital_project` | Grouped capital programme | name, type (branch_opening/workshop/it/fleet/other), entity_id, owner_id, total_budget, approved_at, start_date, target_completion, actual_completion, state, cwip_asset_id, review_due_at |
| `fix.capital.project.review` | `fix_capital_project_review` | Post-implementation review | project_id, actual_cost, budget_variance, benefit_assessment, reviewer_id, reviewed_at, conclusion, document_id |
| `fix.asset.class` | `fix_asset_class` | Class-driven default treatment | code, name_en, name_bn, default_useful_life, default_method, residual_policy, capitalisation_threshold, gl_asset_account_id, gl_depreciation_account_id, gl_accumulated_account_id, **third_schedule_class**, componentisation_required |
| `fix.asset` | `fix_asset` | **The fixed asset register** | asset_number, tag_number, class_id, description_en, description_bn, entity_id, operating_unit_id, branch_id, cost_center_id, business_line_id, acquisition_cost, cost_provisional, currency, acquisition_date, in_service_date, useful_life, residual_value, custodian_id, location_detail, supplier_party_id, source_type (invoice/import/stock/cwip/manual), source_ref, invoice_id (M52), serial_number, warranty_expiry, insurance_policy_ref, state, operational_module_ref, disposed_at |
| `fix.asset.component` | `fix_asset_component` | Component with its own life | parent_asset_id, description, cost_portion, useful_life, method, in_service_date, state |
| `fix.asset.book` | `fix_asset_book` | One depreciation book over an asset | asset_id, book_type (accounting/tax), method, rate_or_life, opening_cost, opening_accumulated, opening_wdv, initial_allowance_claimed, accelerated_allowance_claimed, current_accumulated, current_carrying_value, suspended_flag, last_run_period_id |
| `fix.depreciation.run` | `fix_depreciation_run` | A periodic run | entity_id, period_id, book_type, run_at, run_by, assets_processed, total_charge, inputs_hash, state, gl_batch_ref |
| `fix.depreciation.line` | `fix_depreciation_line` | Charge per asset per period per book | run_id, asset_id, book_type, period_id, opening_value, charge, closing_value, method_applied, cost_center_id, branch_id, business_line_id, gl_entry_ref |
| `fix.book.difference` | `fix_book_difference` | Accounting vs tax book gap | asset_id, period_id, accounting_accumulated, tax_accumulated, temporary_difference, movement, supplied_to_tax_at |
| `fix.asset.cwip` | `fix_asset_cwip` | Capital work in progress | project_id, entity_id, description, accumulated_cost, cost_lines_json, opened_at, age_days, expected_commission_date, state, settled_to_asset_ids, settlement_basis, settled_at |
| `fix.asset.movement` | `fix_asset_movement` | Immutable asset event | asset_id, movement_type (capitalise/transfer/custodian_change/revalue/impair/suspend/reinstate/dispose/writeoff/correct), effective_date, from_values_json, to_values_json, reason_code, requested_by, approved_by, occurred_at, gl_entry_ref, corrects_movement_id |
| `fix.asset.transfer` | `fix_asset_transfer` | Location or entity transfer | asset_id, from_entity_id, to_entity_id, from_branch_id, to_branch_id, from_cost_center_id, to_cost_center_id, cost_transferred, accumulated_transferred, approved_by, effective_date, state |
| `fix.asset.custody` | `fix_asset_custody` | Custodianship history | asset_id, custodian_id, assigned_at, assigned_by, acknowledged_at, released_at, release_reason |
| `fix.asset.verification` | `fix_asset_verification` | A verification round | scope (location/class/custodian), scope_ref, scheduled_for, verifier_id, started_at, completed_at, assets_in_scope, found, not_found, unregistered_found, state, approved_by |
| `fix.asset.verification.line` | `fix_asset_verification_line` | One verified item | verification_id, asset_id, expected_location, scanned, found_flag, found_location, condition_note, variance_type, investigation_state, correction_id |
| `fix.asset.revaluation` | `fix_asset_revaluation` | Revaluation event | asset_id, valuation_date, previous_carrying_value, revalued_amount, basis, valuer_name, valuer_report_doc_id, approved_by, gl_entry_ref |
| `fix.asset.impairment` | `fix_asset_impairment` | Impairment assessment and result | asset_id or cgu_ref, assessment_date, indicators_json, tested_flag, recoverable_amount, carrying_value, impairment_loss, reversal_amount, basis_doc_id, approved_by, gl_entry_ref |
| `fix.asset.disposal` | `fix_asset_disposal` | Disposal | asset_id, method (sale/scrap/tradein/donation), disposal_date, carrying_value_at_disposal, proceeds, proceeds_invoice_id (M20), costs_of_removal, gain_loss, buyer_party_id, approved_by, ewaste_batch_ref (M18), state |
| `fix.asset.writeoff` | `fix_asset_writeoff` | Loss, theft or destruction | asset_id, reason (lost/stolen/destroyed), incident_ref, carrying_value, insurance_policy_ref, claim_ref, claim_recovered, approved_by, gl_entry_ref |
| `fix.asset.insurance` | `fix_asset_insurance` | Coverage linkage | policy_ref, insurer_party_id, covered_asset_ids or class_scope, sum_insured, register_value, coverage_gap, period_from, period_to, last_reviewed_at |
| `fix.asset.tag` | `fix_asset_tag` | Physical tag | asset_id, tag_number, barcode_value, qr_value, printed_at, printed_by, replaced_tag_number |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.gl.account`, `fix.fiscal.period` | M19 | Read for period state and control-account reconciliation |
| `fix.ap.invoice`, `fix.ap.invoice.line` | M52 | Read as the capitalisation source; consume the capital-flagged approval event |
| `fix.purchase.order` | M16 | Read for the capital commitment carrying the capex reference |
| `fix.import.consignment`, `fix.landed.cost` | M44 | Read; adopt final landed cost |
| `fix.stock.quant`, `fix.stock.move` | M15 | Read for stock-to-asset conversion at inventory value |
| **`fix.tax.depreciation.book`, Third Schedule rates and classes** | **M51** | Read; M51 owns the rates, M49 holds the book |
| `fix.budget.line` | M54 | Read for budget consumption and headroom |
| `fix.cash.forecast`, `fix.cash.position` | M50 | Read for the cash view on large capital decisions |
| `fix.ar.invoice` | M20 | Raise the disposal proceeds invoice |
| `fix.recycling.batch`, `fix.disposal.certificate` | M18 | Link the financial disposal to lawful physical disposal |
| `fix.tool.register`, `fix.calibration.record` | M45 | Operational view of the same physical item |
| `fix.vehicle`, `fix.vehicle.service` | M46 | Operational view |
| `fix.site`, `fix.site.infrastructure` | M47 | Operational view |
| `fix.asset` | M17 | Operational view; customer devices are never M49 assets |
| `fix.rental.asset`, `fix.rental.agreement` | M13 | Operational view of the rental pool |
| `fix.employee` | M21 | Custodian identity |
| `fix.party` (supplier, insurer, buyer) | M33 | Read |
| `fix.document` | M24 | Store business cases, valuations, disposal evidence, verification reports |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FXA-01 | A capital request is submitted | Check the capital budget in M54, present the headroom and (above threshold) the M50 cash view, and route by the authority matrix | Route with a budget-unavailable warning; **never approve silently** |
| AUT-FXA-02 | A capital request is approved | Release to M16 as an authorised commitment carrying the capex reference | Manual release with an alert |
| AUT-FXA-03 | An M52 invoice is approved and flagged as capital | Create the asset or add to CWIP, carrying cost, vendor, date, dimensions and the invoice reference | Hold in a capitalisation queue with the missing attribute named |
| AUT-FXA-04 | An invoice above the capitalisation threshold is coded to an expense account | Flag it for capitalisation review before the period closes | Report only |
| AUT-FXA-05 | M44 publishes a final landed cost for an asset | Adjust the asset cost, clear the provisional flag, and recompute depreciation prospectively in both books | Hold as provisional and report on the exception list |
| AUT-FXA-06 | A capital project is commissioned | Settle CWIP to the resulting assets on the approved basis and start depreciation from the in-service date | Halt settlement and report; partial settlement is not permitted |
| AUT-FXA-07 | CWIP exceeds its ageing threshold without commissioning | Escalate to the Finance Manager and then the CFO with the project and value | Escalation is unconditional |
| AUT-FXA-08 | Period end | Execute the dual-book depreciation run, produce the charge by asset and dimension, and raise the accounting-book result to M19 | Halt, report failing assets, and block the M19 close task |
| AUT-FXA-09 | Period end | Reconcile the register to the M19 control account and publish the result to the close checklist | Report the difference and block the close |
| AUT-FXA-10 | Period end | Update the accounting-versus-tax book difference schedule and publish it to M51 | Report and block the tax computation task |
| AUT-FXA-11 | An asset is created | Generate the asset tag with barcode and QR and queue it for printing at its location | Tag queued and reported as unprinted |
| AUT-FXA-12 | An asset transfer is requested | Route for approval (elevated where the entity changes), move cost and accumulated depreciation, and notify both custodians | Transfer held pending approval |
| AUT-FXA-13 | A custodian change occurs | Request acknowledgement from the incoming custodian and escalate if unacknowledged within the configured period | Escalate to the branch manager |
| AUT-FXA-14 | An employee leaves (M21 event) | Produce their custody statement and require reassignment of every asset before the exit is completed | Block the HR exit task and escalate |
| AUT-FXA-15 | Verification schedule due | Generate verification tasks by location and class, assign verifiers, and enable offline scan capture | Escalate overdue verifications |
| AUT-FXA-16 | Verification submitted with variances | Route each variance for investigation, and require approval by a role other than the verifier for any register correction | Variance remains open and reportable |
| AUT-FXA-17 | Annually and on trigger events | Prompt the impairment indicator assessment for each class and cash-generating unit, and record the assessment whether or not impairment results | Assessment task remains open and blocks the year-end close |
| AUT-FXA-18 | A disposal is approved | Compute the gain or loss, raise the proceeds invoice through M20 where a sale, route physical disposal to M18 where required, and raise the events to M19 | Halt and report |
| AUT-FXA-19 | A write-off is approved | Record the incident reference, link any insurance claim, and raise the event to M19 | Halt and report |
| AUT-FXA-20 | Annually | Compare insurance sum insured against register values by location and class, and report any coverage gap to the CFO | Report only |
| AUT-FXA-21 | A capital project passes its review threshold date | Open the post-implementation review task and assign it to the project owner | Task escalates to the CFO |
| AUT-FXA-22 | Daily | Publish the capitalisation queue, CWIP ageing, unacknowledged custody, verification status, provisional-cost and manual-creation registers | Report with a data-availability warning |

---

## 12. Interfaces

### 12.1 Upstream — M49 Consumes

| Source | What | Mechanism |
|---|---|---|
| M52 Payables | Approved invoices flagged as capital, with cost, vendor, date and dimensions | Events + REST |
| M16 Procurement | Purchase orders carrying the capex reference | REST |
| M44 Import & Landed Cost | Final landed cost for imported assets | Events |
| M15 Inventory | Stock-to-asset conversions at inventory value (rental pool, internal deployment) | Events |
| M51 Tax & Regulatory | Third Schedule classes, rates, initial and accelerated allowance rules | REST |
| M54 Costing & FP&A | Capital budget lines and headroom | REST |
| M50 Treasury & Cash | Cash position and forecast for large capital decisions | REST |
| M19 General Ledger | Period state, asset control-account balance, posting confirmation | REST |
| M21 HR & Payroll | Employee identity for custodianship; leaver events | REST + events |
| M13 Rental & EaaS | Rental-pool allocation and return of devices | Events |
| M18 E-Waste | Confirmation of lawful physical disposal | Events |
| M45 / M46 / M47 / M17 | Operational status affecting financial state — condemned, written off, permanently removed | Events |
| M33 Party Master | Supplier, insurer and buyer identity | REST |

### 12.2 Downstream — M49 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 General Ledger | Capitalisation, depreciation, revaluation, impairment, transfer, disposal and write-off as financial events for posting | Events |
| M51 Tax & Regulatory | The tax book, written-down values, allowance history and the book-difference schedule | REST + events |
| M54 Costing & FP&A | Depreciation by cost centre, branch and business line; capital budget consumption; asset cost base | Events + extract |
| M50 Treasury & Cash | Planned and committed capital outflow as forecast input | REST |
| M20 Receivables | Disposal proceeds invoice request | Command |
| M18 E-Waste | Assets disposed of physically, for lawful disposal and certification | Events |
| M45 / M46 / M47 / M17 / M13 | Asset financial identity, value and status for their operational records | REST |
| M15 Inventory | Confirmation that a converted item has left stock and become an asset | Events |
| M25 BI / M62 Data Platform | Asset, depreciation, capital and verification facts | Warehouse extract |
| P03 Admin Portal | Full fixed-asset and capital workspace | Native |
| P11 Field Auditor & Quality App | Physical verification capture | REST |
| P06 Analytics Dashboard | Capital spend and asset base reporting | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `asset.capitalised` | asset, class, cost, source, dimensions, in-service date | M19, M54, M51, operational modules |
| `asset.cwip_opened` / `asset.cwip_settled` | project, accumulated cost, resulting assets, basis | M19, M54 |
| `asset.depreciated` | period, book, asset, charge, dimensions | M19, M54, M51 |
| `asset.cost_adjusted` | asset, old cost, new cost, source (landed cost) | M19, M54 |
| `asset.transferred` | asset, from/to entity, branch, cost centre, values | M19, M54, operational modules |
| `asset.custodian_changed` | asset, from, to, acknowledged | M21, branch manager |
| `asset.revalued` | asset, previous value, revalued amount, basis | M19, M54 |
| `asset.impaired` / `asset.impairment_reversed` | asset or CGU, loss or reversal, basis | M19, M54 |
| `asset.disposed` | asset, method, carrying value, proceeds, gain/loss | M19, M20, M18, M54 |
| `asset.written_off` | asset, reason, incident, carrying value, insurance claim | M19, M23, M54 |
| `asset.verification_completed` | scope, found, not found, unregistered, variance value | M19, M23, M25 |
| `asset.verification_variance` | asset, variance type, value, investigation state | M23, CFO, branch manager |
| `asset.register_reconciled` / `asset.register_variance` | period, register total, GL balance, difference | M19, M23 |
| `capex.requested` / `capex.approved` / `capex.rejected` | request, value, budget position, approver | M54, M16, M50 |
| `capex.over_budget_approved` | request, budget, overrun, approver | M54, CFO, M23 |
| `asset.book_difference_updated` | period, accounting vs tax accumulated, movement | M51 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-FXA-01 | Thermal label printers at branches and head office | Outbound | Asset tag printing with barcode, QR and Bengali description |
| INT-FXA-02 | Handheld scanners and mobile devices | Inbound | Physical verification capture |
| INT-FXA-03 | Insurance broker / insurer | Bidirectional | Schedule of covered assets and values; claim submission support |
| INT-FXA-04 | External valuer (where a revaluation policy is adopted) | Inbound | Valuation reports |
| INT-FXA-05 | External auditor | Outbound | Asset schedules, movements, verification evidence |
| INT-FXA-06 | Legacy fixed asset spreadsheets | Inbound, one-time | Register migration; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/capex/requests` | POST · GET | Raise and track capital requests | P03 |
| `/api/v1/capex/requests/{id}/approve` | POST | Approve within the authority matrix | P03 |
| `/api/v1/capex/projects` | GET · POST | Capital projects, budget and status | P03, P06 |
| `/api/v1/assets` | GET · POST | Asset register enquiry and (exceptional) manual creation | P03, M45, M46, M47, M13, M17 |
| `/api/v1/assets/{id}` | GET · PATCH | Asset detail; controlled attribute change | P03 |
| `/api/v1/assets/{id}/movements` | GET | Full immutable asset history | P03, auditor |
| `/api/v1/assets/{id}/transfer` | POST | Transfer between location, branch, cost centre or entity | P03 |
| `/api/v1/assets/{id}/custodian` | POST | Assign custodianship and request acknowledgement | P03, P11 |
| `/api/v1/assets/{id}/dispose` | POST | Dispose with method, proceeds and approval | P03 |
| `/api/v1/assets/{id}/writeoff` | POST | Write off with incident and approval | P03 |
| `/api/v1/assets/cwip` | GET · POST | CWIP accumulation and settlement | P03 |
| `/api/v1/assets/depreciation-runs` | POST · GET | Execute and review depreciation by book | P03 |
| `/api/v1/assets/books/{type}` | GET | Accounting or tax book values | P03, M51, auditor |
| `/api/v1/assets/book-difference` | GET | The accounting-versus-tax difference schedule | M51, P03 |
| `/api/v1/assets/verification` | POST · GET | Schedule, execute (offline-capable) and close verification | P11, P03 |
| `/api/v1/assets/reconciliation/{period}` | GET | Register-to-GL reconciliation result | P03, M19, auditor |
| `/api/v1/assets/custody/{employee}` | GET | Custody statement per person | P03, M21, P11 |
| `/api/v1/assets/insurance` | GET · POST | Coverage against register values | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R03 Chief Financial Officer | R U A | All entities; approves capital above threshold, disposals, write-offs, impairment, revaluation, life changes |
| R26 Finance Manager | C R U A | All entities; register maintenance, depreciation runs, transfers, verification approval within authority |
| R27 Finance Officer | C R U | Assigned scope; capitalisation, tagging, verification coordination — **cannot approve disposals or corrections** |
| R05 Operations Director | R A | All branches; approves branch capital within authority |
| R06 Branch Manager | R U A | Own branch; custodianship, verification participation, transfer initiation |
| R17 Inventory Manager | R | Stock-to-asset conversions and rental-pool allocations |
| R19 Procurement Officer | R | Capital commitments and their assets |
| R32 Quality Manager / ISO Coordinator | R U | Verification programme, variance register, disposal compliance with M18 |
| R30 HR Manager | R | Custody statements for leaver clearance |
| R33 IT / System Administrator | R U | Own IT asset operational records; **no financial approval rights** |
| R01 Chief Executive Officer | R A | All; approves capital above the CFO band |
| R02 Chief Technology Officer | R A | IT capital requests within authority |
| R38 External Auditor | R | Scoped read-only — register, movements, verification, reconciliation |
| All staff (custodians) | R | Own custody statement only (P03/P02) |

**Field-level restrictions.** Acquisition cost, carrying value, accumulated depreciation,
impairment and disposal proceeds are visible only to R01–R05, R26, R27 and R38, consistent with
the `05-04` §5 cost-visibility restriction. Branch managers and custodians see asset identity,
location and condition — never value. Insurance sums insured are restricted to R03, R26 and R27.

**Segregation of duties.**
- A capital request cannot be approved by its requester — hard block at any value.
- The person who performs a physical verification cannot approve the register correction arising from it (the same principle as SOD-05 for inventory).
- A user may not both propose and approve a disposal.
- A user may not both write off an asset and approve the write-off.
- R33 IT / System Administrator can maintain IT asset operational data but can never capitalise, depreciate, dispose or approve.
- The custodian of an asset cannot approve its own write-off or disposal.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Fixed asset register** | CFO, Finance Manager, auditor | On demand | Every asset with class, cost, accumulated depreciation, net book value, location, custodian and status |
| **Register-to-GL reconciliation** | CFO, Finance Manager, auditor | Monthly | Register totals against control accounts — **the 100% KPI** |
| **Asset movement schedule** | CFO, auditor | Monthly / annual | Opening, additions, disposals, transfers, revaluation, impairment, depreciation, closing — by class |
| **Depreciation by dimension** | CFO, Branch Managers, M54 | Monthly | Charge by branch, cost centre, business line and class |
| **Accounting vs tax book difference** | CFO, tax consultant, M51 | Monthly / annual | Per asset and in total, with movement — the deferred tax input |
| **CWIP ageing and status** | CFO, Operations Director, project owners | Monthly | Accumulated cost by project, age, expected commissioning, overdue balances |
| **Capital request pipeline** | CFO, CEO, Operations Director | Weekly | Requests raised, approved, rejected, committed and capitalised, with budget consumption |
| **Capital budget consumption** | CFO, CEO, M54 | Monthly | Approved capex against budget by category, entity and project |
| **Post-implementation review status** | CFO, CEO | Quarterly | Projects due for review, completed reviews, cost and benefit variance |
| **Physical verification results** | CFO, Quality Manager, Branch Managers, Internal Audit | Per round | Coverage, found, not found, unregistered items, variance value and resolution |
| **Custody statement** | Branch Managers, HR, individual custodians | On demand / on leaver | Assets accountable to each person, with acknowledgement status |
| **Unacknowledged custody register** | Finance Manager, Branch Managers | Weekly | Custodian assignments awaiting acknowledgement, by age |
| **Asset disposal and write-off register** | CFO, auditor, Internal Audit | Monthly | Every disposal and write-off with method, approver, carrying value, proceeds and gain/loss |
| **Impairment assessment log** | CFO, auditor | Annual | Indicator assessments recorded, tests performed, results |
| **Insurance coverage vs register value** | CFO, Finance Manager | Annual | Sum insured against register value by location and class, with gaps |
| **Idle and under-utilised assets** | Operations Director, CFO | Quarterly | Assets flagged idle, by value and duration — a redeployment worklist |
| **Rental pool asset performance** | Corporate Services Head, CFO, M54 | Monthly | Rental asset cost base, depreciation and net book value, paired with M53's rental revenue |
| **Manual asset creation register** | CFO, Internal Audit | Monthly | Assets created outside the invoice path, with reason and approver |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| — | **Fixed asset register reconciled to GL** | manual | 100% | **100%** |
| — | Assets created from an invoice or other system source (not manually) | n/a | 95% | **> 98%** |
| — | Physical verification coverage per year | none | 90% of asset value | **100% of asset value** |
| — | Verification variances unresolved beyond 30 days | unknown | < 5% | **Zero** |
| — | Assets with a named, acknowledged custodian | 0% | 95% | **100%** |
| — | Assets found unregistered during verification | unknown | < 3% | **< 0.5%** |
| — | Capital requests approved within the authority matrix | n/a | 100% | **100%** |
| — | Capital spend within approved budget | unmeasured | 90% | **97%** |
| — | Capital projects with a completed post-implementation review | 0% | 80% | **100%** |
| — | CWIP held beyond 180 days without commissioning | unknown | < 10% | **< 2%** |
| — | Depreciation run completed within the close window | n/a | 100% | **100%** |
| — | Tax book maintained and agreed with the tax consultant | reconstructed annually | 100% | **100%** |
| — | Third Schedule initial and accelerated allowances claimed where eligible | unknown | 90% | **100%** |
| — | Assets with a provisional cost outstanding beyond 30 days | n/a | < 5% | **< 1%** |
| — | Insurance coverage gap against register value | unknown | < 5% | **Zero** |
| — | Assets disposed with M18 lawful-disposal evidence where required | unknown | 95% | **100%** |

> **Register note.** M49 has **no KPI identifiers allocated in `06-02`** — the module did not
> exist in the v2.0 register. The **register-to-GL reconciliation metric is named in
> `_CATEGORY_OVERVIEW.md` §8** and must be registered as canonical. All sixteen metrics require
> allocation — recorded as audit action **A-02**.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `account_asset` — asset objects, depreciation boards, bill-to-asset linkage, disposal | 26% |
| L2 | OCA `account-fixed-asset` family (asset management extensions, disposal and transfer refinements) | 20% |
| L3 | Free label-printing and barcode aids | 4% |
| L5 | `cd_fixed_asset_ext`, `cd_capex_approval`, `cd_asset_depreciation_bd`, `cd_cwip` | 50% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 1 of 4 identifiers below are claimed by another module: **CD-088** also claimed by M58. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-088 | `cd_fixed_asset_ext` — register extensions (custodianship, tagging, componentisation), movements as immutable events, transfer including inter-entity, offline physical verification, impairment and revaluation, disposal and write-off, insurance linkage | Odoo module + mobile surface | **6 PW** |
| **CD-180** | `cd_capex_approval` — capital request and business case, authority matrix, budget consumption against M54, capital projects, post-implementation review | Odoo module | 4 PW |
| **CD-181** | `cd_asset_depreciation_bd` — dual-book depreciation, Third Schedule tax book with initial and accelerated allowances, book-difference schedule, prospective life changes, catch-up | Odoo module | **4 PW** |
| **CD-182** | `cd_cwip` — CWIP accumulation from multiple cost sources, ageing and escalation, allocation basis and settlement to active assets | Odoo module | 2 PW |

> **CD register reallocation.** **CD-088** (`cd_fixed_asset_ext`) was allocated to **M19** in
> `02-05` §5.2 and moves to **M49** under the v2.1 re-scope. Three new IDs, **CD-180…182**, are
> claimed from the Category G block defined in `M19` §16.2. **All CD IDs remain provisional**
> pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M49 is scheduled in **W5** (P2) but declares a dependency on 1 module(s) that land later: **M54** (W6). One of three things must be true before the W5 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W5 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M49 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W5 plan for M49 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M19 General Ledger (W3) | Every asset movement terminates in a journal entry; the control account must exist. **M19 carries asset balances as control-account totals through W3–W4** |
| M52 Payables (W3) | The capitalisation source; capital-flagged invoices must exist before assets can be created from them |
| M51 Tax & Regulatory (W4) | Third Schedule classes and rates for the tax book. **M49 holds no tax rate of its own** |
| M50 Treasury (W3) | Cash view on capital decisions; lease liability where right-of-use applies |
| M54 Costing & FP&A (W6) | Capital budget. **M54 is W6, after M49's W5** — capital budgets are held as a configured allocation in W5 and migrate to M54's budget model in W6. Recorded in §18 Q-03 |
| M16 Procurement (W3) | Capital commitments carrying the capex reference |
| M44 Import & Landed Cost (W6) | Landed cost for imported assets. Until W6, imported asset cost is provisional and adjusted manually |
| M15 Inventory (W2) | Stock-to-asset conversion for the rental pool |
| M13 Rental (W6) | Rental-pool operation. **M13 is W6, after M49** — rental assets are capitalised in W5 and linked to M13's operational records in W6 |
| M45 / M46 / M47 (W5–W6) | Operational asset views join on the M49 asset identifier |
| M21 HR & Payroll (W5) | Custodian identity and leaver clearance |
| M18 E-Waste (W8) | Lawful disposal linkage; until W8 disposal evidence is captured as a document |

**Delivers into:** M19 (asset postings), M51 (tax book and difference schedule), M54
(depreciation by dimension and capital consumption), M13/M45/M46/M47/M17 (financial identity of
the items they operate).

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Legacy fixed asset spreadsheets | Estimated 8,000–20,000 assets | `fix.asset`, `fix.asset.book` | W5 cutover |
| Opening cost and accumulated depreciation (accounting book) | Per asset | `fix.asset.book` (accounting) | **W5 cutover — must reconcile to M19** |
| Opening written-down values and allowance history (tax book) | Per asset | `fix.asset.book` (tax) | **W5 cutover — agreed with the tax consultant** |
| Asset classes, useful lives and methods | Full class set | `fix.asset.class` | W5 minus 2 months |
| Open CWIP balances | Current projects | `fix.asset.cwip` | W5 cutover |
| Custodian assignments | Per asset | `fix.asset.custody` | W5 cutover |
| Insurance policies and covered values | Current policies | `fix.asset.insurance` | W5 cutover |
| Rental-pool devices held in M15 | Per device | `fix.asset` via stock-to-asset conversion | W5–W6 |
| Historical disposals | 2 years, reference only | Warehouse (M62) | W5, best-effort |

> **Migration position — non-negotiable.** The opening register is established by a **full
> physical verification at cutover**, not by loading the spreadsheets. This mirrors the position
> taken for inventory in `M15` §16.4 and for cash in `M50` §16.4, and for the same reason: a
> register that starts wrong can never reach 100% reconciliation, because every subsequent
> variance is contaminated by an unknown opening error. Assets found during verification that are
> not on the legacy list are registered at a **CFO- and auditor-approved deemed cost**; assets on
> the list that cannot be found are written off before cutover with approval, not carried
> forward as an unexplained balance. The **tax book opening written-down values are agreed with
> the tax consultant** and must tie to the last filed income-tax return.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The asset register reconciles to the M19 control account, with zero unexplained difference, every period | Three consecutive monthly closes signed by the CFO |
| AC-02 | Every asset in production has a recorded source — invoice, import, stock transfer, CWIP settlement or approved manual creation | Full-table assertion query |
| AC-03 | An asset created from an M52 invoice retains the invoice reference immutably | Full-table assertion |
| AC-04 | No register change is possible without a corresponding financial event reaching M19 | Negative test on UI, API and import paths |
| AC-05 | The accounting book and the tax book are computed independently and both reconcile to their own opening positions | Dual-book run reviewed by the CFO and the tax consultant |
| AC-06 | The tax book applies Third Schedule rates supplied by M51; no tax rate exists in M49 | Code review plus configuration audit |
| AC-07 | Initial and accelerated allowances are tracked per asset and claimed where eligible | Tax book review by the tax consultant |
| AC-08 | The book-difference schedule is produced every period and consumed by M51's deferred tax computation | Three consecutive periods verified end to end |
| AC-09 | Re-running depreciation for a period over the same asset state produces identical charges in both books | Determinism test |
| AC-10 | Accumulated depreciation never exceeds depreciable cost for any asset | Full-table assertion |
| AC-11 | A life, method or residual change applies prospectively only | Negative test on retrospective application |
| AC-12 | CWIP is not depreciated, and depreciation starts on the in-service date after commissioning | Scripted scenario |
| AC-13 | A capital request cannot be approved by its requester | SoD negative test |
| AC-14 | A capital request exceeding budget requires next-level approval and is recorded as an exception | Scripted scenario |
| AC-15 | Every asset has one named custodian, and a custodian change requires acknowledgement | Full-table assertion plus a scripted scenario |
| AC-16 | An employee cannot complete HR exit clearance while assets remain in their custody | Scripted scenario with M21 |
| AC-17 | Physical verification runs offline for a full location and synchronises without loss or duplication | Offline test at three branches |
| AC-18 | The person who performs a verification cannot approve the register correction arising from it | SoD negative test |
| AC-19 | Physical verification covers 100% of asset value annually | Twelve months of verification records |
| AC-20 | A disposal computes the gain or loss, records proceeds through M20, and routes to M18 where required | Scripted scenario per disposal method |
| AC-21 | A write-off requires an incident reference and CFO approval | Negative test |
| AC-22 | Impairment indicators are assessed annually and the assessment recorded whether or not impairment results | Annual assessment log |
| AC-23 | The full monthly dual-book depreciation run completes in ≤ 15 minutes at projected volume | Performance test |
| AC-24 | Depreciation cannot be posted into a hard-closed M19 period | Negative test |
| AC-25 | The opening register is established by full physical verification, with unfound assets written off and found-unlisted assets registered at approved deemed cost | Signed verification and approval records |
| AC-26 | Opening tax book written-down values tie to the last filed income-tax return | Tax consultant sign-off |
| AC-27 | Asset tags print with barcode, QR and Bengali description on branch printers | Print test at three branches (AS-12) |
| AC-28 | CFO, Finance Manager and the external auditor sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 28 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the capitalisation threshold, and does it differ by asset class? Set too low it creates a register nobody can verify; too high it understates the asset base | CFO / external auditor | W5 design |
| Q-02 | What is the capital approval authority matrix by value band, asset class and entity? | CFO / CEO | W5 build |
| Q-03 | **M54 (capital budget) is W6 but M49 is W5.** Is a configured capital allocation acceptable in W5, migrating to M54's budget model in W6? | CFO / Programme Director | W5 design |
| Q-04 | What asset classes, useful lives and depreciation methods apply, and are they agreed with the external auditor? | CFO / external auditor | **W5 minus 2 months — blocking** |
| Q-05 | Does the reporting framework require right-of-use recognition for branch and equipment leases? This follows the framework decision in `M19` §18 Q-03 | CFO / external auditor | W5 design |
| Q-06 | Is the cost model or the revaluation model adopted, and for which classes? FR-FXA-031 is P2 and can be dropped entirely if the cost model applies throughout | CFO / external auditor | W5 design |
| Q-07 | Is componentisation required for branch fit-outs, and at what level of granularity? | CFO / external auditor | W5 design |
| Q-08 | **Is a full physical verification at cutover approved as a business commitment**, including the branch effort it requires? Without it, the 100% reconciliation KPI is not achievable | CFO / Operations Director / CEO | **W5 minus 3 months — blocking** |
| Q-09 | How complete are the legacy fixed-asset records, and can opening tax written-down values be tied to the last filed return? | CFO / tax consultant | **W5 minus 3 months — determines migration feasibility** |
| Q-10 | What is the physical verification frequency by asset class and value band? | CFO / Quality Manager | W5 build |
| Q-11 | Who is the custodian for shared branch assets — furniture, air conditioning, fit-out — where no individual uses them? A branch-manager default is proposed | CFO / Operations Director | W5 design |
| Q-12 | What is the disposal authority matrix, and is disposal by sale to employees permitted (and if so, under what controls)? | CFO | W5 build |
| Q-13 | Which assets are insured, under what policies, and who maintains the coverage schedule? | CFO / Finance Manager | W5 design |
| Q-14 | Are rental-pool devices capitalised individually or as a pool? Individual capitalisation is required for BO-13's margin measurement but increases register volume materially | CFO / Corporate Services Head | W5 design (with M13 in W6) |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2 (module definition), §4 (money flow — depreciation to the GL),
§5 (boundary map — M49 vs M17/M45/M46, rental-pool capitalisation with M13), §8 (KPI — register
reconciled to GL 100%), §9 (W5, "capital under control") ·
`M19_Financial_Accounting_and_General_Ledger.md` (posting engine, control accounts, period
close gate, Category G CD block, framework decision Q-03) ·
`M51_Tax_and_Regulatory_Compliance_Bangladesh.md` (Third Schedule rates and classes, tax
depreciation, deferred tax) ·
`M52_Accounts_Payable_and_Employee_Expense.md` (capital-flagged invoices as the capitalisation
source) · `M50_Treasury_Cash_and_Banking.md` (cash view on capital, lease liability) ·
`M53_Revenue_Recognition_Commission_and_Settlement.md` (rental revenue paired with rental asset
depreciation) · `M54_Cost_Accounting_Budgeting_and_FPA.md` (capital budget, depreciation by
dimension) · `M20_Accounts_Receivable_Invoicing_and_Collections.md` (disposal proceeds invoice) ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md` §3.2,
§8.2 (rental-pool ownership transfer, BRU-INV-15, BRU-INV-21) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md` ·
`03_Modules/F_Asset_Equipment_and_Facilities/M46_Fleet_and_Vehicle_Management.md` ·
`03_Modules/F_Asset_Equipment_and_Facilities/M47_Facility_Branch_Infrastructure_and_Workplace.md` ·
`03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md` ·
`03_Modules/D_Circular_and_Asset_Based_Business/M18_EWaste_Recycling_and_Circular_Economy.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category G, §7 ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5, §6 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` BO-13

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FIN-015, NFR-022,
§Data Retention · `1000FiX_Services_Company_Profile.md` §Service Infrastructure (51+ centres),
§Growth Initiatives (1000FiX Station network expansion), §Value-Added Services (Laptop Rental)

**External benchmark and accounting framework**
[SAP S/4HANA Asset Accounting in the Universal Journal](https://sapinsider.org/articles/mastering-acdoca-7-essential-universal-journal-insights-for-sap-s-4hana-consultants-2025-edition/) —
asset accounting permanently reconciled with the GL, parallel depreciation areas mapped to
accounting principles, assets under construction with settlement to a final asset ·
[Oracle Fusion Cloud Assets](https://www.oracle.com/erp/financial-management/) — mass additions
from Payables, category-driven depreciation defaults, corporate and tax books, physical
inventory reconciliation ·
[Microsoft Dynamics 365 Finance — Fixed Assets](https://www.randgroup.com/insights/microsoft/dynamics-365/finance-operations/financial-management-in-microsoft-dynamics-365-finance-operations/) —
asset books with independent depreciation profiles, lifecycle states, mass disposal ·
[Bangladesh Income Tax Act 2023, Third Schedule — depreciation rates by class (building 5%, factory building 10%, furniture and office equipment 10%, plant and machinery 10%, motor vehicles 10% / 20% for hire, computer hardware 25%), initial allowance (10% buildings, 25% machinery) and accelerated depreciation (50/30/20)](https://www.taxvatpoint.com/income-tax-act-2023-3rd-schedule-part-1/) —
the basis of the tax book · IAS 16 (componentisation, cost and revaluation models), IAS 36
(impairment indicators and testing), IFRS 16 (right-of-use recognition) as adopted in Bangladesh ·
Odoo 19 `account_asset` and OCA `account-fixed-asset`

---

*Module M49 · Category G · 1000FiX ERP System v2.0 · CONFIDENTIAL*
