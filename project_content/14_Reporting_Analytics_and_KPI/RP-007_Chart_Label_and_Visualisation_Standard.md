---
id: RP-007
title: Chart, Label and Visualisation Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: BI Lead with Design System
author: BI Lead with Design System owner, Content Design and Localisation
reviewers: [CTO delegate, Design System owner, Content Design Lead, Localisation Lead, Accessibility reviewer, Operations Director, CFO delegate]
approver: Design System owner with BI Lead
content_class: D
purpose: >
  How a number is drawn: which chart type answers which question, how axes and units are labelled, how
  status is encoded without relying on colour, how Bengali labels and lakh-crore grouping behave, and
  what a chart must never do. Fifteen consoles, seven executive views, eleven external views and a
  51-branch league table will be built by different teams in two different tools; inconsistent visual
  encoding across them does not merely look untidy, it causes managers to misread the same shape as
  two different things.
traces_to: [VB-008, VB-007, VB-009, VB-006, P06, 04-00 P06, 05-06 §9, 05-06 §10, 05-06 NFR-073, PS-04, PS-05, CG-011, RP-001, RP-003, RP-004, RP-005, RP-011, RP-014, UI-010, UI-016, BN-003, TS-016, MD-039, MD-041]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: RP-007_Chart_Label_and_Visualisation_Standard_BN.md
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md §3.1 — the eight semantic tokens status-neutral, status-progress, status-success, status-warning, status-error, status-info, status-hold, status-inactive, each with text/border hex, contrast ratio on white, fill tint and text-on-tint ratio; §3.3 dark theme
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-17 — "Status and performance are encoded independently of colour alone (PS-04)"; PRU-P06-05 Grafana defines no business metric; PRU-P06-06 every view states its data freshness
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §9 Localisation Standards — Bangladeshi lakh/crore grouping (12,34,567) in the Bengali locale and international grouping in the English locale; BDT two decimal places; DD/MM/YYYY with Bengali month names; July–June fiscal year; ICU bn-BD collation; NFR-073 WCAG 2.1 AA on all web portals; §10 minimum desktop resolution 1366×768
    verified: 2026-08-20
    class: P1
  - source: WCAG 2.1 Success Criterion 1.4.11 Non-text Contrast (Level AA) — the visual presentation of user interface components and graphical objects requires a contrast ratio of at least 3:1 against adjacent colours; this includes lines in line graphs and slices in pie charts, and different data series must have sufficient luminance contrast where colour is the primary differentiator. https://dequeuniversity.com/resources/wcag2.1/1.4.11-non-text-contrast and https://www.pearson.com/accessibility-guidelines/perceivable-principle/non-text-contrast.html
    verified: 2026-08-20
    class: P2
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md — Bengali labels commonly run 20–40% longer than English; icon-plus-label layouts break if not specified
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Chart, Label and Visualisation Standard

| Item | Value |
|---|---|
| Governs | Every chart on `P06`, `P03`, `P04`, `P07`, `P08`, `P12` and in every `RP-002` report |
| Colour source | **`VB-008`'s eight semantic tokens** — no new palette |
| Accessibility | WCAG 2.1 AA; **`1.4.11` non-text contrast ≥ 3:1** |
| Number format | `05-06` §9 — lakh/crore in Bengali locale, international in English |
| Tools | Metabase and Grafana (`PRU-P06-05`) |
| Wave | W4 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the chart-type selection matrix in §4.2. All six sections retained in
> order.

---

## 1. Purpose

The register states the consequence: *"inconsistent visual encoding across 51 branch league tables and
a dozen dashboards produces misreading at management level."* Misreading, not ugliness. Three specific
mechanisms:

| Mechanism | Example |
|---|---|
| **The same shape means two things** | A bar chart where longer is better on one console and longer is worse on the next. A manager scanning six panels reads the shape, not the axis |
| **Colour carries meaning colour cannot carry** | Red for "below target" on one view and for "high volume" on another. `PRU-P06-17` and `PS-04` both forbid colour-only encoding, and roughly one in twelve men has a colour-vision deficiency |
| **Number format changes the magnitude read** | `1,234,567` and `12,34,567` are the same value. A Bangladeshi manager reading the first misreads the magnitude, and a chart axis is where it happens most |

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Chart-type rules | A pie chart with fourteen revenue streams, and a trend shown as a bar comparison |
| An axis and unit standard | A percentage axis starting at 60% to make a difference look large — the commonest honest-intent distortion in management reporting |
| Bengali label rules | `VB-007` gives Bengali 20–40% expansion; unspecified axis labels truncate or overlap at 1366×768 |
| Status encoding rules | `PRU-P06-17` is unimplementable, and `TS-016` `ACC-<P>-03` fails on every dashboard |
| A "never" list | Every chart type the tool offers gets used somewhere |

