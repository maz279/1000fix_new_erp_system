---
id: UX-001
title: Design System & Component Library Specification
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Design System Lead
approver: Design Authority (constituted under GV-002)
standards_basis: >
  W3C Design Tokens Format Module 2025.10 (DTCG, first stable version) ·
  WCAG 2.2 Level AA (W3C Recommendation) · ISO 9241-112:2017 (presentation of information) ·
  ISO/IEC 25010:2023 interaction capability · Semantic Versioning 2.0.0
traces_to: >
  PGD-000 UX-001 · NFR-080 (one design system) · NFR-073 (WCAG) · NFR-077 · NFR-081 ·
  PS-04, PS-05, PS-06 (04-00 §3) · AR-002 AP-04 · AR-012 FF-35 · SWR-006 ·
  VB-003, VB-006, VB-007, VB-008, VB-009 · audit findings PGD-A1-05, RQA-12
depends_on: AR-001 (deployment and surface set) · AR-002 (AP-04) · RQ-006 (NFR-080, NFR-073) · UX-007 (Bengali layout tolerances)
verified_on: 2026-08-18
priority: P0
needed_by: Now
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-001 — Design System & Component Library Specification

### Category 06 · Code `UX` · W3C Design Tokens Format Module 2025.10 · WCAG 2.2 AA

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 06 as `UX-001`.
> 2. **`PG-03` Count, do not consult.** Every figure describing the estate here was counted from the
>    filesystem at **2026-08-18 14:45 (+06)**. Where a counted figure disagrees with a published
>    one, the counted figure is used and the disagreement is recorded.
> 3. **`PG-06` Cite standards.** Conformance and departures are stated in §2.1.
> 4. **`PG-M4` Verify citations.** Standard and vendor-version claims carry `verified_on: 2026-08-18`.

---

## 1. Purpose

This document specifies the **single source of design truth** for the 1000FiX platform: the token
set every surface renders from, the component contract every surface honours, and the conformance
suite that proves a surface honours it.

It exists because `NFR-080` and `PS-06` commit the programme to *"a consistent design system across
all 12 portals — one component library, one token set"*, and **that promise cannot be kept in the
form it is written.** §3 establishes what can be kept instead, and makes it enforceable.

It unblocks four things that cannot start without it: front-end development on any surface
(`BE-004`), the screen inventory's classification of patterned versus bespoke work (`UX-003`), the
accessibility conformance design that must be satisfied at token level before it can be satisfied at
screen level (`UX-005`), and the Bengali layout tolerances that are a property of components, not of
strings (`UX-007`).

**What this adds to what already exists.** `VB-003` states how the brand behaves in dense
operational software and measures the contrast consequences. `VB-006` states what each component may
*say*. `VB-007` states which icon pairs with which label. `VB-008` states how a status is recognised.
`VB-009` states Bengali type metrics. **All five are content standards.** None of them specifies a
token, a component API, a state matrix, a build pipeline or a version policy — and none of them can
be compiled. This document is the engineering artefact those five standards presuppose.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The token architecture — tiers, naming grammar, file format, and the complete semantic token set |
| 2 | Colour, typography, spacing, sizing, radius, elevation, motion, border and z-index tokens, in light and dark themes |
| 3 | The component inventory — every component in the shared library, its states, variants and required props |
| 4 | The **realisation rule**: how one token source becomes five runtime targets without divergence |
| 5 | Distribution — the build pipeline, artefact formats, package names and versioning policy |
| 6 | Governance — contribution, review, deprecation and breaking-change procedure |
| 7 | Conformance — the automated checks that make the system binding rather than advisory |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The copy each component may carry | `VB-006` | A copy contract is a content standard; this document consumes it |
| The strings themselves | `UI-001`…`UI-042`, `BN-009`…`BN-013` | Content, not design |
| Which icon means what | `VB-007` | An icon register is a content standard; this document specifies icon *rendering* rules only |
| Which lifecycle states exist | `MD-027`, `05-02` DM-10 | This document carries the eight semantic tokens `VB-008` derived; it does not define states |
| Screen layouts assembled from components | `UX-003` | A component is not a screen |
| Interaction choreography and motion *behaviour* | `UX-004` | This document carries the motion **tokens**; `UX-004` carries the rules for using them |
| Bengali layout tolerances applied to a screen | `UX-007` | This document carries the per-language type and line-box tokens; `UX-007` carries the layout consequence |
| Brand identity and marketing application | `CB-001`, `VB-003` | The brand is upstream; §4.2 records where this document constrains it |
| Chart and dashboard visual grammar | `RP-007`, `UX-003` §7.6 | Metabase and Grafana are third-party surfaces — see §3.5 |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| Front-end engineers (Next.js, OWL 2, QWeb) | The token package to import; the component API to implement against |
| Mobile engineers (Flutter) | The Dart token artefact and the widget contract |
| Designers | The token names to design with; the component set to compose from |
| Content designers | The slot names and character budgets `VB-006` binds copy to |
| QA and accessibility reviewers | The state matrix and conformance suite to test against |
| Architecture (`AR-012`) | The fitness functions `FF-35` and the new checks in §11 |
| Vendors under `CO-003` | The deliverable definition for "conforms to the design system" |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **W3C Design Tokens Format Module 2025.10** (DTCG; first stable version, October 2025) | Whole | The token source in §5 is authored as DTCG JSON: `$value`, `$type`, `$description`, `$extensions`, `$deprecated`. Composite types (`typography`, `shadow`, `border`, `transition`) are used as typed values, not strings | **It is not a W3C Standard and is not on the W3C Standards Track.** Adopted anyway because it is the only vendor-neutral interchange format and every major transform tool consumes it. The dependency is recorded as risk `UX-R-02` |
| **WCAG 2.2 Level AA** | 1.4.3, 1.4.11, 1.4.12, 2.4.7, 2.4.11, 2.5.8, 3.2.6 | Every colour pair, focus token, target-size token and spacing token in §5 is set so that a component using tokens correctly cannot fail these criteria. Ratios are computed, not asserted | None. **2.2 governs, per `RQ-006` §3.7.** `UX-005` carries the full criteria matrix |
| **ISO 9241-112:2017** — presentation of information | §5 (organising), §6 (coding) | The three-signal rule (colour · glyph · label) inherited from `VB-008` is realised as a token-level constraint: no semantic colour token exists without a paired glyph and label token | None |
| **ISO/IEC 25010:2023** | Interaction capability | Appropriateness recognisability, learnability, operability, user error protection and **inclusivity** are the qualities this system is built to deliver; §11 states how each is measured | None |
| **Semantic Versioning 2.0.0** | Whole | The versioning policy in §10.3 | One addition: a **token-only** change that alters a rendered value is MAJOR, not MINOR — §10.3 rule `DSY-14` |
| Material Design 3 | Referenced, not adopted | Used as the Flutter baseline widget substrate only. **1000FiX tokens override M3 defaults; M3 colour roles are not used** | Adopting M3 wholesale would put Flutter surfaces on a different colour model from the web surfaces, which is the exact failure this document exists to prevent |

> **`PG-06` note on what was *not* adopted.** ISO 9241-125 (visual presentation) and ISO 9241-143
> (forms) are relevant and were reviewed; they are not cited as conformance bases because neither is
> testable in CI, and a standard this document cannot enforce would be decoration. They are named in
> §14 as design references.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `VB-003` §3, §5, §7 | `../../project_content/01_Voice_Brand_and_Design_Content/` | **Measured** contrast ratios of the `CB-001` palette; the operational density rules; the compressed type scale |
| `VB-006` §3–§9 | same | The copy contract per component and the character budgets, keyed to Bengali length |
| `VB-007` §3, §6, §7 | same | Icon pairing modes; the registered icon-only set; Bengali label allowances |
| `VB-008` §2, §3 | same | The three-signal rule; the eight semantic tokens with computed ratios; the dark-theme values |
| `VB-009` §2–§6 | same | Bengali typeface stack, minimum sizes, line heights, mixed-script rules |
| `04-00` §3 `PS-04`…`PS-08`, §P03 | `../../1000fix_ERP_Module/04_Portals_and_Applications/` | Accessibility, responsiveness, one-library and density obligations; the 1366×768 branch hardware |
| Technology Stack Specification §11 | `../../primary-doc/` | The runtime targets: OWL 2, Next.js 15→16 + React 19, Flutter, Odoo Portal, Metabase + Grafana |
| `AR-001` §6, §8 · `AR-002` AP-04 | `../02_Architecture_and_Design/` | Surface set and the "twelve surfaces, one design system" principle |
| `RQ-006` §3.7, §4.4 | `../01_Requirements_Engineering/` | The WCAG 2.2 AA ruling and the restated `NFR-073`, `NFR-080` |

### 2.3 Audit findings this document closes

