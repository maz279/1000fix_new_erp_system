---
id: MM-004
title: Icon Set Requirements
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Design System Lead
author: Design System with Brand, Content Design and Localisation
reviewers: [Content Design Lead, Brand Lead, Localisation Lead, Accessibility reviewer, Platform Engineering, portal owners, Programme Content Lead]
approver: Content Design Lead
content_class: D
purpose: >
  The production specification for the one icon set twelve portals and fourteen admin workspaces
  share — inventory, grid, construction, states, colour, contrast, Bengali label pairing, offline
  payload budget and delivery format. VB-007 fixes what each icon means and where an icon may
  stand alone; nothing fixes how the glyphs are drawn, exported or proven against contrast and
  touch-target thresholds. PS-06 commits the programme to one component library and one token set;
  an icon set drawn to no construction standard makes that commitment cosmetic, and a glyph drawn
  in the brand blue fails WCAG SC 1.4.11 on every light surface in the product.
traces_to: [VB-003, VB-006, VB-007, VB-008, VB-009, CG-004, CG-008, CG-010, CG-011, CG-012, UI-002, UI-003, UI-010, BN-003, BN-006, TS-016, MM-001, MM-003, MM-005, MM-010, MM-011, MM-012, DT-044, RP-007, 04-00 PS-04, 04-00 PS-05, 04-00 PS-06, 04-00 PS-08, 04-00 §P02, 04-00 §P03, 05-02 DM-06, 05-06 NFR-073]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md §3 four pairing modes, §4 seven icon-only prohibition categories, §5 the fifteen registered icon-only controls, §6 the object/action/status register, §7 Bengali width allowances and the drop-icon-before-label rule, §8 AC-01…AC-08 accessibility
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md §3 measured contrast — #39B1DF at 2.46:1 on white fails SC 1.4.3 and SC 1.4.11; #495057 at 8.18:1 and #1E5F8A at 6.86:1 pass; §6 brand excluded from P02 job flow, P09 and the P11 offline bundle
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md §3 PS-04 WCAG 2.1 AA, PS-05 responsive from 320px, PS-06 one component library and one token set, PS-08 offline-capable surfaces; §P02 mid-range Android 11 with 3 GB RAM and the under-12% battery budget per 8-hour shift
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.1.1 non-text content, SC 1.4.11 non-text contrast at 3:1, SC 2.5.5 target size, SC 1.4.5 images of text
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-06 — business records are archived, not deleted; the basis for VB-007 AI-01, the no-bin-icon rule
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Icon Set Requirements

| Item | Value |
|---|---|
| Governs | The single icon set used by all twelve portals, the fourteen `P03` workspaces, print and email |
| Meaning authority | [`VB-007`](../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md) — **this file draws; `VB-007` decides what it means** |
| Audience | Design System, icon designers, Platform Engineering, portal teams |
| Language | **English** — the specification. Accessible names and labels are bilingual (`VB-007` `AC-08`) |
| Wave | W1 · Months 1–4 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.9.
> §7 Open Items added per category convention.

---

## 1. Purpose

`VB-007` is complete on **meaning**: four pairing modes, seven categories where icon-only is
prohibited, a closed list of **fifteen** registered icon-only controls, and a register binding
object, action and status icons to labels and accessible names. Its own §11 names this file as the
missing half — *"`MM-004` Icon Set Requirements — the visual production specification"* — and
`VB-007` §10 step 3 instructs a designer adding an icon to *"design the glyph to `MM-004`."*

**There is currently nothing to design to.**

| Absent | Consequence |
|---|---|
| A construction grid and stroke standard | Glyphs of visibly different weight and size sitting in the same toolbar, drawn months apart by different hands |
| A stated colour and contrast position | **A brand-blue icon on white measures 2.46:1 and fails SC 1.4.11**, on a programme where `PS-04` makes WCAG 2.1 AA contractual |
| A state specification | Disabled icons indistinguishable from enabled ones; focus rings absent on the exact controls `VB-007` §5 permits to stand alone |
| A Bengali sizing rule in production terms | `VB-007` `BL-01` sizes containers for the Bengali rendered width, and a designer has no measured figure to size against |
| An offline payload budget | The `P11` offline bundle, from which `VB-003` §6 excludes brand assets, silently carrying a full icon library |
| A delivery format | Twelve portals on four frameworks each converting SVG their own way, and the `PS-06` single-library commitment reduced to a shared drawing |

