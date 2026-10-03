---
id: TR-024
title: Release Training and Refresher Standard
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Change Management and Internal IT
reviewers: [HR Director, CTO, Operations Director, Quality Manager, Content Design Lead, Localisation Lead]
approver: HR Director with CTO
content_class: D
purpose: >
  The standard that makes retraining repeatable and cheap across nine waves and thirty-six months.
  Users will be retrained repeatedly; without a standard, every release produces an improvised
  scramble that costs more than the release, or — more commonly — produces nothing at all and the
  workforce discovers the change in production.
traces_to: [M22, M30, M66, 06-01, TR-001, TR-002, TR-003, TR-004, TR-005, TR-006, TR-022, TR-023, KB-015, OP-006, SP-031, CM-008]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: TR-024_Release_Training_and_Refresher_Standard_BN.md
sources:
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md — nine delivery waves over thirty-six months
    verified: 2026-08-17
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md — change request, CAB, release, rollback, emergency change
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-019 automatic assignment by role and identified gap; §5.4 FR-LMS-031 automatic needs identification from performance gaps, non-conformances, safety incidents and new products
    verified: 2026-08-17
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md — the parallel currency mechanism for knowledge content, including suspension and purge
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Release Training and Refresher Standard

| Item | Value |
|---|---|
| Audience role(s) | **All 35 internal roles**, scoped per release |
| Headcount | **800+**, of whom only the affected subset is trained per release |
| Duration | **Tiered — 5 minutes to 4 hours** by change class (§3.2) |
| Delivery mode | Predominantly on-device and in-app; classroom only for tier 4 |
| Language | Bengali primary for operational roles |
| Prerequisites | The role's original course pack |
| Certification outcome | Re-assessment only where the change affects a gated competence (§3.4) |
| Wave | W2 — **then every release, permanently** |

> **This is the only pack in the category that never finishes.** Every other file is authored,
> delivered and refreshed on a cycle. This one runs on every release for the life of the system.

---

## 1. Learning Objectives

**The standard's objectives are properties of the process, not of a learner.**

| # | For every release, the process… | Verified by |
|---|---|---|
| 1 | Identifies who is affected, from the change record rather than by assumption | `RL-01` |
| 2 | Classifies the change into a training tier with a declared response | `RL-02` |
| 3 | Produces the training artefact **before** the release, not after | `RL-03` |
| 4 | Updates the affected job aids, question-bank items and knowledge content | `RL-04` |
| 5 | Reaches the affected population before they meet the change in production | `RL-05` |
| 6 | Re-assesses where a gated competence changed | `RL-06` |
| 7 | Withdraws superseded material from the point of work | `RL-07` |
| 8 | Measures whether it worked — support volume after release | `RL-12` |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Every release, permanently | The role's original pack | The standard itself: annually |

---

## 3. Module Outline — *the standard*

### 3.1 The release-training pipeline

**`RL-01`: the affected population comes from the change record** (`SP-031`), not from a guess.

| Step | When | Owner | Output |
|---|---|---|---|
| 1 | Change raised | Change owner | Change record names affected modules, portals and roles |
| 2 | **CAB or release planning** | L&D attends | **Training tier assigned (§3.2)** |
| 3 | Release − 3 weeks | L&D | Training artefact drafted |
| 4 | Release − 2 weeks | Domain owner | Artefact reviewed; **job aids, items and `KB` content updated** (`RL-04`) |
| 5 | Release − 1 week | L&D + champions | Champions briefed (`TR-023`) |
| 6 | Release − 3 days | L&D | **Artefact published to the affected population** (`RL-05`) |
| 7 | Release day | Champions | On the floor at affected sites |
| 8 | Release + 1 week | L&D | **Support-volume review** (`RL-12`) |
| 9 | Release + 2 weeks | L&D | Superseded material withdrawn (`RL-07`) |

**`RL-08`: L&D attends CAB.** Training is not informed of releases; it participates in deciding
them. A change that cannot be trained inside the window is a change that needs a different window.

### 3.2 Training tiers

**`RL-02`: every change gets a tier, including tier 0.**

| Tier | Change class | Response | Duration | Assessment |
|:--:|---|---|---|:--:|
| **0** | No user-visible change | **Nothing** — recorded as tier 0 so the decision is explicit | — | — |
| **1** | Cosmetic or label change | In-app notice; job aid updated if it quotes the label | < 5 min | — |
| **2** | Task changes, same outcome | Microlearning item + job aid update | 5–15 min | Knowledge check |
| **3** | New task, new screen, or a changed rule | Microlearning set + job aid + **question-bank items updated** | 15–60 min | Knowledge check |
| **4** | **New module, new portal, or a changed gated competence** | Full session; may require re-certification | 1–4 hours | **Re-assessment** (`RL-06`) |
| **E** | **Emergency change** | Same-day notice, retrospective artefact within 5 days | Immediate | Per tier once classified |

