---
id: FIX-ERP2-007
title: Pillar C — Supply Chain & Asset Modules (M15–M18)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Pillar C — Supply Chain & Assets
# Modules M15–M18: Features & Functions

**Pillar owner:** Supply Chain Director
**Data domain:** Materials, suppliers, assets, end-of-life
**Modules:** M15 INV · M16 SCM · M17 AST · M18 ESG

---

# M15 — Inventory & Spare Parts Management (INV)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M15 / `INV` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W2 |
| **Delivery layers** | L1 (Odoo stock) + L2 (OCA stock-logistics, barcode, operating-unit) + L5 (CD-067…071) |
| **Requirements** | FR-INV-001 … FR-INV-063 |
| **Effort** | 28 person-weeks |

## 1. Purpose

M15 knows exactly **what parts exist, where they are and what they are worth** across a
distribution network that is far more complex than a typical retailer's: 51+ service centres,
central warehouses, 200–400 technician vans, brand-owned consignment stock, marketplace
seller warehouses, refurbishment stock and rental asset pools.

Inventory accuracy is currently ~75%. The target is 98%+.

## 2. Scope Expansion Over v1.0

| v1.0 | v2.0 Addition |
|---|---|
| Multi-location + van stock | + Consignment stock owned by brand partners, + marketplace seller warehouses, + refurbishment WIP, + rental asset pool, + quarantine and e-waste locations |
| Serial tracking on high-value parts | Full genealogy: which part, from which PO, to which device, on which job, with which warranty outcome |
| Reorder alerts | Demand-forecast-driven replenishment (from M26) with lead-time and service-level parameters |
| FIFO / weighted average | + Landed cost including duty, freight and clearing; + refurbished/harvested part valuation |
| Genuine / Compatible / Refurbished classification | + Harvested (from M14) and + Brand-supplied warranty stock, with strict usage rules |
| Cycle counting | + ABC/XYZ classification driving count frequency; + perpetual count programme |
| — | Kitting and de-kitting for service kits |
| — | Shelf-life and battery-age management for date-sensitive stock |
| — | Cross-branch availability search with automatic best-source recommendation |

## 3. Functional Areas & Features

### 3.1 Item Master & Classification

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-001 | Parts catalogue | Maintain a master catalogue with part number, description (Bengali/English), manufacturer part number, category, UOM, weight and dimensions | P0 |
| FR-INV-002 | Compatibility mapping | Map each part to the device brands, models and revisions it fits, with supersession chains | P0 |
| FR-INV-003 | Part classification | Classify Genuine (OEM) · Compatible · Refurbished · Harvested · Brand-Supplied Warranty · Consumable | P0 |
| FR-INV-004 | Alternate & substitute parts | Define alternates and substitutes with precedence, used automatically when the primary is unavailable | P1 |
| FR-INV-005 | ABC/XYZ classification | Classify by value (ABC) and demand variability (XYZ) to drive stocking and counting policy | P1 |
| FR-INV-006 | Service kits | Define kits of parts and consumables per standard repair, issued and returned as a unit | P1 |
| FR-INV-007 | Shelf life & age tracking | Track manufacture date and shelf life for batteries, adhesives and thermal compounds; block issue of expired stock | P1 |

### 3.2 Stock Locations & Ownership

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-008 | Multi-location network | Manage stock at central warehouses, 51+ branches, workshops, vans, quarantine, refurbishment WIP, rental pool and e-waste holding | P0 |
| FR-INV-009 | Location hierarchy | Model warehouse → zone → aisle → rack → bin, and branch → store → shelf | P1 |
| FR-INV-010 | Van stock | Maintain a stock location per technician van with par levels, replenishment and daily reconciliation | P0 |
| FR-INV-011 | Consignment stock | Track brand-owned stock held by 1000FiX, excluded from own valuation, with usage reporting to the brand | P1 |
| FR-INV-012 | Marketplace seller stock | Hold visibility of seller-declared stock for availability display, without owning it | P2 |
| FR-INV-013 | Ownership segregation | Enforce that brand-supplied warranty stock cannot be issued to non-warranty jobs | P0 |
| FR-INV-014 | Quarantine location | Hold suspect, damaged, returned or pending-inspection stock in quarantine, unavailable for issue | P1 |

