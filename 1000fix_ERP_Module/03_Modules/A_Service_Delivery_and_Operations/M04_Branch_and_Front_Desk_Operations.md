---
id: FIX-ERP2-M04
module_id: M04
module_code: FRD
module_name: Branch & Front-Desk Operations
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.1
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Branch Operations Lead
system_owner: Service Squad
priority: P1
wave: W1
audit_ref: Revision 1.1 applies audit findings C-03 (identifier collision), C-04 (regulatory), M-04 (KPI identifiers)
---

# M04 — Branch & Front-Desk Operations
### Category A · Code `FRD` · Existing module, promoted from a sub-feature in v2.0

> **Revision 1.1 — audit finding C-03.** This module was briefly drafted with the code `BFO`
> and identifiers `FR-BFO-*`. That conflicted with the permanent allocation `FR-FRD-001…031`
> held in `05-01`. The code `FRD` and the `FR-FRD-*` identifiers are restored. `BFO` is
> retired and will never be reissued. One requirement — *intent capture at check-in* — was an
> addition beyond the original 31 and now carries the newly allocated `FR-FRD-032`.

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M04 |
| **Module code** | `FRD` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (promoted from a v1.0 sub-feature; retained in v2.1) |
| **Priority** | **P1** |
| **Delivery wave** | W1 (Months 1–4) — one of the first modules live |
| **Business owner** | Branch Operations Lead |
| **System owner** | Service Squad |
| **Delivery layers** | L5 (custom) with L1 point-of-sale and cash primitives |
| **Custom modules** | `cd_queue`, `cd_cash_drawer`, `cd_branch_ops` |
| **Requirement range** | FR-FRD-001 … FR-FRD-031 |
| **Requirement count** | **31** *(measured 2026-08-13; 1 allocated identifier retired unused — see below)* |
| **Effort estimate** | 13 person-weeks |
| **Depends on** | M01 Service Order · M33 Party Master · M17 Asset Registry · M29 Identity · M30 Platform Admin |
| **Depended on by** | M01, M20, M50, M15, M31, M03, M25 |

---

## 2. Purpose

M04 runs **the counter**. It is the software that 150–250 service centre agents and 51+ branch
managers touch more often than any other, and the first thing a walk-in customer experiences
of 1000FiX's digital transformation.

Its design constraint is unusually specific and unusually strict: **a walk-in intake must be
completed in under three minutes**. Today the paper process takes around ten. If the software
takes longer than the paper it replaces, branch staff will keep the paper, the data will be
wrong, and every module downstream will inherit that error.

### Why It Exists

Walk-in is the highest-volume service delivery mode in the business. Every one of those
interactions involves a queue, an intake, a storage location, a handover and, in most cases,
a cash transaction — across 51+ locations with 500+ staff and no consistent process.

The v1.0 plan treated the counter as a feature of the service order module. That is a
category error: the counter has its own rhythm, its own physical constraints, its own cash
controls and its own daily discipline of opening and closing. Grouping it inside the service
order module would have made the service order module unusable at the counter, which is where
it is used most.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD BR-SRM-001 | Walk-in terminal as a required service order intake channel |
| ERP BRD FSM-030 / CD-17 | Walk-in queue management with token system and estimated wait display |
| ERP BRD §6.2 Process 1 | Current state: agent writes on paper or into a spreadsheet, no acknowledgement, inconsistent tracking numbers |
| ERP URD Persona 1 | Service Centre Agent — "complete service intake in under 3 minutes per customer", "find any customer's full history in ≤ 2 clicks" |
| ERP BRD BRU-FIN-02 | Cash payments above BDT 50,000 must record the customer's NID |
| **Personal Data Protection Act 2026** | NID is **Sensitive Personally Identifiable Data**. Its capture at the counter now carries consent, transparency-notice, residency and retention obligations. *(Audit finding C-04b.)* |
| Company Profile §Service Infrastructure | 51+ service centres; 1000FiX Station network expansion |
| Business Plan §Priority Service Contract | Priority customers require expedited counter handling |
| Service App SOW §Customer categorisation | Different customer classes require different counter treatment |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Token issuance, queue management and waiting-area display |
| 2 | Priority queueing by customer tier, appointment and accessibility need |
| 3 | Counter workstation: fast intake, customer lookup, device recall |
| 4 | Device storage location assignment and retrieval |
| 5 | Collection and handover with identity verification |
| 6 | Counter sales of parts, accessories, memberships and plans |
| 7 | Cash drawer operation: float, receipts, refunds, petty expense |
| 8 | Payment capture at the counter across all methods |
| 9 | Shift open, close, count and variance handling |
| 10 | Banking deposit recording |
| 11 | Branch daily operations: opening and closing checklists, handover notes |
| 12 | Branch operations dashboard |
| 13 | Uncollected device management |
| 14 | Self-service kiosk and receipt/label printing |
| 15 | Counter performance analytics |
| 16 | **Presentation of the PDPA transparency notice at the point of personal data capture** |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Service order object, lifecycle, SLA | **M01** | M04 is a channel into M01, not a parallel record |
| Customer master identity and addresses | **M33** | One party master |
| Consent record and transparency notice content | **M33** | M04 presents the notice; M33 owns and versions it |
| Device identity and history | **M17** | Devices outlive counters |
| Repair execution | **M31** | The counter hands over to the workshop |
| Pricing and estimate calculation | **M11** / **M36** | Commercial decisions |
| Invoice creation and posting | **M20** | Only Category G creates financial documents |
| Bank reconciliation and treasury position | **M50** | M04 records movements; M50 reconciles them |
| Retail stock levels and replenishment | **M15** | M04 sells from stock; M15 owns it |
| Branch premises, lease, utilities, maintenance | **M47** | Facilities are enterprise assets |
| Branch as an organisational unit (code, zone, cost centre) | **M30** | Configuration, not operation |
| Staff rosters and attendance | **M55** | Workforce planning is Category H |
| E-commerce checkout | **M38** | Different channel, different rules |

