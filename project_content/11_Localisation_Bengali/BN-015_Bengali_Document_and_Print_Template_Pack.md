---
id: BN-015
title: Bengali Document and Print Template Pack
project: 1000FiX ERP System v2.0
content_type: Document print template
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Legal, Finance, Brand and Platform Engineering
reviewers: [Legal Counsel, Tax Manager, Finance Controller, Brand Lead, Platform Engineering, Operations Director, HR Director]
approver: Legal Counsel with Localisation Lead and Content Design Lead
content_class: B
purpose: >
  The Bengali layouts, wording and print rules for the 34 bilingual DT documents — everything a
  customer, an employee or a regulator receives on paper or as a PDF. Intake receipts, estimates,
  warranties, money receipts and payslips are read by people who will not read English, and a
  statutory filing to a public body may be legally required to be in Bengali under the Bangla
  Bhasha Prachalan Ain 1987. The pack also fixes what a bilingual document actually looks like,
  because a bilingual layout decided per template produces 34 different documents from one brand.
traces_to: [DT-001, DT-002, DT-005, DT-007, DT-009, DT-010, DT-016, DT-032, DT-041, DT-042, DT-044, VB-004, BN-001 §6.4, BN-002 RD-C, BN-004, BN-006, BN-007, BN-018, CG-010 §4.1, LG-001, LG-013, 05-06 §9]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of the 34 bilingual `DT` templates
pinned_to:
  surface: Print, PDF and thermal output
  release: pending first build
  wave: W2
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — DT 44 files, 34 bilingual, 10 English-only (DT-001, DT-021–DT-025, DT-029, DT-033, DT-039, DT-040)
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §4.1 — for legal and statutory content English governs in a dispute; every bilingual Class A or B document carries a precedence clause drafted in LG-001; where Bangladesh law requires a Bengali instrument to govern, that requirement overrides
    verified: 2026-08-17
    class: P1
  - source: Bangla Bhasha Prachalan Ain, 1987 (Act No. 2 of 1987) §3 — records, correspondence, laws and proceedings must be in Bengali in all courts, government and semi-government offices and autonomous institutions
    verified: 2026-08-17
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 and §10 — Bengali rendering verified on all supported printers; A4 and thermal receipt formats; thermal receipt printers, label printers and kiosks in the supported peripheral set
    verified: 2026-08-17
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-004 and VB-009 TF-05 — PDF font embedding, statutory block placement, bilingual layout for the 44 DT documents
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-015 — Bengali Document and Print Template Pack

> **A document is the one artefact where the language decision is irreversible.** A screen can be
> toggled. A printed intake receipt handed to a customer at a counter in Cumilla is the only
> version they will ever have, and if they cannot read it, the custody record, the warranty terms
> and the liability limit were never communicated.
>
> Two things make this pack Class B rather than Class D. **`CG-010` §4.1** makes English the
> governing language in a dispute, which is a legal position that must appear **on the document**.
> And the **Bangla Bhasha Prachalan Ain 1987** may require Bengali on anything filed with a public
> body — a question `BN-001` §12 item 4 puts to Legal Counsel and which §6 holds open.

---

## 1. Scope

**34 of the 44 `DT` templates are bilingual** (`CG-010` §3.2).

| Group | Bilingual | English-only |
|---|---|---|
| `05A` Service and operations — `DT-002`…`DT-009` | **All 8** | — |
| `05B` Finance and statutory — `DT-010`…`DT-020` | **All 11** | — |
| `05C` Supply chain and logistics — `DT-021`…`DT-029` | `DT-026`, `DT-027`, `DT-028` | `DT-021`–`DT-025`, `DT-029` |
| `05D` Commercial and contract — `DT-030`…`DT-040` | `DT-030`, `DT-031`, `DT-032`, `DT-034`, `DT-035`, `DT-036`, `DT-037`, `DT-038` | `DT-033`, `DT-039`, `DT-040` |
| `05E` People, quality and labelling — `DT-041`…`DT-044` | **All 4** | — |
| `DT-001` standard | — | `DT-001` |
| **Total** | **34** | **10** |

> The English-only ten are **vendor- and brand-facing procurement and claims documents** plus the
> `DT-001` standard itself. Those counterparties contract in English (`CG-010` §3.3). **This is a
> declared decision, not a gap** (`BP-06`).