### 3.3 Stock Movement

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-015 | Goods receipt | Receive against a purchase order with quantity, batch, serial and quality-inspection step before stocking | P0 |
| FR-INV-016 | Barcode & QR operations | Perform every movement — receive, put-away, pick, issue, transfer, count — by scanning, on desktop and mobile | P0 |
| FR-INV-017 | Serial & batch capture | Capture serials and batches at receipt, issue and return where the part class requires it | P0 |
| FR-INV-018 | Reservation | Reserve stock against an approved service order; release automatically on cancellation or expiry | P0 |
| FR-INV-019 | Issue to job | Issue parts to a work order with automatic cost posting and consumption record | P0 |
| FR-INV-020 | Return from job | Return unused or wrong parts to stock with condition assessment | P1 |
| FR-INV-021 | Inter-branch transfer | Request, approve, dispatch, receive and confirm transfers between locations with in-transit visibility | P0 |
| FR-INV-022 | Van replenishment | Generate replenishment picks to restore van par levels, dispatched with the technician's schedule | P1 |
| FR-INV-023 | Van reconciliation | Reconcile van stock daily against issues and returns; escalate unexplained variance | P1 |
| FR-INV-024 | Kitting & de-kitting | Assemble and disassemble service kits with component-level traceability | P1 |
| FR-INV-025 | Scrap & write-off | Write off damaged or obsolete stock with approval and reason code, posting to M19 | P1 |

### 3.4 Availability & Replenishment

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-026 | Network availability view | Show on-hand, reserved, available and in-transit for any part across every location in one view | P0 |
| FR-INV-027 | Best-source recommendation | Recommend the best source for a required part by availability, distance, transfer cost and lead time | P1 |
| FR-INV-028 | Reorder point management | Maintain min/max and reorder points per part per location, reviewed on a schedule | P0 |
| FR-INV-029 | Replenishment alerts | Generate alerts and draft purchase requisitions when stock reaches the reorder point | P0 |
| FR-INV-030 | Demand-driven planning | Consume demand forecasts from M26 to set dynamic reorder parameters by season and location | P2 |
| FR-INV-031 | Safety stock calculation | Calculate safety stock from demand variability, lead-time variability and target service level | P2 |
| FR-INV-032 | Critical part escalation | Escalate immediately when a part required by an open SLA-bound job is unavailable anywhere | P1 |

### 3.5 Counting, Accuracy & Valuation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-033 | Cycle counting | Schedule counts by ABC class and location; capture counts on mobile; report variance | P0 |
| FR-INV-034 | Full physical count | Support periodic wall-to-wall counts with freeze, count, recount and reconciliation | P1 |
| FR-INV-035 | Variance approval | Require approval for adjustments above thresholds, with reason coding and trend analysis | P0 |
| FR-INV-036 | Accuracy measurement | Measure and report inventory accuracy by location and part class | P0 |
| FR-INV-037 | Valuation methods | Support FIFO and weighted average, configured per part category | P0 |
| FR-INV-038 | Landed cost | Include freight, duty, clearing and handling in the receipt cost of imported parts | P1 |
| FR-INV-039 | Refurbished/harvested valuation | Value harvested and refurbished parts on a defined basis, distinct from new parts | P2 |
| FR-INV-040 | Stock ledger & audit | Maintain a complete, immutable movement ledger reconcilable to the general ledger | P0 |

