---
id: DT-039
title: Marketplace Seller Payout Statement
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Marketplace Operations with Finance
author: Marketplace Operations with Finance, Tax and Content Design
reviewers: [External tax adviser, Tax, Finance, Legal & Compliance, Internal Audit]
approver: Chief Financial Officer
content_class: A
purpose: >
  Jobs, gross value, commission, fees, adjustments, holds, net payout and the period. Seller trust
  in the platform rests almost entirely on payout transparency; a seller who cannot reconcile their
  payout will assume they have been short-paid, and disputes here are existential for P07.
traces_to: [M53, M12, M20, M51, P07, DT-001, DT-010, DT-015, DT-017, DT-040, MD-016, MD-018, MD-037, MD-038, MD-040, BRU-BIL-03, BRU-BIL-04, BRU-FIN-08, BRU-FIN-09, BRU-ECM-04, BRU-ECM-09]
priority: P2
wave: W7
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — DT-039 remains English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-BIL-03 — a seller payout is held for the configured period after job completion and blocked entirely while a dispute is open
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-08 — marketplace transactions are accounted per the declared principal-or-agent model; the model cannot vary by transaction
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-BIL-04 — commission is reversed automatically when the underlying transaction is refunded or a dispute is decided against the seller
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-039 — Marketplace Seller Payout Statement

> ⚠ **Class A — statutory consequence.** Commission is a taxable supply by us to the seller.
> Withholding may apply on payments to the seller (`BRU-FIN-09`). And **`BRU-FIN-08`'s
> principal-or-agent model determines what this statement even represents** — a payout of money
> we collected as agent, or a purchase of services we resold as principal.
>
> **That model must be declared before `P07` launches, and it cannot vary by transaction.**

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Seller settlement statement |
| Owning module | `M53` Revenue Recognition, Commission and Settlement, with `M12` |
| Statutory | No prescribed form. **Class A** — commission VAT and withholding on seller payments |
| Recipient(s) | Marketplace seller, marketplace operations, finance, internal audit |
| Languages | **English only** (`CG-010` §3.2) — sellers transact as businesses on `P07` |
| Output formats | `P07` portal (primary) · PDF · structured export (CSV) for the seller's own accounting |
| Numbering mask | `MD-040` — `PAY-{entity}-{yy}-{seq:06d}` per seller per period |
| Retention period | **At least 5 years** where it evidences a taxable supply — confirmed at G6; otherwise `LG-009` |

### 1.1 What a seller needs to be able to do with it

| # | The seller must be able to… | What that requires |
|---:|---|---|
| 1 | Match every job they completed to a line | Job reference, date, customer reference, gross value |
| 2 | Understand every deduction | Itemised commission, fees, adjustments — each with a reason |
| 3 | See what is held and why | Hold lines with reason and expected release |
| 4 | Reconcile the net to what arrived in their account | Payment reference, date, method |
| 5 | Account for tax correctly | Commission VAT, withholding, and the documents that support both |
| 6 | Dispute a specific line | A line reference and a route |

> **If any of the six is not possible, the statement will generate a support contact.** At scale —
> 500 to 2,000 sellers — that is the difference between a platform and a call centre.

---

## 2. Statutory Requirements

No prescribed form. Four obligations:

| Obligation | Source | Verified | Effect |
|---|---|---|---|
| VAT on commission | VAT & SD Act 2012 — **pending G6** | pending | Our commission is a supply to the seller and needs a `DT-010` |
| Withholding on payments to sellers | Income Tax Act 2023; `BRU-FIN-09` — **pending G6** | pending | Deduction and the evidence given to the seller |
| VDS where applicable | `MD-037`, `DT-013` — **pending G6** | pending | Certificate obligation |
| Principal-or-agent presentation | `BRU-FIN-08`; accounting standards | 2026-08-15 | Determines gross-versus-net revenue and what this statement is |

### 2.1 G6 questions