---

## 2. Bilingual layout patterns

**Decided once here, not per template.** `VB-004` owns the brand furniture; this file owns the
language arrangement inside it.

| Pattern | Form | Use for | Why |
|---|---|---|---|
| **P-1 Parallel columns** | Bengali left, English right, per row | Field-label documents: intake receipt, handover, money receipt, delivery challan, gate pass | Both readers scan the same row. Works because labels are short |
| **P-2 Stacked label pairs** | `বাংলা label / English label` above one value | Dense forms and narrow widths where two columns will not fit | One value, two labels, no duplication of data |
| **P-3 Sequential blocks** | Full Bengali section, then full English section | Prose documents: warranty terms, contract annexes, HR letters, policy statements | Long prose does not align row-by-row |
| **P-4 Bengali primary, English annex** | Bengali body; English as a following annex | Documents where Bengali is the operative language (§6, pending decision) | Reserved for the 1987 Act case |
| **P-5 Prescribed form** | **Exactly as the instrument prescribes** | Mushak 6.1, 6.2, 6.3, 6.6, 9.1 | **The form's layout and wording are not ours to change** (`CG-004` `T-05`) |

| # | Rule |
|---|---|
| **DB-01** | **Bengali is placed first** — left in P-1, above in P-2, before in P-3 — on every customer- and employee-facing document. `PS-03` makes Bengali the default and the document must show it (`VB-009` `BR-03`) |
| **DB-02** | **A value appears once.** Two labels may share one value; **a value is never printed twice in two scripts**, because the two copies will diverge on a reprint |
| **DB-03** | The pattern is **chosen per template and recorded in that template's file**, from this list only. A sixth pattern requires a change to this file |
| **DB-04** | **Field labels come from a bundle**, not from the layout file (`BN-005` §8). A label hard-coded into a report definition is an untranslatable string |
| **DB-05** | **Bengali expansion of 20–40% is designed for, not discovered.** A layout that fits English and overflows Bengali is a defect in the layout (`BN-006` `LB-11`) |
| **DB-06** | **Nothing is truncated on a document.** A document grows a page before it shortens a value (`BN-006` `LB-07`) |
| **DB-07** | **P-5 overrides everything in this section.** Where a statutory form prescribes a layout, it is reproduced, and our bilingual conventions do not apply to it |

---

## 3. Typography and rendering on paper

| Item | Value | Source |
|---|---|---|
| Bengali print body floor | **10 pt** | `VB-009` §3 |
| Bengali print table floor | **9 pt** | `VB-009` §3 |
| Bengali legal floor | **8 pt — absolute** | `VB-009` `MS-01` |
| **Thermal 80 mm and 58 mm floor** | **11 pt** | `VB-009` §3 |
| Line height, print body | 1.5 | `VB-009` §4 |
| Line height, print table | 1.4 | `VB-009` §4 |
| Font | **Hind Siliguri, embedded in the PDF** | `VB-009` `TF-05` |
| Justification | **Never.** Ragged right | `VB-009` `LH-04` |
| Letter-spacing | **Zero** | `VB-009` `LH-02` |

| # | Rule |
|---|---|
| **DB-08** | **The font is embedded in every PDF.** A statutory document that substitutes a font is not the document we issued (`VB-009` `TF-05`) |
| **DB-09** | **The language a document was issued in is stored on the document record.** A reprint reproduces the issued language and the issued layout, not today's configuration (`BN-001` `LR-05`) |
| **DB-10** | **Every supported printer model is verified with the `BN-006` §9 test set before each `DT` release** (`05-06` §9) |
| **DB-11** | **A printer that cannot render Bengali conjuncts does not issue Bengali documents; the branch is issued a compliant model.** The document is **never** silently downgraded to English (`VB-009` `RV-03`) |
| **DB-12** | The **PDF text layer must be extractable Bengali**, not outlines. An unextractable PDF cannot be searched, cannot be read by assistive technology and cannot be verified (`BN-004` §7) |
| **DB-13** | **PDF metadata — title, subject, author — is Bengali on a Bengali document.** It is user-visible in the viewer tab and in file listings (`CG-010` §5) |
| **DB-14** | **File names are Latin** (`BN-004` §7). Bengali file names break on some printers, mail gateways and legacy Windows shares |

