---
id: MM-006
title: Video Production Brief — Training Series
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Learning & Development with Brand
author: Learning & Development with Brand, Content Design, Localisation and HSE
reviewers: [HR Director, Content Design Lead, Brand Lead, Localisation Lead, HSE Lead, Technical Director, Accessibility reviewer, Quality Manager, Programme Content Lead]
approver: Content Design Lead with HR Director
content_class: D
purpose: >
  The production specification for the internal training video series — where video is the right
  format and where it is not, duration, language, recording conditions, safety and evidence
  obligations, and the accessibility deliverables that ship with every item. TR-003 fixes the
  instructional design and DS-25 gates production on an approved storyboard; nothing states what
  a camera crew must actually deliver. Video training for 200-400 field technicians must be in
  Bengali, short enough to watch between jobs, and playable on a mid-range Android over a
  congested cell — and a training video that models an unsafe practice or an out-of-date screen
  teaches it to every technician who watches it, at a reshoot cost nobody has budgeted.
traces_to: [TR-001, TR-002, TR-003, TR-004, TR-009, TR-020, TR-022, TR-023, TR-024, KB-013, KB-016, SP-030, SP-008, SP-010, SP-012, CG-003, CG-008, CG-010, CG-011, CG-012, VB-002, VB-009, BN-002, BN-016, BN-017, HC-020, MM-001, MM-002, MM-007, MM-012, TS-002, TS-016, M22, 04-00 PS-03, 04-00 PS-08, 04-00 §P02, 05-06 NFR-073]
priority: P2
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md §4.3 DS-05 segment 5–8 minutes, DS-06 module 20–45 minutes, DS-07 microlearning under 3 minutes; §4.5 "Video demonstration — correct for technique that must be seen, wrong for step-by-step procedure a learner must follow mid-task"; DS-11 statutory and safety content must produce per-learner evidence; DS-17 Bengali authored not translated; DS-19 written for speaking; DS-23 safety re-approved by HSE after translation; DS-25 production does not begin without an approved storyboard; DS-26 five review gates
    verified: 2026-08-18
    class: P1
  - source: project_content/09_Help_Centre_and_Self_Service/HC-020_Video_Tutorial_Script_Library.md VS-02 video is used where reading is the barrier not where the task is long; VS-03 90-second maximum; VS-07 Bengali filmed not subtitled; VS-08 captions mandatory in both languages; VS-13 storyboard approved before production; VS-15 an orphaned video is withdrawn; O-02 production capability, budget and presenters are not identified
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §P02 non-negotiable requirements — complete Bengali interface; runs acceptably on a mid-range Android 11 device with 3 GB RAM; battery consumption under 12% per 8-hour shift; PS-08 offline-capable surfaces operate for 24 hours
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M22 §5.3 FR-LMS-024 digital learning with mobile access and FR-LMS-025 mobile learning delivered within P02; FR-LMS-038 evidence of completion
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.2.2 captions (prerecorded, Level A); SC 1.2.3 audio description or media alternative (Level A); SC 1.2.5 audio description (prerecorded, Level AA); SC 2.3.1 three flashes; SC 1.4.5 images of text
    verified: 2026-08-18
    class: P1
  - source: Bangladesh mobile network conditions — Ookla Speedtest Global Index for the September–November 2025 period placed Bangladesh 86th globally at an average mobile download of 41.72 Mbps, a national mean over a network reported to suffer spectrum shortage, uneven 4G reach and high subscriber density
    verified: 2026-08-18
    class: P3
    note: Reported measurement, used only to establish that a national average is not the design case. The design case is the congested-cell and edge-of-coverage rung in MM-001 §4.5, which is set from the device floor 04-00 §P02 states, not from this figure.
supersedes: none
review_due: 2027-02-18
---

# Video Production Brief — Training Series

| Item | Value |
|---|---|
| Governs | Every video produced for internal training and for the LMS (`M22`) |
| Instructional authority | [`TR-003`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) — **this file produces; `TR-003` designs** |
| Primary audience of the output | **200–400 field technicians**, 150–250 branch agents, 50–200 riders, plus functional roles |
| Language of the output | **Bengali, authored and filmed** (`TR-003` `DS-17`, `LS-07`) |
| Audience of this file | Video production suppliers, L&D, Brand, HSE |
| Wave | W2 · Months 5–8 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.8.
> §7 Open Items added per category convention.

