---
id: TR-009
title: Course Pack — Field Technician
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Technical Services and Specialist Technicians (R12)
reviewers: [Technical Director, Operations Director, Quality Manager, HSE Lead, Localisation Lead, Content Design Lead, HR Director]
approver: Technical Director with Operations Director and HSE Lead
content_class: C
purpose: >
  Trains 200–400 field technicians to competence on the technician application and the field service
  process, delivered in Bengali on the device they actually carry, to a workforce with mixed
  literacy and high turnover. This is the only P0 file in the category: P02 targets daily active
  usage above 95%, and a technician who cannot use the application does not merely underperform —
  they revert to paper, and every downstream measure the programme depends on stops existing.
traces_to: [M02, M01, M22, M31, M55, M59, M61, P02, MD-010, MD-011, MD-021, MD-024, MD-025, MD-026, TR-001, TR-002, TR-003, TR-004, TR-005, TR-022, UI-012, UI-009, SP-008, SP-016, SP-030, SP-033, KB-013, KB-016, DT-007]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: TR-009_Course_Pack_Field_Technician_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P02 non-negotiable requirements include complete Bengali UI including error messages, full offline operation for 24 hours, and offline access to repair manuals and past repair notes; daily active usage target above 95%
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-024 digital learning with mobile access for technicians; FR-LMS-025 mobile learning presented within P02, usable in the field; FR-LMS-027 structured on-the-job training with a supervising technician and sign-off
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09 certification gate; BRU-SRM-11 parts cannot be issued against an unapproved paid repair; BRU-SRM-12 beyond economic repair requires photographic evidence and a second technician; BRU-SRM-14 L3 restriction
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-004 first-time fix 70% to 82% then 88%
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md — field technician training: 200–400 technicians with mixed English literacy; translated training teaches translated concepts, native training teaches the job
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Field Technician

| Item | Value |
|---|---|
| Audience role(s) | `R10` Senior Technician · `R11` Junior Technician · `R12` Specialist Technician |
| Headcount | **200–400** — with continuous turnover, so intake is continuous |
| Duration | **6 hours core**, delivered as ~40 microlearning items of under 3 minutes, plus 10 days supervised OJT |
| Delivery mode | **On-device inside `P02`** (`M22` FR-LMS-025), self-paced, offline-capable · plus branch practical sessions |
| Language | **Bengali, authored in Bengali** (`LS-07`, `DS-17`) |
| Prerequisites | Layer 1 universal core — **including the statutory safety module** (`TR-002` §4.2) |
| Certification outcome | Technical certification per device family and level (`TR-005`), registered in `MD-011` |
| Wave | W2 |

> **This is the only `P0` file in Category 08.** It is `P0` because `P02`'s daily active usage
> target above 95% is not an adoption metric — it is the condition on which job data, parts
> consumption, first-time-fix measurement, knowledge capture and technician safety records all
> depend. A technician who reverts to paper is invisible to the entire system.

---

## 1. Learning Objectives

| # | On completion the learner can… | Assessed by |
|---|---|---|
| 1 | **Identify a hazard and isolate it before any diagnostic action**, on every job, every time | Practical drill — **100% required** (`AS-04`) |
| 2 | Run a full job on `P02` — accept, travel, arrive, diagnose, estimate, repair, evidence, close — without paper | Sandbox job + OJT |
| 3 | Work a full day **offline** and understand exactly what has and has not synced | Offline simulation |
| 4 | Diagnose to a coded fault using the guided tree, and record an honest `FLT-UNK` when it is honest | Practical + items |
| 5 | Capture evidence to the standard a warranty claim and a customer dispute both require | Practical |
| 6 | Request, receive, consume and return parts correctly, including van stock | Sandbox + OJT |
| 7 | Build and present an estimate, and obtain approval at the right threshold | Sandbox + role play |
| 8 | Record resolution codes and time accurately, and understand what they are used for | Sandbox + items |
| 9 | Recognise the boundary of their level and escalate rather than attempt | **Practical — the `TR-005` exercise 5 pattern** |
| 10 | Handle customer data and device identity lawfully, including the IMEI prohibition | Items — **critical on `DF-MB`** |
| 11 | Capture knowledge from a difficult repair in under three minutes | Practical (`M61` FR-KMS-024) |
| 12 | Conduct themselves in a customer's home or business to the standard `SP-008` sets | Role play + OJT |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| `TR-005` technician certification · assignment eligibility · brand specialisation | Layer 1 core **including safety** · basic device competence on hire | On release (`TR-024`); technical refresh 24 months; **safety annually** (`LS-10`) |

