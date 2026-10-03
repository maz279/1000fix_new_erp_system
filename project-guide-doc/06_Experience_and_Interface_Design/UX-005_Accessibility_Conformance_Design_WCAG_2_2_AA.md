---
id: UX-005
title: Accessibility Conformance Design (WCAG 2.2 AA)
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Product Design
approver: Design Authority (constituted under GV-002)
standards_basis: >
  W3C WCAG 2.2 Level AA (W3C Recommendation) · W3C WCAG2ICT (Group Note, WCAG 2.2 edition,
  11 December 2025) for the four non-web applications · EN 301 549 (referenced) ·
  ISO 9241-171:2008 (software accessibility) · ISO/IEC 25010:2023 inclusivity
traces_to: >
  PGD-000 UX-005 · NFR-073 (restated to 2.2 AA by RQ-006 §3.7) · SWR-004 · UI-R4 ·
  PS-04 · CG-011 · UI-010 · TS-016 (and its findings O-01…O-05) ·
  GV-010 Q-05 (no accessibility reviewer) · URD §21 · audit findings RQA-12, U-09
depends_on: UX-001 (token-level conformance) · UX-003 (screen population) · UX-004 (interaction conformance) · UX-007 (Bengali)
verified_on: 2026-08-18
priority: P1
needed_by: W2
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-005 — Accessibility Conformance Design (WCAG 2.2 AA)

### Category 06 · Code `UX` · WCAG 2.2 AA · WCAG2ICT · EN 301 549

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `UX-005` exists in `PGD-000` Category 06.
> 2. **`PG-03` Count, do not consult.** Counted at **2026-08-18 14:45 (+06)**: **100 files cite
>    WCAG 2.1; 4 cite WCAG 2.2**, across the 621 demand-side files.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** Every criterion count and standard status carries
>    `verified_on: 2026-08-18` and is stated with its source in §17.

---

## 1. Purpose

`CG-011` and `UI-010` cover accessibility **text**. `TS-016` is an accessibility **test** pack that
its own audit records **cannot be executed, because no accessibility reviewer exists**. Between the
content standard and the test pack there is nothing: **no statement of what the design must do to
be conformant.** Testing without design guarantees late, expensive failure — retrofit costs 5–10×
design-time cost.

This document is that statement. It fixes the conformance target, applies it to **every** surface
including the four the current wording excludes, allocates each of the 55 Level A and AA success
criteria to a design-time or build-time owner — naming the eleven that no design and no build can
discharge — specifies the Bengali accessibility obligations that
no automated tool can discharge, and defines the conformance report the programme will have to
produce for enterprise and government clients.

It unblocks `TS-016` (which currently has no design to test against), `QA-008`, the `AR-012`
`FF-35` fitness function, and every portal release gate under `05-06` §11.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The conformance target, its version, its level and its scope statement |
| 2 | The **surface scope ruling** — the three Flutter applications the current wording leaves out |
| 3 | The nine criteria new in WCAG 2.2 and the one removed, with the design consequence of each |
| 4 | Allocation of all 55 A+AA criteria to a primary owner, and the subset requiring human evaluation |
| 5 | **Situational accessibility** — the dominant impairment class in this user base |
| 6 | Bengali accessibility obligations |
| 7 | The accessibility conformance report (ACR) and its evidence |
| 8 | The reviewer competency gap and what cannot proceed without it |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Accessibility **text** — alt text, error copy, plain language | `CG-011`, `UI-010` | Content |
| Token-level contrast, target size and focus values | `UX-001` §5 | This document states the criterion; `UX-001` carries the value |
| Interaction alternatives for drag and gesture | `UX-004` §5 | This document states the criterion; `UX-004` designs the path |
| Bengali typography metrics | `VB-009`, `UX-007` | This document states the accessibility consequence |
| **Executing** the tests | `TS-016`, `QA-008` | This document is what they test against |
| Physical and facility accessibility | Out of programme | Branch premises are not software |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Designers | The obligation per criterion at design time |
| Front-end and mobile engineers | Build-time obligations and the semantics contract |
| The accessibility reviewer *(unappointed — `Q-01`)* | The audit basis |
| QA (`TS-016`, `QA-008`) | The design baseline tests assert against |
| Commercial (`CO-003`) | The conformance claim made to corporate and government clients |
| Legal / compliance | The published conformance statement and its limits |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Status at 2026-08-18 | How this document uses it | Departure |
|---|---|---|---|
| **W3C WCAG 2.2** | W3C Recommendation. **86 success criteria — 31 A, 24 AA, 31 AAA.** Adds nine criteria to 2.1 and removes **4.1.1 Parsing** as obsolete | **The conformance target: Level AA = the 55 A + AA criteria** | None |
| **W3C WCAG2ICT** — Guidance on Applying WCAG 2 to Non-Web ICT | W3C **Group Note**; WCAG 2.2 edition published **11 December 2025**, coordinated with the EN 301 549 update | The basis for applying WCAG 2.2 to the **four Flutter applications**, which are non-web software | It is a Note, not a Recommendation — informative, not normative. Adopted by programme decision `UX-005-D-02` because the alternative is no standard at all for a third of the estate |
| **EN 301 549** — Accessibility requirements for ICT products and services | European standard; harmonised with WCAG2ICT in the current update cycle | **Referenced, not adopted.** Named because corporate and government procurement increasingly cites it, and because clause 11 (software) is the closest published equivalent to what WCAG2ICT gives us | Bangladesh has no equivalent instrument; §11.4 records the position |
| **W3C WCAG2Mobile** (MATF) — applying WCAG 2.2 to mobile applications | **In development**, not published | Monitored. **Not cited as a basis** — `PG-M4` forbids relying on an unpublished draft | Reviewed at each `RR-005` cycle |
| ISO 9241-171:2008 | Current | Software accessibility guidance for the non-web surfaces, alongside WCAG2ICT | Dated; used as supporting guidance only |
| ISO/IEC 25010:2023 | Current | **Inclusivity** is a 2023 sub-characteristic of interaction capability with no counterpart in the estate (`RQ-006` §4.4). §7 is its realisation | None |
| `RQ-006` §3.7 | Programme ruling | **WCAG 2.2 AA governs**, resolving `NFR-073` (2.1) against this document (2.2) | None |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `RQ-006` §3.7, §4.4 | The 2.2 ruling and the restated `NFR-073` |
| `CG-011` | Accessibility content standard: plain language, alt-text decision tree, error copy, Bengali content rules, the declared limitation §8.2 |
| `UI-010` | The accessibility text library — icon names, live regions, SR-only text, alt patterns |
| `TS-016` | The test pack; its scope table, its 21 scripts, and findings `O-01`…`O-05` |
| `VB-003` §3 | **Measured** contrast failures in the brand palette — the design constraint accessibility inherits |
| `VB-008` §2 | The three-signal rule |
| `VB-009` §3, §9 | Bengali size floors and the rendering-verification requirement |
| `URD` §21 | Core requirements, **situational accessibility**, and the 2.2 recommendation |
| `GV-010` §, `Q-05` | The three-lines assurance model and the missing reviewer |

