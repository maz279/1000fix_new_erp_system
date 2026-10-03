---
id: SP-023
title: SOP — Recruitment, Onboarding and Exit
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HR
author: Business Process Lead with HR Operations
reviewers: [HR Manager, CTO, Operations Director, Quality Manager, Legal Counsel, Internal Audit, Localisation Lead]
approver: HR Manager with Chief Technology Officer for the access elements
content_class: C
purpose: >
  Technician attrition and rapid network growth make onboarding a continuous, high-volume
  process, and every joiner and leaver is also an access event. This SOP covers requisition,
  sourcing, assessment, offer, joining, provisioning, induction, probation and exit — including
  the one-hour access revocation on a leaver event, which is a security control with a
  zero-tolerance KPI, not an administrative courtesy.
traces_to: [M58, M21, M22, M29, M30, P03, DT-042, MD-008, MD-009, MD-010, MD-011, SP-004, SP-005, SP-006, SP-021, SP-022, SP-031]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: SP-023_SOP_Recruitment_and_Onboarding_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M21_Core_HR_and_Employee_Lifecycle.md — SOD-25 record creator cannot approve salary structure; SOD-26 retrospective effective-date change
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §11 BRU-SEC-06 leaver access revoked within one hour; §12.4 AUT-047, AUT-048
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-090 orphaned accounts after leaver — zero beyond 24h; KPI-062 certifications current; KPI-064 mandatory training completion
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §7 access request — standard role line manager; privileged role line manager + IT Administrator + CTO
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 7.2 competence — determine necessary competence, ensure it, and retain documented information as evidence
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — Recruitment, Onboarding and Exit

| Item | Value |
|---|---|
| SOP ID | `SP-023` |
| Process owner | HR Manager (R30), with CTO for access provisioning and revocation |
| Roles performing | `R30` HR Manager · `R31` HR Officer · hiring line managers · `R33` IT / System Administrator · `R32` Quality Manager (competence) |
| Systems used | `P03` HR console (`UI-030`) · `M58` · `M21` · `M22` · `M29` |
| Frequency / volume | Continuous. 500+ employees with high technician turnover and network growth |
| ISO 9001 clause reference | **7.2** competence · 7.3 awareness · 5.3 assigned authorities · 7.1.2 people |

---

## 1. Purpose and Outcome

**Purpose.** To fill an approved vacancy with a competent person, give them identity, access,
tools and training on day one, confirm their competence before it is relied on, and — when they
leave — remove everything they held, quickly and completely.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| The vacancy was approved before sourcing began | Requisition approval |
| The joiner had identity, role-based access, tools and training assigned on day one | `AUT-047` |
| Role came from the **position**, not from copying another user | `MD-008`, `AA-01` |
| Mandatory training completed within the deadline | `BRU-LMS-01`, `KPI-064` |
| Certification is current before brand warranty work is assigned | `BRU-HRM-01`, `KPI-062` |
| Leaver access revoked within one hour | `BRU-SEC-06`, `AUT-048`, `KPI-090` |
| Delegated authority reassigned before the leaver's last day | `SP-004` DL-06 |

---

## 2. Scope

**Applies to:** the employment lifecycle for all employees — requisition, sourcing, assessment,
offer, joining, provisioning, induction, probation, internal transfer and exit. Contractor and
marketplace-seller onboarding are related but separate.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Payroll processing | `SP-021` |
| Attendance and roster | `SP-022` |
| Marketplace seller onboarding | `SP-024` |
| Vendor onboarding | `SP-017` |
| Training content design and course delivery | `TR-*` category; this SOP assigns and tracks it |
| Disciplinary and grievance procedure | HR policy; escalated per `SP-005` PE-E9 |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Requisition | The approved authority to recruit against a position |
| Position | The organisational slot in `MD-008` carrying role, reporting line, cost centre and authority limit |
| Provisioning | Creation of identity and grant of access derived from the position |
| Induction | The structured first-days programme |
| Mandatory training | Training that must be completed within a deadline; overdue restricts work types (`BRU-LMS-01`) |
| Probation | The period during which competence and fit are confirmed |
| Leaver event | The recorded fact of an employee leaving, triggering `AUT-048` |
| Clearance | Confirmation that assets, access, cash and custody have been returned or transferred |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Position exists and is approved vacant | `MD-008` | Recruiting to a position that does not exist creates an unmapped role |
| Role definition and access profile | `MD-009`, `05-04` | The role must be registered; **an unregistered role is not provisioned** |
| Competency requirement | `MD-010` | The skills and level the position needs |
| Certification requirement | `MD-011` | Where the position performs brand warranty work |
| Budget and headcount approval | `M54` | Approved per `SP-004` A-62 |
| Onboarding checklist and induction content | `TR-*` | Exists before the joiner does |
| Asset availability | `M45`, `M46` | Tools, device, vehicle and PPE ready for day one |

