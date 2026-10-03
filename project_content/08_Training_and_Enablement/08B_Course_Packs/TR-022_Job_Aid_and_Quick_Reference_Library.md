---
id: TR-022
title: Job Aid and Quick Reference Library
project: 1000FiX ERP System v2.0
content_type: Training course pack
template: TPL_Training_Course_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Content Design
reviewers: [Content Design Lead, Operations Director, Quality Manager, Knowledge Manager, HSE Lead, Localisation Lead, Accessibility reviewer]
approver: HR Director with Content Design Lead
content_class: D
purpose: >
  The one-page task references for the twenty most frequent tasks per role, held at the point of
  work. Learning decays; job aids are the Required Driver that sustains competence after go-live,
  and without them a four-hour induction becomes a four-hour memory that has faded by week three.
traces_to: [M22, M61, P02, P03, P09, P10, P11, TR-001, TR-002, TR-003, TR-004, TR-007, TR-008, TR-009, TR-010, TR-011, TR-012, TR-013, TR-014, TR-015, TR-016, TR-017, TR-018, TR-019, TR-020, TR-021, TR-023, TR-024, KB-016, CG-011, VB-009, UI-002]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: TR-022_Job_Aid_and_Quick_Reference_Library_BN.md
sources:
  - source: New World Kirkpatrick Model (Kirkpatrick and Kirkpatrick, 2016) — Level 3 behaviour is sustained by Required Drivers, of which reinforcement at the point of work is the first
    verified: 2026-08-17
    class: P2
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md — the offline technical and safety card set; the CP-01 boundary with this library
    verified: 2026-08-17
    class: P1
  - source: project_content/_AUDIT/AUDIT-008_Category_07_KB_Content_Audit.md finding KB-09 — TR-022 and KB-016 may be the same artefact produced by two workstreams; the boundary must be defined before either is authored
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md — WCAG 2.1 AA is contractual; most WCAG failures are content failures
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# Course Pack — Job Aid and Quick Reference Library

| Item | Value |
|---|---|
| Audience role(s) | **All 35 internal roles** |
| Headcount | **800+** |
| Duration | Not a taught course — **each aid is consumed in under 60 seconds at the point of work** |
| Delivery mode | Printed at the workstation · in-app · in the `P02`/`P09` offline pack |
| Language | **Bengali primary for operational roles**, English parallel |
| Prerequisites | The role's course pack — an aid is a reminder, not an instruction manual |
| Certification outcome | None — aids are not assessed; **the tasks they support are** |
| Wave | W1 |

> **Template conformance.** `TPL_Training_Course_Pack.md` applied to a **library of artefacts
> rather than a taught course**, as `CG-009` §3 requires for all 20 non-framework `TR` files. All
> ten sections retained in order and answered at library level; §11–§12 are justified additions.
> Same template-variant issue as `TR-005`, `TR-006` and `AUDIT-008` KB-10.

---

## 1. Learning Objectives

A job aid does not teach; it **removes the need to remember**. The library's objectives are
therefore properties of the artefacts:

| # | Every aid in this library… | Verified by |
|---|---|---|
| 1 | Answers one task, completely, in under 60 seconds | Timed usability test |
| 2 | Is legible at the workstation it lives at — counter, bench, van, console, phone | Field test |
| 3 | Is readable in Bengali by the person who needs it | Localisation review |
| 4 | States the block or limit that applies to the task | Content review |
| 5 | States where to go when the aid is not enough | Content review |
| 6 | Is traceable to the course pack and the governing `SP`/`MD`/`KB` file it derives from | `JA-01` |
| 7 | Is versioned against the release it describes | `JA-06` |
| 8 | Never duplicates a `KB-016` card | `JA-02` — **the `CP-01` boundary** |

---

## 2. Curriculum Position

| Precedes | Follows | Refreshed every |
|---|---|---|
| Sustained competence after training — the reinforce Required Driver (`LS-04`) | The role's course pack | **Every release affecting the task** (`TR-024`); full review 12 months |

---

## 3. Module Outline — *the library structure*

### 3.1 The `TR-022` / `KB-016` boundary — resolving `AUDIT-008` KB-09

**`JA-02`: the two libraries answer different questions and never duplicate.** `TR-002` §6.3
(`CU-15`) sets the boundary; this is its operational form.

