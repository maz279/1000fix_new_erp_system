---
id: BN-006
title: Bengali Typography, Font and Numeral Standard
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Platform Engineering, Mobile Engineering and Design System
reviewers: [Brand Lead, Design System, Platform Engineering, Mobile Engineering, Accessibility reviewer, QA Lead]
approver: Content Design Lead with Localisation Lead
content_class: D
purpose: >
  The localisation-owned Bengali typography standard: the script behaviour, encoding,
  normalisation, shaping, font-coverage, line-breaking, truncation and rendering-verification
  rules that decide whether Bengali text is correct at all, as distinct from whether it is
  on-brand. VB-009 governs the brand and token view of the same subject and the two are
  ratified together. Bengali conjuncts fuse into unreadable strokes at small sizes on the
  mid-range Android device 200-400 technicians carry, and a text that is encoded, normalised
  or shaped wrongly is not merely ugly — it does not match, does not sort, does not search and
  cannot be truncated without corrupting a letterform.
traces_to: [VB-009, BN-002 OR-02, BN-004, BN-007, CG-010 BC-04, CG-011, 04-00 §P02, 05-06 §9, 05-06 NFR-016, 05-06 NFR-074, 05-06 §10, TS-016]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009 §2 six-rank font stack, §3 minimum sizes with absolute floors, §4 per-language line heights, §5 proposed numeral policy, §6 mixed script, §7 rendering verification and the conjunct test string
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — UTF-8 throughout, ICU bn-BD collation, Bengali fonts rendered correctly across Android, iOS, Windows and print, Bengali printing verified on all supported printers; §10 minimum desktop 1366x768, field device 3 GB RAM Android 11+, thermal receipt printers
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 non-negotiable #4 — runs acceptably on a mid-range Android 11 device with 3 GB RAM
    verified: 2026-08-17
    class: P1
  - source: Unicode FAQ Bengali (Bangla) and Unicode L2/03192 — reph and ya-phala behaviour; the Unicode-recommended ra + U+200C ZWNJ + halant + ya sequence for ra-japhala, with inconsistent shaping-engine support; U+09CE KHANDA TA encoded to avoid the ZWJ workaround
    verified: 2026-08-17
    class: P2
  - source: Bangladesh Standards — BDS 1738:2018 Bijoy keyboard layout and BDS 1935:2018 Bijoy coding system declared national standards; Jatiyo (National) layout developed by Bangladesh Computer Council; Avro phonetic with a built-in legacy-Unicode converter
    verified: 2026-08-17
    class: P2
  - source: Unicode CLDR cldr-numbers-full bn/numbers.json — "defaultNumberingSystem":"beng"; native numbering "beng"
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-006 — Bengali Typography, Font and Numeral Standard

> **`VB-009` asks whether Bengali looks right. This file asks whether it *is* right.**
>
> A Bengali string can be perfectly typeset and still be wrong at the code-point level: the same
> word encoded two ways will not match, will not sort together and will not be found by search,
> and no visual inspection will reveal it. Conversely a correctly encoded string can shatter into
> separate letters with a visible hasant on a shaping engine that does not implement the feature
> the font relies on.
>
> **`VB-009` governs brand and token questions. This file governs script and encoding questions.
> They are ratified together and must not diverge (`CP-01`, `VB-009` §1).**

---

## 1. Purpose and division of ownership

| | |
|---|---|
| **What this governs** | Encoding, normalisation, joiner semantics, shaping-engine behaviour, font glyph and OpenType coverage, line breaking, truncation, collation, input methods, numeral glyph rendering and rendering verification |
| **What `VB-009` governs** | The chosen typefaces and the brand reason for them, the type-scale token values, minimum sizes, line heights, brand lock-ups and print application |
| **What it does not govern** | Number, date and currency **formats** (`BN-007`); which words are used (`BN-002`, `BN-003`); which items stay Latin (`BN-004`) |
| **What breaks without it** | Text that does not match itself, tofu on the device class `P02` targets, truncation that severs a conjunct, search that misses half its results, and Bengali that renders on the developer's machine and not on the branch printer |

### 1.1 Where the two files touch

