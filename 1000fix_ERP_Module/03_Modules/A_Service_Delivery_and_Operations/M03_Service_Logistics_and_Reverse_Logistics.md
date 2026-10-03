---
id: FIX-ERP2-M03
module_id: M03
module_code: LOG
module_name: Service Logistics & Reverse Logistics
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Logistics Manager
system_owner: Service Squad
priority: P1
wave: W3
---

# M03 — Service Logistics & Reverse Logistics
### Category A · Code `LOG` · New in v2.0, retained in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M03 |
| **Module code** | `LOG` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (introduced in v2.0, retained unchanged in v2.1) |
| **Priority** | **P1** |
| **Delivery wave** | W3 (Months 9–13) |
| **Business owner** | Logistics Manager |
| **System owner** | Service Squad |
| **Delivery layers** | L5 (custom + Flutter rider app) with L4 mapping and routing services |
| **Custom modules** | `cd_consignment`, `cd_custody`, `cd_courier`, `cd_rider`, `cd_logistics_charge` |
| **Requirement range** | FR-LOG-001 … FR-LOG-042 |
| **Requirement count** | 42 |
| **Effort estimate** | 22 person-weeks |
| **Depends on** | M01 Service Order · M17 Asset Registry · M33 Party Master · M29 Identity · M24 Documents |
| **Depended on by** | M01, M31, M13, M14, M15, M16, M18, M20, M23, M38, M12, M06, M41 |

---

## 2. Purpose

M03 owns **every physical movement of every item**, and the unbroken chain of custody that
proves who held it and when.

A device collected from a customer's home in Uttara, taken to a Mirpur branch, sent to a
Dhaka workshop for board-level repair, returned to the branch and delivered back to the
customer has passed through six pairs of hands. Today that journey is coordinated by phone
and recorded nowhere. When a device is lost or damaged in transit — and at this volume, some
will be — there is no evidence of where it went wrong, and the dispute is settled by
argument rather than record.

### Why It Exists

Pick & drop is a headline service in the Company profile, offered for laptops, desktops and
printers. Reverse logistics is the physical backbone of four other business lines: rental
delivery and collection, trade-in intake, refurbishment movement and e-waste collection. Parts
returns to vendors, inter-branch transfers and sub-contractor movements all rely on it.

Without M03, all of it stays on WhatsApp.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Company Profile §Pick & Drop Service | "Device pickup from home/office, repair at service center, return delivery to customer — available for laptops, desktops, and printers" |
| Business Plan §Rental Services | "Easy pick-up and drop-off options at their service centers or delivering the devices directly to the customer's location" |
| Service App SOW §Logistics team Interface | "The logistics and shipping team will have a real-time dashboard of pending orders, delivered/cancelled… schedule / re-schedule option… service center-wise separate/central logistics team assignment" |
| Service App SOW §Shipping | "Distance-based delivery charge or shipping cost — within the same area, within the country, or outside the country" |
| Service App SOW §Technology | "QR and OTP features in different steps of financial transactions, service initiation/completion" |
| ERP BRD BR-FSM-015 | "Pick & drop service lifecycle: pickup scheduled → picked up → in repair → completed → delivery scheduled → delivered" |
| Business Plan §Recycling | Collection of end-of-life devices requires movement with documented custody |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Consignment creation from every source: pick & drop, rental, transfer, return, collection, fulfilment |
| 2 | Multi-leg journey modelling with per-leg carrier, status and evidence |
| 3 | Item manifest with serials, declared value, condition and photographs |
| 4 | Chain of custody: scan-plus-identity at every handover |
| 5 | Proof of collection and proof of delivery with OTP, signature and photograph |
| 6 | The immutable custody ledger |
| 7 | Packaging, sealing and tamper detection |
| 8 | Pickup and delivery scheduling with time windows |
| 9 | Rider assignment, route manifest and the rider mobile application |
| 10 | Courier partner onboarding, booking, status ingestion and reconciliation |
| 11 | Distance and zone-based logistics charging, and entitlement-based waiver |
| 12 | Reverse flows: return to vendor, return to origin, recycling transfer |
| 13 | Cash on delivery collection and reconciliation |
| 14 | Loss, damage and insurance claim management |
| 15 | Hub operations, load planning and consolidated movements |
| 16 | Logistics cost allocation and carrier performance measurement |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Service order state and customer promise | **M01** | One customer-facing record; movement is a step within it |
| Repair execution | **M31** | Movement stops at the workshop door |
| Field technician routing to a job | **M02** | A technician visit is service, not a movement of goods |
| Stock quantity, ownership and valuation | **M15** | M03 moves items; M15 knows what they are worth |
| Warehouse bin, put-away and picking | **M41** | Inside a warehouse is warehouse execution, not logistics |
| Vehicle documents, servicing, fuel, telematics | **M46** | Vehicles are enterprise assets |
| Rider employment, roster and pay | **M21** / **M55** / **M56** | People management is Category H |
| Customer notification delivery | **M27** | M03 raises events; M27 sends |
| Invoice for the logistics charge | **M20** | Only Category G creates financial documents |
| Recycling partner certification and disposal certificates | **M18** | M03 moves the batch; M18 owns compliance |
| Data destruction before disposal | **M06** | M03 will not move an item to recycling without the certificate |

