---
id: FIX-ERP2-005
title: Pillar A — Core Service Operations Modules (M01–M06)
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL
---

# Pillar A — Core Service Operations
# Modules M01–M06: Features & Functions

**Pillar owner:** Service Operations Director
**Data domain:** Work, devices in 1000FiX custody, technician execution
**Modules:** M01 SRM · M02 FSM · M03 LOG · M04 FRD · M05 RMS · M06 DTS

---

# M01 — Service & Repair Management (SRM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M01 / `SRM` |
| **Status** | Expanded from v1.0 |
| **Priority** | P0 |
| **Wave** | W1 (core) → W2 (complete) |
| **Business owner** | Service Operations Director |
| **Delivery layers** | L2 (OCA fieldservice, helpdesk) + L5 (CD-001…008) |
| **Requirements** | FR-SRM-001 … FR-SRM-088 |
| **Effort** | 46 person-weeks |

## 1. Purpose

M01 owns the **service order** and **work order** — the two objects around which the entire
company revolves. Every device that enters 1000FiX custody, by any channel, for any business
line, is represented here. It is the operational backbone and the largest module in the system.

## 2. Scope Expansion Over v1.0

| v1.0 | v2.0 Addition |
|---|---|
| Single service order type | Polymorphic service order supporting 9 business lines via typed extensions |
| Field and walk-in only | + Workshop bench repair, pick & drop, RMA, refurbishment intake, data-services intake, rental service intake |
| Flat repair | Level 1 / Level 2 / Level 3 (board-level) repair routing with skill and equipment gating |
| One device per order | Multi-device job batches for corporate site visits and bulk drops |
| Basic checklist | Configurable diagnostic decision trees with conditional branching and photo/measurement evidence |
| Manual escalation | Multi-tier escalation matrix with automatic reassignment |
| — | Repair estimation with parts-and-labour build-up and margin visibility |
| — | Customer approval loop with time-boxed expiry and auto-cancellation |
| — | Second-opinion / peer-review workflow for high-value repairs |
| — | Job hold reasons with SLA clock suspension |

## 3. Functional Areas & Features

### 3.1 Service Intake

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-001 | Multi-channel intake | Create service orders from web portal, mobile app, WhatsApp, chatbot, hotline, walk-in counter, email, corporate portal bulk upload, marketplace, and partner referral | P0 |
| FR-SRM-002 | Order numbering | Auto-generate branch-aware, business-line-aware unique order numbers with configurable sequence masks | P0 |
| FR-SRM-003 | Service order classification | Classify by type: Warranty · Out-of-Warranty · AMC · RAMC · MSP · Emergency · Preventive · Rental Service · Data Service · Refurbishment · Recycling · Marketplace | P0 |
| FR-SRM-004 | Customer identification | Search or create customer at intake with duplicate detection on phone, email and NID | P0 |
| FR-SRM-005 | Device identification | Identify device by serial, IMEI, asset tag, QR label or model + purchase evidence; register new device inline | P0 |
| FR-SRM-006 | Entitlement check | Automatically evaluate brand warranty, extended warranty, AMC coverage, MSP entitlement and Privilege tier at intake and display the resulting commercial treatment | P0 |
| FR-SRM-007 | Complaint capture | Structured complaint taxonomy (symptom → category → sub-category) plus free text in Bengali or English, with voice-to-text | P1 |
| FR-SRM-008 | Accessory & condition log | Record accessories received, cosmetic condition, existing damage, and passwords/data-access notes with customer acknowledgement | P0 |
| FR-SRM-009 | Intake evidence | Capture photographs of the device at intake with timestamp, GPS and staff identity | P0 |
| FR-SRM-010 | Job sheet | Generate and print/e-mail the job sheet with terms, estimated TAT and tracking link | P0 |
| FR-SRM-011 | Multi-device batch | Group multiple devices from one customer or corporate site into a single job batch with a shared reference | P1 |
| FR-SRM-012 | Appointment booking | Reserve a service slot with capacity checking by branch, skill and service type | P1 |
| FR-SRM-013 | Emergency/priority intake | Flag emergency intake with premium tariff and out-of-hours routing | P2 |

### 3.2 Service Order Lifecycle

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-014 | Lifecycle state machine | Enforce states: Draft → Received → Diagnosing → Estimate Pending → Awaiting Approval → Approved → Parts Pending → In Repair → QC → Ready → Delivered/Collected → Invoiced → Closed → Archived, plus Cancelled, Rejected, Unrepairable, Abandoned | P0 |
| FR-SRM-015 | Transition guards | Block invalid transitions and require named preconditions (e.g. QC pass before Ready; approval before parts issue) | P0 |
| FR-SRM-016 | Hold management | Place a job on hold with a reason code (awaiting customer, awaiting parts, awaiting brand approval, customer unreachable) and suspend the SLA clock | P1 |
| FR-SRM-017 | Reassignment & transfer | Transfer a job between technicians, branches or workshops with a full custody trail | P1 |
| FR-SRM-018 | Split & merge | Split an order when a device needs separate repairs; merge duplicate orders for the same device | P2 |
| FR-SRM-019 | Cancellation & abandonment | Cancel with reason codes; auto-flag abandoned devices after a configurable dwell period with statutory notice generation | P1 |
| FR-SRM-020 | Reopen | Reopen a closed order within a policy window, linking to the original as a rework | P1 |

