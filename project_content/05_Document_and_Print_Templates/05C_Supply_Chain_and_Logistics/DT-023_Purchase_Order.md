---
id: DT-023
title: Purchase Order
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Procurement with Legal & Compliance
author: Procurement with Legal & Compliance, Tax and Content Design
reviewers: [Legal Counsel, Finance, Tax, Inventory, Internal Audit, Vendor Management]
approver: Legal Counsel with Chief Financial Officer
content_class: A
purpose: >
  The legally binding order — terms, delivery, tax treatment and acceptance conditions. It is the
  contract with the supplier, and ambiguity in it is settled at the company's expense. It is also
  where the VDS position is fixed, which makes it a class A document even though no form is
  prescribed for it.
traces_to: [M16, M42, M52, M51, P05, DT-001, DT-021, DT-022, DT-024, DT-025, DT-013, MD-016, MD-037, MD-038, MD-040, BRU-SCM-01, BRU-SCM-02, BRU-SCM-03, BRU-INV-03, BRU-FIN-09]
priority: P1
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — vendor-facing procurement documents remain English
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SCM-01 — a vendor invoice cannot be approved for payment without a matched purchase order and goods receipt within tolerance
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-FIN-09 — TDS is deducted at the correct rate on every applicable vendor payment; the payment cannot proceed otherwise
    verified: 2026-08-15
    class: P1
  - source: project_content/05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-013 — the VDS certificate obligation that flows from the position declared here
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-023 — Purchase Order

> ⚠ **Class A — statutory consequence.** The PO is a contract, and it is also the document that
> declares the **VDS and TDS position** to the supplier. A supplier who learns at payment that we
> withhold has been told too late; a supplier who was told here has priced accordingly.
>
> **`BRU-SCM-01`: no vendor invoice is paid without a matched PO and goods receipt.** That makes
> the PO the gate through which all supplier spend passes, and a retrospective PO raised to
> legitimise a purchase already made is a control failure, recorded as one.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Binding purchase contract** |
| Owning module | `M16` Procurement, with `M52` Accounts Payable |
| Statutory | No prescribed form. **Class A** — it fixes the VDS/TDS position and underpins input-VAT claims |
| Recipient(s) | Supplier (original), receiving location, accounts payable, internal audit |
| Languages | **English only** (`CG-010` §3.2) |
| Output formats | `P05` portal (primary) · PDF for email · A4 portrait |
| Numbering mask | `MD-040` — `PO-{entity}-{yy}-{seq:06d}` |
| Retention period | `LG-009`; **contract term plus the limitation period**, and not less than the tax retention on the purchases under it |

### 1.1 What the PO fixes

| Dimension | Fixed here | Consequence if left open |
|---|---|---|
| What | Specification, quantity, unit | The wrong item arrives and we own it |
| Price | Unit price, currency, total | Invoiced at a higher price with no basis to refuse |
| Tax | VAT treatment, **VDS/TDS position and rate** | Supplier disputes the deduction at payment |
| When | Delivery date and location | Late delivery with no remedy |
| Terms | Payment terms, warranty, returns, penalties | Every one of these is settled in the supplier's favour by silence |
| Acceptance | Inspection right and rejection basis | Defective goods become ours on delivery |
| Who | Supplier entity, our entity, receiving location | Invoices to the wrong entity, undeliverable goods |

---

## 2. Statutory Requirements

No prescribed form. Five obligations:

| Obligation | Source | Effect |
|---|---|---|
| VDS position disclosed | `MD-037`, `DT-013`, `BRU-FIN-09` | The supplier must know before supplying that we will withhold, and at what rate |
| TDS position disclosed | Income Tax Act 2023 — **pending G6** | Same, for income-tax withholding on applicable payments |
| Correct entity identification with BIN | VAT & SD Act 2012 — **pending G6** | The supplier's challan must be addressed to the correct entity or the input claim fails (`DT-012` D-1) |
| Enforceable terms | Contract Act — **pending G6** | Terms that are unenforceable are worse than absent, because they are relied on |
| Import compliance where applicable | `M44` Import Trade Compliance | LC, bill of entry and landed-cost obligations |