### 2.3 Findings this document addresses

| Finding | Source | How addressed |
|---|---|---|
| `RQA-12` | `PGD-AUDIT-004` | 2.2 AA is realised here as a criteria matrix, not only recorded as a ruling |
| `U-09` | `URD` §26 | SC 2.5.7 is allocated to `UX-004` §5.3 and its evidence is defined here |
| `TS-016` `O-05` | `AUDIT-014` | **§4 rules `P02`, `P09` and `P11` in scope** via WCAG2ICT, closing the exclusion |
| `TS-016` `O-02` · `GV-010` `Q-05` | `AUDIT-014`, `GV-010` | §12 states precisely what cannot proceed without the reviewer, so the gap has a consequence rather than a note |
| `TS-016` `O-04` | `AUDIT-014` | §6.5 states `P06`'s position and its declared limitation |
| `CG-011` §8.2 | `CG-011` | The declared Bengali screen-reader limitation is carried into the conformance statement §11.2 rather than left in a content file |
| **New — `UXA-11`** | This category | **100 of 621 files cite WCAG 2.1; 4 cite 2.2.** The ruling in `RQ-006` §3.7 has not propagated. §3.3 states the remediation scope |
| **New — `UXA-12`** | This category | `TS-016` scopes **nine web portals** and explicitly excludes the three Flutter apps, so **the three surfaces with the most severe situational-impairment exposure are the three with no accessibility test** |

---

# 3. The Conformance Target

## 3.1 The statement

> **Every surface of the 1000FiX platform shall conform to WCAG 2.2 Level AA** — the 31 Level A and
> 24 Level AA success criteria, **55 in total** — with web surfaces conforming directly and the four
> Flutter applications conforming as interpreted by WCAG2ICT (WCAG 2.2 edition, 11 December 2025).

| Attribute | Value |
|---|---|
| Standard | WCAG 2.2 |
| Level | **AA** |
| Criteria in scope | **55** (31 A + 24 AA) |
| Scope | **All thirteen surfaces** — see §4 |
| Conformance claim type | Partial, per-surface, published as an ACR (§11) |
| Verification | Automated scan **plus** manual audit before each release (`05-06` §11) |

## 3.2 What changed from 2.1

| Change | Consequence for this programme |
|---|---|
| **+2 Level A**: 3.2.6 Consistent Help, 3.3.7 Redundant Entry | Both already promised by the `URD`; now testable. §5.1 |
| **+4 Level AA**: 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum), 3.3.8 Accessible Authentication (Minimum) | **2.5.7 is the one material gap** (`U-09`); the other three are largely met by existing commitments. §5.2 |
| **+3 Level AAA**: 2.4.12, 2.4.13, 3.3.9 | Out of scope at AA; 2.4.13 Focus Appearance is met anyway by the `UX-001` `focus.*` tokens |
| **−1**: **4.1.1 Parsing removed as obsolete** | A criterion the estate never cited. Recorded so that a future auditor does not report its absence as a gap |

> **Nothing already built is invalidated.** 2.2 is a superset of 2.1: a product conforming to 2.2 AA
> conforms to 2.1 AA. That is why `RQ-006` §3.7 could rule for 2.2 without a change request against
> delivered work.

## 3.3 `UXA-11` — the ruling has not propagated

Counted at 2026-08-18 14:45 (+06) across the 621 demand-side files:

| Citation | Files |
|---|---:|
| **WCAG 2.1** | **100** |
| **WCAG 2.2** | **4** |

`RQ-006` §3.7 ruled 2.2 AA on 2026-08-18. One hundred files — including `PS-04`, `NFR-073` in
`05-06`, every `UI-*` pack's surface-summary block, `CG-011`, `TS-016` and all twelve portal specs —
still state 2.1.

> **Remediation.** This is a **citation update, not a re-design**, because 2.2 is a superset. It is
> raised as a single coordinated change under `CG-006` and `GV-003`, not as 100 individual edits.
> Until it completes, **a surface released against a file citing 2.1 has been released against the
> wrong target**, and `TS-016` will test the wrong criteria set. Priority: **W1**.

---

# 4. Surface Scope — closing `TS-016` `O-05`

## 4.1 The gap

`PS-04` and `NFR-073` say *"WCAG 2.1 AA compliance on **all web portals**."* `TS-016` §1.3 reads
that literally and scopes **nine** surfaces, marking `P02`, `P09` and `P11` as *"Not covered by
`PS-04`"*.

**Those three are the technician application, the rider application and the field auditor
application.** They are used by:

| Persona | Situation | `URD` §21.3 |
|---|---|---|
| `A-02` Kabir | One hand occupied, direct sunlight, gloves, noise — **always** | Situational impairment |
| `A-03` Jasim | Helmet, gloves, motorcycle, rain | Situational impairment |
| `A-04` Rubel | Low literacy, Bengali only, both hands full | Permanent + situational |

> **`UXA-12`.** The three surfaces excluded from accessibility scope are the three with the highest
> situational-impairment exposure in the programme. A requirement written as "web portals" in 2024
> has, by 2026, excluded four applications from an obligation that applies to them more strongly
> than to any portal.

## 4.2 The ruling

