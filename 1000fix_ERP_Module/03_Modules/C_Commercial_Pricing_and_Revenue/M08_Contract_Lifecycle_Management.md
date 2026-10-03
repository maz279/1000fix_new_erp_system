---
id: FIX-ERP2-M08
module_id: M08
module_code: CTR
module_name: Contract Lifecycle Management
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P1
wave: W4
---

# M08 — Contract Lifecycle Management
### Category C · Code `CTR` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M08 |
| **Module code** | `CTR` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | Existing (re-scoped — recurring billing mechanics moved to M39; contract product templates moved to M37) |
| **Priority** | **P1** |
| **Delivery wave** | W4 (Months 14–18) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `contract` concepts, `mail`) + L2 (OCA `contract`, `agreement`, `agreement_legal`) + L5 (custom) |
| **Custom modules** | `cd_contract_engine`, `cd_entitlement`, `cd_contract_sla`, `cd_contract_renewal`, `cd_contract_profitability` |
| **Requirement range** | FR-CTR-001 … FR-CTR-062 |
| **Requirement count** | **62** *(measured; register estimate 44)* |
| **Effort estimate** | **32 person-weeks** *(measured; register estimate 24 PW)* |
| **Depends on** | M37 Catalogue · M11 Pricing · M36 Quotation · M33 Party Master · M17 Asset Registry · M24 Document · M29 Identity · M28 Integration |
| **Depended on by** | M01, M02, M05, M09, M39, M20, M53, M04, M13, M03, M23, M25, M26, M40, M54, M22, M48, M67 |

---

## 2. Purpose

M08 owns **the agreement**: what 1000FiX has promised, to whom, for which assets, at what
service level, on what terms, until when — and what remains of that promise at any moment.

It is a contract **engine**, not an AMC table. The category overview lists fourteen contract
product families, from a six-package residential AMC to a healthcare-equipment agreement with
mandatory calibration, to a marketplace seller agreement, to a brand-partner authorisation. All
fourteen must be modelled from templates and configuration, without code change, because the
business plan adds new families faster than a release cycle can absorb them.

M08 answers "what did we promise?". It does **not** answer "what do we bill?" — that is M39 —
and it does not answer "did the money arrive?" — that is M20. The separation is deliberate and
is one of the three boundaries the category overview declares must not blur.

### Why It Exists

AMC and RAMC contracts are tracked today in spreadsheets. Nobody can state the total contract
base with confidence. Renewal is remembered, or it is not: the renewal rate is roughly **60%**,
and the business plan targets **88%**. Entitlement — how many visits remain, whether this device
is covered, whether this fault is in scope — is settled by argument at the counter, because
there is no authoritative record. Contract profitability is unknown, so loss-making contracts
renew year after year.

The business case attributes **BDT 72 lac/year** to AMC/RAMC renewal uplift and targets a
**2.5× contract base growth**. Both depend on a system that knows what exists, what is covered,
what has been consumed, what it costs to serve and when it expires.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.8 (BR-CTR-001…022) | Contract creation, coverage, entitlement, SLA, amendment, renewal, escalation |
| ERP BRD §10.1 BRU-SRM-03 | An AMC order requires the device to appear on an active contract's covered-asset list |
| ERP URD §8 (US-CTR-*) | Account manager and corporate client contract stories |
| `05-04` §7 Approval Authority Matrix | Standard terms — Sales Manager; non-standard terms — CCO + CFO |
| Business Plan §RAMC Packages | Six residential AMC packages |
| Business Plan §Corporate AMC, §IT Infrastructure AMC, §Healthcare AMC, §Specialty AMC | Four further AMC families with distinct scopes and compliance obligations |
| Business Plan §Managed Services | Six MSP tiers requiring contractual SLA and service credits |
| Business Plan §Mobile & Appliance Service | Five service products sold as agreements |
| Business Plan §Rental | Master hire agreements with call-off |
| Service App SOW §Marketplace | Seller agreements with terms, commission and standards |
| Company Profile §Brand Partnerships | 17+ brand partner authorisation agreements |
| `_CATEGORY_OVERVIEW.md` §4.2, §6, §10 | The contract/subscription boundary, the fourteen families, and the "engine cannot model a new family" risk |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The contract object and its lifecycle across all fourteen product families |
| 2 | Template-driven contract creation from M37 contract product templates |
| 3 | Parties, signatories, roles, authorised requesters and approval delegates |
| 4 | Covered scope: assets, sites, departments, service categories, geographies, exclusions |
| 5 | Asset attachment and detachment during the term, with proration triggers to M39 |
| 6 | **Entitlement definition** — visits, hours, incidents, parts value, response commitments, inclusions and caps |
| 7 | **Entitlement consumption and balance** — the authoritative running record of what remains |
| 8 | Entitlement carry-over, expiry, reset cycles and top-up |
| 9 | Contractual SLA definition, precedence over standard SLA, measurement window and calculation basis |
| 10 | Service credits and penalties on SLA breach, and their approval and issue |
| 11 | Preventive maintenance schedules generated from the contract, including calibration obligations |
| 12 | Contract terms, clauses, obligations and their tracking to completion |
| 13 | Amendment, variation and change-order handling with full version history |
| 14 | Suspension, reinstatement, novation, assignment and early termination |
| 15 | Renewal: eligibility, lead-time triggers, escalation, renewal quotation request, auto-renewal governance |
| 16 | Non-renewal, churn recording and win-back candidacy |
| 17 | Contract pricing linkage: the negotiated rate set held in M11 and bound to this contract |
| 18 | Contract profitability: revenue, cost-to-serve, margin, and negative-margin detection |
| 19 | Contract documents, signature capture, retention and legal hold |
| 20 | Obligation and compliance calendar: certificates, insurance, calibration, audit rights, reporting commitments |
| 21 | Corporate hierarchy: master agreement with subsidiary contracts, framework agreements with call-off |
| 22 | Contract-driven work generation into M01 and M05 |
| 23 | The contract API, entitlement-check API and domain events consumed across the estate |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Billing schedule, invoice generation, proration arithmetic, MRR/ARR | **M39** Subscription | M08 defines entitlement; M39 turns it into money owed |
| Invoice posting, receivable, dunning, collection | **M20** Receivable | Only Category G creates financial documents |
| Revenue recognition schedules and postings | **M53** Revenue & Settlement | M08 classifies the obligation; M53 accounts for it |
| The contract product template itself | **M37** Catalogue | A template is a catalogue definition; a contract is an instance |
| Price and rate values | **M11** Pricing | The negotiated rate set lives in M11, bound to this contract |
| The proposal that preceded signature | **M36** Quotation | M36 owns the offer; M08 owns the agreement it became |
| Warranty and protection-plan entitlement | **M09** Warranty | A warranty is a different entitlement instrument with brand recovery attached |
| Service order execution and SLA clock running | **M01** SRM | M08 defines the contractual SLA; M01 measures it on the order |
| Managed-service monitoring, alerting and tickets | **M05** Remote & Managed Services | M08 defines the MSP commitment; M05 delivers it |
| Rental asset custody, condition and utilisation | **M13** Rental | M08 holds the master hire agreement; M13 runs the hire |
| Marketplace seller performance and payouts | **M12** / **M53** | M08 holds the seller agreement; M12 governs conduct |
| Supplier and procurement contracts | **M16** / **M42** | Buy-side agreements are a procurement domain |
| Employment contracts | **M21** Core HR | People agreements are an HR domain |
| Document storage, e-signature infrastructure, retention engine | **M24** Document | M08 uses the service |
| Legal clause authoring and negotiation redlining | **M24** + external counsel | Out of ERP scope; M08 records the agreed outcome |

