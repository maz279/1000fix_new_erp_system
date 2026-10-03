---
id: FIX-ERP2-P02
portal_id: P02
portal_code: TMA
portal_name: Technician Mobile Application
type: Native Mobile Application (offline-first)
category: Portal & Application Suite (filed under K — Platform & Technology)
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Service Operations Director
system_owner: Field Platform Squad
priority: P0
wave: W2
---

# P02 — Technician Mobile Application
### Portal Suite · Code `TMA` · Existing (expanded in v2.1)

---

## 1. Portal Identity

| Attribute | Value |
|---|---|
| **Portal ID** | P02 |
| **Portal code** | `TMA` |
| **Type** | Native mobile application — **offline-first** |
| **Status** | Existing (expanded in v2.1 — workshop mode, logistics custody, van reconciliation, equipment fitness and personal scorecard added) |
| **Priority** | **P0** |
| **Delivery wave** | **W2** (Months 5–8) |
| **Users** | Field technicians, workshop technicians, specialist L3 technicians |
| **Volume** | **200–400 technicians**; target > 95% daily active |
| **Business owner** | Service Operations Director |
| **System owner** | Field Platform Squad |
| **Technology** | Flutter (Android primary, iOS secondary) · SQLite local store · append-only sync journal |
| **Custom development** | `CD-202` |
| **Requirement range** | FR-POR-041 … FR-POR-078 |
| **Requirement count** | **38** *(measured — supersedes the 22 allocation in `05-01` §4)* |
| **Effort estimate** | **40 person-weeks** |
| **Backing modules** | M01, M02, M03, M05, M06, M13, M14, M15, M17, M21, M22, M23, M24, M25, M31, M45, M46, M55, M57, M61 |
| **Platform dependencies** | M29 Identity · M28 Integration Gateway · M30 Platform Admin · M65 Localisation |

---

## 2. Purpose

P02 is **the working surface of the business**. Every service the Company sells is ultimately
performed by a technician holding a phone, and P02 is the instrument through which that work is
instructed, recorded, evidenced and paid for.

It has one requirement that governs every other: **it must work when the network does not.**
A technician in a stairwell in Mirpur, in a basement server room, or in a district town on a
2G fallback is not an exception case — it is a normal Tuesday. An application that requires
connectivity to record a completed repair will be worked around within a week, and the
work-around is paper.

P02 holds no authoritative state. Every job belongs to M01, every part movement to M15, every
photograph to M24. What P02 owns is **the technician's day** — the queue, the sequence, the
capture, and the guarantee that nothing recorded in the field is ever lost.

### Why It Exists

Four things depend on this application and on nothing else.

**Structured capture at the point of work.** Diagnosis, fault code, parts consumed, time spent,
photographs before and after, test results and the customer's signature all originate here.
Every KPI the programme commits to — first-time fix at 88%, TAT under 24 hours, warranty claims
with complete evidence at 98% — is computed from data this application captures. If capture is
poor, no downstream analysis repairs it.

**Van stock accountability.** M15 models 200–400 vans as real stock locations with par levels
and a shift-end reconciliation, and identifies untracked van stock as *the single largest
shrinkage channel in the business*. That reconciliation happens in P02, offline, at the end of
a shift, or it does not happen.

**Evidence that protects revenue.** A warranty claim to a brand partner is paid on photographs,
diagnostic reports and part serials. A damage dispute with a customer is settled by the
condition evidence captured at handover. Both originate in P02, and both are worthless if the
capture is optional or the sync is lossy.

**Technician earnings.** M57 calculates performance-linked incentives from jobs completed,
CSAT and first-time fix. A technician who cannot see their own scorecard and earnings does not
trust the number, and an incentive scheme that is not trusted does not change behaviour.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §4.1 Portal 2 | "Technician Mobile Portal (PWA) — 200-400 technicians — job queue, GPS navigation, digital forms, parts recording, e-signature" |
| ERP BRD BR-FSM-007 | "Provide a mobile app (PWA or native) with offline capability for field technicians" |
| ERP BRD BR-FSM-008 | "Display the technician's daily job queue with priority, schedule, and navigation" |
| ERP BRD BR-FSM-009 | "Provide GPS navigation to each job site via Google Maps integration" |
| ERP BRD BR-FSM-010 | "Auto-capture time stamps for: departed, arrived, repair started, repair completed" |
| ERP BRD BR-FSM-011 | "Enable barcode/QR code scanning for parts consumption recording" |
| ERP BRD BR-FSM-012 | "Capture customer electronic signature on service completion" |
| ERP BRD **BR-FSM-013** | **"Function in offline mode and sync all data when connectivity is restored"** — the governing requirement |
| ERP BRD BR-FSM-017 | "Support offline photo capture (before/after) with auto-sync" |
| ERP BRD BR-SRM-010 | "Before/after photo attachments with timestamp and GPS tag" |
| ERP BRD BR-SRM-014 | "Track labor time per service order (technician time entry from mobile)" |
| ERP BRD BR-SRM-020 | "Technicians require access to complete device and customer history from the service order on mobile" |
| ERP BRD BR-FSM-016 | "Technicians require device repair history, diagnostic guides and troubleshooting references on mobile" |
| ERP BRD BR-QMS-005 | "Enforce quality inspection checklists on service completion before closing work orders" |
| ERP BRD BR-HRM-008 | Performance-based technician incentives — the scorecard surfaced here |
| `04-00` §P02 | Capability set, **seven non-negotiable requirements** and five KPIs, all adopted verbatim |
| `04-00` §3 PS-08 | Offline-capable with queued sync — binding on P02, P09 and P11 |
| `02-01` §10 AS-13 | "Offline-capable apps use an append-only local journal with server-side conflict resolution" |
| `M15` §5.4, §6 T-07 | Van stock reconciliation is offline-capable and syncs through an append-only journal |
| `M45` §12.2 | Instrument fitness must be checked at the point of use — surfaced in P02 |

---

## 3. Scope Boundary

> **This is the anti-overlap control.** P02's boundary is unusual in one respect: it holds a
> **local write-ahead journal** that is authoritative *until it syncs*. That is a durability
> mechanism, not ownership — the journal's only purpose is to guarantee that what the ERP
> eventually receives is exactly what the technician recorded.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | The technician's day: job queue, sequence, accept and decline, shift clock-in and clock-out |
| 2 | Geofenced attendance capture and leave request |
| 3 | Navigation to the job site and automatic arrival detection |
| 4 | Full job context: customer, device, history, prior diagnosis, entitlement and contract terms |
| 5 | Guided diagnostic execution and structured fault coding |
| 6 | Time tracking: start, pause, resume, stop, with automatic milestone timestamps |
| 7 | Van stock view, scan-based consumption, part request, unused return and shift-end reconciliation |
| 8 | Evidence capture: before and after photographs with GPS and timestamp, video, Bengali voice notes, document scan |
| 9 | Estimate presentation on site, customer approval capture and e-signature |
| 10 | On-site payment collection and receipt issue |
| 11 | QC checklist enforcement, test result capture and service report generation |
| 12 | Test-equipment selection with fitness verification before a measurement is recorded |
| 13 | Workshop mode: bench assignment, WIP board, multi-job handling, L1/L2/L3 repair workflows |
| 14 | Logistics: device handover and collection scanning, custody confirmation |
| 15 | Remote support session launch for eligible jobs |
| 16 | In-app messaging with dispatch and workshop, escalation request, panic and safety alert |
| 17 | Offline knowledge: repair manuals, wiring diagrams, prior repair notes |
| 18 | Personal surface: performance scorecard, earnings and incentive tracker, certification status, assigned training |
| 19 | Vehicle pre-use check and defect reporting where the technician is the assigned driver |
| 20 | **The offline journal**: local durability, ordered replay, conflict surfacing and sync reporting |
| 21 | Complete Bengali interface, including every error message |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Job assignment, scheduling, routing and re-optimisation** | **M02** Field Service & Dispatch | The technician accepts or declines with a reason; the engine decides. A technician who can self-assign defeats the scheduling model |
| **The service order lifecycle, SLA clock and state machine** | **M01** Service Request & Order Management | P02 records events; M01 advances states |
| **Repair order lifecycle and bench allocation logic** | **M31** Workshop & Depot Repair | P02 is the bench surface; M31 owns the queue and the allocation |
| **Stock ledger, ownership classes, reservation and valuation** | **M15** Inventory | P02 scans a consumption; M15 decides whether it is permitted and what it costs |
| **Part compatibility and supersession** | **M37** Catalogue | P02 offers what M37 says fits |
| **Device identity resolution, ownership and genealogy** | **M17** Asset Registry | P02 submits a scan; M17 resolves it |
| **Price, estimate construction and approval thresholds** | **M11 / M01 / M36** | P02 presents an estimate it did not compute |
| **Payment processing and settlement** | **M20** Receivable & Collections | P02 initiates a collection; it never holds a payment state |
| **Equipment calibration, custody and the fitness decision** | **M45** Enterprise Asset & Test Equipment | P02 asks "may I use this instrument"; M45 answers, and the answer is binding |
| **QC pass/fail rules, quality events and CAPA** | **M23** Quality Management System | P02 enforces a checklist M23 defines |
| **Competency, certification and training content** | **M22** Learning & Competency | P02 displays status and launches assigned training |
| **Incentive calculation and payroll** | **M57 / M56** | P02 shows a number computed elsewhere; it never calculates earnings |
| **Attendance policy, roster and leave approval** | **M55 / M21** | P02 captures a clock event and submits a request |
| **Vehicle documents, servicing, fuel economics and availability** | **M46** Fleet & Vehicle Management | P02 surfaces the pre-use check; M46 owns the vehicle |
| **Consignment routing, manifests and courier assignment** | **M03** Logistics (rider surface is **P09**) | P02 confirms a handover; M03 owns the movement |
| **Remote session tooling and MSP monitoring** | **M05** Remote Support & Managed Services | P02 launches a session M05 runs |
| **Knowledge authoring, versioning and approval** | **M61** Knowledge Management | P02 caches and displays published content |
| **Customer-facing tracking, booking and feedback** | **P01** | A technician does not act inside the customer's surface |
| **Identity, session policy and credential storage** | **M29** Identity & Security | **PS-01** |

