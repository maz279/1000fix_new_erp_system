---
id: DT-005
title: Repair Estimate and Quotation
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Commercial with Operations
author: Commercial with Operations, Finance and Content Design
reviewers: [Finance, Tax, Legal & Compliance, Operations, Localisation Lead, Platform Engineering]
approver: Chief Commercial Officer with Legal Counsel
content_class: A
purpose: >
  The itemised offer the customer approves before chargeable work begins — parts, labour, taxes,
  validity, terms and the approval capture block. Estimates above BDT 5,000 require documented
  customer approval under BRU-SRM-07; this document is that evidence. Work performed without it
  is unbillable and, in a dispute, indefensible.
traces_to: [M36, M01, M11, M20, DT-001, DT-004, DT-006, DT-010, MD-029, MD-030, MD-037, MD-039, MD-040, BRU-SRM-07, BRU-SRM-08, BRU-SRM-13, 05-05 BRU-SRM-07]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-005_Repair_Estimate_and_Quotation_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-07 — repair estimates above BDT 5,000 require documented customer approval before work begins
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-08 — estimates above BDT 25,000 require customer approval and branch manager approval
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-13 — an estimate expires at its stated validity; expired estimates require re-issue, not extension
    verified: 2026-08-15
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037 — VAT rate derivation and Mushak mapping; all rates pending G6
    verified: 2026-08-15
    class: P1
  - source: Consumer Rights Protection Act 2009 — price disclosure and prohibition on charging above a quoted price — **to be verified against the enacted text at G6**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-005 — Repair Estimate and Quotation