### 3.3 Shared Concepts

| Concept | M08's Role | Owning Module |
|---|---|---|
| Contract | **Owner** | M08 |
| Entitlement definition and balance | **Owner** | M08 |
| Contractual SLA | **Owner** of the definition; M01 measures | M08 |
| Service credit | **Owner** of the calculation and approval; M20 issues the credit note | M08 |
| Contract product template | Consumes; binds to a template version | M37 |
| Negotiated rate set | Referenced; held by M11 | M11 |
| Billing schedule and MRR | Supplies the basis; M39 owns the mechanics | M39 |
| Covered asset | References the asset; owns the coverage relationship | M17 (asset) / M08 (coverage) |
| Preventive schedule | **Owner** of the obligation; M01 executes the generated orders | M08 |
| Renewal quotation | Requests; M36 owns the document | M36 |
| Contract document and signature | References; M24 stores | M24 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA Service** — Service Contract (transaction type SC), contract items, billing plans, response profiles, entitlement determination | Contract header/item with covered objects, response profiles driving SLA, and entitlement determination at service-order creation | **Entitlement determination at intake** as a hard gate, **response profiles** as the contractual SLA carrier, and the header/item structure that lets one contract cover many asset classes | SAP billing plans — M39 owns billing; and SAP's CRM-era contract determination complexity |
| **SAP Condition Contract Management** | Negotiated commercial conditions bound to an agreement | The **rate set bound to a contract** pattern (implemented in M11, referenced here) | Rebate settlement machinery — M53 |
| **Oracle Fusion — Enterprise Contracts / Service Contracts** | Contract templates, clause libraries, contract expert, coverage and entitlement, renewal management | **Template + clause library governance**, **coverage/entitlement modelling**, and **renewal management as a scheduled, owned process** rather than a reminder | Oracle's full contract-authoring and negotiation workspace; redlining stays outside the ERP |
| **Microsoft Dynamics 365 Field Service** — Agreements, agreement booking setups, entitlements | Agreements that automatically generate recurring bookings and work orders on a schedule | **Contract-driven automatic work generation** — the mechanism behind preventive maintenance and calibration visits | Dataverse-specific booking-setup modelling |
| **IFS Cloud — Contract Management, Service Agreements** | Service agreements with entitlement, price agreements, SLA and profitability by agreement | **Contract profitability as a native, standing measure**, not a report someone builds later | IFS's project-contract depth |
| **Icertis / Sirion / Ironclad-class CLM** | Obligation management, clause libraries, risk scoring, renewal intelligence, post-signature compliance tracking | **Obligation tracking as first-class post-signature work** — certificates, calibration, insurance, reporting commitments — which is exactly where AMC contracts fail audits | Enterprise CLM licence cost and the AI-authoring layer; obligations here are a structured checklist, not an NLP extraction problem |
| **ServiceNow CSM** — entitlement and service-contract checks | Real-time entitlement verification driving case handling | The **sub-200 ms entitlement check** as an operational requirement, because it runs on every intake at 51+ branches | ServiceNow's platform coupling |
| **Odoo 19 + OCA** — `contract`, `agreement`, `agreement_legal`, `contract_variable_quantity` | Recurring agreement records, agreement types, clause sections | The `agreement` model as the L2 base for parties, terms and documents | OCA `contract`'s recurring-invoicing engine — that responsibility belongs to M39, and mixing them is exactly the boundary blur the category overview forbids |

**Design position.** 1000FiX differs from the benchmarks in five ways.

First, **one engine, fourteen families**. The acceptance test for M08 is not that AMC works; it
is that all fourteen families instantiate from templates without code change, verified before
the Wave 4 gate. The category risk register rates a failure here as High — a blocked business
line.

Second, **entitlement is a balance, not a flag**. Enterprise systems often model coverage as
boolean. Our RAMC packages sell a specific number of visits; MSP tiers sell incident volumes;
corporate agreements cap parts value. Every one of those is a decrementing balance that must be
checked at intake, decremented on consumption, restored on cancellation, and shown to the
customer in the portal. Disputes about "how many visits do I have left" are a top-three
counter argument today.

Third, **the contractual SLA overrides the standard SLA and carries money**. A breached
commitment produces a service credit that must be computed, approved and issued. Most mid-market
service businesses write SLAs they cannot measure; the category KPI set makes measurement
non-optional.

Fourth, **contract profitability is computed continuously, not annually**. Cost-to-serve
accumulates from M01 job costs, M02 labour, M15 parts and M03 logistics, against contract
revenue from M39. Contracts with negative margin are surfaced while they can still be re-priced
at renewal — the target is **< 3% of contracts with negative margin**.

Fifth, **renewal is an owned process with a lead-time clock, not a reminder**. The 60% → 88%
renewal-rate target is unreachable through diligence alone. M08 generates the renewal
quotation, escalates non-response, and records churn reasons for win-back.

---

## 5. Functional Areas & Features

### 5.1 Contract Creation & Structure

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-001 | Template-driven creation | Create a contract from any of the fourteen M37 contract product templates, inheriting scope, entitlement structure, schedule and SLA, with the template version permanently bound | P0 | L5 |
| FR-CTR-002 | Creation from an accepted proposal | Create a contract automatically from an accepted M36 proposal, carrying scope, term, pricing and signatory detail | P0 | L5 |
| FR-CTR-003 | Contract numbering | Issue a unique, gapless contract number incorporating family, entity and year | P0 | L1 |
| FR-CTR-004 | Parties and signatories | Record all parties, legal entities, signatories, authorised requesters, approvers and notice addresses, with role-scoped portal access | P0 | L5 |
| FR-CTR-005 | Term and dates | Hold effective date, expiry, notice period, cooling-off, auto-renewal flag, minimum commitment and any evergreen behaviour | P0 | L5 |
| FR-CTR-006 | Master and subsidiary contracts | Model a master agreement with subsidiary contracts per site, entity or department, and roll entitlements and reporting up or down as configured | P1 | L5 |
| FR-CTR-007 | Framework agreements with call-off | Model a framework with agreed rates and no committed volume, against which individual call-offs are raised | P1 | L5 |
| FR-CTR-008 | Contract families | Support all fourteen families — RAMC, Commercial AMC, IT Infrastructure AMC, Healthcare AMC, Specialty AMC, Managed Services, Mobile & Appliance Service, Extended Warranty service agreements, Rental master, Marketplace seller, Brand partner, Alliance/referral, Franchise, Corporate framework — from configuration alone | P0 | L5 |
| FR-CTR-009 | Multi-currency and multi-entity | Hold the contract in its own currency and legal entity, with correct treatment when M65 introduces further entities | P2 | L5 |
| FR-CTR-010 | Contract documents | Attach the executed agreement, annexes, schedules and correspondence through M24, with version control and retention | P0 | L2 |
| FR-CTR-011 | Signature capture | Capture wet or electronic signature, record the signing method and date, and seal the executed version | P0 | L5 |
| FR-CTR-012 | Non-standard terms approval | Route any deviation from standard terms to CCO and CFO approval before activation | P0 | L5 |

