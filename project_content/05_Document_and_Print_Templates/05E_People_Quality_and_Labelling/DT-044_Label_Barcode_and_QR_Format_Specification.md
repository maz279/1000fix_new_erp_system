---
id: DT-044
title: Label, Barcode and QR Format Specification
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Enterprise Architecture with Inventory
author: Enterprise Architecture with Inventory, Platform Engineering and Content Design
reviewers: [Platform Engineering, Inventory, Logistics, Quality, Brand, Localisation Lead]
approver: Chief Technology Officer
content_class: D
purpose: >
  Device tag, part label, bin label, consignment label and asset tag — symbology, data payload,
  size and durability. Every scan-based workflow across P02, P09, P11 and the warehouse depends
  on one label data contract; two teams inventing two payload formats produces scanners that read
  the label and cannot resolve the record.
traces_to: [M15, M17, M41, M03, P02, P09, P11, DT-001, DT-002, DT-024, DT-026, DT-027, DT-028, DT-029, VB-004, MD-004, MD-021, MD-022, MD-040, BRU-INV-08, BRU-LOG-01]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-044_Label_Barcode_and_QR_Format_Specification_BN.md
sources:
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-004 §3 and §9 — label 50 × 25 mm format, thermal constraints, QR minimum 20 mm with quiet zone
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-08 — serialised parts must have their serial captured at both receipt and issue
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-01 — no custody transfer without a scan and an identity capture from both parties
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-044 — Label, Barcode and QR Format Specification

> **This is a data contract, not a design.** Every scanner, app, printer and integration in the
> estate depends on the payload format defined here. Changing it after go-live means reprinting
> every label in 51+ branches and warehouses.
>
> **One rule governs the whole file: the payload identifies, it does not describe.** A payload
> that carries a customer name, a price or a status is a payload that becomes wrong the moment
> the record changes — and a label nobody can trust is a label nobody scans.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Specification — machine-readable labelling |
| Owning module | `M15` and `M17`, implemented by Platform Engineering |
| Statutory | No |
| Recipient(s) | Platform Engineering, label print vendors, suppliers (labelling requirements in `DT-023`), warehouse and field operations |
| Languages | **Bilingual** — human-readable label text is bilingual; **payloads are never translated** |
| Output formats | Thermal label stock, 50 × 25 mm and larger · direct thermal and thermal transfer · printed on documents |
| Numbering mask | Labels carry identifiers from `MD-040` and the entity registers; the label itself is not numbered |
| Retention period | n/a — a specification. Durability requirements are in §5.2 |

### 1.1 The label set

| Label | Applied to | Symbology | Size | Durability |
|---|---|---|---|---|
| **Device tag** | A customer device at intake | QR | 50 × 25 mm | Removable, survives the repair cycle |
| **Part label** | An individual spare part or its packaging | 1D + QR | 50 × 25 mm | Survives storage |
| **Bin label** | A storage location | 1D + human-readable | 100 × 50 mm | Permanent, abrasion-resistant |
| **Consignment label** | A package in transit | QR + human-readable address | 100 × 75 mm | Weather-resistant |
| **Asset tag** | Company assets, test equipment | QR | 30 × 15 mm | **Tamper-evident, permanent** |
| **Document QR** | Printed on `DT` documents | QR | ≥ 20 mm | As the document |
| **Employee ID** | Staff identification | QR | Card | Card lifetime |

---

## 2. Statutory Requirements

None. Two adjacent obligations:

| Obligation | Source | Effect |
|---|---|---|
| Personal data on labels | `LG-008`, `05-06` NFR-086 | **No personal data in a payload or in human-readable text.** A label is visible to anyone near it |
| Supplier labelling | `DT-023` FM-23-c | Suppliers are required to label to this specification, and non-conformance is a scorecard item |

---

## 3. Layout

Label layout, per type. Geometry follows `VB-004` §3 label format and §9 thermal constraints.

### 3.1 Device tag — 50 × 25 mm

