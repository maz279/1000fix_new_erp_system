---
id: DT-013
title: VDS Certificate — Mushak 6.6
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
reviewers: [External tax adviser, Finance, Accounts Payable, Procurement, Internal Audit]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The VAT-deducted-at-source certificate issued to a supplier when the company withholds VAT from
  their payment and deposits it to the treasury. The supplier cannot claim a decreasing adjustment
  without it and will, correctly, withhold service until they receive it. Issuing it late or not
  at all converts a routine deduction into a supplier dispute and a compliance failure.
traces_to: [M51, M52, M16, M19, DT-001, DT-012, DT-014, DT-023, MD-002, MD-016, MD-037, MD-040, BRU-FIN-09, TAX-06]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-013_VDS_Certificate_Mushak_6_6_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.6 — VAT withholding certificate. **The prescribed form must be obtained from the enacted Rules and verified at G6**
    verified: 2026-08-15
    class: P1
  - source: A withholding entity deducts VAT from the supplier's invoice, deposits it to the treasury, and issues Mushak 6.6 to the supplier — commonly stated as within three working days of deposit. **The deadline must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: The supplier uses the Mushak 6.6 to claim a decreasing adjustment in their own Mushak 9.1, in the month of payment or within a subsequent window
    verified: 2026-08-15
    class: P2
  - source: project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037 TAX-06 — a VDS code requires the deducting entity to have is_vds_authority TRUE in MD-002
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-013 — VDS Certificate (Mushak 6.6)

> ⚠ **Tier S — the form is prescribed. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **This certificate is somebody else's money.** We deduct VAT from a supplier's payment and pay
> it to the treasury on their behalf. Until they hold this certificate, they have paid the tax
> and cannot prove it.
>
> It is the only document in this category with a **hard external deadline measured in days**.
> Every other statutory document is due at a period end. This one is due almost immediately after
> the deposit — and the deadline is the first thing G6 must confirm.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory VAT withholding certificate** |
| Owning module | `M51`, with `M52` Accounts Payable |
| Statutory | **Yes — Tier S.** VAT & SD Rules 2016, Form Mushak 6.6 |
| Recipient(s) | Supplier (original), company record, NBR on demand |
| Languages | **Bilingual.** The prescribed form's language governs |
| Output formats | A4 portrait · PDF for email delivery to the supplier · **PDF/A-3 archive at issue** |
| Numbering mask | `MD-040` — statutory sequence, **`no_gaps`** |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |
| **Issue deadline** | **Within the prescribed window after treasury deposit — commonly stated as 3 working days. `G6 V2` confirms** |

### 1.1 Preconditions — the certificate cannot issue without these

| # | Precondition | Rule |
|---|---|---|
| 1 | The entity is a **VDS withholding authority** | `TAX-06`, `MD-002.is_vds_authority` |
| 2 | The supply is within a **VDS-applicable category** at the applicable rate | `MD-037` — **rates pending G6** |
| 3 | The deduction has been made from an actual payment | `M52` |
| 4 | **The deducted amount has been deposited to the treasury** | The certificate certifies the deposit, not the deduction |
| 5 | The treasury challan / deposit reference exists | `M50` Treasury |
| 6 | The supplier's BIN is recorded and verified | `MD-016` |

> **Precondition 4 is the one that is skipped.** Issuing a certificate on deduction rather than
> on deposit certifies something that has not happened. The system issues on **deposit
> confirmation**, and the gap between the two is a monitored ageing metric (§5.1).

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title — *Mushak 6.6* | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| **Withholding entity** name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Deductor block |
| **Supplier** name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Supplier block |
| Certificate number and date | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Supplier's challan number and date | VAT & SD Rules 2016 — **pending G6** | pending | Body |
| Description of the supply | VAT & SD Rules 2016 — **pending G6** | pending | Body |
| Value of the supply | VAT & SD Rules 2016 — **pending G6** | pending | Body |
| **VAT rate applied and amount deducted** | `MD-037` — **rate pending G6** | pending | Body |
| **Treasury deposit reference and date** | VAT & SD Rules 2016 — **pending G6** | pending | Deposit block |
| Economic / accounting code of deposit | VAT & SD Rules 2016 — **pending G6** | pending | Deposit block |
| Declaration by the withholding entity | VAT & SD Rules 2016 — **pending G6** | pending | Statutory block |
| Signature and seal of the authorised officer | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 G6 questions specific to this certificate

| # | Question |
|---|---|
| **V1** | Provide the current prescribed Mushak 6.6. Is our element list complete and correctly ordered? |
| **V2** | **What is the issue deadline after deposit, and from what event does it run?** |
| **V3** | Which supply categories attract VDS, and at what rates, for a business of our profile? |
| **V4** | Are we a withholding entity by status, by turnover, by counterparty, or by supply type? |
| **V5** | May the certificate be delivered electronically, or must a physical original be provided? |
| **V6** | What is the consequence of late issue, and what is the remedy? |
| **V7** | How is a certificate corrected or cancelled after issue? |
| **V8** | Within what window may the supplier claim the decreasing adjustment, and does our issue date affect it? |