### 3.3 Shared Concepts

| Concept | M03's Role | Owning Module |
|---|---|---|
| Consignment | Owns | M03 |
| Custody event | Owns the ledger; other modules raise events into it | M03 |
| Asset / device | Reads identity; records location and custody | M17 |
| Part | Moves; does not value | M15 |
| Service order | Parent context for pick & drop | M01 |
| Rental agreement | Parent context for rental movement | M13 |
| Courier partner | Owns the operational relationship; M42 owns the commercial one | M03 / M42 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Oracle Logistics (Transportation Management)** | Shipment, leg, carrier selection, rate management, freight audit | Multi-leg shipment model; carrier rate cards; freight reconciliation | Full TMS optimisation depth — our movements are short-haul and low-complexity |
| **SAP Transportation Management** | Freight order, execution, event management | Event-driven execution tracking | — |
| **Enterprise reverse-logistics practice (mobile/IT)** | RMA issued → device scanned on arrival → serialised asset tag → chain-of-custody log opened → follows the device through every stage → certified erasure → tamper-proof certificate | **The entire pattern.** This is the single most influential external reference for M03 | — |
| **NIST SP 800-88 traceability framework** | Linked records and transportation-stage documentation supporting chain of custody | The principle that custody records must link across transport stages, not just at endpoints | — |
| **Courier/last-mile platforms (Pathao, RedX, Steadfast)** | Booking API, tracking webhooks, POD capture, COD reconciliation | API-based booking, webhook status ingestion, COD reconciliation as a first-class flow | Their consumer-parcel assumptions — our items are high-value and serialised |
| **Depot repair reverse logistics (ServiceMax, QAD)** | RMA-driven inbound to depot, refurbish, return to stock | RMA reference carried through the movement | — |

**Design position.** Three deliberate differences.

First, **custody is the product, not the tracking**. Consumer parcel platforms optimise for
delivery speed and treat custody loosely. 1000FiX takes possession of customers' laptops
containing their data and their businesses. Every handover requires a scan **plus** an
identity capture from both parties — not a signature scribble on a handheld.

Second, **the item, not the parcel, is the unit of record**. A consignment may contain three
devices with three serials, three declared values and three destinations. Custody attaches to
the item, so a device can be traced even after its consignment is split.

Third, **charging and entitlement are joined at the point of movement**. Whether a customer
pays for pick & drop depends on their contract, warranty terms and Privilege tier. Calculating
that at invoice time, days later, is how disputes are created; M03 resolves it when the
consignment is created.

---

## 5. Functional Areas & Features

### 5.1 Consignment Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOG-001 | Consignment creation | Create a consignment from any source: pick & drop request, rental delivery or collection, inter-branch transfer, vendor return, recycling collection, refurbishment intake, marketplace fulfilment, sub-contractor movement | P1 | L5 |
| FR-LOG-002 | Multi-leg journeys | Model a journey as ordered legs — customer → branch → workshop → branch → customer — each with its own carrier, window, status and evidence | P1 | L5 |
| FR-LOG-003 | Item manifest | List every item with serial, description, declared value, condition grade and photographs; custody attaches to the item | P1 | L5 |
| FR-LOG-004 | Packaging and sealing | Record packaging type, seal or tamper-tag number, weight and dimensions | P2 | L5 |
| FR-LOG-005 | Consignment lifecycle | Enforce the state model (see §8) with guards at every transition | P1 | L5 |
| FR-LOG-038 | Consolidated movements | Consolidate multiple items travelling the same route into one physical movement while preserving per-item custody | P2 | L5 |
| FR-LOG-039 | Scheduled inter-branch runs | Operate scheduled shuttle runs between branches and hubs with a standing manifest | P2 | L5 |

