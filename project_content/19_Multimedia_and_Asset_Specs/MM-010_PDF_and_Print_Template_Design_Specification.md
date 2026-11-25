---
id: MM-010
title: PDF and Print Template Design Specification
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead with Platform Engineering
author: Brand with Platform Engineering, Enterprise Architecture, Finance and Localisation
reviewers: [Brand Lead, Chief Technology Officer, Enterprise Architecture, Finance, Tax, Legal Counsel, Localisation Lead, Accessibility reviewer, Quality Manager, Programme Content Lead]
approver: Content Design Lead with Brand Lead
content_class: D
purpose: >
  The specification that carries the print design intent to the rendering engine as values a build
  can consume — tokens, components, the pagination contract, font packaging, bilingual layout
  configuration, tagged-PDF structure and the specimen regression set. DT-001 states what a
  document template must say and VB-004 states how the page is built; between them sits a gap that
  every print programme falls into, where design intent reaches engineering as a reference PDF and
  is reimplemented by inference. Forty-four templates, twenty-six of them statutory, cannot be
  rendered from inference: a statutory block that splits across a page break, a substituted font
  in an archived invoice or a Bengali conjunct that breaks on one branch printer model are each
  a compliance defect rather than a visual one.
traces_to: [DT-001, DT-002, DT-010, DT-016, DT-031, DT-039, DT-041, DT-044, VB-003, VB-004, VB-009, MD-037, MD-039, MD-040, LG-009, LG-019, CG-006, CG-008, CG-010, CG-011, CG-012, BN-006, BN-015, RP-009, RP-014, AP-001, OP-014, MM-001, MM-003, MM-004, MM-012, TS-016, M24, 05-02 DM-11, 05-06 §9, 05-06 §11, 05-06 NFR-073]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md §3 output formats and F-01…F-04, §4 A4 zone geometry and G-01…G-06, §5 brand furniture, §6 print type scale and T-01…T-07, §7 bilingual layout patterns and BL-01…BL-08, §8 statutory yield S-01…S-08, §9 thermal TH-01…TH-08, §10 PDF accessibility AC-01…AC-07, §13 enforcement
    verified: 2026-08-18
    class: P1
  - source: project_content/05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md §2 the statutory evidence obligation and Tier S, §3 L-01…L-05 layout declarations, §4 FM-01…FM-06 field mapping, §5.1 RC-01…RC-07 reprint copy and void, §9 numbering and retention, §9.3 the re-render prohibition, §12 the eleven-section DT spine
    verified: 2026-08-18
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md §3 Bengali print floors — body 10 pt, table 9 pt, legal 8 pt, thermal 11 pt; §4 print line heights 1.5 and 1.4; TF-05 PDFs embed Hind Siliguri; §7 rendering verification per printer model and the conjunct test string
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 localisation standards — A4 and thermal receipt formats, DD/MM/YYYY, lakh and crore grouping, Bengali rendering verified on all supported printers; §11 accessibility scan and manual audit cadence; 05-02 §1 DM-11 branch- and business-line-aware document sequences
    verified: 2026-08-18
    class: P1
  - source: W3C Web Content Accessibility Guidelines (WCAG) 2.1 — SC 1.1.1 non-text content, SC 1.3.1 info and relationships, SC 1.3.2 meaningful sequence, SC 1.4.5 images of text, SC 3.1.1 language of page, SC 3.1.2 language of parts
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# PDF and Print Template Design Specification

| Item | Value |
|---|---|
| Governs | The renderable specification behind all 44 `DT` templates and every PDF the ERP produces |
| Content authority | [`DT-001`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) — what a template must **say** |
| Visual authority | [`VB-004`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) — how the page is **built** |
| This file | **What the engine is given.** Tokens, components, pagination, fonts, structure, specimens |
| Audience | Platform Engineering, the print-engine implementer, Brand, Finance, Localisation |
| Language | English — the specification. **34 of the 44 templates it renders are bilingual** (`CG-010` §3.2) |
| Wave | W1 · Months 1–4 (`06-01` §3) — **and all 44 `DT` templates were authored before it. See `O-01`** |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** is §4.9.
> §7 Open Items added per category convention.

---

## 1. Purpose

`VB-004` §15 names this file as *"the design deliverable this standard is implemented as"* and
`DT-001` §10 as *"the design deliverable that implements this standard."* Both are correct and
neither is sufficient on its own, because **the failure mode is the handover between them.**

> **The register's own justification is the sentence to build against: "the design intent must
> reach the rendering engine as a specification, not as a reference PDF."**

