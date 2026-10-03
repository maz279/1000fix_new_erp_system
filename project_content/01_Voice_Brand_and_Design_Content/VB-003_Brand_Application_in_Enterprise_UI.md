---
id: VB-003
title: Brand Application in Enterprise UI
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead
author: Brand with Content Design
reviewers: [Design System, Content Design Lead, Accessibility reviewer, portal owners]
approver: Content Design Lead
content_class: E
purpose: >
  States how the 1000FiX brand expresses inside dense operational software, and where brand
  yields to legibility. Branch hardware is 1366x768; marketing brand density is unusable at that
  size. It also records a measured accessibility finding: the primary brand blue fails WCAG AA
  text contrast on white, which must be designed around rather than discovered in a portal audit.
traces_to: [04-00 §P03, 04-00 PS-04, 04-00 PS-05, 04-00 PS-06, 05-06 NFR-073, CG-011, VB-008, VB-009]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000_fix_corporate_website project_content CB-001 Brand Guidelines Document v1.0 §3 colour palette and §4 typography
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P03 design requirements — 1366x768 branch hardware, one-click workspaces, four-click record reach
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 PS-04 (WCAG 2.1 AA), PS-05 (responsive from 320px), PS-06 (one component library, one token set)
    verified: 2026-08-15
    class: P1
  - source: W3C WCAG 2.1 SC 1.4.3 (contrast minimum) and SC 1.4.11 (non-text contrast); ratios computed from CB-001 hex values 2026-08-15
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-003 — Brand Application in Enterprise UI

> **The brand was designed to attract. The ERP exists to be operated.** `CB-001` sets a 60/30/10
> colour ratio, a 48px H1 and generous whitespace — all correct for a marketing page viewed once.
> A dispatcher looks at the dispatch console for seven hours a day on a 1366×768 laptop.
>
> This file states where the brand applies unchanged, where it is reduced, and where it is
> excluded — and records a measured contrast finding that constrains all three.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | How brand identity is applied across twelve portals and fourteen admin workspaces |
| **What it does not govern** | The design system implementation (Design System team); the colour tokens themselves (`VB-008` for status semantics); Bengali type (`VB-009`) |
| **What breaks without it** | Either a marketing-styled ERP nobody can work in for eight hours, or twelve unbranded portals that look like different products |

---

## 2. Scope

**In scope:** logo, colour, type scale, density, imagery and brand furniture in `P01`–`P12` and
the fourteen `P03` workspaces; and in the digital artefacts those surfaces produce.

**Out of scope:** print and PDF (`VB-004`), email (`VB-005`), component copy (`VB-006`),
marketing and the corporate website (`CB-001` continues to govern those unchanged).

---

## 3. The measured finding — brand colour and WCAG AA

**This section is a finding, not a preference.** Contrast ratios were computed from the `CB-001`
hex values on 2026-08-15 using the WCAG 2.1 relative-luminance formula.

| Colour | Hex | On white | On `#212529` | Text on white? | Non-text on white (3:1)? |
|---|---|---:|---:|---|---|
| **1000FiX Blue** | `#39B1DF` | **2.46** | 6.26 | ❌ **Fails all text** | ❌ **Fails** |
| Dark Blue | `#1E5F8A` | **6.86** | 2.25 | ✅ AA normal | ✅ |
| **1000FiX Orange** | `#F26100` | **3.24** | 4.76 | ⚠️ Large text only | ✅ |
| Warm Orange | `#FF8C42` | 2.31 | 6.67 | ❌ Fails all text | ❌ Fails |
| Success Green | `#28A745` | 3.13 | 4.92 | ⚠️ Large text only | ✅ |
| Error Red | `#DC3545` | 4.53 | 3.41 | ✅ AA normal (marginal) | ✅ |
| **Warning Yellow** | `#FFC107` | **1.63** | 9.46 | ❌ **Fails badly** | ❌ Fails |
| Info Blue | `#17A2B8` | 3.04 | 5.07 | ⚠️ Large text only (marginal) | ✅ (marginal) |
| Dark Gray | `#495057` | 8.18 | 1.89 | ✅ AA normal | ✅ |
| Medium Gray | `#6C757D` | 4.69 | 3.29 | ✅ AA normal | ✅ |
| Light Gray | `#E9ECEF` | 1.19 | 13.01 | ❌ | ❌ — borders on white only decoratively |
| Near-black | `#212529` | 15.43 | — | ✅ | ✅ |

