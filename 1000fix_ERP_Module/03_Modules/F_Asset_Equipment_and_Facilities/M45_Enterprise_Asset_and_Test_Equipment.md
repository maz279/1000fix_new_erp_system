---
id: FIX-ERP2-M45
module_id: M45
module_code: EAM
module_name: Enterprise Asset & Test Equipment
category: F — Asset, Equipment & Facilities
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Quality Manager
system_owner: Asset & Facilities Squad
priority: P2
wave: W5
---

# M45 — Enterprise Asset & Test Equipment
### Category F · Code `EAM` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M45 |
| **Module code** | `EAM` |
| **Category** | F — Asset, Equipment & Facilities |
| **Status** | ★ New in v2.1 — created from capability that had no owner in v1.0, and from the calibration and tool-register scope removed from M17 |
| **Priority** | **P2** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | Quality Manager |
| **System owner** | Asset & Facilities Squad |
| **Delivery layers** | L1 Odoo `maintenance` · L2 OCA `maintenance` and `management-system` families · L5 custom custody, calibration and equipment-fitness engines |
| **Custom modules** | `cd_equipment_register`, `cd_tool_custody`, `cd_calibration`, `cd_equipment_maintenance` |
| **Requirement range** | FR-EAM-001 … FR-EAM-046 |
| **Requirement count** | **46** *(measured — supersedes the 26 estimate in `02-02`)* |
| **Effort estimate** | **22 person-weeks** *(measured — supersedes the 14 PW estimate)* |
| **Depends on** | M33 Party Master · M37 Catalogue · M21 Core HR · M29 Identity · M30 Platform Admin · M28 Integration · M49 Fixed Assets · M16 Procurement · M24 Documents |
| **Depended on by** | M31, M02, M01, M06, M23, M09, M49, M52, M59, M66, M47, M48, M25 |

---

## 2. Purpose

M45 is the register of **the things 1000FiX uses to do the work** — the oscilloscopes,
multimeters, hot-air rework stations, soldering irons, ESD mats and wrist straps, torque
drivers, thermal cameras, refrigerant gauges, laptops, phones, scanners, printers and branch
equipment that the Company owns and issues to its people.

It answers three questions the business currently cannot answer at all: *where is our
equipment, who has it, and is it fit to use?*

The third question is the one that matters most. 1000FiX is Bangladesh's only ISO-certified IT
service provider and the authorised warranty partner for 17+ brands. Both of those positions
rest on measurement. When a technician records that a board draws 2.1 A where it should draw
0.4 A, that measurement becomes a diagnosis, the diagnosis becomes a parts order, and the parts
order becomes a warranty claim against a brand. **If the meter that took the measurement was
out of calibration, the whole chain is unevidenced** — and a brand auditor examining a rejected
claim is entitled to ask.

### Why It Exists

Three failures are currently invisible because nothing records them.

**Equipment disappears.** Tools issued to a technician who leaves, tools lent between branches,
tools taken home. With 200–400 technicians across 51+ locations and no custody record, the only
control is that someone notices. Nobody notices.

**Calibration lapses silently.** ISO 9001:2015 clause 7.1.5 requires that monitoring and
measuring resources used to verify conformity are suitable, maintained, and — where measurement
traceability is a requirement — calibrated or verified at specified intervals against traceable
standards, with documented evidence retained. The standard also requires that where equipment
is found to be out of calibration, the organisation **determines whether the validity of
previous measurement results has been adversely affected and takes appropriate action.** Doing
that requires knowing which measurements were taken with which instrument. Without an equipment
register linked to QC records, the question cannot even be asked.

**Capital is spent twice.** A branch that cannot find its thermal camera buys another. The
Company has no view of what it owns, no utilisation data, and no basis for deciding whether the
next purchase is necessary.

M45 is P2 and lands in Wave 5 alongside M23 Quality and M49 Fixed Assets, because calibration
control is only meaningful once the QC records it protects exist.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-QMS-001 | "Maintain ISO 9001:2015 compliance documentation with version control" — clause 7.1.5 requires documented evidence of fitness for purpose of measuring resources |
| ERP BRD BR-QMS-005 | "Enforce quality inspection checklists on service completion before closing work orders" — a QC result is only as good as the instrument that produced it |
| ERP BRD BR-QMS-004 | "Support internal audit management with findings and corrective action tracking" — equipment fitness is a standing audit subject |
| ERP BRD BR-SRM-018 | Level 3 board-level repair — the repair class that depends most heavily on calibrated test equipment |
| ERP BRD BR-FIN-015 | "Track fixed assets and calculate depreciation" — the capital view of the same equipment, owned by M49 |
| ERP BRD BR-HRM-002 | Technician skill matrix with certifications — competence and equipment fitness are the two halves of a valid measurement |
| Company Profile §Quality & Certification | "Only ISO-certified IT service provider in Bangladesh"; documented quality policy; systematic QC process — the certification M45 protects |
| Company Profile §Service Philosophy | "Advanced diagnostic equipment" is a stated capability claim |
| Company Profile §Core Services | Motherboard and server repair, AC and refrigeration work — disciplines requiring calibrated measurement |
| `_CATEGORY_OVERVIEW.md` §3 | "M45 never holds a customer device"; regulatory hook is ISO 9001 clause 7.1.5 |
| `_CATEGORY_OVERVIEW.md` §6 | Calibration is "the control that protects warranty revenue"; calibration compliance is a **Wave 5 gate criterion** |
| `M31` §3.2, §12.3 | M31 declares calibration and test-equipment scope out and assigns it to M45; publishes `equipment.calibration_exception` |
| `M06` §10.2 | M06 references `fix.tool.register` (M45) for specialist data-recovery equipment |
| `M15` §3.2 | M15 declares tools, jigs and calibrated instruments out of scope and assigns them to M45 |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M45 sits between four modules that each hold part of
> the equipment picture — M17 (customer assets), M15 (consumable stock), M49 (capital value)
> and M47 (premises). Both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The enterprise equipment register: every company-owned tool, instrument, IT asset and item of branch equipment |
| 2 | Equipment classification: measuring instrument · general tool · IT asset · branch equipment · specialist equipment · consumable-controlled item |
| 3 | Equipment identity: asset tag, serial, manufacturer, model, purchase reference, warranty and expected life |
| 4 | Issue, custody, transfer and return — the tool-crib lifecycle with named accountability |
| 5 | Personal issue: equipment held permanently by a named employee, reconciled at appraisal and at exit |
| 6 | Kit management: a defined set of equipment issued and returned as one unit |
| 7 | **Calibration management: schedule, due date, execution, certificate, traceability and out-of-service enforcement** |
| 8 | As-found and as-left measurement capture against tolerance limits |
| 9 | Automatic out-of-service marking of any instrument past its calibration due date |
| 10 | Retrospective impact assessment when an instrument is found out of tolerance |
| 11 | Preventive and corrective maintenance of company equipment, including internal repair routed to M31 |
| 12 | Equipment fitness state: the single authoritative answer to "may this instrument be used right now" |
| 13 | Instrument usage capture: which instrument was used on which job, repair or QC record |
| 14 | Physical verification: periodic equipment audits by branch with variance and loss reporting |
| 15 | Loss, damage, theft and write-off workflow with accountability |
| 16 | Equipment requisition, replacement justification and retirement recommendation |
| 17 | Retirement and disposal routing, including data-bearing IT assets to M06 and e-waste to M18 |
| 18 | Equipment cost of ownership: purchase, calibration, maintenance, downtime and replacement |
| 19 | ESD control equipment and its periodic verification |
| 20 | Equipment analytics: utilisation, availability, calibration compliance, cost per branch |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Customer-owned devices under repair** | **M17** Device & Customer Asset Registry | A customer's laptop is received and delivered; a company tool is issued and returned. Different lifecycle, different owner, different regulator |
| **Rental-pool assets rented to customers** | **M13** Rental & EaaS (identity in M17) | A rental laptop earns revenue; a tool enables it |
| **Consumable spare parts and stock** | **M15** Inventory | A part is consumed and disappears; a tool is returned. Solder wire and thermal paste are M15 stock even though a technician carries both |
| **Capitalisation, depreciation, revaluation, disposal accounting** | **M49** Fixed Assets & Capital Investment | M45 sees an operational asset; Finance sees a capital asset. Two views, one physical item, linked by reference |
| **Purchase requisition, RFQ, PO, goods receipt, three-way match** | **M16** Procurement | M45 raises the need and the justification; M16 buys |
| **Calibration-provider selection, contract and scorecard** | **M42** Supplier Relationship & Performance | M45 records who calibrated and to what standard; M42 manages the relationship |
| **Vehicles** | **M46** Fleet & Vehicle Management | Vehicles carry statutory documents, drivers and fuel economics |
| **Buildings, premises, fixed building services (generator, UPS, air conditioning, fire systems)** | **M47** Facility & Workplace | Building services are attached to a site; equipment is issued to a person |
| **The QC checklist, the quality event, the CAPA** | **M23** Quality Management System | M45 supplies instrument fitness; M23 owns the quality process it feeds |
| **Employee competence and certification to use an instrument** | **M22** Learning, Competency & Certification | Competence is a property of the person, fitness a property of the tool. Both are checked; neither owns the other |
| **Health and safety inspection regimes and incident management** | **M59** Health, Safety & Wellbeing | M45 records that safety equipment exists and is verified; M59 owns the HSE process |
| **Internal IT service desk, software licences and endpoint configuration** | **M66** Internal IT Service Management | M45 owns the IT asset as a physical, custodied, retired object; M66 owns the ticket, the licence and the build |
| **Secure erasure and destruction certification of data-bearing media** | **M06** Data Services & Secure Data Handling | An IT asset being retired routes to M06 for erasure; M45 records the certificate reference |
| **E-waste batching, recycler compliance and disposal certification** | **M18** E-Waste & Circular Economy | M45 retires; M18 disposes |
| **Telemetry from connected equipment** | **M48** IoT & Predictive Maintenance | Where equipment emits telemetry, M48 ingests it and returns a condition signal |
| **Repair execution on company equipment** | **M31** Workshop & Depot Repair | M45 raises an internal repair order; M31 performs it, exactly as it would for a customer device |
| **Employee expense reimbursement for tools bought personally** | **M52** Accounts Payable & Employee Expense | A tool bought on expense is registered in M45 once the expense is approved |

