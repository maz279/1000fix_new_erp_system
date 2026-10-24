---
id: DT-028
title: Proof of Delivery and Custody Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Logistics
author: Logistics with Legal & Compliance and Content Design
reviewers: [Legal & Compliance, Operations, Finance, Security, Localisation Lead, Platform Engineering]
approver: Chief Operating Officer
content_class: C
purpose: >
  Recipient identity, photograph, OTP, signature, GPS and timestamp — the evidence set that closes
  a consignment. The custody-break target is zero and POD completeness target is 100%; this
  template is how both are evidenced. A consignment without a POD is an open custody liability
  and, where cash was collected, an unreconciled collection.
traces_to: [M03, M41, P09, P02, DT-001, DT-009, DT-016, DT-025, DT-026, DT-027, DT-044, MD-026, MD-040, BRU-LOG-01, BRU-LOG-02, BRU-LOG-06, BRU-FSM-09]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: DT-028_Proof_of_Delivery_and_Custody_Record_BN.md
sources:
  - source: 1000FiX_ERP_Content_Master_Index CATEGORY 05 DT-028 — custody-break target zero, POD completeness target 100%
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-01 — no custody transfer without a scan and an identity capture from both parties
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-02 — a consignment cannot be closed without proof of delivery
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FSM-05 — GPS capture occurs only during working hours and while on duty
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-028 — Proof of Delivery and Custody Record

> **A POD is an evidence set, not a signature.** Identity, photograph, OTP, geolocation and
> timestamp together answer the question a dispute asks: *who received what, where, when, and how
> do you know it was them?*
>
> **`BRU-LOG-02`: a consignment cannot close without one.** That rule is what makes the 100%
> completeness target achievable — completeness is enforced, not chased.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Delivery and custody evidence record |
| Owning module | `M03` Service Logistics, captured in `P09` and `P02` |
| Statutory | No — but it is the evidence that discharges bailment on a delivered customer device |
| Recipient(s) | Recipient (copy), logistics control, customer via portal, finance where cash was collected |
| Languages | **Bilingual — stacked labels.** Recipients and riders read Bengali |
| Output formats | **`P09` / `P02` app capture (primary)** · Thermal 58 mm recipient slip · PDF · A4 for disputes |
| Numbering mask | `MD-040` — `POD-{entity}-{yy}-{seq:06d}`, one per consignment leg |
| Retention period | `LG-009`; **retained with the consignment and, for customer devices, with the `DT-002`/`DT-009` custody pair** |

### 1.1 The evidence set

| # | Element | Why it is not sufficient alone |
|---|---|---|
| 1 | **Recipient identity** | A name alone is unverifiable |
| 2 | **Signature or OTP** | A signature can be anyone's; an OTP proves control of the registered number |
| 3 | **Photograph** | Proves the goods and the place, not the person |
| 4 | **GPS coordinates** | Proves location, not identity |
| 5 | **Timestamp** | Proves when, not what |
| 6 | **Item scan** | Proves which item, not who took it |
| 7 | **Rider identity** | Proves who handed over |

> **No single element proves delivery. The set does.** The minimum required combination per
> consignment type is in §5.1, and it is enforced at capture — the app will not close the stop
> without it.

---

## 2. Statutory Requirements

Not a prescribed form. Three obligations:

| Obligation | Source | Effect |
|---|---|---|
| Discharge of bailment on customer property | Bailment principle — **pending G6, shared with `DT-009`** | The POD is the evidence for a delivered device |
| Personal-data minimisation in evidence capture | `LG-008`, `05-06` NFR-086 | Photographs, GPS and ID references are personal data with a defined purpose and retention |
| GPS capture limited to duty hours | `BRU-FSM-05` | Rider location is captured on duty only; the POD carries the delivery location, not a movement history |

---

## 3. Layout

**Primary capture is in the app.** The printed renditions are the recipient slip and the dispute
rendition.

