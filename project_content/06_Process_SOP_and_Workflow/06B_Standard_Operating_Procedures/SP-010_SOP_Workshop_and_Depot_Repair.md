---
id: SP-010
title: SOP — Workshop and Depot Repair
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Workshop Operations
author: Business Process Lead with Workshop Operations
reviewers: [Operations Director, Workshop Supervisors, Quality Manager, Inventory Manager, HSE Lead, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Workshop throughput and rework rate are the largest determinants of service margin. This SOP
  governs bench assignment, work-in-progress control, L1/L2/L3 escalation, parts holds, the
  quality gate and release. A service order cannot reach Completed unless its quality checklist
  is recorded as passed; the workshop is where that gate is either a real control or a formality.
traces_to: [M31, M01, M15, M23, P03, DT-003, DT-004, DT-008, MD-025, SP-004, SP-005, SP-013, SP-016, SP-029]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: SP-010_SOP_Workshop_and_Depot_Repair_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md — including FR-WSR-053 device security and overnight high-value segregation
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-04, -06, -11, -12, -14, -17, -18, -19
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-002 TAT, KPI-005 rework rate, KPI-007 QC first-pass rate
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.6 release of products and services, and clause 8.7 control of nonconforming outputs
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Workshop and Depot Repair

| Item | Value |
|---|---|
| SOP ID | `SP-010` |
| Process owner | Operations Director (R05); executed under Workshop Supervisor (R09) |
| Roles performing | `R09` Workshop Supervisor · `R10` Senior Technician · `R11` Junior Technician · `R12` Specialist Technician (L3) · `R18` Branch Store Keeper · `R32` Quality Manager |
| Systems used | `P03` Workshop console (`UI-026`) · `M31` · `M01` · `M15` · `M23` |
| Frequency / volume | Continuous across the workshop network; the throughput constraint of the whole service business |
| ISO 9001 clause reference | **8.6** release · **8.7** nonconforming outputs · 8.5.1 controlled conditions · 7.1.5 monitoring and measuring resources (calibrated test equipment) |

---

## 1. Purpose and Outcome

**Purpose.** To convert a diagnosed device into a repaired, tested, quality-passed device within
the turnaround commitment, with parts and time accounted, and with a defensible record of what
was done.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The fault, not a symptom, was resolved | Test result recorded against the original fault code |
| The quality checklist passed **before** the order reached Completed | `BRU-SRM-04`, `DT-008` |
| Parts consumed reconcile to parts issued | `M15` consumption record |
| Time booked reconciles to time available | Bench utilisation report |
| Turnaround was inside the SLA band | `KPI-002`, `KPI-003` |
| The device did not come back for the same fault within 30 days | `KPI-005` rework rate |

---

## 2. Scope

**Applies to:** all bench repair at a branch workshop, a regional depot or the central workshop,
at levels L1 (component swap), L2 (module-level) and L3 (board-level), for consumer, corporate,
warranty, AMC and refurbishment work.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Repair at the customer's premises | `SP-008` |
| Data recovery and secure data handling | `SP-012` — the device is **not opened** in the general workshop |
| Refurbishment grading of company-owned stock | `SP-025` |
| Rental asset servicing between hires | `SP-027` |
| Estimate construction and customer approval | `SP-013` |
| Movement of devices between sites | `SP-009` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| WIP | Work in progress — devices open on a bench or awaiting action inside the workshop |
| Bench | A designated, equipped work position with an assigned technician |
| L1 / L2 / L3 | Repair depth: component swap / module-level / board-level. L3 requires a certified specialist and equipped workshop (`BRU-SRM-14`) |
| Parts hold | A job suspended awaiting a part; the SLA clock pauses only on an approved hold reason (`BRU-SRM-15`) |
| QC gate | The mandatory independent check before release (`DT-008`) |
| Rework | A repeat order for the same device and fault category within 30 days (`BRU-SRM-06`) |
| BER | Beyond economic repair |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Service order in the workshop queue | `M01` | Device physically present and located (`SP-007` or `SP-009`) |
| Diagnosis recorded | `SP-008` or workshop triage | Fault code from `MD-024` present |
| Approved estimate where work is chargeable | `SP-013` | **Parts cannot be issued against an unapproved paid repair** (`BRU-SRM-11`) |
| Technician certified to the required level | `M22` | L3 work requires a certified specialist (`BRU-SRM-14`); brand warranty requires current brand certification (`BRU-SRM-09`) |
| Test equipment calibrated | `MD-046` | An out-of-calibration instrument voids every measurement taken with it |
| ESD-safe bench and tooling | `M47` | Static damage is invisible at the bench and appears as a field failure |
| Parts available or a hold reason approved | `M15` | Otherwise the job is held, not started |

---

## 5. Procedure

### 5.1 Queue to bench

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R09 | Review the queue by SLA risk, not arrival order. Jobs at 75% of SLA take precedence (`AUT-009`) | `P03` workshop console | Queue sequenced | 10 min/shift |
| 2 | R09 | Assign to a bench and a technician matched to the repair level and brand certification | `P03` | Assignment recorded | 1 min |
| 3 | R10–R12 | Collect the device from the secured store against a scan | `P03` · `M15` | Custody scan | 1 min |
| 4 | R10–R12 | Verify the device against the order — serial, model, declared fault, intake photographs | `P03` | Verification recorded | 2 min |

### 5.2 Repair

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 5 | R10–R12 | Confirm or refine the diagnosis at the bench. Where it differs from intake, record why | `P03` · `MD-024` | Confirmed fault code, `DT-004` | 10–30 min |
| 6 | R10–R12 | Where the confirmed work exceeds the approved estimate, **stop** and raise a revision (`SP-013`) | `P03` | `DT-006` revision | — |
| 7 | R10–R12 | Requisition parts against the order. Serialised parts are scanned at issue (`BRU-INV-08`) | `P03` · `SP-016` | Parts issued to the order | 5 min |
| 8 | R10–R12 | Photograph the device before opening it — internal condition, prior repair evidence, corrosion, liquid indicator | `P03` capture | Before-photographs (mandatory on warranty, `BRU-SRM-17`) | 2 min |
| 9 | R10–R12 | Perform the repair at the certified level. Use the repair action codes from `MD-025` | `P03` | Repair actions recorded | Varies |
| 10 | R10–R12 | Book time against the order as work proceeds, not retrospectively at the end | `P03` | Time record | Continuous |
| 11 | R10–R12 | Test against the **original reported fault** and run the standard functional test set for the device class | `P03` test panel | Test results | 10 min |
| 12 | R10–R12 | Photograph the completed work; reassemble; clean | `P03` capture | After-photographs | 5 min |
| 13 | R10–R12 | Return unused parts to store; record consumption accurately | `SP-016` | Return record | 3 min |
| 14 | R10–R12 | Submit for QC | `P03` | Status: Awaiting QC | 1 min |

### 5.3 Quality gate and release

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 15 | R09 or R32 — **not the repairing technician** | Perform the QC checklist for the service category. Mandatory independent QC above BDT 25,000 (`BRU-SRM-18`, `SOD-07`) | `P03` · `M23` | `DT-008` quality checklist record |
| 16 | R09 / R32 | On failure: return to the bench with the reason coded; the job re-enters repair, not release (ISO 8.7) | `P03` | Nonconformity recorded → `SP-029` |
| 17 | R09 | On pass: release. `AUT-008` generates `DT-007` and raises the invoice | `P03` | Order Completed; invoice raised |
| 18 | R18 | Move the device to the ready-for-collection store, secured and located | `M15` | Location recorded |
| 19 | System | Notify the customer that the device is ready; the uncollected reminder sequence begins (`AUT-012`) | `NT-*` | Notification sent |

### 5.4 Daily workshop discipline

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 20 | R09 | WIP review at shift start: every open job aged, every hold justified, every SLA risk flagged | `SP-032` |
| 21 | R09 | Bench audit: ESD compliance, tool control, calibration dates current | `MD-046`, `SP-032` |
| 22 | R09 | **High-value devices held overnight are segregated into secured storage** and counted at shift end | `M31` FR-WSR-053 |
| 23 | R09 | Close the shift: WIP count reconciles to the system, exceptions recorded | `SP-032` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 4 | Device does not match the order | Stop. Do not open. Trace the custody chain (`SP-009`) | R09 → R06 |
| 5 | Diagnosis materially differs from intake | Record both, notify the customer through the estimate revision path | R09 |
| 5 | Fault is not reproducible | Run the extended test set, record it, and contact the customer for usage conditions. **Do not return a device as "no fault found" without a recorded extended test** | R09 |
| 6 | Work exceeds the approved estimate | Stop and revise at the cumulative band (`SP-004` A-05, `BRU-SRM-08`) | Per band |
| 7 | Parts not available | Place on hold with an approved reason; the SLA clock pauses (`BRU-SRM-15`); check network stock (`AUT-007`); inform the customer with a revised ETA | R17 via `SP-016` |
| 7 | Only a brand-supplied warranty part is available and the job is not warranty | **Blocked** (`BRU-WTY-04`) — no override | — |
| 9 | Repair requires L3 and the technician is L1/L2 | Stop. Route to a certified specialist at an equipped workshop (`BRU-SRM-14`) | R09 |
| 9 | Device is beyond economic repair | Photograph, record, obtain **a second technician's confirmation** (`BRU-SRM-12`), then advise the customer with options | R09 + second technician (`SP-004` A-06) |
| 9 | Battery swelling, liquid ingress, or thermal event at the bench | **Stop; isolate; evacuate the bench if necessary.** Safety precedes throughput | HSE + R09, `SP-030` |
| 11 | Repair passes the functional test but the original symptom persists | It is not fixed. Do not submit for QC | R10–R12 |
| 15 | QC fails twice on the same job | Escalate to R32 Quality Manager; the job may not go round a third time without review | R32 |
| 15 | No independent person is available for QC | The job waits. **Self-QC above the threshold is not permitted** (`SOD-07`); use the remote photographic review compensating control (`SP-006` §4.6) | R09 → R06 |
| 17 | Repeat order for the same device and fault within 30 days | Rework flagged automatically (`BRU-SRM-06`); cost attribution per `SP-013`; notify the original technician's manager | R32 |
| 19 | Device uncollected at 30 days | Abandonment process with statutory notice begins (`BRU-SRM-16`) | R06 + Legal (`SP-004` A-10) |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Revised estimate | Cumulative crosses BDT 25,000 | Customer + R06 Branch Manager | R05 |
| Revised estimate | Cumulative crosses BDT 100,000 | Customer + R05 Operations Director | CCO |
| Beyond economic repair declaration | Any | R09 + a second technician (`SP-004` A-06) | R05 |
| Reopen a closed order outside the repair warranty period | Any | R06 Branch Manager (`BRU-SRM-19`, class **A**) | R05 |
| Parts issue against an unapproved paid repair | **None — class H, no override** (`BRU-SRM-11`) | — | — |
| QC waiver | **None — class H, no override** (`BRU-SRM-04`) | — | — |
| Release a device with a known residual defect the customer has accepted | Any | R09, with the customer's written acceptance recorded on `DT-007` | R06 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Device damaged during repair | Stop, photograph, inform R09 immediately, inform the customer the same day. **Do not attempt a silent repair** | R09 → R06; `SP-028` | Nonconformity + ISO 8.5.3 loss report |
| Device lost inside the workshop | Full WIP count, custody trace, escalate as a custody incident from the outset | R09 → R06 → R05 | Loss record |
| Test equipment found out of calibration | Quarantine the instrument; **identify and re-test every job it touched since the last valid calibration** | R32, R09 | Nonconformity (`MD-046`, `SOD-52`) |
| Counterfeit or non-genuine part discovered | Quarantine; do not fit; report to procurement | R17, R19, R32 | Vendor nonconformity (`M42`) |
| Thermal event, smoke or fire at the bench | Evacuate; emergency response; `SP-030`. **L4-direct escalation** | HSE, R05, CEO | Safety incident |
| WIP count does not reconcile at shift close | Do not close the shift. Recount, then escalate | R09 → R06 | WIP exception record |
| `P03` unavailable | Fallback in §9 | R09, R33 via `SP-031` | Paper job cards |
| Rework rate above the configured threshold for a bench or technician | Raise a quality event; retraining or re-certification assessed | R32 → `SP-029`, `M22` | CAPA |
| Customer chases a device that has no recorded location | Treat as a custody incident, not an enquiry | R09 → R06 | Custody exception |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | R09 maintains a **whiteboard WIP board** mirroring bench, order number, device, status and SLA due — this exists permanently as a visual control, not only during an outage |
| 2 | Each job travels on the printed `DT-003` job card; where the printer is unavailable, use a **pre-numbered manual job card** |
| 3 | Parts issue is recorded on the **manual store issue book**, countersigned by R18 |
| 4 | QC is recorded on the **paper `DT-008` checklist**, signed by the checker — QC is never skipped during an outage |
| 5 | Photographs are taken on a workshop-issued camera; references noted on the job card |
| 6 | **Back-enter every job card, parts issue and QC record within 24 hours**, preserving original timestamps |
| 7 | R09 reconciles paper records against the system and signs the reconciliation; R32 samples the QC records |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Order cannot reach Completed without a passed QC checklist | Preventive (`BRU-SRM-04`) | Per job | Hard block |
| Independent QC mandatory above BDT 25,000 | Preventive (`BRU-SRM-18`, `SOD-07`) | Per job | Hard block |
| Parts cannot be issued against an unapproved paid repair | Preventive (`BRU-SRM-11`) | Per issue | Hard block |
| Brand warranty parts cannot be consumed on non-warranty jobs | Preventive (`BRU-WTY-04`) | Per issue | Hard block |
| L3 work restricted to certified specialists at equipped sites | Preventive (`BRU-SRM-14`) | Per assignment | Hard block |
| Before/after photographs mandatory on warranty jobs | Preventive (`BRU-SRM-17`) | Per warranty job | Cannot close |
| Serialised parts scanned at issue and at consumption | Preventive (`BRU-INV-08`) | Per part | Hard block |
| High-value devices segregated and counted overnight | Preventive | Daily | Secured-store count |
| Calibration dates verified at bench audit | Preventive | Daily / per `MD-046` cadence | Calibration register |
| WIP aged report and hold justification | Detective | Daily | WIP review record |
| QC first-pass rate by technician | Detective | Weekly | `KPI-007` |
| Rework analysis by device, fault and technician | Detective | Monthly | `KPI-005` → `SP-029` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Perform the repair | Record the independent QC (`SOD-07`) | Hard block above threshold | At single-technician sites, remote photographic QC review by R09 at another site |
| Issue parts from store | Approve the resulting stock adjustment (`SOD-05`, `SOD-45`) | Hard block | Adjustment approval routes to R17 Inventory Manager |
| Perform a calibration | Approve a change to that instrument's calibration status (`SOD-52`) | Hard block | — |
| Perform a CAPA action arising from a workshop nonconformity | Verify its effectiveness (`SOD-19`) | Hard block | Verification by R32 or an independent auditor |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-002` | Average TAT — IT equipment | unmeasured | < 36 h; stretch < 24 h |
| `KPI-005` | Rework rate | unmeasured | < 5%; stretch < 3% |
| `KPI-007` | QC first-pass rate | unmeasured | 92%; stretch 95% |
| `KPI-009` | Devices uncollected > 30 days | unmeasured | < 1%; stretch < 0.5% |
| `KPI-043` | Part availability at first request | unmeasured | 88%; stretch 93% |
| `KPI-044` | Stockout-caused job delays | unmeasured | < 6%; stretch < 3% |
| Bench utilisation | Booked time as a proportion of available bench hours | unmeasured | To be set from `SP-002` baseline |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-003` Job Card and Work Order Print | Travels with the device |
| `DT-004` Diagnostic and Condition Report | Produced at step 5 |
| `DT-008` Quality Checklist Record | The gate at step 15 |
| `DT-007` Service Completion Report | Produced on release |
| `UI-026` Workspace — Workshop Console Copy | The screens used |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Estimate revision at step 6; rework classification |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Parts at steps 7 and 13 |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Nonconformity and CAPA |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Thermal events and battery handling |
| [`SP-032_Operational_Checklist_Library.md`](SP-032_Operational_Checklist_Library.md) | Bench audit and shift close |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Repair action coding |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Calibration control |
| `TR-010` Course Pack — Workshop Supervisor | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] The QC gate is stated as a hard block with no override path
- [x] L3 and certification constraints stated at the decision points
- [x] Calibration failure path includes retrospective re-test of affected jobs
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback keeps QC in force during an outage
- [x] Segregation of duties cites `SP-006`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
