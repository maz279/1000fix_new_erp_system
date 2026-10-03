---
id: HC-016
title: In-Product Help, Tour and Coach Mark Copy
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with the portal product teams
reviewers: [Customer Service Manager, Operations Director, Accessibility reviewer, Localisation Lead, CTO, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The first-run tours, contextual tips, coach marks, feature-announcement copy and dismissal rules
  that put help where the task is. Help that requires leaving the task is help that is not read —
  and across twelve portals, the moment a user opens a separate help centre is the moment most of
  them stop and ask a colleague instead.
traces_to: [M22, M30, M61, P01, P02, P03, P04, P09, P10, HC-001, HC-002, HC-003, HC-008, HC-015, UI-006, UI-008, CG-011, VB-006, TR-024]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy_BN.md
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md — zero-data, no-results, not-yet-configured and first-login copy; on day one of every wave, every screen is empty
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md — copy rules bound to components; one component library across twelve portals needs one copy contract
    verified: 2026-08-18
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md — WCAG 2.1 AA is contractual; time limits and dismissal behaviour are accessibility concerns
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# In-Product Help, Tour and Coach Mark Copy

| Item | Value |
|---|---|
| Portal | **All twelve** |
| Audience | All eleven audiences, scoped per surface |
| Article type | **In-product help** — object type 5 (`HC-001` §4.2) |
| Reading level target | `CG-011`; **read in passing, not read deliberately** |
| Languages | Bengali and English per surface |
| Related UI copy | `UI-006` empty states and first run · `UI-008` loading and progress · `VB-006` component copy standards |

> **Template conformance.** `TPL_Help_Article.md` applied at library level, as `CG-009` §3 requires.
> All sections retained in order with library-level interpretation.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) | In-product help is entry path 1 (`HC-001` §4.6) — the primary path, not a supplement |
| [`HC-002_Help_Article_Template_and_Style_Rules.md`](HC-002_Help_Article_Template_and_Style_Rules.md) | Style, reading level, bilingual rules |
| `UI-006` first-run and empty-state copy · `VB-006` component copy contract | **The boundary — see below** |

**`PS-33`: the boundary with `UI-006` and `VB-006` is the one this file must not blur.**

| Copy | Owner | Test |
|---|---|---|
| The screen has no data yet, and here is what to do | **`UI-006`** empty states | It is part of the screen |
| The component's own label, hint, toast or validation text | **`VB-006`** / `UI-003` | It is part of the component |
| **A layer over the screen, teaching something the screen does not say** | **`HC-016`** — this file | It can be dismissed and the screen still works |
| A page you navigate to | `HC-003`…`HC-014` | You left the task |

**`PS-34`: if removing it breaks the screen, it is not in-product help.** That is the operational
test, and it keeps three content sets out of each other's way.

---

## Steps — *the in-product help types and their rules*

### Type 1 — First-run tour

| # | Rule |
|---|---|
| **PT-01** | **Maximum five steps.** A tour longer than five is a course (`TR-*`) |
| **PT-02** | Each step teaches **one thing the user could not work out**, not one thing on the screen |
| **PT-03** | Skippable at every step, and **skipping is remembered** |
| **PT-04** | Never blocks the task; a user who wants to start can start |
| **PT-05** | Re-runnable on demand from a stable location |
| **PT-06** | Fires **once per surface per user**, not once per session |

### Type 2 — Coach mark

| # | Rule |
|---|---|
| **PT-07** | One idea, **maximum 15 words** |
| **PT-08** | Anchored to the thing it describes; if the anchor moves, the coach mark is withdrawn, not floated |
| **PT-09** | **Maximum two on a screen at once**; more is a design problem |
| **PT-10** | Dismissible, and dismissal is permanent for that user (`PT-14`) |
| **PT-11** | Never used to apologise for a confusing interface — **that is product feedback** |

### Type 3 — Contextual tip

| # | Rule |
|---|---|
| **PT-12** | Appears on request or on a genuine signal — repeated error, hesitation, a first-time action |
| **PT-13** | Maximum 30 words, and links to the article if more is needed |
| **PT-14** | **Frequency-capped**: no user sees the same tip more than three times, ever |
| **PT-15** | A tip on a destructive action is not a tip; it is a confirmation (`UI-007`) |

### Type 4 — Feature announcement

| # | Rule |
|---|---|
| **PT-16** | States **what changed for you**, not what was built |
| **PT-17** | Fires once, dismissible, and never on a user's first session on that surface |
| **PT-18** | Issued through `TR-024` release training, not independently — **one release, one message** |
| **PT-19** | Never announces a change the user cannot yet use |

### Type 5 — Metric and field definition surfacing

| # | Rule |
|---|---|
| **PT-20** | A metric's definition is reachable **from the metric** (`HC-008` `O-03`), and it links to `RP-001` rather than restating it |
| **PT-21** | A field's help text belongs to `UI-003`; this type surfaces it, it does not duplicate it |

### Cross-cutting rules

