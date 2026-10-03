---
id: FIX-ERP2-M46
module_id: M46
module_code: FLT
module_name: Fleet & Vehicle Management
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Logistics Manager
system_owner: Asset & Facilities Squad
priority: P2
wave: W5
---

# M46 — Fleet & Vehicle Management
### Category F · Code `FLT` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M46 |
| **Module code** | `FLT` |
| **Category** | F — Asset, Equipment & Facilities |
| **Status** | ★ New in v2.1 — **reverses exclusion OOS-4 in the v1.0 BRD** ("Fleet management for delivery vehicles — not in current scope") |
| **Priority** | **P2** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Logistics Manager |
| **System owner** | Asset & Facilities Squad |
| **Delivery layers** | L1 Odoo `fleet` · L2 OCA `fleet` family · L4 telematics ingestion via M48 · L5 custom document compliance, cost-per-kilometre and driver-accountability engines |
| **Custom modules** | `cd_vehicle_ext`, `cd_vehicle_compliance`, `cd_fuel_and_running_cost`, `cd_driver_management` |
| **Requirement range** | FR-FLT-001 … FR-FLT-044 |
| **Requirement count** | **44** *(measured — supersedes the 24 estimate in `02-02`)* |
| **Effort estimate** | **20 person-weeks** *(measured — supersedes the 12 PW estimate)* |
| **Depends on** | M21 Core HR · M33 Party Master · M29 Identity · M30 Platform Admin · M28 Integration · M49 Fixed Assets · M16 Procurement · M52 Accounts Payable & Expense · M24 Documents |
| **Depended on by** | M02, M03, M04, M47, M48, M49, M52, M54, M59, M60, M25 |

---

## 2. Purpose

M46 is the register and control system for **everything 1000FiX drives**: the vans that carry
technicians and van stock, the motorcycles that carry riders and customer devices, and the cars
that carry management. It answers four questions: *what do we own, is it legal to be on the
road today, what does it cost to run, and who was driving it?*

The Company runs a field service business across 51+ locations with 200–400 technicians and a
pick-and-drop logistics service. Vehicles are not a support function in that model — they are
the delivery mechanism. A van off the road because its fitness certificate expired is a
technician who cannot work and a day of jobs redistributed. A motorcycle in an accident with an
expired insurance policy is an uninsured liability carrying a customer's laptop.

M46 does not dispatch vehicles and it does not track technicians. **M02 owns dispatch and the
live position stream; M46 owns the vehicle**, its documents, its servicing, its fuel, its
driver and its cost per kilometre.

### Why It Exists

The v1.0 BRD explicitly excluded fleet management (OOS-4). That exclusion made sense when the
ERP scope was service orders and inventory. It does not survive three facts established
elsewhere in the v2.0 design.

**Van stock lives in a vehicle.** M15 models 200–400 vans as real stock locations holding
inventory that must reconcile daily. A stock location that the ERP does not know exists, cannot
locate, and cannot tell you is off the road is an incomplete control.

**Logistics is now a first-class capability.** M03 owns reverse logistics, custody and proof of
delivery, and P09 is a rider application. Customer devices travel in Company vehicles. Custody
of a customer's device in an untracked vehicle is a gap in the chain of custody that M17 and
M06 are otherwise careful to maintain.

**Statutory compliance is not optional in Bangladesh.** A commercial vehicle requires current
registration, a fitness certificate, a tax token, insurance and — for commercial passenger and
goods carriage — a route permit; the driver requires a valid professional licence. These expire
on different cycles, and commercial vehicles are subject to more frequent fitness inspection
than private ones. Managing that across a growing fleet on a wall calendar produces exactly one
outcome, repeatedly.

M46 is P2 and lands in Wave 5 with M45 and M49, because it is a cost and compliance control
rather than a revenue path — but its document-expiry engine is the single highest-value
component and could be delivered earlier if the fleet size justifies it.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.2 OOS-4 | "Fleet management for delivery vehicles — not in current scope" — **the exclusion this module reverses** |
| ERP BRD BR-FSM-003 | "Track real-time GPS location of all active field technicians on a live map" — the telematics hardware that produces this is a vehicle asset |
| ERP BRD BR-FSM-004 | "Optimize daily routes for each technician to minimize travel time" — route cost is vehicle cost |
| ERP BRD BR-FSM-014 | "Provide customers with a real-time technician tracking link with ETA" — depends on a device fitted to a vehicle |
| ERP BRD BR-INV-002 | "Track van/mobile stock per technician" — the van is a stock location and therefore must be a known asset |
| ERP BRD BR-FSM-015 | Pick-and-drop lifecycle — customer devices move in Company vehicles |
| ERP BRD BR-FIN-015 | "Track fixed assets and calculate depreciation" — vehicles are the largest single capitalised class |
| ERP BRD BR-HRM-004 | GPS-based mobile clock-in — driver and vehicle usage attribution overlap |
| Company Profile §Additional Services | On-site/home service and pick-and-drop across a nationwide network — a fleet-dependent service model |
| `_CATEGORY_OVERVIEW.md` §2, §5 | M46 owns vehicle documents, servicing and fuel; M02 consumes GPS position, M46 owns the device; van stock inside a vehicle is M15 |
| `_CATEGORY_OVERVIEW.md` §7 | Vehicle availability > 95%; cost per kilometre baselined W5, −12% by W8; vehicle document compliance 100% current |
| `M02` §3.2, §5, §10.2, §12 | M02 declares vehicle documents, servicing, fuel and telematics hardware out of scope to M46; records vehicle assignment (FR-FSM-058) and reports usage |
| `M03` §3.2, §10.2, §12 | M03 declares the same boundary and reads vehicle availability and identity |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** The critical boundary is with M02: the vehicle's
> position stream is consumed by dispatch but produced by a device M46 owns. Both sides agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The vehicle register: vans, motorcycles, cars, and any other Company-operated vehicle |
| 2 | Vehicle identity: registration number, chassis and engine number, make, model, year, class, ownership or lease basis |
| 3 | **Statutory document register and expiry control**: registration, fitness certificate, tax token, insurance, route permit |
| 4 | Document renewal workflow, escalation and off-road enforcement on expiry |
| 5 | Driver register: assignment, professional licence validity, licence class against vehicle class, endorsement history |
| 6 | Vehicle-to-driver and vehicle-to-branch assignment, temporary reassignment and pool operation |
| 7 | Daily pre-use vehicle check by the driver, with defect reporting |
| 8 | Preventive servicing schedules by time and by odometer, with service history |
| 9 | Corrective repair, breakdown, and the workshop or external garage that performed it |
| 10 | Tyre, battery and consumable lifecycle tracking |
| 11 | Odometer capture and reconciliation across manual, app and telematics sources |
| 12 | Fuel and lubricant transactions: quantity, cost, source, and fuel-efficiency variance detection |
| 13 | Telematics device register: which unit is fitted to which vehicle, its SIM, its health and its data feed |
| 14 | Trip and usage record: purpose, distance, driver, and attribution to a job, a branch or an overhead |
| 15 | **Cost per kilometre**: total cost of ownership assembled from fuel, servicing, repair, tyres, documents, insurance, depreciation and downtime |
| 16 | Accident, incident and traffic-violation register with insurance claim tracking |
| 17 | Driver behaviour scoring from telematics: speeding, harsh braking, harsh acceleration, idling |
| 18 | Vehicle availability state and off-road tracking with cause |
| 19 | Replacement and disposal decision support; disposal routing and notification to Finance |
| 20 | Fleet analytics: utilisation, availability, cost per kilometre, cost per job, compliance |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Technician dispatch, scheduling, routing and the live map** | **M02** Field Service & Dispatch | Dispatch is a service-operations decision. M46 supplies vehicle availability as a constraint; it never assigns work |
| **The live technician position stream and geofencing** | **M02** | M02 owns the stream and its consumers; M46 owns the physical device producing it and its health |
| **Customer-facing ETA and tracking links** | **M02** | A customer tracks a technician, not a vehicle |
| **Consignment movement, custody and proof of delivery** | **M03** Service Logistics | M03 owns what is in the vehicle and who signed for it; M46 owns the vehicle |
| **Van stock held inside a vehicle** | **M15** Inventory | The van is a stock location in M15 and a vehicle in M46; the same physical object, two registers, one link |
| **Rider manifests and the rider application** | **M03** / P09 | M46 supplies the vehicle and driver identity to the manifest |
| **Capitalisation, depreciation, revaluation and disposal accounting** | **M49** Fixed Assets | M46 supplies acquisition, usage, impairment and disposal triggers; Finance posts them |
| **Vehicle purchase, lease negotiation, RFQ and PO** | **M16** Procurement | M46 raises the replacement justification; M16 buys or leases |
| **Fuel-card supplier contract and garage contracts** | **M42** Supplier Relationship | M46 records transactions and performance; M42 owns the relationship |
| **Payment of fuel and service invoices; driver expense reimbursement** | **M52** Accounts Payable & Employee Expense | M46 validates the transaction against the vehicle; M52 pays |
| **Motor insurance policy administration and broker relationship** | **M60** GRC (with **M49**) | M46 records the policy on the vehicle, tracks expiry and raises claims; policy administration is a Finance and GRC function |
| **Driver employment, payroll, attendance and discipline** | **M21 / M55 / M56 / M57** | M46 records driving accountability; HR owns the employment relationship and any consequence |
| **Driver competency, licence training and defensive-driving certification** | **M22** Learning & Competency | M46 records that a licence is valid; M22 develops and certifies the competence |
| **Road-traffic accident injury management and HSE investigation** | **M59** Health, Safety & Wellbeing | M46 records the vehicle incident; M59 owns the safety investigation and the person |
| **Telemetry ingestion, storage and retention** | **M48** IoT & Predictive Maintenance | M46 registers the device and consumes derived signals; M48 owns the pipe |
| **Predictive failure models for vehicles** | **M26** builds, **M48** applies | M46 consumes the prediction and acts on it |
| **Third-party courier vehicles** | **M03** | 1000FiX does not own them; M03 manages the courier relationship |
| **Premises parking, garage buildings and fuel storage on site** | **M47** Facility & Workplace | The building is a facility; the vehicle in it is a fleet asset |

