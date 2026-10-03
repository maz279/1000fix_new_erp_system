---
id: SP-032
title: Operational Checklist Library
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Quality
author: Business Process Lead with Branch Operations and Quality
reviewers: [Operations Director, Quality Manager, HSE Lead, Finance Manager, Inventory Manager, Branch Managers Forum, Localisation Lead]
approver: Operations Director with Quality Manager
content_class: C
purpose: >
  Checklists are the cheapest control available and the one auditors ask for first. This library
  holds every recurring operational checklist — branch opening and closing, shift handover,
  safety, 5S, cash count, equipment check, vehicle check — with the rule that a checklist is a
  control only when it is completed at the time, by the person who did the work, with exceptions
  recorded rather than ticked away.
traces_to: [M04, M23, M31, M41, M46, M47, P03, P11, DT-008, SP-004, SP-005, SP-006, SP-010, SP-016, SP-018, SP-019, SP-029, SP-030]
priority: P2
wave: W1
bilingual: yes
bn_counterpart: SP-032_Operational_Checklist_Library_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M04_Branch_and_Front_Desk_Operations.md — BRU-FRD-11 and the shift reconciliation separation
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §10 BRU-QMS-01 — a quality checklist cannot be marked complete with unanswered mandatory items
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P11_Field_Auditor_and_Quality_Application.md
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 7.5.3 control of documented information, and clause 8.5.1 controlled conditions
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# Operational Checklist Library

| Item | Value |
|---|---|
| SOP ID | `SP-032` |
| Process owner | Operations Director (R05) with Quality Manager (R32) |
| Roles performing | `R06` Branch Manager · `R08` Service Centre Agent · `R09` Workshop Supervisor · `R18` Branch Store Keeper · `R29` Cashier · `R10`–`R12` Technicians · `R16` Riders · `R20` Warehouse Operatives |
| Systems used | `P03` (`UI-025`, `UI-026`, `UI-027`) · `P02` · `P09` · `P11` · `M23` |
| Frequency / volume | Daily and per shift, across 51+ branches, workshops, warehouses and vehicles |
| ISO 9001 clause reference | **7.5.3** documented information · 8.5.1 controlled conditions · 9.2 internal audit (the checklists auditors sample) |

---

## 1. Purpose and Outcome

**Purpose.** To hold one governed set of recurring operational checklists, so that every site
performs the same checks in the same way, records them at the time, and produces the evidence
that internal, ISO and brand audits ask for first.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every checklist was completed at the time by the person who did the work | Timestamp and identity per item |
| No checklist was closed with unanswered mandatory items | `BRU-QMS-01` — hard block |
| Exceptions were recorded and actioned, not ticked past | Exception records |
| Checklists are the same at every site of the same class | Library governance |
| Audit sampling finds the recorded state matches the actual state | `SP-029` audit findings |
| Checklist completion is measured, and low completion is treated as a control failure | Completion report |

---

## 2. Scope

**Applies to:** branch opening and closing, shift handover, cash count, safety walk, 5S and
housekeeping, equipment and bench checks, vehicle checks, warehouse checks, and the pre-audit
readiness checks — for every operational site and vehicle.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| The per-job quality checklist at release | `DT-008`, `SP-010` §5.3 — governed by Quality, not here |
| The internal audit checklist | `SP-029`; derived from each SOP's §10 controls |
| Statutory inspection records for lifting, electrical or fire systems | `M47` facilities; scheduled, not daily |
| Payroll, close and filing checklists | `SP-020`, `SP-021` |
| Software release checklists | `SP-031` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Checklist | A defined, ordered set of verification items with a completion record |
| Mandatory item | An item that must be answered before the checklist can be closed (`BRU-QMS-01`) |
| Exception | An item answered "no" or "not applicable" requiring a reason and an action |
| Blocking exception | An exception that stops the activity — the site does not open, the vehicle does not move |
| Completion record | Who completed it, when, at which location, with what exceptions |
| Drift | The gap between what the checklist says and what the work now requires |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Site classification | `MD-003` | Checklists differ by site class — flagship, standard, district, kiosk |
| Current SOPs | `06B` | Checklist items derive from SOP controls, never invented separately |
| Bilingual content | `CG-010` | Every operational checklist exists in Bengali; most users are Bengali-first |
| Device availability | `P02`, `P03`, `P11` | Or the printed pack per §9 |
| Named responsible role per checklist | `MD-008` | A checklist with no owner is not completed |
| Exception routing | `SP-005` | Where each exception type escalates |

