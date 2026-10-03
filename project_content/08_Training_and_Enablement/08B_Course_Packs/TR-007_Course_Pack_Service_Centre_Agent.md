---
id: TR-007
title: Course Pack — Service Centre Agent
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Branch Operations
reviewers: [Operations Director, Quality Manager, Branch Managers, Content Design Lead, Localisation Lead, HSE Lead]
approver: Operations Director with HR Director
content_class: D
purpose: >
  Trains 150–250 Service Centre Agents to competence on the walk-in intake and counter task set
  inside the four-hour target P03 commits to. This is the largest single user population in the
  programme and the highest-frequency process in the company; every downstream promise — SLA,
  diagnosis, warranty, analytics — is built on what the agent captures in the first three minutes.
traces_to: [M04, M01, M02, M09, M17, M20, M22, P03, P01, MD-021, MD-024, MD-026, MD-031, TR-001, TR-002, TR-003, TR-004, TR-006, TR-022, UI-013, UI-023, SP-007, SP-033, DT-002, DT-004]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-007_Course_Pack_Service_Centre_Agent_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P03 targets training-time-to-competence under four hours for a new agent, across 150–250 back-office users and fourteen workspaces on 1366×768 branch hardware
    verified: 2026-08-17
    class: P1
  - source: project_content/06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md — the governing procedure this pack teaches
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-01 a service order cannot be created without an identified device; BRU-SRM-02 warranty eligibility at order creation; BRU-SRM-07 estimates above BDT 5,000 require documented customer approval
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-010 walk-in intake time from about 10 minutes to under 4 then under 3
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Service Centre Agent

| Item | Value |
|---|---|
| Audience role(s) | `R08` Service Centre Agent |
| Headcount | **150–250** — the largest single population in the programme |
| Duration | **4 hours to Competent on the core task set**, plus 2 hours deferred (§3.3) |
| Delivery mode | Classroom or virtual with **live sandbox**, followed by supervised OJT |
| Language | **Bengali primary**, English parallel (`LS-07`, `DS-17`) |
| Prerequisites | Layer 1 universal core (`TR-002` §4.2) |
| Certification outcome | Functional competence record (`TR-006` cell 1) — **gates production access** (`CU-05`) |
| Wave | W1 |

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Complete a walk-in intake — greeting, identification, device receipt, condition capture, expectation setting, token, handover — **in under 3 minutes** with a live customer present | Sandbox timed transaction |
| 2 | Identify a device to a `MD-021` model, and register a new model correctly when it is not found | Sandbox + item |
| 3 | Capture device condition to evidential standard, including photographs, so that a later dispute can be settled | Sandbox + `DT-004` output review |
| 4 | Determine warranty and contract coverage before committing to a price or a promise | Sandbox + item |
| 5 | Apply intake triage to route the job correctly — bench, on-site, remote, not-a-fault | Scenario items keyed to `SP-033` |
| 6 | Set customer expectation on time, cost and process using approved wording, without over-promising | Role play against rubric |
| 7 | Take payment and issue the correct document at the counter | Sandbox transaction |
| 8 | Recognise a hard rule that blocks the transaction and respond correctly rather than working around it | Scenario item |
| 9 | Recognise a hazardous device at the counter and isolate it before it enters the workflow | **Safety item — 100% required** |
| 10 | Escalate to the branch manager with the right evidence at the right threshold | Scenario item |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to `P03` intake workspace · OJT sign-off · counter shift | Layer 1 universal core | On release (`TR-024`); full refresh 24 months |

---

## 3. Module Outline

### 3.1 The four-hour core

| # | Module | Duration | Method | Materials |
|---:|---|---|---|---|
| 1 | **Why the first three minutes decide everything** | 15 min | Facilitated, with real downstream failure examples | Cases from intake defects |
| 2 | The counter workspace — orientation and keyboard-first working | 20 min | Guided walkthrough | `UI-023` copy pack, sandbox |
| 3 | **Device identification** — search, model resolution, new-model registration | 30 min | Walkthrough + practice | `MD-021`, sandbox devices |
| 4 | **Condition capture** — what to photograph, what to write, why it is evidence | 30 min | Practice with disputed-case examples | `DT-004`, camera, sample units |
| 5 | Coverage check — warranty, contract, protection plan | 25 min | Walkthrough + practice | `MD-031`, sandbox |
| 6 | **Intake triage** — symptom to route | 30 min | Scenario practice | `SP-033` intake trees |
| 7 | **Expectation setting** — the conversation, in Bengali | 30 min | Role play in pairs | Approved wording, `SP-007` |
| 8 | Payment, documents and handover | 25 min | Sandbox transaction | `DT-002`, `DT-004` |
| 9 | **Safety at the counter** — hazardous device recognition | 20 min | Demonstration + drill | `KB-013` §4, isolation container |
| 10 | Blocks, exceptions and escalation | 20 min | Scenario practice | `MD-026`, `SP-005` |
| 11 | **Timed end-to-end intake** ×3 | 25 min | Assessed practice | Sandbox, stopwatch |
| | **Total** | **4 h 30 min** including breaks | | |

