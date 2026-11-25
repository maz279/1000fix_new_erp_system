---
id: DT-015
title: Credit Note and Debit Note
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance
author: Finance with Tax and Content Design
reviewers: [External tax adviser, Tax, Legal & Compliance, Internal Audit, Localisation Lead]
approver: Chief Financial Officer
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  The statutory adjustment documents — credit note and debit note — that reference an original
  Mushak 6.3 challan, carry a reason code and state the VAT treatment of the adjustment. Refunds,
  rework, price corrections and disputes all require a compliant adjustment document. An issued
  invoice is never edited; this is the only lawful alternative.
traces_to: [M20, M51, M19, M52, DT-001, DT-006, DT-010, DT-011, DT-012, DT-014, DT-020, DT-025, MD-026, MD-037, MD-040, BRU-FIN-04, BRU-DMS-03, BRU-BIL-04, BRU-BIL-05]
priority: P0
wave: W2
bilingual: yes
bn_counterpart: DT-015_Credit_Note_and_Debit_Note_BN.md
sources:
  - source: VAT and Supplementary Duty Rules 2016, Forms Mushak 6.7 (credit note) and Mushak 6.8 (debit note) — **form numbers and prescribed content must be obtained from the enacted Rules and verified at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-04 — a credit note requires approval by the Finance Manager or above
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-DMS-03 — a signed document cannot be modified; changes require a new version and a new signature
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-BIL-05 — refunds are issued to the original payment method unless the customer accepts store credit
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-015 — Credit Note and Debit Note

> ⚠ **Tier S — the forms are prescribed. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **`BRU-DMS-03`: an issued document is never modified.** Every correction to an issued invoice
> passes through this document. That makes it the most commonly misused control in a finance
> function: a credit note is how a genuine correction is made, and it is also how revenue is
> quietly reversed. §5 exists to keep the two apart.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Statutory VAT adjustment documents** — credit note and debit note |
| Owning module | `M20` Accounts Receivable, with `M51`; `M52` for supplier-side notes |
| Statutory | **Yes — Tier S.** VAT & SD Rules 2016 — form numbers **pending G6** |
| Recipient(s) | Customer or supplier (original), company record, NBR on demand |
| Languages | **Bilingual.** The prescribed form's language governs |
| Output formats | A4 portrait · PDF · **PDF/A-3 archive at issue** |
| Numbering mask | `MD-040` — **separate statutory sequences for credit and debit**, `no_gaps` |
| Retention period | **At least 5 years** from the end of the tax period — confirmed at G6 |
| Fiscal pin | **FY2026-27** |

### 1.1 Which document, when

| Situation | Instrument | Direction |
|---|---|---|
| We over-charged the customer | **Credit note** | Reduces our output VAT |
| We under-charged the customer | **Debit note** | Increases our output VAT |
| Goods or services returned by the customer | **Credit note** | Reduces output VAT |
| Post-invoice discount agreed | **Credit note** | Reduces output VAT |
| Refund after a dispute decided against us | **Credit note** | Reduces output VAT |
| We returned goods to a supplier | **Debit advice** (`DT-025`) → **debit note** | Reduces our input VAT claim |
| A supplier under-charged us and corrects it | We receive **their** debit note | Increases our input claim |
| Scope varied **before** invoicing | **Not this document** — `DT-006` revised estimate | — |
| Marketplace commission reversed on a refund | Credit note plus `BRU-BIL-04` reversal | Reduces our commission revenue |

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Prescribed form title and reference | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| Issuer name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Issuer block |
| Recipient name, address and BIN | VAT & SD Rules 2016 — **pending G6** | pending | Recipient block |
| Note number and date | VAT & SD Rules 2016 — **pending G6** | pending | Header |
| **Reference to the original challan — number and date** | VAT & SD Rules 2016 — **pending G6** | pending | Body, prominent |
| Reason for the adjustment | VAT & SD Rules 2016 — **pending G6** | pending | Body |
| Description of goods or services adjusted | VAT & SD Rules 2016 — **pending G6** | pending | Line items |
| Value of the adjustment excluding VAT | VAT & SD Rules 2016 — **pending G6** | pending | Line items, totals |
| **VAT rate and adjustment amount** | `MD-037` — rate **pending G6** | pending | Line items, totals |
| Total adjustment including VAT | VAT & SD Rules 2016 — **pending G6** | pending | Totals |
| Declaration | VAT & SD Rules 2016 — **pending G6** | pending | Statutory block |
| Signature or authorisation | VAT & SD Rules 2016 — **pending G6** | pending | Signature zone |