### 3.3 Shared Concepts

| Concept | M04's Role | Owning Module |
|---|---|---|
| Service order | Creates and hands over; never owns state logic | M01 |
| Customer | Looks up and creates inline | M33 |
| Consent and transparency notice | Presents and records the acknowledgement | M33 |
| Device | Identifies and registers inline | M17 |
| Payment | Captures at the counter | M20 / M50 |
| Cash position | Records branch movements | M50 |
| Storage location | Owns for devices in branch custody | M04 |
| Queue token | Owns | M04 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Enterprise queue management systems** | Virtual queueing, kiosk and QR check-in, intent capture at check-in, routing to the right staff by need and real-time availability, SMS and WhatsApp notification when the token is called | Intent capture at token issue so the counter is prepared before the customer arrives; notification so customers can wait comfortably elsewhere | Full appointment-orchestration suites — excessive for a repair counter |
| **Retail POS with multi-store operations** | Shift open and close, cash drawer, float, variance, multi-store consolidation | The complete shift discipline model | Full retail merchandising |
| **Bank branch operations** | Counter workstation with customer 360 on screen pop, tiered service, cash controls, dual control on variance | Screen-pop pattern; dual control on variance above threshold | Teller-specific transaction types |
| **Dynamics 365 Commerce / Odoo POS** | Counter sale, payment methods, receipt printing, session management | Session model and payment capture as the L1 substrate | Full retail catalogue and promotions engine |
| **Authorised service centre practice (South Asia)** | Job card issued at the counter, gate pass on device release, token queue | Job sheet and gate-pass discipline familiar to Bangladeshi customers and staff | Single-brand assumptions |

**Design position.** Four deliberate differences.

First, **three minutes is a hard constraint, not a target**. Every screen, field and default
in the counter workstation is designed against it. Any feature that cannot be shown to fit
inside three minutes is moved out of the intake path and into a follow-up action.

Second, **search-first, not form-first**. The agent begins by searching — phone number,
serial, name — and the system fills what it can. A blank form is a design failure.

Third, **the queue display is a customer-experience surface, not an internal tool**. Retail
research finds the average customer abandons a queue after roughly eight minutes, and that a
large majority of shoppers regard fast-moving queues as essential. The display and the wait
estimate exist to manage perception as much as flow.

Fourth, **cash discipline is enforced by the system, not by policy**. An unclosed shift blocks
the next shift's opening. This is the single most effective control available against branch
cash leakage, and it costs nothing to implement.

---

## 5. Functional Areas & Features

### 5.1 Queue Management

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FRD-001 | Token issuance | Issue a queue token by service category from a kiosk, a counter, or the customer's own phone via QR | P1 | L5 |
| FR-FRD-002 | Queue display | Drive a waiting-area display showing tokens now serving, by counter, in Bengali and English, with audible announcement | P1 | L5 |
| FR-FRD-003 | Wait-time estimation | Estimate and display the expected wait based on live throughput and queue depth | P2 | L5 |
| FR-FRD-004 | Priority queueing | Give Privilege Gold and Diamond members, corporate account holders, elderly and disabled customers priority placement per policy | P1 | L5 |
| FR-FRD-005 | Appointment check-in | Check in a pre-booked appointment and merge it into the queue at the reserved time | P1 | L5 |
| FR-FRD-006 | Recall and no-show | Recall a skipped token once, then mark it as a no-show and release the position | P2 | L5 |
| FR-FRD-007 | Counter routing | Route tokens to counters by capability — intake, collection, payment, corporate, technical | P2 | L5 |
| FR-FRD-025 | Self-service kiosk | Provide a kiosk for token issue, status check and appointment check-in without staff involvement | P2 | L5 |
| **FR-FRD-032** | **Intent capture at check-in** | Capture the reason for the visit at token issue so the counter is prepared before the customer sits down *(newly allocated — audit C-03)* | P2 | L5 |

