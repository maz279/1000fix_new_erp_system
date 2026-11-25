---
id: DT-037
title: Rental Agreement and Asset Handover Record
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Rental with Legal & Compliance
author: Rental with Legal & Compliance, Finance and Content Design
reviewers: [Legal Counsel, Finance, Quality, Logistics, Localisation Lead]
approver: Legal Counsel with Chief Commercial Officer
content_class: B
purpose: >
  Rental terms, asset identity and condition, deposit, liability and the return-condition standard.
  Equipment-as-a-Service places company assets in customer hands; the handover record is the basis
  on which they are recovered and on which damage is charged. A rental agreement without a
  condition report is an asset the company has given away with paperwork.
traces_to: [M13, M45, M20, M49, DT-001, DT-008, DT-019, DT-027, DT-028, DT-032, MD-021, MD-029, MD-040, MD-044, BRU-RNT-01, BRU-RNT-02, BRU-RNT-03, BRU-RNT-04, BRU-RNT-05]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: DT-037_Rental_Agreement_and_Asset_Handover_Record_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-RNT-01 — a rental asset cannot be dispatched without a completed pre-dispatch condition report
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-RNT-02 — a rental agreement requires a signed condition report and the deposit received before handover
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-RNT-03 — damage charges derive from the difference between outbound and inbound condition reports; discretionary charges require approval
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-037 — Rental Agreement and Asset Handover Record

> ⚠ **Class B — legal.** Two documents that must never be separated: the **agreement** (terms,
> deposit, liability) and the **handover record** (asset identity and condition at each end).
>
> **`BRU-RNT-03`: damage charges derive from the difference between the outbound and inbound
> condition reports.** No outbound report, no chargeable difference. That single rule is why the
> handover record is not optional paperwork.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Rental agreement + asset condition handover record |
| Owning module | `M13` Rental and Equipment-as-a-Service, with `M45` Enterprise Asset |
| Statutory | No — **legally binding**; asset recovery and damage charges depend on it |
| Recipient(s) | Customer, rental operations, finance, logistics, asset register |
| Languages | **Bilingual — separate pages for the agreement, stacked labels on the handover record** |
| Output formats | A4 portrait (agreement) · A4 or A5 (handover record, travels with the asset) · PDF · e-signature (`M24`) |
| Numbering mask | `MD-040` — `RNT-{entity}-{yy}-{seq:06d}` agreement; handover records suffix `/OUT` and `/IN` |
| Retention period | `LG-009`; **rental term plus the limitation period**, and while any charge remains disputed |

### 1.1 The lifecycle

```
Agreement signed  →  Deposit received  →  OUT condition report  →  Handover
                                                                      │
                                            (rental period, charges accrue)
                                                                      ↓
Return  →  IN condition report  →  Difference assessed  →  Damage charge or deposit release
                                                                      ↓
                                   Cleaning, service, functional test  →  Back to pool
```

| Gate | Rule |
|---|---|
| Deposit **and** signed condition report before handover | `BRU-RNT-02` |
| Pre-dispatch condition report before dispatch | `BRU-RNT-01` |
| Damage charge from the OUT/IN difference only | `BRU-RNT-03` |
| Asset returns to the pool only after cleaning, servicing and functional test | `BRU-RNT-04` |
| Overdue rentals accrue charges automatically per tariff | `BRU-RNT-05` |

---

## 2. Statutory Requirements

Not statutory. Five constraints:

| Constraint | Source | Effect |
|---|---|---|
| Enforceability of deposit forfeiture and damage charges | Contract Act; consumer protection — **pending G6** | A charge that reads as a penalty may be unenforceable |
| Title retention | Contract Act — **pending G6** | The asset remains ours throughout; the agreement must say so unambiguously |
| Consumer protection where the hirer is a consumer | Consumer Rights Protection Act 2009 — **pending G6** | Consumer hire carries protections |
| Insurance and liability allocation | Contract; insurer terms | Who bears loss, theft and third-party liability must be explicit |
| Data on returned assets | `LG-008`, `DT-034` | A returned data-bearing asset is sanitised before re-hire |

### 2.1 G6 questions

| # | Question |
|---|---|
| **RN1** | Is our deposit forfeiture and damage-charge mechanism enforceable, particularly against consumers? |
| **RN2** | What must the agreement state to preserve our title against a hirer's creditors? |
| **RN3** | Is equipment hire to consumers a regulated activity in any respect? |
| **RN4** | What is the position on charging for loss or non-return, and at what value — replacement, book, or market? |
| **RN5** | Does stamp duty apply to hire agreements? |

