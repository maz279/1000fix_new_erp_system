---
id: UX-007
title: Bilingual & Bengali Interface Design Standard
category: 06 — Experience & Interface Design
code: UX
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Product Design
approver: Design Authority (constituted under GV-002), with Localisation Lead concurrence
standards_basis: >
  The Unicode Standard 17.0 (9 September 2025), Bengali block U+0980–U+09FF ·
  UAX #14 (line breaking) · UAX #29 (text segmentation) · UAX #15 (normalisation) ·
  Unicode CLDR (bn-BD) · IETF BCP 47 · ICU MessageFormat ·
  WCAG 2.2 SC 1.4.4, 1.4.10, 1.4.12, 3.1.1, 3.1.2
traces_to: >
  PGD-000 UX-007 · L-07, UI-R2, UI-R3, SWR-003 (RQ-001) · NFR-074 · CON-05 ·
  VB-009, BN-005, BN-006, BN-007, CG-010 · UX-001 §5.5 (.bn token family) ·
  AR-007 V-08 · AR-001 §10 (text expansion)
depends_on: UX-001 (token families) · UX-003 (screens carrying bengali_risk) · VB-009 · BN-006 · BN-007
verified_on: 2026-08-18
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-18 14:45 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# UX-007 — Bilingual & Bengali Interface Design Standard

### Category 06 · Code `UX` · Unicode 17.0 · UAX #14 · CLDR · WCAG 2.2 AA

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** Row `UX-007` exists in `PGD-000` Category 06.
> 2. **`PG-03` Count, do not consult.** Counted at **2026-08-18 14:45 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** Unicode version and status verified 2026-08-18; see §17.

---

## 1. Purpose

> **Bengali string expansion is a layout problem, not a translation problem.**

`VB-009` and `BN-006` set Bengali **typography** standards. `BN-005` sets i18n **key** rules.
`BN-003` fixes **terminology**. `BN-009`…`BN-013` hold the **strings**. Every one of these is a
content or linguistic artefact, and every one of them is correct.

**None of them tells a designer how wide to make the container.**

`RQ-001` `L-07` states the consequence directly: *"Bengali strings run 15–30% longer than English —
**any requirement specifying a fixed layout is not implementable**."* `AR-007` `V-08` makes it a
build check. `VB-007` `BL-03` states the disposition: *"A label that fits in English and truncates
in Bengali is a **layout defect**, not a translation problem. Do not shorten the Bengali to fit."*

This document is the layout standard those three statements presuppose: how much room to leave, how
to measure it, when to reflow rather than truncate, what the language switch does to state, and how
a build proves a layout survives Bengali before a human ever sees it.

It unblocks every screen design (`UX-003` — ~90 screens carry `bengali_risk: high`), the `CFM-07`
Bengali-fit conformance check, and the `BN-009`…`BN-013` string bundles, which are currently written
against containers that do not exist.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The default-language matrix per surface, and what "default" means operationally |
| 2 | **Measured expansion** — by character count and by rendered width, which differ, and the derivation behind the estate's +40% |
| 3 | Container sizing rules, per component class |
| 4 | Reflow, wrapping and the truncation policy |
| 5 | Vertical rhythm: line box, row height, and the density consequence |
| 6 | Mixed-script layout and `lang` marking |
| 7 | Numerals in layout, and the ruling on where the decision actually lives |
| 8 | The language-switch interaction and its state contract |
| 9 | **Pseudo-localisation** and the build-time proof |
| 10 | Font loading, bundling and payload budget |
| 11 | Device-level rendering verification |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Bengali typeface stack, size floors, line-height ratios | `VB-009` | Typography. This document applies them to layout |
| Script rendering, normalisation, conjunct behaviour | `BN-006` | Script mechanics |
| Date, number, currency and address **formats** | `BN-007` | Formats, not layout |
| i18n key structure, placeholders, plurals | `BN-005`, `UI-001` | String architecture |
| Terminology and translation quality | `BN-002`, `BN-003`, `BN-018` | Linguistic |
| Which language a legal document governs in | `CG-010` §4.1 | Legal |
| Bengali voice and IVR | `BN-017` | Not an interface layout |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| Designers | Container sizing, reflow and truncation rules; the Bengali-first method |
| Front-end and mobile engineers | The `CFM-07` contract and the pseudo-localisation build step |
| Localisation Lead | The layout tolerances the string bundles are written against |
| QA | Bengali-fit assertions and the device verification matrix |
| Content designers | Why a character budget is stated in Bengali characters |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Status | How this document uses it | Departure |
|---|---|---|---|
| **The Unicode Standard 17.0** (released 9 September 2025) | Current | Bengali block **U+0980–U+09FF**; the character repertoire layouts must render | None. Unicode 17.1 is scheduled for September 2026 and is an `RR-005` review item |
| **UAX #14** — Unicode Line Breaking Algorithm | Current | §5.3 wrapping rules; Bengali breaks at word boundaries and never inside a conjunct cluster | None |
| **UAX #29** — Text Segmentation | Current | Grapheme-cluster boundaries govern truncation and cursor movement. **A Bengali grapheme cluster is not a code point** | None |
| **UAX #15** — Normalisation | Current | NFC on write, per `BN-006` §3 | This document consumes the rule; `BN-006` owns it |
| **Unicode CLDR**, locale `bn-BD` | Current | Baseline locale data, with the overrides `BN-007` §2 declares — notably the numbering system | `latn` overrides the CLDR `beng` default (`BN-007` `NM-A`) |
| **IETF BCP 47** | Current | `bn-BD` / `en-BD` tags; `lang` on every script change | None |
| **ICU MessageFormat** | Current | Mandatory per `BN-005` §3.1; layout implications in §5.5 | This document consumes it |
| **WCAG 2.2 AA** | Recommendation | SC 1.4.4 resize, 1.4.10 reflow, **1.4.12 text spacing**, 3.1.1 / 3.1.2 language | None. 1.4.12 is called out because **Bengali layouts commonly fail it** (`VB-009` LH-06) |