### 3.6 Analytics & Control

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-INV-041 | Turnover & ageing | Report turnover, days-of-supply and ageing by part, category and location | P1 |
| FR-INV-042 | Dead & slow stock | Identify non-moving stock with configurable thresholds; recommend transfer, return or write-off | P1 |
| FR-INV-043 | Stockout analysis | Report stockout frequency, duration, jobs delayed and revenue impact | P1 |
| FR-INV-044 | Consumption analysis | Report consumption by device model, fault code, technician and branch to inform stocking | P1 |
| FR-INV-045 | Defective part returns | Track parts returned to vendor (RTV) with RMA reference, credit expectation and ageing | P1 |
| FR-INV-046 | Shrinkage analysis | Analyse unexplained losses by location and person, feeding M23 | P2 |

*(FR-INV-047 … FR-INV-063 cover warehouse mobile operations, put-away strategies, bin
optimisation, hazardous-material handling for batteries, import tracking and inventory
analytics — catalogued in Doc 11.)*

## 4. Key Entities

`fix.part` · `fix.part.compatibility` · `fix.part.supersession` · `fix.part.class` ·
`fix.service.kit.def` · `fix.stock.location` · `fix.van.stock` · `fix.consignment.stock` ·
`fix.stock.move` (ext) · `fix.stock.reservation` · `fix.transfer.request` ·
`fix.cycle.count` · `fix.count.variance` · `fix.landed.cost` · `fix.rtv.record` ·
`fix.stock.alert` · `fix.replenishment.param`

## 5. Automations

| ID | Trigger | Action |
|---|---|---|
| AUT-INV-01 | Stock ≤ reorder point | Alert inventory manager; draft purchase requisition in M16 |
| AUT-INV-02 | Estimate approved | Reserve required parts; if unavailable, raise a sourcing task and hold the job |
| AUT-INV-03 | Part issued to job | Deduct stock, post cost, update device parts genealogy |
| AUT-INV-04 | End of technician shift | Van reconciliation; variance report to branch manager |
| AUT-INV-05 | Goods receipt failed inspection | Move to quarantine; notify procurement; raise a vendor quality record in M23 |
| AUT-INV-06 | Part unavailable network-wide for an SLA job | Escalate to procurement and operations; notify the customer with a revised ETA |
| AUT-INV-07 | Dead stock threshold reached | Generate a disposition recommendation (transfer / return / discount / write-off) |
| AUT-INV-08 | Warranty part consumed | Record against the brand consignment ledger for reconciliation in M09 |

## 6. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Inventory accuracy | 75% | 98%+ |
| Part availability at first request | unmeasured | > 93% |
| Stockout-caused job delays | unmeasured | < 3% of jobs |
| Inventory turns | unmeasured | > 6 per year |
| Dead stock as % of value | unmeasured | < 5% |
| Van stock variance | untracked | < 1% |
| Days of supply (A-class parts) | unmeasured | 18–28 days |

---

# M16 — Procurement, Vendor & Supplier Management (SCM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M16 / `SCM` |
| **Status** | Expanded |
| **Priority** | P1 |
| **Wave** | W3 |
| **Delivery layers** | L1 (Odoo purchase) + L2 (OCA purchase-workflow) + L5 (CD-072…074) |
| **Requirements** | FR-SCM-001 … FR-SCM-040 |
| **Effort** | 18 person-weeks |

## 1. Purpose

M16 buys everything the Company consumes — spare parts, consumables, rental assets, tools,
IT, services and sub-contracted labour — and manages the vendors who supply them, including
import supply chains for genuine parts.

## 2. Functional Areas & Features

### 2.1 Vendor Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SCM-001 | Vendor master | Maintain vendors with classification (OEM · authorised distributor · local supplier · importer · service provider · sub-contractor), contacts, banking, tax IDs and terms | P1 |
| FR-SCM-002 | Vendor onboarding | Run a structured onboarding with document collection, verification, approval and system activation | P1 |
| FR-SCM-003 | Vendor qualification | Assess and record vendor capability, capacity, certifications and financial standing | P2 |
| FR-SCM-004 | Vendor catalogue & price lists | Maintain vendor-specific catalogues, prices, lead times, MOQs and validity | P1 |
| FR-SCM-005 | Vendor contracts | Record supply agreements with pricing, volume commitments, SLAs and expiry alerts | P2 |
| FR-SCM-006 | Vendor performance scorecard | Score on-time delivery, quality rejection rate, price competitiveness, responsiveness and documentation accuracy | P1 |
| FR-SCM-007 | Vendor risk & compliance | Track single-source risk, compliance documents and blacklist status | P2 |

