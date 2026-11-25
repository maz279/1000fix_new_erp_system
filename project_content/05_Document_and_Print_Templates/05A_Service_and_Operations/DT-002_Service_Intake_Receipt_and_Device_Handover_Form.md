---
id: DT-002
title: Service Intake Receipt and Device Handover Form
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
reviewers: [Legal & Compliance, Branch Operations, Quality, Data Services, Localisation Lead, Platform Engineering]
approver: Chief Operating Officer with Legal Counsel
content_class: A
purpose: >
  The custody document. Records device identity, declared condition, accessories received, the
  customer's declarations, the data-backup warning and the liability terms at the moment the
  company takes possession. Disputes about device condition at intake are the most common
  customer conflict in device service; without this document the company has no evidence.
traces_to: [M04, M17, M01, M06, DT-001, DT-009, DT-044, MD-024, MD-040, LG-013, BRU-SRM-01, BRU-SRM-20, 05-05 §1]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-002_Service_Intake_Receipt_and_Device_Handover_Form_BN.md
sources:
  - source: project_content/05_Document_and_Print_Templates/DT-001 Document Template Standard §2.2 — Tier S classification and instrument citation obligation
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-01 — a service order cannot be created without an identified device
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-20 — customer data-access notes captured only with explicit consent and purged at handover
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-16 — a device uncollected 30 days after Ready enters the abandonment process with statutory notice
    verified: 2026-08-15
    class: P1
  - source: Consumer Rights Protection Act 2009 — obligation to issue a receipt/memo for goods and services received — **to be verified against the enacted text at G6**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-002 — Service Intake Receipt and Device Handover Form

> ⚠ **Class A — statutory consequence.** This document is the company's only evidence of what
> it received and in what condition. Everything downstream — the estimate, the repair, the
> release, the dispute, the abandonment notice — refers back to it.
>
> **A device accepted without a completed intake receipt is a device the company cannot prove
> it received, cannot prove the condition of, and cannot lawfully dispose of if abandoned.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Custody receipt and handover form |
| Owning module | `M04` Branch and Front Desk Operations, with `M17` Device and Customer Asset Registry |
| Statutory | **Yes** — consumer receipt obligation; prerequisite for the statutory abandonment notice under `BRU-SRM-16`. Instrument to be confirmed at **G6** |
| Recipient(s) | Customer (original), branch file (archive copy), technician (working copy via `DT-003`) |
| Languages | **Bilingual — parallel columns** for terms and declarations, **stacked** for field labels |
| Output formats | A5 portrait (primary, branch counter) · Thermal 80 mm (queue slip variant) · A4 portrait (corporate multi-device variant) · PDF/A-3 archive |
| Numbering mask | `MD-040` — `INT-{entity}-{branch}-{yy}-{seq:06d}`, branch-aware, `no_gaps` |
| Retention period | `LG-009` — minimum the tax retention period; longer where a dispute or hold exists |

### 1.1 Intake channels this document serves

| Channel | Who completes it | Signature capture |
|---|---|---|
| Branch counter (`M04`) | Front-desk agent with the customer present | Wet signature or on-screen signature |
| Field collection (`M02`, `P02`) | Technician at the customer's premises | On-screen signature on the technician app |
| Courier / rider pickup (`M03`, `P09`) | Rider, against the pre-booked job | OTP + photo evidence |
| Corporate bulk drop (`P04`) | Account handler, one header + device schedule | Authorised signatory, wet or e-signature |
| Marketplace seller intake (`P07`) | Seller, under the same evidential standard (`BRU-ECM-03`) | On-screen signature |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Issue of a receipt for goods taken into possession for service | Consumer Rights Protection Act 2009 — **pending G6** | 2026-08-15 (unverified) | Whole document |
| Identity of the receiving entity, with BIN | VAT & SD Act 2012 registration display obligation — **pending G6** | 2026-08-15 (unverified) | Header |
| Description sufficient to identify the goods | Bailment / custody principle — **pending G6** | 2026-08-15 (unverified) | §4.2 device block |
| Statement of the terms on which goods are held | Contract of bailment — **pending G6** | 2026-08-15 (unverified) | §6.2 clause T-1…T-8 |
| Notice period and consequence of non-collection | Prerequisite for `BRU-SRM-16` abandonment — **pending G6** | 2026-08-15 (unverified) | §6.2 clause T-7 |
| Personal-data processing notice and consent | Data-protection regime at `05-06` NFR-086; `LG-008` | 2026-08-15 | §6.2 clauses T-3, T-4 |