---

## 1. Purpose

`TR-003` §4.5 places video precisely, and narrowly:

> **Correct for:** *"Technique that must be seen — micro-soldering, refrigerant recovery."*
> **Wrong for:** *"Step-by-step procedure a learner must follow mid-task."*
> **Evidence produced:** *"None."*

That third column is the one production briefs usually miss. `DS-11` follows from it: **statutory
and safety content is delivered in a mode that produces per-learner evidence**, and *"a video with
no check evidences attendance, not competence"*. So a training video is never a deliverable on its
own — it is a segment inside a module that ends in practice (`DS-08`) and prepares an assessment
item (`DS-04`).

**What is missing is everything between the approved storyboard and the accepted file.**

| Absent | Consequence |
|---|---|
| A duration and segmentation rule | A 22-minute "module video" that no technician watches to the end and that cannot be re-cut when one step changes |
| A language position in production terms | A supplier films in English and offers Bengali subtitles — which `HC-020` `VS-07` already identifies as failing the audience it exists for |
| A recording-conditions brief | A video of a technician working without the PPE `SP-030` requires, distributed to 200–400 people as the company's own instruction |
| A device and network target | 1080p files that stall on a congested cell and cannot be downloaded for a basement plant room |
| Accessibility deliverables in the quote | No captions, no transcript, and an `NFR-073` AA failure on the LMS |
| A reshoot and currency rule | A library that shows a UI two releases old and is trusted for the safety content that sits beside it |

**Consequence of absence (`CP-03`).** The most expensive content the programme produces, made
against no acceptance specification, teaching a workforce practices and screens that may be wrong
— with `HC-020` `O-02` already recording that **production capability, budget and presenters are
not identified anywhere.**

**What this file is not.** It is not the curriculum (`TR-002`), not the course design standard
(`TR-003`), not the customer-facing series (`MM-007`), not the animated explainers (`MM-008`), and
not the scripts — which live in the owning course pack.

---

## 2. Scope

**In scope.** The decision test for whether a video is made at all; the series inventory basis;
duration and segmentation; the language and voice position; on-screen text; recording conditions
including safety, PPE, environment and data; screen recording; the storyboard and approval gate;
accessibility deliverables; delivery, encoding and offline behaviour; currency, reshoot and
withdrawal; the deliverable specification; and rules `VT-01`…`VT-28`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Learning objectives, module structure, assessment, the storyboard template | [`TR-003`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) |
| Who takes what course | [`TR-002`](../08_Training_and_Enablement/08A_Framework/TR-002_Role_Based_Curriculum_Map.md) |
| Pass marks, attempts, certification | [`TR-004`](../08_Training_and_Enablement/08A_Framework/TR-004_Assessment_and_Certification_Policy.md) |
| The technical content being demonstrated | The owning `KB-` or `SP-` file (`TR-003` `LS-15`) |
| **Customer-facing how-to video** | [`MM-007`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) — different audience, different length, different distribution |
| Onboarding animation | [`MM-008`](MM-008_Animated_Explainer_Brief_Portal_Onboarding.md) |
| Screenshot capture and redaction | [`MM-002`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) — **§4.6 cites it for screen recording** |
| Encoding ladder, codecs, audio loudness, metadata, acceptance | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) §4.5, §4.6, §4.7, §4.11 |
| Bengali translation standard and voice pack | [`BN-002`](../11_Localisation_Bengali/BN-002_Bengali_Translation_Standard.md), [`BN-017`](../11_Localisation_Bengali/BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) |
| Naming, versioning, retention | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Video production supplier** | The acceptance specification attached to the purchase order | Before quoting |
| **L&D course author** | What to ask for on a storyboard's "Media required" line (`TR-003` §4.10) | Per module |
| **Technical Director / senior technicians (`R12`, `R13`)** | What they are being asked to demonstrate, and on what terms | Before a shoot |
| **HSE Lead** | The safety gate, and the authority to stop a shoot | Before and during |
| **Brand** | Wardrobe, environment, mark usage on screen | At review |
| **Localisation Lead** | The Bengali-filmed position and its production consequence | At planning |
| **Accessibility reviewer** | §4.7 — captions, transcript, description | At acceptance |
| **Finance / Procurement** | What "one video" actually costs once language and accessibility are line items | At sourcing |

