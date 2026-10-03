---
id: FIX-ERP2-M15
module_id: M15
module_code: INV
module_name: Spare Parts & Inventory Management
category: E — Supply Chain & Inventory
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Warehouse Manager
system_owner: Supply Chain Squad
priority: P0
wave: W2
---

# M15 — Spare Parts & Inventory Management
### Category E · Code `INV` · Existing (re-scoped in v2.1)

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M15 |
| **Module code** | `INV` |
| **Category** | E — Supply Chain & Inventory |
| **Status** | Existing (re-scoped in v2.1 — warehouse execution moved to M41, part definition to M37, planning to M43, landed-cost calculation to M44) |
| **Priority** | **P0** |
| **Delivery wave** | W2 (Months 5–8) |
| **Business owner** | Warehouse Manager |
| **System owner** | Supply Chain Squad |
| **Delivery layers** | L1 Odoo `stock` · L2 OCA stock-logistics family · L3 barcode aids · L5 custom ownership, van-stock and availability engines |
| **Custom modules** | `cd_stock_ext`, `cd_stock_ownership`, `cd_cycle_count`, `cd_van_stock_control`, `cd_part_availability` |
| **Requirement range** | FR-INV-001 … FR-INV-054 |
| **Requirement count** | **54** *(measured — supersedes the 48 estimate in `02-02`)* |
| **Effort estimate** | **27 person-weeks** *(measured — supersedes the 24 PW estimate)* |
| **Depends on** | M37 Catalogue · M64 MDM · M33 Party Master · M29 Identity · M30 Platform Admin · M28 Integration · M19 Financial Accounting |
| **Depended on by** | M01, M02, M31, M04, M41, M16, M42, M43, M44, M09, M13, M14, M18, M19, M20, M23, M25, M26, M45, M52, M38, M54 |

---

## 2. Purpose

M15 is the **stock ledger of the 1000FiX estate**. It is the single authoritative answer to
four questions asked hundreds of times a day: *do we have the part, where is it, whose is it,
and what is it worth?*

At 51+ branches, one or more central warehouses, 200–400 technician vans and roughly 10,000
active part numbers, those four questions are currently answered by a store keeper's memory
and a spreadsheet that is out of date the moment it is saved. Measured inventory accuracy is
**75%**, which means one part record in four is wrong. A wrong record is not a clerical
problem — it is a technician despatched to a job that cannot be completed, a customer promised
a turnaround that will be missed, and a warranty claim that cannot be evidenced.

M15 does not move stock and it does not decide how much to hold. It **records what is true**,
and it enforces the one rule that a plain inventory module cannot: *a part may only be used
for the purpose its ownership class permits.*

### Why It Exists

1000FiX is the authorised warranty service partner for **17+ international brands**. Brands
place their own parts in 1000FiX custody for warranty work on their own products. Those parts
are not 1000FiX assets, must never be valued in 1000FiX books, and must never be consumed on a
paid repair. Alongside them sit own-purchase commercial stock, customer-supplied parts,
harvested and refurbished parts, rental-pool assets and marketplace-seller stock — six
ownership classes with six different sets of rules, sitting on the same shelf.

No off-the-shelf inventory module models this. Getting it wrong produces two failures that are
invisible until they are catastrophic: the balance sheet overstates assets the Company does not
own, and a brand partner discovers its consignment stock funding 1000FiX's paid-repair margin.
The second failure ends a partnership.

M15 is P0 and lands in Wave 2 because M01 Service Order and M02 Field Service cannot reserve,
issue or cost a part without it.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-INV-001 | "Manage inventory across 51+ service center locations plus central warehouse(s)" |
| ERP BRD BR-INV-002 | "Track van/mobile stock per technician (parts carried in the field)" |
| ERP BRD BR-INV-003 | "Single dashboard showing real-time stock levels at all locations" |
| ERP BRD BR-INV-004 | "Barcode and QR code scanning for all stock movements" |
| ERP BRD BR-INV-005 | "Serial number tracking for high-value spare parts" |
| ERP BRD BR-INV-006 | "Automatically generate replenishment alerts when stock falls below configured minimum levels" |
| ERP BRD BR-INV-007 | "Inter-branch stock transfer requests with approval workflow" |
| ERP BRD BR-INV-008 | "Automatically reserve parts against a service order when parts requisition is created" |
| ERP BRD BR-INV-010 | "Classify parts as: Genuine (OEM), Compatible, Refurbished" |
| ERP BRD BR-INV-011 | "Support FIFO and weighted average stock valuation methods" |
| ERP BRD BR-INV-012 | "Goods receipt with quality inspection step before stocking" |
| ERP BRD BR-INV-013 | "Cycle counting with variance reporting" |
| ERP BRD BR-INV-014 | "Track defective parts returns to vendor (RTV)" |
| ERP BRD BR-INV-015 | "Identify and report dead stock (no movement in configurable period)" |
| Business Objective BO-03 | "Achieve inventory accuracy across all locations — 75% → 98%+", owner Inventory Manager, module M15 |
| Company Profile §Authorized Service Partnerships | 17+ brands for whom 1000FiX performs warranty work — the origin of consignment stock |
| Business Plan §Refurbishment | Harvested and refurbished parts re-enter stock and must be distinguishable from new |
| Exec Summary §6.2 | Inventory cost reduction valued at **BDT 34 lac per year** (M15 with M26 forecasting) |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** M15 was the largest single source of scope collision in
> the v2.0 draft. Four capabilities have been moved out and are claimed by the modules named
> below; both sides of every boundary agree.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The stock ledger: quantity on hand, reserved, in transit, blocked and available, per part per location |
| 2 | Location hierarchy at stock-holding granularity: entity → warehouse → branch store → van → workbench → quarantine |
| 3 | **The six ownership classes** and the rules governing what each may be used for |
| 4 | Ownership-class segregation, reconciliation and brand-facing consignment reporting |
| 5 | Reservation and allocation of parts to a service order, work order or repair job |
| 6 | Issue, return-unused, and consumption posting against the causing job |
| 7 | Van and technician stock: par levels, replenishment triggers, daily reconciliation, variance escalation |
| 8 | Serial-number and batch/lot traceability from receipt to consumption to warranty claim |
| 9 | Inventory valuation: FIFO and weighted average, per ownership class, per entity |
| 10 | Goods receipt into stock, including the quality-inspection gate before stock becomes available |
| 11 | Cycle counting, full physical counting, variance analysis and controlled adjustment |
| 12 | Stock ageing, dead-stock identification, slow-mover reporting and obsolescence provisioning |
| 13 | ABC/XYZ classification and criticality classification of parts |
| 14 | Inter-branch transfer request, approval, in-transit tracking and receipt confirmation |
| 15 | Network-wide availability search: "who has this part, and how far away is it" |
| 16 | Defective-part quarantine, core/harvest capture, scrap and write-off |
| 17 | Return to vendor initiation and credit tracking to closure |
| 18 | Stock reservation policy: priority, expiry, override and release |
| 19 | Barcode and QR generation, labelling and scan-based movement capture |
| 20 | Part substitution and supersession execution at the point of issue |
| 21 | Stock-movement audit trail and inventory analytics |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Part definition, specification, compatibility matrix, supersession chain | **M37** Catalogue | A part is a catalogue concept before it is a stock concept; the same definition serves pricing, e-commerce and procurement |
| Bin-level location, put-away strategy, pick path, wave and cluster picking, dock and staging | **M41** Warehouse Management | M15 is the ledger; M41 is the floor. A branch with one stockroom needs no M41 |
| Reorder point, safety stock, forecast, network rebalancing proposal | **M43** Demand Planning | M15 executes and alerts; M43 decides the parameters |
| The forecast model itself | **M26** AI/ML Services | M43 owns the planning process; M26 owns the algorithm |
| Requisition, RFQ, purchase order, three-way match | **M16** Procurement | Buying is a transaction lifecycle of its own |
| Supplier qualification, contract, scorecard | **M42** Supplier Relationship | M15 never talks to a supplier |
| Import documentation, LC, customs, duty, clearing | **M44** Import & Landed Cost | Cross-border supply is a discipline, not a stock attribute |
| **Landed-cost calculation and allocation** | **M44** | M15 receives the final unit cost and values stock at it; it does not compute it |
| Physical movement between sites, custody and proof of delivery | **M03** Logistics | M15 raises the transfer; M03 moves it and owns the custody chain |
| Journal posting of stock value, COGS and provisions | **M19** Financial Accounting | Only Category G posts to the ledger; M15 raises valuation events |
| Vendor invoice posting, matching payment and credit note | **M52** Accounts Payable | M16 matches, M52 pays |
| Tools, jigs, test equipment and calibrated instruments | **M45** Enterprise Asset & Test Equipment | A multimeter is an asset issued and returned, not stock consumed |
| Rental-pool devices as capitalised assets | **M49** Fixed Assets (with M13) | M15 holds the visibility; M49 holds the capitalisation |
| Customer-owned devices under repair | **M17** Device & Asset Registry | A customer's laptop is not inventory at any point |
| Refurbishment grading, work and resale pricing | **M14** Trade-In & Refurbishment | M15 stocks the output; M14 creates it |
| E-waste batch, disposal certificate, recycler compliance | **M18** E-Waste & Circular Economy | M15 writes stock off; M18 disposes of it lawfully |

