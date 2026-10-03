---
id: DT-026
title: Stock Transfer Note and Gate Pass
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Inventory
author: Inventory with Security, Tax and Content Design
reviewers: [External tax adviser, Tax, Security, Logistics, Warehouse Operations, Internal Audit, Localisation Lead]
approver: Chief Operating Officer with Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Inter-branch and warehouse transfer with custody signatures and a security gate pass. Stock
  moving between 51+ locations without documented custody is stock that disappears. Where goods
  move between our own premises without a sale, a transfer challan is also a VAT-record obligation,
  which is why this document is statutory and not merely operational.
traces_to: [M15, M41, M03, M51, DT-001, DT-024, DT-027, DT-028, DT-029, DT-044, MD-003, MD-004, MD-026, MD-040, BRU-INV-02, BRU-INV-08, BRU-LOG-01, BRU-LOG-04]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-026_Stock_Transfer_Note_and_Gate_Pass_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.5 transfer challan — issued where goods move between premises of the same registered person without a sale. **Applicability and form must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-02 — inter-branch transfer requires the source branch manager's approval and the destination's confirmed receipt
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-01 — no custody transfer without a scan and an identity capture from both parties
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-026 — Stock Transfer Note and Gate Pass

> ⚠ **Tier S — a transfer challan is probably a prescribed form (Mushak 6.5). Gate G6 mandatory
> and unwaivable (`WV-02`).**
>
> **Two documents, one movement.** The transfer note is the inventory and tax record; the gate
> pass is the security instrument that lets goods leave a site. They are issued together because
> separating them is how goods leave a site without an inventory record — or, equally, how an
> inventory transfer is posted for goods that never moved.
>
> **`BRU-INV-02`: source branch manager approval and destination confirmed receipt. Both, or the
> transfer is not complete.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Inter-location stock transfer + security gate pass |
| Owning module | `M15` Spare Parts and Inventory, with `M41` Warehouse Management |
| Statutory | **Yes — Tier S**, subject to G6 confirmation of Mushak 6.5 applicability |
| Recipient(s) | Destination location, security gate, carrier, inventory control, tax records |
| Languages | **Bilingual — stacked labels.** Gate security and warehouse staff work in Bengali |
| Output formats | **A5 portrait (primary, gate pass)** · A4 portrait (transfer note with many lines) · PDF |
| Numbering mask | `MD-040` — `STN-{entity}-{location}-{yy}-{seq:06d}`; gate pass shares the number |
| Retention period | **At least 5 years** where a transfer challan obligation applies — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 What moves under this document

| Movement | Covered |
|---|:--:|
| Branch → branch stock transfer | ✔ |
| Warehouse → branch replenishment | ✔ |
| Branch → warehouse return | ✔ |
| Van stock issue to a technician (`BRU-FSM-08`) | ✔ |
| Devices under repair moving between sites | **`DT-027`** — customer property, not stock |
| Goods to a supplier | **`DT-025` + `DT-027`** |
| Goods to a customer | **`DT-027` + `DT-028`** |
| Assets and test equipment moving sites | ✔ — asset variant, `MD-046` |
| Scrap and e-waste leaving site | ✔ — with `DT-035` |
| Personal items and non-stock leaving site | ✔ — **gate pass only**, no inventory movement |

> **The gate pass covers everything that leaves; the transfer note covers everything that is
> stock.** They overlap for most movements and diverge at the edges — which is why they are one
> document with two parts rather than two documents.

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Transfer challan where goods move between own premises | VAT & SD Rules 2016, Mushak 6.5 — **pending G6** | pending | Whole transfer note |
| Registered person's identity and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Both premises identified | VAT & SD Rules 2016 — **pending G6** | pending | Party block |
| Description, quantity and value of goods | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| Date and time of movement | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Vehicle / carrier particulars | VAT & SD Rules 2016 — **pending G6** | pending | Transport block |
| Authorised signature | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 G6 questions