### 5.2 Counter Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FRD-008 | Fast intake | Complete a walk-in intake in under three minutes using search-first customer lookup, device recall and defaulted fields | **P1** | L5 |
| FR-FRD-009 | Counter dashboard | Show the agent everything about the customer in front of them: open orders, devices, contracts, entitlements, dues, tier, recent conversations | P1 | L5 |
| FR-FRD-010 | Collection and handover | Verify identity, retrieve the device from its recorded storage location, confirm accessories, capture signature and issue the gate pass | P1 | L5 |
| FR-FRD-011 | Storage location tracking | Record and retrieve the physical shelf or bin holding each device in branch custody | P1 | L5 |
| FR-FRD-012 | Counter sales | Sell parts, accessories, Privilege memberships, warranty extensions and AMC contracts at the counter | P1 | L1 |
| FR-FRD-013 | Quotation printing | Print or send an estimate from the counter | P1 | L2 |
| FR-FRD-026 | Receipt and label printing | Print receipts, job sheets, device labels, gate passes and token slips on thermal and A4 printers | P1 | L5 |
| FR-FRD-029 | Customer feedback at counter | Capture a quick satisfaction rating at handover on a customer-facing display or tablet | P2 | L5 |

### 5.3 Cash & Payment Control

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FRD-014 | Shift open and close | Open a shift with a counted opening float and close it with a counted balance | P1 | L5 |
| FR-FRD-015 | Cash drawer | Record every cash movement — receipts, refunds, petty expense, transfers, banking | P1 | L5 |
| FR-FRD-016 | Payment capture | Take cash, card, bKash, Nagad and bank transfer at the counter with instant receipt | P1 | L5 |
| FR-FRD-017 | Variance handling | Record any cash variance at close and require approval above the tolerance | P1 | L5 |
| FR-FRD-018 | Banking deposit | Record deposits to bank with slip reference for reconciliation in M50 | P1 | L5 |
| FR-FRD-019 | High-value cash control | Require NID capture for cash receipts above the statutory threshold, **presenting the PDPA transparency notice and recording the consent before capture** | **P0** | L5 |
| FR-FRD-030 | Petty cash | Manage the branch petty cash float with expense capture and replenishment | P2 | L5 |

### 5.4 Branch Daily Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-FRD-020 | Opening checklist | Enforce a daily opening checklist covering safety, equipment, stock, cash and staffing | P2 | L5 |
| FR-FRD-021 | Branch dashboard | Show today's intake, work in progress, ready for collection, overdue, revenue and queue health | P1 | L5 |
| FR-FRD-022 | Shift handover notes | Record structured handover notes between shifts, visible to the incoming team | P2 | L5 |
| FR-FRD-023 | Uncollected device report | List devices Ready but uncollected, by age, with reminder actions and escalation | P1 | L5 |
| FR-FRD-024 | Closing checklist | Enforce closing: cash counted, devices secured, orders updated, alarms set | P2 | L5 |
| FR-FRD-027 | Multi-counter configuration | Configure counters per branch with capability and staffing assignment | P2 | L5 |
| FR-FRD-028 | Counter performance analytics | Report throughput, handling time, queue metrics and satisfaction per counter and per agent | P2 | L5 |
| FR-FRD-031 | Branch announcements | Publish branch-level announcements, targets and notices to counter staff | P3 | L5 |