**Consequence of absence (`CP-03`).** `PS-06` commits the programme to one component library and
one token set. An icon set with no construction standard makes that commitment cosmetic: the same
action carries the same *meaning* and a visibly different *mark* in three workspaces, and the
accessibility obligation `VB-007` `AC-04` states is discovered at a portal audit rather than at
design time.

**What this file is not.** It is not the meaning register (`VB-007`), not the component copy
contract (`VB-006`), not illustration (`MM-005`), not chart symbols (`RP-007`), and not the
barcode and QR contract (`DT-044`).

---

## 2. Scope

**In scope.** The icon inventory derived from `VB-007` §5 and §6; the construction grid, keyline
system and stroke standard; optical alignment; the state set; colour tokens and measured contrast;
size ramp and touch targets; Bengali label pairing in production terms; the offline and payload
budget; export formats and framework delivery; the prohibitions carried from `VB-007`; the
deliverable specification; and rules `IC-01`…`IC-28`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| What an icon means; which control may be icon-only; the accessible name | [`VB-007`](../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md) |
| Status colour and label semantics | [`VB-008`](../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md) — this file draws the **glyph**, `VB-008` sets the colour and word |
| The component the icon sits in, and its copy contract | [`VB-006`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) |
| Brand marks and logos | [`VB-003`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) §8, and the **unowned identity standard** (`MM-001` `O-01`) |
| Illustration and empty-state artwork | [`MM-005`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) |
| Chart symbols, series markers and legends | [`RP-007`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) |
| Diagram markers and shapes | [`MM-003`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) §4.3 |
| Barcode and QR symbology | [`DT-044`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) |
| The accessible-name strings at scale | [`UI-010`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md) |
| File format, metadata, delivery and acceptance | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) §4.2 class A2 |
| Naming, versioning and the register | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Icon designer (internal or vendor)** | The construction standard every glyph is drawn to and accepted against | Before drawing |
| **Design System Lead** | The library contract and the addition procedure | Continuously |
| **Platform Engineering** | Export formats, framework packaging, sprite and payload strategy | At integration |
| **Portal team on any of four frameworks** | What they consume and what they may not re-draw | Per portal |
| **Accessibility reviewer** | §4.5 contrast and §4.4 states — where icon sets fail AA | At gate |
| **Localisation Lead** | §4.6 Bengali pairing and the container-sizing consequence | At layout review |
| **Content Design** | Confirmation that no icon carries meaning a label does not | At review |

---

## 4. Content

### 4.1 The inventory

Derived by enumeration from `VB-007` §5 and §6. **This file draws exactly this set and no more**
(`IC-01`).

| Group | Source | Count | Notes |
|---|---|---:|---|
| **Object icons** — what a thing is | `VB-007` §6.1 | **16** | Service order, job, work order, estimate, invoice, payment, device, part, customer, technician, branch, contract, warranty, claim, consignment, complaint |
| **Action icons** — what happens | `VB-007` §6.2 | **16** | Create, edit, approve, reject, cancel, archive, assign, dispatch, escalate, print, download, upload, attach, sync, sign, scan |
| **Status glyphs** | `VB-007` §6.3 | **7** | Info, success, warning, error, blocked, pending, offline |
| **Registered icon-only controls** | `VB-007` §5 | **15** | Close, search, more actions, sort, expand/collapse, previous/next, help, copy, refresh, filter, fullscreen, scan, torch, call, navigate |
| **Overlap** | `scan` appears in both §5 and §6.2 | **−1** | Drawn once, used in both modes |
| **Set total** | | **53 glyphs** | Plus the state and size variants in §4.4 and §4.7 |