| # | Question |
|---|---|
| **TR1** | Does a Mushak 6.5 transfer challan apply to movements between our own branches, and in what circumstances? |
| **TR2** | What value must be shown on a transfer challan — cost, transfer price, or market value? |
| **TR3** | Must a transfer challan accompany the goods physically, or is an electronic record sufficient? |
| **TR4** | Are branch-to-branch movements within one BIN treated differently from movements between separately registered premises? |
| **TR5** | What is the position for van stock issued to a technician — is that a transfer between premises? |

> **TR5 is the operationally awkward one.** Van stock moves daily, in volume, to hundreds of
> technicians. If each movement requires a transfer challan, that is a material process and
> system requirement, not a minor one.

---

## 3. Layout

**Primary format: A5 portrait**, two-part on one sheet where line count permits.

| Part | Zone | Content | Bilingual |
|---|---|---|---|
| **Transfer note** | Header | STN number, date/time, source and destination | Title stacked |
| | Body | Line items with quantity, serial/batch, value | Labels stacked |
| | Signature | Source dispatcher, source approver (`BRU-INV-02`) | Labels stacked |
| **Gate pass** | Header | Same number, gate pass designation | Title stacked |
| | Body | Package count, seal number, carrier and vehicle | Labels stacked |
| | Signature | **Security officer at exit**, carrier, and receipt confirmation at destination | Labels stacked |
| Both | Footer | STN reference, `page n of m`, hotline | English |
| Both | Machine-readable | Barcode/QR: STN reference (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-26-a** | The **gate pass portion is not detachable in a way that leaves the transfer note without it**. Security keeps a scan or a stub, not the only copy |
| **L-26-b** | Package count and seal number print prominently — they are what security actually checks |
| **L-26-c** | The destination confirmation block prints on the document that travels, so the receiver signs the same paper the dispatcher signed |
| **L-26-d** | Where the line count exceeds the A5 body, an A4 transfer note is issued with an A5 gate pass referencing it |
| **L-26-e** | The transfer note prints **values** where a transfer challan obligation applies (G6 TR2); where it does not, values may be suppressed for security reasons at the gate |

---

## 4. Field Mapping

### 4.1 Transfer note

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| STN no. | স্থানান্তর নং | `MD-040` sequence | Monospace | ✔ |
| Date and time | তারিখ ও সময় | `transfer.dispatched_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Source location | উৎস স্থান | `MD-003` / `MD-004` + BIN | Text + monospace | ✔ |
| Destination location | গন্তব্য স্থান | `MD-003` / `MD-004` + BIN | Text + monospace | ✔ |
| Reason for transfer | স্থানান্তরের কারণ | `MD-026.reason_code` | Code + label | ✔ |
| Item code / description | কোড / বিবরণ | `MD-022` | Monospace + text | ✔ |
| Quantity / unit | পরিমাণ / একক | `transfer.line.qty`, `MD-023` | Number + UoM | ✔ |
| Serial / batch | সিরিয়াল / ব্যাচ | `transfer.line.serials[]` | Monospace | **✔ serialised (`BRU-INV-08`)** |
| Value | মূল্য | Per **G6 TR2** | BDT, 2 dp | ✔ where challan applies |
| Source bin | উৎস বিন | `MD-004.bin_code` | Monospace | ✔ |
| Destination bin | গন্তব্য বিন | `MD-004.bin_code` | Monospace | Where known |
| **Dispatched by** | প্রেরক | `employee.display_name` + ID | Text | ✔ |
| **Approved by** | অনুমোদনকারী | Branch/warehouse manager + ID | Text | ✔ **`BRU-INV-02`** |
| Expected receipt date | প্রত্যাশিত প্রাপ্তি | `transfer.expected_at` | `DD/MM/YYYY` | ✔ |

### 4.2 Gate pass and receipt

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Package count | প্যাকেজ সংখ্যা | `transfer.package_count` | Integer | ✔ |
| Package description | প্যাকেজের বিবরণ | `transfer.package_desc` | Text | ✔ |
| Seal number(s) | সিল নং | `transfer.seal_no[]` | Monospace | ✔ where sealed |
| Weight | ওজন | `transfer.weight_kg` | kg, 2 dp | Where weighed |
| Carrier / rider | বাহক | `MD-045` / `P09` rider ID | Text | ✔ |
| Vehicle registration | যানবাহন নং | `MD-045.registration` | Monospace | ✔ where a vehicle is used |
| Restricted items declared | সীমাবদ্ধ পণ্য | `transfer.restricted_flag` | Bool + type | **✔ (`BRU-LOG-05`)** |
| **Security officer** | নিরাপত্তা কর্মকর্তা | `employee.display_name` + ID | Text | ✔ at exit |
| Exit date and time | বহির্গমনের সময় | `gate.exit_at` | `DD/MM/YYYY HH:mm` | ✔ |
| **Received by** | গ্রহণকারী | `employee.display_name` + ID | Text | ✔ **`BRU-INV-02`** |
| Receipt date and time | প্রাপ্তির সময় | `transfer.received_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Seal intact on arrival | সিল অক্ষত | `transfer.seal_intact` | Bool | ✔ where sealed |
| Quantity received | প্রাপ্ত পরিমাণ | `transfer.line.qty_received` | Number | ✔ |
| Discrepancy | অসঙ্গতি | Computed + `MD-026` | Number + code | ✔ where any |

| # | Rule |
|---|---|
| **FM-26-a** | Stock is **in transit** between dispatch and receipt — a distinct state, visible in `M15`, belonging to neither location's available stock |
| **FM-26-b** | The destination counts and confirms. A receipt confirmation that copies the dispatch quantity is not a confirmation (`DT-024` TW-01, same principle) |
| **FM-26-c** | Any discrepancy raises an incident immediately, with both managers notified. **In-transit discrepancies are the most common inventory-loss pattern in a multi-site network** |
| **FM-26-d** | Seal break on arrival follows `BRU-LOG-04` — incident raised, onward movement blocked pending review |
| **FM-26-e** | An unconfirmed transfer older than the configured threshold escalates automatically. **Stock in transit indefinitely is stock that is gone** |
| **FM-26-f** | Restricted items — lithium batteries, refrigerant — are declared and may only travel with a certified carrier (`BRU-LOG-05`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-INV-02` | Source approval and destination confirmation both required |
| `BRU-INV-08` | Serial capture at dispatch and at receipt |
| `BRU-INV-05` | Expired stock cannot be transferred to be issued elsewhere |
| `BRU-LOG-01` | Custody transfer requires a scan and identity capture from both parties |
| `BRU-LOG-04` | Seal break or weight discrepancy raises an incident and blocks onward movement |
| `BRU-LOG-05` | Restricted items only with a certified carrier |
| `BRU-FSM-08` | Van stock cannot exceed the configured maximum per item per technician |
| `BRU-INV-04` | Consignment stock transfers are recorded but excluded from own-stock valuation |

### 5.1 The gate pass as a security control

| # | Rule |
|---|---|
| **GP-01** | **Nothing leaves a site without a gate pass** — stock, assets, scrap, contractor equipment or personal items |
| **GP-02** | The security officer checks package count and seal, not contents. Content verification is the dispatcher's job and is recorded on the transfer note |
| **GP-03** | The gate log is reconciled to issued transfer notes **daily**. A gate log entry with no transfer note, or the reverse, is an exception |
| **GP-04** | A gate pass is single-use and single-movement. Reuse is a control failure |
| **GP-05** | Non-stock gate passes — personal items, contractor equipment — use the same numbering and the same log, with no inventory posting |
| **GP-06** | Out-of-hours movements require an additional named authoriser |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Branch-to-branch A5** | The default | Two-part sheet |
| **Warehouse replenishment A4** | Many lines | A4 transfer note + A5 gate pass |
| **Van stock issue** | Technician van replenishment | Technician is the destination; `BRU-FSM-08` maximum enforced; **G6 TR5 governs whether a challan applies** |
| **Asset movement** | Test equipment, tooling (`MD-046`) | Asset tag and calibration status; calibration validity must survive the move |
| **Scrap / e-waste out** | Disposal (`M18`) | Accompanies `DT-035`; weight and composition recorded |
| **Gate pass only** | Non-stock leaving site | No inventory posting; same log (`GP-05`) |
| **Emergency transfer** | SLA-critical part needed at another site | Expedited approval, same documentation; never a phone call alone |
| **Consignment transfer** | Brand consignment stock | Title unchanged; brand notified per the agreement |

---

## 7. Worked Example

> **The transfer-challan element's specimen follows G6 TR1.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-026-S1` | Branch-to-branch, 6 lines, sealed | Base bilingual two-part rendition |
| `DT-026-S2` | Serialised parts | `BRU-INV-08` capture at both ends |
| `DT-026-S3` | Short receipt at destination | `FM-26-c` discrepancy incident |
| `DT-026-S4` | Seal broken on arrival | `BRU-LOG-04` handling |
| `DT-026-S5` | Van stock issue | `BRU-FSM-08` and the G6 TR5 question |
| `DT-026-S6` | Gate pass only, contractor equipment | `GP-05` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Inventory with Security | 2026-08-15 | Draft issue |
| Reviewer — Security | *pending* | | |
| Reviewer — Logistics | *pending* | | |
| Reviewer — Warehouse Operations | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser (TR1–TR5)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — COO with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `STN-{entity}-{location}-{yy}-{seq:06d}`; **gate pass shares the number** so the two can never be separated in the record |
| Gap policy | **`no_gaps` where a transfer challan obligation applies** (G6 TR1); `gaps_recorded` otherwise |
| Archive format | **PDF/A-3** where a challan obligation applies; standard PDF otherwise |
| Retention | **At least 5 years** where statutory; `LG-009` operational otherwise |
| Re-render | Prohibited after dispatch |
| Reprint | Watermarked **COPY**, logged. **A reprinted gate pass cannot be used to move goods** (`GP-04`) |
| Gate log | Retained and reconciled daily (`GP-03`); the log itself is a retained record |
| In-transit ageing | Unconfirmed transfers are reported daily and escalated (`FM-26-e`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | Where inbound stock originates |
| [`DT-027_Delivery_Challan_and_Logistics_Manifest.md`](DT-027_Delivery_Challan_and_Logistics_Manifest.md) | Customer-property and third-party movements |
| [`DT-028_Proof_of_Delivery_and_Custody_Record.md`](DT-028_Proof_of_Delivery_and_Custody_Record.md) | Custody evidence where a carrier is involved |
| [`DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md`](DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md) | Where undocumented movements eventually appear |
| [`../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | Scrap leaving site |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Scanning payload |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-004_Warehouse_and_Storage_Location_Master.md) | Locations and bins |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-045_Fleet_and_Vehicle_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-045_Fleet_and_Vehicle_Master.md) | Vehicle particulars |
| [`SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-016_SOP_Spare_Parts_Issue_Return_and_Van_Stock.md) | How a movement is executed |
| `OP-014` Manual Fallback Procedure Set | Gate log reconciliation |
| `RP-016` Data Quality Scorecard Definition | In-transit ageing and discrepancy reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Two-part single-number design, in-transit state rule, destination-counts rule, six gate-pass security rules, van-stock challan question raised as G6 TR5 | COO with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Transfer note and gate pass unified under one number, with the reason stated
- [x] In-transit state defined and its ageing escalation specified
- [x] Destination-confirms-by-counting rule stated (`FM-26-b`)
- [x] Van-stock challan applicability raised explicitly (G6 TR5)
- [x] All internal links resolve
- [ ] **G6 TR1 — Mushak 6.5 applicability to inter-branch movement** — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6 TR5 — van stock treatment** — **outstanding; material process and `M15` design impact**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