> **Retired requirement identifiers.** 1 identifier inside the original `FR-FRD-001 … 032` allocation were never issued to a requirement and are **retired, not reissued**, under register rule RG-02 (permanent identity):
>
> FR-FRD-032
>
> The measured requirement count for this module is **31**. Earlier statements of **32** were taken from the highest allocated identifier rather than a count of requirements (audit finding A3-01).

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Sub-three-minute intake path** | The intake transaction is a single-screen flow with no page reloads; every server call on the path is ≤ 300 ms |
| T-02 | **Keyboard-first operation** | Every counter action is completable without a mouse; tab order is deliberate; barcode scan is the primary input |
| T-03 | **Low-spec hardware target** | Renders and performs at 1366×768 on typical branch hardware |
| T-04 | **Offline-tolerant counter** | The counter continues to issue tokens, look up cached customers and record intake for two hours without connectivity, queueing for sync |
| T-05 | **Queue display resilience** | The waiting-area display holds its last known state on connection loss and reconnects without intervention |
| T-06 | **Cash session integrity** | Shift and drawer records are append-only; a correction is a compensating movement with a reason |
| T-07 | **Peripheral integration** | Thermal receipt printers, label printers, barcode scanners, signature pads, cash drawers and customer displays operate through a standard local agent |
| T-08 | **Idempotent payment capture** | A payment recorded twice through a retry produces one record |
| T-09 | **Storage location integrity** | A device cannot be recorded into two locations; retrieval marks the location free |
| T-10 | **Shift-close blocking** | An unclosed shift blocks the next shift's opening at the database level, not merely in the UI |
| T-11 | **Bengali typography at speed** | Bengali rendering verified at counter font sizes; input supports phonetic typing without lag |
| **T-12** | **Residency-aware NID capture** | The NID field is written to the **Bangladesh-resident store** under NFR-086; the counter never holds it in a regional cache, a local offline queue, or a printed artefact beyond the statutory receipt |
| T-13 | **Performance envelope** | Customer lookup ≤ 400 ms; counter dashboard ≤ 1.5 s; token issue ≤ 200 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M04 |
|---|---|---|
| **Service centre agent** | Writes on paper; hunts for the customer's history; cannot check warranty; ten-minute intake | Search, confirm, capture, print — under three minutes with full context on screen |
| **Walk-in customer** | Stands in an undefined line; no idea how long; explains their history from memory | Takes a token, is told the wait, is called by name, and the agent already knows their device |
| **Branch manager** | Discovers the day's position at the end of the day | Live board of intake, WIP, ready, overdue, revenue and queue health |
| **Cashier** | Counts cash and hopes it matches | System-tracked drawer with every movement recorded and variance surfaced immediately |
| **Finance officer** | Reconciles 51 branches from 51 different formats | One consolidated cash position, reconciled daily |
| **Customer collecting a device** | Waits while staff search the storeroom | Device located by shelf reference in seconds; gate pass printed |
| **Operations director** | Cannot compare branch performance | Throughput, wait time, handling time and satisfaction comparable across all 51+ branches |
| **Compliance officer** | Cannot evidence how NID data is collected or on what lawful basis | Consent and transparency notice recorded at the point of capture, per PDPA 2026 |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Intake capacity** | 10 minutes to 3 minutes per walk-in releases roughly **7 minutes per customer** across the highest-volume delivery mode | At 250,000 monthly interactions, a material fraction walk-in, this is the equivalent of tens of staff-hours per branch per month |
| **Cash leakage control** | Shift discipline, recorded movements, enforced variance approval, blocked shift rollover | Target **< 1 variance incident per branch per month**; the control pays for the module |
| **Customer abandonment reduction** | Wait visibility and notification address the eight-minute abandonment threshold | Retained walk-ins that would otherwise leave |
| **Device retrieval time** | Storage location tracking | **> 98% located within 60 seconds**, removing the most visible source of counter embarrassment |
| **Uncollected device recovery** | Systematic ageing, reminders and escalation | Reduces devices uncollected beyond 30 days to **< 0.5%**, freeing storage and recovering revenue |
| **Counter sales uplift** | Membership, warranty extension and accessory sales offered at the point of contact | Contributes to Privilege base growth and warranty attach rate |
| **Data quality at source** | The counter is where most data enters the system; getting it right here prevents error everywhere downstream | Underpins every KPI in Categories A, B and G |
| **PDPA penalty avoidance** | Consent and notice recorded at capture rather than reconstructed later | Avoids exposure of up to BDT 25 lakh per rights violation |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **First impression of the transformation** | For most customers and most staff, M04 *is* the ERP; its usability determines the programme's reputation internally |
| **Adoption anchor** | If the counter works well, branch staff advocate for the rest of the system; if it does not, they resist all of it |
| **Standardisation across 51+ branches** | One process, one job sheet, one gate pass — the foundation of the ISO 9001 claim |
| **Dignity in queueing** | A token and a stated wait is a materially better experience than an undefined crowd, particularly for elderly customers |
| **Staff protection** | Recorded cash movements protect honest staff from suspicion as much as they deter dishonesty |
| **Training simplification** | A new agent reaching competence in four hours makes branch expansion and staff turnover manageable |
| **Lawful basis at the point of collection** | Consent captured at the counter is the only defensible way to satisfy the PDPA for walk-in customers |

---

## 8. Lifecycle & State Models

### 8.1 Queue Token

```
   ISSUED --> WAITING --> CALLED --> SERVING --> COMPLETED
                 |           |
                 |           +--> RECALLED --> NO SHOW
                 |
                 +--> ABANDONED (customer left)
```

### 8.2 Branch Shift

```
   +----------+
   |  CLOSED  |<-----------------------------+
   +----+-----+                              |
        | open with counted float            |
   +----v-----+                              |
   |   OPEN   |                              |
   +----+-----+                              |
        | close requested                    |
   +----v----------+                         |
   |   COUNTING    |                         |
   +----+----------+                         |
        |                                    |
   +----v----------+   within tolerance      |
   |  RECONCILING  |-------------------------+
   +----+----------+                         |
        | variance beyond tolerance          |
   +----v--------------+                     |
   | PENDING APPROVAL  |---- approved -------+
   +-------------------+

   RULE: a branch cannot open a new shift while a prior shift is not CLOSED.
```