### 3.3 Shared Concepts

| Concept | P02's Role | Owning Module |
|---|---|---|
| The technician's working day | **Owns** — the defining concern of this application | P02 |
| **The offline journal** | **Owns** — local durability until sync completes | P02 |
| Job / service order | Executes and records; never advances state directly | M01 |
| Job assignment | Accepts or declines with reason | M02 |
| Van stock | Views, consumes, returns, reconciles | M15 |
| Device | Scans and identifies; records condition and genealogy | M17 |
| Test instrument | Selects; fitness answered by M45 and binding | M45 |
| QC checklist | Enforces | M23 |
| Estimate | Presents; captures decision and signature | M01 / M36 |
| Payment | Collects on site; state owned elsewhere | M20 |
| Custody | Confirms handover with evidence | M03 / M17 |
| Scorecard and earnings | Displays | M57 |
| Certification | Displays; blocks work where required | M22 |
| Knowledge | Caches and displays | M61 |
| Vehicle pre-use check | Captures | M46 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **PTC ServiceMax Go** | Offline capability with **Smart Sync**, handling both full and incremental synchronisation as needed, and delivering **full synchronisation reporting for management and audit of mobile sync performance** | **Sync reporting as a first-class management artefact is the single most influential external reference for P02.** Most offline apps treat sync as invisible plumbing. Making sync success, duration, conflict count and failure visible — to the technician *and* to the supervisor — is what converts "the app is broken" into a diagnosable, assignable fact. Also adopted: incremental sync with periodic full reconciliation | Its Salesforce platform coupling |
| **Salesforce Field Service mobile** | Offline-first design with **intelligent data priming** and offline actions; multiple users collaborating offline with built-in data reconciliation and conflict resolution | **Intelligent data priming** — the app pre-loads exactly what the technician's assigned jobs will need (device history, manuals, part catalogue subset, customer context) before they leave connectivity, rather than caching everything or nothing. This is the difference between a 40 MB useful cache and a 2 GB useless one | Its briefcase configuration model |
| **Offline-sync architecture practice** | Local-first storage, optimistic updates, delta syncing, and conflict-resolution strategies: **last-write-wins for simple fields, field-level merging where several people touch a record, and manual resolution prompts where a machine should not guess** | **The three-tier conflict policy, adopted exactly.** Critically, the third tier: some conflicts must be surfaced to a human rather than resolved automatically. A van stock count and a server-side transfer that disagree is not a merge problem — it is a variance that a named person must explain (M15 BRU-INV-12) | CRDT-based automatic merge for business records. Elegant, and wrong for records that carry financial and evidential weight |
| **Flutter for enterprise applications** | Single codebase across Android and iOS, consistent rendering across a fragmented device estate, mature offline storage | **Flutter over React Native for P02 specifically**, because the Bangladesh Android estate is highly fragmented and Flutter's own rendering engine removes a class of device-specific UI defects. P01 uses React Native; the two choices are deliberate and different, driven by the audience | Cross-portal framework uniformity for its own sake |
| **Field-service evidence practice (photo/GPS/timestamp)** | Before-and-after photographs geo-stamped and time-stamped, embedded in the service record | **Forced capture at defined points**, not optional attachment. Where evidence is optional it is captured on the jobs that go well and missing on the jobs that go to dispute | Continuous background location tracking of technicians outside working hours |
| **Rugged-device and battery practice** | Power-aware design for a full shift without charging | **A hard battery budget** — under 12% per 8-hour shift excluding navigation (`04-00`). Location polling frequency, sync cadence and screen wake are all designed against it. A technician whose phone dies at 3 p.m. stops recording | — |
| **1000FiX-specific: the Bengali-first field worker** | — | **Bengali voice notes as a first-class evidence type.** A technician can describe a fault accurately in speech in Bengali far faster than they can type it in any language. This is the single highest-yield capture decision in the application and no international benchmark supplies it | Requiring typed English notes, which produces short, uninformative records |

**Design position.** Six deliberate differences from the benchmark.

First, **offline is the default assumption, not a degraded mode.** The application is built to
run entirely from its local store and to treat connectivity as an opportunity to sync, not a
precondition to work. `04-00` requirement 7 is absolute: *no feature requires a connection that
a technician cannot complete offline.* Any proposed feature that cannot satisfy this does not
ship in P02 — it goes to P03.

Second, **the local journal is append-only and never edited.** A correction is a new entry
referencing the one it corrects. This is AS-13, and it is what makes the sync guarantee
provable: the server receives an ordered sequence of intents, replays them idempotently, and
the technician's record and the ERP's record are reconcilable line by line.

Third, **conflicts are surfaced, not silently resolved.** Where the machine can safely merge, it
does. Where it cannot — a stock variance, a contradicted state transition, a duplicated
consumption — it raises it to the technician first and the supervisor second. A silently
resolved conflict on a financially weighted record is an undetected error.

Fourth, **the app never blocks work, but it does block *closure*.** A technician can always
record. What they cannot do is close a job without the QC checklist, the evidence, the serial
of a serial-controlled part, or a fit instrument for a measurement. The gates are at completion,
not at the start, because a gate at the start is a gate that gets bypassed on paper.

Fifth, **the technician's own numbers are visible to them.** Scorecard, earnings and incentive
progress are in the application, showing the same figures management sees. An incentive scheme
whose arithmetic is invisible is not an incentive; it is a rumour.

Sixth, **the device estate is the design constraint.** `04-00` requires acceptable operation on
a mid-range Android 11 device with 3 GB RAM. That is not the phone the development team carries,
and the performance budget is measured on the phone the technicians actually have.

---

## 5. Capability Areas & Functions

### 5.1 The Day: Queue, Attendance & Navigation

| FR ID | Feature | Function — "The application shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-041 | Job queue | Present the technician's optimised job queue for the day with priority, promised window, customer, device, address and travel estimate, fully available offline (BR-FSM-008) | **P0** | L5 |
| FR-POR-042 | Accept and decline | Accept a job, or decline it with a mandatory reason code that returns it to M02 for reassignment; never permit self-assignment | **P0** | L5 |
| FR-POR-043 | Shift clock | Clock in and out with geofence verification, working offline and queueing the event, and surface the day's recorded hours (BR-HRM-004) | **P0** | L5 |
| FR-POR-044 | Leave request | Submit a leave request with type and dates to M21, and show its state | P2 | L5 |
| FR-POR-045 | Navigation | Launch turn-by-turn navigation to the job site, present a route overview of the day, and detect arrival automatically by geofence (BR-FSM-009) | **P0** | L5 |
| FR-POR-046 | Milestone timestamps | Capture departed, arrived, work started and work completed automatically, with manual correction permitted and recorded as a correction (BR-FSM-010) | **P0** | L5 |
| FR-POR-047 | Daily summary | Present the day's completed jobs, hours, parts consumed, payments collected and earnings accrued at shift end | P1 | L5 |

