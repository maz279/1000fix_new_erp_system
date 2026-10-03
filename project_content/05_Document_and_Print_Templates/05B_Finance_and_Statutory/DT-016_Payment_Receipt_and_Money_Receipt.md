---
id: DT-016
title: Payment Receipt and Money Receipt
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Treasury, Branch Operations and Content Design
reviewers: [External tax adviser, Tax, Treasury, Internal Audit, Branch Operations, Localisation Lead]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The receipt issued whenever money is taken — cash, mobile money, card, cheque or bank transfer —
  with branch and collector identity. Cash handling across 51+ branches and a mobile field force
  is the most fraud-exposed process in the business, and this receipt is the primary control:
  every taka collected is either on a numbered receipt or it is unaccounted for.
traces_to: [M20, M50, M51, M04, M02, DT-001, DT-002, DT-009, DT-010, DT-017, MD-002, MD-038, MD-039, MD-040, BRU-FIN-02, BRU-FIN-10, BRU-FSM-07, BRU-LOG-06]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: DT-016_Payment_Receipt_and_Money_Receipt_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-02 — cash receipts above BDT 50,000 require the customer's NID to be recorded
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-10 — branch cash must be reconciled and closed daily; an unclosed shift blocks the next shift's opening
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FSM-07 — on-site payment must be reconciled to the branch cash book by the end of the technician's shift
    verified: 2026-08-15
    class: P1
  - source: Stamp Act 1899 — revenue stamp obligation on money receipts above a prescribed value. **Applicability and current threshold must be verified at G6**
    verified: 2026-08-15
    class: P2
  - source: VAT and Supplementary Duty Rules 2016 — where the receipt evidences a taxable supply of services, the relationship to Mushak 6.3 must be established at G6
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-016 — Payment Receipt and Money Receipt

> ⚠ **Tier S — statutory consequence and a probable prescribed element (revenue stamp). Gate G6
> mandatory and unwaivable (`WV-02`).**
>
> **A receipt is a control, not a courtesy.** In a network of 51+ branches, hundreds of field
> technicians and riders collecting cash on delivery, the numbered receipt is the only thing
> standing between "collected" and "collected by the company".
>
> **The receipt is not the tax invoice.** `DT-010` is. §2.1 states the relationship, and G6
> settles it.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Money receipt / payment acknowledgement** |
| Owning module | `M20` Accounts Receivable, with `M50` Treasury |
| Statutory | **Yes — Tier S.** Stamp Act 1899 revenue-stamp obligation (threshold pending G6); VAT relationship pending G6 |
| Recipient(s) | Payer (original), branch cash book, `P01`/`P04` portal record |
| Languages | **Bilingual — stacked labels** |
| Output formats | **Thermal 80 mm (primary, counter)** · Thermal 58 mm (rider) · A5 portrait · A4 (corporate) · PDF · **PDF/A-3 archive** |
| Numbering mask | `MD-040` — statutory sequence, **`no_gaps`, branch- and collector-aware** |
| Retention period | **At least 5 years** — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 Payment methods it covers

| Method | Collected by | Evidence beyond the receipt |
|---|---|---|
| Cash | Branch cashier, technician, rider | Shift reconciliation (`BRU-FIN-10`, `BRU-FSM-07`, `BRU-LOG-06`) |
| Mobile financial services (bKash, Nagad, Rocket) | Branch, field, customer self-service | Transaction ID from the provider |
| Card — present | Branch POS | Terminal reference and slip |
| Card — not present / online gateway | `P01`, `P04` | Gateway transaction reference |
| Bank transfer / RTGS / BEFTN | Customer to the company account | Bank reference; receipt issued on **confirmed credit**, never on advice |
| Cheque | Branch, corporate collection | **Receipt states "subject to realisation"** until cleared |
| Store credit / wallet | System | Internal reference; no cash movement |
| Adjustment against advance | System | `DT-019` proforma reference |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Revenue stamp on money receipts above the prescribed value | Stamp Act 1899 — **pending G6** | pending | Signature zone |
| Identity of the receiving entity with BIN | VAT & SD Act 2012 — **pending G6** | pending | Header |
| Amount received, in figures and words | Commercial and evidential practice; Stamp Act — **pending G6** | pending | Body |
| Date of receipt | **pending G6** | pending | Header |
| What the payment is against | **pending G6** | pending | Body |
| NID where cash exceeds BDT 50,000 | `BRU-FIN-02` | 2026-08-15 | Payer block |
| Signature of the receiving officer | **pending G6** | pending | Signature zone |