| Finding | Source audit | How this document closes it |
|---|---|---|
| `PGD-A1-05` (design-system share) | `PGD-AUDIT-001` | Sizes the design-system stream against a counted component inventory (§8.7) rather than an inferred one; `UX-003` §9 restates the total |
| `A2-04` residual (surface divergence) | `PGD-AUDIT-003` | AP-04 becomes enforceable: §11 defines the checks that detect divergence at build time |
| `RQA-12` residual | `PGD-AUDIT-004` | The token set is authored to WCAG **2.2** thresholds — notably the 24×24 CSS px target token — so the ruling is realised, not merely recorded |
| **New — `UXA-01`** | This category | `NFR-080` as written is unsatisfiable. §3 rules what replaces it and the ruling is raised to `GV-003` for a `D-nnn` |

---

# 3. The Realisation Ruling — What "One Component Library" Can Mean

## 3.1 The problem, stated plainly

`NFR-080` and `PS-06` require **"one component library, one token set"** across all twelve portals.
Counted from the Technology Stack Specification §11 at 2026-08-18 14:45 (+06), the surfaces run on
**five distinct rendering runtimes**:

| # | Runtime | Surfaces | Language | Styling mechanism |
|---|---|---|---|---|
| **R1** | **Odoo Web — OWL 2** | `P03` (14 workspaces), `P09` coordinator view | TypeScript / XML templates | SCSS variables compiled by the Odoo asset bundler |
| **R2** | **Odoo Portal — QWeb** | `P05` (primary) | Python / QWeb XML | Bootstrap-derived SCSS in the `website` bundle |
| **R3** | **Next.js 15→16 + React 19** | `P01` web, `P04`, `P07`, `P08`, `P10`, `P12` | TypeScript / TSX | CSS custom properties |
| **R4** | **Flutter** | `P02` (APP-01), `P09` rider (APP-02), `P11` (APP-03), `P01` app (APP-04) | Dart | `ThemeData` / Dart constants — **no CSS of any kind** |
| **R5** | **Metabase + Grafana, embedded** | `P06` | Third-party | Vendor theming API only |

> **Dart cannot consume a CSS custom property. QWeb cannot consume a React component. Grafana
> cannot consume either.** A single component *library* — one package of one implementation — is
> therefore not achievable, and a requirement that cannot be satisfied will be quietly breached in
> Wave 1 and then cited as satisfied for thirty-six months.

**This is not a reason to abandon the requirement. It is a reason to state the achievable form of
it, and make that form testable.**

## 3.2 The ruling

> **`DSY-01` — One token source. One component contract. Five realisations. One conformance suite.**

| Element | Rule | Enforced by |
|---|---|---|
| **One token source** | A single DTCG JSON tree in one repository is the only place a design value is authored. Every runtime consumes a **generated** artefact; no runtime authors a value | §11 check `CFM-01` (no raw literals) |
| **One component contract** | Each component has one specification — name, props, slots, states, variants, accessibility semantics, copy contract — that all realisations implement identically. §8 is that specification | §11 check `CFM-04` (inventory parity) |
| **Five realisations** | `R1`…`R5` each ship an implementation of the contract. They are permitted to differ in code and **forbidden to differ in rendered result** beyond the platform-idiom allowances of §3.4 | §11 check `CFM-05` (visual parity) |
| **One conformance suite** | A single cross-runtime test suite asserts token values, state coverage, contrast, target size and Bengali fit against every realisation | §11 |

**`NFR-080` is therefore restated as:** *"All twelve surfaces shall render from one generated token
set and implement one component contract, verified by a single cross-runtime conformance suite."*
This restatement is raised to `GV-003` as a change to a baselined requirement and is recorded as
decision `UX-001-D-01`. **Until the Change Board rules, both statements are live and the stricter
reading — this one — is built to.**

## 3.3 Why not reduce the runtime count instead

Considered and rejected, with the reasoning recorded because it will be re-proposed:

| Option | Why rejected |
|---|---|
| Build `P03` in Next.js instead of OWL 2 | Discards the Odoo back office, which is the system of record's native surface. Re-implements ~782 generated views by hand (`UX-003` §5). Not proportionate |
| Build the four apps in React Native instead of Flutter | Reverses TD-03 and the Technology Stack Specification §11.9 ruling; introduces a second mobile toolchain if `P07` later needs one. `AR-010`'s offline engine is specified in Dart |
| Move `P06` off Metabase/Grafana | The analytics stack is chosen for the BI capability, not the UI. Rebuilding dashboards as bespoke screens adds ~24 screens and a permanent maintenance surface |
| Accept divergence | This is the status quo and it is what the requirement exists to prevent |

## 3.4 Permitted platform-idiom differences

A realisation **may** differ from the reference in these ways and only these. Anything else is a
defect under `CFM-05`.

| # | Permitted difference | Example | Boundary |
|---|---|---|---|
| `PID-01` | Native scroll physics and overscroll behaviour | iOS rubber-band, Android glow | Never changes what is on screen |
| `PID-02` | Native text-selection handles and context menus | Platform default | Never changes the selectable content |
| `PID-03` | Native date, time and number pickers | Android vs iOS wheel | **The value written must be identical**, and `BN-007` formats govern the display |
| `PID-04` | Native keyboard type and autofill hints | Numeric keypad for IMEI | Field semantics unchanged |
| `PID-05` | Native back-navigation affordance | Android hardware back, iOS swipe | The navigation model of `UX-002` is unchanged |
| `PID-06` | Elevation implementation | Material elevation vs CSS `box-shadow` | The **rendered** shadow must match the `elevation` token within tolerance `±2 px` blur |
| `PID-07` | Focus-ring rendering primitive | `outline` vs `Focus` widget | The rendered ring must match the `focus` token exactly (§5.9) — this one has no tolerance |

## 3.5 `R5` — the third-party exception, declared

Metabase and Grafana expose a **theming API, not a component model**. `P06` therefore conforms
partially and the partiality is declared rather than discovered:

| Aspect | `P06` conformance | Basis |
|---|---|---|
| Colour tokens | **Full** — the theming API accepts the palette | Vendor theming |
| Type tokens | **Partial** — family and base size settable; the scale is vendor-controlled | Vendor limitation |
| Component contract | **Not applicable** — charts, not components | §1.1 out of scope |
| Chart colour grammar | Governed by `RP-007`, which **must** consume the `chart-*` tokens in §5.10 | This document |
| Accessibility | **`P06` is the hardest surface** — `TS-016` `O-04` already records this | `UX-005` §7.4 |

> **`DSY-02`.** A surface that cannot fully conform declares its non-conformance in this section
> before release. **An undeclared partial conformance is a defect; a declared one is a decision.**

---

# 4. Design Principles

Six principles. Each is testable, and each names what it forbids — a principle that forbids nothing
constrains nothing.

| # | Principle | What it forbids | Test |
|---|---|---|---|
| `DSY-03` | **Operate, then impress.** Density and legibility win over brand expression on operational surfaces | Marketing density in a workspace; 48 px page titles; photography in a dispatch console | `VB-003` §5 density review; `CFM-08` viewport regression at 1366×600 |
| `DSY-04` | **Accessible by construction.** A component built from tokens cannot fail a colour, target-size or focus criterion | Any component that can be composed into a WCAG 2.2 AA failure using only documented props | `CFM-02`, `CFM-03`, `CFM-06` |
| `DSY-05` | **Bengali is the design case, English is the variant.** Every container is sized to the Bengali rendering | Sizing a toolbar to the English label; shortening Bengali to fit | `CFM-07` Bengali fit test; `UX-007` §5 |
| `DSY-06` | **Never colour alone.** Every semantic state carries colour **and** glyph **and** label | A status dot with no label; a red row with no marker | `CFM-09` greyscale render test |
| `DSY-07` | **Composition over configuration.** A component has few props with clear meaning; variation is achieved by composing components, not by adding flags | A component with more than 12 props, or any `variant` enum exceeding 6 members | `CFM-10` API surface lint |
| `DSY-08` | **One way to do a thing.** Where two components could serve a purpose, one is deprecated | Two toast implementations; a `Modal` and a `Dialog` | `CFM-04` inventory parity; §10.4 deprecation |

---

# 5. Token Architecture

## 5.1 Three tiers

Design values move through exactly three tiers. A surface may reference **tier 3 and tier 2 only**;
tier 1 is private to the system.

| Tier | Name | Example | Who may reference it |
|:--:|---|---|---|
| **1** | **Primitive** — a raw value with no meaning | `color.blue.700 = #1E5F8A` | The token source only |
| **2** | **Semantic** — a value with a role | `color.text.link = {color.blue.700}` | Any surface, any component |
| **3** | **Component** — a role scoped to one component | `button.primary.bg.default = {color.action.primary}` | That component's realisations only |