### 3.3 Diagnosis, Estimation & Approval

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-021 | Diagnostic templates | Maintain diagnostic decision trees per device category, brand, model and symptom, with conditional branching | P0 |
| FR-SRM-022 | Guided diagnosis | Present the diagnostic tree to the technician on mobile or bench terminal and record every answer, measurement and photo | P0 |
| FR-SRM-023 | Fault coding | Assign standard fault codes and root-cause categories used across warranty claims, quality analysis and predictive models | P0 |
| FR-SRM-024 | Repair-level routing | Classify required repair as Level 1 (basic), Level 2 (component), Level 3 (board/micro-soldering) and route to a qualified technician or workshop | P1 |
| FR-SRM-025 | Estimate build-up | Build an estimate from parts (with live stock and cost), labour (by rate card and repair level), transportation, and third-party charges, showing cost, price and margin | P0 |
| FR-SRM-026 | Estimate versioning | Maintain estimate versions with a full audit trail when scope changes after diagnosis | P1 |
| FR-SRM-027 | Customer approval loop | Send the quotation via SMS, WhatsApp, email and portal with accept/reject/part-accept options and a configurable expiry | P0 |
| FR-SRM-028 | Approval thresholds | Enforce internal approval above configurable value thresholds (branch manager, operations manager) in addition to customer approval | P0 |
| FR-SRM-029 | Declined-repair handling | On rejection, produce a diagnostic-fee invoice, reassemble instruction and return/collection task | P1 |
| FR-SRM-030 | Second opinion | Route high-value or contentious diagnoses to a senior technician for peer review before quoting | P2 |

### 3.4 Repair Execution

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-031 | Work order generation | Generate one or more work orders from a service order, each with scope, assignee, skill requirement and target time | P0 |
| FR-SRM-032 | Workshop bench management | Assign bench positions, track work-in-progress by bench, and show a live workshop board | P1 |
| FR-SRM-033 | Labour time tracking | Record start/pause/resume/stop per technician per work order; compute actual vs standard time | P0 |
| FR-SRM-034 | Parts requisition & consumption | Request, reserve, issue and consume parts against a work order with barcode/QR scanning and serial capture | P0 |
| FR-SRM-035 | Warranty parts segregation | Prevent brand-supplied warranty parts from being consumed on non-warranty jobs | P0 |
| FR-SRM-036 | Sub-contracting | Send a job or component to an external specialist or marketplace seller with cost, SLA and custody tracking | P2 |
| FR-SRM-037 | Repair notes & knowledge capture | Record repair steps, findings and tips; optionally promote to the knowledge base | P2 |
| FR-SRM-038 | Test & burn-in | Record post-repair testing including burn-in duration and pass/fail results | P1 |
| FR-SRM-039 | Unrepairable determination | Declare a device beyond economic repair with evidence, and route to trade-in, recycling or return | P1 |

### 3.5 Quality Control & Handover

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-040 | QC checklist enforcement | Require a passed QC checklist, appropriate to device type and repair level, before a job can reach Ready | P0 |
| FR-SRM-041 | Independent QC | Require QC by a person other than the repairing technician above a configurable value or risk threshold | P1 |
| FR-SRM-042 | Before/after evidence | Mandate before and after photographs with timestamp and GPS; store as the warranty evidence pack | P0 |
| FR-SRM-043 | Customer handover | Capture customer identity verification, accessory return confirmation and electronic signature at handover | P0 |
| FR-SRM-044 | Service report | Generate a bilingual service report detailing findings, work performed, parts replaced and warranty on the repair | P0 |
| FR-SRM-045 | Repair warranty | Apply and track a service warranty period per repair type; auto-classify returns within the window as warranty rework | P0 |
| FR-SRM-046 | Delivery coordination | Trigger logistics (M03) for pick & drop return, or notify the customer for counter collection | P1 |

### 3.6 SLA, Escalation & Rework

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-047 | SLA definition | Define SLAs by service type, business line, brand, customer tier, contract and priority, with working-calendar awareness | P0 |
| FR-SRM-048 | SLA clock | Run response, diagnosis, repair and total-resolution clocks independently, honouring holds and business hours | P0 |
| FR-SRM-049 | Escalation matrix | Fire escalations at 50%, 75%, 90% and 100% of SLA to defined roles, with acknowledgement tracking | P0 |
| FR-SRM-050 | Auto-reassignment | Reassign or re-prioritise automatically when an SLA is at imminent risk and the assignee is unresponsive | P2 |
| FR-SRM-051 | Rework detection | Automatically flag a new order for the same device and fault category within a configurable window as rework, and link the two | P0 |
| FR-SRM-052 | Rework accountability | Attribute rework to the original technician, branch and root cause; feed M23 quality and M21 incentives | P1 |
| FR-SRM-053 | Repeat-failure analysis | Identify devices, models or parts with abnormal repeat-failure rates and raise a quality alert | P2 |

### 3.7 Notifications & Customer Visibility

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-054 | Milestone notifications | Notify the customer at every lifecycle milestone via their preferred channels (SMS, WhatsApp, email, push, in-app inbox) | P0 |
| FR-SRM-055 | Tracking link | Issue a public, tokenised tracking link showing a visual status timeline without login | P0 |
| FR-SRM-056 | Proactive delay notice | Notify the customer proactively when a promised date will be missed, with a revised commitment | P1 |
| FR-SRM-057 | Post-service survey | Trigger CSAT and NPS surveys after handover; route detractors to M23 complaint handling | P1 |

### 3.8 Reporting & Operations Views

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-SRM-058 | Live operations board | Show all open jobs by state, branch, age, SLA risk and value, with drill-down | P0 |
| FR-SRM-059 | Ageing & WIP analysis | Report work-in-progress ageing, bottleneck states and cycle time per state | P1 |
| FR-SRM-060 | Technician workload view | Show current and queued load per technician and workshop | P1 |
| FR-SRM-061 | Printing & labelling | Print job sheets, device labels (QR), estimates, service reports and gate passes | P0 |
| FR-SRM-062 | API & events | Expose full CRUD and query APIs; publish `service_order.*` and `work_order.*` domain events | P0 |

