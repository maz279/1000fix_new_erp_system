---
id: DT-029
title: Physical Count and Stock Adjustment Sheet
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory with Finance
author: Inventory with Finance, Internal Audit and Content Design
reviewers: [Finance, Internal Audit, Tax, Warehouse Operations, Quality]
approver: Chief Financial Officer
content_class: A
purpose: >
  The count sheet, the variance record, the adjustment authorisation and the reason coding.
  Inventory adjustments without an authorised document are indistinguishable from theft, and
  stock records that are never counted are not records — they are assumptions that the general
  ledger, the VAT position and every availability promise are built on.
traces_to: [M15, M41, M19, M51, M23, DT-001, DT-012, DT-024, DT-026, DT-044, MD-004, MD-022, MD-026, MD-040, BRU-INV-06, BRU-INV-07, BRU-INV-08, BRU-SEC-07]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — DT-029 remains English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-06 — stock adjustments above threshold require approval with a reason code
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SEC-07 — incompatible duty combinations cannot be assigned; exceptions are time-boxed and reported
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-029 — Physical Count and Stock Adjustment Sheet

> ⚠ **Class A — statutory consequence.** Stock is an asset on the balance sheet and a component
> of the VAT position. An adjustment changes both. An unauthorised adjustment changes both
> without anyone deciding to.
>
> **Two documents in one pack, and the order matters.** The **count sheet** records what was
> physically found. The **adjustment sheet** records what was done about the difference. Producing
> them together, in that order, is what prevents the count from being written to match the system.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Physical count record + stock adjustment authorisation |
| Owning module | `M15` Spare Parts and Inventory, with `M41` and `M19` |
| Statutory | No prescribed form. **Class A** — VAT stock records and balance-sheet impact |
| Recipient(s) | Counters, inventory control, finance, internal audit, external audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | **A4 landscape** (count sheet column count) · handheld scanner capture · PDF |
| Numbering mask | `MD-040` — `CNT-{entity}-{location}-{yy}-{seq:06d}` count; `ADJ-{entity}-{location}-{yy}-{seq:06d}` adjustment |
| Retention period | `LG-009`; **not less than the tax retention period**, and available to external audit for the year it affects |

### 1.1 Count types

| Type | Frequency | Scope | Blind |
|---|---|---|:--:|
| **Cycle count** | Continuous, by ABC class | A rotating subset | ✔ |
| **Full physical count** | Annually, at minimum | Entire location | ✔ |
| **Spot count** | Ad hoc, on suspicion or exception | Named items | ✔ |
| **Handover count** | On a location manager change | Entire location | ✔ |
| **Post-incident count** | After a discrepancy, seal break or loss | Affected items | ✔ |
| **Van stock count** | Per technician, per cycle | Van inventory | ✔ |

| # | Rule |
|---|---|
| **CT-01** | **Every count is blind.** The count sheet does **not** print the system quantity. A counter who can see the expected number will find it |
| **CT-02** | The count sheet prints item, location, bin, description and unit — everything needed to count, nothing that reveals the answer |
| **CT-03** | Recounts of a variance are performed by a **different person** |
| **CT-04** | Counts are performed by someone who does not have write access to the affected stock records (`BRU-SEC-07`) |

> **CT-01 is the rule that makes this document worth printing.** A non-blind count is not a
> count; it is a confirmation exercise with a predetermined outcome.

---

## 2. Statutory Requirements

No prescribed form. Four obligations:

| Obligation | Source | Effect |
|---|---|---|
| Accurate stock records for VAT purposes | VAT & SD Act 2012 — **pending G6** | Stock records feed the input-VAT position and are inspectable |
| Balance-sheet accuracy | Accounting standards; `M19` | Inventory valuation is an audited figure |
| Adjustment authorisation | `BRU-INV-06` | An adjustment above threshold requires approval and a reason code |
| Segregation of duties | `BRU-SEC-07` | Counter, approver and stock-record owner are different people |

### 2.1 G6 questions

| # | Question |
|---|---|
| **PC1** | Are there record-keeping obligations for physical stock counts under the VAT regime, and what must be retained? |
| **PC2** | How must a stock write-off or shrinkage adjustment be treated for input-VAT purposes — is a reversal required? |
| **PC3** | Is there a threshold above which a write-off must be notified or supported by external evidence? |

> **PC2 matters more than it looks.** If input VAT must be reversed on written-off stock, every
> adjustment has a tax consequence and must flow into `DT-012` and `DT-014`.

---

## 3. Layout

**A4 landscape** for both parts.

