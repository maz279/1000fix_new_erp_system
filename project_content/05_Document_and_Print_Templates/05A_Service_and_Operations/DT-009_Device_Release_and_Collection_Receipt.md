---
id: DT-009
title: Device Release and Collection Receipt
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations with Legal & Compliance
author: Operations with Legal & Compliance and Content Design
reviewers: [Legal & Compliance, Branch Operations, Finance, Logistics, Localisation Lead]
approver: Chief Operating Officer with Legal Counsel
content_class: A
purpose: >
  Closes the custody chain opened by DT-002. Records identity verification of the collector,
  accessories returned, the customer's acknowledgement of condition, payment status and the
  signature or OTP that discharges the company's liability as bailee. Uncollected-device
  liability, and every "you did not give it back" dispute, turns on this document.
traces_to: [M04, M03, M01, M20, P09, DT-001, DT-002, DT-007, DT-016, DT-028, MD-040, LG-013, BRU-SRM-05, BRU-SRM-16, BRU-LOG-01, BRU-FIN-02]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-009_Device_Release_and_Collection_Receipt_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-16 — a device uncollected 30 days after Ready enters the abandonment process with statutory notice
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-LOG-01 — no custody transfer without a scan and an identity capture from both parties
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-02 — cash receipts above BDT 50,000 require the customer's NID to be recorded
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05A_Service_and_Operations/DT-002 §6.2 clause T-7 — the collection and abandonment term this document discharges
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-009 — Device Release and Collection Receipt

> ⚠ **Class A — statutory consequence.** `DT-002` is the company taking possession. This is the
> company giving it back. Between those two documents the company is a **bailee**, and the
> liability that attaches to that role is only discharged by this record.
>
> **A device handed over without this receipt is, in evidence, a device still in our custody.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Custody discharge / collection receipt |
| Owning module | `M04` Branch and Front Desk Operations, with `M03` for delivered releases |
| Statutory | **Yes** — discharge of bailment; the counterpart to the `BRU-SRM-16` abandonment process. Instrument confirmed at **G6** |
| Recipient(s) | Collector (original), branch file, `P01`/`P04` portal record |
| Languages | **Bilingual — stacked labels, parallel columns for the acknowledgement** |
| Output formats | A5 portrait (primary) · Thermal 80 mm (counter variant) · A4 (corporate multi-device) · PDF |
| Numbering mask | `MD-040` — `REL-{entity}-{branch}-{yy}-{seq:06d}`, branch-aware, `no_gaps` |
| Retention period | `LG-009`; matched to `DT-002`, minimum the tax retention period |

### 1.1 Release channels

| Channel | Identity verification | Acknowledgement |
|---|---|---|
| Branch counter | Photo ID or the registered mobile + OTP | Signature or OTP |
| Authorised third party | **Written authorisation + collector's photo ID**, both recorded | Signature + ID reference |
| Field return by technician | Registered mobile + OTP at the address | On-screen signature |
| Rider delivery (`P09`) | OTP + photo + GPS (`DT-028`) | OTP; `DT-028` is the custody evidence, this is the release record |
| Corporate collection | Authorised signatory from `MD-015` hierarchy | Signature + delegation reference |
| Uncollected → disposed | **No release.** The abandonment path in §6.1 applies instead | Statutory notice trail |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Evidence of redelivery discharging bailment | Bailment principle; Contract Act — **pending G6** | 2026-08-15 (unverified) | Whole document |
| Identity of the person taking delivery | `BRU-LOG-01`; abandonment defence | 2026-08-15 | §4.1 collector block |
| Acknowledgement of the goods and their condition | Consumer Rights Protection Act 2009 — **pending G6** | 2026-08-15 (unverified) | §4.3 acknowledgement |
| NID capture on cash above BDT 50,000 | `BRU-FIN-02` | 2026-08-15 | §4.4 payment block |
| Statutory notice trail where the device was not collected | `BRU-SRM-16`; `DT-002` T-7 | 2026-08-15 | §6.1 |

> **G6 instruction.** Legal Counsel confirms (a) what constitutes valid discharge of bailment on
> redelivery, (b) the evidential standard for release to an authorised third party, and (c) the
> full statutory notice sequence before a device may be disposed of. Item (c) is shared with
> `DT-002` and must be answered once, consistently, for both.