| Handover artefact | What engineering infers | What breaks |
|---|---|---|
| A reference PDF | Margins by measuring pixels; type sizes by eye | Every template drifts a millimetre per implementer |
| A design tool file | Geometry, but not behaviour | Pagination, overflow and the statutory-block rule are invented |
| Prose in `VB-004` | Correct values, no machine contract | Values are re-typed per template and diverge |
| **This file** | **Named tokens, a component inventory, an explicit pagination contract, a font package and a regression set** | — |

**The specific consequences this file prevents**, each of which is a compliance defect rather than
a visual one:

| Defect | Rule breached | Consequence |
|---|---|---|
| A statutory block splits across a page break | `VB-004` `G-04` | The declaration is incomplete on the page it is read on |
| A font substitutes in an archived PDF | `VB-004` `T-02`, `VB-009` `TF-05` | *"A statutory document that renders in a substituted font is not the document we issued"* |
| A Bengali conjunct breaks on one printer model | `VB-009` `RV-03`, `05-06` §9 | The branch cannot issue a Bengali document |
| `Page n of m` missing on a two-page invoice | `VB-004` `G-02` | *"A statutory document without it cannot be shown to be complete"* |
| A screen PDF used for statutory archive | `VB-004` `F-02` | Five-year retention on a non-archival format |
| A re-render served instead of the issued file | `DT-001` §9.3 | **A different document with the same number** |

**Consequence of absence (`CP-03`).** Forty-four templates — twenty-six content class `A` — each
implemented from inference by whichever engineer picked it up, in a programme where `CG-007` gate
`G6` requires the **rendered output** to be verified against the instrument, not only the
specification.

**What this file is not.** It is not `VB-004` (it consumes it), not `DT-001` (it consumes it), not
the templates themselves, not the label payload contract (`DT-044`), and not a product choice —
§4.1 states engine requirements, not a vendor.

---

## 2. Scope