---

## 2. Scope

**In scope.** Chart-type selection; axis, scale and unit rules; number, date and currency formatting;
the colour contract bound to `VB-008`; status and performance encoding without colour; Bengali label
handling; accessibility; density at 1366×768; the sparkline and stat-tile rules; and the prohibitions.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The eight semantic colour tokens and their hex values | **`VB-008`** — this file binds charts to them and defines nothing new |
| Bengali typeface, size, line height, numeral policy | **`VB-009`** |
| Icon-and-label pairing and expansion allowance | **`VB-007`** |
| Component copy contracts | `VB-006` |
| Which metric appears on which view | `RP-003`, `RP-004`, `RP-005` |
| Metric definitions and units of measure | `RP-001` |
| League scoring and its presentation rules | `RP-011` — this file governs how its chart is drawn |
| Accessibility test procedures | **`TS-016`** — this file states the rule; `TS-016` proves it |
| Alt text and accessible names | `UI-010`, `CG-011` |
| Export marking on a rendered chart | `RP-014` |
| Rounding and currency arithmetic | `MD-039` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **BI analysts and engineers** | Building every chart in Metabase and Grafana |
| **Design System owner** (approver) | Consistency with `VB-006`, `VB-007`, `VB-008` |
| **Localisation** | Bengali axis, label and number behaviour |
| **Accessibility reviewer** | The rules `TS-016` verifies |
| **Report and dashboard authors** | Chart selection before building |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **CH-01** | **The question chooses the chart** (§4.2). A chart type chosen because the tool defaults to it is a defect |
| **CH-02** | **If a single number answers the question, show the number.** A stat tile beats a chart, and a count that links to its list beats a stat tile (`RP-004` `OC-08`) |
| **CH-03** | **Every axis is labelled with its unit.** An unlabelled axis is a defect regardless of how obvious the unit seems |
| **CH-04** | **A quantitative axis starts at zero.** Where a truncated axis is genuinely necessary — a percentage clustered at 95–100% — the truncation is **visibly marked** and stated in the caption |
| **CH-05** | **Direction is stated, not implied**: every metric carries `direction` from `RP-001`, and where higher is worse the chart says so in words |
| **CH-06** | **Status and performance are encoded by at least two channels** — colour **plus** label, position, shape or pattern (`PRU-P06-17`, `PS-04`, WCAG `1.4.1`) |
| **CH-07** | **Colour comes only from `VB-008`'s eight semantic tokens.** No new palette, no tool default palette (§4.4) |
| **CH-08** | **Adjacent series and graphical objects meet ≥ 3:1 contrast** (WCAG `1.4.11`); text meets ≥ 4.5:1 (`1.4.3`) |
| **CH-09** | **Categorical series are distinguishable without colour** — direct labelling first, then pattern or marker shape (§4.4) |
| **CH-10** | **Number formatting follows the locale**: `12,34,567` in Bengali, `1,234,567` in English, same value (`05-06` §9) |
| **CH-11** | **Currency is `BDT` with two decimals**, and an axis in lakh or crore **says which** (§4.5) |
| **CH-12** | **Dates are `DD/MM/YYYY`**, with Bengali month names in the Bengali locale; fiscal periods are labelled as fiscal (July–June) so `FY26 Q1` is never read as a calendar quarter |
| **CH-13** | **Every chart carries a comparator** — prior period, target or baseline (`RP-003` `XD-12`) — or states that it has none |
| **CH-14** | **Every chart states its freshness** (`PRU-P06-06`) and is flagged when stale |
| **CH-15** | **A cell or point below the `RP-005` `ED-06` five-record floor reads *"too few to report"***, never zero and never blank |
| **CH-16** | **A `Provisional` metric or dataset is visibly labelled on the chart** (`BRU-DAT-05`, `KD-22`) |
| **CH-17** | **Bengali labels are laid out with `VB-007`'s 20–40% expansion allowance**, verified at 1366×768 and at 320 px (`PS-05`) |
| **CH-18** | **Every chart has a text alternative** conveying its message, not its construction (`UI-010`, `CG-011`, WCAG `1.1.1`) |
| **CH-19** | **Every chart is decomposable** — clicking through reaches its records (`PRU-P06-08`) |
| **CH-20** | **Grafana carries no business metric** (`PRU-P06-05`); it draws counts, countdowns and time series on the real-time board only |