### 3.3 Shared Concepts

| Concept | M15's Role | Owning Module |
|---|---|---|
| Part / SKU | Reads definition, compatibility and supersession; owns its stock position | M37 |
| Stock location | Owns to stock-holding granularity; M41 subdivides central warehouses into bins | M15 / M41 |
| Ownership class | **Owns** — the defining concept of this module | M15 |
| Serial number | Owns for stock items; M17 owns serials for customer devices | M15 / M17 |
| Reservation | Owns; M01 and M02 request, M43 informs the policy | M15 |
| Van stock | Owns par levels, balances and reconciliation; M02 owns consumption in the technician app | M15 / M02 |
| Inventory value | Owns the calculation; M19 owns the posting | M15 / M19 |
| Consignment stock | Owns the balance and the segregation rules; M42 owns the consignment agreement | M15 / M42 |
| Transfer | Owns the request and the receipt; M03 owns the movement | M15 / M03 |
| Core / harvested part | Owns the stock record; M14 owns the harvesting decision and grading | M15 / M14 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA — Inventory Management (MM-IM) & Service Parts Management** | Stock types (unrestricted, quality inspection, blocked), special stock indicators for consignment / customer / vendor stock, valuation area, split valuation | **The special-stock-indicator pattern is the single most influential external reference for M15.** SAP models consignment and customer stock as distinct stock types that are physically present but not owned, valued separately or not at all. Our six ownership classes are a direct descendant. Also adopted: stock-status segregation (quality inspection vs unrestricted vs blocked) as a first-class attribute rather than a location | SAP's valuation-area/plant hierarchy depth and split-valuation configuration burden — we use one valuation area per legal entity |
| **SAP extended Service Parts Planning (eSPP)** | Distribution requirements planning across a multi-echelon parts network, service-level driven inventory targeting | The principle that a service parts network is planned as a network, not as independent locations — implemented by M43, but M15 supplies the network availability primitive it needs | The full eSPP planning stack; disproportionate at 10,000 SKUs and one country |
| **Oracle Fusion Cloud — Inventory Management** | Consigned inventory with ownership transfer at consumption, subinventory and locator model, min-max planning, cycle counting with ABC classes | **Ownership transfer at consumption rather than at receipt** — adopted exactly, and it is the accounting spine of our consignment class. Also adopted: ABC-driven cycle-count frequency | Oracle's locator model (superseded by M41 bins for the warehouses that need it) |
| **Microsoft Dynamics 365 Supply Chain Management** | Inventory dimensions (site, warehouse, location, batch, serial, owner), on-hand list by dimension, inventory blocking | The **`owner` dimension** concept — treating ownership as a stock dimension you can slice by, not a flag on a document. Our `ownership_class` is a mandatory dimension on every stock quant and every move | The full inventory-dimension configuration matrix; we fix the dimension set |
| **IFS Cloud — Service Parts & Inventory** | Repairable/rotable pool, condition codes, core tracking, part interchangeability | **Condition coding** (new · refurbished · harvested · defective · scrap) as an attribute orthogonal to ownership, and **core tracking** for harvested components | IFS's aviation-grade airworthiness traceability |
| **PTC Servigistics / Syncron** | Service-parts specific stocking, criticality classes, multi-echelon | Criticality classification (job-stopping vs deferrable) as an input to reservation priority | Their planning engines — M43's scope |
| **Odoo 19 CE `stock` + OCA `stock-logistics-*`** | Quants, moves, reservations, lots/serials, FIFO/AVCO valuation, inventory adjustments with discrepancy thresholds, location zones | The transactional substrate. OCA `stock_inventory_discrepancy` (block validation above a variance threshold) and `stock_inventory_lockdown` are adopted as-is | Odoo's native "owner" field on quants is too weak for six classes with per-class rules; extended in `cd_stock_ownership` |
| **Field-service practice (van/trunk stock)** | Per-technician sub-stockroom, par min/max, automatic transfer order on threshold breach, scan-at-point-of-use | **The whole pattern.** Van stock modelled as a real stock location with par levels, not as an untracked issue | Predictive van loading — deferred to M43/M26 |
| **GS1 traceability practice** | Serialised identification, parent-child serial relationships, interoperable identifiers | Serial-number traceability from receipt through consumption to warranty claim, as the anti-counterfeit and claim-evidence control | Full GS1 EPCIS event infrastructure — disproportionate today, but our event schema does not preclude it |

**Design position.** Four deliberate differences from the benchmark.

First, **ownership class is mandatory, not optional**. In SAP, Oracle and Dynamics, special
stock or owner is a dimension you *may* use. In M15 every quant and every move carries an
ownership class, and there is no "unspecified" value. This is a hard constraint that will
occasionally be inconvenient. It exists because the alternative — a brand's part consumed on a
paid repair — is a business-ending error, and the only reliable defence is to make the class
impossible to omit.

Second, **the ledger and the floor are separated**. Tier-one suites also separate them (SAP
IM vs EWM, Oracle Inventory vs WMS), but they assume most sites run the warehouse layer. We
invert the default: **M41 is opt-in per location**. Fifty-one branch stockrooms holding a few
hundred lines each do not need bins, waves or put-away strategies, and forcing them would
guarantee non-adoption in exactly the places where accuracy matters most.

Third, **van stock is a first-class stock location, not an issue**. The common ERP shortcut is
to expense a part when it leaves the store and reconcile later. At 200–400 vans that shortcut
is the single largest shrinkage channel in the business. Each van is a location with par
levels, a daily reconciliation and a named accountable technician.

Fourth, **cost is received, not computed**. M15 deliberately does not calculate landed cost.
Imported parts carry duty, VAT, AIT, clearing and freight that materially change unit cost;
computing that inside inventory is how service companies end up with two versions of cost.
M44 computes it once, and M15 values stock at the number M44 publishes.

---

## 5. Functional Areas & Features

### 5.1 Stock Ledger & Multi-Location Visibility

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-001 | Stock position | Maintain, for every part at every stock location, the quantities on hand, reserved, allocated, in transit, in quality inspection, blocked and available-to-promise | **P0** | L1 |
| FR-INV-002 | Location hierarchy | Model stock locations as entity → warehouse → branch store → van → workbench → quarantine → scrap, each with an operating unit, an accountable role and a permitted ownership-class set | **P0** | L1/L5 |
| FR-INV-003 | Real-time network dashboard | Present a single live view of stock at all 51+ locations, filterable by part, brand, class, criticality and ownership class (BR-INV-003) | **P0** | L5 |
| FR-INV-004 | Network availability search | Answer "who holds this part and what is the fulfilment time from each holder" ranked by distance, transfer lead time and stock health | P1 | L5 |
| FR-INV-005 | Stock movement ledger | Record every movement as an immutable line carrying part, quantity, from-location, to-location, ownership class, reason code, actor, timestamp and source document | **P0** | L1/L5 |
| FR-INV-006 | Stock status | Support quality-inspection, unrestricted, blocked and quarantined statuses, where only unrestricted stock is available to reserve | **P0** | L5 |
| FR-INV-007 | Barcode and QR movement | Generate scannable part, bin and location labels and permit every movement to be captured by scan on a handheld or phone (BR-INV-004) | **P0** | L2/L3 |
| FR-INV-008 | Negative-stock prevention | Reject any movement that would drive a location's on-hand quantity below zero, with no configurable exception | **P0** | L5 |
| FR-INV-009 | Stock enquiry API | Expose a low-latency availability API consumed by M01 intake, M02 dispatch, M36 quotation and P01 customer portal | **P0** | L5 |

### 5.2 Ownership Classes & Segregation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-010 | Ownership class dimension | Carry a mandatory ownership class on every quant and every move: own commercial · brand consignment · customer-supplied · refurbished/harvested · rental pool · marketplace seller | **P0** | L5 |
| FR-INV-011 | Use-permission enforcement | Evaluate, at reservation and at issue, whether the ownership class permits the intended use, and hard-block where it does not | **P0** | L5 |
| FR-INV-012 | Consignment ledger by brand | Maintain a per-brand consignment balance showing received, consumed on warranty, returned, damaged and outstanding, reconcilable to the brand's own records | **P0** | L5 |
| FR-INV-013 | Ownership transfer at consumption | Transfer ownership of consignment stock from the brand to 1000FiX at the moment of consumption, not at receipt, and raise the settlement event | **P0** | L5 |
| FR-INV-014 | Consignment reconciliation | Produce a monthly per-brand reconciliation pack and expose it to the brand through P08 | P1 | L5 |
| FR-INV-015 | Customer-supplied parts | Receive a customer's own part against their job, hold it at zero value, and either consume it on that job or return it — never absorb it into general stock | P1 | L5 |
| FR-INV-016 | Valuation exclusion | Exclude brand consignment, customer-supplied and marketplace-seller stock from inventory valuation and from every balance-sheet extract | **P0** | L5 |
| FR-INV-017 | Physical segregation support | Where M41 is deployed, require distinct storage areas per ownership class and reject a put-away that mixes classes in one bin | P1 | L5 |
| FR-INV-018 | Class change control | Permit an ownership-class change only through a named, approved, reason-coded transaction that is separately reportable | **P0** | L5 |