### 3.3 Shared Concepts

| Concept | M46's Role | Owning Module |
|---|---|---|
| Vehicle | **Owns** — the defining concept of this module | M46 |
| Telematics device | **Owns** the device, SIM, fitment and health | M46 |
| Position ping | Produces; M02 owns the stream and its use | M46 / M02 |
| Van as a stock location | References the M15 location; owns the vehicle it corresponds to | M46 / M15 |
| Driver | Owns the driving assignment and accountability; M21 owns the employee | M46 / M21 |
| Fixed-asset record and depreciation | References; supplies usage, impairment and disposal triggers | M49 |
| Fuel transaction | Owns validation against the vehicle; M52 owns payment | M46 / M52 |
| Insurance policy | Owns the vehicle linkage and expiry; M60 and M49 own administration | M46 / M60 |
| Vehicle incident | Owns the vehicle and claim view; M59 owns the safety investigation | M46 / M59 |
| Vehicle availability | **Owns**; M02 and M03 consume it as a constraint | M46 |
| Vehicle condition signal | Consumes | M48 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Fleetio / Geotab / commercial fleet platforms** | Telematics combined with fuel-card integration and analytics to give one view of consumption and spend; fuel cost per mile, MPG tracking, idle-time reporting, fuel-card exception reports, driver fuel-efficiency reporting; open APIs into ERP, HR and dispatch | **Fuel-card-plus-telematics reconciliation is the single most influential external reference for M46.** Fuel is typically 30%+ of fleet operating cost, and the fuel exception — litres dispensed exceeding tank capacity, refuelling far from any known route, consumption diverging from the vehicle's own history — is the highest-yield control in fleet management. Also adopted: cost per distance as the primary operating metric, not total spend | Buying a commercial fleet platform. At the current fleet size the subscription and the integration cost exceed the value; the pattern is adopted, the product is not |
| **Driver-behaviour scoring practice (Geotab, Samsara and equivalents)** | Speeding, harsh braking, rapid acceleration, idling and seatbelt monitoring, with driver scorecards, coaching workflows and links to safety training; mature deployments report accident reduction of 20–30% and fuel reduction of 10–15% through eco-driving | **Driver scorecards with a coaching route, not a punitive one.** The scorecard feeds M22 competency development and M57 incentives; it does not feed discipline directly. This distinction determines whether drivers accept the system or defeat it | Camera-based driver monitoring. Disproportionate, expensive, and a workforce-relations risk that would jeopardise adoption of the whole module |
| **SAP S/4HANA Fleet Management (LO-FM / EAM)** | Vehicles as equipment master with counters, consumption records, measuring points, fuel and service documents, and a link to plant maintenance | The **counter/measuring-point model** for odometer, engine hours and fuel, with maintenance plans triggered from counters rather than from dates alone. This is the correct model for vans whose annual distance varies by a factor of three between city and regional branches | SAP's full fleet object and settlement structure |
| **Microsoft Dynamics 365 / Odoo `fleet`** | Vehicle records, contracts, services, odometer logs, fuel logs, cost reporting, document repository, service scheduling by time or mileage with reminders | Odoo `fleet` is the L1 substrate and is used as intended: vehicle master, odometer, services, costs and document repository. Service scheduling by time **or** mileage with reminders is adopted directly | Odoo `fleet` has no statutory-document compliance model, no driver-licence validity check, no fuel-exception detection and no cost-per-kilometre engine. All four are built |
| **OCA `fleet` modules** | `fleet_vehicle_inspection` (entry and exit inspections with cost), `fleet_vehicle_category`, `fleet_vehicle_usage` (usage records by employee with dates and states), `fleet_vehicle_configuration` | **`fleet_vehicle_inspection` adopted as-is** for the daily pre-use check — it is exactly the right shape and already migrated to v19. `fleet_vehicle_usage` adopted for driver-usage records | — |
| **ISO 15143-3 (AEMP 2.0) equipment telematics standard** | A vendor-neutral interface exposing asset identity, location, cumulative operating hours, idle time and utilisation across mixed-brand telematics | **The interface shape** for telematics ingestion, so that changing telematics supplier is a configuration change rather than a rebuild. This is the same position M13 took for rental assets, and the two must not diverge | Adopting a construction-plant telematics stack |
| **Bangladesh regulatory practice (BRTA)** | Vehicle registration; **fitness certificate — required more frequently for commercial vehicles than for private**; annual road tax token; motor insurance; route permit for commercial carriage; professional driving licence with a minimum age of 21 | **The full Bangladesh document set modelled as first-class, individually-expiring compliance objects**, each with its own renewal cycle, cost, evidence document and escalation ladder. No international product models this correctly, and getting it wrong means vehicles are seized or uninsured | Attempting an automated BRTA integration in Wave 5. The BRTA Service Portal is a manual portal; renewal is a physical and clerical process. M46 manages the calendar, the evidence and the accountability, and treats the renewal itself as an external task |

**Design position.** Four deliberate differences from the benchmark.

First, **document expiry is an operational block, not a reminder.** Every fleet product sends a
reminder. In M46 a vehicle whose fitness certificate, tax token or insurance has expired is
marked **off-road automatically**, and an off-road vehicle cannot be assigned by M02 or M03.
The commercial argument against this is that it stops work. That is precisely the point: a
vehicle on the road without valid insurance carrying a customer's device is a larger loss than
a day of redistributed jobs, and the only reliable way to make renewals happen on time is to
make the alternative visible in advance and expensive on the day.

Second, **cost per kilometre is the module's primary output, and it is assembled, not
estimated.** Fuel, servicing, repairs, tyres, document fees, insurance, depreciation from M49
and downtime cost are all attributed to the vehicle, so the number is defensible. The Category
F target — baseline in Wave 5, −12% by Wave 8 — is only meaningful if the baseline is real.

Third, **the driver, not the branch, is accountable.** Fuel exceptions, behaviour scores and
incidents attach to a named driver on a named date. But the consequence route runs through
coaching and competency (M22) and incentives (M57), never automatically through discipline.
A fleet system that becomes a disciplinary instrument is defeated within a month.

Fourth, **the telematics device is an asset with a health record.** Fleet systems typically
treat the tracker as infrastructure. Here it is registered, its SIM and data plan are tracked,
and a device that stops reporting raises a fault — because M02's dispatch board and BR-FSM-003
depend on it, and a silent tracker looks identical to a stationary vehicle.

---

## 5. Functional Areas & Features

### 5.1 Vehicle Register & Identity

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-001 | Vehicle record | Maintain one record per Company-operated vehicle with registration number, chassis number, engine number, make, model, variant, year, colour, class, seating or load capacity, fuel type and home branch | **P0** | L1 |
| FR-FLT-002 | Vehicle class and profile | Classify vehicles as service van · rider motorcycle · management car · goods vehicle · other, with class-specific document requirements, service intervals, licence-class requirements and cost profiles | **P0** | L5 |
| FR-FLT-003 | Ownership basis | Record whether a vehicle is owned, leased, hired or employee-owned-and-reimbursed, with the contract reference, term and end-of-term obligation | **P0** | L5 |
| FR-FLT-004 | Fixed-asset linkage | Link every owned vehicle to its M49 fixed-asset record and expose acquisition, usage, impairment and disposal triggers without duplicating the depreciation schedule | P1 | L5 |
| FR-FLT-005 | Vehicle-to-branch assignment | Assign each vehicle to a home branch and cost centre, supporting permanent assignment, pool operation and temporary reassignment with dates | **P0** | L5 |
| FR-FLT-006 | Van stock linkage | Link a service van to its M15 stock location, so that a vehicle taken off the road exposes the stock it holds and the technician it serves | **P0** | L5 |
| FR-FLT-007 | Vehicle documents | Store registration papers, purchase or lease documents, insurance policy, permits and photographs through M24 with retention policy applied | P1 | L2/L5 |
| FR-FLT-008 | Availability state | Maintain a single authoritative availability state — available · in use · under service · off-road (document) · off-road (defect) · off-road (accident) · disposed — read by M02 and M03 | **P0** | L5 |

### 5.2 Statutory Document Compliance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-009 | Document register | Hold each statutory document as a separate record with its own issue date, expiry date, issuing authority, reference number, cost and scanned evidence: **registration, fitness certificate, tax token, motor insurance, route permit** and any class-specific permit | **P0** | L5 |
| FR-FLT-010 | Class-driven requirements | Derive the required document set from vehicle class and usage, so that a commercial goods vehicle requires the documents a private car does not | **P0** | L5 |
| FR-FLT-011 | Expiry alerting | Alert the vehicle custodian, the branch manager and the Logistics Manager at 60, 30, 15, 7 and 1 days before each document expires, escalating at each step | **P0** | L5 |
| FR-FLT-012 | Automatic off-road on expiry | Mark a vehicle off-road automatically at midnight on the expiry of registration, fitness, tax token or insurance, and prevent its assignment by M02 and M03 | **P0** | L5 |
| FR-FLT-013 | Renewal workflow | Track a renewal from initiation through submission, payment, collection and evidence upload, with the responsible person and the cost recorded | **P0** | L5 |
| FR-FLT-014 | Renewal cost capture | Capture government fee, agent fee and any penalty for each renewal, attributed to the vehicle's running cost | P1 | L5 |
| FR-FLT-015 | Compliance dashboard | Present fleet-wide document status by vehicle, branch and document type, with a forward view of the next 90 days | **P0** | L5 |
| FR-FLT-016 | Compliance evidence | Produce, for any vehicle on any past date, the set of documents that were valid on that date — the evidence required after an accident or an enforcement action | P1 | L5 |

