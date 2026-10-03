---
id: FIX-ERP2-M01
module_id: M01
module_code: SRM
module_name: Service Request & Order Management
category: A — Service Delivery & Operations
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Service Operations Director
system_owner: Service Squad
priority: P0
wave: W1 (core) → W2 (complete)
---

# M01 — Service Request & Order Management
### Category A · Code `SRM` · Existing module, re-scoped in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M01 |
| **Module code** | `SRM` |
| **Category** | A — Service Delivery & Operations |
| **Status** | Existing (re-scoped — workshop execution moved to M31) |
| **Priority** | **P0** — cannot be descoped |
| **Delivery wave** | W1 core (Months 1–4) → W2 complete (Months 5–8) |
| **Business owner** | Service Operations Director |
| **System owner** | Service Squad |
| **Delivery layers** | L2 (OCA `fieldservice`, `helpdesk`) + L5 (custom) |
| **Custom modules** | `cd_service_order`, `cd_diagnostic`, `cd_sla`, `cd_rework`, `cd_service_ext` |
| **Requirement range** | FR-SRM-001 … FR-SRM-087 |
| **Requirement count** | **70** *(measured 2026-08-13; 18 allocated identifiers retired unused — see below)* |
| **Effort estimate** | 46 person-weeks — the largest single module |
| **Depends on** | M33 Party Master · M17 Asset Registry · M29 Identity · M28 Integration · M37 Catalogue |
| **Depended on by** | M02, M31, M03, M04, M09, M20, M23, M25, M27, M34, M53, M06, M12, M54, M57, M61 |

---

## 2. Purpose

M01 owns the **service order** — the single master record of everything a customer has asked
1000FiX to do, and the authoritative answer to *"what is happening with my device?"*.

Every one of the 250,000+ monthly customer interactions creates or touches a service order.
Every technician, branch manager, finance officer and customer sees it. It is the object
around which the entire company revolves, and the module that most determines whether the
ERP succeeds or fails.

### Why It Exists

Today a service request is written on paper or typed into a branch spreadsheet. There is no
consistent order number, no searchable history, no SLA clock, no automatic customer
notification, and no reliable link between what was promised and what was delivered. The
v1.0 BRD measures the consequence: **only ~20% of the service order lifecycle is automated**,
turnaround time is not measured at all, and rework is invisible.

M01 replaces that with one record, one number, one lifecycle and one truth — across nine
service delivery modes, twelve intake channels and 51+ locations.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.1 (BR-SRM-001…020) | Multi-channel intake, lifecycle, SLA, escalation, rework, approval thresholds |
| ERP BRD §10.1 (BRU-SRM-01…10) | Ten enforced business rules governing service orders |
| ERP BRD §12 Process 1 | End-to-end service request to completion flow |
| ERP URD §6 (US-SRM-*) | Service centre agent and dispatch manager user stories |
| Company Profile §Core Services | The service catalogue that service orders are raised against |
| Service App SOW §Service Management | "If a customer requests a service through apps, it will push data to our ERP through API. Service request ID will be generated at ERP." |
| Service App SOW §Job sheet | "The app should have forms/fields that are like ERP fields. Data entered in the app form will be exported to ERP through API." |
| Business Plan §On-Site Repair, §24/7 Support | Delivery modes the service order must represent |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Service order creation from all twelve intake channels |
| 2 | The service order lifecycle state machine and all transition guards |
| 3 | Entitlement evaluation at intake (warranty, contract, membership, MSP) |
| 4 | Complaint capture, symptom taxonomy and fault coding |
| 5 | Diagnostic template definition and execution |
| 6 | Estimate request, customer approval loop and approval thresholds |
| 7 | Work assignment handoff to M02 (field) or M31 (workshop) |
| 8 | SLA policy application, clock management and escalation |
| 9 | Hold management with SLA suspension |
| 10 | Quality-checkpoint enforcement at defined transitions |
| 11 | Rework detection and linkage |
| 12 | Service report generation and customer handover record |
| 13 | Repair warranty issuance and tracking |
| 14 | Service order search, operations boards and WIP analysis |
| 15 | The service order API and domain events consumed by every other module |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Customer identity, addresses, consent | **M33** Party Master | One party master; M01 references, never edits |
| Device identity, serial, ownership history | **M17** Asset Registry | Devices outlive service orders; identity must not be trapped inside a transaction |
| Price calculation and rate cards | **M11** Pricing | A price is a commercial decision, not a service outcome |
| Estimate document, versions, bidding | **M36** Quotation | Quotation is a commercial object with its own lifecycle and legal weight |
| Bench allocation, component-level repair, test and burn-in | **M31** Workshop | Internal execution detail; the customer never sees it |
| Technician selection, routing, mobile execution | **M02** Field Service | Assignment is an optimisation problem with its own module |
| Physical movement of the device | **M03** Logistics | Custody is a legal chain, not a status field |
| Counter queue, cash, shift | **M04** Front Desk | Branch floor operations have their own cadence |
| Contract terms and entitlement definition | **M08** Contract | M01 validates against entitlements; it does not define them |
| Warranty claim to the brand | **M09** Warranty | Claim recovery is a finance process with brand-specific rules |
| Invoice creation and collection | **M20** Accounts Receivable | Only Category G creates financial documents |
| Non-conformance, root cause, CAPA | **M23** Quality | M01 raises the quality event; M23 investigates it |
| Customer notification delivery | **M27** Contact Centre | M01 raises events; M27 chooses channel, language and timing |
| Parts stock, reservation and valuation | **M15** Inventory | M01 requests parts; it does not hold stock |

### 3.3 Shared Concepts

| Concept | M01's Role | Owning Module |
|---|---|---|
| Customer | Reads live; displays 360 context | M33 |
| Device / asset | Reads live; writes service history events back | M17 |
| Fault code | Assigns; consumes the taxonomy | M37 (definition) |
| SLA policy | Applies and measures | M08 (contractual SLAs), M01 (standard SLAs) |
| Quality checklist | Executes and records | M23 (authors) |
| Custody event | Raises when a device changes hands at intake or handover | M03 |
| Billable event | Emits on completion | M53 / M20 |

---

## 4. Benchmark Basis

