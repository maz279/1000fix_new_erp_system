---
id: SP-030
title: SOP — Health, Safety and Incident Reporting
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HSE
author: Business Process Lead with HSE
reviewers: [HSE Lead, Operations Director, HR Manager, Legal Counsel, Quality Manager, CFO, Localisation Lead]
approver: Operations Director with Legal Counsel
content_class: C
purpose: >
  Field technicians work with electricity, refrigerants, lithium batteries and vehicles, often
  alone, in customers' homes. Safety process is a duty of care, not documentation. This SOP
  governs hazard reporting, incident response, investigation, statutory notification and
  corrective action, and it is the one SOP that overrides every performance target in the
  register — safety escalates immediately and unconditionally.
traces_to: [M59, M46, M47, M23, P02, P09, SP-004, SP-005, SP-008, SP-009, SP-010, SP-026, SP-029, LG-022]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: SP-030_SOP_Health_Safety_and_Incident_Reporting_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M59_Health_Safety_and_Environment.md
    verified: 2026-08-15
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md — ES-06 safety escalates immediately and unconditionally; PE-E1 is L4-direct with no timer
    verified: 2026-08-15
    class: P1
  - source: Bangladesh Labour Act 2006, Chapter XII — duty to give notice of accidents to the prescribed authority; section references and the notifiable-accident definition to be confirmed by Legal Counsel against the consolidated Act
    verified: 2026-08-15
    class: P2
  - source: ISO 9001:2015 clause 7.1.4 environment for the operation of processes; ISO 45001 alignment noted but not certified
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Health, Safety and Incident Reporting

| Item | Value |
|---|---|
| SOP ID | `SP-030` |
| Process owner | HSE Lead, accountable to Operations Director (R05) |
| Roles performing | Every employee · HSE Lead · `R06` Branch Manager · `R09` Workshop Supervisor · `R07` Dispatch Manager · `R32` Quality Manager · `R30` HR Manager |
| Systems used | `P02` · `P09` · `P03` (`UI-031`) · `M59` |
| Frequency / volume | Continuous. Every employee is in scope, every day |
| ISO 9001 clause reference | 7.1.4 environment for operations · 10.2 corrective action (shared with `SP-029`) |

> **This SOP overrides performance targets.** Where any other SOP's timing, throughput or
> customer commitment conflicts with a safety action in this one, this one governs. That
> statement is the point of the document.

---

## 1. Purpose and Outcome

**Purpose.** To prevent harm; where harm occurs, to respond quickly and correctly; to report and
investigate honestly; to notify the authorities where the law requires; and to fix the cause so
it does not happen again.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Hazards are reported before they cause harm | Hazard reports > incidents |
| Every incident was responded to immediately, with escalation unconditioned by any timer | `ES-06`, `SP-005` PE-E1 |
| Notifiable events were notified to the prescribed authority within the statutory period | Notification record |
| Every incident has an investigation and a corrective action | `SP-029` CAPA |
| Near misses are reported without fear of blame | Near-miss reporting rate |
| Nobody was asked to choose between a target and their safety | Culture evidence |

---

## 2. Scope

**Applies to:** every employee, contractor, rider and visitor at every 1000FiX site and at every
customer premises where 1000FiX work is performed — including electrical work, battery and
refrigerant handling, working at height, manual handling, lone working, driving, and workshop
and warehouse operations.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Environmental disposal compliance | `SP-026`; safety aspects of it remain here |
| Information security incidents | `SP-005` TE-E9 / `SP-031` |
| Employee grievance and conduct | HR policy; `SP-005` PE-E9 |
| Product safety recalls of sold goods | `SP-025`, CCO |
| Customer property damage with no injury | `SP-028` |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Hazard | Something with the potential to cause harm |
| Near miss | An event that could have caused harm but did not |
| Incident | An event that caused harm, damage or loss |
| Notifiable event | An incident the law requires be reported to a prescribed authority |
| Lone working | Work performed without a colleague present or within sight |
| Isolation | Making equipment safe before work — electrically, mechanically, thermally |
| PPE | Personal protective equipment appropriate to the task |
| Stop-work authority | The right of any person to stop unsafe work |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Risk assessments per task type | HSE | Written, current, and known to the people doing the work |
| Safe systems of work | HSE with Operations | For electrical work, battery handling, height, and vehicle use |
| PPE issued and serviceable | `M45`, `SP-023` | Issued at onboarding, replaced on wear |
| Safety training completed | `M22` | Mandatory; overdue training restricts affected work types (`BRU-LMS-01`) |
| First-aid provision and trained first-aiders | HSE | Per site, per shift |
| Emergency contacts and procedures | `M47`, `SP-032` | Posted, current, and in both languages |
| Vehicle roadworthiness | `M46`, `SP-032` | Daily check completed |
| Lone-worker check-in arrangement | `M55`, `M02` | Defined intervals and a response if missed |