| # | Question |
|---|---|
| **MP1** | Under the principal-or-agent model we declare, **who is the supplier of record to the end customer**, and who issues the Mushak 6.3? (paired with `DT-010` Q9) |
| **MP2** | Is our commission a taxable supply requiring its own Mushak 6.3 to the seller? |
| **MP3** | Does withholding apply to payments to marketplace sellers, at what rate, and what evidence must we provide? |
| **MP4** | Does VDS apply, and does the seller receive a `DT-013`? |
| **MP5** | What retention applies to settlement records? |

> **MP1 is the same question as `DT-010` Q9 and it is unavoidable.** Until it is answered, `P07`
> cannot invoice, cannot settle and cannot launch.

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | Statement number, seller, period, payout date |
| Party block | Seller name, code, BIN/TIN and bank details left; our entity and contact right |
| Body | **Summary** → job lines → commission and fees → adjustments → holds → tax |
| Totals | Gross, deductions, tax, **net paid**, and the payment reference |
| Statutory block | Not used. The **tax summary and dispute route** occupy this zone |
| Signature | Not signed; issued under system authority |
| Footer | Statement reference, `page n of m`, dispute route and deadline |

| # | Rule |
|---|---|
| **L-39-a** | **Summary first.** Gross, total deductions, held, net — four numbers a seller can check in five seconds before reading detail |
| **L-39-b** | Every deduction line carries a **type and a reason**, never a bare amount |
| **L-39-c** | Held amounts appear as their own block with reason and **expected release date**. A hold with no expected release reads as a confiscation |
| **L-39-d** | The tax summary is separate and complete: commission VAT charged, withholding deducted, certificates issued or due |
| **L-39-e** | The structured export matches the printed statement line for line |
| **L-39-f** | Column headers repeat on every page; the net figure never appears alone on a continuation page |

---

## 4. Field Mapping

### 4.1 Header and summary

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Statement no. | `MD-040` sequence | Monospace | ✔ |
| Statement date | `payout.generated_at` | `DD/MM/YYYY` | ✔ |
| Period from / to | `MD-041` period | Date range | ✔ |
| Seller name and code | `MD-018` / `MD-016` | Text + monospace | ✔ |
| Seller BIN / TIN | `MD-016.bin`, `.tin` | Monospace | ✔ where registered |
| Seller bank account (masked) | `MD-038` | Masked | ✔ |
| **Gross job value** | Computed | BDT, 2 dp | ✔ |
| **Total deductions** | Computed | BDT, 2 dp | ✔ |
| **Total held** | Computed | BDT, 2 dp | ✔ |
| **Net paid** | Computed | BDT, 2 dp, largest type | ✔ |
| Payment reference | `payment.txn_ref` | Monospace | ✔ once paid |
| Payment date and method | `payment.paid_at`, `MD-038` | Date + label | ✔ once paid |

### 4.2 Job lines and deductions

| Label | Source field | Format | Required |
|---|---|---|:--:|
| Job reference | `service_order.order_ref` | Monospace | ✔ |
| Completion date | `service_order.completed_at` | `DD/MM/YYYY` | ✔ |
| Customer reference (anonymised) | `party.masked_ref` | Monospace | ✔ **(`BRU-ECM-05`)** |
| Service description | `MD-019.item_name` | Text | ✔ |
| Gross value | `invoice.line_total` | BDT, 2 dp | ✔ |
| Commission rate | `MD-018.commission_rate` | %, 2 dp | ✔ |
| Commission amount | Computed | BDT, 2 dp | ✔ |
| **Commission VAT** | `MD-037` | BDT, 2 dp | ✔ **per G6 MP2** |
| Platform fee | `MD-018.fee_schedule` | BDT, 2 dp | ✔ where any |
| Payment-processing fee | `MD-038` | BDT, 2 dp | ✔ where any |
| Logistics recharge | `MD-029` | BDT, 2 dp | Where applicable |
| Parts supplied by us | `MD-022` + value | BDT, 2 dp | Where applicable |
| Adjustment | `MD-026.reason_code` + amount | Code + BDT | ✔ where any |
| **Commission reversal** | `BRU-BIL-04` | BDT, 2 dp, negative | ✔ where a refund or dispute occurred |
| Related credit note | `DT-015` reference | Monospace | ✔ with a reversal |
| Line net to seller | Computed | BDT, 2 dp | ✔ |