| # | Rule |
|---|---|
| `TKN-01` | **A surface never references tier 1.** A hex value in application code is a build failure (`CFM-01`) |
| `TKN-02` | A tier-2 token resolves to a tier-1 token or to another tier-2 token. It never carries a literal |
| `TKN-03` | A tier-3 token exists only where a component genuinely needs a value the semantic tier cannot express. **Adding one requires a stated reason in `$description`** |
| `TKN-04` | Alias chains are at most **three** links deep. Deeper chains are unreadable and defeat the purpose of naming |
| `TKN-05` | Every token carries a `$description`. A token whose purpose is not written down will be misused |
| `TKN-06` | **Themes redefine tier 2 only.** Light and dark differ in the semantic layer; no component token is themed |

## 5.2 Naming grammar

```
<tier-1>   color.<hue>.<step>              color.blue.700
           space.<step>                    space.4
           font.size.<step>                font.size.5

<tier-2>   <category>.<role>[.<state>]      color.text.link
                                           color.surface.raised
                                           color.status.error.fill
                                           space.inset.md
                                           type.body.bn

<tier-3>   <component>.<part>.<variant>.<state>
                                           button.label.primary.hover
                                           table.row.bg.selected
```

| # | Rule |
|---|---|
| `TKN-07` | Lower-case, dot-separated, no abbreviations except the registered set: `bg`, `fg`, `bn`, `en`, `md`, `sm`, `lg`, `xs`, `xl` |
| `TKN-08` | State suffixes are drawn from the closed set in §7.1. No component invents a state name |
| `TKN-09` | **No token name encodes its value.** `color.text.dark-blue` is forbidden; `color.text.link` is required. A name that encodes a value cannot be re-themed |
| `TKN-10` | Language-varying tokens carry a `.bn` or `.en` suffix and **both must exist**. A `.en` token with no `.bn` counterpart fails `CFM-07` |

## 5.3 File format — DTCG

The source is one JSON tree conforming to the **Design Tokens Format Module 2025.10**.

```json
{
  "color": {
    "text": {
      "link": {
        "$type": "color",
        "$value": "{color.blue.700}",
        "$description": "Link and interactive text on light surfaces. 6.86:1 on #FFFFFF. Brand #39B1DF is 2.46:1 and is prohibited here — VB-003 BC-01.",
        "$extensions": {
          "com.1000fix.contrast": { "on": "color.surface.base", "ratio": 6.86, "wcag": "AA" },
          "com.1000fix.since": "1.0.0"
        }
      }
    }
  },
  "type": {
    "body": {
      "bn": {
        "$type": "typography",
        "$value": {
          "fontFamily": "{font.family.bengali}",
          "fontSize": "{font.size.4}",
          "fontWeight": 400,
          "lineHeight": 1.7,
          "letterSpacing": "0"
        },
        "$description": "Bengali body. 16px floor per VB-009 MS-01; line height 1.7 per LH-01; letter-spacing is always zero per LH-02."
      }
    }
  }
}
```

| # | Rule |
|---|---|
| `TKN-11` | Every colour token carries a `com.1000fix.contrast` extension stating the background it was measured against, the computed ratio and the WCAG level. **A colour token with no measured ratio does not ship** |
| `TKN-12` | `$deprecated` is set — never deleted — when a token is retired. Deletion is a MAJOR change; deprecation is MINOR (§10.3) |
| `TKN-13` | The token tree is the **only** artefact under design ownership in the build. Generated outputs are never hand-edited; a hand-edited generated file fails `CFM-11` |

## 5.4 Colour — the semantic set

Values inherit `VB-003` §3 (measured against the `CB-001` palette) and `VB-008` §3 (the derived
semantic palette). **Ratios below are carried from those measurements; they were recomputed at
issue and are stated so the reader can check them.**

### 5.4.1 Text and surface — light theme

| Token | Value | On | Ratio | Use |
|---|---|---|---:|---|
| `color.text.primary` | `#212529` | `surface.base` | **15.43** | Body, table cells, headings |
| `color.text.secondary` | `#495057` | `surface.base` | **8.18** | Metadata, captions, help |
| `color.text.tertiary` | `#6C757D` | `surface.base` | **4.69** | Placeholder, disabled label — **AA, no margin; never below 14 px** |
| `color.text.link` | `#1E5F8A` | `surface.base` | **6.86** | Links and interactive text |
| `color.text.inverse` | `#FFFFFF` | `surface.inverse` | 15.43 | Text on dark surfaces |
| `color.text.on-brand` | `#212529` | `color.brand.primary` | 6.26 | **Text on brand blue is near-black, never white** — `VB-003` BC-03 |
| `color.surface.base` | `#FFFFFF` | — | — | Page background |
| `color.surface.raised` | `#F8F9FA` | — | — | Cards, panels |
| `color.surface.sunken` | `#E9ECEF` | — | — | Wells, table headers |
| `color.surface.inverse` | `#212529` | — | — | Dark bars, tooltips |
| `color.border.subtle` | `#E9ECEF` | `surface.base` | 1.19 | **Decorative rules only** — fails 1.4.11, may not be the sole boundary of a control |
| `color.border.default` | `#CED4DA` | `surface.base` | 1.62 | Decorative |
| `color.border.strong` | `#6C757D` | `surface.base` | **4.69** | **Control boundaries** — passes 1.4.11 |
| `color.brand.primary` | `#39B1DF` | — | **2.46** | **Fill, header band, chart series, selected-row background. Never text, never a focus ring, never the sole border** — `VB-003` BC-01 |
| `color.brand.deep` | `#1E5F8A` | `surface.base` | 6.86 | The text-safe brand colour |
| `color.brand.accent` | `#F26100` | `surface.base` | 3.24 | Large text ≥ 24 px, fills, icons ≥ 24 px |

> **`TKN-14` — the brand-blue guard.** `color.brand.primary` is defined with
> `$extensions.com.1000fix.prohibited: ["text", "focus", "border-sole", "icon-on-light"]`. The token
> linter (`CFM-02`) fails any component token that aliases it into a prohibited role. This turns
> `VB-003` BC-01 from a written rule into a build failure, which is the only form it survives in.

### 5.4.2 Status — the eight semantic tokens

Carried from `VB-008` §3.1 without alteration. Each token is a **triple**: text/border colour, fill
tint, and the glyph and label tokens that `DSY-06` requires.

| Token stem | Text / border | On white | Fill tint | Text on tint | Glyph | Meaning |
|---|---|---:|---|---:|:--:|---|
| `color.status.neutral` | `#495057` | 8.18 | `#E9ECEF` | 6.90 | ○ | Not started; no action implied |
| `color.status.progress` | `#1E5F8A` | 6.86 | `#E8F4FC` | 5.90 | ◐ | Under way, on track |
| `color.status.success` | `#146C43` | 6.45 | `#D1E7DD` | 4.97 | ✓ | Completed; no further action |
| `color.status.warning` | `#8A6100` | 5.54 | `#FFF3CD` | 5.00 | △ | At risk; action advisable |
| `color.status.error` | `#B02A37` | 6.50 | `#F8D7DA` | 4.86 | ✕ | Failed, breached or hard-blocked |
| `color.status.info` | `#0F6674` | 6.62 | `#CFF4FC` | 5.67 | ⏱ | Waiting on someone else; no fault |
| `color.status.hold` | `#59359A` | 8.75 | `#E2D9F3` | 6.44 | ‖ | Deliberately paused |
| `color.status.inactive` | `#6C757D` | 4.69 | `#F8F9FA` | 4.50 | ⊘ | Archived, cancelled, superseded |

| # | Rule |
|---|---|
| `TKN-15` | **A tint never appears without its border.** Tints are 1.1–1.4:1 against white and are not distinguishable alone. Every tinted surface carries a 1 px border in its text colour (`VB-008` SP-02) |
| `TKN-16` | Eight tokens. **A ninth requires a Design Authority decision and an `RF-006` entry** (`VB-008` SP-04) |
| `TKN-17` | The `CB-001` functional colours (`#28A745`, `#FFC107`, `#DC3545`, `#17A2B8`) remain valid **as fills only** and are not present in the semantic tier. They exist as tier-1 primitives so that legacy artwork can be referenced, and are marked `$deprecated` for interface use |

### 5.4.3 Dark theme

Carried from `VB-008` §3.3. **Dark theme is a `P02` / `P09` / `P11` field requirement, not a
preference** — see `UX-006` §6.4 for the sunlight/night rationale.

| Token stem | Text | Fill |
|---|---|---|
| `color.status.neutral` | `#ADB5BD` | `#343A40` |
| `color.status.progress` | `#7FC4E8` | `#1C3A4D` |
| `color.status.success` | `#75C69A` | `#12351F` |
| `color.status.warning` | `#E8B84B` | `#3D2E08` |
| `color.status.error` | `#E88A93` | `#3D171B` |
| `color.status.info` | `#6BC5D6` | `#0C2F35` |
| `color.status.hold` | `#B79BE0` | `#241A3D` |
| `color.status.inactive` | `#868E96` | `#2B2F33` |
| `color.text.primary` | `#F8F9FA` | — |
| `color.surface.base` | `#212529` | — |
| `color.surface.raised` | `#2B3035` | — |

