---
id: DT-010
title: Tax Invoice — Mushak 6.3
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Tax with Finance
author: Tax with Finance, Enterprise Architecture and Content Design
reviewers: [External tax adviser, Finance, Legal & Compliance, Platform Engineering, Internal Audit, Localisation Lead]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The NBR-prescribed VAT invoice — the statutory tax invoice a VAT-registered business must issue
  on a taxable supply. Issuing a non-conforming invoice is a compliance failure with penalty
  exposure, and input VAT cannot be claimed by a buyer against a defective one. It must be
  generated automatically at the point of supply, never assembled by hand.
traces_to: [M51, M20, M19, MD-002, MD-035, MD-037, MD-039, MD-040, DT-001, DT-005, DT-011, DT-014, DT-015, DT-016, DT-020, BRU-FIN-01, BRU-SRM-05, 05-06 NFR-100]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-010_Tax_Invoice_Mushak_6_3_BN.md
sources:
  - source: The Value Added Tax and Supplementary Duty Act 2012 and the VAT and Supplementary Duty Rules 2016, Form Mushak 6.3 — **the prescribed form must be obtained from the enacted Rules and verified at G6; the element list below is indicative**
    verified: 2026-08-15
    class: P1
  - source: Mushak 6.3 mandated content as commonly summarised — name, address and BIN of supplier and buyer; sequential invoice number and date; description of goods or services; quantity; unit price; value; VAT rate and amount; supplementary duty where applicable; signature or authorisation
    verified: 2026-08-15
    class: P2
  - source: VAT record retention — Mushak records preserved for at least 5 years
    verified: 2026-08-15
    class: P2
  - source: project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037 — rate and Mushak form derivation; all rates pending G6
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-100 — Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-010 — Tax Invoice (Mushak 6.3)

> ⚠ **Tier S — the form is prescribed. Brand yields completely (`VB-004` S-01).**
>
> This document is not designed by 1000FiX. It is **reproduced** from the form prescribed in the
> VAT and Supplementary Duty Rules 2016. Field order, labels, wording and position are the
> instrument's. Where this file and the enacted form differ, **the instrument governs and this
> file is corrected** — never the reverse.
>
> **Nothing in this file is verified.** The element list, the sequence rules and the retention
> period below are the programme's working understanding. Gate **G6** verification against the
> enacted Rules by the external tax adviser is **mandatory and unwaivable (`WV-02`)**. Until it
> is recorded, no invoice may be issued from this template in production.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory VAT tax invoice (challan)** |
| Owning module | `M51` Tax and Regulatory Compliance (Bangladesh), with `M20` Accounts Receivable |
| Statutory | **Yes — Tier S.** VAT & SD Act 2012; VAT & SD Rules 2016, Form Mushak 6.3 |
| Recipient(s) | Buyer (original), company record, NBR on demand, auditor |
| Languages | **Bilingual.** The prescribed form's language governs; see §6.1 |
| Output formats | A4 portrait · Thermal 80 mm (counter variant, §6.2) · **PDF/A-3 archive, mandatory at issue** |
| Numbering mask | `MD-040` — statutory sequence, **`no_gaps`**, branch-aware (`05-02` DM-11) |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27.** A new pin is required at each Finance Act (`CG-006` §4.1) |

### 1.1 When it is issued

| Trigger | Rule |
|---|---|
| A taxable supply is made | The invoice is issued **at the point of supply**, automatically |
| Service order reaches Completed and is priced | `BRU-SRM-05` — no invoice before Completed |
| A consolidated corporate billing run executes | `DT-020` is the wrapper; conforming Mushak 6.3 challans underpin it |
| Advance payment received | `DT-019` proforma precedes it; the Mushak issues at the tax point, which is a **G6 question** |
| Marketplace supply | The principal-or-agent model in `BRU-FIN-08` determines **who issues the invoice**. This must be settled before `P07` launches |

---

## 2. Statutory Requirements

