---
id: TS-016
title: Accessibility Test Script Pack
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with Content Design
author: QA Lead with Content Design, Design System and Localisation
reviewers: [Content Design Lead, Design System owner, Localisation Lead, CTO delegate, Legal Counsel, portal owners]
approver: Content Design Lead with QA Lead
content_class: D
purpose: >
  The WCAG 2.1 AA test procedures for each web portal, including verification with a Bengali screen
  reader. Accessibility conformance is a contractual standard on this programme, and a conformance
  claim with no test evidence behind it is a claim rather than a fact — most WCAG failures are content
  failures rather than code failures, which means an automated scan finds a minority of them and the
  majority are found only by someone using the product the way an assisted user does. In Bengali,
  with the assistive technology Bangladeshi users actually have.
traces_to: [PS-04, PS-05, PS-09, 05-06 NFR-016, 05-06 NFR-019, 05-06 NFR-073, 05-06 NFR-074, 05-06 NFR-078, 05-06 §10, 05-06 §11, CG-011, VB-007, VB-009, UI-004, UI-010, UI-003, BN-018, MM-002, P01, P03, P04, P05, P06, P07, P08, P10, P12, TS-001, TS-002, TS-006, TS-011, TS-013, TS-018]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: TS-016_Accessibility_Test_Script_Pack_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §3 PS-04 WCAG 2.1 AA accessibility on all web portals; PS-05 responsive from 320 px upward with no horizontal scrolling; PS-09 every user-visible error states what happened and what to do next, in the user's language; P01 Design Requirements list WCAG 2.1 AA
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md NFR-073 WCAG 2.1 AA compliance on all web portals (P1); NFR-016 full Bengali and English support; NFR-074 Bengali input including phonetic typing and voice-to-text on mobile; NFR-078 every error message states what happened and what to do next in the user's language; §10 minimum desktop resolution 1366×768; §11 Accessibility — WCAG 2.1 AA automated scan plus manual audit per portal, before each portal release
    verified: 2026-08-19
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md §8.2 and §10 — Bengali accessibility is tested with real assistive technology, not assumed; screen-reader pass in English and in Bengali with a Bengali-speaking tester, before each portal release; §333 names TS-016 as where §10 is executed
    verified: 2026-08-19
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md AC-06 and §343 — screen-reader testing includes a Bengali-speaking tester with real assistive technology; Bengali screen-reader pass before each portal release
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Accessibility Test Script Pack

| Item | Value |
|---|---|
| Test level | **Accessibility** — `05-06` §11 level 10; **before each portal release** |
| Roles executing | Accessibility reviewer *(unappointed — `O-02`)*, a Bengali-speaking assisted tester, and one business role per portal |
| Modules covered | All, through their portal surfaces |
| Portals covered | **9 web portals** — `P01` `P03` `P04` `P05` `P06` `P07` `P08` `P10` `P12`; the three Flutter apps are covered separately (§1.3) |
| Environment | `UAT` at portal feature-completeness, both languages populated |
| Test data set | `TS-002` — including the `B-01`…`B-11` Bengali stress set |
| Wave | W2 · `P2` — **and both the priority and the wave are challenged in `O-01`** |

> **Template conformance.** `TPL_Test_Script.md` at pack level. All six sections retained in order;
> §3 is organised by WCAG principle and then by portal, which is the addition and is justified — a
> per-portal checklist that does not follow the standard's own structure cannot be mapped to a
> conformance claim.

---

## 1. Traceability

### 1.1 What an automated scan does not find

`05-06` §11 requires *"WCAG 2.1 AA automated scan **plus manual audit** per portal"*. The word "plus"
carries the whole pack, and `CG-011` states why: **most WCAG failures are content failures, not code
failures.** An automated scanner reliably finds a missing `alt` attribute; it cannot find an `alt`
attribute that says "image1".

| Automated scan finds | Only a person finds |
|---|---|
| Missing alternative text | Alternative text that describes nothing useful |
| Insufficient colour contrast, computed | A status conveyed by colour **alone** in a way the label does not repeat (`VB-008`) |
| Missing form labels | A label that does not say what the field wants (`UI-003`) |
| Missing heading levels | A heading structure that does not match the page's logic |
| An element not focusable | A focus order that makes a task impossible to complete |
| A missing error region | An error message that does not say what to do next (`NFR-078`, `PS-09`) |
| — | **A Bengali screen reader mispronouncing a conjunct, or reading a Bengali numeral as an English one** |
| — | Whether the task can actually be completed by an assisted user, start to finish |

