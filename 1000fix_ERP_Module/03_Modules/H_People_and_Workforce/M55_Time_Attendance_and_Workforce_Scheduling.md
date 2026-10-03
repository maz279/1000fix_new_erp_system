---
id: FIX-ERP2-M55
module_id: M55
module_code: WFM
module_name: Time, Attendance & Workforce Scheduling
category: H — People & Workforce
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-12
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: HR Director
system_owner: People Squad
priority: P1
wave: W5
regulatory_verified: 2026-08-12
---

# M55 — Time, Attendance & Workforce Scheduling
### Category H · Code `WFM` · ★ New module in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M55 |
| **Module code** | `WFM` |
| **Category** | H — People & Workforce |
| **Status** | ★ **New** — split from M21 after enterprise benchmarking |
| **Priority** | **P1** |
| **Delivery wave** | W5 (Months 19–22) |
| **Business owner** | HR Director |
| **System owner** | People Squad |
| **Delivery layers** | L1 (Odoo `hr_attendance`, `hr_holidays`) + L2 (OCA) + L5 (custom) + biometric device integration |
| **Custom modules** | `cd_attendance`, `cd_leave`, `cd_roster`, `cd_capacity`, `cd_overtime` |
| **Requirement range** | FR-WFM-001 … FR-WFM-052 |
| **Requirement count** | 52 |
| **Effort estimate** | 22 person-weeks |
| **Depends on** | M21 Core HR · M30 Platform Admin · M29 Identity · M22 Competency |
| **Depended on by** | **M56 Payroll (blocking)** · **M02 Field Service (blocking)** · M31 Workshop · M04 Front Desk · M27 Contact Centre · M57 Performance · M05 Managed Services · M59 · M67 |

---

## 2. Purpose

M55 answers three questions that everything else in the operation depends on:
**who is at work, who is available, and who is scheduled.**

It captures attendance from biometric devices and GPS-verified mobile clock-in, manages every
leave type, builds shift rosters across 51+ branches, and publishes the availability that
dispatch (M02) uses to assign work and payroll (M56) uses to calculate pay.

### Why It Exists

Attendance today is a manual sign-in book. Leave is tracked in a spreadsheet. There are no
rosters. The v1.0 BRD is explicit about the consequences: attendance errors, leave balance
disputes, inaccurate overtime tracking, and payroll calculated from unreliable inputs.

Two downstream modules cannot function without M55:

- **M56 Payroll** cannot compute pay without verified hours, absence and approved overtime.
- **M02 Field Service** cannot assign work without knowing who is on shift, on leave or already
  at capacity. The v1.0 dispatch design assumed this data existed; it does not.

### Why It Is Separate from M21

The employee master changes when someone joins, moves or leaves — a few hundred times a year.
Attendance changes 500+ times a day. Rosters change weekly. Merging them means the highest-volume
transactional data in HR sits inside the lowest-volume master record, and every attendance
correction touches the employee master.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| ERP BRD §8.6 (BR-HRM-004) | "Track attendance via biometric device integration or GPS-based mobile clock-in" |
| ERP BRD BR-HRM-005 | "Manage all leave types (annual, sick, casual, maternity/paternity) with balance tracking" |
| ERP BRD BR-HRM-006 | "Manage Bangladesh public holiday calendar with automatic application" |
| ERP BRD BRU-HRM-02 | **"Overtime must be pre-approved by the line manager before it can be recorded for payroll calculation"** |
| ERP BRD BRU-HRM-04 | "Annual leave cannot be approved if team coverage threshold would fall below the configured level" |
| ERP BRD BRU-HRM-05 | **"Payroll cannot be finalized for a period if attendance records for that period have not been verified and locked"** |
| ERP BRD §6.2 Process 9 | Current state: manual sign-in book, leave spreadsheet, attendance errors, leave balance disputes, inaccurate overtime |
| ERP BRD ASM-11 | Biometric attendance devices procured and installed before HR module go-live |
| **Bangladesh Labour Act 2006** *(verified 2026-08-12)* | **Maximum 8 normal hours per day, 2 hours overtime, total not exceeding 10 hours per day; 48 hours per week**; casual, sick and annual leave; **maternity leave 16 weeks (8 before, 8 after)**; **women prohibited from working between 22:00 and 06:00** |
| **Personal Data Protection Act 2026** *(verified 2026-08-12)* | **Biometric identifiers are Sensitive Personally Identifiable Data** subject to specific consent and cross-border transfer restriction |
| **Field workforce practice** *(verified 2026-08-12)* | Geofenced zones triggering attendance on entry and exit; **biometric proves who clocked in, geofence proves where**; single-tap status change as the usability standard |

---

## 3. Scope Boundary

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Attendance capture: biometric device, GPS mobile, web, kiosk, manual |
| 2 | Geofenced clock-in and clock-out for field and branch staff |
| 3 | Attendance exception detection and regularisation workflow |
| 4 | Working-time rules: normal hours, overtime, rest, weekly limits |
| 5 | Overtime request, pre-approval and recording |
| 6 | Leave types, entitlement, accrual, balance, request and approval |
| 7 | Leave coverage checking against team thresholds |
| 8 | Public holiday calendar including moon-dependent dates |
| 9 | Shift patterns, roster construction and publication |
| 10 | On-call and standby rota |
| 11 | Availability publication for dispatch and contact centre |
| 12 | Capacity forecasting by skill, zone and period |
| 13 | Attendance period verification and locking for payroll |
| 14 | Timesheet for project and contract work allocation |
| 15 | Attendance and absence analytics |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| **Employee master, contract, position, status** | **M21** | Master data; M55 consumes it |
| **Pay calculation from hours** | **M56** | M55 supplies verified hours; M56 turns them into money |
| **Job assignment to a technician** | **M02** | M55 says who is available; M02 decides who does what |
| **Route optimisation and job sequencing** | **M02** | Operational scheduling of work, not of people |
| **Performance measurement and incentive** | **M57** | M55 supplies hours; M57 measures output |
| **Competency and certification** | **M22** | M55 publishes availability; M22 says who is qualified |
| **Contact centre agent scheduling against forecast volume** | **M27** | M27 schedules within the roster M55 publishes |
| **Contractor and marketplace seller availability** | **M12** | Not employees |
| Medical certificates supporting sick leave | **M59** | Medical data is S3 and held under tighter control |
| Expense claims for travel time | **M52** | Financial transaction |
| Biometric device procurement and physical installation | Operations | M55 integrates with devices; it does not buy them |

