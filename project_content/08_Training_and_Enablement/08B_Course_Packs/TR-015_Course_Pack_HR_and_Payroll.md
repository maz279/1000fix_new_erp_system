---
id: TR-015
title: Course Pack — HR and Payroll
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development with HR
author: Learning & Development with HR and Payroll
reviewers: [HR Director, Finance Manager, Legal Counsel, Quality Manager, HSE Lead, Localisation Lead]
approver: HR Director with Finance Manager
content_class: D
purpose: >
  Trains the HR team on the employee lifecycle, attendance, leave, payroll input and statutory
  filing. Payroll errors affect every employee, are immediately visible, and carry legal
  consequence; and HR is the function that operates the competence and certification records the
  whole training regime depends on.
traces_to: [M21, M22, M55, M56, M57, M58, M59, P03, MD-008, MD-009, MD-012, MD-042, MD-043, TR-001, TR-002, TR-004, TR-006, TR-022, UI-030, SP-021, SP-022, SP-023]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: TR-015_Course_Pack_HR_and_Payroll_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md, SP-022 time and attendance, SP-023 recruitment and onboarding
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-HRM-02 overtime must be pre-approved before it counts for payroll; BRU-HRM-05 payroll cannot be finalised until attendance is verified and locked; BRU-HRM-06 payroll requires two approvals, HR Manager and CFO; BRU-HRM-07 payroll visibility restricted; BRU-LMS-01 overdue mandatory training restricts work types
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-060 payroll corrections per run under 0.5% then 0.3%; KPI-061 attendance capture completeness 98% then 99%; KPI-062 certifications current; KPI-064 mandatory training completion
    verified: 2026-08-17
    class: P1
  - source: Bangladesh Labour Act 2006 with Bangladesh Labour Rules 2015 — employment conditions, wages, working hours, safety committees at 50+ workers, accident reporting
    verified: 2026-08-17
    class: P1
    note: Legal confirmation outstanding — TR-001 O-02
supersedes: none
review_due: 2027-02-17
---

# Course Pack — HR and Payroll

| Item | Value |
|---|---|
| Audience role(s) | `R30` HR Manager · `R31` HR Officer |
| Headcount | **4–8** |
| Duration | **10 hours** over three days, plus 5 days supervised OJT |
| Delivery mode | Classroom with sandbox; single cohort |
| Language | English primary with Bengali parallel (`DS-18`) |
| Prerequisites | Layer 1 universal core |
| Certification outcome | Functional competence record (`TR-006` cell 9) |
| Wave | W5 |

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Maintain the employee master to `MD-012` standard, including sensitive-data handling | Sandbox + items |
| 2 | Operate joiner, mover and leaver end to end, including **access and competence consequences** | Practical — `SP-023` |
| 3 | Process attendance and exceptions, and lock the period correctly | Sandbox — `BRU-HRM-05`, `KPI-061` |
| 4 | Apply leave policy and coverage rules | Items — `BRU-HRM-04` |
| 5 | Verify overtime pre-approval before it reaches payroll | Items — `BRU-HRM-02` |
| 6 | **Run payroll to `SP-021` with dual approval, and reconcile it** | **Critical practical** — `BRU-HRM-06` |
| 7 | Prepare statutory deductions and filings correctly | Critical items — `MD-043` |
| 8 | **Protect payroll confidentiality** — who may see what | **Critical items** — `BRU-HRM-07` |
| 9 | **Operate the competence and certification register: assign curricula, track expiry, act before lapse** | Sandbox — `M22`, `KPI-062` |
| 10 | Discharge the employer's statutory safety-record duties | Items — Labour Rules, `M59` |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to HR and payroll transactions | Layer 1 core | On release (`TR-024`); 24 months. **Statutory content on any Labour Act / Rules change** |

---

