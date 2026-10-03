---
id: DT-001
title: Document Template Standard and Branding Rules
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture with Brand
author: Enterprise Architecture with Brand, Finance and Content Design
reviewers: [Brand, Finance, Tax, Legal & Compliance, Quality, Platform Engineering, Localisation Lead]
approver: Chief Technology Officer
content_class: E
purpose: >
  The content standard every one of the other 43 DT templates conforms to — the section spine,
  the statutory-evidence obligation, the numbering and retention contract, the bilingual pattern
  declaration and the output-format declaration. Forty-three templates authored to no standard
  produce forty-three inconsistent legal documents.
traces_to: [VB-004, VB-009, MD-040, MD-037, LG-009, DT-044, CG-006, CG-008, 05-02 DM-11, 05-06 §9]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-004 Print and PDF Brand Template Standard v1.0 — page geometry, type scale, bilingual layout patterns, statutory yield rules
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 Bilingual Content Policy §3.2 — 34 of 44 DT templates bilingual, 10 English-only
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-002 Content Operating Model and RACI §4.1 — DT class allocation A=26, B=6, C=10, D=1, E=1
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §1 DM-11 — branch- and business-line-aware document sequences
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — A4 and thermal receipt formats, Bengali rendering verified on all supported printers
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-001 — Document Template Standard and Branding Rules

> **`DT-001` governs what a document template must *say*. `VB-004` governs how the page is
> *built*.** Neither restates the other (`CP-01`). Where a reader needs millimetres, type sizes
> or colour values, `VB-004` is the answer; where a reader needs the required sections, the
> statutory evidence obligation, the numbering contract or the retention rule, this file is.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Category standard — governs `DT-002` … `DT-044` |
| Owning module | `M24` Document, Records and E-Signature |
| Statutory | No — but 26 of the templates it governs are content class **A** statutory |
| Recipient(s) | Content authors, reviewers, template implementers, auditors |
| Languages | English (the standard); its **outputs** are bilingual per §6 |
| Output formats | n/a — this file defines the permitted set, it does not render |
| Numbering mask | n/a — defines the obligation, `MD-040` holds the masks |
| Retention period | Governance content, retained per `LG-009` governance class |

### 1.1 What this category is

Forty-four templates. Everything the ERP prints, emails as a PDF, or hands to a customer,
regulator, brand partner, employee or auditor.

| Sub-category | Folder | Files | Dominant class |
|---|---|---:|---|
| **05A** Service & Operations | `05A_Service_and_Operations/` | `DT-002`…`DT-009` (8) | A / C |
| **05B** Finance & Statutory | `05B_Finance_and_Statutory/` | `DT-010`…`DT-020` (11) | A |
| **05C** Supply Chain & Logistics | `05C_Supply_Chain_and_Logistics/` | `DT-021`…`DT-029` (9) | A / C |
| **05D** Commercial & Contract | `05D_Commercial_and_Contract/` | `DT-030`…`DT-040` (11) | A / B |
| **05E** People, Quality & Labelling | `05E_People_Quality_and_Labelling/` | `DT-041`…`DT-044` (4) | A / B / C / D |
| **Standard** | category root | `DT-001` (1) | E |

---

## 2. Statutory Requirements

This file mandates no element of its own. It imposes the **evidence obligation** that the
statutory templates discharge.

| Obligation | Rule | Applies to |
|---|---|---|
| Name the instrument | Every class **A** template names the Act, Rule, SRO or form number that mandates it | 26 templates |
| Element-by-element table | Every mandated element is listed in §2 of that template with its source and a verification date | 26 templates |
| Reproduce, do not redesign | Where a form is prescribed, field order, labels and wording are reproduced exactly (`VB-004` S-01) | Tier **S**, §2.2 |
| Fiscal-year pin | Statutory templates are version-pinned to the fiscal year of the instrument (`CG-006` §4.1) | 26 templates |
| External verification | Gate **G6** — no class **A** template is `Approved` on internal review alone (`CG-007`, `CP-07`) | 26 templates |

### 2.1 The two statutory registers, and why both are correct

Two counts circulate in the programme and they measure different things. Both are stated here
so neither is read as an error.