### 5.3 Drivers & Assignment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-017 | Driver register | Maintain a driver record linked to the M21 employee, holding licence number, licence class, professional status, issue and expiry dates, and endorsement history | **P0** | L5 |
| FR-FLT-018 | Licence validity gate | Prevent assignment of a vehicle to a driver whose licence is expired, or whose licence class does not cover the vehicle class | **P0** | L5 |
| FR-FLT-019 | Licence expiry alerting | Alert the driver, the branch manager and HR at 60, 30 and 15 days before licence expiry, mirroring the certification-expiry pattern in BR-HRM-003 | **P0** | L5 |
| FR-FLT-020 | Vehicle assignment | Assign a vehicle to a driver permanently, for a shift, or per trip, retaining the full assignment history for accountability | **P0** | L5 |
| FR-FLT-021 | Pool operation | Support pool vehicles booked for a period by a named driver, with handover condition capture at issue and return | P2 | L5 |
| FR-FLT-022 | Handover accountability | Require a condition check at every driver handover, so that damage is attributable to a period of custody | P1 | L2/L5 |
| FR-FLT-023 | Driver exit | Block employee exit clearance in M21 while a vehicle, its keys or its documents remain assigned to that employee | P1 | L5 |

### 5.4 Inspection, Servicing & Repair

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-024 | Daily pre-use check | Present a class-specific pre-use checklist on the driver's phone — tyres, lights, brakes, fluids, documents present, damage — recording completion, defects and photographs before the first job of the day | **P0** | L2/L5 |
| FR-FLT-025 | Defect reporting | Raise a defect from the pre-use check or during the day, classify it as safety-critical or deferrable, and take a safety-critical vehicle off-road immediately | **P0** | L5 |
| FR-FLT-026 | Preventive service schedule | Define service intervals by elapsed time **and** by odometer per vehicle class, generate service due alerts, and mark a service overdue beyond a configurable tolerance | **P0** | L1/L5 |
| FR-FLT-027 | Service execution | Record a service with the garage or workshop, date, odometer, work performed, parts, cost, invoice reference and the next service due | **P0** | L1 |
| FR-FLT-028 | Corrective repair and breakdown | Record breakdowns and corrective repairs with cause, downtime, recovery cost and the jobs affected | P1 | L5 |
| FR-FLT-029 | Tyre and battery lifecycle | Track tyres and batteries individually with fitment date, position, odometer at fitment, and expected and actual life | P2 | L5 |
| FR-FLT-030 | Odometer capture | Capture odometer readings from the driver app, from service records and from telematics, reconcile the three, and flag implausible readings | **P0** | L5 |
| FR-FLT-031 | Service provider performance | Report garage turnaround, repeat-repair rate and cost against estimate, feeding the M42 supplier scorecard | P2 | L5 |

### 5.5 Fuel, Telematics & Running Cost

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-032 | Fuel transaction capture | Record every fuel and lubricant transaction with date, station, quantity, unit price, total, odometer, payment method and receipt evidence, whether paid by card, by cash advance or by employee expense | **P0** | L1/L5 |
| FR-FLT-033 | Fuel efficiency | Compute consumption per vehicle per period, compare it to the vehicle's own history and to its class baseline, and flag deterioration | **P0** | L5 |
| FR-FLT-034 | Fuel exception detection | Detect and flag: quantity exceeding tank capacity, refuelling intervals inconsistent with distance travelled, transactions at locations far from any recorded trip, duplicate receipts, and consumption diverging materially from history | **P0** | L5 |
| FR-FLT-035 | Telematics device register | Register each telematics unit with its identifier, SIM, data plan, fitment date, fitted vehicle and firmware, and track device health and last-report time | **P0** | L5 |
| FR-FLT-036 | Telematics silence detection | Raise a fault when a fitted device stops reporting for longer than a configurable interval, because a silent tracker is indistinguishable from a stationary vehicle on M02's dispatch board | **P0** | L5 |
| FR-FLT-037 | Trip and usage record | Record trips with start, end, distance, duration, driver and purpose, attributed to a job, a branch or an overhead category | P1 | L5 |
| FR-FLT-038 | Driver behaviour score | Derive a per-driver score from telematics events — speeding, harsh braking, harsh acceleration, excessive idling — normalised for distance, and publish it as a coaching input to M22 and M57 | P2 | L4/L5 |
| FR-FLT-039 | **Cost per kilometre** | Assemble total running cost per vehicle per period from fuel, servicing, repairs, tyres, document and permit fees, insurance premium, depreciation from M49 and downtime cost, and express it per kilometre, per day and per job served | **P0** | L5 |
| FR-FLT-040 | Cost attribution | Attribute vehicle cost to branch, cost centre and, where trips are job-attributed, to the service line — supplying M54 with the true cost of field delivery | P1 | L5 |

### 5.6 Incidents, Insurance & Disposal

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FLT-041 | Incident register | Record accidents, damage, theft and traffic violations with date, driver, location, third parties, photographs, police reference and any cargo or customer device involved | **P0** | L5 |
| FR-FLT-042 | Insurance claim tracking | Track a motor insurance claim from notification through assessment, repair authorisation, settlement and excess recovery, with the vehicle off-road for the duration | P1 | L5 |
| FR-FLT-043 | Violation and penalty handling | Record traffic fines and penalties against the vehicle and the driver on duty at the time, with a recovery or absorption decision recorded | P2 | L5 |
| FR-FLT-044 | Replacement and disposal | Recommend replacement from age, distance, repair-cost history and availability; on approval, route disposal to sale or scrap and notify M49 for disposal accounting | P2 | L5 |