> **V8 matters to the supplier, not to us — which is exactly why we must know it.** If our late
> issue costs a supplier their adjustment window, we have caused them a loss and created a
> commercial dispute we will lose.

---

## 3. Layout

**Primary format: A4 portrait.** Brand yields to the prescribed form (`VB-004` S-01).

| Zone | Content | Bilingual |
|---|---|---|
| Header | Prescribed title, certificate number, date | Per the instrument |
| Party block | **Deductor block** (us) and **supplier block**, in the prescribed order | Per the instrument |
| Body | Supply reference, value, rate, deducted amount | Per the instrument |
| Totals | Deducted amount, stated in figures **and words** | Arabic numerals |
| Statutory block | Prescribed declaration and the **treasury deposit particulars**, verbatim | Per the instrument |
| Signature | Authorised officer, with seal where prescribed | — |
| Footer | Certificate reference, `page n of m` | English |

| # | Rule |
|---|---|
| **L-13-a** | The prescribed form is reproduced exactly. No brand colour, no re-ordering |
| **L-13-b** | The treasury deposit reference is **as prominent as the deducted amount**. It is the evidence the supplier needs |
| **L-13-c** | The certificate is one page. If the prescribed form permits multiple supplies, a schedule attaches with `page n of m` on both |
| **L-13-d** | The statutory declaration never splits |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Certificate no. | সনদ নং | `MD-040` sequence | Monospace | ✔ |
| Certificate date | সনদের তারিখ | `vds_cert.issued_at` | `DD/MM/YYYY` | ✔ |
| Withholding entity | কর্তনকারী প্রতিষ্ঠান | `MD-002.entity_legal_name` | Text | ✔ |
| Withholding entity BIN | কর্তনকারীর বিআইএন | `MD-002.bin` | Monospace | ✔ |
| Withholding entity address | ঠিকানা | `MD-002.registered_address` | Text | ✔ |
| Supplier name | সরবরাহকারীর নাম | `MD-016.vendor_name` | Text | ✔ |
| **Supplier BIN** | **সরবরাহকারীর বিআইএন** | `MD-016.bin` | Monospace | ✔ |
| Supplier address | সরবরাহকারীর ঠিকানা | `MD-016.address` | Text | ✔ |
| Supplier challan no. / date | সরবরাহকারীর চালান | `ap_invoice.supplier_challan_no`, `.date` | Monospace, date | ✔ |
| Description of supply | সরবরাহের বিবরণ | `ap_invoice` line summary | Text | ✔ |
| Value of supply | সরবরাহের মূল্য | `ap_invoice.taxable_value` | BDT, 2 dp | ✔ |
| VDS rate | কর্তনের হার | `MD-037.rate_pct` | %, 3 dp | ✔ **pending G6 V3** |
| **Amount deducted** | **কর্তিত পরিমাণ** | `ap_invoice.vds_amount` | BDT, 2 dp | ✔ |
| Amount in words | কথায় | Computed | Text | ✔ |
| Payment date | পরিশোধের তারিখ | `payment.paid_at` | `DD/MM/YYYY` | ✔ |
| **Treasury deposit reference** | **কোষাগার জমার সূত্র** | `M50.treasury_challan_ref` | Monospace | ✔ |
| **Deposit date** | **জমার তারিখ** | `M50.deposited_at` | `DD/MM/YYYY` | ✔ |
| Deposit code | জমার কোড | `M50.economic_code` | Monospace | ✔ **pending G6 V1** |
| Bank / branch of deposit | জমার ব্যাংক / শাখা | `MD-038.bank_branch` | Text | ✔ |
| Authorised officer | অনুমোদিত কর্মকর্তা | `employee.display_name` + designation | Text | ✔ |
| Seal | সিল | Where prescribed | Image | Per G6 V1 |

| # | Rule |
|---|---|
| **FM-13-a** | Every field derives from a posted record. **Nothing on this certificate is typed** — it certifies facts, and typed facts are unverified facts |
| **FM-13-b** | The certificate cannot render without a treasury deposit reference (precondition 4) |
| **FM-13-c** | The supplier's BIN is validated against `MD-016` before issue. A certificate to a wrong BIN is useless to the supplier and irrecoverable |
| **FM-13-d** | Amount in words prints in the prescribed language; Arabic numerals inside Bengali text (`VB-004` BL-05) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `TAX-06` (`MD-037`) | A VDS code requires `MD-002.is_vds_authority` TRUE. Without it, no deduction and no certificate |
| `TAX-03` (`MD-037`) | An unverified tax code cannot be activated — no VDS may be deducted at an unverified rate |
| `BRU-FIN-09` | TDS/VDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise |
| `BRU-SCM-01` | The underlying payable must be three-way matched |
| `BRU-SCM-03` | Segregation of duties between vendor creation and invoice approval |
| `BRU-DMS-03` | An issued certificate is never edited; correction follows **G6 V7** |

### 5.1 The issue-deadline control

The only hard external clock in the category. It is managed as an operational control, not as a
best effort.

