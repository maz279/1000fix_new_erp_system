---
id: QA-008
title: Accessibility Test Plan
category: 08 — Quality Engineering & Test
code: QA
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead with the QA Lead
approver: Chief Technology Officer with the Chief Commercial Officer
standards_basis: >
  WCAG 2.2 Level AA (W3C Recommendation 5 October 2023, updated 12 December 2024;
  ISO/IEC 40500:2025) · WCAG2ICT for non-web software · EN 301 549 · W3C ACT Rules Format ·
  ISO/IEC/IEEE 29119-3:2021 §8
traces_to: >
  PGD-000 QA-008 · UX-005 (55 A+AA criteria, 13 surfaces, ACD-01…ACD-31) ·
  05-06 §11 (WCAG 2.1 AA automated scan plus manual audit per portal) · NFR-073, NFR-074, NFR-016 ·
  PS-04 (contractual) · TS-016 (cannot be executed — no accessibility reviewer) ·
  AUDIT-014 TS-02 (TS-016 registered P2 on a contractual requirement) · AR-012 FF-35
depends_on: UX-005 (conformance design) · QA-001 (levels, capacity) · QA-005 §12.3 (scan engine) · UX-001 (component library)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 22:01 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# QA-008 — Accessibility Test Plan

### Category 08 · Code `QA` · WCAG 2.2 AA · WCAG2ICT · EN 301 549 · ACT Rules Format

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `QA-008` exists in `PGD-000` Category 08, status ◐ `P1` `W2`.
>    **Issued at `Now`** — `P03` ships in W1 and `05-06` §11 requires an audit *before each portal
>    release*; see §1.3.
> 2. **`PG-03` Count, do not consult.** Surface, criterion and check counts taken from `UX-005` §4.2,
>    §7 and `TS-016` at **2026-08-18 22:01 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1, including the **2.1-versus-2.2 ruling** the estate needs.
> 4. **`PG-M4` Verify citations.** WCAG 2.2 status verified 2026-08-18: W3C Recommendation
>    5 October 2023, updated 12 December 2024, adopted as **ISO/IEC 40500:2025** on 21 October 2025.

---

## 1. Purpose

`TS-016` is a good accessibility test pack. **Its own audit records that it cannot be executed,
because no accessibility reviewer exists** (`AUDIT-014` `TS-06`). `UX-005` then supplied the thing
that was missing beneath it — the conformance design, the surface scope ruling, and the allocation of
all 55 Level A and AA criteria to a design-time or build-time owner.

**What still does not exist is the plan that resources and schedules the human half.** This document
is that plan: who is competent to run the manual audit, on what assistive technology, in which
language, how often, at what volume, against what capacity, and what happens to a failure.

> **The estate's own numbers make the problem exact.** `UX-005` §4.2 rules **thirteen surfaces** in
> scope. `TS-016` scripts **21 checks against 9**. `05-06` §11 requires *"automated scan plus manual
> audit"* **before each portal release**, against `06-01` §5's **monthly production cadence**.
> **13 surfaces × 21 checks × 2 languages, monthly, is 546 manual assertions a month** — and the
> reviewer who would perform them does not exist.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **The conformance target ruling** — 2.1 versus 2.2, and how it propagates (§3) |
| 2 | **The test methods** and what each can and cannot find (§4) |
| 3 | **The assistive-technology matrix**, including Bengali (§5) |
| 4 | **Reviewer competency** — the role that does not exist, what it requires, and three sourcing options (§6) |
| 5 | **Assisted-user testing** — participants, recruitment lead time, session design (§7) |
| 6 | **The volume position** — 546 monthly assertions against capacity, and how it is closed (§8) |
| 7 | **Remediation policy** — severity mapping, SLAs, and what blocks a release (§9) |
| 8 | **The wave schedule and the conformance report as gate evidence** (§10) |

**Explicitly out of scope**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| **The conformance design** — target, surface scope, criterion allocation, Bengali design rules, design-time gates `G1`–`G4` | **`UX-005`** | **Consumed entirely.** `UX-005` §9 already defines the four gates and §10 the five methods; this plan resources and schedules them |
| Design tokens, contrast, target size, focus tokens | `UX-001`, `UX-005` §5 | |
| The `FF-35` automated build check | `AR-012` | Consumed as `G3` output |
| Bengali typography and layout rules | `UX-007` | L11 localisation, not L10 |
| The accessibility **content** standard | `CG-011`, `UI-010` | |
| Test script content | `TS-016` | Governed here; `ACD-05` records it needs three new script sets |
| Usability research | `UX-008` | Assisted-user testing is accessibility verification, not usability research — §7.4 states the boundary |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Content Design Lead** | The plan they own, and §6's sourcing decision |
| **Accessibility reviewer** (when appointed) | §4, §5, §9 — the working method |
| QA engineers | §4.2, §8 — the automated half and its honest ceiling |
| Developers | §9 — what a failure means and how fast it must be fixed |
| CCO and procurement | §10.3 — the conformance report clients will ask for, which the programme currently cannot produce for any surface |
| CFO | §6.3, §8 — the cost of the role and the volume it must cover |