```
┌────────────────────────────────────┐
│ SR-2026-114882          ┌────────┐ │
│ Samsung SM-G991B        │        │ │
│ ...4821                 │   QR   │ │
│ Shewrapara · 15/08      │        │ │
│ ভাঙা স্ক্রিন / Screen      └────────┘ │
└────────────────────────────────────┘
```

| # | Rule |
|---|---|
| **L-44-a** | **Human-readable text is a fallback, not the primary path.** Every label prints the key identifier in text so a failed scan does not stop work |
| **L-44-b** | The QR occupies a fixed corner position per label type, so operators learn where to aim |
| **L-44-c** | Quiet zone of at least 4 modules around every code (`VB-004` TH-06) |
| **L-44-d** | Monochrome only. No colour, no greyscale — thermal cannot render it and scanners do not need it |
| **L-44-e** | Bengali human-readable text is tested per printer model before deployment (`VB-004` TH-08, BL-08) |
| **L-44-f** | No personal data. The customer is identified by the last four digits of their mobile number only, and only where operationally necessary |

---

## 4. Field Mapping — the payload contract

### 4.1 Payload format

All QR payloads use a single URI form so that a consumer scanner resolves them and an
internal scanner parses them.

```
https://s.1000fix.com/{type}/{id}?v=1
```

| Element | Meaning | Example |
|---|---|---|
| `{type}` | Object type code, two characters | `so` service order · `dv` device · `pt` part · `bn` bin · `cn` consignment · `as` asset · `dc` document · `ep` employee |
| `{id}` | The object's permanent identifier | `SR-2026-114882` |
| `v` | **Payload version** | `1` |

| # | Rule |
|---|---|
| **PL-01** | **The payload carries a type, an identifier and a version. Nothing else.** No names, no prices, no status, no descriptions |
| **PL-02** | The identifier is the object's **permanent** identifier, never a display reference that could change |
| **PL-03** | The version parameter is present from day one. **A payload format with no version cannot be migrated**, and this format will need to change eventually |
| **PL-04** | The URI resolves for an external scanner to a public-safe page — a customer scanning a device tag sees their job status after authentication, nothing before it |
| **PL-05** | Internal apps parse the URI locally and do not require connectivity to resolve it (`UI-009` offline) |
| **PL-06** | The domain is short, stable and owned. Changing it invalidates every printed label in the estate |
| **PL-07** | No payload exceeds 120 characters. Longer payloads need larger codes or higher density, and both fail on 203 dpi thermal |

### 4.2 Per-type payload and human-readable content

| Type | `{type}` | `{id}` source | Human-readable text |
|---|:--:|---|---|
| Service order | `so` | `service_order.order_ref` | Order reference, device make/model, last 4 of mobile, branch, date, fault (short) |
| Device | `dv` | `device.serial_no` | Serial, make/model |
| Part | `pt` | `MD-022.part_code` + serial where serialised | Part code, description (short), serial, batch, expiry |
| Bin | `bn` | `MD-004.bin_code` | Bin code in large type, zone, aisle |
| Consignment | `cn` | Consignment reference | Consignment reference, destination address, recipient, package n of m, handling icons |
| Asset | `as` | `asset.asset_tag` | Asset tag, owning entity, "Property of 1000FiX" |
| Document | `dc` | Document reference | Document reference |
| Employee | `ep` | `MD-012.employee_code` | Name, employee ID, photo, designation |

### 4.3 1D barcodes

Where a 1D barcode is used alongside a QR — parts and bins, for legacy scanner compatibility:

| Item | Specification |
|---|---|
| Symbology | **Code 128** — alphanumeric, compact, widely supported |
| Content | The identifier only, no prefix or URI |
| Minimum bar height | 10 mm |
| Minimum X-dimension | 0.25 mm at 203 dpi |
| Quiet zone | 10× X-dimension each side |
| Human-readable | Below the bars, always |