| Reference System | Equivalent | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP S/4HANA Service** — Service Order Management, Service Request Management | Service order header with items, service contracts integration, service confirmations | Header/item structure; separation of request from execution; confirmation as a distinct record | SAP's document-flow complexity — unnecessary at our transaction profile |
| **SAP In-House Repair** | Repair object separated from the service order | The separation itself — this is why M31 exists | Full SAP repair procedure model |
| **Microsoft Dynamics 365 Field Service** — Case → Work Order | Case as customer-facing, work order as execution | Case/work-order split, mapped to service order/work order | Dataverse-specific entity conventions |
| **IFS Cloud Service Management** | Service request, contract and warranty verification at intake | Warranty verification against rules at intake to prevent revenue loss | — |
| **ITIL 4** — Incident vs Service Request | Distinguishing an interruption from a request | Separate priority and SLA treatment for emergency vs planned work | ITIL's full practice structure — this is a repair business, not an IT service desk |
| **Odoo 19 + OCA** — `fieldservice`, `helpdesk_mgmt`, `helpdesk_mgmt_sla` | Order, stage, SLA, escalation | The base object model and SLA framework as the L2 foundation | Odoo's default single-stage model — insufficient for nine delivery modes |
| **Specialist after-sales platforms** (service ERP for authorised service centres) | Job card, ticket, spare parts, gate pass, RMA | Job-sheet concept and gate-pass discipline familiar to Bangladeshi service operations | Their single-brand assumptions |

**Design position.** 1000FiX differs from the benchmarks in three deliberate ways.
First, the service order is **polymorphic across nine delivery modes and fourteen revenue
streams** — a thin core with typed extensions rather than nine separate order types.
Second, **Bengali is the primary interface language** for intake and field surfaces, which
constrains field lengths, fonts and voice input in ways Western products do not consider.
Third, **the customer's tracking view is a first-class output**, not a bolt-on portal — the
lifecycle is designed to be legible to a customer, which is why internal bench detail is
excluded from M01 entirely.

---

## 5. Functional Areas & Features

### 5.1 Multi-Channel Service Intake

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-001 | Twelve-channel intake | Create service orders from: web portal, customer mobile app, WhatsApp, AI assistant, hotline 16743, walk-in counter, email, corporate B2B portal bulk upload, marketplace, partner referral, MSP alert, and contract preventive schedule | P0 | L5 |
| FR-SRM-002 | Order numbering | Generate a unique order number using a configurable mask incorporating branch, business line and year, with no gaps and no reuse | P0 | L1 |
| FR-SRM-003 | Order type classification | Classify as Warranty · Out-of-Warranty · AMC · RAMC · MSP · Emergency · Preventive · Rental Service · Data Service · Refurbishment · Recycling · Marketplace | P0 | L5 |
| FR-SRM-004 | Customer identification | Search or create the customer inline with duplicate detection on phone, email and NID before the order is saved | P0 | L5 |
| FR-SRM-005 | Device identification | Identify the device by serial, IMEI, asset tag, QR label, or brand+model+purchase evidence; register a new device inline without leaving intake | P0 | L5 |
| FR-SRM-006 | Entitlement evaluation | Evaluate brand warranty, extended warranty, AMC/RAMC coverage, MSP entitlement and Privilege tier at intake, and display the resulting commercial treatment before the order is confirmed | P0 | L5 |
| FR-SRM-007 | Structured complaint capture | Capture the complaint through a symptom → category → sub-category taxonomy plus free text in Bengali or English, with voice-to-text on mobile | P1 | L5 |
| FR-SRM-008 | Accessory and condition log | Record accessories received, cosmetic condition, pre-existing damage, and data-access notes, with explicit customer acknowledgement | P0 | L5 |
| FR-SRM-009 | Intake evidence capture | Capture photographs of the device at intake with timestamp, GPS and the identity of the capturing staff member | P0 | L5 |
| FR-SRM-010 | Job sheet | Generate and print or send a bilingual job sheet with terms, estimated turnaround and the tracking link | P0 | L2 |
| FR-SRM-011 | Multi-device job batch | Group multiple devices from one customer or corporate site under a shared batch reference with a single point of coordination | P1 | L5 |
| FR-SRM-012 | Appointment booking | Reserve a service slot with capacity checking by branch, skill and service type | P1 | L5 |
| FR-SRM-013 | Emergency and after-hours intake | Flag emergency intake, apply the premium tariff, and route to the on-call rota outside business hours | P2 | L5 |
| FR-SRM-084 | Universal search | Search service orders by any attribute including free text and Bengali content, returning results in under 600 ms | P1 | L5 |
| FR-SRM-085 | Saved views and filters | Allow users to save, name and share list views and filter sets | P2 | L1 |

### 5.2 Service Order Lifecycle

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-014 | Lifecycle state machine | Enforce the full state model with declared transitions, guards and actors (see §8) | P0 | L5 |
| FR-SRM-015 | Transition guards | Block invalid transitions and enforce named preconditions — approval before parts issue, QC pass before Ready, payment or credit clearance before release | P0 | L5 |
| FR-SRM-016 | Hold management | Place an order on hold with a reason code, suspending the SLA clock, and resume automatically on release | P1 | L5 |
| FR-SRM-017 | Reassignment and transfer | Transfer an order between technicians, branches or workshops with a complete custody and accountability trail | P1 | L5 |
| FR-SRM-018 | Split and merge | Split an order when a device requires independent repairs; merge duplicate orders raised for the same device | P2 | L5 |
| FR-SRM-019 | Cancellation and abandonment | Cancel with reason codes; automatically flag abandoned devices after a configurable dwell period and generate statutory notice | P1 | L5 |
| FR-SRM-020 | Reopen | Reopen a closed order within the repair-warranty window, automatically linking it as rework | P1 | L5 |
| FR-SRM-080 | Priority override | Allow authorised roles to override the calculated priority, with a mandatory logged reason | P1 | L5 |
| FR-SRM-082 | Case linkage | Link every visit, repair order and consignment belonging to one customer problem into a single case view | P1 | L5 |
| FR-SRM-086 | Bulk operations | Perform bulk state changes, assignments and notifications with preview, confirmation and rollback | P1 | L5 |
| FR-SRM-087 | Archival | Archive closed orders beyond the operational window while keeping them fully retrievable | P2 | L5 |