### 1.3 Why this is issued at `Now`, and why `TS-016`'s priority was wrong

`PGD-000` registers `QA-008` at `W2`; `TS-016` was registered `W2` **and `P2`**.

| Fact | Consequence |
|---|---|
| `P03` (the customer portal) ships in **W1** | `05-06` §11's *"before each portal release"* first binds at W1 |
| `PS-04` is **contractual**, and `NFR-073` is **`P1`** | A `P2` on a contractual requirement is a scale error, not a judgement — `AUDIT-014` `TS-02` |
| `G1-11` requires UAT sign-off, and `TS-011` covers the customer portal | Accessibility failures found at UAT are found too late to fix inside the window |

**Both are corrected: this plan at `Now`, and `TS-016` to `Now`, `P1`** — recorded with `QAA-01` and
`QAA-10`.

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Edition, verified 2026-08-18 | Conformance | Departure |
|---|---|---|---|
| **WCAG 2.2 Level AA** | W3C Recommendation **5 October 2023**, updated **12 December 2024**; **ISO/IEC 40500:2025** adopted 21 October 2025 | The conformance target. **55 Level A + AA success criteria** (87 across all three levels) | **The estate says 2.1 in two places.** §3 rules |
| **WCAG2ICT** | current | The four Flutter applications conform to 2.2 AA as interpreted for non-web software (`ACD-01`) | None |
| **EN 301 549** | current | Referenced for the procurement-facing conformance statement | Not a compliance obligation in Bangladesh; used as the report's structural model |
| **W3C ACT Rules Format** | current | §4.2 — the automated engine must be ACT-conformant, so a machine result maps to a criterion rather than to a vendor rule | None |
| **ISO/IEC/IEEE 29119-3:2021** | 2021, 2nd ed. | A level plan under `QA-002` `LP-6` | None |
| **WCAG 3.0** | **Working Draft, March 2026** — 174 requirements; Candidate Recommendation targeted Q4 2027 | **Not adopted.** Recorded in `RR-005` as a watch item | **Declared:** a Working Draft is not a conformance target. `UX-005`'s target stands until 3.0 reaches Recommendation, which is 2028 at the earliest |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `UX-005` §4.2 | **All thirteen surfaces in scope**, including the three Flutter applications `PS-04`'s *"web portals"* wording excluded — `UXA-12` |
| `UX-005` §7 | All **55** Level A + AA criteria allocated to a design-time or build-time owner |
| `UX-005` §9 | Design-time gates **`G1` token · `G2` screen · `G3` build · `G4` release** |
| `UX-005` §10 | **Five verification methods** and what each can and cannot find |
| `UX-005` §8 | `ACD-14`…`ACD-21` — the Bengali obligations no automated tool can discharge |
| `UX-005` §11 | The Accessibility Conformance Report structure, `ACD-27`…`ACD-31` |
| `TS-016` | **21 checks × 9 portals = 189 assertions**; `ACD-05` records it needs three new script sets |
| `05-06` §11 | *"WCAG 2.1 AA automated scan plus manual audit per portal. Before each portal release"* |
| `NFR-073`, `NFR-074`, `NFR-016`, `NFR-019`, `NFR-078` | The accessibility NFR set |
| `AR-012` `FF-35` | The automated build check, **blocking not warning** (`ACD-23`) |
| `06-01` §5 | **Monthly production cadence within a wave** — the multiplier in §8 |
| `AUDIT-014` `TS-06` | **`TS-016` cannot be executed — no accessibility reviewer exists** |
| `GV-010` | **29 of 29 audit reports at independence class `I0`** — self-assessment |

### 2.3 What this document closes

| Finding | Source | How | Residual |
|---|---|---|---|
| `TS-06` (accessibility half) | `AUDIT-014` | §6 specifies the reviewer role, its competency, and three sourcing options with costs — converting *"no reviewer exists"* from an observation into a decision | Appointment — `Q-01` |
| `TS-02` (`TS-016` priority) | `AUDIT-014` | §1.3 corrects `P2` → `P1` and `W2` → `Now` | Category 13 register change — `QAA-01` |
| `ACD-05` | `UX-005` | §8.2 schedules the three new script sets `TS-016` needs for the Flutter applications | Content authoring — `Q-03` |
| `QA-008` register row ◐ | `PGD-000` | *"`TS-016` exists and cannot be executed"* — §6 and §8 make it executable | — |
| `UX-005` `O-04` | `UX-005` | §4.4 gives `P06`'s declared partial conformance a test method and a compensating-control assertion | Vendor dependency |

---

## 3. The Conformance Target Ruling

### 3.1 The conflict, counted

| Source | Says | Status |
|---|---|---|
| `PS-04`, `NFR-073` | **WCAG 2.1 AA**, *"on all web portals"* | Contractual, and it excludes four applications |
| `05-06` §11 | **WCAG 2.1 AA** automated scan plus manual audit per portal | The testing standard |
| `TS-016` | **WCAG 2.1 AA** test procedures | The test content |
| **`UX-005`** | **WCAG 2.2 AA**, thirteen surfaces, WCAG2ICT for the applications | The conformance design |
| `_CATEGORY_OVERVIEW.md`, `PGD-000` | **WCAG 2.2 AA** | The register |

