---
id: FIX-ERP2-M41
module_id: M41
module_code: WMS
module_name: Warehouse Management
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Warehouse Manager
system_owner: Supply Chain Squad
priority: P1
wave: W3
---

# M41 — Warehouse Management
### Category E · Code `WMS` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M41 |
| **Module code** | `WMS` |
| **Category** | E — Supply Chain & Inventory |
| **Status** | ★ **New** — split out of M15 after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Warehouse Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo `stock` (storage categories, putaway rules) · L2 OCA barcode and warehouse families · L5 custom directive engine, wave engine and RF application |
| **Custom modules** | `cd_wms_structure`, `cd_wms_inbound`, `cd_wms_outbound`, `cd_wms_rf`, `cd_wms_labour` |
| **Requirement range** | FR-WMS-001 … FR-WMS-041 |
| **Requirement count** | **41** *(measured — supersedes the 34 estimate in `02-02`)* |
| **Effort estimate** | **22 person-weeks** *(measured — supersedes the 20 PW estimate)* |
| **Depends on** | **M15 Inventory** · M37 Catalogue · M16 Procurement · M44 Import · M03 Logistics · M29 Identity · M30 Platform Admin · M28 Integration |
| **Depended on by** | M15, M16, M03, M43, M44, M14, M12, M23, M25 |
| **Deployment scope** | **Opt-in per location.** Central warehouses and large branch stores only — not the 51+ standard branch stockrooms |

---

## 2. Purpose

M41 owns **the floor**. Where M15 knows that 42 units of a part exist at the Dhaka central
warehouse, M41 knows they are in bin `A-04-C-12`, that the fastest route to them passes three
other picks, and that the operative who last touched them is on shift now.

Every tier-one ERP separates the inventory ledger from warehouse execution — SAP splits MM-IM
from EWM, Oracle splits Inventory from WMS, Dynamics splits Inventory from Warehouse
Management. The v2.0 draft merged them into a single M15. At the scale 1000FiX is building
towards — central warehouses feeding 51+ branches and 200–400 vans, with imported consignments
arriving in bulk and parts flowing outward in small, urgent, job-driven quantities — that merge
does not survive contact with reality.

M41 exists so that the warehouse can be run as a warehouse: directed put-away instead of
"wherever it fits", waved picking instead of one-order-at-a-time walking, cross-dock for the
urgent transfer that should never touch a shelf, and counting that happens continuously on the
floor rather than as an annual shutdown.

### Why It Exists

Three specific failures make the case.

**Put-away is undirected.** An imported consignment of 300 lines arrives; the operative places
each item where there is space. The location is remembered, not recorded. Retrieval then
depends on the same person being present. This is why branch and warehouse accuracy sits at
75% and why receipts take days to become findable.

**Picking is serial and unsequenced.** A picker walks the warehouse once per transfer request.
With 51 branches raising transfers and vans replenishing daily, the same aisle is walked
dozens of times a day. Wave and cluster picking collapse that into one pass.

**Counting is an event, not a rhythm.** A full count requires closing the warehouse. Because
it is expensive it happens rarely, so errors compound for months before they are discovered.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §3 | The explicit architectural decision to separate the inventory ledger (M15) from warehouse execution (M41), with SAP EWM, Oracle WMS and Dynamics Warehouse Management named as the analogues |
| ERP BRD BR-INV-001 | "51+ service center locations plus central warehouse(s)" — the central warehouse is where M41 applies |
| ERP BRD BR-INV-004 | "Barcode and QR code scanning for all stock movements" — the RF execution layer |
| ERP BRD BR-INV-012 | "Goods receipt with quality inspection step before stocking" — the inbound quality gate M41 executes |
| ERP BRD BR-INV-013 | "Cycle counting with variance reporting" — executed on the floor by M41, recorded in the ledger by M15 |
| Business Objective BO-03 | Inventory accuracy 75% → 98%+; accuracy is achieved on the floor, not in the ledger |
| Company Profile §Service Infrastructure | An expanding branch network (1000FiX Station) implies growing central fulfilment volume |
| Exec Summary §6.2 | Inventory cost reduction BDT 34 lac/year depends on throughput and accuracy that M41 delivers |

---

## 3. Scope Boundary

> **The M15/M41 boundary is the most important one in Category E.** The rule is short:
> **M15 is the ledger; M41 is the floor.** M41 never invents a quantity and never changes an
> ownership class. It executes physical work against balances M15 owns, and confirms what
> actually happened.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Warehouse physical structure: zones, aisles, racks, levels, bins, staging areas, docks |
| 2 | Bin master with capacity, dimensions, weight limits, storage category and ownership-class restriction |
| 3 | Slotting: assigning parts to bin classes by velocity, size, weight and pick frequency, with periodic re-slotting |
| 4 | Inbound: dock appointment, unloading, receiving by scan against PO or import consignment |
| 5 | Inbound quality inspection execution: sampling, hold, pass, reject, and release to available |
| 6 | **Directed put-away** by rule: fixed bin, nearest empty, addition to existing, bulk, near-pick-face |
| 7 | Cross-dock: routing an inbound line directly to an outbound stage without put-away |
| 8 | Outbound demand consolidation into **waves**, with wave templates by branch run, van replenishment and urgency |
| 9 | Pick strategy execution: discrete, batch, zone, cluster and pick-and-pass |
| 10 | Pick path sequencing to minimise travel |
| 11 | Pick confirmation by scan, with short-pick, substitution and exception handling |
| 12 | Packing, cartonisation, licence-plate (handling unit) creation and labelling |
| 13 | Staging, dock assignment, load confirmation and handover to M03 |
| 14 | Internal replenishment: bulk-to-pick-face movement triggered by pick-face minimums |
| 15 | Floor-level counting: cycle counts by bin and zone, zero-crossing counts, and count-back after variance |
| 16 | Task management: task generation, queue, priority, assignment and interleaving |
| 17 | Labour management: operative productivity, task time standards, workload balancing |
| 18 | Material-handling equipment assignment and constraints (trolley, ladder, pallet truck) |
| 19 | The **RF mobile execution application** — the operative's entire working surface |
| 20 | Returns and reverse-flow processing on the floor: inbound returns, quarantine placement, RTV staging |
| 21 | Warehouse layout configuration, and enabling or disabling M41 per location |
| 22 | Warehouse throughput, accuracy and labour analytics |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Quantity on hand, available and reserved | **M15** | One ledger. M41 confirms movements; M15 records balances |
| Ownership class and its use permissions | **M15** | M41 must *respect* the class (bin restriction) but can never assign or change it |
| Inventory valuation and cost | **M15** (calculation), **M19** (posting) | Value never enters the floor |
| Reservation and allocation to a job | **M15** | Allocation is a demand decision, not a floor decision |
| Part definition, dimensions, weight, hazard class | **M37** Catalogue | Slotting *uses* physical attributes; it does not own them |
| Reorder point, safety stock, how much to hold | **M43** Demand Planning | The warehouse stores what planning decides to hold |
| Purchase order and supplier | **M16** / **M42** | The PO is the receipt's authority, not M41's object |
| Import documentation and customs clearance | **M44** | M41 receives what M44 has cleared |
| Transport between sites, custody, proof of delivery | **M03** Logistics | M41's responsibility ends at the dock |
| Vehicle loading beyond the dock, route and rider | **M03** / **M46** | — |
| Van stock par levels and reconciliation | **M15** | The van is a stock location, not a warehouse |
| Branch stockroom operations at standard branches | **M15** + **M04** | M41 is deliberately not deployed there |
| Quality standard, inspection plan and NCR | **M23** QMS | M41 *executes* the inspection; M23 defines it and owns the non-conformance |
| Workshop bench stock and WIP staging | **M31** Workshop | The workshop floor is not the warehouse floor |
| Tool and test-equipment issue | **M45** | Tools are issued and returned, not picked and consumed |
| Facility fabric, racking purchase, safety of the building | **M47** Facility | M41 models the layout; M47 owns the premises |
| Warehouse staff employment, roster and pay | **M21** / **M55** / **M56** | M41 measures productivity; HR owns the person |