> ⚠ **Class A — statutory consequence.** An estimate is a **priced offer**. Once accepted it
> constrains what the company may charge, and consumer-protection law limits charging above a
> quoted price. The tax shown on it must be the tax that appears on the resulting `DT-010`.
>
> **`BRU-SRM-07`: above BDT 5,000, no chargeable work begins without this document approved.**
> **`BRU-SRM-08`: above BDT 25,000, branch manager approval as well.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Priced offer / quotation |
| Owning module | `M36` Quotation, Estimation and Tender Management, with `M01` |
| Statutory | **Yes** — consumer price-disclosure consequence; VAT presentation must reconcile to `DT-010`. Instrument confirmed at **G6** |
| Recipient(s) | Customer (original), branch file, `P01`/`P04` portal, technician via `DT-003` |
| Languages | **Bilingual — stacked labels, parallel columns for terms** |
| Output formats | A4 portrait · PDF for portal and email · SMS/WhatsApp summary with an approval link (`NT-004`, `NT-008`) |
| Numbering mask | `MD-040` — `EST-{entity}-{branch}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; not less than the retention of the invoice it becomes |

### 1.1 Approval thresholds

| Estimate total (incl. VAT) | Customer approval | Internal approval | Evidence |
|---|:--:|---|---|
| Up to BDT 5,000 | Recommended | — | Recorded if given |
| **Above BDT 5,000** | **Mandatory (`BRU-SRM-07`)** | — | Signature, portal action, OTP or recorded verbal with reference |
| **Above BDT 25,000** | **Mandatory (`BRU-SRM-08`)** | **Branch manager** | Both recorded before work starts |
| Corporate contract customers | Per `MD-032` contract terms | Per the contract's delegation matrix | `P04` approval trail |

> **The threshold is on the estimate, not the invoice.** An estimate of BDT 4,900 that becomes
> an invoice of BDT 6,200 has bypassed `BRU-SRM-07`. That path is closed by `DT-006`, which
> requires re-approval of any variation.

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Clear statement of price before service | Consumer Rights Protection Act 2009 — **pending G6** | 2026-08-15 (unverified) | Whole document |
| Prohibition on charging above the quoted price | Consumer Rights Protection Act 2009 — **pending G6** | 2026-08-15 (unverified) | §6.2 term Q-3 |
| VAT shown separately at the applicable rate | VAT & SD Act 2012; `MD-037` | 2026-08-15 (rate pending G6) | Totals block |
| Supplier identity with BIN | VAT & SD Act 2012 — **pending G6** | 2026-08-15 (unverified) | Header |
| Validity period stated | `BRU-SRM-13` | 2026-08-15 | Header and §6.2 term Q-2 |

> **G6 instruction.** Tax adviser confirms (a) the VAT rate applicable to each service category
> in `MD-019`, (b) whether an accepted estimate creates a tax point, and (c) whether an estimate
> must carry any prescribed wording distinguishing it from a Mushak 6.3. Legal Counsel confirms
> the consumer-protection price-disclosure obligation and the enforceability of term Q-3.

### 2.1 What this document is not

| # | Rule |
|---|---|
| **NT-05-a** | **An estimate is not a tax invoice.** It prints **"This is not a VAT invoice / এটি ভ্যাট চালান নয়"** in the totals block. Only `DT-010` is |
| **NT-05-b** | It never consumes a Mushak sequence number |
| **NT-05-c** | Where a customer needs a document to raise a payment, that is `DT-019` proforma invoice, not this |

---

## 3. Layout

**Primary format: A4 portrait**, geometry per `VB-004` §4.

```
┌──────────────────────────────────────────────────┐
│ [LOGO]     REPAIR ESTIMATE / মেরামত প্রাক্কলন       │  Header
│ 1000FiX Services Limited · BIN ############      │
│ Estimate EST-…-004417 · Valid to 22/08/2026      │
├───────────────────────────┬──────────────────────┤
│ CUSTOMER                  │ DEVICE & JOB         │
│ Name · Mobile · Address   │ Brand · Model        │
│ BIN/TIN (corporate)       │ Serial · SR ref      │
│                           │ Diagnostic DIA-…     │
├───────────────────────────┴──────────────────────┤
│ WHY THIS WORK IS NEEDED — findings F1…Fn         │
├──────────────────────────────────────────────────┤
│ LINE ITEMS                                       │
│ # │Finding│Description│Qty│Rate│Disc│VAT│Amount │
├──────────────────────────────────────────────────┤
│                      Subtotal · Discount · VAT   │  Totals
│                      TOTAL PAYABLE  BDT ####.##  │
│                      "This is not a VAT invoice" │
├──────────────────────────────────────────────────┤
│ EXCLUSIONS AND ASSUMPTIONS                       │
├──────────────────────────────────────────────────┤
│ TERMS Q-1…Q-8 — parallel columns                 │  Statutory block
├──────────────────────────────────────────────────┤
│ CUSTOMER APPROVAL  ☐ Approve  ☐ Decline          │
│ Signature / OTP / portal · Date · Branch mgr     │
├──────────────────────────────────────────────────┤
│ EST-…-004417 · Page 1 of 2 · Hotline 16743       │  Footer
└──────────────────────────────────────────────────┘
```

| # | Rule |
|---|---|
| **L-05-a** | Every line item cites the `DT-004` finding number that justifies it. **A line with no finding cannot print** |
| **L-05-b** | The totals block, the exclusions block and the terms block never split across pages (`VB-004` G-04) |
| **L-05-c** | `TOTAL PAYABLE` is the largest figure on the page and is stated **including VAT**. A customer who reads only one number reads the one they will pay |
| **L-05-d** | The approval block is the last thing on the document. Nothing prints after it that could be read as a further condition |
| **L-05-e** | Column widths are set for Bengali (`VB-004` BL-02); the description column is the widest |

---

## 4. Field Mapping

### 4.1 Header, party and context

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Estimate no. | প্রাক্কলন নং | `MD-040` sequence | Monospace | ✔ | |
| Estimate date | প্রাক্কলনের তারিখ | `estimate.issued_at` | `DD/MM/YYYY` | ✔ | |
| Valid until | মেয়াদ শেষ | `estimate.valid_to` | `DD/MM/YYYY` | ✔ | **`BRU-SRM-13`** |
| Legal entity + BIN | প্রতিষ্ঠান ও বিআইএন | `MD-002` | Text + monospace | ✔ | |
| Branch | শাখা | `MD-003.branch_name` | Text | ✔ | |
| Customer name | গ্রাহকের নাম | `party.display_name` | Text | ✔ | |
| Customer mobile | মোবাইল | `party.mobile_primary` | `+880 1#########` | ✔ | |
| Customer BIN / TIN | বিআইএন / টিআইএন | `party.bin`, `party.tin` | Monospace | | **✔ for VAT-registered buyers** |
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ | |
| Diagnostic report no. | রিপোর্ট নং | `DT-004` reference | Monospace | ✔ | |
| Device | ডিভাইস | `MD-021` make + model | Text | ✔ | |
| Serial / IMEI | সিরিয়াল | `device.serial_no` | Monospace | ✔ | |