`UX-005` §2.2 counted the estate: **100 files cite WCAG 2.1; 4 cite WCAG 2.2.**

### 3.2 The ruling

> **`ATP-01`. The conformance target is WCAG 2.2 Level AA**, across all thirteen surfaces of
> `UX-005` `ACD-01`, with WCAG2ICT applied to the four Flutter applications.

| Reason | Detail |
|---|---|
| **2.2 is a superset** | 2.2 adds nine criteria and removes one (4.1.1 Parsing). A 2.2 AA claim satisfies a 2.1 AA obligation; the reverse is not true |
| **2.2 is the current Recommendation and now an ISO standard** | Published 5 October 2023, updated 12 December 2024, **ISO/IEC 40500:2025** since 21 October 2025. Testing to a superseded version and calling it conformance is the `C-04`/`H-01`/`M-01` defect class |
| **The added criteria matter here specifically** | 2.4.11 Focus Not Obscured, 2.5.7 Dragging Movements and 2.5.8 Target Size (Minimum) all bear directly on a dispatch board, a bulk-select list and a gloved technician on a 3 GB device |
| **Retesting later costs more** | Adopting 2.1 now and 2.2 at W5 means re-auditing thirteen surfaces against nine additional criteria after they are built |

### 3.3 Propagation

Recorded as changes this ruling requires elsewhere, so the estate does not hold both targets.

| Artefact | Change | Owner | Route |
|---|---|---|---|
| `05-06` §11 | *"WCAG 2.1 AA"* → **2.2 AA**, and *"per portal"* → *"per surface"* | Enterprise Architecture | `RQ-005` |
| `PS-04`, `NFR-073` | Restate to 2.2 AA and to **thirteen surfaces**, not *"web portals"* | Enterprise Architecture with CCO | `RQ-005`; **a contractual restatement** |
| `TS-016` | Retitle to 2.2; **add three script sets** for the Flutter applications (`ACD-05`) | Programme Content Lead | `CG-006` |
| `RR-005` | Register WCAG 2.2 with its verification date, and **WCAG 3.0 March 2026 Working Draft as a watch item** | PMO | — |

> **`ATP-02`.** `4.1.1 Parsing` is **removed** in 2.2 and its absence is not a gap (`ACD-06`). A
> reviewer using a 2.1 checklist against a 2.2 claim will otherwise raise it every time.

---

## 4. Test Methods

`UX-005` §10 defines five methods and what each can and cannot find. This plan schedules them,
assigns them and states their honest yield.

### 4.1 Method allocation

| Method | Gate (`UX-005` §9) | Runs | Owner | Criteria it can evidence |
|---|:--:|---|---|---:|
| **Token / design-system check** | `G1` | Per design-system release | Design System Lead | ~6 systemic |
| **Design review of the screen** | `G2` | Before a screen enters build | Designer + **accessibility reviewer** | ~18 design-time |
| **Automated scan** | `G3` | **Every CI run**, blocking (`FF-35`, `ACD-23`) | Engineering | **~17 of 55 (~31%)** |
| **Manual audit** | `G4` | **Before each surface release**, both languages | **Accessibility reviewer** | ~34 of 55 |
| **Assisted-user testing** | — | **Per wave gate** (`ACD-26`) | Accessibility reviewer with participants | The task-completion question no other method answers |
| **Field-condition testing** | — | Per mobile release | QA with technicians | Situational — `ACD-11`…`ACD-13` |

### 4.2 The automated ceiling, stated honestly

> **`ATP-03`. A clean automated scan is never reported as conformance.** `QA-001` §6.4 sets the
> automation ceiling for L10 at **~30%**, and that is a property of WCAG, not of effort.
>
> `UX-005` `ACD-24` puts it exactly: *"An automated scan finds a missing `alt`; only a person finds
> an `alt` that says 'image1'."*

| # | Rule |
|---|---|
| `ATP-04` | The engine is **ACT-Rules-conformant** (`QA-005` §12.3), so a machine result maps to a success criterion rather than to a vendor-specific rule name |
| `ATP-05` | **A criterion is marked *Supports* only on evidence from a method capable of finding its failure mode** (`ACD-27`). An automated scan cannot evidence 1.1.1, 2.4.3, 3.3.3 or any test-only criterion |
| `ATP-06` | **Scan coverage is reported as a fraction of criteria, not of pages.** *"98% of pages scanned clean"* against 31% of criteria is a misleading number, and it is the number accessibility tooling reports by default |
| `ATP-07` | `G3` **blocks** on violations; it does not warn (`ACD-23`, `FF-35`) |

### 4.3 The manual audit