### 2.2 Source material relied on

| Source | What it establishes |
|---|---|
| `VB-009` §2–§6 | Typeface stack and ranks; **Bengali size floors**; line heights per context; numeral policy (deferred to `BN-007`); mixed-script rules |
| `BN-006` §2–§9 | Why Bengali is a different rendering problem; normalisation; the ra-ya-phala case; line breaking; input methods; the rendering test set; shaping engines in scope |
| `BN-007` §2, §3 | The locale baseline, the overrides, and **the numeral decision `NM-A`…`NM-E`** |
| `BN-005` | ICU MessageFormat, placeholders, plural categories |
| `VB-007` §7 | **Measured** English→Bengali label expansion, and the layout patterns by available width |
| `VB-006` §8 | Character budgets, stated in Bengali characters (`DS-04`) |
| `UX-001` §5.5, `LAY-03` | The `.bn` token family and the Bengali row-height consequence |
| `CG-010` | Bilingual content policy and its open-decisions list |

### 2.3 Findings this document addresses

| Finding | Source | How addressed |
|---|---|---|
| `L-07`, `UI-R3` | `RQ-001` | Converts "layouts shall accommodate up to 30% expansion" into a measurable, buildable container rule (§4) |
| `AR-007` `V-08` | `AR-007` | Supplies the definition `V-08` asserts against |
| `RQ-006` §4.4 note | `RQ-006` | *"inclusivity for users whose first written language is Bengali is `UX-005`'s and `UX-007`'s to specify"* — §3 and §9 |
| `UX-001` `Q-05` | `UX-001` | **Answered: `BN-007` §3.1 decided it.** §6 |
| **New — `UXA-15`** | This category | `BN-007` §3 states *"This closes `CG-010` §12 item 3 and `VB-009` `NU-03`"* — and **`CG-010` §12 still lists item 3 as open**. A closed decision left open in the register that governs it. §6.1 |
| **New — `UXA-16`** | This category | **The rendered-width allowance exists (`VB-007` `BL-02`, +40%) and has never been derived or measured.** `BN-006` `LB-11` defines the measurement method, `MM-004` `IC-23` records that it is *"replaced by measurement"* — and **no measurement harness has ever been built**, across five files that depend on the figure. §4.2 supplies the derivation; §4.3 the harness |
| **New — `UXA-17`** | This category | **Bengali is the default on the highest-volume surfaces, and every `UI-*` pack's example layout is written English-first.** §3.2 rules Bengali-first layout for the eight Bengali-default surfaces |

---

# 3. The Bilingual Model

## 3.1 The default-language matrix

"Bilingual" is not one behaviour. Each surface has a **default**, and the default determines which
language the layout is designed against.

| Surface | Default | Toggle | Basis |
|---|---|---|---|
| `P01` web + app | **Bengali** | English | `PS-03`; individual customers |
| `P02` Technician | **Bengali** | English | `04-00` §P02 non-negotiable #3 — *"Bengali UI, complete, including error messages"* |
| `P03` Admin operations | **Mixed — per workspace** | both | Branch and intake roles work in Bengali; finance, HR and system administration in English. §3.3 |
| `P04` Corporate B2B | **English** | Bengali | `CG-010` §12 item 4 — **open** (`Q-02`) |
| `P05` Vendor & supplier | **Bengali** | English | Local vendors and couriers |
| `P06` Analytics | **English** | Bengali | Management audience; chart labels are dense |
| `P07` Marketplace seller | **Bengali** | English | Local engineers and shops |
| `P08` Brand partner | **English** | Bengali | International brand partners |
| `P09` Rider | **Bengali** | — | **No toggle.** `NVR-33` — three tabs, minimum chrome |
| `P10` Contact centre | **Bengali** | English | Agents speak Bengali to customers |
| `P11` Field auditor | **Bengali** | English | |
| `P12` Partner & referral | **Bengali** | English | |

**Counted: eight surfaces default to Bengali, four to English, one mixed.**

## 3.2 Bengali-first layout — `UXA-17`

> **`LNG-01`.** **For the eight Bengali-default surfaces, the layout is designed in Bengali and
> verified in English — not the reverse.**

Every `UI-*` copy pack writes English in the left column and Bengali in the right. Every example
layout in the estate is English-first. Designing in English and "checking Bengali later" produces a
container sized to the shorter string, and the check then finds a defect that is expensive to fix
because the whole grid was derived from it.

