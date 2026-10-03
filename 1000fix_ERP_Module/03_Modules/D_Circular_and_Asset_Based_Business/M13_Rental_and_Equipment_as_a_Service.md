---
id: FIX-ERP2-M13
module_id: M13
module_code: RNT
module_name: Rental & Equipment-as-a-Service
category: D — Circular & Asset-Based Business
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Corporate Services Head
system_owner: Commercial Squad
priority: P2
wave: W6
---

# M13 — Rental & Equipment-as-a-Service
### Category D · Code `RNT` · Existing (retained from v2.0)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M13 |
| **Module code** | `RNT` |
| **Category** | D — Circular & Asset-Based Business |
| **Status** | Existing (introduced in v2.0, retained in v2.1) |
| **Priority** | **P2** |
| **Delivery wave** | W6 (Months 23–26) |
| **Business owner** | Corporate Services Head |
| **System owner** | Commercial Squad |
| **Delivery layers** | L1 (Odoo `sale_renting` basis) · L2 (OCA stock and maintenance) · L5 (custom) |
| **Custom modules** | `cd_rental_asset`, `cd_rental_agreement`, `cd_condition_report`, `cd_rental_billing` |
| **Requirement range** | FR-RNT-001 … FR-RNT-044 |
| **Requirement count** | 44 |
| **Effort estimate** | 25 person-weeks |
| **Depends on** | M17 Asset Registry · M33 Party Master · M37 Catalogue · M11 Pricing · M08 Contracts · M03 Logistics · M20 Receivable · M49 Fixed Assets · M50 Treasury · M24 Documents · M29 Identity |
| **Depended on by** | M14 Trade-In & Refurbishment (retirement route) · M18 E-Waste (end-of-life route) · M20 Receivable · M53 Revenue Recognition · M39 Subscription · M25 Business Intelligence · P01 / P04 portals |

---

## 2. Purpose

M13 runs the business where **1000FiX owns the equipment and sells the use of it**, rather than
selling labour on equipment somebody else owns. It manages a fleet of rentable units across
eight asset categories, takes reservations against real availability, issues an agreement with
a tariff and a deposit, records the condition of the unit when it goes out and when it comes
back, charges for damage and late return, and keeps the asset earning until it is worth more
sold than rented.

Rental is not a variant of the service order. It is a different economic model. A repair job
succeeds when it is finished. A rental asset succeeds when it is **out on rent again tomorrow**
and comes back in the condition it left in. Everything in this module exists to protect one of
those two things: utilisation, or condition.

### Why It Exists

The Business Plan commits the Company to renting eight asset categories, and the Company
Profile already advertises a laptop rental service. That business is being run today on
spreadsheets and log books, which means nobody can answer the three questions that decide
whether rental makes money: *what proportion of the fleet is earning, what did each unit cost
us in damage and repair, and which units should we have sold six months ago.*

An asset business without utilisation and condition data is not a business — it is a slow
capital write-off. The Company already owns the assets. M13 is what turns them into a
measurable return.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Business Plan §Rental Services | Eight rentable categories: laptops, cameras, projectors, tablets, audiovisual equipment, servers, networking equipment, electronic test equipment |
| Company Profile §Laptop Rental Service | Rental is already a live, advertised service line, not a proposal |
| SOW for 1000FiX Service App | Rental is listed as a purchasable service type in the customer app |
| Scope Charter §Benefit Register | **BO-13 — establish rental as a profitable asset business**; target fleet utilisation 68%, gross margin 55%; base-case benefit **BDT 48 lac/year** |
| Category D Overview §7 | Category KPIs: utilisation > 68%, on-time return > 90%, damage recovery > 85%, loss rate < 0.5%/yr, gross margin > 55% |
| ERP BRD — asset lifecycle | "Rented Out" is a required asset lifecycle state in the shared registry |
| Module Register (02-02) | M13 `RNT`, P2, W6, Corporate Services Head, 44 requirements, 25 PW |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** Both sides of every boundary must agree. Where this
> table says a capability belongs elsewhere, that module's specification must claim it.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The rental fleet register — every rentable unit, its category, specification, condition grade and current operational status |
| 2 | Kits and accessories: what ships with a unit, and what must come back with it |
| 3 | Real-time availability by category, specification, branch and date range |
| 4 | Reservation with hold expiry, allocation rules and overbooking control |
| 5 | Rental agreement generation, e-signature capture and agreement variation |
| 6 | Customer eligibility screening for rental exposure |
| 7 | Tariff structures — hourly, daily, weekly, monthly, custom-period, cumulative and long-term EaaS |
| 8 | Security deposit calculation, hold, offset and release instruction |
| 9 | Optional damage-waiver product with excess, exclusions and per-agreement election |
| 10 | Condition reporting at dispatch and at return, with mandatory photographic evidence |
| 11 | Damage assessment, repair costing and recovery against deposit or invoice |
| 12 | Late return, extension, early return and non-return handling |
| 13 | Loss, theft and insurance-claim workflow for rental assets |
| 14 | In-rental support and swap-out against a contracted response time |
| 15 | Between-rental turnaround: clean, test, service, re-grade, return to pool |
| 16 | Preventive maintenance scheduling by calendar or usage for fleet units |
| 17 | Utilisation measurement — both time utilisation and financial (dollar) utilisation |
| 18 | Fleet health, cumulative cost per unit, and the retire-or-continue recommendation |
| 19 | Sub-rental (cross-hire) from partners when own fleet cannot cover demand |
| 20 | Corporate framework rental agreements with call-off orders |
| 21 | Equipment-as-a-Service: multi-month bundles of hardware, maintenance and support |
| 22 | Rental self-service through the customer and corporate portals |
| 23 | Rental analytics: utilisation, revenue per asset, damage, loss and margin |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Asset identity, serial number and lifetime history | **M17** Device & Asset Registry | One asset identity for the whole enterprise. M13 holds the *rental* attributes of a unit, never a second identity for it |
| Capitalisation, depreciation, revaluation and disposal accounting | **M49** Fixed Assets | M13 sees an operational asset; Finance sees a capital asset. Two views, one register |
| Physical delivery, collection and custody in transit | **M03** Service Logistics | M13 raises a consignment request; M03 moves the goods and owns the custody trail |
| Invoicing, credit notes, dunning and collections | **M20** Receivable | Only Category G handles money. M13 produces charge lines |
| Deposit ledger, escrow and refund execution | **M20** / **M50** | M13 calculates and instructs; Finance holds and releases the cash |
| Recurring billing runs for long rentals and EaaS | **M39** Subscription | M13 supplies the billing basis and usage; M39 runs the cycle |
| Lessor lease classification and revenue recognition schedules | **M53** Revenue Recognition | M13 tags an agreement's term and structure; M53 decides the accounting treatment |
| Price list construction, discount policy and approval thresholds | **M11** Pricing & Rate Cards | M13 consumes an approved tariff; it never invents a price |
| Repair execution on a damaged or failed rental unit | **M31** Workshop / **M02** Field Service | Rental raises the work; the service modules do it, with the cost posted back |
| Spare parts consumed in that repair | **M15** Spare Parts & Inventory | Parts are always issued from stock, never from the rental module |
| Refurbishment and resale of a retired fleet unit | **M14** Trade-In & Refurbishment | M13 decides *when* to retire; M14 decides what it is worth and sells it |
| Recycling of an unsellable retired unit | **M18** E-Waste | Same boundary, other exit |
| Certified data destruction on a returned or retired unit | **M06** Data Services | M13 requests; M06 performs and certifies |
| Contract templates, clause library and legal approval | **M08** Contract Lifecycle | M13 instantiates an approved template |
| Customer identity, KYC and NID verification | **M33** Party Master | M13 asks whether the party is verified; it does not verify |
| Insurance policy administration for the fleet | **M60** GRC / **M49** | M13 raises a claim event; policy administration sits with Finance and GRC |
| Telemetry ingestion and predictive failure models | **M48** IoT & Predictive | Where telemetry exists, M13 consumes the derived signal |

### 3.3 Shared Concepts