### 8.3 Device in Branch Custody

```
   RECEIVED --> STORED (location assigned) --> ISSUED TO WORKSHOP
        |                                            |
        |                                            v
        |                                    RETURNED FROM WORKSHOP
        |                                            |
        |                                            v
        +------------------------------------> READY FOR COLLECTION
                                                     |
                                    +----------------+---------------+
                                    v                v               v
                              COLLECTED      DISPATCHED (M03)   UNCOLLECTED
                                                                     |
                                                                     v
                                                              ABANDONMENT
                                                              PROCESS (M01)
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-FRD-01 | A branch cannot open a shift while a previous shift remains unclosed | **H** | Finance Manager |
| BRU-FRD-02 | A shift cannot close without a counted cash balance | **H** | Finance Manager |
| BRU-FRD-03 | A cash variance beyond the configured tolerance requires branch manager approval before the shift can close | **H** | Finance Manager |
| BRU-FRD-04 | Cash receipts above BDT 50,000 require the customer's NID to be recorded | **H** | CFO |
| BRU-FRD-05 | A device cannot be handed over without identity verification of the collector | **H** | Branch Operations Lead |
| BRU-FRD-06 | A device cannot occupy two storage locations simultaneously | **H** | Branch Operations Lead |
| BRU-FRD-07 | Privilege Gold and Diamond members receive priority queue placement automatically | **C** | CCO |
| BRU-FRD-08 | A token may be recalled once before being marked a no-show | **C** | Branch Operations Lead |
| BRU-FRD-09 | Petty cash expenditure above the threshold requires branch manager approval | **A** | Finance Manager |
| BRU-FRD-10 | A counter sale of a membership or protection product requires the customer's acceptance of terms to be recorded | **H** | CCO |
| BRU-FRD-11 | The same person cannot both handle counter cash and perform the shift reconciliation | **H** | CFO |
| BRU-FRD-12 | An intake cannot be saved without device identification and customer contact verification | **H** | Ops Director |
| **BRU-FRD-13** | **NID capture requires the PDPA transparency notice to be presented and the consent recorded before the field is written** | **H** | CDO / CFO |
| **BRU-FRD-14** | **NID is written only to the Bangladesh-resident store; it is never cached locally, exported, or printed beyond the statutory receipt** | **H** | CTO |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.queue.token` | `fix_queue_token` | A customer's place in line | branch_id, token_number, category, priority, issued_at, called_at, served_at, counter_id, state, intent |
| `fix.queue.counter` | `fix_queue_counter` | A service position | branch_id, code, capabilities, current_agent_id, current_token_id, active |
| `fix.queue.config` | `fix_queue_config` | Branch queue rules | branch_id, categories, priority_rules, recall_policy, display_config |
| `fix.branch.shift` | `fix_branch_shift` | A working session | branch_id, counter_id, agent_id, opened_at, opening_float, closed_at, counted_balance, expected_balance, variance, state, approver_id |
| `fix.cash.drawer` | `fix_cash_drawer` | Physical drawer | branch_id, counter_id, current_balance, last_reconciled_at |
| `fix.cash.movement` | `fix_cash_movement` | Every cash event | shift_id, movement_type, amount, reference_type, reference_id, occurred_at, recorded_by |
| `fix.storage.location` | `fix_storage_location` | Where a device sits | branch_id, code, zone, shelf, bin, capacity, occupied_by_asset_id, secure |
| `fix.branch.checklist` | `fix_branch_checklist` | Opening and closing discipline | branch_id, checklist_type, date, items_json, completed_by, completed_at |
| `fix.shift.handover` | `fix_shift_handover` | Structured handover | branch_id, from_shift_id, to_shift_id, notes, open_items, acknowledged_by |
| `fix.counter.sale` | `fix_counter_sale` | Over-the-counter sale | branch_id, counter_id, shift_id, partner_id, lines, total, payment_method, receipt_ref |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.service.order` | M01 | Creates; reads status |
| `fix.party` | M33 | Search, read, create inline |
| `fix.consent.record` | M33 | Creates the consent record at NID capture |
| `fix.identity.document` | M33 | Writes NID to the resident store |
| `fix.asset` | M17 / M49 | Search, read, register inline |
| `fix.part.item`, `fix.catalogue.item` | M37 | Read for counter sale |
| `fix.membership` | M10 | Read for priority and discount |
| `fix.contract`, `fix.entitlement` | M08 | Read for entitlement display |
| `account.payment` | M20 | Create payment records |
| `fix.bank.account` | M50 | Read for deposit recording |
| `fix.branch` | M30 | Read branch configuration |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-FRD-01 | Token issued | Assign priority by customer tier and intent; estimate wait; display; notify by SMS if the customer opts to wait elsewhere | Token issued without notification |
| AUT-FRD-02 | Counter becomes free | Call the next token by priority and sequence; update the display and announce | Agent calls manually |
| AUT-FRD-03 | Intake saved | Create the service order in M01, print the job sheet, send the acknowledgement and tracking link | Queue for manual order creation; alert |
| AUT-FRD-04 | Device marked Ready by M01 or M31 | Assign a storage location, notify the customer, add to the collection list | Manual location assignment |
| AUT-FRD-05 | Device uncollected at 3, 7, 15 and 30 days | Send escalating reminders; at 30 days trigger the abandonment process in M01 | Manual follow-up task |
| AUT-FRD-06 | Cash receipt above the statutory threshold | Present the transparency notice, record consent, require NID capture before the payment can be saved | Block the transaction |
| AUT-FRD-07 | Shift close requested | Compute the expected balance, present the count screen, calculate variance | Manual reconciliation |
| AUT-FRD-08 | Variance beyond tolerance | Route to the branch manager for approval; block close until approved | Escalate to operations |
| AUT-FRD-09 | Shift closed | Emit the cash position to M50; produce the shift summary | Retry; alert finance |
| AUT-FRD-10 | Branch opening time reached without an open shift | Alert the branch manager and operations | — |
| AUT-FRD-11 | Queue wait exceeds the configured threshold | Alert the branch manager to open an additional counter | — |
| AUT-FRD-12 | Handover completed | Capture the satisfaction rating prompt; emit the collection event | — |

---

## 12. Interfaces

### 12.1 Upstream — M04 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Customer search, profile, tier, consent, transparency notice text | REST |
| M17 Asset Registry | Device search, specification, history | REST |
| M01 Service Order | Order status, Ready notification, order detail | Event + REST |
| M31 Workshop | Device returned from workshop | Event |
| M03 Logistics | Device dispatched or received via consignment | Event |
| M08 Contract | Entitlement for display at intake | REST |
| M09 Warranty | Warranty status for display at intake | REST |
| M10 Loyalty | Membership tier for priority and discount | REST |
| M37 Catalogue / M15 Inventory | Items available for counter sale | REST |
| M30 Platform Admin | Branch, counter and calendar configuration | Master data |

### 12.2 Downstream — M04 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M01 Service Order | Walk-in service order creation and handover confirmation | Command |
| M33 Party Master | Consent record and NID capture | Command |
| M20 Receivable | Counter payments and counter sales | Events |
| M50 Treasury | Branch cash position, deposits, variance | Events |
| M15 Inventory | Counter sale stock consumption | Command |
| M10 Loyalty | Membership sold at counter | Command |
| M09 Warranty | Protection product sold at counter | Command |
| M34 Customer Experience | Counter satisfaction rating | Event |
| M25 Business Intelligence | Queue, throughput, cash and counter facts | Warehouse extract |
| M27 Contact Centre | Token called notification, ready-for-collection reminder | Events |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `queue_token.issued` | branch, token, category, priority, intent | M25, M27 |
| `queue_token.called` | branch, token, counter | M27 |
| `walkin.intake_completed` | service order, customer, device, agent, duration | M01, M25 |
| `consent.captured` | party, purpose, notice version, channel = counter | M33, M60 |
| `device.stored` | asset, branch, storage location | M17 |
| `device.collected` | asset, service order, collector identity, signature | M01, M17, M34 |
| `counter_sale.completed` | branch, lines, total, payment method | M20, M15 |
| `cash.movement_recorded` | shift, type, amount, reference | M50 |
| `shift.opened` | branch, counter, agent, float | M50 |
| `shift.closed` | branch, counter, counted, expected, variance | M50, M25 |
| `cash.variance_flagged` | shift, variance, approver | M50, M60 |
| `device.uncollected` | asset, service order, days ready | M01, M27 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/branch/queue/token` | POST | Issue a token | Kiosk, counter, P01 (QR) |
| `/api/v1/branch/queue/next` | POST | Call the next token | P03 counter |
| `/api/v1/branch/queue/display` | GET | Waiting-area display feed | Display client |
| `/api/v1/branch/intake` | POST | Complete a walk-in intake | P03 counter |
| `/api/v1/branch/customer-lookup` | GET | Search-first customer and device lookup | P03 counter |
| `/api/v1/branch/handover` | POST | Record collection with identity and signature | P03 counter |
| `/api/v1/branch/storage/{asset}` | GET / POST | Locate or assign storage | P03 counter |
| `/api/v1/branch/sale` | POST | Record a counter sale | P03 counter |
| `/api/v1/branch/payment` | POST | Capture a counter payment | P03 counter |
| `/api/v1/branch/shift/open` | POST | Open a shift with float | P03 counter |
| `/api/v1/branch/shift/close` | POST | Close with count and variance | P03 counter |
| `/api/v1/branch/dashboard` | GET | Branch daily operations board | P03 |
| `/api/v1/branch/uncollected` | GET | Uncollected device list | P03 |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R08 Service Centre Agent | C R U | Own branch, own shift |
| R29 Cashier / Counter Finance | C R U | Own counter, own shift |
| R06 Branch Manager | C R U D A | Own branch — including variance approval |
| R05 Operations Director | R U A | All branches |
| R26 Finance Manager | R A | All branches — cash and variance |
| R27 Finance Officer | R | Assigned scope |
| R17 Inventory Manager | R | Counter sale stock movements |
| R32 Quality Manager / ISO Coordinator | R | Checklists and satisfaction |
| R36 Customer | — | Token issue via QR only |