### 3.3 Shared Concepts

| Concept | M55's Role | Owning Module |
|---|---|---|
| Employee | References | M21 |
| Attendance record | **Owns** | M55 |
| Leave | **Owns** | M55 |
| Roster and shift | **Owns** | M55 |
| Availability | **Publishes** | M55 |
| Working-time rule | **Owns** | M55 |
| Overtime approval | **Owns**; M56 pays it | M55 |
| Competency | Consumes for skill-based availability | M22 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **SAP SuccessFactors Time Management** | Time recording, time-off, time valuation feeding payroll | **Time valuation as a distinct step** between raw attendance and payable hours | Full SAP time-type configuration depth |
| **Oracle HCM Time and Labor** | Time entry, rules engine, approvals, payroll integration | The **rules engine as configuration** — working-time rules change with law, not with code | — |
| **Workday Time Tracking & Absence** | Time capture, absence accrual, calendars | Accrual model with balance projection | Platform-specific calculation framework |
| **IFS Mobile Workforce Management** | Planning, scheduling, dispatch and field execution covering the full lifecycle **from work intake and capacity planning to schedule optimisation** | **Capacity planning as an explicit step** preceding schedule optimisation in M02 | Combining people-scheduling and work-scheduling in one module |
| **Geofenced field attendance practice** | Geofenced zones automatically triggering attendance on entry and exit, eliminating manual entry error; **biometric proves who, geofence proves where** | **Both signals together** — neither alone is sufficient for a field workforce | Geofence-only, which cannot prevent buddy punching |
| **Field time-tracking usability practice** | Mobile, GPS-verified tracking requiring **minimal input — ideally a single tap** | Single-tap clock-in; attendance derived from job events where possible | Any design requiring a technician to fill a form to record time |

**Design position.** Five deliberate differences.

First, **attendance is derived, not entered, wherever possible**. A technician who arrives at a
customer site inside the geofence and taps "Arrived" in M02 has recorded attendance. Asking them
to separately clock in is duplicate work that will be skipped or falsified.

Second, **biometric and geofence are complementary, not alternative**. Biometric answers *who*;
geofence answers *where*. Branch staff use biometric at the device; field staff use
GPS-verified mobile clock-in with biometric or selfie verification. Neither signal alone is
sufficient for a distributed workforce.

Third, **working-time rules are configuration**. The Labour Act sets 8 normal hours, 2 overtime
hours, a 10-hour daily maximum and 48 hours weekly. Those limits, the maternity provisions, and
the night-work restriction for women are parameters, not hard-coded logic, because employment
law changes and the Company intends to operate in more than one country.

Fourth, **attendance verification is a gate, not a report**. Payroll cannot run for a period
until attendance for that period is verified and locked. This is the single control that
prevents the most common payroll failure: paying from unverified data and correcting afterwards.

Fifth, **availability is a published product, not a query**. M02 and M27 consume an availability
projection rather than querying rosters and leave at assignment time. This keeps dispatch fast
and keeps roster logic in one place.

---

## 5. Functional Areas & Features

### 5.1 Attendance Capture

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-001 | Biometric device integration | Ingest clock events from biometric devices at branches, by API or scheduled file, with device health monitoring | **P1** | L5 |
| FR-WFM-002 | **GPS mobile clock-in** | Capture clock-in and clock-out from the technician mobile app with GPS coordinates and accuracy | **P1** | L5 |
| FR-WFM-003 | **Geofenced attendance** | Trigger or validate attendance against geofences around branches and customer sites | **P1** | L5 |
| FR-WFM-004 | Identity verification at clock-in | Verify identity by biometric or selfie at mobile clock-in, to prevent proxy attendance | **P1** | L5 |
| FR-WFM-005 | **Derived attendance** | Derive attendance from M02 job events — departed, arrived, completed — so a technician does not clock in twice for the same fact | **P1** | L5 |
| FR-WFM-006 | Web and kiosk capture | Provide web and branch kiosk clock-in for office and counter staff | P1 | L1 |
| FR-WFM-007 | Manual entry | Permit manual attendance entry by an authorised approver, with reason and full audit | P1 | L5 |
| FR-WFM-008 | Offline capture | Capture attendance offline in the mobile app and synchronise on reconnection without loss | **P1** | L5 |
| FR-WFM-009 | Multi-punch handling | Handle multiple in and out events per day — breaks, site-to-site movement — and derive worked time correctly | P1 | L5 |
| FR-WFM-010 | Attendance source recording | Record the capture method and evidence for every attendance record | **P1** | L5 |

### 5.2 Exceptions & Regularisation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-011 | Exception detection | Detect missing punch, late arrival, early departure, absent without leave, geofence mismatch, excessive hours and impossible travel | **P1** | L5 |
| FR-WFM-012 | Regularisation request | Let an employee raise a regularisation request with reason and evidence | P1 | L5 |
| FR-WFM-013 | Regularisation approval | Route to the line manager with escalation, and record the decision | P1 | L5 |
| FR-WFM-014 | Bulk regularisation | Allow a manager to regularise a batch — for example a branch-wide device failure — with a single documented reason | P2 | L5 |
| FR-WFM-015 | Exception ageing | Age unresolved exceptions and escalate before the payroll cut-off | **P1** | L5 |
| FR-WFM-016 | Fraud signal | Flag patterns indicating proxy attendance or manipulation — repeated identical timings, geofence spoofing indicators, device sharing | P2 | L5 |

