---
id: FIX-ERP2-M14
module_id: M14
module_code: TRF
module_name: Trade-In, Refurbishment & Resale
category: D — Circular & Asset-Based Business
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Retail Operations Head
system_owner: Commercial Squad
priority: P2
wave: W6
---

# M14 — Trade-In, Refurbishment & Resale
### Category D · Code `TRF` · Existing (retained from v2.0)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M14 |
| **Module code** | `TRF` |
| **Category** | D — Circular & Asset-Based Business |
| **Status** | Existing (introduced in v2.0, retained in v2.1) |
| **Priority** | **P2** commercially · **P0** for the provenance and destruction controls |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Retail Operations Head |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `stock`, `mrp` repair basis) · L5 (custom) |
| **Custom modules** | `cd_tradein`, `cd_refurb`, `cd_grading`, `cd_resale` |
| **Requirement range** | FR-TRF-001 … FR-TRF-039 |
| **Requirement count** | 39 |
| **Effort estimate** | 22 person-weeks |
| **Depends on** | **M06 Data Services (hard gate)** · M33 Party Master · M17 Asset Registry · M15 Spare Parts · M31 Workshop · M11 Pricing · M20 Receivable · M09 Warranty · M24 Documents · M26 AI/ML · M03 Logistics |
| **Depended on by** | M38 E-Commerce · M12 Marketplace · M15 Spare Parts (harvested stock) · M18 E-Waste · M09 Warranty · M53 Revenue · M25 Business Intelligence · P01 / P04 portals |

---

## 2. Purpose

M14 is the module where **1000FiX buys a used device, makes it good, and sells it again with a
warranty on it**. It runs the whole chain on one traceable record: the customer's trade-in
request, the indicative and then firm valuation, seller identity and provenance verification,
physical intake, certified data destruction, the refurbishment work order, the QA protocol,
the grade, the price, the listing, the sale, the warranty and any return.

Two things make this a system requirement rather than a workshop practice. The first is
**margin**: a refurbished unit's profit is the difference between what was paid for it and the
sum of everything spent on it, and that sum is invisible without per-unit cost accumulation.
The second is **liability**: the Company sells a device it did not manufacture, with a warranty
it wrote itself, to a buyer who is entitled to know what was done to it — and that device may
still hold somebody else's data.

### Why It Exists

The Business Plan describes the full refurbishment chain — refurbishment, data wiping and
privacy protection, quality assurance testing, resale and distribution, warranty and customer
support. The Company Profile advertises an Exchange Offer. The Service App SOW specifies the
customer-facing trade-in quotation flow in detail. All of it is committed; none of it has a
system.

Run on tally sheets, this business has three failure modes and it will hit all of them:
it will lose money per unit without noticing, it will resell a device that still contains a
customer's data, and it will buy a stolen handset. M14 exists to make each of those
structurally impossible rather than merely discouraged.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Business Plan §Refurbishment and Resale | The committed chain: refurbishment, data wiping and privacy protection, QA testing, resale and distribution, warranty and customer support, environmental rationale |
| Company Profile §Exchange Offer | Trade-in against purchase is an advertised, live offer |
| SOW for 1000FiX Service App | The customer-facing trade-in flow: device details, self-assessed condition, photographs, back-office assessment, firm offer, acceptance |
| Scope Charter §Benefit Register | **BO-14 — build a circular device business**; 12,000 refurbished units/year, 22% margin; base-case benefit **BDT 65 lac/year** |
| Category D Overview §4 | The non-negotiable gate: no refurbishment, no listing, no parts harvesting from a storage device without an M06 certificate |
| Category D Overview §9 | Risk register: resold device holding customer data (**Critical**); handling stolen goods (**Critical**) |
| M06 §12.2 | M14 is a hard-gate consumer of the destruction certificate |
| Module Register (02-02) | M14 `TRF`, P2, W6, Retail Operations Head, 39 requirements, 22 PW |
| **BTRC NEIR — enforced since 16 December 2025** | Every handset on a Bangladeshi network must have its IMEI registered in the National Equipment Identity Register; handsets first attaching after that date must be registered, and unregistered IMEIs are blocked from network service. **This is new since v2.0 was drafted and it changes what a resold handset must carry.** |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Trade-in request intake from portal, app, counter, field and corporate channels |
| 2 | Indicative automated valuation from model, age, declared condition and reference pricing |
| 3 | Back-office assessment producing a firm, time-limited offer |
| 4 | Seller identity verification and provenance recording, including IMEI / serial screening |
| 5 | Physical intake and verification against the declared condition, with offer revision |
| 6 | Settlement to the seller — cash, mobile money, bank transfer, store credit or offset against a purchase |
| 7 | Corporate bulk buy-back with lot pricing and asset-list reconciliation |
| 8 | The destruction gate: no processing without an M06 certificate |
| 9 | Refurbishment work order with standard scope by device class |
| 10 | Diagnostics, repair, parts consumption, cosmetic restoration, software and firmware rebuild |
| 11 | Per-unit cost accumulation: acquisition, parts, labour, overhead, logistics |
| 12 | The published grading standard and its objective criteria |
| 13 | The QA test protocol, including battery and consumable health measurement |
| 14 | Grade assignment with controlled supervisor override |
| 15 | Refurbished stock as a distinct, serialised, grade-and-age-tracked inventory class |
| 16 | Grade-based pricing with ageing markdown and channel-shift rules |
| 17 | Resale listing preparation for e-commerce, retail counter and reseller channels |
| 18 | The refurbished warranty term, its liability provision and its claims feedback loop |
| 19 | The buyer's device history and disclosure report |
| 20 | Returns and post-sale support on refurbished units, feeding quality data back to grading |
| 21 | Harvesting unsellable units into parts stock |
| 22 | Routing failed and valueless units to recycling |
| 23 | Unit economics and refurbishment analytics |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Certified data destruction and the certificate itself** | **M06** Data Services | M14 requires the certificate and cannot proceed without it, but does not perform or issue it. Separating the gate from the gated is the entire point of the control |
| Storefront, cart, checkout and payment | **M38** E-Commerce | M14 supplies the graded unit, its disclosure report and its price; the channel sells it |
| Marketplace listing and seller settlement | **M12** Marketplace | Same boundary, other channel |
| Warranty policy definition, claim adjudication and reserve accounting | **M09** Warranty & Claims | M14 defines the *term* offered on a refurbished grade; M09 administers the policy and the liability |
| Repair execution capacity, bench scheduling and technician assignment | **M31** Workshop / **M02** Field Service | Refurbishment is repair work; it runs on the same benches under the same scheduling |
| Parts issue, stock valuation and reservation | **M15** Spare Parts & Inventory | Harvested parts *enter* M15; M14 produces them but never holds stock |
| Price list construction and approval thresholds | **M11** Pricing | M14 consumes the approved grade-based rate card |
| Payment execution to the seller | **M20** Receivable / **M52** Payable | M14 instructs; Finance pays |
| Store credit and wallet balances | **M10** Loyalty & Rewards | The wallet is one balance across the enterprise |
| Customer identity, NID and KYC verification | **M33** Party Master | M14 asks whether the seller is verified; M33 verifies |
| Asset identity and lifetime history | **M17** Asset Registry | A refurbished unit keeps one enterprise identity through every owner |
| Recycling, partner transfer and disposal certificates | **M18** E-Waste | M14 routes failures out; M18 disposes of them |
| Physical movement and custody | **M03** Logistics | Every intake and every dispatch is a consignment |
| Valuation model training and market price ingestion | **M26** AI/ML Services | M26 provides the model and the feed; **M14 decides the offer** |
| VAT treatment of second-hand goods | **M51** Tax (Bangladesh) | M14 supplies the transaction facts |

### 3.3 Shared Concepts

