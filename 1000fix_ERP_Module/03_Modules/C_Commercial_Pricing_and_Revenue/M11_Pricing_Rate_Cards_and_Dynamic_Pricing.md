---
id: FIX-ERP2-M11
module_id: M11
module_code: PRC
module_name: Pricing, Rate Cards & Dynamic Pricing
category: C — Commercial, Pricing & Revenue
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Commercial Officer
system_owner: Commercial Squad
priority: P1
wave: W3 (core) → W7 (dynamic pricing)
---

# M11 — Pricing, Rate Cards & Dynamic Pricing
### Category C · Code `PRC` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M11 |
| **Module code** | `PRC` |
| **Category** | C — Commercial, Pricing & Revenue |
| **Status** | Existing (re-scoped — quotation and estimation moved to M36; catalogue definition moved to M37) |
| **Priority** | **P1** |
| **Delivery wave** | W3 core (Months 9–13) → W7 dynamic pricing (Months 27–30) |
| **Business owner** | Chief Commercial Officer |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `product_pricelist`) + L2 (OCA `product_pricelist_*`, `sale_order_price_recalculation`) + L5 (custom) |
| **Custom modules** | `cd_pricing_engine`, `cd_rate_card`, `cd_discount_governance`, `cd_price_experiment`, `cd_dynamic_pricing` |
| **Requirement range** | FR-PRC-001 … FR-PRC-052 |
| **Requirement count** | **52** *(measured; register estimate 36)* |
| **Effort estimate** | **26 person-weeks** *(measured; register estimate 20 PW)* — 18 PW in W3, 8 PW in W7 |
| **Depends on** | M37 Catalogue · M33 Party Master · M29 Identity · M28 Integration · M30 Platform Admin |
| **Depended on by** | M36, M08, M09, M39, M38, M12, M13, M14, M01, M04, M20, M53, M40, M10, M25, M26, M07 |

> **Register note.** The v1.0 register described M11 as *"Sales, Quotation & Dynamic Pricing"*
> under code `SLS`. Under rule RG-02 the identifier M11 is permanent; the module was re-scoped
> to pricing only and re-coded `PRC` in register v2.1, with quotation moving to the new M36.
> Some older documents (including `05-04` §3.2) still show `M11 SLS`; that reference is
> superseded by `02-02` v2.1.

---

## 2. Purpose

M11 answers exactly one question, for every transaction in the business: **what does this cost
this customer, on this channel, today?**

It is the only module permitted to compute a price. Every other module — quotation, contract,
warranty, subscription, storefront, marketplace, front desk, corporate portal — *requests* a
price and receives an answer with a full explanation of how it was reached. Nothing else stores
a rate; nothing else applies a discount.

That exclusivity is the point. In a business with fourteen revenue streams, 51+ branches,
17+ brand rate cards, corporate contract pricing and a marketplace, the alternative is prices
maintained in a dozen places, none of them agreeing, and margin leaking in every gap.

### Why It Exists

Today price lives in branch spreadsheets, in a manager's judgement, and in the memory of senior
agents. Two branches quote different amounts for the same repair on the same model. Discounts
are granted verbally with no record and no ceiling. Brand-partner labour rates are held in email
attachments. There is no measurement of realised price against list, so margin erosion is
invisible until the year-end accounts.

The business case attributes **BDT 40 lac/year to dynamic pricing margin uplift** and a
**+4 percentage-point gross-margin improvement on paid repair**. Neither is reachable without a
single, governed, measurable pricing engine. M11 is that engine.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.11 (BR-SLS-001…018) | Rate cards, price books, customer-specific pricing, discount approval thresholds |
| ERP BRD §10.1 | Approval authority by discount band |
| ERP URD §7 (US-SLS-*) | Agent, branch manager and account manager pricing user stories |
| `05-04` §7 Approval Authority Matrix | Discount bands: ≤10% agent · ≤20% branch manager · ≤35% sales manager · >35% CCO |
| Business Plan §Pricing Strategy, §Dynamic Pricing | The BDT 40 lac/year dynamic pricing benefit and the +3–6% uplift target |
| Company Profile §Brand Partnerships | 17+ brand partners, each with its own labour and parts reimbursement rate card |
| Service App SOW §Indicative Pricing | "The app should show an indicative price before booking" — requires a public, safe price API |
| `_CATEGORY_OVERVIEW.md` §4.1, §10 | The catalogue/pricing boundary and the "prices in more than one place" risk |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The pricing engine: deterministic resolution of a price for an item, customer, channel, date and context |
| 2 | Price books and their scoping by entity, branch, channel, segment, currency and validity window |
| 3 | Rate cards: labour rates by repair level, skill, brand, delivery mode, urgency and time-of-day |
| 4 | Parts pricing: markup schemes, provenance-grade differentials, banded and tiered pricing |
| 5 | Customer-specific and contract pricing, including negotiated rates bound to an M08 agreement |
| 6 | Corporate and volume pricing: tier breaks, committed-volume rates, site and department differentials |
| 7 | Brand-partner reimbursement rate cards — what the *brand* pays 1000FiX for warranty work |
| 8 | Cost-plus and margin-floor pricing, including a hard margin floor per item class |
| 9 | Discount definition, discount governance, approval routing and override recording |
| 10 | Promotional pricing: campaign prices, time-boxed offers, bundle pricing, minimum-purchase rules |
| 11 | Price adjustment rules: urgency premium, after-hours premium, distance/zone surcharge, emergency tariff |
| 12 | Currency, rounding, price precision and psychological rounding rules |
| 13 | Tax-inclusive / tax-exclusive presentation logic per channel and customer class |
| 14 | Price simulation ("what would this cost") and the price-explanation trace |
| 15 | Price versioning, effective dating, scheduled activation and mass price change |
| 16 | Price approval workflow and price-change governance |
| 17 | Realised-price analytics: list vs realised, discount leakage, margin waterfall |
| 18 | **Dynamic pricing (W7)**: rules and model-driven adjustment by demand, capacity, lead time, seasonality and elasticity |
| 19 | Price experimentation: A/B price tests with guardrails and statistical evaluation |
| 20 | The price API and the price-quote lock (a price, once quoted, is honoured for its validity period) |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| What an item *is* — definition, attributes, rBOM, standard time | **M37** Catalogue | A price is a decision about an item, not a property of it |
| The quotation or estimate document, its versions and its approval by the customer | **M36** Quotation | A quotation is a commercial instrument; M11 supplies the numbers it contains |
| Contract terms, entitlement and covered scope | **M08** Contract | M08 defines *what is covered*; M11 defines *what the uncovered part costs* |
| Recurring billing schedule, proration and MRR | **M39** Subscription | M11 prices the plan; M39 bills it |
| Invoice creation, credit notes and collection | **M20** Receivable | Only Category G creates financial documents |
| Tax rate determination and VAT/SD calculation | **M51** Tax | M11 produces a net price and a tax class; M51 computes the tax |
| Loyalty benefit and points definition | **M10** Loyalty | M10 defines the benefit; M11 applies it as a priced adjustment |
| Marketplace seller's own listing price | **M12** Marketplace | A seller sets their own price; M11 prices only 1000FiX's fees and commissions |
| Commission rate schemes and payout calculation | **M53** Revenue & Settlement | M11 may hold the commercial rate; M53 computes and pays |
| Standard cost and inventory valuation | **M15** Inventory | Cost is an input to pricing, owned by inventory |
| Purchase price and supplier price lists | **M16** Procurement | Buying prices are a procurement domain |
| Payroll rates and technician incentive rates | **M56** / **M57** | Internal compensation is not customer pricing |
| Storefront merchandising, badges and promotional display | **M38** E-Commerce | M38 presents; M11 decides |