### 5.2 Chain of Custody

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOG-006 | Custody handover | Require a scan plus identity capture from both parties at every handover, with GPS and timestamp | P1 | L5 |
| FR-LOG-007 | Proof of collection | Capture the customer's signature, a photograph of the sealed package and OTP verification at collection | P1 | L5 |
| FR-LOG-008 | Proof of delivery | Capture recipient identity, signature, photograph and OTP at delivery | P1 | L5 |
| FR-LOG-009 | Custody ledger | Maintain an immutable, queryable ledger per item recording who held it, when and where | **P0** | L5 |
| FR-LOG-010 | Tamper and discrepancy | Record seal breaks, weight discrepancies and condition changes; raise an incident automatically and block onward movement pending review | P1 | L5 |
| FR-LOG-011 | High-value handling | Apply enhanced controls above a declared-value threshold: dual signature, insurance flag, escort or restricted carrier | P2 | L5 |
| FR-LOG-036 | Recipient authorisation | Allow a customer to nominate an alternative recipient, verified at delivery | P2 | L5 |
| FR-LOG-037 | Restricted items | Flag and control movement of lithium batteries, refrigerant and other restricted items; only certified carriers may accept them | P1 | L5 |

### 5.3 Scheduling & Rider Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOG-012 | Pickup and delivery scheduling | Offer time windows by area, honouring rider capacity and cut-off times | P1 | L5 |
| FR-LOG-013 | Rider assignment | Assign to an internal rider or an external courier partner based on area, declared value, item size and cost | P1 | L5 |
| FR-LOG-014 | Route manifest | Build the rider's daily manifest with an optimised sequence | P1 | L5 |
| FR-LOG-015 | Rescheduling | Reschedule at customer or operational request with notification and SLA adjustment | P1 | L5 |
| FR-LOG-016 | Central versus branch logistics | Support both a central logistics team and branch-assigned riders, configurable per area | P1 | L5 |
| FR-LOG-027 | Rider mobile application | Provide the full rider workflow offline with queued synchronisation | P1 | L5 |
| FR-LOG-028 | Hub operations | Manage sorting, staging and dispatch at logistics hubs | P2 | L5 |
| FR-LOG-029 | Load planning | Plan rider loads by weight, volume and declared-value limits | P2 | L5 |
| FR-LOG-034 | Delivery windows | Offer and honour committed delivery windows, measuring attainment | P1 | L5 |
| FR-LOG-035 | Address validation | Validate and geocode addresses, learning from previously successful deliveries | P1 | L4 |

### 5.4 Courier Partner Integration

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOG-017 | Partner onboarding | Register courier partners with service areas, rate cards, SLAs, restricted-item certification and API credentials | P2 | L5 |
| FR-LOG-018 | Booking API | Book a consignment with a partner and receive their tracking reference | P2 | L5 |
| FR-LOG-019 | Status ingestion | Ingest partner tracking events by webhook or polling and map them to internal states and custody events | P2 | L5 |
| FR-LOG-020 | Partner reconciliation | Reconcile partner invoices against consignments delivered and contracted rate cards | P2 | L5 |
| FR-LOG-021 | Cross-border shipping | Support international shipments with customs documentation and distance-based charging | P3 | L5 |
| FR-LOG-041 | Carrier performance | Score internal riders and external couriers on cost, on-time performance, damage rate and POD completeness | P1 | L5 |