| Subject | Decided by | The other file's role |
|---|---|---|
| Which typeface | `VB-009` `TF-01` | This file states the **glyph and feature coverage** any candidate must have (§5) |
| Minimum size in px/pt | `VB-009` §3 | This file states **why** the floor exists in script terms (§4) |
| Line height | `VB-009` §4 | This file states the matra-collision cause |
| Mixed script and `lang` marking | `VB-009` §6 | Repeated only where encoding is affected |
| Numeral **glyph** rendering | This file §7 | `VB-009` §5 proposes; `BN-007` §3 **decides the policy** |
| Rendering verification | Both | `VB-009` sets the surfaces and cadence; this file sets the **script test set** (§9) |

> **A register discrepancy is recorded, not absorbed.** The Master Index describes `BN-006` as
> carrying the "Bengali versus Arabic numeral policy" and `VB-009` `NU-03` names **`BN-007`** as
> the authoritative decision. Both cannot be true. **Resolution: `BN-007` §3 decides the policy;
> this file §7 governs how the chosen glyphs render.** Raised as `AUDIT-012` **BN-08**.

---

## 2. Why Bengali is a different rendering problem

Not background. Each property below generates a rule later in this file.

| Property | Consequence |
|---|---|
| **Conjunct consonants — যুক্তাক্ষর** | Two or more consonants fuse into a single new letterform. There are several hundred. A font missing one renders it as separate letters with a visible hasant, or as tofu |
| **Matras above and below the baseline** | ি ী ু ূ ৃ ে ৈ ো ৌ and ঁ occupy vertical space outside the x-height. They collide at Latin line heights and clip at fixed container heights |
| **Pre-base vowel reordering** | ি and ে are **typed after** the consonant and **rendered before** it. Character order and visual order differ, which is why cursor movement, selection and truncation must operate on grapheme clusters |
| **Reph — র্** | ra + hasant before a consonant renders as a mark **above** the following cluster |
| **Ya-phala — ্য and ra-phala — ্র** | Subjoined forms that attach below or beside the base |
| **Khanda ta — ৎ (U+09CE)** | Encoded as its own character precisely so a joiner workaround is not needed |
| **No letter case** | Meaning can never rest on capitalisation (`CG-010` `BC-02`, `BN-002` `SC-08`) |
| **Digits have their own block** | ০–৯ (U+09E6–U+09EF) are distinct characters from 0–9 |
| **Words are space-separated** | Line breaking works on spaces, unlike Thai or Khmer — but **never inside a cluster** |
| **Multiple valid encodings for one appearance** | The reason §3 exists |

---

## 3. Encoding and normalisation

**The rules in this section have no visual symptom. They are found by search failing, by a
duplicate record, or by a comparison returning false on two strings that look identical.**

| # | Rule |
|---|---|
| **EN-01** | **UTF-8 everywhere** — client, transport, database, index, cache, export, print, log (`05-06` §9). No `latin1` column, no `cp1252` export, no ASCII log truncation |
| **EN-02** | **Unicode NFC on write.** All Bengali text is normalised to NFC at the point of entry and at every ingestion boundary — UI, API, import, migration, scanner, voice-to-text. **Comparison, deduplication, indexing and matching operate on the normalised form only** |
| **EN-03** | **ZWJ (U+200D) and ZWNJ (U+200C) are permitted only where the Bangla Academy form requires them.** They are otherwise stripped at normalisation. A joiner inserted by a keyboard is invisible on screen and makes the string a different string to every index in the system |
| **EN-04** | **Khanda ta is U+09CE.** The ta + hasant + ZWJ sequence is not used. Migration converts it (`DM-011`) |
| **EN-05** | **Legacy Bijoy ASCII is not accepted as input.** Bangladesh's national standards include the Bijoy coding system (BDS 1935:2018) alongside Unicode, and legacy ASCII pasted into a Unicode field renders as mojibake. Paste and import paths **convert or reject**; they never store (`BN-001` `IN-08`, `DM-011`) |
| **EN-06** | **CSV and XLSX exports are UTF-8 with BOM.** Excel on a Windows branch machine opens a BOM-less UTF-8 file in the system codepage and renders every Bengali column as mojibake (`BN-004` §7, `RP-014`) |
| **EN-07** | **Sorting and comparison use ICU `bn-BD` collation** (`05-06` §9). Code-point order is not Bengali alphabetical order and must never be used for a user-visible sort |
| **EN-08** | Bengali is **left-to-right**. No bidirectional handling is required (`VB-009` `MX-07`) |
| **EN-09** | The locale tag is **`bn-BD`**, never bare `bn` or `bn-IN` (`BN-005` `BU-07`) |
| **EN-10** | Text length is measured in **extended grapheme clusters**, never in code points or UTF-16 units. `ক্ষ` is one cluster and three code points; a 20-character budget counted in code points is not a 20-character budget |