### 3.3 Shared Concepts

| Concept | M45's Role | Owning Module |
|---|---|---|
| Company equipment | **Owns** — the defining concept of this module | M45 |
| Calibration record and certificate | **Owns** — the defining control of this module | M45 |
| Fixed-asset record and depreciation | References; supplies acquisition, transfer, impairment and disposal triggers | M49 |
| Equipment model and specification | References the catalogue where the item is a catalogued product | M37 |
| Employee and role | References for custody accountability and exit clearance | M21 |
| Branch and location | References; owns the equipment's location within it | M30 / M47 |
| Internal repair order | Raises; M31 executes | M31 |
| Instrument used on a QC record | Owns the instrument and its fitness; M23 owns the QC record | M45 / M23 |
| Supplier and calibration provider | References; M42 owns the relationship and scorecard | M42 |
| Purchase order and receipt | References; equipment is registered on receipt | M16 |
| Safety equipment at a branch | Owns the register and verification record; M47 owns site placement; M59 owns the HSE regime | M45 / M47 / M59 |
| Condition signal from telemetry | Consumes | M48 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **IBM Maximo Application Suite — Manage & Calibration** | Calibration assets split into **instruments** (the devices that do the work) and **measuring and test equipment / standards** (the devices that measure the instruments); historical calibration measurement records; **as-found and as-left measurements validated against tolerance limits**; calibration work orders executable online and offline on mobile; 21 CFR Part 11 electronic-signature support | **The instrument-versus-standard distinction is the single most influential external reference for M45.** A calibrated instrument is only as good as the standard used to calibrate it, and that standard has its own due date. Also adopted outright: **as-found/as-left capture against tolerance**, because as-found out-of-tolerance is precisely what triggers the retrospective impact assessment ISO 9001 requires; and **offline calibration execution**, because branch connectivity in Bangladesh is not guaranteed | Maximo's regulated-industry apparatus — 21 CFR Part 11 electronic signatures, full life-sciences validation package. 1000FiX is ISO 9001, not FDA-regulated |
| **SAP S/4HANA Asset Management (PM/EAM) — Test Equipment Management** | Test equipment as equipment master with an inspection/calibration order type, usage decision, and a QM link that blocks usage decisions taken with unsuitable equipment | The **QM linkage pattern**: a quality decision records the instrument that produced it, and the system can later be asked what was decided on an instrument that turned out to be unfit | SAP's inspection-lot and usage-decision machinery; disproportionate for 51 branches and a few hundred instruments |
| **Oracle Maintenance Cloud / IFS Cloud Asset Management** | Asset register with meters, PM programmes, work orders and asset hierarchy; IFS adds tool and equipment issue against a work task | PM triggered by **elapsed time or usage counter**, and equipment issued **against a specific job** rather than to a person indefinitely | Full multi-level asset hierarchies and plant maintenance planning boards |
| **Tool-crib management practice (EZOfficeInventory, Fabrico, GoCodes, Xerafy RFID)** | A library model: scan the tool, scan the badge, create a digital chain of custody; check-in/check-out with due dates; custody assigned to a crew or project; overdue alerting; tool tracking by location, project or team | **The library model, adopted wholesale.** Scan tool + scan person = custody. This is the only pattern that survives contact with a busy workshop, and it is the reason M45 will actually be used. Also adopted: overdue-return alerting and custody by job as well as by person | RFID portal hardware at this stage. Barcode and QR at 51 branches is achievable now; RFID is a Wave 8+ option for high-value items only |
| **Calibration-management practice (Gaugify, QIS, GageList)** | Calibration scheduling with automated reminders; calibration history and due dates accessible by scanning the label on the gauge; traceability to ISO/IEC 17025 accredited providers, NIST or national reference standards; audit logs | **Traceability chain recorded as data**: certificate number, accredited provider, reference standard, measurement uncertainty and traceability path. This is what an auditor actually asks to see. Also adopted: scan-the-label-see-the-status, so a technician can check fitness in two seconds at the bench | Full gauge R&R and statistical measurement-system analysis. Valuable, but a later maturity step |
| **ISO 9001:2015 clause 7.1.5** | Measuring resources determined, provided, suitable and maintained; calibrated or verified at specified intervals or before use against traceable standards; identified as to calibration status; safeguarded from adjustments that invalidate status; **retrospective validity assessment when found unfit**; documented evidence retained | **The clause is implemented as software controls, not as a procedure document.** Automatic out-of-service marking, blocked QC entry, and an impact-assessment worklist naming every measurement taken since the last good calibration | Nothing. This clause is the module's reason to exist |
| **ISO/IEC 17025** | Requirements for the competence, impartiality and consistent operation of calibration laboratories; metrological traceability | Used as the **provider qualification standard**: calibration is accepted from an ISO/IEC 17025-accredited laboratory, or the certificate is flagged as non-accredited and the instrument's use is restricted | Becoming an accredited calibration laboratory ourselves |
| **ISO 55001:2024 asset management system** | Requirements for an asset management system: strategic asset management plan, asset management plans with activities, resources, timescales and responsibilities, lifecycle decision-making and risk | The **lifecycle-decision discipline** — acquire, operate, maintain, replace, dispose — applied to equipment as a portfolio rather than item by item, and the principle that replacement is a decision with evidence behind it | Formal ISO 55001 certification and the SAMP apparatus; disproportionate at this asset base |
| **Odoo 19 CE `maintenance` + OCA `maintenance` and `management-system`** | Equipment records, maintenance teams, preventive and corrective maintenance requests, equipment categories, MTBF/MTTR calculation | The transactional substrate for equipment records and maintenance requests, adopted as-is. OCA `management-system` supplies the ISO documentation spine shared with M23 | Odoo `maintenance` has **no calibration model, no custody model and no fitness gate**. All three are built in `cd_calibration` and `cd_tool_custody` |

**Design position.** Four deliberate differences from the benchmark.

First, **fitness is a hard gate, not a report.** Every benchmark system will tell you an
instrument is overdue. M45 marks it **out of service automatically at midnight on the due
date**, and an out-of-service instrument cannot be selected on a QC record or a repair order.
There is no override at any authority level for a measuring instrument used to verify
conformity. This will be inconvenient the first time a branch's only multimeter goes overdue —
which is exactly the pressure that makes the calibration calendar get managed.

Second, **the retrospective question is asked automatically.** When an instrument returns
as-found out of tolerance, M45 generates the list of every QC record and repair decision taken
with that instrument since its last passing calibration, and routes it to M23 as a quality
event. Almost every implementation of clause 7.1.5 leaves this as a manual procedure, which
means it is done once, at audit time, badly. Here it is a query the system already knows how
to answer.

Third, **custody is to a person, always.** Not to a branch, not to a team, not to a store. At
200–400 technicians the only recoverable custody record is one with a name on it. Team custody
is available for kits, but a kit still has a named accountable holder.

Fourth, **the register is deliberately wide, the control deliberately narrow.** M45 registers
everything the Company issues — including a technician's laptop and a branch's label printer —
because a register with holes is a register nobody trusts. But **calibration control applies
only to measuring instruments used to verify conformity.** Applying calibration ceremony to a
screwdriver would discredit the control that protects warranty revenue.

---

## 5. Functional Areas & Features

### 5.1 Equipment Register & Identity

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-001 | Equipment record | Maintain one record per company-owned item of equipment, with a permanent equipment ID, manufacturer, model, serial, acquisition reference, acquisition cost, expected life and home location | **P0** | L1/L5 |
| FR-EAM-002 | Equipment classification | Classify every item as measuring instrument · calibration standard · general tool · IT asset · branch equipment · specialist equipment · safety equipment, with class-specific mandatory attributes and control behaviour | **P0** | L5 |
| FR-EAM-003 | Measurement-critical flag | Mark whether an item is used to verify conformity of a product or service, which determines whether calibration control applies (ISO 9001 clause 7.1.5) | **P0** | L5 |
| FR-EAM-004 | Asset tagging | Generate, print and associate a durable QR or barcode asset tag; resolve any item by scan in ≤ 1 second on a phone or handheld | **P0** | L3/L5 |
| FR-EAM-005 | Fixed-asset linkage | Link every capitalised item to its M49 fixed-asset record, and expose acquisition, transfer, impairment and disposal triggers to Finance without duplicating the depreciation schedule | P1 | L5 |
| FR-EAM-006 | Warranty and supplier | Hold supplier, purchase order, warranty period and service-contract reference for each item, and surface warranty status before an internal repair is authorised | P1 | L5 |
| FR-EAM-007 | Kit definition | Define a kit as a named set of items issued and returned as one unit, with the kit itself carrying a named accountable holder and a completeness check on return | P2 | L5 |
| FR-EAM-008 | Equipment documents | Attach manual, calibration certificate, purchase invoice, warranty document, risk assessment and photographs through M24, with retention policy applied | P1 | L2/L5 |
| FR-EAM-009 | Register completeness | Report equipment recorded against equipment expected per branch profile, and maintain a register-completeness score by branch | P1 | L5 |