---

## 3. Layout

**Primary format: A5 portrait.**

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Release number, intake reference, service order reference, date/time | Title stacked |
| Party block | Collector identity left; device and order metadata right | Labels stacked |
| Body | Device returned → accessories returned → condition acknowledgement → work summary reference → payment status | Labels stacked |
| Totals | Payment status only: invoiced, paid, outstanding | Numerals per `BL-05` |
| Statutory block | **Customer acknowledgement** — five statements | Parallel columns |
| Signature | Collector; releasing employee; witness where the collector cannot sign | Labels stacked |
| Footer | Release reference, page n of m, hotline | English reference |
| Machine-readable | QR: release reference + device serial (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-09-a** | The accessories block prints the **intake list** from `DT-002` alongside what is being returned, with any difference explained. Returning fewer accessories than were received, silently, is the most common release dispute |
| **L-09-b** | The acknowledgement block never splits across a page |
| **L-09-c** | The thermal variant carries reference, device, accessories and acknowledgement; where it cannot render the full acknowledgement legibly, the A5 is issued instead. **The acknowledgement is never abbreviated away** |
| **L-09-d** | Payment status prints as a **state**, not a figure alone: `PAID`, `PARTIALLY PAID — BDT n outstanding`, or `RELEASED UNPAID — approved by {name}` |

---

## 4. Field Mapping

### 4.1 Header and collector identity

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Release no. | ছাড়পত্র নং | `MD-040` sequence | Monospace | ✔ |
| Intake reference | গ্রহণ রসিদ নং | `DT-002` reference | Monospace | ✔ |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ |
| Released at | ছাড়ের সময় | `release.released_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Days since ready | প্রস্তুতের পর দিন | Computed | Integer | ✔ — **drives `BRU-SRM-16`** |
| Released by | ছাড়দাতা | `employee.display_name` + ID | Text | ✔ |
| Collector name | গ্রহীতার নাম | `release.collector_name` | Text | ✔ |
| Relationship to customer | সম্পর্ক | `release.collector_relationship` | Enum: self / authorised representative / corporate signatory / courier | ✔ |
| ID type and reference | পরিচয়পত্র | `release.collector_id_type` + masked number | Text + monospace | **✔ where not `self` with OTP** |
| Authorisation reference | অনুমোদন সূত্র | `release.authorisation_ref` | Monospace | **✔ where `authorised representative`** |
| OTP verification | ওটিপি যাচাই | `release.otp_ref` | Reference + timestamp | ✔ where used |

### 4.2 Device and accessories

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Device | ডিভাইস | `MD-021` make + model | Text | ✔ |
| Serial / IMEI | সিরিয়াল | `device.serial_no` | Monospace | ✔ — **verified by scan at release** |
| Accessories received at intake | গ্রহণকালে | `DT-002` `intake.accessories[]` | List | ✔ |
| Accessories returned | ফেরত প্রদত্ত | `release.accessories_returned[]` | List | ✔ |
| Difference explained | পার্থক্যের ব্যাখ্যা | `MD-026.reason_code` + note | Code + text | **✔ where lists differ** |
| Removable media | সিম / মেমরি কার্ড | `release.removable_media` | Enum: returned / not held | ✔ |
| Old parts returned | পুরাতন যন্ত্রাংশ | `DT-007` disposition | Enum + list | ✔ |
| Condition at release | ছাড়কালীন অবস্থা | `DT-002` §6.1 enumeration | Enum per attribute | ✔ |
| Photographs at release | ছাড়কালীন ছবি | `release.photo_count` | Integer | ✔ — **minimum 2** |

### 4.3 Work and acknowledgement

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Completion report no. | সমাপ্তি রিপোর্ট নং | `DT-007` reference | Monospace | ✔ where work was performed |
| Work summary | কাজের সারসংক্ষেপ | `DT-007` action list | One line per action | ✔ |
| Repair warranty to | ওয়ারেন্টি মেয়াদ | `DT-007` warranty end | `DD/MM/YYYY` | ✔ where granted |
| Not repaired — reason | মেরামত হয়নি — কারণ | `MD-026.reason_code` | Code + label | ✔ where applicable |
| Acknowledgement A-1…A-5 | স্বীকৃতি | Static | Text, parallel columns | ✔ |
| Collector signature | গ্রহীতার স্বাক্ষর | `release.signature_ref` | Image / vector / OTP ref | ✔ |
| Witness | সাক্ষী | `release.witness_name` + ID | Text | Where the collector cannot sign |

### 4.4 Payment status

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Invoice no. | চালান নং | `DT-010` reference | Monospace | ✔ where invoiced |
| Invoice total | চালান মোট | `invoice.total` | BDT, 2 dp | ✔ where invoiced |
| Amount paid | পরিশোধিত | `payment.total` | BDT, 2 dp | ✔ |
| Outstanding | বকেয়া | Computed | BDT, 2 dp | ✔ |
| Payment status | পরিশোধের অবস্থা | Computed | Per `L-09-d` | ✔ |
| Receipt no. | রসিদ নং | `DT-016` reference | Monospace | ✔ where paid at release |
| NID recorded | এনআইডি সংরক্ষিত | `party.national_id` masked | Monospace | **✔ cash > BDT 50,000 (`BRU-FIN-02`)** |
| Release without payment approved by | বিনা পরিশোধে ছাড় অনুমোদন | `employee.display_name` + ID | Text | **✔ where outstanding > 0** |

| # | Rule |
|---|---|
| **FM-09-a** | The serial is **scanned**, not read, at release. Releasing the wrong device to the wrong customer is a recoverable error only if it is detected at the counter |
| **FM-09-b** | Accessory lists are reproduced from `DT-002`, never re-entered. A re-typed list is a list that can be quietly shortened |
| **FM-09-c** | Release with an outstanding balance requires a named approver and prints their name. An unapproved unpaid release is a control failure, not a customer courtesy |
| **FM-09-d** | Where the device is not repaired, the reason and the charge position both print. "Returned as received" is not sufficient |
| **FM-09-e** | Minimum two photographs at release, mirroring intake. They are the company's evidence in the dispute that arrives a week later |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-05` | An invoice exists only for a Completed order; release before invoicing prints `NOT YET INVOICED` rather than a blank |
| `BRU-SRM-16` | Days-since-ready prints on every release. At 30 days the abandonment process has begun and §6.1 applies |
| `BRU-SRM-20` | The purge of any access note provided at intake is confirmed here, in the acknowledgement block |
| `BRU-LOG-01` | Custody transfer requires a scan and identity capture from **both** parties |
| `BRU-FIN-02` | Cash above BDT 50,000 requires NID capture before the receipt can issue |
| `BRU-FIN-03` | A payment cannot be recorded against a cancelled invoice; release against one is blocked |
| `BRU-FSM-07` | On-site payment must be reconciled to the branch cash book by the end of the technician's shift |
| `BRU-DMS-03` | Once signed, this record is immutable. A correction is a new record citing the original |

### 5.1 The five acknowledgements

| # | Acknowledgement | Why it is separate |
|---|---|---|
| **A-1** | The device identified above has been received back | The core discharge |
| **A-2** | The accessories listed as returned have been received | Separated because accessory disputes are distinct from device disputes |
| **A-3** | The condition of the device has been inspected and is accepted | Must be an act, not an assumption |
| **A-4** | The work summary and any warranty granted have been explained | Prevents "nobody told me what was done" |
| **A-5** | Any access code provided has been confirmed removed from our records | `BRU-SRM-20` closure, visible to the customer |

> Five separate acknowledgements, not one paragraph. A single "I accept everything" tick is
> weak evidence and is routinely set aside. Wording confirmed by Legal at **G6**.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Counter A5** | Branch collection, the default | The base document |
| **Thermal 80 mm** | High-volume counters | Compressed; full acknowledgement or the A5 is issued instead (`L-09-c`) |
| **Field return** | Technician returns on site | Adds GPS and address; on-screen signature |
| **Rider delivery** | `P09` | Pairs with `DT-028`; OTP acknowledgement; the rider is not the collector, the recipient is |
| **Corporate multi-device A4** | `P04` bulk collection | Device schedule with per-device serial verification; one authorised signature |
| **Third-party authorised** | Someone other than the customer collects | Authorisation reference and collector ID mandatory; the customer is notified by SMS at the moment of release (`NT-004`) |
| **Unrepaired return** | Estimate declined or BER | Reason, charge position, and the condition-as-returned statement |
| **Partial release** | Multi-device order, some devices ready | Releases only the listed serials; the order remains open with the balance stated |

### 6.1 The device that is never collected

This document's absence is itself a process. Where a device is not collected:

| Stage | Trigger | Artefact |
|---|---|---|
| Ready | Work complete | `NT-004` ready-for-collection SMS, repeated per `NT-003` frequency policy |
| Day 7 / 14 | Still uncollected | Escalating reminders; storage-charge notice if the terms provide for one (`DT-002` T-7) |
| **Day 30** | `BRU-SRM-16` | **Abandonment process opens.** Formal notice issued to the registered address and mobile |
| Statutory notice period | Per the instrument — **pending G6** | Notice trail retained as the disposal defence |
| Disposal | Notice period expires with no response | Disposal record, valuation, and any proceeds treated per `LG-013`. **`DT-035` applies where the device goes to e-waste** |

| # | Rule |
|---|---|
| **UC-01** | Every notice in the sequence is retained. The disposal defence is the **trail**, not the final notice |
| **UC-02** | Disposal cannot proceed where the intake receipt did not print term T-7 (`DT-002` §9). A device received without that clause is held indefinitely |
| **UC-03** | A device containing customer data is data-destroyed before disposal (`DT-034`, `BRU-ESG-01`), regardless of the abandonment position |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-009-S1` | Branch collection, paid in full | Base bilingual rendition, five acknowledgements |
| `DT-009-S2` | Third-party collection with authorisation | Identity and authorisation evidence |
| `DT-009-S3` | One accessory not returned, explained | `L-09-a` difference handling |
| `DT-009-S4` | Released with BDT 3,200 outstanding | `FM-09-c` named approver |
| `DT-009-S5` | Unrepaired return after declined estimate | Reason and charge position |
| `DT-009-S6` | Corporate 18-device partial release | Per-device verification, order remains open |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Operations with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Branch Operations | *pending* | | |
| Reviewer — Finance | *pending* | | |
| Reviewer — Logistics | *pending* | | |
| **G6 — external legal verification** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — COO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `REL-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `no_gaps` — an abandoned release attempt keeps its number and records the abandonment |
| Reset | Fiscal year |
| Archive format | **PDF/A-3 at issue** (class A, `R-02`) |
| Retention | `LG-009`; matched to `DT-002` — the pair is the complete custody record and is retained as one |
| Re-render | Prohibited (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged (`RC-01`, `RC-03`) |
| Pairing rule | An intake reference with no release reference after the abandonment window is an **open custody item** and appears on the branch's daily exception report |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | **The document this closes** |
| [`DT-007_Service_Completion_Report.md`](DT-007_Service_Completion_Report.md) | Handed over with it |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | The invoice whose payment status prints here |
| [`../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md`](../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) | Issued where payment is taken at release |
| [`../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md`](../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md) | The rider-delivery custody evidence |
| [`../05D_Commercial_and_Contract/DT-034_Data_Destruction_Certificate.md`](../05D_Commercial_and_Contract/DT-034_Data_Destruction_Certificate.md) | Required before an abandoned data-bearing device is disposed of |
| [`../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](../05D_Commercial_and_Contract/DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | Where an abandoned device goes to e-waste |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The terms this discharges |
| [`NT-004_SMS_Template_Library_Customer.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | The ready and reminder messages in §6.1 |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | How a person performs it, including the notice sequence |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six release channels, accessory reconciliation against intake, five separate acknowledgements, unpaid-release approval control, and the uncollected-device notice sequence with its three rules | COO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Every mandated element listed in §2 with source and verification date
- [x] Accessory reconciliation against `DT-002` specified (`L-09-a`, `FM-09-b`)
- [x] Five acknowledgements separated, with the reason for separation stated
- [x] Uncollected-device path documented (§6.1) including the `UC-02` dependency on `DT-002` T-7
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] **G6** legal verification of bailment discharge, third-party release standard and the notice sequence — **outstanding, unwaivable (`WV-02`)**; must be answered **jointly with `DT-002`**
- [ ] Thermal legibility of the full acknowledgement tested per printer model (`VB-004` TH-08) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