### 3.1 The ra-ya-phala case

The one sequence where the correct encoding is genuinely contested and shaping-engine support is
uneven. It appears in ordinary Bangladeshi words — র‍্যাব, র‍্যাক, র‍্যাম.

| # | Rule |
|---|---|
| **EN-11** | The programme adopts **one** encoding for ra-ya-phala, records it here once the target shaping engines have been tested (§9), and normalises all input to it |
| **EN-12** | **Until §10 decision 1 is closed, the affected words are avoided in authored content** where an alternative exists — র‍্যাম is written as **RAM** under `BN-004` Class C, which is the correct treatment regardless |
| **EN-13** | Migration and search normalise both known sequences to the adopted form, so that legacy data remains findable (`DM-011`) |

> **This is exactly the class of defect that is invisible in review and fatal in production.**
> The word renders correctly in the reviewer's browser, incorrectly in the technician's app, and
> the two strings do not match each other in the database. It is recorded as an open decision
> rather than assumed away.

---

## 4. Why the size floors exist

`VB-009` §3 sets the floors and declares them unwaivable. This section supplies the script reason,
so that a designer asking "why not 13px?" gets an answer rather than a rule.

| Script feature | What fails first as size drops |
|---|---|
| Conjunct internal strokes | The components of ক্ষ, ঙ্ক, স্ত্র merge into a single dark mass |
| Hasant (্) | Disappears, turning a conjunct into two letters or the reverse |
| Chandrabindu (ঁ) | Merges into the matra above it — চাঁদ becomes চাদ |
| ি versus ী | The distinguishing tail vanishes; two different words become one |
| ব versus র | The distinguishing dot fills in at low resolution and no anti-aliasing |
| Reph | Collides with the matra above the same cluster |
| Digits ০ / ৩ / ৪ | ০ and ৩ converge; ৪ and ৮ converge |

| # | Rule |
|---|---|
| **SZ-01** | **The `VB-009` §3 floors are this file's floors.** They are not restated here; a single set of numbers exists (`CP-01`) |
| **SZ-02** | **No hinting, sub-pixel or synthetic-bold trick substitutes for size.** Synthetic bold in particular thickens conjunct strokes until they merge |
| **SZ-03** | **Synthetic italic and synthetic bold are prohibited on Bengali.** Only real weights from the family are used (`VB-009` `TF-07`) |
| **SZ-04** | **Never apply `text-transform`** to Bengali. It is inert on a caseless script and, on mixed-script strings, corrupts the Latin half |
| **SZ-05** | **Never letter-space Bengali** (`VB-009` `LH-02`). Tracking separates conjunct components, which is not a legibility trade-off — it is a different letter |
| **SZ-06** | **Never condense or scale Bengali horizontally.** Stroke weights become inconsistent and thin strokes disappear at the floor |
| **SZ-07** | Thermal 203 dpi output has **no anti-aliasing**. Every stroke is one dot or zero dots, which is why the thermal floor is the highest in the table (`VB-009` §3) |

---

## 5. Font requirements — the script view

`VB-009` `TF-01` selects Hind Siliguri and ranks the fallback stack. This section states what any
Bengali face must satisfy to be **eligible**, so that a future substitution is assessed rather
than assumed.

