---
id: FIX-ERP2-M31
module_id: M31
module_code: WSR
module_name: Workshop & Depot Repair Management
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Service Operations Director
system_owner: Service Squad
priority: P1
wave: W2
---

# M31 — Workshop & Depot Repair Management
### Category A · Code `WSR` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M31 |
| **Module code** | `WSR` |
| **Category** | A — Service Delivery & Operations |
| **Status** | ★ **New** — added after enterprise benchmarking revealed the gap |
| **Priority** | **P1** |
| **Delivery wave** | W2 (Months 5–8) |
| **Business owner** | Service Operations Director |
| **System owner** | Service Squad |
| **Delivery layers** | L1 (Odoo `repair`) + L2 (OCA `fieldservice_repair`, `quality`) + L5 (custom) |
| **Custom modules** | `cd_workshop`, `cd_bench`, `cd_repair_order`, `cd_test_burnin` |
| **Requirement range** | FR-WSR-001 … FR-WSR-053 |
| **Requirement count** | **53** *(measured 2026-08-13; 5 allocated identifiers retired unused — see below)* |
| **Effort estimate** | 30 person-weeks |
| **Depends on** | M01 Service Order · M17 Asset Registry · M15 Inventory · M22 Competency · M45 Test Equipment · M23 Quality |
| **Depended on by** | M01, M03, M09, M14, M20, M23, M25, M61, M54, M57 |

---

## 2. Purpose

M31 owns what happens **inside the workshop**: which bench a device sits on, which technician
has it, which components were replaced, which tests it passed, and how long each of those
took.

This is the module the v2.0 draft did not have, and its absence would have been expensive.
1000FiX performs **Level 1, Level 2 and Level 3 (board-level, micro-soldering) repair** across
laptops, desktops, servers, printers, motherboards, mobile devices and appliances. That work
happens at a bench, not in the field, and it has an entirely different operating rhythm from
a field visit: parallel work in progress, component-level part consumption, ESD-controlled
environments, calibrated test equipment, burn-in periods measured in hours, and a queue that
must be balanced across specialised skills.

### Why It Exists

Every tier-one service ERP separates the customer-facing service order from the internal
repair execution — SAP calls it *In-House Repair*, IFS calls it the *Repair Shop*, Oracle and
QAD call it *Depot Repair*. They separate them because the two objects answer different
questions, change at different rates, and have different audiences.

Without M31:

- Workshop work in progress stays on a whiteboard, invisible to the branch and to the customer
- Bench capacity cannot be measured, so throughput cannot be improved
- Component-level parts consumption is not traceable to the board it went into
- Burn-in and test results are recorded on paper, so a rejected warranty claim cannot be defended
- A device that visits two workshops has no coherent record of where it has been

### Evidence Basis

| Source | What It Establishes |
|---|---|
| Company Profile §Motherboard Repair Service | "Specialized motherboard diagnostics and repair — laptop and desktop motherboard services" — board-level work is a named service line |
| Company Profile §Laptop Repair | "Level-based repair services (Level 1, Level 2, etc.)" — repair levels are already a commercial concept |
| Company Profile §Server Repair, §Printer/Plotter/Photocopier | Bench-based service lines requiring workshop capacity |
| ERP BRD BR-SRM-018 | "Repair level classification: Level 1 (Basic), Level 2 (Intermediate), Level 3 (Board-Level/Advanced)" |
| ERP BRD §6.2 Process 3 | Current state: paper forms returned to the service centre, entered 1–3 days late |
| Business Plan §Refurbishment | Refurbishment is bench work requiring the same workshop infrastructure |
| Category A Overview §3 | The M01/M31 boundary decision |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Repair order creation from a service order, refurbishment order, RMA or internal request |
| 2 | Workshop and bench master: capability, capacity, ESD zone, equipment |
| 3 | Bench allocation, queue management and work-in-progress board |
| 4 | Repair level classification and skill-gated routing (L1 / L2 / L3) |
| 5 | Component-level diagnosis, teardown record and repair execution |
| 6 | Component-level parts consumption with serial capture and genealogy |
| 7 | Test protocols, burn-in scheduling and result capture |
| 8 | Rework loops inside the workshop before release |
| 9 | Workshop-to-workshop transfer for specialist stages |
| 10 | Repair costing: labour minutes, component cost, equipment time |
| 11 | Workshop throughput, utilisation and cycle-time analytics |
| 12 | Release of the repaired device back to the owning service order |
| 13 | Repair method capture and promotion to the knowledge library |
| 14 | ESD, safety and environmental compliance records at the bench |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Customer communication and the tracking timeline | **M01** | The customer never sees bench detail; M31 has no customer-facing surface |
| Service order state, SLA and promise date | **M01** | One promise per customer request, not per repair stage |
| Estimate and customer approval | **M36** / **M01** | Commercial decisions live outside the workshop |
| Field visits and technician routing | **M02** | Different work pattern, different optimisation problem |
| Physical movement of devices between sites | **M03** | Custody is a legal chain owned by logistics |
| Parts stock levels, valuation and reordering | **M15** | M31 consumes; it does not hold or value stock |
| Test equipment calibration schedule and certificates | **M45** | Equipment is an enterprise asset with its own lifecycle |
| Technician certification | **M22** | M31 enforces the gate; it does not certify |
| Quality checklist authoring and CAPA | **M23** | M31 executes checklists and raises non-conformances |
| Refurbishment grading standard and resale | **M14** | M31 performs the bench work; M14 owns the grading standard and commercial outcome |
| Warranty claim to the brand | **M09** | M31 supplies the technical evidence; M09 files the claim |