| Concept | M13's Role | Owning Module |
|---|---|---|
| Asset / serial identity | References; adds rental attributes | M17 |
| Fixed asset record and depreciation schedule | References; supplies utilisation and disposal trigger | M49 |
| Rental agreement | **Owns** | M13 (template from M08) |
| Tariff / rate card | Consumes an approved rate card | M11 |
| Reservation and availability | **Owns** | M13 |
| Condition report | **Owns** | M13 (evidence retained by M24) |
| Damage charge | Assesses and prices | M20 invoices |
| Security deposit | Calculates and instructs | M20 / M50 hold |
| Consignment | Requests | M03 |
| Preventive maintenance plan | Defines for fleet units | M45 pattern, M17 record |
| Customer account and credit standing | Reads | M33 / M20 |
| Utilisation metric | **Owns the definition and calculation** | M25 visualises |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Wynne Systems RentalMan** *(enterprise rental ERP)* | Rules-based rate engine applying daily / weekly / monthly tiers automatically; contract-to-invoice in one workflow | **Cumulative rate laddering** — the system always charges the cheapest correct combination of period rates for the actual duration, without the counter clerk calculating it | Its construction-fleet depth: hauling, yard bays, telematics-heavy fleet control |
| **Texada** *(rent-and-service on the same fleet)* | Rental and internal service management on one asset record — work orders, parts, technician scheduling against rented units | **The core structural idea**: the same unit is a rental asset and a serviceable asset simultaneously, and both histories live on one identity | Its dealership/OEM orientation |
| **Point of Rental** | Reservation, contract, delivery, return inspection, damage capture, utilisation reporting for SMB-to-midmarket general rental | Return-inspection-first design; kit and accessory tracking; counter speed | Party and event rental features |
| **United Rentals / Sunbelt — Rental Protection Plan** | An optional damage waiver (explicitly *not insurance*) at a percentage of gross rental, with a stated excess and named exclusions — typically excluding theft without evidence, gross negligence and abuse | **The commercial construct**: an elective waiver line, a published excess, published exclusions, and recovered equipment remaining Company property regardless of any payment made | The 15%-of-rental price point — priced locally against Bangladeshi deposit norms |
| **Odoo 19 Rental (`sale_renting`)** | Quotation → order → pickup → return → invoice; per-product security deposit; configurable late-return cost per hour and per day; padding time between rentals; serial-number tracking; multiple pickup and return locations | **Used as the L1 transactional spine** — order, pickup, return, deposit field, padding, late-fee basis | Its condition model (none), damage workflow (none), utilisation analytics (none), eligibility (none) and multi-branch availability logic (thin). These are the reasons L5 exists |
| **IFS Cloud / SAP S/4HANA rental** | Lessor treatment, service-integrated rental, contract variation | Agreement variation as a first-class event with a full audit trail | Full lessor sub-ledger — that is M53 and M49 |
| **ISO 15143-3 (AEMP 2.0)** *(equipment telematics standard)* | A vendor-neutral JSON interface exposing asset identity, location, cumulative operating hours, idle time and utilisation from mixed-brand telematics | **The interface shape** for any future telematics feed, so 1000FiX never builds a per-vendor connector | Adopting telematics hardware now. IT equipment is not construction plant |
| **Equipment rental KPI practice** | *Time utilisation* = days on rent ÷ days available. *Financial (dollar) utilisation* = annual rental revenue ÷ original equipment cost. Industry sweet spot 65–75% time utilisation; under 60% signals over-fleeting, over 80% signals lost demand | **Both metrics, as first-class computed fields on every unit and category.** Time utilisation alone hides an idle high-value server behind a busy projector | Single-metric reporting |
| **DaaS / Device-as-a-Service providers** | Hardware + deployment + support + end-of-life bundled into one monthly per-device fee, shifting the customer from capex to opex | **The EaaS commercial shape**, which 1000FiX can serve better than a pure lessor because it already owns the repair network | Financing and residual-value underwriting — the Company is not a leasing company |

**Design position.** Six deliberate differences, each forced by the Bangladeshi context or by
what 1000FiX already is.

**First, eligibility is deposit-and-identity-led, not credit-score-led.** There is no accessible
consumer credit bureau to score an individual renter against. The controls that actually work
here are verified NID identity through M33, a risk-tiered deposit, and the Company's own
rental history for that party. The system therefore computes a *rental exposure limit* per
party from those three inputs, and blocks a rental that would exceed it.

**Second, the swap-out SLA is the product, not a service level.** Every competitor can rent a
laptop. Almost none can put a replacement in the customer's hands the same day, because they
have no branch network and no technicians. 1000FiX has both. M13 therefore makes the swap
commitment a contracted, measured term of the agreement — this is the module's commercial
moat and it is deliberately expensive for a pure rental firm to copy.

**Third, photographic condition evidence is mandatory at both ends, and the system refuses to
proceed without it.** Every rental dispute in this industry is a condition dispute, and every
condition dispute is lost by whoever has no photograph. Dispatch cannot complete without an
outbound condition report; return cannot close without an inbound one taken against it.

**Fourth, no GPS telematics on IT assets — device enrolment instead.** Fitting trackers to
laptops and projectors is disproportionate. For laptop and tablet fleets, the equivalent
control is enrolment in the managed-device tooling M05 already operates, giving last-check-in
and, where contractually agreed, remote lock. High-value AV, server and test equipment stays
under deposit and custody control. The ISO 15143-3 interface is defined but not populated.

**Fifth, deposits are never revenue.** A deposit is a liability from the moment it is taken.
M13 calculates and instructs; it has no ability to recognise a deposit as income, and the
deposit release is a Finance action, not a counter action.

**Sixth, retirement is a computed recommendation, not an opinion.** When cumulative repair cost
on a unit crosses a category threshold against its written-down value, or its utilisation
falls below a floor for two consecutive quarters, the system proposes retirement and routes
the unit to M14. Fleets rot when nobody is accountable for the decision to stop.

---

## 5. Functional Areas & Features

### 5.1 Rental Fleet & Asset Pool

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-001 | Rental asset register | Register every rentable unit against its M17 asset identity, with rental category, specification profile, acquisition cost, current condition grade, home branch and operational status | P2 | L5 |
| FR-RNT-002 | Asset status lifecycle | Track and enforce the states Available · Reserved · Allocated · Out on Rent · In Transit · In Turnaround · Under Service · Quarantined · Retired · Sold · Lost, with only permitted transitions | P2 | L5 |
| FR-RNT-003 | Category & specification model | Model rentable categories with searchable attributes (processor, RAM, lumens, sensor, port count, throughput) so a customer selects by specification rather than by unit | P2 | L5 |
| FR-RNT-004 | Accessories & kits | Define the kit that ships with each category — chargers, cases, cables, lenses, tripods, remotes, rack rails — and track each component's dispatch and return individually | P2 | L5 |
| FR-RNT-005 | Fixed-asset linkage | Link every rental unit to its M49 fixed-asset record and depreciation schedule, and expose written-down value to the retirement calculation | P2 | L5 |
| FR-RNT-006 | Utilisation tracking | Compute, per unit and per category, **time utilisation** (days on rent ÷ days available) and **financial utilisation** (rolling 12-month rental revenue ÷ acquisition cost) | P2 | L5 |
| FR-RNT-030 | Fleet composition planning | Report demand-versus-supply by category and specification, and recommend acquisition, redeployment between branches, or disposal | P3 | L5 |
| FR-RNT-031 | Inter-branch redeployment | Transfer a fleet unit between branches with a consignment, preserving utilisation history and re-homing the unit | P2 | L5 |