### 5.3 Working Time & Overtime

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-017 | **Working-time rules** | Configure normal hours, maximum daily hours, maximum weekly hours, minimum rest and break rules **as parameters, per the Labour Act** | **P0** | L5 |
| FR-WFM-018 | **Statutory limit enforcement** | Prevent scheduling and flag actuals that breach the daily 10-hour maximum or the 48-hour weekly limit | **P0** | L5 |
| FR-WFM-019 | **Night-work restriction** | Enforce the statutory restriction on women working between 22:00 and 06:00, with any permitted exception recorded | **P0** | L5 |
| FR-WFM-020 | Time valuation | Convert raw attendance into payable time categories — normal, overtime, holiday, night, on-call — using configured rules | **P1** | L5 |
| FR-WFM-021 | **Overtime pre-approval** | Require line-manager approval **before** overtime is worked; unapproved excess hours are recorded but not payable | **P0** | L5 |
| FR-WFM-022 | Overtime request | Let a manager raise a planned overtime request against a business reason and a budget | P1 | L5 |
| FR-WFM-023 | Retrospective overtime | Permit retrospective approval only by an authority above the line manager, with reason | **A** | L5 |
| FR-WFM-024 | Overtime budget and reporting | Track overtime hours and cost against budget by branch and department | P1 | L5 |
| FR-WFM-025 | Compensatory time off | Support time off in lieu where policy permits, with a balance and expiry | P2 | L5 |

### 5.4 Leave & Absence

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-026 | Leave types | Configure annual, casual, sick, maternity, paternity, bereavement, unpaid, compensatory and special leave with distinct rules | **P1** | L1 |
| FR-WFM-027 | Entitlement and accrual | Calculate entitlement by service, contract type and policy; accrue on the configured basis | **P1** | L5 |
| FR-WFM-028 | **Maternity leave** | Apply the statutory 16 weeks — 8 before and 8 after confinement — with the associated pay treatment | **P0** | L5 |
| FR-WFM-029 | Leave request and approval | Let an employee request leave and route it for approval with delegation and escalation | P1 | L1 |
| FR-WFM-030 | **Coverage check** | Block or warn on leave approval where team coverage would fall below the configured threshold for that branch and skill | **P1** | L5 |
| FR-WFM-031 | Balance and projection | Show current balance and projected balance at any future date, including planned leave | P1 | L5 |
| FR-WFM-032 | Carry-forward and encashment | Apply carry-forward limits, lapse rules and encashment eligibility, feeding M56 | P1 | L5 |
| FR-WFM-033 | Sick leave and certification | Require a medical certificate above a threshold; **the certificate is stored in M59 under S3 control, not in M55** | **P1** | L5 |
| FR-WFM-034 | Leave calendar | Present a team and branch leave calendar to managers and dispatch | P1 | L5 |
| FR-WFM-035 | Absence without leave | Record unauthorised absence with escalation and disciplinary linkage | P1 | L5 |
| FR-WFM-036 | Leave cancellation and recall | Handle cancellation and operational recall from leave with balance restoration | P2 | L5 |

### 5.5 Holidays, Shifts & Rosters

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-037 | **Public holiday calendar** | Maintain the Bangladesh public holiday calendar per year, **including moon-dependent dates confirmed close to the event**, applied automatically | **P1** | L2 |
| FR-WFM-038 | Branch-specific calendars | Support branch or region-specific holiday variations | P2 | L5 |
| FR-WFM-039 | Shift pattern definition | Define shift patterns with start, end, break, and rotation rules | P1 | L5 |
| FR-WFM-040 | Roster construction | Build rosters by branch, skill and shift, respecting working-time rules, leave and coverage requirements | **P1** | L5 |
| FR-WFM-041 | **Roster publication** | Publish the roster before the period begins, with a defined minimum notice, and notify affected staff | **P1** | L5 |
| FR-WFM-042 | Roster change control | Control changes to a published roster, requiring approval and notification within the notice period | P1 | L5 |
| FR-WFM-043 | Shift swap | Let employees request a shift swap, subject to skill equivalence and manager approval | P2 | L5 |
| FR-WFM-044 | On-call and standby rota | Manage the after-hours on-call rota with allowance and callout recording, consumed by M02 and M05 | **P1** | L5 |
| FR-WFM-045 | Roster templates | Maintain reusable roster templates by branch type and season | P2 | L5 |