### 5.3 Reservation, Allocation & Issue

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-019 | Automatic reservation | Reserve stock automatically when a parts requisition is raised against a service order or work order (BR-INV-008) | **P0** | L1/L5 |
| FR-INV-020 | Reservation priority | Resolve competing demand by rule: warranty and SLA-bound work ranks above walk-in paid work, which ranks above stock-building transfers | P1 | L5 |
| FR-INV-021 | Reservation expiry | Expire an unconsumed reservation after a configurable period, return stock to available and notify the requester | P1 | L5 |
| FR-INV-022 | Issue to job | Issue reserved stock against the causing job with scan confirmation, writing consumption, cost and ownership-class evidence to the job record | **P0** | L5 |
| FR-INV-023 | Return unused | Return an unconsumed issued part to stock in its original condition and class, or route it to quarantine if condition has changed | **P0** | L5 |
| FR-INV-024 | Substitution at issue | Offer an approved alternate or superseding part from M37 when the requested part is unavailable, recording the substitution on the job | P1 | L5 |
| FR-INV-025 | Backorder | Where no stock exists anywhere in the network, create a backorder that drives a transfer or a requisition and holds the job's parts-wait state | P1 | L5 |
| FR-INV-026 | Kit issue | Issue a defined service kit as a single transaction, exploding to its component parts in the ledger | P2 | L5 |
| FR-INV-027 | Emergency override | Permit a named role to override a reservation with a recorded reason, notification to the displaced job's owner, and inclusion on a standing override report | P1 | L5 |

### 5.4 Van & Technician Stock

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-028 | Van as a stock location | Model every van as a stock location with a single accountable technician and a distinct ownership-class permission set (BR-INV-002) | **P0** | L5 |
| FR-INV-029 | Par levels | Hold a minimum and maximum quantity per part per van, set by zone, skill profile and historical consumption, and maintained by M43 from W6 | **P0** | L5 |
| FR-INV-030 | Replenishment trigger | Raise a van replenishment request automatically when a part falls below its minimum, targeting the technician's home branch | **P0** | L5 |
| FR-INV-031 | Daily reconciliation | Require a scan-based van stock confirmation at shift end, compare it to the expected balance and record any variance | **P0** | L5 |
| FR-INV-032 | Variance escalation | Escalate an unexplained van variance above a configurable value threshold to the branch manager, and above a second threshold to the inventory manager, with the technician's next issue blocked pending resolution | **P0** | L5 |
| FR-INV-033 | Van-to-van transfer | Permit a controlled part transfer between technicians with dual scan confirmation and no intermediate branch step | P2 | L5 |
| FR-INV-034 | Van stock ageing | Report parts held on a van beyond a configurable period and propose recall to the branch | P2 | L5 |

### 5.5 Serial, Batch & Traceability

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-035 | Serial tracking | Track serial numbers for parts flagged serial-controlled in M37, from receipt through every movement to consumption (BR-INV-005) | **P0** | L1/L2 |
| FR-INV-036 | Batch / lot tracking | Track batch or lot for parts where the supplier identifies by lot, retaining supplier, receipt and expiry where applicable | P1 | L1 |
| FR-INV-037 | Genealogy to job and claim | Resolve, for any consumed serial, the job, technician, customer device and warranty claim it was consumed on — and the reverse | **P0** | L5 |
| FR-INV-038 | Provenance to source | Resolve, for any serial in stock, the purchase order, goods receipt, supplier and import consignment it arrived on | P1 | L5 |
| FR-INV-039 | Counterfeit and grey-market control | Flag a serial that was never received, was received twice, or falls outside a supplier's declared range, and block its issue pending review | P1 | L5 |
| FR-INV-040 | Recall support | Identify and quarantine every unit of an affected batch or serial range across all locations and vans within one transaction, and list the jobs already consuming it | P1 | L5 |

### 5.6 Valuation & Costing

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-041 | Costing methods | Support FIFO and weighted-average valuation, selected per part category and fixed per legal entity (BR-INV-011) | **P0** | L1 |
| FR-INV-042 | Landed cost adoption | Adopt the final landed unit cost published by M44 for imported parts, and revalue the receiving stock layer when it arrives late | **P0** | L5 |
| FR-INV-043 | Refurbished valuation | Value refurbished and harvested parts at recovery value determined by M14's grading, never at new-part cost | P1 | L5 |
| FR-INV-044 | Valuation events | Raise a valuation event to M19 for every receipt, consumption, adjustment, revaluation, provision and write-off, without posting a journal itself | **P0** | L5 |
| FR-INV-045 | Obsolescence provisioning | Calculate an ageing-based provision by policy band and raise it for M19 to post | P2 | L5 |
| FR-INV-046 | Valuation by ownership class | Report inventory value split by ownership class, with a standing assertion that non-owned classes total zero in the books | **P0** | L5 |

### 5.7 Counting, Accuracy & Adjustment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-047 | Cycle counting | Schedule and execute cycle counts with frequency driven by ABC class and value — A monthly, B quarterly, C annually — and by zero-crossing triggers (BR-INV-013) | **P0** | L2/L5 |
| FR-INV-048 | Count execution and blind counting | Execute counts on a scanner or phone without displaying the expected quantity, capturing the counter's identity per line | **P0** | L5 |
| FR-INV-049 | Variance threshold block | Block validation of a count whose line variance exceeds a configured threshold, routing it for recount and approval | **P0** | L2 |
| FR-INV-050 | Adjustment control | Permit a stock adjustment only with a reason code, approval within the authority matrix, and the count that justifies it — and never by the person who performed that count | **P0** | L5 |
| FR-INV-051 | Full physical count | Support a full count at a location with movement lockdown, staged reconciliation and a signed variance report | P1 | L2 |

### 5.8 Returns, Defectives, Dead Stock & Transfers

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-INV-052 | Defective quarantine and RTV | Route defective parts to quarantine, initiate a return to vendor with an RMA reference, and track it to credit or replacement closure (BR-INV-014) | **P0** | L5 |
| FR-INV-053 | Harvest and core capture | Capture a serviceable component recovered from a scrapped device as refurbished-class stock at recovery value, linked to its source device | P2 | L5 |
| FR-INV-054 | Inter-branch transfer | Raise, approve, dispatch, track in transit and receive an inter-branch transfer, with in-transit stock owned by the sending location until receipt (BR-INV-007) | **P0** | L1/L5 |