---

## 4. Content

### 4.1 The decision test — is this a video at all?

**`VT-01`: a video is commissioned only where every answer is yes.** Otherwise the content is a
job aid (`TR-022`), a field reference card (`KB-016`), a sandbox exercise, or an article.

| # | Question | If no |
|---:|---|---|
| 1 | Is there a **physical technique that must be seen** to be learned? (`TR-003` §4.5) | Write it down |
| 2 | Would a photograph sequence or a diagram fail to carry it? | Use those — cheaper, translatable, editable |
| 3 | Is the learner watching **before** the task, not during it? (`DS-24`, `VS-02`) | A learner mid-task cannot scrub to step 7 |
| 4 | Is the subject **stable for at least two waves**? | It will be orphaned before it is watched |
| 5 | Is there an assessment item and an exercise this video prepares? (`DS-04`) | It is decoration |
| 6 | Is the reshoot cost understood and budgeted? (§4.9) | It will decay and stay |

| # | Rule |
|---|---|
| **VT-02** | **Video is for technique, not procedure.** The distinction is `TR-003` §4.5's and it is the single most useful sentence in this file: a procedure is a numbered list, a technique is a hand doing something a list cannot convey |
| **VT-03** | **A video never carries statutory or safety content alone.** `DS-11` requires per-learner evidence, so any safety video is paired with a check, a demonstration sign-off or an assessor observation (`TR-003` §4.5 "Practical demonstration — assessor sign-off") |
| **VT-04** | **A video never replaces a job aid.** `TR-022` job aids and `KB-016` field reference cards are what a technician actually consults at the bench; the video is what they watched last month |

### 4.2 Series inventory and its basis

**The inventory is not fixed here.** It is derived per course pack by applying §4.1 to each
storyboard's "Media required" line, and is enumerated per wave rather than estimated (`CP-11`).

| Series | Owning packs | Format | Typical subjects |
|---|---|---|---|
| **S1 — Technique demonstration** | [`TR-009`](../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md), `TR-010`, `TR-012` | 2–5 min, landscape | Component-level repair, refrigerant handling, ESD discipline, calibration use |
| **S2 — Safety and hazard** | `TR-009`, `TR-020`, all packs touching a hazard | 2–4 min, landscape, **HSE-gated** | Live electrical, battery handling, working at height, lifting, PPE |
| **S3 — Microlearning** | `TR-009`, [`TR-020`](../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) | **Under 3 min** (`DS-07`), **vertical** | One task, one job aid, one safety point — the `P02` and rider format |
| **S4 — System walkthrough** | Functional packs | 3–6 min, landscape, **screen recording** | A transaction demonstrated once before sandbox practice |
| **S5 — Train-the-trainer** | [`TR-023`](../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) | 5–8 min | Facilitation technique, not system content |

| # | Rule |
|---|---|
| **VT-05** | **S4 system walkthroughs are the highest-decay series and are commissioned last**, after the UI they show has stabilised. `TR-003` `DS-12`'s "teach the task and the decision, not the screen" applies with more force to video than to a screenshot, because a screenshot is replaced in minutes and a video is not |
| **VT-06** | **S2 safety videos are the highest-consequence and lowest-decay**, and are commissioned first. A refrigerant-recovery technique does not change with a release |
| **VT-07** | **Every video names the `SP-`, `KB-` or `MD-` file it teaches from** (`TR-003` `LS-15`) in its metadata and its transcript. A video with no governing source is unreviewable |

### 4.3 Duration and structure

