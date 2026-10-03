---
id: FIX-ERP2-CAT-A
category: A
category_name: Service Delivery & Operations
module_count: 7
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT
---

# Category A — Service Delivery & Operations

**7 modules · Pillar owner: Service Operations Director**

---

## 1. What Belongs in This Category

Everything that happens to a **customer's device or IT estate** from the moment a service
need arises until the work is complete and the device is back in the customer's hands.

If a capability answers *"what work is being done, by whom, where, and to what standard"*,
it belongs here. If it answers *"what does it cost"* or *"who is the customer"*, it does not.

---

## 2. Modules

| ID | Module | Status | Priority | Wave | One-Line Definition |
|---|---|---|:--:|:--:|---|
| **M01** | Service Request & Order Management | Re-scoped | P0 | W1–W2 | Owns the service order — the master record of every customer service need, from any channel, for any business line |
| **M31** | Workshop & Depot Repair Management ★ | New | P1 | W2 | Owns in-house bench repair: workshop routing, Level 1/2/3 repair, RMA-in, component-level work, test and burn-in |
| **M02** | Field Service & Dispatch Management | Re-scoped | P0 | W2 | Decides who does field work, when and in what order; tracks and executes it on mobile |
| **M03** | Service Logistics & Reverse Logistics | Retained | P1 | W3 | Moves devices, parts and assets between customers, branches, workshops, vendors and recyclers with unbroken custody |
| **M04** | Branch & Front-Desk Operations | Retained | P1 | W1 | Runs the counter at 51+ service centres: queue, intake, handover, cash, shift discipline |
| **M05** | Remote Support & Managed Services | Retained | P1 | W5 | Delivers remote assistance and contracted managed IT services with monitoring, alerting and SLA reporting |
| **M06** | Data Services & Secure Data Handling | Retained | P2 | W6 | Delivers data recovery, backup subscriptions, migration and certified destruction under controlled custody |

★ = new in v2.1 after enterprise benchmarking.

### 2.1 Measured Scale

> Counted directly from the seven specification files on **2026-08-13** under rule **RG-06**
> (count, do not consult). These figures supersede the 388 recorded in `05-01` §1.3a and the
> 362 recorded in `02-02`, both of which were derived from the **highest allocated identifier**
> rather than a count of requirement rows. *(Audit finding A3-01.)*

| Module | Code | Requirements | Effort |
|---|---|---:|---:|
| M01 | `SRM` | 70 | 46 PW |
| M31 | `WSR` | 53 | 30 PW |
| M02 | `FSM` | 63 | 40 PW |
| M03 | `LOG` | 42 | 22 PW |
| M04 | `FRD` | 31 | 13 PW |
| M05 | `RMS` | 62 | 37 PW |
| M06 | `DTS` | 34 | 18 PW |
| **Total** | | **355** | **206 PW** |

**35 allocated requirement identifiers in this category are retired unused** — 18 in M01, 11 in
M02, 5 in M31 and 1 in M04. They are listed in each module's §5 and are never reissued (RG-02).

---

## 3. Why M01 and M31 Are Separate

This is the most important boundary in the category, and the one enterprise systems get
right that the v2.0 draft did not.

| | M01 Service Request & Order Management | M31 Workshop & Depot Repair |
|---|---|---|
| **Owns** | The customer-facing service order: what the customer asked for, what was promised, what it will cost, what state it is in | The internal repair execution inside a workshop: which bench, which technician, which components, which tests |
| **Analogue** | SAP *Service Order Management* · Dynamics 365 *Case/Work Order* · IFS *Service Request* | SAP *In-House Repair* · IFS *Repair Shop* · Rootstock/QAD *Depot Repair* |
| **Lifecycle** | Received → Diagnosing → Awaiting Approval → In Progress → Ready → Closed | Booked in → Bench assigned → Diagnosed → Under repair → Tested → Released |
| **Customer sees** | Yes — the tracking timeline is M01 | No — internal only |
| **Cardinality** | One per customer request | Zero or many per service order (a device may go to two workshops) |

**Rule:** M01 never contains bench-level detail. M31 never talks to the customer.
The bridge is the `repair_order` object M31 owns, linked to M01's `service_order`.

---

## 4. Category Boundary Map