### 5.5 Charging, Reverse Flows & Exceptions

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-LOG-022 | Distance and zone charging | Calculate the customer's logistics charge by zone, distance, weight, declared value and service level | P1 | L5 |
| FR-LOG-023 | Entitlement waiver | Waive charges automatically where contract, warranty terms or Privilege tier entitle the customer | P1 | L5 |
| FR-LOG-024 | Return to vendor | Move defective parts back to vendors with RMA references and credit tracking | P1 | L5 |
| FR-LOG-025 | Recycling transfer | Move end-of-life devices to certified recycling partners, blocked until the data destruction certificate exists | P2 | L5 |
| FR-LOG-026 | Failed delivery | Apply the re-attempt policy, then return to origin with the applicable charge rules | P1 | L5 |
| FR-LOG-030 | Cash on delivery | Collect and reconcile cash on delivery per rider per shift | P1 | L5 |
| FR-LOG-031 | Insurance and declared value | Record declared value and apply insurance where taken | P2 | L5 |
| FR-LOG-032 | Loss and damage claims | Manage claims for lost or damaged consignments through to settlement, using the custody ledger as evidence | P1 | L5 |
| FR-LOG-033 | Customer rescheduling | Allow the customer to reschedule a collection or delivery from the tracking link | P1 | L5 |
| FR-LOG-040 | Cost allocation | Allocate logistics cost to the job, contract or business line that caused it | P1 | L5 |
| FR-LOG-042 | Logistics analytics | Report volume, cost per consignment, on-time performance and exception causes | P1 | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Append-only custody ledger** | Custody events are insert-only; correction is a compensating entry, never an update or delete |
| T-02 | **Item-level traceability** | Custody attaches to the item, surviving consignment split, merge and re-routing |
| T-03 | **Dual-party capture** | Every handover records both parties' identities; a single-party record is invalid and rejected |
| T-04 | **Offline rider operation** | The rider app operates for a full shift without connectivity, queueing all scans and evidence |
| T-05 | **OTP generation and validation** | Time-limited, single-use OTPs delivered to the customer's registered number, validated server-side |
| T-06 | **Evidence integrity** | POD and POC photographs are hashed at capture; the hash is stored with the custody event |
| T-07 | **Idempotent webhook ingestion** | Courier partner webhooks are signature-verified, replay-protected and idempotent |
| T-08 | **Geocoding cache with learning** | Successful delivery coordinates are retained and preferred over geocoder output on repeat visits |
| T-09 | **Charge determinism** | The logistics charge is computed at consignment creation and stored with its inputs, so it can be explained later |
| T-10 | **Event emission** | Every custody and status change emits through the transactional outbox |
| T-11 | **Barcode/QR generation** | Consignment and item labels are generated as scannable codes printable on thermal label printers |
| T-12 | **Performance** | Consignment creation ≤ 400 ms; rider manifest load ≤ 3 s on 3G; custody ledger query for one item ≤ 200 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M03 |
|---|---|---|
| **Logistics coordinator** | Coordinates by phone and WhatsApp; no dashboard; discovers problems when someone complains | Real-time dashboard of pending, in transit, delivered and exception consignments, exactly as the SOW specified |
| **Rider** | Carries a paper list; no proof of anything | Scannable manifest, scan-based handover, OTP and signature capture, offline-capable |
| **Branch staff** | Hands a device to whoever turns up | Scans the handover, and the record proves it left their custody |
| **Workshop** | Receives devices with no consistent paperwork | Books in against a consignment; discrepancies flagged immediately |
| **Customer** | No idea where their device is between collection and return | Tracking link showing custody state and expected return |
| **Finance** | Cannot allocate logistics cost or reconcile courier invoices | Cost allocated to the causing job; courier invoices reconciled to delivered consignments |
| **Legal / claims** | A lost device is settled by argument | The custody ledger names who held it last, when and where |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Pick & drop scalability** | A phone-coordinated service cannot exceed the coordinator's memory; a system-run one scales linearly | Unlocks pick & drop as a growth channel rather than a favour |
| **Loss and damage reduction** | Custody accountability changes behaviour: people are careful when the record names them | Target loss/damage **< 0.1% of consignments** |
| **Dispute cost avoidance** | Evidence replaces argument | Each avoided high-value dispute saves BDT 40,000–150,000 plus the relationship |
| **Logistics cost reduction** | Route sequencing, consolidation, carrier selection by cost, and cost visibility per movement | **−15% cost per consignment** by Wave 6 |
| **Enables four business lines** | Rental delivery, trade-in intake, refurbishment movement and e-waste collection all depend on M03 | Precondition for **BDT 190 lac/year** across M13, M14 and M18 |
| **Vendor credit recovery** | RTV movements tracked to credit, so defective-part credits are not lost | Recovers value currently written off silently |
| **Charge capture** | Logistics charges calculated at movement, not reconstructed at invoicing | Closes an untracked revenue leak |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Legal defensibility** | For a company holding customers' business laptops, the ability to prove custody is a material risk control |
| **Data protection assurance** | A device in transit holds the customer's data; documented custody is part of the ISO 27001 story |
| **Regulatory compliance** | E-waste movement requires transfer documentation; restricted items require certified handling |
| **Insurance position** | Documented declared values and custody records materially improve insurability and claim outcomes |
| **Corporate client confidence** | A corporate client decommissioning 300 assets will ask how custody is proven; this is a tender question |
| **Operational discipline** | Scan-based handover eliminates the "I gave it to someone" ambiguity that erodes accountability |

---

## 8. Lifecycle & State Model — Consignment

