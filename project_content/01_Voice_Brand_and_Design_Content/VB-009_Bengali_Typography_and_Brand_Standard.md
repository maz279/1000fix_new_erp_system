---
id: VB-009
title: Bengali Typography and Brand Standard
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead
author: Brand with Localisation and Design System
reviewers: [Localisation Lead, Content Design Lead, Design System, Accessibility reviewer, Platform Engineering]
approver: Content Design Lead
content_class: D
purpose: >
  Fixes the Bengali typefaces, sizes, line heights, numeral policy and mixed-script rules for
  every ERP surface. PS-03 makes Bengali the default on customer and field surfaces; P02
  requires a complete Bengali interface on a mid-range Android with 3 GB RAM. Bengali conjuncts
  break at small sizes on exactly that device class, so unresolved typography is not a polish
  issue - it is an unusable technician application.
traces_to: [04-00 PS-03, 04-00 §P02, 05-06 §9, 05-06 NFR-016, 05-06 NFR-074, BN-006, BN-007, VB-003, CG-010, CG-011]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: VB-009_Bengali_Typography_and_Brand_Standard_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards — bn-BD primary, UTF-8, ICU bn-BD collation, lakh/crore grouping, DD/MM/YYYY, Bengali month names, printing verified on all supported printers
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P02 non-negotiable requirements 3 and 4 — complete Bengali UI including error messages; runs acceptably on a mid-range Android 11 device with 3 GB RAM
    verified: 2026-08-15
    class: P1
  - source: 1000_fix_corporate_website project_content CB-001 §4.2 Bengali typeface Hind Siliguri; BN-010 design system reference — Inter 1.6 line height, Hind Siliguri 1.7
    verified: 2026-08-15
    class: P1
  - source: Hind Siliguri — Google Fonts family designed for UI, 820 glyphs including Bengali conjuncts; Noto Sans Bengali is the Android system default Bengali face
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# VB-009 — Bengali Typography and Brand Standard

> **This is a `P0` file for a physical reason.** Bengali is written with conjunct consonants
> (যুক্তাক্ষর) — stacked and fused letterforms — and with matras that sit above and below the
> baseline. At small sizes on a low-density screen, those strokes merge into an unreadable blur
> before the Latin equivalent shows any strain.
>
> `P02` must run on a **mid-range Android 11 device with 3 GB RAM**, used outdoors, by 200–400
> technicians, in Bengali, completely. **Typography is the difference between that application
> being used and being abandoned.**

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Bengali typefaces, minimum sizes, line heights, numerals, mixed-script rules and rendering verification across screen, print and email |
| **What it does not govern** | Which content is Bengali (`CG-010`); translation quality (`BN-002`, `BN-018`); terminology (`BN-003`); formats for date, number and currency (`BN-007`) |
| **What breaks without it** | An illegible technician application, truncated labels, broken conjuncts on branch printers, and a Bengali-first product that is harder to read than its English toggle |

**Relationship to `BN-006`.** `BN-006` is the localisation-owned Bengali typography standard.
This file is the **brand and design-system** view of the same subject — the token values, the
brand relationship, the surface application. They are ratified together and must not diverge
(`CP-01`). Where they do, `BN-006` governs linguistic and script questions; `VB-009` governs
brand and token questions.

---

## 2. Typefaces

### 2.1 The stack

```css
/* Bengali */
font-family: 'Hind Siliguri', 'Noto Sans Bengali', 'Nirmala UI',
             'SolaimanLipi', 'Vrinda', sans-serif;

/* Latin, within Bengali content */
font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
```

| Rank | Face | Source | Conjunct quality | Where it wins |
|---|---|---|---|---|
| 1 | **Hind Siliguri** | Google Fonts; bundled in apps, web font on portals | **Excellent** — 820 glyphs, designed for UI, humanist monolinear strokes with clear counters | Everywhere it loads |
| 2 | **Noto Sans Bengali** | **Android system default** | Good | The realistic majority fallback on Android and in email |
| 3 | Nirmala UI | Windows system | Acceptable | Outlook desktop, branch Windows machines |
| 4 | SolaimanLipi | Widely installed in Bangladesh | Good | Local desktops |
| 5 | Vrinda | Older Windows | Poor conjuncts; legible | Last resort |
| 6 | `sans-serif` | Anything | May render conjuncts as boxes | Failure case |