**The last two rows are the pack's reason to exist.** `CG-011` §8.2 and `VB-009` `AC-06` both require
Bengali accessibility to be tested with real assistive technology, and neither an English screen
reader nor an automated scan can discharge that.

### 1.2 The reciprocal reference — and what it means

`CG-011` §10 names `TS-016` as where its accessibility test regime is executed. `VB-003` §11,
`VB-009` §12, `UI-010` and `CG-011` §333 all point here. **This pack is therefore the single
verification point for four upstream content standards**, which is why it is content class `D` and
approved by the Content Design Lead rather than by QA alone.

It also means the reverse: **this pack defines no accessibility rules.** `CG-011` owns the standard,
`VB-009` owns Bengali typography, `VB-007` owns icon-and-label pairing and expansion allowance,
`UI-010` owns the accessibility text library, `UI-004` owns error messages. This pack owns only the
**procedures** (`CP-01`).

### 1.3 Scope — nine portals, and the three apps

`PS-04` and `NFR-073` say *"all web portals"*. Nine of the twelve surfaces are web; three are Flutter
applications.

| Surface | Type | In this pack | Covered by |
|---|---|:--:|---|
| `P01` Customer | Next.js web + React Native app | **●** web | Native app: platform accessibility, `O-05` |
| `P03` Admin Operations | Odoo Web (OWL 2) | **●** | — |
| `P04` Corporate B2B | Next.js | **●** | — |
| `P05` Vendor & Supplier | Odoo Portal + Next.js | **●** | — |
| `P06` Analytics | Metabase + Grafana embedded | **●** | — **and this is the hardest one, `O-04`** |
| `P07` Marketplace Seller | Next.js + React Native | **●** web | Native app: `O-05` |
| `P08` Brand Partner | Next.js | **●** | — |
| `P10` Contact Centre | Next.js | **●** | — |
| `P12` Partner & Referral | Next.js | **●** | — |
| `P02` Technician | Flutter | ○ | **Not covered by `PS-04`** — `O-05` |
| `P09` Logistics & Rider | Flutter | ○ | **Not covered by `PS-04`** — `O-05` |
| `P11` Field Auditor | Flutter | ○ | **Not covered by `PS-04`** — `O-05` |

**`PS-04` covers web portals only, and the three field applications are used by 275–635 people whose
working conditions — bright sunlight, gloves, one hand, a 5-inch screen — create accessibility needs
that WCAG addresses directly.** That is a scope gap in the specification, not in this pack, and it is
recorded as `O-05` rather than quietly fixed by extending scope this file has no authority to set.

### 1.4 Traceability obligation per script

| Field | Source |
|---|---|
| WCAG success criterion | The numbered AA criterion, e.g. `1.4.3 Contrast (Minimum)` |
| Standard | The `CG-011`, `VB-007`, `VB-009`, `UI-010` or `UI-004` rule it verifies |
| Portal | `Pnn` |
| Method | Automated · manual · **assistive technology** · Bengali assistive technology |
| Assistive technology and version | Recorded per run (`AX-05`) |
| Language | EN, BN, or both |

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **AX-01** | **Every portal gets an automated scan *and* a manual audit before every release.** Neither substitutes for the other (`05-06` §11) |
| **AX-02** | **Bengali is tested with a Bengali screen reader, by a Bengali-speaking assisted tester** (`CG-011` §8.2, `VB-009` `AC-06`). An English screen reader reading Bengali text does not discharge `NFR-016` or `NFR-073` |
| **AX-03** | **Conformance is claimed per success criterion, not per portal.** "WCAG 2.1 AA compliant" is not a test result; "51 AA criteria, 49 pass, 2 fail with named defects" is |
| **AX-04** | **Task completion is the real test.** For every portal, at least one end-to-end task is completed **entirely** with a screen reader and keyboard, and separately at 200% zoom. A page that passes every criterion and cannot be used is a fail |
| **AX-05** | **Assistive technology and version are recorded**, and the technology is one the audience plausibly has — screen readers on low-end Android, and desktop readers, not only a single vendor's flagship |
| **AX-06** | **Keyboard-only operation is verified on the high-volume `P03` roles**, because `04-00` `P03` requires keyboard-first operation for intake, dispatch and finance — accessibility and throughput are the same requirement there |
| **AX-07** | **Errors are audited as content, not as regions.** `NFR-078` and `PS-09` require each error to state what happened and what to do next, in the user's language; the audit reads the text (`UI-004`) |
| **AX-08** | **Colour is never the only carrier.** Every status in `VB-008` is verified to have a non-colour carrier — label, icon with a text equivalent, or position |
| **AX-09** | **Bengali text expansion is tested at layout level.** `VB-007` allows 20–40% expansion; the audit uses the `TS-002` `B-04` longest-expansion set at 1366×768 and at 320 px (`PS-05`) |
| **AX-10** | **No horizontal scrolling at 320 px** (`PS-05`), and no loss of content or function at 400% zoom (WCAG `1.4.10` Reflow) |
| **AX-11** | **Every accessibility defect is raised as a defect**, not as an observation. `PS-04` is contractual; an observation has no owner and no due date |
| **AX-12** | **Findings are reported by criterion and by portal**, so a partial conformance claim is possible and honest (`AX-03`) |