### 5.6 Availability, Capacity & Payroll Interface

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-WFM-046 | **Availability publication** | Publish, per employee per interval, whether they are available, on shift, on leave, on call or unavailable — consumed by M02, M27, M31 and M05 | **P0** | L5 |
| FR-WFM-047 | **Skill-based availability** | Publish availability tagged with competencies from M22, so dispatch can find qualified available people in one call | **P1** | L5 |
| FR-WFM-048 | Capacity forecast | Forecast available capacity by branch, skill and zone for the coming period, consumed by M02 and M35 | **P1** | L5 |
| FR-WFM-049 | Capacity gap alerting | Alert where forecast demand exceeds forecast capacity by branch and skill | P1 | L5 |
| FR-WFM-050 | Timesheet allocation | Allocate time to projects, contracts or cost centres where required by M67 or M05 | P2 | L5 |
| FR-WFM-051 | **Period verification and lock** | Verify attendance for a payroll period, lock it, and **prevent payroll from running on an unlocked period** | **P0** | L5 |
| FR-WFM-052 | Post-lock correction | Permit correction after lock only through an approved adjustment that carries into the next payroll period | **P1** | L5 |

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Biometric template residency** | Biometric templates are **Sensitive Personally Identifiable Data** under the PDPA and are stored in the **Bangladesh-resident store**; only a non-reversible reference is held regionally *(NFR-086, NFR-099)* |
| T-02 | **Biometric consent** | Specific consent for biometric processing is captured and recorded before enrolment; an alternative capture method must exist for employees who decline |
| T-03 | **Device abstraction** | Biometric devices sit behind an adapter; adding or replacing a device model does not change the attendance engine |
| T-04 | **Device health monitoring** | A device that stops reporting raises an alert within one hour; branch attendance falls back to an alternative method automatically |
| T-05 | **Offline-first mobile capture** | Clock events are queued locally with a client-generated key and replayed idempotently on reconnection |
| T-06 | **Geofence evaluation** | Evaluated server-side from reported coordinates and accuracy; a low-accuracy fix is flagged, not silently accepted |
| T-07 | **Rules as configuration** | Working-time, leave and accrual rules are data. A statutory change is a configuration change with an effective date, not a release |
| T-08 | **Time valuation determinism** | Given the same attendance and the same rule version, valuation produces the same payable hours every time, and records which rule version applied |
| T-09 | **Period lock integrity** | A locked period is immutable at the database level; correction is a forward adjustment, never a retrospective edit |
| T-10 | **Availability projection** | Availability is maintained as a materialised projection updated on roster, leave and attendance change — never computed at dispatch time |
| T-11 | **Volume** | 500+ employees × multiple daily events; peak ingestion at branch opening and closing must not degrade dispatch availability queries |
| T-12 | **Performance envelope** | Availability query ≤ 200 ms · roster publication for a branch ≤ 5 s · leave balance projection ≤ 500 ms |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M55 |
|---|---|---|
| **Technician** | Signs a book; disputes leave balance; overtime recorded informally | Clocks in from the phone; sees their own attendance, balance and roster; overtime approved before it is worked |
| **Branch manager** | Does not know who is in today until they look around | Sees attendance, exceptions, leave and roster for the branch in real time |
| **HR Officer** | Reconstructs attendance from books at month end | Attendance verified continuously; the period is locked, not rebuilt |
| **Dispatch (M02)** | Guesses who is available; discovers absence when the technician does not answer | Consumes published availability with skills attached |
| **Payroll (M56)** | Calculates from an unreliable spreadsheet | Runs against verified, locked hours |
| **Contact centre (M27)** | Schedules agents without reference to HR rosters | Schedules within the published roster |
| **Operations Director** | Cannot see capacity | Forecast capacity by branch, skill and zone with gap alerts |
| **Compliance officer** | Cannot evidence working-hour compliance | Statutory limits enforced and breaches visible |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Payroll accuracy** | Verified, locked hours replacing spreadsheet reconstruction | Precondition for **< 0.3% payroll corrections**; the single largest source of payroll error is attendance data |
| **Leave dispute elimination** | Balance visible to the employee, computed from rules | **Frequent disputes → < 5 per year** |
| **Overtime cost control** | Pre-approval enforced before hours are worked | Overtime becomes a managed cost rather than a discovered one |
| **Dispatch reliability** | Published availability with skills | Direct enabler of the **8–9 jobs per technician per day** target and of the 70% auto-assignment rate |
| **Capacity planning** | Forecast capacity against forecast demand | Prevents both idle capacity and unserviceable campaign demand *(see M35 capacity check)* |
| **Attendance integrity** | Biometric plus geofence plus derived attendance | Removes proxy attendance, a material and usually invisible cost at 500+ staff |
| **Statutory compliance** | Working-hour limits, maternity, night-work restriction enforced | Removes a Labour Act exposure that is presently unmanaged |
| **Administrative saving** | Self-service leave and attendance replacing manual handling | Material HR and branch-manager time released |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Fairness in attendance and leave** | A visible, rule-computed balance ends the perception that leave depends on who asks |
| **Protection for employees** | Enforced working-hour limits protect staff from excessive hours as much as they protect the Company from claims |
| **Trust in payroll** | Employees who can see the hours their pay was calculated from dispute it far less |
| **Evidence in a dispute** | Attendance, leave and overtime records are the evidence in a Labour Act claim |
| **Manager capability** | Rostering and coverage become a defined management activity rather than an informal arrangement |
| **Foundation for 24/7 service** | The on-call rota is what turns the business plan's round-the-clock commitment into a staffed reality |

---

## 8. Lifecycle & State Models

### 8.1 Attendance Record

```
   CAPTURED (biometric / GPS mobile / derived from M02 / web / kiosk / manual)
        |
   +----v-----------+
   | VALIDATED      |  identity, geofence, accuracy, plausibility
   +----+-----------+
        |
        +--> EXCEPTION --> REGULARISATION REQUESTED --> APPROVED / REJECTED
        |                        |
        |                        +--> ESCALATED (ageing before payroll cut-off)
        |
   +----v-----------+
   |    VALUED      |  time valuation: normal / overtime / holiday / night / on-call
   +----+-----------+     rule version recorded
        |
   +----v-----------+
   |   VERIFIED     |  manager or HR confirms the period
   +----+-----------+
        |
   +----v-----------+
   |    LOCKED      |  immutable; payroll may now run  <-- BRU-HRM-05 gate
   +----+-----------+
        |
        +--> POST-LOCK ADJUSTMENT --> carried forward to the next payroll period
```

### 8.2 Leave Request

```
   +-----------+
   |   DRAFT   |
   +-----+-----+
         | submitted
   +-----v---------------+     insufficient balance
   | BALANCE CHECKED     |----------------------------> REJECTED
   +-----+---------------+
         |
   +-----v---------------+     coverage below threshold
   | COVERAGE CHECKED    |----------------------------> BLOCKED / WARNED
   +-----+---------------+                                (BRU-HRM-04)
         |
   +-----v---------------+
   | PENDING APPROVAL    |  line manager, with escalation on delay
   +-----+---------------+
         |
   +-----v-----+       +------------+
   | APPROVED  |       |  REJECTED  |  reason recorded
   +-----+-----+       +------------+
         |
   +-----v-----------+
   |  SCHEDULED      |  availability updated; dispatch informed
   +-----+-----------+
         |
   +-----v-----+       +--------------+
   |   TAKEN   |       |  CANCELLED   |  balance restored
   +-----+-----+       +--------------+
         |                    ^
         |                    |
         +--> RECALLED -------+  operational recall; balance restored
```

### 8.3 Roster