| Question the user is asking | Library | Example |
|---|---|---|
| *"How do I do this in the system?"* | **`TR-022`** | Record a resolution · raise a transfer · take a payment · code a disposition |
| *"Is this safe? What does this mean technically? May I substitute this part?"* | **`KB-016`** | Swollen battery · refrigerant class · IMEI prohibition · prohibited substitutions |
| *"What is my approval limit?"* | **`TR-022`** | Discount authority · adjustment threshold |
| *"When must I stop and escalate on a technical judgement?"* | **`KB-016`** | Out-of-level fault · degraded array · BER evidence |

**Where a technician needs both, they are two artefacts that link to each other** (`PK-04`). The
test: if the aid would still be true with the software replaced, it belongs in `KB-016`; if it
describes the software, it belongs here.

### 3.2 Aid types

| Type | Format | Used for |
|---|---|---|
| **Task card** | One page / one screen, numbered steps | The twenty most frequent tasks per role |
| **Decision aid** | Branching, one page | Which code · which route · which document |
| **Limit card** | Table | Approval authority · thresholds · what I may not do |
| **Code card** | Table | Reason codes · disposition codes · resolution codes for the role |
| **Checklist** | Tick list | Opening, closing, handover, close, count — sourced from `SP-032` where it exists |
| **Escalation card** | Who, when, with what | Every role has one |

### 3.3 Library inventory by role

**`JA-03`: twenty aids per role is a ceiling, not a target.** A role with eight genuinely frequent
tasks gets eight aids; padding to twenty produces a folder nobody opens.

| Role family | Aids | Source pack |
|---|---:|---|
| Service Centre Agent (`R08`) | 7 | `TR-007` |
| Dispatch (`R07`) | 6 | `TR-008` |
| Field Technician (`R10`–`R12`) | 5 *(+ `KB-016` cards)* | `TR-009` |
| Workshop Supervisor (`R09`) | 6 | `TR-010` |
| Branch Manager (`R06`) | 7 | `TR-011` |
| Inventory and stores (`R17`, `R18`, `R20`) | 8 | `TR-012` |
| Procurement (`R19`) | 7 | `TR-013` |
| Finance and cash (`R26`–`R29`) | 9 | `TR-014` |
| HR and payroll (`R30`, `R31`) | 7 | `TR-015` |
| Quality and audit (`R32`) | 7 | `TR-016` |
| Contact centre (`R34`, `R35`) | 8 | `TR-017` |
| Account and contract (`R21`, `R22`) | 9 | `TR-018` |
| Marketplace (`R24`) | 7 | `TR-019` |
| Rider and logistics (`R15`, `R16`) | 9 | `TR-020` |
| System administration (`R33`, `R13`) | 6 | `TR-021` |
| **Universal** — escalation, access scope, incident reporting | 3 | `TR-002` Layer 1 |
| | **~111 aids** | |

---

## 4. Facilitator Guide — *authoring rules*

| # | Rule | Class |
|---|---|:--:|
| **JA-01** | Every aid names the course pack and the governing `SP`/`MD`/`KB`/`LG` file it derives from | **H** |
| **JA-02** | No aid duplicates a `KB-016` card; the §3.1 test decides which library owns it | **H** |
| **JA-03** | Twenty aids per role is a ceiling; frequency decides inclusion | **H** |
| **JA-04** | One task per aid. **An aid covering two tasks is two aids** | **H** |
| **JA-05** | Under 60 seconds to answer, measured, not estimated | **H** |
| **JA-06** | Every aid carries its version and the release it describes | **C** |
| **JA-07** | Every aid states the block or limit that applies, and where to go when it is not enough | **H** |
| **JA-08** | **Bengali is authored, not translated**, for operational roles (`DS-17`) | **H** |
| **JA-09** | Laid out for the Bengali text length (`DS-21`, `VB-007`) | **H** |
| **JA-10** | Codes, field labels and error IDs are quoted from `UI-002`/`UI-003`, never from a screenshot (`DS-16`) | **H** |
| **JA-11** | Accessible per `CG-011` — contrast, size, colour not sole carrier, alt text on any image | **H** |
| **JA-12** | Maximum one image, and only where the image is the answer (`DS-13`) | **S** |
| **JA-13** | An aid is revised or withdrawn when the task it describes changes (`TR-024`) | **C** |
| **JA-14** | A withdrawn aid is **removed from the workstation**, not left to be found | **H** |
| **JA-15** | Safety content is never abbreviated into an aid; it is referenced to `KB-016`/`KB-013` (`RC-02` pattern) | **H** |

