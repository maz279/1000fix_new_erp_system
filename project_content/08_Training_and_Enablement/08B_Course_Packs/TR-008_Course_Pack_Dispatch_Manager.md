---
id: TR-008
title: Course Pack — Dispatch Manager
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Field Service Operations
reviewers: [Operations Director, Quality Manager, Technical Director, Content Design Lead, Localisation Lead]
approver: Operations Director with HR Director
content_class: D
purpose: >
  Trains the 3–8 dispatchers whose decisions determine SLA attainment across the whole network.
  A small population with disproportionate impact: one dispatcher allocating a morning queue badly
  costs more SLA than fifty agents working slowly, and the levers — skill match, certification,
  zone, capacity, priority — are invisible unless they are taught deliberately.
traces_to: [M02, M03, M05, M22, M26, M55, P03, P02, P09, MD-005, MD-010, MD-011, MD-026, MD-028, MD-041, TR-001, TR-002, TR-003, TR-004, TR-006, TR-022, UI-024, SP-005, SP-008, SP-033]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-008_Course_Pack_Dispatch_Manager_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M02_Field_Service_and_Dispatch_Management.md — dispatch, skill-based assignment, zone and capacity, automatic assignment
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09 assignment blocked without current brand certification; BRU-SRM-14 L3 board-level work restricted to an equipped workshop and a certified specialist; BRU-HRM-01 expiry blocks assignment
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-013 automatic assignment rate 0% to 20% then 70%; KPI-004 first-time fix 70% to 88%
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P03 dispatch console; dispatching a full morning queue in under 10 minutes
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Dispatch Manager

| Item | Value |
|---|---|
| Audience role(s) | `R07` Dispatch Manager |
| Headcount | **3–8** |
| Duration | **8 hours** over two days, plus 5 days supervised OJT |
| Delivery mode | Classroom with live sandbox; small cohort, high discussion |
| Language | Bengali primary, English parallel |
| Prerequisites | Layer 1 universal core · familiarity with `SP-008` field visit |
| Certification outcome | Functional competence record (`TR-006` cell 2) — **gates production access** |
| Wave | W1 |

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | Dispatch a full morning queue in **under 10 minutes** with correct skill, zone and priority allocation | Timed sandbox |
| 2 | Read SLA risk across the board and act on the job that is about to breach, not the job that is loudest | Scenario + timed sandbox |
| 3 | Match skill and **certification** to job requirement, and recognise when a match is blocked | Items keyed to `BRU-SRM-09`, `BRU-SRM-14`, `BRU-HRM-01` |
| 4 | Allocate against real capacity — travel time, zone, existing load, shift and calendar | Sandbox |
| 5 | Handle the exception day: sickness, vehicle failure, weather, a hazardous device, a VIP escalation | Scenario set |
| 6 | Decide when to route remote, on-site, pick-and-drop or workshop, and explain the cost of each | Scenario items |
| 7 | Work **with** automatic assignment rather than around it, and know when to override and how to log it | Items + sandbox |
| 8 | Communicate a schedule change to customer and technician without creating a second problem | Role play |
| 9 | Recognise when the queue cannot be met and escalate early rather than silently under-delivering | Scenario |
| 10 | Read the dispatch board's own signals — re-routing rate, override rate, travel-time drift | Items |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Production access to the `P03` dispatch console · OJT sign-off | Layer 1 core | On release (`TR-024`); full refresh 24 months. **Re-run whenever `M26` automatic assignment changes** |

---

## 3. Module Outline

| # | Module | Duration | Method | Materials |
|---:|---|---|---|---|
| 1 | What dispatch actually optimises — and the four things it trades off | 30 min | Facilitated | Real queue data |
| 2 | The dispatch console — board, filters, load view, SLA risk | 45 min | Guided walkthrough | `UI-024`, sandbox |
| 3 | **Zones, travel time and the geography of the promise** | 45 min | Practice | `MD-005`, map data |
| 4 | **Skill and certification matching** — and the blocks that are not negotiable | 60 min | Walkthrough + items | `MD-010`, `MD-011`, `BRU-SRM-09`/`-14` |
| 5 | Capacity — shift, calendar, existing load, realistic day length | 45 min | Practice | `MD-042`, `MD-041`, `M55` |
| 6 | **Priority, severity and SLA** — what the customer was actually promised | 60 min | Practice | `MD-028`, `LG-015` |
| 7 | Delivery-mode decision — remote, on-site, pick-and-drop, workshop | 45 min | Scenario | `MD-020`, `SP-033` |
| 8 | **Working with automatic assignment** — trust, override, and logging | 45 min | Practice | `M26`, `BRU-AIM-01`, `MD-026` |
| 9 | **The exception day** — six disruptions in one shift | 60 min | Live simulation | Scenario pack |
| 10 | Communicating change — customer and technician | 30 min | Role play | Approved wording, `SP-034` extract |
| 11 | Reading your own board — the four warning signals | 30 min | Facilitated | Reporting views |
| 12 | **Timed queue dispatch ×2** | 45 min | Assessed practice | Sandbox, full morning queue |
| | **Total** | **~8 hours** over two days | | |