*(FR-SRM-063 … FR-SRM-088 cover business-line extension behaviours — rental service intake,
data-service intake, refurbishment intake, recycling intake, marketplace job acceptance,
MSP-generated work — and are catalogued in Doc 11.)*

## 4. Key Entities

`fix.service.order` · `fix.work.order` · `fix.work.order.task` · `fix.job.batch` ·
`fix.diagnostic.template` · `fix.diagnostic.result` · `fix.fault.code` · `fix.estimate` ·
`fix.estimate.line` · `fix.approval.request` · `fix.qc.checklist` · `fix.qc.result` ·
`fix.hold.reason` · `fix.rework.link` · `fix.sla.policy` · `fix.sla.clock` ·
`fix.escalation.rule` · `fix.workshop.bench` · `fix.custody.event` · `fix.service.report` ·
`fix.repair.warranty` · `fix.device.condition.log`

## 5. Automations

| ID | Trigger | Action |
|---|---|---|
| AUT-SRM-01 | Order created | Entitlement evaluation, SLA assignment, acknowledgement notification, dispatch queue entry |
| AUT-SRM-02 | Diagnosis completed | Estimate draft generated from fault code → standard repair mapping |
| AUT-SRM-03 | Estimate sent | Approval timer started; reminders at 24h and 48h; auto-expire at configured limit |
| AUT-SRM-04 | Customer approved | Parts reserved, work order released, technician notified |
| AUT-SRM-05 | Parts unavailable | Parts request raised to M15/M16; job held; customer informed with revised ETA |
| AUT-SRM-06 | QC passed | Service report generated, invoice raised in M20, customer notified as Ready |
| AUT-SRM-07 | Warranty job closed | Warranty claim created in M09 with evidence pack attached |
| AUT-SRM-08 | Job idle beyond threshold | Escalation to branch manager; second escalation to operations manager |
| AUT-SRM-09 | Same device + fault within window | Rework flag raised, linked, quality event emitted |
| AUT-SRM-10 | Device uncollected beyond dwell period | Reminder sequence, then abandonment notice and disposal workflow |

## 6. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Service order automation rate | 20% | 85% |
| Average turnaround time — IT | unknown | < 24 hours |
| Average turnaround time — appliance on-site | unknown | < 4 hours |
| First-time fix rate | 70% | 88% |
| Rework rate | unmeasured | < 3% |
| QC pass rate at first attempt | unmeasured | > 95% |
| Estimate approval conversion | unmeasured | > 78% |
| SLA compliance | unmeasured | > 96% |
| Devices uncollected > 30 days | unmeasured | < 0.5% |

---

# M02 — Field Service & Dispatch Management (FSM)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M02 / `FSM` |
| **Status** | Expanded |
| **Priority** | P0 |
| **Wave** | W2 |
| **Delivery layers** | L2 (OCA field-service) + L4 (Traccar, VROOM/OSRM) + L5 (CD-009…015) |
| **Requirements** | FR-FSM-001 … FR-FSM-074 |
| **Effort** | 40 person-weeks |

## 1. Purpose

M02 decides **who does the work, when, and in what order**, tracks execution in the field,
and runs the technician mobile application. It converts the demand created by M01 into
scheduled, optimised, tracked and evidenced execution.

## 2. Scope Expansion Over v1.0

| v1.0 | v2.0 Addition |
|---|---|
| Rule-based auto-assignment | ML-assisted assignment scoring (via M26) targeting 70%+ fully automatic assignment |
| Daily route optimisation | Continuous re-optimisation on disruption (emergency, cancellation, traffic, technician unavailability) |
| Own technicians only | + Marketplace external engineers with capability, rating and commercial constraints |
| Single-visit jobs | Multi-visit jobs, multi-technician jobs, and jobs requiring a specialist plus an assistant |
| GPS tracking | + Geofenced auto check-in/out, idle detection, driving-behaviour signals |
| Offline capture | + Conflict resolution policy, 24-hour offline guarantee, selective sync by data class |
| — | Capacity planning and shift-aware availability from M21/M22 |
| — | Skills-and-certification gating enforced at assignment time |
| — | Field parts van replenishment recommendations |

## 3. Functional Areas & Features

### 3.1 Scheduling & Assignment

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-001 | Assignment engine | Score and rank candidate technicians on skill match, certification validity, zone, current load, travel time, van stock, customer preference, past rating and cost | P0 |
| FR-FSM-002 | Auto-assignment | Assign automatically when the top candidate exceeds a confidence threshold; otherwise present ranked options to the dispatcher | P0 |
| FR-FSM-003 | Dispatch board | Provide combined calendar, list and map views with drag-and-drop reassignment and instant conflict detection | P0 |
| FR-FSM-004 | Capacity planning | Show available capacity by zone, skill and day; highlight over/under capacity ahead of time | P1 |
| FR-FSM-005 | Territory & zone management | Define zones and geofences per branch; assign technicians to zones with overflow rules | P1 |
| FR-FSM-006 | Shift & roster integration | Consume shifts, leave and holidays from M21 so unavailable technicians are never offered | P1 |
| FR-FSM-007 | Certification gate | Refuse assignment of brand warranty work to a technician whose certification for that brand has expired | P0 |
| FR-FSM-008 | Multi-technician jobs | Assign a crew with defined roles (lead, assistant, specialist) and track each member's time | P2 |
| FR-FSM-009 | Multi-visit jobs | Plan and track jobs requiring several visits, keeping the SLA and customer view coherent | P1 |
| FR-FSM-010 | Emergency insertion | Insert an emergency job and automatically re-optimise the affected technician's remaining route | P1 |
| FR-FSM-011 | External capacity | Offer overflow jobs to marketplace sellers (M12) under commercial and quality constraints | P2 |