| Unit | Duration | Rule |
|---|---|---|
| **Microlearning (S3)** | **Under 3 minutes** | `TR-003` `DS-07` |
| **Standard segment (S1, S2, S4)** | **2–5 minutes**, never over 6 | `DS-05` sets the segment at 5–8 minutes; video is the tightest of those |
| **Absolute ceiling** | **8 minutes** | `DS-09` — no unbroken presentation longer than 8 minutes in any mode |
| Opening | **First 10 seconds state what the viewer will be able to do** | `VS-04` pattern |
| Closing | **The practice that follows**, named | `DS-08` — every module ends with practice, not a summary |

| # | Rule |
|---|---|
| **VT-08** | **One technique per video.** A video covering two is two videos, and two videos can be re-shot independently when one changes |
| **VT-09** | **No title sequence, no music intro, no logo animation.** A 12-second brand opening on a 2-minute video watched between jobs is 10% of the runtime and 100% of the reason it is skipped |
| **VT-10** | **Chapters are marked** where a video exceeds 3 minutes, so a returning learner can reach the part they need |
| **VT-11** | The video is **cut so a single step can be replaced** without re-shooting the whole item — a shot list discipline, not an editing one (`VS-14`) |

### 4.4 Language and voice

| # | Rule |
|---|---|
| **VT-12** | **Bengali is authored and filmed, not translated and not subtitled** (`TR-003` `DS-17`, `HC-020` `VS-07`). An English video with Bengali captions fails the audience `PS-03` and `04-00` §P02 describe |
| **VT-13** | **The presenter is a Bengali-speaking practitioner**, not a presenter reading a translated script. `DS-17` requires content authored *"by a Bengali-speaking author with the domain"* — the same applies on camera, and a technician can tell within seconds |
| **VT-14** | **The English version is a separate production**, not a dub and not a subtitle track. Where budget forces a choice, **Bengali is produced and English is not** — which inverts the usual default deliberately |
| **VT-15** | Scripts are written for **speaking**: short sentences, one idea each, no stacked subordinate clauses (`DS-19`) |
| **VT-16** | **Codes, part numbers, model names, measurements, system field labels and error identifiers are never translated** (`DS-20`, `MX-01`), and are spoken as they are written |
| **VT-17** | **Safety narration is human-translated in context and re-approved by HSE after translation** (`DS-23`, `AU-06f`). A safety instruction that changed meaning in translation is the failure mode this rule exists for |
| **VT-18** | Numerals follow `VB-009` §5 / `BN-007`; **a figure never changes digit system between the two versions of the same item** (`DS-22`) |

### 4.5 On-screen text and graphics

| # | Rule |
|---|---|
| **VT-19** | **On-screen text meets the `VB-009` §3 Bengali floors measured at the L1 encoding rung**, not at the master resolution (`MM-001` `VE-10`). Text legible at 720p and illegible at 240p is a defect, and L2 is the default rung on mobile data |
| **VT-20** | Text sits inside a **10% safe area** on all sides and never in the lower third where a caption track will render |
| **VT-21** | **On-screen text never duplicates the narration**; it names the thing being shown — a part, a value, a torque figure — which is exactly what a caption cannot convey |
| **VT-22** | Graphics use the `MM-004` icon set and the `MM-003` diagram semantics where either applies. **A video does not invent a visual language** |
| **VT-23** | **No lower-third with a person's name and job title** unless that person has consented and the consent is recorded (`MM-009` §4.2), and the title is current — a lower-third dates a video faster than its content does |

### 4.6 Recording conditions

#### 4.6.1 Safety — the gate

| # | Rule |
|---|---|
| **VT-24** | **Everything filmed is compliant practice.** PPE correct and worn, tools correct, isolation performed, the SOP followed exactly. **A video is instruction: whatever it shows is what 200–400 people will do** |
| **VT-25** | **HSE approves the shot list before the shoot and reviews the cut before release** (`TR-003` `DS-26` gate 5). **HSE may stop a shoot**, and the authority is stated here so it is not negotiated on the day |
| **VT-26** | **No hazardous procedure is staged for camera at a level of risk the SOP would not accept.** Where a demonstration cannot be filmed safely, it is filmed on a de-energised or mock rig and **the video says so on screen** rather than implying live conditions |
| **VT-27** | Filming does not obstruct a working area, and **a live customer job is never the set** (`VT-30`) |