> **Cross-cutting.** Dead-stock and slow-mover identification (BR-INV-015), ABC/XYZ
> classification and stock ageing are delivered as analytics over the ledger and are specified
> in §14 rather than as separate transactional requirements. Replenishment alerting
> (BR-INV-006) is raised by M15 against parameters owned by M43; before W6 the parameters are
> manually maintained defaults.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Ownership class as a mandatory quant dimension** | `ownership_class` is non-null on every `fix.stock.quant` and `fix.stock.move`; there is no default and no unspecified value. Enforced at database constraint level, not only in application code |
| T-02 | **Atomic reservation under concurrency** | Reservation uses row-level locking with a bounded wait; two simultaneous reservations of the last unit must resolve to one success and one clean failure, never to a negative quant |
| T-03 | **Append-only movement ledger** | Stock moves are insert-only. A correction is a compensating move with a reason code and a reference to the move it corrects; no update, no delete |
| T-04 | **Availability query performance** | Single-part network availability across 51+ locations returns in ≤ 300 ms at p95; the branch stock dashboard loads in ≤ 2 s |
| T-05 | **Valuation determinism** | Given the same movement history, valuation is reproducible. Every valuation event stores its inputs (method, layer, quantity, unit cost, source) so any balance can be explained without re-derivation |
| T-06 | **Late-cost revaluation** | Where M44 publishes a landed cost after receipt, the affected layer is revalued and a delta valuation event is raised; consumed quantities generate a COGS adjustment rather than a silent restatement |
| T-07 | **Offline van reconciliation** | Van stock confirmation operates offline in the technician app and synchronises through an append-only journal with server-side conflict resolution (AS-13) |
| T-08 | **Idempotent movement API** | Every movement command carries a client-generated idempotency key; replay after a network failure must not double-post |
| T-09 | **Serial uniqueness and lifecycle** | A serial is unique within its part across the estate and across time; re-receipt of a consumed serial is rejected unless it is an explicit return or warranty-exchange transaction |
| T-10 | **Event emission via outbox** | Every stock state change emits a domain event through the transactional outbox (AS-08); no consumer polls stock tables |
| T-11 | **Multi-entity and operating-unit isolation** | Every stock record carries `company_id` and `operating_unit_id`; record rules prevent a branch from seeing or moving another branch's stock except through a transfer (AS-03) |
| T-12 | **Label generation** | Part, location and transfer labels render as Code-128 and QR, printable on thermal label printers, including Bengali part descriptions |
| T-13 | **Bulk import integrity** | Opening-balance and migration loads are staged, validated against M37 for part existence and against the ownership-class rules, and rejected as a set on any failure |
| T-14 | **Scale envelope** | 10,000 active SKUs × ~400 stock locations ≈ 4M potential quant rows; the model is partitioned and indexed for a working set of ~600,000 non-zero quants and ~250,000 moves per month |
| T-15 | **Field-level encryption exemption** | Stock data is not personal data; no field-level encryption is required, but supplier price and unit cost are field-restricted per §13 |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M15 |
|---|---|---|
| **Branch store keeper** | Keeps a notebook and a spreadsheet; knows the stock personally; the branch is blind when they are on leave | Scans in, scans out; the balance is correct without depending on memory; leave is no longer an operational risk |
| **Technician** | Carries whatever accumulated in the van; discovers on site that the part is not there | Van par levels replenished automatically; can see before travelling whether the part exists and where |
| **Dispatcher** | Assigns a job and hopes the part exists | Sees part availability as a dispatch constraint before assigning |
| **Service centre agent** | Promises a turnaround without knowing whether the part is in the country | Quotes a realistic date because network availability and transfer time are visible at intake |
| **Inventory manager** | Reconstructs the picture from 51 spreadsheets, weeks late | One live view; exception-driven work instead of collection-driven work |
| **Warranty claims officer** | Cannot always evidence which part was fitted | Serial-level genealogy links part to job to claim automatically |
| **Brand partner** | Takes 1000FiX's word on consignment usage | Receives a reconciled monthly statement through P08, generated from the ledger |
| **Finance** | Inventory value is an estimate; the auditor qualifies it | Valuation by class, with non-owned stock provably excluded; count-backed balances |
| **Procurement** | Buys on a phone call from a branch | Buys against a network position and evidenced consumption |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Inventory cost reduction** | Accurate balances remove duplicate buying; network visibility lets one branch's surplus serve another's need; dead stock becomes visible and is worked down | **BDT 34 lac per year** at steady state (Exec Summary §6.2, M15 with M26 forecasting) |
| **Working capital release** | Turns rising from an unmeasured baseline to 6+ per year on ~10,000 SKUs | One-time cash release proportional to the reduction in average stock held |
| **Shrinkage elimination — van stock** | 200–400 vans move from untracked to reconciled daily, with variance named to a person | Van variance to **< 1%**; this is the single largest identified leakage channel |
| **Revenue protection — brand relationships** | Consignment misuse becomes technically impossible rather than policy-discouraged | Protects warranty revenue across **17+ brand partnerships**; a single lost authorisation would exceed the entire M15 build cost |
| **Turnaround time** | Parts-wait is one of the two largest contributors to TAT; availability at first request rises to 93% | Supports KPI-002 (TAT < 24 h IT) and KPI-004 (first-time fix 88%) |
| **Job completion** | Stockout-caused delays fall below 3% | Directly protects technician productivity (KPI-011, 8–9 jobs/day) |
| **Warranty claim success** | Serial genealogy supplies part evidence automatically | Supports KPI-041 (claims with complete evidence 98%) and KPI-038 (leakage < 2%) |
| **Audit and close** | Count-backed, class-segregated valuation | Removes an inventory qualification risk and supports KPI-050 (close ≤ 3 days) |
| **Obsolescence avoidance** | Ageing visible from month one; dead stock < 5% of value | Avoids the periodic large write-off that currently arrives as a surprise |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **ISO 9001 conformance** | Traceability of parts to service outcomes is an explicit requirement; 1000FiX's ISO status is a stated competitive advantage and a tender qualifier |
| **Brand partner assurance** | Brands audit their authorised partners. A system that can produce a reconciled consignment statement on demand changes the tone of that audit |
| **Counterfeit defence** | Serial provenance from supplier to job is the practical control against grey-market parts entering the estate — a genuine risk in the Bangladesh IT parts market and a direct threat to brand authorisation |
| **Financial integrity** | Provable exclusion of non-owned stock from the balance sheet is a statement the CFO can sign |
| **Accountability culture** | Named, scanned custody at every step ends "the part must be somewhere" as an acceptable answer |
| **Foundation for planning** | M43 cannot forecast without clean consumption history. Two years of M15 data is the precondition for demand planning, and for M26's models after it |
| **Expansion readiness** | Entity- and operating-unit-scoped stock means a second country is a configuration exercise (BO-18) |

---

## 8. Lifecycle & State Models

### 8.1 Stock Status Lifecycle

```
                 ┌──────────────────┐
   goods receipt │  IN INSPECTION   │  received, not yet available
   from M16/M44  │  (quality gate)  │
                 └────┬────────┬────┘
              passed  │        │ failed
                 ┌────▼─────┐  │
                 │UNRESTRICTED│ │       ◄── the only status that may be reserved
                 └──┬───┬───┬┘  │
        reserved    │   │   │   │
                 ┌──▼───┐ │   │  │
                 │RESERVED│ │  │  │
                 └──┬───┬┘ │   │  │
             issued │   │ expired
                 ┌──▼────┐ │   │  │
                 │ ISSUED │ │   │  │
                 └──┬──┬──┘ │   │  │
        consumed  │  │ returned unused
                 ┌▼──────┐  │   │  │
                 │CONSUMED│  │   │  │
                 └───────┘  │   │  │
                            │   │  │
                 ┌──────────▼─┐ │  │
                 │  IN TRANSIT│ │  │   (inter-branch, owned by sender)
                 └──────┬─────┘ │  │
                        └───────┘  │
                                   │
                 ┌─────────────────▼┐
                 │   QUARANTINED    │  ◄── defective · recall · counterfeit suspicion
                 └───┬──────┬───────┘
              RTV    │      │  scrap decision
                 ┌───▼───┐ ┌▼────────┐
                 │RETURNED│ │ WRITTEN │──► M18 e-waste
                 │TO VENDOR│ │  OFF   │
                 └────────┘ └─────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | In inspection | Goods receipt posted against a PO or import consignment | Store keeper / warehouse operative |
| In inspection | Unrestricted | Inspection passed and recorded with sample evidence (BRU-INV-09) | Store keeper / QC |
| In inspection | Quarantined | Inspection failed; RTV or rework decision follows | Store keeper / QC |
| Unrestricted | Reserved | Requisition raised; ownership class permits the intended use (BRU-INV-01) | System |
| Reserved | Unrestricted | Reservation expired or released | System / requester |
| Reserved | Issued | Scan confirmation at handover to technician or workbench | Store keeper |
| Issued | Consumed | Job records the part as fitted | Technician (M02/M31) |
| Issued | Unrestricted | Returned unused in original condition | Technician + store keeper |
| Issued | Quarantined | Returned in changed condition | Store keeper |
| Unrestricted | In transit | Transfer approved and dispatched to M03 | Branch manager + logistics |
| In transit | Unrestricted | Received and confirmed at destination | Destination store keeper |
| Any | Quarantined | Defect, recall, or serial anomaly detected | System / any role |
| Quarantined | Returned to vendor | RMA raised with M16 | Procurement officer |
| Quarantined | Written off | Write-off approved within the authority matrix | Inventory manager / CFO |

### 8.2 Ownership Class Transitions

Ownership does not flow freely. Only these transitions exist, and each is a controlled,
reason-coded, separately reported transaction (BRU-INV-06).

```
   BRAND CONSIGNMENT ──consumed on warranty job──► OWN COMMERCIAL (instantaneous,
                        │                            then immediately consumed)
                        └──returned to brand──────► (leaves the estate)

   CUSTOMER SUPPLIED ──consumed on that customer's job──► (leaves the estate)
                     └──returned to customer──────────► (leaves the estate)

   OWN COMMERCIAL ──harvested from scrapped device──► REFURBISHED
                  └──allocated to rental build─────► RENTAL POOL (capitalised, M49)

   REFURBISHED ──may never become──► warranty-eligible stock   ✖ blocked

   MARKETPLACE SELLER ──never transfers to 1000FiX──►          ✖ visibility only
