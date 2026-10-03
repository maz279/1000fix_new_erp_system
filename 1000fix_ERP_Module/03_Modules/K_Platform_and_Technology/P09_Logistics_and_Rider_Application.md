---
id: FIX-ERP2-P09
portal_id: P09
portal_code: LRA
portal_name: Logistics & Rider Application
type: Native Mobile Application (offline-first) + Coordinator Web View
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Logistics Manager
system_owner: Field Platform Squad
priority: P1
wave: W3
---

# P09 — Logistics & Rider Application
### Portal Suite · Code `LRA` · ★ New in v2.1

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P09 |
| **Portal code** | `LRA` |
| **Type** | Native mobile application (**offline-first**) + coordinator web view |
| **Status** | ★ New in v2.1 — pick-and-drop was a v1.0 process with no dedicated surface |
| **Priority** | **P1** |
| **Delivery wave** | **W3** (Months 9–13) |
| **Users** | Internal riders, logistics coordinators, courier partner staff |
| **Volume** | **50–200 users** — 50–150 riders, 10–25 coordinators, courier partner staff |
| **Business owner** | Logistics Manager |
| **System owner** | Field Platform Squad |
| **Technology** | Flutter (rider application) + Next.js 15 / Odoo Web (coordinator view) |
| **Custom development** | `CD-210` |
| **Requirement range** | FR-POR-255 … FR-POR-282 |
| **Requirement count** | **28** *(measured — supersedes the 8 allocation in `05-01` §4)* |
| **Effort estimate** | **22 person-weeks** |
| **Backing modules** | M01, M03, M04, M12, M13, M14, M15, M17, M18, M20, M21, M46, M55 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P09 is **the custody surface**. Every device that moves between a customer and a 1000FiX
location moves in someone's hands, and P09 is where that transfer is recorded, evidenced and
made defensible.

Pick-and-drop is one of the Company's stated competitive advantages. It is also its largest
uncontrolled liability: a customer's laptop, in a bag, on a motorcycle, in Dhaka traffic, with
no record of its condition when it was collected. When it arrives damaged — or does not arrive
— the dispute is unwinnable without evidence, and the evidence has to be captured at the moment
of collection by a rider on a phone.

P09 holds no authoritative state. The consignment belongs to M03, the device to M17, the payment
to M20. What P09 owns is **the rider's day and the chain of custody** — and a custody chain
with a break in it is worth very little.

### Why It Exists

**Custody breaks are the target and the reason.** `04-00` sets **custody breaks: zero** and
**POD capture completeness: 100%**. Those are not aspirational; a single break in the chain on a
high-value device is a loss the Company absorbs and a customer relationship that ends.

**Three modules depend on evidence this application captures.** M17 maintains the immutable
custody chain (FR-AST-020) with signature and photographic evidence at each transfer. M06's
secure data-handling claim — *"your device and data are secure"* — depends on knowing who held
the device at every moment. M03 owns the consignment but not the hands it passes through.

**Riders work where the network does not.** Basements, lifts, stairwells, district roads.
`04-00` requires **rider app offline reliability: 100%** and full offline operation with queued
sync. This places P09 in the same class as P02 — and it reuses P02's journal.

**Cash travels with riders.** Payment on delivery is a real flow in this market. Cash collected
by 50–150 riders across a day, reconciled at shift end, is a control problem that only a
structured surface solves.

**The coordinator has no console.** 10–25 logistics coordinators currently assign, chase and
reschedule by phone. `04-00` specifies a coordinator web view with a real-time dashboard of
pending, in-transit, delivered and exception consignments — the operational counterpart to the
rider's application.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-FSM-015 | "Manage pick & drop service lifecycle: pickup scheduled → picked up → in repair → completed → delivery scheduled → delivered" |
| ERP BRD BR-SRM-010 | Photo attachments with timestamp and GPS tag — applied to custody transfer |
| ERP BRD BR-FSM-012 | Customer electronic signature capture |
| ERP BRD BR-FSM-013 | Offline operation with sync on reconnection |
| ERP BRD BR-FIN-004 | Multiple payment methods including cash — collected on delivery |
| ERP BRD BR-DMS-002 | Electronic signature capture and verification |
| Company Profile §Additional Services | Pick-and-drop from home or office is a stated competitive advantage |
| `04-00` §P09 | Capability set across eight areas **including the coordinator web view**, and four KPIs, adopted verbatim |
| `04-00` §3 PS-08 | Offline-capable with queued sync — binding on P02, P09 and P11 |
| `02-01` §10 AS-13 | Append-only local journal with server-side conflict resolution |
| `M17` §5.3 FR-AST-020 | Immutable custody chain with from-party, to-party, timestamp, location, evidence and signature |
| `M03` §12.3 | `consignment.collected` and `consignment.custody_transferred` events consumed by M17, M24 and M23 |
| `M46` §5.4 FR-FLT-024 | Vehicle pre-use check, surfaced here for riders who are assigned drivers |
| `05-04` §1 R16 | Rider — 50–150 headcount, P09 only, own manifest scope |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The rider's day: optimised pickup and delivery manifest, route overview, permitted reordering |
| 2 | Shift start, vehicle pre-use check where the rider is the assigned driver, and shift end |
| 3 | Collection: consignment scan, item verification against the manifest, condition photography, packaging evidence, seal entry, customer OTP and signature, receipt issue |
| 4 | Transit: status updates, exception recording, rescheduling request |
| 5 | Delivery: recipient identity verification, handover scan, photograph, OTP and signature, payment collection |
| 6 | **The custody record**: every handover with GPS, timestamp and both parties' identity |
| 7 | Cash collected on delivery and shift-end cash reconciliation |
| 8 | Full offline operation with queued, ordered, idempotent sync |
| 9 | Navigation to each stop and automatic arrival detection |
| 10 | In-app communication with the coordinator and escalation |
| 11 | Rider safety alert |
| 12 | **Coordinator web view**: real-time dashboard of pending, in-transit, delivered and exception consignments |
| 13 | Coordinator assignment to riders or courier partners, rescheduling, SLA monitoring |
| 14 | Central versus branch team assignment |
| 15 | Bengali-first interface throughout |
| 16 | Instrumentation of POD completeness, custody integrity and on-time performance |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **The consignment, its lifecycle, routing rules and courier selection** | **M03** Service Logistics & Reverse Logistics | P09 executes a manifest; M03 constructs it |
| **The service order and repair** | **M01 / M31** | A consignment carries a device; the job is elsewhere |
| **Device identity, resolution and the authoritative custody chain** | **M17** Asset Registry | P09 captures the transfer event; M17 holds the chain |
| **Technician field service and repair execution** | **P02** | A rider moves devices; a technician repairs them. Where one person does both, they hold both roles and both applications |
| **Vehicle documents, servicing, fuel and availability** | **M46** Fleet & Vehicle Management | P09 surfaces the pre-use check; M46 owns the vehicle |
| **Payment processing, settlement and reconciliation to the ledger** | **M20** Receivable & Collections | P09 records a collection; M20 owns the money |
| **Courier partner commercial relationship, rates and settlement** | **M03 with M42**; partner self-service is **P05** | A courier partner's own staff may use P09; their invoicing is P05 |
| **Route optimisation algorithm** | **M03 with M02** | P09 presents an optimised manifest; it does not compute one |
| **Warehouse and branch stock movement** | **M15 / M41** | A parts transfer between branches is a stock movement M03 moves; the stock ledger is M15 |
| **E-waste collection routing** | **M18 with M03** | P09 executes an e-waste collection like any other consignment |
| **Customer-facing tracking** | **P01** | The customer tracks in P01; P09 supplies the events |
| **Identity, session policy and MFA** | **M29** | **PS-01** |