### 2.2 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | Portal feature-complete for the release, **both languages populated at 100%** | `KPI-092`; a Bengali audit of untranslated screens tests nothing |
| 2 | `CG-011`, `VB-007`, `VB-009`, `UI-003`, `UI-004`, `UI-010` published | `AX-07`, `AX-08`, `AX-09` |
| 3 | **A named accessibility reviewer** | **Does not exist** — `O-02` |
| 4 | **A Bengali-speaking assisted tester**, with their own assistive technology | `AX-02` — **not sourced**, `O-03` |
| 5 | Automated scanning tool integrated into CI | `05-06` §11 — `06-04` absent |
| 6 | Assistive technology inventory: desktop screen readers, Android screen readers on the `NFR-017` device class, magnification, voice control | `AX-05` |
| 7 | `TS-002` `B-01`…`B-11` Bengali stress set loaded, including `B-04` longest-expansion labels | `AX-09` |
| 8 | Test hardware at `05-06` §10 minimum: **1366×768** desktop, and a 320 px viewport | `AX-10` |
| 9 | One business role per portal available for the `AX-04` task-completion run | `TS-006` `O-02` |

---

## 3. Scripts

### 3.1 Structure

Each of the nine portals receives the same script set, organised by WCAG principle. **`ACC-<Pnn>-nn`**
per `TS-001` §4.3.

| Set | Content | Scripts per portal |
|---|---|---:|
| **1 Perceivable** | Text alternatives, contrast, colour-only, text spacing, reflow, Bengali rendering | 6 |
| **2 Operable** | Keyboard, focus order and visibility, no keyboard trap, target size, timing | 5 |
| **3 Understandable** | Labels and instructions, error identification and suggestion, consistent navigation, language of page and parts | 5 |
| **4 Robust** | Name/role/value, status messages, parsing | 2 |
| **5 Assistive-technology task completion** | One end-to-end task with a screen reader and keyboard, in **English and Bengali**; and at 200% zoom | 3 |
| **Total per portal** | | **21** |
| **Nine portals** | | **189** |

### 3.2 The 21 scripts, per portal