| # | Rule |
|---|---|
| **TF-01** | **Hind Siliguri is the brand Bengali face.** It is chosen to pair with Inter in weight and rhythm (`CB-001` §4.2) |
| **TF-02** | `P02`, `P09` and `P11` **bundle** Hind Siliguri in the application package. They do not rely on a web font or the system face — a technician offline for 24 hours cannot download a font |
| **TF-03** | Web portals load Hind Siliguri with `font-display: swap` and the fallback stack above |
| **TF-04** | Email **designs at rank 2** (`VB-005` BF-01). Custom fonts load reliably only in Apple Mail |
| **TF-05** | PDFs **embed** Hind Siliguri (`VB-004` T-02). A statutory document that substitutes a font is not the document we issued |
| **TF-06** | Never mix two Bengali faces on one surface |
| **TF-07** | Weight is limited to 400, 500, 600 and 700. Hind Siliguri Light at small sizes loses conjunct strokes entirely |

### 2.2 Metric mismatch

Hind Siliguri and Noto Sans Bengali have different vertical metrics. A layout tuned to one
breaks on the other.

| # | Rule |
|---|---|
| **MM-01** | Line height is set so **both** faces fit — see §4 |
| **MM-02** | Never set a fixed pixel height on a container holding Bengali |
| **MM-03** | Vertical centring is on the **line box**, not the glyph box |
| **MM-04** | Every Bengali layout is checked at rank 1 **and** rank 2 before release |

---

## 3. Minimum sizes — the core constraint

**Bengali floors are higher than English floors. This is not negotiable and not a preference.**

| Context | English floor | **Bengali floor** | Rationale |
|---|---:|---:|---|
| Screen — body | 14px | **16px** | Conjunct stroke separation on a 1366×768 or mid-range mobile panel |
| Screen — dense table cell | 13px | **15px** | The most-compressed surface in the ERP |
| Screen — caption, hint, metadata | 12px | **14px** | Absolute screen floor |
| Screen — badge, chip | 12px | **14px** | |
| **`P02` / `P09` mobile body** | 15px | **17px** | Outdoors, in motion, low-density panel |
| **`P02` / `P09` safety and custody text** | — | **19px** | The content whose misreading is most costly |
| Print — body | 9 pt | **10 pt** | Branch laser and inkjet output |
| Print — table | 8 pt | **9 pt** | |
| Print — legal | 7 pt | **8 pt** | Absolute print floor |
| **Thermal 80mm** | 9 pt | **11 pt** | 203 dpi, monochrome, no anti-aliasing |
| **Thermal 58mm** | 9 pt | **11 pt** | Test per printer model; some models cannot render conjuncts at all |
| Email — body | 15px | **16px** | Fallback-face-dependent |

| # | Rule |
|---|---|
| **MS-01** | **14px is the absolute Bengali screen floor. 8 pt is the absolute Bengali print floor.** No exception, no waiver |
| **MS-02** | A design that requires Bengali below its floor is a **design defect**, not a translation problem. Redesign the surface |
| **MS-03** | Where an English and a Bengali element sit side by side, the Bengali sets one step larger **or** at its floor, whichever is larger |
| **MS-04** | `P02` safety and custody content at 19px is not compressed to fit. It is the one place where content length yields to size, not the reverse |
| **MS-05** | Zoom and browser text-scaling must not break Bengali layout up to 200% (WCAG SC 1.4.4) |

---

## 4. Line height and spacing

Bengali needs more vertical room than Latin. Matras above and below the baseline collide at
Latin line heights.

| Context | English | **Bengali** |
|---|---:|---:|
| Body prose | 1.6 | **1.7** |
| Dense table row | 1.4 | **1.55** |
| Headings | 1.3 | **1.4** |
| Buttons and badges | 1.2 | **1.35** |
| Print body | 1.4 | **1.5** |
| Print table | 1.25 | **1.4** |

> The 1.6 / 1.7 pairing matches the existing design-system reference in the website content set,
> which is already in production for the corporate site. Adopting it here keeps one rhythm across
> both properties.