### 5.2 Availability, Reservation & Agreement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-007 | Availability calendar | Present real-time availability by category, specification, branch and date range, net of reservations, turnaround padding and scheduled maintenance | P2 | L5 |
| FR-RNT-008 | Reservation | Reserve by category (soft) or by specific unit (hard), with hold expiry, configurable overbooking tolerance per category, and automatic release on expiry | P2 | L5 |
| FR-RNT-009 | Rental agreement | Generate the agreement from an approved M08 template carrying period, tariff, deposit, waiver election, usage limits, liability terms and swap SLA, and capture e-signature | P2 | L5 |
| FR-RNT-010 | Customer eligibility & exposure limit | Check verified identity, outstanding balance, rental history and open exposure before approval, and block a rental that breaches the computed exposure limit unless overridden with a recorded justification | **P1** | L5 |
| FR-RNT-011 | Corporate framework rentals | Support master rental agreements with call-off orders, agreed rate cards, nominated approvers and consolidated billing | P2 | L5 |
| FR-RNT-012 | Long-term rental & EaaS | Support multi-month Equipment-as-a-Service arrangements bundling hardware, preventive maintenance, support response and end-of-term return or purchase | P3 | L5 |
| FR-RNT-032 | Allocation at pick | Convert a category reservation into a specific unit at dispatch, choosing by condition grade, utilisation balancing and maintenance proximity | P2 | L5 |
| FR-RNT-033 | Agreement variation | Vary an in-flight agreement — period, units, tariff, waiver — as a versioned amendment with re-signature where terms are material | P2 | L5 |
| FR-RNT-034 | Sub-rental / cross-hire | Where own fleet cannot cover a confirmed demand, procure a unit from a partner, track partner cost against the agreement and mark the unit as non-owned throughout | P3 | L5 |

### 5.3 Tariffs, Deposits & Charging

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-013 | Tariff structures | Define hourly, daily, weekly, monthly and custom-period tariffs per category with volume, duration and corporate discounts, sourced from an approved M11 rate card | P2 | L5 |
| FR-RNT-014 | Security deposit | Calculate the deposit from category, unit value and customer risk tier; instruct collection; hold as a liability; offset or instruct refund at closure | P2 | L5 |
| FR-RNT-015 | Metered usage charges | Charge for metered consumption where applicable — projector lamp hours, print counts, server hours — against an included allowance | P3 | L5 |
| FR-RNT-016 | Extension | Extend a rental in flight, checking availability against downstream reservations and re-pricing on the cumulative rate ladder | P2 | L5 |
| FR-RNT-017 | Early return | Handle early return under the agreed minimum-period and refund rules, releasing the unit to availability immediately | P2 | L5 |
| FR-RNT-018 | Late return charges | Apply overdue charges automatically at the configured hourly or daily rate, with escalating notification to the customer and the account owner | P2 | L5 |
| FR-RNT-019 | Recurring invoicing | Generate the recurring billing basis for long rentals and EaaS and pass it to M39 / M20 on the agreed cycle | P2 | L5 |
| FR-RNT-035 | Cumulative rate laddering | Always price the actual duration at the cheapest correct combination of the applicable period rates, and show the customer the applied ladder | P2 | L5 |
| FR-RNT-036 | Damage waiver product | Offer an elective damage-waiver line priced as a percentage of gross rental, carrying a published excess and published exclusions, recorded per agreement and applied automatically at damage assessment | P2 | L5 |
| FR-RNT-037 | Rental order-to-cash handoff | Produce all chargeable lines — rental, waiver, metered usage, late fee, damage, loss — as costed events for M20, never as invoices | P2 | L5 |

### 5.4 Dispatch, Condition & Return

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-020 | Pre-dispatch check | Complete a functional and cosmetic check against the category checklist before dispatch, blocking release on a failed mandatory item | P2 | L5 |
| FR-RNT-021 | Condition report — out | Produce a signed outbound condition report with **mandatory photographs**, itemised accessories, meter readings and declared defects; dispatch cannot complete without it | **P1** | L5 |
| FR-RNT-022 | Delivery & collection | Raise M03 consignments for delivery and collection, tracking custody transfer at both ends | P2 | L5 |
| FR-RNT-023 | Condition report — in | Complete the return inspection **against the outbound report**, presenting the outbound photographs side by side and itemising every difference | **P1** | L5 |
| FR-RNT-024 | Damage assessment & charging | Quantify damage, price the repair from the parts and labour catalogue, apply the waiver excess where elected, offset against deposit and raise the balance as a charge | P2 | L5 |
| FR-RNT-025 | Loss, theft & non-return | Handle non-return with escalating recovery steps, agreed replacement valuation, insurance claim initiation, legal escalation and asset write-off, retaining Company ownership of any recovered unit | P2 | L5 |
| FR-RNT-026 | Turnaround between rentals | Route every returned unit through clean, test, service-if-needed and re-grade before it re-enters the available pool, with a category-specific turnaround time | P2 | L5 |
| FR-RNT-038 | Mobile condition capture | Capture condition reports on a mobile device with offline queueing, forced photograph capture, and customer signature on glass | P2 | L5 |
| FR-RNT-039 | Data handling on return | For any returned data-bearing unit, raise an M06 destruction request before the unit re-enters the pool or leaves for retirement, and block both transitions until it is certified | **P0** | L5 |

### 5.5 In-Rental Support, Maintenance & Fleet Health

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-027 | In-rental support & swap-out | Accept a fault report against a live rental, dispatch support or a replacement unit within the contracted response time, and record the swap with condition reports on both units | P2 | L5 |
| FR-RNT-028 | Preventive maintenance | Schedule maintenance by calendar interval or accumulated usage per category, reserving the unit out of availability for the window | P2 | L5 |
| FR-RNT-029 | Fleet health & retirement | Accumulate repair cost, damage incidents, downtime and revenue per unit, and raise a retirement recommendation when cost-to-value or utilisation thresholds are breached | P2 | L5 |
| FR-RNT-040 | Retirement & disposal routing | On approved retirement, route the unit to M14 for refurbishment and resale, or to M18 where no resale value exists, and notify M49 for disposal accounting | P2 | L5 |
| FR-RNT-041 | Device enrolment control | For laptop and tablet fleets, record enrolment in the managed-device tooling, expose last check-in, and support contractually-agreed remote lock on confirmed non-return | P3 | L5 |
| FR-RNT-042 | Telemetry interface | Where a unit exposes telemetry, ingest operating hours, location and idle time through an **ISO 15143-3-shaped** interface and reconcile against declared usage | P3 | L5 |