**In scope.** The three-layer model and this file's position in it; the print token set; the
component inventory; the pagination and overflow contract; font packaging and embedding; bilingual
layout as engine configuration; thermal as a separate render path; watermark, reprint and void
implementation; tagged-PDF and PDF/A-3 output; the specimen and regression set; the deliverable
specification; and rules `PT-01`…`PT-32`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| What a template must state, its sections, its statutory evidence table | [`DT-001`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) |
| Page geometry in millimetres, type scale in points, bilingual patterns, thermal constraints | [`VB-004`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) — **this file encodes them; it does not re-decide them** |
| Bengali minimum sizes, line heights and rendering verification | [`VB-009`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md), [`BN-006`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) |
| Document sequences and numbering masks | [`MD-040`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) |
| Rounding, currency and number formatting | [`MD-039`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) |
| Retention periods and archive obligations | [`LG-009`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) |
| E-signature evidence | [`LG-019`](../10_Legal_Policy_and_Compliance/LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md), `M24` |
| Barcode and QR payload | [`DT-044`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) |
| Export watermarking of reports and dashboards | [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) |
| Statutory report formats | [`RP-009`](../14_Reporting_Analytics_and_KPI/RP-009_Statutory_and_Regulatory_Report_Format_Register.md) |
| Icons appearing on a document | [`MM-004`](MM-004_Icon_Set_Requirements.md) |
| Naming and versioning of the specimen assets | [`MM-012`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Print-engine implementer** | The values, tokens and behaviours to build | Before implementation |
| **Platform Engineering** | Font packaging, PDF/A-3 output, the regression harness | Continuously |
| **`DT` template authors** | What their template may declare, and what the engine already provides | Per template |
| **Brand Lead** | That the intent survived implementation | At each release |
| **Finance and Tax** | That statutory layout is reproduced, not approximated | At `G6` |
| **Localisation Lead** | §4.6, and the per-printer verification obligation | Per `DT` release |
| **Accessibility reviewer** | §4.8 tagged PDF and reading order | At each `DT` release |

---

## 4. Content

### 4.1 The three-layer model

| Layer | File | Answers | Example |
|---|---|---|---|
| **Content** | `DT-001` + the 43 templates | *What must this document say?* | "A Mushak 6.3 states supplier BIN, buyer BIN, description, quantity, unit price, value and VAT amount" |
| **Visual** | `VB-004` | *How is the page built?* | "Header zone 25 mm; body 9 pt; statutory block never splits" |
| **Renderable** | **`MM-010`** | *What is the engine given?* | `--doc-zone-header: 25mm`; `keep-together: statutory-block`; `font-embed: full-subset` |

| # | Rule |
|---|---|
| **PT-01** | **This file re-decides nothing.** Every value here traces to a `VB-004` or `VB-009` rule identifier. Where they differ, **`VB-004` and `VB-009` govern and this file is corrected** — never the reverse |
| **PT-02** | **A value that appears in no upstream file is a defect in this file**, and is raised to `VB-004` rather than settled here |
| **PT-03** | **The engine is given values, not a picture.** A reference PDF may accompany the specification as a check; **it is never the specification** |
| **PT-04** | **Engine requirements, not an engine choice.** §4.2's requirements are testable against any candidate; the selection is a Platform Engineering decision logged in [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) |

### 4.2 Engine requirements

The rendering engine must demonstrably support all of these. **A candidate failing any one is not
viable**, and the reason is stated so the requirement is not traded away.

| # | Requirement | Because |
|---:|---|---|
| 1 | **Full font embedding, no subsetting on Bengali** | Conjunct coverage; `VB-009` `TF-05` |
| 2 | **Complex-script shaping** (OpenType, Bengali conjunct and matra positioning) | `VB-009` §7 — the failure is invisible until rendered |
| 3 | **`keep-together` on an arbitrary block** | `VB-004` `G-04` statutory block never splits |
| 4 | **Repeating table headers across pages** | `VB-004` `G-06` |
| 5 | **`page n of m` with a known total** | `VB-004` `G-02` — requires a two-pass render |
| 6 | **Widow and orphan control** | `VB-004` `G-05` totals never alone on a continuation page |
| 7 | **PDF/A-3 output with embedded fonts and colour profile** | `VB-004` `F-02`, `S-08`; five-year statutory retention |
| 8 | **Tagged PDF with a structure tree and explicit reading order** | `VB-004` `AC-01`, `AC-07`; `CG-011` |
| 9 | **Per-element language tagging** | `VB-004` `AC-02`; WCAG SC 3.1.2 |
| 10 | **Monochrome 1-bit output path for thermal** | `VB-004` `TH-02` |
| 11 | **Deterministic output** — same input, byte-comparable output | §4.10 regression testing |
| 12 | **Two independent render paths are not permitted** | One engine for A4/PDF; thermal is a separate path by design (§4.7), and **no third** |

### 4.3 The print token set

**Named values the engine consumes.** Every token carries its authority.

#### 4.3.1 Geometry — A4 (`VB-004` §4)

| Token | Value | Authority |
|---|---|---|
| `doc-page-a4` | 210 × 297 mm | `VB-004` §3 |
| `doc-margin` | **15 mm** all sides | `VB-004` §4 |
| `doc-margin-bound` | **20 mm** left where filed in a binder | `VB-004` §4 |
| `doc-zone-header` | **25 mm** | `VB-004` §4 |
| `doc-zone-party` | **30 mm** | `VB-004` §4 |
| `doc-zone-body-min` | **100 mm** on the first page | `VB-004` §4 |
| `doc-zone-summary` | **25 mm** | `VB-004` §4 |
| `doc-zone-signature` | **30 mm** | `VB-004` §4 |
| `doc-zone-footer` | **12 mm** | `VB-004` §4 |
| `doc-rule` | **1 pt `#E9ECEF`**; header rule `#1E5F8A` | `VB-004` §5 |
| `doc-logo-width` | **18 mm**, top-left of header | `VB-004` §5 |
| `doc-qr-min` | **20 mm** square with quiet zone | `VB-004` `TH-06`, `DT-044` `L-44-c` |

#### 4.3.2 Type (`VB-004` §6, Bengali floors `VB-009` §3)

| Token | English | **Bengali** | Weight | Leading EN / **BN** |
|---|---:|---:|---:|---:|
| `doc-title` | 14 pt | 14 pt | 700 | 1.2 / **1.3** |
| `doc-subtitle` | 11 pt | 11 pt | 600 | 1.3 / **1.4** |
| `doc-section` | 10 pt | 10 pt | 600 | 1.3 / **1.4** |
| `doc-body` | **9 pt** | **10 pt** | 400 | 1.4 / **1.5** |
| `doc-table` | **8 pt** | **9 pt** | 400 | 1.25 / **1.4** |
| `doc-table-header` | 8 pt | 9 pt | 600 | 1.25 / **1.4** |
| `doc-numeric` | 9 pt | 9 pt | 500 | 1.25 / 1.25 |
| `doc-legal` | **7 pt** | **8 pt** | 400 | 1.3 / **1.5** |
| `doc-caption` | 7 pt | 8 pt | 400 | 1.3 / **1.5** |
| `doc-thermal` | 9–11 pt | **11 pt** | 400/700 | 1.3 / **1.5** |

| # | Rule |
|---|---|
| **PT-05** | **7 pt English and 8 pt Bengali are absolute floors. The engine rejects a render below them** (`VB-004` `T-01`, `VB-009` `MS-01` — *"no exception, no waiver"*) |
| **PT-06** | **Numerals are tabular figures, right-aligned, two decimals for money** (`VB-004` `T-03`, `MD-039`), and **statutory documents use Arabic numerals regardless of locale** (`VB-004` `BL-05`) |
| **PT-07** | **Identifiers are monospaced and never line-broken** (`VB-004` `T-04`, `DT-001` `FM-04`). They are transcribed by hand into government systems |
| **PT-08** | **Body text is never justified and never letter-spaced or condensed to fit** (`VB-004` `T-05`, `T-06`; `VB-009` `LH-02`, `LH-04`). The engine's auto-fit behaviour is **disabled**, because auto-fit is how a 9 pt body silently becomes 7.5 pt |
| **PT-09** | **Bengali sets one step larger than the English equivalent, or at its floor, whichever is larger** (`VB-004` `BL-03`, `VB-009` `MS-03`) |
| **PT-10** | **Line height is set per language, not once for the layout** (`VB-009` `LH-01`) |

#### 4.3.3 Colour

| Token | Value | Rule |
|---|---|---|
| `doc-ink` | `#212529` | All text |
| `doc-ink-muted` | `#495057` | Captions, footer |
| `doc-rule-light` | `#E9ECEF` | Dividers |
| `doc-rule-brand` | `#1E5F8A` | Header rule only |
| `doc-watermark` | `#E9ECEF`, 45° | `VB-004` §5 |
| **Fills, tints, gradients** | **None** | `VB-004` §5 — *"they consume toner and photocopy as grey"* |
| **`#39B1DF`** | **Not used on any document** | `VB-004` §11; 2.46:1 |

### 4.4 Component inventory

The engine provides these; a template composes them and **does not draw its own** (`PT-11`).

| # | Component | Behaviour |
|---:|---|---|
| **C1** | **Header** | Logo left, title right, entity line, BIN, address. **Repeats on every page** (`G-01`) |
| **C2** | **Party block** | Two columns: counterparty left, document metadata right. Field set declared per template (`DT-001` §3) |
| **C3** | **Line-item table** | Column set declared; **header repeats** (`G-06`); carry-forward subtotal and "continued" marker (`L-03`) |
| **C4** | **Summary / totals** | Right-aligned, tabular. **Never alone on a continuation page without the last two line items** (`G-05`) |
| **C5** | **Statutory block** | Verbatim declarations. **`keep-together`, never splits** (`G-04`) |
| **C6** | **Signature zone** | Present only where a signature is captured or expected; **removed, not left empty** (`DT-001` `SG-05`) |
| **C7** | **Footer** | Page n of m, document reference, hotline 16743. **Every page** (`G-01`, `G-03`) |
| **C8** | **Machine-readable zone** | QR/barcode per `DT-044`; **payload never defined here** (`DT-001` `L-05`) |
| **C9** | **Watermark** | `DRAFT`, `COPY`, `VOID`, `SPECIMEN` only; behind content; **never obscuring a statutory field** (`RC-07`) |
| **C10** | **Bilingual pair** | Stacked, parallel-column or separate-page, per template declaration (`BL-01`) |
| **C11** | **Continuation marker** | "Continued on page n" where a table breaks |
| **C12** | **Blocking-field guard** | **A blank required field blocks the render; it does not print an empty box** (`DT-001` `FM-05`) |

| # | Rule |
|---|---|
| **PT-11** | **A template composes components; it never draws primitives.** A template that positions its own rules and boxes has forked the standard |
| **PT-12** | **A zone not used is declared "not used", not omitted** (`DT-001` `L-02`) |
| **PT-13** | **`C12` is a hard block.** `FM-05`'s empty-box failure is how an incomplete statutory document reaches a customer looking complete |

### 4.5 The pagination contract

**The section most often left to the engine's defaults, and the one where defaults are wrong.**

| # | Rule | Authority |
|---|---|---|
| **PT-14** | **Header and footer repeat on every page.** *"A page 3 that cannot be identified is a lost page"* | `G-01` |
| **PT-15** | **`Page n of m` on every multi-page document**, requiring a two-pass render | `G-02` |
| **PT-16** | **The document reference appears in the footer of every page** | `G-03`, `MD-040` |
| **PT-17** | **The statutory block never splits. If it does not fit, it moves whole to the next page** | `G-04` |
| **PT-18** | **Totals never appear alone on a continuation page without at least the last two line items above them** | `G-05` |
| **PT-19** | **Table header rows repeat on every page** | `G-06` |
| **PT-20** | **Overflow behaviour is declared per template** — repeat header, carry-forward subtotal, continuation marker | `DT-001` `L-03` |
| **PT-21** | **Widows and orphans are suppressed** at two lines minimum |
| **PT-22** | **Pagination is tested at the maximum line-item count**, not at a typical one. `DT-001` `WE-02` requires a class `A` specimen *"with the maximum line-item count, to prove the statutory block does not split"* |

### 4.6 Fonts and bilingual layout

#### 4.6.1 Font packaging

| # | Rule |
|---|---|
| **PT-23** | **Inter (Latin) and Hind Siliguri (Bengali) are embedded, fully, in every PDF** (`VB-004` `T-02`, `VB-009` `TF-05`) |
| **PT-24** | **Bengali is not subsetted.** Subsetting drops glyphs the renderer did not see in this document and breaks a conjunct that appears in the next one. **Full embedding, always** |
| **PT-25** | **Latin inside Bengali is set in Inter, one step smaller** (`VB-009` `MX-02`, `MX-03`), and **every script change carries a language tag** (`MX-04`, WCAG SC 3.1.2) |
| **PT-26** | **Font licences permit embedding**, and the evidence is held (`MM-001` `DL-03`) |
| **PT-27** | **The engine's font-fallback chain is disabled for these two faces.** A silent fallback is exactly the failure `T-02` describes — *"a statutory document that renders in a substituted font is not the document we issued"* |

#### 4.6.2 Bilingual layout as configuration

`VB-004` §7 defines three patterns; the engine implements them as configurations, not as
per-template layout code.

| Pattern | Engine configuration | Rule |
|---|---|---|
| **Stacked** | Two text runs, Bengali first on Bengali-default surfaces, English in `doc-caption` | `BL-01` per template |
| **Parallel columns** | Two columns, **Bengali left, English right**, aligned at paragraph level | `BL-01` |
| **Separate pages** | Bengali page set then English page set, each complete, with a precedence clause | `BL-07` — **pending Legal** |

| # | Rule |
|---|---|
| **PT-28** | **Column widths are computed from the Bengali, not the English** (`BL-02`) — Bengali runs 20–40% longer, and a column sized for English truncates or overflows |
| **PT-29** | **Reading order is explicitly set for parallel columns** (`VB-004` `AC-07`), which *"commonly interleave wrongly"* — the single most common tagged-PDF defect in a bilingual document |
| **PT-30** | **Where a statutory instrument prescribes a language, that language is used exactly** (`BL-06`). The engine does not add a parallel translation to a prescribed form |

### 4.7 Thermal — a separate render path

| # | Rule | Authority |
|---|---|---|
| **PT-31** | **Thermal is a distinct render path**, not an A4 layout scaled down. Different components, different type, different dividers | `VB-004` §9 |
| **PT-32** | **Design for 58 mm and let 80 mm have margin** | `TH-01` |
| **PT-33** | **Monochrome 1-bit only. No greyscale — thermal greyscale is dithering and it smudges** | `TH-02` |
| **PT-34** | **Monospaced type, 9–11 pt English, 11 pt Bengali. Bold for emphasis; there is no italic** | `TH-03`, `VB-009` §3 |
| **PT-35** | **Logo as icon mark only, and only where legible at 203 dpi on that printer model** | `TH-04`, `MM-004` `IC-33` |
| **PT-36** | **Dividers are dashes, not rules** | `TH-05` |
| **PT-37** | **A receipt that must be retained states "Keep this receipt" and names the portal copy** — thermal paper fades | `TH-07` |
| **PT-38** | **A printer model that cannot render Bengali conjuncts does not issue Bengali receipts. The branch is issued a compliant model** — the document is **not** silently downgraded to English | `TH-08`, `VB-009` `RV-03` |

### 4.8 Tagged PDF, accessibility and archive

| # | Rule | SC / authority |
|---|---|---|
| **PT-39** | **Digital PDFs are tagged** — heading structure, reading order, table headers | `AC-01`, SC 1.3.1 |
| **PT-40** | **Document language declared; language changes marked** | `AC-02`, SC 3.1.1, 3.1.2 |
| **PT-41** | **Every image and logo carries a text alternative** | `AC-03`, SC 1.1.1 |
| **PT-42** | **Text is real text, never an image of text** | `AC-04`, SC 1.4.5 |
| **PT-43** | **Colour is never the only signal** | `AC-05`, SC 1.4.1 |
| **PT-44** | **The document title is set in PDF metadata**, not left as the file name | `AC-06` |
| **PT-45** | **Reading order verified for bilingual parallel columns** | `AC-07`, SC 1.3.2 |
| **PT-46** | **Class `A` templates archive as PDF/A-3 with embedded fonts at the moment of issue**, not on demand | `DT-001` `R-02`, `VB-004` `F-02` |
| **PT-47** | **The archived rendition is the evidential copy and is served on every subsequent request.** `DT-001` §9.3 — *"re-rendering an invoice from today's master data produces a different document with the same number"* |
| **PT-48** | **A draft, preview or specimen never consumes a statutory number** (`DT-001` `N-04`) and always carries its watermark (`RC-05`, `RC-06`) |

### 4.9 Deliverable specification

**The `CG-009` §3 required addition for Category 19.**

| Attribute | Specification |
|---|---|
| **Master deliverable** | **A token file + a component specification + a pagination contract**, in a machine-readable form the build consumes (`PT-03`) |
| **Derived formats** | Vector **PDF/X-4** or SVG for fixed artwork (logo lock-ups, watermarks, marks); **1-bit monochrome PNG** for thermal marks |
| **Dimensions** | Per §4.3.1, in **millimetres**, not pixels |
| **Colour** | `doc-ink` set; **no fills, tints or gradients**; monochrome for thermal; **no `#39B1DF`** |
| **Typography** | §4.3.2 in points, per language; **auto-fit disabled** |
| **Fonts** | **Inter + Hind Siliguri, fully embedded, unsubsetted, fallback disabled**, licences evidenced |
| **Output** | Screen PDF (tagged) · **PDF/A-3 archive** (class `A`) · thermal 1-bit |
| **Metadata** | PDF title, language, producer, `dc:relation` = owning `DT-` identifier, document reference from `MD-040` |
| **Naming** | `MM-012` §4.3 for specimen and artwork assets |
| **Regression set** | **§4.10 — the deliverable that proves the rest** |
| **Evidence** | Per-printer Bengali render results (`VB-009` §7); PDF/A-3 validation report; accessibility checker report; contrast and floor-size lint results |

### 4.10 The specimen and regression set

**Without this, none of the above is verifiable.**

| # | Specimen | Proves |
|---:|---|---|
| **R1** | A4 bilingual invoice at **maximum line-item count** | `PT-17` statutory block does not split; `PT-18`, `PT-19`, `PT-22` |
| **R2** | Multi-page document, 3+ pages | `PT-14`, `PT-15`, `PT-16` |
| **R3** | Parallel-column bilingual terms | `PT-28` column sizing; `PT-29`, `PT-45` reading order |
| **R4** | The `VB-009` §7.1 **conjunct test string** rendered at every type token | `PT-23`, `PT-24`, `PT-27`; `CT-01`…`CT-05` |
| **R5** | Prescribed-form document (Mushak 6.3, `DT-010`) | `VB-004` `S-01`…`S-03` — brand yields entirely |
| **R6** | Thermal 58 mm and 80 mm bilingual receipt | `PT-32`…`PT-38` |
| **R7** | Watermarked `DRAFT`, `COPY`, `VOID`, `SPECIMEN` variants | `RC-01`…`RC-07`, `PT-48` |
| **R8** | PDF/A-3 archive of R1 | `PT-46`; validation report |
| **R9** | Tagged-PDF accessibility pass of R1 and R3 | `PT-39`…`PT-45` |
| **R10** | Blank-required-field case | `PT-13` — the render **blocks** |

| # | Rule |
|---|---|
| **PT-49** | **The regression set runs on every engine change, every template change and every font update.** `PT-11`'s determinism requirement exists to make it comparable |
| **PT-50** | **R4 and R6 are physically printed on every supported printer model** (`VB-009` §7, `05-06` §9). This is **visual inspection of paper**, not a checkbox |
| **PT-51** | **Specimens are held in [`RF-009`](../99_Reference_and_Registers/RF-009_Sample_and_Reference_Data_Pack.md) Sample and Reference Data Pack** (`DT-001` §7, `WE-03`), watermarked `SPECIMEN`, on the reserved non-production sequence. **The pack exists; the R1–R10 specimens in it do not.** See `O-04` |
| **PT-52** | **A stale specimen is worse than none** (`DT-001` `WE-04`). Regenerated on every change |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | Every geometry, type, colour, bilingual, statutory and thermal value in §4.3–§4.8 |
| [`DT-001_Document_Template_Standard_and_Branding_Rules.md`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) | `L-01`…`L-05`, `FM-01`…`FM-06`, `RC-01`…`RC-07`, §9 numbering and retention, §9.3 the re-render prohibition |
| [`VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) · [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](../11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | Print floors, per-language line heights, full embedding, the conjunct test string, `RV-03` |
| [`BN-015_Bengali_Document_and_Print_Template_Pack.md`](../11_Localisation_Bengali/BN-015_Bengali_Document_and_Print_Template_Pack.md) | The Bengali template content this engine renders |
| [`VB-003_Brand_Application_in_Enterprise_UI.md`](../01_Voice_Brand_and_Design_Content/VB-003_Brand_Application_in_Enterprise_UI.md) | §3 contrast; the screen counterpart these tokens deliberately do not share |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) · [`DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) · [`DT-016_Payment_Receipt_and_Money_Receipt.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) · [`DT-041_Payslip_and_Salary_Certificate.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-041_Payslip_and_Salary_Certificate.md) | The reference cases R1, R5 and R6 are built from |
| [`DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Component C8; the payload this file never defines |
| [`MD-040_Document_Sequence_and_Numbering_Mask_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) · [`MD-039_Currency_FX_and_Rounding_Standard.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) · [`MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | The reference in every footer; number formatting; the tax point behind `TAX-04` |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md`](../10_Legal_Policy_and_Compliance/LG-019_ESignature_Legal_Notice_and_Evidence_Statement.md) | Archive format and retention; the signature evidence component C6 records |
| [`CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) · [`TS-016_Accessibility_Test_Script_Pack.md`](../13_Test_and_Acceptance_Content/TS-016_Accessibility_Test_Script_Pack.md) | §4.8 obligations and where R9 is executed |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | Fiscal-year pinning of statutory templates; MAJOR change handling |
| [`RP-009_Statutory_and_Regulatory_Report_Format_Register.md`](../14_Reporting_Analytics_and_KPI/RP-009_Statutory_and_Regulatory_Report_Format_Register.md) · [`RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Report output that shares this engine; export marking, which C9 must not conflict with |
| [`OP-014_Manual_Fallback_Procedure_Set.md`](../17_Operations_Support_and_Runbooks/OP-014_Manual_Fallback_Procedure_Set.md) | Print quality, media and the degraded-mode paper path (`DT-044` `PQ-03`) |
| [`AP-001_Developer_Portal_Information_Architecture.md`](../15_Integration_and_Developer_Content/AP-001_Developer_Portal_Information_Architecture.md) | Cites `MM-010` for developer-portal visual design |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) · [`MM-003_Diagram_and_Process_Map_Visual_Standard.md`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) · [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) · [`MM-012_Digital_Asset_Management_and_Naming_Standard.md`](MM-012_Digital_Asset_Management_and_Naming_Standard.md) | Class A11 artwork; diagrams in print; glyphs at 203 dpi; specimen naming |
| `05-02` `DM-11` · `05-06` §9, §11 | Branch-aware sequences; locale standards and printer verification; the accessibility test cadence |
| `M24` | Where issued and archived documents are retained |

| Depended on by |
|---|
| All 44 `DT` templates · the print engine build · `RP-009` and `RP-010` outputs · `BN-015` · `AP-001` · [`RF-009`](../99_Reference_and_Registers/RF-009_Sample_and_Reference_Data_Pack.md) specimen pack |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per `DT` release**; annually for the standard; **statutory templates follow `CG-006` §4.2** |
| Trigger for out-of-cycle review | A `VB-004` or `VB-009` change · a prescribed form changing · a new printer model · a font update · an engine upgrade · an accessibility finding · a failed regression |
| Owner | **Brand Lead with Platform Engineering.** Brand owns intent; Platform owns the implementation and the regression harness |
| Approver | Content Design Lead with Brand Lead (`CG-002` §5.4, class D) |
| Enforcement | `VB-004` §13's checks, extended: automated geometry lint, minimum-type-size lint, font-embedding inspection, PDF/A-3 validation, `page n of m` presence, statutory-block pagination test, tagged-PDF and reading-order check; **physical Bengali print test per printer model** |
| Effectiveness measure | **Regression failures per engine change**, and **`G6` rejections attributable to rendering rather than to content — target zero** |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **All 44 `DT` templates were authored before this specification existed.** Category 05 is complete at 44 of 44 and this file is registered at the same wave, W1; **each template's §3 layout declarations were therefore written against `VB-004` prose rather than against a component inventory.** A reconciliation pass is required — every template's declared zones, overflow behaviour and bilingual pattern checked against §4.4 and §4.6 — **before the engine is built, not after** | Programme Content Lead with Platform Engineering | **W1 — before implementation** |
| **O-02** | **No rendering engine is selected**, and §4.2 lists twelve requirements of which several — complex-script shaping with full Bengali embedding, `keep-together` on arbitrary blocks, two-pass `page n of m`, tagged PDF/A-3 with per-element language tagging, and deterministic output — **are jointly satisfied by very few engines.** The selection is a decision for [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md), which now exists and must carry it | Chief Technology Officer with Platform Engineering | **W1 — it gates 44 templates** |
| **O-03** | **No printer test set exists.** `VB-004` §14 assigns it to Platform Engineering and records it as outstanding; `MM-001` `O-07` and `MM-004` `O-06` record the same gap. **`PT-50` and `PT-38` cannot be executed without it**, and `VB-009` `RV-03`'s replace-the-printer rule cannot be applied to a model nobody has tested | Platform Engineering | **W1 — before the first `DT` release** |
| **O-04** | **[`RF-009`](../99_Reference_and_Registers/RF-009_Sample_and_Reference_Data_Pack.md) Sample and Reference Data Pack now exists** — Category 99 completed 2026-08-18 — and `PT-51` places the ten-specimen regression set there; `DT-001` §7 and `DT-044` §7 do the same for their own specimens. **The gap is no longer existence but content: none of the R1–R10 specimens has been produced, and none can be until `O-02`'s engine is selected.** `PT-52` makes a stale specimen worse than none | Programme Content Lead with Platform Engineering | **W1 — a production gap, no longer an existence gap** |
| **O-05** | **`VB-004` `BL-07` records the bilingual precedence clause as "pending Legal confirmation"**, and `CG-010` §4.1 open decision 2 asks whether English governs in a dispute. **§4.6.2's separate-pages pattern cannot be finalised until it lands**, and 34 templates are bilingual | Legal Counsel | **W1 — before the first bilingual `DT` release** |
| **O-06** | **`DT-001` §2.2 records that none of the fourteen Tier S instrument citations is verified**, and `PT-30`/`R5` require the engine to reproduce a prescribed form exactly. **A form reproduced faithfully from an unverified citation is faithfully wrong** — gate `G6` catches it, and this file's regression set cannot | Legal Counsel and Tax with external verification | **W1 — at `G6`** |
| **O-07** | **No accessibility reviewer is named** for §4.8 — the **eleventh** file to record it. **Tagged-PDF reading order in a bilingual parallel-column document is the single hardest accessibility check in the programme** and no one owns it | Content Design Lead | **W1** |
| **O-08** | **`AUDIT-013` `LG-01` records that `DT-031` maps nine `MD-028` fields that do not exist**, and gate `F3` fails today. **A render specification cannot fix a field-mapping defect**, but `PT-13`'s blocking-field guard will surface it as a blocked render at W1 rather than as a wrong document later — **which is the correct outcome and should be expected** | Programme Content Lead with Service Operations | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.9; §7 added per category convention
- [x] **The three-layer model stated, with this file re-deciding nothing and every value traced to `VB-004` or `VB-009`**
- [x] **Twelve engine requirements stated as testable capabilities with the reason for each, so none is traded away in selection**
- [x] Token set given in millimetres and points per language, with the Bengali floors carried as engine-enforced limits
- [x] **Auto-fit explicitly disabled, because auto-fit is how a 9 pt body silently becomes 7.5 pt**
- [x] Twelve components specified, with templates composing rather than drawing
- [x] **The pagination contract written out rather than left to engine defaults, including the two-pass `page n of m` requirement**
- [x] Maximum-line-item testing required, matching `DT-001` `WE-02`
- [x] **Full, unsubsetted Bengali embedding with font fallback disabled**
- [x] Bilingual layout expressed as three engine configurations with column sizing computed from the Bengali
- [x] **Reading order for parallel columns identified as the most common tagged-PDF defect and made an explicit check**
- [x] Thermal specified as a separate render path, with the replace-the-printer rule carried through rather than softened
- [x] **PDF/A-3 archive at issue, and the archived rendition served on every later request — the re-render prohibition carried from `DT-001` §9.3**
- [x] A ten-specimen regression set defined, with two specimens required to be physically printed on every printer model
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2; **34 of the templates it renders are bilingual**
- [ ] **`O-01` 44 templates authored before this specification — reconciliation pass outstanding**
- [ ] **`O-02` no engine selected — outstanding; it gates 44 templates**
- [ ] **`O-03` no printer test set — outstanding; `PT-50` unexecutable**
- [ ] **`O-05` bilingual precedence clause pending Legal — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Brand Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