### 5.3 Diagnosis, Estimation & Customer Approval

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-021 | Diagnostic template library | Maintain diagnostic decision trees per device category, brand, model and symptom, with conditional branching and versioning | P0 | L5 |
| FR-SRM-022 | Guided diagnosis | Present the decision tree to the technician on mobile or bench terminal and record every answer, measurement and photograph | P0 | L5 |
| FR-SRM-023 | Fault coding | Assign standard fault codes and root-cause categories used consistently across warranty claims, quality analysis and predictive models | P0 | L5 |
| FR-SRM-024 | Repair-level routing | Classify the required repair as Level 1 (basic), Level 2 (component) or Level 3 (board / micro-soldering) and route to a qualified technician or workshop | P1 | L5 |
| FR-SRM-025 | Estimate request | Request an estimate from M36 with the fault code, device, parts indication and labour classification; display the returned estimate | P0 | L5 |
| FR-SRM-027 | Customer approval loop | Deliver the quotation through the customer's preferred channels with accept, part-accept and reject options and a configurable expiry | P0 | L5 |
| FR-SRM-028 | Internal approval thresholds | Enforce internal approval above configurable value thresholds in addition to customer approval | P0 | L5 |
| FR-SRM-029 | Declined-repair handling | On rejection, raise the diagnostic fee, issue reassembly instructions and create the return or collection task | P1 | L5 |
| FR-SRM-030 | Second opinion | Route high-value or contentious diagnoses to a senior technician for peer review before quoting | P2 | L5 |
| FR-SRM-077 | Multi-fault handling | Handle multiple independent faults on one device with separate estimate lines and independent approval | P2 | L5 |

### 5.4 Execution Coordination

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-031 | Work order generation | Generate one or more work orders (M02) or repair orders (M31) from a service order, each with scope, skill requirement and target time | P0 | L5 |
| FR-SRM-033 | Labour time roll-up | Aggregate labour time recorded in M02 and M31 to the service order for costing and analysis | P0 | L5 |
| FR-SRM-034 | Parts requisition | Raise a parts requirement against the service order and track its fulfilment through M15 | P0 | L2 |
| FR-SRM-036 | Sub-contracting | Route a service order or a component to an external specialist or marketplace seller with cost, SLA and custody tracking | P2 | L5 |
| FR-SRM-039 | Unrepairable determination | Declare a device beyond economic repair with evidence and a second technician's confirmation, then route to trade-in, recycling or return | P1 | L5 |
| FR-SRM-076 | Loan device management | Issue and track a loan device to a customer while their own device is in repair, including return reconciliation | P2 | L5 |
| FR-SRM-078 | Job cost roll-up | Accumulate all costs — labour, parts, logistics, sub-contract, overhead — to the service order for margin analysis | P1 | L5 |

### 5.5 Quality, Handover & Repair Warranty

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-040 | Quality gate | Prevent transition to Ready without a passed quality checklist appropriate to device type and repair level | P0 | L2 |
| FR-SRM-041 | Independent quality control | Require QC by a person other than the repairing technician above a configurable value or risk threshold | P1 | L5 |
| FR-SRM-042 | Before/after evidence | Mandate before and after photographs with timestamp and GPS; assemble them into the warranty evidence pack | P0 | L5 |
| FR-SRM-043 | Customer handover | Capture identity verification, accessory return confirmation and electronic signature at handover | P0 | L5 |
| FR-SRM-044 | Service report | Generate a bilingual service report stating findings, work performed, parts replaced and the warranty granted on the repair | P0 | L2 |
| FR-SRM-045 | Repair warranty | Apply and track a service warranty period per repair type; automatically classify returns within the window as warranty rework | P0 | L5 |
| FR-SRM-046 | Delivery coordination | Trigger a logistics consignment for pick-and-drop return, or notify the customer for counter collection | P1 | L5 |
| FR-SRM-083 | Device photo library | Maintain the complete photographic history of a device across all its service events | P2 | L5 |

### 5.6 SLA, Escalation & Rework

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-047 | SLA definition | Define SLAs by service type, business line, brand, customer tier, contract and priority, with working-calendar awareness | P0 | L2 |
| FR-SRM-048 | Multi-clock SLA | Run response, diagnosis, repair and total-resolution clocks independently, honouring holds and business hours | P0 | L5 |
| FR-SRM-049 | Escalation matrix | Fire escalations at 50%, 75%, 90% and 100% of SLA to defined roles, with acknowledgement tracking | P0 | L5 |
| FR-SRM-050 | Automatic re-prioritisation | Reassign or re-prioritise automatically when an SLA is at imminent risk and the assignee is unresponsive | P2 | L5 |
| FR-SRM-051 | Rework detection | Automatically flag a new order for the same device and fault category within a configurable window as rework, linked to the original | P0 | L5 |
| FR-SRM-052 | Rework accountability | Attribute rework to the original technician, branch and root cause; emit the quality and performance events | P1 | L5 |
| FR-SRM-053 | Repeat-failure analysis | Identify devices, models or parts with abnormal repeat-failure rates and raise a quality alert | P2 | L5 |

### 5.7 Customer Visibility & Notification

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-054 | Milestone events | Emit a domain event at every lifecycle milestone with a customer-safe message payload | P0 | L5 |
| FR-SRM-055 | Tracking link | Issue a tokenised public tracking link showing a visual status timeline without requiring login | P0 | L5 |
| FR-SRM-056 | Proactive delay notice | Detect that a promised date will be missed and emit a delay event with a revised commitment before the customer notices | P1 | L5 |
| FR-SRM-057 | Post-service survey trigger | Emit the survey trigger event a configurable interval after handover | P1 | L5 |

### 5.8 Business-Line Extensions

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-SRM-063 | Rental service intake | Create a service order for a rental asset carrying the agreement, deposit and liability context | P2 | L5 |
| FR-SRM-065 | Data-service intake | Create a data-services case as a confidentiality-controlled service order with restricted visibility from creation | P2 | L5 |
| FR-SRM-066 | Refurbishment intake | Create a refurbishment work order from a trade-in, an unrepairable outcome or a rental retirement | P2 | L5 |
| FR-SRM-068 | Marketplace job creation | Create a service order from a marketplace transaction with the external seller as the executing party | P1 | L5 |
| FR-SRM-069 | MSP-generated work | Create a service order from a managed-services alert, ticket or scheduled task | P1 | L5 |
| FR-SRM-070 | Contract-generated work | Create scheduled preventive work orders from contract maintenance plans at the correct lead time | P1 | L5 |
| FR-SRM-072 | Bulk corporate site visit | Plan a single visit covering many devices at one site, with independently tracked per-device outcomes | P1 | L5 |
| FR-SRM-073 | Recall campaign | Execute a brand recall as a batch of service orders against affected serial numbers | P2 | L5 |

