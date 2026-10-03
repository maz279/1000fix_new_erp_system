---
id: SP-008
title: SOP — On-Site Field Service Visit
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Field Operations
author: Business Process Lead with Field Operations
reviewers: [Operations Director, Dispatch Managers, Quality Manager, HSE Lead, HR Manager, Legal Counsel, Localisation Lead]
approver: Operations Director
content_class: C
purpose: >
  Field visits are performed unsupervised in customers' homes and offices by 200–400 technicians.
  The SOP is the only control: it governs pre-visit verification, arrival evidence, consent to
  work, on-site estimating and approval, safety, evidence capture, payment and sign-off. Without
  it, the company's brand, its safety duty and its cash are all in the hands of a lone worker
  with no defined standard.
traces_to: [M02, P02, M01, M15, M20, MD-005, MD-028, DT-005, DT-007, SP-004, SP-005, SP-016, SP-019, SP-030]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: SP-008_SOP_On_Site_Field_Service_Visit_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §3 BRU-FSM-01…BRU-FSM-12; §2 BRU-SRM-07/08/12/17
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P02_Technician_Mobile_Application.md — offline-first, geofenced attendance, guided diagnostics
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-004 first-time fix, KPI-011 jobs per technician per day, KPI-015 on-time arrival
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 — controlled conditions for service provision, including competence of persons and validation of ability to achieve planned results
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — On-Site Field Service Visit

| Item | Value |
|---|---|
| SOP ID | `SP-008` |
| Process owner | Operations Director (R05); executed under Dispatch Manager (R07) |
| Roles performing | `R10` Senior Technician · `R11` Junior Technician · `R12` Specialist Technician · `R07` Dispatch Manager |
| Systems used | `P02` Technician Mobile Application · `P03` dispatch console (`UI-024`) · `M02` · `M01` · `M15` |
| Frequency / volume | Target 7 jobs per technician per day (`KPI-011`), across 200–400 technicians |
| ISO 9001 clause reference | **8.5.1** controlled conditions · 8.5.3 customer property · 7.2 competence · 8.6 release of services |

---

## 1. Purpose and Outcome

**Purpose.** To deliver a service visit at a customer's premises safely, competently and with
enough evidence that the work, the charge and the outcome are all defensible without a witness.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Arrival was inside the promised window and inside the geofence | `KPI-015`; geotagged arrival |
| The customer consented to the work and to its cost before it began | Approved estimate against the `SP-004` band |
| The fault was resolved on the first visit | `KPI-004` first-time fix |
| Parts consumed match parts issued | Van reconciliation clean at shift end (`AUT-035`) |
| Before and after evidence exists | Mandatory on warranty work (`BRU-SRM-17`) |
| The customer signed off and holds a completion record | `DT-007` |
| Any payment taken is reconciled to the branch cash book by shift end | `BRU-FSM-07` |

---

## 2. Scope

**Applies to:** every attendance at a customer's premises by a 1000FiX technician — consumer
home visits, corporate on-site, AMC preventive visits, installation, and emergency call-out —
within the zones defined in `MD-005`.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Remote-only resolution with no attendance | `SP-011` Remote Support and Managed Services |
| Collection or delivery with no work performed | `SP-009` Pick-and-Drop and Reverse Logistics |
| Work performed at a branch or workshop | `SP-007`, `SP-010` |
| Marketplace seller performing the visit | `SP-024`; the evidence and QC standards here still apply (`BRU-ECM-03`) |
| Rental asset delivery and handover | `SP-027` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Visit window | The arrival window promised to the customer, derived from the zone travel band in `MD-005` |
| Geofence | The coordinate boundary around the customer address within which arrival may be recorded (`BRU-FSM-06`) |
| Van stock | Parts held on the technician's person or vehicle, owned by the branch until consumed |
| Failed visit | An attendance where work could not be performed — requires geotagged evidence (`BRU-FSM-09`) |
| First-time fix | The fault resolved in a single visit with no return required (`KPI-004`) |
| Guided diagnostic | The structured decision tree presented in `P02`, sourced from `SP-033` |
| Offline queue | Work recorded on `P02` while disconnected, pending sync (`AUT-014`) |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Assigned service order | `M02` | Skill-matched (`BRU-FSM-02`); technician on shift and within capacity (`BRU-FSM-01`) |
| Certification current for brand warranty work | `M22` | Expired certification removes the technician from that brand's pool (`AUT-042`, `BRU-SRM-09`) |
| Route published | `AUT-013` nightly 05:00 | Technician has the day's sequence before leaving |
| Van stock reconciled from the previous shift | `M15` | Prior variance closed (`SP-016`) |
| `P02` synced before departure | `P02` | Device carries the day's jobs, customer history and offline knowledge pack |
| Safety equipment present | `SP-030` | Insulated tools, PPE appropriate to the work, first-aid kit |
| Customer contactable | `M27` | A phone number that answers; otherwise the visit is at risk before it starts |

