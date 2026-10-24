---
id: DT-011
title: Sales Register — Mushak 6.2
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Tax with Finance
author: Tax with Finance and Content Design
reviewers: [External tax adviser, Finance, Internal Audit, Platform Engineering]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The statutory sales register (sales book) derived from every Mushak 6.3 challan issued. It is
  the summarisation basis for the Mushak 9.1 return and the first record an NBR officer asks for
  in an inspection. It cannot be reconstructed reliably after the fact — a register assembled
  months later from partial data is not a register, it is an estimate.
traces_to: [M51, M20, M19, DT-001, DT-010, DT-014, DT-015, DT-020, MD-037, MD-040, MD-041, RP-009, 05-06 NFR-100]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-011_Sales_Register_Mushak_6_2_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.2 — sales book. **The prescribed column set must be obtained from the enacted Rules and verified at G6**
    verified: 2026-08-15
    class: P1
  - source: Mushak 6.1 is the purchase book and Mushak 6.2 the sales book; both must be maintained alongside issued challans
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-100 — Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-011 — Sales Register (Mushak 6.2)

> ⚠ **Tier S — the form is prescribed.** Column set, order and totals are the instrument's.
> **Nothing below is verified. Gate G6 is mandatory and unwaivable (`WV-02`).**
>
> **This register is not a report. It is a statutory record.** The distinction matters: a report
> is generated when someone asks for it, from whatever the data says today. A statutory record
> is **maintained continuously**, is complete for its period, and does not change when the
> underlying master data changes.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory sales register (sales book)** |
| Owning module | `M51`, with `M20` and `M19` |
| Statutory | **Yes — Tier S.** VAT & SD Rules 2016, Form Mushak 6.2 |
| Recipient(s) | NBR on inspection, external tax adviser, internal audit, the `DT-014` return preparer |
| Languages | **Bilingual.** The prescribed form's language governs (`DT-010` G6 Q2) |
| Output formats | **A4 landscape** (column count requires it) · PDF/A-3 archive per period · structured export for filing |
| Numbering mask | Not a sequenced document. Identified by **entity + period** |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 Its position in the chain

```
DT-010 challans issued  ──┐
DT-015 credit/debit notes ─┼──► DT-011 sales register ──► DT-014 Mushak 9.1 return
DT-020 consolidated invoices ┘                              ▲
                                                            │
DT-012 purchase register (input VAT) ───────────────────────┘
```

| # | Rule |
|---|---|
| **P-11-a** | **Every issued challan appears exactly once.** Not once per line, not once per payment — once per challan |
| **P-11-b** | **Every cancelled and void challan appears too**, marked as such. This is how the gap-free sequence (`SEQ-01`) is demonstrated to an inspector |
| **P-11-c** | Credit and debit notes appear as their own rows, referencing the original challan (`DT-015`) |
| **P-11-d** | The register's output-VAT total **must equal** the output-VAT figure carried into `DT-014`. A difference is a reconciliation failure, never a rounding explanation |

---

## 2. Statutory Requirements

> All rows **unverified pending G6**. The column set below is the programme's working assumption
> and is replaced wholesale by the prescribed set once obtained.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title — *Mushak 6.2* | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Registered person's name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Tax period covered | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Date of supply, per entry | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Challan number, per entry | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Buyer name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| Description of goods or services | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Quantity and unit | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| Value excluding VAT | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| SD amount where applicable | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| VAT rate and amount | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| Total including VAT | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Period totals | VAT & SD Rules 2016 — **pending G6** | pending | Totals row |
| Signature of the registered person or authorised officer | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 G6 questions specific to this register

| # | Question |
|---|---|
| **R1** | Provide the current prescribed Mushak 6.2. Is our column set complete and correctly ordered? |
| **R2** | Is the register maintained **per tax period** or continuously with period cut-offs? |
| **R3** | Must it be maintained per branch, per entity, or consolidated? Our operating model is 51+ branches |
| **R4** | Is an electronic register acceptable, and if so must it be printed and signed per period? |
| **R5** | How are cancelled and void challans presented? |
| **R6** | How are credit and debit notes (`DT-015`) presented — as negative rows or a separate schedule? |
| **R7** | Are exports and zero-rated supplies segregated? |
| **R8** | What is the correction procedure once a period's register has supported a filed return? |

---

## 3. Layout

**Primary format: A4 landscape** — the prescribed column count does not fit portrait.

