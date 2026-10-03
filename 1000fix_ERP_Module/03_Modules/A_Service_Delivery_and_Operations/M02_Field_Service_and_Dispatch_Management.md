---
id: FIX-ERP2-M02
module_id: M02
module_code: FSM
module_name: Field Service & Dispatch Management
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Service Operations Director
system_owner: Service Squad
priority: P0
wave: W2
---

# M02 — Field Service & Dispatch Management
### Category A · Code `FSM` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M02 |
| **Module code** | `FSM` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (re-scoped — shift and roster maintenance moved to M55) |
| **Priority** | **P0** — cannot be descoped |
| **Delivery wave** | W2 (Months 5–8) |
| **Business owner** | Service Operations Director |
| **System owner** | Service Squad |
| **Delivery layers** | L2 (OCA `fieldservice`) + L4 (Traccar, VROOM/OSRM) + L5 (custom + Flutter app) |
| **Custom modules** | `cd_dispatch`, `cd_technician`, `cd_route`, `cd_geofence`, `cd_van_stock`, `cd_field_session`, `cd_offline_sync` |
| **Requirement range** | FR-FSM-001 … FR-FSM-072 |
| **Requirement count** | **63** *(measured 2026-08-13; 11 allocated identifiers retired unused — see below)* |
| **Effort estimate** | 40 person-weeks |
| **Depends on** | M01 Service Order · M55 Workforce Scheduling · M22 Competency · M15 Inventory · M17 Assets · M46 Fleet · M29 Identity |
| **Depended on by** | M01, M03, M05, M08, M09, M13, M20, M23, M25, M26, M57, M59 |

---

## 2. Purpose

M02 answers three questions, thousands of times a day: **who does this job, when, and in what
order** — and then makes sure the work that happens in the field is captured accurately,
even when there is no signal.

It runs the dispatch board that 3–8 dispatch managers work from, and the mobile application
that 200–400 field technicians live in for eight hours a day. That application is the single
highest-risk artefact in the entire ERP programme: if technicians reject it, the field model
collapses and every downstream benefit — inventory accuracy, invoicing speed, warranty
recovery, quality data — degrades with it.

### Why It Exists

Today dispatch is a coordinator with a paper list and a phone. Assignment is verbal. There is
no record of who accepted what, no view of where anyone is, no route planning, and no way to
know a job is at risk until the customer calls. The consequences are measurable in the v1.0
baseline: **4–5 jobs per technician per day against an industry norm of 7–9**, **55%
technician utilisation**, and roughly **35% of the working day spent travelling**.

M02 replaces that with skill-aware assignment, optimised routing, live visibility and
offline-capable field execution.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.2 (BR-FSM-001…017) | AI-powered scheduling, dispatch board, GPS tracking, route optimisation, mobile app with offline mode, e-signature, barcode parts |
| ERP BRD §6.2 Process 2 | Current state: coordinator reviews a paper job list, calls or WhatsApps the technician, no acceptance tracking, no GPS |
| ERP BRD §6.3 | Baseline metrics: 4–5 jobs/day, 55% utilisation, 70% first-time fix |
| ERP BRD BO-02 | Business objective: 7–8 jobs per technician per day within 12 months |
| ERP URD Persona 3 & 4 | Senior and junior field technician needs |
| ERP URD §5.2 | "Work offline for up to 24 hours"; "complete job documentation in under 5 minutes" |
| Service App SOW §GPS tracking | "GPS / location tracking of both customer and service provider… updated on an interval basis" |
| Portal roadmap IMPL-24, IMPL-44 | Dispatch optimisation targeting 50% then 70% auto-assignment |
| Company Profile §On-Site / Home Service | On-site service is a named delivery mode for laptops, desktops, printers and all appliance categories |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Candidate scoring and assignment of field work to technicians |
| 2 | The dispatch board: calendar, list and map views with drag-and-drop |
| 3 | Route optimisation and continuous re-optimisation on disruption |
| 4 | Territory, zone and geofence definition and enforcement |
| 5 | Work order lifecycle for field work |
| 6 | The technician mobile application in full |
| 7 | Offline operation for 24 hours and conflict-resolved synchronisation |
| 8 | Live technician location tracking and the customer-facing ETA |
| 9 | Field evidence capture: photographs, video, voice, signature |
| 10 | Van stock consumption at the point of use |
| 11 | On-site payment collection and daily field cash reconciliation |
| 12 | Field exception handling: customer absent, no access, scope change, cannot complete |
| 13 | Multi-technician crews and multi-visit jobs |
| 14 | External and marketplace engineer dispatch |
| 15 | Field safety: lone-worker check-in, panic alert, incident reporting |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Service order state, SLA and customer promise | **M01** | One customer-facing record; M02 executes against it |
| Workshop bench work | **M31** | Different work pattern, different optimisation |
| Shift patterns, rosters, leave, availability windows | **M55** | Workforce planning is an HR discipline with its own cadence |
| Technician certification | **M22** | M02 enforces the gate; M22 owns the record |
| Van stock levels, par settings and replenishment planning | **M15** | M02 consumes; M15 owns the ledger |
| Vehicle documents, servicing, fuel and telematics hardware | **M46** | Vehicles are enterprise assets |
| Physical device movement between sites | **M03** | Custody is a legal chain |
| Price and estimate calculation | **M11** / **M36** | Commercial decisions |
| Invoice creation | **M20** | Only Category G creates financial documents |
| Assignment scoring model training | **M26** | M02 consumes the model; M26 owns its lifecycle |
| Notification delivery to the customer | **M27** | M02 raises events; M27 sends |
| Incentive calculation from field performance | **M57** | M02 emits the measurements; M57 turns them into pay |

### 3.3 Shared Concepts