### 3.3 Shared Concepts

| Concept | M31's Role | Owning Module |
|---|---|---|
| Service order | Parent; M31 reports status back to it | M01 |
| Device / asset | Reads identity; writes component genealogy | M17 |
| Part | Requests, reserves and consumes | M15 |
| Test equipment | Uses and records which instrument was used | M45 |
| Quality checklist | Executes at defined gates | M23 |
| Technician competency | Enforced at bench assignment | M22 |
| Repair procedure | Consumes; contributes new procedures | M61 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA In-House Repair** | Repair object separate from the service order; repair procedure with steps; advance shipment of parts | The separation of repair object from service order; step-based repair procedure | SAP's full repair-procedure configuration depth |
| **Oracle Depot Repair** | Repair order, service bulletin, diagnostics workbench, repair estimate, WIP tracking | Repair order as the unit of work; WIP visibility as a first-class output | Oracle's separate repair-estimate object — ours lives in M36 |
| **PTC ServiceMax Depot Repair** | RMA-driven intake, triage, repair, test, ship; SLA and cost per repair | RMA-driven intake; cost-per-repair as a managed KPI | — |
| **IFS Repair Shop** | Shop floor, work centres, operations, serialised traceability | Work-centre/bench model and serialised component traceability | — |
| **QAD / Rootstock Field Service & Depot** | Reverse logistics into depot, refurbish, return to stock | Refurbishment sharing the same bench infrastructure as repair | — |
| **Industry depot-repair practice** | Dedicated QC station before shipping; organised parts staging; bench space for incoming, in-progress and outgoing units | Physical bench states modelled in software: incoming buffer, active bench, test/burn-in, awaiting release | — |
| **Odoo 19 `repair` + OCA `fieldservice_repair`** | Repair order, parts lines, repair stages | The base repair object as the L1/L2 foundation | Odoo's single-stage repair flow — insufficient for L3 board work |

**Design position.** Three deliberate differences from the benchmarks.

First, **repair level drives everything**. L1, L2 and L3 are not labels; they determine which
bench, which technician certification, which test protocol, which QC depth and which cost
rate applies. The benchmarks treat repair complexity as an attribute; here it is a routing
dimension.

Second, **burn-in is a first-class state**, not a note. A laptop motherboard that passes an
initial test but fails after four hours of thermal load is the single most common source of
rework in board-level repair. Modelling burn-in as a timed state with its own queue is how
the rework target of under 3% becomes achievable.

Third, **the workshop board is designed for a wall-mounted screen**, not a desktop. In a
Bangladeshi service centre workshop the supervisor manages the floor by looking up, not by
opening a laptop. If the software cannot replace the whiteboard on the wall, the whiteboard
will survive and the data will be wrong.

---

## 5. Functional Areas & Features

### 5.1 Repair Order & Intake

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-001 | Repair order creation | Create a repair order from a service order (M01), a refurbishment order (M14), an internal asset repair (M45), or a returned-from-field device | P1 | L5 |
| FR-WSR-002 | Multiple repair orders per service order | Support zero, one or many repair orders per service order, each independently tracked, when a device requires more than one workshop stage | P1 | L5 |
| FR-WSR-003 | Workshop routing | Route the repair order to the correct workshop based on repair level, device category, brand certification, equipment requirement and current load | P1 | L5 |
| FR-WSR-004 | Booking in | Record physical receipt at the workshop with condition verification against the intake record, discrepancy flagging and photographic evidence | P1 | L5 |
| FR-WSR-005 | Incoming buffer | Hold booked-in devices in a physical and logical incoming buffer with location tracking until a bench is allocated | P1 | L5 |
| FR-WSR-006 | Priority and sequencing | Sequence the workshop queue by SLA risk, customer tier, repair level and promised date, with supervisor override | P1 | L5 |
| FR-WSR-007 | RMA-in handling | Receive devices returned under an RMA with the RMA reference, expected fault and originating channel | P2 | L5 |
| FR-WSR-008 | Batch intake | Book in a batch of devices (corporate decommission, recall campaign, refurbishment lot) in one operation | P2 | L5 |

### 5.2 Bench & Capacity Management

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-009 | Workshop master | Define workshops with location, capability profile, operating hours, ESD zone classification and equipment inventory | P1 | L5 |
| FR-WSR-010 | Bench master | Define benches within a workshop with capability, equipment attached, and single-occupancy enforcement | P1 | L5 |
| FR-WSR-011 | Bench allocation | Allocate a repair order to a bench and a technician, enforcing skill, certification and equipment availability | P1 | L5 |
| FR-WSR-012 | Work-in-progress board | Present a live board showing every device by state, bench, technician, age and SLA risk, designed for wall-mounted display | P1 | L5 |
| FR-WSR-013 | Capacity view | Show available bench-hours by workshop, repair level and skill for the next seven days | P2 | L5 |
| FR-WSR-014 | Parallel work | Allow one technician to hold multiple devices across states (one on bench, two in burn-in) with explicit limits | P1 | L5 |
| FR-WSR-015 | Bench handover | Hand a device between technicians or shifts with a structured handover note and accountability transfer | P1 | L5 |
| FR-WSR-016 | Workshop transfer | Transfer a repair order to another workshop for a specialist stage, creating the logistics consignment automatically | P2 | L5 |
| FR-WSR-017 | Shift board | Show each shift's incoming, in-progress, at-risk and released counts at open and close | P2 | L5 |