### 4.2 Chart-type selection

| The question | Chart | Never |
|---|---|---|
| *What is the value now?* | **Stat tile** with comparator | A gauge — it spends a quarter of the panel on decoration |
| *How has it moved over time?* | **Line**, time on the horizontal axis | Bar for a continuous series; area for more than two series |
| *How do categories compare?* | **Horizontal bar**, sorted by value | Pie; radar; 3-D anything |
| *How do 51 branches compare?* | **Sorted horizontal bar** or a ranked table (`RP-011`) | A map as the primary view — geography is not the question |
| *What is the composition?* | **Stacked bar**, four segments maximum | Pie or donut — see §4.3 |
| *Where in a funnel is it lost?* | **Funnel or stepped bar** with counts **and** conversion at each step | A funnel showing only percentages |
| *How is it distributed?* | **Histogram** or box plot | A mean with no distribution |
| *Is there a relationship?* | **Scatter** with the axes labelled and the direction stated | A trend line without the points |
| *What is the ageing profile?* | **Stacked bar by age band**, oldest at the top | A mean age |
| *What is happening right now?* | **Count with a countdown**, Grafana (`CH-20`) | A trend on a real-time board |
| *Where is it geographically?* | **Choropleth by `MD-006` division**, as a secondary view | Upazila-level shading — `RP-005` `ED-06` re-identification |

### 4.3 Prohibitions, with reasons

| Prohibited | Why |
|---|---|
| **Pie and donut charts with more than three segments** | Angle comparison is unreliable beyond three. The fourteen revenue streams on `RP-003` `E1` slot 3 are a **sorted bar**, and this is the rule that decision rests on |
| **3-D charts of any kind** | Perspective distorts magnitude |
| **Dual axes** | Two scales on one plot invite a correlation the data does not support. Two stacked charts sharing a time axis instead |
| **Truncated quantitative axis without a visible mark** | `CH-04`; the commonest honest-intent distortion |
| **Colour as the only encoding** | `PRU-P06-17`, `PS-04`, WCAG `1.4.1` |
| **A tool's default categorical palette** | Not contrast-checked, not `VB-008`, and inconsistent between Metabase and Grafana |
| **Rainbow or red-amber-green for a continuous scale** | Implies thresholds that do not exist; and red-green is the commonest deficiency pair |
| **A gauge or speedometer** | A stat tile with a comparator carries the same information in a fifth of the space at 1366×768 |
| **More than four segments in a stack** | The fifth segment is unreadable at console density |
| **Animation or transition on a data change** | On an operational console it hides the change it is meant to draw attention to |
| **A chart with no comparator and no statement that it has none** | `CH-13` |
| **A word cloud** | Encodes frequency by area, which is unreadable, and it will be proposed for `MD-024` fault codes |

### 4.4 The colour contract

**No palette is defined here.** `VB-008` §3.1 holds the eight semantic tokens with their contrast
ratios, and this file binds chart usage to them.

| Chart usage | Token | Notes |
|---|---|---|
| On target / passed / complete | `status-success` | Text/border `#146C43` at 6.45:1 on white |
| At risk / approaching threshold | `status-warning` | `#8A6100` at 5.54:1 — **not amber-on-white from a tool default** |
| Breached / failed / blocked | `status-error` | `#B02A37` at 6.50:1 |
| In progress / on track | `status-progress` | `#1E5F8A` |
| Waiting on another party | `status-info` | `#0F6674` |
| Deliberately paused | `status-hold` | `#59359A` — distinct from failure, and the distinction matters on an SLA chart with holds |
| Archived / cancelled / superseded | `status-inactive` | `#6C757D` |
| Neutral / informational series | `status-neutral` | `#495057` |

**Categorical series are the gap `VB-008` does not fill**, because eight *semantic* tokens are not a
categorical palette — using `status-error` for "Chittagong" would imply Chittagong is failing.

| # | Rule for categorical series |
|---|---|
| **CH-21** | **Direct labelling first.** A labelled line or bar needs no colour key, and removes the legend-matching task entirely |
| **CH-22** | Where colour is needed for categories, use **`status-neutral`, `status-progress`, `status-info`, `status-hold`** — the four non-judgemental tokens — in that order, **maximum four series** |
| **CH-23** | **Beyond four categories, do not colour: sort and label.** A sorted bar of 51 branches in one neutral token is more readable than 51 colours |
| **CH-24** | Adjacent categorical series carry **≥ 3:1 luminance contrast** with each other (WCAG `1.4.11`), and are additionally distinguished by **marker shape or pattern** (`CH-09`) |
| **CH-25** | **Semantic tokens are never used categorically**, and categorical tokens are never used to imply status |