### 2.1 G6 questions

| # | Question |
|---|---|
| **C1** | Provide the current prescribed credit-note and debit-note forms and confirm the Mushak numbers |
| **C2** | **Is there a time limit** within which an adjustment note may be issued against an original challan? |
| **C3** | How is an adjustment presented in `DT-011` / `DT-012` and in the `DT-014` return — negative row, separate schedule, or netted? |
| **C4** | What is the treatment where the **original period has already been filed**? |
| **C5** | May a single note reference **multiple** original challans? |
| **C6** | Is a separate note required per VAT rate band? |
| **C7** | What evidence must support a credit note — customer acknowledgement, returned goods, dispute decision? |
| **C8** | Are credit notes to **unregistered** consumers treated differently from those to registered buyers? |

---

## 3. Layout

**Primary format: A4 portrait.** Brand yields to the prescribed form.

| Zone | Content | Bilingual |
|---|---|---|
| Header | Prescribed title — **CREDIT NOTE** or **DEBIT NOTE**, unambiguous — number, date | Per the instrument |
| Party block | Issuer and recipient in the prescribed order | Per the instrument |
| Body | **Original challan reference block**, then adjustment lines, then reason | Per the instrument |
| Totals | Adjustment value, VAT by band, total | Arabic numerals |
| Statutory block | Prescribed declaration | Per the instrument |
| Signature | Authorised signatory with approval reference | — |
| Footer | Note reference, `page n of m` | English |

| # | Rule |
|---|---|
| **L-15-a** | **CREDIT** and **DEBIT** are never rendered in a way that could be confused — different titles, different sequences, and the word is never abbreviated |
| **L-15-b** | The original challan reference is the **most prominent element after the title**. A note that does not obviously belong to an invoice is an orphan adjustment |
| **L-15-c** | The reason prints as text, from `MD-026`, not as a bare code. The recipient is not expected to hold our code register |
| **L-15-d** | The statutory declaration never splits |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Document type | দলিলের ধরন | `note.type` | **CREDIT NOTE / DEBIT NOTE** | ✔ |
| Note no. | নোট নং | `MD-040` sequence (type-specific) | Monospace | ✔ |
| Note date | নোটের তারিখ | `note.issued_at` | `DD/MM/YYYY` | ✔ |
| **Original challan no.** | **মূল চালান নং** | `DT-010` reference | Monospace | ✔ |
| **Original challan date** | **মূল চালানের তারিখ** | `invoice.issued_at` | `DD/MM/YYYY` | ✔ |
| Original challan value | মূল চালানের মূল্য | `invoice.total` | BDT, 2 dp | ✔ |
| Issuer name / BIN | ইস্যুকারী / বিআইএন | `MD-002` | Text + monospace | ✔ |
| Recipient name / BIN | প্রাপক / বিআইএন | `party` / `MD-016` | Text + monospace | ✔ where registered |
| Reason code | কারণ কোড | `MD-026.reason_code` | Code | ✔ |
| Reason text | কারণ | `MD-026.reason_text_en` / `_bn` | Text | ✔ |
| Line description | বিবরণ | Original invoice line | Text | ✔ |
| Original quantity / value | মূল পরিমাণ / মূল্য | Original line | Number, BDT | ✔ |
| Adjustment quantity / value | সমন্বয় পরিমাণ / মূল্য | `note.line` | Number, BDT | ✔ |
| VAT rate | ভ্যাট হার | `MD-037` — **the rate on the original** | %, 3 dp | ✔ |
| VAT adjustment | ভ্যাট সমন্বয় | Computed | BDT, 2 dp | ✔ |
| Total adjustment | মোট সমন্বয় | Computed | BDT, 2 dp | ✔ |
| Amount in words | কথায় | Computed | Text | ✔ |
| Approved by | অনুমোদনকারী | `employee.display_name` + role | Text | ✔ **`BRU-FIN-04`** |
| Approval reference | অনুমোদন সূত্র | `M63` workflow ref | Monospace | ✔ |
| Refund method | ফেরতের পদ্ধতি | `note.refund_method` | Enum | Where a refund follows |
| Refund reference | ফেরতের সূত্র | `payment.refund_ref` | Monospace | Where paid |

