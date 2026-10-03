---
id: DT-017
title: Customer Statement of Account
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Account Management and Content Design
reviewers: [Tax, Legal & Compliance, Account Management, Internal Audit, Localisation Lead]
approver: Chief Financial Officer
content_class: A
purpose: >
  The period statement showing opening balance, every transaction, ageing and the dispute route.
  Corporate collections and reconciliation are impossible without a statement the customer accepts
  as authoritative — an unaccepted statement is not a collections tool, it is the start of an
  argument about which of the two ledgers is right.
traces_to: [M20, M19, M08, P04, DT-001, DT-010, DT-015, DT-016, DT-018, DT-020, MD-013, MD-015, MD-039, MD-041, BRU-CTR-05, BRU-FIN-07]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: DT-017_Customer_Statement_of_Account_BN.md
sources:
  - source: project_content/05_Document_and_Print_Templates/DT-001 §9 — retention, archive and re-render prohibition applied to a period statement
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-05 — contract suspension for non-payment follows the defined notice sequence
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P04 — consolidated invoicing, itemised breakdown, invoice-dispute rate below 3%
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-017 — Customer Statement of Account

> ⚠ **Class A — statutory consequence.** The statement is a VAT-adjacent record: it summarises
> issued challans and adjustment notes, and it is produced to auditors as evidence of the
> receivable. It is not itself a prescribed form.
>
> **The statement's value is entirely in whether the customer accepts it.** A statement the
> customer's accounts-payable team cannot reconcile to their own ledger produces a dispute, not
> a payment — and the `P04` commitment is an **invoice-dispute rate below 3%**.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Period statement of account |
| Owning module | `M20` Accounts Receivable, with `M19` |
| Statutory | No prescribed form; **class A** as a VAT-adjacent and audit-evidential record |
| Recipient(s) | Customer accounts payable, account manager, collections, auditor |
| Languages | **Bilingual — stacked labels.** English-dominant for corporate recipients (`VB-002`) |
| Output formats | A4 portrait · A4 landscape where the transaction columns require it · PDF · portal (`P01`, `P04`) · structured export (CSV) |
| Numbering mask | `MD-040` — `STM-{entity}-{yy}-{seq:06d}` per account per period |
| Retention period | `LG-009`; aligned to the underlying invoices |

### 1.1 Who receives one, and how often

| Audience | Cadence | Trigger |
|---|---|---|
| Corporate contract accounts (`P04`) | Monthly, on the billing cycle | Automatic |
| Credit-terms retail accounts | Monthly where a balance exists | Automatic |
| Accounts in collections | With every dunning step (`DT-018`) | Event |
| Any customer, on request | On demand | `P01` self-service |
| Brand partners | Per the reconciliation cycle (`M09`) | Automatic |
| Marketplace sellers | **Not this document** — `DT-039` payout statement | — |

---

## 2. Statutory Requirements

No prescribed form. Three obligations bind it:

| Obligation | Source | Effect |
|---|---|---|
| Consistency with issued challans | VAT & SD Act 2012 records; `DT-011` | A statement that disagrees with the sales register is evidence against us in both directions |
| Accuracy of a demand for payment | Consumer and contract law — **pending G6** | An overstated balance pursued in collections is a legal exposure (`DT-018`) |
| Personal-data minimisation | `LG-008`, `05-06` NFR-086 | Statements are addressed to a named contact and are not circulated internally beyond need |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | Statement number, account, period, statement date | Title stacked |
| Party block | Customer and contact left; account, credit terms and limit right | Labels stacked |
| Body | Opening balance → transactions in date order → closing balance → **ageing analysis** | Labels stacked |
| Totals | Closing balance, and **amount now due** | Arabic numerals, right-aligned |
| Statutory block | Not used. The **dispute and payment instruction block** occupies this zone | Parallel columns |
| Signature | Not signed. Issued under system authority with a named account contact | — |
| Footer | Statement reference, `page n of m`, hotline, account manager contact | English |

| # | Rule |
|---|---|
| **L-17-a** | **Opening balance, movements, closing balance.** A statement that lists only open items is a list, not a statement, and cannot be reconciled |
| **L-17-b** | The ageing analysis is a fixed bucket set — current, 1–30, 31–60, 61–90, 90+ days — and the buckets never change between periods. Changing buckets destroys comparability |
| **L-17-c** | **Amount now due** is distinguished from the closing balance where terms mean part of the balance is not yet due |
| **L-17-d** | The dispute block never splits across a page |
| **L-17-e** | Column headers repeat on every page; the closing balance never appears alone on a continuation page |