### 5.2 Coverage & Entitlement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-013 | Covered asset register | Maintain the list of covered assets, resolved against M17, with cover start and end dates per asset | P0 | L5 |
| FR-CTR-014 | Coverage by category and site | Express coverage by asset category, site, department or location rather than by enumerated asset, where the customer's estate is fluid | P1 | L5 |
| FR-CTR-015 | Asset attach and detach | Attach or detach assets mid-term with effective dates, automatically signalling M39 for proration | P1 | L5 |
| FR-CTR-016 | Coverage exclusions | Record explicit exclusions — fault types, causes, consumables, accidental damage, unauthorised repair — that override inclusion | P0 | L5 |
| FR-CTR-017 | Entitlement definition | Define entitlements of any type: preventive visits, corrective visits, labour hours, incident count, parts value cap, response commitment, remote hours, storage volume, device count | P0 | L5 |
| FR-CTR-018 | Entitlement period and reset | Define the entitlement period (contract term, annual, quarterly, monthly) and whether balances reset, carry over, or expire | P0 | L5 |
| FR-CTR-019 | Real-time entitlement check | Answer "is this asset and this work covered, and what remains?" in under 200 ms, at intake, in the portal and over API | P0 | L5 |
| FR-CTR-020 | Entitlement consumption | Decrement the balance when covered work is consumed, restore it on cancellation or rework, and record every movement with its source document | P0 | L5 |
| FR-CTR-021 | Entitlement exhaustion handling | On exhaustion, declare the treatment — chargeable at contract rates, chargeable at standard rates, blocked pending approval, or top-up offered | P0 | L5 |
| FR-CTR-022 | Entitlement top-up | Sell additional entitlement mid-term through M36, applying it to the balance on acceptance | P1 | L5 |
| FR-CTR-023 | Fair-use and abuse control | Detect consumption patterns breaching declared fair-use limits and raise a commercial review | P2 | L5 |
| FR-CTR-024 | Customer-visible entitlement | Present the entitlement balance, consumption history and covered-asset list in P01 and P04 | P0 | L5 |

### 5.3 Service Levels, Obligations & Preventive Work

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-025 | Contractual SLA definition | Define response, on-site, restoration, resolution and availability commitments per priority, asset class, site and working calendar | P0 | L5 |
| FR-CTR-026 | SLA precedence | Ensure the contractual SLA overrides the standard M01 SLA whenever an order is contract-covered | P0 | L5 |
| FR-CTR-027 | SLA measurement basis | Declare the measurement window, exclusions, permitted holds and the calculation method, so attainment is computed identically for both parties | P0 | L5 |
| FR-CTR-028 | Service credit scheme | Define credits or penalties on breach — by breach type, severity, cumulative frequency and cap — and compute them automatically | P1 | L5 |
| FR-CTR-029 | Service credit approval and issue | Route computed credits for approval and instruct M20 to issue the credit note, never issuing it directly | P1 | L5 |
| FR-CTR-030 | Availability and uptime commitments | Compute uptime against agreed measurement rules for MSP and rental agreements | P2 | L5 |
| FR-CTR-031 | Preventive maintenance schedule | Generate the preventive visit calendar from the contract, at the correct lead time, honouring site access windows and seasonality | P0 | L5 |
| FR-CTR-032 | Calibration and statutory obligations | Model mandatory calibration, inspection and certification obligations for healthcare and specialty agreements, with evidence capture and expiry alerting | P1 | L5 |
| FR-CTR-033 | Obligation register | Track every post-signature obligation on both sides — certificates, insurance, reports, reviews, audits, notice deadlines — with owner, due date and completion evidence | P1 | L5 |
| FR-CTR-034 | Service review scheduling | Schedule contractual service reviews, assemble the review pack from M25, and record outcomes and actions | P2 | L5 |
| FR-CTR-035 | Contract-driven work generation | Create service orders in M01 and tickets in M05 from schedules and obligations, at the right lead time, with contract context attached | P0 | L5 |

### 5.4 Change, Suspension & Termination

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-036 | Amendment | Amend scope, assets, entitlements, SLA, term or price through a governed change process producing a new contract version | P0 | L5 |
| FR-CTR-037 | Amendment approval | Apply the approval authority matrix to amendments by value and by whether terms remain standard | P0 | L5 |
| FR-CTR-038 | Version history and comparison | Retain every version immutably and present a readable comparison between any two | P1 | L5 |
| FR-CTR-039 | Suspension | Suspend a contract for non-payment, customer request or dispute, blocking entitlement consumption and signalling M39 to halt billing | P1 | L5 |
| FR-CTR-040 | Reinstatement | Reinstate a suspended contract with a declared treatment of the suspended period — entitlement restored, forfeited or prorated | P1 | L5 |
| FR-CTR-041 | Early termination | Terminate with notice-period validation, early-termination charge calculation, entitlement settlement and asset-return obligations | P1 | L5 |
| FR-CTR-042 | Novation and assignment | Transfer a contract to a different legal entity or owner, preserving history and entitlement | P2 | L5 |
| FR-CTR-043 | Dispute flag and legal hold | Flag a contract in dispute, apply legal hold to its documents, and suppress automated renewal and escalation | P1 | L5 |
| FR-CTR-044 | Contract cancellation before commencement | Cancel a signed but not-yet-effective contract with reason, unwinding downstream objects | P2 | L5 |

### 5.5 Renewal, Churn & Growth

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-045 | Renewal eligibility and lead time | Compute renewal eligibility and trigger the renewal process at the contract's configured lead time, defaulting by family | P0 | L5 |
| FR-CTR-046 | Renewal quotation request | Request a renewal quotation from M36 carrying prior-term consumption, incident history, profitability and proposed escalation | P0 | L5 |
| FR-CTR-047 | Price escalation | Apply contractual escalation — fixed percentage, index-linked or negotiated — to renewal proposals, with the basis shown | P1 | L5 |
| FR-CTR-048 | Auto-renewal governance | Support auto-renewal only where contractually permitted, with mandatory advance customer notice and an opt-out window | P1 | L5 |
| FR-CTR-049 | Renewal escalation ladder | Escalate an unanswered renewal to the account manager, then the sales manager, then the CCO, on a defined schedule | P1 | L5 |
| FR-CTR-050 | Non-renewal and churn record | Record non-renewal with a structured reason, competitor where known, and win-back candidacy | P1 | L5 |
| FR-CTR-051 | Win-back campaign feed | Feed churned contracts to M35 for win-back campaigns at a configured interval | P2 | L5 |
| FR-CTR-052 | Upsell and cross-sell signals | Surface entitlement exhaustion, out-of-scope demand and asset growth as upsell opportunities to M07 | P2 | L5 |
| FR-CTR-053 | Renewal forecast | Forecast renewal revenue and probability by family, segment and account, using historical renewal behaviour | P2 | L5 |