### 3.3 Shared Concepts

| Concept | M41's Role | Owning Module |
|---|---|---|
| Stock location | Subdivides an M15 WMS-enabled location into zones and bins | M15 (location) / M41 (bin) |
| Stock quantity | Reads; confirms movement; never authors | M15 |
| Ownership class | Reads and enforces bin segregation | M15 |
| Stock status (inspection / unrestricted / blocked) | Executes the transition physically; M15 records it | M15 / M41 |
| Goods receipt | Executes the physical receipt against M16's PO | M16 / M41 |
| Inspection | Executes sampling and result capture against M23's plan | M23 / M41 |
| Transfer | Picks, packs and stages what M15 requested and M03 will move | M15 / M41 / M03 |
| Handling unit / licence plate | **Owns** | M41 |
| Warehouse operative | Reads identity and shift from M21/M55; owns task assignment and productivity | M21 / M41 |
| Cycle count | Executes on the floor; M15 owns the count record and the adjustment | M15 / M41 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP Extended Warehouse Management (EWM)** | Storage types and sections, nine put-away strategies (manual, fixed bin, general storage, addition to existing stock, empty bin, bulk, pallet, near fixed pick bin, flexible), wave management, handling units, RF framework, annual/continuous/zero-crossing counting | **The put-away strategy set and the wave concept are the primary references for M41.** Adopted: fixed-bin and near-pick-face strategies for fast movers, addition-to-existing for consolidation, empty-bin for new lines; wave grouping of outbound demand for parallel zone execution; handling units as licence plates; the three counting modes | EWM's storage-type/section/bin-type configuration depth, warehouse-order-creation rule complexity, and the resource/queue management layer. We implement one warehouse process type per flow, not a configurable matrix |
| **Microsoft Dynamics 365 Supply Chain — Warehouse Management** | Work templates, location directives, wave templates, work pools, cluster picking, licence plates, the Warehouse Management mobile app | **Work templates + location directives is the cleanest expression of directed work we found, and M41 adopts the pattern directly**: a *directive* answers "which bin", a *template* answers "which steps, in what order". Cluster picking (one operative, several destinations, one pass) is adopted as the primary strategy for branch-transfer waves | The full work-template configuration surface exposed to end users; ours is administrator-configured with a fixed step vocabulary |
| **Oracle Fusion Cloud — Warehouse Management** | Rule-based put-away and picking, task management, cartonisation, LPN | Task interleaving (assigning a put-away on the return leg of a pick) and cartonisation for branch transfers | Oracle's yard and appointment depth |
| **IFS Cloud — Warehouse Management** | Zone-based execution for service-parts warehouses | The service-parts emphasis: many lines, tiny quantities, high urgency — which shapes our wave templates | — |
| **RF/mobile barcoding practice (2025)** | Scan-verified execution at every step; the scanner is the system of record for the floor | **Scan-verified everything.** No keyboard entry of a bin, part or quantity where a scan is possible. This is the difference between 95% and 99.5% pick accuracy | Voice picking and pick-to-light — capital cost is not justified at current throughput; the model does not preclude them |
| **Odoo 19 CE `stock` + OCA `stock-logistics-barcode` / `stock-logistics-warehouse`** | Storage categories, putaway rules, multi-step receipt and delivery routes, barcode app, location zones, inventory lockdown | The transactional substrate and the barcode surface. OCA `stock_location_zone` and `stock_location_position` (coordinate attributes on locations) underpin the bin model | Odoo's putaway rules alone are too shallow for directed put-away across ownership classes and capacity constraints; extended in `cd_wms_inbound` |

**Design position.** Three deliberate differences.

First, **M41 is opt-in per location, and that is the whole point of splitting it out**. Tier-one
suites assume warehouse execution is the default and the exception is a simple site. We invert
it: fifty-one branch stockrooms holding a few hundred lines run on M15 alone, with no bins, no
waves and no directive engine. Imposing warehouse ceremony on a two-shelf stockroom is the
reliable way to produce a system that branches route around. M41 turns on where volume
justifies it and nowhere else.

Second, **the RF application is a single, narrow, offline-tolerant surface, not a menu of
transactions**. A warehouse operative in Bangladesh will be handed an Android device, will work
in Bengali, and will do one of six things at any moment. The app presents the next task, not a
transaction menu. This is a deliberate rejection of the classic RF "green screen" model, which
optimises for configurability at the cost of training time and error rate.

Third, **ownership class is a hard bin constraint, not a report**. This is the one place M41
diverges from every benchmark. Because 1000FiX holds brand consignment stock alongside its own,
a put-away directive that would place own commercial stock into a consignment bin is rejected
at the scanner. Physical segregation is enforced by the directive engine, not by signage and
good intentions.

---

## 5. Functional Areas & Features

### 5.1 Warehouse Structure & Slotting

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WMS-001 | Warehouse structure | Model a WMS-enabled location as zones → aisles → racks → levels → bins, plus staging, dock, quarantine and returns areas | **P0** | L1/L5 |
| FR-WMS-002 | Bin master | Hold per bin: capacity by volume and weight, dimensions, storage category, permitted ownership classes, pick-face flag, coordinates for sequencing, and active status | **P0** | L5 |
| FR-WMS-003 | Location enablement | Enable or disable warehouse execution per M15 stock location, so that standard branches remain ledger-only | **P0** | L5 |
| FR-WMS-004 | Storage categories | Classify parts and bins by storage requirement — small-bin, shelf, bulk, secure cage, temperature-sensitive, hazardous (battery) | P1 | L1 |
| FR-WMS-005 | Slotting assignment | Assign each part a home bin class by velocity, size, weight and pick frequency, keeping fast movers near the pick face | P1 | L5 |
| FR-WMS-006 | Re-slotting | Propose and execute periodic re-slotting as velocity changes, generating internal move tasks | P2 | L5 |
| FR-WMS-007 | Layout visualisation | Present a navigable map of the warehouse showing occupancy, ownership-class zones and congestion | P2 | L5 |