### 5.6 Self-Service & Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-RNT-043 | Rental self-service | Let customers browse availability, reserve, sign, extend, report a fault, book a collection and view their condition reports and charges through the customer and corporate portals | P2 | L5 |
| FR-RNT-044 | Rental analytics | Report utilisation (both measures), revenue per asset per month, damage recovery rate, loss rate, turnaround time, on-time return rate and gross margin, by unit, category, branch and customer segment | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Availability engine** | Availability is computed from confirmed reservations, allocations, turnaround padding, maintenance windows and in-transit state — never from a stored "available" flag that can drift |
| T-02 | **Double-booking prevention** | Unit allocation is serialised under a transactional lock; two concurrent confirmations for the same unit and overlapping window cannot both succeed |
| T-03 | **Cumulative rate resolution** | The rate ladder is evaluated deterministically and the applied combination is persisted with the agreement line, so a price can be reproduced years later |
| T-04 | **Condition evidence integrity** | Condition photographs are hashed at capture, stored immutably in M24 with capture time, device and operator, and cannot be replaced after the report is signed |
| T-05 | **Offline condition capture** | The mobile condition flow operates fully offline and syncs on reconnection with conflict detection; a report captured offline is not valid until synced and hashed |
| T-06 | **Deposit is a liability, always** | The deposit posting path is a liability account only. The module exposes no path to recognise a deposit as revenue |
| T-07 | **Destruction-gate call** | The M06 certificate check on any data-bearing return or retirement is synchronous and **fails closed** — no certificate, no pool re-entry, no retirement |
| T-08 | **Utilisation as a computed series** | Utilisation is stored as a daily time series per unit, so any period, category or branch rollup is derivable without recomputation from transactions |
| T-09 | **Serial-level traceability** | Every agreement line, condition report, damage assessment, charge and movement binds to a specific serial number, never to a category |
| T-10 | **Idempotent charge generation** | Charge events carry an idempotency key; a retried return or extension never double-charges |
| T-11 | **Telemetry interface shape** | The telemetry ingress conforms to the ISO 15143-3 (AEMP 2.0) field set — asset identity, location, cumulative hours, idle time — so any future provider plugs in without redesign |
| T-12 | **Performance** | Availability query across the fleet ≤ 800 ms; condition report sync ≤ 5 s per report with up to 20 photographs; utilisation dashboard ≤ 3 s |
| T-13 | **Evidence retention** | Condition reports, signatures and damage evidence are retained for the statutory limitation period plus one year, and are exportable as a dispute pack |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M13 |
|---|---|---|
| **Rental coordinator** | Availability confirmed by phoning branches and checking a log book; overbooking discovered on the day | Real availability on one screen; reservation that cannot double-book |
| **Counter / front-desk staff** | Writes the agreement by hand; deposit amount decided by judgement | Agreement generated with the correct tariff and deposit; e-signed at the counter |
| **Delivery rider** | Hands over the unit and hopes | Captures the condition report on the phone, photographs forced, customer signs on glass |
| **Return inspector** | Argues with the customer about a scratch nobody photographed | Opens the outbound photographs side by side and itemises the actual difference |
| **Corporate Services Head** | Cannot say what proportion of the fleet is earning | Time and financial utilisation per unit, per category, per branch, daily |
| **Technician** | Services a rental unit as an unbilled favour | Works a costed job against the unit, and that cost lands in the retirement calculation |
| **Account manager (corporate)** | Quotes rental from a rate sheet of uncertain vintage | Quotes from a live rate card with a framework agreement and call-off |
| **Finance Manager** | Deposits mixed into revenue; damage rarely recovered | Deposits held as liabilities; damage assessed, priced and recovered as a measured rate |
| **CFO** | Owns assets of unknown return | Revenue per asset per month against written-down value, and a retirement recommendation with a number behind it |
| **Customer** | Rings the branch to ask if anything is free | Sees availability, books, signs, extends and reports a fault from the portal |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Rental gross margin** | A managed asset business with measured utilisation, enforced return discipline and recovered damage | **BDT 48 lac/year** base case (28 conservative · 72 upside) — Scope Charter BO-13 |
| **Utilisation uplift** | Real availability instead of phone-around; reservations that convert; idle units redeployed between branches | Utilisation from unmeasured to **> 68%**; every point of utilisation on the fleet is margin with no added cost |
| **Damage recovery** | Photographic evidence at both ends turns an unwinnable argument into a priced, defensible charge | **> 85%** of assessed damage recovered, against a baseline of near zero |
| **Loss reduction** | Deposits, exposure limits, custody trail, enrolment and escalation on non-return | Asset loss **< 0.5%/year**; each avoided laptop loss is direct capital preserved |
| **Late-return revenue** | Automatic overdue charging that no longer depends on somebody remembering | Recovers charges that are currently written off by default |
| **Capital efficiency** | Retirement recommendations sell units while they still have resale value, feeding M14 | Higher realised residual value; less capital parked in dead stock |
| **Corporate contract wins** | Framework agreements, consolidated billing and a portal are table stakes for corporate rental; the Company currently has none | Opens tenders that are presently unbiddable |
| **EaaS recurring revenue** | Multi-month bundles of hardware plus support, billed monthly | New recurring line, sized after Wave 6 |
| **Cross-sell into service** | Every rental customer is a qualified prospect for AMC, managed services and refurbished purchase | Feeds M05, M08, M14 pipelines |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Ends the dispute culture** | Condition photographs at both ends remove the single most common cause of customer conflict in rental, and protect honest staff from accusation |
| **Makes the advertised service real** | The Company already advertises laptop rental. M13 is what makes that promise operable at scale rather than branch-by-branch improvisation |
| **Capital discipline** | Asset businesses fail slowly and quietly. A retirement rule with a threshold makes the failure visible while it is still cheap |
| **Auditability of an asset base** | Every unit's location, custody, condition and earnings are reconstructible — which matters for audit, insurance and any future financing of the fleet |
| **Environmental narrative with substance** | Rental is inherently circular: one unit serves many users. With utilisation data, that becomes a measurable ESG claim in M18 rather than a marketing line |
| **A defensible differentiator** | The swap-out SLA is only credible for a company with branches and technicians. It converts an existing structural asset into a contract term competitors cannot match |
| **Training and standardisation** | A category checklist and grading standard turn rental handling from tacit knowledge into a trainable procedure |

---

## 8. Lifecycle & State Models

### 8.1 Rental Asset (fleet unit)

```
        acquisition / transfer from M14 / capitalised in M49
                              │
                       ┌──────▼───────┐
              ┌───────►│  AVAILABLE   │◄──────────────┐
              │        └──────┬───────┘               │
              │               │ reservation confirmed  │ re-graded, passes
              │        ┌──────▼───────┐                │
              │        │   RESERVED   │                │
              │        └──────┬───────┘                │
              │               │ allocated at pick      │
              │        ┌──────▼───────┐         ┌──────┴───────┐
              │        │  ALLOCATED   │         │  TURNAROUND  │
              │        └──────┬───────┘         │ clean · test │
              │               │ dispatched      │ re-grade     │
              │        ┌──────▼───────┐         └──────▲───────┘
              │        │  IN TRANSIT  │                │ returned
              │        └──────┬───────┘                │
              │               │ handover + condition-out
              │        ┌──────▼───────┐                │
              │        │ OUT ON RENT  │────────────────┘
              │        └──────┬───────┘   collection + condition-in
              │               │
              │               │ fault reported        │ not returned
              │        ┌──────▼───────┐        ┌───────▼──────┐
              │        │ UNDER SERVICE│        │     LOST     │──► write-off (M49)
              │        └──────┬───────┘        └──────────────┘     claim (M60)
              │               │ repaired
              │        ┌──────▼───────┐
              └────────┤ QUARANTINED  │  failed re-grade or awaiting M06 certificate
                       └──────┬───────┘
                              │ retirement approved
                       ┌──────▼───────┐
                       │   RETIRED    │──► M14 refurbish & resell ──► SOLD
                       └──────────────┘──► M18 recycle (no resale value)
```

| From | To | Guard | Actor |
|---|---|---|---|
| Available | Reserved | Availability net of padding and maintenance | Coordinator / portal |
| Reserved | Allocated | Specific unit chosen; condition grade meets category minimum | Coordinator |
| Allocated | In Transit | **Outbound condition report complete with photographs** | Dispatch / rider |
| In Transit | Out on Rent | Customer signature captured at handover | Rider / counter |
| Out on Rent | Turnaround | **Inbound condition report complete against the outbound report** | Return inspector |
| Out on Rent | Lost | Non-return escalation exhausted; write-off approved | Corporate Services Head + CFO |
| Turnaround | Available | Clean, functional test and re-grade all passed; **M06 certificate present for data-bearing units** | Turnaround technician |
| Turnaround | Quarantined | Any test failure, or certificate absent | System |
| Quarantined | Under Service | Repair authorised | Service supervisor |
| Any | Retired | Retirement recommendation approved | Corporate Services Head + CFO |
| Retired | Sold | Sale completed through M14 | Retail Operations |

### 8.2 Rental Agreement

```
  DRAFT ──► ELIGIBILITY CHECK ──► QUOTED ──► SIGNED ──► ACTIVE ──► RETURN DUE
              │ fail                                       │            │
              ▼                                     ┌──────┴─────┐      │
          DECLINED                                  │  VARIED    │      │ returned
                                                    │ (extension │      ▼
                                                    │ / swap /   │  INSPECTED
                                                    │ early ret.)│      │
                                                    └──────┬─────┘      │
                                                           └────────────┤
                                                                        ▼
                                                              ┌──────────────────┐
                                                              │ SETTLEMENT       │
                                                              │ damage · late    │
                                                              │ waiver · deposit │
                                                              └────────┬─────────┘
                                                                       │
                                       overdue, unrecovered ◄──────────┼──────────► CLOSED
                                                │                                    (deposit released
                                          IN RECOVERY ──► WRITTEN OFF                  or offset)
```

### 8.3 Damage & Deposit Settlement