| # | Rule |
|---|---|
| **LH-01** | Line height is set **per language**, not once for the layout |
| **LH-02** | Letter-spacing on Bengali is **always zero**. Tracking separates conjunct components and destroys legibility |
| **LH-03** | Word-spacing is never adjusted. Bengali does not justify well |
| **LH-04** | Never justify Bengali text. Ragged right, always |
| **LH-05** | Paragraph spacing is at least 0.75 × line height |
| **LH-06** | WCAG text-spacing adjustment (SC 1.4.12) must not break the layout — verified, because Bengali layouts commonly fail this (`CG-011` BA-06) |

---

## 5. Numerals

**The decision is binary and it must be made once.**

| Option | Form | Argument for | Argument against |
|---|---|---|---|
| **Bengali numerals** | ০১২৩৪৫৬৭৮৯ | Culturally native; expected in Bengali prose | Transcription errors into government and bank systems; harder for mixed-script scanning; many Bangladeshi users read Arabic digits faster in a technical context |
| **Arabic numerals** | 0123456789 | Universal in Bangladeshi commerce, banking and statutory forms; no transcription risk; scans identically in both languages | Reads as less fully localised in prose |

### 5.1 The recommended policy

| Content | Numerals | Rationale |
|---|---|---|
| **Statutory documents** — Mushak forms, tax, filings | **Arabic** | Transcribed into government systems. Non-negotiable |
| **Money, anywhere** | **Arabic** | Financial transcription risk |
| **Identifiers** — references, IMEI, serials, part numbers, phone | **Arabic** | Read character by character; do-not-translate class (`BN-004`) |
| **Dates and times in data** | **Arabic** | DD/MM/YYYY per `05-06` §9 |
| **Quantities in tables** | **Arabic** | Column scanning |
| **Numbers in Bengali prose** | **Bengali** | Natural reading in help, training and knowledge content |
| **Dates in Bengali prose** | **Bengali**, with Bengali month names | `05-06` §9 permits Bengali month names in the Bengali locale |

| # | Rule |
|---|---|
| **NU-01** | **Never mix numeral systems within a single value.** "১২,500" is a defect |
| **NU-02** | Never mix within a single table column |
| **NU-03** | The policy above is **proposed**; `BN-007` is the authoritative decision and `CG-010` §12 item 3 records it as open. **Nothing may be authored to a different policy in the meantime** |
| **NU-04** | Number grouping is lakh/crore in the Bengali locale — 12,34,567 (`05-06` §9) — regardless of which numeral glyphs are used |
| **NU-05** | Currency is `৳` in the Bengali locale, `BDT` in the English locale, two decimals in both |

---

## 6. Mixed script

Bengali content routinely contains Latin: brand names, statutory form names, identifiers,
technical terms. This is normal and must be designed for.

| # | Rule |
|---|---|
| **MX-01** | Do-not-translate items stay in Latin script inside Bengali text (`BN-004`) — `Mushak 6.3`, `BIN`, `bKash`, `Samsung`, `SR-2026-114882` |
| **MX-02** | Latin inside Bengali is set in **Inter**, not in Hind Siliguri's Latin glyphs. The two faces are metric-compatible by design |
| **MX-03** | Latin inside Bengali sets **one step smaller** than the Bengali, because Inter's x-height is proportionally larger and unadjusted Latin looks oversized |
| **MX-04** | **Every script change is marked with a `lang` attribute** (WCAG SC 3.1.2, `CG-011` BA-02). Without it a screen reader pronounces "Mushak" with Bengali phonology |
| **MX-05** | Never transliterate a technical identifier into Bengali script |
| **MX-06** | Never force a line break inside a mixed-script phrase |
| **MX-07** | Bidirectional handling is not required — Bengali is left-to-right, like Latin |

---

## 7. Rendering verification

**The rule that catches what specification cannot.** Bengali conjunct rendering fails
differently on every engine, and the failures are only visible by looking.