### 2.2 Purchase-to-Pay

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SCM-008 | Purchase requisition | Raise requisitions manually or automatically from replenishment alerts, with justification and budget check | P1 |
| FR-SCM-009 | Requisition approval | Route through a configurable approval matrix by value, category and cost centre | P1 |
| FR-SCM-010 | RFQ / tendering | Issue RFQs to multiple vendors, receive and compare quotations on price, lead time and terms | P2 |
| FR-SCM-011 | Purchase order | Convert an approved requisition or quotation into a PO with terms, delivery schedule and tax treatment | P1 |
| FR-SCM-012 | PO transmission & acknowledgement | Send POs to vendors by portal, email or API and track acknowledgement | P1 |
| FR-SCM-013 | Advance shipping notice | Receive ASNs from vendors to pre-stage receiving | P3 |
| FR-SCM-014 | Goods receipt & inspection | Receive against the PO with quantity verification and quality inspection, routing failures to quarantine | P1 |
| FR-SCM-015 | Three-way matching | Match PO, GRN and vendor invoice; block payment on mismatch beyond tolerance | P0 |
| FR-SCM-016 | Invoice processing | Capture vendor invoices (including OCR from PDF), validate, approve and post to M19 accounts payable | P1 |
| FR-SCM-017 | Payment scheduling | Schedule payments by terms, take early-payment discounts and manage cash impact | P1 |
| FR-SCM-018 | Debit notes & claims | Raise debit notes for short delivery, quality rejection and price variance | P1 |

### 2.3 Import & Landed Cost

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SCM-019 | Import order tracking | Track international orders through proforma, LC/TT, shipment, arrival, customs and clearance | P2 |
| FR-SCM-020 | Letter of credit management | Record LC details, amendments, documents and expiry | P2 |
| FR-SCM-021 | Customs & duty | Record HS codes, duty, VAT at import, clearing agent charges and demurrage | P2 |
| FR-SCM-022 | Landed cost allocation | Allocate freight, duty and clearing charges across received items to arrive at true unit cost | P2 |
| FR-SCM-023 | Shipment visibility | Track shipments with expected arrival and delay alerts affecting downstream availability | P2 |

### 2.4 Sub-Contracting & Services Procurement

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SCM-024 | Service purchase orders | Purchase services (specialist repair, logistics, facilities, professional services) with milestone-based receipt | P2 |
| FR-SCM-025 | Sub-contract work orders | Send repair work to external specialists with scope, price, SLA and quality requirements | P2 |
| FR-SCM-026 | Sub-contract custody | Track devices sent to sub-contractors through M03 with full custody evidence | P1 |
| FR-SCM-027 | Marketplace seller as supplier | Treat qualified marketplace sellers as a supplier class for overflow capacity, with purchase and settlement flows | P2 |

*(FR-SCM-028 … FR-SCM-040 cover budget control, catalogue punch-out, blanket orders,
procurement analytics and supplier collaboration through P05 — catalogued in Doc 11.)*

## 3. Key Entities

`fix.vendor.profile` · `fix.vendor.qualification` · `fix.vendor.scorecard` ·
`fix.vendor.pricelist` · `fix.purchase.requisition` · `fix.rfq` · `fix.rfq.response` ·
`fix.purchase.order` (ext) · `fix.grn` · `fix.inspection.result` · `fix.three.way.match` ·
`fix.debit.note` · `fix.import.order` · `fix.letter.of.credit` · `fix.landed.cost.allocation` ·
`fix.subcontract.order`

## 4. KPIs

| KPI | Target |
|---|---|
| Vendor on-time delivery | > 92% |
| Goods inspection rejection rate | < 2% |
| PO cycle time (requisition to PO) | < 24 hours |
| Three-way match exception rate | < 5% |
| Price variance vs contracted price | < 1% |
| Emergency/spot purchases | < 8% of spend |
| Import clearance cycle time | Baselined W3, −20% by W6 |