```
   DRAFT --> COVERAGE VALIDATED --> APPROVED --> PUBLISHED (minimum notice enforced)
                                                      |
                                        +-------------+-------------+
                                        |                           |
                                   IN EFFECT                  CHANGE REQUESTED
                                        |                           |
                                        |                    APPROVED --> REPUBLISHED
                                        |                    (staff notified)
                                        v
                                    COMPLETED --> feeds actual-versus-planned analysis
```

---

## 9. Business Rules

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-WFM-01 | **Payroll cannot be finalised for a period whose attendance is not verified and locked** *(BRU-HRM-05)* | **H** | HR Director / CFO |
| BRU-WFM-02 | **Overtime must be pre-approved by the line manager before it is worked; unapproved excess hours are recorded but not payable** *(BRU-HRM-02)* | **H** | HR Director |
| BRU-WFM-03 | Retrospective overtime approval requires an authority above the line manager, with a recorded reason | **A** | HR Director |
| BRU-WFM-04 | **Leave cannot be approved where team coverage would fall below the configured threshold** *(BRU-HRM-04)* | **H** | Ops Director |
| BRU-WFM-05 | **Daily working time may not exceed 10 hours, of which no more than 2 are overtime; weekly working time may not exceed 48 hours** *(Labour Act)* | **H** | HR Director |
| BRU-WFM-06 | **Women may not be scheduled between 22:00 and 06:00** except where a recorded statutory exception applies *(Labour Act)* | **H** | HR Director / Legal |
| BRU-WFM-07 | **Maternity leave of 16 weeks — 8 before and 8 after confinement — is applied per statute** | **H** | HR Director |
| BRU-WFM-08 | **Biometric enrolment requires specific consent; an alternative capture method must be available to an employee who declines** *(PDPA)* | **H** | CDO |
| BRU-WFM-09 | **Biometric templates are stored only in the Bangladesh-resident store** | **H** | CTO |
| BRU-WFM-10 | A locked period is immutable; correction is a forward adjustment into the next period | **H** | CFO |
| BRU-WFM-11 | Manual attendance entry requires an authorised approver, a reason and full audit | **H** | HR Director |
| BRU-WFM-12 | A published roster may only be changed with approval and notification within the notice period | **H** | Ops Director |
| BRU-WFM-13 | Medical certificates supporting sick leave are stored in M59 under S3 control, never in M55 | **H** | CDO |
| BRU-WFM-14 | Attendance derived from a job event is recorded with its source and cannot be silently overwritten by a manual entry | **H** | HR Director |
| BRU-WFM-15 | An employee on suspension or leave is published as unavailable to dispatch | **C** | HR Director |

*Classification: **H** hard block · **A** approved override · **C** computed*

---

## 10. Data Entities

### 10.1 Owned Entities

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.attendance.record` | `fix_attendance_record` | One attendance event pair | employee_id, date, check_in, check_out, source, device_id, gps_in, gps_out, geofence_result, verification_method, state |
| `fix.attendance.exception` | `fix_attendance_exception` | Detected anomaly | attendance_id, exception_type, detected_at, severity, state, regularisation_id |
| `fix.regularisation.request` | `fix_regularisation_request` | Correction request | employee_id, date, requested_change, reason, evidence_ref, approver_id, decision, decided_at |
| `fix.biometric.enrolment` | `fix_biometric_enrolment` **(resident store)** | Template reference and consent | employee_id, template_ref, device_type, consent_id, enrolled_at, active |
| `fix.attendance.device` | `fix_attendance_device` | Physical device | branch_id, device_code, model, ip_or_endpoint, last_seen, health_state |
| `fix.working.time.rule` | `fix_working_time_rule` | Statutory and policy limits | code, normal_hours_day, max_hours_day, max_overtime_day, max_hours_week, min_rest_hours, effective_from, jurisdiction |
| `fix.time.valuation` | `fix_time_valuation` | Payable time categories | attendance_id, category, hours, rate_multiplier, rule_version, valued_at |
| `fix.overtime.request` | `fix_overtime_request` | Pre-approval | employee_id, planned_date, planned_hours, business_reason, budget_ref, approver_id, decision, decided_at |
| `fix.leave.type` | `fix_leave_type` | Leave configuration | code, name_en, name_bn, paid, accrual_basis, max_balance, carry_forward, encashable, requires_certificate_after_days, statutory |
| `fix.leave.entitlement` | `fix_leave_entitlement` | Employee entitlement | employee_id, leave_type_id, period, entitled, accrued, taken, balance, carried_forward, expires_on |
| `fix.leave.request` | `fix_leave_request` | Leave application | employee_id, leave_type_id, from_date, to_date, days, reason, coverage_check_result, approver_id, state |
| `fix.holiday.calendar` | `fix_holiday_calendar` | Public and branch holidays | year, date, name_en, name_bn, scope, moon_dependent, confirmed |
| `fix.shift.pattern` | `fix_shift_pattern` | Shift definition | code, start_time, end_time, break_minutes, rotation, night_shift |
| `fix.roster` | `fix_roster` | A published roster | branch_id, period_start, period_end, state, published_at, published_by, notice_days |
| `fix.roster.entry` | `fix_roster_entry` | One person, one interval | roster_id, employee_id, date, shift_pattern_id, position, on_call |
| `fix.oncall.rota` | `fix_oncall_rota` | After-hours coverage | period, employee_id, coverage_window, escalation_order, allowance_applicable |
| `fix.availability` | `fix_availability` | Published projection | employee_id, interval_start, interval_end, state, skills, branch_id, zone_id |
| `fix.capacity.forecast` | `fix_capacity_forecast` | Forecast capacity | branch_id, zone_id, skill, period, available_hours, committed_hours, gap |
| `fix.attendance.period` | `fix_attendance_period` | Verification and lock | period, branch_id, state, verified_by, verified_at, locked_at, locked_by |
| `fix.timesheet.line` | `fix_timesheet_line` | Time allocation | employee_id, date, hours, project_id, contract_id, cost_centre_id |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.employee`, `fix.employment.contract` | M21 | Employee, status, contract terms |
| `fix.competency.assessment`, `fix.competency.assessment` | M22 | Skills attached to availability |
| `fix.branch`, `operating.unit` | M30 | Branch and zone structure |
| `fix.work.order`, `fix.visit` | M02 | Derived attendance source |
| `fix.geofence` | M02 | Geofence definitions for customer sites |
| `fix.incident.investigation` | M59 | Medical certificate reference (not content) |
| `fix.payslip` | M56 | Downstream consumer |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-WFM-01 | Biometric device event received | Validate, match to employee, create or complete the attendance record | Queue unmatched events for HR review |
| AUT-WFM-02 | Mobile clock-in submitted | Verify identity, evaluate geofence and accuracy, record with source | Flag low-accuracy or out-of-geofence for approval |
| AUT-WFM-03 | M02 job event received (departed, arrived, completed) | Derive attendance where no explicit clock event exists | Record as unverified for regularisation |
| AUT-WFM-04 | Device stops reporting for one hour | Alert branch manager and IT; switch the branch to fallback capture | Escalate |
| AUT-WFM-05 | End of day | Detect exceptions, notify affected employees and managers | — |
| AUT-WFM-06 | Exception unresolved 3 days before payroll cut-off | Escalate to branch manager, then HR Director | Escalate further; exception blocks period lock |
| AUT-WFM-07 | **Daily or weekly statutory limit approached or breached** | **Warn the manager before the breach; flag the actual breach for review and reporting** | **Escalate to HR Director** |
| AUT-WFM-08 | Leave request submitted | Check balance, run coverage check, route for approval with escalation | Route for manual assessment |
| AUT-WFM-09 | Leave approved or cancelled | Update availability projection within 60 seconds; notify dispatch | Escalate — stale availability causes mis-dispatch |
| AUT-WFM-10 | Roster published | Notify all affected staff through M27; update availability projection | Retry; alert on notification failure |
| AUT-WFM-11 | Accrual date reached | Accrue leave entitlement per rule; notify balance change | Alert HR |
| AUT-WFM-12 | Leave balance approaching lapse | Notify the employee and manager at 60 and 30 days | — |
| AUT-WFM-13 | **Payroll cut-off approaching** | Prompt verification of the attendance period; report unresolved exceptions | **Block lock until exceptions are cleared** |
| AUT-WFM-14 | Period verified | Lock the period; emit the lock event permitting payroll to run | Escalate to HR Director and CFO |
| AUT-WFM-15 | Capacity forecast gap detected | Alert Ops Director and branch manager | — |
| AUT-WFM-16 | Employee joins, moves or leaves (event from M21) | Create, adjust or close attendance, leave and roster records accordingly | Escalate |