---

## 3. Module Outline

### 3.1 Design constraints that shape this pack

**`PK-02`: this pack is not a classroom course, and attempting to deliver it as one will fail.**

| Constraint | Design response |
|---|---|
| 200–400 people across 51+ branches | **Self-paced on-device**, not cohort-based |
| **Continuous turnover** | Always available, always current — a new technician starts on day one, not at the next cohort |
| Mixed literacy | **Video and demonstration first, text second**; audio narration on every item |
| Bengali is the working language | Authored in Bengali (`DS-17`), not translated |
| The device is a mid-range Android | Items under 3 minutes, offline-capable, low data |
| Learning happens between jobs | **No item longer than 3 minutes** (`DS-07`) |
| Practical competence cannot be taught on a phone | Branch practical sessions and OJT carry it (`AS-03`) |

### 3.2 The on-device core — ~40 microlearning items, ~6 hours

| Block | Items | Duration | Focus |
|---|---:|---|---|
| **A — Safety first** | 8 | 55 min | Hazard recognition, isolation, battery, refrigerant class, electrical, height, incident reporting |
| **B — The app and the job** | 7 | 45 min | Accept, navigate, job card, status, close |
| **C — Offline working** | 4 | 25 min | What syncs, what does not, conflict, the sync indicator |
| **D — Diagnose and code** | 6 | 40 min | Guided tree, symptom to fault, `FLT-UNK`, resolution coding |
| **E — Parts** | 5 | 35 min | Request, van stock, consumption, return, prohibited substitution |
| **F — Estimate and approval** | 4 | 30 min | Build, present, thresholds, decline |
| **G — Evidence** | 3 | 25 min | Photographs, verification, service report |
| **H — Customer and conduct** | 4 | 30 min | Arrival, explanation, handover, difficult situations |
| **I — Knowledge capture** | 2 | 15 min | Three-minute capture, why it matters |
| **J — Identity and data** | 3 | 20 min | Customer data, IMEI, device identity |
| | **~46 items** | **~5 h 40 min** | |

### 3.3 Branch practical sessions — 2 × half-day

| Session | Content | Assessor |
|---|---|---|
| **P1 — Safety and handling** | Hazard drill; battery isolation; ESD station; electrical proving; equipment pre-use check | HSE-approved assessor |
| **P2 — End-to-end job** | Seeded fault, diagnose, repair, verify, code, evidence, close on `P02` | `R09` or `R12` qualified above the level |

### 3.4 Supervised OJT — 10 days

`M22` FR-LMS-027. **`PK-03`: no technician works unsupervised before OJT sign-off** (`LS-03`).

| Days | Focus | Sign-off |
|---|---|---|
| 1–3 | Shadowing; observing the process end to end | Supervising technician |
| 4–7 | Performing with the supervisor present | Task list, 15 tasks observed |
| 8–10 | Performing independently with the supervisor available | Final sign-off, `R09` or `R10` |

---

## 4. Facilitator Guide

On-device items are self-paced; this section guides the **practical sessions and the OJT
supervisor**.

