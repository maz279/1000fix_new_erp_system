---
id: DT-038
title: Trade-In Offer and Acceptance Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Refurbishment with Legal & Compliance
author: Refurbishment with Legal & Compliance, Finance and Content Design
reviewers: [Legal Counsel, Finance, Data Services, Quality, Localisation Lead]
approver: Legal Counsel with Chief Commercial Officer
content_class: A
purpose: >
  Device assessment, the offer, any deduction applied, the ownership-transfer declaration and the
  data-erasure confirmation. A trade-in transfers ownership of a data-bearing device from a
  private individual to the company; the declaration protects the customer's data position and
  the company's title, and both are required before the device can be refurbished or resold.
traces_to: [M14, M06, M20, M17, DT-001, DT-002, DT-016, DT-034, DT-036, MD-021, MD-026, MD-029, MD-040, BRU-TRF-01, BRU-TRF-02, BRU-FIN-02, BRU-SEC-05]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: DT-038_TradeIn_Offer_and_Acceptance_Record_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-02 — provenance and identity checks, including stolen-device screening where available, must pass before a trade-in offer is paid
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-01 — no trade-in device proceeds to refurbishment or resale without a certified data destruction record
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-02 — cash receipts above BDT 50,000 require the customer's NID to be recorded
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-038 — Trade-In Offer and Acceptance Record

