---
id: SP-022
title: SOP — Time, Attendance and Roster
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR with Operations
author: Business Process Lead with HR Operations
reviewers: [HR Manager, Operations Director, CFO, Legal Counsel, Data Protection Officer, Branch Managers Forum, Localisation Lead]
approver: HR Manager with Operations Director
content_class: C
purpose: >
  Field technician attendance is geofenced and 500+ employees work across shifts, branches and
  vans. Exception handling must be defined before disputes arise, because an attendance dispute
  is a wage dispute. This SOP governs roster publication, clock-in rules, geofence exceptions,
  overtime approval, leave interaction and the verification and locking of the period that
  payroll depends on.
traces_to: [M55, M21, M02, P02, P03, MD-042, MD-041, MD-008, SP-004, SP-005, SP-006, SP-008, SP-021, SP-030, LG-008]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: SP-022_SOP_Time_Attendance_and_Roster_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M55_Time_Attendance_and_Workforce_Scheduling.md — SOD-27 overtime requester cannot approve; SOD-28 verifier cannot regularise above threshold
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §3 BRU-FSM-05 GPS only on duty in working hours, BRU-FSM-10 scheduling breaching working-time limits requires approved overtime; §10 BRU-HRM-02, BRU-HRM-04, BRU-HRM-05
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-061 attendance capture completeness — manual baseline, 98% target
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Labour Act 2006 — statutory limits on daily and weekly working hours and the overtime rate; section references to be confirmed by Legal Counsel against the consolidated Act
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# SOP — Time, Attendance and Roster

| Item | Value |
|---|---|
| SOP ID | `SP-022` |
| Process owner | HR Manager (R30) with Operations Director (R05) |
| Roles performing | `R06` Branch Manager · `R07` Dispatch Manager · `R09` Workshop Supervisor · `R31` HR Officer · all employees |
| Systems used | `P03` HR console (`UI-030`) · `P02` · `M55` |
| Frequency / volume | Daily capture; weekly roster publication; monthly verification for 500+ employees |
| ISO 9001 clause reference | 7.1.2 people · 5.3 assigned authorities · 7.5.3 documented information |

---

## 1. Purpose and Outcome

**Purpose.** To publish a roster people can plan around, capture attendance accurately including
for staff who never enter a building, handle exceptions fairly and consistently, and hand payroll
a verified, locked period.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The roster was published before the period it covers | Publication timestamp |
| Attendance capture completeness reaches 98% | `KPI-061` |
| Every geofence exception carries a reason and a decision | Exception register |
| Overtime was approved **before** it was worked | `BRU-HRM-02`, `SOD-27` |
| Scheduling never breached working-time limits without approved overtime | `BRU-FSM-10` |
| The period was verified and locked before payroll ran | `BRU-HRM-05` |
| GPS was captured only on duty, during working hours | `BRU-FSM-05`, `LG-008` |

---

## 2. Scope

**Applies to:** roster planning and publication; clock-in and clock-out at branches, workshops and
in the field; geofence and location exceptions; overtime request and approval; leave interaction;
period verification and lock.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Payroll calculation and disbursement | `SP-021` |
| Leave policy and entitlement | `M55` policy; `SP-023` for the employment relationship |
| Job assignment and dispatch optimisation | `SP-008`, `M02` |
| Recruitment and onboarding | `SP-023` |
| Disciplinary process arising from attendance | `SP-023` and HR policy; escalated per `SP-005` PE-E9 |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Roster | The published plan of who works when and where |
| Clock event | A recorded start or end of a working period |
| Geofence | The coordinate boundary within which a field clock event is expected (`BRU-FSM-06`) |
| Exception | Any clock event outside the expected pattern — missing, late, outside geofence, outside shift |
| Regularisation | The correction of an exception by an authorised person |
| Verification | The supervisor's confirmation that a period's attendance is correct |
| Lock | The freeze of a verified period; payroll cannot run without it (`BRU-HRM-05`) |
| Coverage minimum | The configured minimum staffing below which leave cannot be approved (`BRU-HRM-04`) |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Working patterns and shift definitions | `MD-042` | Patterns configured per role and site |
| Calendar including public holidays | `MD-041` | Bangladesh holidays and Eid periods loaded |
| Position and reporting line | `MD-008` | Every employee has a supervisor who can verify |
| Geofence definitions | `MD-003`, `MD-005` | Branch and customer-site boundaries defined |
| Leave balances | `M55` | Entitlement current |
| Coverage minimums | Configuration | Set per site and per skill |
| Employee consent and privacy notice | `LG-008` | Location capture is disclosed, limited and lawful |