> **`ACD-01`.** **All thirteen surfaces are in accessibility scope.** Web surfaces conform to
> WCAG 2.2 AA directly. The four Flutter applications conform to WCAG 2.2 AA **as interpreted by
> WCAG2ICT** for non-web software.

| Surface | Runtime | Conformance basis | Testable by `TS-016` today |
|---|---|---|:--:|
| `P01` web | Next.js | WCAG 2.2 AA | ● |
| `P01` app (APP-04) | Flutter | WCAG 2.2 AA via WCAG2ICT | **○ — added by `ACD-01`** |
| `P02` (APP-01) | Flutter | WCAG 2.2 AA via WCAG2ICT | **○ — added** |
| `P03` | Odoo OWL 2 | WCAG 2.2 AA | ● |
| `P04` | Next.js | WCAG 2.2 AA | ● |
| `P05` | Odoo Portal + Next.js | WCAG 2.2 AA | ● |
| `P06` | Metabase + Grafana | WCAG 2.2 AA **partial — declared** (§6.5) | ● (hardest — `O-04`) |
| `P07` | Next.js | WCAG 2.2 AA | ● |
| `P08` | Next.js | WCAG 2.2 AA | ● |
| `P09` (APP-02) | Flutter | WCAG 2.2 AA via WCAG2ICT | **○ — added** |
| `P10` | Next.js | WCAG 2.2 AA | ● |
| `P11` (APP-03) | Flutter | WCAG 2.2 AA via WCAG2ICT | **○ — added** |
| `P12` | Next.js | WCAG 2.2 AA | ● |

## 4.3 What WCAG2ICT changes for the four applications

WCAG2ICT reinterprets web-specific terms for non-web software. The substantive differences:

| WCAG term | Non-web reading | Consequence for `P02`, `P09`, `P11`, APP-04 |
|---|---|---|
| "web page" | **"non-web document" or "software"** | A criterion scoped to a page applies to a screen |
| "set of web pages" | "set of software programs" | Consistent navigation and consistent help apply across the app's screens |
| 2.4.1 Bypass Blocks | Applies where a repeated block exists | Native navigation structures generally satisfy it |
| 2.4.2 Page Titled | **Screen titled** | Every screen has a programmatically determinable title |
| 2.4.5 Multiple Ways | **Not applicable to a single software program** | Does not apply within the apps |
| 3.2.3 / 3.2.4 Consistent Navigation / Identification | Applies across the app's screens | `UX-002` §6.4 tab model satisfies it |
| 4.1.2 Name, Role, Value | Applies via the **platform accessibility API** | Flutter `Semantics` must be complete; a custom-painted widget with no semantics is a failure |
| 1.4.10 Reflow | Applies to the software's own resizing | 320 px equivalent + 200% text scaling without loss |

| # | Rule |
|---|---|
| `ACD-02` | Every Flutter widget in `fix_ui` carries complete `Semantics` — label, role, value, state. **A custom-painted widget with no semantics is a build failure** (`AC-02` in `UX-001` §8.8) |
| `ACD-03` | The apps are verified with **TalkBack** (Android, primary) and **VoiceOver** (iOS, secondary), in **Bengali and English** |
| `ACD-04` | Platform text scaling to **200%** must not break layout. `VB-009` MS-05 already requires this and the Bengali line box makes it harder |
| `ACD-05` | `TS-016` §1.3's scope table is superseded by §4.2. Raised as a content change under `CG-006`; **`TS-016` needs three new script sets** |

---

# 5. The Nine New Criteria

## 5.1 Level A additions

### SC 3.2.6 Consistent Help (A)

> Help mechanisms, where provided, occur in the same relative order on each page.

| Aspect | Position |
|---|---|
| Design obligation | `UX-002` §9.6 `NVR-77`: help is top-right of global chrome on **all thirteen surfaces** |
| Risk | One surface deviating. It is met by construction and broken by a single exception |
| Verification | Automated position assertion across surfaces; `CFM-04` inventory parity |
| Note | The criterion covers **contact details**, not only documentation. `NVR-79` requires human contact in one further action |

### SC 3.3.7 Redundant Entry (A)

> Information previously entered by the user is auto-populated or available for selection.

| Aspect | Position |
|---|---|
| Design obligation | `UX-004` §9 `IXN-75`…`IXN-79` |
| Already promised | `URD` user commitment #5 |
| Highest-risk surfaces | `P01` booking (three steps), `P04` bulk upload, `P07` registration |
| Common breach | A failed submission that clears the form (`IXN-79`) |
| Permitted exception | Re-entry for security — a payment PIN, a step-up code — **stated in the screen record** (`IXN-77`) |

## 5.2 Level AA additions

### SC 2.4.11 Focus Not Obscured (Minimum) (AA)

> When a user-interface component receives keyboard focus, the component is not entirely hidden
> due to author-created content.

| Aspect | Position |
|---|---|
| Design obligation | `UX-001` `FOC-04`, `UX-002` `NVR-15`, `UX-004` `IXN-55` |
| **Highest-risk surface** | **`P03`.** Fourteen workspaces with a fixed header (≤ 96 px) and a fixed action bar create exactly the geometry this criterion addresses |
| Mechanism | Sticky regions declare their height; scroll-into-view compensates |
| Verification | `CFM-06`, automated, every `P03` build |

### SC 2.5.7 Dragging Movements (AA)

> All functionality that uses a dragging movement can be achieved by a single pointer without
> dragging, unless dragging is essential.

| Aspect | Position |
|---|---|
| **The one material gap** | Identified in `URD` §21.4 and audit `U-09`; unresolved until now |
| Design obligation | `UX-004` §5.3 — **every drag in the estate enumerated with a single-pointer and a keyboard path** |
| "Essential" claim | **Not available.** Assignment, transfer and reordering are data changes, not essential drags |
| Secondary benefit | Single-pointer selection is faster for bulk, which the < 10-minute morning dispatch target requires (`IXN-26`) |
| Verification | `IX-D1` — **manual and exhaustive**; a scanner cannot detect the presence of an alternative |

### SC 2.5.8 Target Size (Minimum) (AA)

> Targets have an area of at least 24 by 24 CSS pixels, with stated exceptions.