### 2.1 The receipt-versus-invoice question

| Position | Consequence |
|---|---|
| The receipt **is** the tax document for a service supply | Then it must conform to Mushak 6.3 and this template merges with `DT-010` |
| The receipt is **separate** from the tax invoice | Then two documents issue, and the receipt must state clearly that it is not a VAT invoice |
| The tax point is **payment** rather than completion | Then `DT-010` issues at the moment this receipt does, and they are printed together |

> **G6 M1 decides this, and it changes the branch counter workflow.** Until it is answered, the
> receipt prints **"This is not a VAT invoice / এটি ভ্যাট চালান নয়"** and a separate `DT-010`
> is issued — the conservative position.

### 2.2 G6 questions

| # | Question |
|---|---|
| **M1** | Is the money receipt a separate document from the Mushak 6.3, or does the challan serve as the receipt? What is the tax point for a repair service? |
| **M2** | Does the Stamp Act revenue-stamp obligation apply to our receipts, and at what current threshold? |
| **M3** | Is an electronic or thermal receipt acceptable where a revenue stamp would otherwise be required? |
| **M4** | Are there record-keeping obligations specific to cash receipts beyond the VAT retention period? |
| **M5** | Is any obligation triggered by cash receipts above a threshold — reporting, identity verification — beyond our internal `BRU-FIN-02`? |
| **M6** | For mobile financial services, is the provider's transaction record sufficient, or must our own receipt still issue? |

---

## 3. Layout

**Primary format: Thermal 80 mm** — the highest-volume rendition. A5 and A4 where a signature or
a revenue stamp is required.

```
      1000FiX Services Limited
        BIN ############
      Shewrapara Branch
    ------------------------------
       MONEY RECEIPT / টাকা প্রাপ্তির রসিদ
    Receipt   RCP-SHW-26-004417
    Date      15/08/2026 16:42
    ------------------------------
    Received from / প্রাপ্তি
      Md. Rahman  ...4821
    Against / যার বিপরীতে
      SR-2026-114882
      Invoice INV-…-009914
    ------------------------------
    Method / পদ্ধতি      Cash
    Amount / পরিমাণ   BDT 12,400.00
    In words: Twelve thousand four
      hundred taka only
    ------------------------------
    Invoice total     12,400.00
    Paid to date      12,400.00
    Balance                0.00
    ------------------------------
    Received by / গ্রহণকারী
      A. Rahman (EMP-2211)
    ------------------------------
    This is not a VAT invoice
    এটি ভ্যাট চালান নয়
    Keep this receipt / রসিদটি সংরক্ষণ করুন
    Hotline 16743   [QR]
```

| # | Rule |
|---|---|
| **L-16-a** | The **amount in words** prints on every rendition, in both languages. It is the oldest anti-alteration control there is and it still works |
| **L-16-b** | The receipt number, the collector's identity and the branch print on every rendition without exception |
| **L-16-c** | Balance after payment prints. A customer who cannot see their remaining balance will assume there is none |
| **L-16-d** | **"Keep this receipt"** prints on thermal output — thermal paper fades (`VB-004` TH-07) — together with the statement that the record is in the portal |
| **L-16-e** | Where a revenue stamp is required (G6 M2), the thermal rendition **cannot** be used; A5 issues instead |
| **L-16-f** | Bengali on thermal is tested per printer model. A model that cannot render conjuncts does not issue Bengali receipts (`VB-004` TH-08) |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Receipt no. | রসিদ নং | `MD-040` sequence | Monospace | ✔ |
| Receipt date and time | তারিখ ও সময় | `payment.received_at` | `DD/MM/YYYY HH:mm` | ✔ |
| Legal entity + BIN | প্রতিষ্ঠান ও বিআইএন | `MD-002` | Text + monospace | ✔ |
| Branch / location | শাখা / স্থান | `MD-003` | Text | ✔ |
| Received from | প্রাপ্তি | `party.display_name` | Text | ✔ |
| Payer mobile (masked) | মোবাইল | `party.mobile_primary` | Last 4 | ✔ |
| **NID** | **এনআইডি** | `party.national_id` masked | Monospace | **✔ cash > BDT 50,000 (`BRU-FIN-02`)** |
| Against — order | যার বিপরীতে — অর্ডার | `service_order.order_ref` | Monospace | ✔ where applicable |
| Against — invoice | চালান | `DT-010` reference | Monospace | ✔ where invoiced |
| Against — description | বিবরণ | Free text | Text | Where no order or invoice |
| Payment method | পদ্ধতি | `MD-038.payment_method_code` | Label | ✔ |
| Provider transaction ID | লেনদেন আইডি | `payment.provider_txn_ref` | Monospace | **✔ for MFS, card, bank** |
| Cheque no. / bank / date | চেক নং / ব্যাংক | `payment.cheque_*` | Monospace | ✔ for cheque |
| **Amount received** | **প্রাপ্ত পরিমাণ** | `payment.amount` | BDT, 2 dp | ✔ |
| **Amount in words** | **কথায়** | Computed | Text, both languages | ✔ |
| Currency | মুদ্রা | `MD-039` | BDT default | ✔ |
| Invoice total | চালান মোট | `invoice.total` | BDT, 2 dp | Where invoiced |
| Paid to date | মোট পরিশোধিত | Computed | BDT, 2 dp | ✔ |
| Balance | বকেয়া | Computed | BDT, 2 dp | ✔ |
| Received by | গ্রহণকারী | `employee.display_name` + ID | Text | ✔ |
| Shift / session | শিফট | `M50.cash_session_id` | Monospace | ✔ for cash |
| Subject to realisation | আদায় সাপেক্ষে | Static | Text | **✔ for cheque** |
| Revenue stamp | রেভিনিউ স্ট্যাম্প | Physical | — | Per G6 M2 |