### 5.2 Custody, Issue & Return

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-010 | Scan-based issue | Issue an item by scanning the item and the receiving employee's badge or app identity, creating a custody record with issue time, expected return and purpose | **P0** | L5 |
| FR-EAM-011 | Custody states | Maintain custody as one of: in store · issued to person · issued against a job · on loan to another branch · at calibration · under repair · lost · retired | **P0** | L5 |
| FR-EAM-012 | Personal issue | Support permanent personal issue of equipment to a named employee, listed on their record and reconciled at appraisal and at exit clearance | **P0** | L5 |
| FR-EAM-013 | Job-linked issue | Issue an item against a specific service order, repair order or field visit, so that instrument usage is attributable to the work performed | P1 | L5 |
| FR-EAM-014 | Return and condition | Record return by scan with a condition check, routing a damaged item to repair or write-off rather than back to available stock | **P0** | L5 |
| FR-EAM-015 | Overdue custody | Detect items held beyond their expected return, escalate to the holder, then the branch manager, then the Quality Manager, and include them on a standing overdue register | **P0** | L5 |
| FR-EAM-016 | Inter-branch loan | Transfer custody between branches with dispatch and receipt confirmation, retaining accountability with the sending branch until receipt | P1 | L5 |
| FR-EAM-017 | Exit clearance | Block employee exit clearance in M21 while any equipment remains in that employee's custody, and produce the outstanding list | **P0** | L5 |
| FR-EAM-018 | Custody history | Retain a complete, immutable custody chain per item: who held it, when, for what, and in what condition it was returned | **P0** | L5 |

### 5.3 Calibration Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-019 | Calibration profile | Define, per instrument, the calibration interval, the measurement parameters and ranges, the tolerance limits, the required traceability level and the approved provider type | **P0** | L5 |
| FR-EAM-020 | Calibration schedule | Maintain a due date per instrument, generate the calibration schedule, and alert the owning branch at 60, 30, 15 and 7 days before due | **P0** | L5 |
| FR-EAM-021 | Calibration execution | Record a calibration event with provider, certificate number, date performed, date due next, standard used, ambient conditions where relevant, and the technician or laboratory that performed it | **P0** | L5 |
| FR-EAM-022 | As-found / as-left capture | Capture as-found and as-left readings per measurement point against the defined tolerance, and derive pass, adjusted-and-pass or fail automatically | **P0** | L5 |
| FR-EAM-023 | Traceability chain | Record the traceability path — accredited provider, accreditation reference, reference standard used, and that standard's own calibration status — and flag any certificate from a non-accredited source | **P0** | L5 |
| FR-EAM-024 | Certificate retention | Store the calibration certificate against the instrument, retained for the statutory and brand-required period through M24, and retrievable in one action during an audit | **P0** | L2/L5 |
| FR-EAM-025 | Automatic out-of-service | Mark any measurement-critical instrument out of service automatically when its calibration due date passes, with no override at any authority level | **P0** | L5 |
| FR-EAM-026 | Fitness gate | Prevent an out-of-service instrument from being selected on a QC record, a repair order or a diagnostic result, and reject the selection through UI and API alike | **P0** | L5 |
| FR-EAM-027 | Retrospective impact assessment | On an as-found out-of-tolerance result, generate the list of every QC record, diagnosis and warranty claim produced with that instrument since its last passing calibration, and raise a quality event to M23 (ISO 9001 clause 7.1.5) | **P0** | L5 |
| FR-EAM-028 | Standards register | Register calibration standards separately, track their own calibration status, and prevent an instrument from being calibrated against an expired standard | P1 | L5 |
| FR-EAM-029 | Calibration recall | Recall an instrument for calibration by generating the movement, notifying the holder, and marking the instrument unavailable for the duration | P1 | L5 |
| FR-EAM-030 | Interval adjustment | Permit an approved change to a calibration interval, based on documented stability history, recorded with justification and approver | P2 | L5 |
| FR-EAM-031 | Verification-only items | Support items requiring periodic verification rather than formal calibration — ESD wrist straps, mats, torque drivers — with a simpler check record and the same fitness gate | P1 | L5 |

### 5.4 Maintenance, Repair & Availability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-032 | Preventive maintenance | Define preventive maintenance plans per item or category, triggered by elapsed time or usage counter, generating scheduled maintenance requests | P1 | L1/L2 |
| FR-EAM-033 | Corrective maintenance | Raise a fault against an item from any role by scan, capturing symptom and evidence, and route it to internal repair or an external provider | **P0** | L1/L5 |
| FR-EAM-034 | Internal repair routing | Raise an internal repair order in M31 for company equipment, tracked exactly as a customer repair but flagged internal and costed to the owning cost centre | P1 | L5 |
| FR-EAM-035 | Availability state | Maintain a single authoritative availability state per item — available · issued · at calibration · under repair · out of service · retired — that every consuming module reads | **P0** | L5 |
| FR-EAM-036 | Downtime tracking | Record equipment downtime with cause, and report MTBF, MTTR and availability by item, category and branch | P2 | L1/L5 |
| FR-EAM-037 | Critical-equipment cover | Flag items whose absence stops work at a branch, and alert when a branch has no available fit instrument of a required class | P1 | L5 |

### 5.5 Verification, Loss & Retirement

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-038 | Physical verification | Schedule and execute periodic physical equipment audits by branch, counted by scan, blind to the expected list, capturing the counter's identity | **P0** | L5 |
| FR-EAM-039 | Variance and loss | Report items not found at audit, escalate by value, and drive each to a resolution — found, recovered, written off or attributed | **P0** | L5 |
| FR-EAM-040 | Loss and damage accountability | Record loss or damage against a named custodian where custody was held, with an approved recovery or write-off decision within the authority matrix | **P0** | L5 |
| FR-EAM-041 | Write-off control | Require approval within the authority matrix for equipment write-off, with the person who reported the loss barred from approving it | **P0** | L5 |
| FR-EAM-042 | Retirement decision | Support a retirement recommendation based on age, repair cost history, calibration failure history and availability, with an approver and a replacement justification | P2 | L5 |
| FR-EAM-043 | Disposal routing | Route a retired item to secure erasure in M06 where it is data-bearing, to M18 for lawful e-waste disposal, or to resale, and notify M49 for disposal accounting | P1 | L5 |
| FR-EAM-044 | Requisition and justification | Raise an equipment requisition to M16 with a justification built from utilisation, availability and criticality evidence rather than from assertion | P2 | L5 |

### 5.6 Cost, Usage & Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-EAM-045 | Instrument usage record | Record which instrument was used on which QC record, repair or diagnostic result, retained for the life of the associated claim evidence | **P0** | L5 |
| FR-EAM-046 | Cost of ownership | Accumulate acquisition, calibration, maintenance, repair and downtime cost per item and per category, reported by branch and cost centre | P2 | L5 |

> **Cross-cutting.** Calibration compliance, equipment availability, register accuracy and
> cost-of-ownership reporting are delivered as analytics over the register and are specified in
> §14. Telemetry-derived condition on connected equipment arrives from M48 in Wave 8 and is
> consumed by FR-EAM-032 as an additional PM trigger; before that, plans are time- and
> usage-triggered only.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Fitness as a synchronous check** | Instrument fitness is evaluated synchronously at the point of selection in M23, M31 and M01 — never asynchronously and never cached beyond 60 seconds. A stale fitness cache would defeat the entire control |
| T-02 | **Out-of-service is a scheduled state change, not a filter** | The nightly job writes the state; the state is stored. Fitness never depends on the reader computing "is today after the due date", because every consumer would have to implement it identically |
| T-03 | **Immutable calibration records** | A calibration event is insert-only. A correction is a new event referencing the one it supersedes, with a reason. Certificates are stored with a content hash |
| T-04 | **Retrospective query performance** | "Every QC record produced with instrument X since date D" returns in ≤ 2 seconds across three years of QC history; the instrument-usage table is indexed for this query specifically |
| T-05 | **Append-only custody chain** | Custody events are insert-only, carrying item, from-holder, to-holder, timestamp, location, scan evidence and condition |
| T-06 | **Offline calibration and audit execution** | Calibration recording and physical verification operate offline on a phone or handheld and synchronise through an append-only journal with server-side conflict resolution (AS-13) |
| T-07 | **Idempotent scan capture** | Every scan-driven custody or audit command carries a client idempotency key; a replayed scan after a network failure must not double-post a custody transfer |
| T-08 | **Event emission via outbox** | Every equipment state change — issue, return, calibration, out-of-service, loss, retirement — emits a domain event through the transactional outbox (AS-08) |
| T-09 | **Multi-entity and operating-unit isolation** | Every equipment record carries `company_id` and `operating_unit_id`; a branch sees its own equipment and any item on loan to it (AS-03) |
| T-10 | **Tolerance evaluation** | As-found and as-left evaluation against tolerance is computed server-side from stored tolerance definitions, never from a value typed by the person performing the calibration |
| T-11 | **Certificate integrity** | Calibration certificates are stored as PDF/A with a content hash recorded on the calibration event, so a substituted certificate is detectable |
| T-12 | **Scale envelope** | 8,000–15,000 equipment items, of which 800–2,000 are measurement-critical; 40,000 custody events and 4,000 calibration events per year |
| T-13 | **Label durability** | Asset tags are specified for workshop conditions — solvent, heat and abrasion resistant — and encode the equipment ID, not the serial, so a replaced label resolves identically |
| T-14 | **Bengali support** | All equipment, custody and calibration screens used by store keepers and technicians are complete in Bengali (AS-12) |
| T-15 | **Authority matrix enforcement** | Write-off and interval-change approvals are evaluated against the M29 authority matrix at the moment of approval, not at request time |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M45 |
|---|---|---|
| **Technician** | Borrows a meter, returns it or does not; has no way to know if it is calibrated | Scans the tool out and in; sees calibration status on the label in two seconds; cannot unknowingly use an unfit instrument |
| **Workshop supervisor** | Knows roughly what the workshop owns; discovers absences when work stops | Sees the workshop's full inventory, who holds what, and which critical instruments are due for calibration next month |
| **Branch manager** | Signs for equipment they cannot subsequently account for | Holds a branch register that reconciles at audit, with named custody for every item |
| **Quality Manager** | Cannot demonstrate clause 7.1.5 conformance beyond a folder of certificates | Produces calibration compliance on demand, with traceability, and can answer the retrospective-impact question in minutes |
| **Warranty claims officer** | Cannot evidence that the measurement behind a claim was valid | Instrument identity and calibration status attach to the claim evidence automatically |
| **ISO auditor / brand auditor** | Asks for calibration records; receives a partial folder | Asks for any instrument's status and history; receives it, with the standard it was traced to |
| **HR** | Processes an exit with no idea what the leaver holds | Exit clearance blocked until equipment is returned; the list is generated, not remembered |
| **Procurement** | Buys what a branch says it needs | Buys against utilisation, availability and criticality evidence |
| **CFO** | Owns an equipment base of unknown size and condition | Sees equipment count, value, cost of ownership and loss rate, reconciled to the fixed-asset register |