---

## 4. Facilitator Guide

| Module | Talking points | Common misconceptions | Timing |
|---|---|---|---|
| 1 | Dispatch trades SLA against travel cost against skill fit against technician fairness. **You cannot maximise all four** | *"There's one right answer."* There is a defensible answer, and it changes by day | 30 |
| 3 | Travel time is the hidden cost centre; two jobs in one zone beats two jobs across the city almost always | *"The customer called first so they go first."* | 45 |
| 4 | `BRU-SRM-09` is a **hard block** and cannot be overridden (`AS-12`). A certified technician who is unavailable means reschedule, not substitute | *"I'll assign them anyway and sort the paperwork later."* — this creates a rejected claim | 60 |
| 6 | Priority is a contractual promise with a financial consequence, not an urgency feeling | *"Everything is priority 1 today."* | 60 |
| 8 | Automatic assignment gets better when you tell it why you overrode it; overriding silently teaches it nothing | *"The system doesn't understand our area."* Sometimes true — log it so it can | 45 |
| 9 | The exception day is the job. A dispatcher who is only good on a normal day is not yet competent | | 60 |
| 11 | A rising re-routing rate means your triage is wrong upstream, not that technicians are failing | *"They keep sending me the wrong jobs."* — that is a `SP-033` signal | 30 |

---

## 5. Participant Workbook Contents

| Section | Purpose |
|---|---|
| The four trade-offs, with worked examples | The mental model |
| Zone map and travel-time bands | `MD-005` extract |
| **Skill and certification matrix — what blocks what** | `MD-010`, `MD-011`, and the three hard rules |
| Priority and SLA table | `MD-028` extract |
| Delivery-mode decision aid | Cost and promise per mode |
| Override reason codes | `MD-026` subset |
| Exception-day playbook | Six disruptions, six responses |
| Communication phrases, Bengali and English | Change, delay, reschedule |
| Escalation thresholds | `SP-005` |
| **My access scope** | `QB-21` |

---

## 6. Exercises

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | Allocate 20 jobs across 8 technicians and 4 zones | `P03` sandbox | Full morning queue | All allocated; zone clustering evident; no certification breach |
| 2 | **Certification-blocked assignment** | Sandbox | Brand job, uncertified technician | Recognises the block; reschedules or routes, **does not override** |
| 3 | L3 job with no specialist on shift | Sandbox | Seeded board-level fault | Routes to an equipped workshop (`BRU-SRM-14`) |
| 4 | SLA-risk board triage | Sandbox | Queue with 3 jobs near breach | Acts on breach risk first; explains the choice |
| 5 | **The exception day simulation** | Sandbox, live-run | Sickness, vehicle failure, rain, hazardous device, VIP escalation, part shortage | Queue recovered; escalation raised where the day cannot be met |
| 6 | Override with logging | Sandbox | Automatic assignment the dispatcher disagrees with | Override recorded with a valid `MD-026` reason |
| 7 | Communicate two schedule changes | Role play | Customer + technician | Rubric: clear, honest, no second problem created |
| 8 | **Timed queue dispatch ×2** | Sandbox | Two full morning queues | **Under 10 minutes on the second, allocation defensible** |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| `TR-006` cell 2 written form, 30 items | 30% | 80% overall, **100% on certification-block items** | 3 | 24 months |
| Sandbox exercises 1–4, 6 | 30% | All passed | 3 | 24 months |
| **Exception-day simulation (exercise 5)** | 25% | Queue recovered; escalation appropriate | 3 | 24 months |
| Timed queue dispatch (exercise 8) | 15% | **Under 10 minutes, allocation defensible** | 3 | 24 months |
| **OJT sign-off — 5 live shifts observed** | Gate | Operations Director or delegate | — | — |