> **`TKN-18`.** Brand blue `#39B1DF` **is** safe as text on `color.surface.base` in dark theme
> (6.26:1). This is the only context in which brand blue may carry text, and the linter's
> prohibition in `TKN-14` is theme-scoped accordingly.

## 5.5 Typography

### 5.5.1 The scale

Carried from `VB-003` §7, with the Bengali floors of `VB-009` §3 applied as a **separate token
family** rather than as a note. A single scale with a footnote about Bengali will be implemented as
a single scale.

| Token | EN desktop | EN mobile | **BN desktop** | **BN mobile** | Weight | LH EN | **LH BN** | Use |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `type.title.page` | 20 | 20 | 20 | 20 | 600 | 1.3 | **1.4** | Page or workspace title. There is no larger text |
| `type.title.section` | 16 | 16 | 17 | 17 | 600 | 1.35 | 1.4 | Section within a page |
| `type.title.card` | 14 | 14 | 16 | 16 | 600 | 1.4 | 1.4 | Card and panel headings |
| `type.body` | 14 | 15 | **16** | **17** | 400 | 1.6 | **1.7** | Prose, help, descriptions |
| `type.body.dense` | 13 | — | **15** | — | 400 | 1.4 | **1.55** | Table cells, list rows |
| `type.label` | 13 | 14 | **15** | 16 | 500 | 1.4 | 1.55 | Field labels, column headers |
| `type.caption` | 12 | 12 | **14** | **14** | 400 | 1.4 | 1.55 | Hints, metadata, timestamps |
| `type.numeric` | 14 | 15 | 14 | 15 | 500 | 1.4 | 1.4 | **Tabular figures, right-aligned. Arabic numerals in both locales** (`VB-009` §5.1) |
| `type.code` | 13 | 13 | 13 | 13 | 400 | 1.5 | 1.5 | Identifiers, serials, references — **always Latin** (`VB-009` MX-05) |
| `type.field.body` | 15 | **17** | 15 | **17** | 400 | 1.6 | 1.7 | `P02` / `P09` body — outdoors, in motion |
| `type.field.safety` | — | **19** | — | **19** | 600 | 1.5 | 1.6 | **`P02` / `P09` safety and custody text.** Never compressed to fit (`VB-009` MS-04) |

| # | Rule |
|---|---|
| `TYP-01` | **14 px is the absolute Bengali screen floor; 12 px the English.** No exception, no waiver (`VB-009` MS-01) |
| `TYP-02` | Mobile body is **larger** than desktop body (`VB-003` TY-02) |
| `TYP-03` | Line height is a **per-language** token. `LH-01` is realised by `type.*` carrying `.bn` and `.en` variants, not by a runtime multiplier |
| `TYP-04` | Bengali letter-spacing is **always zero**. The token exists and is locked at `0`; a component that sets tracking on `.bn` type fails `CFM-07` |
| `TYP-05` | Weight below 400 does not exist in the scale. Hind Siliguri Light loses conjunct strokes (`VB-009` TF-07) |
| `TYP-06` | ALL CAPS only in status badges of ≤ 12 characters (`VB-003` TY-06), and **never in Bengali** — Bengali has no case |
| `TYP-07` | All money and quantity uses `type.numeric` with tabular figures, right-aligned (`VB-003` TY-03) |

### 5.5.2 Font families and loading

| Token | Value | Notes |
|---|---|---|
| `font.family.latin` | `Inter, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` | |
| `font.family.bengali` | `"Hind Siliguri", "Noto Sans Bengali", "Nirmala UI", SolaimanLipi, Vrinda, sans-serif` | `VB-009` §2.1 |
| `font.family.mono` | `"JetBrains Mono", "SF Mono", Consolas, monospace` | Identifiers |

| # | Rule | Basis |
|---|---|---|
| `TYP-08` | `R4` Flutter surfaces **bundle** Hind Siliguri in the application package. A technician offline for 24 hours cannot download a font | `VB-009` TF-02 |
| `TYP-09` | `R3` web surfaces load Hind Siliguri with `font-display: swap` and subset to the Bengali block + Latin basic. **The subset budget is 120 KB** against the 400 KB first-load ceiling (`NFR-081`) | `NFR-081`, `TSA` |
| `TYP-10` | Latin inside Bengali sets in Inter, **one step smaller**, and every script change carries a `lang` attribute | `VB-009` MX-02…MX-04 |
| `TYP-11` | Every Bengali layout is verified at rank 1 (Hind Siliguri) **and** rank 2 (Noto Sans Bengali) before release — the metrics differ | `VB-009` MM-04 |

## 5.6 Space, grid and layout

| Token | Value | Use |
|---|---:|---|
| `space.0` … `space.10` | 0, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96 px | **8 px base grid**; 2 and 4 exist for dense table padding only |
| `space.inset.dense` | `space.2` (4 px) | Table cell padding |
| `space.inset.sm` | `space.3` (8 px) | Compact controls |
| `space.inset.md` | `space.5` (16 px) | Cards, panels |
| `space.inset.lg` | `space.6` (24 px) | Page gutters |
| `space.stack.*` | Same scale | Vertical rhythm between siblings |
| `size.target.min` | **24 px** | WCAG 2.2 SC 2.5.8 AA floor. **The absolute minimum any pointer target may be** |
| `size.target.comfortable` | **44 px** | The programme standard for all touch surfaces (`URD` §19.3, `VB-007` AC-06) |
| `size.target.field` | **56 px** | `P02` / `P09` gloved operation (`UX-006` §5.2) |
| `size.icon.sm` / `.md` / `.lg` | 16 / 20 / 24 px | Paired with `type.caption` / `type.body` / `type.title.section` |

### 5.6.1 Breakpoints and the density contract

| Token | Width | Density | Primary surfaces |
|---|---:|---|---|
| `bp.xs` | 320 px | Comfortable | `P01` app, `P02`, `P09`, `P11` — `PS-05` minimum |
| `bp.sm` | 600 px | Comfortable | Large phone, small tablet |
| `bp.md` | 905 px | Compact | Tablet, `P11` |
| `bp.lg` | **1366 px** | **Dense** | **The design target for `P03` — branch hardware** |
| `bp.xl` | 1920 px | Dense | Dispatch and analytics wall displays |

| # | Rule | Basis |
|---|---|---|
| `LAY-01` | The primary work area is designed to **1366 × 600** usable. A layout requiring more is a defect, not a large-screen feature | `VB-003` D-01 |
| `LAY-02` | Global chrome consumes **≤ 96 px** of vertical space in total | `VB-003` D-02 |
| `LAY-03` | A list view shows **≥ 12 rows** without scrolling at 1366 × 600 — **measured with Bengali `type.body.dense` at 15 px / 1.55**, not English at 13 px / 1.4 | `VB-003` D-03, tightened by `DSY-05` |
| `LAY-04` | Every surface is functional from 320 px with no horizontal scroll, and at 200 % zoom (WCAG 1.4.4, 1.4.10) | `PS-05`, `UX-005` |
| `LAY-05` | Density is a **token set**, not a component prop. A surface selects `density: dense \| compact \| comfortable` once; components read it | `DSY-07` |

> **`LAY-03` is the rule that will bite.** At English 13 px / 1.4 a row is ~18 px and 12 rows fit
> easily. At Bengali 15 px / 1.55 a row is ~23 px, and with `space.inset.dense` padding the same
> viewport holds ~11. **The Bengali case sets the row height and therefore the whole table design.**
> This is `DSY-05` in its most concrete form and it is why `UX-007` is `P1`, not `P3`.

## 5.7 Radius, elevation and border

| Token | Value | Use |
|---|---|---|
| `radius.none` / `.sm` / `.md` / `.pill` | 0 / 2 / 4 / 999 px | `radius.md` (4 px) is the default; expressive radii are excluded from operational surfaces (`VB-003` §5) |
| `elevation.0` | none | Default. **Operational surfaces are flat** |
| `elevation.1` | `0 1px 2px rgba(33,37,41,.10)` | Cards on `surface.base` |
| `elevation.2` | `0 4px 8px rgba(33,37,41,.12)` | Dropdowns, popovers |
| `elevation.3` | `0 12px 24px rgba(33,37,41,.16)` | Modals, drawers |
| `border.width.hairline` / `.default` / `.emphasis` | 1 / 1 / 2 px | `hairline` is decorative; `default` and `emphasis` carry meaning and use `color.border.strong` |

> **`TKN-19`.** Shadow appears only on overlay layers (`elevation.2`, `.3`). Depth cues cost
> rendering and attention (`VB-003` §5), and on `R4` they cost battery against `NFR-082`.

## 5.8 Motion

| Token | Value | Use |
|---|---:|---|
| `motion.duration.instant` | 0 ms | State changes with no spatial movement |
| `motion.duration.fast` | 120 ms | Hover, focus, small state changes |
| `motion.duration.base` | 200 ms | Dropdowns, tooltips, inline expansion |
| `motion.duration.slow` | 320 ms | Modals, drawers, page transitions |
| `motion.easing.standard` | `cubic-bezier(.2,0,0,1)` | Entering and moving |
| `motion.easing.exit` | `cubic-bezier(.4,0,1,1)` | Leaving |