### 7.2 Quantified Business Benefit

M45 is a **protective and cost-avoidance module**. It carries no revenue line in the Scope
Charter §6.2 benefit register, and none is claimed here. Its value is stated as loss avoided
and risk removed, in terms the CFO can test.

| Benefit | Mechanism | Value |
|---|---|---|
| **Protection of 17+ brand authorisations** | Calibration evidence available on demand; measurements behind warranty claims defensible; the retrospective question answerable | The dominant benefit. A single lost brand authorisation would exceed the entire M45 build cost several times over. Protects the **BDT 100 lac/year** warranty recovery attributed to M09 in §6.2 |
| **Protection of ISO 9001 certification** | Clause 7.1.5 implemented as enforced software controls rather than as a procedure nobody follows | ISO status is a stated competitive advantage and a corporate-tender qualifier. Its loss would close the corporate segment |
| **Elimination of unrecorded equipment loss** | Named, scanned custody at every transfer; exit clearance gate; periodic verification | Equipment loss is currently untracked. Target: tools unaccounted for at audit = **0** (`_CATEGORY_OVERVIEW.md` §7) |
| **Avoided duplicate purchasing** | Branches can see what exists before requisitioning; utilisation evidence supports or refuses the request | Direct capital avoidance across 51+ branches; the most common cause of duplicate purchase is not knowing an item already exists |
| **Reduced rework from invalid measurement** | An out-of-tolerance instrument is caught at calibration rather than after a run of misdiagnoses | Supports first-time fix (KPI-004) and reduces the rework rate M23 measures |
| **Reduced equipment downtime** | Preventive maintenance and critical-cover alerting replace repair-when-it-fails | Protects branch throughput; a workshop without a working rework station stops board-level work entirely |
| **Fixed-asset register accuracy** | Physical verification reconciled to M49 | Removes an audit qualification risk on the equipment line of the balance sheet |
| **Insurance and claim defensibility** | Equipment identity, value and custody are evidenced | A theft or fire claim is supportable with a register rather than a recollection |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 clause 7.1.5 conformance by construction** | The control is enforced by the system, so conformance does not depend on whether a branch remembered. This is the difference between passing an audit and being genuinely in control |
| **Measurement credibility** | The Company's technical claims — board-level diagnosis, refrigerant charge, torque specification — become defensible statements rather than assertions |
| **Accountability culture** | Named custody ends "someone borrowed it" as an acceptable answer, in the same way van-stock reconciliation ended it for parts in M15 |
| **Audit readiness as a standing state** | Calibration compliance is a Wave 5 gate criterion; after Wave 5 it is a dashboard, not a project |
| **Safety assurance** | ESD equipment verification, first-aid and safety-equipment registers give M59 and M47 a factual basis for their compliance claims |
| **Foundation for technical maturity** | An equipment register with usage data is the precondition for capability planning — knowing whether the Company can take on a class of work at a given branch |
| **Expansion readiness** | A new branch's equipment complement becomes a defined, costed, checklist-driven fit-out rather than an improvisation (with M47) |

---

## 8. Lifecycle & State Models

### 8.1 Equipment Lifecycle

```
                    ┌──────────────┐
      goods receipt │  REGISTERED  │  tagged, classified, linked to M49
      from M16      └──────┬───────┘
                           │ commissioned; calibration baseline taken
                    ┌──────▼───────┐
        ┌──────────►│  AVAILABLE   │◄──────────┐
        │           └──┬────┬───┬──┘           │
        │ returned     │    │   │              │ returned from
        │              │    │   │              │ calibration, fit
        │        ┌─────▼─┐  │   │        ┌─────┴──────────┐
        └────────┤ISSUED │  │   └───────►│ AT CALIBRATION │
                 │(named │  │            └─────┬──────────┘
                 │holder)│  │                  │ failed as-found
                 └───┬───┘  │                  │
                     │      │ fault raised     │
                     │  ┌───▼──────────┐       │
                     └─►│ UNDER REPAIR │       │
                        └───┬──────┬───┘       │
                            │      │ beyond economic repair
                            │      │           │
                 ┌──────────▼──┐   │    ┌──────▼────────────┐
                 │ OUT OF      │◄──┼────┤ calibration due    │
                 │ SERVICE     │   │    │ date passed        │
                 │ (blocked)   │   │    │ (automatic)        │
                 └──────┬──────┘   │    └────────────────────┘
                        │          │
                        │      ┌───▼────┐
                        │      │  LOST  │──► write-off, accountability
                        │      └────────┘
                 ┌──────▼──────┐
                 │  RETIRED    │──► M06 erasure (if data-bearing)
                 └──────┬──────┘    └──► M18 e-waste  or  resale
                        │
                 ┌──────▼──────┐
                 │  DISPOSED   │──► M49 disposal accounting
                 └─────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Registered | Goods receipt posted in M16, or an approved expense purchase in M52 | Store keeper / branch manager |
| Registered | Available | Tagged, classified, and — for measurement-critical items — a baseline calibration recorded | Quality Manager / store keeper |
| Available | Issued | Scan of item and holder; custody accepted | Store keeper + holder |
| Issued | Available | Returned by scan with a passed condition check | Store keeper |
| Issued | Under repair | Returned damaged, or a fault raised in the field | Any role |
| Available / Issued | At calibration | Calibration recall raised or due date approaching | Quality Manager |
| At calibration | Available | Calibration passed, or adjusted and passed, certificate recorded | Quality Manager |
| At calibration | Out of service | Failed as-found and unfit after adjustment | Quality Manager, automatic |
| Any | Out of service | Calibration due date passed on a measurement-critical instrument | **System, automatic, no override** |
| Under repair | Available | Repair completed, and re-calibrated where measurement-critical | Workshop supervisor + Quality Manager |
| Under repair | Retired | Beyond economic repair, retirement approved | Quality Manager + CFO by value |
| Any | Lost | Not found at audit, or reported lost | Branch manager |
| Lost | Available | Recovered | Branch manager |
| Lost | Retired | Write-off approved within the authority matrix | CFO / Quality Manager by value |
| Any | Retired | Retirement approved with a replacement justification | Quality Manager + Finance |
| Retired | Disposed | Erasure certified (M06) where data-bearing; disposal completed (M18) or resale settled | Quality Manager |

### 8.2 Calibration State

```
   ┌──────────┐  interval elapses,     ┌──────────┐  recalled     ┌──────────────┐
   │ IN        │  alert at 60/30/15/7  │ DUE      │──────────────►│ AT           │
   │ CALIBRATION│─────────────────────►│ SOON     │               │ CALIBRATION  │
   │ (valid)   │                       └────┬─────┘               └──────┬───────┘
   └──────────┘                             │ due date passes            │
        ▲                                   ▼                            │
        │                            ┌──────────────┐                    │
        │                            │ OUT OF       │                    │
        │                            │ CALIBRATION  │                    │
        │                            │ = OUT OF     │                    │
        │                            │   SERVICE    │                    │
        │                            └──────────────┘                    │
        │                                                                │
        │  as-found within tolerance, or adjusted and as-left within      │
        └────────────────────────────────────────────────────────────────┤
                                                                         │
                              as-found OUT OF TOLERANCE                  │
                                       │                                 │
                        ┌──────────────▼──────────────┐                  │
                        │ RETROSPECTIVE IMPACT         │◄─────────────────┘
                        │ ASSESSMENT (automatic)       │
                        │ every QC record, diagnosis   │
                        │ and claim since last pass    │
                        └──────────────┬───────────────┘
                                       │
                        ┌──────────────▼───────────────┐
                        │ QUALITY EVENT → M23 CAPA     │
                        └──────────────────────────────┘