| Part | Zone | Content |
|---|---|---|
| **Count sheet** | Header | Count number, type, location, date, counter, **no system quantities** |
| | Body | Item, bin, description, unit, **blank count column**, condition, batch/serial |
| | Signature | Counter, supervisor |
| **Adjustment sheet** | Header | Adjustment number, count reference, date |
| | Body | Item, system quantity, counted quantity, **variance**, value, reason code |
| | Totals | Variance by direction, count and value; net adjustment value |
| | Statutory block | Not used. The **authorisation block** occupies this zone |
| | Signature | Preparer, approver(s) per threshold |

| # | Rule |
|---|---|
| **L-29-a** | The count sheet's quantity column is **blank on print**. Pre-printing a quantity defeats `CT-01` |
| **L-29-b** | The adjustment sheet shows system, counted and variance side by side, with the variance value at cost |
| **L-29-c** | Positive and negative variances are subtotalled **separately**. A net figure near zero can hide two large offsetting errors |
| **L-29-d** | Every variance line carries a reason code. A line with "variance" as its reason is not a reason |
| **L-29-e** | The authorisation block prints the threshold that applied and every approver it required |
| **L-29-f** | Column headers repeat on every page; totals never appear alone on a continuation page |

---

## 4. Field Mapping

### 4.1 Count sheet

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Count no. | `MD-040` sequence | Monospace | ✔ |
| Count type | `count.type` | Enum per §1.1 | ✔ |
| Location | `MD-004` / `MD-003` | Text | ✔ |
| Count date and time | `count.started_at`, `.ended_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Counter | `employee.display_name` + ID | Text | ✔ |
| Supervisor | `employee.display_name` + ID | Text | ✔ |
| Item code | `MD-022.part_code` | Monospace | ✔ |
| Description | `MD-022.part_name` | Text | ✔ |
| Bin / location | `MD-004.bin_code` | Monospace | ✔ |
| Unit | `MD-023.uom_code` | Label | ✔ |
| **Counted quantity** | Entered | Number | ✔ **blank on print (`L-29-a`)** |
| Serial / batch found | Entered | Monospace | **✔ serialised items** |
| Condition | Entered | Enum: good / damaged / expired / quarantined | ✔ |
| Not found | Entered | Bool | ✔ |
| Found not on sheet | Entered | Item + qty | ✔ where applicable |
| Recount required | Computed | Bool | ✔ |
| Recount by | `employee.display_name` + ID | Text | **✔ different person (`CT-03`)** |

### 4.2 Adjustment sheet

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Adjustment no. | `MD-040` sequence | Monospace | ✔ |
| Count reference | `CNT-…` | Monospace | ✔ |
| Item code / description | `MD-022` | Monospace + text | ✔ |
| System quantity | `M15` at count cut-off | Number | ✔ |
| Counted quantity | `count.line.qty` | Number | ✔ |
| **Variance quantity** | Computed | Number, signed | ✔ |
| Variance % | Computed | %, 1 dp | ✔ |
| Unit cost | `M15` valuation | BDT, 2 dp | ✔ |
| **Variance value** | Computed | BDT, 2 dp, signed | ✔ |
| **Reason code** | `MD-026.reason_code` | Code + label | ✔ |
| Reason detail | Free text | Text | ✔ where the code is insufficient |
| Investigation reference | `M23` / incident ref | Monospace | **✔ above the investigation threshold** |
| VAT consequence | Per **G6 PC2** | Text | ✔ where applicable |
| Prepared by | `employee.display_name` + ID | Text | ✔ |
| **Approved by** | `employee.display_name` + role + timestamp | Text | ✔ **`BRU-INV-06`** |
| Threshold applied | `M63` configuration | Text | ✔ |
| Posted at | `M19` posting timestamp | `DD/MM/YYYY HH:mm` | ✔ |
| GL accounts affected | `MD-035` | Monospace | ✔ |

| # | Rule |
|---|---|
| **FM-29-a** | The system quantity is taken at the **count cut-off**, and movements are frozen or recorded during the count. A count against a moving figure produces variances that are not variances |
| **FM-29-b** | Reason codes distinguish **cause categories**: miscount, mis-picking, receipt error, transfer error, damage, expiry, theft/loss, system error, unit-of-measure error |
| **FM-29-c** | A variance above the investigation threshold cannot be posted until an investigation reference exists. **Posting first and investigating later means never investigating** |
| **FM-29-d** | The preparer and the approver are different people, and neither may be the counter for the same line (`BRU-SEC-07`) |
| **FM-29-e** | Serialised items reconcile **by serial**, not by count. Three of five serials matching is not a quantity variance of two; it is a specific-unit loss |
| **FM-29-f** | Where **G6 PC2** requires an input-VAT reversal, the adjustment carries the tax consequence and flows to `DT-012` |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-INV-06` | Adjustments above threshold require approval with a reason code |
| `BRU-INV-07` | Quarantined stock is counted separately and never merged into available |
| `BRU-INV-08` | Serial-level reconciliation |
| `BRU-INV-05` | Expired stock found in a count is quarantined, not adjusted away quietly |
| `BRU-INV-04` | Consignment stock is counted and reported **separately** from own stock |
| `BRU-SEC-07` | Segregation across counter, preparer and approver |
| `BRU-FIN-05` / `BRU-FIN-06` | Adjustments post to an open period; a closed period requires the reopening process |
| `BRU-DMS-03` | Neither sheet is edited after approval; a correction is a new adjustment referencing it |