> ⚠ **Class A — statutory consequence.** Buying a used device from a member of the public is
> the point at which two risks meet: **title** (is it theirs to sell?) and **data** (is the
> previous owner's personal data now ours?).
>
> **`BRU-TRF-02`: provenance and identity checks pass before the offer is paid.**
> **`BRU-TRF-01`: no refurbishment or resale without a `DT-034` data destruction record.**
>
> A trade-in accepted without the first is potentially handling stolen goods. Accepted without the
> second, it is a personal-data breach in slow motion.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Trade-in assessment, offer and ownership transfer |
| Owning module | `M14` Trade-In, Refurbishment and Resale |
| Statutory | No prescribed form. **Class A** — title, identity verification and data protection |
| Recipient(s) | Customer, refurbishment operations, finance, data services, internal audit |
| Languages | **Bilingual — parallel columns for the declarations** |
| Output formats | A4 portrait · A5 counter variant · PDF · in-app offer (`P01`) |
| Numbering mask | `MD-040` — `TRD-{entity}-{branch}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **not less than the tax retention**, and longer where title is later questioned |

### 1.1 The sequence

```
Assessment  →  Offer (with validity)  →  Customer accepts
                                              ↓
              Identity + provenance check (BRU-TRF-02)  →  pass required
                                              ↓
              Ownership declaration signed  →  Payment / credit applied  →  DT-016 receipt
                                              ↓
              Device to data destruction (DT-034)  →  then DT-036 grading
```

| # | Rule |
|---|---|
| **TS-01** | **The offer is made before the identity check, but paid only after it.** Asking for identity documents before an offer exists reads as suspicion; paying before the check is the actual risk |
| **TS-02** | The device does not enter refurbishment stock until the declaration is signed and payment is made |
| **TS-03** | Data destruction (`DT-034`) happens **before** grading (`DT-036`), not after. A device in the grading queue with live customer data is the failure mode this ordering prevents |

---

## 2. Statutory Requirements

Not a prescribed form. Five constraints:

| Constraint | Source | Effect |
|---|---|---|
| Title and provenance | Contract; criminal law on handling — **pending G6** | Buying stolen goods carries consequences regardless of good faith |
| Identity verification | `BRU-TRF-02`; `BRU-FIN-02` for cash | Identity of the seller is recorded |
| Data protection | `LG-008`, `05-06` NFR-086 | The previous owner's data becomes our responsibility on transfer |
| Consumer fairness in the offer | Consumer Rights Protection Act 2009 — **pending G6** | Deductions must be explained, not merely applied |
| Cash-transaction thresholds | `BRU-FIN-02` | NID for cash above BDT 50,000 |

### 2.1 G6 questions

| # | Question |
|---|---|
| **TI1** | What identity verification is required or advisable when purchasing used goods from the public? |
| **TI2** | Are there record-keeping or reporting obligations for second-hand purchases? |
| **TI3** | What is our position if a device later proves to be stolen — what does a documented check protect? |
| **TI4** | Does the transfer of a data-bearing device create any specific obligation to the previous owner? |
| **TI5** | Is any registration required to deal in second-hand electronic goods? |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Record number, date, **offer validity**, branch | Title stacked |
| Party block | Customer identity and verification left; assessor and branch right | Labels stacked |
| Body | Device identity → assessment → offer calculation → deductions → payment method | Labels stacked |
| Totals | Base offer, deductions itemised, **net offer** | Arabic numerals |
| Statutory block | **Ownership declaration and data-erasure confirmation** | **Parallel columns** |
| Signature | Customer and assessor; witness where the customer cannot sign | Labels stacked |
| Footer | Record reference, `page n of m`, hotline | English |

| # | Rule |
|---|---|
| **L-38-a** | Deductions are **itemised with reasons**, never netted into a single lower figure. A customer who sees "offer: 8,000" after being told "up to 12,000" without explanation will not trade in again |
| **L-38-b** | The declarations block is the most prominent body element and never splits |
| **L-38-c** | Offer validity prints in the header. An assessment ages; device values move |
| **L-38-d** | The data-erasure confirmation states plainly **what the customer must do** (remove accounts, sign out, back up) and what we will do (`DT-034`) |
| **L-38-e** | Identity document references print **masked**; the full value lives in `M33` (`BRU-SEC-05`) |

---

## 4. Field Mapping

### 4.1 Customer, identity and provenance

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Record no. | রেকর্ড নং | `MD-040` sequence | Monospace | ✔ |
| Date and time | তারিখ ও সময় | `tradein.assessed_at` | `DD/MM/YYYY HH:mm` | ✔ |
| **Offer valid until** | প্রস্তাবের মেয়াদ | `tradein.offer_valid_to` | `DD/MM/YYYY` | ✔ |
| Customer name | গ্রাহকের নাম | `party.display_name` | Text | ✔ |
| Mobile | মোবাইল | `party.mobile_primary` | Masked | ✔ |
| Address | ঠিকানা | `party.address` | Text | ✔ |
| **Identity document** | পরিচয়পত্র | `party.id_type` + masked number | Enum + monospace | ✔ **`BRU-TRF-02`** |
| Identity verified by | যাচাইকারী | `employee.display_name` + ID | Text | ✔ |
| **Provenance check result** | উৎস যাচাইয়ের ফল | `BRU-TRF-02` screening | Enum: pass / fail / unavailable | ✔ |
| Screening reference | যাচাই সূত্র | Screening record | Monospace | ✔ where performed |
| Purchase proof shown | ক্রয়ের প্রমাণ | `tradein.purchase_proof` | Enum + reference | ✔ where available |
| NID recorded | এনআইডি সংরক্ষিত | `party.national_id` masked | Monospace | **✔ cash > BDT 50,000** |

### 4.2 Device, assessment and offer

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Make / model | মেক / মডেল | `MD-021` | Text | ✔ |
| **Serial / IMEI** | সিরিয়াল | `device.serial_no` | Monospace | ✔ |
| Storage / variant | স্টোরেজ / ভ্যারিয়েন্ট | `MD-021.variant` | Text | ✔ |
| Accessories included | আনুষঙ্গিক | `tradein.accessories[]` | List | ✔ |
| Cosmetic condition | বাহ্যিক অবস্থা | `DT-002` §6.1 attributes | Enum per attribute | ✔ |
| Functional test result | কার্যকারিতা | `MD-025` test codes | Pass/fail per test | ✔ |
| Battery health | ব্যাটারির স্বাস্থ্য | Measured | %, integer | ✔ where applicable |
| Activation lock / account lock | অ্যাকাউন্ট লক | `tradein.lock_status` | Enum: clear / locked | ✔ **blocks purchase if locked** |
| Provisional grade | সাময়িক গ্রেড | `DT-036` grade scale | A–F | ✔ |
| **Base offer** | মূল প্রস্তাব | `MD-029` trade-in matrix | BDT, 2 dp | ✔ |
| Deduction — reason and amount | কর্তন — কারণ ও পরিমাণ | `MD-026` + amount | Code, text, BDT | ✔ per deduction |
| **Net offer** | নিট প্রস্তাব | Computed | BDT, 2 dp, largest type | ✔ |
| Offer basis | প্রস্তাবের ভিত্তি | `MD-029` matrix version | Version reference | ✔ |
| Payment method | পরিশোধের পদ্ধতি | Enum: cash / MFS / bank / **credit against purchase** | ✔ |
| Applied against purchase | ক্রয়ের বিপরীতে | `DT-010` reference | Monospace | Where credited |
| Receipt reference | রসিদ সূত্র | `DT-016` reference | Monospace | ✔ where paid |

### 4.3 Declarations

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| **Ownership declaration** | মালিকানার ঘোষণা | Static approved text | Text | ✔ |
| Free of encumbrance | দায়মুক্ত | Static | Text | ✔ |
| **Data-erasure confirmation** | ডেটা মুছে ফেলার নিশ্চয়তা | Static + customer action list | Text | ✔ |
| Accounts signed out | অ্যাকাউন্ট সাইন-আউট | `tradein.accounts_cleared` | Bool | ✔ |
| Backup taken by customer | ব্যাকআপ নেওয়া হয়েছে | `tradein.backup_confirmed` | Bool | ✔ |
| Our destruction undertaking | আমাদের অঙ্গীকার | Static + `DT-034` | Text | ✔ |
| Irrevocability | অপরিবর্তনীয়তা | Static, per G6 | Text | ✔ |
| Customer signature | গ্রাহকের স্বাক্ষর | Signature / OTP | ✔ | ✔ |
| Assessor signature | মূল্যায়নকারীর স্বাক্ষর | `employee` | ✔ | ✔ |

| # | Rule |
|---|---|
| **FM-38-a** | **A locked device is not purchased.** An activation-locked device cannot be sanitised, refurbished or resold, and buying one transfers a worthless asset for real money |
| **FM-38-b** | Payment is released only after the provenance check passes (`TS-01`, `BRU-TRF-02`) |
| **FM-38-c** | Every deduction carries a reason code and an amount. Deduction distribution by assessor is reported — **a single assessor deducting far more than peers is either stricter or negotiating** |
| **FM-38-d** | The offer basis references the `MD-029` matrix version, so an offer can be explained months later |
| **FM-38-e** | Identity references print masked (`BRU-SEC-05`) |
| **FM-38-f** | The record links forward to `DT-034` and then `DT-036`. A trade-in with no downstream destruction record is an exception reported daily |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-TRF-01` | Data destruction before refurbishment or resale |
| `BRU-TRF-02` | Provenance and identity checks before payment |
| `BRU-FIN-02` | NID for cash above BDT 50,000 |
| `BRU-SEC-05` | Personal data minimised and masked on the printed record |
| `BRU-BIL-05` | Where a trade-in credit is later reversed, it follows the refund rules |
| `BRU-DMS-03` | A signed record is not modified |

### 5.1 What a documented check protects

| # | Rule |
|---|---|
| **PC-38-a** | Identity captured, verified and retained, per **G6 TI1** |
| **PC-38-b** | Serial screened against available stolen-device sources where one exists; the result and its timestamp are recorded, including `unavailable` |
| **PC-38-c** | `unavailable` is recorded as such, never as `pass`. **A check that did not happen must not look like a check that passed** |
| **PC-38-d** | A `fail` blocks purchase and follows the escalation in `SP-025`, which is a Legal and Security matter, not a commercial one |
| **PC-38-e** | Serials of purchased devices are retained and searchable, so a later enquiry can be answered |
| **PC-38-f** | Trade-in volume by customer is monitored. **A single individual trading in devices at volume is a pattern, whatever the explanation** |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Counter trade-in** | Branch walk-in | The base A4/A5 record |
| **In-app offer** | `P01` self-assessment | Provisional offer subject to physical assessment; the difference is explained on arrival |
| **Trade-in against purchase** | Credit applied to a new device | Credit reference and the resulting `DT-010` linkage |
| **Corporate bulk buy-back** | Estate refresh (`P04`) | Asset schedule, one declaration by an authorised signatory, per-asset `DT-034` |
| **Declined at assessment** | Offer refused or device rejected | Records the reason and returns the device; no ownership transfer |
| **Offer expired** | Customer returns after validity | Re-assessed; a new record, never an extension |
| **Non-viable device** | Assessed as e-waste only | Zero or nominal offer; consent to disposal recorded; routes to `DT-035` |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-038-S1` | Handset, BDT 14,500 net after 3 deductions | Base bilingual record and itemised deductions |
| `DT-038-S2` | Activation-locked device | `FM-38-a` refusal |
| `DT-038-S3` | Screening unavailable | `PC-38-c` honest recording |
| `DT-038-S4` | Cash payment BDT 62,000 | `BRU-FIN-02` NID capture |
| `DT-038-S5` | Corporate bulk buy-back, 40 devices | Schedule variant with per-asset `DT-034` |
| `DT-038-S6` | Trade-in credited against a new purchase | Credit and invoice linkage |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Refurbishment with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Data Services | *pending* | | |
| Reviewer — Quality | *pending* | | |
| **Legal Counsel — declarations and TI1–TI5** | *pending* | | **Required** |
| Approver — Legal Counsel with CCO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `TRD-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `gaps_recorded`; a declined assessment retains its number with a reason |
| Archive format | **PDF/A-3 at execution** |
| Retention | `LG-009`; **not less than the tax retention**, and longer where title is questioned or `G6 TI2` requires |
| Identity data | Retained per `LG-009` with access restricted; masked on every printed rendition |
| Serial index | Purchased-device serials retained and searchable for the retention period (`PC-38-e`) |
| Re-render | Prohibited |
| Reprint | Watermarked **COPY**, logged |
| Chain | `DT-038` → `DT-034` → `DT-036` (or `DT-035`) retrievable as one chain per device |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-034_Data_Destruction_Certificate.md`](DT-034_Data_Destruction_Certificate.md) | **Mandatory next step (`BRU-TRF-01`)** |
| [`DT-036_Refurbishment_Grading_and_Certification_Record.md`](DT-036_Refurbishment_Grading_and_Certification_Record.md) | Where a viable device goes after destruction |
| [`DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | Where a non-viable device goes |
| [`../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md`](../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) | Payment of the offer |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | Where the credit is applied to a purchase |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | §6.1 condition enumeration reused |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | The trade-in valuation matrix |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full terms |
| [`SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | The process, including `PC-38-d` escalation |
| `UI-017` P07 Marketplace Seller Portal UI Copy Pack | In-app offer journey |
| `RP-002` Report Catalogue by Role and Module | Deduction and volume-pattern reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Offer-before-check-payment-after sequencing, locked-device refusal, itemised deductions with reporting, honest recording of unavailable screening, six provenance rules, forward chain to `DT-034`/`DT-036` | Legal Counsel with CCO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Payment gated on the provenance check (`FM-38-b`)
- [x] Locked devices refused, with the reason stated (`FM-38-a`)
- [x] `unavailable` screening recorded honestly (`PC-38-c`)
- [x] Deductions itemised with reason codes and monitored
- [x] All internal links resolve
- [ ] **Legal Counsel approval of the ownership and data declarations (TI1–TI5)** — **outstanding**
- [ ] Stolen-device screening source identified and integrated, or its absence formally accepted — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Trade-in valuation matrix published in `MD-029` and versioned — **outstanding, dependency**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