| Concept | M02's Role | Owning Module |
|---|---|---|
| Work order | Owns | M02 |
| Service order | Parent; reports status | M01 |
| Technician availability | Consumes | M55 |
| Certification | Enforces at assignment | M22 |
| Van stock | Consumes and reconciles | M15 |
| Vehicle | Uses; reports usage | M46 |
| Location ping | Owns the stream; M46 owns the device | M02 / M46 |
| Assignment model | Consumes | M26 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Microsoft Dynamics 365 Field Service** | Work order, resource scheduling optimisation, mobile app, IoT-triggered work | Work order model; schedule-board interaction pattern; optimisation as an advisory layer | Universal Resource Scheduling's configuration depth |
| **IFS Cloud FSM** | Planning and schedule optimisation, mobile worker productivity, contractor management, service logistics | Contractor/external-engineer dispatch as a first-class case; parts-aware assignment | IFS's full MRO scheduling model |
| **Salesforce Field Service** | Skill-based routing, appointment booking, mobile offline priming | Skill-based routing rules; offline data priming by assignment | Platform-specific object model |
| **PTC ServiceMax** | Technician productivity, first-time fix optimisation, parts on van | Van stock as an assignment input — a genuine differentiator | — |
| **ServicePower / ServiceTitan / Jobber** (SME field service) | Simple dispatch board, drag-and-drop, live map, customer "on the way" notification | The customer tracking link and ETA notification pattern | Their single-trade assumptions |
| **VROOM + OSRM** | Vehicle routing problem solver over an OpenStreetMap road network | Self-hosted VRP solving at zero licence cost with Bangladesh road data | Commercial routing APIs at $200–400/month |
| **Traccar** | GPS server supporting 200+ device protocols | Position ingestion and streaming as a separate concern from the ERP | — |
| **Odoo 19 + OCA `fieldservice`** | Order, worker, location, route, timeline | Base object model and calendar/timeline views | Odoo's default scheduling — no optimisation |

**Design position.** Four deliberate differences.

First, **offline is not a feature, it is the operating assumption**. Industry guidance treats
offline as important; in Bangladesh, outside Dhaka metro, it is the normal condition for part
of most working days. The app is architected offline-first with a 24-hour guarantee, not
online-first with an offline fallback.

Second, **the model advises, the dispatcher decides — until the model earns trust**. Auto-
assignment starts at 0% in Wave 2 and reaches 70% by Wave 8, gated on measured dispatcher
agreement rather than on a calendar date. Every override is captured with a reason and feeds
back into training.

Third, **van stock is an assignment input, not an afterthought**. Sending a technician to a
job whose part is not on their van is the largest avoidable cause of a second visit, and
first-time fix rate is the KPI that drives everything else.

Fourth, **Bengali-first with icon-led fallback**. Field-facing screens are designed for
technicians whose reading speed in Bengali varies. Critical actions are recognisable by icon
and colour before they are read.

---

## 5. Functional Areas & Features

### 5.1 Assignment & Scheduling

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-001 | Candidate scoring | Score and rank candidate technicians on skill match, certification validity, zone, current load, travel time, van stock, customer preference, historical rating and cost | P0 | L5 |
| FR-FSM-002 | Auto-assignment | Assign automatically when the top candidate's score exceeds the confidence threshold; otherwise present the ranked list to the dispatcher | P0 | L5 |
| FR-FSM-003 | Dispatch board | Provide combined calendar, list and map views with drag-and-drop reassignment and immediate conflict detection | P0 | L5 |
| FR-FSM-004 | Capacity view | Show available capacity by zone, skill and day, highlighting over- and under-capacity in advance | P1 | L5 |
| FR-FSM-005 | Territory and zone management | Define zones and geofences per branch, assign technicians to zones, and define overflow rules | P1 | L5 |
| FR-FSM-006 | Availability consumption | Consume shifts, leave and holidays from M55 so that an unavailable technician is never offered | P1 | L5 |
| FR-FSM-007 | Certification gate | Refuse assignment of brand warranty work to a technician whose certification for that brand has expired | P0 | L5 |
| FR-FSM-008 | Multi-technician crews | Assign a crew with defined roles — lead, assistant, specialist — tracking each member's time separately | P2 | L5 |
| FR-FSM-009 | Multi-visit jobs | Plan and track jobs requiring several visits while keeping the SLA and the customer view coherent | P1 | L5 |
| FR-FSM-010 | Emergency insertion | Insert an emergency job and re-optimise the affected technician's remaining route automatically | P1 | L5 |
| FR-FSM-011 | External capacity | Offer overflow jobs to marketplace sellers under commercial, certification and quality constraints | P2 | L5 |
| FR-FSM-045 | Dispatcher productivity | Provide bulk assign, filter presets, keyboard shortcuts and undo | P1 | L5 |
| FR-FSM-046 | Assignment explanation | Show the dispatcher why a technician was recommended, in plain language | P1 | L5 |
| FR-FSM-047 | Override logging | Record every override of an automatic recommendation with a reason code, feeding model improvement | P1 | L5 |
| FR-FSM-052 | Slot capacity management | Manage bookable capacity by branch, skill and slot to prevent overbooking at intake | P1 | L5 |
| FR-FSM-053 | Working-time awareness | Prevent scheduling that would breach working-time limits without approved overtime | P1 | L5 |
| FR-FSM-055 | Standby and emergency rota | Manage the after-hours on-call rota and dispatch from it | P1 | L5 |

