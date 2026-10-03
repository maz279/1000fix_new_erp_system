---
id: MM-008
title: Animated Explainer Brief — Portal Onboarding
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design with Brand
author: Content Design with Brand, Design System, Localisation and the portal product teams
reviewers: [Content Design Lead, Brand Lead, Design System Lead, Localisation Lead, Accessibility reviewer, portal owners, Marketplace Operations, Account Management, Procurement, Partnerships, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The production specification for the short onboarding animations shown at first run in each
  externally-facing portal. HC-016 fixes the copy and the behaviour of in-product help and caps a
  first-run tour at five steps; nothing states what a moving asset inside that tour must be. Six
  external audiences with documented adoption targets meet the product for the first time on these
  screens, and an animation is the one asset class that can fail accessibility by existing — it
  moves without being asked, it can be undismissible, and it can carry the whole explanation in a
  form a screen reader cannot reach. The brief exists to make the moving version an improvement on
  the static one rather than a replacement for it.
traces_to: [HC-001, HC-015, HC-016, UI-005, UI-006, UI-008, UI-040, UI-042, VB-001, VB-002, VB-003, VB-006, VB-009, CG-003, CG-008, CG-010, CG-011, CG-012, BN-012, BN-013, EO-001, EO-003, EO-005, EO-007, EO-009, EO-010, MM-001, MM-004, MM-005, MM-007, MM-011, MM-012, TS-016, P01, P04, P05, P07, P08, P09, P12, 04-00 PS-03, 04-00 PS-04, 04-00 PS-05, 04-00 §P01, 04-00 §P07, 05-06 NFR-073]
priority: P3
wave: W6
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md PT-01 maximum five tour steps, PT-03 skippable at every step and skipping remembered, PT-04 never blocks the task, PT-06 once per surface per user, PT-22 nothing undismissible except a safety or legal notice, PT-24 no timed auto-advance, PT-26 laid out for Bengali length, PT-27 screen-reader accessible, PT-28 total in-product help capped, PT-11 never used to apologise for a confusing interface; PS-35 a high skip rate is information
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md §4 — full brand on first-run tours and onboarding, "introductory, not operational"; §5 corner radius, shadows minimal, "depth cues cost rendering and attention"; §6 brand excluded from P02 job flow, P09 and the P11 offline bundle
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — the externally-facing portals and their adoption targets, including P07 seller onboarding completion above 60% of started registrations; PS-03 Bengali default on customer and field surfaces; PS-04 WCAG 2.1 AA; PS-05 responsive from 320px
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 2.2.2 pause, stop, hide (Level A) for moving content that starts automatically, lasts more than five seconds and is presented alongside other content; SC 2.3.1 three flashes (Level A); SC 1.1.1 non-text content; SC 2.3.3 animation from interactions (Level AAA, adopted here as the prefers-reduced-motion obligation)
    verified: 2026-08-18
    class: P1
  - source: project_content/18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md §4.1 the nine-stage onboarding journey and the completion funnel stages 1–6; SO-01 the document set is stated in full before stage 2
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Animated Explainer Brief — Portal Onboarding

| Item | Value |
|---|---|
| Governs | Short animated explainers shown at first run in the externally-facing portals |
| Copy and behaviour authority | [`HC-016`](../09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) — **this file animates; `HC-016` writes and decides when it fires** |
| Portals in scope | `P01`, `P04`, `P05`, `P07`, `P08`, `P12` — **six external portals**; `P09` as a stated exception |
| Language of the output | **Bengali-first on `P01`, `P07`, `P09`** (`PS-03`); English on `P04`, `P05`, `P08`, `P12` per `CG-010` §3.3 |
| Wave | W6 · Months 23–26 (`06-01` §3) — **and `HC-016` is W2. See `O-01`** |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.7.
> §7 Open Items added per category convention.

---

## 1. Purpose

The register's justification is a claim about leverage: *"first-run explanation is the
highest-leverage moment for adoption in every external portal."* It is supported by the numbers
those portals carry — `P07` seller onboarding completion **above 60% of started registrations**,
`P04` corporate portal adoption **above 85% of contracted clients**, `P08` brand claims **above
80% through the portal**, `P05` vendor **above 90% PO acknowledgement**.

`HC-016` already governs the moment: a first-run tour of **at most five steps** (`PT-01`), each
teaching *"one thing the user could not work out"* (`PT-02`), skippable at every step (`PT-03`),
never blocking the task (`PT-04`), firing once per surface per user (`PT-06`).

**What is missing is what a moving asset inside that tour may be** — and animation is the asset
class where the wrong answer does the most damage.

| Absent | Consequence |
|---|---|
| A length and weight budget | A 30-second animated intro on the first screen of a portal reached over mobile data |
| An accessibility position | Motion that starts by itself, cannot be paused, and carries the explanation in a form no screen reader reaches — three Level A failures in one asset |
| A silent-by-default rule | Sound firing in a shared office or on a bus, on the user's very first interaction |
| A boundary against `MM-007` | Animation used where a 90-second video already exists, or the reverse |
| A text-layer separation rule | Six portals × two languages re-animated rather than re-rendered |
| A "when not to animate" test | Motion used to soften a confusing screen, which `HC-016` `PT-11` explicitly prohibits |

**Consequence of absence (`CP-03`).** The first thing six external audiences ever see is either
nothing, or a moving asset that blocks them, excludes assistive-technology users, costs them data
and teaches them the product is decorative rather than usable.

**What this file is not.** It is not the tour copy or its firing rules (`HC-016`), not the
customer how-to video series (`MM-007` — §4.2 draws the boundary), not empty-state artwork
(`MM-005`), not the registration flow copy (`UI-040`), and not the onboarding kits the animations
sit alongside (`EO-001`…`EO-010`).

---

## 2. Scope

**In scope.** The inventory per portal; the decision test for animating at all; the boundary with
video and with static artwork; duration, weight and format; motion design constraints;
**accessibility, including the three Level A obligations motion can breach**; the text-layer
separation that makes bilingual delivery affordable; distribution and first-run behaviour; the
deliverable specification; and rules `AN-01`…`AN-26`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Tour copy, step count, firing, dismissal, frequency capping | [`HC-016`](../09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) |
| First-run and empty-state copy | [`UI-006`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) |
| Registration and onboarding flow copy | [`UI-040`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md) |
| The onboarding kits issued outside the product | [`EO-001`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md) … [`EO-010`](../18_Ecosystem_Onboarding_Content/EO-010_Franchise_and_Channel_Partner_Pack.md) |
| Customer how-to video | [`MM-007`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) |
| Static illustration | [`MM-005`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) |
| Icons appearing inside an animation | [`MM-004`](MM-004_Icon_Set_Requirements.md) |
| Encoding, metadata, acceptance | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) |
| Naming, versioning, retirement | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Motion designer / animation supplier** | The acceptance specification attached to the purchase order | Before quoting |
| **Portal product teams** | What their first-run surface must support, and what it must not do | At build |
| **Content Design** | The pairing with `HC-016` copy and the when-not-to-animate test | Per portal |
| **Design System** | Consistency with the icon and illustration families | At review |
| **Accessibility reviewer** | §4.5 — three Level A criteria that motion can breach on its own | At acceptance |
| **Localisation Lead** | §4.6 — why the text layer is separated | At planning |
| **Ecosystem owners** (Marketplace Ops, Account Management, Procurement, Partnerships) | What their audience is shown at first contact | At approval |