### 4.2 Line items

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Line no. | ক্রমিক | Computed | Integer | ✔ | |
| Finding ref. | পর্যবেক্ষণ সূত্র | `DT-004` `F{n}` | Monospace | ✔ | **`L-05-a`** |
| Item type | ধরন | `estimate.line.type` | Enum: part / labour / transport / consumable / fee | ✔ | |
| Description | বিবরণ | `MD-019` or `MD-022` name | Text | ✔ | |
| Part code | যন্ত্রাংশ কোড | `MD-022.part_code` | Monospace | | Part lines |
| Part origin | যন্ত্রাংশের উৎস | `estimate.line.part_origin` | Enum: OEM / OEM-equivalent / refurbished / customer-supplied | | **✔ on every part line** |
| Quantity | পরিমাণ | `estimate.line.qty` | Number + `MD-023` UoM | ✔ | |
| Unit rate | একক দর | `MD-029` rate card | BDT, 2 dp | ✔ | |
| Discount | ছাড় | `MD-030` rule | BDT / % | | **✔ where applied; reason printed** |
| VAT rate | ভ্যাট হার | `MD-037.rate_pct` | % , 3 dp | ✔ | **Pending G6** |
| VAT amount | ভ্যাট পরিমাণ | Computed | BDT, 2 dp | ✔ | |
| Line amount | মোট | Computed | BDT, 2 dp | ✔ | |

### 4.3 Totals

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Subtotal — parts | উপমোট — যন্ত্রাংশ | Computed | BDT, 2 dp | ✔ |
| Subtotal — labour | উপমোট — শ্রম | Computed | BDT, 2 dp | ✔ |
| Subtotal — other | উপমোট — অন্যান্য | Computed | BDT, 2 dp | ✔ |
| Discount total | মোট ছাড় | Computed | BDT, 2 dp | ✔ |
| Taxable value | করযোগ্য মূল্য | Computed | BDT, 2 dp | ✔ |
| VAT total | মোট ভ্যাট | Computed per rate band | BDT, 2 dp | ✔ |
| Inspection fee already paid | পরিশোধিত পরিদর্শন ফি | `DT-016` reference | BDT, 2 dp | Where applicable |
| **Total payable** | **মোট প্রদেয়** | Computed | BDT, 2 dp, largest type | ✔ |
| Amount in words | কথায় | Computed | Text, both languages | ✔ |