| Concept | M14's Role | Owning Module |
|---|---|---|
| Destruction certificate | **Consumes as a hard gate** | M06 |
| Asset / serial identity | References; adds refurbishment history | M17 |
| Trade-in offer | **Owns** | M14 |
| Provenance record | **Owns** | M14 |
| Refurbishment work order | **Owns** the order; M31 supplies the bench | M14 / M31 |
| Grading standard | **Owns** | M14 (published via M24) |
| Refurbished unit as stock | **Owns** the grade, age and disclosure; M15 owns the stock record | M14 / M15 |
| Harvested part | Produces | M15 |
| Resale listing | Supplies the unit and its price | M38 / M12 |
| Refurbished warranty | Defines the term | M09 administers |
| Valuation model | Consumes | M26 |
| Seller settlement | Instructs | M20 / M52 / M10 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **R2v3 (SERI) Appendix B — Data Sanitization** | Serial-number-level tracking of data-bearing devices, verified sanitisation methods, documented quality control, and a physical method of distinguishing sanitised from unsanitised devices | **The distinguishing requirement**: sanitised and unsanitised units are physically and systemically segregated, and the system will not let an unsanitised unit onto a refurbishment bench | Nothing — this is the governing practice |
| **R2v3 Appendix C — Test & Repair** | Devices must be functionally verified and accurately graded before resale or redeployment; the facility must hold an accredited QMS (ISO 9001:2015) covering the full scope of test and repair | **The whole shape**: a defined test protocol per device class, functional verification before grading, and grading tied to the QMS. 1000FiX is already ISO 9001:2015 certified, which makes this achievable rather than aspirational | Full R2v3 certification at W6 — adopted as a design target, not a launch prerequisite |
| **Apple Certified Refurbished** | A single certified standard rather than letter grades: full inspection, new battery, new outer shell, original accessories, one-year warranty | **The insight that a *certified* tier outsells a *graded* one.** M14 supports an optional "Certified" tier above Grade A, defined by a replaced battery and a full functional rebuild | Making every unit certified — the economics do not work at Bangladeshi price points |
| **Back Market** | Marketplace-enforced minimum standards, most notably a **minimum 80% battery health** on every phone shipped | **A hard minimum battery-health threshold per grade**, disclosed on the listing and enforced by the QA protocol | Marketplace mechanics — that is M12 |
| **Industry grading practice (Grade A / B / C)** | Grade A: like-new, no notable cosmetic damage. Grade B: light scratches and scuffs, cosmetic only. Grade C: visible wear, fully functional. No single global standard exists; each seller publishes its own | **A published, objective, photographed grading standard** with cosmetic *and* functional criteria per grade. The absence of an industry standard is exactly why ours must be written down and shown to the buyer | Vague adjectives. "Good condition" is not a grade |
| **ITAD buy-back pricing practice** | Buy-back price is the resale estimate less logistics, data destruction, refurbishment and recycling cost, with deductions confirmed before shipment | **The offer formula**: every offer is built from a resale estimate minus explicitly itemised expected costs, so a bad offer is visible as a bad assumption rather than a bad instinct | Post-hoc deduction after intake — the offer must be honest up front, with revision only on verified condition difference |
| **Recommerce pricing engines (e.g. Dipli)** | Residual-value models over tens of thousands of SKUs, grade- and market-specific, repriced from live market data. Smartphones depreciate ~35–50% in year 1, 60–75% by year 2, ~80% by year 3; laptops decline more gradually at 15–20% a year | **Depreciation-curve-based valuation with a market reference feed**, and automatic markdown as stock ages | Buying a commercial price feed at launch — the Bangladeshi second-hand market is not covered by them. We build a local curve from our own transaction history via M26 |
| **Serialised inventory and landed-cost accounting** | Landed cost includes purchase price plus freight, duty, handling; refurbished inventory carries a reserve for estimated refurbishment cost or a write-down to net realisable value | **Per-unit landed cost and a net-realisable-value test at each ageing band** | — |
| **BTRC NEIR (Bangladesh)** | Every handset on a Bangladeshi network must have a registered IMEI; unregistered IMEIs are blocked from network service. Verification available by USSD `*16161#` and through the NEIR portal | **IMEI status verification as a mandatory intake step for every handset**, and a hard block on both purchase and resale of an unregisterable device | — |

**Design position.** Five deliberate differences, four of them more conservative than the
benchmark and one of them more commercially aggressive.

**First, the destruction gate is a state-machine precondition, not a checklist item.** A unit
cannot enter refurbishment, cannot be listed, cannot be harvested for parts and cannot be
recycled until M06 returns `CERTIFIED` for its storage media. The call fails closed. There is
no supervisor override and no "pending certificate" pathway, because the failure mode this
prevents — a resold device carrying a stranger's data — is the single largest latent liability
in the entire ERP.

**Second, provenance is a purchase precondition, and in Bangladesh that now means NEIR.**
Since 16 December 2025 every handset on a Bangladeshi network must carry a registered IMEI.
That changes trade-in from a judgement call into a checkable fact: an unregisterable IMEI is
either grey-market or stolen, and in both cases it is unsellable. The system therefore
verifies IMEI status at intake, records verified seller identity from M33, and blocks payment
on any device that fails. A device the Company cannot lawfully resell is a device it must not
buy.

**Third, the grade is a computed output of the QA protocol, not an opinion.** The grade is
derived from measured criteria — cosmetic scores per surface, functional test results, battery
health percentage. A supervisor may override, but the override is recorded, justified,
attributed, and reported monthly. Grading drift is how refurbishment businesses quietly
destroy their return rate.

**Fourth, disclosure is complete and buyer-facing.** Every refurbished unit ships with a device
history report: what grade, what was replaced, what the test results were, what the battery
health is, and what the warranty covers. This is unusual in the local market and it is a
deliberate competitive position — the Company is asking a buyer to trust a used device, and
the only currency that buys that trust is evidence.

**Fifth — the aggressive one — refurbishment runs on the existing repair network.** Competitors
in recommerce must build a refurbishment operation. 1000FiX already has one: benches,
technicians, parts, diagnostics, an ISO 9001 quality system and a warranty capability. M14 is
therefore deliberately thin on repair mechanics and thick on valuation, grading, disclosure
and unit economics — the parts the Company does *not* already have.

---

## 5. Functional Areas & Features

### 5.1 Trade-In & Acquisition

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-001 | Trade-in request | Accept a trade-in request from portal, app, counter, field or corporate channel with device details, condition self-assessment, photographs and warranty status | P2 | L5 |
| FR-TRF-002 | Automated indicative valuation | Produce an indicative price from model, age, declared condition and market reference data, presented as indicative and subject to verification | P2 | L5 |
| FR-TRF-003 | Back-office assessment | Route the request to the assessment team, which reviews evidence and issues a firm offer | P2 | L5 |
| FR-TRF-004 | Offer & acceptance | Present the firm offer with an explicit validity period and capture the customer's acceptance or decline | P2 | L5 |
| FR-TRF-005 | Physical intake & verification | Verify the device on receipt against the declared condition and revise or withdraw the offer with photographic evidence where it differs | P2 | L5 |
| FR-TRF-006 | Ownership & provenance | Verify seller identity through M33, record a provenance chain, and screen the IMEI or serial against the **BTRC NEIR** register and available blocklists | **P0** | L5 |
| FR-TRF-007 | Payment to seller | Instruct settlement by mobile money, bank transfer, cash or store credit, recorded against the verified party | P2 | L5 |
| FR-TRF-008 | Exchange against purchase | Offset the trade-in value against the purchase of another device, a service or a subscription | P2 | L5 |
| FR-TRF-009 | Bulk corporate buy-back | Handle corporate fleet buy-backs with lot pricing, per-unit reconciliation against the client's declared asset list, and per-unit certification | P2 | L5 |
| FR-TRF-031 | Trade-in mobile experience | Guide a customer through model selection, condition questions, forced photograph capture and instant indicative pricing in the app | P2 | L5 |
| FR-TRF-032 | Market price reference | Ingest and maintain reference prices for new and used devices, and derive a local depreciation curve per model family from the Company's own transaction history | P3 | L5 |
| FR-TRF-033 | Offer economics guardrail | Build every offer as resale estimate **minus** expected refurbishment, logistics, destruction and channel cost, and block an offer whose modelled margin falls below the category floor without approval | P2 | L5 |

### 5.2 Intake Control & The Destruction Gate

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-011 | Data destruction gate | Require a valid M06 certificate of destruction for every data-bearing unit before refurbishment, listing, harvesting or recycling may begin, and **block progression without it** | **P0** | L5 |
| FR-TRF-034 | Sanitised / unsanitised segregation | Maintain a physical and systemic distinction between sanitised and unsanitised units, with distinct storage locations and a system block on moving an unsanitised unit to a refurbishment bench | **P0** | L5 |
| FR-TRF-035 | Accessory and completeness capture | Record what arrived with the unit — charger, box, accessories, documentation — as it affects both the offer and the resale price | P3 | L5 |