```
  CONDITION-IN DIFFERENCE FOUND
            │
            ▼
   ASSESSMENT (priced from parts + labour catalogue)
            │
            ├── waiver elected ──► excess applied ──► balance waived
            │
            └── no waiver ──────► full assessed amount
                                          │
                                          ▼
                            OFFSET AGAINST DEPOSIT (M20 instruction)
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
              deposit covers it                    balance remains
              → refund the remainder               → charge line to M20
                                                   → dispute path available
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-RNT-01 | A unit cannot be dispatched without a complete outbound condition report carrying at least the category-minimum number of photographs | **H** | Corporate Services Head |
| BRU-RNT-02 | A rental cannot be closed without an inbound condition report completed against the outbound report | **H** | Corporate Services Head |
| BRU-RNT-03 | A data-bearing unit cannot re-enter the available pool, be retired or be sold without a valid M06 destruction certificate | **H** | Quality Manager |
| BRU-RNT-04 | The same unit cannot be allocated to two overlapping rental periods | **H** | System |
| BRU-RNT-05 | A rental that would take a party above its computed exposure limit requires documented approval one level above the branch | **A** | Corporate Services Head |
| BRU-RNT-06 | A security deposit is a liability until released; it may never be recognised as revenue | **H** | CFO |
| BRU-RNT-07 | The deposit amount is computed from category, unit value and customer risk tier; manual reduction requires approval and a recorded reason | **C** / **A** | Finance Manager |
| BRU-RNT-08 | Rental pricing must come from an approved M11 rate card; ad-hoc pricing is not permitted | **H** | Chief Commercial Officer |
| BRU-RNT-09 | The applied rate ladder is the cheapest correct combination for the actual duration, and is persisted with the line | **C** | System |
| BRU-RNT-10 | The damage waiver does not cover theft without a police report, gross negligence, deliberate damage, or use outside the agreed purpose | **H** | Corporate Services Head |
| BRU-RNT-11 | A recovered unit remains Company property regardless of any waiver or insurance payment made | **H** | CFO / Legal |
| BRU-RNT-12 | Late charges accrue automatically from the contracted return time; suppression requires approval | **A** | Corporate Services Head |
| BRU-RNT-13 | A returned unit re-enters the pool only after clean, functional test and re-grade all pass | **H** | Turnaround supervisor |
| BRU-RNT-14 | A unit whose condition grade falls below the category minimum cannot be allocated to a rental | **H** | System |
| BRU-RNT-15 | Retirement is recommended by rule and approved by the Corporate Services Head and the CFO jointly | **A** | CFO |
| BRU-RNT-16 | A sub-rented (cross-hired) unit is flagged as non-owned on every document, and is never capitalised | **H** | Finance Manager |
| BRU-RNT-17 | Every rental unit must carry a valid M17 asset identity before it can be made available | **H** | Asset Manager |
| BRU-RNT-18 | An EaaS or long-term agreement with a term of twelve months or more is flagged for M53 lease-classification assessment before activation | **H** | CFO |
| BRU-RNT-19 | Condition photographs cannot be replaced or deleted after the report is signed | **H** | CTO |
| BRU-RNT-20 | Rental to a party without verified identity in M33 is not permitted | **H** | Corporate Services Head |
| BRU-RNT-21 | Preventive maintenance falling due removes the unit from availability for the window; it cannot be rented "just this once" | **S** | Corporate Services Head |
| BRU-RNT-22 | Loss write-off above the category threshold requires CFO approval and an insurance claim record or a documented decision not to claim | **A** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.rental.asset` | `fix_rental_asset` | The rentable unit's rental profile | asset_id (M17), rental_category_id, spec_profile, acquisition_cost, fixed_asset_id (M49), condition_grade, home_branch_id, state, enrolment_ref, retired_at, retirement_route |
| `fix.rental.category` | `fix_rental_category` | Rentable category and its rules | name, attribute_schema, min_condition_grade, turnaround_hours, padding_hours, deposit_basis, overbooking_tolerance, pm_interval, photo_minimum |
| `fix.rental.kit` | `fix_rental_kit` | What ships with a unit | rental_category_id, component_name, quantity, mandatory, replacement_value |
| `fix.rental.reservation` | `fix_rental_reservation` | Held demand | partner_id, rental_category_id, spec_filter, branch_id, date_from, date_to, quantity, hold_expiry, state, allocated_asset_ids |
| `fix.rental.agreement` | `fix_rental_agreement` | The contract | name, partner_id, contract_id (M08), agreement_type (spot / framework call-off / EaaS), period_from, period_to, tariff_id, deposit_amount, waiver_elected, waiver_excess, swap_sla_hours, state, signed_at, signature_ref, version |
| `fix.rental.line` | `fix_rental_line` | A unit on an agreement | agreement_id, rental_asset_id, date_out, date_due, date_in, applied_rate_ladder, gross_rental, state |
| `fix.rental.tariff` | `fix_rental_tariff` | The rate structure in force | rental_category_id, rate_card_id (M11), hourly, daily, weekly, monthly, custom_periods, min_period, discount_rules, valid_from, valid_to |
| `fix.rental.deposit` | `fix_rental_deposit` | Deposit instruction and status | agreement_id, computed_amount, collected_amount, collection_ref, held_state, offset_amount, release_instruction_ref, released_at |
| `fix.condition.report` | `fix_condition_report` | Condition at a point of custody transfer | agreement_id, rental_asset_id, direction (out / in), inspector_id, captured_at, location, meter_readings, accessory_checklist, signature_ref, hash, offline_captured, synced_at |
| `fix.condition.photo` | `fix_condition_photo` | Immutable evidence | condition_report_id, sequence, view_code, document_id (M24), captured_at, device_ref, hash |
| `fix.damage.assessment` | `fix_damage_assessment` | Priced difference between out and in | agreement_id, rental_asset_id, difference_items, parts_cost, labour_cost, total_assessed, waiver_applied, excess_amount, deposit_offset, balance_charged, state, disputed |
| `fix.rental.extension` | `fix_rental_extension` | In-flight variation | agreement_id, requested_at, new_date_to, availability_result, reprice_result, approved_by, state |
| `fix.rental.swap` | `fix_rental_swap` | In-rental replacement | agreement_id, out_asset_id, in_asset_id, fault_ref, sla_target, sla_met, condition_report_out_id, condition_report_in_id |
| `fix.asset.utilisation` | `fix_asset_utilisation` | Daily utilisation series | rental_asset_id, date, status, on_rent, revenue_accrued, days_available_ytd, days_on_rent_ytd |
| `fix.rental.loss` | `fix_rental_loss` | Non-return, loss and theft | agreement_id, rental_asset_id, reported_at, escalation_stage, police_report_ref, valuation, claim_ref, recovered, written_off_at, approved_by |
| `fix.rental.turnaround` | `fix_rental_turnaround` | Between-rental processing | rental_asset_id, received_at, clean_done, test_result, service_order_ref, destruction_cert_ref, new_grade, released_at |
| `fix.subrental` | `fix_subrental` | Cross-hired unit | agreement_id, supplier_id, supplier_asset_ref, cost, period_from, period_to, condition_report_ids |
| `fix.rental.exposure` | `fix_rental_exposure` | Party exposure limit and usage | partner_id, risk_tier, computed_limit, current_exposure, last_reviewed, override_ref |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.asset` | M17 / M49 | Read / update lifecycle state via API |
| `fix.asset` | M17 / M49 | Read written-down value; publish disposal trigger |
| `fix.party` | M33 | Read identity, verification status, segment |
| `fix.contract` | M08 | Read template; instantiate agreement |
| `fix.rate.card` | M11 | Read approved tariffs |
| `fix.consignment` | M03 | Create delivery and collection requests |
| `fix.ar.invoice` / `fix.billable.event` | M20 | Publish chargeable events |
| `fix.destruction.certificate` | M06 | Synchronous gate check |
| `fix.document` | M24 | Store agreements, reports, photographs, signatures |
| `fix.service.order` | M01 | Raise repair on a fleet unit |
| `fix.catalogue.item` | M37 | Rental catalogue item |
| `fix.maintenance.plan` | M17 | Preventive maintenance schedule |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-RNT-01 | Reservation created | Hold availability, set hold expiry, notify the customer with the confirmation and the deposit amount | Reservation held without confirmation; alert coordinator |
| AUT-RNT-02 | Hold expiry reached without confirmation | Release the reservation and return the units to availability | Alert coordinator; do not silently retain |
| AUT-RNT-03 | Agreement signed | Instruct deposit collection; raise the delivery consignment in M03; schedule the pre-dispatch check | Block dispatch; alert coordinator |
| AUT-RNT-04 | Outbound condition report signed | Move the unit to In Transit / Out on Rent; start the rental clock; publish `rental.dispatched` | Block state change; the report is the gate |
| AUT-RNT-05 | Return date approaches (T-48h, T-24h) | Notify the customer with return instructions and the collection option; offer extension | Log and retry; escalate on repeated failure |
| AUT-RNT-06 | Return date passes without return or extension | Start late charges at the configured rate; notify at 1, 3 and 7 days; escalate to the account owner | Escalate immediately — an uncharged overdue is a revenue leak |
| AUT-RNT-07 | Inbound condition report completed with differences | Create a damage assessment, price it from the catalogue, apply waiver excess, propose the deposit offset | Route to manual assessment; never auto-close |
| AUT-RNT-08 | Damage assessment approved | Offset the deposit, raise the balance charge to M20, notify the customer with the evidence pack | Retry; escalate to Finance |
| AUT-RNT-09 | Rental closed with no damage | Instruct deposit release to M20 within the agreed window | Escalate — a withheld deposit is a customer-trust failure |
| AUT-RNT-10 | Unit returned to turnaround | Open the turnaround record; if data-bearing, raise the M06 destruction request automatically | Unit stays quarantined; it cannot be rented |
| AUT-RNT-11 | Turnaround tests pass and certificate present | Re-grade, release to Available, recompute availability | Quarantine and alert |
| AUT-RNT-12 | Preventive maintenance falls due | Remove the unit from availability, raise the maintenance work order, restore on completion | Alert; the unit remains bookable only with an approved override |
| AUT-RNT-13 | Fault reported on a live rental | Open the swap case, start the SLA clock, allocate a replacement from the nearest branch with stock | Escalate to Corporate Services Head at 50% of SLA |
| AUT-RNT-14 | Unit not returned 7 days past due | Move to recovery: formal notice, enrolment last-check-in lookup, remote lock where contracted, valuation prepared | Escalate to Legal at 14 days |
| AUT-RNT-15 | Cumulative repair cost crosses the category threshold, or utilisation stays below the floor for two quarters | Raise a retirement recommendation with the supporting numbers | Log for the monthly fleet review |
| AUT-RNT-16 | Retirement approved | Route to M14 or M18, notify M49 for disposal accounting, remove from availability permanently | Block retirement; assets must have a destination |
| AUT-RNT-17 | Long rental billing cycle due | Publish the recurring billing basis to M39 / M20 | Escalate to Finance |
| AUT-RNT-18 | Utilisation falls below the category target for a branch | Propose inter-branch redeployment with the demand evidence | Log to the fleet dashboard |
| AUT-RNT-19 | Framework agreement call-off raised | Apply the framework rate card and approver routing automatically | Fall back to standard flow with a warning |
| AUT-RNT-20 | Sub-rental required | Raise the partner request, record cost, mark the unit non-owned for the whole life of the agreement | Block sub-rental without a cost record |

---

## 12. Interfaces

### 12.1 Upstream — M13 Consumes

| Source | What | Mechanism |
|---|---|---|
| M17 Asset Registry | Asset identity, serial, model, lifetime history | REST + event |
| M49 Fixed Assets | Written-down value, depreciation schedule | REST |
| M33 Party Master | Verified identity, segment, corporate hierarchy | REST |
| M20 Receivable | Outstanding balance and payment behaviour for eligibility | REST |
| M11 Pricing | Approved rate cards and discount policy | REST |
| M08 Contract Lifecycle | Agreement templates and clause library | REST |
| M37 Catalogue | Rental catalogue items and specification attributes | REST |
| M03 Logistics | Consignment status and custody events | Event |
| M06 Data Services | **Destruction certificate — hard gate** | Synchronous REST, fails closed |
| M31 / M02 Service | Repair outcome and cost against a fleet unit | Event |
| M45 / M17 Maintenance | Preventive maintenance plans and due dates | Event |
| M05 Managed Services | Device enrolment status and last check-in | REST |
| M48 IoT | Telemetry-derived usage where available | Event |
| M29 Identity | Roles, approvals, e-signature identity | Service |

### 12.2 Downstream — M13 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M20 Receivable | Rental charges, waiver, metered usage, late fees, damage charges, deposit instructions | Events |
| M39 Subscription | Recurring billing basis for long rentals and EaaS | Events |
| M53 Revenue Recognition | Agreement term, structure and classification flag | Events |
| M49 Fixed Assets | Utilisation, impairment signals, disposal and write-off triggers | Events |
| M14 Trade-In & Refurbishment | Retired units with full condition and service history | Command |
| M18 E-Waste | Retired units with no resale value | Command |
| M17 Asset Registry | Lifecycle state changes (Rented Out, Under Service, Retired, Lost) | Events |
| M03 Logistics | Delivery and collection consignment requests | Command |
| M06 Data Services | Destruction requests on returned and retired data-bearing units | Command |
| M24 Documents | Agreements, condition reports, photographs, signatures | Command |
| M23 Quality | Turnaround failures, repeat-damage patterns, SLA breaches | Events |
| M60 GRC | Loss, theft and insurance-claim events | Events |
| M25 Business Intelligence | Utilisation, revenue per asset, damage, loss, margin | Warehouse extract |
| P01 Customer Portal | Availability, booking, agreement, extension, fault report, condition reports | REST |
| P04 Corporate Portal | Framework call-offs, fleet-on-hire view, consolidated billing | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `rental.reserved` | reservation, category, period, branch | M25, P01 |
| `rental.agreement_signed` | agreement, party, period, deposit, waiver | M20, M24, M53 |
| `rental.dispatched` | agreement, asset, condition report ref | M17, M03, M25 |
| `rental.returned` | agreement, asset, condition report ref, differences found | M17, M20, M23 |
| `rental.overdue` | agreement, asset, days overdue, charges accrued | M20, M27 |
| `rental.damage_assessed` | agreement, asset, assessed amount, waiver applied, deposit offset | M20, M23 |
| `rental.deposit_release_instructed` | agreement, amount, reason | M20, M50 |
| `rental.asset_lost` | asset, valuation, claim reference | M49, M60, M20 |
| `rental.swap_executed` | agreement, out asset, in asset, SLA met | M23, M25 |
| `rental.retirement_recommended` | asset, cumulative cost, utilisation, WDV | M49, M14 |
| `rental.asset_retired` | asset, route (M14 / M18), disposal reference | M14, M18, M49, M17 |
| `rental.utilisation_daily` | asset, date, status, revenue accrued | M25, M62 |
| `rental.usage_reported` | agreement id, asset, period, hire days, metered usage, utilisation | M39, M53, M20 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-RNT-01 | E-signature provider (via M24) | Outbound | Agreement and condition-report signature |
| INT-RNT-02 | SMS / WhatsApp gateway (via M27) | Outbound | Return reminders, overdue notices, swap updates |
| INT-RNT-03 | Mobile financial services / bank (via M20, M50) | Outbound | Deposit collection and refund instruction |
| INT-RNT-04 | Managed-device tooling (via M05) | Inbound | Enrolment status, last check-in, remote lock |
| INT-RNT-05 | Telematics provider — **ISO 15143-3 (AEMP 2.0)** shape | Inbound | Operating hours, location, idle time for equipped units *(interface defined, not populated at W6)* |
| INT-RNT-06 | Insurer / claims portal | Outbound | Loss and damage claim submission |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/rental/availability` | GET | Availability by category, spec, branch and date range | P01, P04, counter |
| `/api/v1/rental/reservations` | POST / DELETE | Create or release a reservation | P01, P04 |
| `/api/v1/rental/agreements` | POST | Create an agreement from a reservation | P01, P04, counter |
| `/api/v1/rental/agreements/{id}/sign` | POST | Capture e-signature | P01, counter |
| `/api/v1/rental/agreements/{id}/extend` | POST | Request an extension with availability check and reprice | P01, P04 |
| `/api/v1/rental/condition-reports` | POST | Submit an outbound or inbound condition report with photographs | Mobile app |
| `/api/v1/rental/condition-reports/{id}` | GET | Retrieve a report and its evidence | P01, P04, dispute pack |
| `/api/v1/rental/agreements/{id}/fault` | POST | Report a fault and request a swap | P01, P04 |
| `/api/v1/rental/damage-assessments/{id}` | GET | Assessment detail with evidence | P01, P04 |
| `/api/v1/rental/assets/{id}/utilisation` | GET | Utilisation series for a unit | P06, M25 |
| `/api/v1/rental/fleet/analytics` | GET | Utilisation, revenue per asset, damage and loss rollups | P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| Corporate Services Head | C R U D A | All rental — approvals, exposure overrides, retirement recommendation |
| R21 Sales Manager | C R U | Reservations, agreements, quotes within own segment |
| R22 Account Manager (Corporate) | C R U | Framework agreements and call-offs for assigned accounts |
| R08 Service Centre Agent | C R U | Counter reservations, agreements and returns for own branch |
| R15 Logistics Coordinator | R U | Delivery and collection scheduling; consignment status |
| R16 Rider / Delivery Agent | C R | **Condition reports only**, on own manifest — cannot alter agreements or charges |
| R17 Inventory Manager | R U | Fleet composition, inter-branch redeployment |
| R10/R11 Technician | C R U | Turnaround checks and service on fleet units assigned to them |
| R25 Retail / Refurbishment Officer | R | Retired units routed for refurbishment |
| R26 Finance Manager | R U A | Deposits, damage charges, write-off approval, waiver configuration |
| R29 Cashier / Counter Finance | C R | Deposit collection at the counter for own shift |
| R32 Quality Manager / ISO Coordinator | R | Turnaround failures, repeat damage, SLA breaches |
| R36 Customer | C R | Own reservations, agreements, condition reports and charges |
| R37 Corporate Portal User | C R | Own organisation's framework, call-offs and fleet on hire |
| R38 External Party (sub-rental partner) | R | Only the sub-rental records naming them |