*(Full requirement text for FR-SRM-058 … FR-SRM-088 is held in
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md`.)*

> **Retired requirement identifiers.** 18 identifiers inside the original `FR-SRM-001 … 088` allocation were never issued to a requirement and are **retired, not reissued**, under register rule RG-02 (permanent identity):
>
> FR-SRM-026, 032, 035, 037, 038, 058, 059, 060, 061, 062, 064, 067, 071, 074, 075, 079, 081, 088
>
> The measured requirement count for this module is **70**. Earlier statements of **88** were taken from the highest allocated identifier rather than a count of requirements (audit finding A3-01).

---

## 6. Technical Functions

These are engineering behaviours the module must exhibit. They are not user-visible but they
determine whether the module survives production.

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Idempotent creation** | Every intake channel supplies an idempotency key; a retried booking never creates a duplicate order |
| T-02 | **Optimistic concurrency** | Two users editing the same order produce a detectable conflict, never a silent overwrite |
| T-03 | **Transactional outbox** | Every state change writes its domain event in the same database transaction as the state change |
| T-04 | **State machine as data** | Transitions, guards and side effects are declared in one configuration table, not scattered through code |
| T-05 | **Partitioning** | `fix_service_order` is range-partitioned by creation date from year three to hold 5 million orders per year |
| T-06 | **Index strategy** | Composite indexes on (branch, state, date), (customer, date), (asset, date); GIN index for Bengali full-text search |
| T-07 | **SLA clock evaluation** | A single scheduled evaluator scans only orders with an upcoming breach threshold, not the full table |
| T-08 | **Bulk operation safety** | Bulk actions run as background jobs with progress reporting, preview and rollback |
| T-09 | **Offline compatibility** | Every field-originated state change is expressible as an idempotent command replayable from the technician app journal |
| T-10 | **Read model for tracking** | The public tracking view is served from a denormalised read model, never by querying the transactional table |
| T-11 | **API versioning** | `/api/v1/service-orders` with a documented deprecation policy and two concurrent versions |
| T-12 | **Localisation** | Every user-facing string translatable; Bengali text stored UTF-8 with ICU collation for correct sorting |
| T-13 | **Audit completeness** | Every field change on a service order is audited with before and after values |
| T-14 | **Attachment handling** | Photographs are compressed client-side, malware-scanned server-side, stored in object storage, referenced not embedded |
| T-15 | **Performance envelope** | Order creation ≤ 500 ms p95; order retrieval ≤ 250 ms p95; operations board with 500 open orders ≤ 1 s |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M01 |
|---|---|---|
| **Service centre agent** | Writes on paper or types into a branch spreadsheet; cannot see the customer's history; no way to check warranty | Search-first intake in under three minutes with full history, automatic entitlement check and a printed job sheet |
| **Dispatch manager** | Works from a paper list; phones technicians; has no idea which jobs are at risk | Live queue sorted by SLA risk, with automatic escalation before a breach |
| **Technician** | Receives verbal instructions; carries a paper form; writes findings by hand | Full job context on the phone, guided diagnosis, evidence capture, customer signature |
| **Branch manager** | Discovers problems when a customer complains | Sees WIP ageing, SLA risk and uncollected devices on a live board |
| **Finance officer** | Types invoices from paper forms, three to seven days late | Invoice raised automatically the moment the order is completed |
| **Warranty officer** | Compiles claims manually from paper, weeks later | Claim created automatically within 24 hours with the evidence pack already assembled |
| **Customer** | Calls the hotline three or more times to ask for status | Receives a message at every milestone and tracks progress on a link |
| **Executive** | Waits for compiled spreadsheets | Sees live volume, TAT, SLA and rework across all 51+ branches |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Warranty revenue recovery** | Automatic claim creation on completion of a warranty order, with evidence already captured — closing the 30–90 day submission delay | Enables **BDT 100 lac/year** (M09 realises it; M01 makes it possible) |
| **Administrative labour saving** | Elimination of double entry between paper, spreadsheet and accounting; automatic invoicing and notification | **BDT 62 lac/year** across the estate |
| **Reduced customer churn** | Transparency and proactive notification; measured satisfaction; complaint traceability | Contributes to **BDT 78 lac/year** retention benefit |
| **Rework reduction** | Rework becomes visible and attributable for the first time; root causes reach M23 | *Illustrative:* each percentage point of rework reduction avoids the cost of roughly 1% of job volume being redone. **The monetary value cannot be stated until the rework baseline is measured** — rework is currently unmeasured (see `06-02` KPI-005). No figure should be carried into the business case before Wave 2 baselining. |
| **Hotline deflection** | Tracking link and milestone notifications remove the reason for status calls | **60% reduction** in status enquiries, releasing contact-centre capacity |
| **Revenue leakage closure** | No completed work can be closed without a billable event | Reduces unbilled delivered work from unknown to **< 0.5%** |
| **ISO 9001 defensibility** | Documented, traceable process with enforced quality gates | Protects the certification that wins corporate tenders |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Institutional memory** | Device and customer history stops living in a technician's head or a branch drawer |
| **Fair workload measurement** | Technician performance becomes measurable and therefore arguable on evidence rather than impression |
| **Dispute defensibility** | Intake condition photographs and signed handover records settle customer disputes with evidence |
| **Regulatory readiness** | Traceable records support NBR, brand-partner and certification audits without a scramble |
| **Change capability** | A configurable state machine means a new business line is configuration, not a project |
| **Data foundation for AI** | Every model in M26 — dispatch, duration, fault classification, quality risk — trains on M01 data |

---

## 8. Lifecycle & State Model

```
                    ┌─────────┐
                    │  DRAFT  │  (intake in progress, not yet confirmed)
                    └────┬────┘
                         │ confirm
                    ┌────▼─────┐
      ┌────────────►│ RECEIVED │◄──────────── reopen (within warranty window)
      │             └────┬─────┘
      │                  │ assign for diagnosis
      │             ┌────▼──────────┐
      │             │  DIAGNOSING   │──────────────┐
      │             └────┬──────────┘              │
      │                  │ diagnosis complete      │
      │             ┌────▼───────────────┐         │
      │             │ ESTIMATE PENDING   │         │
      │             └────┬───────────────┘         │
      │                  │ estimate issued         │
      │             ┌────▼───────────────┐         │
      │             │ AWAITING APPROVAL  │─────────┤ reject ──► DECLINED ──► RETURN
      │             └────┬───────────────┘         │
      │                  │ approved                │
      │             ┌────▼───────────┐             │
      │             │   APPROVED     │             │
      │             └────┬───────────┘             │
      │                  │ release to execution    │
      │             ┌────▼───────────┐             │
      │        ┌───►│  IN PROGRESS   │◄────────────┘ (no estimate needed — warranty/AMC)
      │        │    └────┬───────────┘
      │        │         │
      │        │    ┌────▼──────────┐  parts / customer / brand / access
      │        └────┤    ON HOLD    │  (SLA clock suspended)
      │             └───────────────┘
      │                  │ work complete
      │             ┌────▼────┐
      │             │   QC    │──── fail ──► back to IN PROGRESS
      │             └────┬────┘
      │                  │ pass
      │             ┌────▼────┐
      │             │  READY  │  (awaiting collection or delivery)
      │             └────┬────┘
      │                  │ handover / delivery confirmed
      │             ┌────▼──────────┐
      │             │  DELIVERED    │
      │             └────┬──────────┘
      │                  │ billable event emitted
      │             ┌────▼──────────┐
      │             │   INVOICED    │
      │             └────┬──────────┘
      │                  │ payment settled / claim raised
      │             ┌────▼──────────┐
      └─────────────│    CLOSED     │──► ARCHIVED (after retention window)
                    └───────────────┘

  Terminal exceptions: CANCELLED · UNREPAIRABLE · ABANDONED
```

### Transition Guards

| From | To | Guard | Actor |
|---|---|---|---|
| Draft | Received | Customer and device identified; entitlement evaluated | Agent, portal, API |
| Received | Diagnosing | Assigned to a technician or workshop | Dispatcher, agent |
| Diagnosing | Estimate Pending | Diagnostic checklist complete; fault code assigned | Technician |
| Estimate Pending | Awaiting Approval | Estimate received from M36 and issued to the customer | System |
| Awaiting Approval | Approved | Customer decision recorded; internal threshold approvals obtained | Customer + approver |
| Awaiting Approval | Declined | Customer rejection recorded with reason | Customer |
| Approved / Received | In Progress | Required parts reserved or confirmed available | System |
| Any active | On Hold | Approved hold reason selected | Technician, dispatcher |
| In Progress | QC | Work recorded complete; time and parts posted | Technician |
| QC | Ready | **Quality checklist passed** — hard gate (BRU-SRM-04) | QC inspector |
| Ready | Delivered | Identity verified; accessories confirmed; signature captured | Agent, technician, rider |
| Delivered | Invoiced | Billable event accepted by M20 | System |
| Invoiced | Closed | Payment settled, credit terms applied, or warranty claim raised | System |
| Closed | Received | Reopen within the repair-warranty window; auto-flagged as rework | Agent, manager |

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-SRM-01 | A service order cannot be created without an identified device; unregistered devices must be registered during intake | **H** | Ops Director |
| BRU-SRM-02 | A warranty-type order can only be created if warranty is active at the service request date | **H** | Warranty Officer |
| BRU-SRM-03 | An AMC-type order can only be created if the device appears on an active contract's covered-asset list | **H** | Account Manager |
| BRU-SRM-04 | An order cannot reach Ready without a passed quality checklist | **H** | Quality Manager |
| BRU-SRM-05 | An invoice cannot be raised for an order that is not Delivered | **H** | Finance Manager |
| BRU-SRM-06 | A new order for the same device and fault category within 30 days is automatically flagged as rework and linked | **C** | Quality Manager |
| BRU-SRM-07 | Estimates above BDT 5,000 require documented customer approval before work begins | **H** | Ops Director |
| BRU-SRM-08 | Estimates above BDT 25,000 require customer approval and branch manager approval | **H** | Ops Director |
| BRU-SRM-09 | An order cannot be assigned to a technician lacking a current certification for that brand's warranty work | **H** | Quality Manager |
| BRU-SRM-10 | Privilege Gold and Diamond members receive priority-1 SLA automatically regardless of service type | **C** | CCO |
| BRU-SRM-12 | Beyond-economic-repair requires photographic evidence and a second technician's confirmation | **H** | Ops Director |
| BRU-SRM-13 | An expired estimate must be re-issued, never extended | **H** | CCO |
| BRU-SRM-15 | The SLA clock is suspended only by an approved hold reason and resumes automatically on release | **C** | Ops Director |
| BRU-SRM-16 | A device uncollected 30 days after Ready enters the abandonment process with statutory notice | **C** | Branch Manager |
| BRU-SRM-17 | Before and after photographs are mandatory on every warranty order; the order cannot close without them | **H** | Warranty Officer |
| BRU-SRM-18 | Independent QC by a second person is mandatory above BDT 25,000 | **H** | Quality Manager |
| BRU-SRM-19 | Reopening is permitted only within the repair-warranty period and links the orders as rework | **A** | Branch Manager |
| BRU-SRM-20 | Customer data-access notes are captured only with explicit consent and are purged at handover | **H** | Quality Manager |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.service.order` | `fix_service_order` | The master service record | name, partner_id, asset_id, order_type, channel, state, priority, branch_id, business_line_id, sla_policy_id, promised_date, total_cost, total_price |
| `fix.service.order.rental` | `fix_service_order_rental` | Rental-mode extension | rental_agreement_id, swap_required, liability_ref |
| `fix.service.order.msp` | `fix_service_order_msp` | Managed-service extension | msp_contract_id, alert_id, ticket_ref |
| `fix.service.order.data` | `fix_service_order_data` | Data-services extension | data_case_id, confidentiality_level |
| `fix.service.order.marketplace` | `fix_service_order_marketplace` | Marketplace extension | seller_id, offer_id, commission_scheme_id |
| `fix.job.batch` | `fix_job_batch` | Multi-device coordination | name, partner_id, site_id, planned_date |
| `fix.diagnostic.template` | `fix_diagnostic_template` | Decision-tree definition | category_id, brand_id, model_id, symptom_id, tree_json, version |
| `fix.diagnostic.result` | `fix_diagnostic_result` | Recorded diagnosis | order_id, template_id, answers_json, findings, completed_by |
| `fix.fault.code` | `fix_fault_code` | Standard fault taxonomy | code, category, sub_category, description_bn, description_en |
| `fix.sla.policy` | `fix_sla_policy` | SLA definition | service_type, business_line, tier, response_min, resolution_min, calendar_id |
| `fix.sla.clock` | `fix_sla_clock` | Running clock per order | order_id, clock_type, started_at, paused_total_min, breached, breach_at |
| `fix.escalation.rule` | `fix_escalation_rule` | Escalation configuration | sla_policy_id, threshold_pct, role_id, action |
| `fix.hold.reason` | `fix_hold_reason` | Hold reason codes | code, description, suspends_sla |
| `fix.rework.link` | `fix_rework_link` | Rework relationship | original_order_id, rework_order_id, fault_code_id, days_between, attributed_to |
| `fix.service.report` | `fix_service_report` | Customer-facing outcome | order_id, findings, work_done, parts, warranty_terms, document_id |
| `fix.repair.warranty` | `fix_repair_warranty` | Warranty granted on the repair | order_id, asset_id, start_date, end_date, scope, claimed |
| `fix.device.condition.log` | `fix_device_condition_log` | Condition at each event | asset_id, event_type, cosmetic_grade, functional_notes, evidence_ids |

### 10.2 Referenced Entities

| Entity | Owned By | Access Pattern |
|---|---|---|
| `fix.party` | M33 | Live read via API |
| `fix.asset` | M17 / M49 | Live read; writes history events back |
| `fix.contract`, `fix.entitlement` | M08 | Live read for validation |
| `fix.warranty.register` | M09 | Live read for entitlement |
| `fix.quotation` | M36 | Live read; requests creation |
| `fix.checklist.template` | M23 | Live read of template; writes result |
| `fix.part.item`, `fix.stock.reservation` | M15 / M37 | Requests reservation and consumption |
| `fix.work.order` | M02 | Creates; reads status |
| `fix.repair.order` | M31 | Creates; reads status |
| `fix.consignment` | M03 | Requests creation; reads status |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-SRM-01 | Service order confirmed | Evaluate entitlement, assign SLA policy, start clocks, emit acknowledgement event, enter the dispatch queue | Queue for manual completion; alert branch manager |
| AUT-SRM-02 | Diagnosis recorded | Request a draft estimate from M36 using fault code → standard repair mapping | Present a blank estimate for manual build |
| AUT-SRM-03 | Estimate issued | Start the approval timer; remind at 24 h and 48 h; auto-expire at the configured limit | Create a manual follow-up task |
| AUT-SRM-04 | Customer approves | Reserve parts in M15, release the work or repair order, notify the assignee | Create a manual release task |
| AUT-SRM-05 | Parts unavailable network-wide | Raise a sourcing request, place the order on hold, emit a revised-ETA event to the customer | Escalate to inventory manager |
| AUT-SRM-06 | QC passed | Generate the service report, emit the billable event to M20, emit the ready-for-collection event | Create a manual invoice task |
| AUT-SRM-07 | Warranty order delivered | Emit the claim-eligible event to M09 with the evidence pack reference | Create a manual claim task with a checklist |
| AUT-SRM-08 | Order idle beyond threshold | Escalate to branch manager; second escalation to operations manager on non-acknowledgement | Repeat and escalate further |
| AUT-SRM-09 | Same device + fault within 30 days | Raise the rework flag, link the orders, emit the quality event | — |
| AUT-SRM-10 | Device Ready and uncollected | Reminder sequence at 3, 7, 15 and 30 days; then abandonment process with statutory notice | — |
| AUT-SRM-11 | Promised date will be missed | Emit a proactive delay event with a revised commitment | Escalate to branch manager |
| AUT-SRM-12 | Order delivered | Emit the survey trigger event after the configured interval | Retry once, then drop |

---

## 12. Interfaces

### 12.1 Upstream — M01 Consumes

| Source | What | Mechanism |
|---|---|---|
| M33 Party Master | Customer identity, addresses, tier, consent, credit status | REST `GET /api/v1/customer/{id}` |
| M17 Asset Registry | Device identity, specification, history, warranty dates | REST `GET /api/v1/assets/{id}` |
| M08 Contract | Active contracts, covered assets, entitlement balance | REST `GET /api/v1/contracts?asset_id=` |
| M09 Warranty | Warranty status by serial and date | REST `POST /api/v1/warranty/check` |
| M37 Catalogue | Service definitions, standard times, repair kits, fault taxonomy | Master data projection |
| M11 Pricing | Applicable price book for the customer | REST, via M36 |
| M36 Quotation | Estimate document and customer decision | Event `quotation.decided` |
| M23 Quality | Checklist templates applicable to device type and repair level | Master data projection |
| M55 Workforce | Technician availability windows | Event projection |
| M22 Competency | Certification validity for dispatch gating | REST, via M02 |
| M12 Marketplace | Marketplace job award | Event `mp_job.awarded` |
| M05 Managed Services | Alert or ticket requiring field intervention | Event `msp_ticket.escalated` |
| M63 Automation | Scheduled preventive work generation | Scheduled job |

### 12.2 Downstream — M01 Provides

| Consumer | What | Mechanism |
|---|---|---|
| M02 Field Service | Work order with full job context | Command + event `service_order.ready_for_dispatch` |
| M31 Workshop | Repair order with diagnosis and scope | Command + event `service_order.routed_to_workshop` |
| M03 Logistics | Consignment request for collection or delivery | Command |
| M15 Inventory | Parts reservation and consumption requests | Command |
| M09 Warranty | Claim-eligible completion with evidence pack | Event `service_order.completed` |
| M20 Receivable | Billable event on delivery | Event `service_order.delivered` |
| M23 Quality | Rework, QC failure and complaint-linked quality events | Events |
| M27 Contact Centre | Every customer-visible milestone | Events |
| M34 Customer Experience | Survey trigger and satisfaction linkage | Event |
| M25 Business Intelligence | Full order fact stream | Warehouse extract |
| M26 AI/ML | Training data for duration, fault, quality-risk and dispatch models | Warehouse extract |
| P01 Customer Portal | Status, timeline, tracking, approvals | REST + webhook |
| P04 Corporate Portal | Bulk order creation and estate-level status | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Principal Consumers |
|---|---|---|
| `service_order.created` | order id, customer, asset, type, channel, promised date, tracking token | M02, M27, M34, M25 |
| `service_order.classified` | order id, type, entitlement result | M08, M09, M11 |
| `service_order.diagnosed` | order id, fault codes, repair level | M36, M31, M26 |
| `service_order.estimated` | order id, estimate id, total | M27, M36 |
| `service_order.approved` | order id, approved scope and value | M15, M02, M31 |
| `service_order.on_hold` | order id, reason, expected release | M02, M27, M23 |
| `service_order.released` | order id | M02, M31 |
| `service_order.qc_failed` | order id, failed items | M23, M31 |
| `service_order.ready` | order id, collection or delivery mode | M03, M04, M27 |
| `service_order.delivered` | order id, handover evidence, billable summary | M20, M09, M27, M34 |
| `service_order.closed` | order id, final cost and revenue | M25, M33 |
| `service_order.cancelled` | order id, reason | M02, M15, M20 |
| `sla.warning` | order id, clock, threshold percentage | M02, M27, M23 |
| `sla.breached` | order id, clock, breach duration | M08, M23, M53 |
| `rework.detected` | original order, rework order, fault, attribution | M23, M57, M26 |
| `billing.event` | customer, source document, lines, unit price (M11), quantity, dimensions, currency, tax context, idempotency key | M20, M53 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/service-orders` | POST | Create an order | P01, P04, P07, M27, M12 |
| `/api/v1/service-orders/{id}` | GET | Full order detail, authorisation-scoped | All portals |
| `/api/v1/service-orders/{id}/status` | GET | Lightweight status for tracking | P01 |
| `/api/v1/service-orders/{id}/transition` | POST | Execute a state transition with guard evaluation | P02, P03 |
| `/api/v1/service-orders/{id}/hold` | POST | Place on hold with reason | P02, P03 |
| `/api/v1/service-orders/{id}/diagnosis` | POST | Submit diagnostic result | P02 |
| `/api/v1/service-orders/{id}/evidence` | POST | Attach photographs and documents | P02, P09 |
| `/api/v1/service-orders/{id}/handover` | POST | Record handover with signature | P02, P03, P09 |
| `/api/v1/service-orders/{id}/reschedule` | POST | Reschedule within policy | P01, P03 |
| `/api/v1/service-orders/{id}/cancel` | POST | Cancel with reason | P01, P03 |
| `/api/v1/service-orders/search` | GET | Multi-attribute and full-text search | P03, P10 |
| `/api/v1/service-orders/bulk` | POST | Bulk operation submission | P03, P04 |
| `/api/v1/diagnostic-templates` | GET | Template retrieval for offline caching | P02 |
| `/api/v1/tracking/{token}` | GET | Public tokenised tracking view | P01, unauthenticated |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R05 Operations Director | C R U D A | All branches |
| R06 Branch Manager | C R U D A | Own branch |
| R07 Dispatch Manager | C R U | Assigned zones |
| R08 Service Centre Agent | C R U | Own branch |
| R09 Workshop Supervisor | C R U | Own workshop |
| R10 / R11 / R12 Technician | R U | Own assigned orders |
| R13 Remote Support Engineer | C R U | Assigned clients |
| R14 Data Services Technician | R | Own cases only |
| R15 Logistics Coordinator | R | All (movement context) |
| R28 Warranty Claims Officer | R | All warranty orders |
| R27 Finance Officer | R | All (billing context) |
| R32 Quality Manager / ISO Coordinator | R | All |
| R34 Contact Centre Agent | C R U | Customer-facing scope |
| R36 Customer | R U | Own orders only |
| R37 Corporate Portal User | R U | Own company's orders |
| R38 Marketplace Seller | R U | Awarded orders only, time-limited |

**Field-level restrictions:** `unit_cost`, `total_cost` and `margin` are visible only to
R01–R06, R17, R21, R22, R26 and R27. `internal_note` is never exposed to any external portal.

**Segregation of duties:** the technician who performed the repair cannot record the
independent QC above the value threshold (SOD-07).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Live operations board | Dispatch, branch and operations managers | Real time | Open orders by state, age, SLA risk, value; drill to order |
| WIP ageing analysis | Operations Director | Daily | Work in progress by state with cycle time per state and bottleneck identification |
| SLA compliance report | Operations, Quality | Daily / monthly | Attainment by branch, service type, tier and brand, with breach causes |
| Rework analysis | Quality Manager, HR | Weekly | Rework rate by technician, branch, device model and fault code |
| Turnaround time analysis | Operations Director | Weekly | TAT distribution by service type and delivery mode, versus promise |
| Uncollected device report | Branch Manager | Daily | Devices Ready but uncollected, by age, with action status |
| Channel performance | CCO, CTO | Monthly | Order volume, conversion and cost per intake channel |
| Approval conversion | CCO | Weekly | Estimate acceptance rate by value band, device category and branch |
| Fault pattern report | Quality, Brand partners | Monthly | Failure patterns by brand, model and component |
| Service order cost and margin | Finance, Operations | Monthly | Cost roll-up versus revenue by order type and business line |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W8 Target |
|---|---|---|---|---|
| KPI-001 | Service order automation rate | 20% | 65% | **85%** |
| KPI-002 | Average turnaround — IT equipment | unmeasured | < 36 h | **< 24 h** |
| KPI-004 | First-time fix rate | 70% | 82% | **88%** |
| KPI-005 | Rework rate | unmeasured | < 5% | **< 3%** |
| KPI-006 | SLA compliance | unmeasured | 92% | **96%** |
| KPI-007 | QC first-pass rate | unmeasured | 92% | **95%** |
| KPI-008 | Estimate approval conversion | unmeasured | 72% | **78%** |
| KPI-009 | Devices uncollected > 30 days | unmeasured | < 1% | **< 0.5%** |
| KPI-025 | Status enquiries deflected to self-service | 0% | 60% | **80%** |
| KPI-056 | Revenue leakage — delivered but unbilled | unknown | < 1.5% | **< 0.5%** |
| — | Order creation p95 latency | n/a | ≤ 500 ms | ≤ 500 ms |
| — | Orders created without manual entry (digital channels) | 0% | 80% | 90% |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `repair`, `project`, `mail`, `product` | 12% |
| L2 | OCA `fieldservice`, `fieldservice_substatus`, `fieldservice_stage_validation`, `fieldservice_template`, `helpdesk_mgmt`, `helpdesk_mgmt_sla`, `helpdesk_mgmt_priority` | 34% |
| L5 | `cd_service_order`, `cd_diagnostic`, `cd_sla`, `cd_rework`, `cd_service_ext` | 54% |

### 16.2 Custom Development

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-001 | `cd_service_order` — core object, state machine, extensions | Odoo module | 16 PW |
| CD-002 | `cd_diagnostic` — template builder, execution, fault coding | Odoo module | 8 PW |
| CD-003 | `cd_sla` — multi-clock SLA, escalation matrix | Odoo module | 6 PW |
| CD-004 | `cd_rework` — detection, linkage, attribution | Odoo module | 3 PW |
| CD-005 | `cd_service_ext` — business-line extensions | Odoo module | 7 PW |
| CD-006 | Service order API layer and tracking read model | Service | 6 PW |

### 16.3 Sequencing

> ⚠ **Wave inversion — unresolved.** M01 is scheduled in **W1** (P0) but declares a dependency on 1 module(s) that land later: **M17** (W2). One of three things must be true before the W1 gate, and the programme must say which:
>
> 1. the dependency is **not** a true prerequisite for the W1 scope, and §1 overstates it;
> 2. a defined **interim capability** covers the gap (name it, and the wave it retires in); or
> 3. the wave assignment of M01 or of the prerequisite is **wrong** and must change in `06-01`.
>
> Until this is resolved the W1 plan for M01 is not buildable as specified. *(Audit finding A3-07, 2026-08-13.)*

| Prerequisite | Reason |
|---|---|
| M29 Identity | Every order carries an actor and an authorisation scope |
| M28 Integration | Events and APIs are the module's principal interface |
| M33 Party Master | An order cannot exist without a customer |
| M17 Asset Registry | An order cannot exist without a device (BRU-SRM-01) |
| M37 Catalogue | Fault taxonomy and standard times must exist |
| M30 Platform Admin | Branch, zone and calendar configuration must exist |

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Branch service order spreadsheets | ~50,000 open and recent | `fix.service.order` | W1–W2 |
| `station.1000fix.com` order tracking | Unknown, to be profiled | `fix.service.order` (archive) | W2 |
| Legacy tracking portal `123.0.26.238` | Unknown | `fix.service.order` (archive) | W2 |
| Paper service history archive | 500,000+ historical | Archive area, flagged, excluded from operational logic | W2–W6 |

Migrated historical orders retain their legacy reference for lookup and are excluded from
SLA, rework and KPI calculations.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Service orders are created successfully from all twelve intake channels | Demonstration plus transaction log per channel |
| AC-02 | The full lifecycle executes end to end for all nine delivery modes | Nine scripted end-to-end demonstrations |
| AC-03 | Walk-in intake is completed in under three minutes by branch staff, not by the project team | Timed observation, twenty samples across three branches |
| AC-04 | SLA clocks start, pause, resume and breach correctly, including across working-calendar boundaries | Automated test suite plus manual verification |
| AC-05 | Escalations fire at 50/75/90/100% and are acknowledged | Test evidence with acknowledgement records |
| AC-06 | No order can reach Ready without a passed quality checklist, including via API | Negative test through UI and API |
| AC-07 | Rework is detected and linked automatically within the configured window | Scripted scenario |
| AC-08 | Every lifecycle milestone emits its domain event exactly once under retry and failure conditions | Event delivery test with induced failure |
| AC-09 | The public tracking link renders correctly on a 3G connection in under three seconds | Field test |
| AC-10 | All screens and generated documents are complete in Bengali | Translation coverage report at 100% |
| AC-11 | Order creation p95 ≤ 500 ms and operations board ≤ 1 s with 500 open orders | Load test report |
| AC-12 | A field-originated order created offline synchronises with full integrity after 24 hours | Offline test with 24-hour disconnection |
| AC-13 | Migrated historical orders are retrievable by legacy reference and excluded from KPIs | Migration reconciliation report |
| AC-14 | Named business super-users sign off UAT for all P0 and P1 requirements | Signed UAT record |
| AC-15 | Zero critical or high security findings | Security review record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | What is the statutory notice period and disposal process for abandoned devices in Bangladesh? | Legal / Ops Director | W1 build |
| Q-02 | Should the diagnostic fee on a declined repair be waived for Privilege members? | CCO | W1 build |
| Q-03 | What is the repair warranty period by device category and repair level? | Ops Director / Quality | W2 build |
| Q-04 | How far back should the historical service archive be migrated — 3, 5 or all years? | Ops Director / CTO | W2 planning |
| Q-05 | For marketplace-fulfilled orders, does 1000FiX's repair warranty apply or the seller's? | CEO / Legal | W7 (M12) |

---

## 19. References

**Internal**
`03_Modules/A_Service_Delivery_and_Operations/_CATEGORY_OVERVIEW.md` ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` ·
`05_Cross_Cutting_Specifications/05-01_Feature_and_Function_Register.md` ·
`05-02_Data_Model_and_Entity_Catalogue.md` · `05-05_Business_Rules_and_Automation_Catalogue.md` ·
`06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md`

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` §8.1, §10.1, §12 ·
`1000FiX_ERP_System_Comprehensive_URD.md` §6 ·
`1000fix_business/SOW for 1000FiX Service App Development.docx` §Service Management ·
`1000FiX_Services_Company_Profile.md`

**External benchmark**
SAP S/4HANA Service — service order and in-house repair processing ·
Microsoft Dynamics 365 Field Service — case and work order model ·
IFS Cloud Service Management — warranty verification at intake ·
ITIL 4 — incident versus service request distinction ·
Odoo 19 / OCA `fieldservice` and `helpdesk` module families

---

*Module M01 · Category A · 1000FiX ERP System v2.0 · CONFIDENTIAL*