**Dark theme** follows `VB-008` §3.3; no chart defines its own dark values.

### 4.5 Numbers, units and axes

| Element | Rule |
|---|---|
| **Grouping** | `12,34,567` in the Bengali locale; `1,234,567` in English (`05-06` §9). **The same chart in two locales shows two groupings of one value** |
| **Large values** | An axis in lakh or crore is **labelled "BDT lakh" or "BDT crore"**. `06-02` §3.1 states the benefit model in BDT lac, so a board chart mixing lac and crore is a real misreading risk |
| **Currency** | `BDT` two decimals on detail; whole units on an axis, with the unit stated (`CH-11`, `MD-039`) |
| **Percentages** | One decimal maximum; zero-based axis unless `CH-04`'s marked exception applies |
| **Counts** | Integers, never rounded to "k" on an operational console where the exact count is the action |
| **Durations** | Stated unit — hours, working days (`ds_calendar_dim`), or minutes — never a bare number |
| **Dates** | `DD/MM/YYYY`; Bengali month names in the Bengali locale (`CH-12`) |
| **Fiscal periods** | Labelled as fiscal, July–June (`MD-041`). `FY26 Q1` is July–September |
| **Null** | Shown as a gap, **never as zero** (`RP-001` `KD-10`) |
| **Below the floor** | *"too few to report"* (`CH-15`) |

### 4.6 Bengali labels

| # | Rule |
|---|---|
| **CH-26** | Bengali chart labels are **authored**, not machine-translated (`CG-010`); metric names come from `RP-001` `name_bn` |
| **CH-27** | Layout carries **`VB-007`'s 20–40% expansion**; a Bengali axis label that fits only in English is a defect against this file, not against the translation |
| **CH-28** | **Bengali axis labels are never rotated to fit.** Rotated Bengali with conjuncts and vowel signs is materially harder to read than rotated Latin; the chart becomes horizontal-bar instead (`CH-23` already prefers it) |
| **CH-29** | Numerals follow **`VB-009`'s numeral policy**; a chart mixes Bengali and Arabic digits nowhere |
| **CH-30** | Categorical **sort order in Bengali uses ICU `bn-BD` collation** (`05-06` §9), so a sorted branch list is in Bengali alphabetical order and not in Latin transliteration order |
| **CH-31** | Bengali rendering is verified at **1366×768 and 320 px** on the `TS-002` `B-04` longest-expansion set (`TS-016` `ACC-<P>-06`) |

> **`CH-30` is the rule most likely to be missed.** A branch list sorted correctly in English will
> appear randomly ordered to a Bengali reader if the sort ran on transliterated values, and it will
> look like a data defect rather than a collation defect. `TS-002` `B-08` supplies the answer key.

### 4.7 Accessibility

| Requirement | Rule | Verified |
|---|---|---|
| Non-text contrast ≥ 3:1 for series, lines, slices, borders | `CH-08`, `CH-24` — WCAG `1.4.11` | `TS-016` `ACC-<P>-02` |
| Text contrast ≥ 4.5:1 | `VB-008` ratios | `TS-016` `ACC-<P>-02` |
| Not colour alone | `CH-06`, `CH-09` — WCAG `1.4.1` | `TS-016` `ACC-<P>-03` |
| Text alternative conveying the message | `CH-18` — WCAG `1.1.1` | `TS-016` `ACC-<P>-01` |
| Keyboard access to chart data | Data table alternative reachable by keyboard | `TS-016` `ACC-<P>-07` |
| Reflow at 320 px, no horizontal scroll | `CH-17`, `PS-05` | `TS-016` `ACC-<P>-04` |
| Announced by a screen reader in both languages | Chart title, message and data table | `TS-016` `ACC-<P>-19`/`-20` |