### 3.3 Shared Concepts

| Concept | M11's Role | Owning Module |
|---|---|---|
| Item | Reads the definition; never edits | M37 |
| Standard cost | Reads as a pricing input and margin-floor basis | M15 |
| Customer, segment, tier | Reads for price applicability | M33 |
| Loyalty tier benefit | Applies as a priced adjustment | M10 |
| Contract negotiated rate | Stores the rate; M08 owns the agreement it belongs to | M11 (rate) / M08 (agreement) |
| Brand reimbursement rate | **Owner** of the rate card; M09 claims against it | M11 |
| Quotation line price | Supplies; M36 stores it on the document | M36 |
| Tax class | Reads from M37; passes to M51 | M37 / M51 |
| Price lock | **Owner** — a quoted price is immutable for its validity | M11 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Condition Technique** (condition tables, access sequences, condition types, pricing procedures) | The canonical enterprise pricing architecture: a price is derived by walking an ordered access sequence over condition tables until a match is found | **The whole architecture, simplified.** Access sequence, condition record, pricing procedure and condition type map directly onto our price-rule resolution. Also SAP's absolute separation of price from product master | SAP's 16-field condition tables and the requirement for ABAP routines to express any non-trivial rule. Our rules are declarative and testable from the UI |
| **SAP Condition Contract Management** | Customer- and supplier-specific negotiated condition agreements with settlement | The concept of a **rate agreement bound to a contract**, used for corporate negotiated pricing and brand reimbursement rate cards | Full rebate settlement machinery — M53 owns settlement |
| **Oracle Fusion Pricing Cloud** | Price lists, pricing strategies, matrix-based rules, pricing algorithms, segment assignment | **Pricing strategy assignment by customer segment**, and the **matrix rule** model for tier and volume breaks | Oracle's pricing algorithm scripting layer |
| **Microsoft Dynamics 365** — Price lists, price-level hierarchy | Simple, comprehensible price-list precedence | The comprehensibility target: a branch manager must be able to explain a price | Its limited rule expressiveness for service work |
| **IFS Cloud** — service pricing, rate types, price-per-repair-level | Labour rate by skill, repair level and contract | The **rate card by repair level and skill** structure, which is exactly our field-service reality | — |
| **CPQ platforms** (Salesforce CPQ, Oracle CPQ, PROS, Conga, DealHub class) | Discount governance, approval routing, deal desk, floor checks, margin guardrails, price guidance | **Discount bands with automatic approval routing, hard margin floors, and pre-signature out-of-policy flagging.** This is the direct answer to our unmeasured discount leakage | The full CPQ configurator — product configuration lives in M37, quoting in M36 |
| **PROS / Revology-class price optimisation** | Elasticity estimation, price guidance, win-rate modelling, margin waterfall | **Margin waterfall analytics and realised-vs-list measurement from day one**, with elasticity-driven guidance deferred to W7 | Buying a commercial optimisation engine; M26 provides the models on our own data |
| **Odoo 19 + OCA** — `product_pricelist`, `sale_order_price_recalculation`, `product_pricelist_direct_print` | Price list with rules by product, category, quantity, date and partner | The pricelist item model as the L1 store for simple rules | Odoo's assumption that pricelist rules alone are sufficient — they cannot express rate cards, margin floors or approval governance |

**Design position.** 1000FiX differs from the benchmark in five ways.

First, **service labour is priced by a rate card against a standard time, not by an hourly
meter**. The price of a repair is `SRT × rate + parts`, not `actual hours × rate`. This protects
the customer from a slow technician and protects 1000FiX from an under-quoted job — and it is
only possible because M37 owns standard repair times.

Second, **every price returns an explanation**. The API response carries the full derivation:
which price book, which rule, which adjustments, which discounts, which approvals. A branch
manager facing an angry customer can show exactly how the number was produced. Enterprise
pricing engines treat this as an audit feature; for us it is a front-line feature.

Third, **the margin floor is a hard block, not a warning**. Below-floor pricing requires an
explicit, named, logged approval at CCO level. Benchmarks typically warn; our discount culture
requires a block.

Fourth, **dynamic pricing is deliberately deferred to W7 and deliberately bounded**. It may move
a price within a declared corridor around the governed list price, never outside it, and it can
never change a price after a customer has been quoted. The category risk register records the
consequence of getting this wrong as trust damage — a cost that exceeds the uplift.

Fifth, **the public price API must be safe for anonymous use**. The customer app shows an
indicative price before booking. That surface exposes no cost, no margin, no rule structure and
no customer-specific rate — an explicit design constraint not present in back-office pricing
engines.

---

## 5. Functional Areas & Features

### 5.1 Pricing Engine & Resolution

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRC-001 | Deterministic price resolution | Resolve exactly one price for a given item, customer, channel, quantity, branch, currency and date, by walking an ordered, configurable access sequence | P0 | L5 |
| FR-PRC-002 | Price explanation trace | Return with every price the complete derivation — price book, rule matched, base, each adjustment, each discount, approvals required — in a form renderable to a non-technical user | P0 | L5 |
| FR-PRC-003 | Price simulation | Simulate a price for any hypothetical combination without creating a document, for use by agents, account managers and the corporate portal | P1 | L5 |
| FR-PRC-004 | Bulk pricing | Price a whole basket, estimate or bulk corporate upload in one call with per-line explanation, in ≤ 400 ms for 100 lines | P1 | L5 |
| FR-PRC-005 | Price lock | Freeze the resolved price on issue of a quotation, order or contract line, and honour it for its declared validity period regardless of subsequent price changes | P0 | L5 |
| FR-PRC-006 | Rule precedence and conflict resolution | Apply a declared, visible precedence when multiple rules match, and never resolve a price non-deterministically | P0 | L5 |
| FR-PRC-007 | Effective dating | Hold every price and rule with a validity window, and resolve historical documents against the rule that was valid at their document date | P0 | L5 |
| FR-PRC-008 | Currency and rounding | Support multi-currency price books, configurable rounding rules, price precision and psychological rounding per channel | P1 | L1 |
| FR-PRC-009 | Tax presentation mode | Return both tax-exclusive and tax-inclusive figures, and declare which is authoritative for the requesting channel and customer class | P0 | L5 |
| FR-PRC-010 | Public indicative price API | Expose an anonymous, rate-limited endpoint returning an indicative price band for a service and device, revealing no cost, margin, rule or customer-specific data | P1 | L5 |