```

| Trigger | Consequence | Owner |
|---|---|---|
| 60 / 30 / 15 / 7 days before due | Escalating alert to branch, then Quality Manager | System |
| Due date passes | Instrument marked out of service automatically; selection blocked everywhere | System — **no override** |
| Calibration passed as-found | New due date set; instrument returns to available | Quality Manager |
| Adjusted, as-left within tolerance | New due date set; adjustment recorded; no retrospective assessment required | Quality Manager |
| As-found out of tolerance | Retrospective impact assessment generated; quality event raised to M23; affected claims flagged to M09 | System, automatic |
| Calibrated against an expired standard | Calibration rejected as invalid; instrument remains out of service | System |
| Certificate from a non-accredited provider | Certificate flagged; instrument use restricted to non-conformity-verification work | System |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-EAM-01 | A measurement-critical instrument past its calibration due date is out of service automatically, with **no override at any authority level** | **H** | Quality Manager |
| BRU-EAM-02 | An out-of-service instrument cannot be selected on a QC record, diagnostic result or repair order through any path — UI, API or import | **H** | Quality Manager |
| BRU-EAM-03 | An as-found out-of-tolerance result automatically generates a retrospective impact assessment covering every measurement recorded since the last passing calibration | **H** | Quality Manager |
| BRU-EAM-04 | An instrument may not be calibrated against a standard that is itself out of calibration | **H** | Quality Manager |
| BRU-EAM-05 | Every calibration event records provider, certificate number, standard used and traceability path; a certificate from a non-accredited provider is flagged and restricts the instrument's use | **H** | Quality Manager |
| BRU-EAM-06 | Calibration certificates are retained for the statutory and brand-required period under the M24 retention policy and may not be deleted | **H** | Quality Manager |
| BRU-EAM-07 | Every item of equipment is in the custody of exactly one named party at any time — a person, or a branch store | **H** | Branch Operations Lead |
| BRU-EAM-08 | Custody transfer requires a scan of the item and identification of the receiving party; unscanned transfers are not recorded | **H** | Branch Operations Lead |
| BRU-EAM-09 | Employee exit clearance in M21 is blocked while equipment remains in that employee's custody | **H** | HR Director |
| BRU-EAM-10 | A damaged item returned to store is routed to repair or write-off; it never returns directly to available | **H** | Workshop Supervisor |
| BRU-EAM-11 | Equipment write-off requires approval within the authority matrix — ≤ BDT 25,000 Quality Manager, above that CFO — mirroring the inventory write-off thresholds in `05-04` §7 | **H** | CFO |
| BRU-EAM-12 | The person who reports an item lost or damaged may not approve its write-off | **H** | CFO |
| BRU-EAM-13 | A calibration interval change requires documented stability history, a justification and an approver | **A** | Quality Manager |
| BRU-EAM-14 | Physical equipment verification is performed at every branch at least annually, and quarterly for measurement-critical instruments | **C** | Quality Manager |
| BRU-EAM-15 | Every QC record and board-level diagnostic result records the instrument used | **H** | Quality Manager |
| BRU-EAM-16 | A retired data-bearing IT asset may not leave the Company's control until M06 has certified erasure | **H** | Quality Manager |
| BRU-EAM-17 | Company equipment is never issued to a customer; a device provided to a customer is a rental asset under M13 with an identity in M17 | **H** | Chief Commercial Officer |
| BRU-EAM-18 | M45 never holds a customer-owned device; a customer device is registered in M17 | **H** | CTO |
| BRU-EAM-19 | A capitalised item's operational record links to exactly one M49 fixed-asset record; M45 never computes depreciation | **H** | CFO |
| BRU-EAM-20 | A branch with no available fit instrument of a class required for the work it performs is flagged as a capability exception to the Operations Director | **C** | Operations Director |
| BRU-EAM-21 | Calibration compliance is a **Wave 5 gate criterion**: the wave does not close below 100% for measurement-critical instruments in scope | **H** | Quality Manager |
| BRU-EAM-22 | An item on loan to another branch remains the accountability of the sending branch until receipt is confirmed | **C** | Branch Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.tool.register` | `fix_tool_register` | The enterprise equipment record | equipment_uid, name, classification, measurement_critical, manufacturer, model_id, serial, asset_tag, acquisition_ref, acquisition_cost, expected_life_months, home_location_id, fixed_asset_id (M49), supplier_party_id, warranty_until, availability_state, criticality, company_id, operating_unit_id |
| `fix.equipment.category` | `fix_equipment_category` | Class behaviour and defaults | code, name, classification, default_calibration_interval, default_pm_plan, mandatory_attributes, requires_verification, requires_calibration |
| `fix.equipment.custody` | `fix_equipment_custody` | Immutable custody event | equipment_id, from_holder_type, from_holder_id, to_holder_type, to_holder_id, issued_at, expected_return_at, returned_at, purpose, job_ref, scan_evidence, condition_on_return, overdue_escalated_at |
| `fix.equipment.kit` | `fix_equipment_kit` | A set issued as one unit | name, branch_id, accountable_employee_id, member_equipment_ids, completeness_checked_at, state |
| `fix.calibration.profile` | `fix_calibration_profile` | What "calibrated" means for this instrument | equipment_id, interval_months, measurement_points, tolerance_definition, required_traceability, approved_provider_types, verification_only |
| `fix.calibration.record` | `fix_calibration_record` | A calibration event | equipment_id, performed_at, next_due_at, provider_party_id, provider_accredited, accreditation_ref, certificate_number, certificate_document_id, certificate_hash, standard_equipment_id, ambient_conditions, result (pass/adjusted/fail), performed_by, supersedes_record_id |
| `fix.calibration.reading` | `fix_calibration_reading` | As-found and as-left per point | calibration_record_id, measurement_point, nominal, tolerance_low, tolerance_high, as_found, as_left, in_tolerance_found, in_tolerance_left, uncertainty |
| `fix.calibration.impact` | `fix_calibration_impact` | Retrospective assessment | calibration_record_id, equipment_id, period_from, period_to, affected_qc_ids, affected_order_ids, affected_claim_ids, assessment_state, quality_event_id, closed_at, disposition |
| `fix.equipment.usage` | `fix_equipment_usage` | Which instrument produced which result | equipment_id, used_at, used_by, source_module, source_doc_type, source_doc_id, calibration_record_id_at_use, fitness_state_at_use |
| `fix.equipment.maintenance` | `fix_equipment_maintenance` | PM and corrective work | equipment_id, type (preventive/corrective), trigger, raised_at, symptom, internal_repair_order_id (M31), external_provider_id, started_at, completed_at, cost, downtime_hours |
| `fix.equipment.pm.plan` | `fix_equipment_pm_plan` | Preventive schedule | scope_type, scope_id, trigger_type (elapsed/usage/condition), interval_value, interval_uom, task_template_id, next_due_at, last_completed_at, active |
| `fix.equipment.audit` | `fix_equipment_audit` | Physical verification run | branch_id, scheduled_for, scope (all/critical), counter_id, approver_id, state, expected_count, found_count, variance_value |
| `fix.equipment.audit.line` | `fix_equipment_audit_line` | One item counted | audit_id, equipment_id, expected_location, found, found_location, found_holder_id, condition, variance_reason |
| `fix.equipment.loss` | `fix_equipment_loss` | Loss, damage and write-off | equipment_id, reported_at, reported_by, custodian_at_loss_id, circumstances, evidence_ids, recovery_attempted, decision (recovered/recharged/written_off), approved_by, value_impact |
| `fix.equipment.retirement` | `fix_equipment_retirement` | Retirement and disposal | equipment_id, recommended_at, basis (age/repair_cost/calibration_failure/obsolete), approved_by, replacement_requisition_id, erasure_certificate_id (M06), disposal_route, ewaste_batch_id (M18), resale_ref, fixed_asset_disposal_notified_at |
| `fix.equipment.cost` | `fix_equipment_cost` | Cost of ownership accumulation | equipment_id, period, acquisition_cost, calibration_cost, maintenance_cost, repair_cost, downtime_hours, cost_centre_id |
| `fix.branch.equipment.profile` | `fix_branch_equipment_profile` | What a branch of a given type should hold | branch_type, required_equipment_categories, minimum_quantities, criticality, effective_from |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.asset`, depreciation schedule | **M17** / **M49** | Read; supply acquisition, transfer, impairment and disposal triggers |
| `fix.employee`, exit clearance checklist | **M21** | Read for custody accountability; write a clearance blocker |
| `fix.party` — supplier, calibration provider | M33 | Read |
| `fix.catalogue.item` — equipment model where catalogued | M37 | Read |
| `fix.purchase.order`, `fix.goods.receipt` | M16 | Read as the registration source |
| `fix.expense.claim` | M52 | Read for expense-purchased equipment |
| `fix.repair.order` | M31 | Create for internal equipment repair; read status |
| `fix.checklist.result`, `fix.quality.event`, `fix.capa` | M23 | Read for impact assessment; create the quality event |
| `fix.brand.claim` | M09 | Read for claims affected by an out-of-tolerance instrument |
| `fix.data.case`, `fix.destruction.certificate` | M06 | Read the erasure certificate on retirement |
| `fix.ewaste.item` | M18 | Read the disposal reference |
| `fix.branch`, `fix.entity`, `fix.cost.center` | M30 / M54 | Read |
| `fix.document`, `fix.retention.class` | M24 | Read/write certificates and manuals |
| `fix.asset.health` | M48 | Read where the equipment is connected |
| `fix.safety.inspection` | M59 | Read/write for safety-equipment verification linkage |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-EAM-01 | Goods receipt posted in M16 against an equipment category | Create the equipment record, generate the asset tag, schedule a baseline calibration where measurement-critical, and notify the receiving branch | Manual registration task |
| AUT-EAM-02 | Calibration due in 60, 30, 15 and 7 days | Alert the holder and the branch, escalating to the Quality Manager at 15 days and the Operations Director at 7 | Alert only; never silently suppressed |
| AUT-EAM-03 | Calibration due date passes, midnight | Mark the instrument out of service, revoke it from every open selection, and notify the holder, the branch and the Quality Manager | Hard block; no failure path |
| AUT-EAM-04 | An out-of-service instrument is selected on a QC record or repair order | Reject the selection with an explanatory message naming the calibration status and the nearest fit alternative | Hard block |
| AUT-EAM-05 | Calibration recorded with an as-found out-of-tolerance reading | Generate the retrospective impact assessment, list affected QC records, orders and claims, raise a quality event to M23 and notify M09 for any affected open claim | Raise the assessment empty and escalate; never skip |
| AUT-EAM-06 | Calibration recorded against a standard that is out of calibration | Reject the calibration as invalid; instrument remains out of service; notify the Quality Manager | Hard block |
| AUT-EAM-07 | Item issued | Create the custody record, set the expected return, and notify the holder of their accountability | Manual custody task |
| AUT-EAM-08 | Expected return date passes | Notify the holder, escalate to the branch manager at +3 days and to the Quality Manager at +7, and add to the standing overdue register | Alert only |
| AUT-EAM-09 | Employee exit initiated in M21 | Generate the outstanding-equipment list and block clearance until it is empty or written off with approval | Hard block on clearance |
| AUT-EAM-10 | Item returned damaged | Route to internal repair in M31 or to write-off assessment; never return to available | Manual routing task |
| AUT-EAM-11 | Preventive maintenance plan falls due | Raise a maintenance request against the item, assign it, and mark the item unavailable for the duration where required | Overdue maintenance exception |
| AUT-EAM-12 | Physical verification schedule due | Generate audit tasks by branch, present the count blind, and assign a counter who is not the branch store keeper | Escalate overdue audits |
| AUT-EAM-13 | Audit line not found | Open a loss record, notify the custodian of record and the branch manager, and start the resolution clock | Item remains open and reportable |
| AUT-EAM-14 | Loss or damage record approved for write-off | Notify M49 for disposal accounting and M52 where a recovery is being recharged to an employee | Queue and retry |
| AUT-EAM-15 | Retirement approved on a data-bearing IT asset | Raise a secure-erasure case in M06 and block disposal until the certificate is returned | Hard block on disposal |
| AUT-EAM-16 | Retirement completed | Route to M18 for e-waste or to resale, notify M49, and close the equipment record | Manual routing task |
| AUT-EAM-17 | A branch has no available fit instrument of a required class | Raise a capability exception to the branch manager and the Operations Director, and propose the nearest available loan source | Alert only |
| AUT-EAM-18 | Nightly | Recompute availability, calibration compliance, register completeness, overdue custody and cost of ownership | Retain previous figures and alert |
| AUT-EAM-19 | M48 publishes a condition signal for connected equipment | Evaluate condition-triggered PM plans and raise maintenance where the threshold is crossed | Retain the time-based plan and alert |

---

## 12. Interfaces

### 12.1 Upstream — M45 Consumes

| Source | What | Mechanism |
|---|---|---|
| M16 Procurement | Purchase order and goods receipt for equipment | Event `goods.received` |
| M52 Accounts Payable & Expense | Approved expense purchases of tools | Event |
| M49 Fixed Assets | Capitalisation confirmation and asset reference | REST |
| M21 Core HR | Employee identity, branch, role, exit initiation | REST + events |
| M33 Party Master / M42 Supplier Relationship | Supplier and calibration-provider identity, accreditation status | REST |
| M37 Catalogue | Equipment model and specification where catalogued | REST |
| M31 Workshop | Internal repair progress and completion | Events |
| M31 Workshop | **Instrument used on a repair, and any attempted use of an unfit instrument** | Event `equipment.calibration_exception` (declared in `M31` §12.3) |
| M23 Quality | QC record creation referencing an instrument | Events |
| M06 Data Services | Secure erasure certificate on retirement | Event |
| M18 E-Waste | Disposal batch confirmation | Event |
| M48 IoT & Predictive | Condition signal for connected equipment | Event |
| M24 Documents | Certificate and manual storage, retention policy | REST |
| M30 / M64 | Branch, entity, cost centre, category governance | REST |

### 12.2 Downstream — M45 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M23 Quality | **Instrument fitness at the moment of QC entry**; out-of-tolerance impact assessments; quality events | REST (synchronous) + events |
| M31 Workshop | Test-equipment identity, calibration status, availability for the bench | REST |
| M01 / M02 | Instrument fitness for diagnostic results recorded in the field | REST |
| M06 Data Services | Specialist recovery-equipment identity and fitness | REST |
| M09 Warranty | Instrument identity and calibration status attached to claim evidence; notification where a claim is affected by an out-of-tolerance finding | REST + events |
| M49 Fixed Assets | Acquisition, transfer, impairment, loss and disposal triggers with operational evidence | Events |
| M52 Accounts Payable | Employee recharge instruction for lost or damaged equipment | Event |
| M21 Core HR | Exit-clearance blocker and outstanding-equipment list | REST |
| M16 Procurement | Equipment requisitions with utilisation and criticality justification | Events |
| M42 Supplier Relationship | Calibration-provider performance: turnaround, first-time pass rate, certificate quality | Events |
| M59 Health & Safety | Safety and ESD equipment register and verification status | REST |
| M47 Facility | Branch equipment complement and gaps for a new or refitted site | REST |
| M66 Internal IT Service Management | IT asset identity, custody and retirement state | REST |
| M25 BI / M62 Data Platform | Equipment, calibration, custody, availability and cost facts | Warehouse extract |
| P03 Admin Portal | Full register, custody, calibration and audit surfaces | REST |
| P02 Technician App | Scan-to-check fitness, issue and return, offline calibration and audit capture | REST + sync |
| P11 Field Auditor App | Physical verification execution | REST + sync |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `equipment.registered` | equipment, classification, branch, acquisition reference, capitalised flag | M49, M16, M25 |
| `equipment.issued` | equipment, holder, purpose, job reference, expected return | M21, M23 |
| `equipment.returned` | equipment, holder, condition, duration held | M21, M25 |
| `equipment.custody_overdue` | equipment, holder, days overdue, escalation level | M21, M23 |
| `equipment.calibration_due` | equipment, due date, branch, days remaining | M23, M31 |
| `equipment.calibration_completed` | equipment, result, certificate, provider, next due | M23, M42, M24 |
| `equipment.out_of_service` | equipment, reason, effective from, affected branch | **M23, M31, M01, M02, M06** |
| `equipment.returned_to_service` | equipment, calibration record, effective from | M23, M31 |
| `equipment.out_of_tolerance` | equipment, as-found readings, period affected | **M23, M09** |
| `equipment.impact_assessment_raised` | equipment, affected QC records, orders and claims | M23, M09 |
| `equipment.maintenance_raised` | equipment, type, symptom, expected downtime | M31, M47 |
| `equipment.lost` | equipment, custodian, circumstances, value | M49, M23, M21 |
| `equipment.written_off` | equipment, approver, value, basis | M49, M52 |
| `equipment.retired` | equipment, basis, disposal route | M49, M06, M18 |
| `equipment.capability_gap` | branch, missing equipment class, work affected | M05, M02, M47 |
| `equipment.audit_completed` | branch, expected, found, variance, value | M49, M23, M25 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-EAM-01 | Accredited calibration laboratories (Bangladesh Standards and Testing Institution and private ISO/IEC 17025 providers) | Bidirectional | Calibration booking, certificate return; file and email exchange in W5, portal or API by exception |
| INT-EAM-02 | Equipment manufacturers' service portals | Outbound | Warranty status and service-part lookup for company equipment |
| INT-EAM-03 | Thermal label printers | Outbound | Durable asset-tag printing |
| INT-EAM-04 | Handheld scanners and Android scan devices | Inbound | Custody, audit and fitness-check capture |
| INT-EAM-05 | Legacy branch equipment lists and purchase records | Inbound, one-time | Migration staging; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/equipment/{id}` | GET | Full equipment record with availability and calibration status | P03, M31, M23 |
| `/api/v1/equipment/{id}/fitness` | GET | **Synchronous fitness answer: may this instrument be used right now, and why** | **M23, M31, M01, M02, M06** |
| `/api/v1/equipment/resolve` | POST | Resolve an asset tag or serial by scan | P02, P03, P11 |
| `/api/v1/equipment` | POST | Register an item | P03 |
| `/api/v1/equipment/{id}/custody` | POST | Issue or return by scan (idempotent) | P02, P03 |
| `/api/v1/equipment/{id}/custody/history` | GET | Full custody chain | P03 |
| `/api/v1/equipment/{id}/calibration` | POST | Record a calibration with readings and certificate | P03, P11 |
| `/api/v1/equipment/{id}/calibration/history` | GET | Calibration history and certificates | P03, M23 |
| `/api/v1/calibration/due` | GET | Calibration schedule by branch and horizon | P03, P06 |
| `/api/v1/calibration/impact/{recordId}` | GET | Retrospective impact assessment result | M23, M09 |
| `/api/v1/equipment/{id}/usage` | POST | Record instrument usage against a QC record or order | M23, M31 |
| `/api/v1/equipment/{id}/maintenance` | POST | Raise preventive or corrective maintenance | P02, P03 |
| `/api/v1/equipment/audits` | POST | Create and submit a physical verification | P11, P03 |
| `/api/v1/equipment/{id}/loss` | POST | Report loss or damage | P03 |
| `/api/v1/equipment/{id}/retirement` | POST | Recommend and approve retirement | P03 |
| `/api/v1/employees/{id}/equipment` | GET | Outstanding equipment held by an employee | M21, P03 |
| `/api/v1/branches/{id}/equipment/gaps` | GET | Branch complement versus profile | M47, P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R32 Quality Manager / ISO Coordinator | C R U D A | **All — owns calibration, fitness, impact assessment and the register standard** |
| R06 Branch Manager | C R U A | Own branch — custody, audit, loss reporting, overdue resolution |
| R09 Workshop Supervisor | C R U | Own workshop — issue, return, fault raising, instrument selection |
| R18 Branch Store Keeper | C R U | Own branch store — issue, return, condition check |
| R10 / R11 / R12 Technician | R U | Own custody only — scan out, scan in, check fitness, raise a fault |
| R05 Operations Director | R A | All — capability exceptions, critical-cover decisions |
| R19 Procurement Officer | R | All — requisition justification and supplier performance |
| R26 Finance Manager | R A | All — write-off and retirement approval within threshold, fixed-asset reconciliation |
| R03 Chief Financial Officer | R A | All — write-off and retirement above threshold |
| R30 HR Manager / R31 HR Officer | R | Exit clearance and employee custody lists only |
| R33 IT / System Administrator | C R U | IT-asset class only, plus configuration; **no calibration rights** |
| R02 Chief Technology Officer | R A | All; approves classification taxonomy and integration configuration |
| R14 Data Services Technician | R | Specialist recovery equipment assigned to their case |
| R38 External Auditor (P11 / read-only) | R | Calibration records, certificates and audit results for the audit period; never cost, never custody detail beyond the record |
| R38 Calibration Provider (P05) | R U | Own calibration jobs and certificate upload only |