---

## 4. Content

### 4.1 The inventory

**One explainer per external portal**, aligned to that portal's first-run tour (`HC-016` type 1).

| # | Portal | Audience | Adoption target it serves | Explainer subject | Language |
|---:|---|---|---|---|---|
| **A1** | **`P01`** Customer | 250,000+ a month | Booking and tracking adoption | **Book, track, approve, collect** — the four things a customer does | **Bengali-first** |
| **A2** | **`P04`** Corporate | 500–2,000 users | **> 85% of contracted clients** | **Raise a request, see your estate, approve** | English (`CG-010` §3.3 partly) |
| **A3** | **`P05`** Vendor | Supplier base | **> 90% PO acknowledgement** | **Acknowledge a PO, submit an invoice, see your score** | English |
| **A4** | **`P07`** Seller | 500–2,000 | **> 60% registration completion** | **What we ask for, what verification means, how you get paid** | **Bengali-first** |
| **A5** | **`P08`** Brand partner | 17+ | **> 80% of claims through the portal** | **Submit a claim with the evidence it needs** | English |
| **A6** | **`P12`** Partner / referral | Partners and franchisees | **> 12% of new customers referral-attributed** | **Refer, track attribution, get paid** | English |
| **A7** | **`P09`** Rider — **exception** | 50–200 | Custody integrity | **Scan, seal, deliver, collect** | **Bengali-first** |

