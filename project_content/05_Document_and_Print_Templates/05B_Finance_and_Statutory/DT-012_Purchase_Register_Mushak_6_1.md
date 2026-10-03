---
id: DT-012
title: Purchase Register — Mushak 6.1
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
reviewers: [External tax adviser, Finance, Procurement, Internal Audit, Platform Engineering]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The statutory purchase register (purchase book) derived from every Mushak 6.3 challan received
  from suppliers. Input-VAT credit depends on it entirely: a purchase absent from this register
  is input VAT not claimed, which is lost money as well as a compliance defect. It is also where
  a defective supplier challan is caught, while the supplier can still be asked to correct it.
traces_to: [M51, M52, M16, M19, DT-001, DT-010, DT-013, DT-014, DT-024, DT-025, MD-016, MD-037, MD-041, RP-009]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-012_Purchase_Register_Mushak_6_1_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.1 — purchase book. **The prescribed column set must be obtained from the enacted Rules and verified at G6**
    verified: 2026-08-15
    class: P1
  - source: Mushak 6.1 is the purchase book and Mushak 6.2 the sales book; both must be maintained alongside issued and received challans
    verified: 2026-08-15
    class: P2
  - source: project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037 — is_reclaimable flag governing input-VAT recoverability
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-012 — Purchase Register (Mushak 6.1)

> ⚠ **Tier S — the form is prescribed. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> `DT-011` protects the company from a penalty. **This one protects the company's money.** Input
> VAT that is not registered is input VAT that is not claimed, and on a business buying spare
> parts at volume across 51+ branches, that is a recurring, invisible loss.
>
> It has a second job the sales register does not have: **it is the control point where a
> defective supplier challan is detected.** A supplier challan missing our BIN, carrying the
> wrong rate, or not conforming to the prescribed form, is a challan we cannot claim against —
> and the only moment we can realistically get it corrected is now.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory purchase register (purchase book)** |
| Owning module | `M51`, with `M52` Accounts Payable and `M16` Procurement |
| Statutory | **Yes — Tier S.** VAT & SD Rules 2016, Form Mushak 6.1 |
| Recipient(s) | NBR on inspection, external tax adviser, internal audit, the `DT-014` return preparer |
| Languages | **Bilingual.** The prescribed form's language governs |
| Output formats | **A4 landscape** · PDF/A-3 archive per period · structured export |
| Numbering mask | Not sequenced. Identified by **entity + period** |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 What must reach it

| Source | Document | Rule |
|---|---|---|
| Supplier supply | Supplier's Mushak 6.3 | Every received challan, whether or not the VAT is reclaimable |
| Goods receipt | `DT-024` GRN | Three-way match: PO ↔ GRN ↔ supplier challan (`BRU-SCM-01`) |
| Return to vendor | `DT-025` debit advice | Reverses the input claim |
| Import | Bill of entry and duty documents (`M44`) | Import VAT treatment — **G6 P4** |
| VDS deducted by us | `DT-013` Mushak 6.6 we issue | The deduction is evidenced separately but reconciles here |

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title — *Mushak 6.1* | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Registered person's name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Tax period | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Date of purchase, per entry | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Supplier's challan number and date | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| **Supplier name, address and BIN** | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| Description of goods or services | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Quantity and unit | VAT & SD Rules 2016 — **pending G6** | pending | Columns |
| Value excluding VAT | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| SD paid where applicable | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| **Input VAT amount** | VAT & SD Rules 2016 — **pending G6** | pending | Column |
| Whether the input is reclaimable | `MD-037.is_reclaimable`; VAT & SD Act 2012 — **pending G6** | pending | Column |
| Period totals | VAT & SD Rules 2016 — **pending G6** | pending | Totals row |
| Signature of the registered person or authorised officer | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 G6 questions specific to this register

| # | Question |
|---|---|
| **P1** | Provide the current prescribed Mushak 6.1. Is our column set complete and correctly ordered? |
| **P2** | What are the **conditions for input-VAT credit** — a conforming supplier challan, payment made, goods received, or a combination? |
| **P3** | Is there a **time limit** for claiming an input credit, and what is the treatment of a challan received late? |
| **P4** | How are imports treated in this register — by bill of entry, by supplier challan, or separately? |
| **P5** | Which of our purchase categories carry non-reclaimable input VAT? |
| **P6** | How is a return to vendor (`DT-025`) presented — negative row or separate schedule? |
| **P7** | Where we deduct VDS, how does the transaction appear here relative to the `DT-013` certificate we issue? |
| **P8** | What is the correction procedure once a period's register has supported a filed return? |

---

## 3. Layout

**Primary format: A4 landscape.** Structurally the mirror of `DT-011`, and deliberately so —
the two registers are read together and inconsistent layouts slow every inspection.