### 5.3 Refurbishment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-010 | Refurbishment work order | Create a work order with a standard scope by device class, scheduled onto the M31 workshop bench | P2 | L5 |
| FR-TRF-012 | Diagnostics & repair | Run full diagnostics, repair identified faults and replace consumables, consuming parts issued from M15 | P2 | L5 |
| FR-TRF-013 | Cosmetic restoration | Record cleaning, panel or shell replacement, screen polishing and other cosmetic work with before-and-after evidence | P2 | L5 |
| FR-TRF-014 | Software & firmware rebuild | Reinstall the operating system, apply firmware updates, remove activation locks with proof of ownership, and verify licensing | P2 | L5 |
| FR-TRF-015 | Per-unit cost accumulation | Accumulate acquisition price, parts, labour at the standard rate, logistics and allocated overhead per unit to produce a landed cost | P2 | L5 |
| FR-TRF-036 | Rework control | Where a unit fails QA and returns to the bench, record the rework, its cause and its cost separately from first-pass work | P2 | L5 |

### 5.4 Grading & Quality Assurance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-016 | Grading standard | Maintain a published, versioned grading standard — Certified / A / B / C / Parts-only — with objective cosmetic and functional criteria and reference photographs per grade | P2 | L5 |
| FR-TRF-017 | QA test protocol | Run the full protocol per device class — hardware components, ports, display, camera, connectivity, thermal, software functionality — and record every result | P2 | L5 |
| FR-TRF-018 | Battery & consumable health | Measure and record battery health as a percentage, and other wear indicators, enforcing the per-grade minimum and disclosing the figure at point of sale | P2 | L5 |
| FR-TRF-019 | Grade assignment | Compute the grade from the QA results; permit supervisor override only with a recorded justification, attribution and monthly reporting of override rates | P2 | L5 |
| FR-TRF-020 | Rejection routing | Route units that fail refurbishment to parts harvesting or to M18 recycling, writing off the accumulated cost with approval | P2 | L5 |
| FR-TRF-037 | Grading audit sample | Re-grade a random sample of graded units independently each period and report the variance as a quality measure | P3 | L5 |

### 5.5 Resale, Warranty & Disclosure

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-021 | Resale listing | Prepare a listing for the e-commerce channel, retail counter or authorised reseller, carrying the grade, disclosed condition, battery health, warranty and photographs of the actual unit | P2 | L5 |
| FR-TRF-022 | Grade-based pricing | Price by model, grade, specification and market reference from an approved M11 rate card, with automatic ageing markdown | P2 | L5 |
| FR-TRF-023 | Refurbished warranty | Apply the defined warranty term by grade, register it with M09, and track the resulting liability provision per unit sold | **P1** | L5 |
| FR-TRF-024 | Device history & disclosure report | Issue the buyer a report covering refurbishment date, work performed, parts replaced, grade, QA results, battery health, destruction certificate reference and warranty terms | P2 | L5 |
| FR-TRF-025 | Reseller & distribution channel | Manage sales through partner resellers with allocation, channel pricing and settlement | P3 | L5 |
| FR-TRF-026 | Return & post-sale support | Handle returns and warranty claims on refurbished units, and feed the failure data back into the grading and QA protocol | P2 | L5 |
| FR-TRF-038 | NEIR resale compliance | Confirm the handset's IMEI registration status before listing, and refuse to list a handset that cannot be lawfully activated on a Bangladeshi network | **P0** | L5 |

### 5.6 Inventory, Economics & Circular Routing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-TRF-027 | Refurbished inventory | Track refurbished stock as a distinct, serialised inventory class in M15, segmented by grade, model and age | P2 | L5 |
| FR-TRF-028 | Unit economics | Report acquisition cost, refurbishment cost, sale price, channel cost, warranty provision and net margin per unit, per model and per grade | P2 | L5 |
| FR-TRF-029 | Ageing & markdown | Age refurbished stock in bands, trigger markdown or channel-shift rules automatically, and apply a net-realisable-value test at each band | P2 | L5 |
| FR-TRF-030 | Harvest for parts | Convert unsellable units into harvested parts, adding them to M15 with the harvested classification, cost basis and source-unit traceability | P2 | L5 |
| FR-TRF-039 | Refurbishment analytics | Report yield, cycle time, cost per unit, margin, return rate, override rate, ageing profile and channel performance | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Fail-closed destruction gate** | The M06 certificate check is synchronous and blocks on any response other than `CERTIFIED`, including timeout and service unavailability |
| T-02 | **Serial-bound everything** | Every valuation, offer, cost line, test result, grade, listing, sale, warranty and return binds to one serial or IMEI. There is no model-level shortcut anywhere in the module |
| T-03 | **IMEI / NEIR verification service** | An abstracted verification service records the checked identifier, the response, the source and the timestamp, so a purchase decision is reconstructible years later |
| T-04 | **Immutable provenance record** | Seller identity, declaration, evidence and verification results are written once and cannot be amended; corrections are appended |
| T-05 | **Cost accumulation integrity** | Per-unit cost is the sum of posted transactions only — parts issued from M15, labour booked in M31, logistics from M03. No manual cost entry path exists |
| T-06 | **Deterministic grading** | The grade function is versioned; re-running it on stored QA results reproduces the same grade, and the standard version is stamped on every graded unit |
| T-07 | **Override attribution** | Every grade override records actor, prior grade, new grade, justification and timestamp, and cannot be made by the technician who ran the QA |
| T-08 | **Disclosure generation** | The device history report is generated from the record, not authored — no free-text path can overstate condition |
| T-09 | **Segregated storage enforcement** | Unsanitised units are held in a distinct stock location; a move to a refurbishment location is rejected without a certificate |
| T-10 | **Warranty provision hook** | Every sale publishes a provision event to M09 / M19 carrying grade, term and modelled failure rate, so the liability is booked at sale, not at claim |
| T-11 | **Valuation model interface** | Valuation calls M26 for a modelled price and records the model version and inputs; if M26 is unavailable, the module falls back to the last published price table and flags the offer |
| T-12 | **Performance** | Indicative valuation ≤ 2 s; gate check ≤ 200 ms; disclosure report generation ≤ 3 s; grading computation ≤ 1 s |
| T-13 | **Evidence retention** | Intake photographs, QA results, grading evidence and disclosure reports are retained for the warranty term plus three years |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M14 |
|---|---|---|
| **Customer trading in a device** | Gets a number from a counter clerk with no explanation | Gets an indicative price in the app, a firm offer with validity, and a clear reason if it changes at intake |
| **Assessment officer** | Values by memory and market feel | Values from a model, a curve and an explicit cost build-up, with a margin guardrail |
| **Counter staff** | Takes the device on trust | Cannot complete a purchase without verified seller identity and an IMEI check |
| **Refurbishment technician** | Assumes somebody wiped it | Cannot get the unit onto the bench until the certificate exists |
| **QA technician** | Judges condition by eye | Runs a protocol, records results, and the grade computes itself |
| **Retail Operations Head** | Knows total refurbishment revenue, not per-unit margin | Sees acquisition, cost, price and margin per unit, model and grade — and which models to stop buying |
| **Buyer of a refurbished unit** | Told "refurbished, good condition" | Receives a device history report, a battery health figure, a grade against a published standard and a warranty |
| **Warranty Claims Officer** | Handles refurbished claims with no build history | Opens the unit's full refurbishment record and sees exactly what was replaced |
| **Quality Manager** | Cannot evidence test and repair for ISO or R2v3 | Has a documented protocol, records per unit and a grading audit sample |
| **Finance Manager** | Refurbished stock valued by guess | Landed cost per unit, ageing bands, NRV test and a booked warranty provision |
| **CFO** | Carries an unquantified data and stolen-goods exposure | Carries two hard, evidenced controls and can say so to an auditor or a regulator |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Refurbishment & resale margin** | A traceable circular business with per-unit economics and controlled grading | **BDT 65 lac/year** base case (38 conservative · 96 upside) — Scope Charter BO-14 |
| **Volume** | Trade-in intake through app, counter and corporate channels feeding a graded resale pipeline | **12,000 refurbished units/year** by W8 (KPI-078) |
| **Yield protection** | Standard scope, rework control and cause analysis raise the proportion of intake that becomes sellable | Refurbishment yield **> 88%** (KPI-077) |
| **Margin protection** | The offer guardrail refuses to buy at a price that cannot make the category margin floor | **> 22%** gross margin per refurbished unit |
| **Return-rate reduction** | Objective grading, enforced battery minimums and honest disclosure cut post-sale disputes | Refurbished return rate **< 4%** |
| **Working-capital release** | Ageing bands and automatic markdown stop capital dying in unsold stock | Stock ageing beyond 90 days **< 12%** |
| **Trade-in as an acquisition channel** | The Exchange Offer converts a trade-in into a new-device or service sale at the same visit | Feeds M38, M12, M08 pipelines; measurable attach rate |
| **Parts cost reduction** | Harvested components from unsellable units enter M15 at a fraction of purchase cost | Reduces parts spend; feeds M15's refurbished/harvested classification |
| **Corporate buy-back contracts** | Reconciled, per-unit-certified fleet buy-backs are saleable to every corporate client | New revenue line, paired with M06 bulk decommissioning |
| **Avoided loss** | Not buying a stolen or unregisterable handset avoids both the write-off and the legal exposure | Risk avoidance; each avoided incident exceeds a month of category margin |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Makes the environmental claim true** | The Business Plan justifies refurbishment on environmental grounds. With unit-level data, that becomes a measurable diversion figure in M18 rather than a paragraph |
| **Protects the brand at its most exposed point** | Selling used hardware under the 1000FiX name puts the brand behind somebody else's device. Grading, disclosure and warranty are what make that defensible |
| **Criminal-exposure control** | Verified identity plus NEIR screening is a documented, auditable defence against a handling-stolen-goods allegation |
| **R2v3 and ISO readiness** | The test-and-repair protocol, the QMS linkage and the sanitisation segregation are the substance of R2v3 Appendix B and C — this module makes future certification a documentation exercise rather than a rebuild |
| **Consumer trust in a low-trust market** | The Bangladeshi second-hand device market runs on personal trust and has no published standards. A company that publishes one, and evidences it per unit, occupies ground nobody else is standing on |
| **Technician skill development** | A defined QA protocol turns refurbishment from tacit craft into a trainable, certifiable competency through M22 |
| **Data for pricing everything else** | Every refurbished sale is a real observation of what a used device is worth in Bangladesh — the only such dataset the Company will ever own, and the basis of every future trade-in offer |