---

## 3. Layout

**Two documents, issued together, separately signed.**

| Part | Zone | Content | Bilingual |
|---|---|---|---|
| **Agreement** | Header | Agreement reference, hirer, term, asset summary | Title stacked |
| | Body | Terms: title, use, care, liability, insurance, deposit, charges, overdue, return, termination | **Separate pages** per language |
| | Statutory block | Signature page with precedence clause | Both present |
| **Handover record** | Header | Agreement reference + `/OUT` or `/IN`, date, direction | Title stacked |
| | Body | Asset identity, accessories, condition per attribute, meter readings, photographs, functional test | Labels stacked |
| | Signature | Both parties at each handover | Labels stacked |

| # | Rule |
|---|---|
| **L-37-a** | The **OUT and IN records use the identical attribute set**, so the difference is computable rather than argued (`BRU-RNT-03`) |
| **L-37-b** | Photographs are mandatory at both ends, with a stated minimum, and are referenced by count and case ID |
| **L-37-c** | The deposit amount, its conditions and its release timetable print on the agreement **and** on the OUT record. A hirer should not have to find the agreement to know their deposit position |
| **L-37-d** | Meter or usage readings — hours, cycles, kilometres — print where the asset has them, because charges may depend on them |
| **L-37-e** | The IN record prints the OUT values alongside, so the difference is visible to the customer at the moment of return, not in a later invoice |

---

## 4. Field Mapping

### 4.1 Agreement

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Agreement reference | চুক্তি সূত্র | `MD-040` sequence | Monospace | ✔ |
| Hirer name and identity | ভাড়াগ্রহীতা | `party` / `MD-015` | Text | ✔ |
| Hirer NID / registration | এনআইডি / নিবন্ধন | `party.national_id` / `.registration` | Monospace | ✔ |
| Hirer address and contact | ঠিকানা | `party` | Text | ✔ |
| Asset — make, model, serial | সম্পদ | `MD-021`, `MD-045`/`M45` | Text + monospace | ✔ |
| Asset tag | অ্যাসেট ট্যাগ | `asset.asset_tag` | Monospace | ✔ |
| Rental start / end | শুরু / শেষ | `rental.start_date`, `.end_date` | `DD/MM/YYYY` | ✔ |
| Tariff | ভাড়ার হার | `MD-029` rental rate card | BDT per period | ✔ |
| Billing frequency | বিলিং চক্র | `MD-033` | Enum | ✔ |
| **Deposit amount** | জামানত | `rental.deposit_amount` | BDT, 2 dp | ✔ |
| Deposit received | জামানত গৃহীত | `DT-016` reference | Monospace | ✔ **`BRU-RNT-02`** |
| Deposit release conditions | জামানত ফেরতের শর্ত | Terms | Text | ✔ |
| **Overdue charge** | বিলম্ব চার্জ | `MD-029` tariff | BDT per period | ✔ **`BRU-RNT-05`** |
| Loss / non-return charge | হারানোর চার্জ | Per **G6 RN4** | BDT basis | ✔ |
| Insurance responsibility | বিমার দায়িত্ব | Terms | Text | ✔ |
| Permitted use and location | অনুমোদিত ব্যবহার | Terms | Text | ✔ |
| Title statement | মালিকানার বিবৃতি | Static, per **G6 RN2** | Text | ✔ |
| Termination and recovery | সমাপ্তি ও পুনরুদ্ধার | Terms | Text | ✔ |
| Language precedence | ভাষার প্রাধান্য | Per `CG-010` §4.1 | Text | ✔ |