```

| From Class | To Class | Trigger | Financial Consequence |
|---|---|---|---|
| Brand consignment | Own commercial | Consumption on a warranty job for that brand | Liability to the brand recognised; settlement event raised to M52 |
| Brand consignment | — (returns to brand) | Period-end return or expiry of the consignment agreement | None; balance reduces |
| Customer supplied | — (leaves) | Consumed on that customer's job, or returned | None; never valued |
| Own commercial | Refurbished | Harvest of a serviceable component from a scrapped device (M14 grades it) | Recognised at recovery value, not at new cost |
| Own commercial | Rental pool | Allocation to a rental build | Capitalised as a fixed asset in M49; leaves consumable stock |
| Refurbished | Own commercial | **Never** | — |
| Marketplace seller | Any | **Never** | — |

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-INV-01 | Brand consignment stock may be consumed only on a warranty job for that brand's product. Any other use is blocked with no override at any authority level | **H** | Supply Chain Director |
| BRU-INV-02 | Brand consignment, customer-supplied and marketplace-seller stock are never included in inventory valuation or in any balance-sheet extract | **H** | CFO |
| BRU-INV-03 | Refurbished or harvested parts may never be used on warranty work | **H** | Quality Manager |
| BRU-INV-04 | A customer-supplied part may be consumed only on that customer's job; it is never absorbed into general stock | **H** | Warehouse Manager |
| BRU-INV-05 | Every stock quant and every stock move carries a non-null ownership class | **H** | CTO |
| BRU-INV-06 | An ownership-class change occurs only through an approved, reason-coded transaction and appears on the monthly class-change report | **H** | CFO |
| BRU-INV-07 | No stock movement may drive a location's on-hand quantity negative | **H** | Warehouse Manager |
| BRU-INV-08 | Stock in quality inspection, blocked or quarantined status cannot be reserved or issued | **H** | Quality Manager |
| BRU-INV-09 | Received goods become available only after the inspection step is recorded | **H** | Quality Manager |
| BRU-INV-10 | The person who performs a count may not approve the adjustment arising from it (SOD-05) | **H** | CFO |
| BRU-INV-11 | A stock adjustment requires a reason code and approval within the authority matrix: ≤ BDT 25,000 Inventory Manager, above that CFO | **H** | CFO |
| BRU-INV-12 | Van stock is reconciled at the end of every shift; an unresolved variance above threshold blocks the technician's next parts issue | **H** | Warehouse Manager |
| BRU-INV-13 | A serial-controlled part cannot be issued without capturing its serial | **H** | Warehouse Manager |
| BRU-INV-14 | A serial not previously received, or already consumed, cannot be issued; it is quarantined and reported | **H** | Quality Manager |
| BRU-INV-15 | Imported parts are not valued as final until M44 publishes the landed cost; interim value is flagged provisional | **H** | CFO |
| BRU-INV-16 | An inter-branch transfer remains the sending location's stock and value until receipt is confirmed | **C** | Warehouse Manager |
| BRU-INV-17 | Reservation priority is warranty/SLA-bound > paid customer work > internal and stock-building demand | **C** | Operations Director |
| BRU-INV-18 | A reservation not consumed within its validity period is released automatically and the requester notified | **C** | Warehouse Manager |
| BRU-INV-19 | A reservation override requires a named role, a recorded reason and notification to the displaced job's owner | **A** | Branch Manager |
| BRU-INV-20 | A part with no movement for the configured dead-stock period is flagged and provisioned by policy band | **C** | CFO |
| BRU-INV-21 | Rental-pool assets are not consumable stock and cannot be issued to a repair job | **H** | Finance Manager |
| BRU-INV-22 | Cycle-count frequency follows ABC class: A monthly, B quarterly, C annually, plus zero-crossing counts | **C** | Warehouse Manager |
| BRU-INV-23 | A count line whose variance exceeds the configured threshold cannot be validated; it is recounted and approved separately | **H** | Warehouse Manager |
| BRU-INV-24 | Stock write-off above BDT 25,000 requires CFO approval | **H** | CFO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.stock.location` | `fix_stock_location` | Stock-holding location hierarchy | name, type (warehouse/branch/van/workbench/quarantine/scrap/transit), parent_id, company_id, operating_unit_id, accountable_user_id, permitted_ownership_classes, wms_enabled |
| `fix.stock.quant` | `fix_stock_quant` | The balance | part_id, location_id, **ownership_class**, owner_party_id, status, lot_id, serial_id, quantity, reserved_qty, unit_cost, cost_provisional, last_movement_at |
| `fix.stock.move` | `fix_stock_move` | The immutable ledger line | part_id, from_location_id, to_location_id, ownership_class, quantity, reason_code, source_doc_type, source_doc_id, actor_id, occurred_at, unit_cost, corrects_move_id |
| `fix.stock.ownership.class` | `fix_stock_ownership_class` | Class definition and rules | code, name, owner_party_type, valued_in_books, permitted_uses, transfer_rules, reporting_group |
| `fix.stock.reservation` | `fix_stock_reservation` | Demand held against stock | part_id, location_id, quantity, requester_module, source_doc_id, priority, expires_at, state, override_by, override_reason |
| `fix.stock.issue` | `fix_stock_issue` | Issue and return against a job | reservation_id, job_id, technician_id, quantity_issued, quantity_returned, quantity_consumed, serials, scanned_at |
| `fix.van.stock.par` | `fix_van_stock_par` | Par levels per van per part | location_id (van), part_id, min_qty, max_qty, set_by, source (manual/M43), effective_from |
| `fix.van.reconciliation` | `fix_van_reconciliation` | Shift-end count | location_id, technician_id, shift_date, lines, variance_qty, variance_value, state, escalated_to, resolved_at |
| `fix.stock.count` | `fix_stock_count` | Cycle or full count | location_id, type, abc_scope, scheduled_for, counter_id, approver_id, state, total_variance_value |
| `fix.stock.count.line` | `fix_stock_count_line` | One counted line | count_id, part_id, lot_id, expected_qty, counted_qty, variance, recount_qty, threshold_breached |
| `fix.stock.adjustment` | `fix_stock_adjustment` | Controlled correction | count_id, part_id, location_id, quantity_delta, reason_code, requested_by, approved_by, value_impact |
| `fix.stock.transfer` | `fix_stock_transfer` | Inter-branch transfer | from_location_id, to_location_id, lines, state, approved_by, consignment_id (M03), dispatched_at, received_at |
| `fix.consignment.balance` | `fix_consignment_balance` | Per-brand consignment position | brand_party_id, part_id, location_id, received_qty, consumed_qty, returned_qty, damaged_qty, outstanding_qty, last_reconciled_at |
| `fix.consignment.reconciliation` | `fix_consignment_reconciliation` | Monthly brand statement | brand_party_id, period, opening, received, consumed, returned, closing, variance, statement_doc_id, brand_acknowledged_at |
| `fix.stock.serial` | `fix_stock_serial` | Serial lifecycle | part_id, serial, current_location_id, current_status, received_on_grn_id, supplier_party_id, consumed_on_job_id, warranty_claim_id, anomaly_flag |
| `fix.stock.quarantine` | `fix_stock_quarantine` | Held stock | part_id, location_id, quantity, reason (defect/recall/counterfeit/condition), detected_by, evidence_ids, disposition, closed_at |
| `fix.stock.rtv` | `fix_stock_rtv` | Return to vendor | supplier_party_id, part_id, quantity, rma_reference, po_reference, dispatched_at, credit_expected, credit_received, state |
| `fix.stock.valuation.event` | `fix_stock_valuation_event` | Value change raised to M19 | move_id, event_type, ownership_class, quantity, unit_cost, total_value, method, inputs_json, posted_to_gl_at |
| `fix.stock.classification` | `fix_stock_classification` | ABC/XYZ and criticality | part_id, scope (global/location), abc_class, xyz_class, criticality, consumption_value_12m, movement_count_12m, computed_at |
| `fix.stock.ageing` | `fix_stock_ageing` | Ageing and dead stock | part_id, location_id, quantity, days_since_last_movement, age_band, provision_rate, provision_value |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.catalogue.item` (part definition, compatibility, supersession, serial-control flag) | M37 | Read via API; cached projection |
| `fix.party` (brand, supplier, customer, seller) | M33 | Read via API |
| `fix.branch`, `fix.entity`, `fix.cost.center` | M30 / M54 | Read |
| `fix.service.order`, `fix.work.order` | M01 / M02 | Read as reservation and consumption context; write consumption back |
| `fix.technician.profile` | M02 | Read for van accountability |
| `fix.purchase.order`, `fix.goods.receipt` | M16 | Read as receipt source |
| `fix.import.consignment`, `fix.landed.cost` | M44 | Read; adopt final unit cost |
| `fix.replenishment.parameter` (reorder point, safety stock) | M43 | Read; execute alerts against |
| `fix.wh.task`, `fix.wh.bin` | M41 | Read where the location is WMS-enabled |
| `fix.consignment` (physical movement) | M03 | Read status for in-transit tracking |
| `fix.brand.claim` | M09 | Read for serial-to-claim genealogy |
| `fix.refurb.grade` | M37 | Read for refurbished recovery value |
| `fix.supplier.agreement` (consignment terms) | M42 | Read |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-INV-01 | Parts requisition raised on a service or work order | Evaluate ownership-class permission, reserve the highest-priority eligible stock, notify the requester of location and availability | Fall back to a manual reservation task for the store keeper |
| AUT-INV-02 | Reservation cannot be met locally | Search the network, propose the best source by distance and stock health, and offer a transfer or a backorder | Raise a parts-unavailable exception on the job |
| AUT-INV-03 | Stock falls below the reorder point (parameter from M43) | Raise a replenishment alert to the branch and a requisition suggestion to M16 (BR-INV-006) | Alert only; no silent suppression |
| AUT-INV-04 | Van part falls below its par minimum | Raise a van replenishment request against the technician's home branch and include it on the next branch pick list | Alert the branch manager |
| AUT-INV-05 | Technician shift ends | Prompt the van reconciliation; on variance, compute value and route by threshold | Block the next issue after a configurable grace period |
| AUT-INV-06 | Consignment stock consumed on a warranty job | Transfer ownership at consumption, update the brand balance, raise the settlement event to M52 | Queue and retry; alert on repeated failure |
| AUT-INV-07 | Month end | Generate the per-brand consignment reconciliation pack and publish it to P08 | Escalate to the Warehouse Manager |
| AUT-INV-08 | Goods receipt posted | Create stock in inspection status, generate labels, schedule the inspection task | Manual receipt task |
| AUT-INV-09 | Inspection recorded as passed | Release stock to unrestricted; where a reservation is waiting, allocate immediately and notify the job | Manual release |
| AUT-INV-10 | M44 publishes a final landed cost | Revalue the affected layer, clear the provisional flag, raise the delta valuation event to M19 | Hold as provisional and report on the exception list |
| AUT-INV-11 | Cycle-count schedule due | Generate count tasks by ABC class and zero-crossing triggers, assign to counters, present blind | Escalate overdue counts to the Warehouse Manager |
| AUT-INV-12 | Count line variance exceeds threshold | Block validation, raise a recount task, route the adjustment for approval | Count remains open and reportable |
| AUT-INV-13 | Serial anomaly detected (unknown, duplicate, out-of-range) | Quarantine the unit, block issue, notify the Quality Manager and Procurement | Immediate hard block |
| AUT-INV-14 | Recall or batch defect declared | Locate every unit across all locations and vans, quarantine in one transaction, list affected jobs | Manual sweep with a generated worklist |
| AUT-INV-15 | Part exceeds the dead-stock threshold | Flag, compute the provision, add to the disposition worklist and notify Procurement to stop reordering | Report only |
| AUT-INV-16 | Defective part quarantined against a supplier | Open an RTV, notify M16 to raise the RMA and M42 to record the quality event on the scorecard | Manual RTV creation |
| AUT-INV-17 | Transfer received at destination | Confirm quantities, transfer value, close in-transit, notify the sending branch of any shortfall | Raise a transfer discrepancy incident |
| AUT-INV-18 | Nightly | Recompute ABC/XYZ classification, criticality, ageing and availability projections | Retain the previous classification and alert |

---

## 12. Interfaces

### 12.1 Upstream — M15 Consumes

| Source | What | Mechanism |
|---|---|---|
| M37 Catalogue | Part definition, compatibility, supersession, serial-control and inspection flags | REST + cached projection |
| M64 MDM | Part, location and unit-of-measure master governance | Event projection |
| M16 Procurement | Purchase order and goods receipt | Command + event `goods.received` |
| M44 Import & Landed Cost | Final landed unit cost per receipt layer | Event `landed_cost.finalised` |
| M43 Demand Planning | Reorder point, safety stock, van par levels, rebalancing proposals | REST (parameters) |
| M41 Warehouse Management | Physical put-away, pick and count confirmations at WMS-enabled locations | Events |
| M01 / M31 / M02 | Parts requisition, consumption confirmation, unused return | Commands |
| M03 Logistics | Transfer dispatch, in-transit status, receipt confirmation | Events |
| M14 Refurbishment | Harvested part grading and recovery value | Event |
| M42 Supplier Relationship | Consignment agreement terms per brand | REST |
| M33 Party Master | Brand, supplier, customer and seller identity | REST |
| M09 Warranty | Claim linkage for consumed serials | REST |

### 12.2 Downstream — M15 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Availability at intake, reservation state, parts-wait status | REST + events |
| M02 Field Service | Van stock position, par status, availability as a dispatch constraint | REST + events |
| M31 Workshop | Workbench stock, issue and return, part genealogy | REST + events |
| M41 Warehouse Management | Authoritative quantity and ownership class that the floor must respect | REST + events |
| M16 Procurement | Consumption history, reorder alerts, RTV initiation | Events |
| M42 Supplier Relationship | Quality events (inspection failures, defect rates) feeding the scorecard | Events |
| M43 Demand Planning | Clean consumption history, stockout events, current positions | Warehouse extract + REST |
| M19 Financial Accounting | Valuation events for receipt, consumption, adjustment, revaluation, provision, write-off | Events |
| M52 Accounts Payable | Consignment settlement obligations at consumption | Events |
| M09 Warranty | Part serial and cost evidence for the claim | REST |
| M20 Receivable / M11 Pricing | Part cost as an input to estimate and invoice lines | REST |
| M23 Quality | Inspection failures, counterfeit flags, recall execution | Events |
| M18 E-Waste | Written-off stock as recycling input | Events |
| M25 BI / M62 Data Platform | Stock, movement, valuation and accuracy facts | Warehouse extract |
| M26 AI/ML | Consumption series for forecasting and failure-pattern models | Warehouse extract |
| P08 Brand Portal | Consignment balance and monthly reconciliation | REST |
| P05 Vendor Portal | RTV status and expected credit | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `stock.received` | part, location, quantity, ownership class, status, cost provisional flag | M16, M19, M41, M43 |
| `stock.inspection_completed` | part, quantity, result, evidence | M23, M42, M16 |
| `stock.reserved` | part, location, quantity, source document, priority | M01, M02, M31 |
| `stock.reservation_released` | reservation, reason | M01, M02 |
| `stock.issued` | part, serials, quantity, job, technician | M01, M31, M02 |
| `stock.consumed` | part, serials, quantity, job, ownership class, unit cost | M19, M09, M20, M43 |
| `stock.ownership_transferred` | part, from class, to class, reason, value | M19, M52, M42 |
| `stock.consignment_consumed` | brand, part, quantity, warranty job, settlement value | M52, M42, P08 |
| `stock.transfer_requested` | from, to, lines, priority | M03, M41 |
| `stock.transfer_received` | transfer, lines, discrepancies | M19, M03 |
| `stock.count_completed` | location, lines, variance quantity and value | M19, M23, M25 |
| `stock.adjusted` | part, location, delta, reason, approver, value | M19, M23 |
| `stock.quarantined` | part, quantity, reason, evidence | M23, M16, M42 |
| `stock.rtv_raised` | supplier, part, quantity, RMA, expected credit | M16, M42, M52 |
| `stock.written_off` | part, quantity, value, approver, disposition | M19, M18 |
| `stock.stockout` | part, location, unmet demand, causing job | M43, M16, M25 |
| `stock.van_variance_detected` | van, technician, lines, variance value | M02, M21, M23 |
| `stock.serial_anomaly` | part, serial, anomaly type, evidence | M23, M42, M29 |
| `stock.dead_stock_flagged` | part, location, value, age band | M43, M16, M19 |
| `stock.revalued` | part, layer, old cost, new cost, delta, source | M19 |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-INV-01 | Brand partner parts portals (Dell, HP, Lenovo, Acer and others) | Bidirectional | Consignment balance confirmation and parts-order status, where the brand exposes an interface; file exchange otherwise |
| INT-INV-02 | Thermal label printers (branch and warehouse) | Outbound | Part, location and transfer label printing over IPP/ZPL |
| INT-INV-03 | Handheld barcode scanners and Android scan devices | Inbound | Movement, count and reconciliation capture |
| INT-INV-04 | Legacy branch stock spreadsheets | Inbound, one-time | Migration staging only; retired at cutover |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/stock/availability` | GET | Availability for a part across the network, with source ranking | M01, M02, M36, P01, P03 |
| `/api/v1/stock/positions` | GET | Quant-level positions filtered by location, part, class and status | P03, P06 |
| `/api/v1/stock/reservations` | POST | Reserve stock against a source document | M01, M02, M31 |
| `/api/v1/stock/reservations/{id}` | DELETE | Release a reservation | M01, M02 |
| `/api/v1/stock/issues` | POST | Issue reserved stock with scan and serial capture | P03, P02 |
| `/api/v1/stock/returns` | POST | Return unused or changed-condition stock | P03, P02 |
| `/api/v1/stock/moves` | POST | Record a movement (idempotent) | P03, M41 |
| `/api/v1/stock/transfers` | POST | Raise an inter-branch transfer | P03 |
| `/api/v1/stock/transfers/{id}/receive` | POST | Confirm receipt with discrepancies | P03 |
| `/api/v1/stock/counts` | POST | Create and submit a count | P03, M41 |
| `/api/v1/stock/adjustments` | POST | Request an adjustment for approval | P03 |
| `/api/v1/van/{id}/stock` | GET | Van position and par status | P02 |
| `/api/v1/van/{id}/reconciliation` | POST | Submit shift-end reconciliation (offline-capable) | P02 |
| `/api/v1/stock/serials/{serial}` | GET | Full serial genealogy and provenance | P03, P08, M09 |
| `/api/v1/consignment/{brand}/balance` | GET | Brand consignment position | P08 |
| `/api/v1/consignment/{brand}/reconciliation` | GET | Monthly reconciliation statement | P08 |
| `/api/v1/stock/valuation` | GET | Valuation by class, location and entity | M19, P06 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R17 Inventory Manager | C R U D A | All locations |
| R18 Branch Store Keeper | C R U | Own branch stock |
| R20 Warehouse Operative | C R U | Own warehouse location |
| R06 Branch Manager | R U A | Own branch; approves transfers and variance resolution |
| R19 Procurement Officer | R | All — read for buying decisions; initiates RTV |
| R05 Operations Director | R A | All |
| R10 / R11 / R12 Technician | R U | Own van only; issue confirmation and reconciliation |
| R09 Workshop Supervisor | R U | Own workshop and workbench stock |
| R08 Service Centre Agent | R | Own branch — availability enquiry only |
| R07 Dispatch Manager | R | Assigned zones — availability as a dispatch constraint |
| R26 Finance Manager | R A | Valuation, adjustments, write-offs, provisions |
| R27 Finance Officer | R | Valuation and movement reporting |
| R03 Chief Financial Officer | R A | All; approves write-offs and adjustments above threshold |
| R32 Quality Manager / ISO Coordinator | R U | Inspection results, quarantine, recall, counterfeit flags |
| R28 Warranty Claims Officer | R | Serial genealogy and part cost for claims |
| R25 Retail / Refurbishment Officer | C R U | Refurbished-class stock only |
| R33 IT / System Administrator | R | Configuration and technical support; no transactional rights |
| R38 Brand Partner | R | Own consignment balance and reconciliation only (P08) |
| R38 Vendor | R | Own RTV records and expected credits only (P05) |

