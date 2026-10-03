---
id: SP-031
title: SOP — IT Service Desk and Change Management
project: 1000FiX ERP System v2.0
content_type: SOP
template: TPL_SOP.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Internal IT
author: Business Process Lead with Platform Engineering
reviewers: [CTO, Operations Director, CFO, Quality Manager, Internal Audit, Data Protection Officer, Localisation Lead]
approver: Chief Technology Officer
content_class: C
purpose: >
  With 800+ internal users on a 67-module system, internal IT process failure stops the business.
  This SOP governs internal ticket handling, priority, request fulfilment, change request, CAB,
  release, rollback and emergency change. Configuration changes in production must be traceable
  to an approved change record; without a change process, the ERP becomes an environment nobody
  can explain and no auditor can accept.
traces_to: [M66, M30, M29, M28, P03, OP-008, SP-004, SP-005, SP-006, SP-011, SP-023, SP-029, SP-030]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: SP-031_SOP_IT_Service_Desk_and_Change_Management_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M66_Internal_IT_Service_Management.md
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §11 BRU-ADM-01, BRU-ADM-02, BRU-SEC-01, BRU-SEC-02, BRU-SEC-06, BRU-SEC-08; §12.5 AUT-053, AUT-054
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 KPI-085 uptime 99.9%, KPI-088 integration failures undetected > 5 min zero, KPI-090 orphaned accounts, KPI-091 backup restore tests
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-064 segregation of duties enforced by the permission engine
    verified: 2026-08-15
    class: P1
  - source: ISO 9001:2015 clause 7.1.3 infrastructure, and clause 8.5.6 control of changes
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# SOP — IT Service Desk and Change Management

| Item | Value |
|---|---|
| SOP ID | `SP-031` |
| Process owner | Chief Technology Officer |
| Roles performing | `R33` IT / System Administrator · service desk analysts · change owners · CAB members · CTO |
| Systems used | `P03` System console (`UI-036`) · `M66` · `M30` · `M29` |
| Frequency / volume | Continuous, for 800+ internal users across 51+ sites |
| ISO 9001 clause reference | 7.1.3 infrastructure · **8.5.6** control of changes · 7.5.3 documented information |

---

## 1. Purpose and Outcome

**Purpose.** To restore service quickly when something breaks, fulfil access and equipment
requests through a controlled path, and change the production environment only through an
approved, tested, reversible change record.

**Outcome — you know it succeeded when:**

| Test | Evidence |
|---|---|
| Every production change traces to an approved change record | `BRU-ADM-02` |
| No change was executed and approved by the same person | `SOD-59` pattern; CAB |
| Every access grant followed the `SP-004` path, not a helpful shortcut | `SP-004` A-85/A-86 |
| Leaver access was revoked within one hour | `BRU-SEC-06`, `KPI-090` |
| Every change had a tested rollback, or an explicit statement that it had none | Change record |
| Emergency changes were reviewed retrospectively within 2 business days | `SP-004` A-91 |
| Uptime meets 99.9% in business hours | `KPI-085` |

---

## 2. Scope

**Applies to:** internal incident and request handling for employees; change to the ERP, its
configuration, its integrations and the supporting infrastructure; release management; rollback;
emergency change; and problem management.

**Does not apply to:**

| Situation | Covered by |
|---|---|
| Customer-facing service incidents | `SP-028`; a platform incident affecting customers escalates via `SP-005` TE-E1 |
| Changes in a **customer's** environment | `SP-011` |
| Technical incident runbooks and severity classification | `OP-008` |
| Master data change approval | `SP-004` A-89, `MD-001` |
| Joiner and leaver decisions | `SP-023`; this SOP executes the provisioning and revocation |
| Security incident response | `SP-005` TE-E9…TE-E12 and the security runbooks |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| Incident | An unplanned interruption or reduction in quality of a service |
| Request | A standard, pre-approved service — access, equipment, a report, a password reset |
| Problem | The underlying cause of one or more incidents |
| Change | Any addition, modification or removal affecting a production service |
| Standard change | Pre-approved, low-risk, repeatable, with a documented procedure |
| Normal change | Assessed and approved by the CAB before implementation |
| Emergency change | A change needed to restore or protect service, approved outside the normal cycle |
| CAB | Change Advisory Board — the forum that assesses and approves normal changes |
| Rollback | The tested means of reversing a change |