| Script | Success criterion | What is verified | Method | Pri |
|---|---|---|---|:--:|
| `ACC-<P>-01` | `1.1.1` Non-text Content | Every image, icon and chart has a **useful** text alternative; decorative items are marked decorative (`UI-010`) | Manual | **P0** |
| `ACC-<P>-02` | `1.4.3` Contrast (Minimum) | 4.5:1 body, 3:1 large text and UI components, against `VB-008` status colours | Automated + manual | **P0** |
| `ACC-<P>-03` | `1.4.1` Use of Colour | **Every status has a non-colour carrier** (`AX-08`, `VB-008`) | Manual | **P0** |
| `ACC-<P>-04` | `1.4.12` Text Spacing · `1.4.10` Reflow | No content or function lost at increased spacing; **no horizontal scroll at 320 px** (`AX-10`, `PS-05`) | Manual | **P0** |
| `ACC-<P>-05` | `1.4.4` Resize Text | Usable at 200%; content retained at 400% | Manual | P1 |
| `ACC-<P>-06` | `1.4.3` + `VB-009` | **Bengali renders correctly**: conjuncts, vowel signs, reph, at `VB-009` sizes and line heights; `B-01`…`B-03` set | Manual, Bengali | **P0** |
| `ACC-<P>-07` | `2.1.1` Keyboard | Every function reachable and operable by keyboard | Manual | **P0** |
| `ACC-<P>-08` | `2.1.2` No Keyboard Trap | Focus can always leave every component, including modals and date pickers | Manual | **P0** |
| `ACC-<P>-09` | `2.4.3` Focus Order · `2.4.7` Focus Visible | Order follows the task; focus always visible | Manual | **P0** |
| `ACC-<P>-10` | `2.5.8` Target Size (Minimum) | Targets meet the minimum, including on a 320 px viewport | Automated + manual | P1 |
| `ACC-<P>-11` | `2.2.1` Timing Adjustable | Session timeout warns and can be extended (`NFR-069`, `EA-08`) | Manual | P1 |
| `ACC-<P>-12` | `3.3.2` Labels or Instructions | Every field's label says what it wants (`UI-003`); placeholders are not labels | Manual | **P0** |
| `ACC-<P>-13` | `3.3.1` Error Identification · `3.3.3` Error Suggestion | **Every error says what happened and what to do next, in the user's language** (`AX-07`, `NFR-078`, `PS-09`, `UI-004`) | Manual, both languages | **P0** |
| `ACC-<P>-14` | `3.2.3` Consistent Navigation · `3.2.4` Consistent Identification | Navigation and component naming consistent across the portal and against `UI-002` | Manual | P1 |
| `ACC-<P>-15` | `3.1.1` Language of Page · `3.1.2` Language of Parts | `lang` correct, and **correct on mixed-script content** — the `B-06` set (Bengali with embedded English model numbers) | Automated + manual | **P0** |
| `ACC-<P>-16` | `3.3.4`/`3.3.6` Error Prevention | Destructive and financial actions are confirmable and reversible where possible (`NFR-079`) | Manual | P1 |
| `ACC-<P>-17` | `4.1.2` Name, Role, Value | Custom components expose name, role and value to assistive technology | Automated + AT | **P0** |
| `ACC-<P>-18` | `4.1.3` Status Messages | Status changes are announced without stealing focus — save, sync, validation, long-running job (`UI-008`) | AT | **P0** |
| `ACC-<P>-19` | `AX-04` | **One end-to-end task completed entirely with a screen reader and keyboard, in English** | AT | **P0** |
| `ACC-<P>-20` | `AX-04` + `AX-02` | **The same task completed with a Bengali screen reader by a Bengali-speaking assisted tester** | **Bengali AT** | **P0** |
| `ACC-<P>-21` | `AX-04` | The same task completed at **200% zoom on 1366×768** | Manual | P1 |

### 3.3 The `AX-04` task per portal

`ACC-<P>-19`, `-20` and `-21` need a task worth completing. These are chosen as the portal's primary
purpose, so a failure is a failure of the portal, not of a corner of it.

| Portal | The task |
|---|---|
| `P01` Customer | **Book a service, approve the estimate and pay** |
| `P03` Admin | **Complete a walk-in intake and issue a receipt** |
| `P04` Corporate | Raise a service request against a contract and approve it |
| `P05` Vendor | Acknowledge a PO and submit an invoice against it |
| `P06` Analytics | Read a dashboard figure and drill to its underlying records |
| `P07` Seller | Quote on a broadcast job and accept it |
| `P08` Brand | Open a claim, review its evidence and approve it |
| `P10` Contact centre | Answer a contact, create an order and code the disposition |
| `P12` Partner | Generate a referral link and read a commission statement |

**Pack total: 189 scripts across 9 portals · 126 at `P0` · 63 at `P1`.**

### 3.4 Bilingual check

This pack **is** bilingual verification, so the template's bilingual table is where the pack's own
Bengali obligation is recorded rather than a summary of it.

| Element | EN correct | BN correct | Truncation |
|---|:--:|:--:|:--:|
| Every one of the 189 scripts' subject content | ● | ● | ● at 1366×768 and 320 px (`AX-09`) |
| `ACC-<P>-20` — Bengali screen-reader task completion, all nine portals | — | **●** | — |
| `ACC-<P>-06` — Bengali typography rendering (`VB-009`) | — | **●** | ● |
| `ACC-<P>-13` — error messages in both languages (`UI-004`) | ● | ● | ● |
| `ACC-<P>-15` — `lang` on mixed-script content (`B-06`) | ● | ● | — |
| **This pack's own script text** | ● | ● | — |