| # | Rule |
|---|---|
| **IC-01** | **The set is closed at 53 glyphs and grows only through `VB-007` §10.** A glyph drawn without a `VB-007` register entry has no meaning, no accessible name and no Bengali label, and it will be used inconsistently within a wave |
| **IC-02** | **One glyph, one meaning, across twelve portals** (`VB-007` §6). A portal may not draw a local variant of a registered glyph |
| **IC-03** | Where `VB-007` gives a glyph two modes — `scan` is Mode B on `P02`/`P09`/`P11` and Mode A elsewhere — **the artwork is identical in both.** `VB-007` `PM-05` requires the icon and the accessible name to be the same in both modes |
| **IC-04** | **`VB-007` §6.3 fixes the glyph and `VB-008` fixes the colour and the word.** This file draws seven status shapes that must be distinguishable **without colour** — `SI-02` requires the warning triangle and the error circle to differ by shape so the distinction survives greyscale, monochrome print and colour-blind vision |

### 4.2 Construction

| Property | Specification |
|---|---|
| **Design grid** | **24 × 24 px**, 1 px subdivision |
| **Live area** | 20 × 20 px — a **2 px padding on all sides** so glyphs of different silhouette optically align |
| **Keyline shapes** | Square 18 × 18 · circle ⌀ 20 · portrait rectangle 16 × 20 · landscape rectangle 20 × 16. **Every glyph is built on one of these**, which is what makes a square and a circle look the same size |
| **Stroke weight** | **2 px** at 24 px. **1.5 px** at 20 px and below is prohibited — see `IC-07` |
| **Stroke terminals** | Butt cap, mitre join, **90° and 45° angles only** |
| **Corner radius** | 2 px outer, 1 px inner |
| **Counters and gaps** | **Minimum 2 px** — the constraint that decides whether a glyph survives at 16 px and on a 203 dpi thermal print |
| **Fill** | **Outline style, single weight.** Filled variants exist only for the seven status glyphs and only where `VB-008` requires a filled badge |
| **Alignment** | Optical, not geometric. **Verified by eye at 16 px, not by coordinate** |

| # | Rule |
|---|---|
| **IC-05** | **Every glyph is drawn once, at 24 px, on the grid.** Smaller and larger sizes are the *same* artwork with adjusted stroke, never a redrawn glyph — except at 16 px, where `IC-06` applies |
| **IC-06** | **A 16 px optical variant is drawn for any glyph whose 24 px form loses a counter at 16 px.** Simply scaling a 24 px glyph to 16 px is how an icon set becomes mush in a dense table, and `VB-003` `D-03` puts twelve rows on a 1366 × 600 screen |
| **IC-07** | **Stroke weight is never below 2 px at the rendered size.** A 1 px stroke on a low-density branch panel disappears, and on a 203 dpi thermal print it does not resolve at all (`VB-004` `TH-04`) |
| **IC-08** | **Glyphs are geometric and literal, never illustrative.** An icon is a mnemonic, not a picture (`VB-007` §1). No perspective, no shading, no gradients, no more than two visual elements per glyph |
| **IC-09** | **No text or numeral inside a glyph**, with two registered exceptions — the `i` in the info circle and the `?` in the help circle, both from `VB-007` §5/§6.3. Text in a glyph cannot be translated (SC 1.4.5) |
| **IC-10** | Paths are **outlined and merged** on export; no open strokes, no clipping masks, no live effects. An unmerged stroke re-renders differently in each of the four frameworks |
| **IC-11** | **The glyph is tested at 16, 20, 24, 32 and 48 px, on a low-density panel, before it enters the library.** Not at 200% in a design tool |

### 4.3 The size ramp and touch targets

| Size | Use | Minimum interactive target |
|---:|---|---|
| **16 px** | Dense table cells, inline with 13 px `body-dense` text (`VB-003` §7) | **Non-interactive only** |
| **20 px** | Inline with 14 px body; secondary controls | 44 × 44 px target area |
| **24 px** | **Default.** Toolbars, buttons, list rows | 44 × 44 px |
| **32 px** | `P02` / `P09` primary actions; empty-state accents | **48 × 48 px** |
| **48 px** | `P02` / `P09` scan, torch, call, navigate — the four gloved-hand controls | **56 × 56 px** |