| # | Rule |
|---|---|
| `LNG-02` | Bengali-default surfaces: the **first** artefact is the Bengali layout. English is a variant of it |
| `LNG-03` | English-default surfaces (`P04`, `P06`, `P08`) still size containers to the Bengali rendering, because the toggle exists and Bengali must not break the layout when used |
| `LNG-04` | A design review of a Bengali-default screen that is presented in English is **not a review**. The artefact is returned |

## 3.3 `P03` — the mixed-language workspace

`P03` is the only surface where two languages coexist by role rather than by preference.

| Workspace | Working language | Note |
|---|---|---|
| Service intake, Dispatch, Branch, Workshop | **Bengali** | Customer-facing and floor roles |
| Inventory, Procurement, Quality, Warranty, Marketplace, Managed services | Mixed | Bengali floor terms, English system terms |
| Finance, HR, System | **English** | Statutory forms, payroll and configuration are English-anchored |

| # | Rule |
|---|---|
| `LNG-05` | Language is a **user** setting, not a workspace setting. A branch manager who prefers English gets English in the Branch Console |
| `LNG-06` | **Every `P03` workspace is sized to Bengali regardless of its typical working language.** The user setting can change; the grid cannot |
| `LNG-07` | Statutory content — Mushak forms, BEFTN files, filings — is never translated for layout convenience (`BN-004`) |

---

# 4. Expansion — measured

## 4.1 By character count

Carried from `VB-007` §7.1, which measured it:

| English label | Chars | Bengali | Chars | Expansion |
|---|---:|---|---:|---:|
| Search | 6 | অনুসন্ধান | 9 | **+50%** |
| Approve | 7 | অনুমোদন | 7 | 0% |
| Service order | 13 | সার্ভিস অর্ডার | 14 | +8% |
| Customer | 8 | গ্রাহক | 6 | **−25%** |
| Technician | 10 | টেকনিশিয়ান | 11 | +10% |
| Cancel order | 12 | অর্ডার বাতিল করুন | 18 | **+50%** |
| Download report | 15 | রিপোর্ট ডাউনলোড করুন | 21 | **+40%** |

**The spread is −25% to +50%, not a uniform 15–30%.** The mean is close to the estate's stated
range; the **maximum** is what breaks a layout, and it is +50%.

## 4.2 By rendered width — `UXA-16`

`VB-007` §7.1 states the problem correctly:

> *"Character count understates the problem. Bengali conjuncts and matras occupy more rendered
> width per character than Latin at the same point size, and Bengali needs a larger minimum size
> (`VB-009`). The practical allowance is on **rendered width**, not character count."*

**And it supplies the figure.** `VB-007` `BL-02`: *"Plan for **+40% rendered width** over English as
the working assumption. Measure the actual string before shipping."* `BN-006` `LB-11` defines the
measurement; `MM-004` `IC-23` carries the figure into icon production and records that it is
*"replaced by measurement"*; `UI-001` §8 and `BN-009` §11 both state budgets as Bengali rendered widths. **Five files depend on +40%.**

> **`UXA-16` — what is actually missing.** The figure has **no stated derivation**, and the
> measurement `BL-02`, `LB-11` and `IC-23` all defer to **has never been built**. A working
> assumption that survives four documents without either derivation or measurement stops being an
> assumption and becomes an unexamined constant.

**The derivation.** Rendered width is the product of three effects, all running the same direction:

| Effect | Contribution |
|---|---|
| More characters (mean, from §4.1) | ~ +15% |
| **Higher point size** — Bengali body 16 px against English 14 px (`VB-009` §3) | **+14%** |
| Wider average advance per character at the same size — conjuncts, matras, and Hind Siliguri's metrics against Inter's | ~ +10% |

Compounded, these give **+44%**, which is `BL-02`'s +40% to within the precision either figure
deserves. **The +40% is therefore adopted unchanged, now with a derivation behind it.**

| # | Rule |
|---|---|
| `EXP-01` | **The working allowance is `VB-007` `BL-02`'s +40% rendered width over English**, adopted unchanged and derived above. **No second figure is introduced** — two numbers for one thing is the defect class `RQA-12`, `AP-02` and `UX-008-D-01` all record. It remains a **working assumption** until §4.3's measurement replaces it |
| `EXP-02` | **The allowance is never applied to a translated string that has been measured.** Measure first; the allowance is for designing before the string exists |
| `EXP-03` | Containers carry a further **10% headroom** on top (`VB-007` `BL-01`), because the string bundles are not final |
| `EXP-04` | Expansion is **not uniform across the ramp**. Short labels expand most in percentage terms (`Search` +50%); long sentences expand least. Toolbars and action bars break first (`VB-007` `BL-07`) |

## 4.3 The measurement obligation

An interim factor is a temporary instrument. It is replaced by measurement, and the measurement is
mechanical.