---

## 5. Procedure

### 5.1 Governance rules for the library

| # | Rule |
|---|---|
| **CL-01** | **Every checklist item traces to a control in an SOP §10 table.** An item that controls nothing is removed. This is what keeps checklists short enough to be done honestly |
| **CL-02** | **Completed at the time, at the place, by the person who did the work.** A checklist completed at the end of the day from memory is a work of fiction |
| **CL-03** | **Mandatory items cannot be skipped** (`BRU-QMS-01`). The checklist does not close |
| **CL-04** | **An exception requires a reason and an action, not just a mark.** "No" with no reason is an unanswered item |
| **CL-05** | **Blocking exceptions block.** A safety or cash exception stops the activity; it does not generate a note for later |
| **CL-06** | **No checklist exceeds 15 items.** Longer lists are completed less honestly. Split by activity instead |
| **CL-07** | **Every checklist is bilingual**, and the Bengali is the working version at most sites |
| **CL-08** | **Photographic evidence where a state is disputable** — housekeeping, damage, safety, stock condition |
| **CL-09** | **The library is versioned centrally.** A branch may not add, remove or reword an item locally; it may propose a change |
| **CL-10** | **Completion is measured and low completion is a control failure**, investigated as such, not chased administratively |

### 5.2 The library

Each entry names its owner, frequency, the SOP whose controls it carries, and its blocking items.

#### CL-A — Branch opening

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Prior shift closed and reconciled | ✔ | **✔** | `SP-019` `BRU-FIN-10` |
| 2 | Safe intact; keys and combination access correct | ✔ | **✔** | `SP-019` |
| 3 | Float counted jointly and signed | ✔ | **✔** | `SP-019` §5.1 |
| 4 | Premises secure; no signs of entry or damage | ✔ | **✔** | `M47` |
| 5 | Fire exits clear; extinguishers in place and in date | ✔ | **✔** | `SP-030` |
| 6 | First-aid kit present and stocked | ✔ | | `SP-030` |
| 7 | Systems reachable — `P03`, printer, scanner, card and MFS terminal | ✔ | | `SP-007` |
| 8 | Ready-for-collection store reconciled to the system count | ✔ | | `SP-010` §5.4 |
| 9 | Customer-facing area clean and signage current | ✔ | | `VB-003` |
| 10 | Staffing against roster; coverage minimum met | ✔ | | `SP-022` |

#### CL-B — Branch closing

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Cash counted, declared blind, reconciled by a second person | ✔ | **✔** | `SP-019` `SOD-12` |
| 2 | Takings secured or banked per the holding limit | ✔ | **✔** | `SP-019` |
| 3 | Shift closed in the system | ✔ | **✔** | `BRU-FIN-10` |
| 4 | Customer devices accounted for and secured; high-value segregated | ✔ | **✔** | `SP-010` §5.4 |
| 5 | Open service orders reviewed for SLA risk | ✔ | | `SP-005` |
| 6 | Equipment powered down; hazardous items stored correctly | ✔ | **✔** | `SP-030`, `SP-026` |
| 7 | Premises secured; alarm set | ✔ | **✔** | `M47` |
| 8 | Exceptions from the day handed over in writing | ✔ | | CL-C |

#### CL-C — Shift handover

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Open jobs and their SLA position | ✔ | | `SP-010` |
| 2 | Devices in custody, by location | ✔ | **✔** | `SP-007` |
| 3 | Cash position and any variance | ✔ | **✔** | `SP-019` |
| 4 | Outstanding customer commitments made today | ✔ | | `SP-028` |
| 5 | Equipment faults or safety issues | ✔ | **✔** | `SP-030` |
| 6 | Parts on order or awaited | ✔ | | `SP-016` |
| 7 | Both parties sign the handover | ✔ | **✔** | — |