### 3.1 What this means

| # | Consequence |
|---|---|
| **BC-01** | **The primary brand blue cannot carry text on a white background.** Not as body text, not as a link, not as large text. At 2.46:1 it fails even the 3:1 non-text threshold of SC 1.4.11, so it cannot be the only carrier of a border, focus ring or status dot on white either |
| **BC-02** | **`#1E5F8A` Dark Blue is the ERP's text and link blue.** At 6.86:1 it passes AA comfortably and reads as the same brand family |
| **BC-03** | **`#39B1DF` remains the brand colour** — used as a fill, a header band, a chart series, an illustration colour, a selected-row background — with text on it in `#212529`, not white. White on `#39B1DF` is also 2.46:1 and also fails |
| **BC-04** | **Warning Yellow `#FFC107` is a fill only.** Text on yellow is `#212529` (9.46:1). Yellow text on white at 1.63:1 is unusable anywhere |
| **BC-05** | Orange, Green and Info Blue are **large-text-or-fill** colours. Body text in any of them fails |
| **BC-06** | `#DC3545` at 4.53:1 passes AA but with almost no margin. On any background that is not pure white it will fail. **Error text is `#212529` with red used as the fill, icon or border** |

### 3.2 Status of this finding

`PS-04` and `NFR-073` make WCAG 2.1 AA contractual on all web portals. `05-06` §11 requires an
automated scan plus a manual audit before each portal release. **These ratios will fail that
scan if the marketing palette is applied to text unchanged.**

> **This is escalated, not decided here.** Changing a brand colour is a Brand and Steering
> decision, not a content one (`CG-013` T-A19). The escalation asks Brand to confirm one of:
>
> 1. Adopt `#1E5F8A` as the ERP text/link blue and keep `#39B1DF` as a fill-only brand colour
>    (**recommended** — no brand change, no marketing impact); or
> 2. Darken `#39B1DF` for digital text use, creating a divergence from `CB-001`; or
> 3. Accept documented AA failures, which contradicts `PS-04`.
>
> Recorded in `RF-006` and as content risk `CR-13` in `RF-011`. **Option 1 is assumed in this
> document until Brand rules otherwise.**

---

## 4. Where brand applies unchanged

| Surface | Treatment | Why |
|---|---|---|
| `P01` Customer portal and app | Full brand — colour, imagery, generous type | The customer chose to be here. Brand builds the trust the transaction needs |
| `P07` Marketplace seller | Full brand | External audience being recruited and retained |
| `P12` Partner and referral | Full brand | External, chosen, advocacy audience |
| Sign-in and sign-out screens, all portals | Full brand | The one moment on every surface with no operational task competing |
| Error pages, maintenance and status pages | Full brand | Brand reassurance is the only content available |
| First-run tours and onboarding | Full brand | Introductory, not operational |
| Public tracking link (no login) | Full brand | Often the first 1000FiX interface a person ever sees |

---

## 5. Where brand is reduced

Operational surfaces. The brand is present, recognisable, and out of the way.

| Element | Marketing (`CB-001`) | Operational ERP | Reason |
|---|---|---|---|
| Colour ratio | 60% blue / 30% neutral / 10% orange | **10% brand / 85% neutral / 5% accent** | Blue behind a data table destroys row scanning |
| H1 | 48px desktop | **20px** | A workspace has no hero. The largest text is a page title |
| Body | 16px | **14px** (13px minimum in dense tables) | 1366×768 with a 14-column table |
| Line height | 1.6 | **1.4** for tabular data; 1.6 retained for prose | Row density |
| Whitespace | Generous | **Compressed** — 8px base grid | Any record reachable in ≤ 4 clicks (`04-00` §P03) |
| Logo | Prominent | **28px height, top-left, once** | It is a wayfinding mark, not a banner |
| Imagery | Photography throughout | **None** in operational views | Photography in a dispatch console is noise |
| Illustration | Brand illustration | **Empty states only** | The only place a picture helps |
| Corner radius, shadows | Expressive | **Minimal** — 4px radius, shadow only on overlays | Depth cues cost rendering and attention |