### 5.2 Route Optimisation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-012 | Nightly route solve | Solve the vehicle routing problem for all technicians nightly, honouring time windows, skills, capacity and priorities | P1 | L4 |
| FR-FSM-013 | Live re-optimisation | Re-solve affected routes when a job is added, cancelled or extended, or a technician becomes unavailable | P1 | L4 |
| FR-FSM-014 | Travel-time estimation | Estimate travel using road-network data, augmented with real-time traffic for the Dhaka metro area | P1 | L4 |
| FR-FSM-015 | Route publishing | Push the optimised route to the technician app with turn-by-turn navigation handoff | P1 | L5 |
| FR-FSM-016 | Route adherence | Measure planned versus actual route and flag material deviation | P2 | L5 |
| FR-FSM-067 | SLA-aware sequencing | Sequence a route so that SLA-critical jobs are protected even at the cost of additional travel | P1 | L5 |
| FR-FSM-068 | Zone rebalancing | Recommend zone or roster changes where demand and capacity are persistently mismatched | P2 | L5 |

### 5.3 Field Execution — Technician Mobile Application

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-017 | Job queue | Show today's jobs in optimised order with customer, device, history, complaint and entitlement context | P0 | L5 |
| FR-FSM-018 | Accept or decline | Accept or decline a job with a reason; a decline triggers reassignment | P0 | L5 |
| FR-FSM-019 | Navigation | Launch turn-by-turn navigation to the job location | P0 | L5 |
| FR-FSM-020 | Automatic timestamps | Capture departed, arrived, started, paused, completed and left, with GPS and geofence validation | P0 | L5 |
| FR-FSM-021 | On-site diagnosis | Run the M01 diagnostic tree on the device with full offline support | P0 | L5 |
| FR-FSM-022 | Parts scanning | Scan van stock by barcode or QR to consume parts; request parts not held on the van | P0 | L5 |
| FR-FSM-023 | Media capture | Capture before and after photographs, short video and voice notes with automatic metadata | P0 | L5 |
| FR-FSM-024 | Electronic signature | Capture the customer's signature on screen with the declaration text in Bengali or English | P0 | L5 |
| FR-FSM-025 | On-site payment | Collect cash, mobile money or card at the customer site, issue a receipt, and reconcile to the branch cash book | P1 | L5 |
| FR-FSM-026 | Offline operation | Operate fully offline for 24 hours; queue all actions; synchronise automatically within 30 seconds of reconnection with complete integrity | P0 | L5 |
| FR-FSM-027 | Conflict resolution | Resolve concurrent edits deterministically with a server-authoritative policy and a technician-visible reconciliation log | P0 | L5 |
| FR-FSM-028 | Offline knowledge | Provide repair manuals, wiring diagrams and previous repair notes offline | P2 | L5 |
| FR-FSM-029 | In-app messaging | Message dispatch, the workshop and — where permitted — the customer, with offline queueing | P2 | L5 |
| FR-FSM-030 | Personal scorecard | Show the technician their own jobs, ratings, first-time-fix rate and earned incentive | P2 | L5 |
| FR-FSM-031 | Safety and duty of care | Record site safety checks, lone-worker check-in and a panic alert | P2 | L5 |
| FR-FSM-057 | Field expense capture | Capture travel and incidental expenses in the field for reimbursement | P2 | L5 |
| FR-FSM-060 | Photo quality validation | Reject blurred, dark or duplicate evidence photographs at the point of capture | P2 | L5 |
| FR-FSM-061 | Data-usage optimisation | Compress and defer non-critical uploads to reduce the technician's mobile data cost | P1 | L5 |
| FR-FSM-062 | Battery optimisation | Manage location and sync frequency to preserve device battery across a full shift | P1 | L5 |
| FR-FSM-063 | App update management | Deliver forced and optional updates with version-compatibility enforcement | P1 | L5 |
| FR-FSM-064 | Device enrolment | Register technician devices and revoke access on loss or departure | P1 | L5 |

### 5.4 Tracking & Customer Visibility

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-032 | Live technician tracking | Stream technician positions at a configurable interval to a live operations map | P0 | L4 |
| FR-FSM-033 | Customer tracking page | Provide the customer a live map with the technician's position, photograph, name and ETA on the day of service | P0 | L5 |
| FR-FSM-034 | ETA calculation | Recalculate and publish ETA as conditions change, emitting an event on material change | P1 | L5 |
| FR-FSM-035 | Geofence events | Raise automatic events on entering and leaving customer, branch and warehouse geofences | P1 | L5 |
| FR-FSM-036 | Privacy controls | Suspend location capture outside working hours and during breaks; log every access to location history | P0 | L5 |
| FR-FSM-066 | Route replay | Replay a technician's actual route and events for investigation | P2 | L5 |

### 5.5 Field Exceptions

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-037 | Customer absent | Record a failed visit with geotagged evidence, notify the customer, and trigger rescheduling or a charge per policy | P1 | L5 |
| FR-FSM-038 | Cannot complete | Record the reason — parts, access, complexity, safety — and convert to a follow-up visit or a workshop transfer | P1 | L5 |
| FR-FSM-039 | On-site scope change | Raise a revised estimate on site and obtain approval before proceeding | P1 | L5 |
| FR-FSM-040 | Convert to collection | Convert a failed on-site repair into a pick-and-drop consignment handled by M03 | P1 | L5 |
| FR-FSM-059 | Field incident reporting | Report accidents, hazards, abuse or security incidents from the field to M59 | P2 | L5 |
| FR-FSM-071 | Customer rescheduling | Allow the customer to reschedule from the tracking link within policy | P1 | L5 |
| FR-FSM-072 | No-access evidence | Capture geotagged evidence when access is refused or the customer is absent | P1 | L5 |