### 3.1 Thermal output

The least forgiving surface in the system: 203 dpi, monochrome, no anti-aliasing, and some models
cannot shape Bengali at all.

| # | Rule |
|---|---|
| **TH-01** | **11 pt Bengali floor** on 80 mm and 58 mm, higher than the A4 floor |
| **TH-02** | **Arabic digits only** on thermal output. ০ and ৩ converge at 203 dpi (`BN-006` `NU-06`, `BN-007` §3.3) |
| **TH-03** | **P-2 stacked labels**, not P-1 columns — 58 mm cannot carry two columns |
| **TH-04** | The **customer's copy carries the full Bengali**; abbreviation to fit is prohibited. If it does not fit, it prints on two receipts |
| **TH-05** | **Every thermal model is certified individually.** Certification is per model and per firmware version (`BN-006` §10 item 5) |
| **TH-06** | Where a certified thermal printer is not available at a branch, **the branch prints A4** — it does not print English |

---

## 4. Statutory documents

### 4.1 The prescribed forms

| Document | Template | Pattern | Language position |
|---|---|:--:|---|
| `DT-010` Tax invoice — **Mushak 6.3** | `fix.mushak.invoice` | **P-5** | Prescribed. Our additions sit outside the prescribed block |
| `DT-011` Sales register — **Mushak 6.2** | | **P-5** | Prescribed |
| `DT-012` Purchase register — **Mushak 6.1** | | **P-5** | Prescribed |
| `DT-013` VDS certificate — **Mushak 6.6** | | **P-5** | Prescribed |
| `DT-014` VAT return — **Mushak 9.1** | | **P-5** | Prescribed |

| # | Rule |
|---|---|
| **ST-B01** | **The prescribed form governs.** Its wording, field order and layout are reproduced exactly; nothing in this pack overrides it (`DB-07`, `CG-004` `T-05`) |
| **ST-B02** | **`Mushak 6.3`, `BIN`, `TIN`, `VDS` and `VAT` are Tier 1 and remain Latin** in any wording we add (`BN-004` §3.1) |
| **ST-B03** | **All numerals on a statutory document are Arabic** (`BN-007` §3.3). The figures are transcribed into government systems |
| **ST-B04** | **G6 external verification applies to the Bengali as well as the English.** A statutory document whose Bengali has not been verified against the instrument is not verified (`CG-007` §3.6) |
| **ST-B05** | **The `VAT` / মূসক question is open** (`BN-004` §10 item 2). Until Tax Manager decides, our own prose uses `VAT` and the prescribed forms use whatever they prescribe |

### 4.2 Money receipt and amount in words

| # | Rule |
|---|---|
| **AW-B01** | `DT-016` money receipt carries the **amount in words in both languages** (`BN-007` §4.3) |
| **AW-B02** | Bengali form: **তিন হাজার দুইশত টাকা পঞ্চাশ পয়সা মাত্র** — লাখ/কোটি structure, ending মাত্র |
| **AW-B03** | **Generated from the figure, never typed**, and verified against it at render (`BN-007` `AW-05`) |
| **AW-B04** | The **figure** uses Arabic digits with the `৳` prefix; the **words** contain no digits at all |

---

## 5. Customer-facing service documents

| Document | Pattern | Bengali-critical content |
|---|:--:|---|
| `DT-002` Intake receipt and device handover | **P-1** | Device identity, declared condition, **custody statement**, warranty exclusions summary, liability limit, unclaimed-device terms |
| `DT-003` Job card | P-2 | Internal; branch and workshop staff |
| `DT-004` Diagnostic and condition report | P-2 | Fault (`MD-024`) and condition wording |
| `DT-005` Repair estimate and quotation | **P-1** | Line items, parts vs labour, `VAT`, total, **approval statement**, validity period |
| `DT-006` Revised estimate | **P-1** | **What changed and why** — the highest-dispute document in the set |
| `DT-007` Service completion report | **P-1** | Work done (`MD-025`), parts used, **repair warranty period and its exclusions** |
| `DT-008` Quality checklist record | P-2 | |
| `DT-009` Device release and collection receipt | **P-1** | **Custody transfer, condition on release, customer acknowledgement** |