## 3. Module Outline

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | HR as a control function, not an administrative one | 30 min | Facilitated |
| 2 | Employee master, position structure and sensitive data | 75 min | Practice — `MD-008`, `MD-012` |
| 3 | **Joiner, mover, leaver — and what each does to access and competence** | 90 min | Practical — `SP-023`, `M29`, `M22` |
| 4 | Attendance, exceptions and period lock | 75 min | Sandbox — `SP-022` |
| 5 | Leave, coverage and approval | 45 min | Items |
| 6 | Overtime pre-approval discipline | 30 min | Items — `BRU-HRM-02` |
| 7 | **Payroll run, dual approval and reconciliation** | 120 min | Practical — `SP-021` |
| 8 | **Statutory deductions and filing** | 90 min | Practice — `MD-043` |
| 9 | **Payroll confidentiality and access boundaries** | 45 min | Items — `BRU-HRM-07` |
| 10 | **Operating the competence register** — assignment, expiry, lapse | 90 min | Sandbox — `M22`, `TR-002` |
| 11 | Employer safety-record duties | 45 min | Facilitated — Labour Rules, `M59` |
| 12 | Reading HR data — attrition, coverage, single points of failure | 45 min | Walkthrough — `UI-030`, `P06` |
| | **Total** | **~10 hours** | |

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 3 | **A leaver who keeps access is a security incident; a leaver whose articles are unowned is a knowledge loss** (`KB-015` `KR-02`). The leaver checklist covers both | *"IT handles access."* |
| 4 | Payroll cannot be finalised until attendance is verified and locked (`BRU-HRM-05`). Locking late compresses every downstream step | *"We'll lock it after payroll."* |
| 6 | Overtime not pre-approved does not count. Approving retrospectively defeats the control (`BRU-HRM-02`) | *"They worked it, so we must pay it."* — pay it and fix the process, but record the exception |
| 7 | Two approvals — HR Manager **and** CFO — are not bureaucracy; they are the only control over the single largest cash outflow | *"The CFO always signs."* |
| 9 | An employee's payroll record is visible to them and to HR/finance, **never to peers or to line managers below HR Manager** (`BRU-HRM-07`) | *"Their manager asked."* |
| 10 | **HR operates the gate that stops an uncertified technician being assigned.** A certification allowed to lapse is a job that cannot be done and a claim that cannot be made | *"Certificates are a technical matter."* |

---

## 5. Participant Workbook Contents

Employee master field standard (`MD-012`) · joiner/mover/leaver checklists **including access and
article-ownership transfer** · attendance exception guide · leave and coverage rules · overtime
pre-approval rule · **payroll run checklist and dual-approval flow** · statutory deduction and
filing calendar · **confidentiality boundaries** · competence register operating guide ·
safety-record duties · **my access scope**.

---

## 6. Exercises

| # | Exercise | Sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Create and maintain three employee records | Sandbox | Joiner set incl. sensitive fields | Complete, correctly classified |
| 2 | **Leaver with access and article ownership** | Sandbox | Leaver with owned `KNW-` articles | Access revoked; **ownership transferred** (`KR-02`) |
| 3 | Attendance period with five exceptions | Sandbox | Seeded exceptions | All resolved; period locked correctly |
| 4 | Overtime without pre-approval | Scenario | Retrospective overtime claim | Recognises the breach; records the exception |
| 5 | **Payroll run with a seeded error** | Practical | Payroll period with one incorrect element | Error found **before** approval; dual approval obtained |
| 6 | Statutory deduction calculation | Practice | Deduction scenarios | All correct |
| 7 | **Confidentiality scenario** | Scenario | Line manager requests a payroll record | Refuses; explains; records the request |
| 8 | **Certification lapse management** | Sandbox | Three technicians with expiring certifications | All actioned before lapse (`AS-10`) |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 9 form, 30 items | 25% | 80%, **100% on confidentiality and statutory items** | 3 | 24 months |
| **Payroll run practical (exercise 5)** | 25% | Error found before approval | 3 | 24 months |
| Statutory deduction (exercise 6) | 15% | All correct | 3 | **On Labour Act / Rules change** |
| Leaver and certification exercises (2, 8) | 20% | Both passed | 3 | 24 months |
| Attendance, overtime, confidentiality (3, 4, 7) | 15% | All passed | 3 | 24 months |
| **OJT sign-off — one full payroll cycle observed** | Gate | HR Director | — | — |