| # | Rule | Basis |
|---|---|---|
| `MOT-01` | **`prefers-reduced-motion` collapses every duration to `instant`** and disables all transform-based transitions. This is a token-level switch, not a per-component opt-in | WCAG 2.3.3, `URD` §21.2 |
| `MOT-02` | No information is carried by motion alone | WCAG 1.3.3, `URD` §21.2 |
| `MOT-03` | On `R4`, animations that run while the screen is idle are prohibited — they defeat `NFR-082` | `NFR-082` |
| `MOT-04` | Motion **behaviour** — what animates, in what direction, and what it means — is `UX-004`'s. This section carries only the values | Boundary |

## 5.9 Focus — a token with no tolerance

| Token | Value |
|---|---|
| `focus.ring.color` | `#1E5F8A` (light) · `#7FC4E8` (dark) |
| `focus.ring.width` | 2 px |
| `focus.ring.offset` | 2 px |
| `focus.ring.style` | solid, fully surrounding the control |

| # | Rule | Basis |
|---|---|---|
| `FOC-01` | **Every interactive element has a visible focus indicator.** No exceptions, on any runtime | WCAG 2.4.7 |
| `FOC-02` | The ring meets **3:1 against both the component background and the adjacent background** | WCAG 1.4.11 |
| `FOC-03` | Focus is **never removed** — `outline: none` without a replacement is a build failure (`CFM-06`) | WCAG 2.4.7 |
| `FOC-04` | A focused element is **never entirely obscured** by sticky headers, banners or chat widgets. Sticky regions declare their height so scroll-into-view can compensate | **WCAG 2.2 SC 2.4.11 — new in 2.2** |
| `FOC-05` | `PID-07` applies: focus-ring rendering has **no platform tolerance** | §3.4 |

> `FOC-04` is the one most likely to be breached on `P03`. Fourteen workspaces with a fixed header
> and a fixed action bar create exactly the sticky-obscuring geometry SC 2.4.11 was written for.
> `CFM-06` tests it at build time on every workspace.

## 5.10 Chart tokens — the `RP-007` boundary

`P06` and every embedded chart consume a **separate, ordered categorical sequence**, because status
colours must not be reused as series colours.

| Token | Value | Ratio on white |
|---|---|---:|
| `chart.series.1` … `.8` | `#1E5F8A`, `#F26100`, `#146C43`, `#59359A`, `#0F6674`, `#8A6100`, `#B02A37`, `#495057` | all ≥ 5.54 |
| `chart.grid` | `#E9ECEF` | decorative |
| `chart.axis` | `#6C757D` | 4.69 |

| # | Rule |
|---|---|
| `TKN-20` | Series colours are **ordered**; a chart with *n* series uses `series.1`…`series.n` in order, so the same series occupies the same colour across dashboards |
| `TKN-21` | **Series colour is never the sole encoding.** Direct labels or a pattern fill accompany every series (WCAG 1.4.1) |
| `TKN-22` | Status tokens are **prohibited** as series colours. A green bar meaning "Q3" and a green badge meaning "complete" in the same viewport is the defect this prevents |

---

# 6. Theme and Locale Model

A surface resolves its rendering from **three orthogonal axes**. They compose; they do not
interact.

| Axis | Values | Selected by | Persisted |
|---|---|---|---|
| **Theme** | `light`, `dark`, `high-contrast` | User preference, with OS default | Per user, per device |
| **Density** | `comfortable`, `compact`, `dense` | Surface class (§5.6.1), not the user | Per surface |
| **Locale** | `bn-BD`, `en-BD` | User preference; `UX-007` §3 sets the default per surface | Per user, synced |

| # | Rule |
|---|---|
| `THM-01` | **3 × 3 × 2 = 18 valid renderings.** The conformance suite tests every component in all 18 (§11 `CFM-12`) |
| `THM-02` | `high-contrast` is a distinct theme, not a filter. It raises every text pair to **≥ 7:1** (AAA) and every non-text pair to ≥ 4.5:1, and it is the **`P02` / `P09` sunlight mode** |
| `THM-03` | Theme and locale are **independent**. A Bengali dark-theme dense table is a valid rendering and is tested as one |
| `THM-04` | A component never reads the locale to change its *structure* — only its type tokens and its container sizing. Structural branching by language is a design defect (`UX-007` §4) |

---

# 7. Component States

## 7.1 The closed state set

**Every interactive component implements all applicable states. A component missing an applicable
state is incomplete, not minimal.**

| State | Applies to | Token suffix | Required behaviour |
|---|---|---|---|
| `default` | All | `.default` | Resting |
| `hover` | Pointer surfaces | `.hover` | **Never the only affordance** — touch surfaces have no hover |
| `focus` | All interactive | `.focus` | §5.9 ring; never suppressed |
| `active` | All interactive | `.active` | Pressed |
| `selected` | Selectable | `.selected` | Carries a non-colour signal (`DSY-06`) |
| `disabled` | All interactive | `.disabled` | **Accompanied by text saying why** (`VB-006` BT-05). A bare disabled control is a dead end |
| `loading` | Async actions | `.loading` | Shows progress; announces via live region (`UI-008`) |
| `error` | Inputs, forms | `.error` | Message adjacent, in the user's language (`NFR-078`) |
| `readonly` | Inputs | `.readonly` | Visually distinct from `disabled` — different meaning, different token |
| `empty` | Collections | — | `UI-006` copy; never a blank region |
| `offline` | `R4` + PWA | `.offline` | **`UX-006` §4 states**; a component that can be used offline says so |
| `stale` | Cached data | `.stale` | Shows the age of the data and a refresh affordance (`URD` §20.2) |

| # | Rule |
|---|---|
| `CMP-01` | A component's specification names which of the twelve states apply. **"Not applicable" is a stated decision, not an omission** |
| `CMP-02` | `offline` and `stale` are first-class states, not error states. Conflating them with `error` is the defect `AR-010` §6.1 warns against |
| `CMP-03` | `disabled` and `readonly` are never the same token. `readonly` means "you may read this"; `disabled` means "you may not act, and here is why" |
| `CMP-04` | Every state change that matters to a screen-reader user is announced through a live region (`UI-010` §3.2) |

## 7.2 The mandatory data states

Any component that displays server data implements **six** data states. `UX-003` §6 requires the
same six per screen; they are the same six, specified once here.

| # | State | Copy source | Never |
|---|---|---|---|
| 1 | **Loading** | `UI-008` | A blank region; a spinner with no label after 2 s |
| 2 | **Empty — nothing yet** | `UI-006` §3.1 | "No data" |
| 3 | **Empty — no results** | `UI-006` §3.2 | The same copy as "nothing yet" — they need different actions |
| 4 | **Populated** | — | — |
| 5 | **Error** | `UI-004` §5.2 | A bare code; a stack trace |
| 6 | **No permission** | `UI-006` §3.4 | Revealing that the record exists (`URD` §19.4) |

---

# 8. Component Inventory

## 8.1 How this inventory was derived

Composed from three counted sources, reconciled:

| Source | Contribution | Counted at |
|---|---|---|
| `VB-006` §4–§7 component blocks | 20 components already carrying a copy contract | 2026-08-18 14:45 (+06) |
| `VB-007` §5 registered icon-only controls + §6 icon register | Icon, glyph and badge primitives | same |
| The 42 `UI-*` copy packs — every distinct control referenced | 31 further components implied by existing copy but not yet in any library | same |

**Counted total: 68 components in six tiers.** Every one is listed. A component not in this list
does not exist; adding one follows §10.2.

## 8.2 Tier 1 — Foundation (7)

| # | Component | States | Key props | Notes |
|---|---|---|---|---|
| `C-01` | `Box` | — | `as`, `padding`, `background`, `border`, `radius` | Layout primitive; consumes tokens only |
| `C-02` | `Stack` | — | `direction`, `gap`, `align`, `wrap` | 8 px grid enforced |
| `C-03` | `Grid` | — | `columns`, `gap`, `breakpoint` | Responsive from `bp.xs` |
| `C-04` | `Text` | — | `variant`, `lang`, `truncate` | **`lang` is required** — drives type family and line height (`TYP-03`, `TYP-10`) |
| `C-05` | `Icon` | default, disabled | `name`, `size`, `decorative`, `label` | `decorative=false` requires `label` (`VB-007` AC-01) |
| `C-06` | `VisuallyHidden` | — | — | Screen-reader-only text (`UI-010` §3.3) |
| `C-07` | `FocusRing` | focus | — | Single implementation of §5.9; components never draw their own |

## 8.3 Tier 2 — Controls (16)