#### CL-D — Daily safety walk

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Walkways and exits clear | ✔ | **✔** | `SP-030` |
| 2 | No exposed wiring, damaged sockets or overloaded points | ✔ | **✔** | `SP-030` |
| 3 | Battery storage correct and containment intact | ✔ | **✔** | `SP-026` |
| 4 | No swollen, damaged or leaking cells in general storage | ✔ | **✔** | `SP-026` |
| 5 | PPE available and serviceable | ✔ | | `SP-030` |
| 6 | Spill and fire response equipment in place | ✔ | **✔** | `SP-030` |
| 7 | Racking and shelving undamaged and within load | ✔ | **✔** | `SP-018` |
| 8 | Any hazard reported the same shift | ✔ | | `SP-030` §5.2 |

#### CL-E — Cash count

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Count performed before the system figure is viewed | ✔ | **✔** | `SP-019` §5.4 |
| 2 | Declared amount entered | ✔ | **✔** | `SP-019` |
| 3 | Variance explained with a reason code | ✔ | **✔** | `MD-026` |
| 4 | Verified by a person other than the holder | ✔ | **✔** | `SOD-12` |
| 5 | Manual receipt book numbers accounted for | ✔ | | `SP-019` §9 |
| 6 | Banking prepared against the reconciled position | ✔ | | `SP-019` §5.5 |

#### CL-F — Workshop bench and equipment

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | ESD protection in use and tested | ✔ | **✔** | `SP-010` |
| 2 | Test equipment calibration dates current | ✔ | **✔** | `MD-046` `SOD-52` |
| 3 | Tools accounted for and serviceable | ✔ | | `M45` |
| 4 | WIP count reconciles to the system | ✔ | **✔** | `SP-010` §5.4 |
| 5 | High-value devices segregated and secured | ✔ | **✔** | `SP-010` |
| 6 | Bench clean; no loose components or fluids | ✔ | | 5S |
| 7 | Waste segregated correctly | ✔ | | `SP-026` |

#### CL-G — Vehicle daily check

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Tyres, lights, brakes, mirrors, horn | ✔ | **✔** | `M46`, `SP-030` |
| 2 | Fluid levels | ✔ | | `M46` |
| 3 | Documents valid — registration, fitness, insurance, licence | ✔ | **✔** | `M46` |
| 4 | First-aid kit and fire extinguisher present | ✔ | **✔** | `SP-030` |
| 5 | Load secure; restricted items only if certified | ✔ | **✔** | `BRU-LOG-05` |
| 6 | Van stock reconciled at shift end | ✔ | | `SP-016` §5.5 |
| 7 | Damage recorded with photographs | ✔ | | `M46` |

#### CL-H — Warehouse daily

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Receiving bay clear; nothing unrecorded | ✔ | | `SP-018` |
| 2 | Quarantine area segregated and labelled | ✔ | **✔** | `BRU-INV-07` |
| 3 | Cycle count tasks for the day issued | ✔ | | `AUT-036` |
| 4 | Bin labels legible and correct | ✔ | | `DT-044` |
| 5 | Hazardous and battery storage compliant | ✔ | **✔** | `SP-026` |
| 6 | Handling equipment inspected | ✔ | **✔** | `SP-030` |
| 7 | Holdings within permitted limits | ✔ | **✔** | `SP-026` |

#### CL-I — 5S and housekeeping (weekly)

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Sort — nothing present that is not needed | ✔ | | 5S |
| 2 | Set in order — everything has a marked location | ✔ | | 5S |
| 3 | Shine — cleaned, with photographic evidence | ✔ | | `CL-08` |
| 4 | Standardise — the standard is displayed | ✔ | | 5S |
| 5 | Sustain — last week's actions closed | ✔ | | 5S |