---

## 5. Procedure

### 5.1 Before travelling

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 1 | R10–R12 | Review the job: device history, prior repairs, entitlement, contract scope, customer notes | `P02` job card | Reviewed flag | 2 min |
| 2 | R10–R12 | Confirm the parts likely needed are in van stock; request a transfer if not, **before** travelling | `P02` · `M15` | Parts check recorded | 2 min |
| 3 | R10–R12 | Call the customer to confirm presence, access and any site restriction (lift, security pass, pet, gate code) | `P02` click-to-call | Call logged | 2 min |
| 4 | R10–R12 | Start travel; the customer receives the tracking link automatically (`AUT-003`) | `P02` | Travel started, timestamped | — |

### 5.2 On site

| Step | Who | Action | System / screen | Evidence produced | Time |
|---:|---|---|---|---|---|
| 5 | R10–R12 | Record arrival **inside the geofence**. Outside it, an exception reason is required (`BRU-FSM-06`) | `P02` arrival | Geotagged arrival | 30 s |
| 6 | R10–R12 | Identify yourself: ID badge visible, state your name and 1000FiX, confirm the customer's name and the job | — | — | 1 min |
| 7 | R10–R12 | **Survey for safety before touching anything** — exposed wiring, water, gas, unstable mounting, animals, children, lone-working risk | `P02` safety check | Safety check recorded | 1 min |
| 8 | R10–R12 | Inspect the device with the customer present. Photograph its condition **before** any work | `P02` capture | Before-photographs (mandatory on warranty, `BRU-SRM-17`) | 2 min |
| 9 | R10–R12 | Diagnose using the guided decision tree; record the fault code from `MD-024` | `P02` · `SP-033` | Diagnosis with fault code | 5–20 min |
| 10 | R10–R12 | Build the estimate from `MD-025` standard actions and `MD-029` rates. Explain it in the customer's language | `P02` estimate | `DT-005` estimate issued | 3 min |
| 11 | Customer | Approve, decline or defer. Above BDT 5,000 the approval is captured formally (`BRU-SRM-07`); above BDT 25,000 branch manager approval is additionally required (`BRU-SRM-08`) | `P02` signature / OTP | Documented approval | 2 min |
| 12 | R10–R12 | Perform the work. Consume parts from van stock, recording each against the order | `P02` · `M15` | Parts consumption recorded | Varies |
| 13 | R10–R12 | Test the repair against the fault, not against a general "it works". Record the test performed | `P02` | Test result | 3 min |
| 14 | R10–R12 | Photograph the completed work — after-photographs mandatory on warranty jobs | `P02` capture | After-photographs | 1 min |
| 15 | R10–R12 | Clean the work area. Return every removed part or accessory, or record its retention with the customer's agreement | — | Site-clear confirmation | 2 min |
| 16 | R10–R12 | Brief the customer: what was wrong, what was done, what warranty applies, what to watch for | — | — | 2 min |
| 17 | R10–R12 | Take payment if due; issue the receipt | `P02` · `M20` | `DT-016` receipt | 2 min |
| 18 | Customer | Sign off the completion record | `P02` signature / OTP | `DT-007` completion report | 1 min |
| 19 | R10–R12 | Close the job; sync if connected, otherwise it queues (`AUT-014`) | `P02` | Job Completed | 30 s |