### 5.2 Inbound — Receiving, Inspection & Put-Away

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WMS-008 | Dock and appointment | Schedule inbound deliveries against dock slots and record arrival, start and completion of unloading | P2 | L5 |
| FR-WMS-009 | Receiving by scan | Receive against a purchase order (M16) or an import consignment (M44) by scanning part and quantity, flagging over-, under- and unexpected receipts | **P0** | L2/L5 |
| FR-WMS-010 | Handling unit creation | Create a licence-plated handling unit at receipt, so a pallet or carton can be moved, stored and traced as one object containing many lines | P1 | L5 |
| FR-WMS-011 | Inspection execution | Execute the inbound inspection plan defined by M23: sample size, checks, evidence capture, and pass/reject per line (BR-INV-012) | **P0** | L5 |
| FR-WMS-012 | Inspection hold | Hold received stock in an inspection area, physically and logically separate from available stock, until the result is recorded | **P0** | L5 |
| FR-WMS-013 | **Directed put-away** | Generate a put-away directive per received line using a configured strategy sequence: fixed bin → addition to existing stock → near fixed pick face → nearest empty bin → bulk, subject to capacity, storage category and **ownership-class permission** | **P0** | L5 |
| FR-WMS-014 | Put-away confirmation | Require scan of the bin and the item at put-away, and reject a scan that violates the directive without a recorded override reason | **P0** | L5 |
| FR-WMS-015 | Put-away exception | Handle full-bin, blocked-bin and damaged-item exceptions by re-directing to the next eligible bin and recording the cause | P1 | L5 |
| FR-WMS-016 | Cross-dock | Route an inbound line whose demand is already waiting directly to an outbound staging area, bypassing put-away, and record it as a cross-dock movement | P1 | L5 |
| FR-WMS-017 | Return receiving | Receive inbound returns — branch returns, RTV rejects, customer-supplied parts, harvested components — into the returns area with a disposition decision | P1 | L5 |

### 5.3 Outbound — Wave, Pick, Pack & Dispatch

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WMS-018 | Outbound demand queue | Receive and queue outbound demand from M15 transfers, van replenishments, RTV dispatches and refurbishment issues, with priority and cut-off time | **P0** | L5 |
| FR-WMS-019 | Wave templates | Define wave templates by purpose — scheduled branch run, urgent job-driven, van replenishment, RTV consolidation — each with its own release rule, cut-off and pick strategy | P1 | L5 |
| FR-WMS-020 | Wave release | Group outbound demand into a wave, check stock availability with M15, allocate, and release picking work in one action | **P0** | L5 |
| FR-WMS-021 | Pick strategies | Support discrete, batch, zone, **cluster** and pick-and-pass picking, selected by wave template | P1 | L5 |
| FR-WMS-022 | Pick path sequencing | Sequence pick tasks by bin coordinates to minimise operative travel within a zone and across zones | P1 | L5 |
| FR-WMS-023 | Pick confirmation | Confirm each pick by scanning bin, part and — where serial-controlled — serial, with quantity verification | **P0** | L2/L5 |
| FR-WMS-024 | Short pick | Handle a short pick by recording the shortfall, triggering a count-back of the bin, re-sourcing from an alternate bin, and notifying M15 | **P0** | L5 |
| FR-WMS-025 | Packing and cartonisation | Pack picked lines into cartons or handling units, propose carton size from part dimensions, and generate content-labelled packing documentation | P1 | L5 |
| FR-WMS-026 | Staging and load | Stage packed units by destination, confirm the load, and hand over to M03 with a manifest reference | **P0** | L5 |
| FR-WMS-027 | Dispatch confirmation | Confirm dispatch, close the outbound work, and emit the movement confirmation that lets M15 move stock into transit | **P0** | L5 |

### 5.4 Internal Movement, Replenishment & Counting

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WMS-028 | Pick-face replenishment | Monitor pick-face bin minimums and generate bulk-to-pick-face replenishment tasks before a pick fails | P1 | L5 |
| FR-WMS-029 | Internal move | Execute an ad-hoc bin-to-bin move by scan, with reason code and directive validation | P1 | L5 |
| FR-WMS-030 | Consolidation | Identify a part split across multiple bins and propose consolidation into one, respecting ownership-class segregation | P2 | L5 |
| FR-WMS-031 | Floor cycle counting | Generate and execute counts by bin, zone or ABC class, blind, on the RF device, and submit results to M15 for variance and adjustment (BR-INV-013) | **P0** | L5 |
| FR-WMS-032 | Zero-crossing count | Trigger an automatic count of a bin the moment a pick drives it to zero, as a low-cost continuous accuracy check | P1 | L5 |
| FR-WMS-033 | Count-back on exception | Trigger an immediate bin count after any short pick or put-away exception | P1 | L5 |
| FR-WMS-034 | Bin blocking | Block a bin from picking and put-away pending investigation, with an audit record | P1 | L5 |