#### 4.6.2 Environment, data and people

| # | Rule |
|---|---|
| **VT-28** | **No live customer data, no live customer device, no customer premises** without written consent under `MM-009` §4.2. The default is a **staged bench with sandbox data** |
| **VT-29** | **Screens in frame are sandbox screens** (`MM-002` `SC-01`). A production screen in a video is the same disclosure as a production screenshot, running at 25 frames a second and impossible to redact after the fact |
| **VT-30** | **A live customer job is never filmed.** Consent obtained in the moment, from a customer waiting for a repair, is not freely given |
| **VT-31** | Everyone on camera has **recorded consent** (`MM-009` §4.2), including bystanders, and **consent is withdrawable** — which is why `VT-23` and §4.9 matter |
| **VT-32** | The set carries **no third-party branding, no competitor material, no unrelated brand-partner product, and no visible document** (`MM-002` §4.4.3) |
| **VT-33** | **Audio is recorded in conditions where speech survives a phone speaker in a workshop** (`MM-001` `AU-04`). Workshop ambience is authentic and is not an excuse for unintelligible narration |

#### 4.6.3 Screen recording (S4)

| # | Rule |
|---|---|
| **VT-34** | Screen recordings are captured from the **sandbox**, at the surface's own device class, following [`MM-002`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) §4.1–§4.4 in full — **including the redaction obligation, which cannot be discharged frame by frame and must therefore be discharged by not capturing** |
| **VT-35** | **No mouse trails, no click sound effects, no zoom-and-pan on a screen recording.** They are the three things that make a walkthrough harder to follow, not easier |
| **VT-36** | Cursor movement is deliberate and slow; **the pointer pauses before every click** so the viewer sees where it lands |
| **VT-37** | **UI labels spoken and shown match `UI-002`/`UI-003`** (`TR-003` `DS-16`, `HC-020` `VS-10`). A narrator inventing a label creates a synonym `CG-004` prohibits |

### 4.7 Accessibility deliverables

**Acceptance criteria, not extras** (`CG-011` §9, `MM-001` §4.7).

| Deliverable | Requirement | SC |
|---|---|---|
| **Captions** | **WebVTT, both languages, authored not auto-generated**, carrying speaker changes and meaningful non-speech sound | **1.2.2 (A)** |
| **Transcript** | A structured document with headings and the on-screen text included — usable as a text alternative | **1.2.3 (A)** |
| **Audio description or media alternative** | Where the picture carries information the narration does not | **1.2.3 (A)**, **1.2.5 (AA)** |
| Poster frame | A real frame from the first 5 seconds | `MM-001` `VE-07` |
| No auto-play with sound | Enforced by the LMS and by `P02` | `MM-001` `VE-08` |
| No flashing | Nothing flashes more than three times in any second | **2.3.1 (A)** |
| Captions burned in? | **Prohibited** (`MM-001` `AC-01`) | 1.4.5 |

| # | Rule |
|---|---|
| **VT-38** | **Captions are mandatory in both languages**, and the reason is operational as well as legal: **this workforce frequently watches without headphones, in noise, or in public** (`TR-003` §4.8, `HC-020` `VS-08`) |
| **VT-39** | **Automatic Bengali speech recognition is not accepted as a caption source** (`MM-001` `AC-02`). An inaccurate caption on a safety video is a hazard, and `CP-05` already prohibits machine translation on field-facing content |
| **VT-40** | **`AC-05` applies with full force here: where audio description would be needed, the correct fix is usually to change the narration.** A demonstration narrated as *"I am now removing the screw at the top left"* needs no description track. **This is cheaper, better and more accessible than adding one**, and it is a storyboard decision, not a post-production one |
| **VT-41** | The transcript is **indexed and searchable in the LMS**, which is how a technician finds the 40 seconds they need without watching 4 minutes |