| Zone | Content | Bilingual |
|---|---|---|
| Header | Prescribed title, entity, BIN, VAT circle, **tax period**, branch scope | Per the instrument |
| Party block | Not used — parties appear per row | — |
| Body | One row per challan, in **challan-number order**, with cancelled and void rows in place | Column headers per the instrument |
| Totals | Period totals by rate band, plus a grand total row | Arabic numerals |
| Statutory block | Prescribed declaration by the registered person | Per the instrument |
| Signature | Authorised signatory, per period | — |
| Footer | Entity, period, `page n of m`, generation timestamp | English |

| # | Rule |
|---|---|
| **L-11-a** | Rows are ordered by **challan number**, not by date or value. An inspector reads it as a sequence and looks for gaps |
| **L-11-b** | The column header row repeats on **every** page (`VB-004` G-06) |
| **L-11-c** | Period totals never appear alone on a continuation page (`VB-004` G-05) |
| **L-11-d** | The generation timestamp and the **source data cut-off** both print. A register generated at 09:00 on the 3rd covers data as at a stated moment, and that moment is part of the record |
| **L-11-e** | Totals subtotal by rate band before the grand total, matching `DT-010` FM-10-b and the `DT-014` schedule structure |

---

## 4. Field Mapping

### 4.1 Header

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Registered person | নিবন্ধিত ব্যক্তি | `MD-002.entity_legal_name` | Text | ✔ |
| BIN | বিআইএন | `MD-002.bin` | Monospace | ✔ |
| Address | ঠিকানা | `MD-002.registered_address` | Text | ✔ |
| VAT circle / division | ভ্যাট সার্কেল / বিভাগ | `MD-002.vat_circle`, `.vat_division` | Text | ✔ |
| Tax period | কর মেয়াদ | `MD-041` fiscal period | `MM/YYYY` or range | ✔ |
| Branch scope | শাখার পরিধি | `MD-003` scope | Text | ✔ **per G6 R3** |
| Generated at / data as at | তৈরির সময় / তথ্য সময় | System | `DD/MM/YYYY HH:mm` | ✔ |

### 4.2 Row columns

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Serial | ক্রমিক | Computed | Integer | ✔ |
| Date of supply | সরবরাহের তারিখ | `invoice.tax_point_date` | `DD/MM/YYYY` | ✔ |
| Challan no. | চালান নং | `DT-010` reference | Monospace | ✔ |
| Status | অবস্থা | `invoice.status` | Enum: issued / cancelled / void | ✔ **per G6 R5** |
| Buyer name | ক্রেতার নাম | `party.display_name` | Text | ✔ |
| Buyer BIN | ক্রেতার বিআইএন | `party.bin` | Monospace | Where registered |
| Description | বিবরণ | Aggregated line description | Text | ✔ |
| Quantity / unit | পরিমাণ / একক | Aggregated | Number + `MD-023` | ✔ |
| Value excl. VAT | মূল্য (ভ্যাট ব্যতীত) | `invoice.taxable_value` | BDT, 2 dp | ✔ |
| SD | সম্পূরক শুল্ক | `invoice.sd_amount` | BDT, 2 dp | Where applicable |
| VAT rate | ভ্যাট হার | `MD-037.rate_pct` | %, 3 dp | ✔ |
| VAT amount | ভ্যাট পরিমাণ | `invoice.vat_amount` | BDT, 2 dp | ✔ |
| Total incl. VAT | ভ্যাটসহ মোট | Computed | BDT, 2 dp | ✔ |
| Adjustment reference | সমন্বয় সূত্র | `DT-015` reference | Monospace | Credit/debit rows |

| # | Rule |
|---|---|
| **FM-11-a** | A challan spanning multiple rate bands occupies **one row per band** under one challan number, or a single row with a band breakdown — **G6 R1 decides**. It is never blended |
| **FM-11-b** | Cancelled and void challans carry zero values with a status marker, not omitted rows |
| **FM-11-c** | The register is generated **from posted invoice records**, never from the invoice PDF archive. The archive is evidence; the ledger is the source |
| **FM-11-d** | An invoice posted after the period's register was finalised **cannot** be silently absorbed. It follows the G6 R8 correction procedure |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `SEQ-01` (`MD-040`) | The gap-free sequence obligation is **demonstrated** by this register |
| `TAX-04` (`MD-037`) | Each row carries the rate effective at its tax point, not the current rate |
| `BRU-FIN-05` | The period cannot be closed while unposted entries exist in it — the register would be incomplete |
| `BRU-FIN-06` | A hard-closed period reopens only on CFO approval, logged. **Reopening invalidates a finalised register and triggers G6 R8** |
| `BRU-FIN-08` | Marketplace principal-or-agent treatment determines whether a marketplace supply appears here at all |
| `BRU-DMS-01` / `BRU-DMS-02` | Retention and legal hold |