| Zone | Content | Bilingual |
|---|---|---|
| Header | POD number, consignment reference, date/time | Title stacked |
| Party block | Recipient left; rider, vehicle and manifest right | Labels stacked |
| Body | Items delivered → evidence captured → condition → cash collected → exceptions | Labels stacked |
| Totals | Package count delivered, cash collected | Arabic numerals |
| Statutory block | Not used. The **recipient acknowledgement** occupies this zone | Parallel columns |
| Signature | Recipient signature or OTP reference; rider identity | Labels stacked |
| Footer | POD reference, consignment reference, hotline | English |

| # | Rule |
|---|---|
| **L-28-a** | The recipient slip is deliberately short — reference, items, cash taken, acknowledgement, hotline. A rider handing over a dense A4 at a doorstep is a rider whose slip is not read |
| **L-28-b** | The **evidence set is listed on the slip** — "photo captured, OTP verified" — so the recipient knows what was recorded about them (`LG-008` transparency) |
| **L-28-c** | The dispute rendition (A4) includes the photograph, the map reference and the full evidence chain |
| **L-28-d** | Where cash was collected, a `DT-016` receipt is issued **in addition**. The POD is not a money receipt |
| **L-28-e** | The acknowledgement text is short and unambiguous in both languages |

---

## 4. Field Mapping

### 4.1 Delivery and identity

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| POD no. | প্রাপ্তি প্রমাণ নং | `MD-040` sequence | Monospace | ✔ |
| Consignment / challan no. | চালান নং | `DT-027` reference | Monospace | ✔ |
| Manifest no. | ম্যানিফেস্ট নং | `MAN-…` | Monospace | Where part of a trip |
| Delivery date and time | সরবরাহের সময় | `pod.delivered_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Rider / carrier | রাইডার / বাহক | `employee.display_name` + ID | Text | ✔ |
| Vehicle | যানবাহন | `MD-045.registration` | Monospace | Where used |
| **Recipient name** | **গ্রহীতার নাম** | `pod.recipient_name` | Text | ✔ |
| Relationship | সম্পর্ক | `pod.recipient_relationship` | Enum: self / family / colleague / security / authorised agent | ✔ |
| Recipient mobile (masked) | মোবাইল | `pod.recipient_mobile` | Last 4 | ✔ |
| **ID verified** | **পরিচয় যাচাই** | `pod.id_type` + masked ref | Enum + monospace | **✔ where not OTP-verified** |
| **OTP reference** | **ওটিপি সূত্র** | `pod.otp_ref` + timestamp | Monospace | ✔ where used |
| **Signature** | **স্বাক্ষর** | `pod.signature_ref` | Vector capture | ✔ where used |
| **Photograph** | **ছবি** | `pod.photo_ref[]` | Reference + count | ✔ per §5.1 |
| **GPS** | **জিপিএস** | `pod.geo_lat`, `.geo_lon`, accuracy | Coordinates | ✔ **on duty only (`BRU-FSM-05`)** |
| Geofence match | জিওফেন্স মিল | Computed against the address | Bool + distance | ✔ |

### 4.2 Items, condition, cash and exceptions

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Item scanned | স্ক্যানকৃত পণ্য | `pod.line.scan_ref` | Monospace | ✔ **(`BRU-LOG-01`)** |
| Item description / serial | বিবরণ / সিরিয়াল | Device or `MD-022` | Text + monospace | ✔ |
| Packages delivered | প্রদত্ত প্যাকেজ | `pod.package_count` | Integer | ✔ |
| Seal intact | সিল অক্ষত | `pod.seal_intact` | Bool | ✔ where sealed |
| Condition on delivery | সরবরাহকালীন অবস্থা | `pod.condition` | Enum + note | ✔ |
| Recipient condition remark | গ্রহীতার মন্তব্য | `pod.recipient_remark` | Free text | Where given |
| Cash collected | সংগৃহীত নগদ | `pod.cod_amount` | BDT, 2 dp | ✔ where COD |
| Receipt no. issued | রসিদ নং | `DT-016` reference | Monospace | **✔ where cash collected** |
| Delivery outcome | ফলাফল | `pod.outcome` | Enum: delivered / partial / refused / failed | ✔ |
| Exception reason | ব্যতিক্রমের কারণ | `MD-026.reason_code` | Code + label | ✔ where not delivered |
| Exception evidence | ব্যতিক্রমের প্রমাণ | `pod.exception_photo_ref[]` | Reference | **✔ where not delivered** |
| Attempt number | চেষ্টার ক্রম | Computed | Integer | ✔ |
| Acknowledgement | স্বীকৃতি | Static | Text, both languages | ✔ |

| # | Rule |
|---|---|
| **FM-28-a** | The item is **scanned** at handover, not typed (`BRU-LOG-01`). Typed identifiers are transcription, not verification |
| **FM-28-b** | Delivery to someone other than the addressee records the relationship and requires ID verification. **"Left with security" is a valid outcome only if the security officer is identified** |
| **FM-28-c** | GPS is captured with an accuracy figure. A coordinate with 500 m accuracy is not evidence of a doorstep |
| **FM-28-d** | Geofence mismatch beyond the tolerance requires an exception reason (`BRU-FSM-06` discipline applied to logistics) |
| **FM-28-e** | A failed or refused delivery requires geotagged evidence (`BRU-FSM-09`). **A failed attempt with no evidence is indistinguishable from an attempt not made** |
| **FM-28-f** | Cash collected produces a `DT-016` receipt with its own number; the POD records the receipt reference, not the money |
| **FM-28-g** | Photographs of people are avoided; the photograph evidences goods at a location. Where a recipient photograph is captured, consent and retention follow `LG-008` |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-LOG-01` | Scan and identity capture from both parties |
| `BRU-LOG-02` | No consignment closure without a POD |
| `BRU-LOG-03` | High-value consignments require dual signature — both signatories recorded |
| `BRU-LOG-04` | Seal break raises an incident and blocks onward movement |
| `BRU-LOG-06` | Cash reconciled per rider per shift, zero tolerance for unexplained variance |
| `BRU-LOG-08` | Failed delivery re-attempt policy; each attempt has its own POD record |
| `BRU-FSM-05` | GPS on duty only |
| `BRU-FSM-06` | Outside-geofence completion requires an exception reason |
| `BRU-FSM-09` | Failed visits require geotagged evidence |