### 3.3 Shared Concepts

| Concept | P09's Role | Owning Module |
|---|---|---|
| The rider's day and the manifest execution | **Owns** — the defining concern of this application | P09 |
| **The offline journal** | **Owns** — local durability until sync, reusing the P02 pattern | P09 |
| Consignment | Executes; updates status | M03 |
| **Custody transfer** | **Captures the evidence**; M17 holds the chain | P09 / M17 |
| Device | Scans, records condition | M17 |
| Vehicle pre-use check | Captures | M46 |
| Cash collected | Records and reconciles at shift end | M20 / M04 |
| Coordinator dashboard | **Owns** the view; M03 owns the consignments | P09 / M03 |
| Rider assignment | Coordinator assigns in P09's coordinator view; M03 owns the allocation model | P09 / M03 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Electronic proof-of-delivery practice (Onfleet, Locus, Spoke, CXT)** | POD captured digitally on site with **OTP, photographs, barcodes and signatures**; drivers handle every verification type; delivery coordinates and timestamps automatically attached to both signature and photograph proofs | **Multi-factor POD as the default, not the exception.** A device handover captures scan **and** photograph **and** OTP **and** signature — four independent proofs, geo- and time-stamped. For a customer's laptop this is proportionate; for a parcel it would not be. Also adopted: coordinates and timestamps attached automatically rather than entered | Signature-only POD, which is the weakest form and the one most easily disputed |
| **Chain-of-custody delivery software** | **Time-stamped, geo-verified proof establishing an indisputable chain of custody** to minimise disputes and improve accountability; a signed receipt establishing custody within the organisation and allowing tracking of when and in what condition an item arrived | **"When and in what condition" as the governing requirement**, which is why condition photography at collection is mandatory rather than optional. Most POD systems prove *that* something was handed over; a repair business must prove *what state it was in* | Chain-of-custody legal formalism beyond what a commercial dispute requires |
| **Customer-side signature ahead of time (SMS link)** | Customers sign ahead via an SMS link, avoiding contact with the driver's device | **Adopted as an option**, not the default — useful for contactless handover and for a recipient who is not the account holder | Making it the default; a physical handover of a valuable device should have the recipient present |
| **Last-mile driver applications (TrackObit, CXT, courier platforms)** | Optimised manifest, barcode scanning that auto-opens the stop, status updates, exception codes, offline operation with queued sync, cash-on-delivery recording and shift reconciliation | **The whole operational pattern**, including **scan-to-open-stop**, which removes a navigation step at every single stop and compounds across a 20-stop day | Full TMS capability; M03 does the planning |
| **P02 Technician Mobile Application** *(the internal benchmark)* | Append-only offline journal, idempotent ordered replay, three-tier conflict policy, sync reporting to technician and supervisor | **The journal and sync engine are reused, not rebuilt.** P02 ships in W2 and P09 in W3; building a second offline engine one wave later would be the most expensive avoidable duplication in the suite | — |
| **Rider gig platforms (Pathao, Foodpanda rider apps)** *(the local benchmark)* | Bengali-first, phone-only, low-bandwidth, simple stop-by-stop flow, earnings and shift summary, safety features | **The interaction vocabulary Bangladeshi riders already have.** A rider who has delivered for Pathao should be productive in P09 within one shift | Gig-style acceptance-rate penalties; these are employed riders on a manifest, not bidding couriers |

**Design position.** Five deliberate differences from the benchmark.

First, **custody is proven four ways, and the capture is compulsory.** Scan, condition
photograph, OTP and signature. A handover cannot be completed without all four where the
consignment carries a customer device. This is heavier than parcel delivery because the item is
worth more than the delivery.

Second, **condition is captured, not just receipt.** Every collection photographs the device's
condition and its packaging before it moves. `04-00` requires photographs of items and
packaging at collection, and this is the single evidence artefact that decides a damage dispute.
A rider who does not photograph is a liability the Company carries.

Third, **the journal is P02's.** Same append-only structure, same idempotent replay, same
three-tier conflict policy, same sync reporting. Riders and technicians face the same
connectivity, and one engine maintained is better than two.

Fourth, **the coordinator view is part of this portal, not P03.** `04-00` places it here
deliberately: the coordinator's work is the real-time counterpart of the rider's, and splitting
them across two surfaces separates two halves of one operation. It is delivered as a web view
alongside the rider application.

Fifth, **cash is reconciled at shift end, by the rider, in the app.** Cash collected on delivery
across 50–150 riders is a control exposure of the same shape as van stock in M15. The rider
counts, the app computes the expected figure, the variance is named to a person, and an
unresolved variance blocks the next shift's cash-collection assignments.

---

## 5. Capability Areas & Functions

### 5.1 The Rider's Day

| FR ID | Feature | Function — "The application shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-255 | Daily manifest | Present the rider's optimised pickup and delivery manifest with stop sequence, time windows, customer, address, item count and any special instruction, fully available offline | **P0** | L5 |
| FR-POR-256 | Route overview | Present the day's route on a map with the stop sequence, total distance and estimated completion time | **P0** | L5 |
| FR-POR-257 | Permitted reordering | Allow the rider to reorder stops within constraints M03 defines — time windows, priority, SLA — and never outside them | P1 | L5 |
| FR-POR-258 | Shift start and vehicle check | Start the shift, and where the rider is the assigned driver present the M46 vehicle pre-use check and block the first stop until it is submitted (M46 FR-FLT-024) | **P0** | L5 |
| FR-POR-259 | Navigation and arrival | Launch navigation to each stop and detect arrival automatically by geofence, recording the timestamp | **P0** | L5 |
| FR-POR-260 | Scan to open | Open the correct stop by scanning the consignment or item barcode, without navigating a list | P1 | L5 |
| FR-POR-261 | Shift end | Present the shift summary — stops completed, exceptions, items carried, cash collected — and require reconciliation before close | **P0** | L5 |