**Field-level restrictions.** Acquisition cost, written-down value, cumulative repair cost and
margin per unit are visible to the Corporate Services Head, Finance and management only —
never to counter staff, riders or customers. Customer risk tier and exposure limit are visible
to Finance and the account owner only.

**Segregation of duties.**

| Incompatible combination | Why |
|---|---|
| Inbound condition inspector **and** damage assessment approver | The person who finds the damage cannot alone price and approve the charge |
| Deposit collection **and** deposit release authorisation | Cash control |
| Retirement recommendation **and** retirement approval | An operational recommendation must meet a financial decision |
| Rider capturing the condition report **and** editing the agreement | Evidence capture is separated from commercial terms |

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| Fleet availability board | Rental coordinators, counters | Real time | Available, reserved, on rent, in turnaround, under service, by category and branch |
| Utilisation dashboard | Corporate Services Head, CFO | Daily | Time utilisation and financial utilisation by unit, category, branch; idle high-value units flagged |
| Revenue per asset per month | Corporate Services Head, CFO | Monthly | Revenue against acquisition cost and written-down value, ranked |
| Overdue and recovery report | Corporate Services Head, Finance | Daily | Units past due by age band, charges accrued, escalation stage |
| Damage and recovery report | Finance Manager, Quality Manager | Weekly | Assessed damage, recovered amount, recovery rate, waiver take-up, disputes |
| Deposit position | Finance Manager, CFO | Daily | Deposits held, offset, released, ageing of unreleased deposits |
| Turnaround performance | Corporate Services Head | Weekly | Time from return to available, by category; quarantine reasons |
| Swap SLA performance | Corporate Services Head, Account Managers | Weekly | Swap requests, SLA met rate, breach causes |
| Fleet health & retirement candidates | Corporate Services Head, CFO | Monthly | Cumulative cost, downtime, utilisation and WDV per candidate unit |
| Loss and claims register | CFO, GRC | Monthly | Losses, valuations, claims, recoveries, write-offs |
| Corporate account fleet view | Account Manager, corporate client | On demand | Units on hire, agreements, charges, condition history |
| Rental P&L by category | CFO, Corporate Services Head | Monthly | Revenue, direct cost, depreciation, damage, loss and gross margin per category |
| Condition dispute pack | Legal, Customer Service | On demand | Both condition reports, photographs, signatures, assessment and correspondence for one agreement |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W7+ Target |
|---|---|---|---|---|
| **KPI-075** | Rental fleet time utilisation | unmeasured | 60% | **> 68%** |
| — | Rental fleet financial utilisation | unmeasured | 45% | **> 55%** of acquisition cost per year |
| **KPI-076** | Damage recovery rate (recovered ÷ assessed) | near zero | 70% | **> 85%** |
| — | On-time return rate | unmeasured | 85% | **> 90%** |
| — | Rental asset loss rate | unmeasured | < 1.0%/yr | **< 0.5%/yr** |
| — | Rental gross margin | unmeasured | 48% | **> 55%** |
| — | Revenue per asset per month | unmeasured | Category baselines set at launch | Category targets |
| — | Turnaround time, return to available | unmeasured | < 48 h | **< 24 h** |
| — | Swap SLA met rate | n/a | 85% | **> 95%** |
| — | Dispatches without a complete condition report | n/a | **0** | **0** |
| — | Returns closed without an inbound condition report | n/a | **0** | **0** |
| — | Double-booked units | n/a | **0** | **0** |
| — | Units re-entering the pool without an M06 certificate (data-bearing) | n/a | **0** | **0** |
| — | Deposits released within the agreed window | n/a | 95% | **> 98%** |
| — | Reservation-to-agreement conversion | unmeasured | 65% | **> 75%** |

