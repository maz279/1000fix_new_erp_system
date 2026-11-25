---
id: DT-025
title: Return to Vendor and Debit Advice
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory with Finance
author: Inventory with Finance, Tax and Content Design
reviewers: [External tax adviser, Tax, Finance, Procurement, Logistics, Internal Audit]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Return authorisation, reason, credit expectation and logistics reference — and, where VAT was
  claimed on the original purchase, the statutory debit note that reverses it. Defective parts
  returned without documentation become an unrecoverable write-off: the supplier denies receipt,
  the input claim stands on a purchase we no longer hold, and the stock record shows goods that
  are not there.
traces_to: [M15, M52, M51, M41, M42, DT-001, DT-012, DT-015, DT-023, DT-024, DT-027, MD-016, MD-026, MD-037, MD-040, BRU-INV-07, BRU-SCM-01, BRU-DMS-03]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.8 debit note — **the form and its applicability to a return to vendor must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — procurement documents remain English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-07 — goods failing inspection go to quarantine and never to available stock
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-025 — Return to Vendor and Debit Advice

> ⚠ **Tier S — the debit note element is prescribed. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **This document does two jobs and they must not be confused.** The **return authorisation** is
> a logistics and custody instrument: it moves goods out of our premises and evidences that the
> supplier received them. The **debit advice** is a financial and tax instrument: it reverses the
> input VAT and the payable.
>
> They are issued together and printed as one pack, but the debit advice element is the one G6
> governs.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Return authorisation + statutory debit advice |
| Owning module | `M15` Spare Parts and Inventory, with `M52` and `M51` |
| Statutory | **Yes — Tier S** for the debit advice element. Form pending G6 |
| Recipient(s) | Supplier (original), warehouse, accounts payable, carrier, internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | A4 portrait (two-part pack) · PDF · accompanies the goods in transit |
| Numbering mask | `MD-040` — `RTV-{entity}-{location}-{yy}-{seq:06d}`; the debit note carries its own **statutory** sequence |
| Retention period | **At least 5 years** where a VAT adjustment is made — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 Why returns become write-offs

The failure modes this document exists to prevent, in the order they occur:

| # | Failure | Prevented by |
|---|---|---|
| 1 | Goods leave without authorisation | Numbered RTV required before dispatch |
| 2 | Supplier denies receiving them | Proof of delivery to the supplier (`DT-027`, `DT-028`) attached |
| 3 | No credit is ever issued | Credit expectation stated with a due date and chased |
| 4 | Input VAT stays claimed on goods we no longer have | Debit advice reverses it in the same period |
| 5 | Stock record still shows the goods | RTV posts the stock movement at dispatch, not at credit |
| 6 | Nobody owns the chase | Named owner and ageing report |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed debit-note form | VAT & SD Rules 2016, Mushak 6.8 — **pending G6** | pending | Debit advice part |
| Reference to the original supplier challan | VAT & SD Rules 2016 — **pending G6** | pending | Debit advice part |
| Issuer and recipient identity with BIN | VAT & SD Rules 2016 — **pending G6** | pending | Both parts |
| Value and VAT of the adjustment | `MD-037` — **pending G6** | pending | Debit advice part |
| Reason for the adjustment | VAT & SD Rules 2016 — **pending G6** | pending | Both parts |
| Movement documentation for goods in transit | `DT-027` — **pending G6** | pending | Return authorisation part |

### 2.1 G6 questions

| # | Question |
|---|---|
| **RV1** | Is a return to vendor evidenced by our debit note (Mushak 6.8), by the supplier's credit note (6.7), or by both? |
| **RV2** | In which tax period must the input-VAT reversal be made — the period of return, or of the original claim? |
| **RV3** | What movement documentation must accompany goods returned to a supplier? (paired with `DT-027`) |
| **RV4** | Is the treatment different where the input VAT was not claimed, or where the goods were never accepted into stock? |
| **RV5** | What is the treatment of a return where the supplier is unregistered? |

---

## 3. Layout

**Two-part A4 pack**, printed and issued together.

| Part | Zone | Content |
|---|---|---|
| **Part 1 — Return authorisation** | Header | RTV number, date, authorising officer |
| | Party | Supplier and return-to address left; our location and contact right |
| | Body | Lines returned, reason, condition, packaging, carrier and consignment reference |
| | Signature | Warehouse dispatcher, carrier acknowledgement, supplier receipt acknowledgement |
| **Part 2 — Debit advice** | Header | Debit note number (**statutory sequence**), date |
| | Party | Prescribed issuer and recipient blocks |
| | Body | Original challan reference, value, VAT reversed |
| | Statutory block | Prescribed declaration |
| | Signature | Authorised signatory |