---

## 5. Procedure

### 5.1 Stop-work authority — the first rule

| # | Rule |
|---|---|
| **SW-01** | **Any person may stop any work they believe to be unsafe, at any time, without needing permission.** |
| **SW-02** | Stopping work is never a disciplinary matter, even where the assessment turns out to have been wrong. |
| **SW-03** | Work resumes only when the person who stopped it, or the HSE Lead, is satisfied. |
| **SW-04** | Every stop-work event is recorded — not to scrutinise the person, but because it identifies a hazard. |

### 5.2 Hazard and near-miss reporting

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | Any employee | Report the hazard or near miss the same shift | `P02` / `P09` / `P03` | Hazard report |
| 2 | R06 / R09 | Make safe immediately where possible; isolate, barrier or withdraw the equipment | — | Immediate action |
| 3 | HSE Lead | Assess, assign an owner and a date, and record it | `M59` | Assessment |
| 4 | HSE Lead | Where the hazard exists elsewhere in the network, act everywhere, not only where it was reported | `M59` | Network action |
| 5 | HSE Lead | Report hazard and near-miss volumes monthly. **A falling near-miss report rate is a warning, not a success** | `M59` | Reporting |

### 5.3 Incident response

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | Anyone present | **Make the area safe; do not create a second casualty.** Isolate power, ventilate, move away from fire | — | — |
| 7 | Anyone present | Give first aid within competence; call emergency services where needed | — | — |
| 8 | Anyone present | **Escalate immediately — L4-direct, no timer** (`SP-005` PE-E1, `ES-06`) | `P02` / phone | Escalation |
| 9 | R06 / HSE Lead | Preserve the scene and the equipment where safe to do so; photograph before anything is moved | `P03` capture | Scene evidence |
| 10 | HSE Lead | Account for everyone; notify next of kin through HR, never informally or by message | `R30` | Notification record |
| 11 | HSE Lead | Record the incident with the facts known, and update as more emerge. **Do not delay the record until the picture is complete** | `M59` | Incident record |

### 5.4 Statutory notification

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 12 | HSE Lead + Legal Counsel | Determine whether the event is notifiable | Bangladesh Labour Act 2006, Chapter XII — **definition and period to be confirmed, O-01** |
| 13 | HSE Lead with Legal Counsel | Notify the prescribed authority within the statutory period. **Only these two roles notify externally** (`SP-005` §4.8 L5) | Legal Counsel |
| 14 | CFO | Notify the insurer per the policy terms | Insurance policy |
| 15 | Legal Counsel | Handle any authority visit, request or interview. **No branch or manager responds to an inspector directly** | `SP-005` §4.8 |