| Element | Provision |
|---|---|
| Scope | The surface's screens at the six data states `UX-005` `G2` requires — empty, loading, error, populated, partial, offline |
| **Languages** | **Both.** `ACD-20`: *"a screen that passes in English is not tested"* |
| Method | Keyboard-only traversal · screen-reader traversal · zoom to 200% and text-spacing · colour-only-signal check · error-recovery walk · focus-order-versus-task check |
| Output | Per-criterion result, per surface, with evidence — feeding the ACR §11 per-criterion table |
| Independence | Stated per `ACD-29`. **`GV-010` records 29 of 29 audit reports at class `I0`**; an `I0` accessibility claim must say so |

### 4.4 `P06` — the declared partial

`P06` is Metabase + Grafana, and `UX-005` §6.5 declares partial conformance with `ACD-08`'s
compensating control: **every dashboard has an accessible tabular equivalent, exportable and
screen-reader navigable.**

| # | Rule |
|---|---|
| `ATP-08` | **The compensating control is itself tested**, to the full manual standard. A declared partial with an untested compensator is an undeclared failure |
| `ATP-09` | **`ACD-08` is asserted as a build check**: no analytical content exists only as a chart. This is testable automatically and is cheaper than auditing each board |
| `ATP-10` | Vendor accessibility is re-assessed **at every major version upgrade** (`ACD-10`), and a regression in a vendor component is a defect against this plan, not an excuse |

---

## 5. The Assistive-Technology Matrix

### 5.1 What is tested with what

| Surface class | Screen reader | Browser / platform | Language | Priority |
|---|---|---|---|:--:|
| Web portals | **NVDA** | Chrome, Firefox on Windows | **Bengali + English** | **Primary** |
| Web portals | **JAWS** | Chrome on Windows | Bengali + English | Secondary |
| Web portals | VoiceOver | Safari on macOS/iOS | English | Tertiary |
| **Flutter applications** | **TalkBack** | Android — **floor spec: mid-range Android 11, 3 GB** | **Bengali + English** | **Primary** (`ACD-03`) |
| Flutter applications | VoiceOver | iOS | English | Secondary (`ACD-03`) |
| All | Keyboard only | all | both | **Primary** |
| All | Platform magnification, 200% text scaling | all | both | Primary (`ACD-04`) |

> **`ATP-11`.** The **primary** rows run before every surface release. Secondary and tertiary run
> **per wave gate**. Prioritising by the assistive technology Bangladeshi users actually have is the
> point `TS-016` makes and it is adopted: NVDA on Windows and TalkBack on Android are the realistic
> combinations, and testing VoiceOver first would optimise for a population this system does not
> primarily serve.

### 5.2 The Bengali obligations

`UX-005` §8 carries `ACD-14`…`ACD-21`. Their **test** obligations:

| # | Test | From |
|---|---|---|
| `ATP-12` | Every script change carries `lang` (SC 3.1.2) — verified by listening, because without it a screen reader applies Bengali phonology to `Mushak 6.3`, `bKash` and `SR-2026-114882` | `ACD-14` |
| `ATP-13` | **Numeral reading is verified in both numeral sets.** A Bengali numeral read as an English one corrupts an amount or an identifier | `ACD-16` |
| `ATP-14` | **Conjunct rendering is verified on the reference device** at rank 1 and rank 2 faces. A conjunct rendered as a box is a 1.1.1 failure with no alt text available | `ACD-17` |
| `ATP-15` | SC 1.4.12 Text Spacing is verified **in Bengali**, where layouts commonly fail it | `ACD-19` |
| `ATP-16` | Bengali size floors are tested as **accessibility floors**: 14 px absolute on screen, 8 pt absolute in print | `ACD-18` |
| `ATP-17` | Where Bengali assistive-technology support is materially weaker than English, the limitation is **declared in the ACR** — and the declaration is itself checked, because an undeclared limitation is a false claim | `ACD-21`, `ACD-09` |

> **`ATP-18`. The bilingual trap is the single most likely failure of this plan.** A reviewer under
> time pressure tests English, finds it clean, and reports the surface as passing. **Every manual
> audit result is invalid unless both language runs are recorded** — this is `ACD-20` made an
> evidence rule.

---

## 6. Reviewer Competency

### 6.1 The role that does not exist

`AUDIT-014` `TS-06` records `TS-016` as unexecutable *"because no accessibility reviewer exists."*
`QA-001` §9.1 carries it as `MTS-D2` and `QAA-06`. This section specifies the role so it can be
filled rather than described.

| Competency | Requirement |
|---|---|
| WCAG | Able to evaluate all 55 A+AA criteria against a live surface, including the nine new in 2.2 |
| Assistive technology | **Operationally fluent in NVDA and TalkBack**, not merely aware of them. A reviewer who cannot navigate with a screen reader cannot assess focus order |
| **Bengali** | **Reads and hears Bengali**, and can judge whether a Bengali screen-reader rendering is correct. **This is the hardest requirement and the one that will be quietly dropped** |
| Mobile | WCAG2ICT applied to Flutter; TalkBack gestures; platform text scaling |
| Judgement | Able to distinguish a technical pass from a usable outcome — the whole reason `G4` cannot be discharged by `G3` |
| Independence | Able to state an independence class per `ACD-29` and `GV-010` |

### 6.2 What the role is not

