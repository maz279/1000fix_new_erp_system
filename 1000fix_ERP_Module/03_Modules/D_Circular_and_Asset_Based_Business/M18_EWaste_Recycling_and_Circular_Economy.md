---
id: FIX-ERP2-M18
module_id: M18
module_code: ESG
module_name: E-Waste, Recycling & Circular Economy
category: D — Circular & Asset-Based Business
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Platform Squad
priority: P3
wave: W8
---

# M18 — E-Waste, Recycling & Circular Economy
### Category D · Code `ESG` · Existing (retained from v2.0)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M18 |
| **Module code** | `ESG` |
| **Category** | D — Circular & Asset-Based Business |
| **Status** | Existing (introduced in v2.0, retained in v2.1) |
| **Priority** | **P3** commercially · **P0** for the destruction gate and the disposal-certificate control |
| **Delivery wave** | W8 (Months 31–34) |
| **Business owner** | Quality Manager |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 (Odoo `stock` basis) · L5 (custom) |
| **Custom modules** | `cd_ewaste`, `cd_recycling`, `cd_esg_report` |
| **Requirement range** | FR-ESG-001 … FR-ESG-026 |
| **Requirement count** | 26 |
| **Effort estimate** | 13 person-weeks |
| **Depends on** | **M06 Data Services (hard gate)** · M14 Trade-In & Refurbishment · M15 Spare Parts · M03 Logistics · M17 Asset Registry · M33 Party Master · M24 Documents · M16 Procurement · M20 Receivable |
| **Depended on by** | M24 Documents (certificate custody) · M60 GRC · M23 Quality · M25 Business Intelligence · M10 Loyalty (collection incentives) · M35 Marketing (ESG claims) · P01 / P04 portals |

---

## 2. Purpose

M18 is the **end of the circle**. It takes in devices that have reached the end of their useful
life — from customers, from branches, from unrepairable service outcomes, from failed
refurbishment, from retired rental fleet and from corporate decommissioning — decides what
should happen to each one, and makes sure that whatever happens is documented, lawful and
certified.

It exists because the Company already touches thousands of end-of-life devices a year and
currently has no record of where any of them went. Every one of those devices is three things
at once: a regulatory obligation, a data-breach risk, and a small amount of recoverable
material value. M18 turns all three from exposure into evidence.

It is also the module that makes the Company's environmental claims **countable**. Diversion
from landfill, refurbishment rate, materials recovered and emissions avoided are either
measured figures with an audit trail behind them, or they are marketing. M18 is the difference.

### Why It Exists

The Business Plan commits the Company to responsible e-waste handling: designated collection
points, assessment for refurbishment, certified recycling partners, secure destruction,
regulatory compliance, component and material recovery, and public awareness. That commitment
is now also a legal one.

Bangladesh published the **Hazardous Waste (E-waste) Management Rules 2021** under the
Environment Conservation Act 1995. They require manufacturers, traders, sellers, transporters,
**repairers**, recyclers and dismantlers to register with the Department of Environment and to
submit an e-waste management plan. They establish an Extended Producer Responsibility regime
with collection targets rising from 10% in the first year to 50% by the fifth. And they carry
criminal penalties: up to two years' imprisonment or a fine of BDT 200,000, rising to between
two and ten years and BDT 200,000–1,000,000 for repeat offences.

1000FiX is a repairer and a seller of electrical and electronic equipment. It is inside the
scope of those rules. It has no system that could produce the required records.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Business Plan §Device Recycling and Responsible Disposal | Collection points, triage, certified partners, data destruction, secure disposal, regulatory compliance, component recovery, public awareness |
| Category D Overview §4 | The non-negotiable gate: no recycling transfer without an M06 destruction certificate |
| Category D Overview §7 | 25,000 devices collected per year; diversion from landfill > 92%; disposal certificates on file 100% |
| Scope Charter §Benefit Register | E-waste material recovery **BDT 12 lac/year** base case (7 conservative · 19 upside) |
| **Hazardous Waste (E-waste) Management Rules 2021** *(DoE, 10 June 2021, under the Environment Conservation Act 1995)* | Registration and an approved e-waste management plan required for repairers, sellers, transporters, recyclers and dismantlers; EPR collection targets from 10% to 50%; RoHS-aligned restriction of ten substances; criminal penalties for non-compliance |
| **BTRC WEEE Guidelines** *(published 7 July 2022)* | Telecom-sector e-waste handling and recycling obligations under DoE oversight |
| **Basel Convention e-waste amendments** *(in force 1 January 2025)* | All transboundary movements of e-waste, hazardous or not, are subject to the prior-informed-consent procedure |
| Company Profile §ISO 9001:2015 | An existing certified quality system, and an ISO 14001 ambition that this module makes achievable |
| Module Register (02-02) | M18 `ESG`, P3, W8, Quality Manager, 26 requirements, 13 PW |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Collection from every channel — branch drop-off, scheduled pickup, corporate decommission, internal write-off, unrepairable service outcome, failed refurbishment, retired rental |
| 2 | Customer-facing collection booking with incentives |
| 3 | The collection event record: item, source, weight, category, condition, evidence |
| 4 | Chain of custody from the point of collection to the point of final disposal |
| 5 | Triage and disposition: refurbish (M14), harvest (M15), recycle, or hazardous treatment |
| 6 | The disposition decision log with assessor, criteria and evidence |
| 7 | The destruction gate: no item leaves without an M06 certificate |
| 8 | Certified recycling partner register with certification currency and accepted material classes |
| 9 | Recycling batch assembly by material class |
| 10 | Transfer notes, manifests and hazardous-material declarations |
| 11 | Disposal certificate receipt, indexing and reconciliation to individual items |
| 12 | Material recovery accounting — weights, values and income |
| 13 | Hazardous material handling rules, most critically lithium-ion battery storage |
| 14 | Downstream due diligence on partners and their onward vendors |
| 15 | The regulatory register and the Company's obligations under each instrument |
| 16 | Statutory returns and DoE / BTRC reporting |
| 17 | Audit evidence packs for regulators, brand partners and ISO 14001 readiness |
| 18 | Carbon and impact estimation — avoided emissions, diverted waste |
| 19 | Internal and external sustainability reporting |
| 20 | Awareness campaigns and their measurement |
| 21 | Donation programmes for functional low-value devices |
| 22 | Supplier ESG assessment input |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Certified data destruction and the certificate** | **M06** Data Services | M18 requires it and cannot transfer without it, but does not perform or issue it. The gate must be operated by a different module from the one it gates |
| Refurbishment, grading and resale | **M14** Trade-In & Refurbishment | M18 triages and routes; M14 does the bench work and sells the outcome |
| Parts harvesting execution and stock entry | **M15** Spare Parts / **M14** | M18 identifies harvest candidates; the part enters stock through M15 |
| Physical transport and custody in transit | **M03** Service Logistics | Every movement is a consignment with a custody trail owned by M03 |
| Partner contracting, onboarding and payment | **M16** Procurement / **M42** SRM | M18 defines the qualification criteria and verifies currency; Procurement contracts |
| Material recovery income invoicing | **M20** Receivable | M18 records weights and values; Finance invoices |
| Document retention and versioning | **M24** Documents | Certificates and manifests are retained by M24; M18 obtains and indexes them |
| Enterprise risk register and incident investigation | **M60** GRC | M18 raises compliance events; GRC investigates |
| ESG dashboard visualisation for management | **M25** Business Intelligence | M18 owns the metric definitions and the underlying data; M25 renders it |
| Loyalty points and voucher issuance for collection incentives | **M10** Loyalty & Rewards | M18 triggers the reward; M10 owns the balance |
| Campaign execution and audience management | **M35** Marketing | M18 supplies the substance and the results |
| The Company's own fixed-asset write-off accounting | **M49** Fixed Assets | M18 provides the disposal evidence |
| Occupational health and safety incident management | **M59** HSE | M18 defines hazmat handling rules; HSE owns incidents and training records |
| Facility fire safety, storage infrastructure and permits | **M47** Facility | M18 states the requirement; Facilities provides the building |