### 3.2 Route Optimisation

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-012 | Daily route solve | Solve the vehicle routing problem nightly for all technicians, honouring time windows, skills, capacity and priorities | P1 |
| FR-FSM-013 | Live re-optimisation | Re-solve affected routes when a job is added, cancelled, extended or a technician becomes unavailable | P1 |
| FR-FSM-014 | Travel-time estimation | Estimate travel using road-network data, with selective real-time traffic for the Dhaka metro area | P1 |
| FR-FSM-015 | Route publishing | Push the optimised route to the technician app with turn-by-turn navigation handoff | P1 |
| FR-FSM-016 | Route adherence | Measure planned vs actual route and flag significant deviations | P2 |

### 3.3 Field Execution (Technician Application)

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-017 | Job queue | Show today's jobs in optimised order with customer, device, history, complaint and entitlement | P0 |
| FR-FSM-018 | Accept / decline | Accept or decline a job with a reason; decline triggers reassignment | P0 |
| FR-FSM-019 | Navigation | Launch turn-by-turn navigation to the job location | P0 |
| FR-FSM-020 | Automatic timestamps | Capture departed, arrived, started, paused, completed, left — with GPS and geofence validation | P0 |
| FR-FSM-021 | On-site diagnosis | Run the M01 diagnostic tree on the device with offline support | P0 |
| FR-FSM-022 | Parts scanning | Scan van stock by barcode/QR to consume parts; request parts not in van | P0 |
| FR-FSM-023 | Photo & media capture | Capture before/after photos, short videos and audio notes with automatic metadata | P0 |
| FR-FSM-024 | E-signature | Capture the customer's signature on-screen with declaration text in Bengali or English | P0 |
| FR-FSM-025 | On-site payment | Collect cash, mobile money or card at the customer site and reconcile to the branch cash book | P1 |
| FR-FSM-026 | Offline operation | Operate fully offline for 24 hours; queue all actions; sync automatically within 30 seconds of reconnection with 100% integrity | P0 |
| FR-FSM-027 | Conflict resolution | Resolve concurrent edits deterministically with a server-authoritative policy and a technician-visible reconciliation log | P0 |
| FR-FSM-028 | Knowledge access | Access repair manuals, wiring diagrams and past repair notes offline | P2 |
| FR-FSM-029 | In-app messaging | Message dispatch, the workshop and (where permitted) the customer, with offline queueing | P2 |
| FR-FSM-030 | Earnings & performance | Show the technician their jobs, ratings, first-time-fix rate and earned incentives | P2 |
| FR-FSM-031 | Safety & duty of care | Record site safety checks, lone-worker check-in, and panic alert | P2 |

### 3.4 Tracking & Customer Visibility

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-032 | Live technician tracking | Stream technician positions at a configurable interval to a live operations map | P0 |
| FR-FSM-033 | Customer tracking page | Give the customer a live map with technician position, photo, name and ETA on the day of service | P0 |
| FR-FSM-034 | ETA calculation | Recalculate and publish ETA as conditions change; notify the customer on material change | P1 |
| FR-FSM-035 | Geofence events | Raise automatic events on entering/leaving customer, branch and warehouse geofences | P1 |
| FR-FSM-036 | Privacy controls | Suspend location capture outside working hours and during breaks; log all access to location history | P0 |

### 3.5 Field Exceptions

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FSM-037 | Customer absent | Record a failed visit with evidence, notify the customer, and trigger rescheduling or a charge per policy | P1 |
| FR-FSM-038 | Job cannot be completed | Record reason (parts, access, complexity, safety), convert to a follow-up visit or workshop transfer | P1 |
| FR-FSM-039 | Scope change on site | Raise a revised estimate on site and obtain approval before proceeding | P1 |
| FR-FSM-040 | Device collection on site | Convert a failed on-site repair into a pick & drop consignment handled by M03 | P1 |

*(FR-FSM-041 … FR-FSM-074 cover van stock management, technician performance instrumentation,
dispatcher productivity tools, bulk site-visit planning, and external-engineer dispatch and are
catalogued in Doc 11.)*

## 4. Key Entities

`fix.dispatch.job` · `fix.assignment.score` · `fix.technician.profile` · `fix.technician.shift` ·
`fix.zone` · `fix.geofence` · `fix.route.plan` · `fix.route.stop` · `fix.location.ping` ·
`fix.visit` · `fix.visit.exception` · `fix.van.stock` · `fix.van.replenishment` ·
`fix.field.session` · `fix.offline.journal` · `fix.crew`

## 5. Automations

| ID | Trigger | Action |
|---|---|---|
| AUT-FSM-01 | Service order ready for dispatch | Candidate scoring; auto-assign or queue for dispatcher |
| AUT-FSM-02 | Nightly 05:00 | Full route optimisation for the next day; publish routes; notify technicians |
| AUT-FSM-03 | Emergency job created | Identify nearest qualified available technician; re-optimise route; notify |
| AUT-FSM-04 | Technician marks arrived | Notify customer; start on-site SLA clock |
| AUT-FSM-05 | Job completed offline then synced | Reconcile parts, time and evidence; release invoice |
| AUT-FSM-06 | Technician idle > threshold during shift | Alert dispatcher |
| AUT-FSM-07 | Van stock below par after job | Generate replenishment request to branch store |
| AUT-FSM-08 | Certification expiring in 30 days | Notify technician, manager and M22; restrict new warranty assignments at expiry |

## 6. KPIs

| KPI | Baseline | Target |
|---|---|---|
| Jobs per technician per day | 4–5 | 8–9 |
| Technician utilisation | 55% | 82% |
| Automatic assignment rate | 0% | 70% |
| Travel time as % of working day | ~35% | < 22% |
| On-time arrival within promised window | unmeasured | > 92% |
| Offline sync integrity | — | 100% |
| App daily active usage | — | > 95% of active technicians |