### 5.2 Price Books & Rate Cards

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRC-011 | Price book management | Create price books scoped by entity, branch group, channel, customer segment, currency and validity, with a declared precedence order | P0 | L1 |
| FR-PRC-012 | Labour rate card | Define labour rates by repair level, skill class, brand, delivery mode and branch group, applied against the M37 standard repair time | P0 | L5 |
| FR-PRC-013 | Parts pricing scheme | Price parts by markup on cost, fixed price, banded markup by cost tier, or provenance-grade differential (genuine / OEM / aftermarket) | P0 | L5 |
| FR-PRC-014 | Service fixed pricing | Set fixed prices for standardised services independent of time and parts (diagnostics, data transfer, installation, collection) | P0 | L1 |
| FR-PRC-015 | Brand reimbursement rate card | Maintain per-brand warranty reimbursement rates for labour and parts, with version history and effective dating, consumed by M09 claims | P0 | L5 |
| FR-PRC-016 | Contract rate agreement | Bind a negotiated rate set to an M08 contract, applicable only to that contract's parties, sites and covered items, for the contract's term | P0 | L5 |
| FR-PRC-017 | Volume and tier breaks | Define quantity, value and committed-volume breaks with either bracket or cumulative treatment | P1 | L1 |
| FR-PRC-018 | Zone and distance pricing | Apply branch-zone and distance-band adjustments for on-site and pick-and-drop work | P1 | L5 |
| FR-PRC-019 | Urgency and time-based premiums | Apply express, emergency, after-hours, weekend and public-holiday premiums as declared, auditable adjustments | P1 | L5 |
| FR-PRC-020 | Channel differential | Permit a declared price differential by channel (branch, app, web, marketplace, corporate portal, partner) with a governed maximum spread | P1 | L5 |
| FR-PRC-021 | Rental and subscription rate structures | Express periodic rates, minimum-hire pricing, usage-overage rates and deposit bases for M13 and M39 | P2 | L5 |
| FR-PRC-022 | Refurbished pricing | Price refurbished units by grade band, age and model, with a declared depreciation curve | P2 | L5 |
| FR-PRC-023 | Marketplace fee schedule | Define commission percentages, listing fees, promotion/boost prices and payment-processing pass-through per category and seller tier | P1 | L5 |
| FR-PRC-024 | Mass price change | Apply a percentage or absolute change across a filtered item set with preview, approval, scheduled activation and one-step rollback | P1 | L5 |
| FR-PRC-025 | Price book copy and versioning | Copy a price book to create a new version, diff two versions, and schedule a version's activation | P1 | L5 |

### 5.3 Discount, Margin & Governance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRC-026 | Discount definition | Define discounts by type (percentage, absolute, override price), scope (line, document, customer, campaign) and eligibility | P0 | L5 |
| FR-PRC-027 | Discount authority bands | Enforce the approval matrix — ≤10% agent, ≤20% branch manager, ≤35% sales manager, >35% CCO — at the point of application, in every channel including API | P0 | L5 |
| FR-PRC-028 | Margin floor | Compute margin against standard cost on every priced line and hard-block any price below the item class's declared floor | P0 | L5 |
| FR-PRC-029 | Below-floor approval | Permit a below-floor price only through an explicit CCO-level approval carrying a mandatory reason, recorded permanently on the document | P0 | L5 |
| FR-PRC-030 | Discount reason codes | Require a reason code on every discount above a configurable threshold, from a governed list | P1 | L5 |
| FR-PRC-031 | Cumulative discount control | Compute the total effective discount across all sources (rule, campaign, loyalty, negotiated, manual) and apply the authority band to the *total*, not each part | P0 | L5 |
| FR-PRC-032 | Price override recording | Record every manual override with the original price, the override, the actor, the reason and the approval chain | P0 | L5 |
| FR-PRC-033 | Approval routing and SLA | Route approval requests to the correct role with an escalation timer, and allow approval from mobile | P1 | L5 |
| FR-PRC-034 | Price change governance | Require review and approval for any change to an active price book, with a preview of affected open documents | P0 | L5 |
| FR-PRC-035 | Segregation of duties | Prevent the same user from proposing and approving a price change or a below-floor discount | P0 | L5 |
| FR-PRC-036 | Exception reporting | Produce a standing exception report of overrides, below-floor approvals and out-of-band discounts for quarterly review | P1 | L5 |

### 5.4 Promotions, Campaigns & Loyalty Interaction

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRC-037 | Promotional price | Apply time-boxed promotional prices to a defined item and audience set, with automatic expiry | P1 | L1 |
| FR-PRC-038 | Conditional offers | Express buy-X-get-Y, minimum-value, bundle and first-time-customer offers as priced rules | P2 | L5 |
| FR-PRC-039 | Voucher and code application | Validate and apply a voucher or promotion code issued by M10, honouring its usage limits and eligibility | P1 | L5 |
| FR-PRC-040 | Loyalty benefit application | Apply Privilege-tier benefits defined by M10 as priced adjustments, with the tier's entitlement visible in the explanation | P1 | L5 |
| FR-PRC-041 | Promotion stacking rules | Declare which promotions may combine, and enforce a maximum combined benefit | P1 | L5 |
| FR-PRC-042 | Campaign attribution | Tag every priced line with the campaign or offer that influenced it, for M35 and M25 attribution | P2 | L5 |

### 5.5 Analytics, Experimentation & Dynamic Pricing *(W7)*

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-PRC-043 | Margin waterfall | Report, per segment, channel, branch and item class, the movement from list price to realised price to net margin, with every leakage component named | P1 | L5 |
| FR-PRC-044 | Realised-vs-list measurement | Measure realised price as a percentage of list on every transaction and trend it by branch, agent and segment | P1 | L5 |
| FR-PRC-045 | Price consistency monitor | Detect and report the same item priced differently across branches or channels beyond the permitted spread | P1 | L5 |
| FR-PRC-046 | Win/loss price analysis | Correlate quotation acceptance and rejection with price position, using M36 outcomes | P2 | L5 |
| FR-PRC-047 | Elasticity estimation | Consume M26 elasticity estimates by item class, segment and channel, and surface them as guidance to pricing owners | P2 | L5 |
| FR-PRC-048 | Dynamic pricing rules | Adjust price within a declared corridor by demand, branch capacity, technician availability, lead time, seasonality and inventory position | P2 | L5 |
| FR-PRC-049 | Dynamic pricing guardrails | Enforce a hard maximum deviation from list, a hard margin floor, an exclusion list of items and segments, and a kill switch that reverts to static pricing instantly | P2 | L5 |
| FR-PRC-050 | Price experimentation | Run controlled A/B price tests on defined item and audience sets with declared duration, guardrails and statistical evaluation | P2 | L5 |
| FR-PRC-051 | Dynamic pricing transparency | Never change a price already quoted or accepted, and always show the customer a single price with no visible variability within a session | P0 | L5 |
| FR-PRC-052 | Competitor price reference | Record observed competitor prices as a manual or feed-based reference input, clearly separated from own pricing data | P3 | L5 |