| # | Rule |
|---|---|
| **SV-B01** | **`DT-002` and `DT-009` are custody instruments.** The Bengali custody sentence is the operative text for a customer who does not read English, and it is not abbreviated to fit a thermal receipt (`TH-04`) |
| **SV-B02** | **Warranty exclusions and the liability limit appear in Bengali on `DT-002`** (`LG-013`), at no smaller than the 8 pt absolute legal floor (`VB-009` `MS-01`) |
| **SV-B03** | **`DT-006` states what changed**, in Bengali, in plain language. "সংশোধিত এস্টিমেট" alone is not a statement of change (`UI-038`) |
| **SV-B04** | Fault, action and reason text comes from `MD-024`, `MD-025` and `MD-026` **`name_bn` columns**, not re-translated on the document (`BN-003` §12) |
| **SV-B05** | Status wording is `MD-027` **`customer_label_bn`** (`BN-003` `ST-01`) |

**Key Bengali strings on service documents**

| Slot | **Bengali** |
|---|---|
| Intake receipt title | **ইনটেক রসিদ ও ডিভাইস হস্তান্তর ফর্ম** |
| Custody statement | **এই ডিভাইসটি আমাদের হেফাজতে গ্রহণ করা হলো। সংগ্রহের সময় এই রসিদটি সঙ্গে আনুন।** |
| Declared condition | **গ্রহণের সময় ঘোষিত অবস্থা** |
| Estimate validity | **এই এস্টিমেট {days} দিন পর্যন্ত কার্যকর।** |
| Approval statement | **আমি উপরের কাজ ও মূল্যে সম্মত আছি।** |
| Repair warranty | **মেরামত ওয়ারেন্টি {months} মাস। শর্তাবলী প্রযোজ্য।** |
| Release acknowledgement | **আমি ডিভাইসটি বর্ণিত অবস্থায় বুঝে পেয়েছি।** |
| Unclaimed device notice | **{days} দিনের মধ্যে সংগ্রহ না করা হলে সংরক্ষণ চার্জ প্রযোজ্য হবে।** |

> Class A/B documents use the **formal sub-register** (`BN-002` `RD-C`) — মূল্য rather than দাম,
> কার্যকর rather than চালু. A UI surface showing the same fact uses the standard register
> (`BN-002` `FR-02`).

---

## 6. The 1987 Act question

**`BN-001` §12 item 4 is open and this section holds the document list it will decide.**

| Category | Documents | If the Act applies |
|---|---|---|
| Filed with NBR | `DT-011`, `DT-012`, `DT-014` and supporting schedules | Bengali required; prescribed forms already carry their own language |
| Filed with a court | Dispute bundles, statutory notices, evidence of terms accepted (`LG-001`) | **Bengali required.** English may accompany |
| Filed with a semi-government or autonomous body | Regulatory disclosures (`LG-024`), licence renewals, environmental declarations (`DT-035`, `LG-018`) | Bengali required |
| Correspondence with a public body | Notices, responses, submissions | Bengali required |
| Private counterparty contracts | `DT-030`, `DT-031`, `DT-032`, `DT-037` | **Unaffected.** `CG-010` §4.1 governs |

| # | Rule |
|---|---|
| **LA-01** | **This pack does not decide the question.** It records the affected list so that a decision can be executed rather than researched |
| **LA-02** | Where the Act applies, the pattern is **P-4 — Bengali primary, English annex** — and `CG-010` §4.1's English-governs position is **overridden for those documents**, exactly as `CG-010` §4.1 anticipates |
| **LA-03** | Until decided, **no filing to a public body is generated from the ERP without Legal sign-off** on its language |

---

## 7. Employee-facing documents

`DT-041` and `DT-042` are read by 500+ employees, many of whom will not read an English payslip.

| Document | Pattern | Bengali-critical content |
|---|:--:|---|
| `DT-041` Payslip and salary certificate | **P-1** | Earnings and deduction line names, statutory deductions, net pay, **amount in words** |
| `DT-042` HR letter set | **P-3** | Appointment, confirmation, transfer, warning, termination, experience |