| # | Component | States | Copy contract | Notes |
|---|---|---|---|---|
| `C-08` | `Button` | 6 (+ loading) | `VB-006` §4.1 | Label ≤ **20 BN chars**; one primary per view (BT-03) |
| `C-09` | `IconButton` | 6 | `VB-006` §4.1 + `VB-007` §5 | **Only the registered icon-only set**; requires accessible name |
| `C-10` | `Link` | 5 | `VB-006` §4.2 | `color.text.link`; never `brand.primary` |
| `C-11` | `TextField` | 8 | `VB-006` §6.2, `UI-003` | Label always visible; placeholder is never the label |
| `C-12` | `NumberField` | 8 | `UI-003` §3.4 | `type.numeric`; Arabic digits both locales (`BN-007` §3.3) |
| `C-13` | `TextArea` | 8 | `UI-003` | Bengali line height; no fixed pixel height (`VB-009` MM-02) |
| `C-14` | `Select` | 8 | `VB-006` §6.2 | Native picker allowed under `PID-03` |
| `C-15` | `Combobox` | 8 | `UI-041` | Typeahead in **both scripts simultaneously** (`URD` §19.2) |
| `C-16` | `Checkbox` | 7 | `VB-006` §6.2 | Target `size.target.comfortable` |
| `C-17` | `Radio` | 7 | `VB-006` §6.2 | |
| `C-18` | `Switch` | 7 | `VB-006` §6.2 | **Label states the on-meaning**, not "Enabled" |
| `C-19` | `DatePicker` | 8 | `BN-007` §5 | DD/MM/YYYY; Bengali month names in `bn-BD` prose only |
| `C-20` | `TimePicker` | 8 | `BN-007` §6 | |
| `C-21` | `FileUpload` | 9 | `UI-003` | Malware-scan wait state (`NFR-063`); offline queue state |
| `C-22` | `SignaturePad` | 7 | `UI-037`, `DT-002` | Custody evidence; `UX-006` §7.3 |
| `C-23` | `ScanInput` | 8 | `UI-012` | Barcode / QR / IMEI; **scan-first, type-fallback** (`URD` §21.3) |

## 8.4 Tier 3 — Data display (14)

| # | Component | States | Notes |
|---|---|---|---|
| `C-24` | `Table` | 12 + 6 data states | Column header = `type.label`; cells `type.body.dense`; **`LAY-03` row-height rule** |
| `C-25` | `TableToolbar` | 6 | Bulk actions with preview and confirmation (`URD` §19.2) |
| `C-26` | `DataList` | 6 data states | Mobile equivalent of `Table`; never a horizontally scrolling table |
| `C-27` | `Card` | 6 | `VB-006` §6.4 |
| `C-28` | `DescriptionList` | 4 | Record detail key–value pairs |
| `C-29` | `Badge` | 4 | **Tint + 1 px border + glyph + label** (`TKN-15`, `DSY-06`) |
| `C-30` | `StatusChip` | 5 | The eight semantic tokens only |
| `C-31` | `Avatar` | 3 | Technician photo; initials fallback |
| `C-32` | `Timeline` | 6 | Order status history; customer-facing labels only (`MD-027`) |
| `C-33` | `KeyValueTile` | 5 | Dashboard metric; `type.numeric` |
| `C-34` | `Chart` | 6 data states | Wraps `RP-007` grammar; `chart.series.*` tokens; direct labels required |
| `C-35` | `Map` | 7 + offline | Live technician / rider position; **degraded and offline states are mandatory** (`URD` §20.5) |
| `C-36` | `MediaViewer` | 6 | Evidence photographs; EXIF/GPS shown |
| `C-37` | `DocumentPreview` | 6 | PDF and print previews |

## 8.5 Tier 4 — Feedback (11)

| # | Component | States | Copy contract | Notes |
|---|---|---|---|---|
| `C-38` | `InlineValidation` | 3 | `VB-006` §5.1 | Adjacent to the field; never colour alone |
| `C-39` | `Toast` | 4 | `VB-006` §5.2 | **Never for errors requiring action**; auto-dismiss ≥ 6 s, pausable |
| `C-40` | `InlineAlert` | 4 | `VB-006` §5.3 | |
| `C-41` | `Banner` | 4 | `VB-006` §5.4 | Persistent; the offline banner is a `Banner` (`UI-009`) |
| `C-42` | `Modal` | 5 | `VB-006` §5.5 | Focus trapped; `Esc` closes; returns focus to the trigger |
| `C-43` | `ConfirmDialog` | 5 | `VB-006` §5.5, `UI-007` | **Names the specific item**; destructive verb on the button (BT-04) |
| `C-44` | `EmptyState` | 3 | `UI-006` | Four distinct kinds (§7.2 states 2, 3, 6 + not-configured) |
| `C-45` | `ErrorPage` | 2 | `VB-006` §5.7 | Full brand (`VB-003` §4) |
| `C-46` | `ProgressBar` | 4 | `UI-008` | Determinate wherever a total is knowable |
| `C-47` | `Spinner` | 2 | `UI-008` | **Labelled after 2 s**; never bare beyond that |
| `C-48` | `SkeletonLoader` | 2 | — | Respects `prefers-reduced-motion` (`MOT-01`) |

## 8.6 Tier 5 — Navigation and structure (12)

| # | Component | States | Notes |
|---|---|---|---|
| `C-49` | `AppShell` | 4 | Global chrome ≤ 96 px (`LAY-02`); declares sticky height for `FOC-04` |
| `C-50` | `WorkspaceSwitcher` | 5 | `P03`'s fourteen workspaces, one click from home |
| `C-51` | `PrimaryNav` | 5 | **≤ 7 top-level items** (`URD` §19.2) |
| `C-52` | `Breadcrumb` | 3 | On every drill-down screen |
| `C-53` | `Tabs` | 6 | Keyboard-operable per ARIA APG |
| `C-54` | `Stepper` | 6 | `VB-006` §7.1; booking is ≤ 3 steps (`04-00` §P01) |
| `C-55` | `Drawer` | 5 | Focus trapped as `Modal` |
| `C-56` | `Menu` | 6 | |
| `C-57` | `Pagination` | 5 | |
| `C-58` | `SearchBar` | 7 | Global; **accepts Bengali and English simultaneously** (`URD` §19.2) |
| `C-59` | `FilterPanel` | 7 | Saved views (`UI-041`) |
| `C-60` | `HelpLauncher` | 3 | **Same position on all twelve surfaces — WCAG 2.2 SC 3.2.6 Consistent Help** |

## 8.7 Tier 6 — Domain components (8)

Components that encode 1000FiX-specific meaning. They are in the shared library because
re-implementing them per surface is how the estate diverges.

| # | Component | Used by | Notes |
|---|---|---|---|
| `C-61` | `StatusIndicator` | All | The `VB-008` triple — colour, glyph, label — as one component. **The single most-used component in the system** |
| `C-62` | `SyncStatusBar` | `P02`, `P09`, `P11`, `P01` app | **Two distinct indicators: saved-on-device and sent-to-office** (`AR-010` §6.1). Queue depth and last-sync time always visible |
| `C-63` | `ConflictDisclosure` | `P02`, `P09`, `P11` | Realises `AR-010` §6.3. **Discloses a server-authoritative outcome; it does not offer a choice** — see `UXA-06` |
| `C-64` | `EntitlementBadge` | `P01`, `P03`, `P04`, `P10` | Warranty / AMC / MSP coverage at a glance |
| `C-65` | `MoneyAmount` | All | `type.numeric`, lakh/crore grouping, `৳`/`BDT` per locale (`BN-007` §4.2) |
| `C-66` | `IdentifierText` | All | `type.code`; character-by-character legibility; never transliterated |
| `C-67` | `EvidenceCapture` | `P02`, `P09`, `P11` | Photo + GPS + timestamp; on-device compression (`URD` §20.4) |
| `C-68` | `ConsentBlock` | `P01`, `P04`, `P07`, `P12` | `LG-008`, `UI-042`; granular, withdrawable, logged |

## 8.8 Component specification schema

Every component in §8.2–§8.7 carries a specification record with these fields. **A component
without a complete record does not enter the library** (`CFM-04`).

```yaml
id: C-08
name: Button
tier: 2 — Controls
purpose: Triggers an action in the current context.
props:
  - name: variant
    type: primary | secondary | tertiary | destructive
    required: true
  - name: size
    type: sm | md | lg
    default: md
  - name: loading
    type: boolean
    default: false
slots:
  - name: label
    content_contract: VB-006 §4.1
    budget_bn_chars: 20
  - name: icon
    content_contract: VB-007 §6.2
    optional: true
states: [default, hover, focus, active, disabled, loading]
a11y:
  role: button
  name_from: label slot
  target_min: size.target.comfortable
  criteria: [2.4.7, 2.5.8, 1.4.11, 3.2.6]
tokens:
  - button.primary.bg.*
  - button.primary.fg.*
  - button.radius
realisations: [R1, R2, R3, R4]
bengali:
  container_sizing: Bengali rendered width + 10%   # VB-007 BL-01
  overflow_rule: two-line icon-above-label, never truncate   # VB-007 BL-05
since: 1.0.0
```