| # | Rule |
|---|---|
| `EXP-05` | The build renders **every string in `BN-009`…`BN-013`** at its token's type settings, in Hind Siliguri **and** Noto Sans Bengali, and records its width. Output is a per-key table of English width, Bengali width and the ratio |
| `EXP-06` | The **p95 ratio** replaces `EXP-01`'s +40% as the design allowance — discharging the *"measure the actual string before shipping"* half of `BL-02`, which has never been executed. The **p100** is the container-sizing input for toolbars and single-line controls |
| `EXP-07` | The table is regenerated on every string-bundle change and is a build artefact, not a document |
| `EXP-08` | Keys whose ratio exceeds the p95 by more than 20% are flagged to Localisation and to Design together. **Either the container is wrong or the string is** — `VB-007` `BL-03` says which one changes |

## 4.4 Counted string population

| Bundle | Surface | Keys counted |
|---|---|---:|
| `BN-009` | `P01` Customer | 133 |
| `BN-010` | `P02` Technician | 101 |
| `BN-011` | `P03` Admin | 172 |
| `BN-012` | `P04`–`P06` | 106 |
| `BN-013` | `P07`–`P12` | 127 |
| **Total measurable today** | | **639** |
| Distinct keys in the `UI-*` packs | | **696** |

> **639 measured against 696 written, for 1,404 screens** (`UX-003` §6.4). The measurement harness
> of `EXP-05` should be built now, while the bundles are small enough that its output can be read by
> a person — not when there are forty thousand keys.

---

# 5. Layout Rules

## 5.1 Container sizing

| Component class | Sizing rule | Overflow behaviour |
|---|---|---|
| **Button, action bar, toolbar** | Bengali rendered width + 10% headroom | **Two-line icon-above-label**, never icon-only, never truncated (`VB-007` `BL-05`) |
| **Tab, chip, badge** | Bengali width; badge ≤ 12 characters | Reduce the label set, not the type |
| **Field label** | Bengali width; labels wrap to two lines rather than truncate | Wrap |
| **Table column header** | Bengali width; the column sets its own minimum | Header wraps to two lines; **the table does not scroll horizontally** (SC 1.4.10) |
| **Table cell** | Content-driven | **Truncation permitted with a tooltip and full value on focus** — the one place truncation is allowed |
| **Nav item** | Bengali width | Two lines on `bp.xs`; never truncated |
| **Empty state, help, prose** | Fluid | Wrap |
| **Fixed-height container** | **Prohibited when it holds Bengali** | `VB-009` MM-02 |

| # | Rule | Basis |
|---|---|---|
| `EXP-09` | **Never truncate a label.** Truncation in a *data cell* with a tooltip is acceptable; truncation in a *label*, button, tab or nav item is a defect | `VB-007` `BL-04` |
| `EXP-10` | When space runs out, **drop the icon before the label**. The label carries the meaning; the icon carries the speed | `VB-007` §7.3 |
| `EXP-11` | The degradation order is: icon + label horizontal → icon above label → **label only** → *(registered icon-only set only)* | `VB-007` §7.3 |
| `EXP-12` | No container derives its width from an English string at design time | `LNG-01` |

## 5.2 Vertical rhythm and the density consequence

Bengali needs more vertical room. Matras above and below the baseline collide at Latin line heights.

| Context | English | **Bengali** | Row height at 8 px grid |
|---|---:|---:|---:|
| Body prose | 1.6 | **1.7** | — |
| **Dense table row** | 1.4 | **1.55** | English ~18 px → **Bengali ~23 px** |
| Headings | 1.3 | **1.4** | — |
| Buttons, badges | 1.2 | **1.35** | 40 px → **44 px** |
| Field body (`P02`, `P09`) | 1.6 | **1.7** | — |

> **`LAY-03` restated.** `VB-003` `D-03` requires **≥ 12 rows without scrolling at 1366 × 600**.
> At English `type.body.dense` 13 px / 1.4 with 4 px insets, a row is ~26 px and 20 rows fit
> comfortably. At **Bengali 15 px / 1.55** the same row is ~31 px and, after chrome (≤ 96 px), the
> viewport holds **~16**. The rule still passes — **but the headroom the English design appears to
> have does not exist**, and any addition to row content spends it.

| # | Rule |
|---|---|
| `EXP-13` | **Row height is set by the Bengali line box, in every table, on every surface** |
| `EXP-14` | Line height is a **per-language token**, not a runtime multiplier (`UX-001` `LNG-03`) |
| `EXP-15` | **Letter-spacing on Bengali is always zero.** Tracking separates conjunct components and destroys legibility. The token is locked | `VB-009` LH-02 |
| `EXP-16` | Bengali is **never justified**. Ragged right, always | `VB-009` LH-04 |
| `EXP-17` | Vertical centring is on the **line box**, never the glyph box | `VB-009` MM-03 |

## 5.3 Wrapping and breaking

| # | Rule | Basis |
|---|---|---|
| `EXP-18` | Line breaking follows **UAX #14**; Bengali wraps at word boundaries only | `VB-009` LH-06, `BN-006` §6 |
| `EXP-19` | **Never break inside a conjunct cluster.** A broken conjunct is not a legibility problem, it is a different word | `VB-007` `BL-06` |
| `EXP-20` | Truncation, where permitted (table cells), operates on **grapheme-cluster boundaries per UAX #29**, never on code points. Truncating mid-cluster produces a dotted-circle rendering |
| `EXP-21` | Never force a line break inside a mixed-script phrase | `VB-009` MX-06 |
| `EXP-22` | Hyphenation is **off** for Bengali |