### 5.2 Job Execution & Diagnosis

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-048 | Job context | Present the full job context offline — customer, device, specification, complete service history, prior diagnosis, entitlement and contract terms (BR-SRM-020) | **P0** | L5 |
| FR-POR-049 | Device history offline | Hold twelve months of history for every assigned device, refreshed on sync, with the fetch time shown (M17 FR-AST-026) | **P0** | L5 |
| FR-POR-050 | Repeat-fault alert | Surface prominently that this device has returned with the same fault within the rework window, with the prior diagnosis (M17 FR-AST-029) | **P0** | L5 |
| FR-POR-051 | Guided diagnostics | Execute the diagnostic checklist or decision tree for the device category and complaint, recording each step and its result (BR-SRM-013) | **P0** | L5 |
| FR-POR-052 | Fault coding | Capture a structured fault code and resolution code from the M23/M61 taxonomy, with free text and voice permitted alongside but never instead | **P0** | L5 |
| FR-POR-053 | Time tracking | Start, pause, resume and stop labour time per job, recording pause reasons, and prevent two jobs running a clock simultaneously (BR-SRM-014) | **P0** | L5 |
| FR-POR-054 | Repair level | Record the repair level performed (L1 basic, L2 intermediate, L3 board-level) and block a level the technician is not certified for (BR-SRM-018) | **P0** | L5 |
| FR-POR-055 | Remote session | Launch a remote support session through M05 for eligible jobs, with customer consent captured | P2 | L5 |

### 5.3 Parts & Van Stock

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-056 | Van stock view | Show the technician's van stock with quantity, par level and below-minimum lines, available offline (M15 FR-INV-028) | **P0** | L5 |
| FR-POR-057 | Scan to consume | Consume a part against the job by scanning its barcode or QR, capturing the serial where the part is serial-controlled, and refusing consumption without it (BR-FSM-011, M15 BRU-INV-13) | **P0** | L5 |
| FR-POR-058 | Part request | Request a part not held in the van, showing network availability where connectivity permits and queueing the request where it does not | **P0** | L5 |
| FR-POR-059 | Return unused | Return an unconsumed part to stock in its original condition, or route it to quarantine where condition has changed | **P0** | L5 |
| FR-POR-060 | Shift-end reconciliation | Present the van reconciliation at shift end, capture a scan-based count offline, compute the variance against expected, and submit it to M15 (M15 FR-INV-031) | **P0** | L5 |
| FR-POR-061 | Variance block | Where an unresolved variance above threshold exists, show the block clearly and prevent the next parts issue, stating what must happen to clear it (M15 BRU-INV-12) | **P0** | L5 |

### 5.4 Evidence, Quality & Equipment

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-062 | Photographic evidence | Capture before and after photographs with GPS coordinates and timestamp embedded, compress on device, and queue for upload (BR-SRM-010, BR-FSM-017) | **P0** | L5 |
| FR-POR-063 | Forced capture points | Require photographic evidence at defined points — condition at receipt, condition at handover, damage claimed, board-level work — and prevent job closure without it | **P0** | L5 |
| FR-POR-064 | Voice and video | Capture Bengali voice notes and short video as evidence types of equal standing to text, transcribed asynchronously where M32 is available | **P0** | L5 |
| FR-POR-065 | Document scan | Scan a purchase invoice, warranty card or handover note into the job record through M24 | P1 | L5 |
| FR-POR-066 | QC checklist | Enforce the QC checklist for the service type before the job can be marked complete, recording each result (BR-QMS-005) | **P0** | L5 |
| FR-POR-067 | Test result capture | Capture measured test results against the expected range, marking a result outside range clearly | **P0** | L5 |
| FR-POR-068 | **Instrument fitness** | Require selection of the test instrument used for any recorded measurement by scan, verify its fitness with M45, and **refuse a measurement taken with an out-of-service instrument** (M45 FR-EAM-026, BRU-EAM-02) | **P0** | L5 |
| FR-POR-069 | Service report | Generate the service report on device from the captured record, present it to the customer, and attach it to the job | **P0** | L5 |

### 5.5 Customer Interaction on Site

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-070 | Estimate presentation | Present the estimate on device with itemised work and parts, in Bengali, and capture approve, part-approve or decline (BR-SRM-012) | **P0** | L5 |
| FR-POR-071 | E-signature | Capture the customer's signature on estimate approval and on job completion, bound to the record with a timestamp and the version signed (BR-FSM-012) | **P0** | L5 |
| FR-POR-072 | Payment collection | Collect payment on site by cash, bKash, Nagad or card, issue a receipt, and reconcile collections at shift end (BR-FIN-004) | **P0** | L5 |
| FR-POR-073 | Custody scanning | Scan a device on collection and on handover, capturing condition, accessories and the counterparty's identity and signature (M17 FR-AST-020) | **P0** | L5 |

### 5.6 Workshop Mode

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-074 | Bench and WIP | Present the workshop bench assignment and the WIP board by state, allowing a technician to hold several jobs concurrently with a clock on only one (M31) | **P0** | L5 |
| FR-POR-075 | Component genealogy | Record component-level replacement with the removed component's disposition, writing genealogy to M17 (M17 FR-AST-028) | P1 | L5 |

### 5.7 Communication, Safety, Knowledge & Personal

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-POR-076 | Messaging and escalation | Message dispatch and the workshop in-app, request escalation with a reason, and raise a **panic and safety alert** that transmits position and identity by every available channel | **P0** | L5 |
| FR-POR-077 | Offline knowledge | Hold repair manuals, wiring diagrams and prior repair notes for the technician's device categories offline, refreshed on sync (BR-FSM-016) | P1 | L5 |
| FR-POR-078 | Personal surface | Present the technician's own performance scorecard, earnings and incentive progress, certification status with expiry, and assigned training — showing the same figures management sees (BR-HRM-002, BR-HRM-008) | P1 | L5 |

> **Cross-cutting.** The vehicle pre-use check (M46 FR-FLT-024) is surfaced within P02 for
> technicians who are the assigned driver, reusing the M46 checklist rather than duplicating it.
> The offline journal, sync protocol and conflict handling are technical functions and are
> specified in §6.

---

## 6. Technical Functions