### 5.6 Van Stock & Field Logistics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FSM-041 | Van par levels | Consume per-technician par levels defined in M15, based on skill profile and job mix | P1 | L5 |
| FR-FSM-042 | Van stock in assignment | Consider van stock when scoring candidate technicians for a job | P1 | L5 |
| FR-FSM-043 | Field parts transfer | Transfer a part directly between two technicians in the field with scanning by both | P2 | L5 |
| FR-FSM-056 | Field cash reconciliation | Reconcile cash collected in the field daily against jobs and deposits | P1 | L5 |
| FR-FSM-058 | Vehicle assignment | Record which vehicle a technician is using and report usage to M46 | P2 | L5 |

*(FR-FSM-044, 048–051, 054, 065, 069, 070, 073, 074 cover performance instrumentation, site
visit planning, sub-contractor dispatch, appointment reminders, technician constraints,
dispatch simulation, availability self-service, job handover, dispatch analytics and the
dispatch API; full text in `05-01_Feature_and_Function_Register.md`.)*

> **Retired requirement identifiers.** 11 identifiers inside the original `FR-FSM-001 … 074` allocation were never issued to a requirement and are **retired, not reissued**, under register rule RG-02 (permanent identity):
>
> FR-FSM-044, 048, 049, 050, 051, 054, 065, 069, 070, 073, 074
>
> The measured requirement count for this module is **63**. Earlier statements of **74** were taken from the highest allocated identifier rather than a count of requirements (audit finding A3-01).

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Offline-first architecture** | Local encrypted store with an append-only command journal; the app never blocks on a network call |
| T-02 | **Idempotent command replay** | Every field action carries a client-generated UUID; replay after reconnection is exactly-once |
| T-03 | **Deterministic conflict resolution** | Server authoritative for assignment, pricing, stock and state; client authoritative for evidence, notes and field timestamps; every resolution is visible to the technician |
| T-04 | **Selective sync scoping** | The device downloads only the technician's assigned work plus required reference data; scope is re-evaluated on every sync |
| T-05 | **Bandwidth discipline** | Photographs compressed client-side; non-critical uploads deferred to Wi-Fi; delta sync only |
| T-06 | **Battery discipline** | Adaptive GPS interval — dense while travelling, sparse while stationary; background work batched; target ≤ 12% per 8-hour shift excluding navigation |
| T-07 | **Position stream separation** | GPS positions land in a time-series store, never in the transactional database |
| T-08 | **Optimisation as a service** | The VRP solver runs as a separate service with a timeout and a graceful fallback to the previous manual sequence |
| T-09 | **Model consumption with fallback** | Assignment scoring calls M26 with a strict timeout; on failure it falls back to deterministic rule-based scoring |
| T-10 | **Real-time board updates** | The dispatch board updates by push, not polling, and degrades to polling on WebSocket failure |
| T-11 | **Device enrolment and revocation** | Devices are registered per technician; access is revoked centrally on loss or exit within one hour |
| T-12 | **Low-end device support** | Runs acceptably on a mid-range Android 11 device with 3 GB RAM; cold start ≤ 4 s |
| T-13 | **Bengali rendering** | Complex Bengali conjunct rendering verified across the supported device matrix, including on-screen signature declaration text |
| T-14 | **Performance** | Job list load ≤ 8 s cold on 3G, ≤ 2 s warm; sync after 24 hours offline ≤ 30 s on 3G |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M02 |
|---|---|---|
| **Dispatch manager** | Paper list, phone calls, no visibility, constant re-assignment | Ranked recommendations, live map, SLA-risk queue; a full morning assigned in under ten minutes |
| **Field technician** | Verbal instructions, paper form, no history, writes up at day's end | Full context on the phone, guided diagnosis, scan-to-consume parts, signature on screen, done before leaving the site |
| **Customer** | No idea when anyone will arrive | A link showing the technician on a map with an ETA, and a message when they set off |
| **Branch manager** | Cannot see field activity at all | Live view of every technician and job in their branch |
| **Inventory manager** | Van stock is a black hole | Consumption recorded at the point of use; daily reconciliation |
| **Finance officer** | Field cash reconciled by trust | Reconciled per technician per day against jobs and deposits |
| **HR / payroll** | Technician performance is impressionistic | Objective jobs, hours, first-time fix and CSAT feeding incentive calculation |
| **Operations director** | Cannot answer "how productive are we?" | Jobs per technician per day, utilisation, travel share, all live |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Technician productivity** | Optimised routing, van-stock-aware assignment, elimination of documentation lag and travel to depot | **4–5 → 8–9 jobs/day**; the largest single operational benefit in the programme: **BDT 130 lac/year** |
| **Travel cost reduction** | Route optimisation and zone discipline | Travel share of the working day **35% → 22%**; fuel and vehicle cost fall proportionally |
| **First-time fix improvement** | Skill matching, parts availability at assignment, history in hand | **70% → 88%**; each avoided second visit saves a full job slot |
| **Faster cash conversion** | On-site payment collection and immediate invoice trigger | Contributes to **DSO < 32 days** |
| **Inventory accuracy** | Point-of-use consumption and daily van reconciliation | Van variance from untracked to **< 1%** |
| **Warranty evidence** | Photographs, GPS, timestamps and signature captured automatically | Protects the **BDT 100 lac/year** warranty recovery |
| **Reduced hotline load** | Live tracking and ETA notification | Contributes to the **60% deflection** of status enquiries |
| **Fair, defensible incentives** | Objective performance data | Enables performance-linked pay without dispute — a precondition for the productivity gain |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Technician safety** | Lone-worker check-in and panic alert give the Company a duty-of-care mechanism it does not currently have |
| **Dispute defensibility** | Geotagged arrival, photographs and signature settle "the technician never came" disputes with evidence |
| **Fairness in work allocation** | Assignment by rule and score, visible to all, removes favouritism from job distribution |
| **Career progression evidence** | Measured competence supports promotion from junior to senior to specialist |
| **Training data foundation** | Every field action trains the models that raise auto-assignment from 0% to 70% |
| **Brand credibility** | A customer watching a technician approach on a map is the most visible proof that 1000FiX is a modern operation |