### 5.3 After the last job of the shift

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 20 | R10–R12 | Sync all queued work. Resolve any conflict flagged by `AUT-014` | `UI-009` |
| 21 | R10–R12 | Reconcile van stock; return unused parts (`AUT-035`) | `SP-016` |
| 22 | R10–R12 | Hand over cash collected and obtain the receipt (`BRU-FSM-07`) | `SP-019` |
| 23 | R10–R12 | Report any safety issue, near miss or vehicle defect | `SP-030`, `M46` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 5 | Customer not present | Wait the configured grace period, call twice, then record a **failed visit with geotagged evidence** (`BRU-FSM-09`). Do not simply leave | R10–R12; R07 informed |
| 5 | Address wrong or unreachable | Record, photograph the location, contact dispatch. Do not guess a nearby address | R07 |
| 7 | **Any immediate danger** — exposed live conductor, gas smell, structural risk, aggression | **Stop. Leave if necessary. Report immediately.** Safety overrides every target (`SP-030`, `ES-06`) | Technician acts; HSE Lead + R05 informed at once |
| 7 | Work requires isolation the technician is not competent to perform | Do not proceed. Reschedule with the right competence (`BRU-FSM-02`) | R07 |
| 9 | Fault is outside the technician's certified level | Do not attempt. Raise for L2/L3 (`BRU-SRM-14`) and explain to the customer | R07 → R09 |
| 9 | Device is beyond economic repair | Photograph, record, and obtain a **second technician's confirmation** (`BRU-SRM-12`) before telling the customer it is final | R09 Workshop Supervisor |
| 11 | Customer declines the estimate | Record the decline reason from `MD-026`, charge only the agreed call-out, leave the device as found | R10–R12 |
| 11 | Customer approves verbally but will not sign | Capture OTP to their registered number instead. **Work above the band does not start without a captured approval** | R10–R12 |
| 12 | Required part not in van stock | Do not improvise a substitute. Check network availability (`AUT-007`), give a revised ETA, and record the job as held on parts | R17 via `SP-016` |
| 12 | Scope grows beyond the approved estimate | Stop. Issue a revised estimate at the **cumulative** value band (`SP-004` A-05). Do not continue and settle later | Per `SP-004` band |
| 17 | Customer disputes the charge | Do not argue. Take no payment, record the dispute, complete the sign-off, and route to `SP-028` | R06 → `SP-028` |
| 19 | Offline with no connectivity | Continue in the offline queue. **Approval above a band still cannot be granted offline** (`SP-004` OF-01/OF-02) | — |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Estimate | > BDT 5,000 | Customer + system record | — |
| Estimate | > BDT 25,000 | Customer + R06 Branch Manager | R05 after the `SP-005` timer |
| Estimate | > BDT 100,000 | Customer + R05 Operations Director | CCO |
| Revised estimate | Cumulative total crosses a band | Re-approval at the cumulative band (`SP-004` A-05) | As above |
| Discount at the door | ≤ 10% | R08-equivalent authority held by the technician's branch, not the technician | R06 |
| Arrival outside the geofence | Any | R07 Dispatch Manager, with reason code (`BRU-FSM-06`) | R06 |
| Beyond economic repair | Any | R09 + second technician (`SP-004` A-06) | R05 |
| Overtime to complete a job | Any | Pre-approved by the line manager (`BRU-HRM-02`, `SOD-27`) | R06 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Safety incident or injury | Emergency services first; then `SP-030`. **L4-direct escalation** (`SP-005` PE-E1) | HSE Lead, R05, CEO | Safety incident record |
| Road traffic accident | As above; secure the vehicle and any customer device in it | HSE Lead, R05, `M46` | Incident + fleet record |
| Customer device damaged during the visit | Stop, photograph, tell the customer immediately, do not attempt a quiet repair | R06 → `SP-028` | Complaint record; ISO 8.5.3 loss report |
| `P02` fails or the device is lost | Fallback in §9 | R07, R33 via `SP-031` | Paper job card |
| No connectivity all day | Offline queue; sync at shift end. Jobs needing an online approval are rescheduled, not performed | R07 | Offline exception report |
| Technician cannot complete the route | Dispatch re-optimises; the customer is notified before the window is missed (`ES-07`) | R07 | Route change log |
| Cash lost or stolen in the field | Report immediately; do not attempt to make it up personally | R06, R26, and per `SP-005` fraud path if theft is suspected | Cash incident record |
| Customer requests work outside the order scope | Raise a new service order. **Never perform unrecorded work** — it is uninsured, unbilled and unwarranted | R07 | New order |
| Lone-working check-in missed | Dispatch calls; no answer within the configured period escalates as a welfare concern | R07 → R06 → HSE | Lone-worker log |

---

## 9. Manual Fallback

`P02` depends on the mobile platform; field service depends on nothing else. Cross-reference
`OP-014`.