| # | Requirement |
|---|---|
| **FR-01** | Full coverage of the **Bengali block U+0980–U+09FF**, including ৎ (U+09CE), ৳ (U+09F3) and the digits ০–৯ |
| **FR-02** | **Conjunct glyph coverage** for the full set in ordinary Bangladeshi usage, not a subset. A face with 400 glyphs will render some conjuncts as fallback compositions |
| **FR-03** | OpenType Indic feature support: **`nukt`, `akhn`, `rphf`, `blwf`, `half`, `pstf`, `vatu`, `cjct`, `pres`, `abvs`, `blws`, `psts`, `haln`** |
| **FR-04** | Correct **mark positioning** (`mark`, `mkmk`) so that a matra and a chandrabindu on the same cluster do not overlap |
| **FR-05** | Real weights at **400, 500, 600, 700** (`VB-009` `TF-07`). Light weights lose conjunct strokes at the floor |
| **FR-06** | **Vertical metrics compatible with the rank-2 fallback**, since layouts must hold on both (`VB-009` `MM-01`…`MM-04`) |
| **FR-07** | A **licence permitting embedding in PDF and bundling in a mobile application package** (`VB-009` `TF-02`, `TF-05`) |
| **FR-08** | Tabular figures for both numeral systems, so that a column of numbers aligns (§7) |

| # | Rule |
|---|---|
| **FR-09** | **A font substitution is a `BN-006` and `VB-009` change**, assessed against `FR-01`…`FR-08` and re-verified per §9. It is never a build-configuration change |
| **FR-10** | **Never rely on a system Bengali font on `P02`, `P09` or `P11`.** The font is bundled (`VB-009` `TF-02`, `BN-005` `BU-05`) |
| **FR-11** | Where a surface cannot bundle — email, some print drivers — it is **designed at rank 2** and verified there (`VB-009` `TF-04`) |

---

## 6. Line breaking, wrapping and truncation

The area where Bengali most often breaks in ways English never does.

| # | Rule |
|---|---|
| **LB-01** | Line breaking occurs at **spaces and at explicit break opportunities only** |
| **LB-02** | **Never break inside an extended grapheme cluster.** A break between a consonant and its matra produces a fragment that is not a letter |
| **LB-03** | **Never break inside a conjunct**, even where the renderer offers the opportunity |
| **LB-04** | **Never break inside a mixed-script phrase** (`VB-009` `MX-06`) or inside an identifier (`BN-004` `DN-05`) |
| **LB-05** | **Never hyphenate Bengali.** Bengali has no hyphenation convention and automatic hyphenation invents one |
| **LB-06** | **Never justify Bengali** (`VB-009` `LH-04`). Ragged right, always |
| **LB-07** | **Truncation operates on grapheme clusters** and appends `…` (single character). A truncation that severs a cluster displays a broken letterform, not a shortened word |
| **LB-08** | **Prefer two lines to truncation, and truncation to icon-only** (`VB-007` `BL-04`, `VB-009`) |
| **LB-09** | Where truncation is unavoidable, the **full value is available** — tooltip, detail view, or accessible name (`CG-011`) |
| **LB-10** | **Never set a fixed height on a container holding Bengali** (`VB-009` `MM-02`). Matras clip at the line-box edge before they overflow it |
| **LB-11** | Text expansion is measured as **rendered width at the target size in the target face**, never as a character count (`UI-001` §8, `VB-006` `DS-04`) |
| **LB-12** | The planning assumption is **20–40% expansion over English** (`CG-010` `BC-01`), but the **measured** value governs at the gate |

---

## 7. Numerals — the script view

**The policy decision belongs to `BN-007` §3.** This section states what the script requires
whichever way that decision goes, and records the CLDR default that makes the decision urgent.

### 7.1 The default nobody chose

| Fact | Consequence |
|---|---|
| **CLDR declares `beng` — Bengali digits — as the `defaultNumberingSystem` for locale `bn`** | An ICU number formatter configured with `bn` or `bn-BD` and no explicit numbering system **renders ০১২৩ by default**, including in money, references and quantities |
| CLDR declares the decimal pattern as `#,##,##0.###` | Lakh/crore grouping is the locale default and is correct (`05-06` §9) |
| CLDR declares the currency pattern as `#,##,##0.00¤` | **The currency symbol is a suffix in the Bengali locale** — the opposite of the `৳ 12,34,567.00` form used in existing content examples |