> These are the seven non-negotiable requirements in `04-00` §P02, expanded into testable
> engineering commitments, plus the platform standards that bind them.

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **24-hour offline operation** | Full operation for 24 hours with no data loss and no feature unavailable (`04-00` req. 1, 7). Verified by a scripted full-shift offline test |
| T-02 | **Sync within 30 seconds** | On reconnection, the queue syncs within 30 seconds with 100% data integrity (`04-00` req. 2) |
| T-03 | **Append-only local journal** | Every state-changing action is written to an append-only local journal before the UI acknowledges it. A correction is a new entry referencing the corrected one; no entry is edited or deleted (AS-13) |
| T-04 | **Idempotent server replay** | Every journal entry carries a client-generated idempotency key. Replay after partial failure produces exactly one server-side effect (`04-00` req. 6) |
| T-05 | **Ordered replay per aggregate** | Entries replay in capture order within a job, a van and a shift, so a consume-then-return sequence can never invert |
| T-06 | **Three-tier conflict policy** | **Tier 1** last-write-wins for technician-local fields (notes, sequence). **Tier 2** field-level merge where several actors touch one record. **Tier 3** manual resolution surfaced to the technician, then the supervisor, for stock variance, contradicted state transitions and duplicate consumption. **No financially or evidentially weighted conflict is auto-resolved** |
| T-07 | **Sync reporting** | Sync success, duration, entries pending, entries failed and conflicts raised are visible to the technician in-app and to the supervisor in P03, per technician per day |
| T-08 | **Intelligent data priming** | The app pre-loads exactly what the assigned jobs require — device history, manuals for those categories, the relevant catalogue subset, customer context — sized to a bounded cache, not a full replica |
| T-09 | **Device envelope** | Acceptable operation on a mid-range Android 11 device with 3 GB RAM (`04-00` req. 4), measured on the device estate technicians actually hold |
| T-10 | **Battery budget** | Under 12% consumption per 8-hour shift excluding navigation (`04-00` req. 5). Location cadence, sync interval and wake behaviour are designed against this budget |
| T-11 | **Media handling** | Photographs are compressed and EXIF-stamped with GPS and time on device, queued with a bounded local store, uploaded on connectivity with resumable transfer, and never lost if the queue is full — capture is refused with an explanation instead |
| T-12 | **Complete Bengali interface** | Every string including every error message (`04-00` req. 3, AS-12, PS-03). Bengali is the default for technician roles |
| T-13 | **All traffic through the gateway** | Every call routes through the M28 gateway with per-portal credentials and rate limits (**PS-02**) |
| T-14 | **No client-side business logic** | Entitlement, price, permission and stock-eligibility decisions come from their owning module. The client caches an answer; it never derives one (**PS-11**) |
| T-15 | **Fitness check is synchronous-or-cached-strict** | Instrument fitness is checked live where connectivity exists. Offline, the app uses the fitness state primed at last sync **and marks the measurement provisional**, which M45 and M23 re-verify on sync. An instrument that went out of service since priming invalidates the measurement and raises an exception |
| T-16 | **Session and credential policy** | Authentication, session lifetime and re-authentication are M29 policy. Offline operation uses a time-boxed local session that expires and requires reconnection (**PS-01, PS-12**) |
| T-17 | **Local data protection** | The local store is encrypted at rest. Customer personal data and evidence media are purged from the device on job closure plus a bounded retention window, and immediately on logout or remote wipe (AS-14) |
| T-18 | **Remote wipe and device binding** | A lost or stolen device can be wiped remotely and its binding revoked through M29 |
| T-19 | **Crash and stability** | Crash-free session rate above 99.5%, with crash reporting that never transmits customer personal data |
| T-20 | **Instrumentation** | Every critical action emits an analytics event to M25, queued offline like any other entry (**PS-10**) |
| T-21 | **Graceful degradation** | Where a feature genuinely requires connectivity — network stock search, remote session — it states so plainly and offers the offline alternative (**PS-09**) |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Actor

| Actor | Today | With P02 |
|---|---|---|
| **Field technician** | Carries a job sheet, phones the branch for history, writes notes to type up later | Has the device's full history in hand, records once, in Bengali, by voice and camera |
| **Workshop technician** | Works a bench queue held on a whiteboard | Works a WIP board with bench assignment, part holds and repair level visible |
| **Specialist L3 technician** | Board-level work documented inconsistently | Component genealogy captured as work proceeds, with instrument traceability |
| **Technician as driver** | No record that the van was checked | Completes the pre-use check in the same app before the first job |
| **Dispatcher** | Phones technicians to find out where they are | Sees arrival, start and completion timestamps as they happen |
| **Workshop supervisor** | Chases technicians for paperwork | Sees documentation completeness per job; chases only exceptions |
| **Branch store keeper** | Reconciles van stock by conversation | Receives a scanned, variance-computed reconciliation every shift |
| **Quality manager** | Audits QC compliance retrospectively from paper | QC checklists are enforced at source; instrument fitness is provable |
| **Warranty claims officer** | Chases photographs and part serials after the fact | Evidence arrives with the job, complete, because closure required it |
| **Technician (as an earner)** | Does not know what they have earned until payday | Sees jobs, score and incentive progress daily |
| **HR** | Attendance recorded separately from work | Geofenced clock events tied to the day's actual work |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Technician productivity** | Optimised queue, navigation, in-hand history, on-device documentation and no return trip to the branch to file paperwork | The delivery mechanism for the **BDT 130 lac/year** productivity benefit attributed to M02 + M26 in Scope Charter §6.2, and for KPI-011 (8–9 jobs/day from 5–6) |
| **Job documentation time** | Structured capture, voice notes, scan-to-consume | `04-00` target: **under 5 minutes per job**. At 8–9 jobs/day across 200–400 technicians this is the largest single time recovery in the estate |
| **Van shrinkage elimination** | Shift-end scanned reconciliation with variance named to a person, offline-capable | Supports M15's van variance target of **< 1%**, addressing what M15 identifies as *the single largest identified leakage channel in the business* |
| **Warranty revenue protection** | Evidence complete at closure because closure required it | Supports the **BDT 100 lac/year** warranty recovery attributed to M09, and KPI-041 (claims with complete evidence 98%) |
| **First-time fix** | Prior diagnosis in hand, repeat-fault alert, van stock visible, guided diagnostics | Supports KPI-004 (72% → **88%**) |
| **Rework reduction** | Repeat-fault surfaced before work begins rather than discovered after | Direct labour and parts avoidance |
| **On-site cash collection** | Payment collected at completion through the customer's usual wallet | Reduces receivable days; supports the **BDT 26 lac/year** cash-flow benefit attributed to M19 + M20 |
| **Quality evidence** | QC checklist enforced at source and instrument fitness verified | Protects ISO 9001 conformance and brand authorisation |
| **Incentive effectiveness** | Technicians see their own score and earnings daily | Makes the M57 incentive scheme behaviour-changing rather than notional |
| **Administrative labour** | No transcription of paper job sheets | Contributes to the **BDT 62 lac/year** cross-module administrative saving |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Technician safety** | The panic and safety alert, with position transmitted by every available channel, is the Company's practical duty of care to 200–400 people working alone in customer premises |
| **Bengali as a working language** | A technician documenting in their own language, by voice, produces a genuinely useful record. An English-only app produces three words and a tick |
| **Evidence integrity** | Geo-stamped, time-stamped, append-only capture is what makes the record defensible in a customer dispute, a brand audit or a legal matter |
| **Accountability without surveillance** | The application records work, not people. Location is captured at job events, not continuously, and the scorecard is visible to the technician first |
| **Professional standing** | A technician arriving with the device's full history and leaving a printed service report presents a different company from one arriving with a job sheet |
| **Training and progression** | Certification status, expiry and assigned training in the working app makes competency development part of the job rather than an HR exercise |
| **Data foundation** | Structured fault and resolution coding captured at source is the training signal M26 needs and M48 depends on |

---

## 8. User Journeys & State Models

### 8.1 The Offline Journal — the application's defining mechanism

```
   TECHNICIAN ACTION (consume part · capture photo · complete QC · sign off)
        │
   ┌────▼──────────────────────────────────────────┐
   │  1. WRITE TO APPEND-ONLY LOCAL JOURNAL        │  ← durable BEFORE the UI acknowledges
   │     entry_id · idempotency_key · aggregate    │
   │     sequence · payload · captured_at · actor  │
   └────┬──────────────────────────────────────────┘
        │
   ┌────▼──────────────┐
   │  2. UI ACKNOWLEDGES │  the technician moves on; nothing waits on a network
   └────┬──────────────┘
        │              ┌─────────────────────────────┐
        │  no network  │  QUEUE GROWS (bounded)      │
        ├─────────────►│  media queued separately    │
        │              │  with resumable transfer    │
        │              └─────────────┬───────────────┘
        │ network available          │
   ┌────▼───────────────────────────▼──────────────┐
   │  3. ORDERED REPLAY per aggregate               │
   │     idempotent · at-least-once · exactly-effect│
   └────┬───────────────────────────────────────────┘
        │
   ┌────▼───────────────┐        ┌──────────────────────────────┐
   │  4. SERVER APPLIES │───────►│  CONFLICT?                    │
   └────┬───────────────┘        └──────┬───────────────────────┘
        │ accepted                      │
        │                    ┌──────────▼──────────┬──────────────┐
        │              Tier 1│ last-write-wins     │ auto-resolved│
        │              Tier 2│ field-level merge   │ auto-resolved│
        │              Tier 3│ STOCK VARIANCE ·    │ SURFACED to  │
        │                    │ CONTRADICTED STATE ·│ technician,  │
        │                    │ DUPLICATE CONSUME   │ then supervisor│
        │                    └─────────────────────┴──────────────┘
   ┌────▼──────────────────────────────────────────┐
   │  5. SYNC REPORT — visible to technician (in-app)│
   │     and supervisor (P03): synced · pending ·   │
   │     failed · conflicts · duration              │
   └───────────────────────────────────────────────┘
```