> **G6 instruction.** Legal Counsel confirms (a) whether a prescribed receipt form exists for
> service intake, (b) the minimum lawful notice period before a device may be treated as
> abandoned, and (c) the enforceability of the limitation-of-liability wording in §6.2 clause T-8. Until
> all three are recorded, this template remains `Draft` and the abandonment clause prints the
> conservative 90-day period, not 30.

---

## 3. Layout

**Primary format: A5 portrait.** Geometry per `VB-004` §4, scaled: 12 mm margins, 20 mm header.

```
┌──────────────────────────────────────────────┐
│ [LOGO]        SERVICE INTAKE RECEIPT         │  Header
│               সার্ভিস গ্রহণ রসিদ                  │
│ 1000FiX Services Limited · BIN ############  │
├──────────────────────────────────────────────┤
│ CUSTOMER              │ RECEIPT              │
│ Name / নাম            │ No.  INT-…-000482    │
│ Mobile / মোবাইল        │ Date 15/08/2026 14:20│
│ Address               │ Branch  Shewrapara   │
│                       │ Received by  A. Rahman│
├──────────────────────────────────────────────┤
│ DEVICE / ডিভাইস                               │
│ Type · Brand · Model · Serial / IMEI          │
│ [QR: intake ref + serial — DT-044]            │
├──────────────────────────────────────────────┤
│ REPORTED FAULT / জানানো সমস্যা                  │
├──────────────────────────────────────────────┤
│ CONDITION AT INTAKE / গ্রহণকালীন অবস্থা          │
│ Checklist + photo count + remarks             │
├──────────────────────────────────────────────┤
│ ACCESSORIES RECEIVED / গৃহীত আনুষঙ্গিক           │
├──────────────────────────────────────────────┤
│ ESTIMATE & TURNAROUND / প্রাক্কলন ও সময়          │
├──────────────────────────────────────────────┤
│ DECLARATIONS AND TERMS — parallel columns    │  Statutory block
│ বাংলা                    │ English            │  (never splits)
├──────────────────────────────────────────────┤
│ Customer signature      │ Company signature   │
├──────────────────────────────────────────────┤
│ INT-…-000482 · Page 1 of 1 · Hotline 16743   │  Footer
└──────────────────────────────────────────────┘
```

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Entity, BIN, branch, title | Title stacked BN over EN |
| Party block | Customer identity left, receipt metadata right | Labels stacked, values as entered |
| Device block | Type, brand, model, serial/IMEI, asset tag, ownership | Labels stacked; identifiers Latin script (`BL-04`) |
| Body | Reported fault, condition checklist, accessories, estimate expectation | Labels stacked, free text in the customer's language |
| Statutory block | Declarations and terms | **Parallel columns**, Bengali left, English right |
| Signature | Customer and company, plus witness where the customer cannot sign | Labels stacked |
| Machine-readable | QR: intake reference + device serial (`DT-044`) | Payload never translated |
| Footer | Reference, page n of m, hotline 16743 | English reference, bilingual caption |

| # | Rule |
|---|---|
| **L-02-a** | The condition checklist and the declarations block never split across a page. On the A4 multi-device variant they move whole (`VB-004` G-04) |
| **L-02-b** | Photographic evidence is **referenced by count and case ID**, not printed. Printed photographs on a branch printer are not evidence |
| **L-02-c** | The thermal queue-slip variant carries the reference, device identity and a QR only — it is **not** a substitute for the receipt and says so |

---

## 4. Field Mapping

### 4.1 Header and party

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Legal entity | প্রতিষ্ঠান | `MD-002.entity_legal_name` | Text | ✔ | |
| BIN | বিআইএন | `MD-002.bin` | Monospace | ✔ | |
| Branch | শাখা | `MD-003.branch_name` | Text | ✔ | |
| Receipt no. | রসিদ নং | `MD-040` sequence | Monospace | ✔ | |
| Date and time received | গ্রহণের তারিখ ও সময় | `service_order.intake_at` | `DD/MM/YYYY HH:mm` | ✔ | |
| Received by | গ্রহণকারী | `employee.display_name` + ID | Text | ✔ | |
| Customer name | গ্রাহকের নাম | `party.display_name` | Text | ✔ | |
| Mobile | মোবাইল | `party.mobile_primary` | `+880 1#########` | ✔ | |
| Alternate contact | বিকল্প যোগাযোগ | `party.mobile_alternate` | | | Where given |
| Address | ঠিকানা | `party.address` | Text | | Field collection: ✔ |
| NID / passport | এনআইডি / পাসপোর্ট | `party.national_id` | Monospace, masked | | **✔ where cash taken at intake exceeds BDT 50,000 (`BRU-FIN-02`)** |
| Corporate account | কর্পোরেট হিসাব | `contract.account_code` | Monospace | | Corporate variant |