### 4.8 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **ProRes 422 or DNxHD, 1920 × 1080, 25 fps**, with separated audio stems |
| **Delivery formats** | **H.264 High Profile ≤ L4.0** at the `MM-001` §4.5 ladder — L1 240p / L2 360p / L3 480p / L4 720p — **plus a progressive MP4 at L2 for offline download** |
| **Ceiling** | **720p. No 1080p or 4K delivery rung exists** (`MM-001` `VE-02`) |
| **Orientation** | **Landscape 16:9** for S1, S2, S4, S5 · **vertical 9:16** for S3 microlearning |
| **Duration** | S3 < 3 min · S1/S2/S4 2–5 min · S5 5–8 min · **absolute ceiling 8 min** |
| **Audio** | AAC-LC 128 kbps; **−16 LUFS integrated, true peak ≤ −1 dBTP** (`MM-001` `AU-03`); music ≥ 18 dB below speech or absent |
| **Colour** | Rec. 709 |
| **Captions** | **WebVTT, `bn` and `en`, separate files, authored** |
| **Transcript** | Structured document per language |
| **Poster** | Real frame from the first 5 s, PNG, 1280 × 720 |
| **Chapters** | WebVTT chapter file where > 3 min |
| **Metadata** | Title, language, duration, owning course and module (`TR-nnn-Mnn`), **governing `SP-`/`KB-` source** (`VT-07`), caption track IDs, release captured against for S4 |
| **Naming** | `MM-012` §4.3 |
| **Source** | **Project file, uncut footage, audio stems, graphics source** (`MM-001` `DL-02`) — a payment condition |
| **Evidence** | **HSE shot-list approval and cut review** (`VT-25`); **consent records** for every person on camera (`VT-31`); storyboard approval (`DS-25`) |

### 4.9 Currency, reshoot and withdrawal