**Field-level restrictions:** cost and margin on counter sales are hidden from agents.
Customer NID is **write-only at the counter** — the agent who captures it cannot read it
back; retrieval is restricted to R26, R27 and R06 with access logging.

**Segregation of duties:** the person handling counter cash cannot perform the shift
reconciliation (BRU-FRD-11, SOD-12).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Branch daily operations board | Branch Manager | Real time | Intake, WIP, ready, overdue, revenue, queue health, staffing |
| Queue performance | Branch Manager, Ops Director | Daily | Tokens issued, average wait, abandonment, peak analysis by hour |
| Counter productivity | Branch Manager | Weekly | Intakes per agent, average handling time, satisfaction rating |
| Intake time distribution | Ops Director | Weekly | Distribution against the three-minute constraint, by branch and agent |
| Cash reconciliation | Finance Manager | Daily | Position, movements, variance, deposits by branch |
| Variance exception report | Finance Manager, GRC | Weekly | Variances above tolerance with approvals and patterns |
| Uncollected device ageing | Branch Manager, Ops Director | Daily | Devices Ready by age band with actions taken |
| Counter sales | CCO, Finance | Monthly | Membership, protection product and accessory sales by branch |
| Branch comparison | Ops Director, CEO | Monthly | All 51+ branches on throughput, wait, handling time, satisfaction, cash discipline |
| Checklist compliance | Ops Director, Quality | Monthly | Opening and closing checklist completion rates |
| Consent capture completeness | CDO, Quality Manager | Monthly | NID captures with a valid recorded consent — target 100% |