| Aspect | Position |
|---|---|
| Design obligation | `UX-001` §5.6: `size.target.min` 24 px (floor), `size.target.comfortable` 44 px (programme standard), `size.target.field` 56 px |
| Position | **Exceeded by policy.** The `URD` §19.3 44 px standard already surpasses AA; 2.2 formalises the floor |
| Residual risk | Dense `P03` tables at 1366×600 — inline row actions can fall below 24 px when Bengali row height compresses padding. `CFM-03` + `CFM-08` together catch it |
| Verification | `CFM-03`, automated |

### SC 3.3.8 Accessible Authentication (Minimum) (AA)

> A cognitive function test is not required for any step in an authentication process, unless an
> alternative, a mechanism to assist, object recognition, or personal content is available.

| Aspect | Position |
|---|---|
| Design obligation | Utility archetypes 1, 2 and 4 (`UX-003` §5.6), reviewed before any surface ships (`SIR-15`) |
| Prohibited | Puzzle CAPTCHA · transcription CAPTCHA · memorised-answer security questions · blocking paste into an OTP field |
| Required | OTP fields accept **paste and autofill**; password fields accept paste and support password managers; biometric login where the platform offers it |
| Highest-risk audiences | `A-01` Abdul (62, low tech literacy, Bengali only) and every technician logging in with gloves |
| Note | `M29` bot protection (`NFR-068`) must not be implemented as a puzzle CAPTCHA. **Raised to `SC-004`** |

## 5.3 The removal — 4.1.1 Parsing

Removed from WCAG 2.2 as obsolete: modern browsers handle malformed markup consistently, so the
criterion no longer distinguished accessible from inaccessible content.

| # | Rule |
|---|---|
| `ACD-06` | 4.1.1 is **not** part of the conformance target and its absence is not a gap. Recorded because a reviewer using a 2.1 checklist against a 2.2 claim will otherwise raise it |
| `ACD-07` | Valid markup remains a **build-quality** requirement under `BE-*`, not an accessibility criterion |

---

# 6. Allocation of the 55 Criteria

## 6.1 The allocation, counted

**Regenerated by counting the owner column of all 55 rows in §6.2–§6.4 immediately before issue
(`PG-M10`), not by arithmetic on an earlier draft.**

| Primary owner | What it means | Count |
|---|---|---:|
| **D — Design-time** | Satisfied or failed by a design decision before code exists | **44** |
| **B — Build-time** | Satisfied by implementation of a correct design | **11** |
| | **Total** | **55** |

**Of those 55, 11 additionally require test-time verification** and are marked **`+ T`** in
§6.2–§6.4. These are the criteria a correct design and a correct build can still fail, because what
they require is a *judgement* — whether an alternative text is useful, whether a focus order permits
the task, whether an error message says something actionable.

| Criterion | Why design and build cannot assure it |
|---|---|
| 1.1.1 Non-text Content | A scanner finds a missing `alt`; only a person finds an `alt` that says "image1" |
| 1.3.1 Info and Relationships | Correct markup can still express the wrong structure |
| **1.4.1 Use of Colour** | Colour-only signalling that the label happens not to repeat |
| 2.4.3 Focus Order | A valid order can still make a task impossible |
| 2.4.4 Link Purpose · 2.4.6 Headings and Labels | Present, but uninformative |
| 3.1.2 Language of Parts | A `lang` attribute can be present and wrong |
| 3.3.1 Error Identification · 3.3.3 Error Suggestion | An error can be identified and still tell the user nothing |
| 4.1.2 Name, Role, Value · 4.1.3 Status Messages | Complete semantics that announce the wrong thing, or at the wrong moment |

> **These 11 are why `TS-016` exists and why `UX-005` `Q-01` blocks.** No amount of design rigour
> discharges them, and no automated scanner discharges them either — §10 states what each method can
> and cannot find.

## 6.2 Principle 1 — Perceivable

| SC | Level | Owner | Design obligation | Where |
|---|:--:|:--:|---|---|
| 1.1.1 Non-text Content | A | D + T | Alt-text decision tree; icon accessible names; decorative marking | `CG-011` §4, `VB-007` §8, `UI-010` §3.4 |
| 1.2.1 Audio-only / Video-only | A | D | Transcripts for `HC-020` video tutorials and `BN-017` IVR prompts | `HC-020`, `BN-017` |
| 1.2.2 Captions (Prerecorded) | A | D | Captions on every training and help video, **in Bengali** | `CH-*`, `HC-020` |
| 1.2.3 Audio Description or Alternative | A | D | Text alternative for procedural video | `HC-020` |
| 1.2.4 Captions (Live) | AA | D | Applies to live training webinars only; **not to voice calls** | `CH-*` |
| 1.2.5 Audio Description | AA | D | Procedural video | `HC-020` |
| 1.3.1 Info and Relationships | A | B + T | Heading structure and focus order declared in every screen record | `SIR-21` |
| 1.3.2 Meaningful Sequence | A | D | Reading order = visual order; both languages are LTR | `UX-004` `IXN-53` |
| 1.3.3 Sensory Characteristics | A | D | Never "the red rows" — always "the breached rows, shown in red" | `VB-008` TS-04, `CG-011` |
| 1.3.4 Orientation | AA | D | Functional in portrait and landscape | `URD` §19.3 |
| 1.3.5 Identify Input Purpose | AA | B | Autocomplete tokens on personal-data fields; also serves 3.3.7 | `UI-003` |
| 1.4.1 Use of Colour | A | D + T | **The three-signal rule** — colour + glyph + label | `VB-008` §2, `CFM-09` |
| 1.4.2 Audio Control | A | D | No auto-playing audio anywhere | — |
| 1.4.3 Contrast (Minimum) | AA | D | Every token pair measured; brand blue prohibited for text | `UX-001` §5.4, `CFM-02` |
| 1.4.4 Resize Text | AA | D | 200% without loss; **Bengali line box makes this harder** | `VB-009` MS-05, `LAY-04` |
| 1.4.5 Images of Text | AA | D | No text in images; **especially none in Bengali** — it cannot be resized, translated or read | `MM-*` |
| 1.4.10 Reflow | AA | D | 320 px, no horizontal scroll, any surface | `LAY-04`, `SIR-20` |
| 1.4.11 Non-text Contrast | AA | D | Borders, focus rings, status indicators ≥ 3:1. **`#39B1DF` at 2.46:1 fails** | `VB-003` BC-01, `TKN-14` |
| 1.4.12 Text Spacing | AA | D | Layout survives the WCAG spacing adjustment. **Bengali layouts commonly fail this** | `VB-009` LH-06 |
| 1.4.13 Content on Hover or Focus | AA | D | Dismissible, hoverable, persistent | `VB-007` AC-07, `IXN-07` |