### 5.5 Investigation and corrective action

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 16 | HSE Lead | Investigate: sequence of events, conditions, decisions, and why the controls did not prevent it | `M59` | Investigation |
| 17 | HSE Lead | Establish the root cause. **"Careless" is not a root cause**; ask why the system permitted the outcome | `M59` | Root cause |
| 18 | HSE Lead | Raise a nonconformity and a CAPA through `SP-029`; safety CAPAs are not a separate system | `M23` | CAPA |
| 19 | HSE Lead | Where the cause exists elsewhere, act across the network before the CAPA closes | `M59` | Network action |
| 20 | R32 | Verify effectiveness independently of the person who acted (`SOD-19`) | `M23` | Verification |
| 21 | HSE Lead | Share the learning — anonymised — with everyone doing similar work | `TR-*`, `NT-*` | Safety alert |
| 22 | R30 | Manage any injury absence, return to work and, where applicable, statutory compensation | HR policy, Legal | Case record |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| — | Any doubt about safety at any time | **Stop.** `SW-01`. The doubt is sufficient reason | Any person |
| 6 | Electrical incident with a person in contact | Isolate the supply before touching anyone. Do not become the second casualty | Anyone present |
| 6 | Lithium battery fire or thermal runaway | Do not use water on a battery fire unless trained and equipped; evacuate; call emergency services. Battery fires reignite | Anyone present |
| 6 | Refrigerant release | Ventilate and evacuate; do not enter a confined space | Anyone present |
| 8 | The incident is at a customer's premises | Escalate identically. The customer is informed by R05 or HSE, not by the technician improvising | HSE + R05 |
| 9 | Preserving the scene conflicts with restoring safety | Safety first. Photograph what you can, and record what was moved and why | HSE Lead |
| 11 | The employee involved fears blame | Reassure and record. **An incident report is not a disciplinary document.** Concealment kills people | HSE Lead, R30 |
| 12 | It is unclear whether the event is notifiable | **Treat it as notifiable and take legal advice immediately.** Late notification is worse than unnecessary notification | HSE Lead + Legal |
| 15 | An inspector or authority attends a site | The site cooperates and contacts Legal Counsel at once; no statements are made beyond the facts of access | R06 → Legal |
| 17 | The investigation points to production pressure as a contributing cause | Record it. Suppressing that finding guarantees recurrence | HSE Lead → R05 |
| 19 | The same hazard exists at other sites | Act everywhere immediately; do not wait for the CAPA cycle | HSE Lead |
| 22 | An injured employee is pressed to return early | Refuse. Medical fitness governs, not roster pressure | R30 + HSE |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Stop unsafe work | Any | **Any person; no approval required** (`SW-01`) | — |
| Resume stopped work | Any | The person who stopped it, or the HSE Lead (`SW-03`) | R05 |
| Statutory notification | Any | HSE Lead **with** Legal Counsel only (`SP-005` L5) | CFO |
| Respond to an authority or inspector | Any | Legal Counsel only | CFO |
| Withdraw equipment or a vehicle from service on safety grounds | Any | HSE Lead, or any supervisor pending HSE review | R05 |
| Close a site or suspend an activity on safety grounds | Any | HSE Lead with R05 | CEO |
| Spend on immediate risk removal | ≤ BDT 50,000 | R05 Operations Director, without prior procurement process | CFO retrospectively |
| Spend on immediate risk removal | > BDT 50,000 | CFO | CEO |
| Close a safety CAPA without verified effectiveness | **None — class H, no override** (`BRU-QMS-03`) | — | — |

> Must reconcile exactly with `SP-004`. The emergency-spend rows are an intentional exception to
> the `SP-017` procurement path and are recorded in `SP-004` §4.6 as acting-first authority.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Fatality or serious injury | Emergency services; secure the scene; **L4-direct: CEO, R05, HSE, Legal**; do not disturb equipment | As stated | Incident record + statutory notification |
| Road traffic accident involving a company vehicle | Safety first; police as required; secure any customer device on board | HSE, R05, `M46`, insurer | Incident + fleet record |
| Fire at a site | Evacuate; roll call; emergency services; do not re-enter | HSE, R05, CEO | Incident record |
| Battery thermal event | Evacuate the immediate area; battery fires reignite — do not assume it is out | HSE, R09 | Incident + batch review |
| Injury to a customer or member of the public | First aid; emergency services; **do not admit liability**; route to Legal and `SP-028` | HSE, Legal, CCO | Incident + complaint |
| Employee refuses unsafe work | Support them. Investigate the hazard, not the refusal | HSE, R06 | Stop-work record |
| Near-miss reporting falls | Investigate the culture, not the numbers. Falling reports usually mean falling trust | HSE → R05 | Culture review |
| Incident concealed and discovered later | Treat the concealment as a system failure first; ask why reporting felt unsafe | HSE, R30, R05 | Restricted record |
| Lone worker unreachable | Welfare escalation immediately; do not wait for the end of a shift | R07 → R06 → HSE | Lone-worker log |
| Safety training overdue for staff performing hazardous work | Restrict the work type until complete (`BRU-LMS-01`) | R32, R30 | Training compliance |

---

## 9. Manual Fallback

Safety does not depend on any system. Cross-reference `OP-014`.