**`PK-01`: the four-hour target is measured on modules 2–11 excluding breaks.** Module 1 is
motivation and is not part of the competence claim; that distinction is stated openly rather than
used to make the number work.

### 3.2 What makes four hours possible

The target is achievable only because the workload is shared with product design (`LS-06`):

| Carrier | Contribution |
|---|---|
| `UI-023` workspace copy | Field labels and inline help that teach at the point of entry |
| `UI-004` error messages | Every block states what is wrong and what to do (`BR-STD-04`) |
| `TR-022` job aids | The twenty most frequent tasks, one page each, at the counter |
| `SP-033` intake trees | Triage decisions made by the tree, not by recall |
| Keyboard-first design | Speed comes from the interface, not from drilling |

**If any of these is absent at W1, the four-hour target is not achievable and this pack cannot
recover it.** Recorded as `O-01`.

### 3.3 Deferred to week two (not in the four hours)

| Topic | When | Why deferred |
|---|---|---|
| Bulk and corporate intake | Week 2 OJT | Low frequency for a new agent |
| Pick-and-drop booking | Week 2 | `P09` dependency, W3 |
| Loyalty and campaign handling | Week 3 | Not present at W1 |
| Complaint intake beyond acknowledgement | Week 2, with `SP-028` | Requires judgement built on the core first |
| Refurbished sales and trade-in | Week 4 | Separate flow |

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions | Timing |
|---|---|---|---|
| 1 | One bad device identification breaks warranty matching, parts planning and analytics for that job forever | *"We can fix the record later."* Later never comes, and the claim is already rejected | 15 |
| 3 | Free-text device entry is prohibited by `BRU-SRM-01`; registering a new model is a normal action, not an exception | *"If I can't find it I'll type it in the notes."* | 30 |
| 4 | **Condition capture is the company's defence in a damage dispute** | *"The customer saw the scratch, so it's fine."* Verbal agreement is not evidence | 30 |
| 5 | Checking coverage before quoting prevents the most common customer conflict at the counter | *"I'll check later and call them."* | 25 |
| 6 | The tree exists so that five agents code one symptom the same way — using it is the point, even when you already know the answer | *"I've seen this a hundred times."* — `SP-033` decision point | 30 |
| 7 | An expectation set honestly and low is a satisfied customer; set optimistically and high is a complaint | *"Tell them tomorrow, it keeps them happy."* | 30 |
| 9 | A swollen battery at the counter is isolated **before** it enters the bin, not after | *"I'll mention it on the job sheet."* | 20 |
| 10 | A block is the system doing its job. Working around it is the error the block existed to prevent | *"The system won't let me, so I'll book it as something else."* | 20 |

---

## 5. Participant Workbook Contents

| Section | Purpose |
|---|---|
| The three-minute intake, step by step | The spine of the job, matching `SP-007` |
| Device identification decision aid | Search strategies; when to register a new model |
| Condition capture standard — the six photographs | Removes judgement from evidence |
| Coverage check flow | Warranty, contract, plan |
| Intake triage trees for the top device families | `SP-033` extract |
| **Expectation-setting phrases, Bengali and English** | Approved wording, not improvisation |
| Reason codes an agent uses | `MD-026` subset |
| Hazard recognition card | `KB-013` extract |
| Escalation thresholds | Who, when, with what |
| **My access scope** | What this role may and may not do (`QB-21`) |

---

## 6. Exercises

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Identify eight devices, two of them unregistered | `P03` sandbox | Device set incl. ambiguous legacy strings | 8/8 resolved or correctly registered |
| 2 | Condition capture on a damaged unit | Sandbox + camera | Pre-damaged training unit | All six standard photographs; written description matches |
| 3 | Coverage check across four scenarios | Sandbox | In-warranty, expired, contract, none | Correct outcome and correct customer message |
| 4 | Triage six presented symptoms | Sandbox + trees | Symptom set incl. one not-a-fault | Correct route; **not-a-fault closed without raising an order** |
| 5 | **Expectation-setting role play** | Pairs | Three customer types incl. one impatient | Rubric: honest, specific, no over-promise |
| 6 | Counter payment and document issue | Sandbox | Cash and mobile-wallet cases | Correct document, correct reconciliation |
| 7 | **Hazardous device drill** | Physical | Swollen-cell training unit *(inert)* | Isolated before any other action |
| 8 | Hard-rule block response | Sandbox | Seeded block — unapproved repair, parts issue | Escalates or corrects; **no workaround attempted** |
| 9 | **Timed end-to-end intake ×3** | Sandbox | Three full walk-in scenarios | **Under 3 minutes on the third, all data correct** |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| `TR-006` cell 1 written form, 30 items | 40% | 80% overall, **100% on critical** | 3 | 24 months |
| Sandbox transactions (exercises 1, 3, 6, 8) | 30% | All passed | 3 | 24 months |
| **Timed intake (exercise 9)** | 20% | **Under 3 minutes with complete, correct data** | 3 | 24 months |
| Expectation-setting role play (exercise 5) | 10% | Rubric pass | 3 | 24 months |
| **OJT sign-off — 10 live intakes observed** | Gate | Supervisor sign-off (`LS-03`) | — | — |