---

## 4. Field Mapping

### 4.1 Header and account

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Statement no. | বিবরণী নং | `MD-040` sequence | Monospace | ✔ |
| Statement date | বিবরণীর তারিখ | `statement.generated_at` | `DD/MM/YYYY` | ✔ |
| Period from / to | মেয়াদ | `MD-041` period | `DD/MM/YYYY` | ✔ |
| Account code | হিসাব কোড | `MD-013.party_code` / `MD-015` | Monospace | ✔ |
| Account name | হিসাবের নাম | `party.display_name` | Text | ✔ |
| Contact | যোগাযোগ | `party.ap_contact_name` + email | Text | ✔ |
| Credit terms | ক্রেডিট শর্ত | `MD-038.payment_term_code` | Label | ✔ where credit |
| Credit limit | ক্রেডিট সীমা | `party.credit_limit` | BDT | ✔ where credit |
| Contract reference | চুক্তি সূত্র | `M08.contract_ref` | Monospace | Where contracted |
| Currency | মুদ্রা | `MD-039` | BDT default | ✔ |

### 4.2 Transactions

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Date | তারিখ | `transaction.doc_date` | `DD/MM/YYYY` | ✔ |
| Document type | দলিলের ধরন | Enum: invoice / receipt / credit note / debit note / adjustment | Label | ✔ |
| Document no. | দলিল নং | `DT-010` / `DT-015` / `DT-016` ref | Monospace | ✔ |
| Reference | সূত্র | Order, PO or contract reference | Monospace | Where held |
| Description | বিবরণ | Line summary | Text | ✔ |
| Due date | নির্ধারিত তারিখ | Computed from terms | `DD/MM/YYYY` | ✔ for invoices |
| Debit | ডেবিট | `transaction.debit` | BDT, 2 dp | ✔ |
| Credit | ক্রেডিট | `transaction.credit` | BDT, 2 dp | ✔ |
| Running balance | চলতি স্থিতি | Computed | BDT, 2 dp | ✔ |
| Status | অবস্থা | Enum: open / part-paid / paid / disputed | Label per `VB-008` | ✔ |
| Dispute reference | বিরোধ সূত্র | `M34.case_ref` | Monospace | Where disputed |

### 4.3 Ageing and instructions

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Opening balance | প্রারম্ভিক স্থিতি | Prior statement closing | BDT, 2 dp | ✔ |
| Total debits / credits | মোট ডেবিট / ক্রেডিট | Computed | BDT, 2 dp | ✔ |
| **Closing balance** | **সমাপনী স্থিতি** | Computed | BDT, 2 dp | ✔ |
| Not yet due | এখনো বকেয়া নয় | Computed | BDT, 2 dp | ✔ |
| **Amount now due** | **এখন প্রদেয়** | Computed | BDT, 2 dp, largest type | ✔ |
| Ageing buckets | বয়সভিত্তিক বিশ্লেষণ | Computed | BDT per bucket | ✔ |
| Disputed amount excluded | বিরোধপূর্ণ পরিমাণ | Computed | BDT, 2 dp | ✔ where any |
| Payment instructions | পরিশোধের নির্দেশনা | `MD-038` bank details | Text | ✔ |
| Dispute instructions | বিরোধ জানানোর পদ্ধতি | Static + `M34` route + deadline | Text | ✔ |
| Account manager | হিসাব ব্যবস্থাপক | `employee.display_name` + contact | Text | ✔ corporate |