---

## 5. Procedure

### 5.1 Roster

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | R06 / R07 / R09 | Build the roster against forecast demand, skills and coverage minimums | `P03` | Draft roster |
| 2 | R06 | Check working-time limits; scheduling that would breach them requires approved overtime **first** (`BRU-FSM-10`) | `P03` | Limit check |
| 3 | R06 | Publish at least the configured notice period before the roster starts. A roster published late is a roster nobody planned around | `P03` · `NT-*` | Published roster |
| 4 | Employees | View the roster; raise swap or availability requests | `P02` / `P03` | Requests |
| 5 | R06 | Approve or decline swaps against coverage and skill | `P03` | Swap decisions |

### 5.2 Attendance capture

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | Branch and workshop staff | Clock in at the site device or `P03` under their own identity | `P03` | Clock event |
| 7 | Field staff | Clock in through `P02`; location captured **only while on duty during working hours** (`BRU-FSM-05`) | `P02` | Geotagged clock event |
| 8 | Field staff | Where offline, the clock event queues and syncs (`AUT-014`) | `P02` | Queued event |
| 9 | All | Clock out at the end of the working period | `P02` / `P03` | Clock event |
| 10 | System | Flag exceptions: missing, late, early, outside geofence, outside shift, excessive duration | `M55` | Exception list |

### 5.3 Exception handling

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 11 | Employee | Explain the exception with a reason at the time, not at month end | `P02` / `P03` | Employee explanation |
| 12 | R06 / R07 / R09 | Review daily. **Daily review is the control; a month of unreviewed exceptions cannot be reconstructed** | `P03` | Review record |
| 13 | R06 | Regularise where justified, with the reason recorded | `P03` | Regularisation |
| 14 | R30 | Above the threshold count of regularisations in a period, a different person verifies (`SOD-28`) | `P03` | Independent verification |
| 15 | R06 | Escalate a pattern of geofence exceptions for one person to a conversation, not a deduction | `SP-005` PE-E10 | Escalation record |

### 5.4 Overtime and leave

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | Employee | Request overtime **before** working it | `P02` / `P03` | Request |
| 17 | Line manager | Approve or decline. **The requester may never approve** (`SOD-27`) | `P03` | Approval |
| 18 | System | Unapproved overtime does not count for payroll (`BRU-HRM-02`) | `M55` | Exclusion |
| 19 | Employee | Request leave | `P03` | Leave request |
| 20 | Line manager | Approve against coverage; below the coverage minimum requires an override (`BRU-HRM-04`, class **A**) | `P03` | Leave decision |
| 21 | R06 | Re-roster to cover approved leave before it starts | `P03` | Roster update |