---

## 15. KPIs

> **Audit finding M-04.** KPIs in this module previously carried no identifiers. They are now
> allocated in the `KPI-1nn` range reserved for Category A module-level metrics.

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-010 | Average walk-in intake time | ~10 min | < 4 min | **< 3 min** |
| KPI-110 | Average queue wait time | unmeasured | < 15 min | **< 12 min** |
| KPI-111 | Queue abandonment rate | unmeasured | < 8% | **< 4%** |
| KPI-112 | Devices located within 60 seconds at collection | unmeasured | 95% | **> 98%** |
| KPI-113 | Counter cash variance incidents per branch per month | unmeasured | < 2 | **< 1** |
| KPI-114 | Shifts closed on time | unmeasured | 94% | **> 97%** |
| KPI-009 | Devices uncollected > 30 days | unmeasured | < 1% | **< 0.5%** |
| KPI-115 | Counter satisfaction rating | unmeasured | > 4.2/5 | **> 4.5/5** |
| KPI-116 | New agent time to competence | 2–3 days | < 6 h | **< 4 h** |
| KPI-117 | Intakes created without the paper form | 0% | **100%** | **100%** |
| KPI-118 | Opening and closing checklist completion | 0% | 90% | **> 97%** |
| **KPI-119** | **NID captures with a valid recorded consent** | n/a | **100%** | **100%** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `point_of_sale` primitives, `account.payment`, `product` | 18% |
| L2 | OCA `pos_*` extensions where applicable | 6% |
| L5 | `cd_queue`, `cd_cash_drawer`, `cd_branch_ops`, counter workstation, kiosk, display client | 76% |

### 16.2 Custom Development

> **Audit finding H-03.** CD identifiers are provisional pending the unified CD register in
> `02-05`. The numbers below are reserved for M04 and will be confirmed when the register is
> restated for all 67 modules.

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-022 | `cd_queue` — token, counter, display, priority, kiosk | Odoo module | 4 PW |
| CD-023 | `cd_cash_drawer` — shift, drawer, movements, variance, deposit | Odoo module | 4 PW |
| CD-024 | `cd_branch_ops` — counter workstation, storage location, checklists, dashboard | Odoo module + frontend | 5 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M04 is scheduled in **W1** (P1) but declares a dependency on 1 module(s) that land later: **M17** (W2). One of three things must be true before the W1 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W1 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M04 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W1 plan for M04 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M33 Party Master | Customer lookup is the first action of every intake; consent and notice originate here |
| M17 Asset Registry | Device identification is mandatory at intake |
| M01 Service Order | The counter creates service orders |
| M29 Identity | Agent authentication and shift attribution |
| M30 Platform Admin | Branch and counter configuration must exist |
| **Bangladesh-resident store** | Required before NID capture goes live *(NFR-086, dependency DEP-31)* |
| M20 / M50 | Payment and cash posting — may be stubbed in W1 and completed in W3 |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Devices currently held at branches | ~5,000 across pilot branches | `fix.storage.location` assignment | W1 cutover |
| Branch, counter and storage layout | 51+ branches | `fix.queue.counter`, `fix.storage.location` | W1 |
| Opening cash floats | 51+ | `fix.branch.shift` | W1 cutover |