> **`JA-15` is the rule that keeps the two libraries honest.** The temptation, when a task has a
> safety implication, is to summarise the safety point onto the task card. That produces a
> compressed safety instruction in an unreviewed artefact — exactly what `KB-016` `RC-02` prohibits.

---

## 5. Participant Workbook Contents

Not applicable — the library **is** the reference material. What each role receives:

| Delivery | Contents |
|---|---|
| **Workstation set** | Printed, laminated, at the counter / bench / console |
| **In-app** | Surfaced contextually where the portal supports it |
| **Offline pack** | Technician and rider aids inside `P02` / `P09`, alongside `KB-016` cards |
| **Index** | One page per role listing its aids and where each lives |

---

## 6. Exercises

The library is not taught. It is **tested**, and the tests are its quality gate.

| # | Test | Method | Success criterion |
|---|---|---|---|
| 1 | **60-second test** | 10 users per aid, timed, cold | **8 of 10 complete the task inside 60 seconds** |
| 2 | **Cold-read test** | A user who has not taken the pack attempts the task | Either succeeds or correctly stops and escalates |
| 3 | Workstation legibility | At the actual workstation, in actual lighting | Readable without leaning in |
| 4 | Bengali naturalness | Native reader, in context | Reads as written, not as translated |
| 5 | Boundary test | Reviewer checks against `KB-016` | **No duplication** (`JA-02`) |
| 6 | Accessibility | Against `CG-011` | Conformant |
| 7 | **Currency test** | After each release | Aids for changed tasks revised or withdrawn (`JA-13`) |

**`JA-16`: an aid that fails the 60-second test is redesigned, not explained.** If users need
context to use it, it is a course page, not a job aid.

---

## 7. Assessment

**Job aids are not assessed; the tasks they support are.** The library's own quality gates:

| Gate | Standard | Owner |
|---|---|---|
| Authoring conformance | `JA-01`…`JA-15` | L&D |
| 60-second and cold-read tests | §6 tests 1–2 | Content Design |
| Localisation | Bengali authored and reviewed in context (`BN-018`) | Localisation Lead |
| Accessibility | `CG-011` | Accessibility reviewer |
| Boundary | No `KB-016` duplication | Knowledge Manager **and** L&D jointly |
| Currency | Per release | `TR-024` |

---

## 8. Job Aids Produced

This file **is** the job-aid library. Its own deliverable is the **index**: one page per role
listing its aids, their version, and where each lives — printed, in-app or offline.

---

## 9. Trainer Requirements

| Requirement | Detail |
|---|---|
| Authors | Content Design with the domain owner of each pack |
| **Bengali authors** | Native, domain-competent (`JA-08`) — capability gap, `TR-001` `O-05` |
| Testers | **Real users at real workstations** — the tests in §6 cannot be run at a desk |
| Accessibility reviewer | `CG-011` gate — **unowned**, `TR-003` `O-02` |
| Boundary reviewer | Knowledge Manager, jointly with L&D |
| Production | Print, lamination and distribution to 51+ sites; in-app publication |

---

## 10. Evaluation

| Level | Measure | Target |
|---|---|---|
| **Reaction** | Whether users report reaching for the aid rather than asking a colleague | Diagnostic only (`LS-02`) |
| **Learning** | Cold-read test pass rate | 8 of 10 |
| **Behaviour** | **Aid usage where measurable** (in-app opens) · help-desk contacts on tasks that have an aid · error rate on aided tasks vs unaided | Help-desk contacts on aided tasks falling |
| **Result** | **Sustained competence: error and rework rates at 30, 60 and 90 days after training do not rise back toward baseline** | Per `RP-001` |

**Required Drivers**: this library **is** the reinforce driver (`LS-04`). Its own drivers are —
encourage: champions point to aids rather than answering (`TR-023`) · monitor: help-desk topic
analysis identifies missing aids · reward: none; an aid that is used is its own evidence.