### 5.6 Profitability, Reporting & Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-CTR-054 | Cost-to-serve accumulation | Accumulate all delivery cost against the contract — labour, parts, logistics, sub-contract, remote, overhead allocation — from M01, M02, M03, M05 and M15 | P0 | L5 |
| FR-CTR-055 | Contract profitability | Compute revenue, cost-to-serve and margin per contract, per site and per asset class, continuously | P0 | L5 |
| FR-CTR-056 | Negative-margin detection | Detect and escalate contracts trending to negative margin, with sufficient lead time to act at renewal | P0 | L5 |
| FR-CTR-057 | Contract base reporting | Report the total contract base by family, segment, branch, value and expiry profile | P0 | L5 |
| FR-CTR-058 | Concentration and exposure | Report revenue concentration by customer and family, and the aggregate SLA credit exposure | P2 | L5 |
| FR-CTR-059 | Contract compliance dashboard | Report obligation completion, certificate currency, calibration status and audit readiness per contract | P1 | L5 |
| FR-CTR-060 | Entitlement utilisation analysis | Report entitlement consumption against sold entitlement, identifying both under-use (churn risk) and over-use (margin risk) | P1 | L5 |
| FR-CTR-061 | Contract data export for audit | Produce a complete, evidenced contract file — agreement, amendments, obligations, SLA attainment, entitlement ledger — for any contract on demand | P1 | L5 |
| FR-CTR-062 | Bulk contract operations | Perform bulk renewal, bulk escalation and bulk amendment across a filtered contract set with preview, approval and rollback | P2 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Entitlement ledger, not a counter** | Entitlement balance is derived from an append-only movement ledger. A balance is never edited directly; it is always the sum of its movements |
| T-02 | **Entitlement check performance** | Coverage and balance check ≤ 200 ms p95, served from a read model, under the load of 250,000+ monthly intakes |
| T-03 | **Idempotent consumption** | Consuming entitlement for the same source document twice is a no-op. Restoration on cancellation is likewise idempotent |
| T-04 | **Template binding with version pinning** | A contract binds to a specific template version at creation. Later template changes never mutate live contracts |
| T-05 | **Configuration-driven families** | A new contract family requires configuration only. Enforced by an acceptance test that instantiates all fourteen families from configuration |
| T-06 | **Immutable versions** | Every amendment produces a new immutable version; prior versions are never mutated |
| T-07 | **Effective-dated everything** | Coverage, entitlement, SLA and price all carry validity windows; a query at any past date returns what was true then |
| T-08 | **Scheduled generation at scale** | Preventive schedule generation for the full contract base completes within its nightly window and is restartable from the point of failure |
| T-09 | **Transactional outbox** | Contract state changes and their events are written in one transaction; M39 and M20 never diverge from M08 |
| T-10 | **SLA computation reproducibility** | Attainment is recomputed deterministically from the order record, so 1000FiX and the customer always agree on the number |
| T-11 | **Cost-to-serve aggregation** | Cost accrues incrementally from source events rather than by periodic full recomputation |
| T-12 | **Legal hold and retention** | Documents under hold are excluded from purge; retention follows the records schedule in M24 |
| T-13 | **Concurrency** | Simultaneous entitlement consumption from two branches for the same contract is serialised without deadlock or double-spend |
| T-14 | **Portal scoping** | A corporate user sees only their own company's contracts, further scoped by their role, enforced at the record-rule layer |
| T-15 | **Performance envelope** | Contract read ≤ 250 ms p95 · entitlement check ≤ 200 ms p95 · contract base dashboard over 20,000 contracts ≤ 2 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M08 |
|---|---|---|
| **Service centre agent** | Argues with the customer about whether the device is covered and how many visits remain | Sees coverage and balance at intake in under a second, and can show the customer the same screen |
| **Account manager** | Keeps a personal spreadsheet of renewals and loses some of them | Works a generated renewal pipeline with lead-time triggers and escalation |
| **Branch manager** | Cannot tell which contracts in the branch are losing money | Sees contract margin by account and asset class |
| **Dispatch manager** | Treats every job the same | Contract-covered jobs carry their contractual SLA and priority automatically |
| **Technician** | Does not know what is in scope; does work that is not covered | Sees covered scope and exclusions on the job |
| **Finance officer** | Cannot reconcile AMC revenue to a contract base | Contract, entitlement and billing agree because M39 bills from M08's definition |
| **Corporate client** | Phones to ask what is covered and how many visits remain | Sees entitlement, consumption, SLA attainment and the maintenance calendar in P04 |
| **Quality manager** | Discovers a lapsed calibration obligation during an audit | Sees the obligation register with due dates and evidence |
| **CCO** | Cannot state the contract base or the renewal rate | Sees base, growth, renewal rate, churn reasons and margin distribution weekly |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **AMC / RAMC renewal uplift** | Lead-time-triggered renewal quotations, escalation ladder, consumption evidence attached to the proposal | **BDT 72 lac/year** *(business case §6.2)*; renewal rate **60% → 88%** |
| **Contract base growth** | A contract engine that can model any family without a project, plus visible entitlement that makes contracts sellable | **2.5× contract base** *(category KPI)* |
| **Contract margin protection** | Continuous cost-to-serve against contract revenue; negative-margin contracts surfaced before renewal | Contracts with negative margin from unknown to **< 3%** |
| **Revenue leakage closure on covered work** | Entitlement exhaustion is detected and treated (charged, blocked or topped up) rather than silently absorbed | Removes unbilled out-of-entitlement work, currently invisible |
| **SLA credit control** | Credits computed from the same measurement both parties can see, approved before issue | Prevents both under-payment disputes and uncontrolled credit issue |
| **Managed-services contribution** | MSP agreements cannot be sold at scale without contractual SLA, entitlement and service credits | Enables the **BDT 95 lac/year** MSP contribution attributed to M05 |
| **Dispute and administration saving** | Coverage arguments at the counter, and renewal chasing by phone, both disappear | Part of the **BDT 62 lac/year** administrative saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Contractual memory** | The company stops depending on one account manager's recollection of what was promised to whom |
| **Auditability** | ISO 9001 contract review and customer-property clauses, and brand-partner audits, are answered from a complete contract file |
| **Regulatory and statutory obligation safety** | Healthcare calibration and specialty certification obligations are tracked, not remembered. A missed calibration is a patient-safety and liability exposure, not merely a commercial one |
| **Negotiating position** | Entering a renewal with consumption data, SLA attainment and cost-to-serve changes the conversation from price haggling to value evidence |
| **Predictable revenue** | A known contract base with known expiry profile is the foundation of the recurring-revenue story the business plan depends on |
| **Fair treatment** | Two customers on the same package receive the same entitlement, the same SLA and the same escalation |
| **Model-ready data** | Churn prediction, renewal probability and cost-to-serve forecasting in M26 all train on M08 data |

---

## 8. Lifecycle & State Model