| # | Rule |
|---|---|
| **L-25-a** | The two parts are printed together but are **separately numbered and separately archived**. The debit advice must be producible on its own to a tax inspector |
| **L-25-b** | Part 1 travels with the goods. Part 2 goes to the supplier's finance function |
| **L-25-c** | The reason appears identically on both parts. Different reasons on the two parts is the kind of inconsistency an audit finds immediately |
| **L-25-d** | The debit advice may be **suppressed** where no input VAT was claimed (per **G6 RV4**), in which case Part 1 states plainly that no VAT adjustment arises |

---

## 4. Field Mapping

### 4.1 Part 1 — Return authorisation

| Label | Source field | Format | Required |
|---|---|---|:--:|
| RTV no. | `MD-040` sequence | Monospace | ✔ |
| RTV date | `rtv.authorised_at` | `DD/MM/YYYY` | ✔ |
| Authorised by | `employee.display_name` + ID | Text | ✔ |
| Supplier name, code, BIN | `MD-016` | Text + monospace | ✔ |
| Return-to address | `MD-016.return_address` | Text | ✔ |
| Our location | `MD-004` / `MD-003` | Text | ✔ |
| Original PO no. | `DT-023` reference | Monospace | ✔ |
| Original GRN no. | `DT-024` reference | Monospace | ✔ |
| Supplier challan no. / date | `DT-024` capture | Monospace | ✔ |
| Item code / description | `MD-022` | Monospace + text | ✔ |
| Quantity returned | `rtv.line.qty` | Number + `MD-023` | ✔ |
| Serial / batch returned | `rtv.line.serials[]` | Monospace | **✔ serialised items** |
| **Reason code** | `MD-026.reason_code` | Code + text | ✔ |
| Condition on return | `rtv.line.condition` | Enum: unused / opened / faulty on arrival / failed inspection / wrong item / expired | ✔ |
| Evidence attached | `M24` reference + count | Reference | **✔ for faulty and failed-inspection returns** |
| Carrier / consignment ref | `DT-027` reference | Monospace | ✔ |
| Dispatch date | `rtv.dispatched_at` | `DD/MM/YYYY` | ✔ |
| Proof of delivery to supplier | `DT-028` reference | Monospace | ✔ on completion |
| Credit expected | `rtv.credit_expected` | BDT, 2 dp | ✔ |
| Credit due by | `rtv.credit_due_by` | `DD/MM/YYYY` | ✔ |
| **Chase owner** | `employee.display_name` | Text | ✔ |

### 4.2 Part 2 — Debit advice

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Debit note no. | `MD-040` **statutory** sequence | Monospace | ✔ |
| Debit note date | `debit_note.issued_at` | `DD/MM/YYYY` | ✔ |
| Issuer name, address, BIN | `MD-002` | Text + monospace | ✔ |
| Recipient name, address, BIN | `MD-016` | Text + monospace | ✔ |
| Original challan no. / date | `DT-024` capture | Monospace | ✔ |
| Description of goods | `MD-022` | Text | ✔ |
| Quantity | `rtv.line.qty` | Number | ✔ |
| Value excl. VAT | Computed at original price | BDT, 2 dp | ✔ |
| VAT rate | **The rate on the original challan** | %, 3 dp | ✔ |
| **VAT reversed** | Computed | BDT, 2 dp | ✔ |
| Total adjustment | Computed | BDT, 2 dp | ✔ |
| Amount in words | Computed | Text | ✔ |
| Reason | `MD-026` | Text | ✔ |
| Declaration | Prescribed | Text | ✔ pending G6 |
| Authorised signatory | `employee.display_name` + designation | Text | ✔ |