---

## 8. Job Aids Produced

Joiner/mover/leaver checklists · attendance exception guide · **payroll run checklist** · statutory
filing calendar · confidentiality boundary card · **certification expiry action guide** · employee
master field standard. All in `TR-022`.

---

## 9. Trainer Requirements

L&D with **HR Director delivering modules 7, 9 and 11** · Finance Manager co-delivers module 7 ·
Legal or Compliance for module 11 · sandbox with a full payroll period · cohort maximum 8 — one
cohort covers the population.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence running a payroll cycle unaided | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and payroll practical pass | > 85% first attempt |
| **Behaviour** | Attendance lock timeliness · overtime pre-approval rate · **certification lapses** · confidentiality incidents | **Lapses zero**; incidents zero |
| **Result** | **`KPI-060` payroll corrections under 0.5% then 0.3%** · **`KPI-061` attendance capture 98% then 99%** · **`KPI-062` certifications current 100%** · `KPI-064` mandatory training completion | Per `06-02` |

**Required Drivers** (`LS-04`): reinforce — payroll checklist and expiry action guide · encourage —
HR Director runs the first cycle alongside · monitor — the four behaviour signals · reward —
competence record; payroll accuracy visible.

> **HR is the only function whose training directly moves four separate KPIs**, three of which
> (`KPI-062`, `KPI-064` and, indirectly, `KPI-063`) are the training regime's own measures. If this
> pack fails, the training function cannot measure itself.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-022_SOP_Time_Attendance_and_Roster.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-022_SOP_Time_Attendance_and_Roster.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-023_SOP_Recruitment_and_Onboarding.md) ·
[`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-043_Payroll_Element_and_Statutory_Deduction_Register.md) ·
[`../08A_Framework/TR-002_Role_Based_Curriculum_Map.md`](../08A_Framework/TR-002_Role_Based_Curriculum_Map.md) — HR operates it ·
[`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md) — HR operates renewal ·
`UI-030` HR console copy · `KB-015` `KR-02` article-ownership transfer on leaving.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MD-043` payroll elements and statutory deductions are unpopulated.** Modules 7 and 8 have no live rates | HR with Finance | **W5 — blocking** |
| **O-02** | `TS-002` sandbox with a full payroll period does not exist | Test Lead with HR | W5 |
| **O-03** | **`KR-02` requires the leaver checklist to transfer knowledge-article ownership.** Whether `SP-023` includes it is unconfirmed (`KB-015` `O-04`) | HR Manager with Knowledge Manager | W5 |
| **O-04** | **This pack is W5 but HR operates the competence register from W1.** Module 10 content is needed four waves before the pack is scheduled — raised as audit finding **TR-04** | Training Lead with HR Director | **W1 interim for module 10** |
| **O-05** | Statutory content rests on `TR-001` `O-02`, unconfirmed by Legal | Legal Counsel with HR Director | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); four Level 4 KPIs named (`LS-01`)
- [x] Leaver module covers access **and** knowledge-article ownership (`KR-02`)
- [x] Payroll dual approval and confidentiality taught as controls with critical assessment items
- [x] HR's role operating the competence register made explicit — the training regime's own dependency
- [x] Statutory refresh tied to legislative change rather than a calendar
- [x] OJT sign-off across a full payroll cycle (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-HRM-02`/`-04`/`-05`/`-06`/`-07`, `BRU-LMS-01` cited to `05-05`; `KPI-060`…`-064` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-04` module 10 needed at W1, pack scheduled W5 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Director and Finance Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
