---
id: TR-021
title: Course Pack — System Administrator
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development with Internal IT
author: Learning & Development with Internal IT and Security
reviewers: [CTO, Security Lead, Quality Manager, Operations Director, Legal Counsel, Data Services Lead, Localisation Lead]
approver: CTO with Security Lead
content_class: C
purpose: >
  Trains the internal IT administrators who hold the most destructive permissions in the platform,
  and — as an interim route — the remote support engineers who hold equivalent permissions on
  customers' estates. A wrong administrative action is not a transaction to be corrected; it is a
  configuration change, a permission grant or a deletion that affects everyone at once.
traces_to: [M29, M30, M66, M05, M22, M62, P03, 05-04, MD-009, MD-026, TR-001, TR-002, TR-004, TR-006, TR-022, UI-036, SP-011, SP-031, KB-007, LG-020, LG-021]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-021_Course_Pack_System_Administrator_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md — R33 IT / System Administrator, all systems scope; 05-05 §2 BRU-SEC family and BR-STD-06 override discipline
    verified: 2026-08-17
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md — internal ticket handling, priority, change request, CAB, release, rollback, emergency change
    verified: 2026-08-17
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md — consent capture, session control, evidence, patch and alert handling (R13 delta)
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P03 system console; administrator actions are the most destructive in the system and their confirmation copy is a safety control
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — System Administrator

| Item | Value |
|---|---|
| Audience role(s) | `R33` IT / System Administrator · **`R13` Remote Support Engineer (delta, `TR-002` §7.4)** |
| Headcount | `R33` 4–8 · **`R13` 15–40** |
| Duration | **Core 12 hours** over three days · **MSP delta 6 h** · plus 10 days supervised OJT |
| Delivery mode | Classroom with a **non-production** sandbox |
| Language | English primary with Bengali parallel (`DS-18`) |
| Prerequisites | Layer 1 universal core — **including information security** |
| Certification outcome | Functional competence record (`TR-006` cell 12) — **gates administrative access** |
| Wave | W1 |

> **This pack carries `R13` Remote Support Engineer** as an interim route under `TR-002` §7.4,
> because no pack exists for `SP-011` — a gap `AUDIT-006` SP-02 and `KB-007` `O-03` both record.
> `CU-16` requires the compromise to be declared; §3.2 declares it, and it is the **largest** of the
> four interim routes: 15–40 people with privileged access to customer estates.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Operate the system console within their scope, and state what lies outside it | Sandbox + items |
| 2 | **Grant, modify and revoke access correctly, and never beyond the requested scope** | **Critical items** — `05-04`, `M29` |
| 3 | Recognise a destructive action, honour its confirmation, and know what cannot be undone | **Critical practical** |
| 4 | Make a configuration change through change control, with a rollback prepared | Practical — `SP-031` |
| 5 | Handle an emergency change correctly and complete the retrospective record | Scenario |
| 6 | **Never use a shared or personal credential, and never record one** | **Critical items** — `TG-43` pattern |
| 7 | Read and preserve the audit trail; recognise when their own action needs justification | Items |
| 8 | Operate the competence-gating link — how `M22` signals affect access (`CU-05`) | Sandbox |
| 9 | Respond to a security event within `SP-031` and escalate correctly | Scenario |
| 10 | *(MSP delta)* Obtain and record consent, control a session, and apply `KB-007` §5.1 before touching a degraded array | **Critical practical** |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| **Administrative access grant** | Layer 1 core including security | On release (`TR-024`); **security content annually** |

---

## 3. Module Outline

### 3.1 Core — 12 hours

| # | Module | Duration | Method |
|---:|---|---|---|
| 1 | The blast radius of an administrative action | 45 min | Facilitated |
| 2 | The system console and scope boundaries | 90 min | Walkthrough — `UI-036` |
| 3 | **Access: grant, modify, revoke — and the least-privilege rule** | 120 min | Practical — `05-04`, `M29` |
| 4 | **Destructive actions, confirmations and what cannot be undone** | 90 min | Practical |
| 5 | Configuration change through change control | 90 min | Practical — `SP-031` |
| 6 | **Rollback — prepared before the change, not after** | 60 min | Practical |
| 7 | Emergency change and the retrospective record | 45 min | Scenario |
| 8 | **Credentials — never shared, never recorded** | 45 min | Items + scenario |
| 9 | Audit trail and self-justification | 45 min | Items |
| 10 | Competence gating and access (`CU-05`) | 45 min | Sandbox — `M22` |
| 11 | Security events and escalation | 60 min | Scenario — `SP-031` |
| 12 | Service desk: priority, routing and the user experience of a ticket | 45 min | Practice |
| | **Total** | **~12 hours** | |