### 5.3 Diagnosis & Repair Execution

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-018 | Bench diagnosis | Execute the diagnostic template from M01 at bench level, extended with component-level checks appropriate to the repair level | P1 | L5 |
| FR-WSR-019 | Teardown record | Record the disassembly sequence, components removed, and their condition, with photographic evidence at defined points | P2 | L5 |
| FR-WSR-020 | Repair level confirmation | Confirm or revise the repair level after physical inspection, triggering re-routing and re-estimation if it changes | P1 | L5 |
| FR-WSR-021 | Repair procedure execution | Present the applicable repair procedure from M61 as a step list, recording completion, measurements and deviations | P2 | L5 |
| FR-WSR-022 | Component-level part consumption | Consume parts at component level with serial or batch capture, recording exactly which component went into which board | P1 | L2 |
| FR-WSR-023 | Component harvesting | Record components harvested from a donor board, adding them to inventory with harvested classification and provenance | P2 | L5 |
| FR-WSR-024 | Consumables tracking | Record consumables used (solder, flux, thermal paste, adhesive, cleaning agents) against the repair for costing | P2 | L5 |
| FR-WSR-025 | Equipment usage | Record which test and repair equipment was used, capturing the instrument identity for calibration traceability | P1 | L5 |
| FR-WSR-026 | Labour time capture | Record start, pause, resume and stop per technician per repair order, distinguishing active work from waiting | P1 | L5 |
| FR-WSR-027 | Repair notes | Capture findings, technique used and cautions, in Bengali or English, with optional voice input | P2 | L5 |
| FR-WSR-028 | Knowledge promotion | Propose a repair note for promotion to the technical library when it resolves a fault not previously documented | P3 | L5 |
| FR-WSR-029 | Escalation to specialist | Escalate a repair to a higher-level technician or another workshop with the full context and reason | P1 | L5 |
| FR-WSR-030 | Beyond-economic-repair | Declare a device beyond economic repair with evidence, cost comparison and second-technician confirmation | P1 | L5 |

### 5.4 Test, Burn-In & Quality

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-031 | Test protocol library | Maintain test protocols by device category, repair level and fault type, defining required tests, pass criteria and duration | P1 | L5 |
| FR-WSR-032 | Functional test capture | Record functional test results against the protocol with measured values, not only pass/fail | P1 | L5 |
| FR-WSR-033 | Burn-in scheduling | Schedule burn-in with a defined duration and load profile, tracking the device through a timed state with automatic completion prompting | P1 | L5 |
| FR-WSR-034 | Burn-in station management | Manage burn-in station capacity as a constrained resource with its own queue | P2 | L5 |
| FR-WSR-035 | Post-burn-in verification | Require a verification test after burn-in before release is permitted | P1 | L5 |
| FR-WSR-036 | Quality gate | Prevent release without a passed quality checklist appropriate to device type and repair level | P1 | L2 |
| FR-WSR-037 | Independent QC | Require QC by a technician other than the repairer for L2 and L3 repairs and above the value threshold | P1 | L5 |
| FR-WSR-038 | In-workshop rework | Loop a failed device back to a bench with the failure reason recorded, counting internal rework separately from customer-returned rework | P1 | L5 |
| FR-WSR-039 | Test evidence | Attach test results, measurements and photographs to the repair order and the parent service order's evidence pack | P1 | L5 |
| FR-WSR-040 | Calibration enforcement | Warn when a repair uses an instrument whose calibration has lapsed, and flag the resulting QC record | P1 | L5 |

### 5.5 Release, Costing & Analytics

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-041 | Release to service order | Release the repaired device back to M01 with outcome, work summary, parts consumed and test results | P1 | L5 |
| FR-WSR-042 | Outgoing staging | Track released devices in an outgoing staging location until collected by the branch or logistics | P1 | L5 |
| FR-WSR-043 | Repair costing | Calculate the full cost of the repair: labour minutes at the applicable rate, components, consumables, equipment time and overhead absorption | P1 | L5 |
| FR-WSR-044 | Cost versus estimate | Compare actual repair cost to the estimate and flag variance beyond tolerance | P2 | L5 |
| FR-WSR-045 | Throughput analytics | Report devices released per bench per day, per workshop and per repair level | P1 | L5 |
| FR-WSR-046 | Cycle time analytics | Report cycle time by state — waiting, diagnosis, repair, burn-in, QC, awaiting release — to identify the bottleneck | P1 | L5 |
| FR-WSR-047 | Bench utilisation | Report bench occupancy against available hours | P2 | L5 |
| FR-WSR-048 | Failure pattern analytics | Report component failure patterns by device model to feed brand feedback and predictive models | P2 | L5 |
| FR-WSR-049 | Workshop dashboard | Present workshop performance to the supervisor and operations director | P1 | L5 |

### 5.6 Compliance & Safety at the Bench

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WSR-050 | ESD compliance record | Record ESD wrist-strap and mat verification at shift start for benches in ESD-controlled zones | P2 | L5 |
| FR-WSR-051 | Hazardous material handling | Record handling of batteries, refrigerant and chemicals per the safety procedure, linking to M59 | P2 | L5 |
| FR-WSR-052 | Environmental conditions | Record workshop temperature and humidity where the repair type requires it | P3 | L5 |
| FR-WSR-053 | Device security | Track physical security of devices held overnight, including high-value segregation | P2 | L5 |