---

# M17 — Asset, Device Registry & IoT Telemetry (AST)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M17 / `AST` |
| **Status** | Expanded (promoted from a v1.0 sub-feature) |
| **Priority** | P1 |
| **Wave** | W2 (registry) → W8 (IoT/telemetry) |
| **Delivery layers** | L2 (OCA fieldservice_equipment) + L4 (TimescaleDB) + L5 (CD-075…079) |
| **Requirements** | FR-AST-001 … FR-AST-042 |
| **Effort** | 25 person-weeks |

## 1. Purpose

Everything the Company touches is an asset with an identity and a history. M17 is the single
registry for:

- **Customer-owned devices** — the 200,000+ devices in the service history
- **Corporate asset estates** — the bulk-registered fleets described in the Service App SOW
- **Rental pool assets** — owned by 1000FiX, rented out
- **Refurbished units** — acquired, reworked, resold
- **Monitored assets** — client IT estates under managed-service contracts
- **Internal assets** — tools, test equipment, vehicles, branch equipment, IT

Every service order, warranty claim, contract entitlement and predictive model depends on this.

## 2. Functional Areas & Features

### 2.1 Asset Registry

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-001 | Unified asset record | Register every asset with a unique identity (serial, IMEI, MAC, asset tag), category, brand, model, specification and current owner | P0 |
| FR-AST-002 | Asset categories | Model IT equipment, mobile devices, home appliances, network equipment, medical equipment, tools and vehicles with category-specific attributes | P0 |
| FR-AST-003 | Brand & model master | Maintain brand, model, revision and specification masters used across service, parts compatibility and warranty rules | P0 |
| FR-AST-004 | Identity resolution | Resolve an asset from any identifier — serial, IMEI, asset tag, QR label, or model plus customer | P0 |
| FR-AST-005 | Asset labelling | Generate and print durable QR/barcode asset labels; support customer-supplied asset tags | P1 |
| FR-AST-006 | Bulk registration | Register asset estates in bulk from CSV/Excel with validation, de-duplication and error reporting | P1 |
| FR-AST-007 | Ownership & custody | Track legal owner and current custodian separately; record every transfer | P0 |
| FR-AST-008 | Asset lifecycle status | Track In Use · In Service · In Transit · In Storage · Rented Out · Under Refurbishment · Retired · Recycled · Lost | P1 |

### 2.2 Asset History & Genealogy

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-009 | Complete service history | Show every service order, work order, fault, part replaced and technician for the asset's whole life | P0 |
| FR-AST-010 | Parts genealogy | Record which specific part (with its serial and source PO) was fitted to which asset, when and by whom | P1 |
| FR-AST-011 | Warranty history | Show manufacturer warranty, extended warranty, repair warranties and claim history | P0 |
| FR-AST-012 | Cost of ownership | Accumulate total service cost per asset and compare to replacement value | P2 |
| FR-AST-013 | Condition history | Track condition grade over time from intake inspections, rental returns and refurbishment | P2 |
| FR-AST-014 | Provenance report | Produce a shareable asset history report — used at resale, for corporate audits and for disputes | P2 |

### 2.3 Corporate Asset Estate Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-015 | Estate structure | Organise a client's assets by company → location → department → user | P1 |
| FR-AST-016 | Contract coverage mapping | Map assets to the contracts and entitlements that cover them | P1 |
| FR-AST-017 | Estate self-service | Let corporate customers view, add, retire and reassign their assets in the B2B portal | P1 |
| FR-AST-018 | Estate reconciliation | Reconcile the client's declared asset list against assets actually seen in service | P2 |
| FR-AST-019 | Refresh planning | Report asset age profile and recommend refresh cycles, feeding sales opportunities | P2 |
| FR-AST-020 | Decommission projects | Manage bulk decommissioning with data destruction (M06), buy-back (M14) and recycling (M18) | P2 |