### 5.5 Task, Labour & RF Execution

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WMS-035 | Task generation and queue | Generate every physical action as a task with type, priority, zone, equipment requirement and time standard, held in a queue | **P0** | L5 |
| FR-WMS-036 | Task assignment | Assign the next task to an operative by zone, skill, equipment and priority — push-based by default, with a pull option | **P0** | L5 |
| FR-WMS-037 | Task interleaving | Offer a put-away or replenishment task on an operative's return leg from a pick, to reduce empty travel | P2 | L5 |
| FR-WMS-038 | **RF mobile application** | Provide the operative's complete working surface on an Android handheld: next task, scan-verified execution, exception capture, Bengali-first, tolerant of intermittent Wi-Fi | **P0** | L5 |
| FR-WMS-039 | Equipment constraints | Record material-handling equipment and prevent assignment of a task requiring equipment the operative does not hold | P2 | L5 |
| FR-WMS-040 | Labour productivity | Measure tasks and lines per operative-hour against time standards, by task type and zone | P1 | L5 |
| FR-WMS-041 | Workload and congestion | Present live workload by zone and rebalance assignment to relieve congestion | P2 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Directive engine determinism** | Given the same bin state and part attributes, a put-away directive is reproducible. Every directive stores the strategy that produced it and the bins it rejected, so an operative's "why here?" can be answered |
| T-02 | **Ownership-class bin constraint** | The directive engine and the scan validator both enforce the permitted-ownership-class set on a bin. A violating scan is rejected at the device, not corrected afterwards |
| T-03 | **M15 is authoritative** | M41 never writes a quantity to `fix.stock.quant` directly. It confirms physical work, and M15 posts the ledger consequence. A discrepancy between floor and ledger always resolves in favour of a count, never a silent overwrite |
| T-04 | **Task atomicity** | A task is assigned to exactly one operative at a time; assignment uses optimistic locking so two devices cannot claim the same pick |
| T-05 | **RF latency budget** | Scan-to-next-instruction ≤ 500 ms at p95 over warehouse Wi-Fi; the app remains usable at 2 s and degrades to queued mode beyond that |
| T-06 | **Intermittent-connectivity tolerance** | The RF app holds the current task and the next three, queues confirmations in an append-only journal, and replays them idempotently on reconnection (AS-13) |
| T-07 | **Idempotent confirmation** | Every task confirmation carries an idempotency key; replay after a dropped connection must not double-move stock |
| T-08 | **Wave allocation atomicity** | Wave release allocates all lines in one transaction against M15; partial allocation either short-releases explicitly or rolls back — never silently |
| T-09 | **Bin coordinate model** | Bins carry an (aisle, bay, level, position) coordinate that supports serpentine and zone-sequenced path generation without a full routing engine |
| T-10 | **Barcode standards** | Bins, handling units and tasks carry Code-128 and QR labels; part identification accepts supplier barcodes, GS1 identifiers where present, and internal codes |
| T-11 | **Handling-unit nesting** | A handling unit may contain items or other handling units to one level of nesting; content is resolvable to individual parts and serials |
| T-12 | **Event emission** | Every receipt, put-away, pick, pack, count and dispatch confirmation emits through the transactional outbox (AS-08) |
| T-13 | **Multi-warehouse isolation** | All records carry `company_id` and `operating_unit_id`; an operative at one warehouse cannot see or execute another's tasks (AS-03) |
| T-14 | **Scale envelope** | Designed for up to 6 WMS-enabled locations, ~20,000 bins, ~4,000 outbound lines and ~2,500 inbound lines per day at Wave 8 |
| T-15 | **Device management** | RF devices are enrolled, named to a warehouse, remotely deactivatable, and a lost device grants no data at rest |
| T-16 | **Bengali-first rendering** | The RF app renders Bengali part descriptions and instructions correctly on low-cost Android devices, including in the constrained space of a scanner screen (AS-12) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M41 |
|---|---|---|
| **Warehouse operative** | Finds space, remembers where; walks the warehouse once per request; keys nothing into a system | Told exactly which bin, confirms by scan; picks several destinations in one pass; the device is the job |
| **Warehouse manager** | Cannot see work in progress; discovers a backlog when a branch complains | Live task queue, workload by zone, throughput and accuracy by operative |
| **Branch store keeper** | Raises a transfer and waits without visibility | Sees the transfer picked, packed, staged and dispatched, with expected arrival |
| **Inventory manager** | Accuracy is a monthly discovery | Zero-crossing and count-back make accuracy continuous; variance is caught at the bin, hours after it occurs |
| **Procurement / import** | An arriving consignment disappears into the warehouse for days | Receipt, inspection and put-away are tracked with cycle times; urgent lines cross-dock straight out |
| **Quality manager** | Inspection is a signature on paper | Inspection executed on the device with evidence, sample size enforced, results attributable |
| **Technician (indirectly)** | Waits because the part is "in the warehouse somewhere" | The part is findable, and urgent demand cross-docks rather than queuing behind put-away |
| **Finance / audit** | Warehouse stock is trusted least of all | Bin-level, scan-evidenced, continuously counted |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Pick accuracy** | Scan-verified pick with bin, part and serial confirmation | **> 99.5%** — each error avoided is a wrong part sent to a branch, a failed job, a return movement and a lost day |
| **Labour productivity** | Wave, cluster and zone picking with path sequencing and task interleaving | **Lines picked per hour +35%** against the pre-M41 baseline; at 15–30 warehouse operatives this is the equivalent of 5–10 additional heads without hiring |
| **Put-away cycle time** | Directed put-away with immediate bin recording | **< 2 hours from receipt** to findable and available, against days today. This directly shortens the parts-wait component of TAT (KPI-002) |
| **Inventory accuracy contribution** | Continuous zero-crossing and count-back counting on the floor | The mechanism by which BO-03 (75% → 98%+) is actually achieved at the warehouses; M15 records it, M41 produces it |
| **Cross-dock savings** | Urgent lines never touch a shelf | Removes a full put-away/pick cycle for the most time-critical demand — the lines where delay costs most |
| **Space utilisation** | Slotting, consolidation and capacity-aware directives | Defers the capital cost of additional warehouse space as volume grows |
| **Reduced search time** | Nothing is "somewhere" | The single largest recoverable time loss in an undirected warehouse |
| **Consignment integrity on the floor** | Ownership-class bin constraint enforced at the scanner | Removes the physical mixing that makes consignment misuse possible in the first place (supports BRU-INV-01) |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 evidence** | Directed, scan-evidenced execution with attributable inspection is exactly what a process audit asks to see |
| **Brand partner confidence** | Brands auditing an authorised partner's warehouse expect physical segregation of their consignment stock. A bin-level constraint is a demonstrable control, not a claim |
| **Training time collapse** | A new operative follows the device rather than learning the warehouse. Onboarding falls from weeks to a day, which matters in a growing network with staff turnover |
| **Key-person risk removed** | The warehouse no longer depends on the person who remembers where things are |
| **Safety** | Equipment constraints, weight limits and hazardous-storage categories (lithium batteries are a real and growing part of the estate) are enforced rather than advisory |
| **Scalability of the network** | 1000FiX Station expansion multiplies branch demand on central fulfilment. Without M41, central warehouse throughput becomes the constraint on branch growth |
| **Foundation for automation** | A bin-and-task model is the precondition for any future pick-to-light, voice or robotics investment. Nothing in the design forecloses it |

---

## 8. Lifecycle & State Models

### 8.1 Inbound Line Lifecycle

```
   PO (M16) / Import consignment (M44)
              │
        ┌─────▼──────┐
        │  EXPECTED  │  advance ship notice or PO line
        └─────┬──────┘
              │ vehicle arrives, dock assigned
        ┌─────▼──────┐
        │  ARRIVED   │
        └─────┬──────┘
              │ scan receipt — quantity and variance recorded
        ┌─────▼──────┐
        │  RECEIVED  │  ──► M15 creates stock in INSPECTION status
        └─────┬──────┘
              │
        ┌─────▼──────────┐
        │ UNDER INSPECTION│  physically held in the inspection area
        └──┬──────────┬──┘
    passed │          │ failed
           │          └──────────────┐
    ┌──────▼───────┐          ┌──────▼───────┐
    │ AWAITING     │          │  REJECTED    │──► quarantine → RTV (M16)
    │ PUT-AWAY     │          └──────────────┘
    └──┬────────┬──┘
       │        │ demand already waiting
       │        └──────────────► CROSS-DOCKED ──► outbound staging
       │ directive issued
    ┌──▼─────────┐
    │ PUT AWAY   │  ──► M15 releases stock to UNRESTRICTED
    └────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Expected | Arrived | Vehicle at dock; consignment identified | Warehouse operative |
| Arrived | Received | Scan-based receipt complete; variance recorded against PO or import lines | Warehouse operative |
| Received | Under inspection | Inspection plan exists for the part or supplier (M23) | System |
| Under inspection | Awaiting put-away | Inspection passed and evidence captured (BRU-INV-09) | Operative / QC |
| Under inspection | Rejected | Inspection failed | Operative / QC |
| Awaiting put-away | Cross-docked | Open outbound demand matches and the wave has not been released | System |
| Awaiting put-away | Put away | Directive issued, bin scanned, ownership class permitted (BRU-WMS-03) | Warehouse operative |
| Rejected | Quarantine | Disposition recorded | QC |

### 8.2 Outbound Wave & Task Lifecycle

```
   Outbound demand (M15 transfer · van replenishment · RTV · refurb issue)
              │
        ┌─────▼──────┐
        │  QUEUED    │  priority and cut-off applied
        └─────┬──────┘
              │ wave template matched
        ┌─────▼──────┐
        │  WAVED     │  grouped, not yet allocated
        └─────┬──────┘
              │ availability confirmed with M15, stock allocated
        ┌─────▼──────┐
        │ RELEASED   │  pick tasks generated and sequenced
        └─────┬──────┘
              │
        ┌─────▼──────┐        ┌────────────────┐
        │  PICKING   │───────►│  SHORT PICK    │──► count-back, re-source
        └─────┬──────┘        └────────────────┘
              │ all lines confirmed
        ┌─────▼──────┐
        │  PICKED    │
        └─────┬──────┘
              │ cartonised, handling unit created
        ┌─────▼──────┐
        │  PACKED    │
        └─────┬──────┘
              │ moved to destination stage
        ┌─────▼──────┐
        │  STAGED    │
        └─────┬──────┘
              │ load confirmed, handed to M03
        ┌─────▼──────┐
        │ DISPATCHED │  ──► M15 moves stock to IN TRANSIT
        └────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| Queued | Waved | Wave template matched; cut-off reached or urgent flag set | System / warehouse manager |