### 5.1 Shrinkage as a signal

| # | Rule |
|---|---|
| **SH-01** | Shrinkage is reported **by location, by item class and by reason code**, not as one number |
| **SH-02** | A location whose shrinkage is concentrated in high-value items is a different problem from one with broad small variances, and the report distinguishes them |
| **SH-03** | Repeat variances on the same item at the same location trigger a spot count and an investigation, automatically |
| **SH-04** | Positive variances are investigated with the same seriousness as negative ones. Stock appearing from nowhere means a receipt, transfer or issue was recorded wrongly |
| **SH-05** | Count accuracy — variances found per count — is a **location performance metric**, reported alongside shrinkage value |
| **SH-06** | Adjustment reason distribution by approver is reviewed monthly. A single approver signing off most write-offs is a pattern worth looking at |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Cycle count** | Routine, ABC-driven | Subset sheet, high frequency |
| **Full physical count** | Annual | Whole location; movements frozen; external audit may observe |
| **Spot count** | Exception or suspicion | Named items; short turnaround; investigation-linked |
| **Van stock count** | Per technician | Counted at the vehicle; `BRU-FSM-08` maximum verified at the same time |
| **Handover count** | Manager change | Both outgoing and incoming manager sign |
| **Consignment count** | Brand consignment stock | Counted and reported separately; the brand is notified of variances per the agreement |
| **Quarantine count** | Quarantined stock | Counted separately; disposition decisions recorded (`BRU-INV-07`) |
| **Post-incident count** | After a seal break or loss | Linked to the incident; forms part of the investigation record |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-029-S1` | Cycle count, 60 lines, blind sheet | `CT-01` and `L-29-a` |
| `DT-029-S2` | Variance found, recounted by another person | `CT-03` |
| `DT-029-S3` | Adjustment above threshold with investigation | `FM-29-c` |
| `DT-029-S4` | Serialised items, two serials missing | `FM-29-e` specific-unit loss |
| `DT-029-S5` | Offsetting positive and negative variances | `L-29-c` separate subtotalling |
| `DT-029-S6` | Van stock count | `BRU-FSM-08` verification |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Inventory with Finance | 2026-08-15 | Draft issue |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — Tax | *pending* | | |
| Reviewer — Warehouse Operations | *pending* | | |
| **G6 — external tax adviser (PC1–PC3)** | *pending* | | **Required** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequences | `CNT-…` count and `ADJ-…` adjustment, separate |
| Gap policy | `gaps_recorded`; an abandoned count retains its number with a reason |
| Archive format | **PDF/A-3** for the adjustment sheet — it supports a balance-sheet figure |
| Retention | `LG-009`; **not less than the tax retention period**, and available to external audit for the financial year it affects |
| Pairing | **The count sheet is archived with its adjustment sheet.** An adjustment with no count behind it is unsupported |
| Re-render | Prohibited after approval |
| Reprint | Watermarked **COPY**, logged |
| External audit | Full-count records for the financial year are producible as a set, with the reconciliation to `M19` |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | A common source of variance |
| [`DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Another common source; in-transit stock is reconciled here |
| [`../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md`](../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md) | Where an input-VAT reversal would appear (G6 PC2) |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Scanning during counts |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Bins and locations |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-035_Chart_of_Accounts_Bangladesh.md) | Adjustment posting accounts |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | How a count is planned and executed |
| `RP-016` Data Quality Scorecard Definition | Shrinkage and count-accuracy reporting |
| `OP-014` Manual Fallback Procedure Set | Cycle-count scheduling |
| `TR-012` Course Pack — Inventory and Store Keeper | Counting discipline |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six count types all blind, four count-integrity rules, separate positive/negative subtotalling, nine reason cause-categories, investigation-before-posting rule, six shrinkage-signal rules | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Blind-count rule stated and enforced in the print design (`CT-01`, `L-29-a`)
- [x] Segregation of duties across counter, preparer and approver
- [x] Investigation required before posting above threshold (`FM-29-c`)
- [x] Serialised reconciliation treated as specific-unit, not quantity
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **G6 PC2 — input-VAT treatment of write-offs** — **outstanding; determines whether adjustments flow to `DT-012`**
- [ ] Adjustment and investigation thresholds configured in `M63` and approved by the CFO — **outstanding**
- [ ] Reason-code cause categories added to `MD-026` — **outstanding, dependency**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
