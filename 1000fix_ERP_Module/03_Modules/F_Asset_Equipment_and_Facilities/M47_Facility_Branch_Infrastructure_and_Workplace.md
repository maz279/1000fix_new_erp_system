---
id: FIX-ERP2-M47
module_id: M47
module_code: FAC
module_name: Facility, Branch Infrastructure & Workplace
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Branch Operations Lead
system_owner: Asset & Facilities Squad
priority: P3
wave: W7
---

# M47 — Facility, Branch Infrastructure & Workplace
### Category F · Code `FAC` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M47 |
| **Module code** | `FAC` |
| **Category** | F — Asset, Equipment & Facilities |
| **Status** | ★ New in v2.1 — **reverses exclusion OOS-5 in the v1.0 BRD** ("Property / real estate management for service center premises — outside core operations") |
| **Priority** | **P3** |
| **Delivery wave** | W7 (Months 27–30) |
| **Business owner** | Branch Operations Lead |
| **System owner** | Asset & Facilities Squad |
| **Delivery layers** | L1 Odoo `maintenance` and `project` · L2 OCA `management-system`, `contract`, `dms` · L5 custom site, lease, compliance and facility work-order engines |
| **Custom modules** | `cd_site_register`, `cd_lease_admin`, `cd_facility_work_order`, `cd_site_compliance` |
| **Requirement range** | FR-FAC-001 … FR-FAC-044 |
| **Requirement count** | **44** *(measured — supersedes the 22 estimate in `02-02`)* |
| **Effort estimate** | **20 person-weeks** *(measured — supersedes the 11 PW estimate)* |
| **Depends on** | M30 Platform Admin · M33 Party Master · M29 Identity · M28 Integration · M49 Fixed Assets · M19 Financial Accounting · M16 Procurement · M52 Accounts Payable · M24 Documents · M45 Enterprise Assets |
| **Depended on by** | M04, M31, M15, M41, M45, M46, M48, M49, M19, M54, M59, M60, M67, M25 |

---

## 2. Purpose

M47 is the register and control system for **the places 1000FiX operates from** — 51+ service
centres, stations, workshops, warehouses and the corporate office. It answers four questions:
*what premises do we hold and on what terms, are they legal to operate, does the infrastructure
in them work, and what does each site cost to run?*

A service branch is not a passive box. It contains a generator and a UPS that keep the workshop
running through load shedding, air conditioning that protects both the electronics and the
customers waiting at the counter, a fire extinguisher whose certificate expires, a lease whose
renewal date nobody is watching, a trade licence and a fire licence without which the branch is
operating unlawfully, and a landlord who must be paid on a date.

Today all of that lives in 51 separate heads and 51 separate drawers. M47 puts it in one place
and enforces the dates.

### Why It Exists

The v1.0 BRD excluded premises management as "outside core operations" (OOS-5). That
judgement is defensible for a company with three offices. It fails at 51+ locations for three
reasons.

**Statutory compliance at 51 sites is not a clerical matter.** Every premises requires a current
trade licence, and commercial establishments require a fire licence issued by the Fire Service
and Civil Defence under the Fire Prevention and Fire Fighting Act 2003 — renewed annually.
These interlock: a trade licence renewal can be refused where the fire licence has lapsed. At
51 sites with 51 different renewal dates, managed on paper, some proportion is always expired,
and the Company does not know which.

**Infrastructure failure stops revenue.** A branch without power runs no workshop. A branch
without air conditioning in Dhaka in May cannot hold customers at a counter or run a bench
safely. These are not facilities inconveniences — they are direct causes of the turnaround time
and CSAT that M01 and M34 are measured on, and nobody currently connects the two.

**Branch cost is invisible.** Rent, utilities, maintenance, security and cleaning are booked to
a branch cost centre in aggregate. Whether a given branch is expensive because it is large,
because it is badly maintained or because its electricity bill is anomalous cannot be
determined. M54 cannot do branch profitability properly without a facility cost basis.

M47 is P3 and lands in Wave 7 — the latest of the Category F modules — because it does not
block any service transaction. That priority is a judgement about sequence, not about value:
the statutory-compliance component alone justifies the module, and if a licence lapse is
discovered before Wave 7, the compliance register is the slice to pull forward.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.2 OOS-5 | "Property / real estate management for service center premises — outside core operations" — **the exclusion this module reverses** |
| ERP BRD BR-INV-001 | "Manage inventory across 51+ service center locations plus central warehouse(s)" — establishes the estate size M47 must administer |
| ERP BRD BR-BI-002 | "Provide branch performance dashboards comparing all 51+ locations" — branch comparison is incomplete without facility cost and availability |
| ERP BRD BR-FIN-001 | "Multi-branch chart of accounts with configurable structure per branch and cost center" — the accounting structure facility cost attaches to |
| ERP BRD BR-FIN-015 | "Track fixed assets and calculate depreciation" — leasehold improvements and building services are capitalised assets |
| ERP BRD BR-QMS-001 | ISO 9001:2015 compliance documentation — premises and infrastructure are within the scope of the quality management system |
| ERP BRD BR-QMS-004 | Internal audit management — branch facility audits are part of the audit programme |
| Company Profile §Service Infrastructure | "1000FiX Station" network expansion; service centres across Bangladesh; Elephant Road branch and others — a growing estate |
| Company Profile §Future Outlook | "Expanding service center network (1000FiX Station)" — new-site opening is a recurring process, not a one-off |
| `_CATEGORY_OVERVIEW.md` §1, §2 | M47 owns "51+ premises: leases, utilities, maintenance, security, safety equipment, occupancy, opening and closing" |
| `_CATEGORY_OVERVIEW.md` §5 | Branch premises, lease and utilities are M47; M30 owns branch configuration as an org unit; fire, safety and first-aid equipment is M47 inventory and M59 compliance |
| `_CATEGORY_OVERVIEW.md` §7, §9 | Branch statutory compliance 100% current; maintenance requests closed within SLA > 90%; risk of facilities being bolted on late |
| `M04` §3.2 | M04 declares branch premises, lease, utilities and maintenance out of scope and assigns them to M47 |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** The sharpest boundary is with M30: a branch is
> simultaneously an organisational unit (M30) and a physical site (M47). One branch, two
> records, one link. Both sides agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The site register: every premises the Company occupies — service centre, station, workshop, warehouse, office, storage |
| 2 | Site attributes: address, geolocation, area, floor, layout zones, capacity, service capability and operating hours |
| 3 | **Lease and tenancy administration**: landlord, term, rent, escalation, deposit, notice period, break clause, renewal option |
| 4 | Critical-date control for every lease event, with escalation and a decision workflow |
| 5 | Rent and service-charge scheduling, and the data extract that supports lease accounting in M19 and M49 |
| 6 | **Statutory site compliance**: trade licence, fire licence, signage permit, environmental clearance, generator permit and any local authority requirement |
| 7 | Compliance expiry control, renewal workflow, evidence retention and operating-risk escalation |
| 8 | Utility accounts and consumption: electricity, gas, water, internet and telephony, per site |
| 9 | Utility consumption anomaly detection and cost per square foot |
| 10 | **Branch infrastructure asset register**: generator, UPS, air conditioning, electrical distribution, water, CCTV, access control, fire detection and suppression, signage, furniture |
| 11 | Preventive maintenance schedules for building services, and their execution |
| 12 | **Facility work orders**: request, triage, assignment, vendor dispatch, SLA, completion, verification and cost |
| 13 | Facility vendor management at execution level: assignment, SLA performance and quality |
| 14 | Safety equipment register: fire extinguishers, alarms, emergency lighting, first-aid kits, with inspection and refill dates |
| 15 | Security: guarding arrangement, CCTV coverage and retention, access control, key and alarm-code custody, incident log |
| 16 | Site condition assessment and periodic facility audit |
| 17 | Occupancy: seats, workstations, bench positions, queue and waiting capacity against branch headcount |
| 18 | **Site opening**: fit-out checklist, equipment complement, licence acquisition, readiness gate and go-live sign-off |
| 19 | **Site closure and relocation**: asset recovery, licence surrender, deposit recovery, data and record handling |
| 20 | Facility cost per site: rent, utilities, maintenance, security, cleaning, compliance, and cost per square foot and per job |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The branch as an organisational unit, its code, hierarchy and configuration** | **M30** Platform Administration | M30 owns the operating unit that scopes data and permissions; M47 owns the physical place. A branch that moves premises keeps its M30 identity and gets a new M47 site |
| **Branch service operations, queue, counter and cash drawer** | **M04** Branch & Front-Desk Operations | M47 provides the premises; M04 runs the operation inside it |
| **Workshop process, bench allocation and repair throughput** | **M31** Workshop & Depot Repair | M47 owns the bench as a physical position; M31 owns what happens at it |
| **Stock held at a branch, and warehouse bin and pick logic** | **M15 / M41** | Stock is inventory; the shelf it sits on is a facility asset |
| **Tools, test equipment and portable IT assets issued to people** | **M45** Enterprise Asset & Test Equipment | Building services are fixed to the site; equipment is issued to a person. A branch's label printer is M45; its air conditioner is M47 |
| **Vehicles, including those parked at a site** | **M46** Fleet & Vehicle Management | The car park is a facility; the vehicle in it is a fleet asset |
| **Capitalisation and depreciation of leasehold improvements and building services; right-of-use asset and lease liability recognition** | **M49** Fixed Assets **and M19** Financial Accounting | M47 supplies the lease terms and the asset register; only Category G posts to the ledger |
| **Lease accounting judgements, discount rate and remeasurement** | **M19** Financial Accounting | M47 is the authoritative source of lease *data*; the accounting treatment is Finance's |
| **Rent and utility invoice payment** | **M52** Accounts Payable | M47 validates against the site, the contract and the consumption; M52 pays |
| **Landlord and facility vendor sourcing, contracting and scorecards** | **M16 / M42** | M47 assigns work and records performance; the commercial relationship is Procurement's |
| **Property acquisition, disposal and capital approval** | **M49 / M54 / M67** | A new branch is a capital project; M67 runs the project, M54 budgets it, M47 delivers the facility readiness |
| **Health and safety policy, risk assessment, incident investigation and drills** | **M59** Health, Safety & Wellbeing | M47 records that safety equipment exists and is inspected; M59 owns the HSE management system |
| **Corporate insurance policy administration** | **M60** GRC / **M49** | M47 records site values and raises claims; policy administration is Finance and GRC |
| **Employee seating allocation and hot-desking preference** | **M21** Core HR | M47 provides capacity; HR allocates people |
| **Internal IT infrastructure — servers, network equipment, endpoint builds** | **M66** Internal IT Service Management | M47 owns the comms room as a space and its power and cooling; M66 owns what is racked in it |
| **Building-services telemetry ingestion** | **M48** IoT & Predictive Maintenance | M47 registers the asset and consumes the signal; M48 owns the pipe |
| **New-branch project management, milestones and budget** | **M67** Project, Program & Portfolio Management | M67 runs the project; M47 owns the facility readiness checklist that is one of its gates |
| **E-waste and disposal of removed building equipment** | **M18** E-Waste & Circular Economy | M47 retires; M18 disposes |