---

## 4. Inputs and Preconditions

| Input | Source | Must be true before starting |
|---|---|---|
| Service catalogue | `M66` | What is offered, to whom, with what target |
| Priority matrix | `OP-008` | Impact × urgency, agreed with the business |
| Configuration record | `M30` | What is in production, and its dependencies |
| Environments | `M28` | Dev, SIT, UAT, Prod separated; production data masked in non-production (`BRU-SEC-08`) |
| Access model | `05-04`, `M29` | Roles derived from positions, SoD enforced (`NFR-064`) |
| CAB membership and schedule | CTO | Named, quorate, meeting on a published cadence |
| Backup and restore capability | `OP-*` | Restore tests passing (`KPI-091`) |

---

## 5. Procedure

### 5.1 Incident handling

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 1 | User | Raise the incident through the service desk. **A message to an engineer directly is not a ticket** | `P03` | Ticket |
| 2 | Analyst | Classify by impact and urgency; assign the priority from the matrix | `OP-008` | Priority |
| 3 | Analyst | Acknowledge within the target; tell the user what happens next | `NT-*` | Acknowledgement |
| 4 | Analyst | Diagnose; apply a known fix from the runbook where one exists | `OP-*` | Diagnosis |
| 5 | Analyst | Where the fix requires a production change, raise a change (§5.3) — **do not change production from an incident ticket** | `P03` | Change raised |
| 6 | Analyst | Restore service; confirm with the user before closing | `P03` | Restoration confirmed |
| 7 | Analyst | Where the incident recurs or its cause is unknown, raise a problem record | `M66` | Problem record |
| 8 | R33 | Escalate per `SP-005` TE-E1…TE-E6 by severity, including the 24×7 P1 path | `SP-005` | Escalation |

### 5.2 Request fulfilment

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 9 | User | Raise the request | `P03` | Request |
| 10 | Line manager | Approve per `SP-004` A-85; privileged access additionally requires R33 and CTO (A-86) | `P03` | Approval |
| 11 | R33 | Fulfil. **Access is derived from the position profile, never copied from another user** (`SP-023` §6) | `M29` | Fulfilment |
| 12 | System | Check SoD at assignment; block incompatible combinations (`BRU-SEC-07`, `NFR-064`) | `M29` | SoD check |
| 13 | R33 | Record the grant; it enters the next access certification cycle (`AUT-052`) | `M29` | Access record |

### 5.3 Normal change

| Step | Who | Action | System / screen | Evidence produced |
|---:|---|---|---|---|
| 14 | Change owner | Raise the change: what, why, risk, impact, affected services, test evidence, rollback plan, implementation window | `P03` | Change record |
| 15 | Change owner | Test in a non-production environment. **Production data used in non-production must be masked** (`BRU-SEC-08`) | `M28` | Test evidence |
| 16 | CAB | Assess and approve or reject. **The change owner does not approve their own change** | `P03` | CAB decision |
| 17 | Change owner | Notify affected business owners before the window, not during it | `NT-*` | Notification |
| 18 | Change owner | Implement in the window; record the actual steps taken, not the planned ones | `P03` | Implementation record |
| 19 | Change owner | Post-implementation check against defined success criteria | `P03` | Verification |
| 20 | Change owner | Where the check fails, **roll back**. Record it as a failed change, not as a completed one | `P03` | Rollback record |
| 21 | R33 | Update the configuration record | `M30` | CMDB update |