```
        ┌────────────┐
        │ REQUESTED  │  (raised by M01, M13, M14, M15, M16 or M18)
        └─────┬──────┘
              │ charge calculated, entitlement evaluated
        ┌─────▼──────┐
        │ SCHEDULED  │  window agreed, rider or courier assigned
        └─────┬──────┘
              │ rider dispatched
        ┌─────▼──────────────┐
        │ OUT FOR COLLECTION │
        └─────┬──────────────┘
              │ scan + identity + OTP + signature + photo
        ┌─────▼──────┐
        │ COLLECTED  │  ◄── custody event: customer → rider
        └─────┬──────┘
              │
        ┌─────▼──────┐
   ┌───►│ IN TRANSIT │
   │    └─────┬──────┘
   │          │ arrival at intermediate node
   │    ┌─────▼──────┐
   │    │  AT HUB    │  ◄── custody event: rider → hub
   │    └─────┬──────┘
   │          │ next leg dispatched
   │          └──────────────┐
   │                         │
   │    ┌────────────────────▼─┐
   │    │ OUT FOR DELIVERY     │
   │    └─────┬────────────────┘
   │          │ scan + identity + OTP + signature + photo
   │    ┌─────▼──────┐
   │    │ DELIVERED  │  ◄── custody event: rider → recipient
   │    └─────┬──────┘
   │          │
   │    ┌─────▼──────┐
   │    │   CLOSED   │
   │    └────────────┘
   │
   │    ┌────────────┐
   └────┤ EXCEPTION  │  absent · address wrong · refused · damaged · seal broken
        └─────┬──────┘
              │
        ┌─────▼──────────┐
        │ RETURNED TO    │
        │ ORIGIN         │
        └────────────────┘
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Requested | Scheduled | Charge calculated; window agreed; capacity confirmed | Coordinator / system |
| Scheduled | Out for Collection | Rider or courier assigned; manifest published | Coordinator |
| Out for Collection | Collected | **Scan + both-party identity + OTP + signature + photograph** (BRU-LOG-01) | Rider + customer |
| Collected | In Transit | Custody event written | System |
| In Transit | At Hub | Scan on arrival; custody transferred | Hub operative |
| At Hub | Out for Delivery | Next leg assigned | Coordinator |
| Out for Delivery | Delivered | **Scan + recipient identity + OTP + signature + photograph** (BRU-LOG-02) | Rider + recipient |
| Delivered | Closed | POD complete; cash on delivery reconciled if applicable | System |
| Any | Exception | Reason recorded with geotagged evidence | Rider |
| Exception | Returned to Origin | Re-attempt policy exhausted; charge rules applied | System / coordinator |
| Any | Blocked | Seal break or discrepancy detected — onward movement suspended (BRU-LOG-04) | System |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-LOG-01 | No custody transfer without a scan and an identity capture from both parties | **H** | Logistics Manager |
| BRU-LOG-02 | A consignment cannot be closed without proof of delivery | **H** | Logistics Manager |
| BRU-LOG-03 | Consignments above the declared-value threshold require dual signature and insurance flagging | **H** | CFO |
| BRU-LOG-04 | Any seal break or weight discrepancy raises an incident and blocks onward movement pending review | **H** | Logistics Manager |
| BRU-LOG-05 | Restricted items may only be carried by a rider or courier certified for them | **H** | Quality Manager |
| BRU-LOG-06 | Cash on delivery is reconciled per rider per shift with zero tolerance for unexplained variance | **H** | Finance Manager |
| BRU-LOG-07 | Logistics charges are waived automatically where contract, warranty or Privilege tier entitles the customer | **C** | CCO |
| BRU-LOG-08 | Failed delivery is re-attempted per policy, then returned to origin with charge rules applied | **C** | Logistics Manager |
| BRU-LOG-09 | An item cannot move to a recycling partner without a valid data destruction certificate from M06 | **H** | Quality Manager |
| BRU-LOG-10 | A courier partner whose restricted-item certification has lapsed cannot be assigned restricted consignments | **H** | Logistics Manager |
| BRU-LOG-11 | The custody ledger is append-only; corrections are compensating entries with a stated reason | **H** | CTO |
| BRU-LOG-12 | An item's declared value must be recorded before collection; a zero declared value is not permitted | **H** | Logistics Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.consignment` | `fix_consignment` | The movement record | name, source_type, source_id, origin_party, destination_party, state, declared_value_total, charge_amount, charge_waived, insurance_flag |
| `fix.consignment.leg` | `fix_consignment_leg` | One stage of the journey | consignment_id, sequence, from_location, to_location, carrier_type, rider_id, courier_partner_id, tracking_ref, planned_window, actual_start, actual_end, state |
| `fix.consignment.item` | `fix_consignment_item` | One item within the consignment | consignment_id, asset_id, part_id, serial, description, declared_value, condition_grade, evidence_ids |
| `fix.custody.event` | `fix_custody_event` | The immutable ledger | item_id, leg_id, from_party_type, from_party_id, to_party_type, to_party_id, occurred_at, gps, method, evidence_hash, otp_verified |
| `fix.rider` | `fix_rider` | Internal rider profile | employee_id, vehicle_id, areas, max_value_limit, restricted_item_certified, active |
| `fix.route.manifest` | `fix_route_manifest` | A rider's day | rider_id, date, leg_ids, sequence, total_stops, completed_stops, cash_collected |
| `fix.courier.partner` | `fix_courier_partner` | External carrier | partner_id, service_areas, api_config, restricted_item_certified, sla_terms, active |
| `fix.courier.rate` | `fix_courier_rate` | Partner rate card | courier_partner_id, zone_from, zone_to, weight_band, value_band, rate, effective_from |
| `fix.pod.record` | `fix_pod_record` | Proof of collection or delivery | leg_id, type, recipient_name, recipient_id_ref, signature_ref, photo_refs, otp_code_hash, captured_at, gps |
| `fix.logistics.charge` | `fix_logistics_charge` | Customer charge calculation | consignment_id, basis, distance_km, weight, value_band, service_level, computed_amount, waiver_reason, inputs_json |
| `fix.logistics.incident` | `fix_logistics_incident` | Loss, damage, tamper, delay | consignment_id, item_id, incident_type, detected_at, detected_by, evidence_ids, claim_id, resolution |
| `fix.consignment.seal` | `fix_consignment_seal` | Tamper control | consignment_id, seal_number, applied_by, applied_at, broken_at, broken_by, authorised |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order` | M01 | Parent context; status write-back |
| `fix.asset` | M17 / M49 | Read identity; write location and custody |
| `fix.party`, `fix.address` | M33 | Read for origin, destination and recipient |
| `fix.part.item` | M37 | Read for parts movements |
| `fix.rental.agreement` | M13 | Parent context for rental movement |
| `fix.destruction.certificate` | M06 | Read as a gate before recycling movement |
| `fix.vehicle` | M46 | Read; report usage |
| `fix.supplier.profile` | M42 | Read for return-to-vendor destination |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-LOG-01 | Pick & drop requested at intake | Create the consignment, calculate the charge, evaluate entitlement waiver, offer windows | Manual consignment creation |
| AUT-LOG-02 | Consignment scheduled | Assign a rider or courier by area, value and cost; publish to the manifest; notify the customer | Coordinator assigns manually |
| AUT-LOG-03 | Collection completed | Write the custody event, notify the customer, advance the parent service order | Manual status update |
| AUT-LOG-04 | Seal break or weight discrepancy detected | Raise an incident, block onward movement, notify the logistics manager and the originating branch | Immediate escalation |
| AUT-LOG-05 | Delivery attempt failed | Record the exception with evidence, notify the customer, schedule the re-attempt per policy | Manual rescheduling task |
| AUT-LOG-06 | Re-attempt policy exhausted | Return to origin, apply the charge rules, notify the customer and the originating module | Manual decision |
| AUT-LOG-07 | Courier partner webhook received | Map to the internal state, write the custody event, update tracking | Log and alert on unmappable status |
| AUT-LOG-08 | Rider shift ends | Reconcile cash on delivery against delivered consignments; block the next shift until reconciled | Escalate to finance |
| AUT-LOG-09 | Consignment created for recycling | Verify the data destruction certificate exists; block if absent | Block and alert quality manager |
| AUT-LOG-10 | Restricted item detected in a manifest | Verify carrier certification; reassign if not certified | Block and alert coordinator |
| AUT-LOG-11 | Consignment overdue against its window | Alert the coordinator; notify the customer proactively | Escalate to logistics manager |
| AUT-LOG-12 | Courier invoice received | Reconcile against delivered consignments and the rate card; flag variance | Route to manual reconciliation |

---

## 12. Interfaces

### 12.1 Upstream — M03 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order | Pick & drop and return requests | Command |
| M31 Workshop | Workshop transfer requests | Command |
| M13 Rental | Delivery and collection requests | Command |
| M14 Trade-in / Refurbishment | Intake and movement requests | Command |
| M15 Inventory | Inter-branch transfer and return-to-vendor requests | Command |
| M16 Procurement | Sub-contractor movement requests | Command |
| M18 E-Waste | Recycling collection and batch transfer requests | Command |
| M06 Data Services | Destruction certificate existence check | REST (gate) |
| M33 Party Master | Addresses, geocodes, recipient identity | REST |
| M17 Asset Registry | Item identity and declared value basis | REST |
| M46 Fleet | Vehicle availability and identity | REST |
| M42 Supplier Relationship | Courier partner commercial terms | REST |

### 12.2 Downstream — M03 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Collection and delivery status, custody confirmation | Events |
| M17 Asset Registry | Item location and custody updates | Events |
| M15 Inventory | Confirmation of stock movement between locations | Events |
| M13 / M14 / M18 | Movement completion for their business processes | Events |
| M20 Receivable | Logistics charge as a billable event; COD receipts | Events |
| M23 Quality | Custody exceptions, damage, tamper incidents | Events |
| M24 Documents | POD, POC and transfer documents for retention | Command |
| M27 Contact Centre | Customer-visible movement milestones | Events |
| M25 Business Intelligence | Consignment, cost and performance facts | Warehouse extract |
| P01 Customer Portal | Tracking view and rescheduling | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `consignment.created` | consignment, items, origin, destination, charge | M01, M27, M20 |
| `consignment.scheduled` | consignment, window, carrier | M27, P01 |
| `consignment.collected` | consignment, custody event, POC evidence | M01, M17, M27 |
| `consignment.custody_transferred` | item, from party, to party, time, GPS | M17, M24, M23 |
| `consignment.at_hub` | consignment, hub, next leg | M27 |
| `consignment.delivered` | consignment, POD evidence, recipient | M01, M13, M20, M27 |
| `consignment.exception` | consignment, exception type, evidence | M01, M27, M23 |
| `consignment.returned` | consignment, reason, charge applied | M01, M20 |
| `custody.tamper_detected` | item, seal, detected by, evidence | M23, management |
| `logistics.charge_calculated` | consignment, amount, waiver reason, inputs | M20 |
| `cod.collected` | rider, consignment, amount | M50, M20 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/consignments` | POST | Create a consignment | M01, M13, M14, M15, M18, P03 |
| `/api/v1/consignments/{id}` | GET | Full consignment detail with custody chain | P03, P09 |
| `/api/v1/consignments/{id}/schedule` | POST | Assign carrier and window | P03 |
| `/api/v1/consignments/{id}/reschedule` | POST | Reschedule within policy | P01, P03 |
| `/api/v1/logistics/manifest` | GET | Rider's daily manifest | P09 |
| `/api/v1/logistics/legs/{id}/handover` | POST | Record custody transfer with evidence | P09 |
| `/api/v1/logistics/legs/{id}/exception` | POST | Record a failed attempt | P09 |
| `/api/v1/logistics/sync` | POST | Offline command replay for the rider app | P09 |
| `/api/v1/items/{serial}/custody` | GET | Full custody history for one item | P03, P04, legal |
| `/hooks/v1/courier/{partner}` | POST | Courier partner status webhook | External |
| `/api/v1/consignments/{id}/tracking` | GET | Customer-facing tracking view | P01 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R15 Logistics Coordinator | C R U D A | Own area or central |
| R16 Rider / Delivery Agent | R U | Own manifest only |
| R05 Operations Director | C R U D A | All |
| R06 Branch Manager | C R U | Own branch's consignments |
| R08 Service Centre Agent | C R | Own branch |
| R09 Workshop Supervisor | R U | Consignments to and from own workshop |
| R17 Inventory Manager | C R | Stock movements |
| R19 Procurement Officer | C R | Return-to-vendor movements |
| R26 Finance Manager | R | Charges, COD, courier reconciliation |
| R32 Quality Manager / ISO Coordinator | R | Incidents and custody exceptions |
| R36 Customer | R | Own consignment tracking only |
| R38 Courier Partner | R U | Own assigned consignments only, minimum data |