### 3.3 Shared Concepts

| Concept | M18's Role | Owning Module |
|---|---|---|
| Destruction certificate | **Consumes as a hard gate** | M06 |
| Disposal certificate | **Obtains, indexes and reconciles** | M24 retains |
| Collection event | **Owns** | M18 |
| Triage disposition | **Owns** | M18 |
| Recycling partner qualification | **Owns the criteria and currency check** | M16 / M42 contract |
| Consignment and custody | Requests | M03 |
| Harvested part | Identifies the candidate | M15 / M14 |
| Refurbishable unit | Routes | M14 |
| ESG metric definition | **Owns** | M25 visualises |
| Hazmat handling rule | **Owns** | M59 owns the incident |
| Regulatory obligation register | **Owns the e-waste subset** | M60 owns the enterprise register |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Hazardous Waste (E-waste) Management Rules 2021 (Bangladesh)** | Registration with the Department of Environment and an approved e-waste management plan for repairers, sellers, transporters, recyclers and dismantlers; EPR collection targets rising 10% → 50%; RoHS-aligned substance restrictions; criminal penalties | **The entire compliance spine.** The regulatory register, the collection-target tracker, the statutory return and the evidence pack are all shaped by this instrument, because it is the one the Company is actually accountable to | Nothing — this is the governing law |
| **BTRC WEEE Guidelines (7 July 2022)** | Telecom-sector e-waste handling and recycling obligations under DoE oversight | Telecom-device handling recorded separately where the guideline imposes distinct duties | — |
| **Basel Convention e-waste amendments (in force 1 January 2025)** | All transboundary movements of e-waste — hazardous *and* non-hazardous — subject to the prior-informed-consent procedure; written consent of the importing state before shipment | **A hard block on any cross-border transfer without a recorded PIC reference.** Bangladesh has no domestic capacity for several material streams, so this will be tested in practice | — |
| **R2v3 (SERI) downstream due diligence** | The certified party remains responsible for material passed to downstream vendors, requiring documented verification of each onward vendor's authorisation and capability | **Two-tier partner verification**: the Company verifies its partner *and* records the partner's declared onward destinations. "We gave it to a licensed recycler" is not an answer to "where did it go" | Full R2v3 certification at W8 — a design target, not a launch prerequisite |
| **e-Stewards** | Prohibition on export of hazardous e-waste to developing countries; strong chain-of-custody expectations | Chain-of-custody continuity as a hard requirement across every transfer | Its export-policy framing, which is written from an exporting-country perspective |
| **GRI 306: Waste 2020** | Disclosure 306-3 waste generated, 306-4 waste **diverted from disposal** broken down by recovery operation, 306-5 waste **directed to disposal**, each split hazardous / non-hazardous | **The reporting model, verbatim.** Diversion is measured by recovery operation — preparation for reuse, recycling, other recovery — not as a single headline number | — |
| **ESRS E5 (CSRD)** *(as simplified by Omnibus I, February 2026)* | Resource inflows and outflows, circular material use rate, recycled input share, waste split hazardous / non-hazardous and further into preparation for reuse, recycling and other recovery | **The outflow taxonomy**, so the Company's numbers are already in a shape international brand partners and lenders recognise | Full CSRD reporting — 1000FiX is not in scope, and building for it would be waste |
| **ISO 14001** | Environmental management system: aspects and impacts, legal register, operational control, monitoring, audit | **The legal register and operational-control pattern**, which the Company can adopt on top of its existing ISO 9001 system | Full EMS certification scope at W8 |
| **Lithium-ion battery handling practice** *(EPA, EERA, fire-protection guidance)* | Segregation by chemistry and state, maximum storage quantities, minimum separation distances, temperature control (~15 °C ideal), ventilation, damaged/defective cells handled under stricter procedure, dedicated suppression and alarm | **Explicit, enforced storage rules with a system-tracked quantity ceiling per location**, and a separate handling path for damaged or swollen cells. Waste-sector data attributes hundreds of facility fires to mismanaged lithium cells | Building a dedicated battery facility at W8 — the control is procedural and quantity-limited until volumes justify capital |

**Design position.** Four deliberate differences.

**First, this is a compliance module wearing a sustainability jacket.** The ESG dashboard is
the visible output; the reason the module is funded is that the Company is a registered
repairer and seller under the E-waste Rules 2021, with criminal penalties attached to
non-compliance. Every design decision resolves toward *can we evidence this to the Department
of Environment*, not toward *does this look good in a report*.

**Second, the disposal certificate is reconciled to the item, not to the batch.** The easy
implementation records one certificate per transfer. The defensible one reconciles every item
in the batch to that certificate, so the Company can answer the only question that matters in
an investigation: *where did this specific serial number go, and who certified its
destruction*. This is the same discipline M06 applies to destruction certificates, applied to
disposal.

**Third, partner certification currency is checked at the moment of transfer, not at
onboarding.** A recycler whose licence expired last month is not a certified recycler, and a
transfer to them is a regulatory breach committed by 1000FiX. The system therefore re-checks
expiry at transfer time and blocks — this is a hard stop, not a warning on a supplier record
nobody reads.

**Fourth, the environmental numbers are computed from transactions, never entered.** Diversion
rate, material recovery and avoided emissions derive from weighed, recorded, certificated
events. No user can type an ESG figure into this system. That constraint is what makes the
resulting claims defensible — and it is the reason M18 is worth building even though its direct
revenue is the smallest in the category.

---

## 5. Functional Areas & Features

### 5.1 Collection

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ESG-001 | Collection channels | Accept end-of-life devices from branch drop-off, scheduled customer collection, corporate bulk decommission, internal write-off, unrepairable service outcomes, failed refurbishment (M14) and retired rental fleet (M13) | P3 | L5 |
| FR-ESG-002 | Collection booking & incentive | Let customers book a drop-off or collection through the portal or app, and trigger the agreed incentive — loyalty points, voucher or trade-in credit — on confirmed receipt | P3 | L5 |
| FR-ESG-003 | Collection event record | Record every item received with source, source reference, weight, device category, condition, hazardous flags and photographic evidence | P2 | L5 |
| FR-ESG-004 | Custody from collection | Raise an M03 consignment for every movement of e-waste and maintain unbroken chain-of-custody evidence from receipt to final disposal | P2 | L5 |
| FR-ESG-005 | Corporate disposal contracts | Manage contracted bulk disposal with reconciliation against the client's declared asset list and per-unit certification | P3 | L5 |
| FR-ESG-022 | Collection point register | Maintain designated collection points with their capacity, storage constraints, hazardous-material limits and responsible person | P3 | L5 |

### 5.2 Triage, Disposition & The Destruction Gate

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ESG-006 | Triage assessment | Assess every item against published criteria for refurbishment (route to M14), parts harvesting (route to M15), recycling, or hazardous treatment | P2 | L5 |
| FR-ESG-007 | Disposition decision log | Record each disposition with the assessor's identity, the criteria applied, the evidence and the timestamp, immutably | P2 | L5 |
| FR-ESG-008 | Parts harvesting identification | Identify harvestable components, route the unit for harvesting and track the resulting parts into M15 with source traceability | P2 | L5 |
| FR-ESG-009 | Data destruction gate | **Require a valid M06 certificate for every data-bearing item before it may be transferred to a recycler, harvested or routed to resale — and block the transition without it** | **P0** | L5 |
| FR-ESG-023 | Donation programme | Route functional low-value devices to approved donation recipients with the same destruction gate, custody trail and certification as any other outbound route | P3 | L5 |