---

## 5. Procedure

### 5.1 Requisition and sourcing

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | Line manager | Raise the requisition against a position, with justification and budget reference | `P03` · `M58` | Requisition |
| 2 | R30 + approver per band | Approve (`SP-004` A-62). Additional headcount requires CFO | `P03` | Approval |
| 3 | R31 | Source: internal first where the policy requires, then external channels | `M58` | Candidate pipeline |
| 4 | R31 + line manager | Assess against the position's competency profile, with structured, recorded scoring | `M58` | Assessment record |
| 5 | R31 | Verify identity, qualifications, prior employment and any required certification **before** the offer | `M58` | Verification record |

### 5.2 Offer and joining

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 6 | R30 | Issue the offer from `DT-042`; the salary structure is approved by someone other than the record creator (`SOD-25`) | `DT-042` | Offer issued |
| 7 | Candidate | Accept; provide documents, bank details and statutory information | `P03` | Acceptance |
| 8 | R31 | Create the employee record with the correct **effective date**; retrospective dating requires separate approval (`SOD-26`) | `M21` | Employee record |
| 9 | System | On the joining date, create identity, assign the role **from the position profile**, grant portal access, assign onboarding and mandatory training (`AUT-047`) | `M29`, `M22` | Provisioning record |
| 10 | R33 | Issue devices and credentials; enforce MFA where the role requires it (`BRU-SEC-01`) | `M45`, `M29` | Asset issue record |
| 11 | Line manager | Issue tools, PPE and vehicle where applicable; record the issue | `M45`, `M46` | Asset record |

### 5.3 Induction and probation

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 12 | R31 | Deliver induction: company, safety, quality, data protection, the SOPs the role performs | `TR-*` | Induction record |
| 13 | Line manager | Assign a buddy and a 30/60/90-day plan | `P03` | Plan |
| 14 | R32 | Confirm mandatory training completion within the deadline (`BRU-LMS-01`) | `M22` | Completion record |
| 15 | R32 | Where the role performs brand warranty work, confirm certification **before** the first such assignment (`BRU-SRM-09`) | `MD-011` | Certification record |
| 16 | Line manager | Conduct probation reviews on schedule; confirm, extend or end with a recorded decision | `P03` · `DT-042` | Probation decision |

### 5.4 In-life changes

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 17 | Line manager | Transfer, promotion or role change is a **position change**, and access is re-derived from the new position | `MD-008`, `AA-01` |
| 18 | R33 | **Remove the access the old position carried.** Access accumulation across a career is the most common cause of SoD violations | `SOD-09`, `AUT-052` |
| 19 | R30 | Issue the letter from `DT-042`; update payroll effective-dated | `SP-021` |
| 20 | R32 | Reassess competence and certification for the new position | `M22` |