---

## 12. Interfaces

### 12.1 Upstream — M55 Consumes

| Source | What | Mechanism |
|---|---|---|
| M21 Core HR | Employee, contract, position, status, joiner–mover–leaver events | REST + event |
| M22 Competency | Employee skills and valid certifications for skill-tagged availability | REST |
| M02 Field Service | Job events used to derive attendance; customer site geofences | Event + REST |
| M30 Platform Admin | Branch, zone, calendar and entity configuration | Master data |
| M29 Identity | Authentication; biometric consent record; residency enforcement | Service |
| M33 Party Master | Consent framework for biometric processing | REST |
| Biometric devices | Clock events | API / scheduled file |

### 12.2 Downstream — M55 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **M56 Payroll** | **Verified, locked, valued hours; leave taken; approved overtime; encashable balances** | **Event + REST — blocking dependency** |
| **M02 Field Service** | **Published availability with skills, by interval and zone** | **Event projection — blocking dependency** |
| M31 Workshop | Bench technician availability | Event projection |
| M04 Front Desk | Counter staff roster and shift alignment | REST |
| M27 Contact Centre | Agent roster within which M27 schedules against volume forecast | Event projection |
| M05 Managed Services | On-call rota for out-of-hours coverage | REST |
| M57 Performance | Hours worked as the denominator for productivity measures | Warehouse extract |
| M59 Health & Safety | Hours and shift patterns for fatigue and exposure analysis | Warehouse extract |
| M67 Project Management | Timesheet allocation to projects | Event |
| M25 Business Intelligence | Attendance, absence, overtime, capacity facts | Warehouse extract |
| P03 Admin Portal, P02 Technician App | Self-service attendance, leave and roster | REST |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `attendance.recorded` | employee, date, hours, source | M57, M25 |
| `attendance.exception_raised` | employee, date, type, severity | Manager, M25 |
| **`attendance.period_locked`** | **period, branch, verified by** | **M56 — permits payroll** |
| `overtime.approved` | employee, date, hours, approver | M56, M25 |
| `overtime.limit_breached` | employee, period, limit type | HR Director, M60 |
| `leave.approved` | employee, type, dates, days | **M02**, M56, M27 |
| `leave.cancelled` | employee, dates, balance restored | M02, M56 |
| **`availability.changed`** | **employee, interval, state, skills** | **M02, M27, M31, M05** |
| `roster.published` | branch, period, entries | M02, M27, M04, staff |
| `capacity.gap_detected` | branch, skill, period, shortfall | Ops Director, M35 |
| `leave.balance_updated` | employee, type, balance | P02, P03 |