### 3.5 Negative and edge cases

| # | Condition | Expected behaviour |
|---|---|---|
| N-01 | Automated scan clean; manual audit finds 9 failures | Normal, and the reason `AX-01` requires both. A clean scan reported as conformance is the defect this rule prevents |
| N-02 | Bengali screen reader mispronounces a conjunct | **A defect** — against `VB-009` or the platform, and it is raised either way (`AX-11`) |
| N-03 | Bengali numerals read as English digits | Defect against `VB-009`'s numeral policy |
| N-04 | Expanded Bengali label truncates a button at 1366×768 | Defect against `VB-007`'s 20–40% allowance (`AX-09`) |
| N-05 | Error text is announced but says only "invalid" | Defect against `UI-004`, `NFR-078` and `PS-09` — announced is not sufficient (`AX-07`) |
| N-06 | Status message announced by stealing focus | Defect against `4.1.3` |
| N-07 | `P06` embedded third-party dashboard fails criteria we do not control | **Recorded honestly as a partial conformance with the boundary named** (`AX-03`, `AX-12`); `O-04` |
| N-08 | Task completable in English and not in Bengali | **Fail** — `NFR-016` and `NFR-073` are not language-conditional |
| N-09 | An accessibility finding raised as an observation | Reclassified as a defect (`AX-11`) |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| Portals with an automated scan **and** a manual audit for the release | **9 of 9** (`AX-01`) |
| WCAG 2.1 AA criteria passing, per portal | **100% of `P0` scripts; ≥ 95% of `P1`** |
| Conformance reported **per criterion** | 100% (`AX-03`, `AX-12`); a portal-level "compliant" claim is not accepted |
| **`AX-04` task completion with a screen reader and keyboard, English** | **9 of 9 portals** |
| **`AX-04` task completion with a Bengali screen reader, by a Bengali-speaking assisted tester** | **9 of 9 portals** (`AX-02`) |
| Task completion at 200% zoom on 1366×768 | 9 of 9 |
| Keyboard-only operation on high-volume `P03` roles | Verified (`AX-06`) |
| Assistive technology and version recorded per run | 100% (`AX-05`) |
| Bengali expansion tested at 1366×768 and 320 px | 100% (`AX-09`) |
| Horizontal scroll at 320 px | **None** (`AX-10`, `PS-05`) |
| Accessibility findings raised as defects | 100% (`AX-11`) |
| Open Critical or High accessibility defects at a portal release | **Zero** — `PS-04` is contractual |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Severity is set by task impact, not by criterion count:**

| Impact | Severity |
|---|---|
| An assisted user **cannot complete** the portal's `AX-04` task | **Critical** |
| An assisted user can complete it only with help, or only in English | **High** |
| A criterion fails without blocking the task | Medium |
| A criterion fails on a low-traffic path | Low |

**One automatic escalation:** a portal released with an open Critical or High accessibility defect
escalates to the CTO **and Legal Counsel**, because `PS-04` is a contractual commitment and shipping
against it is a contractual matter rather than a quality trade-off.

---

## 6. Sign-off