### 2.1 G6 questions

| # | Question |
|---|---|
| **PO1** | Which purchase categories attract VDS, at what rates, and what must the PO state? (paired with `DT-013` V3) |
| **PO2** | Which vendor payments attract TDS, at what rates, and what evidence must we give the supplier? |
| **PO3** | Are our standard terms — liability cap, penalties, retention of title, governing law — enforceable as drafted? |
| **PO4** | What must a PO state to protect the input-VAT claim on the resulting supply? |

---

## 3. Layout

| Zone | Content |
|---|---|
| Header | **PURCHASE ORDER**, PO number, date, revision number |
| Party block | Supplier left; our entity, BIN, delivery location and invoicing address right |
| Body | Line items → delivery schedule → **tax treatment block** → acceptance conditions |
| Totals | Value, VAT, **VDS/TDS to be withheld**, net payable |
| Statutory block | **Terms and conditions** — the binding set |
| Signature | Authorised signatory, with the approval reference |
| Footer | PO reference, `page n of m`, acknowledgement instruction |

| # | Rule |
|---|---|
| **L-23-a** | The **tax treatment block** is a distinct, headed section — not a footnote. It states VAT, VDS and TDS positions and the certificates that will follow |
| **L-23-b** | **Net payable after withholding** prints alongside the gross. A supplier who reads only the total must read the amount they will actually receive |
| **L-23-c** | Terms and conditions print in full on the PO, or the PO states where they are and confirms the supplier has accepted them. **A reference to terms the supplier has never seen is not incorporation** |
| **L-23-d** | The acknowledgement instruction and deadline print prominently — the vendor acknowledgement target is above 90% (`NT-011`) |
| **L-23-e** | Revisions are marked **REVISION n** with a change summary; the original PO number is retained |

---

## 4. Field Mapping

### 4.1 Header, parties and lines

| Label | Source field | Format | Required |
|---|---|---|:--:|
| PO no. | `MD-040` sequence | Monospace | ✔ |
| Revision no. | `po.revision_seq` | `R{n}` | Where revised |
| PO date | `po.issued_at` | `DD/MM/YYYY` | ✔ |
| Requisition reference | `DT-021` reference | Monospace | ✔ |
| RFQ reference | `DT-022` reference | Monospace | Where tendered |
| Supplier name, code, address | `MD-016` | Text + monospace | ✔ |
| **Supplier BIN** | `MD-016.bin` | Monospace | ✔ |
| Supplier TIN | `MD-016.tin` | Monospace | Where applicable |
| Our entity, address, **BIN** | `MD-002` | Text + monospace | ✔ |
| Invoice-to address | `MD-002` | Text | ✔ |
| Deliver-to location | `MD-003` / `MD-004` + contact | Text | ✔ |
| Line no. / specification | `po.line.*`, `MD-022` | Integer, text | ✔ |
| Manufacturer part number | `MD-022.mpn` | Monospace | Where applicable |
| Quantity / unit | `po.line.qty`, `MD-023` | Number + UoM | ✔ |
| Unit price / currency | `po.line.unit_price`, `MD-039` | BDT or FX, 2 dp | ✔ |
| Line value | Computed | 2 dp | ✔ |
| Required delivery date | `po.line.required_by` | `DD/MM/YYYY` | ✔ |
| Partial delivery permitted | `po.line.partial_allowed` | Bool | ✔ |
| Over/under-delivery tolerance | `po.line.tolerance_pct` | % | ✔ **feeds `BRU-SCM-01` matching** |

### 4.2 Tax, totals and terms