> **This is why the numeral question is not cosmetic.** It is not "shall we use Bengali digits";
> it is "**we are already using them unless someone configures otherwise**", and the places that
> matters most — an amount transcribed into a bank form, a reference read over the hotline, an
> IMEI typed into a brand partner's portal — are the places with the highest error cost.

### 7.2 Script rules, whichever policy is chosen

| # | Rule |
|---|---|
| **NU-01** | **Never mix numeral systems within one value.** `১২,500` is a defect (`VB-009` `NU-01`) |
| **NU-02** | **Never mix within a table column** (`VB-009` `NU-02`) |
| **NU-03** | **Never mix within a document, a message or a single screen region** — this file extends the rule beyond the value and the column, because a receipt showing a Bengali quantity and a Latin price is read as an error by the customer |
| **NU-04** | **Identifiers are always Arabic digits**, in both locales, without exception (`BN-004` `DN-04`) |
| **NU-05** | Numerals are set in **tabular figures** in any column that is scanned vertically (`FR-08`) |
| **NU-06** | Bengali digits at the size floor are **less distinguishable than Latin digits** (§4). Where a value must be read accurately at a small size — a table cell, a thermal receipt — Arabic digits are used regardless of prose context |
| **NU-07** | **The ICU numbering system is set explicitly in code**, never left to the locale default (§7.1). The setting is derived from `BN-007` §3 and from no other source |
| **NU-08** | **Voice output reads digits individually with a pause** (`NT-019` §2.3, `BN-017` `VP-07`), whichever glyphs are displayed |

---

## 8. Input methods

| # | Rule |
|---|---|
| **IM-01** | **The system never requires a specific keyboard, IME or layout.** Users type with Avro phonetic, the Jatiyo/National layout, Bijoy Unicode, the Android or iOS Bengali keyboard, or by voice |
| **IM-02** | Bengali **phonetic input is the norm** (`05-06` NFR-074). Search and matching accommodate the spelling variation it produces (`BN-003` §14) |
| **IM-03** | Input is **NFC-normalised on write** (`EN-02`), so that keyboards emitting different sequences converge |
| **IM-04** | Keyboards that emit **ZWNJ where ZWJ is required, or the reverse**, are a known population. Normalisation handles the difference; the user is never asked to retype |
| **IM-05** | **Voice-to-text on `P02`** captures Bengali (`NFR-074`, `04-00` §P02 Evidence). The transcript is stored as Bengali and is never machine-translated (`CG-010` MT-01) |
| **IM-06** | Numeric fields — mobile, IMEI, amount, NID — **accept Bengali digits as input and normalise them to Arabic on write.** A user with a Bengali keyboard must not be blocked from typing a phone number (`BN-007` `FM-13`) |
| **IM-07** | Copy and paste from a **legacy Bijoy ASCII** source is detected and converted or rejected, never stored (`EN-05`) |
| **IM-08** | The **branch hardware keyboard population** — Windows machines across 51+ sites — is surveyed before W1, because an agent with no working Bengali input cannot complete a Bengali-default intake (`§10` decision 3) |

---

## 9. Rendering verification — the script test set

`VB-009` §7 sets which surfaces are verified and how often, and supplies a brand-level conjunct
test string. This section supplies the **script test set**, which is longer, targeted and
diagnostic: each line isolates one failure mode so that a failure identifies its own cause.

```
1  CONJUNCTS      ক্ষ ঙ্ক জ্ঞ ত্র দ্ব ন্ত ম্ভ ষ্ট স্ত্র হ্ম ক্ত ঞ্চ ণ্ড
2  REPH           কার্যাদেশ · সার্ভিস · কর্তৃপক্ষ · নির্ধারণ
3  YA-PHALA       স্বাক্ষর · ব্যবস্থা · প্রয়োজনীয় · সংক্রান্ত
4  RA-PHALA       ক্রয় · প্রিন্টার · ট্রান্সমিশন · গ্রাহক
5  MATRA STACK    উদ্ভূত · দ্রষ্টব্য · কৃতজ্ঞ · পূর্ববর্তী
6  CHANDRABINDU   চাঁদ · দাঁড়ি · ভাঁজ · আঁকা
7  KHANDA TA      ৎ · বিদ্যুৎ · সাক্ষাৎ · হঠাৎ
8  PRE-BASE VOWEL কি · কে · কৈ · কো · কৌ  (typed after, rendered before)
9  I / II         দিন / দীন · মিল / মীল      (must be distinguishable)
10 BA / RA        বই / রই · বাড়ি / রাড়ি      (must be distinguishable)
11 DIGITS         ০১২৩৪৫৬৭৮৯  ·  0123456789
12 CURRENCY       ৳ ১২,৩৪,৫৬৭.৮৯  ·  ৳ 12,34,567.89  ·  BDT 12,34,567.89
13 MIXED SCRIPT   Mushak 6.3 · BIN 001234567 · SR-2026-114882 · bKash · Samsung
14 LONG LABEL     অব্যবহৃত পার্টস ফেরত দিন  (expansion and wrap behaviour)
15 SAFETY         বিদ্যুৎ সংযোগ বিচ্ছিন্ন করুন। সুরক্ষা সরঞ্জাম পরুন।
```