**`RL-09`: tier is assigned by L&D with the change owner, and a disagreement escalates to the CTO.**
The incentive to under-tier is real — a lower tier is cheaper and faster — and it is exactly how a
workforce meets a changed rule in production.

### 3.3 What a release updates

**`RL-04`: a release does not update the course; it updates everything the course produced.**

| Artefact | Owner | Rule |
|---|---|---|
| Course pack modules | L&D | Amended, versioned |
| **Job aids** (`TR-022`) | L&D | Revised or withdrawn (`JA-13`, `JA-14`) |
| **Question-bank items** (`TR-006`) | Domain owner | **Items testing a changed transaction are retired, not edited** (`TR-006` §11) |
| Technician bank (`TR-005`) | Technical | Reviewed if the change touches technical work |
| **Knowledge articles and cards** (`KB-015`, `KB-016`) | Knowledge Manager | Reviewed at the change's severity (`KR-06`) |
| Screenshots (`DS-15`) | Content Design | Re-captured or removed |
| Champion briefs | L&D | Issued at release − 1 week |
| Help content (`HC-*`) | Content Design | Aligned |

> **The question-bank consequence is the one most often missed.** `TR-006` §11 records that the
> functional bank ages with the software rather than with the devices. A release that changes a
> transaction silently invalidates every item testing it, and an assessment gating production access
> on obsolete items is worse than no assessment.

### 3.4 Re-assessment triggers

**`RL-06`: re-assessment is required only where a gated competence changed.**

| Trigger | Re-assessment |
|---|---|
| A hard business rule (`BRU-*`, `BR-STD-*`) changes | **Yes** — the items testing it and the affected population |
| An access scope changes (`05-04`) | **Yes** for the affected roles |
| A safety procedure changes | **Yes**, and immediately (`LS-10`) |
| A statutory treatment changes — VAT, payroll, filing | **Yes** for the affected function (`TR-014`, `TR-015`) |
| A transaction changes but the rule does not | Knowledge check only |
| A label or layout changes | No |

### 3.5 Scheduled refreshers — independent of releases

| Content | Interval | Basis |
|---|---|---|
| **Safety and statutory** | **Annual** | `LS-10`; Labour Rules expectation |
| Brand certification | Per `MD-011` validity | Brand terms |
| Technician technical | 24 months | `TR-005` |
| Functional competence | 24 months | `TR-006` |
| Framework and policy | Annual | `TR-001`…`TR-004` |

**`RL-10`: a scheduled refresher is not skipped because a release-training event happened
recently.** They serve different purposes — one restores decayed competence, the other teaches a
change.

---

## 4. Facilitator Guide — *operating the standard*

| Topic | Talking points | Common failure |
|---|---|---|
| Tiering | The tier is a decision with a cost either way. **Under-tiering is not cheaper; it moves the cost to the service desk and to errors** | *"It's only a small change."* |
| Timing | Artefacts before the release. A training artefact published after go-live is a post-mortem | *"We'll do it once it's stable."* |
| Population | The change record names it. **Training "everyone to be safe" wastes 800 people's time and trains nobody well** | *"Send it to all users."* |
| Withdrawal | Superseded aids left at the workstation are actively harmful — a user cannot tell which is current (`JA-14`) | *"We'll clear them out later."* |
| Measurement | Support volume in the week after release is the honest measure of whether it worked | *"Attendance was good."* |
| Emergency change | Tier E still gets an artefact — retrospectively, within five days | *"It was an emergency, there was no time."* |

---

## 5. Participant Workbook Contents

Not a taught course. **What the standard issues per release:**

| Artefact | Audience |
|---|---|
| Release training brief — what changed, who is affected, what to do | Champions, managers |
| Microlearning item(s) | Affected users |
| Updated job aids | Affected workstations |
| Champion brief | Champions (`TR-023`) |
| Re-assessment notice, where triggered | Affected users, `M22` |
| **Withdrawal list** — what to remove from workstations | Site owners |

---

## 6. Exercises — *the standard's own tests*

| # | Test | Method | Success criterion |
|---|---|---|---|
| 1 | **Tiering consistency** | Ten past changes tiered independently by two assessors | Agreement on at least 8 |
| 2 | Pipeline timing | Audit of the last five releases | Artefacts published before release in all 5 (`RL-03`, `RL-05`) |
| 3 | **Artefact completeness** | Per release, against §3.3 | All applicable artefacts updated |
| 4 | Withdrawal | Site spot-check after release | **No superseded aid at any checked workstation** |
| 5 | Re-assessment trigger | Audit against §3.4 | Every gated change re-assessed |
| 6 | **Support-volume response** | Service-desk data, week after release | Contacts on the changed task within the declared threshold |

---

## 7. Assessment

The standard is audited, not assessed. Its gates:

| Gate | Standard | Owner |
|---|---|---|
| Tier assigned to every change, including tier 0 | 100% (`RL-02`) | L&D at CAB |
| Artefact published before release | 100% (`RL-05`) | L&D |
| All applicable artefacts updated | 100% (`RL-04`) | L&D with domain owners |
| Superseded material withdrawn within 2 weeks | 100% (`RL-07`) | Site owners |
| Re-assessment where triggered | 100% (`RL-06`) | L&D with `M22` |
| Post-release review completed | 100% (`RL-12`) | L&D |

---

## 8. Job Aids Produced

Release training brief template · **tiering decision aid** · artefact update checklist (§3.3) ·
withdrawal list template · champion release-brief template · post-release review template.
All in `TR-022`.

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| **L&D presence at CAB** | `RL-08` — a standing seat, not an invitation |
| Artefact authors | L&D with the domain owner of the changed area |
| Champions | Briefed at release − 1 week (`TR-023`) |
| **Capacity** | Nine waves plus routine releases means this is **continuous load**, not project load |
| Bengali | Every release artefact for operational roles, authored in Bengali |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Whether users felt prepared for the change | Diagnostic only (`LS-02`) |
| **Learning** | Knowledge-check pass on tier 2–3; re-assessment pass on tier 4 | > 85% |
| **Behaviour** | **Error rate on the changed task in week 1 vs the prior baseline** · superseded-aid sightings · re-assessment completion | Errors return to baseline within 2 weeks |
| **Result** | **Service-desk contacts per release, per affected user** · release-related incidents · `KPI-064` mandatory completion maintained across waves | Contacts per release falling wave on wave |

**Required Drivers** (`LS-04`): reinforce — updated job aids at the workstation · encourage —
champions on the floor on release day · monitor — post-release support-volume review · reward —
none needed; **a release that goes quietly is its own reward**.

> **`RL-12`: service-desk contacts in the week after release, per affected user, is the standard's
> single honest measure.** It is available for free, it cannot be gamed by the training function,
> and it falls when the standard works.

---

## 11. Related Documents

[`../08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md`](../08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md) §4.8 — refresh and decay ·
[`../08A_Framework/TR-002_Role_Based_Curriculum_Map.md`](../08A_Framework/TR-002_Role_Based_Curriculum_Map.md) `CU-14` — retraining after early exposure ·
[`../08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) `DS-15` — screenshots versioned to a release ·
[`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) §11 — release sensitivity of the bank ·
[`TR-022_Job_Aid_and_Quick_Reference_Library.md`](TR-022_Job_Aid_and_Quick_Reference_Library.md) `JA-13`, `JA-14` ·
[`TR-023_Train_the_Trainer_and_Super_User_Kit.md`](TR-023_Train_the_Trainer_and_Super_User_Kit.md) — champions carry the release brief ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) — the change process this attaches to ·
`KB-015` Knowledge Review, Currency and Retirement Policy — **the parallel mechanism for knowledge content** ·
`OP-006` Release and Deployment Operations · `CM-008` change communications.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **L&D has no seat at CAB** (`RL-08`). `SP-031` defines the change process and does not name a training participant. **The entire standard depends on this one arrangement** | CTO with HR Director | **W2 — before the first post-go-live release** |
| **O-02** | **Continuous release-training capacity is unresourced.** Nine waves plus routine releases over 36 months is permanent load on a training function that has no establishment (`TR-001` `O-04`) | HR Director with L&D | **W2** |
| **O-03** | **This pack is `P2`/`W2`, but releases begin at W1.** The first W1 releases will occur without the standard — raised as audit finding **TR-09** | Programme Content Lead with CTO | **W1** |
| **O-04** | `OP-006` release and deployment operations is unwritten (Category 17 unstarted); the pipeline in §3.1 assumes a release process it cannot yet reference precisely | Internal IT with L&D | W2 |
| **O-05** | The tiering decision aid and the post-release review template do not exist; §6 tests 1 and 6 cannot run without them | L&D | W2 |
| **O-06** | Service-desk data granularity — contacts attributable to a **specific changed task** — is unconfirmed. `RL-12`, the standard's only honest measure, depends on it | CTO with Internal IT | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections retained in order, standard-level interpretation stated; §11 and Open Items added per category convention
- [x] Pipeline defined with owners and timing relative to release, not to convenience
- [x] Tiering defined including **tier 0**, so "no training needed" is an explicit decision
- [x] Under-tiering identified as the standard's principal failure mode, with an escalation route
- [x] Release consequences extended to job aids, **question-bank items** and knowledge content (`RL-04`)
- [x] Re-assessment limited to genuinely gated competence changes (`RL-06`)
- [x] Scheduled refreshers kept independent of release training (`RL-10`)
- [x] Withdrawal of superseded material made an enforced step (`RL-07`)
- [x] Single honest measure identified — service-desk contacts per affected user (`RL-12`)
- [x] All four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `FR-LMS-019`/`-031` cited to `M22`; `KPI-064` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` L&D seat at CAB — outstanding; the standard does not function without it**
- [ ] **`O-03` W2 placement versus W1 releases — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Director and CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