| Guarantee | Mechanism | Verified By |
|---|---|---|
| Nothing recorded is lost | Journal write precedes UI acknowledgement | AC-02, AC-03 |
| Nothing is applied twice | Client idempotency key, server-side dedup | AC-04 |
| Sequence is preserved | Per-aggregate ordering with monotonic sequence | AC-05 |
| Disagreement is visible | Tier 3 conflicts surfaced, never auto-resolved | AC-06 |
| Sync health is knowable | Sync report to technician and supervisor | AC-07 |

### 8.2 The Job, as the Technician Works It

```
   ASSIGNED ──accept──► ACCEPTED ──travel──► EN ROUTE ──geofence──► ARRIVED
      │                                                                │
      │ decline (reason) → back to M02                                 │
      │                                                       ┌────────▼────────┐
      │                                                       │  DIAGNOSING     │
      │                                                       │  guided tree ·  │
      │                                                       │  fault coding · │
      │                                                       │  evidence       │
      │                                                       └────────┬────────┘
      │                                              ┌─────────────────┤
      │                                    estimate  │                 │ no estimate
      │                                    required  │                 │ needed
      │                                    ┌─────────▼──────┐          │
      │                                    │ AWAITING       │          │
      │                                    │ CUSTOMER       │          │
      │                                    │ DECISION       │          │
      │                                    └────┬───────┬───┘          │
      │                              approved   │       │ declined     │
      │                                         │       └──────────┐   │
      │                                    ┌────▼───────────────┐  │   │
      │                                    │    REPAIRING       │◄─┼───┘
      │                                    │ parts scanned ·    │  │
      │                                    │ time tracked ·     │  │
      │                                    │ instrument fitness │  │
      │                                    └────┬──────────┬────┘  │
      │                        part unavailable │          │       │
      │                              ┌──────────▼────┐     │       │
      │                              │ PARTS PENDING │     │       │
      │                              └───────────────┘     │       │
      │                                                    │       │
      │              ┌─────────────────────────────────────▼───┐   │
      │              │  CLOSURE GATE — all must pass:          │   │
      │              │   ✓ QC checklist complete               │   │
      │              │   ✓ evidence captured at forced points  │   │
      │              │   ✓ serials captured for controlled parts│  │
      │              │   ✓ instrument fit for every measurement│   │
      │              │   ✓ customer signature                  │   │
      │              └─────────────────┬───────────────────────┘   │
      │                                │ all pass                  │
      │                          ┌─────▼──────┐                    │
      └─────────────────────────►│ COMPLETED  │◄───────────────────┘
                                 └─────┬──────┘
                                       │ payment collected where due
                                 ┌─────▼──────┐
                                 │  CLOSED    │──► journal syncs → M01 advances
                                 └────────────┘
```

> **The closure gate is the application's central control.** A technician may record anything at
> any time; they may not *close* until the record is complete. Placing the gate at closure
> rather than at each step means the technician is never blocked mid-repair by a form, and the
> record is never incomplete when it reaches the ERP.

---

## 9. Portal Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| PRU-P02-01 | No feature requires a connection that a technician cannot complete offline (`04-00` req. 7) | **H** | CTO |
| PRU-P02-02 | Every state-changing action is written to the append-only local journal before the UI acknowledges it | **H** | CTO |
| PRU-P02-03 | A journal entry is never edited or deleted; a correction is a new entry referencing it (AS-13) | **H** | CTO |
| PRU-P02-04 | Every journal entry is idempotent on the server; replay produces exactly one effect | **H** | CTO |
| PRU-P02-05 | A Tier 3 conflict — stock variance, contradicted state, duplicate consumption — is never auto-resolved | **H** | Operations Director |
| PRU-P02-06 | A technician cannot self-assign a job; acceptance and decline with reason are the only actions | **H** | Operations Director |
| PRU-P02-07 | A job cannot be closed without the QC checklist complete (BR-QMS-005) | **H** | Quality Manager |
| PRU-P02-08 | A job cannot be closed without evidence captured at every forced-capture point | **H** | Quality Manager |
| PRU-P02-09 | A serial-controlled part cannot be consumed without capturing its serial (M15 BRU-INV-13) | **H** | Warehouse Manager |
| PRU-P02-10 | A measurement recorded against an out-of-service instrument is refused; offline, it is marked provisional and re-verified on sync (M45 BRU-EAM-02) | **H** | Quality Manager |
| PRU-P02-11 | A technician cannot record a repair level they are not certified for (M22) | **H** | Quality Manager |
| PRU-P02-12 | An unresolved van variance above threshold blocks the next parts issue (M15 BRU-INV-12) | **H** | Warehouse Manager |
| PRU-P02-13 | Labour time runs on at most one job at a time | **H** | Operations Director |
| PRU-P02-14 | Every user-visible string, including every error, exists in Bengali before release (`04-00` req. 3) | **H** | Operations Director |
| PRU-P02-15 | Location is captured at defined job events, never continuously outside working hours | **H** | HR Director |
| PRU-P02-16 | Customer personal data and evidence media are purged from the device after closure plus the retention window, and immediately on logout | **H** | CTO |
| PRU-P02-17 | The local store is encrypted at rest, and a lost device can be wiped remotely (AS-14) | **H** | CTO |
| PRU-P02-18 | No price, entitlement or eligibility value is derived in the client (**PS-11**) | **H** | CTO |
| PRU-P02-19 | Sync status is visible to the technician and to their supervisor at all times | **C** | Operations Director |
| PRU-P02-20 | The panic and safety alert transmits by every available channel and is never rate-limited or suppressed | **H** | HR Director |
| PRU-P02-21 | The technician's scorecard and earnings show the same figures management sees | **C** | HR Director |
| PRU-P02-22 | Battery consumption stays under 12% per 8-hour shift excluding navigation (`04-00` req. 5) | **C** | Field Platform Squad |

---

## 10. Data, Caching & State Model

### 10.1 Local Store — permitted, bounded, purged

| Object | Purpose | Retention | Reconstructible From |
|---|---|---|---|
| **Journal entries (pending)** | Durability of unsynced actions — **the only locally authoritative data** | Until synced and acknowledged | Nothing — this is the point |
| Journal entries (synced) | Reconciliation and dispute evidence | 7 days, then purged | Server-side record |
| Assigned job queue and context | Offline execution | Assignment period + 24 h | M01, M02 |
| Device history projection | Diagnosis without a network | 12 months per assigned device; purged on closure + window | M17 |
| Van stock projection | Consumption and reconciliation | Current shift, refreshed on sync | M15 |
| Catalogue subset | Part identification and compatibility | 7 days, primed by category | M37 |
| Instrument fitness snapshot | Offline fitness check (**provisional**) | Until next sync | M45 |
| Knowledge documents | Manuals and diagrams for assigned categories | 30 days | M61 |
| QC checklist definitions | Closure gate | Until version change | M23 |
| Media queue | Photographs, video, voice pending upload | Until uploaded, bounded store | — |
| Session context | Time-boxed offline session | Per M29 policy | M29 |
| Scorecard and earnings snapshot | Personal surface offline | 24 hours | M57 |

### 10.2 Never Held Locally

| Item | Reason |
|---|---|
| Another technician's jobs, stock or scorecard | Scope is own-assignment only (`05-04` §1) |
| Customer cost, margin or internal notes beyond the job's own estimate | `05-04` §5 field restrictions |
| Payment credentials | Collection is a gateway handoff |
| Authentication credentials | M29 owns identity; the app holds a token reference |
| Pricing, entitlement or permission rules | PRU-P02-18 |
| Customer data for jobs no longer assigned | PRU-P02-16 |

### 10.3 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order`, `fix.work.order` | M01 / M31 | Read; submit execution events |
| `fix.dispatch.assignment` | M02 | Read; accept or decline |
| `fix.asset`, `fix.asset.service.history`, `fix.part.genealogy` | M17 | Read; submit condition, custody and genealogy |
| `fix.stock.quant` (van), `fix.van.reconciliation` | M15 | Read; submit consumption, return and reconciliation |
| `fix.tool.register`, fitness state | M45 | Read; submit usage |
| `fix.qc.record` | M23 | Submit |
| `fix.estimate` | M01 / M36 | Read; submit decision and signature |
| `fix.payment` | M20 | Initiate collection |
| `fix.document` | M24 | Submit media and documents |
| `fix.competency`, certification | M22 | Read; block uncertified work |
| `fix.attendance`, `fix.leave` | M55 / M21 | Submit |
| `fix.incentive`, scorecard | M57 | Read |
| `fix.knowledge.article` | M61 | Read, cached |
| `fix.vehicle.check` | M46 | Submit |
| `fix.consignment`, custody event | M03 | Submit |