### 3.3 Shared Concepts

| Concept | M47's Role | Owning Module |
|---|---|---|
| Site / premises | **Owns** — the defining concept of this module | M47 |
| Branch as an operating unit | References; links site to operating unit | M30 |
| Lease agreement | **Owns** the operational record and critical dates | M47 |
| Right-of-use asset and lease liability | Supplies the data; never computes or posts | M19 / M49 |
| Building service asset (generator, UPS, HVAC) | **Owns** the register and its maintenance | M47 |
| Portable equipment at a branch | References; M45 owns it | M45 |
| Safety and fire equipment | Owns the register and inspection dates; M59 owns the HSE regime | M47 / M59 |
| Facility work order | **Owns** | M47 |
| Facility vendor | Assigns and rates; M42 owns the relationship | M47 / M42 |
| Utility consumption | Owns capture and anomaly detection; M52 pays the invoice | M47 / M52 |
| Site compliance licence | **Owns**; M60 aggregates into the compliance register | M47 / M60 |
| New-branch project | Owns the facility readiness gate; M67 owns the project | M47 / M67 |
| Building-services condition signal | Consumes | M48 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **IWMS platforms (IBM TRIRIGA, Archibus, Planon, Accruent, MRI, Nakisa)** | Five functional pillars: real estate and lease administration, space management, facilities maintenance, capital projects, and sustainability — centralising the built environment in one system. Lease administration covers lease abstraction, critical-date tracking, rent payment automation and portfolio reporting, with lease-accounting output for IFRS 16 / ASC 842 | **The lease-abstraction and critical-date model is the single most influential external reference for M47.** A lease is decomposed into dated events — rent review, escalation, break option, renewal notice deadline, expiry — each of which is an alarm with an owner and a decision, not a paragraph in a PDF. Also adopted: **facilities maintenance as work orders with vendor SLA**, and the principle that facility data feeds finance rather than duplicating it | The full IWMS product footprint and its licence cost. Gartner's own definition requires all five pillars; a platform covering two or three is a CAFM or CMMS. **M47 is deliberately a CAFM/CMMS with lease administration** — pillars one, three and part of two — and does not attempt capital projects (M67) or a sustainability module (M18) |
| **IFRS 16 / BFRS 16 lease accounting** | A single lessee model recognising a right-of-use asset and a lease liability for leases over twelve months unless the underlying asset is of low value; amortisation schedules, journal generation and disclosure | **The data model required to support it**, held in M47 and published to M19: commencement date, term, extension and termination options and whether they are reasonably certain to be exercised, fixed and variable payments, and incremental borrowing rate input. Retail and branch estates are precisely the case the standard was written for | **Performing the accounting.** M47 never computes a right-of-use asset, never selects a discount rate and never posts a journal. That judgement is Finance's, and splitting it across two modules is how organisations end up with two lease liabilities |
| **CMMS practice (Limble, Fiix, Fexa, multi-site retail FM)** | A centralised facility management system unifying all locations on one platform: automated work orders, preventive maintenance scheduling by equipment type and site condition, shared checklists and vendor SLAs to hold quality consistent across sites, and auto-assignment of work to the nearest technician | **The multi-site pattern in full.** One system, standard checklists, per-site schedules adjusted for equipment and usage, vendor SLAs measured centrally. This is exactly the 51-branch problem, and the practice literature is unambiguous that per-site improvisation is what fails | Contractor-marketplace features and integrated procurement of facility services; that is M16 and M42 |
| **Availability-SLA practice for critical infrastructure (UPS, generator, HVAC)** | Uptime SLAs on building services, with unplanned outages carrying contractual penalties and driving customer churn in service environments | **Availability as the primary measure for building services, not maintenance completion.** A branch's generator is measured on whether the branch kept working, not on whether the service visit happened. Load shedding makes this the correct emphasis in Bangladesh specifically | Data-centre-grade redundancy engineering; a service branch is not a data centre |
| **Bangladesh regulatory practice** | **Fire licence** issued by Fire Service and Civil Defence under the Fire Prevention and Fire Fighting Act 2003, certifying that premises meet fire-safety standards, **renewed annually** through the FSCD office; **trade licence** renewed annually at the local authority, with renewal requiring proof of continued legal occupancy, up-to-date TIN and — for companies — an up-to-date fire licence. Authorities may refuse to renew or revoke a trade licence where the fire licence has expired | **Licence interdependency modelled explicitly.** The fire licence is not one compliance item among many — it is a *prerequisite* for another, and the renewal calendar must reflect that ordering. Also adopted: proof of occupancy as a renewal input, which links the lease record directly to the licence record | Attempting automated integration with local authorities or FSCD. Renewal is a physical, clerical process; M47 manages the calendar, the responsible person, the cost and the evidence |
| **Odoo 19 `maintenance` + `project` + OCA `contract`, `management-system`, `dms`** | Equipment records with maintenance teams and preventive requests; project tasks for fit-out; recurring contract management for leases; ISO documentation; document storage | The transactional substrate: `maintenance` for building services and facility work orders (shared with M45), OCA `contract` for the recurring rent schedule, `management-system` for the ISO documentation spine, `dms` for licence and lease evidence | None of these provides a site register, a critical-date engine, a licence-dependency model or utility anomaly detection. All four are built |

**Design position.** Four deliberate differences from the benchmark.

First, **M47 is not an IWMS and does not pretend to be.** The honest scope is a multi-site CMMS
with lease and licence administration. Capital projects belong to M67, sustainability reporting
to M18, and space planning beyond seat counts is not a problem 1000FiX has. Scoping it as an
IWMS would produce a large module that is never adopted, which is exactly the risk
`_CATEGORY_OVERVIEW.md` §9 names for this module.

Second, **statutory compliance is the minimum viable scope, and it is delivered first.** If
Wave 7 is compressed, the order of retreat is: keep the site register and the compliance
engine; defer utility anomaly detection, occupancy and condition assessment. A branch operating
on an expired fire licence is a closure risk; a branch whose electricity bill is unanalysed is
a cost inefficiency. These are not the same class of problem.

Third, **licence expiry escalates but does not automatically close a branch.** This is a
deliberate asymmetry with M46, where document expiry automatically takes a vehicle off-road. A
vehicle can be replaced by another vehicle within a day; a branch cannot, and automatically
suspending a branch's operations would cause more harm than the lapse it responds to. Instead,
expiry raises an **operating-risk exception** to the Branch Manager, the Operations Director and
the CEO, is reported until cleared, and appears on the M60 risk register. The decision to
continue operating is then a named human decision with a date on it — which is the correct
control for a risk of this shape.

Fourth, **facility work orders reuse the service-order discipline the Company already runs.**
1000FiX is a service business. It already understands request, triage, SLA, assignment,
completion and verification. M47 applies the same shape to its own premises rather than
inventing a facilities vocabulary, so a branch manager who can raise a customer job can raise a
facility job.

---

## 5. Functional Areas & Features

### 5.1 Site Register & Portfolio

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-001 | Site record | Maintain one record per premises with site code, type, address, geolocation, floor and unit, gross and usable area, occupancy basis, operating hours and status | **P0** | L5 |
| FR-FAC-002 | Site type and profile | Classify sites as service centre · station · workshop · warehouse · corporate office · storage, each with a required compliance set, infrastructure profile and equipment complement | **P0** | L5 |
| FR-FAC-003 | Organisational linkage | Link each site to its M30 operating unit and cost centre, supporting one operating unit across two sites and one site hosting two units | **P0** | L5 |
| FR-FAC-004 | Site zones | Model zones within a site — reception, counter, waiting area, workshop, bench positions, store, comms room, staff area, parking — with area and capacity | P2 | L5 |
| FR-FAC-005 | Site status | Maintain site lifecycle status: planned · fitting out · operational · under refurbishment · suspended · closing · closed | **P0** | L5 |
| FR-FAC-006 | Portfolio view | Present the whole estate on a map and in a list with status, area, cost, compliance state and infrastructure availability | P1 | L5 |
| FR-FAC-007 | Site documents | Store lease, licences, floor plans, photographs, handover records and inspection reports through M24 with retention policy applied | **P0** | L2/L5 |

### 5.2 Lease & Tenancy Administration

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-008 | Lease record | Hold the lease or tenancy with landlord party, commencement, term, expiry, rent, payment frequency, escalation basis and rate, service charge, and security deposit | **P0** | L2/L5 |
| FR-FAC-009 | Lease abstraction | Decompose the lease into dated, ownable events: rent review, escalation, break option, renewal notice deadline, expiry, deposit return, and any landlord obligation | **P0** | L5 |
| FR-FAC-010 | Critical-date alerting | Alert the responsible role at configurable horizons before each lease event — with the renewal-notice deadline treated as the highest-severity date in the module | **P0** | L5 |
| FR-FAC-011 | Renewal decision workflow | Route a lease renewal, renegotiation, break or exit decision through a recorded workflow with the branch's performance and facility cost attached as evidence | P1 | L5 |
| FR-FAC-012 | Rent schedule | Generate the forward rent and service-charge schedule per site, and reconcile actual payments against it | **P0** | L2/L5 |
| FR-FAC-013 | Deposit tracking | Track security deposits paid, held, adjusted and recovered, with ageing and a recovery workflow at exit | P1 | L5 |
| FR-FAC-014 | Lease accounting extract | Publish to M19 and M49 the data required for lease accounting: commencement, term, extension and termination options with a reasonably-certain assessment, fixed and variable payments, and modification events — **without performing the accounting** | P1 | L5 |
| FR-FAC-015 | Lease variation | Record a lease modification — rent change, area change, term extension — as a dated event that supersedes prior terms and notifies Finance of a remeasurement trigger | P1 | L5 |