---

# M03 — Logistics, Pick & Drop and Reverse Logistics (LOG)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M03 / `LOG` |
| **Status** | ★ New in v2.0 |
| **Priority** | P1 |
| **Wave** | W3 |
| **Delivery layers** | L5 (CD-016…020) with L4 mapping services |
| **Requirements** | FR-LOG-001 … FR-LOG-042 |
| **Effort** | 22 person-weeks |

## 1. Purpose

Every device, part, rental asset and recycled unit that moves between a customer, a branch,
a workshop, a vendor or a recycler is a **consignment** with an unbroken chain of custody.
M03 owns that movement. Without it, pick & drop, rental delivery, refurbishment collection
and e-waste collection all remain phone-coordinated and legally undefended.

**Evidence:** Business Plan §Pick & Drop; Service App SOW §"Logistics team Interface —
real-time dashboard of pending orders, delivered/cancelled, schedule/re-schedule,
service-center-wise separate/central logistics team assignment"; Company Profile §Pick & Drop.

## 2. Functional Areas & Features

### 2.1 Consignment Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-001 | Consignment creation | Create a consignment from any source: pick & drop request, rental delivery, inter-branch transfer, vendor return, recycling collection, refurbishment intake, marketplace fulfilment | P1 |
| FR-LOG-002 | Multi-leg journeys | Model a journey as ordered legs (customer → branch → workshop → branch → customer), each with its own carrier, status and evidence | P1 |
| FR-LOG-003 | Item manifest | List every item in a consignment with serial, description, declared value, condition and photographs | P1 |
| FR-LOG-004 | Packaging & sealing | Record packaging type, seal/tamper-tag number and weight/dimensions | P2 |
| FR-LOG-005 | Consignment states | Requested → Scheduled → Out for Collection → Collected → In Transit → At Hub → Out for Delivery → Delivered → Exception → Returned | P1 |

### 2.2 Chain of Custody

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-006 | Custody handover | Require a scan plus identity capture at every handover between parties, with GPS and timestamp | P1 |
| FR-LOG-007 | Proof of collection (POC) | Capture customer signature, photo of the sealed package and OTP verification at collection | P1 |
| FR-LOG-008 | Proof of delivery (POD) | Capture recipient identity, signature, photo and OTP at delivery | P1 |
| FR-LOG-009 | Custody ledger | Maintain an immutable, queryable custody ledger per item — who held it, when, where | P0 |
| FR-LOG-010 | Tamper & discrepancy | Record seal breaks, weight discrepancies and condition changes; raise an incident automatically | P1 |
| FR-LOG-011 | High-value handling | Apply enhanced controls (dual signature, insurance flag, escort) above a declared-value threshold | P2 |

### 2.3 Scheduling & Routing

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-012 | Pickup/delivery scheduling | Offer time windows by area, honouring rider capacity and cut-off times | P1 |
| FR-LOG-013 | Rider assignment | Assign to an internal rider or an external courier partner based on area, value, size and cost | P1 |
| FR-LOG-014 | Route manifest | Build the rider's daily manifest with optimised sequence | P1 |
| FR-LOG-015 | Rescheduling | Reschedule at customer or operational request with notification and SLA adjustment | P1 |
| FR-LOG-016 | Central vs branch logistics | Support both a central logistics team and branch-assigned riders, configurable per area | P1 |

### 2.4 Courier Partner Integration

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-017 | Partner onboarding | Register courier partners with service areas, rate cards, SLAs and API credentials | P2 |
| FR-LOG-018 | Booking API | Book a consignment with a partner and receive their tracking reference | P2 |
| FR-LOG-019 | Status ingestion | Ingest partner tracking events by webhook or polling and map them to internal states | P2 |
| FR-LOG-020 | Partner reconciliation | Reconcile partner invoices against consignments delivered and rate cards | P2 |
| FR-LOG-021 | Cross-border shipping | Support international shipments with customs documentation and distance-based charging | P3 |

### 2.5 Charging & Reverse Flows

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-LOG-022 | Distance/zone-based charging | Calculate the customer's logistics charge by zone, distance, weight, value and service level | P1 |
| FR-LOG-023 | Free-logistics entitlement | Waive charges where the contract, warranty terms or Privilege tier entitles the customer | P1 |
| FR-LOG-024 | Reverse logistics — returns to vendor | Move defective parts back to vendors with RMA references and credit tracking | P1 |
| FR-LOG-025 | Reverse logistics — recycling | Move end-of-life devices to recycling partners with disposal certificates (M18) | P2 |
| FR-LOG-026 | Failed delivery handling | Apply the re-attempt policy, then return to origin with charge rules | P1 |