---

## 8. Lifecycle & State Models

### 8.1 Trade-In Request → Refurbished Unit → Sale

```
   ┌──────────────────┐
   │  REQUEST RAISED  │  portal · app · counter · field · corporate
   └────────┬─────────┘
            │ model, age, declared condition, photographs
   ┌────────▼─────────┐
   │ INDICATIVE VALUE │  M26 model + local depreciation curve
   └────────┬─────────┘
   ┌────────▼─────────┐
   │    ASSESSED      │  back-office review · cost build-up · margin guardrail
   └────────┬─────────┘
   ┌────────▼─────────┐   declined / expired
   │  OFFER ISSUED    │────────────────────► CLOSED — NO DEAL
   └────────┬─────────┘
            │ accepted
   ┌────────▼─────────┐
   │  PHYSICAL INTAKE │  condition verified against declaration
   └────────┬─────────┘
            │                              condition differs materially
            │                       ┌──────────────────────────────┐
            │                       │  OFFER REVISED / WITHDRAWN   │
            │                       │  evidence recorded · device  │
            │                       │  returned if declined        │
            │                       └──────────────────────────────┘
   ┌────────▼──────────────┐
   │ PROVENANCE VERIFIED   │  seller identity (M33) · IMEI / NEIR · blocklist
   └────────┬──────────────┘
            │ fail ─────────────────► REJECTED — NOT PURCHASED (recorded, reported)
   ┌────────▼─────────┐
   │  PURCHASED       │  settlement instructed · asset identity created in M17
   └────────┬─────────┘
   ┌────────▼──────────────────────────┐
   │  AWAITING DATA DESTRUCTION        │  unsanitised storage location
   │  ✖ cannot move to a bench         │  M06 wipe request raised automatically
   └────────┬──────────────────────────┘
            │ M06 returns CERTIFIED        ◄── the gate · fails closed · no override
   ┌────────▼─────────┐
   │  IN REFURBISHMENT│  diagnostics · repair · cosmetic · software · cost accrual
   └────────┬─────────┘
   ┌────────▼─────────┐   fail → rework (recorded separately) ──┐
   │       QA         │◄─────────────────────────────────────────┘
   └────────┬─────────┘
            │ pass                                   │ unrecoverable
   ┌────────▼─────────┐                       ┌──────▼──────────┐
   │     GRADED       │  Certified / A / B / C│  PARTS-ONLY     │
   └────────┬─────────┘                       └──────┬──────────┘
            │                                        │
   ┌────────▼─────────┐                       ┌──────▼──────────┐   no usable parts
   │     LISTED       │  disclosure report    │  HARVESTED      │──────────────────►
   │  (M38 / M12 /    │  NEIR check for       │  → M15 stock    │   M18 RECYCLE
   │   counter)       │  handsets             └─────────────────┘
   └────────┬─────────┘
            │ sold                          │ ages past band
   ┌────────▼─────────┐              ┌──────▼──────────┐
   │      SOLD        │              │  MARKED DOWN /  │
   │  warranty active │              │  CHANNEL SHIFT  │
   │  provision booked│              └─────────────────┘
   └────────┬─────────┘
            │ returned or claimed
   ┌────────▼─────────┐
   │ RETURN / CLAIM   │──► re-refurbish and re-grade · or harvest · feedback to QA
   └──────────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Assessed | Offer Issued | Modelled margin ≥ category floor, or approved exception | Assessment officer |
| Offer Issued | Physical Intake | Customer acceptance within validity | Customer |
| Physical Intake | Provenance Verified | Condition verification complete with evidence | Intake officer |
| Provenance Verified | Purchased | **Verified seller identity AND IMEI/serial screening passed** | Intake officer |
| Purchased | Awaiting Destruction | Automatic on purchase for any data-bearing unit | System |
| Awaiting Destruction | In Refurbishment | **M06 returns `CERTIFIED` for the unit's media** | System — no human override |
| In Refurbishment | QA | Work order scope complete; all costs posted | Technician |
| QA | Graded | All mandatory tests recorded; battery health meets the grade minimum | System (computed) |
| Graded | Listed | Price from approved rate card; disclosure report generated; **NEIR status confirmed for handsets** | Retail Operations |
| QA | Parts-Only | Unrecoverable fault, or cost-to-complete exceeds resale estimate | Supervisor + approval |
| Parts-Only | Harvested | **M06 certificate present for any storage device** | Technician |
| Harvested | Recycled | No further usable component | Technician |
| Listed | Sold | Channel completes the sale | M38 / M12 / counter |
| Sold | Return / Claim | Within return window or warranty term | Customer |

### 8.2 The Gate, Stated Plainly

> **No unit moves from `PURCHASED` to any downstream state without a valid M06 certificate of
> destruction bound to its media serial.**

| Blocked Transition | Enforced By | Bypass |
|---|---|---|
| Purchased → In Refurbishment | M14 state machine | **None** |
| Graded → Listed | M14 state machine | **None** |
| Parts-Only → Harvested (storage devices) | M14 state machine | **None** |
| Any → routed to M18 | M14 state machine | **None** |

When M06 is unreachable, the gate returns *blocked*, not *allowed*. Units queue; they do not
proceed.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-TRF-01 | **No unit enters refurbishment without a valid M06 certificate of destruction for its media** | **H** | Quality Manager |
| BRU-TRF-02 | **No unit is listed or sold without a valid M06 certificate** | **H** | Quality Manager |
| BRU-TRF-03 | No storage device is harvested for parts without a valid M06 certificate | **H** | Quality Manager |
| BRU-TRF-04 | Unsanitised units are held in a segregated location and cannot be moved to a refurbishment location | **H** | Retail Operations Head |
| BRU-TRF-05 | No device is purchased without a verified seller identity in M33 | **H** | Retail Operations Head |
| BRU-TRF-06 | No handset is purchased or listed where the IMEI fails NEIR verification or appears on a blocklist | **H** | Retail Operations Head / Legal |
| BRU-TRF-07 | A rejected-provenance intake is recorded and reported monthly, and the device is not retained | **H** | Legal |
| BRU-TRF-08 | An offer is valid only for its stated period and cannot be honoured after expiry without re-assessment | **H** | Retail Operations Head |
| BRU-TRF-09 | An offer may be revised at intake only where the verified condition differs from the declaration, with photographic evidence | **H** | Retail Operations Head |
| BRU-TRF-10 | Every offer is built as resale estimate minus expected cost; an offer below the category margin floor requires approval | **C** / **A** | Retail Operations Head |
| BRU-TRF-11 | Per-unit cost is derived only from posted transactions; no manual cost entry is permitted | **H** | Finance Manager |
| BRU-TRF-12 | The grade is computed from the QA results against the published standard version in force | **C** | Quality Manager |
| BRU-TRF-13 | A grade override requires a recorded justification and cannot be made by the technician who ran the QA | **A** | Quality Manager |
| BRU-TRF-14 | A unit whose battery health falls below the grade minimum cannot carry that grade; either the battery is replaced or the grade drops | **H** | Quality Manager |
| BRU-TRF-15 | Every listed unit carries a device history and disclosure report generated from its record | **H** | Retail Operations Head |
| BRU-TRF-16 | Refurbished pricing comes from an approved M11 rate card; ad-hoc pricing is not permitted | **H** | Chief Commercial Officer |
| BRU-TRF-17 | Every sale books a warranty provision to M09 / M19 at the point of sale | **H** | CFO |
| BRU-TRF-18 | Refurbished stock is valued at the lower of landed cost and net realisable value, tested at each ageing band | **C** | Finance Manager |
| BRU-TRF-19 | Write-off of accumulated cost on a rejected unit requires approval above the supervisor | **A** | Finance Manager |
| BRU-TRF-20 | Harvested parts enter M15 with the harvested classification, a defined cost basis and traceability to the source unit | **H** | Inventory Manager |
| BRU-TRF-21 | A refurbished unit keeps the same M17 asset identity through every owner and every cycle | **H** | Asset Manager |
| BRU-TRF-22 | Activation-lock removal requires documented proof of ownership from the seller | **H** | Retail Operations Head |
| BRU-TRF-23 | A corporate bulk buy-back is not closed until every declared asset is reconciled to an intake, a certificate or a documented exception | **H** | Retail Operations Head |
| BRU-TRF-24 | Returns and warranty failures on refurbished units are analysed against the grading standard each period | **S** | Quality Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.tradein.request` | `fix_tradein_request` | The customer's request | name, partner_id, channel, device_model_id, declared_age, declared_condition, declared_faults, photo_ids, warranty_status, state, created_at |
| `fix.tradein.valuation` | `fix_tradein_valuation` | Modelled and assessed value | request_id, model_version, reference_price, depreciation_factor, condition_factor, expected_refurb_cost, expected_logistics_cost, expected_channel_cost, modelled_margin, indicative_value, assessed_value, assessor_id |
| `fix.tradein.offer` | `fix_tradein_offer` | The firm offer | request_id, amount, settlement_options, valid_until, state, accepted_at, revised_from_id, revision_reason, revision_evidence_ids |
| `fix.provenance.record` | `fix_provenance_record` | Purchase legitimacy evidence | offer_id, seller_party_id, identity_verification_ref, identifier_type (IMEI / serial), identifier, neir_status, neir_checked_at, blocklist_result, declaration_ref, outcome, immutable |
| `fix.refurb.unit` | `fix_refurb_unit` | The unit through its whole circular life | asset_id (M17), source (trade-in / rental retirement / e-waste triage / corporate buy-back), source_ref, acquisition_cost, state, destruction_cert_ref, grade, grading_standard_version, battery_health_pct, landed_cost, listed_price, sold_at, cycle_count |
| `fix.refurb.order` | `fix_refurb_order` | The work order | refurb_unit_id, device_class, standard_scope_id, workshop_order_ref (M31), started_at, completed_at, rework_count, state |
| `fix.refurb.cost.line` | `fix_refurb_cost_line` | Per-unit cost accumulation | refurb_order_id, cost_type (acquisition / part / labour / logistics / overhead / destruction), source_transaction_ref, quantity, amount, posted_at |
| `fix.grading.standard` | `fix_grading_standard` | The published standard | version, grade_code, cosmetic_criteria, functional_criteria, battery_minimum_pct, reference_photo_ids, published_at, superseded_at |
| `fix.qa.test.result` | `fix_qa_test_result` | Every measured result | refurb_unit_id, protocol_version, test_code, expected, measured, outcome, operator_id, tested_at, equipment_ref |
| `fix.grading.result` | `fix_grading_result` | The computed grade and any override | refurb_unit_id, computed_grade, standard_version, override_grade, override_reason, override_by, override_at, audit_sample_flag, audit_variance |
| `fix.resale.listing` | `fix_resale_listing` | Channel-facing listing | refurb_unit_id, channel (ecommerce / counter / reseller / marketplace), price, rate_card_ref, disclosure_report_id, neir_confirmed, listed_at, aged_band, markdown_applied, state |
| `fix.disclosure.report` | `fix_disclosure_report` | What the buyer is told | refurb_unit_id, grade, work_performed, parts_replaced, qa_summary, battery_health_pct, destruction_cert_ref, warranty_terms, generated_at, document_id (M24) |
| `fix.refurb.warranty` | `fix_refurb_warranty` | Term offered and liability booked | refurb_unit_id, sale_ref, grade, term_months, coverage_scope, policy_ref (M09), provision_amount, provision_posted_at |
| `fix.harvest.record` | `fix_harvest_record` | Unit dismantled into parts | refurb_unit_id, destruction_cert_ref, harvested_at, operator_id, part_lines (part_id, condition, cost_basis, stock_move_ref), residual_routed_to |
| `fix.bulk.buyback` | `fix_bulk_buyback` | Corporate fleet purchase | partner_id, contract_ref, declared_asset_count, lot_price_basis, reconciled_count, exception_lines, state, closed_at |
| `fix.market.reference` | `fix_market_reference` | Price reference and local curve | device_model_id, new_price, used_reference_price, source, observed_at, local_curve_points, curve_updated_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.destruction.certificate` | **M06** | **Synchronous gate check by media serial — fails closed** |
| `fix.asset` | M17 / M49 | Create and maintain identity through every cycle |
| `fix.party` | M33 | Seller identity and verification status |
| `fix.stock.quant` / `fix.part.item` | M15 / M37 | Refurbished stock and harvested parts |
| `fix.repair.order` | M31 | Bench execution and labour booking |
| `fix.rate.card` | M11 | Approved grade-based resale pricing |
| `fix.protection.policy` | M09 | Refurbished warranty administration |
| `fix.consignment` | M03 | Intake and dispatch movement |
| `fix.document` | M24 | Standards, reports, certificates, evidence |
| `fix.model.version` | M26 | Valuation model and residual-value curve |
| `fix.wallet` | M10 | Store-credit settlement |
| `fix.billable.event` | M20 | Seller settlement and sale posting |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-TRF-01 | Trade-in request submitted | Call M26 for an indicative value; present it as indicative; queue for back-office assessment | Fall back to the last published price table and flag the offer for manual review |
| AUT-TRF-02 | Assessment completed | Issue the firm offer with validity; notify the customer through their preferred channel | Manual issue task; escalate at 24 h |
| AUT-TRF-03 | Offer accepted | Book the intake appointment or raise the collection consignment in M03 | Manual booking task |
| AUT-TRF-04 | Offer validity expires | Lapse the offer; notify the customer; retain the valuation for re-assessment | Log; do not silently honour an expired price |
| AUT-TRF-05 | Physical intake recorded | Compare verified condition to the declaration; where materially different, generate a revision proposal with the evidence attached | Route to supervisor |
| AUT-TRF-06 | Intake of a handset | Run IMEI verification against NEIR and blocklists; record the result immutably | **Block purchase** — no verification, no purchase |
| AUT-TRF-07 | Provenance verification fails | Refuse the purchase, record the case, notify Legal, do not retain the device | Escalate immediately |
| AUT-TRF-08 | Purchase completed | Create the M17 asset identity; instruct settlement; move the unit to the unsanitised location; **raise the M06 wipe request automatically** | Unit remains blocked; alert Retail Operations Head |
| AUT-TRF-09 | M06 publishes `wipe.certified` | Release the unit from the gate; open the refurbishment work order with the standard scope for its class | Unit stays blocked; retry the gate check |
| AUT-TRF-10 | M06 publishes `wipe.failed` | Hold the unit; route to physical destruction; block every downstream transition permanently for that media | Escalate to Quality Manager |
| AUT-TRF-11 | Refurbishment work order completed | Schedule the QA protocol for the device class | Manual scheduling |
| AUT-TRF-12 | QA results recorded | Compute the grade against the standard in force; apply the battery-health minimum; publish the result | Hold ungraded; alert supervisor |
| AUT-TRF-13 | QA fails | Route to rework with cause recorded, or to Parts-Only where cost-to-complete exceeds resale estimate | Route to supervisor decision |
| AUT-TRF-14 | Grade assigned | Generate the disclosure report; price from the approved rate card; prepare the channel listing | Manual listing task |
| AUT-TRF-15 | Listing prepared for a handset | Re-confirm NEIR status before publication | **Block publication** |
| AUT-TRF-16 | Unit sold | Register the warranty with M09; post the provision; publish the disclosure report to the buyer; close the unit's cost record | Escalate to Finance — an unprovisioned sale is a control failure |
| AUT-TRF-17 | Stock crosses an ageing band | Apply the markdown or channel-shift rule; run the net-realisable-value test; notify Retail Operations | Log to the ageing dashboard |
| AUT-TRF-18 | Refurbished unit returned or a warranty claim raised | Open the case with the unit's full build history attached; feed the failure code back to the grading analysis | Manual attachment |
| AUT-TRF-19 | Monthly | Report grade override rate by supervisor, and re-grade a random audit sample | Log for the quality review |
| AUT-TRF-20 | Harvest completed | Add parts to M15 with harvested classification and source traceability; route the residual to M18 | Block harvest completion without a stock destination |
| AUT-TRF-21 | Rental retirement received from M13 | Create the refurb unit with source = rental retirement, carrying its full service and condition history | Manual creation with alert |
| AUT-TRF-22 | Corporate bulk buy-back lot received | Reconcile every declared asset to an intake; list exceptions; block closure until each is resolved | Keep the buy-back open |

---

## 12. Interfaces

### 12.1 Upstream — M14 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M06 Data Services** | **Destruction certificate — hard gate** | **Synchronous REST, fails closed** + `wipe.certified` / `wipe.failed` events |
| M33 Party Master | Seller identity, NID verification status, corporate hierarchy | REST |
| M17 Asset Registry | Asset identity creation and lifetime history | REST + event |
| M26 AI/ML Services | Valuation model, residual-value curve, condition scoring from photographs | REST |
| M15 Spare Parts | Parts issue for refurbishment; harvested-part stock destination | Event + command |
| M31 Workshop | Bench scheduling, labour booking, repair outcome | Event |
| M11 Pricing | Approved grade-based resale rate cards | REST |
| M03 Logistics | Intake collection and dispatch consignments | Event |
| M13 Rental | Retired fleet units routed for refurbishment | Command |
| M18 E-Waste | Triaged units assessed as refurbishable | Command |
| M10 Loyalty | Store-credit wallet balance for settlement | REST |
| M24 Documents | Grading standard, certificates, evidence retention | Command |
| M29 Identity | Roles, approvals, override attribution | Service |

### 12.2 Downstream — M14 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M38 E-Commerce | Graded units, prices, disclosure reports, availability | Events + REST |
| M12 Marketplace | Refurbished listings for the marketplace channel | Events + REST |
| M15 Spare Parts | Harvested parts with classification, cost basis and traceability | Command |
| M09 Warranty | Refurbished warranty registration and provision basis | Command + event |
| M18 E-Waste | Units with no resale or parts value | Command |
| M20 Receivable / M52 Payable | Seller settlement instructions; sale postings | Events |
| M19 / M53 Finance | Landed cost, stock valuation, NRV adjustments, warranty provision | Events |
| M17 Asset Registry | Lifecycle state through refurbishment, sale and re-entry | Events |
| M23 Quality | QA failures, rework causes, override rates, audit variance | Events |
| M60 GRC | Rejected-provenance cases and NEIR failures | Events |
| M25 Business Intelligence | Yield, cycle time, cost, margin, return rate, ageing | Warehouse extract |
| P01 Customer Portal | Trade-in request, offer, acceptance, status, disclosure report | REST |
| P04 Corporate Portal | Bulk buy-back reconciliation and per-unit certification | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `tradein.requested` | request, party, model, declared condition | M25, M27 |
| `tradein.offer_issued` | request, amount, validity | M27, P01 |
| `tradein.offer_accepted` | offer, settlement option | M03, M20 |
| `tradein.provenance_rejected` | identifier, reason, party | **M60**, Legal, M25 |
| `tradein.purchased` | unit, asset identity, acquisition cost | M17, M06, M52 |
| `refurb.gate_blocked` | unit, media serial, reason | M23, Retail Operations |
| `refurb.started` | unit, work order, standard scope | M31, M25 |
| `refurb.graded` | unit, grade, standard version, battery health | M38, M12, M11 |
| `refurb.grade_overridden` | unit, prior grade, new grade, actor, justification | **M23**, Quality |
| `refurb.rejected` | unit, cause, destination (harvest / recycle), write-off amount | M15, M18, M19 |
| `refurb.listed` | unit, channel, price, disclosure report | M38, M12 |
| `refurb.sold` | unit, channel, price, grade, warranty term, provision | M09, M19, M53, M25 |
| `refurb.returned` | unit, reason, failure code, grade at sale | M23, M09 |
| `parts.harvested` | source unit, part lines, cost basis | **M15** |
| `refurb.stock_aged` | unit, band, markdown applied, NRV result | M19, M11 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-TRF-01 | **BTRC NEIR** — IMEI registration verification | Outbound | Confirm a handset's IMEI is registered and lawfully activatable before purchase and before listing |
| INT-TRF-02 | GSMA / operator device blocklists, where accessible | Outbound | Stolen-device screening |
| INT-TRF-03 | Market price reference sources | Inbound | New and used reference pricing to seed the local depreciation curve |
| INT-TRF-04 | Mobile financial services and banking (via M52) | Outbound | Seller settlement |
| INT-TRF-05 | OEM activation-lock and warranty-status lookups | Outbound | Ownership proof and remaining-warranty check at intake |
| INT-TRF-06 | Diagnostic tooling for the QA protocol | Inbound | Automated capture of battery health and hardware test results |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/tradein/requests` | POST | Raise a trade-in request | P01, app, counter |
| `/api/v1/tradein/valuation` | POST | Indicative valuation for a model and declared condition | P01, app |
| `/api/v1/tradein/offers/{id}/accept` | POST | Accept a firm offer | P01, app |
| `/api/v1/tradein/provenance/verify` | POST | Verify an IMEI or serial before purchase | Counter, intake |
| `/api/v1/refurb/units/{id}` | GET | Unit state, grade, cost and history | Internal |
| `/api/v1/refurb/units/{id}/gate` | GET | Destruction-gate status for the unit | Internal, audit |
| `/api/v1/refurb/units/{id}/disclosure` | GET | Buyer-facing device history report | P01, M38, M12 |
| `/api/v1/refurb/listings` | GET | Graded units available for a channel | M38, M12 |
| `/api/v1/refurb/grading-standard` | GET | The published grading standard in force | P01, M38, public |
| `/api/v1/refurb/bulk-buybacks/{id}/reconciliation` | GET | Corporate buy-back reconciliation and exceptions | P04 |
| `/api/v1/refurb/analytics` | GET | Yield, cycle time, cost, margin, returns | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| Retail Operations Head | C R U D A | All trade-in, refurbishment and resale; offer exceptions; write-off recommendation |
| R25 Retail / Refurbishment Officer | C R U | Assessment, offers, intake, listing preparation |
| R08 Service Centre Agent | C R | Counter trade-in intake and status for own branch |
| R10/R11/R12 Technician | C R U | Refurbishment work orders and QA results on assigned units |
| Refurbishment Supervisor | C R U A | Grade override, rework authorisation, parts-only routing — **cannot be the technician who ran the QA** |
| R32 Quality Manager / ISO Coordinator | R U A | Grading standard, QA protocol, audit sample, override reporting |
| R17 Inventory Manager | R U | Refurbished stock, harvested parts, ageing |
| R26 Finance Manager | R U A | Landed cost, valuation, NRV, write-off approval, warranty provision |
| R28 Warranty Claims Officer | R | Full build history on any refurbished unit under claim |
| R22 Account Manager (Corporate) | C R | Corporate bulk buy-back for assigned accounts |
| R24 Marketplace Operations Officer | R U | Listings on the marketplace channel |
| R21 Sales Manager | R | Pricing performance and channel margin |
| R36 Customer | C R | Own trade-in requests, offers and purchased-unit disclosure reports |
| R37 Corporate Portal User | C R | Own organisation's buy-back and reconciliation |
| R38 External Party (reseller) | R | Allocated listings only |