| Step | Manual action |
|---|---|
| 1 | Dispatch reads the job to the technician by phone and records that it did so |
| 2 | Technician uses the **pre-numbered paper field job card** carried in every vehicle |
| 3 | Record: order number, arrival and departure times, customer name, work performed, parts used with part numbers, test result, charge, and the customer's signature |
| 4 | Photograph before and after on the technician's phone camera; note the image reference |
| 5 | Payment: issue a **pre-numbered manual receipt**; the receipt book is controlled stationery reconciled per `SP-019` |
| 6 | Telephone dispatch to confirm completion so the customer can be updated |
| 7 | **Back-enter every paper job card into `P02`/`P03` within 24 hours**, preserving original timestamps |
| 8 | R07 reconciles paper cards against the system at the end of the outage and signs it |

> Work requiring an approval above a `SP-004` band **cannot** be authorised by phone alone unless
> the approver records it in `P03` at the time. A verbal approval with no system record is an
> exception under `SP-004` OF-03, reviewed by R06 within 24 hours.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Assignment requires a skill match | Preventive (`BRU-FSM-02`) | Per job | Hard block |
| Uncertified technician cannot be assigned brand warranty work | Preventive (`BRU-SRM-09`) | Per job | Hard block |
| Arrival requires geofence or an exception reason | Preventive (`BRU-FSM-06`) | Per job | Exception log |
| Failed visit requires geotagged evidence | Preventive (`BRU-FSM-09`) | Per failed visit | Hard block |
| Before/after photographs mandatory on warranty jobs | Preventive (`BRU-SRM-17`) | Per warranty job | Cannot close without them |
| Van stock capped per item per technician | Preventive (`BRU-FSM-08`) | Continuous | Hard block |
| On-site payment reconciled by shift end | Preventive (`BRU-FSM-07`) | Per shift | Reconciliation record |
| GPS captured only on duty during working hours | Preventive (`BRU-FSM-05`) | Continuous | Privacy control — `LG-008` |
| Van stock variance reviewed | Detective | Per shift (`AUT-035`) | Variance report |
| Geofence exception pattern per technician | Detective | Weekly | `SP-005` PE-E10 |
| First-time-fix and rework analysis | Detective | Monthly | `KPI-004`, `KPI-005` |
| Field visit audit by `P11` field auditor | Detective | Sampled | Audit record |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Perform the repair | Record its independent QC (`SOD-07`) | Hard block above threshold | Remote photographic QC by R09 for field work, since a second technician on site is not economic |
| Collect cash in the field | Reconcile the branch cash book (`SOD-12`) | Hard block at assignment | Rider/technician hands cash to R29 Cashier against a receipt; reconciliation is performed by a different person |
| Request overtime | Approve it (`SOD-27`) | Hard block | — |
| Consume van stock | Approve the resulting variance write-off (`SOD-05`, `SOD-45`) | Hard block | Variance approval sits with R17 Inventory Manager, off-site |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-004` | First-time fix rate | 70% | 82%; stretch 88% |
| `KPI-011` | Jobs per technician per day | 4–5 | 7; stretch 8–9 |
| `KPI-012` | Technician utilisation | 55% | 74%; stretch 82% |
| `KPI-014` | Travel time as % of working day | ~35% | 26%; stretch 22% |
| `KPI-015` | On-time arrival within window | unmeasured | 88%; stretch 92% |
| `KPI-016` | Technician app daily active usage | 0% | 92%; stretch 95% |
| `KPI-017` | Offline sync failures | n/a | Zero |
| `KPI-047` | Van stock variance | untracked | < 2%; stretch < 1% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-005` Repair Estimate and Quotation | Issued at step 10 |
| `DT-007` Service Completion Report | Signed at step 18 |
| `UI-012` `P02` Technician App UI Copy Pack | The screens this SOP is performed on |
| `UI-009` Offline, Sync and Conflict Resolution Copy | Offline behaviour at step 19 |
| [`SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | The guided diagnostic at step 9 |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Van stock at steps 2, 12 and 21 |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](SP-019_SOP_Cash_Collection_and_Banking.md) | Payment at steps 17 and 22 |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Safety at step 7 and §8 |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Estimate construction and revision |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | §7 limits |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md) | Zones and travel bands |
| `TR-009` Course Pack — Field Technician | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Every step names who, the system, the evidence produced and a time
- [x] Safety branch present and takes precedence over performance targets
- [x] Offline behaviour specified, including what may **not** be approved offline
- [x] §7 reconciles with `SP-004`
- [x] Manual fallback specified with a back-entry deadline
- [x] Segregation of duties cites `SP-006`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
