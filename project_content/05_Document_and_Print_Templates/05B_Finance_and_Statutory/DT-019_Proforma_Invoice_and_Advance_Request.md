---
id: DT-019
title: Proforma Invoice and Advance Request
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Commercial and Content Design
reviewers: [External tax adviser, Tax, Commercial, Account Management, Localisation Lead]
approver: Chief Financial Officer
content_class: A
purpose: >
  The pre-payment document corporate and government buyers need in order to raise a payment before
  a supply is made. Many such buyers cannot release funds without a proforma; its absence blocks
  revenue outright. It is deliberately not a tax invoice, and the discipline that keeps the two
  apart is the reason this file is class A.
traces_to: [M20, M36, M51, P04, DT-001, DT-005, DT-010, DT-016, DT-020, DT-023, MD-037, MD-038, MD-039, MD-040, BRU-SRM-13, NT-05-a]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: DT-019_Proforma_Invoice_and_Advance_Request_BN.md
sources:
  - source: project_content/05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010 §2.1 and G6 Q3 — the tax point question that determines when a Mushak 6.3 must follow an advance
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05A_Service_and_Operations/DT-005 §2.1 — an estimate is not a tax invoice; the same discipline applied here
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-13 — validity expiry and re-issue rather than extension
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-019 — Proforma Invoice and Advance Request

> ⚠ **Class A — statutory consequence, by omission rather than commission.**
>
> A proforma is **not** a tax invoice. It creates no VAT liability by itself, gives the buyer no
> input credit, and consumes no Mushak sequence. Every one of those statements stops being true
> the moment a proforma is allowed to look like a challan — which is why the "this is not a VAT
> invoice" marking on this document is a compliance control, not a courtesy.
>
> **The open question is what happens when the advance is received.** `DT-010` G6 Q3 — the tax
> point — decides it, and until it is answered this template's §5.1 states the conservative path.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Proforma invoice / advance payment request |
| Owning module | `M20` Accounts Receivable, with `M36` Quotation and Tender |
| Statutory | No prescribed form. **Class A** because misuse creates a VAT consequence |
| Recipient(s) | Corporate, government and institutional buyers; account manager; finance |
| Languages | **Bilingual — stacked labels.** English-dominant for institutional recipients |
| Output formats | A4 portrait · PDF for email and portal (`P04`) |
| Numbering mask | `MD-040` — `PRO-{entity}-{yy}-{seq:06d}`. **A non-statutory sequence, deliberately distinct in format from the Mushak sequence** |
| Retention period | `LG-009`; aligned to the resulting invoice where one follows |

### 1.1 When a proforma is the right instrument

| Situation | Instrument |
|---|---|
| Buyer's procurement requires a document to raise a payment before supply | **`DT-019`** |
| Buyer needs a priced offer to decide | `DT-005` estimate, or `M36` quotation |
| Advance or deposit required by contract | **`DT-019`** |
| Tender or bid submission | `M36` bid, not this |
| Supply has been made and is billable | `DT-010` tax invoice |
| Rental deposit | `DT-037` handles the deposit terms; `DT-019` requests the money |
| Corporate consolidated billing | `DT-020` |

---

## 2. Statutory Requirements

No prescribed form. The obligations are all about **not being mistaken for one**:

| Obligation | Source | Effect |
|---|---|---|
| Must not be presented as a tax invoice | VAT & SD Act 2012 — **pending G6** | Issuing a document that appears to be a Mushak 6.3 without being one is a compliance risk in both directions |
| Must not consume a Mushak sequence | `SEQ-01`, `MD-040` | A statutory sequence is gap-free; a proforma consuming a number creates an unexplainable gap |
| Tax point on receipt of an advance | `DT-010` G6 Q3 — **pending** | Determines whether a Mushak 6.3 must issue on receipt of the advance |
| Accuracy of the amount requested | Contract | An advance request that does not match the contract is a payment that will not be released |

### 2.1 G6 questions

| # | Question |
|---|---|
| **PF1** | Does receipt of an advance create a tax point requiring a Mushak 6.3 at that moment? (paired with `DT-010` Q3) |
| **PF2** | If so, is the challan issued for the advance amount, and how is it reconciled to the final supply challan? |
| **PF3** | Is there any prescribed content or prohibition for a proforma or advance request? |
| **PF4** | What wording must appear to make clear the document is not a tax invoice? |

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | **PROFORMA INVOICE** — unambiguous, never abbreviated — number, date, validity | Title stacked |
| Party block | Buyer and their procurement reference left; entity, BIN and bank details right | Labels stacked |
| Body | Line items, deliverables, delivery expectation | Labels stacked |
| Totals | Value, VAT **shown as it will be charged**, total requested | Arabic numerals |
| Statutory block | **The not-a-tax-invoice statement and the payment terms** | Parallel columns |
| Signature | Authorised signatory | Labels stacked |
| Footer | Proforma reference, `page n of m`, hotline | English |