| Waved | Released | M15 confirms availability and allocates; tasks generated and sequenced | System |
| Released | Picking | First task claimed by an operative | Warehouse operative |
| Picking | Short pick | Bin quantity insufficient — count-back triggered automatically (FR-WMS-033) | System |
| Picking | Picked | Every line confirmed by scan | Warehouse operative |
| Picked | Packed | Handling unit created and labelled | Warehouse operative |
| Packed | Staged | Moved to the destination staging area by scan | Warehouse operative |
| Staged | Dispatched | Load confirmed and manifest handed to M03 | Warehouse operative / logistics |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-WMS-01 | M41 never authors a stock quantity; every physical confirmation is posted to the ledger by M15 | **H** | CTO |
| BRU-WMS-02 | Warehouse execution is enabled per location; a location not enabled operates on M15 alone | **C** | Warehouse Manager |
| BRU-WMS-03 | A put-away or internal move into a bin whose permitted ownership-class set excludes the item's class is rejected at the scanner | **H** | Supply Chain Director |
| BRU-WMS-04 | Received stock is not available to pick until the inspection result is recorded | **H** | Quality Manager |
| BRU-WMS-05 | Every put-away and every pick is confirmed by scanning both the bin and the item | **H** | Warehouse Manager |
| BRU-WMS-06 | A directive override requires a reason code and appears on the daily override report | **A** | Warehouse Manager |
| BRU-WMS-07 | A short pick triggers an immediate count-back of the affected bin | **H** | Warehouse Manager |
| BRU-WMS-08 | A pick that drives a bin to zero triggers a zero-crossing count | **C** | Warehouse Manager |
| BRU-WMS-09 | A put-away that would exceed a bin's volume or weight capacity is rejected and re-directed | **H** | Warehouse Manager |
| BRU-WMS-10 | Serial-controlled parts require serial capture at both put-away and pick | **H** | Warehouse Manager |
| BRU-WMS-11 | Hazardous items (lithium batteries, pressurised or flammable materials) may only be put away into bins of the matching storage category | **H** | Quality Manager |
| BRU-WMS-12 | A blocked bin cannot be picked from or put away into until it is unblocked with a recorded reason | **H** | Warehouse Manager |
| BRU-WMS-13 | A wave is released only when M15 confirms allocation for its lines; partial release is explicit, never silent | **H** | Warehouse Manager |
| BRU-WMS-14 | A task is assigned to exactly one operative; reassignment releases the prior claim explicitly | **H** | Warehouse Manager |
| BRU-WMS-15 | Cross-dock applies only to lines with confirmed open demand and only before the receiving wave is released | **C** | Warehouse Manager |
| BRU-WMS-16 | A count performed on the floor is submitted to M15; the adjustment is approved there, never on the device (SOD-05) | **H** | CFO |
| BRU-WMS-17 | Dispatch cannot be confirmed without a complete, scanned handling-unit manifest | **H** | Warehouse Manager |
| BRU-WMS-18 | An operative may not be assigned a task requiring equipment or certification they do not hold | **H** | Warehouse Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.wh.warehouse` | `fix_wh_warehouse` | WMS-enabled location configuration | stock_location_id (M15), name, company_id, operating_unit_id, enabled, wave_cutoffs, shift_pattern |
| `fix.wh.zone` | `fix_wh_zone` | Zone within a warehouse | warehouse_id, code, type (bulk/pick/inspection/quarantine/staging/returns/secure), permitted_ownership_classes |
| `fix.wh.bin` | `fix_wh_bin` | The storage bin | zone_id, code, aisle, bay, level, position, storage_category, volume_capacity, weight_capacity, current_volume, current_weight, is_pick_face, permitted_ownership_classes, blocked, blocked_reason |
| `fix.wh.slotting` | `fix_wh_slotting` | Part-to-bin-class assignment | part_id, warehouse_id, home_bin_id, bin_class, velocity_band, pick_frequency_90d, last_reslotted_at |
| `fix.wh.inbound` | `fix_wh_inbound` | An inbound delivery | source_type (po/import/return/transfer), source_id, warehouse_id, dock_id, expected_at, arrived_at, received_at, state |
| `fix.wh.inbound.line` | `fix_wh_inbound_line` | One received line | inbound_id, part_id, expected_qty, received_qty, variance_reason, lot_id, serials, inspection_result, state |
| `fix.wh.handling.unit` | `fix_wh_handling_unit` | Licence-plated pallet or carton | code, warehouse_id, parent_hu_id, current_bin_id, type, gross_weight, state, contents |
| `fix.wh.directive` | `fix_wh_directive` | A put-away or pick instruction | type, inbound_line_id / pick_line_id, part_id, quantity, target_bin_id, strategy_used, rejected_bins_json, issued_at |
| `fix.wh.wave` | `fix_wh_wave` | A grouped outbound release | warehouse_id, template_id, state, released_at, line_count, pick_strategy, cutoff_at, completed_at |
| `fix.wh.wave.template` | `fix_wh_wave_template` | Wave configuration | name, purpose, release_rule, cutoff_times, pick_strategy, priority, destination_filter |
| `fix.wh.outbound.line` | `fix_wh_outbound_line` | One line of outbound demand | wave_id, source_type (transfer/van/rtv/refurb), source_id, part_id, quantity, destination, priority, state, short_qty |
| `fix.wh.task` | `fix_wh_task` | The unit of physical work | warehouse_id, type (putaway/pick/replen/move/count/pack/stage/load), reference_id, zone_id, from_bin_id, to_bin_id, part_id, quantity, priority, equipment_required, time_standard_sec, assigned_to, claimed_at, completed_at, state |
| `fix.wh.task.event` | `fix_wh_task_event` | Scan-level execution record | task_id, operative_id, device_id, scan_type, scanned_value, accepted, rejection_reason, occurred_at, offline_captured |
| `fix.wh.count` | `fix_wh_count` | Floor count execution | warehouse_id, type (cycle/zero-cross/count-back/full), scope (bin/zone/abc), bin_ids, counter_id, submitted_at, m15_count_id |
| `fix.wh.replenishment` | `fix_wh_replenishment` | Bulk-to-pick-face task source | part_id, pick_face_bin_id, source_bin_id, trigger_qty, quantity, state |
| `fix.wh.operative` | `fix_wh_operative` | Warehouse worker profile | employee_id, warehouse_id, zones, equipment_certifications, shift, active |
| `fix.wh.equipment` | `fix_wh_equipment` | Material-handling equipment | warehouse_id, type, code, capacity, assigned_to, active |
| `fix.wh.device` | `fix_wh_device` | RF handheld | warehouse_id, device_code, enrolled_at, last_seen_at, app_version, active |
| `fix.wh.productivity` | `fix_wh_productivity` | Labour measurement | operative_id, date, task_type, tasks_completed, lines, units, actual_seconds, standard_seconds, accuracy_rate |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.stock.location` | M15 | Read; M41 subdivides WMS-enabled locations |
| `fix.stock.quant`, `fix.stock.move` | M15 | Read; movement confirmations written via M15's API only |
| `fix.stock.ownership.class` | M15 | Read; enforced as a bin constraint |
| `fix.stock.reservation` | M15 | Read; wave allocation requested through M15 |
| `fix.stock.transfer` | M15 | Read as outbound demand |
| `fix.catalogue.item` (dimensions, weight, hazard class, serial control) | M37 | Read via API |
| `fix.purchase.order`, `fix.goods.receipt` | M16 | Read as inbound authority |
| `fix.import.consignment` | M44 | Read as inbound authority for imports |
| `fix.checklist.template`, `fix.nonconformance` | M23 | Read the plan; raise the non-conformance |
| `fix.consignment` (transport) | M03 | Write the handover; read the collection status |
| `fix.employee`, `fix.shift.pattern` | M21 / M55 | Read for operative identity and roster |
| `fix.stock.rtv` | M15 | Read as outbound demand |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-WMS-01 | Inbound delivery arrives at dock | Open the inbound record, present the expected lines on the RF device, start the unload clock | Manual inbound creation |
| AUT-WMS-02 | Receipt line confirmed | Notify M15 to create stock in inspection status; generate labels; create the inspection task where a plan exists | Queue and retry; alert on repeated failure |
| AUT-WMS-03 | Inspection recorded as passed | Generate the put-away directive using the strategy sequence and create the put-away task | Manual directive request |
| AUT-WMS-04 | Inspection recorded as failed | Direct the line to quarantine, raise the non-conformance to M23 and the RTV signal to M15 | Hold in inspection and escalate |
| AUT-WMS-05 | Receipt line matches open outbound demand | Propose cross-dock, route to the outbound stage, and skip put-away | Normal put-away path |
| AUT-WMS-06 | Put-away directive violated at scan | Reject the scan, re-direct to the next eligible bin, log the attempt | Hard reject at device |
| AUT-WMS-07 | Wave cut-off reached, or urgent demand flagged | Match the wave template, request allocation from M15, release, generate and sequence pick tasks | Manual wave release |
| AUT-WMS-08 | Operative completes a task | Assign the next task by zone, priority and equipment; offer an interleaved task where one is on the return path | Present the queue for pull selection |
| AUT-WMS-09 | Short pick recorded | Trigger a count-back of the bin, attempt re-source from an alternate bin, notify M15 of the shortfall and the requesting branch | Escalate to warehouse manager |
| AUT-WMS-10 | Pick drives a bin to zero | Create a zero-crossing count task for that bin | Log only |
| AUT-WMS-11 | Pick-face bin falls below minimum | Generate a bulk-to-pick-face replenishment task ahead of the next wave | Alert the warehouse manager |
| AUT-WMS-12 | Wave picking complete | Create packing tasks, propose cartonisation, generate handling units and labels | Manual packing |
| AUT-WMS-13 | Load confirmed at the dock | Notify M03 of the ready manifest and notify M15 to move stock into transit | Manual handover |
| AUT-WMS-14 | Count submitted on the device | Post to M15 as a count record for variance evaluation and adjustment approval | Retain locally and retry |
| AUT-WMS-15 | Nightly | Recompute slotting velocity bands, propose re-slotting moves, refresh time standards and productivity | Retain previous values |
| AUT-WMS-16 | RF device offline beyond threshold | Flag the device, preserve its queued journal, and alert the supervisor to the operative's unconfirmed work | Alert only |
| AUT-WMS-17 | Put-away cycle time exceeds target for a receipt | Escalate to the warehouse manager with the blocking task identified | Report only |