**Field-level restrictions:** declared value is visible to R15, R05, R06, R26 and R32 only —
riders see a value band, not the exact figure, to reduce theft incentive.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Logistics live dashboard | Logistics coordinator | Real time | Pending, scheduled, in transit, delivered, exception — exactly as specified in the SOW |
| Rider performance | Logistics Manager | Weekly | Stops completed, on-time rate, POD completeness, exceptions, COD variance |
| Courier partner scorecard | Logistics Manager, Procurement | Monthly | On-time, damage rate, cost per consignment, invoice accuracy |
| Custody exception report | Quality Manager, Logistics Manager | Daily | Seal breaks, discrepancies, unexplained gaps |
| Loss and damage register | Finance, Legal, Quality | Monthly | Incidents, value, claim status, root cause |
| Cost per consignment | Finance, Logistics Manager | Monthly | By zone, service level, carrier type and business line |
| Charge waiver analysis | CCO, Finance | Monthly | Value of logistics charges waived by entitlement type |
| On-time performance | Operations Director | Weekly | Collection and delivery attainment against committed windows |
| Restricted-item compliance | Quality Manager | Monthly | Movements of batteries and hazardous items, carrier certification status |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-018 | On-time collection | unmeasured | 90% | **93%** |
| KPI-018 | On-time delivery | unmeasured | 90% | **93%** |
| KPI-019 | Chain-of-custody exceptions | untracked | **0** | **0** |
| — | Loss and damage rate | untracked | < 0.3% | **< 0.1%** |
| — | POD capture completeness | 0% | **100%** | **100%** |
| — | Cost per consignment | untracked | baselined | **−15%** |
| — | Courier invoice reconciliation accuracy | n/a | 95% | **99%** |
| — | COD variance | untracked | < 0.5% | **< 0.1%** |
| — | Customer rescheduling via self-service | 0% | 40% | **65%** |
| — | Restricted-item movements with certified carrier | unmeasured | **100%** | **100%** |
| — | Rider app offline reliability | n/a | **100%** | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `stock` (internal transfers as the movement substrate) | 8% |
| L4 | OSRM (sequencing), geocoding service | 10% |
| L5 | `cd_consignment`, `cd_custody`, `cd_courier`, `cd_rider`, `cd_logistics_charge`, Flutter rider application | 82% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-017 | `cd_consignment` — consignment, leg, item, state machine | Odoo module | 6 PW |
| CD-018 | `cd_custody` — custody ledger, POD/POC, seal, evidence integrity | Odoo module | 4 PW |
| CD-019 | `cd_courier` — partner registry, booking API, webhook ingestion, reconciliation | Odoo module + service | 4 PW |
| CD-020 | `cd_logistics_charge` — zone/distance charging, entitlement waiver | Odoo module | 2 PW |
| CD-021 | **Rider mobile application (Flutter)** | Mobile app | 6 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M01 Service Order | Pick & drop originates from a service order |
| M17 Asset Registry | Items must have identity to be tracked |
| M33 Party Master | Addresses and recipient identity |
| M29 Identity | Rider authentication and evidence attribution |
| M24 Documents | POD and transfer documents must be retained |
| M15 Inventory | Stock movements — may be stubbed and completed in W3 |
| M06 Data Services | The recycling gate — required only from W6 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Open pick & drop jobs | Current only, ~200 | `fix.consignment` | W3 cutover |
| Courier partner contracts and rate cards | 3–5 partners | `fix.courier.partner`, `fix.courier.rate` | W3 |
| Rider master | 50–150 | `fix.rider` | W3 |