**Field-level restrictions.** Acquisition cost, accumulated refurbishment cost, landed cost and
margin per unit are visible to Retail Operations, Finance and management only — never to
counter staff, technicians, resellers or customers. Seller identity on a purchased unit is
visible to the intake officer, Legal and GRC only, and is **never** disclosed to the buyer.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| QA technician **and** grade override approver | The grade would stop being an independent measurement |
| Assessment officer **and** intake verification officer for the same unit | The person who set the price cannot alone confirm the condition that justifies it |
| Purchase settlement instruction **and** settlement execution | Cash control |
| Parts-only routing **and** write-off approval | A rejected unit destroys accumulated cost; that needs a second signature |
| Anyone in M14 **and** issuing a destruction certificate | The gate must be operated by M06, never by the module it gates |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Trade-in funnel | Retail Operations Head, Marketing | Daily | Requests, indicative values, offers, acceptance rate, intake conversion, decline reasons |
| Offer accuracy | Retail Operations Head | Weekly | Offer versus realised margin per model; revisions at intake and their causes |
| Gate compliance | Quality Manager, CFO | Daily | Units awaiting certificate, gate blocks, time-in-gate, and **any unit that moved without one (must be zero)** |
| Provenance rejections | Legal, GRC, Retail Operations Head | Monthly | NEIR failures, blocklist hits, refused purchases, patterns by seller and by channel |
| Refurbishment throughput | Retail Operations Head | Daily | Work orders by state, cycle time, bench load, rework rate |
| Yield and cause analysis | Quality Manager, Retail Operations Head | Weekly | Units in versus units sellable; failure causes; rework causes |
| Grading integrity | Quality Manager | Monthly | Override rate by supervisor, audit-sample variance, grade distribution drift |
| Unit economics | CFO, Retail Operations Head | Monthly | Acquisition, refurbishment, logistics, channel cost, price, warranty provision and net margin by unit, model and grade |
| Stock ageing and markdown | Retail Operations Head, Finance | Weekly | Stock by age band and grade, markdowns applied, NRV adjustments, channel-shift actions |
| Return and warranty analysis | Quality Manager, Warranty Claims | Monthly | Return rate and warranty claim rate by grade and model, mapped to QA results at sale |
| Harvested parts contribution | Inventory Manager, Finance | Monthly | Parts harvested, value added to stock, offset against parts purchasing |
| Corporate buy-back reconciliation | Account Manager, corporate client | Per project | Declared assets against intakes and certificates, with exceptions |
| Circular contribution | Quality Manager, M18 | Quarterly | Units diverted from waste through refurbishment, feeding the ESG position |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| **KPI-077** | Refurbishment yield (intake units that become sellable) | unmeasured | 82% | **> 88%** |
| **KPI-078** | Refurbished units sold per year | 0 | 6,000 run-rate | **12,000** |
| — | Trade-in offer acceptance rate | unmeasured | 45% | **> 55%** |
| — | Refurbishment cycle time (purchase to listed) | unmeasured | < 8 days | **< 5 days** |
| — | Gross margin per refurbished unit | unmeasured | 18% | **> 22%** |
| — | Refurbished return rate | unmeasured | < 6% | **< 4%** |
| — | Refurbished stock ageing beyond 90 days | unmeasured | < 18% | **< 12%** |
| — | Offers revised at intake | n/a | < 20% | **< 12%** |
| — | **Units processed without a destruction certificate** | n/a | **0** | **0** |
| — | **Handsets purchased without IMEI verification** | n/a | **0** | **0** |
| — | **Units listed without a disclosure report** | n/a | **0** | **0** |
| — | Grade override rate | n/a | < 10% | **< 5%** |
| — | Grading audit-sample variance | n/a | < 1 grade on 95% | **< 1 grade on 98%** |
| — | Rework rate | unmeasured | < 12% | **< 8%** |
| — | Warranty claim rate on refurbished units | unmeasured | < 8% | **< 5%** |
| — | Bulk buy-back reconciliation accuracy | n/a | **100%** | **100%** |