| # | Rule |
|---|---|
| **FM-17-a** | The opening balance **equals the prior statement's closing balance**, always. A break in that chain is a reconciliation failure and blocks issue |
| **FM-17-b** | Disputed amounts are shown, aged, and **excluded from "amount now due"**. Demanding payment of a disputed item is what turns a dispute into a complaint |
| **FM-17-c** | Every line resolves to a document the customer can be sent. "Adjustment" with no document reference is not acceptable on a statement |
| **FM-17-d** | Foreign-currency balances follow `BRU-FIN-07` revaluation and print the rate and date used |
| **FM-17-e** | The dispute instruction states a **deadline** — after which the statement is treated as accepted for reconciliation purposes. Wording confirmed by Legal |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-CTR-05` | Contract suspension for non-payment follows a defined notice sequence; the statement is the evidence of the balance at each step |
| `BRU-FIN-07` | Foreign-currency revaluation at period end |
| `BRU-CTR-04` | Entitlement over-consumption appears as billed lines, never as an invisible balance |
| `BRU-BIL-07` | Consolidated corporate invoices appear as single lines with the `DT-020` reference |
| `BRU-FIN-05` | The statement is generated from a closed period; a mid-period statement is marked **interim** |

### 5.1 Reconciliation discipline

| # | Rule |
|---|---|
| **RC-17-a** | The statement is generated from `M19` sub-ledger balances, not from an invoice list |
| **RC-17-b** | Statement totals reconcile to the `M19` receivables control account before issue. An unreconciled difference blocks issue |
| **RC-17-c** | A customer's reconciliation query is answered against the **issued** statement, from the archive — never against a freshly generated one (`DT-001` §9.3) |
| **RC-17-d** | Where a statement is corrected, a **revised statement** is issued referencing the original; the original is retained |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Monthly A4** | The default | Full statement with ageing |
| **Open-item** | On request from AP teams | Only unsettled items, with the closing balance still reconciling (`L-17-a` satisfied by an explicit reconciliation line) |
| **Corporate multi-site** | `P04` | Sub-totals by site, department and cost centre, matching `DT-020` structure |
| **Interim** | Mid-period request | Watermarked **INTERIM**; states that the period is not closed |
| **Collections rendition** | Attached to `DT-018` | Adds the dunning step reference and the consequence stated in that letter |
| **Brand partner reconciliation** | `M09` claim settlement cycle | Claims, approvals, rejections and remittances rather than invoices |
| **Structured export** | AP system ingestion | CSV/XML matching the printed columns exactly |
| **Zero-balance** | Account settled | Issued once to confirm settlement, then suppressed until activity resumes |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-017-S1` | Corporate account, one month, 14 invoices, 3 receipts | Base rendition and ageing |
| `DT-017-S2` | Account with one disputed invoice | `FM-17-b` exclusion from amount due |
| `DT-017-S3` | Multi-site corporate | Sub-totalling matching `DT-020` |
| `DT-017-S4` | Account with a credit note and a part payment | Running-balance correctness |
| `DT-017-S5` | Revised statement after a correction | `RC-17-d` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Account Management | 2026-08-15 | Draft issue |
| Reviewer — Account Management | *pending* | | |
| Reviewer — Legal & Compliance (`FM-17-e` wording) | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `STM-{entity}-{yy}-{seq:06d}` per account per period |
| Gap policy | `gaps_recorded` |
| Archive format | PDF/A-3 at issue — it is produced to auditors and cited in collections |
| Retention | `LG-009`; aligned to the underlying invoices, minimum the tax retention period |
| Re-render | **Prohibited.** A statement re-generated later reflects subsequent transactions and will not match the one the customer holds (`RC-17-c`) |
| Reprint | Watermarked **COPY**, logged |
| Chain integrity | Opening-to-closing continuity across consecutive statements is verified monthly and reported as an exception where broken (`FM-17-a`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | Debit lines |
| [`DT-015_Credit_Note_and_Debit_Note.md`](DT-015_Credit_Note_and_Debit_Note.md) | Adjustment lines |
| [`DT-016_Payment_Receipt_and_Money_Receipt.md`](DT-016_Payment_Receipt_and_Money_Receipt.md) | Credit lines |
| [`DT-018_Dunning_and_Collection_Letter_Series.md`](DT-018_Dunning_and_Collection_Letter_Series.md) | Attaches this statement at every step |
| [`DT-020_Consolidated_Corporate_Invoice.md`](DT-020_Consolidated_Corporate_Invoice.md) | Appears as a single line; structure mirrored in the multi-site variant |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-015_Corporate_Account_Hierarchy_Standard.md) | Site, department and cost-centre structure |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-039_Currency_FX_and_Rounding_Standard.md) | Revaluation and rounding |
| `RP-004` Dashboard Specification Pack — Operational Consoles | Ageing analytics and the dispute-rate KPI |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) | Where the statement supports collection — **note: no collections SOP exists in the `SP` register; see `AUDIT-007` finding DT-02** |
| [`NT-010_Email_Template_Library_Corporate_and_B2B.md`](../../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md) | The covering email |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Opening-to-closing continuity rule, fixed ageing buckets, disputed-amount exclusion, four reconciliation rules, eight variants | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Opening-balance continuity stated as a blocking rule (`FM-17-a`)
- [x] Disputed amounts excluded from the demand (`FM-17-b`)
- [x] Reconciliation-against-the-issued-copy rule stated (`RC-17-c`)
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Legal wording for the dispute deadline (`FM-17-e`) — **outstanding**
- [ ] Ageing bucket set confirmed with Finance and locked (`L-17-b`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