*(FR-WSR-054 … FR-WSR-058 cover refurbishment-specific bench workflow, recall campaign
handling, loaner preparation, workshop stock replenishment and supervisor productivity tools;
full text in `05-01_Feature_and_Function_Register.md`.)*

> **Retired requirement identifiers.** 5 identifiers inside the original `FR-WSR-001 … 058` allocation were never issued to a requirement and are **retired, not reissued**, under register rule RG-02 (permanent identity):
>
> FR-WSR-054, 055, 056, 057, 058
>
> The measured requirement count for this module is **53**. Earlier statements of **58** were taken from the highest allocated identifier rather than a count of requirements (audit finding A3-01).

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Wall-display rendering** | The WIP board renders legibly at 1920×1080 from four metres, auto-refreshing without user interaction, degrading gracefully on connection loss |
| T-02 | **Single-occupancy invariant** | A bench cannot hold two active repair orders; enforced at the database level with a partial unique constraint |
| T-03 | **Timed state management** | Burn-in state transitions are driven by a scheduled evaluator, not a user action; overdue burn-in surfaces automatically |
| T-04 | **Serialised genealogy write** | Every component consumption writes an immutable genealogy record linking part serial → board → device → repair order |
| T-05 | **Concurrent bench updates** | Multiple technicians updating the board simultaneously produce consistent state through optimistic concurrency |
| T-06 | **Offline bench terminal** | A workshop terminal continues to operate for four hours without connectivity, queueing state changes |
| T-07 | **Barcode-first interaction** | Every bench operation is completable by scanning, without keyboard entry |
| T-08 | **Photographic evidence pipeline** | Bench photographs are captured, compressed, scanned and stored asynchronously without blocking the technician |
| T-09 | **Equipment identity capture** | Instrument selection is by scan or short-code, resolving to the M45 asset record |
| T-10 | **Cost calculation determinism** | Repair cost is recomputed deterministically from source records; it is never a stored figure that can drift |
| T-11 | **Event emission** | Repair order state changes emit events through the transactional outbox for M01 and M25 |
| T-12 | **Performance** | WIP board with 200 active repairs renders ≤ 1.5 s; bench scan operation ≤ 300 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M31 |
|---|---|---|
| **Workshop supervisor** | Manages the floor from a whiteboard; guesses at capacity; discovers overdue devices when a branch calls | Live board showing every device, bench, technician and SLA risk; capacity visible seven days out |
| **Bench technician** | Works from a paper job card; hunts for parts; records findings by hand at the end of the day | Scans the device to open the repair; sees the procedure, the history and the parts; records as they work |
| **Branch manager** | Cannot answer "where is my customer's laptop?" without phoning the workshop | Sees the workshop state on the same board as their own branch WIP |
| **Warranty officer** | Cannot prove what was tested when a brand rejects a claim | Test results, measurements, instrument identity and photographs attached to the claim automatically |
| **Inventory manager** | Sees parts leave stock but not what they went into | Component-level genealogy: which part, from which purchase order, into which board |
| **Operations director** | Has no measure of workshop productivity | Throughput per bench, cycle time by state, and the bottleneck named explicitly |
| **Quality manager** | Learns about repeat failures from customer complaints | Sees internal rework and failure patterns before the customer does |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Workshop throughput** | Bottleneck identification, queue sequencing, parallel work management, elimination of part-hunting time | **+40% devices per bench per day** — the single largest capacity gain available without hiring |
| **Rework reduction** | Burn-in as an enforced state; independent QC on L2/L3; internal rework counted and attributed | Contributes directly to the **< 3% rework** target. *The monetary value cannot be stated until the rework baseline is measured* — rework is currently unmeasured (`06-02` KPI-005). No figure is carried into the business case before Wave 2 baselining. |
| **Warranty claim defensibility** | Test evidence, instrument traceability and photographs assembled automatically | Protects the **BDT 100 lac/year** warranty recovery benefit against rejection |
| **Turnaround time** | Visible queue, sequenced by SLA risk rather than arrival order | Supports the **< 24 hour IT turnaround** target |
| **Parts accountability** | Component-level consumption closes the gap where parts leave stock untraceably | Contributes to the **BDT 34 lac/year** inventory benefit |
| **Refurbishment capacity** | The same bench infrastructure serves repair and refurbishment with shared measurement | Enables the **BDT 65 lac/year** refurbishment margin without a separate facility |
| **Reduced beyond-economic-repair losses** | Cost-versus-value comparison made explicit before work proceeds | Avoids spending BDT 8,000 of labour on a BDT 6,000 device |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Board-level expertise becomes visible** | The Company's L3 capability is a genuine competitive moat in Bangladesh; today it is undocumented and concentrated in a few people |
| **Technique capture** | A successful repair on an unfamiliar fault becomes a knowledge article rather than being forgotten |
| **Training pipeline evidence** | Junior technicians' progression from L1 to L2 is measurable, making promotion decisions defensible |
| **ISO 9001 clause 8.5.1 conformance** | Documented work instructions, controlled conditions and traceability at the point of production |
| **Calibration traceability** | The link between a measurement and the instrument that made it is what survives a brand audit |
| **Safety discipline** | ESD and hazardous-material handling recorded rather than assumed |