| Zone | Content | Bilingual |
|---|---|---|
| Header | Prescribed title, entity, BIN, VAT circle, tax period, branch scope | Per the instrument |
| Body | One row per received challan, in **date order within supplier**, or as prescribed | Per the instrument |
| Totals | Period totals by rate band; **reclaimable and non-reclaimable subtotalled separately** | Arabic numerals |
| Statutory block | Prescribed declaration | Per the instrument |
| Signature | Authorised signatory, per period | — |
| Footer | Entity, period, `page n of m`, generation timestamp and data cut-off | English |

| # | Rule |
|---|---|
| **L-12-a** | Reclaimable and non-reclaimable input VAT are **subtotalled separately**. Blending them produces a wrong `DT-014` claim, which is the most consequential error this register can make |
| **L-12-b** | Column headers repeat on every page; totals never appear alone on a continuation page |
| **L-12-c** | A row for a challan **flagged as defective** prints its defect code and is excluded from the reclaimable subtotal until corrected |
| **L-12-d** | Generation timestamp and data cut-off both print (`DT-011` L-11-d) |

---

## 4. Field Mapping

### 4.1 Row columns

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Serial | ক্রমিক | Computed | Integer | ✔ |
| Purchase date | ক্রয়ের তারিখ | `ap_invoice.tax_point_date` | `DD/MM/YYYY` | ✔ |
| Supplier challan no. | সরবরাহকারীর চালান নং | `ap_invoice.supplier_challan_no` | Monospace | ✔ |
| Supplier challan date | চালানের তারিখ | `ap_invoice.supplier_challan_date` | `DD/MM/YYYY` | ✔ |
| Supplier name | সরবরাহকারীর নাম | `MD-016.vendor_name` | Text | ✔ |
| **Supplier BIN** | **সরবরাহকারীর বিআইএন** | `MD-016.bin` | Monospace | **✔ — absence is a defect, see §5.1** |
| Description | বিবরণ | Aggregated line description | Text | ✔ |
| Quantity / unit | পরিমাণ / একক | Aggregated | Number + `MD-023` | ✔ |
| Value excl. VAT | মূল্য (ভ্যাট ব্যতীত) | `ap_invoice.taxable_value` | BDT, 2 dp | ✔ |
| SD paid | সম্পূরক শুল্ক | `ap_invoice.sd_amount` | BDT, 2 dp | Where applicable |
| VAT rate | ভ্যাট হার | `MD-037.rate_pct` | %, 3 dp | ✔ |
| **Input VAT** | **ইনপুট ভ্যাট** | `ap_invoice.vat_amount` | BDT, 2 dp | ✔ |
| Reclaimable | ফেরতযোগ্য | `MD-037.is_reclaimable` | Bool | ✔ |
| GRN reference | জিআরএন সূত্র | `DT-024` reference | Monospace | ✔ for goods |
| PO reference | ক্রয়াদেশ সূত্র | `DT-023` reference | Monospace | Where a PO exists |
| VDS deducted | উৎসে কর্তন | `ap_invoice.vds_amount` | BDT, 2 dp | Where we deducted |
| VDS certificate ref | কর্তন সনদ সূত্র | `DT-013` reference | Monospace | **✔ where VDS deducted** |
| Defect code | ত্রুটি কোড | §5.1 code | Code | Where flagged |