### 2.4 Maintenance Planning

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-021 | Maintenance plans | Define calendar-based, usage-based and condition-based maintenance plans per asset class | P1 |
| FR-AST-022 | Automatic work generation | Generate preventive work orders at the right lead time, respecting contract entitlements | P1 |
| FR-AST-023 | Calibration management | Track calibration schedules, certificates and due dates for medical and test equipment | P2 |
| FR-AST-024 | Compliance inspections | Schedule and record statutory or contractual inspections with evidence | P2 |

### 2.5 IoT & Telemetry (Wave 8)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-025 | Telemetry ingestion | Ingest device telemetry from monitoring agents, IoT gateways and connected appliances into a time-series store | P2 |
| FR-AST-026 | Telemetry model | Define per asset class which signals are collected, at what frequency and with what retention | P2 |
| FR-AST-027 | Threshold alerting | Raise alerts on threshold breach, mapped to service or MSP tickets | P2 |
| FR-AST-028 | Health index | Compute an asset health index from telemetry, service history and age | P2 |
| FR-AST-029 | Failure prediction | Consume predictive-maintenance models from M26 to forecast likely failure and recommend intervention | P2 |
| FR-AST-030 | Proactive service offer | Convert a prediction into a proactive customer contact and a scheduled service opportunity | P3 |
| FR-AST-031 | Telemetry privacy | Collect only agreed signals, disclose collection to the customer and honour opt-out | P0 |

### 2.6 Internal Assets

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-AST-032 | Tool & equipment register | Register workshop tools, test equipment and diagnostic devices with assignment and calibration | P2 |
| FR-AST-033 | Tool issue & return | Issue tools to technicians and branches with accountability and return tracking | P2 |
| FR-AST-034 | Vehicle register | Register service vehicles with documents, servicing, fuel and GPS device linkage | P2 |
| FR-AST-035 | Internal IT asset register | Track company IT assets, licences and assignment | P3 |
| FR-AST-036 | Fixed asset linkage | Link capitalised assets to their fixed-asset and depreciation records in M19 | P1 |

*(FR-AST-037 … FR-AST-042 cover asset search and analytics, asset APIs for portals, and
asset data-quality management — catalogued in Doc 11.)*

## 3. Key Entities

`fix.asset` · `fix.asset.category` · `fix.brand` · `fix.model` · `fix.asset.identifier` ·
`fix.asset.ownership` · `fix.asset.custody` · `fix.asset.status.history` ·
`fix.asset.service.history` · `fix.part.genealogy` · `fix.asset.estate` ·
`fix.maintenance.plan` · `fix.calibration.record` · `fix.telemetry.stream` ·
`fix.telemetry.point` · `fix.asset.health` · `fix.failure.prediction` · `fix.tool.register`

## 4. KPIs

| KPI | Target |
|---|---|
| Devices with complete registry data | > 95% |
| Assets identified at intake without manual entry | > 90% |
| Corporate estates reconciled | > 90% of contracted estates |
| Preventive work generated on schedule | 100% |
| Calibration compliance | 100% |
| Predicted failures confirmed (precision) | > 70% by W8 end |

---

# M18 — E-Waste, Recycling & Sustainability (ESG)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M18 / `ESG` |
| **Status** | ★ New in v2.0 |
| **Priority** | P3 |
| **Wave** | W8 |
| **Delivery layers** | L5 (CD-080…082) |
| **Requirements** | FR-ESG-001 … FR-ESG-026 |
| **Effort** | 13 person-weeks |

## 1. Purpose

The business plan commits the Company to responsible e-waste handling: designated collection
points, assessment for refurbishment, certified recycling partners, secure destruction,
regulatory compliance, component and material recovery, and public awareness.

Two things make this a system requirement rather than a policy statement:

1. **Compliance evidence.** Handling e-waste without documented disposal creates regulatory
   and reputational exposure.
2. **Data risk.** Every recycled device may hold customer data. Destruction must be certified.