### 5.4 Standard and emergency change

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 22 | CAB | Pre-approve standard changes as a catalogue, reviewed periodically | CTO |
| 23 | Change owner | Execute a standard change against its documented procedure; deviation makes it a normal change | `P03` |
| 24 | CTO or delegate | Approve an emergency change to restore or protect service (`SP-004` A-91) | `SP-004` |
| 25 | Change owner | Implement with the same recording discipline; testing may be compressed but is not skipped silently | `P03` |
| 26 | CAB | **Review every emergency change retrospectively within 2 business days** | `SP-004` A-91 |
| 27 | CTO | Report the emergency-change rate monthly. A high rate means the normal path is too slow, not that emergencies are frequent | `M66` |

### 5.5 Problem management

| Step | Who | Action | Governed by |
|---:|---|---|---|
| 28 | R33 | Investigate recurring incidents to root cause | `SP-029` method |
| 29 | R33 | Raise a CAPA where the cause is process rather than technical | `SP-029` |
| 30 | R33 | Maintain and publish known errors and workarounds so the service desk resolves at first contact | `KB-*`, `OP-*` |

---

## 6. Decision Points

| At step | Condition | Then | Authority |
|---|---|---|---|
| 1 | A user asks an engineer directly | Log it, then help. Untracked work is invisible capacity and unmeasurable service | Analyst |
| 5 | A production change would fix the incident quickly | Raise the change. **Speed is not an exemption from the change record** (`BRU-ADM-02`); use the emergency path where genuinely warranted | R33 → CTO |
| 10 | The requester's manager is unavailable and the user is blocked | Escalate per `SP-004` DL-09 — authority rises, it never lapses. **Do not grant access on urgency** | R33 → CTO |
| 12 | SoD check blocks the assignment | The assignment is refused. Exception requires CFO or CTO, time-boxed (`SP-004` A-87, `SOD-22`) | CFO or CTO |
| 15 | Testing is not possible in a non-production environment | State it explicitly in the change record and raise the risk to the CAB. Do not imply testing occurred | Change owner |
| 16 | The CAB is not quorate | The change waits, unless it qualifies as an emergency. A non-quorate CAB does not approve | CTO |
| 16 | The change owner is the only person competent to assess it | Bring in a second reviewer, internal or vendor. **Self-approval is not permitted** | CTO |
| 19 | The post-implementation check is ambiguous | Treat as a failure and roll back. Ambiguity after a change is usually a partial failure | Change owner |
| 20 | Rollback is not possible | This must have been stated at step 14. An unrecoverable change requires explicit CAB acceptance **before** implementation | CAB |
| 24 | An emergency change is claimed but service is not at risk | Route it through the normal path. Emergency is a service condition, not a schedule preference | CTO |
| — | A production change is discovered with no change record | Investigate as a control failure, restore the recorded state where necessary | CTO, Internal Audit |
| — | A leaver's access is still active | **L4-direct escalation** (`SP-005` PE-E8); revoke immediately | CTO + R30 |

---

## 7. Approvals and Authority Limits

| Decision | Limit | Approver | Escalation on absence |
|---|---|---|---|
| Access request — standard role | Any | Line manager (`SP-004` A-85) | Skip-level manager per DL-09 |
| Access request — privileged role | Any | Line manager + R33 + CTO (`SP-004` A-86) | CTO only |
| Normal change | Any | CAB; **never the change owner alone** (`SP-004` A-90) | CTO |
| Emergency change | Any | CTO or delegate, retrospective CAB within 2 business days (`SP-004` A-91) | CTO only |
| Standard change | Per catalogue | Pre-approved; deviation escalates to normal | CAB |
| SoD exception | Any | CFO or CTO, time-boxed; grantor ≠ beneficiary (`SP-004` A-87/A-88, `SOD-22`) | — |
| Master data change above the significance threshold | Per `MD-001` | Data domain owner (`SP-004` A-89) | CTO |
| Bulk personal-data export | Any | DPO + CTO, logged (`SP-004` A-92, `BRU-SEC-05`) | — |
| Use unmasked production data in a non-production environment | **None — class H, no override** (`BRU-SEC-08`) | — | — |