### 5.3 Recycling, Partners & Material Recovery

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ESG-010 | Recycling partner register | Register certified partners with certification type, issuing body, scope, accepted material classes, expiry date and declared downstream vendors | P2 | L5 |
| FR-ESG-011 | Recycling batch | Assemble items into batches by material class, with itemised contents, gross and net weights, and a batch identifier that follows the material to its destination | P3 | L5 |
| FR-ESG-012 | Transfer documentation | Produce transfer notes, manifests and hazardous-material declarations, and block a transfer whose documentation is incomplete or whose partner certification has expired | P2 | L5 |
| FR-ESG-013 | Disposal certificates | Receive, index and store certificates of disposal from partners, reconciled to individual items within the batch, and flag any item not covered by a returned certificate | **P0** | L5 |
| FR-ESG-014 | Material recovery accounting | Record recovered material classes and weights — ferrous, non-ferrous, precious metals, circuit boards, plastics, glass, cabling — with agreed rates and the resulting income to M20 | P3 | L5 |
| FR-ESG-015 | Hazardous material handling | Apply specific handling, storage, quantity-limit and transport rules for lithium-ion and other batteries, CRTs, mercury-containing lamps, refrigerant-bearing equipment and toner, with a stricter path for damaged or swollen cells | **P1** | L5 |
| FR-ESG-024 | Downstream due diligence | Record each partner's declared onward destinations, verify them periodically, and report any material stream whose final destination is unverified | P2 | L5 |
| FR-ESG-025 | Transboundary movement control | Where any material is destined to cross a border, require a recorded **prior-informed-consent** reference under the Basel Convention before the transfer can execute | **P1** | L5 |

### 5.4 Compliance, ESG Reporting & Awareness

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-ESG-016 | Regulatory register | Maintain the applicable e-waste and environmental instruments — E-waste Rules 2021, Environment Conservation Act 1995 and Rules, BTRC WEEE Guidelines, Basel Convention — with the Company's obligation, owner, evidence source and review date under each | P2 | L5 |
| FR-ESG-017 | Statutory reporting | Produce the returns required by the Department of Environment and BTRC on volumes collected, treated, recovered and disposed, including progress against the EPR collection target in force | P2 | L5 |
| FR-ESG-018 | Audit evidence pack | Assemble, for any period, a complete evidence pack for a regulator, brand partner or ISO 14001 audit — collections, dispositions, certificates, manifests, partner certifications and exceptions | P2 | L5 |
| FR-ESG-019 | Carbon & impact metrics | Estimate diverted waste and avoided emissions from refurbishment and recycling using a documented, versioned factor set, with the factor version stamped on every published figure | P3 | L5 |
| FR-ESG-020 | Sustainability reporting | Publish internal and external metrics structured to **GRI 306** — waste generated, waste diverted from disposal by recovery operation, waste directed to disposal — split hazardous and non-hazardous | P3 | L5 |
| FR-ESG-021 | Awareness campaigns | Run and measure customer awareness campaigns through M35 / M10, attributing collections to campaigns | P3 | L5 |
| FR-ESG-026 | Supplier ESG assessment | Supply e-waste and disposal performance data into supplier and partner assessment in M42, and flag partners whose performance or certification lapses | P3 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Fail-closed destruction gate** | The M06 certificate check blocks on any response other than `CERTIFIED`, including timeout and unavailability. No transfer proceeds on an unanswered call |
| T-02 | **Certification currency at transfer** | Partner certification expiry is evaluated at the moment of transfer, not at onboarding; an expired certification is a hard block |
| T-03 | **Item-to-certificate reconciliation** | Every item in a batch is reconciled to a returned disposal certificate; unreconciled items are reported as open exceptions until closed |
| T-04 | **Immutable disposition log** | Triage decisions are write-once; a changed decision is a new record referencing the prior one |
| T-05 | **Weight integrity** | Batch net weight must reconcile to the sum of item weights within a configured tolerance; a breach blocks the transfer document |
| T-06 | **Hazmat quantity ceilings** | Each storage location carries a maximum quantity per hazardous class; receipt beyond the ceiling is blocked and alerted |
| T-07 | **Computed ESG metrics only** | Diversion rate, recovery weights and avoided emissions are derived from posted transactions. No user-entry path to any published environmental figure exists |
| T-08 | **Factor versioning** | Emissions and impact factors are versioned; every published figure records the factor set used, so a restatement is explainable |
| T-09 | **Chain-of-custody continuity** | Every custody handoff carries a signed transfer with both parties identified; a gap in the chain is an exception, not a silent omission |
| T-10 | **Basel PIC block** | Any transfer whose destination is outside Bangladesh requires a recorded prior-informed-consent reference before execution |
| T-11 | **Evidence pack assembly** | A complete audit pack for any period is assembled on demand without manual collation |
| T-12 | **Retention** | Collection records, dispositions, manifests and certificates are retained for the statutory period plus five years, and are exportable |
| T-13 | **Performance** | Gate check ≤ 200 ms; batch transfer document generation ≤ 5 s; evidence pack for a 12-month period ≤ 60 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M18 |
|---|---|---|
| **Branch staff** | Dead devices accumulate in a back room until someone clears them | Booked in as a collection event, weighed, categorised and moved on a schedule |
| **Triage assessor** | Decides by eye; the decision is not recorded | Applies published criteria; the decision, the reason and the assessor are on the record |
| **Quality Manager** | Cannot answer a Department of Environment enquiry | Produces a complete evidence pack for any period in under a minute |
| **Technician** | Discards a battery in the general waste bin | Follows a handling rule the system enforces, with a storage location and a quantity ceiling |
| **Procurement Officer** | Knows a recycler is "certified" | Sees the certification, its scope, its expiry and the partner's declared downstream vendors |
| **Corporate client** | Disposes of 300 devices on a promise | Receives per-unit destruction and disposal certification, reconciled to their own asset list |
| **Marketing Manager** | Makes environmental claims with nothing behind them | Publishes measured, GRI-structured figures with an audit trail |
| **Account manager** | Cannot answer a tender's ESG section | Has documented disposal, certified partners and reportable metrics |
| **CFO** | Carries an unquantified regulatory exposure with criminal penalties attached | Carries a registered, evidenced, auditable process |
| **CEO** | Has an environmental commitment in the business plan | Has an environmental position with numbers, and a defensible one |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Material recovery income** | Recorded weights and agreed rates on recovered ferrous, non-ferrous, precious metal, board, plastic and cable streams | **BDT 12 lac/year** base case (7 conservative · 19 upside) |
| **Corporate disposal contracts** | Certified, reconciled, per-unit-documented disposal is a saleable service to every corporate client — and pairs directly with M06 bulk decommissioning and M14 buy-back | New revenue line, sized after Wave 8 |
| **Refurbishment feedstock** | Triage routes 30%+ of collected units into M14 rather than into a skip | Feeds the **BDT 65 lac/year** refurbishment line at near-zero acquisition cost |
| **Parts feedstock** | Harvested components from unrefurbishable units enter M15 | Reduces parts purchasing, especially on obsolete models with no supply |
| **Avoided regulatory penalty** | The E-waste Rules 2021 carry up to two years' imprisonment or BDT 200,000, and BDT 200,000–1,000,000 with two to ten years for repeat offences | Risk avoidance — the downside is personal liability for named officers, not just a fine |
| **Tender qualification** | Corporate, brand-partner and government tenders increasingly carry ESG and disposal requirements the Company currently cannot answer | Removes a disqualifier from bids that are presently unbiddable |
| **Brand partner compliance** | OEM and brand partners increasingly require documented downstream disposal from their service partners | Protects existing authorised-service relationships |
| **ISO 14001 readiness** | The legal register, operational control and monitoring evidence are the substance of an EMS | Turns certification into a documentation exercise |
| **Collection as an acquisition channel** | A customer bringing in a dead device is standing in a branch with a reason to buy | Feeds M14 trade-in, M38 resale and service pipelines |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Closes the data-liability loop** | M06 and M14 protect the resale path. Without M18, the recycling path stays open — and a device sent to a recycler with a working drive in it is the same breach by a different route |
| **Makes the environmental commitment countable** | The Business Plan's environmental language becomes a set of measured, GRI-structured figures that survive scrutiny |
| **Legal standing** | The Company is inside the scope of the E-waste Rules 2021 as a repairer and seller. Registration and an approved management plan are obligations, not options, and this module is what makes them satisfiable |
| **Worker safety** | Enforced lithium-ion handling rules and quantity ceilings address a genuine and well-documented fire risk in exactly the kind of facility the Company operates |
| **Community standing** | Collection points and awareness campaigns give branches a role in their neighbourhoods beyond selling repairs |
| **Institutional memory** | Where devices went, who certified it and under what licence becomes a permanent record rather than a departed employee's recollection |
| **Completes the circle** | Categories A through C sell service and product. M18 is what makes the Company's device business genuinely circular rather than merely linear with a recycling paragraph |