> Every row is **unverified**. The `Verified` column will carry the adviser's date only after
> G6. A blank or "pending" entry here blocks `status: Approved` under `CG-007`.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title and reference — *Mushak 6.3* | VAT & SD Rules 2016 — **pending G6** | pending | Header, verbatim |
| Supplier name and address | VAT & SD Rules 2016 — **pending G6** | pending | Supplier block |
| **Supplier BIN** | VAT & SD Act 2012; `BRU-FIN-01` | pending | Supplier block |
| Buyer name and address | VAT & SD Rules 2016 — **pending G6** | pending | Buyer block |
| **Buyer BIN** (where VAT-registered) | VAT & SD Rules 2016 — **pending G6** | pending | Buyer block |
| Unique sequential invoice number | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Invoice date (and time where prescribed) | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Description of goods or services | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| HS code / service code where applicable | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| Quantity and unit | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| Unit price | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| Value excluding VAT | VAT & SD Rules 2016 — **pending G6** | pending | Line items, totals |
| **VAT rate applied** | `MD-037` — **rate pending G6** | pending | Line items, totals |
| **VAT amount** | VAT & SD Rules 2016 — **pending G6** | pending | Line items, totals |
| Supplementary duty where applicable | VAT & SD Rules 2016 — **pending G6** | pending | Line items, totals |
| Total value including VAT | VAT & SD Rules 2016 — **pending G6** | pending | Totals |
| Signature or authorisation mark | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 The G6 question list

The adviser is asked these questions, in writing, and the answers are recorded here.

| # | Question |
|---|---|
| **Q1** | Provide the current prescribed Mushak 6.3 form. Is our element list complete and in the prescribed order? |
| **Q2** | Is a Bengali rendition mandatory, permitted bilingually, or is English acceptable? |
| **Q3** | What is the **tax point** for a repair service — completion, invoice, or payment? This determines when the invoice must issue |
| **Q4** | May the invoice be issued electronically only, or must a physical copy be given? |
| **Q5** | What is the prescribed numbering format and reset behaviour? Are branch-aware sequences permitted? |
| **Q6** | Which of our supply types attract a rate other than the 15% standard, and under which SRO? |
| **Q7** | What is the exact retention period and format obligation for issued challans? |
| **Q8** | Is a digital signature acceptable in place of a manual one? |
| **Q9** | For marketplace supplies, who is the supplier of record under the `BRU-FIN-08` model we declare? |
| **Q10** | Is any NBR e-invoicing, fiscal-device or real-time reporting obligation applicable to us at our turnover? |

> **Q10 is a schedule risk, not a content question.** If a fiscal device or real-time reporting
> obligation applies, it is an integration requirement in `05-03`, not a template change, and it
> must be discovered now rather than at UAT.

---

## 3. Layout

**Primary format: A4 portrait.** Geometry yields to the prescribed form (`VB-004` §8.1).

| Zone | Treatment | Bilingual |
|---|---|---|
| Header | **Prescribed title, verbatim.** Logo only in space the form leaves free | Per the instrument (G6 Q2) |
| Supplier block | Prescribed field set and order. **No re-ordering for visual balance** | Per the instrument |
| Buyer block | Prescribed field set and order | Per the instrument |
| Line items | Prescribed columns, prescribed order | Per the instrument |
| Totals | Prescribed. Value, VAT per rate band, SD, gross | Arabic numerals (`BL-05`) |
| Statutory block | Prescribed declarations, **verbatim** | Per the instrument |
| Signature zone | Prescribed authorisation mark | — |
| Footer | Document reference and `page n of m` permitted | English |
| Brand colour | **None** (`VB-004` §8.1) | — |
| Machine-readable | QR permitted **only if it does not displace a prescribed element**; payload per `DT-044` | — |

| # | Rule |
|---|---|
| **L-10-a** | Where the instrument prescribes a layout, it is reproduced exactly. Every deviation is a defect, not a design decision |
| **L-10-b** | The statutory block never splits across a page (`VB-004` G-04) |
| **L-10-c** | Multi-page invoices carry the invoice number and `page n of m` on **every** page. An invoice that cannot be shown to be complete is not evidence |
| **L-10-d** | Totals never appear alone on a continuation page (`VB-004` G-05) |
| **L-10-e** | Fonts are **embedded**; the archive is **PDF/A-3**. A challan that renders in a substituted font on the NBR's machine is not the challan we issued (`VB-004` T-02, F-02) |

---

## 4. Field Mapping