| # | Rule |
|---|---|
| **IC-12** | **Every interactive icon has a target of at least 44 × 44 px** (`VB-007` `IO-03`, `AC-06`; WCAG SC 2.5.5). The target is the hit area, not the glyph — a 16 px glyph in a 44 px target is correct; a 44 px glyph is not required |
| **IC-13** | **`P02` and `P09` raise the floor to 48 × 48 px** and the four registered field controls to 56 × 56 px. The hand is gloved, the phone is wet, the user is standing, and `VB-007` `IO-04` makes these the only icon-only controls those surfaces have |
| **IC-14** | Adjacent targets have **at least 8 px of separation.** Two 44 px targets touching is one 88 px target with a coin-flip outcome |

### 4.4 States

| State | Treatment | Rule |
|---|---|---|
| **Default** | Token `icon-default` — `#495057` (8.18:1 on white) | |
| **Hover** | Token `icon-strong` — `#212529` (15.43:1). **Background change only where the component defines one** | Never a colour change that carries meaning |
| **Active / pressed** | `#212529` with the component's pressed background | |
| **Selected** | **Paired with a text or shape indicator**, never colour alone (`CG-011` `CL-01`) | |
| **Disabled** | `#ADB5BD` **plus** an explanation in text — `VB-006` `BT-05` prohibits a disabled control with no stated reason | The icon alone never explains |
| **Focus** | **2 px focus ring, `#1E5F8A`, 2 px offset, ≥ 3:1 against both the icon background and the page background** | Never removed, on any surface |
| **Loading** | The component's progress indicator, **not a spinning icon** (`VB-006` `PR-01`) | |
| **Error / warning on a control** | The `VB-008` semantic colour **as a fill or border**, with the word present | Colour never alone |

| # | Rule |
|---|---|
| **IC-15** | **Every state is a token, not a hand-picked value.** `PS-06` commits to one token set; an icon state chosen per portal is a divergence the design system was supposed to prevent |
| **IC-16** | **The focus ring is part of the icon specification, not the component's afterthought.** `VB-007` §5 permits fifteen icon-only controls; each of them is keyboard-reachable and a missing focus ring on any of them is an AA failure |
| **IC-17** | **No state is signalled by colour alone** (`CG-011` `CL-01`, WCAG SC 1.4.1) |

### 4.5 Colour and contrast

| Token | Value | On `#FFFFFF` | On `#F8F9FA` | Permitted for |
|---|---|---:|---:|---|
| `icon-default` | `#495057` | **8.18:1** | ~7.8:1 | All icons, default state |
| `icon-strong` | `#212529` | **15.43:1** | ~14.7:1 | Hover, active, high-emphasis |
| `icon-accent` | `#1E5F8A` | **6.86:1** | ~6.5:1 | Focus ring, link-adjacent icons |
| `icon-disabled` | `#ADB5BD` | ~1.9:1 | — | **Disabled only**, always with text (`VB-006` `BT-05`) |
| `icon-error` | `#DC3545` | 4.53:1 | ~4.3:1 | Fill, border or glyph **with the word present** |
| `icon-warning` | `#FFC107` | **1.63:1** | — | **Fill only.** Never a glyph on light |
| **Brand blue** | `#39B1DF` | **2.46:1** | — | **Never an icon on a light background** |
| Reversed | `#FFFFFF` | on `#212529` 15.43:1 | — | Icons on dark UI |

| # | Rule |
|---|---|
| **IC-18** | **`#39B1DF` is not an icon colour on any light surface.** `VB-003` `BC-01` measured it at **2.46:1**, below both the SC 1.4.3 text threshold and the **SC 1.4.11 3:1 non-text threshold**. `VB-007` `AC-04` already states the consequence: *"a brand-blue icon on a white background fails SC 1.4.11"*. **This file does not provide a brand-blue icon variant**, so the failure cannot be introduced by choosing one |
| **IC-19** | **Every icon meets 3:1 non-text contrast against every background the design system places it on** — including selected-row and hover backgrounds, which are the pairs most often left unmeasured |
| **IC-20** | Icons ship with **`fill="currentColor"`**, so colour is inherited from the token and cannot be hard-coded into the artwork (`MM-001` §4.2 class A2) |
| **IC-21** | **Dark-mode icon variants are the same artwork with an inherited colour**, not a separate set. `IC-20` is what makes that true |