### 5.1 Minimum evidence by consignment type

Enforced at capture. The app will not close a stop without the required set.

| Consignment type | Scan | Signature **or** OTP | Photo | GPS | ID |
|---|:--:|:--:|:--:|:--:|:--:|
| Customer device — delivery to customer | ✔ | **OTP required** | ✔ | ✔ | Where not OTP |
| Customer device — pickup from customer | ✔ | **OTP required** | ✔ | ✔ | Where not OTP |
| High-value (above `BRU-LOG-03`) | ✔ | **Both, dual signature** | ✔ | ✔ | ✔ |
| Stock between our sites | ✔ | Signature | — | ✔ | Employee ID |
| Return to supplier | ✔ | Signature | ✔ | ✔ | ✔ |
| E-waste to partner | ✔ | Signature | ✔ | ✔ | ✔ + partner certification |
| Refused / failed | ✔ | — | **✔ mandatory** | ✔ | — |

| # | Rule |
|---|---|
| **EV-01** | OTP is the strongest routine identity control available at a doorstep and is **mandatory for customer devices** |
| **EV-02** | Where the recipient's mobile is unreachable, delivery to that recipient requires ID verification and a supervisor authorisation recorded on the POD |
| **EV-03** | Offline capture is permitted; evidence syncs on reconnect with the **capture** timestamp preserved, not the sync timestamp (`UI-009`) |
| **EV-04** | An unsynced POD older than the threshold escalates. A rider's device holding uncommitted custody evidence is a custody gap |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **App capture** | The primary path (`P09`, `P02`) | Full evidence set, enforced at capture |
| **Thermal 58 mm recipient slip** | Handed over at the door | Short form (`L-28-a`), evidence list, hotline |
| **Dispute rendition A4** | Complaint or claim | Photograph, map reference, full evidence chain, all attempts |
| **Customer-device POD** | Device pickup or delivery | OTP mandatory; links `DT-002` ↔ `DT-009` |
| **High-value** | Above the `BRU-LOG-03` threshold | Dual signature, both parties identified |
| **Exception POD** | Failed, refused or partial | Reason code, geotagged evidence, next action stated |
| **Third-party courier** | External courier used | Courier POD captured as evidence **in addition to** ours where the courier's system is used |
| **Bulk corporate delivery** | `P04` multi-device drop | Per-serial scan with one recipient acknowledgement covering the schedule |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-028-S1` | Repaired device delivered, OTP verified | Base evidence set, customer-device minimum |
| `DT-028-S2` | Delivered to building security | `FM-28-b` relationship and ID capture |
| `DT-028-S3` | Refused delivery | `FM-28-e` geotagged exception evidence |
| `DT-028-S4` | COD BDT 4,200 | `FM-28-f` and the `DT-016` linkage |
| `DT-028-S5` | Offline capture, synced 4 hours later | `EV-03` timestamp preservation |
| `DT-028-S6` | High-value dual signature | `BRU-LOG-03` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Logistics with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Legal & Compliance (evidence and data protection) | *pending* | | |
| Reviewer — Operations | *pending* | | |
| Reviewer — Finance (COD) | *pending* | | |
| Reviewer — Platform Engineering (offline capture) | *pending* | | |
| Approver — Chief Operating Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `POD-{entity}-{yy}-{seq:06d}`, one per consignment leg including failed attempts |
| Gap policy | `gaps_recorded` |
| Archive format | Structured record in `M03` with evidence artefacts in `M24`; PDF/A-3 for the dispute rendition |
| Retention | `LG-009`; **customer-device PODs retained with the `DT-002`/`DT-009` custody pair**; evidence artefacts inherit the same period |
| Personal data | Photographs, GPS and ID references are minimised, purpose-bound and deleted on schedule (`LG-009`, `LG-008`) |
| Re-render | Prohibited |
| Reprint | Recipient slip may be reprinted as **COPY**; the evidence record is not re-issued |
| Completeness | POD completeness against closed consignments is reported daily against the **100% target** |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-027_Delivery_Challan_and_Logistics_Manifest.md`](DT-027_Delivery_Challan_and_Logistics_Manifest.md) | The consignment this closes |
| [`DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Inter-site custody |
| [`DT-025_Return_to_Vendor_and_Debit_Advice.md`](DT-025_Return_to_Vendor_and_Debit_Advice.md) | Evidence the supplier received the return |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Custody opened |
| [`../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md`](../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md) | Custody closed |
| [`../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md`](../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) | Cash collected on delivery |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Scan payload |
| `UI-009` Offline Sync and Conflict Resolution Copy | Offline capture behaviour |
| `UI-019` P09 Logistics and Rider App UI Copy Pack | Rider capture screens |
| `LG-008` Privacy Notice and Consent Copy | Evidence-capture data protection |
| [`SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | The operational procedure |
| `RP-004` Dashboard Specification Pack — Operational Consoles | POD completeness and custody-break reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven-element evidence set with per-type minimums enforced at capture, OTP-mandatory rule for customer devices, GPS accuracy requirement, offline timestamp-preservation rule, exception-evidence mandate | Chief Operating Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Evidence set defined element by element, with why each alone is insufficient
- [x] Per-consignment-type minimums specified and stated as capture-enforced
- [x] Failed and refused deliveries require evidence (`FM-28-e`)
- [x] Offline capture preserves the capture timestamp (`EV-03`)
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Legal review of evidence capture against `LG-008`, particularly recipient photographs — **outstanding**
- [ ] Geofence tolerance values agreed with Operations — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