| # | Rule |
|---|---|
| **FM-15-a** | The VAT rate is **the rate on the original challan**, not today's rate (`TAX-04`). An adjustment reverses a specific past transaction |
| **FM-15-b** | The adjustment cannot exceed the original challan's value. A cumulative check across all notes against one challan is enforced |
| **FM-15-c** | Approval identity and reference print on the document. `BRU-FIN-04` requires Finance Manager approval or above, and the recipient can see it was obtained |
| **FM-15-d** | Where a refund follows, `BRU-BIL-05` applies — original payment method unless the customer accepts store credit — and the method prints |
| **FM-15-e** | Per **G6 C6**, a separate note may be required per rate band. Until answered, the system issues one note per band |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-FIN-04` | Finance Manager approval or above, always, with no value threshold below which it is waived |
| `BRU-FIN-03` | A payment cannot be recorded against a cancelled invoice; a credit note is not a cancellation |
| `BRU-FIN-05` / `BRU-FIN-06` | Period-close rules; a note against a hard-closed period follows **G6 C4** |
| `BRU-BIL-04` | Commission reverses automatically when the underlying transaction is refunded or a dispute is decided against the seller |
| `BRU-BIL-05` | Refund to the original payment method unless store credit is accepted |
| `BRU-DMS-03` | The reason this document exists — issued documents are never edited |
| `TAX-04` (`MD-037`) | Rate at the original tax point |
| `SEQ-01` (`MD-040`) | Gap-free statutory sequences, one per note type |

### 5.1 Controls against misuse

A credit note reduces revenue and reduces output VAT. Both make it attractive.

| # | Control |
|---|---|
| **CN-01** | Approval at Finance Manager or above, **always** (`BRU-FIN-04`) |
| **CN-02** | The **approver may not be the issuer**, and neither may be the person who raised the original invoice (`BRU-SEC-07`) |
| **CN-03** | Every note carries a reason code; **reason distribution by branch and by approver is reported monthly** (`RP-009`) |
| **CN-04** | A note issued more than *n* days after the original challan escalates a level. The threshold is set once **G6 C2** answers the statutory time limit |
| **CN-05** | Credit notes as a percentage of revenue are a **standing management-review metric**, by branch and by account manager |
| **CN-06** | A credit note against a challan that has already been the subject of a credit note requires the next approval level up |
| **CN-07** | Evidence per **G6 C7** is attached before issue — customer acknowledgement, returned-goods record or dispute decision |
| **CN-08** | Credit notes issued in the final three days of a period are listed for the Finance Manager before period close. Period-end concentration is the classic pattern |

> **CN-05 and CN-08 are the two that find real problems.** A rising credit-note ratio in one
> branch, or a cluster in the last days of a period, is visible in the data long before it is
> visible in an audit.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Customer credit note** | Over-charge, return, post-invoice discount, refund | The base document |
| **Customer debit note** | Under-charge correction | Increases the receivable; same discipline |
| **Supplier debit note** | Return to vendor (`DT-025`) | Issued by us to a supplier; reduces our input claim |
| **Supplier credit note received** | Supplier corrects an over-charge | Not issued by us; recorded against `DT-012` |
| **Marketplace** | Refund on a seller job (`P07`) | Commission reversal per `BRU-BIL-04`; seller statement adjusted (`DT-039`) |
| **Corporate consolidated** | Adjustment to a `DT-020` invoice | References the consolidated invoice **and** the underlying challan lines |
| **Goodwill credit** | Service-recovery gesture with no billing error | Distinct reason code; **highest scrutiny** — it is a discount after the fact and is reported separately |

---

## 7. Worked Example

> **Specimens produced only after G6 delivers the prescribed forms.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-015-S1` | Over-charge corrected, registered buyer | Base credit note, original reference prominence |
| `DT-015-S2` | Under-charge corrected | Debit note, `L-15-a` distinguishability |
| `DT-015-S3` | Two rate bands on the original | `FM-15-e` per-band handling |
| `DT-015-S4` | Refund to bKash, original method | `BRU-BIL-05` |
| `DT-015-S5` | Second credit note against one challan | `FM-15-b` cumulative cap and `CN-06` escalation |
| `DT-015-S6` | Goodwill credit | Distinct reason code and reporting treatment |

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Tax | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| Reviewer — Legal & Compliance | *pending* | | |
| **G6 — external tax adviser** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — Chief Financial Officer | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — **two separate statutory sequences**, credit and debit, both `no_gaps` |
| Reset | Fiscal year |
| Archive format | **PDF/A-3 at issue** |
| Retention | **At least 5 years** from the end of the tax period — pending G6 |
| Linkage | Archived **with** the original challan as one evidential set; neither is served without the other |
| Re-render | Prohibited (`DT-001` §9.3) |
| Reprint | Watermarked **COPY**, logged |
| Cancellation | A note issued in error is **voided** and a corrected note issued; the void retains its number (`RC-04`) |
| Register presentation | Per **G6 C3** in `DT-011` / `DT-012` and the `DT-014` return |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The original every note references |
| [`DT-011_Sales_Register_Mushak_6_2.md`](DT-011_Sales_Register_Mushak_6_2.md) | Where customer notes appear |
| [`DT-012_Purchase_Register_Mushak_6_1.md`](DT-012_Purchase_Register_Mushak_6_1.md) | Where supplier notes appear |
| [`DT-014_VAT_Return_Pack_Mushak_9_1.md`](DT-014_VAT_Return_Pack_Mushak_9_1.md) | The adjustment schedule |
| [`DT-020_Consolidated_Corporate_Invoice.md`](DT-020_Consolidated_Corporate_Invoice.md) | Corporate adjustments |
| [`../05A_Service_and_Operations/DT-006_Revised_Estimate_and_Approval_Record.md`](../05A_Service_and_Operations/DT-006_Revised_Estimate_and_Approval_Record.md) | The pre-invoice instrument; boundary stated there in §5.1 |
| [`../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md`](../05C_Supply_Chain_and_Logistics/DT-025_Return_to_Vendor_and_Debit_Advice.md) | The supplier-side trigger |
| [`../05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md`](../05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md) | Commission reversal lands here |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | The reason vocabulary |
| `RP-009` Statutory and Regulatory Report Format Register | `CN-03`, `CN-05`, `CN-08` reporting |
| [`SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | The operational procedure |
| `UI-039` Payment and Checkout Flow Copy | The on-screen journey |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Which-document-when table, eight-question G6 list, rate-at-original-tax-point rule, cumulative adjustment cap, eight anti-misuse controls, goodwill-credit segregation | Chief Financial Officer (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Credit and debit clearly distinguished in title, sequence and rendering (`L-15-a`)
- [x] Original-challan reference made mandatory and prominent
- [x] Anti-misuse controls stated with the two that actually detect problems identified
- [x] Boundary with `DT-006` stated
- [x] All internal links resolve
- [ ] **G6 — prescribed forms and Mushak numbers confirmed** — **outstanding, unwaivable (`WV-02`)**
- [ ] G6 C2 time limit — **outstanding; `CN-04` threshold cannot be set without it**
- [ ] G6 C3 register/return presentation — **outstanding; blocks `DT-011`/`DT-012` column design**
- [ ] G6 C4 treatment where the original period is filed — **outstanding; blocks `M51` correction design**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