### 4.6 Bengali label pairing — production terms

`VB-007` §7 is the layout rule. This section is what a designer must build to.

| # | Rule |
|---|---|
| **IC-22** | **The icon-plus-label container is sized on the Bengali rendered width plus 10% headroom** (`VB-007` `BL-01`), and **rendered width is measured, not counted in characters**. Bengali conjuncts and matras occupy more width per character than Latin at the same size, and Bengali sets one step larger or at its `VB-009` §3 floor |
| **IC-23** | The working assumption is **+40% rendered width over English** (`VB-007` `BL-02`), **replaced by a measurement before ship.** A designer who lays out to +40% and never measures has produced a defect that only appears in Bengali |
| **IC-24** | Icon and label are **vertically centred on the Bengali line box**, which is taller — line height 1.7 against 1.6 (`VB-007` `BL-08`, `VB-009` §4). Centring on the Latin line box leaves the icon visibly high in Bengali |
| **IC-25** | **When space runs out, the icon is dropped before the label** (`VB-007` §7.3). The set therefore ships **label-only layouts as a supported state**, and no glyph is drawn on the assumption it will always be visible |
| **IC-26** | **A Bengali label is never shortened to fit beside an icon** (`VB-007` `BL-03`). The container widens or the layout goes two-line — icon above label — and **the two-line form is a specified variant of every Mode A pairing**, not an improvisation |
| **IC-27** | Toolbar and action-bar layouts are **visually regression-tested at Bengali width** before release (`VB-007` `BL-07`). This is where breakage concentrates |

### 4.7 Payload, offline and print

| # | Rule |
|---|---|
| **IC-28** | **Icons are delivered as an SVG sprite or as tree-shakeable components, never as an icon font.** An icon font renders as a missing glyph or a wrong character when the font fails, is announced as a letter by some screen readers, and cannot carry `currentColor` per-path |
| **IC-29** | **Each glyph is ≤ 3 KB optimised** (`MM-001` §4.2 class A2). At 53 glyphs the whole set is under 160 KB uncompressed and well under that gzipped |
| **IC-30** | **A surface ships only the glyphs it uses.** `P02` runs on a mid-range Android with 3 GB RAM and a **battery budget under 12% per 8-hour shift** (`04-00` §P02); `P11` operates offline and `VB-003` §6 states that **brand assets are not downloaded into the `P11` offline bundle — payload is the constraint** |
| **IC-31** | The **offline bundle carries the icon set it needs and nothing else**, and the bundle size is a declared, measured figure per release — not an emergent one |
| **IC-32** | **Print and email consume PNG at @1×, @2× and @3×**, generated from the same SVG source (`MM-001` §4.2, `MM-011` §4.3). Email clients do not render SVG reliably and `VB-004` `F-03` makes thermal output monochrome |
| **IC-33** | **A glyph that does not resolve as 1-bit monochrome at 203 dpi is not used on thermal output.** `VB-004` `TH-04` already permits omitting the logo on that basis; the same test applies to any glyph |

### 4.8 Prohibitions

Carried from `VB-007` and restated **because a designer reads this file, not that one** — each
with its owning identifier so the two cannot drift.