| # | Rule |
|---|---|
| **VT-42** | **Every video is reviewed at each release affecting its subject** (`TR-024` `RL-04`, `HC-020` `VS-15`) |
| **VT-43** | **An orphaned video is withdrawn, not left.** A video showing a UI that no longer exists, or a practice that has changed, is worse than no video — and on safety content it is a hazard |
| **VT-44** | **The reshoot asymmetry is stated at commissioning, not discovered.** An article orphaned by a UI change is edited in minutes; a video needs a crew, a presenter, a location, a translation and a production cycle (`HC-020` `VS-15`). **This asymmetry is why §4.1 exists and why the library is deliberately small** |
| **VT-45** | **A safety video is re-reviewed by HSE annually even where nothing has changed** — the no-trigger rule `CG-012` §5.1 applies to instruction as it does to sources |
| **VT-46** | **Consent withdrawal by a person on camera triggers withdrawal or re-edit of the asset** (`MM-009` §4.2, `MM-012` §4.7). A video is not exempt because it is expensive |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`TR-003_Course_Design_Standard_and_Storyboard_Template.md`](../08_Training_and_Enablement/08A_Framework/TR-003_Course_Design_Standard_and_Storyboard_Template.md) | §4.5 the decision test, `DS-05`…`DS-11`, `DS-17`…`DS-23`, `DS-25`, `DS-26` — the design this file produces to |
| [`TR-001_Training_Strategy_and_Competency_Framework.md`](../08_Training_and_Enablement/08A_Framework/TR-001_Training_Strategy_and_Competency_Framework.md) · [`TR-002_Role_Based_Curriculum_Map.md`](../08_Training_and_Enablement/08A_Framework/TR-002_Role_Based_Curriculum_Map.md) · [`TR-004_Assessment_and_Certification_Policy.md`](../08_Training_and_Enablement/08A_Framework/TR-004_Assessment_and_Certification_Policy.md) | The framework, the audience and the evidence `VT-03` depends on |
| [`TR-009_Course_Pack_Field_Technician.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-009_Course_Pack_Field_Technician.md) · [`TR-020_Course_Pack_Rider_and_Logistics.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-020_Course_Pack_Rider_and_Logistics.md) · [`TR-023_Train_the_Trainer_and_Super_User_Kit.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-023_Train_the_Trainer_and_Super_User_Kit.md) | The packs commissioning S1, S2, S3 and S5 |
| [`TR-022_Job_Aid_and_Quick_Reference_Library.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-022_Job_Aid_and_Quick_Reference_Library.md) · [`KB-016_Technician_Field_Reference_Card_Set.md`](../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) | What `VT-04` says a video never replaces |
| [`TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) | `RL-04` — the release review behind `VT-42` |
| [`SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) · [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | The practices `VT-24`…`VT-26` require to be filmed correctly |
| [`SP-008_SOP_On_Site_Field_Service_Visit.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) · [`SP-010_SOP_Workshop_and_Depot_Repair.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) · [`SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | Governing sources for demonstrated technique (`VT-07`) |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | §4.5 ladder, §4.6 audio, §4.7 accessibility, §4.11 acceptance |
| [`MM-002_Screenshot_Annotation_and_Redaction_Standard.md`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) | §4.1–§4.4 applied to screen recording (`VT-34`) |
| [`MM-003_Diagram_and_Process_Map_Visual_Standard.md`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) · [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) | The visual language `VT-22` requires rather than invents |
| [`MM-007_Video_Production_Brief_Customer_How_To_Series.md`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) | The customer-facing counterpart; **shared supplier, different specification** |
| [`MM-009_Photography_Brief_Branches_Workshop_and_Field.md`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) | §4.2 consent, which `VT-31` and `VT-46` rely on |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, versioning, withdrawal on consent withdrawal |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-002_Bengali_Translation_Standard.md`](../11_Localisation_Bengali/BN-002_Bengali_Translation_Standard.md) · [`BN-016_Bengali_Help_and_Training_Content_Plan.md`](../11_Localisation_Bengali/BN-016_Bengali_Help_and_Training_Content_Plan.md) · [`BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md`](../11_Localisation_Bengali/BN-017_Bengali_Voice_IVR_and_Speech_Prompt_Pack.md) | On-screen text floors, translation standard, Bengali voice practice |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | §4.7 obligations and where they are verified |
| [`TS-002_Test_Data_Pack_and_Persona_Set.md`](../13_Test_and_Acceptance_Content/TS-002_Test_Data_Pack_and_Persona_Set.md) | The sandbox `VT-29` and `VT-34` require |
| [`HC-020_Video_Tutorial_Script_Library.md`](../09_Help_Centre_and_Self_Service/HC-020_Video_Tutorial_Script_Library.md) | `VS-02`…`VS-17`, whose reasoning this file adopts for a different audience |
| `M22` `FR-LMS-024`, `FR-LMS-025`, `FR-LMS-038` | Mobile delivery inside `P02` and the completion evidence `VT-03` depends on |
| `04-00` §P02, `PS-03`, `PS-08` | The device floor, Bengali default and the offline obligation behind `VT-12` and the L2 download |

| Depended on by |
|---|
| Every `TR` course pack with a media line · `M22` LMS content · `TR-024` release refresher · `MM-007` (shared supplier and crew) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave** during production; **annually** for the standard; **annually for every S2 safety item regardless of change** (`VT-45`) |
| Trigger for out-of-cycle review | A `TR-003` change · an SOP or safety-data change affecting a filmed technique · a release orphaning an S4 item · a device or network baseline change · a consent withdrawal · an accessibility finding |
| Owner | **Learning & Development with Brand**; **HSE owns the §4.6.1 gate and may stop a shoot** |
| Approver | Content Design Lead with HR Director (`TR-003` approver pattern) |
| Enforcement | `TR-003` `DS-25` storyboard gate; `DS-26` five review gates including HSE; `MM-001` §4.11 acceptance; `TR-024` `RL-04` release review |
| Effectiveness measure | **Videos withdrawn as orphaned per release** · **assessment pass rates on objectives a video prepares** · watch-through and, more importantly, **task performance after watching** |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No video production capability, budget, crew or presenters exist.** `HC-020` `O-02` records it for the customer series — *"44 productions in two languages is a programme, and it appears in no plan"* — and **this file adds the training series on top of it**, including safety content that cannot be produced by an untrained crew. The Master Index §7 Category 19 estimate is **specification only** | Content Design Lead and HR Director with Finance | **W2 — it is a budget question, not a content one** |
| **O-02** | **`TS-002` sandbox does not exist**, so S4 walkthroughs and every screen in frame have no lawful source (`VT-29`, `VT-34`). Recorded by `TR-003` `O-01`, `HC-002` `O-02`, `HC-020` `O-04`, `MM-001` `O-03` and `MM-002` `O-01` — **six files, one cause** | Test Lead with L&D | **W2 — blocking S4 entirely** |
| **O-03** | **Bengali-authoring and on-camera capability is unresourced.** `VT-13` requires a Bengali-speaking practitioner presenter with the domain; `TR-003` `O-03` records that Bengali authoring requires authors who are *"domain-competent **and** Bengali-native"* and that the capability gap is open. **A presenter is a scarcer version of the same person** | Localisation Lead with Technical Director | **W2 — gates `TR-009`** |
| **O-04** | **No HSE reviewer is named for content**, and §4.6.1 gives HSE authority to stop a shoot and to gate a release. `TR-003` `DS-26` gate 5 and `MM-005` `O-06` record the same gap. **A safety video with no HSE gate is the most dangerous artefact this category can produce** | HSE Lead with HR Director | **W2 — before any S2 item** |
| **O-05** | **No accessibility reviewer is named** for §4.7 — the **eighth** file to record this gap, after `TR-003` `O-02`, `HC-002` `O-04`, `HC-016` `O-04`, `MM-001` `O-06`, `MM-002` `O-04`, `MM-003` `O-04` and `MM-004` `O-03` | Content Design Lead | **W2** |
| **O-06** | **Whether `M22` supports segment-level tracking is unconfirmed** (`TR-003` `O-05`). §4.3's segmentation and `VT-10`'s chapters assume a learner can resume and can be targeted at a segment; **if tracking is course-level only, video length and structure should be reconsidered before production, not after** | CTO with L&D | **W2 — before the first commission** |
| **O-07** | **The offline video path in `P02` is unspecified.** `PS-08` requires 24-hour offline operation and `MM-001` `VE-04` requires every training video to be downloadable at L2; **no file states how a technician gets a video onto the device, how much storage is allowed, or how it is expired.** `OP-011` covers app release channels, not content payload | CTO with Mobile Engineering and L&D | **W2** |
| **O-08** | **The Bengali-only fallback in `VT-14` is a policy position taken by this file and not ratified.** It says that where budget forces a choice, Bengali is produced and English is not. That is consistent with `PS-03` and `CP-05` but **inverts the programme's usual English-source default and has not been approved by anyone** | HR Director with Localisation Lead and Content Design Lead | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.8; §7 added per category convention
- [x] **A six-question commissioning test that can return "do not make a video"**
- [x] `TR-003` §4.5's technique-not-procedure distinction carried through as the governing rule
- [x] **Video prohibited from carrying statutory or safety content alone, tied to `DS-11`'s per-learner evidence requirement**
- [x] Five series defined with their owning packs, and the highest-decay series identified and sequenced last
- [x] Duration bounded against `DS-05`/`DS-07`/`DS-09`, with no title sequence permitted
- [x] **Bengali authored and filmed, with the English version a separate production and the budget inversion stated explicitly**
- [x] Safety translation re-approved by HSE after translation (`DS-23`)
- [x] On-screen text required to meet Bengali floors **at the lowest encoding rung**, not at master resolution
- [x] **Recording conditions state that whatever is filmed is what 200–400 people will do, with HSE holding stop authority**
- [x] Live customer jobs, live customer data and production screens excluded, with the reason given for each
- [x] Screen recording bound to `MM-002` in full, including the observation that frame-by-frame redaction is impossible
- [x] **Accessibility deliverables listed with success criteria; captions authored not auto-generated; the narration-instead-of-audio-description position stated as the cheaper and better fix**
- [x] Reshoot asymmetry stated at commissioning, and consent withdrawal made a withdrawal trigger
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2; the outputs are Bengali-first
- [ ] **`O-01` no production capability or budget — outstanding; nothing can be filmed**
- [ ] **`O-02` `TS-002` absent — outstanding; S4 blocked**
- [ ] **`O-04` no HSE reviewer — outstanding; S2 safety series cannot be gated**
- [ ] **`O-08` the Bengali-only budget fallback is unratified — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and HR Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