| Step | Manual action |
|---|---|
| 1 | Every site holds a **paper accident book and hazard report pad**, and every vehicle carries a paper incident form |
| 2 | Emergency contact numbers are posted physically at every site, in Bengali and English, and carried by every field worker |
| 3 | **Escalation is by telephone. It never depends on an application being available** |
| 4 | Statutory notification is made on the prescribed form by whatever route the instrument allows |
| 5 | **Back-enter every hazard, near miss and incident within 24 hours**, preserving the original dates and times |
| 6 | HSE Lead reconciles the paper books against the system monthly and signs |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Stop-work authority held by every person | Preventive | Continuous | Stop-work records |
| Safety training mandatory and gating | Preventive (`BRU-LMS-01`) | Continuous | Training compliance |
| Risk assessments current per task type | Preventive | Annual and on change | Assessment register |
| PPE issued, inspected and replaced | Preventive | Per issue; inspected monthly | PPE register |
| Daily vehicle checks | Preventive (`SP-032`) | Daily | Check records |
| Lone-worker check-in with a defined response | Preventive | Per shift | Check-in log |
| Restricted-item carriage certification | Preventive (`BRU-LOG-05`) | Per movement | Certification check |
| Battery storage and handling rules | Preventive (`BRU-ESG-04`) | Continuous | Storage compliance |
| Emergency drills | Detective | Per site, at least annually | Drill record |
| Hazard and near-miss reporting rate | Detective | Monthly | HSE report |
| Incident investigation completion and CAPA effectiveness | Detective | Monthly | `SP-029` |
| Safety audit within the internal audit programme | Detective | Per plan | `SP-029` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Investigate an incident | Be the manager whose production pressure is a candidate cause | Assignment control | Investigation led by HSE, independent of the line |
| Perform a safety corrective action | Verify its effectiveness (`SOD-19`) | Hard block | Verification by R32 or HSE |
| Audit safety in an area | Be responsible for that area (`SOD-20`) | Hard block | Cross-site or external auditor |
| Withdraw equipment on safety grounds | Approve its return to service | Hard block | Return authorised by HSE Lead, not by the supervisor who wants it back |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| Lost-time injuries | Injuries causing absence, per period and per hours worked | untracked | **Zero** |
| Notifiable events | Count per period | untracked | Zero |
| Hazard and near-miss reports | Reports per employee per period | untracked | **Rising** — a rising rate is a healthy signal |
| Safety CAPA closed on time | Within `KPI-066` | unmeasured | 90%; stretch 95% |
| Safety training compliance | Within `KPI-064` | unmeasured | 95%; stretch 98% |
| Stop-work events | Count and hazard yield | untracked | Recorded, not minimised |

> Note the direction of the third and sixth rows. **Rising hazard reports and stop-work events
> are targets to increase, not to reduce.** A safety scorecard that rewards low reporting
> produces low reporting, not high safety.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `LG-022` Health and Safety Policy | The published policy this SOP operates |
| `UI-031` Workspace — Quality Console Copy · `UI-012` `P02` Technician App Copy Pack | Reporting surfaces |
| [`SP-032_Operational_Checklist_Library.md`](SP-032_Operational_Checklist_Library.md) | Daily safety, vehicle and equipment checks |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Safety CAPAs run through the same process |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](SP-008_SOP_On_Site_Field_Service_Visit.md) | Field safety survey and lone working |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](SP-010_SOP_Workshop_and_Depot_Repair.md) | Bench safety and thermal events |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](SP-026_SOP_EWaste_Collection_and_Disposal.md) | Hazardous storage and battery containment |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Restricted-item carriage and road safety |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | PE-E1 and the L5 statutory notification path |
| `TR-002` Role-Based Curriculum Map | **No HSE course pack exists — a safety-training gap**, raised in `AUDIT-006` |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Operations Director with Legal Counsel (pending) |

**Open items**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **Confirm the notifiable-accident definition, the prescribed authority and the notification period** under the Bangladesh Labour Act 2006 and any subordinate rules. Cited here at class **P2**; `SP-005` O-01 raises the same item and the two must be answered together | Legal Counsel | **Before `Approved`** |
| O-02 | Confirm statutory employment-injury compensation obligations and the insurance position | Legal Counsel + CFO | Before W5 |
| O-03 | Complete task-type risk assessments for electrical, battery, refrigerant, height, manual handling, lone working and driving | HSE Lead | Before W2 field rollout — **earlier than this SOP's own W5 wave** |
| O-04 | Decide whether ISO 45001 certification is pursued | CEO | Before W6 |

> **O-03 is a wave conflict worth stating plainly.** This SOP is scheduled for W5, but field
> technicians go live in W2 (`SP-008`). The risk assessments and the safety training that
> `SP-008` depends on cannot wait for W5. Raised as a finding in `AUDIT-006`.

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] Stop-work authority stated first, unconditioned, and protected from disciplinary consequence
- [x] Escalation stated as immediate and unconditional, overriding performance targets
- [x] "Treat it as notifiable and take legal advice" stated as the default under uncertainty
- [x] Reporting-rate KPIs stated as targets to **increase**, with the reason
- [x] Manual fallback makes escalation independent of any system
- [x] §7 reconciles with `SP-004`, including the emergency-spend exception
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 statutory notification requirements verified — outstanding; blocks `Approved`**
- [ ] **O-03 risk assessments completed before W2 field rollout — outstanding; wave conflict raised**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
