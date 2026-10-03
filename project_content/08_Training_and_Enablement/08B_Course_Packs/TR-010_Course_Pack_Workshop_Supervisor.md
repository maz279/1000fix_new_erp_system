---
id: TR-010
title: Course Pack — Workshop Supervisor
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Workshop Operations
reviewers: [Operations Director, Technical Director, Quality Manager, HSE Lead, Finance Manager, Localisation Lead]
approver: Operations Director with Technical Director
content_class: D
purpose: >
  Trains 20–40 workshop supervisors on the three levers that determine workshop margin — work in
  progress, escalation and the quality gate. A supervisor who releases work without a QC gate
  converts throughput into rework, and rework is the largest single controllable cost in a depot
  repair operation.
traces_to: [M31, M15, M22, M23, M45, P03, MD-010, MD-011, MD-022, MD-025, MD-026, TR-001, TR-002, TR-004, TR-006, TR-022, UI-026, SP-010, SP-013, SP-016, KB-012, KB-013, KB-014]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-010_Course_Pack_Workshop_Supervisor_BN.md
sources:
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md — bench assignment, WIP control, L1/L2/L3 escalation, parts hold, QC gate, release
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-06 rework auto-flagged within 30 days; BRU-SRM-12 BER evidence and second technician; BRU-SRM-14 L3 restricted to an equipped workshop and certified specialist; BRU-INV-07 goods failing inspection go to quarantine
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-004 first-time fix 70% to 88%
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Workshop Supervisor

| Item | Value |
|---|---|
| Audience role(s) | `R09` Workshop Supervisor |
| Headcount | **20–40** |
| Duration | **8 hours** over two days, plus 5 days supervised OJT |
| Delivery mode | Classroom with sandbox; regional cohorts |
| Language | Bengali primary, English parallel |
| Prerequisites | Layer 1 universal core · technician competence at `L2` or above |
| Certification outcome | Functional competence record (`TR-006` cell 3) |
| Wave | W1 |

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Assign bench work by skill, certification and level, and recognise a blocked assignment | Items keyed to `BRU-SRM-09`, `BRU-SRM-14` |
| 2 | Control WIP — see the board, spot the ageing job, act before it becomes an SLA breach | Sandbox board exercise |
| 3 | Manage parts hold without letting held jobs disappear from view | Sandbox |
| 4 | Operate the **QC gate**: what is checked, what fails, and the authority to refuse release | Practical + scenario |
| 5 | Classify rework correctly and attribute it to cause rather than to a person | Scenario keyed to `BRU-SRM-06`, `KB-011` `KW-17` |
| 6 | Confirm a beyond-economic-repair conclusion as the second technician | Practical keyed to `BRU-SRM-12` |
| 7 | Escalate `L3` work to an equipped site rather than allowing an attempt | Scenario keyed to `BRU-SRM-14` |
| 8 | Verify that bench equipment is calibrated and that ESD control is working, and stop work when it is not | **Practical — critical** |
| 9 | Read repair time against `KB-014` norms without turning a norm into a deadline | Items keyed to `RT-09`, `RT-20` |
| 10 | Approve, refuse and record within their authority, with the right reason code | Sandbox + items |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to the `P03` workshop console · release authority | Layer 1 core · `TR-009` or equivalent technician competence | On release (`TR-024`); 24 months. **Equipment and safety content annually** |

---

## 3. Module Outline