### 4.2 Device

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Device type | ডিভাইসের ধরন | `MD-021.device_category` | Text | ✔ | |
| Brand | ব্র্যান্ড | `MD-021.make` | Text | ✔ | |
| Model | মডেল | `MD-021.model` | Text | ✔ | |
| Serial / IMEI | সিরিয়াল / আইএমইআই | `device.serial_no` | Monospace | ✔ | Where the device bears one |
| Serial not available | সিরিয়াল পাওয়া যায়নি | `device.serial_absent_reason` | Enum | | **✔ where serial is blank** |
| Asset tag | অ্যাসেট ট্যাগ | `device.asset_tag` | Monospace | | Corporate / rental |
| Ownership declared | মালিকানা ঘোষণা | `intake.ownership_declaration` | Enum: owner / authorised / other | ✔ | |
| Warranty status | ওয়ারেন্টি অবস্থা | `M09.warranty_state` | Enum | ✔ | |
| Purchase proof seen | ক্রয়ের প্রমাণ দেখা হয়েছে | `intake.purchase_proof_seen` | Bool | | Warranty intake: ✔ |

### 4.3 Condition, accessories and fault

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Reported fault | জানানো সমস্যা | `service_order.reported_fault` | Free text, customer's words | ✔ | |
| Fault category | সমস্যার শ্রেণি | `MD-024.symptom_code` | Code + label | ✔ | |
| Powers on | চালু হয় | `intake.condition.powers_on` | Enum: yes / no / not tested | ✔ | |
| Screen condition | স্ক্রিনের অবস্থা | `intake.condition.screen` | Enum from §6.1 | ✔ | |
| Body condition | বডির অবস্থা | `intake.condition.body` | Enum from §6.1 | ✔ | |
| Liquid-damage indicator | তরল ক্ষতির চিহ্ন | `intake.condition.lci` | Enum: clear / triggered / not visible | ✔ | Mobile / laptop |
| Previous repair evidence | পূর্ববর্তী মেরামতের চিহ্ন | `intake.condition.prior_repair` | Enum | ✔ | |
| Other observations | অন্যান্য পর্যবেক্ষণ | `intake.condition.remarks` | Free text | | |
| Photographs taken | তোলা ছবির সংখ্যা | `intake.photo_count` | Integer | ✔ | **Minimum per §6.1** |
| Accessories received | গৃহীত আনুষঙ্গিক | `intake.accessories[]` | Multi-select + count | ✔ | Blank prints "None" |
| SIM / memory card | সিম / মেমরি কার্ড | `intake.removable_media` | Enum: returned to customer / retained | ✔ | Mobile |
| Passcode provided | পাসকোড দেওয়া হয়েছে | `intake.access_note_given` | Bool | ✔ | **`BRU-SRM-20` consent required** |

### 4.4 Commercial expectation

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Service type | সেবার ধরন | `service_order.order_type` | Enum: warranty / paid / AMC / goodwill | ✔ | |
| Inspection fee | পরিদর্শন ফি | `MD-029` rate card | BDT, 2 dp | ✔ | Prints "None" where waived |
| Fee refundable if job proceeds | কাজ চললে ফি ফেরতযোগ্য | `MD-029.fee_refundable` | Bool | ✔ | |
| Indicative turnaround | সম্ভাব্য সময় | `MD-028.tat_target` | Text | ✔ | Marked **indicative** |
| Estimate will be issued | প্রাক্কলন দেওয়া হবে | Static | Text | ✔ | Paid jobs |
| Declared value | ঘোষিত মূল্য | `intake.declared_value` | BDT | | Field / courier intake: ✔ |