| Count | Source | What it counts |
|---:|---|---|
| **14** | Master Index Category 05 preamble | **Tier S** — documents whose *form* is prescribed by a Bangladeshi instrument. The layout is not ours to design |
| **26** | `CG-002` §4.1 class allocation | **Content class A** — documents whose *consequence* is statutory. Includes Tier S plus 12 documents that are freely designed but whose content carries regulatory or tax consequence |

> `CG-002` §4.1 is the authoritative class allocation. Tier S is a sub-classification defined
> here for the first time, in §2.2, to reconcile the two figures.

### 2.2 Tier S — the 14 prescribed-form documents

| # | ID | Document | Prescribing instrument (to be confirmed at G6) |
|---:|---|---|---|
| 1 | `DT-010` | Tax Invoice — Mushak 6.3 | VAT & SD Act 2012; VAT & SD Rules 2016, Form Mushak 6.3 |
| 2 | `DT-011` | Sales Register — Mushak 6.2 | VAT & SD Rules 2016, Form Mushak 6.2 |
| 3 | `DT-012` | Purchase Register — Mushak 6.1 | VAT & SD Rules 2016, Form Mushak 6.1 |
| 4 | `DT-013` | VDS Certificate — Mushak 6.6 | VAT & SD Rules 2016, Form Mushak 6.6 |
| 5 | `DT-014` | VAT Return — Mushak 9.1 | VAT & SD Rules 2016, Form Mushak 9.1 |
| 6 | `DT-015` | Credit / debit note | VAT & SD Rules 2016, Forms Mushak 6.7 / 6.8 |
| 7 | `DT-016` | Money receipt | VAT & SD Rules 2016 Form Mushak 6.3 for service supplies; Stamp Act 1899 for money receipts above the prescribed value |
| 8 | `DT-020` | Consolidated corporate invoice | Must itself be a conforming Mushak 6.3 or be accompanied by them |
| 9 | `DT-025` | Debit advice on return to vendor | VAT & SD Rules 2016, Form Mushak 6.8 |
| 10 | `DT-026` | Stock transfer note | VAT & SD Rules 2016, Form Mushak 6.5 transfer challan |
| 11 | `DT-027` | Delivery challan | VAT & SD Rules 2016, Form Mushak 6.5 where goods move without a sale |
| 12 | `DT-034` | Data destruction certificate | Data-protection regime referenced at `05-06` NFR-086; contractual and audit requirement |
| 13 | `DT-035` | E-waste disposal certificate | Hazardous Waste (E-waste) Management Rules 2021, under the Bangladesh Environment Conservation Act 1995 |
| 14 | `DT-041` | Payslip | Bangladesh Labour Act 2006 wage-record obligations; Income Tax Act 2023 withholding evidence |

> ⚠ **None of the 14 instrument citations above is verified.** Each is carried into the
> individual template's §2 and is verified there at gate **G6** by the external tax, legal or
> environmental adviser as applicable. `CG-012` EV-02 prohibits relying on secondary summaries.

### 2.3 Content class allocation for the category

| Class | Count | IDs |
|:--:|---:|---|
| **A** Statutory | 26 | `DT-002`, `DT-005`, `DT-009`, `DT-010`–`DT-017`, `DT-019`, `DT-020`, `DT-023`–`DT-027`, `DT-029`, `DT-034`–`DT-036`, `DT-038`–`DT-041` |
| **B** Legal / contractual | 6 | `DT-018`, `DT-030`, `DT-031`, `DT-032`, `DT-037`, `DT-042` |
| **C** Operational-critical | 10 | `DT-003`, `DT-004`, `DT-006`, `DT-007`, `DT-008`, `DT-021`, `DT-022`, `DT-028`, `DT-033`, `DT-043` |
| **D** User-facing | 1 | `DT-044` |
| **E** Internal governance | 1 | `DT-001` |
| | **44** | Reconciles to `CG-002` §4.1 exactly |

---

## 3. Layout

Layout is `VB-004`. This section states only what a `DT` template must **declare** about layout.

| Zone | What the template must declare | Bilingual treatment |
|---|---|---|
| Header | Document title as it prints, in both languages where bilingual | Declared, not chosen per render |
| Party block | Which party appears left, which metadata right, and which identifiers are mandatory | Labels stacked; values not translated |
| Body / line items | Column set, column order, and what happens when the body overflows a page | Column widths sized for Bengali (`VB-004` BL-02) |
| Totals / summary | Which totals appear, in what order, and the rounding rule (`MD-039`) | Numerals per `BL-05` |
| Statutory block | The verbatim declarations, and that they never split across a page (`VB-004` G-04) | Parallel columns |
| Signature / stamp zone | Who signs, whether a company stamp is required, and whether an e-signature is accepted (`M24`) | Stacked labels |
| Footer | Document reference, page n of m, hotline 16743 | English reference, bilingual caption |
| Machine-readable | Which symbology and which payload, per `DT-044` | Payload is never translated |