| # | Rule |
|---|---|
| **AN-01** | **One explainer per portal. Not one per feature.** `HC-016` `PT-28` caps the total in-product help on a screen, and `PT-01` caps a tour at five steps; an inventory that grows per feature defeats both |
| **AN-02** | **The explainer covers what a first-time user could not work out** (`PT-02`) — not a feature tour. A1 is *"book, track, approve, collect"*, not *"here is the navigation"* |
| **AN-03** | **A4 is the highest-value item and it is produced first.** `EO-001` §4.1 identifies **stage 4, document submission, as the highest-drop-off stage** in a nine-stage funnel measured against a 60% target, and `HC-020` script 9 addresses the same step in video. **The two must say the same thing** — see `AN-05` |
| **AN-04** | **`P09` is an exception and is treated as one.** `VB-003` §6 excludes brand from `P09` entirely, and `VB-007` §4 calls the rider case *"absolute"* on ambiguity. **A7 is produced only if `HC-016` `O-01` confirms `P09` supports a tour at all**, and it carries no brand styling |
| **AN-05** | **Where an explainer and a `MM-007` video address the same task, one of them is withdrawn.** Two assets teaching the same step diverge at the first change; A4 and script 9 are the live case and Content Design decides which survives at commissioning |
| **AN-06** | **`P02`, `P03`, `P06`, `P10`, `P11` get no explainer.** They are operational or internal surfaces; `VB-003` §5 and §6 exclude decorative motion from them, and their users are trained under `TR-*` rather than onboarded |

### 4.2 The decision test, and the boundary with video and static art

**`AN-07`: animate only where movement is the information.**

| The thing being explained | Correct asset |
|---|---|
| **A relationship that changes over time** — a job moving through states, a claim being matched, money moving | **Animation** |
| **A spatial or physical action** — photographing a document, sealing a package | **Video** (`MM-007`, `VS-17`) |
| **A single moment or object** | **Static illustration** (`MM-005`) or nothing |
| **A sequence of screens** | **The tour itself** (`HC-016` type 1) — anchored coach marks on the real UI, not a re-drawn one |
| **A concept the copy already carries** | **Nothing.** `PT-02` requires each step to teach something the screen does not say |

| # | Rule |
|---|---|
| **AN-08** | **An animation never re-draws the product's own UI.** A drawn interface ages faster than the real one and orphans on the first redesign — the `TR-003` `DS-12` and `HC-002` `HS-17` reasoning applied to motion, where the cost of being wrong is highest |
| **AN-09** | **Animation is never used to soften or excuse a confusing screen.** `HC-016` `PT-11` and `PT-28` say this twice deliberately; a motion budget spent on an unusable flow is a product defect wearing a coat |
| **AN-10** | **The explainer is not required for the portal to be usable.** If removing it breaks onboarding, the onboarding is broken (`HC-016` `PS-34`) |

### 4.3 Duration, weight and format

| Property | Specification |
|---|---|
| **Duration** | **≤ 20 seconds** per explainer; **≤ 6 seconds** per tour-step animation |
| **Loop** | **Plays once by default.** Looping is permitted only for a ≤ 3-second ambient element and only where `AN-16` is satisfied |
| **Format — master** | **Lottie JSON** (vector, scriptable, text separable) |
| **Format — fallback** | **MP4 H.264** at the `MM-001` §4.5 L2 rung, **and a static first-frame PNG** |
| **Weight** | **≤ 100 KB Lottie**; ≤ 500 KB MP4; **the static PNG is always the smallest and always ships** |
| **Frame rate** | 30 fps; **motion designed to read at 24 fps** on a mid-range device |
| **Canvas** | 400 × 300 nominal, vector; renders 320 px wide upward (`PS-05`) |
| **Colour** | The `MM-005` §4.1 palette — two colours plus neutrals; **`#39B1DF` as a fill only** (`VB-003` `BC-03`) |
| **Style** | The `MM-005` illustration family and the `MM-004` stroke weight. **An animation is a moving illustration, not a third visual language** |