| # | Check | Pass condition |
|---|---|---|
| **RV-01** | Lines 1–7 | Every glyph is a **formed conjunct or mark**, never separate letters with a visible hasant, never tofu |
| **RV-02** | Line 5 | Matras above and below do **not clip** at the line-box edge and do not overlap each other |
| **RV-03** | Line 6 | Chandrabindu is **distinct** from the matra above it |
| **RV-04** | Line 7 | Khanda ta renders from U+09CE alone |
| **RV-05** | Line 8 | Cursor movement and text selection step **one grapheme cluster at a time**, matching visual order |
| **RV-06** | Lines 9–10 | Distinguishable **at the size floor**, on the target device, at arm's length |
| **RV-07** | Lines 11–12 | Grouping is lakh/crore; the numeral system is the one `BN-007` specifies; the currency symbol is where `BN-007` says |
| **RV-08** | Line 13 | Latin renders in Inter, sits on the same baseline, one step smaller (`VB-009` `MX-02`, `MX-03`) |
| **RV-09** | Line 14 | Wraps at a space, never inside a cluster; truncates with `…` on a cluster boundary if at all |
| **RV-10** | Line 15 | Legible at the `P02` safety size, outdoors, in sunlight (`VB-009` §3) |
| **RV-11** | All lines | Copy the rendered text out and compare byte-for-byte with the source. **A round-trip mismatch is an encoding defect even when the display is correct** |
| **RV-12** | All lines | Verified on the **rank-2 fallback** as well as rank 1 (`VB-009` `MM-04`) |