| Surface | Verify on | When |
|---|---|---|
| Web portals | Chrome, Firefox, Safari, Edge — desktop and Android | Every release |
| `P02`, `P09`, `P11` | **A mid-range Android 11 device with 3 GB RAM**, the `P02` baseline | Every mobile release |
| `P01` app | Android and iOS, low and high density | Every app release |
| Email | Gmail Android, Gmail web, Outlook desktop, Apple Mail iOS | Every bilingual template |
| **Print** | **Every supported printer model** (`05-06` §9) | Before each `DT` release |
| **Thermal** | **Every supported thermal printer model** | Before each `DT` release |
| PDF | Adobe Reader, Chrome PDF, macOS Preview, Android PDF | Every `DT` release |

| # | Rule |
|---|---|
| **RV-01** | Verification is **visual inspection of rendered Bengali**, not a checkbox |
| **RV-02** | The check set includes a standard string containing the most demanding conjuncts — see §7.1 |
| **RV-03** | **A printer model that cannot render Bengali conjuncts does not issue Bengali documents.** The branch is issued a compliant model. The document is not silently downgraded to English |
| **RV-04** | Failures are recorded per model in a rendering register held by Platform Engineering |
| **RV-05** | A new device or printer model is verified before deployment, not after |

### 7.1 The conjunct test string

A standard string exercising demanding conjuncts, matras and mixed script. Used at every
verification point.

```
কার্যাদেশ · সার্ভিস সেন্টার · ট্রান্সমিশন · স্বাক্ষর · উদ্ভূত
বিদ্যুৎ · সংক্রান্ত · প্রয়োজনীয় · কর্তৃপক্ষ · দ্রষ্টব্য
Mushak 6.3 · BIN 001234567 · SR-2026-114882 · ৳ 12,34,567.00
```

| # | Rule |
|---|---|
| **CT-01** | Every glyph renders as a formed conjunct, not as separate letters with a visible virama |
| **CT-02** | No box, no tofu, no missing glyph |
| **CT-03** | Matras above and below do not clip at the line box edge |
| **CT-04** | Latin renders in Inter and sits on the same baseline |
| **CT-05** | The currency symbol and lakh/crore grouping render correctly |

---

## 8. Bengali and the brand

| # | Rule |
|---|---|
| **BR-01** | The 1000FiX wordmark is **never** transliterated into Bengali script. It is a mark, not a word (`BN-004`) |
| **BR-02** | The tagline may exist in Bengali as an approved translation, registered in `VB-010` |
| **BR-03** | Bengali and English lock-ups place Bengali first on Bengali-default surfaces |
| **BR-04** | Bengali headline type does not use the brand's expressive treatments — no tight tracking, no condensing, no outline. Bengali does not survive them (`LH-02`) |
| **BR-05** | Brand colour rules are unchanged by language. `VB-003` §3 contrast findings apply identically |
| **BR-06** | Bengali is never rendered as an image to guarantee a font (`CG-011` AT-07, `VB-005` BF-05) |

---

## 9. Accessibility

| # | Rule | SC |
|---|---|---|
| **AC-01** | Page and document language declared as `bn-BD` | 3.1.1 |
| **AC-02** | Every script change marked with `lang` | **3.1.2** |
| **AC-03** | Contrast requirements are unchanged by script | 1.4.3 |
| **AC-04** | Text resizes to 200% without loss of content or function | 1.4.4 |
| **AC-05** | WCAG text-spacing adjustment does not break Bengali layout — explicitly verified | 1.4.12 |
| **AC-06** | Screen-reader testing includes a Bengali-speaking tester with real assistive technology (`CG-011` §8.2, `TS-016`) | — |
| **AC-07** | Bengali screen-reader engine limitations are recorded in the accessibility statement, not silently accepted (`CG-011` §8.2) | — |

---

## 10. Do and do not

| Do not | Do |
|---|---|
| Set Bengali at the English minimum size | Use the Bengali floor from §3 |
| Use one line height for both languages | Set per language: 1.6 / 1.7 |
| Apply letter-spacing to Bengali | Zero tracking, always |
| Justify Bengali text | Ragged right |
| Set a fixed height on a Bengali container | Let it grow |
| Rely on a web font in `P02` | Bundle Hind Siliguri in the package |
| Mix Bengali and Arabic numerals in one value | Follow `BN-007`; never mix within a value |
| Transliterate `Mushak 6.3` | Keep it in Latin, marked with `lang` |
| Render Bengali as an image | Real text, always |
| Assume conjuncts render because the spec says so | Look at it, on the device, on the printer |
| Downgrade a Bengali document to English because a printer cannot render it | Replace the printer |