> Must reconcile exactly with `SP-004`.

---

## 8. Exceptions and Failure Handling

| Exception | Immediate action | Who to inform | Recorded where |
|---|---|---|---|
| P1 incident — business stopped | **L4-direct: CTO + R05 + CEO**, 24×7, acknowledge within 15 minutes (`SP-005` TE-E1) | As stated | Incident record + post-mortem |
| Change causes an incident | Roll back; treat as a failed change; post-implementation review is mandatory | CAB, CTO | Failed change record |
| Change implemented without approval | Control failure; investigate; consider reverting | CTO, Internal Audit | Control exception |
| Integration failure | Circuit breaker opens; fallback activated (`AUT-053`); escalate (`SP-005` TE-E3) | Integration owner, CTO | `NT-021` alert record |
| Undetected integration failure beyond 5 minutes | `KPI-088` targets zero; investigate the monitoring, not only the integration | CTO | Monitoring gap record |
| Backup restore test fails | **Escalate immediately**; an untested backup is not a backup (`KPI-091`) | R33, CTO (`SP-005` TE-E7) | Restore test record |
| Critical vulnerability open beyond 7 days | `KPI-089` targets zero; escalate daily past 7 days | CTO (`SP-005` TE-E8) | Vulnerability register |
| Orphaned account found after a leaver | Revoke; investigate the `AUT-048` failure | CTO, R30 | Access incident |
| Suspected personal-data breach | **L4-direct: CTO + DPO + Legal** within the hour (`SP-005` TE-E9) | As stated | Breach register |
| Emergency change rate rising | The normal path is too slow; fix the process, do not normalise emergencies | CTO | CAB review |
| Shadow IT discovered | Assess risk, bring under management or remove; ask why the sanctioned path did not meet the need | CTO | Risk record |

---

## 9. Manual Fallback

| Step | Manual action |
|---|---|
| 1 | The service desk operates from a **manual ticket log** — telephone and paper — with sequential reference numbers |
| 2 | Priority and escalation follow `SP-005` unchanged; the escalation path is telephone-based and does not depend on tooling |
| 3 | Change records are completed on the **manual change form**, with CAB approval by signature or recorded email from named members. **CAB approval is not skipped during an outage** |
| 4 | Access grants during an outage require the same `SP-004` approvals, recorded on the manual access form, and are re-verified on restoration |
| 5 | **Back-enter every ticket, change and access grant within 48 hours** |
| 6 | CTO reviews all manually approved changes and access grants after restoration |

---

## 10. Controls

| Control | Type | Frequency | Evidence |
|---|---|---|---|
| Production change traceable to an approved change record | Preventive (`BRU-ADM-02`) | Per change | Hard block |
| Change owner cannot approve their own change | Preventive | Per change | CAB record |
| Access derived from position, never copied | Preventive | Per grant | Provisioning record |
| SoD evaluated at role assignment | Preventive (`BRU-SEC-07`, `NFR-064`) | Per assignment | Hard block |
| MFA on admin, finance and HR access | Preventive (`BRU-SEC-01`) | Per login | Auth log |
| Step-up authentication for sensitive actions | Preventive (`BRU-SEC-02`) | Per action | Auth log |
| Leaver access revoked within one hour | Preventive (`BRU-SEC-06`, `AUT-048`) | Per leaver | Revocation log |
| Production data masked in non-production | Preventive (`BRU-SEC-08`) | Continuous | Environment control |
| Bulk personal-data export requires approval and is logged | Preventive (`BRU-SEC-05`) | Per export | Export log |
| Access certification cycle | Detective (`AUT-052`) | Per cycle | Certification record |
| Change success and rollback rate | Detective | Monthly | CAB report |
| Emergency change rate and retrospective review completion | Detective | Monthly | CAB report |
| Backup restore tests | Detective | Per schedule | `KPI-091` |
| Uptime and latency | Detective | Continuous | `KPI-085`, `KPI-086` |