---

## 8. Lifecycle & State Model — Work Order

```
         ┌───────────┐
         │  CREATED  │  (raised from M01)
         └─────┬─────┘
               │ candidate scoring
         ┌─────▼───────┐
    ┌───►│  PROPOSED   │  (auto-assigned or dispatcher-selected)
    │    └─────┬───────┘
    │          │ technician notified
    │    ┌─────▼───────┐
    │    │  ASSIGNED   │──── decline ────┐
    │    └─────┬───────┘                 │
    │          │ accept                   │
    │    ┌─────▼───────┐                 │
    │    │  ACCEPTED   │                 │
    │    └─────┬───────┘                 │
    │          │ depart (auto-timestamp) │
    │    ┌─────▼───────┐                 │
    │    │  EN ROUTE   │  ETA published, customer notified
    │    └─────┬───────┘                 │
    │          │ geofence arrival        │
    │    ┌─────▼───────┐                 │
    │    │   ON SITE   │                 │
    │    └─────┬───────┘                 │
    │          │ start work               │
    │    ┌─────▼───────┐                 │
    │    │ IN PROGRESS │◄──── resume ────┤
    │    └─────┬───────┘                 │
    │          │                          │
    │    ┌─────▼───────┐  scope change / parts / access
    │    │   PAUSED    │─────────────────┤
    │    └─────────────┘                 │
    │          │ work complete            │
    │    ┌─────▼──────────┐              │
    │    │ CUSTOMER SIGN  │              │
    │    └─────┬──────────┘              │
    │          │ signature captured       │
    │    ┌─────▼───────┐                 │
    │    │  COMPLETED  │                 │
    │    └─────┬───────┘                 │
    │          │ synced to server         │
    │    ┌─────▼───────┐                 │
    │    │   CLOSED    │                 │
    │    └─────────────┘                 │
    │                                     │
    └─────────────────────────────────────┘  reassignment

  Exceptions: CUSTOMER ABSENT · NO ACCESS · CANNOT COMPLETE · CONVERTED TO COLLECTION
              · CANCELLED
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Created | Proposed | Candidate scored above threshold, or dispatcher selection | System / dispatcher |
| Proposed | Assigned | Certification valid (BRU-FSM-02); technician available (M55); no schedule conflict | System |
| Assigned | Accepted | Technician confirmation received | Technician |
| Assigned | Created | Decline with reason — returns to the pool | Technician |
| Accepted | En Route | Departure recorded, GPS active | Technician |
| En Route | On Site | Geofence entry, or manual arrival with exception reason (BRU-FSM-06) | System / technician |
| On Site | In Progress | Work start recorded | Technician |
| In Progress | Paused | Approved pause reason | Technician |
| In Progress | Customer Sign | Diagnostic, parts, evidence and checklist complete | Technician |
| Customer Sign | Completed | Signature captured, or documented refusal with alternative evidence | Technician + customer |
| Completed | Closed | Synchronised to server; parts, time and evidence reconciled | System |
| Any | Customer Absent | Geotagged evidence captured (BRU-FSM-09) | Technician |
| Any | Cannot Complete | Reason recorded; follow-up or transfer created | Technician |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FSM-01 | A technician on leave, off shift or at capacity is never offered as a candidate | **H** | Dispatch Manager |
| BRU-FSM-02 | Assignment requires a skill match to the job's required competency | **H** | Quality Manager |
| BRU-FSM-03 | Automatic assignment occurs only when the top candidate's score exceeds the configured confidence threshold | **C** | Ops Director |
| BRU-FSM-04 | Every dispatcher override of an automatic recommendation requires a reason code | **H** | Ops Director |
| BRU-FSM-05 | GPS capture occurs only during working hours and while on duty | **H** | HR Director |
| BRU-FSM-06 | A job cannot be marked On Site outside the customer geofence without a recorded exception reason | **A** | Dispatch Manager |
| BRU-FSM-07 | On-site cash must be reconciled to the branch cash book by the end of the technician's shift | **H** | Finance Manager |
| BRU-FSM-08 | Van stock cannot exceed the configured maximum per item per technician | **H** | Inventory Manager |
| BRU-FSM-09 | A failed visit requires geotagged evidence before it can be recorded | **H** | Ops Director |
| BRU-FSM-10 | Scheduling that would breach working-time limits requires approved overtime first | **H** | HR Director |
| BRU-FSM-11 | Emergency insertion may displace lower-priority jobs but never an SLA-critical job already at risk | **C** | Dispatch Manager |
| BRU-FSM-12 | A marketplace seller may be offered a job only if score, certification and category access all qualify | **H** | Marketplace Operations |
| BRU-FSM-13 | A brand warranty job cannot be assigned to a technician whose certification for that brand has expired | **H** | Quality Manager |
| BRU-FSM-14 | Location history access is logged and available only to named roles | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.work.order` | `fix_work_order` | The unit of field work | name, service_order_id, technician_id, crew_id, state, scheduled_start, actual_start, actual_end, zone_id, visit_sequence |
| `fix.dispatch.job` | `fix_dispatch_job` | Dispatch queue entry | work_order_id, priority, sla_risk, required_skills, required_parts, status |
| `fix.assignment.score` | `fix_assignment_score` | Candidate ranking record | dispatch_job_id, technician_id, score, factors_json, selected, override_reason |
| `fix.technician.profile` | `fix_technician_profile` | Field-service view of an employee | employee_id, zones, skills, vehicle_id, van_location_id, max_daily_jobs, current_load |
| `fix.zone` | `fix_zone` | Dispatch territory | code, branch_id, boundary_geojson, primary_technicians |
| `fix.geofence` | `fix_geofence` | Location boundary | reference_type, reference_id, centre, radius_m, boundary_geojson |
| `fix.route.plan` | `fix_route_plan` | A technician's day | technician_id, date, optimised_at, total_travel_min, total_distance_km, adherence_pct |
| `fix.route.stop` | `fix_route_stop` | An ordered stop | route_plan_id, sequence, work_order_id, planned_arrival, actual_arrival, travel_min |
| `fix.visit` | `fix_visit` | One attendance at a location | work_order_id, arrived_at, departed_at, gps_arrival, gps_departure, outcome |
| `fix.visit.exception` | `fix_visit_exception` | Failed or partial visit | visit_id, exception_type, reason, evidence_ids, follow_up_action |
| `fix.location.ping` | `fix_location_ping` *(TimescaleDB)* | Position stream | technician_id, time, lat, lng, accuracy, speed, source |
| `fix.field.session` | `fix_field_session` | A technician's working day | technician_id, date, started_at, ended_at, jobs_completed, cash_collected |
| `fix.offline.journal` | `fix_offline_journal` | Replay log of offline commands | device_id, command_uuid, command_type, payload, created_at, applied_at, conflict_resolution |
| `fix.van.stock` | `fix_van_stock` *(shared with M15)* | Parts on a technician's van | technician_id, location_id, product_id, quantity, par_level |
| `fix.crew` | `fix_crew` | Multi-technician assignment | work_order_id, lead_id, member_ids, role_map |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order` | M01 | Parent; status write-back |
| `fix.asset` | M17 / M49 | Read identity and history |
| `fix.employee`, `fix.roster`, `hr.leave` | M55 / M21 | Read availability |
| `fix.competency.assessment`, `fix.competency.assessment` | M22 | Read for the assignment gate |
| `fix.part.item`, `fix.stock.reservation` | M15 / M37 | Consume and request |
| `fix.vehicle` | M46 | Read; report usage |
| `fix.model` (assignment, duration, travel) | M26 | Consume predictions |
| `fix.consignment` | M03 | Create on conversion to collection |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FSM-01 | Service order ready for dispatch | Score candidates; auto-assign above threshold or queue for the dispatcher | Present the ranked list |
| AUT-FSM-02 | Nightly 05:00 | Optimise all routes for the next day; publish; notify technicians | Retain the previous manual sequence |
| AUT-FSM-03 | Emergency job created | Identify the nearest qualified available technician; re-optimise their route; notify both parties | Escalate to the dispatcher |
| AUT-FSM-04 | Technician departs | Publish ETA; emit the en-route event for customer notification | Manual notification task |
| AUT-FSM-05 | Geofence arrival detected | Record arrival, emit the arrival event, start the on-site clock | Manual arrival with exception reason |
| AUT-FSM-06 | Job completed offline then synced | Reconcile parts, time and evidence; release the downstream invoice trigger | Flag conflicts for supervisor review |
| AUT-FSM-07 | Technician idle beyond threshold during shift | Alert the dispatcher | — |
| AUT-FSM-08 | Van stock falls below par after a job | Generate a replenishment request to the branch store | Alert inventory manager |
| AUT-FSM-09 | ETA changes materially | Emit the revised-ETA event for customer notification | — |
| AUT-FSM-10 | Shift end | Prompt field cash reconciliation; block the next shift start until complete | Escalate to branch manager |
| AUT-FSM-11 | Panic alert raised | Notify the dispatcher, branch manager and safety officer immediately with location | Escalate through all channels simultaneously |
| AUT-FSM-12 | Certification expires | Remove the technician from that brand's warranty dispatch pool | — |
| AUT-FSM-13 | Device not synced for 26 hours | Alert the dispatcher — possible device loss or technician issue | — |

---

## 12. Interfaces

### 12.1 Upstream — M02 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order | Job context, scope, promise date, SLA risk | Command + event |
| M55 Workforce Scheduling | Shifts, rosters, leave, availability windows | Event projection |
| M22 Competency | Certification validity by brand and repair level | REST |
| M15 Inventory | Van stock levels, part availability by location | REST + event |
| M17 Asset Registry | Device identity, specification, service history | REST |
| M46 Fleet | Vehicle assignment and telematics device identity | REST |
| M26 AI/ML | Assignment score, duration prediction, travel prediction | REST with timeout and fallback |
| M11 Pricing | On-site revised estimate pricing | REST via M36 |
| M61 Knowledge | Repair procedures for offline caching | REST |
| M12 Marketplace | External seller availability and eligibility | REST |

### 12.2 Downstream — M02 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Work order status, field outcome, evidence | Events |
| M15 Inventory | Parts consumed and returned | Command |
| M03 Logistics | Consignment request on conversion to collection | Command |
| M17 Asset Registry | Device condition and service event | Event |
| M20 Receivable | On-site payment records | Event |
| M23 Quality | Field QC results, failed visits, incidents | Events |
| M27 Contact Centre | En route, arrived, completed, delayed events | Events |
| M57 Performance | Jobs completed, first-time fix, hours, CSAT linkage | Warehouse extract |
| M59 Health & Safety | Field incidents, panic alerts, safety checks | Events |
| M25 Business Intelligence | Full work order and route fact stream | Warehouse extract |
| M26 AI/ML | Assignment outcomes, actual durations, actual travel, overrides | Warehouse extract |
| P01 Customer Portal | Technician position, ETA, photograph and name | REST + WebSocket |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `work_order.assigned` | work order, technician, scheduled window | M01, M27, M55 |
| `work_order.accepted` | work order, technician, accepted at | M01 |
| `work_order.declined` | work order, technician, reason | M01, M57 |
| `technician.dispatched` | work order, technician name and photo, ETA, tracking token | M27, P01 |
| `technician.arrived` | work order, arrival time, GPS | M01, M27 |
| `technician.location_updated` | technician, coordinates, ETA (throttled) | P01 |
| `work_order.started` | work order, start time | M01, M25 |
| `work_order.paused` | work order, reason | M01 |
| `work_order.completed` | work order, outcome, parts, time, evidence, signature | M01, M15, M20, M23 |
| `visit.failed` | work order, exception type, evidence | M01, M27, M23 |
| `field_payment.collected` | work order, amount, method, receipt | M20, M50 |
| `panic_alert.raised` | technician, location, time | M59, dispatch, management |
| `van_stock.consumed` | technician, part, quantity, work order | M15 |
| `assignment.overridden` | dispatch job, recommended, selected, reason | M26 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/technician/jobs` | GET | Today's job queue with full context | P02 |
| `/api/v1/technician/jobs/{id}/accept` | POST | Accept or decline | P02 |
| `/api/v1/technician/jobs/{id}/status` | POST | State transition with timestamp and GPS | P02 |
| `/api/v1/technician/jobs/{id}/evidence` | POST | Upload media | P02 |
| `/api/v1/technician/jobs/{id}/parts` | POST | Record parts consumption | P02 |
| `/api/v1/technician/jobs/{id}/signature` | POST | Capture customer signature | P02 |
| `/api/v1/technician/sync` | POST | Batch replay of offline commands | P02 |
| `/api/v1/technician/sync` | GET | Delta download since sync token | P02 |
| `/api/v1/technician/location` | POST | Position report | P02 |
| `/api/v1/ops/dispatch/board` | GET | Dispatch board data | P03 |
| `/api/v1/ops/dispatch/{job}/candidates` | GET | Ranked candidates with explanation | P03 |
| `/api/v1/ops/dispatch/{job}/assign` | POST | Assign, with override reason where applicable | P03 |
| `/api/v1/ops/routes/optimise` | POST | Trigger re-optimisation | P03 |
| `/api/v1/technicians/{id}/location` | GET | Live position for the customer tracking page | P01 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R05 Operations Director | C R U D A | All zones |
| R07 Dispatch Manager | C R U D A | Assigned zones |
| R06 Branch Manager | C R U A | Own branch |
| R10 Senior Technician | R U | Own assigned work orders |
| R11 Junior Technician | R U | Own assigned work orders |
| R12 Specialist Technician | R U | Own assigned work orders |
| R08 Service Centre Agent | R | Own branch — visibility only |
| R15 Logistics Coordinator | R | Movement-relevant work orders |
| R17 Inventory Manager | R | Van stock consumption |
| R32 Quality Manager / ISO Coordinator | R | All — field QC and incidents |
| R34 Contact Centre Agent | R | Status for customer enquiry |
| R36 Customer | R | Own job's technician position and ETA only |
| R38 Marketplace Seller | R U | Own awarded work orders only |