| # | Rule |
|---|---|
| **AN-11** | **Lottie is the master because the text layer stays separable** (`AN-19`) and because a vector animation scales without a second render per density |
| **AN-12** | **The MP4 fallback and the static PNG are not optional.** A surface that cannot run Lottie shows the MP4; a surface that will not autoplay, or a user who has asked for reduced motion, shows the PNG — **and the PNG alone must carry the point** |
| **AN-13** | **Weight is measured on the delivered file including embedded assets.** A Lottie with a rasterised background embedded is a raster asset with a JSON wrapper |
| **AN-14** | **No embedded raster inside a Lottie**, no embedded font, no expressions requiring a runtime feature the portal's player does not support — **confirmed against the actual player, per portal, before delivery** |

### 4.4 Motion design

| # | Rule |
|---|---|
| **AN-15** | **Motion is functional, not expressive.** Objects move to show a relationship changing. No bounce, no overshoot, no elastic easing, no parallax, no confetti |
| **AN-16** | **Nothing moves in the background of a screen the user is trying to read.** SC 2.2.2 governs anything that starts automatically, runs more than five seconds and sits alongside other content; **the safest design is one that never triggers it** |
| **AN-17** | **Silent. Always.** No sound, no music, no narration in an in-product animation. The user is meeting the product for the first time, possibly in a shared office, on a bus, or in front of a customer |
| **AN-18** | **One idea per animation**, matching `MM-005` `IL-01` and `HC-016` `PT-02`. Three things moving at once reads as none |
| **AN-19** | **Easing is standard and shared**: 200–300 ms transitions, `ease-out` for entry and `ease-in` for exit, matching the design system's motion tokens where they exist |
| **AN-20** | **Depth cues are minimal** — `VB-003` §5 states the reason: *"depth cues cost rendering and attention"*, on a device class with 3 GB of RAM |

### 4.5 Accessibility — the three Level A criteria motion can breach on its own

**This is the section that makes animation different from every other asset class in this
category.** A static image cannot fail an accessibility criterion by existing. An animation can
fail three.

| Criterion | How an animation breaches it | The rule |
|---|---|---|
| **SC 2.2.2 Pause, Stop, Hide (A)** | It starts automatically, runs over five seconds, and sits beside content the user is reading | `AN-21` |
| **SC 2.3.1 Three Flashes (A)** | A transition, a highlight pulse or a fast cut exceeds three flashes in a second | `AN-22` |
| **SC 1.1.1 Non-text Content (A)** | It carries the whole explanation and offers no text alternative | `AN-23` |

| # | Rule |
|---|---|
| **AN-21** | **Every animation is pausable and dismissible**, and **anything running over five seconds beside other content provides a visible pause control** (SC 2.2.2). `HC-016` `PT-22` already makes nothing undismissible except a safety or legal notice, and `PT-24` prohibits timed auto-advance — **an animation must not reintroduce a timer the tour deliberately removed** |
| **AN-22** | **Nothing flashes more than three times in any one second** (SC 2.3.1). This is measured on the rendered output, not assumed from the design |
| **AN-23** | **The animation is never the only carrier.** The `HC-016` tour-step copy carries the point in text; **the animation is decorative and marked decorative** (`MM-005` `IL-22` pattern). Where the animation would carry something the copy does not, **the copy is amended** — not an alternative description written |
| **AN-24** | **`prefers-reduced-motion` is honoured**: the static first frame replaces the animation entirely, and the experience is complete without motion. Adopted from SC 2.3.3, which is Level AAA — **this programme adopts it as an obligation because the device class and the audience make it a usability requirement, not an enhancement** |
| **AN-25** | **The tour containing the animation is screen-reader accessible** (`HC-016` `PT-27`) — a coach mark invisible to assistive technology is an accessibility failure, not a visual nicety, and an animated one is worse because focus may move under it |
| **AN-26** | **Contrast obligations are unchanged by motion.** Any shape a user must perceive meets 3:1 (SC 1.4.11), measured on the frames where it matters, not on the master artwork |
| **AN-27** | **No text is animated character by character**, and no text is rendered as a moving image (SC 1.4.5). Text is the separate layer in `AN-28` |