**Field-level restrictions.** `acquisition_cost`, `value_impact`, `calibration_cost` and
`cost_of_ownership` are visible only to R01–R05, R06, R17, R19, R26, R27 and R03, consistent
with `05-04` §5. Technicians and store keepers see identity, location, custody and fitness,
never cost. External calibration providers see only the instruments assigned to them and never
any 1000FiX cost or custody history.

**Segregation of duties.**
- The person who reports an item lost or damaged may not approve its write-off (BRU-EAM-12).
- The branch store keeper may not be the counter for their own branch's physical verification —
  mirroring SOD-05 in `05-04` §6.
- The person who performs a calibration may not approve a change to that instrument's
  calibration interval.
- **SOD-07 supported:** the technician who repairs company equipment does not certify it fit;
  re-calibration after repair is performed or accepted by the Quality Manager.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Calibration compliance dashboard** | Quality Manager, Operations Director, CEO | Real time | Instruments in scope, in calibration, due soon, out of service — the **Wave 5 gate metric**, target 100% |
| **Calibration schedule** | Quality Manager, Branch Manager | Weekly | Due in the next 90 days by branch, with recall planning and provider booking status |
| Calibration certificate register | Quality Manager, external auditor | On demand | Every certificate with provider, accreditation, standard and traceability path |
| **Out-of-tolerance impact register** | Quality Manager, Warranty Claims Officer, CEO | On occurrence | Every out-of-tolerance finding, the measurements affected, and the disposition of each |
| Equipment register and completeness | Quality Manager, Branch Manager, CFO | Monthly | Items registered, by class and branch, against the branch equipment profile |
| **Custody and overdue register** | Branch Manager, Quality Manager | Daily | Who holds what, for how long, past expected return, by branch and by person |
| Physical verification results | Quality Manager, CFO, Internal Audit | Per audit | Expected, found, variance, value, and resolution of every discrepancy |
| **Loss, damage and write-off register** | CFO, Quality Manager, Internal Audit | Monthly | Every loss with custodian, circumstances, decision, approver and value |
| Equipment availability and downtime | Operations Director, Branch Manager | Weekly | Availability by branch and class, MTBF, MTTR, downtime cause |
| Critical-cover exceptions | Operations Director, Branch Manager | Daily | Branches without a fit instrument of a required class, and the work affected |
| Cost of ownership | CFO, Procurement, Quality Manager | Quarterly | Acquisition, calibration, maintenance and downtime cost per item, class and branch |
| Calibration-provider performance | Procurement, Quality Manager | Quarterly | Turnaround, first-time pass rate, certificate completeness, price — feeds the M42 scorecard |
| Retirement and replacement pipeline | CFO, Procurement, Operations Director | Quarterly | Items recommended for retirement with basis, and replacement capital requirement |
| Fixed-asset reconciliation | CFO, Finance Manager | Annually | Physical verification reconciled to the M49 register, with the variance explained |
| Employee equipment holdings | HR Manager, Branch Manager | On demand | Outstanding equipment per employee, used at appraisal and at exit |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| — | **Calibration compliance (measurement-critical instruments)** | unmeasured | **100%** | **100%** |
| — | **Tools unaccounted for at audit** | untracked | **0** | **0** |
| — | Tool and equipment inventory accuracy | untracked | 96% | **> 98%** |
| — | Equipment register completeness against branch profile | 0% | 92% | **98%** |
| — | Custody transfers captured by scan | 0% | 90% | **98%** |
| — | Items held beyond expected return | untracked | < 5% | **< 2%** |
| — | Exit clearances with equipment outstanding | untracked | 0 | **0** |
| — | QC records recording the instrument used | 0% | **100%** | **100%** |
| — | Out-of-tolerance impact assessments closed within 10 working days | n/a | 90% | **100%** |
| — | Equipment availability (measurement-critical) | unmeasured | 95% | **98%** |
| — | Calibration provider first-time pass rate | unknown | baselined | **> 92%** |
| — | Physical verification schedule adherence | n/a | 95% | **99%** |
| — | Branch critical-cover exceptions open beyond 5 days | untracked | < 3 | **0** |
| **KPI-004** *(supported)* | First-time fix rate | 72% | 85% | **88%** |
| **KPI-041** *(supported)* | Warranty claims with complete evidence | unmeasured | 95% | **98%** |