No historical consignment data exists. Zone definitions and rate cards must be **authored**
before Wave 3.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Pick & drop operates end to end with unbroken custody for 100 consecutive consignments | Custody ledger audit |
| AC-02 | No custody transfer is possible without a scan and both-party identity, including via API | Negative test |
| AC-03 | POD and POC are captured on 100% of completed legs | Completeness report over four weeks |
| AC-04 | The logistics dashboard shows pending, delivered, cancelled and exception in real time | Demonstration against the SOW requirement |
| AC-05 | A seal break blocks onward movement and raises an incident automatically | Scripted scenario |
| AC-06 | The rider app operates for a full shift offline and synchronises with complete integrity | Offline test with 10 riders |
| AC-07 | Distance-based charging computes correctly for same-area, within-country and cross-border cases | Test matrix |
| AC-08 | Entitlement-based waiver applies automatically for contract, warranty and Privilege cases | Test matrix |
| AC-09 | A courier partner webhook is ingested, mapped and written to the custody ledger idempotently | Replay test |
| AC-10 | COD reconciles per rider per shift with variance below 0.5% | Four weeks of records |
| AC-11 | An item's full custody history is retrievable by serial in under 200 ms | Performance test |
| AC-12 | A recycling movement is blocked without a data destruction certificate | Negative test (from W6) |
| AC-13 | The rider app is complete in Bengali | Translation coverage report |
| AC-14 | Logistics coordinator signs off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which courier partners will be contracted, and do they expose booking and tracking APIs? | Logistics Manager / Procurement | W3 minus 2 months |
| Q-02 | What is the declared-value threshold above which enhanced controls apply? | CFO | W3 build |
| Q-03 | Is pick & drop charged, free above a service value, or free for Privilege members only? | CCO | W3 build |
| Q-04 | Does the Company carry transit insurance today, and at what declared-value limit? | CFO / Legal | W3 build |
| Q-05 | Central logistics team, branch riders, or both — and in which areas? | Logistics Manager | W3 design |
| Q-06 | What is the re-attempt policy — how many attempts before return to origin, and who bears the cost? | CCO / Logistics Manager | W3 build |
| Q-07 | Are riders employees or contractors? This affects the app's access model and cash liability. | HR Director / Legal | W3 minus 1 month |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` · `M01_Service_Request_and_Order_Management.md` ·
`M31_Workshop_and_Depot_Repair_Management.md` ·
`03_Modules/K_Platform_and_Technology/P09_Logistics_and_Rider_Application.md` ·
`03_Modules/D_Circular_and_Asset_Based_Business/_CATEGORY_OVERVIEW.md` §4 (destruction gate)

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Pick & Drop Service ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Logistics team Interface,
§Shipping charges, §QR and OTP features ·
`1000fix_business/Business planning for 1000 fix.docx` §Rental Services, §Device Recycling ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FSM-015

**External benchmark**
Oracle Logistics — Transportation Management, shipment legs and freight audit ·
SAP Transportation Management — freight order and event management ·
Enterprise reverse-logistics practice for mobile and IT assets — RMA, serialised asset tag,
chain-of-custody log opened at arrival and maintained through every stage, certified erasure
and tamper-proof certificate · NIST SP 800-88 traceability framework — linked records and
transportation-stage documentation · Bangladeshi last-mile courier platforms — booking API,
webhook tracking, COD reconciliation

---

*Module M03 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