| Prohibited | Why | Owner |
|---|---|---|
| **A bin or trash icon, anywhere in the system** | `05-02` `DM-06` archives business records and does not delete them. **A bin icon promises something the system does not do** | `VB-007` `AI-01` |
| **An emoji as any icon** | Renders differently per platform, cannot be recoloured, is announced unpredictably | `VB-007` `SI-03` |
| **An hourglass for "pending"** | Reads as "loading". Pending uses a clock | `VB-007` §6.3 |
| **A light bulb for info, a thumbs-up for success, a skull or sad face for error** | `VB-007` §6.3's "never" column | `VB-007` §6.3 |
| **✕ for "cancel order"** | ✕ is Close. Cancel has its own glyph and its own word — the most common icon defect in ERP UI | `VB-007` `AI-02` |
| **One glyph for both Sync and Refresh** | Sync reconciles offline state; refresh re-reads the server | `VB-007` `AI-03` |
| **An icon-only Approve, Reject, Sign, Cancel or Archive** | Approval, financial, legal and destructive actions are Mode A only | `VB-007` §4 |
| **Any icon-only control on `P01`, `P07`, `P09` or `P12`** | First-time and low-literacy audiences. **`P09` is absolute** | `VB-007` §4 |
| **A brand-blue glyph on a light background** | 2.46:1, fails SC 1.4.11 | `VB-003` `BC-01` |
| **A glyph with baked-in text** | Cannot be translated (SC 1.4.5) | `IC-09` |

### 4.9 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master format** | **SVG 1.1**, 24 × 24 viewBox, paths merged and outlined, `fill="currentColor"`, no `<style>`, no editor metadata |
| **Derived formats** | SVG sprite; framework components (Odoo OWL, React, React Native, Flutter); **PNG @1×/2×/3×** for email and print; 1-bit monochrome PNG for thermal |
| **Dimensions** | 24 px design grid, 20 px live area; 16 px optical variants where `IC-06` applies; ramp 16/20/24/32/48 |
| **Colour** | **Inherited** — no fill in the artwork. Tokens per §4.5, every pair measured |
| **Compression** | **≤ 3 KB per glyph optimised**; set ≤ 160 KB uncompressed; per-surface bundle declared and measured |
| **States** | Default, hover, active, selected, disabled, focus — as tokens, not as separate artwork (§4.4) |
| **Accessibility** | Accessible name from `VB-007` §5/§6, **bilingual**; 3:1 non-text contrast verified on every background; 44 px target (48/56 on `P02`/`P09`) |
| **Metadata** | XMP `dc:title` = `VB-007` register name · `dc:description` = accessible name · `dc:relation` = `VB-007` · `dc:rights` |
| **Naming** | `MM-012` §4.3; the stem is the `VB-007` register name, not a designer's file name |
| **Source** | Editable design-tool source with the keyline layer intact (`MM-001` `DL-02`) |
| **Evidence** | A **contrast report** and a **size-ramp proof sheet** at 16/20/24/32/48 px on light and dark, delivered with the set |

### 4.10 Adding, changing and retiring a glyph

| Step | Action | Who |
|---|---|---|
| 1 | Confirm no registered glyph already carries the meaning | Design System |
| 2 | Confirm the label exists in `CG-004` and `BN-003` | Content Design + Localisation |
| 3 | Register the meaning, mode and accessible name in **`VB-007` §6** | Design System |
| 4 | **Draw the glyph to this file** — grid, keyline, stroke, counters | Icon designer |
| 5 | Prove 3:1 non-text contrast on every background, in all themes | Accessibility |
| 6 | Measure the Bengali label width and confirm the layout holds | Localisation |
| 7 | Prove the size ramp, including 16 px and thermal monochrome | Design System |
| 8 | Register the asset in `MM-012` and release with the library version | Design System + Platform |
| 9 | Log the decision in [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) | Content Lead |

