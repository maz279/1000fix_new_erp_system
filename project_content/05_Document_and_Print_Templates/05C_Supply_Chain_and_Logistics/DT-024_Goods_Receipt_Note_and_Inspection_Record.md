---
id: DT-024
title: Goods Receipt Note and Inspection Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Inventory with Quality, Finance and Content Design
reviewers: [Quality, Finance, Procurement, Tax, Internal Audit, Warehouse Operations]
approver: Chief Operating Officer with Chief Financial Officer
content_class: A
purpose: >
  Records received quantity, condition, inspection outcome and acceptance or rejection with a
  reason. Three-way matching and vendor performance scoring both depend on a consistent GRN, and
  input-VAT credit depends on it being matched to a conforming supplier challan. It is the moment
  goods become ours and the last moment we can decline them.
traces_to: [M41, M42, M15, M52, M51, M23, DT-001, DT-012, DT-023, DT-025, DT-044, MD-016, MD-022, MD-023, MD-026, MD-040, BRU-SCM-01, BRU-INV-07, BRU-INV-08]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — procurement documents remain English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SCM-01 — a vendor invoice cannot be approved for payment without a matched purchase order and goods receipt within tolerance
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-07 — goods failing inspection go to quarantine and never to available stock
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-08 — serialised parts must have their serial captured at both receipt and issue
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-024 — Goods Receipt Note and Inspection Record

> ⚠ **Class A — statutory consequence.** The GRN is the evidence that a supply was received. It
> supports the input-VAT claim in `DT-012`, it is the second leg of the `BRU-SCM-01` three-way
> match, and it is the record that decides whether defective goods are the supplier's problem or
> ours.
>
> **A GRN signed without inspection is a GRN that transfers the supplier's risk onto us.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Goods receipt and inspection record |
| Owning module | `M41` Warehouse Management, with `M15` and `M23` |
| Statutory | No prescribed form. **Class A** — input-VAT evidence and three-way-match leg |
| Recipient(s) | Warehouse, procurement, accounts payable, quality, supplier (rejection copy), internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | A4 portrait · handheld scanner capture (primary data path) · PDF |
| Numbering mask | `MD-040` — `GRN-{entity}-{location}-{yy}-{seq:06d}`, location-aware |
| Retention period | `LG-009`; **not less than the tax retention on the purchase it evidences** |

### 1.1 The three-way match

```
DT-023 Purchase Order   — what we ordered, at what price, within what tolerance
DT-024 Goods Receipt    — what actually arrived, in what condition        ← this document
Supplier challan (6.3)  — what we are being asked to pay for
                          ↓
              BRU-SCM-01: all three agree within tolerance, or no payment
```

| # | Rule |
|---|---|
| **TW-01** | The GRN records **what arrived**, never what was ordered. Pre-populating received quantity from the PO defeats the entire control |
| **TW-02** | Quantity, condition and specification are each checked. A match on quantity alone is not an inspection |
| **TW-03** | Tolerance is the PO's (`DT-023` FM-23-b). Out-of-tolerance receipts route to procurement before acceptance |
| **TW-04** | The supplier challan is attached at receipt and checked against `DT-012` defect codes **at this moment**, while the delivery person is still present |

---

## 2. Statutory Requirements

No prescribed form. Four obligations:

| Obligation | Source | Effect |
|---|---|---|
| Evidence of receipt supporting the input-VAT claim | VAT & SD Act 2012; `DT-012` — **pending G6 P2** | Without a GRN, the input claim may not be supportable |
| Supplier challan captured and checked | `DT-012` §5.1 | A defective challan detected later is usually uncorrectable |
| Serial capture on serialised items | `BRU-INV-08` | Traceability for warranty, recall and theft |
| Quarantine of failed goods | `BRU-INV-07` | Failed goods must not reach available stock |

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | GRN number, receipt date/time, location, receiver |
| Party block | Supplier and delivery reference left; PO reference and challan reference right |
| Body | Line receipt table → inspection results → serial capture → disposition |
| Totals | Received / accepted / rejected / quarantined quantities and values |
| Statutory block | Not used. The **acceptance declaration** occupies this zone |
| Signature | Receiver, inspector, and the delivering party where a rejection is recorded |
| Footer | GRN reference, `page n of m`, PO reference |

| # | Rule |
|---|---|
| **L-24-a** | Ordered, received, accepted, rejected and quarantined quantities all print **per line**. A single "received" figure hides the entire decision |
| **L-24-b** | Rejection reasons print from `MD-026` with free text where needed. A rejection with no reason cannot support a `DT-025` return |
| **L-24-c** | The serial-capture block prints for serialised lines only, sized to the received quantity |
| **L-24-d** | The supplier challan number, date and defect status print in the header block, not buried |
| **L-24-e** | The rejection copy given to the delivering party is a complete document, not a note |