### 5.2 Collection

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-262 | Consignment scan | Scan the consignment and verify every item against the manifest, refusing completion where an item is missing or unexpected | **P0** | L5 |
| FR-POR-263 | Device identification | Capture or confirm the device's identifier by scan or photograph, submitting it to M17 for resolution | **P0** | L5 |
| FR-POR-264 | **Condition photography** | Require photographs of the device's condition and its packaging before it moves, geo- and time-stamped, with a minimum count enforced and no path to skip | **P0** | L5 |
| FR-POR-265 | Accessory checklist | Record accessories handed over — charger, bag, stylus, cables — as a checklist that must be reconciled at return (M17 FR-AST-015) | **P0** | L5 |
| FR-POR-266 | Seal and packaging | Record the tamper-seal number and packaging type applied at collection | P1 | L5 |
| FR-POR-267 | Customer verification and signature | Verify the handing party by OTP, capture their signature, and issue a receipt showing items, condition and reference | **P0** | L5 |
| FR-POR-268 | Collection receipt | Issue a printed or digital receipt to the customer at the moment of collection, in Bengali | **P0** | L5 |

### 5.3 Transit & Delivery

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-269 | Status updates | Update consignment status at each transition, offline-capable, queued for sync | **P0** | L5 |
| FR-POR-270 | Exception recording | Record an exception with a structured reason — customer absent, address wrong, refused, item damaged, access denied, unsafe — with a photograph and a note | **P0** | L5 |
| FR-POR-271 | Reschedule request | Request rescheduling of an undeliverable stop, routed to the coordinator, with the customer notified through M27 | **P0** | L5 |
| FR-POR-272 | Recipient verification | Verify the recipient's identity at delivery by OTP, and where the recipient differs from the account holder record the relationship and evidence | **P0** | L5 |
| FR-POR-273 | Handover evidence | Capture handover scan, photograph, OTP and signature, geo- and time-stamped, and refuse completion without all four where the consignment carries a customer device | **P0** | L5 |
| FR-POR-274 | Condition at handover | Photograph the device's condition at handover and reconcile the accessory checklist, flagging any discrepancy before the customer signs | **P0** | L5 |
| FR-POR-275 | Remote signature option | Support customer signature by SMS link ahead of arrival, as an option for contactless handover, without replacing physical verification | P2 | L5 |

### 5.4 Custody, Cash, Safety & Offline

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-276 | **Custody record** | Record every handover as an immutable event carrying from-party, to-party, timestamp, GPS coordinates, condition evidence and both parties' identity, submitted to M17's custody chain (M17 FR-AST-020) | **P0** | L5 |
| FR-POR-277 | Rider-to-rider and rider-to-branch transfer | Record a transfer between riders or from a rider to a branch with dual confirmation, so the chain has no unattributed gap | **P0** | L5 |
| FR-POR-278 | Cash collection | Record cash collected on delivery against the consignment, issue a receipt, and hold it against the rider's shift float | **P0** | L5 |
| FR-POR-279 | Cash reconciliation | Reconcile cash at shift end against the expected figure, record the variance, and block the next shift's cash assignments where an unresolved variance exceeds threshold | **P0** | L5 |
| FR-POR-280 | Safety alert | Provide a panic and safety alert transmitting position and identity by every available channel, never rate-limited | **P0** | L5 |
| FR-POR-281 | **Offline operation** | Operate fully offline for a complete shift with no feature unavailable and no data loss, syncing through the append-only journal reused from P02 (AS-13, **PS-08**) | **P0** | L5 |

### 5.5 Coordinator Web View

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-282 | **Coordinator console** | Present a real-time dashboard of pending, in-transit, delivered and exception consignments; assign to internal riders or courier partners; reschedule; monitor SLA; switch between central and branch team assignment; and view every rider's live position, manifest progress and sync health | **P0** | L5 |