---

## 11. Automations & Notifications

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-P02-01 | Job assigned by M02 | Push the job to the technician's queue and prime its context, history, manuals and catalogue subset before they leave connectivity | Job appears on next sync; priming retried |
| AUT-P02-02 | Shift start | Prompt the vehicle pre-use check where the technician is the assigned driver, and block the first job start until it is submitted (M46 AUT-FLT-07) | Configurable grace period, then block and notify |
| AUT-P02-03 | Geofence entered at the job site | Record arrival automatically and start the on-site clock | Manual arrival with a recorded correction |
| AUT-P02-04 | Device identified at a job | Check the rework window and surface a repeat-fault alert with the prior diagnosis (M17 AUT-AST-07) | Show history without the alert |
| AUT-P02-05 | Part scanned for consumption | Validate ownership class and serial requirement with M15; where offline, queue and validate on sync | Offline consumption is provisional; a rejected consumption raises a Tier 3 conflict |
| AUT-P02-06 | Instrument selected for a measurement | Verify fitness with M45; offline, use the primed snapshot and mark the measurement provisional | An instrument out of service since priming invalidates the measurement and raises an exception to M23 and M45 |
| AUT-P02-07 | Job marked complete | Evaluate the closure gate; on failure, list precisely which items are missing | Job stays open; nothing is silently accepted |
| AUT-P02-08 | Connectivity restored | Replay the journal in order, upload media resumably, and present the sync report | Retry with backoff; surface pending and failed counts continuously |
| AUT-P02-09 | Tier 3 conflict detected on replay | Surface it to the technician with both versions and the action required; escalate to the supervisor after the configured period | Conflict remains open and reportable |
| AUT-P02-10 | Shift end | Prompt the van reconciliation, compute the variance offline, and submit it (M15 AUT-INV-05) | Block the next issue after the grace period |
| AUT-P02-11 | Journal pending beyond the threshold | Warn the technician, then notify the supervisor in P03 that a device is holding unsynced work | Escalate; never discard |
| AUT-P02-12 | Certification approaching expiry | Notify the technician and block the affected repair levels on expiry (BR-HRM-003) | Notify; block at expiry |
| AUT-P02-13 | Panic alert raised | Transmit position and identity to dispatch, the branch manager and the safety contact by every available channel including SMS | Retry indefinitely; never rate-limited |
| AUT-P02-14 | Local storage approaching capacity | Warn the technician and refuse further media capture with an explanation rather than dropping queued evidence | Refuse capture; never silently discard |

---

## 12. Module Interfaces

### 12.1 Modules P02 Consumes

| Module | What | Mechanism |
|---|---|---|
| M29 Identity & Security | Authentication, time-boxed offline session, device binding, remote wipe | OIDC via gateway |
| M28 Integration Platform | Every call; sync endpoint, rate limits, observability | Gateway |
| M02 Field Service & Dispatch | Job assignment, queue order, route, geofence definitions | REST + push |
| M01 Service Order | Job context, estimate, state | REST + events |
| M31 Workshop | Bench assignment, WIP board, repair order context | REST |
| M17 Asset Registry | Device identity, twelve-month history, repeat-fault flag, entitlement | REST, primed |
| M15 Inventory | Van stock, par levels, consumption validation, reconciliation | REST + commands |
| M37 Catalogue | Part identification, compatibility, supersession | REST, cached |
| M45 Enterprise Assets | **Instrument fitness** — synchronous where connected, primed snapshot offline | REST (synchronous) |
| M23 Quality | QC checklist definitions, fault taxonomy | REST, cached |
| M22 Competency | Certification status and repair-level authorisation | REST |
| M57 Performance & Incentives | Scorecard and earnings | REST |
| M55 / M21 Workforce & HR | Roster, geofence, leave state | REST |
| M46 Fleet | Pre-use checklist for the assigned vehicle | REST |
| M61 Knowledge | Manuals, diagrams, repair notes | REST, cached |
| M11 Pricing | Estimate figures for presentation | REST |
| M20 Receivable | Payment collection initiation | REST |
| M05 Managed Services | Remote session launch | REST |
| M24 Documents | Media and document storage | REST (resumable upload) |
| M65 Localisation | Bengali translation bundles | Build-time + REST |

### 12.2 What P02 Writes Back

| Target | What | Mechanism |
|---|---|---|
| M01 | Diagnosis, fault code, time entries, completion, service report | Journal replay (idempotent) |
| M02 | Accept/decline with reason, arrival, departure, milestone timestamps | Journal replay |
| M31 | Bench events, repair-level record, component swap | Journal replay |
| M15 | Part consumption with serial, unused return, van reconciliation with variance | Journal replay |
| M17 | Device condition, custody transfer, part and component genealogy | Journal replay |
| M45 | Instrument usage against a measurement | Journal replay |
| M23 | QC checklist results, test results, quality exceptions | Journal replay |
| M20 | On-site payment collection and receipt issue | Journal replay |
| M24 | Photographs, video, voice notes, scanned documents | Resumable upload |
| M55 / M21 | Clock in/out with geofence, leave request | Journal replay |
| M46 | Vehicle pre-use check and defect report | Journal replay |
| M03 | Custody confirmation on collection and handover | Journal replay |
| M25 / M62 | Usage, timing and sync-health analytics | Event stream (queued) |

### 12.3 Events P02 Consumes

| Event | Source | Effect in P02 |
|---|---|---|
| `dispatch.job_assigned` / `dispatch.job_reassigned` | M02 | Add or remove from the queue; prime or purge context |
| `service_order.updated` | M01 | Refresh job context |
| `stock.reserved` / `stock.stockout` | M15 | Update van and part-request state |
| `equipment.out_of_service` | M45 | Invalidate the primed fitness snapshot for that instrument |
| `asset.repeat_fault_detected` | M17 | Raise the rework alert on the job |
| `certification.expiring` | M22 | Warn; block affected repair levels at expiry |
| `vehicle.off_road` | M46 | Warn the assigned driver and notify dispatch |
| `incentive.updated` | M57 | Refresh the scorecard snapshot |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-P02-01 | Google Maps Platform / navigation | Outbound | Turn-by-turn navigation, route overview, geofencing |
| INT-P02-02 | Firebase Cloud Messaging | Inbound | Job assignment push and priority alerts |
| INT-P02-03 | Device camera, microphone and GPS | Local | Evidence capture with EXIF GPS and timestamp |
| INT-P02-04 | Bluetooth and USB barcode/QR scanners | Local | High-volume scanning in workshop mode |
| INT-P02-05 | bKash / Nagad / card SDK | Outbound | On-site payment collection; via M20 and M28 |
| INT-P02-06 | Mobile device management, where deployed | Inbound | Device binding, remote wipe, application distribution |

### 12.5 API Surface Consumed

| Endpoint | Method | Purpose | Owner |
|---|---|---|---|
| `/api/v1/sync/pull` | GET | Prime assigned jobs, context, history, catalogue subset, manuals | M28 orchestrated |
| `/api/v1/sync/push` | POST | **Ordered, idempotent journal replay with conflict response** | M28 orchestrated |
| `/api/v1/sync/report` | GET | Sync health for this technician and device | M28 |
| `/api/v1/dispatch/assignments` | GET/POST | Queue; accept or decline with reason | M02 |
| `/api/v1/service-orders/{id}` | GET | Full job context | M01 |
| `/api/v1/assets/{id}/history` | GET | Twelve-month device history | M17 |
| `/api/v1/van/{id}/stock` | GET | Van position and par status | M15 |
| `/api/v1/van/{id}/reconciliation` | POST | Shift-end reconciliation (offline-capable) | M15 |
| `/api/v1/stock/issues` | POST | Consume a part with serial capture | M15 |
| `/api/v1/equipment/{id}/fitness` | GET | **May this instrument be used right now** | M45 |
| `/api/v1/qc/records` | POST | QC checklist and test results | M23 |
| `/api/v1/documents/upload` | POST | Resumable media upload | M24 |
| `/api/v1/payments/collect` | POST | On-site payment collection | M20 |
| `/api/v1/attendance/clock` | POST | Geofenced clock in and out | M55 |
| `/api/v1/technicians/me/scorecard` | GET | Personal performance and earnings | M57 |
| `/api/v1/vehicles/{id}/checks` | POST | Vehicle pre-use check | M46 |
| `/api/v1/safety/panic` | POST | Panic and safety alert | M29 / M27 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| **R10 Senior Technician** | C R U | **Assigned jobs + zone** — full execution, all repair levels they are certified for |
| **R11 Junior Technician** | C R U | **Assigned jobs only** — execution limited to certified repair levels; escalation available |
| **R12 Specialist Technician (L3 / board-level)** | C R U | **Assigned jobs + workshop** — board-level workflows, component genealogy; also holds P03 access |
| — Own van stock | C R U | Own van only; never another technician's |
| — Own scorecard and earnings | R | Own record only |