| # | Rule |
|---|---|
| **L-19-a** | The title reads **PROFORMA INVOICE** in both languages, in the largest type in the header. It is never rendered as "Invoice" alone |
| **L-19-b** | **"This is not a VAT invoice / এটি ভ্যাট চালান নয়"** prints in the totals block and again in the statutory block |
| **L-19-c** | The document reference format is visibly different from the Mushak sequence — different prefix, different length |
| **L-19-d** | VAT is shown as **the amount that will be charged**, clearly labelled as indicative of the future challan, never as VAT charged |
| **L-19-e** | Bank details for payment print in full, once, and are drawn from `MD-038` — never typed |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Proforma no. | প্রোফর্মা নং | `MD-040` sequence | Monospace | ✔ |
| Proforma date | তারিখ | `proforma.issued_at` | `DD/MM/YYYY` | ✔ |
| Valid until | মেয়াদ | `proforma.valid_to` | `DD/MM/YYYY` | ✔ **`BRU-SRM-13` discipline applies** |
| Buyer name and address | ক্রেতা | `party` / `MD-015` | Text | ✔ |
| Buyer BIN / TIN | বিআইএন / টিআইএন | `party.bin`, `.tin` | Monospace | Where registered |
| Buyer PO / procurement ref | ক্রয়াদেশ সূত্র | `party.po_ref` | Monospace | **✔ where the buyer requires it** |
| Contract reference | চুক্তি সূত্র | `M08.contract_ref` | Monospace | Where contracted |
| Entity name and BIN | প্রতিষ্ঠান ও বিআইএন | `MD-002` | Text + monospace | ✔ |
| Line description | বিবরণ | `MD-019` / `MD-022` | Text | ✔ |
| Quantity / unit / rate | পরিমাণ / একক / দর | `MD-023`, `MD-029` | Number, BDT | ✔ |
| Value excl. VAT | মূল্য (ভ্যাট ব্যতীত) | Computed | BDT, 2 dp | ✔ |
| VAT to be charged | প্রযোজ্য ভ্যাট | `MD-037.rate_pct` applied | BDT, 2 dp | ✔ **labelled indicative** |
| **Total requested** | **মোট অনুরোধকৃত** | Computed | BDT, 2 dp, largest type | ✔ |
| Amount in words | কথায় | Computed | Text, both languages | ✔ |
| Advance percentage | অগ্রিমের হার | `contract.advance_pct` | % | Where partial |
| Balance on supply | সরবরাহে প্রদেয় | Computed | BDT, 2 dp | Where partial |
| Payment terms | পরিশোধের শর্ত | `MD-038.payment_term_code` | Label + text | ✔ |
| Bank details | ব্যাংক বিবরণ | `MD-038` | Text | ✔ |
| Expected delivery | সরবরাহের সম্ভাব্য সময় | `proforma.expected_delivery` | Text | ✔ |
| Not a tax invoice | ভ্যাট চালান নয় | Static | Text | ✔ |
| Authorised signatory | অনুমোদিত স্বাক্ষরকারী | `employee.display_name` + designation | Text | ✔ |