*(Full requirement text is mirrored in `05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Pure function pricing** | Price resolution is a pure function of its inputs and the rule set version. The same inputs always produce the same output, and the rule set version is returned with every answer |
| T-02 | **Rules as data** | Every price rule, adjustment and precedence is declared in configuration tables. No rule requires code |
| T-03 | **Explanation as a first-class output** | The trace is produced by the engine itself, not reconstructed afterwards; it cannot diverge from the calculation |
| T-04 | **Rule-set snapshot** | Every priced document records the rule-set version used, making historical prices exactly reproducible years later |
| T-05 | **Resolution performance** | Single-line price ≤ 60 ms p95 · 100-line basket ≤ 400 ms p95 · public indicative price ≤ 150 ms p95 |
| T-06 | **Rule caching and invalidation** | The active rule set is cached in memory; a price-book activation invalidates the cache atomically across all nodes |
| T-07 | **No price writes outside M11** | No other module's schema contains a rate table. Enforced by architectural test in CI |
| T-08 | **Idempotent price lock** | Locking a price twice for the same document line is a no-op, never a re-resolution |
| T-09 | **Precision and rounding safety** | All money arithmetic uses fixed-point decimal; rounding occurs once, at a declared point in the pipeline |
| T-10 | **Approval as state, not notification** | An out-of-band price is a document state that blocks progression, not merely an email to a manager |
| T-11 | **Public API hardening** | The anonymous price endpoint is rate-limited per IP and per device, returns bands rather than exact figures where configured, and exposes no internal identifiers |
| T-12 | **Dynamic pricing isolation** | The dynamic layer is a bounded adjustment applied *after* static resolution, is independently disableable, and defaults to zero adjustment on any error or timeout |
| T-13 | **Experiment integrity** | Assignment to a price experiment is deterministic per customer, stable across sessions, and excluded from contract and warranty pricing entirely |
| T-14 | **Auditability** | Every price-affecting change is audited with actor, before/after and reason; the audit is append-only |
| T-15 | **Simulation isolation** | Simulation never creates state, never consumes voucher usage counts, and is clearly marked in logs |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M11 |
|---|---|---|
| **Service centre agent** | Quotes from a laminated sheet or asks a colleague; the price varies by who is asked | Requests a price and receives one number with an explanation the customer can be shown |
| **Branch manager** | Grants discounts verbally with no ceiling and no record | Approves within a defined band; anything beyond routes upward automatically and is recorded |
| **Account manager** | Negotiates corporate rates in email; re-explains them at every renewal | Negotiated rates are bound to the contract and applied automatically for its term |
| **Warranty officer** | Looks up brand labour rates in an email attachment, sometimes an outdated one | Claims are valued against the current versioned brand rate card automatically |
| **Sales manager** | Cannot see whether the field is discounting to win or discounting from habit | Sees realised-vs-list and discount leakage by branch and agent every week |
| **Finance officer** | Discovers margin erosion at year-end | Sees the margin waterfall monthly, with each leakage component named |
| **Marketing** | Cannot run a genuine offer because there is no mechanism to end it | Time-boxed promotions expire automatically and are attributed |
| **Customer** | Is quoted differently at two branches and loses trust | Sees one price, in the app before booking and at the counter, with the same explanation |
| **CCO** | Sets a pricing policy that cannot be enforced or measured | Sets a policy that is enforced by the system and measured weekly |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Dynamic pricing margin uplift** | Demand-, capacity- and lead-time-aware adjustment within a governed corridor, from W7 | **BDT 40 lac/year** *(business case §6.2)*; category target **+3–6%** uplift on eligible volume |
| **Gross-margin improvement on paid repair** | Rate card against standard time replaces guesswork; margin floors block loss-making work; discount bands stop uncontrolled giveaway | **+4 percentage points** *(category KPI)* |
| **Discount leakage reduction** | Cumulative discount authority applied to the total, mandatory reason codes, standing exception review | Price override exceptions from unmeasured to **< 5%** of transactions |
| **Brand claim value accuracy** | Claims valued at the current versioned brand rate card rather than a stale attachment | Protects a measurable share of the **BDT 100 lac/year** warranty recovery owned by M09 |
| **Corporate contract profitability** | Negotiated rates enforced automatically; contract margin visible per contract | Supports the M08 target of **< 3% of contracts with negative margin** |
| **Price consistency across 51+ branches** | One engine, one answer | Removes the dispute and rework cost of inconsistent quoting; contributes to the retention benefit of **BDT 78 lac/year** |
| **Faster quoting** | Price resolution in under 60 ms with explanation removes the "let me check with the manager" round trip | Enables the M36 **< 2 h quotation turnaround** target |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Pricing becomes a policy, not a folklore** | The company's commercial intent is expressed once, in a governed artefact, rather than transmitted verbally and degraded at each hop |
| **Defensible pricing** | Customer disputes, brand audits and NBR queries are answered with a reproducible derivation, not an assertion |
| **Fairness and trust** | Two customers with the same circumstances receive the same price. This is a reputational asset in a market where inconsistent pricing is the norm |
| **Delegation without loss of control** | Authority bands let branch managers act quickly while keeping the ceiling with the CCO |
| **Anti-corruption control** | Verbal, unrecorded discounting is a known leakage and integrity risk; making every concession named, reasoned and reviewed removes the opportunity |
| **Measurement culture** | Realised-vs-list is the first commercial metric the company will have ever had |
| **Model-ready data** | Elasticity, win/loss and demand models in M26 require priced outcomes with explanations. Without M11 they cannot be trained |

---

## 8. Lifecycle & State Model

M11 owns two lifecycles: the **price book version** and the **price approval request**.

### 8.1 Price Book Version

```
   ┌─────────┐  author a version (copy or new)
   │  DRAFT  │
   └────┬────┘
        │ submit (impact preview generated)
   ┌────▼─────────┐
   │  IN REVIEW   │──── reject ──► DRAFT (reason recorded)
   └────┬─────────┘
        │ approve (approver ≠ author)
   ┌────▼─────────┐
   │  APPROVED    │  awaiting its effective date
   └────┬─────────┘
        │ effective date reached (or immediate activation)
   ┌────▼─────────┐
   │   ACTIVE     │  the engine resolves against this version
   └────┬─────────┘
        │ superseded by a later version / validity ends
   ┌────▼─────────┐
   │  SUPERSEDED  │  retained forever; historical documents resolve against it
   └──────────────┘

   Emergency rollback: ACTIVE ──► SUPERSEDED with immediate reactivation of the
   prior version, requiring CCO approval and generating a mandatory incident record.
```

### 8.2 Price Approval Request

```
   REQUESTED ──► PENDING APPROVAL ──► APPROVED ──► APPLIED (locked to the document)
        │               │
        │               ├── ESCALATED (SLA breach; routed to the next authority)
        │               └── REJECTED ──► document returns to the standard price
        └── WITHDRAWN (by the requester before decision)
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | In Review | All rules validated; no ambiguous precedence; impact preview generated | Pricing Officer |
| In Review | Approved | Approver ≠ author; margin-floor compliance verified across the affected set | CCO or delegate |
| Approved | Active | Effective date reached; cache invalidation confirmed on all nodes | System |
| Active | Superseded | A later approved version becomes active, or validity ends | System |
| Active | Superseded *(emergency)* | CCO approval + incident record | CCO |
| Requested | Pending Approval | Discount or below-floor amount exceeds the requester's band | System |
| Pending Approval | Approved | Approver holds the required band; reason code present | Band-holding role |
| Pending Approval | Escalated | Approval SLA elapsed | System |
| Approved | Applied | Document line still open and unlocked | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-PRC-01 | M11 is the only module permitted to compute or store a customer-facing price or rate | **H** | CTO |
| BRU-PRC-02 | Every resolved price is accompanied by a complete explanation trace | **H** | CCO |
| BRU-PRC-03 | A price quoted to a customer is immutable for its declared validity period | **H** | CCO |
| BRU-PRC-04 | No price may be resolved below the item class's margin floor without a recorded CCO-level approval | **H** | CFO |
| BRU-PRC-05 | Discount authority applies to the *cumulative* discount from all sources, not to each source separately | **H** | CCO |
| BRU-PRC-06 | Discount bands are: ≤10% agent · ≤20% branch manager · ≤35% sales manager · >35% CCO | **H** | CCO |
| BRU-PRC-07 | The proposer of a price change or below-floor discount cannot approve it | **H** | CFO |
| BRU-PRC-08 | An expired price is never extended; a new price is issued | **H** | CCO |
| BRU-PRC-09 | Dynamic pricing may move a price only within the declared corridor around list, never below the margin floor | **H** | CCO |
| BRU-PRC-10 | Dynamic pricing never applies to contract-covered work, warranty work, brand reimbursement or an accepted quotation | **H** | CCO |
| BRU-PRC-11 | Contract negotiated rates override all other price books for that contract's scope and term | **C** | CCO |
| BRU-PRC-12 | Brand reimbursement rate cards are versioned; a claim is valued at the version in force on the service date | **C** | Finance Director |
| BRU-PRC-13 | A discount above the configured threshold requires a reason code from the governed list | **H** | CCO |
| BRU-PRC-14 | The permitted price spread between channels for the same item may not exceed the configured maximum | **S** | CCO |
| BRU-PRC-15 | Price experiments never include contract, warranty, corporate or marketplace-fee pricing | **H** | CCO |
| BRU-PRC-16 | A mass price change requires preview, approval and a scheduled effective date; immediate mass change requires CCO approval | **H** | CCO |
| BRU-PRC-17 | The anonymous public price endpoint never returns cost, margin, rule identity or customer-specific rates | **H** | CTO |
| BRU-PRC-18 | Loyalty benefits are applied by M11 but defined by M10; M11 may not create a loyalty benefit | **H** | CCO |

*Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.price.book` | `fix_price_book` | Price book header | code, name, entity_id, branch_group_id, channel, segment_id, currency_id, precedence, valid_from, valid_to, state, version |
| `fix.price.rule` | `fix_price_rule` | A single priced rule | book_id, item_id, category_id, computation (fixed / markup / formula), value, min_qty, break_type, conditions_json, valid_from, valid_to |
| `fix.rate.card` | `fix_rate_card` | Labour rate card | code, scope (own / brand / contract), brand_id, contract_id, branch_group_id, valid_from, valid_to, version, state |
| `fix.rate.card.line` | `fix_rate_card_line` | Rate per repair level / skill | card_id, repair_level, skill_class_id, delivery_mode, rate_per_hour, rate_basis (SRT / actual), currency_id |
| `fix.price.adjustment` | `fix_price_adjustment` | Premiums and surcharges | code, type (urgency / after-hours / zone / distance / holiday), basis, value, conditions_json |
| `fix.discount.scheme` | `fix_discount_scheme` | Discount definitions | code, type, scope, value, eligibility_json, stackable, max_combined_pct |
| `fix.discount.authority` | `fix_discount_authority` | Authority bands | role_id, max_pct, max_absolute, requires_reason, escalation_role_id |
| `fix.margin.floor` | `fix_margin_floor` | Floors by item class | item_class, branch_group_id, floor_pct, floor_absolute, override_role_id |
| `fix.price.approval` | `fix_price_approval` | Approval requests | document_ref, line_ref, requested_price, standard_price, discount_pct, reason_code, state, requester_id, approver_id, decided_at |
| `fix.price.override.log` | `fix_price_override_log` | Permanent override record | document_ref, original, override, actor_id, approval_id, reason, at |
| `fix.price.lock` | `fix_price_lock` | Locked quoted prices | document_ref, line_ref, price, rule_set_version, locked_at, valid_until |
| `fix.promotion` | `fix_promotion` | Promotional pricing | code, item_scope_json, audience_json, benefit_json, valid_from, valid_to, usage_limit, stack_group |
| `fix.marketplace.fee.schedule` | `fix_marketplace_fee_schedule` | Commission and fee rates | category_id, seller_tier, commission_pct, listing_fee, boost_price_json, valid_from |
| `fix.brand.reimbursement.rate` | `fix_brand_reimbursement_rate` | What brands pay us | brand_id, repair_level, model_class, labour_rate, parts_markup_pct, version, valid_from |
| `fix.price.experiment` | `fix_price_experiment` | A/B price tests | code, hypothesis, item_scope_json, audience_json, variants_json, guardrails_json, state, started_at, ended_at |
| `fix.dynamic.pricing.rule` | `fix_dynamic_pricing_rule` | Dynamic adjustment rules | code, signal (demand / capacity / lead_time / season / inventory), corridor_pct, item_scope_json, exclusions_json, enabled |
| `fix.price.resolution.log` | `fix_price_resolution_log` | Sampled resolution trace store | request_hash, inputs_json, result, trace_json, rule_set_version, at |
| `fix.rule.set.version` | `fix_rule_set_version` | Global rule-set snapshot | version, activated_at, activated_by, content_hash |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.catalogue.item`, `fix.standard.repair.time`, `fix.repair.bom` | M37 | Master data projection |
| `fix.party`, segment, tier, credit status | M33 | Live read |
| `fix.stock.valuation.event` | M15 | Live read — margin floor basis |
| `fix.contract` | M08 | Live read — contract rate applicability |
| `fix.membership`, `fix.voucher` | M10 | Live read and usage validation |
| `fix.tax.code` | M51 | Live read for presentation mode |
| `fix.branch`, `fix.zone`, `fix.working.calendar` | M02 / M30 / M63 | Configuration read |
| `fix.model`, `fix.model` | M26 | Model output projection (W7) |
| `fix.availability` | M55 | Live read (W7 dynamic signal) |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-PRC-01 | Price requested for a document line | Resolve, attach the explanation, evaluate margin floor and discount authority, and set the line's approval state | Return the last known good price flagged as stale; alert the Pricing Officer |
| AUT-PRC-02 | Discount exceeds the requester's band | Create an approval request, route to the band-holding role, notify, and block document progression | Escalate after the SLA; never auto-approve |
| AUT-PRC-03 | Approval SLA elapsed | Escalate to the next authority and notify both parties | Repeat escalation; log |
| AUT-PRC-04 | Price below margin floor | Hard-block, create a CCO approval request with the computed margin attached | — |
| AUT-PRC-05 | Quotation issued | Lock the price with its rule-set version and validity | Block issue; the document cannot be sent without a lock |
| AUT-PRC-06 | Quotation expires | Release the lock and require re-pricing on any revival | — |
| AUT-PRC-07 | Price book version reaches its effective date | Activate, invalidate caches on all nodes, emit `pricing.book_activated` | Hold activation and alert; never activate partially |
| AUT-PRC-08 | Catalogue item discontinued | Flag every price rule referencing it and require disposition before the item's last-order date | Escalate to the Pricing Officer |
| AUT-PRC-09 | Standard repair time re-baselined in M37 | Recompute affected labour prices, produce an impact report, and require review before the new prices go live | Hold the new SRT's price effect; alert CCO |
| AUT-PRC-10 | Standard cost moves beyond the configured tolerance | Flag every item whose margin now sits below floor or below target, and raise a re-pricing task | Escalate to Finance Manager |
| AUT-PRC-11 | Nightly consistency scan | Detect the same item priced beyond the permitted spread across branches or channels and report | Log and retry |
| AUT-PRC-12 | Weekly leakage scan | Produce realised-vs-list and discount-leakage figures by branch, agent and segment; alert on outliers | Log and retry |
| AUT-PRC-13 | Dynamic pricing signal received (W7) | Compute the corridor adjustment, apply guardrails, and record the signal and adjustment on the resolution trace | Apply zero adjustment; log; alert if repeated |
| AUT-PRC-14 | Dynamic pricing guardrail breached (W7) | Disable the offending rule automatically, revert to static pricing, and raise a priority incident | — |
| AUT-PRC-15 | Brand rate card version received | Version, effective-date and notify M09; re-value only claims not yet submitted | Hold and alert the Warranty Officer |

---

## 12. Interfaces

### 12.1 Upstream — M11 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Items, item classes, standard repair times, rBOM, tax class, UoM | Master data projection |
| M33 Party Master | Customer, segment, tier, entity, credit status | REST `GET /api/v1/customer/{id}` |
| M15 Inventory | Standard cost for margin floor and markup schemes | REST |
| M08 Contract | Active contracts and their negotiated rate scope | REST `GET /api/v1/contracts?party_id=` |
| M10 Loyalty | Tier benefits, vouchers, promotion codes and their eligibility | REST + event `loyalty.benefit_changed` |
| M30 Platform Admin | Branches, zones, channels, calendars, currencies | Configuration read |
| M26 AI/ML *(W7)* | Elasticity estimates, demand forecasts, price guidance | Model output projection |
| M02 / M55 *(W7)* | Branch and technician capacity signals | Event projection |
| M36 Quotation | Quotation acceptance and rejection outcomes for win/loss analysis | Event `quotation.decided` |
| M51 Tax | Valid tax classes and presentation rules | REST |

### 12.2 Downstream — M11 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M36 Quotation | Every line price with explanation; discount evaluation; approval state | REST `POST /api/v1/pricing/resolve` |
| M08 Contract | Contract pricing at creation, amendment and renewal; escalation calculations | REST |
| M09 Warranty | Brand reimbursement rates for claim valuation; protection product pricing | REST |
| M39 Subscription | Plan rates, usage rates and change-of-plan pricing | REST |
| M38 E-Commerce | Storefront prices, promotional prices, cart totals | REST + cache with invalidation event |
| M12 Marketplace | Commission, listing fee and boost pricing | REST |
| M13 Rental · M14 Refurbishment | Period rates, deposits, grade-based pricing | REST |
| M01 SRM · M04 Front Desk | Indicative price at intake; final price at completion | REST |
| M20 Receivable | Priced lines with explanation for invoice generation | Via M36 / M39 documents |
| M53 Revenue & Settlement | Commission rates and fee schedules for settlement | REST |
| M40 Partner | Partner and referral commercial rates | REST |
| M25 BID · M26 AIM | Full pricing fact stream: resolutions, overrides, approvals, outcomes | Warehouse extract |
| P01 Customer Portal / App | Anonymous indicative price band | REST `GET /api/v1/pricing/indicative` |
| P04 Corporate Portal | Contract-scoped pricing and bulk price simulation | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `pricing.book_activated` | book id, version, scope, effective_from, content hash | M36, M38, M12, M25 |
| `pricing.rate_card_versioned` | card id, scope, brand/contract, version | M09, M08, M36 |
| `pricing.price_locked` | document ref, line ref, price, rule-set version, valid_until | M36, M20 |
| `pricing.approval_requested` | document ref, requested price, band, requester, approver role | M27, P03 |
| `pricing.approval_decided` | approval id, decision, approver, reason | M36, M25 |
| `pricing.floor_breach_blocked` | document ref, item, computed margin, floor | M25, CFO alerting |
| `pricing.override_applied` | document ref, original, override, actor, reason | M25, audit |
| `pricing.mass_change_applied` | scope, magnitude, affected item count, effective_from | M38, M12, M25 |
| `pricing.dynamic_adjustment_applied` | item, base, adjustment, signal, corridor | M25, M26 |
| `pricing.dynamic_disabled` | rule id, reason, at | M25, incident management |
| `pricing.experiment_concluded` | experiment id, variants, result, decision | M25, M35 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-PRC-01 | Brand partner rate-card publications (17+) | Inbound | Import and version warranty reimbursement rates |
| INT-PRC-02 | Bangladesh Bank / bank FX feed | Inbound | Daily reference rates for multi-currency price books |
| INT-PRC-03 | Corporate website / Next.js platform | Outbound | Publish indicative public prices |
| INT-PRC-04 | Competitor price observation feed *(optional, P3)* | Inbound | Reference-only competitive input |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/pricing/resolve` | POST | Resolve one or many lines with explanation | M36, M38, M12, M01, P03, P04 |
| `/api/v1/pricing/simulate` | POST | Simulate without creating state | P03, P04, P07 |
| `/api/v1/pricing/indicative` | GET | Anonymous indicative price band | P01, website, app |
| `/api/v1/pricing/lock` | POST | Lock a resolved price to a document line | M36, M39 |
| `/api/v1/pricing/lock/{id}` | DELETE | Release a lock on expiry or cancellation | M36 |
| `/api/v1/pricing/discount/evaluate` | POST | Evaluate a proposed discount against authority and floor | M36, P03 |
| `/api/v1/pricing/approvals` | GET/POST | List and decide approval requests | P03, mobile approval |
| `/api/v1/pricing/rate-cards` | GET | Rate cards by scope and date | M09, M08, M36 |
| `/api/v1/pricing/books/{id}/versions` | GET | Version history and diff | P03 |
| `/api/v1/pricing/books/{id}/mass-change` | POST | Preview or apply a mass change | P03 |
| `/api/v1/pricing/explain/{trace_id}` | GET | Retrieve a stored explanation trace | P03, P04, dispute handling |
| `/api/v1/pricing/experiments` | GET/POST | Manage price experiments | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R04 Chief Commercial Officer | C R U D A | All — sole holder of below-floor and >35% authority |
| R03 Chief Financial Officer | R A | All — margin floors, cost basis, exception review |
| R21 Sales Manager | C R U A | Assigned segment — discount authority ≤ 35% |
| R22 Account Manager (Corporate) | R, propose | Assigned accounts — contract rate proposals |
| R06 Branch Manager | R, A | Own branch — discount authority ≤ 20% |
| R08 Service Centre Agent | R, apply | Own branch — discount authority ≤ 10% |
| R24 Marketplace Operations Officer | R U | Marketplace fee schedules only |
| R23 Marketing Manager | C R U | Promotions and campaign prices (subject to approval) |
| R28 Warranty Claims Officer | R | Brand reimbursement rate cards |
| R26 Finance Manager | R A | Margin floors, exception reports, mass change approval |
| R27 Finance Officer | R | Pricing on documents in scope |
| R25 Retail / Refurbishment Officer | R U | Refurbished grade pricing |
| R34 Contact Centre Agent | R, apply | Discount authority ≤ 10% within campaign scope |
| R36 Customer / R37 Corporate Portal User | R | Own applicable prices only, no rules, no cost |
| R38 External Party | R | Own applicable rates only (seller fees, partner commissions) |
| — Pricing Officer *(new position under R04)* | C R U | All rules and books; cannot approve own change |

**Field-level restrictions.** `standard_cost`, `margin_pct`, `floor_pct` and the internal rule
structure are visible only to R01–R05, R17, R21, R22, R26 and R27 (consistent with `05-04` §5).
No external portal ever receives cost, margin or rule identity. `commission_rate` remains
restricted to R03, R04, R24 and R26.

**Segregation of duties.** SOD-14 *(to be registered in `05-04` §6)*: proposing and approving the
same price change or below-floor discount is a hard block. SOD-04 (credit note create/approve)
is unaffected but interacts: a discount refused at quotation must not be granted later as a
credit note — a cross-module control reported jointly by M11 and M20.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Margin waterfall | CCO, CFO, Sales Manager | Monthly | List → realised → net margin by segment, channel, branch and item class, with every leakage component named |
| Realised-vs-list tracker | CCO, Sales Manager, Branch Managers | Weekly | Realised price as % of list, trended by branch, agent and segment |
| Discount leakage report | CCO, CFO | Weekly | Discount value by band, reason code, approver and branch; outliers highlighted |
| Price override exception register | CFO, Quality Manager, auditor | Quarterly (standing) | Every override and below-floor approval with actor, reason and value |
| Price consistency monitor | CCO | Daily | Same item, different price, beyond permitted spread — by branch and channel |
| Approval cycle-time report | Sales Manager, CCO | Weekly | Time from approval request to decision, by band and approver |
| Contract profitability by rate agreement | CCO, CFO, Account Managers | Monthly | Realised margin per contract against its negotiated rates |
| Brand reimbursement adequacy | Finance Director, Warranty Officer | Quarterly | Brand rate card vs actual delivery cost, by brand and repair level |
| Win/loss price analysis | CCO, Sales Manager | Monthly | Quotation outcome correlated with price position and discount level |
| Promotion effectiveness | Marketing Head, CCO | Per campaign | Uplift, margin cost, cannibalisation and attribution |
| Dynamic pricing performance *(W7)* | CCO, CFO | Weekly | Adjustment distribution, uplift vs control, guardrail events, kill-switch activations |
| Price experiment results *(W7)* | CCO | Per experiment | Variant performance with statistical confidence and recommendation |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-C11-01 | Gross margin on paid repair | baseline | +2 pts | **+4 pts** |
| KPI-C11-02 | Price override exceptions as % of transactions | unmeasured | < 10% | **< 5%** |
| KPI-C11-03 | Realised price as % of list | unmeasured | ≥ 92% | **≥ 95%** |
| KPI-C11-04 | Transactions priced below margin floor without approval | unknown | 0 | **0** |
| KPI-C11-05 | Same-item price variance across branches | unmeasured | < 8% | **< 3%** |
| KPI-C11-06 | Discount approval cycle time | n/a | < 4 h | **< 45 min** |
| KPI-C11-07 | Discounts with a recorded reason code | 0% | 90% | **100%** |
| KPI-C11-08 | Dynamic pricing margin uplift on eligible volume *(W7)* | 0 | n/a | **+3–6%** |
| KPI-C11-09 | Price resolution latency p95 | n/a | ≤ 80 ms | **≤ 60 ms** |
| KPI-C11-10 | Prices resolved with a complete explanation trace | n/a | 100% | **100%** |
| KPI-C11-11 | Customer price disputes attributable to inconsistency | unmeasured | −50% | **−85%** |
| KPI-C11-12 | Claims valued at a superseded brand rate | unknown | < 2% | **0%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `product_pricelist`, `account` currency and rounding | 14% |
| L2 | OCA `product_pricelist_supplierinfo`, `sale_order_price_recalculation`, `product_pricelist_revision`, `sale_discount_display_amount` | 16% |
| L5 | `cd_pricing_engine`, `cd_rate_card`, `cd_discount_governance`, `cd_price_experiment`, `cd_dynamic_pricing` | 70% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort | Wave |
|---|---|---|---|:--:|
| CD-C11-01 | `cd_pricing_engine` — resolution engine, access sequences, explanation trace, price lock, rule-set versioning | Odoo module + service | 8 PW | W3 |
| CD-C11-02 | `cd_rate_card` — labour, brand, contract and marketplace rate cards with versioning | Odoo module | 4 PW | W3 |
| CD-C11-03 | `cd_discount_governance` — bands, floors, approval routing, override log, exception reporting | Odoo module | 4 PW | W3 |
| CD-C11-04 | Pricing API, public indicative endpoint, caching and invalidation | Service | 2 PW | W3 |
| CD-C11-05 | `cd_price_experiment` — A/B framework with guardrails and evaluation | Odoo module | 3 PW | W7 |
| CD-C11-06 | `cd_dynamic_pricing` — signal ingestion, corridor engine, guardrails, kill switch | Odoo module + service | 5 PW | W7 |
| | | **Total** | **26 PW** | |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M37 Catalogue | There is nothing to price until items, item classes and standard repair times exist |
| M33 Party Master | Customer, segment and tier determine applicability |
| M15 Inventory | Standard cost is the margin-floor and markup basis |
| M29 Identity · M28 Integration | Authority bands are identity; every consumer calls through the gateway |
| M30 Platform Admin | Branches, zones, channels and currencies must be configured |
| **For W7 only:** M26 AI/ML, M02/M55 capacity, M36 outcome history | Dynamic pricing requires elasticity estimates, capacity signals and at least four quarters of win/loss data |

**M11 must be accepted before M36, M08, M09 and M39 can be accepted**, and before any
storefront or marketplace price is shown to a customer.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch service price sheets (51+ variants) | ~1,200 price points, inconsistent | `fix.price.rule` (after reconciliation to one governed set) | W3 |
| Parts price lists | ~18,000 rows | `fix.price.rule` / markup schemes | W3 |
| Brand partner rate cards (17+, email attachments) | ~400 rate lines | `fix.brand.reimbursement.rate` | W3 |
| Corporate negotiated rates (contracts and emails) | ~150 agreements | `fix.rate.card` scope = contract | W3–W4 |
| AMC/RAMC package prices | ~40 variants | `fix.price.rule` | W3 |
| Historical invoices (for realised-price baseline) | 24 months | Warehouse only, not operational | W3 |

**Migration rule.** Where source price points conflict, the migration does **not** pick one
silently. Every conflict is listed for CCO decision before the price book can be approved.
Establishing the first single governed price set is a commercial decision exercise, not a data
exercise, and the plan must budget for it.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every priced line in every module obtains its price from M11 and nowhere else | Architectural test in CI + schema inspection of all modules |
| AC-02 | The same inputs always produce the same price and the same explanation | Determinism test over 10,000 randomised input sets |
| AC-03 | A quoted price is honoured for its validity period even after a mass price change | Scripted scenario |
| AC-04 | A price below the margin floor cannot be applied by any route, including API and import | Negative test via UI, API and direct ORM call |
| AC-05 | Cumulative discount from all sources triggers the correct authority band | Test matrix across all band boundaries and stacking combinations |
| AC-06 | A branch manager can show a customer a readable explanation of any price within two clicks | Usability demonstration with real branch staff |
| AC-07 | Brand claims are valued at the rate card version in force on the service date | Scripted scenario across a rate-card version boundary |
| AC-08 | Contract negotiated rates take precedence for that contract's scope and term, and lapse at expiry | Scripted scenario |
| AC-09 | The anonymous indicative endpoint exposes no cost, margin, rule or customer-specific data | Security review + response inspection |
| AC-10 | Price resolution meets ≤ 60 ms p95 single-line and ≤ 400 ms p95 for a 100-line basket | Load test report |
| AC-11 | Price book activation invalidates caches on all nodes within 5 seconds | Cluster test |
| AC-12 | Dynamic pricing never moves a price outside its corridor or below floor, and the kill switch reverts instantly *(W7)* | Guardrail test suite + chaos test |
| AC-13 | Dynamic pricing is provably excluded from contract, warranty, corporate and accepted-quotation pricing *(W7)* | Negative test suite |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings | Security review record |

**Definition of done:** all 17 criteria in `02-02` §8 plus the criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the margin floor per item class, and who is empowered to set it — CCO or CFO? | CCO / CFO | W3 build |
| Q-02 | Is a price differential between branch and app permitted at all, and if so what is the maximum spread? | CCO | W3 build |
| Q-03 | Are labour prices charged against standard repair time or actual time when the two diverge materially? The design assumes standard | Ops Director / CCO | W3 build |
| Q-04 | For the 17+ brand partners, are reimbursement rate cards contractually confidential in a way that constrains storage or visibility? | Finance Director / Legal | W3 build |
| Q-05 | Which item classes and customer segments are excluded from dynamic pricing on policy grounds, beyond the hard exclusions already stated? | CCO | W6 (pre-W7 design) |
| Q-06 | Does the company accept price experimentation on retail customers at all, given the trust risk recorded in the category risk register? | CEO / CCO | W6 |
| Q-07 | How are prices to be handled when M65 introduces a second country entity — separate books, or one book with entity scoping? | CTO / CFO | W9 (M65) |

---

## 19. References

**Internal**
`03_Modules/C_Commercial_Pricing_and_Revenue/_CATEGORY_OVERVIEW.md` §4.1, §8, §10 ·
`03_Modules/C_Commercial_Pricing_and_Revenue/M37_Product_and_Service_Catalogue_Management.md` §3 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2, §5 ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-04_Role_Permission_and_Access_Matrix.md` §5, §6, §7 ·
`05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.11, §10.1 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §7 ·
`1000FiX Business Plan` §Pricing Strategy, §Dynamic Pricing ·
`1000FiX_Services_Company_Profile.md` §Brand Partnerships ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Indicative Pricing

**External benchmark**
SAP S/4HANA condition technique — condition tables, access sequences, condition types, pricing procedures ·
SAP Condition Contract Management — negotiated condition agreements ·
Oracle Fusion Pricing Cloud — pricing strategies, segment assignment, matrix rules ·
Microsoft Dynamics 365 price lists and price-level precedence ·
IFS Cloud service rate types by repair level and skill ·
CPQ discount-governance practice (Salesforce CPQ, Oracle CPQ, Conga, DealHub, PROS) — approval routing, floor checks, out-of-policy flagging ·
Price-optimisation practice (PROS, Revology) — margin waterfall, elasticity guidance ·
Odoo 19 `product_pricelist` and OCA pricelist module family

---

*Module M11 · Category C · 1000FiX ERP System v2.0 · CONFIDENTIAL*