---

## 8. Lifecycle & State Model

```
                      ┌──────────────┐
                      │   CREATED    │  (repair order raised from M01/M14/M45)
                      └──────┬───────┘
                             │ physical receipt at workshop
                      ┌──────▼───────┐
                      │  BOOKED IN   │  condition verified, discrepancies flagged
                      └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │   QUEUED     │  incoming buffer, sequenced by SLA risk
                      └──────┬───────┘
                             │ bench + technician allocated (skill gate)
                      ┌──────▼───────┐
                 ┌───►│  ON BENCH    │◄────────────────┐
                 │    └──────┬───────┘                 │
                 │           │ diagnosis complete      │
                 │    ┌──────▼───────────┐             │
                 │    │  REPAIR LEVEL    │  confirm or revise
                 │    │  CONFIRMED       │  (revision may re-route)
                 │    └──────┬───────────┘             │
                 │           │                          │
                 │    ┌──────▼───────┐                 │
                 │    │ UNDER REPAIR │                 │
                 │    └──────┬───────┘                 │
                 │           │                          │
                 │    ┌──────▼───────┐  parts / specialist / customer decision
                 │    │  WAITING     │──────────────────┤
                 │    └──────────────┘                  │
                 │           │ repair complete           │
                 │    ┌──────▼───────┐                  │
                 │    │   TESTING    │                  │
                 │    └──────┬───────┘                  │
                 │           │ initial test passed       │
                 │    ┌──────▼───────┐                  │
                 │    │   BURN-IN    │  timed state, station capacity
                 │    └──────┬───────┘                  │
                 │           │ burn-in complete          │
                 │    ┌──────▼───────────┐              │
                 │    │ POST-BURN VERIFY │              │
                 │    └──────┬───────────┘              │
                 │           │ verified                  │
                 │    ┌──────▼───────┐                  │
                 │    │      QC      │─── fail ─────────┘  (internal rework, counted)
                 │    └──────┬───────┘
                 │           │ pass  ← hard gate
                 │    ┌──────▼───────┐
                 │    │   RELEASED   │  outcome reported to M01
                 │    └──────┬───────┘
                 │           │
                 │    ┌──────▼───────────┐
                 │    │ OUTGOING STAGING │  awaiting branch or logistics collection
                 │    └──────┬───────────┘
                 │           │ collected
                 │    ┌──────▼───────┐
                 └────┤    CLOSED    │
                      └──────────────┘

  Exceptions: TRANSFERRED (to another workshop) · UNREPAIRABLE · CANCELLED
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Created | Booked In | Physical receipt scanned; condition verified against intake record | Workshop clerk |
| Booked In | Queued | Location assigned in the incoming buffer | Workshop clerk |
| Queued | On Bench | Bench free; technician holds the required certification for the repair level and brand (BRU-WSR-02) | Supervisor |
| On Bench | Repair Level Confirmed | Bench diagnosis recorded | Technician |
| Repair Level Confirmed | Under Repair | Required parts available or reserved; re-estimation complete if level changed | Technician |
| Under Repair | Waiting | Approved waiting reason selected | Technician |
| Under Repair | Testing | Repair work recorded complete; parts and time posted | Technician |
| Testing | Burn-In | Initial functional test passed; burn-in station available | Technician |
| Burn-In | Post-Burn Verify | Configured burn-in duration elapsed | System |
| Post-Burn Verify | QC | Verification test passed | Technician |
| QC | Released | **Quality checklist passed**; independent QC where required (BRU-WSR-04) | QC inspector |
| QC | On Bench | QC failed — internal rework, reason recorded and counted | QC inspector |
| Released | Outgoing Staging | Outcome reported to M01; staging location assigned | System |
| Any | Transferred | Receiving workshop confirmed; logistics consignment created | Supervisor |
| Any | Unrepairable | Evidence, cost comparison and second confirmation recorded (BRU-WSR-05) | Supervisor |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-WSR-01 | A repair order cannot be created without a parent service order, refurbishment order or internal asset request | **H** | Ops Director |
| BRU-WSR-02 | A device cannot be allocated to a technician who lacks the certification required for its repair level and brand | **H** | Quality Manager |
| BRU-WSR-03 | Level 3 board-level repair may only be performed at a workshop with the required equipment and ESD classification | **H** | Ops Director |
| BRU-WSR-04 | A repair order cannot be released without a passed quality checklist; L2 and L3 repairs require independent QC | **H** | Quality Manager |
| BRU-WSR-05 | Beyond-economic-repair requires photographic evidence, a documented cost comparison and a second technician's confirmation | **H** | Ops Director |
| BRU-WSR-06 | A bench holds exactly one active repair order at a time | **H** | Workshop Supervisor |
| BRU-WSR-07 | Burn-in cannot be shortened below the protocol duration; extension is permitted, reduction is not | **H** | Quality Manager |
| BRU-WSR-08 | Brand-supplied warranty parts cannot be consumed on a non-warranty repair | **H** | Inventory Manager |
| BRU-WSR-09 | A repair performed with an out-of-calibration instrument is flagged, and the QC record is marked for review | **A** | Quality Manager |
| BRU-WSR-10 | Internal rework is recorded and counted separately from customer-returned rework, and is never hidden | **H** | Quality Manager |
| BRU-WSR-11 | A repair level revision that increases cost beyond the approved estimate requires re-approval before work continues | **H** | Ops Director |
| BRU-WSR-12 | Harvested components carry provenance and cannot be used on warranty repairs | **H** | Inventory Manager |
| BRU-WSR-13 | High-value devices held overnight must be recorded into secure storage at shift close | **H** | Workshop Supervisor |
| BRU-WSR-14 | A workshop transfer requires the receiving workshop's confirmation and a logistics consignment | **H** | Logistics Manager |

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.repair.order` | `fix_repair_order` | The unit of workshop work | name, service_order_id, asset_id, workshop_id, bench_id, technician_id, repair_level, state, received_at, released_at, total_labour_min, total_cost |
| `fix.workshop` | `fix_workshop` | Workshop master | code, branch_id, capability_json, esd_zone, operating_hours, active |
| `fix.workshop.bench` | `fix_workshop_bench` | Bench master | workshop_id, code, capability, equipment_ids, current_repair_order_id |
| `fix.repair.stage.log` | `fix_repair_stage_log` | Time in each state | repair_order_id, state, entered_at, exited_at, duration_min, actor |
| `fix.teardown.record` | `fix_teardown_record` | Disassembly detail | repair_order_id, sequence, component, condition, evidence_id |
| `fix.component.consumption` | `fix_component_consumption` | Component-level parts use | repair_order_id, part_id, serial, quantity, position, source_class |
| `fix.consumable.usage` | `fix_consumable_usage` | Consumables for costing | repair_order_id, consumable_id, quantity |
| `fix.equipment.usage` | `fix_equipment_usage` | Instrument traceability | repair_order_id, equipment_id, used_from, used_to, calibration_valid |
| `fix.test.protocol` | `fix_test_protocol` | Test definition | device_category, repair_level, fault_type, tests_json, burnin_minutes, pass_criteria |
| `fix.test.result` | `fix_test_result` | Recorded test outcome | repair_order_id, protocol_id, test_code, measured_value, unit, passed, equipment_id |
| `fix.burnin.session` | `fix_burnin_session` | Burn-in tracking | repair_order_id, station_id, started_at, required_minutes, completed_at, outcome |
| `fix.burnin.station` | `fix_burnin_station` | Constrained resource | workshop_id, code, capacity, current_sessions |
| `fix.workshop.rework` | `fix_workshop_rework` | Internal rework record | repair_order_id, failed_at_state, reason, attributed_to, iteration |
| `fix.repair.cost.line` | `fix_repair_cost_line` | Cost build-up | repair_order_id, cost_type, quantity, rate, amount |
| `fix.bench.handover` | `fix_bench_handover` | Shift and technician handover | repair_order_id, from_technician, to_technician, note, occurred_at |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order` | M01 | Parent; read and status write-back |
| `fix.asset` | M17 / M49 | Read identity; write component genealogy |
| `fix.part.item`, `fix.stock.reservation` | M15 / M37 | Reserve and consume |
| `fix.tool.register` (test equipment) | M45 | Read identity and calibration status |
| `fix.checklist.template` | M23 | Read template; write result |
| `fix.competency.assessment` | M22 | Read for bench allocation gate |
| `fix.knowledge.article` | M61 | Read procedures; propose new |
| `fix.consignment` | M03 | Create for workshop transfer |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-WSR-01 | Service order routed to workshop | Create the repair order, select the workshop by capability and load, notify the supervisor | Queue for manual routing |
| AUT-WSR-02 | Device booked in | Verify condition against the intake record; flag discrepancies to the originating branch | Manual verification task |
| AUT-WSR-03 | Bench becomes free | Propose the next repair order from the queue by SLA risk and skill match | Supervisor selects manually |
| AUT-WSR-04 | Repair level revised upward | Recalculate cost, compare to the approved estimate, and request re-approval if exceeded | Hold and escalate to supervisor |
| AUT-WSR-05 | Parts unavailable at bench | Raise a parts request to M15, move the order to Waiting, notify M01 with a revised ETA | Escalate to inventory manager |
| AUT-WSR-06 | Initial test passed | Reserve a burn-in station, start the timed session, set the completion prompt | Queue for the next available station |
| AUT-WSR-07 | Burn-in duration elapsed | Prompt the technician for post-burn verification; escalate if not actioned within the threshold | Repeat prompt, then escalate |
| AUT-WSR-08 | QC failed | Return to bench, record the failure reason, increment the internal rework counter, emit a quality event | — |
| AUT-WSR-09 | Repair order released | Report the outcome, work summary, parts and test results to M01; assign an outgoing staging location | Manual release task |
| AUT-WSR-10 | Device in outgoing staging beyond threshold | Alert the originating branch and logistics | Escalate to supervisor |
| AUT-WSR-11 | Instrument calibration lapsed | Mark the instrument out of service, flag any QC record created with it | Immediate supervisor alert |
| AUT-WSR-12 | Shift close | Prompt secure storage recording for high-value devices; produce the shift board summary | Block shift close until completed |

---

## 12. Interfaces

### 12.1 Upstream — M31 Consumes

| Source | What | Mechanism |
|---|---|---|
| M01 Service Order | Routing instruction, diagnosis to date, approved scope, promise date | Command + event `service_order.routed_to_workshop` |
| M14 Refurbishment | Refurbishment work order requiring bench execution | Command |
| M45 Enterprise Assets | Test equipment identity and calibration status | REST |
| M15 Inventory | Part availability, reservation confirmation | REST + event |
| M22 Competency | Technician certification validity for the bench gate | REST |
| M23 Quality | Checklist templates and test protocols | Master data projection |
| M61 Knowledge | Repair procedures and technical bulletins | REST |
| M37 Catalogue | Standard repair times and component structures | Master data projection |

### 12.2 Downstream — M31 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Repair status, outcome, work summary, test evidence | Event `repair_order.*` |
| M15 Inventory | Component consumption and harvested components | Command |
| M17 Asset Registry | Component genealogy and condition update | Event |
| M09 Warranty | Technical evidence pack for claim substantiation | Event payload |
| M23 Quality | Internal rework, QC failures, calibration exceptions | Events |
| M03 Logistics | Workshop transfer consignment requests | Command |
| M25 Business Intelligence | Throughput, cycle time, utilisation, cost facts | Warehouse extract |
| M26 AI/ML | Repair duration and component failure training data | Warehouse extract |
| M61 Knowledge | Proposed new repair procedures | Command |
| M53 Costing | Repair cost lines for margin analysis | Event |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `repair_order.created` | repair order, service order, workshop, repair level | M01, M25 |
| `repair_order.booked_in` | repair order, condition verification, discrepancies | M01, M03 |
| `repair_order.bench_allocated` | repair order, bench, technician | M01, M25 |
| `repair_order.level_revised` | repair order, old level, new level, cost impact | M01, M36 |
| `repair_order.waiting` | repair order, reason, expected release | M01, M15 |
| `repair_order.burnin_started` | repair order, station, required duration | M25 |
| `repair_order.qc_failed` | repair order, failure reason, iteration | M23, M01 |
| `repair_order.released` | repair order, outcome, parts, test results, cost | M01, M09, M53 |
| `component.consumed` | part serial, board, device, repair order | M15, M17 |
| `component.harvested` | source device, component, provenance | M15, M14 |
| `equipment.calibration_exception` | equipment, repair order, QC record | M45, M23 |
| `billing.event` | customer, repair order, labour and parts lines, unit price (M11), dimensions, currency, tax context, idempotency key | M20, M53 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/repair-orders` | POST | Create a repair order | M01, M14, P03 |
| `/api/v1/repair-orders/{id}` | GET | Full repair detail | P03 |
| `/api/v1/repair-orders/{id}/transition` | POST | State transition with guard evaluation | P03, bench terminal |
| `/api/v1/repair-orders/{id}/components` | POST | Record component consumption | P03, bench terminal |
| `/api/v1/repair-orders/{id}/tests` | POST | Record test results | P03, bench terminal |
| `/api/v1/repair-orders/{id}/release` | POST | Release to the parent service order | P03 |
| `/api/v1/workshops/{id}/board` | GET | WIP board data for wall display | P03 |
| `/api/v1/workshops/{id}/capacity` | GET | Available bench-hours forecast | P03 |
| `/api/v1/benches/{id}/allocate` | POST | Allocate a repair order to a bench | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R05 Operations Director | C R U D A | All workshops |
| R09 Workshop Supervisor | C R U D A | Own workshop |
| R12 Specialist Technician (L3) | R U | Own assigned repair orders; all repair levels |
| R10 Senior Technician (L2) | R U | Own assigned repair orders; L1 and L2 only |
| R11 Junior Technician (L1) | R U | Own assigned repair orders; L1 only |
| R06 Branch Manager | R | Repair orders originating from own branch |
| R08 Service Centre Agent | R | Repair orders originating from own branch |
| R32 Quality Manager / ISO Coordinator | R U | All — QC records and rework |
| R17 Inventory Manager | R | Component consumption |
| R28 Warranty Claims Officer | R | Test evidence for claims |
| R15 Logistics Coordinator | R | Outgoing staging and transfers |