> Conforms to [`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md).
> **Safety item (objective 9) is critical — 100% required** (`AS-04`).

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| The three-minute intake | One page, laminated | Counter · `TR-022` |
| Six-photograph condition standard | One page with examples | Counter · `TR-022` |
| Intake triage quick trees | Two pages | Counter · `TR-022` |
| Expectation-setting phrases | One page, bilingual | Counter · `TR-022` |
| Hazardous device — stop and isolate | One page | Counter · `TR-022`, sourced from `KB-013` |
| Reason codes for intake | One page | `TR-022` |
| Escalation thresholds | One page | `TR-022` |

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| Trainer | L&D trainer or a certified branch champion (`TR-023`) |
| Domain support | An experienced agent or branch manager co-delivers modules 3–7 |
| Bengali | **Delivery is in Bengali**; the trainer must be fluent, not translated-through |
| Sandbox | `P03` sandbox with `TS-002` data, one seat per learner |
| Physical | Training devices including one inert swollen-cell unit, camera, isolation container |
| Cohort size | **Maximum 12** — module 5 and 9 are individually observed |
| HSE | Module 9 content and the drill approved by HSE |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Perceived readiness to take the counter | Diagnostic only (`LS-02`) |
| **Learning** | Assessment pass rate; timed-intake pass | > 85% first attempt; near-100% triggers review (`AS-06`) |
| **Behaviour** | Intake completeness and accuracy of newly trained agents at 30 days — device resolution rate, condition-capture completeness, triage code agreement with bench | Not materially worse than population |
| **Result** | **`KPI-010` walk-in intake time — about 10 minutes today, under 4 at W7, under 3 at W9** · contribution to `KPI-004` first-time fix through better intake data | Per `06-02` |

**Required Drivers** (`LS-04`): reinforce — counter job aids (`TR-022`) · encourage — branch
champion present for the first two weeks (`TR-023`) · monitor — supervisor observation at day 5 and
day 30 against the behaviour measures · reward — production access and competence record.

---

## 11. Related Documents

| Document | Relationship |
|---|---|
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | The procedure this pack teaches (`LS-15`) |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Intake triage trees |
| `UI-023` Workspace — Service Intake Copy · `UI-013` `P03` copy pack | The interface that carries part of the teaching load |
| `DT-002` job sheet · `DT-004` diagnostic and condition report | Documents produced at intake |
| [`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) | Cell 1 assessment |
| [`TR-022_Job_Aid_and_Quick_Reference_Library.md`](TR-022_Job_Aid_and_Quick_Reference_Library.md) | The seven job aids |
| [`TR-023_Train_the_Trainer_and_Super_User_Kit.md`](TR-023_Train_the_Trainer_and_Super_User_Kit.md) | Champions who deliver and sustain it |
| `KB-013` ESD, Chemical and Battery Safety Data | Module 9 source |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The four-hour target depends on `UI-023`, `UI-004`, `TR-022` and `SP-033` all being present at W1.** `UI-023` and `UI-004` are written; **`TR-022` is this category and `SP-033`'s 36 trees are unauthored** (`SP-033` O-01). If the trees are absent, module 6 teaches a method with no content | Operations Director with Technical Director | **W1** |
| **O-02** | `TS-002` sandbox data does not exist (Category 13 unstarted). **Nine of nine exercises depend on it** | Test Lead with L&D | **W1 — blocking** |
| **O-03** | An inert swollen-cell training unit must be sourced and a safe presentation procedure written. `TR-005` `O-06` records the same gap for practical assessment | HSE Lead with Technical Director | **W1 — before module 9 runs** |
| **O-04** | Delivering 150–250 agents at cohorts of 12 is **13–21 cohorts**. At one cohort per day per trainer that is 3–4 trainer-weeks per pass, repeated on release. **No trainer establishment exists** (`TR-001` `O-04`) | HR Director with L&D | **W1** |
| **O-05** | `TR-006` cell 1 items do not exist and `TR-006` is scheduled W2 while this pack is W1 — **agents would be trained and given access before the assessment gate exists** (`TR-006` `O-01`) | L&D | **W1** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable, timed and assessable (`DS-02`); no banned verbs
- [x] Level 4 measure named first (`KPI-010`) and designed backwards from (`LS-01`, `DS-01`)
- [x] The four-hour target defined precisely, with what it excludes stated openly (`PK-01`, §3.3)
- [x] The dependency of the target on UI copy, job aids and triage trees made explicit (`LS-06`)
- [x] Safety module included with a critical assessment item
- [x] OJT sign-off gate present (`LS-03`)
- [x] All four Required Drivers named with owners (`LS-04`)
- [x] Bengali delivery, not translated delivery (`DS-17`)
- [x] All internal links resolve
- [x] `BRU-SRM-01`/`-02`/`-07` cited to `05-05`; `KPI-010` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-02` sandbox data — outstanding; blocks every exercise**
- [ ] **`O-05` assessment gate available before access is granted — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and HR Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