| Capability | Owned By | Not Owned By |
|---|---|---|
| Customer identity | **M33** | M01 (references only) |
| Device identity and history | **M17** | M01, M31 (reference only) |
| Estimate and price | **M36** quotation, **M11** pricing | M01 (displays, does not calculate) |
| Contract entitlement | **M08** | M01 (validates against) |
| Warranty entitlement | **M09** | M01 (validates against) |
| Parts stock and consumption cost | **M15** | M31 (requests and consumes, does not value) |
| Technician shift availability | **M55** | M02 (consumes, does not maintain) |
| Technician competency | **M22** | M02 (enforces gate, does not certify) |
| Invoice | **M20** | M01 (triggers, does not create) |
| Quality checklist definition | **M23** | M01, M31 (execute, do not author) |
| Customer notification delivery | **M27** | All (raise events, do not send) |
| Vehicle and van | **M46** | M02, M03 (use, do not manage) |

---

## 5. The Nine Service Delivery Modes

Every module in this category must support all nine. A mode is configuration, not code.

| # | Mode | Primary Modules | Notes |
|---|---|---|---|
| 1 | Walk-in at service centre | M04 → M31 | Highest volume |
| 2 | On-site / home service | M01 → M02 | Appliance and corporate |
| 3 | Pick & drop | M01 → M03 → M31 → M03 | Custody-critical |
| 4 | Remote support | M01 → M05 | Software and configuration faults |
| 5 | Workshop / depot repair | M31 | Board-level and specialist |
| 6 | Preventive / scheduled maintenance | M08 → M02 | Contract-driven |
| 7 | Managed-service incident | M05 → M02 | Alert-driven |
| 8 | Marketplace-fulfilled | M12 → M01 → M02 | External seller executes |
| 9 | Data services | M06 | Confidentiality-controlled |

---

## 6. Shared Lifecycle Vocabulary

All seven modules use one vocabulary. Divergence is a defect.

| Term | Definition | Owned By |
|---|---|---|
| **Service order** | The customer's request, one per need | M01 |
| **Work order** | An assignable unit of field work | M02 |
| **Repair order** | An assignable unit of workshop work | M31 |
| **Consignment** | A movement of physical items with custody | M03 |
| **Queue token** | A walk-in customer's place in line | M04 |
| **MSP ticket** | A contracted client's support request | M05 |
| **Data case** | A confidentiality-controlled data engagement | M06 |
| **Visit** | One physical attendance at a location | M02 |
| **Custody event** | A transfer of physical possession | M03 (shared) |

---

## 7. Category KPIs

| KPI | Baseline | Target | Owning Module |
|---|---|---|---|
| Service order automation rate | 20% | 85% | M01 |
| Average turnaround — IT equipment | unmeasured | < 24 h | M01 / M31 |
| Average turnaround — appliance on-site | unmeasured | < 4 h | M02 |
| First-time fix rate | 70% | 88% | M02 / M31 |
| Rework rate | unmeasured | < 3% | M01 |
| Jobs per technician per day | 4–5 | 8–9 | M02 |
| Walk-in intake time | ~10 min | < 3 min | M04 |
| Workshop throughput per bench per day | unmeasured | baseline +40% | M31 |
| Chain-of-custody exceptions | untracked | 0 | M03 |
| Remote resolution rate (no site visit) | 0% | 65% | M05 |
| Data-services custody exceptions | n/a | 0 | M06 |

---

## 8. Category Delivery Sequence

```
W1   M04 Branch & Front-Desk ──┐
     M01 Service Order (core) ─┴──► first transactions
W2   M31 Workshop ─────────────┐
     M02 Field Service ────────┴──► full service execution
W3   M03 Logistics ───────────────► pick & drop, custody
W5   M05 Managed Services ────────► MSP business line
W6   M06 Data Services ───────────► data business line
```

---

## 9. Category Risks

| Risk | Impact | Mitigation | Owning Module |
|---|---|---|---|
| Technician rejects the mobile app | Critical — the field model collapses | Bengali-first, extreme simplicity, field pilot, earnings visibility | M02 |
| Workshop staff keep parallel paper WIP boards | High — no real-time visibility | Bench board on a wall-mounted screen; QC gate cannot be bypassed | M31 |
| Counter intake slower than paper | High — branch resistance | 3-minute intake is a hard design constraint, measured | M04 |
| Custody breaks in pick & drop | High — legal exposure on lost devices | Scan-plus-identity at every handover, no exceptions | M03 |
| Data-services confidentiality breach | Critical — regulatory and reputational | Least privilege, dual control, field encryption, full audit | M06 |

---

*Category A · 1000FiX ERP System v2.0*