---

# 9. Distribution and Build

## 9.1 The pipeline

```
                    design-tokens/            ◄── the ONLY authored source
                    ├── primitive/*.json
                    ├── semantic/*.json
                    └── component/*.json
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Token transform     │   Style Dictionary, DTCG-native
                   │  + contrast validator│   fails the build on any unmeasured colour
                   └──────────┬───────────┘
                              │
      ┌───────────┬───────────┼───────────┬────────────┐
      ▼           ▼           ▼           ▼            ▼
  R1 OWL 2     R2 QWeb     R3 Next.js   R4 Flutter   R5 Metabase
  _tokens.scss _tokens.scss tokens.css  tokens.dart  theme.json
      │           │           │           │            │
      ▼           ▼           ▼           ▼            ▼
  fix_web_ui/  fix_portal/  @1000fix/ui  fix_ui (pub)  (config only)
  (Odoo addon) (Odoo addon) (npm)        (Dart pkg)
      └───────────┴───────────┴───────────┴────────────┘
                              │
                              ▼
                  Cross-runtime conformance suite  (§11)
```

## 9.2 Published artefacts

| Artefact | Registry | Consumed by | Contains |
|---|---|---|---|
| `@1000fix/design-tokens` | private npm | R1, R2, R3, and the transform | The DTCG source and all generated formats |
| `@1000fix/ui` | private npm | R3 | React 19 components, `C-01`…`C-68` |
| `fix_web_ui` | Odoo addon repo | R1 | OWL 2 components + SCSS tokens |
| `fix_portal_ui` | Odoo addon repo | R2 | QWeb templates + SCSS tokens |
| `fix_ui` | private pub registry | R4 | Flutter widgets + `tokens.dart` |
| `fix-theme.json` | config repo | R5 | Metabase/Grafana theme payload |

| # | Rule |
|---|---|
| `DSY-09` | **All six artefacts are released from one version number.** A surface on `@1000fix/ui@2.3.0` and another on `fix_ui@2.1.0` is the divergence this document exists to prevent |
| `DSY-10` | The token transform runs in CI, never on a developer machine as the source of a committed file. Generated files are committed **by CI only** (`CFM-11`) |
| `DSY-11` | Every artefact publishes a `tokens.lock.json` digest. `CFM-01` compares the digest across all six; a mismatch fails every surface's build |

## 9.3 Versioning

| Change | Level | Rule |
|---|---|---|
| New component; new token; new optional prop | **MINOR** | |
| Bug fix with no rendered change | **PATCH** | |
| Removing a component, token or prop | **MAJOR** | |
| Renaming anything | **MAJOR** | |
| **Changing a rendered token value** | **MAJOR** — `DSY-14` | A departure from SemVer, which would call this MINOR. It is MAJOR here because a colour or size change can break a WCAG conformance claim and a visual regression baseline across twelve surfaces |
| Deprecating without removing | MINOR | `$deprecated` set; removal no earlier than the next MAJOR |

| # | Rule |
|---|---|
| `DSY-14` | **A change to a rendered token value is MAJOR**, not MINOR — the departure from SemVer stated in the table above and in §2.1 |
| `DSY-12` | A MAJOR release requires a **migration note** naming every affected component and a codemod where one is mechanically possible |
| `DSY-13` | Surfaces have **one wave** to adopt a MAJOR. Running two MAJORs concurrently across the estate is permitted only within that window, and the window is tracked in `GV-005` |
| `DSY-15` | The library is versioned independently of the ERP release train, but a **wave gate cannot be passed while any surface is more than one MAJOR behind** (`GV-009`) |

---

# 10. Governance

## 10.1 Ownership

| Role | Accountability |
|---|---|
| **Design System Lead** (owner) | The token source, the component contract, the release |
| **Design Authority** (`GV-002`) | Approves MAJOR releases, new tier-2 tokens, and any §3.5 partial-conformance declaration |
| **Content Design Lead** | Owns `VB-006`; approves every copy contract change |
| **Accessibility reviewer** | Approves every component's `a11y` block. **This role does not exist yet — `UXA-03`** |
| **Localisation Lead** | Approves `.bn` token values and Bengali container rules |
| Surface tech leads (×5) | Deliver and maintain their runtime's realisation |

## 10.2 Adding a component

| Step | Gate |
|---|---|
| 1 | **Is it composition?** If `C-01`…`C-68` can compose it, it is not a component (`DSY-07`) |
| 2 | Used on **≥ 2 surfaces**, or once on `P03` where fourteen workspaces share it |
| 3 | `VB-006` copy contract block written and approved |
| 4 | Specification record (§8.8) complete, including the Bengali container rule |
| 5 | All applicable states from §7.1 specified |
| 6 | Accessibility block approved |
| 7 | Realised on **every runtime the specification names** — a component realised on R3 only is not in the library, it is in `P04` |
| 8 | Conformance suite extended |

## 10.3 Changing a component

Breaking changes follow §9.3. **Non-breaking changes still require the copy contract and
accessibility approvals** — a prop that changes what a component can say is a content change.

## 10.4 Deprecation

| # | Rule |
|---|---|
| `DSY-16` | Deprecation sets `$deprecated` with a replacement and a removal version. It never deletes |
| `DSY-17` | A deprecated component emits a build-time warning naming its replacement |
| `DSY-18` | Removal happens at the next MAJOR, and not before every surface has migrated (`CFM-04` reports usage) |

---

# 11. Conformance — Making It Binding

> **A design system that is not tested is a style guide.** `AR-012` `FF-35` already gates portal
> builds on axe-core. These twelve checks extend it, and each names the failure it prevents.

| # | Check | Runs | Level | Fails when |
|---|---|---|---|---|
| `CFM-01` | **No raw literals.** No hex, rgb, px font size, or px spacing in application code | Every build, all runtimes | **Block** | Any literal outside the token source |
| `CFM-02` | **Token contrast.** Every colour token pair recomputed against WCAG 2.2 thresholds | Token release | **Block** | Any pair below its declared level, or any token with no measured ratio |
| `CFM-03` | **Target size.** Every interactive token ≥ `size.target.min` (24 px); touch surfaces ≥ 44 px | Every build | **Block** | Below threshold — WCAG 2.2 SC 2.5.8 |
| `CFM-04` | **Inventory parity.** All 68 components present on every runtime their spec names; prop signatures match | Nightly, cross-runtime | **Block** | Any divergence |
| `CFM-05` | **Visual parity.** Reference renders of each component compared across R1–R4 within the §3.4 tolerances | Nightly | **Block** | Difference beyond `PID-01`…`PID-07` |
| `CFM-06` | **Focus.** Every interactive element has a visible ring; no `outline:none`; **no focused element fully obscured** | Every build | **Block** | WCAG 2.4.7 / 2.4.11 failure |
| `CFM-07` | **Bengali fit.** Every component rendered with the `BN` string bundle and the longest registered string; overflow detected | Every build | **Block** | Any truncation of a *label* (truncation of a data cell with a tooltip passes) |
| `CFM-08` | **Viewport.** `P03` workspaces rendered at 1366 × 600, Bengali dense; row count asserted | Every `P03` build | **Block** | Fewer than 12 rows, or any horizontal scroll |
| `CFM-09` | **Greyscale.** Every status rendering converted to greyscale; glyph and label asserted present | Every build | **Block** | Colour is the sole signal — WCAG 1.4.1 |
| `CFM-10` | **API surface.** Prop count ≤ 12; variant enums ≤ 6 | Every build | Warn | `DSY-07` breach |
| `CFM-11` | **Generated-file integrity.** Generated artefacts match a fresh transform of the source | Every build | **Block** | A hand-edited generated file |
| `CFM-12` | **Theme matrix.** Every component rendered in all 18 combinations of theme × density × locale | Nightly | **Block** | Any combination unrendered or failing `CFM-02` |

> **`CFM-05` is the check that makes §3.2 real.** Without it, "five realisations, one contract" is an
> aspiration. With it, a Flutter button that drifts from the React button fails the nightly build
> and someone fixes it that week rather than in Wave 6.

### 11.1 What these checks do not catch

Stated so it is not assumed away:

| Not caught | Caught by |
|---|---|
| An accessible name that is present but meaningless | Manual audit — `TS-016`, `UX-005` §8 |
| A focus order that makes a task impossible | Manual audit |
| Bengali conjuncts rendering as boxes on a specific device | Device verification — `VB-009` §7, `UX-007` §7 |
| Whether the screen is the right screen | `UX-003`, `UX-008` |
| Whether the component was the right choice | Design review |

---

# 12. Adoption Plan