Storage layouts must be **surveyed and authored** per branch before go-live. This is a
physical exercise, not a data extract, and it is the most commonly underestimated task in
Wave 1.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Walk-in intake is completed in under three minutes by branch staff, not by the project team | Timed observation, 20 samples across 3 branches, median and 90th percentile both under 3 minutes |
| AC-02 | A new agent reaches competence within four hours of training | Observed on three new agents |
| AC-03 | Paper intake forms are withdrawn at all live branches | Physical confirmation and stock destruction |
| AC-04 | The queue display operates continuously through a full trading day including a connection interruption | Observation over five days |
| AC-05 | A shift cannot open while a prior shift is unclosed, including via API | Negative test |
| AC-06 | Cash variance beyond tolerance blocks shift close until approved | Negative test |
| AC-07 | NID capture is enforced on cash receipts above the statutory threshold | Negative test |
| **AC-08** | **NID cannot be captured without the transparency notice presented and consent recorded** | **Negative test** |
| **AC-09** | **NID is written only to the Bangladesh-resident store and is absent from every regional cache, log and export** | **Data-flow audit and log review** |
| AC-10 | A device is located from its storage reference within 60 seconds in 98% of collections | Timed observation, 50 collections |
| AC-11 | Every counter cash movement reconciles to the branch position in M50 | Four weeks of daily reconciliation |
| AC-12 | The counter workstation operates for two hours without connectivity and syncs cleanly | Controlled disconnection test |
| AC-13 | All counter screens, printed documents and the display are complete in Bengali | Translation coverage report |
| AC-14 | Customer lookup returns in ≤ 400 ms and the counter dashboard in ≤ 1.5 s | Load test at branch hardware specification |
| AC-15 | Peripheral integration works for receipt printer, label printer, scanner and signature pad | Hardware integration test at three branches |
| AC-16 | Branch managers and agents sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | Which branches get a kiosk and a waiting-area display in Wave 1, and what is the hardware budget? | Ops Director / CFO | W1 minus 2 months |
| Q-02 | What is the cash variance tolerance before manager approval is required? | CFO | W1 build |
| Q-03 | What is the priority policy — do corporate account holders outrank Privilege Gold? | CCO | W1 build |
| Q-04 | Is there an existing storage-location convention at branches, or must one be designed? | Branch Operations Lead | W1 design |
| Q-05 | Do branches currently hold a petty cash float, and under whose authority? | CFO | W1 build |
| Q-06 | Should the counter be able to take card payments in Wave 1, or cash and mobile money only? | CFO | W1 build |
| Q-07 | What identity document is acceptable for device collection by a person other than the customer? | Legal / Ops Director | W1 build |
| **Q-08** | **Is the BDT 50,000 NID threshold still current under NBR rules, and does the PDPA 2026 change how it must be collected, stored and retained?** | **CFO / Legal / CDO** | **W1 build** |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` · `M01_Service_Request_and_Order_Management.md` ·
`M31_Workshop_and_Depot_Repair_Management.md` ·
`00_Governance_and_Charter/00-06_Documentation_Audit_Report.md` (findings C-03, C-04, M-04) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3–6.4 ·
`03_Modules/G_Finance_and_Treasury/_CATEGORY_OVERVIEW.md` §7 (cash control across branches) ·
`03_Modules/K_Platform_and_Technology/P03_Admin_Operations_Portal.md` *(planned)*

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-SRM-001, FSM-030,
§6.2 Process 1, BRU-FIN-02 · `1000FiX_ERP_System_Comprehensive_URD.md` Persona 1, §5.1 ·
`1000FiX_Services_Company_Profile.md` §Service Infrastructure ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Customer categorisation

**External benchmark and regulation** *(verified 2026-08-12)*
Enterprise queue management practice — virtual queueing, kiosk and QR check-in, intent capture
at check-in, routing by need and real-time availability, SMS and WhatsApp notification, live
wait times and manager analytics; the eight-minute queue abandonment threshold ·
Retail multi-store POS — shift, drawer, float and variance discipline ·
Bank branch operations — screen pop and tiered service ·
Odoo `point_of_sale` and Dynamics 365 Commerce session models ·
**Bangladesh Personal Data Protection Act 2026 (Law 63 of 2026)** — consent, transparency
notice, sensitive personal data including NID, and cross-border transfer restriction

---

*Module M04 · Category A · 1000FiX ERP System v2.0 · Revision 1.1 · CONFIDENTIAL*