| Label | Source field | Format | Required |
|---|---|---|:--:|
| VAT treatment | `MD-037.tax_code` + rate | Text + % | ✔ |
| **VDS applicable / rate** | `MD-037` VDS code | Bool + % | ✔ **`PO1`** |
| VDS certificate commitment | Static + `DT-013` reference | Text | ✔ where VDS applies |
| **TDS applicable / rate** | Tax register | Bool + % | ✔ **`PO2`** |
| Order value excl. VAT | Computed | 2 dp | ✔ |
| VAT | Computed | 2 dp | ✔ |
| Gross order value | Computed | 2 dp | ✔ |
| Less VDS to be withheld | Computed | 2 dp | ✔ where applicable |
| Less TDS to be withheld | Computed | 2 dp | ✔ where applicable |
| **Net payable to supplier** | Computed | 2 dp, prominent | ✔ |
| Payment terms | `MD-038.payment_term_code` | Label + text | ✔ |
| Warranty required | `po.warranty_terms` | Text | ✔ |
| Return / rejection rights | Static terms | Text | ✔ |
| Delivery basis / Incoterms | `po.delivery_basis` | Enum | ✔ |
| Packaging and labelling requirement | `DT-044` reference | Text | ✔ for stock items |
| Acknowledgement deadline | `po.ack_deadline` | `DD/MM/YYYY` | ✔ |
| Authorised signatory | `employee.display_name` + designation | Text | ✔ |
| Approval reference | `M63` workflow ref | Monospace | ✔ |