### 5.1 Finalisation

| # | Rule |
|---|---|
| **FZ-01** | The register is **finalised** for a period. A finalised register is immutable and archived as PDF/A-3 |
| **FZ-02** | Finalisation happens **before** the `DT-014` return is prepared, not after. The return is built from the register, never the other way round |
| **FZ-03** | Finalisation is approved by the Finance Manager and recorded with the approver's identity and timestamp |
| **FZ-04** | A post-finalisation change produces a **supplementary register** for the period, referencing the original. The original is never regenerated (`CP-10`) |
| **FZ-05** | The finalised register's totals are reconciled to `M19` general-ledger output-VAT balances before finalisation. An unreconciled difference blocks it |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Period register** | Monthly, the governing rendition | Full prescribed form, finalised and signed |
| **Per-branch register** | Where G6 R3 requires branch-level maintenance | One register per branch, plus a consolidation |
| **Draft / working** | Mid-period review | Watermarked **DRAFT**, no signature block, cannot be filed (`RC-05`) |
| **Supplementary** | Post-finalisation correction (`FZ-04`) | References the original register and states only the delta |
| **Structured export** | Filing and adviser review | CSV/XML matching the prescribed column set; **the printed register remains the record** |
| **Export / zero-rated segregation** | Where G6 R7 requires it | Segregated section with its own totals |

---

## 7. Worked Example

> **Specimens are produced only after G6 delivers the prescribed form** (`DT-010` §7 rule).

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-011-S1` | One month, 2,400 challans, single entity | Base rendition, page-break and header repeat |
| `DT-011-S2` | Period containing 3 cancelled and 1 void challan | `FM-11-b` and the gap demonstration |
| `DT-011-S3` | Period containing credit and debit notes | `P-11-c` presentation per G6 R6 |
| `DT-011-S4` | Mixed rate bands | `FM-11-a` and `L-11-e` band subtotals |
| `DT-011-S5` | Supplementary register after a reopened period | `FZ-04` |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Tax with Finance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser, against the enacted Rules** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |
| Per-period finalisation | Finance Manager | Per period | Recorded in `M19` with timestamp (`FZ-03`) |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | None. Identified by **entity + branch scope + tax period** |
| Gap policy | n/a for the register; the register **evidences** the challan sequence's gap-free state |
| Archive format | **PDF/A-3 at finalisation**, plus the structured export |
| Retention | **At least 5 years** from the end of the tax period — **pending G6** |
| Re-render | **Prohibited after finalisation.** A regenerated register would reflect today's data and would differ from the one that supported the filed return |
| Reprint | Watermarked **COPY**, logged |
| Reconciliation evidence | The `M19` reconciliation supporting `FZ-05` is archived with the register |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | Every row originates in a challan issued from it |
| [`DT-012_Purchase_Register_Mushak_6_1.md`](DT-012_Purchase_Register_Mushak_6_1.md) | The input-side counterpart |
| [`DT-014_VAT_Return_Pack_Mushak_9_1.md`](DT-014_VAT_Return_Pack_Mushak_9_1.md) | Built from this register (`FZ-02`) |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | Adjustment rows |
| [`DT-020_Consolidated_Corporate_Invoice.md`](DT-020_Consolidated_Corporate_Invoice.md) | Its constituent challans appear here |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Which codes feed 6.2 |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Tax periods and filing deadlines |
| `RP-009` Statutory and Regulatory Report Format Register | Where the register is produced and reconciled |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | The operational sequence |
| `TS-009` UAT Script Pack — Finance Roles | Where completeness and reconciliation are proven |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Record-not-report principle, challan-order rule, cancelled/void presentation, eight-question G6 list, five finalisation rules, supplementary-register mechanism | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Column set stated as indicative and unverified, with the replacement rule
- [x] G6 question list specific to this register
- [x] Finalisation rules defined, including the reconciliation gate (`FZ-05`)
- [x] Supplementary-register mechanism replaces regeneration
- [x] All internal links resolve
- [ ] **G6 — prescribed form obtained and column set verified** — **outstanding, unwaivable (`WV-02`)**
- [ ] G6 R3 branch-vs-consolidated determination — **outstanding; affects `MD-040` and `M51` design**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