### 4.2 Handover record — OUT and IN

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Direction | দিক | `handover.direction` | OUT / IN | ✔ |
| Date and time | তারিখ ও সময় | `handover.at` | `DD/MM/YYYY HH:mm` | ✔ |
| Location | স্থান | `MD-003` or customer address | Text | ✔ |
| Handed over / received by | হস্তান্তর / গ্রহণ | `employee` + `party` names and IDs | Text | ✔ |
| Asset serial verified by scan | স্ক্যানে যাচাই | `handover.scan_ref` | Monospace | ✔ |
| Accessories | আনুষঙ্গিক | `handover.accessories[]` | Checklist | ✔ |
| **Condition per attribute** | অবস্থা | `DT-002` §6.1 set + asset-specific | Enum per attribute | ✔ |
| Cosmetic damage | বাহ্যিক ক্ষতি | `handover.damage[]` numbered | Numbered list + photo | ✔ (prints "None") |
| Functional test result | কার্যকারিতা পরীক্ষা | `MD-025` test codes | Pass/fail per test | ✔ |
| Meter / usage reading | মিটার পাঠ | `handover.meter_reading` | Number + unit | ✔ where metered |
| Consumables level | ভোগ্যপণ্যের মাত্রা | `handover.consumables` | Text | Where applicable |
| Photographs | ছবি | `M24` count | Integer | ✔ **minimum per `L-37-b`** |
| Data-bearing | ডেটা ধারণকারী | `asset.data_bearing` | Bool | ✔ |
| Data destruction on return | ফেরতে ডেটা ধ্বংস | `DT-034` reference | Monospace | **✔ IN, where data-bearing** |
| **Difference from OUT** | আউট থেকে পার্থক্য | Computed | Table | ✔ **IN only** |
| Damage charge assessed | ক্ষতির চার্জ | Computed + `MD-029` | BDT, 2 dp | ✔ IN, where any |
| Discretionary charge | বিবেচনামূলক চার্জ | `rental.discretionary_charge` | BDT + approver | **✔ approval required (`BRU-RNT-03`)** |
| Deposit disposition | জামানতের গতি | Enum: released / partially applied / retained | ✔ IN |
| Both-party signature | উভয় পক্ষের স্বাক্ষর | Signature or OTP | ✔ | ✔ |