**Field-level restrictions:** repair cost and margin are visible to R05, R06, R09, R26 and
R27 only. Technicians see labour minutes but not monetary cost rates.

**Segregation of duties:** the repairing technician cannot record the independent QC for
L2 and L3 repairs (SOD-07).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Workshop WIP board (wall display) | Workshop floor | Real time | Every device by state, bench, technician, age, SLA risk |
| Bench throughput | Workshop supervisor, Ops Director | Daily | Devices released per bench per day versus target |
| Cycle time by state | Ops Director | Weekly | Time in queue, diagnosis, repair, waiting, burn-in, QC, staging — bottleneck named |
| Internal rework analysis | Quality Manager | Weekly | Rework by technician, repair level, device model, failure reason |
| Repair cost versus estimate | Finance, Ops Director | Weekly | Variance by repair level and device category |
| Component failure pattern | Quality, Brand partners | Monthly | Which component fails on which model, with volumes |
| Bench utilisation | Workshop supervisor | Weekly | Occupancy against available hours |
| Burn-in station utilisation | Workshop supervisor | Weekly | Station capacity constraint analysis |
| Calibration exception report | Quality Manager | Weekly | Repairs performed with lapsed instruments |
| Beyond-economic-repair report | Ops Director | Monthly | Volume, value and pattern of unrepairable determinations |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| — | Devices released per bench per day | unmeasured | baseline +20% | **baseline +40%** |
| — | Workshop cycle time (booked-in to released) | unmeasured | < 48 h | **< 30 h** |
| — | Bench utilisation | unmeasured | 68% | **78%** |
| — | Internal rework rate (QC failures) | unmeasured | < 8% | **< 5%** |
| KPI-004 | First-time fix rate (workshop contribution) | 70% | 82% | **88%** |
| KPI-007 | QC first-pass rate | unmeasured | 92% | **95%** |
| — | Burn-in completed per protocol without shortcut | n/a | **100%** | **100%** |
| — | Component genealogy completeness | 0% | 95% | **99%** |
| — | Calibration exceptions | untracked | < 5 per month | **0** |
| — | Repair cost variance versus estimate | unmeasured | within 15% | **within 8%** |
| — | Devices in outgoing staging > 24 h | unmeasured | < 5% | **< 2%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `repair`, `stock`, `product` | 14% |
| L2 | OCA `fieldservice_repair`, `fieldservice_quality_control`, `quality_control_oca`, `stock_barcodes` | 26% |
| L5 | `cd_workshop`, `cd_bench`, `cd_repair_order`, `cd_test_burnin` | 60% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-007 | `cd_repair_order` — repair order object, state machine, costing | Odoo module | 10 PW |
| CD-008 | `cd_workshop` + `cd_bench` — workshop and bench master, allocation, capacity | Odoo module | 7 PW |
| CD-009 | `cd_test_burnin` — test protocols, burn-in scheduling, station management | Odoo module | 6 PW |
| CD-010 | WIP board — wall-display web application with auto-refresh | Frontend | 4 PW |
| CD-011 | Bench terminal — barcode-first, offline-capable operator interface | Frontend | 3 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M31 is scheduled in **W2** (P1) but declares a dependency on 3 module(s) that land later: **M22** (W5); **M23** (W5); **M45** (W5). One of three things must be true before the W2 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W2 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M31 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W2 plan for M31 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M01 Service Order | The repair order has no meaning without its parent |
| M17 Asset Registry | Component genealogy needs a device identity |
| M15 Inventory | Component consumption requires stock |
| M22 Competency | The bench allocation gate depends on certification data |
| M23 Quality | Checklist templates must exist |
| M45 Test Equipment | Instrument traceability requires the equipment register — may be stubbed in W2 and completed in W5 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Workshop whiteboards and paper job cards | Current WIP only, ~500 devices | `fix.repair.order` | W2 cutover |
| Historical repair records | Not migrated — held in the M01 service order archive | — | — |