| # | Rule |
|---|---|
| **FM-02-a** | `Serial / IMEI` is required unless `serial_absent_reason` is recorded. A device with neither cannot be booked (`BRU-SRM-01`) |
| **FM-02-b** | The photograph minimum in §6.1 is enforced at capture, not at print. The document prints the **count**; the images live in `M24` |
| **FM-02-c** | `Reported fault` prints the customer's own words. The agent's interpretation goes in `Fault category`, never over the customer's text |
| **FM-02-d** | Accessories print as an explicit list. A blank accessories block prints **"None received / কিছুই গ্রহণ করা হয়নি"** — silence is not evidence |
| **FM-02-e** | `Passcode provided` may only be TRUE where the consent tick in §4.5 was captured (`BRU-SRM-20`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-01` | No intake receipt can issue without an identified device; the device is registered in `M17` as part of intake |
| `BRU-SRM-16` | The abandonment clause and its notice period print on every receipt. Without it, the 30-day abandonment process has no contractual foundation |
| `BRU-SRM-20` | Access notes are captured only with explicit consent, print as "provided / not provided" and are **purged at handover** — the value is never printed |
| `BRU-SEC-05` | The NID field prints masked (last four digits) on the customer copy; the full value exists only in `M33` |
| `BRU-LOG-01` | Courier intake requires a scan and identity capture from both parties; the receipt records both |
| `BRU-FSM-09` | A failed field collection produces a geotagged non-collection record, not an intake receipt |
| `TAX-01` (`MD-037`) | An inspection fee charged at intake is a taxable supply and requires a `DT-016` money receipt — the intake receipt is **not** a tax document |

### 5.1 What this document must never do

| # | Rule |
|---|---|
| **NV-01** | It is not a tax invoice and must not be mistaken for one. Any amount collected at intake is receipted separately on `DT-016` |
| **NV-02** | It never states a repair price. It states the inspection fee and that an estimate will follow (`DT-005`) |
| **NV-03** | It never records a passcode, pattern or unlock code in printed form |
| **NV-04** | It never disclaims liability for the company's own negligence — that wording is void and its presence undermines the enforceable clauses beside it. **Legal confirms at G6** |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Counter A5** | Branch walk-in, the default | Full document, wet or on-screen signature |
| **Thermal queue slip** | Busy branch, customer waits | Reference, device identity, QR, collection instruction only. Prints **"This is not the intake receipt"** and the full receipt is issued on the same visit |
| **Field / technician A5** | Device collected at the customer's premises | Adds GPS stamp and collection address; signature on the `P02` app |
| **Rider / courier** | `P09` pickup | Adds consignment reference, seal number and declared value; OTP acknowledgement replaces signature (`SG-04`) |
| **Corporate multi-device A4** | `P04` bulk drop | One header, a device schedule table of *n* rows, one authorised signature covering all rows; each row still carries its own intake reference |
| **Marketplace seller** | `P07` seller collects | Identical content, seller identity in a "collected by" block, plus the disclosure that 1000FiX remains responsible for the job (`BRU-ECM-03`) |
| **Data-recovery intake** | `M06` cases | Adds the restricted-handling notice, the chain-of-custody block and the `BRU-SEC-03` access statement |

### 6.1 The intake condition enumeration

No `MD` register holds intake condition. It is defined here because it is a **document-capture
vocabulary**, not master data reused elsewhere — and because printing a free-text condition is
how condition disputes are lost. `MD-026` supplies reason codes where a condition is contested;
`MD-024` supplies the symptom taxonomy for the fault, which is a different axis.

| Attribute | Permitted values | Photo minimum |
|---|---|---:|
| `powers_on` | `yes` · `no` · `not tested` · `intermittent` | — |
| `screen` | `intact` · `scratched` · `cracked` · `display fault` · `no screen` · `n/a` | 1 if not `intact` |
| `body` | `as new` · `light marks` · `heavy marks` · `dented` · `cracked` · `deformed` | 1 if not `as new` |
| `lci` (liquid-damage indicator) | `clear` · `triggered` · `not visible` · `n/a` | 1 if `triggered` |
| `prior_repair` | `none visible` · `visible` · `seals broken` · `non-original parts` | 1 if not `none visible` |
| `ports_buttons` | `all functional` · `partial` · `not tested` | — |
| `battery_swelling` | `none` · `suspected` · `confirmed` | 1 if not `none` |

| # | Rule |
|---|---|
| **CE-01** | **Four photographs minimum on every intake** — front, rear, and both sides — plus one per triggered condition above |
| **CE-02** | A device recorded as `not tested` on `powers_on` prints an explicit line: *"Device could not be powered on at intake. Condition below the surface is unknown."* |
| **CE-03** | `battery_swelling` = `confirmed` triggers the restricted-handling path (`BRU-LOG-05`) and the device does not travel by rider |
| **CE-04** | This enumeration is the same list used by `DT-004` findings and `DT-009` release, so that the three documents are directly comparable. Changing it here changes all three (`CM-R1`) |

### 6.2 Declarations and terms — the statutory block

The eight clauses below print on every variant, in parallel columns. Wording is indicative and
is **settled by Legal at G6**.

| # | Clause | Substance |
|---|---|---|
| **T-1** | Ownership | The customer declares they own the device or are authorised to hand it over |
| **T-2** | Condition | The condition recorded above is agreed as the condition at intake |
| **T-3** | Data backup | **The customer is responsible for backing up their data. Repair may result in data loss. 1000FiX does not guarantee data preservation unless a data-services engagement is separately agreed (`M06`)** |
| **T-4** | Access consent | Where a passcode is provided, it is used only to test and repair, is not recorded after handover, and is purged (`BRU-SRM-20`) |
| **T-5** | Estimate | No chargeable work begins without an approved estimate above the `BRU-SRM-07` threshold |
| **T-6** | Parts | Replaced parts are returned to the customer on request, except where a brand warranty claim requires their return to the brand |
| **T-7** | Collection and abandonment | Notice period, storage charge if any, and the consequence of non-collection — **period pending G6** |
| **T-8** | Limitation of liability | The company's maximum liability and its exclusions — **wording and enforceability pending G6** |

---

## 7. Worked Example

Specimen `RF-009 / DT-002-S1` — mobile handset, paid repair, branch intake, bilingual A5,
watermarked **SPECIMEN**, reserved sequence.

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-002-S1` | Handset, paid, branch counter | Base bilingual rendition, parallel-column statutory block |
| `DT-002-S2` | Laptop with no legible serial | `serial_absent_reason` path and `FM-02-a` |
| `DT-002-S3` | Corporate drop, 24 devices | A4 multi-device schedule; statutory block does not split at maximum rows (`WE-02`) |
| `DT-002-S4` | Data-recovery case | Restricted-handling and custody blocks |
| `DT-002-S5` | Rider pickup, OTP acknowledgement | Evidence set for `SG-04` |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Operations with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Branch Operations | *pending* | | |
| Reviewer — Data Services (`M06`) | *pending* | | |
| Reviewer — Localisation | *pending* | | |
| **G6 — external legal verification** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — COO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `INT-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `no_gaps` — an aborted intake is recorded as cancelled with a reason, never skipped (`SEQ-01`) |
| Reset | Fiscal year |
| Archive format | **PDF/A-3 with embedded fonts, at issue** (`R-02`) |
| Retention | `LG-009` — minimum the tax retention period; extended while the device is uncollected, a dispute is open, or a hold applies |
| Re-render | Prohibited. The archived rendition is served on every subsequent request (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged with user and reason (`RC-01`, `RC-03`) |

> **Abandonment dependency.** `BRU-SRM-16` starts a statutory notice process 30 days after
> `Ready`. That process cites this receipt's clause **T-7**. If the receipt was not issued, or
> T-7 did not print, the company **cannot lawfully dispose of the device** and carries the
> storage liability indefinitely. This is the single highest-value reason the document exists.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-003_Job_Card_and_Work_Order_Print.md`](DT-003_Job_Card_and_Work_Order_Print.md) | Carries the intake condition into the workshop |
| [`DT-004_Diagnostic_and_Condition_Report.md`](DT-004_Diagnostic_and_Condition_Report.md) | Findings measured against the condition recorded here |
| [`DT-005_Repair_Estimate_and_Quotation.md`](DT-005_Repair_Estimate_and_Quotation.md) | The estimate this receipt promises |
| [`DT-009_Device_Release_and_Collection_Receipt.md`](DT-009_Device_Release_and_Collection_Receipt.md) | **Closes the custody chain this document opens** |
| [`../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md`](../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) | Any money taken at intake |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Device tag applied at intake; QR payload |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | Device type, make and model |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | Fault categorisation |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Reason codes where a condition is contested |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full terms this document summarises |
| [`SP-007_SOP_Walk_In_Intake_and_Front_Desk.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md) | How a person completes it |
| `UI-037` Booking and Order Creation Flow Copy | The on-screen copy that captures these fields |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven intake variants, four-part field map, eight-clause statutory block, abandonment dependency stated | COO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Every mandated element listed in §2 with source and verification date
- [x] Field mapping resolves every printed field to a source (`FM-01`)
- [x] Business rules from `05-05` cited, not paraphrased
- [x] Variants enumerated with the difference stated
- [x] Numbering, retention and archive stated
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] **G6** legal verification of the abandonment notice period and the liability limitation — **outstanding, unwaivable (`WV-02`)**
- [ ] Bengali rendering tested on every supported branch and thermal printer model (`VB-004` BL-08) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