> **The Level 4 measure here is the most important in the category and the least often attempted.**
> Every course produces a spike in competence that decays. The question this library exists to
> answer is whether the decay curve flattens. Measuring error rates at 30, 60 and 90 days after
> training — against the same measure before it — is the only way to know, and it costs nothing but
> the discipline to look.

---

## 11. Sourcing and Ownership *(addition — justified: 111 aids across 15 packs and two libraries need an explicit ownership rule)*

| Aid origin | Authored by | Owned by | Lives in |
|---|---|---|---|
| Produced by a course pack | That pack's author | L&D | `TR-022` |
| Derived from an `SP` procedure | L&D with the process owner | L&D | `TR-022` |
| Derived from an `MD` register | L&D with the data steward | L&D | `TR-022` |
| **Technical or safety decision** | **`KB` authors** | **Technical / HSE** | **`KB-016`** |
| Checklist already in `SP-032` | Not re-authored — **referenced** (`CP-01`) | Operations | `SP-032` |

**`JA-17`: an aid is authored once and referenced everywhere.** Three packs needing an escalation
card share one card, not three.

---

## 12. Related Documents *(addition — justified: category convention)*

`TR-007`…`TR-021` — every pack's §8 lists the aids it produces ·
[`../08A_Framework/TR-002_Role_Based_Curriculum_Map.md`](../08A_Framework/TR-002_Role_Based_Curriculum_Map.md) §6.3 — the `CU-15` boundary ·
[`../08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) — `DS-13`, `DS-16`, `DS-21` ·
[`TR-024_Release_Training_and_Refresher_Standard.md`](TR-024_Release_Training_and_Refresher_Standard.md) — currency on release ·
[`TR-023_Train_the_Trainer_and_Super_User_Kit.md`](TR-023_Train_the_Trainer_and_Super_User_Kit.md) — champions point to aids ·
`KB-016` Technician Field Reference Card Set — **the boundary partner** ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) — checklists referenced, not duplicated ·
[`../../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · `VB-009` · `UI-002`.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **111 aids are unwritten**, and each depends on its parent course pack, which is also unwritten. Estimated **220–440 hours** of Content Design and domain-owner time, plus Bengali authoring, testing, production and distribution to 51+ sites | Content Design with L&D | **W1 — the reinforce driver must exist when W1 training lands** |
| **O-02** | **The `KB-016` boundary (`JA-02`) requires a joint owner.** §7 assigns it to Knowledge Manager and L&D jointly; neither has agreed to it. This is `AUDIT-008` KB-09 resolved on paper and unresolved in practice | Programme Content Lead | **W1** |
| **O-03** | The §6 tests require **real users at real workstations**. Before go-live those workstations do not exist in their final form; testing must be staged | Content Design with Operations | W1 |
| **O-04** | **Print, lamination and physical distribution to 51+ sites is unbudgeted and unowned.** An aid that exists as a PDF nobody printed is not at the point of work | Operations with L&D | **W1** |
| **O-05** | Accessibility reviewer unowned (`TR-003` `O-02`) | Content Design Lead | W1 |
| **O-06** | **`UI-002`/`UI-003` label sources exist, but in-app contextual surfacing (§5) depends on portal support that is unconfirmed** per portal | CTO with Content Design | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Training_Course_Pack.md` — all ten sections retained in order, library-level interpretation stated, additions §11–§12 justified
- [x] **`AUDIT-008` KB-09 resolved: the `TR-022` / `KB-016` boundary defined with an operational test (`JA-02`, §3.1)**
- [x] Twenty-per-role stated as a ceiling, not a target (`JA-03`)
- [x] 60-second and cold-read tests defined as measured gates, not aspirations (`JA-05`, `JA-16`)
- [x] Safety content prohibited from abbreviation into aids (`JA-15`)
- [x] Bengali authored rather than translated (`JA-08`)
- [x] Currency bound to release (`JA-13`) with withdrawal enforced at the workstation (`JA-14`)
- [x] Single-authorship rule prevents duplication across packs (`JA-17`, `CP-01`)
- [x] Level 4 measure identified as the decay curve — the category's most important and least-attempted measure
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` 111 aids authored — outstanding**
- [ ] **`O-02` boundary ownership agreed — outstanding**
- [ ] **`O-04` print and distribution to 51+ sites — outstanding; an unprinted aid is not a job aid**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending HR Director and Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