There is no meaningful historical workshop dataset. M31 starts with current work in progress
only, captured during a single cutover count.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Repair orders flow correctly from service orders, refurbishment orders and internal requests | Three scripted end-to-end demonstrations |
| AC-02 | The WIP board replaces the physical whiteboard in all pilot workshops | Whiteboards removed; supervisor confirmation |
| AC-03 | A technician cannot be allocated a repair level for which they are not certified, including via API | Negative test through UI and API |
| AC-04 | A repair order cannot be released without a passed QC; L2/L3 require independent QC | Negative test |
| AC-05 | Burn-in cannot be shortened below the protocol duration | Negative test |
| AC-06 | Component consumption produces a complete genealogy record traceable from part serial to device | Trace test on ten repairs |
| AC-07 | Instrument identity is captured on every test and links to calibration status | Sample audit of 50 test records |
| AC-08 | Cycle time by state is reported and the bottleneck is identifiable | Report demonstration with real data |
| AC-09 | The bench terminal operates for four hours offline and synchronises with full integrity | Offline test |
| AC-10 | The WIP board is legible at four metres on a 1920×1080 wall display | Physical verification in a workshop |
| AC-11 | All bench interfaces are complete in Bengali | Translation coverage report |
| AC-12 | WIP board with 200 active repairs renders in ≤ 1.5 s | Load test |
| AC-13 | Internal rework is counted and attributed separately from customer-returned rework | Report demonstration |
| AC-14 | Workshop supervisors sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | How many workshops exist today, and which have L3 board-level capability and ESD control? | Ops Director | W2 design |
| Q-02 | What are the standard burn-in durations by device category? Are these currently defined anywhere? | Quality Manager | W2 build |
| Q-03 | Should the labour rate at the bench differ by repair level for internal costing? | CFO / Ops Director | W2 build |
| Q-04 | Is there an existing test equipment register, or does M45 start from zero? | Quality Manager | W2 planning |
| Q-05 | What is the policy on using harvested components — disclosed to the customer, or prohibited on paid repairs? | CCO / Quality | W2 build |
| Q-06 | Does the Company intend to offer depot repair to third parties (other service providers) as a revenue line? | CCO | W6 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3 (M01/M31 boundary) · `M01_Service_Request_and_Order_Management.md` ·
`02_Architecture/02-03_Module_Boundary_and_Overlap_Rules.md` *(planned — boundaries currently declared in each module's §3 and each `_CATEGORY_OVERVIEW.md`)* ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Motherboard Repair, §Laptop Repair (Level 1/2),
§Server Repair · `ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md`
BR-SRM-018, §6.2 Process 3 · `1000fix_business/Business planning for 1000 fix.docx`
§Refurbishment and Resale

**External benchmark**
SAP S/4HANA *In-House Repair* · Oracle *Depot Repair Workbench* · PTC ServiceMax
*Depot Repair* · IFS *Repair Shop* · QAD / Rootstock depot repair and reverse logistics ·
industry depot-repair operating practice (bench staging, dedicated QC station, parts
staging, turnaround tracking) · Odoo 19 `repair` and OCA `fieldservice_repair`

---

*Module M31 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