| Not | Why |
|---|---|
| A developer running a scan | §4.2's ceiling; a scan is `G3` and this role owns `G4` |
| A designer checking their own screens | `MTS-S2`; and `G2` already places the reviewer alongside the designer, not instead of them |
| A general QA engineer | The competency set above is specialised, and the Bengali screen-reader requirement is not transferable |
| An assisted user | §7 — participants are a separate population and are not a substitute for a trained evaluator |

### 6.3 Three sourcing options

| Option | Model | Cost shape | Assessment |
|---|---|---|---|
| **A — Hire** | A permanent accessibility specialist | Salaried, ~36 months | Best continuity; the Bengali + AT + WCAG combination is scarce in the market and recruitment lead time is real |
| **B — Train** | Develop an existing Content Design or QA person, with external certification and mentoring | Training + ramp of ~3 months | **Recommended.** The Bengali competency already exists inside the team; WCAG and AT fluency are trainable, and the reverse is not |
| **C — Contract per release** | An external agency audit before each surface release | Per engagement × ~33 releases | Highest independence (`ACD-29`), and the **highest total cost by a wide margin** at monthly cadence. Viable as a *supplement* at wave gates |

> **Recommended: `B` for the per-release audit, with `C` at the W4 and W9 gates for an independent
> opinion.** This gives continuity where volume is high and independence where the claim is
> external — and it directly addresses `ACD-29`'s observation that **29 of 29 audits to date are
> class `I0` self-assessment.** Recorded as `QA-008-D-03`; the appointment is `Q-01`.

---

## 7. Assisted-User Testing

### 7.1 Why it is not optional

`UX-005` §10 records that assisted-user testing finds *"task completion by a real user with
assistive technology, in Bengali"* and that **nothing else finds this**; `ACD-25` records that
dropping it is *"the standard cost saving and the standard cause of a failed conformance claim."*

### 7.2 Participants

| Participant class | Per session | Surfaces | Note |
|---|---:|---|---|
| Screen-reader user, **Bengali-first** | 2 | `P01`, `P03`, `P04`, `P05` | The hardest to recruit and the most informative |
| Screen-reader user, English | 1 | Same | |
| Low-vision, magnification / high contrast | 2 | All web | |
| Motor impairment, keyboard-only or switch | 1 | `P03`, `P05` | |
| Cognitive / low literacy, **Bengali** | 2 | `P01`, `P02`, `P09` | `A-04` Rubel's persona is real: low literacy, Bengali only |
| **Situational** — gloves, sunlight, one hand | 2 | `P02`, `P09`, `P11` | Real technicians; overlaps `MTS-D5` field logistics |

### 7.3 Cadence and lead time

| # | Rule |
|---|---|
| `ATP-19` | **Per wave gate, not per release** (`ACD-26`), because recruitment has a lead time monthly cadence cannot absorb |
| `ATP-20` | **Recruitment begins at T−10 weeks**, four weeks before the `GV-009` gate window opens at T−6. A participant panel assembled at T−2 is a panel of whoever was available |
| `ATP-21` | **Participants are compensated**, and the arrangement is recorded. An unpaid accessibility participant panel does not persist across nine gates |
| `ATP-22` | **Sessions are task-based, not feature-based**: *"book a repair"*, not *"try the booking page"*. A feature tour measures the tour |
| `ATP-23` | **A task the participant cannot complete is a `S2` defect at minimum**, and `S1` if the surface is `P01`, `P03` or `P05` and the task is primary (`TS-018`: *"an assisted user cannot complete a portal's primary task"* is an automatic `S1`) |

### 7.4 The boundary with `UX-008`

| | `QA-008` assisted-user testing | `UX-008` usability research |
|---|---|---|
| Question | *Can an assisted user complete the task at all?* | *Is the design good for its users?* |
| Population | Assistive-technology users and situationally impaired users | The general user population |
| Output | **Defects** against WCAG conformance and task completion | Design findings |
| Cadence | Per wave gate | Per design cycle |

> **`ATP-24`.** Where a session produces both, it is routed to both (`MTS-S5`), and **never converted
> into a usability finding to avoid a conformance defect.**

---

## 8. The Volume Position

### 8.1 The arithmetic