### 5.3 Statutory & Operating Compliance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-016 | Compliance item register | Hold each statutory requirement per site as a separate record with authority, reference number, issue and expiry dates, cost, responsible role and scanned evidence: **trade licence, fire licence, signage permit, environmental clearance, generator permit** and any local requirement | **P0** | L5 |
| FR-FAC-017 | Site-type requirement set | Derive the required compliance set from site type, so that a warehouse and a counter-only station carry different obligations | **P0** | L5 |
| FR-FAC-018 | **Licence dependency** | Model prerequisite relationships between licences — notably that trade licence renewal depends on a current fire licence — and sequence the renewal calendar accordingly | **P0** | L5 |
| FR-FAC-019 | Expiry alerting and escalation | Alert at 90, 60, 30, 15 and 7 days before expiry, escalating from the branch manager to the Branch Operations Lead to the Operations Director, and on expiry to the CEO | **P0** | L5 |
| FR-FAC-020 | Operating-risk exception | On expiry, raise an operating-risk exception against the site, publish it to the M60 risk register, and require a named continue-or-suspend decision with a date — **without automatically suspending operations** | **P0** | L5 |
| FR-FAC-021 | Renewal workflow | Track a renewal from initiation through document assembly, submission, fee payment, inspection where required, and evidence upload, with the responsible person and total cost recorded | **P0** | L5 |
| FR-FAC-022 | Compliance evidence at a date | Produce, for any site on any past date, the licences that were valid on that date | P1 | L5 |
| FR-FAC-023 | Estate compliance dashboard | Present compliance status across the whole estate by site, licence type and expiry horizon, with the 100%-current target visible | **P0** | L5 |

### 5.4 Infrastructure Assets & Maintenance

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-024 | Infrastructure asset register | Register every fixed building-service asset per site — generator, UPS, air conditioning unit, electrical distribution board, water system, CCTV, access control, fire detection and suppression, signage, major furniture — with make, model, capacity, install date, warranty and expected life | **P0** | L1/L5 |
| FR-FAC-025 | Preventive maintenance plans | Define PM schedules per asset class and site, triggered by elapsed time, running hours or condition, generating scheduled facility work orders | **P0** | L1/L5 |
| FR-FAC-026 | Generator and UPS regime | Apply a specific maintenance and testing regime to power-continuity assets — load test, fuel level, battery condition, run-hours — reflecting their role in keeping a branch operating through load shedding | **P0** | L5 |
| FR-FAC-027 | Infrastructure availability | Track availability and outage of critical building services per site, with cause and duration, and report branch operating hours lost | **P0** | L5 |
| FR-FAC-028 | Asset condition and life | Record condition assessments and remaining-life estimates, feeding a replacement pipeline and a capital plan for M54 | P2 | L5 |
| FR-FAC-029 | Fixed-asset linkage | Link capitalised infrastructure and leasehold improvements to M49 fixed-asset records and supply disposal and impairment triggers | P1 | L5 |
| FR-FAC-030 | Condition-triggered maintenance | Where M48 supplies a condition signal for a connected building-service asset, evaluate condition-triggered plans and raise work accordingly | P2 | L5 |

### 5.5 Facility Work Orders & Vendors

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-031 | Facility request | Allow any branch role to raise a facility request by category and urgency from the admin portal or a phone, with photographs, and acknowledge it immediately | **P0** | L5 |
| FR-FAC-032 | Triage and SLA | Triage a request to a priority with a response and resolution SLA by category and site criticality, and track elapsed time against both | **P0** | L5 |
| FR-FAC-033 | Assignment | Assign work to an internal facility resource or an approved external vendor, with the assignment, acceptance and attendance recorded | **P0** | L5 |
| FR-FAC-034 | Completion and verification | Require completion evidence and branch verification before a work order closes, so that "attended" and "fixed" are distinguishable | **P0** | L5 |
| FR-FAC-035 | Work order cost | Capture labour, parts and vendor cost per work order, attributed to the site and cost centre, and route the invoice reference to M52 | P1 | L5 |
| FR-FAC-036 | Vendor SLA performance | Measure facility vendor response time, resolution time, first-time fix and repeat-visit rate, and publish it to the M42 scorecard | P1 | L5 |
| FR-FAC-037 | Recurring services | Manage recurring facility services — cleaning, security guarding, pest control, waste removal, generator fuel supply — with schedule, attendance verification and cost | P2 | L5 |

### 5.6 Utilities, Safety, Security & Occupancy

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FAC-038 | Utility accounts and consumption | Hold utility accounts per site — electricity, gas, water, internet, telephony — with meter identifiers, tariff, billing cycle, consumption and cost per period | **P0** | L5 |
| FR-FAC-039 | Consumption anomaly detection | Compare consumption against the site's own history, its area and its peer sites, and flag anomalies for investigation before the invoice is approved | P1 | L5 |
| FR-FAC-040 | Safety equipment register | Register fire extinguishers, alarms, emergency lighting, exit signage and first-aid kits per site with location, inspection interval, refill or replacement date and inspection evidence, and alert before each due date | **P0** | L5 |
| FR-FAC-041 | Security arrangements | Record guarding arrangement and roster, CCTV camera inventory, coverage and retention period, access-control configuration, and key and alarm-code custody | P1 | L5 |
| FR-FAC-042 | Site incident log | Record facility incidents — break-in, fire, flood, power failure, structural damage, unauthorised access — with evidence, notification to M59 and M60, and any insurance claim | P1 | L5 |
| FR-FAC-043 | Occupancy and capacity | Record seats, workstations, bench positions and customer waiting capacity per site, compare them to assigned headcount and footfall, and flag over- and under-utilised sites | P2 | L5 |
| FR-FAC-044 | **Site opening and closure** | Run a site opening as a checklist of lease, licence, fit-out, infrastructure, equipment complement, safety, security and connectivity items with a readiness gate and sign-off; and run a closure as asset recovery, licence surrender, deposit recovery, record handling and final settlement | P1 | L5 |