#### CL-J — Pre-audit readiness (monthly)

| # | Item | Mandatory | Blocking | From |
|---:|---|:--:|:--:|---|
| 1 | Open CAPAs for this site reviewed and on track | ✔ | | `SP-029` |
| 2 | Checklist completion for the month at or above target | ✔ | | `CL-10` |
| 3 | Training and certification currency for site staff | ✔ | | `SP-023` |
| 4 | Prior audit findings closed | ✔ | | `SP-029` |
| 5 | Documented information current — SOPs, notices, emergency contacts | ✔ | | ISO 7.5.3 |

### 5.3 Completing a checklist

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | Responsible role | Open the checklist at the point of work, on `P03`, `P02`, `P09` or `P11` | Device | Session opened with identity and location |
| 2 | Responsible role | Complete each item as it is verified. **Do not pre-tick and verify afterwards** | Device | Item responses with timestamps |
| 3 | Responsible role | On an exception, record the reason and take the immediate action | Device | Exception record |
| 4 | Responsible role | On a **blocking** exception, stop the activity and escalate (`CL-05`) | `SP-005` | Escalation |
| 5 | Responsible role | Attach photographs where the item requires them | Device | Evidence |
| 6 | Responsible role | Close the checklist. Mandatory items unanswered prevent closure (`BRU-QMS-01`) | Device | Completion record |
| 7 | R06 / R09 | Review exceptions daily; close or escalate them | `P03` | Review record |
| 8 | R32 | Sample completion quality — do the records match the observed state? | `P11` | Audit sample |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | The person completing it did not do the work | Stop. The checklist has no value as a record of someone else's activity | R06 |
| 3 | An item is genuinely not applicable at this site | Record "not applicable" with the reason. **If an item is never applicable at a site class, the library is wrong** — propose a change (`CL-09`) | R32 |
| 4 | A blocking exception occurs at opening | **The site does not open** until resolved or a documented interim control is approved | R06 → R05 |
| 4 | A blocking exception occurs on a vehicle check | **The vehicle does not move** | R06 / R15 |
| 4 | A blocking safety exception occurs | Stop-work authority applies unconditionally (`SP-030` `SW-01`) | Any person |
| 6 | The device is unavailable | Use the printed pack (§9); do not defer the check | R06 |
| 7 | The same exception recurs daily | It is not an exception, it is the current state. Raise a nonconformity | R32 → `SP-029` |
| 8 | Records are complete but the observed state is poor | The checklist is being completed dishonestly. That is a serious finding about the control, not a housekeeping issue | R32 → R05 |
| — | A branch proposes an item change | Route to R32 for the library; useful local knowledge should improve the library, not fork it (`CL-09`) | R32 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Add, remove or reword a checklist item | Any | R32 Quality Manager with R05 (`CL-09`) | CEO |
| Open a site with an unresolved blocking exception | Any | R05 Operations Director, with a documented interim control | CEO |
| Move a vehicle with a blocking exception | **None — safety, no override** | — | — |
| Waive a checklist for a shift | Any | R06 with R32, recorded; **a waived checklist is an exception, not an absence** | R05 |
| Accept a "not applicable" as permanent for a site class | Any | R32; the library is amended | R05 |
| Approve a local variant checklist | Any | R32; variants are versioned centrally, never local files | R05 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Blocking exception at opening | Site does not open; escalate immediately | R06 → R05 | Exception record |
| Checklist completion below target at a site | Investigate as a control failure, not as an administrative lapse | R32 → R05 | `SP-029` |
| Checklists completed but conditions poor | Serious integrity finding; audit the site and the supervision | R32 → R05 | Nonconformity |
| Checklist completed in bulk at end of day | Timestamp analysis reveals it; treat as `CL-02` breach | R32 | Nonconformity |
| Photographic evidence missing where required | Item is unanswered; the checklist does not close | R06 | System block |
| Bengali version out of step with English | Halt use of the changed item until the Bengali is signed off (`BN-018`) | Localisation Lead | Translation exception |
| A site has invented its own checklist | Withdraw it; incorporate anything genuinely useful into the library | R32 | Library change |
| Device unavailable across a site for more than a shift | Printed pack in use; back-entry within 24 hours | R06, R33 | Manual record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Every site holds a **printed checklist pack**, current version, in both languages, reprinted on every library change |
| 2 | Checklists are completed on paper at the time, signed and timed |
| 3 | Photographs are taken on a site camera with the reference noted against the item |
| 4 | **Blocking exceptions block exactly as they do in the system.** Paper does not lower the bar |
| 5 | **Back-enter every checklist within 24 hours**, preserving completion times |
| 6 | R06 reconciles the paper pack against the system; R32 samples |