> **Cross-cutting.** Fleet utilisation, availability, cost-per-kilometre trend and compliance
> reporting are delivered as analytics over the register and are specified in §14. Telematics
> ingestion itself is performed by **M48**; M46 registers the device, consumes derived signals
> and owns the vehicle context. Before M48 goes live in Wave 8, M46 accepts a direct provider
> feed through M28 with a reduced signal set.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Off-road is a stored state, not a computed filter** | The nightly compliance job writes the availability state. M02 and M03 read a state; they never re-implement expiry arithmetic. A single implementation is the only way the block is uniform |
| T-02 | **Availability read latency** | Vehicle availability for a branch's fleet returns in ≤ 150 ms at p95, because M02's dispatch board calls it on every assignment decision |
| T-03 | **Telematics interface shape** | The telematics ingress conforms to the ISO 15143-3 (AEMP 2.0) field set — asset identity, location, cumulative distance, engine hours, idle time — so a change of provider is configuration, not redesign. This matches the position taken by M13 §6 T-11 |
| T-04 | **No duplicate position stream** | M46 stores device identity and health, and the derived aggregates it needs (distance, idle, harsh events per period). The position stream itself is stored once, by M48, and consumed by M02. M46 never holds a second copy |
| T-05 | **Odometer reconciliation** | Readings from app, service record and telematics are reconciled with a monotonic constraint; a reading lower than the previous accepted value, or implying an implausible daily distance, is rejected for confirmation rather than stored |
| T-06 | **Fuel exception evaluation** | Exception rules are evaluated server-side on transaction commit, with each rule's inputs and outcome stored, so a flagged transaction can be explained to the driver it was raised against |
| T-07 | **Cost assembly determinism** | Cost per kilometre stores its inputs — component costs, distance basis, period, depreciation source — so any published figure is reproducible and explainable without re-derivation |
| T-08 | **Append-only registers** | Document, assignment, incident, odometer and fuel records are insert-only; corrections are compensating entries with a reason and a reference |
| T-09 | **Offline pre-use check** | The daily check operates offline on the driver's phone and synchronises through an append-only journal with server-side conflict resolution (AS-13) |
| T-10 | **Idempotent capture** | Fuel, odometer and check submissions carry a client idempotency key; a replayed submission after network failure must not double-post |
| T-11 | **Document evidence integrity** | Scanned statutory documents are stored as PDF/A with a content hash on the document record, so a substituted scan is detectable |
| T-12 | **Event emission via outbox** | Every vehicle state change — off-road, returned to service, document expiring, incident, assignment — emits a domain event through the transactional outbox (AS-08) |
| T-13 | **Multi-entity and operating-unit isolation** | Every vehicle carries `company_id` and `operating_unit_id`; a branch sees its own and pool vehicles assigned to it (AS-03) |
| T-14 | **Scale envelope** | 150–400 vehicles; 120,000 fuel and odometer records, 2,000 document renewals and 150,000 trip records per year — small by transaction volume, high by compliance consequence |
| T-15 | **Bengali support** | Driver-facing screens — pre-use check, defect reporting, fuel capture, trip logging — are complete in Bengali, and Bengali is the default for these roles (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M46 |
|---|---|---|
| **Technician / driver** | Discovers a document has expired when stopped by traffic police | Completes a two-minute check on the phone; knows the vehicle is legal and roadworthy before starting |
| **Rider** | Carries customer devices on a motorcycle with no recorded condition or check | Pre-use check recorded; incident capture with photographs if anything happens to the cargo |
| **Branch manager** | Keeps vehicle documents in a drawer and a renewal date in memory | Sees the branch fleet's compliance status and the next 90 days of renewals on one screen |
| **Logistics Manager** | Cannot say what the fleet costs to run, or which vehicles cost most | Cost per kilometre by vehicle, branch and class, with the components behind every number |
| **Dispatch Manager** | Assigns work assuming a vehicle is available | Sees off-road vehicles and their cause as a dispatch constraint before assigning |
| **Inventory Manager** | Van stock invisible when the van is off the road | A vehicle taken off-road exposes its M15 stock location and the recovery required |
| **HR** | No view of licence validity across the workforce | Licence expiry alerts alongside certification expiry, and exit clearance blocked while a vehicle is held |
| **Finance** | Fuel and service invoices approved without vehicle-level validation | Every transaction validated against a vehicle, an odometer and a consumption history before payment |
| **CFO** | Vehicles are a cost line with no unit economics | Cost per kilometre and cost per job, with a −12% target that can actually be measured |

### 7.2 Quantified Business Benefit

M46 is a **cost-control and compliance module**. It carries no revenue line in the Scope
Charter §6.2 benefit register, and none is claimed. Its value is stated as cost reduced, loss
avoided and risk removed.

| Benefit | Mechanism | Value |
|---|---|---|
| **Running-cost reduction** | Fuel exception detection, consumption monitoring, preventive servicing replacing breakdown repair, and eco-driving coaching from behaviour scores | **Cost per kilometre −12% by Wave 8** against a Wave 5 baseline (`_CATEGORY_OVERVIEW.md` §7). Industry practice reports 10–15% fuel reduction from eco-driving programmes alone; the target is deliberately set below that |
| **Fuel leakage elimination** | Every litre attributed to a vehicle, an odometer and a driver; exceptions flagged automatically | Fuel is the largest single running cost. This is the fleet equivalent of the van-stock control in M15, and it addresses the same leakage pattern |
| **Vehicle availability** | Preventive servicing, defect capture before failure, and document renewal before expiry | **Availability > 95%** (`_CATEGORY_OVERVIEW.md` §7). Each percentage point of availability is technician capacity protected |
| **Technician productivity protection** | A van off the road is 8–9 jobs redistributed or lost | Directly protects KPI-011 (8–9 jobs/day) and supports the **BDT 130 lac/year** productivity benefit attributed to M02 in §6.2 |
| **Regulatory penalty avoidance** | 100% document compliance with automatic off-road enforcement | Avoids fines, vehicle seizure and the operational disruption of an impounded van; **document compliance 100% current** (`_CATEGORY_OVERVIEW.md` §7) |
| **Uninsured-liability elimination** | A vehicle with expired insurance cannot be assigned | Removes an unbounded liability, particularly where the vehicle carries customer devices under M03 custody |
| **Accident reduction** | Driver behaviour scoring with a coaching route | Industry practice reports 20–30% accident reduction in mature deployments; benefit is claimed conservatively as insurance premium stability and downtime avoided |
| **Replacement decisions with evidence** | Age, distance, repair-cost history and availability assembled per vehicle | Converts capital replacement from an assertion into a business case; feeds M54 budgeting |
| **Custody-chain completeness** | The vehicle carrying a customer device is known, checked and attributed to a driver | Closes the last gap in the M17/M03/M06 chain of custody |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Legal and regulatory standing** | A fleet that is provably compliant on any past date protects the Company in enforcement action, in an insurance dispute and in a liability claim |
| **Driver safety** | The pre-use check and the safety-critical defect block are the practical mechanism by which the Company discharges its duty of care to 200–400 people who drive for it daily |
| **Workforce relations** | A behaviour score routed to coaching rather than discipline is the difference between a safety programme and a surveillance programme. This choice is recorded deliberately |
| **Environmental reporting** | Fuel consumption per vehicle is the Company's largest measurable direct emissions source, and the only credible input to a Scope 1 figure should ESG reporting be required (with M18) |
| **Insurance negotiating position** | A fleet with documented checks, maintenance records and behaviour scoring negotiates premiums from evidence |
| **Expansion readiness** | A new branch's vehicle complement, cost and compliance calendar become a defined, costed template rather than an improvisation (with M47) |

---

## 8. Lifecycle & State Models

### 8.1 Vehicle Availability

```
                       ┌───────────────┐
      acquired / leased│  REGISTERED   │ documents loaded, telematics fitted,
                       └───────┬───────┘ M49 asset created
                               │ all mandatory documents valid
                       ┌───────▼───────┐
          ┌───────────►│   AVAILABLE   │◄───────────┐
          │            └──┬──┬──┬───┬──┘            │
          │  released     │  │  │   │               │ renewed / repaired /
          │               │  │  │   │               │ cleared
          │        ┌──────▼┐ │  │   │        ┌──────┴─────────────┐
          └────────┤IN USE │ │  │   │        │  OFF-ROAD          │
                   │(driver│ │  │   │        │  ├ document expired│◄── automatic,
                   │assigned)│ │  │  │        │  ├ safety defect  │    midnight
                   └───┬───┘ │  │   │        │  ├ under service  │
                       │     │  │   │        │  ├ accident       │
                       │     │  │   └───────►│  └ awaiting parts │
                       │     │  │            └──────┬─────────────┘
                       │     │  │ service due       │
                       │     │  └───────────────────┘
                       │     │
                       │  ┌──▼──────────┐
                       └─►│  INCIDENT   │──► insurance claim ──┐
                          └─────────────┘                      │
                                                        ┌──────▼──────┐
                                                        │  DISPOSED   │
                                                        │  sold/scrap │
                                                        └─────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Registered | Vehicle acquired or leased; documents loaded; M49 asset created | Logistics Manager |
| Registered | Available | All mandatory documents for the class valid; telematics fitted and reporting; first pre-use check passed | Logistics Manager |
| Available | In use | Assigned to a driver whose licence is valid for the class; pre-use check completed | Branch manager / driver |
| In use | Available | Returned; end-of-day condition recorded | Driver |
| Any | Off-road (document) | Registration, fitness, tax token or insurance expired | **System, automatic, midnight** |
| Any | Off-road (defect) | Safety-critical defect raised on a pre-use check or during the day | Driver / branch manager |
| Available / In use | Off-road (service) | Preventive service due beyond tolerance, or service booked | Branch manager |
| In use | Incident | Accident, theft or damage reported | Driver |
| Incident | Off-road (accident) | Vehicle not roadworthy pending assessment and repair | Logistics Manager |
| Off-road (document) | Available | Renewal completed and evidence uploaded | Branch admin / Logistics Manager |
| Off-road (defect/service/accident) | Available | Repair complete; re-check passed | Branch manager |
| Any | Disposed | Replacement approved; sale or scrap completed; M49 notified | Logistics Manager + CFO |

### 8.2 Statutory Document Cycle

```
   ┌──────────┐  60/30/15/7/1 day   ┌──────────┐  submitted   ┌───────────┐
   │  VALID   │────alerts──────────►│ DUE      │─────────────►│ RENEWAL   │
   └──────────┘                     │ SOON     │              │ IN        │
        ▲                           └────┬─────┘              │ PROGRESS  │
        │                                │ expiry date passes └─────┬─────┘
        │                                ▼                          │
        │                      ┌──────────────────┐                 │
        │                      │ EXPIRED          │                 │
        │                      │ → VEHICLE        │                 │
        │                      │   OFF-ROAD       │                 │
        │                      │   (automatic)    │                 │
        │                      └──────────────────┘                 │
        │                                                           │
        └──────── new document issued, evidence uploaded, hashed ────┘
```

| Document | Typical cycle | Consequence of expiry |
|---|---|---|
| Vehicle registration | One-time, with periodic renewal by class | Vehicle off-road; unregistered operation is an offence |
| **Fitness certificate** | Annual for private; **more frequent for commercial vehicles** | Vehicle off-road; a primary enforcement target |
| **Tax token (road tax)** | Annual | Vehicle off-road; penalties accrue |
| **Motor insurance** | Annual | Vehicle off-road — **the single non-negotiable block**, because an uninsured vehicle carrying customer property is an unbounded liability |
| **Route permit** | Per class and route, where commercial carriage applies | Vehicle off-road for the affected operation |
| Driver professional licence | Per licence class and term | Driver blocked from assignment to that vehicle class |

> The precise renewal cycles, fees and documentary requirements for each class are confirmed
> against BRTA current practice at build time (Open Question Q-02); the model is deliberately
> configuration-driven so that a change in cycle is a parameter change, not a code change.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FLT-01 | A vehicle whose registration, fitness certificate, tax token or motor insurance has expired is off-road automatically and cannot be assigned by any module | **H** | Logistics Manager |
| BRU-FLT-02 | An off-road vehicle cannot be assigned to a technician, a rider or a job through any path — UI, API or dispatch engine | **H** | Operations Director |
| BRU-FLT-03 | **Motor insurance expiry admits no override at any authority level**, including CEO | **H** | CFO |
| BRU-FLT-04 | A vehicle with a safety-critical defect is off-road until the defect is cleared and re-checked | **H** | Logistics Manager |
| BRU-FLT-05 | A vehicle may not be assigned to a driver whose licence is expired or whose licence class does not cover the vehicle class | **H** | HR Director |
| BRU-FLT-06 | Every vehicle in use has exactly one accountable driver assigned for the period of use | **H** | Logistics Manager |
| BRU-FLT-07 | The daily pre-use check must be completed before the vehicle's first job of the day is started | **H** | Branch Manager |
| BRU-FLT-08 | Every fuel transaction records the vehicle, the odometer, the driver and evidence; a transaction without an odometer reading is held for completion | **H** | Logistics Manager |
| BRU-FLT-09 | A fuel transaction breaching an exception rule is flagged, held from payment approval, and reviewed by the Logistics Manager before it reaches M52 | **H** | Logistics Manager |
| BRU-FLT-10 | An odometer reading lower than the previous accepted reading, or implying an implausible daily distance, is rejected for confirmation | **H** | Logistics Manager |
| BRU-FLT-11 | Preventive service is due on elapsed time or odometer, whichever occurs first; a vehicle beyond the overdue tolerance is off-road | **C** | Logistics Manager |
| BRU-FLT-12 | An accident, theft or damage incident is recorded the same day, with photographs and any police reference | **H** | Branch Manager |
| BRU-FLT-13 | A vehicle involved in an incident is off-road until roadworthiness is assessed | **H** | Logistics Manager |
| BRU-FLT-14 | Where a vehicle carrying customer devices is involved in an incident, M03 and M17 are notified so that custody and condition are recorded against the affected assets | **H** | Logistics Manager |
| BRU-FLT-15 | Employee exit clearance is blocked while a vehicle, its keys or its documents remain assigned to that employee | **H** | HR Director |
| BRU-FLT-16 | Traffic fines are recorded against the vehicle and the driver on duty; a recovery-or-absorb decision is required within the authority matrix | **A** | Logistics Manager |
| BRU-FLT-17 | Driver behaviour scores route to coaching (M22) and incentives (M57); they are **never** an automatic disciplinary input | **H** | HR Director |
| BRU-FLT-18 | Cost per kilometre is published only where the underlying distance basis is reconciled; an unreconciled period is reported as provisional | **C** | CFO |
| BRU-FLT-19 | A telematics device that has not reported for the configured interval raises a fault, and the vehicle is flagged as position-unknown to M02 | **C** | Logistics Manager |
| BRU-FLT-20 | Vehicle disposal requires approval within the authority matrix and notification to M49 before the vehicle leaves Company control | **H** | CFO |
| BRU-FLT-21 | A vehicle taken off-road that holds M15 van stock triggers a stock-recovery task; the stock remains the responsibility of the assigned technician | **H** | Inventory Manager |
| BRU-FLT-22 | M46 never holds a customer's vehicle or a customer's device; those belong to M17 | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.vehicle` | `fix_vehicle` | The vehicle record | registration_no, chassis_no, engine_no, make, model, variant, year, vehicle_class, fuel_type, capacity, ownership_basis, lease_contract_ref, home_branch_id, cost_centre_id, fixed_asset_id (M49), stock_location_id (M15), availability_state, off_road_reason, acquired_at, disposed_at, company_id, operating_unit_id |
| `fix.vehicle.class.profile` | `fix_vehicle_class_profile` | Class-driven requirements | vehicle_class, required_documents, required_licence_class, service_interval_months, service_interval_km, pre_use_checklist_id, cost_baseline_per_km |
| `fix.vehicle.document` | `fix_vehicle_document` | One statutory document | vehicle_id, document_type (registration/fitness/tax_token/insurance/route_permit/other), reference_no, issuing_authority, issued_on, expires_on, cost, evidence_document_id, evidence_hash, state, renewed_from_id |
| `fix.vehicle.document.renewal` | `fix_vehicle_document_renewal` | A renewal in progress | document_id, initiated_at, responsible_employee_id, submitted_at, government_fee, agent_fee, penalty, completed_at, new_document_id, state |
| `fix.driver` | `fix_driver` | Driver record | employee_id (M21), licence_no, licence_class, professional, issued_on, expires_on, endorsements, behaviour_score_current, state |
| `fix.vehicle.assignment` | `fix_vehicle_assignment` | Vehicle to driver, over time | vehicle_id, driver_id, assignment_type (permanent/shift/trip/pool), assigned_from, assigned_to, assigned_by, handover_condition_out_id, handover_condition_in_id |
| `fix.vehicle.check` | `fix_vehicle_check` | Daily pre-use check | vehicle_id, driver_id, checked_at, checklist_id, lines, defects_found, photographs, offline_captured, synced_at, result |
| `fix.vehicle.defect` | `fix_vehicle_defect` | A reported defect | vehicle_id, raised_by, raised_at, category, safety_critical, description, evidence_ids, state, cleared_at, cleared_by, related_repair_id |
| `fix.vehicle.service` | `fix_vehicle_service` | Preventive or corrective service | vehicle_id, service_type, provider_party_id, performed_on, odometer, work_performed, parts, labour_cost, parts_cost, total_cost, invoice_ref, downtime_hours, next_due_date, next_due_odometer |
| `fix.vehicle.consumable` | `fix_vehicle_consumable` | Tyres, batteries and similar | vehicle_id, consumable_type, identifier, position, fitted_on, fitted_odometer, expected_life_km, removed_on, removed_odometer, removal_reason, cost |
| `fix.vehicle.odometer` | `fix_vehicle_odometer` | Reading with provenance | vehicle_id, reading, read_at, source (driver_app/service/telematics), captured_by, accepted, rejection_reason |
| `fix.vehicle.fuel` | `fix_vehicle_fuel` | A fuel or lubricant transaction | vehicle_id, driver_id, transacted_at, station_party_id, product, quantity, unit_price, total, odometer, payment_method, receipt_document_id, exception_flags, review_state, expense_claim_id (M52) |
| `fix.vehicle.fuel.exception` | `fix_vehicle_fuel_exception` | A flagged transaction | fuel_id, rule_code, rule_inputs, severity, raised_at, reviewed_by, disposition, notes |
| `fix.telematics.device` | `fix_telematics_device` | The tracker as an asset | device_identifier, provider_party_id, sim_number, data_plan_ref, firmware, fitted_vehicle_id, fitted_on, removed_on, health_state, last_report_at |
| `fix.vehicle.trip` | `fix_vehicle_trip` | A journey | vehicle_id, driver_id, started_at, ended_at, start_location, end_location, distance_km, duration_minutes, purpose, attributed_job_id, attributed_cost_centre_id, source |
| `fix.driver.behaviour` | `fix_driver_behaviour` | Behaviour aggregate per period | driver_id, period, distance_km, speeding_events, harsh_braking_events, harsh_acceleration_events, idling_minutes, normalised_score, coaching_referred_at |
| `fix.vehicle.incident` | `fix_vehicle_incident` | Accident, theft, damage, violation | vehicle_id, driver_id, incident_type, occurred_at, location, description, third_parties, injuries_flag, police_reference, cargo_affected, affected_asset_ids (M17), photographs, hse_case_id (M59), state |
| `fix.vehicle.insurance.claim` | `fix_vehicle_insurance_claim` | Motor claim | incident_id, vehicle_id, policy_ref, notified_at, assessor, assessed_amount, authorised_repair_id, settled_amount, excess, settled_at, state |
| `fix.vehicle.penalty` | `fix_vehicle_penalty` | Fine or penalty | vehicle_id, driver_id, issued_on, authority, offence, amount, paid_at, recovery_decision, approved_by |
| `fix.vehicle.cost` | `fix_vehicle_cost` | Assembled running cost | vehicle_id, period, distance_km, fuel_cost, service_cost, repair_cost, consumable_cost, document_cost, insurance_cost, depreciation (M49), downtime_cost, total_cost, cost_per_km, basis_reconciled, inputs_json |
| `fix.vehicle.disposal` | `fix_vehicle_disposal` | Replacement and disposal | vehicle_id, recommended_at, basis, approved_by, replacement_requisition_id (M16), route (sale/scrap/lease_return), proceeds, disposed_at, fixed_asset_notified_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, exit clearance checklist | **M21** | Read for driver identity; write a clearance blocker |
| `fix.asset`, depreciation schedule | **M17** / **M49** | Read depreciation for cost assembly; supply acquisition and disposal triggers |
| `fix.stock.location` (the van) | **M15** | Read; raise stock-recovery tasks when the vehicle goes off-road |
| `fix.visit`, `fix.dispatch.job` | M02 | Read for job attribution; provide availability as a constraint |
| `fix.consignment`, `fix.custody.event` | M03 | Read for cargo attribution on an incident |
| `fix.asset` (customer devices in the vehicle) | M17 / M49 | Read; notify on incident |
| `fix.party` — garage, fuel station, insurer, telematics provider | M33 | Read |
| `fix.purchase.order`, `fix.goods.receipt` | M16 | Read as acquisition source |
| `fix.expense.claim`, `fix.ap.invoice` | M52 | Read/write for fuel and service settlement |
| `fix.insurance.policy` | M60 | Read policy terms and expiry |
| `fix.incident.investigation` | M59 | Create on an injury incident; read status |
| `fix.competency`, `fix.enrolment` | M22 | Write a coaching referral from behaviour score |
| `fix.telemetry.stream` | **M48** | Read derived signals; M48 owns ingestion |
| `fix.document`, `fix.retention.class` | M24 | Read/write document evidence |
| `fix.branch`, `fix.entity`, `fix.cost.center` | M30 / M54 | Read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FLT-01 | Statutory document due in 60, 30, 15, 7 and 1 days | Alert the vehicle custodian, then the branch manager, then the Logistics Manager, escalating at each step, and open a renewal task at 30 days | Alert only; never silently suppressed |
| AUT-FLT-02 | Document expiry date passes, midnight | Mark the vehicle off-road, revoke it from open assignments, notify M02 and M03, and notify the branch manager and Logistics Manager | Hard block; no failure path |
| AUT-FLT-03 | Vehicle goes off-road holding M15 van stock | Raise a stock-recovery task to the branch and notify the Inventory Manager | Manual recovery task |
| AUT-FLT-04 | Driver licence due in 60, 30 and 15 days | Alert the driver, the branch manager and HR, mirroring the BR-HRM-003 certification pattern | Alert only |
| AUT-FLT-05 | Driver licence expires | Remove the driver from vehicle assignment eligibility and notify the branch manager and M02 | Hard block on assignment |
| AUT-FLT-06 | Assignment attempted with an invalid or wrong-class licence | Reject the assignment with an explanatory reason | Hard block |
| AUT-FLT-07 | Start of a driver's shift | Present the pre-use checklist on the driver's phone; block the first job start until it is completed | Allow a configurable grace period, then block and notify |
| AUT-FLT-08 | Safety-critical defect reported | Take the vehicle off-road immediately, notify the branch manager and M02, and open a repair task | Hard block |
| AUT-FLT-09 | Service due by date or odometer | Raise a service booking task, alert the branch, and mark the vehicle off-road beyond the overdue tolerance | Alert, then enforce at tolerance |
| AUT-FLT-10 | Fuel transaction recorded | Evaluate exception rules; on breach, flag the transaction, hold it from payment approval and notify the Logistics Manager | Record with an unevaluated flag and alert |
| AUT-FLT-11 | Odometer reading submitted | Reconcile against the last accepted reading and telematics distance; reject implausible readings for confirmation | Hold for confirmation |
| AUT-FLT-12 | Telematics device silent beyond the configured interval | Raise a device fault, flag the vehicle position-unknown to M02, and notify the Logistics Manager and the provider | Alert only |
| AUT-FLT-13 | Incident reported | Take the vehicle off-road, open an incident record, notify the Logistics Manager, and where the vehicle carried customer devices notify M03 and M17 | Manual escalation |
| AUT-FLT-14 | Incident involves injury | Open an HSE case in M59 and notify the HR Director | Manual escalation |
| AUT-FLT-15 | Incident record completed | Initiate the insurance claim, attach evidence, and track it to settlement | Manual claim initiation |
| AUT-FLT-16 | Employee exit initiated in M21 | Generate the outstanding vehicle, key and document list and block clearance until it is empty | Hard block on clearance |
| AUT-FLT-17 | Month end | Assemble cost per kilometre per vehicle from all cost components and M49 depreciation, publish it, and mark unreconciled periods provisional | Publish provisional and alert |
| AUT-FLT-18 | Monthly | Compute driver behaviour scores, refer scores below the coaching threshold to M22, and publish the scorecard to branch managers | Retain previous scores and alert |
| AUT-FLT-19 | Vehicle exceeds the replacement threshold on age, distance or cumulative repair cost | Raise a replacement recommendation with the supporting evidence to the Logistics Manager and CFO | Report only |
| AUT-FLT-20 | M48 publishes a vehicle condition signal or failure prediction | Evaluate condition-triggered service plans and raise a service task where the threshold is crossed | Retain the time- and distance-based plan and alert |

---

## 12. Interfaces

### 12.1 Upstream — M46 Consumes

| Source | What | Mechanism |
|---|---|---|
| M21 Core HR | Employee identity, branch, role, exit initiation | REST + events |
| M49 Fixed Assets | Capitalisation confirmation, depreciation for cost assembly | REST |
| M16 Procurement | Vehicle acquisition, goods receipt, service and tyre purchase | Events |
| M52 Accounts Payable & Expense | Fuel and service invoice settlement, driver expense claims | Events |
| M02 Field Service | Vehicle usage reported against a job or visit (FR-FSM-058) | Events |
| M03 Logistics | Consignment carried, cargo attribution for incidents | Events |
| M15 Inventory | Van stock location linkage and current stock value at risk | REST |
| M17 Asset Registry | Customer devices in a vehicle at the time of an incident | REST |
| M48 IoT & Predictive | Derived telematics signals: distance, idle, harsh events, condition, prediction | Events |
| M60 GRC / M49 | Motor insurance policy terms and expiry | REST |
| M42 Supplier Relationship | Garage, fuel station and telematics provider terms | REST |
| M24 Documents | Statutory document evidence storage and retention | REST |
| M30 / M64 | Branch, entity, cost centre and vehicle-class governance | REST |

### 12.2 Downstream — M46 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M02 Field Service & Dispatch | **Vehicle availability as a dispatch constraint**; vehicle and telematics device identity; position-unknown flag | REST (synchronous) + events |
| M03 Service Logistics | Vehicle availability and identity for consignment planning; driver identity for the manifest | REST + events |
| M15 Inventory | Vehicle off-road notification triggering van stock recovery | Events |
| M49 Fixed Assets | Acquisition, usage, impairment, incident and disposal triggers | Events |
| M52 Accounts Payable | Validated fuel and service transactions, and held exceptions | Events |
| M54 Cost Accounting & FP&A | Vehicle cost by branch, cost centre and service line; cost per job served | Warehouse extract + REST |
| M21 Core HR | Exit-clearance blocker; licence expiry alerts | REST |
| M22 Learning & Competency | Driver coaching referrals from behaviour scores | Events |
| M57 Performance & Incentives | Driver behaviour score as an incentive input | REST |
| M59 Health & Safety | Vehicle incidents with injury; safety-critical defect trends | Events |
| M60 GRC | Compliance status, incident register, penalty register for the risk register | REST |
| M42 Supplier Relationship | Garage, fuel station and telematics provider performance | Events |
| M47 Facility | Vehicle complement per branch for parking and fit-out planning | REST |
| M48 IoT | Vehicle and device identity that every telematics stream binds to | REST |
| M25 BI / M62 Data Platform | Vehicle, cost, compliance, incident and behaviour facts | Warehouse extract |
| P03 Admin Portal | Full fleet register, compliance dashboard, cost analytics | REST |
| P02 Technician App | Pre-use check, defect reporting, fuel and odometer capture | REST + sync |
| P09 Rider Application | Pre-use check and vehicle assignment for riders | REST + sync |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `vehicle.registered` | vehicle, class, branch, ownership basis, asset reference | M49, M02, M03 |
| `vehicle.available` | vehicle, branch, effective from | M02, M03 |
| `vehicle.off_road` | vehicle, reason, effective from, expected return, stock at risk | **M02, M03, M15** |
| `vehicle.document_expiring` | vehicle, document type, expiry date, days remaining | M60, M52 |
| `vehicle.document_expired` | vehicle, document type, expiry date | M02, M03, M60 |
| `vehicle.document_renewed` | vehicle, document type, new expiry, cost | M52, M54 |
| `vehicle.assigned` | vehicle, driver, assignment type, period | M02, M03, M21 |
| `vehicle.check_completed` | vehicle, driver, result, defects | M02, M59 |
| `vehicle.defect_raised` | vehicle, defect, safety-critical flag | M02, M59 |
| `vehicle.service_due` | vehicle, trigger, due date or odometer | M02, M16 |
| `vehicle.service_completed` | vehicle, provider, cost, downtime, next due | M49, M52, M42 |
| `vehicle.fuel_recorded` | vehicle, driver, quantity, cost, odometer | M52, M54 |
| `vehicle.fuel_exception` | vehicle, driver, rule, severity | M52, M60 |
| `vehicle.telematics_silent` | vehicle, device, last report | **M02**, M42 |
| `vehicle.incident` | vehicle, driver, type, cargo affected, injuries flag | **M03, M17, M59, M60** |
| `vehicle.penalty_recorded` | vehicle, driver, offence, amount | M21, M52 |
| `driver.behaviour_scored` | driver, period, score, referral flag | M22, M57 |
| `driver.licence_expiring` | driver, licence class, expiry date | M21, M02 |
| `vehicle.cost_published` | vehicle, period, cost per km, reconciled flag | M54, M25 |
| `vehicle.disposed` | vehicle, route, proceeds, approver | M49, M16 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-FLT-01 | Telematics provider platform | Inbound | Position, distance, engine hours, idle and harsh-event data — ingested through M48 from Wave 8; direct through M28 with a reduced signal set in Wave 5 |
| INT-FLT-02 | Fuel card provider, where adopted | Inbound | Transaction feed for automated reconciliation; manual receipt capture where cards are not used |
| INT-FLT-03 | BRTA Service Portal | Manual / reference | Renewal fees, status lookup and evidence. **Treated as a manual external process**; M46 manages the calendar, the responsible person and the evidence |
| INT-FLT-04 | Motor insurers and brokers | Bidirectional | Policy documents, claim notification and settlement status; document exchange in Wave 5 |
| INT-FLT-05 | Authorised garages and service providers | Outbound | Service booking and invoice reference; portal or email |
| INT-FLT-06 | Legacy vehicle files and registration folders | Inbound, one-time | Migration staging; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/vehicles/{id}` | GET | Full vehicle record with availability, documents and assignment | P03, M02, M03 |
| `/api/v1/vehicles/availability` | GET | **Availability for a branch's fleet, with off-road cause** | **M02, M03** |
| `/api/v1/vehicles` | POST | Register a vehicle | P03 |
| `/api/v1/vehicles/{id}/documents` | GET/POST | Statutory documents and renewals | P03 |
| `/api/v1/vehicles/compliance` | GET | Fleet compliance status and 90-day forward view | P03, P06, M60 |
| `/api/v1/vehicles/{id}/compliance-at` | GET | Documents valid on a given past date | M60, Legal |
| `/api/v1/vehicles/{id}/assignments` | POST | Assign a vehicle to a driver (licence-gated) | P03, M02 |
| `/api/v1/vehicles/{id}/checks` | POST | Submit the daily pre-use check (offline-capable) | P02, P09 |
| `/api/v1/vehicles/{id}/defects` | POST | Raise a defect | P02, P09 |
| `/api/v1/vehicles/{id}/odometer` | POST | Submit an odometer reading (idempotent) | P02, P09, P03 |
| `/api/v1/vehicles/{id}/fuel` | POST | Record a fuel transaction with evidence | P02, P09, P03 |
| `/api/v1/vehicles/{id}/services` | GET/POST | Service history and booking | P03 |
| `/api/v1/vehicles/{id}/incidents` | POST | Report an incident with photographs | P02, P09, P03 |
| `/api/v1/vehicles/{id}/cost` | GET | Cost per kilometre with component breakdown | P06, M54 |
| `/api/v1/drivers/{id}` | GET | Driver record, licence validity, behaviour score | P03, M02, M57 |
| `/api/v1/drivers/{id}/vehicles` | GET | Vehicles currently assigned to a driver | M21, P03 |
| `/api/v1/telematics/devices` | GET/POST | Device register and health | P03, M48 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R15 Logistics Coordinator | C R U | Own area — vehicle records, documents, services, fuel, incidents |
| R06 Branch Manager | C R U A | Own branch fleet — assignment, defect clearance, incident reporting, renewal responsibility |
| R05 Operations Director | R A | All — off-road exceptions, replacement approval within threshold |
| R16 Rider / Delivery Agent | R U | Own assigned vehicle — pre-use check, defect, fuel, odometer, incident |
| R10 / R11 / R12 Technician | R U | Own assigned vehicle — pre-use check, defect, fuel, odometer, incident |
| R07 Dispatch Manager | R | Assigned zones — availability as a dispatch constraint only |
| R17 Inventory Manager | R | Van-to-stock-location linkage and stock at risk |
| R19 Procurement Officer | R | All — acquisition, replacement and service provider performance |
| R26 Finance Manager / R27 Finance Officer | R A | Cost, fuel exceptions, claims, disposal, penalty recovery |
| R03 Chief Financial Officer | R A | All — insurance, disposal and capital approval |
| R30 HR Manager / R31 HR Officer | R | Driver licence validity, exit clearance, behaviour referrals |
| R32 Quality Manager / ISO Coordinator | R | Incident, defect and compliance trends for the QMS |
| R33 IT / System Administrator | R U | Telematics device configuration and technical support; no transactional rights |
| R02 Chief Technology Officer | R A | All; approves telematics integration configuration |
| R38 External Party — garage, insurer, telematics provider (P05) | R U | Own jobs, claims or devices only; never cost history, never driver data |

**Field-level restrictions.** `total_cost`, `cost_per_km`, `depreciation`, `settled_amount` and
`proceeds` are visible only to R01–R05, R15, R19, R26, R27 and R03, consistent with `05-04` §5.
Drivers see their own assignment, checks, fuel and behaviour score, and never another driver's.
`behaviour_score` and its components are visible to the driver, their branch manager, R30/R31
and R57 processes only — never to peers and never on any external portal. `nid_number` and
`licence_no` follow the identity-document restrictions in `05-04` §5.

**Segregation of duties.**
- The person who records a fuel transaction may not approve its exception review.
- The driver who reports an incident may not close the resulting insurance claim.
- The person responsible for a document renewal may not be the sole approver of the penalty
  arising from its lapse.
- A vehicle disposal follows the same separation as an inventory write-off: requester and
  approver are distinct, mirroring `05-04` §7.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Fleet compliance dashboard** | Logistics Manager, Operations Director, CFO | Real time | Every vehicle's document status, off-road vehicles and cause, next 90 days of renewals — target 100% current |
| **Vehicle availability** | Dispatch Manager, Branch Manager, Operations Director | Real time | Available, in use, off-road by cause, with stock and jobs at risk — target > 95% |
| **Cost per kilometre** | CFO, Logistics Manager, Branch Manager | Monthly | Cost per km by vehicle, class, branch and period, with the full component breakdown and the −12% trajectory |
| Cost per job served | CFO, Operations Director | Monthly | Vehicle cost attributed to field jobs, giving true cost of field delivery |
| **Fuel exception register** | Logistics Manager, Finance Manager, Internal Audit | Weekly | Flagged transactions by rule, driver and vehicle, with disposition |
| Fuel efficiency trend | Logistics Manager, Branch Manager | Monthly | Consumption per vehicle against its own history and class baseline |
| Service compliance and history | Logistics Manager, Branch Manager | Monthly | Services due, completed, overdue; cost and downtime per vehicle |
| Pre-use check compliance | Branch Manager, Operations Director | Daily | Checks completed before first job, by branch and driver; defects raised |
| **Incident and accident register** | Operations Director, HR Director, CFO, Quality Manager | Weekly | Incidents by type, driver, branch and cause; cargo and customer devices affected; injuries |
| Insurance claim status | Finance Manager, Logistics Manager | Monthly | Claims open, assessed, settled, excess recovered, ageing |
| **Driver scorecard** | Branch Manager, HR, driver | Monthly | Behaviour score with components, normalised for distance, and coaching referrals |
| Driver licence status | HR Manager, Branch Manager | Monthly | Licences valid, expiring, expired; class coverage against assigned vehicles |
| Telematics device health | Logistics Manager, IT Administrator | Daily | Devices reporting, silent, faulty; SIM and data plan status |
| Utilisation | Logistics Manager, CFO | Monthly | Distance, trips and days in use per vehicle; under-utilised vehicles as reallocation candidates |
| Replacement pipeline | CFO, Logistics Manager, Procurement | Quarterly | Vehicles beyond age, distance or repair-cost thresholds, with the capital requirement |
| Penalty and violation register | Logistics Manager, HR, Finance | Monthly | Fines by vehicle and driver, recovery decisions and outstanding amounts |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| — | **Vehicle availability** | unmeasured | 92% | **> 95%** |
| — | **Vehicle document compliance (current)** | manual | **100%** | **100%** |
| — | **Cost per kilometre** | untracked | **baselined** | **−12% against baseline** |
| — | Vehicles off-road for document expiry | unknown | < 3 events | **0** |
| — | Pre-use checks completed before first job | 0% | 90% | **98%** |
| — | Fuel transactions with a validated odometer | ~0% | 92% | **99%** |
| — | Fuel exceptions per 100 transactions | unknown | baselined | **−50% against baseline** |
| — | Preventive services completed on schedule | untracked | 88% | **96%** |
| — | Breakdown events per vehicle per year | untracked | baselined | **−30% against baseline** |
| — | Telematics devices reporting | unmeasured | 95% | **99%** |
| — | Driver licences valid against assigned vehicle class | unmeasured | **100%** | **100%** |
| — | Incidents per 100,000 km | untracked | baselined | **−20% against baseline** |
| — | Insurance claims settled within 60 days | untracked | 70% | **90%** |
| **KPI-011** *(supported)* | Technician jobs per day | 5–6 | 7–8 | **8–9** |

> **Register note.** The first three metrics are adopted verbatim from
> `_CATEGORY_OVERVIEW.md` §7 (availability > 95%, cost per kilometre baselined W5 and −12% by
> W8, document compliance 100% current). M46 has **no KPI-0nn identifiers allocated** in the
> programme KPI register; all thirteen unnumbered metrics require allocation in `06-02` (not yet
> issued). Recorded as an audit action. KPI-011 is owned by M02 and is shown as *supported*.
>
> **Baseline dependency.** Six of these targets are expressed against a baseline that does not
> yet exist. Establishing the Wave 5 baseline is itself a deliverable, and no reduction target
> is contractually meaningful until it is published and accepted (BRU-FLT-18).

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `fleet` — vehicle master, odometer logs, service records, cost entries, contract and document repository, service reminders by date or mileage | 26% |
| L2 | OCA `fleet` — `fleet_vehicle_inspection` (entry/exit inspection with cost), `fleet_vehicle_usage` (usage by employee with dates and states), `fleet_vehicle_category`, `fleet_vehicle_configuration` | 14% |
| L4 | Telematics ingestion via M48 (Wave 8) or direct provider feed via M28 (Wave 5) | 6% |
| L5 | `cd_vehicle_ext`, `cd_vehicle_compliance`, `cd_fuel_and_running_cost`, `cd_driver_management` | 54% |

> Odoo `fleet` is a genuine foundation and is used as intended — it is one of the stronger
> native modules for this purpose, and `02-05` §2 already schedules it for Wave 3. OCA
> `fleet_vehicle_inspection` is adopted as-is for the daily pre-use check; it is already
> migrated to v19 and is exactly the right shape. The custom share covers what neither
> provides: **Bangladesh statutory document compliance with automatic off-road enforcement,
> driver-licence class gating, fuel exception detection, and cost-per-kilometre assembly.**

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-163** also claimed by M20, M66; **CD-164** also claimed by M52, M66; **CD-165** also claimed by M52, M67; **CD-166** also claimed by M52, M67. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-163** | `cd_vehicle_ext` — vehicle record extension, class profiles, ownership basis, availability state machine, fixed-asset and van-stock linkage, disposal | Odoo module | 4 PW |
| **CD-164** | `cd_vehicle_compliance` — statutory document register, class-driven requirements, expiry alerting, **automatic off-road enforcement**, renewal workflow and cost, compliance-at-a-past-date evidence | Odoo module | 6 PW |
| **CD-165** | `cd_fuel_and_running_cost` — fuel capture, exception rule engine, odometer reconciliation, telematics device register and silence detection, trip and usage records, **cost-per-kilometre assembly** | Odoo module + service | 6 PW |
| **CD-166** | `cd_driver_management` — driver register, licence validity gating, assignment and handover, pre-use check surface, behaviour scoring, incident and insurance claim, penalty handling | Odoo module + driver-app surface | 4 PW |

> **CD register.** M46 has no allocation in `02-05` §5.2, which predates the module. Four new
> IDs, **CD-163…166**, are claimed from the extension block reserved for modules M31–M67,
> following CD-159…162 claimed by M45. **All CD IDs remain provisional** pending the unified CD
> register required by audit finding M-01 in `02-05`.
>
> **Category F CD block.** CD-075…077 + CD-157…158 M17 · CD-159…162 M45 ·
> **CD-163…166 M46** · CD-167…170 M47 · CD-078…079 + CD-171…173 M48.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M21 Core HR | A driver is an employee; licence gating and exit clearance depend on the employee record |
| M49 Fixed Assets | Depreciation is a component of cost per kilometre; both land in Wave 5 |
| M16 Procurement, M52 Accounts Payable | Acquisition, fuel and service settlement; available from Wave 3 |
| M24 Documents | Statutory document evidence storage with retention |
| M29, M30, M28 | Platform foundation: record rules, authority matrix, event outbox |
| M02 Field Service, M03 Logistics | Bidirectional: both consume availability and both report usage. Available from Wave 2 and Wave 3; M46 supplies availability from Wave 5 |
| M48 IoT | Telematics ingestion at scale from Wave 8. **M46 does not wait for it** — a reduced direct provider feed through M28 covers Wave 5 |

**Delivers into:** M02 and M03 gain vehicle availability as a real constraint; M15 gains
visibility of stock trapped in an off-road van; M49 and M54 gain the cost basis. Nothing is
blocked by M46's absence, which is why it is P2 — but every day it is absent is a day of
unmeasured fuel and unmanaged document expiry.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Vehicle registration folders and files | 150–400 vehicles | `fix.vehicle`, `fix.vehicle.document` | W5 cutover |
| Insurance policies | One per vehicle, various insurers | `fix.vehicle.document` (insurance) | W5, insurer-confirmed |
| Service records held by garages and branches | Fragmentary | `fix.vehicle.service` | W5, best-effort |
| Driver licences | 200–400 drivers | `fix.driver` | W5, verified against the physical licence |
| Telematics device inventory | Held by the provider | `fix.telematics.device` | W5, provider-supplied |
| Fuel records | Cash receipts and card statements | `fix.vehicle.fuel` | W5, current period only |
| Fixed-asset vehicle register | From M49 migration | `fix.vehicle` (asset link) | W5, reconciled with Finance |

> **Migration position.** Every statutory document is loaded **with its scanned evidence and its
> real expiry date**, verified against the physical document — not from a spreadsheet of dates.
> A document loaded without evidence is loaded as **expired**, which takes the vehicle off-road
> until it is produced. This will be uncomfortable at cutover and it is the only defensible
> position: a compliance register that cannot be evidenced provides false assurance, and the
> first traffic stop or insurance claim will demonstrate that at the worst possible moment.
>
> **Driver licences are verified against the physical licence at cutover**, not transcribed
> from HR files, for the same reason.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A vehicle whose registration, fitness, tax token or insurance expires is marked off-road automatically at midnight, without human action | Scheduled-job test with clock manipulation across a month boundary |
| AC-02 | An off-road vehicle cannot be assigned to a technician, rider or job through UI, API or the M02 dispatch engine | Negative test suite covering all three paths |
| AC-03 | No role, including CEO and CTO, can override an insurance-expiry off-road state | Privilege-escalation negative test |
| AC-04 | A vehicle cannot be assigned to a driver whose licence is expired or of the wrong class | Negative test across permanent, shift and pool assignment |
| AC-05 | The compliance dashboard shows every vehicle's document status and a correct 90-day forward view | Reconciliation against physical documents at three branches |
| AC-06 | The system produces, for any vehicle on any past date, the documents that were valid on that date | Scripted historical query verified against evidence |
| AC-07 | Vehicle availability for a branch's fleet returns in ≤ 150 ms at p95 | Performance test at production data volume |
| AC-08 | A vehicle taken off-road while holding van stock raises a stock-recovery task in M15 within 60 seconds | Scripted scenario with M15 |
| AC-09 | The daily pre-use check completes offline and blocks the first job start until submitted | Offline test with 20 drivers over five shifts |
| AC-10 | A safety-critical defect takes the vehicle off-road immediately and notifies M02 | Scripted scenario |
| AC-11 | Every fuel transaction records vehicle, odometer, driver and evidence; a transaction without an odometer is held | Negative test and data assertion |
| AC-12 | Each of the five fuel exception rules fires correctly on seeded data and stores its inputs | Rule-by-rule test with explainable output |
| AC-13 | A flagged fuel transaction is held from payment approval in M52 until reviewed | Scripted scenario with M52 |
| AC-14 | An odometer reading lower than the previous accepted value, or implying an implausible daily distance, is rejected for confirmation | Negative test |
| AC-15 | A replayed fuel, odometer or check submission after network failure does not double-post | Idempotency test with induced failure |
| AC-16 | Cost per kilometre is reproducible from stored inputs, including M49 depreciation, and reconciles to the general ledger | Finance-signed reconciliation for one quarter |
| AC-17 | An incident involving a vehicle carrying customer devices notifies M03 and M17 with the affected asset list | Scripted scenario |
| AC-18 | A telematics device silent beyond the configured interval raises a fault and flags the vehicle position-unknown to M02 | Scripted scenario |
| AC-19 | Employee exit clearance is blocked while a vehicle, keys or documents remain assigned | Scripted exit scenario with M21 |
| AC-20 | Driver behaviour scores route to M22 coaching and M57 incentives, and to no disciplinary process | Configuration and integration review signed by the HR Director |
| AC-21 | Statutory documents loaded without scanned evidence are loaded as expired | Migration assertion query |
| AC-22 | All driver-facing screens are complete in Bengali and default to Bengali for driver roles | Translation coverage report (AS-12) |
| AC-23 | Logistics Manager and Operations Director sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many vehicles does the Company own, lease and hire today, by class, and how many are employee-owned and reimbursed? | Logistics Manager | W5 minus 4 months |
| Q-02 | What are the current BRTA renewal cycles, fees and documentary requirements for each vehicle class the Company operates, and which classes require a route permit? | Logistics Manager / Legal | W5 design |
| Q-03 | Is the "expired insurance means off-road, no override" rule accepted by the Operations Director and CEO, including on a day when it stops a branch working? | Operations Director / CEO / CFO | W5 design |
| Q-04 | Are technicians permitted to use personal motorcycles for Company work, and if so what document, insurance and liability regime applies to them? | HR Director / Legal / CFO | W5 design |
| Q-05 | Is a fuel card programme in place or planned? Without one, every transaction is a manual capture and the exception engine's yield falls materially | Logistics Manager / CFO | W5 design |
| Q-06 | Which telematics provider is in use for BR-FSM-003, on what contract, and does the feed conform to a standard interface or a proprietary one? | CTO / Logistics Manager | W5 minus 3 months |
| Q-07 | Who is accountable for a vehicle's document renewals — the branch, a central fleet administrator, or an agent? | Logistics Manager / Operations Director | W5 design |
| Q-08 | Is a traffic fine recovered from the driver, and under what policy and labour-law constraint? | HR Director / Legal / CFO | W5 build |
| Q-09 | What are the service intervals per vehicle class — manufacturer schedule, or an internal standard adjusted for Bangladesh road and traffic conditions? | Logistics Manager | W5 build |
| Q-10 | What are the replacement thresholds — age, distance, cumulative repair cost, or a combination — and who approves? | CFO / Logistics Manager | W5 build |
| Q-11 | Are riders' motorcycles in scope from Wave 5, or is Wave 5 limited to four-wheeled vehicles with motorcycles following? | Logistics Manager / Operations Director | W5 scoping |
| Q-12 | Is the driver behaviour score published to the driver, and is it an input to the M57 incentive calculation or purely to coaching? | HR Director / Operations Director | W5 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §1 (four asset populations), §2, §5 (boundary map — M02 consumes GPS,
M46 owns the device; van stock is M15), §7 (category KPIs), §9 (risks) ·
`M17_Device_and_Customer_Asset_Registry.md` §3 ·
`M45_Enterprise_Asset_and_Test_Equipment.md` §3 ·
`M47_Facility_Branch_Infrastructure_and_Workplace.md` ·
`M48_IoT_Telemetry_and_Predictive_Maintenance.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md`
§3.2, §5 FR-FSM-058, §10.2, §12.1, §16.3 ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md`
§3.2, §10.2, §12.1 ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§5.4 (van as a stock location) ·
`03_Modules/D_Circular_and_Asset_Based_Business/M13_Rental_and_Equipment_as_a_Service.md`
§6 T-11 (ISO 15143-3 interface shape — held consistent here) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-03, AS-08, AS-12, AS-13) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category F ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §2 (`fleet` module, W3), §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1, §5, §7 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §Wave 5

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.2 OOS-4 *(the exclusion
reversed)*, BR-FSM-003, BR-FSM-004, BR-FSM-014, BR-FSM-015, BR-INV-002, BR-FIN-015, BR-HRM-003,
BR-HRM-004 ·
`1000FiX_Services_Company_Profile.md` §Additional Services, §Service Coverage