| # | Rule |
|---|---|
| **IC-34** | **Steps 3 and 4 are in that order.** A glyph drawn before its meaning is registered is a glyph looking for a use, and `VB-007` `IO-01` says the icon-only list *"only shrinks or grows by decision, never by drift"* |
| **IC-35** | **A glyph is never silently redrawn.** Changing artwork for a meaning users have learned is a **MAJOR** library change (`CG-006` §6.2) with a release note (`OP-006`) and a screenshot re-capture sweep (`MM-002` `SC-44`) |
| **IC-36** | **A retired glyph is not reused for a different meaning** — the `CP-02` principle applied to artwork, and for the same reason: users remember the mark |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`VB-007_Iconography_and_Label_Pairing_Register.md`](../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md) | The meaning register; §5 and §6 supply §4.1's inventory; §7 supplies §4.6; §10 step 3 names this file |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | §3 measured contrast behind `IC-18`; §6 the `P11` offline payload constraint; §7 the type sizes icons sit beside |
| [`VB-006_Design_System_Content_Standards.md`](../01_Voice_Brand_and_Design_Content/VB-006_Design_System_Content_Standards.md) | `BT-05` disabled-with-explanation, `BT-07` no bare icon on a destructive action, `PR-01` loading |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md) | Colour and word for the seven status glyphs this file draws |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | Bengali floors and line height behind `IC-22`…`IC-24` |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) · [`BN-003_Bilingual_Terminology_Glossary.md`](../11_Localisation_Bengali/BN-003_Bilingual_Terminology_Glossary.md) | The labels glyphs pair with; §4.10 step 2 |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | `CL-01`, `AT-01`; the obligations §4.4 and §4.5 discharge |
| [`UI-002_Global_Navigation_and_Label_Register.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-002_Global_Navigation_and_Label_Register.md) · [`UI-003_Field_Label_Placeholder_and_Help_Text_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-003_Field_Label_Placeholder_and_Help_Text_Library.md) · [`UI-010_Accessibility_Text_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-010_Accessibility_Text_Library.md) | The labels and accessible names delivered alongside the glyphs |
| [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | Where §4.4 focus, §4.5 contrast and §4.3 target size are tested |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | Class A2 format, metadata, acceptance |
| [`MM-003_Diagram_and_Process_Map_Visual_Standard.md`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) | Diagram markers, which are **not** drawn from this set |
| [`MM-005_Illustration_and_Empty_State_Artwork_Brief.md`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) | The boundary — an illustration is not a large icon |
| [`MM-010_PDF_and_Print_Template_Design_Specification.md`](MM-010_PDF_and_Print_Template_Design_Specification.md) · [`MM-011_Email_and_HTML_Asset_Specification.md`](MM-011_Email_and_HTML_Asset_Specification.md) | The PNG consumers in `IC-32` |
| [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Naming, versioning, the library release record |
| [`DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Machine-readable symbols — explicitly not icons |
| [`RP-007_Chart_Label_and_Visualisation_Standard.md`](../14_Reporting_Analytics_and_KPI/RP-007_Chart_Label_and_Visualisation_Standard.md) | Chart symbols, which this set does not supply |
| [`OP-006_Release_Notes_Standard_and_Wave_Note_Set.md`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) · [`OP-011_Runbook_Portal_and_Mobile_App_Operations.md`](../17_Operations_Support_and_Runbooks/OP-011_Runbook_Portal_and_Mobile_App_Operations.md) | Library releases and the mobile bundle `IC-31` bounds |
| `04-00` `PS-04`…`PS-08`, §P02, §P03 | Accessibility, responsiveness, one library, offline, the device and screen baselines |
| `05-02` `DM-06` | The archive-not-delete rule behind the no-bin-icon prohibition |

| Depended on by |
|---|
| `VB-007` §10 step 3 · the shared component library on four frameworks · all twelve portals and fourteen `P03` workspaces · `MM-010` print artwork · `MM-011` email assets · `MM-005` (visual consistency) |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per design-system release**, matching `VB-007` §13 so the pair does not drift |
| Trigger for out-of-cycle review | A `VB-007` register change · a new portal or surface · a Bengali truncation defect · an accessibility finding · a device or panel class entering the estate · a payload budget breach |
| Owner | **Design System Lead** |
| Approver | Content Design Lead (`CG-002` §5.4, class D) |
| Enforcement | Automated: icon-only control not in `VB-007` §5; icon without an accessible name; icon contrast below 3:1; bin or trash glyph present; emoji used as an icon; touch target below 44 px; per-surface bundle over budget. Manual: optical alignment and the size-ramp proof sheet |
| Effectiveness measure | **Glyphs failing the §4.9 contrast report at first delivery**, and **Bengali truncation defects per release — target zero** |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`VB-007` §6.1's Bengali labels are indicative pending `BN-003`**, which `VB-007` §13 records as an open dependency. `IC-22`…`IC-26` size containers on the Bengali rendered width; **until `BN-003` binds the labels, every container width in the library is provisional** and `IC-23`'s +40% assumption cannot be replaced by a measurement | Localisation Lead | **W1 — before the component library ships** |
| **O-02** | **The Brand ruling on `#39B1DF` is open** (`VB-003` §3.2, content risk `CR-13`). `IC-18` assumes option 1 — brand blue stays a fill and `#1E5F8A` carries text and accent — which is `VB-003`'s stated assumption. **If Brand rules otherwise, §4.5's token table changes and every glyph's contrast evidence is re-run** | Brand Lead with Steering | **W1 — it blocks design-system token approval** |
| **O-03** | **No accessibility reviewer is named** to operate §4.5's contrast gate or §4.4's focus verification — the **seventh** file to record this, after `TR-003` `O-02`, `HC-002` `O-04`, `HC-016` `O-04`, `MM-001` `O-06`, `MM-002` `O-04` and `MM-003` `O-04` | Content Design Lead | **W1** |
| **O-04** | **No icon designer is engaged and no design-tool or library-tooling decision is made.** 53 glyphs with 16 px optical variants, a five-step size ramp, six states and a proof sheet is a discrete piece of specialist work that appears in no plan; the Master Index §7 Category 19 estimate is **specification only** | Design System Lead with Finance | **W1 — the library gates twelve portals** |
| **O-05** | **The per-surface icon bundle budget in `IC-30`/`IC-31` has no number.** `04-00` §P02 sets a battery budget and `VB-003` §6 excludes brand assets from the `P11` offline bundle, but **no payload ceiling exists for any mobile surface**. "Ships only what it uses" is unenforceable without a measured target, which is the same defect `HC-002` `O-06` records for the 3G page-weight budget | CTO with Design System | **W2** |
| **O-06** | **Thermal monochrome qualification (`IC-33`) has no test set.** `VB-004` §14 assigns a printer test set to Platform Engineering and records it as outstanding; `MM-001` `O-07` records the same gap. **No glyph can be cleared for thermal output until it exists** | Platform Engineering | **W1 — before the first `DT` release** |
| **O-07** | **`VB-007` §5's fifteen icon-only controls were registered before any of them was drawn.** Four — scan, torch, call, navigate — are `P02`/`P09` controls at 48 px with a 56 px target; **whether all fifteen survive `IC-06`'s 16 px legibility test is unproven**, and a control that fails it must move to Mode A, which is a `VB-007` change, not an `MM-004` one | Design System with Content Design | **W1 — before `P02` build** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.9; §7 added per category convention
- [x] **Inventory enumerated from `VB-007` §5 and §6 with the overlap deducted — 53 glyphs, counted not estimated**
- [x] Construction specified in grid, keyline, stroke, terminal, counter and optical terms a designer can build to
- [x] **16 px optical variants required rather than assumed to scale, with the dense-table case as the reason**
- [x] Size ramp bound to touch targets, with `P02`/`P09` raised for gloved field use
- [x] Six states specified as tokens, with focus treated as part of the icon spec because fifteen controls stand alone
- [x] **Every colour token carries its measured ratio; no brand-blue variant is provided, so the SC 1.4.11 failure cannot be chosen**
- [x] Bengali pairing expressed in production terms — measured rendered width, taller line box, two-line variant, drop-icon-before-label
- [x] **Icon font prohibited, with the failure modes stated; sprite or tree-shakeable components required**
- [x] Payload treated as an offline and battery constraint, tied to `VB-003` §6 and `04-00` §P02
- [x] Prohibitions carried from `VB-007` **with their owning identifiers**, so the two files cannot drift
- [x] Addition procedure ordered so meaning is registered before artwork exists (`IC-34`)
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` `BN-003` unwritten — outstanding; every Bengali container width is provisional**
- [ ] **`O-02` Brand ruling on `#39B1DF` open — outstanding; §4.5 tokens are assumed**
- [ ] **`O-04` no icon designer engaged and no library tooling chosen — outstanding**
- [ ] **`O-07` the fifteen icon-only controls are unproven at 16 px — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