| # | Rule |
|---|---|
| **BC-01** | 1D carries the **same identifier** as the QR on the same label. Two codes on one label that resolve differently is a defect that surfaces months later |
| **BC-02** | Code 128 subset selection is automatic; the identifier format avoids characters that force inefficient encoding |
| **BC-03** | Where only one code fits, it is the **QR** — it survives partial damage and carries the type and version |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this specification |
|---|---|
| `BRU-INV-08` | Serialised parts scan at receipt and at issue — the part label must carry the serial |
| `BRU-LOG-01` | Custody transfer requires a scan — device and consignment labels are the scan targets |
| `BRU-INV-05` | Expiry is enforced at issue — the part label carries the expiry in human-readable text |
| `BRU-INV-07` | Quarantined stock is physically distinguishable — a quarantine overlabel is specified in §6 |
| `BRU-FSM-08` | Van stock is scanned — part labels must survive vehicle conditions |
| `BRU-SEC-05` | No personal data on labels (`L-44-f`) |

### 5.1 Print and scan quality

| # | Rule |
|---|---|
| **PQ-01** | Print quality is verified by **scan test**, not by eye. A label that looks fine and reads at 60% first-pass is a productivity tax on every scan |
| **PQ-02** | First-pass read rate is monitored per printer and per label type; below threshold triggers printer maintenance or media replacement |
| **PQ-03** | Print head cleaning and media specification are in `OP-014`, because thermal print quality degrades gradually and invisibly |
| **PQ-04** | Every new printer or media type is qualified before deployment, including a Bengali render test (`L-44-e`) |
| **PQ-05** | Labels are printed at the point of application, not in advance. Pre-printed label stock invites the wrong label on the wrong object |

### 5.2 Durability by environment

| Label | Environment | Requirement |
|---|---|---|
| Device tag | Workshop: heat, solvents, handling | Survives 30 days; adhesive removable without residue |
| Part label | Storage and van | Survives 24 months; resists abrasion |
| Bin label | Fixed, high-abrasion | Permanent; laminated or engraved for long-term locations |
| Consignment label | Outdoor, rain, handling | Weather-resistant; direct thermal unsuitable where exposed — thermal transfer required |
| Asset tag | Permanent | **Tamper-evident**; removal destroys the label |
| Employee ID | Daily handling | Card lifetime |