### 4.6 Language and the separable text layer

| # | Rule |
|---|---|
| **AN-28** | **Text lives in a separate, named layer and is never baked into the animation.** This is what turns six portals × two languages from twelve productions into **six productions and six re-renders** — the `MM-001` `AS-18` rule applied where it saves the most |
| **AN-29** | **The layout holds the Bengali length**, which runs 20–40% longer (`HC-016` `PT-26`, `VB-007` `BL-02`). A caption that fits in English and overflows in Bengali is broken, and in an animation it is broken in motion |
| **AN-30** | **Bengali on-screen text meets the `VB-009` §3 floors at the rendered size**, not at canvas size |
| **AN-31** | **`P01`, `P07` and `P09` explainers are Bengali-first** (`PS-03`); `P04`, `P05`, `P08` and `P12` follow `CG-010` §3.3's audience rule and are English |
| **AN-32** | **The safest animation carries no text at all** and lets the `HC-016` tour copy do the talking. **Where that is achievable it is preferred**, and it removes `AN-28`…`AN-30` entirely |

### 4.7 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **Lottie JSON**, vector only, **no embedded raster, no embedded font, no unsupported expressions** |
| **Derived formats** | **MP4 H.264** at `MM-001` §4.5 L2; **static first-frame PNG** (mandatory) |
| **Dimensions** | 400 × 300 nominal vector canvas; renders from 320 px width (`PS-05`) |
| **Duration** | **≤ 20 s** explainer · **≤ 6 s** per tour step · **≤ 3 s** for any looping element |
| **Frame rate** | 30 fps, legible at 24 fps on the device floor |
| **Colour** | `MM-005` §4.1 palette, sRGB; **light and dark variants authored** (`MM-001` `CS-08`) |
| **Weight** | **≤ 100 KB Lottie**; ≤ 500 KB MP4; PNG ≤ 40 KB |
| **Audio** | **None** (`AN-17`) |
| **Text** | **Separate named layer**, or absent (`AN-28`, `AN-32`) |
| **Accessibility** | Pausable and dismissible; no flashing; decorative with the copy carrying the point; `prefers-reduced-motion` → static frame; contrast verified on the frames that matter |
| **Metadata** | Title, portal, audience, `HC-016` tour step served, language, author, licence |
| **Naming** | `MM-012` §4.3, carrying the portal identifier |
| **Source** | Editable animation project file with layers named and the text layer isolated (`MM-001` `DL-02`) |
| **Evidence** | **Player-compatibility confirmation per portal** (`AN-14`) · **flash-rate measurement** (`AN-22`) · reduced-motion behaviour demonstrated |

### 4.8 First-run behaviour

**Owned by `HC-016`; restated here only as the constraints an animation must be built to satisfy.**

| Behaviour | Rule | Owner |
|---|---|---|
| Fires once per surface per user | `PT-06` | `HC-016` |
| Skippable at every step, and skipping remembered | `PT-03` | `HC-016` |
| Never blocks the task | `PT-04` | `HC-016` |
| Re-runnable on demand from a stable location | `PT-05` | `HC-016` |
| Dismissal persists across sessions and devices | `PT-23` | `HC-016` |
| **No timed auto-advance** | `PT-24` | `HC-016` — and `AN-21` here |
| A high skip rate is information, not failure | `PS-35` | `HC-016` |

