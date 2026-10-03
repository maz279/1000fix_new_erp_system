---
id: TR-003
title: Course Design Standard and Storyboard Template
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development
author: Learning & Development with Content Design
reviewers: [HR Director, Content Design Lead, Localisation Lead, Quality Manager, Technical Director, Accessibility reviewer, Programme Content Lead]
approver: HR Director with Content Design Lead
content_class: E
purpose: >
  The learning-objective format, module length, interaction types, assessment design and bilingual
  scripting rules that make courses authored by different vendors and trainers interchangeable and
  maintainable across nine waves and thirty-six months. Without it, twenty course packs by several
  authors cannot be reviewed against anything, cannot be translated predictably, and cannot be
  updated when the system they teach changes underneath them.
traces_to: [M22, TR-001, TR-002, TR-004, TR-005, TR-006, TR-022, TR-024, CG-003, CG-004, CG-008, CG-010, CG-011, VB-009, BN-003, TS-002, UI-001]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-017 course catalogue with objectives, competencies addressed, duration, delivery mode and prerequisites; FR-LMS-024 digital learning with mobile access; FR-LMS-025 mobile learning within P02
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-008_Content_Definition_of_Done_and_QA_Checklist.md — the checklist a file must pass to become Approved
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md — WCAG 2.1 AA is contractual under 04-00 PS-04 and 05-06; most WCAG failures are content failures
    verified: 2026-08-17
    class: P1
  - source: New World Kirkpatrick Model (Kirkpatrick and Kirkpatrick, 2016) — design backwards from Level 4, define leading indicators, sustain behaviour through Required Drivers
    verified: 2026-08-17
    class: P2
  - source: Cognitive-load and adult-learning practice — working memory constrains how much new material can be processed at once; segmenting content and pruning material that does not serve the objective improves transfer. Applied here as the module-length and pruning rules in §4.4
    verified: 2026-08-17
    class: P3
supersedes: none
review_due: 2027-02-17
---

# TR-003 — Course Design Standard and Storyboard Template

> **`TR-001` says what training must achieve. `TR-002` says who takes what. This file says what a
> course looks like** — so that a pack written by an internal trainer in W1 and a pack written by a
> vendor in W7 can be reviewed against the same standard, translated by the same process, and
> updated by someone who wrote neither.

---

## 1. Purpose

Twenty course packs will be authored across thirty-six months by internal L&D staff, technical
specialists, and — realistically — at least one external vendor. Without a design standard:

| Without it | Consequence |
|---|---|
| Objectives written as topics ("Understand dispatch") | Nothing is assessable, so assessment becomes a quiz about the slides |
| Module length set by content volume | Learners lose the thread; the four-hour target is missed by an hour and nobody can say why |
| Interaction chosen by author preference | Statutory content delivered as a video nobody can evidence, and a simple lookup delivered as a workshop |
| Bengali produced by handing a deck to a translator | Translated concepts rather than the job — the failure `CG-010` names explicitly |
| Screenshots embedded freely | Every UI change orphans a course, and nine waves of UI change orphan all of them |

**Consequence of absence (`CP-03`).** Packs that cannot be compared, substituted, translated,
maintained or reviewed — and a training function that rewrites its entire library at every release
because nothing was designed to be updated.

---

## 2. Scope