### 3.2 MSP delta — 6 hours (`R13`) — *declared interim route*

| Content | Source |
|---|---|
| **Consent capture and session control on a customer estate** | `SP-011`, `LG-016` |
| Evidence and session logging | `SP-011` |
| **The degraded-array sequence — stop, record, verify, decide** | `KB-007` §5.1 `TG-36` |
| Backup verification before data-path work | `KB-007` `TG-39` |
| Rollback and maintenance windows on a client system | `KB-007` `TG-38`, `TG-44` |
| **Client credentials — issued accounts only, never recorded** | `KB-007` `TG-43` |
| CCTV footage and privacy handling | `KB-007` §6.2 |
| Access control and the egress test | `KB-007` §6.3 |

**`PK-10`: this delta is an interim control and the most consequential of the four.** `R13` operates
on customer infrastructure where an error stops a client's business or destroys their data. A
system-administrator pack teaches the right instincts but not the domain. Gap: `TR-002` `O-03`,
`KB-007` `O-03`.

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions |
|---|---|---|
| 1 | An agent's mistake affects one job. **Yours affects everyone, at once, and often silently** | *"I'll test it in production, it's a small change."* |
| 3 | Least privilege is not distrust of colleagues; it is limiting the damage of a compromised account — including yours | *"Give them admin, it's easier."* |
| 4 | Some actions cannot be undone. **The confirmation dialog is a safety control, not an obstacle** (`UI-036`) | *"I read it."* — did you read *this* one? |
| 6 | **A change without a prepared rollback is not a change; it is a gamble** (`TG-38`) | *"We can restore from backup."* — verified when? |
| 8 | A credential in a ticket, a screenshot or a chat message is a credential that has left your control permanently | *"It's an internal system."* |
| 9 | You are the one role whose actions nobody else reviews in real time. **The audit trail is how the company trusts you** | *"Nobody checks."* |
| 3.2 | On a degraded array, the **client** owns the risk decision (`TG-36` step 7). Making it for them — even correctly — transfers the consequence to us | *"I know what's best for their data."* |

---

## 5. Participant Workbook Contents

Console scope map · **least-privilege access decision aid** · **destructive-action list — what
cannot be undone** · change-control flow and rollback template · emergency-change record · **credential
rules** · audit-trail guide · competence-gating explanation · security-event escalation ·
*(delta)* **consent, session, degraded-array and backup-verification cards** (from `KB-007`) ·
**my scope and what lies outside it**.

---

## 6. Exercises

| # | Exercise | Sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Grant access for three requests | **Non-production** sandbox | One over-scoped request | **Over-scoped request refused or reduced** |
| 2 | Revoke on a leaver | Sandbox | Leaver record | Complete and timely |
| 3 | **Destructive-action drill** | Sandbox | Action with an irreversible consequence | Confirmation honoured; consequence stated correctly |
| 4 | Configuration change with rollback | Sandbox | Change request | **Rollback prepared before execution** |
| 5 | Emergency change | Scenario | Out-of-hours incident | Correct route; retrospective record complete |
| 6 | **Credential scenario** | Scenario | Colleague requests a shared login | Refuses; provides the correct route; records it |
| 7 | Audit-trail review | Sandbox | Trail with an unexplained action | Identifies and escalates |
| 8 | Competence-gated access | Sandbox | User without a passed assessment | Access withheld (`CU-05`) |
| 9 | Security event | Scenario | Suspected compromise | Correct containment and escalation |
| 10 | *(Delta)* **Degraded array** | Scenario | Client array, one member failed | **`TG-36` sequence followed; client decision sought before any action** |
| 11 | *(Delta)* Consent and session | Practical | Client remote session | Consent captured and logged before connection |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification |
|---|---:|---:|---:|---|
| `TR-006` cell 12 form, 30 items | 25% | 80%, **100% on access, credential and destructive-action items** | 3 | 24 months |
| **Access exercises (1, 2, 8)** | 25% | All passed | 3 | 24 months |
| **Destructive-action and rollback (3, 4, 6)** | 25% | All passed | 2 | **Annual** |
| Change, audit and security (5, 7, 9) | 25% | All passed | 3 | 24 months |
| *(Delta)* exercises 10, 11 | Gate for `R13` | Both passed | 2 | **Annual** |
| **OJT sign-off — 10 days, all changes reviewed** | Gate | CTO or Security Lead | — | — |