| # | Rule |
|---|---|
| **FM-05-a** | Rounding follows `MD-039`. The document never rounds a line and the total independently — the total is the sum of the rounded lines |
| **FM-05-b** | VAT is subtotalled **per rate band** where more than one rate applies (`MD-037`), because `DT-010` must present it the same way |
| **FM-05-c** | `part_origin` prints on every part line. A refurbished or OEM-equivalent part sold as if new is a misrepresentation |
| **FM-05-d** | A customer-supplied part prints at zero value with the warranty consequence stated in term Q-6 |
| **FM-05-e** | Discounts print with their `MD-030` reason. An unexplained discount on a customer document is an audit finding and a negotiation precedent |
| **FM-05-f** | Amount in words prints in **both** languages, using Arabic numerals inside the Bengali text (`VB-004` BL-05) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-07` | Above BDT 5,000 the approval block is mandatory and work is blocked until it is captured |
| `BRU-SRM-08` | Above BDT 25,000 a branch-manager approval line prints in addition to the customer's |
| `BRU-SRM-11` | Parts cannot be issued until this estimate is approved. The estimate is the gate |
| `BRU-SRM-13` | An expired estimate is **re-issued**, never extended. The reissue carries a new number and cites the expired one |
| `BRU-WTY-06` | Privilege discounts apply to **labour only** — never to parts, consumables or transport. The discount column enforces it per line |
| `BRU-SRM-10` | Privilege Gold and Diamond members carry priority-1 SLA; the estimate states the resulting turnaround |
| `BRU-CTR-02` | Work outside contract scope is quoted separately and never silently absorbed — contract customers receive an estimate for the out-of-scope portion |
| `BRU-CTR-04` | Entitlement over-consumption prints as a chargeable line, never as an invisible absorption |
| `TAX-01`, `TAX-04` (`MD-037`) | Each line resolves to exactly one tax code; the rate is the rate at the tax point |
| `BRU-AIM-02` | An `M11` dynamic price cannot cross the configured floor or ceiling; the printed rate is always a governed rate |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard A4** | Walk-in and field paid repair | The base document |
| **Portal rendition** | `P01`, `P04` | Approve / decline actions inline; identical content (`UI-038`) |
| **SMS / WhatsApp summary** | Low-value, high-volume | Total, validity, one-line scope and a signed approval link. **The full estimate is always available; the summary is never the offer** |
| **Corporate quotation** | `P04`, `M36` | Adds cost-centre, site, asset tag, PO reference and the contract's approval chain |
| **Tender / bid** | `M36` public and enterprise tenders | Adds compliance schedule, validity extension terms and bid-security reference; approved by Commercial, not by a branch |
| **AMC-covered zero-value** | Work fully covered by contract | Prints at BDT 0.00 with the entitlement consumed, so the customer sees the value delivered (`BRU-CTR-04`) |
| **Warranty zero-value** | Manufacturer warranty | Prints at BDT 0.00, cause category from `DT-004`, and states no charge applies |
| **Marketplace** | `P07` seller job | Seller identity disclosed; 1000FiX remains the contracting party; commission never shown to the customer |

### 6.1 Exclusions and assumptions block

Printed on every variant. Populated from `MD-026` where an exclusion is standard, free text otherwise.

| # | Content |
|---|---|
| E-1 | Faults not identified in `DT-004` are not covered by this estimate |
| E-2 | Hidden damage found once the device is opened requires a revised estimate (`DT-006`) |
| E-3 | Data loss risk as stated in `DT-004`; backup is the customer's responsibility (`DT-002` T-3) |
| E-4 | Parts availability and lead time where a part is not in stock |
| E-5 | Consequential faults arising from the customer's decision to decline recommended work |

### 6.2 Terms — the statutory block

| # | Term | Substance |
|---|---|---|
| **Q-1** | Scope | Only the listed lines are quoted |
| **Q-2** | Validity | The estimate expires on the stated date; prices and part availability are not held beyond it (`BRU-SRM-13`) |
| **Q-3** | Price certainty | **The final invoice will not exceed the approved estimate unless a revised estimate is approved (`DT-006`).** Wording and enforceability confirmed at G6 |
| **Q-4** | Taxes | VAT at the applicable rate is included as shown; a compliant `DT-010` is issued on payment |
| **Q-5** | Warranty on the repair | The repair warranty granted, its term and its exclusions, cross-referenced to `DT-032` |
| **Q-6** | Customer-supplied parts | Carry no warranty from 1000FiX, and labour warranty is limited where they fail |
| **Q-7** | Old parts | Returned on request except where a brand claim requires their return |
| **Q-8** | Declining the estimate | The inspection fee position, storage, and the collection deadline (`DT-002` T-7) |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-005-S1` | Handset screen + battery, BDT 12,400 | Base bilingual, `BRU-SRM-07` approval block |
| `DT-005-S2` | Board-level repair, BDT 31,000 | `BRU-SRM-08` dual approval |
| `DT-005-S3` | Two VAT rate bands on one estimate | `FM-05-b` per-band subtotalling |
| `DT-005-S4` | Privilege Gold customer, labour discount | `BRU-WTY-06` line-level discount restriction |
| `DT-005-S5` | AMC-covered, BDT 0.00 | Entitlement consumption visible |
| `DT-005-S6` | Maximum line items, 2 pages | Totals and terms blocks do not split (`WE-02`) |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Commercial with Operations | 2026-08-15 | Draft issue |
| Reviewer — Finance | *pending* | | |
| Reviewer — Tax | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| **G6 — external tax and legal verification** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — CCO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `EST-{entity}-{branch}-{yy}-{seq:06d}` |
| Gap policy | `no_gaps` — a declined or expired estimate keeps its number and records its outcome |
| Reset | Fiscal year |
| Archive format | **PDF/A-3 at issue** (class A, `R-02`) |
| Retention | `LG-009`; not less than the retention of the `DT-010` it becomes, because the two must be reconcilable |
| Re-render | **Prohibited.** Rate cards and tax rates move; a re-render would quote today's prices under yesterday's number (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged with user and reason (`RC-01`, `RC-03`) |
| Approval evidence | Signature image, portal action log, OTP reference or call recording reference stored in `M24` against the estimate number |

### 9.1 Approval evidence — what counts

| Method | Evidence stored | Acceptable above BDT 25,000 |
|---|---|:--:|
| Wet signature on the printed estimate | Scanned image | ✔ |
| On-screen signature (`P02`, branch tablet) | Vector capture + device + timestamp | ✔ |
| Portal approve action (`P01`, `P04`) | Authenticated user, IP, timestamp | ✔ |
| OTP confirmation against the estimate number | Masked number, timestamp, message reference | ✔ |
| Recorded verbal approval via `P10` | Call recording reference + agent ID | **Only with a follow-up SMS confirmation logged** |
| Email reply | Message ID and full header retained | ✔ |
| Verbal, unrecorded | **Not acceptable at any value** | ✖ |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-004_Diagnostic_and_Condition_Report.md`](DT-004_Diagnostic_and_Condition_Report.md) | Supplies the finding numbers every line cites |
| [`DT-006_Revised_Estimate_and_Approval_Record.md`](DT-006_Revised_Estimate_and_Approval_Record.md) | The only lawful route to charging more than this document |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | What this becomes; VAT presentation must reconcile |
| [`../05B_Finance_and_Statutory/DT-019_Proforma_Invoice_and_Advance_Request.md`](../05B_Finance_and_Statutory/DT-019_Proforma_Invoice_and_Advance_Request.md) | Where a customer needs a payment document instead |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Unit rates |
| [`../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-030_Discount_Promotion_and_Voucher_Rule_Register.md`](../../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-030_Discount_Promotion_and_Voucher_Rule_Register.md) | Discount rules and reasons |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) | VAT rate derivation |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) | Rounding |
| `UI-038` Estimate and Approval Flow Copy | The on-screen approval journey |
| [`NT-004_SMS_Template_Library_Customer.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | The estimate-ready and approval-reminder messages |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The full terms Q-1…Q-8 summarise |
| [`SP-013_SOP_Estimate_Approval_and_Rework_Control.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-013_SOP_Estimate_Approval_and_Rework_Control.md) | How it is produced and approved |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Finding-to-line binding, dual approval thresholds, per-band VAT subtotalling, part-origin disclosure, eight-term statutory block, approval-evidence hierarchy | CCO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Every mandated element listed in §2 with source and verification date
- [x] Approval thresholds stated and bound to `BRU-SRM-07` / `BRU-SRM-08`
- [x] "This is not a VAT invoice" rule stated (`NT-05-a`)
- [x] Approval-evidence hierarchy defined, with the unacceptable method named
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] **G6** tax verification of rates and tax-point treatment — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6** legal verification of term Q-3 price-certainty wording — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