## 5.4 The Bengali-first design method

| Step | Action |
|:--:|---|
| 1 | Take the **Bengali** string from `BN-009`…`BN-013`, or the longest plausible Bengali if unwritten |
| 2 | Set it at the `.bn` type token for its role, at the Bengali floor |
| 3 | Size the container to the rendered width **+ 10%** |
| 4 | Verify the English variant fits the same container — it will, being shorter |
| 5 | Verify at **rank 2** (Noto Sans Bengali), whose metrics differ (`VB-009` MM-04) |
| 6 | Verify at **200% text scale** (SC 1.4.4) and at **320 px** (SC 1.4.10) |
| 7 | Apply the WCAG **text-spacing** adjustment (SC 1.4.12) and confirm nothing is lost |

| # | Rule |
|---|---|
| `EXP-23` | Steps 5, 6 and 7 are where Bengali layouts fail. **`VB-009` LH-06 records that Bengali layouts commonly fail SC 1.4.12**; it is not an edge case |
| `EXP-24` | A screen with `bengali_risk: high` (`UX-003` `SIR-24`) completes all seven steps and produces an **F4** artefact (`UX-003` §9) |

## 5.5 Placeholders and plurals in layout

| # | Rule | Basis |
|---|---|---|
| `EXP-25` | A container sized to a message with a `{placeholder}` is sized to the **longest substitution**, not the placeholder token | `BN-005` §3.2 |
| `EXP-26` | Bengali has **two** cardinal plural categories where English has two but with different boundaries; the container is sized to the longest form | `BN-005` §4.1 |
| `EXP-27` | Concatenation is prohibited. Sentences are assembled by ICU MessageFormat, never by joining fragments — the fragments reorder in Bengali | `BN-005` §3.1 |
| `EXP-28` | A number substituted into Bengali prose may render in Bengali digits (`BN-007` §3.2) and Bengali digits have **different advance widths**. Size to the wider |

---

# 6. Numerals in Layout

## 6.1 The decision, and `UXA-15`

`UX-001` `Q-05` asked which numeral policy applies, noting that `VB-009` `NU-03` called its own
policy *"proposed"* and deferred to `BN-007`, while `CG-010` §12 item 3 listed the decision as open.

> **Answer: it is decided.** `BN-007` §3.1 states `NM-A`…`NM-E` and opens with *"This closes
> `CG-010` §12 item 3 and `VB-009` `NU-03`."*

| # | The decision (`BN-007` §3.1) |
|---|---|
| `NM-A` | **Arabic digits are the system default in both locales.** ICU numbering set to `latn`, overriding the CLDR `beng` default |
| `NM-B` | Bengali digits only in help/training/knowledge prose, Bengali-prose dates, and Bengali marketing copy |
| `NM-C` | Never mix numeral systems within one value, column, document, message or screen region |
| `NM-D` | **Identifiers are Arabic digits always** |
| `NM-E` | **Bengali digits are accepted as input everywhere** and normalised on write |

> **`UXA-15`.** `CG-010` §12 **still lists item 3 as an open decision**, and `CG-010` is the policy
> that governs the `BN` bundles and every `UI` pack. An open-decisions register carrying a closed
> decision causes exactly the confusion `UX-001` `Q-05` recorded. Raised as a content correction
> under `CG-006`. **Severity is low; the cost of not raising it is that the next document to ask
> the question gets the same wrong answer.**

## 6.2 Layout consequences

| # | Rule |
|---|---|
| `EXP-29` | Because output is Arabic digits nearly everywhere (`NM-A`), **numeric column widths are the same in both locales** — the one part of a bilingual table that does not expand |
| `EXP-30` | `type.numeric` uses **tabular figures**, right-aligned, in both locales. Proportional figures make columns unscannable | `VB-003` TY-03 |
| `EXP-31` | Where Bengali digits do render (`NM-B` contexts), the container is sized to the **wider** of the two digit sets (`EXP-28`) |
| `EXP-32` | **Number grouping is lakh/crore in the Bengali locale** — 12,34,567 — regardless of digit glyphs. A column formatted 1,234,567 in one locale and 12,34,567 in the other has **different widths**; size to lakh/crore | `VB-009` NU-04, `BN-007` §4.1 |
| `EXP-33` | Currency is `৳` in the Bengali locale and `BDT` in the English locale — **one character against three**. Money columns are sized to `BDT` | `VB-009` NU-05 |
| `EXP-34` | `NM-E` means every numeric input accepts Bengali digits. **The input control must not visually reject them** while normalising on write |

---

# 7. Mixed Script

Bengali interface content routinely contains Latin: brand names, statutory form names, identifiers,
technical terms. This is normal and must be laid out for, not treated as an exception.