| # | Module | Duration | Method | Materials |
|---:|---|---|---|---|
| 1 | The three levers — WIP, escalation, QC — and what each costs when it slips | 30 min | Facilitated | Workshop cost data |
| 2 | The workshop console — board, states, ageing, holds | 45 min | Walkthrough | `UI-026`, sandbox |
| 3 | **Bench assignment** — skill, certification, level, and the hard blocks | 60 min | Practice + items | `MD-010`, `MD-011` |
| 4 | **WIP control** — the ageing job, the parts hold, the forgotten unit | 60 min | Board exercise | Sandbox with seeded aged jobs |
| 5 | **The QC gate** — criteria, refusal, and why refusing is the job | 75 min | Practical + role play | `SP-010`, `KB-004`…`KB-007` §8 |
| 6 | Rework — classification, attribution, and the learning loop | 45 min | Scenario | `BRU-SRM-06`, `KB-011` |
| 7 | **BER confirmation as second technician** | 45 min | Practical | `BRU-SRM-12`, photographs |
| 8 | Escalation to `L3` and to an equipped site | 30 min | Scenario | `BRU-SRM-14` |
| 9 | **Equipment, calibration and ESD — stopping work when control has failed** | 60 min | Practical | `KB-012`, `KB-013` §3, `MD-046` |
| 10 | Repair time norms — using them without weaponising them | 45 min | Facilitated | `KB-014` §6.4 |
| 11 | Authority, approvals and reason codes | 30 min | Sandbox | `SP-004`, `MD-026` |
| 12 | Running a shift — handover, priorities, escalation | 45 min | Simulation | Shift scenario |
| | **Total** | **~8 hours** | | |

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions | Timing |
|---|---|---|---|
| 1 | Throughput without a QC gate is not throughput; it is deferred rework at a higher cost | *"We're behind, so let it go."* | 30 |
| 4 | The most expensive unit in a workshop is the one nobody has looked at for nine days | *"It's on hold, it's not my problem."* | 60 |
| 5 | **You have the authority to refuse release, and using it is not obstruction** | *"The branch is chasing, so I'll pass it."* | 75 |
| 6 | Rework caused by a known issue, a faulty instrument or a bad part is **not** the technician's rework (`KW-17`, `RT-18`) | *"Rework means someone made a mistake."* | 45 |
| 7 | BER needs photographs and a second technician's confirmation. **You are that second technician** and signing without looking is the failure `BRU-SRM-12` exists to prevent | *"They're experienced, I'll just sign."* | 45 |
| 9 | An out-of-calibration instrument produces confident wrong readings. `TE-04` says withdraw, not "use carefully" | *"It's only slightly out."* | 60 |
| 10 | A norm is a planning figure, not a stopwatch. A technician working to a clock skips the safety step | *"They're over standard, push them."* — `RT-20` | 45 |

---

## 5. Participant Workbook Contents

| Section | Purpose |
|---|---|
| The three levers, with cost | The mental model |
| Assignment matrix — skill, certification, level | And the three hard blocks |
| WIP ageing thresholds and actions | What to do on day 3, 5, 9 |
| **QC gate checklist per repair class** | `KB-004`…`KB-007` §8 verification criteria |
| Rework classification and attribution | `BRU-SRM-06`, `KW-17` |
| BER confirmation checklist | `BRU-SRM-12` |
| Equipment and ESD shift check | `KB-012` §5.1, `KB-013` §3.3 |
| Norm usage rules | `KB-014` `RT-09`, `RT-18`, `RT-20` |
| Approval authority and reason codes | `SP-004`, `MD-026` |
| **My access scope** | `QB-21` |

---

## 6. Exercises

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Assign 12 bench jobs across 6 technicians | `P03` sandbox | Mixed levels and brands | No certification or level breach |
| 2 | **Board triage — find the three jobs at risk** | Sandbox | Board with aged and held jobs | All three found; correct action per job |
| 3 | **QC gate — pass, fail, refuse** | Practical | 4 completed units, 2 defective | Both defectives caught; refusal recorded with reason |
| 4 | Rework classification | Scenario | 5 rework cases, 3 not technician-attributable | Correct attribution on all 5 |
| 5 | **BER second-technician confirmation** | Practical | Unit presented as BER with weak evidence | **Refuses to confirm; requests the missing evidence** |
| 6 | L3 escalation decision | Scenario | Board-level fault, no specialist on shift | Routes to equipped site |
| 7 | **Equipment check with a failed strap and an out-of-calibration meter** | Practical | Seeded failures | Both caught; station and instrument withdrawn |
| 8 | Shift simulation | Sandbox | Full shift with 4 disruptions | Shift completed; escalation raised where needed |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| `TR-006` cell 3 written form, 30 items | 30% | 80% overall, **100% on hard-rule items** | 3 | 24 months |
| Sandbox exercises 1, 2, 8 | 25% | All passed | 3 | 24 months |
| **QC gate practical (exercise 3)** | 20% | Both defectives caught | 3 | 24 months |
| **BER and equipment practicals (5, 7)** | 15% | Both passed | 3 | **Equipment annually** |
| Rework and escalation (4, 6) | 10% | Both passed | 3 | 24 months |
| **OJT sign-off — 5 shifts observed** | Gate | Operations Director or Technical Director delegate | — | — |