> **Register note.** The first three metrics are adopted verbatim from
> `_CATEGORY_OVERVIEW.md` §7 (calibration compliance 100%, tools unaccounted for 0, inventory
> accuracy > 98%). M45 has **no KPI-0nn identifiers allocated** in the programme KPI register;
> all thirteen unnumbered metrics require allocation in `06-02` (not yet issued). Recorded as an
> audit action. KPI-004 and KPI-041 are owned by M02 and M09 and are shown as *supported*.
>
> **Gate criterion.** Calibration compliance at 100% for measurement-critical instruments is a
> **Wave 5 gate criterion** per `_CATEGORY_OVERVIEW.md` §6 and BRU-EAM-21. It is the only
> Category F metric that gates a wave.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `maintenance` — equipment records, categories, maintenance teams, preventive and corrective requests, MTBF/MTTR | 20% |
| L2 | OCA `maintenance` extensions (equipment sequences, request stages), OCA `management-system` (ISO documentation spine, shared with M23), OCA `dms` for certificates | 16% |
| L3 | Free barcode and label-printing modules, shared with M15 | 4% |
| L5 | `cd_equipment_register`, `cd_tool_custody`, `cd_calibration`, `cd_equipment_maintenance` | 60% |

> Odoo `maintenance` provides a genuine equipment and maintenance foundation and is used as
> intended. It provides **no calibration model, no custody model and no fitness gate** — the
> three capabilities that give M45 its purpose — so the custom share is necessarily high. No
> production-grade OCA calibration module exists for v19 at the time of writing; this is
> re-checked at build start, and if one has matured it displaces part of `cd_calibration`.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 4 of 4 identifiers below are claimed by another module: **CD-159** also claimed by M19, M30; **CD-160** also claimed by M19, M64; **CD-161** also claimed by M20, M64; **CD-162** also claimed by M20, M65. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-159** | `cd_equipment_register` — equipment record, classification, measurement-critical flag, tagging, fixed-asset linkage, kits, branch profile and completeness scoring | Odoo module | 5 PW |
| **CD-160** | `cd_tool_custody` — scan-based issue and return, custody states and chain, personal and job-linked issue, overdue escalation, inter-branch loan, exit-clearance gate | Odoo module + technician-app surface | 5 PW |
| **CD-161** | `cd_calibration` — calibration profiles, schedule, execution with as-found/as-left, traceability chain, certificate storage and hashing, **automatic out-of-service**, **fitness gate API**, **retrospective impact assessment**, standards register | Odoo module + service | 8 PW |
| **CD-162** | `cd_equipment_maintenance` — PM plans, corrective routing to M31, availability state, downtime, physical verification, loss and write-off, retirement and disposal routing, cost of ownership | Odoo module + auditor-app surface | 4 PW |

> **CD register.** M45 has no allocation in `02-05` §5.2, which predates the module. Four new
> IDs, **CD-159…162**, are claimed from the extension block reserved for modules M31–M67,
> following CD-157…158 claimed by M17. **All CD IDs remain provisional** pending the unified CD
> register required by audit finding M-01 in `02-05`.
>
> **Category F CD block.** CD-075…077 + CD-157…158 M17 · **CD-159…162 M45** ·
> CD-163…166 M46 · CD-167…170 M47 · CD-078…079 + CD-171…173 M48.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M23 Quality Management System | The fitness gate has nothing to protect until QC records exist. M45 and M23 are delivered together in Wave 5 |
| M21 Core HR | Custody requires an employee identity, and the exit-clearance gate requires the exit process |
| M31 Workshop | Internal equipment repair is routed to M31; available from Wave 2 |
| M49 Fixed Assets | Capitalisation linkage; both land in Wave 5 |
| M16 Procurement | Goods receipt is the primary registration inflow; available from Wave 3 |
| M24 Documents | Certificate storage under a retention policy |
| M29, M30, M28 | Platform foundation: record rules, authority matrix, event outbox |
| M06 Data Services | Erasure certification on retirement of data-bearing IT assets; available from Wave 6 — before then, retirement of data-bearing assets is held |