| # | Rule | Basis |
|---|---|---|
| `EXP-35` | Do-not-translate items stay in Latin inside Bengali text — `Mushak 6.3`, `BIN`, `bKash`, `Samsung`, `SR-2026-114882` | `VB-009` MX-01, `BN-004` |
| `EXP-36` | Latin inside Bengali is set in **Inter**, not Hind Siliguri's Latin glyphs | `VB-009` MX-02 |
| `EXP-37` | Latin inside Bengali sets **one step smaller** — Inter's x-height is proportionally larger and unadjusted Latin looks oversized | `VB-009` MX-03 |
| `EXP-38` | **Every script change carries a `lang` attribute** (SC 3.1.2). Without it a screen reader pronounces "Mushak" with Bengali phonology | `VB-009` MX-04, `ACD-14` |
| `EXP-39` | Never transliterate a technical identifier into Bengali script | `VB-009` MX-05 |
| `EXP-40` | Bidirectional handling is **not required** — Bengali is left-to-right, like Latin. Reading order, focus order and breadcrumb direction are shared | `VB-009` MX-07 |
| `EXP-41` | A mixed-script line's height is set by the **taller** line box, which is the Bengali one |

---

# 8. The Language Switch

## 8.1 The control

| # | Rule | Basis |
|---|---|---|
| `EXP-42` | The control is in global chrome, **top-right, on all thirteen surfaces** (`P09` excepted — no toggle) | `UX-002` §6.1 |
| `EXP-43` | It always shows the **other** language — "English" when in Bengali, "বাংলা" when in English | `UI-002` §3 |
| `EXP-44` | It is a **two-state toggle**, not a dropdown. Two languages do not need a menu |
| `EXP-45` | It is never inside a settings screen only. A user who cannot read the current language cannot navigate to settings to change it |

## 8.2 The state contract

| # | Rule |
|---|---|
| `EXP-46` | Switching language **preserves the current screen, the current record, scroll position, unsaved form input, filter state and selection**. Nothing is lost |
| `EXP-47` | The route changes only its locale segment (`UX-002` §7.1): `/bn/…` ↔ `/en/…` |
| `EXP-48` | The preference is **persisted per user and synced across devices**, not per browser session |
| `EXP-49` | On `R4`, the switch works **offline** — both bundles are in the application package (`LNG-08`) |
| `EXP-50` | The switch **never changes the data**. A record created in Bengali reads in English with the same values; only labels and formats change |
| `EXP-51` | Free-text content is **not machine-translated** on switch. A Bengali diagnosis stays Bengali, marked `lang="bn"` (`EXP-38`) |

> **`EXP-46` is the rule most likely to be implemented badly.** A language switch that reloads to a
> home screen and discards a half-completed intake form will be used once by each agent and never
> again, and the bilingual commitment fails silently.

## 8.3 The unresolved surface — `P04`

`CG-010` §12 item 4 is open: *"Corporate portal (`P04`) — is the UI bilingual while its documents
stay English?"* Needed by W4.

| # | Position |
|---|---|
| `EXP-52` | **`P04` is designed as bilingual regardless of the outcome.** Containers are sized to Bengali (`LNG-03`), so a decision either way costs nothing later. Deciding to be English-only *after* sizing to English is the expensive path |

---

# 9. Fonts and Payload

| # | Rule | Basis |
|---|---|---|
| `LNG-08` | `R4` applications **bundle Hind Siliguri** and both string bundles. A technician offline for 24 hours cannot download a font or a language | `VB-009` TF-02 |
| `LNG-09` | `R3` web surfaces load Hind Siliguri with `font-display: swap` and the `VB-009` §2.1 fallback stack | `VB-009` TF-03 |
| `LNG-10` | The Bengali web font is **subset to U+0980–U+09FF plus Latin basic**, with a budget of **120 KB** against the 400 KB first-load ceiling | `NFR-081` |
| `LNG-11` | **Both faces are verified**: rank 1 Hind Siliguri and rank 2 Noto Sans Bengali (the Android default and the realistic majority fallback). Their vertical metrics differ and a layout tuned to one breaks on the other | `VB-009` MM-01, MM-04 |
| `LNG-12` | Never mix two Bengali faces on one surface | `VB-009` TF-06 |
| `LNG-13` | A fallback to generic `sans-serif` renders conjuncts as boxes. **The layout must not depend on the fallback being adequate** — it is a failure case, and the swap window is designed for, not ignored |

---

# 10. Build-Time Proof

> A layout standard that is checked by a designer looking at screenshots is checked once.

## 10.1 Pseudo-localisation

| # | Rule |
|---|---|
| `EXP-53` | The build produces a **pseudo-locale** that expands every English string by the current design allowance (`EXP-01`, later `EXP-06`) and substitutes accented and conjunct-bearing characters |
| `EXP-54` | Every screen is rendered in the pseudo-locale in CI. **Overflow, clipping and horizontal scroll fail the build** |
| `EXP-55` | Pseudo-localisation runs **before** translation exists, so a layout defect is found while it is cheap. It does not replace real-Bengali verification (`EXP-56`) |

## 10.2 Real-Bengali verification — `CFM-07`