---

## 4. Field Mapping

### 4.1 Header and delivery

| Label | Source field | Format | Required |
|---|---|---|:--:|
| GRN no. | `MD-040` sequence | Monospace | ✔ |
| Receipt date and time | `grn.received_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Receiving location | `MD-004` warehouse / `MD-003` branch | Text | ✔ |
| Received by | `employee.display_name` + ID | Text | ✔ |
| Supplier name and code | `MD-016` | Text + monospace | ✔ |
| PO number and revision | `DT-023` reference | Monospace | ✔ |
| **Supplier challan no. / date** | `grn.supplier_challan_no`, `.date` | Monospace, date | ✔ |
| Challan defect status | `DT-012` §5.1 code | Code | ✔ (prints "None") |
| Delivery note / consignment ref | `grn.delivery_ref` | Monospace | Where provided |
| Vehicle / courier | `grn.carrier_ref` | Text | Where relevant |
| Seal number and condition | `grn.seal_no`, `.seal_intact` | Monospace, bool | **✔ for sealed consignments (`BRU-LOG-04`)** |

### 4.2 Line receipt and inspection

| Label | Source field | Format | Required |
|---|---|---|:--:|
| PO line no. | `DT-023` line | Integer | ✔ |
| Item code / description | `MD-022` | Monospace + text | ✔ |
| Quantity ordered | `DT-023` line qty | Number | ✔ |
| **Quantity received** | `grn.line.qty_received` | Number | ✔ **counted, not assumed (`TW-01`)** |
| Unit | `MD-023.uom_code` | Label | ✔ |
| Variance to order | Computed | Number + % | ✔ |
| Within tolerance | Computed against `DT-023` | Bool | ✔ |
| Inspection required | `MD-022.inspection_required` | Bool | ✔ |
| Inspection result | `grn.line.inspection_result` | Enum: pass / fail / partial | ✔ where required |
| Sampling basis | `M23` sampling plan | Text | ✔ where sampled |
| **Quantity accepted** | `grn.line.qty_accepted` | Number | ✔ |
| **Quantity rejected** | `grn.line.qty_rejected` | Number | ✔ |
| **Quantity quarantined** | `grn.line.qty_quarantined` | Number | ✔ **`BRU-INV-07`** |
| Rejection reason | `MD-026.reason_code` + note | Code + text | ✔ where rejected |
| Serial numbers | `grn.line.serials[]` | Monospace list | **✔ serialised items (`BRU-INV-08`)** |
| Batch / lot | `grn.line.batch_no` | Monospace | Where applicable |
| Expiry / shelf life | `grn.line.expiry_date` | `DD/MM/YYYY` | **✔ where shelf-life applies (`BRU-INV-05`)** |
| Storage location assigned | `MD-004.bin_code` | Monospace | ✔ for accepted |
| Label applied | `DT-044` | Bool | ✔ for accepted |

### 4.3 Disposition and declaration

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Total received / accepted / rejected / quarantined | Computed | Number, value | ✔ |
| Accepted value | Computed at PO price | BDT, 2 dp | ✔ |
| Rejection route | `DT-025` reference | Monospace | ✔ where rejected |
| Quarantine reference | `M23` case | Monospace | ✔ where quarantined |
| Inspector | `employee.display_name` + ID | Text | ✔ where inspected |
| Receiver declaration | Static | Text | ✔ |
| Delivering party acknowledgement | Name + signature | Text | ✔ where goods are rejected on the spot |

| # | Rule |
|---|---|
| **FM-24-a** | `qty_received` is **entered from a count**, not defaulted from the PO. Systems that pre-fill it produce GRNs that are signed without counting |
| **FM-24-b** | `accepted + rejected + quarantined = received`, always. A residual is a defect that blocks posting |
| **FM-24-c** | Serialised lines cannot post without a serial per unit (`BRU-INV-08`) |
| **FM-24-d** | Quarantined stock is not available stock and never appears in availability (`BRU-INV-07`) |
| **FM-24-e** | Shelf-life items require an expiry date at receipt; without it `BRU-INV-05` cannot be enforced later |
| **FM-24-f** | Where the seal is broken or weight differs, `BRU-LOG-04` raises an incident and blocks onward movement pending review |
| **FM-24-g** | The supplier challan is scanned or photographed at receipt and attached. Chasing it afterwards is how input claims are lost |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SCM-01` | The GRN is a match leg; tolerance is the PO's |
| `BRU-SCM-03` | The receiver cannot be the person who raised the requisition or approves the invoice |
| `BRU-SCM-04` | Import receipts require landed-cost allocation before final valuation |
| `BRU-INV-05` | Expiry captured at receipt so expired stock can be blocked at issue |
| `BRU-INV-07` | Failed goods to quarantine, never to available stock |
| `BRU-INV-08` | Serial capture at receipt |
| `BRU-INV-04` | Consignment stock is received but excluded from own-stock valuation and reported separately |
| `BRU-LOG-04` | Seal break or weight discrepancy raises an incident and blocks onward movement |