**Three of these targets are zero and one is one hundred per cent.** They are controls, not
performance measures. A single unit processed without a certificate is a reportable incident,
not a missed target.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `stock` (serialised lots, locations), `repair`/`mrp` (work order basis), `sale` | 18% |
| L2 | OCA quality-control and stock extensions | 6% |
| L5 | `cd_tradein`, `cd_refurb`, `cd_grading`, `cd_resale` | 76% |

The valuation engine, provenance and NEIR verification, the destruction gate, the grading
computation, the disclosure report and per-unit economics have no standard equivalent. Odoo
supplies serialised stock and a work-order skeleton; everything that makes this module
defensible is custom.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-063** also claimed by M35; **CD-064** also claimed by M35; **CD-065** also claimed by M35; **CD-066** also claimed by M21. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-063 | `cd_tradein` — request intake, valuation engine and curve, offer lifecycle, provenance and NEIR verification, settlement instruction, bulk buy-back reconciliation | Odoo module + service | 7 PW |
| CD-064 | `cd_refurb` — work order, standard scope by class, cost accumulation, rework control, **destruction gate and segregated storage enforcement** | Odoo module | 6 PW |
| CD-065 | `cd_grading` — grading standard versioning, QA protocol execution, battery-health capture, deterministic grade computation, override control, audit sample | Odoo module | 5 PW |
| CD-066 | `cd_resale` — refurbished stock class, grade-based pricing, ageing and markdown, disclosure report generation, channel listing, warranty registration, returns feedback | Odoo module | 4 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M06 Data Services — in or before W6** | **M14 cannot launch without the destruction gate. This is the binding constraint on the whole category** |
| M33 Party Master | Seller identity verification is a purchase precondition |
| M17 Device & Asset Registry | Every unit needs an identity that survives resale |
| M15 Spare Parts & Inventory | Parts consumption and harvested-part destination |
| M31 Workshop | Refurbishment runs on workshop benches |
| M11 Pricing | Grade-based resale rate cards |
| M09 Warranty | Refurbished warranty administration and provision |
| M24 Documents | Grading standard publication and evidence retention |
| M26 AI/ML | Valuation model *(degraded fallback available — not a hard blocker)* |
| M38 / M12 — W7 | Full digital resale channels arrive one wave later; counter and reseller channels carry W6 |