---

## 12. Interfaces

### 12.1 Upstream — M41 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M15 Inventory** | Location definition, quantity, ownership class, status, allocation confirmation, outbound demand | REST + events |
| M37 Catalogue | Part dimensions, weight, hazard class, storage requirement, serial-control flag | REST |
| M16 Procurement | Purchase order and expected receipt lines | Event `po.confirmed` + REST |
| M44 Import | Cleared import consignment and its expected lines | Event `import.cleared` |
| M23 Quality | Inspection plan, sampling rule, checklist | REST |
| M03 Logistics | Inbound arrival notification; outbound collection readiness | Events |
| M21 / M55 | Operative identity, certification, shift roster | REST |
| M43 Demand Planning | Velocity signals informing slotting | Warehouse extract |

### 12.2 Downstream — M41 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M15 Inventory** | Receipt, put-away, pick, move, count and dispatch confirmations; bin-level positions | Commands + events |
| M16 Procurement | Receipt confirmation and variance for three-way match | Events |
| M42 Supplier Relationship | Inspection results, receipt accuracy and packaging quality for the scorecard | Events |
| M44 Import | Physical receipt confirmation against the import consignment | Events |
| M03 Logistics | Staged and loaded manifests ready for collection | Commands |
| M23 Quality | Inspection outcomes, non-conformances, damage findings | Events |
| M43 Demand Planning | Throughput and capacity signals | Warehouse extract |
| M25 BI / M62 Data Platform | Throughput, accuracy, cycle-time and labour facts | Warehouse extract |
| P03 Admin Portal | Warehouse control tower | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `wh.inbound_arrived` | inbound, source, dock, expected lines | M16, M44, M03 |
| `wh.receipt_confirmed` | line, part, expected qty, received qty, variance | M15, M16, M44, M42 |
| `wh.inspection_completed` | line, result, sample size, evidence | M15, M23, M42 |
| `wh.putaway_completed` | part, quantity, bin, handling unit, strategy | M15 |
| `wh.cross_docked` | line, inbound, outbound demand, stage | M15, M03 |
| `wh.wave_released` | wave, template, line count, strategy | M15 |
| `wh.pick_confirmed` | task, part, quantity, bin, serials | M15 |
| `wh.short_pick` | line, part, requested, picked, shortfall, bin | M15, M43 |
| `wh.packed` | handling unit, contents, destination | M03 |
| `wh.dispatched` | handling units, destination, manifest, M03 consignment | M15, M03 |
| `wh.count_submitted` | bins, lines, counted quantities | M15 |
| `wh.bin_blocked` | bin, reason, actor | M15 |
| `wh.directive_overridden` | directive, intended bin, actual bin, reason, actor | M15, M23 |
| `wh.productivity_recorded` | operative, date, tasks, lines, accuracy | M21, M25, M57 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-WMS-01 | Android RF handheld scanners | Bidirectional | The operative execution surface |
| INT-WMS-02 | Thermal label printers (ZPL/IPP) | Outbound | Bin, handling-unit and dispatch labels |
| INT-WMS-03 | Warehouse Wi-Fi and device management | Bidirectional | Device enrolment, health and remote deactivation |
| INT-WMS-04 | Weighing scales at pack stations *(optional, W8)* | Inbound | Weight verification against expected content weight |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/wh/tasks/next` | GET | Fetch the operative's next task | RF app |
| `/api/v1/wh/tasks/{id}/claim` | POST | Claim a task | RF app |
| `/api/v1/wh/tasks/{id}/confirm` | POST | Confirm execution with scans (idempotent) | RF app |
| `/api/v1/wh/tasks/{id}/exception` | POST | Record short pick, full bin, damage or blocked bin | RF app |
| `/api/v1/wh/sync` | POST | Offline journal replay | RF app |
| `/api/v1/wh/inbound` | POST | Open an inbound delivery | P03, M44 |
| `/api/v1/wh/inbound/{id}/receive` | POST | Confirm received lines | RF app, P03 |
| `/api/v1/wh/inbound/{id}/inspect` | POST | Record inspection result and evidence | RF app, P03 |
| `/api/v1/wh/waves` | POST | Create and release a wave | P03 |
| `/api/v1/wh/waves/{id}` | GET | Wave progress and exceptions | P03 |
| `/api/v1/wh/bins` | GET | Bin master, occupancy and constraints | P03, M15 |
| `/api/v1/wh/bins/{id}/block` | POST | Block or unblock a bin | P03 |
| `/api/v1/wh/counts` | POST | Submit a floor count to M15 | RF app |
| `/api/v1/wh/handling-units/{code}` | GET | Resolve a licence plate to its contents | P03, M03 |
| `/api/v1/wh/dashboard` | GET | Live workload, throughput and congestion | P03, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R17 Inventory Manager | C R U D A | All warehouses |
| R20 Warehouse Operative | R U | Own warehouse, own assigned tasks |
| R18 Branch Store Keeper | R | Own branch's inbound and outbound only |
| R06 Branch Manager | R | Own branch's transfers in progress |
| R19 Procurement Officer | R | Receipt status and inspection outcomes |
| R32 Quality Manager / ISO Coordinator | R U A | Inspection execution, non-conformance, bin blocking |
| R15 Logistics Coordinator | R | Staged and ready-to-collect loads |
| R05 Operations Director | R | All |
| R26 Finance Manager | R | Throughput and accuracy; no transactional rights |
| R33 IT / System Administrator | R U | Device enrolment, layout configuration; no stock transactions |

**Warehouse-supervisor rights.** The Warehouse Manager role is exercised through R17 with a
warehouse-scoped supervisor grant covering wave release, task reassignment, directive-override
approval and bin blocking.

**Field-level restrictions.** No cost or value field appears anywhere in M41 — not on the RF
device, not in the control tower. The floor has no business knowing part cost, and removing it
removes both a theft incentive and a confidentiality exposure on a shared handheld.

**Segregation of duties.**
- An operative who performs a count on the device cannot approve the resulting adjustment — the adjustment is approved in M15 by a different role (SOD-05).
- An operative cannot both override a put-away directive and approve the override.
- Bin blocking and bin unblocking above a duration threshold require different actors.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Warehouse control tower** | Warehouse Manager, Inventory Manager | Real time | Open tasks by type and zone, wave progress, congestion, exceptions, dock status |
| Inbound cycle time | Warehouse Manager, Procurement, Import | Daily | Arrival → receipt → inspection → put-away, by consignment, against the 2-hour target |
| Put-away compliance | Warehouse Manager | Daily | Directive adherence, override count and reasons, exception causes |
| Pick performance | Warehouse Manager | Daily | Lines per hour by operative, zone and strategy; travel time proxy; short-pick rate |
| **Pick accuracy** | Warehouse Manager, Quality Manager | Weekly | Errors detected at pack, at branch receipt and at count, against the 99.5% target |
| Wave analysis | Warehouse Manager | Weekly | Wave size, release-to-dispatch time, lines short, template effectiveness |
| Bin occupancy and capacity | Warehouse Manager | Weekly | Utilisation by zone, full-bin exceptions, consolidation opportunities |
| Slotting effectiveness | Warehouse Manager, Inventory Manager | Monthly | Pick-face hit rate, travel implied by current slotting, re-slot proposals |
| Floor count coverage | Inventory Manager, Quality Manager | Monthly | Cycle, zero-crossing and count-back coverage; variance found by count type |
| Labour productivity | Warehouse Manager, HR | Monthly | Actual vs standard time by task type; workload balance across operatives |
| Cross-dock utilisation | Warehouse Manager, Operations Director | Monthly | Lines cross-docked, time saved, demand types benefiting |
| Inspection outcomes | Quality Manager, Procurement | Monthly | Rejection rate by supplier and part — feeds the M42 scorecard |
| Ownership-class segregation | Warehouse Manager, Supply Chain Director | Monthly | Attempted violations rejected at scan, by class and operative |
| Device and connectivity health | IT Administrator | Weekly | Device availability, offline episodes, unsynchronised journals |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Warehouse pick accuracy** | unmeasured | 99.0% | **> 99.5%** |
| — | **Lines picked per operative-hour** | unmeasured | baseline +20% | **baseline +35%** |
| — | **Put-away cycle time (receipt → available)** | days | < 4 h | **< 2 h** |
| — | Inbound cycle time (arrival → put away) | unmeasured | < 8 h | **< 4 h** |
| — | Put-away directive compliance | n/a | 95% | **99%** |
| — | Short-pick rate | unmeasured | < 3% | **< 1%** |
| — | Zero-crossing counts executed on trigger | n/a | 90% | **99%** |
| — | Bin-level location accuracy | n/a | 97% | **99.5%** |
| — | Cross-docked share of urgent lines | 0% | 25% | **40%** |
| — | Wave release-to-dispatch time | unmeasured | < 6 h | **< 3 h** |
| — | Ownership-class violations reaching a bin | unknown | **0** | **0** |
| — | RF task confirmations captured by scan | 0% | 98% | **99.9%** |
| — | Operative onboarding to full productivity | ~3 weeks | 5 days | **2 days** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §7 names pick accuracy (> 99.5%), lines picked per
> hour (+35%) and put-away cycle time (< 2 h) as the category KPIs owned by M41. None has a
> canonical `KPI-0nn` identifier in `06-02` §2.6, which stops at KPI-049. **Allocation of new
> KPI identifiers for M41, M42, M43 and M44 is an audit action.**

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `stock` — storage categories, putaway rules, multi-step receipt and delivery routes, internal transfer substrate | 14% |
| L2 | OCA `stock-logistics-barcode` (scan surface), `stock-logistics-warehouse` (`stock_location_zone`, `stock_location_position`, inventory lockdown, discrepancy thresholds) | 20% |
| L5 | `cd_wms_structure`, `cd_wms_inbound`, `cd_wms_outbound`, `cd_wms_rf`, `cd_wms_labour` | 66% |

The custom share is high and is expected to be. Odoo's putaway rules and the OCA barcode app
provide a scan surface and a naive bin model; the directive engine, wave engine, task model,
labour standards and ownership-class enforcement have no open-source equivalent at this
fidelity.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-141** | `cd_wms_structure` — warehouse, zone, bin master, capacity model, storage categories, slotting and re-slotting | Odoo module | 4 PW |
| **CD-142** | `cd_wms_inbound` — inbound lifecycle, scan receipt, inspection execution, **directive engine**, cross-dock, handling units | Odoo module | 6 PW |
| **CD-143** | `cd_wms_outbound` — outbound queue, wave templates and engine, pick strategies, path sequencing, packing, staging, dispatch | Odoo module | 6 PW |
| **CD-144** | `cd_wms_rf` — **RF mobile application** (Android, Bengali-first, offline-tolerant, scan-verified) | Mobile app | 5 PW |
| **CD-145** | `cd_wms_labour` — task model, assignment and interleaving, equipment constraints, time standards, productivity | Odoo module | 1 PW |

> CD IDs 141–145 are claimed from the extension block for modules M31–M67 and are
> **provisional** pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M41 is scheduled in **W3** (P1) but declares a dependency on 1 module(s) that land later: **M44** (W6). One of three things must be true before the W3 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W3 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M41 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W3 plan for M41 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| **M15 Inventory (W2)** | Hard prerequisite. M41 has no ledger of its own; without M15 there is nothing to execute against |
| M37 Catalogue | Slotting and cartonisation need part dimensions, weight and hazard class |
| M16 Procurement | The purchase order is the inbound authority for domestic receipts |
| M23 Quality | The inspection plan must exist before inspection can be executed |
| M03 Logistics | Dispatch hands over to a consignment |
| M44 Import | Import consignments are the largest inbound volume — M44 lands in W6, so W3 receipts are PO-driven and import handling is completed then |
| Physical prerequisite: **warehouse labelling** | Every bin must be physically labelled before go-live. This is a warehouse project, not a software one, and it is on the critical path |
| Physical prerequisite: **Wi-Fi coverage** | Full-coverage warehouse Wi-Fi and an RF device fleet must be procured and installed |

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Warehouse layout (surveyed, not migrated) | ~20,000 bins at full build; ~6,000 at W3 | `fix.wh.bin` | W3, authored |
| Initial slotting | ~10,000 parts × enabled warehouses | `fix.wh.slotting` | W3, derived from M15 consumption history |
| Operative master | 15–30 | `fix.wh.operative` | W3 |
| Equipment register | ~20 units | `fix.wh.equipment` | W3 |
| Bin-level opening positions | Full count at the enabled warehouses | `fix.wh.bin` occupancy via M15 | W3 cutover |

No warehouse execution data exists to migrate. **The bin master and the initial slotting must be
authored**, and bin-level opening positions established by a physical count at the enabled
warehouses — a smaller repeat of the M15 cutover count, confined to the WMS-enabled sites.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | M41 writes no stock quantity directly; every ledger change at a WMS-enabled location originates from an M15 posting | Code review plus a write-path audit over four weeks |
| AC-02 | A put-away into a bin whose permitted ownership classes exclude the item is rejected at the scanner | Negative test on the device and through the API |
| AC-03 | Directed put-away issues a valid bin for 99% of received lines without operative intervention | Four weeks of receipts |
| AC-04 | Put-away cycle time from receipt to available is under 2 hours at p90 | Four weeks of measured receipts |
| AC-05 | Pick accuracy exceeds 99.5%, measured by errors found at pack, at branch receipt and at count | Twelve weeks of production picking |
| AC-06 | Lines picked per operative-hour improve by at least 35% against the pre-M41 baseline | Baseline measured in W2, compared at W8 |
| AC-07 | A short pick automatically triggers a bin count-back and a re-source attempt | Scripted scenario |
| AC-08 | A pick driving a bin to zero creates a zero-crossing count within the same shift | Four weeks of trigger-to-count records |
| AC-09 | Wave release either allocates every line or short-releases explicitly; no silent partial release | Negative test with induced stock shortage |
| AC-10 | Cross-dock routes a matching inbound line to the outbound stage without a put-away | Scripted scenario |
| AC-11 | The RF app functions through a two-hour Wi-Fi outage and replays its journal with no duplicate or lost movement | Induced-outage test with 10 devices |
| AC-12 | Scan-to-next-instruction latency is at or below 500 ms at p95 on warehouse Wi-Fi | Performance test at production task volume |
| AC-13 | Two devices cannot claim the same task | Concurrency test |
| AC-14 | A floor count is submitted to M15 and cannot be self-approved by the counter | SoD negative test (SOD-05) |
| AC-15 | A hazardous item cannot be put away into a non-matching storage category | Negative test |
| AC-16 | A serial-controlled part cannot be put away or picked without serial capture | Negative test |
| AC-17 | Enabling M41 at one location leaves all other M15 locations operating unchanged | Regression test across three non-enabled branches |
| AC-18 | The RF application is complete in Bengali and legible on the standard handheld | Translation coverage report and field review (AS-12) |
| AC-19 | A new operative reaches full task productivity within two days | Onboarding cohort measurement |
| AC-20 | Warehouse Manager and Inventory Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 20 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many central warehouses exist, where are they, and what is the floor area and rack configuration of each? | Warehouse Manager | W3 minus 3 months |
| Q-02 | Which branch stores are large enough to justify M41? What is the threshold — line count, throughput, or floor area? | Warehouse Manager / Operations Director | W3 design |
| Q-03 | Is bin labelling of the existing warehouses approved and budgeted, and who executes it? It is on the critical path. | Warehouse Manager / Facilities | W3 minus 4 months |
| Q-04 | Is full warehouse Wi-Fi coverage in place, and if not, what is the installation lead time? | IT Administrator | W3 minus 4 months |
| Q-05 | What RF device is standardised on, how many, and what is the procurement lead time? Rugged handheld or consumer Android with a sled? | IT Administrator / Procurement | W3 minus 3 months |
| Q-06 | Are warehouse operatives employees or contractors? This determines whether productivity data may be used in performance management (M57). | HR Director / Legal | W3 build |
| Q-07 | What are the branch transfer run schedules? Wave cut-off times must align with departure times. | Logistics Manager | W3 build |
| Q-08 | Does any brand partner contractually require physically separate, lockable storage for its consignment stock rather than segregated bins? | Warehouse Manager / CCO | W3 design |
| Q-09 | Is a secure cage required for high-value parts, and what is the value threshold? | Inventory Manager / CFO | W3 build |
| Q-10 | What is the lithium-battery storage policy and does the current warehouse meet it? | Quality Manager / Facilities | W3 build |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (why inventory and warehouse are separate), §6, §7, §9 ·
`M15_Spare_Parts_and_Inventory_Management.md` §3 (the reciprocal boundary) ·
`M16_Procurement_and_Strategic_Sourcing.md` (receipt authority) ·
`M44_Import_Trade_Compliance_and_Landed_Cost.md` (import inbound) ·
`M43_Demand_Planning_and_Replenishment.md` (velocity signals) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md` (dock handover) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §3.3, §6 SOD-05 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` BO-03

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-INV-001, BR-INV-004,
BR-INV-012, BR-INV-013 · `1000FiX_Services_Company_Profile.md` §Service Infrastructure

**External benchmark**
[SAP Extended Warehouse Management — put-away strategies](https://community.sap.com/t5/supply-chain-management-blog-posts-by-members/putaway-strategies-in-extended-warehouse-management-part-1/ba-p/13798628)
(fixed bin, addition to existing stock, near fixed pick bin, empty bin, bulk) ·
[SAP EWM picking strategies, wave management and cycle counting](https://www.rfgen.com/products/sap-enterprise-mobility/sap-extended-warehouse-management-guide/) ·
[SAP EWM 2025 warehouse mobility practice](https://www.rfgen.com/blog/ewm-2025-executives-guide-warehouse-mobility-efficiency/) ·
[Microsoft Dynamics 365 — work templates and location directives](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/create-location-directive) ·
[Microsoft Dynamics 365 — cluster picking](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/set-up-cluster-picking) ·
[Dynamics 365 warehouse management overview](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/warehouse-management-overview) —
licence plates, wave processing, cross-docking, packing stations ·
Oracle Fusion Cloud Warehouse Management — rule-based put-away, task interleaving, cartonisation ·
[OCA stock-logistics-warehouse](https://github.com/oca/stock-logistics-warehouse) — location
zones, coordinate attributes, inventory lockdown, discrepancy blocking ·
[ABC-driven cycle counting on the floor](https://www.getonecart.com/cycle-counting-inventory/)

---

*Module M41 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