**Five of these targets are zero.** Condition evidence, double booking and the destruction gate
are controls, not performance measures — a partial score there is a control failure.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `sale_renting` — rental order, pickup, return, deposit field, late-fee basis, padding | 22% |
| L1 | Odoo `stock`, `maintenance`, `sign` — movement, PM scheduling, e-signature | 8% |
| L2 | OCA stock and maintenance extensions | 5% |
| L5 | `cd_rental_asset`, `cd_rental_agreement`, `cd_condition_report`, `cd_rental_billing` | 65% |

Odoo's rental app supplies the transactional spine and nothing else this module depends on.
Availability across branches, condition evidence, damage assessment, exposure limits,
utilisation analytics and the destruction gate are all custom — which is why the module carries
25 person-weeks rather than five.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-059** also claimed by M34; **CD-060** also claimed by M34; **CD-061** also claimed by M34; **CD-062** also claimed by M35. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-059 | `cd_rental_asset` — fleet register, category and spec model, kits, status lifecycle, availability engine, utilisation series, fleet health and retirement rules | Odoo module | 8 PW |
| CD-060 | `cd_rental_agreement` — reservation, allocation, agreement, eligibility and exposure, variation, framework call-off, EaaS, sub-rental | Odoo module | 7 PW |
| CD-061 | `cd_condition_report` — mobile capture with offline queue, forced photography, hashing, side-by-side comparison, damage assessment, dispute pack | Odoo module + mobile | 6 PW |
| CD-062 | `cd_rental_billing` — rate ladder engine, deposit instruction and offset, waiver, metered usage, late charges, recurring basis, charge-event publication | Odoo module | 4 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M17 Device & Asset Registry | Every fleet unit needs one enterprise asset identity before it can be rented |
| M33 Party Master | Eligibility depends on verified party identity |
| M11 Pricing & Rate Cards | Tariffs must come from an approved rate card |
| M08 Contract Lifecycle | Agreement templates and clause library |
| M20 Receivable | Charges, deposits and refunds |
| M49 Fixed Assets | Written-down value for the retirement rule and disposal accounting |
| M03 Service Logistics | Delivery, collection and custody |
| M24 Documents | Agreements, reports, photographs, signatures |
| **M06 Data Services — in or before W6** | The destruction gate on data-bearing returns and retirements cannot be satisfied without it |
| M14 — same wave | Retired units need a destination from day one |

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Rental log books and spreadsheets | All currently-owned rentable units | `fix.rental.asset` (identity created first in M17) | W6 cutover |
| Open rental agreements at cutover | Live agreements only | `fix.rental.agreement` + `fix.rental.line` | W6 cutover |
| Deposits currently held | All open deposits | `fix.rental.deposit`, reconciled to the Finance liability balance | W6 cutover |
| Historical rental history | **Not migrated** — no condition evidence exists, so the records cannot support a dispute or a utilisation baseline | — | — |