### 4.1 Supplier

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Supplier name | সরবরাহকারীর নাম | `MD-002.entity_legal_name` | Text | ✔ |
| Supplier address | ঠিকানা | `MD-002.registered_address` | Text | ✔ |
| **Supplier BIN** | **বিআইএন** | `MD-002.bin` | Monospace, unbroken | ✔ |
| VAT circle / division / commissionerate | ভ্যাট সার্কেল / বিভাগ | `MD-002.vat_circle`, `.vat_division`, `.vat_commissionerate` | Text | ✔ **pending G6 confirmation** |
| Branch / place of supply | সরবরাহস্থল | `MD-003.branch_name` + address | Text | ✔ |

### 4.2 Buyer

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Buyer name | ক্রেতার নাম | `party.display_name` | Text | ✔ |
| Buyer address | ঠিকানা | `party.address` | Text | ✔ |
| **Buyer BIN** | **বিআইএন** | `party.bin` | Monospace | **✔ where the buyer is VAT-registered** |
| Buyer TIN | টিআইএন | `party.tin` | Monospace | Where applicable |
| Buyer type | ক্রেতার ধরন | `party.party_type` | Enum: registered / unregistered / government / export | ✔ |

### 4.3 Line items

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Serial | ক্রমিক | Computed | Integer | ✔ |
| Description of goods / services | পণ্য / সেবার বিবরণ | `MD-019.item_name` / `MD-022.part_name` | Text | ✔ |
| HS code / service code | এইচএস / সেবা কোড | `MD-019.hs_code`, `.service_code` | Monospace | ✔ **where applicable — G6 Q1** |
| Unit | একক | `MD-023.uom_code` | Text | ✔ |
| Quantity | পরিমাণ | `invoice.line.qty` | Number | ✔ |
| Unit price | একক মূল্য | `invoice.line.unit_price` | BDT, 2 dp | ✔ |
| Value (excl. VAT) | মূল্য (ভ্যাট ব্যতীত) | Computed | BDT, 2 dp | ✔ |
| SD rate / amount | সম্পূরক শুল্ক | `MD-037` | %, BDT | Where applicable |
| **VAT rate** | **ভ্যাট হার** | `MD-037.rate_pct` | %, 3 dp | ✔ |
| **VAT amount** | **ভ্যাট পরিমাণ** | Computed | BDT, 2 dp | ✔ |
| Total including VAT | ভ্যাটসহ মোট | Computed | BDT, 2 dp | ✔ |

### 4.4 Totals and authorisation

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Total value excluding VAT | মোট মূল্য (ভ্যাট ব্যতীত) | Computed | BDT, 2 dp | ✔ |
| Total SD | মোট সম্পূরক শুল্ক | Computed | BDT, 2 dp | Where applicable |
| **Total VAT, per rate band** | **মোট ভ্যাট (হার অনুযায়ী)** | Computed | BDT, 2 dp | ✔ |
| **Grand total** | **সর্বমোট** | Computed | BDT, 2 dp | ✔ |
| Amount in words | কথায় | Computed | Text | ✔ **language per G6 Q2** |
| VDS deducted by buyer | ক্রেতা কর্তৃক উৎসে কর্তন | `MD-037` VDS code | BDT, 2 dp | Where the buyer is a withholding entity |
| Net payable | নিট প্রদেয় | Computed | BDT, 2 dp | ✔ |
| Authorised signatory | অনুমোদিত স্বাক্ষরকারী | `employee.display_name` + designation | Text | ✔ |
| Signature / authorisation mark | স্বাক্ষর | Per G6 Q8 | Image or digital | ✔ |