---

## 8. Lifecycle & State Models

### 8.1 E-Waste Item

```
   ┌────────────────────────────────────────────────────────────┐
   │  SOURCES                                                    │
   │  customer drop-off · booked collection · corporate          │
   │  decommission · internal write-off · unrepairable service    │
   │  outcome · M14 refurbishment failure · M13 rental retirement │
   └───────────────────────────┬────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      RECEIVED       │  weighed · categorised · photographed
                    └──────────┬──────────┘  hazmat flags set · custody opened
                               │
                    ┌──────────▼──────────┐
                    │      TRIAGED        │  published criteria · assessor recorded
                    └──────────┬──────────┘
          ┌────────────────────┼────────────────────┬──────────────────┐
          │                    │                    │                  │
   ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐   ┌──────▼──────┐
   │ REFURBISH   │      │   HARVEST   │      │   RECYCLE   │   │  HAZARDOUS  │
   │  → M14      │      │   → M15     │      │             │   │  TREATMENT  │
   └──────┬──────┘      └──────┬──────┘      └──────┬──────┘   └──────┬──────┘
          │                    │                    │                  │
          └────────────────────┴──────────┬─────────┴──────────────────┘
                                          │
                        ┌─────────────────▼──────────────────┐
                        │   AWAITING DATA DESTRUCTION        │
                        │   ✖ no route proceeds from here    │
                        │   M06 wipe request raised          │
                        └─────────────────┬──────────────────┘
                                          │ M06 returns CERTIFIED
                                          │ ◄── the gate · fails closed · no override
                        ┌─────────────────▼──────────────────┐
                        │   CLEARED FOR DISPOSITION          │
                        └─────────────────┬──────────────────┘
                                          │
                                  ┌───────▼────────┐
                                  │   BATCHED      │  by material class · weighed
                                  └───────┬────────┘
                                          │ partner certification checked AT TRANSFER
                                          │ manifest + hazmat declaration complete
                                          │ Basel PIC ref if crossing a border
                                  ┌───────▼────────┐
                                  │  TRANSFERRED   │  consignment via M03 · custody signed
                                  └───────┬────────┘
                                          │ partner processes
                                  ┌───────▼────────┐
                                  │   CERTIFIED    │  disposal certificate received
                                  │   DISPOSED     │  reconciled item by item
                                  └───────┬────────┘
                                          │ any item not covered
                                  ┌───────▼────────┐
                                  │   EXCEPTION    │──► investigated · escalated to GRC
                                  └────────────────┘     until closed
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Received | Weight, category and evidence captured; custody opened | Collection point staff |
| Received | Triaged | Assessment against published criteria complete | Triage assessor |
| Triaged | Awaiting Destruction | Automatic for any data-bearing item, on every route | System |
| Awaiting Destruction | Cleared | **M06 returns `CERTIFIED`** | System — no human override |
| Cleared | Batched | Material class assigned; weights recorded | Warehouse operative |
| Batched | Transferred | **Partner certification valid at this moment**; manifest and hazmat declaration complete; batch weight reconciles; PIC reference present for cross-border | Quality Manager |
| Transferred | Certified Disposed | Disposal certificate received and reconciled to the item | Quality Manager |
| Transferred | Exception | Certificate not received within the agreed window, or an item unreconciled | System |

### 8.2 The Gate, Stated Plainly

> **No item leaves 1000FiX custody — to a recycler, a harvester, a resale route or a donation
> recipient — without a valid M06 certificate of destruction bound to its storage media.**

| Blocked Transition | Enforced By | Bypass |
|---|---|---|
| Triaged → transfer to recycling partner | M18 state machine | **None** |
| Triaged → harvesting of a storage device | M18 state machine | **None** |
| Triaged → routed to M14 for refurbishment | M14 state machine (its own gate) | **None** |
| Triaged → donation recipient | M18 state machine | **None** |

### 8.3 Recycling Partner

```
  IDENTIFIED ──► QUALIFIED ──► CONTRACTED ──► ACTIVE ──► UNDER REVIEW ──► ACTIVE
                (certification    (M16)         │            ▲                │
                 verified ·                     │            │                │
                 scope · downstream             │  certification expiring     │
                 vendors declared)              │  or performance concern     │
                                                │                             │
                                                └──► SUSPENDED ──► TERMINATED ┘
                                                     (expired certification =
                                                      automatic suspension;
                                                      transfers blocked)
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-ESG-01 | **No item is transferred to a recycler, harvested, donated or routed to resale without a valid M06 certificate of destruction** | **H** | Quality Manager |
| BRU-ESG-02 | **A transfer to a partner whose certification has expired is blocked at the moment of transfer** | **H** | Quality Manager |
| BRU-ESG-03 | Every transfer requires a complete manifest and, where applicable, a hazardous-material declaration | **H** | Quality Manager |
| BRU-ESG-04 | Every item in a transferred batch must be reconciled to a returned disposal certificate; unreconciled items remain open exceptions | **H** | Quality Manager |
| BRU-ESG-05 | Batch net weight must reconcile to the sum of item weights within tolerance | **C** / **H** | Warehouse Manager |
| BRU-ESG-06 | Any transfer whose destination is outside Bangladesh requires a recorded Basel prior-informed-consent reference before execution | **H** | Quality Manager / Legal |
| BRU-ESG-07 | Lithium-ion and other batteries are stored only in designated locations, within the quantity ceiling for that location | **H** | HSE Officer |
| BRU-ESG-08 | Damaged, swollen or defective cells follow the stricter handling path and cannot be batched with sound cells | **H** | HSE Officer |
| BRU-ESG-09 | Triage decisions are recorded with assessor, criteria and evidence, and are immutable once made | **H** | Quality Manager |
| BRU-ESG-10 | Chain of custody must be unbroken from collection to certified disposal; a gap is an exception requiring investigation | **H** | Quality Manager |
| BRU-ESG-11 | Published environmental figures are computed from posted transactions; no manual entry path exists | **H** | CTO |
| BRU-ESG-12 | Every published impact figure records the emissions-factor version used | **C** | Quality Manager |
| BRU-ESG-13 | Collection events attributed to a customer trigger the agreed incentive only on confirmed physical receipt | **H** | Marketing Head |
| BRU-ESG-14 | A corporate disposal contract is not closed until every declared asset is reconciled to a certificate or a documented exception | **H** | Quality Manager |
| BRU-ESG-15 | Donated devices carry the same destruction gate, custody trail and certification as any other outbound route | **H** | Quality Manager |
| BRU-ESG-16 | The regulatory register is reviewed at least quarterly and after any published amendment | **S** | Quality Manager |
| BRU-ESG-17 | Statutory returns are filed within the deadline in the instrument; a late filing is a reportable compliance event | **H** | Quality Manager / CFO |
| BRU-ESG-18 | Partner downstream destinations are declared at qualification and verified at least annually | **H** | Procurement Officer |
| BRU-ESG-19 | Material recovery income is recorded against the batch that produced it, never as an unallocated receipt | **H** | Finance Manager |
| BRU-ESG-20 | An item routed to refurbishment that M14 subsequently rejects returns to M18 triage, retaining its original collection record | **C** | Quality Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.ewaste.collection` | `fix_ewaste_collection` | A collection event | name, channel, source_type, source_ref, partner_id, collection_point_id, collected_at, collected_by, consignment_ref, incentive_ref, campaign_ref, item_count, total_weight_kg |
| `fix.ewaste.item` | `fix_ewaste_item` | One end-of-life item | collection_id, asset_id (M17 where known), device_category, make_model, serial_or_imei, weight_kg, condition, data_bearing, hazmat_classes, destruction_cert_ref, state, disposition, batch_id, disposal_cert_ref, photo_ids |
| `fix.triage.assessment` | `fix_triage_assessment` | The disposition decision | ewaste_item_id, assessor_id, assessed_at, criteria_version, functional_result, cosmetic_result, market_value_estimate, disposition, rationale, evidence_ids, immutable, superseded_by |
| `fix.collection.point` | `fix_collection_point` | A designated collection location | branch_id, name, capacity_kg, hazmat_limits, responsible_person_id, active_from, active_to |
| `fix.recycling.partner` | `fix_recycling_partner` | A qualified downstream partner | partner_id (M33), certification_type, issuing_body, certificate_ref, scope, accepted_material_classes, valid_from, expiry_date, state, contract_ref (M16), last_audit_at |
| `fix.partner.downstream` | `fix_partner_downstream` | The partner's onward vendors | recycling_partner_id, downstream_name, material_class, country, declared_at, verified_at, verification_evidence_ref |
| `fix.recycling.batch` | `fix_recycling_batch` | Material grouped for transfer | name, material_class, item_ids, gross_weight_kg, net_weight_kg, tare_kg, reconciliation_variance, recycling_partner_id, state, assembled_at |
| `fix.transfer.note` | `fix_transfer_note` | The outbound document | batch_id, recycling_partner_id, manifest_ref, hazmat_declaration_ref, basel_pic_ref, transport_consignment_ref, dispatched_at, dispatched_by, received_signature_ref |
| `fix.disposal.certificate` | `fix_disposal_certificate` | The partner's proof of disposal | batch_id, recycling_partner_id, certificate_number, issued_at, method, covered_item_ids, document_id (M24), received_at, reconciled, unreconciled_item_ids |
| `fix.material.recovery` | `fix_material_recovery` | What was recovered and what it earned | batch_id, material_class, weight_kg, agreed_rate, income_amount, invoice_ref (M20), recorded_at |
| `fix.hazmat.record` | `fix_hazmat_record` | Hazardous item handling and storage | ewaste_item_id, hazmat_class, condition (sound / damaged / swollen), storage_location_id, quantity_at_location, ceiling, handling_path, disposal_route, incident_ref |
| `fix.esg.metric` | `fix_esg_metric` | A computed, published figure | period, metric_code, gri_reference, value, unit, hazardous_split, recovery_operation, factor_set_version, computed_at, source_query_ref |
| `fix.regulatory.obligation` | `fix_regulatory_obligation` | The legal register (e-waste subset) | instrument, citation, obligation_text, applies_because, owner_role, evidence_source, frequency, next_review, last_reviewed, status |
| `fix.statutory.return` | `fix_statutory_return` | A filed return | instrument, authority (DoE / BTRC), period, volumes, epr_target_pct, achieved_pct, prepared_by, filed_at, acknowledgement_ref |
| `fix.corporate.disposal` | `fix_corporate_disposal` | Contracted bulk disposal | partner_id, contract_ref, declared_asset_count, received_count, certified_count, exception_lines, state, closed_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.destruction.certificate` | **M06** | **Synchronous gate check — fails closed** |
| `fix.asset` | M17 / M49 | Read identity; publish end-of-life state |
| `fix.consignment` | M03 | Movement and custody |
| `fix.party` | M33 | Customers, corporate clients, recycling partners |
| `fix.document` | M24 | Certificates, manifests, declarations, evidence packs |
| `fix.refurb.unit` | M14 | Units routed in and rejected back out |
| `fix.part.item` | M37 | Harvested components entering stock |
| `fix.supplier.scorecard` | M42 | Partner performance feed |
| `fix.wallet` / `fix.points.ledger` | M10 | Collection incentives |
| `fix.billable.event` | M20 | Material recovery income |
| `fix.risk` / `fix.obligation` | M60 | Enterprise register and incidents |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-ESG-01 | Collection booked through a portal | Confirm the slot, raise the M03 collection consignment, notify the customer | Manual scheduling task |
| AUT-ESG-02 | Item received at a collection point | Create the item record, capture weight and category, set hazmat flags, open custody | Block receipt without weight and category |
| AUT-ESG-03 | Collection confirmed for an incentivised booking | Trigger the loyalty points or voucher through M10 | Retry; escalate to Marketing |
| AUT-ESG-04 | Triage completed with a disposition | Route to M14, M15, recycling or hazardous treatment; **raise the M06 wipe request for any data-bearing item automatically** | Item stays blocked; alert Quality Manager |
| AUT-ESG-05 | M06 publishes `wipe.certified` | Clear the item for its assigned disposition | Item stays blocked; retry the gate check |
| AUT-ESG-06 | M06 publishes `wipe.failed` | Route to physical destruction; block every outbound transition for that item until certified | Escalate to Quality Manager |
| AUT-ESG-07 | Batch assembled and transfer requested | Verify partner certification currency, manifest completeness, hazmat declaration and weight reconciliation | **Block the transfer** and state which check failed |
| AUT-ESG-08 | Transfer destination is outside Bangladesh | Require a Basel PIC reference before the transfer can execute | Block the transfer |
| AUT-ESG-09 | Transfer executed | Raise the M03 consignment, publish the transfer note, start the certificate-due clock | Escalate to Quality Manager |
| AUT-ESG-10 | Disposal certificate received | Index it, reconcile it item by item, close the covered items, list any item not covered | Raise an exception for every uncovered item |
| AUT-ESG-11 | Certificate not received within the agreed window | Raise an exception, notify the partner and the Quality Manager, suspend further transfers to that partner after the second occurrence | Escalate to GRC |
| AUT-ESG-12 | Partner certification approaching expiry (T-60, T-30, T-7 days) | Notify Procurement and the Quality Manager; on expiry, suspend the partner automatically and block transfers | Suspend regardless — no grace period |
| AUT-ESG-13 | Hazardous item received | Assign the storage location by class, check the quantity ceiling, apply the handling path; route damaged or swollen cells to the stricter path | **Block receipt** where the ceiling would be breached; alert HSE |
| AUT-ESG-14 | Material recovery weights returned by the partner | Record against the batch, compute income at the agreed rate, raise the receivable event to M20 | Manual reconciliation task |
| AUT-ESG-15 | Period close | Compute the ESG metric set from posted transactions, stamp the factor-set version, publish to M25 | Do not publish partial figures; alert Quality Manager |
| AUT-ESG-16 | Statutory return due | Assemble the return from posted data, compute progress against the EPR target in force, route for review and filing | Escalate — a late filing is a compliance event |
| AUT-ESG-17 | Corporate disposal lot received | Reconcile every declared asset to a received item; list exceptions; block closure until each is resolved | Keep the contract open |
| AUT-ESG-18 | M14 rejects a unit as unrefurbishable | Return it to M18 triage retaining its original collection record and certificate reference | Manual re-triage task |
| AUT-ESG-19 | Quarterly | Prompt the regulatory-register review; flag any instrument not reviewed within its cycle | Escalate to GRC |
| AUT-ESG-20 | Campaign-attributed collection recorded | Attribute the item, weight and disposition to the campaign for effectiveness reporting | Log unattributed |