**Field-level restrictions.** `unit_cost`, `total_value`, `vendor_price` and `provision_value`
are visible only to R01–R05, R06, R17, R19, R26, R27 and R03 (per `05-04` §5). Technicians and
store keepers see quantity, location and condition, never cost. Brand partners see their own
consignment quantities and never any 1000FiX cost.

**Segregation of duties.**
- **SOD-05 enforced here:** the user who performs a count may not approve the adjustment arising from it — hard block.
- A user may not both raise and approve an inter-branch transfer above the value threshold.
- A user may not both quarantine stock and approve its write-off.
- R19 Procurement Officer has read-only stock access; procurement staff cannot adjust the balances that justify their own buying.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Network stock dashboard** | Inventory Manager, Operations Director | Real time | Live position across all 51+ locations by part, brand, class and ownership class — the explicit BR-INV-003 requirement |
| Branch stock position | Branch Manager, Store Keeper | Real time | On hand, reserved, available, in transit, below-minimum lines |
| Van stock and variance | Branch Manager, Inventory Manager | Daily | Par compliance, reconciliation completion, variance value by technician |
| Inventory accuracy | Inventory Manager, CFO, Quality Manager | Monthly | Count coverage, line accuracy, value accuracy, trend against the 98% target |
| **Brand consignment reconciliation** | Warehouse Manager, brand partner (P08), Finance | Monthly | Opening, received, consumed on warranty, returned, damaged, closing, variance |
| Ownership-class value assertion | CFO, external auditor | Monthly | Value by class with the standing assertion that non-owned classes total zero |
| Dead stock and ageing | Inventory Manager, Procurement, CFO | Monthly | Age bands, no-movement lines, provision, disposition proposals |
| ABC/XYZ and criticality | Inventory Manager, M43 planners | Quarterly | Nine-box classification with consumption value and variability |
| Stockout and unmet demand | Operations Director, Procurement | Weekly | Stockout events, jobs delayed, parts most frequently unavailable |
| Part availability at first request | Operations Director | Weekly | Requests met from the requesting location, from the network, and not met |
| Slow and fast movers | Procurement, Inventory Manager | Monthly | Turns by part and by category |
| Adjustment and write-off register | CFO, Quality Manager, Internal Audit | Monthly | Every adjustment with reason, requester, approver and value |
| Serial traceability enquiry | Warranty Claims, Quality, Legal | On demand | Full genealogy for any serial, both directions |
| Quarantine and counterfeit register | Quality Manager, Procurement | Weekly | Held stock by reason, supplier attribution, disposition |
| RTV and credit recovery | Procurement, Finance | Monthly | Returns raised, credits expected, credits received, ageing |
| Transfer performance | Logistics Manager, Inventory Manager | Weekly | Transfer volume, in-transit ageing, discrepancy rate |
| Inventory valuation pack | CFO, Finance Manager | Monthly | Value by method, class, location and entity, reconciled to the GL |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| **KPI-042** | Inventory accuracy | 75% | 96% | **98%** |
| **KPI-043** | Part availability at first request | unmeasured | 88% | **93%** |
| **KPI-044** | Stockout-caused job delays | unmeasured | < 6% | **< 3%** |
| **KPI-045** | Inventory turns per year | unmeasured | 4.5 | **6+** |
| **KPI-046** | Dead stock as % of value | unmeasured | < 8% | **< 5%** |
| **KPI-047** | Van stock variance | untracked | < 2% | **< 1%** |
| — | Consignment reconciliation variance | untracked | < 1% | **0%** |
| — | Consignment misuse incidents | unknown | **0** | **0** |
| — | Movements captured by scan | ~0% | 90% | **98%** |
| — | Cycle-count schedule adherence | n/a | 95% | **99%** |
| — | Serial capture on serial-controlled issues | ~0% | **100%** | **100%** |
| — | Reservations honoured without override | n/a | 92% | **97%** |
| — | Van reconciliation completion per shift | 0% | 95% | **99.5%** |
| — | Transfer discrepancy rate | untracked | < 2% | **< 0.5%** |
| — | RTV credits recovered as % of value raised | unknown | 80% | **95%** |
| — | Provisional-cost lines outstanding beyond 30 days | n/a | < 5% | **< 1%** |