| # | Rule |
|---|---|
| **FM-23-a** | The PO states the **net payable after withholding**. This single field removes the most common supplier payment dispute |
| **FM-23-b** | Over- and under-delivery tolerances are stated per line, because `BRU-SCM-01` matches within tolerance and an unstated tolerance defaults to zero |
| **FM-23-c** | Labelling requirements cite `DT-044`. Goods arriving without scannable labels cost warehouse time on every receipt |
| **FM-23-d** | A PO cannot issue to an inactive or unapproved vendor (`BRU-SCM-02`), nor for an item above maximum stock without the `DT-021` override (`BRU-INV-03`) |
| **FM-23-e** | The approval reference prints. The supplier can see the order is authorised; the auditor can trace it |
| **FM-23-f** | Currency and, where foreign, the FX basis and the party bearing FX risk are stated (`MD-039`) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SCM-01` | The PO is one leg of the three-way match; tolerances printed here govern it |
| `BRU-SCM-02` | Active, approved vendors only |
| `BRU-SCM-03` | The PO raiser cannot approve the resulting invoice |
| `BRU-SCM-04` | Import landed cost allocated before received stock is finally valued — import POs carry the landed-cost basis |
| `BRU-INV-03` | Stock-above-maximum block, overridable only through the `DT-021` approval |
| `BRU-FIN-09` | TDS deducted at the correct rate or the payment cannot proceed |
| `BRU-ADM-01` | A material change is a **revision**, re-approved and re-issued |
| `BRU-WTY-04` | Brand-supplied warranty parts are ordered on their own PO type and cannot be consumed on non-warranty jobs |

### 5.1 Retrospective POs

| # | Rule |
|---|---|
| **RP-23-a** | A PO raised **after** the goods or services were received is marked **RETROSPECTIVE** on the document and in the record |
| **RP-23-b** | It requires approval one level above the normal threshold |
| **RP-23-c** | The reason is coded (`MD-026`) and reported monthly by requester and by supplier |
| **RP-23-d** | It is never backdated. The issue date is the actual issue date |
| **RP-23-e** | A supplier with a rising retrospective-PO rate is a supplier who is being allowed to supply without authorisation, and that is a vendor-management finding, not a paperwork one |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Standard goods PO** | Parts, consumables, equipment | The base document |
| **Services PO** | Contractors, facilities, logistics, professional services | Scope of work and milestones replace quantity; **TDS position usually applies** |
| **Blanket / framework** | Call-off against an agreed ceiling | Ceiling, price-hold period, call-off mechanics; releases are not separate POs |
| **Import PO** | Foreign supplier (`M44`) | LC or payment terms, Incoterms, HS codes, landed-cost basis, customs documentation requirements |
| **Consignment PO** | Brand consignment stock (`BRU-INV-04`) | Zero value at receipt; title and valuation terms stated explicitly |
| **Capital PO** | Fixed asset (`M49`) | Asset class, commissioning and acceptance criteria, warranty and support terms |
| **Emergency / retrospective** | §5.1 | Marked, escalated, reported |
| **Revision** | Material change | **REVISION n**, change summary, re-acknowledgement required |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-023-S1` | Spare parts, VAT only, no withholding | Base rendition |
| `DT-023-S2` | Service PO with VDS and TDS | `L-23-b` net-payable presentation |
| `DT-023-S3` | Import PO with Incoterms and landed cost | Import variant |
| `DT-023-S4` | Revision after a delivery-date change | `L-23-e` and re-acknowledgement |
| `DT-023-S5` | Retrospective PO | `RP-23-a`…`RP-23-d` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Procurement with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Tax | *pending* | | |
| Reviewer — Finance | *pending* | | |
| Reviewer — Inventory | *pending* | | |
| **Legal Counsel — terms and conditions** | *pending* | | **Required** |
| **G6 — external tax adviser (PO1, PO2, PO4)** | *pending* | | **Required** |
| Approver — Legal Counsel with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `PO-{entity}-{yy}-{seq:06d}`; revisions suffix `/R{n}` on the same number |
| Gap policy | `gaps_recorded`; a cancelled PO retains its number with a reason and is notified to the supplier |
| Archive format | **PDF/A-3 at issue** — it is a contract |
| Retention | `LG-009`; **contract term plus limitation period**, and not less than the tax retention on purchases under it |
| Re-render | **Prohibited.** Prices, terms and tax positions change |
| Reprint | Watermarked **COPY**, logged |
| Acknowledgement | The supplier's acknowledgement is archived with the PO. **An unacknowledged PO is an offer, not an agreement** |
| Chain | `DT-021` → `DT-022` → `DT-023` → `DT-024` → invoice → payment → `DT-013`, retrievable as one file |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-021_Purchase_Requisition.md`](DT-021_Purchase_Requisition.md) | The authorisation |
| [`DT-022_Request_for_Quotation.md`](DT-022_Request_for_Quotation.md) | The sourcing basis |
| [`DT-024_Goods_Receipt_Note_and_Inspection_Record.md`](DT-024_Goods_Receipt_Note_and_Inspection_Record.md) | The second leg of the three-way match |
| [`DT-025_Return_to_Vendor_and_Debit_Advice.md`](DT-025_Return_to_Vendor_and_Debit_Advice.md) | Rejection route under the acceptance conditions |
| [`../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md`](../05B_Finance_and_Statutory/DT-013_VDS_Certificate_Mushak_6_6.md) | The certificate this PO commits us to issue |
| [`../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md`](../05B_Finance_and_Statutory/DT-012_Purchase_Register_Mushak_6_1.md) | Where the resulting supply is registered |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Supplier labelling requirement |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Supplier identity, BIN and withholding applicability |
| `LG-006` Vendor Portal Terms and Supplier Code of Conduct | The full terms this PO incorporates |
| `EO-005` Vendor and Supplier Onboarding Pack | Where a supplier accepts the standard terms |
| [`NT-011_Email_Template_Library_Vendor_and_Supplier.md`](../../04_Notification_and_Messaging/04C_Email/NT-011_Email_Template_Library_Vendor_and_Supplier.md) | PO issue and acknowledgement chasing |
| [`SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) | How it is raised and issued |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven-dimension "what the PO fixes" table, distinct tax-treatment block with net-payable presentation, tolerance-per-line rule, five retrospective-PO rules, eight variants | Legal Counsel with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] VDS/TDS position made a first-class element with net payable printed (`L-23-a`, `L-23-b`)
- [x] Incorporation-of-terms rule stated (`L-23-c`)
- [x] Retrospective POs handled with recorded escalation, never backdating
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **Legal Counsel approval of the standard terms (`LG-006`)** — **outstanding; blocks `Approved`**
- [ ] **G6 PO1/PO2 — VDS and TDS categories and rates** — **outstanding; the tax block cannot be populated without them**
- [ ] G6 PO3 — enforceability of liability cap, penalties and retention of title — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