> **Cross-cutting.** Facility cost per site, cost per square foot, cost per job served,
> compliance rates and infrastructure availability are delivered as analytics over the register
> and are specified in §14. New-branch **project** management — milestones, budget, contractors —
> is owned by M67; M47 owns only the facility readiness gate within it (FR-FAC-044).

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Critical dates as first-class scheduled objects** | Every lease and compliance date is a stored, ownable, alertable object with its own state — not a date column scanned by a report. This is what makes a missed date impossible to explain away |
| T-02 | **Licence dependency graph** | Prerequisite relationships between compliance items are stored as a directed graph and evaluated when scheduling renewals, so a dependent renewal is never scheduled before its prerequisite |
| T-03 | **Operating-risk exception is a stored state** | Site compliance state is written by the scheduled job and read by every consumer; no module re-implements expiry arithmetic |
| T-04 | **Append-only registers** | Lease events, compliance records, work orders, utility readings and incidents are insert-only; corrections are compensating entries with a reason and a reference |
| T-05 | **Document evidence integrity** | Licences, leases and inspection certificates are stored as PDF/A with a content hash on the record, so a substituted scan is detectable |
| T-06 | **Lease data publication, not lease accounting** | The extract to M19 and M49 is a versioned, timestamped data contract. M47 never stores a right-of-use asset, a lease liability or a discount rate |
| T-07 | **Work-order SLA clock** | Response and resolution clocks pause only for defined states — awaiting parts, awaiting branch access, awaiting approval — and every pause is logged with a reason, exactly as in M01 |
| T-08 | **Offline facility audit** | Facility and safety-equipment audits operate offline on a phone and synchronise through an append-only journal with server-side conflict resolution (AS-13) |
| T-09 | **Idempotent capture** | Meter readings, inspection submissions and work-order updates carry a client idempotency key; replay after network failure must not double-post |
| T-10 | **Consumption anomaly explainability** | Every anomaly flag stores its comparison basis — own history, area normalisation, peer group — so the branch can be told why its bill was questioned |
| T-11 | **Event emission via outbox** | Every site, compliance, infrastructure and work-order state change emits a domain event through the transactional outbox (AS-08) |
| T-12 | **Multi-entity and operating-unit isolation** | Every site carries `company_id` and `operating_unit_id`; a branch manager sees their own sites, the Branch Operations Lead sees the estate (AS-03) |
| T-13 | **Scale envelope** | 51–120 sites, 1,500–4,000 infrastructure assets, 12,000 facility work orders and 6,000 utility readings per year — modest volume, high compliance consequence |
| T-14 | **Geospatial support** | Sites carry geolocation for the portfolio map, for M02 zone planning and for M03 routing; coordinates are validated on entry |
| T-15 | **Bengali support** | Branch-facing screens — facility request, safety inspection, meter reading — are complete in Bengali (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M47 |
|---|---|---|
| **Branch manager** | Keeps the lease, the trade licence and the fire licence in a drawer and the dates in memory | Sees the branch's compliance status, next renewals and open facility jobs on one screen; is alerted before, not after |
| **Front-desk agent** | Reports a broken air conditioner by phoning someone who may or may not act | Raises a facility request in the portal; it is acknowledged, has an SLA, and can be chased |
| **Technician / workshop supervisor** | Loses bench time to power failure with no record that it happened | Infrastructure outage recorded with duration and cause, and visible as lost operating hours |
| **Branch Operations Lead** | Cannot say which of 51 branches has an expired licence | Estate-wide compliance dashboard with a forward view, and a named owner for every renewal |
| **Facility vendor** | Attends when convenient; performance is anecdotal | Assigned with an SLA, verified on completion, and measured on response, resolution and repeat visits |
| **Operations Director** | Cannot connect branch performance to branch conditions | Sees facility availability alongside TAT and CSAT, and can tell a maintenance problem from a management problem |
| **CFO** | Rent and utilities are a cost line; lease commitments are a spreadsheet | Forward rent commitments, deposit position, cost per square foot per site, and a defensible lease data source for M19 |
| **Finance / audit** | Lease accounting data assembled from PDFs at year end | A single authoritative lease record published to M19 as a data contract |
| **Quality Manager** | Branch audits cover process but not premises | Facility condition, safety equipment and compliance are auditable from the same system as the QMS |
| **CEO** | Learns of a licence lapse when an inspector arrives | Sees expiry escalations before they become closures, and signs the continue-or-suspend decision knowingly |

### 7.2 Quantified Business Benefit

M47 is a **compliance, continuity and cost-control module**. It carries no revenue line in the
Scope Charter §6.2 benefit register, and none is claimed.

| Benefit | Mechanism | Value |
|---|---|---|
| **Branch closure risk eliminated** | 100% statutory compliance with modelled licence dependency and escalation before expiry | The dominant benefit. A branch closed by an authority loses all of its revenue for the closure period, plus reputational cost in its catchment. **Branch statutory compliance 100% current** (`_CATEGORY_OVERVIEW.md` §7) |
| **Operating continuity** | Preventive maintenance and testing regimes on generators, UPS and air conditioning; outage recorded and acted on | Protects branch operating hours, and therefore turnaround time (KPI-002) and technician productivity (KPI-011). In a load-shedding environment, power continuity is throughput |
| **Facility responsiveness** | Requests with SLA, assignment and verified completion instead of phone calls | **Facility maintenance requests closed within SLA > 90%** (`_CATEGORY_OVERVIEW.md` §7) |
| **Utility cost recovery** | Consumption anomaly detection before invoice approval; cost per square foot benchmarked across 51 sites | Utilities across 51+ sites are a material recurring cost; peer benchmarking makes the outliers visible for the first time |
| **Lease cost control** | Renewal decisions taken deliberately, with branch performance and facility cost as evidence, and before the notice deadline | A lease auto-renewed by inattention at an escalated rent is a multi-year cost. The renewal-notice deadline is the highest-severity date in the module for exactly this reason |
| **Deposit recovery** | Deposits tracked, aged and recovered at exit | Security deposits across an estate of this size are working capital currently at risk of being forgotten |
| **Maintenance cost reduction** | Preventive replacing reactive; vendor performance measured; repeat visits visible | Standard multi-site FM outcome; claimed conservatively as avoided emergency call-out premium and extended asset life |
| **Branch profitability accuracy** | True facility cost per site attributed to the cost centre | Enables M54 branch profitability and BR-BI-002 branch comparison to be meaningful rather than indicative |
| **Insurance and claim defensibility** | Site asset register, values, safety equipment inspection and incident log | A fire or flood claim is supportable with a register and inspection evidence |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Legal standing of every site** | Operating without a current fire licence or trade licence is unlawful. Provable compliance on any past date protects the Company and its directors |
| **Duty of care** | Fire equipment inspected, emergency lighting working, exits clear, first-aid kits stocked — the physical basis of the safety commitment M59 makes on paper |
| **ISO 9001 infrastructure clause** | Clause 7.1.3 requires the organisation to determine, provide and maintain the infrastructure necessary for conformity of products and services. M47 is the evidence that it does |
| **Customer experience** | A clean, cooled, well-lit branch with a working queue display is the physical expression of a service brand. The Company's competitive claim rests partly on premises it currently cannot measure |
| **Expansion capability** | The 1000FiX Station expansion becomes a repeatable, checklist-driven, costed opening rather than an improvisation each time — the single largest operational benefit for a growing estate |
| **Orderly exit** | Site closure with asset recovery, licence surrender and deposit recovery ensures a closing branch does not leave assets, liabilities and licences behind it |
| **Environmental basis** | Electricity and generator fuel consumption per site is the Company's second measurable direct emissions source after fleet, and the only credible input to a facilities footprint (with M18) |

---

## 8. Lifecycle & State Models

### 8.1 Site Lifecycle

```
   ┌───────────┐  site identified, lease heads of terms agreed
   │  PLANNED  │  (M67 project opened)
   └─────┬─────┘
         │ lease signed, deposit paid, M49 asset created
   ┌─────▼─────────┐
   │  FITTING OUT  │  fit-out, infrastructure install, equipment complement (M45),
   └─────┬─────────┘  licence applications, connectivity
         │ readiness gate passed — all mandatory checklist items complete
   ┌─────▼─────────┐
   │  OPERATIONAL  │◄──────────────┐
   └──┬─────┬───┬──┘               │
      │     │   │                  │ works complete, re-verified
      │     │   │  refurbishment   │
      │     │   └─────────────────►│ UNDER REFURBISHMENT
      │     │                      │
      │     │ compliance lapse, incident, or landlord action
      │     └────────────────────► SUSPENDED (named decision required)
      │                                  │
      │ closure decision approved        │ resolved
      │◄─────────────────────────────────┘
   ┌──▼────────┐
   │  CLOSING  │  asset recovery (M45, M15, M46), licence surrender,
   └──┬────────┘  deposit recovery, record handling, final settlement
      │ all closure checklist items complete
   ┌──▼────────┐
   │  CLOSED   │  retained for record and for lease-liability run-off
   └───────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Planned | Site identified and an M67 project opened | Branch Operations Lead |
| Planned | Fitting out | Lease signed, deposit paid, M49 asset created | Branch Operations Lead + CFO |
| Fitting out | Operational | **Readiness gate**: lease, trade licence, fire licence, power, connectivity, safety equipment, security, equipment complement and signage all complete and signed off | Branch Operations Lead + Operations Director |
| Operational | Under refurbishment | Refurbishment approved; interim operating arrangement recorded | Branch Operations Lead |
| Operational | Suspended | Compliance lapse, serious incident or landlord action, with a **named continue-or-suspend decision** | Operations Director / CEO |
| Suspended | Operational | Cause resolved and re-verified | Operations Director |
| Operational / Suspended | Closing | Closure decision approved | CEO + CFO |
| Closing | Closed | Assets recovered, licences surrendered, deposit recovered or written off, records transferred, final settlement complete | Branch Operations Lead + CFO |

### 8.2 Compliance Item Cycle

```
   ┌──────────┐  90/60/30/15/7 day    ┌──────────┐  submitted   ┌───────────┐
   │  VALID   │────alerts────────────►│ DUE      │─────────────►│ RENEWAL   │
   └──────────┘  branch → Ops Lead    │ SOON     │              │ IN        │
        ▲        → Ops Director       └────┬─────┘              │ PROGRESS  │
        │                                  │ expiry passes      └─────┬─────┘
        │                                  ▼                          │
        │                     ┌────────────────────────┐              │
        │                     │ EXPIRED                │              │
        │                     │ → OPERATING-RISK       │              │
        │                     │   EXCEPTION            │              │
        │                     │ → CEO notified         │              │
        │                     │ → M60 risk register    │              │
        │                     │ → named continue-or-   │              │
        │                     │   suspend decision      │              │
        │                     └────────────────────────┘              │
        │                                                             │
        └──── new licence issued, evidence uploaded and hashed ───────┘

   Dependency:  FIRE LICENCE ──must be current──► TRADE LICENCE renewal
```

| Compliance item | Cycle | Consequence of lapse |
|---|---|---|
| **Trade licence** | Annual, local authority | Unlawful operation; renewal may be refused if the fire licence has lapsed |
| **Fire licence** (FSCD, Fire Prevention and Fire Fighting Act 2003) | **Annual** | Unlawful operation; **blocks trade licence renewal**; invalidates insurance position |
| Signage permit | Per local authority | Signage removal, penalty |
| Environmental clearance, where applicable | Per category | Enforcement action |
| Generator permit / fuel storage approval | Per authority and capacity | Generator use prohibited — directly stops branch operation during load shedding |
| Lease — renewal notice deadline | Per lease | **Automatic renewal at escalated rent, or loss of the premises** — the highest-severity date in the module |
| Safety equipment inspection and refill | Per equipment class | Equipment unusable in an emergency; HSE and insurance exposure |

> The precise licence set, cycles and fees per local authority are confirmed at build time
> (Open Question Q-02). The model is configuration-driven so a change in requirement is a
> parameter change, not a code change.

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FAC-01 | Every operational site holds a current trade licence and, where required by site type, a current fire licence | **H** | Branch Operations Lead |
| BRU-FAC-02 | An expired statutory licence raises an operating-risk exception, notifies the CEO, and requires a **named, dated continue-or-suspend decision**; it does not automatically suspend operations | **A** | CEO |
| BRU-FAC-03 | A trade licence renewal cannot be scheduled or submitted while the site's fire licence is expired | **H** | Branch Operations Lead |
| BRU-FAC-04 | A site cannot move to operational status until every mandatory readiness-gate item is complete and signed off | **H** | Operations Director |
| BRU-FAC-05 | A lease renewal-notice deadline may not pass without a recorded decision by the responsible role | **H** | CFO |
| BRU-FAC-06 | Every site has exactly one accountable manager for facility and compliance matters at any time | **H** | Branch Operations Lead |
| BRU-FAC-07 | A facility work order cannot close without completion evidence and branch verification | **H** | Branch Operations Lead |
| BRU-FAC-08 | A safety-critical facility request — fire system, electrical hazard, structural, security breach — is assigned within the emergency SLA and escalates automatically if unaccepted | **H** | Branch Operations Lead |
| BRU-FAC-09 | Safety equipment past its inspection or refill date is marked unfit, and the site's safety status is flagged to M59 | **H** | Quality Manager |
| BRU-FAC-10 | Generator and UPS testing regimes are executed on schedule; a missed test escalates to the Operations Director | **C** | Branch Operations Lead |
| BRU-FAC-11 | A utility invoice whose consumption breaches the anomaly threshold is held from payment approval until reviewed | **H** | Finance Manager |
| BRU-FAC-12 | Rent is paid against the lease schedule; a payment not matching the schedule is held for review | **H** | Finance Manager |
| BRU-FAC-13 | M47 publishes lease data to M19 and M49; it never computes a right-of-use asset, a lease liability or a discount rate, and never posts a journal | **H** | CFO |
| BRU-FAC-14 | A lease modification raises a remeasurement trigger to M19 within one working day of being recorded | **C** | Finance Manager |
| BRU-FAC-15 | A site cannot reach closed status until assets are recovered and reconciled with M45, M15 and M46, licences are surrendered, and the deposit is recovered or written off with approval | **H** | CFO |
| BRU-FAC-16 | CCTV retention conforms to the period defined by M29 and M24 policy; footage is not held longer or shorter | **H** | CTO |
| BRU-FAC-17 | Key and alarm-code custody is recorded against named individuals and reconciled at every staff change at the site | **H** | Branch Manager |
| BRU-FAC-18 | A facility incident involving injury opens an HSE case in M59 the same day | **H** | HR Director |
| BRU-FAC-19 | Facility vendor performance below the agreed SLA for two consecutive periods is escalated to M42 for contractual review | **C** | Procurement Manager |
| BRU-FAC-20 | Facility cost is attributed to the site and its cost centre; unattributed facility cost is not permitted | **H** | CFO |
| BRU-FAC-21 | M47 holds premises and fixed building services only; portable equipment is M45, vehicles are M46, stock is M15, and customer devices are M17 | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.site` | `fix_site` | The premises record | site_code, name, site_type, address_id, latitude, longitude, floor, unit, gross_area, usable_area, occupancy_basis (owned/leased/licensed), operating_unit_id (M30), cost_centre_id, operating_hours, status, opened_on, closed_on, accountable_manager_id, company_id |
| `fix.site.type.profile` | `fix_site_type_profile` | What a site of this type requires | site_type, required_compliance_items, required_infrastructure_classes, required_equipment_profile (M45), required_safety_equipment, readiness_checklist_id |
| `fix.site.zone` | `fix_site_zone` | A space within a site | site_id, zone_type, name, area, capacity, seats, bench_positions, notes |
| `fix.site.lease` | `fix_site_lease` | Lease or tenancy | site_id, landlord_party_id, agreement_ref, commenced_on, term_months, expires_on, rent_amount, payment_frequency, escalation_basis, escalation_rate, service_charge, deposit_amount, notice_period_days, break_option, renewal_option, low_value_or_short_term_flag, state |
| `fix.site.lease.event` | `fix_site_lease_event` | An abstracted dated obligation | lease_id, event_type (rent_review/escalation/break_option/renewal_notice/expiry/deposit_return/landlord_obligation), due_on, responsible_role, alert_horizons, state, decision, decided_by, decided_on |
| `fix.site.lease.schedule` | `fix_site_lease_schedule` | Forward rent and service charge | lease_id, period, rent_due, service_charge_due, paid_amount, paid_on, variance, invoice_ref (M52) |
| `fix.site.deposit` | `fix_site_deposit` | Security deposit position | lease_id, amount_paid, paid_on, adjustments, recoverable_amount, recovery_initiated_on, recovered_amount, recovered_on, written_off_amount, approver_id |
| `fix.site.lease.extract` | `fix_site_lease_extract` | Versioned data contract to Finance | lease_id, version, commencement, term, extension_options, termination_options, reasonably_certain_assessment, fixed_payments, variable_payment_basis, modification_event_id, published_at, consumed_by_m19_at |
| `fix.site.compliance` | `fix_site_compliance` | One statutory item per site | site_id, item_type (trade_licence/fire_licence/signage/environmental/generator/other), authority_party_id, reference_no, issued_on, expires_on, cost, responsible_role, evidence_document_id, evidence_hash, state, prerequisite_item_ids, renewed_from_id |
| `fix.site.compliance.renewal` | `fix_site_compliance_renewal` | A renewal in progress | compliance_id, initiated_at, responsible_employee_id, documents_assembled, submitted_at, fee_paid, inspection_required, inspection_on, completed_at, new_compliance_id, total_cost, state |
| `fix.site.risk.exception` | `fix_site_risk_exception` | Operating-risk exception on lapse | site_id, compliance_id, raised_at, severity, notified_roles, decision (continue/suspend), decided_by, decided_on, review_due_on, grc_risk_id (M60), closed_at |
| `fix.site.infrastructure` | `fix_site_infrastructure` | A fixed building-service asset | site_id, zone_id, asset_class (generator/ups/hvac/electrical/water/cctv/access/fire_detection/fire_suppression/signage/furniture), make, model, capacity, serial, installed_on, warranty_until, expected_life_months, condition, availability_state, fixed_asset_id (M49), telemetry_stream_id (M48) |
| `fix.site.infrastructure.pm` | `fix_site_infrastructure_pm` | PM plan for building services | infrastructure_id or asset_class, site_id, trigger_type (elapsed/hours/condition), interval_value, interval_uom, task_template_id, next_due_at, last_completed_at, active |
| `fix.site.outage` | `fix_site_outage` | Infrastructure outage | site_id, infrastructure_id, started_at, ended_at, cause, operating_hours_lost, workaround_used, work_order_id |
| `fix.facility.work.order` | `fix_facility_work_order` | A facility job | site_id, zone_id, infrastructure_id, category, priority, raised_by, raised_at, description, photographs, response_sla_due, resolution_sla_due, assigned_type (internal/vendor), assigned_to_id, accepted_at, attended_at, completed_at, completion_evidence_ids, verified_by, verified_at, labour_cost, parts_cost, vendor_cost, invoice_ref, state, sla_pause_log |
| `fix.facility.vendor.performance` | `fix_facility_vendor_performance` | Vendor SLA outcome | vendor_party_id, period, site_scope, jobs_assigned, response_within_sla, resolution_within_sla, first_time_fix, repeat_visits, average_cost, rating |
| `fix.facility.recurring.service` | `fix_facility_recurring_service` | Cleaning, guarding, pest control and similar | site_id, service_type, vendor_party_id, schedule, contract_ref, attendance_verification_method, monthly_cost, active_from, active_to |
| `fix.site.utility.account` | `fix_site_utility_account` | Utility supply account | site_id, utility_type, provider_party_id, account_no, meter_identifier, tariff, billing_cycle, connection_capacity, active_from, active_to |
| `fix.site.utility.reading` | `fix_site_utility_reading` | Consumption and cost per period | utility_account_id, period, previous_reading, current_reading, consumption, unit, cost, invoice_ref, anomaly_flags, anomaly_basis, review_state |
| `fix.site.safety.equipment` | `fix_site_safety_equipment` | Fire and first-aid equipment | site_id, zone_id, equipment_type, identifier, capacity, installed_on, inspection_interval_months, last_inspected_on, next_due_on, refill_due_on, condition, fit_state, evidence_document_id |
| `fix.site.security` | `fix_site_security` | Security arrangements | site_id, guarding_vendor_id, guard_roster, cctv_camera_count, cctv_coverage_zones, cctv_retention_days, access_control_type, key_custody, alarm_code_custody, last_reviewed_on |
| `fix.site.incident` | `fix_site_incident` | Facility incident | site_id, incident_type (break_in/fire/flood/power/structural/unauthorised_access/other), occurred_at, description, evidence_ids, injuries_flag, hse_case_id (M59), grc_risk_id (M60), insurance_claim_ref, loss_value, state |
| `fix.site.condition.assessment` | `fix_site_condition_assessment` | Periodic facility audit | site_id, assessed_on, assessor_id, checklist_id, lines, overall_condition, remedial_actions, capital_recommendations, offline_captured |
| `fix.site.occupancy` | `fix_site_occupancy` | Capacity against use | site_id, period, seats, workstations, bench_positions, waiting_capacity, assigned_headcount, average_footfall, utilisation_index |
| `fix.site.opening.checklist` | `fix_site_opening_checklist` | Readiness gate | site_id, project_id (M67), checklist_lines, mandatory_flags, completed_lines, readiness_state, signed_off_by, signed_off_on |
| `fix.site.closure` | `fix_site_closure` | Closure execution | site_id, approved_by, approved_on, asset_recovery_lines (M45/M15/M46), licences_surrendered, deposit_recovery_id, records_transferred_to, final_settlement_amount, completed_on |
| `fix.site.cost` | `fix_site_cost` | Assembled facility cost | site_id, period, rent, service_charge, utilities, maintenance, security, cleaning, compliance_fees, insurance, depreciation (M49), total_cost, cost_per_sqft, cost_per_job, basis_reconciled |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.branch`, `fix.entity`, `fix.entity`, `fix.cost.center` | **M30** / **M54** | Read; link site to operating unit |
| `fix.party` — landlord, authority, vendor, utility provider, insurer | M33 | Read |
| `fix.asset`, depreciation schedule | **M17** / **M49** | Read for cost assembly; supply acquisition, impairment and disposal triggers |
| Lease accounting treatment, right-of-use asset, lease liability | **M19** | Write-only publication of the data extract; never read back as authoritative |
| `fix.purchase.order`, `fix.goods.receipt` | M16 | Read for infrastructure acquisition and facility services |
| `fix.ap.invoice`, `fix.ap.payment.run` | M52 | Read/write for rent, utility and facility invoice validation |
| `fix.tool.register` (branch equipment complement) | **M45** | Read for the readiness gate and closure recovery |
| `fix.stock.location` | M15 | Read for closure asset recovery |
| `fix.vehicle` | M46 | Read for parking capacity and closure recovery |
| `fix.incident.investigation`, inspection regime | **M59** | Create on injury; read the HSE requirement set |
| `fix.risk`, compliance register | **M60** | Publish operating-risk exceptions |
| `fix.project`, milestones, budget | **M67** | Read the new-branch project; publish the readiness gate result |
| `fix.telemetry.stream`, condition signal | **M48** | Read where building services are connected |
| `fix.document`, `fix.retention.class` | M24 | Read/write lease, licence and inspection evidence |
| `fix.service.order` volume per branch | M01 | Read for cost-per-job attribution |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FAC-01 | Statutory licence due in 90, 60, 30, 15 and 7 days | Alert the branch manager, escalating to the Branch Operations Lead at 30 days and the Operations Director at 15, and open a renewal task at 60 | Alert only; never silently suppressed |
| AUT-FAC-02 | Trade licence renewal scheduled while the fire licence is expired | Block the schedule, raise the fire licence renewal first, and notify the responsible role | Hard block |
| AUT-FAC-03 | Statutory licence expires | Raise an operating-risk exception, notify the CEO and the Operations Director, publish to the M60 risk register, and require a dated continue-or-suspend decision | Escalate daily until decided |
| AUT-FAC-04 | Lease critical date approaches — renewal notice, break option, rent review | Alert the responsible role and the CFO at the configured horizons, and open a decision workflow with branch performance and facility cost attached | Escalate; the renewal-notice deadline escalates to the CFO daily inside 30 days |
| AUT-FAC-05 | Lease recorded or modified | Publish the versioned lease data extract to M19 and M49 and raise a remeasurement trigger on modification | Queue and retry; alert Finance on repeated failure |
| AUT-FAC-06 | Rent or service charge falls due | Generate the payable schedule entry for M52 and reconcile it against the lease schedule | Raise a schedule-variance exception |
| AUT-FAC-07 | Facility request raised | Acknowledge immediately, triage to a priority and SLA by category and site criticality, and assign to the internal resource or approved vendor | Route to the Branch Operations Lead as a manual assignment |
| AUT-FAC-08 | Safety-critical facility request unaccepted within the emergency SLA | Escalate to the Branch Operations Lead, then the Operations Director, and notify the branch manager of the interim arrangement required | Escalate continuously |
| AUT-FAC-09 | Facility work order completed | Require branch verification before closure; on verification, capture cost and route the invoice reference to M52 | Work order remains open and reportable |
| AUT-FAC-10 | Preventive maintenance plan falls due for a building service | Raise a scheduled facility work order and assign it to the responsible vendor or internal resource | Overdue maintenance exception |
| AUT-FAC-11 | Generator or UPS test regime falls due | Raise the test task, capture the result, and escalate a missed test to the Operations Director | Escalate |
| AUT-FAC-12 | Infrastructure outage recorded | Compute operating hours lost, notify the Operations Director where the branch is stopped, and link affected service orders | Record only |
| AUT-FAC-13 | Utility reading or invoice recorded | Evaluate anomaly rules against own history, area normalisation and peer sites; on breach, hold from payment approval and notify the Branch Operations Lead and Finance | Record with an unevaluated flag and alert |
| AUT-FAC-14 | Safety equipment inspection or refill due | Alert the branch and the Quality Manager at 30 and 7 days; on lapse, mark the equipment unfit and flag the site's safety status to M59 | Escalate |
| AUT-FAC-15 | Facility incident recorded | Notify the Operations Director; on injury open an HSE case in M59; on loss initiate the insurance claim and publish to M60 | Manual escalation |
| AUT-FAC-16 | Site readiness checklist completed | Evaluate the readiness gate; on pass, notify M67 and route for Operations Director sign-off; on fail, list the outstanding mandatory items | Gate remains closed |
| AUT-FAC-17 | Site closure approved | Generate the asset recovery worklist against M45, M15 and M46, the licence surrender list and the deposit recovery task | Manual closure worklist |
| AUT-FAC-18 | Month end | Assemble facility cost per site including M49 depreciation, compute cost per square foot and cost per job served, and publish to M54 and M25 | Publish provisional and alert |
| AUT-FAC-19 | Quarterly | Compute facility vendor SLA performance and publish it to M42; escalate two consecutive periods below SLA | Retain previous scores and alert |
| AUT-FAC-20 | M48 publishes a condition signal for a connected building service | Evaluate condition-triggered PM plans and raise work where the threshold is crossed | Retain the time-based plan and alert |

---

## 12. Interfaces

### 12.1 Upstream — M47 Consumes

| Source | What | Mechanism |
|---|---|---|
| M30 Platform Admin / M64 MDM | Branch, operating unit, entity and cost-centre master | REST + event projection |
| M33 Party Master / M42 Supplier Relationship | Landlord, authority, facility vendor and utility provider identity and terms | REST |
| M49 Fixed Assets | Capitalisation confirmation and depreciation for cost assembly | REST |
| M19 Financial Accounting | Confirmation that a lease extract has been consumed and any remeasurement outcome | Events |
| M16 Procurement | Infrastructure acquisition and facility service purchase | Events |
| M52 Accounts Payable | Rent, utility and facility invoice status | Events |
| M45 Enterprise Assets | Branch equipment complement and gaps | REST |
| M15 / M41 | Stock locations at the site, for closure recovery | REST |
| M46 Fleet | Vehicles based at the site, for parking capacity and closure recovery | REST |
| M59 Health & Safety | Required inspection regimes and HSE case outcomes | REST + events |
| M67 Project Management | New-branch project, milestones and target opening date | REST |
| M48 IoT & Predictive | Condition signals from connected building services | Events |
| M01 Service Order | Branch job volume for cost-per-job attribution | Warehouse extract |
| M24 Documents | Lease, licence and inspection evidence storage | REST |

### 12.2 Downstream — M47 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M19 Financial Accounting | **Versioned lease data extract** for lease accounting; rent schedule; modification and remeasurement triggers | Events (data contract) |
| M49 Fixed Assets | Leasehold improvement and infrastructure asset register; impairment and disposal triggers | Events |
| M52 Accounts Payable | Validated rent, utility and facility invoices; held anomalies | Events |
| M54 Cost Accounting & FP&A | Facility cost per site, cost per square foot, cost per job served, capital replacement pipeline | Warehouse extract + REST |
| M04 Branch & Front-Desk | Site status, infrastructure availability, open facility jobs affecting the counter | REST |
| M31 Workshop | Bench positions, workshop infrastructure availability, outage impact | REST |
| M15 / M41 | Site storage capacity and condition | REST |
| M45 Enterprise Assets | Site placement for branch equipment; readiness-gate equipment requirements | REST |
| M46 Fleet | Parking capacity and site-based vehicle assignment | REST |
| M59 Health & Safety | Safety equipment fitness, site condition, incident register | REST + events |
| M60 GRC | Site compliance status, operating-risk exceptions, incident register for the risk register | Events |
| M67 Project Management | Facility readiness gate result for a new-site project | Events |
| M48 IoT | Site and infrastructure asset identity that building-service streams bind to | REST |
| M25 BI / M62 Data Platform | Site, compliance, cost, availability and work-order facts | Warehouse extract |
| P03 Admin Portal | Site register, compliance dashboard, facility work orders, cost analytics | REST |
| P11 Field Auditor App | Facility condition assessment and safety-equipment inspection | REST + sync |
| P05 Vendor Portal | Facility vendor job assignment, acceptance, completion evidence and SLA status | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `site.registered` | site, type, operating unit, area, occupancy basis | M30, M49, M25 |
| `site.status_changed` | site, from status, to status, reason, approver | M04, M30, M15, M45, M46 |
| `site.readiness_gate_passed` | site, checklist, outstanding items, signatory | **M67**, M04, M30 |
| `site.closing` | site, approved by, asset recovery worklist | **M45, M15, M46**, M49 |
| `site.closed` | site, final settlement, deposit outcome, records destination | M49, M19, M30 |
| `lease.recorded` | lease, site, term, payments, options | **M19, M49** |
| `lease.extract_published` | lease, version, accounting-relevant fields | **M19** |
| `lease.modified` | lease, modification type, effective date, remeasurement trigger | **M19, M49** |
| `lease.critical_date_due` | lease, event type, due date, responsible role | M52, M54 |
| `lease.renewal_decision_required` | lease, site, deadline, branch performance summary | M60, M54 |
| `site.compliance_expiring` | site, item type, expiry, days remaining | M60 |
| `site.compliance_expired` | site, item type, expiry | **M60**, M04, M30 |
| `site.risk_exception_raised` | site, item, severity, decision required by | **M60** |
| `site.risk_decision_recorded` | site, decision, decided by, review due | M60 |
| `facility.work_order_raised` | site, category, priority, SLA due | M52, M42 |
| `facility.work_order_closed` | site, category, resolution time, cost, verified by | M52, M42, M54 |
| `facility.sla_breached` | site, work order, category, elapsed | M42, M60 |
| `site.outage` | site, infrastructure, duration, operating hours lost, cause | **M04, M31**, M01 |
| `site.utility_anomaly` | site, utility, consumption, comparison basis | M52, M54 |
| `site.safety_equipment_unfit` | site, equipment, due date, location | **M59** |
| `site.incident` | site, type, injuries flag, loss value | **M59, M60**, M49 |
| `site.cost_published` | site, period, total, cost per sqft, cost per job | M54, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-FAC-01 | Local authority (city corporation / municipality) trade licence services | Manual / reference | Renewal fees, submission and evidence. **Treated as a manual external process**; M47 manages the calendar, the responsible person and the evidence |
| INT-FAC-02 | Fire Service and Civil Defence (FSCD) fire licence process | Manual / reference | Annual renewal via bank chalan and inspector submission; M47 tracks the chalan, the inspection and the certificate |
| INT-FAC-03 | Utility providers — electricity distribution, gas, water, internet | Inbound | Bill and consumption data by file or portal download where available; manual capture otherwise |
| INT-FAC-04 | Facility vendors — HVAC, generator, electrical, cleaning, security | Bidirectional | Job assignment, acceptance and completion evidence through P05 |
| INT-FAC-05 | CCTV and access-control systems at sites | Reference | Camera and controller inventory, coverage and retention configuration; footage remains on the site system under M29 policy |
| INT-FAC-06 | Legacy branch files — leases, licences, utility bills | Inbound, one-time | Migration staging; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/sites/{id}` | GET | Full site record with status, compliance and infrastructure availability | P03, M04, M30 |
| `/api/v1/sites` | GET/POST | Portfolio list and site registration | P03, P06 |
| `/api/v1/sites/{id}/leases` | GET/POST | Lease record and abstracted events | P03, M19 |
| `/api/v1/leases/{id}/extract` | GET | **Versioned lease data extract for lease accounting** | **M19, M49** |
| `/api/v1/leases/critical-dates` | GET | Estate-wide critical-date forward view | P03, P06, M54 |
| `/api/v1/sites/{id}/compliance` | GET/POST | Compliance items and renewals | P03, M60 |
| `/api/v1/compliance/status` | GET | **Estate compliance dashboard with forward view** | P03, P06, M60 |
| `/api/v1/sites/{id}/compliance-at` | GET | Licences valid on a given past date | M60, Legal |
| `/api/v1/sites/{id}/infrastructure` | GET/POST | Building-service asset register | P03, M48 |
| `/api/v1/sites/{id}/availability` | GET | Infrastructure availability and current outages | M04, M31 |
| `/api/v1/facility/work-orders` | POST | Raise a facility request | P03, P02 |
| `/api/v1/facility/work-orders/{id}` | GET/PATCH | Track, assign, complete and verify | P03, P05 |
| `/api/v1/sites/{id}/utilities` | GET/POST | Utility accounts, readings and anomalies | P03, M52 |
| `/api/v1/sites/{id}/safety-equipment` | GET/POST | Safety equipment register and inspection | P11, M59 |
| `/api/v1/sites/{id}/incidents` | POST | Record a facility incident | P03, P11 |
| `/api/v1/sites/{id}/cost` | GET | Facility cost with component breakdown | P06, M54 |
| `/api/v1/sites/{id}/readiness` | GET/PATCH | Opening readiness checklist and gate | M67, P03 |
| `/api/v1/sites/{id}/closure` | POST | Initiate and track closure | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R06 Branch Manager | C R U | **Own site** — facility requests, compliance renewal responsibility, safety inspection, incident reporting, meter readings |
| Branch Operations Lead *(R05 delegate; see note)* | C R U D A | **All sites** — the module's business owner; site register, compliance, leases, work orders, vendors |
| R05 Operations Director | R U A | All — readiness gates, suspension decisions, SLA escalations |
| R01 Chief Executive Officer | R A | All — continue-or-suspend decisions on compliance lapse |
| R03 Chief Financial Officer | R A | All — lease decisions, deposits, closure approval, capital replacement |
| R26 Finance Manager / R27 Finance Officer | R A | Rent schedules, utility anomalies, facility invoice validation, cost reporting |
| R08 Service Centre Agent | C R | Own branch — raise and track facility requests only |
| R09 Workshop Supervisor | C R | Own workshop — raise facility requests, view infrastructure availability |
| R19 Procurement Officer | R U | All — vendor assignment, performance and contract escalation |
| R32 Quality Manager / ISO Coordinator | R U A | All — safety equipment fitness, condition assessment, facility audit |
| R30 HR Manager | R | Occupancy and headcount capacity; incident cases with injury |
| R17 Inventory Manager | R | Site storage capacity and closure stock recovery |
| R15 Logistics Coordinator | R | Parking capacity and site-based vehicle arrangements |
| R33 IT / System Administrator | R U | Comms room, connectivity and CCTV/access configuration reference; no lease or compliance rights |
| R02 Chief Technology Officer | R A | All; approves retention configuration for CCTV |
| R38 Facility Vendor (P05) | R U | Own assigned work orders only — accept, attend, complete with evidence; never cost history, never other sites |
| R38 External Auditor (P11 read-only) | R | Compliance records, safety inspections and condition assessments for the audit period |

> **Role register action.** `05-04` §1 does not contain a "Branch Operations Lead" role,
> although `02-02` names it as the business owner of M04 and M47. It is referenced here as a
> distinct accountability and requires either allocation as a new role ID or explicit mapping to
> an existing role. Recorded as an audit action.

**Field-level restrictions.** `rent_amount`, `deposit_amount`, `total_cost`, `cost_per_sqft`,
`vendor_cost` and `loss_value` are visible only to R01–R05, the Branch Operations Lead, R19,
R26, R27 and R03, consistent with `05-04` §5. Branch managers see their own site's cost, never
another site's. Landlord contact details and lease commercial terms are never exposed on any
external portal. `key_custody` and `alarm_code_custody` are visible only to the branch manager,
the Branch Operations Lead and R32.

**Segregation of duties.**
- The person responsible for a licence renewal may not be the sole approver of the operating-risk
  exception arising from its lapse.
- The person who raises a facility work order may not be its sole verifier where the work order
  value exceeds the configured threshold.
- The person who records a utility reading may not approve the anomaly review.
- Site closure follows the same separation as a write-off: recovery executor and approver are
  distinct, mirroring `05-04` §7.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Estate compliance dashboard** | Branch Operations Lead, Operations Director, CEO, CFO | Real time | Every site's licence status, expiries at 90/60/30 days, open operating-risk exceptions — target 100% current |
| **Lease critical-date calendar** | CFO, Branch Operations Lead | Weekly | Renewal notice deadlines, break options, rent reviews and expiries across the estate, with days remaining |
| Lease commitment schedule | CFO, Finance Manager | Monthly | Forward rent and service-charge commitment by site, period and entity |
| Deposit position | CFO, Finance Manager | Quarterly | Deposits held, aged, adjusted and recoverable, with recovery status at exiting sites |
| **Facility work order SLA** | Branch Operations Lead, Operations Director | Weekly | Requests raised, responded, resolved, breached — target > 90% within SLA |
| Facility vendor scorecard | Procurement, Branch Operations Lead | Quarterly | Response, resolution, first-time fix, repeat visits and cost by vendor — feeds M42 |
| **Infrastructure availability** | Operations Director, Branch Manager | Daily | Critical building-service outages by site, duration, cause and branch operating hours lost |
| Generator and UPS regime | Branch Operations Lead, Operations Director | Monthly | Tests due, completed, missed; run hours; fuel; battery condition |
| **Facility cost per site** | CFO, Branch Operations Lead, Branch Manager | Monthly | Rent, utilities, maintenance, security, cleaning, compliance, depreciation; cost per square foot and per job served |
| Utility consumption and anomalies | Branch Operations Lead, Finance Manager | Monthly | Consumption per site normalised by area, peer comparison, flagged anomalies and disposition |
| Safety equipment status | Quality Manager, HR Director, Branch Manager | Monthly | Equipment fit, due, overdue by site and type; inspection evidence completeness |
| Site condition and capital pipeline | CFO, Branch Operations Lead | Quarterly | Condition assessments, remaining life, replacement recommendations and capital requirement |
| Site incident register | Operations Director, HR Director, Quality Manager, CFO | Monthly | Incidents by type and site, injuries, loss value, insurance status |
| Occupancy and capacity | HR Director, Operations Director, CFO | Quarterly | Seats, benches and waiting capacity against headcount and footfall; over- and under-utilised sites |
| **New site readiness** | Operations Director, CEO, M67 project manager | Per opening | Checklist completion, outstanding mandatory items, target versus actual opening date |
| Site closure status | CFO, Branch Operations Lead | Per closure | Asset recovery, licence surrender, deposit recovery and final settlement |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W7 Target | W9 Target |
|---|---|---|---|---|
| — | **Branch statutory compliance (current)** | manual | **100%** | **100%** |
| — | **Facility maintenance requests closed within SLA** | n/a | **> 90%** | **> 95%** |
| — | Sites with a complete facility record | 0% | 95% | **100%** |
| — | Lease critical dates missed | unknown | **0** | **0** |
| — | Operating-risk exceptions open beyond 30 days | n/a | 0 | **0** |
| — | Critical infrastructure availability (power continuity, HVAC) | unmeasured | 97% | **99%** |
| — | Branch operating hours lost to infrastructure outage | untracked | baselined | **−40% against baseline** |
| — | Preventive maintenance completed on schedule | untracked | 88% | **95%** |
| — | Generator and UPS test regime adherence | untracked | 95% | **100%** |
| — | Safety equipment inspections current | unmeasured | 98% | **100%** |
| — | Utility cost per square foot | untracked | baselined | **−8% against baseline** |
| — | Utility anomalies detected before invoice approval | 0% | 85% | **95%** |
| — | Facility cost attributed to a site and cost centre | partial | **100%** | **100%** |
| — | New site opened within the readiness-gate target date | unmeasured | 80% | **90%** |
| — | Security deposits recovered at site exit | unknown | 85% | **95%** |

> **Register note.** The first two metrics are adopted verbatim from
> `_CATEGORY_OVERVIEW.md` §7 (branch statutory compliance 100% current; facility maintenance
> requests closed within SLA > 90%). M47 has **no KPI-0nn identifiers allocated** in the
> programme KPI register; all fifteen metrics require allocation in `06-02` (not yet issued).
> Recorded as an audit action.
>
> **Wave note.** M47 lands in W7 (Months 27–30), so its second target column is W9 rather than
> W8 — the estate has one full year of operation under the module before the programme closes.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `maintenance` (building-service assets and facility work orders, shared with M45), `project` (fit-out tasks), `mail` activity and chatter | 18% |
| L2 | OCA `contract` (recurring rent and service schedules), `management-system` (ISO documentation spine, shared with M23), `dms` (lease and licence evidence), `partner-contact` (landlord and authority records) | 18% |
| L5 | `cd_site_register`, `cd_lease_admin`, `cd_facility_work_order`, `cd_site_compliance` | 64% |

> Odoo `maintenance` is reused rather than duplicated: M45 and M47 share the equipment and
> maintenance-request substrate, differing in what they attach to (a person versus a site) and
> what controls apply (calibration versus statutory compliance). OCA `contract` gives a
> workable recurring-schedule engine for rent. Nothing in L1–L3 provides a site register, a
> critical-date engine, a licence-dependency model or utility anomaly detection.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-167** also claimed by M50, M67; **CD-168** also claimed by M50; **CD-169** also claimed by M50; **CD-170** also claimed by M50. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-167** | `cd_site_register` — site record, type profiles, zones, status lifecycle, portfolio view and map, occupancy, condition assessment, opening readiness gate and closure execution | Odoo module | 6 PW |
| **CD-168** | `cd_lease_admin` — lease record, **lease abstraction into dated events**, critical-date engine, renewal decision workflow, rent schedule, deposit tracking, **versioned lease data extract to M19/M49**, variation and remeasurement trigger | Odoo module | 5 PW |
| **CD-169** | `cd_facility_work_order` — facility request, triage and SLA, assignment to internal or vendor, completion and verification, cost capture, vendor SLA performance, recurring services, infrastructure asset register, PM plans, outage and availability tracking | Odoo module + vendor-portal surface | 6 PW |
| **CD-170** | `cd_site_compliance` — compliance item register, site-type requirement sets, **licence dependency graph**, expiry escalation, operating-risk exception, renewal workflow, compliance-at-a-past-date evidence, safety equipment register, utility accounts and anomaly detection, security and incident register | Odoo module + auditor-app surface | 3 PW |

> **CD register.** M47 has no allocation in `02-05` §5.2, which predates the module. Four new
> IDs, **CD-167…170**, are claimed from the extension block reserved for modules M31–M67,
> following CD-163…166 claimed by M46. **All CD IDs remain provisional** pending the unified CD
> register required by audit finding M-01 in `02-05`.
>
> **Category F CD block.** CD-075…077 + CD-157…158 M17 · CD-159…162 M45 · CD-163…166 M46 ·
> **CD-167…170 M47** · CD-078…079 + CD-171…173 M48.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M30 Platform Admin | The site must link to an operating unit that already exists |
| M49 Fixed Assets, M19 Financial Accounting | Lease extract and infrastructure capitalisation require a consumer; both live from Wave 5 and Wave 3 |
| M16 Procurement, M52 Accounts Payable | Facility purchase and rent, utility and vendor invoice settlement; live from Wave 3 |
| M24 Documents | Lease and licence evidence with retention |
| M45 Enterprise Assets | The readiness gate and closure recovery reference the branch equipment complement; live from Wave 5 |
| M42 Supplier Relationship | Facility vendor scorecards; live from Wave 4 |
| M60 GRC | Operating-risk exceptions publish into the risk register; live from Wave 6 |
| M67 Project Management | New-branch projects; both land in Wave 7 |
| M59 Health & Safety | Safety equipment regimes and HSE cases; live from Wave 6 |
| M29, M28 | Platform foundation: record rules, authority matrix, event outbox |

**Delivers into:** nothing is blocked by M47's absence, which is why it is P3. **But the
compliance slice is separable and can be pulled forward** independently of the rest of the
module if a licence lapse is discovered before Wave 7 — it depends only on M30, M24 and the
platform foundation, all live from Wave 1 to Wave 3. This is recorded as the module's
contingency position.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Lease and tenancy agreements | 51+ sites | `fix.site.lease`, `fix.site.lease.event` | W7 cutover |
| Trade licences and fire licences | 51+ sites × 2+ items | `fix.site.compliance` | W7, verified against the physical licence |
| Utility accounts and 12 months of bills | 51+ sites × 3–5 utilities | `fix.site.utility.account`, `fix.site.utility.reading` | W7, for baseline establishment |
| Branch infrastructure — generators, UPS, HVAC, CCTV | 1,500–4,000 assets | `fix.site.infrastructure` | W7, by physical survey |
| Safety equipment | Fire extinguishers, kits per site | `fix.site.safety.equipment` | W7, by physical survey |
| Deposits paid | Per lease | `fix.site.deposit` | W7, reconciled with Finance |
| Facility vendor arrangements | Cleaning, security, HVAC contracts | `fix.facility.recurring.service` | W7 |
| Leasehold improvements | From M49 migration | `fix.site.infrastructure` (asset link) | W7, reconciled with Finance |

> **Migration position.** Leases and licences are loaded **from the physical documents, scanned
> and hashed** — not from a summary spreadsheet. A licence loaded without evidence is loaded as
> **expired**, raising an operating-risk exception on day one. This will produce an
> uncomfortable opening compliance figure, and that figure is the truth: the current state is
> unknown, and the purpose of the module is to make it known.
>
> **Infrastructure and safety equipment are established by physical survey at every site**, not
> by list. The survey is the same visit that establishes the M45 branch equipment complement and
> should be scheduled once and used for both — a point of practical coordination between the two
> modules that saves 51 duplicate visits.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every operational site holds a compliance record for each item required by its site type, with scanned, hashed evidence | Full-estate assertion query with zero gaps |
| AC-02 | A trade licence renewal cannot be scheduled or submitted while the site's fire licence is expired | Negative test on the dependency graph |
| AC-03 | Licence expiry raises an operating-risk exception, notifies the CEO, publishes to M60, and requires a dated decision — without automatically suspending the site | Scripted scenario with clock manipulation |
| AC-04 | The estate compliance dashboard is accurate against physical documents at five sampled sites | Physical audit at five branches by the Quality Manager |
| AC-05 | The system produces, for any site on any past date, the licences that were valid on that date | Scripted historical query verified against evidence |
| AC-06 | A lease renewal-notice deadline cannot pass without a recorded decision; it escalates daily to the CFO inside 30 days | Scripted scenario across a full lease cycle |
| AC-07 | The lease data extract to M19 contains every field required for lease accounting, is versioned, and is accepted by Finance | Finance-signed data-contract review for ten leases |
| AC-08 | M47 stores no right-of-use asset, lease liability or discount rate anywhere in its schema | Schema assertion and code review |
| AC-09 | A lease modification raises a remeasurement trigger to M19 within one working day | Scripted scenario with M19 |
| AC-10 | A facility work order cannot close without completion evidence and branch verification | Negative test |
| AC-11 | A safety-critical facility request escalates automatically when unaccepted within the emergency SLA | Scripted scenario |
| AC-12 | Facility maintenance requests close within SLA at > 90% for three consecutive months | Three monthly SLA reports |
| AC-13 | An infrastructure outage records duration, cause and branch operating hours lost, and links affected service orders | Scripted scenario with M01 |
| AC-14 | Generator and UPS test regimes generate work on schedule and escalate a missed test | Scripted scenario |
| AC-15 | A utility invoice breaching the anomaly threshold is held from payment approval in M52 until reviewed, with its comparison basis stored | Scripted scenario with M52 |
| AC-16 | Safety equipment past its inspection or refill date is marked unfit and flagged to M59 | Scripted scenario |
| AC-17 | Facility condition assessment and safety inspection complete offline for a full site visit and synchronise with complete integrity | Offline test at three sites |
| AC-18 | A site cannot reach operational status until every mandatory readiness-gate item is complete and signed off | Negative test on a simulated new site |
| AC-19 | Site closure generates the asset recovery worklist against M45, M15 and M46, and the site cannot close until it is cleared | Scripted closure scenario |
| AC-20 | Facility cost per site reconciles to the general ledger for one full quarter, with 100% of cost attributed to a site and cost centre | Finance-signed reconciliation |
| AC-21 | Licences and leases loaded without scanned evidence are loaded as expired | Migration assertion query |
| AC-22 | All branch-facing screens — facility request, safety inspection, meter reading — are complete in Bengali | Translation coverage report (AS-12) |
| AC-23 | Branch Operations Lead, Operations Director and CFO sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many premises does the Company occupy, on what basis (owned, leased, licensed, shared), and where are the agreements held? | Branch Operations Lead / CFO | W7 minus 6 months |
| Q-02 | What is the complete statutory requirement set per site type and per local authority — trade licence, fire licence, signage, environmental, generator — and do requirements differ between city corporations? | Legal / Branch Operations Lead | W7 design |
| Q-03 | What is the current compliance state of the estate? This is unknown, and the answer determines whether the compliance slice must be pulled forward ahead of Wave 7 | Branch Operations Lead / Operations Director | **As early as possible** |
| Q-04 | Is the "compliance lapse escalates but does not auto-suspend" position accepted by the CEO and Legal, given that operating on an expired licence is unlawful? | CEO / Legal / CFO | W7 design |
| Q-05 | Does the Company apply BFRS 16 lease accounting, and what does Finance require from M47 as the lease data source? Who owns the reasonably-certain assessment on extension options? | CFO / Finance Manager / auditor | W7 design |
| Q-06 | Who is accountable for licence renewals today — the branch, a central administrator, or an agent — and does that change under M47? | Branch Operations Lead / Operations Director | W7 design |
| Q-07 | What facility SLA is committed per request category and site criticality, and is there capacity — internal or contracted — to meet it at 51+ sites? | Branch Operations Lead / Procurement | W7 design |
| Q-08 | Which facility services are contracted centrally and which are arranged locally by each branch? Central contracting is a precondition for meaningful vendor SLA measurement | Procurement Manager / Branch Operations Lead | W7 design |
| Q-09 | What is the CCTV retention period, and does it satisfy both M29 security policy and any local or customer-contract requirement? | CTO / Legal / Quality Manager | W7 build |
| Q-10 | Is the physical survey of infrastructure and safety equipment at 51+ sites approved as a business commitment, and can it be combined with the M45 equipment audit? | Operations Director / Quality Manager | W7 minus 4 months |
| Q-11 | What is the standard branch fit-out specification and its cost, and who owns it — M47, M67 or Operations? | Operations Director / Branch Operations Lead | W7 design |
| Q-12 | Should the compliance slice be pulled forward to an earlier wave independently of the rest of M47? | Operations Director / CEO | **Wave 4 planning** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §1, §2 (M47 definition), §5 (boundary map — M30 owns branch
configuration; fire and safety equipment is M47 inventory and M59 compliance), §7 (category
KPIs), §9 (risk of facilities being bolted on late) ·
`M17_Device_and_Customer_Asset_Registry.md` §3 ·
`M45_Enterprise_Asset_and_Test_Equipment.md` §3, §5 FR-EAM-009 (branch equipment profile) ·
`M46_Fleet_and_Vehicle_Management.md` §3 ·
`M48_IoT_Telemetry_and_Predictive_Maintenance.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md` §3.2 ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md` §3 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §8 (multi-branch model),
§10 (AS-03, AS-08, AS-12, AS-13) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category F ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §2 (`maintenance`, `project`), §3 (OCA), §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1, §5, §7 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §Wave 7

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.2 OOS-5 *(the exclusion
reversed)*, BR-INV-001, BR-BI-002, BR-FIN-001, BR-FIN-015, BR-QMS-001, BR-QMS-004 ·
`1000FiX_Services_Company_Profile.md` §Service Infrastructure, §Future Outlook

**External benchmark**
[SAP Real Estate Management / IWMS](https://www.sap.com/products/financial-management/real-estate-management.html) ·
[What is IWMS software — real estate, facilities, space, lease administration and asset management in one platform](https://www.mrisoftware.com/uk/blog/what-is-iwms-software/) ·
[IWMS complete guide — the five functional modules and the CAFM/CMMS distinction](https://www.accruent.com/resources/knowledge-hub/iwms-complete-guide) ·
[Enterprise IWMS — lease abstraction, critical-date tracking, rent automation and IFRS 16 / ASC 842 output](https://nakisa.com/products/iwms-software/) ·
[IWMS and lease accounting compliance](https://www.mrisoftware.com/au/solutions/extensible-iwms/) ·
[IFRS 16 Leases — single lessee model, right-of-use asset and lease liability](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-16-leases/) ·
[IFRS 16 summary, entries and disclosures](https://finquery.com/blog/ifrs-16-leases-summary-examples-entries-disclosures/) ·
[Multi-site facility management strategy — centralised platform, standard checklists, per-site schedules](https://limble.com/blog/multi-site-facility-management) ·
[Scaling multi-site facility maintenance](https://brandpointservices.com/scaling-smart-how-to-handle-facility-maintenance-for-multi-site-operations/) ·
[Multi-location facility maintenance — shared checklists and vendor SLAs](https://trilliumfacility.com/multi-location-facility-maintenance/) ·
[Facility service level agreements — availability SLAs and outage penalties](https://fexa.io/blog/what-is-a-service-level-agreement-sla/) ·
[UPS and site-uptime consequences of unplanned outages](https://www.abm.com/perspectives/data-center-partners-with-abm-to-implement-ups-solution-and-restore-site-wide-uptime) ·
[Fire licence in Bangladesh — Fire Prevention and Fire Fighting Act 2003, FSCD issuance, annual renewal by bank chalan](https://legalseba.com/bd-licenses/fire-license-in-bangladesh/) ·
[Obtaining a fire licence in Bangladesh](https://fmcibd.com/services-services/licensing/how-to-obtain-fire-license-in-bangladesh) ·
[Trade licence in Bangladesh — registration, renewal and compliance; renewal requires proof of occupancy, TIN and a current fire licence](https://tahmidur.com/trade-license-in-bangladesh/) ·
[Trade licence requirements — refusal or revocation where the fire licence has lapsed](https://juralacuity.com/trade-license-requirements-in-bd/) ·
ISO 9001:2015 clause 7.1.3 — infrastructure

---

*Module M47 · Category F · 1000FiX ERP System v2.0 · CONFIDENTIAL*