**In scope:** the objective format; the design sequence (backwards from Level 4); module and segment
length; interaction types and when each is correct; the storyboard template; screen and screenshot
rules; bilingual scripting; accessibility; reusable-asset rules; the review gates; and rules
`DS-01`…`DS-20`.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Learning model, delivery mix, evaluation framework | [`TR-001_Training_Strategy_and_Competency_Framework.md`](TR-001_Training_Strategy_and_Competency_Framework.md) |
| Who takes what, in what order | [`TR-002_Role_Based_Curriculum_Map.md`](TR-002_Role_Based_Curriculum_Map.md) |
| Pass marks, attempts, item quality, re-certification | [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) |
| Question-bank construction | [`TR-005_Question_Bank_Technician_Certification.md`](TR-005_Question_Bank_Technician_Certification.md) · [`TR-006_Question_Bank_Functional_Roles.md`](TR-006_Question_Bank_Functional_Roles.md) |
| Job-aid format | [`../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) |
| Product voice, tense, person, terminology | [`../../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) · [`../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) |
| Bengali typography and numerals | `VB-009` · `BN-003` |
| Media production specifications — resolution, format, compression | `MM-001` |
| Sandbox and training data | `TS-002` |

---

## 3. Audience

| Audience | Uses this file to… |
|---|---|
| **L&D course authors** | Author packs that pass review first time |
| **Technical specialists (`R12`, `R13`)** | Contribute technical content in a shape a designer can use |
| **External training vendors** | Deliver work that integrates rather than sits apart |
| **Localisation Lead** | Receive content that is scriptable rather than translatable-only |
| **Reviewers** | Have something specific to review against (§6) |
| **Accessibility reviewer** | Check against `CG-011` at design time rather than after production |

---

## 4. Content

### 4.1 Design sequence — backwards

**`DS-01`: courses are designed in this order and no other.**

| Step | Produce | Why here |
|:--:|---|---|
| 1 | **The Level 4 measure** the pack exists to move (`LS-01`) | If it cannot be named, the course should not be built |
| 2 | The Level 3 behaviours that would move it — observable, on the job | These become the OJT sign-off criteria (`LS-03`) |
| 3 | The **Required Drivers** that will sustain those behaviours (`LS-04`) | Designed in, not added after |
| 4 | The Level 2 competences the behaviours require | These become the learning objectives |
| 5 | Assessment that evidences those competences | Written **before** content, so content cannot drift from it |
| 6 | Module outline and sequence | |
| 7 | Content, exercises, job aids | Last, because it is the most expensive thing to change |

> **Step 5 before step 7 is the rule most often broken and the one that matters most.** Writing
> assessment after content produces an assessment of the content. Writing it before produces an
> assessment of the competence — and content that must earn its place by preparing learners for it.

### 4.2 Learning objective format

**`DS-02`: every objective uses the form *"On completion the learner can \<observable action\> \<to
what standard\> \<under what conditions\>."***

| ✅ Conforming | ❌ Non-conforming | Why |
|---|---|---|
| "…can complete a walk-in intake including device identification, condition capture and customer expectation setting, in under 3 minutes, using the `P03` intake workspace with a live customer present" | "Understand the intake process" | Not observable; not assessable |
| "…can identify from a nameplate whether a system contains an A1, A2L or A3 refrigerant, and state the handling consequence of each" | "Be aware of refrigerant safety" | "Be aware" cannot be failed |
| "…can reconcile a van stock discrepancy, apply the correct `MD-026` reason code, and escalate above the approval threshold" | "Learn about van stock" | No standard, no condition |

**Banned objective verbs:** understand · know · be aware of · appreciate · be familiar with ·
learn about · gain knowledge of. **`DS-03`** — none of them can be observed, so none can be assessed
or evidenced, and `M22` FR-LMS-038 requires evidence.

**`DS-04`: every objective maps to at least one assessment item and at least one exercise.** An
objective with neither is decoration. An assessment item with no objective is a trick question.

### 4.3 Course architecture

| Unit | Length | Contains | Rule |
|---|---|---|---|
| **Segment** | **5–8 minutes** | One concept or one task | `DS-05` — the unit of attention |
| **Module** | 20–45 minutes | 3–6 segments + practice + check | `DS-06` |
| **Course (pack)** | 1–8 hours | Modules + assessment + job aids | Per `TR-002` |
| **Microlearning item** | **Under 3 minutes** | One task, one job aid, one safety point | `DS-07` — the `P02` and rider format |

**`DS-08`: every module ends with practice, not with a summary.** A summary tells the learner what
they heard. Practice tells them — and the trainer — whether they can do it.

**`DS-09`: no unbroken presentation longer than 8 minutes in any mode.** Classroom, virtual and
e-learning alike. Working memory is the constraint, and it does not care which channel the content
arrived through.

### 4.4 The pruning rule

**`DS-10`: content that does not serve a stated objective is removed, however interesting it is.**

This is the hardest rule to apply and the one that protects the four-hour target. In practice the
material that gets cut is:

| Commonly included | Why it is cut | Where it belongs instead |
|---|---|---|
| System architecture and module map | No agent task requires it | Onboarding orientation, if anywhere |
| "History of the project" | Zero objectives | Change comms (`CM-*`) |
| Exhaustive field-by-field screen tours | Learners cannot retain 40 fields | Job aid (`TR-022`); field help text (`UI-003`) |
| Every exception path | 80% of exceptions occur in 20% of cases | Job aid + escalation route |
| Policy read aloud | Reading is not training | Pre-read with a comprehension check |
| Another worked example of the same pattern | Diminishing returns after two | Practice with varied cases |

### 4.5 Interaction types — choosing correctly

| Interaction | Correct for | Wrong for | Evidence produced |
|---|---|---|---|
| **Guided system walkthrough** | First exposure to a transaction | Anything the learner will do rarely | None on its own |
| **Sandbox practice with real-shaped data** | Every operational transaction | Where `TS-002` data does not exist | Completion + accuracy |
| **Scenario / decision case** | Judgement — dispatch priority, escalation, override, complaint | Rote procedure | Reasoning quality |
| **Practical demonstration** | Technician repair, safety procedure, equipment use | Anything without physical performance | **Assessor sign-off** |
| **Role play** | Customer conversations, complaint handling, collections | Technical procedure | Observation |
| **Error-first drill** | Showing what a mistake looks like before teaching the right path | Statutory content, where errors must not be modelled | Recognition speed |
| **Peer teach-back** | Consolidation in supervisor and champion cohorts | Large mixed-experience cohorts | Explanation quality |
| **Comprehension check** | Confirming a pre-read was done | Establishing competence | Pass/fail |
| **Video demonstration** | Technique that must be seen — micro-soldering, refrigerant recovery | Step-by-step procedure a learner must follow mid-task | None |

**`DS-11`: statutory and safety content is delivered in a mode that produces per-learner evidence.**
A video with no check evidences attendance, not competence, and `LS-13` requires competence to be
evidenced per learner.

### 4.6 Screens, screenshots and the maintenance trap

**Nine waves of UI change will orphan any course built on screenshots.** `DS-12`…`DS-15` exist to
contain that.

| # | Rule |
|---|---|
| **DS-12** | Teach the **task and the decision**, not the screen. "Find the customer, confirm the device, capture condition" survives a redesign; "click the blue button top-right" does not |
| **DS-13** | Screenshots are used only where the visual is the point — a status colour, a warning state, a layout that must be recognised. **Maximum one screenshot per segment** |
| **DS-14** | Every screenshot is captured from the **sandbox** (`TS-002`), never from production. `AU-26` prohibits customer-identifiable content and a production screenshot contains it by definition |
| **DS-15** | Screenshots are registered with the release they were captured against; `TR-024` release training reviews them at each release |
| **DS-16** | UI labels quoted in course text come from `UI-002`/`UI-003`, not from a screenshot's pixels, so a label change is a find-and-replace rather than a re-shoot |

### 4.7 Bilingual scripting

`CG-010` places 20 of 24 `TR` files bilingual, and `LS-07` requires technician and rider content to
be **authored in Bengali**, not translated into it.

| # | Rule |
|---|---|
| **DS-17** | Technician, rider, store keeper, cashier and agent content is authored in Bengali by a Bengali-speaking author with the domain, then rendered in English — **not the reverse** |
| **DS-18** | Head-office functional content may be authored in English and translated, with in-context sign-off (`BN-018`) |
| **DS-19** | Scripts are written for **speaking**, not for reading aloud — short sentences, one idea per sentence, no subordinate clauses stacked. This is what makes translation tractable |
| **DS-20** | Codes, part numbers, model names, measurements, system field labels and error IDs are never translated (`LS-08`, `AU-31`) |
| **DS-21** | Layout is designed for the **Bengali** text length, which runs 20–40% longer (`VB-007`) — slides, job aids and on-screen text alike |
| **DS-22** | Numerals follow `VB-009`; a figure never changes digit system between the two versions of the same item |
| **DS-23** | Safety content is human-translated in context and re-approved by HSE after translation (`AU-06f`) |

### 4.8 Accessibility

`CG-011` makes WCAG 2.1 AA contractual, and most WCAG failures are content failures.

| Requirement | Applied to training |
|---|---|
| Text alternatives | Every image, diagram and screenshot carries alt text in both languages |
| Captions | Every video carries captions in both languages; **captions are not optional for a workforce that often works in noisy environments or without headphones** |
| Colour not sole carrier | Status, pass/fail and hazard indications pair colour with a word or symbol |
| Contrast and text size | Legible on the device class the audience actually uses — mid-range Android for technicians and riders |
| Structure | Headings, lists and tables used semantically so screen readers and translators both work |
| Reading level | Plain language; `CG-011` reading-level target applies |
| Time limits | No timed interaction except where the assessment deliberately measures speed, and then it is declared |

### 4.9 Reusable assets

**`DS-24`: an asset used by more than one pack is authored once and referenced.** The register is
built on `CP-01`, and courses are the easiest place to violate it.

| Asset | Authored in | Referenced by |
|---|---|---|
| Universal core modules | `TR-002` §4.2 *(pending `TR-025`)* | Every pack |
| Safety content | `KB-013`, `SP-030` | Every pack touching a hazard |
| Terminology | `CG-004`, `BN-003` | Every pack |
| System-basics module | Universal core | Every pack |
| Job aids | `TR-022` | The pack that produces them |
| Question items | `TR-005`, `TR-006` | The packs that assess against them |
| Exercise data | `TS-002` | Every pack with a sandbox exercise |
| Field reference cards | `KB-016` | Technician and rider packs |

### 4.10 The storyboard template

Every module is storyboarded before production. **`DS-25`: production does not begin without an
approved storyboard**, because changing a storyboard costs minutes and changing a produced module
costs days.

| Field | Content |
|---|---|
| Module ID | `TR-nnn-Mnn` |
| Objective(s) served | From §4.2 — **at least one, stated in full** |
| Duration | Target minutes |
| Segment breakdown | 3–6 segments, 5–8 minutes each, each with its own single point |
| Method per segment | From §4.5 |
| On-screen / on-slide text | **Final wording**, both languages, not placeholder |
| Facilitator narration | Speaking script (`DS-19`), both languages |
| Media required | Screenshot / diagram / video, with source and `MM-001` spec |
| Practice | What the learner does, with the success criterion |
| Sandbox data required | `TS-002` reference |
| Check | The assessment item(s) this segment prepares for |
| Job aid produced | If any — `TR-022` reference |
| Accessibility notes | Alt text, captions, colour-pairing |
| Governing source | The `SP`, `KB`, `MD` or `LG` file this teaches from (`LS-15`) |
| Review status | Content · technical · localisation · accessibility · HSE where applicable |

### 4.11 Review gates

**`DS-26`: a pack passes five reviews, and the reviewer is never the author** (`BRU-KMS-02` pattern,
applied to training).

| Gate | Reviewer | Checks |
|---|---|---|
| **1 — Instructional** | L&D peer | Objectives observable; assessment maps to objectives; segment length; pruning applied |
| **2 — Technical** | Domain owner (`R12`, `R32`, Finance, etc.) | Is it correct? Does it match the governing `SP`/`KB`/`MD` file? |
| **3 — Localisation** | Localisation Lead with a domain reviewer | Bengali authored not translated; terminology per `BN-003`; layout for Bengali length |
| **4 — Accessibility** | Accessibility reviewer | `CG-011` conformance |
| **5 — HSE** | HSE Lead | **Any pack containing safety content** — same gate as `BRU-KMS-03` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`TR-001_Training_Strategy_and_Competency_Framework.md`](TR-001_Training_Strategy_and_Competency_Framework.md) | Design sequence, Required Drivers, language position |
| [`TR-004_Assessment_and_Certification_Policy.md`](TR-004_Assessment_and_Certification_Policy.md) | §4.1 step 5 — assessment written before content |
| [`../../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) · [`../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Voice and terminology |
| [`../../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §4.8 |
| `VB-009` · `BN-003` · `BN-018` | Bengali typography, terms, in-context sign-off |
| `TS-002` | Sandbox data every exercise depends on |
| `MM-001` | Media production specifications |
| `M22` FR-LMS-017/024/025 | Course catalogue metadata and mobile delivery |

| Depended on by |
|---|
| `TR-005`…`TR-024` — every course pack and question bank · external training vendors · `TR-024` release training |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Annual**, and after the first three packs are authored — the first three will show what this standard got wrong |
| Trigger for out-of-cycle review | The four-hour target missed · translation rework exceeding a threshold · packs orphaned by a UI release (`DS-12`…`DS-16` failing) · an accessibility finding |
| Owner | Learning & Development with Content Design |
| Change log | `RF-006` |
| Enforcement | `DS-01`…`DS-26`; the five review gates; `CG-008` Definition of Done |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`TS-002` sandbox and training data does not exist** (Category 13 unstarted). §4.5 makes sandbox practice the default for every operational transaction and `DS-14` requires screenshots from it. **Without it, packs are built on demonstration rather than practice** | Test Lead with L&D | **W1 — before the first pack is produced** |
| **O-02** | No accessibility reviewer is named for training content. Gate 4 has no owner | Content Design Lead with HR | W1 |
| **O-03** | Bengali-authoring capability (`DS-17`) requires authors who are domain-competent **and** Bengali-native. `TR-001` `O-05` records the terminology gap; this adds the authoring-capability gap | Localisation Lead with Technical Director | **W1 — gates `TR-009`** |
| **O-04** | **`MM-001` is written** — Category 19 completed 2026-08-18. The gap changes shape: storyboards can now cite a real media specification, and **the §4.10 "Media required" line must name the `MM-001` asset class (A1, A4, A7) rather than a free-text description**. `MM-001` `O-04` records that **media production itself remains unbudgeted** | Content Design | W2 — a read-across, no longer a gap |
| **O-05** | Whether `M22` supports segment-level tracking, or only course-level completion, is unconfirmed. §4.3 assumes segments are the unit of design; if tracking is course-level only, resumption and refresher targeting are coarser than designed | CTO with L&D | Before `M22` build |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections present, §7 added per category convention
- [x] Design sequence stated as backwards-from-results, with assessment before content (`DS-01`)
- [x] Objective format specified with conforming and non-conforming examples, and banned verbs named
- [x] Segment, module and microlearning lengths set with the reason (attention, not preference)
- [x] Pruning rule given with a concrete list of what usually gets cut and where it goes instead
- [x] Interaction types matched to purpose, with wrong-use cases stated
- [x] Screenshot and maintenance-trap rules stated — the nine-wave problem addressed at design time
- [x] Bengali authored rather than translated for field roles (`DS-17`)
- [x] Accessibility treated as a design input, not a production check
- [x] Reusable assets bound to `CP-01`
- [x] Storyboard template specified field by field, with production gated on approval (`DS-25`)
- [x] Five review gates with reviewer ≠ author
- [x] All internal links resolve
- [x] `FR-LMS-*` cited to `M22`; governance rules cited to their `CG` files
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` `TS-002` sandbox data — outstanding; blocks practical exercise design**
- [ ] **`O-03` Bengali authoring capability — outstanding**
- [ ] Named approvers recorded — **pending HR Director and Content Design Lead**
- [x] English-only, per `CG-010` §3.2 — framework content

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