**External benchmark**
[Fleet fuel management — telematics plus fuel-card integration, cost per mile, exception reporting](https://www.geotab.com/blog/fuel-management-system-tools/) ·
[Top fleet fuel management system features for cost control](https://autosist.com/blog/top-features-fleet-fuel-management-system/) ·
[Integrating telematics and fuel cards](https://www.fleevo.io/blog/enhance-fleet-management-by-integrating-telematics-and-fuel-cards) ·
[Fleet management software key features — driver scorecards, coaching workflows, ERP integration](https://flotillaiot.com/top-fleet-management-system-features-for-2026-ultimate-guide/) —
including reported 20–30% accident reduction and 10–15% fuel reduction from eco-driving ·
[Fleetio integrations — telematics, fuel and ERP](https://www.fleetio.com/solutions/integrations) ·
[Odoo Fleet features — service scheduling by time or mileage, document repository, cost tracking](https://www.odoo.com/app/fleet-features) ·
[Managing a fleet with the Odoo 19 Fleet module](https://www.netilligence.io/blog/how-to-manage-your-fleet-using-the-odoo-19-fleet-management-module/) ·
[OCA fleet repository](https://github.com/OCA/fleet) ·
[OCA `fleet_vehicle_inspection` (19.0) — entry and exit inspections with cost](https://github.com/OCA/fleet/tree/19.0/fleet_vehicle_inspection) ·
[OCA `fleet_vehicle_usage` — usage records by employee](https://apps.odoo.com/apps/modules/16.0/fleet_vehicle_usage) ·
ISO 15143-3 (AEMP 2.0) — vendor-neutral equipment telematics interface ·
[BRTA vehicle fitness requirements — more frequent inspection for commercial vehicles](https://brtaserviceportal.com/brta-car-fitness-check-cost-in-bangladesh/) —
documents required include previous certificate, registration, tax token, insurance and licence ·
[BRTA registration fees and annual road tax](https://brtaserviceportal.com/brta-car-registration-fees/) ·
[Bangladesh Road Transport Authority](https://brta.gov.bd/) — registration, fitness, tax token,
route permit and professional driving licence

---

*Module M46 · Category F · 1000FiX ERP System v2.0 · CONFIDENTIAL*