M18 is also a modest revenue line through material recovery and corporate disposal contracts.

## 2. Functional Areas & Features

### 2.1 Collection

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ESG-001 | Collection channels | Accept end-of-life devices from customer drop-off at branches, scheduled home collection, corporate bulk decommission, internal write-off and unrepairable service outcomes | P3 |
| FR-ESG-002 | Collection booking | Let customers book a collection or drop-off through the portal with incentives (points, vouchers) | P3 |
| FR-ESG-003 | Collection event record | Record every item received with source, weight, category, condition and photographs | P2 |
| FR-ESG-004 | Custody from collection | Create a consignment in M03 for every movement of e-waste with chain-of-custody evidence | P2 |
| FR-ESG-005 | Corporate disposal contracts | Manage contracted bulk disposal with reconciliation against the client's asset list and per-unit certification | P3 |

### 2.2 Triage & Disposition

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ESG-006 | Triage assessment | Assess each item for refurbishment (route to M14), parts harvesting (route to M15), or recycling | P2 |
| FR-ESG-007 | Disposition decision log | Record the disposition decision with the assessor, criteria and evidence | P2 |
| FR-ESG-008 | Parts harvesting | Track components harvested from a unit into inventory with a harvested classification | P2 |
| FR-ESG-009 | Data destruction gate | Require a certified wipe or physical destruction record from M06 before any item leaves for recycling or resale | P0 |

### 2.3 Recycling & Material Recovery

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ESG-010 | Recycling partner register | Register certified recycling partners with their certifications, accepted material classes and expiry dates | P2 |
| FR-ESG-011 | Recycling batch | Group items into batches by material class for transfer to a partner | P3 |
| FR-ESG-012 | Transfer documentation | Produce transfer notes, manifests and hazardous-material declarations | P2 |
| FR-ESG-013 | Disposal certificates | Receive, store and index certificates of disposal from partners, linked to individual items where possible | P0 |
| FR-ESG-014 | Material recovery accounting | Record recovered material weights and values (metals, boards, plastics) and the resulting income | P3 |
| FR-ESG-015 | Hazardous material handling | Apply specific handling, storage and transport rules for batteries, CRTs, refrigerant and mercury-containing items | P1 |

### 2.4 Compliance & ESG Reporting

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-ESG-016 | Regulatory register | Maintain the applicable e-waste and environmental regulations and the Company's obligations under each | P2 |
| FR-ESG-017 | Compliance reporting | Produce statutory returns on volumes collected, treated and disposed | P2 |
| FR-ESG-018 | Audit evidence pack | Assemble an evidence pack per period for regulators, brand partners and ISO 14001 readiness | P2 |
| FR-ESG-019 | Carbon & impact metrics | Estimate avoided emissions and diverted waste from refurbishment and recycling | P3 |
| FR-ESG-020 | Sustainability dashboard | Publish internal and external ESG metrics — devices diverted from landfill, materials recovered, refurbishment rate | P3 |
| FR-ESG-021 | Awareness campaigns | Run and measure customer awareness campaigns through M10 | P3 |

*(FR-ESG-022 … FR-ESG-026 cover donation programmes, refrigerant recovery logs, and
supplier ESG assessment — catalogued in Doc 11.)*

## 3. Key Entities

`fix.ewaste.collection` · `fix.ewaste.item` · `fix.triage.assessment` ·
`fix.recycling.partner` · `fix.recycling.batch` · `fix.transfer.note` ·
`fix.disposal.certificate` · `fix.material.recovery` · `fix.hazmat.record` ·
`fix.esg.metric`

## 4. KPIs

| KPI | Target |
|---|---|
| Devices collected per year | 25,000 by W9 |
| Diversion from landfill | > 92% of collected units |
| Refurbishment rate of collected units | > 30% |
| Disposal certificates on file | 100% of recycled units |
| Data destruction before disposal | 100% |
| Material recovery income | BDT 12 lac/year at steady state |

---

*Next document: `08_Pillar_D_Finance_People_Governance_Modules.md`*