## 6.3 Principle 2 — Operable

| SC | Level | Owner | Design obligation | Where |
|---|:--:|:--:|---|---|
| 2.1.1 Keyboard | A | D | **Every action has a keyboard path** | `UX-004` `IXN-01`, §6 |
| 2.1.2 No Keyboard Trap | A | B | Modal and drawer focus management | `IXN-56` |
| 2.1.4 Character Key Shortcuts | A | D | Remappable, suppressible, inactive in text inputs | `IXN-48`, `IXN-49` |
| 2.2.1 Timing Adjustable | A | D | **No form times out and discards data** without warning and extension | `IXN-47`, `NFR-069` |
| 2.2.2 Pause, Stop, Hide | A | D | Nothing auto-advances > 5 s without a control | `IXN-98` |
| 2.3.1 Three Flashes | A | D | Nothing flashes | — |
| 2.4.1 Bypass Blocks | A | B | Skip-to-content first focusable | `IXN-58` |
| 2.4.2 Page Titled | A | B | Unique, descriptive; **screen titled** on the apps | `ACD-02` |
| 2.4.3 Focus Order | A | D + T | Declared per screen record | `SIR-21`, `IXN-53` |
| 2.4.4 Link Purpose (In Context) | A | D + T | No "click here"; link text carries purpose | `CG-011` §7.1 |
| 2.4.5 Multiple Ways | AA | D | Navigation **and** global search on every surface | `UX-002` §8, `NVR-47` |
| 2.4.6 Headings and Labels | AA | D + T | Descriptive; every input has a visible label | `UI-003`, `CG-011` §6 |
| 2.4.7 Focus Visible | AA | D | `focus.*` tokens; `outline:none` is a build failure | `UX-001` §5.9, `CFM-06` |
| **2.4.11 Focus Not Obscured (Min)** | AA | D | Sticky chrome declares height | §5.2, `FOC-04` |
| 2.5.1 Pointer Gestures | A | D | No path-based or multipoint gesture is ever the only way | `IXN-17` |
| 2.5.2 Pointer Cancellation | A | B | Nothing commits on down-event | `IXN-03`, `IX-P1` |
| 2.5.3 Label in Name | A | D | Accessible name contains the visible label | `VB-006` DS-11 |
| 2.5.4 Motion Actuation | A | D | **No shake, no tilt** — a technician on a motorcycle triggers them | `IXN-20` |
| **2.5.7 Dragging Movements** | AA | D | Three paths for every drag | `UX-004` §5.3 |
| **2.5.8 Target Size (Minimum)** | AA | D | 24 px floor, 44 px standard, 56 px field | `UX-001` §5.6 |

## 6.4 Principles 3 and 4 — Understandable, Robust

| SC | Level | Owner | Design obligation | Where |
|---|:--:|:--:|---|---|
| 3.1.1 Language of Page | A | B | `lang` on the document, per locale | `BN-005` |
| 3.1.2 Language of Parts | AA | B + T | **`lang` on every script change** — without it a reader pronounces "Mushak" with Bengali phonology | `VB-009` MX-04 |
| 3.2.1 On Focus | A | B | Focus never changes context | — |
| 3.2.2 On Input | A | D | Input never changes context without warning | `IXN-57` |
| 3.2.3 Consistent Navigation | AA | D | Global chrome identical on thirteen surfaces | `UX-002` §6.1, `NVR-01` |
| 3.2.4 Consistent Identification | AA | D | Same function, same name and icon everywhere | `VB-007` PM-05 |
| **3.2.6 Consistent Help** | A | D | Help top-right, all thirteen surfaces | §5.1, `NVR-77` |
| 3.3.1 Error Identification | A | D + T | Errors identified in text, adjacent to the field | `UI-004`, `IXN-44` |
| 3.3.2 Labels or Instructions | A | D | Visible label on every input; placeholder is never the label | `UI-003`, `C-11` |
| 3.3.3 Error Suggestion | AA | D + T | Every error says what to do next | `NFR-078`, `IXN-45` |
| 3.3.4 Error Prevention (Legal, Financial, Data) | AA | D | Reversible, checked, or confirmed for money, custody and legal actions | `IXN-39`, `IXN-41` |
| **3.3.7 Redundant Entry** | A | D | Never asked twice | §5.1, `UX-004` §9 |
| **3.3.8 Accessible Authentication (Min)** | AA | D | No cognitive-function test; paste and autofill permitted | §5.2 |
| 4.1.2 Name, Role, Value | A | B + T | Complete semantics; **`Semantics` on every Flutter widget** | `ACD-02` |
| 4.1.3 Status Messages | AA | B + T | Live regions for every state change that matters | `UI-010` §3.2, `IXN-59` |

> **4.1.1 Parsing is absent from this table because WCAG 2.2 removed it** (§5.3).

## 6.5 `P06` — the declared partial conformance

`TS-016` `O-04` already records `P06` as the hardest surface. Metabase and Grafana are third-party
and expose theming, not markup.

| Aspect | Position |
|---|---|
| Fully controllable | Colour (via `chart.*` tokens), chart series encoding, direct labelling, embedding chrome |
| Partially controllable | Type scale, focus order within the vendor's widgets, keyboard operation of vendor controls |
| Not controllable | The vendor's internal semantics and ARIA implementation |
| **Position** | **Partial conformance, declared per release** under `UX-001` `DSY-02`, with the specific unmet criteria named |
| Compensating control | **Every `P06` dashboard has an accessible tabular equivalent**, exportable and screen-reader navigable. This is `ACD-08` and it is not optional |