| # | Rule |
|---|---|
| **L-01** | A template declares exactly one primary output format and lists any secondary formats (`VB-004` F-01) |
| **L-02** | Every zone the template uses is specified. A zone that is not used is stated as "not used", not omitted |
| **L-03** | Overflow behaviour is specified for every table: repeat header, carry-forward subtotal, "continued" marker |
| **L-04** | A document that can exceed one page declares its `page n of m` position and its continuation rule |
| **L-05** | Machine-readable zones cite `DT-044` for the payload; they never define their own encoding |

---

## 4. Field Mapping

Every template carries a field-mapping table with these columns, in this order:

| Column | Meaning | Required |
|---|---|:--:|
| `Label EN` | The printed English label, sentence case per `CG-003`, except where an instrument prescribes otherwise | ✔ |
| `Label BN` | The printed Bengali label, terminology per `BN-003` | Where bilingual |
| `Source field` | The `05-02` entity and attribute, or the `MD-nnn` register it resolves from | ✔ |
| `Format` | Date, number, currency, identifier or free-text format per `MD-039` and `05-06` §9 | ✔ |
| `Required` | Whether the document may print without it | ✔ |
| `Conditional` | The condition under which it appears | Where conditional |

| # | Rule |
|---|---|
| **FM-01** | Every printed field resolves to a named source. A field with no source is a field somebody types, and typed fields on statutory documents are defects |
| **FM-02** | A field whose absence makes the document non-compliant is `Required = ✔` **and** appears in §2 with its instrument reference |
| **FM-03** | Dates print `DD/MM/YYYY`; money prints two decimals, thousands-separated, right-aligned (`05-06` §9, `MD-039`) |
| **FM-04** | Identifiers — BIN, TIN, NID, serial, document reference — print in a monospaced face and are never line-broken |
| **FM-05** | A blank required field blocks the render. It does not print an empty box |
| **FM-06** | Bengali labels are authored, never machine-translated (`CP-05`, `CG-010`) |

---

## 5. Business Rules Affecting Output

Rules that constrain the whole category. Individual templates add their own from `05-05`.

| Rule ID | Effect on every document |
|---|---|
| `BRU-DMS-01` | A document cannot be deleted before its retention period expires |
| `BRU-DMS-02` | A document under legal hold is not disposed of regardless of retention |
| `BRU-DMS-03` | A signed document cannot be modified. A change is a new version with a new signature |
| `SEQ-01` (`MD-040`) | A statutory sequence is gap-free. A cancelled number is recorded as cancelled, never skipped |
| `SEQ-04` (`MD-040`) | A statutory numbering mask cannot change mid-period |
| `TAX-04` (`MD-037`) | A document is taxed at the rate effective on its **tax point**, not the rate current at reprint |

### 5.1 Reprint, copy and void

The three states every issued document can enter. Ungoverned, they are the category's largest
fraud and audit exposure.

| # | Rule |
|---|---|
| **RC-01** | A reprint of an issued document is watermarked **COPY** and carries the reprint timestamp and the user who requested it |
| **RC-02** | The **original** is issued once. There is no second original |
| **RC-03** | Every reprint of a class **A** or **B** document is logged with user, timestamp and reason, and is visible in the audit trail (`M24`) |
| **RC-04** | A voided document is watermarked **VOID**, retains its number, and states the reason and the replacing document's number |
| **RC-05** | A draft rendered before issue is watermarked **DRAFT** and carries no document number from a statutory sequence |
| **RC-06** | A specimen used in training or testing is watermarked **SPECIMEN** and uses a reserved non-production sequence prefix (`MD-040`) |
| **RC-07** | Watermarks never obscure a statutory field (`VB-004` brand furniture) |

### 5.2 Signature and stamp