---

## 11. Segregation of Duties

| Duty A | Incompatible with Duty B | Enforcement | Compensating control |
|---|---|---|---|
| Administer users | Approve access requests for oneself (`SOD-09`) | Hard block | — |
| Execute a change | Be its sole approver | Hard block via CAB | Emergency path with CTO approval and retrospective CAB review |
| Grant an SoD exception | Be its beneficiary (`SOD-22`) | Hard block | — |
| Hold configuration access | Hold transactional posting rights (`SOD-42`) | Hard block at assignment | R33 configures; Finance posts |
| Author a guard rail or alert rule | Be sole approver of its removal or indefinite suppression (`SOD-36`) | Hard block | CTO countersign |

---

## 12. KPIs

| KPI | Definition (`RP-001`) | Baseline | Target |
|---|---|---|---|
| `KPI-085` | System uptime (business hours) | no baseline stated in `06-02` | ≥ 99.9% |
| `KPI-086` | API p95 latency | no baseline stated in `06-02` | < 400 ms |
| `KPI-088` | Integration failures undetected > 5 min | no baseline stated in `06-02` | **Zero** |
| `KPI-089` | Critical vulnerabilities open > 7 days | no baseline stated in `06-02` | **Zero** |
| `KPI-090` | Orphaned accounts after leaver | no baseline stated in `06-02` | **Zero beyond 24 h** |
| `KPI-091` | Backup restore tests passed | no baseline stated in `06-02` | 100% |
| Change success rate | Changes implemented without rollback or incident | untracked | To be set |
| Emergency change proportion | Emergency changes as a share of all changes | untracked | Falling |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| `OP-008` Incident Management Runbook | Severity classification and technical response |
| `UI-036` Workspace — System Console Copy | The screens used |
| `NT-021` System, Integration and Job Failure Alert Library | Alert content |
| [`SP-023_SOP_Recruitment_and_Onboarding.md`](SP-023_SOP_Recruitment_and_Onboarding.md) | Provisioning and revocation triggers |
| [`SP-011_SOP_Remote_Support_and_Managed_Services.md`](SP-011_SOP_Remote_Support_and_Managed_Services.md) | The same change discipline applied to customer estates |
| [`SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Problem records raising CAPAs |
| [`../06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../06A_Process_Architecture/SP-005_Escalation_Matrix.md) | TE-E1…TE-E12 |
| [`../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md`](../06A_Process_Architecture/SP-006_Segregation_of_Duties_Register.md) | The 60 controls this SOP's engine must enforce (`RA-10`) |
| [`../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md`](../06A_Process_Architecture/SP-004_Approval_Matrix_and_Delegation_of_Authority.md) | The 97 authorities this SOP's engine must gate (`RA-01`) |
| `TR-021` Course Pack — System Administrator | Trains this SOP |

---

## 14. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue | Chief Technology Officer (pending) |

**Open item**

| # | Item | Owner | Needed by |
|---|---|---|---|
| O-01 | **This SOP is scheduled for W5, but the change control it defines governs the W1 build and every wave after it.** A programme running from W1 to W5 without a change process leaves five waves of production configuration untraceable. Either the SOP moves earlier or an interim programme change process is adopted and named | CTO + PMO | **Before W1 build** — raised as a finding in `AUDIT-006` |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_SOP.md` — all 14 sections present
- [x] "Speed is not an exemption from the change record" stated at the decision point
- [x] Emergency change defined as a service condition, not a schedule preference
- [x] Access-on-urgency explicitly refused, with the DL-09 alternative named
- [x] Manual fallback preserves CAB approval and `SP-004` levels
- [x] §7 reconciles with `SP-004`
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **O-01 wave conflict resolved — outstanding; the change process is needed from W1, not W5**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] CAB membership, cadence and quorum defined — **outstanding**
- [ ] Walked end-to-end in UAT (`PD-19`) — **outstanding**
- [ ] Named approver recorded — **pending CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