**Sequencing risk.** M38 E-Commerce and M12 Marketplace land in W7, one wave after M14. At W6
the module must sell through the retail counter and authorised resellers only. Plan the W6
volume ramp accordingly — do not size the W6 intake for a channel that does not yet exist.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Refurbishment tally sheets | Work in progress only | `fix.refurb.unit` + `fix.refurb.order` | W6 cutover |
| Refurbished stock on hand | All units held for resale | `fix.refurb.unit` (state = Graded or Listed) | W6 cutover |
| Historical trade-in and resale records | **Not migrated** — no grading standard, no certificates and no cost records exist, so the data cannot support margin analysis or a warranty claim | — | — |
| Existing refurbished units under warranty | All live warranties | `fix.refurb.warranty` + M09 policy | W6 cutover |

**Cutover control.** Every unit in stock at cutover must be assessed against the destruction
gate before it can be listed under the new system. Units already in stock without a certificate
must be re-wiped and certified through M06, not grandfathered. This will slow the first two
weeks of go-live and it is not negotiable.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **A unit cannot enter refurbishment without a valid M06 certificate for its media** | Negative test through UI, API and direct state manipulation |
| AC-02 | **A unit cannot be listed or sold without a valid M06 certificate** | Negative test |
| AC-03 | **The gate fails closed when M06 is unavailable** — the unit blocks rather than proceeds | Fault-injection test |
| AC-04 | A storage device cannot be harvested for parts without a certificate | Negative test |
| AC-05 | An unsanitised unit cannot be moved to a refurbishment stock location | Negative test on stock move |
| AC-06 | **A handset cannot be purchased without a recorded IMEI verification result**, and a NEIR failure blocks the purchase | Negative test with a simulated failure response |
| AC-07 | A handset failing NEIR verification cannot be listed | Negative test |
| AC-08 | A purchase cannot complete without a verified seller identity from M33 | Negative test |
| AC-09 | The provenance record cannot be amended after creation | Tamper test |
| AC-10 | Per-unit cost equals the sum of posted parts, labour, logistics and overhead transactions, with no manual entry path | Reconciliation against M15, M31 and M19 |
| AC-11 | Re-running the grading function on stored QA results reproduces the recorded grade | Determinism test across 100 units |
| AC-12 | A unit whose battery health is below the grade minimum cannot carry that grade | Boundary test at the threshold |
| AC-13 | A grade override by the technician who ran the QA is rejected | Negative test |
| AC-14 | Every listed unit has a generated disclosure report, and no free-text path can alter its condition statements | Data-model review and generation test |
| AC-15 | Every sale books a warranty provision to M09 / M19 at the point of sale | Reconciliation test |
| AC-16 | Refurbished stock ageing triggers markdown and an NRV test at each band | Scripted scenario over a compressed clock |
| AC-17 | Harvested parts appear in M15 with the harvested classification, a cost basis and traceability to the source unit | Integration test |
| AC-18 | A corporate bulk buy-back cannot close with any declared asset unreconciled | Scripted project with 100 assets including three deliberate exceptions |
| AC-19 | A retired rental unit from M13 arrives with its full service and condition history intact | Integration test |
| AC-20 | A rejected unit routes to harvest or M18 and cannot be left without a destination | Negative test |
| AC-21 | Retail Operations Head, Quality Manager and Finance Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 21 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **In which legal entity does the resale business sit, and how is second-hand-goods VAT treated in Bangladesh — on the full sale price or on the margin?** This materially changes unit economics *(decision D-04)* | CFO / M51 owner | **W6 minus 3 months** |
| Q-02 | Is programmatic or bulk access to **NEIR** available to a commercial party, or must verification be performed per device through the portal and USSD? This determines whether FR-TRF-006 automates or stays manual-with-evidence | CTO / Legal | **W6 minus 3 months** |
| Q-03 | What warranty term will be offered by grade — 3, 6 or 12 months — and what failure rate underpins the provision? | Retail Operations Head / CFO | W6 build |
| Q-04 | What is the battery-health minimum per grade? Back Market uses 80% as a floor; is that commercially viable at Bangladeshi price points, or is a lower disclosed floor acceptable? | Retail Operations Head / Quality Manager | W6 build |
| Q-05 | Will a "Certified" tier above Grade A be offered, requiring a replaced battery and a full rebuild? | Retail Operations Head | W6 build |
| Q-06 | What is the category margin floor below which an offer must be refused or escalated? | CFO / Retail Operations Head | W6 build |
| Q-07 | How is the seller's legal ownership evidenced where no purchase receipt exists — the common case in this market? | Legal | **W6 minus 2 months** |
| Q-08 | What is the Company's position where a device is identified as stolen after purchase — surrender, hold, notify? | Legal | W6 minus 2 months |
| Q-09 | Are there refurbished units currently in stock with no certificate of destruction? If so they require re-wiping before go-live | Retail Operations Head | **Immediately** |
| Q-10 | Which authorised resellers will carry refurbished stock at W6, before M38 and M12 arrive in W7? | Chief Commercial Officer | W6 minus 1 month |
| Q-11 | Does the Company intend to pursue **R2v3 certification**, and if so with which appendices? The design supports it; the commitment is a business decision | Quality Manager / CEO | W8 |
| Q-12 | What proportion of intake is expected from rental retirement (M13) versus customer trade-in versus corporate buy-back? This sizes the bench | Retail Operations Head | W6 build |