| # | Rule |
|---|---|
| `ACD-08` | No analytical content exists only as a chart. Every board offers the underlying table |
| `ACD-09` | The partial conformance is stated in the ACR (§11) with the criteria named — **an undeclared partial conformance is a false claim** |
| `ACD-10` | Vendor accessibility is re-assessed at every major version upgrade, and the assessment is an `RR-005` register entry |

---

# 7. Situational Accessibility — the dominant class

`URD` §21.3 makes the point that the rest of the estate then forgets: **the most common impairments
in this user base are situational, not permanent — and they are constant.**

| Situation | Who | Frequency | Design response | Criterion it also serves |
|---|---|---|---|---|
| One hand occupied | Every field technician | **Always** | Thumb-reach primaries; no two-handed gesture; one-handed completion of every primary flow | 2.5.1, 2.5.8 |
| Direct sunlight | Field and rider | Most of the day | `high-contrast` theme; large type; no thin weights; no low-contrast decoration | 1.4.3, 1.4.11 |
| Gloves, wet hands | Riders, technicians in rain | Daily | `size.target.field` 56 px; scan and tap over typing | 2.5.8 |
| Noise | Branch counters, street | Continuous | Never sound alone; haptic + visual + audible for scans | 1.4.2, `IXN-65` |
| Low literacy | Store keepers, riders, some technicians and customers | Structural | Icons **paired with** Bengali text; scan-first; voice input | 1.1.1, 3.1.5 (AAA, adopted) |
| Low-end device on 3G | Most field and customer users | Structural | Payload discipline; graceful degradation | 1.4.4, `NFR-081` |
| Helmet, motorcycle | Riders | Daily | Largest type in the estate; 3 tabs; no motion actuation | 2.5.4, `NVR-33` |

| # | Rule |
|---|---|
| `ACD-11` | **Situational accessibility is designed for by default, not as an accommodation.** The `P02` and `P09` field type scale (`type.field.body` 17 px, `type.field.safety` 19 px) exists for this reason and is not compressible |
| `ACD-12` | Every field prototype is evaluated **in the condition** — outdoors, in sunlight, with gloves, one-handed (`IXN-83`, `UX-008` §7) |
| `ACD-13` | ISO/IEC 25010:2023 **inclusivity** is measured by these seven situations, since the estate has no other instrument for it (`RQ-006` §4.4) |

---

# 8. Bengali Accessibility

**The obligations no automated tool discharges**, and the reason `TS-016` §1.1's last two rows
exist.

| # | Rule | Basis |
|---|---|---|
| `ACD-14` | Every script change carries `lang` (SC 3.1.2). Without it, a screen reader applies Bengali phonology to `Mushak 6.3`, `bKash` and `SR-2026-114882` | `VB-009` MX-04 |
| `ACD-15` | Bengali screen-reader behaviour is verified with **real assistive technology in Bengali** — TalkBack Bengali on Android, NVDA/JAWS with a Bengali voice on Windows — before each portal release | `CG-011` §8.1, `TS-016` §1.1 |
| `ACD-16` | **Numeral reading is verified.** A Bengali numeral read as an English one, or the reverse, corrupts an amount or an identifier | `BN-007` §3, `TS-016` |
| `ACD-17` | Conjunct rendering is verified on the reference device at rank 1 and rank 2 faces. A conjunct rendered as a box is a 1.1.1 failure with no alt text available | `VB-009` §7, MM-04 |
| `ACD-18` | Bengali size floors are accessibility floors, not preferences: **14 px absolute screen, 8 pt absolute print** | `VB-009` MS-01 |
| `ACD-19` | SC 1.4.12 Text Spacing is verified **in Bengali**, because Bengali layouts commonly fail it | `VB-009` LH-06 |
| `ACD-20` | **The bilingual trap:** a screen that passes in English is not tested. Every accessibility test runs in **both** languages (`CG-011` §8.3) |

### 8.1 The declared limitation

`CG-011` §8.2 records a known limitation in Bengali assistive-technology support. **It is carried
into the conformance statement (§11.2) rather than left inside a content file**, because a
limitation a client cannot see has not been declared.

> **`ACD-21`.** Where Bengali assistive-technology support is materially weaker than English, the
> ACR states **which criteria are affected, on which surface, with which technology, and what
> compensating measure applies.** A general statement that "Bengali support varies" is not a
> declaration.

---

# 9. Design-Time Gates

Accessibility is checked at four points, and **the earliest three are cheaper than the fourth by an
order of magnitude.**

| Gate | When | Checks | Owner |
|:--:|---|---|---|
| **G1 — Token** | Design-system release | Contrast (`CFM-02`), target size (`CFM-03`), focus (`CFM-06`), greyscale (`CFM-09`) | Design System Lead |
| **G2 — Screen** | Before a screen enters build | All six data states; heading structure; focus order; Bengali risk; criteria list in the screen record | Designer + accessibility reviewer |
| **G3 — Build** | Every CI run | `FF-35` axe-core; `CFM-01`…`CFM-12`; `IX-*` automated subset | Engineering |
| **G4 — Release** | Before each portal release | `TS-016` automated scan **plus manual audit**, both languages | Accessibility reviewer |

| # | Rule |
|---|---|
| `ACD-22` | **A screen without a completed G2 does not enter build.** This is the gate that prevents retrofit |
| `ACD-23` | G3 blocks on violations (`AR-012` `FF-35`); it does not warn |
| `ACD-24` | G4 cannot be discharged by G3. **An automated scan finds a missing `alt`; only a person finds an `alt` that says "image1"** (`TS-016` §1.1) |

---

# 10. Verification — what each method can and cannot find

| Method | Finds | Cannot find |
|---|---|---|
| Automated scan (axe-core, `FF-35`) | Missing alt, computed contrast, missing labels, missing heading levels, unfocusable elements, missing error regions | Whether the alt is useful; whether focus order permits the task; whether colour is the sole signal in a way the label does not repeat |
| Token and build checks (`CFM-01`…`CFM-12`) | Systemic failures across all surfaces at once | Anything composed incorrectly from correct parts |
| Manual audit | Focus-order usability, alt quality, error-message usefulness, colour-only signalling | Whether a real assisted user can complete the task |
| **Assisted-user testing** | **Task completion by a real user with assistive technology, in Bengali** | Nothing else finds this |
| Field-condition testing | Sunlight, gloves, one hand, weak signal | — |