| Session / block | Talking points | Common misconceptions | Timing |
|---|---|---|---|
| A / P1 | A swollen cell is not a fault to diagnose — it is a hazard to isolate. **The order is always isolate, then think** | *"I'll finish the diagnosis first and deal with the battery after."* | 55 |
| A / P1 | Refrigerant class is read from the nameplate on **every** job. The system you worked on last week is not this system | *"It's the same model, it'll be R-22."* — `KB-013` §5 | |
| C | The sync indicator is the difference between work recorded and work lost. **Check it before you leave site** | *"I entered it, so it's saved."* | 25 |
| D | `FLT-UNK` is a legitimate outcome. A guessed code is worse than an honest unknown because it corrupts everyone's data | *"I have to put something."* — `SP-033` `DT-02` | 40 |
| E | Parts cannot be issued against an unapproved paid repair. This is a hard block, not a delay | *"I'll fit it and get approval after."* — `BRU-SRM-11` | 35 |
| F | An estimate above BDT 5,000 needs documented customer approval **before** work begins | *"They said yes on the phone."* — `BRU-SRM-07` | 30 |
| G | The photographs are not for us. They are for the claim, the dispute and the next technician | *"It's obvious what I did."* | 25 |
| I | Three minutes at the end of a hard repair saves the next person an hour — and it is **your** name on it | *"Someone else will write it up."* Nobody will | 15 |
| P2 / OJT | The boundary of your level is not a limitation, it is a protection. `BRU-SRM-14` exists because board-level work needs equipment you do not have in a van | *"I can probably manage it."* | |

---

## 5. Participant Workbook Contents

**Delivered on-device, not as a printed workbook** — with a printed fallback for branches during an
outage (`SP-032` pattern).

| Section | Purpose |
|---|---|
| Safety cards — hazard, isolate, report | Mirrors `KB-016` layer 1; **the same content, one source** (`CP-01`) |
| The job on `P02`, step by step | Visual, minimal text |
| Offline: what syncs and what does not | The single most common support call |
| Diagnostic trees for my families | `SP-033` extract, offline |
| Coding quick reference | `MD-024`, `MD-025` |
| Parts: request, van stock, return, prohibited substitutions | `KB-009` extract |
| Estimate thresholds | `BRU-SRM-07`/`-08` |
| Evidence standard — what to photograph | `DT-007` |
| **Escalation: when I must stop** | `SP-005`, `BRU-SRM-12`/`-14` |
| Customer conduct | `SP-008` |
| **My level and what it permits** | `QB-21` equivalent for technicians |

---

## 6. Exercises

| # | Exercise | System / sandbox | Test data (`TS-002`) | Success criterion |
|---|---|---|---|---|
| 1 | **Hazard drill** — five presented devices, two hazardous | Physical, session P1 | Inert swollen cell, liquid-damaged unit | Both identified and isolated **before** any other action |
| 2 | Electrical isolation and proving | Physical, P1 | Training rig | Correct sequence; proved dead before touching |
| 3 | ESD station shift check | Physical, P1 | Station + tester | Strap and mat tested; failed strap replaced not adjusted |
| 4 | Accept and run a job end to end | `P02` sandbox | Seeded job | Completed, coded, evidenced |
| 5 | **Full day offline, then sync** | `P02` sandbox, airplane mode | 4 seeded jobs | All work captured; **technician can state what had not synced before reconnecting** |
| 6 | Diagnose a seeded fault | Physical + `P02`, P2 | Family-appropriate fault unit | Correct `FLT-` code or honest `FLT-UNK` with a route |
| 7 | **Out-of-level fault** | P2 | Board-level fault presented to L1/L2 | **Escalates; does not attempt** (`BRU-SRM-14`) |
| 8 | Parts request under a blocked condition | Sandbox | Unapproved paid repair | Recognises the block; **no workaround** (`BRU-SRM-11`) |
| 9 | Build and present an estimate over threshold | Sandbox + role play | BDT 8,000 repair | Approval obtained and documented before work (`BRU-SRM-07`) |
| 10 | Evidence capture | P2 | Completed repair | Photographs meet `DT-007` standard |
| 11 | **Three-minute knowledge capture** | `P02` sandbox | The exercise-6 repair | Captured in under 3 minutes, in Bengali, with photographs (`M61` FR-KMS-024) |
| 12 | Customer conduct role play | Pairs | Arrival, explanation, an unhappy customer | Rubric pass |