| # | Rule |
|---|---|
| **FM-37-a** | The asset **cannot dispatch** without a completed OUT condition report (`BRU-RNT-01`) and a received deposit (`BRU-RNT-02`) |
| **FM-37-b** | Damage charges are computed from the OUT/IN difference. A charge with no corresponding difference is discretionary and requires approval (`BRU-RNT-03`) |
| **FM-37-c** | Fair wear and tear is defined in the agreement per asset class and is **excluded** from damage charges. Undefined fair wear is a dispute in every return |
| **FM-37-d** | A data-bearing asset returning requires `DT-034` before re-hire (`LG-008`) |
| **FM-37-e** | The asset re-enters the available pool only after cleaning, servicing and functional test (`BRU-RNT-04`) — recorded on the IN record or a linked `DT-008` |
| **FM-37-f** | Overdue charges accrue automatically per tariff with escalating notification (`BRU-RNT-05`); the agreement states the rate so the accrual is not a surprise |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-RNT-01` | Pre-dispatch condition report mandatory |
| `BRU-RNT-02` | Signed condition report and deposit before handover |
| `BRU-RNT-03` | Damage charges from the OUT/IN difference; discretionary charges approved |
| `BRU-RNT-04` | Return to pool only after cleaning, servicing and functional test |
| `BRU-RNT-05` | Automatic overdue accrual with escalating notification |
| `BRU-LOG-01` | Scan and identity capture at each custody transfer |
| `BRU-DMS-03` | A signed agreement is not modified; a change is an amendment |

### 5.1 Asset recovery

The scenario the agreement is actually written for.

| # | Rule |
|---|---|
| **AR-37-a** | Overdue triggers the notification ladder before it triggers recovery (`BRU-RNT-05`, `NT-004`) |
| **AR-37-b** | Recovery follows the agreement's stated process. **A recovery outside the agreed process is a legal exposure, whatever the provocation** |
| **AR-37-c** | Loss or non-return is charged on the basis stated in the agreement (**G6 RN4**), not on a figure decided at the time |
| **AR-37-d** | An unrecovered asset is written off only with Finance approval and a documented recovery history (`DT-029` discipline) |
| **AR-37-e** | Assets are tracked in `M45` throughout; a rental asset with no recorded location is an asset in the process of being lost |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Consumer short-term hire** | Individual hirer | Plainer terms, tighter consumer protections, NID captured |
| **Corporate equipment-as-a-service** | `M13` contracted service | Multi-asset schedule, contract-linked billing, delegation from `MD-015` |
| **Loan / courtesy device** | Device provided while a repair is in progress | Zero tariff, deposit may be waived, but the **condition record is identical** |
| **Demo / trial** | Evaluation placement | Fixed short term, no auto-extension, sales-owned |
| **Subscription hardware** | `M39` hardware bundled with a subscription | Terms reference the subscription; return obligations on cancellation stated |
| **Extension** | Term extended | Amendment referencing the original; no new OUT record unless the asset was returned |
| **Swap** | Asset replaced mid-term | IN record for the old, OUT record for the new, one agreement |

> **The loan-device variant is the one that leaks assets.** A courtesy device given without a
> condition record and a return date is a device the company will not see again. The zero tariff
> is not a reason to skip the record.

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-037-S1` | Corporate equipment hire, 3-month term | Agreement plus OUT record |
| `DT-037-S2` | Return with two new damages | `L-37-e` OUT/IN comparison and charge derivation |
| `DT-037-S3` | Data-bearing asset returned | `FM-37-d` `DT-034` linkage |
| `DT-037-S4` | Overdue by 12 days | `BRU-RNT-05` accrual and notification ladder |
| `DT-037-S5` | Courtesy loan device | Zero-tariff variant with a full condition record |
| `DT-037-S6` | Discretionary charge applied | `BRU-RNT-03` approval |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Rental with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Finance (deposit and write-off) | *pending* | | |
| Reviewer — Quality (return-to-pool test) | *pending* | | |
| Reviewer — Logistics | *pending* | | |
| **Legal Counsel — terms, deposit and recovery (RN1–RN5)** | *pending* | | **Required** |
| Approver — Legal Counsel with CCO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `RNT-{entity}-{yy}-{seq:06d}`; handover records suffix `/OUT`, `/IN`, `/IN-2` for swaps |
| Gap policy | `gaps_recorded` |
| Archive format | **PDF/A-3 at execution** for the agreement; PDF/A-3 for both handover records |
| Retention | `LG-009`; **rental term plus the limitation period**, extended while any charge is disputed |
| Pairing | **The agreement, the OUT record and the IN record are archived as one set.** An IN record without its OUT is evidentially useless |
| Re-render | Prohibited |
| Reprint | Watermarked **COPY**, logged |
| Photographs | Retained with the records for the same period, at the resolution captured |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-030_Contract_and_AMC_Agreement_Template_Set.md`](DT-030_Contract_and_AMC_Agreement_Template_Set.md) | Where hire sits inside a service contract |
| [`DT-034_Data_Destruction_Certificate.md`](DT-034_Data_Destruction_Certificate.md) | Data-bearing assets on return |
| [`DT-032_Warranty_Certificate_and_Extension_Document.md`](DT-032_Warranty_Certificate_and_Extension_Document.md) | Cover on hired assets |
| [`../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md`](../05A_Service_and_Operations/DT-008_Quality_Checklist_Record.md) | Return-to-pool test (`BRU-RNT-04`) |
| [`../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md`](../05B_Finance_and_Statutory/DT-016_Payment_Receipt_and_Money_Receipt.md) | Deposit receipt |
| [`../05B_Finance_and_Statutory/DT-019_Proforma_Invoice_and_Advance_Request.md`](../05B_Finance_and_Statutory/DT-019_Proforma_Invoice_and_Advance_Request.md) | Deposit request |
| [`../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md`](../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md) | Asset movement |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md) | Asset classes and book values |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full terms |
| [`SP-027_SOP_Rental_and_Equipment_as_a_Service.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-027_SOP_Rental_and_Equipment_as_a_Service.md) | The operational process |
| [`NT-004_SMS_Template_Library_Customer.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | Overdue and return reminders |
| `RP-002` Report Catalogue by Role and Module | Asset utilisation and loss reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Agreement plus paired OUT/IN handover records with an identical attribute set, deposit position printed on both, fair-wear definition requirement, five asset-recovery rules, and the courtesy-loan leakage warning | Legal Counsel with CCO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] OUT and IN records use an identical attribute set so the difference is computable (`L-37-a`)
- [x] Deposit position printed on both agreement and handover record
- [x] Fair wear and tear required to be defined per asset class (`FM-37-c`)
- [x] Courtesy-loan variant given the same condition discipline
- [x] All internal links resolve
- [ ] **Legal Counsel approval of terms, deposit forfeiture and recovery process (RN1–RN5)** — **outstanding**
- [ ] Fair-wear definitions authored per asset class with Quality — **outstanding; blocks first return assessment**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Loss/non-return charge basis decided (G6 RN4) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
