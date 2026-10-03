---
id: DT-027
title: Delivery Challan and Logistics Manifest
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Logistics
author: Logistics with Tax, Security and Content Design
reviewers: [External tax adviser, Tax, Legal & Compliance, Security, Operations, Localisation Lead]
approver: Chief Operating Officer with Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Consignment contents, route, handling instructions, seal number and the statutory movement
  documentation goods require in transit. The manifest also drives the rider application in P09 —
  it is simultaneously the legal document that accompanies goods on the road and the operational
  instruction set for the person carrying them.
traces_to: [M03, M41, M15, M51, P09, DT-001, DT-002, DT-025, DT-026, DT-028, DT-044, MD-003, MD-005, MD-026, MD-040, MD-045, BRU-LOG-01, BRU-LOG-03, BRU-LOG-04, BRU-LOG-05, BRU-SCM-05]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: DT-027_Delivery_Challan_and_Logistics_Manifest_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Form Mushak 6.5 — movement of goods without a sale. **Applicability to customer-device movements must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-03 — consignments above the declared-value threshold require dual signature and insurance flagging
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-05 — restricted items may only be carried by a rider or courier certified for them
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SCM-05 — sub-contracted devices must move under a logistics consignment with full custody evidence
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-027 — Delivery Challan and Logistics Manifest

> ⚠ **Tier S — movement documentation is a statutory obligation. Gate G6 mandatory and
> unwaivable (`WV-02`).**
>
> **Most of what this company moves is not its own property.** Customer devices travelling to a
> workshop and back are goods held in bailment (`DT-002`), not stock. The movement document must
> satisfy the tax position for goods in transit **and** the custody position for somebody else's
> property, and those are different obligations with different evidence.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Delivery challan + consignment manifest |
| Owning module | `M03` Service Logistics and Reverse Logistics, driving `P09` |
| Statutory | **Yes — Tier S**, subject to G6 confirmation |
| Recipient(s) | Rider or carrier, recipient, checkpoint authorities, logistics control, customer |
| Languages | **Bilingual — stacked labels.** Riders and checkpoint staff work in Bengali |
| Output formats | A5 portrait (challan, travels with goods) · A4 (multi-drop manifest) · `P09` app (primary operational view) · PDF |
| Numbering mask | `MD-040` — `DCH-{entity}-{yy}-{seq:06d}` challan; `MAN-{entity}-{yy}-{seq:06d}` manifest |
| Retention period | **At least 5 years** where a movement-challan obligation applies — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 Challan versus manifest

| | Delivery challan | Logistics manifest |
|---|---|---|
| Scope | **One consignment** | **One trip, many consignments** |
| Travels with | The goods | The rider |
| Purpose | Statutory movement document + custody | Route, sequence, instructions, reconciliation |
| Recipient signs | ✔ (via `DT-028`) | ✖ |
| Statutory | ✔ where applicable | ✖ |
| Numbered | `DCH-…` | `MAN-…` |

> One manifest lists many challans. A challan can exist without a manifest — a single dedicated
> movement — but a manifest never exists without challans.

### 1.2 What moves

| Movement | Property of | Custody instrument |
|---|---|---|
| Customer device to workshop | **Customer** | `DT-002` intake → this challan |
| Repaired device to customer | **Customer** | This challan → `DT-028` → `DT-009` |
| Device to a sub-contractor | **Customer** | `BRU-SCM-05` — full custody evidence required |
| Stock between our sites | Us | `DT-026`, this challan for the road leg |
| Goods returned to a supplier | Us | `DT-025` + this challan |
| Rental asset out and back | Us | `DT-037` + this challan |
| E-waste to a disposal partner | Us / regulated | `DT-035` + this challan |
| Marketplace seller collection | **Customer** | Same evidential standard (`BRU-ECM-03`) |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Movement documentation accompanying goods | VAT & SD Rules 2016 Mushak 6.5 — **pending G6** | pending | Challan |
| Consignor and consignee identity | **pending G6** | pending | Party block |
| Description and quantity of goods | **pending G6** | pending | Line items |
| Value of goods | **pending G6** | pending | Line items — see `L-27-e` |
| Vehicle and driver particulars | **pending G6** | pending | Transport block |
| Date, time and route | **pending G6** | pending | Header |
| Custody acknowledgement | Bailment; `BRU-LOG-01` | 2026-08-15 | Signature zone / `DT-028` |