| # | Rule |
|---|---|
| **FM-12-a** | The register is built from **posted payables records**, matched to a received challan document in `M24`. A payable with no challan attached cannot claim input VAT |
| **FM-12-b** | Three-way match status is carried, not re-derived (`BRU-SCM-01`) |
| **FM-12-c** | Where VDS was deducted, the `DT-013` certificate reference is mandatory. A deduction with no issued certificate is both a supplier dispute and a compliance defect (`DT-013` §5) |
| **FM-12-d** | An import row references the bill of entry, per **G6 P4** |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SCM-01` | A vendor invoice cannot be approved for payment without a matched PO and goods receipt within tolerance |
| `BRU-SCM-03` | The same user cannot create a vendor and approve that vendor's invoice — the segregation that protects this register's integrity |
| `BRU-FIN-09` | TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise |
| `BRU-INV-07` | Goods failing inspection go to quarantine; the input claim position on quarantined goods is a **G6 P2** question |
| `TAX-06` (`MD-037`) | A VDS code requires the entity to be a VDS authority |
| `BRU-FIN-05` / `BRU-FIN-06` | Period-close and reopening rules, as for `DT-011` |

### 5.1 Supplier challan defect codes

The register's second job. A defect found here is recoverable; the same defect found at
inspection is not.

| Code | Defect | Consequence | Action |
|---|---|---|---|
| **D-1** | Our BIN missing or wrong | Input credit at risk | Request a corrected challan before payment |
| **D-2** | Supplier BIN missing or wrong | Challan may not be valid | Verify the supplier's registration; hold payment |
| **D-3** | Not on the prescribed form | Challan may not support a claim | Request a conforming Mushak 6.3 |
| **D-4** | Rate inconsistent with `MD-037` | Wrong VAT charged | Query with the supplier and the adviser |
| **D-5** | Arithmetic error | Wrong VAT amount | Request correction |
| **D-6** | Challan date outside the claim window | Credit may be time-barred — **G6 P3** | Escalate to Finance Manager |
| **D-7** | No challan received | No claim possible | Chase; withhold payment per the PO terms |
| **D-8** | Duplicate challan number from the same supplier | Possible duplicate claim | Block and investigate |

| # | Rule |
|---|---|
| **DF-01** | A defective challan is **flagged, not silently excluded**. An excluded row that nobody sees is a loss nobody chases |
| **DF-02** | Defect rates by supplier feed vendor scorecards (`M42`, `DT-024`). A supplier who cannot issue a conforming challan is a supplier who costs us money on every purchase |
| **DF-03** | `D-8` blocks payment outright pending investigation |
| **DF-04** | Defect resolution is tracked to closure; open defects at period end are reported to the Finance Manager before finalisation |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Period register** | Monthly, the governing rendition | Full prescribed form, finalised and signed |
| **Per-branch / per-warehouse** | Where G6 P1/R3 requires it | One per location plus a consolidation |
| **Draft / working** | Mid-period, defect chasing | Watermarked **DRAFT**; the defect columns are its main use |
| **Supplementary** | Post-finalisation correction | Delta only, referencing the original |
| **Import schedule** | Where G6 P4 requires segregation | Bill-of-entry-based rows with landed-cost linkage (`M44`) |
| **Structured export** | Filing and adviser review | CSV/XML matching the prescribed column set |
| **Defect exception report** | Weekly, operational | Not a statutory rendition. Defect rows only, by supplier, with age — this is the **money-recovery** view |

---

## 7. Worked Example

> **Specimens produced only after G6 delivers the prescribed form.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-012-S1` | One month, mixed suppliers, all conforming | Base rendition |
| `DT-012-S2` | Reclaimable and non-reclaimable mixed | `L-12-a` separate subtotals |
| `DT-012-S3` | Four defect codes present | `DF-01` flagging and exclusion from the reclaimable subtotal |
| `DT-012-S4` | VDS deducted, certificate issued | `FM-12-c` linkage to `DT-013` |
| `DT-012-S5` | Return to vendor within the period | `DT-025` presentation per G6 P6 |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Tax with Finance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Procurement | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | None. Identified by **entity + scope + tax period** |
| Archive format | **PDF/A-3 at finalisation**, plus structured export |
| Retention | **At least 5 years** from the end of the tax period — **pending G6** |
| Supporting evidence | **Every received supplier challan is retained as an image or PDF in `M24`**, linked to its register row, for the same period. The register alone does not evidence a claim |
| Re-render | Prohibited after finalisation |
| Reprint | Watermarked **COPY**, logged |
| Finalisation | Same five rules as `DT-011` §5.1, applied here (`FZ-01`…`FZ-05`), with the additional gate that **no unresolved `D-8` may exist** |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-011_Sales_Register_Mushak_6_2.md`](DT-011_Sales_Register_Mushak_6_2.md) | The output-side counterpart; finalisation rules are defined there |
| [`DT-013_VDS_Certificate_Mushak_6_6.md`](DT-013_VDS_Certificate_Mushak_6_6.md) | Certificates we issue against rows here |
| [`DT-014_VAT_Return_Pack_Mushak_9_1.md`](DT-014_VAT_Return_Pack_Mushak_9_1.md) | The input-VAT claim this register supports |
| [`../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Three-way match evidence |
| [`../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md`](../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md) | Reversal rows |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Supplier BIN and VDS applicability |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | Reclaimability and rate |
| `RP-009` Statutory and Regulatory Report Format Register | Production, reconciliation and the defect exception report |
| [`SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) | Where defects are caught operationally |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | The operational sequence |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Reclaimable/non-reclaimable separation, eight supplier-challan defect codes with actions, defect-to-vendor-scorecard linkage, eight-question G6 list, supplier-challan retention obligation | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Column set stated as indicative and unverified
- [x] Defect codes defined with consequence and action, not merely listed
- [x] Reclaimable/non-reclaimable subtotal separation stated as a rule
- [x] Supplier challan retention obligation stated (§9)
- [x] All internal links resolve
- [ ] **G6 — prescribed form obtained and column set verified** — **outstanding, unwaivable (`WV-02`)**
- [ ] G6 P2 input-credit conditions and P3 time limit — **outstanding; affects `M52` design**
- [ ] G6 P5 non-reclaimable purchase categories — **outstanding; blocks `MD-037` completion**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