**Field-level restrictions:** cost and margin are hidden from technicians. Location history is
accessible only to R05, R06, R07 and R32, and every access is logged (BRU-FSM-14).

**Privacy control:** location capture is suspended outside working hours and during recorded
breaks (BRU-FSM-05). Technicians can see that tracking is active.

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Live dispatch map | Dispatch, branch, operations | Real time | Technician positions, job states, SLA countdowns |
| Daily dispatch summary | Dispatch Manager | Daily | Assigned, completed, failed, reassigned, auto-assign rate |
| Technician productivity | Ops Director, HR | Weekly | Jobs/day, utilisation, travel share, first-time fix, CSAT |
| Route efficiency | Ops Director | Weekly | Planned versus actual travel, adherence, optimisation benefit |
| Failed visit analysis | Ops Director, Quality | Weekly | Failure reasons by cause, zone and technician |
| Assignment quality | Ops Director, CTO | Monthly | Auto-assign rate, override rate and reasons, model agreement |
| Capacity versus demand | Ops Director | Weekly | Zone-level capacity gaps, forward seven days |
| Field cash reconciliation | Finance Manager | Daily | Collected, deposited, variance by technician |
| App adoption and health | CTO, Ops Director | Weekly | Daily active users, crash-free rate, sync failures, offline duration |
| Safety report | Safety Officer, HR | Monthly | Incidents, panic alerts, lone-worker compliance |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-011 | Jobs per technician per day | 4–5 | 7 | **8–9** |
| KPI-012 | Technician utilisation | 55% | 74% | **82%** |
| KPI-013 | Automatic assignment rate | 0% | 20% | **70%** |
| KPI-014 | Travel time as % of working day | ~35% | 26% | **22%** |
| KPI-015 | On-time arrival within window | unmeasured | 88% | **92%** |
| KPI-016 | Technician app daily active usage | 0% | 92% | **95%** |
| KPI-017 | Offline sync failures | n/a | **0** | **0** |
| KPI-004 | First-time fix rate | 70% | 82% | **88%** |
| — | Dispatcher agreement with recommendation | n/a | 80% | **90%** |
| — | Job documentation time | 15–20 min + write-up | < 7 min | **< 5 min** |
| — | Crash-free sessions | n/a | 99% | **99.5%** |
| — | Field cash variance | untracked | < 1% | **< 0.3%** |
| — | Technician satisfaction with the app | n/a | > 3.8/5 | **> 4.2/5** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L2 | OCA `fieldservice`, `fieldservice_route`, `fieldservice_skill`, `fieldservice_timeline`, `fieldservice_geoengine`, `fieldservice_vehicle`, `fieldservice_google_map` | 22% |
| L4 | Traccar (GPS), VROOM + OSRM (routing), Firebase (push) | 16% |
| L5 | `cd_dispatch`, `cd_technician`, `cd_route`, `cd_geofence`, `cd_van_stock`, `cd_field_session`, `cd_offline_sync`, Flutter application | 62% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-012 | `cd_dispatch` — scoring, board, assignment, override capture | Odoo module | 8 PW |
| CD-013 | `cd_route` — VROOM/OSRM orchestration, publishing, adherence | Service + module | 5 PW |
| CD-014 | `cd_offline_sync` — journal, replay, conflict resolution | Odoo module + protocol | 6 PW |
| CD-015 | **Technician mobile application (Flutter)** | Mobile app | 18 PW |
| CD-016 | `cd_geofence` + Traccar integration | Odoo module + service | 3 PW |