> **Per `05-04` §2, only R10, R11 and R12 hold P02 access.** No supervisor, manager or agent
> signs in to P02. A supervisor observing technician work does so in P03 under their own
> identity. There is no impersonation path into P02.

**Field-level restrictions.** `unit_cost`, `margin`, `vendor_price` and
`technician_incentive_detail` for any other technician are absent from every P02 payload
(`05-04` §5). A technician sees the estimate presented to their customer and the parts cost
basis only where their role permits it; they never see another technician's earnings, another
customer's data, or another van's stock.

**Segregation of duties.** Per `05-04` §6 SOD-07, the technician who performs a repair does not
perform its independent QC above the value threshold; P02 enforces this by routing the QC step
to a different identity where the threshold applies. Per M15 SOD-05, a technician's van
reconciliation count does not approve the adjustment arising from it.

---

## 14. Analytics & Instrumentation

| Instrumentation | What Is Captured | Consumer |
|---|---|---|
| **Sync health** | Success rate, duration, entries pending, entries failed, conflicts by tier — per technician, per device, per day | M30, M25 — **the application's primary operational metric** |
| Job documentation time | Time from arrival to closure-gate pass, decomposed by step | M25, M02 |
| Closure-gate failures | Which gate item blocked closure, how often, by technician and job type | M23, M25 |
| Offline duration | Time operated without connectivity per shift, and the queue depth reached | M30 |
| Evidence capture | Photographs, voice notes and video per job; forced-capture compliance | M23, M09 |
| Part consumption | Scan versus manual entry rate; serial capture compliance | M15 |
| Instrument fitness | Fitness checks performed, refusals, provisional offline measurements re-verified | M45, M23 |
| Diagnostic path | Guided-tree completion, abandonment and free-text fallback rate | M23, M61 |
| Van reconciliation | Completion rate per shift, variance value, time taken | M15 |
| Accept and decline | Decline rate with reason, by technician and job type | M02 |
| Battery and performance | Consumption per shift, cold-start time, frame rendering on the target device class | M30 |
| Crash and stability | Crash-free session rate, crash cause, device model distribution | M30 |
| Knowledge usage | Manuals opened, searches, searches returning nothing | M61 |
| App adoption | Daily active among active technicians; feature usage distribution | M25, HR |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | **Daily active usage among active technicians** | 0% | 90% | **> 95%** |
| — | **Job documentation time** | unmeasured | < 7 min | **< 5 min** |
| — | **Offline sync failures** | n/a | **Zero** | **Zero** |
| — | **Crash-free sessions** | n/a | > 99.0% | **> 99.5%** |
| — | **Technician satisfaction with the app** | n/a | > 3.8/5 | **> 4.2/5** |
| — | Sync completion within 30 seconds of reconnection | n/a | 95% | **99.5%** |
| — | Journal entries lost | n/a | **Zero** | **Zero** |
| — | Tier 3 conflicts resolved within one shift | n/a | 85% | **97%** |
| — | Forced-capture compliance at closure | ~0% | **100%** | **100%** |
| — | Serial capture on serial-controlled consumption | ~0% | **100%** | **100%** |
| — | Van reconciliation completed per shift | 0% | 95% | **99.5%** |
| — | Measurements with a verified fit instrument | 0% | 98% | **100%** |
| — | Battery consumption per 8-hour shift (excl. navigation) | n/a | < 15% | **< 12%** |
| — | Bengali string completeness | n/a | **100%** | **100%** |
| **KPI-004** *(supported)* | First-time fix rate | 72% | 82% | **88%** |
| **KPI-011** *(supported)* | Technician jobs per day | 5–6 | 7–8 | **8–9** |
| **KPI-041** *(supported)* | Warranty claims with complete evidence | unmeasured | 92% | **98%** |

> **Register note.** The first five metrics are adopted verbatim from `04-00` §P02. P02 has
> **no KPI-0nn identifiers allocated**; all fourteen unnumbered metrics require allocation in
> `06-02` (not yet issued). Recorded as an audit action. KPI-004, KPI-011 and KPI-041 are owned
> by M02, M02 and M09 respectively and are shown as *supported*, not claimed.

---

## 16. Delivery

### 16.1 Technology & Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L5 | **Flutter application** — the whole surface: queue, execution, evidence, parts, QC, workshop mode, personal | 72% |
| L5 | **Offline journal, sync engine and conflict resolution** — the hardest component, shared in design with P09 and P11 | 20% |
| L4 | Local encrypted store (SQLite), resumable media transfer, scanner and camera integration | 8% |

> P02 is entirely custom and necessarily so. `04-00` specifies a PWA *or* native app; **native
> is selected** because the offline guarantee, the battery budget, the camera and scanner
> integration and the 3 GB RAM device envelope are not reliably achievable in a browser on the
> Bangladesh Android estate. The sync engine is designed once here and reused by P09 and P11.

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| **CD-202** | `p02_technician_app` — job queue and day, execution and diagnosis, evidence capture, parts and van reconciliation, QC and instrument fitness, customer interaction, workshop mode, communication and safety, offline knowledge, personal surface, **and the offline journal and sync engine** | Flutter application | 40 PW |

> **CD register.** One ID, **CD-202**, claimed from the extension block following CD-201 (P01).
> **All CD IDs remain provisional** pending the unified CD register required by audit finding
> M-01 in `02-05`.
>
> **Effort note.** 40 PW is the largest single application in the suite. Roughly a quarter of it
> is the offline journal and sync engine, which is genuinely difficult work and must not be
> estimated as though it were screens. `02-05` §5.4 allocates 126 PW across four Flutter
> applications; P02 consumes the largest share of that, and P09 and P11 benefit from the sync
> engine built here.

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| M29 Identity & Security | Authentication, device binding, remote wipe, offline session policy |
| M28 Integration Platform | The sync endpoint is the single most important API in the estate |
| M01 Service Order | Jobs must exist |
| M02 Field Service & Dispatch | Jobs must be assigned; **P02 and M02 are delivered together** |
| M17 Asset Registry | Device identity and history — the W1 identity core is the binding prerequisite |
| M15 Inventory | Van stock and reconciliation; **both land in W2 and are mutually dependent** |
| M23 Quality | QC checklists — may be a minimal set in W2, complete in W5 |
| M22 Competency | Repair-level authorisation; may be a static matrix in W2 |
| M24 Documents | Media storage with retention |
| M45 Enterprise Assets | Instrument fitness — **available W5**. Before then, instrument capture is recorded without a fitness gate, and this is a stated interim risk |
| M65 Localisation | Bengali is a release gate, not a follow-up |

> **Sequencing risk.** The instrument-fitness gate (FR-POR-068) depends on M45, which lands in
> Wave 5, three waves after P02. From W2 to W5, measurements are recorded with the instrument
> identified but not fitness-verified. This is recorded as an accepted interim gap in
> `M45` §16.3 and must not be forgotten at the Wave 5 gate.

### 16.4 Rollout

| Stage | Scope | Wave |
|---|---|---|
| Pilot | 20 technicians at 2 branches, including one district branch on poor connectivity | W2, month 6 |
| Branch wave | Dhaka branches | W2, months 7–8 |
| National | All 51+ locations | W2–W4, per `06-01` §6 rollout pattern |
| Workshop mode | Central workshops and L3 benches | W2, with M31 |