| # | Rule |
|---|---|
| `EXP-56` | Every component and screen is rendered with the **longest registered Bengali string** for each of its slots, from `BN-009`…`BN-013` |
| `EXP-57` | **Any truncation of a label fails the build.** Truncation of a data cell with a working tooltip passes | `EXP-09` |
| `EXP-58` | The check runs in **both faces** (`LNG-11`), at **100% and 200%** scale, and with the **WCAG text-spacing** adjustment applied |
| `EXP-59` | `P03` list screens additionally assert the **≥ 12-row** count at 1366 × 600 in Bengali dense type (`CFM-08`) |

## 10.3 Device verification

Automation cannot see a conjunct rendered as a box. `BN-006` §9 supplies the test set; this is when
it runs.

| Surface | Verify on | When |
|---|---|---|
| Web portals | Chrome, Firefox, Safari, Edge — desktop and Android | Every release |
| `P02`, `P09`, `P11` | **Mid-range Android 11, 3 GB RAM** — the reference device | Every mobile release |
| `P01` app | Android and iOS, low and high density | Every app release |
| Print and thermal | Branch laser and 80 mm / 58 mm thermal | Per template change |

| # | Rule |
|---|---|
| `EXP-60` | Verification uses the `BN-006` §9 conjunct test set, including the **ra-ya-phala** case (`BN-006` §3.1), which is where shaping engines diverge |
| `EXP-61` | A rendering failure on rank 2 is a **release blocker on `R4`**, because rank 2 is what most technician devices will actually use |

---

# 11. Per-Surface Bengali Risk

Feeds `UX-003` `SIR-24` (`bengali_risk`) and orders the F4 verification work.

| Surface | Risk | Why |
|---|:--:|---|
| `P03` | **High** | Dense tables at 1366 × 600, 14 workspaces, toolbars everywhere — the tightest layout in the estate meets the largest expansion |
| `P02` | **High** | 17 px floor, 19 px safety text, small screen, one hand. Least room, largest type |
| `P09` | **High** | 3 tabs, largest type in the estate, no toggle to fall back to |
| `P10` | **High** | Agent console density plus live conversation; screen switches < 3 per contact |
| `P01` app | Medium | Mobile-first, generous by design |
| `P01` web | Medium | Booking funnel is short-form |
| `P11` | Medium | Checklists and forms; moderate density |
| `P05`, `P07`, `P12` | Medium | Bengali default, moderate density |
| `P04`, `P08` | Low | English default; Bengali is the toggle |
| `P06` | Low–Medium | English default, **but chart labels have no room to expand** and are the one place truncation is not fixable by reflow |

| # | Rule |
|---|---|
| `EXP-62` | High-risk surfaces produce F4 artefacts for **every** screen, not a sample |
| `EXP-63` | `P06` chart labels use the shortest registered Bengali term (`BN-003`) and never abbreviate ad hoc; where no short term exists, the label sits outside the plot area |

---

# 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `UX-007-D-01` | Which language a layout is designed in | (a) English, verify Bengali; (b) **Bengali-first on the eight Bengali-default surfaces** | **(b)** | A container sized to the shorter string produces a defect the whole grid derives from | Design reviews reject English-only artefacts (`LNG-04`) |
| `UX-007-D-02` | The expansion allowance | (a) +30% per `L-07` (character count); (b) **adopt `VB-007` `BL-02`'s +40% rendered width, derived and then measured**; (c) publish a new derived figure (+44%) | **(b)** | `L-07` is a character-count figure and understates the problem; `BL-02` is already the estate's rendered-width figure and the derivation in §4.2 lands on +44%, which is +40% within either figure's precision. **Introducing a competing number would be the defect this document criticises elsewhere** | `EXP-05` measurement harness must be built; `BL-02` is confirmed, not superseded |
| `UX-007-D-03` | Truncation | (a) truncate with tooltip; (b) **never for labels, permitted for data cells** | **(b)** | `VB-007` `BL-03`: a truncating label is a layout defect | `CFM-07` fails the build on label truncation |
| `UX-007-D-04` | Line height | (a) one value with a runtime multiplier; (b) **per-language token** | **(b)** | A multiplier cannot express different floors | Row heights are Bengali-derived everywhere (`EXP-13`) |
| `UX-007-D-05` | `P04` bilingual status | (a) wait for `CG-010` item 4; (b) **design bilingual regardless** | **(b)** | Sizing to Bengali costs nothing; sizing to English and reversing is expensive | `EXP-52` |
| `UX-007-D-06` | Pseudo-localisation | (a) rely on real Bengali only; (b) **both** | **(b)** | Real Bengali arrives after the layout is built; pseudo finds the defect while it is cheap | Two CI steps rather than one |

---

# 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | When is the `EXP-05` measurement harness built? Until it runs, `BL-02`'s +40% is a working assumption carrying every container in the estate — and `BL-02`, `LB-11` and `IC-23` have all deferred to a measurement that has never been executed | Front-end Lead + Localisation Lead | **W1** | `EXP-06`, every container |
| `Q-02` | `CG-010` §12 item 4 — is `P04` bilingual? Design proceeds bilingual either way (`EXP-52`), but content volume depends on it | Account Management + Localisation | **W4** | `UI-014`, `BN-012` |
| `Q-03` | `CG-010` §12 item 1 — single Bengali register, or formal for Class A/B? Register affects string length and therefore layout | Localisation Lead | **W1** | All `BN` bundles, `EXP-05` |
| `Q-04` | Who raises the `UXA-15` correction to `CG-010` §12? | Content Design Lead | W1 | `UXA-15` closure |
| `Q-05` | Is the Bengali string estate to be extended to 1,404 screens, and at what rate? 639 keys exist (`UX-003` `UXA-07`) | Localisation Lead + `GV-007` owner | **W1** | Content baseline, `EXP-56` coverage |
| `Q-06` | Does the reference-device fleet include a rank-2-only device (no Hind Siliguri) for `EXP-61`? | Mobile Lead | W2 | `LNG-11` verification |