> **Cross-cutting.** The coordinator console is specified as one requirement because it is a
> single console with one purpose — real-time consignment control — whose sub-capabilities are
> enumerated in `04-00` §P09 and reproduced above. Its detailed content is specified by M03,
> which owns the consignment model.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Full offline operation** | A complete shift offline with no feature unavailable and no data loss (**PS-08**; `04-00` "rider app offline reliability: 100%") |
| T-02 | **Journal reuse** | The append-only journal, idempotent replay, ordered per-aggregate sequencing and three-tier conflict policy are **the P02 implementation**, not a second engine (AS-13) |
| T-03 | **Durability before acknowledgement** | Every custody, status, evidence and cash action is written to the journal before the UI acknowledges it |
| T-04 | **Custody atomicity** | A custody transfer is a single journal entry carrying all four proofs; a partial capture is never recorded as a transfer |
| T-05 | **Evidence integrity** | Photographs are EXIF-stamped with GPS and time on device, compressed, queued with resumable upload, and never discarded — capture is refused when the queue is full |
| T-06 | **Forced capture enforcement** | The minimum photograph count, OTP and signature at collection and handover are enforced client-side **and** re-validated server-side on replay |
| T-07 | **Idempotent replay** | Every entry carries a client idempotency key; replay after failure produces exactly one custody event |
| T-08 | **Sync reporting** | Sync success, pending count, failures and conflicts visible to the rider in-app and to the coordinator in the console |
| T-09 | **Coordinator real-time** | The coordinator console reflects a rider event within 15 seconds of sync, and shows each rider's last-sync time explicitly |
| T-10 | **Device envelope** | Acceptable operation on a mid-range Android device; battery budget under 15% per shift excluding navigation |
| T-11 | **Cash isolation** | Cash figures are recorded against the consignment and the rider's shift float; P09 holds no ledger and posts nothing |
| T-12 | **Local data protection** | The local store is encrypted at rest; customer data and evidence are purged after handover plus a bounded window, and immediately on logout or remote wipe (AS-14) |
| T-13 | **Remote wipe** | A lost rider device can be wiped and its binding revoked through M29 |
| T-14 | **All traffic through the gateway** | Every call routes through M28 (**PS-02**) |
| T-15 | **No client-side business logic** | Route constraints, SLA and charge values come from M03 and M20 (**PS-11**) |
| T-16 | **Bengali-first** | Complete Bengali including every error; Bengali is the default for rider roles (**PS-03**) |
| T-17 | **Courier partner scoping** | A courier partner's staff see only consignments assigned to their organisation, and never another partner's or an internal rider's manifest |
| T-18 | **Instrumentation** | POD completeness, custody integrity, exception reasons and sync health instrumented to M25 (**PS-10**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P09 |
|---|---|---|
| **Rider** | Carries a printed list and a pen; photographs on WhatsApp if at all | Works a scanned manifest; captures four proofs at each handover in under a minute |
| **Customer handing over a device** | Gets a handwritten slip, or nothing | Gets a receipt showing items, condition and reference, and a tracking link |
| **Customer receiving a device** | Signs a paper sheet | Verifies by OTP, sees the condition photographs from collection, signs |
| **Logistics coordinator** | Assigns and chases by phone all day | Works a live dashboard of pending, in-transit and exception consignments |
| **Branch** | Receives devices with no formal handover | Confirms custody by dual scan; the chain has no gap |
| **Workshop** | Cannot tell whether damage predates the repair | Sees collection condition photographs against the device record |
| **Customer service** | Cannot answer "where is my laptop" | The status is on the customer's own tracking view |
| **Finance** | Cash on delivery reconciled by trust | Reconciled per rider per shift with variance named |
| **Courier partner** | Sends POD by WhatsApp | Captures it in the same application against the consignment |
| **Legal / claims** | A damage dispute is one word against another | Four geo- and time-stamped proofs at each transfer |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Damage and loss dispute elimination** | Condition photographed at collection and at handover; four proofs per transfer | The dominant benefit. Each disputed high-value device currently costs the Company the device, the relationship, or both. This is loss avoided rather than revenue earned, and it is why the custody-break target is **zero** |
| **Pick-and-drop scalability** | A stated competitive advantage becomes a controlled, measurable operation | Enables growth in the service mode that most differentiates the Company, without proportionate risk growth |
| **On-time performance** | Optimised manifests, scan-to-open, exception handling with rescheduling | `04-00` target: **on-time collection and delivery > 93%**, directly supporting TAT (KPI-002) |
| **Customer retention** | Transparency at the most anxious moment — when a customer has handed over their device | Contributes to the **BDT 78 lac/year** retention benefit |
| **Cash control** | Per-rider, per-shift reconciliation with variance named | Addresses a leakage channel of the same shape as van stock in M15, across 50–150 riders |
| **Administrative labour** | Paper manifests, WhatsApp photographs and phone chasing eliminated | Contributes to the **BDT 62 lac/year** administrative saving |
| **Coordinator capacity** | 10–25 coordinators move from phone chasing to exception management | Releases capacity as consignment volume grows |
| **Data-services credibility** | M06's secure-handling claim is evidenced by an unbroken custody chain | Protects the **BDT 30 lac/year** data-services revenue attributed to M06 |
| **Reverse logistics enablement** | Trade-in collection (M14) and e-waste collection (M18) run on the same surface | Enables the **BDT 65 lac** refurbishment and **BDT 12 lac** e-waste lines |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **The custody chain is complete** | M17's chain, M06's ISMS claim and M03's proof of delivery all depend on this surface. A gap here invalidates all three |
| **Rider safety** | The panic alert and shift-tracking are the Company's duty of care to 50–150 people carrying valuable goods through traffic |
| **Evidential defensibility** | Four geo- and time-stamped proofs per transfer is what protects the Company in a dispute, an insurance claim or a legal matter |
| **Customer confidence at the point of greatest anxiety** | Handing over a laptop containing one's work and photographs is a moment of trust. A receipt with condition photographs changes that experience |
| **Accountability without surveillance** | Position is captured at stop events, not continuously; the record is of consignments, not of people |
| **Courier partner parity** | Partner staff work to the same evidence standard as internal riders, so the chain does not weaken when work is outsourced |
| **Bengali as a working language** | Riders work in Bengali; an English-only application produces skipped steps and missing evidence |

---

## 8. Journeys & State Models

### 8.1 The Custody Chain — the application's reason to exist

```
   CUSTOMER ──collection──► RIDER ──handover──► BRANCH ──► WORKSHOP
        ▲                                                      │
        │                                                      │ repaired
        └──── delivery ◄── RIDER ◄── handover ◄── BRANCH ◄─────┘

   EVERY ARROW IS A CUSTODY EVENT requiring, without exception:

   ┌──────────────────────────────────────────────────────────┐
   │  1. SCAN          consignment / item barcode              │
   │  2. PHOTOGRAPH    condition + packaging, EXIF GPS + time   │
   │  3. OTP           the counterparty's identity verified     │
   │  4. SIGNATURE     bound to the record and the version      │
   │                                                            │
   │  + from-party · to-party · timestamp · GPS · accessories   │
   └──────────────────────────────────────────────────────────┘
        │ written to the append-only journal BEFORE UI acknowledges
        ▼
   M17 CUSTODY CHAIN (FR-AST-020) — immutable, gap-free

   ✖ A transfer with fewer than four proofs is NOT a transfer
   ✖ A gap between two custody events is a CUSTODY BREAK — target: ZERO
```

| Transfer | From | To | Additional requirement |
|---|---|---|---|
| Collection | Customer | Rider | Accessory checklist established; seal applied; receipt issued |
| Rider → Branch | Rider | Branch | Dual confirmation; both identities recorded |
| Rider → Rider | Rider | Rider | Dual confirmation; no intermediate gap |
| Branch → Rider | Branch | Rider | Accessory checklist verified before release |
| Delivery | Rider | Customer | Condition reconciled against collection; accessories reconciled; discrepancy flagged **before** signature |

### 8.2 The Stop — collection and delivery

```
   ARRIVE (geofence) ──► SCAN TO OPEN STOP
        │
   ┌────▼─────────────────────────────────────────┐
   │  COLLECTION                 │  DELIVERY       │
   ├─────────────────────────────┼─────────────────┤
   │ verify items vs manifest    │ verify recipient│
   │ identify device (M17)       │ (OTP)           │
   │ PHOTOGRAPH condition +      │ PHOTOGRAPH      │
   │   packaging (min. count)    │   condition     │
   │ accessory checklist         │ reconcile       │
   │ seal number                 │   accessories   │
   │ OTP + signature             │ OTP + signature │
   │ issue receipt               │ collect payment │
   └────┬────────────────────────┴─────────┬───────┘
        │ all required proofs captured     │
   ┌────▼─────────────────────────────────▼───────┐
   │  CUSTODY EVENT WRITTEN TO JOURNAL             │
   └────┬──────────────────────────────────────────┘
        │ any proof missing
   ┌────▼──────────────────────────────────────────┐
   │  STOP CANNOT COMPLETE — the missing proof is  │
   │  named; the rider cannot proceed past it      │
   └───────────────────────────────────────────────┘

   EXCEPTION PATH (customer absent · address wrong · refused ·
   item damaged · access denied · unsafe):
        │ structured reason + photograph + note
   ┌────▼──────────────────────────────────────────┐
   │  EXCEPTION RECORDED → coordinator notified →   │
   │  reschedule requested → customer notified (M27)│
   └───────────────────────────────────────────────┘
```

### 8.3 Cash at Shift End

```
   SHIFT ENDS
        │
   ┌────▼────────────────────────────────────┐
   │  APP COMPUTES EXPECTED CASH              │
   │  (collections recorded − any handover)   │
   └────┬────────────────────────────────────┘
        │
   ┌────▼────────────────────────────────────┐
   │  RIDER COUNTS AND ENTERS ACTUAL          │
   └────┬────────────────────────────────────┘
        │
   ┌────▼──────────────┬─────────────────────┐
   │  MATCHES          │  VARIANCE           │
   │  → handover to    │  → recorded, named  │
   │    branch cashier │    to the rider     │
   └───────────────────┴──────────┬──────────┘
                                  │ above threshold, unresolved
                       ┌──────────▼─────────────────────┐
                       │  NEXT SHIFT'S CASH ASSIGNMENTS │
                       │  BLOCKED pending resolution     │
                       └────────────────────────────────┘
```

> Deliberately the same control shape as M15's van-stock reconciliation (BRU-INV-12): count,
> compute, name the variance, block the next assignment. One control pattern, two contexts.

---

## 9. Portal Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P09-01 | A custody transfer requires scan, condition photograph, OTP and signature; fewer than four proofs is not a transfer | **H** | Logistics Manager |
| PRU-P09-02 | A stop cannot complete without every required proof; the missing item is named | **H** | Logistics Manager |
| PRU-P09-03 | Condition photography at collection is compulsory with a minimum count and no skip path | **H** | Logistics Manager |
| PRU-P09-04 | Every custody event is written to the append-only journal before the UI acknowledges it (AS-13) | **H** | CTO |
| PRU-P09-05 | The custody chain has no unattributed gap; rider-to-rider and rider-to-branch transfers require dual confirmation | **H** | Logistics Manager |
| PRU-P09-06 | Accessories are reconciled at handover and any discrepancy is flagged **before** the customer signs | **H** | Logistics Manager |
| PRU-P09-07 | A rider may reorder stops only within the constraints M03 defines | **H** | Logistics Manager |
| PRU-P09-08 | Cash is reconciled at every shift end; an unresolved variance above threshold blocks the next shift's cash assignments | **H** | CFO |
| PRU-P09-09 | The vehicle pre-use check is completed before the first stop where the rider is the assigned driver (M46) | **H** | Logistics Manager |
| PRU-P09-10 | No feature requires connectivity that a rider cannot complete offline (**PS-08**) | **H** | CTO |
| PRU-P09-11 | Position is captured at stop events, not continuously outside working hours | **H** | HR Director |
| PRU-P09-12 | Customer data and evidence are purged from the device after handover plus the retention window, and immediately on logout | **H** | CTO |
| PRU-P09-13 | A courier partner's staff see only consignments assigned to their organisation | **H** | Logistics Manager |
| PRU-P09-14 | The panic alert transmits by every available channel and is never rate-limited or suppressed | **H** | HR Director |
| PRU-P09-15 | P09 records a cash collection; it posts no ledger entry and holds no balance | **H** | CFO |
| PRU-P09-16 | Every string including every error exists in Bengali, and Bengali is the default for rider roles | **H** | Logistics Manager |
| PRU-P09-17 | Sync status is visible to the rider and to the coordinator at all times | **C** | Logistics Manager |
| PRU-P09-18 | The offline journal and sync engine are the P02 implementation, not a second engine | **C** | CTO |

---

## 10. Data, Caching & State Model

### 10.1 Local Store — permitted, bounded, purged

| Object | Purpose | Retention | Reconstructible From |
|---|---|---|---|
| **Journal entries (pending)** | Durability of unsynced custody, status, evidence and cash actions — **the only locally authoritative data** | Until synced and acknowledged | Nothing |
| Journal entries (synced) | Reconciliation and dispute evidence | 7 days | Server-side record |
| Manifest and stop context | Offline execution | Shift + 24 h | M03 |
| Consignment and item detail | Verification against the manifest | Shift + 24 h | M03 |
| Device identity projection | Identification at collection | Per consignment, purged on handover + window | M17 |
| Media queue | Condition photographs pending upload | Until uploaded, bounded store | — |
| Cash float and collections | Shift reconciliation | Shift + 24 h | M20 |
| Session context | Time-boxed offline session | Per M29 policy | M29 |

### 10.2 Never Held Locally

| Item | Reason |
|---|---|
| Another rider's manifest, custody records or cash | Own-manifest scope (`05-04` §1 R16) |
| Customer history beyond the consignment in hand | PRU-P09-12 |
| Repair cost, margin or internal notes | `05-04` §5 |
| Payment credentials | Collection is cash or a gateway handoff |
| Route optimisation or SLA logic | PRU-P09-... (**PS-11**) |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.consignment`, manifest, routing constraints | **M03** | Read; submit status and exceptions |
| `fix.custody.event` | **M03 / M17** | **Submit — the portal's primary output** |
| `fix.asset`, condition, accessory checklist | **M17** | Read; submit condition and custody evidence |
| `fix.service.order` | M01 | Read for context |
| `fix.payment` — cash collection | M20 | Submit collection; read expected |
| `fix.vehicle.check` | M46 | Submit |
| `fix.attendance` — shift start and end | M55 / M21 | Submit |
| `fix.document` — evidence media, receipts | M24 | Resumable upload |
| `fix.ewaste.collection` | M18 | Read as a consignment type |
| `fix.tradein` collection | M14 | Read as a consignment type |
| `fix.rental` delivery and return | M13 | Read as a consignment type |
| `fix.party` — courier partner organisation | M33 / M42 | Read for scoping |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P09-01 | Manifest assigned by M03 | Push to the rider and prime consignment, device and route context before they leave connectivity | Appears on next sync; priming retried |
| AUT-P09-02 | Shift start | Present the M46 vehicle pre-use check where applicable and block the first stop until submitted | Grace period, then block and notify the coordinator |
| AUT-P09-03 | Geofence entered at a stop | Record arrival and open the stop automatically | Manual arrival with a recorded correction |
| AUT-P09-04 | Stop completion attempted | Evaluate the proof gate — scan, photograph, OTP, signature, accessories — and name precisely what is missing | Stop stays open; nothing silently accepted |
| AUT-P09-05 | Custody event captured | Submit to M17's chain and publish `consignment.custody_transferred` for M17, M24 and M23 (M03 §12.3) | Queued in the journal; replayed on sync |
| AUT-P09-06 | Exception recorded | Notify the coordinator, notify the customer through M27, and open a reschedule request | Exception queued; coordinator sees it on sync |
| AUT-P09-07 | Accessory discrepancy at handover | Flag it to the rider and the customer **before** signature, and record the customer's acknowledgement of the discrepancy | Block completion pending acknowledgement |
| AUT-P09-08 | Connectivity restored | Replay the journal in order, upload media resumably, and present the sync report | Retry with backoff; pending count always visible |
| AUT-P09-09 | Conflict on replay — e.g. a consignment reassigned while offline | Surface to the rider and the coordinator; never auto-resolve a custody conflict | Conflict remains open and reportable |
| AUT-P09-10 | Shift end | Compute expected cash, prompt reconciliation, record the variance, and block next-shift cash assignments above threshold | Block after grace period |
| AUT-P09-11 | Journal pending beyond threshold | Warn the rider and notify the coordinator that a device is holding unsynced custody records | Escalate; never discard |
| AUT-P09-12 | Panic alert raised | Transmit position and identity to the coordinator, the branch manager and the safety contact by every channel including SMS | Retry indefinitely |
| AUT-P09-13 | Local storage approaching capacity | Warn and refuse further media capture with an explanation rather than dropping queued evidence | Refuse capture; never discard |
| AUT-P09-14 | Consignment SLA at risk | Alert the coordinator console with the affected stops and the rider's position | Console display only |

---

## 12. Module Interfaces

### 12.1 Modules P09 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, offline session, device binding, remote wipe | OIDC via gateway |
| M28 Integration Platform | Sync endpoint, gateway, rate limits | Gateway |
| **M03 Logistics** | Manifest, consignment, routing constraints, courier assignment | REST + push |
| **M17 Asset Registry** | Device identity, accessory checklist definition, prior condition | REST, primed |
| M01 Service Order | Job context behind a consignment | REST |
| M20 Receivable | Amount due on delivery; cash float | REST |
| M46 Fleet | Vehicle pre-use checklist for the assigned rider | REST |
| M55 / M21 | Shift roster, geofence, attendance | REST |
| M24 Documents | Evidence media and receipt storage | REST (resumable) |
| M27 Communications | Customer notification on exception and reschedule | REST |
| M13 / M14 / M18 | Rental delivery, trade-in collection and e-waste collection as consignment types | REST |
| M42 / M33 | Courier partner organisation identity for scoping | REST |
| M65 Localisation | Bengali bundles | Build-time + REST |

### 12.2 What P09 Writes Back

| Target | What | Mechanism |
|---|---|---|
| **M03** | Consignment status, exceptions, reschedule requests, POD | Journal replay (idempotent) |
| **M17** | **Custody events with four proofs**, condition grade, accessory reconciliation | Journal replay |
| M20 | Cash collected on delivery; shift reconciliation and variance | Journal replay |
| M24 | Condition photographs, signatures, receipts | Resumable upload |
| M46 | Vehicle pre-use check and defect report | Journal replay |
| M55 / M21 | Shift start and end with geofence | Journal replay |
| M01 | Collection and delivery milestones affecting the job | Journal replay |
| M25 / M62 | POD completeness, custody integrity, exception and sync analytics | Event stream (queued) |

### 12.3 Events P09 Consumes

| Event | Source | Effect in P09 |
|---|---|---|
| `consignment.assigned` / `consignment.reassigned` | M03 | Add or remove from the manifest; prime or purge context |
| `consignment.rescheduled` | M03 | Update the stop and its window |
| `asset.flagged` (lost/stolen/disputed) | M17 | Block release of that device with the reason shown |
| `vehicle.off_road` | M46 | Warn the assigned rider and notify the coordinator |
| `payment.received` | M20 | Update the amount due at the stop |
| `sla.at_risk` | M03 / M01 | Surface on the coordinator console |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P09-01 | Google Maps Platform | Outbound | Navigation, route overview, geofencing |
| INT-P09-02 | Firebase Cloud Messaging | Inbound | Manifest assignment and priority alerts |
| INT-P09-03 | Device camera and GPS | Local | Condition photography with EXIF GPS and timestamp |
| INT-P09-04 | Bluetooth barcode scanners | Local | High-volume scanning at branch handover |
| INT-P09-05 | Mobile thermal printers | Outbound | Collection and delivery receipts, where deployed |
| INT-P09-06 | SMS gateway | Outbound | Recipient OTP and remote signature link; via M27 and M29 |
| INT-P09-07 | Courier partner tracking systems | Bidirectional | Status exchange for partners with their own systems; via M03 |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/sync/pull` | GET | Prime manifest, consignments, device and route context | M28 orchestrated |
| `/api/v1/sync/push` | POST | **Ordered, idempotent journal replay** — the P02 endpoint | M28 orchestrated |
| `/api/v1/logistics/manifest` | GET | The rider's day | M03 |
| `/api/v1/consignments/{id}` | GET/PATCH | Consignment detail and status | M03 |
| `/api/v1/assets/{id}/custody` | POST | **Custody transfer with evidence** | **M17** |
| `/api/v1/assets/{id}/condition` | POST | Condition grade with photographs | M17 |
| `/api/v1/consignments/{id}/exception` | POST | Structured exception with evidence | M03 |
| `/api/v1/payments/collect` | POST | Cash collection on delivery | M20 |
| `/api/v1/riders/me/cash-reconciliation` | POST | Shift-end cash reconciliation | M20 |
| `/api/v1/vehicles/{id}/checks` | POST | Vehicle pre-use check | M46 |
| `/api/v1/documents/upload` | POST | Resumable evidence upload | M24 |
| `/api/v1/safety/panic` | POST | Panic and safety alert | M29 / M27 |
| `/api/v1/logistics/coordinator/dashboard` | GET | Real-time consignment and rider state | M03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R16 Rider / Delivery Agent** | C R U | **Own manifest only** — stops, custody capture, exceptions, cash, safety |
| **R15 Logistics Coordinator** | C R U A | **Own area or central** — coordinator console: assignment, reschedule, SLA, rider oversight |
| **R38 External Party — courier partner staff** | C R U | **Only consignments assigned to their organisation**; never another partner's or an internal rider's manifest |
| R07 Dispatch Manager | R | Assigned zones — coordinator console visibility (per `05-04` §2) |

> **Per `05-04` §2, P09 access is held by R15, R16, R07 and R38 (courier sub-class) only.**
> A branch manager or workshop supervisor sees consignment status in P03, not P09. **No
> impersonation path into P09 exists.**

**Field-level restrictions.** A rider sees the consignment, the device identity, the customer's
name and delivery address, and the amount due. They never see repair cost, margin, internal
notes, the customer's other devices, or another rider's manifest or cash position. Courier
partner staff additionally never see 1000FiX internal references beyond the consignment.

**Segregation of duties.** The rider who collects cash does not reconcile the branch cash book
(`05-04` §6 SOD-12); they hand over to the branch cashier, and the reconciliation is a separate,
attributed action.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **POD completeness** | Custody events with all four proofs versus fewer — the `04-00` 100% KPI | M03, M17, M25 |
| **Custody integrity** | Gaps detected between consecutive custody events on a device — the `04-00` zero-break KPI | **M17**, M25 |
| **On-time performance** | Collections and deliveries within window, by rider, area and time of day | M03, M25 |
| **Offline reliability** | Shifts completed fully offline without loss; journal entries lost — the `04-00` 100% KPI | M30 |
| Exception analysis | Exceptions by structured reason, rider, area and time — the input to reducing failed stops | M03 |
| Stop duration | Time at stop, decomposed by capture step — identifies which proof slows the rider | M25 |
| Cash reconciliation | Completion per shift, variance value and resolution time | M20, CFO |
| Sync health | Success rate, duration, pending, conflicts, per rider per day | M30 |
| Coordinator activity | Assignments, reschedules, SLA interventions | M03 |
| Courier partner performance | POD completeness, on-time and exception rate by partner | M42, M03 |
| Application stability | Crash-free rate, battery consumption, device model distribution | M30 |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W5 Target | W8 Target |
|---|---|---|---|---|
| — | **POD capture completeness** | ~0% | 98% | **100%** |
| — | **On-time collection and delivery** | unmeasured | 88% | **> 93%** |
| — | **Custody breaks** | unknown | **Zero** | **Zero** |
| — | **Rider app offline reliability** | n/a | **100%** | **100%** |
| — | Custody events with all four proofs | 0% | 98% | **100%** |
| — | Condition photographs at collection | ~0% | **100%** | **100%** |
| — | Journal entries lost | n/a | **Zero** | **Zero** |
| — | Sync completion within 30 s of reconnection | n/a | 95% | **99.5%** |
| — | Damage disputes per 1,000 consignments | unmeasured | baselined | **−70% against baseline** |
| — | Cash reconciliation completed per shift | 0% | 95% | **99.5%** |
| — | Cash variance value per rider per month | untracked | baselined | **< 0.5% of collections** |
| — | Failed stops requiring reschedule | unmeasured | < 9% | **< 5%** |
| — | Courier partner POD completeness | ~0% | 92% | **100%** |
| — | Bengali string completeness | n/a | **100%** | **100%** |
| **KPI-002** *(supported)* | Turnaround time (IT) | unmeasured | < 30 h | **< 24 h** |

> **Register note.** The first four metrics are adopted verbatim from `04-00` §P09. P09 has
> **no KPI-0nn identifiers allocated**; all fourteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Flutter rider application** — manifest, stops, custody capture, exceptions, cash, safety | 58% |
| L5 | **Coordinator web view** — real-time dashboard, assignment, reschedule, SLA, rider oversight | 22% |
| L5 | Offline journal and sync — **the P02 implementation, reused** | 12% |
| L4 | Local encrypted store, resumable media transfer, scanner, camera and printer integration | 8% |

> **Reuse position.** The journal, replay and conflict engine built for P02 in Wave 2 is reused
> here in Wave 3. The 12% shown is integration and adaptation, not reconstruction. This is the
> single largest efficiency available in the portal suite and is stated in P02 §16.1 from the
> other side.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-210** | `p09_logistics_rider` — rider manifest and day, scan-to-open stops, **four-proof custody capture at collection and handover**, accessory checklist and reconciliation, seal and packaging, exception handling with reschedule, cash collection and shift reconciliation, safety alert, offline journal integration reusing P02, **and the coordinator web console** | Flutter application + web console | 22 PW |

> **CD register.** One ID, **CD-210**, claimed following CD-209 (P08). All CD IDs remain
> provisional pending the unified CD register required by audit finding M-01 in `02-05`.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M03 Logistics** | The consignment and the manifest. **W3 — P09 and M03 are delivered together** |
| **M17 Asset Registry** | Device identity and the custody chain this application feeds. **W2** |
| **P02** | **The offline journal and sync engine, reused here.** W2 — P09 cannot start before P02's engine is proven |
| M29 Identity & Security | Rider identity, offline session, device binding, remote wipe |
| M28 Integration Platform | The sync endpoint |
| M01 Service Order | Job context behind a consignment (W1–W2) |
| M20 Receivable | Cash collection and amount due (W3) |
| M46 Fleet | Vehicle pre-use check (**W5**) — **before W5, riders who drive complete no in-app check; this is a stated interim gap** |
| M24 Documents | Evidence media with retention |
| M27 Communications | Customer notification on exception |
| M13 / M14 / M18 | Rental, trade-in and e-waste consignment types added as those modules land (W6, W6, W8) |

### 16.4 Rollout

| Stage | Scope | Wave |
|---|---|---|
| Pilot | 15 riders on the Dhaka pick-and-drop route, including one poor-connectivity area | W3, month 10 |
| Internal rider fleet | All internal riders | W3, months 11–13 |
| Coordinator console | All logistics coordinators, central and branch | W3, with the rider rollout |
| Courier partners | Partner staff onboarded per partner, after internal rollout is stable | W4 |

> **Rollout position.** There is **no paper fallback after a route's cutover** — the application
> is the custody record. Each route's cutover is gated on its riders completing a full offline
> shift with complete POD capture. Courier partners follow only after the internal fleet is
> stable, because a partner experiencing early defects is a partner who reverts to WhatsApp
> permanently.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | A custody transfer cannot complete without scan, condition photograph, OTP and signature | Four negative tests, one per missing proof |
| AC-02 | Condition photography at collection cannot be skipped by any path | Negative test including API submission |
| AC-03 | The application operates fully for a complete shift offline with no feature unavailable and no data loss | Scripted offline shift with 15 riders |
| AC-04 | No journal entry is lost across app termination, device restart, storage pressure or forced update | Fault-injection suite |
| AC-05 | Replay after partial failure produces exactly one custody event per transfer | Idempotency test with induced mid-replay failure |
| AC-06 | Custody events replay in capture order; a collection cannot appear after its handover | Ordering test with shuffled transport |
| AC-07 | A custody conflict — consignment reassigned while offline — is surfaced, never auto-resolved | Scripted conflict scenario |
| AC-08 | Sync completes within 30 seconds of reconnection with complete integrity, and the sync report is visible to rider and coordinator | Timed reconnection test at full queue depth |
| AC-09 | An accessory discrepancy is flagged before the customer signs, and the acknowledgement is recorded | Scripted discrepancy scenario |
| AC-10 | The custody chain in M17 has no gap across a full collection → branch → workshop → branch → delivery cycle | End-to-end chain audit on 50 consignments |
| AC-11 | Photographs carry correct GPS and timestamps, survive queueing, and upload resumably after interruption | Evidence-integrity test |
| AC-12 | When the media queue reaches capacity, capture is refused with an explanation and no queued evidence is discarded | Storage-pressure test |
| AC-13 | Cash reconciles per shift, the variance is computed correctly, and an unresolved variance above threshold blocks next-shift cash assignments | Scripted scenario with M20 |
| AC-14 | A rider can access only their own manifest, custody records and cash | Isolation test including direct API call |
| AC-15 | A courier partner's staff see only their organisation's consignments | Isolation test across two partners |
| AC-16 | Customer data and evidence are purged from the device after handover plus the retention window, and immediately on logout | Storage audit after a scripted lifecycle |
| AC-17 | The panic alert transmits by every available channel within 10 seconds and is never suppressed | Safety drill on two routes |
| AC-18 | The coordinator console reflects a rider event within 15 seconds of sync and shows each rider's last-sync time | Latency test |
| AC-19 | The application runs acceptably on a mid-range Android device with battery under 15% per shift excluding navigation | Instrumented field measurement |
| AC-20 | Every string including every error renders in Bengali, and Bengali is the default for rider roles | Translation coverage report |
| AC-21 | A route's cutover is gated on its riders completing a full offline shift with complete POD capture | Cutover records per route |
| AC-22 | POD completeness reaches 100% and custody breaks remain at zero for three consecutive months | Three monthly custody-integrity reports |
| AC-23 | Logistics Manager, one coordinator and rider representatives sign off UAT, conducted in Bengali on real routes | Signed UAT record |

**Definition of done:** the twelve cross-portal standards in `04-00` §3, PS-08 offline capability,
plus the 23 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the rider device estate, and are devices company-issued or personal? Remote wipe and encrypted storage are unenforceable on BYOD | Logistics Manager / CTO | **W3 minus 3 months** |
| Q-02 | What is the minimum condition-photograph count at collection, and does it vary by device value or type? | Logistics Manager / Quality Manager | **W3 design** |
| Q-03 | Is a tamper seal used, and is it available at the point of collection for every rider? | Logistics Manager | W3 design |
| Q-04 | Are mobile thermal printers issued for receipts, or is a digital receipt by SMS sufficient? | Logistics Manager / CFO | W3 build |
| Q-05 | What is the cash variance threshold that blocks next-shift assignments, and who resolves it? | CFO / Logistics Manager | W3 design |
| Q-06 | Can a device be released to a person other than the account holder, and what evidence is required? | Legal / CCO | **W3 design** |
| Q-07 | What is the escalation path behind the panic alert, and who responds outside office hours? | HR Director / Logistics Manager | **W3 design** |
| Q-08 | Do courier partners use their own applications, requiring integration rather than P09 access? | Logistics Manager / CTO | W3 design |
| Q-09 | What retention applies to condition photographs, given volume across 50–150 riders daily? | Legal / CFO / Quality Manager | W3 build |
| Q-10 | How is a rider who drives without an assigned company vehicle handled — personal motorcycle, and what check applies? *(Matches M46 Q-04)* | Logistics Manager / HR Director | W3 design |
| Q-11 | Is continuous location during shift acceptable to riders, or is stop-event capture the agreed limit? *(Matches P02 Q-05 — one answer should serve both)* | HR Director / Logistics Manager | **W3 design** |
| Q-12 | What is the recovery procedure if a rider's device is lost with unsynced custody records? | Logistics Manager / CTO | **W3 design** |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P09 (capability set including the
coordinator web view, KPIs), §1, §3 PS-01…PS-12 (**PS-08**), §4 ·
`P02_Technician_Mobile_Application.md` §6 (**the journal and sync engine reused here**), §8.1 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` (customer tracking) ·
`P03_Admin_Operations_Portal.md` · `P05_Vendor_and_Supplier_Portal.md` (courier partner settlement) ·
`03_Modules/A_Service_Delivery_and_Operations/M03_Service_Logistics_and_Reverse_Logistics.md`
§12.3 (`consignment.collected`, `consignment.custody_transferred`) ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`
§5.3 FR-AST-020 (custody chain), FR-AST-015 (accessory checklist), §12.1 ·
`03_Modules/F_Asset_Equipment_and_Facilities/M46_Fleet_and_Vehicle_Management.md`
§5.4 FR-FLT-024 (pre-use check), §16.3 ·
`03_Modules/A_Service_Delivery_and_Operations/M06_Data_Services_and_Secure_Data_Handling.md`
(custody chain underpinning the secure-handling claim) ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§9 BRU-INV-12 (the reconciliation control pattern reused for cash) ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (**AS-13**, AS-14) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md`
§1 (R15, R16, R38), §2, §5, §6 SOD-12

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-FSM-012, BR-FSM-013,
BR-FSM-015, BR-SRM-010, BR-FIN-004, BR-DMS-002 ·
`1000FiX_Services_Company_Profile.md` §Additional Services (pick-and-drop), §Customer Benefits

**External benchmark**
[Proof of delivery apps for couriers — OTPs, photos, barcodes and signatures](https://onfleet.com/blog/proof-of-delivery-apps-couriers/) ·
[Electronic proof of delivery explained](https://locus.sh/blogs/electronic-proof-of-delivery/) ·
[The importance of proof of delivery in the last mile — time-stamped, geo-verified chain of custody](https://routetitan.com/en/blog/proof-of-delivery-in-the-last-mile) ·
[Chain of custody delivery and dispatch software — signed receipt establishing custody and condition on arrival](https://www.idsapp.com/chain-of-custody/) ·
[Courier driver app — every verification type, scan-to-open stops, offline operation](https://cxtsoftware.com/driver/) ·
[Proof of delivery apps 2026 — customer signature ahead of time by SMS link](https://spoke.com/dispatch/blog/proof-of-delivery-app) ·
[Last-mile delivery apps for businesses](https://trackobit.com/blog/last-mile-delivery-apps) ·
[Last-mile POD verification audit practice](https://www.mangoapps.com/templates/inspections/last-mile-delivery-pod-verification-audit)

---

*Portal P09 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