> **`PK-11`: no administrative access is granted before this assessment is passed.** `R33` is the
> clearest case of `LS-14` and `CU-05` in the register.

---

## 8. Job Aids Produced

Console scope map · least-privilege decision aid · **destructive-action list** · change and rollback
template · credential rules card · security-event escalation card · *(delta)* **`KB-007` cards —
degraded array, backup verification, consent, egress test** (sourced from `KB-007`, `CP-01`).

---

## 9. Trainer Requirements

L&D with **Security Lead delivering modules 3, 8 and 11** · CTO for module 1 · **`R13` senior and
Data Services for the delta** · **a non-production sandbox that can be destroyed and rebuilt** ·
cohort maximum 8 core, 12 delta · Legal input on the delta's consent content.

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence refusing an over-scoped access request | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and destructive-action practical | > 90% first attempt — **the highest bar in the category** |
| **Behaviour** | Over-scoped grants · changes without rollback · shared-credential incidents · unexplained audit entries · *(delta)* client-decision compliance on arrays | **All target zero** |
| **Result** | Security incidents attributable to administration · unplanned outages from change · **zero data-loss events on client estates** | Per `RP-001`, `SP-031` |

**Required Drivers** (`LS-04`): reinforce — destructive-action list and rollback template ·
encourage — CTO reviews every change for the first month · monitor — audit-trail review, weekly ·
reward — access granted; competence record.

---

## 11. Related Documents

[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) *(delta)* ·
`KB-007` Troubleshooting Guide Set — Server, Network and CCTV *(delta source)* ·
`UI-036` system console copy · `LG-020` acceptable use · `LG-021` ISMS policy set ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) cell 12 ·
[`../08A_Framework/TR-002_Role_Based_Curriculum_Map.md`](../08A_Framework/TR-002_Role_Based_Curriculum_Map.md) §7.4.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The `R13` delta is the largest interim route in the category — 15–40 people with privileged access to customer estates, trained on a pack designed for internal administration.** `AUDIT-006` SP-02 and `KB-007` `O-03` both record the gap; a proper `R13` pack requires a register change | Programme Content Lead with CTO | **W1 for internal; W4 before the first MSP contract** |
| **O-02** | **`KB-007`'s 34 articles are unwritten** (`AUDIT-008`). The delta teaches `TG-36`, `TG-38`, `TG-39` and §6.2/§6.3 from a specification, not from authored content | Technical Director | **W4** |
| **O-03** | **A destroyable non-production sandbox is required** for exercises 3 and 4. Using a shared environment makes the destructive-action drill impossible to run honestly | CTO with L&D | **W1 — blocking** |
| **O-04** | `LG-020` and `LG-021` are unwritten (Category 10 unstarted). Modules 8 and 11 have no governing source | Legal Counsel with Security Lead | W1 |
| **O-05** | `CU-05` competence gating (module 10, exercise 8) depends on `M29` reading an `M22` signal — unconfirmed (`TR-002` `O-07`, `TR-004` `O-03`, `TR-006` `O-04`) | CTO with Security Lead | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable (`DS-02`); Level 4 measures named as zero-targets (`LS-01`)
- [x] **`R13` interim route declared as the largest and most consequential of the four (`PK-10`, `CU-16`)**
- [x] Least privilege, destructive actions and credentials taught as critical, annually-refreshed competences
- [x] Rollback taught as a precondition of change, not a recovery step
- [x] Access grant made conditional on assessment (`PK-11`, `LS-14`, `CU-05`)
- [x] Delta content sourced from `KB-007` rather than restated (`CP-01`, `LS-15`)
- [x] Highest learning bar in the category set deliberately (> 90%)
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-SEC-*`, `BR-STD-06` cited to `05-05`; `TG-*` rules cited to `KB-007`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` proper `R13` route — outstanding; 15–40 people on an interim control**
- [ ] **`O-03` destroyable sandbox — outstanding; blocks the destructive-action drill**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending CTO and Security Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