> The printed pack must be reissued on every library change. A site working from a superseded
> printed pack is performing yesterday's controls — the same risk `SP-013` §9 records for the
> printed rate card, and owned by the same distribution discipline.

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Mandatory items cannot be skipped | Preventive (`BRU-QMS-01`) | Per checklist | Hard block |
| Blocking exceptions stop the activity | Preventive (`CL-05`) | Per exception | Activity block |
| Identity, time and location captured per completion | Preventive | Per checklist | Completion record |
| Photographic evidence where required | Preventive (`CL-08`) | Per item | Attachment required |
| Library versioned centrally; no local variants | Preventive (`CL-09`) | Continuous | Version control |
| Checklist items trace to an SOP control | Preventive (`CL-01`) | Per library change | Traceability map |
| Daily exception review | Detective | Daily | Review record |
| Completion rate by site and checklist | Detective (`CL-10`) | Weekly | Completion report |
| Timestamp pattern analysis for bulk completion | Detective | Monthly | Integrity check |
| Audit sampling of recorded versus observed state | Detective | Per audit plan | `SP-029` |
| Bilingual currency check | Detective | Per library change | `BN-018` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Hold cash | Verify the cash count (`SOD-12`, CL-E item 4) | Hard block | At single-person sites, remote verification per `SP-006` §4.6 |
| Perform the work | Audit the checklist that covers it (`SOD-20`) | Hard block | `P11` field auditor or cross-site auditor |
| Complete a checklist | Approve a waiver of it | Hard block | Waiver approved by R06 with R32 |
| Propose a library change | Approve it alone | Hard block | R32 approves with R05 |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| Checklist completion rate | Completed against due, by site and checklist | untracked | ≥ 98% |
| Blocking exceptions | Count and resolution time | untracked | Recorded, resolved same day |
| Bulk-completion incidents | Checklists completed outside the work window | untracked | **Zero** |
| Audit findings on checklist integrity | Findings where records did not match observation | untracked | **Zero** |
| Exception recurrence | Same exception recurring beyond 5 occurrences | untracked | Converted to CAPA |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-008` Quality Checklist Record | The per-job quality gate, governed separately |
| `UI-025` Workspace — Branch Console Copy · `UI-021` `P11` Field Auditor App Copy Pack | The screens used |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](SP-019_SOP_Cash_Collection_and_Banking.md) | CL-A, CL-B, CL-E |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | CL-C, CL-F |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | CL-G item 6 |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | CL-H |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Battery and hazardous storage items |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | CL-D and every blocking safety item |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Audits sample against this library |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | CL-F item 2 |
| `TR-011` Course Pack — Branch Manager · `TR-022` Job Aid and Quick Reference Library | Train this library |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue — ten checklists, CL-A to CL-J | Operations Director with Quality Manager (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Ten checklists specified with mandatory and blocking items, each traced to an SOP control
- [x] The 15-item bound and the "completed at the time" rule stated as governance
- [x] Bulk-completion detection included as an integrity control
- [x] Local variants prohibited, with a proposal route that improves the library
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`. This is the highest-priority Bengali item in the category — these are the forms front-line staff use every shift**
- [ ] Site-class variants confirmed against `MD-003` clustering — **outstanding**
- [ ] Printed pack distribution and reissue process agreed — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