### 5.1 The 1366×768 constraint

`04-00` §P03 names 1366×768 as the most common branch hardware. After browser chrome and OS
furniture, roughly **1366×600** is usable.

| Rule | Detail |
|---|---|
| **D-01** | The primary work area is designed to 1366×600. Anything requiring more is a defect, not a "best on large screens" feature |
| **D-02** | Global chrome — header, workspace switcher, breadcrumb — consumes no more than **96px** of vertical space total |
| **D-03** | A list view shows at least **12 rows** without scrolling at 1366×600 |
| **D-04** | No decorative element occupies primary work area space |
| **D-05** | Brand furniture never occupies a fixed side rail wider than 64px in a collapsed state |
| **D-06** | `PS-05` responsive from 320px still applies. 1366×600 is the design target, not the minimum |

---

## 6. Where brand is excluded

| Surface | Rule |
|---|---|
| `P02` Technician app job execution | No brand colour in the job flow beyond a 24px header mark. Sunlight legibility and battery (`P02` non-negotiable #5, under 12% per 8-hour shift) govern |
| `P09` Rider app | As `P02`. Largest possible type, highest possible contrast, minimum chrome |
| `P11` Auditor app, offline mode | Brand assets are not downloaded into the offline bundle. Payload is the constraint |
| Dense data tables anywhere | No brand colour in cells. Status uses the `VB-008` semantic palette, which is not the brand palette |
| Printed thermal output | Monochrome. Logo only if it renders legibly at the printer's resolution (`VB-004`) |
| System and administrator consoles | Neutral only. Destructive actions must not be visually attractive |

---

## 7. Type scale for the ERP

Derived from `CB-001` §4.3, compressed for operational density. Bengali equivalents and minimum
sizes are in `VB-009`.

| Token | Desktop | Mobile | Weight | Line height | Use |
|---|---:|---:|---:|---:|---|
| `title-page` | 20px | 20px | 600 | 1.3 | Page or workspace title. There is no H1 above this |
| `title-section` | 16px | 16px | 600 | 1.35 | Section within a page |
| `title-card` | 14px | 14px | 600 | 1.4 | Card and panel headings |
| `body` | 14px | 15px | 400 | 1.6 | Prose, help, descriptions |
| `body-dense` | 13px | — | 400 | **1.4** | Table cells, list rows |
| `label` | 13px | 14px | 500 | 1.4 | Field labels, column headers |
| `caption` | 12px | 12px | 400 | 1.4 | Hints, metadata, timestamps |
| `numeric` | 14px | 15px | 500 | 1.4 | **Tabular figures, right-aligned** |
| `code` | 13px | 13px | 400 | 1.5 | Identifiers, references, serials |

| # | Rule |
|---|---|
| **TY-01** | **12px is the absolute floor** in English. Bengali has a higher floor — `VB-009` |
| **TY-02** | Mobile body is **larger** than desktop body, not smaller. Reading distance and conditions are worse |
| **TY-03** | All money and quantity uses `numeric` with tabular figures, right-aligned. Proportional figures make columns unscannable |
| **TY-04** | Identifiers — `SR-2026-114882`, IMEI, part numbers — use `code`. They are read character by character |
| **TY-05** | Never use weight below 400. `CB-001` §4.4 already states this |
| **TY-06** | Never use ALL CAPS except in status badges of 12 characters or fewer (`CG-003` §1.2) |

---

## 8. Logo in the ERP

| Rule | Detail |
|---|---|
| **LG-01** | One logo per screen, top-left, 28px height in operational surfaces, 40px in `P01`/`P07`/`P12` |
| **LG-02** | Clear space is the height of the "1" (`CB-001` §2.3), unchanged |
| **LG-03** | Below 100px width, use the icon mark only (`CB-001` §2.4) |
| **LG-04** | Never in a table, card, modal, notification body or repeated element |
| **LG-05** | On dark UI, use the reversed white logo |
| **LG-06** | Co-branding — brand partner marks in `P08`, payment marks at checkout — follows `CB-001` §2.5: 1000FiX equal or greater prominence, 2× clear space between marks |
| **LG-07** | In `P02` and `P09`, a 24px icon mark only, in the header, never in the job flow |

---

## 9. Do and do not

| Do not | Do |
|---|---|
| Use `#39B1DF` for link text | Use `#1E5F8A` for link text; keep `#39B1DF` for fills and the brand mark |
| Put a blue gradient header on the dispatch console | Use a 1px `#E9ECEF` rule and a neutral background |
| Set 48px page titles in a workspace | Use `title-page` at 20px |
| Use photography in an operational view | Use no image, or a single empty-state illustration |
| Signal status with the brand palette | Use the `VB-008` semantic palette, which is separate by design |
| Use Warning Yellow for text | Use yellow as a fill with `#212529` text |
| Add brand colour to table rows | Keep tables neutral; colour only the status cell |
| Ship the same density to `P03` and `P01` | Design `P03` to 1366×600 and `P01` to mobile-first |
| Put the logo in every card | One logo, one screen, top-left |
| Use colour alone to mean something | Pair colour with a label and an icon (`CG-011` CL-01) |

---

## 10. Dependencies

| Depends on | Why |
|---|---|
| `CB-001` Brand Guidelines (website set) | The brand this file applies and constrains |
| `VB-008` Status Colour and Label Semantics | The semantic palette that is deliberately not the brand palette |
| `VB-009` Bengali Typography Standard | Bengali minimum sizes, which are higher than English |
| `CG-011` Accessibility Content Standard | The contrast obligations §3 measures against |
| `04-00` §P03, PS-04, PS-05, PS-06 | Density, accessibility, responsiveness and single-design-system obligations |

---

## 11. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Contrast of every text/background token pair | Automated token audit against WCAG 2.1 AA | Every design-system release |
| Non-text contrast of borders, focus rings, status indicators | Automated, 3:1 threshold | Every design-system release |
| 1366×600 fit for `P03` workspaces | Visual regression at fixed viewport | Every `P03` release |
| Minimum type size | Automated token lint | Every design-system release |
| Logo usage | Manual design review | Per surface |
| No brand colour as the sole status signal | `CG-011` CL-01 review | Per surface |
| Full accessibility scan and manual audit | `05-06` §11 | Before each portal release |

---

## 12. Maintenance

| Item | Value |
|---|---|
| Review cadence | Every two waves |
| Out-of-cycle trigger | A `CB-001` revision; a Brand ruling on §3.2; a new portal; a change to the branch hardware baseline |
| Owner | Brand Lead, with Content Design Lead as approver |
| Open dependency | **§3.2 Brand decision on `#39B1DF`** — blocks final token approval |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](VB-004_Print_and_PDF_Brand_Template_Standard.md) | Brand in printed output |
| [`VB-005_Email_Brand_Template_Standard.md`](VB-005_Email_Brand_Template_Standard.md) | Brand in email |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](VB-008_Status_Colour_and_Label_Semantics_Register.md) | The semantic palette |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali type, which overrides §7 minimums |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Accessibility obligations |
| [`../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | T-A19 brand escalation |
| `MM-004` Icon Set Requirements | Icon style consistent with this |
| `TS-016` Accessibility Test Script Pack | Where §11 is executed |
| `CB-001` Brand Guidelines Document (website set) | Source palette and type scale |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Measured contrast finding on the full `CB-001` palette with six consequences, brand applied/reduced/excluded by surface, ERP type scale compressed for 1366×600, logo rules, do/do-not table. Escalates the `#39B1DF` text-contrast failure to Brand | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Contrast ratios computed from `CB-001` hex values, method and date stated (`CG-012` EV-06)
- [x] The accessibility finding is escalated per `CG-013` T-A19 rather than decided here
- [x] Brand treatment stated per surface — applied, reduced, excluded
- [x] Type scale reconciles to `CB-001` §4.3 with the compression rationale given
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; Bengali type is `VB-009`
- [ ] Named approver recorded — **pending**
- [ ] Brand ruling on §3.2 — **open; blocks design-system token approval**
- [x] Registered in the Content Master Index
- [x] Content risk `CR-13` raised for `RF-011`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