**Cutover note.** Every open rental at cutover must have a condition baseline established, even
retrospectively: units on hire without an outbound report are recorded as *baseline unknown*,
and damage cannot be charged against them. This is a one-time, deliberate loss, and it is the
strongest possible argument for going live before the fleet grows further.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A unit cannot be dispatched without a complete outbound condition report meeting the category photograph minimum | Negative test through UI, API and mobile |
| AC-02 | A rental cannot be closed without an inbound condition report completed against the outbound report | Negative test |
| AC-03 | Two overlapping agreements cannot be confirmed for the same unit | Concurrency test under simultaneous confirmation |
| AC-04 | Availability reflects reservations, turnaround padding, maintenance windows and in-transit units within one second of a change | Scripted scenario across three branches |
| AC-05 | The rate ladder charges the cheapest correct combination for a 9-day, a 23-day and a 40-day rental, and the applied ladder is persisted | Pricing test matrix |
| AC-06 | A deposit cannot be posted to a revenue account by any path in the module | Data-model review and negative test |
| AC-07 | Damage assessed against a waived agreement applies the excess correctly and waives the balance | Scenario test with and without waiver |
| AC-08 | **A data-bearing unit cannot re-enter the pool, be retired or be sold without a valid M06 certificate**, and the gate fails closed when M06 is unavailable | Negative test plus fault injection |
| AC-09 | A condition photograph cannot be replaced or deleted after the report is signed | Tamper test |
| AC-10 | A condition report captured offline syncs correctly, is hashed on sync, and is rejected if tampered with in the queue | Offline scenario test |
| AC-11 | A rental breaching the party exposure limit is blocked and can only proceed with a recorded, higher-level approval | Negative test |
| AC-12 | Late charges accrue automatically from the contracted return time without human action | Scripted scenario over a compressed clock |
| AC-13 | Both time utilisation and financial utilisation reconcile to the underlying agreements and charges for a full period | Reconciliation against M20 and M49 |
| AC-14 | A retirement recommendation is raised automatically when the cost-to-value or utilisation threshold is breached, and cannot be actioned without dual approval | Threshold test |
| AC-15 | A retired unit routes to M14 or M18 and cannot be left without a destination | Negative test |
| AC-16 | A complete dispute pack — both reports, all photographs, signatures, assessment, correspondence — can be exported for any agreement | Export test |
| AC-17 | A sub-rented unit is flagged non-owned on every document and never appears in the fixed-asset register | Data test |
| AC-18 | An EaaS agreement of twelve months or more is flagged to M53 before activation | Negative test |
| AC-19 | Corporate Services Head and Finance Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 19 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **In which legal entity will the rental fleet sit?** This determines VAT treatment, depreciation and whether rental revenue consolidates *(decision D-04)* | CFO | **W6 minus 3 months** |
| Q-02 | What is the current fleet — how many units, in which categories, at what acquisition cost and book value? | Corporate Services Head | W6 minus 3 months |
| Q-03 | Is rental VAT treated as a supply of service at the standard rate, and does Mushak 6.3 issuance differ from repair? | CFO / M51 owner | W6 minus 2 months |
| Q-04 | Will the damage waiver be offered at launch, and has it been reviewed against Bangladeshi insurance law to confirm it is not a regulated insurance product? | Legal / CFO | W6 minus 2 months |
| Q-05 | What deposit levels are commercially acceptable by category and customer tier without suppressing demand? | Corporate Services Head / CFO | W6 build |
| Q-06 | Does the Company hold insurance cover on the rental fleet for damage, loss and theft, and what is the excess? | CFO | W6 minus 3 months |
| Q-07 | Will laptop and tablet fleets be enrolled in managed-device tooling, and is remote lock contractually permissible in the rental agreement? | CTO / Legal | W6 minus 2 months |
| Q-08 | What is the retirement threshold per category — cumulative repair cost as a percentage of WDV, and the utilisation floor? | Corporate Services Head / CFO | W6 build |
| Q-09 | Which partners are available for sub-rental, and on what commercial terms? | Corporate Services Head | W6 minus 1 month |
| Q-10 | Are there open rentals today with no condition record, and how will the baseline-unknown position be communicated to those customers? | Corporate Services Head | **Before cutover** |
| Q-11 | Does the Company intend to offer EaaS at launch, or after the rental base is proven? | CEO / Corporate Services Head | W6 build |
| Q-12 | **Reciprocity gap (audit finding).** This module claims a hard destruction gate on data-bearing rental returns and retirements (FR-RNT-039, BRU-RNT-03, AC-08). M06 §12.2 lists only M14 and M18 as gate consumers, and the Category D overview §4 gate table has no M13 row. The claim is substantively correct — a returned rental laptop holds a customer's data — but **M06 and the category overview must be updated to name M13 as a third gate consumer**, or M13's claim must be withdrawn. Both sides of a boundary must agree | Quality Manager / CTO | **W6 minus 3 months** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` (Category D — the circular flow and the non-negotiable gate) ·
`M14_TradeIn_Refurbishment_and_Resale.md` (retirement destination) ·
`M18_EWaste_Recycling_and_Circular_Economy.md` (end-of-life destination) ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md` §8.2 (the gate) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md` ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §Category D ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` (FR-RNT-001…044) ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` (BO-13, KPI-075, KPI-076, benefit line 9)

**Workspace evidence**
`1000fix_business/Business planning for 1000 fix.docx` §Rental Services (eight asset categories) ·
`1000FiX_Services_Company_Profile.md` §Laptop Rental Service ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` (rental as a purchasable service type) ·
`00_Governance_and_Charter/00-02_Executive_Summary_and_Scope_Charter.md` §Benefit Register (BDT 48 lac)

**External benchmark**
Wynne Systems RentalMan, Texada and Point of Rental — rules-based rate tiers, rent-and-service
on one asset record, return-inspection-first design ·
United Rentals and Sunbelt Rental Protection Plan — elective damage waiver with published
excess and exclusions, explicitly not insurance, recovered equipment remaining lessor property ·
Odoo 19 `sale_renting` documentation — pickup/return, per-product security deposit, per-hour
and per-day late-return cost, padding time, serial tracking, multiple pickup and drop-off
locations ·
Equipment rental KPI practice — time utilisation (days on rent ÷ days available) and financial
/ dollar utilisation (annual rental revenue ÷ original equipment cost); 65–75% time utilisation
as the general-fleet operating band ·
ISO 15143-3 / AEMP 2.0 — vendor-neutral telematics interface for asset identity, location,
cumulative operating hours and idle time ·
IFRS 16 lessor accounting — operating versus finance lease classification, operating-lease
income recognised on a straight-line basis with the asset retained on the lessor's balance sheet ·
Device-as-a-Service practice — hardware, deployment, support and end-of-life bundled into a
single per-device monthly fee

**Sources consulted**
- [Texada — equipment rental software](https://texadasoftware.com/equipment-rental-software-rental-management/)
- [Sycor / Microsoft — best equipment rental software for 2026](https://sycor-group.com/us-en/microsoft/blog/microsoft/best-equipment-rental-software-for-2026-7-platforms-to-consider.html)
- [InTempo — time utilisation vs dollar utilisation](https://www.intemposoftware.com/blog/equipment-rental-metrics-time-dollar-utilization)
- [Quipli — equipment rental utilisation guide](https://quipli.com/resources/calculators/general-and-heavy-equipment-rental-utilization/)
- [Odoo 19 — Rental documentation](https://www.odoo.com/documentation/19.0/applications/sales/rental.html)
- [United Rentals — Rental Protection Plan terms](https://www.unitedrentals.com/legal/rpp-us-eng)
- [Sunbelt Rentals — Rental Protection Plan](https://www.sunbeltrentals.com/resources/rental-protection-plan/)
- [AEM — ISO 15143-3 fleet data exchange](https://www.aem.org/standards/iso15143/3)
- [IFRS Foundation — IFRS 16 Leases](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-16-leases/)
- [IFRS Community — lessor accounting under IFRS 16](https://ifrscommunity.com/knowledge-base/ifrs-16-lessor-accounting/)
- [Intel — Device as a Service and the PC lifecycle](https://www.intel.com/content/www/us/en/business/enterprise-computers/resources/daas.html)

---

*Module M13 · Category D · 1000FiX ERP System v2.0 · CONFIDENTIAL*