| # | Rule |
|---|---|
| **FM-10-a** | Every line resolves to **exactly one** tax code at the tax point (`TAX-01`, `TAX-04`). A line whose tax code cannot be resolved blocks the invoice |
| **FM-10-b** | VAT totals subtotal **per rate band**. A single blended VAT figure across mixed rates is not reconstructable into `DT-011` or `DT-014` |
| **FM-10-c** | Rounding per `MD-039`. The grand total is the sum of the rounded line values, never an independently rounded figure |
| **FM-10-d** | A buyer claiming input VAT **must** have their BIN on the invoice. Omitting it costs the buyer money and produces an immediate dispute |
| **FM-10-e** | Where the buyer is a VDS withholding entity, the deduction shows on the invoice and the buyer's `DT-013` Mushak 6.6 is expected. The receivable is tracked net (`M20`) |
| **FM-10-f** | No field on this document is hand-typed at issue. Every value derives from a registered source (`FM-01`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-FIN-01` | Every customer invoice includes VAT at the applicable rate and displays the company's BIN |
| `BRU-SRM-05` | An invoice cannot be raised for a service order that is not Completed |
| `BRU-BIL-01` | The invoice generates automatically on job closure; manual creation for a completed job requires approval |
| `BRU-FIN-03` | A payment cannot be recorded against a cancelled invoice |
| `BRU-FIN-04` | A credit note requires Finance Manager approval or above — **an issued invoice is never edited** (`BRU-DMS-03`) |
| `BRU-FIN-05` / `BRU-FIN-06` | Period-close rules constrain when an invoice may post |
| `BRU-FIN-08` | The marketplace principal-or-agent model determines the supplier of record and cannot vary by transaction |
| `BRU-BIL-07` | A consolidated corporate invoice cannot issue until every constituent job is Completed and priced |
| `TAX-01`…`TAX-08` (`MD-037`) | Rate resolution, SRO evidence, tax-point rating, and the block on unverified tax codes |
| `SEQ-01`…`SEQ-04` (`MD-040`) | Gap-free statutory numbering, no decrement, no mid-period mask change |

### 5.1 Cancellation and correction

| # | Rule |
|---|---|
| **CX-01** | **An issued Mushak 6.3 is never edited.** A correction is a `DT-015` credit or debit note referencing it |
| **CX-02** | Cancellation before issue releases nothing — the number is recorded as **cancelled**, never reused (`SEQ-01`) |
| **CX-03** | A cancelled challan is retained and reported. An unexplained gap in the sequence is an audit finding of its own |
| **CX-04** | The cancellation reason comes from `MD-026` and is approved at Finance Manager level or above |
| **CX-05** | Cancellation after the VAT return for the period has been filed is not a cancellation — it is a return adjustment, and it goes to the adviser |

---

## 6. Variants

### 6.1 Language

The prescribed form's language governs. Three positions are possible and **G6 Q2 decides which**:

| If the instrument… | Then |
|---|---|
| Prescribes Bengali | The challan is issued in **Bengali**, exactly as prescribed. An English courtesy rendition may accompany it, clearly marked as not the challan |
| Permits bilingual | Parallel columns, Bengali first (`VB-004` BL-06) |
| Is silent | Bilingual, Bengali first — the safer position for a consumer-facing statutory document |

**Arabic numerals are used regardless** (`VB-004` BL-05) — the figures are transcribed into
government systems.

### 6.2 Output variants

| Variant | When used | Difference |
|---|---|---|
| **A4 standard** | The governing rendition | Full prescribed form |
| **Thermal 80 mm counter** | Branch counter sales | **Only if every prescribed element renders legibly.** Where it cannot, an A4 is issued. Legibility is proven per printer model, not assumed (`VB-004` TH-08) |
| **PDF for email / portal** | `P01`, `P04` delivery | Content identical to print; tagged and accessible (`VB-004` §10) |
| **PDF/A-3 archive** | **Every issue, mandatory** | The evidential copy served on all later requests |
| **Export / zero-rated** | Export supplies | Zero-rate treatment and the evidence the rate depends on; **G6 Q6** |
| **Government buyer** | Public-sector supply | VDS deduction near-certain; `DT-013` expected in return |
| **Marketplace** | `P07` | Supplier of record per `BRU-FIN-08`; **blocked until G6 Q9 is answered** |
| **Consolidated corporate** | `P04` monthly billing | `DT-020` wrapper over conforming challans |

---

## 7. Worked Example

> **No specimen may be produced from an unverified template.** The specimens below are built
> **after** G6 delivers the prescribed form. Producing a plausible-looking specimen first is how
> an unverified layout becomes the de-facto standard.

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-010-S1` | Single-rate repair service, unregistered buyer | Base prescribed rendition |
| `DT-010-S2` | Registered buyer with BIN, input-VAT claimable | `FM-10-d` |
| `DT-010-S3` | Mixed rate bands, parts + labour | `FM-10-b` per-band subtotalling |
| `DT-010-S4` | Government buyer with VDS deduction | `FM-10-e` and the `DT-013` expectation |
| `DT-010-S5` | Maximum line items across 3 pages | `L-10-c`, `L-10-d` pagination |
| `DT-010-S6` | Thermal 80 mm | Legibility of every prescribed element |

Held in `RF-009`, watermarked **SPECIMEN**, on the reserved non-production sequence (`RC-06`).

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Tax with Finance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — Platform Engineering | *pending* | | |
| **G6 — external tax adviser, against the enacted Rules** | *pending* | | **Unwaivable (`WV-02`). Blocks production issue** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040`, statutory. Format **pending G6 Q5** |
| Gap policy | **`no_gaps`.** Every number is issued, cancelled or void — never skipped (`SEQ-01`) |
| Branch awareness | Required by `05-02` DM-11; permissibility **pending G6 Q5** |
| Reset | Fiscal year, subject to G6 Q5 |
| Archive format | **PDF/A-3 with embedded fonts, at issue** (`VB-004` F-02) |
| Retention | **At least 5 years** from the end of the tax period — exact period **pending G6 Q7** |
| Re-render | **Prohibited absolutely.** Rates, addresses and entity data move. A re-render is a different document with the same number (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged with user, timestamp and reason (`RC-01`, `RC-03`) |
| Void | Watermarked **VOID**, retains its number, states the reason and the replacing document (`RC-04`) |
| Sequence audit | The full issued/cancelled/void sequence is reportable for any period, with no unexplained gap (`RP-009`) |

> **The gap-free rule is the one that gets audited.** Every number in a statutory sequence must
> be accounted for across the whole retention period. A system that "skips" a number on an error
> has created an audit finding that cannot be repaired later — which is why `SEQ-01` is a hard
> rule in `MD-040` and is tested explicitly in `TS-009`.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard; §2.2 Tier S |
| [`DT-011_Sales_Register_Mushak_6_2.md`](DT-011_Sales_Register_Mushak_6_2.md) | **Summarises every challan issued from this template** |
| [`DT-014_VAT_Return_Pack_Mushak_9_1.md`](DT-014_VAT_Return_Pack_Mushak_9_1.md) | The filing this ultimately feeds |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | The only lawful way to adjust an issued challan |
| [`DT-013_VDS_Certificate_Mushak_6_6.md`](DT-013_VDS_Certificate_Mushak_6_6.md) | Expected from a withholding buyer |
| [`DT-016_Payment_Receipt_and_Money_Receipt.md`](DT-016_Payment_Receipt_and_Money_Receipt.md) | Receipt of the money this invoice demands |
| [`DT-019_Proforma_Invoice_and_Advance_Request.md`](DT-019_Proforma_Invoice_and_Advance_Request.md) | Precedes it where advance payment is required; **not a tax invoice** |
| [`DT-020_Consolidated_Corporate_Invoice.md`](DT-020_Consolidated_Corporate_Invoice.md) | The corporate wrapper over conforming challans |
| [`../05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md`](../05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md) | The approved offer this must reconcile to |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Rate and form derivation |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-040_Document_Sequence_and_Numbering_Mask_Register.md) | The statutory sequence |
| [`../../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md`](../../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | §8.1 — where brand may and may not appear on this form |
| `LG-009` Data Retention and Deletion Schedule | Retention |
| `RP-009` Statutory and Regulatory Report Format Register | Sequence audit and return support |
| `TS-009` UAT Script Pack — Finance Roles | Where Mushak correctness is proven by Finance |
| `05-03` Integration and API Catalogue — NBR VAT Online | Filing and any e-invoicing obligation (G6 Q10) |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Tier S declaration, 17-element indicative mandate table, ten-question G6 list, cancellation/correction rules, gap-free sequence obligation, specimen-after-verification rule | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:`, `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Every mandated element listed with its source; **all marked unverified pending G6**
- [x] G6 question list written and specific enough to be answered
- [x] Brand yield to the instrument stated (`L-10-a`)
- [x] Cancellation and correction path defined; edit-in-place prohibited
- [x] Gap-free numbering and PDF/A-3 archive obligations stated
- [x] Specimen production deferred until after verification (§7)
- [x] All internal links resolve
- [ ] **G6 — prescribed form obtained and every element verified against the enacted Rules** — **outstanding, unwaivable (`WV-02`); blocks production issue**
- [ ] G6 Q2 language determination recorded — **outstanding; blocks the Bengali counterpart**
- [ ] G6 Q9 marketplace supplier-of-record determination — **outstanding; blocks `P07`**
- [ ] G6 Q10 e-invoicing / fiscal-device applicability — **outstanding; schedule risk on `05-03` and `AP-011`**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] `statutory_pin: FY2026-27` confirmed against the current Finance Act — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