| # | Rule |
|---|---|
| **AN-33** | **An animation must work when the user skips it at second two.** Everything essential is in the tour copy and in the first frame; **the motion is the enhancement, never the payload** |
| **AN-34** | **A low completion rate retires the animation.** `HC-016` `PS-35` says a tour skipped by 80% of users should be removed rather than made undismissible; the same applies to the asset inside it, and the effort is written off rather than defended |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../09_Help_Centre_and_Self_Service/HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) | The copy, the firing rules, `PT-01`…`PT-28`, `PS-33`…`PS-36` — everything §4.8 restates by reference |
| [`HC-001_Help_Centre_Information_Architecture.md`](../09_Help_Centre_and_Self_Service/HC-001_Help_Centre_Information_Architecture.md) · [`HC-015_FAQ_Bank_by_Audience.md`](../09_Help_Centre_and_Self_Service/HC-015_FAQ_Bank_by_Audience.md) | Where in-product help leads next |
| [`UI-006_Empty_State_and_First_Run_Copy_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-006_Empty_State_and_First_Run_Copy_Library.md) · [`UI-040_Registration_and_Onboarding_Flow_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-040_Registration_and_Onboarding_Flow_Copy.md) | The first-run copy an explainer sits beside; the registration flow A4 explains |
| [`UI-005_System_Permission_and_Session_Message_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-005_System_Permission_and_Session_Message_Library.md) · [`UI-008_Loading_Progress_and_Long_Running_Job_Copy.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-008_Loading_Progress_and_Long_Running_Job_Copy.md) · [`UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | Adjacent first-run surfaces motion must not obstruct |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | §4 full brand on first-run; §5 minimal depth cues; §6 the `P09` exclusion behind `AN-04` |
| [`VB-006_Design_System_Content_Standards.md`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) · [`VB-002_Persona_and_Portal_Tone_Matrix.md`](../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md) | The component the animation sits in; the register per audience |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-012_Bengali_String_Bundle_P04_to_P06.md`](../11_Localisation_Bengali/BN-012_Bengali_String_Bundle_P04_to_P06.md) · [`BN-013_Bengali_String_Bundle_P07_to_P12.md`](../11_Localisation_Bengali/BN-013_Bengali_String_Bundle_P07_to_P12.md) | On-screen text floors and the Bengali strings for the portals in scope |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | §4.5 obligations and where they are verified |
| [`CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §3.3's audience rule behind `AN-31` |
| [`EO-001_Marketplace_Seller_Onboarding_Kit.md`](../18_Ecosystem_Onboarding_Content/EO-001_Marketplace_Seller_Onboarding_Kit.md) | §4.1 stage 4 — the drop-off A4 addresses |
| [`EO-003_Brand_Partner_Onboarding_Pack.md`](../18_Ecosystem_Onboarding_Content/EO-003_Brand_Partner_Onboarding_Pack.md) · [`EO-005_Vendor_and_Supplier_Onboarding_Pack.md`](../18_Ecosystem_Onboarding_Content/EO-005_Vendor_and_Supplier_Onboarding_Pack.md) · [`EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md`](../18_Ecosystem_Onboarding_Content/EO-007_Corporate_Client_Onboarding_and_Welcome_Kit.md) · [`EO-009_Referral_and_Alliance_Partner_Kit.md`](../18_Ecosystem_Onboarding_Content/EO-009_Referral_and_Alliance_Partner_Kit.md) | The kits A2, A3, A5 and A6 sit alongside, and whose targets they serve |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | Class A9 format, the L2 fallback rung, metadata, acceptance |
| [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) · [`MM-005_Illustration_and_Empty_State_Artwork_Brief.md`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) | The visual family an animation must belong to, not extend |
| [`MM-007_Video_Production_Brief_Customer_How_To_Series.md`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) | The `AN-05` overlap — A4 and `HC-020` script 9 |
| [`MM-011_Email_and_HTML_Asset_Specification.md`](MM-011_Email_and_HTML_Asset_Specification.md) | Where animation is **not** used — email (`MM-011` §4.3) |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, versioning, retirement on `AN-34` |
| `04-00` §P01, §P07, `PS-03`, `PS-04`, `PS-05` | The portals, their targets, Bengali default, AA, and 320 px responsiveness |

| Depended on by |
|---|
| `HC-016` type 1 first-run tours · the six external portals' onboarding surfaces · `EO-001`…`EO-010` (the in-product half of an onboarding kit) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per portal release** affecting a first-run flow; annually for the standard |
| Trigger for out-of-cycle review | A registration or onboarding flow change · a completion-rate movement · a skip-rate above the `PS-35` threshold · an accessibility finding · a player or framework change breaking `AN-14` · an `AN-05` overlap emerging with `MM-007` |
| Owner | **Content Design with Brand**; portal owners are consulted per explainer |
| Approver | Content Design Lead (`CG-002` §5.4, class D) |
| Enforcement | `HC-016`'s own behaviour rules; `MM-001` §4.11 acceptance; **flash-rate and reduced-motion measured, not asserted** |
| Effectiveness measure | **Tour completion versus skip rate** (`HC-016` §What happens next, target > 60%) and, for A4, **the `P07` stage-4 drop-off** |
| Retirement | **`AN-34` — a low completion rate retires the asset.** Explicitly permitted, so it is not defended past its usefulness |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is registered at W6 and `HC-016` is at W2**, and `HC-016` `O-02` already records a sequencing problem of its own — *"`HC-005` `P03` help is W1 but this file is W2"*. **An onboarding animation four waves after the tour copy that surfaces it means the first users of `P04`, `P05` and `P08` see a tour with no asset.** `AUDIT-018` `EO-03` recorded thirty-nine instances of this shape and `AUDIT-014` R-02 / `AUDIT-015` R-04 / `AUDIT-018` R-03 asked that the basis be corrected **once, register-wide**. **Reported, deliberately not patched** | Programme Content Lead with Content Design | **W2 — reported, not patched** |
| **O-02** | **Whether any portal supports tours, animation playback, dismissal persistence and frequency capping is unconfirmed.** `HC-016` `O-01` states it plainly: *"`PT-14`, `PT-23` and `PT-24` are product capabilities, not content; if they are absent, most of this file is unimplementable."* **`AN-14` adds a Lottie-player requirement per portal to that list**, on four frameworks | CTO with the portal teams | **W6 — before commissioning** |
| **O-03** | **The `AN-05` overlap between explainer A4 and `HC-020` script 9 is unresolved.** Both address seller document submission — the highest-drop-off step against the 60% target — and **the register commissions both.** One must be withdrawn or the two must be scoped to different halves of the step | Content Design with Marketplace Operations | **W6 — before either is produced** |
| **O-04** | **No motion designer is engaged and no animation budget exists.** Seven explainers, light and dark variants, static fallbacks and per-portal player testing is discrete specialist work; the Master Index §7 Category 19 estimate is **specification only**, and `MM-006` `O-01` and `MM-007` `O-01` already record the same absence for video | Content Design Lead with Finance | **W6** |
| **O-05** | **No accessibility reviewer is named** for §4.5 — the **tenth** file to record it. **This is the file where it matters most**, because three Level A criteria can be breached by the asset's mere existence and none of them is visible in a static review | Content Design Lead | **W6 — before the first animation ships** |
| **O-06** | **`P09` `A7` is conditional on `HC-016` `O-01` confirming that the rider app supports a tour at all** (`AN-04`). `VB-003` §6 excludes brand from `P09` and `VB-007` §4 calls the rider ambiguity case absolute; **if the answer is no, A7 is not produced and the rider onboarding stays in `TR-020`** | Mobile Engineering with Content Design | **W6** |
| **O-07** | **The design system has no motion tokens.** `AN-19` requires shared easing and duration values; **`VB-006` specifies no motion contract at all**, and an animation set built to its own timing will not match the product's transitions | Design System Lead | **W6** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.7; §7 added per category convention
- [x] **One explainer per external portal, each tied to that portal's stated adoption target**
- [x] The `P09` case treated as an exception with the `VB-003` §6 exclusion honoured rather than overridden
- [x] Operational and internal portals explicitly excluded
- [x] **A decision test that distinguishes animation from video, static art, the tour itself, and nothing**
- [x] **Re-drawing the product's own UI prohibited, with the orphaning reason stated**
- [x] Animation prohibited from softening a confusing screen (`HC-016` `PT-11`)
- [x] Duration, weight and format bounded, with a mandatory static first frame that must carry the point alone
- [x] Motion design constrained to the functional, and **silence made absolute**
- [x] **The three Level A criteria motion can breach identified individually, each with a rule**
- [x] `prefers-reduced-motion` adopted as an obligation despite being AAA, with the device-class reason given
- [x] **Text separated into its own layer, turning twelve productions into six plus six re-renders**
- [x] The no-text-at-all option identified as preferred where achievable
- [x] First-run behaviour restated **by reference with `HC-016` identifiers**, not duplicated
- [x] **Retirement on low completion made an explicit permitted outcome**
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` W6 registration against a W2 need — reported, not patched, per `AUDIT-018` R-03**
- [ ] **`O-02` portal animation and tour capability unconfirmed — outstanding; much of this file may be unimplementable**
- [ ] **`O-03` the A4 / script 9 overlap is unresolved — outstanding**
- [ ] **`O-05` no accessibility reviewer — outstanding; this is the file where it matters most**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