> **Register note.** The six KPI-0nn identifiers above are the canonical ones allocated to M15
> in `06-02` §2.6. The ten unnumbered metrics are new to this specification and require
> allocation in `06-02` — recorded as an audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo 19 `stock` — quants, moves, reservations, lots and serials, FIFO/AVCO valuation, internal transfers | 24% |
| L2 | OCA `stock-logistics-warehouse` (discrepancy thresholds, lockdown, location zones), `stock-logistics-workflow`, `stock-logistics-barcode` | 30% |
| L3 | Free barcode and label-printing modules | 4% |
| L5 | `cd_stock_ext`, `cd_stock_ownership`, `cd_van_stock_control`, `cd_cycle_count`, `cd_part_availability` | 42% |

> The custom share is higher than the `02-01` §11 indication for M15. That table was written
> against the v2.0 scope, before the six ownership classes and van-stock control were made
> explicit. The re-scope moved capability *out* of M15 (to M37, M41, M43, M44) but made what
> remains materially more custom.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 3 of 5 identifiers below are claimed by another module: **CD-068** also claimed by M21; **CD-069** also claimed by M21; **CD-070** also claimed by M55. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-068 | `cd_stock_ext` — location hierarchy, status model, movement ledger, transfer lifecycle, negative-stock guard | Odoo module | 6 PW |
| CD-069 | `cd_stock_ownership` — the six ownership classes, use-permission engine, class-change control, consignment balance and reconciliation, valuation exclusion | Odoo module | 8 PW |
| CD-070 | `cd_cycle_count` — ABC-driven scheduling, blind counting, variance thresholds, adjustment approval with SoD | Odoo module | 3 PW |
| **CD-139** | `cd_van_stock_control` — van locations, par levels, replenishment triggers, offline shift reconciliation, variance escalation | Odoo module + technician-app surface | 6 PW |
| **CD-140** | `cd_part_availability` — network availability search, reservation priority engine, substitution and backorder | Odoo module + service | 4 PW |

> **CD register reallocation.** The register in `02-05` §5.2 allocated CD-067…071 to M15 as
> `cd_part_master`, `cd_stock_ext`, `cd_consignment_stock`, `cd_cycle_count`, `cd_landed_cost`.
> Under the v2.1 re-scope: `cd_part_master` (CD-067) moves to **M37**; `cd_landed_cost` (CD-071)
> moves to **M44**; `cd_consignment_stock` (CD-069) is absorbed into the broader
> `cd_stock_ownership` and retains its ID; `cd_cycle_count` retains CD-070. Two new IDs,
> **CD-139 and CD-140**, are claimed from the extension block reserved for modules M31–M67.
> **All CD IDs remain provisional** pending the unified CD register required by audit finding
> M-01 in `02-05`.
>
> **Category E CD block (for cross-module coherence).** CD-139…140 M15 · CD-141…145 M41 ·
> CD-073 + CD-146…148 M16 · CD-072 + CD-149…151 M42 · CD-152…154 M43 ·
> CD-071 + CD-074 + CD-155…156 M44.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M15 is scheduled in **W2** (P0) but declares a dependency on 1 module(s) that land later: **M19** (W3). One of three things must be true before the W2 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W2 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M15 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W2 plan for M15 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M37 Catalogue | A part must be defined before it can be stocked; compatibility and serial-control flags originate there |
| M64 MDM | Part, location and UoM governance must exist before a 10,000-SKU load |
| M29 Identity, M30 Platform Admin, M28 Integration | Platform foundation; record rules, entity/operating-unit model, event outbox |
| M33 Party Master | Brands, suppliers and customers must be identifiable to attach ownership |
| M19 Financial Accounting | Valuation events need a consumer; may be stubbed in W2 and connected in W3 |
| M16 Procurement | Goods receipt is the primary inflow; W2 accepts manual receipt, W3 connects the PO |
| M03 Logistics | Transfer movement; W2 accepts manual dispatch, W3 connects consignments |