---

# 14. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every surface has a stated default language and a stated layout language | §3.1, §3.2 |
| `AC-02` | Expansion is stated by character count **and** by rendered width, the estate's existing +40% is derived rather than replaced, and the difference is explained | §4.1, §4.2 |
| `AC-03` | A measurement obligation replaces the working assumption, with a defined output | §4.3 |
| `AC-04` | Container sizing rules exist per component class, with a defined overflow behaviour | §5.1 |
| `AC-05` | The density consequence of the Bengali line box is quantified | §5.2 |
| `AC-06` | The numeral question is answered with its source, and the stale open item is raised | §6, `UXA-15` |
| `AC-07` | The language switch has a state contract | §8.2 |
| `AC-08` | Every rule is provable at build time or is named as device-verification-only | §10 |

**Definition of done.** Complete when every criterion is met, the `EXP-05` harness runs in CI,
`Q-03` is decided, the `CG-010` §12 correction is raised, and `PGD-000`'s `UX-007` row is updated
with a fresh enumeration timestamp.

---

# 15. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `VB-009`, `BN-006` | Typography and script mechanics |
| Upstream | `BN-005`, `BN-007` | Message format and the numeral decision |
| Upstream | `UX-001` §5.5 | The `.bn` token family |
| Upstream | `RQ-001` `L-07`, `UI-R3` | The requirement this makes buildable |
| Downstream | **`UX-003`** | `bengali_risk` and the ~90 F4 artefacts |
| Downstream | **`UX-006`** | Field floors applied to the four applications |
| Downstream | `AR-007` `V-08` | The definition `V-08` asserts against |
| Downstream | `BN-009`…`BN-013` | The containers the bundles are written against |
| Downstream | `QA-003` | `CFM-07`, `EXP-54` assertions |
| Lateral | `CG-010` §12 | Two open items; one stale (`UXA-15`) |
| Lateral | `VB-007` §7 | Measured expansion; **`BL-02`'s +40% adopted unchanged** and given a derivation (§4.2) |

---

# 16. References

**Within this repository**
`../PGD-000_…` · `./_CATEGORY_OVERVIEW.md` · `./UX-001`, `./UX-003`, `./UX-005`, `./UX-006` ·
`../01_Requirements_Engineering/RQ-001`, `RQ-006` · `../02_Architecture_and_Design/AR-007`

**Workspace**
`../../project_content/01_Voice_Brand_and_Design_Content/VB-007` §7, `VB-009` ·
`../../project_content/11_Localisation_Bengali/BN-004`, `BN-005`, `BN-006`, `BN-007`, `BN-009`…`BN-013` ·
`../../project_content/00_Content_Governance_and_Standards/CG-010` ·
`../../project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-001`, `UI-002`

**External standards and sources**

| Source | Status at verification | Verified |
|---|---|---|
| The Unicode Standard, **Version 17.0** (released 9 September 2025); Bengali block U+0980–U+09FF. Unicode 17.1 scheduled September 2026 | Current | 2026-08-18 |
| Unicode **UAX #14** — Unicode Line Breaking Algorithm | Current | 2026-08-18 |
| Unicode **UAX #29** — Unicode Text Segmentation (grapheme clusters) | Current | 2026-08-18 |
| Unicode **UAX #15** — Unicode Normalization Forms | Current | 2026-08-18 |
| Unicode **CLDR**, locale `bn-BD` | Current | 2026-08-18 |
| IETF **BCP 47** — Tags for Identifying Languages | Current | 2026-08-18 |
| **ICU MessageFormat** | Current | 2026-08-18 |
| W3C — WCAG 2.2, SC 1.4.4, 1.4.10, **1.4.12**, 3.1.1, 3.1.2 | Recommendation | 2026-08-18 |

---

# 17. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Head of Product Design | Initial issue. Converts `L-07` and `UI-R3` from a statement about translation into a **buildable layout standard**: Bengali-first design for the eight Bengali-default surfaces, **`VB-007` `BL-02`'s +40% rendered-width allowance adopted unchanged and given a derivation** (`UXA-16` — the figure has carried five files with neither derivation nor the measurement three of them defer to), the measurement harness that discharges it, container rules per component class, and build-time proof by pseudo-localisation plus real-Bengali rendering. Quantifies the Bengali density consequence for `LAY-03`. **Answers `UX-001` `Q-05`** — `BN-007` §3.1 decided the numeral policy — and raises `UXA-15`, that `CG-010` §12 still carries it as open | *(pending — `PGD-A1-09`)* |

---

*`UX-007` · Category 06 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