### 12.4 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/attendance/clock` | POST | Mobile or web clock-in and clock-out | P02, P03 |
| `/api/v1/attendance/{employee}` | GET | Attendance history | P02, P03 |
| `/api/v1/attendance/exceptions` | GET | Exception queue | P03 |
| `/api/v1/attendance/regularise` | POST | Raise and approve regularisation | P02, P03 |
| `/api/v1/attendance/period/{id}/verify` | POST | Verify and lock a period | P03 |
| `/api/v1/leave/request` | POST | Leave application | P02, P03 |
| `/api/v1/leave/balance/{employee}` | GET | Balance and projection | P02, P03 |
| `/api/v1/roster/{branch}/{period}` | GET / POST | Roster construction and publication | P03 |
| **`/api/v1/availability`** | **GET** | **Availability by employee, interval, skill and zone** | **M02, M27, M31, M05** |
| `/api/v1/capacity/forecast` | GET | Capacity forecast and gaps | P03, P06, M35 |
| `/hooks/v1/biometric/{device}` | POST | Biometric device event ingestion | Devices |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R30 HR Manager | C R U D A | All employees, all branches; rule configuration |
| R31 HR Officer | C R U | Assigned scope — attendance, leave, regularisation |
| R06 Branch Manager | C R U A | Own branch — roster, approvals, regularisation, overtime |
| R05 Operations Director | R A | All — coverage threshold override, capacity |
| R07 Dispatch Manager | R | Availability and roster for assigned zones |
| R26 Finance Manager | R | Locked periods, overtime cost |
| **R40 Chief Data Officer** | R A | Biometric consent and residency compliance |
| **Employee (self)** | R U | **Own attendance, leave, roster only** |
| R35 Contact Centre Supervisor | R | Agent roster within own queues |
| R32 Quality Manager / ISO Coordinator | R | Attendance context for quality investigation |

**Field-level restrictions.** Biometric template references are visible to no operational role;
only the enrolment status is shown. GPS location history is accessible to R25, R06, R05 and
R32, and every access is logged.

**Segregation of duties.** The person who requests overtime cannot approve it (SOD-27). The
person who verifies an attendance period cannot be the same person who regularised the
exceptions within it above a threshold count (SOD-28).

---

## 14. Reports & Analytics

| Report / Board | Audience | Frequency | Key Content |
|---|---|---|---|
| Daily attendance board | Branch managers, Ops Director | Real time | Present, absent, late, on leave, exceptions by branch |
| **Exception queue** | **Branch managers, HR** | **Daily** | Open exceptions by type and age against payroll cut-off |
| **Period verification status** | **HR Director, CFO** | **Per cycle** | Branches verified, locked, outstanding — the payroll gate |
| Absence analysis | HR Director, Ops Director | Monthly | Absence rate by branch, type, day of week, seasonality |
| **Overtime report** | **HR Director, CFO, branch managers** | **Weekly** | Hours and cost by branch; approved versus worked; budget position |
| **Statutory limit breaches** | **HR Director, GRC** | **Weekly** | Daily 10-hour and weekly 48-hour breaches, with cause |
| Leave liability | CFO, HR Director | Monthly | Accrued unused leave and encashment exposure — feeds M56 provision |
| Leave calendar | Managers, dispatch | Continuous | Team and branch leave forward view |
| **Roster publication compliance** | **Ops Director** | **Weekly** | Rosters published before the period with the required notice |
| **Capacity forecast** | **Ops Director, CCO** | **Weekly** | Available capacity by branch, skill and zone against forecast demand |
| Attendance integrity | HR Director, GRC | Monthly | Fraud signals, proxy-attendance patterns, manual entry volume |
| On-call utilisation | Ops Director, Corporate Services Head | Monthly | Callouts, response, allowance cost |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W6 Target | W8 Target |
|---|---|---|---|---|
| KPI-223 | **Attendance capture completeness** | sign-in books | 96% | **> 99%** |
| KPI-224 | Leave balance disputes | frequent | < 15/year | **< 5/year** |
| KPI-225 | **Rosters published before the period with required notice** | ad hoc | 90% | **100%** |
| KPI-226 | **Attendance periods locked before payroll run** | n/a | **100%** | **100%** |
| KPI-227 | Attendance exceptions unresolved at payroll cut-off | n/a | < 2% | **< 0.5%** |
| KPI-228 | **Overtime worked without pre-approval** | unknown | < 5% | **< 1%** |
| KPI-229 | Overtime cost against budget | unmeasured | within 10% | **within 5%** |
| KPI-230 | **Statutory working-hour breaches** | unknown | baselined | **Reducing to zero** |
| KPI-231 | Manual attendance entries as a share of total | 100% | < 8% | **< 3%** |
| KPI-232 | **Availability accuracy — dispatch assignments to unavailable staff** | unknown | < 2% | **< 0.5%** |
| KPI-233 | Biometric enrolment coverage (of consenting employees) | 0% | 90% | **> 97%** |
| KPI-234 | Availability query response time | — | < 300 ms | **< 200 ms** |

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo `hr_attendance`, `hr_holidays` | 18% |
| L2 | OCA `hr_attendance_geolocation`, `hr_holidays_public`, `hr_attendance_*` | 12% |
| L5 | `cd_attendance`, `cd_leave`, `cd_roster`, `cd_capacity`, `cd_overtime` + device adapters | 70% |

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 6 of 6 identifiers below are claimed by another module: **CD-070** also claimed by M15; **CD-071** also claimed by M44; **CD-072** also claimed by M42; **CD-073** also claimed by M16; **CD-074** also claimed by M44; **CD-075** also claimed by M17. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID *(provisional)* | Component | Type | Effort |
|---|---|---|---|
| CD-070 | **`cd_attendance`** — capture, geofence, derived attendance, exceptions, valuation, period lock | Odoo module + service | **7 PW** |
| CD-071 | `cd_leave` — types, entitlement, accrual, coverage check, balance projection | Odoo module | 4 PW |
| CD-072 | `cd_roster` — shift patterns, roster construction, publication, change control, on-call | Odoo module | 5 PW |
| CD-073 | **`cd_capacity`** — availability projection, skill tagging, capacity forecast | Service | **3 PW** |
| CD-074 | `cd_overtime` — request, pre-approval, budget, statutory limit enforcement | Odoo module | 2 PW |
| CD-075 | Biometric device adapter and health monitoring | Service | 1 PW |

### 16.3 Sequencing