```
              ┌─────────┐
              │  DRAFT  │  built from a template or an accepted proposal
              └────┬────┘
                   │ submit
              ┌────▼──────────────┐
              │ PENDING APPROVAL  │──── rejected ──► DRAFT (reason)
              └────┬──────────────┘
                   │ approved (standard terms: Sales Manager;
                   │            non-standard: CCO + CFO)
              ┌────▼────────┐
              │  APPROVED   │
              └────┬────────┘
                   │ signature captured and sealed
              ┌────▼────────┐
              │   SIGNED    │  executed, not yet effective
              └────┬────────┘
                   │ effective date reached
              ┌────▼────────┐
    ┌────────►│   ACTIVE    │◄──────── reinstated
    │         └────┬────────┘
    │              │
    │      ┌───────┼──────────┬─────────────────┐
    │      │       │          │                 │
    │      ▼       ▼          ▼                 ▼
    │  ┌────────┐ ┌─────────────┐  ┌─────────────────┐
    │  │AMENDED │ │  SUSPENDED  │  │ RENEWAL PENDING │
    │  │(new    │ │ (billing &  │  │ (lead time      │
    │  │version)│ │ entitlement │  │  reached)       │
    │  └───┬────┘ │  halted)    │  └────────┬────────┘
    │      │      └──────┬──────┘           │
    └──────┘             └──────────────────┤
                                            │
                    ┌───────────────────────┼──────────────────┐
                    │                       │                  │
                    ▼                       ▼                  ▼
            ┌───────────────┐      ┌────────────────┐  ┌──────────────┐
            │   RENEWED     │      │    EXPIRED     │  │  TERMINATED  │
            │ (new term or  │      │ (lapsed with   │  │ (early, with │
            │  new contract)│      │  no renewal)   │  │  settlement) │
            └───────────────┘      └───────┬────────┘  └──────┬───────┘
                                           │                  │
                                           └────────┬─────────┘
                                                    ▼
                                            ┌──────────────┐
                                            │    CLOSED    │
                                            └──────────────┘

  Cross-cutting: DISPUTED (flag, not a state) suppresses auto-renewal and escalation.
  Terminal exceptions: CANCELLED (signed but never effective) · NOVATED (transferred).
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | Pending Approval | Template bound; parties, term, coverage, entitlement and pricing complete | Account Manager |
| Pending Approval | Approved | Standard terms → Sales Manager; non-standard → CCO **and** CFO *(`05-04` §7)* | Approver |
| Approved | Signed | Executed document attached; signature method and date recorded; version sealed | Account Manager |
| Signed | Active | Effective date reached; covered assets resolved; entitlement initialised; M39 billing schedule created | System |
| Active | Amended | Amendment approved at the correct authority; new version created | Account Manager + approver |
| Active | Suspended | Approved suspension reason; M39 billing halt confirmed | Finance Manager / CCO |
| Suspended | Active | Reinstatement approved; suspended-period treatment declared | Finance Manager / CCO |
| Active | Renewal Pending | Renewal lead time reached and the contract is not disputed | System |
| Renewal Pending | Renewed | Renewal quotation accepted in M36 | Customer + system |
| Renewal Pending / Active | Expired | Expiry date passed with no accepted renewal | System |
| Active | Terminated | Notice validated; early-termination charge computed; entitlement settled; asset return raised | CCO + CFO |
| Expired / Terminated | Closed | All obligations discharged; final settlement complete; assets returned | System |
| Signed | Cancelled | Cancellation before the effective date, with reason; downstream objects unwound | CCO |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-CTR-01 | A contract cannot become Active without at least one covered asset or a declared category-based coverage rule | **H** | CCO |
| BRU-CTR-02 | An AMC-type service order can only be created if the device is on an active contract's covered-asset list *(BRU-SRM-03)* | **H** | Account Manager |
| BRU-CTR-03 | The contractual SLA always overrides the standard SLA for contract-covered work | **C** | Ops Director |
| BRU-CTR-04 | Entitlement is decremented only on confirmed consumption, and restored on cancellation or warranty rework | **C** | Ops Director |
| BRU-CTR-05 | Work beyond entitlement is never delivered free; it is charged, blocked or topped up per the contract's declared exhaustion treatment | **H** | CCO |
| BRU-CTR-06 | Non-standard terms require CCO **and** CFO approval before activation | **H** | CFO |
| BRU-CTR-07 | Auto-renewal is permitted only where the contract expressly allows it, and only with advance customer notice and an opt-out window | **H** | CCO |
| BRU-CTR-08 | A suspended contract consumes no entitlement and generates no billing | **H** | CFO |
| BRU-CTR-09 | A service credit is computed by the system, approved by an authorised role, and issued only by M20 as a credit note | **H** | CFO |
| BRU-CTR-10 | A contract amendment creates a new immutable version; prior versions are never edited | **H** | CCO |
| BRU-CTR-11 | Early termination requires notice-period validation and settlement of outstanding entitlement and charges | **H** | CFO |
| BRU-CTR-12 | A disputed contract does not auto-renew, does not escalate, and its documents are under legal hold | **H** | Quality Manager |
| BRU-CTR-13 | A contract trending to negative margin is escalated to the CCO no later than the renewal lead time | **C** | CCO |
| BRU-CTR-14 | Preventive and calibration work is generated at the contractual lead time, and a missed calibration obligation blocks contract compliance sign-off | **H** | Quality Manager |
| BRU-CTR-15 | A contract binds to a template version at creation; later template changes never alter a live contract | **H** | CTO |
| BRU-CTR-16 | Entitlement balances are derived from the movement ledger and can never be edited directly | **H** | CTO |
| BRU-CTR-17 | The account manager who negotiates a contract cannot approve its non-standard terms | **H** | CFO |
| BRU-CTR-18 | A covered asset detached mid-term triggers proration in M39 from the detachment date | **C** | CFO |
| BRU-CTR-19 | Every contract must carry a named 1000FiX owner at all times; on staff departure ownership is reassigned automatically | **C** | CCO |
| BRU-CTR-20 | Contract documents are retained for the statutory period after closure and cannot be purged while under hold | **H** | Quality Manager |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.contract` | `fix_contract` | Contract header | name, family, template_id, template_version, partner_id, entity_id, currency_id, state, effective_from, expiry_date, notice_days, auto_renew, owner_id, parent_contract_id, value, margin_pct |
| `fix.contract.version` | `fix_contract_version` | Immutable versions | contract_id, version, change_type, summary, approved_by, sealed_at, document_id |
| `fix.contract.party` | `fix_contract_party` | Parties and roles | contract_id, partner_id, role (customer/signatory/requester/approver/notice), portal_access |
| `fix.contract.coverage` | `fix_contract_coverage` | Covered scope | contract_id, asset_id, category_id, site_id, department_id, cover_from, cover_to, rule_type |
| `fix.contract.exclusion` | `fix_contract_exclusion` | Explicit exclusions | contract_id, exclusion_type, fault_code_id, cause, text_bn, text_en |
| `fix.entitlement` | `fix_entitlement` | Entitlement definition | contract_id, type, quantity, uom_id, period, reset_rule, carry_over, exhaustion_treatment, valid_from, valid_to |
| `fix.entitlement.movement` | `fix_entitlement_movement` | Append-only ledger | entitlement_id, movement_type (grant/consume/restore/expire/topup), qty, source_doc_ref, at, actor_id |
| `fix.entitlement.balance` | `fix_entitlement_balance` | Derived read model | entitlement_id, as_of, granted, consumed, restored, expired, remaining |
| `fix.contract.sla` | `fix_contract_sla` | Contractual SLA | contract_id, priority, asset_class_id, site_id, response_min, onsite_min, restore_min, resolve_min, availability_pct, calendar_id, exclusions_json |
| `fix.service.credit.scheme` | `fix_service_credit_scheme` | Credit rules | contract_id, breach_type, severity, credit_basis, credit_value, cumulative_rule, cap_value |
| `fix.service.credit` | `fix_service_credit` | Computed credits | contract_id, period, breach_refs, computed_value, state, approved_by, credit_note_ref |
| `fix.contract.schedule` | `fix_contract_schedule` | Preventive & calibration plan | contract_id, schedule_type, asset_id, frequency, lead_days, next_due, last_done, generated_order_ref |
| `fix.contract.obligation` | `fix_contract_obligation` | Obligation register | contract_id, obligation_type, party, description, due_date, recurrence, owner_id, state, evidence_document_id |
| `fix.contract.renewal` | `fix_contract_renewal` | Renewal process record | contract_id, lead_triggered_at, quotation_id, escalation_level, outcome, churn_reason, competitor, winback_eligible |
| `fix.contract.escalation` | `fix_contract_escalation` | Price escalation rules | contract_id, basis (fixed/index/negotiated), value, index_ref, applies_at |
| `fix.contract.cost` | `fix_contract_cost` | Cost-to-serve accrual | contract_id, period, cost_type, source_module, source_doc_ref, amount |
| `fix.contract.profitability` | `fix_contract_profitability` | Derived margin view | contract_id, period, revenue, cost, margin, margin_pct, trend, alert_state |
| `fix.contract.suspension` | `fix_contract_suspension` | Suspension record | contract_id, reason, from_date, to_date, entitlement_treatment, approved_by |
| `fix.contract.termination` | `fix_contract_termination` | Termination record | contract_id, requested_by, notice_valid, effective_date, early_charge, settlement_ref, asset_return_ref |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.contract.product.template` | M37 | Bound by id and version at creation |
| `fix.rate.card` (contract-scoped) | M11 | Referenced; price resolution by API |
| `fix.quotation` (proposal and renewal) | M36 | Referenced; created by request |
| `fix.party`, sites, departments, credit status | M33 | Live read |
| `fix.asset` | M17 / M49 | Live read for coverage resolution |
| `fix.service.order`, `fix.sla.clock` | M01 | Live read; consumes entitlement and SLA outcomes |
| `fix.msp.ticket`, estate health | M05 | Live read; consumes entitlement |
| Job cost components | M01, M02, M03, M15 | Event-driven cost accrual |
| Billing schedule, invoices, MRR | M39 | Live read; commands issued |
| `fix.ar.credit.note` | M20 | Command issued for service credits |
| `fix.document`, e-signature, retention | M24 | Service call |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-CTR-01 | Contract proposal accepted in M36 | Create the contract in Draft from the template, populate parties, scope, entitlement, SLA and pricing, and assign for signature | Create a manual contract task with the proposal attached |
| AUT-CTR-02 | Contract reaches its effective date | Activate, resolve covered assets, initialise entitlement grants, instruct M39 to create the billing schedule, and emit `contract.activated` | Hold activation; alert the account manager and Finance |
| AUT-CTR-03 | Service order created for a covered asset | Return coverage, entitlement balance, contractual SLA and applicable rates to M01 at intake | Return "coverage unverified"; flag the order for manual entitlement review |
| AUT-CTR-04 | Covered work confirmed complete | Decrement entitlement against the movement ledger and update the balance read model | Queue the movement; alert if unprocessed after one hour |
| AUT-CTR-05 | Covered order cancelled or reworked under warranty | Restore the consumed entitlement idempotently | Flag for manual reconciliation |
| AUT-CTR-06 | Entitlement falls below the configured threshold | Notify the customer and the account manager, and offer a top-up quotation | Log; retry notification |
| AUT-CTR-07 | Entitlement exhausted | Apply the declared exhaustion treatment — charge, block or offer top-up — and inform the customer before further work | Block and escalate to the account manager |
| AUT-CTR-08 | Preventive or calibration schedule due within lead time | Generate the service order in M01 or the task in M05 with contract context | Escalate to the branch manager; calibration misses escalate to Quality |
| AUT-CTR-09 | Contractual SLA breached on a covered order | Compute the service credit, route it for approval, and record the breach against the contract | Record the breach; escalate the credit calculation manually |
| AUT-CTR-10 | Renewal lead time reached | Set Renewal Pending, request a renewal quotation from M36 with consumption and profitability attached, and assign the account manager | Create a manual renewal task |
| AUT-CTR-11 | Renewal unanswered at each escalation interval | Escalate to sales manager, then CCO, notifying at each step | Repeat; log |
| AUT-CTR-12 | Contract expires with no renewal | Set Expired, halt billing in M39, record churn, and feed win-back candidacy to M35 | Alert the account manager |
| AUT-CTR-13 | Non-payment threshold reached (M20 event) | Propose suspension to Finance with the entitlement and SLA consequence stated | Alert only; never auto-suspend without approval |
| AUT-CTR-14 | Cost event received from M01/M02/M03/M15 | Accrue to contract cost-to-serve and recompute margin incrementally | Queue; reconcile nightly |
| AUT-CTR-15 | Margin trends below zero or below the alert threshold | Escalate to the CCO with the cost breakdown and renewal date | Log; repeat weekly |
| AUT-CTR-16 | Obligation due date approaching | Notify the obligation owner; escalate on the due date; block compliance sign-off if a mandatory obligation lapses | Escalate to Quality Manager |
| AUT-CTR-17 | Contract owner leaves (M21 event) | Reassign every owned contract to the named successor and notify | Escalate to the CCO |
| AUT-CTR-18 | Asset attached or detached mid-term | Recompute coverage and signal M39 for proration from the effective date | Flag for manual proration |

---

## 12. Interfaces

### 12.1 Upstream — M08 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Contract product templates, covered service definitions, SLA templates | Master data projection |
| M36 Quotation | Accepted proposals and accepted renewal quotations | Event `quotation.accepted` |
| M11 Pricing | Contract rate sets, escalation calculations, renewal pricing | REST |
| M33 Party Master | Customers, legal entities, sites, departments, signatories, credit status | Live read |
| M17 Asset Registry | Assets for coverage resolution, and asset lifecycle changes | Live read + event `asset.status_changed` |
| M01 SRM | Covered work consumption, SLA outcomes, job costs | Events `service_order.closed`, `sla.breached` |
| M05 Managed Services | Ticket consumption, estate health, availability measurement | Events |
| M02 / M03 / M15 | Labour, logistics and parts cost for cost-to-serve | Events |
| M39 Subscription | Billing status, invoiced value, collection status | Live read + events |
| M20 Receivable | Payment status and dunning stage for suspension proposals | Event `receivable.dunning_stage_changed` |
| M24 Document | Executed agreements, annexes, e-signature, retention | Service call |
| M21 Core HR | Staff departures triggering contract ownership reassignment | Event `employee.left` |

### 12.2 Downstream — M08 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 SRM | Coverage verdict, entitlement balance, contractual SLA, applicable rate context at intake | REST `POST /api/v1/contracts/entitlement-check` |
| M39 Subscription | The billing basis: plan, term, quantity, proration triggers, suspension and termination signals | Events + REST |
| M20 Receivable | Service credit instructions and contract references for invoicing | Command + reference |
| M09 Warranty | Contract coverage context where warranty and contract overlap | REST |
| M05 Managed Services | MSP entitlement, SLA and estate scope | REST + projection |
| M02 Field Service | Contractual priority and SLA on covered work | Via M01 |
| M36 Quotation | Renewal and top-up quotation requests with consumption evidence | Event `contract.renewal_due` + REST |
| M53 Revenue | Contract obligations for revenue-recognition classification | Projection |
| M13 Rental | Master hire agreement terms for call-off | REST |
| M12 Marketplace | Seller agreement terms and standing | REST |
| M40 Partner | Brand partner, alliance and franchise agreement records | REST |
| M23 Quality | Contractual obligations relevant to audit and certification | Projection |
| M35 Marketing | Churned contracts for win-back campaigns | Event `contract.expired` |
| M07 CRM | Upsell signals from entitlement exhaustion and asset growth | Events |
| M25 BID · M26 AIM | Contract base, renewal, churn, entitlement and profitability fact streams | Warehouse extract |
| P01 / P04 portals | Contract view, entitlement balance, maintenance calendar, SLA attainment, renewal | REST via M28 |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `contract.created` | contract id, family, customer, value, term | M39, M25 |
| `contract.activated` | contract id, effective_from, coverage, entitlements, SLA | M39, M01, M05, M20 |
| `contract.amended` | contract id, version, change summary, effective_from | M39, M01, M11, M20 |
| `contract.asset_attached` / `contract.asset_detached` | contract id, asset id, effective date | M39, M17, M01 |
| `contract.entitlement_consumed` | contract id, entitlement, qty, remaining, source doc | M01, M04, M27, M25 |
| `contract.entitlement_low` | contract id, entitlement, remaining, threshold | M27, M36, M07 |
| `contract.entitlement_exhausted` | contract id, entitlement, treatment applied | M01, M27, M36 |
| `contract.sla_breached` | contract id, order ref, commitment, actual, credit computed | M20, M23, M25 |
| `contract.service_credit_approved` | contract id, period, value | M20, M53 |
| `contract.suspended` / `contract.reinstated` | contract id, reason, dates, treatment | M39, M01, M20 |
| `contract.renewal_due` | contract id, expiry, consumption summary, margin | M36, M07, M27 |
| `contract.renewed` | old contract id, new contract/term, value change | M39, M25 |
| `contract.expired` | contract id, churn reason, win-back eligibility | M39, M35, M25 |
| `contract.terminated` | contract id, effective date, early charge, settlement | M39, M20, M13 |
| `contract.margin_alert` | contract id, margin, trend, renewal date | M25, CCO alerting |
| `contract.obligation_overdue` | contract id, obligation, owner, days overdue | M23, M27 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-CTR-01 | E-signature provider *(via M24, L6)* | Bidirectional | Execution of contracts and amendments |
| INT-CTR-02 | Corporate client procurement portals | Outbound | Contract and SLA reporting where the client requires it |
| INT-CTR-03 | Calibration and certification bodies | Bidirectional (document) | Calibration certificate evidence for healthcare and specialty agreements |
| INT-CTR-04 | Insurance providers | Inbound (document) | Insurance obligation evidence on both sides |
| INT-CTR-05 | Index sources for escalation | Inbound | Index-linked price escalation basis where contractually agreed |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/contracts` | GET/POST | Contract register and creation | P03, P04, M36 |
| `/api/v1/contracts/{id}` | GET | Full contract detail, authorisation-scoped | All portals |
| `/api/v1/contracts/entitlement-check` | POST | Coverage verdict, balance, SLA and treatment for an asset and work type | M01, M05, P01, P04 |
| `/api/v1/contracts/{id}/entitlements` | GET | Entitlement definitions, balances and movement history | P04, P03 |
| `/api/v1/contracts/{id}/consume` | POST | Idempotent entitlement consumption | M01, M05 |
| `/api/v1/contracts/{id}/restore` | POST | Idempotent entitlement restoration | M01 |
| `/api/v1/contracts/{id}/assets` | POST/DELETE | Attach or detach a covered asset | P03, P04 |
| `/api/v1/contracts/{id}/amend` | POST | Raise an amendment | P03 |
| `/api/v1/contracts/{id}/suspend` | POST | Suspend with reason | P03 |
| `/api/v1/contracts/{id}/terminate` | POST | Terminate with notice validation and settlement | P03 |
| `/api/v1/contracts/{id}/renew` | POST | Trigger or record renewal | P03, M36 |
| `/api/v1/contracts/{id}/sla` | GET | Contractual SLA and attainment | M01, P04 |
| `/api/v1/contracts/{id}/schedule` | GET | Preventive and calibration calendar | P04, M01 |
| `/api/v1/contracts/{id}/obligations` | GET/POST | Obligation register | P03, P04 |
| `/api/v1/contracts/{id}/profitability` | GET | Revenue, cost-to-serve and margin | P03, P06 |
| `/api/v1/contracts/{id}/file` | GET | Complete evidenced contract file for audit | P03, auditor |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All |
| R03 Chief Financial Officer | R A | All — non-standard terms, suspension, termination, credits |
| R21 Sales Manager | C R U A | Assigned segment — standard-terms approval |
| R22 Account Manager (Corporate) | C R U A | Assigned accounts |
| R06 Branch Manager | R | Own branch's contracts |
| R08 Service Centre Agent | R | Own branch — entitlement check only |
| R07 Dispatch Manager | R | Assigned zones — SLA and priority context |
| R13 Remote Support Engineer | R | Assigned MSP clients |
| R26 Finance Manager | R A | All — suspension, credits, settlement |
| R27 Finance Officer | R | Billing and collection scope |
| R28 Warranty Claims Officer | R | Contracts overlapping warranty |
| R32 Quality Manager / ISO Coordinator | R U | Obligation register, calibration compliance, legal hold |
| R05 Operations Director | R | All — delivery obligation view |
| R34 Contact Centre Agent | R | Customer-facing entitlement and coverage |
| R36 Customer | R | Own contracts, entitlement and calendar |
| R37 Corporate Portal User | R | Own company; role-scoped within it |
| R38 External Party | R | Own agreement only (seller, brand partner, franchise) |