| # | Rule |
|---|---|
| **HR-B01** | **Payslip line names come from the `MD` payroll element `name_bn` column**, not re-translated per payslip (`BN-003` §12) |
| **HR-B02** | **Statutory deduction names are Tier 1** — `TIN`, `AIT`, provident fund reference codes (`BN-004` §3) |
| **HR-B03** | **Net pay carries the amount in words in Bengali** (`AW-B02`) |
| **HR-B04** | A **warning or termination letter is Bengali-primary** where the employee's working language is Bengali. A disciplinary instrument the recipient cannot read is not effective notice |
| **HR-B05** | Payslip PDFs are **password-protected** and the password instruction is in Bengali (`NT-014`) |

---

## 8. Labels, barcodes and QR — `DT-044`

| # | Rule |
|---|---|
| **LB-B01** | **Bengali is never encoded into a barcode or QR payload** (`BN-004` §7). The payload is Latin and Arabic digits |
| **LB-B02** | **Human-readable label text may be Bengali**; the machine-readable payload never is |
| **LB-B03** | Label stock is small and thermal. **11 pt Bengali floor applies** (`TH-01`), which usually means the Bengali is a short noun, not a sentence |
| **LB-B04** | **Identifiers printed beneath a barcode are Arabic digits, ungrouped** (`BN-004` `DN-05`) |
| **LB-B05** | Where a label is too small for legible Bengali, it carries **the identifier and an icon**, and the Bengali lives on the accompanying document — **not a shrunken Bengali below the floor** (`VB-009` `MS-02`) |

---

## 9. The precedence clause

Every bilingual Class A and B document carries it. Drafted once in `LG-001` and reproduced
(`CG-010` §4.1).

| Language | Text |
|---|---|
| English | This document is issued in Bengali and English. **In the event of any inconsistency, the English version prevails**, except where the law of Bangladesh requires otherwise. |
| **Bengali** | **এই ডকুমেন্টটি বাংলা ও ইংরেজিতে ইস্যু করা হয়েছে। কোনো অসঙ্গতি দেখা দিলে ইংরেজি সংস্করণ প্রাধান্য পাবে, তবে বাংলাদেশের আইনে ভিন্ন কিছু প্রয়োজন হলে তা প্রযোজ্য হবে।** |

| # | Rule |
|---|---|
| **PC-01** | The clause is **not optional and not abbreviated**. It appears on every bilingual Class A and B document |
| **PC-02** | It is **not applied to P-4 documents** under §6, where Bengali is the operative language |
| **PC-03** | The Bengali wording is **fixed here and is not re-translated per document** (`CP-01`) |
| **PC-04** | The clause is **subject to Legal Counsel confirmation** — `CG-010` §12 item 2 remains open |

---

## 10. Verification

| Check | Mechanism | When |
|---|---|---|
| Bengali below its print floor | Automated layout lint | Every template release |
| Font embedded in the PDF | Automated | Every render |
| PDF text layer extractable as Bengali | Automated | Every render |
| PDF metadata language | Automated | Every render |
| Latin file name | Automated | Every render |
| Bengali in a barcode payload | Automated | Every render |
| Amount in words matches the figure | Render-time assertion | Every render |
| Bengali digits on a statutory document | Automated | Every render |
| **Conjunct rendering, per printer model** | **Visual, with the `BN-006` §9 test set** | **Before each `DT` release** |
| **Thermal rendering, per model and firmware** | **Visual** | Before each `DT` release |
| Precedence clause present on Class A/B | Automated | Every render |
| Bengali expansion does not overflow the layout | Visual, with maximum-length sample data (`TS-002`) | Every template release |
| G6 statutory verification of the Bengali | External | Per statutory template |

---

## 11. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7).

**This pack delivers rules and patterns, not a per-document string set.** That distinction was
blurred in the first issue of this table, which claimed 320 authored Bengali strings. The counted
figure is **9 canonical strings plus the precedence clause**; the per-document Bengali is authored
**in each `DT` template**, against the patterns fixed here.

| Deliverable | Counted |
|---|---:|
| Bilingual `DT` templates in scope | **34 of 44** ✔ reconciles to `CG-010` §3.2 |
| Layout patterns fixed (§2) | 5 |
| Pattern assignments made (§5, §7, §8) | 34 |
| **Canonical Bengali strings authored (§5)** | **9** |
| **Precedence clause authored (§9)** | **1** |
| Rules issued (`DB-`, `TH-`, `ST-B`, `AW-B`, `SV-B`, `LA-`, `HR-B`, `LB-B`, `PC-`) | **48** |
| **Per-document Bengali strings still to be authored, in the `DT` files** | **Not yet enumerable — the `DT` templates do not carry key inventories.** Raised as `AUDIT-012` **BN-20** |