---

## 12. Interfaces

### 12.1 Upstream — M18 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M06 Data Services** | **Destruction certificate — hard gate** | **Synchronous REST, fails closed** + `wipe.certified` / `wipe.failed` events |
| M14 Trade-In & Refurbishment | Units failing refurbishment; residuals after harvesting | Command |
| M13 Rental | Retired fleet units with no resale value | Command |
| M01 / M31 Service | Unrepairable service outcomes offered for disposal | Event |
| M15 Spare Parts | Obsolete and scrap stock written off for disposal | Command |
| M49 Fixed Assets | Internally written-off equipment | Event |
| M03 Logistics | Collection and transfer consignment status, custody events | Event |
| M33 Party Master | Customers, corporate clients and recycling partners | REST |
| M16 / M42 Procurement | Partner contracts and performance history | REST |
| M17 Asset Registry | Asset identity where the item is a known asset | REST |
| M10 Loyalty | Incentive eligibility and issuance | REST |
| M35 Marketing | Campaign definitions for attribution | REST |

### 12.2 Downstream — M18 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M14 Trade-In & Refurbishment | Units triaged as refurbishable, with their collection and certificate history | Command |
| M15 Spare Parts | Harvest candidates and the resulting parts | Command |
| M24 Documents | Disposal certificates, manifests, hazmat declarations, evidence packs | Command |
| M20 Receivable | Material recovery income and corporate disposal charges | Events |
| M60 GRC | Compliance events, custody gaps, certificate exceptions, partner suspensions | Events |
| M23 Quality | Triage variance, exception rates, weight reconciliation failures | Events |
| M59 HSE | Hazmat storage breaches and handling exceptions | Events |
| M42 Supplier Performance | Partner certificate timeliness, reconciliation accuracy, audit outcomes | Events |
| M17 Asset Registry | End-of-life state on a known asset | Events |
| M25 Business Intelligence | The computed ESG metric set, GRI-structured | Warehouse extract |
| M35 Marketing | Campaign attribution and publishable figures | REST |
| M10 Loyalty | Incentive triggers on confirmed receipt | Command |
| P01 Customer Portal | Collection booking, status, personal diversion contribution | REST |
| P04 Corporate Portal | Disposal reconciliation, per-unit certificates, client ESG extract | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `ewaste.collected` | collection, source, items, weight, campaign | M25, M10, M35 |
| `ewaste.triaged` | item, disposition, assessor, criteria version | M14, M15, M25 |
| `ewaste.gate_blocked` | item, reason, days blocked | M23, Quality |
| `ewaste.cleared` | item, certificate reference, disposition | M14, M15 |
| `ewaste.batched` | batch, material class, item count, net weight | M03, M25 |
| `ewaste.transferred` | batch, partner, manifest, PIC reference | M24, M60, M03 |
| `ewaste.disposal_certified` | batch, certificate, covered items | **M24**, M25, M60 |
| `ewaste.certificate_exception` | batch, uncovered items, partner, age | **M60**, M23 |
| `ewaste.partner_suspended` | partner, reason (expiry / performance) | M16, M42, M60 |
| `ewaste.hazmat_ceiling_breach` | location, class, quantity, ceiling | **M59**, M47 |
| `ewaste.custody_gap` | item, last known custody, detected at | **M60**, M03 |
| `esg.metrics_published` | period, metric set, factor version | M25, M35, P04 |
| `esg.statutory_return_filed` | authority, period, volumes, EPR achievement | M60, M24 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-ESG-01 | **Department of Environment** — registration, e-waste management plan, statutory returns | Outbound | Regulatory filing and evidence submission |
| INT-ESG-02 | **BTRC** — telecom WEEE reporting | Outbound | Sector-specific returns under the 2022 guidelines |
| INT-ESG-03 | Recycling partner portals / data exchange | Bidirectional | Transfer notes out, disposal certificates and recovery weights back |
| INT-ESG-04 | Weighbridge and platform scales | Inbound | Verified gross, tare and net weights |
| INT-ESG-05 | Emissions factor sources | Inbound | Versioned factor sets for avoided-emissions estimation |
| INT-ESG-06 | Basel / competent-authority PIC documentation | Outbound | Prior-informed-consent evidence for any cross-border movement |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/ewaste/collections` | POST | Book or record a collection | P01, branch |
| `/api/v1/ewaste/items` | POST | Record a received item | Branch, warehouse |
| `/api/v1/ewaste/items/{id}/triage` | POST | Record a disposition decision | Triage assessor |
| `/api/v1/ewaste/items/{id}/gate` | GET | Destruction-gate status | Internal, audit |
| `/api/v1/ewaste/batches` | POST | Assemble a batch | Warehouse |
| `/api/v1/ewaste/batches/{id}/transfer` | POST | Execute a transfer (runs every block check) | Quality Manager |
| `/api/v1/ewaste/disposal-certificates` | POST | Record a received certificate and reconcile it | Quality Manager |
| `/api/v1/ewaste/partners/{id}/status` | GET | Certification currency and suspension state | Procurement, internal |
| `/api/v1/esg/metrics` | GET | Published, GRI-structured metric set for a period | P06, M25, M35 |
| `/api/v1/esg/evidence-pack` | GET | Complete audit evidence pack for a period | Quality Manager, auditor |
| `/api/v1/ewaste/corporate-disposals/{id}/reconciliation` | GET | Client reconciliation and per-unit certificates | P04 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R32 Quality Manager / ISO Coordinator** | C R U D A | All e-waste — triage policy, transfers, certificates, returns, evidence packs |
| R20 Warehouse Operative | C R U | Receipt, weighing, batching, storage within own location |
| R18 Branch Store Keeper | C R | Collection receipt at own branch |
| Triage Assessor (R10/R12 technician with the competency) | C R U | Triage assessments on assigned items |
| R17 Inventory Manager | R U | Harvest routing and stock destination |
| R19 Procurement Officer | C R U | Partner register, qualification, downstream declarations |
| R15 Logistics Coordinator | R U | Collection and transfer consignments |
| HSE Officer | R U A | Hazmat rules, storage ceilings, damaged-cell handling |
| R26 Finance Manager | R U | Material recovery income and corporate disposal charges |
| R23 Marketing Manager | R | Published metrics and campaign attribution — **published figures only, never raw records** |
| R22 Account Manager (Corporate) | R | Corporate disposal reconciliation for assigned accounts |
| CFO | R A | Statutory returns, penalties exposure, write-off approval |
| R38 External Party (recycling partner) | C R | **Only their own transfers and certificates** — submit certificates and recovery weights, view their own batches |
| R38 External Party (auditor) | R | Read-only evidence pack for a defined period |
| R36 Customer | C R | Own collection bookings and personal diversion contribution |
| R37 Corporate Portal User | R | Own organisation's disposal reconciliation and certificates |

**Field-level restrictions.** Material recovery rates and income are visible to Finance,
Procurement and the Quality Manager only. Partner commercial terms are not visible to
operations staff. A recycling partner sees only records naming them.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Triage assessor **and** transfer authoriser for the same item | The person who decides an item is worthless cannot alone send it away |
| Anyone in M18 **and** issuing a destruction certificate | The gate must be operated by M06 |
| Partner qualification **and** transfer execution | Qualification is a control on execution; one person cannot hold both |
| Material recovery recording **and** income invoicing | Cash control |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Collection dashboard | Quality Manager, Branch Operations | Daily | Items and weight collected by channel, branch, campaign; against the annual target |
| Triage disposition analysis | Quality Manager, Retail Operations | Weekly | Disposition mix, refurbishment rate, assessor variance, criteria-version drift |
| Gate compliance | Quality Manager, CFO | Daily | Items awaiting certificate, days blocked, and **any item transferred without one (must be zero)** |
| Partner certification status | Procurement, Quality Manager | Weekly | Certification expiry runway, suspensions, blocked transfers, audit dates |
| Transfer and certificate register | Quality Manager, auditor | Monthly | Every batch, partner, manifest, certificate and its item-level reconciliation |
| Certificate exception report | Quality Manager, GRC | Weekly | Overdue certificates, unreconciled items, ageing, partner attribution |
| Material recovery report | Finance, Procurement | Monthly | Weights by material class, rates, income, variance to expectation |
| Hazardous material position | HSE Officer, Facilities | Daily | Quantity by class and location against ceilings; damaged-cell holdings |
| Chain-of-custody exceptions | Quality Manager, GRC | Weekly | Custody gaps, unsigned handoffs, weight reconciliation failures |
| **ESG / sustainability report (GRI 306 structured)** | CEO, Marketing, corporate clients | Quarterly | Waste generated; diverted from disposal by recovery operation; directed to disposal; each split hazardous / non-hazardous; diversion rate; avoided emissions with factor version |
| Statutory return pack | Quality Manager, CFO, DoE / BTRC | Per instrument | Volumes collected, treated, recovered, disposed; EPR target progress |
| Audit evidence pack | Regulator, brand partner, ISO 14001 auditor | On demand | Complete period evidence: collections, dispositions, certificates, manifests, partner certifications, exceptions |
| Corporate disposal reconciliation | Account Manager, corporate client | Per project | Declared assets against received items, destruction and disposal certificates, exceptions |
| Campaign effectiveness | Marketing Manager | Per campaign | Collections attributed, weight, disposition mix, incentive cost per kilogram |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W8 Target | W9 Target |
|---|---|---|---|---|
| — | Devices collected per year | untracked | 15,000 run-rate | **25,000** |
| **KPI-083** | Diversion from landfill | untracked | 88% | **> 92%** |
| **KPI-084** | Disposal certificates on file | 0% | **100%** | **100%** |
| — | **Items transferred without a destruction certificate** | untracked | **0** | **0** |
| — | **Transfers to a partner with expired certification** | untracked | **0** | **0** |
| — | Refurbishment rate of collected units (routed to M14) | untracked | 25% | **> 30%** |
| — | Certificate reconciliation at item level | 0% | 95% | **> 99%** |
| — | Certificates received within the agreed window | n/a | 90% | **> 95%** |
| — | Chain-of-custody gaps | untracked | **0** | **0** |
| — | Hazmat storage ceiling breaches | untracked | **0** | **0** |
| — | Material recovery income | 0 | BDT 7 lac run-rate | **BDT 12 lac/year** |
| — | Statutory returns filed on time | n/a | **100%** | **100%** |
| — | EPR collection target achievement | unmeasured | Target in force | Target in force |
| — | Regulatory register items reviewed within cycle | n/a | **100%** | **100%** |
| — | Triage assessor variance on audit re-assessment | n/a | < 10% | **< 5%** |

**Seven of these targets are zero or one hundred per cent.** In a compliance module, a partial
score is a breach with a percentage attached to it.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `stock` (locations, lots, moves), `documents`, `survey` (triage checklists) | 20% |
| L2 | OCA stock and quality extensions | 7% |
| L5 | `cd_ewaste`, `cd_recycling`, `cd_esg_report` | 73% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 3 identifiers below are claimed by another module: **CD-080** also claimed by M56; **CD-081** also claimed by M57; **CD-082** also claimed by M57. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-080 | `cd_ewaste` — collection channels and points, item record, triage and disposition log, **destruction gate**, hazmat rules and quantity ceilings, donation routing, corporate disposal reconciliation | Odoo module | 6 PW |
| CD-081 | `cd_recycling` — partner register with certification currency and downstream declarations, batch assembly and weight reconciliation, transfer notes and manifests, Basel PIC control, disposal certificate receipt and item-level reconciliation, material recovery accounting | Odoo module | 4 PW |
| CD-082 | `cd_esg_report` — regulatory register, statutory returns with EPR target tracking, versioned factor sets, GRI 306-structured metric computation, evidence-pack assembly, campaign attribution | Odoo module | 3 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M06 Data Services** | The destruction gate. M18 cannot transfer anything without it |
| **M14 Trade-In & Refurbishment (W6)** | Triage needs a refurbishment destination to route to, and M14 needs a recycling destination for its failures. They must not be separated by more than one wave |
| M03 Service Logistics | Collection and transfer consignments with custody |
| M15 Spare Parts | Harvested-part destination |
| M24 Documents | Certificate and manifest retention |
| M16 / M42 Procurement | Partner contracting |
| M33 Party Master | Customers, corporate clients and partners |
| M60 GRC | Compliance event escalation |
| M10 / M35 | Collection incentives and awareness campaigns |

**Sequencing note.** M14 goes live in W6 and M18 in W8 — a two-wave gap in which M14 has no
system-managed recycling destination for its rejected units. Rejected units in that window must
be held in a controlled quarantine location with their certificates, and processed through M18
when it lands. The alternative — pulling M18 forward to W7 — should be considered if
refurbishment reject volumes in W6 run above forecast.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Existing accumulated e-waste at branches and warehouses | All held stock | `fix.ewaste.item` with source = *pre-implementation backlog* | W8 cutover |
| Existing recycler relationships | All active partners | `fix.recycling.partner` with certification verified afresh | W8 cutover |
| Historical disposal records | **Not migrated** — no certificates, weights or custody evidence exist, so the records cannot support a statutory return or an audit | — | — |

**Cutover control.** The pre-implementation backlog is the largest single exposure this module
inherits: devices already held, of unknown origin, some data-bearing, with no certificates.
Every backlog item must go through the full gate — triage, destruction, certification, transfer
— exactly as a new item would. None may be grandfathered, and the backlog clearance should be
planned and resourced as a project in its own right, not absorbed into go-live.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **An item cannot be transferred to a recycler without a valid M06 certificate**, and the gate fails closed when M06 is unavailable | Negative test plus fault injection |
| AC-02 | A storage device cannot be harvested or donated without a certificate | Negative test |
| AC-03 | **A transfer to a partner whose certification expired yesterday is blocked**, with the reason stated | Negative test with a time-shifted expiry |
| AC-04 | A transfer with an incomplete manifest or missing hazmat declaration is blocked | Negative test |
| AC-05 | A batch whose net weight does not reconcile to the sum of item weights within tolerance cannot be transferred | Boundary test |
| AC-06 | A cross-border transfer without a recorded Basel PIC reference is blocked | Negative test |
| AC-07 | Every item in a transferred batch reconciles to a returned disposal certificate, and any uncovered item raises an exception that cannot be closed silently | Scripted scenario with a deliberate short certificate |
| AC-08 | A triage decision cannot be edited after it is made; a change creates a new record referencing the prior one | Tamper test |
| AC-09 | Receipt of a hazardous item that would breach the location's quantity ceiling is blocked and alerted | Boundary test |
| AC-10 | Damaged or swollen cells cannot be batched with sound cells | Negative test |
| AC-11 | **No user interface or API path allows a published environmental figure to be entered manually** | Data-model review and query audit |
| AC-12 | Every published figure carries the emissions-factor version used, and restating with a new factor set produces an explainable difference | Restatement test |
| AC-13 | A complete audit evidence pack for a 12-month period assembles on demand without manual collation | Timed export test |
| AC-14 | The statutory return computes volumes and EPR target progress from posted data | Reconciliation against the item ledger |
| AC-15 | A corporate disposal contract cannot close with any declared asset unreconciled | Scripted project with 100 assets and three deliberate exceptions |
| AC-16 | A chain-of-custody gap is detected and raised as an exception rather than silently tolerated | Injected-gap test |
| AC-17 | A unit rejected by M14 returns to triage retaining its original collection record and certificate reference | Integration test |
| AC-18 | The pre-implementation backlog has been fully processed through triage, destruction and certification | Backlog clearance record |
| AC-19 | Quality Manager and CFO sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 19 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is 1000FiX registered with the Department of Environment under the Hazardous Waste (E-waste) Management Rules 2021, and has an e-waste management plan been submitted and approved?** The Company is inside scope as a repairer and seller | Quality Manager / CEO | **Immediately — this is a live legal exposure, not a design input** |
| Q-02 | **Is there an existing backlog of e-waste held at branches or warehouses?** If so, how much, and does any of it contain undestroyed data? | Quality Manager | **Immediately** |
| Q-03 | Does the EPR collection-target obligation apply to 1000FiX as a seller and repairer, and at what percentage in the current year? | Legal / Quality Manager | **W8 minus 4 months** |
| Q-04 | Which DoE-licensed recyclers operate in Bangladesh, for which material classes, and what is their certification currency? | Procurement Officer | W8 minus 3 months |
| Q-05 | Which material streams have no domestic processing capacity and would require cross-border movement under Basel PIC? | Quality Manager / Legal | W8 minus 3 months |
| Q-06 | What are the material recovery rates achievable in the local market, and are they contracted or spot? | Procurement Officer / CFO | W8 minus 2 months |
| Q-07 | Where will lithium-ion batteries be stored, and does the facility meet segregation, ventilation, temperature and suppression requirements? | HSE Officer / Facilities | **W8 minus 3 months** |
| Q-08 | What collection incentive is affordable per device, and does it change customer behaviour enough to reach 25,000 units a year? | Marketing Head / CFO | W8 build |
| Q-09 | Which emissions-factor set will be used for avoided-emissions estimation, and who approves a change to it? | Quality Manager | W8 build |
| Q-10 | Does the Company intend to pursue **ISO 14001** or **R2v3** certification, and on what timeline? | CEO / Quality Manager | W9 |
| Q-11 | Do any brand or OEM partners impose their own downstream disposal requirements on authorised service partners? | Account Management / Quality Manager | W8 minus 2 months |
| Q-12 | Should M18 be pulled forward to W7 to close the gap with M14's W6 launch? | Programme Director | **W6 minus 1 month** |

**Q-01 and Q-02 are not design questions.** They are current-state compliance exposures with
criminal penalties attached, and they should be investigated now, independently of the ERP
programme.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category D §3 the circular flow, §4 the non-negotiable gate, §7 KPIs) ·
`M14_TradeIn_Refurbishment_and_Resale.md` (refurbishment source and rejection destination) ·
`M13_Rental_and_Equipment_as_a_Service.md` (retired fleet source) ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md`
§5.4, §8.2, §12.2 (the certificate and the fail-closed gate) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §Category D ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` (FR-ESG-001…026) ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (KPI-083, KPI-084,
benefit line 13)

**Workspace evidence**
`1000fix_business/Business planning for 1000 fix.docx` §Device Recycling and Responsible
Disposal — collection points, triage, certified partners, data destruction, secure disposal,
regulatory compliance, component recovery, awareness ·
`1000FiX_Services_Company_Profile.md` §ISO 9001:2015 ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register
(BDT 12 lac)

**External benchmark and regulation**
**Hazardous Waste (E-waste) Management Rules 2021** (Department of Environment, Bangladesh,
10 June 2021, under the Environment Conservation Act 1995) — registration and approved
management plan for manufacturers, traders, sellers, transporters, repairers, recyclers and
dismantlers; EPR collection targets rising from 10% in year one to 50%; RoHS-aligned
restriction of ten substances; penalties up to two years' imprisonment or BDT 200,000, and two
to ten years or BDT 200,000–1,000,000 for repeat offences ·
**BTRC WEEE Management and Recycling Guidelines** (published 7 July 2022) ·
**Basel Convention e-waste amendments** — adopted at COP-15 (2022), in force **1 January 2025**;
all transboundary movements of e-waste, hazardous and non-hazardous, subject to the
prior-informed-consent procedure ·
**R2v3 (SERI)** — downstream due diligence obligations on certified parties for material passed
to onward vendors ·
**e-Stewards** — chain-of-custody and export-control expectations ·
**GRI 306: Waste 2020** — Disclosure 306-3 waste generated, 306-4 waste diverted from disposal
by recovery operation, 306-5 waste directed to disposal, each split hazardous / non-hazardous ·
**ESRS E5 Resource use and circular economy** (CSRD; simplified by Omnibus I, February 2026) —
resource inflows and outflows, circular material use rate, waste split into preparation for
reuse, recycling and other recovery ·
**ISO 14001** — environmental management system, legal register and operational control ·
Lithium-ion battery storage practice — segregation by chemistry and state, maximum storage
quantities, minimum separation distances, temperature control, ventilation, dedicated
suppression, and a stricter handling path for damaged or defective cells; hundreds of waste-
and recycling-facility fires are attributed to mismanaged lithium cells

**Sources consulted**
- [Enviliance ASIA — Bangladesh publishes E-waste Management Rule](https://enviliance.com/regions/south-asia/bd/report_2900)
- [ChemLinked — Bangladesh publishes E-waste Management Rules](https://chemical.chemlinked.com/news/chemical-news/bangladesh-publishes-e-waste-management-rules)
- [Transparency International Bangladesh — E-Waste Management in Bangladesh: Governance Challenges and Way Forward](https://www.ti-bangladesh.org/images/2025/report/e-waste-management/Full-Report-on-e-Waste-Management-En.pdf)
- [Enviliance ASIA — BTRC e-waste management and recycling guideline](https://enviliance.com/regions/south-asia/bd/report_3596)
- [Basel Convention — E-waste Amendments overview](https://www.basel.int/Implementation/Ewaste/EwasteAmendments/Overview/tabid/9266/Default.aspx)
- [US EPA — new international requirements for electrical and electronic waste](https://www.epa.gov/hwgenerators/new-international-requirements-electrical-and-electronic-waste)
- [SERI — R2v3 knowledge base](https://sustainableelectronics.org/knowledge-base/r2v3-appendix-determination-tool/)
- [GRI 306: Waste 2020](https://www.globalreporting.org/publications/documents/english/gri-306-waste-2020/)
- [EFRAG — ESRS E5 Resource use and circular economy](https://www.efrag.org/sites/default/files/sites/webpublishing/SiteAssets/ED_ESRS_E5.pdf)
- [Coolset — how to interpret ESRS E5 (updated March 2026)](https://www.coolset.com/academy/esrs-e5-circular-economy)
- [US EPA — analysis of lithium-ion battery fires in waste management and recycling](https://www.epa.gov/system/files/documents/2021-08/lithium-ion-battery-report-update-7.01_508.pdf)
- [EERA — lithium handling industry guidance](https://www.eera-recyclers.com/industry-guide)

---

*Module M18 · Category D · 1000FiX ERP System v2.0 · CONFIDENTIAL*