| # | Rule |
|---|---|
| **FM-19-a** | The proforma **never** carries a Mushak number, a challan reference, or a VAT registration statement phrased as a charge |
| **FM-19-b** | Where a buyer's procurement system requires a PO reference on the document, it prints. Its absence is the most common reason a payment stalls |
| **FM-19-c** | An expired proforma is **re-issued** with a new number, not extended (`BRU-SRM-13` discipline) |
| **FM-19-d** | The advance percentage and the balance both print where the advance is partial. A buyer who thinks they have paid in full will dispute the balance |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-13` | Validity expiry; re-issue rather than extension |
| `BRU-CTR-01` | A contract cannot be activated without entitlements, billing frequency and approval — an advance request against an unactivated contract is premature |
| `BRU-FIN-03` | Payment cannot be recorded against a cancelled document |
| `SEQ-03` (`MD-040`) | The proforma sequence must be unique and distinguishable from statutory sequences |
| `TAX-01` (`MD-037`) | The indicative VAT uses the same rate resolution the eventual challan will use |

### 5.1 What happens when the advance is received — the conservative path

Until **G6 PF1** answers the tax-point question, the system follows this:

| Step | Action |
|---|---|
| 1 | Payment received against the proforma → **`DT-016` money receipt** issues, referencing the proforma |
| 2 | The amount is held as an **advance on account**, not as revenue (`M19`) |
| 3 | When the supply is made, **`DT-010` Mushak 6.3** issues for the full supply |
| 4 | The advance is applied against the challan; the balance, if any, is demanded |
| 5 | `DT-017` shows the advance as a credit throughout |

| # | Rule |
|---|---|
| **AD-01** | The advance is **never** treated as revenue before supply (`BRU-BIL-06` deferred-revenue discipline) |
| **AD-02** | If **G6 PF1** determines that receipt creates a tax point, step 3 moves to step 1 and a challan issues on receipt. **This is a material design change to `M20` and must be answered before W3** |
| **AD-03** | An advance held with no supply made after the agreed period is reported as an ageing item and either applied, refunded, or escalated |
| **AD-04** | Refund of an advance follows `DT-015` and `BRU-BIL-05`, not an informal return |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard proforma** | Corporate buyer needs a document to pay | The base document |
| **Advance request** | Contract requires a deposit or advance | Advance percentage and balance-on-supply prominent |
| **Government / institutional** | Public-sector procurement | Adds tender reference, budget code and any prescribed certification the buyer requires |
| **Rental deposit request** | `M13` | Deposit terms cross-referenced to `DT-037`; refundability stated |
| **AMC renewal advance** | Contract renewal cycle | References the contract and the renewal period |
| **Export / foreign buyer** | Where applicable | Currency per `MD-039`, FX basis and date stated; bank details for the foreign-currency account |
| **Revised proforma** | Scope or price changed before payment | New number, references the superseded proforma, which is marked **VOID** |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-019-S1` | Corporate proforma, full value | Base rendition, not-a-tax-invoice markings |
| `DT-019-S2` | 40% advance with balance on supply | `FM-19-d` |
| `DT-019-S3` | Government buyer with tender and budget references | Institutional variant |
| `DT-019-S4` | Advance received, challan issued on supply | §5.1 conservative path end to end |
| `DT-019-S5` | Expired proforma re-issued | `FM-19-c` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Commercial | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Commercial | *pending* | | |
| Reviewer — Account Management | *pending* | | |
| **G6 — external tax adviser (PF1–PF4)** | *pending* | | **Required before W3** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `PRO-{entity}-{yy}-{seq:06d}`, **non-statutory, visibly distinct** (`L-19-c`) |
| Gap policy | `gaps_recorded` — an unused proforma number is recorded, not hidden |
| Archive format | PDF/A-3 where a payment followed; standard PDF otherwise |
| Retention | `LG-009`; aligned to the resulting invoice, or to the advance's ageing where no supply followed |
| Re-render | Prohibited once issued to a buyer |
| Reprint | Watermarked **COPY**, logged |
| Void | A superseded proforma is marked **VOID** and retains its number (`RC-04`) |
| Linkage | The proforma, the `DT-016` receipt and the eventual `DT-010` challan are retrievable as one chain |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | What must follow; G6 Q3 tax point governs when |
| [`DT-016_Payment_Receipt_and_Money_Receipt.md`](DT-016_Payment_Receipt_and_Money_Receipt.md) | Issued on receipt of the advance |
| [`DT-017_Customer_Statement_of_Account.md`](DT-017_Customer_Statement_of_Account.md) | Shows the advance as a credit |
| [`DT-020_Consolidated_Corporate_Invoice.md`](DT-020_Consolidated_Corporate_Invoice.md) | Where advances are applied against consolidated billing |
| [`../05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md`](../05A_Service_and_Operations/DT-005_Repair_Estimate_and_Quotation.md) | The offer instrument; §2.1 states the same not-a-tax-invoice discipline |
| [`../05D_Commercial_and_Contract/DT-037_Rental_Agreement_and_Asset_Handover_Record.md`](../05D_Commercial_and_Contract/DT-037_Rental_Agreement_and_Asset_Handover_Record.md) | Rental deposit terms |
| [`../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md`](../../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-038_Payment_Method_Term_and_Bank_Master.md) | Bank details and payment terms |
| [`NT-010_Email_Template_Library_Corporate_and_B2B.md`](../../04_Notification_and_Messaging/04C_Email/NT-010_Email_Template_Library_Corporate_and_B2B.md) | The covering email |
| [`SP-020_SOP_Month_End_and_Year_End_Close.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) | The `M19` treatment |
| `UI-038` Estimate and Approval Flow Copy | The portal journey |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Instrument-selection table, distinct non-statutory sequence rule, dual not-a-tax-invoice markings, conservative advance-receipt path with the `AD-02` design-change warning | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Not-a-tax-invoice discipline stated as a compliance control with two printed markings
- [x] Sequence made visibly distinct from statutory sequences (`L-19-c`)
- [x] Advance-receipt path stated conservatively with the open tax-point question flagged
- [x] All internal links resolve
- [ ] **G6 PF1 — advance tax point** — **outstanding; `AD-02` is a material `M20` design dependency, needed before W3**
- [ ] G6 PF4 — required not-a-tax-invoice wording — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