| Element | Count | Source |
|---|---:|---|
| Surfaces in scope | **13** | `UX-005` `ACD-01` |
| Surfaces `TS-016` currently scripts | **9** | `TS-016` §1.3 |
| **Script sets missing** | **3** *(the Flutter applications; the fourth is `P01`'s app)* | `ACD-05` |
| Checks per surface | **21** | `TS-016` |
| Languages per check | **2** | `ACD-20` |
| **Manual assertions per full round** | **13 × 21 × 2 = 546** | |
| Release cadence within a wave | **monthly** | `06-01` §5 |
| Production releases across the programme | **~33** | `QA-002` §10.1 |
| **Manual assertions if every surface is audited every release** | **~18,000** | |

Against `LP-6`'s **~10 QA FTE-months total**, shared with performance, security, localisation and
offline (`QA-002` §12.2). **`TS-016` `O-06` already says this is not feasible for one person across
nine portals; at thirteen surfaces and two languages it is further from feasible, not closer.**

### 8.2 How it is closed

| # | Mechanism | Effect |
|:--:|---|---|
| 1 | **`G1` token checks catch systemic failures once, across all 13 surfaces** | Contrast, target size, focus indication are design-system properties. A `G1` pass removes ~6 criteria from every surface audit |
| 2 | **`G2` screen review prevents rather than detects** (`ACD-22`) | A screen without a completed `G2` does not enter build. **This is the gate that removes the most downstream cost** |
| 3 | **`G3` automated scan on every CI run**, blocking | ~31% of criteria, continuously, at zero marginal cost |
| 4 | **Change-scoped manual audit** — `ATP-25` | **The largest reduction.** §8.3 |
| 5 | **Three new `TS-016` script sets authored once** (`ACD-05`) | Removes the coverage gap without recurring cost |
| 6 | **Assisted-user testing per gate, not per release** (`ACD-26`) | 9 rounds, not 33 |

### 8.3 The change-scoped audit rule

> **`ATP-25`.** A full 21-check manual audit runs **per surface per wave gate**, and **not** per
> monthly release. Between gates, the manual audit is **scoped to what changed**: the screens
> touched, plus any screen whose `G1` tokens changed, plus a **rotating 10% sample** of unchanged
> screens.

| # | Supporting rules |
|---|---|
| `ATP-26` | **The scope reduction is logged at the gate** as an `MTS-X2` exception naming what was not audited (`MTS-R2`, `TS-013` `RS-13`). This is a truncation with a record, not a silent one |
| `ATP-27` | **A surface's first release is always a full audit.** There is no change scope for a new surface |
| `ATP-28` | **A `G3` regression re-triggers a full audit of the affected criterion across all surfaces**, because a systemic failure is usually a component-library failure |
| `ATP-29` | **`RC-A` criteria are never change-scoped**: keyboard operability, focus order, error identification and the Bengali set (§5.2) are audited every release on customer-facing surfaces |

> **Honest reading.** Even with all six mechanisms, this level remains under-resourced against
> `06-01`'s staffing, and §8.1's figure is why. **`ATP-25` is a truncation with a rule and a record**,
> which `QA-001` §12.3 permits, rather than an unrecorded reduction, which it prohibits. The
> resourcing decision is `QA-001` `Q-01`.

---

## 9. Remediation Policy

### 9.1 Severity mapping

`TS-018` owns the severity scale; this maps accessibility failures onto it, so an accessibility
defect is triaged with every other defect rather than in a separate, slower register.

| Failure | Severity | Rationale |
|---|:--:|---|
| **An assisted user cannot complete a portal's primary task** | **`S1`** | `TS-018`'s own automatic-`S1` list |
| A Level A criterion fails on a customer-facing surface | **`S1`** | Level A is the floor; `PS-04` is contractual |
| A Level AA criterion fails on a customer-facing surface | `S2` | |
| A Level A criterion fails on an internal surface | `S2` | |
| A Bengali-specific failure — numerals, conjuncts, `lang` | **`S2`**, `S1` if it corrupts an amount or an identifier | `ATP-13` |
| A Level AA criterion fails on an internal surface | `S3` | |
| A criterion fails only under a tertiary AT combination | `S3` | |
| Cosmetic, no criterion engaged | `S4` | |

### 9.2 SLAs and release blocking

| # | Rule |
|---|---|
| `ATP-30` | **No customer-facing surface releases with an open `S1` accessibility defect.** `PS-04` is contractual, and a contractual conformance claim with a known Level A failure is a misrepresentation |
| `ATP-31` | **Open `S2` accessibility defects are capped per surface** by `QA-010`'s threshold, and each carries a dated remediation plan in the ACR §7 |
| `ATP-32` | **A criterion below *Supports* appears in the ACR with a remediation date** (`ACD-09`). An undeclared partial conformance is a false claim |
| `ATP-33` | **A retrofit costs 5–10× design-time cost** (`UX-005` §1). A defect traceable to a skipped `G2` is recorded as such, so the cost lands where the decision was made |
| `ATP-34` | **Accessibility defects enter `TS-018` triage** with the same cadence and the same authority as every other defect (`TR-01`, `TR-02`) |

---

## 10. Schedule and Gate Evidence

### 10.1 Wave schedule

| Wave | Surfaces released | Full audits | Assisted-user session | Note |
|:--:|---|:--:|:--:|---|
| **W1** | `P03`, `P01` web | 2 | 1 | **First conformance claim.** `P03` is the customer portal |
| **W2** | + `P02`, `P09` apps | 4 | 1 | **WCAG2ICT first applied**; TalkBack in Bengali; `ACD-05`'s script sets needed |
| **W3** | + `P05` | 5 | 1 | |
| **W4** | + `P04`, `P06` | 7 | 1 | **`P06` declared partial** + compensating-control test; **independent `C` audit** |
| **W5** | + `P11` | 8 | 1 | Field auditor app |
| **W6** | + `P01` app | 9 | 1 | |
| **W7** | + `P07`, `P08` | 11 | 1 | Marketplace seller surfaces |
| **W8** | + `P10`, `P12` | **13** | 1 | Full estate |
| **W9** | all | 13 | 1 | **Independent `C` audit**; final ACR set for `G9-04` handover |

### 10.2 Gate evidence

| Element | Content | Class |
|---|---|:--:|
| Automated scan results | Per surface, per release, **with criterion coverage stated** (`ATP-06`) | `E5` |
| Manual audit reports | Per surface, **both languages**, per-criterion result | `E5` + `E6` |
| Assisted-user session records | Tasks, participants by class, completion, findings | `E1` + `E6` |
| **Accessibility Conformance Report** | Per surface, per release, `UX-005` §11 structure | `E6` |
| Independence statement | Per `ACD-29` — **`I0` self-assessment must say so** | `E6` |
| Open defects | By severity, with remediation dates | `E2` |
| **Not audited** | The `ATP-25` change scope, named (`MTS-R2`) | `E2` |

### 10.3 The conformance report is a commercial deliverable

> `UX-005` §11.1: corporate and government clients — `P04`, 500–2,000 users — increasingly require an
> accessibility conformance statement in procurement, and `CO-003` acceptance will be asked for one.
> **The programme currently cannot produce it for any surface.**

| # | Rule |
|---|---|
| `ATP-35` | **The ACR is a delivery obligation, not a by-product.** It is produced per surface per release (`ACD-28`) and its absence blocks the release of a customer-facing surface |
| `ATP-36` | **One statement for "the platform" would be false for at least one surface** (`ACD-28`) — `P06` is a declared partial |
| `ATP-37` | The published statement names a **contact route for accessibility problems** and a response commitment (`ACD-31`). A statement with no feedback channel is decoration |

---

## 11. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `QA-008-D-01` | Conformance target | (a) WCAG 2.1 AA per `PS-04`, `05-06` §11 and `TS-016`; (b) **2.2 AA per `UX-005`** | **(b)** | 2.2 is a superset, is the current Recommendation and **ISO/IEC 40500:2025**, and its added criteria bear directly on this system's dispatch board, bulk select and gloved field use | Four propagation changes (§3.3), one of them **contractual** |
| `QA-008-D-02` | WCAG 3.0 | (a) adopt the March 2026 Working Draft; (b) **watch item in `RR-005`** | **(b)** | A Working Draft is not a conformance target; Candidate Recommendation is targeted Q4 2027 and Recommendation 2028+ | Declared in §2.1 |
| `QA-008-D-03` | Reviewer sourcing | (a) hire; (b) **train internally, external audit at W4 and W9**; (c) contract every release | **(b)** | The **Bengali** competency exists inside the team and is the scarcest; WCAG and AT fluency are trainable. (c) at monthly cadence is the most expensive option by a wide margin | Closes `TS-06`'s accessibility half; addresses `ACD-29`'s 29-of-29 `I0` position |
| `QA-008-D-04` | Manual audit cadence | (a) full audit every release; (b) **full per wave gate, change-scoped between**; (c) per wave only | **(b)** | (a) is ~18,000 manual assertions and is not resourced; (c) leaves monthly releases unverified. (b) is a truncation **with a rule and a record** | `ATP-25`…`ATP-29`; logged as an `MTS-X2` exception at each gate |
| `QA-008-D-05` | AT priority | (a) VoiceOver-first, the common default; (b) **NVDA + TalkBack first, in Bengali** | **(b)** | Optimises for the assistive technology Bangladeshi users actually have, which is `TS-016`'s own position | §5.1; secondary and tertiary run per gate |
| `QA-008-D-06` | Assisted-user testing | (a) drop as a cost saving; (b) **per wave gate with T−10 recruitment** | **(b)** | `ACD-25`: dropping it is the standard cost saving and the standard cause of a failed conformance claim | `ATP-19`…`ATP-23` |

---

## 12. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Is the accessibility reviewer appointed — trained internally per `D-03` — and funded?** | Content Design Lead with CFO | **T−6 of `G1`** | **The entire plan.** `TS-016`; every `G4`; every ACR |
| `Q-02` | Is the contractual restatement of `PS-04` from 2.1 to **2.2 AA, thirteen surfaces**, accepted? | CCO with Enterprise Architecture | **W1** | §3.3; the ACR's standards section |
| `Q-03` | Who authors `TS-016`'s three missing script sets for the Flutter applications? | Programme Content Lead | **W2** | `ACD-05`; `P02`, `P09`, `P11` coverage |
| `Q-04` | Is the assisted-user participant panel funded, including compensation? | Content Design Lead with CFO | **T−10 of `G1`** | `ATP-19`…`ATP-21` |
| `Q-05` | Is an external independent audit funded at W4 and W9? | CFO with CCO | **W3** | `ACD-29`; the independence class on the customer-facing ACR |
| `Q-06` | Does `UX-001` expose accessible-name and role test hooks so `G3` can assert semantics rather than only markup? | Design System Lead | **W1** | §4.2; shared with `QA-005` `Q-03` |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | One conformance target is ruled, with every propagation change named and routed | §3 — 2.2 AA, 4 changes |
| `AC-02` | Every `UX-005` §10 method is scheduled, assigned and given an honest yield | §4.1 — 6 methods |
| `AC-03` | The automated ceiling is stated and a clean scan is never reportable as conformance | §4.2 — ~31%, `ATP-03`…`ATP-07` |
| `AC-04` | An assistive-technology matrix exists, prioritised for the actual user population | §5.1 |
| `AC-05` | Bengali obligations have test rules, and the bilingual trap is an evidence rule | §5.2 — `ATP-12`…`ATP-18` |
| `AC-06` | The reviewer role is specified with competency, exclusions and three costed sourcing options | §6 |
| `AC-07` | Assisted-user testing has participants, lead time, compensation and a severity consequence | §7 |
| `AC-08` | The volume position is counted and closed by six mechanisms, with the residual stated | §8 — **546 per round, ~18,000 unmanaged** |
| `AC-09` | The scope reduction is a rule with a record, not a silent truncation | `ATP-25`, `ATP-26` |
| `AC-10` | Accessibility failures map onto `TS-018` severities and block releases where contractual | §9 |
| `AC-11` | The conformance report is a delivery obligation with a blocking rule | §10.3 |

**Definition of done.** Complete when every criterion is met, the reviewer is appointed, `P03`'s
first full audit is complete in both languages, and its ACR is published. Approval carries the
`PGD-A1-09` qualification.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `UX-005` | The conformance design, surface scope, criterion allocation, `G1`–`G4`, and the five methods |
| Upstream | `UX-001` | The component library whose tokens `G1` checks |
| Upstream | `UX-007` | Bengali typography — L11, adjacent to L10 |
| Upstream | `AR-012` `FF-35` | The blocking automated build check |
| Upstream | `QA-001` §6.4 | The ~30% automation ceiling |
| Upstream | `QA-005` §12.3 | The ACT-conformant scan engine |
| Downstream | `QA-010` | Accessibility defects and their gate thresholds |
| Downstream | `QA-011` | Criterion coverage per surface reported as a triple |
| Downstream | `CO-003` | The ACR as an acceptance deliverable |
| Downstream | `RL-003` | Go-live readiness consumes the ACR |
| Lateral | `../../project_content/13_Test_and_Acceptance_Content/TS-016` | The pack this plan makes executable, and whose priority it corrects |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./QA-001_Master_Test_Strategy.md` · `./QA-002_Test_Plans_per_Level.md` ·
`./QA-005_Test_Automation_Framework_Specification.md` · `./QA-010_Defect_Management_and_Quality_Gate_Standard.md` ·
`./QA-011_Requirements_to_Test_Coverage_Standard_and_Report.md` ·
`../00_Programme_Governance_and_Control/GV-009_Wave_Gate_and_Phase_Exit_Criteria_Handbook.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../06_Experience_and_Interface_Design/UX-001_Design_System_and_Component_Library_Specification.md` ·
`../06_Experience_and_Interface_Design/UX-005_Accessibility_Conformance_Design_WCAG_2_2_AA.md` ·
`../06_Experience_and_Interface_Design/UX-007_Bilingual_and_Bengali_Interface_Design_Standard.md` ·
`../06_Experience_and_Interface_Design/UX-008_Usability_Test_Plan_and_Findings_Log.md`

**Workspace**
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` §10, §11 ·
`../../1000fix_ERP_Module/06_Delivery_and_Implementation/06-01_Implementation_Roadmap_and_Phasing.md` §5 ·
`../../project_content/13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md` ·
`../../project_content/_AUDIT/AUDIT-014_Category_13_TS_Content_Audit.md`

**External — verified 2026-08-18**
**WCAG 2.2**, W3C Recommendation 5 October 2023, updated 12 December 2024; **ISO/IEC 40500:2025**
adopted 21 October 2025; 87 success criteria, **55 at Level A + AA** ·
WCAG2ICT · EN 301 549 · W3C ACT Rules Format ·
**WCAG 3.0 Working Draft, March 2026** — 174 requirements; not adopted (§2.1)

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Content Design with Quality Engineering | Initial issue. **Rules the conformance target at WCAG 2.2 AA** against the estate's 100-files-say-2.1 position, with four propagation changes including a **contractual restatement of `PS-04`**; schedules all six verification methods with an honest automated ceiling of ~31% of criteria; an assistive-technology matrix **prioritised for NVDA and TalkBack in Bengali** rather than the VoiceOver-first default; **specifies the reviewer role that does not exist**, with competency, exclusions and three costed sourcing options — closing the accessibility half of `TS-06`; assisted-user testing with a T−10 recruitment lead time and compensation; **the counted volume position — 546 manual assertions per round and ~18,000 if audited every release** — closed by six mechanisms with the residual stated; and the change-scoped audit rule `ATP-25` as a **truncation with a record**. Corrects `TS-016` from `P2`/`W2` to `P1`/`Now` | *Pending — `GV-002`* |

---

*`QA-008` · Category 08 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