> Conforms to [`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md).

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| QC gate checklist per repair class | Two pages | Bench · `TR-022` |
| WIP ageing actions | One page | Console · `TR-022` |
| Assignment block matrix | One page | Console · `TR-022` |
| BER confirmation checklist | One page | `TR-022` |
| Equipment and ESD shift check | One page | Bench · sourced from `KB-012`/`KB-013` |
| Rework attribution guide | One page | `TR-022` |

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| Trainer | L&D with an experienced workshop supervisor or `R12` co-delivering |
| Practical assessor | Technical Director delegate for modules 5, 7, 9 |
| HSE | Module 9 approved by HSE |
| Sandbox | `P03` workshop console with a realistic board |
| Physical | 4 completed units (2 defective), a failed ESD strap, an out-of-calibration meter, a BER candidate unit |
| Cohort size | Maximum 10 |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence refusing a release | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and QC-gate practical pass | > 85% first attempt |
| **Behaviour** | QC refusal rate (should be **non-zero**) · WIP ageing profile · rework attribution accuracy · equipment withdrawal events | Refusals recorded; ageing falling |
| **Result** | **`KPI-004` first-time fix 70% → 88%** · rework rate falling · workshop margin | Per `06-02`, `RP-001` |

**Required Drivers** (`LS-04`): reinforce — QC checklist at the bench · encourage — Technical
Director backs a refusal publicly the first time it happens · monitor — refusal and rework rates ·
reward — competence record; workshop performance in `P06`.

> **A zero QC-refusal rate is a failure signal, not a success one.** Either nothing is defective —
> implausible — or the gate is not being operated. This is stated in module 5 and measured here.

---

## 11. Related Documents

| Document | Relationship |
|---|---|
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | The process this pack teaches |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | Rework classification |
| `KB-012` tool and equipment guides · `KB-013` safety data | Module 9 |
| `KB-014` repair time norms | Module 10 |
| `KB-011` known issues | Rework attribution |
| `UI-026` Workspace — Workshop Console Copy | The interface |
| [`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) | Cell 3 assessment |
| [`TR-009_Course_Pack_Field_Technician.md`](TR-009_Course_Pack_Field_Technician.md) | The prerequisite competence |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | `TS-002` sandbox with a realistic workshop board does not exist | Test Lead with L&D | **W1 — blocking** |
| **O-02** | **QC gate criteria per repair class come from `KB-004`…`KB-007` §8, which are unwritten** (`AUDIT-008` O-01). Module 5 teaches a gate with no published criteria | Technical Director | **W1** |
| **O-03** | Physical training units including deliberately defective ones must be assembled and maintained per delivering site | Technical Director with Operations | W1 |
| **O-04** | `KB-014` norms are unwritten and `MD-025` `standard_minutes` unpopulated (`KB-014` `O-01`). Module 10 teaches norm usage against no norms | Operations Director with Finance | W1 |
| **O-05** | `TR-006` cell 3 items do not exist and land at W2 while this pack is W1 (`TR-006` `O-01`) | L&D | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable and assessable (`DS-02`)
- [x] Level 4 measure named (`KPI-004`) and designed backwards from (`LS-01`)
- [x] QC-gate refusal authority taught explicitly, and a zero-refusal rate identified as a failure signal
- [x] Rework attribution taught as cause-based rather than person-based (`KW-17`, `RT-18`)
- [x] BER second-technician role assessed by requiring a refusal on weak evidence
- [x] Equipment and ESD control made a stop-work competence
- [x] Norms taught with the anti-weaponisation rules (`RT-09`, `RT-20`)
- [x] OJT sign-off gate present (`LS-03`); all four Required Drivers named (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-SRM-06`/`-09`/`-12`/`-14`, `BRU-INV-07` cited to `05-05`; `KPI-004` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` QC criteria from unwritten `KB` guide sets — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and Technical Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