### 4.3 Holds, tax and dispute

| Label | Source field | Format | Required |
|---|---|---|:--:|
| **Hold type** | `payout.hold_type` | Enum: settlement period / open dispute / performance / compliance / negative balance | ✔ |
| Hold amount | `payout.hold_amount` | BDT, 2 dp | ✔ |
| Hold reason | `MD-026.reason_code` + text | Code + text | ✔ |
| Related job or case | Job / `M34` case reference | Monospace | ✔ |
| **Expected release** | `payout.expected_release` | `DD/MM/YYYY` or "on dispute closure" | ✔ **`L-39-c`** |
| Released this period | Computed | BDT, 2 dp | ✔ |
| Commission VAT total | Computed | BDT, 2 dp | ✔ |
| Commission tax invoice | `DT-010` reference | Monospace | ✔ **per G6 MP2** |
| **Withholding deducted** | Per G6 MP3 | BDT, 2 dp | ✔ where applicable |
| Withholding evidence | Certificate reference | Monospace | ✔ with a deduction |
| VDS deducted / certificate | `DT-013` reference | Monospace | ✔ per G6 MP4 |
| Opening / closing balance | Computed | BDT, 2 dp | ✔ |
| Dispute route and deadline | `M34` route | Text | ✔ |

| # | Rule |
|---|---|
| **FM-39-a** | **Opening balance equals the prior statement's closing balance**, always. The same continuity rule as `DT-017` FM-17-a, and the same blocking consequence |
| **FM-39-b** | Customer identity is anonymised beyond the awarded-job window (`BRU-ECM-05`) |
| **FM-39-c** | Payouts are held for the configured settlement period and **blocked entirely while a dispute is open** (`BRU-BIL-03`) — shown as separate hold types, because a routine settlement hold and a dispute block feel very different to a seller |
| **FM-39-d** | Commission reversals reference the credit note that caused them (`BRU-BIL-04`) |
| **FM-39-e** | Where withholding applies, the evidence the seller needs to claim it is referenced **on the statement**, not sent separately |
| **FM-39-f** | A negative closing balance is carried forward and stated plainly, with the recovery route (set-off against future payouts) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-BIL-03` | Settlement hold period; complete block during a dispute |
| `BRU-BIL-04` | Automatic commission reversal on refund or adverse dispute |
| `BRU-FIN-08` | Principal-or-agent model fixes what the statement represents |
| `BRU-FIN-09` | Withholding correctness on payments |
| `BRU-ECM-04` | Performance below threshold reduces visibility; below suspension threshold suspends — a suspension affects payouts and the statement says how |
| `BRU-ECM-05` | Customer contact data access expires after completion |
| `BRU-ECM-09` | Disputes are decided by 1000FiX; the decision and its evidence are recorded and referenced here |
| `BRU-ECM-08` | Registration expiry suspends the seller; held funds position is stated |

### 5.1 Trust mechanics

| # | Rule |
|---|---|
| **TM-01** | The statement is available **before** the payment arrives, not after. A seller who sees the money first and the explanation later has already formed a view |
| **TM-02** | Every deduction type is defined once, in the seller agreement, and named identically here (`MD-018`) |
| **TM-03** | Commission rate changes are notified in advance and take effect from a stated date. **A rate change discovered on a statement is a trust event, not a pricing event** |
| **TM-04** | Dispute outcomes are reflected on the next statement with the case reference, whichever way they went |
| **TM-05** | Payout timeliness against the stated schedule is a monitored platform metric, reported to Marketplace Operations |
| **TM-06** | A seller can export their full settlement history at any time. **A platform that makes a seller's own data hard to retrieve is a platform they will leave** |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard period statement** | Regular settlement cycle | The base statement |
| **Zero-payout period** | No completed jobs or all held | Still issued, showing why |
| **Negative balance** | Reversals exceed earnings | Carry-forward and recovery route (`FM-39-f`) |
| **Suspended seller** | `BRU-ECM-04` / `BRU-ECM-08` | Held funds position and the release conditions stated |
| **Final settlement** | Seller leaves the platform | Full reconciliation, release of holds subject to the dispute window, closing statement |
| **Corrected statement** | Error found after issue | New statement referencing the original; the original retained |
| **Structured export** | Seller's accounting | CSV matching the print exactly (`L-39-e`) |

---

## 7. Worked Example

> **Structure depends on G6 MP1.** Specimens are produced once the principal-or-agent model is
> declared.

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-039-S1` | 34 jobs, standard commission | Base statement and summary-first layout |
| `DT-039-S2` | Period with a dispute hold | `FM-39-c` hold-type separation |
| `DT-039-S3` | Commission reversal after a refund | `BRU-BIL-04` and credit-note reference |
| `DT-039-S4` | Withholding deducted | `FM-39-e` evidence reference |
| `DT-039-S5` | Negative closing balance | `FM-39-f` carry-forward |
| `DT-039-S6` | Final settlement on exit | Hold release and closing reconciliation |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Marketplace Operations with Finance | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax adviser (MP1–MP5)** | *pending* | | **Required before `P07` launch** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `PAY-{entity}-{yy}-{seq:06d}` per seller per period |
| Gap policy | `gaps_recorded` |
| Archive format | **PDF/A-3 at issue**, plus the structured export |
| Retention | **At least 5 years** where it evidences a taxable supply — pending G6 MP5; otherwise `LG-009` |
| Re-render | **Prohibited.** A regenerated statement reflects later adjustments and will not match the seller's copy |
| Reprint | Watermarked **COPY**, logged |
| Continuity | Opening-to-closing continuity verified per seller each period and reported as an exception where broken (`FM-39-a`) |
| Seller access | Full history downloadable from `P07` for the retention period (`TM-06`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-040_Partner_Commission_Statement.md`](DT-040_Partner_Commission_Statement.md) | The referral-partner counterpart; different mechanics, shared discipline |
| [`../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | Commission tax invoice; supplier-of-record question (Q9 / MP1) |
| [`../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md`](../05B_Finance_and_Statutory/DT-015_Credit_Note_and_Debit_Note.md) | Refunds driving commission reversal |
| [`../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md`](../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md) | Where VDS applies to seller payments |
| [`../05B_Finance_and_Statutory/DT-017_Customer_Statement_of_Account.md`](../05B_Finance_and_Statutory/DT-017_Customer_Statement_of_Account.md) | The continuity discipline this follows |
| [`../05B_Finance_and_Statutory/DT-018_Dunning_and_Collection_Letter_Series.md`](../05B_Finance_and_Statutory/DT-018_Dunning_and_Collection_Letter_Series.md) | Negative-balance recovery |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-018_Marketplace_Seller_Category_and_Standard_Register.md) | Commission rates, fees and standards |
| `LG-004` Marketplace Seller Agreement | Where every deduction type is defined (`TM-02`) |
| `EO-001` Marketplace Seller Onboarding Kit | Where the payout model is explained before a seller joins |
| `UI-017` P07 Marketplace Seller Portal UI Copy Pack | Portal presentation |
| [`NT-012_Email_Template_Library_Seller_and_Partner.md`](../../04_Notification_and_Messaging/04C_Email/NT-012_Email_Template_Library_Seller_and_Partner.md) | Payout and hold notifications |
| `RP-005` Dashboard Specification Pack — External Audiences | Payout timeliness and dispute reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six-capability seller test, summary-first layout, hold types separated with expected release, opening-balance continuity, six trust-mechanics rules, principal-or-agent question raised as launch-gating MP1 | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] The six things a seller must be able to do are stated and mapped to fields
- [x] Hold types separated with expected release dates (`L-39-c`)
- [x] Opening-balance continuity enforced (`FM-39-a`)
- [x] Withholding evidence referenced on the statement itself
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **G6 MP1 — principal-or-agent model and supplier of record** — **outstanding; gates `P07` launch, shared with `DT-010` Q9**
- [ ] G6 MP2–MP4 — commission VAT, withholding and VDS on seller payments — **outstanding**
- [ ] Commission rates, fee schedules and deduction types published in `MD-018` and in `LG-004` — **outstanding, dependency**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