| # | Rule |
|---|---|
| **DU-01** | **Direct thermal fades.** It is acceptable for short-lived labels and unacceptable for parts, bins and assets |
| **DU-02** | Adhesive is specified per surface. A label that falls off a part in a bin creates an unidentifiable part and a stock discrepancy (`DT-029`) |
| **DU-03** | A device tag must not damage the device or leave residue. A customer whose device comes back with adhesive marks has a legitimate complaint |
| **DU-04** | Asset tags are tamper-evident so that removal is visible during counts |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Device tag — standard** | Branch intake | 50 × 25 mm, QR, removable adhesive |
| **Device tag — small device** | Wearables, accessories | 30 × 15 mm; QR only, minimal text |
| **Device tag — tie-on** | Devices that cannot be adhesive-labelled | Tag with the same payload |
| **Part label — bulk** | Non-serialised parts | No serial field |
| **Part label — serialised** | Serialised parts | Serial in both payload and text (`BRU-INV-08`) |
| **Quarantine overlabel** | Failed inspection (`BRU-INV-07`) | High-contrast overlabel applied over the part label; does not obscure the code |
| **Bin label — long-term** | Fixed racking | Laminated or engraved |
| **Consignment — restricted goods** | Lithium batteries, refrigerant | Handling markings per the applicable transport rules (`DT-027` G6 DC6) |
| **Asset tag — test equipment** | `MD-046` calibrated instruments | Adds calibration due date in human-readable text |
| **Supplier-applied label** | Supplier labels to our spec (`DT-023`) | Same payload contract; conformance is a scorecard item |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-044-S1` | Device tag, 50 × 25 mm, bilingual | Layout, payload, quiet zone |
| `DT-044-S2` | Serialised part label with 1D + QR | `BC-01` identifier parity |
| `DT-044-S3` | Bin label, 100 × 50 mm | Large human-readable code |
| `DT-044-S4` | Consignment label with restricted-goods markings | Handling markings |
| `DT-044-S5` | Asset tag, tamper-evident | `DU-04` |
| `DT-044-S6` | Scan-test report across three printer models | `PQ-01`, `PQ-04` |

Held in `RF-009`. Physical specimens are held by Platform Engineering with the printer test set
(`VB-004` §14).

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Enterprise Architecture with Inventory | 2026-08-15 | Draft issue |
| Reviewer — Platform Engineering | *pending* | | |
| Reviewer — Logistics | *pending* | | |
| Reviewer — Quality | *pending* | | |
| Reviewer — Brand (`VB-004` conformance) | *pending* | | |
| Approver — Chief Technology Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | None. Labels carry identifiers issued by `MD-040` and the entity registers |
| Payload versioning | `v=1` from first issue. **A version increment requires a migration plan covering labels already in the field** (`PL-03`) |
| Domain | Short, stable, owned. Its permanence is a Platform Engineering commitment, not an assumption (`PL-06`) |
| Specification retention | Every payload version retained while any label of that version may still be in circulation |
| Physical specimens | Held with the printer test set; regenerated on any change |
| Change control | A change to the payload contract is a **breaking change** for every scanner, app and integration, and follows `BRU-ADM-02` with a coordinated release |

> **§9 is the section that matters most in five years.** The payload contract will need to change.
> Whether that is a planned migration or an estate-wide reprint depends entirely on the version
> parameter being there from the first label.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard; §3 L-05 cites this file for machine-readable zones |
| [`../../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md`](../../01_Voice_Brand_and_Design_Content/VB-004_Print_and_PDF_Brand_Template_Standard.md) | Label format, thermal constraints, QR minimum size |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Device tag applied at intake |
| [`../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](../05C_Supply_Chain_and_Logistics/DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Labels applied on acceptance |
| [`../05C_Supply_Chain_and_Logistics/DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](../05C_Supply_Chain_and_Logistics/DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Scanning at custody transfer |
| [`../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md`](../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md) | Consignment labels |
| [`../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md`](../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md) | Scan at handover (`BRU-LOG-01`) |
| [`../05C_Supply_Chain_and_Logistics/DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md`](../05C_Supply_Chain_and_Logistics/DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md) | Scanning during counts |
| [`../05C_Supply_Chain_and_Logistics/DT-023_Purchase_Order.md`](../05C_Supply_Chain_and_Logistics/DT-023_Purchase_Order.md) | Supplier labelling requirement |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Bin codes |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) | Part codes and serialisation flags |
| `MM-001` Multimedia Asset Standard and Delivery Specification | The design deliverable implementing this contract |
| `AP-002` API Reference Content Standard | How apps parse the payload |
| `OP-014` Manual Fallback Procedure Set | Print quality and media (`PQ-03`) |
| `UI-009` Offline Sync and Conflict Resolution Copy | Offline scanning behaviour |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven-label set, versioned URI payload contract carrying type/id/version only, Code 128 parity rule, five print-quality rules, durability by environment, and the §9 migration warning | Chief Technology Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Payload contract defined as type + identifier + version, with descriptive data excluded (`PL-01`)
- [x] Version parameter mandated from first issue, with the migration reason stated (`PL-03`)
- [x] 1D and QR identifier parity required (`BC-01`)
- [x] Durability specified per environment, not generically
- [x] No personal data on labels (`L-44-f`)
- [x] All internal links resolve
- [ ] Domain registered and its permanence committed by Platform Engineering (`PL-06`) — **outstanding**
- [ ] Scan-test qualification completed for every deployed printer and media combination (`PQ-04`) — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Adhesive and media specifications confirmed per environment with a supplier (`DU-02`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