*(FR-LOG-027 … FR-LOG-042 cover the rider mobile application, hub operations, insurance,
loss/damage claims, and logistics analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.consignment` · `fix.consignment.leg` · `fix.consignment.item` · `fix.custody.event` ·
`fix.rider` · `fix.route.manifest` · `fix.courier.partner` · `fix.courier.rate` ·
`fix.pod.record` · `fix.logistics.charge` · `fix.logistics.incident`

## 4. KPIs

| KPI | Target |
|---|---|
| On-time collection | > 93% |
| On-time delivery | > 93% |
| Custody-break incidents | 0 |
| Loss/damage rate | < 0.1% of consignments |
| Pick & drop cost per consignment | Baselined in W3, −15% by W6 |
| POD capture completeness | 100% |

---

# M04 — Front Desk, Queue & Branch Operations (FRD)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M04 / `FRD` |
| **Status** | Expanded (promoted from a v1.0 sub-feature) |
| **Priority** | P1 |
| **Wave** | W1 |
| **Delivery layers** | L5 (CD-021…023) |
| **Requirements** | FR-FRD-001 … FR-FRD-031 |
| **Effort** | 13 person-weeks |

## 1. Purpose

51+ service centres receive walk-in customers all day. M04 is the counter system: token
queue, intake, handover, cash drawer, shift discipline and daily branch operations. It is
the module that most staff touch most often, so its usability determines adoption.

## 2. Functional Areas & Features

### 2.1 Queue Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FRD-001 | Token issuance | Issue a queue token by service category from a kiosk, counter or a customer's phone (QR) | P1 |
| FR-FRD-002 | Queue display | Drive a waiting-area display showing tokens now serving, per counter, in Bengali and English | P1 |
| FR-FRD-003 | Wait-time estimation | Estimate and display expected wait based on live throughput | P2 |
| FR-FRD-004 | Priority queueing | Give Privilege Gold/Diamond, corporate and elderly/disabled customers priority | P1 |
| FR-FRD-005 | Appointment check-in | Check in a pre-booked appointment and merge it into the queue at the reserved time | P1 |
| FR-FRD-006 | No-show and recall | Recall a skipped token once, then mark no-show | P2 |
| FR-FRD-007 | Counter assignment | Route tokens to counters by capability (intake, collection, payment, corporate) | P2 |

### 2.2 Counter Operations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FRD-008 | Fast intake | Complete a walk-in intake in under three minutes with search-first customer lookup and device recall | P1 |
| FR-FRD-009 | Counter dashboard | Show the agent everything for the customer in front of them: open jobs, devices, contracts, dues, tier | P1 |
| FR-FRD-010 | Collection & handover | Verify identity, retrieve the device from storage location, confirm accessories, capture signature | P1 |
| FR-FRD-011 | Storage location tracking | Record and find the physical shelf/bin where a device is stored | P1 |
| FR-FRD-012 | Counter sales | Sell parts, accessories, Privilege memberships, warranty extensions and AMC at the counter | P1 |
| FR-FRD-013 | Quotation printing | Print or send an estimate from the counter | P1 |

### 2.3 Cash & Shift Control

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FRD-014 | Shift open/close | Open and close a shift with an opening float and a counted closing balance | P1 |
| FR-FRD-015 | Cash drawer | Record every cash movement — receipts, refunds, petty expenses, banking | P1 |
| FR-FRD-016 | Payment capture | Take cash, card, bKash, Nagad and bank transfer at the counter, with instant receipt | P1 |
| FR-FRD-017 | Variance handling | Record and require approval for any cash variance at close | P1 |
| FR-FRD-018 | Banking deposit | Record deposits to bank with slip reference and reconcile in M19 | P1 |
| FR-FRD-019 | High-value cash controls | Require NID capture for cash above the statutory threshold | P0 |

### 2.4 Branch Daily Operations

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-FRD-020 | Branch opening checklist | Enforce a daily opening checklist (safety, equipment, stock, staffing) | P2 |
| FR-FRD-021 | Branch dashboard | Show today's intake, WIP, ready-for-collection, overdue, revenue and queue health | P1 |
| FR-FRD-022 | Shift handover notes | Record structured handover notes between shifts | P2 |
| FR-FRD-023 | Uncollected device report | List devices ready but uncollected, by age, with reminder actions | P1 |
| FR-FRD-024 | Branch closing checklist | Enforce closing: cash counted, devices secured, jobs updated, alarms set | P2 |

*(FR-FRD-025 … FR-FRD-031 cover the kiosk application, receipt/label printing, counter
performance analytics and multi-counter configuration — catalogued in Doc 11.)*

## 3. Key Entities

`fix.queue.token` · `fix.queue.counter` · `fix.queue.config` · `fix.branch.shift` ·
`fix.cash.drawer` · `fix.cash.movement` · `fix.storage.location` · `fix.branch.checklist`

## 4. KPIs

| KPI | Target |
|---|---|
| Average walk-in intake time | < 3 minutes |
| Average queue wait time | < 12 minutes |
| Counter cash variance incidents | < 1 per branch per month |
| Devices located within 60 seconds at collection | > 98% |
| Shift closed on time | > 97% |

---

# M05 — Remote Support & Managed Services (RMS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M05 / `RMS` |
| **Status** | ★ New in v2.0 |
| **Priority** | P1 |
| **Wave** | W5 |
| **Delivery layers** | L4 (monitoring, remote access) + L5 (CD-024…029) + optional L6 (RMM agent) |
| **Requirements** | FR-RMS-001 … FR-RMS-061 |
| **Effort** | 37 person-weeks |

## 1. Purpose

The Company's business plan commits to **six categories of managed service contract** and a
**24/7 technical support** operation. M05 is the system that delivers them: remote assistance
sessions, proactive monitoring of client IT estates, alerting, patch and update management,
backup oversight, a managed service desk, and contractual SLA reporting.

This is the highest-margin B2B line described anywhere in the Company's documentation and
currently has no system at all.

**Evidence:** Business Plan §Managed Service Contracts (Basic, Comprehensive, Security-focused,
Cloud Services, DR/BC, IT Strategy Consulting) and §24/7 Technical Support (remote, software,
hardware, networking, mobile, email/account support); Service App SOW §"Remote service feature…
like the TeamViewer app".

## 2. Functional Areas & Features

### 2.1 Remote Assistance

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-001 | Session initiation | Start a remote support session from a ticket, with a one-time code issued to the customer | P1 |
| FR-RMS-002 | Consent & authorisation | Require explicit, logged customer consent before any remote connection; display what will be accessed | P0 |
| FR-RMS-003 | Attended & unattended access | Support attended sessions (customer present) and, for contracted assets only, unattended access | P1 |
| FR-RMS-004 | Session recording | Record sessions where policy requires; store as evidence with retention rules in M24 | P1 |
| FR-RMS-005 | Session billing | Meter session duration and bill by contract entitlement or on demand | P1 |
| FR-RMS-006 | File transfer control | Permit, log and scan file transfers during a session | P1 |
| FR-RMS-007 | Session handover | Transfer a live session between agents with context | P2 |

### 2.2 Monitored Estate

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-008 | Asset onboarding | Register a client's monitored assets — endpoints, servers, network devices, printers, cloud subscriptions — linked to the M17 registry | P1 |
| FR-RMS-009 | Agent deployment | Deploy, register and health-check a monitoring agent per asset | P1 |
| FR-RMS-010 | Agentless monitoring | Monitor network devices via SNMP/ICMP where an agent cannot be installed | P1 |
| FR-RMS-011 | Metric collection | Collect CPU, memory, disk, temperature, uptime, service state, backup state, security state and store as time series | P1 |
| FR-RMS-012 | Software inventory | Maintain installed-software and licence inventory per asset | P2 |
| FR-RMS-013 | Configuration baseline | Record a configuration baseline and detect drift | P2 |
| FR-RMS-014 | Health score | Compute a health index per asset and per client estate | P2 |

### 2.3 Alerting & Incident Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-015 | Alert rules | Define thresholds and conditions per asset class, client and contract tier | P1 |
| FR-RMS-016 | Alert-to-ticket | Automatically raise a service ticket from an alert with de-duplication and correlation | P1 |
| FR-RMS-017 | Escalation policy | Escalate unacknowledged alerts through an on-call rota with acknowledgement tracking | P1 |
| FR-RMS-018 | Runbook automation | Attach and execute remediation runbooks; record what was attempted and the outcome | P2 |
| FR-RMS-019 | Maintenance windows | Suppress alerting during agreed maintenance windows | P1 |
| FR-RMS-020 | Major incident handling | Declare a major incident, notify all affected client contacts, and run a structured resolution and post-incident review | P2 |

### 2.4 Patch, Update & Security Management

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-021 | Patch inventory | Track available and missing patches per asset | P2 |
| FR-RMS-022 | Patch scheduling | Schedule patch deployment by ring, window and client approval | P2 |
| FR-RMS-023 | Patch reporting | Report compliance per client and per asset class | P2 |
| FR-RMS-024 | Antivirus/EDR oversight | Monitor endpoint protection status and raise alerts on gaps | P2 |
| FR-RMS-025 | Vulnerability reporting | Report known vulnerabilities on the monitored estate to the client | P3 |

### 2.5 Managed Service Desk

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-026 | Client ticketing | Accept tickets from client contacts by portal, email, phone or chat, scoped to their entitlement | P1 |
| FR-RMS-027 | Ticket classification | Classify by service, urgency, impact and derived priority | P1 |
| FR-RMS-028 | Contractual SLA | Apply response and resolution SLAs from the client's contract; measure and report breach | P1 |
| FR-RMS-029 | Knowledge base | Maintain solution articles, publish selected articles to client self-service | P2 |
| FR-RMS-030 | Problem management | Link recurring incidents to a problem record with root-cause and permanent fix tracking | P2 |
| FR-RMS-031 | Change management | Record and approve changes to client environments with rollback plans | P2 |
| FR-RMS-032 | Field escalation | Escalate a remote ticket into an on-site visit through M02 | P1 |

### 2.6 Contract Delivery & Reporting

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-RMS-033 | Entitlement consumption | Track consumption against contracted hours, incidents, assets or seats (from M08) | P1 |
| FR-RMS-034 | Overage handling | Detect overage and bill it or request an uplift | P1 |
| FR-RMS-035 | Service reports | Generate periodic client service reports: SLA attainment, incidents, patch compliance, health, recommendations | P1 |
| FR-RMS-036 | Service review meetings | Schedule, record and track actions from client service review meetings | P2 |
| FR-RMS-037 | SLA credits | Calculate service credits automatically on breach and pass them to M20 for crediting | P1 |
| FR-RMS-038 | 24/7 coverage model | Define follow-the-clock coverage, on-call rotas and out-of-hours cost recovery | P1 |

*(FR-RMS-039 … FR-RMS-061 cover backup-service oversight, cloud subscription management,
DR/BC test tracking, IT strategy consulting deliverables and client CSAT — catalogued in Doc 11.)*

## 3. Key Entities

`fix.msp.contract.instance` · `fix.monitored.asset` · `fix.monitor.agent` · `fix.metric.series` ·
`fix.alert.rule` · `fix.alert` · `fix.msp.ticket` · `fix.problem.record` · `fix.change.record` ·
`fix.remote.session` · `fix.patch.job` · `fix.runbook` · `fix.oncall.rota` ·
`fix.maintenance.window` · `fix.service.review` · `fix.sla.credit`

## 4. KPIs

| KPI | Target |
|---|---|
| Monitored assets under management | 5,000 by end of W6 |
| Alert-to-ticket automation rate | > 90% |
| Mean time to acknowledge (P1 alert) | < 10 minutes |
| Mean time to resolve (P1 incident) | < 4 hours |
| Contractual SLA attainment | > 98% |
| Remote resolution rate (no site visit) | > 65% |
| MSP gross margin | > 55% |

---

# M06 — Data Services: Recovery, Backup & Destruction (DTS)

| Attribute | Value |
|---|---|
| **Module ID / Code** | M06 / `DTS` |
| **Status** | ★ New in v2.0 |
| **Priority** | P2 |
| **Wave** | W6 |
| **Delivery layers** | L5 (CD-030…032) |
| **Requirements** | FR-DTS-001 … FR-DTS-034 |
| **Effort** | 18 person-weeks |

## 1. Purpose

Data recovery, backup subscriptions and certified data destruction are billable services the
Company already offers. They are also the services with the **highest confidentiality risk** in
the entire business: 1000FiX takes possession of customers' data.

M06 makes these services deliverable and, critically, **defensible** — with chain of custody,
access control, evidence and certificates that satisfy ISO 27001 and the Bangladesh Digital
Security Act.

**Evidence:** Business Plan §Data Recovery Services (hard drive, SSD, RAID, USB, memory card,
mobile, email/database), §Data Backup Solutions (cloud, on-site, hybrid, continuous data
protection, archiving), §Refurbishment "Data Wiping and Privacy Protection",
§Recycling "Data Destruction".

## 2. Functional Areas & Features

### 2.1 Data Recovery

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DTS-001 | Recovery case intake | Open a recovery case with media type, failure symptoms, criticality, target data description and customer declarations | P2 |
| FR-DTS-002 | Media chain of custody | Track the physical media through evaluation, cleanroom, imaging, recovery, verification and return, with sealed-container controls | P0 |
| FR-DTS-003 | Free evaluation stage | Record a no-charge evaluation with a recoverability assessment and a firm quotation | P2 |
| FR-DTS-004 | Recovery methodology log | Record the technique applied (logical, firmware, mechanical, chip-off, RAID reconstruction) and every step taken | P2 |
| FR-DTS-005 | Success-based pricing | Support no-recovery-no-fee and tiered pricing by data volume and complexity | P2 |
| FR-DTS-006 | Recovered-data inventory | List recovered files/volumes by type and size without exposing content | P1 |
| FR-DTS-007 | Data handover | Deliver recovered data on approved media or secure transfer, with signed receipt | P1 |
| FR-DTS-008 | Retention & purge | Hold recovered data only for the agreed window, then verifiably purge; issue a purge certificate | P0 |
| FR-DTS-009 | Access restriction | Restrict access to recovery workspaces to named, MFA-authenticated staff; log every access | P0 |
| FR-DTS-010 | Confidentiality undertaking | Capture staff confidentiality undertakings per case and customer NDAs where required | P0 |

### 2.2 Backup & Archival Services

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DTS-011 | Backup plan definition | Define a customer's backup plan — scope, schedule, retention, destination (cloud, on-site, hybrid), encryption | P2 |
| FR-DTS-012 | Backup job monitoring | Monitor backup job outcomes and raise incidents on failure or missed schedule | P2 |
| FR-DTS-013 | Restore testing | Schedule and record periodic restore tests with evidence for the customer's DR obligations | P2 |
| FR-DTS-014 | Capacity & usage billing | Meter storage consumed and bill against the subscription tier with overage | P2 |
| FR-DTS-015 | Archival service | Manage long-term archival with retrieval SLAs and retrieval charging | P3 |
| FR-DTS-016 | Continuous data protection | Track CDP-enabled assets and recovery point coverage | P3 |

### 2.3 Data Migration

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DTS-017 | Migration job | Manage device-to-device or platform migrations as a service with scope, checklist and verification | P3 |
| FR-DTS-018 | Migration verification | Record source/target counts and integrity verification, and obtain customer sign-off | P3 |

### 2.4 Secure Data Destruction

| FR ID | Feature | Function | Pri |
|---|---|---|:--:|
| FR-DTS-019 | Wipe request | Accept a destruction request from refurbishment (M14), recycling (M18), a customer, or a corporate decommission project | P1 |
| FR-DTS-020 | Wipe method & standard | Record the erasure standard applied per media type and verify completion | P0 |
| FR-DTS-021 | Physical destruction | Record shredding/degaussing where erasure is not possible, with photographic evidence | P1 |
| FR-DTS-022 | Certificate of destruction | Issue a serialised, verifiable certificate per device with method, operator, date and witness | P0 |
| FR-DTS-023 | Bulk decommission projects | Manage corporate bulk decommissioning with reconciliation against the client's asset list | P2 |
| FR-DTS-024 | Exception handling | Handle media that cannot be erased or verified, with escalation and customer notification | P1 |

*(FR-DTS-025 … FR-DTS-034 cover cleanroom scheduling, specialist equipment tracking, partner
lab referral, and data-services analytics — catalogued in Doc 11.)*

## 3. Key Entities

`fix.data.case` · `fix.media.item` · `fix.media.custody.event` · `fix.recovery.attempt` ·
`fix.recovered.inventory` · `fix.backup.plan` · `fix.backup.run` · `fix.restore.test` ·
`fix.wipe.request` · `fix.destruction.certificate` · `fix.cleanroom.booking` ·
`fix.data.access.log`

## 4. Controls (Non-Negotiable)

| Control | Requirement |
|---|---|
| Least privilege | Only case-assigned staff may access a case workspace |
| Dual control | Media entering and leaving the secure area requires two signatures |
| Encryption | All recovered data encrypted at rest with per-case keys |
| No export | Recovered data may not leave the controlled environment except by the approved handover path |
| Full audit | Every read, copy, transfer and deletion is logged immutably and retained 5 years |
| Time-boxed retention | Recovered data purged automatically at the agreed date unless a documented hold applies |

## 5. KPIs

| KPI | Target |
|---|---|
| Recovery success rate (accepted cases) | > 82% |
| Average recovery turnaround | < 7 days |
| Chain-of-custody exceptions | 0 |
| Certificates issued within 24h of destruction | 100% |
| Backup job success rate (managed customers) | > 99% |
| Restore tests completed on schedule | 100% |

---

*Next document: `06_Pillar_B_Customer_Commercial_Revenue_Modules.md`*