> **Unresolved cross-wave dependency — M42 consignment terms.** M15 enforces brand consignment
> rules from **W2** (BRU-INV-01, BRU-INV-02) and §10.2 reads those terms from
> `fix.consignment.agreement`, which **M42 owns and does not deliver until W3–W4**. Either the
> consignment-agreement entity ships as a **W2 stub built under M15 with ownership transferring
> to M42 in W3**, or the terms are held as M15 configuration in W2 and migrated. This is the
> reciprocal of **Q-01 in `M42_Supplier_Relationship_and_Performance.md`** and must be resolved
> before W2 build. It does **not** block the ownership-class enforcement itself — the six classes
> and their use permissions are M15's own — only the per-brand commercial terms behind them.

**Delivers into:** M01, M02 and M31 cannot complete their W2 scope without M15. This makes M15
the binding constraint of Wave 2 alongside M01.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Branch stock spreadsheets (51+ files) | ~10,000 SKUs × up to 51 locations | `fix.stock.quant` | W2 cutover |
| Central warehouse records | ~10,000 SKUs | `fix.stock.quant` | W2 cutover |
| Van stock | 200–400 vans, unrecorded today | `fix.stock.quant` (van locations) | W2 cutover |
| Brand consignment records | 17+ brands, held by each brand | `fix.consignment.balance` | W2, brand-confirmed |
| Open RTVs and pending credits | Current only | `fix.stock.rtv` | W2 |
| Historical consumption (for M43) | 24 months where recoverable | Warehouse (M62) | W2–W3, best-effort |

> **Migration position — non-negotiable.** Opening balances are established by a **full
> physical count at cutover**, not by loading the spreadsheets. The spreadsheets are 75%
> accurate; loading them guarantees that inventory accuracy never recovers, because every
> subsequent variance is contaminated by an unknown opening error. This is recorded as a
> category-level risk in `_CATEGORY_OVERVIEW.md` §9 and is the single largest operational
> commitment M15 asks of the business: **51+ locations counted, van stock recalled and counted,
> and consignment balances confirmed with each brand, inside the cutover window.**

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every quant and every move in production carries a non-null ownership class | Database constraint plus a full-table assertion query |
| AC-02 | Consignment stock cannot be consumed on a paid repair through any path — UI, API or bulk import | Negative test suite covering all three paths |
| AC-03 | Refurbished stock cannot be consumed on a warranty job | Negative test |
| AC-04 | Inventory valuation excludes all non-owned classes, and the excluded total reconciles to the consignment and customer-supplied balances | Valuation pack reconciled to the GL by Finance |
| AC-05 | Inventory accuracy reaches 96% at Wave 4 and 98% at Wave 8, measured by independent count | Twelve consecutive monthly count cycles |
| AC-06 | Network availability for a single part across 51+ locations returns in ≤ 300 ms at p95 | Performance test at production data volume |
| AC-07 | Two concurrent reservations of the last unit resolve to one success and one clean failure | Concurrency test at 50 parallel requests |
| AC-08 | No transaction can drive a quant negative, including through the API and offline replay | Negative test and fuzz test |
| AC-09 | Van reconciliation completes offline for a full shift and synchronises with complete integrity | Offline test with 20 technicians over five shifts |
| AC-10 | An unresolved van variance above threshold blocks the technician's next parts issue | Scripted scenario |
| AC-11 | A serial-controlled part cannot be issued without a serial, and an unknown serial is quarantined | Negative test |
| AC-12 | Full serial genealogy — receipt, movements, job, technician, customer device, warranty claim — is retrievable in ≤ 500 ms | Performance and correctness test |
| AC-13 | A recall quarantines every affected unit across all locations and vans in one transaction and lists affected jobs | Scripted recall drill |
| AC-14 | The counter of a line cannot approve the adjustment arising from it | SoD negative test (SOD-05) |
| AC-15 | A count line above the variance threshold cannot be validated without recount and approval | Negative test |
| AC-16 | The monthly brand consignment reconciliation is generated automatically and accepted by at least three brand partners | Signed brand acknowledgements |
| AC-17 | A landed cost published after receipt revalues the layer and raises a delta valuation event, including where stock is already consumed | Scripted scenario with M44 |
| AC-18 | Every stock state change emits its domain event through the outbox with no loss under induced failure | Event-integrity test |
| AC-19 | Opening balances are established by physical count at every location, with signed variance reports | Cutover count records for all 51+ locations |
| AC-20 | All store keeper, warehouse and technician screens are complete in Bengali | Translation coverage report (AS-12) |
| AC-21 | Inventory Manager and Warehouse Manager sign off UAT | Signed UAT record |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 21 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which of the 17+ brands place consignment stock, on what terms, and what reconciliation cadence and format does each require? | Warehouse Manager / CCO | W2 minus 2 months |
| Q-02 | Is the physical count at cutover approved as a business commitment, including the branch downtime it requires? | Operations Director / CEO | W2 minus 3 months |
| Q-03 | FIFO or weighted average — per part category, and who decides? Is the choice acceptable to the external auditor? | CFO | W2 design |
| Q-04 | Which parts are serial-controlled? A value threshold, a category rule, or a brand mandate? | Warehouse Manager / Quality Manager | W2 build |
| Q-05 | What is the van variance value threshold for branch-manager escalation, and for blocking further issue? | Inventory Manager / CFO | W2 build |
| Q-06 | Dead-stock period and provision bands — 90, 180 or 365 days, and at what provision rates? | CFO | W2 build |
| Q-07 | Do any brands mandate their own parts-ordering portal, and can consignment balances be exchanged with it, or is it file-based? | Warehouse Manager | W3 |
| Q-08 | How many central warehouses exist today, and which branch stores are large enough to justify M41? | Warehouse Manager | W3 (M41 scoping) |
| Q-09 | Is customer-supplied-part acceptance a permitted policy, and under what liability terms? | CCO / Legal | W2 build |
| Q-10 | Who owns the physical scanner estate — is there a device standard, and what is the procurement lead time? | IT Administrator / Procurement | W2 minus 2 months |
| Q-11 | Are marketplace-seller stock positions in scope for visibility in W2, or deferred to M12 in W7? | CCO | W2 design |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §5 (the six ownership classes), §6 (boundary map), §9 (risks) ·
`M41_Warehouse_Management.md` · `M16_Procurement_and_Strategic_Sourcing.md` ·
`M42_Supplier_Relationship_and_Performance.md` · `M43_Demand_Planning_and_Replenishment.md` ·
`M44_Import_Trade_Compliance_and_Landed_Cost.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` (van stock consumption) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md` (transfer movement) ·
`02_Architecture/02-02_Module_Catalogue_Master_Register.md` §2 Category E ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §3.3, §5, §6 SOD-05, §7 ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` §2.6 (KPI-042…047), BO-03

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-INV-001 … BR-INV-015 ·
`1000FiX_Services_Company_Profile.md` §Authorized Service Partnerships (17+ brands),
§Service Infrastructure · `1000fix_business/Business planning for 1000 fix.docx`
§Refurbishment, §Recycling

**External benchmark**
SAP S/4HANA Inventory Management — special stock indicators for consignment, customer and
vendor-owned stock; stock status segregation ·
[SAP Service Parts Management](https://sapinsider.org/topic/sap-supply-chain-management/sap-spm/) ·
[SAP S/4HANA extended Service Parts Planning](https://sapinsider.org/blogs/sap-s4hana-supply-chain-for-extended-service-parts-planning/) —
multi-echelon service parts network principles ·
Oracle Fusion Cloud Inventory Management — consigned inventory with ownership transfer at
consumption, ABC-driven cycle counting ·
[Microsoft Dynamics 365 warehouse and inventory dimensions](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/warehouse-management-overview) —
the owner dimension ·
IFS Cloud — rotable pools, condition codes and core tracking
([rotable pool practice](https://supplychainplanning.ie/scor-best-practice-168-rotable-spares-pool/)) ·
[Consignment inventory accounting and segregation practice](https://www.cleverence.com/articles/for-business/consignment-inventories-4837/) —
dedicated bins/virtual locations, ownership transfer at withdrawal, balance-sheet exclusion ·
[Field-service van/trunk stock practice](https://www.fieldpulse.com/resources/blog/field-service-inventory-management) —
par levels per van, automatic replenishment, scan at point of use ·
[ABC/XYZ classification and cycle-count frequency](https://www.scmdojo.com/blog/abc-xyz-analysis-complete-guide) ·
[GS1 serialisation and traceability for anti-counterfeiting](https://blog.acviss.com/gs1-compliant-traceability-for-factory-warehouse-market) ·
[Odoo 19 inventory valuation and costing methods](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/landed_costs.html) ·
[OCA stock-logistics-warehouse](https://github.com/oca/stock-logistics-warehouse) — discrepancy
thresholds, inventory lockdown, location zones

---

*Module M15 · Category E · 1000FiX ERP System v2.0 · CONFIDENTIAL*