| # | Control |
|---|---|
| **DL-01** | The clock starts at **treasury deposit confirmation**, per G6 V2 |
| **DL-02** | Certificate generation is **automatic** on deposit confirmation. There is no queue for a human to work through |
| **DL-03** | Delivery to the supplier is automatic — email to the `MD-016` registered address, plus availability in `P05` (`NT-011`) |
| **DL-04** | Undeliverable certificates raise an exception the same day, not at month end |
| **DL-05** | An ageing report of deduction-to-deposit and deposit-to-issue is produced **daily** and escalates to the Finance Manager past the threshold |
| **DL-06** | A certificate not issued within the prescribed window is reported as a **compliance incident**, not an operational delay, and follows `CG-013` escalation |
| **DL-07** | The deduction-to-deposit gap is monitored separately. Deducting and not depositing is a materially more serious failure than issuing late |

> **DL-07 is the one that ends careers.** Money deducted from a supplier and not deposited to the
> treasury is not a compliance defect; it is the company holding tax it collected on the state's
> behalf. The daily report exists to make that impossible to overlook.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard A4** | Per supply, the default | The prescribed form |
| **Multi-supply with schedule** | Where the prescribed form permits a period certificate | Schedule attached, `page n of m` on both, per G6 V1 |
| **Electronic delivery** | The default channel | Same content; delivery evidence retained. Physical original where **G6 V5** requires it |
| **Corrected certificate** | Error found after issue | Per **G6 V7**. Until answered, the working assumption is cancel-and-reissue with both retained (`RC-04`) |
| **Duplicate for supplier** | Supplier lost the original | Watermarked **COPY**, logged. **Never a second original** (`RC-02`) |
| **Government / large-taxpayer supplier** | Where the counterparty has its own format expectations | The prescribed form governs regardless; supplementary data may be provided separately |

---

## 7. Worked Example

> **Specimens produced only after G6 delivers the prescribed form.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-013-S1` | Single service supply, VDS deducted and deposited | Base prescribed rendition |
| `DT-013-S2` | Deposit reference and date prominent | `L-13-b` |
| `DT-013-S3` | Multi-supply schedule | `L-13-c` pagination |
| `DT-013-S4` | Corrected certificate after a wrong supplier BIN | `RC-04` and G6 V7 path |
| `DT-013-S5` | Duplicate issued to a supplier | `RC-02` — copy, not a second original |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Tax with Finance | 2026-08-15 | Draft issue |
| Reviewer — Accounts Payable | *pending* | | |
| Reviewer — Procurement | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040`, statutory, **`no_gaps`**. Format pending G6 V1 |
| Reset | Fiscal year, subject to G6 |
| Archive format | **PDF/A-3 at issue** |
| Retention | **At least 5 years** from the end of the tax period — pending G6 |
| Delivery evidence | Email delivery receipt or portal download log retained with the certificate |
| Re-render | **Prohibited.** The certificate states facts as at deposit (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged (`RC-01`, `RC-03`) |
| Cancellation | Per G6 V7; until answered, cancel-and-reissue with both retained and the sequence gap-free |
| Reconciliation | Total certificates issued in a period reconciles to the VDS deducted in `DT-012` and to the treasury deposits in `M50` — **a three-way reconciliation, monthly** |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-012_Purchase_Register_Mushak_6_1.md`](DT-012_Purchase_Register_Mushak_6_1.md) | Carries the certificate reference on every VDS row |
| [`DT-014_VAT_Return_Pack_Mushak_9_1.md`](DT-014_VAT_Return_Pack_Mushak_9_1.md) | Where deductions made are reported |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The mirror case — a certificate we **expect to receive** where a customer withholds from us |
| [`../05C_Supply_Chain_and_Logistics/DT-023_Purchase_Order.md`](../05C_Supply_Chain_and_Logistics/DT-023_Purchase_Order.md) | Where the VDS position is declared to the supplier up front |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Supplier BIN, VDS applicability, delivery address |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Deposit bank and branch |
| [`NT-011_Email_Template_Library_Vendor_and_Supplier.md`](../../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) | The delivery message |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | Where the three-way reconciliation is run |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | The operational procedure and the daily ageing check |
| `RP-009` Statutory and Regulatory Report Format Register | Ageing and exception reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six preconditions with the deposit-not-deduction rule, eight-question G6 list, seven issue-deadline controls including the deduct-without-deposit monitor, three-way monthly reconciliation | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Preconditions stated, with deposit — not deduction — as the trigger
- [x] Issue-deadline treated as a monitored control with escalation, not a target
- [x] Deduct-without-deposit monitoring stated explicitly (`DL-07`)
- [x] Three-way reconciliation defined (§9)
- [x] All internal links resolve
- [ ] **G6 — prescribed form obtained and elements verified** — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6 V2 — issue deadline confirmed** — **outstanding; `DL-01`…`DL-06` cannot be configured without it**
- [ ] G6 V3/V4 — VDS-applicable categories, rates and our withholding status — **outstanding; blocks `MD-037` VDS codes**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