| # | Rule |
|---|---|
| **RV-13** | **Verification is looking at rendered output on the real device or printer.** It is never a passing unit test or a specification statement (`VB-009` `RV-01`) |
| **RV-14** | Results are recorded per device, engine and printer model in the **rendering register** held by Platform Engineering (`VB-009` `RV-04`) |
| **RV-15** | **A printer that cannot render Bengali conjuncts does not issue Bengali documents; the branch is issued a compliant model.** The document is never silently downgraded to English (`VB-009` `RV-03`) |
| **RV-16** | The mandatory device is a **mid-range Android 11 handset with 3 GB RAM** — the `P02` baseline (`04-00` §P02 #4, `05-06` §10) |
| **RV-17** | A new device, OS version, shaping-engine version, font version or printer model is verified **before** deployment (`VB-009` `RV-05`) |

### 9.1 Shaping engines in scope

| Platform | Engine | Note |
|---|---|---|
| Android — `P01`, `P02`, `P09`, `P11` | HarfBuzz via Minikin | The primary target. Behaviour varies by Android version |
| iOS — `P01` secondary | CoreText | |
| Windows — branch desktops, Outlook | DirectWrite / Uniscribe | Historically the only engine implementing some ra-ya-phala sequences (§3.1) |
| Chrome, Firefox, Edge | HarfBuzz | |
| Safari | CoreText | |
| PDF renderers | Varies | Embedded font does not guarantee identical shaping |
| Thermal and label printers | Vendor firmware | **The least predictable class.** Some models cannot shape Bengali at all (`RV-15`) |

---

## 10. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Which ra-ya-phala encoding is adopted** (`EN-11`), after testing across the §9.1 engines | Platform Engineering with Localisation Lead | Before W1 data load | `DM-011`, search, `MD-021` |
| 2 | **Numeral policy** — inherited from `CG-010` §12 item 3 and `VB-009` `NU-03`. **`BN-007` §3 proposes; ratification is required** | Localisation Lead with Design | **Before W1** | Every bundle, `NU-07`, `BN-007` |
| 3 | **Branch Bengali input survey** (`IM-08`) — what Bengali input exists today on 51+ sites, and what must be deployed | Platform Engineering with Operations | Before W1 | `P03` Bengali-default intake |
| 4 | Is Hind Siliguri's conjunct coverage sufficient for the full Bangladeshi set, verified rather than assumed (`FR-02`)? | Localisation Lead with Design System | Before W1 | `VB-009` `TF-01` |
| 5 | Which thermal and label printer models are certified for Bengali, and what is the replacement plan for those that are not (`RV-15`)? | Platform Engineering with Operations | Before the first `DT` release | `BN-015`, `DT-044` |

---

## 11. Dependencies

| Depends on | Why |
|---|---|
| `VB-009` | The brand counterpart; ratified together. Sizes, line heights and the font stack live there |
| `BN-002` `OR-02` | Orthography and the NFC requirement |
| `BN-004` | Tier 1 items in mixed-script rendering; export encoding |
| `BN-007` | The numeral policy `NU-07` implements |
| `BN-005` `BU-04`, `BU-05` | Bundling of strings and font together |
| `CG-011` | Accessibility consequences of §6 and §9 |
| `05-06` §9, §10 | Encoding, collation, device and printer scope |
| `TS-016` | Where the accessibility half of §9 is executed |

---

## 12. Related documents

| Document | Relationship |
|---|---|
| [`../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | The brand counterpart; ratified together |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | The numeral and format decisions |
| [`BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md`](BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md) | Bundle encoding and font bundling |
| [`BN-015_Bengali_Document_and_Print_Template_Pack.md`](BN-015_Bengali_Document_and_Print_Template_Pack.md) | Where `RV-15` is enforced |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | Where §9 runs as a gate |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | Bengali screen-reader limitations |

---

## 13. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Ownership boundary with `VB-009` stated subject by subject, and the Master Index numeral-policy discrepancy recorded; thirteen encoding and normalisation rules including NFC-on-write, joiner semantics, khanda ta, legacy Bijoy rejection and BOM-on-export; the ra-ya-phala encoding question raised rather than assumed; script reasons supplied for the `VB-009` size floors; eleven font eligibility requirements including OpenType Indic feature coverage; twelve line-break and truncation rules on grapheme clusters; **the CLDR finding that `beng` is the default numbering system for `bn`**; eight input-method rules including Bengali-digit input normalisation; a fifteen-line diagnostic script test set with seventeen verification rules; five open decisions | Content Design Lead with Localisation Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Ownership boundary with `VB-009` stated subject by subject; no size, line-height or font-stack value is restated (`CP-01`)
- [x] **The Master Index / `VB-009` numeral-ownership discrepancy recorded and resolved, not absorbed**
- [x] Encoding rules cover the failures that have no visual symptom
- [x] The ra-ya-phala encoding question raised as open with an interim authoring rule, rather than assumed away
- [x] Script reasons supplied for every size floor, so the rule can be defended rather than only cited
- [x] Font eligibility stated as requirements a substitute must meet, not as a product name
- [x] Truncation and line breaking specified on **grapheme clusters**, with the measurement rule stated
- [x] **CLDR `beng` default sourced and dated**, with the consequence stated plainly
- [x] Input methods cover the real Bangladeshi keyboard population, including Bengali-digit entry into numeric fields
- [x] A diagnostic test set where each line isolates one failure mode, with pass conditions
- [x] Shaping engines enumerated, including the least predictable class
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal standard, English-only by `CG-010` §3.2
- [ ] **ra-ya-phala encoding decided** — outstanding; §10 item 1
- [ ] **Numeral policy ratified** — outstanding; §10 item 2, `W1` blocker
- [ ] **Hind Siliguri conjunct coverage verified** — outstanding; §10 item 4
- [ ] **Printer certification list produced** — outstanding; §10 item 5
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