---

## 7. Assessment

| Item | Weight | Pass mark | Attempts | Re-certification interval |
|---|---:|---:|---:|---|
| On-device knowledge checks (per block) | 15% | 80% per block | Unlimited within the block | On release |
| **`TR-005` written form, 40 items** | 25% | 80% overall, **100% on critical** | 3 (2 for safety) | 24 months |
| **Practical P1 — safety (exercises 1–3)** | 20% | **All three passed, no partial credit** | 3 | **Annual** (`LS-10`) |
| Practical P2 — end-to-end (exercises 6, 7, 10) | 25% | All passed; **exercise 7 is non-negotiable** | 3 | 24 months |
| Offline and app exercises (4, 5, 8, 9, 11) | 15% | All passed | 3 | On release |
| **OJT sign-off — 15 tasks over 10 days** | Gate | Supervising technician + `R09`/`R10` (`FR-LMS-027`) | — | — |

> Conforms to [`../08A_Framework/TR-004_Assessment_and_Certification_Policy.md`](../08A_Framework/TR-004_Assessment_and_Certification_Policy.md).
> **Safety practical is annual and carries no grace period** (`AS-10`, `LS-10`).

---

## 8. Job Aids Produced

| Job aid | Format | Where it lives |
|---|---|---|
| Hazard, isolate, report | One screen | **`KB-016` layer 1 — authored there, referenced here** (`CP-01`) |
| Offline: what syncs | One screen | `P02` · `TR-022` |
| Coding quick reference | One screen | `KB-016` layer 2 |
| Estimate thresholds | One screen | `TR-022` |
| Evidence standard | One screen | `TR-022` |
| **My level and what it permits** | One screen | `KB-016` layer 2 |
| Three-minute capture prompt | In-app | `P02` |

**`PK-04`: technician job aids that are technical or safety decisions live in `KB-016`; those that
are system tasks live in `TR-022`.** The boundary is `TR-002` §6.3 (`CU-15`), which resolves
`AUDIT-008` KB-09.

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| On-device content authors | **Bengali-native technical authors** (`DS-17`) — capability gap, `TR-001` `O-05` |
| P1 safety assessor | HSE-approved; qualified to run the hazard drill safely |
| P2 practical assessor | `R09` or `R12` **qualified above the level being assessed** (`AS-16`) |
| OJT supervisors | `R10`/`R12` with capacity released for supervision — **10 days per new technician** |
| Video production | Demonstration video for mixed literacy; `MM-001` specs |
| Physical | Seeded fault units per family; inert hazard units; ESD station; isolation container |
| Branch capability | **Every branch running P1/P2 needs an assessor and a rig** — 51+ sites |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Whether technicians find on-device learning usable between jobs | Diagnostic only (`LS-02`) |
| **Learning** | `TR-005` pass rate; practical pass rate | > 80% first attempt on written; **safety practical 100% eventually, no exceptions** |
| **Behaviour** | **`P02` daily active usage** · paper reversion incidents · coding completeness · evidence completeness · knowledge captures accepted | **Usage > 95%**; paper reversion zero |
| **Result** | **`KPI-004` first-time fix 70% → 82% (W7) → 88% (W9)** · safety incident rate · rework rate | Per `06-02` |

**Required Drivers** (`LS-04`): reinforce — `KB-016` offline cards and in-app prompts · encourage —
`R10`/`R12` mentors and branch champions (`TR-023`) · monitor — usage telemetry, coding
completeness, supervisor observation at day 10 and day 30 · reward — certification unlocking brand
work and level progression.

> **The Behaviour measure is the one that matters here.** `P02` daily active usage above 95% is the
> proxy for everything else. If usage falls, the cause is almost never that technicians forgot the
> training — it is that the app failed them offline, or the Bengali did not read naturally, or a
> job aid was missing. **A falling usage rate is a signal to investigate the product and the
> content, not to re-train the workforce.**