### 5.5 Exit

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 21 | Line manager / employee | Record the leaver event with the last working day | `M21` | Leaver record |
| 22 | R30 | Plan the handover: work in progress, customer relationships, delegated authority | `P03` | Handover plan |
| 23 | R30 | **Reassign delegated authority before the last day** (`SP-004` DL-06) | `MD-008` | Delegation reassignment |
| 24 | Line manager | Clearance: assets, tools, vehicle, uniform, keys, van stock, cash float, customer devices in custody | `M45`, `M15` | Clearance record |
| 25 | System | **Revoke all access within one hour of the leaver event**; deregister devices; trigger clearance (`AUT-048`, `BRU-SEC-06`) | `M29` | Revocation log |
| 26 | R30 | Final settlement through payroll, including leave encashment and statutory dues | `SP-021` | Final settlement |
| 27 | R30 | Issue the exit and clearance letters | `DT-042` | Letters issued |
| 28 | R31 | Conduct the exit interview; feed themes to retention analysis | `M58` | Exit record |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | No position exists for the role being recruited | Create and register the position first (`MD-008`). **Do not recruit to an unregistered role** — audit `00-07` H2-07 records R39–R50 already used but unregistered | R30 + Enterprise Architecture |
| 5 | Verification cannot be completed | Do not issue the offer. A conditional offer with unverified credentials becomes an employment problem later | R30 |
| 5 | A required certification is absent but obtainable | Offer with a documented condition and a deadline; restrict the work type until it is held (`BRU-HRM-01`) | R30 + R32 |
| 6 | Salary structure approved by the person who created the record | **Blocked** (`SOD-25`) | — |
| 8 | Joining date has passed and the record is being created retrospectively | Requires separate approval (`SOD-26`, `SP-004` A-60) | R30 |
| 9 | The position's access profile has not been defined | Provisioning waits. **Never copy another user's access** — it propagates accumulated and inappropriate rights | R33 + CTO |
| 9 | Privileged access is required | Line manager + R33 + CTO (`SP-004` A-86) | CTO |
| 14 | Mandatory training overdue | Affected work types are restricted automatically (`BRU-LMS-01`). Escalate at 14 days (`SP-005` PE-E7) | Line manager → R30 |
| 16 | Probation outcome is negative | Follow the documented process with legal advice on notice and settlement | R30 + Legal |
| 17 | Transfer without removing prior access | The transfer is not complete. Re-derive access from the new position only | R33 |
| 21 | Leaver is a security or fraud concern | **Revoke access immediately, before the last day**, on CFO or CTO authority | CFO or CTO |
| 24 | Assets, cash or a customer device cannot be accounted for | Do not issue clearance. Escalate; a missing customer device is a custody incident (`SP-009`) | R30 → R05 |
| 25 | Access not revoked within one hour | **L4-direct escalation** (`SP-005` PE-E8); `KPI-090` targets zero orphaned accounts beyond 24 hours | CTO + R30 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Recruitment requisition — replacement | Any | Line manager + R30 (`SP-004` A-62) | R05 |
| Recruitment requisition — additional headcount | Any | Line manager + R30 + CFO | CEO |
| Salary structure for a new record | Any | Not the record creator (`SOD-25`, `SP-004` A-61) | CFO |
| Retrospective effective-date change | Any | R30, not the processor (`SOD-26`, `SP-004` A-60) | CFO |
| Access request — standard role | Any | Line manager (`SP-004` A-85) | R30 |
| Access request — privileged role | Any | Line manager + R33 + CTO (`SP-004` A-86) | CTO |
| Immediate revocation ahead of the last day | Any | CFO or CTO | — |
| Offer above the position's approved band | Any | R30 + CFO | CEO |
| Probation extension or termination | Any | R30 with Legal Counsel | CFO |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| Leaver access not revoked within one hour | **L4-direct: CTO + R30** (`SP-005` PE-E8); revoke manually immediately | As stated | Access incident |
| Joiner arrives with no provisioning | Escalate; a joiner without access is unproductive and often given someone else's login — which destroys attribution | R33, R30 | Provisioning exception |
| Shared or borrowed credentials discovered | Security incident; every control that depends on attribution is void for that period | CTO, R30 | Security incident |
| Mandatory training overdue | Work types restricted automatically; escalate at 14 days | Line manager → R30 (`SP-005` PE-E7) | Training compliance report |
| Certification lapsed | Technician removed from that brand's pool (`AUT-042`); claims performed after lapse are unrecoverable (`SP-014`) | R32, R07 (`SP-005` PE-E6) | Certification register |
| Unregistered role requested | Register in `05-04` and `MD-009` first (`RG-01`) | Enterprise Architecture, CTO | Role register |
| Access accumulated across transfers | Found at access certification (`AUT-052`); remove and record | R33, CTO | Certification record |
| Grievance or conduct allegation | **L4-direct: R30 only**, restricted distribution (`SP-005` PE-E9) | R30 | Restricted record |
| Clearance incomplete at the last day | Withhold final settlement only to the extent lawful; take legal advice | R30 + Legal | Clearance record |
| High attrition in one role or site | Analysis, not replacement recruiting alone | R30 → R05 | Retention analysis |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | Requisitions, offers and letters are produced from the **controlled `DT-042` template pack**; approvals recorded by signature on the printed requisition |
| 2 | Provisioning is requested on the **manual access request form**, signed by the line manager and, for privileged access, by CTO. **The approval levels do not relax during an outage** |
| 3 | Asset issue is recorded on the **manual asset issue register**, signed by both parties |
| 4 | **Leaver revocation is performed manually and immediately** — the one-hour obligation is independent of system availability. R33 records each system revoked on the leaver checklist |
| 5 | **Back-enter every record within 48 hours**, preserving dates |
| 6 | R30 reconciles manual records against the system and signs; CTO reviews the manual revocation checklists |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Role assigned from the position profile, never copied | Preventive (`AA-01`) | Per joiner | Provisioning record |
| Unregistered roles cannot be provisioned | Preventive (`RG-01`) | Per request | Hard block |
| Record creator cannot approve the salary structure | Preventive (`SOD-25`) | Per record | Hard block |
| Retrospective change processed and approved by different people | Preventive (`SOD-26`) | Per change | Hard block |
| Administer users + approve own access | Preventive (`SOD-09`) | Continuous | Hard block |
| Leaver access revoked within one hour | Preventive (`BRU-SEC-06`, `AUT-048`) | Per leaver | Revocation log |
| Delegated authority reassigned before the last day | Preventive (`DL-06`) | Per leaver | Delegation record |
| Mandatory training restricts work types when overdue | Preventive (`BRU-LMS-01`) | Continuous | Restriction log |
| Certification gating for brand warranty work | Preventive (`BRU-HRM-01`, `BRU-SRM-09`) | Per assignment | Hard block |
| Access certification cycle | Detective (`AUT-052`) | Per cycle | Certification record |
| Orphaned account report | Detective | Weekly | `KPI-090` |
| Training completion and certification currency | Detective | Monthly | `KPI-062`, `KPI-064` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Create an employee record | Approve that employee's salary structure (`SOD-25`) | Hard block | — |
| Process a retrospective effective-date change | Approve it (`SOD-26`) | Hard block | — |
| Administer users | Approve access requests for oneself (`SOD-09`) | Hard block | — |
| Recruit into a position | Approve the requisition for it | Hard block | Line manager raises; R30 and, for headcount, CFO approve |
| Issue an asset | Sign for its return at clearance | Detective | R30 samples clearance records |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-090` | Orphaned accounts after leaver | no baseline stated in `06-02` | **Zero beyond 24 h** |
| `KPI-062` | Certifications current, no lapses | unknown | 100% |
| `KPI-064` | Mandatory training completion on time | unmeasured | 95%; stretch 98% |
| `KPI-065` | Employee self-service adoption | 0% | 75%; stretch 85% |
| Time to productive | Joining date to first unsupervised work | untracked | To be set from `SP-002` |
| Day-one provisioning completeness | Joiners fully provisioned on day one | untracked | 100% |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `DT-042` HR Letter Template Set | Offer, appointment, transfer, probation, exit and clearance letters |
| `UI-030` Workspace — HR Console Copy | The screens used |
| [`SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) | Joiners, leavers and final settlement |
| [`SP-022_SOP_Time_Attendance_and_Roster.md`](SP-022_SOP_Time_Attendance_and_Roster.md) | Roster impact of joiners and leavers |
| [`SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Provisioning and revocation execution |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | Delegation reassignment on exit |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-008_Organisation_Structure_and_Position_Master.md) | Positions carry role and authority |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-009_Role_and_Job_Title_Master.md) | Registered roles; closes `00-07` H2-07 |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Certification gating |
| `TR-015` Course Pack — HR and Payroll · `TR-011` Course Pack — Branch Manager | Train this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | HR Manager with CTO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] "Never copy another user's access" stated as a decision point with its reason
- [x] Leaver revocation stated as independent of system availability in the fallback
- [x] Delegated authority reassignment placed before the last day
- [x] Unregistered-role prohibition cites `RG-01` and audit `00-07` H2-07
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] `MD-009` role register confirmed complete to `R50` — **outstanding; carried from `00-07` H2-07 and module-set A3-17**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Manager and CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