| # | Rule |
|---|---|
| **FM-25-a** | The VAT reversed uses **the rate on the original challan**, never today's rate (`TAX-04`) |
| **FM-25-b** | Faulty and failed-inspection returns require photographic evidence attached. A supplier will contest a fault they cannot see |
| **FM-25-c** | The **credit due-by date and a named chase owner** are mandatory. Unowned credit expectations are the mechanism by which returns become write-offs |
| **FM-25-d** | Stock is relieved at **dispatch**, not at credit receipt. Goods physically gone but shown as on hand corrupt availability and drive false replenishment |
| **FM-25-e** | Serialised returns record the serials leaving, closing the `BRU-INV-08` traceability loop |
| **FM-25-f** | The quantity returned cannot exceed the quantity received on the referenced GRN |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-INV-07` | Quarantined goods are the usual source of a return; they never re-enter available stock |
| `BRU-SCM-01` | The three-way match is amended by the return; the payable reduces accordingly |
| `BRU-INV-08` | Serial capture on return |
| `BRU-DMS-03` | Neither part is edited after issue; correction is a new document referencing it |
| `TAX-04` (`MD-037`) | Rate at the original tax point |
| `SEQ-01` (`MD-040`) | The debit-note sequence is statutory and gap-free |

### 5.1 Credit recovery discipline

| # | Rule |
|---|---|
| **CR-25-a** | Every RTV has a credit expectation, a due date and a named owner — even where the expectation is zero, which is stated explicitly |
| **CR-25-b** | Outstanding credits age on a report reviewed **weekly** by Procurement and Finance |
| **CR-25-c** | An overdue credit is set off against the next payment to that supplier where the PO terms permit, and the set-off is notified |
| **CR-25-d** | A credit outstanding beyond the escalation threshold goes to the vendor scorecard (`M42`) and to the account owner, not into a write-off queue |
| **CR-25-e** | Write-off requires Finance Manager approval with the chase history attached. **A return written off without a documented chase is a control failure, not a commercial loss** |
| **CR-25-f** | Supplier credit-issue performance is a scorecard metric alongside delivery and quality |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard RTV + debit advice** | Input VAT was claimed | Both parts |
| **RTV only** | No input VAT claimed, or goods never accepted (per **G6 RV4**) | Part 1 only; states no VAT adjustment arises |
| **Rejected at receipt** | Goods refused and returned with the delivering party | Issued at the counter with `DT-024`; no stock movement occurs at all |
| **Warranty return to supplier** | Faulty part within the supplier's warranty | Replacement expected rather than credit; the expectation field states which |
| **Consignment return** | Brand consignment stock (`BRU-INV-04`) | No value adjustment; title never passed to us |
| **Recall** | Supplier or manufacturer recall | Bulk return with the recall reference; traceability by serial or batch is the point |
| **Import return** | Foreign supplier (`M44`) | Export documentation, customs treatment and freight responsibility stated |
| **Return to a brand partner** | `M09` claim parts (`BRU-WTY-04`) | Returned under the brand agreement, not as a commercial return |

---

## 7. Worked Example

> **The debit advice specimen is produced only after G6 delivers the form.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-025-S1` | Failed-inspection return, input VAT claimed | Full two-part pack |
| `DT-025-S2` | Return with no VAT adjustment | `L-25-d` suppression |
| `DT-025-S3` | Serialised parts recall | Serial traceability |
| `DT-025-S4` | Credit overdue, set off against the next payment | `CR-25-c` |
| `DT-025-S5` | Rejected at receipt, goods never entered stock | Counter variant |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Inventory with Finance | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Procurement | *pending* | | |
| Reviewer — Logistics | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser (RV1–RV5)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequences | Two — `RTV-…` operational (`gaps_recorded`) and the debit note on a **statutory** sequence (`no_gaps`) |
| Archive format | **PDF/A-3** for the debit advice; standard PDF for the return authorisation |
| Retention | **At least 5 years** for the debit advice; `LG-009` operational for the authorisation, but not shorter than the debit advice where both exist |
| Evidence | Photographs, the GRN, the supplier challan and the proof of delivery are archived with the pack |
| Re-render | Prohibited |
| Reprint | Watermarked **COPY**, logged |
| Linkage | `DT-023` → `DT-024` → `DT-025` → supplier credit → payable adjustment, retrievable as one chain |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | The receipt being reversed |
| [`DT-023_Purchase_Order.md`](DT-023_Purchase_Order.md) | Return and rejection rights |
| [`DT-027_Delivery_Challan_and_Logistics_Manifest.md`](DT-027_Delivery_Challan_and_Logistics_Manifest.md) | Movement documentation for the return |
| [`DT-028_Proof_of_Delivery_and_Custody_Record.md`](DT-028_Proof_of_Delivery_and_Custody_Record.md) | Evidence the supplier received the goods |
| [`../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md`](../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md) | Where the reversal appears |
| [`../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md`](../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md) | The general adjustment-note rules this follows |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Return address and supplier identity |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | Where rejections originate |
| `RP-002` Report Catalogue by Role and Module | Credit ageing and scorecard |
| [`NT-011_Email_Template_Library_Vendor_and_Supplier.md`](../../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) | Return notification and credit chasing |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Two-part pack with separate numbering, six write-off failure modes addressed in order, stock-relieved-at-dispatch rule, six credit-recovery rules including documented-chase-before-write-off, eight variants | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] The two instruments separated, separately numbered and separately archived (`L-25-a`)
- [x] Credit expectation given a due date and a named owner (`FM-25-c`)
- [x] Stock relieved at dispatch, with the reason stated (`FM-25-d`)
- [x] Write-off requires a documented chase (`CR-25-e`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **G6 RV1/RV2 — instrument and reversal period** — **outstanding, unwaivable (`WV-02`)**
- [ ] G6 RV3 — movement documentation for returns — **outstanding; shared with `DT-027`**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