**Every chart has a data-table alternative.** It satisfies `CH-18` and `CH-19` at once, and it is the
only reliable way an assisted user reads a chart — which is why `TS-016`'s `AX-04` task completion is
achievable on `P06` at all.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **[`VB-008`](../01_Voice_Brand_and_Design_Content/VB-008_Status_Colour_and_Label_Semantics_Register.md)** | The eight semantic tokens and their contrast ratios — this file defines no colour |
| **[`VB-007`](../01_Voice_Brand_and_Design_Content/VB-007_Iconography_and_Label_Pairing_Register.md)**, **`VB-009`** | Expansion allowance; Bengali typography and numeral policy |
| `VB-006` | Component copy contracts |
| **[`RP-001`](RP-001_KPI_Dictionary_and_Metric_Definition_Standard.md)** | `unit`, `direction` and `name_bn` for every metric charted |
| [`RP-003`](RP-003_Dashboard_Specification_Pack_Executive.md), `RP-004`, `RP-005`, `RP-011` | The views this standard is applied to |
| `05-06` §9, §10 | Locale formatting and the 1366×768 target |
| [`CG-011`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md), `UI-010` | Accessibility standard and alt-text library |
| **[`TS-016`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md)** | Where every rule here is verified |
| `MD-039`, `MD-041` | Rounding, currency, fiscal calendar |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per portal release; with `VB-008` on any token change |
| Trigger for out-of-cycle review | A `VB-008` token change; a new chart type request; a WCAG version change; a tool change; a Bengali rendering defect found in `TS-016` |
| Owner | BI Lead with the Design System owner, who approves |
| Data file | `RP-007_Chart_Type_Matrix.csv` · `RP-007_Categorical_Token_Order.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **This file is W4 and `RP-004` is W1.** `OC-12` requires `RP-007` status encoding on all fifteen consoles at `P03` go-live. **`P03` ships three waves before the standard that governs how its panels are drawn**, so either a W1 subset covering stat tiles, sorted bars, status encoding and number formatting is issued, or the consoles are re-worked at W4 | Programme Content Lead with BI Lead | **W1 — subset needed** |
| **O-02** | **`VB-008` provides eight semantic tokens and no categorical palette.** §4.4 works around it with direct labelling, four non-judgemental tokens and sort-don't-colour — **which is a genuine constraint, not a preference.** Whether the Design System adds a contrast-checked categorical set is a `VB-008` decision this file cannot take | Design System owner | **W4** |
| **O-03** | **No accessibility reviewer is named, and none has been for four consecutive categories.** `CH-06`, `CH-08`, `CH-18` and the whole of §4.7 need one, and `TS-016` `O-02` records the fourth request; `AUDIT-010` R-09 escalated it under check `G1`. **This is now the fifth request** | Content Design Lead | **W1 — escalated** |
| **O-04** | **`CH-30` ICU `bn-BD` collation on chart sort order has no verification.** `TS-002` `B-08` supplies a 60-item answer key and `TS-016` covers screen-reader rendering, but **no test sorts a Bengali categorical axis and compares it to the key**. A misordered 51-branch list will be reported as a data defect | BI Lead with QA Lead | **W4** |
| **O-05** | **Metabase and Grafana enforce none of this.** Both ship default palettes, default chart types and a truncated-axis option, and `CH-07`, `CH-20` and `CH-04` are conventions until a theme, a template set and a review gate exist. `AUT-P06-08` rejects a dashboard with an inline calculation at review; **nothing rejects a pie chart with fourteen slices** | BI Lead with Platform Engineering | **W4 — a review gate is needed** |
| **O-06** | **No Bengali chart labels exist**, and `CH-26` requires them authored. `RP-001` `O-05` records the metric-name half; axis labels, units and the *"too few to report"* string are this file's. Bengali authoring is unresourced across the programme | Localisation Lead | **W1 with `RP-004`** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the chart-selection matrix
- [x] **Three misreading mechanisms named, so the standard is justified by consequence rather than consistency**
- [x] Thirty-one rules stated across selection, axes, colour, numbers, Bengali and accessibility
- [x] Chart-type selection driven by the question, with an explicit "never" for each
- [x] **Twelve prohibitions each carrying its reason, including the fourteen-slice pie that `RP-003` `E1` depends on avoiding**
- [x] **Colour bound to `VB-008`'s eight tokens with no new palette defined (`CP-01`)**
- [x] The categorical-palette gap identified as a real constraint, with a labelling-first workaround and a `VB-008` decision requested
- [x] Number, currency, percentage, duration, date and fiscal-period rules tied to `05-06` §9 and `MD-041`
- [x] Bengali rules including no-rotated-labels and ICU `bn-BD` sort order, with the collation trap called out
- [x] WCAG `1.4.11` 3:1 non-text contrast sourced externally with a verification date
- [x] Every accessibility rule mapped to the `TS-016` script that verifies it
- [x] Data-table alternative required on every chart, satisfying alt-text and decomposability together
- [x] All internal links resolve
- [x] Six open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` W1 consoles against a W4 standard — outstanding**
- [ ] **`O-05` neither tool enforces any of this — outstanding; a review gate is needed**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding (`O-06`)**
- [ ] Named approvers recorded — **pending Design System owner and BI Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