> **Rollout position.** The pilot **must** include a district branch on genuinely poor
> connectivity. A pilot conducted only in Dhaka on office wifi validates nothing about the one
> requirement that governs this application. There is no paper fallback after cutover at a
> branch — the application is the system of record for field work — so each branch's cutover is
> gated on its technicians completing a full offline shift successfully.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | The application operates fully for 24 hours with no connectivity, with no feature unavailable and no data loss | Scripted 24-hour offline test with 20 technicians across five shifts |
| AC-02 | Every state-changing action is durable in the local journal before the UI acknowledges it | Kill-the-process test at every action point |
| AC-03 | No journal entry is lost across app termination, device restart, storage pressure or forced update | Fault-injection suite |
| AC-04 | Replaying a journal after partial failure produces exactly one server-side effect per entry | Idempotency test with induced mid-replay failure |
| AC-05 | Entries replay in capture order per aggregate; a consume-then-return sequence cannot invert | Ordering test with deliberately shuffled transport |
| AC-06 | A stock variance, a contradicted state transition and a duplicate consumption are each surfaced for manual resolution, never auto-resolved | Three scripted conflict scenarios |
| AC-07 | Sync completes within 30 seconds of reconnection with 100% data integrity, and the sync report is visible to technician and supervisor | Timed reconnection test at full queue depth |
| AC-08 | A job cannot be closed with an incomplete QC checklist, missing forced-capture evidence, an uncaptured serial on a controlled part, or an unfit instrument | Four negative tests at the closure gate |
| AC-09 | A measurement recorded offline against an instrument that went out of service since priming is invalidated on sync and raises an exception to M23 and M45 | Scripted scenario with M45 |
| AC-10 | A technician cannot self-assign a job through any path | Negative test including direct API call |
| AC-11 | A technician cannot record a repair level they are not certified for | Negative test with M22 |
| AC-12 | Van reconciliation completes offline, computes variance correctly, and an unresolved variance above threshold blocks the next issue | Scripted scenario with M15 |
| AC-13 | Photographs carry correct GPS coordinates and timestamps, survive queueing, and upload resumably after interruption | Evidence-integrity test |
| AC-14 | When the media queue reaches capacity, capture is refused with an explanation and no queued evidence is discarded | Storage-pressure test |
| AC-15 | The application runs acceptably on a mid-range Android 11 device with 3 GB RAM | Performance test on the actual technician device estate |
| AC-16 | Battery consumption stays under 12% per 8-hour shift excluding navigation | Instrumented field measurement across 20 technicians |
| AC-17 | Crash-free session rate exceeds 99.5% over 30 days in production | Production stability report |
| AC-18 | Every string, including every error message, renders in Bengali, and Bengali is the default for technician roles | Translation coverage report at 100% |
| AC-19 | Customer data and evidence media are purged from the device after closure plus the retention window, and immediately on logout | Storage audit after a scripted lifecycle |
| AC-20 | The local store is encrypted at rest and a lost device can be wiped remotely | Security test with M29 |
| AC-21 | A technician can access only their own jobs, own van and own scorecard | Isolation test including direct API call |
| AC-22 | The panic alert transmits by every available channel within 10 seconds and is never suppressed | Safety drill at two branches |
| AC-23 | A branch cutover is gated on its technicians completing a full offline shift successfully | Cutover records per branch |
| AC-24 | Service Operations Director and technician representatives sign off UAT, conducted in Bengali on real jobs | Signed UAT record |

**Definition of done:** the seven non-negotiable requirements in `04-00` §P02, the twelve
cross-portal standards in `04-00` §3, plus the 24 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the actual technician device estate — models, Android versions, RAM, storage? The performance envelope is meaningless until this is known | CTO / Operations Director | **W2 minus 4 months** |
| Q-02 | Are devices company-issued or personal (BYOD)? This determines whether remote wipe, device binding and encrypted storage are enforceable at all | CTO / HR Director / CFO | **W2 minus 4 months** |
| Q-03 | Who pays for the technician's mobile data, and what monthly volume does priming plus media upload actually consume? | CFO / Operations Director | W2 design |
| Q-04 | What is the retention window for customer data and evidence media on the device after job closure? | Legal / Quality Manager | W2 design |
| Q-05 | Is continuous location tracking during working hours acceptable to the workforce, or is job-event capture the agreed limit? This is a workforce-relations decision, not a technical one | HR Director / Operations Director | **W2 design** |
| Q-06 | What is the escalation path and response commitment behind the panic alert, and who is on the receiving end at 9 p.m.? | HR Director / Operations Director | W2 design |
| Q-07 | Which forced-capture points apply per service type? Too many and technicians resent it; too few and evidence is missing when it matters | Quality Manager | W2 design |
| Q-08 | Is a Bluetooth scanner issued for workshop mode, or is the phone camera sufficient at workshop scan volumes? | Workshop Supervisor / Procurement | W2 build |
| Q-09 | What happens to a job if a technician's device is lost with unsynced work? Is there a recovery procedure, and what is the maximum acceptable loss? | Operations Director / CTO | **W2 design** |
| Q-10 | How is the SOD-07 independent-QC threshold applied in the field, where a second technician may not be present? | Quality Manager | W2 design |
| Q-11 | Are technicians permitted to see the customer's price on the estimate, and the parts cost basis? | CFO / Operations Director | W2 design |
| Q-12 | Is iOS required at all, given the technician device estate, or is Android-only acceptable for the life of the programme? | CTO | W2 scoping |

---

## 19. References

**Internal**
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` §P02 (capability set, seven
non-negotiable requirements, KPIs), §3 PS-01…PS-12, §4 ·
`P01_Customer_Self_Service_Portal_and_Mobile_Application.md` ·
`P03_Admin_Operations_Portal.md` · `P09_Logistics_and_Rider_Application.md` ·
`P11_Field_Auditor_and_Quality_Application.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M01_Service_Request_and_Order_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md` ·
`03_Modules/E_Supply_Chain_and_Inventory/M15_Spare_Parts_and_Inventory_Management.md`
§5.4, §6 T-07, §9 BRU-INV-12 and BRU-INV-13 ·
`03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md`
§5.4 FR-AST-026 and FR-AST-029 ·
`03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md`
§5.3 FR-EAM-026, §9 BRU-EAM-02, §12.2, §16.3 ·
`03_Modules/F_Asset_Equipment_and_Facilities/M46_Fleet_and_Vehicle_Management.md`
§5.4 FR-FLT-024 ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §10 (AS-08, **AS-13**, AS-14) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §5.4 (Flutter applications) ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` §4 ·
`05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md` §1, §2, §5, §6 SOD-07 ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §6 (rollout pattern)

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §4.1 Portal 2, BR-FSM-007
… BR-FSM-013, BR-FSM-016, BR-FSM-017, BR-SRM-010, BR-SRM-013, BR-SRM-014, BR-SRM-018,
BR-SRM-020, BR-QMS-005, BR-HRM-002, BR-HRM-003, BR-HRM-004, BR-HRM-008, BR-FIN-004 ·
`1000FiX_Services_Company_Profile.md` §Service Delivery Process, §Quality Assurance Process

**External benchmark**
[ServiceMax Go — offline Smart Sync with full synchronisation reporting for management and audit](https://www.ptc.com/en/products/servicemax/go-mobile) ·
[ServiceMax field service management platform](https://www.ptc.com/en/products/servicemax) ·
[Salesforce Field Service mobile — offline-first with intelligent data priming and offline actions](https://play.google.com/store/apps/details?id=com.salesforce.fieldservice.app&hl=en-US) ·
[Salesforce mobile offline guide 2026 — data priming and conflict resolution](https://www.jitendrazaa.com/blog/salesforce/salesforce-mobile-offline-complete-guide-2026-briefcase-2/) ·
[Offline and sync architecture for field operations — local-first storage, optimistic updates, delta sync, and conflict strategies including manual resolution where a machine should not guess](https://www.alphasoftware.com/blog/offline-sync-architecture-tutorial-examples-tools-for-field-operations) ·
[Why offline-first mobile apps matter in field service operations](https://www.nustechnology.com/blog/why-offline-first-mobile-apps-matter-in-field-service-operations) ·
[Flutter versus React Native for enterprise applications](https://shorebird.dev/blog/react-native-vs-flutter-for-enterprise-apps) ·
[Flutter versus React Native 2026 — enterprise decision guide](https://internative.net/insights/blog/react-native-vs-flutter-enterprise-decision-2026)

---

*Portal P02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