| Prerequisite | Reason |
|---|---|
| **M21 Core HR** | **Blocking** — attendance attaches to an employee with a contract |
| **Biometric devices procured and installed** | **Blocking** *(ASM-11)* — this is a procurement and installation programme across 51+ branches, not a software task |
| **Bangladesh-resident store** | **Blocking** — biometric templates are sensitive personal data *(DEP-31)* |
| **Biometric consent notice approved** | **Blocking** — specific consent is required before enrolment *(PDPA)* |
| M22 Competency | Skill-tagged availability — may be stubbed and completed in the same wave |
| M30 Platform Admin | Branch, zone and calendar structure |
| M02 Field Service | Derived attendance from job events; geofences — already live from W2 |

> **Critical path note.** M55 is a **blocking dependency for both M56 Payroll and M02 dispatch
> quality**. If the biometric device programme slips, M55 must launch on GPS mobile and web
> capture alone, with biometric added later. That fallback should be planned now, not
> improvised.

### 16.4 Data Migration

| Source | Volume | Target | Wave |
|---|---|---|---|
| Leave balances (spreadsheets) | 500+ | `fix.leave.entitlement` | W5 |
| Leave policy and entitlement rules | Policy documents | `fix.leave.type` | W5 |
| Public holiday calendar | Current and next year | `fix.holiday.calendar` | W5 |
| Historical attendance | **Not migrated** — sign-in books are not machine-readable and not reliable | — | — |
| Shift patterns and rosters | **Authored, not migrated** — none exist in structured form | `fix.shift.pattern` | W5 |

> **Migration warning.** Opening leave balances must be **agreed with each employee before
> cutover**, not imported and announced. A disputed opening balance is the fastest way to
> lose staff confidence in the whole system.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | **Payroll cannot run for a period that is not verified and locked** | **Negative test through UI and API** |
| AC-02 | **Overtime worked without pre-approval is recorded but not passed to payroll as payable** | **Negative test end-to-end with M56** |
| AC-03 | Leave approval is blocked where coverage falls below threshold | Negative test |
| AC-04 | **Daily 10-hour and weekly 48-hour limits are enforced in scheduling and flagged in actuals** | **Test matrix across shift patterns** |
| AC-05 | **Women cannot be scheduled between 22:00 and 06:00 without a recorded exception** | **Negative test** |
| AC-06 | Maternity leave applies 16 weeks with the statutory split | Scripted test |
| AC-07 | **Biometric enrolment is blocked without recorded specific consent, and an alternative method is available** | **Negative test** |
| AC-08 | **Biometric templates are absent from every regional store, cache, log and export** | **Data-flow audit** |
| AC-09 | Attendance derived from M02 job events is recorded with its source and not duplicated by a separate clock-in | End-to-end test with 20 technicians |
| AC-10 | Mobile clock-in works offline and synchronises without loss | Offline test, 24 hours |
| AC-11 | **Availability updates reach M02 within 60 seconds of a leave or roster change** | **Timed test** |
| AC-12 | A locked period is immutable; correction carries forward | Negative test |
| AC-13 | Rosters publish with the required notice and staff are notified | Four consecutive weeks |
| AC-14 | Availability query returns in ≤ 200 ms under dispatch load | Load test |
| AC-15 | Opening leave balances are agreed with employees before cutover | Signed acknowledgement sample, 10% of staff |
| AC-16 | HR Director, two branch managers and the Dispatch Manager sign off UAT | Signed UAT record |

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Have biometric devices been procured and installed across 51+ branches?** *(ASM-11)* If not, what is the fallback plan and its cost? | Ops Director / CTO | **W5 minus 4 months** |
| Q-02 | **Do employees consent to biometric processing, and what is the alternative for those who decline?** | HR Director / CDO | **W5 minus 3 months** |
| Q-03 | What is the leave entitlement policy by contract type and service length? This must be documented before it can be configured. | HR Director | **W5 minus 3 months** |
| Q-04 | What coverage threshold applies per branch and skill for leave approval? | Ops Director | W5 build |
| Q-05 | Is time off in lieu offered, or is all overtime paid? | HR Director / CFO | W5 build |
| Q-06 | How are moon-dependent public holidays confirmed and by whom, given they are announced close to the date? | HR Director | W5 build |
| Q-07 | Do branches currently operate shifts, or is it a single working day? Rostering is a new management practice if the latter. | Ops Director | **W5 design** |
| Q-08 | What is the payroll cut-off date, and how many days does that leave for exception resolution? | HR Director / CFO | W5 build |
| Q-09 | Are opening leave balances reconstructable and agreed, or must the Company set an agreed opening position? | HR Director | **W5 minus 2 months** |

**Q-01 is on the critical path.** Without devices, M55 launches degraded, and M56 payroll
accuracy depends on it.

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §3, §5, §7 · `M21_Core_HR_and_Employee_Lifecycle.md` ·
`M56_Payroll_Benefits_and_Statutory_Compliance.md` ·
`M22_Learning_Competency_and_Certification.md` ·
`03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md` ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §6.3–6.4

**Workspace evidence**
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` BR-HRM-004/005/006,
BRU-HRM-02/04/05, §6.2 Process 9, ASM-11 · `1000FiX_ERP_System_Comprehensive_URD.md`
Personas 9–10

**External benchmark and regulation** *(verified 2026-08-12)*
**Bangladesh Labour Act 2006 (as amended)** — maximum 8 normal hours per day with 2 hours
overtime and a 10-hour daily total; 48 hours per week; casual, sick and annual leave;
**maternity leave of 16 weeks, 8 before and 8 after childbirth**; **prohibition on women
working between 22:00 and 06:00** · **Bangladesh Personal Data Protection Act 2026** —
biometric identifiers are sensitive personal data requiring specific consent and subject to
cross-border transfer restriction · SAP SuccessFactors Time Management — time valuation feeding
payroll · Oracle HCM Time and Labor — configurable rules engine · Workday Absence — accrual and
balance projection · IFS Mobile Workforce Management — **capacity planning preceding schedule
optimisation** · Field workforce attendance practice — **geofenced zones triggering attendance
on entry and exit; biometric proves who clocked in, geofence proves where**; single-tap status
change as the usability standard

---

*Module M55 · Category H · 1000FiX ERP System v2.0 · CONFIDENTIAL*