| Portal | Accessibility reviewer | Bengali assisted tester | Business role | Release | Date | Signature |
|---|---|---|---|---|---|---|
| `P01` | | | | | | |
| `P03` | | | | | | |
| `P04` | | | | | | |
| `P05` | | | | | | |
| `P06` | | | | | | |
| `P07` | | | | | | |
| `P08` | | | | | | |
| `P10` | | | | | | |
| `P12` | | | | | | |
| **Pack acceptance** — Content Design Lead with QA Lead | | | | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is registered `P2`/W2, and `PS-04` is contractual with `P03` releasing at W1.** `05-06` §11 requires the accessibility audit *before each portal release*, `NFR-073` is `P1`, and `06-02` `G1-08` gates on translation coverage at Month 4. **A `P2` priority on a contractual requirement, in the wave after the first portal ships, is the wrong position on both axes** — the eighth sequencing instance in this category and the only priority challenge | Programme Content Lead with Content Design Lead | **W1 — register correction on priority and wave** |
| **O-02** | **No accessibility reviewer is named — the fourth consecutive request.** `AUDIT-009` TR-03, `AUDIT-010` HC-10, `TR-003` `O-02`, `HC-002` `O-04` and `HC-016` `O-04` all record it, and `AUDIT-010` R-09 escalated it under check `G1` for reaching three consecutive audits. **This pack cannot be executed without the role it depends on** | Content Design Lead | **W1 — escalated; four requests** |
| **O-03** | **No Bengali-speaking assisted tester is sourced.** `AX-02`, `CG-011` §8.2 and `VB-009` `AC-06` all require one, and 9 of the 189 scripts are `P0` and depend entirely on this person. **Recruiting an assisted tester who reads Bengali and uses their own assistive technology is a sourcing task nobody owns**, and it is not the same task as `O-02` | Content Design Lead with HR | **W2 — before the first audit** |
| **O-04** | **`P06` is Metabase and Grafana embedded, and its accessibility is largely not ours to fix.** `AX-03` and `N-07` handle it honestly by reporting a partial conformance with the boundary named, **but `PS-04` says "all web portals" without qualification.** Either `PS-04` acknowledges third-party embedding or `P06` cannot claim conformance | CTO with Legal Counsel | **W4 — before `P06` releases** |
| **O-05** | **`PS-04` covers web portals only; `P02`, `P09` and `P11` are Flutter applications used by 275–635 people in bright sunlight, with gloves, one-handed, on 5-inch screens.** Those are accessibility conditions WCAG addresses directly, and no requirement covers them. **This pack has no authority to extend `PS-04`**, so the gap is reported rather than filled | CTO with Content Design Lead | **W2 — specification decision** |
| **O-06** | **189 scripts × per-release execution is unestimated.** `AX-01` requires both methods before **every** portal release, and `06-01` §5 sets a monthly production cadence. A full manual audit of nine portals monthly is not feasible; **a risk-based per-release subset with a full audit per wave gate is the likely answer, and it needs deciding rather than discovering** | QA Lead with Content Design Lead | **W2** |
| **O-07** | **Category 19 is written (2026-08-18) and the owning specifications now exist**: `MM-002` §4.6 for screenshots, `MM-003` §4.6 for diagrams including the SVG `title`/`desc` pattern, `MM-001` §4.7 for captions, transcripts and audio description, and `RP-007` for charts. **`MM-003` `O-02` records that the SVG accessibility pattern carries `class: P3` and converts to `P1` only on this pack's screen-reader pass** — which still has no named accessibility reviewer and no Bengali-speaking tester | Brand Lead with Content Design and QA | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; the by-WCAG-principle organisation justified
- [x] **The automated-versus-manual distinction stated row by row, which is what `05-06` §11's "plus" requires**
- [x] The reciprocal reference from `CG-011`, `VB-003`, `VB-009` and `UI-010` acknowledged, and the rule-versus-procedure boundary stated (`CP-01`)
- [x] Twelve rules stated, including per-criterion conformance reporting and task completion as the real test
- [x] **Scope stated as nine web portals, with the three Flutter apps' exclusion reported as a specification gap rather than silently extended**
- [x] 21 scripts per portal mapped to numbered WCAG 2.1 AA success criteria, 189 in total
- [x] A specific `AX-04` task named per portal, chosen as the portal's primary purpose
- [x] **Bengali screen-reader task completion made a `P0` exit criterion for all nine portals**
- [x] Bengali expansion tested at both `05-06` §10 resolutions (`AX-09`, `AX-10`)
- [x] Nine edge cases stated, including a clean scan reported as conformance and third-party embedding
- [x] Severity set by task impact rather than criterion count, with the scale stated
- [x] Automatic escalation to CTO and Legal because `PS-04` is contractual
- [x] All internal links resolve
- [x] Seven open items recorded, including the fourth request for an accessibility reviewer
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 189 per-script procedures — outstanding; this file specifies and enumerates**
- [ ] **`O-01` `P2`/W2 position on a contractual requirement — outstanding; register correction**
- [ ] **`O-02` no accessibility reviewer — outstanding; fourth request, escalated**
- [ ] **`O-03` no Bengali assisted tester — outstanding; 9 `P0` scripts depend on one person**
- [ ] **`O-06` per-release execution volume undecided — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and QA Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