**Field-level restrictions.** `cost_to_serve`, `margin`, `margin_pct` and internal renewal
strategy notes are visible only to R01–R05, R21, R22, R26 and R27. `customer_credit_limit`
follows `05-04` §5. No external portal receives cost, margin or internal notes.

**Segregation of duties.** SOD-15 *(to be registered in `05-04` §6)*: the account manager who
negotiates a contract cannot approve its non-standard terms. Service credit computation,
approval and credit-note issue are three separate roles, interacting with SOD-04.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Contract base dashboard | CCO, CEO | Real time | Active contracts by family, segment, branch, value and expiry profile; growth against the 2.5× target |
| Renewal pipeline | Account Managers, Sales Manager, CCO | Weekly | Contracts in the renewal window by value, days remaining, escalation level and probability |
| Renewal rate and churn analysis | CCO, CEO | Monthly | Renewal rate by family and segment; churn reasons ranked; competitor mentions |
| Contract profitability | CFO, CCO, Account Managers | Monthly | Revenue, cost-to-serve and margin per contract; negative and at-risk contracts listed |
| Entitlement utilisation | CCO, Account Managers | Monthly | Consumption vs sold entitlement; under-use (churn risk) and over-use (margin risk) |
| SLA attainment by contract | Ops Director, CCO, corporate clients | Monthly | Commitment vs actual by priority and site, with breach detail |
| Service credit exposure | CFO | Monthly | Credits computed, approved, issued and forecast; aggregate exposure against caps |
| Obligation and compliance register | Quality Manager, CCO | Weekly | Obligations due, overdue and discharged; calibration and certificate currency |
| Preventive schedule adherence | Ops Director, Quality Manager | Weekly | Scheduled vs generated vs completed preventive and calibration visits |
| Contract concentration and exposure | CFO, CEO | Quarterly | Revenue concentration by customer and family; largest single-contract dependency |
| Amendment and dispute log | CCO, Quality Manager | Monthly | Amendments by type and value; disputed contracts and their status |
| Contract file (per contract) | Auditor, corporate client, brand partner | On demand | Complete evidenced record — agreement, versions, obligations, SLA, entitlement ledger |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-C08-01 | AMC / RAMC renewal rate | 60% | 78% | **88%** |
| KPI-C08-02 | Contract base growth (vs Wave 1 baseline) | baseline | 1.6× | **2.5×** |
| KPI-C08-03 | Contracts with negative margin | unknown | < 8% | **< 3%** |
| KPI-C08-04 | Entitlement check latency p95 | n/a | ≤ 250 ms | **≤ 200 ms** |
| KPI-C08-05 | Contract-covered orders with an automatic coverage verdict at intake | 0% | 95% | **100%** |
| KPI-C08-06 | Contractual SLA attainment | unmeasured | 92% | **96%** |
| KPI-C08-07 | Preventive visits generated and completed on schedule | unmeasured | 85% | **> 95%** |
| KPI-C08-08 | Calibration obligations completed before expiry | unmeasured | 98% | **100%** |
| KPI-C08-09 | Renewal quotations issued before the lead-time deadline | 0% | 90% | **100%** |
| KPI-C08-10 | Out-of-entitlement work delivered unbilled | unknown | < 3% | **< 0.5%** |
| KPI-C08-11 | Contracts with a complete obligation register | 0% | 90% | **100%** |
| KPI-C08-12 | Coverage disputes raised at the counter | unmeasured | −60% | **−90%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `mail`, `portal`, `product` linkage | 8% |
| L2 | OCA `agreement`, `agreement_legal`, `agreement_serviceprofile`, `partner_contact_*` | 20% |
| L5 | `cd_contract_engine`, `cd_entitlement`, `cd_contract_sla`, `cd_contract_renewal`, `cd_contract_profitability` | 72% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-C08-01 | `cd_contract_engine` — contract object, template binding, versioning, families, amendment, suspension, termination | Odoo module | 9 PW |
| CD-C08-02 | `cd_entitlement` — definition, movement ledger, balance read model, check API, exhaustion treatment | Odoo module + service | 8 PW |
| CD-C08-03 | `cd_contract_sla` — contractual SLA, precedence, attainment computation, service credit scheme | Odoo module | 5 PW |
| CD-C08-04 | `cd_contract_renewal` — lead-time triggers, renewal pipeline, escalation ladder, churn record | Odoo module | 4 PW |
| CD-C08-05 | `cd_contract_profitability` — cost-to-serve accrual, margin computation, alerting | Odoo module | 3 PW |
| CD-C08-06 | Preventive and obligation scheduler, contract API layer | Service | 3 PW |
| | | **Total** | **32 PW** |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M37 Catalogue | The fourteen contract product templates must exist |
| M11 Pricing | Contract rate sets and escalation |
| M36 Quotation | The creation path is an accepted proposal |
| M33 Party Master | Parties, sites and legal entities |
| M17 Asset Registry | Coverage resolves to assets |
| M01 SRM | Entitlement is consumed by service orders |
| M24 Document | Execution, retention and legal hold |
| **Delivered alongside M39** | M39 consumes M08's definition; the two are gated together in W4 |