| # | Rule |
|---|---|
| **SG-01** | The template declares who signs, in what capacity, and whether a company stamp is required |
| **SG-02** | Electronic signature is accepted where `M24` records signer identity, timestamp and document hash |
| **SG-03** | A customer-facing acknowledgement may be captured by signature, OTP or biometric; the template declares which are acceptable and the evidence stored for each |
| **SG-04** | An OTP acknowledgement records the masked number, the timestamp and the message reference — not the OTP value |
| **SG-05** | A signature zone that is never signed is removed, not left empty. An unsigned signature block on an issued document reads as an incomplete document |

---

## 6. Variants

### 6.1 Bilingual pattern

34 of the 44 templates are bilingual (`CG-010` §3.2). The pattern is declared per template
(`VB-004` BL-01), from this set:

| Pattern | Typical use |
|---|---|
| **Stacked** | Field labels on forms, receipts and thermal output |
| **Parallel columns** | Terms, declarations and statutory blocks |
| **Separate pages** | Long legal documents, with a precedence clause |

**The 10 English-only templates** (`CG-010` §3.2): `DT-001`, `DT-021`, `DT-022`, `DT-023`,
`DT-024`, `DT-025`, `DT-029`, `DT-033`, `DT-039`, `DT-040`. All are vendor-, brand- or
B2B-facing, or internal specifications; none is issued to a consumer or a field employee.

> **Note.** `DT-025` and `DT-039`/`DT-040` are English-only as documents while remaining
> content class **A**. English-only is a *language* decision; class is a *consequence*
> decision. They are independent.

### 6.2 Output format

| Format | Templates that use it as primary |
|---|---|
| A4 portrait | The majority — invoices, estimates, reports, certificates, contracts, statements |
| A4 landscape | `DT-011`, `DT-012`, `DT-029` registers and count sheets |
| A5 portrait | `DT-026` gate pass, branch handover forms |
| Thermal 80 mm | `DT-016` counter receipt variant, `DT-002` counter slip variant |
| Thermal 58 mm | Rider handheld receipts (`DT-028` variant) |
| Label | `DT-044` — the specification, not a document |
| PDF/A-3 archive | **All class A templates**, on issue (`VB-004` F-02) |

### 6.3 Channel variants

A template may render to more than one channel. Each channel variant is listed in §6 of that
template with the difference stated.

| Channel | Constraint |
|---|---|
| Print | The governing rendition |
| PDF attachment (email) | Must be identical in content to the print rendition; `VB-005` governs the carrying email, not the attachment |
| Portal download | Tagged, accessible PDF (`VB-004` §10) |
| In-app view | May reflow; must not omit any element the print rendition carries |
| Thermal | May abbreviate labels from a declared abbreviation list; may never omit a statutory element |

---

## 7. Worked Example

The category's specimen set is held in `RF-009`. Each template links its own specimen.

| # | Rule |
|---|---|
| **WE-01** | Every template has at least one rendered specimen with representative data, including a Bengali rendition where bilingual |
| **WE-02** | Class **A** templates carry a specimen with the **maximum** line-item count, to prove the statutory block does not split (`VB-004` G-04) |
| **WE-03** | Specimens are watermarked **SPECIMEN** and use the reserved non-production sequence (`RC-06`) |
| **WE-04** | A specimen is regenerated whenever the template changes. A stale specimen is worse than none |

---

## 8. Approval

| Class | Reviewers | Approver | External gate |
|:--:|---|---|---|
| **A** Statutory | Tax / Legal / Environmental / HR as applicable, Finance, Platform Engineering | CFO or Legal Counsel | **G6 — external adviser verification, unwaivable (`WV-02`)** |
| **B** Legal | Legal & Compliance, domain owner | Legal Counsel | Legal sign-off recorded |
| **C** Operational | Domain owner, Quality, Platform Engineering | Domain Content Owner + Business Owners Forum | — |
| **D** User-facing | Content Design, Design System | Content Design Lead | — |
| **E** Governance | Programme Content Lead | Programme Content Lead | — |

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Enterprise Architecture with Brand | 2026-08-15 | Draft issue |
| Reviewer — Brand | *pending* | | |
| Reviewer — Tax | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Approver — CTO | *pending* | | |

---

## 9. Numbering, Retention and Archive

### 9.1 Numbering

Every issued document draws its reference from a sequence registered in `MD-040`. No template
defines its own mask.