**Q-09 is not a design question.** It is an active exposure and should be investigated now,
independently of the ERP programme.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category D §4 — the non-negotiable gate; §9 — category risks) ·
`M13_Rental_and_Equipment_as_a_Service.md` (retirement source) ·
`M18_EWaste_Recycling_and_Circular_Economy.md` (rejection destination) ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md`
§5.4, §8.2, §12.2 (the certificate, the gate API, the fail-closed contract) ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §Category D ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` (FR-TRF-001…039) ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (BO-14, KPI-077,
KPI-078, benefit line 10)

**Workspace evidence**
`1000fix_business/Business planning for 1000 fix.docx` §Refurbishment and Resale — refurbishment,
data wiping and privacy protection, QA testing, resale and distribution, warranty and customer
support ·
`1000FiX_Services_Company_Profile.md` §Exchange Offer ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` (trade-in quotation flow) ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register
(BDT 65 lac)

**External benchmark**
**R2v3 (SERI)** Appendix B *Data Sanitization* — serialised tracking, verified methods,
documented quality control, and a method of distinguishing sanitised from data-bearing devices ·
**R2v3 Appendix C** *Test & Repair* — functional verification and accurate grading before
resale, requiring an accredited QMS (ISO 9001:2015) over the full test-and-repair scope ·
Apple Certified Refurbished — a single certified standard with new battery, new shell, full
inspection and a one-year warranty, rather than letter grades ·
Back Market — marketplace-enforced minimum 80% battery health on every phone shipped ·
Industry grading practice — Grade A like-new, Grade B light cosmetic wear, Grade C visible wear
but fully functional, with no single global standard, which is why a published in-house standard
is required ·
ITAD buy-back pricing — resale estimate less logistics, data destruction, refurbishment and
recycling cost, with deductions confirmed before shipment ·
Recommerce residual-value modelling — smartphone depreciation of 35–50% in year one, 60–75% by
year two and ~80% by year three; laptops declining 15–20% a year ·
Serialised inventory and landed-cost accounting — reserve for estimated refurbishment cost or
write-down to net realisable value ·
**BTRC NEIR** — mandatory IMEI registration on Bangladeshi networks, enforced from 16 December
2025, with unregistered handsets blocked from network service

**Sources consulted**
- [SERI — R2v3 appendix determination](https://sustainableelectronics.org/knowledge-base/r2v3-appendix-determination-tool/)
- [R2v3 Appendix B data sanitization requirements](https://www.bitraser.com/article/seri-r2v3-data-sanitization-requirements-appendix-b.php)
- [R2v3 Appendix C — test, repair and reuse](https://www.bitraser.com/article/r2v3-appendix-c-test-repair.php)
- [ITAD certifications explained — R2v3, e-Stewards, NAID AAA](https://itadintelligence.com/itad-certifications-explained.html)
- [What is Apple Certified Refurbished](https://www.refurb.me/blog/what-is-apple-certified-refurbished-definition)
- [Back Market — cosmetic condition and battery standards](https://www.backmarket.com/en-us/c/iphone/refurbished-iphones-cosmetic-damage)
- [Refurbished grades A, B and C explained](https://www.refurb.me/blog/what-are-refurbished-grades-a-b-c)
- [How ITAD buy-back pricing works](https://www.ewasteatl.com/post/how-itad-buy-back-pricing-works)
- [Device residual value and trade-in pricing](https://blog.dipli.com/en/trade-in-pricing-residual-value)
- [RecommerceIQ — pricing models for used and refurbished electronics](https://www.recommerceiq.com/topics/pricing-models)
- [PwC Viewpoint — inventory costing, refurbishment reserves and NRV](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/inventory/Inventory-Guide/Chapter-1-Inventory-costing/1_5_Other.html)
- [BTRC — National Equipment Identity Register](https://btrc.gov.bd/site/page/62ed0ce5-34ee-4110-9f00-317288f1c5fa/-)
- [The Business Standard — what is the National Equipment Identity Register](https://www.tbsnews.net/explainer/what-national-equipment-identity-register-neir-1290026)

---

*Module M14 · Category D · 1000FiX ERP System v2.0 · CONFIDENTIAL*