> Conforms to [`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md). Certification-block items are critical
> (`AS-05`) because a breach produces a rejected claim (`KPI-063` target zero).

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| The four trade-offs | One page | Console · `TR-022` |
| Certification and skill block matrix | One page | Console · `TR-022` |
| Priority and SLA quick table | One page | Console · `TR-022` |
| Exception-day playbook | Two pages | Console · `TR-022` |
| Override reason codes | One page | `TR-022` |
| Escalation thresholds | One page | `TR-022` |

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| Trainer | L&D trainer **with an experienced dispatcher or Operations Director co-delivering** — modules 1, 9 and 11 need lived experience |
| Sandbox | `P03` dispatch console with a realistic queue and a realistic technician roster |
| Cohort size | **Maximum 6** — the population is 3–8, so this is one or two cohorts total |
| Simulation | Module 9 needs a facilitator injecting disruptions live |
| Bengali | Delivery in Bengali; console labels in both languages |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Confidence handling an exception day | Diagnostic only (`LS-02`) |
| **Learning** | Assessment and timed-dispatch pass | > 85% first attempt |
| **Behaviour** | Re-routing rate · override rate with valid reasons · zone clustering · certification breaches | Re-routing falling; **certification breaches zero**; overrides logged 100% |
| **Result** | **`KPI-013` automatic assignment rate 0% → 20% (W7) → 70% (W9)** · contribution to `KPI-004` first-time fix and to SLA attainment | Per `06-02` |

**Required Drivers** (`LS-04`): reinforce — console job aids · encourage — Operations Director
reviews the board weekly with the dispatcher for the first month · monitor — the four behaviour
signals in module 11 · reward — competence record; dispatch quality visible in `P06`.

> **A note on the Level 4 measure.** `KPI-013` is an *automation* target, and a dispatcher might
> reasonably read it as measuring their own replacement. It is not: automatic assignment rises only
> when coding, skills data and zone data are good enough to trust, and the dispatcher is the person
> who makes them good enough. That framing belongs in module 8 and is stated here so a trainer does
> not have to invent it.

---

## 11. Related Documents

| Document | Relationship |
|---|---|
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) | What the dispatcher is scheduling |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Upstream triage; re-routing signal |
| [`../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md`](../../06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-005_Escalation_Matrix.md) | Escalation thresholds |
| `UI-024` Workspace — Dispatch Console Copy | The interface |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md) · [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | Zones and SLA |
| [`../08A_Framework/TR-006_Question_Bank_Functional_Roles.md`](../08A_Framework/TR-006_Question_Bank_Functional_Roles.md) | Cell 2 assessment |
| [`TR-022_Job_Aid_and_Quick_Reference_Library.md`](TR-022_Job_Aid_and_Quick_Reference_Library.md) | The six job aids |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | `TS-002` sandbox with a realistic queue and roster does not exist. **Exercise 5, the most important one, cannot be run without a live-injectable simulation environment** | Test Lead with L&D | **W1 — blocking** |
| **O-02** | `MD-005` dispatch zones and `MD-011` certifications are unpopulated. Modules 3 and 4 teach against empty registers | MDM with Operations | **W1** |
| **O-03** | `TR-006` cell 2 items do not exist; this pack is W1 and `TR-006` is W2 (`TR-006` `O-01`) | L&D | **W1** |
| **O-04** | Whether `M26` automatic assignment is present at W1 is unconfirmed. Module 8 teaches working with it; if it lands later the module is theoretical and must be re-run (`TR-024`) | CTO with Operations Director | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Objectives observable and timed (`DS-02`)
- [x] Level 4 measure named (`KPI-013`) and its motivational risk addressed openly
- [x] The non-overridable certification block taught as an absolute (`AS-12`)
- [x] Exception-day simulation made a weighted assessment component rather than an optional extra
- [x] OJT sign-off gate present (`LS-03`)
- [x] All four Required Drivers named with owners (`LS-04`)
- [x] All internal links resolve
- [x] `BRU-SRM-09`/`-14`, `BRU-HRM-01`, `BRU-AIM-01` cited to `05-05`; `KPI-004`/`-013` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` simulation environment — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Operations Director and HR Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