| # | Rule | Class |
|---|---|:--:|
| **PT-22** | **Nothing is undismissible except a safety or legal notice** | **H** |
| **PT-23** | Dismissal state is stored per user and survives sessions and devices | **H** |
| **PT-24** | **No timed auto-advance** — `CG-011` prohibits time limits the user did not choose | **H** |
| **PT-25** | Bengali authored for customer-, technician- and rider-facing surfaces (`HS-29`) | **H** |
| **PT-26** | Laid out for Bengali length; a coach mark that fits in English and overflows in Bengali is broken (`HS-33`) | **H** |
| **PT-27** | Screen-reader accessible; a coach mark invisible to assistive technology is an accessibility failure, not a visual nicety | **H** |
| **PT-28** | **Total in-product help on any screen is capped**; if a screen needs a tour, two coach marks and three tips, the screen is the problem | **S** |

> **`PT-11` and `PT-28` say the same thing twice deliberately.** In-product help is the cheapest
> way to paper over a confusing interface, and it is the most common. The content function has to
> be able to say *"this is a design problem"* and be heard — which `TR-007` `O-01` and `HC-012`
> `O-01` both depend on elsewhere.

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Users find help without leaving the task | **In-product help opens vs help-centre visits** | In-product dominant |
| First-run tours are completed rather than skipped | Tour completion | > 60%; **a very low rate means the tour is not earning its place** |
| Tips reduce errors | Error rate on tipped actions | Falling |
| Announcements are read | Dismissal-without-read rate | Falling |

**`PS-35`: a high skip rate is information, not failure.** A tour skipped by 80% of users is a tour
that is not needed, and the correct response is to remove it — not to make it undismissible.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Users dismiss everything immediately | Too much, too often, or not relevant | `PT-14`, `PT-28` — reduce before rewriting |
| Coach marks obscure the task | Anchoring or count | `PT-08`, `PT-09` |
| The same tip keeps returning | Dismissal state not persisted | `PT-23` — a product defect, not a content one |
| Bengali overflows | Laid out for English | `PT-26` |
| In-product help used to explain a rename | It is a release matter | `TR-024` `RL-04`, `PT-18` |
| Tours added instead of fixing a screen | `PT-11` | Raise as product feedback and record that it was raised |

---

## Related

`UI-006` · `UI-008` · `UI-003` · `UI-007` · `VB-006` ·
[`HC-001_Help_Centre_Information_Architecture.md`](HC-001_Help_Centre_Information_Architecture.md) §4.6 — path 1 ·
[`HC-015_FAQ_Bank_by_Audience.md`](HC-015_FAQ_Bank_by_Audience.md) — tips link to FAQ items ·
[`09A_Help_Sets_By_Portal/HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md`](09A_Help_Sets_By_Portal/HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md) — type 5 is how article 1 of that set is actually reached ·
[`../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) — `PT-18` ·
[`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md).

---

## Feedback

Dismissal, completion and repeat-view telemetry per item, reported monthly. **`PS-36`: the primary
measure is whether in-product help reduces help-centre visits for the same task** — if both rise
together, the task is too hard and neither content set is the answer.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Items required | **~120 across twelve portals** — tours ~15, coach marks ~45, tips ~40, announcements per release, metric surfacing ~20 |
| Items written | **0** |
| Effort | 120 × 0.5–1 h = **60–120 hours**, plus Bengali and accessibility review |
| Sequencing | `P03` and `P01` at W1–W2 with their portals; others per portal wave |
| **Dependency** | **Every item must be authored against a built screen**; none can be written in advance |
| Bengali | All customer-, technician- and rider-facing items authored in Bengali |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Whether each portal supports tours, coach marks, dismissal persistence and frequency capping is unconfirmed.** `PT-14`, `PT-23` and `PT-24` are product capabilities, not content; if they are absent, most of this file is unimplementable | CTO with the portal teams | **W2 — before authoring** |
| **O-02** | **`HC-005` `P03` help is W1 but this file is W2**, and `P03` is the surface most in need of in-product help at go-live. The same sequencing problem `HC-005` `O-01` records | Programme Content Lead | **W1** |
| **O-03** | Type 5 metric surfacing depends on `RP-001`, unwritten (`HC-008` `O-01`), and on a product path from a number to its definition (`HC-008` `O-03`) | BI Lead with CTO | W4 |
| **O-04** | Accessibility reviewer unowned — the third file to record it after `TR-003` `O-02` and `HC-002` `O-04` | Content Design Lead | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at library level; additions justified
- [x] **Boundary with `UI-006` and `VB-006` stated with an operational test (`PS-33`, `PS-34`)**
- [x] Five in-product types with bounded length, count and frequency
- [x] Dismissal permanent and persisted; nothing undismissible except safety or legal (`PT-22`)
- [x] No timed auto-advance, per `CG-011` (`PT-24`)
- [x] Bengali authored and laid out for Bengali length
- [x] **In-product help explicitly prohibited from papering over interface problems (`PT-11`, `PT-28`)**
- [x] High skip rate treated as information rather than failure (`PS-35`)
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` portal capability confirmation — outstanding; much of this file depends on it**
- [ ] **`O-02` `P03` needs this at W1 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