### 5.5 Verification and lock

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 22 | R06 / R07 / R09 | Verify the period: every day accounted, every exception resolved | `P03` | Verification |
| 23 | R30 | Confirm all sites verified. **An unverified site blocks payroll for everyone** — that is the intended pressure | `P03` | Site completeness |
| 24 | R30 | Lock the period (`BRU-HRM-05`) | `M55` | Period lock |
| 25 | R30 | Hand the locked period to payroll | `SP-021` | Handover |
| 26 | R30 | Post-lock corrections are off-cycle and approved, never a silent unlock | `SP-004` | Correction record |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 2 | Roster would breach working-time limits | Do not publish it. Obtain approved overtime first, or re-roster (`BRU-FSM-10`) | R06 → R30 |
| 3 | Roster cannot be published in the notice period | Publish what is fixed and flag the remainder; late publication is recorded, not normalised | R06 |
| 7 | Employee has no device or the device fails | Supervisor records the clock event on their behalf, with the reason. **Never a shared device login** | R06 |
| 7 | Location capture outside working hours | Blocked (`BRU-FSM-05`). If observed, it is a privacy incident | DPO |
| 10 | Clock-in outside the geofence | Exception with a reason; genuine causes are common — a customer site moved, a job started early, poor GPS in a dense area | R07 |
| 12 | Exceptions not reviewed daily | Escalate to the supervisor's manager. Backlogged exception review is the root cause of month-end payroll disputes | R30 |
| 13 | The employee disputes the regularisation | Record both positions; escalate to R30. Do not resolve a wage-affecting dispute by manager fiat | R30 |
| 14 | Regularisations exceed the threshold | Independent verification required (`SOD-28`); a high regularisation rate means the capture method does not fit the work | R30 |
| 16 | Overtime worked without prior approval | It does not count automatically (`BRU-HRM-02`). Where the work genuinely happened and was necessary, retrospective approval is a documented exception — **and a repeated pattern is a rostering failure, not an employee failure** | R30 |
| 20 | Leave would take coverage below minimum | Override with a recorded reason (`BRU-HRM-04`, class **A**), or decline with an alternative date | R06 |
| 22 | A day cannot be accounted for | Do not verify the period. An unaccounted day is either unpaid work or unworked pay | R06 → R30 |
| 24 | A site has not verified by the cut-off | Escalate to R05 Operations Director; payroll cannot run (`SP-005` PE-E3) | R30 → R05 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Overtime | Any | Line manager, **before** it is worked (`SP-004` A-57, `SOD-27`) | R06, then R30 |
| Retrospective overtime approval | Any | R30, as a documented exception | CFO |
| Leave below the coverage minimum | Any | R06 override, logged (`SP-004` A-58, `BRU-HRM-04`) | R05 |
| Attendance exception regularisation above the threshold count | Per config | Verifier ≠ regulariser (`SP-004` A-59, `SOD-28`) | R30 |
| Unlock a locked period | Any | R30 + CFO; never a silent unlock | CFO |
| Roster published inside the notice period | Any | R06, recorded | R05 |
| Record a clock event on an employee's behalf | Any | Line manager, with the reason | R06 |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Site fails to verify by the cut-off | Escalate the same day; payroll is blocked for all (`SP-005` PE-E3) | R30 → R05 | Verification tracker |
| Attendance device or `P02` unavailable | Fallback in §9 | R06, R33 | Manual attendance sheet |
| Geofence exception pattern for one person | Conversation and investigation, not deduction (`SP-005` PE-E10) | R06 → R07 | Exception review |
| Employee works through a rest period | Working-time issue; address it in rostering, and record it | R06 → R30 | Working-time record |
| Lone worker fails to clock out | Welfare check before any payroll consideration | R07 → HSE (`SP-008` §8) | Lone-worker log |
| Employee alleges unpaid time | Investigate from clock records, job records and dispatch history together | R30 | Grievance path (`SP-005` PE-E9) |
| Location data requested for a purpose other than attendance and dispatch | Refuse; route to DPO. Purpose limitation is a legal constraint | DPO, Legal | `LG-008` |
| Roster repeatedly published late | Treated as a management issue with a named owner | R05 | Operations review |
| Locked period found to contain an error | Off-cycle correction with approval; the lock is not reversed silently | R30 + CFO | Correction record |

---