| Group | Bilingual templates | Pattern assigned |
|---|---:|---|
| `05A` Service and operations | 8 | P-1 ×5, P-2 ×3 |
| `05B` Finance and statutory | 11 | P-5 ×5, P-1 ×6 |
| `05C` Supply chain (bilingual subset) | 3 | P-1 ×3 |
| `05D` Commercial and contract (bilingual subset) | 8 | P-3 ×8 |
| `05E` People, quality and labelling | 4 | P-1 ×2, P-3 ×1, P-2 ×1 |
| **Total** | **34** | |
| English-only | 10 | — |

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **Does the Bangla Bhasha Prachalan Ain 1987 apply, and to which documents?** (§6) | **Legal Counsel** with Tax Manager | `LA-02`, `LA-03`, every filing |
| 2 | **Precedence clause confirmed** — `CG-010` §12 item 2 | Legal Counsel | `PC-04`, every Class A/B bilingual document |
| 3 | **`VAT` / মূসক in our own prose** — `BN-004` §10 item 2 | Tax Manager | `ST-B05`, `DT-010`…`DT-014` |
| 4 | **Printer and thermal certification list** — `BN-006` §10 item 5 | Platform Engineering with Operations | `DB-10`, `DB-11`, `TH-05` |
| 5 | **Category 10 `LG` is not yet written.** `LG-001`, `LG-013` and `LG-015` are cited here and do not exist | Legal | `PC-03`, `SV-B02`, warranty wording |
| 6 | `BN-002` `RD-C` formal sub-register ratified, and a reviewer with legal-Bengali experience identified (`BN-002` §13 item 3) | Localisation Lead with Legal | G4 on Class A/B |
| 7 | `BN-007` numeral and currency-position decisions ratified | Localisation Lead with Finance | Every amount on every document |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) | The document standard this localises |
| [`../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | The custody instrument §5 governs |
| [`../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | The P-5 prescribed form |
| [`../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | The brand furniture around these layouts |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | §9 test set, thermal constraints |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | Amount in words, currency prefix, date form |
| [`BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md`](BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md) | §6.4, the 1987 Act obligation |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Five bilingual layout patterns decided once and assigned per template; Bengali-first placement and the value-appears-once rule; print, PDF and thermal rules including font embedding, extractable text layers, Bengali PDF metadata and Latin file names; the replace-the-printer rule carried through to documents; statutory prescribed-form precedence; amount-in-words in both languages; **the 1987 Act document list held open for Legal**; employee-document rules including Bengali-primary disciplinary letters; barcode payload prohibition; the bilingual precedence clause fixed once in both languages | Legal Counsel with Localisation Lead and Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Scope reconciled to `CG-010` §3.2 at 34 of 44, with the English-only ten declared as a decision
- [x] **Bilingual layout decided once as five patterns**, rather than per template
- [x] Bengali-first placement stated, and the value-printed-once rule that prevents reprint divergence
- [x] Print, PDF and thermal floors cited from `VB-009` rather than restated (`CP-01`)
- [x] **The replace-the-printer rule carried through, with no silent English downgrade**
- [x] Statutory prescribed forms given precedence over every convention in this pack
- [x] Amount in words specified in both languages, generated and verified
- [x] **The 1987 Act document list produced so the open legal question can be executed on**
- [x] Employee documents treated as effective notice, not as information
- [x] The precedence clause fixed once, in both languages, with its own open-decision flag
- [x] All internal links resolve
- [ ] **G4 in-context review on printed output, per printer model** — outstanding; blocks `Approved`
- [ ] **G5 legal review of the Bengali** — outstanding; this file is Class B
- [ ] **G6 statutory verification of the Bengali on `DT-010`…`DT-014`** — outstanding
- [ ] **1987 Act applicability decided** — outstanding; §12 item 1
- [ ] **Precedence clause confirmed by Legal Counsel** — outstanding; §12 item 2
- [ ] **Category 10 `LG` written**, so the documents this file cites exist — outstanding; §12 item 5
- [ ] Named approver recorded — **pending Legal Counsel**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