| # | Rule |
|---|---|
| `ACD-25` | All five run. Dropping the last two is the standard cost saving and the standard cause of a failed conformance claim |
| `ACD-26` | Assisted-user testing is scheduled per wave gate (`GV-009`), not per release, because participant recruitment has a lead time |

---

# 11. The Accessibility Conformance Report

## 11.1 Why one is needed

Corporate and government clients (`P04`, 500–2,000 users) increasingly require an accessibility
conformance statement in procurement, and `CO-003` acceptance will be asked for one. **The
programme currently cannot produce it for any surface.**

## 11.2 Structure

| Section | Content |
|---|---|
| 1 | Product, version, date, evaluation methods |
| 2 | Standards applied: **WCAG 2.2 AA**; WCAG2ICT for the four applications |
| 3 | **Per-criterion table** — all 55, each Supports / Partially Supports / Does Not Support / Not Applicable, with remarks |
| 4 | **Per-surface** conformance, since thirteen surfaces do not conform identically |
| 5 | **Declared limitations** — `P06` partial (§6.5); Bengali assistive technology (§8.1) |
| 6 | Evaluation evidence: scan reports, audit reports, assisted-user session records |
| 7 | Remediation plan with dates for anything below Supports |
| 8 | Evaluator identity and **independence class** (`GV-010`) |

| # | Rule |
|---|---|
| `ACD-27` | A criterion is marked **Supports** only with evidence from a method capable of finding its failure mode (§10). An automated scan cannot evidence 1.1.1, 2.4.3, 3.3.3 or any test-only criterion |
| `ACD-28` | The ACR is **per surface and per release**. One statement for "the platform" would be false for at least one surface |
| `ACD-29` | The evaluator's independence class is stated. `GV-010` records **29 of 29 audit reports at independence class I0** — self-assessment. An I0 accessibility claim must say so |

## 11.3 Publication

| # | Rule |
|---|---|
| `ACD-30` | The current ACR for each customer-facing surface is published and linked from the accessibility statement in the footer, in Bengali and English |
| `ACD-31` | The statement names a **contact route for accessibility problems** and a response commitment. A statement with no feedback channel is decoration |

## 11.4 The Bangladesh position

Stated because it will be asked, and because assuming an obligation exists is as damaging as
assuming none does.

| # | Position |
|---|---|
| `ACD-32` | Bangladesh has no statutory instrument imposing WCAG on private-sector software equivalent to EN 301 549 or Section 508. **The programme's obligation is contractual and reputational, not statutory** — it arises from `PS-04`, `NFR-073` and `CO-003` |
| `ACD-33` | Government and development-partner clients frequently import donor procurement standards that **do** cite WCAG or EN 301 549. The conformance target is set to meet those, not to the local minimum |
| `ACD-34` | This position is reviewed at each `RR-005` cycle. A statutory change is a `GV-005` risk trigger, not a surprise |

---

# 12. The Reviewer Gap — what cannot proceed

`TS-016` `O-02` and `GV-010` `Q-05` both record that **no accessibility reviewer exists.** This is
not a resourcing note; it has specific, nameable consequences.

| Blocked | Consequence |
|---|---|
| Gate **G2** (§9) | **No screen can complete design review.** 148 F2 wireframes have no approver |
| Gate **G4** (§9) | `TS-016`'s 21 scripts cannot be executed; no portal can pass `05-06` §11 |
| `UX-001` §10.1 | No component's `a11y` block can be approved; **68 components** are blocked at contract level |
| The ACR (§11) | Cannot be produced; `CO-003` acceptance and `P04` procurement are exposed |
| Assisted-user testing (§10) | Requires a facilitator competent in Bengali assistive technology |

| # | Rule |
|---|---|
| `ACD-35` | The competency required is: WCAG 2.2 audit experience, **Bengali-language assistive-technology fluency**, and mobile (TalkBack/VoiceOver) capability. It is unlikely to be one person; §12.1 states the minimum viable arrangement |
| `ACD-36` | Until appointed, **every accessibility status in the estate is unevidenced**, and any surface released is released without the manual half of `05-06` §11. This is stated in `GV-005` as a risk with a named owner, not carried as an open question |

## 12.1 Minimum viable arrangement

| Role | Source | Wave |
|---|---|---|
| Lead accessibility reviewer | External specialist, retained | **W0** |
| Bengali assisted tester | Recruited from the local disability community; trained on the product | **W1** |
| Internal accessibility champion per surface team | Trained internally; performs G2 pre-review | W1 |
| Assisted-user participant panel | Recruited with `UX-008` §4 | W2 |

> **The external lead is the only part that must be in place before W1**, because G2 blocks 148
> wireframes and 68 component contracts. The rest can ramp.

---

# 13. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-005-D-01` | Conformance version | (a) 2.1 AA per `NFR-073`; (b) **2.2 AA** | **(b)** | `RQ-006` §3.7 ruled it; superset, invalidates nothing; the four new AA criteria are material for gloved field use and low-literacy customers | 100 files need a citation update (`UXA-11`) |
| `UX-005-D-02` | Basis for the four Flutter apps | (a) exclude, per `PS-04` "web portals"; (b) **WCAG 2.2 AA via WCAG2ICT**; (c) invent a standard | **(b)** | The excluded surfaces have the highest situational-impairment exposure. WCAG2ICT is informative but is the only published interpretation | `TS-016` needs three new script sets (`ACD-05`) |
| `UX-005-D-03` | `P06` conformance | (a) claim full; (b) **declared partial + tabular equivalents** | **(b)** | Vendor semantics are not controllable; claiming full would be false | `ACD-08` tabular equivalent on every board |
| `UX-005-D-04` | EN 301 549 | (a) adopt as a target; (b) **reference only** | **(b)** | No Bangladeshi obligation; adopting a second target creates the same two-live-targets defect `RQA-12` found | Reviewed per `RR-005`; `ACD-33` covers donor procurement |
| `UX-005-D-05` | WCAG2Mobile | (a) adopt the draft; (b) **monitor** | **(b)** | Unpublished; `PG-M4` forbids relying on a draft | Re-reviewed at each `RR-005` cycle |
| `UX-005-D-06` | Reviewer sourcing | (a) internal training only; (b) **external lead + internal champions + Bengali assisted tester** | **(b)** | Internal training cannot produce Bengali AT fluency in the W1 window | Retained cost; §12.1 |