**Wave 4 gate condition.** All fourteen contract families must instantiate from configuration
before the gate is passed. The category risk register rates failure here as High.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| AMC / RAMC tracking spreadsheets | ~3,000–5,000 active contracts, to be profiled | `fix.contract` + coverage + entitlement | W4 |
| Corporate AMC agreements (documents) | ~150 | `fix.contract` + `fix.document` | W4 |
| MSP agreements | ~40 | `fix.contract` (Managed Services family) | W4–W5 |
| Brand partner authorisation agreements | 17+ | `fix.contract` (Brand partner family) | W4 |
| Rental master agreements | ~30 | `fix.contract` (Rental master family) | W6 |
| Historic expired contracts | Unknown | Archive area; excluded from base and renewal KPIs | W4 |

**Migration rule.** Entitlement balances are migrated as an opening `grant` movement with a
declared as-at date and a reconciliation note, never as an edited balance. Any contract whose
remaining entitlement cannot be evidenced is migrated with a zero opening balance and flagged
for customer confirmation before the first covered job — a deliberately conservative choice that
must be communicated to account managers before Wave 4 cutover.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | All fourteen contract families instantiate from configuration with no code change | Fourteen scripted instantiations at the Wave 4 gate |
| AC-02 | An entitlement check returns coverage, balance, SLA and treatment in ≤ 200 ms p95 under production-scale load | Load test report |
| AC-03 | Entitlement balance always equals the sum of its ledger movements, and no route permits direct balance edit | Reconciliation test + negative test via UI, API and ORM |
| AC-04 | Consumption and restoration are idempotent under retry and duplicate delivery | Chaos test with duplicated events |
| AC-05 | A contractual SLA overrides the standard SLA on every covered order, in every channel | Scripted scenario across all delivery modes |
| AC-06 | An SLA breach computes a service credit that is approved before any credit note is issued | End-to-end test with M20 |
| AC-07 | Preventive and calibration work generates at the correct lead time across the full contract base within the nightly window | Scheduled-job test at scale |
| AC-08 | A missed mandatory calibration blocks contract compliance sign-off | Negative test |
| AC-09 | An amendment produces a new immutable version; prior versions are unchanged and comparable | Mutation attempt + comparison demonstration |
| AC-10 | Asset attach and detach mid-term trigger correct proration signals to M39 | Joint test with M39 |
| AC-11 | A renewal quotation is generated at the lead time with consumption and profitability attached, and escalates when unanswered | Scripted scenario over a compressed timeline |
| AC-12 | Contract profitability reconciles to source cost events and to M39 revenue | Reconciliation report |
| AC-13 | A corporate portal user sees only their own company's contracts, scoped by their role | Negative test per role |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the actual size and quality of the current AMC/RAMC contract base? Migration effort and the entitlement reconciliation approach both depend on it | CCO / Ops Director | W3 planning |
| Q-02 | What is the standard renewal lead time per contract family — 30, 60 or 90 days? | CCO | W4 build |
| Q-03 | Is auto-renewal permitted in the current standard RAMC terms, and does Bangladeshi consumer law constrain it? | Legal / CCO | W4 build |
| Q-04 | What is the service credit scheme for MSP contracts — is it already committed in signed agreements? | Corporate Services Head / CFO | W4 build |
| Q-05 | On migration, where entitlement consumed to date cannot be evidenced, does the company grant the benefit of the doubt or start from zero? The design assumes zero with confirmation | CCO / CEO | W4 cutover |
| Q-06 | Do healthcare AMC agreements carry statutory calibration obligations that make 1000FiX legally liable, and is that liability insured? | Legal / Quality Manager | W4 build |
| Q-07 | Should brand-partner authorisation agreements live in M08 or M40? The design places the *agreement* in M08 and the *relationship* in M40 | CCO | W4 build |
| Q-08 | What is the treatment of entitlement during suspension — forfeited, frozen or prorated? Currently declared per contract; should there be a company default? | CFO / CCO | W4 build |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §4.2, §6, §8, §10 ·
`M37_Product_and_Service_Catalogue_Management.md` §5.5 ·
`M36_Quotation_Estimation_and_Tender_Management.md` §5.2, §12 ·
`M11_Pricing_Rate_Cards_and_Dynamic_Pricing.md` §5.2 ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` §3, §12 ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §6, §7 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` P04 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.8, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §8 ·
`1000FiX Business Plan` §RAMC Packages, §Corporate AMC, §IT Infrastructure AMC, §Healthcare AMC, §Specialty AMC, §Managed Services, §Rental ·
`1000FiX_Services_Company_Profile.md` §Brand Partnerships ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Marketplace

**External benchmark**
SAP S/4HANA Service — service contracts, response profiles, entitlement determination ·
SAP Condition Contract Management — negotiated agreements ·
Oracle Fusion Enterprise Contracts / Service Contracts — templates, clause libraries, coverage, renewal management ·
Microsoft Dynamics 365 Field Service — agreements and automatic booking generation ·
IFS Cloud — service agreements and agreement profitability ·
Enterprise CLM practice (Icertis, Sirion, Ironclad, Conga) — obligation management and renewal intelligence ·
ServiceNow CSM — real-time entitlement verification ·
Odoo 19 / OCA `agreement` module family

---

*Module M08 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