| # | Rule |
|---|---|
| **FM-16-a** | **No receipt without a numbered sequence.** A handwritten receipt is not a receipt; it is an unrecorded collection |
| **FM-16-b** | A cheque receipt states **"subject to realisation"** and does not clear the balance until the cheque clears. Printing a zero balance on an uncleared cheque is how a bounced cheque becomes an unrecoverable debt |
| **FM-16-c** | MFS, card and bank receipts carry the provider's transaction reference. Without it the payment cannot be reconciled to the settlement file |
| **FM-16-d** | A bank transfer receipt issues on **confirmed credit**, never on a customer's payment advice |
| **FM-16-e** | The collector's employee ID prints. A receipt that does not name who took the money is not a control |
| **FM-16-f** | Refunds are **never** issued on this document. A refund is a `DT-015` credit note with a payment reference |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-FIN-02` | NID captured and printed masked on cash above BDT 50,000; the receipt cannot issue without it |
| `BRU-FIN-03` | No payment against a cancelled invoice |
| `BRU-FIN-10` | Branch cash reconciled and closed daily; an unclosed shift blocks the next shift's opening |
| `BRU-FSM-07` | Field payment reconciled to the branch cash book by shift end |
| `BRU-LOG-06` | Cash on delivery reconciled per rider per shift, **zero tolerance for unexplained variance** |
| `BRU-BIL-05` | Refunds to the original payment method — enforced on `DT-015`, not here |
| `SEQ-01` (`MD-040`) | Gap-free, branch- and collector-aware sequences |

### 5.1 The cash control chain

The receipt is one link. It only works as part of the chain.

| Step | Control | Artefact |
|---|---|---|
| 1 | Collector opens a cash session with a counted float | `M50` session open |
| 2 | Every collection issues a numbered receipt | **This document** |
| 3 | Receipt numbers are sequential per collector per session | `SEQ-01` |
| 4 | Session closes with a physical count against the system total | `BRU-FIN-10` |
| 5 | Variance is explained and approved, or escalated | `MD-026` reason code |
| 6 | Cash is banked and the deposit reference recorded | `M50` |
| 7 | Bank credit is matched to the deposit | `M50` reconciliation |
| 8 | Unmatched deposits age and escalate | `RP-012` |

| # | Rule |
|---|---|
| **CC-01** | A gap in a collector's receipt sequence within a session is an **immediate** exception, not a month-end finding |
| **CC-02** | A voided receipt retains its number, states the reason and is counted in the session (`RC-04`) |
| **CC-03** | An unclosed session blocks the collector's next session (`BRU-FIN-10`) — this is the rule that makes daily reconciliation actually happen |
| **CC-04** | Rider cash follows the same chain with the consignment as the session boundary (`BRU-LOG-06`) |
| **CC-05** | Variance tolerance is **zero for explanation**, not zero for occurrence. Every variance is explained; the size determines the approval level |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Thermal 80 mm counter** | Branch, the highest-volume rendition | The base document |
| **Thermal 58 mm rider** | `P09` cash on delivery | Narrower; consignment reference replaces the session; pairs with `DT-028` |
| **A5 with revenue stamp** | Where G6 M2 requires a stamp | Physical stamp and wet signature; thermal not permitted (`L-16-e`) |
| **A4 corporate** | Cheque or transfer against a `DT-020` invoice | Multi-invoice allocation table; authorised signatory |
| **Field technician** | On-site collection (`M02`) | Adds GPS and job reference; reconciles by shift (`BRU-FSM-07`) |
| **Digital-only** | Online gateway, MFS self-service | No print; PDF to the portal and email. Gateway reference mandatory |
| **Advance / on-account** | Payment not against a specific invoice | States it is held on account; links to `DT-019` where a proforma exists |
| **Part payment** | Partial settlement | Balance and the agreed schedule print |
| **Refund acknowledgement** | **Not this document** | Use `DT-015` (`FM-16-f`) |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-016-S1` | Cash BDT 12,400 at branch counter, thermal | Base bilingual thermal rendition |
| `DT-016-S2` | Cash BDT 62,000 | `BRU-FIN-02` NID capture |
| `DT-016-S3` | bKash payment with provider reference | `FM-16-c` |
| `DT-016-S4` | Cheque, subject to realisation | `FM-16-b` balance treatment |
| `DT-016-S5` | Rider COD, 58 mm | Consignment linkage to `DT-028` |
| `DT-016-S6` | Corporate cheque allocated across 4 invoices | Allocation table |
| `DT-016-S7` | Bengali on three thermal printer models | `L-16-f` per-model legibility |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Treasury | 2026-08-15 | Draft issue |
| Reviewer — Treasury | *pending* | | |
| Reviewer — Branch Operations | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — external tax and legal verification (M1, M2)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040`, statutory, **`no_gaps`**, branch- and collector-aware |
| Reset | Fiscal year; **session boundaries do not reset the sequence**, they segment it |
| Archive format | **PDF/A-3 at issue** for every receipt, including thermal renditions — the thermal paper fades, the archive does not |
| Retention | **At least 5 years** — pending G6 M4 |
| Re-render | Prohibited (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged. A customer who lost a thermal receipt receives a **COPY**, never a second original (`RC-02`) |
| Void | Retains its number, states the reason, counted in the session (`CC-02`) |
| Portal availability | Every receipt is available in `P01` / `P04` indefinitely within the retention period — this is the mitigation for thermal fade |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The tax document this is **not**, pending G6 M1 |
| [`DT-017_Customer_Statement_of_Account.md`](DT-017_Customer_Statement_of_Account.md) | Every receipt appears as a credit on the statement |
| [`DT-019_Proforma_Invoice_and_Advance_Request.md`](DT-019_Proforma_Invoice_and_Advance_Request.md) | Advance receipts reference it |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | Refunds — never issued on this document |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Inspection fee taken at intake |
| [`../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md`](../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md) | Payment status at release |
| [`../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md`](../05C_Supply_Chain_and_Logistics/DT-028_Proof_of_Delivery_and_Custody_Record.md) | Rider cash on delivery |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Payment methods and banks |
| `RP-004` Dashboard Specification Pack — Operational Consoles | Session, variance and unmatched-deposit reporting |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) | The operational chain in §5.1 |
| `OP-014` Manual Fallback Procedure Set | Session open and close |
| [`NT-004_SMS_Template_Library_Customer.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-004_SMS_Template_Library_Customer.md) | Payment confirmation message |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Eight payment methods, the receipt-versus-invoice question raised for G6, amount-in-words and cheque-realisation rules, eight-step cash control chain with five rules, thermal-fade mitigation via portal availability | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Receipt-versus-invoice ambiguity raised explicitly with a stated conservative default (§2.1)
- [x] Cheque, MFS and bank-transfer treatments differentiated
- [x] Cash control chain documented as a chain, not as a receipt in isolation
- [x] Thermal fade mitigated by mandatory archive and portal availability
- [x] All internal links resolve
- [ ] **G6 M1 — receipt versus Mushak 6.3 and the tax point** — **outstanding; changes the branch counter workflow**
- [ ] **G6 M2 — revenue-stamp applicability and threshold** — **outstanding; determines whether thermal may be used at all above the threshold**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Bengali thermal legibility proven on every deployed printer model (`L-16-f`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