## 9. Manual Fallback

Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Each site maintains a **pre-numbered manual attendance register**: date, name, employee number, in, out, breaks, signature of the employee and the supervisor |
| 2 | Field staff telephone or message their supervisor at start and end; the supervisor records it with the time received |
| 3 | Overtime approval is recorded on the **overtime approval form**, signed before the work where at all possible |
| 4 | The supervisor signs the register daily, not weekly. Daily signature is the control |
| 5 | **Back-enter every attendance record within 48 hours**, preserving dates and times |
| 6 | R30 reconciles registers against the system before locking; unaccounted days are resolved, not estimated |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Payroll cannot finalise until attendance is verified and locked | Preventive (`BRU-HRM-05`) | Per period | Hard block |
| Overtime pre-approved before it counts | Preventive (`BRU-HRM-02`) | Per record | Hard block |
| Overtime requester cannot approve | Preventive (`SOD-27`) | Per record | Hard block |
| Verifier cannot regularise above threshold | Preventive (`SOD-28`) | Per period | Threshold block |
| Scheduling breaching working-time limits requires approved overtime | Preventive (`BRU-FSM-10`) | Per roster | Hard block |
| Leave below coverage minimum requires override | Preventive (`BRU-HRM-04`) | Per request | Approved override |
| GPS captured only on duty during working hours | Preventive (`BRU-FSM-05`) | Continuous | Privacy control |
| Individual identity on every clock event | Preventive | Per event | No shared logins |
| Daily exception review | Detective | Daily | Review record |
| Regularisation rate by site and supervisor | Detective | Monthly | HR report |
| Attendance capture completeness | Detective | Monthly | `KPI-061` |
| Roster publication timeliness | Detective | Weekly | Publication report |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Request overtime | Approve it (`SOD-27`) | Hard block | — |
| Verify an attendance period | Regularise its exceptions above the threshold (`SOD-28`) | Threshold block | Regularisation above threshold routes to R30 |
| Record a clock event on someone's behalf | Verify the period containing it | Detective review | R30 samples supervisor-recorded events |
| Manage the roster | Approve one's own overtime on it | Hard block (`SOD-27` applies to managers equally) | R06's own overtime is approved by R05 |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-061` | Attendance capture completeness | manual | 98%; stretch 99% |
| `KPI-065` | Employee self-service adoption | 0% | 75%; stretch 85% |
| Roster publication timeliness | Rosters published within the notice period | untracked | 100% |
| Exception regularisation rate | Exceptions requiring manual correction | untracked | Falling; a high rate indicates unfit capture |
| Verification on time | Sites verified by the cut-off | untracked | 100% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `UI-030` Workspace — HR Console Copy · `UI-012` `P02` Technician App Copy Pack | The screens used |
| [`SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) | Consumes the locked period |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field clock events and geofence |
| [`SP-023_SOP_Recruitment_and_Onboarding.md`](SP-023_SOP_Recruitment_and_Onboarding.md) | Joiners and leavers affecting the roster |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Lone-worker and working-time safety |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-042_Shift_Roster_and_Working_Pattern_Master.md) | Patterns and limits |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Holidays and Eid periods |
| `LG-008` Employee Privacy and Location Data Notice | Lawful basis for location capture |
| `TR-015` Course Pack — HR and Payroll · `TR-011` Course Pack — Branch Manager | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Manager with Operations Director (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | Confirm statutory daily and weekly working-hour limits and the overtime rate against the consolidated Bangladesh Labour Act 2006. Cited here at class **P2** | Legal Counsel | Before `Approved` |
| O-02 | Confirm the lawful basis, retention and purpose limitation for location capture, and align `LG-008` | Data Protection Officer + Legal Counsel | Before W2 |
| O-03 | Set roster notice period, coverage minimums and the regularisation threshold from `SP-002` baseline | HR Manager + Operations | Before W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Daily exception review named as the control, with the month-end consequence stated
- [x] Geofence exceptions treated as investigable, not automatically punitive
- [x] Location capture bounded by purpose and working hours
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] O-01 statutory working-time limits verified — **outstanding**
- [ ] O-02 privacy basis confirmed and `LG-008` aligned — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Manager and Operations Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