| # | Rule |
|---|---|
| **N-01** | The template names its `MD-040` sequence code. If none exists, the template is not implementable and the gap is raised against `MD-040`, not solved locally |
| **N-02** | Statutory sequences are `no_gaps` and branch-aware (`05-02` DM-11) |
| **N-03** | The document reference prints in the footer of **every** page (`VB-004` G-03) |
| **N-04** | A document that is not issued — draft, preview, specimen — never consumes a statutory number |
| **N-05** | Reset policy is a `MD-040` property. A template never states a reset policy of its own |

### 9.2 Retention

| Class | Minimum retention | Basis |
|:--:|---|---|
| **A** — VAT and tax documents | **At least 5 years** from the end of the tax period | VAT record-keeping obligation — *to be confirmed at G6* |
| **A** — payroll and employment | Per the Labour Act record obligations — *to be confirmed at G6* | `LG-009` |
| **A** — environmental and data destruction | Per the customer contract, minimum matching the tax retention | `LG-009` |
| **B** — contracts | Contract term plus the limitation period | `LG-009` |
| **C** / **D** | Per `LG-009` operational schedule | `LG-009` |

| # | Rule |
|---|---|
| **R-01** | Retention is stated in `LG-009` and cited by the template. A template that states its own conflicting period is a defect |
| **R-02** | Class **A** documents archive as **PDF/A-3 with embedded fonts** at the moment of issue, not on demand (`VB-004` F-02) |
| **R-03** | The archived rendition is the evidential copy. A re-render from live data years later is **not** the document that was issued, because master data has moved |
| **R-04** | Legal hold overrides retention expiry in both directions — it prevents deletion, never mandates it (`BRU-DMS-02`) |

### 9.3 The re-render prohibition, stated plainly

> A statutory document is a **fact about a moment**. Tax rates change, addresses change, price
> lists change, entity names change. Re-rendering an invoice from today's master data produces
> a different document with the same number. Every class **A** and **B** template therefore
> archives its issued rendition and serves *that file* on every subsequent request.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | The visual and structural standard this content standard serves |
| [`../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | Bengali minimum print sizes and rendering |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) | Every document reference in the category |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Rates and Mushak form derivation for `DT-010`…`DT-015` |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) | Money formatting and rounding on every document |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §3.2 — which 34 templates are bilingual |
| [`../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | Fiscal-year pinning of statutory templates |
| [`../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md`](../00_Content_Governance_and_Standards/CG-007_Review_Approval_and_Signoff_Workflow.md) | Gate G6 external verification |
| [`05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | The machine-readable payload contract |
| `LG-009` Data Retention and Deletion Schedule | Retention periods cited in §9.2 |
| `RF-009` Sample and Reference Data Pack | Where every worked example lives |
| `MM-010` PDF and Print Template Design Specification | The design deliverable that implements this standard |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Twelve-section DT spine defined; Tier S sub-classification introduced to reconcile the 14 and 26 statutory counts; reprint/copy/void rules; re-render prohibition; retention and numbering contract | Chief Technology Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Document_Print_Template.md`, with the four-section extension justified in §12 below
- [x] Class allocation reconciles to `CG-002` §4.1 exactly (26 / 6 / 10 / 1 / 1)
- [x] Bilingual allocation reconciles to `CG-010` §3.2 exactly (34 / 10)
- [x] Statutory count reconciled — Tier S = 14, class A = 26, both explained
- [x] Every internal link resolves
- [x] Bengali counterpart — n/a; this is a specification, its outputs are bilingual
- [ ] Instrument citations verified at gate **G6** — **outstanding, unwaivable (`WV-02`)**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

## 12. The DT Section Spine — template extension justification

`TPL_Document_Print_Template.md` defines sections 1–8 and a Definition of Done. Every `DT`
file in this category adds three numbered sections after §8, in this fixed order:

| § | Section | Why it is required for this category |
|---|---|---|
| 9 | Numbering, Retention and Archive | 26 statutory templates have a gap-free numbering obligation and a multi-year retention obligation. Neither fits in §1's summary table, and both are audited |
| 10 | Related Documents | `CP-01` forbids duplication, so cross-reference density in this category is high; the audit check **D1** enumerates these links |
| 11 | Revision History | `CG-006` requires statutory templates to be pinned and their changes traceable |

This extension is the justification required by the template's own Definition of Done
("no sections removed, none added without justification"), and is registered in `CG-009`.
Files in this category therefore run **1–11 plus DoD**. A `DT` file with a different spine
fails check **E7**.

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