**Delivers into:** M23 cannot certify a QC result as evidenced without M45. M09's claim evidence
is materially stronger with it. Neither is blocked by its absence, which is why M45 is P2 rather
than P1 — but the Wave 5 gate criterion means it must be complete before the wave closes.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch equipment lists, where they exist | 51+ branches, unstructured, incomplete | `fix.tool.register` | W5 cutover |
| Purchase records for capitalised equipment | From M49 migration and finance records | `fix.tool.register` (fixed-asset link) | W5, reconciled with M49 |
| Existing calibration certificates | Unknown; held in branch folders | `fix.calibration.record` | W5, only where certificate and traceability are verifiable |
| Workshop and specialist equipment | Central workshops and the data-recovery lab | `fix.tool.register` | W5 |
| IT asset list | Held by IT administration | `fix.tool.register` (IT-asset class) | W5, with M66 |

> **Migration position — non-negotiable.** The opening register is established by a **physical
> equipment audit at every branch and workshop at cutover**, not by loading lists. Existing
> lists are 51 unreconciled spreadsheets of unknown accuracy; loading them would make the
> "tools unaccounted for = 0" target unmeasurable from day one, exactly as loading stock
> spreadsheets would have done for M15.
>
> **Calibration migration is stricter still.** A historical calibration is loaded **only where a
> certificate exists and its traceability is verifiable.** Any instrument without such a
> certificate enters the register **out of service** and is calibrated before first use. This
> will place a real cost and a real delay on Wave 5, and it is the only defensible starting
> position: a calibration record that cannot be evidenced is worse than no record, because it
> creates a false assurance that a brand auditor will eventually test.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A measurement-critical instrument is marked out of service automatically at its calibration due date, without human action | Scheduled-job test with clock manipulation across a month boundary |
| AC-02 | An out-of-service instrument cannot be selected on a QC record, repair order or diagnostic result through UI, API or bulk import | Negative test suite covering all three paths in M23, M31 and M01 |
| AC-03 | No role, including CEO, CTO and system administrator, can override the out-of-service state on a measurement-critical instrument | Privilege-escalation negative test |
| AC-04 | An as-found out-of-tolerance calibration automatically produces a complete list of every QC record, order and claim produced with that instrument since its last passing calibration | Scripted scenario with three years of seeded QC history |
| AC-05 | The retrospective impact query returns in ≤ 2 seconds at production history volume | Performance test |
| AC-06 | An instrument cannot be calibrated against a standard that is itself out of calibration | Negative test |
| AC-07 | Every calibration record carries provider, certificate number, standard used and traceability path; a non-accredited certificate is flagged and restricts use | Data assertion plus negative test |
| AC-08 | A calibration certificate is retrievable in one action, with its content hash verifying against the stored file | Audit simulation with the Quality Manager |
| AC-09 | Every item of equipment in production is in the custody of exactly one named party | Full-table assertion query with zero exceptions |
| AC-10 | Custody issue and return complete by scan in ≤ 10 seconds per item on a standard branch device | Timed field test at three branches |
| AC-11 | A replayed custody scan after network failure does not double-post | Idempotency test with induced failure |
| AC-12 | Employee exit clearance is blocked while equipment is outstanding, and the outstanding list is generated automatically | Scripted exit scenario with M21 |
| AC-13 | Calibration recording and physical verification complete offline for a full working day and synchronise with complete integrity | Offline test at two branches over three days |
| AC-14 | A physical verification at a branch produces a variance list, and no discrepancy can be closed without a reason and an approver | Scripted audit at a live branch |
| AC-15 | The person reporting a loss cannot approve its write-off | SoD negative test |
| AC-16 | A retired data-bearing IT asset cannot be disposed of until M06 returns an erasure certificate | Negative test with M06 |
| AC-17 | Calibration compliance for measurement-critical instruments reaches and holds 100% for three consecutive months before the Wave 5 gate | Three monthly compliance reports signed by the Quality Manager |
| AC-18 | The opening register is established by physical audit at every branch and workshop, with signed variance reports | Cutover audit records for all 51+ locations |
| AC-19 | Equipment loaded without a verifiable calibration certificate enters the register out of service | Migration assertion query |
| AC-20 | Physical verification reconciles to the M49 fixed-asset register with every variance explained | Signed reconciliation with Finance |
| AC-21 | All technician, store keeper and branch screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-22 | Quality Manager and Operations Director sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 22 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Does a test-equipment register exist today in any form, or does M45 start from zero? *(Raised as Q-04 in `M31`; owned here.)* | Quality Manager | W5 minus 4 months |
| Q-02 | How many measurement-critical instruments exist across 51+ branches and the central workshops, and what is the annual calibration cost at the required interval? | Quality Manager / CFO | W5 minus 4 months |
| Q-03 | Which ISO/IEC 17025-accredited calibration providers are available in Bangladesh for the instrument classes used, at what turnaround, and is BSTI capacity sufficient? | Quality Manager / Procurement | W5 minus 4 months |
| Q-04 | Which instruments are genuinely used to verify conformity, and which are indicative only? This determines the size of the calibration burden and must be decided by the Quality Manager, not by convenience | Quality Manager | W5 design |
| Q-05 | What calibration interval applies per instrument class — manufacturer recommendation, brand mandate, or a documented internal standard? | Quality Manager | W5 design |
| Q-06 | Is the "no override on out-of-service" rule accepted by the Operations Director, including the case where it stops work at a branch? | Operations Director / Quality Manager / CEO | W5 design |
| Q-07 | What is the branch equipment profile — what should a standard branch, a workshop and a station hold? This is also the M47 new-branch fit-out input | Operations Director / Branch Operations Lead | W5 design |
| Q-08 | Are IT assets (technician laptops, phones, scanners) in M45 scope from Wave 5, or deferred to M66 in Wave 6? | CTO / IT Administrator | W5 design |
| Q-09 | Is equipment loss recharged to employees, and under what policy and labour-law constraint? | HR Director / Legal / CFO | W5 build |
| Q-10 | What is the equipment write-off authority threshold — BDT 25,000 as for inventory, or a separate scale? | CFO | W5 build |
| Q-11 | Who performs physical verification — the branch, an internal audit function, or the P11 field-auditor role? | Quality Manager / Internal Audit | W5 build |
| Q-12 | Are calibration certificates required in physical original form by any brand partner, or is a hashed digital copy sufficient? | Quality Manager / CCO | W5 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §1 (four asset populations), §3 (M17 versus M45), §6 (calibration as
the control that protects warranty revenue), §7 (category KPIs), §9 (risks) ·
`M17_Device_and_Customer_Asset_Registry.md` §3 · `M46_Fleet_and_Vehicle_Management.md` ·
`M47_Facility_Branch_Infrastructure_and_Workplace.md` ·
`M48_IoT_Telemetry_and_Predictive_Maintenance.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md`
§3.2, §6 T-09, §12.3 `equipment.calibration_exception`, §18 Q-04 ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md` §10.2, §12 ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md` §3.2 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-03, AS-08, AS-12, AS-13) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category F ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §2 (`maintenance` module, W5), §5.2 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §5, §6 SOD-05 and SOD-07, §7 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §Wave 5

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-QMS-001, BR-QMS-004,
BR-QMS-005, BR-SRM-018, BR-FIN-015, BR-HRM-002 ·
`1000FiX_Services_Company_Profile.md` §Quality & Certification, §Service Philosophy,
§Competitive Advantages

**External benchmark**
[ISO 9001:2015 clause 7.1.5 — monitoring and measuring resources](https://www.nqa.com/en-gb/resources/blog/may-2020/iso-9001-clause-7-1-5) ·
[Clause 7.1.5 calibration requirements explained](https://www.thecoresolution.com/clause-7-1-5-iso-9001-explained) ·
[Calibration management for ISO 9001:2015 clause 7.1.5](https://www.gaugify.io/blog/calibration-management-for-iso-9001-2015-clause-7-1-5-explained) —
scheduling, reminders, records, tolerance ·
[In-depth calibration requirements of ISO 9001:2015](https://www.wilkshireconsulting.com/single-post/in-depth-calibration-requirements-for-iso-9001-2015) —
action required when results are invalidated by out-of-calibration equipment ·
[IBM Maximo Calibration — instruments versus measuring and test equipment (standards)](https://www.ibm.com/docs/en/masv-and-l/maximo-manage/cd?topic=locations-calibration-assets) ·
[IBM Maximo Calibration overview](https://www.ibm.com/docs/en/mfls/7.6.1?topic=product-overview) ·
[Calibration in Maximo Mobile — as-found/as-left against tolerance, online and offline](https://www.ibm.com/docs/en/SSLPL8_cd/com.ibm.mam.doc/mobile/c_calibration_overview.html) ·
[IBM Maximo Calibration 7.6.1.1 overview](https://info.banetti.com/maximo-calibration/) ·
[ISO/IEC 17025 — competence of testing and calibration laboratories](https://en.wikipedia.org/wiki/ISO/IEC_17025) ·
[ISO/IEC 17025 accreditation and metrological traceability](https://cloudlims.com/what-is-iso-iec-17025-accreditation-key-benefits-the-role-of-an-iso-iec-17025-lims-solution/) ·
[ISO 55001:2024 asset management system requirements](https://www.iso.org/standard/83054.html) ·
[ISO 55001 requirements summary](https://tractian.com/en/glossary/iso-55001) ·
[Tool crib management — importance, process and best practice](https://ezo.io/ezofficeinventory/blog/tool-crib-management/) —
the scan-tool/scan-badge chain of custody ·
[Tool crib management software review](https://www.fabrico.io/blog/best-tool-crib-management-software/) ·
[Tool tracking software — custody, due dates and accountability](https://www.ezofficeinventory.com/industries/tool-tracking-software) ·
[Calibration management and gage tracking practice](https://www.qi-a.com/qiss-qms/calibration-management-software/) ·
[OCA maintenance and management-system repositories](https://odoo-community.org/) ·
Bangladesh Standards and Testing Institution (BSTI) — national calibration and metrology authority

---

*Module M45 · Category F · 1000FiX ERP System v2.0 · CONFIDENTIAL*