### 2.1 G6 questions

| # | Question |
|---|---|
| **DC1** | Does a movement challan apply to **customer-owned devices** in our custody, and if so which form? |
| **DC2** | What value is shown for customer property — declared value, repair value, or none? |
| **DC3** | Must the document physically accompany the goods, or is an electronic record on the rider's device sufficient? (paired with `DT-026` TR3) |
| **DC4** | Are there route, checkpoint or inter-district requirements we must satisfy? |
| **DC5** | What documentation applies to goods moving to and from a sub-contractor? |
| **DC6** | Are there specific requirements for restricted goods — lithium batteries in particular, which are in almost every consignment we move? |

> **DC6 is not theoretical.** Nearly every device we transport contains a lithium battery.
> Whatever obligations attach to that are obligations on the majority of our movements.

---

## 3. Layout

**Challan: A5 portrait. Manifest: A4 portrait.**

| Zone | Challan content | Bilingual |
|---|---|---|
| Header | Challan number, date/time, consignment type | Title stacked |
| Party block | Consignor left, consignee right, both with address and contact | Labels stacked |
| Body | Line items, packaging, seal, handling instructions, declared value | Labels stacked |
| Totals | Package count, weight, declared value | Arabic numerals |
| Statutory block | Prescribed movement declaration | Parallel columns |
| Signature | Dispatcher, carrier, recipient (or `DT-028` reference) | Labels stacked |
| Footer | Challan reference, `page n of m`, hotline, manifest reference | English |
| Machine-readable | QR: challan reference + consignment ID (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-27-a** | **Handling instructions print in Bengali first** on the challan. The person who must follow them reads Bengali |
| **L-27-b** | Restricted-item declarations print in a distinct, bordered block. They are a safety instruction, not a data field |
| **L-27-c** | The seal number and package count are the two fields checked at every handover; they print largest in the body |
| **L-27-d** | Customer-property consignments print **"CUSTOMER PROPERTY — HANDLE AS SUCH"** in both languages |
| **L-27-e** | Declared value prints per **G6 DC2**. Where it prints, the insurance position prints beside it (`BRU-LOG-03`) |
| **L-27-f** | The manifest prints the drop sequence, the address, the contact and the exception route per stop — it is the rider's working document |

---

## 4. Field Mapping

### 4.1 Challan

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Challan no. | চালান নং | `MD-040` sequence | Monospace | ✔ |
| Date and time | তারিখ ও সময় | `consignment.dispatched_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Consignment type | চালানের ধরন | `consignment.type` | Enum per §1.2 | ✔ |
| Consignor | প্রেরক | `MD-003` / `MD-004` + BIN | Text + monospace | ✔ |
| Consignee | প্রাপক | `party` or location + contact | Text | ✔ |
| Delivery address | সরবরাহ ঠিকানা | `MD-007` formatted address | Text | ✔ |
| Zone / route | জোন / রুট | `MD-005.zone_code` | Code + label | ✔ |
| Item description | পণ্যের বিবরণ | Device or `MD-022` | Text | ✔ |
| Serial / IMEI / asset tag | সিরিয়াল | `device.serial_no` | Monospace | ✔ for devices |
| Quantity / packages | পরিমাণ / প্যাকেজ | `consignment.package_count` | Integer | ✔ |
| Weight | ওজন | `consignment.weight_kg` | kg, 2 dp | ✔ |
| **Seal number** | **সিল নং** | `consignment.seal_no[]` | Monospace | ✔ where sealed |
| **Declared value** | **ঘোষিত মূল্য** | Per G6 DC2 | BDT, 2 dp | Per G6 |
| Insurance flagged | বিমা চিহ্নিত | `consignment.insured` | Bool + policy ref | **✔ above the `BRU-LOG-03` threshold** |
| Dual signature required | দ্বৈত স্বাক্ষর | Computed | Bool | **✔ above threshold** |
| **Restricted items** | **সীমাবদ্ধ পণ্য** | `consignment.restricted[]` | Enum: lithium battery / refrigerant / other | ✔ |
| Carrier certification | বাহকের সনদ | `MD-011` / courier certification | Code | **✔ where restricted (`BRU-LOG-05`)** |
| Handling instructions | হ্যান্ডলিং নির্দেশনা | `consignment.handling[]` | Text | ✔ |
| Carrier / rider | বাহক | `employee.display_name` / courier + ID | Text | ✔ |
| Vehicle registration | যানবাহন নং | `MD-045.registration` | Monospace | ✔ where a vehicle is used |
| Manifest reference | ম্যানিফেস্ট সূত্র | `MAN-…` | Monospace | Where part of a trip |
| POD reference | প্রাপ্তির প্রমাণ | `DT-028` reference | Monospace | ✔ on completion |

### 4.2 Manifest

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Manifest no. | ম্যানিফেস্ট নং | `MD-040` sequence | Monospace | ✔ |
| Trip date | ভ্রমণের তারিখ | `manifest.trip_date` | `DD/MM/YYYY` | ✔ |
| Rider / driver | রাইডার / চালক | `employee.display_name` + ID | Text | ✔ |
| Vehicle | যানবাহন | `MD-045` | Text + monospace | ✔ |
| Zone | জোন | `MD-005` | Code + label | ✔ |
| Stop sequence | স্টপ ক্রম | Computed | Integer | ✔ |
| Challan no. per stop | চালান নং | `DCH-…` | Monospace | ✔ |
| Action | কার্যক্রম | Enum: pickup / delivery / both | Label | ✔ |
| Time window | সময়সীমা | `manifest.stop.window` | `HH:mm–HH:mm` | ✔ |
| Contact | যোগাযোগ | Recipient name + mobile | Text | ✔ |
| Cash to collect | সংগ্রহযোগ্য নগদ | `manifest.stop.cod_amount` | BDT, 2 dp | ✔ where COD |
| Exception route | ব্যতিক্রম নির্দেশনা | Static + hotline | Text | ✔ |
| **Total cash expected** | **মোট প্রত্যাশিত নগদ** | Computed | BDT, 2 dp | ✔ **`BRU-LOG-06`** |
| Total consignments | মোট চালান | Computed | Integer | ✔ |

| # | Rule |
|---|---|
| **FM-27-a** | Every consignment carries a challan. **A device moving without one is a device with no custody record**, and `DT-002` liability continues with no evidence of where it went |
| **FM-27-b** | Restricted-item declaration and carrier certification are checked **before** dispatch, not at the roadside (`BRU-LOG-05`) |
| **FM-27-c** | Consignments above the declared-value threshold require dual signature and insurance flagging (`BRU-LOG-03`); both print |
| **FM-27-d** | Sub-contractor movements carry full custody evidence (`BRU-SCM-05`) — the sub-contractor signs as a custodian, not as a recipient |
| **FM-27-e** | The manifest's total cash expected is reconciled per rider per shift with **zero tolerance for unexplained variance** (`BRU-LOG-06`) |
| **FM-27-f** | A consignment cannot close without a POD (`BRU-LOG-02`, `DT-028`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-LOG-01` | Scan and identity capture from both parties at every custody transfer |
| `BRU-LOG-02` | A consignment cannot close without proof of delivery |
| `BRU-LOG-03` | Declared-value threshold triggers dual signature and insurance flagging |
| `BRU-LOG-04` | Seal break or weight discrepancy raises an incident and blocks onward movement |
| `BRU-LOG-05` | Restricted items only with a certified carrier |
| `BRU-LOG-06` | Cash on delivery reconciled per rider per shift, zero tolerance |
| `BRU-LOG-07` | Logistics charges waived automatically where contract, warranty or Privilege tier entitles the customer — the challan shows the entitlement, not a blank charge |
| `BRU-LOG-08` | Failed delivery re-attempted per policy, then returned to origin with charge rules applied |
| `BRU-SCM-05` | Sub-contracted devices move under a consignment with full custody evidence |

### 5.1 Failed delivery

| # | Rule |
|---|---|
| **FD-01** | A failed attempt is recorded with a reason code, geotagged evidence and a timestamp (`BRU-FSM-09` discipline applied to logistics) |
| **FD-02** | The challan remains open; the consignment does **not** close on a failed attempt |
| **FD-03** | Re-attempt follows `BRU-LOG-08` policy; each attempt is recorded separately |
| **FD-04** | After the policy limit, the consignment returns to origin under the **same challan number**, with the return leg recorded |
| **FD-05** | Customer property returned to origin re-enters custody under `DT-002`'s original terms — the abandonment clock in `BRU-SRM-16` does not restart |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Customer device challan** | Pickup or delivery of customer property | `L-27-d` marking; declared value per G6 DC2; custody language throughout |
| **Multi-drop manifest** | Rider trip (`P09`) | A4 manifest listing challans in drop sequence |
| **Inter-site stock leg** | Road leg of a `DT-026` transfer | References the STN; value per G6 TR2 |
| **Return to supplier** | With `DT-025` | Consignee is the supplier; return authorisation referenced |
| **Sub-contractor** | `BRU-SCM-05` | Custodian signature block, not a recipient block; return leg pre-booked |
| **E-waste to partner** | With `DT-035` | Weight and composition; partner certification checked before dispatch (`BRU-ESG-02`) |
| **Rental asset** | With `DT-037` | Condition report referenced at both ends |
| **Third-party courier** | Where an external courier is used | Courier's own documentation does **not** replace ours; both travel |
| **High-value** | Above the `BRU-LOG-03` threshold | Dual signature, insurance reference, restricted routing |

---

## 7. Worked Example

> **Statutory element specimens follow G6 DC1.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-027-S1` | Customer device pickup, single consignment | Base bilingual challan, custody marking |
| `DT-027-S2` | Rider trip, 11 stops, 4 COD | Manifest with cash reconciliation total |
| `DT-027-S3` | Lithium battery declared | `L-27-b` block and `BRU-LOG-05` certification check |
| `DT-027-S4` | High-value consignment | Dual signature and insurance flag |
| `DT-027-S5` | Two failed attempts then return to origin | `FD-01`…`FD-05` |
| `DT-027-S6` | Sub-contractor movement | `BRU-SCM-05` custody evidence |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Logistics with Tax and Security | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Legal & Compliance (custody language) | *pending* | | |
| Reviewer — Security | *pending* | | |
| Reviewer — Operations | *pending* | | |
| **G6 — external tax and legal verification (DC1–DC6)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — COO with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequences | Challan `DCH-…` and manifest `MAN-…`, separate |
| Gap policy | **`no_gaps` on the challan where a statutory movement obligation applies**; `gaps_recorded` on the manifest |
| Archive format | **PDF/A-3** for challans where statutory; standard PDF for manifests |
| Retention | **At least 5 years** where statutory; `LG-009` operational otherwise. **Customer-property challans are retained with the `DT-002`/`DT-009` custody pair** |
| Re-render | Prohibited after dispatch |
| Reprint | Watermarked **COPY**, logged; a reprinted challan cannot authorise a new movement |
| Linkage | `DT-002` → `DT-027` → `DT-028` → `DT-009` is the complete custody chain for a customer device |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-028_Proof_of_Delivery_and_Custody_Record.md`](DT-028_Proof_of_Delivery_and_Custody_Record.md) | Closes every consignment |
| [`DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Inter-site stock movements |
| [`DT-025_Return_to_Vendor_and_Debit_Advice.md`](DT-025_Return_to_Vendor_and_Debit_Advice.md) | Supplier returns |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Opens custody on customer devices |
| [`../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md`](../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md) | Closes it |
| [`../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | E-waste movements |
| [`../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md`](../../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-005_Dispatch_Zone_and_Territory_Master.md) | Zones and routing |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-045_Fleet_and_Vehicle_Master.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-045_Fleet_and_Vehicle_Master.md) | Vehicle particulars |
| `UI-019` P09 Logistics and Rider App UI Copy Pack | The rider-facing experience |
| [`NT-017_Push_Notification_Library_P09_Rider_App.md`](../../04_Notification_and_Messaging/04B_WhatsApp_and_Push/NT-017_Push_Notification_Library_P09_Rider_App.md) | Manifest and exception messages |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | How a consignment is built and dispatched |
| `RP-004` Dashboard Specification Pack — Operational Consoles | POD completeness and custody-break reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Challan-versus-manifest distinction, eight movement types with custody instrument mapped, Bengali-first handling instructions, restricted-item pre-dispatch check, five failed-delivery rules, lithium-battery question raised as G6 DC6 | COO with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Challan and manifest distinguished with separate sequences and purposes
- [x] Customer-property movements distinguished from stock movements throughout
- [x] Restricted-item handling made a pre-dispatch check (`FM-27-b`)
- [x] Failed delivery and return-to-origin fully specified, including the `BRU-SRM-16` interaction
- [x] All internal links resolve
- [ ] **G6 DC1/DC2 — movement documentation and value for customer property** — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6 DC6 — lithium-battery transport obligations** — **outstanding; affects the majority of movements**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