---

## 11. Related Documents

| Document | Relationship |
|---|---|
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) | The process this pack teaches (`LS-15`) |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Block A source |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Block D trees |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | Block E |
| `KB-013` ESD, Chemical and Battery Safety Data | Block A hazard data |
| `KB-016` Technician Field Reference Card Set | Job aids; the `CP-01` boundary (`PK-04`) |
| `KB-004`…`KB-007` guide sets | Technical content the practical sessions draw on |
| `UI-012` `P02` copy pack · `UI-009` offline and sync copy | The interface |
| [`../08A_Framework/TR-005_Question_Bank_Technician_Certification.md`](../08A_Framework/TR-005_Question_Bank_Technician_Certification.md) | The certification instrument |
| `DT-007` service report | Evidence output |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Bengali technical authoring capability does not exist** (`TR-001` `O-05`, `KB-002` `O-05`). This pack is `P0`, must be authored in Bengali, and the terminology base is unbuilt. **This is the single largest risk to the only `P0` file in the category** | Localisation Lead with Technical Director | **W1 — ahead of W2 delivery** |
| **O-02** | **`M22` FR-LMS-025 mobile learning inside `P02` must exist at W2.** The entire delivery model depends on it; if it is not present, 200–400 technicians need a classroom alternative that does not scale | CTO with L&D | **W2 — blocking the delivery model** |
| **O-03** | **P1/P2 practical sessions require an assessor and a physical rig at every delivering branch.** With 51+ branches and `R12` at 15–30 people, assessor coverage is not solved | Technical Director with HR | **W2** |
| **O-04** | **OJT costs 10 supervised days per new technician.** With high turnover across 200–400 technicians, this is a continuous, uncosted demand on `R10`/`R12` capacity — the same people owed to `KB` articles and `TR-005` items | Operations Director with PMO | **W2** |
| **O-05** | Inert hazard training units (swollen cell, liquid-damaged unit) must be sourced, stored and presented safely. Same gap as `TR-005` `O-06` and `TR-007` `O-03` | HSE Lead | **W2** |
| **O-06** | `SP-033`'s 36 diagnostic trees are unauthored (`SP-033` O-01) and `KB-004`…`KB-007`'s 160 articles are unwritten (`AUDIT-008`). **Blocks D and the P2 practical teach against content that does not exist** | Technical Director | **W2** |
| **O-07** | The printed fallback pack for §5 during an outage is unspecified | Operations with Content Design | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections in order; §11 and Open Items added per category convention
- [x] Delivery model designed against the real constraints — turnover, literacy, device, language (`PK-02`)
- [x] On-device microlearning at under 3 minutes per item (`DS-07`)
- [x] Bengali **authored**, not translated (`DS-17`, `LS-07`)
- [x] Safety block first, with an annual practical carrying no grace period
- [x] Out-of-level escalation made a non-negotiable practical (exercise 7)
- [x] Offline working assessed as a full-day simulation, not a lecture
- [x] Knowledge capture built into the curriculum, connecting `M61` to training
- [x] OJT sign-off gate present with a defined task count (`LS-03`, FR-LMS-027)
- [x] Job-aid boundary with `KB-016` stated (`PK-04`, `CU-15`) — resolves `AUDIT-008` KB-09 at pack level
- [x] All four Required Drivers named; usage identified as the true behaviour signal
- [x] All internal links resolve
- [x] `BRU-SRM-07`/`-09`/`-11`/`-12`/`-14` cited to `05-05`; `FR-LMS-*` and `FR-KMS-024` to their modules; `KPI-004` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` Bengali authoring capability — outstanding; the largest risk to the only `P0` file**
- [ ] **`O-02` `M22` mobile learning in `P02` at W2 — outstanding; blocks the delivery model**
- [ ] **`O-06` upstream `SP-033` trees and `KB` articles — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director, Operations Director and HSE Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