---

## 11. Dependencies

| Depends on | Why |
|---|---|
| `BN-006` Bengali Typography, Font and Numeral Standard | The localisation-owned counterpart; ratified together |
| `BN-007` Date, Time, Number, Currency and Address Formats | The authoritative numeral decision |
| `BN-004` Do-Not-Translate and Transliteration Register | `MX-01`, `BR-01` |
| `CG-010` | Which surfaces are Bengali; the open register decision |
| `VB-003` | Type scale this file raises for Bengali |
| `VB-004`, `VB-005` | Print and email application |
| `05-06` §9 | Locale standards, printer verification obligation |

---

## 12. Enforcement

| Check | Mechanism | When |
|---|---|---|
| Bengali below its floor | Automated token and CSS lint | Every commit |
| Letter-spacing applied to Bengali | Automated | Every commit |
| Fixed height on a Bengali container | Automated | Every commit |
| Line height set per language | Automated | Every commit |
| `lang` attribute on script changes | Automated | Every commit |
| Font embedded in PDF | Automated | Every render |
| Font bundled in `P02` / `P09` / `P11` package | Build check | Every mobile release |
| Conjunct test string renders correctly | **Visual, per surface and per printer model** | Every release |
| Text at 200% zoom | Visual regression | Every release |
| Text-spacing adjustment | Visual regression | Every release |
| Bengali screen-reader pass | `TS-016` with a Bengali-speaking tester | Before each portal release |

---

## 13. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per design-system release |
| Out-of-cycle trigger | A new device or printer model; a font update; a `BN-006` or `BN-007` decision; a rendering defect in production |
| Owner | Brand Lead with Localisation Lead |
| Rendering register | Held by Platform Engineering, one row per device and printer model |
| Bengali counterpart | `VB-009_Bengali_Typography_and_Brand_Standard_BN.md` — required, not yet written |
| Open dependency | `BN-007` numeral decision — §5.1 is proposed, not decided |

---

## 14. Related documents

| Document | Relationship |
|---|---|
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](VB-003_Brand_Application_in_Enterprise_UI.md) | The English type scale this raises |
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](VB-004_Print_and_PDF_Brand_Template_Standard.md) | Print sizes and printer verification |
| [`VB-005_Email_Brand_Template_Standard.md`](VB-005_Email_Brand_Template_Standard.md) | The email font stack |
| [`VB-007_Iconography_and_Label_Pairing_Register.md`](VB-007_Iconography_and_Label_Pairing_Register.md) | Bengali label width allowances |
| [`VB-010_Product_Plan_and_Programme_Naming_Standard.md`](VB-010_Product_Plan_and_Programme_Naming_Standard.md) | `BR-02` tagline and product names in Bengali |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | `BC-04`, `BC-06`, `BC-07` |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §9 |
| `BN-006` Bengali Typography, Font and Numeral Standard | The localisation counterpart |
| `BN-007` Date, Time, Number, Currency and Address Formats | The numeral decision |
| `TS-016` Accessibility Test Script Pack | Where §12 screen-reader checks run |

---

## 15. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six-rank font stack with bundling rules, Bengali minimum sizes per context with absolute floors, per-language line heights, proposed numeral policy pending `BN-007`, mixed-script rules with `lang` marking, rendering verification with a conjunct test string and the replace-the-printer rule | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Font stack ranked with the realistic fallback identified, not only the ideal
- [x] Minimum sizes stated per context with absolute floors declared unwaivable
- [x] Line heights stated per language, reconciled to the existing design-system reference
- [x] Numeral policy proposed with the decision correctly deferred to `BN-007` and marked open
- [x] Mixed-script `lang` marking required, with the screen-reader consequence stated
- [x] Rendering verification specified as visual inspection with a reusable test string
- [x] The replace-the-printer rule stated rather than allowing a silent English downgrade
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off in context — **outstanding; blocks `Approved`**
- [ ] `BN-007` numeral decision — **outstanding; §5.1 proposed only**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