---

# 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who is the accessibility reviewer?** Open in `GV-010` `Q-05`, `TS-016` `O-02` and `UX-001` `Q-01`. Three documents now depend on the same unfilled role | CTO | **W0 — blocking** | §12 — G2, G4, 68 component contracts, 148 wireframes, the ACR |
| `Q-02` | Who owns the `UXA-11` citation update across 100 files? | Content Design Lead + `GV-003` | **W1** | Correct test target for every surface |
| `Q-03` | Does `M29` bot protection (`NFR-068`) use a puzzle CAPTCHA? If so it fails SC 3.3.8 | Security Architect | **W1** | Utility archetypes 1, 2, 4 |
| `Q-04` | Which Bengali screen readers are in the verification matrix, and are Bengali voices available for NVDA/JAWS? | Localisation Lead + accessibility reviewer | W2 | `ACD-15`, `ACD-21` |
| `Q-05` | Is `TS-016` re-scoped to thirteen surfaces, and who writes the three Flutter script sets? | QA Lead | **W2** | `ACD-05`, `UXA-12` |
| `Q-06` | Do `P04` contracts already commit to an accessibility standard? If a signed contract cites one, it governs | Commercial (`CO-*`) | W1 | §11, `UX-005-D-04` |

---

# 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | The conformance target states version, level, criterion count and scope | §3.1 — 55 of 86 |
| `AC-02` | Every surface is in scope, and the exclusion of the four applications is closed with a named basis | §4, `ACD-01`, `ACD-02` |
| `AC-03` | All nine criteria new in 2.2 have a design obligation and an owner; the removal of 4.1.1 is recorded | §5 |
| `AC-04` | All 55 A+AA criteria carry a primary owner, and the roll-up is regenerated by counting the rows | §6.1 — **44 D + 11 B = 55 ✓**, of which **11** additionally carry `+ T` |
| `AC-05` | Situational accessibility is specified as a first-class design input | §7 |
| `AC-06` | Bengali obligations are stated with a declared limitation carried into the conformance statement | §8 |
| `AC-07` | An ACR structure exists that a client can be given | §11 |
| `AC-08` | The reviewer gap has stated, specific consequences rather than a note | §12 |

**Definition of done.** Complete when every criterion is met, `Q-01` is filled, the `UXA-11`
citation update is raised as a single change, `TS-016` is re-scoped, and `PGD-000`'s `UX-005` row is
updated with a fresh enumeration timestamp.

---

# 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-006` §3.7, §4.4 | `NFR-073` restated to 2.2 AA |
| Upstream | `UX-001` §5 | Token-level conformance — the floor |
| Upstream | `UX-004` §5 | Interaction conformance — SC 2.5.x |
| Upstream | `CG-011`, `UI-010` | Accessibility content |
| Downstream | **`TS-016`** | The design baseline it tests; re-scoped by `ACD-05` |
| Downstream | **`QA-008`** | Accessibility testing derives from here |
| Downstream | `AR-012` `FF-35` | Extended by `DC-*` and `IX-*` |
| Downstream | `UX-008` | Assisted-user testing is a `UX-008` protocol |
| Downstream | `CO-003` | The conformance claim in acceptance |
| Lateral | `GV-005` | `ACD-36` reviewer risk |
| Lateral | `GV-010` `Q-05` | The same unfilled role |
| Lateral | `RR-005` | Standards currency review |

---

# 17. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`…`./UX-004`, `./UX-006`…`./UX-008` ·
`../01_Requirements_Engineering/RQ-006` · `../02_Architecture_and_Design/AR-012` ·
`../00_Programme_Governance_and_Control/GV-005`, `GV-009`, `GV-010`

**Workspace**
`../../project_content/00_Content_Governance_and_Standards/CG-011` ·
`../../project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010` ·
`../../project_content/13_Test_and_Acceptance_Content/TS-016` ·
`../../project_content/01_Voice_Brand_and_Design_Content/VB-003`, `VB-007`, `VB-008`, `VB-009` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06` §11 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_URD.md` §21

**External standards and sources**

| Source | Status at verification | Verified |
|---|---|---|
| W3C — *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation. **86 SC: 31 A, 24 AA, 31 AAA.** Nine added versus 2.1; **4.1.1 Parsing removed as obsolete** | Recommendation | 2026-08-18 |
| W3C — *Guidance on Applying WCAG 2 to Non-Web Information and Communications Technologies (WCAG2ICT)*, W3C **Group Note**; WCAG 2.2 edition **11 December 2025**, coordinated with the EN 301 549 update | Group Note (informative) | 2026-08-18 |
| ETSI/CEN/CENELEC — **EN 301 549**, Accessibility requirements for ICT products and services | European standard; **referenced, not adopted** | 2026-08-18 |
| W3C MATF — *Guidance on Applying WCAG 2.2 to Mobile Applications (WCAG2Mobile)* | **In development — not cited as a basis** | 2026-08-18 |
| ISO 9241-171:2008 — Guidance on software accessibility | Current | 2026-08-18 |
| ISO/IEC 25010:2023 — interaction capability, **inclusivity** | Current | 2026-08-18 |

---

# 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. Fixes the target at **WCAG 2.2 AA — 55 of 86 criteria** and allocates every one to a primary owner — **44 design-time, 11 build-time**, of which **11 additionally require human evaluation** because no design and no scanner can discharge them. **Closes `TS-016` `O-05`** by ruling all thirteen surfaces in scope, with the four Flutter applications conforming via WCAG2ICT — finding that the three excluded surfaces carry the highest situational-impairment exposure (`UXA-12`). Records that **100 of 621 files still cite WCAG 2.1** against the `RQ-006` ruling (`UXA-11`). Specifies the ACR and states the precise consequences of the unfilled reviewer role | *(pending — `PGD-A1-09`)* |

---

*`UX-005` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