### 5.1 Vendor performance data captured here

Every GRN is a data point in the vendor scorecard (`M42`). Recording it well is the only way the
scorecard means anything.

| Metric | Field |
|---|---|
| On-time delivery | Receipt date against PO required-by |
| Quantity accuracy | Received against ordered, and the direction of variance |
| Quality acceptance rate | Accepted against received |
| Documentation quality | Challan defect code (`DT-012` §5.1) |
| Packaging and labelling compliance | `DT-044` conformance flag |
| Serial and batch data quality | Completeness at receipt |

| # | Rule |
|---|---|
| **VP-01** | Scorecard metrics derive from GRN data, not from opinion |
| **VP-02** | A rejection recorded without a reason code contributes nothing to the scorecard and is therefore not permitted |
| **VP-03** | Documentation defects count. A supplier whose goods are perfect and whose challans are not is still costing us money (`DT-012` DF-02) |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard GRN** | Warehouse receipt against a PO | The base document |
| **Branch receipt** | Direct delivery to a branch | Simplified inspection; central quality notified for sampled categories |
| **Import receipt** | Foreign supply (`M44`) | Bill of entry, customs documentation, landed-cost basis; provisional valuation until allocation |
| **Consignment receipt** | Brand consignment stock | Zero-value receipt; title remains with the brand (`BRU-INV-04`) |
| **Return receipt** | Goods returned by a customer or from a branch | References the outbound document, not a PO |
| **Service receipt** | Services PO milestone | Milestone acceptance replaces quantity; signed by the service owner |
| **Partial receipt** | Split delivery | References the PO line's remaining balance; the PO stays open |
| **Rejection-only** | Entire delivery refused | Complete document issued to the delivering party (`L-24-e`); goods do not enter stock at all |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-024-S1` | 12 lines, all accepted | Base rendition and label/bin assignment |
| `DT-024-S2` | Short delivery within tolerance | Variance and tolerance handling |
| `DT-024-S3` | Failed inspection, quarantined | `BRU-INV-07` disposition and `FM-24-b` arithmetic |
| `DT-024-S4` | Serialised parts, 40 serials | `BRU-INV-08` capture block |
| `DT-024-S5` | Supplier challan missing our BIN | `DT-012` D-1 flagged at receipt |
| `DT-024-S6` | Broken seal | `BRU-LOG-04` incident and movement block |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Inventory with Quality and Finance | 2026-08-15 | Draft issue |
| Reviewer — Quality | *pending* | | |
| Reviewer — Procurement | *pending* | | |
| Reviewer — Tax | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Approver — COO with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `GRN-{entity}-{location}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded` |
| Archive format | PDF/A-3 — it supports an input-VAT claim |
| Retention | `LG-009`; **not less than the tax retention on the purchase** |
| Supplier challan | Scanned image attached and retained with the GRN for the same period (`FM-24-g`) |
| Re-render | Prohibited after posting. Stock has moved on the strength of it |
| Reprint | Watermarked **COPY**, logged |
| Correction | A posting error is corrected by a **reversal GRN** referencing the original, never by editing (`BRU-DMS-03`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-023_Purchase_Order.md`](DT-023_Purchase_Order.md) | Match leg one; supplies tolerances |
| [`DT-025_Return_to_Vendor_and_Debit_Advice.md`](DT-025_Return_to_Vendor_and_Debit_Advice.md) | Where rejected goods go |
| [`DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Onward movement of accepted stock |
| [`DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md`](DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md) | Where receipt errors eventually surface |
| [`../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md`](../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md) | The register this evidences; defect codes checked here |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Labelling applied on acceptance |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Inspection requirement and serialisation flags |
| [`SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-018_SOP_Warehouse_Receipt_PutAway_and_Count.md) | How a receipt is performed |
| `RP-002` Report Catalogue by Role and Module | Scorecard derivation |
| `TR-012` Course Pack — Inventory and Store Keeper | Where counting discipline is taught |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Three-way-match position with four rules, count-not-default rule, disposition arithmetic rule, challan-check-at-receipt, six vendor-scorecard metrics, eight variants | COO with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Count-not-default rule stated as the core control (`TW-01`, `FM-24-a`)
- [x] Disposition arithmetic enforced (`FM-24-b`)
- [x] Supplier challan checked at receipt against `DT-012` defect codes
- [x] Vendor scorecard metrics derived from this document's fields
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] Inspection sampling plans defined per item category with Quality (`M23`) — **outstanding**
- [ ] Serialisation and inspection flags populated in `MD-022` — **outstanding, dependency**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