**CD-015 is the single largest and highest-risk deliverable in Wave 2.** It should be
piloted with 15–20 respected senior technicians for four weeks before any general rollout.

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M02 is scheduled in **W2** (P0) but declares a dependency on 3 module(s) that land later: **M22** (W5); **M46** (W5); **M55** (W5). One of three things must be true before the W2 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W2 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M02 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W2 plan for M02 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M01 Service Order | There is no field work without a service order |
| M17 Asset Registry | The technician needs device identity and history |
| M15 Inventory | Van stock must exist before it can be consumed |
| M22 Competency | The certification gate requires certification data — may be stubbed in W2, enforced from W5 |
| M55 Workforce | Availability data — may be stubbed in W2 with simple working hours, enforced from W5 |
| M29 Identity | Technician authentication and device enrolment |
| M46 Fleet | Vehicle identity — optional in W2 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Technician master (names, zones, skills) | 200–400 | `fix.technician.profile` | W2 |
| Current open field jobs | ~1,000 at cutover | `fix.work.order` | W2 |
| Zone definitions | To be created, not migrated | `fix.zone` | W2 |

No historical field data exists to migrate. Zones and skill profiles must be **authored**
before Wave 2, not extracted — this is a business prerequisite, not a technical one.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every Dhaka technician uses the app daily for all assigned work | Usage report ≥ 95% daily active |
| AC-02 | The app operates fully for 24 hours offline with zero data loss | Controlled 24-hour disconnection test with 20 devices |
| AC-03 | Synchronisation after 24 hours offline completes within 30 seconds on 3G | Field test |
| AC-04 | Route optimisation reduces measured travel time by at least 15% versus the pre-implementation baseline | Before/after measurement over four weeks |
| AC-05 | GPS tracking and the customer tracking page function live | Demonstration with a real customer journey |
| AC-06 | A technician without valid certification cannot be assigned brand warranty work, including via API | Negative test |
| AC-07 | Every dispatcher override is captured with a reason | Sample audit of 100 assignments |
| AC-08 | Job documentation is completed in under five minutes by technicians, not by the project team | Timed observation, 30 samples |
| AC-09 | The app is complete in Bengali including all error messages | Translation coverage report at 100% |
| AC-10 | The app runs acceptably on the lowest supported device (Android 11, 3 GB RAM) | Device matrix test |
| AC-11 | Battery consumption is at or below 12% per 8-hour shift excluding navigation | Field measurement over five shifts |
| AC-12 | Field cash reconciles daily with variance below 1% | Four weeks of reconciliation records |
| AC-13 | Crash-free session rate is at or above 99.5% | Crash reporting over four weeks |
| AC-14 | Technician satisfaction with the app is at or above 3.8/5 at pilot exit | Anonymous survey of pilot technicians |
| AC-15 | Paper service forms are withdrawn in Dhaka | Physical confirmation |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Are technician devices Company-issued or is a data/device allowance paid? This changes the support model and the security posture. | Ops Director / CFO | W2 minus 2 months (decision D-11) |
| Q-02 | What is the policy on charging a customer for a failed visit due to absence? | CCO | W2 build |
| Q-03 | How many dispatch zones should exist, and who authors the boundaries? | Ops Director | W2 design |
| Q-04 | Is on-site card payment in scope for Wave 2, or mobile money and cash only? | CFO | W2 build |
| Q-05 | What confidence threshold should govern auto-assignment at launch, and who may change it? | Ops Director / CTO | W2 build |
| Q-06 | Does the Company accept location tracking of technicians from a labour-relations standpoint, and has this been communicated? | HR Director | W2 minus 1 month |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` · `M01_Service_Request_and_Order_Management.md` ·
`M03_Service_Logistics_and_Reverse_Logistics.md` ·
`03_Modules/K_Platform_and_Technology/P02_Technician_Mobile_Application.md` ·
`05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §6 (offline protocol)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.2, §6.2 Process 2,
§6.3, BO-02 · `1000FiX_ERP_System_Comprehensive_URD.md` Personas 3–4, §5.2 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §GPS tracking ·
`Intergrated_web_portal/.../IMPL-24_Dispatch_Optimization_Guide.md`,
`IMPL-44_Enhanced_Dispatch_Optimization.md`

**External benchmark**
Microsoft Dynamics 365 Field Service — work order and resource scheduling optimisation ·
IFS Cloud FSM — planning, schedule optimisation, contractor management, service logistics ·
Salesforce Field Service — skill-based routing and mobile offline priming ·
PTC ServiceMax — technician productivity and first-time fix ·
Field service optimisation practice — route optimisation increasing job density 15–22%,
mobile workforce solutions increasing technician productivity by ~25%, offline capability as
a reliability requirement · VROOM/OSRM · Traccar · Odoo 19 OCA `fieldservice`

---

*Module M02 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