| Wave | Deliverable | Gate |
|:--:|---|---|
| **W0** | Token source, transform pipeline, `CFM-01`, `CFM-02`, `CFM-03`, `CFM-11`. Tiers 1–2 components on R1 and R3 | Cannot start `P03` |
| **W1** | Tiers 3–5 on R1 (`P03`'s 14 workspaces) and R3. `CFM-06`, `CFM-07`, `CFM-08`, `CFM-09` live | **`GV-009` Gate 1** |
| **W2** | R4 realisation complete (`C-61`…`C-67` for APP-01). `CFM-04`, `CFM-05`, `CFM-12` live | **Gate 2 — APP-01 cannot ship without `C-62`, `C-63`** |
| **W3** | R2 realisation (`P05`). Rider-specific field tokens | Gate 3 |
| **W4** | R5 theme payload (`P06`); §3.5 partial conformance declared and approved | Gate 4 |
| **W5–W9** | Maintenance; one MAJOR per year maximum | Standing |

> **The W0 dependency is the one to watch.** `P03` is a Wave 1 surface and `GV-004` already
> finds Wave 1 over-committed at **5.33×**. If the token pipeline is not delivered in W0, fourteen
> workspaces will be built against hard-coded values and `CFM-01` will be switched off to unblock
> them. Raised as `UXA-02` and as risk `UX-R-01`.

---

# 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-001-D-01` | How to satisfy `NFR-080` across five runtimes | (a) one literal library; (b) one token source + one contract + N realisations; (c) reduce the runtime count | **(b)** | (a) is not achievable in any language combination present; (c) discards architecture decisions already taken for stronger reasons | `NFR-080` is restated. Raised to `GV-003` for a `D-nnn`; **`CFM-04`/`CFM-05` are the compensating controls** |
| `UX-001-D-02` | Token interchange format | (a) DTCG 2025.10; (b) Style Dictionary native; (c) bespoke YAML | **(a)** | The only vendor-neutral format with a stable version and multi-tool support; typed composites remove stringly-typed shadows and type ramps | Dependency on a non-W3C-track specification — risk `UX-R-02` |
| `UX-001-D-03` | Whether Bengali type is a variant or a family | (a) one scale + runtime multiplier; (b) **separate `.bn` token family** | **(b)** | A multiplier cannot express different *floors*; `VB-009` MS-01 sets floors, not ratios | Every type token exists twice; `TKN-10` enforces the pair |
| `UX-001-D-04` | Semantic-value change severity | (a) MINOR per SemVer; (b) **MAJOR** | **(b)** | A value change can break a conformance claim and every visual baseline across twelve surfaces | Fewer, larger releases; `DSY-12` migration notes become mandatory |
| `UX-001-D-05` | Material Design 3 on Flutter | (a) adopt M3 roles; (b) **M3 substrate, 1000FiX tokens override** | **(b)** | Adopting M3 colour roles would put R4 on a different colour model from R1–R3 | Flutter theming is more work; parity is achievable |
| `UX-001-D-06` | `P06` conformance | (a) rebuild dashboards natively; (b) **declared partial conformance** | **(b)** | ~24 screens and a permanent maintenance surface for a vendor-controlled UI | §3.5 declaration requires Design Authority approval each release |

---

# 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who is the accessibility reviewer?** `GV-010` `Q-05` and `TS-016` `O-02` both record the role as unfilled. No component's `a11y` block can be approved without it | CTO | **W0** | §10.1, every component release |
| `Q-02` | Is the corporate website (`ES-03`) inside the design system's scope? `AR-002` `Q-02` raises the same question from the other side | CTO / Marketing | W1 | Token scope, `CB-001` reconciliation |
| `Q-03` | Does the Next.js 15 → 16 upgrade (Technology Stack `TSA-05`) happen before or after the R3 realisation? Building against 15 and migrating is rework; waiting delays W1 | Chief Architect | **W0** | R3 delivery |
| `Q-04` | Is `high-contrast` a third theme or a `dark` variant? §5 assumes a third theme; that is 6 more renderings in `CFM-12` | Design System Lead | W1 | `THM-02`, test matrix size |
| `Q-05` | Which Bengali numeral policy applies? `VB-009` NU-03 states the policy is **proposed** and `BN-007` is authoritative; `BN-007` §3.1 states a decision but `CG-010` §12 still records it open | Localisation Lead | W1 | `C-12`, `C-65`, `type.numeric` |
| `Q-06` | Do the four Flutter apps share one `fix_ui` package, or does `P02` fork for field-specific tokens? | Mobile Lead | W2 | `DSY-09` single-version rule |

---

# 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every runtime in the estate is named and its conformance position stated | §3.1, §3.5 |
| `AC-02` | `NFR-080`'s unsatisfiability is stated, and a satisfiable restatement is specified and testable | §3.2, `UX-001-D-01`, §11 |
| `AC-03` | Every colour token carries a measured contrast ratio and the background it was measured against | §5.4, `TKN-11` |
| `AC-04` | Bengali is expressed as tokens, not as a note | §5.5.1, `TKN-10`, `UX-001-D-03` |
| `AC-05` | The component inventory is **counted**, complete, and each entry names its states and copy contract | §8.1–§8.7 — 68 components |
| `AC-06` | Every WCAG 2.2 AA criterion that is satisfiable at token level has a token that satisfies it and a check that proves it | §5.6, §5.9, §11 |
| `AC-07` | The build pipeline, artefacts and version policy are specified to the level a vendor can implement | §9 |
| `AC-08` | Every rule is enforced by a named check, or is explicitly listed as unenforceable | §11, §11.1 |

**Definition of done.** Complete when every criterion is met, `Q-01` has an appointed reviewer,
`PGD-000`'s `UX-001` row is updated with a fresh enumeration timestamp, and the Design Authority
has approved `UX-001-D-01`.

---

# 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `RQ-006` §4.4 | `NFR-073`, `NFR-077`, `NFR-080`, `NFR-081` — the requirements this realises |
| Upstream | `AR-001` §6, §8 · `AR-002` AP-04 | The surface set and the one-design-system principle |
| Upstream | `VB-003`, `VB-006`, `VB-007`, `VB-008`, `VB-009` | The five content standards this compiles |
| Downstream | **`UX-002`** | Navigation components `C-49`…`C-60` realise the navigation model |
| Downstream | **`UX-003`** | Screen classification depends on the component and pattern set |
| Downstream | **`UX-004`** | Motion and interaction behaviour consume §5.8 tokens |
| Downstream | **`UX-005`** | Token-level conformance is the floor the screen-level design builds on |
| Downstream | **`UX-006`** | `C-62`, `C-63`, `C-67` are the offline components |
| Downstream | **`UX-007`** | `.bn` tokens and container rules are applied to layouts |
| Downstream | `BE-004` | Repository structure hosts the six artefacts |
| Downstream | `QA-008` | Accessibility test derives from §11 |
| Lateral | `AR-012` `FF-35` | Extended by `CFM-01`…`CFM-12` |
| Lateral | `../../project_content/03_UI_Copy_and_Microcopy/` | 42 copy packs bind to component slots |
| Lateral | `../../1000fix_ERP_Module/04_Portals_and_Applications/04-00` | `PS-04`…`PS-08` |

---

# 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./UX-002` … `./UX-008` · `../01_Requirements_Engineering/RQ-006` ·
`../02_Architecture_and_Design/AR-001`, `AR-002`, `AR-010`, `AR-012` ·
`../00_Programme_Governance_and_Control/GV-002`, `GV-003`, `GV-007`, `GV-009`

**Workspace**
`../../1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md` ·
`../../project_content/01_Voice_Brand_and_Design_Content/VB-003`, `VB-006`, `VB-007`, `VB-008`, `VB-009` ·
`../../project_content/03_UI_Copy_and_Microcopy/` (42 packs) ·
`../../project_content/11_Localisation_Bengali/BN-005`, `BN-006`, `BN-007` ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §11

**External standards and sources**

| Source | Verified |
|---|---|
| W3C Design Tokens Community Group — *Design Tokens Format Module 2025.10* (first stable version, announced 2025-10-28). Not a W3C Standard; not on the W3C Standards Track | 2026-08-18 |
| W3C — *Web Content Accessibility Guidelines (WCAG) 2.2*, W3C Recommendation | 2026-08-18 |
| ISO 9241-112:2017 — Ergonomics of human-system interaction — Principles for the presentation of information | 2026-08-18 |
| ISO/IEC 25010:2023 — SQuaRE — Product quality model (interaction capability) | 2026-08-18 |
| Semantic Versioning 2.0.0 | 2026-08-18 |
| Material Design 3 — referenced as the Flutter substrate only; not adopted as a colour model | 2026-08-18 |
| ISO 9241-125:2017 and ISO 9241-143:2012 — reviewed as design references, **not cited as conformance bases** (§2.1) | 2026-08-18 |

---

# 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Design System Lead | Initial issue. Rules `NFR-080` unsatisfiable as written and specifies the satisfiable form (`UX-001-D-01`). Publishes a three-tier DTCG token architecture with measured contrast on every colour token, a Bengali token family with its own floors, and a **counted inventory of 68 components** in six tiers. Defines twelve conformance checks `CFM-01`…`CFM-12` that make the system binding | *(pending — no constituted body, `PGD-A1-09`)* |

---

*`UX-001` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
